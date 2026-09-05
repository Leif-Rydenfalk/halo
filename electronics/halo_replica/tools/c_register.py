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
        px_per_mm=15.6850,
        px_per_mm_basis="metrology/scale-at-board-photo6.json - m_scale_at AT THE BOARD "
                        "(952,678), bottom-rule and right-rule routes 0.228% apart, "
                        "halfrange 0.0179 px/mm (lane L1, M02). THE SCALE IS TAKEN AT THE "
                        "BOARD, not at either rule.",
        px_per_mm_note="DEFAULT CORRECTED 2026-09-05 by L2: 15.887546 -> 15.6850.\n"
                       "The old default was photo 6's BOTTOM RULE measured AT THE RULE,\n"
                       "and the board does not sit on that rule. Its sibling view\n"
                       "fcc7-back already defaulted to an AT-THE-BOARD scale (L9), so the\n"
                       "two entries of one catalogue defaulted to different KINDS of\n"
                       "number, and only the FRONT one was wrong. The error was 1.29% in\n"
                       "the FLATTERING direction: every held-out mm computed against the\n"
                       "old default came out 1.29% SMALLER than the truth.\n"
                       "The rule's own value, still true of the rule, is 15.887546 px/mm\n"
                       "(93 ticks / 97 mm, stderr 0.0022, split-half 0.33%); photo 6's\n"
                       "RIGHT rule reads 15.5651, a 2.07% rule-to-rule disagreement that\n"
                       "m_scale_at resolves by interpolating TO THE BOARD.\n"
                       "Pass --target-px-per-mm 15.887546 for the old behaviour.",
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
        centre=(1174.0, 1172.0), r=962.0,
        face='BACK (test-point side)',
        note="O'Flynn 'frontside-fullres' - the OPPOSITE face. Serves TWO roles: the "
             "WRONG-FACE negative control for a FRONT registration, and (added by lane "
             "L9, 2026-09-05) the SOURCE for a BACK registration against fcc7-back. "
             "SEED RADIUS CORRECTED 1090 -> 962 by L9: 1090 traces the plastic antenna "
             "carrier, not the board. 962 = M06's measured board span of 1924 px / 2. "
             "The old seed put the true scale ratio 13.3% out, beyond the fit's +-10% "
             "refine window, so a BACK registration could not have converged with it. "
             "IT IS STILL A SEED, NOT A MEASUREMENT - the fit moves off it.",
        px_per_mm=None, px_per_mm_basis=None,
    ),
    'fcc7-back': dict(
        path='fcc-BCGA2187-internal-photo-7.jpg',
        centre=(935.25, 755.395), r=187.482,
        face='BACK (test-point / battery-contact side)',
        note="FCC BCGA2187 internal photo 7, captioned 'MLB - Back'. Added by lane L9, "
             "2026-09-05, so the BACK face has a scale donor at all - before this the "
             "catalogue held no ruler-bearing view of this face and no BACK registration "
             "was possible. Board circle seed from metrology/outline-fit-photo7.json "
             "(cx 935.25, cy 755.395, circle_fit_radius_px 187.482, lane L1). "
             "*** THIS IS NOT THE SAME PHYSICAL BOARD AS oflynn-back. *** Its silkscreen "
             "reads 920-08283-01 with data code 3119 (a 2019 engineering build); "
             "O'Flynn's reads 820-01736-A, data code 2920 17 (2020 production). Whether "
             "the two share dimensions is CANNOT DETERMINE and is NOT assumed - see the "
             "warning under px_per_mm_basis. The same caveat already applies, unstated, "
             "to the FRONT pair fcc6-front / oflynn-front.",
        px_per_mm=15.0719,
        px_per_mm_basis="metrology/scale-at-board-photo7.json - m_scale_at at the board "
                        "(932,752), bottom rule and right rule routes 0.45% apart, "
                        "halfrange 0.0339 px/mm. THE SCALE IS MEASURED AT THE BOARD, not "
                        "at the rule, so it does not carry the 1.29% rule-to-board error. "
                        "*** THE ASSUMPTION THIS SHARES WITH ITS OWN HELD-OUT CONTROL: "
                        "that the 920- sample board and the 820- production board have the "
                        "same dimensions. A uniform dimensional difference between them is "
                        "absorbed into the fitted scale and leaves the held-out residual "
                        "COMPLETELY UNCHANGED, because the check divides both sides by the "
                        "same number. Registration consistency is not scale accuracy. What "
                        "would settle it: a caliper on one board of each part number. ***",
        px_per_mm_note="NOTE: this value is ALREADY AT THE BOARD, not at the rule, so it\n"
                       "carries no rule-to-board transfer error. Its two routes (bottom\n"
                       "rule and right rule) disagree by 0.45%, not photo 6's 2.07%.\n"
                       "The open risk here is a DIFFERENT one: this is the 920- sample\n"
                       "board and the source is the 820- production board.",
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


def radial_structure(lm, tgt, trials=400, seed=13):
    """IS THE COHERENT MISFIT RADIAL, AND ABOUT WHAT?

    R11 established that the registration misfit is a smooth spatially coherent
    field on both faces, and R17 bounded lens distortion in the TARGET frames to
    under ~0.2 px of bow. Two candidates remain and they make DIFFERENT geometric
    predictions, which is what makes this worth measuring:

      * A BOARD THAT IS NOT FLAT displaces features RADIALLY ABOUT THE BOARD'S OWN
        CENTRE, growing with distance from it - a dome or a bow projects that way.
      * OPTICS displace features RADIALLY ABOUT THE IMAGE CENTRE, which for this
        crop is somewhere else entirely.
      * A DIFFERENCE BETWEEN TWO PHYSICAL BOARDS has no reason to be radial about
        anything.

    So decompose each landmark's residual into radial and tangential components
    about each candidate centre, and ask whether the radial part grows with radius.

    The residual field in TARGET pixels is exactly the measured local shift (dx,dy):
    the intensity fit produced H, and these are what it left behind.

    CONTROL: the same statistic with the residual VECTORS PERMUTED among positions,
    which destroys any relationship to geometry and keeps the vectors themselves.
    """
    if len(lm) < 40:
        return None
    P = np.array([[l['tx'], l['ty']] for l in lm])
    D = np.array([[l['dx'], l['dy']] for l in lm])
    ny, nx = tgt.img.shape
    centres = {
        'board centre': (tgt.cx, tgt.cy),
        'target image centre': (tgt.full_size[0]/2.0 - tgt.ox, tgt.full_size[1]/2.0 - tgt.oy),
        'crop centre': (nx/2.0, ny/2.0),
    }
    rng = np.random.default_rng(seed)
    out = {}
    for name, (cx, cy) in centres.items():
        d = P - np.array([cx, cy])
        r = np.hypot(d[:, 0], d[:, 1])
        good = r > 1e-6
        u = d[good]/r[good][:, None]
        tvec = np.column_stack([-u[:, 1], u[:, 0]])
        Dg = D[good]; rg = r[good]
        pr = (Dg*u).sum(axis=1)
        pt = (Dg*tvec).sum(axis=1)

        def corr(vals, rr):
            if vals.std() == 0 or rr.std() == 0:
                return 0.0
            return float(np.corrcoef(vals, rr)[0, 1])

        c_obs = corr(pr, rg)
        null = np.empty(trials)
        for k in range(trials):
            q = rng.permutation(len(Dg))
            Dp = Dg[q]
            null[k] = corr((Dp*u).sum(axis=1), rg)
        m, sd = float(null.mean()), float(null.std())

        # DETECTION LIMIT, for the same reason the coherence statistic has one: a
        # confident negative from an untested check is the mistake this lane made
        # four times on 2026-09-05. Inject a DOME about THIS centre into the real
        # residuals, sweep its amplitude down, and report the smallest one still
        # separable from the null. "No dome" then means "no dome bigger than THIS".
        rms = float(np.sqrt((Dg*Dg).sum(axis=1).mean()))
        Rn = max(rg.max(), 1e-9)
        limit = None
        sweep = []
        for f in (1.0, 0.7, 0.5, 0.35, 0.25, 0.18, 0.12, 0.08):
            inj = Dg + u*(rms*f*(rg/Rn))[:, None]
            ci = corr((inj*u).sum(axis=1), rg)
            zi = (ci-m)/sd if sd > 0 else float('nan')
            sweep.append(dict(frac=f, amp_px=rms*f, z=float(zi)))
            if zi > 3.0:
                limit = f
        out[name] = dict(centre=[float(cx+tgt.ox), float(cy+tgt.oy)],
                         residual_rms_px=rms, dome_sweep=sweep,
                         detection_limit_frac=limit,
                         detection_limit_px=(rms*limit if limit is not None else None),
                         radial_vs_radius_corr=c_obs, null_mean=m, null_sd=sd,
                         z=float((c_obs-m)/sd) if sd > 0 else float('nan'),
                         radial_rms_px=float(np.sqrt((pr**2).mean())),
                         tangential_rms_px=float(np.sqrt((pt**2).mean())),
                         radial_over_tangential=float(np.sqrt((pr**2).mean() /
                                                              max((pt**2).mean(), 1e-12))),
                         n=int(good.sum()))
    return out

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


def fit_ridge(P, Q, lam):
    """Homography PLUS a ridge-penalised quadratic CORRECTION to it.

    R11 measured the registration misfit to be a smooth, spatially coherent field
    on both faces (z = +11.1 and +8.5 against permutation nulls). So there IS
    structure left to capture. But an unregularised poly2 made the front 3.8x
    WORSE (R09/R11 postscript): four free parameters fitted to noisy landmarks
    extrapolate wildly.

    The question was never "more parameters or fewer" - it is HOW FAR the extra
    ones may move. That is lam:
        lam -> infinity   reproduces the homography EXACTLY
        lam -> 0          reproduces the poly2 that failed
    The correction is fitted to the homography's RESIDUAL, so lam penalises
    departure from the homography rather than departure from zero, and the
    homography is what it falls back to rather than a constant.
    """
    H = fit_homography_geometric(P, Q)
    px, py = apply_H(H, P[:, 0], P[:, 1])
    R = np.column_stack([Q[:, 0]-px, Q[:, 1]-py])
    x, y = P[:, 0], P[:, 1]
    mx, my = x.mean(), y.mean()
    sx = max(x.std(), 1e-9); sy = max(y.std(), 1e-9)
    u, v = (x-mx)/sx, (y-my)/sy
    A = np.column_stack([np.ones_like(u), u, v, u*u, u*v, v*v])
    G = A.T @ A + lam*np.eye(A.shape[1])
    cu = np.linalg.solve(G, A.T @ R[:, 0])
    cv = np.linalg.solve(G, A.T @ R[:, 1])
    return ('ridge', H, cu, cv, mx, my, sx, sy)


def _apply_ridge(M, X, Y):
    _, H, cu, cv, mx, my, sx, sy = M
    px, py = apply_H(H, X, Y)
    u, v = (np.asarray(X)-mx)/sx, (np.asarray(Y)-my)/sy
    A = np.column_stack([np.ones_like(u), u, v, u*u, u*v, v*v])
    return px + A @ cu, py + A @ cv


LAMS = (1e7, 1e6, 1e5, 3e4, 1e4, 3e3, 1e3, 300.0, 100.0, 30.0, 10.0, 3.0, 1.0)


def _ang_folds(th, k, off):
    for i in range(k):
        a0, a1 = 360.0*i/k, 360.0*(i+1)/k
        tha = (th - off) % 360.0
        yield (tha >= a0) & (tha < a1)


def ridge_vs_homography(P, Q, th, K=2, offset=0.0, lams=LAMS, inner_K=2):
    """Does the regularised correction actually help? Measured NESTED.

    lam is chosen INSIDE the fitting portion, by a further split of that portion
    alone, and is then applied to the held-out fold which neither the fit nor the
    choice of lam has ever seen.

    Choosing lam on the held-out data would be tuning on the test set. It would
    guarantee an apparent gain, and it is the same family of mistake as everything
    this lane got wrong on 2026-09-05 - a comparison that could not have come out
    against the thing being proposed.
    """
    rows = []
    for held in _ang_folds(th, K, offset):
        fitm = ~held
        if held.sum() < 5 or fitm.sum() < 24:
            continue
        Pf, Qf, thf = P[fitm], Q[fitm], th[fitm]
        best_lam, best_err = None, None
        for lam in lams:
            errs = []
            for ih in _ang_folds(thf, inner_K, offset + 90.0):
                inf_ = ~ih
                if ih.sum() < 4 or inf_.sum() < 14:
                    continue
                M = fit_ridge(Pf[inf_], Qf[inf_], lam)
                ex, ey = _apply_ridge(M, Pf[ih][:, 0], Pf[ih][:, 1])
                errs.append(np.hypot(ex-Qf[ih][:, 0], ey-Qf[ih][:, 1]))
            if not errs:
                continue
            e = float(np.sqrt((np.concatenate(errs)**2).mean()))
            if best_err is None or e < best_err:
                best_lam, best_err = lam, e
        if best_lam is None:
            continue
        Hh = fit_homography_geometric(Pf, Qf)
        hx, hy = apply_H(Hh, P[held][:, 0], P[held][:, 1])
        e_hom = float(np.sqrt((np.hypot(hx-Q[held][:, 0], hy-Q[held][:, 1])**2).mean()))
        M = fit_ridge(Pf, Qf, best_lam)
        rx, ry = _apply_ridge(M, P[held][:, 0], P[held][:, 1])
        e_rid = float(np.sqrt((np.hypot(rx-Q[held][:, 0], ry-Q[held][:, 1])**2).mean()))
        rows.append(dict(lam_chosen=best_lam, n_held=int(held.sum()),
                         homography_rms=e_hom, ridge_rms=e_rid,
                         gain_pct=(100.0*(e_hom-e_rid)/e_hom) if e_hom else 0.0))
    return rows

def fit_homography_geometric(P, Q, iters=200):
    """A homography fitted to minimise GEOMETRIC error, seeded by the DLT.

    *** WHY THIS EXISTS, AND IT MATTERS TO EVERY NUMBER THIS LANE HAS PUBLISHED. ***
    fit_homography_dlt minimises ALGEBRAIC error - the SVD residual of the DLT
    system - which is not the distance anybody cares about and is known to be
    biased. Measured 2026-09-05: a ridge-regularised correction beat the DLT by
    53-79% on synthetic correspondences generated BY A HOMOGRAPHY plus isotropic
    noise, where by construction there was NOTHING for a correction to capture.
    The "gain" was the correction repairing the DLT's own bias.

    That confound would have turned an improvement in the FITTER into a published
    claim about the BOARD. So the baseline is now the best a homography can do,
    and any remaining gain from a richer model is structure rather than slack.
    """
    H = fit_homography_dlt(P, Q)
    p0 = (H/H[2, 2]).ravel()[:8]
    step = np.array([1e-3, 1e-3, 1.0, 1e-3, 1e-3, 1.0, 1e-8, 1e-8])

    def err(q):
        p = list(p0 + q*step) + [1.0]
        Hm = np.array(p).reshape(3, 3)
        x, y = apply_H(Hm, P[:, 0], P[:, 1])
        if not (np.isfinite(x).all() and np.isfinite(y).all()):
            return 1e18
        return float(((x-Q[:, 0])**2 + (y-Q[:, 1])**2).sum())

    r = optimize.minimize(err, np.zeros(8), method='Nelder-Mead',
                          options=dict(xatol=1e-10, fatol=1e-12,
                                       maxiter=iters*80, maxfev=iters*80))
    Hg = np.array(list(p0 + r.x*step) + [1.0]).reshape(3, 3)
    return Hg if err(r.x) <= err(np.zeros(8)) else H

def fit_poly2(P, Q):
    """*** A DISCARDED ROUTE. NOT WIRED TO ANY VERB. Kept so it is not retried. ***

    Least-squares 2nd-order polynomial, target px -> source px: 12 parameters
    against a homography's 8.  It was written to separate two causes of the
    homography misfit that R08 measured on the BACK face - a smooth geometric
    cause (a board that is not flat, or uncorrected lens distortion) from a
    component-wise one (two different physical boards whose parts sit in slightly
    different places) - on the reasoning that a low-order model absorbs the first
    and cannot absorb the second.

    IT FAILED ITS OWN POSITIVE CONTROL, 2026-09-05, and is therefore not used.
    Given a 5% radial warp INJECTED ON PURPOSE, poly2's held-out error came out
    WORSE than the homography's, under both splits:
        extrapolating (K=2):  3.759 px  vs the homography's 3.393 px
        interpolating (K=4):  1.834 px  vs the homography's 1.473 px
    With ~60 noisy landmarks the four extra parameters cost more than the warp
    they were meant to capture.  A discriminator that cannot see a defect planted
    for it to see is not a discriminator, and shipping it would have meant reading
    "poly2 did not help" on the real data as evidence about the BOARD when it is
    only evidence about the METHOD.  The cause of the back face's azimuthal misfit
    stays CANNOT DETERMINE.  `validate --coherence` asks a related question
    without adding any parameters at all.
    """
    x, y = P[:, 0], P[:, 1]
    # centre and scale the design matrix, or the x^2 column is ~1e6 and the
    # normal equations lose the linear terms to rounding
    mx, my = x.mean(), y.mean()
    sx = max(x.std(), 1e-9); sy = max(y.std(), 1e-9)
    u, v = (x-mx)/sx, (y-my)/sy
    A = np.column_stack([np.ones_like(u), u, v, u*u, u*v, v*v])
    if A.shape[0] < A.shape[1] + 2:
        return None
    cu, *_ = np.linalg.lstsq(A, Q[:, 0], rcond=None)
    cv, *_ = np.linalg.lstsq(A, Q[:, 1], rcond=None)
    return ('poly2', cu, cv, mx, my, sx, sy)


def apply_model(M, X, Y):
    """Evaluate either model at target coordinates."""
    if isinstance(M, tuple) and M[0] == 'poly2':
        _, cu, cv, mx, my, sx, sy = M
        u, v = (np.asarray(X)-mx)/sx, (np.asarray(Y)-my)/sy
        A = np.column_stack([np.ones_like(u), u, v, u*u, u*v, v*v])
        return A @ cu, A @ cv
    return apply_H(M, X, Y)


def residual_coherence(P, Q, k=4, trials=400, seed=11):
    """Is the misfit SMOOTH or COMPONENT-WISE? - asked without adding a parameter.

    Fit the homography on ALL landmarks, take each one's residual VECTOR, and
    measure how well it agrees with the mean residual of its k nearest
    NEIGHBOURS, itself excluded.  A smooth geometric cause - a board that is not
    flat, uncorrected lens distortion - moves neighbouring points TOGETHER, so
    the field is spatially coherent.  Parts sitting in different places on two
    different physical boards move independently, so it is not.

    Statistic: the mean over landmarks of the cosine-weighted projection of each
    residual onto its neighbourhood mean, normalised - a Moran's-I in spirit.

    THE CONTROL, and it is the whole reason this is trustworthy: the SAME
    statistic is recomputed with the residuals PERMUTED among the positions,
    hundreds of times.  Permutation destroys every spatial relationship and keeps
    the residual magnitudes exactly as they are, so the null says what this
    statistic reads on a field with no structure at all.  A value that does not
    stand clear of that null is not coherence.

    Returns (I, null_mean, null_sd, z).  It does NOT return a cause: a coherent
    field is consistent with a warp AND with a uniformly displaced region, and
    this cannot separate those.
    """
    H = fit_homography_dlt(P, Q)
    px, py = apply_H(H, P[:, 0], P[:, 1])
    R = np.column_stack([Q[:, 0]-px, Q[:, 1]-py])
    n = len(P)
    if n < k+4:
        return None
    d = np.hypot(P[:, 0][:, None]-P[:, 0][None, :], P[:, 1][:, None]-P[:, 1][None, :])
    np.fill_diagonal(d, np.inf)
    nb = np.argsort(d, axis=1)[:, :k]

    def stat(Rv):
        Rc = Rv - Rv.mean(axis=0)
        num = 0.0
        den = float((Rc*Rc).sum())
        for i in range(n):
            num += float((Rc[i]*Rc[nb[i]].mean(axis=0)).sum())
        return num/den if den > 0 else 0.0

    I = stat(R)
    rng = np.random.default_rng(seed)

    def zof(Rv):
        Iv = stat(Rv)
        nl = np.empty(trials)
        for t in range(trials):
            nl[t] = stat(Rv[rng.permutation(n)])
        m_, sd_ = float(nl.mean()), float(nl.std())
        return Iv, m_, sd_, ((Iv-m_)/sd_ if sd_ > 0 else float('nan'))

    I, m, sd, z = zof(R)

    # POWER PROBE - and it exists because its absence produced a wrong published
    # conclusion.  On 2026-09-05 this statistic read z=+1.4 on the BACK face with
    # 58 landmarks and R09 published "a smooth geometric cause is RULED OUT".  The
    # same face with 192 landmarks reads z=+8.5.  The low z was not evidence of
    # absence, it was ABSENCE OF POWER, and nothing in the output said so.
    #
    # So: inject a SMOOTH radial warp into the ACTUAL residuals, sized to the
    # residuals already present, and re-score.  If the injected z does not clear
    # the threshold, this landmark set CANNOT detect a smooth field and a low z
    # means CANNOT DETERMINE - never "ruled out".
    c = P.mean(axis=0); d = P - c
    rr = np.hypot(d[:, 0], d[:, 1]); Rn = max(rr.max(), 1e-9)
    rms = float(np.sqrt((R*R).sum(axis=1).mean()))
    shape = d/np.maximum(rr, 1e-9)[:, None] * ((rr/Rn)**2)[:, None]

    # A FIRST VERSION OF THIS PROBE WAS ALSO WRONG, 2026-09-05, and the failure is
    # kept here because it is the instructive one.  It injected ONE warp, sized to
    # the FULL residual RMS, and reported POWERED / UNDERPOWERED.  On the back
    # face's 58 landmarks it said POWERED (injected z=+5.1) while the observed
    # z was +1.4 -- and the same face at 192 landmarks then read z=+8.5.  So the
    # probe passed the set that had just got the answer wrong.  The reason: the
    # real coherent component is a FRACTION of the residual RMS, most of which is
    # localisation noise, so a probe at full RMS tests for a warp far larger than
    # the one in question.  A yes/no at one over-large effect size is not power.
    #
    # What replaces it: sweep the injected amplitude DOWN and report the smallest
    # one this landmark set can still see.  A low observed z then means something
    # precise -- "no coherent component larger than THIS" -- instead of "none".
    fracs = [1.0, 0.7, 0.5, 0.35, 0.25, 0.18, 0.12, 0.08]
    sweep, limit = [], None
    for f in fracs:
        _, _, _, zf = zof(R + shape*(rms*f))
        sweep.append(dict(frac=f, amp_px=rms*f, z=float(zf)))
        if zf > 3.0:
            limit = f
    return dict(I=float(I), null_mean=m, null_sd=sd, z=float(z), k=k, trials=trials, n=n,
                residual_rms_px=rms, power_sweep=sweep,
                detection_limit_frac=limit,
                detection_limit_px=(rms*limit if limit is not None else None),
                powered=bool(limit is not None and limit <= 0.5),
                power_note="detection_limit_* is the SMALLEST smooth radial warp, injected "
                           "into the real residuals, that this landmark set can still "
                           "distinguish from its permutation null at z>3. A low observed z "
                           "bounds any coherent component BELOW that amplitude - it never "
                           "means there is none.")


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
def apply_scale_override(tgt, a):
    """Let the caller supply the px/mm measured AT THE BOARD rather than at the rule.

    WHY THIS MATTERS AND WHY THE HELD-OUT ERROR CANNOT SEE IT.  `validate` fits the
    transform and measures its error on held-out landmarks, converting BOTH to mm
    with the SAME px/mm.  A wrong scale divides both sides equally, so it cancels:
    the held-out RMS is a statement about REGISTRATION CONSISTENCY and carries no
    information about SCALE ACCURACY at all.  A 1.29% scale error and a 0.1029 mm
    held-out error can coexist happily, and the second does not warn you about the
    first -- the check shares its assumption with the thing it checks.
    """
    if a.target_px_per_mm is None:
        if tgt.view.get('px_per_mm'):
            print("  SCALE BASIS  %.6f px/mm  [%s]" % (tgt.view['px_per_mm'],
                                                       tgt.view['px_per_mm_basis']))
            # The note is a property of THE VIEW, not a constant. It was hardcoded to
            # photo 6's numbers and printed under every target, so pointing the tool at
            # fcc7-back produced a correct scale with photo 6's provenance written over
            # it - a right number wearing the wrong reason, which is the family
            # docs/TOOLS-THAT-LIE.md is about. Fixed by L9, 2026-09-05.
            n = tgt.view.get('px_per_mm_note')
            if n:
                for line in n.splitlines():
                    print("               " + line)
        return
    tgt.view = dict(tgt.view)
    tgt.view['px_per_mm'] = a.target_px_per_mm
    tgt.view['px_per_mm_basis'] = (a.target_px_per_mm_basis
                                   or 'CALLER OVERRIDE (basis not stated)')
    print("  SCALE BASIS  %.6f px/mm  [%s]" % (tgt.view['px_per_mm'],
                                               tgt.view['px_per_mm_basis']))


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
    apply_scale_override(tgt, a)
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

    if tgt.view['px_per_mm']:
        ppm_src, jac = transfer_scale(H, src, tgt, tgt.view['px_per_mm'])
        # H maps target -> source, so source px per mm = (source px/target px) x (target px/mm)
        print("  TRANSFERRED SCALE  %s: %.3f px/mm  (spread over the board %.3f-%.3f, "
              "sd %.3f = %.2f%%)" % (src.view['name'], ppm_src.mean(), ppm_src.min(),
                                     ppm_src.max(), ppm_src.std(),
                                     100*ppm_src.std()/ppm_src.mean()))
        print("                     A tilted view has no ONE scale. The spread is the "
              "statement of that, not noise.")
        out['transferred_scale'] = dict(
            source_px_per_mm_mean=float(ppm_src.mean()),
            source_px_per_mm_min=float(ppm_src.min()),
            source_px_per_mm_max=float(ppm_src.max()),
            source_px_per_mm_sd=float(ppm_src.std()),
            spread_pct=float(100*ppm_src.std()/ppm_src.mean()),
            n_samples=int(ppm_src.size),
            inherits="every error in the target's px/mm basis, which is: "
                     + (tgt.view.get('px_per_mm_basis') or 'UNSTATED - no basis on this view'))

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

    # Each landmark's TRUE source correspondence.  The warped image is
    # warped[y,x] = source[H(x,y)], and the local search found that the TARGET
    # patch at (tx,ty) matches the WARPED patch at (tx+dx, ty+dy).  So the pair
    # is  target(tx,ty)  <->  source at H(tx+dx, ty+dy).
    #
    # DEFECT WATCHED ON PURPOSE, 2026-09-05.  The first version of this put the
    # shift on the TARGET side and evaluated H at the unshifted grid node, which
    # made Q = H(grid) exactly - points generated BY the homography being tested.
    # The hold-out then returned 0.0151 mm, BETTER than the in-sample landmark
    # residual of 1.047 px (0.066 mm), which is impossible.  That impossibility
    # is the only thing that caught it.  A hold-out fitted to its own model's
    # output is a check that can agree with what it checks.
    P = np.array([[l['tx'], l['ty']] for l in lm])                       # target px
    Q = np.array([apply_H(H, l['tx']+l['dx'], l['ty']+l['dy']) for l in lm])   # source px (ds frame)
    th = np.array([l['theta_deg'] for l in lm])

    ppm = tgt.view['px_per_mm']
    folds = []
    K = a.folds
    split = getattr(a, 'split', 'angular')
    # RADIAL is the HARSHER split and it exists because the angular one is soft:
    # with K=4, three quarters of the board still surround every held-out sector,
    # so the fit interpolates rather than extrapolates.  A radial split holds out
    # a whole annulus, which the remaining landmarks can only reach by
    # extrapolating outward or inward.  K=2 angular (halves) is harsher still.
    rad = np.array([l['r'] for l in lm])
    edges = np.percentile(rad, np.linspace(0, 100, K+1)) if split == 'radial' else None
    for i in range(K):
        if split == 'radial':
            a0, a1 = float(edges[i]), float(edges[i+1])
            held = (rad >= a0) & (rad <= a1) if i == K-1 else (rad >= a0) & (rad < a1)
        else:
            off = float(getattr(a, 'split_offset', 0.0) or 0.0)
            a0, a1 = 360.0*i/K + off, 360.0*(i+1)/K + off
            tha = (th - off) % 360.0
            held = (tha >= 360.0*i/K) & (tha < 360.0*(i+1)/K)
        fit = ~held
        if held.sum() < 4 or fit.sum() < 12:
            folds.append(dict(sector=[a0, a1], n_held=int(held.sum()),
                              verdict='CANNOT DETERMINE', why='too few landmarks in fold'))
            continue
        fitmodel = getattr(a, 'fit_model', 'homography')
        Hf = fit_poly2(P[fit], Q[fit]) if fitmodel == 'poly2' else fit_homography_dlt(P[fit], Q[fit])
        if Hf is None:
            folds.append(dict(sector=[a0, a1], n_held=int(held.sum()),
                              verdict='CANNOT DETERMINE',
                              why='too few landmarks to fit %s' % fitmodel))
            continue
        px, py = apply_model(Hf, P[held][:, 0], P[held][:, 1])
        err_ds = np.hypot(px-Q[held][:, 0], py-Q[held][:, 1])   # downsampled-source px
        # ds-source px per target px, so the error can be quoted in the frame the
        # ruler actually lives in, and only then converted to millimetres.
        Hlin = fit_homography_dlt(P[fit], Q[fit])
        s_ds = math.sqrt(abs(np.linalg.det(Hlin[:2, :2])))
        err_tgt = err_ds/s_ds if s_ds > 0 else np.full_like(err_ds, np.nan)
        # PER-LANDMARK held-out residuals.  The RMS alone cannot tell a transform
        # that is uniformly a little wrong from one that is right everywhere except
        # over a handful of features - and those two have completely different
        # meanings when the two photographs are of two DIFFERENT physical boards.
        # A localised cluster of large residuals is what a real layout difference
        # would look like; a broad elevation is what a bad fit looks like.
        idx = np.nonzero(held)[0]
        per = [dict(theta_deg=float(th[i]), r=float(rad[i]),
                    target_px=[float(P[i, 0] + tgt.ox), float(P[i, 1] + tgt.oy)],
                    err_mm=float(e/s_ds/ppm) if (ppm and s_ds > 0) else None)
               for i, e in zip(idx, err_ds)] if len(idx) else []
        per.sort(key=lambda z: -(z['err_mm'] or 0))
        folds.append(dict(sector=[a0, a1], n_held=int(held.sum()), n_fit=int(fit.sum()),
                          per_landmark_worst=per[:10], per_landmark_all=per,
                          rms_source_px=float(np.sqrt((err_ds**2).mean())*src.k),
                          p95_source_px=float(np.percentile(err_ds, 95)*src.k),
                          rms_target_px=float(np.sqrt((err_tgt**2).mean())),
                          p95_target_px=float(np.percentile(err_tgt, 95)),
                          rms_mm=float(np.sqrt((err_tgt**2).mean())/ppm) if ppm else None,
                          p95_mm=float(np.percentile(err_tgt, 95)/ppm) if ppm else None))
    print("  split=%s  K=%d  fit-model=%s   (angular = sectors in degrees; radial = "
          "annuli in target px)" % (split, K, getattr(a, 'fit_model', 'homography')))
    print("  %-16s %5s %10s %10s %9s %9s"
          % ('held-out band', 'n', 'RMS src px', 'RMS tgt px', 'RMS mm', 'p95 mm'))
    ok = []
    for f in folds:
        if 'rms_mm' not in f:
            print("  %5.0f-%-9.0f %5d   %s" % (f['sector'][0], f['sector'][1], f['n_held'], f.get('why', '')))
            continue
        ok.append(f)
        print("  %5.0f-%-9.0f %5d %10.2f %10.3f %9.4f %9.4f"
              % (f['sector'][0], f['sector'][1], f['n_held'],
                 f['rms_source_px'], f['rms_target_px'], f['rms_mm'], f['p95_mm']))
    coh = residual_coherence(P, Q)
    if coh:
        print("  RESIDUAL COHERENCE  I = %+.4f   null %.4f +- %.4f over %d permutations"
              "   z = %+.1f" % (coh['I'], coh['null_mean'], coh['null_sd'],
                                coh['trials'], coh['z']))
        if coh['detection_limit_frac'] is None:
            print("                      DETECTION LIMIT: none - this set cannot see a "
                  "smooth warp even at the full residual RMS (%.2f px)." % coh['residual_rms_px'])
        else:
            print("                      DETECTION LIMIT: %.0f%% of the residual RMS = "
                  "%.2f px. A smooth field smaller than that is INVISIBLE here."
                  % (100*coh['detection_limit_frac'], coh['detection_limit_px']))
        if coh['z'] > 3.0:
            print("                      SPATIALLY COHERENT: neighbouring landmarks miss "
                  "TOGETHER, so the misfit is a smooth field, not independent per-part "
                  "scatter. It does NOT say which smooth cause.")
        else:
            print("                      CANNOT DETERMINE. A coherent field is BOUNDED "
                  "below %s, not excluded. Reading a low score as 'ruled out' is the "
                  "error R09 published and R11 corrected."
                  % ('the full residual RMS' if coh['detection_limit_px'] is None
                     else '%.2f px' % coh['detection_limit_px']))

    rs = radial_structure(lm, tgt)
    if rs:
        print("  RADIAL STRUCTURE  is the coherent field radial, and about WHAT centre?")
        print("    %-22s %9s %8s %10s %10s" % ('centre', 'corr(r)', 'z', 'radial px', 'tang px'))
        for nm, v in rs.items():
            lim = ('%.3f px' % v['detection_limit_px']
                   if v['detection_limit_px'] is not None else 'NONE')
            print("    %-22s %+9.3f %+8.1f %10.3f %10.3f   detects a dome >= %s"
                  % (nm, v['radial_vs_radius_corr'], v['z'],
                     v['radial_rms_px'], v['tangential_rms_px'], lim))
        best = max(rs.items(), key=lambda kv: abs(kv[1]['z']))
        if abs(best[1]['z']) > 3.0:
            print("    -> the radial component about the %s grows with radius (z=%+.1f). "
                  "A BOARD\n       that is not flat predicts this about the BOARD centre; "
                  "optics predict it\n       about the IMAGE centre; a difference between "
                  "two boards predicts neither."
                  % (best[0], best[1]['z']))
        else:
            lims = [v['detection_limit_px'] for v in rs.values()
                    if v['detection_limit_px'] is not None]
            print("    -> no centre shows a radial component growing with radius above its "
                  "own null.")
            if lims:
                print("       A dome of %.3f px or more WOULD have been seen, so one is "
                      "BOUNDED\n       below that, not excluded." % min(lims))
            else:
                print("       And no injected dome was detectable either, so this is "
                      "absence of POWER,\n       not absence of a dome.")
            print("       Either way it cannot exclude a UNIFORM radial term, which the "
                  "homography\n       absorbs before these residuals are formed.")

    verdict = PASS; why = []
    if not ok:
        verdict = CANNOT; why.append('no fold had enough landmarks')
        worst = None
    else:
        worst = max(f['rms_mm'] for f in ok)
        worst_p95 = max(f['p95_mm'] for f in ok)
        print("  WORST held-out fold: RMS %.4f mm, p95 %.4f mm  (tolerance %.4f mm on RMS)"
              % (worst, worst_p95, a.tol_mm))
        print("  A SINGLE component inherits the p95, not the RMS. Quote the RMS for the "
              "transform and the p95 for any one position.")
        if worst > a.tol_mm:
            verdict = FAIL
            why.append("worst held-out RMS %.4f mm exceeds tolerance %.4f mm" % (worst, a.tol_mm))
    out = dict(tool='c_register.py', verb='validate',
               side_convention="FRONT = component side (Apple FCC 'MLB - Front')",
               source=src.view['path'], target=tgt.view['path'],
               scale_basis=tgt.view['px_per_mm_basis'], px_per_mm=ppm,
               model=a.model, fit_model=getattr(a, 'fit_model', 'homography'),
               ncc=stages[-1]['ncc'], split=split, folds_k=K,
               split_offset_deg=float(getattr(a, 'split_offset', 0.0) or 0.0), folds=folds,
               worst_holdout_rms_mm=worst,
               worst_holdout_p95_mm=(max(f['p95_mm'] for f in ok) if ok else None),
               tolerance_mm=a.tol_mm,
               residual_coherence=coh, radial_structure=rs,
               landmarks_kept=len(lm), landmarks_discarded=disc,
               verdict=V[verdict], why=why)
    if a.json_out:
        with open(a.json_out, 'w') as fh: json.dump(out, fh, indent=1)
        print("  wrote %s" % a.json_out)
    print("  %s%s" % (V[verdict], (': ' + '; '.join(why)) if why else ''))
    return verdict


# ------------------------------------------------------------------ selftest
def _synth(tmp):
    """A synthetic source/target pair with a KNOWN homography, so the recovered
    one can be graded against an answer rather than against itself."""
    rng = np.random.default_rng(7)
    n = 900
    a = np.full((n, n), 40.0)
    Y, X = np.mgrid[0:n, 0:n].astype(np.float64)
    rr = np.hypot(X-n/2, Y-n/2)
    a[(rr < 400) & (rr > 170)] = 90.0
    for _ in range(260):                       # bright "pads" - the texture to lock onto
        t = rng.uniform(0, 2*math.pi); r = rng.uniform(200, 375)
        cx, cy = n/2+r*math.cos(t), n/2+r*math.sin(t)
        w, h = rng.uniform(8, 26), rng.uniform(8, 26)
        a[int(cy-h/2):int(cy+h/2), int(cx-w/2):int(cx+w/2)] = rng.uniform(150, 235)
    a += rng.normal(0, 2.0, a.shape)
    sp = os.path.join(tmp, 'synth_source.png')
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(sp)
    return sp, n

def _synth_target(sp, tmp, theta, scale, tx, ty, name='synth_target.png'):
    im = np.asarray(Image.open(sp).convert('L'), dtype=np.float64)
    n = im.shape[0]; m = int(n*scale)
    Y, X = np.mgrid[0:m, 0:m].astype(np.float64)
    th = math.radians(theta); ct, st = math.cos(th), math.sin(th)
    dx = X - m/2 - tx; dy = Y - m/2 - ty
    sx = (ct*dx + st*dy)/scale + n/2
    sy = (-st*dx + ct*dy)/scale + n/2
    v = ndimage.map_coordinates(im, [sy, sx], order=1, mode='constant', cval=40.0)
    p = os.path.join(tmp, name)
    Image.fromarray(np.clip(v, 0, 255).astype(np.uint8)).save(p)
    return p, m

def _view(path, centre, r, face='synthetic'):
    return dict(path=path, abspath=path, name=os.path.basename(path), centre=centre, r=r,
                face=face, note='selftest synthetic', px_per_mm=10.0,
                px_per_mm_basis='synthetic: 10 px/mm by construction')

def run_selftest(a):
    print("c_register selftest - synthetic ground truth and deliberate breaks")
    tmp = tempfile.mkdtemp(prefix='c_register-selftest-')
    results = []
    def rec(ok, msg):
        results.append(ok); print("  %s  %s" % ('PASS' if ok else 'FAIL', msg))

    sp, n = _synth(tmp)
    TH, SC = 37.0, 0.42
    tp, m = _synth_target(sp, tmp, TH, SC, 0.0, 0.0)
    src = Frame(_view(sp, (n/2, n/2), 400.0), downsample=1/SC if SC < 1 else 1.0)
    # pre-average the source to the target's sampling, as the real pipeline does
    src = Frame(_view(sp, (n/2, n/2), 400.0), downsample=round(1/SC, 2))
    tgt = Frame(_view(tp, (m/2, m/2), 400.0*SC))
    H, stages, coarse, mask = register(src, tgt, model='similarity')
    # 1: recover a known transform
    x0, y0 = apply_H(H, tgt.cx, tgt.cy)
    cerr = math.hypot(x0-src.cx, y0-src.cy)*src.k
    rec(stages[-1]['ncc'] > 0.9 and cerr < 4.0,
        "recover a KNOWN transform (theta=%.0f scale=%.2f): NCC %.4f, centre error %.2f source px"
        % (TH, SC, stages[-1]['ncc'], cerr))
    # 2: null control must sit far below the true fit
    nul = null_distribution(H, src, tgt, mask)
    nm = max(v for _, v in nul)
    rec(stages[-1]['ncc'] > 3.0*nm,
        "NULL control separates: fit %.4f vs worst wrong-rotation %.4f (%.1fx)"
        % (stages[-1]['ncc'], nm, stages[-1]['ncc']/max(nm, 1e-9)))
    # 3: pure noise as target -> no registration
    rng = np.random.default_rng(3)
    npth = os.path.join(tmp, 'noise.png')
    Image.fromarray(rng.integers(0, 255, (m, m)).astype(np.uint8)).save(npth)
    ntgt = Frame(_view(npth, (m/2, m/2), 400.0*SC))
    _, nst, _, _ = register(src, ntgt, model='similarity')
    rec(nst[-1]['ncc'] < 0.30,
        "NOISE target yields no registration: best NCC %.4f (floor for a claim is %.2f)"
        % (nst[-1]['ncc'], 0.30))
    # 4: landmark gate DISCARDS a featureless patch
    flat = os.path.join(tmp, 'flat.png')
    Image.fromarray(np.full((m, m), 128, dtype=np.uint8)).save(flat)
    ftgt = Frame(_view(flat, (m/2, m/2), 400.0*SC))
    lm, disc, _ = landmark_field(H, src, ftgt, step=20, patch=15, search=5)
    rec(len(lm) == 0 and sum(disc.values()) > 0,
        "landmark gate DISCARDS a featureless target: 0 kept, %d discarded %s"
        % (sum(disc.values()), dict(disc)))
    # 5: the hold-out MUST GO RED on a deliberately wrong transform
    lm2, _, _ = landmark_field(H, src, tgt, step=16, patch=15, search=5)
    if len(lm2) >= 30:
        P = np.array([[l['tx'], l['ty']] for l in lm2])
        Q = np.array([apply_H(H, l['tx']+l['dx'], l['ty']+l['dy']) for l in lm2])
        th = np.array([l['theta_deg'] for l in lm2])
        def worst_rms(Pp, Qq, fitter=None, K=4):
            fitter = fitter or fit_homography_dlt
            w = 0.0
            for i in range(K):
                a0, a1 = 360.0/K*i, 360.0/K*(i+1)
                held = (th >= a0) & (th < a1); fit = ~held
                if held.sum() < 4 or fit.sum() < 14: continue
                Hf = fitter(Pp[fit], Qq[fit])
                if Hf is None: continue
                px, py = apply_model(Hf, Pp[held][:, 0], Pp[held][:, 1])
                w = max(w, float(np.sqrt(((px-Qq[held][:, 0])**2+(py-Qq[held][:, 1])**2).mean())))
            return w
        clean = worst_rms(P, Q)
        # DELIBERATE BREAK.  The first attempt here injected a uniform 3% scale
        # and the hold-out did NOT go red - correctly, because a uniform scale IS
        # a homography and the fit absorbs it exactly.  The test was wrong, not
        # the hold-out, and it was fixed rather than loosened.  The break has to
        # be something a homography CANNOT represent: a radial (barrel) warp.
        c = Q.mean(axis=0); d = Q - c
        R = np.hypot(d[:, 0], d[:, 1]).max()
        Qb = c + d*(1.0 + 0.03*(np.hypot(d[:, 0], d[:, 1])/R)**2)[:, None]
        moved = float(np.hypot(*(Qb-Q).T).max())
        bad = worst_rms(P, Qb)
        rec(bad > 3.0*clean and bad > 0.5,
            "HOLD-OUT goes RED on a radial warp a homography CANNOT absorb "
            "(max point move %.2f px): clean %.3f px -> broken %.3f px"
            % (moved, clean, bad))
        # 6 & 7: the COHERENCE statistic, both directions.  A statistic that only
        # ever goes up is a decoration; these two say it moves for the right reason.
        rngc = np.random.default_rng(19)
        Qi = Q + rngc.normal(0, 1.2, Q.shape)          # independent per-landmark scatter
        ci = residual_coherence(P, Qi)
        rec(ci is not None and abs(ci['z']) < 3.0,
            "COHERENCE stays at its null for INDEPENDENT per-landmark scatter: "
            "I=%+.4f null %.4f+-%.4f z=%+.1f" % (ci['I'], ci['null_mean'],
                                                 ci['null_sd'], ci['z']))
        cc = Q.mean(axis=0); dd = Q - cc
        Rn2 = np.hypot(dd[:, 0], dd[:, 1]).max()
        Qs = cc + dd*(1.0 + 0.05*(np.hypot(dd[:, 0], dd[:, 1])/Rn2)**2)[:, None]
        cs = residual_coherence(P, Qs)
        rec(cs is not None and cs['z'] > 3.0,
            "COHERENCE RISES for a genuinely SMOOTH warp: I=%+.4f null %.4f+-%.4f "
            "z=%+.1f" % (cs['I'], cs['null_mean'], cs['null_sd'], cs['z']))
        # 8: THE POWER PROBE, which is the control whose absence produced a wrong
        # published conclusion (R09: "a smooth cause is RULED OUT", from z=+1.4 on
        # 58 landmarks; the same face reads z=+8.5 on 192). A thin landmark set
        # must be REPORTED as unable to see, not read as having seen nothing.
        thin = np.arange(0, len(P), max(1, len(P)//14))
        ct = residual_coherence(P[thin], Qi[thin])
        cf = residual_coherence(P, Qi)
        lt = ct['detection_limit_frac'] if ct else None
        lf = cf['detection_limit_frac'] if cf else None
        rec(cf is not None and lf is not None and (lt is None or lt > lf),
            "DETECTION LIMIT is WORSE for a THIN set than a full one: n=%d limit %s "
            "vs n=%d limit %s (fraction of residual RMS; None = cannot see even at 1.0)"
            % (len(thin), lt, cf['n'], lf))
        # The limit must TIGHTEN when the data get quieter, in the unit that
        # matters (pixels). A "bound" that ignores the noise it is bounding
        # against would be a decoration. An earlier version of this case asserted
        # `limit <= 0.5 x RMS` and went red on a set whose limit is legitimately
        # 1.0 - an arbitrary threshold, not a property; replaced with this.
        Qq = Q + (Qi - Q)*0.4                      # same field, 40% of the noise
        cq = residual_coherence(P, Qq)
        rec(cq is not None and cq['detection_limit_px'] is not None
            and cf['detection_limit_px'] is not None
            and cq['detection_limit_px'] < cf['detection_limit_px'],
            "DETECTION LIMIT TIGHTENS as the data get quieter: %.2f px at 40%% noise "
            "vs %.2f px at full noise" % (cq['detection_limit_px'], cf['detection_limit_px']))
    # THE RIDGE CORRECTION, both directions. This is a proposal to CHANGE the
    # transform every published position depends on, so the bar is that it must
    # lose when there is nothing to win and win when there is - both measured
    # through the same nested procedure used on the real board.
    if len(lm2) >= 40:
        Pr = np.array([[l['tx'], l['ty']] for l in lm2])
        Qr = np.array([apply_H(H, l['tx']+l['dx'], l['ty']+l['dy']) for l in lm2])
        thr_ = np.array([l['theta_deg'] for l in lm2])
        # (a) NOTHING TO WIN: correspondences generated BY a homography.
        rowsA = ridge_vs_homography(Pr, Qr, thr_, K=2)
        gA = max([r['gain_pct'] for r in rowsA] or [0.0])
        rec(rowsA and gA < 20.0,
            "RIDGE does NOT win on data a homography already explains: best held-out "
            "gain %+.1f%% over %d fold(s), lam chosen %s"
            % (gA, len(rowsA), [r['lam_chosen'] for r in rowsA]))
        # (b) SOMETHING TO WIN: a smooth radial warp a homography cannot absorb.
        cW = Qr.mean(axis=0); dW = Qr - cW
        RnW = max(np.hypot(dW[:, 0], dW[:, 1]).max(), 1e-9)
        Qw2 = cW + dW*(1.0 + 0.05*(np.hypot(dW[:, 0], dW[:, 1])/RnW)**2)[:, None]
        rowsB = ridge_vs_homography(Pr, Qw2, thr_, K=2)
        gB = max([r['gain_pct'] for r in rowsB] or [0.0])
        rec(rowsB and gB > 20.0,
            "RIDGE DOES win when a real smooth warp is present: best held-out gain "
            "%+.1f%% (homography %.3f px -> ridge %.3f px), lam chosen %s"
            % (gB, rowsB[0]['homography_rms'], rowsB[0]['ridge_rms'],
               [r['lam_chosen'] for r in rowsB]))

    # RADIAL STRUCTURE, both directions, on a stub frame. A statistic that names a
    # centre must be shown to name the RIGHT one, and to name none when there is none.
    class _T:
        pass
    st = _T(); st.cx, st.cy = 300.0, 300.0
    st.img = np.zeros((600, 600)); st.full_size = (600, 600); st.ox = st.oy = 0.0
    rr = np.random.default_rng(21)
    pts = rr.uniform(60, 540, size=(200, 2))
    d0 = pts - np.array([st.cx, st.cy])
    rad = np.hypot(d0[:, 0], d0[:, 1])
    u0 = d0/np.maximum(rad, 1e-9)[:, None]
    # a DOME about the board centre: radial displacement growing with radius
    Ddome = u0*(0.004*rad)[:, None] + rr.normal(0, 0.15, (200, 2))
    lm_d = [dict(tx=float(p[0]), ty=float(p[1]), dx=float(v[0]), dy=float(v[1]),
                 r=0.0, theta_deg=0.0) for p, v in zip(pts, Ddome)]
    rd = radial_structure(lm_d, st, trials=200)
    zb = rd['board centre']['z']
    rec(rd is not None and zb > 5.0,
        "RADIAL STRUCTURE finds a synthetic DOME about the board centre: corr %+.3f, "
        "z=%+.1f, radial %.3f px vs tangential %.3f px"
        % (rd['board centre']['radial_vs_radius_corr'], zb,
           rd['board centre']['radial_rms_px'], rd['board centre']['tangential_rms_px']))
    Drand = rr.normal(0, 0.6, (200, 2))
    lm_r = [dict(tx=float(p[0]), ty=float(p[1]), dx=float(v[0]), dy=float(v[1]),
                 r=0.0, theta_deg=0.0) for p, v in zip(pts, Drand)]
    rr2 = radial_structure(lm_r, st, trials=200)
    rec(rr2 is not None and abs(rr2['board centre']['z']) < 3.0,
        "RADIAL STRUCTURE stays at its null for a field with NO radial structure: "
        "z=%+.1f" % rr2['board centre']['z'])
    lim = rr2['board centre']['detection_limit_px']
    rec(lim is not None and lim < rr2['board centre']['residual_rms_px'],
        "and that null carries a DETECTION LIMIT rather than a bare 'no': a dome of "
        "%.3f px WOULD have been seen against a residual RMS of %.3f px"
        % (lim or -1, rr2['board centre']['residual_rms_px']))

    ok = sum(1 for r in results if r)
    print("\n%d/%d passed, %d failed" % (ok, len(results), len(results)-ok))
    print("synthetic inputs kept at %s" % tmp)
    return PASS if ok == len(results) else FAIL


def run_doctor(a):
    print("c_register doctor")
    good = True
    for mod, ver in (('numpy', np.__version__),
                     ('PIL', Image.__version__ if hasattr(Image, '__version__') else '?'),
                     ('scipy', __import__('scipy').__version__)):
        print("  PASS  %s %s" % (mod, ver))
    print("  image catalogue: %s" % IMGDIR)
    for k, v in VIEWS.items():
        p = os.path.join(IMGDIR, v['path'])
        e = os.path.exists(p)
        good &= e
        print("  %s  view %-14s %-42s face=%s" % ('PASS' if e else 'FAIL', k, v['path'], v['face']))
    cal = os.path.join(os.path.dirname(HERE), 'metrology', 'ruler-calibration.json')
    if os.path.exists(cal):
        d = json.load(open(cal))['photo6_bottom']
        agree = abs(d['px_per_mm'] - VIEWS['fcc6-front']['px_per_mm']) < 1e-9
        good &= agree
        print("  %s  scale basis matches metrology/ruler-calibration.json photo6_bottom "
              "(%.6f px/mm)" % ('PASS' if agree else 'FAIL', d['px_per_mm']))
    else:
        good = False; print("  FAIL  metrology/ruler-calibration.json missing")
    # CANARY: a real registration with a known answer, not a ping
    tmp = tempfile.mkdtemp(prefix='c_register-doctor-')
    sp, n = _synth(tmp)
    tp, m = _synth_target(sp, tmp, -63.0, 0.35, 0, 0)
    src = Frame(_view(sp, (n/2, n/2), 400.0), downsample=round(1/0.35, 2))
    tgt = Frame(_view(tp, (m/2, m/2), 400.0*0.35))
    H, stages, _, _ = register(src, tgt, model='similarity')
    x0, y0 = apply_H(H, tgt.cx, tgt.cy)
    cerr = math.hypot(x0-src.cx, y0-src.cy)*src.k
    ok = stages[-1]['ncc'] > 0.9 and cerr < 4.0
    good &= ok
    print("  CANARY  known transform theta=-63 scale=0.35: NCC %.4f, centre error %.2f px "
          "(expect NCC>0.9, err<4)" % (stages[-1]['ncc'], cerr))
    print("  %s  canary - a doctor pass is a MEASUREMENT, not a ping" % ('PASS' if ok else 'FAIL'))
    return PASS if good else FAIL


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='verb', required=True)
    def common(p):
        p.add_argument('--source', default='oflynn-front')
        p.add_argument('--target', default='fcc6-front')
        p.add_argument('--model', default='homography', choices=['similarity', 'affine', 'homography'])
        p.add_argument('--downsample', type=float, default=None)
        p.add_argument('--step', type=int, default=14)
        p.add_argument('--patch', type=int, default=15)
        p.add_argument('--search', type=int, default=5)
        p.add_argument('--min-landmarks', type=int, default=40)
        p.add_argument('--target-px-per-mm', type=float, default=None,
                       help='override the target view\'s px/mm. THE BUILT-IN DEFAULT IS THE '
                            'BOTTOM RULE\'S OWN VALUE (15.8875), measured AT THE RULE, near '
                            'the frame edge. metrology/M02 measures 15.6850 AT THE BOARD by '
                            'two independent routes -- 1.29%% lower. Every millimetre derived '
                            'through the default is therefore 1.29%% too small, which is 3x '
                            'the held-out error this tool validates to.')
        p.add_argument('--target-px-per-mm-basis', default=None)
        p.add_argument('--json-out', default=None)
    p = sub.add_parser('fit'); common(p)
    p.add_argument('--min-ncc', type=float, default=0.35)
    p.add_argument('--min-margin', type=float, default=2.5,
                   help='fit must beat its worst wrong-rotation null by this factor')
    q = sub.add_parser('validate'); common(q)
    q.add_argument('--folds', type=int, default=4)
    q.add_argument('--fit-model', default='homography', choices=['homography', 'poly2'],
                   help='model fitted to the LANDMARK CORRESPONDENCES in each fold. '
                        'poly2 adds 4 parameters. It is judged ONLY by the HELD-OUT '
                        'error - in-sample error always falls when parameters are added. '
                        'It FAILED its own positive control at 58 landmarks (see '
                        'fit_poly2); whether it pays at 274 is a question for the '
                        'hold-out, not for a preference.')
    q.add_argument('--split-offset', type=float, default=0.0,
                   help='rotate the angular fold boundaries by this many degrees. '
                        'A failure that FOLLOWS a fixed region of the board is a '
                        'property of that region; one that moves with the boundaries '
                        'is a property of the split.')
    q.add_argument('--split', default='angular', choices=['angular', 'radial'],
                   help='angular = hold out a sector; radial = hold out an annulus, '
                        'which forces EXTRAPOLATION rather than interpolation and is '
                        'the harsher test')
    q.add_argument('--tol-mm', type=float, default=0.20)
    sub.add_parser('doctor')
    sub.add_parser('selftest')
    a = ap.parse_args()
    return {'fit': run_fit, 'validate': run_validate,
            'doctor': run_doctor, 'selftest': run_selftest}[a.verb](a)

if __name__ == '__main__':
    sys.exit(main())
