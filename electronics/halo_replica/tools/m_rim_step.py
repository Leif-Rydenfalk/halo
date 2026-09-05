#!/usr/bin/env python3
"""m_rim_step.py -- is the measured outer edge the PCB SUBSTRATE, or the GASKET?

L1 PHOTOGRAPH METROLOGY lane, halo Replica.
SIDE NAMING: FRONT = the COMPONENT side.

THE QUESTION, AND WHY IT IS THE BIGGEST REMAINING SYSTEMATIC.  A grey fibrous
material laps OVER the board's edge -- the same material that defeated luminance
edge-finding in M01 Sec 2 and that E01 identified as a conductive gasket or
adhesive.  Every outer-diameter number this lane has published came from the
steepest luma gradient on a radial ray.  If that gradient is the GASKET's outer
boundary rather than the substrate's, then every OD is too large, in BOTH
photographs, by the same amount -- and their 0.40% agreement would not detect it,
because a shared bias is not a disagreement.  It is additive: a gasket can only
make the board look bigger.

THE MEASUREMENT.  Cast rays outward, locate the edge exactly as m_outline_fit
does (steepest luma gradient), then sample luma at fixed offsets AROUND that edge
and average across all angles WITH THE EDGE ALIGNED.  Edge-aligned averaging is
the point: a real two-step structure survives averaging over hundreds of rays
because it sits at the same offset every time, while shading and texture do not.

WHAT A GASKET LOOKS LIKE:  dark substrate -> a GREY PLATEAU -> bright paper.
Two steps with a flat between them.  A bare substrate edge gives ONE step.

The resolution table (M06) predicts the answer per photograph, and the prediction
is printed before the result so it cannot be fitted after the fact.

Exit 0 resolved, 2 CANNOT DETERMINE.
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import m_outline_fit as OF


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--raw", required=True, help="outline-raw-*.json for this image")
    ap.add_argument("--px-per-mm", type=float, required=True)
    ap.add_argument("--genuine-px-per-mm", type=float, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--inner-px", type=float, default=None, help="how far inside the edge to sample")
    ap.add_argument("--outer-px", type=float, default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    path = a.image if os.path.isabs(a.image) else os.path.join(ROOT, "images", "airtag", a.image)
    lum = np.asarray(Image.open(path).convert("L")).astype(float)
    raw = json.load(open(a.raw))
    cx, cy = raw["outer_centre"]
    P = np.array(raw["outer_r_theta"], float)
    s, g = a.px_per_mm, a.genuine_px_per_mm
    inner = a.inner_px if a.inner_px else 0.9 * s      # ~0.9 mm inside
    outer = a.outer_px if a.outer_px else 0.9 * s
    step = 0.25

    print(f"m_rim_step.py -- {a.label}")
    print(f"  image   {os.path.relpath(path, ROOT)}")
    print(f"  edge    {len(P)} rays from {os.path.basename(a.raw)} "
          f"(run {raw.get('run_utc')}, git {raw.get('git_rev')})")
    print(f"  scale   {s:.3f} stored px/mm, {g:.1f} GENUINE px/mm (M06)")
    print(f"  PREDICTION BEFORE THE RESULT: a 0.3 mm gasket lip is "
          f"{0.3*g:.1f} genuine px here. A step needs about 2 genuine px to exist "
          f"at all, so this is {'RESOLVABLE' if 0.3*g >= 2 else 'BELOW THE RESOLUTION'}.")

    offs = np.arange(-inner, outer + step, step)
    acc = np.zeros(len(offs)); cnt = 0
    for th, r in P:
        A = math.radians(th)
        rr = r + offs
        v = OF.bilinear(lum, cx + rr * math.cos(A), cy + rr * math.sin(A))
        if not np.all(np.isfinite(v)):
            continue
        acc += v; cnt += 1
    prof = acc / cnt
    print(f"  edge-aligned mean over {cnt}/{len(P)} rays")
    print(f"\n  offset_mm   luma      (0.00 = the edge this lane published)")
    for i in range(0, len(offs), max(1, int(round(0.05 * s / step)))):
        bar = "#" * int(prof[i] / 6)
        print(f"  {offs[i]/s:+8.3f}  {prof[i]:6.1f}  {bar}")

    d1 = np.gradient(prof)
    k = max(3, int(round(0.03 * s / step)) | 1)
    d1s = np.convolve(d1, np.ones(k) / k, mode="same")
    m = max(4, int(round(0.05 * s / step)))
    core = d1s[m:-m]
    pk1 = int(np.argmax(core)) + m
    supp = np.ones(len(d1s), bool)
    w = max(2, int(round(0.10 * s / step)))
    supp[max(0, pk1 - w):pk1 + w + 1] = False
    cand = np.where(supp)[0]
    cand = cand[(cand >= m) & (cand < len(d1s) - m)]
    pk2 = cand[int(np.argmax(d1s[cand]))] if len(cand) else None
    r1, r2 = float(d1s[pk1]), float(d1s[pk2]) if pk2 is not None else 0.0
    print(f"\n  strongest luma rise at {offs[pk1]/s:+.3f} mm, slope {r1:.2f} luma/sample")
    if pk2 is not None:
        print(f"  next    luma rise at {offs[pk2]/s:+.3f} mm, slope {r2:.2f} "
              f"({100*r2/r1:.0f}% of the first), separated by "
              f"{abs(offs[pk2]-offs[pk1])/s:.3f} mm")
    sep_mm = abs(offs[pk2] - offs[pk1]) / s if pk2 is not None else 0.0
    sep_gen = sep_mm * g
    two_step = (pk2 is not None and r2 > 0.45 * r1 and sep_gen >= 2.0)
    print(f"\n  a SECOND step would have to clear 45% of the first AND be at least "
          f"2 genuine px away ({2.0/g:.3f} mm).")
    print(f"  second/first {100*r2/r1:.0f}%, separation {sep_mm:.3f} mm = "
          f"{sep_gen:.1f} genuine px")
    if two_step:
        print(f"\n  TWO STEPS RESOLVED. The published edge sits at {offs[pk1]/s:+.3f} mm; "
              f"the other boundary is {(offs[pk2]-offs[pk1])/s:+.3f} mm from it. "
              f"If the outer one is the gasket, the substrate OD is smaller by "
              f"{2*abs(offs[pk2]-offs[pk1])/s:.3f} mm.")
        rc = 0
    else:
        print(f"\n  CANNOT DETERMINE: substrate and gasket are ONE boundary at this "
              f"resolution. No second step clears the gate, so this photograph cannot "
              f"say whether the published edge is the substrate or the gasket lip.")
        rc = 2
    if a.json:
        json.dump(dict(tool="m_rim_step.py", label=a.label,
                       image=os.path.relpath(path, ROOT), px_per_mm=s,
                       genuine_px_per_mm=g, rays_used=cnt,
                       predicted_gasket_lip_genuine_px=round(0.3 * g, 2),
                       peak1_offset_mm=round(float(offs[pk1] / s), 4), peak1_slope=r1,
                       peak2_offset_mm=(round(float(offs[pk2] / s), 4) if pk2 is not None else None),
                       peak2_slope=r2, separation_mm=round(sep_mm, 4),
                       separation_genuine_px=round(sep_gen, 2),
                       verdict="TWO STEPS" if two_step else "CANNOT DETERMINE",
                       profile=[[round(float(o / s), 4), round(float(p), 2)]
                                for o, p in zip(offs, prof)]),
                  open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
