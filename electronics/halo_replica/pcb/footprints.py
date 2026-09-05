"""halo Replica — the land patterns. Generated, never hand-drawn.

    python3 electronics/halo_replica/pcb/footprints.py

Writes `electronics/halo_replica/halo_replica.pretty/*.kicad_mod` plus an
`fp-lib-table` beside it. Same shape as `halo_rev_a/footprints.py`, which is
the template, and for the same reason: a land pattern is geometry with a
source, so it is generated from that source and the source is printed.

---------------------------------------------------------------------------
THE ONE RULE THIS FILE ENFORCES: EVERY PAD CARRIES ITS EVIDENCE CLASS
---------------------------------------------------------------------------
The Replica is a reconstruction from photographs. Three completely different
kinds of geometry end up on the same board and they must never be confused:

  CLASS A  STANDARD PACKAGE GEOMETRY. 0201 and 0402 case sizes are EIA
           standards; the WLCSP pitch is a datasheet number. These are facts
           about the PART, not measurements of Apple's board. Marked
           `[EIA]` / `[DATASHEET]` in the descr.

  CLASS B  MEASURED METAL. `metrology/HANDOFF-positions-front.json` reports
           bright-metal regions with a size the producing lane vouches for.
           Those become real F.Cu lands at the MEASURED extent. The descr
           says, in the producing lane's own words, that the handoff is
           "A LIST OF METAL AND BLUE. It is NOT a list of components."

  CLASS C  A REFUSAL WITH A POSITION. 63 rows are located but NOT sized; 14
           may be grey rim material rather than a part; 3 must not be drawn;
           4 positions are eyeballed and flagged `measured:false`. Every one
           of those gets a NO-COPPER marker whose silkscreen/fab text states
           the refusal. A refusal that is invisible on the board is a
           refusal nobody downstream can honour.

A CLASS C marker has no pad, no mask opening and no paste. It cannot become
copper by accident, which is the whole point: the failure mode this lane
exists to prevent is an eyeballed position sitting in a fabrication output
looking exactly like a measured one.

---------------------------------------------------------------------------
WHAT IS DELIBERATELY MISSING, AND WHY IT IS NOT AN OVERSIGHT
---------------------------------------------------------------------------
  * U3 (SPI NOR, WLCSP-10)  — package size NOT YET MEASURED (bom.json).
    A WLCSP-10 land pattern needs a pitch and a body; neither is in evidence.
  * X1, X2 (crystals)       — package "NOT YET MEASURED" / no manufacturer,
    no part number, no drawing. A seam-sealed ceramic package is a family,
    not a footprint.
  * U2, the Apple U1 UWB module — the land pattern is HERE (it is a legend
    and a size BOUND, with no copper) but board.py does NOT place it: no
    measured centre for that can exists in any handoff file, and its own
    remeasure swings 6.735 -> 7.891 mm on the operator's padding alone
    (metrology/uwb-can-remeasure.json). See REFUSALS in pcb/README.md.
  * Rim / tear-off pads     — count CANNOT DETERMINE and CLOSED (M03, M05).
    The withdrawn 15- and 13-pad angle sets failed a positive control.
  * Antennas                — NOT on this PCB. They are on a moulded carrier
    (evidence/E01). No antenna in copper, ever.
  * The NFC/voice coil      — wound magnet wire, not a trace (board.json).
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
OUT = os.path.join(REPLICA, "halo_replica.pretty")
LIBNAME = "halo_replica"

HANDOFF = os.path.join(REPLICA, "metrology", "HANDOFF-positions-front.json")
HANDOFF_BACK = os.path.join(REPLICA, "metrology",
                            "HANDOFF-positions-back.json")
BOMFILE = os.path.join(REPLICA, "bom", "bom.json")
UWBFILE = os.path.join(REPLICA, "metrology", "uwb-can-remeasure.json")

VERSION = "20240108"
SILK_MIN_H = 0.80        # KiCad's default silkscreen minimum text height, and
SILK_MIN_T = 0.15        # thickness. Both are checked by DRC and both were
                         # violated 116 times by the first draft of this file.
GEN = "halo_replica/pcb/footprints.py"

# --------------------------------------------------------------------------
# CLASS A — standard package geometry. Every number below is a package fact
# with a named source, and NOT a measurement of Apple's board.
# --------------------------------------------------------------------------
#
# THESE LANDS ARE DERIVED, AND THE DERIVATION IS PRINTED RATHER THAN CITED.
# IPC-7351B's tables are not available to this lane offline, so quoting them
# from memory would be a fabricated citation. Instead each land is built from
# the EIA case-size nominal body plus three stated fillet allowances, and the
# construction is written into the footprint's own `descr` so a reviewer can
# redo the arithmetic without this file. The allowances are the conventional
# "Density Level B / median" values for chip components; they are a CHOICE of
# this lane and are labelled as one.
TOE = 0.15        # copper outboard of the termination, mm
HEEL = 0.10       # copper inboard of the termination band, mm
SIDE = 0.05       # copper each side of the body width, mm

# EIA case sizes. body_long x body_short x termination band, mm.
CHIP_SIZES = {
    # imperial name : (L, W, band, metric name)
    "0201": (0.60, 0.30, 0.15, "0603Metric"),
    "0402": (1.00, 0.50, 0.25, "1005Metric"),
}
CHIP_SRC = ("EIA case-size nominal body. 0201 = 0.60 x 0.30 mm, 0402 = "
            "1.00 x 0.50 mm. Land = band + toe %.2f + heel %.2f long, "
            "body + 2 x side %.2f wide." % (TOE, HEEL, SIDE))

# nRF52832-CIAA. BODY IS MEASURED BY THIS PROJECT; PITCH AND BALL COUNT ARE
# THE DATASHEET'S.
NRF_BODY_LONG = 3.226     # bom.json U1 size_mm.value.long_mm, "MEASURED, and
NRF_BODY_SHORT = 2.956    # it is the ruler" (tools/b_pkgsize.py, 10/10 selftest)
NRF_PITCH = 0.40          # NRF-PS v1.4 Table 132
NRF_BALLS = 50            # "WLCSP-50", bom.json U1
NRF_BALL_D = 0.25         # land diameter. CHOICE: 0.625 x pitch, the usual
                          # NSMD ratio for 0.4 mm CSP. Labelled a choice.

# TEN BALL DESIGNATORS ARE SOURCED. FORTY ARE NOT. That ratio is the point.
#
# Colin O'Flynn's test-point table gives pad, BALL and GPIO per row, and ten
# of the nRF52832-CIAA's fifty balls appear in it. They are labelled on the
# fabrication layer from that source; the other 46 grid positions carry no
# designator at all, so the gap is VISIBLE ON THE DRAWING rather than hidden
# behind a generated A1..H7 grid that would have looked equally authoritative.
#
# TEN OF FIFTY IS NOT A BALL MAP. This changes nothing about the land
# pattern: U1 is still not landed, the six depopulated positions are still
# CANNOT DETERMINE, and these ten are not licence to generate the other
# forty.
#
# ONE CONTRADICTION IN THE SOURCE, CARRIED AND NOT RESOLVED: its row 8 says
# ball E2 is P0.16 and its row 19 says ball H3 is P0.16. Two balls, one GPIO,
# one transcription error. Lane L11 takes row 19 because H3/H4/G3/F4 form a
# coherent flash-bus group; E2 is marked DISPUTED here and drawn as such.
NRF_SOURCED_BALLS = {
    "H3": "P0.16 flash COPI", "H4": "P0.15 flash CIPO",
    "G3": "P0.17 flash SCLK", "F4": "P0.11 flash CS",
    "H1": "nRST", "H2": "SWO", "F1": "SWCLK", "G1": "SWDIO",
    "D3": "sourced, signal not recorded here",
    "E2": "P0.16 DISPUTED — the source also gives P0.16 as H3",
}
NRF_BALL_SOURCE = ("Colin O'Flynn's AirTag test-point table (pad, ball and "
                   "GPIO per row), via lane L11, 2026-09-05")


def _fmt(v):
    return ("%.4f" % float(v)).rstrip("0").rstrip(".") or "0"


def _line(x0, y0, x1, y1, layer, w=0.05):
    return ('  (fp_line (start %s %s) (end %s %s) '
            '(stroke (width %s) (type solid)) (layer "%s"))'
            % (_fmt(x0), _fmt(y0), _fmt(x1), _fmt(y1), _fmt(w), layer))


def _circle(cx, cy, r, layer, w=0.05):
    return ('  (fp_circle (center %s %s) (end %s %s) '
            '(stroke (width %s) (type solid)) (fill no) (layer "%s"))'
            % (_fmt(cx), _fmt(cy), _fmt(cx + r), _fmt(cy), _fmt(w), layer))


def _rect(cx, cy, w, h, layer, stroke=0.05):
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    y0, y1 = cy - h / 2.0, cy + h / 2.0
    return [_line(x0, y0, x1, y0, layer, stroke),
            _line(x1, y0, x1, y1, layer, stroke),
            _line(x1, y1, x0, y1, layer, stroke),
            _line(x0, y1, x0, y0, layer, stroke)]


def _text(kind, s, x, y, layer, size=0.5, hide=False):
    h = " hide" if hide else ""
    return ('  (property "%s" "%s" (at %s %s 0) (layer "%s")%s\n'
            '    (effects (font (size %s %s) (thickness %s)))\n  )'
            % (kind, s, _fmt(x), _fmt(y), layer, h,
               _fmt(size), _fmt(size), _fmt(size * 0.15)))


def _fp_text(s, x, y, layer, size=0.4):
    th = max(size * 0.15, SILK_MIN_T) if layer.endswith("SilkS") \
        else size * 0.15
    return ('  (fp_text user "%s" (at %s %s 0) (layer "%s")\n'
            '    (effects (font (size %s %s) (thickness %s)))\n  )'
            % (s, _fmt(x), _fmt(y), layer,
               _fmt(size), _fmt(size), _fmt(th)))


def _head(name, descr, tags, attr):
    return ['(footprint "%s"' % name,
            '  (version %s)' % VERSION,
            '  (generator "%s")' % GEN,
            '  (layer "F.Cu")',
            '  (descr "%s")' % descr.replace('"', "'"),
            '  (tags "%s")' % tags,
            '  (attr %s)' % attr,
            # THE REFERENCE GOES ON F.Fab, NOT ON SILKSCREEN, and that is a
            # measured decision. With 103 refdes in silk on a 25 mm annulus
            # KiCad's own DRC returned 116 text_height + 116 text_thickness +
            # 69 silk_over_copper violations: at a size that fits, the text is
            # below the minimum any fab will print, and at a size that prints,
            # it is on top of the copper. Apple's board carries NO refdes silk
            # either (bom.json conventions). Silkscreen on this board is
            # reserved for the four legends that MUST be physically printed.
            _text("Reference", "REF**", 0, -1.6, "F.Fab", 0.5),
            _text("Value", name, 0, 1.6, "F.Fab", 0.4, hide=True)]


# --------------------------------------------------------------------------
def chip(imperial):
    """CLASS A — a two-terminal chip land pair, 0201 or 0402."""
    L, W, band, metric = CHIP_SIZES[imperial]
    pw = band + TOE + HEEL                     # pad length along the part
    ph = W + 2 * SIDE                          # pad width across the part
    gap = L - 2 * band                         # gap between termination bands
    cx = gap / 2.0 + band - band / 2.0 - HEEL / 2.0 + TOE / 2.0
    cx = (L / 2.0) - band + (band + TOE + HEEL) / 2.0 - HEEL
    # pad centre: outer edge at L/2 + TOE, inner edge at L/2 - band - HEEL
    outer = L / 2.0 + TOE
    inner = L / 2.0 - band - HEEL
    pw = outer - inner
    cx = (outer + inner) / 2.0
    name = "REPL_%s_%s" % (imperial, metric)
    descr = ("CLASS A [EIA] chip land pair, %s (%s). %s "
             "Fillet allowances are a CHOICE of this lane, not a citation. "
             "No part on Apple's board was measured to produce this pattern; "
             "it is here because the Replica's discretes are 0201/0402 and a "
             "library needs the pattern before a placement can use it."
             % (imperial, metric, CHIP_SRC))
    o = _head(name, descr, "halo replica chip %s %s" % (imperial, metric),
              "smd")
    for n, s in ((1, -1), (2, +1)):
        o.append('  (pad "%d" smd roundrect (at %s 0) (size %s %s) '
                 '(layers "F.Cu" "F.Paste" "F.Mask") '
                 '(roundrect_rratio 0.25))'
                 % (n, _fmt(s * cx), _fmt(pw), _fmt(ph)))
    o += _rect(0, 0, L, W, "F.Fab")
    cw = 2 * cx + pw + 0.5
    ch = max(ph, W) + 0.5
    o += _rect(0, 0, cw, ch, "F.CrtYd")
    o.append(")")
    return name, "\n".join(o)


def wlcsp_nrf():
    """CLASS A/B hybrid — the SoC land grid. THE ONE OVER-DRAW ON THIS BOARD.

    Body is MEASURED (bom.json U1, tools/b_pkgsize.py). Pitch is the
    datasheet's. The BALL MAP IS NOT IN EVIDENCE HERE: the part is a
    WLCSP-50 and a 0.40 mm grid inside a 3.226 x 2.956 mm body is 8 x 7 =
    56 positions, so SIX POSITIONS ARE DEPOPULATED AND THIS LANE DOES NOT
    KNOW WHICH SIX. All 56 are drawn.

    That is an OVER-DRAW of 6 lands and it is stated three times — here, in
    the footprint's own descr, and in fab text on the footprint itself — so
    that it cannot travel silently into a fabrication output. It is drawn
    rather than refused because a WLCSP body with no lands is not a
    footprint, and the alternative (guessing the six) invents copper.
    """
    ncols = int(math.floor(NRF_BODY_SHORT / NRF_PITCH))   # 7
    nrows = int(math.floor(NRF_BODY_LONG / NRF_PITCH))    # 8
    name = "REPL_WLCSP_%dx%d_P%s_GRID%d" % (nrows, ncols, _fmt(NRF_PITCH),
                                            nrows * ncols)
    descr = ("CLASS A/B [DATASHEET + MEASURED] nRF52832-CIAA land grid. "
             "Body %s x %s mm MEASURED (bom.json U1, b_pkgsize.py, 10/10 "
             "selftest). Pitch %s mm from nRF52832 PS v1.4 Table 132. "
             "OVER-DRAWN: the part is WLCSP-%d and %d grid positions are "
             "drawn, so %d LANDS HERE DO NOT EXIST ON THE PART. Which six "
             "are depopulated is CANNOT DETERMINE in this lane -- no ball "
             "map is in evidence. NOT FABRICATION-READY as a solder land "
             "set. Land diameter %s mm is a CHOICE (0.625 x pitch, the "
             "usual NSMD ratio at 0.4 mm), not a measurement."
             % (_fmt(NRF_BODY_LONG), _fmt(NRF_BODY_SHORT), _fmt(NRF_PITCH),
                NRF_BALLS, nrows * ncols, nrows * ncols - NRF_BALLS,
                _fmt(NRF_BALL_D)))
    o = _head(name, descr, "halo replica wlcsp nrf52832 overdrawn", "smd")
    letters = "ABCDEFGHJKLMNP"
    x0 = -(ncols - 1) * NRF_PITCH / 2.0
    y0 = -(nrows - 1) * NRF_PITCH / 2.0
    for r in range(nrows):
        for c in range(ncols):
            o.append('  (pad "%s%d" smd circle (at %s %s) (size %s %s) '
                     '(layers "F.Cu" "F.Paste" "F.Mask"))'
                     % (letters[r], c + 1,
                        _fmt(x0 + c * NRF_PITCH), _fmt(y0 + r * NRF_PITCH),
                        _fmt(NRF_BALL_D), _fmt(NRF_BALL_D)))
    o += _rect(0, 0, NRF_BODY_SHORT, NRF_BODY_LONG, "F.Fab")
    o.append(_fp_text("56 LANDS DRAWN / 50 BALLS - 6 UNKNOWN",
                      0, NRF_BODY_LONG / 2.0 + 0.45, "F.Fab", 0.30))
    o.append(_circle(x0 - 0.30, y0 - 0.30, 0.10, "F.SilkS"))   # A1 corner
    o += _rect(0, 0, NRF_BODY_SHORT + 0.5, NRF_BODY_LONG + 0.5, "F.CrtYd")
    o.append(")")
    return name, "\n".join(o)


def wlcsp_nrf_no_lands():
    """CLASS C — the SoC as DOCUMENTATION. Zero copper. This is what lands.

    Same body and same grid as wlcsp_nrf(), drawn entirely on F.Fab. A
    reader can measure the pattern; a fabricator gets nothing, because the
    six depopulated positions of the WLCSP-50 are CANNOT DETERMINE and six
    lands that do not exist on the part are six lands a board house would
    make. The solderable version stays in this library as a drawing.
    """
    ncols = int(math.floor(NRF_BODY_SHORT / NRF_PITCH))
    nrows = int(math.floor(NRF_BODY_LONG / NRF_PITCH))
    name = "REPL_U1_WLCSP50_NO_LANDS"
    descr = ("CLASS C [LAND PATTERN REFUSED] nRF52832-CIAA, WLCSP-50. NO "
             "COPPER, NO MASK, NO PASTE. Body %s x %s mm MEASURED "
             "(bom.json U1); %s mm pitch from nRF52832 PS v1.4 Table 132; "
             "%d grid positions shown on F.Fab for %d balls, and WHICH %d "
             "ARE DEPOPULATED IS CANNOT DETERMINE -- no ball map exists in "
             "this repo and KiCad's 179 Package_CSP footprints hold no "
             "nRF52832 WLCSP. The A1 corner is unknown too: the placement "
             "angle is a min-area-rect long side, modulo 180 deg. TEN "
             "designators (%s) are SOURCED from %s and are ringed and "
             "labelled; the other %d positions carry NO designator, so the "
             "gap is visible on the drawing instead of hidden behind a "
             "generated grid. Ten of fifty is not a ball map."
             % (_fmt(NRF_BODY_LONG), _fmt(NRF_BODY_SHORT), _fmt(NRF_PITCH),
                nrows * ncols, NRF_BALLS, nrows * ncols - NRF_BALLS,
                ", ".join(sorted(NRF_SOURCED_BALLS)), NRF_BALL_SOURCE,
                nrows * ncols - len(NRF_SOURCED_BALLS)))
    o = _head(name, descr, "halo replica wlcsp nrf52832 refused no copper",
              "smd board_only exclude_from_pos_files exclude_from_bom")
    letters = "ABCDEFGHJKLMNP"
    x0 = -(ncols - 1) * NRF_PITCH / 2.0
    y0 = -(nrows - 1) * NRF_PITCH / 2.0
    labelled = 0
    for r in range(nrows):
        for c in range(ncols):
            bx, by = x0 + c * NRF_PITCH, y0 + r * NRF_PITCH
            o.append(_circle(bx, by, NRF_BALL_D / 2.0, "F.Fab", 0.03))
            ball = "%s%d" % (letters[r], c + 1)
            if ball in NRF_SOURCED_BALLS:
                # SOURCED. Marked with a second ring and its designator, so a
                # reader can see at a glance which ten of the fifty rest on a
                # source and which do not.
                o.append(_circle(bx, by, NRF_BALL_D / 2.0 + 0.05, "F.Fab",
                                 0.03))
                o.append(_fp_text(ball, bx, by - 0.22, "F.Fab", 0.15))
                labelled += 1
    o += _rect(0, 0, NRF_BODY_SHORT, NRF_BODY_LONG, "F.Fab", 0.06)
    o.append(_fp_text("U1 WLCSP-50 - NO LANDS, BALL MAP CANNOT DETERMINE",
                      0, NRF_BODY_LONG / 2.0 + 0.45, "F.Fab", 0.30))
    o.append(_fp_text("%d of %d designators SOURCED (%s); the rest are "
                      "UNLABELLED because they are unknown"
                      % (labelled, NRF_BALLS, NRF_BALL_SOURCE),
                      0, NRF_BODY_LONG / 2.0 + 0.80, "F.Fab", 0.18))
    o.append(")")
    return name, "\n".join(o)


def metal_land(w_mm, l_mm):
    """CLASS B — one MEASURED bright-metal region, drawn as the land it is."""
    name = "REPL_METAL_%sx%s" % (_fmt(round(w_mm, 2)), _fmt(round(l_mm, 2)))
    descr = ("CLASS B [MEASURED] bright-metal region, %s x %s mm, from "
             "metrology/HANDOFF-positions-front.json (bright-metal "
             "segmentation, m_components.py). The producing lane's own "
             "words: the handoff is 'A LIST OF METAL AND BLUE. It is NOT a "
             "list of components.' This land is what was MEASURED to be "
             "metal at this place and this size -- it is NOT a claim about "
             "which component the metal belongs to, nor that it is one pad."
             % (_fmt(round(w_mm, 2)), _fmt(round(l_mm, 2))))
    o = _head(name, descr, "halo replica measured metal land", "smd")
    o.append('  (pad "1" smd rect (at 0 0) (size %s %s) '
             '(layers "F.Cu" "F.Paste" "F.Mask"))'
             % (_fmt(round(w_mm, 2)), _fmt(round(l_mm, 2))))
    # NO COURTYARD, AND FOR THE SAME REASON THE MARKERS HAVE NONE. A
    # courtyard is the space a PART BODY occupies. This is a transcription of
    # a MEASURED METAL REGION -- the handoff explicitly is not a list of
    # components -- so there is no body and there is nothing to reserve space
    # for. Giving these courtyards produced 25 courtyards_overlap errors that
    # were statements about a convention this lane invented, not about the
    # board; crowding between two measured lands is already reported, and
    # reported better, by the clearance rule.
    o.append(")")
    return name, "\n".join(o)


def back_pad(d_mm):
    """CLASS B — one MEASURED round gold pad on Apple's BATTERY-CONTACT face.

    NO PASTE. These are test / probe lands (O'Flynn's TP1..TP38 field is the
    positive control that found them), not solder joints for a part, and a
    paste aperture on a probe pad is an instruction to print solder where
    nothing is placed.

    The diameter is an EQUIVALENT CIRCLE from the measured area -- the
    handoff flags every one of these `diameter_is_equivalent_circle`, and a
    round pad of that diameter is precisely what that flag licenses. It is
    not a claim that the land is a perfect circle.
    """
    d = round(float(d_mm), 2)
    name = "REPL_BPAD_D%s" % _fmt(d)
    descr = ("CLASS B [MEASURED] round gold pad, equivalent-circle diameter "
             "%s mm, from metrology/HANDOFF-positions-back.json (gold colour "
             "AND circular shape, k_backface). Population median 0.5985 mm, "
             "IQR 0.0340. NO PASTE: a probe land is not a solder joint. The "
             "diameter is an equivalent circle from area, which is what the "
             "row's `diameter_is_equivalent_circle` flag says it is."
             % _fmt(d))
    o = _head(name, descr, "halo replica backface gold pad measured", "smd")
    o.append('  (pad "1" smd circle (at 0 0) (size %s %s) '
             '(layers "F.Cu" "F.Mask"))' % (_fmt(d), _fmt(d)))
    # NO COURTYARD, AND FOR THE SAME REASON THE MARKERS HAVE NONE. A
    # courtyard is the space a PART BODY occupies. This is a transcription of
    # a MEASURED METAL REGION -- the handoff explicitly is not a list of
    # components -- so there is no body and there is nothing to reserve space
    # for. Giving these courtyards produced 25 courtyards_overlap errors that
    # were statements about a convention this lane invented, not about the
    # board; crowding between two measured lands is already reported, and
    # reported better, by the clearance rule.
    o.append(")")
    return name, "\n".join(o)


def back_pad_sizes():
    """Distinct measured pad diameters, and the rows refused, on the back."""
    h = json.load(open(HANDOFF_BACK))
    sizes, kept, refused = set(), [], []
    for r in h["rows"]:
        if r.get("do_not_draw_as_component"):
            refused.append((r["id"], "outside_the_board_OD_bound"))
            continue
        if "extent_is_pad_OR_spring_not_separable" in (r.get("flags") or []):
            refused.append((r["id"], "contact_position_only"))
            continue
        sizes.add(round(float(r["long_mm"]), 2))
        kept.append(r["id"])
    return sorted(sizes), kept, refused


def _marker(name, descr, glyph, note, size=1.0, tags="halo replica marker"):
    """CLASS C — a refusal with a position. NO COPPER, EVER.

    attr is `virtual` plus both exclusions, so it can never reach a
    fabrication output as a part and never reach the BOM as a line.
    """
    o = _head(name, descr, tags,
              "smd board_only exclude_from_pos_files exclude_from_bom")
    r = size / 2.0
    if glyph == "cross":
        o.append(_line(-r, 0, r, 0, "Cmts.User", 0.08))
        o.append(_line(0, -r, 0, r, "Cmts.User", 0.08))
        o.append(_circle(0, 0, r * 0.7, "Cmts.User", 0.06))
    elif glyph == "x":
        o.append(_line(-r, -r, r, r, "Cmts.User", 0.10))
        o.append(_line(-r, r, r, -r, "Cmts.User", 0.10))
        o.append(_circle(0, 0, r, "Cmts.User", 0.06))
    elif glyph == "square":
        o += _rect(0, 0, size, size, "Cmts.User", 0.08)
        o.append(_line(-r, -r, r, r, "Cmts.User", 0.06))
    elif glyph == "query":
        o.append(_circle(0, 0, r, "Cmts.User", 0.08))
        o.append(_line(0, -r * 0.45, 0, r * 0.15, "Cmts.User", 0.10))
        o.append(_line(0, r * 0.40, 0, r * 0.55, "Cmts.User", 0.10))
    o.append(_fp_text(note, 0, r + 0.35, "Cmts.User", 0.25))
    # NO COURTYARD. A courtyard is the space a PART occupies, and a CLASS C
    # marker is not a part -- it is a position with a refusal attached. Giving
    # it one manufactured 144 courtyards_overlap violations that said nothing
    # about the board and buried the ones that do (clearance, mask bridge,
    # edge clearance between MEASURED lands, all still reported).
    o.append(")")
    return name, "\n".join(o)


def pos_marker():
    return _marker(
        "REPL_POS_ONLY",
        "CLASS C [POSITION ONLY, NO SIZE] One of the 63 handoff rows that "
        "are LOCATED but NOT SIZED. The position is usable; the size is "
        "not, so no land is drawn. NO COPPER, NO MASK, NO PASTE -- this "
        "marker cannot become a pad by accident, which is the point.",
        "cross", "POSITION ONLY - SIZE NOT MEASURED")


def rim_suspect_marker():
    return _marker(
        "REPL_RIM_SUSPECT",
        "CLASS C [MAY NOT BE A PART] One of the 14 rows flagged "
        "on_rim_material_suspect: at this radius the bright region may be "
        "the grey fibrous rim material rather than a component (M02 sec 8, "
        "M09). Corroborated independently by L5b's R7 test, which found L1's "
        "set CONTAINED in its own 16. Drawn WITHOUT COPPER whatever its "
        "measured size, because a land drawn over rim material is a "
        "fabrication instruction derived from a maybe.",
        "square", "RIM MATERIAL SUSPECT - MAY NOT BE A PART")


def not_drawn_marker():
    return _marker(
        "REPL_NOT_DRAWN",
        "CLASS C [DO NOT DRAW] A handoff row carrying "
        "do_not_draw_as_component:true. Two are merged pad RUNS (7.30 mm "
        "and 14.48 mm long sides -- adjacent pads joined at the "
        "segmentation threshold, NOT A SINGLE PART) and one is an "
        "edge-bright strip at 4.1:1 that an IC body cannot be. Present on "
        "the board so the exclusion is visible where the board is read, "
        "not only in a JSON file.",
        "x", "DO NOT DRAW - SEE VALUE FIELD FOR REASON", size=1.4)


def eyeballed_marker():
    return _marker(
        "REPL_ABSENCE_EYEBALLED",
        "CLASS C [EYEBALLED, measured:false] A position found BY LOOKING at "
        "a native-resolution tile (M09) and never by a detector. The "
        "handoff carries position_eyeballed_mm, measured:false and "
        "do_not_draw_as_measured:true, and all three are honoured here. "
        "Accurate to about a millimetre. It is on the board so that the "
        "board is KNOWINGLY incomplete rather than looking complete -- a "
        "miss written down is a different object from a miss not written "
        "down.",
        "query", "EYEBALLED ~1 mm - NOT MEASURED", size=1.4)


def back_contact_marker():
    return _marker(
        "REPL_BACK_CONTACT_POS",
        "CLASS C [POSITION ONLY — EXTENT IS NOT A PAD DIMENSION] One of the "
        "three battery contacts on Apple's BATTERY-CONTACT face. The "
        "handoff flags it extent_is_pad_OR_spring_not_separable: the only "
        "photograph showing this face shows the board ASSEMBLED IN THE "
        "SHELL, so the board pad and the sprung contact sitting on it are "
        "COINCIDENT IN PLAN VIEW and no measurement here can separate them. "
        "Its own instruction: 'USE THE CONTACT POSITIONS; do not take their "
        "extents as pad dimensions.' So the position is drawn and the extent "
        "is not. NO COPPER. What would settle it: FCC internal photo 4, the "
        "battery cavity with the contacts and NO BOARD.",
        "cross", "BATTERY CONTACT - POSITION ONLY, EXTENT NOT A PAD",
        size=1.6)


def uwb_module():
    """CLASS C — the module that is never sold, drawn as a SIZE BOUND.

    board.py does NOT place this. There is no measured centre for the UWB
    can anywhere in the handoff files. It is generated so the library is
    complete and so the bound is on disk in a form KiCad can open.
    """
    rows = json.load(open(UWBFILE))["rows"]
    lo_l = min(r["long_mm"] for r in rows)
    hi_l = max(r["long_mm"] for r in rows)
    lo_s = min(r["short_mm"] for r in rows)
    hi_s = max(r["short_mm"] for r in rows)
    name = "REPL_U2_UWB_MODULE_UNPOPULATED"
    descr = ("CLASS C [SIZE IS A BOUND, POSITION CANNOT DETERMINE] The Apple "
             "U1 UWB module. UNPOPULATED ON EVERY REPLICA BOARD -- the part "
             "is never sold to anyone. NO COPPER is drawn: five remeasures "
             "of the same can in the same photograph give %s-%s x %s-%s mm, "
             "differing ONLY in the operator's chosen padding "
             "(metrology/uwb-can-remeasure.json), and no handoff file gives "
             "the can a centre. Both rectangles below are drawn: the inner "
             "is the smallest remeasure, the outer the largest. A land "
             "pattern picked from either would be a number invented by the "
             "operator."
             % (_fmt(round(lo_l, 3)), _fmt(round(hi_l, 3)),
                _fmt(round(lo_s, 3)), _fmt(round(hi_s, 3))))
    o = _head(name, descr, "halo replica uwb unpopulated dnp",
              "smd board_only exclude_from_pos_files exclude_from_bom")
    o += _rect(0, 0, lo_l, lo_s, "Cmts.User", 0.08)
    o += _rect(0, 0, hi_l, hi_s, "Cmts.User", 0.08)
    o.append(_fp_text("U2 APPLE U1 UWB - UNPOPULATED, NEVER SOLD",
                      0, hi_s / 2.0 + 0.5, "F.SilkS", 0.35))
    o.append(_fp_text("SIZE IS A BOUND %s-%s mm - POSITION NOT MEASURED"
                      % (_fmt(round(lo_l, 2)), _fmt(round(hi_l, 2))),
                      0, -hi_s / 2.0 - 0.5, "Cmts.User", 0.28))
    o += _rect(0, 0, hi_l + 0.4, hi_s + 0.4, "F.CrtYd", 0.05)
    o.append(")")
    return name, "\n".join(o)


def legend(name, lines, layer="Cmts.User", size=0.32, tag="legend"):
    """A block of board legend text. No copper, no courtyard obligations.

    TWO LEGENDS EXIST AND THEY ARE NOT THE SAME OBJECT.

      REPL_LEGEND_BOARD   the full block, on Cmts.User. It reaches the
                          fabrication drawing and the person reading the
                          board in KiCad. It is too wide for a 25 mm annulus
                          and putting it in silkscreen would mean shrinking
                          it to unreadable or running it off the board.
      REPL_SILK_*         short lines that DO fit in the annulus, in
                          F.SilkS, so they are physically printed on the
                          board. The brief's requirement -- the UWB module
                          is unpopulated and it SAYS SO ON THE BOARD -- is
                          discharged by these, not by the block.
    """
    descr = ("CLASS C [BOARD LEGEND] Text placed ON THE BOARD, layer %s. "
             "Facts a reader of the board itself must not have to open a "
             "document to learn." % layer)
    o = _head(name, descr, "halo replica legend " + tag,
              "smd board_only exclude_from_pos_files exclude_from_bom")
    y = 0.0
    for ln in lines:
        o.append(_fp_text(ln, 0, y, layer, size))
        y += size * 1.7
    o.append(")")
    return name, "\n".join(o)


# --------------------------------------------------------------------------
def metal_sizes_from_handoff():
    """Every DISTINCT measured land size the placement will need.

    A row earns a CLASS B land only if ALL of these hold:
      * do_not_draw_as_component is false
      * on_rim_material_suspect is not among its flags
      * BOTH long_mm and short_mm are present   <- the size exists
      * confidence is not 'low'                 <- the producing lane vouches
    Anything else is CLASS C. The rule is here, once, and board.py imports it
    rather than restating it.
    """
    h = json.load(open(HANDOFF))
    sizes, kept, refused = set(), [], []
    for r in h["rows"]:
        why = classify(r)
        if why == "metal":
            w = round(float(r["short_mm"]), 2)
            l = round(float(r["long_mm"]), 2)
            sizes.add((w, l))
            kept.append(r["id"])
        else:
            refused.append((r["id"], why))
    return sorted(sizes), kept, refused


def classify(row):
    """The single decision function. board.py imports THIS, never a copy."""
    if row.get("do_not_draw_as_component"):
        return "not_drawn"
    flags = row.get("flags") or []
    if "on_rim_material_suspect" in flags:
        return "rim_suspect"
    if row.get("long_mm") is None or row.get("short_mm") is None:
        return "pos_only"
    if str(row.get("confidence", "")).lower() == "low":
        return "pos_only"
    return "metal"


PATTERNS_STATIC = [chip("0201"), chip("0402"), wlcsp_nrf(),
                   wlcsp_nrf_no_lands(), pos_marker(),
                   rim_suspect_marker(), not_drawn_marker(),
                   eyeballed_marker(), uwb_module(),
                   back_contact_marker()]


def write_fp_lib_table(outdir):
    p = os.path.join(os.path.dirname(outdir), "fp-lib-table")
    with open(p, "w", encoding="utf-8") as f:
        f.write('(fp_lib_table\n  (version 7)\n'
                '  (lib (name "%s")(type "KiCad")'
                '(uri "${KIPRJMOD}/../%s.pretty")(options "")'
                '(descr "halo Replica land patterns, generated by '
                'pcb/footprints.py"))\n)\n' % (LIBNAME, LIBNAME))
    return p


def main():
    os.makedirs(OUT, exist_ok=True)
    pats = list(PATTERNS_STATIC)

    sizes, kept, refused = metal_sizes_from_handoff()
    for w, l in sizes:
        pats.append(metal_land(w, l))

    bsizes, bkept, brefused = back_pad_sizes()
    for d in bsizes:
        pats.append(back_pad(d))

    pats.append(legend("REPL_LEGEND_BOARD", [
        "halo REPLICA MLB - RECONSTRUCTION FROM PHOTOGRAPHS, NOT APPLE ART",
        "OD IS A BOUND 24.95-26.34 mm. DRAWN VALUE IS NOT A SETTLED DIAMETER.",
        "0.30 mm AS-DRAWN. BELOW PCBWAY AND JLCPCB 4-LAYER 0.40 mm FLOORS.",
        "AS DRAWN THIS BOARD CANNOT BE ORDERED AT EITHER HOUSE.",
        "U2 APPLE U1 UWB MODULE: UNPOPULATED. THE PART IS NEVER SOLD.",
        "KNOWINGLY INCOMPLETE: 5 DARK BODIES CANNOT DETERMINE, NOT DRAWN.",
        "NO ANTENNA IN COPPER - APPLE'S ARE ON A MOULDED CARRIER.",
        "RIM PAD COUNT CANNOT DETERMINE - NO RIM PADS DRAWN.",
    ]))

    # The lines that must be PRINTED ON THE BOARD, not merely documented.
    # Sized and split to fit inside a 6.4 mm annulus at 0.26 mm text.
    # SIZED TO WHAT A FAB WILL ACTUALLY PRINT, WHICH DECIDED THE WORDING.
    # KiCad's default silkscreen minimum is 0.8 mm high / 0.15 mm thick and
    # that is close to what board houses quote. At 0.8 mm a character is
    # about 0.6 mm wide and the annulus is 6.4 mm wide at its narrowest, so a
    # radial line gets ~10 characters. Everything longer went to Cmts.User in
    # REPL_LEGEND_BOARD. THE WORDS WERE CUT TO FIT THE PROCESS; the process
    # was not bent to fit the words, and the earlier 0.26 mm version -- which
    # said more and would have printed as nothing -- is gone.
    for nm, lines, tag in (
            ("REPL_SILK_U2_DNP", ["U2 UWB", "DNP"], "silk uwb dnp"),
            ("REPL_SILK_THICKNESS", ["0.30mm"], "silk thickness"),
            ("REPL_SILK_INCOMPLETE", ["PARTIAL"], "silk incomplete"),
            ("REPL_SILK_REPLICA", ["REPLICA"], "silk replica")):
        pats.append(legend(nm, lines, layer="F.SilkS", size=SILK_MIN_H,
                           tag=tag))

    keep = {n + ".kicad_mod" for n, _ in pats}
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".kicad_mod") and f not in keep:
            os.remove(os.path.join(OUT, f))
            print("removed stale %s" % f)

    for name, body in pats:
        with open(os.path.join(OUT, name + ".kicad_mod"), "w",
                  encoding="utf-8") as f:
            f.write(body + "\n")

    tbl = write_fp_lib_table(OUT)

    print("halo Replica land patterns -> %s" % OUT)
    print("  %d footprints written, fp-lib-table at %s" % (len(pats), tbl))
    print()
    print("  CLASS A [package geometry, not a measurement of Apple's board]")
    print("    REPL_0201_0603Metric, REPL_0402_1005Metric   %s" % CHIP_SRC)
    print("    REPL_WLCSP_8x7_P0.4_GRID56  OVER-DRAWN BY 6 LANDS, stated on "
          "the footprint")
    print("  CLASS B [measured metal]  %d distinct sizes for %d rows"
          % (len(sizes), len(kept)))
    print("  CLASS B [measured gold pads, BACK face]  %d distinct diameters "
          "for %d rows" % (len(bsizes), len(bkept)))
    print("  CLASS C [refusals with a position]  %d front rows, %d back rows"
          % (len(refused), len(brefused)))
    from collections import Counter
    for k, n in sorted(Counter(w for _, w in refused).items()):
        print("      %-12s %d" % (k, n))
    print()
    print("  REFUSED OUTRIGHT, no pattern generated: U3 (WLCSP-10, size NOT "
          "YET MEASURED), X1/X2 (crystal, no part, no drawing), rim pads "
          "(count CANNOT DETERMINE, CLOSED), antennas (not on this PCB), "
          "the coil (wound wire, not a trace).")


if __name__ == "__main__":
    main()
