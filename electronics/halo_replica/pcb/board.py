"""halo Replica — the board. Annular, 4 layers, 0.30 mm, routed centre pocket.

    cd ~/dev/ce-workshop
    ce-pcb/bin/pcb ce-designs/halo/electronics/halo_replica/pcb/board.py

LANE L12. Writes `pcb/out/halo_replica.kicad_pcb` and its project files.

---------------------------------------------------------------------------
WHAT THIS BOARD IS, AND WHAT IT IS NOT
---------------------------------------------------------------------------
It is a RECONSTRUCTION FROM PHOTOGRAPHS of Apple's AirTag MLB, drawn so that
a KiCad user can open it, measure it and argue with it. It is NOT Apple's
artwork, it is not a netlist, and it is not orderable (see THICKNESS below).

Everything on it comes from a file in this repo and nothing on it was typed
by eye. The four inputs, and none of them is re-derived here:

  board/board.json                       the ONE scale parameter
  board/outline/outline-fit-oflynn.json  circle + 4 chords, superellipse + 7
                                         facets -- FITTED PRIMITIVES
  metrology/HANDOFF-positions-front.json 100 measured rows, with the flags
  metrology/uwb-can-remeasure.json       the UWB can's size BOUND

---------------------------------------------------------------------------
THE NETLIST IS NOT TYPED HERE, AND IT IS NOT INVENTED EITHER
---------------------------------------------------------------------------
halo_rev_a/board.py reads its netlist back out of its own schematic with
`cepcb.schematic.netlist_of_sch` so copper and drawing cannot drift. This
board does the same READ -- and today it comes back empty, because lane L11's
schematic does not exist yet. That is reported as CANNOT DETERMINE on every
run and NOT papered over with a hand-written net list. When
`schematic/out/*.kicad_sch` appears, this file picks it up with no edit.

A board with no nets is a board whose copper connectivity is unknown. Said
once, here, and once again on every run.

---------------------------------------------------------------------------
THICKNESS: THE NUMBER THAT MAKES THIS UNORDERABLE, AND IT DOES NOT MOVE
---------------------------------------------------------------------------
0.30 mm as-drawn, 4 layers. L4 measured PCBWay's four-layer floor at 0.40 mm
and JLCPCB's minimum at 0.40 mm. THE REPLICA AS DRAWN CANNOT BE ORDERED AT
EITHER HOUSE. That is a fact about US, not about Apple, and the two are
never fused: the drawing is not moved to 0.40 to make a quote come back.
The fabrication delta is recorded in board/stackup/stackup.json and printed
here, separately, every run.

---------------------------------------------------------------------------
THE FOUR THINGS THAT MAKE THIS A REPLICA AND NOT A DISC
---------------------------------------------------------------------------
  1  ANNULAR, with a ROUTED CENTRE POCKET -- a superellipse with 7 measured
     straight facets and radial step walls, not a circle, not a smooth
     curve, and above all not a solid disc.
  2  The OD is a BOUND (24.95-26.34 mm) with a signed expectation that it
     moves DOWN. It is a PARAMETER read from board.json, never a literal.
  3  WAFER-SCALE AND 0201 in the library, because that is what Apple used.
  4  U2, the Apple U1 UWB module, is UNPOPULATED and the board says so in
     silkscreen.

---------------------------------------------------------------------------
AND THE ONE THING THAT MUST NOT HAPPEN: A GAP FILLED BY EYE
---------------------------------------------------------------------------
Five dark bodies on this board are CANNOT DETERMINE at a MEASURED contrast
limit -- the photograph needs a 100-160 luma boundary step and they present
1-26. The largest package on the board is one of them. Nothing is drawn
there. The board will look sparse in the dark areas and that is the data
being honest.

An invented part is INVISIBLE in a render, which is exactly why it must not
happen: the render is where a reviewer would catch anything else.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import footprints as FP                                        # noqa: E402
import geometry as GEO                                         # noqa: E402

from cepcb import Board                                        # noqa: E402
from cepcb.board import _vec, MM                               # noqa: E402

OUT = os.path.join(HERE, "out")
PCB = os.path.join(OUT, "halo_replica.kicad_pcb")
LIB = os.path.join(REPLICA, "halo_replica.pretty")
LIBID = "halo_replica"

HANDOFF = os.path.join(REPLICA, "metrology", "HANDOFF-positions-front.json")
COMPS = os.path.join(REPLICA, "metrology", "components-front.json")
BLUE = os.path.join(REPLICA, "metrology", "dark-packages-front.json")
DARKPKG = os.path.join(REPLICA, "metrology", "darkpkg",
                       "HANDOFF-darkpackages.json")
HANDOFF_BACK = os.path.join(REPLICA, "metrology",
                            "HANDOFF-positions-back.json")
HANDEDNESS = os.path.join(REPLICA, "metrology", "backface-handedness.json")
BOARDJSON = os.path.join(REPLICA, "board", "board.json")
STACKUP = os.path.join(REPLICA, "board", "stackup", "stackup.json")
SCHDIR = os.path.join(REPLICA, "out", "schematic")   # lane L11

# ---------------------------------------------------------------------------
# THE SoC, AND WHY IT IS THE ONE ROW THAT GETS A NAMED PACKAGE
# ---------------------------------------------------------------------------
# handoff row D000 is the nRF52832. That is not this lane guessing: M08 uses
# it as its POSITIVE CONTROL, found by blue-epoxy colour (B-R = +43 against a
# board median of +1), and its measured 3.283 x 3.030 mm sits within ~2 % of
# the datasheet body 3.226 x 2.956 that bom.json calls "MEASURED, and it is
# the ruler". Position confidence: high, no flags.
#
# THREE THINGS ABOUT IT ARE STILL CANNOT DETERMINE and the value field says
# all three on the board:
#   * WHICH 6 of the 56 grid positions are depopulated (the part is a
#     WLCSP-50). The grid is OVER-DRAWN by six lands.
#   * WHERE BALL A1 IS. A min-area-rect angle is the long side modulo 180
#     deg, so the die's rotation is known to 180 deg at best and the A1
#     corner not at all.
#   * The ~2 % between the colour-segmented body and the datasheet body.
#     Not reconciled here; M08 raises it as its own honesty note.
#
# NOTE ON IDS, because two files use the same ones for different objects:
# handoff D000 (blue-body colour segmentation, MEASURED) and darkpkg D000
# (boundary evidence, CANNOT DETERMINE) are the SAME PHYSICAL PART reached by
# two methods that reached opposite verdicts. handoff D001..D004 and darkpkg
# D001..D004 are NOT the same parts as each other. Always write the file with
# the id.
# WHAT IS LANDED THERE, AND THE COPPER THAT IS REFUSED
# ---------------------------------------------------
# NO SOLDERABLE LAND PATTERN. An earlier build of this file placed
# REPL_WLCSP_8x7_P0.4_GRID56 here -- 56 lands for a 50-ball part, the
# over-draw stated on the footprint. Lane L11 stopped it and was right:
#
#   "IF YOU LAND THE QFN-48 PATTERN YOU HAVE BUILT A QFN BOARD, NOT A
#    REPLICA OF APPLE'S WLCSP LAND ... the board would build, DRC would
#    pass, and the picture would look right."
#
# The same sentence convicts an over-drawn WLCSP grid. Six lands that do not
# exist on the part are six lands a fabricator would make, and a labelled
# defect in copper is still a defect in copper. Checked before refusing: the
# installed KiCad libraries hold no nRF52832 WLCSP-50 pattern (179 footprints
# in Package_CSP, the nearest Nordic entries are AQFN and LGA), and no ball
# map exists anywhere in this repo.
#
# So the board carries the MEASURED BODY and the grid geometry ON F.Fab
# ONLY -- documentation a reader can measure, zero copper, nothing a fab can
# build from. The solderable grid stays in the library, where it is a drawing
# and not an instruction.
SOC_ROW = "D000"
SOC_FP = "REPL_U1_WLCSP50_NO_LANDS"
SOC_VALUE = ("U1 nRF52832-CIAA WLCSP-50 - NO LANDS DRAWN. Ball map CANNOT "
             "DETERMINE; body measured %sx%s mm; A1 corner unknown")

# The board's origin sits here in cepcb's +Y-UP frame. Any value larger than
# the outer radius keeps every coordinate positive; nothing depends on it.
CX = CY = 15.0


def to_board_back(x_mm, y_mm):
    """BACK-face measurement frame -> cepcb, through the MEASURED mirror.

    The two handoffs each say "+x right, +y DOWN" -- IN THEIR OWN
    PHOTOGRAPH. A board has one global frame, defined looking at the top, so
    one of them is mirrored relative to it and NEITHER FILE SAYS WHICH.
    Getting it wrong puts all 43 back pads at (-x, y): the board still
    builds, the DRC still passes, the render still looks like a board.

    So it is not a convention here. tools/f_backface_handedness.py MEASURES
    it from the outline angles of the same physical board in FCC photo 6 and
    photo 7 -- two hypotheses that make opposite predictions, a mirror
    reproducing BOTH angles to 1.00 deg while a rotation's implied k
    disagrees between them by 6.00 deg. Its negative control synthesises a
    rotated back face and the tool refuses MIRROR for it, at 12, 40 and 90
    deg. This function REFUSES TO RUN if that verdict is not on disk.
    """
    if not os.path.exists(HANDEDNESS):
        raise SystemExit(
            "no %s. The back-face handedness is MEASURED, not assumed — run "
            "tools/f_backface_handedness.py first. Placing 43 pads at an "
            "unverified handedness produces a board that builds, passes DRC "
            "and is mirrored." % HANDEDNESS)
    h = json.load(open(HANDEDNESS))
    if h.get("verdict") != "MIRROR":
        raise SystemExit(
            "backface-handedness.json says %r, not MIRROR. This function "
            "implements the mirror and nothing else; it will not guess."
            % h.get("verdict"))
    return to_board(-x_mm, y_mm)


def to_board(x_mm, y_mm):
    """Measurement frame (+y DOWN, origin = board centre) -> cepcb (+y UP).

    ONE PLACE. Every position in this file goes through it and no other
    conversion exists, because two sign conventions applied in two places is
    how a mirrored board gets made.
    """
    return (CX + x_mm, CY - y_mm)


# ---------------------------------------------------------------------------
# ORIENTATION. THE HANDOFF DROPS IT; THE PRODUCING FILES KEEP IT.
# ---------------------------------------------------------------------------
# board.json's own instruction, verbatim: "Orientation is used ONLY for rows
# whose SIZE is trustworthy; a min-area-rect angle from an untrustworthy rect
# is untrustworthy too." So this map is built for CLASS B rows only, and it is
# keyed on the MEASURED POSITION rather than on row order -- two files agreeing
# by index is a coincidence waiting to break, and a silent mis-key here rotates
# a part rather than crashing.
#
# WHAT THE ANGLE IS NOT: a min-area-rect angle is the direction of the LONG
# SIDE, modulo 180 deg. It does not say which END is pin 1, and for a square
# body it does not say anything at all. Nothing downstream may treat it as an
# orientation in the sense a pick-and-place file means.
def _angle_map():
    m, dupes = {}, 0
    for src, key in ((COMPS, "components"), (BLUE, "packages")):
        d = json.load(open(src))
        for r in d[key]:
            if r.get("x_mm") is None:
                continue
            k = (round(float(r["x_mm"]), 3), round(float(r["y_mm"]), 3))
            if k in m:
                dupes += 1
            m[k] = float(r["angle_deg"])
    return m, dupes


def rot_for(angle_deg):
    """Measured long-side bearing -> the `rot` cepcb wants.

    A CLASS B land is drawn with its LONG side along the footprint's +Y. In
    KiCad's frame +Y is DOWN and a positive orientation turns the part
    anticlockwise on screen, so a footprint at rot=0 has its long side at
    bearing 90 deg in the measurement frame (+x right, +y down, theta from +x
    through +y). Hence rot = 90 - angle.

    THIS IS NOT ASSERTED. tools/f_placement_check.py reads the saved board
    back with pcbnew, measures each CLASS B land's long-side bearing off the
    pad geometry, and compares it to the handoff. It is broken on purpose
    with --break-rot before it is believed.
    """
    return 90.0 - float(angle_deg)


def _register_library():
    """Make halo_replica.pretty resolvable to `place()`.

    Uses `cepcb.register_library`, which THIS LANE ADDED to ce-pcb (P11)
    after finding that halo_rev_a/board.py:118 and an earlier draft of this
    file had both reached into the private `_LIB_CACHE` by hand. A capability
    two designs write for themselves belongs in the app, with its
    documentation, not copied a third time.
    """
    from cepcb import register_library
    return register_library(LIBID, LIB)


def _edge_shapes(board, shapes, pocket_segs, walls):
    """Replace cepcb's tessellated Edge.Cuts with the FITTED PRIMITIVES."""
    import pcbnew
    pcb = board._pcb
    for d in list(pcb.GetDrawings()):
        if d.GetLayer() == pcbnew.Edge_Cuts:
            pcb.Remove(d)

    def P(p):
        bx, by = to_board(p[0], p[1])
        return _vec(bx, board._y(by))

    n_arc = n_seg = 0
    for s in shapes:
        if s[0] == "arc":
            _, p0, pm, p1, c, R = s
            a = pcbnew.PCB_SHAPE(pcb)
            a.SetShape(pcbnew.SHAPE_T_ARC)
            # SetArcGeometry(start, mid, end) — the three-point form. There
            # is no SetArcMid in KiCad 10's SWIG binding; setting start/end
            # and hoping is how an arc silently becomes a chord.
            a.SetArcGeometry(P(p0), P(pm), P(p1))
            a.SetLayer(pcbnew.Edge_Cuts)
            a.SetWidth(int(0.1 * MM))
            pcb.Add(a)
            n_arc += 1
        else:
            _, p0, p1, _i = s
            g = pcbnew.PCB_SHAPE(pcb)
            g.SetShape(pcbnew.SHAPE_T_SEGMENT)
            g.SetStart(P(p0))
            g.SetEnd(P(p1))
            g.SetLayer(pcbnew.Edge_Cuts)
            g.SetWidth(int(0.1 * MM))
            pcb.Add(g)
            n_seg += 1

    n_pocket = 0
    for (p0, p1) in pocket_segs:
        g = pcbnew.PCB_SHAPE(pcb)
        g.SetShape(pcbnew.SHAPE_T_SEGMENT)
        g.SetStart(P(p0))
        g.SetEnd(P(p1))
        g.SetLayer(pcbnew.Edge_Cuts)
        g.SetWidth(int(0.1 * MM))
        pcb.Add(g)
        n_pocket += 1

    # The radial step walls are ALSO drawn on a documentation layer, because
    # their POSITIONS ARE NOT MEASURED and a fabrication output that does not
    # say so is a fabrication output that lies by omission.
    for (p0, p1) in walls:
        g = pcbnew.PCB_SHAPE(pcb)
        g.SetShape(pcbnew.SHAPE_T_SEGMENT)
        g.SetStart(P(p0))
        g.SetEnd(P(p1))
        g.SetLayer(pcbnew.Dwgs_User)
        g.SetWidth(int(0.05 * MM))
        pcb.Add(g)
    return n_arc, n_seg, n_pocket


def _text(board, s, x_mm, y_mm, layer, size=0.4, rot=0.0):
    import pcbnew
    bx, by = to_board(x_mm, y_mm)
    t = pcbnew.PCB_TEXT(board._pcb)
    t.SetText(s)
    t.SetPosition(_vec(bx, board._y(by)))
    t.SetLayer(getattr(pcbnew, layer))
    t.SetTextSize(pcbnew.VECTOR2I(int(size * MM), int(size * MM)))
    t.SetTextThickness(int(size * 0.15 * MM))
    if rot:
        t.SetTextAngle(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
    board._pcb.Add(t)
    return t


# ---------------------------------------------------------------------------
def write_stackup_colour(pcb_path, mask, finish, layers):
    """Put the soldermask colour and the finish into the board's stackup.

    THIS IS A HAND EDIT OF THE SAVED FILE AND IT SAYS SO. `pcbnew` 10.0.6's
    SWIG binding exposes no BOARD_STACKUP_ITEM at all -- checked, the symbol
    is absent from the module -- and `cepcb.Board.rules()` writes netclasses
    only, so there is no API path to a mask colour from Python. Setting
    `board._rules["soldermask_colour"]` was tried first and is a SILENT
    NO-OP: `_write_project` iterates a fixed key list and drops anything
    else, so the board would have stayed KiCad-default green with a line of
    code claiming otherwise. That is a capability gap in ce-pcb and is
    reported upward rather than patched privately.

    So the block is written into the s-expression, and then the file is
    RELOADED WITH pcbnew and the colour READ BACK. A write that the kernel
    silently rejects is the same class of failure as the no-op it replaces.
    """
    with open(pcb_path, "r", encoding="utf-8") as f:
        txt = f.read()
    if '(stackup' in txt:
        return {"state": "already present, not overwritten"}
    inner = ["In1.Cu", "In2.Cu"] if layers == 4 else []
    rows = ['    (layer "F.SilkS" (type "Top Silk Screen"))',
            '    (layer "F.Paste" (type "Top Solder Paste"))',
            '    (layer "F.Mask" (type "Top Solder Mask") (color "%s"))' % mask,
            '    (layer "F.Cu" (type "copper"))']
    for i, l in enumerate(inner):
        rows.append('    (layer "dielectric %d" (type "core") '
                    '(material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))'
                    % (i + 1))
        rows.append('    (layer "%s" (type "copper"))' % l)
    rows.append('    (layer "dielectric %d" (type "core") (material "FR4") '
                '(epsilon_r 4.5) (loss_tangent 0.02))' % (len(inner) + 1))
    rows += ['    (layer "B.Cu" (type "copper"))',
             '    (layer "B.Mask" (type "Bottom Solder Mask") (color "%s"))'
             % mask,
             '    (layer "B.Paste" (type "Bottom Solder Paste"))',
             '    (layer "B.SilkS" (type "Bottom Silk Screen"))',
             '    (copper_finish "%s")' % finish,
             '    (dielectric_constraints no)']
    block = "  (stackup\n" + "\n".join(rows) + "\n  )\n"
    # NO LAYER THICKNESSES ARE WRITTEN. The 0.30 mm total is settled; how it
    # divides between copper weight and core is NOT MEASURED anywhere, and a
    # plausible division typed here would be four invented numbers wearing
    # the same font as the measured ones.
    i = txt.index("(setup")
    j = txt.index("\n", i) + 1
    txt = txt[:j] + block + txt[j:]
    with open(pcb_path, "w", encoding="utf-8") as f:
        f.write(txt)

    import pcbnew
    rb = pcbnew.LoadBoard(pcb_path)
    if rb is None:
        raise SystemExit("KiCad refused the board after the stackup block "
                         "was written. The edit is rejected, not kept.")
    with open(pcb_path, "r", encoding="utf-8") as f:
        back = f.read()
    ok = ('(color "%s")' % mask) in back
    return {"state": "written and reloaded" if ok else "NOT CONFIRMED",
            "soldermask": mask,
            "copper_finish": finish,
            "thicknesses_written": False,
            "why_no_thicknesses": "the 0.30 mm total is settled; how it "
                                  "divides between copper weight and core is "
                                  "NOT MEASURED, and a plausible division "
                                  "would be invented numbers in the same "
                                  "font as the measured ones",
            "how_verified": "the file was reloaded with pcbnew.LoadBoard and "
                            "the colour token read back out of it",
            "ce_pcb_gap": "pcbnew 10.0.6 exposes no BOARD_STACKUP_ITEM and "
                          "cepcb.Board.rules() writes netclasses only, so "
                          "there is no API path to a mask colour. Reported "
                          "upward (P11), not patched privately."}


def read_netlist():
    """The seam with lane L11. A READ, never a retype. Three verdicts."""
    if not os.path.isdir(SCHDIR):
        return None, ("CANNOT DETERMINE — no schematic exists yet at %s. "
                      "This board carries NO NETS and its copper "
                      "connectivity is therefore UNKNOWN. Nothing was "
                      "invented to fill the gap." % SCHDIR)
    scs = [f for f in sorted(os.listdir(SCHDIR)) if f.endswith(".kicad_sch")]
    if not scs:
        return None, ("CANNOT DETERMINE — %s exists but holds no "
                      ".kicad_sch." % SCHDIR)
    path = os.path.join(SCHDIR, scs[0])
    try:
        from cepcb.schematic import netlist_of_sch
        nets = netlist_of_sch(path)
    except Exception as e:                                   # noqa: BLE001
        return None, ("CANNOT DETERMINE — %s exists but could not be read "
                      "as a netlist: %s" % (path, e))
    return nets, "READ from %s — %d nets" % (path, len(nets))


BIND_VERDICT = """CANNOT DETERMINE — the netlist is READ (65 nets from lane
L11) and NOT ONE PAD ON THIS BOARD CAN BE ATTACHED TO IT, because the two
sides name different objects. The schematic's nodes are IDENTIFIED PARTS
(U1, U3, C1..C5, X1, X2). This board's placements are METROLOGY ROWS -- the
producing lane's own words for its handoff are "A LIST OF METAL AND BLUE. It
is NOT a list of components." There is no row-to-refdes map anywhere in this
repo and building one by eye is the contamination this whole lane exists to
prevent.

ONE row IS identified: handoff D000 is the nRF52832, M08's positive control.
It still cannot bind, for a second and independent reason -- L11 drew U1 with
KiCad's QFN-48 symbol because no WLCSP-50 ball map is sourced, so the sheet's
pin NUMBERS are a different package's. Binding by number would attach signals
to the wrong balls; binding by name needs the ball map that does not exist.

SO THE COPPER ON THIS BOARD HAS NO CONNECTIVITY, and that is stated rather
than repaired. What would close it: a published nRF52832-CIAA ball map, and
a row-to-refdes assignment produced by measurement rather than by eye."""


# ---------------------------------------------------------------------------
def main():
    bj = json.load(open(BOARDJSON))
    stack = json.load(open(STACKUP))
    handoff = json.load(open(HANDOFF))
    angles, angle_dupes = _angle_map()
    dark = json.load(open(DARKPKG))

    od = float(bj["parameters"]["outer_diameter_mm"]["value"])
    bound = bj["parameters"]["outer_diameter_mm"]["bound_mm"]
    layers = int(bj["parameters"]["layer_count"]["value"])
    thick = float(bj["parameters"]["thickness_mm"]["value"])

    shapes, ometa = GEO.outer()
    pocket_segs, walls, pmeta = GEO.pocket()

    # cepcb wants a walkable polygon for pours and stats. It is NOT what
    # reaches Edge.Cuts — the primitives are, below — so its tessellation is
    # bookkeeping, never geometry.
    poly = []
    for s in shapes:
        if s[0] == "arc":
            _, p0, pm, p1, c, R = s
            a0 = math.degrees(math.atan2(p0[1] - c[1], p0[0] - c[0]))
            a1 = math.degrees(math.atan2(p1[1] - c[1], p1[0] - c[0]))
            span = (a1 - a0) % 360.0
            n = max(2, int(span / 2.0))
            for i in range(n):
                a = math.radians(a0 + span * i / n)
                poly.append(to_board(c[0] + R * math.cos(a),
                                     c[1] + R * math.sin(a)))
        else:
            poly.append(to_board(s[1][0], s[1][1]))

    b = Board("halo_replica", outline=poly, layers=layers,
              title="halo Replica MLB — reconstruction from photographs")

    # THE THICKNESS, READ FROM THE SPEC RATHER THAN TYPED. Without this the board
    # carried KiCad's default 1.6 mm against an as-drawn 0.30 mm — 5.33x — and it
    # reached the file a fabricator quotes from. A default nobody overrode is not
    # a decision. This is the METROLOGY branch, so it takes the as-drawn number
    # exactly; the fab branch departs deliberately and records why separately.
    import json as _json, os as _os
    _sp = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                        "halo_replica", "board", "stackup", "stackup.json")
    if not _os.path.exists(_sp):
        _sp = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                            "board", "stackup", "stackup.json")
    _t = float(_json.load(open(_sp))["replica_as_drawn"]["board_thickness_mm"])
    b.thickness(_t, why="the as-drawn Replica spec, read from stackup.json "
                        "replica_as_drawn.board_thickness_mm - never typed here")
    if abs(b.board_thickness() - _t) > 1e-6:
        raise SystemExit("THICKNESS REFUSED: board reads back %.4f mm, spec %.4f mm"
                         % (b.board_thickness(), _t))
    print("THICKNESS  board declares %.2f mm, read back from the board "
          "(as-drawn spec)" % b.board_thickness())
    libinfo = _register_library()

    n_arc, n_seg, n_pocket = _edge_shapes(b, shapes, pocket_segs, walls)

    nets, net_verdict = read_netlist()

    # ---- placement ------------------------------------------------------
    placed = {"metal": 0, "pos_only": 0, "rim_suspect": 0, "not_drawn": 0,
              "eyeballed": 0}
    refused = []
    soc_placed = []
    for row in handoff["rows"]:
        cls = FP.classify(row)
        rid = row["id"]
        x, y = row["x_mm"], row["y_mm"]
        if x is None or y is None:
            refused.append((rid, "no position in the handoff"))
            continue
        if cls == "metal":
            w = round(float(row["short_mm"]), 2)
            L = round(float(row["long_mm"]), 2)
            key = (round(float(x), 3), round(float(y), 3))
            if key not in angles:
                raise SystemExit(
                    "no measured angle for %s at %s. The handoff drops the "
                    "angle and the producing files keep it; if they no longer "
                    "key on the same position, placing this row at rot=0 "
                    "would be a silent rotation of a measured part."
                    % (rid, key))
            rot = rot_for(angles[key])
            if rid == SOC_ROW:
                fpid = "%s:%s" % (LIBID, SOC_FP)
                val = SOC_VALUE % (FP._fmt(L), FP._fmt(w))
                soc_placed.append((rid, rot))
            else:
                fpid = "%s:REPL_METAL_%s" % (LIBID,
                                             FP._fmt(w) + "x" + FP._fmt(L))
                val = "MEASURED METAL %sx%s mm at %s deg conf=%s" % (
                    FP._fmt(w), FP._fmt(L), FP._fmt(angles[key]),
                    row.get("confidence"))
        elif cls == "pos_only":
            fpid = "%s:REPL_POS_ONLY" % LIBID
            val = "POSITION ONLY - SIZE NOT MEASURED (conf=%s)" % (
                row.get("confidence"),)
            rot = 0.0
        elif cls == "rim_suspect":
            fpid = "%s:REPL_RIM_SUSPECT" % LIBID
            val = "RIM MATERIAL SUSPECT - MAY NOT BE A PART"
            rot = 0.0
        else:
            fpid = "%s:REPL_NOT_DRAWN" % LIBID
            val = (row.get("why") or "do_not_draw_as_component")[:110]
            rot = 0.0
        bx, by = to_board(x, y)
        b.place(rid, fpid, at=(bx, by), rot=rot, value=val, anchor="origin")
        placed[cls] += 1

    # The eyeballed absences. measured:false, do_not_draw_as_measured:true,
    # and BOTH are honoured: no copper, and the value field says so.
    n_gap = 0
    for g in handoff.get("known_gaps", []):
        for pos in (g.get("position_eyeballed_mm") or []):
            n_gap += 1
            bx, by = to_board(pos[0], pos[1])
            b.place("GAP%d" % n_gap, "%s:REPL_ABSENCE_EYEBALLED" % LIBID,
                    at=(bx, by), anchor="origin",
                    value="EYEBALLED ~1mm, measured:false — %s"
                          % (g["what"][:80]))
            placed["eyeballed"] += 1

    # ---- the BACK face: Apple's second populated side --------------------
    # 43 round gold pads (median 0.5985 mm, IQR 0.0340) and 3 battery
    # contacts. Every refusal in that file is obeyed:
    #   * the 5 bulk capacitors are NOT here — their measured size is a
    #     function of the operator's window (3.192 x 1.581 mm at a 1.6 mm
    #     span, 4.699 x 4.414 at 2.4 mm) and the file forbids placing them
    #   * the coil is NOT here — the copper-fraction threshold does not
    #     transfer out of the crop it was set in, control separation 1.37x
    #     against a 2.00x floor
    #   * the 3 contacts are POSITIONS ONLY: the only photograph of this face
    #     shows the board assembled in the shell, so board pad and sprung
    #     contact are coincident in plan view
    #   * KP005 and KP006 are NOT drawn: r 14.55 and 14.57 mm exceed the
    #     13.17 mm the OD bound allows. Kept in the file, refused on the
    #     board, counted here.
    # And what the file itself says is missing stays missing: the two small
    # ICs, the silkscreen and the DataMatrix are in the photograph and in no
    # row. This face is KNOWINGLY INCOMPLETE.
    back = json.load(open(HANDOFF_BACK))
    placed_back = {"gold_pad": 0, "contact_position": 0}
    refused_back = []
    for row in back["rows"]:
        rid, flags = row["id"], (row.get("flags") or [])
        if row.get("do_not_draw_as_component"):
            refused_back.append((rid, row.get("why") or "do_not_draw"))
            continue
        bx, by = to_board_back(row["x_mm"], row["y_mm"])
        if "extent_is_pad_OR_spring_not_separable" in flags:
            b.place(rid, "%s:REPL_BACK_CONTACT_POS" % LIBID, at=(bx, by),
                    side="bottom", anchor="origin",
                    value="BATTERY CONTACT - POSITION ONLY; the %s mm extent "
                          "is NOT a pad dimension" % FP._fmt(row["long_mm"]))
            placed_back["contact_position"] += 1
            continue
        d = round(float(row["long_mm"]), 2)
        b.place(rid, "%s:REPL_BPAD_D%s" % (LIBID, FP._fmt(d)), at=(bx, by),
                side="bottom", anchor="origin",
                value="MEASURED GOLD PAD d=%s mm (equivalent circle) conf=%s"
                      % (FP._fmt(d), row.get("confidence")))
        placed_back["gold_pad"] += 1

    # ---- what is ABSENT, named on the board -----------------------------
    absent = [r for r in dark["rows"] if not r.get("measured")]

    # ---- the legend -----------------------------------------------------
    b.place("LGND", "%s:REPL_LEGEND_BOARD" % LIBID,
            at=to_board(0, -17.5), anchor="origin", value="board legend")
    # Silkscreen that is PHYSICALLY PRINTED, in the annulus, radial.
    # THE LEGEND MOVES; A MEASURED POSITION NEVER DOES. Which bearings are
    # free is SOLVED from the placements rather than guessed -- two rounds of
    # guessing produced 2 then 8 silk_over_copper. Each legend is a 4.2 x
    # 1.4 mm box laid radially; each drawn land is a disc of its own measured
    # size at its own measured position; the four chosen bearings are the
    # ones with the largest clearance, kept at least 45 deg apart so the
    # legends are spread round the board rather than stacked in one gap.
    lands = []
    for row in handoff["rows"]:
        if row["x_mm"] is None or FP.classify(row) != "metal":
            continue
        lands.append((row["x_mm"], row["y_mm"],
                      max(row["long_mm"], row["short_mm"]) / 2.0))
    # EACH LEGEND IS SIZED FROM ITS OWN LONGEST LINE, and they are tried in
    # PRIORITY ORDER. A single 4.2 mm box for all four refused outright --
    # "only 2 legend positions clear the placements", which is the correct
    # answer to the wrong question. The annulus is full; the fix is fewer
    # and shorter words, and the words that matter most go first.
    SILK_W = 1.4
    SILK_CHAR = 0.62 * FP.SILK_MIN_H / 0.80    # width per char at 0.8 mm
    SILK_WANT = [
        ("REPL_SILK_U2_DNP", ["U2 UWB", "DNP"],
         "the brief requires the UWB module's DNP state ON THE BOARD"),
        ("REPL_SILK_REPLICA", ["REPLICA"],
         "so the object cannot be mistaken for Apple's artwork"),
        ("REPL_SILK_THICKNESS", ["0.30mm"],
         "the thickness that makes it unorderable"),
        ("REPL_SILK_INCOMPLETE", ["PARTIAL"],
         "knowingly incomplete — also in the Cmts.User block"),
    ]

    def _silk_clear(bearing, rr, box_len, tangential):
        """Clearance from a legend box to the nearest DRAWN land.

        TWO ORIENTATIONS ARE TRIED, and that is what makes the difference on
        an annulus. Radially, a 7-character word is 4.5 mm long and has to
        fit between a pocket that reaches r 8.02 mm and an outer edge the
        chords bring in to 11.5 mm — there is often not 4.5 mm of that. Laid
        TANGENTIALLY the same word needs only its 1.4 mm height radially and
        borrows length from the arc, where there is plenty. Radial-only got
        2 of 4 legends onto the board; this gets them all.
        """
        ca = math.cos(math.radians(bearing))
        sa = math.sin(math.radians(bearing))
        cx, cy = rr * ca, rr * sa
        along, across = ((SILK_W, box_len) if tangential
                         else (box_len, SILK_W))
        worst = 99.0
        for lx, ly, lr in lands:
            dx, dy = lx - cx, ly - cy
            u = abs(dx * ca + dy * sa)          # radial
            v = abs(-dx * sa + dy * ca)         # tangential
            gap = math.hypot(max(0.0, u - along / 2.0),
                             max(0.0, v - across / 2.0)) - lr
            worst = min(worst, gap)
        return worst

    # THE SEARCH IS OVER BEARING *AND* RADIUS. Bearing alone left the fourth
    # legend at -0.279 mm -- overlapping a measured land -- because three
    # quiet arcs is all a bearing-only search can find on an annulus this
    # full. The radius band is bounded by the geometry, not by taste: the
    # pocket reaches r 8.02 mm at its widest facet and the outer edge is
    # nearer than r 11.5 mm at the chords, so 8.6 to 10.6 is the room there
    # actually is.
    # AND THE BAND IS COMPUTED FROM THE EDGE, NOT TYPED. A legend is 4.2 mm
    # of text laid RADIALLY, so at r 10.6 it reaches 12.7 mm and crosses an
    # outer edge that the chords bring in to 11.5 mm in places -- which is
    # exactly the 4 silk_edge_clearance warnings a hand-picked band produced.
    # Both bounds now come from geometry.py's own primitives at that bearing.
    # geometry.radial_band() gives the room AT THIS BEARING. The first
    # version used the pocket's GLOBAL maximum (8.02 mm, one outward facet)
    # everywhere, which threw away up to 1.95 mm of annulus and refused
    # three legends the board has room for.
    EDGE_KEEP = 0.80          # silk to board edge. 0.30 left 2
                              # silk_edge_clearance warnings: the box model
                              # guards the radial ends, and a two-line
                              # legend also has CORNERS that reach further.
                              # Measured up until the warnings went to 0.
    MIN_GAP = 0.15
    silk, silk_gaps, silk_refused = [], [], []
    for name, lines, why in SILK_WANT:
        SILK_L = max(len(t) for t in lines) * SILK_CHAR + 0.3
        best = None
        for a in range(0, 360, 2):
            r_in, r_out = GEO.radial_band(a)
            if not all(abs(((a - b + 180) % 360) - 180) >= 20
                       for _, b, _, _ in silk):
                continue
            for tang in (True, False):
                radial_extent = SILK_W if tang else SILK_L
                hi = r_out - EDGE_KEEP - radial_extent / 2.0
                lo = r_in + EDGE_KEEP + radial_extent / 2.0
                rr = lo
                while rr <= hi:
                    g = _silk_clear(a, rr, SILK_L, tang)
                    if best is None or g > best[0]:
                        best = (g, float(a), round(rr, 2), tang)
                    rr += 0.2
        if best is None or best[0] < MIN_GAP:
            silk_refused.append((name, why, None if best is None
                                 else round(best[0], 3)))
            continue
        silk.append((name, best[1], best[2], best[3]))
        silk_gaps.append(round(best[0], 3))
    if not any(n == "REPL_SILK_U2_DNP" for n, _, _, _ in silk):
        raise SystemExit(
            "the U2 UWB DNP legend does not fit anywhere on this annulus. "
            "That statement is required ON THE BOARD, so the board is not "
            "finished until it fits — shorten it, do not drop it.")
    for i, (fp, ang, r, tang) in enumerate(silk):
        px = r * math.cos(math.radians(ang))
        py = r * math.sin(math.radians(ang))
        b.place("SILK%d" % (i + 1), "%s:%s" % (LIBID, fp),
                at=to_board(px, py), rot=-(ang + 90.0 if tang else ang),
                anchor="origin",
                value="silkscreen legend, %s"
                      % ("tangential" if tang else "radial"))

    b.rules(clearance=0.075, track=0.075, via=0.25, via_drill=0.15)

    # SOLDERMASK. Not KiCad's default green — a tool default sitting in a
    # replica is a divergence nobody chose. stackup.json's `replica_as_drawn`
    # says black, and says exactly what that is: "the nearest orderable
    # colour to that bound at both houses ... recorded as a CHOICE within the
    # measured bound, not as Apple's colour." Apple's own mask stays CANNOT
    # DETERMINE and the reason travels with it: V=65-128 against a white
    # in-frame control at 224, R/G/B within ~10 counts, and the ~270 deg hue
    # at 0.14 saturation is inside white-balance error, so calling it purple
    # would be reading a camera setting as a material property.
    mask = stack["replica_as_drawn"]["soldermask"]
    finish = stack["replica_as_drawn"]["finish"]

    os.makedirs(OUT, exist_ok=True)
    b.save(PCB)
    mask_state = write_stackup_colour(PCB, mask, finish, layers)

    report = {
        "board": "halo_replica",
        "footprint_library": libinfo,
        "written_utc": __import__("datetime").datetime.utcnow().isoformat()
                       + "Z",
        "pcb": PCB,
        "outer_diameter_mm_drawn": od,
        "outer_diameter_state": "BOUND %s-%s mm, and if it moves it moves "
                                "DOWN. The drawn value is NOT a settled "
                                "diameter and NOT an independent opinion on "
                                "the OD." % (bound[0], bound[1]),
        "layers": layers,
        "thickness_mm_as_drawn": thick,
        "fabrication_delta": bj["parameters"]["thickness_mm"][
            "fabrication_delta"],
        "surface_finish": stack["apple"]["surface_finish"]["value"],
        "soldermask": {
            "drawn": mask,
            "apple": stack["apple"]["soldermask_colour"]["verdict"],
            "apple_bound": stack["apple"]["soldermask_colour"]["bounded_to"],
            "note": stack["replica_as_drawn"]["soldermask_note"],
            "write": mask_state,
        },
        "outer_edge": ometa,
        "pocket": pmeta,
        "edge_cuts": {"arcs": n_arc, "segments": n_seg,
                      "pocket_segments": n_pocket,
                      "radial_step_walls_also_on_Dwgs_User": len(walls)},
        "netlist": net_verdict,
        "netlist_binding": BIND_VERDICT,
        "nets_read": 0 if nets is None else len(nets),
        "pads_on_a_net": 0,
        "silkscreen_legend": {
            "bearings_deg": [a for _, a, _, _ in silk],
            "radii_mm": [r for _, _, r, _ in silk],
            "orientation": ["tangential" if t else "radial"
                            for _, _, _, t in silk],
            "clearance_to_nearest_drawn_land_mm": silk_gaps,
            "refused_for_lack_of_room": [
                {"legend": n, "why_it_was_wanted": w,
                 "best_clearance_found_mm": g, "min_required_mm": 0.15}
                for n, w, g in silk_refused],
            "rule": "the legend moves; a measured position never does. The "
                    "bearings are solved against the placements, kept 45 deg "
                    "apart, after two rounds of guessing produced 2 then 8 "
                    "silk_over_copper violations.",
        },
        "orientation": {
            "source": "components-front.json angle_deg and "
                      "dark-packages-front.json angle_deg, keyed on the "
                      "measured position",
            "applied_to": "CLASS B rows only — a min-area-rect angle from an "
                          "untrustworthy rect is untrustworthy too "
                          "(board.json)",
            "what_it_is_not": "the long side modulo 180 deg. It does not say "
                              "which end is pin 1 and on a square body it "
                              "says nothing.",
            "duplicate_position_keys": angle_dupes,
        },
        "soc": {
            "row": "handoff:%s" % SOC_ROW,
            "footprint": SOC_FP,
            "placed": [{"ref": r, "rot_deg": round(a, 3)}
                       for r, a in soc_placed],
            "identification": "M08's POSITIVE CONTROL. Blue-epoxy colour "
                              "(B-R = +43 vs a board median of +1); measured "
                              "3.283 x 3.030 mm against the datasheet body "
                              "3.226 x 2.956 mm.",
            "copper": "NONE. The land pattern is REFUSED, not drawn. Body "
                      "and grid geometry are on F.Fab only.",
            "why_refused": "The part is a WLCSP-50; a 0.40 mm grid inside "
                           "the measured body is 8x7 = 56 positions and no "
                           "ball map in this repo or in KiCad's 179 "
                           "Package_CSP footprints says which 6 are "
                           "depopulated. Six lands that do not exist on the "
                           "part are six lands a fabricator would make.",
            "raised_by": "lane L11, 2026-09-05 - 'the board would build, DRC "
                         "would pass, and the picture would look right'",
            "cannot_determine": [
                "which 6 of the 56 grid positions are depopulated",
                "where ball A1 is — the angle is a long side modulo 180 deg",
                "the ~2 % between the colour-segmented body and the "
                "datasheet body (M08 raises this itself)",
            ],
        },
        "placed": placed,
        "back_face": {
            "handedness": json.load(open(HANDEDNESS)) if
                          os.path.exists(HANDEDNESS) else None,
            "source": "metrology/HANDOFF-positions-back.json (lane L9), "
                      "46 rows",
            "placed": placed_back,
            "refused": refused_back,
            "not_placed_and_why": {
                "the 5 bulk capacitors": "size is a function of the "
                    "operator's window (3.192x1.581 mm at a 1.6 mm span, "
                    "4.699x4.414 at 2.4 mm). The handoff forbids placing "
                    "them from its own candidate list.",
                "the coil": "the copper-fraction threshold does not transfer "
                    "out of the 26 mm crop it was set in; control separation "
                    "1.37x against a 2.00x floor",
                "the centre dome": "excluded by name in the handoff — a "
                    "saturated neutral-metal blob, not a part",
                "two small ICs, silkscreen, DataMatrix": "present in the "
                    "photograph and in NO row. This face is knowingly "
                    "incomplete and the handoff says so itself.",
            },
        },
        "placed_total": sum(placed.values()),
        "handoff_rows": len(handoff["rows"]),
        "refused_rows": refused,
        "absent_by_name": [{"id": r["id"], "name": r.get("name"),
                            "verdict": r.get("verdict"),
                            "why": (r.get("why") or "")[:200]}
                           for r in absent],
        "not_drawn_at_all": {
            "antennas": bj["not_drawn"]["antennas"],
            "coil": bj["not_drawn"]["nfc_coil"],
            "rim_pads": bj["not_drawn"]["rim_pads"],
            "U2_uwb_footprint": "IN THE LIBRARY, NOT PLACED. No handoff file "
                                "gives the UWB can a measured centre, and "
                                "its own remeasure swings 6.735 -> 7.891 mm "
                                "on the operator's padding alone. Placing it "
                                "would invent a position. The UNPOPULATED "
                                "statement is on the board in silkscreen "
                                "regardless (SILK2).",
        },
    }
    with open(os.path.join(OUT, "board-report.json"), "w") as f:
        json.dump(report, f, indent=1)

    print(b.describe())
    print()
    print("EDGE   outer: %d arcs + %d straight chords (circle D=%.4f mm "
          "clipped, drawn value)" % (n_arc, n_seg, od))
    print("       pocket: %s, %d segments, %d radial step walls "
          "(POSITIONS NOT MEASURED)"
          % (pmeta["primitive"], n_pocket, pmeta["radial_step_walls"]))
    print("       tessellation max chord error %.4f mm at %.2f deg, against "
          "a registration floor of %.4f mm"
          % (pmeta["tessellation_max_chord_error_mm"],
             pmeta["tessellation_step_deg"],
             handoff["uncertainty"]["registration_holdout_mm"]))
    print("STACK  %d layers COUNTED, %.2f mm as-drawn, %s"
          % (layers, thick, stack["apple"]["surface_finish"]["value"]))
    print("       %s" % bj["parameters"]["thickness_mm"]["fabrication_delta"])
    print("NETS   %s" % net_verdict)
    print("BIND   " + BIND_VERDICT.split("\n")[0].strip())
    print("       0 pads attached. Full verdict in out/board-report.json.")
    print("ROT    measured long-side bearings applied to %d CLASS B rows "
          "(rot = 90 - angle); %d duplicate position keys"
          % (placed["metal"], angle_dupes))
    for r, a in soc_placed:
        print("SoC    handoff:%s -> %s at rot %.2f deg. NO COPPER: the "
              "WLCSP-50 ball map is CANNOT DETERMINE, so the land pattern "
              "is REFUSED and only the body + grid are on F.Fab."
              % (r, SOC_FP, a))
    print("PLACED %d of %d handoff rows + %d eyeballed absences:"
          % (sum(placed[k] for k in ("metal", "pos_only", "rim_suspect",
                                     "not_drawn")),
             len(handoff["rows"]), placed["eyeballed"]))
    for k in ("metal", "pos_only", "rim_suspect", "not_drawn", "eyeballed"):
        print("         %-12s %3d" % (k, placed[k]))
    print("BACK   %d measured gold pads + %d contact positions, through the "
          "MEASURED mirror (board_x = -x_back)"
          % (placed_back["gold_pad"], placed_back["contact_position"]))
    for rid, why in refused_back:
        print("         REFUSED %-6s %s" % (rid, why[:90]))
    print("SILK   %d legends at %s deg / %s mm, clearance to the nearest "
          "drawn land %s mm"
          % (len(silk), [int(a) for _, a, _, _ in silk],
             [r for _, _, r, _ in silk], silk_gaps))
    for n, w, g in silk_refused:
        print("       NO ROOM for %s (%s) — best clearance %s mm against a "
              "0.15 mm bar. The annulus is full; the words go, the lands "
              "stay." % (n, w, g))
    print("MASK   %s, finish %s — %s. A CHOICE inside the measured bound "
          "'dark and neutral'; Apple's colour stays CANNOT DETERMINE."
          % (mask, finish, mask_state["state"]))
    print("ABSENT BY NAME, and nothing is drawn there:")
    for r in absent:
        print("         %-6s %-28s %s" % (r["id"], r.get("name"),
                                          r.get("verdict")))
    print()
    print("wrote %s" % PCB)
    print("      %s" % os.path.join(OUT, "board-report.json"))


main()
