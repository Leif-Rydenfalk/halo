#!/usr/bin/env python3
"""d_darkpkg.py -- the dark IC packages, found by their BOUNDARIES.

L7 DARK-PACKAGE DETECTOR lane, halo Replica.
SIDE NAMING: the side carrying the SoC and the shield can.  O'Flynn's
`oflynn-backside-fullres.jpeg` IS that side.  ("front"/"back" are not used here:
three sources use "front" for two different faces.)

Engine: tools/d_rect.py.  Run `bin/boardmetro rect-selftest` before trusting this.

WHY A BOUNDARY METHOD.  Intensity and texture are ruled out BY MEASUREMENT, not
by opinion: M08 attempts 1-4 and M10 on an independent source with 1.9x more
genuine resolution, where the packages' luma (61, 73) sits inside bare
soldermask's range (52-145) and their local-sd (9.94, 4.22) inside soldermask's
(5.17-14.59).  What the eye uses instead is straight boundaries meeting at right
angles.  That is what d_rect measures.

THE ADMISSION BAR HAS NO OPERATOR IN IT.  M08 attempt 3 failed because a stated
ROI returned the box: 0/20/40/60 px of padding gave 3.35/3.98/4.09/4.50 mm for
one package.  So the bar here is NOT a hand-picked patch of bare board -- picking
an easy patch would set the bar low and admit junk, which is the same defect in a
new costume.  It is the SAME detector, over the SAME annulus mask, on a
PHASE-SCRAMBLED copy of this photograph: identical power spectrum (hence identical
texture statistics at every scale) with all straight edges and all closure
destroyed.  Nothing scoring below what the scramble returns is a detection.
Reported alongside it, for the reader to judge, is the score distribution over an
AUTOMATIC tiling of the whole annulus -- also with no box chosen by me.

Verbs
  bar        measure the admission bar (phase-scramble null + annulus tiling)
  control    nRF52832 positive control + ROI-padding sweep + CONTRAST LADDER
  run        detect across the board, sweep every parameter, publish the handoff
Exit 0 pass, 1 fail, 2 CANNOT DETERMINE.
"""
import argparse, hashlib, json, math, os, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import d_rect as DR
import m_dark_packages as MD

NRF_MM = (2.956, 3.226)
NRF_SOURCE = "Nordic nRF52832 PS v1.4, Table 132, p.541 (fetched by lane L3, not recalled)"
GENUINE = (20.7, 27.4)
REG_FLOOR_MM = 0.1029          # c_register worst held-out fold; the position floor

DEFAULTS = dict(down=4, astep=2.0, smooth=1.0, npeak=22, nms=3)
SWEEP = dict(down=[3, 5], astep=[1.0, 3.0], smooth=[0.6, 1.6],
             npeak=[16, 30], nms=[2, 5])


def run_id(path):
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
    except Exception:
        rev = "unknown"
    return dict(run_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), git_rev=rev,
                image_sha256_12=hashlib.sha256(open(path, "rb").read()).hexdigest()[:12],
                tool="d_darkpkg.py", engine="d_rect.py")


def prep(lum, board, d):
    return DR.downsample(lum, d), DR.downsample(board.astype(float), d) > 0.999


def phase_scramble(a, seed=20260905):
    """Same power spectrum, random phases.  Every texture statistic survives;
    every straight edge and every closed corner does not."""
    rng = np.random.default_rng(seed)
    F = np.fft.rfft2(a)
    ph = rng.uniform(-np.pi, np.pi, F.shape)
    ph[0, 0] = 0.0
    out = np.fft.irfft2(np.abs(F) * np.exp(1j * ph), s=a.shape)
    # match the first two moments back to the original, so luma and contrast
    # are not quietly changed by the transform
    return (out - out.mean()) / (out.std() + 1e-9) * a.std() + a.mean()


def detect_at(lum, board, ppm, p, mask_extra=None, scramble=False, z=4.0):
    L, M = prep(lum, board, p["down"])
    if scramble:
        L = phase_scramble(L)
    if mask_extra is not None:
        M = M & mask_extra(p["down"])
    return DR.detect(L, M, ppm / p["down"], astep=p["astep"], smooth=p["smooth"],
                     npeak=p["npeak"], nms=p["nms"], z_thr=z), ppm / p["down"]


def to_mm(r, ppmd, d, origin, ppm):
    cx, cy = r["cx"] * d + (d - 1) / 2.0, r["cy"] * d + (d - 1) / 2.0
    dx, dy = (cx - origin[0]) / ppm, (cy - origin[1]) / ppm
    o = dict(r)
    o.update(cx_full_px=round(cx, 1), cy_full_px=round(cy, 1),
             x_mm=round(dx, 2), y_mm=round(dy, 2),
             r_mm=round(math.hypot(dx, dy), 2),
             theta_pos_deg=round(math.degrees(math.atan2(dy, dx)) % 360, 1),
             long_mm=round(r["long_px"] / ppmd, 3), short_mm=round(r["short_px"] / ppmd, 3),
             short_genuine_px=[round(r["short_px"] / ppmd * GENUINE[0], 1),
                               round(r["short_px"] / ppmd * GENUINE[1], 1)])
    return o


def side_steps(lum, cx, cy, theta_deg, w_px, h_px, out_px=16.0, in_px=6.0):
    """Median luma OUTSIDE minus INSIDE, FOR EACH SIDE SEPARATELY.

    Averaging the four sides was wrong and it hid the finding: around the nRF the
    four steps are -68, -15, -14 and +5 luma, so the mean is -2 and reads as "no
    boundary" for a package with one very strong boundary.  The illumination
    gradient across a single 3 mm part makes a whole-perimeter statistic
    meaningless here."""
    t = math.radians(theta_deg)
    out = {}
    for name, ax, sgn in (("left", 0, -1), ("right", 0, 1),
                          ("top", 1, -1), ("bottom", 1, 1)):
        half = (w_px if ax == 0 else h_px) / 2.0
        span = (h_px if ax == 0 else w_px)
        s = np.linspace(-0.35, 0.35, 41) * span
        vals = {}
        for band, key in ((-in_px, "in"), (out_px, "out")):
            u = sgn * (half + band) if sgn > 0 else sgn * (half + band)
            u = sgn * half + sgn * band
            ux, uy = (np.full(41, u), s) if ax == 0 else (s, np.full(41, u))
            px = cx + ux * math.cos(t) - uy * math.sin(t)
            py = cy + ux * math.sin(t) + uy * math.cos(t)
            ii = np.clip(np.round(py).astype(int), 0, lum.shape[0] - 1)
            jj = np.clip(np.round(px).astype(int), 0, lum.shape[1] - 1)
            vals[key] = float(np.median(lum[ii, jj]))
        out[name] = round(vals["out"] - vals["in"], 1)
    return out


def boundary_step(lum, cx, cy, theta_deg, w_px, h_px, out_px=16.0, in_px=6.0):
    """Median luma OUTSIDE the boundary minus median INSIDE it, in luma units.
    This is the quantity the method actually lives on, and it is exactly what a
    control on a BLUE package shares with the neutral-black packages it stands in
    for.  E07 sec.4: check the assumption the method shares with its own control."""
    t = math.radians(theta_deg)
    ins, outs = [], []
    for ax, half, span in ((0, w_px / 2, h_px), (1, h_px / 2, w_px)):
        s = np.linspace(-0.35, 0.35, 41) * span
        for sgn in (-1, 1):
            for band, store in ((-in_px, ins), (out_px, outs)):
                u = sgn * (half + band)
                ux, uy = (np.full(41, u), s) if ax == 0 else (s, np.full(41, u))
                px = cx + ux * math.cos(t) - uy * math.sin(t)
                py = cy + ux * math.sin(t) + uy * math.cos(t)
                ii = np.clip(np.round(py).astype(int), 0, lum.shape[0] - 1)
                jj = np.clip(np.round(px).astype(int), 0, lum.shape[1] - 1)
                store.append(lum[ii, jj])
    return float(np.median(np.concatenate(outs)) - np.median(np.concatenate(ins)))


def attenuate(lum, cx, cy, theta_deg, w_px, h_px, k, feather=4.0):
    """Shrink a package's boundary STEP to a fraction k of itself while leaving
    its interior texture alone."""
    H, W = lum.shape
    y0, y1 = max(0, int(cy - w_px - h_px)), min(H, int(cy + w_px + h_px))
    x0, x1 = max(0, int(cx - w_px - h_px)), min(W, int(cx + w_px + h_px))
    yy, xx = np.mgrid[y0:y1, x0:x1]
    t = math.radians(theta_deg)
    u = (xx - cx) * math.cos(t) + (yy - cy) * math.sin(t)
    v = -(xx - cx) * math.sin(t) + (yy - cy) * math.cos(t)
    inside = (np.abs(u) <= w_px / 2 + feather) & (np.abs(v) <= h_px / 2 + feather)
    ring = (np.abs(u) <= w_px / 2 + 26) & (np.abs(v) <= h_px / 2 + 26) & ~inside
    out = lum.copy()
    if not inside.any() or not ring.any():
        return out
    sub = out[y0:y1, x0:x1]
    shift = (1.0 - k) * (float(np.median(sub[ring])) - float(np.median(sub[inside])))
    sub[inside] += shift
    out[y0:y1, x0:x1] = sub
    return out


def boxmask(box, shape):
    def f(d):
        m = np.zeros((shape[0] // d, shape[1] // d), bool)
        x0, y0, x1, y1 = [int(round(v / d)) for v in box]
        m[max(0, y0):y1, max(0, x0):x1] = True
        return m
    return f


# ------------------------------------------------------------------ bar

def v_bar(a, ctx):
    lum, board, outer, origin, ppm, spath, f, rid = ctx
    p = dict(DEFAULTS); p["down"] = a.down
    print("d_darkpkg bar -- THE ADMISSION BAR, and no box in it is mine\n")
    hdr(ctx, p)
    t0 = time.time()
    got, ppmd = detect_at(lum, board, ppm, p, scramble=True, z=a.zfloor)
    barN1 = max((g["score"] for g in got), default=0.0)
    print(f"  N1 PHASE-SCRAMBLED BOARD, same annulus mask, same code path")
    print(f"     identical power spectrum, no straight edge and no corner survives")
    print(f"     n={len(got)}   MAX SCORE {barN1:.2f}    ({time.time()-t0:.0f} s)")

    real, _ = detect_at(lum, board, ppm, p, z=a.zfloor)
    L, M = prep(lum, board, p["down"])
    ts = int(round(a.tile_mm * ppmd))
    tiles = []
    for y in range(0, L.shape[0] - ts, ts):
        for x in range(0, L.shape[1] - ts, ts):
            if M[y:y + ts, x:x + ts].mean() < 0.98:
                continue
            sc = [g["score"] for g in real
                  if x <= g["cx"] < x + ts and y <= g["cy"] < y + ts]
            tiles.append(max(sc) if sc else 0.0)
    tiles = np.array(tiles) if tiles else np.zeros(1)
    qs = {q: round(float(np.percentile(tiles, q)), 2) for q in (50, 75, 90, 95, 99)}
    print(f"\n  N2 THE REAL BOARD, tiled automatically at {a.tile_mm} mm -- {len(tiles)} "
          f"full-board tiles, no box chosen by hand")
    print(f"     max score per tile:  median {qs[50]}  p75 {qs[75]}  p90 {qs[90]}  "
          f"p95 {qs[95]}  p99 {qs[99]}  max {tiles.max():.2f}")
    print(f"     tiles above the N1 bar: {(tiles > barN1).sum()} of {len(tiles)}")
    print(f"\n  ADMISSION BAR = {barN1:.2f}   (N1).  It is measured, by the same code, on")
    print(f"  this image, and it CAN GO UP and disqualify my own findings.")
    out = dict(**rid, verb="bar", source=f["source"]["path"], px_per_mm=ppm,
               params=p, admission_bar=round(barN1, 2),
               n1=dict(kind="phase-scrambled board, whole annulus", n=len(got),
                       max_score=round(barN1, 2)),
               n2=dict(kind=f"real board, automatic {a.tile_mm} mm tiling",
                       n_tiles=len(tiles), quantiles=qs,
                       max=round(float(tiles.max()), 2),
                       tiles_above_bar=int((tiles > barN1).sum())))
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2); print(f"  wrote {a.json}")
    return out


def hdr(ctx, p):
    lum, board, outer, origin, ppm, spath, f, rid = ctx
    print(f"  run_id   {rid['run_utc']} git {rid['git_rev']} image sha {rid['image_sha256_12']}")
    print(f"  SOURCE   {f['source']['path']}  (the side carrying the SoC and the shield can)")
    print(f"  scale    {ppm:.3f} px/mm stored [{f['target']['px_per_mm_basis']}]")
    print(f"           {ppm/p['down']:.3f} px/mm at downsample {p['down']}; "
          f"GENUINE {GENUINE[0]}-{GENUINE[1]} px/mm")
    print(f"  params   {p}\n")


# ------------------------------------------------------------------ control

def v_control(a, ctx):
    lum, board, outer, origin, ppm, spath, f, rid = ctx
    p = dict(DEFAULTS); p["down"] = a.down
    box = [int(v) for v in a.nrf_box.split(",")]
    print("d_darkpkg control -- the nRF52832-CIAA, and the ladder that can fail it\n")
    hdr(ctx, p)
    print(f"  POSITIVE CONTROL  nRF52832-CIAA, published body "
          f"{max(NRF_MM):.3f} x {min(NRF_MM):.3f} mm")
    print(f"    truth  {NRF_SOURCE}")
    print(f"    box    {tuple(box)} stored px -- generous; the detector is NOT told")
    print(f"           where the part is inside it, and the candidate is chosen by")
    print(f"           BOUNDARY SCORE, never by closeness to the published size.\n")

    res, pads = [], [int(v) for v in a.pads.split(",")]
    for pad in pads:
        b = [box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad]
        got, ppmd = detect_at(lum, board, ppm, p, mask_extra=boxmask(b, lum.shape),
                              z=a.zfloor)
        if not got:
            print(f"    pad {pad:3d}  nothing found"); res.append(None); continue
        c = max(got, key=lambda g: g["score"])
        L, W = c["long_px"] / ppmd, c["short_px"] / ppmd
        res.append(dict(pad=pad, long_mm=L, short_mm=W, score=c["score"],
                        theta_deg=c["theta_deg"], cx=c["cx"] * p["down"],
                        cy=c["cy"] * p["down"], n=len(got)))
        print(f"    pad {pad:3d}  {L:6.3f} x {W:6.3f} mm   score {c['score']:6.1f}  "
              f"theta {c['theta_deg']:5.1f}  ({len(got)} candidates in box)")
    ok = [r for r in res if r]
    if not ok:
        print("\n  FAIL  the control found nothing at any padding"); return None, 1
    Ls = np.array([r["long_mm"] for r in ok]); Ws = np.array([r["short_mm"] for r in ok])
    swing = 100 * (Ls.max() - Ls.min()) / np.median(Ls)
    swingW = 100 * (Ws.max() - Ws.min()) / np.median(Ws)
    print(f"\n    ROI-PADDING SWING  long {swing:.2f} %   short {swingW:.2f} %")
    print(f"    M08 attempt 3, the method this replaces, swung 34 % on this axis.")
    eL = 100 * (np.median(Ls) - max(NRF_MM)) / max(NRF_MM)
    eW = 100 * (np.median(Ws) - min(NRF_MM)) / min(NRF_MM)
    print(f"    MEASURED (median over paddings)  {np.median(Ls):.3f} x {np.median(Ws):.3f} mm")
    print(f"    PUBLISHED                        {max(NRF_MM):.3f} x {min(NRF_MM):.3f} mm")
    print(f"    ERROR   long {eL:+.2f} %   short {eW:+.2f} %")
    passed = abs(eL) <= a.tol and abs(eW) <= a.tol and swing <= a.swing_tol
    print(f"    {'PASS' if passed else 'FAIL'}  size within +/-{a.tol} %, "
          f"ROI swing within {a.swing_tol} %")

    c0 = ok[len(ok) // 2]
    step = boundary_step(lum, c0["cx"], c0["cy"], c0["theta_deg"],
                         c0["long_mm"] * ppm, c0["short_mm"] * ppm)
    print(f"\n  THE ASSUMPTION THE CONTROL SHARES WITH THE METHOD  (E07 sec.4)")
    print(f"    The nRF is BLUE epoxy, so its boundary STEP is large -- and boundary")
    print(f"    step is the one thing this method lives on.  A control that is easy in")
    print(f"    exactly the dimension that decides the black packages is not evidence.")
    print(f"    nRF52832 boundary step, measured: {step:+.1f} luma (outside minus inside)")
    for name, bx in [(k, [int(v) for v in b.split(",")])
                     for k, b in (s.split("=") for s in a.dark_boxes.split(";"))]:
        got, ppmd = detect_at(lum, board, ppm, p, mask_extra=boxmask(bx, lum.shape),
                              z=a.zfloor)
        if got:
            g = max(got, key=lambda x: x["score"])
            s2 = boundary_step(lum, g["cx"] * p["down"], g["cy"] * p["down"],
                               g["theta_deg"], g["long_px"] / ppmd * ppm,
                               g["short_px"] / ppmd * ppm)
            print(f"    {name:22s} boundary step {s2:+6.1f} luma   "
                  f"(best score in box {g['score']:.1f})")

    print(f"\n  THE CONTRAST LADDER -- the nRF's own step, shrunk, and re-detected")
    ladder = []
    for k in [float(v) for v in a.ladder.split(",")]:
        La = attenuate(lum, c0["cx"], c0["cy"], c0["theta_deg"],
                       c0["long_mm"] * ppm, c0["short_mm"] * ppm, k)
        st = boundary_step(La, c0["cx"], c0["cy"], c0["theta_deg"],
                           c0["long_mm"] * ppm, c0["short_mm"] * ppm)
        got, ppmd = detect_at(La, board, ppm, p,
                              mask_extra=boxmask(box, lum.shape), z=a.zfloor)
        near = [g for g in got
                if math.hypot(g["cx"] * p["down"] - c0["cx"],
                              g["cy"] * p["down"] - c0["cy"]) < 0.4 * c0["short_mm"] * ppm]
        b = max(near, key=lambda g: g["score"]) if near else None
        ladder.append(dict(k=k, step_luma=round(st, 1),
                           score=round(b["score"], 1) if b else 0.0,
                           long_mm=round(b["long_px"] / ppmd, 3) if b else None,
                           short_mm=round(b["short_px"] / ppmd, 3) if b else None))
        print(f"    k={k:4.2f}  step {st:+6.1f} luma   "
              f"score {ladder[-1]['score']:6.1f}   "
              f"{('%.3f x %.3f mm' % (ladder[-1]['long_mm'], ladder[-1]['short_mm'])) if b else 'NOT FOUND'}")

    print(f"\n  DELIBERATE BREAKS -- each must go RED")
    breaks = {}
    g1, _ = detect_at(lum, board, ppm, p,
                      mask_extra=lambda d: np.zeros((lum.shape[0] // d,
                                                     lum.shape[1] // d), bool), z=a.zfloor)
    breaks["empty_mask"] = len(g1) == 0
    print(f"    {'PASS' if breaks['empty_mask'] else 'FAIL'}  empty mask -> {len(g1)} found")
    Ls_, Ms_ = prep(lum, board, p["down"])
    g2 = DR.detect(Ls_, Ms_ & boxmask(box, lum.shape)(p["down"]), ppm / p["down"],
                   astep=p["astep"], smooth=p["smooth"], npeak=p["npeak"], nms=p["nms"],
                   z_thr=1e6)
    breaks["impossible_threshold"] = len(g2) == 0
    print(f"    {'PASS' if breaks['impossible_threshold'] else 'FAIL'}  an impossible "
          f"score requirement (1e6) -> {len(g2)} found")
    g3 = DR.detect(phase_scramble(Ls_), Ms_ & boxmask(box, lum.shape)(p["down"]),
                   ppm / p["down"], astep=p["astep"], smooth=p["smooth"],
                   npeak=p["npeak"], nms=p["nms"], z_thr=a.zfloor)
    s3 = max((g["score"] for g in g3), default=0.0)
    breaks["scramble_in_control_box"] = s3 < np.median([r["score"] for r in ok])
    print(f"    {'PASS' if breaks['scramble_in_control_box'] else 'FAIL'}  the SAME box, "
          f"phase-scrambled: best score {s3:.1f} against the control's "
          f"{np.median([r['score'] for r in ok]):.1f}")

    allok = passed and all(breaks.values())
    out = dict(**rid, verb="control", source=f["source"]["path"], px_per_mm=ppm, params=p,
               nrf=dict(published_mm=list(NRF_MM), truth_source=NRF_SOURCE,
                        roi_padding_stored_px=pads, per_padding=ok,
                        measured_long_mm=round(float(np.median(Ls)), 3),
                        measured_short_mm=round(float(np.median(Ws)), 3),
                        err_long_pct=round(eL, 2), err_short_pct=round(eW, 2),
                        roi_swing_long_pct=round(float(swing), 2),
                        roi_swing_short_pct=round(float(swingW), 2),
                        boundary_step_luma=round(step, 1),
                        implied_px_per_mm=round(float(np.median(Ls)) * ppm / max(NRF_MM), 2)),
               contrast_ladder=ladder, breaks=breaks,
               verdict="PASS" if allok else "FAIL")
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2); print(f"\n  wrote {a.json}")
    print(f"\n  {'PASS' if allok else 'FAIL'}  positive control, ROI sweep, breaks")
    return out, (0 if allok else 1)


# ------------------------------------------------------------------ probe / limit

SEEDS = {
    # name: (cx, cy, theta_deg, long_mm, short_mm)  -- stored px, read BY LOOKING at
    # native-resolution tiles.  These are SEEDS ONLY.  Nothing here is published as a
    # position: what is published is each side's own evidence, and the seed-jitter
    # table says how far the fit moves when the seed moves.
    "nRF52832_CIAA_control": (1205, 813, 68.1, 3.32, 2.97),
    "black_9oclock":         (544, 1397, 48.1, 2.75, 1.21),
    "plus_AKN_8H7":          (2415, 1457, 20.0, 1.65, 1.60),
    "black_05I_1A8":         (645, 1705, 20.0, 1.30, 1.10),
    "black_diode_lower":     (770, 2040, 25.0, 1.20, 0.95),
}


def v_probe(a, ctx):
    lum, board, outer, origin, ppm, spath, f, rid = ctx
    p = dict(DEFAULTS); p["down"] = a.down
    L, M = prep(lum, board, p["down"]); ppmd = ppm / p["down"]
    print("d_darkpkg probe -- each boundary measured ON ITS OWN, against two nulls\n")
    hdr(ctx, p)
    print("  THE TWO NULLS, both built with the SAME scan, span and search range:")
    nb = DR.side_bar(L, M, ppmd, 3.2 * ppmd, 3.0 * ppmd, n=a.null_n, scramble=True)
    nr = DR.side_bar(L, M, ppmd, 3.2 * ppmd, 3.0 * ppmd, n=a.null_n, scramble=False)
    print(f"    N1 phase-scrambled board   |z| p50 {nb['p50']:.1f}  p90 {nb['p90']:.1f}  "
          f"p99 {nb['p99']:.1f}  max {nb['max']:.1f}   (n={nb['n']})")
    print(f"    N3 REAL board, random place and random angle")
    print(f"       |z| p50 {nr['p50']:.1f}  p90 {nr['p90']:.1f}  p99 {nr['p99']:.1f}  "
          f"max {nr['max']:.1f}   (n={nr['n']})")
    print(f"    N3 is the one that decides: it asks whether a package boundary is")
    print(f"    EXCEPTIONAL among the straight structures this board already has --")
    print(f"    traces, pad rows, silkscreen, the rim.  N1 only asks whether it beats")
    print(f"    texture of the same spectrum.\n")
    bar = nr["p99"]
    rows = []
    for name, (cx, cy, th, lo, sh) in SEEDS.items():
        best = None
        jit = []
        for dx in (-30, 0, 30):
            for dy in (-30, 0, 30):
                r = DR.fit_sides(L, M, ppmd, (cx + dx) / p["down"], (cy + dy) / p["down"],
                                 th, sh * ppmd, lo * ppmd)
                jit.append(r)
                if best is None or sum(abs(s["z"]) for s in r["sides"].values() if s) > \
                        sum(abs(s["z"]) for s in best["sides"].values() if s):
                    best = r
        z = {k: (round(abs(v["z"]), 1) if v else None) for k, v in best["sides"].items()}
        sup = {k: (v is not None and abs(v) > bar) for k, v in z.items()}
        steps = side_steps(lum, cx, cy, th, sh * ppm, lo * ppm)
        Lm = np.array([max(r["w_px"], r["h_px"]) / ppmd for r in jit])
        Sm = np.array([min(r["w_px"], r["h_px"]) / ppmd for r in jit])
        Cx = np.array([r["cx"] * p["down"] for r in jit])
        Cy = np.array([r["cy"] * p["down"] for r in jit])
        seed_swing_mm = float(np.hypot(Cx.max() - Cx.min(), Cy.max() - Cy.min()) / ppm)
        nsup = sum(sup.values())
        rows.append(dict(name=name, seed_stored_px=[cx, cy], seed_theta_deg=th,
                         seed_long_mm=lo, seed_short_mm=sh,
                         side_abs_z=z, side_supported=sup, n_sides_supported=nsup,
                         side_step_luma_at_seed=steps,
                         fit_long_mm=round(float(np.median(Lm)), 3),
                         fit_short_mm=round(float(np.median(Sm)), 3),
                         fit_long_spread_mm=round(float(Lm.max() - Lm.min()), 3),
                         fit_short_spread_mm=round(float(Sm.max() - Sm.min()), 3),
                         seed_swing_mm=round(seed_swing_mm, 3)))
        print(f"  {name}")
        print(f"    |z| per side  L {z['left']}  R {z['right']}  T {z['top']}  B {z['bottom']}"
              f"   (bar = N3 p99 = {bar:.1f})")
        print(f"    step luma     L {steps['left']:+7.1f}  R {steps['right']:+7.1f}  "
              f"T {steps['top']:+7.1f}  B {steps['bottom']:+7.1f}   (at the SEED outline)")
        print(f"    sides clearing the bar: {nsup} of 4")
        print(f"    fit across 9 seeds: long {np.median(Lm):.3f} mm (spread "
              f"{Lm.max()-Lm.min():.3f}), short {np.median(Sm):.3f} mm (spread "
              f"{Sm.max()-Sm.min():.3f}), centre wanders {seed_swing_mm:.3f} mm")
    out = dict(**rid, verb="probe", source=f["source"]["path"], px_per_mm=ppm, params=p,
               nulls=dict(n1_phase_scramble=nb, n3_real_board_random=nr),
               admission_bar_abs_z=round(bar, 2), rows=rows)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2, default=float)
        print(f"\n  wrote {a.json}")
    return out


def v_limit(a, ctx):
    """A positive control at the REAL noise, with a truth I set: paste a rectangle
    of KNOWN size and KNOWN boundary step into the photograph and ask what step it
    takes for its sides to clear the real-board null.  E07 sec.4: a synthetic
    control that is cleaner than the photograph is not evidence, so this one is
    made OF the photograph."""
    lum, board, outer, origin, ppm, spath, f, rid = ctx
    p = dict(DEFAULTS); p["down"] = a.down
    L, M = prep(lum, board, p["down"]); ppmd = ppm / p["down"]
    print("d_darkpkg limit -- what boundary step would this photograph need?\n")
    hdr(ctx, p)
    nr = DR.side_bar(L, M, ppmd, 3.2 * ppmd, 3.0 * ppmd, n=a.null_n, scramble=False)
    bar = nr["p99"]
    if a.paste_at == "auto":
        # THE SITE IS A PARAMETER TOO.  The first version used the single quietest
        # window and it landed on the metal shield can -- found by DRAWING it and
        # looking, not by reasoning.  A can is smooth at 4.2 mm and so it wins a
        # gradient-energy contest while being nothing like the soldermask a package
        # actually sits on.  So: the N quietest NON-OVERLAPPING windows, the ladder
        # run at every one, and the spread reported.  One site is an anecdote.
        g = np.hypot(*np.gradient(ndimage.gaussian_filter(L, 1.0)))
        w = int(4.2 * ppmd)
        E = ndimage.uniform_filter(g, w)
        C = ndimage.uniform_filter(M.astype(float), w)
        E = np.where(C > 0.999, E, np.inf)
        if not np.isfinite(E).any():
            print("  CANNOT DETERMINE: no window of that size lies wholly on the board")
            sys.exit(2)
        sites, Ew = [], E.copy()
        for _ in range(a.sites):
            if not np.isfinite(Ew).any():
                break
            iy, ix = np.unravel_index(np.argmin(Ew), Ew.shape)
            sites.append((float(ix * p["down"]), float(iy * p["down"]), float(E[iy, ix])))
            y0, y1 = max(0, iy - w), iy + w
            x0, x1 = max(0, ix - w), ix + w
            Ew[y0:y1, x0:x1] = np.inf
        print(f"  {len(sites)} paste sites chosen AUTOMATICALLY: the quietest "
              f"NON-OVERLAPPING 4.2 mm windows lying wholly on the board.")
        for k, (sx, sy, e) in enumerate(sites):
            print(f"    site {k}  ({sx:6.0f},{sy:6.0f}) stored px   mean |grad| {e:5.2f}")
    else:
        v = [float(x) for x in a.paste_at.split(",")]
        sites = [(v[0], v[1], float("nan"))]
    lo, sh, th = 3.226, 2.956, 30.0
    print(f"  a {lo} x {sh} mm rectangle at theta {th}, pasted into the photograph itself")
    print(f"  bar = real-board null p99 = {bar:.1f}\n")
    yy, xx = np.mgrid[0:L.shape[0], 0:L.shape[1]]
    t = math.radians(th)
    steps = [float(x) for x in a.steps.split(",")]
    per_site, need3, need4 = [], [], []
    for k, (cx, cy, e) in enumerate(sites):
        u = (xx - cx / p["down"]) * math.cos(t) + (yy - cy / p["down"]) * math.sin(t)
        v = -(xx - cx / p["down"]) * math.sin(t) + (yy - cy / p["down"]) * math.cos(t)
        body = (np.abs(u) <= sh * ppmd / 2) & (np.abs(v) <= lo * ppmd / 2)
        rows = []
        print(f"\n  SITE {k} ({cx:.0f},{cy:.0f})  mean |grad| {e:.2f}")
        for step in steps:
            Lp = L.copy(); Lp[body] -= step
            r = DR.fit_sides(Lp, M, ppmd, cx / p["down"], cy / p["down"], th,
                             sh * ppmd, lo * ppmd, search=int(0.25 * sh * ppmd))
            z = {kk: (round(abs(s["z"]), 1) if s else None) for kk, s in r["sides"].items()}
            n = sum(1 for x in z.values() if x and x > bar)
            rows.append(dict(step_luma=step, abs_z=z, sides_clearing=n,
                             long_mm=round(max(r["w_px"], r["h_px"]) / ppmd, 3),
                             short_mm=round(min(r["w_px"], r["h_px"]) / ppmd, 3)))
            print(f"    step {step:6.1f} luma   |z| L {z['left']} R {z['right']} "
                  f"T {z['top']} B {z['bottom']}   sides clearing {n}/4   "
                  f"{rows[-1]['long_mm']:.3f} x {rows[-1]['short_mm']:.3f} mm")
        asc = sorted(rows, key=lambda r: r["step_luma"])
        n3 = next((r["step_luma"] for r in asc if r["sides_clearing"] >= 3), None)
        n4 = next((r["step_luma"] for r in asc if r["sides_clearing"] >= 4), None)
        need3.append(n3); need4.append(n4)
        per_site.append(dict(site=k, at_stored_px=[cx, cy], mean_abs_grad=e,
                             step_for_3_of_4=n3, step_for_4_of_4=n4, ladder=rows))
        print(f"    -> 3 of 4 sides at {n3} luma, 4 of 4 at {n4}")
    ok3 = [x for x in need3 if x]; ok4 = [x for x in need4 if x]
    print(f"\n  ACROSS {len(sites)} AUTOMATIC SITES:")
    print(f"    3 of 4 sides needs {min(ok3) if ok3 else None}-{max(ok3) if ok3 else None} luma"
          f"   ({len(ok3)}/{len(sites)} sites ever reach it)")
    print(f"    4 of 4 sides needs {min(ok4) if ok4 else None}-{max(ok4) if ok4 else None} luma"
          f"   ({len(ok4)}/{len(sites)} sites ever reach it)")
    out = dict(**rid, verb="limit", px_per_mm=ppm, params=p,
               sites=[[s[0], s[1], s[2]] for s in sites],
               paste_at_stored_px=[sites[0][0], sites[0][1]],
               rect_mm=[lo, sh], theta_deg=th,
               bar_abs_z=round(bar, 2), null=nr, per_site=per_site,
               step_for_3_of_4_luma=dict(min=min(ok3) if ok3 else None,
                                         max=max(ok3) if ok3 else None,
                                         n_sites_reaching=len(ok3), n_sites=len(sites)),
               step_for_4_of_4_luma=dict(min=min(ok4) if ok4 else None,
                                         max=max(ok4) if ok4 else None,
                                         n_sites_reaching=len(ok4), n_sites=len(sites)),
               ladder=per_site[0]["ladder"])
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2, default=float)
        print(f"\n  wrote {a.json}")
    return out


def v_stepaudit(a, ctx):
    """AUDIT MY OWN HEADLINE.  M11 reports the dark packages presenting "1-26 luma
    on most of their sides", and that number came from `side_steps` at a ROUGH,
    HAND-PLACED seed outline.

    On the rim, that same construction was measured to be DILUTED: a bad outline
    puts the inside band partly outside and vice versa, and the step reads low.
    A low step makes the gap to the detection limit look BIGGER, which flatters
    the conclusion I published.  So the check has to be run hardest here, because
    this is the result I am pleased with.

    The test: sweep the outline -- position, size, angle -- and take the LARGEST
    per-side step obtainable anywhere in that neighbourhood.  That is an upper
    bound on what a perfect outline could recover.  If it stays near the published
    band the headline stands; if it is far above, the headline understated what the
    packages present and must be corrected."""
    lum, board, outer, origin, ppm, spath, f, rid = ctx
    print("d_darkpkg stepaudit -- is my own published step number diluted?\n")
    print(f"  run_id   {rid['run_utc']} git {rid['git_rev']} image sha {rid['image_sha256_12']}")
    print(f"  SOURCE   {f['source']['path']}")
    print(f"  M11 published: the packages present 1-26 luma on most of their sides,")
    print(f"  the nRF 75 on its best one, against a needed 100-160.\n")
    rows = []
    for name, (cx, cy, th, lo, sh) in SEEDS.items():
        seed = side_steps(lum, cx, cy, th, sh * ppm, lo * ppm)
        seed_best = max(abs(v) for v in seed.values())
        best = {k: 0.0 for k in seed}
        for dx in range(-24, 25, 8):
            for dy in range(-24, 25, 8):
                for dth in (-8, -4, 0, 4, 8):
                    for fs in (0.85, 0.925, 1.0, 1.075, 1.15):
                        st = side_steps(lum, cx + dx, cy + dy, th + dth,
                                        sh * ppm * fs, lo * ppm * fs)
                        for k, v in st.items():
                            if abs(v) > abs(best[k]):
                                best[k] = v
        bb = max(abs(v) for v in best.values())
        # the number M11 actually leans on is the MEDIAN side, not the best one
        seed_med = float(np.median([abs(v) for v in seed.values()]))
        best_med = float(np.median([abs(v) for v in best.values()]))
        rows.append(dict(name=name, seed_side_step=seed, seed_largest=seed_best,
                         swept_side_step=best, swept_largest=round(bb, 1),
                         seed_median_side=round(seed_med, 1),
                         swept_median_side=round(best_med, 1),
                         inflation_largest=round(bb / seed_best, 2) if seed_best else None))
        print(f"  {name:24s} seed: largest {seed_best:5.0f}  median side {seed_med:5.0f}")
        print(f"  {'':24s} SWEPT: largest {bb:5.0f}  median side {best_med:5.0f}   "
              f"x{bb/seed_best if seed_best else float('nan'):.2f} on the largest")
    sw_med = [r["swept_median_side"] for r in rows]
    sw_big = [r["swept_largest"] for r in rows]
    print(f"\n  SWEPT median side across the five: {min(sw_med):.0f}-{max(sw_med):.0f} luma")
    print(f"  SWEPT largest side across the five: {min(sw_big):.0f}-{max(sw_big):.0f} luma")
    print(f"\n  A swept maximum is an UPPER BOUND and is itself optimistic: sweeping")
    print(f"  4275 outlines per package and keeping the best takes the maximum of a")
    print(f"  noisy field, so some of this rise is selection, not signal. It bounds")
    print(f"  the dilution; it does not measure the step.")
    out = dict(**rid, verb="stepaudit", source=f["source"]["path"], px_per_mm=ppm,
               published_claim="packages present 1-26 luma on most sides, nRF 75 on its best",
               swept_median_side_range=[min(sw_med), max(sw_med)],
               swept_largest_range=[min(sw_big), max(sw_big)],
               caveat="a swept maximum is an upper bound taken over 4275 outlines per "
                      "package; part of the rise is selection over a noisy field",
               rows=rows)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2, default=float)
        print(f"  wrote {a.json}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["bar", "control", "run", "probe", "limit", "stepaudit"])
    ap.add_argument("--fit", default=os.path.join(HERE, "..", "metrology",
                                                  "c_register-fit-boardscale.json"))
    ap.add_argument("--down", type=int, default=DEFAULTS["down"])
    ap.add_argument("--zfloor", type=float, default=4.0)
    ap.add_argument("--bar", type=float, default=None)
    ap.add_argument("--tile-mm", type=float, default=4.0)
    ap.add_argument("--nrf-box", default="1040,660,1400,990")
    ap.add_argument("--pads", default="0,20,40,60,80,120")
    ap.add_argument("--ladder", default="1.0,0.7,0.5,0.35,0.25,0.15,0.1")
    ap.add_argument("--dark-boxes",
                    default="black_9oclock=380,1200,760,1650;plus_AKN=2280,1330,2640,1620")
    ap.add_argument("--tol", type=float, default=6.0)
    ap.add_argument("--swing-tol", type=float, default=6.0)
    ap.add_argument("--null-n", type=int, default=60)
    ap.add_argument("--paste-at", default="auto")
    ap.add_argument("--sites", type=int, default=5)
    ap.add_argument("--steps", default="160,120,80,60,45,35,25,18,12,8")
    ap.add_argument("--png", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    lum, board, outer, origin, ppm, spath, f = MD.board_frame(a.fit)
    ctx = (lum, board, outer, origin, ppm, spath, f, run_id(spath))
    if a.verb == "bar":
        v_bar(a, ctx); sys.exit(0)
    if a.verb == "control":
        _, code = v_control(a, ctx); sys.exit(code)
    if a.verb == "probe":
        v_probe(a, ctx); sys.exit(0)
    if a.verb == "limit":
        v_limit(a, ctx); sys.exit(0)
    if a.verb == "stepaudit":
        v_stepaudit(a, ctx); sys.exit(0)
    print("run: not yet wired"); sys.exit(2)


if __name__ == "__main__":
    main()
