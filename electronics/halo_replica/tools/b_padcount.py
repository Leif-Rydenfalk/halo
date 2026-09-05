#!/usr/bin/env python3
"""b_padcount.py — count the pads of an EXPOSED LAND PATTERN, or refuse.

Exit code IS the verdict: 0 PASS, 1 FAIL, 2 CANNOT DETERMINE.

Why this exists: `images/airtag/oflynn-airtag-tests.jpeg` shows an AirTag board
with chips PULLED OFF, so land patterns that are hidden under a package in
every other photograph are bare. A pad count is a COUNTABLE integer — the
strongest kind of evidence available from a photograph, because unlike a
length it cannot be off by 4 %; it is either right or it is a different number.

Two INDEPENDENT routes to the same integer, which is the point:
  A. blob count — threshold, label, filter by area, count connected components
  B. lattice prediction — from the pad CENTROIDS alone, find the two lattice
     vectors and predict how many cells the array's extent spans
Route A knows nothing about periodicity; route B knows nothing about how many
blobs there were. They can disagree, and when they do the answer is CANNOT
DETERMINE. (Contrast the coil measurement this project got wrong: a turn count
and a band width taken from above are the SAME radial extent twice, so they
could not have disagreed. Two routes are only worth something if each could
have refuted the other.)

THE CONTROL THAT MATTERS — `--sweep`. E07 family 11: "a result that tracks a
parameter of the SEARCH rather than a property of the SUBJECT." So the count is
re-run across a grid of threshold offsets and box paddings. If the count moves,
the count is a property of the operator and the verdict is CANNOT DETERMINE.

Usage:
  b_padcount.py IMG --box X0 Y0 X1 Y1 [--sweep] [--label NAME] [--json-out F]
  b_padcount.py --self-test
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

MIN_PADS = 4


def _otsu(v):
    hist, edges = np.histogram(v, bins=256, range=(0, 255))
    total = hist.sum()
    if total == 0:
        return 128.0
    w0 = np.cumsum(hist); w1 = total - w0
    c = (edges[:-1] + edges[1:]) / 2
    s0 = np.cumsum(hist * c); s1 = s0[-1] - s0
    with np.errstate(invalid="ignore", divide="ignore"):
        between = w0 * w1 * (s0 / w0 - s1 / w1) ** 2
    between[~np.isfinite(between)] = -1
    return float(c[int(np.argmax(between))])


def blobs(arr, thr_offset=0.0):
    """Route A. Returns (centroids Nx2 as (x,y), areas, threshold)."""
    t = _otsu(arr.astype(float).ravel()) + thr_offset
    mask = arr > t
    lab, n = ndimage.label(mask)
    if n == 0:
        return np.zeros((0, 2)), np.zeros(0), t
    areas = np.asarray(ndimage.sum(mask, lab, range(1, n + 1)))
    # A land pattern's pads are all the same size. Keep blobs within a factor
    # of 3 of the MEDIAN area: this drops single-pixel speckle and drops the
    # one huge blob you get when neighbouring pads bridge.
    med = float(np.median(areas))
    keep = np.nonzero((areas >= max(2.0, med / 3.0)) & (areas <= med * 3.0))[0]
    if len(keep) == 0:
        return np.zeros((0, 2)), np.zeros(0), t
    cen = np.asarray(ndimage.center_of_mass(mask, lab, list(keep + 1)))
    return cen[:, ::-1], areas[keep], t   # centre_of_mass gives (row, col)


def lattice(cen):
    """Route B. Two lattice vectors from the centroid cloud, and the count of
    grid cells its extent spans. Knows nothing about how many blobs there were
    beyond their positions."""
    if len(cen) < MIN_PADS:
        return None
    # nearest-neighbour offsets
    d = cen[:, None, :] - cen[None, :, :]
    dist = np.hypot(d[..., 0], d[..., 1])
    np.fill_diagonal(dist, np.inf)
    nn = dist.min(axis=1)
    pitch = float(np.median(nn))
    if not np.isfinite(pitch) or pitch <= 0:
        return None
    # dominant axis of the near-neighbour offsets, folded to [0,90)
    near = np.nonzero(dist < pitch * 1.4)
    if len(near[0]) < MIN_PADS:
        return None
    off = cen[near[1]] - cen[near[0]]
    ang = np.degrees(np.arctan2(off[:, 1], off[:, 0])) % 90.0
    hist, edges = np.histogram(ang, bins=90, range=(0, 90))
    a0 = math.radians((edges[int(np.argmax(hist))] + 0.5))
    u = np.array([math.cos(a0), math.sin(a0)])
    v = np.array([-u[1], u[0]])
    pu, pv = cen @ u, cen @ v
    # pitch along each axis, measured on the projections rather than assumed equal
    def axis_pitch(p):
        s = np.sort(p)
        gaps = np.diff(s)
        gaps = gaps[gaps > pitch * 0.35]
        return float(np.median(gaps)) if len(gaps) else pitch
    du, dv = axis_pitch(pu), axis_pitch(pv)
    cols = int(round((pu.max() - pu.min()) / du)) + 1
    rows = int(round((pv.max() - pv.min()) / dv)) + 1
    return {"pitch_px": round(pitch, 2), "pitch_u_px": round(du, 2),
            "pitch_v_px": round(dv, 2), "rows": rows, "cols": cols,
            "cells": rows * cols, "axis_deg": round(math.degrees(a0), 1),
            "extent_u_px": round(float(pu.max() - pu.min()), 1),
            "extent_v_px": round(float(pv.max() - pv.min()), 1)}


def one(arr, thr_offset=0.0):
    cen, areas, t = blobs(arr, thr_offset)
    lat = lattice(cen)
    return {"count": int(len(cen)), "threshold": round(t, 1),
            "median_pad_area_px": round(float(np.median(areas)), 1) if len(areas) else None,
            "lattice": lat}


def run(args):
    im = Image.open(args.image).convert("L")
    x0, y0, x1, y1 = args.box
    print(f"b_padcount  input: {args.image}  box [{x0}:{x1},{y0}:{y1}] "
          f"({x1-x0}x{y1-y0} px)")
    if args.label:
        print(f"  label: {args.label}")
    base = one(np.asarray(im.crop((x0, y0, x1, y1))))
    if base["count"] < MIN_PADS:
        print(f"  CANNOT DETERMINE — only {base['count']} pad-like blobs in this box")
        return 2
    lat = base["lattice"]
    print(f"  route A  blob count           : {base['count']}")
    if lat:
        print(f"  route B  lattice {lat['rows']} x {lat['cols']} = {lat['cells']} cells, "
              f"pitch {lat['pitch_px']} px, axis {lat['axis_deg']} deg")
    else:
        print("  route B  CANNOT DETERMINE — no lattice recoverable")
        return 2
    # the two routes must be reconcilable: a real land pattern may have EMPTY
    # cells (depopulated corners are normal) so A <= B, but A > B is impossible
    # and means the blobs are not on the lattice the fit found.
    if base["count"] > lat["cells"]:
        print(f"  FAIL — {base['count']} blobs on a lattice with only "
              f"{lat['cells']} cells. The two routes are irreconcilable, so at "
              "least one is measuring something other than this land pattern.")
        return 1
    empty = lat["cells"] - base["count"]
    print(f"  reconciled: {base['count']} pads in a {lat['rows']} x {lat['cols']} "
          f"lattice, {empty} cell(s) empty ({empty/lat['cells']:.0%})")

    if args.sweep:
        print("  --sweep: is the count a property of the BOARD or of the SEARCH?")
        counts, rows_seen = [], []
        for pad in (0, 3, 6, 9):
            for dt in (-12.0, -6.0, 0.0, 6.0, 12.0):
                a = np.asarray(im.crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad)))
                r = one(a, dt)
                counts.append(r["count"])
                if r["lattice"]:
                    rows_seen.append((r["lattice"]["rows"], r["lattice"]["cols"]))
        lo, hi = min(counts), max(counts)
        spread = (hi - lo) / max(1, base["count"])
        uniq = sorted(set(rows_seen))
        print(f"    blob count over 20 (pad, threshold) combinations: "
              f"{lo}..{hi}, spread {spread:.0%} of the base count")
        print(f"    lattice shapes seen: {uniq}")
        base["sweep"] = {"min": lo, "max": hi, "spread_frac": round(spread, 3),
                         "lattice_shapes": [list(s) for s in uniq],
                         "n_combinations": len(counts)}
        if len(uniq) == 1 and spread <= 0.05:
            print("    STABLE — the lattice shape never changed and the blob "
                  "count moved by <=5%. This is a property of the board.")
        else:
            print("    UNSTABLE — the answer tracks the search parameters. "
                  "CANNOT DETERMINE, and the exact figure above must not be "
                  "quoted as the pad count.")
            base["verdict"] = "CANNOT DETERMINE"
            if args.json_out:
                base["input"] = {"image": args.image, "box": args.box}
                json.dump(base, open(args.json_out, "w"), indent=2)
            return 2
    base["verdict"] = "MEASURED"
    base["empty_cells"] = empty
    if args.json_out:
        base["input"] = {"image": args.image, "box": args.box, "label": args.label}
        json.dump(base, open(args.json_out, "w"), indent=2)
        print(f"  wrote {args.json_out}")
    return 0


def _grid_img(rows, cols, pitch=20, r=6, drop=(), size=None, deg=0.0,
              noise=3.0, seed=3, fade=None):
    rng = np.random.default_rng(seed)
    size = size or (int(pitch * (max(rows, cols) + 3)),) * 2
    img = np.full(size, 30.0) + rng.normal(0, noise, size)
    cy, cx = size[0] / 2, size[1] / 2
    a = math.radians(deg)
    yy, xx = np.mgrid[0:size[0], 0:size[1]]
    k = 0
    for i in range(rows):
        for j in range(cols):
            if (i, j) in drop:
                continue
            u = (j - (cols - 1) / 2) * pitch
            v = (i - (rows - 1) / 2) * pitch
            px = cx + u * math.cos(a) - v * math.sin(a)
            py = cy + u * math.sin(a) + v * math.cos(a)
            bright = 220.0
            if fade is not None and k in fade:
                bright = 120.0          # a pad only just above the ground
            img[(xx - px) ** 2 + (yy - py) ** 2 <= r * r] = bright
            k += 1
    return np.clip(img + rng.normal(0, noise, size), 0, 255).astype(np.uint8)


def self_test():
    print("b_padcount self-test — synthetic ground truth and deliberate breaks\n")
    rng = np.random.default_rng(11)
    p = f = 0

    def chk(name, cond, detail=""):
        nonlocal p, f
        print(f"  {'PASS' if cond else 'FAIL'}  {name}{': ' + detail if detail else ''}")
        if cond: p += 1
        else: f += 1

    r = one(_grid_img(13, 7))
    chk("recover a full 13 x 7 grid", r["count"] == 91 and r["lattice"] and
        r["lattice"]["cells"] == 91,
        f"count {r['count']}, lattice {r['lattice']['rows']}x{r['lattice']['cols']}")

    r = one(_grid_img(13, 7, drop=((0, 0), (0, 6), (12, 0))))
    chk("3 DEPOPULATED corners: blob count drops, lattice does NOT",
        r["count"] == 88 and r["lattice"]["cells"] == 91,
        f"count {r['count']}, cells {r['lattice']['cells']}")

    r = one(_grid_img(9, 5, deg=23.0))
    chk("a ROTATED grid is still counted", r["count"] == 45 and
        r["lattice"]["cells"] == 45,
        f"count {r['count']}, axis {r['lattice']['axis_deg']} deg")

    # route B must be able to REFUSE: scattered blobs are not a lattice
    size = 300
    img = np.full((size, size), 30.0) + rng.normal(0, 3, (size, size))
    yy, xx = np.mgrid[0:size, 0:size]
    pts = rng.uniform(30, 270, (40, 2))
    for px, py in pts:
        img[(xx - px) ** 2 + (yy - py) ** 2 <= 36] = 220
    r = one(np.clip(img, 0, 255).astype(np.uint8))
    lat = r["lattice"]
    bad = lat is None or r["count"] > lat["cells"]
    chk("SCATTERED blobs are NOT reconciled as a land pattern",
        bad, f"count {r['count']}, cells {lat['cells'] if lat else None} "
             "— route A exceeds route B, which is the irreconcilable case")

    r = one(np.full((200, 200), 40, np.uint8))
    chk("a flat box yields no pads", r["count"] < MIN_PADS, f"count {r['count']}")

    # THE SWEEP CONTROL: pads of graded brightness, so the count MUST move
    faded = _grid_img(13, 7, fade=set(range(0, 91, 3)))
    c_lo = one(faded, -30.0)["count"]
    c_hi = one(faded, +40.0)["count"]
    chk("sweep control FIRES: a graded land pattern gives different counts at "
        "different thresholds", c_lo != c_hi, f"{c_lo} at -30, {c_hi} at +40")

    clean = _grid_img(13, 7)
    c_lo = one(clean, -30.0)["count"]
    c_hi = one(clean, +40.0)["count"]
    chk("sweep control STAYS QUIET: a clean land pattern gives the SAME count "
        "across the same threshold range", c_lo == c_hi == 91,
        f"{c_lo} at -30, {c_hi} at +40")

    print(f"\n{p}/{p+f} passed, {f} failed")
    return 1 if f else 0


def main():
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--box", nargs=4, type=int, required=True,
                    metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--label")
    ap.add_argument("--json-out")
    sys.exit(run(ap.parse_args()))


if __name__ == "__main__":
    main()
