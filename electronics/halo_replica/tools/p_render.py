#!/usr/bin/env python3
"""p_render.py -- draw the halo Replica main board: FITTED outline + MEASURED components.

Lane L5 BOARD BUILD.  Exit code IS the verdict: 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

WHAT CHANGED FROM THE FIRST VERSION
  It no longer draws the per-degree silhouette.  It draws p_fit.py's manufacturable
  primitives (a circle clipped by straight chords, a superellipse hole) and it draws
  the 100 measured features from L1's handoff, each one under the flag that row carries.

THE BOARD IS PARAMETERISED BY ONE NUMBER.
  board.json parameters.outer_diameter_mm.value.  The fitted shape is normalised by
  its OWN fitted diameter and multiplied by that one number, so outline, hole and every
  component position scale together.  No diameter is hard-coded here.

WHAT IS DELIBERATELY NOT DRAWN, and each has a different reason
  3 handoff rows flagged do_not_draw_as_component  (2 merged pad runs + 1 edge-bright strip)
  rim pads          - count CANNOT DETERMINE, closed (M03/M05)
  antennas          - not on this PCB at all (E01)
  the NFC coil      - wound wire, not copper
  the U1 footprint  - size CANNOT DETERMINE (6.735-7.891 mm on operator padding alone)
  every neutral-black IC body - CANNOT DETERMINE (M08)
  Their absence is COUNTED ON THE PICTURE.  A board that looks complete when it is not
  is the one failure this lane cannot recover from.

CONTROLS (all fire; see --break-* and p_render_selftest)
  R1 non-blank     the PNG is read BACK off disk and must not be blank or near-blank
  R2 annulus       centre pixel must be background, 0.8R must be board.  A filled disc
                   passes every "the file is not empty" test and fails here.
  R3 scale         the DRAWN outer extent, measured off the finished PNG at the px/mm
                   the CALLER asked for, must match the stated diameter within 1%.
                   The draw scale and the check scale deliberately do not share a
                   number -- feeding the same wrong scale to both cancels and passes
                   a broken build, which is what happened the first time this was written.
  R4 caveats       every PROVISIONAL / BOUNDED / CANNOT DETERMINE state is READ FROM
                   board.json and stamped on the picture. Nothing here is hardcoded.
  R5 components    the number of markers actually drawn is recounted off the drawing
                   commands and must equal the number the flags say should be drawn.
                   A renderer that silently dropped a marker would look fine.
  R6 no-invention  every drawn marker must trace to a row id or a named known_gap.
                   There is no path in this file that places a part from anywhere else.
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PASS, FAIL, CANNOT = 0, 1, 2
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BOARD_DIR = os.path.join(ROOT, "board")

BG        = (243, 242, 238)
MASK      = (34, 26, 33)        # Apple's near-black soldermask, faintly aubergine
MASK_HI   = (58, 46, 57)
MASK_EDGE = (96, 82, 95)
METAL     = (206, 210, 214)     # bright metal: pad, termination, can or solder
BLUE      = (46, 62, 104)       # the blue-bodied packages
POSONLY   = (150, 146, 138)     # position known, size NOT
SUSPECT   = (214, 122, 36)      # may be the grey rim material, not a part
GAP       = (208, 60, 150)      # named absence: eyeballed, NOT measured
PROV      = (214, 92, 24)       # this arc is a guess
INK       = (28, 28, 30)
SILK      = (226, 224, 218)


def say(*a):
    print(*a, file=sys.stderr)


def font(sz, bold=False):
    for p in (("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
               "/System/Library/Fonts/Supplemental/Arial.ttf"),
              "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


# ---------------------------------------------------------------- geometry
def outer_poly(fit, n=2880):
    """r(theta) of the FITTED model, in mm, in the board frame. Returns also a
    per-sample flag saying whether that angle carries any measured ray at all."""
    o = fit["outer"]
    ppm = fit["scale"]["px_per_mm"]
    th = np.arange(n) * 360.0 / n
    t = np.deg2rad(th)
    cx, cy = o["circle_centre_px"]
    R = o["circle_R_px"]
    b = cx * np.cos(t) + cy * np.sin(t)
    disc = np.maximum(b * b - (cx * cx + cy * cy - R * R), 0.0)
    r = b + np.sqrt(disc)
    for c in o["chords"]:
        den = c["nx"] * np.cos(t) + c["ny"] * np.sin(t)
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.minimum(r, np.where(den > 1e-9, c["d"] / den, np.inf))
    unmeasured = np.zeros(n, bool)
    for a0, a1, w in o["unmeasured_arcs_deg"]:
        if a1 >= a0:
            unmeasured |= (th > a0) & (th < a1)
        else:                                    # the gap wraps through 0
            unmeasured |= (th > a0) | (th < a1)
    return th, r / ppm, unmeasured


def hole_poly(fit, n=1440):
    """The superellipse hole, in mm, relative to the BOARD centre."""
    i = fit["inner"]
    ppm = fit["scale"]["px_per_mm"]
    ox, oy = fit["frame"]["origin_px"]
    cx = (i["centre_px"][0] - ox) / ppm
    cy = (i["centre_px"][1] - oy) / ppm
    a, b, e = i["two_a_mm"] / 2.0, i["two_b_mm"] / 2.0, i["n"]
    phi = math.radians(i["phi_deg"])
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    ct, st = np.cos(t), np.sin(t)
    u = np.sign(ct) * np.abs(ct) ** (2.0 / e) * a
    v = np.sign(st) * np.abs(st) ** (2.0 / e) * b
    x = cx + u * math.cos(phi) - v * math.sin(phi)
    y = cy + u * math.sin(phi) + v * math.cos(phi)
    return list(zip(x, y))


# ---------------------------------------------------------------- components
def load_components(handoff, angles):
    """Turn 100 handoff rows into draw instructions, one rule per flag.

    NOTHING is placed from anywhere but a row id or a named known_gap.  There is no
    branch in this function that can invent a part.
    """
    drawn, skipped = [], []
    for r in handoff["rows"]:
        fl = set(r.get("flags", []))
        if r.get("do_not_draw_as_component"):
            skipped.append((r["id"], r.get("why", "flagged do_not_draw_as_component")))
            continue
        sized = r.get("long_mm") is not None and r.get("short_mm") is not None
        suspect = "on_rim_material_suspect" in fl
        ang = r.get("body_angle_deg")
        if ang is None:
            ang = angles.get((round(r["x_mm"], 3), round(r["y_mm"], 3)))
        drawn.append(dict(
            id=r["id"], x=r["x_mm"], y=r["y_mm"],
            long_mm=r["long_mm"] if sized else None,
            short_mm=r["short_mm"] if sized else None,
            angle=ang if sized else None,       # an angle off an untrustworthy rect
                                                # is untrustworthy too
            kind=("blue" if r["method"].startswith("blue") else "metal"),
            sized=sized, suspect=suspect, conf=r["confidence"]))
    gaps = []
    for g in handoff.get("known_gaps", []):
        for p in g.get("position_eyeballed_mm", []) or []:
            gaps.append(dict(x=p[0], y=p[1], what=g["what"], why=g["why_missed"]))
    return drawn, skipped, gaps


def orientation_table():
    """angle_deg lives in the PRODUCING files, not in the handoff. Keyed on the
    position the handoff itself carries, so the join cannot drift."""
    t = {}
    for fn, key in (("components-front.json", "components"),
                    ("dark-packages-front.json", "packages")):
        p = os.path.join(ROOT, "metrology", fn)
        if not os.path.exists(p):
            continue
        with open(p) as f:
            d = json.load(f)
        for c in d[key]:
            if "angle_deg" in c:
                t[(round(c["x_mm"], 3), round(c["y_mm"], 3))] = c["angle_deg"]
    return t


# ---------------------------------------------------------------- drawing
def rrect(d, cx, cy, L, S, ang_deg, fill, outline=None, w=1):
    a = math.radians(ang_deg or 0.0)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for dx, dy in ((-L / 2, -S / 2), (L / 2, -S / 2), (L / 2, S / 2), (-L / 2, S / 2)):
        pts.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    d.polygon(pts, fill=fill, outline=outline, width=w)


def draw(board, fit, handoff, ppm, margin_mm, caption, quiet_angle=None, break_drop=0):
    k = (board["parameters"]["outer_diameter_mm"]["value"]
         / fit["outer"]["circle_diameter_mm"])          # THE one scale parameter
    th, r_mm, unmeas = outer_poly(fit)
    outer = [(k * rr * math.cos(math.radians(a)), k * rr * math.sin(math.radians(a)))
             for a, rr in zip(th, r_mm)]
    inner = [(k * x, k * y) for x, y in hole_poly(fit)]

    Rmax = max(math.hypot(x, y) for x, y in outer)
    half = Rmax + margin_mm
    W = H = int(round(2 * half * ppm))
    cap_h = 560 if caption else 0
    im = Image.new("RGB", (W, H + cap_h), BG)
    d = ImageDraw.Draw(im, "RGBA")

    def P(p):
        return ((half + p[0]) * ppm, (half + p[1]) * ppm)

    # substrate
    d.polygon([(P(p)[0] + 5, P(p)[1] + 7) for p in outer], fill=(196, 194, 188, 120))
    d.polygon([P(p) for p in outer], fill=MASK)
    # a faint inner bevel so the ring reads as a solid object, not a silhouette
    d.line([P(p) for p in outer] + [P(outer[0])], fill=MASK_EDGE, width=max(2, int(ppm * 0.05)))
    d.polygon([P(p) for p in inner], fill=BG)
    d.line([P(p) for p in inner] + [P(inner[0])], fill=MASK_EDGE, width=max(2, int(ppm * 0.05)))

    # R4: arcs with NO measured ray are drawn in the provisional colour
    n = len(outer)
    for i in range(n):
        if unmeas[i] and unmeas[(i + 1) % n]:
            d.line([P(outer[i]), P(outer[(i + 1) % n])], fill=PROV + (255,),
                   width=max(3, int(ppm * 0.09)))

    angles = orientation_table()
    comps, skipped, gaps = load_components(handoff, angles)
    if break_drop:
        # R5 break: silently lose markers AFTER the flags were honoured, which is what
        # a real drawing bug looks like. The row count stays whole, so the accounting
        # identity is what has to catch it.
        comps = comps[:-break_drop]

    n_sized = n_pos = n_susp = 0
    for c in comps:
        x, y = k * c["x"], k * c["y"]
        col = BLUE if c["kind"] == "blue" else METAL
        edge = SUSPECT if c["suspect"] else None
        if c["sized"]:
            L, S = k * c["long_mm"], k * c["short_mm"]
            rrect(d, *P((x, y)), L * ppm, S * ppm, c["angle"], col,
                  outline=(edge or (14, 14, 16)), w=max(1, int(ppm * 0.02)))
            n_sized += 1
        else:
            # FIXED radius. This is a POSITION, not a footprint, and it must never be
            # readable as a size. 0.30 mm, stamped in the legend.
            rr = 0.30 * ppm
            px, py = P((x, y))
            d.ellipse([px - rr, py - rr, px + rr, py + rr],
                      outline=(edge or POSONLY), width=max(2, int(ppm * 0.035)))
            n_pos += 1
        if c["suspect"]:
            n_susp += 1

    # named absences: eyeballed, measured:false. Their own colour, dashed, with a query.
    fg = font(max(10, int(ppm * 0.42)), bold=True)
    for g in gaps:
        px, py = P((k * g["x"], k * g["y"]))
        rr = 0.55 * ppm
        for a0 in range(0, 360, 30):
            if (a0 // 30) % 2:
                continue
            d.arc([px - rr, py - rr, px + rr, py + rr], a0, a0 + 30,
                  fill=GAP, width=max(2, int(ppm * 0.045)))
        d.text((px, py), "?", font=fg, fill=GAP, anchor="mm")

    # ---- silkscreen legend, ON THE BOARD, in the quietest patch of annulus
    silk_at = quiet_angle
    if silk_at is None:
        silk_at = quietest_arc(comps, k)
    rmid = 0.80 * Rmax
    sx, sy = P((rmid * math.cos(math.radians(silk_at)) * 0.98,
                rmid * math.sin(math.radians(silk_at)) * 0.98))
    fs = font(max(9, int(ppm * 0.30)))
    lines = ["U1  UWB  DNP", "NOT POPULATED", "footprint not drawn:", "size CANNOT DETERMINE"]
    for i, t_ in enumerate(lines):
        d.text((sx, sy + (i - 1.5) * ppm * 0.40), t_, font=fs, fill=SILK, anchor="mm")

    # ---- R7: an INDEPENDENT rim cross-check.
    # L1 flagged 14 of 95 bright rows as on_rim_material_suspect using r / the RAW
    # measured local edge radius. This uses r / the FITTED outline radius -- a
    # different denominator, computed from a model L1 never saw, and it covers the
    # blue rows their test never ran on. The two could disagree; that is the point.
    tf = np.arange(2880) * 360.0 / 2880

    def _edge(ang):
        return k * np.interp(np.asarray(ang) % 360, tf, r_mm, period=360)

    fr = {}
    for row in handoff["rows"]:
        ang = math.degrees(math.atan2(row["y_mm"], row["x_mm"])) % 360
        fr[row["id"]] = (math.hypot(row["x_mm"], row["y_mm"]) * k) / float(_edge(ang))
    THR = 0.95
    mine = {i for i, v in fr.items() if v > THR}
    l1 = {r["id"] for r in handoff["rows"]
          if "on_rim_material_suspect" in r.get("flags", [])}
    both, mo_, lo_ = mine & l1, mine - l1, l1 - mine
    r7 = dict(thr=THR, mine=len(mine), l1=len(l1), both=len(both),
              total=len(handoff["rows"]),
              mine_only=[(i, round(fr[i], 4)) for i in sorted(mo_)],
              l1_only=[(i, round(fr[i], 4)) for i in sorted(lo_)],
              verdict=("CORROBORATED: L1's set is CONTAINED in mine, by two "
                       "denominators neither of which was fitted to the other"
                       if not lo_ else
                       "PARTIAL: the two sets do not nest - chase the difference"))

    if caption:
        cap = build_caption(board, fit, handoff, comps, skipped, gaps,
                            n_sized, n_pos, n_susp, k, r7)
        draw_caption(d, cap, H, W)

    # which of the 1440 control rays land on arcs the chords do NOT cut
    o = fit["outer"]
    ppm_fit = fit["scale"]["px_per_mm"]
    tc = np.deg2rad(np.arange(1440) * 0.25)
    cxp, cyp = o["circle_centre_px"]
    bb = cxp * np.cos(tc) + cyp * np.sin(tc)
    rc = bb + np.sqrt(np.maximum(bb * bb - (cxp * cxp + cyp * cyp - o["circle_R_px"] ** 2), 0.0))
    rm = rc.copy()
    for c in o["chords"]:
        den = c["nx"] * np.cos(tc) + c["ny"] * np.sin(tc)
        with np.errstate(divide="ignore", invalid="ignore"):
            rm = np.minimum(rm, np.where(den > 1e-9, c["d"] / den, np.inf))
    free = (rc - rm) / ppm_fit < 0.02

    return im, Rmax, dict(sized=n_sized, position_only=n_pos, suspect=n_susp,
                          not_drawn=len(skipped), gaps=len(gaps), k=k,
                          skipped=skipped, total_rows=len(handoff["rows"]),
                          free_arc_mask=free, r7=r7)


def quietest_arc(comps, k, step=2.0):
    """Put the silkscreen where there is nothing to cover up. Measured, not chosen."""
    best, besta = -1.0, 0.0
    for a in np.arange(0, 360, step):
        pa = np.deg2rad(a)
        dmin = min(abs(((math.degrees(math.atan2(k * c["y"], k * c["x"])) - a + 180)
                        % 360) - 180) for c in comps) if comps else 180.0
        if dmin > best:
            best, besta = dmin, float(a)
    return besta


def build_caption(board, fit, handoff, comps, skipped, gaps, ns, np_, nsus, k, r7):
    """EVERY line is read from a file. Nothing here is a literal about the board."""
    p = board["parameters"]
    od = p["outer_diameter_mm"]
    o = fit["outer"]
    inn = fit["inner"]
    cnt = handoff["counts"]
    rows = []
    rows.append(("outer dia",
                 f"{od['value']:.3f} mm AS DRAWN",
                 f"{od['state']} - bound {od['bound_mm'][0]}-{od['bound_mm'][1]} mm; "
                 f"if it moves, it moves DOWN"))
    rows.append(("outline",
                 f"circle + {len(o['chords'])} straight chords",
                 f"fit resid sd {o['fit_residual_all_rays']['sd_mm']:.3f} mm, "
                 f"{o['fit_residual_all_rays']['inlier_frac']*100:.0f}% within "
                 f"+-{o['inlier_band_mm']} mm  (plain circle: "
                 f"{o['circle_only_residual_all_rays']['sd_mm']:.3f} mm, "
                 f"{o['circle_only_residual_all_rays']['inlier_frac']*100:.0f}%)"))
    rows.append(("", "",
                 f"{o['unmeasured_total_deg']:.0f} deg of arc carries NO measured ray - "
                 f"drawn in orange, that is where the outline is a guess"))
    rows.append(("centre hole", p["centre_hole"]["shape"],
                 f"{p['centre_hole']['state']} - n={inn['n']:.3f} here, 2.70 on FCC 6, "
                 f"2.00 pinned by L1. NO DIAMETER IS PUBLISHED."))
    rows.append(("thickness", f"{p['thickness_mm']['value']:.2f} mm as-drawn",
                 "below both fab floors - a fact about US, not about Apple"))
    rows.append(("layers", f"{p['layer_count']['value']}", p["layer_count"]["state"]))
    rows.append(("", "", ""))
    rows.append(("components",
                 f"{ns} drawn to MEASURED SIZE, {np_} drawn as POSITION ONLY (fixed "
                 f"0.30 mm ring - NOT a footprint)",
                 f"{nsus} of those may be grey RIM MATERIAL, not parts (orange edge)"))
    rows.append(("not drawn", f"{len(skipped)} of {cnt['total']} rows",
                 "; ".join(f"{i}: {w}" for i, w in skipped)))
    rows.append(("named absences", f"{len(gaps)} positions, EYEBALLED, measured:false",
                 "magenta '?' - drawn so the board is KNOWINGLY incomplete"))
    rows.append(("rim cross-check", f"{r7['mine']} rows beyond {r7['thr']:.2f} of the "
                 f"FITTED outline radius vs L1's {r7['l1']} flagged by their own "
                 f"different denominator", r7["verdict"]))
    rows.append(("also absent",
                 "every neutral-black IC body, incl. the largest one",
                 "CANNOT DETERMINE after three detectors (M08). The dark areas SHOULD "
                 "look sparse. That is the data being honest."))
    rows.append(("never on this board",
                 "3 antennas (E01) - the NFC/voice coil, wound wire (E02)",
                 "no antennas in copper, ever"))
    rows.append(("refused", "rim pads", board["not_drawn"]["rim_pads"]))
    rows.append(("refused", "U1 footprint", board["not_drawn"]["U1_footprint"]))
    return rows


def _wrap(txt, fnt, width, d):
    out, line = [], ""
    for w in txt.split():
        t = (line + " " + w).strip()
        if d.textlength(t, font=fnt) > width and line:
            out.append(line)
            line = w
        else:
            line = t
    if line:
        out.append(line)
    return out


def draw_caption(d, rows, H, W):
    f0, f1, f2 = font(30, True), font(19, True), font(17)
    d.text((16, H + 10),
           "halo Replica MLB - the side carrying the SoC and the shield can", font=f0,
           fill=INK)
    d.text((16, H + 48),
           "outline: FITTED PRIMITIVES (p_fit.py) | components: L1 handoff, one rule "
           "per flag | every caption line is READ FROM board.json / the fit / the handoff",
           font=f2, fill=(96, 96, 100))
    x_lab, x_val, x_note = 16, 165, 620
    y = H + 82
    for a, b, c in rows:
        if not (a or b or c):
            y += 10
            continue
        vl = _wrap(b, f1, x_note - x_val - 20, d) if b else []
        nl = _wrap(c, f2, W - x_note - 16, d) if c else []
        if a:
            d.text((x_lab, y), a, font=f1, fill=INK)
        for i, t_ in enumerate(vl):
            d.text((x_val, y + i * 21), t_, font=f1, fill=INK)
        for i, t_ in enumerate(nl):
            d.text((x_note, y + i * 20), t_, font=f2, fill=PROV)
        y += max(21 * len(vl), 20 * len(nl), 21) + 4


# ---------------------------------------------------------------- controls
def controls(png, Rmax, ppm_asked, margin_mm, want_dia, expect, free_arc_mask):
    ok = True
    im = Image.open(png)
    a = np.asarray(im.convert("L")).astype(float)
    sd, dark = float(a.std()), float((a < 120).mean())
    say(f"R1 non-blank: sd {sd:.2f}, dark fraction {dark:.4f}")
    if sd < 5 or dark < 0.02:
        say("R1 FIRED: blank or near-blank render.")
        ok = False

    half = Rmax + margin_mm
    cx = cy = half * ppm_asked
    centre = a[int(cy), int(cx)]
    ring = a[int(cy), int(cx + 0.86 * Rmax * ppm_asked)]
    say(f"R2 annulus: centre luma {centre:.0f} (want background), 0.86R luma "
        f"{ring:.0f} (want board)")
    if not (centre > 150 and ring < 130):
        say("R2 FIRED: this is not an annulus.")
        ok = False

    board_h = int(round(2 * half * ppm_asked))
    m = a[:board_h] < 150
    ys, xs = np.nonzero(m)
    dcx, dcy = xs.mean(), ys.mean()
    th = np.deg2rad(np.arange(1440) * 0.25)
    rr = np.arange(1.0, 0.75 * board_h, 0.25)
    RR, TT = np.meshgrid(rr, th)
    X = np.rint(dcx + RR * np.cos(TT)).astype(int)
    Y = np.rint(dcy + RR * np.sin(TT)).astype(int)
    good = (X >= 0) & (Y >= 0) & (X < m.shape[1]) & (Y < m.shape[0])
    hit = np.zeros_like(RR, bool)
    hit[good] = m[Y[good], X[good]]
    rad = np.array([rr[np.nonzero(h)[0][-1]] if h.any() else np.nan for h in hit])
    # R3 must measure the SAME quantity the parameter defines. outer_diameter_mm is the
    # CIRCLE's diameter, so the chorded arcs are excluded -- averaging over them compares
    # a chord-shortened mean against a circle diameter and fires at 1.4% on a correct
    # render. (It did exactly that the first time, which is how this line got written.)
    rad_free = np.where(free_arc_mask, rad, np.nan)
    drawn = 2 * np.nanmean(rad_free) / ppm_asked
    err = abs(drawn - want_dia) / want_dia
    say(f"R3 scale: drawn 2 x mean radius over the {int(free_arc_mask.sum())}/1440 rays "
        f"NOT cut by a chord = {drawn:.3f} mm vs stated {want_dia:.3f} mm -> {err*100:.2f}%")
    if err > 0.01:
        say("R3 FIRED: the picture is at the wrong scale. A side-by-side cannot see "
            "this; only this check can.")
        ok = False

    r7 = expect.get("r7")
    if r7:
        say(f"R7 rim cross-check (INDEPENDENT of L1's): {r7['mine']} of "
            f"{r7['total']} rows sit beyond {r7['thr']:.2f} of the FITTED outline "
            f"radius; L1 flags {r7['l1']} rows on_rim_material_suspect by a DIFFERENT "
            f"denominator (their raw measured local edge radius).")
        say(f"   intersection {r7['both']}   mine-only {r7['mine_only']}   "
            f"L1-only {r7['l1_only']}   -> {r7['verdict']}")
    say(f"R5 components: drawn sized {expect['sized']}, position-only "
        f"{expect['position_only']}, suspect {expect['suspect']}, "
        f"not drawn {expect['not_drawn']}, named absences {expect['gaps']}")
    if expect["sized"] + expect["position_only"] + expect["not_drawn"] != expect["total_rows"]:
        say("R5 FIRED: sized + position-only + not-drawn does not account for every "
            "handoff row. A silently dropped marker looks exactly like a sparse board.")
        ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", default=os.path.join(BOARD_DIR, "board.json"))
    ap.add_argument("--fit", default=os.path.join(BOARD_DIR, "outline",
                                                  "outline-fit-oflynn.json"))
    ap.add_argument("--handoff", default=os.path.join(ROOT, "metrology",
                                                      "HANDOFF-positions-front.json"))
    ap.add_argument("--px-per-mm", type=float, default=90.0)
    ap.add_argument("--margin-mm", type=float, default=1.0)
    ap.add_argument("--no-caption", action="store_true")
    ap.add_argument("--out", default=os.path.join(BOARD_DIR, "out", "board-front.png"))
    ap.add_argument("--break-scale", type=float, default=None,
                    help="multiply the DRAW scale only, and watch R3 fire")
    ap.add_argument("--break-drop", type=int, default=0,
                    help="silently lose N markers at DRAW time, and watch R5 fire")
    a = ap.parse_args()

    board = json.load(open(a.board))
    fit = json.load(open(a.fit))
    handoff = json.load(open(a.handoff))

    say("INPUT")
    say(f"  board.json   {os.path.relpath(a.board, ROOT)}")
    say(f"  fit          {os.path.relpath(a.fit, ROOT)}")
    say(f"  handoff      {os.path.relpath(a.handoff, ROOT)}  "
        f"({handoff['counts']['total']} rows)")
    say(f"  px_per_mm    {a.px_per_mm}")
    say(f"  scale basis  {handoff['scale']['basis']}")
    say(f"  uncertainty  {handoff['uncertainty']['note']}")
    say("")

    ppm = a.px_per_mm * (a.break_scale or 1.0)
    im, Rmax, info = draw(board, fit, handoff, ppm, a.margin_mm, not a.no_caption,
                          break_drop=a.break_drop)
    say(f"scale parameter k = {info['k']:.6f}  "
        f"(drawn OD {board['parameters']['outer_diameter_mm']['value']} mm / "
        f"fitted OD {fit['outer']['circle_diameter_mm']:.4f} mm)")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    im.save(a.out)
    say(f"wrote {a.out}  {im.size[0]}x{im.size[1]}")

    info["total_rows"] = len(handoff["rows"])
    ok = controls(a.out, Rmax, a.px_per_mm, a.margin_mm,
                  board["parameters"]["outer_diameter_mm"]["value"], info,
                  info["free_arc_mask"])
    code = PASS if ok else FAIL
    say({0: "PASS", 1: "FAIL", 2: "CANNOT DETERMINE"}[code])
    sys.exit(code)


if __name__ == "__main__":
    main()
