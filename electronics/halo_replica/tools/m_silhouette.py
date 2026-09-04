#!/usr/bin/env python3
"""m_silhouette.py -- diameter of a dark object on white paper, by AREA.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.

SIDE NAMING (project convention, halo lane commit 391f676):
  FRONT = COMPONENT side, per Apple's own FCC caption "MLB - Front".
  O'Flynn's "frontside" (battery contacts, NFC coil) is this project's BACK.

WHY AREA AND NOT A RAY-CAST.  A per-ray edge finder has to be right at every
single angle; a soft contact shadow on one side, or a bright component sitting
on the rim, corrupts that ray and the number with it.  (Measured: a half-max
ray-cast on FCC photo 6 followed the PENUMBRA and returned r sd 6.8 px on a
board that is round to about 1 px.)  Area integrates the whole boundary, so a
local defect moves the answer by its own size divided by the whole area.

  equivalent diameter  D = 2*sqrt(A/pi)   of the hole-FILLED largest dark blob.

THE THRESHOLD IS NOT A FREE PARAMETER -- IT IS SWEPT AND THE PLATEAU IS THE
RESULT.  A genuine step edge gives an area that barely moves across a wide
range of thresholds; a soft or ambiguous edge does not, and then this tool
answers CANNOT DETERMINE instead of picking a threshold that flatters it.
The reported uncertainty IS the spread across the plateau; nothing is assumed.

Exit codes: 0 measured, 2 CANNOT DETERMINE.  Prints its inputs.
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def sweep(sub, thr_lo, thr_hi, step=5):
    rows = []
    for t in range(thr_lo, thr_hi + 1, step):
        m = sub < t
        lab, n = ndimage.label(m)
        if n == 0:
            continue
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        k = int(np.argmax(sizes)) + 1
        big = lab == k
        # a blob touching the crop border is not a whole object
        touches = bool(big[0].any() or big[-1].any() or big[:, 0].any() or big[:, -1].any())
        filled = ndimage.binary_fill_holes(big)
        A = int(filled.sum())
        holeA = int(A - big.sum())
        ys, xs = np.nonzero(filled)
        rows.append(dict(thr=t, area_px=A, D_px=2 * math.sqrt(A / math.pi),
                         enclosed_hole_px=holeA,
                         hole_D_px=2 * math.sqrt(holeA / math.pi) if holeA > 0 else 0.0,
                         centroid_px=[float(xs.mean()), float(ys.mean())],
                         touches_border=touches))
    return rows


def plateau(rows, max_spread_pct=2.0, min_width=4):
    """Longest run of consecutive thresholds whose D_px spread stays under
    max_spread_pct.  Returns (rows_in_plateau, spread_pct) or (None, None)."""
    best = None
    for i in range(len(rows)):
        for j in range(len(rows), i + min_width - 1, -1):
            seg = rows[i:j]
            if len(seg) < min_width:
                continue
            D = np.array([r["D_px"] for r in seg])
            sp = 100 * (D.max() - D.min()) / D.mean()
            if sp <= max_spread_pct:
                if best is None or len(seg) > len(best[0]):
                    best = (seg, sp)
                break
    return best if best else (None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--box", required=True, help="x0,y0,x1,y1 crop containing ONLY the object")
    ap.add_argument("--thr", default="60,160", help="threshold sweep lo,hi")
    ap.add_argument("--px-per-mm", type=float, default=None)
    ap.add_argument("--px-per-mm-label", default="unstated")
    ap.add_argument("--expect-mm", type=float, default=None,
                    help="known diameter, for validating the METHOD against a standard object")
    ap.add_argument("--max-spread-pct", type=float, default=2.0)
    ap.add_argument("--label", default="object")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    path = a.image if os.path.isabs(a.image) else os.path.join(ROOT, "images", "airtag", a.image)
    lum = np.asarray(Image.open(path).convert("L")).astype(float)
    x0, y0, x1, y1 = (int(v) for v in a.box.split(","))
    sub = lum[y0:y1, x0:x1]
    tlo, thi = (int(v) for v in a.thr.split(","))

    print("m_silhouette.py -- inputs:")
    print(f"  image        {os.path.relpath(path, ROOT)} ({lum.shape[1]}x{lum.shape[0]})")
    print(f"  object       {a.label}")
    print(f"  crop box     {(x0, y0, x1, y1)}  ({x1-x0}x{y1-y0} px)")
    print(f"  threshold    swept {tlo}..{thi} luma, step 5")
    print(f"  scale basis  {a.px_per_mm} px/mm  [{a.px_per_mm_label}]")
    if a.expect_mm:
        print(f"  KNOWN SIZE   {a.expect_mm} mm -- this run VALIDATES the method")

    rows = sweep(sub, tlo, thi)
    if not rows:
        print("  CANNOT DETERMINE: no dark blob at any threshold in the sweep")
        sys.exit(2)
    for r in rows:
        flag = "  <-- blob touches the crop border, object not whole" if r["touches_border"] else ""
        print(f"    thr {r['thr']:3d}  area {r['area_px']:7d}  D {r['D_px']:7.2f} px"
              f"  enclosed hole D {r['hole_D_px']:6.2f} px{flag}")

    rows = [r for r in rows if not r["touches_border"]]
    if not rows:
        print("  CANNOT DETERMINE: the blob touches the crop border at every threshold "
              "-- the crop box does not contain the whole object")
        sys.exit(2)
    seg, sp = plateau(rows, a.max_spread_pct)
    if seg is None:
        D = np.array([r["D_px"] for r in rows])
        print(f"  CANNOT DETERMINE: no plateau. D varies {100*(D.max()-D.min())/D.mean():.1f}% "
              f"across the sweep, over the {a.max_spread_pct}% limit -- this edge is too soft "
              f"for the area method to have a threshold-independent answer.")
        sys.exit(2)

    D = np.array([r["D_px"] for r in seg])
    H = np.array([r["hole_D_px"] for r in seg])
    Dm, Dlo, Dhi = float(D.mean()), float(D.min()), float(D.max())
    print(f"\n  PLATEAU  thresholds {seg[0]['thr']}..{seg[-1]['thr']} ({len(seg)} steps), "
          f"D spread {sp:.2f}%")
    print(f"  D = {Dm:.2f} px  (range {Dlo:.2f} .. {Dhi:.2f})")
    print(f"  enclosed hole equivalent D = {H.mean():.2f} px (range {H.min():.2f} .. {H.max():.2f})")
    out = dict(tool="m_silhouette.py", image=os.path.relpath(path, ROOT), label=a.label,
               box=[x0, y0, x1, y1], threshold_sweep=[tlo, thi],
               plateau_thresholds=[seg[0]["thr"], seg[-1]["thr"]],
               plateau_spread_pct=round(sp, 3),
               D_px=round(Dm, 3), D_px_range=[round(Dlo, 3), round(Dhi, 3)],
               enclosed_hole_D_px=round(float(H.mean()), 3),
               enclosed_hole_D_px_range=[round(float(H.min()), 3), round(float(H.max()), 3)],
               centroid_px=[round(v, 2) for v in seg[len(seg)//2]["centroid_px"]],
               px_per_mm=a.px_per_mm, px_per_mm_label=a.px_per_mm_label,
               rows=rows)
    rc = 0
    if a.px_per_mm:
        s = a.px_per_mm
        out["D_mm"] = round(Dm / s, 4)
        out["D_mm_range"] = [round(Dlo / s, 4), round(Dhi / s, 4)]
        out["hole_D_mm"] = round(float(H.mean()) / s, 4)
        print(f"  -> D = {Dm/s:.3f} mm  ({Dlo/s:.3f} .. {Dhi/s:.3f})  "
              f"[at {s} px/mm, {a.px_per_mm_label}]")
        print(f"  -> enclosed hole equivalent D = {H.mean()/s:.3f} mm  (equivalent-circle only; "
              f"see m_board_outline.py if the hole is not round)")
        if a.expect_mm:
            err = 100 * (Dm / s - a.expect_mm) / a.expect_mm
            out["expect_mm"] = a.expect_mm
            out["error_vs_known_pct"] = round(err, 3)
            print(f"\n  METHOD VALIDATION against a {a.expect_mm} mm standard: "
                  f"measured {Dm/s:.3f} mm, error {err:+.2f}%")
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
