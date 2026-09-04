#!/usr/bin/env python3
"""b_pkgsize.py — measure a component package off a photograph, or refuse.

Exit code IS the verdict: 0 PASS, 1 FAIL, 2 CANNOT DETERMINE.

The method, stated so a reader can attack it:
  1. inside a caller-given box, threshold luminance (Otsu) and keep either the
     bright side or the dark side, as the caller says;
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


def run(args):
    im = Image.open(args.image).convert("L")
    x0, y0, x1, y1 = args.box
    arr = np.asarray(im.crop((x0, y0, x1, y1)))
    print(f"b_pkgsize  input: {args.image}  box [{x0}:{x1},{y0}:{y1}] "
          f"({x1-x0}x{y1-y0} px)  pick={args.pick}")
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
                      "label": args.label, "ruler_note": args.ruler_note}
        json.dump(r, open(args.json_out, "w"), indent=2)
        print(f"  wrote {args.json_out}")
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
    p.add_argument("--px-per-mm", type=float)
    p.add_argument("--ruler-note")
    p.add_argument("--label")
    p.add_argument("--json-out")
    sys.exit(run(p.parse_args()))


if __name__ == "__main__":
    main()
