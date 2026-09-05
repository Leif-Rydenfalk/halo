#!/usr/bin/env python3
"""p_compare.py -- THE SIDE-BY-SIDE. Our render beside Apple's photograph at ONE shared
px/mm, plus our geometry drawn ON Apple's photograph.

Lane L5 BOARD BUILD, halo Replica.  This picture is what this lane is judged on.
Exit code IS the verdict: 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

REGISTRATION IS BY CONSTRUCTION, NOT BY ALIGNMENT.
  The frame (origin_px, px/mm) in which every component position was measured is a
  stated property of the photograph.  The crop is taken about that origin at that
  scale, so panel 2 and panel 1 are in the same millimetres WITHOUT anything being
  fitted to make them agree.  Nothing here nudges one picture onto the other.

PANELS
  1 OURS     -- p_render.py, uncaptioned, at the montage scale
  2 APPLE'S  -- the photograph, cropped about the measured board centre, resampled to
                the SAME px/mm
  3 OVERLAY  -- our fitted outline, our hole and EVERY drawn component marker, on
                Apple's photograph.  Resemblance is what panels 1 and 2 show;
                DISAGREEMENT is what panel 3 shows, and only panel 3 is evidence.

CONTROLS
  X1 scale match     both silhouettes measured back off the finished panels, 2 x mean
                     radius in mm must agree within 1%
  X2 non-blank       the montage is read BACK off disk
  X3 mis-registration  --break-rotation N rotates OUR geometry N degrees before
                     overlaying; X4 and X5 must both get worse.  A comparison whose
                     numbers do not move when the alignment is destroyed measures nothing.
  X4 outline residual  RMS radial disagreement, ours vs the photograph's own silhouette
  X5 COMPONENT LANDING -- the one that tests the components rather than the outline.
                     For every drawn marker, the photograph's luma at that position is
                     compared against the SAME statistic at randomly drawn positions
                     inside the annulus.  Bright-metal markers must separate from
                     random.  If they do not, the positions are decoration.  The random
                     draw IS the negative control and it is reported, always.
"""
import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

PASS, FAIL, CANNOT = 0, 1, 2
HERE = os.path.dirname(os.path.abspath(__file__))
REPL = os.path.dirname(HERE)
BOARD_DIR = os.path.join(REPL, "board")
ROOT = os.path.dirname(os.path.dirname(REPL))
BG = (243, 242, 238)
INK = (26, 26, 28)
PROV = (208, 92, 24)
CYAN = (0, 226, 234)
GAPC = (255, 60, 190)

sys.path.insert(0, HERE)
import p_render as PR                                    # ONE definition of the geometry


def say(*a):
    print(*a, file=sys.stderr)


def font(sz, bold=False):
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
              "/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def board_mask(a_l):
    m = a_l < 120
    lab, n = ndimage.label(m)
    if n == 0:
        return None
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    return ndimage.binary_fill_holes(lab == (int(np.argmax(sizes)) + 1))


def radial(mask, n=720):
    """r(theta) of a mask, IMAGE CONVENTION (+y down), same as everything else here."""
    ys, xs = np.nonzero(mask)
    cx, cy = xs.mean(), ys.mean()
    th = np.deg2rad(np.arange(n) * 360.0 / n)
    rr = np.arange(1.0, 0.75 * max(mask.shape), 0.5)
    R, T = np.meshgrid(rr, th)
    X = np.rint(cx + R * np.cos(T)).astype(int)
    Y = np.rint(cy + R * np.sin(T)).astype(int)
    ok = (X >= 0) & (Y >= 0) & (X < mask.shape[1]) & (Y < mask.shape[0])
    hit = np.zeros_like(R, dtype=bool)
    hit[ok] = mask[Y[ok], X[ok]]
    r = np.array([rr[np.nonzero(h)[0][-1]] if h.any() else np.nan for h in hit])
    return cx, cy, np.rad2deg(th), r


def crop_about(img, cx, cy, half_px):
    """Crop about a STATED centre, padding rather than shifting if the frame runs out.
    Shifting would silently move the origin and every millimetre with it."""
    l, t = int(round(cx - half_px)), int(round(cy - half_px))
    r, b = int(round(cx + half_px)), int(round(cy + half_px))
    out = Image.new("RGB", (r - l, b - t), (238, 236, 232))
    sl, st = max(l, 0), max(t, 0)
    sr, sb = min(r, img.width), min(b, img.height)
    out.paste(img.crop((sl, st, sr, sb)), (sl - l, st - t))
    return out


def rot(pts, deg):
    if not deg:
        return pts
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(x * c - y * s, x * s + y * c) for x, y in pts]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", default=os.path.join(ROOT, "images", "airtag",
                                                    "oflynn-backside-fullres.jpeg"))
    ap.add_argument("--photo-label",
                    default="APPLE'S  O'Flynn teardown, the SoC/shield-can side")
    ap.add_argument("--board", default=os.path.join(BOARD_DIR, "board.json"))
    ap.add_argument("--fit", default=os.path.join(BOARD_DIR, "outline",
                                                  "outline-fit-oflynn.json"))
    ap.add_argument("--handoff", default=os.path.join(REPL, "metrology",
                                                      "HANDOFF-positions-front.json"))
    ap.add_argument("--apple-profile", default=os.path.join(
        REPL, "metrology", "outline-raw-oflynn-front.json"),
        help="APPLE'S OWN SILHOUETTE, as measured off this photograph by L1 in this "
             "same frame. It is used instead of re-thresholding the crop because the "
             "crop contains dark background furniture -- wooden blocks above and below "
             "the board -- that no luma threshold can separate from the board, and "
             "which inflated Apple's measured diameter by 3.2 pct. Stated, not hidden.")
    ap.add_argument("--px-per-mm", type=float, default=48.0,
                    help="the ONE shared scale of the montage")
    ap.add_argument("--margin-mm", type=float, default=1.0)
    ap.add_argument("--break-rotation", type=float, default=0.0)
    ap.add_argument("--out", default=os.path.join(BOARD_DIR, "out", "compare-front.png"))
    a = ap.parse_args()

    board = json.load(open(a.board))
    fit = json.load(open(a.fit))
    handoff = json.load(open(a.handoff))
    ppm_ph = fit["scale"]["px_per_mm"]
    ox, oy = fit["frame"]["origin_px"]

    say("INPUT")
    say(f"  photo        {os.path.relpath(a.photo, ROOT)}")
    say(f"  frame        origin_px ({ox:.1f},{oy:.1f})  {ppm_ph:.4f} px/mm")
    say(f"  frame basis  {fit['scale']['basis']}")
    say(f"  montage      {a.px_per_mm} px/mm, BOTH panels")
    if a.break_rotation:
        say(f"  X3 BREAK     our geometry rotated {a.break_rotation} deg on purpose")
    say("")

    # ---- geometry, in mm, from the SAME functions the renderer uses
    k = (board["parameters"]["outer_diameter_mm"]["value"]
         / fit["outer"]["circle_diameter_mm"])
    th, r_mm, _ = PR.outer_poly(fit)
    outer = rot([(k * rr * math.cos(math.radians(t)), k * rr * math.sin(math.radians(t)))
                 for t, rr in zip(th, r_mm)], a.break_rotation)
    inner = rot([(k * x, k * y) for x, y in PR.hole_poly(fit)], a.break_rotation)
    comps, skipped, gaps = PR.load_components(handoff, PR.orientation_table())
    cpts = rot([(k * c["x"], k * c["y"]) for c in comps], a.break_rotation)
    gpts = rot([(k * g["x"], k * g["y"]) for g in gaps], a.break_rotation)

    Rmax = max(math.hypot(x, y) for x, y in outer)
    half = Rmax + a.margin_mm

    # ---- panel 1
    ours_png = os.path.join(BOARD_DIR, "out", ".compare-ours.png")
    r = subprocess.run([sys.executable, os.path.join(HERE, "p_render.py"),
                        "--board", a.board, "--fit", a.fit, "--handoff", a.handoff,
                        "--px-per-mm", str(a.px_per_mm), "--margin-mm", str(a.margin_mm),
                        "--no-caption", "--out", ours_png], capture_output=True, text=True)
    if r.returncode != 0:
        say("p_render.py refused; the montage inherits its verdict:")
        say(r.stderr.strip()[-900:])
        sys.exit(r.returncode)
    ours = Image.open(ours_png).convert("RGB")

    # ---- panel 2: cropped about the STATED origin, at the STATED scale
    full = Image.open(a.photo).convert("RGB")
    ph = crop_about(full, ox, oy, half * ppm_ph)
    side = int(round(2 * half * a.px_per_mm))
    ph = ph.resize((side, side), Image.LANCZOS)
    say(f"photo cropped about the measured board centre, {ph.size[0]}x{ph.size[1]} px "
        f"at {a.px_per_mm} px/mm  (no alignment was fitted)")
    if ours.size != ph.size:
        ours = ours.resize(ph.size, Image.LANCZOS)

    # ---- OURS: measured off the finished panel, so this tests the DRAWING
    mo = board_mask(np.asarray(ours.convert("L")).astype(float))
    if mo is None:
        say("X2 FIRED: no board silhouette in our panel.")
        sys.exit(CANNOT)
    _, _, oth, orad = radial(mo)
    ours_mm = orad / a.px_per_mm
    if a.break_rotation:
        # X3 must reach X4 as well as X5. Panel 1 is rendered by a subprocess that knows
        # nothing about the break, so the break is applied to the profile read off it.
        # Without this line X4 sat at 0.413 mm under a 12 deg rotation and the control
        # was a decoration on that number.
        ours_mm = np.interp((oth + a.break_rotation) % 360, oth, ours_mm, period=360)

    # ---- APPLE'S: L1's measurement of THIS photograph, in THIS frame.
    # Re-thresholding the crop was tried and rejected: the wooden blocks in the
    # photograph's background merge into the board blob and inflated Apple's
    # diameter by 3.20%. That is a defect in the instrument, not a disagreement
    # about the board, and swapping in a worse instrument to make a number look
    # better would be the same error in the other direction.
    ap_raw = json.load(open(a.apple_profile))
    art = np.array(ap_raw["outer_r_theta"], float)
    a_th, a_r = art[:, 0], art[:, 1] / ppm_ph
    tt = np.concatenate([a_th - 360, a_th, a_th + 360])
    vv = np.concatenate([a_r, a_r, a_r])
    apple_mm = np.interp(oth, tt, vv)
    near = np.min(np.abs(((oth[:, None] - tt[None, :] + 180) % 360) - 180), axis=1)
    apple_mm = np.where(near <= 1.0, apple_mm, np.nan)   # never interpolate a gap
    say(f"Apple's silhouette: L1's own measurement of this photograph, "
        f"{len(a_th)} rays; {int(np.isnan(apple_mm).sum())}/{len(oth)} comparison rays "
        f"fall in a measurement gap and are DROPPED, not interpolated")

    pth = oth
    od = 2 * np.nanmean(np.where(np.isfinite(apple_mm), ours_mm, np.nan))
    pd = 2 * np.nanmean(apple_mm)
    x1 = abs(od - pd) / pd <= 0.01
    say(f"X1 scale match: OURS 2 x mean r {od:.3f} mm | APPLE'S {pd:.3f} mm | "
        f"delta {abs(od-pd)/pd*100:.2f}% -> {'ok' if x1 else 'FIRED'}")

    resid = ours_mm - apple_mm
    good = np.isfinite(resid)
    rms = float(np.sqrt(np.nanmean(resid[good] ** 2)))
    p95 = float(np.nanpercentile(np.abs(resid[good]), 95))
    say(f"X4 outline residual (OUR DRAWN PANEL vs Apple's measured silhouette) over {good.sum()} rays: RMS {rms:.3f} mm, "
        f"p95 {p95:.3f} mm, max {np.nanmax(np.abs(resid[good])):.3f} mm")

    # ---- X5 COMPONENT LANDING, with its negative control
    L = np.asarray(ph.convert("L")).astype(float)
    c0 = side / 2.0
    def luma_at(x_mm, y_mm, rad_mm=0.18):
        px, py = c0 + x_mm * a.px_per_mm, c0 + y_mm * a.px_per_mm
        rr = max(1, int(rad_mm * a.px_per_mm))
        x0, x1_, y0, y1_ = int(px - rr), int(px + rr + 1), int(py - rr), int(py + rr + 1)
        if x0 < 0 or y0 < 0 or x1_ > side or y1_ > side:
            return np.nan
        return float(np.median(L[y0:y1_, x0:x1_]))
    hit = np.array([luma_at(x, y) for x, y in cpts])
    rng = np.random.default_rng(3)
    inner_r = 0.5 * fit["inner"]["two_a_mm"] * k
    ctrl = []
    while len(ctrl) < 4000:
        t = rng.uniform(0, 2 * math.pi)
        rr = math.sqrt(rng.uniform((inner_r + 0.4) ** 2, (Rmax - 0.4) ** 2))
        v = luma_at(rr * math.cos(t), rr * math.sin(t))
        if np.isfinite(v):
            ctrl.append(v)
    ctrl = np.array(ctrl)
    hit_ok = hit[np.isfinite(hit)]
    med_h, med_c = float(np.median(hit_ok)), float(np.median(ctrl))
    thr = float(np.percentile(ctrl, 90))
    frac_h = float((hit_ok > thr).mean())
    frac_c = 0.10
    say(f"X5 component landing: median luma under our {len(hit_ok)} markers "
        f"{med_h:.1f} vs {len(ctrl)} RANDOM annulus positions {med_c:.1f}")
    say(f"   fraction above the random-90th-percentile ({thr:.1f}): "
        f"markers {frac_h*100:.1f}%  |  random 10.0% by construction  "
        f"-> enrichment {frac_h/frac_c:.2f}x")
    x5 = frac_h > 0.25          # 2.5x the random rate; stated once, here
    if not x5:
        say("X5 FIRED: our markers are not landing on anything brighter than a random "
            "spot on the annulus. The positions would be decoration.")

    # ---- panel 3
    ov = ph.copy()
    dv = ImageDraw.Draw(ov, "RGBA")
    def P(p):
        return (c0 + p[0] * a.px_per_mm, c0 + p[1] * a.px_per_mm)
    # THE OUTLINE IS COLOURED BY ITS OWN DISAGREEMENT, per angle, so the picture says
    # WHERE it is not close instead of leaving that to prose.
    a_th_s = np.array(ap_raw["outer_r_theta"], float)
    tt2 = np.concatenate([a_th_s[:, 0] - 360, a_th_s[:, 0], a_th_s[:, 0] + 360])
    vv2 = np.concatenate([a_th_s[:, 1] / ppm_ph] * 3)
    n_out = len(outer)
    ang_out = np.arange(n_out) * 360.0 / n_out + a.break_rotation
    ap_at = np.interp(ang_out % 360, tt2, vv2)
    near_out = np.min(np.abs(((ang_out[:, None] % 360) - tt2[None, :] + 180) % 360 - 180),
                      axis=1)
    ours_at = np.array([math.hypot(x, y) for x, y in outer])
    dres = np.where(near_out <= 1.0, np.abs(ours_at - ap_at), np.nan)
    BANDS = [(0.15, (40, 200, 90)), (0.40, (245, 200, 40)), (1e9, (240, 60, 60))]
    GREY = (150, 150, 155)
    for i in range(n_out):
        v = dres[i]
        if not np.isfinite(v):
            col = GREY
        else:
            col = next(c for t_, c in BANDS if v <= t_)
        dv.line([P(outer[i]), P(outer[(i + 1) % n_out])], fill=col + (255,), width=4)
    band_counts = dict(
        within_0_15=int(np.nansum(dres <= 0.15)),
        between_0_15_and_0_40=int(np.nansum((dres > 0.15) & (dres <= 0.40))),
        beyond_0_40=int(np.nansum(dres > 0.40)),
        no_apple_ray=int(np.isnan(dres).sum()), total=n_out)
    say(f"X6 outline disagreement map (model vs Apple's measured rays, {n_out} "
        f"samples): <=0.15 mm {band_counts['within_0_15']}, 0.15-0.40 mm "
        f"{band_counts['between_0_15_and_0_40']}, >0.40 mm "
        f"{band_counts['beyond_0_40']}, no Apple ray {band_counts['no_apple_ray']}")
    worst = []
    dd = np.where(np.isfinite(dres), dres, -1)
    bad = dd > 0.40
    i = 0
    while i < n_out:
        if bad[i]:
            j = i
            while j + 1 < n_out and bad[j + 1]:
                j += 1
            if (j - i + 1) * 360.0 / n_out >= 3.0:
                worst.append((round(ang_out[i] % 360, 1), round(ang_out[j] % 360, 1),
                              round(float(dd[i:j + 1].max()), 3)))
            i = j + 1
        else:
            i += 1
    for w in worst:
        say(f"   worst arc {w[0]:.1f}-{w[1]:.1f} deg, peak {w[2]:.3f} mm")
    dv.line([P(p) for p in inner] + [P(inner[0])], fill=CYAN + (255,), width=3)
    for (x, y), c in zip(cpts, comps):
        px, py = P((x, y))
        if c["sized"]:
            PR.rrect(dv, px, py, k * c["long_mm"] * a.px_per_mm,
                     k * c["short_mm"] * a.px_per_mm, c["angle"], None,
                     outline=CYAN + (255,), w=2)
        else:
            rr = 0.30 * a.px_per_mm
            dv.ellipse([px - rr, py - rr, px + rr, py + rr], outline=CYAN + (200,), width=2)
    for x, y in gpts:
        px, py = P((x, y))
        rr = 0.55 * a.px_per_mm
        dv.ellipse([px - rr, py - rr, px + rr, py + rr], outline=GAPC + (255,), width=3)

    # ---- montage
    cols = [("OURS  halo Replica R0", ours), (a.photo_label, ph),
            ("OVERLAY  our outline, hole and every marker, on Apple's", ov)]
    cw, ch = ph.size
    head, gap = 66, 22
    foot = 340
    W, H = 3 * cw + 4 * gap, head + ch + foot
    m = Image.new("RGB", (W, H), BG)
    dm = ImageDraw.Draw(m, "RGBA")
    fb, fs, ft = font(30, True), font(20), font(17)
    for i, (t, im2) in enumerate(cols):
        x = gap + i * (cw + gap)
        m.paste(im2, (x, head))
        dm.text((x, 22), t, font=fb, fill=INK)
    bx, by = gap, head + ch + 20
    dm.line([(bx, by), (bx + 10 * a.px_per_mm, by)], fill=INK, width=4)
    for t in range(11):
        dm.line([(bx + t * a.px_per_mm, by),
                 (bx + t * a.px_per_mm, by - (12 if t % 5 else 20))], fill=INK, width=2)
    dm.text((bx + 10 * a.px_per_mm + 12, by - 12), "10 mm  (all three panels)",
            font=fs, fill=INK)

    p = board["parameters"]
    od_p = p["outer_diameter_mm"]
    lines = [
        (f"X4 outline residual   RMS {rms:.3f} mm   p95 {p95:.3f} mm   over "
         f"{good.sum()} rays", INK),
        (f"X5 component landing  median luma under our markers {med_h:.1f} vs random "
         f"annulus {med_c:.1f};  {frac_h*100:.1f}% of markers above the random 90th "
         f"percentile vs 10% by construction  ->  {frac_h/frac_c:.2f}x enrichment", INK),
        (f"X1 scale match        OURS {od:.3f} mm   APPLE'S {pd:.3f} mm   "
         f"delta {abs(od-pd)/pd*100:.2f}%   (registration is by construction, "
         f"nothing was fitted to make these agree)", INK),
        (f"X6 disagreement map  the OVERLAY OUTLINE IS COLOURED BY ITS OWN ERROR: "
         f"green <=0.15 mm ({band_counts['within_0_15']*100//band_counts['total']}% of "
         f"the perimeter), yellow 0.15-0.40 mm "
         f"({band_counts['between_0_15_and_0_40']*100//band_counts['total']}%), "
         f"red >0.40 mm ({band_counts['beyond_0_40']*100//band_counts['total']}%), "
         f"grey = no measured ray "
         f"({band_counts['no_apple_ray']*100//band_counts['total']}%)", INK),
        ("worst arcs (deg, peak mm): " + ("  ".join(f"{a0:.0f}-{a1:.0f}: {v:.2f}"
                                                    for a0, a1, v in worst)
                                          or "none beyond 0.40 mm"), INK),
        ("Apple's silhouette is L1's measurement of THIS photograph in THIS frame. "
         "Re-thresholding the crop was tried and REJECTED: the wooden blocks behind "
         "the board merge into it and inflated Apple's diameter by 3.20%.",
         (110, 110, 114)),
        ("", INK),
        (f"outer diameter {od_p['value']:.3f} mm AS DRAWN - {od_p['state']}; "
         f"bound {od_p['bound_mm'][0]}-{od_p['bound_mm'][1]} mm and if it moves it "
         f"moves DOWN", PROV),
        (f"centre hole {p['centre_hole']['state']} - no diameter is published; "
         f"three fits give n = 2.00 (pinned) / "
         f"{fit['inner']['n']:.2f} / 2.70 and disagree in different directions", PROV),
        (f"thickness {p['thickness_mm']['value']:.2f} mm as-drawn, below both fab "
         f"floors - a fact about US, not about Apple.   "
         f"{p['layer_count']['value']} layers - {p['layer_count']['state']}", PROV),
        (f"{len([c for c in comps if c['sized']])} components drawn to MEASURED SIZE, "
         f"{len([c for c in comps if not c['sized']])} drawn as POSITION ONLY (fixed "
         f"0.30 mm ring, NOT a footprint), "
         f"{len([c for c in comps if c['suspect']])} may be grey RIM MATERIAL not parts",
         PROV),
        (f"KNOWINGLY INCOMPLETE: {len(skipped)} rows not drawn at all, "
         f"{len(gaps)} named absences (magenta). Every neutral-black IC body is "
         f"CANNOT DETERMINE (M08) - INCLUDING THE LARGEST ONE. The dark areas SHOULD "
         f"look sparse.", PROV),
        ("NOT DRAWN AND NOT AN OVERSIGHT: rim pads (count CANNOT DETERMINE, closed), "
         "the 3 antennas (not on this PCB at all), the NFC/voice coil (wound wire), "
         "the U1 footprint (size CANNOT DETERMINE). U1 IS UNPOPULATED.", PROV),
        ("", INK),
        (f"scale basis: {fit['scale']['basis']}", (110, 110, 114)),
        (f"positional floor: {handoff['uncertainty']['note']}", (110, 110, 114)),
        ("faces are named by what is on them; 'front' means two different faces across "
         "three sources and is not used here", (110, 110, 114)),
    ]
    y = by + 28
    for line, col in lines:
        if line:
            dm.text((bx, y), line, font=ft, fill=col)
        y += 20
    if a.break_rotation:
        dm.text((bx + cw + gap, by - 4),
                f"X3 CONTROL ACTIVE: our geometry rotated {a.break_rotation} deg on purpose",
                font=fs, fill=(200, 0, 0))

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    m.save(a.out)
    say(f"\nwrote {a.out}  {W}x{H}")
    back = np.asarray(Image.open(a.out).convert("L")).astype(float)
    x2 = back.std() > 5 and (back < 120).mean() > 0.02
    say(f"X2 non-blank: sd {back.std():.2f}, dark {(back<120).mean():.4f} -> "
        f"{'ok' if x2 else 'FIRED'}")

    code = PASS if (x1 and x2 and x5) else FAIL
    say({0: "PASS", 1: "FAIL", 2: "CANNOT DETERMINE"}[code])
    print(json.dumps(dict(x6=band_counts, worst_arcs=worst,
                          rms_mm=rms, p95_mm=p95, ours_dia_mm=od, apple_dia_mm=pd,
                          rays=int(good.sum()), rotation_deg=a.break_rotation,
                          x5_marker_median_luma=med_h, x5_random_median_luma=med_c,
                          x5_enrichment=frac_h / frac_c)))
    sys.exit(code)


if __name__ == "__main__":
    main()
