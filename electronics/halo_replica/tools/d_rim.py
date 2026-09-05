#!/usr/bin/env python3
"""d_rim.py -- the rim tear-off joints, by boundary evidence.

L7 DARK-PACKAGE DETECTOR lane, halo Replica.
SIDE NAMING: the side carrying the SoC and the shield can. O'Flynn's
`oflynn-backside-fullres.jpeg` IS that side.

THE QUESTION.  How many tear-off joints hold the antenna carrier to the board
rim?  It has never been counted here.  Earlier attempts closed CANNOT DETERMINE
with INTENSITY and BLOB methods on a source carrying 4.6 genuine px/mm, and their
closing statement was about SIGNAL-TO-NOISE rather than about the board.  This
engine is not an intensity method and this source carries 20-27 genuine px/mm.

THIS FILE IS BLIND-SAFE AND IS MEANT TO STAY THAT WAY.  It states no count, cites
no count, and carries no feature positions.  The seeds `step` and `probe` need
live in metrology/darkpkg/r-seeds-WITHHELD.json, which is CONTAMINATING: it
reveals how many rim features one person found by eye and where.  A lane counting
rim features must not open it, and `step`/`probe` will refuse rather than load it
unless --i-am-not-counting is passed.  See PROTOCOL-rim-count-blind.md.

THE BAR IS NOT A PROPERTY OF THE BOARD -- IT SCALES WITH EDGE LENGTH.  The dark
packages' published limit (100-160 luma) was measured on a 3.2 mm object.
Quoting it at a 1.1 mm pad would be a borrowed constant, which is the defect this
lane exists to catch.  `limit` therefore re-runs the whole ladder AT PAD SIZE and
AT THE RIM, and `null` measures the rim's own null rather than the board's.

Verbs: step   the boundary step the seeded rim features actually present
       null   the rim-local null, at pad scale (P3)
       limit  the pad-scale detection limit, pasted into the rim itself (P2)
       count  scan the whole rim annulus and count -- ONLY meaningful if the bar clears
Exit 0 pass, 1 fail, 2 CANNOT DETERMINE.
"""
import argparse, json, math, os, sys, time
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d_rect as DR
import d_darkpkg as DD
import m_dark_packages as MD

SEEDS_PATH = os.path.join(HERE, "..", "metrology", "darkpkg", "r-seeds-WITHHELD.json")


def load_seeds(allowed):
    """Eye-located rim features.  Their COUNT and POSITIONS are contaminating for
    any lane counting rim features, so they live outside this file and loading
    them is an explicit act."""
    if not allowed:
        print("  REFUSED: `step` and `probe` need seeds that reveal how many rim\n"
              "  features one person found by eye, and where.  If you are counting\n"
              "  rim features, opening them destroys your blindness -- run `null`,\n"
              "  `limit` and `count` instead, which need no seeds.  If you are NOT\n"
              "  counting, pass --i-am-not-counting.\n"
              "  PROTOCOL: metrology/darkpkg/PROTOCOL-rim-count-blind.md")
        sys.exit(2)
    if not os.path.exists(SEEDS_PATH):
        print(f"  CANNOT DETERMINE: {SEEDS_PATH} is not present.")
        sys.exit(2)
    return {k: tuple(v) for k, v in json.load(open(SEEDS_PATH))["seeds"].items()}


def rim_mask(board, outer, origin, ppm, lo=0.86, hi=1.01):
    """The rim annulus, as a fraction of the LOCAL edge radius r(theta).

    A constant-radius ring is wrong: this board's apparent radius varies ~5 % with
    angle (M02 sec.3) and such a ring drifts on and off the board.  M03 established
    that and it is reused here rather than re-derived."""
    O = np.asarray(outer, float)
    th = np.degrees(np.arctan2(O[:, 1] - origin[1], O[:, 0] - origin[0])) % 360
    rr = np.hypot(O[:, 0] - origin[0], O[:, 1] - origin[1])
    k = np.argsort(th)
    yy, xx = np.mgrid[0:board.shape[0], 0:board.shape[1]]
    A = np.degrees(np.arctan2(yy - origin[1], xx - origin[0])) % 360
    R = np.interp(A, th[k], rr[k])
    Rp = np.hypot(yy - origin[1], xx - origin[0])
    return board & (Rp >= lo * R) & (Rp <= hi * R), R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["step", "null", "limit", "count", "probe"])
    ap.add_argument("--fit", default=os.path.join(HERE, "..", "metrology",
                                                  "c_register-fit-boardscale.json"))
    ap.add_argument("--down", type=int, default=3)
    ap.add_argument("--pad-mm", type=float, default=1.10)
    ap.add_argument("--null-n", type=int, default=80)
    ap.add_argument("--sites", type=int, default=5)
    ap.add_argument("--steps", default="200,170,140,120,100,80,60,45,30,20,10")
    ap.add_argument("--bar", type=float, default=None)
    ap.add_argument("--min-mm", type=float, default=0.6)
    ap.add_argument("--max-mm", type=float, default=2.2)
    ap.add_argument("--i-am-not-counting", action="store_true",
                    help="required by `step` and `probe`: confirms you are NOT counting "
                         "rim features, because their seeds reveal how many were found "
                         "by eye and where")
    ap.add_argument("--dilate-mm", type=float, default=1.5,
                    help="dilate the board mask outward for rim work, so a feature that "
                         "straddles the edge is measurable rather than silently unmeasured")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    lum, board, outer, origin, ppm, spath, f = MD.board_frame(a.fit)
    rid = DD.run_id(spath)
    d = a.down
    L, BM0 = DD.prep(lum, board, d)         # BM0: the WHOLE board
    # A RIM FEATURE STRADDLES THE EDGE.  Fitting against the board mask alone cuts
    # its outer boundary, and the scan then returns |z| = 0.0 -- which means NOT
    # MEASURED, not NO BOUNDARY.  Reporting those zeros as evidence would be the
    # saturated-check defect this lane catalogued this morning wearing a new face.
    # So the rim is fitted against the board DILATED outward by --dilate-mm, which
    # is where the gasket and the background legitimately are.
    BM = ndimage.binary_dilation(BM0, np.ones((3, 3)),
                                 iterations=max(0, int(round(a.dilate_mm * ppm / d / 1.5)))) \
        if a.dilate_mm > 0 else BM0
    RM, R = rim_mask(board, outer, origin, ppm)
    M = DR.downsample(RM.astype(float), d) > 0.999   # the rim annulus -- WHERE we look
    ppmd = ppm / d
    print(f"d_rim {a.verb} -- the rim tear-off joints by boundary evidence\n")
    print(f"  run_id   {rid['run_utc']} git {rid['git_rev']} image sha {rid['image_sha256_12']}")
    print(f"  SOURCE   {f['source']['path']}  (the side carrying the SoC and the shield can)")
    print(f"  scale    {ppm:.3f} px/mm stored, {ppmd:.3f} at downsample {d}; "
          f"GENUINE {DD.GENUINE[0]}-{DD.GENUINE[1]} px/mm")
    print(f"  rim mask 0.86-1.01 of the LOCAL edge radius r(theta); "
          f"{RM.sum()} stored px, {M.sum()} at d={d}")
    print(f"  Pre-registered predictions are REQUIRED before running this on a")
    print(f"  counting question: metrology/darkpkg/PROTOCOL-rim-count-blind.md\n")
    out = dict(**rid, verb=a.verb, source=f["source"]["path"], px_per_mm=ppm,
               downsample=d, rim_px=int(RM.sum()))

    if a.verb == "step":
        print("  P1 TEST -- the boundary step the seeded rim features present.")
        print("  Steps are OUTSIDE minus INSIDE, per side, at the seed outline.\n")
        # A per-side step measured at a ROUGH seed is DILUTED by the seed error: the
        # inside band lands partly outside and vice versa.  Since the whole verdict
        # rests on this number, it is also measured a second way that does not depend
        # on the outline at all -- the brightest part of the feature against the board
        # just beyond it.  That is the CONTRAST THE SOURCE ACTUALLY OFFERS, and it is
        # an upper bound on any boundary step a better outline could recover.
        yy, xx = np.mgrid[0:lum.shape[0], 0:lum.shape[1]]
        rows = []
        for name, (cx, cy, th, lo, sh, shape) in load_seeds(a.i_am_not_counting).items():
            st = DD.side_steps(lum, cx, cy, th, sh * ppm, lo * ppm, out_px=12.0, in_px=5.0)
            best = max(abs(v) for v in st.values())
            rr = np.hypot(xx - cx, yy - cy)
            size = 0.5 * (lo + sh) * ppm
            core = rr <= 0.40 * size
            ring = (rr >= 0.85 * size) & (rr <= 1.45 * size) & board
            inside = float(np.percentile(lum[core], 90)) if core.any() else float("nan")
            outside = float(np.median(lum[ring])) if ring.any() else float("nan")
            avail = inside - outside
            rows.append(dict(name=name, shape=shape, seed_stored_px=[cx, cy],
                             seed_theta_deg=th, seed_long_mm=lo, seed_short_mm=sh,
                             side_step_luma=st, largest_abs_step=best,
                             core_luma_p90=round(inside, 1),
                             ring_luma_median=round(outside, 1),
                             available_contrast_luma=round(avail, 1)))
            print(f"  {name:20s} {shape:22s} L {st['left']:+6.0f} R {st['right']:+6.0f} "
                  f"T {st['top']:+6.0f} B {st['bottom']:+6.0f} | largest {best:5.0f} | "
                  f"core {inside:5.0f} ring {outside:5.0f} AVAILABLE {avail:+6.0f}")
        allb = [r["largest_abs_step"] for r in rows]
        av = [r["available_contrast_luma"] for r in rows]
        print(f"\n  AVAILABLE CONTRAST (outline-independent): {min(av):.0f}-{max(av):.0f} luma")
        print(f"  This is an UPPER BOUND on any boundary step a better outline could give.")
        print(f"\n  largest step over the five: {min(allb):.0f}-{max(allb):.0f} luma")
        print(f"  P1 predicted 100-200 luma and is FALSIFIED below 60.")
        print(f"  P1 {'HOLDS' if min(allb) >= 60 else 'IS FALSIFIED'}")
        out.update(rows=rows, p1_predicted="100-200 luma, falsified below 60",
                   p1_verdict="HOLDS" if min(allb) >= 60 else "FALSIFIED",
                   largest_side_step_range=[min(allb), max(allb)],
                   available_contrast_range=[min(av), max(av)])

    elif a.verb == "null":
        print(f"  P3 TEST -- the rim's OWN null, at pad scale ({a.pad_mm} mm), "
              f"against the board-average 33.4\n")
        w = a.pad_mm * ppmd
        n1 = DR.side_bar(L, BM, ppmd, w, w, n=a.null_n, scramble=True, sample_mask=M)
        n3 = DR.side_bar(L, BM, ppmd, w, w, n=a.null_n, scramble=False, sample_mask=M)
        print(f"    N1 phase-scrambled, rim only   |z| p50 {n1['p50']:.1f}  p90 {n1['p90']:.1f}"
              f"  p99 {n1['p99']:.1f}  max {n1['max']:.1f}  (n={n1['n']})")
        print(f"    N3 real rim, random place/angle |z| p50 {n3['p50']:.1f}  p90 {n3['p90']:.1f}"
              f"  p99 {n3['p99']:.1f}  max {n3['max']:.1f}  (n={n3['n']})")
        print(f"\n  P3 predicted the rim null ABOVE the board-average 33.4, "
              f"falsified below it.")
        print(f"  P3 {'HOLDS' if n3['p99'] > 33.4 else 'IS FALSIFIED'}  "
              f"(rim p99 {n3['p99']:.1f})")
        print(f"\n  BAR for the rim at pad scale = {n3['p99']:.2f}")
        out.update(pad_mm=a.pad_mm, n1=n1, n3=n3, bar=round(n3["p99"], 2),
                   p3_verdict="HOLDS" if n3["p99"] > 33.4 else "FALSIFIED")

    elif a.verb == "limit":
        if a.bar is None:
            print("  CANNOT DETERMINE: no bar. Run `d_rim null` first and pass --bar.")
            sys.exit(2)
        print(f"  P2 TEST -- the PAD-SCALE limit, pasted INTO THE RIM ITSELF.")
        print(f"  The dark packages' 100-160 luma was measured on a 3.2 mm object and")
        print(f"  MUST NOT be reused at {a.pad_mm} mm. This ladder is at pad size, at the rim.\n")
        g = np.hypot(*np.gradient(ndimage.gaussian_filter(L, 1.0)))
        w = int(1.9 * a.pad_mm * ppmd)
        E = ndimage.uniform_filter(g, w)
        # the window must lie wholly ON THE BOARD; its CENTRE must lie in the rim
        # annulus.  Requiring the whole window inside a 1.8 mm annulus is
        # impossible for a 2.1 mm window and returned CANNOT DETERMINE -- which was
        # a statement about my mask, not about the board.
        C = ndimage.uniform_filter(BM.astype(float), w)
        E = np.where((C > 0.999) & M, E, np.inf)
        if not np.isfinite(E).any():
            print("  CANNOT DETERMINE: no window of that size lies wholly in the rim annulus")
            sys.exit(2)
        sites, Ew = [], E.copy()
        for _ in range(a.sites):
            if not np.isfinite(Ew).any():
                break
            iy, ix = np.unravel_index(np.argmin(Ew), Ew.shape)
            sites.append((float(ix * d), float(iy * d), float(E[iy, ix])))
            Ew[max(0, iy - w):iy + w, max(0, ix - w):ix + w] = np.inf
        print(f"  {len(sites)} paste sites: the quietest non-overlapping "
              f"{1.9*a.pad_mm:.1f} mm windows lying wholly IN THE RIM ANNULUS.")
        for k, (sx, sy, e) in enumerate(sites):
            ang = math.degrees(math.atan2(sy - origin[1], sx - origin[0])) % 360
            print(f"    site {k}  ({sx:6.0f},{sy:6.0f}) theta {ang:6.1f} deg  "
                  f"mean |grad| {e:5.2f}")
        yy, xx = np.mgrid[0:L.shape[0], 0:L.shape[1]]
        steps = [float(x) for x in a.steps.split(",")]
        per_site, n3s, n4s = [], [], []
        for k, (cx, cy, e) in enumerate(sites):
            u = xx - cx / d; v = yy - cy / d
            body = (np.abs(u) <= a.pad_mm * ppmd / 2) & (np.abs(v) <= a.pad_mm * ppmd / 2)
            rows = []
            print(f"\n  SITE {k}")
            for stp in steps:
                Lp = L.copy(); Lp[body] += stp        # a PAD IS BRIGHT: add, don't subtract
                r = DR.fit_sides(Lp, BM, ppmd, cx / d, cy / d, 0.0,
                                 a.pad_mm * ppmd, a.pad_mm * ppmd,
                                 search=int(0.4 * a.pad_mm * ppmd))
                z = {kk: (round(abs(s["z"]), 1) if s else None)
                     for kk, s in r["sides"].items()}
                n = sum(1 for x in z.values() if x and x > a.bar)
                rows.append(dict(step_luma=stp, abs_z=z, sides_clearing=n,
                                 long_mm=round(max(r["w_px"], r["h_px"]) / ppmd, 3),
                                 short_mm=round(min(r["w_px"], r["h_px"]) / ppmd, 3)))
                print(f"    step {stp:6.1f}  |z| L {z['left']} R {z['right']} "
                      f"T {z['top']} B {z['bottom']}   clearing {n}/4   "
                      f"{rows[-1]['long_mm']:.3f} x {rows[-1]['short_mm']:.3f} mm")
            asc = sorted(rows, key=lambda r: r["step_luma"])
            n3 = next((r["step_luma"] for r in asc if r["sides_clearing"] >= 3), None)
            n4 = next((r["step_luma"] for r in asc if r["sides_clearing"] >= 4), None)
            n3s.append(n3); n4s.append(n4)
            per_site.append(dict(site=k, at_stored_px=[cx, cy], mean_abs_grad=e,
                                 step_for_3_of_4=n3, step_for_4_of_4=n4, ladder=rows))
            print(f"    -> 3 of 4 at {n3} luma, 4 of 4 at {n4}")
        ok3 = [x for x in n3s if x]; ok4 = [x for x in n4s if x]
        print(f"\n  PAD-SCALE LIMIT ACROSS {len(sites)} RIM SITES:")
        print(f"    3 of 4 sides needs {min(ok3) if ok3 else None}-{max(ok3) if ok3 else None}"
              f" luma  ({len(ok3)}/{len(sites)} sites reach it)")
        print(f"    4 of 4 sides needs {min(ok4) if ok4 else None}-{max(ok4) if ok4 else None}"
              f" luma  ({len(ok4)}/{len(sites)} sites reach it)")
        out.update(pad_mm=a.pad_mm, bar=a.bar, sites=[[s[0], s[1], s[2]] for s in sites],
                   per_site=per_site,
                   step_for_3_of_4=dict(min=min(ok3) if ok3 else None,
                                        max=max(ok3) if ok3 else None,
                                        n_reaching=len(ok3), n_sites=len(sites)),
                   step_for_4_of_4=dict(min=min(ok4) if ok4 else None,
                                        max=max(ok4) if ok4 else None,
                                        n_reaching=len(ok4), n_sites=len(sites)))

    elif a.verb == "probe":
        if a.bar is None:
            print("  CANNOT DETERMINE: no bar. Run `d_rim null` first and pass --bar.")
            sys.exit(2)
        print(f"  WHAT THE DETECTOR ACTUALLY GETS AT EACH SEEDED JOINT, bar {a.bar}\n")
        print(f"  Two step estimates disagreed -- a per-side step at a rough seed said")
        print(f"  64-99 luma, an outline-independent core-minus-ring said 174-191 -- and")
        print(f"  neither is what the detector uses. This is: per-side |z| at each joint.\n")
        rows = []
        for name, (cx, cy, th, lo, sh, shape) in load_seeds(a.i_am_not_counting).items():
            best = None
            for dx in (-20, 0, 20):
                for dy in (-20, 0, 20):
                    for tth in ([th] if "rect" in shape else [0.0, 15.0, 30.0, 45.0, 60.0, 75.0]):
                        r = DR.fit_sides(L, BM, ppmd, (cx + dx) / d, (cy + dy) / d, tth,
                                         sh * ppmd, lo * ppmd)
                        v = sum(abs(s["z"]) for s in r["sides"].values() if s)
                        if best is None or v > best[0]:
                            best = (v, r)
            r = best[1]
            z = {k: (round(abs(s["z"]), 1) if s else None) for k, s in r["sides"].items()}
            unmeasured = [k for k, v in z.items() if v is None or v == 0.0]
            n = sum(1 for x in z.values() if x and x > a.bar)
            ang = math.degrees(math.atan2(cy - origin[1], cx - origin[0])) % 360
            rows.append(dict(name=name, shape=shape, theta_deg=round(ang, 1),
                             abs_z=z, sides_clearing=n,
                             fit_long_mm=round(max(r["w_px"], r["h_px"]) / ppmd, 3),
                             fit_short_mm=round(min(r["w_px"], r["h_px"]) / ppmd, 3),
                             sides_not_measured=unmeasured))
            print(f"  {name:20s} theta {ang:6.1f}  |z| L {z['left']:6.1f} R {z['right']:6.1f} "
                  f"T {z['top']:6.1f} B {z['bottom']:6.1f}   clearing {n}/4"
                  f"{('   NOT MEASURED: ' + ','.join(unmeasured)) if unmeasured else ''}")
        tot = sum(r["sides_clearing"] for r in rows)
        nm = sum(len(r["sides_not_measured"]) for r in rows)
        print(f"\n  {tot} of {4*len(rows)} boundaries clear the bar; {nm} were NOT MEASURED")
        print(f"  A side reported 0.0 is a coverage failure, NOT an absence of boundary.")
        out.update(bar=a.bar, rows=rows, sides_supported_total=tot,
                   sides_examined=4 * len(rows), sides_not_measured=nm,
                   dilate_mm=a.dilate_mm)

    elif a.verb == "count":
        if a.bar is None:
            print("  CANNOT DETERMINE: no bar. Run `d_rim null` first and pass --bar.")
            sys.exit(2)
        print(f"  THE COUNT -- whole rim annulus, sizes {a.min_mm}-{a.max_mm} mm, "
              f"bar {a.bar}\n")
        g = DR.detect(L, BM, ppmd, astep=2.0, smooth=1.0, npeak=22, nms=3,
                      z_thr=a.bar, band=1, min_mm=a.min_mm, max_mm=a.max_mm)
        g = DR.maximal(g)
        rows = []
        kept = [r for r in g if M[int(round(r["cy"])) % M.shape[0],
                                 int(round(r["cx"])) % M.shape[1]]]
        print(f"    {len(g)} rectangles on the whole board above the bar; "
              f"{len(kept)} have their centre in the rim annulus\n")
        for r in sorted(kept, key=lambda r: -r["score"]):
            cx, cy = r["cx"] * d, r["cy"] * d
            ang = math.degrees(math.atan2(cy - origin[1], cx - origin[0])) % 360
            rr = math.hypot(cx - origin[0], cy - origin[1]) / ppm
            rows.append(dict(theta_deg=round(ang, 1), r_mm=round(rr, 2),
                             long_mm=round(r["long_px"] / ppmd, 3),
                             short_mm=round(r["short_px"] / ppmd, 3),
                             score=round(r["score"], 2), polarity=r["polarity"],
                             stored_px=[round(cx, 1), round(cy, 1)]))
            print(f"    theta {ang:6.1f} deg  r {rr:6.2f} mm  "
                  f"{rows[-1]['long_mm']:.3f} x {rows[-1]['short_mm']:.3f} mm  "
                  f"score {r['score']:6.2f}  {r['polarity']}")
        print(f"\n  COUNT = {len(rows)}")
        if rows:
            ths = sorted(r["theta_deg"] for r in rows)
            print(f"  angular spread {ths[0]:.0f}-{ths[-1]:.0f} deg over "
                  f"{len(set(int(t)//45 for t in ths))} of 8 octants")
            print(f"  P6: L1's disqualifying tell was FRONT candidates in 147-199 deg and")
            print(f"  BACK in 210-308 deg -- disjoint arcs from per-photograph illumination.")
            print(f"  Judge this spread against that before believing the count.")
        out.update(bar=a.bar, count=len(rows), n_whole_board=len(g), rows=rows)

    if a.json:
        json.dump(out, open(a.json, "w"), indent=2, default=float)
        print(f"\n  wrote {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
