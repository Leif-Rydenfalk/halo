#!/usr/bin/env python3
"""p_dark.py -- can a SECOND source see the neutral-black packages, or is M08's
CANNOT DETERMINE a fact about the board rather than about one photograph?

Lane L5b BOARD BUILD.  Exit 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

THE QUESTION
  M08 closed the neutral-black IC packages as CANNOT DETERMINE after three detector
  attempts on O'Flynn's photograph.  Its sharpest finding was not "too dark" but
  OPERATOR DEPENDENCE: a stated ROI with Otsu inside returned the BOX -- 0/20/40/60 px
  of padding gave 3.35/3.98/4.09/4.50 mm for the SAME part, a 34% swing on padding
  alone.  An answer that is a function of the operator's choice is not a measurement.

  So the test here is NOT "does a threshold find something".  It is: DOES THE ANSWER
  STAY PUT WHEN THE OPERATOR'S NUMBER MOVES?  The same tool is run on both sources
  with the same physical parameters and the same sweep, and the two are compared.

SOURCE HANDLING -- READ, MEASURE, DO NOT VENDOR
  images/airtag/CATALOG.md lists iFixit's teardown photographs as LINK ONLY: their
  licence does not clearly permit redistribution.  They are fetched to a scratchpad
  OUTSIDE the repository, measured, and NOT saved into it.  Every number derived from
  one carries the URL and the retrieval time.  No account, no login, nothing sent.

CONTROLS
  D1 negative  the same detector on a stated patch of BARE SOLDERMASK must find
               nothing. If it finds packages there it is finding darkness, not parts.
  D2 sweep     the threshold is swept, and a component counts only if it SURVIVES
               most of the sweep with its centroid inside a stated tolerance. This is
               M08's own complaint turned into an admission rule.
  D3 A/B       the identical tool, identical physical parameters, on BOTH sources.
               If the new source is no better, that is a clean negative and it ends
               the question rather than leaving it open.
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

PASS, FAIL, CANNOT = 0, 1, 2
HERE = os.path.dirname(os.path.abspath(__file__))
REPL = os.path.dirname(HERE)


def say(*a):
    print(*a, file=sys.stderr)


def find_board(a_l, bright_bg=True):
    """Locate the board disc so nothing has to be typed in by hand."""
    m = a_l < 0.55 * float(np.percentile(a_l, 99)) if bright_bg else a_l > 0
    m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m)
    if n == 0:
        return None
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    m = lab == (int(np.argmax(sizes)) + 1)
    ys, xs = np.nonzero(m)
    cx, cy = xs.mean(), ys.mean()
    r = math.sqrt(m.sum() / math.pi)
    return cx, cy, r, m


def local_std(a, win):
    # separable box filter -- a dense (win x win) convolution on a 27 Mpx image with a
    # 44 px window does not finish
    m1 = ndimage.uniform_filter(a, win, mode="nearest")
    m2 = ndimage.uniform_filter(a * a, win, mode="nearest")
    return np.sqrt(np.maximum(m2 - m1 * m1, 0.0))


def detect(a_l, board_mask, tex, ppm, dark_thr, tex_thr, min_mm2, max_mm2, min_fill):
    m = (a_l < dark_thr) & (tex < tex_thr) & board_mask
    m = ndimage.binary_opening(m, np.ones((3, 3)))
    lab, n = ndimage.label(m)
    if n == 0:
        return []
    idx = np.arange(1, n + 1)
    counts = np.asarray(ndimage.sum(m, lab, idx))
    areas = counts / (ppm * ppm)
    keep = np.nonzero((areas >= min_mm2) & (areas <= max_mm2))[0]
    if len(keep) == 0:
        return []
    objs = ndimage.find_objects(lab)
    cents = ndimage.center_of_mass(m, lab, idx[keep])
    out = []
    for q, i in enumerate(keep):
        sl = objs[i]
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        fill = counts[i] / float(h * w)
        if fill < min_fill:
            continue
        cy_, cx_ = cents[q]
        out.append(dict(cx=float(cx_), cy=float(cy_), area_mm2=float(areas[i]),
                        bbox_mm=[float(w / ppm), float(h / ppm)], fill=float(fill)))
    return out


def sweep(a_l, board_mask, tex, ppm, thrs, tol_mm, **kw):
    """D2. A component is ADMITTED only if it survives most of the sweep with its
    centroid inside tol_mm. M08's operator-dependence, turned into an admission rule."""
    per = []
    for t in thrs:
        per.append(detect(a_l, board_mask, tex, ppm, t, **kw))
        say(f"  dark_thr {t:5.0f}: {len(per[-1]):3d} candidates")
    base = max(per, key=len)
    stable = []
    for c in base:
        hits, areas = 0, []
        for lst in per:
            near = [d for d in lst
                    if math.hypot(d["cx"] - c["cx"], d["cy"] - c["cy"]) / ppm <= tol_mm]
            if near:
                hits += 1
                areas.append(min(near, key=lambda d: math.hypot(
                    d["cx"] - c["cx"], d["cy"] - c["cy"]))["area_mm2"])
        if hits > len(thrs) / 2 and len(areas) > 1:
            sw = (max(areas) - min(areas)) / np.mean(areas) * 100
            stable.append(dict(c, n_thresholds=hits, of=len(thrs),
                               area_swing_pct=float(sw),
                               area_mm2_median=float(np.median(areas))))
    return per, stable


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--source-url", default=None,
                    help="required for a link-only source: every number derived from "
                         "one carries its URL")
    ap.add_argument("--retrieved-utc", default=None)
    ap.add_argument("--board-od-mm", type=float, default=25.1593)
    ap.add_argument("--hole-frac", type=float, default=0.55,
                    help="inner radius as a fraction of the board radius, to exclude "
                         "the centre hole. STATED, and swept in the sweep.")
    ap.add_argument("--thrs", nargs="*", type=float,
                    default=[70, 80, 90, 100, 110, 120])
    ap.add_argument("--tex-thr", type=float, default=None,
                    help="local-std ceiling. Omit and it is set from THIS image's own "
                         "texture distribution, so the two sources are not compared "
                         "through a constant that suits one of them.")
    ap.add_argument("--min-mm2", type=float, default=0.45)
    ap.add_argument("--max-mm2", type=float, default=60.0)
    ap.add_argument("--min-fill", type=float, default=0.72)
    ap.add_argument("--tol-mm", type=float, default=0.25)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    im = Image.open(a.image).convert("L")
    A = np.asarray(im).astype(float)
    say(f"{a.label}: {a.image}  {A.shape[1]}x{A.shape[0]}")
    if a.source_url:
        say(f"  LINK-ONLY SOURCE, measured not vendored: {a.source_url}")
        say(f"  retrieved {a.retrieved_utc}")
    b = find_board(A)
    if b is None:
        say("CANNOT DETERMINE: no board disc found.")
        sys.exit(CANNOT)
    cx, cy, R, bm = b
    ppm = 2 * R / a.board_od_mm
    say(f"  board disc: centre ({cx:.0f},{cy:.0f}) r {R:.0f} px -> {ppm:.2f} px/mm "
        f"at a STATED OD of {a.board_od_mm} mm")

    yy, xx = np.mgrid[0:A.shape[0], 0:A.shape[1]]
    rr = np.hypot(xx - cx, yy - cy)
    annulus = bm & (rr > a.hole_frac * R) & (rr < 0.97 * R)
    say(f"  annulus mask: {annulus.sum()} px = {annulus.sum()/ppm/ppm:.1f} mm2")

    win = max(3, int(round(0.25 * ppm)) | 1)          # a 0.25 mm window on BOTH images
    tex = local_std(A, win)
    tt = a.tex_thr if a.tex_thr else float(np.percentile(tex[annulus], 35))
    say(f"  texture window {win} px = 0.25 mm; ceiling {tt:.2f} "
        f"({'stated' if a.tex_thr else 'this image own 35th percentile'})")

    kw = dict(tex_thr=tt, min_mm2=a.min_mm2, max_mm2=a.max_mm2, min_fill=a.min_fill)
    say("D2 threshold sweep:")
    per, stable = sweep(A, annulus, tex, ppm, a.thrs, a.tol_mm, **kw)
    say(f"D2: {len(stable)} components survive more than half the sweep within "
        f"{a.tol_mm} mm")
    for c in sorted(stable, key=lambda d: -d["area_mm2_median"]):
        say(f"   {c['area_mm2_median']:7.3f} mm2  bbox {c['bbox_mm'][0]:.2f} x "
            f"{c['bbox_mm'][1]:.2f} mm  fill {c['fill']:.2f}  survives "
            f"{c['n_thresholds']}/{c['of']}  AREA SWING {c['area_swing_pct']:.1f}%")

    # D1 negative: a patch of the annulus with the detector's own found parts removed
    # is bare board. Running there must find nothing of package size.
    clear = annulus.copy()
    for c in stable:
        clear &= (np.hypot(xx - c["cx"], yy - c["cy"]) > 1.2 * math.sqrt(
            c["area_mm2_median"]) * ppm)
    d1 = detect(A, clear, tex, ppm, float(np.median(a.thrs)), **kw)
    say(f"D1 negative (the same detector on the annulus with its own finds masked out): "
        f"{len(d1)} package-sized components remain")

    med_swing = float(np.median([c["area_swing_pct"] for c in stable])) if stable else None
    say("")
    if not stable:
        say("VERDICT for this source: CANNOT DETERMINE -- nothing survives the sweep.")
        code = CANNOT
    elif med_swing is not None and med_swing > 34.0:
        say(f"VERDICT for this source: CANNOT DETERMINE -- median area swing "
            f"{med_swing:.1f}% is no better than M08's 34% on operator padding alone. "
            f"The answer is still a function of the operator's number.")
        code = CANNOT
    else:
        say(f"VERDICT for this source: MEASURED -- {len(stable)} components, median "
            f"area swing {med_swing:.1f}% across the whole threshold sweep, against "
            f"M08's 34% on padding alone.")
        code = PASS

    if a.out:
        json.dump(dict(tool="p_dark.py", label=a.label,
                       image_basename=os.path.basename(a.image),
                       source_url=a.source_url, retrieved_utc=a.retrieved_utc,
                       vendored=False,
                       licence_note=("LINK ONLY per images/airtag/CATALOG.md. Measured, "
                                     "not copied into the repository. Numbers derived "
                                     "from it cite the URL and the retrieval time."),
                       board_centre_px=[cx, cy], board_r_px=R, px_per_mm=ppm,
                       board_od_mm_stated=a.board_od_mm,
                       texture_window_px=win, texture_ceiling=tt,
                       thresholds=a.thrs, tol_mm=a.tol_mm,
                       per_threshold_counts=[len(p) for p in per],
                       n_stable=len(stable), median_area_swing_pct=med_swing,
                       D1_leftover_components=len(d1),
                       stable=stable),
                  open(a.out, "w"), indent=2)
        say(f"wrote {a.out}")
    say({0: "PASS", 1: "FAIL", 2: "CANNOT DETERMINE"}[code])
    sys.exit(code)


if __name__ == "__main__":
    main()
