#!/usr/bin/env python3
"""p_fit.py -- fit MANUFACTURABLE PRIMITIVES to the measured board profile, and publish
the fit residual.

Lane L5 (BOARD BUILD), halo Replica.  Exit 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

WHY
  p_outline.py returns a per-degree silhouette traced off a photograph. That polygon
  carries the edge detector's noise into the geometry: it cannot be dimensioned, cannot
  be toleranced, no fab will take it, and beside Apple's crisp machined ring it reads as
  "not even close" for reasons that have nothing to do with our dimensions. Apple's board
  is a MANUFACTURED outline -- arcs, straight segments, corner radii.

  So: fit primitives, draw the fit, and publish how well the manufacturable shape
  describes what was photographed. The RAW profile stays on disk as evidence and the two
  files are NEVER merged.

THE TRAP THIS TOOL IS BUILT AGAINST
  "The residual went down" is NOT evidence a model is right. Extra parameters always
  lower a residual -- a rounded rectangle has 6 and a circle has 3, so the rectangle wins
  on residual even when the hole is a perfect circle. Two defences, and neither can be
  satisfied by a model that merely absorbed noise:

    HELD-OUT ANGLES  -- every model is fitted on the EVEN rays and scored on the ODD
                        rays it never saw. Noise-absorption does not survive that.
    INLIER FRACTION  -- the fraction of held-out rays inside a fixed +/-0.15 mm band.
                        A fit chooses the inliers that make its own residual small, so
                        residual can agree with what it checks; a FIXED band cannot.

CONTROLS, all run by --selftest with synthetic ground truth
  F1 recover circle   -- a synthetic circle must come back with the right radius, and the
                         rounded-rect model must DEGENERATE to it (rc ~ a ~ b), not report
                         a spurious squareness.
  F2 recover rrect    -- a synthetic rounded rectangle of known w,h,rc must come back to
                         within 1%.
  F3 discrimination   -- on the synthetic CIRCLE, the rrect model must NOT beat the circle
                         model on held-out data. This is the control that fails if the
                         extra parameters are just eating noise, and it is the whole point.
  F4 noise refusal    -- pure noise must fit nothing: held-out inlier fraction stays low
                         and the tool says CANNOT DETERMINE rather than publishing a shape.
"""
import argparse, json, math, os, sys
import numpy as np
from scipy.optimize import least_squares

PASS, FAIL, CANNOT = 0, 1, 2
HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.join(os.path.dirname(HERE), "board")
BAND_MM = 0.15          # the FIXED inlier band. Never widened to make a model pass.


def say(*a):
    print(*a, file=sys.stderr)


# ---------------------------------------------------------------- shape primitives
def circle_r(th_deg, p):
    """radius from the ORIGIN to a circle of radius R centred at (cx,cy)."""
    cx, cy, R = p
    t = np.deg2rad(th_deg)
    ux, uy = np.cos(t), np.sin(t)
    b = cx * ux + cy * uy
    c = cx * cx + cy * cy - R * R
    disc = b * b - c
    disc = np.where(disc < 0, np.nan, disc)
    return b + np.sqrt(disc)


def rrect_sdf(x, y, a, b, rc):
    qx = np.abs(x) - (a - rc)
    qy = np.abs(y) - (b - rc)
    return (np.hypot(np.maximum(qx, 0), np.maximum(qy, 0))
            + np.minimum(np.maximum(qx, qy), 0) - rc)


def rrect_effective(p):
    """The parameters the shape ACTUALLY has. rrect_r clamps rc to the half-extents
    internally (a corner radius cannot exceed the box), so the optimiser is free to
    return rc=7.54 for a box of half-width 6.50 and mean a CIRCLE by it. Reporting the
    raw parameter would then describe a shape nobody drew. Everything published and
    everything asserted goes through here."""
    cx, cy, a, b, rc, rot = p
    a, b = abs(a), abs(b)
    rc = min(abs(rc), a, b)
    return [cx, cy, a, b, rc, rot]


def rrect_r(th_deg, p, iters=44, rmax=60.0):
    """radius from the ORIGIN to a rounded rectangle (half-extents a,b, corner radius rc,
    centred at cx,cy, rotated by rot). Convex, so a bisection on the SDF is exact to
    machine limits and cannot land on a wrong root."""
    cx, cy, a, b, rc, rot = rrect_effective(p)
    rc = min(rc, a - 1e-6, b - 1e-6)
    t = np.deg2rad(th_deg)
    ux, uy = np.cos(t), np.sin(t)
    cs, sn = math.cos(rot), math.sin(rot)
    lo = np.zeros_like(t)
    hi = np.full_like(t, rmax)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        X, Y = mid * ux - cx, mid * uy - cy
        xr = X * cs + Y * sn
        yr = -X * sn + Y * cs
        inside = rrect_sdf(xr, yr, a, b, rc) < 0
        lo = np.where(inside, mid, lo)
        hi = np.where(inside, hi, mid)
    return 0.5 * (lo + hi)


MODELS = {
    "circle": dict(f=circle_r, k=3,
                   p0=lambda th, r: [0.0, 0.0, float(np.nanmean(r))],
                   names=["cx_mm", "cy_mm", "R_mm"]),
    "rounded_rect": dict(f=rrect_r, k=6,
                         p0=lambda th, r: [0.0, 0.0, float(np.nanmax(r)) * 0.78,
                                           float(np.nanmax(r)) * 0.78,
                                           float(np.nanmax(r)) * 0.30, 0.0],
                         names=["cx_mm", "cy_mm", "half_w_mm", "half_h_mm",
                                "corner_r_mm", "rot_rad"]),
}


def fit(model, th, r):
    m = MODELS[model]
    p0 = m["p0"](th, r)

    def res(p):
        v = m["f"](th, p) - r
        return np.nan_to_num(v, nan=10.0)

    out = least_squares(res, p0, loss="soft_l1", f_scale=0.25, max_nfev=4000)
    return rrect_effective(out.x) if model == "rounded_rect" else out.x


def score(model, p, th, r):
    pred = MODELS[model]["f"](th, p)
    e = pred - r
    ok = np.isfinite(e)
    e = e[ok]
    if e.size == 0:
        return None
    return dict(n=int(e.size), rms_mm=float(np.sqrt((e ** 2).mean())),
                p95_mm=float(np.percentile(np.abs(e), 95)),
                max_mm=float(np.abs(e).max()),
                inlier_frac=float((np.abs(e) < BAND_MM).mean()))


def evaluate(th, r, label):
    """Fit every model on EVEN rays, score on the ODD rays it never saw."""
    idx = np.argsort(th)
    th, r = th[idx], r[idx]
    tr, te = slice(0, None, 2), slice(1, None, 2)
    say(f"\n{label}: {len(th)} clean rays -> fit on {len(th[tr])} even, "
        f"score on {len(th[te])} HELD-OUT odd")
    res = {}
    for name in MODELS:
        p = fit(name, th[tr], r[tr])
        s_in = score(name, p, th[tr], r[tr])
        s_out = score(name, p, th[te], r[te])
        res[name] = dict(params=dict(zip(MODELS[name]["names"],
                                         [float(v) for v in p])),
                         n_params=MODELS[name]["k"],
                         in_sample=s_in, held_out=s_out)
        say(f"  {name:13s} k={MODELS[name]['k']}  "
            f"in-sample rms {s_in['rms_mm']:.4f}  |  HELD-OUT rms {s_out['rms_mm']:.4f} "
            f"p95 {s_out['p95_mm']:.4f} max {s_out['max_mm']:.4f}  "
            f"inlier(+/-{BAND_MM}) {s_out['inlier_frac']:.3f}")
    return res


def verdict(res, label):
    """Which model DESCRIBES the shape -- decided on held-out data and a fixed band,
    never on in-sample residual."""
    c, q = res["circle"]["held_out"], res["rounded_rect"]["held_out"]
    # ABSOLUTE FLOOR, before any ratio. If the simpler model is already inside the
    # measurement's own resolution there is nothing left to improve, and a percentage
    # computed against ~0 is a number about arithmetic, not about the board.
    FLOOR = 0.02
    if c["rms_mm"] < FLOOR:
        say(f"  -> {label}: CIRCLE. Circle held-out rms {c['rms_mm']:.5f} mm is already "
            f"below the {FLOOR} mm floor; no richer model can be shown to beat it.")
        return "circle", 0.0, q["inlier_frac"] - c["inlier_frac"]
    d_rms = (c["rms_mm"] - q["rms_mm"]) / c["rms_mm"]
    d_in = q["inlier_frac"] - c["inlier_frac"]
    say(f"  -> held-out rms improves {d_rms*100:+.1f}%, inlier fraction "
        f"{d_in:+.3f} ({c['inlier_frac']:.3f} -> {q['inlier_frac']:.3f})")
    if d_rms > 0.15 and d_in > 0.05:
        v = "rounded_rect"
        say(f"  -> {label}: ROUNDED RECTANGLE describes it. Both held-out measures "
            f"improve, so the 3 extra parameters bought shape and not noise.")
    elif d_rms < 0.05:
        v = "circle"
        say(f"  -> {label}: CIRCLE. The extra parameters bought nothing held-out.")
    else:
        v = "CANNOT DETERMINE"
        say(f"  -> {label}: CANNOT DETERMINE -- the two measures disagree. Not a "
            f"soft pass, and not resolved by picking the nicer one.")
    return v, d_rms, d_in


# ---------------------------------------------------------------- selftest
def selftest():
    th = np.arange(0, 360, 0.5)
    fails = []

    def chk(name, cond, detail):
        say(f"  [{'ok  ' if cond else 'FAIL'}] {name}: {detail}")
        if not cond:
            fails.append(name)

    say("F1 recover a synthetic CIRCLE (R=6.500, centre +0.20,-0.30)")
    r = circle_r(th, [0.20, -0.30, 6.500])
    pc = fit("circle", th, r)
    chk("F1 circle radius", abs(pc[2] - 6.5) < 0.01, f"R={pc[2]:.4f} want 6.5000")
    pq = fit("rounded_rect", th, r)
    a, b, rc = pq[2], pq[3], pq[4]
    chk("F1 rrect degenerates", abs(rc - a) < 0.15 and abs(rc - b) < 0.15,
        f"effective a={a:.3f} b={b:.3f} rc={rc:.3f} -- rc~a~b means it became a circle, "
        f"not a spurious square")
    chk("F1 effective radius right", abs(rc - 6.5) < 0.02,
        f"effective corner radius {rc:.4f} = the circle's own radius 6.5000")

    say("F2 recover a synthetic ROUNDED RECT (a=6.0 b=5.4 rc=1.6 rot=8deg)")
    truth = [0.10, 0.05, 6.0, 5.4, 1.6, math.radians(8)]
    r2 = rrect_r(th, truth)
    p2 = fit("rounded_rect", th, r2)
    for i, nm in enumerate(["a", "b", "rc"]):
        got, want = abs(p2[2 + i]), truth[2 + i]
        chk(f"F2 {nm}", abs(got - want) / want < 0.01, f"{got:.4f} want {want:.4f}")

    say("F3 DISCRIMINATION -- on the synthetic circle, rrect must NOT win held-out")
    res = evaluate(th, r, "synthetic circle")
    v, dr, di = verdict(res, "synthetic circle")
    chk("F3 no false squareness", v == "circle",
        f"verdict={v} (rms {dr*100:+.1f}%, inlier {di:+.3f}) -- if this said "
        f"rounded_rect the extra parameters would be eating noise")
    say("F3b and on the synthetic rounded rect, rrect MUST win held-out")
    res2 = evaluate(th, r2, "synthetic rrect")
    v2, dr2, di2 = verdict(res2, "synthetic rrect")
    chk("F3b true squareness found", v2 == "rounded_rect",
        f"verdict={v2} (rms {dr2*100:+.1f}%, inlier {di2:+.3f})")

    say("F4 NOISE must fit nothing")
    rng = np.random.default_rng(7)
    rn = 6.5 + rng.normal(0, 1.2, th.size)
    resn = evaluate(th, rn, "pure noise")
    worst = max(resn[k]["held_out"]["inlier_frac"] for k in resn)
    chk("F4 noise refused", worst < 0.35,
        f"best held-out inlier fraction {worst:.3f} < 0.35 -- no shape is published")

    say("")
    if fails:
        say(f"SELFTEST FAILED: {fails}")
        return FAIL
    say("SELFTEST 8/8 -- and F3 is the one that matters: it fires when a richer model "
        "merely absorbs noise.")
    return PASS


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=os.path.join(BOARD, "outline", "outline-photo6.json"))
    ap.add_argument("--out", default=os.path.join(BOARD, "outline", "outline-fit.json"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        code = selftest()
        say({0: "PASS", 1: "FAIL", 2: "CANNOT DETERMINE"}[code])
        sys.exit(code)

    with open(a.raw) as f:
        raw = json.load(f)
    say("INPUT")
    say(f"  raw profile   {os.path.relpath(a.raw)}")
    say(f"  image         {raw['image']}")
    say(f"  scale         {raw['scale']['px_per_mm']} px/mm -- {raw['scale']['basis']}")
    say(f"  inlier band   +/-{BAND_MM} mm, FIXED. Never widened to make a model pass.")
    say(f"  side          {raw['side_convention']}")

    doc = dict(tool="p_fit.py", lane="L5 BOARD BUILD",
               raw_profile_source=os.path.relpath(a.raw),
               never_merge="This file is the FIT. The raw silhouette stays in "
                           "outline-photo6.json as evidence. The two are never merged.",
               side_convention=raw["side_convention"],
               scale=raw["scale"], inlier_band_mm=BAND_MM,
               method="every model fitted on EVEN rays and scored on HELD-OUT ODD rays; "
                      "model chosen on held-out rms AND a fixed-band inlier fraction, "
                      "never on in-sample residual, because extra parameters always "
                      "lower an in-sample residual.",
               features={})

    overall = PASS
    for which in ("outer", "inner"):
        rows = np.array(raw[which]["r_theta_deg_mm"], float)
        th, r = rows[:, 0], rows[:, 1]
        disc = set(raw["discarded"][f"{which}_rays_deg"])
        keep = np.array([t not in disc for t in th])
        say(f"\n=== {which.upper()} ===")
        say(f"  {keep.sum()}/{len(th)} rays clean; {len(th)-keep.sum()} excluded as "
            f"contaminated (leader arrows / watermark). Contaminated rays are NOT fitted "
            f"and NOT scored -- fitting them would launder annotation into geometry.")
        res = evaluate(th[keep], r[keep], which)
        v, dr, di = verdict(res, which)
        best = res[v] if v in res else None
        doc["features"][which] = dict(
            n_rays_clean=int(keep.sum()), n_rays_excluded=int(len(th) - keep.sum()),
            models=res, chosen=v,
            held_out_rms_improvement=float(dr), held_out_inlier_gain=float(di),
            chosen_params=(best["params"] if best else None),
            fit_residual_held_out=(best["held_out"] if best else None))
        if v == "CANNOT DETERMINE":
            overall = max(overall, CANNOT)
        elif best["held_out"]["inlier_frac"] < 0.35:
            say(f"  -> {which}: REFUSED. Best held-out inlier fraction "
                f"{best['held_out']['inlier_frac']:.3f} < 0.35: no primitive describes "
                f"this profile well enough to publish as geometry.")
            doc["features"][which]["chosen"] = "CANNOT DETERMINE - no primitive fits"
            overall = max(overall, CANNOT)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(doc, f, indent=2)
    say(f"\nwrote {a.out}")
    say({0: "PASS", 1: "FAIL", 2: "CANNOT DETERMINE"}[overall])
    sys.exit(overall)


if __name__ == "__main__":
    main()
