"""halo revision A — the board. Ø26.00 mm, four layers, notched and keyed.

    cd ~/dev/ce-workshop
    ce-pcb/bin/pcb ce-designs/halo/electronics/halo_rev_a/board.py

LANE B1. The netlist is NEVER RETYPED here: it is read back out of
`out/halo_rev_a.kicad_sch` with `cepcb.schematic.netlist_of_sch`, so the
copper and the drawing cannot drift apart, and `bin/sch check` grades them
against each other afterwards. If a pin moves on the sheet it moves here.

---------------------------------------------------------------------------
THE OUTLINE IS Ø26.00, AND THE BRIEF SAID Ø31.87. THE BRIEF IS QUOTING THE
SHELL.
---------------------------------------------------------------------------
SPEC.md §4 gives 31.87 mm as "maximum outer diameter … occurs at z = 4.34 mm",
which is the moulded shell's widest section, not the board. Lane M's
mechanical source — ce-designs/halo/design.py, the single place every
mechanical number in this project is typed — fixes the board:

    D_PCB         = 26.00     the disc
    T_PCB         =  0.600    its thickness
    PCB_NOTCH_DEG = 26.0      three keying notches
    R_PCB_NOTCH   = 12.60     how deep they cut
    TAB_ANGLES    = 0/120/240 where they are
    D_CARRIER_RIM = 26.20     the carrier's locating rim = Ø26.00 + 0.10

A Ø31.87 board cannot fit inside a Ø31.87 shell, and a board that ignores
the notches goes in the wrong way round and lands the antenna feed on the
wrong carrier trace — which is exactly what lane M put the notches there to
prevent. So the board is Ø26.00 with the notches, and this paragraph is the
record of the substitution rather than a silent correction.

---------------------------------------------------------------------------
WHAT DECIDES EVERY PLACEMENT: THE CELL IS UNDER THE BOARD
---------------------------------------------------------------------------
design.py again: Z_CELL_TOP = 4.022, Z_DECK_TOP = 4.600. A Ø20.0 mm steel
can sits 0.578 mm below the middle of this disc, spanning R 0 to R 10.0.
That single fact writes the floorplan:

  * R 10.0 -> 13.0 is THE ONLY ANNULUS WITH NO BATTERY UNDER IT, 3.0 mm
    wide. Both antennas have to live there or live over steel.
  * The 2.4 GHz antenna gets a sector of it with ALL FOUR LAYERS cleared
    beneath — an inverted-F over a ground plane is a short circuit, and an
    inverted-F over a battery can is not an antenna anybody can predict.
  * The NFC coil takes the rest of the annulus on the BOTTOM layer, so the
    two are not on the same copper. 13.56 MHz and 2.44 GHz do not couple
    strongly, but their copper competes for the same 3 mm and SPEC.md §4
    already flagged that as lane C's warning.
  * Actives go on the BOTTOM (B.Cu), passives on the TOP (F.Cu). Not for
    signal-integrity reasons — because of height, below.

---------------------------------------------------------------------------
THE HEIGHT DELTA, MEASURED, AND NOT ABSORBED
---------------------------------------------------------------------------
Lane M's stack allows, per design.py's own budget table:

    top face, inside Ø21.2      0.400 mm   (the bender's moving gap)
    top face, Ø21.2 -> Ø26.0    ~0.9-1.2 mm (the shell's inner surface)
    bottom face, over the cell   0.578 mm   (4.600 - 4.022)
    bottom face, over a finger   0.428 mm   (4.600 - 4.172)

Against that, the parts this circuit needs:

    QFN-48 6x6 (U1)             0.85 mm    OVER by 0.27 mm on the best face
    0603 inductor (L1)          0.90 mm    OVER by 0.32 mm
    3215 crystal (X1)           0.90 mm    OVER by 0.32 mm
    USON-8 (U3)                 0.60 mm    OVER by 0.02 mm
    LGA-12 (U2)                 0.70 mm    OVER by 0.12 mm
    0402 (bulk C9-C12)          0.55 mm    fits, 0.03 mm spare
    0201 (everything else)      0.33 mm    fits

FIVE OF THE SEVEN PART CLASSES DO NOT FIT. This is not a rounding error and
it is not this lane's to close alone — the stack belongs to lane M. The
board is drawn anyway, because the netlist, the outline, the keep-outs and
the routing are all correct regardless of who finds the 0.32 mm, and a board
that is not drawn teaches nobody anything. `report()` at the bottom prints
the table above every run so it cannot be forgotten, and
electronics/README.md carries the four candidate resolutions.

---------------------------------------------------------------------------
WHAT THIS BOARD DOES NOT CLAIM
---------------------------------------------------------------------------
  * THE ANTENNA GEOMETRY IS THIS FILE'S, NOT ce-rf's. Lane T3 owns the
    shape and, as of this writing, its two round-board cases resonate at
    4.0 and 5.8 GHz instead of 2.44 and it is retuning — on a Ø30 outline,
    which is not this board either. So the AE1 element drawn here is a
    PARAMETRIC PLACEHOLDER at a length computed from a quarter wavelength,
    put where the copper has to go, so that ce-rf has real geometry to
    solve instead of a blank annulus. Its S11 is CANNOT DETERMINE until
    ce-rf measures THIS copper. It is not asserted to work.
  * THE NFC COIL'S INDUCTANCE IS UNMEASURED, so C24/C25's 130 pF is a
    placeholder, exactly as the schematic says (X-2).
  * A PASSING DRC MEANS MANUFACTURABLE, NOT CORRECT. Whether the circuit
    works is the schematic's question and the simulators'.
"""
# AE1 TOPOLOGY IS NOT SETTLED, and this file used to call it three things.
# It was described here as a "meandered quarter-wave monopole", an "inverted-F"
# and an "inverted-L monopole" in three separate places. Those are three
# different topologies with three different counterpoise requirements, so a
# reader could not tell what was drawn and neither could anyone setting up a
# solver port. The names were removed rather than one being picked, because
# picking one would assert something nobody has established.
#
# What IS established, measured: the element is a meandered trace on F.Cu only,
# nine teeth, conductor 24.49100 mm against a quarter-wave target of the same,
# error -0.00000, copper R11.1920-R12.2000 at theta 256-340 degrees, fed at one
# end with the other end open. Whether that behaves as a monopole, an
# inverted-F or an inverted-L on THIS ground depends on the counterpoise, which
# is what ce-rf is still trying to characterise -- three hypotheses refuted so
# far (DECISIONS.md D26b-D26e).
#
# Call it "the AE1 element" until a solve identifies its mode.

import json
import math
import os
import sys

from cepcb import Board, find                                      # noqa: F401
from cepcb import kicad as _kicad
from cepcb.schematic import netlist_of_sch

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# REGISTER halo's OWN .pretty. `cepcb.footprint_libraries()` scans only
# KiCad's SharedSupport tree, so a project-local library is invisible to
# `load_footprint()` and to `find()`. Priming the cache here rather than
# editing ce-pcb, because lane T1 owns that repo and a shared tool should not
# grow a halo-shaped hole. THIS IS A GAP IN ce-pcb, NOT A HALO PREFERENCE:
# every board with a part the catalogue does not carry hits it, and it is
# filed to T1 as a P11 item (a `libs=` argument on Board, or a read of the
# project's own fp-lib-table, would close it for everyone).
# ---------------------------------------------------------------------------
_kicad.footprint_libraries()                       # build the cache, then add
_kicad._LIB_CACHE["halo"] = os.path.join(HERE, "halo.pretty")
_kicad._INDEX = None                               # so find() re-indexes

# The etched geometry lives in footprints.py and is IMPORTED, not re-typed.
# The antenna element and the NFC winding are drawn here as tracks; their
# radii, widths and turn counts are that file's, so a change there moves the
# copper here and cannot leave the two disagreeing.
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import footprints as fpg                                          # noqa: E402
SCH = os.path.join(HERE, "out", "halo_rev_a.kicad_sch")
OUT = os.path.join(HERE, "out", "halo_rev_a.kicad_pcb")

# ==========================================================================
# 1. LANE M'S NUMBERS. Typed once, cited, never re-derived.
# ==========================================================================
D_PCB = 26.00
T_PCB = 0.600
PCB_NOTCH_DEG = 26.0
R_PCB_NOTCH = 12.60
TAB_ANGLES = (0.0, 120.0, 240.0)
D_CELL = 20.00
Z_CELL_TOP = 4.022
Z_DECK_TOP = 4.600
D_LAND = 21.20                 # the bender's bond land -> the 0.400 mm rule
D_SPEAKER_KO = 25.75           # Apple: "DO NOT OBSTRUCT THIS AREA"
D_ANTENNA_KO = 37.31           # Apple: no metal above or below - HOST scope
M_SRC = "ce-designs/halo/design.py (lane M)"

R = D_PCB / 2.0
CX = CY = R                    # the board's frame has its origin at a corner

# Derived height allowances, computed rather than quoted.
H_TOP_INNER = 0.400            # design.py's own keep-out on part:halo-pcb-blank
H_BOT_CELL = round(Z_DECK_TOP - Z_CELL_TOP, 3)          # 0.578

# ==========================================================================
# 2. THE FLOORPLAN, in polar coordinates, because a disc has no corners
# ==========================================================================
R_CELL = D_CELL / 2.0          # 10.0 - nothing below this radius is clear
R_ANNULUS_IN = 10.20           # 0.2 mm margin off the can's edge
R_ANNULUS_OUT = 12.70          # 0.3 mm in from the edge, for the router bit

# The three notches eat 26 deg each at 0/120/240, so the clear arcs are
# 13->107, 133->227 and 253->347. The antenna takes the middle of the first.
ANT_SECTOR_MID = 60.0
ANT_SECTOR_ARC = 88.0          # 16 -> 104 deg, inside the 13->107 clear arc


#: Where the antenna is fed, and where the coil's two halves meet. Both are
#: angles because everything on a disc is.
ANT_FEED_DEG = 20.0

#: Where the NFC winding's two halves meet, computed the same way the spiral
#: is so the net tie lands ON the conductor rather than near it.
# MEASURED WRONG 2026-09-04, AND THE SHAPE OF THE MISTAKE IS WORTH KEEPING.
# This read `20.0 + 360.0 * 3 - 40.0`, a hand-typed copy of a THREE-turn coil
# that was cut to two turns in footprints.py and never copied back. The tie
# was therefore placed at 180 deg and radius 10.3167 while the winding's gap
# is at 380 deg and radius 10.4486: 160 degrees and 20 mm away from the
# conductor it is supposed to join, on a Ø26 mm board. Nothing failed - the
# tie was simply a two-pad island in the middle of the coil, and the coil was
# open. Derived from fpg.NFC_TURNS now, and CHECKED against the spiral's own
# midpoint below, because the defect was not the arithmetic, it was that two
# expressions for one number were allowed to disagree in silence.
_NFC_A0_PRE = 20.0
_NFC_A1_PRE = _NFC_A0_PRE + 360.0 * fpg.NFC_TURNS
NFC_TIE_DEG_PRE = (_NFC_A0_PRE + _NFC_A1_PRE) / 2.0
NFC_TIE_R_PRE = fpg.NFC_R_OUT - (fpg.NFC_W + fpg.NFC_GAP) * \
    (NFC_TIE_DEG_PRE - _NFC_A0_PRE) / 360.0


def at_r(r, deg):
    """Polar placement. `deg` is CCW from +X with +Y up, so 90 is the top."""
    a = math.radians(deg)
    return (CX + r * math.cos(a), CY + r * math.sin(a))


def outline_polygon(segments=360):
    """The Ø26.00 disc with three 26 deg notches cut to R12.60.

    Reproduces `pcb_blank()` in design.py: `_sector(p, R_PCB_NOTCH,
    D_PCB/2+0.5, ..., a, PCB_NOTCH_DEG, op="cut")` — `a` is the sector's
    CENTRE angle and PCB_NOTCH_DEG its total arc, which is the convention
    `battery_contact()` in the same file uses.
    """
    half = PCB_NOTCH_DEG / 2.0
    notches = [(a - half, a + half) for a in TAB_ANGLES]

    def in_notch(deg):
        d = deg % 360.0
        for lo, hi in notches:
            lo %= 360.0
            hi %= 360.0
            if lo <= hi:
                if lo <= d <= hi:
                    return True
            elif d >= lo or d <= hi:          # the notch straddling 0 deg
                return True
        return False

    pts = []
    for i in range(segments):
        deg = 360.0 * i / segments
        rr = R_PCB_NOTCH if in_notch(deg) else R
        pts.append(at_r(rr, deg))
    return pts


#: 360 steps, not 180, and the reason is 1.7 um. A ring drawn as chords sits
#: INSIDE the circle it approximates by r(1-cos(pi/steps)); at 180 steps and
#: r 9.74 that is 0.0015 mm, so a band asked for 0.30 mm was drawn at 0.2983
#: and every report of it would have been a number nobody asked for. At 360 it
#: is 0.0004 mm. The cost is 360 more points in one zone outline.
def annulus_polygon(r_in, r_out, steps=360):
    """A full ring, as one polygon with a bridge so it is simply connected.

    KiCad zones have no holes, so a ring is drawn as an outer circle walked
    forwards and an inner circle walked back, meeting at a seam. The seam is
    zero-width and the fill closes over it.
    """
    pts = [at_r(r_out, 360.0 * i / steps) for i in range(steps + 1)]
    pts += [at_r(r_in, 360.0 - 360.0 * i / steps) for i in range(steps + 1)]
    return pts


def sector_polygon(r_in, r_out, mid_deg, arc_deg, steps=48):
    """An annular sector, for keep-outs and for clearing the antenna's ground."""
    a0, a1 = mid_deg - arc_deg / 2.0, mid_deg + arc_deg / 2.0
    pts = [at_r(r_out, a0 + (a1 - a0) * i / steps) for i in range(steps + 1)]
    pts += [at_r(r_in, a1 - (a1 - a0) * i / steps) for i in range(steps + 1)]
    return pts


# ==========================================================================
# 3. THE BOARD
# ==========================================================================
b = Board("halo_rev_a", outline=outline_polygon(), layers=4,
          title="halo rev A - Ø26.00 mm, 4 layer, nRF54L10 Find My tag")

# 0.127 mm / 0.127 mm is JLCPCB's standard 4-layer process, and this board
# needs all of it: the nRF54L10 is a 0.4 mm pitch QFN-48, so the gap between
# adjacent lands is about 0.20 mm and an escape trace has to pass through it.
# Anything looser than 5 mil cannot leave the part at all.
b.rules(clearance=0.127, track=0.127, min_track=0.127,
        via=0.45, via_drill=0.25, hole_clearance=0.20,
        why="JLCPCB standard 4-layer capability (ce-pcb/data/stackups.json, "
            "jlcpcb-4layer). The nRF54L10-QFAA is a 0.4 mm pitch QFN-48 and "
            "its escape does not exist at a looser clearance. Via 0.45/0.25 "
            "rather than 0.6/0.3 for the same reason: a 0.6 mm via does not "
            "fit between two 0.4 mm pitch lands.")

# -- keep-outs, and they are three DIFFERENT KINDS OF CLAIM ----------------
# 1. The cell. A Ø20 steel can 0.578 mm below the board is not a copper rule
#    — copper under it is fine and the ground plane wants to be there — it is
#    a KEEP-OUT ON PARTS AND ON THE ANTENNA. Recorded on one layer (B.Cu) as
#    a footprint keep-out so KiCad's DRC reports anything mounted into it.
b.keepout(diameter=D_CELL + 0.4, center=(CX, CY), layers=["B.Cu"],
          tracks=False, vias=False, pads=False, pours=False, footprints=False,
          scope="board", name="cell-body-HEIGHT-0.578mm",
          why="DOCUMENTATION, NOT AN ENFORCED RULE, and the distinction is "
              "the point. A Ø20.0 mm CR2032 sits 0.578 mm below this face "
              "(%s: Z_CELL_TOP 4.022, Z_DECK_TOP 4.600). What is forbidden "
              "here is HEIGHT, not presence: a 0201 at 0.33 mm is welcome "
              "and a QFN-48 at 0.85 mm is not. KiCad rule areas have no "
              "height axis, so forbidding footprints outright would fail "
              "every part on the bottom face including the ones that fit - "
              "an alarm that is always on tells you nothing. The real check "
              "is arithmetic and it is in height_check() below, which grades "
              "each part against the allowance at its own radius." % M_SRC)

# 2. The bender. Apple's Ø25.75 "do not obstruct" is acoustic, and lane M
#    turned it into the number that binds: nothing taller than 0.400 mm on
#    the top face inside Ø21.2. Also not a copper rule.
b.keepout(diameter=D_LAND, center=(CX, CY), layers=["F.Cu"],
          tracks=False, vias=False, pads=False, pours=False, footprints=False,
          scope="board", name="bender-diaphragm-HEIGHT-0.400mm",
          why="DOCUMENTATION, same reason as the cell. The Murata 7BB-20-3 "
              "is bonded to the shell's Ø21.2 mm land and needs a 0.680 mm "
              "moving gap, so %s limits top-face parts inside this circle to "
              "0.400 mm. Height again, not presence: 0201 (0.33 mm) passes "
              "and every active on this board does not. Graded in "
              "height_check()." % M_SRC)

# 3. Apple's Ø37.31 "no metal above or below" is LARGER THAN THE PRODUCT, so
#    it cannot mean "no board". It governs whatever the puck is fitted into.
#    scope="host" makes keepout_check() grade it CANNOT DETERMINE with the
#    measurement rather than quietly passing a rule it cannot see.
# FORBIDS NOTHING, deliberately. Created with the default forbids first, and
# because Ø37.31 covers every square millimetre of a Ø26 board, KiCad's DRC
# reported ordinary parts as items_not_allowed inside it - a rule area that
# outlaws the entire board. A host-scope region is a constraint on whatever
# the puck is fitted INTO and this board cannot enforce it, so it is drawn
# and documented and enforces nothing.
b.keepout(diameter=D_ANTENNA_KO, center=(CX, CY), layers="*",
          tracks=False, vias=False, pads=False, pours=False, footprints=False,
          scope="host", name="antenna-host-clearance",
          why="SPEC.md §4, Apple's own callout: no metal above or below, "
              "Ø37.31 mm - 11.44 mm LARGER than this board. Every square "
              "millimetre of halo is inside it, so it is a constraint on the "
              "HOST, and this board cannot grade it.")

# 4. The antenna's own ground clearance. This one IS a copper rule and it is
#    the load-bearing one: an inverted-F needs its counterpoise removed from
#    under the radiating element or it does not radiate.
ANT_CLEAR = sector_polygon(R_ANNULUS_IN - 0.3, R - 0.05,
                           ANT_SECTOR_MID, ANT_SECTOR_ARC + 6.0)
# FORBIDS POURS AND VIAS, NOT TRACKS AND PADS. What the AE1 element
# needs is its COUNTERPOISE removed - the ground and VDD planes, and any via
# stitching them - from under the radiating element. Forbidding tracks and
# pads as well was tried and reported 100 items_not_allowed against the NFC
# winding, which necessarily crosses this sector on its way round the board
# and is 13.56 MHz copper that does not behave as a 2.4 GHz counterpoise.
# WHAT DOES CROSS HERE IS A REAL COUPLING QUESTION AND IT IS ce-rf's: the NFC
# coil on B.Cu and BT1's positive contact land both sit under this sector and
# neither can move. They are in the model, not designed out.
# F.Cu IS IN THIS LIST, and leaving it out was a real bug. The antenna lives
# on F.Cu, so the first version excluded that layer entirely - which meant
# the top-side GND pour filled right up to the element with 0.127 mm of
# clearance on both sides. That is not an antenna beside a ground plane, it
# is a coplanar waveguide, and it would have radiated almost nothing. Pours
# are forbidden on all four layers in this sector; TRACKS are allowed,
# because the element itself is one.
b.keepout(outline=ANT_CLEAR, layers=["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"],
          tracks=False, vias=True, pads=False, pours=True, footprints=False,
          scope="board", name="antenna-ground-clearance",
          why="No ground plane, no inner copper and no bottom copper under "
              "the 2.4 GHz element. An inverted-F over its own ground plane "
              "is a short circuit. F.Cu is deliberately NOT in this list - "
              "the antenna itself lives there.")

# 4c. THE NFC COIL'S OWN CLEARANCE, and it is the bigger of the two.
#     ce-rf refused to solve the 2026-09-05 re-run and its reason was a fact
#     about this board: the closest approach of the coil to the ground shape is
#     0.1492 mm, against a 0.1500 mm mesh cell. The solver cannot separate two
#     conductors closer than one cell and would have merged them into a short,
#     so it answered CANNOT DETERMINE instead of answering wrongly.
#
#     THAT 0.1492 mm WAS NEVER A DECISION. It is the 0.127 mm netclass
#     clearance plus fill rounding - the pour simply filled as close to the
#     coil as the rules let it, and nobody chose the number.
#
#     AND THE COPLANAR GAP IS THE SMALLER PROBLEM. Measured on the shipped
#     board by sampling the coil's own ring every 2 degrees:
#
#         In1.Cu  133 of 180 points -> 74 % of the coil has GROUND PLANE
#         In2.Cu  133 of 180 points -> 74 % has the VDD PLANE
#         F.Cu    101 of 180 points -> 56 %
#         B.Cu      0 of 180 points -> 0 %, the coil's own layer is clear
#
#     A 13.56 MHz loop with a solid plane one dielectric away is loaded by the
#     eddy currents it induces in that plane; clearing the ground under an NFC
#     antenna is the first line of every vendor's antenna note, and it had
#     never been done here. B.Cu being clear is the coil's own fill clearance,
#     not a decision either - it is what made this look fine.
#
#     THE BAND: the coil's copper grown by 0.30 mm, the same working point D26
#     set for coil-to-antenna. Measured before writing it: ZERO of the board's
#     49 vias fall inside it, so nothing is orphaned by the cut.
NFC_CLEAR_GAP = 0.30
_coil_in = fpg.NFC_R_OUT - fpg.NFC_TURNS * (fpg.NFC_W + fpg.NFC_GAP) - fpg.NFC_W / 2.0
_coil_out = fpg.NFC_R_OUT + fpg.NFC_W / 2.0
NFC_CLEAR_R_IN = _coil_in - NFC_CLEAR_GAP
NFC_CLEAR_R_OUT = _coil_out + NFC_CLEAR_GAP
NFC_CLEAR = annulus_polygon(NFC_CLEAR_R_IN, NFC_CLEAR_R_OUT)
b.keepout(outline=NFC_CLEAR, layers=["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"],
          tracks=False, vias=True, pads=False, pours=True, footprints=False,
          scope="board", name="nfc-coil-clearance",
          why="No plane copper and no vias within %.2f mm of the NFC winding, "
              "on any layer. A 13.56 MHz loop with a solid plane one "
              "dielectric away is loaded by the eddy currents it induces in "
              "it; 74%% of this coil's ring had ground on In1 and VDD on In2 "
              "until this existed. TRACKS are allowed because the winding "
              "itself is one, and because the two tie stubs and the coil's "
              "own escape have to cross this band."
              % NFC_CLEAR_GAP)


# 4b. THE ARM'S SHADOW. The rule above allows TRACKS, and it has to: the
#     antenna is itself a track in that sector, and cepcb's keepout() -- like
#     KiCad's rule areas -- has no per-net exception, so "forbid tracks" would
#     forbid the element. That exemption is far too broad, and it is the hole
#     the whole 2026-09-05 antenna defect walked through: NOTHING stopped the
#     NFC coil, a signal net, or the autorouter's output from lying directly
#     under the radiating arm. Measured before this existed: NFC1 overlapping
#     the arm by 0.1747 mm, and after one autoroute XL1 at 0.2630 mm and
#     PIEZO_DRV at 0.3429 mm.
#
#     THE FIX NEEDS NO NET EXCEPTION, because of where the antenna is not.
#     The element lives on F.Cu ALONE. On In1.Cu, In2.Cu and B.Cu the antenna
#     has no copper at all, so a keep-out there can forbid EVERYTHING without
#     forbidding the element -- and those three layers are exactly where the
#     668 MHz comes from, since the coupling that matters is vertical through
#     0.60 mm of laminate, not lateral along F.Cu.
#
#     The band is the arm's own radial extent grown by lane T3's measured
#     0.30 mm floor: they solved the Ø25.2 mm coil at a 0.30 mm gap to
#     2.4321 GHz, in band, and the same coil under the arm to 1.7666 GHz.
ANT_SHADOW_GAP = 0.30          # T3, 2026-09-05: the smallest gap ever solved
_arm_in = fpg.ANT_R - fpg.ANT_TOOTH_DEPTH - fpg.ANT_W / 2.0
_arm_out = fpg.ANT_R + fpg.ANT_W / 2.0
ANT_SHADOW = sector_polygon(_arm_in - ANT_SHADOW_GAP,
                            min(_arm_out + ANT_SHADOW_GAP, R - 0.05),
                            ANT_SECTOR_MID, ANT_SECTOR_ARC + 6.0)
# PADS ARE EXCLUDED, AND THE REASON IS ON THE RECORD RATHER THAN IMPLIED.
# With pads=True this rule's first run reported exactly one hit: BT1.2, the
# cell's negative contact land (GND, B.Cu, 23.046/7.200), sitting directly
# under the arm. That land's position is set by where a CR2032's rim actually
# touches, so it is a mechanical fact and not a routing choice - lane M's and
# lane C's, not this one's. A rule that is permanently red for something
# nobody intends to change is a rule people learn to skip, which is how the
# original keep-out's blanket tracks=False exemption survived. So this
# governs what this lane and the autorouter CAN move - tracks, vias, pours -
# and BT1.2 is carried in docs/VERIFICATION-DEBT.md as RF copper the antenna
# case must model, which is where it actually belongs: ce-rf's own
# halo-rev-a-2g4 has `passive_copper: []` and models neither it nor the coil.
b.keepout(outline=ANT_SHADOW, layers=["In1.Cu", "In2.Cu", "B.Cu"],
          tracks=True, vias=True, pads=False, pours=True, footprints=False,
          scope="board", name="antenna-arm-shadow",
          why="NOTHING under the 2.4 GHz arm on any layer the arm is not on. "
              "R%.4f to R%.4f is the arm's own copper grown by the 0.30 mm "
              "gap lane T3 solved as the working point; the same coil under "
              "the arm moves the resonance 668 MHz and no tuning recovers it. "
              "The element is on F.Cu only, so this forbids everything on the "
              "other three layers and still cannot forbid the element."
              % (_arm_in - ANT_SHADOW_GAP, _arm_out + ANT_SHADOW_GAP))


# ==========================================================================
# 4. PLACEMENT
# ==========================================================================
C0201 = "Capacitor_SMD:C_0201_0603Metric"
R0201 = "Resistor_SMD:R_0201_0603Metric"
L0201 = "Inductor_SMD:L_0201_0603Metric"
TP = "halo:HALO_TP_D0.8"        # ours, not KiCad's - see footprints.py
FID = "Fiducial:Fiducial_0.5mm_Mask1mm"
MARK = "halo:HALO_SERIAL_MARK_1X8"   # the laser-marked serial land

# side: actives BOTTOM, passives TOP. See the height paragraph - the top
# face inside Ø21.2 allows 0.400 mm and every active here is taller, so the
# bottom's 0.578 mm is the better of two faces that are both too shallow.
PLACE = [
    # ref, footprint,                                  r,     deg, rot, side
    ("U1", "Package_DFN_QFN:QFN-48-1EP_6x6mm_P0.4mm_EP4.4x4.4mm",
     0.0, 0.0, 0.0, "bottom"),
    ("U2", "Package_LGA:LGA-12_2x2mm_P0.5mm", 7.6, 262.0, 0.0, "bottom"),
    ("X2", "Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm", 7.4, 330.0, 60.0,
     "bottom"),
    ("X1", "Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm", 7.0, 146.0, 56.0,
     "bottom"),
    ("L1", "Inductor_SMD:L_0603_1608Metric", 7.3, 40.0, 40.0, "bottom"),
    # the CR2032's three lands: its own pads are already at r = 11.6
    ("BT1", "halo:HALO_BATT_CONTACT_3PAD", 0.0, 0.0, 0.0, "bottom"),
    # bulk, 0402, on the bottom where 0.55 mm still fits under 0.578 mm
    ("C9", "Capacitor_SMD:C_0402_1005Metric", 8.5, 352.0, 82.0, "bottom"),
    ("C10", "Capacitor_SMD:C_0402_1005Metric", 8.5, 286.0, 16.0, "bottom"),
    ("C11", "Capacitor_SMD:C_0402_1005Metric", 8.5, 172.0, 82.0, "bottom"),
    ("C12", "Capacitor_SMD:C_0402_1005Metric", 8.5, 235.0, 325.0, "bottom"),
    # Crystal load capacitors, DNP, beside the crystal each one loads. 0201
    # at 0.33 mm clears the bottom face's 0.578 mm with room.
    ("C14", C0201, 8.60, 116.0, 26.0, "bottom"),
    ("C15", C0201, 8.60, 127.0, 37.0, "bottom"),
    ("C16", C0201, 8.60, 311.0, 41.0, "bottom"),
    ("C17", C0201, 8.60, 302.0, 32.0, "bottom"),
    # SWD pads and the UWB stub, top face, out of the bender's circle
    # The Tag-Connect went here first and did not fit - 80 mm2 with two NPTH
    # through the SoC's pads. See footprints.swd_pads().
    ("J1", "halo:HALO_SWD_PADS_1x06_P1.27", 9.60, 312.0, 42.0, "top"),
    ("J2", "halo:HALO_UWB_LANDS_1x08_P1.00", 11.10, 180.0, 90.0, "top"),
    # The three etched "parts". Their footprints are generated by
    # footprints.py from computed geometry, and they are placed with
    # anchor="origin" because their origin IS their feed point - a courtyard
    # centre is meaningless for an 84-degree arc.
    ("AE1", "halo:HALO_ANT_2G4_FEED", fpg.ANT_R, ANT_FEED_DEG, 0.0,
     "top"),
    # KiCad's own net tie, placed where the two halves of the winding
    # meet. See footprints.py for why the coil is not a footprint.
    # +90: the tie's two pads lie on its local x axis, so rotating it to the
    # spiral's TANGENT puts them along the conductor. Rotated to the radius
    # instead they sit 0.5 mm off it on either side and the stubs that close
    # the winding have to jump the gap sideways.
    ("AE2", "halo:HALO_NFC_TIE_2", NFC_TIE_R_PRE,
     NFC_TIE_DEG_PRE, NFC_TIE_DEG_PRE + 90.0, "bottom"),
    ("LS1", "halo:HALO_PIEZO_LEADS_2", 10.30, 118.0, 28.0, "top"),
]

#: Parts whose footprint origin is the feature, not the centre of a body.
ANCHOR_ORIGIN = {"BT1"}

# ---------------------------------------------------------------------------
# THE 0201 PASSIVES, LAID OUT ON STREETS
# ---------------------------------------------------------------------------
# Hand-tuned polar coordinates were tried first and the DRC found 70 shorting
# pads: a C_0201_0603Metric is 1.09 mm across its two lands, so two of them
# 1.17 mm apart on the same arc OVERLAP, and by eye they look nicely spaced.
# A number nobody computed is a number nobody checked.
#
# So the passives are placed on radial STREETS instead. Each street is an
# angle; parts step outward along it by a fixed PITCH that is larger than the
# longest 0201 land pattern plus a courtyard. Streets that share a radius
# band are kept far enough apart in angle that their arc separation at the
# INNERMOST shared radius still clears - which is the case that bites,
# because arc length shrinks with radius and the eye does not notice.
STREET_PITCH = 1.60        # mm between parts along a street. A 0201 land
                           # pattern is 1.09 mm end to end and its courtyard
                           # is 1.29 mm; 1.60 leaves 0.31 mm of air.
                           # MIN_ARC_SEP was 1.40 first and the DRC still
                           # found two pairs at 0.1209 mm against a 0.127 mm
                           # rule - a courtyard is not a clearance, and 1.58
                           # is what actually clears.
MIN_ARC_SEP = 1.58         # mm between neighbouring streets, at the smallest
                           # radius they both occupy

#: (angle, first radius, [(ref, footprint), ...]). The order along a street
#: is the order of the signal, not alphabetical - the RF ladder runs outward
#: from the SoC pin to the antenna feed, which is also how the current goes.
STREETS = [
    # -- the RF ladder. Series parts on one street, shunts on the next, so
    #    every shunt sits beside the node it shunts.
    (62.0, 4.70, [("L2", L0201), ("L3", L0201), ("L4", L0201),
                  ("L10", L0201)]),
    (84.0, 4.70, [("C23", C0201), ("C18", C0201), ("C19", C0201),
                  ("C22", C0201)]),
    (104.0, 6.30, [("C20", C0201), ("C21", C0201)]),
    # -- decoupling, one per VDD pin, around the SoC
    (20.0, 4.70, [("C4", C0201), ("C9x", None)][:1]),
    (130.0, 4.70, [("C1", C0201)]),
    (200.0, 4.70, [("C2", C0201)]),
    (310.0, 4.70, [("C3", C0201)]),
    # -- the DC/DC node, beside L1 at 40 deg on the bottom
    (40.0, 4.70, [("C5", C0201), ("C6", C0201), ("C7", C0201)]),
    (330.0, 4.70, [("C8", C0201)]),
    # -- NFC tuning, at pins 3/4
    (150.0, 4.70, [("C24", C0201), ("C25", C0201)]),
    # -- the crystal load caps are NOT on a street. They belong beside
    #    their crystals, which are on the BOTTOM face, and every top-side
    #    ray that was near enough to be useful was already 10 degrees from
    #    another street - C25/C14 and C16/R8 both came out at 1.111 mm.
    #    They are in PLACE instead, on the bottom, next to X1 and X2.
    # -- the accelerometer's straps and its bus pull-ups
    (255.0, 4.70, [("R5", R0201), ("R6", R0201)]),
    (275.0, 4.70, [("R7", R0201), ("R8", R0201)]),
    # -- cell-removal sense
    (215.0, 7.90, [("R1", R0201), ("R2", R0201), ("C13", C0201)]),
    # -- piezo damping and the reset pull-up
    (118.0, 7.90, [("R9", R0201)]),
    (345.0, 6.30, [("R10", R0201)]),
]

SMALL = []
for ang, r0, items in STREETS:
    for k, (ref, fp) in enumerate(items):
        if fp is None:
            continue
        SMALL.append((ref, fp, r0 + k * STREET_PITCH, ang, ang - 90.0, "top"))


def check_street_separation():
    """Refuse a layout whose parts cannot clear, BEFORE placing anything.

    ALL PAIRS, not neighbouring streets. The first version of this compared
    only streets whose radius BANDS overlapped, and two streets whose bands
    merely ABUT slipped through it: C25 ended a street at r=6.30 on the 150
    degree ray and C14 began one at r=6.40 on the 160 degree ray, 1.15 mm
    apart, and the DRC found them at 0.1209 mm against a 0.127 mm rule. A
    check with a blind spot is worse than no check, because it is trusted.

    So this measures the distance between every pair of placed passives. It
    is 34 parts and about 560 comparisons; it costs nothing and it has no
    blind spot.
    """
    pts = []
    for ang, r0, items in STREETS:
        k = 0
        for ref, fp in items:
            if fp is None:
                continue
            r = r0 + k * STREET_PITCH
            a = math.radians(ang)
            pts.append((ref, r * math.cos(a), r * math.sin(a)))
            k += 1
    bad = []
    for i2 in range(len(pts)):
        for j2 in range(i2 + 1, len(pts)):
            r1, x1, y1 = pts[i2]
            r2, x2, y2 = pts[j2]
            d = math.hypot(x1 - x2, y1 - y2)
            if d < MIN_ARC_SEP:
                bad.append((r1, r2, d))
    return sorted(bad, key=lambda t: t[2])


_bad = check_street_separation()
if _bad:
    raise SystemExit(
        "REFUSED: %d part pairs are closer than %.2f mm centre to centre, "
        "which is how 0201 land patterns end up overlapping:\n%s"
        % (len(_bad), MIN_ARC_SEP,
           "\n".join("  %-5s and %-5s are %.3f mm apart"
                      % (r1, r2, d) for r1, r2, d in _bad)))

placed, skipped = [], []
for ref, fpid, r, deg, rot, side in PLACE + SMALL:
    x, y = at_r(r, deg)
    b.place(ref, fpid, at=(x, y), rot=rot, side=side,
            anchor="origin" if ref in ANCHOR_ORIGIN else "center")
    placed.append(ref)


# ---------------------------------------------------------------------------
# THE QFN'S LANDS ARE WIDENED TO THE FAB'S OWN MINIMUM, AND THE TWO NUMBERS
# THAT DECIDE IT ARE THE FAB'S, NOT A PREFERENCE
# ---------------------------------------------------------------------------
# `fab dfm` FAILED `smd_pad_min` at 0.2000 mm against JLCPCB's published
# "Minimum SMD pad: 0.25mm x 0.25mm". The 0.20 mm is not ours either: KiCad's
# `QFN-48-1EP_6x6mm_P0.4mm_EP4.4x4.4mm` is IPC-nominal from ST's STM32WB06
# land pattern, and it puts 48 lands at 0.20 x 0.85.
#
# READ THE FAB'S TWO LINES TOGETHER AND THE ANSWER IS FORCED (both from the
# Traces table, https://jlcpcb.com/capabilities/pcb-capabilities, re-read
# 2026-09-05):
#
#   "Minimum SMD pad: 0.25mm x 0.25mm"
#   "SMD pad to pad clearance (different nets) 0.15mm"
#
# On a 0.40 mm pitch those two meet EXACTLY at a 0.25 mm land: 0.40 - 0.25 =
# 0.15. So 0.25 is not a number nudged until the check went green, it is the
# only width on this pitch that satisfies both published lines at once, and
# the fab's own assembly page names 0.40 mm as its minimum IC pin spacing on
# the cheaper service. The resulting 0.15 mm mask dam clears their soldermask
# bridge minimum of 0.10 mm as well.
#
# The LENGTH is untouched at 0.85 mm — this widens the land toward its
# neighbours, which is where the fab's clearance line governs, and does not
# change the toe or heel the joint is inspected on.
import pcbnew as _pcbnew                                          # noqa: E402

QFN_LAND_MIN = 0.25
QFN_LANDS_WIDENED = []
for _pad in b.refs["U1"].Pads():
    _w, _h = _pad.GetSizeX() / 1e6, _pad.GetSizeY() / 1e6
    if not _pad.GetNumber() or min(_w, _h) >= QFN_LAND_MIN:
        continue
    _nw = max(_w, QFN_LAND_MIN) if _w < _h else _w
    _nh = max(_h, QFN_LAND_MIN) if _h < _w else _h
    _pad.SetSize(_pcbnew.VECTOR2I(int(round(_nw * 1e6)), int(round(_nh * 1e6))))
    QFN_LANDS_WIDENED.append((_pad.GetNumber(), _w, _h, _nw, _nh))
if len(QFN_LANDS_WIDENED) != 48:
    raise SystemExit(
        "expected to widen 48 QFN lands and widened %d. Either the footprint "
        "changed under this code or it was already wide, and either way a "
        "silent 0 here would leave the board failing smd_pad_min with a line "
        "in the file that says it does not."
        % len(QFN_LANDS_WIDENED))

# ---------------------------------------------------------------------------
# TEST ACCESS, PLACED BY SEARCH RATHER THAN BY HAND
# ---------------------------------------------------------------------------
# Eleven probe pads, two fiducials and a serial-mark land had to go onto a
# board that was already full, and placing them by hand produced a new set of
# courtyard overlaps on every attempt - eight, then eleven, each one a
# different pair. Hand-placing into a crowded board is guesswork with a
# feedback loop, and the loop was the DRC, which is expensive and late.
#
# So they are placed by SEARCH. Every part already on the board contributes
# its real courtyard radius; each test pad starts from a preferred angle -
# near the net it probes, because that is what makes the fixture short - and
# spirals outward through (radius, angle) until it finds a spot that clears
# everything placed so far by CLEAR_MM. First fit wins, the order is fixed,
# so the result is deterministic and re-running this file reproduces it
# exactly. A pad that cannot be placed is REPORTED, not dropped.
CLEAR_MM = 0.25            # edge-to-edge air between courtyards


def _extent(ref):
    """The radius of the smallest circle that covers this part's courtyard."""
    fp = b.refs[ref]
    bb = fp.GetBoundingBox(False, False)
    return math.hypot(bb.GetWidth(), bb.GetHeight()) / 2e6


def _centre(ref):
    fp = b.refs[ref]
    p = fp.GetPosition()
    return p.x / 1e6, 26.0 - p.y / 1e6


def auto_place(items, r_lo=3.4, r_hi=11.4, dr=0.2, dtheta=3.0):
    """Place each (ref, fpid, radius_of_this_part, preferred_deg) by search."""
    taken = [(_centre(r)[0], _centre(r)[1], _extent(r))
             for r in b.refs if not b.refs[r].IsFlipped()]
    placed_here, failed = [], []
    for item in items:
        ref, fpid, rad, pref_deg = item[:4]
        # An optional per-item radius band. The fiducials use it: a pair at
        # the same radius maps onto itself under rotation and therefore
        # fixes position but NOT rotation, which is most of what a fiducial
        # is for. The search found them 0.20 mm apart on its own and the
        # asymmetry check refused that, so the bands are stated here.
        lo = item[4] if len(item) > 4 else r_lo
        hi = item[5] if len(item) > 5 else r_hi
        best = None
        # spiral: try the preferred angle first, then walk away from it in
        # both directions, at each radius from the inside out
        for rr in [lo + dr * k for k in range(int((hi - lo) / dr) + 1)]:
            for off in [0.0] + [s2 * dtheta * k
                                for k in range(1, int(180 / dtheta) + 1)
                                for s2 in (1, -1)]:
                deg = (pref_deg + off) % 360.0
                x, y = at_r(rr, deg)
                if math.hypot(x - CX, y - CY) + rad > R - 0.6:
                    continue
                if all(math.hypot(x - tx, y - ty) > (rad + tr + CLEAR_MM)
                       for tx, ty, tr in taken):
                    best = (deg, rr, x, y)
                    break
            if best:
                break
        if not best:
            failed.append(ref)
            continue
        deg, rr, x, y = best
        b.place(ref, fpid, at=(x, y), rot=0.0, side="top")
        taken.append((x, y, rad))
        placed_here.append((ref, rr, deg))
    return placed_here, failed


#: (ref, footprint, its own courtyard radius, the angle it would prefer).
#: THE RADII ARE MEASURED FROM THE LAND PATTERNS, not guessed. They were
#: declared as 0.80 and 1.10 first and the DRC found three courtyard
#: overlaps among the test points themselves: TestPoint_Pad_D1.0mm has a
#: 2.05 x 2.05 mm courtyard, so its circumradius is 1.45 mm, and
#: Fiducial_1mm_Mask2mm's is 1.80 mm. A placer fed the wrong size places
#: confidently and wrongly.
#:
#: AT THOSE SIZES FIVE OF THE THIRTEEN DID NOT FIT, and the placer said so
#: rather than dropping them. The fix is a fixture sized for the product:
#: halo's own HALO_TP_D0.8 (0.78 mm circumradius, a 0.80 mm land for a
#: 0.5 mm pogo tip) and Fiducial_0.5mm_Mask1mm (0.95 mm). A 26 mm board
#: gets a 26 mm fixture; it does not get fewer tests.
#: The preferred angle is where the net it probes already lives, so the
#: fixture's wiring is short; the search moves it only as far as it must.
TEST_ACCESS = [
    # THE FIDUCIALS GO FIRST, and the order is the point. This is a first-fit
    # placer, so whatever is placed earliest gets the widest choice. The
    # fiducials are the MOST constrained items on the list - each is banded
    # to a radius range, and the pair has to come out asymmetric - while a
    # probe pad only wants to be somewhere near its net. Placing eleven
    # flexible things first left the two rigid ones with nowhere to go, and
    # the placer refused FID2 rather than fudging it. Datums first.
    ("FID1", FID, 1.10, 250.0, 9.6, 11.4),
    ("FID2", FID, 1.10, 196.0, 3.4, 7.2),
    ("TP1", TP, 0.78, 20.0),     # VDD force
    ("TP2", TP, 0.78, 340.0),    # VDD sense
    ("TP3", TP, 0.78, 200.0),    # GND force
    ("TP4", TP, 0.78, 160.0),    # GND sense
    ("TP5", TP, 0.78, 108.0),    # PIEZO_P, near LS1
    ("TP6", TP, 0.78, 126.0),    # PIEZO_N, near LS1
    ("TP7", TP, 0.78, 224.0),    # VBAT_SNS, near R1/R2
    ("TP8", TP, 0.78, 268.0),    # I2C_SDA
    ("TP9", TP, 0.78, 282.0),    # I2C_SCL
    ("TP10", TP, 0.78, 152.0),   # NFC1
    ("TP11", TP, 0.78, 138.0),   # NFC2
    # The serial mark goes LAST because it is the largest and the placer is
    # first-fit: ask for the 1.41 mm circumradius before the 0.78 mm ones and
    # it takes the only hole three probe pads could have shared.
    ("M1", MARK, 1.415, 300.0),  # serial DataMatrix, probed face
]

_tp_placed, _tp_failed = auto_place(TEST_ACCESS)

# AE1, AE2 and LS1 have no footprint ON PURPOSE — etched copper and a bonded
# bender are not catalogue land patterns, and the schematic says so. Their
# copper is drawn below; their pads are real pads on real nets.


# ==========================================================================
# 5. THE NETLIST, READ BACK FROM THE SCHEMATIC. Never retyped.
# ==========================================================================
nets = netlist_of_sch(SCH)
on_board = set(b.refs)
bound, deferred = 0, {}
for name, pins in sorted(nets.items()):
    have = sorted(p for p in pins if p.split(".")[0] in on_board)
    missing = sorted(p for p in pins if p.split(".")[0] not in on_board)
    if missing:
        deferred[name] = missing
    if have:
        b.net(name, *have)
        bound += 1

# EXPOSED PADS. The schematic cannot decide these: a symbol pin does not
# exist for U3's thermal pad, and the pcb-design skill's rule 3 is blunt
# about the consequence - "a DFN/QFN EP left on no net sits ~0.175 mm from
# each signal pad and fails clearance against all of them. It is thermal AND
# electrical." U1's pad 49 already has a net because the nRF54L datasheet
# gives it one (VSS_PAD, and Nordic requires it tied to pins 32 and 44).
# U3's does not, so the decision is made HERE, where the copper is, and it
# is GND per the GD25LQ32E datasheet's own land-pattern note.
# (U3's exposed pad was bonded here when the flash existed. The flash is
# deleted - schematic block 6 - so there is nothing left to bond.)


# M1's land is copper on the top face and the top face is poured GND. Left on
# no net it is a 3.2 mm2 isolated island - which the filler reports, correctly,
# as isolated copper, and which is an antenna nobody designed.
if "M1" in b.refs:
    b.net("GND", "M1.1")


# ==========================================================================
# 6. THE ANTENNAS — copper this file draws, because nobody sells the shape
# ==========================================================================
# A quarter wave in FR4's effective medium. eps_eff for a trace on the
# SURFACE of a 4-layer board with its reference plane cleared away is close
# to the air/substrate average and NOT eps_r = 4.3; 2.2 is used, which is the
# usual figure for a coplanar-ish surface trace with no plane beneath.
# THIS IS A STARTING LENGTH, NOT A TUNED ONE — ce-rf owns the tuning, and
# every case it has run so far resonated in the wrong place, which is the
# whole reason this is flagged rather than trusted.
C0 = 299792458.0
F0 = 2.44e9
EPS_EFF = 2.2
LAMBDA_MM = (C0 / F0) * 1000.0 / math.sqrt(EPS_EFF)
QUARTER_MM = LAMBDA_MM / 4.0                       # ~20.7 mm

ANT_R = 12.10                  # the element's radius, mid-annulus
ANT_W = 0.60                   # trace width
FEED_DEG = ANT_SECTOR_MID - ANT_SECTOR_ARC / 2.0 + 2.0    # 25 deg
# An arc of `QUARTER_MM` at radius ANT_R subtends this many degrees:
ANT_ARC_DEG = math.degrees(QUARTER_MM / ANT_R)
ANT_ARC_DEG_FIT = min(ANT_ARC_DEG, ANT_SECTOR_ARC - 6.0)


def arc_track(net, r, a0, a1, width, layer, steps=40):
    """An arc as a chain of track segments, for anything that is not a part."""
    pts = [at_r(r, a0 + (a1 - a0) * i / steps) for i in range(steps + 1)]
    return b.track(net, pts, width=width, layer=layer)


# ==========================================================================
# 6b. THE ETCHED COPPER, AS TRACKS
# ==========================================================================
# Tracks, not footprint copper. footprints.py records the two constructs that
# failed first and KiCad's own words for why the second of them is refused:
# "custom pad shape must resolve to a single polygon". A track is arbitrary
# in shape, carries a net, plots as copper and is understood by the DRC.

# -- AE1: a meandered element, topology UNRESOLVED (see note below) -----------------------------
# The waypoints come from footprints.element_path(), whose tooth depth is
# SOLVED so the conductor is exactly a quarter wave at the eps_eff openEMS
# measured on this board (1.573, not the textbook 2.2). One path, drawn here
# as tracks and in make_rf_specs.py as a staircase.
ANT_PATH = fpg.element_path()
ANT_LEN_MM = fpg.path_length_mm(ANT_PATH)
_prev = None
for _r, _a in ANT_PATH:
    _pt = at_r(_r, ANT_FEED_DEG + _a)
    if _prev is not None:
        b.track("ANT_FEED", [_prev, _pt], width=fpg.ANT_W, layer="F.Cu")
    _prev = _pt

# -- AE2: the NFC winding, one half on each net ---------------------------
# A TRUE ARCHIMEDEAN SPIRAL, not three concentric arcs joined by radial
# jumps. The jumps were drawn first and each one cut across the gap between
# turns at a steep angle, which put 0.44 mm of NFC2 through U3's chip-select
# land and 0.50 mm of NFC1 through the net tie's own second pad. A spiral has
# no crossovers to collide with, and it is also what a coil actually is.
# EXACTLY fpg.NFC_TURNS full turns. The first version subtracted 40 degrees
# from the total sweep and then divided the pitch by 360, which quietly made
# 3 "turns" 2.89 turns and put the innermost winding at R9.88 instead of
# R10.15 - through the crystal load capacitors and U3's chip select, 17
# clearance violations that read as a placement problem and were an
# arithmetic one.
NFC_A0 = 20.0
NFC_A1 = NFC_A0 + 360.0 * fpg.NFC_TURNS
NFC_PITCH = fpg.NFC_W + fpg.NFC_GAP


# HOW MANY SEGMENTS, AND WHY IT IS NOT 600. The spiral was drawn with 600
# chords, which is 583 track segments once the tie gap is cut out - 97 % of
# every piece of copper on this board and 583 of the 600 obstacle edges the
# autorouter has to reason about. That is the difference between this board
# and the Ø31.87 mm puck the same jar routes in 96 s. The count is now
# DERIVED FROM A CHORD-ERROR BUDGET instead of typed: a chord across angle
# dtheta at radius r sits r*(1-cos(dtheta/2)) inside the true arc, and 5 um
# is a twentieth of the 0.10 mm the fab can hold anyway.
NFC_CHORD_ERR_MM = 0.005
_dtheta = 2.0 * math.degrees(math.acos(1.0 - NFC_CHORD_ERR_MM / fpg.NFC_R_OUT))
# EVEN, so that `_sp[len(_sp)//2]` is the exact midpoint of the sweep and the
# net tie placed from the closed-form midpoint lands on it. With an odd count
# the two expressions disagree by half a chord - 0.317 mm, measured, which is
# most of a 0.5 mm pad.
NFC_SEGS = 2 * int(math.ceil((NFC_A1 - NFC_A0) / _dtheta / 2.0))


def _spiral_pts(n=None):
    n = NFC_SEGS if n is None else n
    out = []
    for k in range(n + 1):
        f = k / float(n)
        a = NFC_A0 + (NFC_A1 - NFC_A0) * f
        r = fpg.NFC_R_OUT - NFC_PITCH * (a - NFC_A0) / 360.0
        out.append((r, a))
    return out


_sp = _spiral_pts()
# MEASURED, NOT ASSUMED: the polyline actually drawn is shorter than the
# spiral it approximates, and the coil's inductance goes with its length. If
# this ever exceeds the budget the number above is wrong, not the geometry.
_true_len = 0.0
for _k in range(len(_sp) - 1):
    (_r0, _a0), (_r1, _a1) = _sp[_k], _sp[_k + 1]
    _true_len += math.hypot(_r1 - _r0,
                            math.radians(_a1 - _a0) * 0.5 * (_r0 + _r1))
_chord_len = sum(math.dist(at_r(*_sp[_k]), at_r(*_sp[_k + 1]))
                 for _k in range(len(_sp) - 1))
NFC_LEN_ERR_PCT = 100.0 * (_true_len - _chord_len) / _true_len
_mid = len(_sp) // 2
# A gap of GAP_PTS points at the midpoint is where the net tie sits: the
# winding is one conductor, and the tie is how a two-net conductor is
# declared to KiCad rather than hidden from it.
# THE GAP IS A LENGTH, NOT A POINT COUNT. `GAP_PTS = 8` was written when the
# spiral had 600 chords; at 207 it is 5.07 mm of missing copper in a
# conductor that has to be continuous, and a coil with a 5 mm hole in it is
# not a coil. The tie's two pads sit 1.0 mm apart, so the gap is sized from
# that and the stubs below actually close it.
NFC_GAP_MM = 0.70   # the tie is 0.60 mm long end to end
_arc_per_seg = math.radians((NFC_A1 - NFC_A0) / NFC_SEGS) * fpg.NFC_R_OUT
GAP_PTS = max(1, int(round(NFC_GAP_MM / (2.0 * _arc_per_seg))))
NFC_TIE_R, NFC_TIE_DEG_ACTUAL = _sp[_mid]
# THE TWO EXPRESSIONS FOR ONE NUMBER, MADE TO AGREE OUT LOUD. See the note on
# _NFC_A1_PRE: this is the check that would have caught a tie 20 mm from its
# own conductor the first time, instead of a coil that was open on the board
# and closed in every report.
_tie_err = math.hypot(NFC_TIE_R - NFC_TIE_R_PRE,
                      math.radians(NFC_TIE_DEG_ACTUAL - NFC_TIE_DEG_PRE)
                      * NFC_TIE_R)
if _tie_err > 0.05:
    raise SystemExit(
        "the net tie is placed at r=%.4f deg=%.2f and the winding's gap is at "
        "r=%.4f deg=%.2f - %.3f mm apart. One of the two spiral definitions "
        "is stale." % (NFC_TIE_R_PRE, NFC_TIE_DEG_PRE, NFC_TIE_R,
                       NFC_TIE_DEG_ACTUAL, _tie_err))

_nfc1_pts = [at_r(r, a) for r, a in _sp[:_mid - GAP_PTS + 1]]
_nfc2_pts = [at_r(r, a) for r, a in _sp[_mid + GAP_PTS:]]
b.track("NFC1", _nfc1_pts, width=fpg.NFC_W, layer="B.Cu")
b.track("NFC2", _nfc2_pts, width=fpg.NFC_W, layer="B.Cu")

# -- and CLOSE the gap onto the tie's own pads ----------------------------
# Measured 2026-09-04: the winding was drawn with a hole in it and nothing
# reached the tie, so the "net tie" tied nothing and both coil halves ended
# in mid-air. The stubs are drawn to the pads that are actually there, read
# off the placed footprint rather than recomputed from the placement angle -
# NetTie-2_SMD_Pad0.5mm puts its pads on its local x axis and the part is
# rotated to the spiral's tangent, so re-deriving them is one sign error
# away from a coil that is open on the board and closed in the report.
def _pad_xy(ref, num):
    for pad in b.refs[ref].Pads():
        if pad.GetNumber() == str(num):
            pos = pad.GetPosition()
            return (pos.x / 1e6, 26.0 - pos.y / 1e6)
    raise SystemExit("no pad %s on %s" % (num, ref))


# EACH END TO ITS NEAREST PAD, NOT TO A PAD NUMBER. Assigning NFC1 to pad 1
# and NFC2 to pad 2 crossed the two stubs over each other - each one ran past
# the OTHER net's pad at 0.043 mm and 0.068 mm against a 0.127 mm rule, four
# clearance violations that read as a spacing problem and were a topology
# one. Which pad is which is decided by geometry here, and the assignment is
# printed so the swap is visible rather than assumed.
NFC_TIE_STUBS = []
_tie_pads = {1: _pad_xy("AE2", 1), 2: _pad_xy("AE2", 2)}
_e1, _e2 = _nfc1_pts[-1], _nfc2_pts[0]


def _crosses(a, b, c, d):
    """Do segments ab and cd intersect? Orientation test, no tolerance."""
    def o(p, q, r):
        return ((q[1] - p[1]) * (r[0] - q[0])
                - (q[0] - p[0]) * (r[1] - q[1]))
    return (o(a, b, c) * o(a, b, d) < 0) and (o(c, d, a) * o(c, d, b) < 0)


# THE PAD NUMBERS ARE NOT INTERCHANGEABLE, AND ASSIGNING BY DISTANCE SHORTED
# THE COIL. AE2 pad 1 is on NFC1 and pad 2 on NFC2 — the schematic says so and
# the net tie is the whole reason those are two nets. A "nearest pad" rule
# therefore ran NFC2's stub onto NFC1's pad, and KiCad reported it exactly:
# "Items shorting two nets (nets NFC1 and NFC2)", twice. What is free to
# change is not which pad each half goes to, it is WHICH WAY ROUND THE TIE
# SITS — so the part is turned, not the netlist.
#
# AND THE TURN IS SEARCHED, NOT DERIVED. The tie is placed at an angle on a
# disc, rotated to the winding's tangent, and FLIPPED to the bottom face:
# three sign conventions, and getting any one of them wrong puts the pad axis
# across the gap instead of along it. `NFC_TIE_DEG_PRE + 90` looked right and
# produced a pad axis at +50.9 deg against a gap running at +129.0 deg — the
# mirror, exactly. So the orientation is swept in 2 deg steps and the one that
# actually minimises pad-1-to-NFC1-end plus pad-2-to-NFC2-end is kept, read
# back off the placed footprint each time. A measurement beats a convention.
_fp_ae2 = b.refs["AE2"]
_o0 = _fp_ae2.GetOrientationDegrees()
_best_tie = None
for _k in range(180):
    _fp_ae2.SetOrientationDegrees(_o0 + _k * 2.0)
    _pp = {1: _pad_xy("AE2", 1), 2: _pad_xy("AE2", 2)}
    _cost = math.dist(_e1, _pp[1]) + math.dist(_e2, _pp[2])
    if _best_tie is None or _cost < _best_tie[0]:
        _best_tie = (_cost, _o0 + _k * 2.0, _pp)
NFC_TIE_ROT = _best_tie[1] % 360.0
_fp_ae2.SetOrientationDegrees(_best_tie[1])
_tie_pads = _best_tie[2]


def _crosses(a, b_, c, d):
    """Do segments ab and cd intersect? Orientation test, no tolerance."""
    def o(p, q, r):
        return ((q[1] - p[1]) * (r[0] - q[0])
                - (q[0] - p[0]) * (r[1] - q[1]))
    return (o(a, b_, c) * o(a, b_, d) < 0) and (o(c, d, a) * o(c, d, b_) < 0)


if _crosses(_e1, _tie_pads[1], _e2, _tie_pads[2]):
    raise SystemExit("the two tie stubs cross at every orientation - the net "
                     "tie is not aligned with the winding's gap")
_assign = (("NFC1", _e1, 1), ("NFC2", _e2, 2))
for _net, _end, _padnum in _assign:
    _pxy = _tie_pads[_padnum]
    b.track(_net, [_end, _pxy], width=fpg.NFC_W, layer="B.Cu")
    NFC_TIE_STUBS.append(("%s->pad%d" % (_net, _padnum),
                          round(math.dist(_end, _pxy), 4)))

# WHICH COIL COPPER IS WHICH, FOR THE Specctra EXPORT. KiCad merges NFC1 into
# NFC2 the moment a net tie joins them - correctly, because a coil IS a DC
# short between its own terminals - and the .kicad_pcb that comes out labels
# every one of the winding's segments NFC2 while the PADS keep their own
# nets. Handed that, freerouting sees one net with six pins and joins them by
# the shortest path it can find, which is a 2 mm trace straight across the
# feed: the coil is bypassed, the board is DRC-clean, and there is no NFC
# antenna. The winding is a spiral, so RADIUS separates the two halves
# exactly, and this is the number that does it.
NFC_SPLIT_R = 0.5 * (math.hypot(_nfc1_pts[-1][0] - CX, _nfc1_pts[-1][1] - CY)
                     + math.hypot(_nfc2_pts[0][0] - CX, _nfc2_pts[0][1] - CY))

# ==========================================================================
# 6c. VIAS — because a plane nobody stitched is not a plane
# ==========================================================================
# THIS IS WHY THE ROUTER COULD NOT FINISH. The Specctra export hands
# freerouting every net including GND (39 pins) and VDD (24 pins), and
# freerouting does not know those are poured planes - it sees 63 pin-to-pin
# connections to route as traces, on a Ø26 mm disc, and thrashes. Three runs
# timed out at 900, 3300 and 2400 seconds.
#
# They are not connections a router should make. A GND pad on F.Cu is already
# joined to the F.Cu pour by the fill; what is missing is the copper tying
# F.Cu's pour to In1's plane to B.Cu's pour. That is a via, and it is the
# designer's job, not the router's. VDD is worse: the top-side pour is GND,
# so every VDD pad on F.Cu is an island until a via reaches In2.
#
# So the planes are stitched HERE, before the DSN is written, and GND and VDD
# come out of the routing problem entirely. It also kills the isolated_copper
# violations, which were the same fact wearing a different name: an inner
# plane with no via reaching it is copper connected to nothing.
import pcbnew as _pcbnew                                          # noqa: E402

VIA_D, VIA_DRILL = 0.45, 0.25

#: What the stitch actually covered, per net. Filled by `stitch()`.
STITCH_REPORT = {}

#: Nets this file draws itself and the autorouter must not touch. GND and VDD
#: are poured and stitched below; NFC1/NFC2 are the winding, which a router
#: would short out; the RF chain is a matching network whose element ORDER is
#: the circuit. `dsnfix.py` removes exactly these from the Specctra network.
HAND_ROUTED = {"GND", "VDD", "NFC1", "NFC2"}

#: Pins NO ROUTER CAN REACH ON THIS REVISION, with the reason, so freerouting
#: is not sent to look for a path that does not exist. This is NOT a way to
#: make a check green: the pin stays on the net, KiCad's DRC still counts it
#: unconnected, and the release gate still fails on it. It only stops the
#: autorouter spending passes on an impossible net and reporting a flat score.
ROUTER_SKIP_PINS = {
    "BT1-2": "the cell's negative contact sits at r 11.600 theta 30.0, "
             "directly under the antenna element (theta 20..104, "
             "r 11.192..12.200). antenna-arm-shadow forbids B.Cu tracks over "
             "r 10.892..12.500 there and antenna-ground-clearance forbids a "
             "via anywhere in the sector on all four layers, so every escape "
             "from that pad is closed by an RF rule. The fix is mechanical "
             "(rotate BT1's three contacts onto 0/120/240 +/- 7 deg, the only "
             "family with no contact in the sector) and belongs to lane M. "
             "DECISIONS.md D28.",
}


def _obstacles():
    """Everything a via must not land on, EACH ONE CARRYING ITS NET.

    PADS AND TRACKS. The first version knew only about pads, so the widened
    search happily dropped vias on top of the antenna element and the NFC
    winding: 32 clearance, 20 hole-clearance and 11 hole-to-hole violations
    appeared the moment the search got good enough to find those spaces. An
    obstacle model that omits a class of obstacle does not prevent
    collisions, it just moves them somewhere the search likes better.

    THE NET IS THE FOURTH FIELD, AND ITS ABSENCE WAS A MEASURED DEFECT.
    Without it every obstacle was foreign, INCLUDING THE PAD THE VIA WAS
    BEING PLACED FOR. A VDD pad's own copper is 0.21 mm across; the stub
    check skipped only the first 0.35 mm of its own path while the pad's own
    obstacle disc reached 0.45 mm, so every single pad-origin candidate
    collided with the pad it started on. Effect, measured on 2026-09-04:
    ZERO fanout vias placed and ZERO stubs drawn on either plane net. The 35
    vias that did land all came from the rings, where `origin is None` skips
    the stub check entirely - so 13 VDD vias sat on the In2 plane joined to
    nothing, KiCad reported 13 dangling vias and 24 unconnected VDD pads,
    and the board looked like a routing problem. It was an arithmetic one,
    in the obstacle model, and it is the reason clearance is a rule BETWEEN
    NETS rather than a rule about distance.
    """
    out = []
    for ref, fp in b.refs.items():
        for pad in fp.Pads():
            pos = pad.GetPosition()
            sz = pad.GetSize()
            # A PAD IS A CAPSULE, NOT A DISC, AND THE DIFFERENCE IS A QFN-48.
            # This used hypot(w, h)/2 - the pad's DIAGONAL - as one radius, so
            # a 0.25 x 0.60 mm QFN land became a disc 0.65 mm across and its
            # neighbour 0.40 mm away was permanently inside it. Every escape
            # from every fine-pitch pin was refused for a collision with
            # copper that is not there: 16 of 24 VDD pads unreachable, and the
            # number did not move when the clearance rule was corrected,
            # because the clearance was never what was wrong. Sampled as discs
            # of radius min(w,h)/2 along the long axis, which is what a
            # rounded rectangle actually is.
            # KiCad's OWN BOUNDING BOX, not a rotation this file works out
            # for itself. `GetOrientationDegrees()` is the pad's angle in
            # KiCad's frame, this file works in a Y-flipped one, and the
            # footprint may be FLIPPED on top of that - three sign
            # conventions to get right for a number KiCad will hand over
            # correctly if asked. It was got wrong: a GND via landed 0.064 mm
            # from X1 pad 1 against a 0.127 mm rule, on a pad this model
            # thought it was clearing by 0.29 mm. A bounding box is
            # conservative for a rotated pad and exact for the axis-aligned
            # ones, which is every pad on this board that matters.
            bb = pad.GetBoundingBox()
            w, h = bb.GetWidth() / 1e6, bb.GetHeight() / 1e6
            rr = min(max(min(w, h) / 2.0, 0.02), 0.15)
            ct, st = 1.0, 0.0
            px = (bb.GetX() + bb.GetWidth() / 2) / 1e6
            py = 26.0 - (bb.GetY() + bb.GetHeight() / 2) / 1e6
            # COVERED, NOT APPROXIMATED. A capsule along the long axis leaves
            # the four corners of the rectangle sticking out - by 0.026 mm on
            # a QFN land and by 0.16 mm on the 3215 crystal's, which is
            # exactly where the DRC then found vias 0.064 mm from X1 pad 1.
            # A grid of discs on a pitch of rr*sqrt(2) COVERS the rectangle
            # with no gap, because that is the condition for discs of radius
            # rr on a square lattice to overlap at the cell corners.
            step = rr * 1.41421356
            nx = max(1, int(math.ceil(w / step)))
            ny = max(1, int(math.ceil(h / step)))
            for ix in range(nx):
                for iy in range(ny):
                    u = (-0.5 + (ix + 0.5) / nx) * w
                    v = (-0.5 + (iy + 0.5) / ny) * h
                    out.append((px + u * ct - v * st, py + u * st + v * ct,
                                rr, pad.GetNetname(), "pad"))
    for t in b._pcb.GetTracks():
        if t.Type() == _pcbnew.PCB_VIA_T:
            # VIAS WERE NOT IN THIS LIST AT ALL, so the VDD stitch could not
            # see the 40 GND vias the GND stitch had just placed and the only
            # thing keeping their drills apart was luck.
            pos = t.GetPosition()
            out.append((pos.x / 1e6, 26.0 - pos.y / 1e6,
                        t.GetWidth() / 2e6, t.GetNetname(), "via"))
            continue
        if t.Type() != _pcbnew.PCB_TRACE_T:
            continue
        w = t.GetWidth() / 2e6
        nn = t.GetNetname()
        a = (t.GetStart().x / 1e6, 26.0 - t.GetStart().y / 1e6)
        z = (t.GetEnd().x / 1e6, 26.0 - t.GetEnd().y / 1e6)
        n = max(1, int(math.hypot(z[0] - a[0], z[1] - a[1]) / 0.25))
        for k in range(n + 1):
            f = k / float(n)
            out.append((a[0] + (z[0] - a[0]) * f,
                        a[1] + (z[1] - a[1]) * f, w, nn, "track"))
    return out


def stitch(net, layers, want, pads_of_net=True, ring_r=None):
    """Put vias on `net`, next to its pads and/or on a ring, where they fit.

    Returns the list actually placed. A via that will not fit is NOT placed
    and NOT silently dropped - the count is reported.
    """
    all_obs = _obstacles()
    # SAME NET IS NOT AN OBSTACLE - it is the thing being joined. Foreign
    # copper must be cleared; own copper must merely not be drilled through.
    obs = [o for o in all_obs if o[3] != net]
    own = [o for o in all_obs if o[3] == net]
    placed = []
    # ONE VIA PER PAD BEFORE ANY PAD GETS TWO. The candidate list is
    # pad-major and 120 positions deep, so without this the first few pads
    # took a via each from three different rings and the `want` budget ran
    # out before the far side of the QFN was reached. A plane stitch is
    # coverage, not a count.
    served = set()
    cands = []          # (x, y, origin_pad_xy_or_None, layer)
    if pads_of_net:
        for ref, fp in b.refs.items():
            for pad in fp.Pads():
                if pad.GetNetname() != net:
                    continue
                px, py = pad.GetPosition().x / 1e6, 26.0 - pad.GetPosition().y / 1e6
                # Several RINGS around each pad, not one. The first version
                # tried a single ring at 0.62 mm and placed ZERO VDD vias -
                # on a board this dense every one of those twelve points was
                # already occupied, and a search that only looks in one place
                # reports "does not fit" when it means "did not look".
                lay = "B.Cu" if fp.IsFlipped() else "F.Cu"
                for dist in (0.58, 0.72, 0.88, 1.05, 1.25, 1.45, 1.70,
                             1.95):
                    for k in range(36):
                        a = math.radians(k * 10.0)
                        cands.append((px + dist * math.cos(a),
                                      py + dist * math.sin(a)),)
                        cands[-1] = (cands[-1][0], cands[-1][1],
                                     (px, py), lay)
    if ring_r:
        for rr in ring_r:
            n = max(6, int(2 * math.pi * rr / 1.8))
            for k in range(n):
                a = 2 * math.pi * k / n
                cands.append((CX + rr * math.cos(a), CY + rr * math.sin(a),
                              None, None))
    for x, y, origin, lay in cands:
        if len(placed) >= want:
            break
        if origin is not None and origin in served:
            continue
        if math.hypot(x - CX, y - CY) > R - 0.9:
            continue
        # THE NFC COIL'S CLEARANCE BAND IS AN OBSTACLE FOR VIAS TOO, and the
        # via's COPPER is what has to clear it, not its centre. Measured
        # 2026-09-05: with only the keep-out declared and the search unaware
        # of it, `stitch()` put a GND via centre at r 9.5389 -- outside the
        # band -- whose 0.45 mm pad reaches r 9.7639 and intrudes 0.0208 mm.
        # A point-in-polygon test on the centre said it was fine; the
        # keep-out check, which knows a via has a diameter, said it was not.
        _r = math.hypot(x - CX, y - CY)
        if (NFC_CLEAR_R_IN - VIA_D / 2.0) <= _r <= (NFC_CLEAR_R_OUT + VIA_D / 2.0):
            continue
        # TWO CLEARANCES, NOT ONE, BECAUSE THE FAB HAS TWO RULES. Against
        # copper (a pad, a track) the rule is FAB_RULES["min_clearance"] =
        # 0.127 mm and nothing more; against another DRILL it is hole-to-hole
        # 0.20 mm edge to edge, which on a 0.25 mm drill inside a 0.45 mm pad
        # is the binding one. A single 0.30 mm number for both was applying
        # the DRILL rule to every 0201 land on the board, and beside a QFN-48
        # on 0.40 mm pitch that forbids every position there is: 17 of 24 VDD
        # pads came back "does not fit" when the truth was "was not allowed
        # to look". 0.033 mm of margin on top, for the fact that this model
        # treats every obstacle as a disc.
        if any(math.hypot(x - ox, y - oy)
               < (VIA_D / 2.0 + (0.30 if kind == "via" else 0.16) + orr)
               for ox, oy, orr, _, kind in obs):
            continue
        # ...AND NOT DRILLED INTO ITS OWN NET'S PADS EITHER. Clearance does
        # not apply between copper of one net, but a hole through a land is
        # via-in-pad, which is a fab option this board has not bought: the
        # solder wicks down the barrel and the joint starves. 0.05 mm of air
        # edge to edge, no more, because on the same net that is all that is
        # needed.
        if any(math.hypot(x - ox, y - oy) < (VIA_D / 2.0 + orr + 0.05)
               for ox, oy, orr, _, _k in own):
            continue
        if any(math.hypot(x - vx, y - vy) < VIA_D + 0.45
               for vx, vy in placed):
            continue
        # AND CHECK THE STUB'S PATH, not just where the via lands. The via
        # position was tested and the 1.25 mm track running to it was not,
        # so the longest stubs drove straight across U1 pad 33, C15, C17 and
        # C5 - one short and four clearance violations, every one of them on
        # the wire rather than the hole. A fanout is copper too.
        if origin is not None:
            ox0, oy0 = origin
            steps = max(2, int(math.hypot(x - ox0, y - oy0) / 0.1))
            hit = False
            for k in range(1, steps):
                f = k / float(steps)
                sx, sy = ox0 + (x - ox0) * f, oy0 + (y - oy0) * f
                if any(math.hypot(sx - bx, sy - by)
                       < (0.10 + (0.30 if bk == "via" else 0.16) + br)
                       for bx, by, br, _, bk in obs):
                    hit = True
                    break
            if hit:
                continue
        b.via(net, (x, y), drill=VIA_DRILL, size=VIA_D, layers=layers)
        # AND A STUB FROM THE PAD TO IT. A via near a VDD pad is not
        # connected to that pad: on F.Cu and B.Cu the surrounding pour is
        # GND, so the only layer the via reaches is the In2 VDD plane and
        # KiCad reports all 26 of them as DANGLING VIAS - which they were.
        # The short track is the connection, and it is the designer's to
        # draw because it is a fanout, not a route.
        if origin is not None:
            b.track(net, [origin, (x, y)], width=0.20, layer=lay)
        placed.append((x, y))
        if origin is not None:
            served.add(origin)
        obs.append((x, y, VIA_D / 2.0, net, "via"))
        own.append((x, y, VIA_D / 2.0, net, "via"))
        if origin is not None:
            # the stub is copper too, and the NEXT via must clear it
            steps = max(2, int(math.hypot(x - ox0, y - oy0) / 0.2))
            for k in range(steps + 1):
                f = k / float(steps)
                own.append((ox0 + (x - ox0) * f, oy0 + (y - oy0) * f,
                            0.10, net, "track"))
    # AND SAY WHICH PADS WERE NOT REACHED, BY NAME. A count of vias placed
    # cannot distinguish 26 vias covering 26 pads from 26 vias covering 9;
    # the second is what the ring-heavy version was doing and it read as a
    # success. A VDD pad with no via is a pin fed by nothing.
    missed = []
    if pads_of_net:
        for ref, fp in sorted(b.refs.items()):
            for pad in fp.Pads():
                if pad.GetNetname() != net:
                    continue
                px = pad.GetPosition().x / 1e6
                py = 26.0 - pad.GetPosition().y / 1e6
                if (px, py) not in served:
                    missed.append("%s.%s" % (ref, pad.GetNumber()))
    STITCH_REPORT[net] = {"vias": len(placed), "pads_served": len(served),
                          "pads_missed": missed, "_served": sorted(served)}
    return placed


def link_orphans(net, layer_for, max_mm=2.6, width=0.20):
    """Join pads of `net` that no via could reach to ones that were.

    WHY THIS EXISTS AND WHY IT IS NOT THE ROUTER'S JOB. F.Cu and B.Cu are both
    poured GND, so a GND pad is joined to its plane by the fill and needs
    nothing; a VDD pad has NO surface copper of its own net anywhere near it
    and is an island until something reaches the In2 plane. `stitch()` gets a
    via next to 7 of the 24 VDD pads and cannot fit one beside the other 17 -
    measured, by name, in STITCH_REPORT. Those 17 are not a routing problem
    either: a VDD pin and its own decoupling capacitor are placed 0.5 mm apart
    on purpose, so the copper that joins them is a fanout, and handing it to
    an autorouter is how VDD's 24 pins became 24 ratlines and the router
    thrashed.

    Nearest-anchor, straight line, and the line is CHECKED against every
    foreign obstacle at 0.1 mm intervals. A pad that still cannot be reached
    is REPORTED BY NAME rather than left to look connected.
    """
    all_obs = _obstacles()
    obs = [o for o in all_obs if o[3] != net]
    served = set(STITCH_REPORT.get(net, {}).get("_served", ()))
    pads = []
    for ref, fp in sorted(b.refs.items()):
        for pad in fp.Pads():
            if pad.GetNetname() != net:
                continue
            px = pad.GetPosition().x / 1e6
            py = 26.0 - pad.GetPosition().y / 1e6
            lay = "B.Cu" if fp.IsFlipped() else "F.Cu"
            pads.append(("%s.%s" % (ref, pad.GetNumber()), px, py, lay))
    anchors = {p[0]: (p[1], p[2], p[3]) for p in pads if (p[1], p[2]) in served}
    linked, still = [], []
    changed = True
    while changed:
        changed = False
        for name, px, py, lay in pads:
            if name in anchors:
                continue
            best = None
            for aname, (ax, ay, alay) in anchors.items():
                if alay != lay:
                    continue
                d = math.hypot(ax - px, ay - py)
                if d < max_mm and (best is None or d < best[0]):
                    best = (d, ax, ay)
            if best is None:
                continue
            d, ax, ay = best
            steps = max(2, int(d / 0.1))
            clash = False
            for k in range(steps + 1):
                f = k / float(steps)
                sx, sy = px + (ax - px) * f, py + (ay - py) * f
                if any(math.hypot(sx - bx, sy - by)
                       < (width / 2.0 + (0.25 if bk == "via" else 0.16) + br)
                       for bx, by, br, _, bk in obs):
                    clash = True
                    break
            if clash:
                continue
            b.track(net, [(px, py), (ax, ay)], width=width, layer=lay)
            anchors[name] = (px, py, lay)
            linked.append((name, round(d, 3)))
            changed = True
    still = [p[0] for p in pads if p[0] not in anchors]
    STITCH_REPORT.setdefault(net, {})["linked"] = linked
    STITCH_REPORT[net]["orphans"] = still
    return linked, still


# ==========================================================================
# 7. THE PLANES
# ==========================================================================
# THE POURS ARE INSET FROM THE EDGE. Handed the board outline, KiCad fills
# to it and then reports every pad and every graphic near the rim as a
# copper-edge-clearance violation - 199 of them on the first run, which is
# not 199 mistakes, it is one. The inset is 0.35 mm: 0.25 mm is JLCPCB's
# copper-to-edge minimum and 0.10 mm is margin for the routing bit.
POUR_OUTLINE = [at_r(rr - 0.35 if rr > 12.9 else rr - 0.35, dd)
                for rr, dd in
                [(math.hypot(x - CX, y - CY),
                  math.degrees(math.atan2(y - CY, x - CX)))
                 for x, y in b.outline]]

# THE THREE GROUND POURS STOP AT THE COIL'S CLEARANCE BAND, AND THE VDD ONE
# DOES NOT. MEASURED 2026-09-05 (lane B2), on the board this file had just
# written, by reading the FILLED polygons back:
#
#   GND  F.Cu    2 islands: r 2.795..9.743 (255.270 mm2)  +  r 11.125..12.499
#                theta 165..195 (4.226 mm2)  <- STRANDED
#   GND  B.Cu    1 island   r 3.339..9.743
#   GND  In1.Cu  1 island   r 3.291..9.743
#   VDD  In2.Cu  2 islands: r 4.771..9.743 (275.232)  +  r 11.125..12.499,
#                a C spanning 266 deg (68.065 mm2)     <- STRANDED, AND IT
#                CARRIES THE CELL'S POSITIVE CONTACT
#
# `nfc-coil-clearance` is a FULL annulus (r 9.743..11.125 on every layer), so
# it does not thin the planes, it CUTS THEM IN TWO. Everything outside it is a
# separate island. On B.Cu and In1.Cu those outer rings touched no pad or via
# and KiCad's island removal deleted them, which is why nobody saw this. On
# F.Cu J2 pad 2 (GND) held one wedge alive and on In2.Cu the two annulus vias
# serving BT1.1 and J2.1 held the whole ring alive — and the ring is where the
# CR2032's positive terminal lands. The board had no power distribution from
# its own cell and every check passed.
#
# So: say it. The three GND pours are the CORE DISC, which is all the fill
# ever reached anyway; the outer ring on those layers is now ABSENT BY
# CONSTRUCTION rather than absent because a filler swept it up. That matters
# for more than tidiness: an island the filler keeps is an island a later via
# can resurrect, and a resurrected GND ring in the annulus is 68 mm2 of
# counterpoise appearing under a 2.4 GHz element that was solved without it.
#
# PROVED NOT TO MOVE ANY COPPER: the core radius is NFC_CLEAR_R_IN + 0.2, so
# the fill is still cut by the keep-out at exactly NFC_CLEAR_R_IN and the three
# inner islands come out with the same areas to 1e-3 mm2. The VDD pour keeps
# the full outline because its outer ring is real copper this board needs;
# it is joined to the core by the spokes below.
POUR_CORE_OUTLINE = [at_r(NFC_CLEAR_R_IN + 0.2, 360.0 * i / 360)
                     for i in range(360)]

b.pour("GND", "In1.Cu", outline=POUR_CORE_OUTLINE,
       why="The uninterrupted return path under every signal. On a 26 mm "
           "disc there is no room to run a ground trunk around a QFN-48's "
           "four sides and still escape the signals; the plane is what buys "
           "the escape. Cleared under the antenna by the rule area above, "
           "and stopped at the NFC coil's clearance band because everything "
           "beyond it is a separate island either way.")
b.pour("VDD", "In2.Cu", outline=POUR_OUTLINE,
       why="The cell's rail as a plane rather than a trace. A CR2032 at end "
           "of life has ohms of internal resistance and the board must not "
           "add any: a plane is the lowest-impedance path from the contact "
           "lands to five VDD pins and four bulk capacitors.")
b.pour("GND", "F.Cu", outline=POUR_CORE_OUTLINE,
       why="Top-side fill, for the RF ground the matching network's shunt "
           "capacitors return into and for the inverted-F's counterpoise.")
b.pour("GND", "B.Cu", outline=POUR_CORE_OUTLINE,
       why="Bottom-side fill under the actives, and the shield between the "
           "circuit and the cell can 0.578 mm below it.")



# -- stitch the planes now that both nets exist ---------------------------
# NO RING VIAS ON VDD. F.Cu and B.Cu are both poured GND, so a VDD via that
# is not attached to a VDD pad reaches the In2 plane and NOTHING ELSE - KiCad
# calls it a dangling via and it is right. Measured: 10 of them, all VDD, all
# from the ring. GND keeps its rings because both outer pours ARE GND, so a
# ring via there joins three real planes.
VIAS_VDD = stitch("VDD", ("F.Cu", "B.Cu"), want=40, pads_of_net=True,
                  ring_r=None)
VIAS_GND = stitch("GND", ("F.Cu", "B.Cu"), want=40, pads_of_net=True,
                  ring_r=(5.2, 7.0, 8.8))

# and the VDD pads no via could sit beside
VDD_LINKED, VDD_ORPHANS = link_orphans("VDD", None)


# ==========================================================================
# 7b. WHAT THE COIL'S CLEARANCE BAND CUT IN TWO, JOINED BACK
# ==========================================================================
# THREE UNCONNECTED ITEMS THE DRC HAD BEEN REPORTING AND NOBODY HAD READ AS
# ONE SENTENCE (measured 2026-09-05 by lane B2, on this file's own output):
#
#   Zone [GND] on In1.Cu | Zone [GND] on F.Cu     the stranded F.Cu wedge
#   Zone [GND] on B.Cu   | Pad 2 [GND] of BT1     the cell's negative return
#   Pad 49 [GND] of U1   | Pad 44 [GND] of U1     the SoC's exposed pad
#
# plus fifteen VDD ratlines. Two of the three are the SAME defect as the VDD
# ring above: `nfc-coil-clearance` is a full annulus, so it severs every plane
# into a core disc and an outer ring, and three pads live in the outer ring.
# The third is separate and worse.
#
# THE MEASUREMENT THAT SETTLED EACH ONE. `pcbnew`'s own connectivity, read
# after the zones are filled, returns the CLUSTER a pad belongs to. It does
# not agree with itself the way a geometric guess would:
#
#   U1.47/U1.48  VDD  cluster of 23, reaches the In2 zone   <- on the plane
#   BT1.1/J2.1   VDD  cluster of  7, reaches the In2 zone   <- on the RING
#   C1.1/C4.1    VDD  cluster of  1, reaches no zone        <- on nothing
#   U1.44/U1.32  GND  cluster of 91, reaches F/In1/B zones  <- on the plane
#   U1.49        GND  cluster of  1, reaches no zone        <- ON NOTHING
#   J2.2         GND  cluster of  2, reaches the F.Cu zone  <- on the WEDGE
#   BT1.2        GND  cluster of  1, reaches no zone        <- on nothing
#
# U1.49 is the QFN-48's 4.4 x 4.4 mm exposed pad. It is the SoC's analogue and
# RF ground and its datasheet requires it soldered to a plane through vias.
# It had NONE: the B.Cu pour is cleared 3.377 mm away from its centre by the
# 48 pins around it, so the pad touched no copper of its own net on any layer.
# That is not a routing gap, it is a missing connection to the part that
# radiates, and no ratline count made it look different from the other 27.

# -- a) the SoC's exposed pad, stitched to the In1 ground plane ------------
# 3 x 3 on 1.40 mm, so the outermost via's copper reaches 1.625 mm from the
# centre against the pad's own 2.20 mm half-width -- 0.575 mm inside its own
# land on every side, and 1.40 mm apart against a 0.20 mm hole-to-hole rule.
# In1.Cu is GND under the whole footprint (probed: inside the fill at the
# centre and at +/-1.2 mm), so each via lands on real plane copper.
#
# THIS IS VIA-IN-PAD AND stitch() REFUSES TO DO IT ON PURPOSE (see its own
# note: "the solder wicks down the barrel and the joint starves"). The
# exception is deliberate and narrow: that rule protects 0.40 mm signal
# lands, where one wicked barrel is the whole joint. An exposed pad is
# 19.36 mm2 with nine 0.049 mm2 barrels in it, the vias are TENTED on F.Cu
# (KiCad's default: no mask aperture on a via), so the only opening is the
# B.Cu side the paste is on, and every QFN reference layout in the industry
# does exactly this. The paste aperture over the pad is the reflow control
# and belongs to the stencil, not here.
EP_VIA_PITCH = 1.40
_ep_x, _ep_y = _pad_xy("U1", 49)
EP_VIAS = []
for _dx in (-EP_VIA_PITCH, 0.0, EP_VIA_PITCH):
    for _dy in (-EP_VIA_PITCH, 0.0, EP_VIA_PITCH):
        b.via("GND", (_ep_x + _dx, _ep_y + _dy), drill=VIA_DRILL, size=VIA_D,
              layers=("F.Cu", "B.Cu"))
        EP_VIAS.append((_ep_x + _dx, _ep_y + _dy))

# -- b) the In2 VDD ring, joined to the In2 VDD core ----------------------
# RADIAL SPOKES, NOT A SECOND RING AND NOT A VIA PAIR. `nfc-coil-clearance`
# forbids pours and vias inside the band and ALLOWS TRACKS, in its own words
# because "the two tie stubs and the coil's own escape have to cross this
# band". A track on In2.Cu therefore needs no via at either end -- it is the
# same layer as the copper at both ends -- and it is the cheapest thing that
# can cross.
#
# AND A RADIAL SPOKE IS THE ONE SHAPE THAT DOES NOT LOAD THE COIL. What a
# 13.56 MHz winding induces in nearby metal is a CIRCULATING current; the
# 68 mm2 ring above it was severed for exactly that reason. A spoke offers no
# closed path around the coil's axis, so there is no loop to drive. This is
# the standard answer for a plane that has to reach past a coil and it is why
# the spokes run radially rather than taking any convenient diagonal.
#
# THE ANGLES ARE CHOSEN AGAINST THE ANTENNA, MEASURED, NOT GUESSED. The
# element's copper occupies theta 20..104 and `antenna-arm-shadow` forbids
# In1/In2/B.Cu copper over theta 13..107. 186 and 306 are 79 and 161 degrees
# clear of it, and they are also clear of both annulus vias (theta 200.2 and
# 278.3, the nearest 14 degrees = 2.9 mm away at r 11.7).
#
# AND 6 DEGREES OFF THE ROUND NUMBER, WHICH IS NOT COSMETIC. At 180.0 and
# 300.0 the spoke's inner end lands on the same ray as a GND ring via:
# stitch()'s outermost ring is r 8.8 with n = int(2*pi*8.8/1.8) = 30 vias, so
# they sit every 12 degrees starting at 0. MEASURED on the first build with
# these spokes: "Clearance violation (clearance 0.1270 mm; actual 0.0681 mm)"
# between "Via [GND] on F.Cu - B.Cu r 8.800 th 180.0" and this track. Half a
# step - 6 degrees, 0.92 mm at that radius - is the offset that clears it, and
# it is derived from the ring's own spacing rather than nudged until green.
VDD_SPOKE_DEG = (186.0, 306.0)
VDD_SPOKE_W = 0.50
VDD_SPOKES = []
for _deg in VDD_SPOKE_DEG:
    _a = (at_r(NFC_CLEAR_R_IN - 0.40, _deg), at_r(NFC_CLEAR_R_OUT + 0.40, _deg))
    b.track("VDD", list(_a), width=VDD_SPOKE_W, layer="In2.Cu")
    VDD_SPOKES.append((_deg, _a))

# -- c) J2's ground pin, which was holding a stranded wedge alive ---------
# With the GND pours cut back to the core disc the wedge is gone, so J2.2 now
# has to be reached the way any annulus pad is reached: a track on the layer
# it is already on. F.Cu carries no coil (the winding is B.Cu only), so the
# crossing is unobstructed. Its neighbours are J2.1 at theta 197.5 and J2.3 at
# theta 187.7, both 5 degrees away -- 0.96 mm at this radius against a
# 0.127 mm rule.
_j2x, _j2y = _pad_xy("J2", 2)
_j2_deg = math.degrees(math.atan2(_j2y - CY, _j2x - CX)) % 360.0
GND_SPOKE = [(_j2x, _j2y), at_r(NFC_CLEAR_R_IN - 0.40, _j2_deg)]
b.track("GND", GND_SPOKE, width=0.30, layer="F.Cu")

# -- d) BT1.2, the cell's negative return: NOT FIXED HERE, and why --------
# It cannot be. BT1 pad 2 sits at r 11.600, theta 30.0 -- directly under the
# antenna element, which spans theta 20..104 at r 11.192..12.200. Every layer
# and every direction out of that pad is closed by a rule this lane must not
# break:
#
#   inward on B.Cu   `antenna-arm-shadow` forbids tracks on B.Cu over
#                    r 10.892..12.500 in that sector; below 10.892 the coil
#                    itself occupies r 10.043..10.825, leaving a 0.067 mm slot
#   outward on B.Cu  the same shadow reaches r 12.500 and
#                    `antenna-ground-clearance` forbids a via to r 12.950;
#                    the pour inset is 12.650, so there is no annulus left
#   a via anywhere   forbidden by `antenna-ground-clearance` across the whole
#                    sector, on all four layers, because a via to a plane IS
#                    the counterpoise D26/D27 removed to get the element to
#                    radiate at all
#
# The three sprung contacts are 120 degrees apart at theta 270/30/150 and the
# forbidden sector is 94 degrees wide, so ONE contact is always inside it. The
# pad half-width is 5.93 degrees, which leaves exactly one family of rotations
# with no contact in the sector: centres at 0/120/240 +/- 7 degrees -- which is
# where lane M's three keying notches are. So this is a mechanical decision
# (rotate BT1 onto the notches, or accept a contact that carries no net), not
# a routing one, and it is escalated rather than papered over.
# See docs/VERIFICATION-DEBT.md and DECISIONS.md D28.


# SOLID PAD CONNECTIONS, not thermal spokes. KiCad's default is four spokes
# per pad, and on a 0201 land 0.40 mm across there is no room for a spoke
# wider than the zone's own minimum - which KiCad reports, correctly, as a
# starved thermal. There is also no reflow argument for spokes here: every
# part on this board is a chip passive or a leadless package on a 0.6 mm
# four-layer board, none of them a thermal mass a spoke would protect.
# THE BOARD IS 0.60 mm THICK AND KiCad's DEFAULT IS 1.6. Board() does not
# take a thickness, so without this line the .kicad_pcb says 1.6 mm, the DFM
# report says 1.6 mm, and a fab quoting from these files builds a board
# nearly three times too thick for a stack that has 1.5 mm of headroom in
# total. Found by reading ce-fab's DFM output, which prints the thickness it
# measured - which is exactly what that line is for.
b._pcb.GetDesignSettings().SetBoardThickness(int(round(T_PCB * 1e6)))

for _z in b._pcb.Zones():
    _z.SetPadConnection(_pcbnew.ZONE_CONNECTION_FULL)
    # ISLANDS ARE REMOVED, not left and reported. A pour on a crowded 26 mm
    # disc strands little pockets of copper that touch nothing; KiCad calls
    # them isolated_copper and it is right - unconnected copper is an
    # antenna nobody designed. Removing them is the fix; silencing the check
    # would not be.
    _z.SetIslandRemovalMode(_pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)


# ---------------------------------------------------------------------------
# CARRY THE SCHEMATIC'S FIELDS ONTO THE BOARD
# ---------------------------------------------------------------------------
# `Board.place()` puts a land pattern down; it does not bring the part's
# VALUE or its order code with it, because those live on the schematic. The
# consequence was silent and total: `fab jlc` reads the .kicad_pcb, found no
# LCSC field on any footprint, and returned CANNOT DETERMINE for 42 of 44
# placed parts - every order code was on the sheet and not one of them
# reached the bill of materials. The BOM's Comment column was the footprint
# name repeated back, which is not a part number either.
#
# So the schematic is imported and its fields are copied across. That also
# makes the schematic the single place a part number is typed, which is the
# point.
import schematic as sch_mod                                       # noqa: E402

_sch = sch_mod.build()
_fielded, _valued, _dnp, _nobom = 0, 0, 0, 0
for _ref, _part in _sch.parts.items():
    if _ref not in b.refs:
        continue
    _fp = b.refs[_ref]
    if _part.value:
        _fp.SetValue(str(_part.value))
        _valued += 1
    # DNP AND EXCLUDE-FROM-BOM, CARRIED ACROSS. They were not, and the
    # consequence was in the fabrication report: C14-C17 are the crystal load
    # capacitors D-3 deliberately does NOT fit, the schematic says so with
    # dnp=True and in_bom=False, and the BOARD said nothing at all - so every
    # tool reading the .kicad_pcb counted four 0201 capacitors of unknown
    # value and filed them as UNDETERMINED. A part that is deliberately not
    # fitted is a decision, and a decision that does not reach the file the
    # factory reads is not a decision, it is a note in a Python source.
    if getattr(_part, "dnp", False):
        _fp.SetDNP(True)
        _dnp += 1
    if not getattr(_part, "in_bom", True):
        _fp.SetExcludedFromBOM(True)
        _nobom += 1
    for _k, _v in (_part.fields or {}).items():
        if _v in (None, ""):
            continue
        _fp.SetField(str(_k), str(_v))
        _fielded += 1
    # AND HIDE THEM. A KiCad footprint field is a TEXT ITEM, and a new one
    # arrives VISIBLE and on the silkscreen. Copying 324 fields across 61
    # parts therefore put 324 strings - order codes, prices, stock figures,
    # paragraphs of Note - onto the silk of a 26 mm disc, and the DRC went
    # from 10 violations to 584: 199 silk overlaps, 199 silk over copper,
    # 101 off the board edge and 75 unmirrored on the back. The fields are
    # wanted (the BOM reads them); the printing is not.
    for _fld in _fp.GetFields():
        _fld.SetVisible(False)


# ---------------------------------------------------------------------------
# SILKSCREEN OFF, and it is a decision rather than a tidy-up. 51 reference
# designators do not fit on a Ø26 mm disc: KiCad's DRC reported 45 of them
# over copper and 7 overlapping each other, and every one was true. A
# designator printed on top of another designator identifies nothing. The
# assembly house works from the pick-and-place file, and the F.Fab / B.Fab
# layers still carry every reference for the fabrication drawing, where
# there is room for them.
# ---------------------------------------------------------------------------
for _fp in b._pcb.GetFootprints():
    _fp.Reference().SetVisible(False)
    _fp.Value().SetVisible(False)


# ==========================================================================
# 8a. THE HEIGHT CHECK — the one a KiCad rule area cannot do
# ==========================================================================
# Package heights, mm, MAXIMUM not typical, each from the package drawing of
# the part the schematic actually orders. A typical height on a stack budget
# this tight is a number that passes on paper and fails on the line.
BODY_H = {
    "QFN-48-1EP_6x6mm_P0.4mm_EP4.4x4.4mm": (0.85, "nRF54L10-QFAA, QFN48 "
                                                  "0.75-0.85 mm"),
    "LGA-12_2x2mm_P0.5mm": (0.70, "LIS2DW12TR LGA-12, 0.7 mm"),
    "Crystal_SMD_2016-4Pin_2.0x1.6mm": (0.50, "NX2016SA, 2.0x1.6x0.5"),
    "Crystal_SMD_3215-2Pin_3.2x1.5mm": (0.90, "X321532768KGD2SI, 3.2x1.5x0.9"),
    "L_0603_1608Metric": (0.90, "MLZ1608M4R7, 0603 multilayer"),
    "C_0402_1005Metric": (0.55, "0402 X5R 10uF"),
    "C_0201_0603Metric": (0.33, "0201 MLCC"),
    "R_0201_0603Metric": (0.33, "0201 thick film"),
    "L_0201_0603Metric": (0.33, "0201 wirewound RF inductor"),
    "HALO_SWD_PADS_1x06_P1.27": (0.00, "PADS ONLY, no connector"),
    "TestPoint_Pad_D1.0mm": (0.00, "a probe land, no body"),
    "Fiducial_1mm_Mask2mm": (0.00, "bare copper, no body"),
    "HALO_UWB_LANDS_1x08_P1.00": (0.00, "PADS ONLY, not fitted"),
    "HALO_BATT_CONTACT_3PAD": (0.00, "solder lands, no body"),
    "HALO_ANT_2G4_MONOPOLE": (0.00, "etched copper"),
    "HALO_NFC_COIL_3T": (0.00, "etched copper"),
    "HALO_PIEZO_LEADS_2": (0.00, "solder lands; the bender is on the shell"),
}


def height_check():
    """Grade every placed part against lane M's stack, at its own radius.

    Three verdicts, and the middle one is used honestly:
      PASS              the body fits the allowance where it actually sits
      FAIL              it does not, with the overshoot in millimetres
      CANNOT DETERMINE  the allowance at that place is not in design.py

    THE THIRD CASE IS REAL AND IT IS NOT A DODGE. design.py fixes the
    clearance over the cell (0.578 mm) and over a compressed contact finger
    (0.428 mm), and lane M's own keep-out fixes the top face inside Ø21.2
    (0.400 mm). It does NOT state the clearance between the board's bottom
    face and the carrier deck outside the cell, nor between the top face and
    the shell's inner surface outside Ø21.2 - both would have to be read off
    the carrier and shell solids. So parts in those two regions are graded
    CANNOT DETERMINE and named, which is a work item for lane M rather than
    a guess dressed as a result.
    """
    rows, worst = [], []
    for ref, fp in sorted(b.refs.items()):
        fpid = b.fpids[ref].partition(":")[2]
        h, src = BODY_H.get(fpid, (None, "NO PACKAGE HEIGHT ON FILE"))
        bb = fp.GetBoundingBox(False, False)
        # the furthest the body reaches from the board centre, in mm
        cx, cy = bb.GetCenter().x / 1e6, bb.GetCenter().y / 1e6
        half = math.hypot(bb.GetWidth(), bb.GetHeight()) / 2e6
        r_far = math.hypot(cx - CX, (26.0 - cy) - CY) + half
        r_near = max(0.0, math.hypot(cx - CX, (26.0 - cy) - CY) - half)
        bottom = fp.IsFlipped()
        if h is None:
            rows.append((ref, fpid, None, None, "CANNOT DETERMINE", src))
            continue
        if h == 0.0:
            rows.append((ref, fpid, 0.0, None, "PASS", "no body: " + src))
            continue
        if bottom:
            if r_far <= R_CELL:
                allow, where = H_BOT_CELL, "over the cell"
            elif r_near >= R_CELL:
                allow, where = None, ("bottom face outside the cell - the "
                                      "carrier deck clearance is not in "
                                      "design.py")
            else:
                allow, where = H_BOT_CELL, "straddles the cell's edge"
        else:
            if r_far <= D_LAND / 2.0:
                allow, where = H_TOP_INNER, "top face inside Ø21.2"
            elif r_near >= D_LAND / 2.0:
                allow, where = None, ("top face outside Ø21.2 - the shell's "
                                      "inner surface is not in design.py")
            else:
                allow, where = H_TOP_INNER, "straddles Ø21.2"
        if allow is None:
            rows.append((ref, fpid, h, None, "CANNOT DETERMINE", where))
        elif h <= allow:
            rows.append((ref, fpid, h, allow, "PASS", where))
        else:
            rows.append((ref, fpid, h, allow, "FAIL", where))
            worst.append((h - allow, ref, h, allow, where))
    return rows, sorted(worst, reverse=True)


# ==========================================================================
# 8. REPORT — everything this board could not settle, printed every run
# ==========================================================================
def report():
    print("\n" + "=" * 72)
    print("halo rev A board — %s" % b.title)
    print("=" * 72)
    print(b.describe())
    print(b.stats())

    print("\n--- outline (from %s) ---" % M_SRC)
    print("  Ø%.2f mm x %.3f mm, %d notches of %.0f deg to R%.2f at %s"
          % (D_PCB, T_PCB, len(TAB_ANGLES), PCB_NOTCH_DEG, R_PCB_NOTCH,
             "/".join("%.0f" % a for a in TAB_ANGLES)))
    print("  NOT Ø31.87 — that is the SHELL's max OD at z=4.339, not the board")

    rows, worst = height_check()
    n = {"PASS": 0, "FAIL": 0, "CANNOT DETERMINE": 0}
    for r in rows:
        n[r[4]] += 1
    print("\n--- HEIGHT CHECK, part by part, against lane M's stack ---")
    print("  %-5s %-46s %6s %6s  %s" % ("ref", "package", "body", "allow",
                                        "verdict"))
    for ref, fpid, h, allow, verdict, where in rows:
        if verdict == "PASS" and h == 0.0:
            continue                    # etched copper and bare lands
        print("  %-5s %-46s %6s %6s  %-16s %s"
              % (ref, fpid[:46],
                 "-" if h is None else "%.2f" % h,
                 "-" if allow is None else "%.3f" % allow, verdict, where))
    print("  PASS %d   FAIL %d   CANNOT DETERMINE %d   (of %d parts)"
          % (n["PASS"], n["FAIL"], n["CANNOT DETERMINE"], len(rows)))
    if worst:
        print("  WORST OVERSHOOT: %s by %.3f mm (%.2f into %.3f, %s)"
              % (worst[0][1], worst[0][0], worst[0][2], worst[0][3],
                 worst[0][4]))
    import json as _j
    with open(os.path.join(HERE, "out", "height_check.json"), "w") as fh:
        _j.dump({"verdict": "FAIL" if n["FAIL"] else
                            ("CANNOT DETERMINE" if n["CANNOT DETERMINE"]
                             else "PASS"),
                 "counts": n,
                 "allowances_mm": {"bottom_over_cell": H_BOT_CELL,
                                   "top_inside_D21.2": H_TOP_INNER},
                 "source": M_SRC,
                 "rows": [dict(zip(("ref", "package", "body_mm", "allow_mm",
                                    "verdict", "where"), r)) for r in rows]},
                fh, indent=1)

    print("\n--- the height delta, open against lane M ---")
    rows = [("QFN-48 6x6 (U1)", 0.85), ("0603 inductor (L1)", 0.90),
            ("3215 crystal (X1)", 0.90), ("LGA-12 (U2)", 0.70),
            ("USON-8 (U3)", 0.60), ("0402 bulk (C9-C12)", 0.55),
            ("0201 passives", 0.33)]
    print("  bottom-face allowance over the cell: %.3f mm  (%.3f - %.3f)"
          % (H_BOT_CELL, Z_DECK_TOP, Z_CELL_TOP))
    print("  top-face allowance inside Ø%.1f:      %.3f mm"
          % (D_LAND, H_TOP_INNER))
    bad = 0
    for what, h in rows:
        v = "FITS" if h <= H_BOT_CELL else "OVER by %.2f mm" % (h - H_BOT_CELL)
        if h > H_BOT_CELL:
            bad += 1
        print("    %-22s %.2f mm   %s" % (what, h, v))
    print("  VERDICT: FAIL - %d of %d part classes exceed the stack."
          % (bad, len(rows)))
    # THE RESOLUTION IS ALREADY WRITTEN DOWN, in lane M's own D17.
    RECOVERABLE = 0.542
    worst_h = max(h for _, h in rows)
    need = worst_h + 0.05                      # body + a solder fillet
    print("  BUT DECISIONS.md D17 (lane M, 2026-09-04) ends: 'leaving "
          "%.3f mm of dead air under the cell that a flat pad embossed in "
          "the door could still recover'." % RECOVERABLE)
    print("  If that pad is embossed, the cell drops and the bottom-face "
          "allowance becomes %.3f + %.3f = %.3f mm."
          % (H_BOT_CELL, RECOVERABLE, H_BOT_CELL + RECOVERABLE))
    print("  The tallest part here is %.2f mm and needs %.2f mm with a "
          "fillet.  -> %s" % (worst_h, need,
                              "EVERY PART CLEARS" if need <= H_BOT_CELL + RECOVERABLE
                              else "still short by %.3f mm"
                                   % (need - H_BOT_CELL - RECOVERABLE)))
    print("  Only %.3f mm of the %.3f has to be recovered to clear the "
          "tallest part. THIS IS A REQUEST TO LANE M, and it is the single "
          "change that closes this lane's largest open item."
          % (max(0.0, need - H_BOT_CELL), RECOVERABLE))

    print("\n--- antenna ---")
    print("  eps_eff %.3f  MEASURED by openEMS on this board, not assumed"
          % fpg.EPS_EFF)
    print("  quarter wave at %.2f GHz          %.4f mm"
          % (fpg.F0 / 1e9, fpg.QUARTER_MM))
    print("  meander: %d teeth, depth SOLVED   %.4f mm"
          % (fpg.ANT_TEETH, fpg.ANT_TOOTH_DEPTH))
    print("  conductor drawn                   %.4f mm (error %.5f)"
          % (ANT_LEN_MM, ANT_LEN_MM - fpg.QUARTER_MM))
    print("  radial extent  R%.2f .. R%.2f, inside the cleared sector"
          % (min(r for r, a in ANT_PATH), max(r for r, a in ANT_PATH)))
    print("  S11 on this copper: ce-rf's to grade, and its last run on the")
    print("  20.71 mm version returned 2.886 GHz - which is why this is")
    print("  24.49 mm. Re-run halo-rev-a-2g4 to see whether that closed it.")

    if deferred:
        print("\n--- nets with pins on parts that have no land pattern ---")
        print("  (AE1/AE2/LS1 are etched copper and a bonded bender; their")
        print("   connections are drawn as tracks and pads, not footprints)")
        for name, pins in sorted(deferred.items()):
            print("    %-14s %s" % (name, ", ".join(pins)))

    # `unassigned_pads()` counts KiCad's PASTE-RELIEF SUB-PADS too - the
    # numberless roundrects modern library footprints carry to break a big
    # stencil aperture into several small ones. There are 84 of them on this
    # board and NONE of them is electrical, so reporting them as unconnected
    # would be a number that is always alarming and never actionable. The
    # real question is how many NUMBERED pads reached no net, and that is
    # counted separately below - it is the one that must be zero.
    import pcbnew as _pcb
    real, paste = [], 0
    for fp in b._pcb.GetFootprints():
        for pad in fp.Pads():
            if not pad.GetNumber():
                paste += 1
            elif not pad.GetNetname():
                real.append("%s.%s" % (fp.GetReference(), pad.GetNumber()))
    print("\n--- what the copper already joins (KiCad connectivity, "
          "post-fill) ---")
    for _net, _cl in sorted(PLANE_JOIN.items()):
        _npads = sum(len(g) for g in _cl)
        print("  %-4s %d pad(s) in %d cluster(s)%s"
              % (_net, _npads, len(_cl),
                 "   <- ONE PIECE" if len(_cl) == 1 else
                 "   the router is owed %d pin(s)" % len(_cl)))
        for _g in _cl[1:]:
            print("      apart: " + ", ".join(_g))
    print("\n--- plane stitching ---")
    print("  VDD vias %d   GND vias %d   (a plane nobody stitched is not a "
          "plane, and the router was being asked to route 63 pins that the "
          "copper should already join)" % (len(VIAS_VDD), len(VIAS_GND)))
    print("    VDD pads linked to a served neighbour: %d   still orphaned: "
          "%d%s" % (len(VDD_LINKED), len(VDD_ORPHANS),
                    "" if not VDD_ORPHANS else "   " + ", ".join(VDD_ORPHANS)))
    for _net in ("VDD", "GND"):
        _r = STITCH_REPORT.get(_net, {})
        _npad = sum(1 for fp in b.refs.values() for pd in fp.Pads()
                    if pd.GetNetname() == _net)
        print("    %-4s %d vias, %d of %d pads reached%s"
              % (_net, _r.get("vias", 0), _r.get("pads_served", 0), _npad,
                 "" if not _r.get("pads_missed")
                 else "   NOT REACHED: " + ", ".join(_r["pads_missed"])))

    print("\n--- schematic fields carried onto the board ---")
    print("  %d values and %d fields copied across %d parts"
          % (_valued, _fielded, len(_sch.parts)))
    _dnp_refs = sorted(r for r in b.refs if b.refs[r].IsDNP())
    print("  marked DO NOT POPULATE on the board: %d  %s"
          % (_dnp, ", ".join(_dnp_refs) or "none"))
    print("  excluded from the BOM: %d   (read back off the .kicad_pcb, not "
          "off the schematic that asked for it)" % _nobom)
    _missing = [r for r in sorted(b.refs)
                if r in _sch.parts
                and not (_sch.parts[r].fields or {}).get("LCSC Part #")]
    print("  placed parts with NO LCSC Part # field: %d%s"
          % (len(_missing), ("  " + ", ".join(_missing)) if _missing else ""))

    print("\n--- test access, placed by search ---")
    for ref, rr, deg in _tp_placed:
        print("  %-5s r=%5.2f  %5.1f deg" % (ref, rr, deg))
    if _tp_failed:
        print("  COULD NOT PLACE: %s — the board has no clear spot for "
              "these, which is a finding and not a reason to drop them"
              % ", ".join(_tp_failed))
    else:
        print("  all %d placed with >= %.2f mm of courtyard air"
              % (len(_tp_placed), CLEAR_MM))
    # THE ASYMMETRY THAT MAKES THE FIDUCIALS USEFUL, measured rather than
    # asserted: two fiducials at the same radius on opposite sides fix
    # position but NOT rotation, because the pair maps onto itself. These
    # must differ in radius and must not be diametrically opposite.
    fids = {r: (rr, dg) for r, rr, dg in _tp_placed if r.startswith("FID")}
    if len(fids) == 2:
        (r1, d1), (r2, d2) = fids["FID1"], fids["FID2"]
        dd = abs(d1 - d2) % 360.0
        dd = min(dd, 360.0 - dd)
        print("  fiducial asymmetry: dr = %.2f mm, dtheta = %.1f deg  -> %s"
              % (abs(r1 - r2), dd,
                 "PASS" if abs(r1 - r2) > 0.5 and abs(dd - 180.0) > 10.0
                 else "FAIL — the pair is symmetric and cannot fix rotation"))

    print("\n--- pads on no net ---")
    print("  paste-relief sub-pads (no number, not electrical): %d" % paste)
    print("  NUMBERED pads with no net: %d%s"
          % (len(real), "" if real else "   <- this is the number that matters"))
    for r in sorted(real):
        print("    " + r)

    print("\n--- keep-out check (KiCad's own rule areas) ---")
    ko = b.keepout_check()
    print("  verdict: %s" % ko.get("verdict"))
    if ko.get("note"):
        print("  note:    %s" % ko["note"])
    for row in ko.get("keepouts", []):
        print("    %-26s scope=%-5s %s"
              % (row.get("name"), row.get("scope"), row.get("verdict", "")))
    print("  hits: %s" % ko.get("hits"))
    import json as _json
    with open(os.path.join(HERE, "out", "keepout_check.json"), "w") as fh:
        _json.dump(ko, fh, indent=1, default=str)


# ==========================================================================
# 9. THE FAB RULES THE PROJECT FILE DOES NOT CARRY
# ==========================================================================
# `Board.rules()` writes clearance, track, via and hole rules. It does not
# write board-edge clearance or the solder-mask constraints, so KiCad falls
# back to ITS defaults - and a default is not a decision anybody made.
#
# THIS IS THE TRAP THE FACTORY LANE WARNED ABOUT and it caught us: the DRC
# reported "board setup constraints edge clearance 0.5000 mm; actual 0.3478"
# while this file's own report named JLCPCB's process. The rule that fired
# was not the rule the report named. So both are written explicitly below,
# each with the fab number it comes from, and `verify_rules()` reads the
# project file BACK and prints what the DRC will actually use.
FAB_RULES = {
    # JLCPCB "Min. board outline to copper": 0.2 mm for a routed edge. 0.30
    # is used - 0.2 plus 0.1 of margin for the routing bit's tolerance on a
    # 26 mm disc with three notches, where the cutter changes direction
    # inside the copper's blind spot.
    "min_copper_edge_clearance": 0.30,
    # SOLDER MASK: the web between two adjacent lands on a 0.4 mm pitch QFN
    # is about 0.2 mm and on an 0201 about 0.3 mm. KiCad's default asks for a
    # web it cannot have there and reported 23 "solder mask aperture bridges
    # items with different nets". That is TRUE and it is also NORMAL: at
    # 0.4 mm pitch the fab uses mask-defined openings and does not attempt a
    # web at all. Setting the minimum to 0 records that the apertures are
    # deliberately merged; it does not switch off the copper clearance check,
    # which is the one that would catch a real short.
    "solder_mask_min_width": 0.0,
    "solder_mask_to_copper_clearance": 0.0,
}


# ---------------------------------------------------------------------------
# THE NET NAMES KiCad LOSES ON THE WAY TO DISK
# ---------------------------------------------------------------------------
def track_net_snapshot():
    """{(x0,y0,x1,y1) in nm, KiCad frame: netname} for every track in memory."""
    out = {}
    for t in b._pcb.GetTracks():
        if t.Type() != _pcbnew.PCB_TRACE_T:
            continue
        a, z = t.GetStart(), t.GetEnd()
        out[(a.x, a.y, z.x, z.y)] = t.GetNetname()
    return out


_SEG_RE = __import__("re").compile(
    r'\(segment\s*\n\s*\(start ([-\d.]+) ([-\d.]+)\)\s*\n'
    r'\s*\(end ([-\d.]+) ([-\d.]+)\)\s*\n'
    r'(?:\s*\([^\n]*\)\s*\n)*?\s*\(net "([^"]*)"\)')


def repair_track_nets(pcb_path, snapshot):
    """Put back the net names `BOARD::Save()` dropped, and PROVE it took.

    MEASURED 2026-09-04, KiCad 10.0.6. board.py draws the NFC winding as two
    conductors, NFC1 from the outer end to the net tie and NFC2 from the tie
    to the inner end, and in memory that is exactly what it is - 291 segments
    on NFC1 and 292 on NFC2, printed straight off `GetTracks()` immediately
    before the write. The file that comes out has 583 segments on NFC2 and
    ZERO on NFC1. The four NFC1 PADS keep their net; only the tracks lose it.
    The same board saved through a two-net minimal case does not reproduce
    it, with or without the net-tie footprint, so this is not cepcb.

    WHY IT MATTERS RATHER THAN BEING COSMETIC. The Specctra export reads the
    file, so freerouting is handed an NFC1 that is three pads with no coil
    between them - and it will happily join those three pads with a short
    trace that BYPASSES THE WINDING ENTIRELY. The board would come back
    routed, DRC-clean, and with no NFC antenna. A net name is not a label
    here; it is the statement of what the copper is for.

    The repair is textual and it is checked by reloading the file through
    pcbnew afterwards - the same reader that found the loss. A repair that
    cannot be seen by a second reader is not a repair.
    """
    txt = open(pcb_path).read()
    fixed, checked = 0, 0
    out, pos = [], 0
    for m in _SEG_RE.finditer(txt):
        checked += 1
        key = tuple(int(round(float(m.group(i)) * 1e6)) for i in (1, 2, 3, 4))
        want = snapshot.get(key)
        if want is None or want == m.group(5):
            continue
        out.append(txt[pos:m.start(5)])
        out.append(want)
        pos = m.end(5)
        fixed += 1
    if fixed:
        out.append(txt[pos:])
        with open(pcb_path, "w") as fh:
            fh.write("".join(out))
    # READ IT BACK WITH pcbnew, not with the regex that just wrote it.
    rl = _pcbnew.LoadBoard(pcb_path)
    got = {}
    for t in rl.GetTracks():
        if t.Type() == _pcbnew.PCB_TRACE_T:
            got[t.GetNetname()] = got.get(t.GetNetname(), 0) + 1
    want_counts = {}
    for n in snapshot.values():
        want_counts[n] = want_counts.get(n, 0) + 1
    ok = got == want_counts
    return {"segments_in_file": checked, "net_names_repaired": fixed,
            "want": want_counts, "got": got, "verdict": "PASS" if ok else "FAIL"}


# ---------------------------------------------------------------------------
# CONTROLLED IMPEDANCE — D21. The number the factory needs, or a refusal.
# ---------------------------------------------------------------------------
#: The 0.60 mm four-layer builds a house will actually commit to, with the
#: L1->L2 prepreg each one presses. JLCPCB IS NOT HERE AND THAT IS THE POINT:
#: its own impedance stackup page and the thickness dropdown in its own
#: calculator offer 0.8/1.0/1.2/1.6/2.0 mm for four layers and nothing else,
#: so impedance control CANNOT BE BOUGHT from JLCPCB at 0.60 mm. PCBWay
#: publishes six builds and the height is set by the INNER LAYERS' RESIDUAL
#: COPPER RATIO, not by the order - which is why this is a table and not a
#: number. https://www.pcbway.com/multi-layer-laminated-structure.html
STACK_CANDIDATES = [
    ("PCBWay 0.60mm 4L #35  (70% inner residual, 3313 RC58%)", 0.0925, 4.45),
    ("PCBWay 0.60mm 4L #36  (50% inner residual, 3313 RC58%)", 0.0855, 4.45),
    ("PCBWay 0.60mm 4L #112 (30% inner residual, 2x1080 RC68%)", 0.1375, 4.21),
]
RF_W = 0.127            # the netclass width, and the RF trace width
CU_T = 0.035            # 1 oz outer, plated


def _z0_hammerstad(w, h, t, er):
    """Hammerstad-Jensen microstrip, with Hammerstad's thickness correction.

    A SECOND FORMULA ON PURPOSE. cepcb.stackup.microstrip_z0 is IPC-2141's
    closed form and answers ADVISORY, +/-10 % class. Two independent closed
    forms that agree to 1.7 ohm are worth more than one that passes, which is
    the rule in docs/TOOLS-THAT-LIE.md item 5.
    """
    u = w / h
    if t > 0:
        coth = 1.0 / math.tanh(math.sqrt(6.517 * u))
        dw = (t / math.pi) * math.log(1 + 4 * math.e / (t / h) / (coth ** 2))
        u += dw / h
    f = 6 + (2 * math.pi - 6) * math.exp(-((30.666 / u) ** 0.7528))
    z0air = (376.73 / (2 * math.pi)) * math.log(f / u + math.sqrt(1 + (2 / u) ** 2))
    a = (1 + math.log((u ** 4 + (u / 52) ** 2) / (u ** 4 + 0.432)) / 49
         + math.log(1 + (u / 18.1) ** 3) / 18.7)
    bb = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
    ee = (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / u) ** (-a * bb)
    return z0air / math.sqrt(ee), ee


def impedance_report():
    """What the RF trace is, in ohms, on every stack a house will commit to."""
    rows = []
    for name, h, er in STACK_CANDIDATES:
        z_hj, ee = _z0_hammerstad(RF_W, h, CU_T, er)
        lo, hi = 0.02, 3.0
        for _ in range(80):                       # w for exactly 50 ohm
            mid = (lo + hi) / 2.0
            if _z0_hammerstad(mid, h, CU_T, er)[0] > 50.0:
                lo = mid
            else:
                hi = mid
        rows.append({"stack": name, "h_mm": h, "er": er,
                     "z0_ohm": round(z_hj, 2), "eps_eff": round(ee, 3),
                     "w_for_50R_mm": round((lo + hi) / 2.0, 4)})
    zs = [r["z0_ohm"] for r in rows]
    gamma = max(abs((z - 50.0) / (z + 50.0)) for z in zs)
    return {"rf_width_mm": RF_W, "copper_mm": CU_T, "rows": rows,
            "z0_min": min(zs), "z0_max": max(zs),
            "worst_gamma": round(gamma, 4),
            "worst_return_loss_dB": round(-20 * math.log10(gamma), 2),
            "worst_mismatch_loss_dB": round(-10 * math.log10(1 - gamma ** 2), 4)}


#: Filled by `plane_join_report()`, read by `write_dsn_hints()`.
PLANE_JOIN = {}


def plane_join_report():
    """WHICH PADS THE COPPER ON THIS BOARD ALREADY JOINS — asked of KiCad.

    THE DEFECT THIS REPLACES. `dsnfix` used to delete GND and VDD from the
    routing problem outright, on the claim in its own docstring that "the
    pours join them and board.py's stitch() already put the vias in". That is
    TRUE FOR GND, whose pours are on both outer layers and touch every GND
    pad there, and FALSE FOR VDD, whose plane is on In2 and whose pads are on
    F.Cu and B.Cu: `stitch()` reached 9 of 24 and `link_orphans()` reached 0
    of the remaining 15, both reporting the miss by name. So fifteen VDD pins
    were removed from the router's problem on the grounds that they were
    already connected, while the board's own DRC reported them unconnected.
    The claim and the measurement had been disagreeing for a day.

    The fix is not a better guess. It is to ASK: `pcbnew`'s connectivity, run
    after the zones are filled, groups every item into clusters, so the number
    the router actually needs — how many separate pieces this net is in — is a
    measurement and not an assertion. One pin per cluster goes to the router;
    the rest are dropped because joining them is what the copper already does.

    Must be called AFTER `b.fill_zones()`: connectivity through a plane is
    connectivity through its FILL, and an unfilled zone joins nothing.
    """
    b._pcb.BuildConnectivity()
    conn = b._pcb.GetConnectivity()
    out = {}
    # GND and VDD ONLY, deliberately. NFC1/NFC2 are also hand-drawn, but they
    # are a coil whose two halves KiCad merges through a net tie, and dsnfix
    # has a separate, tested rule for that (`renet_nfc`). Handing the coil to
    # this one as well would let a cluster measurement decide which pins the
    # router may join on a net where the answer is already known.
    for net in ("GND", "VDD"):
        pads = []
        for ref, fp in sorted(b.refs.items()):
            for pad in fp.Pads():
                if pad.GetNetname() == net:
                    pads.append(("%s-%s" % (ref, pad.GetNumber()), pad))
        # Cluster identity by MEMBERSHIP, not by object identity: SWIG hands
        # back a fresh proxy each call, so two proxies for the same C++ pad
        # are not `is` and are not `==`. The set of (x, y) of the PADS in a
        # cluster is stable, cheap and cannot collide - two pads cannot share
        # a position.
        #
        # `GetConnectedItems(pad)` AND NOT `GetConnectedPads(pad)`. The second
        # one returns an EMPTY LIST for every pad on this board (measured:
        # 0 for U1-47, C1-1, BT1-1, BT1-2, U1-49, U1-44), so every key came
        # out `frozenset()`, every pad landed in one group, and this function
        # reported GND and VDD each as ONE PIECE while the DRC was reporting
        # 15 VDD ratlines. A cluster measurement that cannot tell a joined net
        # from a shattered one is the exact defect it was written to end, so
        # the empty key is now a REFUSAL rather than an answer.
        groups = {}
        for name, pad in pads:
            key = frozenset(
                (i.GetPosition().x, i.GetPosition().y)
                for i in conn.GetConnectedItems(pad)
                if i.Type() == _pcbnew.PCB_PAD_T)
            if not key:
                raise SystemExit(
                    "plane_join_report: KiCad's connectivity returned no pad "
                    "for %s on %s - not even itself. That is an API that has "
                    "changed under this code, not a net with no pads, and a "
                    "cluster count derived from it would call every net one "
                    "piece." % (name, net))
            groups.setdefault(key, []).append(name)
        # EACH CLUSTER'S PINS ARE ORDERED INNERMOST FIRST, and that decides
        # something. dsnfix keeps the FIRST pin of each cluster as the router's
        # anchor, so alphabetical order made BT1-1 -- the cell's positive
        # contact, out at r 11.600 in the annulus -- the anchor for VDD's main
        # cluster, and the router would have been asked to reach fourteen
        # central pads FROM THE ANNULUS, dragging power copper back and forth
        # across the NFC coil's clearance band to do it. The anchor should be
        # the pin the plane most surrounds, which is the innermost one.
        _pos = {name: pad.GetPosition() for name, pad in pads}

        def _r_of(name):
            p = _pos[name]
            return math.hypot(p.x / 1e6 - CX, 26.0 - p.y / 1e6 - CY)
        groups = {k: sorted(v, key=lambda n: (round(_r_of(n), 4), n))
                  for k, v in groups.items()}
        clusters = sorted(groups.values(), key=lambda g: (-len(g), g[0]))
        out[net] = clusters
    PLANE_JOIN.clear()
    PLANE_JOIN.update(out)
    return out


def write_dsn_hints(pcb_path):
    """What the Specctra export cannot say, written beside it for `dsnfix`.

    The DSN is a lossy picture of this board (see dsnfix.py's header). The two
    facts a router needs that it does not carry are which copper layers are
    poured planes and which half of the NFC winding is which net. Both are
    computed here, in the file that knows them, rather than typed into the
    fixer as constants that would silently go stale the day the coil moves.
    """
    import json as _j
    out = os.path.join(os.path.dirname(pcb_path), "dsn_hints.json")
    doc = {
        "source": "electronics/halo_rev_a/board.py",
        "board_centre_mm": [CX, CY],
        "dsn_centre_um": [CX * 1000.0, -(26.0 - CY) * 1000.0],
        "plane_layers": {"In1.Cu": "GND", "In2.Cu": "VDD"},
        "hand_routed_nets": sorted(HAND_ROUTED),
        # ONE PIN PER CLUSTER IS WHAT THE ROUTER IS OWED. See
        # plane_join_report(): these are the groups of pins this board's own
        # copper already joins, measured by KiCad's connectivity after the
        # fill. dsnfix keeps the first pin of each group and drops the rest, so
        # a net in one piece disappears from the problem and a net in sixteen
        # pieces arrives as sixteen pins. Empty means the report was never run,
        # and dsnfix REFUSES rather than falling back to dropping whole nets.
        "plane_clusters": PLANE_JOIN,
        "router_skip_pins": ROUTER_SKIP_PINS,
        "nfc": {
            "layer": "B.Cu",
            "width_um": fpg.NFC_W * 1000.0,
            "split_radius_um": NFC_SPLIT_R * 1000.0,
            "outer_half_net": "NFC1",
            "inner_half_net": "NFC2",
            "why": "KiCad merges NFC1 into NFC2 through the AE2 net tie - "
                   "correct, because a coil is a DC short between its own "
                   "terminals - so every winding segment exports as NFC2 "
                   "while the pads keep their own nets. The winding is a "
                   "spiral, so radius separates the halves exactly.",
            "segments_outer": len(_nfc1_pts) - 1,
            "segments_inner": len(_nfc2_pts) - 1,
        },
    }
    with open(out, "w") as fh:
        _j.dump(doc, fh, indent=1)
    return out


def write_fab_rules(pcb_path):
    import json as _j
    pro = os.path.splitext(pcb_path)[0] + ".kicad_pro"
    with open(pro) as fh:
        doc = _j.load(fh)
    doc.setdefault("board", {}).setdefault("design_settings", {}) \
       .setdefault("rules", {}).update(FAB_RULES)
    with open(pro, "w") as fh:
        _j.dump(doc, fh, indent=2)
    return pro


def verify_rules(pcb_path):
    """Read the project file BACK and print the rules the DRC will use.

    Not a formality. A rule this script believes it set, that is not in the
    file the DRC reads, is exactly the failure the edge-clearance default
    already caused once here.
    """
    import json as _j
    pro = os.path.splitext(pcb_path)[0] + ".kicad_pro"
    with open(pro) as fh:
        doc = _j.load(fh)
    r = doc["board"]["design_settings"]["rules"]
    nc = doc.get("net_settings", {}).get("classes", [{}])[0]
    print("\n--- the rules the DRC will actually apply ---")
    for k in sorted(set(list(r) + ["clearance", "track_width"])):
        v = r.get(k, nc.get(k))
        print("  %-34s %s" % (k, v))
    missing = [k for k in FAB_RULES if k not in r]
    print("  written and read back: %d of %d%s"
          % (len(FAB_RULES) - len(missing), len(FAB_RULES),
             "" if not missing else "   MISSING: " + ", ".join(missing)))
    return not missing


if __name__ == "__main__":
    b.fill_zones()
    # AFTER THE FILL, NEVER BEFORE: connectivity through a plane is
    # connectivity through its fill, and an unfilled zone joins nothing.
    plane_join_report()
    _snap = track_net_snapshot()
    path = b.save(OUT)
    NET_REPAIR = repair_track_nets(path, _snap)
    HINTS = write_dsn_hints(path)
    write_fab_rules(path)
    # LAST, because `bin/sch build` overwrites this file with an 8-library
    # version of its own and anything written earlier is discarded.
    _n = fpg.write_fp_lib_table(os.path.dirname(path))
    print("fp-lib-table: %d libraries (KiCad's %d + halo)" % (_n, _n - 1))
    report()
    print("\n--- net names on the saved copper ---")
    print("  segments in the file: %d   net names repaired after save: %d"
          % (NET_REPAIR["segments_in_file"], NET_REPAIR["net_names_repaired"]))
    for _n in sorted(set(NET_REPAIR["want"]) | set(NET_REPAIR["got"])):
        print("    %-10s built %4d   in file %4d %s"
              % (_n, NET_REPAIR["want"].get(_n, 0), NET_REPAIR["got"].get(_n, 0),
                 "" if NET_REPAIR["want"].get(_n) == NET_REPAIR["got"].get(_n)
                 else "  <-- MISMATCH"))
    print("  verdict: %s   (KiCad 10.0.6 drops NFC1 on write; see "
          "repair_track_nets)" % NET_REPAIR["verdict"])
    print("  NFC winding: %d chords, chord error %.4f mm, length error "
          "%.5f %% of the true spiral"
          % (NFC_SEGS, NFC_CHORD_ERR_MM, NFC_LEN_ERR_PCT))
    print("  coil closed onto the tie: " + ", ".join(
        "%s %.3f mm" % (n, d) for n, d in NFC_TIE_STUBS)
        + ("   -> PASS" if all(d < 2.0 for _, d in NFC_TIE_STUBS)
           else "   -> FAIL, the winding has a hole in it"))
    _imp = impedance_report()
    print("\n--- controlled impedance (D21) ---")
    print("  RF trace %.3f mm, %.3f mm copper. JLCPCB DOES NOT SELL IMPEDANCE "
          "CONTROL AT 0.60 mm 4-layer" % (_imp["rf_width_mm"], _imp["copper_mm"]))
    print("  %-56s %7s %5s %9s %9s" % ("stack", "h_mm", "er", "Z0_ohm",
                                       "w@50R"))
    for _r in _imp["rows"]:
        print("  %-56s %7.4f %5.2f %9.2f %9.4f"
              % (_r["stack"], _r["h_mm"], _r["er"], _r["z0_ohm"],
                 _r["w_for_50R_mm"]))
    print("  Z0 across the builds a house will commit to: %.2f .. %.2f ohm"
          % (_imp["z0_min"], _imp["z0_max"]))
    print("  worst mismatch into 50 ohm: |G| %.4f, return loss %.2f dB, "
          "mismatch loss %.4f dB" % (_imp["worst_gamma"],
                                     _imp["worst_return_loss_dB"],
                                     _imp["worst_mismatch_loss_dB"]))
    print("  VERDICT: 50 ohm IS REACHABLE on this stack at 0.126-0.230 mm, "
          "all above the 0.09 mm multilayer floor. The number to name in a "
          "controlled-impedance order is PCBWay build #35 at 0.127 mm. "
          "Uncontrolled, the trace is CANNOT DETERMINE inside %.0f-%.0f ohm."
          % (_imp["z0_min"], _imp["z0_max"]))
    print("  NFC split radius for the DSN: %.4f mm   hints -> %s"
          % (NFC_SPLIT_R, os.path.basename(HINTS)))
    verify_rules(path)
    print("\nwrote", path)
