#!/usr/bin/env python3
"""m_rim_pads.py -- COUNT the bright features on the board's rim, and place them.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.
SIDE NAMING: FRONT = component side (Apple's FCC caption). See M02.

THE QUESTION.  `docs/REFERENCE-TEARDOWN.md` says SIX tear-off joints hold the
antenna carrier to the board's rim.  Nobody in this project has counted them;
the number is inherited.  A count is a check that can FAIL, so it is worth more
than another dimension.

METHOD.  Resample the rim into (angle x radius-fraction) space with the radius
normalised to the MEASURED edge r(theta) -- a constant-radius ring is wrong
because the board's apparent radius varies ~5% with angle (M02 Sec 3) and such a
ring drifts on and off the board.  Then label connected BRIGHT blobs and, for
each, report where it sits, how wide it is, and HOW FAR OUT IT REACHES as a
fraction of the local edge radius.

THE DISCRIMINATOR, stated so it can be disagreed with.  An edge-plated pad or a
tear-off stub runs out TO the board edge.  A surface component near the rim does
not: it stops short.  So `reach` = the blob's outermost radius fraction is the
separator, and --min-reach is the one number that decides a pad from a
component.  It is reported for every blob, so a reader can move the line and see
what changes rather than take my word for where it goes.

TWO CONTROLS, both of which can fail:
 * PERMUTATION -- the same detector on the same annulus with its angular columns
   randomly permuted.  Same pixels, same brightness histogram, no 2-D coherence.
   A blob count that does not collapse there is not finding blobs.
 * THE INTERIOR BAND -- the same detector run on a band deep inside the board,
   where by construction nothing can "reach the edge".  Any pad it reports there
   is a pad the criterion invents.

Exit 0 counted, 2 CANNOT DETERMINE.  Prints its inputs.
"""
import argparse, hashlib, json, math, os, subprocess, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def run_id(path):
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
    except Exception:
        rev = "unknown"
    return dict(run_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), git_rev=rev,
                image_sha256_12=hashlib.sha256(open(path, "rb").read()).hexdigest()[:12],
                tool="m_rim_pads.py")


def bilinear(img, x, y):
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    h, w = img.shape[:2]
    x0 = np.clip(x0, 0, w - 2); y0 = np.clip(y0, 0, h - 2)
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
            + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)


def polar(lum, cx, cy, redge, f_lo, f_hi, n_ang, n_rad):
    A = np.linspace(0, 2 * math.pi, n_ang, endpoint=False)
    Re = redge(np.degrees(A))
    F = np.linspace(f_lo, f_hi, n_rad)
    out = np.zeros((n_rad, n_ang))
    for j, f in enumerate(F):
        r = f * Re
        out[j] = bilinear(lum, cx + r * np.cos(A), cy + r * np.sin(A))
    return out, np.degrees(A), F


def blobs(P, F, ang, thr, min_area, min_reach, n_ang):
    m = P > thr
    # connect across the 0/360 seam by labelling a doubled array and folding back
    lab, n = ndimage.label(np.concatenate([m, m], axis=1))
    seen, out = set(), []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(ys) < min_area:
            continue
        xs0 = xs % n_ang
        key = (round(float(F[ys].mean()), 3), round(float(np.sort(np.unique(xs0))[0]), 1))
        if key in seen:
            continue
        seen.add(key)
        # angular centre on the circle
        th = np.radians(ang[xs0])
        cth = math.degrees(math.atan2(np.sin(th).mean(), np.cos(th).mean())) % 360
        span = len(np.unique(xs0)) * 360.0 / n_ang
        out.append(dict(angle_deg=round(cth, 2), span_deg=round(span, 2),
                        area_px=int(len(ys)),
                        reach=round(float(F[ys].max()), 4),
                        inner=round(float(F[ys].min()), 4),
                        mean_luma=round(float(P[ys, xs0].mean()), 1),
                        max_luma=round(float(P[ys, xs0].max()), 1)))
    out.sort(key=lambda d: d["angle_deg"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--centre", required=True)
    ap.add_argument("--profile", required=True, help="raw json from m_outline_fit.py")
    ap.add_argument("--f-lo", type=float, default=0.86)
    ap.add_argument("--f-hi", type=float, default=1.00)
    ap.add_argument("--n-ang", type=int, default=1440)
    ap.add_argument("--n-rad", type=int, default=56)
    ap.add_argument("--bright-pct", type=float, default=80.0,
                    help="threshold = this percentile of the annulus itself")
    ap.add_argument("--min-area", type=int, default=40)
    ap.add_argument("--min-reach", type=float, default=0.975,
                    help="a blob must reach this fraction of the local edge radius to count "
                         "as an EDGE pad rather than a component near the rim")
    ap.add_argument("--min-span-deg", type=float, default=1.0)
    ap.add_argument("--max-span-mm", type=float, default=None,
                    help="upper bound on a feature's arc length. A tear-off tab or an edge pad "
                         "is of the order of a millimetre; a 10 mm bright arc is a region, not "
                         "a pad. Stated rather than tuned: change it and the table shows what "
                         "moves.")
    ap.add_argument("--px-per-mm", type=float, default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    path = a.image if os.path.isabs(a.image) else os.path.join(ROOT, "images", "airtag", a.image)
    rid = run_id(path)
    lum = np.asarray(Image.open(path).convert("L")).astype(float)
    cx, cy = (float(v) for v in a.centre.split(","))
    raw = json.load(open(a.profile))
    pr = np.array(raw["outer_r_theta"], float)
    o = np.argsort(pr[:, 0]); pt, prr = pr[o, 0], pr[o, 1]
    k = 41
    sm = np.convolve(np.concatenate([prr, prr, prr]), np.ones(k) / k, mode="same")[len(prr):2 * len(prr)]
    redge = lambda d: np.interp(np.asarray(d) % 360, pt, sm)

    print("m_rim_pads.py -- inputs:")
    print(f"  run_id     {rid['run_utc']} git {rid['git_rev']} image sha {rid['image_sha256_12']}")
    print(f"  image      {os.path.relpath(path, ROOT)}   centre ({cx:.2f},{cy:.2f})")
    print(f"  edge r(theta) from {os.path.basename(a.profile)} "
          f"run {raw.get('run_utc')} git {raw.get('git_rev')}; "
          f"local radius {sm.min():.1f}..{sm.max():.1f} px")
    print(f"  annulus    {a.f_lo}..{a.f_hi} of the local edge radius, "
          f"{a.n_ang} x {a.n_rad} bins")
    if a.px_per_mm:
        print(f"  1 deg of arc at the rim ~ "
              f"{2*math.pi*sm.mean()/360/a.px_per_mm:.3f} mm")

    P, ang, F = polar(lum, cx, cy, redge, a.f_lo, a.f_hi, a.n_ang, a.n_rad)
    thr = float(np.percentile(P, a.bright_pct))
    print(f"  threshold  {a.bright_pct}th percentile of the annulus itself = {thr:.1f} luma "
          f"(annulus median {np.median(P):.1f})")
    print(f"  a blob counts as an EDGE pad if it reaches >= {a.min_reach} of the local edge "
          f"radius and spans >= {a.min_span_deg} deg")

    B = blobs(P, F, ang, thr, a.min_area, a.min_reach, a.n_ang)
    def arc_mm(b):
        return (2 * math.pi * float(redge(b["angle_deg"])) * b["span_deg"] / 360 / a.px_per_mm
                if a.px_per_mm else None)
    pads = [b for b in B if b["reach"] >= a.min_reach and b["span_deg"] >= a.min_span_deg]
    if a.max_span_mm and a.px_per_mm:
        wide = [b for b in pads if arc_mm(b) > a.max_span_mm]
        pads = [b for b in pads if arc_mm(b) <= a.max_span_mm]
        print(f"  {len(wide)} edge-reaching blobs EXCLUDED as too wide to be a pad "
              f"(> {a.max_span_mm} mm of arc): "
              f"{[(b['angle_deg'], round(arc_mm(b),2)) for b in wide]}")
    print(f"\n  {len(B)} bright blobs in the annulus; {len(pads)} of them reach the edge")

    # CONTROL 1: independent angular ROLL of each radius row.
    #
    # An earlier version permuted the angular COLUMNS. That is a BROKEN control
    # here and it was measured to be broken: a permuted column is a full-height
    # stripe, every full-height stripe trivially satisfies "reaches the edge",
    # and the control returned 46.8 features against the real 26 -- i.e. the
    # control manufactured the very property under test. Rolling each radius row
    # by its own random angle keeps every row's brightness AND its runs intact,
    # and destroys only the RADIAL ALIGNMENT that makes a pad a pad.
    rng = np.random.default_rng(20260905)
    cn = []
    for _ in range(30):
        Pp = np.stack([np.roll(P[j], int(rng.integers(a.n_ang))) for j in range(P.shape[0])])
        Bp = blobs(Pp, F, ang, thr, a.min_area, a.min_reach, a.n_ang)
        cn.append(len([b for b in Bp if b["reach"] >= a.min_reach and b["span_deg"] >= a.min_span_deg]))
    cn = np.array(cn)
    print(f"  CONTROL 1 (each radius row rolled independently, 30 draws -- same pixels, same "
          f"per-row runs, no RADIAL alignment): mean {cn.mean():.2f}, max {cn.max()}")

    # CONTROL 2: an interior band, where nothing can reach the edge
    Pi, _, Fi = polar(lum, cx, cy, redge, 0.55, 0.69, a.n_ang, a.n_rad)
    Bi = blobs(Pi, Fi, ang, thr, a.min_area, a.min_reach, a.n_ang)
    padi = [b for b in Bi if b["reach"] >= a.min_reach and b["span_deg"] >= a.min_span_deg]
    print(f"  CONTROL 2 (the same detector on the interior band 0.55..0.69 of the edge radius, "
          f"where nothing CAN reach the edge): {len(Bi)} blobs, {len(padi)} called pads")

    ok = len(pads) > cn.max() and len(padi) == 0
    print(f"\n  EDGE-REACHING FEATURES: {len(pads)}")
    print(f"  {'angle':>8}  {'span':>6}  {'reach':>6}  {'inner':>6}  {'area':>6}  {'maxluma':>7}"
          + ("  arc_mm" if a.px_per_mm else ""))
    for b in pads:
        arc = arc_mm(b)
        print(f"  {b['angle_deg']:8.2f}  {b['span_deg']:6.2f}  {b['reach']:6.3f}  "
              f"{b['inner']:6.3f}  {b['area_px']:6d}  {b['max_luma']:7.1f}"
              + (f"  {arc:6.3f}" if arc else ""))
    if not ok:
        print("\n  CANNOT DETERMINE: the count does not clear its controls "
              f"(permutation max {cn.max()}, interior band called {len(padi)} pads).")
    out = dict(**rid, image=os.path.relpath(path, ROOT), centre=[cx, cy],
               edge_profile=os.path.basename(a.profile),
               edge_profile_run=raw.get("run_utc"), edge_profile_git=raw.get("git_rev"),
               annulus=[a.f_lo, a.f_hi], bright_pct=a.bright_pct, threshold_luma=round(thr, 1),
               min_reach=a.min_reach, min_area=a.min_area, min_span_deg=a.min_span_deg,
               n_blobs=len(B), n_edge_features=len(pads),
               control_permutation_mean=float(cn.mean()), control_permutation_max=int(cn.max()),
               control_interior_blobs=len(Bi), control_interior_called_pads=len(padi),
               verdict="COUNTED" if ok else "CANNOT DETERMINE",
               edge_features=pads, all_blobs=B)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
