#!/usr/bin/env python3
"""r_circ.py -- ROUND features by CIRCULAR BOUNDARY EVIDENCE.

L10 BLIND RIM COUNT lane, halo Replica.
SIDE NAMING: the side carrying the SoC and the shield can. O'Flynn's
`oflynn-backside-fullres.jpeg` IS that side.

BLIND-SAFE.  This file states no count, cites no count, carries no feature
positions and loads no seeds.  It was written before its author had looked at the
rim of the photograph.  Keep it that way.

WHY IT EXISTS.  `d_rect` integrates a directional derivative along a STRAIGHT
span: a real straight edge sums coherently (~L), texture sums incoherently
(~sqrt L).  A circle's tangent is straight only over a short arc, so a round
solder joint is not a thing that engine can score -- it cleared 2 of 20
boundaries, and that is a statement about the instrument.

THE STATISTIC.  For a centre (cx,cy) and a radius r, sample the OUTWARD RADIAL
derivative around the ring:

    D(phi) = Gx(cx + r cos phi, cy + r sin phi) * cos phi
           + Gy(cx + r cos phi, cy + r sin phi) * sin phi

  * a round feature brighter than its ground has D < 0 at EVERY phi.  The ring
    integral sums coherently.
  * A STRAIGHT EDGE has gradient g in one fixed direction n, so
    D(phi) = |g| cos(phi - phi_n), and its integral around a FULL circle is
    IDENTICALLY ZERO.  The instrument is blind to a straight edge BY
    CONSTRUCTION, not by a threshold anyone chose.  That is the whole reason to
    build this rather than re-tune the rectangle engine.

CLOSURE, the part texture cannot fake, is the round analogue of `d_rect`'s
min-of-four-sides: the ring is cut into 8 OCTANTS, each octant integral is
normalised, and the feature's score is the MINIMUM octant z OF CONSISTENT
POLARITY.  Three supported octants and five absent is rejected, and an octant
whose gradient points the other way makes the score NEGATIVE.  A straight edge --
whose octants alternate in sign -- is rejected twice over.

THE DENOMINATOR IS GUARDED (E07 sec.25).  A statistic normalised by a spread must
refuse when that spread collapses, not divide by something near zero and report
1e11.  The ring's own robust spread is floored at a level MEASURED over the
search region (`--sd-floor-pct`), the same floor is applied to the nulls, and
whether the floor binds is reported.

AN UNMEASURED THING IS NEVER A MEASURED ZERO (E07 sec.29).  A ring whose samples
are not wholly inside the validity mask returns None and is NAMED unmeasured.  It
never becomes 0.0.

THE BAR IS NOT IN THIS FILE.  It is measured per run, at the size of the thing
being counted, by `null`.

Verbs: selftest  synthetic ground truth + 7 deliberate breaks, each watched red
Exit 0 pass, 1 fail, 2 CANNOT DETERMINE.
"""
import math
import numpy as np
from scipy import ndimage

OCT = 8


# --------------------------------------------------------------- field prep

def grads(L, smooth=1.0):
    """Gx, Gy of a lightly smoothed luma.  Smoothing is a parameter and is swept."""
    S = ndimage.gaussian_filter(L, smooth) if smooth > 0 else L
    Gy, Gx = np.gradient(S)
    return Gx, Gy


# --------------------------------------------------------------- whole-field scan

def ring_field(Gx, Gy, valid, r_px, nphi=64):
    """Per-octant ring sums of the outward radial derivative, for EVERY centre.

    Returns (S[8,H,W], S2[H,W], C[H,W]) -- octant sums, sum of squares, and the
    summed validity weight.  C/nphi is the ring's coverage; anything short of
    full coverage is UNMEASURED, never zero."""
    H, W = Gx.shape
    S = np.zeros((OCT, H, W), np.float32)
    S2 = np.zeros((H, W), np.float32)
    C = np.zeros((H, W), np.float32)
    V = valid.astype(np.float32)
    for i in range(nphi):
        phi = 2.0 * math.pi * (i + 0.5) / nphi
        c, s = math.cos(phi), math.sin(phi)
        P = (Gx * c + Gy * s).astype(np.float32)
        dy, dx = -r_px * s, -r_px * c          # out[cy,cx] = P[cy + r sin, cx + r cos]
        Ps = ndimage.shift(P, (dy, dx), order=1, mode="constant", cval=0.0)
        Vs = ndimage.shift(V, (dy, dx), order=1, mode="constant", cval=0.0)
        S[(i * OCT) // nphi] += Ps
        S2 += Ps * Ps
        C += Vs
    return S, S2, C


def score_field(S, S2, C, nphi, sd_floor):
    """z of the whole ring, and the CLOSURE (min octant z of consistent polarity).

    Unmeasured centres come back as NaN in both, never as 0.0."""
    Stot = S.sum(0)
    mean = Stot / nphi
    var = np.maximum(S2 / nphi - mean * mean, 0.0)
    sd = np.sqrt(var)
    sd_eff = np.maximum(sd, sd_floor)
    z_tot = Stot / (math.sqrt(nphi) * sd_eff)
    nk = nphi / OCT
    sgn = np.where(z_tot < 0, -1.0, 1.0)
    zk = (S * sgn[None]) / (math.sqrt(nk) * sd_eff[None])
    closure = zk.min(0)
    bad = C / nphi < 0.9999
    z_tot = np.where(bad, np.nan, z_tot)
    closure = np.where(bad, np.nan, closure)
    return z_tot, closure, sd, (sd < sd_floor)


# --------------------------------------------------------------- point evaluation

def ring_at(Gx, Gy, valid, cx, cy, r_px, nphi=64, sd_floor=0.0):
    """The same statistic at ONE centre.  Used by the nulls and the ladder, so the
    null and the scan compute the identical number -- E07 sec.22: a null is only a
    null with respect to a particular statistic."""
    i = np.arange(nphi)
    phi = 2.0 * math.pi * (i + 0.5) / nphi
    c, s = np.cos(phi), np.sin(phi)
    yy = cy + r_px * s
    xx = cx + r_px * c
    co = np.stack([yy, xx])
    gx = ndimage.map_coordinates(Gx, co, order=1, mode="constant", cval=0.0)
    gy = ndimage.map_coordinates(Gy, co, order=1, mode="constant", cval=0.0)
    vv = ndimage.map_coordinates(valid.astype(np.float32), co, order=1,
                                 mode="constant", cval=0.0)
    if vv.min() < 0.9999:
        return None                       # UNMEASURED.  Named by the caller.
    D = gx * c + gy * s
    sd = float(D.std())
    sd_eff = max(sd, sd_floor)
    if not np.isfinite(sd_eff) or sd_eff <= 1e-9:
        return None                       # denominator collapsed -- refuse (E07 sec.25)
    z_tot = float(D.sum() / (math.sqrt(nphi) * sd_eff))
    sgn = -1.0 if z_tot < 0 else 1.0
    k = (i * OCT) // nphi
    zk = np.array([D[k == j].sum() * sgn / (math.sqrt(nphi / OCT) * sd_eff)
                   for j in range(OCT)])
    return dict(z_total=z_tot, closure=float(zk.min()), oct_z=zk.tolist(),
                ring_sd=sd, sd_floored=bool(sd < sd_floor),
                polarity="bright" if z_tot < 0 else "dark")


def best_at(Gx, Gy, valid, cx, cy, radii_px, nphi=64, sd_floor=0.0, guard=True):
    """Max closure over the radius grid at one centre -- the SAME multiple-comparison
    burden the whole-field scan carries.  `guard=False` removes the polarity
    consistency guard and exists so the selftest can watch its own guard matter."""
    best = None
    for r in radii_px:
        o = ring_at(Gx, Gy, valid, cx, cy, r, nphi, sd_floor)
        if o is None:
            continue
        cl = o["closure"] if guard else float(np.abs(o["oct_z"]).min())
        if best is None or cl > best[0]:
            best = (cl, r, o)
    if best is None:
        return None
    o = dict(best[2]); o["closure_used"] = best[0]; o["r_px"] = best[1]
    return o


# --------------------------------------------------------------- nulls

def null_dist(Gx, Gy, valid, sample_ys, sample_xs, radii_px, n=1500,
              nphi=64, sd_floor=0.0, seed=20260905):
    """N3 / N1.  The identical scan -- same statistic, same radius grid, same
    max-over-radii -- at random centres drawn from `sample_*`.  No operator choice
    is in it.  Unmeasured draws are COUNTED AND NAMED, not scored 0."""
    rng = np.random.default_rng(seed)
    vals, unmeasured = [], 0
    for _ in range(n):
        k = int(rng.integers(0, len(sample_ys)))
        o = best_at(Gx, Gy, valid, float(sample_xs[k]), float(sample_ys[k]),
                    radii_px, nphi, sd_floor)
        if o is None:
            unmeasured += 1
        else:
            vals.append(o["closure_used"])
    v = np.array(vals) if vals else np.array([np.nan])
    return dict(n=len(vals), unmeasured=unmeasured,
                p50=float(np.percentile(v, 50)), p90=float(np.percentile(v, 90)),
                p99=float(np.percentile(v, 99)), max=float(v.max()))


def phase_scramble(a, seed=20260905):
    """Same power spectrum, random phases.  Every texture statistic survives; no
    coherent round structure does."""
    rng = np.random.default_rng(seed)
    F = np.fft.rfft2(a)
    ph = rng.uniform(-np.pi, np.pi, F.shape)
    ph[0, 0] = 0.0
    o = np.fft.irfft2(np.abs(F) * np.exp(1j * ph), s=a.shape)
    return (o - o.mean()) / (o.std() + 1e-9) * a.std() + a.mean()


# --------------------------------------------------------------- shape gate

def shape_gate(lum, cx, cy, r_px, band=None, min_px=40, sigma=3.0):
    """INDEPENDENT of the locator.  A FILLED SQUARE is also a compact bright blob
    and WILL clear the locator -- that is how five SMD capacitor pads became five
    confident rim detections (E07 sec.30).  So the blob's own boundary contour is
    extracted at half-max and a circle is fitted to it; the discriminator is the
    INLIER FRACTION, which IRLS cannot manufacture (bin/boardmetro sec.1: square
    0.055, ring 1.000).  Returns None when the blob cannot be isolated -- which is
    UNMEASURED and is reported as such."""
    R = int(round(2.6 * r_px))
    y0, y1 = int(max(0, cy - R)), int(min(lum.shape[0], cy + R + 1))
    x0, x1 = int(max(0, cx - R)), int(min(lum.shape[1], cx + R + 1))
    if y1 - y0 < 8 or x1 - x0 < 8:
        return None
    W = lum[y0:y1, x0:x1]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    rr = np.hypot(xx - cx, yy - cy)
    core = rr <= 0.45 * r_px
    ring = (rr >= 1.35 * r_px) & (rr <= 1.95 * r_px)
    if core.sum() < 8 or ring.sum() < 24:
        return None
    hi = float(np.percentile(W[core], 90))
    lo = float(np.median(W[ring]))
    if not np.isfinite(hi) or not np.isfinite(lo) or hi <= lo:
        return None                       # not a bright blob at all -- unmeasured
    thr = 0.5 * (hi + lo)
    B = W > thr
    lab, n = ndimage.label(B)
    ky = int(round(cy)) - y0
    kx = int(round(cx)) - x0
    if not (0 <= ky < lab.shape[0] and 0 <= kx < lab.shape[1]):
        return None
    k = lab[ky, kx]
    if k == 0:
        # the centre is below half-max: try the largest component touching the core
        ks = [v for v in np.unique(lab[core]) if v]
        if not ks:
            return None
        k = max(ks, key=lambda v: (lab == v).sum())
    blob = lab == k
    area = int(blob.sum())
    edge = blob & ~ndimage.binary_erosion(blob)
    ys, xs = np.nonzero(edge)
    if len(ys) < min_px:
        return None
    ys = ys + y0; xs = xs + x0
    bw = band if band else max(2.0, 0.10 * r_px)
    cxf, cyf, rf, keep, res = _fit_circle(xs.astype(float), ys.astype(float), band=bw)
    frac = float(keep.mean()) if len(keep) else 0.0
    d_eq = 2.0 * math.sqrt(area / math.pi)
    peri = float(len(ys))
    circ = 4.0 * math.pi * area / (peri * peri) if peri else 0.0
    prof = radial_profile(lum, cx, cy, r_px, sigma=sigma)
    return dict(inlier_frac=frac, profile=prof, fit_r_px=float(rf), fit_cx=float(cxf),
                fit_cy=float(cyf), resid_sd_px=float(res.std()) if len(res) else float("nan"),
                area_px=area, d_equiv_px=float(d_eq), boundary_px=int(len(ys)),
                iso_circularity=float(circ), half_max_thr=float(thr),
                core_p90=hi, ring_median=lo, band_px=float(bw),
                touches_window=bool(blob[0].any() or blob[-1].any()
                                    or blob[:, 0].any() or blob[:, -1].any()))


def radial_profile(lum, cx, cy, r_px, sigma=3.0, nth=180, nr=140):
    """The half-max radius R(theta) about a candidate centre, and its NON-CIRCULAR
    ENERGY -- the general shape statistic.

    WHY NOT THE INLIER FRACTION ALONE.  bin/boardmetro's published separation
    (square 0.055, ring 1.000) was measured on a THIN SQUARE OUTLINE against a THIN
    RING, where the corners sit far from any circle.  A FILLED square of equal area
    deviates from its own best-fit circle by only +/-17 % of the radius, which at a
    1.4 mm feature is +/-3.5 px -- comparable to any usable IRLS band.  Measured on
    filled features it separates 1.17-1.45x at every band and every smoothing, and
    never reaches the pre-registered 0.85 / 0.30.  THE PUBLISHED SEPARATION DOES NOT
    TRANSFER FROM OUTLINES TO FILLED BLOBS.  That is E07 sec.20 (a threshold is a
    property of a material AND a field of view) arriving on a shape statistic.

    THE REPLACEMENT.  R(theta) is Fourier-decomposed; k=0 is the size and k=1 is a
    centring error, so the shape lives in k>=2:

        noncirc = sqrt( 2 * sum_{k>=2} |F_k|^2 ) / mean(R)

    It is rotation-invariant by construction and covers 2-fold (a rectangular pad),
    3-fold and 4-fold (a square) alike -- unlike the 4-fold amplitude alone, which
    scores a 2:1 rectangle as round (0.023) and would have admitted exactly the SMD
    capacitor pads that fooled an earlier lane.  `a4` is kept as a diagnostic.

    SMOOTHING TO GENUINE RESOLUTION IS NOT A TUNE.  The source carries 20.7-27.4
    genuine px/mm against 106.313 stored, so per-pixel structure at stored
    resolution is JPEG noise and not board detail (E07's resolution table).  sigma
    is a parameter and is swept."""
    Ls = ndimage.gaussian_filter(lum, sigma) if sigma > 0 else lum
    th = np.linspace(0, 2 * np.pi, nth, endpoint=False)
    rs = np.linspace(0.15 * r_px, 2.4 * r_px, nr)
    ys = cy + rs[None, :] * np.sin(th[:, None])
    xs = cx + rs[None, :] * np.cos(th[:, None])
    if (ys.min() < 1 or xs.min() < 1 or ys.max() > lum.shape[0] - 2
            or xs.max() > lum.shape[1] - 2):
        return None                        # the profile leaves the image -- UNMEASURED
    V = ndimage.map_coordinates(Ls, [ys, xs], order=1, mode="nearest")
    hi = float(np.percentile(V[:, :10], 90))
    lo = float(np.median(V[:, -20:]))
    if not np.isfinite(hi) or not np.isfinite(lo) or hi <= lo:
        return None                        # no bright core over its own surround
    thr = 0.5 * (hi + lo)
    below = V < thr
    R = np.where(below.any(1), rs[np.argmax(below, 1)], np.nan)
    n_open = int(np.isnan(R).sum())        # rays that never cross -- NAMED, not filled
    if n_open > nth // 10:
        return None
    R = np.where(np.isnan(R), np.nanmedian(R), R)
    m = float(R.mean())
    F = np.fft.rfft(R) / len(R)
    nc = float(math.sqrt(2.0 * sum(abs(F[k]) ** 2 for k in range(2, len(F)))) / m)
    a4 = float(2 * abs(F[4]) / m)
    return dict(noncirc=nc, a4=a4, R_mean_px=m, R_min_px=float(R.min()),
                R_max_px=float(R.max()), rays_open=n_open, half_max_thr=thr,
                core_p90=hi, surround_median=lo, contrast_luma=hi - lo,
                sigma_px=float(sigma))


def _fit_circle(x, y, iters=30, band=2.0):
    """Kasa + IRLS, the same fit bin/boardmetro uses; kept here so the engine has no
    import-time dependency on a CLI script.  boardmetro `circles` calls INTO this."""
    w = np.ones_like(x)

    def kasa(x, y, w):
        A = np.stack([x, y, np.ones_like(x)], 1) * w[:, None]
        b = (x * x + y * y) * w
        sol, *_ = np.linalg.lstsq(A, b, rcond=None)
        cx, cy = sol[0] / 2, sol[1] / 2
        return cx, cy, math.sqrt(max(sol[2] + cx * cx + cy * cy, 1e-12))

    cx, cy, r = kasa(x, y, w)
    for i in range(iters):
        d = np.abs(np.hypot(x - cx, y - cy) - r)
        bw = max(band, 3.0 * 1.4826 * np.median(d)) if i < 8 else band
        w = (d < bw).astype(float)
        if w.sum() < 12:
            break
        cx, cy, r = kasa(x, y, w)
    keep = w > 0
    res = np.hypot(x[keep] - cx, y[keep] - cy) - r if keep.sum() else np.array([0.0])
    return cx, cy, r, keep, res


# --------------------------------------------------------------- synthetics

def synth(kind, n=360, ppm=35.4, seed=7, contrast=120.0, texture=35.0, size_mm=1.4):
    """Board-like ground with a known feature.  `texture` defaults to 35 luma, the
    photograph's own measured differential robust sd (34.6 / 37.3) -- E07 sec.4:
    a positive control 19x cleaner than the source is not a positive control."""
    rng = np.random.default_rng(seed)
    base = rng.normal(0, texture, (n, n))
    base = ndimage.gaussian_filter(base, 1.2)
    base = base / (base.std() + 1e-9) * texture + 90.0
    yy, xx = np.mgrid[0:n, 0:n]
    c = (n - 1) / 2.0
    s = size_mm * ppm
    if kind == "disc":
        base[np.hypot(xx - c, yy - c) <= s / 2] += contrast
    elif kind == "square":
        a = math.sqrt(math.pi) * s / 2.0        # EQUAL AREA to the disc
        base[(np.abs(xx - c) <= a / 2) & (np.abs(yy - c) <= a / 2)] += contrast
    elif kind == "edge":
        base[yy >= c] += contrast
    elif kind == "flat":
        pass
    elif kind == "bipolar":
        # one disc, brighter than ground on one side and DARKER on the other.  Every
        # octant carries a strong boundary, so |z| is large all the way round and the
        # closure requirement alone accepts it -- only the POLARITY consistency of
        # those octants rejects it.  This is the case the guard exists for; a
        # straight edge is rejected by the ring integral being structurally zero and
        # by closure, and so tests neither guard (E07 sec.27).
        b = np.hypot(xx - c, yy - c) <= s / 2
        base[b & (xx < c)] += contrast
        base[b & (xx >= c)] -= contrast
    elif kind == "octagon":
        a = math.sqrt(math.pi * (s / 2) ** 2 / (2 * (1 + math.sqrt(2)))) * (1 + math.sqrt(2))
        base[(np.abs(xx - c) <= a) & (np.abs(yy - c) <= a)
             & (np.abs(xx - c) + np.abs(yy - c) <= a * math.sqrt(2))] += contrast
    elif kind == "rect21":
        A = math.pi * (s / 2) ** 2
        w = math.sqrt(A * 2.0); h = A / w
        base[(np.abs(xx - c) <= w / 2) & (np.abs(yy - c) <= h / 2)] += contrast
    elif kind == "ring":
        d = np.abs(np.hypot(xx - c, yy - c) - s / 2)
        base[d <= max(1.0, 0.06 * s)] += contrast
    mask = np.ones((n, n), bool)
    return base, mask, dict(cx=c, cy=c, size_mm=size_mm, ppm=ppm, contrast=contrast,
                            texture=texture)


# --------------------------------------------------------------- selftest

def _center(t):
    """(image, cx, cy, r_px) for a synth() result -- the feature is always centred."""
    L, M, meta = t
    return L, (L.shape[1] - 1) / 2.0, (L.shape[0] - 1) / 2.0, meta["size_mm"] * meta["ppm"] / 2


def selftest(verbose=True):
    """Ground truth we generate, and SEVEN DELIBERATE BREAKS, each of which was
    watched go red before the check it protects was trusted.  Every synthetic here
    is NOISE-MATCHED to the photograph (texture 35 luma), because a regression case
    written against an easy synthetic is not a regression case (E07 sec.27)."""
    P, F = [], []

    def check(name, ok, detail=""):
        (P if ok else F).append(name)
        if verbose:
            print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  -- ' + detail) if detail else ''}")

    ppm = 35.4
    radii = [r for r in np.arange(0.50, 1.101, 0.05) * ppm]

    def prep(kind, **kw):
        L, M, t = synth(kind, ppm=ppm, **kw)
        Gx, Gy = grads(L, 1.0)
        return L, M, t, Gx, Gy

    # a floor measured on a FLAT field of the same texture, the same way the real
    # run measures it -- so the selftest and the run share the guard, not just the code
    Lf, Mf, _, Gfx, Gfy = prep("flat")
    ys, xs = np.nonzero(Mf)
    sub = np.random.default_rng(1).integers(0, len(ys), 400)
    sds = [ring_at(Gfx, Gfy, Mf, float(xs[k]), float(ys[k]), radii[6], 64)
           for k in sub]
    sds = [o["ring_sd"] for o in sds if o]
    floor = float(np.percentile(sds, 5)) if sds else 0.0

    # 1 POSITIVE, noise-matched: a disc we drew is found, and beats a flat field
    L, M, t, Gx, Gy = prep("disc", contrast=120.0)
    d = best_at(Gx, Gy, M, t["cx"], t["cy"], radii, 64, floor)
    nul = null_dist(Gfx, Gfy, Mf, ys, xs, radii, n=300, nphi=64, sd_floor=floor)
    check("1 a 1.4 mm DISC at 120 luma in texture-35 ground beats the flat null p99",
          d is not None and d["closure_used"] > nul["p99"],
          f"closure {d['closure_used']:.2f} against flat p99 {nul['p99']:.2f} "
          f"(max {nul['max']:.2f}), polarity {d['polarity']}")
    ref = d["closure_used"] if d else 0.0

    # 2 BREAK: a STRAIGHT EDGE must NOT clear.  The statistic is zero on it by
    #   construction and the polarity guard rejects it a second time.
    Le, Me, te, Gex, Gey = prep("edge", contrast=120.0)
    e = best_at(Gex, Gey, Me, te["cx"], te["cy"], radii, 64, floor)
    check("2 BREAK a straight EDGE at the same contrast does not clear the disc's score",
          e is not None and e["closure_used"] < nul["p99"],
          f"edge closure {e['closure_used']:.2f} vs flat p99 {nul['p99']:.2f}, "
          f"disc {ref:.2f}")

    # 7 GUARD-REMOVAL REGRESSION, and the FIRST VERSION OF THIS CASE WAS WRONG.
    #   Removing the polarity guard on the straight EDGE left it rejected (0.48 vs a
    #   0.64 null p99): the edge is killed by the ring integral being structurally
    #   zero and by CLOSURE, so it tests neither guard.  A regression case must
    #   reproduce the conditions the guard exists for (E07 sec.27).  The case the
    #   POLARITY guard exists for is a BIPOLAR feature -- one boundary, bright on one
    #   side of it and dark on the other.  Every octant is strongly supported, so
    #   closure alone admits it; only polarity consistency rejects it.
    Lb, Mb, tb, Gbx, Gby = prep("bipolar", contrast=120.0)
    b_on = best_at(Gbx, Gby, Mb, tb["cx"], tb["cy"], radii, 64, floor, guard=True)
    b_off = best_at(Gbx, Gby, Mb, tb["cx"], tb["cy"], radii, 64, floor, guard=False)
    check("7 REGRESSION the POLARITY guard is what rejects a BIPOLAR feature "
          "(guard off -> it passes)",
          b_on is not None and b_off is not None
          and b_on["closure_used"] < nul["p99"] < b_off["closure_used"],
          f"guard on {b_on['closure_used']:.2f} (rejected), guard off "
          f"{b_off['closure_used']:.2f} > null p99 {nul['p99']:.2f} (accepted)")

    # 3 BREAK: zero contrast -- nothing to find
    L0, M0, t0, G0x, G0y = prep("disc", contrast=0.0)
    z = best_at(G0x, G0y, M0, t0["cx"], t0["cy"], radii, 64, floor)
    check("3 BREAK a disc at ZERO contrast does not clear the null",
          z is not None and z["closure_used"] < nul["p99"],
          f"closure {z['closure_used']:.2f} against p99 {nul['p99']:.2f}")

    # 4 BREAK: the denominator collapses -- the tool must REFUSE, not return 1e11
    Lc = np.full((240, 240), 100.0)
    Gcx, Gcy = grads(Lc, 1.0)
    r0 = ring_at(Gcx, Gcy, np.ones((240, 240), bool), 120.0, 120.0, radii[6], 64, 0.0)
    check("4 BREAK a zero-variance field REFUSES rather than scoring infinity",
          r0 is None, "returned None (E07 sec.25: guard the denominator)")

    # 5 BREAK: coverage.  A ring reaching outside the validity mask is UNMEASURED
    #   and must be None -- never 0.0 in the same field as a measured score.
    Mm = np.ones((360, 360), bool); Mm[:, :200] = False
    u = ring_at(Gx, Gy, Mm, 180.0, 180.0, radii[-1], 64, floor)
    ok5 = u is None
    S, S2, C, = ring_field(Gx, Gy, Mm, radii[-1], 64)
    zt, cl, sd, fl = score_field(S, S2, C, 64, floor)
    n_nan = int(np.isnan(cl[:, :150]).all())
    check("5 BREAK a ring outside the mask is UNMEASURED (None / NaN), never 0.0",
          ok5 and n_nan == 1,
          "point eval None and the masked half of the field is NaN, not zero")

    # 6 BREAK: an impossible search must say CANNOT DETERMINE, not return an empty
    #   count.  An empty count and an impossible search must not print the same thing.
    Mt = np.zeros((360, 360), bool)
    t6 = best_at(Gx, Gy, Mt, 180.0, 180.0, radii, 64, floor)
    check("6 BREAK an empty validity mask returns None (-> CANNOT DETERMINE), not 0 found",
          t6 is None, "no radius was measurable, so there is no count to report")

    # SHAPE GATE.  Case 8 shows why it is needed; 9-12 are what it can and cannot do.
    Ls, Ms, ts, Gsx, Gsy = prep("square", contrast=120.0)
    ds = best_at(Gsx, Gsy, Ms, ts["cx"], ts["cy"], radii, 64, floor)
    check("8 an EQUAL-AREA SQUARE clears the LOCATOR too -- which is why a shape gate exists",
          ds is not None and ds["closure_used"] > nul["p99"],
          f"square locator closure {ds['closure_used']:.2f} > null p99 {nul['p99']:.2f}; "
          f"the locator alone would have counted it")

    # 9 THE PRE-REGISTERED GATE FAILS, AND THIS CASE RECORDS THE FAILURE.
    #   R00 predicted the INLIER FRACTION would separate disc >=0.85 from equal-area
    #   square <=0.30 at ratio >=2.5.  It does not, at ANY band and ANY smoothing:
    #   a filled square deviates from its own best-fit circle by only +/-17 % of the
    #   radius.  The published 0.055 / 1.000 was measured on OUTLINES.  This check is
    #   written to PASS only while that falsification holds, so if a later change
    #   ever makes the inlier fraction separate, this goes red and the amendment
    #   must be revisited.
    sg_d = shape_gate(L, t["cx"], t["cy"], d["r_px"], band=3.0)
    sg_s = shape_gate(Ls, ts["cx"], ts["cy"], ds["r_px"], band=3.0)
    ratio_if = sg_d["inlier_frac"] / max(sg_s["inlier_frac"], 1e-9)
    check("9 the PRE-REGISTERED inlier-fraction gate is FALSIFIED on filled blobs",
          ratio_if < 2.5 and sg_s["inlier_frac"] > 0.30,
          f"disc {sg_d['inlier_frac']:.3f} vs square {sg_s['inlier_frac']:.3f} = "
          f"{ratio_if:.2f}x, against a predicted >=2.5x with square <=0.30 -- P3 FALSIFIED")

    # 10 the replacement statistic separates disc / square / 2:1 rectangle, and is
    #    rotation-invariant.  The 2:1 rectangle is the SMD capacitor pad class that
    #    fooled an earlier lane, and 4-fold amplitude alone scores it as ROUND.
    Lr, Mr, tr, Grx, Gry = prep("rect21", contrast=120.0)
    dr = best_at(Grx, Gry, Mr, tr["cx"], tr["cy"], radii, 64, floor)
    p_d = radial_profile(L, t["cx"], t["cy"], d["r_px"])
    p_s = radial_profile(Ls, ts["cx"], ts["cy"], ds["r_px"])
    p_r = radial_profile(Lr, tr["cx"], tr["cy"], dr["r_px"] if dr else radii[6])
    check("10 NONCIRC separates disc from square AND from a 2:1 rectangle, ratio >=2",
          p_d and p_s and p_r and p_s["noncirc"] / p_d["noncirc"] >= 2.0
          and p_r["noncirc"] / p_d["noncirc"] >= 2.0,
          f"disc {p_d['noncirc']:.4f}  square {p_s['noncirc']:.4f} "
          f"({p_s['noncirc']/p_d['noncirc']:.2f}x)  rect2:1 {p_r['noncirc']:.4f} "
          f"({p_r['noncirc']/p_d['noncirc']:.2f}x)")
    check("11 BREAK the 4-fold amplitude ALONE scores the 2:1 rectangle as ROUND",
          p_r["a4"] < 2.0 * p_d["a4"] or p_r["a4"] < 0.05,
          f"rect2:1 a4 {p_r['a4']:.4f} against disc a4 {p_d['a4']:.4f} -- which is why "
          f"the gate is total non-circular energy, not a4")

    # 12 THE GATE HAS A MEASURED CONTRAST FLOOR AND MUST DECLARE IT.  Below it the
    #    disc and square distributions overlap and the gate separates NOTHING.  A
    #    gate that is silently useless at low contrast is worse than no gate.
    seps = {}
    for C in (120.0, 90.0, 50.0):
        dd = [radial_profile(*_center(synth("disc", ppm=ppm, contrast=C, seed=k)))
              for k in range(12)]
        qq = [radial_profile(*_center(synth("square", ppm=ppm, contrast=C, seed=k)))
              for k in range(12)]
        dv = [x["noncirc"] for x in dd if x]; qv = [x["noncirc"] for x in qq if x]
        seps[C] = (float(np.percentile(dv, 90)), float(np.percentile(qv, 10)))
    check("12 the shape gate SEPARATES at 120 and 90 luma and OVERLAPS at 50 -- "
          "declared, not hidden",
          seps[120.0][0] < seps[120.0][1] and seps[90.0][0] < seps[90.0][1]
          and seps[50.0][0] >= seps[50.0][1],
          "  ".join(f"{int(C)}: disc_p90 {a:.4f} vs square_p10 {b:.4f} "
                    f"{'SEP' if a < b else 'OVERLAP'}" for C, (a, b) in seps.items()))

    print(f"\n  {len(P)}/{len(P)+len(F)} passed, {len(F)} failed")
    if F:
        print("  FAILED: " + ", ".join(F))
    return 0 if not F else 1


if __name__ == "__main__":
    import sys
    sys.exit(selftest())
