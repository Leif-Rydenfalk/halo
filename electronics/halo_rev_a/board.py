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
    which is not this board either. So the inverted-F drawn here is a
    PARAMETRIC PLACEHOLDER at a length computed from a quarter wavelength,
    put where the copper has to go, so that ce-rf has real geometry to
    solve instead of a blank annulus. Its S11 is CANNOT DETERMINE until
    ce-rf measures THIS copper. It is not asserted to work.
  * THE NFC COIL'S INDUCTANCE IS UNMEASURED, so C24/C25's 130 pF is a
    placeholder, exactly as the schematic says (X-2).
  * A PASSING DRC MEANS MANUFACTURABLE, NOT CORRECT. Whether the circuit
    works is the schematic's question and the simulators'.
"""
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
NFC_TIE_DEG = 200.0


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
# FORBIDS POURS AND VIAS, NOT TRACKS AND PADS. What an inverted-L monopole
# needs is its COUNTERPOISE removed - the ground and VDD planes, and any via
# stitching them - from under the radiating element. Forbidding tracks and
# pads as well was tried and reported 100 items_not_allowed against the NFC
# winding, which necessarily crosses this sector on its way round the board
# and is 13.56 MHz copper that does not behave as a 2.4 GHz counterpoise.
# WHAT DOES CROSS HERE IS A REAL COUPLING QUESTION AND IT IS ce-rf's: the NFC
# coil on B.Cu and BT1's positive contact land both sit under this sector and
# neither can move. They are in the model, not designed out.
b.keepout(outline=ANT_CLEAR, layers=["In1.Cu", "In2.Cu", "B.Cu"],
          tracks=False, vias=True, pads=False, pours=True, footprints=False,
          scope="board", name="antenna-ground-clearance",
          why="No ground plane, no inner copper and no bottom copper under "
              "the 2.4 GHz element. An inverted-F over its own ground plane "
              "is a short circuit. F.Cu is deliberately NOT in this list - "
              "the antenna itself lives there.")


# ==========================================================================
# 4. PLACEMENT
# ==========================================================================
# side: actives BOTTOM, passives TOP. See the height paragraph - the top
# face inside Ø21.2 allows 0.400 mm and every active here is taller, so the
# bottom's 0.578 mm is the better of two faces that are both too shallow.
PLACE = [
    # ref, footprint,                                  r,     deg, rot, side
    ("U1", "Package_DFN_QFN:QFN-48-1EP_6x6mm_P0.4mm_EP4.4x4.4mm",
     0.0, 0.0, 0.0, "bottom"),
    ("U3", "Package_SON:Winbond_USON-8-1EP_3x2mm_P0.5mm_EP0.2x1.6mm",
     7.9, 197.0, 17.0, "bottom"),
    ("U2", "Package_LGA:LGA-12_2x2mm_P0.5mm", 7.6, 262.0, 0.0, "bottom"),
    ("X2", "Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm", 7.4, 330.0, 60.0,
     "bottom"),
    ("X1", "Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm", 7.6, 148.0, 58.0,
     "bottom"),
    ("L1", "Inductor_SMD:L_0603_1608Metric", 7.3, 40.0, 40.0, "bottom"),
    # the CR2032's three lands: its own pads are already at r = 11.6
    ("BT1", "halo:HALO_BATT_CONTACT_3PAD", 0.0, 0.0, 0.0, "bottom"),
    # bulk, 0402, on the bottom where 0.55 mm still fits under 0.578 mm
    ("C9", "Capacitor_SMD:C_0402_1005Metric", 8.9, 340.0, 70.0, "bottom"),
    ("C10", "Capacitor_SMD:C_0402_1005Metric", 8.9, 300.0, 30.0, "bottom"),
    ("C11", "Capacitor_SMD:C_0402_1005Metric", 8.9, 170.0, 80.0, "bottom"),
    ("C12", "Capacitor_SMD:C_0402_1005Metric", 8.9, 235.0, 325.0, "bottom"),
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
    ("AE2", "NetTie:NetTie-2_SMD_Pad0.5mm", fpg.NFC_R_OUT,
     NFC_TIE_DEG, NFC_TIE_DEG + 90.0, "bottom"),
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

C0201 = "Capacitor_SMD:C_0201_0603Metric"
R0201 = "Resistor_SMD:R_0201_0603Metric"
L0201 = "Inductor_SMD:L_0201_0603Metric"

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
    # -- crystal load caps, DNP, out near their crystals
    (160.0, 6.40, [("C14", C0201), ("C15", C0201)]),
    (285.0, 6.40, [("C16", C0201), ("C17", C0201)]),
    # -- flash straps
    (176.0, 4.70, [("R3", R0201), ("R4", R0201)]),
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
    """Refuse a layout whose streets cannot clear, BEFORE placing anything.

    This is the check that would have caught the 70 shorting pads, and it
    costs nothing to run. It compares every pair of streets whose radius
    bands overlap and measures their arc separation at the smallest radius
    they share - the worst case, and the one the eye is worst at.
    """
    bands = []
    for ang, r0, items in STREETS:
        n = len([1 for _, fp in items if fp])
        if n:
            bands.append((ang, r0, r0 + (n - 1) * STREET_PITCH))
    bad = []
    for i, (a1, lo1, hi1) in enumerate(bands):
        for a2, lo2, hi2 in bands[i + 1:]:
            lo, hi = max(lo1, lo2), min(hi1, hi2)
            if lo > hi:
                continue                      # the bands do not overlap
            d = abs(a1 - a2) % 360.0
            d = min(d, 360.0 - d)
            sep = math.radians(d) * lo
            if sep < MIN_ARC_SEP:
                bad.append((a1, a2, lo, sep))
    return bad


_bad = check_street_separation()
if _bad:
    raise SystemExit(
        "REFUSED: %d street pairs are closer than %.2f mm at the radius they "
        "share, which is how 0201 land patterns end up overlapping:\n%s"
        % (len(_bad), MIN_ARC_SEP,
           "\n".join("  %5.1f deg vs %5.1f deg: %.2f mm at r=%.2f"
                      % (a1, a2, sep, lo) for a1, a2, lo, sep in _bad)))

placed, skipped = [], []
for ref, fpid, r, deg, rot, side in PLACE + SMALL:
    x, y = at_r(r, deg)
    b.place(ref, fpid, at=(x, y), rot=rot, side=side,
            anchor="origin" if ref in ANCHOR_ORIGIN else "center")
    placed.append(ref)

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
b.net("GND", "U3.9")


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

# -- AE1: the bent quarter-wave monopole ----------------------------------
ANT_ARC_DEG_WANT = math.degrees(fpg.QUARTER_MM / fpg.ANT_R)
ANT_ARC_DEG = min(ANT_ARC_DEG_WANT, fpg.ANT_ARC_MAX_DEG)
ANT_ARC_MM = math.radians(ANT_ARC_DEG) * fpg.ANT_R
ANT_TAIL_MM = max(0.0, fpg.QUARTER_MM - ANT_ARC_MM)

arc_track("ANT_FEED", fpg.ANT_R, ANT_FEED_DEG, ANT_FEED_DEG + ANT_ARC_DEG,
          fpg.ANT_W, "F.Cu", steps=72)
if ANT_TAIL_MM > 0.05:
    _a = ANT_FEED_DEG + ANT_ARC_DEG
    b.track("ANT_FEED",
            [at_r(fpg.ANT_R, _a), at_r(fpg.ANT_R - ANT_TAIL_MM, _a)],
            width=fpg.ANT_W, layer="F.Cu")

# -- AE2: the NFC winding, one half on each net ---------------------------
# Three turns from NFC_A0 round to NFC_A1, spiralling inward, cut in half at
# the net tie. The tie is a real part on the board, so the DRC sees a legal
# junction between two nets rather than a short.
NFC_A0, NFC_A1 = 20.0, 340.0
_turn = []
for _t in range(fpg.NFC_TURNS):
    _rr = fpg.NFC_R_OUT - _t * (fpg.NFC_W + fpg.NFC_GAP)
    _turn.append((_rr, NFC_A0 + _t * 4.0, NFC_A1 - _t * 4.0))
_half = len(_turn) // 2 or 1
for _i, (_rr, _a0, _a1) in enumerate(_turn):
    _net = "NFC1" if _i < _half else "NFC2"
    arc_track(_net, _rr, _a0, _a1, fpg.NFC_W, "B.Cu", steps=120)
    if _i + 1 < len(_turn):
        _rn = fpg.NFC_R_OUT - (_i + 1) * (fpg.NFC_W + fpg.NFC_GAP)
        _nx = "NFC1" if _i + 1 < _half else "NFC2"
        if _nx == _net:
            b.track(_net, [at_r(_rr, _a0), at_r(_rn, _a0 + 4.0)],
                    width=fpg.NFC_W, layer="B.Cu")

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

b.pour("GND", "In1.Cu", outline=POUR_OUTLINE,
       why="The uninterrupted return path under every signal. On a 26 mm "
           "disc there is no room to run a ground trunk around a QFN-48's "
           "four sides and still escape the signals; the plane is what buys "
           "the escape. Cleared under the antenna by the rule area above.")
b.pour("VDD", "In2.Cu", outline=POUR_OUTLINE,
       why="The cell's rail as a plane rather than a trace. A CR2032 at end "
           "of life has ohms of internal resistance and the board must not "
           "add any: a plane is the lowest-impedance path from the contact "
           "lands to five VDD pins and four bulk capacitors.")
b.pour("GND", "F.Cu", outline=POUR_OUTLINE,
       why="Top-side fill, for the RF ground the matching network's shunt "
           "capacitors return into and for the inverted-F's counterpoise.")
b.pour("GND", "B.Cu", outline=POUR_OUTLINE,
       why="Bottom-side fill under the actives, and the shield between the "
           "circuit and the cell can 0.578 mm below it.")



# SOLID PAD CONNECTIONS, not thermal spokes. KiCad's default is four spokes
# per pad, and on a 0201 land 0.40 mm across there is no room for a spoke
# wider than the zone's own minimum - which KiCad reports, correctly, as a
# starved thermal. There is also no reflow argument for spokes here: every
# part on this board is a chip passive or a leadless package on a 0.6 mm
# four-layer board, none of them a thermal mass a spoke would protect.
import pcbnew as _pcbnew
for _z in b._pcb.Zones():
    _z.SetPadConnection(_pcbnew.ZONE_CONNECTION_FULL)
    # ISLANDS ARE REMOVED, not left and reported. A pour on a crowded 26 mm
    # disc strands little pockets of copper that touch nothing; KiCad calls
    # them isolated_copper and it is right - unconnected copper is an
    # antenna nobody designed. Removing them is the fix; silencing the check
    # would not be.
    _z.SetIslandRemovalMode(_pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)


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
    "Winbond_USON-8-1EP_3x2mm_P0.5mm_EP0.2x1.6mm": (0.60, "GD25LQ32E USON-8"),
    "LGA-12_2x2mm_P0.5mm": (0.70, "LIS2DW12TR LGA-12, 0.7 mm"),
    "Crystal_SMD_2016-4Pin_2.0x1.6mm": (0.50, "NX2016SA, 2.0x1.6x0.5"),
    "Crystal_SMD_3215-2Pin_3.2x1.5mm": (0.90, "X321532768KGD2SI, 3.2x1.5x0.9"),
    "L_0603_1608Metric": (0.90, "MLZ1608M4R7, 0603 multilayer"),
    "C_0402_1005Metric": (0.55, "0402 X5R 10uF"),
    "C_0201_0603Metric": (0.33, "0201 MLCC"),
    "R_0201_0603Metric": (0.33, "0201 thick film"),
    "L_0201_0603Metric": (0.33, "0201 wirewound RF inductor"),
    "HALO_SWD_PADS_1x06_P1.27": (0.00, "PADS ONLY, no connector"),
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
    print("  VERDICT: FAIL - %d of %d part classes exceed the stack. "
          "Lane M owns the resolution." % (bad, len(rows)))

    print("\n--- antenna, CANNOT DETERMINE ---")
    print("  quarter wave at %.2f GHz, eps_eff %.1f: %.2f mm"
          % (F0 / 1e9, EPS_EFF, QUARTER_MM))
    print("  arc at R%.2f: %.1f deg wanted, %.1f deg drawn (sector is %.0f)"
          % (ANT_R, ANT_ARC_DEG, ANT_ARC_DEG_FIT, ANT_SECTOR_ARC))
    if ANT_ARC_DEG_FIT < ANT_ARC_DEG:
        print("  THE ELEMENT IS TRUNCATED: the clear sector is shorter than a "
              "quarter wave by %.1f deg (%.2f mm of arc). A truncated element "
              "resonates HIGH, which is the direction ce-rf's two cases "
              "already failed in. This is a real finding, not a placement "
              "detail." % (ANT_ARC_DEG - ANT_ARC_DEG_FIT,
                           math.radians(ANT_ARC_DEG - ANT_ARC_DEG_FIT) * ANT_R))
    print("  S11 on this copper: CANNOT DETERMINE until ce-rf solves it.")

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
    path = b.save(OUT)
    write_fab_rules(path)
    report()
    verify_rules(path)
    print("\nwrote", path)
