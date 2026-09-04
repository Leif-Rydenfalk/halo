#!/usr/bin/env python3
"""m_board_outline.py -- r(theta) for the bare MLB's OUTER edge and CENTRE HOLE.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.

SIDE NAMING, stated per project convention (halo lane, commit 391f676):
  FRONT = the COMPONENT side, following Apple's own FCC filing captions.
  FCC internal photo 6 "MLB - Front"  == component side == FRONT.
  O'Flynn's "frontside" (battery contacts, NFC coil) is this project's BACK.

WHY NOT FIT A CIRCLE.  The centre hole is not a circle -- at 3x it is a rounded
square with a notch at top centre.  A circle fit would return a "diameter" that
describes nothing.  So the primitive here is r(theta), sub-pixel, and every
shape statement is derived from it.  A circle is fitted to the OUTER edge only,
and its per-angle residual is reported so the reader can judge circularity
instead of being told it.

EDGE CRITERION.  Along each ray, the board is dark and its surround (white
paper outside; over-exposed white paper seen through the hole) is bright.  The
edge is the half-way crossing between the LOCAL bright level and the LOCAL dark
level, both taken as robust medians of that same ray -- so a shadow gradient or
the tan watermark shifts both levels together and largely cancels.

WHAT IS EXCLUDED, AND IT IS REPORTED.  Apple drew four orange leader arrows that
touch the rim.  Orange (R-B large, R high) is masked and the affected angular
sectors are listed in the output as excluded, not silently averaged in.

Re-runnable.  Prints its inputs.  Raw r(theta) to JSON.
"""
import argparse, json, math, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def bilinear(img, x, y):
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx = x - x0; fy = y - y0
    h, w = img.shape[:2]
    x0 = np.clip(x0, 0, w - 2); y0 = np.clip(y0, 0, h - 2)
    a = img[y0, x0]; b = img[y0, x0 + 1]; c = img[y0 + 1, x0]; d = img[y0 + 1, x0 + 1]
    return (a * (1 - fx) * (1 - fy) + b * fx * (1 - fy)
            + c * (1 - fx) * fy + d * fx * fy)


def orange_mask(rgb):
    R = rgb[:, :, 0].astype(float); G = rgb[:, :, 1].astype(float); B = rgb[:, :, 2].astype(float)
    return (R - B > 70) & (R > 150) & (G > 80) & (G < R - 40)


def azimuthal_profile(lum, cx, cy, r_max, n_ang=180, step=0.5):
    """Mean luma vs radius about (cx,cy).  Used ONLY to bootstrap search windows,
    never to produce a reported number."""
    rs = np.arange(1.0, r_max, step)
    acc = np.zeros(len(rs))
    for k in range(n_ang):
        a = 2 * math.pi * k / n_ang
        acc += bilinear(lum, cx + rs * math.cos(a), cy + rs * math.sin(a))
    return rs, acc / n_ang


def bootstrap_radii(lum, cx, cy, r_max, level=150.0):
    """(hole radius, board radius) to ~1 px, from the azimuthal profile.

    Going outward the profile is: bright (over-exposed paper through the hole)
    -> dark (board) -> bright (paper).  Take the FIRST fall below `level` as the
    hole and the LAST rise above it as the board.
    """
    rs, v = azimuthal_profile(lum, cx, cy, r_max)
    above = v > level
    falls = [i for i in range(1, len(rs)) if above[i - 1] and not above[i]]
    rises = [i for i in range(1, len(rs)) if above[i] and not above[i - 1]]
    r_hole = float(rs[falls[0]]) if falls else None
    r_board = float(rs[rises[-1]]) if rises else None
    return r_hole, r_board, rs, v


def find_centre(lum, box, dark_thr):
    x0, y0, x1, y1 = box
    sub = lum[y0:y1, x0:x1]
    m = sub < dark_thr
    ys, xs = np.nonzero(m)
    if len(xs) < 500:
        return None
    # robust: trim 1% tails on each axis before taking the mean
    cx = float(np.mean(np.clip(xs, np.percentile(xs, 1), np.percentile(xs, 99)))) + x0
    cy = float(np.mean(np.clip(ys, np.percentile(ys, 1), np.percentile(ys, 99)))) + y0
    return cx, cy, int(m.sum())


def _smooth(v, sigma=1.2):
    n = max(3, int(round(sigma * 4)) | 1)
    x = np.arange(n) - n // 2
    k = np.exp(-0.5 * (x / sigma) ** 2); k /= k.sum()
    return np.convolve(v, k, mode="same")


def ray_edge(lum, bad, cx, cy, ang, r_lo, r_hi, mode, step=0.25, method="gradient",
             sigma=1.2, min_step=40.0):
    """Sub-pixel radius of the board edge along one ray.

    method 'gradient' (DEFAULT AND THE ONLY ONE TRUSTED):
        the edge is the extremum of dLuma/dr, located to sub-pixel by parabolic
        interpolation on the smoothed derivative.

    method 'halfmax' (KEPT ONLY AS THE NEGATIVE CONTROL -- it is WRONG here):
        the half-way crossing between the ray's dark and bright medians.  The
        board casts a soft shadow on the white paper, so the half-way level
        lands inside the PENUMBRA and the returned radius is the shadow's, not
        the board's.  m_selftest_outline.py exercises this deliberately.

    mode 'out': dark inside, bright outside.  mode 'in': bright inside, dark out.
    """
    rs = np.arange(r_lo, r_hi, step)
    xs = cx + rs * math.cos(ang); ys = cy + rs * math.sin(ang)
    v = bilinear(lum, xs, ys)
    blocked = bilinear(bad.astype(float), xs, ys) > 0.25
    if blocked.mean() > 0.10:
        return None, "orange leader arrow crosses this ray"
    n = len(rs)
    q = max(6, n // 6)
    if mode == "out":
        dark = float(np.median(v[:q])); bright = float(np.median(v[-q:]))
    else:
        bright = float(np.median(v[:q])); dark = float(np.median(v[-q:]))
    if bright - dark < min_step:
        return None, "luma step below the %.0f minimum along this ray" % min_step

    if method == "halfmax":
        thr = 0.5 * (dark + bright)
        above = v > thr
        if mode == "out":
            idx = [i for i in range(1, n) if above[i] and not above[i - 1]]
            if not idx: return None, "no dark->bright crossing"
            i = idx[-1]
        else:
            idx = [i for i in range(1, n) if (not above[i]) and above[i - 1]]
            if not idx: return None, "no bright->dark crossing"
            i = idx[0]
        v0, v1 = v[i - 1], v[i]
        f = 0.0 if v1 == v0 else (thr - v0) / (v1 - v0)
        return float(rs[i - 1] + f * step), None

    g = np.gradient(_smooth(v, sigma / step))
    sig = g if mode == "out" else -g
    m = 3
    if n < 2 * m + 3:
        return None, "ray too short"
    j = int(np.argmax(sig[m:n - m])) + m
    if sig[j] <= 0:
        return None, "no step of the expected sign along this ray"
    y0, y1, y2 = sig[j - 1], sig[j], sig[j + 1]
    den = y0 - 2 * y1 + y2
    dj = 0.5 * (y0 - y2) / den if den != 0 else 0.0
    dj = max(-1.0, min(1.0, dj))
    return float(rs[j] + dj * step), None


def fit_circle(x, y):
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x ** 2 + y ** 2
    s, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = s[0], s[1]
    r = math.sqrt(s[2] + cx ** 2 + cy ** 2)
    return cx, cy, r


def profile(lum, bad, cx, cy, r_lo, r_hi, mode, n_ang=720, method="gradient"):
    out, dropped = [], {}
    for k in range(n_ang):
        a = 2 * math.pi * k / n_ang
        r, why = ray_edge(lum, bad, cx, cy, a, r_lo, r_hi, mode, method=method)
        if r is None:
            dropped.setdefault(why, []).append(round(math.degrees(a), 1))
        else:
            out.append((math.degrees(a), r))
    return out, dropped


def refine(lum, bad, cx, cy, r_lo, r_hi, mode, iters=3, n_ang=360, method="gradient"):
    for _ in range(iters):
        pr, _ = profile(lum, bad, cx, cy, r_lo, r_hi, mode, n_ang, method)
        if len(pr) < 60:
            return cx, cy, None
        A = np.array([math.radians(a) for a, _ in pr]); R = np.array([r for _, r in pr])
        X = cx + R * np.cos(A); Y = cy + R * np.sin(A)
        nx, ny, nr = fit_circle(X, Y)
        if math.hypot(nx - cx, ny - cy) < 0.02:
            cx, cy = nx, ny
            break
        cx, cy = nx, ny
    return cx, cy, nr


def describe(pr, cx, cy, label):
    A = np.array([math.radians(a) for a, _ in pr]); R = np.array([r for _, r in pr])
    X = cx + R * np.cos(A); Y = cy + R * np.sin(A)
    fx, fy, fr = fit_circle(X, Y)
    resid = np.hypot(X - fx, Y - fy) - fr
    # per-angle radius about the FITTED centre
    Rf = np.hypot(X - fx, Y - fy)
    return dict(
        label=label, n_angles=len(pr),
        fitted_centre_px=[round(fx, 2), round(fy, 2)],
        r_mean_px=round(float(Rf.mean()), 3), r_min_px=round(float(Rf.min()), 3),
        r_max_px=round(float(Rf.max()), 3),
        r_sd_px=round(float(Rf.std()), 3),
        r_p5_px=round(float(np.percentile(Rf, 5)), 3),
        r_p95_px=round(float(np.percentile(Rf, 95)), 3),
        circle_fit_r_px=round(fr, 3),
        circle_fit_resid_sd_px=round(float(resid.std()), 3),
        circle_fit_resid_max_px=round(float(np.abs(resid).max()), 3),
        peak_to_peak_px=round(float(Rf.max() - Rf.min()), 3),
        theta_of_r_max_deg=round(float(np.degrees(A[int(np.argmax(Rf))])), 1),
        theta_of_r_min_deg=round(float(np.degrees(A[int(np.argmin(Rf))])), 1),
        _A=A, _R=Rf, _X=X, _Y=Y,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", default="fcc-BCGA2187-internal-photo-6.jpg")
    ap.add_argument("--box", default="700,440,1200,920", help="x0,y0,x1,y1 search box for the board")
    ap.add_argument("--px-per-mm", type=float, default=None)
    ap.add_argument("--px-per-mm-label", default="unstated")
    ap.add_argument("--n-ang", type=int, default=720)
    ap.add_argument("--method", default="gradient", choices=["gradient", "halfmax"],
                help="halfmax is the NEGATIVE CONTROL and is wrong on a shadowed edge")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    path = os.path.join(ROOT, "images", "airtag", a.image)
    rgb = np.asarray(Image.open(path).convert("RGB"))
    lum = np.asarray(Image.open(path).convert("L")).astype(float)
    bad = orange_mask(rgb)
    box = tuple(int(v) for v in a.box.split(","))
    print(f"m_board_outline.py -- inputs:")
    print(f"  image        {os.path.relpath(path, ROOT)}  ({rgb.shape[1]}x{rgb.shape[0]})")
    print(f"  search box   {box}")
    print(f"  scale basis  {a.px_per_mm} px/mm  [{a.px_per_mm_label}]")
    print(f"  rays         {a.n_ang} angles, method={a.method}, step 0.25 px")
    print(f"  orange-arrow mask: {int(bad[box[1]:box[3], box[0]:box[2]].sum())} px inside the box")

    c = find_centre(lum, box, 120)
    if c is None:
        print("  CANNOT DETERMINE: fewer than 500 dark pixels in the search box")
        return
    cx, cy, ndark = c
    print(f"  seed centre  ({cx:.1f}, {cy:.1f}) from {ndark} dark px (luma<120)")

    r_hole0, r_board0, prs, pv = bootstrap_radii(lum, cx, cy, 340.0)
    print(f"  bootstrap (azimuthal luma profile, crossing level 150):"
          f" hole ~{r_hole0} px, board ~{r_board0} px")
    if r_board0 is None:
        print("  CANNOT DETERMINE: the azimuthal profile never returns to paper level")
        return

    # OUTER: tight window around the bootstrap radius, centre re-fitted twice
    for _ in range(3):
        pr, _d = profile(lum, bad, cx, cy, r_board0 * 0.88, r_board0 * 1.14, "out", 360, a.method)
        if len(pr) < 100:
            print("  CANNOT DETERMINE: outer edge gave <100 usable rays")
            return
        A = np.array([math.radians(t) for t, _ in pr]); R = np.array([r for _, r in pr])
        nx, ny, nr = fit_circle(cx + R * np.cos(A), cy + R * np.sin(A))
        moved = math.hypot(nx - cx, ny - cy)
        cx, cy = nx, ny
        if moved < 0.05:
            break
    r_out = nr
    print(f"  outer edge: centre ({cx:.2f}, {cy:.2f}), r {r_out:.2f} px "
          f"(window {r_board0*0.88:.0f}..{r_board0*1.14:.0f} px)")
    pr_out, drop_out = profile(lum, bad, cx, cy, r_out * 0.90, r_out * 1.12, "out", a.n_ang, a.method)
    d_out = describe(pr_out, cx, cy, "outer edge")

    # INNER: the hole is NOT round, so the window must be generous, but it is
    # anchored on the bootstrap so a bright component cannot capture the ray.
    if r_hole0 is None:
        d_in, drop_in = None, {}
        print("  centre hole: CANNOT DETERMINE - the azimuthal profile shows no bright core")
    else:
        pr_in, drop_in = profile(lum, bad, cx, cy, max(2.0, r_hole0 * 0.55),
                                 r_hole0 * 1.55, "in", a.n_ang, a.method)
        d_in = describe(pr_in, cx, cy, "centre hole") if len(pr_in) > 100 else None

    def report(d, drops, name):
        print(f"\n  {name.upper()}")
        if d is None:
            print("    CANNOT DETERMINE - too few usable rays")
            return
        print(f"    usable rays {d['n_angles']}/{a.n_ang}; fitted centre {d['fitted_centre_px']}")
        print(f"    radius  mean {d['r_mean_px']:.2f}  min {d['r_min_px']:.2f} (at {d['theta_of_r_min_deg']:+.0f} deg)"
              f"  max {d['r_max_px']:.2f} (at {d['theta_of_r_max_deg']:+.0f} deg)")
        print(f"    sd {d['r_sd_px']:.2f} px, peak-to-peak {d['peak_to_peak_px']:.2f} px"
              f"  ({100*d['peak_to_peak_px']/d['r_mean_px']:.1f}% of mean radius)")
        print(f"    circle fit r {d['circle_fit_r_px']:.2f} px, resid sd {d['circle_fit_resid_sd_px']:.2f}, "
              f"max {d['circle_fit_resid_max_px']:.2f} px")
        if a.px_per_mm:
            s = a.px_per_mm
            print(f"    -> diameter {2*d['r_mean_px']/s:.3f} mm mean, "
                  f"{2*d['r_min_px']/s:.3f} .. {2*d['r_max_px']/s:.3f} mm  "
                  f"[at {s} px/mm, {a.px_per_mm_label}]")
        for why, angs in drops.items():
            print(f"    DISCARDED {len(angs)} rays: {why}  (e.g. {angs[:6]}...)")

    report(d_out, drop_out, "outer edge")
    report(d_in, drop_in, "centre hole")

    if a.px_per_mm and d_out:
        print(f"\n  RATIO hole/board (scale-free, survives a better datum): "
              f"{d_in['r_mean_px']/d_out['r_mean_px']:.4f}" if d_in else "")

    if a.json:
        def strip(d):
            if d is None: return None
            o = {k: v for k, v in d.items() if not k.startswith("_")}
            o["r_theta_deg_px"] = [[round(float(math.degrees(t)), 2), round(float(r), 3)]
                                   for t, r in zip(d["_A"], d["_R"])]
            return o
        json.dump(dict(
            tool="m_board_outline.py", image=os.path.relpath(path, ROOT),
            side_convention="FRONT = component side (Apple FCC caption); "
                            "O'Flynn 'frontside' is this project's BACK",
            search_box=list(box), n_angles=a.n_ang, method=a.method,
            px_per_mm=a.px_per_mm, px_per_mm_label=a.px_per_mm_label,
            outer=strip(d_out), inner=strip(d_in),
            discarded_outer={k: v for k, v in drop_out.items()},
            discarded_inner={k: v for k, v in drop_in.items()},
        ), open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")


if __name__ == "__main__":
    main()
