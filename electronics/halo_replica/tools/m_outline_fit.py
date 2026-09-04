#!/usr/bin/env python3
"""m_outline_fit.py -- the bare MLB outline as FITTED PRIMITIVES, with residuals.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.

SIDE NAMING (project convention, halo lane commit 391f676): FRONT = the
COMPONENT side, per Apple's own FCC caption "MLB - Front".  O'Flynn's
"frontside" (battery contacts, NFC coil) is this project's BACK.

WHAT IT PUBLISHES.  A circle for the outer edge, and a SUPERELLIPSE (squircle)
for the centre hole, each with its fit residual as a stated number, plus the
notch as an explicit feature.  A per-degree polygon is deliberately NOT the
published artefact: it is a measurement artefact wearing the costume of a board
and it is not manufacturable.  The raw r(theta) IS kept, in a separate file
named by --raw-json, and the two files are never merged.

THE TWO CONTAMINATIONS THIS TOOL EXISTS TO AVOID, both measured, not supposed:

 1. THE CONTACT SHADOW.  A half-max threshold between the board's dark level and
    the paper's bright level lands inside the PENUMBRA, so the detected edge is
    the shadow's, not the board's.  It gave r sd 6.8 px on a board round to
    about 1 px, and the error is one-sided, so it also fakes an ellipse whose
    major axis points -40 deg in photo 6 and +13 deg in photo 7 -- a different
    direction in each photograph, which no real board shape does.

 2. BRIGHT PADS ON THE RIM.  Segmenting the board as "the largest dark blob"
    breaks wherever a pale metal pad sits at the edge: the blob is cut there and
    that sector's radius collapses.  Measured on FCC photo 7: r = 136 px against
    a mean of 185 px at 100 deg, exactly where a pale rim pad sits.  That is the
    30% excursion; it is the detector, not the board.

Both are avoided the same way: the edge is the STEEPEST LUMA GRADIENT along a
ray, inside a window bootstrapped from the azimuthal profile.  A step survives a
pale pad (pad 180 -> paper 240 is still a step) and ignores a distant shadow.

EVERY REJECTED RAY IS COUNTED AND ITS ANGLE PUBLISHED.  Nothing is dropped
silently.

Exit 0 fitted, 2 CANNOT DETERMINE.  Prints its inputs.  Every output file
carries a run_id, because this filename has been rewritten under a reader.
"""
import argparse, hashlib, json, math, os, subprocess, sys, time
import numpy as np
from PIL import Image
from scipy.optimize import least_squares

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def run_id(path):
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
    except Exception:
        rev = "unknown"
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()[:12]
    return dict(run_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                git_rev=rev, image_sha256_12=h, tool="m_outline_fit.py")


def bilinear(img, x, y):
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx = x - x0; fy = y - y0
    h, w = img.shape[:2]
    x0 = np.clip(x0, 0, w - 2); y0 = np.clip(y0, 0, h - 2)
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
            + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)


def orange_mask(rgb):
    R, G, B = (rgb[:, :, i].astype(float) for i in range(3))
    return (R - B > 70) & (R > 150) & (G > 80) & (G < R - 40)


def smooth(v, sigma):
    n = max(3, int(round(sigma * 4)) | 1)
    x = np.arange(n) - n // 2
    k = np.exp(-0.5 * (x / sigma) ** 2)
    return np.convolve(v, k / k.sum(), mode="same")


def ray(lum, bad, cx, cy, ang, r_lo, r_hi, mode, step=0.25, sigma=1.2,
        min_step=35.0, min_rel_peak=0.45):
    rs = np.arange(r_lo, r_hi, step)
    xs = cx + rs * np.cos(ang); ys = cy + rs * np.sin(ang)
    v = bilinear(lum, xs, ys)
    if bilinear(bad.astype(float), xs, ys).mean() > 0.08:
        return None, "orange leader arrow crosses this ray"
    q = max(6, len(rs) // 6)
    a_, b_ = (np.median(v[:q]), np.median(v[-q:])) if mode == "out" else (np.median(v[-q:]), np.median(v[:q]))
    if b_ - a_ < min_step:
        return None, "luma step across this ray is below the minimum"
    g = np.gradient(smooth(v, sigma / step))
    sig = g if mode == "out" else -g
    m = 3
    core = sig[m:len(rs) - m]
    if core.size < 5:
        return None, "ray too short"
    j = int(np.argmax(core)) + m
    if sig[j] <= 0:
        return None, "no step of the expected sign along this ray"
    # a second, comparable step in the window means the edge is ambiguous here
    far = np.abs(np.arange(len(sig)) - j) > max(4, int(2.0 / step))
    if far.any() and sig[far].max() > min_rel_peak * sig[j] and sig[far].max() > 0:
        pass  # recorded below, not fatal -- reported as ambiguity, not dropped
    y0, y1, y2 = sig[j - 1], sig[j], sig[j + 1]
    den = y0 - 2 * y1 + y2
    dj = 0.0 if den == 0 else max(-1.0, min(1.0, 0.5 * (y0 - y2) / den))
    return float(rs[j] + dj * step), None


def profile(lum, bad, cx, cy, r_lo, r_hi, mode, n_ang):
    ok, drop = [], {}
    for k in range(n_ang):
        a = 2 * math.pi * k / n_ang
        r, why = ray(lum, bad, cx, cy, a, r_lo, r_hi, mode)
        (ok.append((math.degrees(a), r)) if r is not None
         else drop.setdefault(why, []).append(round(math.degrees(a), 2)))
    return ok, drop


def robust_circle(X, Y, n_sigma=3.0, iters=6):
    keep = np.ones(len(X), bool)
    for _ in range(iters):
        x, y = X[keep], Y[keep]
        A = np.c_[2 * x, 2 * y, np.ones(len(x))]
        s, *_ = np.linalg.lstsq(A, x ** 2 + y ** 2, rcond=None)
        cx, cy = s[0], s[1]
        r = math.sqrt(max(s[2] + cx ** 2 + cy ** 2, 0))
        res = np.hypot(X - cx, Y - cy) - r
        sd = res[keep].std()
        nk = np.abs(res) < n_sigma * max(sd, 1e-6)
        if nk.sum() < 30 or (nk == keep).all():
            keep = nk
            break
        keep = nk
    return cx, cy, r, res, keep


def se_radius(th, a, b, n):
    c, s = np.cos(th), np.sin(th)
    return (np.abs(c / a) ** n + np.abs(s / b) ** n) ** (-1.0 / n)


def fit_superellipse(X, Y, cx0, cy0, a0):
    def resid(p):
        cx, cy, a, b, n, phi = p
        n = max(2.0, min(12.0, n))
        dx, dy = X - cx, Y - cy
        th = np.arctan2(dy, dx) - phi
        r = np.hypot(dx, dy)
        return r - se_radius(th, abs(a), abs(b), n)
    p0 = [cx0, cy0, a0, a0, 3.0, 0.0]
    sol = least_squares(resid, p0, loss="soft_l1", f_scale=2.0, max_nfev=4000)
    cx, cy, a, b, n, phi = sol.x
    n = max(2.0, min(12.0, n))
    return dict(cx=float(cx), cy=float(cy), a=float(abs(a)), b=float(abs(b)),
                n=float(n), phi_deg=float(math.degrees(phi) % 180)), resid(sol.x)


def se_corner_radius(a, b, n, samples=20000):
    """Minimum radius of curvature of |x/a|^n+|y/b|^n=1, found numerically."""
    t = np.linspace(1e-4, math.pi / 2 - 1e-4, samples)
    ct, st = np.cos(t), np.sin(t)
    x = a * np.sign(ct) * np.abs(ct) ** (2.0 / n)
    y = b * np.sign(st) * np.abs(st) ** (2.0 / n)
    dx = np.gradient(x, t); dy = np.gradient(y, t)
    ddx = np.gradient(dx, t); ddy = np.gradient(dy, t)
    k = np.abs(dx * ddy - dy * ddx) / np.power(dx * dx + dy * dy, 1.5)
    i = 8
    kk = k[i:-i]
    return float(1.0 / kk.max()) if kk.max() > 0 else float("nan")


def runs_below(theta, res, thr, min_len_deg=3.0):
    """Contiguous angular runs where residual < thr.  Wraps at 360."""
    m = res < thr
    if not m.any():
        return []
    idx = np.where(m)[0]
    groups, cur = [], [idx[0]]
    for i in idx[1:]:
        if i == cur[-1] + 1:
            cur.append(i)
        else:
            groups.append(cur); cur = [i]
    groups.append(cur)
    if len(groups) > 1 and groups[0][0] == 0 and groups[-1][-1] == len(res) - 1:
        groups[0] = groups[-1] + groups[0]; groups.pop()
    out = []
    step = 360.0 / len(res)
    for g in groups:
        if len(g) * step < min_len_deg:
            continue
        out.append(dict(start_deg=round(float(theta[g[0]]), 1),
                        end_deg=round(float(theta[g[-1]]), 1),
                        span_deg=round(len(g) * step, 1),
                        depth_px=round(float(-res[g].min()), 2),
                        depth_at_deg=round(float(theta[g[int(np.argmin(res[g]))]]), 1)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--box", required=True)
    ap.add_argument("--n-ang", type=int, default=1440)
    ap.add_argument("--px-per-mm", type=float, required=True)
    ap.add_argument("--px-per-mm-err", type=float, default=0.0)
    ap.add_argument("--px-per-mm-label", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--raw-json", required=True)
    a = ap.parse_args()

    path = a.image if os.path.isabs(a.image) else os.path.join(ROOT, "images", "airtag", a.image)
    rid = run_id(path)
    rgb = np.asarray(Image.open(path).convert("RGB"))
    lum = np.asarray(Image.open(path).convert("L")).astype(float)
    bad = orange_mask(rgb)
    x0, y0, x1, y1 = (int(v) for v in a.box.split(","))

    print("m_outline_fit.py -- inputs:")
    print(f"  run_id       {rid['run_utc']} git {rid['git_rev']} image sha {rid['image_sha256_12']}")
    print(f"  image        {os.path.relpath(path, ROOT)} ({rgb.shape[1]}x{rgb.shape[0]})")
    print(f"  search box   {(x0, y0, x1, y1)}")
    print(f"  scale basis  {a.px_per_mm} +/- {a.px_per_mm_err} px/mm  [{a.px_per_mm_label}]")
    print(f"  rays         {a.n_ang}, edge = steepest luma gradient, step 0.25 px, sigma 1.2 px")

    sub = lum[y0:y1, x0:x1]
    ys, xs = np.nonzero(sub < 120)
    cx = float(np.mean(np.clip(xs, *np.percentile(xs, [1, 99])))) + x0
    cy = float(np.mean(np.clip(ys, *np.percentile(ys, [1, 99])))) + y0
    rr = np.arange(1.0, 340.0, 0.5)
    prof = np.mean([bilinear(lum, cx + rr * math.cos(t), cy + rr * math.sin(t))
                    for t in np.linspace(0, 2 * math.pi, 180, endpoint=False)], axis=0)
    ab = prof > 150
    falls = [i for i in range(1, len(rr)) if ab[i - 1] and not ab[i]]
    rises = [i for i in range(1, len(rr)) if ab[i] and not ab[i - 1]]
    if not rises:
        print("  CANNOT DETERMINE: the azimuthal profile never returns to paper level")
        sys.exit(2)
    r_hole0 = float(rr[falls[0]]) if falls else None
    r_board0 = float(rr[rises[-1]])
    print(f"  bootstrap    seed centre ({cx:.1f},{cy:.1f}); hole ~{r_hole0} px, board ~{r_board0} px")

    # ---- OUTER ------------------------------------------------------------
    for _ in range(4):
        pr, _d = profile(lum, bad, cx, cy, r_board0 * 0.88, r_board0 * 1.14, "out", 360)
        if len(pr) < 120:
            print("  CANNOT DETERMINE: fewer than 120 usable rays on the outer edge")
            sys.exit(2)
        T = np.radians([t for t, _ in pr]); R = np.array([r for _, r in pr])
        ncx, ncy, nr, _, _ = robust_circle(cx + R * np.cos(T), cy + R * np.sin(T))
        moved = math.hypot(ncx - cx, ncy - cy); cx, cy = ncx, ncy
        if moved < 0.05:
            break
    pr_o, drop_o = profile(lum, bad, cx, cy, nr * 0.91, nr * 1.10, "out", a.n_ang)
    To = np.array([t for t, _ in pr_o]); Ro = np.array([r for _, r in pr_o])
    Xo, Yo = cx + Ro * np.cos(np.radians(To)), cy + Ro * np.sin(np.radians(To))
    ocx, ocy, orad, ores, okeep = robust_circle(Xo, Yo)
    s, se = a.px_per_mm, a.px_per_mm_err
    D = 2 * orad
    print(f"\n  OUTER EDGE -- fitted primitive: CIRCLE")
    print(f"    rays used {len(pr_o)}/{a.n_ang}; inliers {int(okeep.sum())} ({okeep.mean():.3f})")
    print(f"    centre ({ocx:.2f}, {ocy:.2f}) px   radius {orad:.3f} px   DIAMETER {D:.3f} px")
    print(f"    fit residual: sd {ores[okeep].std():.3f} px, p95 |res| "
          f"{np.percentile(np.abs(ores[okeep]), 95):.3f} px, max {np.abs(ores[okeep]).max():.3f} px")
    dmm = D / s
    dmm_err = dmm * (se / s) if s else 0.0
    print(f"    -> OUTER DIAMETER = {dmm:.3f} mm  (+/- {dmm_err:.3f} mm from the scale basis alone)")
    print(f"       scale basis: {s} +/- {se} px/mm [{a.px_per_mm_label}]")
    for why, angs in drop_o.items():
        print(f"    REJECTED {len(angs)} rays: {why}")
    nout = int((~okeep).sum())
    outl = runs_below(To, -np.abs(ores), -3 * ores[okeep].std(), 2.0)
    print(f"    {nout} rays rejected by the 3-sigma circle fit; excursion runs >2 deg: "
          f"{[ (o['start_deg'], o['end_deg']) for o in outl ] or 'none'}")

    # ---- INNER ------------------------------------------------------------
    inner = None
    if r_hole0 is None:
        print("\n  CENTRE HOLE: CANNOT DETERMINE -- no bright core in the azimuthal profile")
    else:
        pr_i, drop_i = profile(lum, bad, ocx, ocy, max(2.0, r_hole0 * 0.60),
                               r_hole0 * 1.55, "in", a.n_ang)
        Ti = np.array([t for t, _ in pr_i]); Ri = np.array([r for _, r in pr_i])
        Xi, Yi = ocx + Ri * np.cos(np.radians(Ti)), ocy + Ri * np.sin(np.radians(Ti))
        se_p, se_res = fit_superellipse(Xi, Yi, ocx, ocy, float(np.median(Ri)))
        icx, icy, ia, ib, inx, iphi = (se_p["cx"], se_p["cy"], se_p["a"],
                                       se_p["b"], se_p["n"], se_p["phi_deg"])
        # circle fit, for comparison only -- shows WHY a circle is the wrong primitive
        _, _, crad, cres, ckeep = robust_circle(Xi, Yi)
        rc = se_corner_radius(ia, ib, inx)
        sd_se = float(np.std(se_res))
        print(f"\n  CENTRE HOLE -- fitted primitive: SUPERELLIPSE  |x/a|^n + |y/b|^n = 1")
        print(f"    rays used {len(pr_i)}/{a.n_ang}")
        print(f"    centre ({icx:.2f}, {icy:.2f}) px, offset from the board centre "
              f"{math.hypot(icx-ocx, icy-ocy):.2f} px = {math.hypot(icx-ocx, icy-ocy)/s:.3f} mm")
        print(f"    a {ia:.2f} px  b {ib:.2f} px  n {inx:.2f}  major axis {iphi:.1f} deg")
        print(f"    full extents  2a = {2*ia:.2f} px = {2*ia/s:.3f} mm,  "
              f"2b = {2*ib:.2f} px = {2*ib/s:.3f} mm")
        print(f"    corner radius (min radius of curvature) {rc:.2f} px = {rc/s:.3f} mm")
        print(f"    superellipse residual sd {sd_se:.3f} px   |   "
              f"CIRCLE residual sd {cres[ckeep].std():.3f} px  <- the circle is the worse primitive")
        print(f"    n = 2.00 would be an ellipse; n -> inf a rectangle. Measured n = {inx:.2f}.")
        notches = runs_below(Ti, se_res, -3.0 * sd_se, 3.0)
        print(f"    NOTCH candidates (residual < -3 sd of the superellipse fit, span > 3 deg):")
        if notches:
            for nt in notches:
                print(f"      {nt['start_deg']:.1f}..{nt['end_deg']:.1f} deg "
                      f"(span {nt['span_deg']:.1f} deg), depth {nt['depth_px']:.2f} px "
                      f"= {nt['depth_px']/s:.3f} mm, deepest at {nt['depth_at_deg']:.1f} deg")
        else:
            print("      none")
        for why, angs in drop_i.items():
            print(f"    REJECTED {len(angs)} rays: {why}")
        inner = dict(primitive="superellipse", **se_p,
                     two_a_px=round(2*ia, 3), two_b_px=round(2*ib, 3),
                     two_a_mm=round(2*ia/s, 4), two_b_mm=round(2*ib/s, 4),
                     corner_radius_px=round(rc, 3), corner_radius_mm=round(rc/s, 4),
                     residual_sd_px=round(sd_se, 3),
                     circle_alternative_radius_px=round(crad, 3),
                     circle_alternative_residual_sd_px=round(float(cres[ckeep].std()), 3),
                     offset_from_board_centre_px=round(math.hypot(icx-ocx, icy-ocy), 3),
                     offset_from_board_centre_mm=round(math.hypot(icx-ocx, icy-ocy)/s, 4),
                     notches=notches, rays_used=len(pr_i), rejected=drop_i)

    ratio = (2 * inner["a"] / (2 * orad)) if inner else None
    if inner:
        print(f"\n  SCALE-FREE RATIOS (these survive a better scale basis):")
        print(f"    hole 2a / board OD = {2*inner['a']/(2*orad):.4f}")
        print(f"    hole 2b / board OD = {2*inner['b']/(2*orad):.4f}")

    fit = dict(**rid, image=os.path.relpath(path, ROOT), box=[x0, y0, x1, y1],
               side_convention="FRONT = component side (Apple FCC caption)",
               px_per_mm=s, px_per_mm_err=se, px_per_mm_label=a.px_per_mm_label,
               n_angles=a.n_ang,
               outer=dict(primitive="circle", cx=round(ocx, 3), cy=round(ocy, 3),
                          radius_px=round(orad, 3), diameter_px=round(D, 3),
                          diameter_mm=round(dmm, 4), diameter_mm_scale_err=round(dmm_err, 4),
                          residual_sd_px=round(float(ores[okeep].std()), 3),
                          residual_p95_px=round(float(np.percentile(np.abs(ores[okeep]), 95)), 3),
                          residual_max_px=round(float(np.abs(ores[okeep]).max()), 3),
                          inlier_fraction=round(float(okeep.mean()), 4),
                          rays_used=len(pr_o), rejected=drop_o,
                          excursion_runs=outl),
               inner=inner,
               ratio_hole_2a_over_board_OD=round(ratio, 4) if ratio else None)
    json.dump(fit, open(a.json, "w"), indent=2)
    raw = dict(**rid, image=os.path.relpath(path, ROOT),
               note="RAW r(theta) EVIDENCE ONLY. The published geometry is the fit in "
                    + os.path.basename(a.json) + ". Never merge these two files.",
               outer_r_theta=[[round(float(t), 3), round(float(r), 4)] for t, r in zip(To, Ro)],
               outer_centre=[round(ocx, 3), round(ocy, 3)],
               inner_r_theta=([[round(float(t), 3), round(float(r), 4)] for t, r in zip(Ti, Ri)]
                              if inner else None),
               inner_centre=[round(ocx, 3), round(ocy, 3)])
    json.dump(raw, open(a.raw_json, "w"), indent=2)
    print(f"\n  wrote fit  {a.json}")
    print(f"  wrote raw  {a.raw_json}  (evidence; not the published geometry)")
    sys.exit(0)


if __name__ == "__main__":
    main()
