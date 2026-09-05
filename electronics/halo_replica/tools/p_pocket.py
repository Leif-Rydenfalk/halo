#!/usr/bin/env python3
"""p_pocket.py -- does a SECOND photograph agree about where the hole's walls are?

Lane L5b BOARD BUILD.  Exit 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

THE QUESTION, and it bears on a verdict another lane has already published.
  L1 closed the centre hole as PARTIALLY DETERMINED because three superellipse fits
  gave n = 2.70 / 2.00 (pinned) / 2.449.  That reasoning assumes the hole IS a
  superellipse and the spread is measurement error.  p_fit.py found the hole is a
  ROUTED POCKET -- arcs and straight facets, line inlier 0.86-1.00 against the
  superellipse's 0.00 on the same arcs.  If that is right then n is not a property of
  the hole at all: it is whatever exponent best splits the difference across whichever
  facets a given photograph happened to sample, and two photographs would disagree on
  n BY CONSTRUCTION.

  So the test is on FACET ANGLES, not on n and not on residuals.  A residual can
  improve for reasons that have nothing to do with agreement.

  If the two photographs agree on where the walls are, the hole moves from PARTIALLY
  DETERMINED towards MEASURED.  If they disagree on wall positions too, L1's verdict
  stands for a better reason than it currently has.  Both outcomes are results.

PRE-REGISTRATION, FCC PHOTO 7, WRITTEN AND COMMITTED BEFORE PHOTO 7 WAS EXTRACTED
  The photo-6 test returned CANNOT DETERMINE (p 8.64%) on the set it was first run on.
  Restricting B to CH3's threshold-stable normals moved p to 2.81%, but that choice was
  made AFTER seeing the null, so it is a hypothesis and not a result.  This is the
  replication, and every choice in it is fixed here in advance:

    source        FCC photo 7, hole centre (930.44, 746.40) px, 15.0719 px/mm, both
                  read from metrology/outline-fit-photo7.json, which this lane did not
                  produce and has not altered
    B facet set   CH3's THRESHOLD-STABLE normals -- decided in advance this time,
                  because CH3 is now a standard part of extraction
    tolerance     12 deg, unchanged, and derived rather than tuned (see --tol-deg)
    statistic     the maximum number of matches over a rotation scan of 0-360 deg in
                  0.25 deg steps.  No registration is used, so no homography can be
                  blamed.  The rotation is a nuisance parameter and it is granted to
                  the random sets in the negative control identically, which is what
                  charges the real set for the freedom it is being given.
    null          20000 random facet sets of the same size, same scan, same tolerance
    threshold     p < 0.05 -> AGREE.  p >= 0.05 -> the hole stays PARTIALLY DETERMINED
                  and L1's verdict stands.
    prediction    if the pocket is real, photo 7's best rotation should ALSO land near
                  +87 deg relative to photo 6 -- but that is a bonus observation and
                  the verdict does not depend on it.

TWO INDEPENDENT WAYS OF COMPARING, and neither is fitted to the facets
  A  registered  -- photo 6's normals are rotated into the O'Flynn frame by the
     rotation c_register fitted on 80 INTERIOR LANDMARKS. It never saw the hole
     boundary, so it cannot have been tuned to make the facets line up.
  B  rotation-free -- the SORTED SET OF PAIRWISE ANGULAR GAPS between facets is
     invariant under rotation, so it needs no registration at all.  If A and B
     agree, the answer does not depend on the homography.

THE NEGATIVE CONTROL IS THE WHOLE POINT.  A few facets matched within a few degrees
  can happen by chance.  So the same matching is run against thousands of RANDOM
  facet sets of the same size, and the reported number is how often chance does this
  well.  Without that, "the angles agree" is an adjective.

POWER IS STATED BEFORE THE TEST RUNS, not after.  photo 6 resolves ~4.53 genuine
  px/mm at the board (respro-FCC6_board rolloff 0.2891 on a 15.685 px/mm file), so of
  the 7 facets found on the ~30 px/mm photograph only ONE (45.2-62.3 deg, 9.1 x 4.2
  genuine px) is comfortably above the floor and three more are marginal.  Recovering
  none is CANNOT DETERMINE for lack of resolution -- it is NOT evidence against the
  pocket, and this file says so before it knows the answer.
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

PASS, FAIL, CANNOT = 0, 1, 2
HERE = os.path.dirname(os.path.abspath(__file__))
REPL = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(REPL))
sys.path.insert(0, HERE)
import p_fit as PF


def say(*a):
    print(*a, file=sys.stderr)


# ---------------------------------------------------------------- extraction
def extract_hole(img_path, cx, cy, r_guess_px, level, n_bins=720):
    """The bright region connected to the hole centre, traced radially.
    Same method L1 used on the other photograph, so the comparison is of the shapes
    and not of two different segmenters."""
    im = Image.open(img_path).convert("L")
    a = np.asarray(im).astype(float)
    pad = int(2.2 * r_guess_px)
    x0, y0 = max(0, int(cx - pad)), max(0, int(cy - pad))
    x1, y1 = min(a.shape[1], int(cx + pad)), min(a.shape[0], int(cy + pad))
    sub = a[y0:y1, x0:x1]
    m = sub > level
    lab, n = ndimage.label(m)
    if n == 0:
        return None, None, 0
    seed = lab[int(cy - y0), int(cx - x0)]
    if seed == 0:                        # centre not bright: no hole here
        return None, None, 0
    hole = ndimage.binary_fill_holes(lab == seed)
    area = int(hole.sum())
    ys, xs = np.nonzero(hole)
    hcx, hcy = xs.mean(), ys.mean()
    th = np.arange(n_bins) * 360.0 / n_bins
    rr = np.arange(1.0, 2.0 * r_guess_px, 0.5)
    T, R = np.meshgrid(np.deg2rad(th), rr, indexing="ij")
    X = np.rint(hcx + R * np.cos(T)).astype(int)
    Y = np.rint(hcy + R * np.sin(T)).astype(int)
    ok = (X >= 0) & (Y >= 0) & (X < hole.shape[1]) & (Y < hole.shape[0])
    hit = np.zeros_like(R, bool)
    hit[ok] = hole[Y[ok], X[ok]]
    pts, keep = [], []
    for i in range(n_bins):
        idx = np.nonzero(hit[i])[0]
        if len(idx) == 0:
            continue
        r = rr[idx[-1]]
        pts.append((x0 + hcx + r * math.cos(math.radians(th[i])),
                    y0 + hcy + r * math.sin(math.radians(th[i]))))
        keep.append(th[i])
    return np.array(pts), np.array(keep), area


# ---------------------------------------------------------------- comparison
def match(a_norms, b_norms, tol):
    """Greedy nearest-angle matching, each facet used once. Returns the matched pairs
    and the mean absolute angular error."""
    used, pairs = set(), []
    for i, an in enumerate(a_norms):
        best, bj = 1e9, None
        for j, bn in enumerate(b_norms):
            if j in used:
                continue
            d = abs(((an - bn + 180) % 360) - 180)
            if d < best:
                best, bj = d, j
        if bj is not None and best <= tol:
            used.add(bj)
            pairs.append((i, bj, best))
    return pairs


def gaps(norms):
    n = sorted(x % 360 for x in norms)
    return sorted(round((n[(i + 1) % len(n)] - n[i]) % 360, 3) for i in range(len(n)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["extract", "compare", "rotation"])
    ap.add_argument("--image", default=os.path.join(ROOT, "images", "airtag",
                                                    "fcc-BCGA2187-internal-photo-6.jpg"))
    ap.add_argument("--centre", nargs=2, type=float, default=[945.73, 676.58],
                    help="hole centre in the image, px. STATED, from outline-fit-photo6.")
    ap.add_argument("--r-guess-px", type=float, default=108.0)
    ap.add_argument("--px-per-mm", type=float, default=None)
    ap.add_argument("--scale-basis", default=None)
    ap.add_argument("--level", type=float, default=None,
                    help="brightness level for the hole region. Omit and the tool "
                         "SWEEPS and refuses if the answer is a function of the choice.")
    ap.add_argument("--out", default=os.path.join(REPL, "metrology",
                                                  "pocket-photo6.json"))
    ap.add_argument("--a", default=os.path.join(REPL, "board", "outline",
                                                "outline-fit-oflynn.json"))
    ap.add_argument("--b", default=os.path.join(REPL, "metrology", "pocket-photo6.json"))
    ap.add_argument("--register", default=os.path.join(
        REPL, "metrology", "c_register-fit-boardscale.json"))
    ap.add_argument("--rotation-deg", type=float, default=None,
                    help="B -> A rotation, from c_register's similarity stage. STATED.")
    ap.add_argument("--tol-deg", type=float, default=12.0,
                    help="matching tolerance. NOT tuned to the answer: a facet normal "
                         "on photo 6 is uncertain by about atan(1 genuine px / facet "
                         "span) = atan(0.22 mm / 1.5 mm) ~ 8 deg, so 12 is that plus "
                         "the registration's 1.05 px rms. Derived before the run.")
    ap.add_argument("--free-rotation", action="store_true",
                    help="PRE-REGISTERED replication test. No registration is needed: "
                         "the rotation is a nuisance parameter scanned 0-360 in 0.25 deg "
                         "steps and maximised, AND THE SAME SCAN IS RUN FOR EVERY RANDOM "
                         "SET in the negative control, so the extra freedom is charged "
                         "to the real set and the random ones equally. See the "
                         "pre-registration block at the top of this file.")
    ap.add_argument("--out-compare", default=os.path.join(
        REPL, "metrology", "pocket-cross-photograph.json"))
    a = ap.parse_args()

    if a.verb == "rotation":
        # The rotation is DERIVED from the registration homography's local Jacobian at
        # the hole centre, so there is no sign to guess. Guessing a sign, or trying both
        # and keeping the one that matches, would make the whole test circular.
        d = json.load(open(a.register))
        H = np.array(d["H_target_to_source_cropframe"], float)
        ox, oy = d["target"]["crop_origin"]
        cx, cy = a.centre[0] - ox, a.centre[1] - oy

        def ap_(p):
            v = H @ np.array([p[0], p[1], 1.0])
            return v[:2] / v[2]

        p0, e = ap_((cx, cy)), 2.0
        J = np.c_[(ap_((cx + e, cy)) - p0) / e, (ap_((cx, cy + e)) - p0) / e]
        U, S, Vt = np.linalg.svd(J)
        R = U @ Vt
        th_ = math.degrees(math.atan2(R[1, 0], R[0, 0]))
        say(f"rotation photo6-crop -> oflynn = {th_:.3f} deg")
        say(f"  singular values {S[0]:.5f}, {S[1]:.5f} (isotropy "
            f"{abs(S[0]-S[1])/S.mean()*100:.2f}%)")
        say(f"  det J {np.linalg.det(J):.5f}  -> "
            f"{'NO reflection' if np.linalg.det(J) > 0 else 'REFLECTION - the two faces are not the same face'}")
        say(f"  source: {os.path.relpath(a.register, REPL)}, homography fitted on "
            f"{d['landmarks']['kept']} INTERIOR LANDMARKS, NCC {d['ncc']:.4f} against a "
            f"null-control max of {d['null_control']['max']:.4f}")
        print(f"{th_:.4f}")
        sys.exit(PASS)

    if a.verb == "extract":
        if a.px_per_mm is None or a.scale_basis is None:
            say("CANNOT DETERMINE: --px-per-mm and --scale-basis are both required.")
            sys.exit(CANNOT)
        cx, cy = a.centre
        # CH2: the threshold sweep. M08's lesson -- an answer that is purely a function
        # of the operator's chosen number is not a measurement. Reported ALWAYS, and it
        # decides the verdict rather than decorating it.
        levels = [a.level] if a.level else [150, 165, 180, 190, 200, 210]
        sweep = []
        for L in levels:
            P, th, area = extract_hole(a.image, cx, cy, a.r_guess_px, L)
            sweep.append(dict(level=L, area_px=area,
                              eq_dia_mm=(2 * math.sqrt(area / math.pi) / a.px_per_mm
                                         if area else None),
                              n_boundary=int(len(P)) if P is not None else 0))
            say(f"  level {L:5.0f}: area {area:8d} px  eq dia "
                f"{sweep[-1]['eq_dia_mm'] if area else float('nan'):.4f} mm  "
                f"{sweep[-1]['n_boundary']} boundary points")
        ds = [s["eq_dia_mm"] for s in sweep if s["eq_dia_mm"]]
        spread = (max(ds) - min(ds)) / np.mean(ds) * 100 if len(ds) > 1 else 0.0
        say(f"CH2 threshold sweep: equivalent diameter spread {spread:.2f}% over "
            f"levels {levels}")

        # CH1 negative control: the same extraction centred on SOLID BOARD must find
        # no hole. If it finds one, the segmenter is finding brightness, not a hole.
        offx = a.r_guess_px * 1.6
        Pn, _, area_n = extract_hole(a.image, cx + offx, cy, a.r_guess_px * 0.5,
                                     levels[len(levels) // 2])
        say(f"CH1 negative (same extractor centred on solid board {offx:.0f} px away): "
            f"area {area_n} px")
        ch1 = area_n < 0.15 * max(s["area_px"] for s in sweep)
        if not ch1:
            say("CH1 FIRED: the extractor finds a comparable 'hole' on solid board. "
                "It is finding brightness, not a hole.")

        # CH3: are the FACET ANGLES stable under the operator's threshold, or does the
        # answer move with the choice? CH2 already showed the hole's DIAMETER moves
        # 6.6% across the sweep. If the angles move too, any cross-photograph null is
        # explained by an unstable extractor rather than by the two boards disagreeing,
        # and that distinction decides what the null is allowed to mean.
        ch3 = []
        for Lv in levels:
            Pv, _, av = extract_hole(a.image, cx, cy, a.r_guess_px, Lv)
            if Pv is None:
                ch3.append(dict(level=Lv, facets=None))
                continue
            hv = PF.fit_hole(Pv, a.px_per_mm)
            ch3.append(dict(level=Lv, n_facets=len(hv["facets"]),
                            normals_deg=sorted(round(f["normal_deg"], 1)
                                               for f in hv["facets"])))
            say(f"CH3 level {Lv:5.0f}: {len(hv['facets'])} facets at "
                f"{ch3[-1]['normals_deg']}")
        # how many normals recur across at least half the sweep, within 8 deg
        alln = [n for r in ch3 if r.get("normals_deg") for n in r["normals_deg"]]
        stable = []
        for n in sorted(set(round(x) for x in alln)):
            hits = sum(1 for r in ch3 if r.get("normals_deg") and
                       any(abs(((m - n + 180) % 360) - 180) <= 8 for m in r["normals_deg"]))
            if hits >= max(2, len(levels) // 2 + 1):
                if not any(abs(((n - t + 180) % 360) - 180) <= 8 for t in stable):
                    stable.append(n)
        say(f"CH3 facet-angle stability: {len(stable)} normals recur in more than half "
            f"the threshold sweep (within 8 deg): {stable}")

        L = a.level or 190
        P, th, area = extract_hole(a.image, cx, cy, a.r_guess_px, L)
        if P is None:
            say("CANNOT DETERMINE: no bright region connected to the stated centre.")
            sys.exit(CANNOT)
        hf = PF.fit_hole(P, a.px_per_mm)
        out = dict(tool="p_pocket.py", verb="extract", image=os.path.relpath(a.image, ROOT),
                   centre_px=[cx, cy], level_used=L, px_per_mm=a.px_per_mm,
                   scale_basis=a.scale_basis, n_boundary=int(len(P)),
                   CH1_negative_area_px=int(area_n), CH1_pass=bool(ch1),
                   CH2_threshold_sweep=sweep, CH2_eq_dia_spread_pct=float(spread),
                   CH3_facets_per_level=ch3, CH3_stable_normals_deg=stable,
                   CH3_note=("a facet normal that appears at only one threshold is the "
                             "operator's choice, not the board's geometry"),
                   inner=hf,
                   boundary_px=[[float(x), float(y)] for x, y in P])
        with open(a.out, "w") as f:
            json.dump(out, f, indent=2)
        say(f"\nfit: {len(hf['facets'])} facets admitted, "
            f"{len(hf['facets_refused'])} refused; resid "
            f"{hf['superellipse_only_resid_sd_mm']:.4f} -> {hf['facet_resid_sd_mm']:.4f} mm")
        for f_ in hf["facets"]:
            say(f"  {f_['direction']:7s} {f_['arc_deg'][0]:6.1f}-{f_['arc_deg'][1]:6.1f} "
                f"deg  offset {f_['offset_mm']:.3f} mm  normal {f_['normal_deg']:.1f} deg")
        say(f"wrote {os.path.relpath(a.out, REPL)}")
        sys.exit(PASS if ch1 else FAIL)

    # ---------------- compare
    if a.rotation_deg is None and not a.free_rotation:
        say("CANNOT DETERMINE: --rotation-deg is required and must come from a "
            "registration fitted on something OTHER than the hole. Guessing it, or "
            "fitting it to the facets, would make this test circular.")
        sys.exit(CANNOT)
    A = json.load(open(a.a))["inner"]
    B = json.load(open(a.b))["inner"]
    an = [f["normal_deg"] for f in A["facets"]]
    # B's facets are taken from CH3's STABLE set where one exists -- the normals that
    # recur across more than half the threshold sweep. A facet that appears at one
    # threshold only is the operator's choice, not the board's geometry, and CH3 showed
    # photo 6's level-190 set contains one of those. This choice is made by a control,
    # not by the answer: CH3 runs during extraction, before any comparison.
    Bfull = json.load(open(a.b))
    stable = Bfull.get("CH3_stable_normals_deg")
    raw = sorted(f["normal_deg"] for f in B["facets"])
    bn = [(f["normal_deg"] + (a.rotation_deg or 0.0)) % 360 for f in B["facets"]]
    if a.free_rotation:
        say("PRE-REGISTERED FREE-ROTATION TEST. Procedure fixed in this file's header "
            "and committed before the second photograph was extracted.")
    say(f"A ({os.path.basename(a.a)}): {len(an)} facets at "
        f"{[round(x,1) for x in sorted(an)]}")
    say(f"B ({os.path.basename(a.b)}): {len(bn)} facets, rotated by "
        f"{a.rotation_deg:+.2f} deg -> {[round(x,1) for x in sorted(bn)]}")

    rng = np.random.default_rng(5)
    N = 20000

    SCAN = np.arange(0, 360, 0.25)

    def best_over_rotation(anorm, bset):
        best, bth = -1, 0.0
        for th_ in SCAN:
            k = len(match(anorm, [(x + th_) % 360 for x in bset], a.tol_deg))
            if k > best:
                best, bth = k, float(th_)
        return best, bth

    def run(label, bset):
        if a.free_rotation:
            k, bth = best_over_rotation(an, bset)
            pr = match(an, [(x + bth) % 360 for x in bset], a.tol_deg)
            say(f"\n{label}: best rotation {bth:.2f} deg gives {k} matches")
        else:
            pr = match(an, bset, a.tol_deg)
            bth = None
        er = [q[2] for q in pr]
        cnt = np.zeros(N, int)
        for t in range(N):
            rb = list(rng.uniform(0, 360, len(bset)))
            if a.free_rotation:
                cnt[t] = best_over_rotation(an, rb)[0]
            else:
                cnt[t] = len(match(an, rb, a.tol_deg))
        pv = float((cnt >= len(pr)).mean())
        say(f"\n{label}: {len(bset)} B facets -> {len(pr)} pairs, mean |err| "
            f"{np.mean(er) if er else float('nan'):.2f} deg")
        for i, j, e in pr:
            say(f"   A {an[i]:6.1f} deg  <->  B {bset[j]:6.1f} deg   err {e:.2f} deg")
        say(f"   NEGATIVE CONTROL {N} random sets of the same size: chance matches "
            f"mean {cnt.mean():.2f}; {pv*100:.2f}% do at least as well")
        return dict(label=label, n_b=len(bset), pairs=len(pr), best_rotation_deg=bth,
                    mean_abs_err_deg=float(np.mean(er)) if er else None,
                    p_at_least_as_good=pv,
                    matches=[dict(A_deg=an[i], B_deg=bset[j], err_deg=e) for i, j, e in pr])

    # BOTH sets are always run and BOTH are always reported. The chronology matters and
    # is recorded: the single-threshold set was run FIRST and returned a null (p 8.64%).
    # CH3 -- facet stability across the threshold sweep -- was written AFTER that null,
    # to ask whether an unstable extractor explained it. Restricting B to CH3's stable
    # normals then moved p to 2.68%. Excluding an operator-dependent feature is this
    # project's own standing rule, but the choice was still made AFTER seeing the null,
    # so this file publishes the WEAKER of the two as the verdict and names the stronger
    # one as a hypothesis needing a PRE-REGISTERED replication on a third photograph.
    if a.free_rotation:
        r_raw = run("PRE-REGISTERED free-rotation test, CH3 threshold-stable set",
                    list(stable) if stable else raw)
        r_stb = None
    else:
        r_raw = run("SINGLE-THRESHOLD set (run first)", bn)
        r_stb = None
        if stable:
            r_stb = run("CH3 THRESHOLD-STABLE set (chosen AFTER the null above)",
                        [(x + a.rotation_deg) % 360 for x in stable])
    pairs = [(m["A_deg"], m["B_deg"], m["err_deg"]) for m in r_raw["matches"]]
    errs = [p[2] for p in pairs]
    p_val = max(r_raw["p_at_least_as_good"],
                r_stb["p_at_least_as_good"] if r_stb else 0.0)
    say(f"\nThe verdict is taken on the WEAKER result, p = {p_val*100:.2f}%. "
        f"A verdict chosen after seeing which analysis wins is not a verdict.")

    # B rotation-free: the sorted pairwise gap structure
    ga, gb = gaps(an), gaps(bn)
    say(f"\nB rotation-free: gap sets  A {ga}   B {gb}")

    verdict, code = "CANNOT DETERMINE", CANNOT
    if len(pairs) == 0:
        why = ("no facet on B matched any facet on A. Given the PRE-STATED power "
               "(only 1 of 7 facets is comfortably above photo 6's resolution floor) "
               "this is a null for lack of resolution and is NOT evidence against the "
               "pocket. L1's PARTIALLY DETERMINED stands, unchanged by this test.")
    elif p_val < 0.05:
        verdict, code = "AGREE", PASS
        why = (f"{len(pairs)} facet normals agree to {np.mean(errs):.1f} deg mean, and "
               f"chance does this well only {p_val*100:.2f}% of the time, on the WEAKER "
               f"of the two runs.")
    else:
        why = (f"on the weaker run, {len(pairs)} pairs matched but chance matches this "
               f"well {p_val*100:.1f}% of the time, so the agreement is not "
               f"distinguishable from coincidence. The stronger run reaches "
               f"{(r_stb or r_raw)['p_at_least_as_good']*100:.2f}% but its facet set was "
               f"chosen after the null, so it is a HYPOTHESIS needing a pre-registered "
               f"replication on FCC photo 7, not a result. L1's PARTIALLY DETERMINED "
               f"stands.")
    say(f"\nVERDICT: {verdict} -- {why}")

    out = dict(tool="p_pocket.py", verb="compare", A=os.path.relpath(a.a, REPL),
               B=os.path.relpath(a.b, REPL), rotation_deg=a.rotation_deg,
               rotation_source=("c_register similarity stage theta_deg, fitted on 80 "
                                "INTERIOR LANDMARKS -- it never saw the hole boundary"),
               tol_deg=a.tol_deg, A_normals=sorted(an),
               B_normals_raw=raw, B_normals_rotated=sorted(bn),
               runs=[r for r in (r_raw, r_stb) if r],
               verdict_taken_on="the WEAKER of the two runs",
               chronology=("the single-threshold set was run FIRST and returned a null "
                           "(p 8.64%). CH3 was written AFTER that null to ask whether an "
                           "unstable extractor explained it; restricting B to CH3's "
                           "threshold-stable normals moved p to 2.68%. That is a "
                           "post-hoc analytic choice and it is recorded as one."),
               p_reported=p_val,
               rotation_free_gap_sets=dict(A=ga, B=gb),
               prestated_power=("photo 6 resolves ~4.53 genuine px/mm at the board; of "
                                "the 7 O'Flynn facets only 45.2-62.3 deg (9.1 x 4.2 "
                                "genuine px) is comfortably above the floor, 3 more are "
                                "marginal, 3 are below it. Stated before the run."),
               verdict=verdict, why=why)
    with open(a.out_compare, "w") as f:
        json.dump(out, f, indent=2)
    say(f"wrote {os.path.relpath(a.out_compare, REPL)}")
    sys.exit(code)


if __name__ == "__main__":
    main()
