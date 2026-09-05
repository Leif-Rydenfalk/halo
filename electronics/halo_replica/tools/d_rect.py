#!/usr/bin/env python3
"""d_rect.py -- rectangle detection by BOUNDARY EVIDENCE, not by intensity level.

L7 DARK-PACKAGE DETECTOR lane, halo Replica.
SIDE NAMING: the side carrying the SoC and the shield can. O'Flynn's
`oflynn-backside-fullres.jpeg` IS that side.

WHY THIS EXISTS.  Four intensity-based attempts have failed to separate the
neutral-black IC packages from bare soldermask, and the fourth failure was
measured on an INDEPENDENT source with 1.9x more genuine resolution
(metrology/M10-DARK-PACKAGES-SECOND-SOURCE.json):

  1 dark + smooth + rectangular ....... package merges with bare soldermask
  2 black top-hat (local darkness) .... the board connects into one 1.76 Mpx blob
  3 stated ROI + Otsu ................. returns an answer, and the answer is the BOX
                                        (0/20/40/60 px padding -> 3.35/3.98/4.09/4.50 mm)
  4 colour (B-R) ...................... works for BLUE epoxy only; the black
                                        package is B-R=+0.5 against a board +1
  and on the sharper source: package luma 61 and 73 sit INSIDE the bare-soldermask
  range 52-145; package local-sd 9.94 and 4.22 sit INSIDE the soldermask range
  5.17-14.59.  INTENSITY AND TEXTURE ARE RULED OUT BY MEASUREMENT.

WHAT A HUMAN IS ACTUALLY USING is the thing none of those looked at: the package
has STRAIGHT BOUNDARIES meeting at RIGHT ANGLES, and soldermask does not.

THE MEASUREMENT.  For an orientation theta, in the rotated frame:
    Dx = dI/dx   responds to vertical edges,  Dy = dI/dy to horizontal ones.
  A straight edge of length L integrates Dx COHERENTLY along its length: the sum
  grows like L.  Unaligned texture of the same local contrast sums INCOHERENTLY:
  it grows like sqrt(L).  So the discriminator is the ratio of a line integral to
  the null distribution of that same integral -- a z-score against the image's own
  texture, with NO absolute intensity anywhere in it.

THE NULL IS EMPIRICAL, NOT ASSUMED.  sqrt(L) is only true for white noise and
this is a JPEG.  The null is built by ROLLING EACH ROW OF Dx INDEPENDENTLY by a
random amount: identical per-row statistics, identical spatial correlation along
the row, only the alignment BETWEEN rows destroyed.  That is exactly the fix
E07 sec.2 records for L1's rim-pad control, which permuted the wrong thing twice.

CLOSURE IS THE PART SOLDERMASK CANNOT FAKE.  A rectangle scores
    min( |z_left|, |z_right|, |z_top|, |z_bottom| )
  -- the MINIMUM, so three good sides and one absent is rejected -- and the four
  sides must carry a CONSISTENT POLARITY (all four gradients pointing into the
  body, or all four out).  A dark stretch of soldermask has no fourth side and no
  consistent polarity.

WHAT IT STILL SHARES WITH ITS OWN CONTROL, and this is the E07 sec.4 trap: the
nRF52832 is a BLUE package, so its boundary STEP is large.  A control on the nRF
is easy in exactly the dimension that decides the black packages.  `control`
therefore also runs a CONTRAST-MATCHED case: the nRF's boundary step is attenuated
to the black package's measured step and the detector is re-run.  If it still finds
it, the method reaches; if it does not, then "we could not see them" upgrades to
"at this boundary contrast they could not have been seen".

Verbs: selftest  synthetic ground truth + deliberate breaks (run this first)
Exit 0 pass, 1 fail, 2 CANNOT DETERMINE.
"""
import math
import numpy as np
from scipy import ndimage

# ----------------------------------------------------------------- engine

def downsample(a, d):
    """Area-average by an integer factor. Never interpolate up."""
    if d == 1:
        return a.astype(float)
    h, w = a.shape[0] // d * d, a.shape[1] // d * d
    return a[:h, :w].astype(float).reshape(h // d, d, w // d, d).mean(axis=(1, 3))


def _cum0(a, axis):
    """cumsum with a leading zero, so C[j]-C[i] is the sum over rows/cols i..j-1."""
    z = np.zeros((1, a.shape[1])) if axis == 0 else np.zeros((a.shape[0], 1))
    return np.concatenate([z, np.cumsum(a, axis=axis)], axis=axis)


def highpass_grad(D, w, axis):
    """Remove slowly-varying gradient along the scan axis.

    A smooth ILLUMINATION RAMP has a constant non-zero derivative, and a constant
    integrates coherently over any length -- exactly like an edge.  That is where
    a spectrum-matched null gets its power on this photograph, whose interior luma
    runs 90/41/66/36 across a single 3 mm package.  A step is a SPIKE in the
    derivative, so subtracting the local mean derivative over a window much wider
    than an edge and much narrower than a package removes the ramp and keeps the
    step.  The null is rebuilt through the identical filter, so nothing is free."""
    if not w or w < 3:
        return D
    return D - ndimage.uniform_filter1d(D, int(w), axis=axis)


def phase_scramble(a, seed=20260905):
    """Same power spectrum, random phases: every texture statistic of the image
    survives and every straight edge and closed corner does not.  This is the null
    a boundary detector has to beat before anything else is discussed."""
    rng = np.random.default_rng(seed)
    F = np.fft.rfft2(a)
    ph = rng.uniform(-np.pi, np.pi, F.shape)
    ph[0, 0] = 0.0
    out = np.fft.irfft2(np.abs(F) * np.exp(1j * ph), s=a.shape)
    return (out - out.mean()) / (out.std() + 1e-9) * a.std() + a.mean()


def _row_roll_null(D, rng):
    """Per-row independent circular roll.  Same per-row values, same along-row
    correlation, alignment BETWEEN rows destroyed.  E07 sec.2."""
    n, m = D.shape
    sh = rng.integers(0, m, size=n)
    idx = (np.arange(m)[None, :] + sh[:, None]) % m
    return np.take_along_axis(D, idx, axis=1)


def _null_sd_table(D, rng, lens, Mcum=None, sub=3, half=1):
    """Robust sd of the line integral over each span length, measured on the null.

    Mcum is the cumulative of the VALIDITY mask along the same axis.  Without it
    the estimate is taken over spans that lie partly or wholly off the board,
    where the derivative is identically zero -- and once more than half the
    samples are zero the median absolute deviation is ZERO, the z-scores go to
    infinity, and every rectangle scores the same.  That was a real defect in this
    file, found by pointing `score_rect` at a rectangle whose answer was known."""
    N = _row_roll_null(D, rng)
    if half:
        N = ndimage.uniform_filter1d(N, 2 * half + 1, axis=1) * (2 * half + 1)
    C = _cum0(N, 0)
    out = {}
    for L in lens:
        if L >= C.shape[0]:
            out[L] = np.inf
            continue
        S = C[L::sub, :] - C[:-L:sub, :]
        if Mcum is not None:
            ok = (Mcum[L::sub, :] - Mcum[:-L:sub, :]) >= L - 1e-6
            S = S[ok]
        s = S[np.isfinite(S)]
        if s.size < 32:
            out[L] = np.inf
            continue
        # robust: 1.4826 * MAD, so a few real-ish structures cannot inflate it
        out[L] = float(1.4826 * np.median(np.abs(s - np.median(s))) + 1e-9)
    return out


def _sd_of(tab, lens, L):
    """Interpolate the null sd in sqrt(L), which is the white-noise scaling; the
    table itself carries whatever the real correlation does to it."""
    xs = np.sqrt(np.asarray(lens, float))
    ys = np.asarray([tab[l] for l in lens], float)
    return float(np.interp(math.sqrt(L), xs, ys))


def _peaks(prof, k, nms):
    """Top-k local maxima with non-maximum suppression."""
    order = np.argsort(-prof)
    got = []
    for i in order:
        if prof[i] <= 0:
            break
        if all(abs(i - j) >= nms for j in got):
            got.append(int(i))
        if len(got) >= k:
            break
    return sorted(got)


def _pairs(idx, lo, hi):
    """All ordered index pairs whose separation lies in [lo,hi]."""
    a = np.asarray(idx)
    I, J = np.triu_indices(len(a), 1)
    d = a[J] - a[I]
    k = (d >= lo) & (d <= hi)
    return I[k], J[k], d[k]


def _band(C, cols, r0, r1, half=1):
    """Signed line integral over a BAND of 2*half+1 adjacent lines.

    A single column was the first version and it was wrong: the real boundary is
    blurred across 2-4 px at this resolution and drifts by ~1 px along a long side
    at a 2 deg angle step, so one column recovers a fraction of the step and a
    long package edge loses to a short high-contrast pad edge.  Summing the band
    recovers the whole step and tolerates the drift; the NULL is measured through
    exactly the same band, so nothing is gained for free."""
    out = 0.0
    for o in range(-half, half + 1):
        c = np.clip(np.asarray(cols) + o, 0, C.shape[1] - 1)
        out = out + (C[r1][:, c].T - C[r0][:, c].T)
    return out


def detect(lum, mask, ppm, *, angles=None, astep=2.0, smooth=1.0,
           min_mm=0.7, max_mm=9.0, z_thr=6.0, npeak=22, nms=3,
           seed=20260905, band=1, polarity=None):
    """Rectangles supported by four straight, closed, polarity-consistent
    boundaries.  `ppm` is pixels per mm IN THE ARRAY GIVEN.

    z_thr is NOT a number to be believed on its own.  The CLI sets it from a
    NEGATIVE CONTROL run end to end -- the same detector on bare board and on a
    spectrum-matched scramble -- and every other arbitrary value here (astep,
    smooth, npeak, nms, the caller's downsample) is a sweep axis.
    """
    rng = np.random.default_rng(seed)
    H, W = lum.shape
    if angles is None:
        angles = np.arange(0.0, 90.0, astep)
    wmin, wmax = min_mm * ppm, max_mm * ppm
    lens = sorted({max(2, int(round(v))) for v in
                   np.geomspace(max(2.0, wmin * 0.6), wmax * 1.15, 12)})

    ys, xs = np.nonzero(mask)
    if ys.size == 0:
        return []
    cy, cx = (ys.min() + ys.max()) / 2.0, (xs.min() + xs.max()) / 2.0
    rad = int(math.ceil(0.5 * math.hypot(ys.max() - ys.min(), xs.max() - xs.min()))) + 8
    y0, x0 = int(round(cy)) - rad, int(round(cx)) - rad
    pad = ((max(0, -y0), max(0, y0 + 2 * rad - H)), (max(0, -x0), max(0, x0 + 2 * rad - W)))
    Lp = np.pad(lum, pad, mode="edge")
    Mp = np.pad(mask.astype(float), pad, mode="constant")
    y0 += pad[0][0]; x0 += pad[1][0]
    Lc = Lp[y0:y0 + 2 * rad, x0:x0 + 2 * rad]
    Mc = Mp[y0:y0 + 2 * rad, x0:x0 + 2 * rad]
    off = (x0 - pad[1][0], y0 - pad[0][0])

    if smooth > 0:
        Lc = ndimage.gaussian_filter(Lc, smooth)

    out = []
    for th in angles:
        R = ndimage.rotate(Lc, th, reshape=False, order=1, mode="nearest")
        Mr = ndimage.rotate(Mc, th, reshape=False, order=1, mode="constant") > 0.995
        Mr = ndimage.binary_erosion(Mr, np.ones((5, 5)))
        if Mr.sum() < 64:
            continue
        Dx = np.zeros_like(R); Dx[:, 1:-1] = 0.5 * (R[:, 2:] - R[:, :-2])
        Dy = np.zeros_like(R); Dy[1:-1, :] = 0.5 * (R[2:, :] - R[:-2, :])
        Dx = np.where(Mr, Dx, 0.0); Dy = np.where(Mr, Dy, 0.0)

        MV = _cum0(Mr.astype(float), 0)
        MH = _cum0(Mr.astype(float), 1).T
        sdV = _null_sd_table(Dx, rng, lens, MV, half=band)
        sdH = _null_sd_table(Dy.T, rng, lens, MH, half=band)
        CV = _cum0(Dx, 0)
        CH = _cum0(Dy, 1).T                # transpose so rows index the scan axis

        Dxb = ndimage.uniform_filter1d(Dx, 2 * band + 1, axis=1) * (2 * band + 1)
        Dyb = ndimage.uniform_filter1d(Dy, 2 * band + 1, axis=0) * (2 * band + 1)
        CVb = _cum0(Dxb, 0); CHb = _cum0(Dyb, 1).T
        px = np.zeros(R.shape[1]); py = np.zeros(R.shape[0])
        for L in lens:
            if L >= R.shape[0] or not np.isfinite(sdV[L]):
                continue
            S = np.abs(CVb[L:, :] - CVb[:-L, :]) / sdV[L]
            S = np.where((MV[L:, :] - MV[:-L, :]) >= L - 1e-6, S, 0.0)
            px = np.maximum(px, S.max(axis=0))
            if L >= CH.shape[0]:
                continue
            T = np.abs(CHb[L:, :] - CHb[:-L, :]) / sdH[L]
            T = np.where((MH[L:, :] - MH[:-L, :]) >= L - 1e-6, T, 0.0)
            py = np.maximum(py, T.max(axis=0))
        cxs = np.array(_peaks(px, npeak, nms))
        cys = np.array(_peaks(py, npeak, nms))
        if len(cxs) < 2 or len(cys) < 2:
            continue
        Ix, Jx, Wp = _pairs(cxs, wmin, wmax)       # x-pairs -> rectangle width
        Iy, Jy, Hp = _pairs(cys, wmin, wmax)
        if len(Ix) == 0 or len(Iy) == 0:
            continue
        A, B = cxs[Ix], cxs[Jx]
        Cc, Dd = cys[Iy], cys[Jy]

        # (ncols, ny-pairs) and (nrows, nx-pairs)
        Vv = _band(CV, cxs, Cc, Dd, band)
        Hh = _band(CH, cys, A, B, band)
        okV = ((MV[Dd][:, cxs].T - MV[Cc][:, cxs].T) >= Hp[None, :] - 1e-6)
        okH = ((MH[B][:, cys].T - MH[A][:, cys].T) >= Wp[None, :] - 1e-6)

        sdh = np.array([_sd_of(sdV, lens, int(h)) for h in Hp])
        sdw = np.array([_sd_of(sdH, lens, int(w)) for w in Wp])
        Zl = Vv[Ix, :] / sdh[None, :]              # (nxp, nyp)
        Zr = Vv[Jx, :] / sdh[None, :]
        Zt = (Hh[Iy, :] / sdw[None, :]).T          # (nxp, nyp)
        Zb = (Hh[Jy, :] / sdw[None, :]).T
        good = okV[Ix, :] & okV[Jx, :] & okH[Iy, :].T & okH[Jy, :].T
        pol = ((Zl < 0) & (Zr > 0) & (Zt < 0) & (Zb > 0)) | \
              ((Zl > 0) & (Zr < 0) & (Zt > 0) & (Zb < 0))
        sc = np.minimum(np.minimum(np.abs(Zl), np.abs(Zr)),
                        np.minimum(np.abs(Zt), np.abs(Zb)))
        sc = np.where(good & pol, sc, 0.0)
        if polarity == "dark_inside":
            sc = np.where((Zl < 0) & (Zt < 0), sc, 0.0)
        elif polarity == "bright_inside":
            sc = np.where((Zl > 0) & (Zt > 0), sc, 0.0)
        ii, jj = np.nonzero(sc >= z_thr)
        t = math.radians(th)
        for u, v in zip(ii, jj):
            a, b = A[u], B[u]; c, d = Cc[v], Dd[v]
            ux = (a + b) / 2.0 - rad
            uy = (c + d) / 2.0 - rad
            gx = ux * math.cos(t) - uy * math.sin(t) + rad + off[0]
            gy = ux * math.sin(t) + uy * math.cos(t) + rad + off[1]
            out.append(dict(cx=float(gx), cy=float(gy), theta_deg=float(th),
                            w_px=float(b - a), h_px=float(d - c),
                            long_px=float(max(b - a, d - c)),
                            short_px=float(min(b - a, d - c)),
                            score=float(sc[u, v]),
                            z=[float(Zl[u, v]), float(Zr[u, v]),
                               float(Zt[u, v]), float(Zb[u, v])],
                            polarity="dark_inside" if Zl[u, v] < 0 else "bright_inside"))
    return nms_rects(out)


def nms_rects(rects, frac=0.5, cap=4000):
    """Greedy non-maximum suppression on centre distance scaled by size.
    `cap` bounds the O(n^2) sweep; it only ever discards LOW-scoring candidates,
    so it cannot manufacture a detection or raise a null's maximum."""
    rects = sorted(rects, key=lambda r: -r["score"])[:cap]
    keep = []
    for r in rects:
        ok = True
        for k in keep:
            lim = frac * min(k["short_px"], r["short_px"])
            if math.hypot(k["cx"] - r["cx"], k["cy"] - r["cy"]) < lim:
                ok = False
                break
        if ok:
            keep.append(r)
    return keep


# ----------------------------------------------------------------- synthetics

def synth(kind, n=420, ppm=26.0, seed=7, contrast=40.0, texture=18.0):
    """Ground truth the detector has never seen: a board-like textured field with
    or without a rectangle in it."""
    rng = np.random.default_rng(seed)
    base = 90.0 + texture * ndimage.gaussian_filter(rng.normal(size=(n, n)), 2.0) * 3.0
    base += rng.normal(scale=3.0, size=(n, n))
    mask = np.zeros((n, n), bool)
    yy, xx = np.mgrid[0:n, 0:n]
    mask[(yy - n / 2) ** 2 + (xx - n / 2) ** 2 < (n / 2 - 6) ** 2] = True
    truth = None
    if kind == "rect":
        w, h, th = 3.0 * ppm, 2.5 * ppm, 23.0
        t = math.radians(th)
        u = (xx - n / 2) * math.cos(t) + (yy - n / 2) * math.sin(t)
        v = -(xx - n / 2) * math.sin(t) + (yy - n / 2) * math.cos(t)
        body = (np.abs(u) <= w / 2) & (np.abs(v) <= h / 2)
        base = np.where(body, base - contrast, base)
        truth = dict(long_mm=w / ppm, short_mm=h / ppm, theta_deg=th, cx=n / 2, cy=n / 2)
    elif kind == "blob":
        b = ndimage.gaussian_filter(rng.normal(size=(n, n)), 9.0)
        base = np.where(b > np.percentile(b, 88), base - contrast, base)
    elif kind == "stripe":
        base = np.where(np.abs(xx - n / 2) < 1.5 * ppm, base - contrast, base)
    elif kind == "onesided":
        # The nRF's real situation, made synthetic: ONE strong boundary and three
        # that are nearly absent.  A clean four-edged synthetic cannot test the
        # side-crossing bound, because its sides never have any reason to wander --
        # that made selftest case 7 a check that could not fail, and this is the fix.
        w, h, th = 3.0 * ppm, 2.5 * ppm, 23.0
        t = math.radians(th)
        u = (xx - n / 2) * math.cos(t) + (yy - n / 2) * math.sin(t)
        v = -(xx - n / 2) * math.sin(t) + (yy - n / 2) * math.cos(t)
        body = (np.abs(u) <= w / 2) & (np.abs(v) <= h / 2)
        edge = body & (u < -w / 2 + 3)
        base = np.where(body, base - 2.0, base)          # three sides: 2 luma
        base = np.where(edge, base - contrast, base)     # one side: full contrast
        truth = dict(long_mm=w / ppm, short_mm=h / ppm, theta_deg=th, cx=n / 2, cy=n / 2)
    elif kind == "flat":
        pass
    return ndimage.gaussian_filter(base, 0.8), mask, truth


def maximal(rects, tol=0.72):
    """Keep only rectangles NOT nested inside a larger admitted one.

    A package outline has sub-features -- laser marking, lead frame, the pads under
    it -- and each of those is itself a small high-contrast rectangle.  Scoring
    alone prefers them, because a z-score grows with contrast linearly and with
    edge length only as sqrt.  Nesting is the geometric fact that separates them,
    and it does NOT select on size the way "take the biggest" would: a large
    rectangle sitting beside a small one keeps both."""
    out = []
    for r in rects:
        t = math.radians(r["theta_deg"])
        nested = False
        for q in rects:
            if q is r or q["long_px"] * q["short_px"] <= 1.3 * r["long_px"] * r["short_px"]:
                continue
            tq = math.radians(q["theta_deg"])
            dx, dy = r["cx"] - q["cx"], r["cy"] - q["cy"]
            u = dx * math.cos(tq) + dy * math.sin(tq)
            v = -dx * math.sin(tq) + dy * math.cos(tq)
            if abs(u) <= tol * q["w_px"] / 2 and abs(v) <= tol * q["h_px"] / 2:
                nested = True
                break
        if not nested:
            out.append(r)
    return out


def score_rect(lum, mask, ppm, cx, cy, theta_deg, w_px, h_px, *, smooth=1.0,
               band=1, seed=20260905, refine=0):
    """Score ONE stated rectangle.  A diagnostic, not a detector: it answers
    'would the scorer have accepted this if the candidate generator had proposed
    it?', which separates a scoring failure from a proposal failure."""
    rng = np.random.default_rng(seed)
    H, W = lum.shape
    rad = int(math.ceil(0.5 * math.hypot(H, W))) + 8
    Lp = np.pad(lum, ((rad, rad), (rad, rad)), mode="edge")
    Mp = np.pad(mask.astype(float), ((rad, rad), (rad, rad)), mode="constant")
    cxp, cyp = cx + rad, cy + rad
    if smooth > 0:
        Lp = ndimage.gaussian_filter(Lp, smooth)
    R = ndimage.rotate(Lp, theta_deg, reshape=False, order=1, mode="nearest")
    Mr = ndimage.rotate(Mp, theta_deg, reshape=False, order=1, mode="constant") > 0.995
    # where the centre lands after rotating about the array centre
    c0 = (Lp.shape[1] - 1) / 2.0, (Lp.shape[0] - 1) / 2.0
    t = math.radians(theta_deg)
    ux, uy = cxp - c0[0], cyp - c0[1]
    rx = ux * math.cos(t) + uy * math.sin(t) + c0[0]
    ry = -ux * math.sin(t) + uy * math.cos(t) + c0[1]
    Dx = np.zeros_like(R); Dx[:, 1:-1] = 0.5 * (R[:, 2:] - R[:, :-2])
    Dy = np.zeros_like(R); Dy[1:-1, :] = 0.5 * (R[2:, :] - R[:-2, :])
    Dx = np.where(Mr, Dx, 0.0); Dy = np.where(Mr, Dy, 0.0)
    lens = [max(2, int(round(v))) for v in (h_px, w_px)]
    MV = _cum0(Mr.astype(float), 0); MH = _cum0(Mr.astype(float), 1).T
    sdV = _null_sd_table(Dx, rng, lens, MV, half=band)
    sdH = _null_sd_table(Dy.T, rng, lens, MH, half=band)
    CV = _cum0(Dx, 0); CH = _cum0(Dy, 1).T
    a, b = int(round(rx - w_px / 2)), int(round(rx + w_px / 2))
    c, d = int(round(ry - h_px / 2)), int(round(ry + h_px / 2))
    best = None
    for da in range(-refine, refine + 1):
        for db in range(-refine, refine + 1):
            for dc in range(-refine, refine + 1):
                for dd in range(-refine, refine + 1):
                    A, B, C_, D_ = a + da, b + db, c + dc, d + dd
                    zl = float(_band(CV, [A], np.array([C_]), np.array([D_]), band)[0, 0]) / sdV[lens[0]]
                    zr = float(_band(CV, [B], np.array([C_]), np.array([D_]), band)[0, 0]) / sdV[lens[0]]
                    zt = float(_band(CH, [C_], np.array([A]), np.array([B]), band)[0, 0]) / sdH[lens[1]]
                    zb = float(_band(CH, [D_], np.array([A]), np.array([B]), band)[0, 0]) / sdH[lens[1]]
                    pol = (zl < 0 < zr and zt < 0 < zb) or (zr < 0 < zl and zb < 0 < zt)
                    sc = min(abs(zl), abs(zr), abs(zt), abs(zb)) if pol else 0.0
                    if best is None or sc > best["score"]:
                        best = dict(score=sc, z=[zl, zr, zt, zb], w_px=B - A, h_px=D_ - C_,
                                    sdV=sdV[lens[0]], sdH=sdH[lens[1]])
    return best


def score_grid(lum, mask, ppm, cx0, cy0, *, angles, wmm, hmm, rad_px=34, smooth=1.0,
               band=2, seed=20260905, stride=1):
    """Exhaustive local search: score EVERY rectangle near a stated centre, at
    every stated angle and size, with no peak-picking in the way.

    `detect` proposes candidate edges by peak-picking, which prefers short
    high-contrast strokes (laser marking) over a long faint package boundary.
    This function removes that stage entirely, so a disagreement between the two
    localises the failure: if score_grid finds the outline and detect does not,
    the defect is in PROPOSAL, not in SCORING."""
    rng = np.random.default_rng(seed)
    best = None
    R0 = int(math.ceil(max(wmm) * ppm + max(hmm) * ppm)) + rad_px + 12
    y0, y1 = int(cy0) - R0, int(cy0) + R0
    x0, x1 = int(cx0) - R0, int(cx0) + R0
    py = (max(0, -y0), max(0, y1 - lum.shape[0]))
    px_ = (max(0, -x0), max(0, x1 - lum.shape[1]))
    Lp = np.pad(lum, (py, px_), mode="edge")
    Mp = np.pad(mask.astype(float), (py, px_), mode="constant")
    Lc = Lp[y0 + py[0]:y1 + py[0], x0 + px_[0]:x1 + px_[0]]
    Mc = Mp[y0 + py[0]:y1 + py[0], x0 + px_[0]:x1 + px_[0]]
    if smooth > 0:
        Lc = ndimage.gaussian_filter(Lc, smooth)
    for th in angles:
        R = ndimage.rotate(Lc, th, reshape=False, order=1, mode="nearest")
        Mr = ndimage.rotate(Mc, th, reshape=False, order=1, mode="constant") > 0.995
        Mr = ndimage.binary_erosion(Mr, np.ones((5, 5)))
        Dx = np.zeros_like(R); Dx[:, 1:-1] = 0.5 * (R[:, 2:] - R[:, :-2])
        Dy = np.zeros_like(R); Dy[1:-1, :] = 0.5 * (R[2:, :] - R[:-2, :])
        Dx = np.where(Mr, Dx, 0.0); Dy = np.where(Mr, Dy, 0.0)
        MV = _cum0(Mr.astype(float), 0); MH = _cum0(Mr.astype(float), 1).T
        lens = sorted({max(2, int(round(v * ppm))) for v in list(wmm) + list(hmm)})
        sdV = _null_sd_table(Dx, rng, lens, MV, half=band)
        sdH = _null_sd_table(Dy.T, rng, lens, MH, half=band)
        CV = _cum0(Dx, 0); CH = _cum0(Dy, 1).T
        c = R0                                   # centre of the crop, both axes
        offs = np.arange(-rad_px, rad_px + 1, stride)
        for w in wmm:
            W = int(round(w * ppm))
            for h in hmm:
                Hh = int(round(h * ppm))
                A = c + offs - W // 2; B = A + W
                C_ = c + offs - Hh // 2; D_ = C_ + Hh
                if A.min() < 1 or B.max() >= R.shape[1] - 1:
                    continue
                if C_.min() < 1 or D_.max() >= R.shape[0] - 1:
                    continue
                zl = _band(CV, A, C_, D_, band) / _sd_of(sdV, lens, Hh)   # (nx, ny)
                zr = _band(CV, B, C_, D_, band) / _sd_of(sdV, lens, Hh)
                zt = (_band(CH, C_, A, B, band) / _sd_of(sdH, lens, W)).T
                zb = (_band(CH, D_, A, B, band) / _sd_of(sdH, lens, W)).T
                pol = ((zl < 0) & (zr > 0) & (zt < 0) & (zb > 0)) | \
                      ((zl > 0) & (zr < 0) & (zt > 0) & (zb < 0))
                sc = np.where(pol, np.minimum(np.minimum(np.abs(zl), np.abs(zr)),
                                              np.minimum(np.abs(zt), np.abs(zb))), 0.0)
                i, j = np.unravel_index(np.argmax(sc), sc.shape)
                if best is None or sc[i, j] > best["score"]:
                    t = math.radians(th)
                    ux, uy = float(offs[i]), float(offs[j])
                    best = dict(score=float(sc[i, j]), theta_deg=float(th),
                                w_px=float(W), h_px=float(Hh),
                                long_px=float(max(W, Hh)), short_px=float(min(W, Hh)),
                                cx=cx0 + ux * math.cos(t) - uy * math.sin(t),
                                cy=cy0 + ux * math.sin(t) + uy * math.cos(t),
                                z=[float(zl[i, j]), float(zr[i, j]),
                                   float(zt[i, j]), float(zb[i, j])])
    return best


def _local(lum, mask, cx, cy, theta_deg, R, smooth):
    """Crop a square window around (cx,cy) and rotate it so theta is axis-aligned."""
    H, W = lum.shape
    y0, x0 = int(round(cy)) - R, int(round(cx)) - R
    py = (max(0, -y0), max(0, y0 + 2 * R - H))
    px = (max(0, -x0), max(0, x0 + 2 * R - W))
    Lp = np.pad(lum, (py, px), mode="edge")
    Mp = np.pad(mask.astype(float), (py, px), mode="constant")
    Lc = Lp[y0 + py[0]:y0 + py[0] + 2 * R, x0 + px[0]:x0 + px[0] + 2 * R]
    Mc = Mp[y0 + py[0]:y0 + py[0] + 2 * R, x0 + px[0]:x0 + px[0] + 2 * R]
    if smooth > 0:
        Lc = ndimage.gaussian_filter(Lc, smooth)
    R_ = ndimage.rotate(Lc, theta_deg, reshape=False, order=1, mode="nearest")
    Mr = ndimage.rotate(Mc, theta_deg, reshape=False, order=1, mode="constant") > 0.995
    Mr = ndimage.binary_erosion(Mr, np.ones((5, 5)))
    return R_, Mr


def fit_sides(lum, mask, ppm, cx, cy, theta_deg, w_px, h_px, *, search=None,
              band=2, smooth=1.0, seed=20260905, iters=2, hp=0):
    """Fit the FOUR SIDES OF A RECTANGLE INDEPENDENTLY and report each side's own
    evidence.

    Closure -- requiring all four sides at once -- was refuted on this board by
    measurement: at the nRF52832's outline the four perpendicular luma profiles
    give a strong step, two weak steps and NO STEP AT ALL, and the interior luma
    runs 90/41/66/36 around one package because the illumination gradient across
    it is large.  A detector that demands four alike boundaries cannot recover a
    part whose fourth boundary is not in the data, and a detector that settles for
    the best CLOSED rectangle nearby returns a stable wrong answer (-26 % on the
    nRF, unmoved by every parameter) -- which is worse, because it looks measured.

    So: each side is scanned on its own, each carries its own |z| against the same
    empirical null, and the caller decides per AXIS whether a dimension exists.
    A dimension is real only when BOTH of its sides are supported."""
    rng = np.random.default_rng(seed)
    if search is None:
        search = int(round(0.45 * min(w_px, h_px)))
    R = int(math.ceil((w_px + h_px) / 2 + 2 * search)) + 14
    Rot, Mr = _local(lum, mask, cx, cy, theta_deg, R, smooth)
    Dx = np.zeros_like(Rot); Dx[:, 1:-1] = 0.5 * (Rot[:, 2:] - Rot[:, :-2])
    Dy = np.zeros_like(Rot); Dy[1:-1, :] = 0.5 * (Rot[2:, :] - Rot[:-2, :])
    Dx = highpass_grad(np.where(Mr, Dx, 0.0), hp, 1)
    Dy = highpass_grad(np.where(Mr, Dy, 0.0), hp, 0)
    Dx = np.where(Mr, Dx, 0.0); Dy = np.where(Mr, Dy, 0.0)
    MV = _cum0(Mr.astype(float), 0); MH = _cum0(Mr.astype(float), 1).T
    CV = _cum0(Dx, 0); CH = _cum0(Dy, 1).T
    c = R
    a, b = c - w_px / 2.0, c + w_px / 2.0
    cc, dd = c - h_px / 2.0, c + h_px / 2.0
    lens = sorted({max(2, int(round(v))) for v in
                   np.linspace(0.4 * min(w_px, h_px), 1.6 * max(w_px, h_px), 14)})
    sdV = _null_sd_table(Dx, rng, lens, MV, half=band)
    sdH = _null_sd_table(Dy.T, rng, lens, MH, half=band)

    def scan(C, Mc, sd, pos, span_lo, span_hi, lim_lo=None, lim_hi=None):
        """|z| of one side as its offset moves, at fixed opposite-axis span.

        lim_lo/lim_hi keep this side from wandering past its opposite number.
        Without them the two scans converge on the SAME strong edge and the
        rectangle collapses to zero width -- seen, and the reason this bound
        exists."""
        lo = int(round(pos)) - search if lim_lo is None else max(int(round(pos)) - search,
                                                                 int(round(lim_lo)))
        hi = int(round(pos)) + search if lim_hi is None else min(int(round(pos)) + search,
                                                                 int(round(lim_hi)))
        offs = np.arange(lo, hi + 1)
        offs = offs[(offs > band + 1) & (offs < C.shape[1] - band - 2)]
        if offs.size == 0 or span_hi <= span_lo:
            return None
        s0, s1 = int(round(span_lo)), int(round(span_hi))
        s0 = max(0, s0); s1 = min(C.shape[0] - 1, s1)
        if s1 - s0 < 2:
            return None
        v = _band(C, offs, np.array([s0]), np.array([s1]), band)[:, 0]
        cov = Mc[s1][offs] - Mc[s0][offs]
        z = v / _sd_of(sd, lens, s1 - s0)
        z = np.where(cov >= (s1 - s0) - 1e-6, z, 0.0)
        k = int(np.argmax(np.abs(z)))
        return dict(offset=float(offs[k]), z=float(z[k]),
                    profile=[float(x) for x in z], off0=float(offs[0]),
                    span=int(s1 - s0))

    gapw, gaph = 0.45 * w_px, 0.45 * h_px
    a0, b0, c0_, d0 = a, b, cc, dd
    out = {}
    for _ in range(max(1, iters)):
        L_ = scan(CV, MV, sdV, a0, cc, dd, lim_hi=b - gapw)
        R_ = scan(CV, MV, sdV, b0, cc, dd, lim_lo=a + gapw)
        T_ = scan(CH, MH, sdH, c0_, a, b, lim_hi=dd - gaph)
        B_ = scan(CH, MH, sdH, d0, a, b, lim_lo=cc + gaph)
        if L_: a = L_["offset"]
        if R_: b = R_["offset"]
        if T_: cc = T_["offset"]
        if B_: dd = B_["offset"]
        out = dict(left=L_, right=R_, top=T_, bottom=B_)
    t = math.radians(theta_deg)
    ux, uy = (a + b) / 2.0 - c, (cc + dd) / 2.0 - c
    return dict(sides=out, theta_deg=theta_deg,
                w_px=float(b - a), h_px=float(dd - cc),
                cx=cx + ux * math.cos(t) - uy * math.sin(t),
                cy=cy + ux * math.sin(t) + uy * math.cos(t),
                search_px=search)


def side_bar(lum, mask, ppm, w_px, h_px, *, n=80, band=2, smooth=1.0,
             seed=20260905, scramble=True, hp=0, sample_mask=None):
    """The bar a SINGLE side must clear.  Same scan, same span, same search range,
    at n random on-board locations of a phase-scrambled copy -- so it carries the
    same multiple-comparison burden the real scan does.  Returns the whole
    distribution, because the maximum of a null is itself noisy."""
    rng = np.random.default_rng(seed)
    src = lum
    if scramble:
        F = np.fft.rfft2(lum)
        ph = rng.uniform(-np.pi, np.pi, F.shape); ph[0, 0] = 0.0
        o = np.fft.irfft2(np.abs(F) * np.exp(1j * ph), s=lum.shape)
        src = (o - o.mean()) / (o.std() + 1e-9) * lum.std() + lum.mean()
    # WHERE the null is sampled and WHAT it is fitted against are different
    # questions.  Masking to a narrow annulus makes the fitter fight an artificial
    # boundary of my own making; sampling centres in the annulus while fitting
    # against the whole board asks the rim question without inventing an edge.
    ys, xs = np.nonzero(sample_mask if sample_mask is not None else mask)
    zs = []
    for i in range(n):
        k = rng.integers(0, len(ys))
        f = fit_sides(src, mask, ppm, float(xs[k]), float(ys[k]),
                      float(rng.uniform(0, 90)), w_px, h_px,
                      band=band, smooth=smooth, hp=hp,
                      seed=int(rng.integers(1 << 30)), iters=1)
        for s in f["sides"].values():
            if s:
                zs.append(abs(s["z"]))
    zs = np.array(zs) if zs else np.zeros(1)
    return dict(n=len(zs), p50=float(np.percentile(zs, 50)),
                p90=float(np.percentile(zs, 90)), p99=float(np.percentile(zs, 99)),
                max=float(zs.max()))


# ----------------------------------------------------------------- selftest

def selftest(verbose=True):
    """Synthetic ground truth and deliberate breaks.  Every case here failed on
    purpose at least once before it was trusted; cases 6 and 7 are REGRESSIONS for
    two real defects this file shipped and that are described at their fix sites."""
    P, F = [], []

    def check(name, ok, detail=""):
        (P if ok else F).append(name)
        if verbose:
            print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  -- ' + detail) if detail else ''}")

    ppm = 26.0
    lum, mask, truth = synth("rect", ppm=ppm)
    got = detect(lum, mask, ppm, astep=3.0, z_thr=4.0, band=1)
    top = max(got, key=lambda r: r["score"]) if got else None
    eL = 100 * (top["long_px"] / ppm - truth["long_mm"]) / truth["long_mm"] if top else 999
    eW = 100 * (top["short_px"] / ppm - truth["short_mm"]) / truth["short_mm"] if top else 999
    check("1 a 3.000 x 2.500 mm rectangle in board-like texture is recovered to 5 %",
          top is not None and abs(eL) < 5 and abs(eW) < 5,
          f"{top['long_px']/ppm:.3f} x {top['short_px']/ppm:.3f} mm, "
          f"{eL:+.1f} % / {eW:+.1f} %" if top else "nothing found")
    ref = top["score"] if top else 0.0

    worst = 0.0
    for kind in ("flat", "blob", "stripe"):
        for sd in (7, 8, 9):
            l2, m2, _ = synth(kind, ppm=ppm, seed=sd)
            g2 = detect(l2, m2, ppm, astep=3.0, z_thr=4.0, band=1)
            worst = max(worst, max((r["score"] for r in g2), default=0.0))
    check("2 no field WITHOUT a rectangle reaches the rectangle's score",
          worst < ref, f"best null {worst:.1f} against {ref:.1f}")

    g = detect(lum, mask, ppm, astep=3.0, z_thr=1e6, band=1)
    check("3 an impossible score requirement returns nothing", len(g) == 0, f"{len(g)} found")
    g = detect(lum, np.zeros_like(mask), ppm, astep=3.0, z_thr=4.0, band=1)
    check("4 an empty mask returns nothing", len(g) == 0, f"{len(g)} found")

    l0, m0, _ = synth("rect", ppm=ppm, contrast=0.0)
    g0 = detect(l0, m0, ppm, astep=3.0, z_thr=4.0, band=1)
    s0 = max((r["score"] for r in g0), default=0.0)
    check("5 the SAME image with the rectangle's contrast set to zero loses it",
          s0 < ref, f"{s0:.1f} against {ref:.1f}")

    # REGRESSION 6.  _null_sd_table once took its robust sd over spans lying off the
    # mask, where the derivative is identically zero.  Past 50 % zeros the MAD is
    # ZERO, every z becomes infinite and every rectangle scores the same -- a check
    # that SATURATES rather than one that fails.  Measured 1e11 before the fix.
    rng = np.random.default_rng(3)
    D = np.zeros((300, 300))
    D[120:180, :] = rng.normal(size=(60, 300))          # only 20 % of rows carry data
    Mc = np.zeros((300, 300), bool); Mc[120:180, :] = True
    tab = _null_sd_table(D, rng, [40], _cum0(Mc.astype(float), 0), half=1)
    check("6 REGRESSION: the null sd stays finite and non-zero when most spans are "
          "off-mask", np.isfinite(tab[40]) and tab[40] > 1e-6, f"sd = {tab[40]:.4f}")

    # REGRESSION 7.  fit_sides once let a side's scan walk onto its opposite number,
    # collapsing the rectangle to zero width.  The case must be ONE-SIDED: on a clean
    # four-edged synthetic the sides never wander, so removing the bound changed
    # nothing and the check could not fail.  Watched red with the bound removed.
    l7, m7, t7 = synth("onesided", ppm=ppm, contrast=90.0)
    r = fit_sides(l7, m7, ppm, t7["cx"], t7["cy"], t7["theta_deg"],
                  t7["long_mm"] * ppm, t7["short_mm"] * ppm, search=int(0.9 * ppm * 2.5))
    check("7 REGRESSION: with ONE strong side and three nearly absent, opposite sides "
          "still cannot cross", r["w_px"] > 0.3 * t7["long_mm"] * ppm and
          r["h_px"] > 0.3 * t7["short_mm"] * ppm,
          f"{r['w_px']/ppm:.3f} x {r['h_px']/ppm:.3f} mm")

    # 8.  maximal() must drop a nested rectangle and KEEP a neighbouring one.
    big = dict(cx=100., cy=100., theta_deg=0., w_px=80., h_px=80., long_px=80.,
               short_px=80., score=9.)
    inside = dict(cx=105., cy=98., theta_deg=0., w_px=20., h_px=20., long_px=20.,
                  short_px=20., score=20.)
    beside = dict(cx=220., cy=100., theta_deg=0., w_px=20., h_px=20., long_px=20.,
                  short_px=20., score=20.)
    keep = maximal([big, inside, beside])
    check("8 a nested rectangle is dropped and a neighbouring one is kept",
          big in keep and inside not in keep and beside in keep,
          f"{len(keep)} of 3 kept")

    # 9.  score_grid, with the peak-picking stage removed, must find the same truth.
    # w is the x-extent of the rotated frame, which is the LONG axis here
    b = score_grid(lum, mask, ppm, truth["cx"], truth["cy"],
                   angles=[truth["theta_deg"]], wmm=[truth["long_mm"]],
                   hmm=[truth["short_mm"]], rad_px=8, band=1)
    check("9 the exhaustive local search agrees with the peak-picking detector",
          b is not None and b["score"] > 0.5 * ref, f"{b['score']:.1f} against {ref:.1f}")

    # 10.  side_bar on a scrambled copy must not exceed the real rectangle's sides.
    rr = fit_sides(lum, mask, ppm, truth["cx"], truth["cy"], truth["theta_deg"],
                   truth["long_mm"] * ppm, truth["short_mm"] * ppm)
    zr = min(abs(s["z"]) for s in rr["sides"].values() if s)
    nb = side_bar(lum, mask, ppm, truth["long_mm"] * ppm, truth["short_mm"] * ppm, n=25)
    check("10 a spectrum-matched null does not reach the real rectangle's weakest side",
          nb["p99"] < zr, f"null p99 {nb['p99']:.1f} against weakest side {zr:.1f}")

    print(f"\n  {len(P)} passed, {len(F)} failed")
    return len(F) == 0


if __name__ == "__main__":
    import sys as _s
    print("d_rect selftest -- synthetic ground truth and deliberate breaks\n")
    _s.exit(0 if selftest() else 1)
