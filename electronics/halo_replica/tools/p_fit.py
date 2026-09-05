#!/usr/bin/env python3
"""p_fit.py -- fit MANUFACTURABLE primitives to the measured board outline.

Lane L5 BOARD BUILD.  Exit code IS the verdict: 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

WHY THIS EXISTS
  The previous render drew the per-degree silhouette straight from the edge detector.
  That reproduces JPEG and detector noise AS BOARD GEOMETRY: it cannot be dimensioned,
  cannot be toleranced, cannot be made, and beside Apple's machined ring it reads wrong
  for reasons that have nothing to do with our dimensions.

  A real board edge is a routed path: arcs and straight segments.  This tool fits that
  and PUBLISHES THE RESIDUAL, which is worth more than the raw profile because it says
  how well a manufacturable shape describes what was photographed.

  The raw profile stays on disk untouched.  The fit is written to a DIFFERENT file.
  The two are never merged.

INPUT (stated, never guessed)
  metrology/outline-raw-oflynn-front.json   outer r(theta) in px, 1194 rays, centre in px
  scale px/mm passed on the command line or read from the handoff header

MODEL
  outer = circle(cx, cy, R) clipped by zero or more CHORDS (straight segments).
  A chord is admitted ONLY if a line fits its arc better than the circle does AND the
  inlier fraction separates.  "The residual went down" is not evidence -- extra
  parameters always lower a residual.

CONTROLS, and every one has been watched to fire
  N1 negative  --selftest: a synthetic PERFECT circle must yield ZERO chords.  A
               detector that invents a flat where there is none fabricates geometry.
  N2 positive  --selftest: a synthetic circle with a KNOWN chord must recover it to
               within 0.05 mm in offset and 1.0 deg in normal direction.  A detector
               that cannot find a flat it was handed cannot be trusted to find a real one.
  N3 separation: the chord model must beat the circle on BOTH residual and inlier
               fraction on the chord's own arc.  Residual alone can agree with itself.
  N4 break     --break-chord-mm D: displace every fitted chord outward by D mm and
               re-measure.  The residual MUST rise.  If it does not, the residual is
               not describing the chord.
"""
import argparse, json, math, os, sys
import numpy as np

PASS, FAIL, CANNOT = 0, 1, 2
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BOARD = os.path.join(ROOT, "board")

INLIER_MM = 0.15          # the band an inlier must sit in, stated once
CHORD_MIN_DEPTH_MM = 0.30 # a run must be at least this far INSIDE the circle
CHORD_MIN_ARC_DEG = 5.0   # ... and at least this wide, or it is detector noise


def say(*a):
    print(*a, file=sys.stderr)


# ---------------------------------------------------------------- primitives
def circle_fit(x, y, w=None):
    if w is None:
        w = np.ones_like(x)
    A = np.c_[x, y, np.ones_like(x)] * w[:, None]
    b = (x * x + y * y) * w
    s, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = s[0] / 2.0, s[1] / 2.0
    return cx, cy, math.sqrt(max(s[2] + cx * cx + cy * cy, 0.0))


def robust_circle(x, y, mask=None, iters=15):
    """IRLS circle fit.  `mask` excludes points known not to belong to the arc."""
    m = np.ones(len(x), bool) if mask is None else mask
    cx, cy, R = circle_fit(x[m], y[m])
    for _ in range(iters):
        res = np.hypot(x[m] - cx, y[m] - cy) - R
        s = 1.4826 * np.median(np.abs(res - np.median(res)))
        w = 1.0 / (1.0 + (res / (2.0 * s + 1e-9)) ** 2)
        cx, cy, R = circle_fit(x[m], y[m], w)
    return cx, cy, R


def line_tls(px, py):
    """Total-least-squares line.  Returns (unit normal, signed offset from origin)."""
    mx, my = px.mean(), py.mean()
    u = np.c_[px - mx, py - my]
    _, _, V = np.linalg.svd(u, full_matrices=False)
    d = V[0]
    n = np.array([-d[1], d[0]])
    off = mx * n[0] + my * n[1]
    if off < 0:                       # point the normal outward from the origin
        n, off = -n, -off
    resid = u @ n
    span = (u @ d)
    return n, off, resid, float(span.max() - span.min())


def model_r(theta, cx, cy, R, chords):
    """r(theta) of circle(cx,cy,R) clipped by each chord {n:(nx,ny), d:offset}."""
    ct, st = np.cos(theta), np.sin(theta)
    # circle, ray from ORIGIN (the board frame origin), centre offset (cx,cy)
    b = cx * ct + cy * st
    disc = b * b - (cx * cx + cy * cy - R * R)
    disc = np.maximum(disc, 0.0)
    r = b + np.sqrt(disc)
    for ch in chords:
        nx, ny, dd = ch["nx"], ch["ny"], ch["d"]
        den = nx * ct + ny * st
        with np.errstate(divide="ignore", invalid="ignore"):
            rc = np.where(den > 1e-9, dd / den, np.inf)
        r = np.minimum(r, rc)
    return r


def stats(res_mm):
    a = np.abs(res_mm)
    return dict(sd_mm=float(res_mm.std()), p95_mm=float(np.percentile(a, 95)),
                max_mm=float(a.max()), inlier_frac=float((a < INLIER_MM).mean()))


# ---------------------------------------------------------------- the fit

def _runs(inward, theta_deg, bridge=3):
    """Contiguous inward runs, allowing up to `bridge` non-inward samples inside a run.
    The raw profile has 246 of 1440 rays missing (the detector discarded them), so a
    run detector that breaks on the first gap SILENTLY LOSES REAL FLATS -- it lost a
    1.02 mm one at 101-118 deg the first time this was written."""
    out, i, n = [], 0, len(inward)
    while i < n:
        if inward[i]:
            j = i
            k = i
            while k + 1 < n:
                if inward[k + 1]:
                    k += 1
                    j = k
                else:
                    look = k + 1
                    gap = 0
                    while look < n and not inward[look] and gap < bridge:
                        look += 1
                        gap += 1
                    if look < n and inward[look]:
                        k = look
                        j = k
                    else:
                        break
            if theta_deg[j] - theta_deg[i] >= CHORD_MIN_ARC_DEG:
                out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out

def fit_outer(theta_deg, r_px, ppm, verbose=True):
    th = np.deg2rad(theta_deg)
    x, y = r_px * np.cos(th), r_px * np.sin(th)

    # pass 1: circle over everything, robustly
    cx, cy, R = robust_circle(x, y)
    res = (np.hypot(x - cx, y - cy) - R) / ppm

    # pass 2: find INWARD runs -- candidate straight segments
    runs = _runs(res < -CHORD_MIN_DEPTH_MM, theta_deg)

    # pass 3: refit the circle EXCLUDING those runs, so the flats do not drag R
    keep = np.ones(len(x), bool)
    for i, j in runs:
        keep[i:j + 1] = False
    if keep.sum() > 50:
        cx, cy, R = robust_circle(x, y, keep)
    res = (np.hypot(x - cx, y - cy) - R) / ppm

    # pass 4: re-detect on the refitted circle, then fit a LINE to each run
    runs = _runs(res < -CHORD_MIN_DEPTH_MM, theta_deg)

    chords, rejected = [], []
    for i, j in runs:
        px, py = x[i:j + 1], y[i:j + 1]
        n, off, lres, span = line_tls(px, py)
        line_sd = float(lres.std()) / ppm
        line_in = float((np.abs(lres) / ppm < INLIER_MM).mean())
        circ = res[i:j + 1]
        circ_sd = float(circ.std())
        circ_in = float((np.abs(circ) < INLIER_MM).mean())
        row = dict(
            arc_deg=[float(theta_deg[i]), float(theta_deg[j])],
            n_rays=int(j - i + 1),
            nx=float(n[0]), ny=float(n[1]),
            normal_deg=float(math.degrees(math.atan2(n[1], n[0])) % 360.0),
            d=float(off), offset_mm=float(off / ppm),
            chord_span_mm=float(span / ppm),
            line_resid_sd_mm=line_sd, line_inlier_frac=line_in,
            circle_resid_sd_mm_here=circ_sd, circle_inlier_frac_here=circ_in,
            max_depth_below_circle_mm=float(-circ.min()),
        )
        # N3 SEPARATION: both must move, and the inlier fraction is the discriminator
        if line_sd < circ_sd and line_in > circ_in + 0.25:
            row["admitted"] = True
            chords.append(row)
        else:
            row["admitted"] = False
            row["why_refused"] = (
                "a line does not separate from the circle on this arc: "
                f"line sd {line_sd:.4f} vs circle sd {circ_sd:.4f} mm, "
                f"inlier {line_in:.3f} vs {circ_in:.3f}. Extra parameters always "
                "lower a residual; without inlier separation this is not a flat.")
            rejected.append(row)

    # arcs where the detector found NO ray at all. The model is drawn across them
    # because a closed outline must close, but it is NOT measured there and the
    # picture says so. A 1.02 mm inward excursion at 115-118.5 deg sits on the edge
    # of the largest such gap; modelling a flat across a 13.5 deg hole in the data
    # would be inventing geometry, so it is REFUSED and reported here instead.
    gaps = []
    ts = np.sort(theta_deg)
    for k in range(len(ts)):
        a0 = ts[k]
        a1 = ts[(k + 1) % len(ts)] + (360.0 if k == len(ts) - 1 else 0.0)
        if a1 - a0 > 1.0:
            gaps.append([float(a0), float(a1 % 360.0), float(a1 - a0)])
    return dict(cx=float(cx), cy=float(cy), R=float(R), chords=chords,
                refused_chords=rejected, ppm=float(ppm),
                excluded_rays=int((~keep).sum()), unmeasured_arcs=gaps,
                unmeasured_deg=float(sum(g[2] for g in gaps)))


def measure(fit, theta_deg, r_px, ppm, chord_shift_mm=0.0):
    th = np.deg2rad(theta_deg)
    ch = [dict(c) for c in fit["chords"]]
    for c in ch:
        c["d"] = c["d"] + chord_shift_mm * ppm      # N4: move the flat on purpose
    pred = model_r(th, fit["cx"], fit["cy"], fit["R"], ch)
    return (pred - r_px) / ppm, pred



# ---------------------------------------------------------------- the hole
def _se_resid(p, P):
    cx, cy, a, b, n, phi = p
    c, s = math.cos(phi), math.sin(phi)
    dx, dy = P[:, 0] - cx, P[:, 1] - cy
    u = (c * dx + s * dy) / a
    v = (-s * dx + c * dy) / b
    f = (np.abs(u) ** n + np.abs(v) ** n) ** (1.0 / n)
    return (f - 1.0) * np.hypot(dx, dy)


def _ci_resid(p, P):
    return np.hypot(P[:, 0] - p[0], P[:, 1] - p[1]) - p[2]


def _hole_resid(P, cx, cy, a, b, n, phi):
    dx, dy = P[:, 0] - cx, P[:, 1] - cy
    c, s = math.cos(phi), math.sin(phi)
    u = (c * dx + s * dy) / a
    v = (-s * dx + c * dy) / b
    f = (np.abs(u) ** n + np.abs(v) ** n) ** (1.0 / n)
    return (f - 1.0) * np.hypot(dx, dy), np.degrees(np.arctan2(dy, dx)) % 360.0


def find_facets(P, cx, cy, a, b, n, phi, ppm, depth_mm=0.30):
    """The hole is not a smooth curve: straight FACETS fit parts of it far better than
    the superellipse does.  Same admission rule as the outer chords -- a facet is
    admitted only if a line separates from the superellipse on INLIER FRACTION, not
    merely on residual.
    Returns facets as {normal_deg, offset_mm} in the hole's own centre frame.
    """
    res_px, th = _hole_resid(P, cx, cy, a, b, n, phi)
    o = np.argsort(th)
    th, res, Q = th[o], res_px[o] / ppm, P[o]
    out, refused = [], []
    for sign in (+1, -1):
        for i, j in _runs(sign * res > depth_mm, th):
            px, py = Q[i:j + 1, 0] - cx, Q[i:j + 1, 1] - cy
            mx, my = px.mean(), py.mean()
            u = np.c_[px - mx, py - my]
            _, _, V = np.linalg.svd(u, full_matrices=False)
            dv = V[0]
            nv = np.array([-dv[1], dv[0]])
            off = mx * nv[0] + my * nv[1]
            if off < 0:
                nv, off = -nv, -off
            lres = u @ nv
            line_sd = float(lres.std()) / ppm
            line_in = float((np.abs(lres) / ppm < INLIER_MM).mean())
            se_sd = float(res[i:j + 1].std())
            se_in = float((np.abs(res[i:j + 1]) < INLIER_MM).mean())
            row = dict(arc_deg=[float(th[i]), float(th[j])], n_pts=int(j - i + 1),
                       normal_deg=float(math.degrees(math.atan2(nv[1], nv[0])) % 360.0),
                       offset_mm=float(off / ppm),
                       direction=("outward" if sign > 0 else "inward"),
                       line_resid_sd_mm=line_sd, line_inlier_frac=line_in,
                       superellipse_resid_sd_mm_here=se_sd,
                       superellipse_inlier_frac_here=se_in)
            # A straight edge can only BE the boundary within ~90 deg of its own
            # normal -- d/cos(theta-normal) diverges at 90. A line fitted to a short
            # noisy arc comes out nearly TANGENTIAL, and applying it then throws the
            # radius to infinity inside its own arc. That is exactly how the H3 floor
            # first came back at -221%: the detector was fabricating tangential facets
            # on a pure superellipse and they made the fit catastrophically worse.
            devs = np.abs(((th[i:j + 1] - row["normal_deg"] + 180) % 360) - 180)
            row["max_arc_to_normal_deg"] = float(devs.max())
            geometric_ok = devs.max() < 60.0
            if geometric_ok and line_sd < se_sd and line_in > se_in + 0.25:
                out.append(row)
            else:
                row["why_refused"] = (
                    ("this line is nearly TANGENTIAL to its own arc "
                     f"({devs.max():.1f} deg from its normal, limit 60) -- a straight "
                     "edge cannot be the boundary that far from its normal"
                     if not geometric_ok else
                     f"line sd {line_sd:.4f} vs superellipse {se_sd:.4f} mm, inlier "
                     f"{line_in:.3f} vs {se_in:.3f} -- no separation, so this is the "
                     "extra parameters talking and not a facet"))
                refused.append(row)
    return out, refused


# no EXTEND: see hole_r's docstring -- extending was tried twice and measured worse


def hole_r(theta_deg, a, b, n, phi_deg, facets):
    """r(theta): the superellipse, cut by each straight FACET.

    EACH FACET IS APPLIED ONLY ON ITS MEASURED ARC, and that is a decision with two
    rejected alternatives behind it, both MEASURED rather than argued:

      extending each facet to its natural crossing with the superellipse (+-25 deg,
      min for inward and max for outward) -- residual 0.3342 -> 0.4428 mm, WORSE,
      and H3 correctly turned NOT EARNED. An outward pocket's d/cos(th-n) grows
      without bound away from its normal, so max() is not self-limiting and the
      extension pushes the boundary out across arcs where the real edge is the curve.

      inward facets as GLOBAL half-plane clips (the operator the outer chords use)
      -- residual 0.3342 -> 0.4267 mm, also WORSE. The 5.746 mm facet spans only
      0.96 mm of edge; clipping globally with it cuts 0.6 mm off a 35 deg arc where
      the measured boundary is farther out.

    On-arc only gives 0.1987 mm. CONSEQUENCE, AND IT IS AN HONEST ONE: each facet
    ends in a radial STEP where its measured arc ends. A routed pocket really does
    have side walls, so a step is the right KIND of geometry -- but the arc ends are
    where the boundary crosses 0.30 mm from the superellipse, NOT where the wall is.
    The wall positions are NOT MEASURED and the step is drawn at the only place the
    data names.
    """
    th = np.asarray(theta_deg, float) % 360.0
    t = np.deg2rad(th)
    ph = math.radians(phi_deg)
    c, s = math.cos(ph), math.sin(ph)
    ct, st = np.cos(t), np.sin(t)
    u = (c * ct + s * st) / a
    v = (-s * ct + c * st) / b
    r = (np.abs(u) ** n + np.abs(v) ** n) ** (-1.0 / n)
    for f in facets:
        fn = math.radians(f["normal_deg"])
        den = math.cos(fn) * ct + math.sin(fn) * st
        a0, a1 = f["arc_deg"]
        span = (a1 - a0) % 360.0
        with np.errstate(divide="ignore", invalid="ignore"):
            rl = np.where(den > 1e-9, f["offset_mm"] / den, np.nan)
        win = ((th - a0) % 360.0) <= span              # the MEASURED arc, and no more
        r = np.where(win & np.isfinite(rl), rl, r)
    return r


def fit_hole(P, ppm):
    """Superellipse AND circle, both fitted, both reported.

    H2 -- THE CONTROL THAT MATTERS.  Two extra parameters always lower a residual.
    So the same pair of models is fitted to a SYNTHETIC CIRCLE carrying the same
    noise, and the improvement the superellipse buys THERE is the floor the real
    improvement has to clear.  Without that floor, 'the superellipse fits better'
    is a statement about parameter counting, not about the hole.
    """
    from scipy.optimize import least_squares
    mx, my = P[:, 0].mean(), P[:, 1].mean()
    # Bounds are derived from the POINTS' own scale, never from a pixel constant. They
    # were hardcoded for one photograph's ~730 px hole and refused a 108 px one outright.
    r0 = float(np.median(np.hypot(P[:, 0] - mx, P[:, 1] - my)))
    lo = [mx - 0.4 * r0, my - 0.4 * r0, 0.4 * r0, 0.4 * r0, 1.5, -3.2]
    hi = [mx + 0.4 * r0, my + 0.4 * r0, 1.7 * r0, 1.7 * r0, 6.0, 3.2]
    se = least_squares(_se_resid, [mx, my, r0, r0, 2.5, 0.0], args=(P,), bounds=(lo, hi))
    ci = least_squares(_ci_resid, [mx, my, r0], args=(P,))
    se_sd = float(_se_resid(se.x, P).std()) / ppm
    ci_sd = float(_ci_resid(ci.x, P).std()) / ppm
    real_gain = 1.0 - se_sd / ci_sd

    # H2 floor: a true circle, same point count, same residual scale
    rng = np.random.default_rng(11)
    th = np.linspace(0, 2 * math.pi, len(P), endpoint=False)
    R0 = ci.x[2]
    noise = rng.normal(0, ci_sd * ppm, len(P))
    Q = np.c_[mx + (R0 + noise) * np.cos(th), my + (R0 + noise) * np.sin(th)]
    lo2 = [mx - 0.4 * R0, my - 0.4 * R0, 0.4 * R0, 0.4 * R0, 1.5, -3.2]
    hi2 = [mx + 0.4 * R0, my + 0.4 * R0, 1.7 * R0, 1.7 * R0, 6.0, 3.2]
    se2 = least_squares(_se_resid, [mx, my, R0, R0, 2.5, 0.0], args=(Q,), bounds=(lo2, hi2))
    ci2 = least_squares(_ci_resid, [mx, my, R0], args=(Q,))
    floor = 1.0 - float(_se_resid(se2.x, Q).std()) / float(_ci_resid(ci2.x, Q).std())

    pinned = [abs(se.x[i] - lo[i]) < 1e-6 or abs(se.x[i] - hi[i]) < 1e-6 for i in range(6)]

    # ---- FACETS, and H3: the floor that keeps them honest.
    cx0, cy0, aa, bb, nn, pp = se.x
    facets, refused = find_facets(P, cx0, cy0, aa, bb, nn, pp, ppm)
    res0, th0 = _hole_resid(P, cx0, cy0, aa, bb, nn, pp)
    sd_se = float(res0.std()) / ppm
    rfit = hole_r(th0, aa / ppm, bb / ppm, nn, math.degrees(pp) % 360.0,
                  [dict(f) for f in facets])
    rmeas = np.hypot(P[:, 0] - cx0, P[:, 1] - cy0) / ppm
    sd_fac = float((rfit - rmeas).std())

    # H3 floor: the SAME detector on a synthetic PURE superellipse carrying the same
    # angular sampling and the same noise. Whatever it "finds" there is fabricated, and
    # whatever residual drop that fabrication buys is the floor the real drop must clear.
    # (The first version of this control built its synthetic points in the wrong frame
    # and returned a floor of -3836%. A control that returns a nonsense number is not a
    # control; it was rebuilt to generate points ON the fitted curve at the MEASURED
    # angles, which is checkable: with zero noise its own residual must be ~0.)
    rng2 = np.random.default_rng(23)
    a_mm, b_mm, phi_d = aa / ppm, bb / ppm, math.degrees(pp) % 360.0
    r_true = hole_r(th0, a_mm, b_mm, nn, phi_d, []) * ppm
    zero_chk = float(np.abs(np.hypot(
        (cx0 + r_true * np.cos(np.deg2rad(th0))) - cx0,
        (cy0 + r_true * np.sin(np.deg2rad(th0))) - cy0) - r_true).max())
    r_syn = r_true + rng2.normal(0, sd_se * ppm, len(th0))
    Psyn = np.c_[cx0 + r_syn * np.cos(np.deg2rad(th0)),
                 cy0 + r_syn * np.sin(np.deg2rad(th0))]
    fsyn, _ = find_facets(Psyn, cx0, cy0, aa, bb, nn, pp, ppm)
    sd_s0 = float((np.hypot(Psyn[:, 0] - cx0, Psyn[:, 1] - cy0) - r_true).std()) / ppm
    rfs = hole_r(th0, a_mm, b_mm, nn, phi_d, [dict(f) for f in fsyn])
    sd_s1 = float((rfs - np.hypot(Psyn[:, 0] - cx0, Psyn[:, 1] - cy0) / ppm).std())
    floor3 = 1.0 - sd_s1 / sd_s0 if sd_s0 else 0.0
    gain3 = 1.0 - sd_fac / sd_se if sd_se else 0.0

    return dict(
        centre_px=[float(se.x[0]), float(se.x[1])],
        two_a_mm=float(2 * se.x[2] / ppm), two_b_mm=float(2 * se.x[3] / ppm),
        n=float(se.x[4]), phi_deg=float(math.degrees(se.x[5]) % 180.0),
        any_parameter_pinned_at_its_bound=bool(any(pinned)),
        superellipse_resid_sd_mm=se_sd,
        circle_alternative_R_mm=float(ci.x[2] / ppm),
        circle_alternative_resid_sd_mm=ci_sd,
        improvement_frac=float(real_gain),
        H2_improvement_floor_from_parameter_count=float(floor),
        facets=facets, facets_refused=refused,
        facet_resid_sd_mm=sd_fac,
        superellipse_only_resid_sd_mm=sd_se,
        H3_facet_improvement_frac=float(gain3),
        H3_floor_from_fabricated_facets=float(floor3),
        H3_facets_fabricated_on_a_pure_superellipse=len(fsyn),
        H3_synthetic_generator_zero_noise_error_px=float(zero_chk),
        H3_synthetic_resid_sd_mm=float(sd_s0),
        H3_verdict=("EARNED" if (gain3 > 2.0 * floor3 and gain3 > 0.05) else
                    "NOT EARNED -- the facets do not beat what the same detector "
                    "fabricates on a shape that has none"),
        H2_verdict=("EARNED" if real_gain > 2.0 * max(floor, 1e-6) else
                    "NOT EARNED -- the superellipse's advantage over a circle is not "
                    "clearly larger than what two extra parameters buy on a pure circle"),
    )


# ---------------------------------------------------------------- controls
def selftest(break_which=None):
    """N1, N1b and N2.  `break_which` feeds each control the input that MUST make it
    fire, so the controls are watched failing rather than assumed to work.
      break=N1   the 'perfect circle' is given a real 1.4 mm flat -> N1 must report a chord
      break=N2   the 'known chord' input is a plain circle    -> N2 must fail to recover it
      break=N1b  the noise input is given a real 1.0 mm flat  -> N1b must fire
    """
    ok = True
    ppm = 106.313
    th = np.arange(0, 360, 0.25)
    t = np.deg2rad(th)

    # N1 negative: a perfect circle must yield NO chord
    R = 12.6 * ppm
    r = np.full_like(t, R)
    if break_which == "N1":
        nx0, ny0 = math.cos(math.radians(20.0)), math.sin(math.radians(20.0))
        den0 = nx0 * np.cos(t) + ny0 * np.sin(t)
        r = np.minimum(r, np.where(den0 > 1e-9, (R - 1.4 * ppm) / den0, np.inf))
    f = fit_outer(th, r, ppm)
    say(f"N1 negative (perfect circle): chords admitted = {len(f['chords'])} (want 0)")
    if f["chords"]:
        say("N1 FIRED: the fitter invented a flat where the input has none.")
        ok = False

    # N2 positive: a circle with a KNOWN chord must be recovered
    d_true, phi_true = 11.50 * ppm, 167.0
    nx, ny = math.cos(math.radians(phi_true)), math.sin(math.radians(phi_true))
    den = nx * np.cos(t) + ny * np.sin(t)
    rc = np.where(den > 1e-9, d_true / den, np.inf)
    r2 = np.minimum(np.full_like(t, R), rc)
    if break_which == "N2":
        r2 = np.full_like(t, R)          # no chord at all: N2 MUST fail to recover one
    f2 = fit_outer(th, r2, ppm)
    if len(f2["chords"]) != 1:
        say(f"N2 FIRED: {len(f2['chords'])} chords recovered from a single-chord input.")
        ok = False
    else:
        c = f2["chords"][0]
        do = abs(c["offset_mm"] - d_true / ppm)
        dphi = abs((c["normal_deg"] - phi_true + 180) % 360 - 180)
        say(f"N2 positive (chord at {d_true/ppm:.3f} mm, normal {phi_true:.1f} deg): "
            f"recovered {c['offset_mm']:.3f} mm / {c['normal_deg']:.2f} deg "
            f"-> err {do:.4f} mm, {dphi:.3f} deg")
        if do > 0.05 or dphi > 1.0:
            say("N2 FIRED: the fitter cannot recover a flat it was handed.")
            ok = False

    # N1b: a perfect circle plus gaussian pixel noise must STILL yield no chord
    rng = np.random.default_rng(7)
    r3 = R + rng.normal(0, 0.08 * ppm, t.shape)
    if break_which == "N1b":
        # a REAL straight flat buried in the noise. (A curved 0.5 mm Gaussian dent was
        # tried first and was correctly REFUSED by the N3 separation test -- a dent is
        # not a flat -- which is a second, unplanned demonstration that N3 has teeth.)
        nx1, ny1 = math.cos(math.radians(300.0)), math.sin(math.radians(300.0))
        den1 = nx1 * np.cos(t) + ny1 * np.sin(t)
        r3 = np.minimum(r3, np.where(den1 > 1e-9, (R - 1.0 * ppm) / den1, np.inf))
    f3 = fit_outer(th, r3, ppm)
    say(f"N1b negative (circle + 0.08 mm noise): chords = {len(f3['chords'])} (want 0)")
    if f3["chords"]:
        say("N1b FIRED: detector noise is being promoted to geometry -- the exact "
            "defect this tool was written to end.")
        ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=os.path.join(ROOT, "metrology",
                                                  "outline-raw-oflynn-front.json"))
    ap.add_argument("--hole", default=os.path.join(ROOT, "metrology",
                                                   "hole-oflynn-front.json"))
    ap.add_argument("--px-per-mm", type=float, default=None)
    ap.add_argument("--scale-basis", default=None)
    ap.add_argument("--out", default=os.path.join(BOARD, "outline", "outline-fit-oflynn.json"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-break", choices=["N1", "N1b", "N2"], default=None,
                    help="feed one control the input that MUST make it fire, and watch it")
    ap.add_argument("--break-chord-mm", type=float, default=0.0)
    a = ap.parse_args()

    if a.selftest or a.selftest_break:
        good = selftest(a.selftest_break)
        if a.selftest_break:
            if good:
                say(f"CONTROL {a.selftest_break} DID NOT FIRE on an input designed to "
                    "make it fire. The control is a decoration.")
                sys.exit(FAIL)
            say(f"control {a.selftest_break} fired as it must -- it is a real control")
            sys.exit(PASS)
        sys.exit(PASS if good else FAIL)

    if a.px_per_mm is None or a.scale_basis is None:
        say("CANNOT DETERMINE: --px-per-mm and --scale-basis are both required. "
            "A millimetre without its scale basis is not a measurement.")
        sys.exit(CANNOT)

    with open(a.raw) as f:
        raw = json.load(f)
    rt = np.array(raw["outer_r_theta"], float)
    th, r = rt[:, 0], rt[:, 1]
    ppm = a.px_per_mm

    say("INPUT")
    say(f"  raw outline   {os.path.relpath(a.raw, ROOT)}  ({len(r)} rays)")
    say(f"  hole fit      {os.path.relpath(a.hole, ROOT)}")
    say(f"  px_per_mm     {ppm}   basis: {a.scale_basis}")
    say("")

    say("N1/N2 controls first -- a fitter that has not been seen to fail is not known to work")
    if not selftest(None):
        say("FAIL: the fitter's own controls did not pass. No fit is published.")
        sys.exit(FAIL)
    say("")

    fit = fit_outer(th, r, ppm)
    res, pred = measure(fit, th, r, ppm)
    st = stats(res)

    # the plain circle, for the comparison that matters
    cres = (model_r(np.deg2rad(th), fit["cx"], fit["cy"], fit["R"], []) - r) / ppm
    cst = stats(cres)

    say(f"circle          c=({fit['cx']:.1f},{fit['cy']:.1f}) px  "
        f"R={fit['R']:.1f} px  D={2*fit['R']/ppm:.4f} mm")
    say(f"  circle alone : sd {cst['sd_mm']:.4f}  p95 {cst['p95_mm']:.4f}  "
        f"max {cst['max_mm']:.4f} mm  inliers(+-{INLIER_MM} mm) {cst['inlier_frac']:.3f}")
    for c in fit["chords"]:
        say(f"chord ADMITTED  {c['arc_deg'][0]:.2f}-{c['arc_deg'][1]:.2f} deg  "
            f"offset {c['offset_mm']:.4f} mm  normal {c['normal_deg']:.2f} deg  "
            f"span {c['chord_span_mm']:.3f} mm")
        say(f"                line sd {c['line_resid_sd_mm']:.4f} / inl "
            f"{c['line_inlier_frac']:.3f}   vs circle sd "
            f"{c['circle_resid_sd_mm_here']:.4f} / inl {c['circle_inlier_frac_here']:.3f}")
    for c in fit["refused_chords"]:
        say(f"chord REFUSED   {c['arc_deg'][0]:.2f}-{c['arc_deg'][1]:.2f} deg -- "
            f"{c['why_refused']}")
    say(f"  circle+chords: sd {st['sd_mm']:.4f}  p95 {st['p95_mm']:.4f}  "
        f"max {st['max_mm']:.4f} mm  inliers {st['inlier_frac']:.3f}")

    # N4 -- move the flats and watch the residual rise
    n4 = None
    if fit["chords"]:
        bres, _ = measure(fit, th, r, ppm, chord_shift_mm=0.30)
        bst = stats(bres)
        n4 = dict(shift_mm=0.30, sd_before=st["sd_mm"], sd_after=bst["sd_mm"],
                  inlier_before=st["inlier_frac"], inlier_after=bst["inlier_frac"])
        say(f"N4 break: chords displaced +0.30 mm -> sd {st['sd_mm']:.4f} -> "
            f"{bst['sd_mm']:.4f} mm, inliers {st['inlier_frac']:.3f} -> "
            f"{bst['inlier_frac']:.3f}")
        if bst["sd_mm"] <= st["sd_mm"]:
            say("N4 FIRED: displacing the flat did NOT worsen the fit, so the "
                "residual is not describing the flat.")
            sys.exit(FAIL)

    if a.break_chord_mm:
        bres, _ = measure(fit, th, r, ppm, chord_shift_mm=a.break_chord_mm)
        say(f"--break-chord-mm {a.break_chord_mm}: sd -> {stats(bres)['sd_mm']:.4f} mm")

    with open(a.hole) as f:
        hole = json.load(f)
    HP = np.array(hole["boundary"], float)[:, 1:3]
    hf = fit_hole(HP, ppm)
    say("")
    say(f"hole superellipse  centre offset from board centre "
        f"{math.hypot(hf['centre_px'][0]-raw['outer_centre'][0], hf['centre_px'][1]-raw['outer_centre'][1])/ppm:.3f} mm")
    say(f"  2a {hf['two_a_mm']:.4f} mm  2b {hf['two_b_mm']:.4f} mm  n {hf['n']:.4f}  "
        f"phi {hf['phi_deg']:.2f} deg  resid sd {hf['superellipse_resid_sd_mm']:.4f} mm")
    say(f"  circle alternative R {hf['circle_alternative_R_mm']:.4f} mm  "
        f"resid sd {hf['circle_alternative_resid_sd_mm']:.4f} mm")
    say(f"  facets: {len(hf['facets'])} admitted, {len(hf['facets_refused'])} refused; "
        f"resid sd {hf['superellipse_only_resid_sd_mm']:.4f} -> "
        f"{hf['facet_resid_sd_mm']:.4f} mm")
    for f in hf["facets"]:
        say(f"    {f['direction']:7s} {f['arc_deg'][0]:6.1f}-{f['arc_deg'][1]:6.1f} deg  "
            f"offset {f['offset_mm']:.3f} mm  normal {f['normal_deg']:.1f} deg  "
            f"line sd {f['line_resid_sd_mm']:.4f}/inl {f['line_inlier_frac']:.2f} vs "
            f"SE {f['superellipse_resid_sd_mm_here']:.4f}/inl "
            f"{f['superellipse_inlier_frac_here']:.2f}")
    say(f"  H3: facets buy {hf['H3_facet_improvement_frac']*100:.2f}% vs a floor of "
        f"{hf['H3_floor_from_fabricated_facets']*100:.2f}% "
        f"({hf['H3_facets_fabricated_on_a_pure_superellipse']} facets fabricated on a "
        f"PURE superellipse) -> {hf['H3_verdict']}")
    say(f"  H2: real improvement {hf['improvement_frac']*100:.2f}% vs "
        f"parameter-count floor {hf['H2_improvement_floor_from_parameter_count']*100:.2f}% "
        f"-> {hf['H2_verdict']}")
    hole_out = dict(hf)
    hole_out.update({
        "primitive": "superellipse",
        "state": "PARTIALLY DETERMINED -- NO single hole diameter is published",
        "why": ("three fits disagree on the exponent and they disagree in DIFFERENT "
                "directions: FCC photo 6 gives n=2.70, L1's fit in this frame pinned n "
                "at its 2.00 bound, and this refit of the SAME boundary points gives "
                f"n={hf['n']:.3f}. A rounded square is n=4, a circle/ellipse is n=2."),
        "refit_note": ("refitted here from hole-oflynn-front.json's own `boundary` "
                       "points because that file's `centre_px` is 2.76 mm from the "
                       "board centre while its boundary points imply 0.62 mm -- the "
                       "two fields disagree, so the points were used and the stated "
                       "centre was not. REPORTED UPSTREAM, not edited."),
        "L1_stated_for_contrast": {"two_a_mm": hole["two_a_mm"],
                                   "two_b_mm": hole["two_b_mm"], "n": hole["n"],
                                   "phi_deg": hole["phi_deg"],
                                   "centre_px": hole["centre_px"],
                                   "residual_sd_mm": hole["residual_sd_mm"]},
        "source_points": os.path.relpath(a.hole, ROOT),
        "n_boundary_points": int(len(HP)),
    })

    out = {
        "tool": "p_fit.py",
        "run_utc": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lane": "L5 BOARD BUILD",
        "what_this_is": (
            "FITTED MANUFACTURABLE PRIMITIVES, not samples. The raw per-degree profile "
            "lives in metrology/outline-raw-oflynn-front.json and is NEVER merged into "
            "this file."),
        "side_convention": "the side carrying the SoC and the shield can",
        "frame": {"origin": "board centre in oflynn-backside-fullres.jpeg, "
                            "transferred from FCC photo 6 through c_register's homography",
                  "origin_px": raw["outer_centre"],
                  "axes": "+x right, +y DOWN (image convention); theta from +x through +y"},
        "scale": {"px_per_mm": ppm, "basis": a.scale_basis},
        "source_raw": os.path.relpath(a.raw, ROOT),
        "rays": int(len(r)),
        "outer": {
            "primitive": "circle clipped by straight chords",
            "circle_centre_px": [fit["cx"], fit["cy"]],
            "circle_centre_mm": [fit["cx"] / ppm, fit["cy"] / ppm],
            "circle_R_px": fit["R"],
            "circle_diameter_mm": 2 * fit["R"] / ppm,
            "diameter_state": ("DERIVED, NOT INDEPENDENT -- this millimetre inherits the "
                               "same registration scale as every other number in this "
                               "frame. It is a shape result, not a third opinion on the OD."),
            "chords": fit["chords"],
            "chords_refused": fit["refused_chords"],
            "fit_residual_all_rays": st,
            "circle_only_residual_all_rays": cst,
            "N4_break_control": n4,
            "inlier_band_mm": INLIER_MM,
            "unmeasured_arcs_deg": fit["unmeasured_arcs"],
            "unmeasured_total_deg": fit["unmeasured_deg"],
            "unmeasured_note": ("no ray exists on these arcs. The outline is drawn "
                                "across them so it closes, and drawn in the PROVISIONAL "
                                "colour so the picture says where it is guessing."),
        },
        "inner": hole_out,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=2)
    say(f"\nwrote {os.path.relpath(a.out, ROOT)}")

    if not fit["chords"]:
        say("CANNOT DETERMINE: no straight segment separated from the circle. "
            "The outline is published as a plain circle and that is a weaker claim.")
        sys.exit(CANNOT)
    if st["inlier_frac"] <= cst["inlier_frac"]:
        say("FAIL: the fitted model does not beat the plain circle on inlier fraction.")
        sys.exit(FAIL)
    say("PASS")
    sys.exit(PASS)


if __name__ == "__main__":
    main()
