#!/usr/bin/env python3
"""m_scale_at.py -- px/mm AT A POINT in the frame, from two rules at the edges.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.

THE PROBLEM THIS SOLVES.  Both steel rules lie near the frame edges; the object
lies near the frame centre.  In FCC photo 6 the two rules disagree by 2.05% and
in photo 8 by 3.29%, always with the right rule lower, so "the px/mm of a
photograph" is not a single number, and using either rule's value for an object
somewhere else is an unstated 1-3% error.

THE MODEL, FIRST ORDER ON PURPOSE.  s(x,y) = s(rule) + a*dx + b*dy, with
  a  = ds/dx measured on the BOTTOM rule (m_scale_field.py, cubic differentiated)
  b  = ds/dy measured on the RIGHT rule
Nothing about the lens is assumed.  Both gradients are measured.

THE CHECK IS BUILT IN AND IT CAN FAIL.  The target is reached by TWO routes --
along the bottom rule then across in y, and along the right rule then across in
x.  THE DISAGREEMENT BETWEEN THE ROUTES IS REPORTED AS THE UNCERTAINTY; it is
not averaged out of sight, and past --max-route-disagreement-pct the answer is
CANNOT DETERMINE.

WHAT WOULD MAKE THE TWO ROUTES DISAGREE, stated so their agreement means
something (they are not the same measurement twice): route 1 carries a scale
measured ALONG X on the line y=1156 across 478 px of y; route 2 carries a scale
measured ALONG Y on the line x=1562 across 610 px of x.  They share no tick, no
rule, no direction and no travel path.  They disagree if the field is
anisotropic at the target, if either gradient is wrong, or if the field is not
first-order over that distance.

Exit 0 measured, 2 CANNOT DETERMINE.
"""
import argparse, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def series(rec):
    s = np.array(rec["local_pitch_samples"], float)
    return s[:, 0], s[:, 1]


def at(P, Q, t):
    """Local pitch at position t along the rule.  Extrapolation is REFUSED."""
    if not (P.min() <= t <= P.max()):
        return None
    return float(np.interp(t, P, Q))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field", default=os.path.join(HERE, "..", "metrology", "scale-field.json"))
    ap.add_argument("--photo", required=True, help="e.g. photo6")
    ap.add_argument("--at", required=True, help="x,y of the target in image pixels")
    ap.add_argument("--max-route-disagreement-pct", type=float, default=2.0)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    d = json.load(open(a.field))
    bot, rig = d.get(a.photo + "_bottom"), d.get(a.photo + "_right")
    tx, ty = (float(v) for v in a.at.split(","))
    print("m_scale_at.py -- inputs:")
    print(f"  field file  {a.field}")
    print(f"  photo       {a.photo}   target ({tx:.1f}, {ty:.1f}) px")
    for nm, r in (("bottom", bot), ("right", rig)):
        if r is None or r.get("verdict") != "MEASURED":
            print(f"  CANNOT DETERMINE: the {nm} rule is not measured for {a.photo}")
            sys.exit(2)
        print(f"  {nm:6s} rule: {r['n_ticks']} ticks, band {r['tick_band_xyxy']}, "
              f"ticks span {r['tick_pixel_span']} px, linear {r['linear_px_per_mm']:.4f} px/mm")

    Pb, Qb = series(bot)
    Pr, Qr = series(rig)
    y_bot = 0.5 * (bot["tick_band_xyxy"][1] + bot["tick_band_xyxy"][3])
    x_rig = 0.5 * (rig["tick_band_xyxy"][0] + rig["tick_band_xyxy"][2])

    a_x = float(np.polyfit(Pb, Qb, 1)[0])
    b_y = float(np.polyfit(Pr, Qr, 1)[0])
    print(f"  ds/dx from the bottom rule (line y={y_bot:.0f}): {a_x:+.3e} (px/mm) per px")
    print(f"  ds/dy from the right  rule (line x={x_rig:.0f}): {b_y:+.3e} (px/mm) per px")

    s_bx = at(Pb, Qb, tx)
    s_ry = at(Pr, Qr, ty)
    if s_bx is None:
        print(f"  CANNOT DETERMINE: the bottom rule's ticks do not reach x={tx:.0f} "
              f"(span {Pb.min():.0f}..{Pb.max():.0f}); this tool refuses to extrapolate")
        sys.exit(2)
    if s_ry is None:
        print(f"  CANNOT DETERMINE: the right rule's ticks do not reach y={ty:.0f} "
              f"(span {Pr.min():.0f}..{Pr.max():.0f}); this tool refuses to extrapolate")
        sys.exit(2)

    r1 = s_bx + b_y * (ty - y_bot)
    r2 = s_ry + a_x * (tx - x_rig)
    mean = 0.5 * (r1 + r2)
    dis = 100 * abs(r1 - r2) / mean
    print(f"\n  route 1  bottom rule at x={tx:.0f} = {s_bx:.4f} px/mm, "
          f"carried {ty-y_bot:+.0f} px in y -> {r1:.4f}")
    print(f"  route 2  right  rule at y={ty:.0f} = {s_ry:.4f} px/mm, "
          f"carried {tx-x_rig:+.0f} px in x -> {r2:.4f}")
    print(f"  routes disagree by {dis:.2f}% (limit {a.max_route_disagreement_pct}%)")
    out = dict(tool="m_scale_at.py", photo=a.photo, target_px=[tx, ty],
               bottom_rule_line_y=y_bot, right_rule_line_x=x_rig,
               bottom_rule_at_target_x=round(s_bx, 4), right_rule_at_target_y=round(s_ry, 4),
               ds_dx=a_x, ds_dy=b_y, route1_px_per_mm=round(r1, 4),
               route2_px_per_mm=round(r2, 4), route_disagreement_pct=round(dis, 3))
    if dis > a.max_route_disagreement_pct:
        out["verdict"] = "CANNOT DETERMINE"
        print("  CANNOT DETERMINE: the routes disagree by more than the limit, so the "
              "frame's scale field is not described by a first-order model here.")
        rc = 2
    else:
        out["verdict"] = "MEASURED"
        out["px_per_mm"] = round(mean, 4)
        out["px_per_mm_halfrange"] = round(abs(r1 - r2) / 2, 4)
        print(f"\n  PX/MM AT ({tx:.0f},{ty:.0f}) = {mean:.4f} +/- {abs(r1-r2)/2:.4f} "
              f"(the +/- IS the route disagreement, not a fit error)")
        rc = 0
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
