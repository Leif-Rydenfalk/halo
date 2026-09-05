#!/usr/bin/env python3
"""b_pkgsize.py — measure a component package off a photograph, or refuse.

Exit code IS the verdict: 0 PASS, 1 FAIL, 2 CANNOT DETERMINE.

The method, stated so a reader can attack it:
  1. inside a caller-given box, build a CHANNEL (luminance by default, or a
     colour difference such as blue-minus-red), threshold it (Otsu) and keep
     either the bright side or the dark side, as the caller says. The colour
     channels exist because the thing this tool most needs to isolate — a
     dark blue silicon package on a dark maroon PCB — has almost NO luminance
     contrast at all, and a luminance threshold merges the two;
  2. keep the LARGEST connected component, so a neighbouring part cannot join
     the measurement;
  3. the MINIMUM-AREA rotated rectangle of the component's convex hull gives
     the package's own axes and extents. PCA was tried first and is WRONG for
     a square: the covariance is degenerate, the axes come out arbitrary, and
     a 150x150 test square came back 206x206. That failure is selftest case 2
     and it is why rotating calipers are used instead;
  4. report the two side lengths of that rectangle.

What it does NOT do: it does not know millimetres. It returns PIXELS. A caller
converts with `--px-per-mm`, and the ONLY honest source of that number in these
photographs is a part whose body size a datasheet publishes — name it in
`--ruler-note` and it is printed with every result.

Negative controls, all exercised by --self-test:
  * a blank box yields no component -> CANNOT DETERMINE, never a zero size
  * a component touching the box edge is REFUSED: the box clipped the part, so
    the extent measured is the box's, not the package's
  * a component that fills almost the whole box is refused for the same reason
  * a box with no bimodal separation (flat, or all one material) is refused:
    Otsu will always return SOME threshold, and on a flat box it returned 0.5
    and reported the whole box as a 200x200 part. The separability of the two
    classes must beat a floor before any extent is reported.

Usage:
  b_pkgsize.py IMG --box X0 Y0 X1 Y1 --pick dark|bright [--px-per-mm F]
               [--label NAME] [--ruler-note TEXT] [--json-out F]
               [--pad-sweep [--pads 0,20,40,60]] [--overlay-png F]
  b_pkgsize.py --self-test
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import ConvexHull


def otsu(v):
    hist, edges = np.histogram(v, bins=256, range=(0, 255))
    total = hist.sum()
    if total == 0:
        return None
    w0 = np.cumsum(hist)
    w1 = total - w0
    centres = (edges[:-1] + edges[1:]) / 2
    s0 = np.cumsum(hist * centres)
    s1 = s0[-1] - s0
    with np.errstate(invalid="ignore", divide="ignore"):
        m0, m1 = s0 / w0, s1 / w1
        between = w0 * w1 * (m0 - m1) ** 2
    between[~np.isfinite(between)] = -1
    k = int(np.argmax(between))
    var_total = float(((centres - (s0[-1] / total)) ** 2 * hist).sum() / total)
    eta = float(between[k] / total ** 2 / var_total) if var_total > 1e-9 else 0.0
    return float(centres[k]), eta


def min_area_rect(xs, ys):
    """Side lengths and angle of the minimum-area rotated rectangle."""
    pts = np.stack([xs, ys], axis=1).astype(float)
    if len(pts) < 3:
        return None
    try:
        hull = pts[ConvexHull(pts).vertices]
    except Exception:
        return None
    best = None
    n = len(hull)
    for i in range(n):
        e = hull[(i + 1) % n] - hull[i]
        L = math.hypot(*e)
        if L < 1e-9:
            continue
        u = e / L
        v = np.array([-u[1], u[0]])
        a = hull @ u
        b = hull @ v
        w, h = a.max() - a.min() + 1.0, b.max() - b.min() + 1.0
        if best is None or w * h < best[0]:
            best = (w * h, w, h, math.degrees(math.atan2(u[1], u[0])))
    if best is None:
        return None
    _, w, h, ang = best
    return (max(w, h), min(w, h), ang if w >= h else ang + 90.0)


MIN_SEPARABILITY = 0.55
MIN_RECTANGULARITY = 0.60   # see selftest case 6


def measure(arr, pick):
    """arr: HxW uint8 luminance of the BOX ONLY. Returns dict or None."""
    if float(arr.std()) < 2.0:
        return None
    got = otsu(arr.astype(float).ravel())
    if got is None:
        return None
    t, eta = got
    if eta < MIN_SEPARABILITY:
        return None
    mask = arr > t if pick == "bright" else arr < t
    if mask.sum() < 25:
        return None
    lab, n = ndimage.label(mask)
    if n == 0:
        return None
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    keep = int(np.argmax(sizes)) + 1
    m = lab == keep
    ys, xs = np.nonzero(m)
    rect = min_area_rect(xs, ys)
    if rect is None:
        return None
    long_px, short_px, ang = rect
    H, W = arr.shape
    touches = (xs.min() == 0) or (ys.min() == 0) or (xs.max() == W - 1) or (ys.max() == H - 1)
    fill = float(m.sum()) / (H * W)
    rect_fill = float(m.sum()) / (long_px * short_px)
    if rect_fill < MIN_RECTANGULARITY:
        return None
    return {"threshold": round(t, 1), "separability": round(eta, 3),
            "pixels": int(m.sum()),
            "long_px": float(long_px), "short_px": float(short_px),
            "angle_deg": round(float(ang), 1),
            "touches_box_edge": bool(touches), "box_fill_fraction": round(fill, 3),
            "rectangularity": round(float(m.sum()) / (long_px * short_px), 3),
            "components_found": int(n)}


def measure_at(arr, pick, t):
    """The same extraction as measure(), at a CALLER-GIVEN threshold.

    Split out because the threshold is the second arbitrary parameter in this
    tool (the box is the first), and E07 s11's rule is to sweep an arbitrary
    parameter rather than trust one value of it.
    """
    mask = arr > t if pick == "bright" else arr < t
    if mask.sum() < 25:
        return None
    lab, n = ndimage.label(mask)
    if n == 0:
        return None
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    m = lab == (int(np.argmax(sizes)) + 1)
    ys, xs = np.nonzero(m)
    rect = min_area_rect(xs, ys)
    if rect is None:
        return None
    H, W = arr.shape
    return {"threshold": round(float(t), 2), "long_px": rect[0],
            "short_px": rect[1], "angle_deg": round(float(rect[2]), 1),
            "pixels": int(m.sum()),
            "touches_box_edge": bool(xs.min() == 0 or ys.min() == 0 or
                                     xs.max() == W - 1 or ys.max() == H - 1),
            "rectangularity": round(float(m.sum()) / (rect[0] * rect[1]), 3)}


def half_max(arr, pick, t_otsu, erode=6):
    """Re-measure at the 50 % crossing between the part and its background.

    WHY THIS EXISTS, measured 2026-09-05 (L8): Otsu picks the threshold that
    maximises between-class variance, which is NOT the midpoint between the two
    materials whenever the classes are unequally sized. On a photograph whose
    edges are several pixels wide, a threshold off the midpoint moves the
    extracted boundary OUTWARD or INWARD by a fixed number of pixels PER SIDE -
    an ADDITIVE error that looks like a small percentage on a big part and a
    large one on a small part.

    The nRF52832-CIAA is the case that showed it. Its published body is
    2.956 x 3.226 mm (Nordic PS v1.4 Table 132 p.541). At the registration scale
    106.313 px/mm it should image 342.97 x 314.26 px; Otsu returns
    355.10 x 326.60 px. The excess is +12.13 and +12.34 px - agreeing to 1.7 % in
    PIXELS and only to 10.4 % in PERCENT. A scale error is multiplicative and
    would agree in percent. This one is additive, so it is the outline, not the
    ruler.

    The 50 % crossing is the project's standing answer to this (E07's closing
    note: a gradient PEAK carried 4.21 px of bias on a synthetic step, the 50 %
    crossing 0.05 px). Foreground and background means are taken well inside and
    well outside the Otsu blob, so the soft transition itself is excluded from
    both.
    """
    m0 = arr > t_otsu if pick == "bright" else arr < t_otsu
    lab, n = ndimage.label(m0)
    if n == 0:
        return None
    sizes = ndimage.sum(m0, lab, range(1, n + 1))
    core = lab == (int(np.argmax(sizes)) + 1)
    inner = ndimage.binary_erosion(core, iterations=erode)
    outer = ~ndimage.binary_dilation(core, iterations=erode)
    if inner.sum() < 50 or outer.sum() < 50:
        return None
    fg = float(arr[inner].mean())
    bg = float(arr[outer].mean())
    t50 = (fg + bg) / 2.0
    r = measure_at(arr, pick, t50)
    if r is None:
        return None
    r.update({"fg_mean": round(fg, 2), "bg_mean": round(bg, 2),
              "t50": round(t50, 2), "t_otsu": round(float(t_otsu), 2),
              "otsu_offset_from_midpoint": round(float(t_otsu) - t50, 2),
              "contrast": round(abs(fg - bg), 2)})
    return r


def robust_extent(arr, pick, t, min_bin=3):
    """Median cross-section of the kept component, in its own rotated frame.

    WHY, measured 2026-09-05 (L8): the minimum-area rectangle is set by the
    EXTREME points of the blob, so anything that protrudes at a corner sets the
    size. X1 (T320/RBEV) is soldered on four pads that stick out past the
    package on all four corners and merge with it at this threshold: the
    min-area rectangle reads 262.2 x 211.5 px at rectangularity 0.748, and
    262.2 px is the pad-to-pad span, not the package. X2 (A048L) has no visible
    protruding fillets and reads at rectangularity 0.802 - so comparing the two
    parts' aspect ratios from min-area rectangles is NOT like for like, and the
    Catley test turns on exactly that comparison.

    A median does not care about four corners. For each 1-px slice across the
    blob's own long axis, take the extent along the short axis; the median over
    all slices is the body width. Symmetrically for the length. On a clean
    rectangle the medians equal the extents, which is the selftest's negative
    control: this estimator must not shrink a part that has nothing sticking out.

    Reports both, plus the fraction by which the min-area rectangle exceeds the
    medians - which is a direct, per-part measure of how much of the "size" is
    protrusion.

    THE LIMIT, and it is real: a median recovers the body only while the
    protruding slices are FEWER THAN HALF of the slices on that axis. Selftest
    case 15b is a deliberate case where they are not - four tabs each half the
    body height - and there the median equals the rectangle and this estimator
    CANNOT see the protrusion. The 25th percentile can, and both are reported;
    when they disagree, the protrusion is large and the p25 is the body. Neither
    is silently preferred, because choosing the statistic after seeing which
    answer it gives is E07 s17.
    """
    mask = arr > t if pick == "bright" else arr < t
    lab, n = ndimage.label(mask)
    if n == 0:
        return None
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    m = lab == (int(np.argmax(sizes)) + 1)
    ys, xs = np.nonzero(m)
    rect = min_area_rect(xs, ys)
    if rect is None:
        return None
    long_px, short_px, ang = rect
    a = math.radians(ang)
    u = xs * math.cos(a) + ys * math.sin(a)
    v = -xs * math.sin(a) + ys * math.cos(a)

    def med_extent(along, across):
        keys = np.round(along).astype(int)
        order = np.argsort(keys)
        keys, vals = keys[order], across[order]
        bounds = np.searchsorted(keys, np.unique(keys), side="left")
        bounds = np.append(bounds, len(keys))
        widths = []
        for i in range(len(bounds) - 1):
            seg = vals[bounds[i]:bounds[i + 1]]
            if len(seg) >= min_bin:
                widths.append(seg.max() - seg.min() + 1.0)
        if not widths:
            return None, None, 0
        return (float(np.median(widths)),
                float(np.percentile(widths, 25)), len(widths))

    med_short, p25_short, n_long_bins = med_extent(u, v)
    med_long, p25_long, n_short_bins = med_extent(v, u)
    if med_short is None or med_long is None:
        return None
    return {"threshold": round(float(t), 2),
            "rect_long_px": long_px, "rect_short_px": short_px,
            "median_long_px": round(med_long, 1),
            "median_short_px": round(med_short, 1),
            "p25_long_px": round(p25_long, 1),
            "p25_short_px": round(p25_short, 1),
            "median_aspect": round(med_long / med_short, 3),
            "p25_aspect": round(p25_long / p25_short, 3),
            "rect_aspect": round(long_px / short_px, 3),
            "median_vs_p25_long_frac": round(med_long / p25_long - 1.0, 4),
            "median_vs_p25_short_frac": round(med_short / p25_short - 1.0, 4),
            "protrusion_long_frac": round(long_px / med_long - 1.0, 4),
            "protrusion_short_frac": round(short_px / med_short - 1.0, 4),
            "n_slices_long": n_long_bins, "n_slices_short": n_short_bins}


def thr_sweep(arr, pick, t_otsu, n=9, span=0.6):
    """Extent as a function of the threshold, across the part/background gap.

    The companion to the box sweep: the threshold is the tool's OTHER arbitrary
    parameter. If the extent barely moves across the whole gap, the edge is
    sharp and any disagreement with another method is about WHICH PIXELS each
    method calls the part, not about where the threshold sat. If it moves a lot,
    the size is a threshold choice and must be reported as such.
    """
    hm = half_max(arr, pick, t_otsu)
    if hm is None:
        return None
    fg, bg = hm["fg_mean"], hm["bg_mean"]
    lo, hi = (min(fg, bg), max(fg, bg))
    mid = (lo + hi) / 2.0
    half = (hi - lo) / 2.0 * span
    rows = []
    for t in np.linspace(mid - half, mid + half, n):
        r = measure_at(arr, pick, float(t))
        rows.append({"t": round(float(t), 2),
                     "long_px": None if r is None else r["long_px"],
                     "short_px": None if r is None else r["short_px"],
                     "clipped": None if r is None else r["touches_box_edge"]})
    ok = [r for r in rows if r["long_px"] is not None and not r["clipped"]]
    out = {"rows": rows, "t50": hm["t50"], "contrast": hm["contrast"],
           "span_frac_of_contrast": span, "n_usable": len(ok)}
    if len(ok) >= 2:
        for axis in ("long_px", "short_px"):
            v = np.array([r[axis] for r in ok], float)
            out[axis] = {"min": float(v.min()), "max": float(v.max()),
                         "range_px": round(float(v.max() - v.min()), 1),
                         "px_per_luma": round(float(v.max() - v.min()) /
                                              max(1e-9, (ok[-1]["t"] - ok[0]["t"])), 2)}
    return out


def channel(rgb, name):
    r, g, b = (rgb[..., i].astype(float) for i in range(3))
    if name == "lum":
        return np.clip(0.299 * r + 0.587 * g + 0.114 * b, 0, 255).astype(np.uint8)
    if name == "b-r":
        return np.clip((b - r) + 128, 0, 255).astype(np.uint8)
    if name == "r-b":
        return np.clip((r - b) + 128, 0, 255).astype(np.uint8)
    raise ValueError(name)


PAD_TOL = 0.05          # 5 % — an axis that moves more than this with the box
                        # is reporting the box, not the part (E07 section 11)


def pad_sweep(im, box, pick, chan, pads):
    """Re-measure the SAME part with the box grown by each pad, and report how
    much the answer moves.

    E07 section 11: L1's third dark-package attempt padded its ROI 0/20/40/60 px
    and got 3.35 / 3.98 / 4.09 / 4.50 mm for one package -- a 34 % swing driven
    entirely by the operator's choice of box. A single run cannot see that. The
    general test is to sweep the arbitrary parameter and watch whether the answer
    moves with it, so this is not optional on any real photograph.

    Returns (rows, summary). An axis whose spread exceeds PAD_TOL is
    ROI-DEPENDENT and its millimetres are CANNOT DETERMINE, no matter how
    confident the single run looked.
    """
    W, H = im.size
    x0, y0, x1, y1 = box
    rows = []
    for pad in pads:
        bx = (max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad))
        arr = channel(np.asarray(im.crop(bx)), chan)
        r = measure(arr, pick)
        rows.append({"pad": pad, "box": list(bx),
                     "clamped": bx != (x0 - pad, y0 - pad, x1 + pad, y1 + pad),
                     "result": None if r is None else
                     {k: r[k] for k in ("long_px", "short_px", "angle_deg",
                                        "threshold", "separability",
                                        "rectangularity", "pixels",
                                        "touches_box_edge")}})
    ok = [r for r in rows if r["result"] is not None and
          not r["result"]["touches_box_edge"]]
    summary = {"n_pads": len(rows), "n_usable": len(ok),
               "pads": list(pads)}
    if len(ok) < 2:
        summary["verdict"] = "CANNOT DETERMINE"
        summary["reason"] = (f"only {len(ok)} of {len(rows)} paddings produced an "
                             "unclipped measurement, so the sweep has nothing to "
                             "compare and box-dependence is UNTESTED")
        return rows, summary
    for axis in ("long_px", "short_px"):
        v = np.array([r["result"][axis] for r in ok], float)
        med = float(np.median(v))
        spread = float(v.max() - v.min()) / med if med > 0 else float("inf")
        summary[axis] = {"min": float(v.min()), "max": float(v.max()),
                         "median": med, "spread_frac": round(spread, 4),
                         "stable": bool(spread <= PAD_TOL)}
    a = np.array([r["result"]["long_px"] / r["result"]["short_px"] for r in ok])
    summary["aspect"] = {"min": round(float(a.min()), 3),
                         "max": round(float(a.max()), 3),
                         "median": round(float(np.median(a)), 3),
                         "spread_frac": round(float(a.max() - a.min()) /
                                              float(np.median(a)), 4)}
    both = summary["long_px"]["stable"] and summary["short_px"]["stable"]
    summary["verdict"] = "STABLE" if both else "ROI-DEPENDENT"
    summary["tolerance"] = PAD_TOL
    return rows, summary


def overlay(im, box, pick, chan, out_png, scale=2.0):
    """Draw the kept component and its min-area rectangle back onto the crop.

    Leif's rule: LOOK at it. A rectangularity of 0.97 is not a picture of what
    was actually segmented, and every wrong answer in this project so far was
    caught by drawing the thing back onto the photograph.
    """
    from PIL import ImageDraw
    x0, y0, x1, y1 = box
    crop = im.crop(box)
    arr = channel(np.asarray(crop), chan)
    if float(arr.std()) < 2.0:
        return None
    got = otsu(arr.astype(float).ravel())
    if got is None:
        return None
    t, _ = got
    mask = arr > t if pick == "bright" else arr < t
    lab, n = ndimage.label(mask)
    if n == 0:
        return None
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    m = lab == (int(np.argmax(sizes)) + 1)
    edge = m & ~ndimage.binary_erosion(m)
    big = crop.resize((int(crop.width * scale), int(crop.height * scale)),
                      Image.NEAREST)
    px = big.load()
    ys, xs = np.nonzero(edge)
    for yy, xx in zip(ys, xs):
        for dy in range(int(scale)):
            for dx in range(int(scale)):
                px[int(xx * scale) + dx, int(yy * scale) + dy] = (0, 255, 0)
    d = ImageDraw.Draw(big)
    d.text((3, 3), f"box {x0},{y0},{x1},{y1}  {chan}/{pick}  thr {t:.0f}",
           fill=(255, 255, 0))
    big.save(out_png)
    return out_png


def run(args):
    im = Image.open(args.image).convert("RGB")
    x0, y0, x1, y1 = args.box
    arr = channel(np.asarray(im.crop((x0, y0, x1, y1))), args.channel)
    print(f"b_pkgsize  input: {args.image}  box [{x0}:{x1},{y0}:{y1}] "
          f"({x1-x0}x{y1-y0} px)  channel={args.channel} pick={args.pick}")
    if args.label:
        print(f"  label: {args.label}")
    r = measure(arr, args.pick)
    if r is None:
        print("  CANNOT DETERMINE — no component in this box that behaves like a "
              "package: either the box is flat, the two classes do not separate, "
              f"or the largest component fills under {MIN_RECTANGULARITY:.0%} of "
              "its own bounding rectangle (which is what thresholded texture "
              "looks like, not a part).")
        return 2
    print(f"  otsu threshold {r['threshold']} (separability {r['separability']}), "
          f"{r['components_found']} components, largest {r['pixels']} px, "
          f"rectangularity {r['rectangularity']}")
    print(f"  oriented extent: {r['long_px']:.1f} x {r['short_px']:.1f} px "
          f"at {r['angle_deg']:.1f} deg")
    if r["touches_box_edge"]:
        print("  FAIL — the component touches the box edge, so the box clipped "
              "the part and this extent is the BOX's, not the package's. "
              "Widen --box and re-run.")
        return 1
    if r["box_fill_fraction"] > 0.85:
        print(f"  FAIL — the component fills {r['box_fill_fraction']:.0%} of the "
              "box; there is no background left to define an edge against.")
        return 1
    if getattr(args, "half_max", False):
        hm = half_max(arr, args.pick, r["threshold"])
        if hm is None:
            print("  half-max: CANNOT DETERMINE — no clean interior/exterior to "
                  "take the two class means from")
        else:
            print(f"  --- 50 % crossing (Otsu is not the midpoint) ---")
            print(f"    part {hm['fg_mean']:.1f}  background {hm['bg_mean']:.1f}  "
                  f"contrast {hm['contrast']:.1f}  ->  t50 {hm['t50']:.1f}, "
                  f"Otsu {hm['t_otsu']:.1f} "
                  f"({hm['otsu_offset_from_midpoint']:+.1f} off midpoint)")
            print(f"    extent at t50: {hm['long_px']:.1f} x {hm['short_px']:.1f} px"
                  f"   (Otsu gave {r['long_px']:.1f} x {r['short_px']:.1f}, "
                  f"difference {hm['long_px']-r['long_px']:+.1f} / "
                  f"{hm['short_px']-r['short_px']:+.1f} px)")
            if hm["touches_box_edge"]:
                print("    NOTE the t50 blob touches the box edge; widen --box "
                      "before using this number")
            r["half_max"] = hm
    if getattr(args, "robust", False):
        rb = robust_extent(arr, args.pick, r["threshold"])
        if rb is None:
            print("  robust extent: CANNOT DETERMINE")
        else:
            print("  --- median cross-section (min-area rect is set by extremes) ---")
            print(f"    median {rb['median_long_px']:.1f} x "
                  f"{rb['median_short_px']:.1f} px, aspect {rb['median_aspect']} "
                  f"({rb['n_slices_long']} / {rb['n_slices_short']} slices)")
            print(f"    p25    {rb['p25_long_px']:.1f} x "
                  f"{rb['p25_short_px']:.1f} px, aspect {rb['p25_aspect']}")
            if (abs(rb["median_vs_p25_long_frac"]) > 0.03 or
                    abs(rb["median_vs_p25_short_frac"]) > 0.03):
                print(f"    median and p25 DISAGREE "
                      f"({rb['median_vs_p25_long_frac']*100:+.1f}% long, "
                      f"{rb['median_vs_p25_short_frac']*100:+.1f}% short): the "
                      "protrusion covers a large share of the slices, so the "
                      "median may be carrying it. Report both.")
            print(f"    min-area rect exceeds the medians by "
                  f"{rb['protrusion_long_frac']*100:+.1f}% long, "
                  f"{rb['protrusion_short_frac']*100:+.1f}% short "
                  f"— that excess IS the protrusion (solder fillets, pads)")
            r["robust"] = rb
    if getattr(args, "thr_sweep", False):
        ts = thr_sweep(arr, args.pick, r["threshold"])
        if ts is None:
            print("  threshold sweep: CANNOT DETERMINE")
        else:
            print("  --- threshold sweep (the OTHER arbitrary parameter) ---")
            for row in ts["rows"]:
                if row["long_px"] is None:
                    print(f"    t {row['t']:6.1f}: nothing")
                else:
                    print(f"    t {row['t']:6.1f}: {row['long_px']:7.1f} x "
                          f"{row['short_px']:6.1f} px"
                          + ("  CLIPPED" if row["clipped"] else ""))
            if "long_px" in ts:
                print(f"    across the middle {ts['span_frac_of_contrast']:.0%} of a "
                      f"{ts['contrast']:.1f}-unit contrast the long axis moves "
                      f"{ts['long_px']['range_px']} px "
                      f"({ts['long_px']['px_per_luma']} px per luma unit), the "
                      f"short axis {ts['short_px']['range_px']} px")
            r["thr_sweep"] = ts
    sweep = None
    if getattr(args, "pad_sweep", False):
        pads = [int(v) for v in args.pads.split(",")]
        rows, sweep = pad_sweep(im, (x0, y0, x1, y1), args.pick, args.channel, pads)
        print("  --- ROI padding sweep (E07 s11: does the answer track the box?) ---")
        for row in rows:
            rr = row["result"]
            if rr is None:
                print(f"    pad {row['pad']:>3}: CANNOT DETERMINE (no package-like "
                      "component in this box)")
            elif rr["touches_box_edge"]:
                print(f"    pad {row['pad']:>3}: {rr['long_px']:7.1f} x "
                      f"{rr['short_px']:6.1f} px  CLIPPED (touches box edge) - "
                      "excluded from the spread")
            else:
                print(f"    pad {row['pad']:>3}: {rr['long_px']:7.1f} x "
                      f"{rr['short_px']:6.1f} px  thr {rr['threshold']:5.1f}  "
                      f"rect {rr['rectangularity']:.3f}  {rr['pixels']:>7} px")
        if sweep["n_usable"] < 2:
            print(f"    SWEEP CANNOT DETERMINE - {sweep['reason']}")
        else:
            for axis, name in (("long_px", "long "), ("short_px", "short")):
                a = sweep[axis]
                print(f"    {name} spread {a['spread_frac']*100:5.2f}% "
                      f"({a['min']:.1f}-{a['max']:.1f} px, median {a['median']:.1f})"
                      f"  {'STABLE' if a['stable'] else 'ROI-DEPENDENT'}")
            print(f"    aspect {sweep['aspect']['min']}-{sweep['aspect']['max']} "
                  f"(spread {sweep['aspect']['spread_frac']*100:.2f}%)")
            print(f"    SWEEP VERDICT: {sweep['verdict']} "
                  f"(tolerance {sweep['tolerance']*100:.0f}%)")
        r["pad_sweep"] = {"rows": rows, "summary": sweep}
    if args.overlay_png:
        got = overlay(im, (x0, y0, x1, y1), args.pick, args.channel,
                      args.overlay_png)
        print(f"  overlay: {got or 'NOT WRITTEN - nothing segmented'}")
    if args.px_per_mm:
        f = args.px_per_mm
        r["px_per_mm"] = f
        r["long_mm"] = round(r["long_px"] / f, 3)
        r["short_mm"] = round(r["short_px"] / f, 3)
        print(f"  -> {r['long_mm']:.3f} x {r['short_mm']:.3f} mm "
              f"at {f:.4f} px/mm")
        print(f"  RULER: {args.ruler_note or 'NOT STATED — this number has no basis'}")
        if not args.ruler_note:
            print("  FAIL — a millimetre with no stated ruler is not a measurement.")
            return 1
    else:
        print("  no --px-per-mm given: PIXELS ONLY. Ratios are usable, "
              "millimetres are not.")
    r["aspect"] = round(r["long_px"] / r["short_px"], 3)
    print(f"  aspect (long/short): {r['aspect']}")
    if args.json_out:
        r["input"] = {"image": args.image, "box": args.box, "pick": args.pick,
                      "channel": args.channel,
                      "label": args.label, "ruler_note": args.ruler_note}
        json.dump(r, open(args.json_out, "w"), indent=2)
        print(f"  wrote {args.json_out}")
    if sweep is not None and sweep["verdict"] != "STABLE":
        print("  CANNOT DETERMINE — the extent moves with the box, so it is a "
              "measurement of the operator's ROI and not of the part. The "
              "single-run number above is NOT a size. Aspect may still be usable "
              "if its own spread is small; the sweep prints it.")
        return 2
    return 0


def self_test():
    print("b_pkgsize self-test — synthetic ground truth and deliberate breaks\n")
    rng = np.random.default_rng(7)
    passes = fails = 0

    def draw(w, h, deg, size=400, bg=30, fg=220):
        """A rotated filled rectangle w x h, centred, on a noisy background."""
        img = np.full((size, size), bg, float) + rng.normal(0, 3, (size, size))
        yy, xx = np.mgrid[0:size, 0:size]
        cx = cy = (size - 1) / 2
        a = math.radians(deg)
        u = (xx - cx) * math.cos(a) + (yy - cy) * math.sin(a)
        v = -(xx - cx) * math.sin(a) + (yy - cy) * math.cos(a)
        m = (np.abs(u) <= w / 2) & (np.abs(v) <= h / 2)
        img[m] = fg + rng.normal(0, 3, m.sum())
        return np.clip(img, 0, 255).astype(np.uint8)

    for w, h, deg in [(180.0, 90.0, 0.0), (150.0, 150.0, 31.0), (200.0, 60.0, -17.0)]:
        r = measure(draw(w, h, deg), "bright")
        el, es = max(w, h), min(w, h)
        e1 = abs(r["long_px"] - el) / el
        e2 = abs(r["short_px"] - es) / es
        if e1 < 0.03 and e2 < 0.03:
            print(f"  PASS  recover {el:.0f}x{es:.0f} at {deg} deg: got "
                  f"{r['long_px']:.1f}x{r['short_px']:.1f} px "
                  f"({e1*100:.1f}%, {e2*100:.1f}% error)")
            passes += 1
        else:
            print(f"  FAIL  recover {el:.0f}x{es:.0f}: got "
                  f"{r['long_px']:.1f}x{r['short_px']:.1f}")
            fails += 1

    r = measure(np.full((200, 200), 40, np.uint8), "bright")
    if r is None:
        print("  PASS  a flat box yields NO component -> CANNOT DETERMINE, "
              "not a zero size")
        passes += 1
    else:
        print(f"  FAIL  a flat box produced a measurement: {r}")
        fails += 1

    big = draw(430.0, 200.0, 0.0)   # clipped left and right, background above
    r = measure(big, "bright")     # and below so the box is still separable
    if r is not None and r["touches_box_edge"]:
        print("  PASS  edge control FIRES on a part that runs out of the box")
        passes += 1
    else:
        print("  FAIL  edge control stayed quiet on a clipped part")
        fails += 1

    flat2 = np.clip(np.full((200, 200), 40.0) + rng.normal(0, 6, (200, 200)),
                    0, 255).astype(np.uint8)
    r = measure(flat2, "bright")
    if r is None:
        print("  PASS  a NOISY box with no real object is refused "
              "(rectangularity floor) - Otsu's separability alone did NOT "
              "catch this and that is why the second gate exists")
        passes += 1
    else:
        print(f"  FAIL  noise-only box produced a measurement: "
              f"{r['long_px']:.0f}x{r['short_px']:.0f} px, separability "
              f"{r['separability']}, rectangularity {r['rectangularity']}")
        fails += 1

    r = measure(draw(180.0, 90.0, 0.0), "bright")
    if not r["touches_box_edge"]:
        print("  PASS  edge control STAYS QUIET on a part with clear margin")
        passes += 1
    else:
        print("  FAIL  edge control fired on a part with clear margin")
        fails += 1

    two = draw(120.0, 120.0, 0.0)
    two[10:40, 10:70] = 230
    r = measure(two, "bright")
    e = abs(r["long_px"] - 120) / 120
    if r["components_found"] >= 2 and e < 0.03:
        print(f"  PASS  a second bright object nearby does NOT join the "
              f"measurement: {r['components_found']} components, still "
              f"{r['long_px']:.1f} px")
        passes += 1
    else:
        print(f"  FAIL  neighbour contaminated the measurement: {r}")
        fails += 1

    r = measure(draw(180.0, 90.0, 0.0, bg=220, fg=30), "dark")
    if abs(r["long_px"] - 180) / 180 < 0.03:
        print(f"  PASS  --pick dark recovers a dark part on a light ground: "
              f"{r['long_px']:.1f} px")
        passes += 1
    else:
        print(f"  FAIL  --pick dark: {r}")
        fails += 1

    # colour control: a blue part on a red ground at EQUAL luminance
    size = 300
    rgb = np.zeros((size, size, 3), float)
    rgb[..., 0] = 120.0                      # red ground: R high
    rgb[..., 2] = 40.0                       # 0.299R+0.114B = 40.44
    yy, xx = np.mgrid[0:size, 0:size]
    m = (np.abs(xx - 150) <= 60) & (np.abs(yy - 150) <= 35)
    rgb[m, 0] = 60.0                         # blue part, chosen so that
    rgb[m, 2] = 197.4                        # 0.299R+0.114B = 40.44 EXACTLY,
                                             # i.e. identical luminance
    rgb[..., 1] = 80.0
    rgb += rng.normal(0, 2, rgb.shape)
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    lum_r = measure(channel(rgb, "lum"), "dark")
    bmr = measure(channel(rgb, "b-r"), "bright")
    lum_failed = lum_r is None or abs(lum_r["long_px"] - 121) / 121 > 0.05
    if lum_failed and bmr is not None and abs(bmr["long_px"] - 121) / 121 < 0.05:
        print(f"  PASS  colour channel earns its keep: luminance CANNOT find a "
              f"blue part on an equal-luminance red ground, b-r recovers it at "
              f"{bmr['long_px']:.0f}x{bmr['short_px']:.0f} px (true 121x71)")
        passes += 1
    else:
        print(f"  FAIL  colour control: lum={lum_r}, b-r={bmr}")
        fails += 1

    # ---- ROI-padding sweep (E07 s11). Three cases, and case 12 is the one that
    # ---- matters: a single run that LOOKS confident and is 30 % wrong.
    import tempfile
    from scipy import ndimage as _nd

    def _soft_scene(seed=11, S=700):
        r2 = np.random.default_rng(seed)
        yy, xx = np.mgrid[0:S, 0:S]
        c = (S - 1) / 2
        img = np.full((S, S), 70.0)
        img[(np.abs(xx - c) <= 70) & (np.abs(yy - c) <= 45)] = 170.0
        img = _nd.gaussian_filter(img, 18.0)      # soft edges, as a photograph has
        img[np.hypot(xx - c, yy - c) > 160] = 245.0   # bright surround that only
        img += r2.normal(0, 3, (S, S))                # enters as the box grows
        return np.clip(img, 0, 255).astype(np.uint8), c

    # 11: a HARD-edged part with clear margin must NOT move with the box
    hard = draw(180.0, 90.0, 0.0, size=500)
    him = Image.fromarray(np.stack([hard] * 3, -1))
    _, sm = pad_sweep(him, (140, 180, 360, 320), "bright", "lum", [0, 20, 40, 60])
    if sm["verdict"] == "STABLE" and sm["long_px"]["spread_frac"] < 0.02:
        print(f"  PASS  pad sweep STAYS QUIET on a hard-edged part with margin: "
              f"long spread {sm['long_px']['spread_frac']*100:.2f}%, "
              f"short {sm['short_px']['spread_frac']*100:.2f}% -> STABLE")
        passes += 1
    else:
        print(f"  FAIL  pad sweep fired on a part that does not move: {sm}")
        fails += 1

    # 12: THE ONE THAT MATTERS. A soft-edged part whose Otsu threshold is dragged
    # by a bright surround entering the box. It never touches the box edge, so the
    # existing clip control cannot see it; separability 0.83 and rectangularity
    # 0.86 at pad 0 make the single run look like a measurement. It is 30 % wrong.
    soft, c = _soft_scene()
    sim = Image.fromarray(np.stack([soft] * 3, -1))
    box = (int(c) - 120, int(c) - 95, int(c) + 120, int(c) + 95)
    single = measure(channel(np.asarray(sim.crop(box)), "lum"), "bright")
    rows, sm = pad_sweep(sim, box, "bright", "lum", [0, 20, 40, 60])
    looked_fine = (single is not None and not single["touches_box_edge"]
                   and single["rectangularity"] > 0.8
                   and single["separability"] > 0.7)
    caught = sm["verdict"] == "ROI-DEPENDENT" and sm["long_px"]["spread_frac"] > 0.15
    if looked_fine and caught:
        print(f"  PASS  pad sweep CATCHES a box-dependent extent the clip control "
              f"cannot see: single run {single['long_px']:.0f}x"
              f"{single['short_px']:.0f} px, rect {single['rectangularity']:.2f}, "
              f"sep {single['separability']:.2f}, edge NOT touched — sweep says "
              f"long moves {sm['long_px']['spread_frac']*100:.0f}%, short "
              f"{sm['short_px']['spread_frac']*100:.0f}% -> ROI-DEPENDENT")
        passes += 1
    else:
        print(f"  FAIL  box-dependence control: looked_fine={looked_fine} "
              f"caught={caught} summary={sm}")
        fails += 1

    # 12b: the break must reach the EXIT CODE, not just the summary dict (E07 s14:
    # a break in one place and a check in another are not connected by intention).
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        sim.save(tf.name)
        ns = argparse.Namespace(image=tf.name, box=list(box), pick="bright",
                                channel="lum", px_per_mm=None, ruler_note=None,
                                label="selftest-softbox", json_out=None,
                                pad_sweep=True, pads="0,20,40,60",
                                overlay_png=None)
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = run(ns)
    if code == 2:
        print("  PASS  the sweep verdict reaches the EXIT CODE: run() returns 2 "
              "(CANNOT DETERMINE) on the box-dependent scene, so a caller reading "
              "$? cannot miss it")
        passes += 1
    else:
        print(f"  FAIL  run() returned {code} on a ROI-DEPENDENT scene; the sweep "
              "found it and the exit code did not carry it")
        fails += 1

    # 14: the median cross-section must EQUAL the extent on a clean rectangle.
    # This is the negative control for the robust estimator: it must not shrink a
    # part that has nothing sticking out, or every size in the BOM moves.
    clean = draw(180.0, 90.0, 0.0, size=400)
    got = otsu(clean.astype(float).ravel())
    rbc = robust_extent(clean, "bright", got[0])
    if (abs(rbc["median_long_px"] - 180) / 180 < 0.03 and
            abs(rbc["median_short_px"] - 90) / 90 < 0.03 and
            abs(rbc["protrusion_long_frac"]) < 0.03):
        print(f"  PASS  median cross-section EQUALS the extent on a clean "
              f"rectangle: {rbc['median_long_px']:.0f}x{rbc['median_short_px']:.0f} "
              f"px (true 180x90), protrusion {rbc['protrusion_long_frac']*100:+.1f}%")
        passes += 1
    else:
        print(f"  FAIL  robust estimator distorts a clean rectangle: {rbc}")
        fails += 1

    # 15: THE CASE IT EXISTS FOR. Four corner tabs, exactly X1's solder fillets.
    # The min-area rectangle must be badly inflated and the median must not be.
    def _tabbed(halfy):
        t2 = draw(180.0, 90.0, 0.0, size=400)
        for sx in (-1, 1):
            for sy in (-1, 1):
                x, y = 200 + sx * 90, 200 + sy * 45
                t2[max(0, y - halfy):y + halfy, max(0, x - 20):x + 20] = 235
        return t2

    tab = _tabbed(9)          # tabs 18 px on a 90 px side: X1's pads, roughly
    rbt = robust_extent(tab, "bright", otsu(tab.astype(float).ravel())[0])
    rect_err = abs(rbt["rect_long_px"] - 180) / 180
    med_err = abs(rbt["median_long_px"] - 180) / 180
    if rect_err > 0.15 and med_err < 0.05:
        print(f"  PASS  corner tabs inflate the min-area rectangle to "
              f"{rbt['rect_long_px']:.0f}x{rbt['rect_short_px']:.0f} px "
              f"({rect_err*100:.0f}% long error) and the median holds at "
              f"{rbt['median_long_px']:.0f}x{rbt['median_short_px']:.0f} px "
              f"({med_err*100:.1f}% error) — this is X1's four solder pads")
        passes += 1
    else:
        print(f"  FAIL  corner-tab case: rect_err={rect_err:.3f} "
              f"med_err={med_err:.3f} {rbt}")
        fails += 1

    # 15b: THE STATED LIMIT. Tabs half the body height cover MORE than half the
    # slices, so the median carries them and cannot see the protrusion. Asserted
    # as a known limit so that a future change claiming otherwise goes red here.
    big = _tabbed(22)
    rbb = robust_extent(big, "bright", otsu(big.astype(float).ravel())[0])
    med_blind = abs(rbb["median_long_px"] - rbb["rect_long_px"]) < 1.0
    p25_sees = abs(rbb["p25_long_px"] - 180) / 180 < 0.05
    if med_blind and p25_sees:
        print(f"  PASS  stated limit holds: with tabs over half the slices the "
              f"MEDIAN is blind ({rbb['median_long_px']:.0f} px = the rectangle) "
              f"and the p25 still recovers the body "
              f"({rbb['p25_long_px']:.0f} px, true 180). Both are reported and "
              f"they disagree by "
              f"{rbb['median_vs_p25_long_frac']*100:+.0f}%, which is the tell.")
        passes += 1
    else:
        print(f"  FAIL  limit case: med_blind={med_blind} p25_sees={p25_sees} "
              f"{rbb}")
        fails += 1

    # 13: one padding is not a sweep. A single point must be CANNOT DETERMINE,
    # never STABLE — otherwise a sweep that silently collapsed to one box would
    # report the strongest possible verdict from no comparison at all.
    _, sm1 = pad_sweep(him, (140, 180, 360, 320), "bright", "lum", [0])
    if sm1["verdict"] == "CANNOT DETERMINE" and sm1["n_usable"] == 1:
        print("  PASS  a sweep with one usable padding reports CANNOT DETERMINE, "
              "not STABLE")
        passes += 1
    else:
        print(f"  FAIL  single-point sweep did not refuse: {sm1}")
        fails += 1

    print(f"\n{passes}/{passes+fails} passed, {fails} failed")
    return 1 if fails else 0


def main():
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    p = argparse.ArgumentParser()
    p.add_argument("image")
    p.add_argument("--box", nargs=4, type=int, required=True,
                   metavar=("X0", "Y0", "X1", "Y1"))
    p.add_argument("--pick", choices=["dark", "bright"], required=True)
    p.add_argument("--channel", choices=["lum", "b-r", "r-b"], default="lum")
    p.add_argument("--px-per-mm", type=float)
    p.add_argument("--ruler-note")
    p.add_argument("--label")
    p.add_argument("--json-out")
    p.add_argument("--pad-sweep", action="store_true",
                   help="re-measure with the box grown by each --pads value and "
                        "report how much the answer moves (E07 s11). An axis that "
                        "moves more than 5%% is reporting the BOX, not the part.")
    p.add_argument("--pads", default="0,20,40,60",
                   help="paddings in px for --pad-sweep (default 0,20,40,60)")
    p.add_argument("--half-max", action="store_true",
                   help="also report the extent at the 50%% crossing between the "
                        "part and its background. Otsu is not the midpoint when "
                        "the two classes differ in size, and on a soft edge that "
                        "costs a FIXED number of px per side - additive, so it is "
                        "worst on small parts. Measured on the nRF52832: Otsu "
                        "reads +12.1/+12.3 px over the published body.")
    p.add_argument("--robust", action="store_true",
                   help="also report the MEDIAN cross-section in the part's own "
                        "frame. The min-area rectangle is set by extremes, so "
                        "corner solder fillets become the size; a median ignores "
                        "them. Prints how much of the rectangle is protrusion.")
    p.add_argument("--thr-sweep", action="store_true",
                   help="extent across the middle 60%% of the part/background gap. "
                        "Says whether the size is a threshold choice or a property "
                        "of the edge.")
    p.add_argument("--overlay-png",
                   help="write the kept component outlined in green on the crop, "
                        "so the segmentation can be LOOKED at")
    sys.exit(run(p.parse_args()))


if __name__ == "__main__":
    main()
