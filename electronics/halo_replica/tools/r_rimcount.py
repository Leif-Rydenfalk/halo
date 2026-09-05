#!/usr/bin/env python3
"""r_rimcount.py -- the BLIND count of the rim tear-off joints, with r_circ.

L10 BLIND RIM COUNT lane, halo Replica.
SIDE NAMING: the side carrying the SoC and the shield can. O'Flynn's
`oflynn-backside-fullres.jpeg` IS that side.

BLIND-SAFE.  States no count, cites no count, loads no seeds, and reads nothing
outside the protocol's allow-list.

Verbs
  null    N1 (phase-scrambled) and N3 (the real rim) for the CIRCULAR statistic,
          at the size being counted, in the annulus.  N3 p99 is the bar.
  limit   the pad-scale detection limit, pasted INTO THE RIM ITSELF, site swept,
          plus the shape gate's calibration and its measured contrast floor.
  count   scan the annulus, gate on shape, classify, and report every class --
          including the ones that are NOT joints and the ones NOT MEASURED.
  draw    render detections, rejections, unmeasured regions and paste sites onto
          the photograph.  NOT OPTIONAL: every worst defect in this project today
          was caught by looking at this picture and by no number.

Exit 0 pass, 1 fail, 2 CANNOT DETERMINE.
"""
import argparse, json, math, os, sys
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d_rect as DR
import r_circ as RC
import r_frame as RF

# `d_darkpkg`, `d_rim` and `m_dark_packages` cannot be imported in this sanitised
# worktree: they reach `c_register` / `m_components`, which were removed with
# everything else that could state the withheld figure.  Recovering them is
# forbidden.  What this file needs from them is small, is reproduced here with
# attribution, and the frame is rebuilt and VERIFIED in r_frame.py.
GENUINE = (20.7, 27.4)          # d_darkpkg.GENUINE -- genuine px/mm on this source
REG_FLOOR_MM = 0.1029           # c_register worst held-out fold; the position floor


def run_id(path):
    import hashlib, subprocess, time
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE,
                             capture_output=True, text=True).stdout.strip()
    except Exception:
        rev = "unknown"
    return dict(run_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), git_rev=rev,
                image_sha256_12=hashlib.sha256(open(path, "rb").read()).hexdigest()[:12],
                tool="r_rimcount.py", engine="r_circ.py", frame="r_frame.py")


def rim_mask(board, outer, origin, ppm, lo=0.86, hi=1.01):
    """The rim annulus as a fraction of the LOCAL edge radius r(theta).  Reproduced
    from `d_rim.rim_mask` (allow-listed, unimportable here).  A CONSTANT-radius ring
    is wrong: this board's apparent radius varies ~5 % with angle and such a ring
    drifts on and off the board.  M03 established that; it is reused, not re-derived."""
    O = np.asarray(outer, float)
    th = np.degrees(np.arctan2(O[:, 1] - origin[1], O[:, 0] - origin[0])) % 360
    rr = np.hypot(O[:, 0] - origin[0], O[:, 1] - origin[1])
    k = np.argsort(th)
    yy, xx = np.mgrid[0:board.shape[0], 0:board.shape[1]]
    A = np.degrees(np.arctan2(yy - origin[1], xx - origin[0])) % 360
    R = np.interp(A, th[k], rr[k])
    Rp = np.hypot(yy - origin[1], xx - origin[0])
    return board & (Rp >= lo * R) & (Rp <= hi * R), R

FIT = os.path.join(HERE, "..", "metrology", "c_register-fit-boardscale.json")


def frame(a):
    """Everything geometric, in one place, so every verb shares one input line."""
    ok, chk = RF.selfcheck(verbose=False)
    if not ok:
        print("  CANNOT DETERMINE: the reconstructed frame failed its own checks", chk)
        sys.exit(2)
    lum, board, outer, origin, ppm, spath, f = RF.board_frame(a.fit)
    RM, R = rim_mask(board, outer, origin, ppm, a.rim_lo, a.rim_hi)
    BG, POLY = RF.background_mask(lum, outer, a.bg_thr)
    BGd = DR.downsample(BG.astype(float), a.down) > 0.5
    d = a.down
    L = DR.downsample(lum, d)
    B0 = DR.downsample(board.astype(float), d) > 0.999
    # E07 sec.29: a rim feature STRADDLES the board edge.  Fitting against the eroded
    # board mask cuts its outer boundary and the scan prints a zero -- the absence of
    # a measurement wearing the costume of evidence of absence.  Dilate outward into
    # the gasket, where a rim feature's outer boundary legitimately is.
    it = max(0, int(round(a.dilate_mm * ppm / d / 1.5)))
    VALID = ndimage.binary_dilation(B0, np.ones((3, 3)), iterations=it) if it else B0
    ANN = DR.downsample(RM.astype(float), d) > 0.999
    ppmd = ppm / d
    Gx, Gy = RC.grads(L, a.smooth)
    radii = list(np.arange(a.min_mm, a.max_mm + 1e-9, a.r_step_mm) * ppmd / 2.0)
    rid = run_id(spath)
    return dict(lum=lum, board=board, outer=outer, origin=origin, ppm=ppm, ppmd=ppmd,
                L=L, VALID=VALID, ANN=ANN, Gx=Gx, Gy=Gy, radii=radii, d=d,
                spath=spath, fit=f, rid=rid, RM=RM, frame_check=chk,
                BG=BG, BGd=BGd)


def hdr(c, a):
    print(f"r_rimcount {a.verb} -- ROUND rim features by circular boundary evidence\n")
    print(f"  run_id   {c['rid']['run_utc']} git {c['rid']['git_rev']} "
          f"image sha {c['rid']['image_sha256_12']}")
    print(f"  SOURCE   {c['fit']['source']['path']}  (the side carrying the SoC and the "
          f"shield can)")
    print(f"  scale    {c['ppm']:.3f} px/mm stored, {c['ppmd']:.3f} at down {c['d']}; "
          f"GENUINE {GENUINE[0]}-{GENUINE[1]} px/mm")
    print(f"  annulus  {a.rim_lo}-{a.rim_hi} of the LOCAL edge radius r(theta); "
          f"{c['RM'].sum()} stored px, {c['ANN'].sum()} at down {c['d']}")
    print(f"  mask     board dilated {a.dilate_mm} mm OUTWARD (E07 sec.29)")
    bgf = float((c["BGd"] & c["ANN"]).sum()) / max(int(c["ANN"].sum()), 1)
    print(f"  overshoot {100*bgf:.2f} % of the annulus is BRIGHT BACKGROUND connected to "
          f"outside the outline (luma > {a.bg_thr}) -- LABELLED, never deleted")
    print(f"  frame    REBUILT here and verified: scale {c['frame_check']['scale_err_pct']:+.3f} % "
          f"vs stored, outline diameter {c['frame_check']['dia_mm']:.3f} mm")
    print(f"  sizes    {a.min_mm}-{a.max_mm} mm diameter, {len(c['radii'])} radii, "
          f"{a.nphi} ring samples, smooth {a.smooth}\n")


def centres(c):
    """Annulus positions whose whole ring can be measured -- and how many cannot."""
    ys, xs = np.nonzero(c["ANN"])
    return ys, xs


def sd_floor(c, a, ys, xs, n=600):
    """The denominator guard, MEASURED on this image at this size (E07 sec.25).
    The same floor is applied to the nulls, the ladder and the scan, so nothing is
    normalised by a different number than the thing it is compared with."""
    rng = np.random.default_rng(20260905)
    v = []
    rmid = c["radii"][len(c["radii"]) // 2]
    for k in rng.integers(0, len(ys), n):
        o = RC.ring_at(c["Gx"], c["Gy"], c["VALID"], float(xs[k]), float(ys[k]),
                       rmid, a.nphi)
        if o:
            v.append(o["ring_sd"])
    if len(v) < n // 4:
        print(f"  CANNOT DETERMINE: only {len(v)} of {n} floor draws were measurable")
        sys.exit(2)
    return float(np.percentile(v, a.sd_floor_pct)), len(v), n


def crop_eval(c, a, cx, cy, floor, paste=None, shape="disc", size_mm=1.4,
               step=0.0, blur_px=0.0):
    """Evaluate the SAME statistic at one full-resolution position, optionally after
    pasting a synthetic feature of known size and contrast into the PHOTOGRAPH ITSELF.

    The paste goes into the stored-resolution image and is then downsampled through
    the identical path the real scan uses, so the control is made OF the photograph
    (E07 sec.4) rather than of something cleaner than it."""
    d = c["d"]
    # the shape profile reaches 2.4x the ring radius, so the crop must hold it --
    # a crop that truncates the profile makes it refuse, which is a statement about
    # the crop and not about the feature
    R = int(2.6 * max(c["radii"]) * d) + 10 * d
    y0 = int(max(0, (cy - R) // d * d)); y1 = int(min(c["lum"].shape[0], cy + R))
    x0 = int(max(0, (cx - R) // d * d)); x1 = int(min(c["lum"].shape[1], cx + R))
    W = c["lum"][y0:y1, x0:x1].copy()
    if paste is not None or step:
        yy, xx = np.mgrid[y0:y1, x0:x1]
        s = size_mm * c["ppm"]
        if shape == "disc":
            m = np.hypot(xx - cx, yy - cy) <= s / 2
        elif shape == "square":
            aa = math.sqrt(math.pi) * s / 2.0          # EQUAL AREA to the disc
            m = (np.abs(xx - cx) <= aa / 2) & (np.abs(yy - cy) <= aa / 2)
        elif shape == "annulus":
            rr = np.hypot(xx - cx, yy - cy)
            m = (rr <= s / 2) & (rr >= 0.62 * s / 2)   # a gold ring pad: bright ring,
        elif shape == "rect21":                        # dark centre, same outer size
            A = math.pi * (s / 2) ** 2
            w = math.sqrt(A * 2.0); h = A / w
            m = (np.abs(xx - cx) <= w / 2) & (np.abs(yy - cy) <= h / 2)
        # THE PASTE MUST BE AS HARD TO SEE AS THE REAL THING (E07 sec.4).  Two ways
        # a synthetic pad is easier than a real one, and both were found by looking
        # at the numbers a hard unclipped paste produced:
        #   1 A HARD EDGE.  This source resolves 20.7-27.4 genuine px/mm against
        #     106.313 stored, so a real feature's edge is smeared over ~4.4 stored px.
        #     A step function is not something this photograph can contain.
        #   2 8-BIT SATURATION.  Pasting +120 onto luma 213 gave a core of 333, which
        #     no photograph can hold.  The paste is clipped like the sensor clips.
        F = m.astype(float)
        if blur_px > 0:
            F = ndimage.gaussian_filter(F, blur_px / 2.355)
        W = np.clip(W + step * F, 0.0, 255.0)
    Lc = DR.downsample(W, d)
    Gx, Gy = RC.grads(Lc, a.smooth)
    vy0, vx0 = y0 // d, x0 // d
    V = c["VALID"][vy0:vy0 + Lc.shape[0], vx0:vx0 + Lc.shape[1]]
    if V.shape != Lc.shape:
        return None, None, None
    o = RC.best_at(Gx, Gy, V, (cx - x0) / d, (cy - y0) / d, c["radii"], a.nphi, floor)
    sg = RC.shape_gate(W, cx - x0, cy - y0, (o["r_px"] * d) if o else
                       c["radii"][len(c["radii"]) // 2] * d, sigma=a.shape_sigma,
                       bg=c["BG"][y0:y0 + W.shape[0], x0:x0 + W.shape[1]])
    return o, sg, (W, x0, y0)


def quiet_sites(c, a, n=5, mode="quiet"):
    """Paste sites.  E07 sec.26: 'chosen by the code' is not the same as controlled --
    the criterion's own blind spot stays exactly where it was.  So the SITE SELECTION
    IS SWEPT: the quietest windows AND uniformly random annulus positions, and the
    verdict is taken on the worse of the two."""
    d = c["d"]
    g = np.hypot(*np.gradient(ndimage.gaussian_filter(c["L"], 1.0)))
    w = int(1.9 * a.size_mm * c["ppmd"])
    E = ndimage.uniform_filter(g, w)
    C = ndimage.uniform_filter(c["VALID"].astype(float), w)
    # THE SITE MUST BE ON BOARD MATERIAL.  The quiet criterion selects BACKGROUND,
    # because background is smooth -- E07 sec.26 and sec.7 in one.  Here a false
    # exclusion costs nothing (another site is picked), so the flood mask is safe.
    NB = ndimage.uniform_filter(c["BGd"].astype(float), w) < 1e-6
    E = np.where((C > 0.999) & c["ANN"] & NB, E, np.inf)
    out = []
    if mode == "quiet":
        Ew = E.copy()
        for _ in range(n):
            if not np.isfinite(Ew).any():
                break
            iy, ix = np.unravel_index(np.argmin(Ew), Ew.shape)
            out.append((float(ix * d), float(iy * d), float(E[iy, ix])))
            Ew[max(0, iy - w):iy + w, max(0, ix - w):ix + w] = np.inf
    else:
        ys, xs = np.nonzero(np.isfinite(E))
        rng = np.random.default_rng(4242)
        for k in rng.choice(len(ys), size=min(n, len(ys)), replace=False):
            out.append((float(xs[k] * d), float(ys[k] * d), float(E[ys[k], xs[k]])))
    return out


# ------------------------------------------------------------------ verbs

def v_null(c, a, out):
    ys, xs = centres(c)
    floor, nok, ntry = sd_floor(c, a, ys, xs)
    print(f"  ring-sd floor {floor:.4f} luma/px  (p{a.sd_floor_pct} of {nok}/{ntry} "
          f"measurable draws) -- the denominator guard")
    n3 = RC.null_dist(c["Gx"], c["Gy"], c["VALID"], ys, xs, c["radii"],
                      n=a.null_n, nphi=a.nphi, sd_floor=floor)
    Ls = RC.phase_scramble(c["L"])
    sx, sy = RC.grads(Ls, a.smooth)
    n1 = RC.null_dist(sx, sy, c["VALID"], ys, xs, c["radii"],
                      n=a.null_n, nphi=a.nphi, sd_floor=floor)
    print(f"\n  N1 phase-scrambled, annulus   closure p50 {n1['p50']:6.2f}  p90 "
          f"{n1['p90']:6.2f}  p99 {n1['p99']:6.2f}  max {n1['max']:6.2f}  "
          f"(n={n1['n']}, {n1['unmeasured']} unmeasured)")
    print(f"  N3 THE REAL RIM, random c/r   closure p50 {n3['p50']:6.2f}  p90 "
          f"{n3['p90']:6.2f}  p99 {n3['p99']:6.2f}  max {n3['max']:6.2f}  "
          f"(n={n3['n']}, {n3['unmeasured']} unmeasured)")
    ok = n3["p99"] > n1["p99"]
    print(f"\n  P2 predicted N3 p99 > N1 p99, falsified at or below it.")
    print(f"  P2 {'HOLDS' if ok else 'IS FALSIFIED'}  ({n3['p99']:.2f} vs {n1['p99']:.2f}"
          f", ratio {n3['p99']/max(n1['p99'],1e-9):.2f}x)")
    print(f"\n  BAR = {n3['p99']:.2f}   (N3 p99; N3 max {n3['max']:.2f} reported too)")
    out.update(sd_floor=floor, n1=n1, n3=n3, bar=round(n3["p99"], 3),
               p2_verdict="HOLDS" if ok else "FALSIFIED")


def v_limit(c, a, out):
    if a.bar is None:
        print("  CANNOT DETERMINE: no bar. Run `null` and pass --bar.")
        sys.exit(2)
    ys, xs = centres(c)
    floor = a.sd_floor if a.sd_floor else sd_floor(c, a, ys, xs)[0]
    print(f"  bar {a.bar}   ring-sd floor {floor:.4f}   feature {a.size_mm} mm\n")
    steps = [float(x) for x in a.steps.split(",")]
    allsites, ladders, rejected = [], [], []

    def empty_sites(mode, want):
        """A LADDER SITE MUST BE EMPTY, AND THAT IS MEASURED, NOT ASSUMED.

        Seven of ten ladders came back NON-MONOTONIC -- closure FALLING as the pasted
        contrast ROSE.  A detector that loses a feature as its contrast rises is
        reporting on the site.  The cause is that the site already contained
        something: pasting a bright disc over an existing bright feature raises the
        local level and destroys the boundary that was already there, so the ladder
        measures the demolition rather than the paste.  So every site is scored
        UNPASTED first and is admitted only if it is below the bar.  Sites rejected
        for being occupied are counted and reported, not silently replaced."""
        got, tried, rej = [], 0, 0
        for (sx, sy, e) in quiet_sites(c, a, want * 6, mode):
            tried += 1
            o0, _, _ = crop_eval(c, a, sx, sy, floor)
            if o0 is None:
                rej += 1; continue
            if o0["closure_used"] > a.bar:
                rej += 1
                rejected.append(dict(mode=mode, xy=[sx, sy],
                                     unpasted_closure=round(o0["closure_used"], 2)))
                continue
            got.append((sx, sy, e, o0["closure_used"]))
            if len(got) >= want:
                break
        print(f"  {mode.upper()} site selection: {len(got)} empty sites admitted, "
              f"{rej} rejected as OCCUPIED or unmeasurable, out of {tried} examined")
        return got

    for mode in ("quiet", "random"):
        sites = empty_sites(mode, a.sites)
        for k, (sx, sy, e, c0) in enumerate(sites):
            th = math.degrees(math.atan2(sy - c["origin"][1], sx - c["origin"][0])) % 360
            base = float(np.median(c["lum"][int(sy) - 40:int(sy) + 40,
                                            int(sx) - 40:int(sx) + 40]))
            row = dict(mode=mode, site=k, xy=[sx, sy], theta_deg=round(th, 1),
                       mean_abs_grad=round(e, 3), base_luma=round(base, 1),
                       unpasted_closure=round(c0, 2), ladder=[])
            clear = None
            for st in steps:
                o, sg, _ = crop_eval(c, a, sx, sy, floor, paste=True, shape="disc",
                                     size_mm=a.size_mm, step=st, blur_px=a.paste_blur_px)
                cl = o["closure_used"] if o else None
                row["ladder"].append(dict(step_luma=st,
                                          closure=round(cl, 2) if cl is not None else None,
                                          z_total=round(o["z_total"], 1) if o else None,
                                          ring_sd=round(o["ring_sd"], 3) if o else None,
                                          sd_floored=o["sd_floored"] if o else None,
                                          d_mm=round(2 * o["r_px"] / c["ppmd"], 3) if o else None,
                                          measured=o is not None))
                if cl is not None and cl > a.bar:
                    clear = st
            # A LADDER THAT IS NOT MONOTONIC HAS NO SINGLE LIMIT, and quoting the
            # LOWEST clearing step from one reads as high sensitivity while the
            # ladder itself says the detector fails at high contrast.  So the limit
            # is the lowest step ABOVE WHICH EVERY HIGHER STEP ALSO CLEARS, and
            # non-monotonicity is reported rather than averaged away.
            asc = sorted(row["ladder"], key=lambda r: r["step_luma"])
            vals = [r["closure"] for r in asc]
            row["monotonic"] = all(
                (vals[i] is not None and vals[i + 1] is not None
                 and vals[i + 1] >= vals[i] - 0.05 * max(abs(vals[i]), 1.0))
                for i in range(len(vals) - 1))
            lim = None
            for i, r in enumerate(asc):
                if r["closure"] is not None and all(
                        (x["closure"] is not None and x["closure"] > a.bar)
                        for x in asc[i:]):
                    lim = r["step_luma"]; break
            row["step_to_clear"] = lim
            row["clears_at_top"] = (asc[-1]["closure"] is not None
                                    and asc[-1]["closure"] > a.bar)
            print(f"    {mode:6s} site {k} theta {th:6.1f}  |grad| {e:5.2f}  "
                  f"base {base:5.1f} empty {c0:5.2f}  limit {row['step_to_clear']} luma"
                  f"{'' if row['monotonic'] else '  NON-MONOTONIC'}"
                  f"{'' if row['clears_at_top'] else '  FAILS AT TOP STEP'}   "
                  + " ".join(f"{r['step_luma']:.0f}:{r['closure']:.1f}"
                             if r["closure"] is not None else f"{r['step_luma']:.0f}:UNMEAS"
                             for r in sorted(row["ladder"], key=lambda r: -r["step_luma"])))
            ladders.append(row); allsites.append((sx, sy, e, mode))
    got = [r["step_to_clear"] for r in ladders if r["step_to_clear"] is not None]
    n_fail = sum(1 for r in ladders if r["step_to_clear"] is None)
    n_nonmono = sum(1 for r in ladders if not r["monotonic"])
    n_toptail = sum(1 for r in ladders if not r["clears_at_top"])
    fl = [r for r in ladders if all(x["sd_floored"] for x in r["ladder"] if x["measured"])]
    print(f"\n  the ring-sd FLOOR binds at every step at {len(fl)}/{len(ladders)} sites; "
          f"where it does the closure is exactly proportional to contrast and the ladder "
          f"is monotone, and where it does not the ring's own spread grows WITH the paste")
    print(f"  {n_nonmono}/{len(ladders)} ladders are NON-MONOTONIC and "
          f"{n_toptail}/{len(ladders)} FAIL AT THE TOP STEP -- a detector that loses a "
          f"feature as its contrast RISES is reporting on the site, not on the feature")
    print(f"\n  PAD-SCALE LIMIT, {a.size_mm} mm, IN THE RIM, over {len(ladders)} sites "
          f"in 2 swept selections:")
    print(f"    clears the bar at {min(got) if got else None}-{max(got) if got else None}"
          f" luma; {len(got)}/{len(ladders)} sites reach it, {n_fail} never do")
    print(f"\n  P1 predicted 25-100 luma, FALSIFIED above 160 and ALSO below 10.")
    v = ("FALSIFIED-HIGH" if got and max(got) > 160 else
         "FALSIFIED-LOW" if got and max(got) < 10 else
         "HOLDS" if got and 25 <= max(got) <= 100 else
         "OUTSIDE-PREDICTED-RANGE-BUT-NOT-FALSIFIED" if got else "NO-SITE-CLEARED")
    print(f"  P1 {v}")
    out.update(bar=a.bar, sd_floor=floor, size_mm=a.size_mm, ladders=ladders,
               sites_rejected_occupied=rejected,
               step_to_clear=dict(min=min(got) if got else None,
                                  max=max(got) if got else None,
                                  n_reaching=len(got), n_sites=len(ladders)),
               p1_verdict=v)

    # ---- the SHAPE GATE calibrated where it will be used, at the contrast the
    # ---- candidates present.  R01: the threshold is a PROCEDURE, not a constant.
    print(f"\n  SHAPE GATE CALIBRATION -- pasted into the rim, at {a.shape_contrast} luma")
    cal = {}
    for shp in ("disc", "square", "rect21"):
        vals = []
        for mode in ("quiet", "random"):
            for (sx, sy, e) in quiet_sites(c, a, max(a.sites, 12), mode):
                o, sg, _ = crop_eval(c, a, sx, sy, floor, paste=True, shape=shp,
                                     size_mm=a.size_mm, step=a.shape_contrast,
                                     blur_px=a.paste_blur_px)
                p = sg.get("profile") if sg else None
                if p:
                    vals.append(p["noncirc"])
        cal[shp] = vals
        print(f"    {shp:7s} n={len(vals):3d}  noncirc p10 {np.percentile(vals,10):.4f}"
              f"  p50 {np.percentile(vals,50):.4f}  p90 {np.percentile(vals,90):.4f}")
    dp90 = float(np.percentile(cal["disc"], 90))
    qp10 = float(np.percentile(cal["square"], 10))
    ratio = float(np.median(cal["square"]) / max(np.median(cal["disc"]), 1e-9))
    sep = dp90 < qp10 and ratio >= 2.0
    print(f"\n    ROUND if noncirc <= {dp90:.4f} (disc p90); "
          f"NOT ROUND if >= {qp10:.4f} (square p10); between = UNDECIDED")
    print(f"    median ratio square/disc {ratio:.2f}x (need >=2.0)")
    print(f"    P3-replacement {'SEPARATES' if sep else 'DOES NOT SEPARATE'} on this source")
    out.update(shape_cal={k: dict(n=len(v), p10=float(np.percentile(v, 10)),
                                  p50=float(np.percentile(v, 50)),
                                  p90=float(np.percentile(v, 90))) for k, v in cal.items()},
               shape_round_max=dp90, shape_notround_min=qp10, shape_ratio=ratio,
               shape_separates=bool(sep), shape_contrast=a.shape_contrast)


def v_count(c, a, out):
    if a.bar is None:
        print("  CANNOT DETERMINE: no bar. Run `null` and pass --bar.")
        sys.exit(2)
    ys, xs = centres(c)
    floor = a.sd_floor if a.sd_floor else sd_floor(c, a, ys, xs)[0]
    print(f"  bar {a.bar}   ring-sd floor {floor:.4f}\n")
    best_cl = np.full(c["L"].shape, np.nan)
    best_r = np.zeros(c["L"].shape)
    for r in c["radii"]:
        S, S2, C = RC.ring_field(c["Gx"], c["Gy"], c["VALID"], r, a.nphi)
        zt, cl, sd, fl = RC.score_field(S, S2, C, a.nphi, floor)
        take = np.isfinite(cl) & (~np.isfinite(best_cl) | (cl > best_cl))
        best_cl = np.where(take, cl, best_cl)
        best_r = np.where(take, r, best_r)
    # E07 sec.29: an UNMEASURED position is NAMED, never scored 0.
    unmeas = c["ANN"] & ~np.isfinite(best_cl)
    frac_un = float(unmeas.sum()) / max(int(c["ANN"].sum()), 1)
    print(f"  UNMEASURED annulus area {100*frac_un:.2f} %  ({int(unmeas.sum())} of "
          f"{int(c['ANN'].sum())} positions) -- named, not scored")
    # DIAGNOSTIC, and it is the check that ties the answer to its SUBJECT (E07 sec.24:
    # sweep-invariance rules out the operator and establishes nothing else).  If the
    # strongest round features on the WHOLE BOARD are not in the annulus, then the
    # annulus is not where the subject is, and a count taken inside it is a correct
    # computation on the wrong region.
    SEARCH = (c["ANN"] if not a.anywhere
              else (DR.downsample(c["board"].astype(float), c["d"]) > 0.999))
    hits = SEARCH & np.isfinite(best_cl) & (best_cl > a.bar)
    lab, n = ndimage.label(hits)
    cand = []
    for i in range(1, n + 1):
        m = lab == i
        v = np.where(m, best_cl, -np.inf)
        iy, ix = np.unravel_index(np.argmax(v), v.shape)
        cand.append((float(best_cl[iy, ix]), float(ix * c["d"]), float(iy * c["d"]),
                     float(best_r[iy, ix] * c["d"])))
    cand.sort(key=lambda t: -t[0])
    keep = []
    a.top = a.top or 10**6
    for cl, cx, cy, r in cand:
        if all(math.hypot(cx - k[1], cy - k[2]) > a.nms_frac * (r + k[3]) for k in keep):
            keep.append((cl, cx, cy, r))
        if len(keep) >= a.top:
            break
    print(f"  {n} above-bar regions -> {len(keep)} maxima after NMS "
          f"(search = {'WHOLE BOARD' if a.anywhere else 'rim annulus'})\n")
    rows = []
    for cl, cx, cy, r in keep:
        sg = RC.shape_gate(c["lum"], cx, cy, r, sigma=a.shape_sigma, bg=c["BG"])
        p = sg.get("profile") if sg else None
        th = math.degrees(math.atan2(cy - c["origin"][1], cx - c["origin"][0])) % 360
        rr = math.hypot(cx - c["origin"][0], cy - c["origin"][1]) / c["ppm"]
        inann = bool(c["ANN"][int(round(cy / c["d"])) % c["ANN"].shape[0],
                              int(round(cx / c["d"])) % c["ANN"].shape[1]])
        if p is None:
            klass = "UNMEASURED-SHAPE"
        elif a.shape_round_max is None:
            klass = "UNGATED"
        elif p["contrast_luma"] < a.shape_floor_luma:
            klass = "UNDECIDED-BELOW-GATE-CONTRAST-FLOOR"
        elif p["noncirc"] <= a.shape_round_max:
            klass = "ROUND"
        elif p["noncirc"] >= a.shape_notround_min:
            klass = "NOT-ROUND"
        else:
            klass = "UNDECIDED"
        rows.append(dict(closure=round(cl, 2), theta_deg=round(th, 1), r_mm=round(rr, 2),
                         d_mm=round(2 * r / c["ppm"], 3), stored_px=[round(cx, 1), round(cy, 1)],
                         noncirc=round(p["noncirc"], 4) if p else None,
                         a4=round(p["a4"], 4) if p else None,
                         inlier_frac=round(sg["inlier_frac"], 3) if sg else None,
                         contrast_luma=round(p["contrast_luma"], 1) if p else None,
                         core_p90=round(p["core_p90"], 1) if p else None,
                         surround_median=round(p["surround_median"], 1) if p else None,
                         in_annulus=inann, klass=klass))
        print(f"  closure {cl:7.2f}  theta {th:6.1f}  r {rr:5.2f} mm  d {2*r/c['ppm']:.3f} mm"
              f"  noncirc {('%.4f' % p['noncirc']) if p else '  UNMEAS'}"
              f"  contrast {('%5.0f' % p['contrast_luma']) if p else '  n/a'}  {'ANN' if inann else '---'} {klass}")
    tally = {}
    for r in rows:
        tally[r["klass"]] = tally.get(r["klass"], 0) + 1
    print(f"\n  CLASSES: " + "  ".join(f"{k} {v}" for k, v in sorted(tally.items())))
    nr = tally.get("ROUND", 0)
    print(f"\n  ROUND (class R) = {nr}")
    if rows:
        ths = sorted(r["theta_deg"] for r in rows if r["klass"] == "ROUND")
        if ths:
            print(f"  angular spread {ths[0]:.0f}-{ths[-1]:.0f} deg over "
                  f"{len(set(int(t)//45 for t in ths))} of 8 octants  "
                  f"(the disjoint-arc tell: necessary, NOWHERE NEAR sufficient -- E07 sec.30)")
    out.update(bar=a.bar, sd_floor=floor, unmeasured_frac=frac_un,
               n_above_bar=n, n_after_nms=len(keep), rows=rows, tally=tally,
               count_round=nr,
               shape_round_max=a.shape_round_max, shape_notround_min=a.shape_notround_min)


def v_draw(c, a, out):
    from PIL import Image, ImageDraw
    if not a.rows_json or not os.path.exists(a.rows_json):
        print("  CANNOT DETERMINE: --rows-json with a `count` result is required")
        sys.exit(2)
    got = json.load(open(a.rows_json))
    im = Image.open(c["spath"]).convert("RGB")
    dr = ImageDraw.Draw(im)
    COL = dict(ROUND=(0, 255, 0), NOTROUND=(255, 0, 0), UNDECIDED=(255, 200, 0))
    # the annulus itself, so it is visible WHERE the search actually looked
    ann = np.asarray(Image.fromarray((c["RM"] * 255).astype(np.uint8)))
    edge = ann & ~ndimage.binary_erosion(ann > 0, np.ones((5, 5)))
    px = im.load()
    yy, xx = np.nonzero(edge)
    for y, x in zip(yy[::7], xx[::7]):
        px[int(x), int(y)] = (0, 120, 255)
    for r in got.get("rows", []):
        cx, cy = r["stored_px"]
        rad = r["d_mm"] * c["ppm"] / 2
        k = r["klass"]
        col = COL.get(k.replace("-", ""), (255, 0, 255) if k.startswith("NOT")
                      else (255, 200, 0))
        if k == "ROUND":
            col = (0, 255, 0)
        elif k.startswith("NOT"):
            col = (255, 0, 0)
        elif k.startswith("UNMEAS"):
            col = (255, 0, 255)
        dr.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=col, width=4)
        dr.text((cx + rad + 4, cy - 8), f"{k[:4]} {r['closure']:.0f}", fill=col)
    for s in got.get("sites", []):
        dr.rectangle([s[0] - 30, s[1] - 30, s[0] + 30, s[1] + 30], outline=(255, 255, 0), width=3)
    im.save(a.out)
    print(f"  wrote {a.out}  ({im.size[0]}x{im.size[1]})")
    print(f"  green ROUND, red NOT-ROUND, magenta UNMEASURED, amber UNDECIDED, "
          f"blue = the annulus searched, yellow = paste sites")
    out.update(drawn=a.out, n_drawn=len(got.get("rows", [])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["null", "limit", "count", "draw"])
    ap.add_argument("--fit", default=FIT)
    ap.add_argument("--down", type=int, default=3)
    ap.add_argument("--smooth", type=float, default=1.0)
    ap.add_argument("--nphi", type=int, default=64)
    ap.add_argument("--min-mm", type=float, default=1.0)
    ap.add_argument("--max-mm", type=float, default=2.2)
    ap.add_argument("--r-step-mm", type=float, default=0.10)
    ap.add_argument("--rim-lo", type=float, default=0.86)
    ap.add_argument("--rim-hi", type=float, default=1.01)
    ap.add_argument("--dilate-mm", type=float, default=1.5)
    ap.add_argument("--sd-floor-pct", type=float, default=5.0)
    ap.add_argument("--sd-floor", type=float, default=None)
    ap.add_argument("--null-n", type=int, default=1200)
    ap.add_argument("--bar", type=float, default=None)
    ap.add_argument("--size-mm", type=float, default=1.4)
    ap.add_argument("--sites", type=int, default=5)
    ap.add_argument("--steps", default="220,180,140,110,90,70,50,35,25,15,8")
    ap.add_argument("--bg-thr", type=float, default=190.0)
    ap.add_argument("--paste-blur-px", type=float, default=4.42,
                    help="FWHM in STORED px of the blur applied to a pasted control. "
                         "Default 106.313/24.05 = the source's own resolution cell; a "
                         "hard-edged paste is a positive control the photograph could "
                         "not contain. Sweep it.")
    ap.add_argument("--shape-sigma", type=float, default=3.0)
    ap.add_argument("--shape-contrast", type=float, default=120.0)
    ap.add_argument("--shape-round-max", type=float, default=None)
    ap.add_argument("--shape-notround-min", type=float, default=None)
    ap.add_argument("--shape-floor-luma", type=float, default=90.0)
    ap.add_argument("--nms-frac", type=float, default=0.7)
    ap.add_argument("--anywhere", action="store_true")
    ap.add_argument("--top", type=int, default=None)
    ap.add_argument("--rows-json", default=None)
    ap.add_argument("--out", default="rim-drawn.png")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    c = frame(a)
    hdr(c, a)
    out = dict(**c["rid"], verb=a.verb, source=c["fit"]["source"]["path"],
               px_per_mm=c["ppm"], down=a.down, nphi=a.nphi, smooth=a.smooth,
               rim=[a.rim_lo, a.rim_hi], dilate_mm=a.dilate_mm,
               sizes_mm=[a.min_mm, a.max_mm], r_step_mm=a.r_step_mm)
    {"null": v_null, "limit": v_limit, "count": v_count, "draw": v_draw}[a.verb](c, a, out)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2, default=float)
        print(f"\n  wrote {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
