#!/usr/bin/env python3
"""p_outline.py -- extract the BOARD SILHOUETTE (outer edge + centre hole) from a
photograph, in millimetres, or refuse.

Lane L5 (BOARD BUILD), halo Replica.  Exit code IS the verdict: 0 PASS / 1 FAIL /
2 CANNOT DETERMINE.  CANNOT DETERMINE is never a soft pass.

SIDE CONVENTION: FRONT = COMPONENT SIDE (Apple's FCC caption "MLB - Front").
O'Flynn's "frontside" is this project's BACK.

WHY THIS EXISTS AND NOT A CIRCLE FIT
  Apple's centre hole is a rounded square with a notch at top centre.  A circle
  fitted to it returns a small clean residual while being the wrong shape, and a
  number that looks well-measured is worse than one that is merely imprecise.
  This tool returns a POLYGON, r(theta), and never a single "hole diameter".

CONTROLS (every one has been watched to fire -- see selftest)
  C1 clip control      -- if the segmented board touches the crop box, the box is
                          too small and every radius is a lower bound. FAIL.
  C2 bimodality        -- the luma histogram must be genuinely two-humped, or the
                          threshold is meaningless. CANNOT DETERMINE.
  C3 annotation mask   -- Apple's orange leader arrows and the diagonal watermark
                          cross the board edge. Those rays are DISCARDED and named,
                          not silently averaged in.
  C4 negative control  -- --negative runs the identical pipeline on a patch of bare
                          background. It MUST find nothing. If it finds a board,
                          the segmentation is fitting noise.
  C5 hole-is-enclosed  -- the centre hole must be a hole (enclosed by copper on all
                          sides), not a bay open to the outside.
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

PASS, FAIL, CANNOT = 0, 1, 2


def say(*a):
    print(*a, file=sys.stderr)


def luma(rgb):
    return (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2])


def otsu(vals):
    hist, _ = np.histogram(vals, bins=256, range=(0, 256))
    hist = hist.astype(float)
    tot = hist.sum()
    w0 = np.cumsum(hist)
    w1 = tot - w0
    mids = np.arange(256) + 0.5
    s0 = np.cumsum(hist * mids)
    s1 = s0[-1] - s0
    with np.errstate(invalid="ignore", divide="ignore"):
        m0 = s0 / w0
        m1 = s1 / w1
        between = w0 * w1 * (m0 - m1) ** 2
    between[~np.isfinite(between)] = -1
    t = int(np.argmax(between))
    return t, float(between[t])


def bimodality(vals, t):
    """Two-hump evidence the threshold cannot manufacture: the fraction of pixels
    living in the valley band around t. A unimodal image piles up there."""
    band = ((vals > t - 12) & (vals < t + 12)).mean()
    lo = (vals <= t - 12).mean()
    hi = (vals >= t + 12).mean()
    return float(band), float(lo), float(hi)


def boundary_polar(mask, cx, cy, n_ang, rmax):
    """For each ray, the LAST radius at which the mask is still true (outer boundary
    of the mask along that ray). Returns r in px, NaN where the ray never hits."""
    th = np.deg2rad(np.arange(n_ang) * 360.0 / n_ang)
    rr = np.arange(1.0, rmax, 0.25)
    R, T = np.meshgrid(rr, th)
    xs = np.rint(cx + R * np.cos(T)).astype(int)
    ys = np.rint(cy - R * np.sin(T)).astype(int)
    ok = (xs >= 0) & (ys >= 0) & (xs < mask.shape[1]) & (ys < mask.shape[0])
    hit = np.zeros_like(R, dtype=bool)
    hit[ok] = mask[ys[ok], xs[ok]]
    out = np.full(n_ang, np.nan)
    for i in range(n_ang):
        idx = np.nonzero(hit[i])[0]
        if idx.size:
            out[i] = rr[idx[-1]]
    return np.rad2deg(th), out


def inner_polar(hole, cx, cy, n_ang, rmax):
    """For each ray, the FIRST radius at which we LEAVE the hole (hole boundary)."""
    th = np.deg2rad(np.arange(n_ang) * 360.0 / n_ang)
    rr = np.arange(1.0, rmax, 0.25)
    R, T = np.meshgrid(rr, th)
    xs = np.rint(cx + R * np.cos(T)).astype(int)
    ys = np.rint(cy - R * np.sin(T)).astype(int)
    ok = (xs >= 0) & (ys >= 0) & (xs < hole.shape[1]) & (ys < hole.shape[0])
    inh = np.zeros_like(R, dtype=bool)
    inh[ok] = hole[ys[ok], xs[ok]]
    out = np.full(n_ang, np.nan)
    for i in range(n_ang):
        idx = np.nonzero(~inh[i])[0]
        if idx.size:
            out[i] = rr[idx[0]]
    return np.rad2deg(th), out


def run(img_path, box, px_per_mm, n_ang, negative, json_out, scale_basis, scale_note):
    say("INPUT")
    say(f"  image        {img_path}")
    say(f"  crop box     {box}")
    say(f"  px_per_mm    {px_per_mm}   basis: {scale_basis}")
    say(f"  n_angles     {n_ang}")
    say(f"  mode         {'NEGATIVE CONTROL (must find nothing)' if negative else 'measure'}")
    say("")

    im = Image.open(img_path).convert("RGB")
    rgb = np.asarray(im.crop(box)).astype(float)
    L = luma(rgb)
    H, W = L.shape

    # C3 annotation mask: Apple's orange leader arrows + the pale-orange watermark.
    orange = (rgb[..., 0] - rgb[..., 2] > 35) & (rgb[..., 0] > 110)
    orange = ndimage.binary_dilation(orange, iterations=2)
    say(f"C3 annotation mask: {orange.mean()*100:.2f}% of the crop is orange annotation")

    # C2 bimodality
    t, sep = otsu(L)
    band, lo, hi = bimodality(L, t)
    say(f"C2 otsu t={t} between-var={sep:.0f} valley_frac={band:.4f} dark={lo:.4f} light={hi:.4f}")
    verdicts = []
    if band > 0.20 or lo < 0.01 or hi < 0.01:
        say("C2 FIRED: luma histogram is not two-humped at this threshold.")
        if negative:
            say("NEGATIVE CONTROL PASSED: no board found in bare background.")
            return PASS, None
        return CANNOT, None

    dark = (L < t) & ~orange
    dark = ndimage.binary_opening(dark, np.ones((3, 3)), iterations=1)
    lab, n = ndimage.label(dark)
    if n == 0:
        say("no dark component at all")
        if negative:
            say("NEGATIVE CONTROL PASSED: no board found in bare background.")
            return PASS, None
        return CANNOT, None
    sizes = ndimage.sum(dark, lab, range(1, n + 1))
    k = int(np.argmax(sizes)) + 1
    board = lab == k
    frac = board.mean()
    say(f"largest dark component = {sizes[k-1]:.0f} px, {frac*100:.1f}% of crop, of {n} components")

    if negative:
        if frac > 0.05:
            say(f"NEGATIVE CONTROL FAILED: found a {frac*100:.1f}% blob in bare background.")
            return FAIL, None
        say("NEGATIVE CONTROL PASSED: no board-sized blob in bare background.")
        return PASS, None

    if frac < 0.02:
        say("largest component is too small to be a board")
        return CANNOT, None

    filled = ndimage.binary_fill_holes(board)

    # C1 clip control
    touch = []
    if filled[0, :].any(): touch.append("top")
    if filled[-1, :].any(): touch.append("bottom")
    if filled[:, 0].any(): touch.append("left")
    if filled[:, -1].any(): touch.append("right")
    if touch:
        say(f"C1 FIRED: the board touches the crop box on {touch}. Every radius is a "
            f"lower bound. Widen --box.")
        return FAIL, None
    say("C1 clip control: board is fully interior to the crop box.")

    cy, cx = ndimage.center_of_mass(filled)
    say(f"centroid of filled silhouette: ({cx:.2f}, {cy:.2f}) px in crop")

    # holes
    holes = filled & ~board
    holes = ndimage.binary_opening(holes, np.ones((3, 3)))
    hl, hn = ndimage.label(holes)
    if hn == 0:
        say("C5 FIRED: no enclosed hole. This is a solid disc, not an annulus.")
        return FAIL, None
    hsz = ndimage.sum(holes, hl, range(1, hn + 1))
    hk = int(np.argmax(hsz)) + 1
    hole = hl == hk
    say(f"C5 centre hole: {hsz[hk-1]:.0f} px, enclosed, of {hn} enclosed holes")
    hcy, hcx = ndimage.center_of_mass(hole)
    say(f"hole centroid: ({hcx:.2f}, {hcy:.2f}) px -- offset from board centroid "
        f"({hcx-cx:+.2f}, {hcy-cy:+.2f}) px = ({(hcx-cx)/px_per_mm:+.3f}, "
        f"{(hcy-cy)/px_per_mm:+.3f}) mm")

    rmax = max(H, W)
    th, r_out = boundary_polar(filled, cx, cy, n_ang, rmax)
    _, r_in = inner_polar(hole, cx, cy, n_ang, rmax)

    # which rays crossed annotation near the edge -> DISCARD and name them
    disc_out, disc_in = [], []
    for i in range(n_ang):
        a = math.radians(th[i])
        for r, lst in ((r_out[i], disc_out), (r_in[i], disc_in)):
            if not np.isfinite(r):
                lst.append(float(th[i])); continue
            xs = np.rint(cx + np.arange(r - 6, r + 7) * math.cos(a)).astype(int)
            ys = np.rint(cy - np.arange(r - 6, r + 7) * math.sin(a)).astype(int)
            ok = (xs >= 0) & (ys >= 0) & (xs < W) & (ys < H)
            if ok.any() and orange[ys[ok], xs[ok]].mean() > 0.25:
                lst.append(float(th[i]))
    say(f"C3 discarded {len(disc_out)}/{n_ang} outer rays and {len(disc_in)}/{n_ang} "
        f"inner rays crossing annotation or missing")

    keep_o = np.array([th[i] not in disc_out for i in range(n_ang)])
    keep_i = np.array([th[i] not in disc_in for i in range(n_ang)])
    ro_mm = r_out / px_per_mm
    ri_mm = r_in / px_per_mm

    def stats(v, keep):
        w = v[keep & np.isfinite(v)]
        return dict(n=int(w.size), mean=float(w.mean()), sd=float(w.std()),
                    min=float(w.min()), max=float(w.max()),
                    p5=float(np.percentile(w, 5)), p95=float(np.percentile(w, 95)))

    so, si = stats(ro_mm, keep_o), stats(ri_mm, keep_i)
    say("")
    say(f"OUTER r  mean {so['mean']:.3f} mm  sd {so['sd']:.3f}  min {so['min']:.3f}  "
        f"max {so['max']:.3f}   -> diameter about {2*so['mean']:.3f} mm")
    say(f"INNER r  mean {si['mean']:.3f} mm  sd {si['sd']:.3f}  min {si['min']:.3f}  "
        f"max {si['max']:.3f}   (NOT a diameter -- the hole is not round)")
    say(f"hole roundness r_max/r_min = {si['max']/si['min']:.3f}  "
        f"(1.000 = circle, 1.414 = square)")
    say(f"RATIOS, which do NOT inherit the scale: "
        f"inner_mean/outer_mean = {si['mean']/so['mean']:.4f}, "
        f"annulus width mean = {so['mean']-si['mean']:.3f} mm")

    doc = dict(
        tool="p_outline.py", lane="L5 BOARD BUILD",
        side_convention="FRONT = component side (Apple FCC 'MLB - Front'); "
                        "O'Flynn 'frontside' is this project's BACK",
        image=img_path, crop_box=list(box), n_angles=n_ang,
        scale=dict(px_per_mm=px_per_mm, basis=scale_basis, note=scale_note),
        method="otsu on luma, orange-annotation mask, largest dark component, "
               "fill-holes for the outer silhouette, largest enclosed hole for the "
               "centre. NO circle is fitted to anything.",
        centre_px_in_crop=[float(cx), float(cy)],
        hole_centroid_px_in_crop=[float(hcx), float(hcy)],
        hole_offset_mm=[float((hcx - cx) / px_per_mm), float((cy - hcy) / px_per_mm)],
        outer=dict(stats_mm=so,
                   r_theta_deg_mm=[[float(th[i]), float(ro_mm[i])]
                                   for i in range(n_ang)
                                   if keep_o[i] and np.isfinite(ro_mm[i])]),
        inner=dict(stats_mm=si, roundness_rmax_over_rmin=float(si["max"] / si["min"]),
                   note="the centre hole is a rounded square with a notch at top "
                        "centre. There is no 'hole diameter'.",
                   r_theta_deg_mm=[[float(th[i]), float(ri_mm[i])]
                                   for i in range(n_ang)
                                   if keep_i[i] and np.isfinite(ri_mm[i])]),
        discarded=dict(outer_rays_deg=disc_out, inner_rays_deg=disc_in,
                       reason="ray crossed an orange leader arrow / watermark, or "
                              "never met the boundary"),
        controls=dict(C1_clip="PASS - silhouette interior to crop box",
                      C2_bimodality=dict(otsu_t=t, valley_frac=band, dark=lo, light=hi),
                      C3_annotation_mask_frac=float(orange.mean()),
                      C5_hole_enclosed=True),
    )
    if json_out:
        os.makedirs(os.path.dirname(json_out) or ".", exist_ok=True)
        with open(json_out, "w") as f:
            json.dump(doc, f, indent=2)
        say(f"\nwrote {json_out}")
    return PASS, doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--box", nargs=4, type=int, required=True, metavar=("X0","Y0","X1","Y1"))
    ap.add_argument("--px-per-mm", type=float, required=True)
    ap.add_argument("--scale-basis", default="UNSTATED")
    ap.add_argument("--scale-note", default="")
    ap.add_argument("--n-angles", type=int, default=1440)
    ap.add_argument("--negative", action="store_true",
                    help="negative control: run on a bare-background patch, must find nothing")
    ap.add_argument("--json-out")
    a = ap.parse_args()
    if a.scale_basis == "UNSTATED":
        say("REFUSED: --scale-basis is required. A number without its input is not a "
            "measurement.")
        sys.exit(CANNOT)
    code, _ = run(a.image, tuple(a.box), a.px_per_mm, a.n_angles, a.negative,
                  a.json_out, a.scale_basis, a.scale_note)
    say({0: "PASS", 1: "FAIL", 2: "CANNOT DETERMINE"}[code])
    sys.exit(code)


if __name__ == "__main__":
    main()
