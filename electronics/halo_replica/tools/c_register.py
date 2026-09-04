#!/usr/bin/env python3
"""c_register - transfer a metric datum from a photograph that HAS a ruler onto a
photograph that does NOT, by registering the two views of the same planar board.

Lane L2 (component-side metrology), halo Replica.

SIDE CONVENTION, stated because the two sources disagree on the word:
    FRONT = THE COMPONENT SIDE.  This follows Apple's own FCC filing, which
    captions internal photo 6 "MLB - Front".  Colin O'Flynn calls that same face
    "backside", so O'Flynn's file `backside-fullres.jpeg` IS this project's FRONT.

WHY THIS TOOL EXISTS
    O'Flynn's component-side photograph is ~6.5x sharper than the FCC one but
    carries NO scale reference.  FCC internal photo 6 shows the SAME FACE between
    two steel rulers.  So the datum can be TRANSFERRED - if, and only if, the
    registration between the two views is shown to be accurate on features that
    were NOT used to fit it.  A registration validated on its own control points
    is a check that can agree with what it checks.

THREE VERDICTS, AND THEY ARE THE EXIT CODE
    0  PASS              a transform, with its HELD-OUT error
    1  FAIL              it ran and the held-out error exceeds tolerance
    2  CANNOT DETERMINE  the photographs do not support a registration. Never a default.

EVERY NUMBER CARRIES ITS INPUT: source file, target file, region, model, scale basis.

THE CONTROLS, and each has been watched to fire (see `selftest`)
  * NULL DISTRIBUTION.  The alignment score is compared against the SAME score at
    deliberately wrong rotations.  A score that does not stand clear of its own
    null is not a registration.
  * WRONG-FACE CONTROL.  Registering the OPPOSITE face of the same board must not
    succeed.  It is the same object, the same photographer, the same lighting -
    the only thing that differs is that it is not the same face.
  * SPATIAL HOLD-OUT.  The transform is fitted on one angular sector of the board
    and its error is measured on landmarks in the sector it never saw.
  * LANDMARK AMBIGUITY GATE.  A landmark whose correlation peak is not clearly
    the only peak is DISCARDED and counted, not quietly averaged in.
"""
import argparse, json, math, os, sys, tempfile
import numpy as np
from PIL import Image
from scipy import ndimage, optimize

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))   # ce-designs/halo
IMGDIR = os.path.join(REPO, 'images', 'airtag')

PASS, FAIL, CANNOT = 0, 1, 2
V = {PASS: 'PASS', FAIL: 'FAIL', CANNOT: 'CANNOT DETERMINE'}

# ---------------------------------------------------------------- known views
# Approximate board circle in each view. These are SEEDS for the search, not
# measurements; the fit moves off them and the fit is what is reported.
VIEWS = {
    'fcc6-front': dict(
        path='fcc-BCGA2187-internal-photo-6.jpg',
        centre=(952.57, 678.36), r=195.69,
        face='FRONT (component side)',
        note="FCC BCGA2187 internal photo 6, captioned 'MLB - Front'. Board circle "
             "seed from metrology/board-outline-photo6.json (lane L1).",
        px_per_mm=15.887545712881764,
        px_per_mm_basis="metrology/ruler-calibration.json photo6_bottom: 93 ticks / 97 mm, "
                        "stderr 0.0022 px/mm, split-half 0.33%. The RIGHT rule in the same "
                        "frame gives 15.5651 px/mm - a 2.07% disagreement that this tool "
                        "does NOT resolve and does not hide.",
    ),
    'oflynn-front': dict(
        path='oflynn-backside-fullres.jpeg',
        centre=(1405.0, 1700.0), r=1287.5,
        face='FRONT (component side)',
        note="O'Flynn 'backside-fullres' - same face as fcc6-front, ~6.5x finer. "
             "NO scale reference of its own. Circle seed read off a 4x grid overlay.",
        px_per_mm=None, px_per_mm_basis=None,
    ),
    'oflynn-back': dict(
        path='oflynn-frontside-fullres.jpeg',
        centre=(1174.0, 1172.0), r=1090.0,
        face='BACK (test-point side)',
        note="O'Flynn 'frontside-fullres' - the OPPOSITE face. Present only as the "
             "WRONG-FACE negative control.",
        px_per_mm=None, px_per_mm_basis=None,
    ),
}

# ------------------------------------------------------------------ utilities
def gray(path):
    return np.asarray(Image.open(path).convert('L'), dtype=np.float64)

def feature(a, sigma=1.4):
    """Gradient magnitude of a blurred image. Chosen because the two photographs
    differ in exposure, white balance and sensor; edge STRUCTURE survives that,
    raw intensity does not."""
    b = ndimage.gaussian_filter(a, sigma)
    gy, gx = np.gradient(b)
    return np.hypot(gx, gy)

def resolve_view(name_or_path):
    if name_or_path in VIEWS:
        v = dict(VIEWS[name_or_path]); v['name'] = name_or_path
        v['abspath'] = os.path.join(IMGDIR, v['path']); return v
    p = os.path.abspath(name_or_path)
    return dict(name=os.path.basename(p), path=p, abspath=p, centre=None, r=None,
                face='UNSTATED', note='ad-hoc path, no catalogue entry',
                px_per_mm=None, px_per_mm_basis=None)


class Frame:
    """A board view reduced to a working raster: the target keeps full resolution,
    the source is pre-averaged down to roughly the target's sampling so that
    warping is not aliasing a 6x finer image."""
    def __init__(self, view, downsample=1.0, crop=None):
        self.view = view
        self.k = float(downsample)
        im = Image.open(view['abspath']).convert('L')
        self.full_size = im.size
        if self.k != 1.0:
            im = im.resize((max(1,int(im.width/self.k)), max(1,int(im.height/self.k))),
                           Image.LANCZOS)
        a = np.asarray(im, dtype=np.float64)
        self.ox, self.oy = 0.0, 0.0
        if crop is not None:
            x0, y0, x1, y1 = crop
            a = a[y0:y1, x0:x1]; self.ox, self.oy = float(x0), float(y0)
        self.img = a
        self.feat = feature(a)
        self.cx = view['centre'][0]/self.k - self.ox
        self.cy = view['centre'][1]/self.k - self.oy
        self.r = view['r']/self.k

    def to_full(self, x, y):
        return (x + self.ox) * self.k, (y + self.oy) * self.k
    def from_full(self, X, Y):
        return X/self.k - self.ox, Y/self.k - self.oy


# ------------------------------------------------------------- transform model
def sim_matrix(theta_deg, s, tx, ty, src, tgt):
    """Homogeneous 3x3 mapping TARGET frame px -> SOURCE frame px."""
    th = math.radians(theta_deg); ct, st = math.cos(th), math.sin(th)
    A = np.array([[ct/s, st/s, 0.0], [-st/s, ct/s, 0.0], [0, 0, 1.0]])
    Tt = np.array([[1, 0, -tgt.cx - tx], [0, 1, -tgt.cy - ty], [0, 0, 1.0]])
    B = np.array([[1, 0, src.cx], [0, 1, src.cy], [0, 0, 1.0]])
    return B @ A @ Tt

def apply_H(H, X, Y):
    d = H[2, 0]*X + H[2, 1]*Y + H[2, 2]
    return (H[0, 0]*X + H[0, 1]*Y + H[0, 2])/d, (H[1, 0]*X + H[1, 1]*Y + H[1, 2])/d


def ncc_score(H, src, tgt, mask):
    X = tgt._X[mask]; Y = tgt._Y[mask]
    sx, sy = apply_H(H, X, Y)
    v = ndimage.map_coordinates(src.feat, [sy, sx], order=1, mode='constant', cval=np.nan)
    g = np.isfinite(v)
    if g.sum() < 1500:
        return -1.0
    a = v[g]; b = tgt.feat[mask][g]
    a = a - a.mean(); b = b - b.mean()
    d = math.sqrt((a*a).sum() * (b*b).sum())
    return float((a*b).sum()/d) if d > 0 else -1.0


def build_mask(tgt, r_frac_lo=0.0, r_frac_hi=0.985, sector=None):
    ny, nx = tgt.img.shape
    Y, X = np.mgrid[0:ny, 0:nx].astype(np.float64)
    tgt._X, tgt._Y = X, Y
    rr = np.hypot(X - tgt.cx, Y - tgt.cy)
    m = (rr <= r_frac_hi*tgt.r) & (rr >= r_frac_lo*tgt.r)
    if sector is not None:
        a0, a1 = sector
        th = (np.degrees(np.arctan2(Y - tgt.cy, X - tgt.cx)) + 360.0) % 360.0
        m &= ((th - a0) % 360.0) < ((a1 - a0) % 360.0 or 360.0)
    return m


def register(src, tgt, model='homography', quiet=True):
    """Coarse similarity sweep -> refine similarity -> affine -> homography."""
    mask = build_mask(tgt)
    s0 = tgt.r / src.r
    best = None
    for theta in np.arange(-180, 180, 3.0):
        for sf in (0.92, 1.0, 1.08):
            H = sim_matrix(theta, s0*sf, 0, 0, src, tgt)
            v = ncc_score(H, src, tgt, mask)
            if best is None or v > best[0]:
                best = (v, theta, s0*sf)
    _, th0, sc0 = best
    for theta in np.arange(th0-4, th0+4.01, 0.5):
        for sf in np.arange(0.90, 1.101, 0.02):
            for tx in (-10, 0, 10):
                for ty in (-10, 0, 10):
                    H = sim_matrix(theta, (tgt.r/src.r)*sf, tx, ty, src, tgt)
                    v = ncc_score(H, src, tgt, mask)
                    if v > best[0]:
                        best = (v, theta, (tgt.r/src.r)*sf, tx, ty)
    if len(best) == 3:
        best = best + (0.0, 0.0)
    coarse = dict(ncc=best[0], theta_deg=best[1], scale=best[2], tx=best[3], ty=best[4])

    f = lambda p: -ncc_score(sim_matrix(*p, src, tgt), src, tgt, mask)
    r = optimize.minimize(f, [best[1], best[2], best[3], best[4]], method='Nelder-Mead',
                          options=dict(xatol=1e-5, fatol=1e-8, maxiter=6000, maxfev=6000))
    H = sim_matrix(*r.x, src, tgt)
    stages = [dict(model='similarity', ncc=float(-r.fun),
                   theta_deg=float(r.x[0]), scale=float(r.x[1]))]

    def refine(H_in, ndof):
        p0 = (H_in/H_in[2, 2]).ravel()[:ndof]
        step = np.array([1, 1, 60, 1, 1, 60, 3e-5, 3e-5])[:ndof]
        def g(q):
            p = list(p0 + q*step) + [0.0]*(8-ndof) + [1.0]
            return -ncc_score(np.array(p).reshape(3, 3), src, tgt, mask)
        rr_ = optimize.minimize(g, np.zeros(ndof), method='Nelder-Mead',
                                options=dict(xatol=1e-7, fatol=1e-9,
                                             maxiter=4000*ndof, maxfev=4000*ndof))
        p = list(p0 + rr_.x*step) + [0.0]*(8-ndof) + [1.0]
        return np.array(p).reshape(3, 3), float(-rr_.fun)

    if model in ('affine', 'homography'):
        H, n = refine(H, 6); stages.append(dict(model='affine', ncc=n))
    if model == 'homography':
        H2, n2 = refine(H, 8)
        if n2 >= stages[-1]['ncc']:
            H = H2
        stages.append(dict(model='homography', ncc=n2,
                           kept=bool(n2 >= stages[-1]['ncc'])))
    return H, stages, coarse, mask


def null_distribution(H, src, tgt, mask, offsets=(30, 60, 90, 120, 150, 180, -30, -60, -90, -120, -150)):
    """The SAME score at deliberately wrong rotations about the board centre.
    This is the control: a score that does not stand clear of this is not a fit."""
    out = []
    for d in offsets:
        th = math.radians(d); ct, st = math.cos(th), math.sin(th)
        R = np.array([[ct, -st, 0], [st, ct, 0], [0, 0, 1.0]])
        Tm = np.array([[1, 0, -tgt.cx], [0, 1, -tgt.cy], [0, 0, 1.0]])
        Tp = np.array([[1, 0, tgt.cx], [0, 1, tgt.cy], [0, 0, 1.0]])
        out.append((d, ncc_score(H @ Tp @ R @ Tm, src, tgt, mask)))
    return out


# ------------------------------------------------------------------ landmarks
def landmark_field(H, src, tgt, step=14, patch=15, search=5,
                   min_texture=None, min_peak=0.45, ambiguity=0.80,
                   r_lo=0.42, r_hi=0.95):
    """Grid the board in TARGET space. At each node, render the warped source and
    find the local shift that best aligns it to the target. If the transform is
    right, every shift is ~0; the SPREAD of those shifts is the transfer error.

    A node is DISCARDED, and the reason recorded, when:
      no_texture   - the target patch has too little gradient energy to localise
      low_peak     - the best local correlation is weak
      ambiguous    - a second peak rivals the best one (periodic pad arrays do this)
      on_boundary  - the peak sits on the edge of the search window, so it is a
                     lower bound on the shift, not a measurement of it
      off_source   - the patch maps outside the source image
    """
    ny, nx = tgt.img.shape
    Y, X = np.mgrid[0:ny, 0:nx].astype(np.float64)
    sx, sy = apply_H(H, X, Y)
    warped = ndimage.map_coordinates(src.feat, [sy, sx], order=1,
                                     mode='constant', cval=np.nan)
    valid = np.isfinite(warped)
    wf = np.where(valid, warped, 0.0)
    tf = tgt.feat
    half = patch//2
    tex_all = []
    nodes = []
    for cy in range(half+search, ny-half-search, step):
        for cx in range(half+search, nx-half-search, step):
            rr = math.hypot(cx-tgt.cx, cy-tgt.cy)
            if not (r_lo*tgt.r <= rr <= r_hi*tgt.r):
                continue
            tp = tf[cy-half:cy+half+1, cx-half:cx+half+1]
            tex_all.append(float(tp.std()))
            nodes.append((cx, cy, rr, tp))
    if not nodes:
        return [], {'no_nodes': 1}, tex_all
    if min_texture is None:
        min_texture = float(np.percentile(tex_all, 40))

    kept, disc = [], {}
    def bump(k): disc[k] = disc.get(k, 0) + 1
    for cx, cy, rr, tp in nodes:
        if tp.std() < min_texture:
            bump('no_texture'); continue
        if not valid[cy-half-search:cy+half+search+1, cx-half-search:cx+half+search+1].all():
            bump('off_source'); continue
        surf = np.full((2*search+1, 2*search+1), -2.0)
        a = tp - tp.mean(); na = math.sqrt((a*a).sum())
        if na == 0:
            bump('no_texture'); continue
        for dy in range(-search, search+1):
            for dx in range(-search, search+1):
                wp = wf[cy+dy-half:cy+dy+half+1, cx+dx-half:cx+dx+half+1]
                b = wp - wp.mean(); nb = math.sqrt((b*b).sum())
                if nb == 0:
                    continue
                surf[dy+search, dx+search] = float((a*b).sum()/(na*nb))
        iy, ix = np.unravel_index(np.argmax(surf), surf.shape)
        peak = surf[iy, ix]
        if peak < min_peak:
            bump('low_peak'); continue
        if iy in (0, 2*search) or ix in (0, 2*search):
            bump('on_boundary'); continue
        m2 = surf.copy()
        m2[max(0, iy-2):iy+3, max(0, ix-2):ix+3] = -2.0
        second = float(m2.max())
        if second > ambiguity*peak:
            bump('ambiguous'); continue
        # parabolic sub-pixel
        def sub(c, l, r_):
            d = (l - 2*c + r_)
            return 0.0 if d == 0 else 0.5*(l - r_)/d
        ddx = sub(peak, surf[iy, ix-1], surf[iy, ix+1])
        ddy = sub(peak, surf[iy-1, ix], surf[iy+1, ix])
        shift = ((ix-search)+ddx, (iy-search)+ddy)
        th = (math.degrees(math.atan2(cy-tgt.cy, cx-tgt.cx)) + 360.0) % 360.0
        kept.append(dict(tx=float(cx), ty=float(cy), r=float(rr), theta_deg=float(th),
                         dx=float(shift[0]), dy=float(shift[1]),
                         peak=float(peak), second=float(second)))
    return kept, disc, tex_all


def fit_homography_dlt(P, Q):
    """Least-squares homography mapping P (target px) -> Q (source px)."""
    A = []
    for (x, y), (u, v) in zip(P, Q):
        A.append([x, y, 1, 0, 0, 0, -u*x, -u*y, -u])
        A.append([0, 0, 0, x, y, 1, -v*x, -v*y, -v])
    A = np.asarray(A, dtype=np.float64)
    _, _, Vt = np.linalg.svd(A)
    H = Vt[-1].reshape(3, 3)
    return H / H[2, 2]


# ------------------------------------------------------------------- pipeline
def prepare(src_name, tgt_name, downsample=None):
    sv, tv = resolve_view(src_name), resolve_view(tgt_name)
    for v in (sv, tv):
        if v['centre'] is None:
            raise SystemExit("no board circle seed for %s - only catalogue views are "
                             "supported (%s)" % (v['name'], ', '.join(VIEWS)))
    if downsample is None:
        downsample = max(1.0, round(sv['r']/tv['r'], 2))
    src = Frame(sv, downsample=downsample)
    tgt = Frame(tv, downsample=1.0,
                crop=(int(tv['centre'][0]-1.12*tv['r']), int(tv['centre'][1]-1.12*tv['r']),
                      int(tv['centre'][0]+1.12*tv['r']), int(tv['centre'][1]+1.12*tv['r'])))
    return src, tgt, downsample


def transfer_scale(H, src, tgt, tgt_px_per_mm):
    """px/mm in the SOURCE image, carried across the registration.
    A homography has no single scale, so this is reported as the mean over the
    board area together with its spread - and the spread is the honest statement
    that a tilted view has no one scale."""
    ny, nx = tgt.img.shape
    vals = []
    for cy in np.linspace(0.2*ny, 0.8*ny, 9):
        for cx in np.linspace(0.2*nx, 0.8*nx, 9):
            if math.hypot(cx-tgt.cx, cy-tgt.cy) > 0.95*tgt.r:
                continue
            e = 1.0
            x0, y0 = apply_H(H, cx, cy)
            x1, y1 = apply_H(H, cx+e, cy)
            x2, y2 = apply_H(H, cx, cy+e)
            J = abs((x1-x0)*(y2-y0) - (x2-x0)*(y1-y0))      # source px per target px^2
            vals.append(math.sqrt(J))
    v = np.array(vals)
    # source px per target px, times target px per mm, in SOURCE full-res px
    return (v * tgt_px_per_mm * src.k), v


def run_fit(a):
    src, tgt, ds = prepare(a.source, a.target, a.downsample)
    print("c_register fit")
    print("  SIDE CONVENTION  FRONT = component side (Apple FCC caption 'MLB - Front')")
    print("  SOURCE  %s  %s" % (src.view['name'], src.view['path']))
    print("          face=%s  seed centre=(%.1f,%.1f) r=%.1f  pre-averaged /%.2f"
          % (src.view['face'], src.view['centre'][0], src.view['centre'][1], src.view['r'], ds))
    print("  TARGET  %s  %s" % (tgt.view['name'], tgt.view['path']))
    print("          face=%s  seed centre=(%.1f,%.1f) r=%.1f  crop=(%d,%d)"
          % (tgt.view['face'], tgt.view['centre'][0], tgt.view['centre'][1], tgt.view['r'],
             tgt.ox, tgt.oy))
    print("  METHOD  gradient-magnitude NCC, coarse similarity sweep -> %s" % a.model)

    H, stages, coarse, mask = register(src, tgt, model=a.model)
    for s in stages:
        print("    %-11s NCC %.4f" % (s['model'], s['ncc']))
    ncc = stages[-1]['ncc']

    null = null_distribution(H, src, tgt, mask)
    nvals = np.array([v for _, v in null])
    print("  NULL CONTROL  same score at wrong rotations: max %.4f  mean %.4f  (n=%d)"
          % (nvals.max(), nvals.mean(), len(nvals)))
    margin = ncc/max(nvals.max(), 1e-9)
    print("                fit / worst-case null = %.2fx  (floor %.2fx)" % (margin, a.min_margin))

    lm, disc, tex = landmark_field(H, src, tgt, step=a.step, patch=a.patch, search=a.search)
    ndisc = sum(disc.values())
    print("  LANDMARKS  %d kept, %d discarded  %s"
          % (len(lm), ndisc, ' '.join('%s=%d' % kv for kv in sorted(disc.items()))))
    out = dict(tool='c_register.py', verb='fit',
               side_convention="FRONT = component side (Apple FCC 'MLB - Front'); "
                               "O'Flynn 'backside' is this FRONT",
               source=dict(name=src.view['name'], path=src.view['path'], face=src.view['face'],
                           note=src.view['note'], seed_centre=src.view['centre'],
                           seed_r=src.view['r'], pre_average=ds, full_size=src.full_size),
               target=dict(name=tgt.view['name'], path=tgt.view['path'], face=tgt.view['face'],
                           note=tgt.view['note'], seed_centre=tgt.view['centre'],
                           seed_r=tgt.view['r'], crop_origin=[tgt.ox, tgt.oy],
                           px_per_mm=tgt.view['px_per_mm'],
                           px_per_mm_basis=tgt.view['px_per_mm_basis']),
               method='gradient-magnitude NCC; coarse similarity sweep then Nelder-Mead',
               model=a.model, coarse=coarse, stages=stages, ncc=ncc,
               null_control=dict(offsets_deg=[d for d, _ in null],
                                 ncc=[v for _, v in null], max=float(nvals.max()),
                                 mean=float(nvals.mean()), margin=float(margin),
                                 min_margin_required=a.min_margin),
               H_target_to_source_cropframe=H.tolist(),
               landmarks=dict(kept=len(lm), discarded=disc, discarded_total=ndisc))

    if len(lm) >= 8:
        d = np.array([[l['dx'], l['dy']] for l in lm])
        rms = float(np.sqrt((d**2).sum(axis=1).mean()))
        out['landmarks']['residual_px_rms_in_sample'] = rms
        print("  IN-SAMPLE landmark residual RMS %.3f px  (NOT a validation - see `validate`)" % rms)

    verdict = PASS
    why = []
    if ncc < a.min_ncc:
        verdict = CANNOT; why.append("alignment score %.4f below floor %.2f" % (ncc, a.min_ncc))
    if margin < a.min_margin:
        verdict = CANNOT; why.append("fit only %.2fx its own null (floor %.2f) - not "
                                     "distinguishable from a wrong alignment" % (margin, a.min_margin))
    if len(lm) < a.min_landmarks:
        verdict = CANNOT; why.append("only %d usable landmarks (need %d)" % (len(lm), a.min_landmarks))
    out['verdict'] = V[verdict]; out['why'] = why
    if a.json_out:
        with open(a.json_out, 'w') as fh: json.dump(out, fh, indent=1)
        print("  wrote %s" % a.json_out)
    print("  %s%s" % (V[verdict], (': ' + '; '.join(why)) if why else ''))
    return verdict


def run_validate(a):
    """SPATIAL HOLD-OUT. Fit the transform on landmarks in one angular sector,
    predict landmarks in the sector it never saw, measure the error there.
    What would have to be true for this to disagree: if the registration were
    only locally right - matching the sector it was fitted on and drifting
    elsewhere - the held-out sector's residual would blow up while the in-sample
    one stayed small. That is the disagreement this test can see."""
    src, tgt, ds = prepare(a.source, a.target, a.downsample)
    print("c_register validate  (spatial hold-out)")
    print("  SOURCE %s   TARGET %s" % (src.view['path'], tgt.view['path']))
    H, stages, coarse, mask = register(src, tgt, model=a.model)
    lm, disc, _ = landmark_field(H, src, tgt, step=a.step, patch=a.patch, search=a.search)
    print("  landmarks %d kept, %d discarded %s"
          % (len(lm), sum(disc.values()), ' '.join('%s=%d' % kv for kv in sorted(disc.items()))))
    if len(lm) < a.min_landmarks:
        print("  CANNOT DETERMINE: %d landmarks, need %d" % (len(lm), a.min_landmarks))
        return CANNOT

    # each landmark's TRUE source correspondence, from the local shift
    P = np.array([[l['tx']+l['dx'], l['ty']+l['dy']] for l in lm])       # target px (corrected)
    Q = np.array([apply_H(H, l['tx'], l['ty']) for l in lm])             # source px
    th = np.array([l['theta_deg'] for l in lm])

    ppm = tgt.view['px_per_mm']
    folds = []
    K = a.folds
    for i in range(K):
        a0, a1 = 360.0*i/K, 360.0*(i+1)/K
        held = (th >= a0) & (th < a1)
        fit = ~held
        if held.sum() < 4 or fit.sum() < 12:
            folds.append(dict(sector=[a0, a1], n_held=int(held.sum()),
                              verdict='CANNOT DETERMINE', why='too few landmarks in fold'))
            continue
        Hf = fit_homography_dlt(P[fit], Q[fit])
        px, py = apply_H(Hf, P[held][:, 0], P[held][:, 1])
        err = np.hypot(px-Q[held][:, 0], py-Q[held][:, 1]) / (src.k)      # source FULL-RES px
        # express in TARGET px (the frame the ruler lives in) and in mm
        src_px_per_tgt_px = math.sqrt(abs(np.linalg.det(Hf[:2, :2]))) * 1.0
        err_tgt = err * src.k / (src_px_per_tgt_px * src.k) if src_px_per_tgt_px else np.nan
        folds.append(dict(sector=[a0, a1], n_held=int(held.sum()), n_fit=int(fit.sum()),
                          rms_source_px=float(np.sqrt((err**2).mean())),
                          p95_source_px=float(np.percentile(err, 95)),
                          rms_target_px=float(np.sqrt((err_tgt**2).mean())),
                          rms_mm=float(np.sqrt((err_tgt**2).mean())/ppm) if ppm else None))
    print("  %-16s %5s %10s %10s %9s" % ('held-out sector', 'n', 'RMS src px', 'RMS tgt px', 'RMS mm'))
    ok = []
    for f in folds:
        if 'rms_mm' not in f:
            print("  %5.0f-%-9.0f %5d   %s" % (f['sector'][0], f['sector'][1], f['n_held'], f.get('why', '')))
            continue
        ok.append(f)
        print("  %5.0f-%-9.0f %5d %10.2f %10.3f %9.4f"
              % (f['sector'][0], f['sector'][1], f['n_held'],
                 f['rms_source_px'], f['rms_target_px'], f['rms_mm']))
    verdict = PASS; why = []
    if not ok:
        verdict = CANNOT; why.append('no fold had enough landmarks')
        worst = None
    else:
        worst = max(f['rms_mm'] for f in ok)
        print("  WORST held-out fold: %.4f mm  (tolerance %.4f mm)" % (worst, a.tol_mm))
        if worst > a.tol_mm:
            verdict = FAIL
            why.append("worst held-out RMS %.4f mm exceeds tolerance %.4f mm" % (worst, a.tol_mm))
    out = dict(tool='c_register.py', verb='validate',
               side_convention="FRONT = component side (Apple FCC 'MLB - Front')",
               source=src.view['path'], target=tgt.view['path'],
               scale_basis=tgt.view['px_per_mm_basis'], px_per_mm=ppm,
               model=a.model, ncc=stages[-1]['ncc'], folds=folds,
               worst_holdout_rms_mm=worst, tolerance_mm=a.tol_mm,
               landmarks_kept=len(lm), landmarks_discarded=disc,
               verdict=V[verdict], why=why)
    if a.json_out:
        with open(a.json_out, 'w') as fh: json.dump(out, fh, indent=1)
        print("  wrote %s" % a.json_out)
    print("  %s%s" % (V[verdict], (': ' + '; '.join(why)) if why else ''))
    return verdict
