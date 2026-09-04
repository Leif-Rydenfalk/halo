#!/usr/bin/env python3
"""m_scale_field.py -- is the px/mm CONSTANT across the frame?  Measure it.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.

WHY THIS EXISTS.  m_ruler_calib.py returns ONE px/mm per rule, and the two
rules in the same photograph disagree by 1.7-3.3%.  Averaging that away would
be inventing a number.  The disagreement is a measurement of the imaging
system, so measure it: fit a CUBIC to tick position vs tick index along each
rule and differentiate -- that gives local px/mm as a function of position
ALONG that rule, with no model of the lens assumed.

The board sits near the image centre; both rules sit near frame edges.  So the
question that decides every millimetre downstream is: does px/mm rise or fall
towards the centre, and by how much.

Prints its inputs.  Raw output to JSON.
"""
import argparse, json, os
import numpy as np
import m_ruler_calib as R

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = R.ROOT


def local_pitch(path, name, axis, along, search):
    img = R.load_gray(path)
    edge = R.find_edge(img, axis, search, along)
    a0, a1 = along
    best = None
    for start in range(4, 26, 2):
        for depth in (18, 24, 30):
            o0, o1 = edge + start, edge + start + depth
            box = (a0, o0, a1, o1) if axis == "x" else (o0, a0, o1, a1)
            try:
                d, _, ang = R.band_signal(img, box, axis)
                _, snr = R.fft_pitch(d, 8.0, 40.0)
            except Exception:
                continue
            if best is None or snr > best[0]:
                best = (snr, box)
    box = best[1]
    fit, ang, snr, p0, n = R.comb(img, box, axis, 8.0, 40.0)
    if fit is None:
        return dict(name=name, verdict="CANNOT DETERMINE", reason="no comb")
    pos, idx = np.asarray(fit["pos"], float), np.asarray(fit["idx"], float)
    if fit["n"] / (fit["span"] + 1) < 0.85:
        return dict(name=name, verdict="CANNOT DETERMINE",
                    reason=f"tick coverage {fit['n']}/{fit['span']+1} too low to trust "
                           f"the integer index assignment")
    out = dict(name=name, verdict="MEASURED",
               image=os.path.relpath(path, ROOT), axis=axis,
               tick_band_xyxy=list(box), n_ticks=fit["n"], span_mm=fit["span"],
               linear_px_per_mm=fit["pitch"], linear_resid_sd_px=fit["sd"])
    for deg, key in ((1, "poly1"), (2, "poly2"), (3, "poly3")):
        c = np.polyfit(idx, pos, deg)
        r = pos - np.polyval(c, idx)
        out[key] = dict(coeffs=[float(v) for v in c], resid_sd_px=float(r.std(ddof=deg + 1)),
                        resid_max_px=float(np.abs(r).max()))
    c3 = np.polyfit(idx, pos, 3)
    d3 = np.polyder(c3)
    # local pitch sampled at each tick, tabulated against the tick's PIXEL position
    samp = [(float(np.polyval(c3, i)), float(np.polyval(d3, i))) for i in idx]
    out["local_pitch_samples"] = [[round(p, 1), round(q, 4)] for p, q in samp]
    P = np.array([s[0] for s in samp]); Q = np.array([s[1] for s in samp])
    out["local_pitch_at"] = {}
    for label, target in (("frame_centre_1067" if axis == "x" else "frame_centre_800",
                           1067.0 if axis == "x" else 800.0),
                          ("rule_start", float(P.min())), ("rule_end", float(P.max()))):
        if P.min() <= target <= P.max():
            out["local_pitch_at"][label] = round(float(np.interp(target, P, Q)), 4)
        else:
            out["local_pitch_at"][label] = None
    out["tick_pixel_span"] = [round(float(P.min()), 1), round(float(P.max()), 1)]
    out["pitch_range_px_per_mm"] = [round(float(Q.min()), 4), round(float(Q.max()), 4)]
    out["pitch_variation_pct"] = round(100 * (Q.max() - Q.min()) / Q.mean(), 3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    print("m_scale_field.py -- local px/mm along each rule (cubic fit, differentiated)")
    out = {}
    for k, (fn, axis, along, search) in R.RULES.items():
        r = local_pitch(os.path.join(R.IMGDIR, fn), k, axis, along, search)
        out[k] = r
        if r["verdict"] != "MEASURED":
            print(f"  {k:16s} {r['verdict']}: {r['reason']}")
            continue
        print(f"  {k:16s} {os.path.basename(r['image'])} band {r['tick_band_xyxy']}")
        print(f"      linear fit  {r['linear_px_per_mm']:.4f} px/mm, resid sd {r['linear_resid_sd_px']:.3f} px")
        print(f"      resid sd by degree: 1={r['poly1']['resid_sd_px']:.3f}  "
              f"2={r['poly2']['resid_sd_px']:.3f}  3={r['poly3']['resid_sd_px']:.3f} px")
        print(f"      local pitch spans {r['pitch_range_px_per_mm']} px/mm "
              f"= {r['pitch_variation_pct']:.2f}% across the rule")
        print(f"      at points: {r['local_pitch_at']}")
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")


if __name__ == "__main__":
    main()
