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


def _row_roll_null(D, rng):
    """Per-row independent circular roll.  Same per-row values, same along-row
    correlation, alignment BETWEEN rows destroyed.  E07 sec.2."""
    n, m = D.shape
    sh = rng.integers(0, m, size=n)
    idx = (np.arange(m)[None, :] + sh[:, None]) % m
    return np.take_along_axis(D, idx, axis=1)


def _null_sd_table(D, rng, lens, sub=3):
    """Robust sd of the line integral over each span length, measured on the null."""
    N = _row_roll_null(D, rng)
    C = _cum0(N, 0)
    out = {}
    for L in lens:
        if L >= C.shape[0]:
            out[L] = np.inf
            continue
        S = C[L::sub, :] - C[:-L:sub, :]
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


def _best3(C, cols, r0, r1):
    """Signed line integral at each of `cols`, taking the largest-magnitude of the
    three adjacent lines, for every (r0,r1) span.  Returns (ncols, nspans)."""
    n = C.shape[1] if C.ndim == 2 else 0
    out = None
    for o in (-1, 0, 1):
        c = np.clip(np.asarray(cols) + o, 0, C.shape[1] - 1)
        v = C[r1][:, c].T - C[r0][:, c].T          # (ncols, nspans)
        out = v if out is None else np.where(np.abs(v) > np.abs(out), v, out)
    return out


def detect(lum, mask, ppm, *, angles=None, astep=2.0, smooth=1.0,
           min_mm=0.7, max_mm=9.0, z_thr=6.0, npeak=22, nms=3,
           seed=20260905, ret_angles=False):
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

        sdV = _null_sd_table(Dx, rng, lens)
        sdH = _null_sd_table(Dy.T, rng, lens)
        CV = _cum0(Dx, 0)
        CH = _cum0(Dy, 1).T                # transpose so rows index the scan axis
        MV = _cum0(Mr.astype(float), 0)
        MH = _cum0(Mr.astype(float), 1).T

        px = np.zeros(R.shape[1]); py = np.zeros(R.shape[0])
        for L in lens:
            if L >= R.shape[0] or not np.isfinite(sdV[L]):
                continue
            S = np.abs(CV[L:, :] - CV[:-L, :]) / sdV[L]
            S = np.where((MV[L:, :] - MV[:-L, :]) >= L - 1e-6, S, 0.0)
            px = np.maximum(px, S.max(axis=0))
            if L >= CH.shape[0]:
                continue
            T = np.abs(CH[L:, :] - CH[:-L, :]) / sdH[L]
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
        Vv = _best3(CV, cxs, Cc, Dd)
        Hh = _best3(CH, cys, A, B)
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
    elif kind == "flat":
        pass
    return ndimage.gaussian_filter(base, 0.8), mask, truth
