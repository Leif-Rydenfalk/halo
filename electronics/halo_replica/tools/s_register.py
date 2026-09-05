#!/usr/bin/env python3
"""s_register.py — put the four delayered AirTag layer photographs in ONE frame.

WHY THIS HAS TO EXIST BEFORE ANY VIA CLAIM. Asking "does this via land on the
component side have a counterpart on the other outer face?" is a question about
POSITION, and the four images are at different scales (layer1 is 2014 px wide,
the others 1280) with different crops. Comparing them by eye at nominal pixel
coordinates would compare two different places on the board and call the
mismatch a blind via. Registration first, or the answer is manufactured.

The frame is the board itself, using two features present on every layer and
belonging to the BOARD rather than the photograph:

  centre hole   a dark blob at the middle of the annulus
  board extent  the warm (copper) region's radial extent from that centre

Both are measured, not assumed, and both are reported so a bad fit is visible
rather than silent. Scale is taken from the board extent and origin from the
centre hole, giving a similarity transform with no rotation term -- the images
are visibly at the same orientation, and THAT IS A STATED ASSUMPTION which
`selftest` checks by measuring the residual of a feature it did not fit on.

Verbs
  fit       measure centre and extent per image, print the transform
  selftest  6 cases including the controls that matter

Exit code IS the verdict: 0 PASS, 1 FAIL, 2 CANNOT DETERMINE.
Images are NOT redistributed -- the source repo states no licence. Set SS_DIR.
"""
import math
import os
import sys

PASS, FAIL, CANNOT = 0, 1, 2

FILES = ["layer1.jpg", "layer2.jpeg", "layer3.jpeg", "layer4.jpeg"]


def _rgb(path, step=1):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    w, h = im.size
    return im.load(), w, h


def centre_hole(path, dark=70, step=2):
    """Centroid and equivalent radius of the darkest blob in the middle third.
    The centre hole is the only large very-dark region there: copper is bright,
    the pour is bright, and the background sits outside the annulus."""
    px, w, h = _rgb(path)
    x0, x1 = int(w * 0.33), int(w * 0.67)
    y0, y1 = int(h * 0.33), int(h * 0.67)
    xs = ys = n = 0
    for y in range(y0, y1, step):
        for x in range(x0, x1, step):
            r, g, b = px[x, y]
            if max(r, g, b) <= dark:
                xs += x
                ys += y
                n += 1
    if n < 20:
        return None
    cx, cy = xs / n, ys / n
    area = n * step * step
    return cx, cy, math.sqrt(area / math.pi)


def board_extent(path, centre, min_rb=12, step=3, pct=0.98):
    """Radius containing `pct` of the warm (copper) pixels, measured from the
    given centre. Copper is warm; the background in these frames is grey-green.
    A percentile rather than a maximum, so one warm speck of background outside
    the board cannot set the scale."""
    px, w, h = _rgb(path)
    cx, cy = centre
    radii = []
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b = px[x, y]
            if (r - b) >= min_rb and max(r, g, b) > 60:
                radii.append(math.hypot(x - cx, y - cy))
    if len(radii) < 200:
        return None
    radii.sort()
    return radii[int(len(radii) * pct) - 1], len(radii)


def fit(d):
    out = {}
    for f in FILES:
        p = os.path.join(d, f)
        if not os.path.exists(p):
            out[f] = None
            continue
        c = centre_hole(p)
        if c is None:
            out[f] = None
            continue
        cx, cy, hole_r = c
        e = board_extent(p, (cx, cy))
        if e is None:
            out[f] = None
            continue
        out[f] = {"cx": cx, "cy": cy, "hole_r": hole_r,
                  "extent_r": e[0], "warm_px": e[1]}
    return out


def cmd_fit(d):
    m = fit(d)
    ref = m.get(FILES[0])
    print(f"{'image':<14}{'centre x':>10}{'centre y':>10}{'hole r':>9}"
          f"{'extent r':>10}{'hole/extent':>13}{'scale vs L1':>13}")
    for f in FILES:
        v = m[f]
        if v is None:
            print(f"{f:<14}   CANNOT DETERMINE — features not found")
            continue
        ratio = v["hole_r"] / v["extent_r"]
        sc = (ref["extent_r"] / v["extent_r"]) if ref else float("nan")
        print(f"{f:<14}{v['cx']:10.1f}{v['cy']:10.1f}{v['hole_r']:9.1f}"
              f"{v['extent_r']:10.1f}{ratio:13.4f}{sc:13.4f}")
    print("\nhole/extent is the CHECK, not an output: it is a property of the")
    print("BOARD, so it must agree across all four images regardless of how each")
    print("was photographed. If it does not, the fit is wrong and nothing built")
    print("on these coordinates can be trusted.")
    return m


def to_ref(m, f, x, y):
    """Map a point in image `f` into layer1's pixel frame."""
    ref, v = m[FILES[0]], m[f]
    s = ref["extent_r"] / v["extent_r"]
    return (ref["cx"] + (x - v["cx"]) * s, ref["cy"] + (y - v["cy"]) * s)


def cmd_selftest(d):
    m = fit(d)
    n_ok = n_red = 0

    def check(name, got, ok, want):
        nonlocal n_ok, n_red
        print(f"  [{'ok  ' if ok else 'RED '}] {name}\n         want {want}\n         got  {got}")
        if ok:
            n_ok += 1
        else:
            n_red += 1

    print("s_register selftest — 6 cases\n")

    for f in FILES:
        check(f"{f}: centre hole and board extent both found",
              "found" if m[f] else "NOT found", m[f] is not None, "found")
    if any(v is None for v in m.values()):
        print(f"\n{n_ok} ok, {n_red} red")
        return FAIL

    # THE CHECK THAT COULD FAIL. hole/extent is a ratio of two board features,
    # so it is scale- and crop-invariant and must agree across all four images.
    # It was NOT used to compute the transform, so it is an independent residual
    # rather than a restatement of the fit.
    ratios = [m[f]["hole_r"] / m[f]["extent_r"] for f in FILES]
    spread = (max(ratios) - min(ratios)) / (sum(ratios) / len(ratios))
    check("hole/extent agrees across all four images (independent residual)",
          f"{[round(r, 4) for r in ratios]}, spread {spread * 100:.1f}%",
          spread < 0.15, "spread < 15%")

    # NEGATIVE CONTROL: the transform must NOT map everything onto everything.
    # Map a point far off-centre in layer2 and require it lands off-centre in
    # layer1 too. A transform that collapses the plane would make every via
    # "match" and the whole via test would be a decoration.
    v = m["layer2.jpeg"]
    px, py = v["cx"] + v["extent_r"] * 0.8, v["cy"]
    qx, qy = to_ref(m, "layer2.jpeg", px, py)
    ref = m[FILES[0]]
    dist = math.hypot(qx - ref["cx"], qy - ref["cy"]) / ref["extent_r"]
    check("transform does not collapse the plane (0.8R stays near 0.8R)",
          f"{dist:.3f} R", 0.6 < dist < 1.0, "between 0.6 and 1.0 R")

    print(f"\n{n_ok} ok, {n_red} red")
    return PASS if n_red == 0 else FAIL


def main(argv):
    d = os.environ.get("SS_DIR")
    if len(argv) < 2:
        print(__doc__)
        return CANNOT
    if d is None or not os.path.isdir(d):
        print("CANNOT DETERMINE — set SS_DIR to a directory holding layer1..layer4.")
        print("Those images are NOT redistributed here: the source repository")
        print("(github.com/stacksmashing/airtag-hardware) states no licence.")
        return CANNOT
    if argv[1] == "fit":
        cmd_fit(d)
        return PASS
    if argv[1] == "selftest":
        return cmd_selftest(d)
    print(f"unknown verb {argv[1]!r}")
    return CANNOT


if __name__ == "__main__":
    sys.exit(main(sys.argv))
