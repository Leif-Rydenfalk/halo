"""halo's own land patterns — the six KiCad does not have, generated.

    python3 ce-designs/halo/electronics/halo_rev_a/footprints.py

Writes `electronics/halo_rev_a/halo.pretty/*.kicad_mod`. Every pattern here
exists because SPEC.md or DECISIONS.md forced a part no catalogue sells, and
the honest response to "there is no footprint for this" is to draw one from
the mechanical source — not to borrow a similar-looking one.

  HALO_BATT_CONTACT_3PAD      three sprung CR2032 fingers (SPEC.md §4)
  HALO_ANT_2G4_FEED           the 2.4 GHz feed land
  HALO_PIEZO_LEADS_2          two wire lands for the bender (D11a)
  HALO_SWD_PADS_1x06_P1.27    programming lands
  HALO_TP_D0.8                a probe land sized for THIS board
  HALO_UWB_LANDS_1x08_P1.00   the reserved halo-uwb stub (D12)

The two ETCHED SHAPES - the antenna element and the NFC coil - are NOT
footprints. They are board tracks, drawn by board.py from the geometry
constants in this file. Why, and the two constructs that failed first, is
below and repeated in antenna_2g4().

---------------------------------------------------------------------------
HOW ETCHED COPPER IS DRAWN, AND THE TWO WAYS THAT DO NOT WORK
---------------------------------------------------------------------------
An antenna and a coil are shapes in copper on a net. Getting both halves of
that at once took three attempts, and the first two are recorded here
because each produced a board that looked right and failed its own DRC.

  1. A CUSTOM PAD WITH OPEN `gr_line` PRIMITIVES. KiCad closes an open
     primitive chain into an outline and FILLS it, so a 3-turn coil at
     R11.7-12.7 became a solid Ø25 mm disc of copper on the coil's net.
     Measured: 18 shorting_items against pads at the board centre that no
     winding could reach, including U1 pad 25 three millimetres from the
     origin.
  2. FOOTPRINT GRAPHICS ON A COPPER LAYER (`fp_line` with `(layer "F.Cu")`).
     These stroke correctly and they do reach the Gerbers as copper. But a
     footprint graphic CARRIES NO NET, so KiCad's DRC treats the element as a
     foreign object and demands clearance from everything near it —
     including the antenna's own feed pad. Measured: 41 clearance and 34
     solder_mask_bridge violations, and there is no way to give an `fp_line`
     a net.
  3. A CUSTOM PAD WHOSE PRIMITIVE IS AN EXPLICITLY CLOSED RIBBON — the outer
     arc forward, the inner arc back. It fills to exactly the trace, and it
     is on a net. KiCad refuses it too, and says why in as many words:
     "Padstack is not valid (custom pad shape must resolve to a single
     polygon)". A 20 mm arc of 0.6 mm trace is a long thin ribbon whose
     primitive does not merge with the anchor rect into one polygon.
  4. A TRACK. Which is the construct KiCad has for exactly this — arbitrary
     shape, on a net, plotted as copper, understood by the DRC, the Gerber
     plotter and a human. So the antenna element and the NFC winding are
     drawn in board.py with `Board.track()`, from the geometry constants in
     this file, which board.py imports rather than re-derives.

The coil needs one more thing: it is a short circuit at DC, and KiCad is
right to say so. It uses KiCad's own `NetTie:NetTie-2_SMD_Pad0.5mm` placed
mid-winding. Writing a bespoke net-tie footprint was tried first and failed
for the same single-polygon reason; also measured on the way, an
`allow_bridged_nets` token inside `(attr ...)` makes KiCad's parser refuse
the file outright — found by bisecting four variants through
`FootprintLoad`, which returned None for every one carrying it.

---------------------------------------------------------------------------
EVERY MECHANICAL NUMBER COMES FROM LANE M
---------------------------------------------------------------------------
`ce-designs/halo/design.py` is the single place every mechanical number in
this project is typed. This file re-states only the ones it needs, and
prints them on every run so a reviewer can diff them against that file
rather than trust this one.
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "halo.pretty")

# --- lane M's numbers, ce-designs/halo/design.py --------------------------
R_SPRING_ARC = 11.60       # mean radius of the sprung contact's cantilever
W_SPRING = 2.40            # C5191 strip width -> the land's tangential size
SPOKE_ANGLES = (90.0, 210.0, 330.0)
D_PCB = 26.00
R_PCB_NOTCH = 12.60        # the three keying notches cut this deep
SRC = ("ce-designs/halo/design.py (lane M): R_SPRING_ARC=11.60, "
       "W_SPRING=2.40, SPOKE_ANGLES=(90,210,330), D_PCB=26.00, "
       "R_PCB_NOTCH=12.60")

# --- halo's own, each argued where it is used -----------------------------
PAD_RADIAL = 1.20          # radial length of a contact land. 1.20 mm gives
                           # the formed tongue a wiping zone wider than lane
                           # M's 0.400 mm working deflection plus the 0.250
                           # mm detent travel, and keeps the land's far
                           # corner inside R12.25 - which the notch bottom at
                           # R12.60 makes the binding constraint, not taste.

C0 = 299792458.0
F0 = 2.44e9
EPS_EFF = 1.573            # MEASURED, not assumed. 2.2 was the textbook
                           # figure for a surface trace with its reference
                           # plane cleared away, and it was wrong for this
                           # board: openEMS solved the real Ø26 x 0.60 mm
                           # geometry and reported eps_eff_implied = 1.573
                           # with the element resonating at 2.886 GHz
                           # against a 2.4-2.4835 GHz target. A thinner
                           # board with its ground cleared holds less of the
                           # field in the substrate, so the effective
                           # permittivity is lower and the quarter wave is
                           # LONGER: 24.49 mm, not 20.71.
                           # Source: ce-rf/out/halo-rev-a-2g4, run
                           # 2026-09-04, 664224 cells, 934.6 s, converged.
QUARTER_MM = (C0 / F0) * 1000.0 / math.sqrt(EPS_EFF) / 4.0

ANT_R = 11.90              # mid-annulus, and inside R12.25
ANT_W = 0.60
ANT_ARC_MAX_DEG = 84.0     # the three 26 deg keying notches at 0/120/240
                           # leave clear arcs of 94 deg; 5 deg of margin at
                           # each end keeps the element off the routed edge
ANT_TEETH = 4              # four meander teeth; see element_path()
ANT_TOOTH_MAX = 1.05       # the deepest a tooth may reach inward. The
                           # element sits at R11.90 and the NFC winding's
                           # outermost turn is at R10.75 on the other face,
                           # so 1.05 mm stops at R10.85 and no deeper.

NFC_W = 0.15
NFC_GAP = 0.15
# 2.106, NOT 2, AND THE 0.106 IS A SOURCING FACT RATHER THAN AN RF ONE.
# The NFC tank is L * C and lane S1 measured that the C half cannot be bought:
# NO 1.1 nF CAPACITOR EXISTS IN 0201 IN ANY DIELECTRIC, none in 0402 either,
# and the smallest 1.1 nF in the whole LCSC catalogue is 0603 - three sizes
# too big for a Ø26 mm board. 1.2 nF C0G does not exist in 0201 either, so
# there is not even a bracketing pair to interpolate between. The only part in
# the neighbourhood is 1.0 nF C0G (C161371, 139,150 in stock).
#
# So the tuning moves into the copper, where it is free. Each series capacitor
# drops 1.109 -> 1.0 nF, the series capacitance across the coil drops
# 554.6 -> 500 pF, and L must rise by exactly that ratio, 554.6/500 = 1.1092:
# ce-rf's measured 0.2449 uH -> a TARGET of 0.2716 uH.
#
# Turns, on the N-squared scaling a planar spiral obeys to first order:
#     N' = 2 * sqrt(1.1092) = 2.1064
# which at a 0.30 mm pitch moves the innermost turn from R10.150 to R10.118,
# still outside the Ø20.0 cell can at R10.0 with 0.043 mm of copper edge to
# spare. THE RESULTING INDUCTANCE IS NOT MEASURED. N-squared is the first term
# of Wheeler's expression and the mean diameter moves too; ce-rf owns the
# solve and until it re-runs on 2.106 turns the tank's resonant frequency is
# CANNOT DETERMINE, not 13.56 MHz. The number here is what to solve, not what
# was found.
NFC_TURNS_TARGET_UH = 0.2716
NFC_TURNS_MEASURED_UH = 0.2449          # ce-rf, on the 2.000-turn winding
NFC_TURNS = 2.0 * (NFC_TURNS_TARGET_UH / NFC_TURNS_MEASURED_UH) ** 0.5
NFC_R_OUT = 10.75          # INSIDE the contact lands, not outside them. The
                           # outer annulus is oversubscribed: the three
                           # contact lands occupy R11.0-12.2 on the bottom
                           # face and the notches cap everything at R12.25.
                           # The coil therefore sits between the cell's edge
                           # (R10.0) and the lands, which puts it just
                           # outside the can rather than over it.
                           #
                           # THE BAND IS 0.85 mm WIDE AND THAT SETS THE TRACE.
                           # R10.0 is the cell can's edge and R10.85 is the
                           # nearest contact land minus clearance. Three
                           # turns at 0.20/0.20 need 1.20 mm and ran straight
                           # through the crystal load capacitors and U3's
                           # pads - 17 clearance violations, measured. At
                           # 0.15/0.15 three turns need 0.60 mm and the
                           # winding closes at R10.15, inside the band. 0.15
                           # is still above the 0.127 mm process minimum.


# ==========================================================================
# COPPER PRIMITIVES
# ==========================================================================
def _poly(pts):
    body = ['      (gr_poly\n        (pts\n']
    for x, y in pts:
        body.append('          (xy %.4f %.4f)\n' % (x, y))
    body.append('        )\n        (width 0) (fill yes)\n      )\n')
    return body


def _ribbon(r, a0_deg, a1_deg, width, steps=64):
    """An arc of copper as a CLOSED FILLED POLYGON, for a custom pad."""
    half = width / 2.0
    pts = []
    for i in range(steps + 1):
        t = math.radians(a0_deg + (a1_deg - a0_deg) * i / steps)
        pts.append(((r + half) * math.cos(t), -(r + half) * math.sin(t)))
    for i in range(steps + 1):
        t = math.radians(a1_deg - (a1_deg - a0_deg) * i / steps)
        pts.append(((r - half) * math.cos(t), -(r - half) * math.sin(t)))
    return _poly(pts)


def _ribbon_line(x0, y0, x1, y1, width):
    """A straight run of copper as a closed filled polygon."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * width / 2.0, dx / L * width / 2.0
    return _poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
                  (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])


def _courtyard(pts, layer="F.CrtYd"):
    """A CLOSED courtyard outline.

    Closed, because KiCad's DRC reports an open polyline as a malformed
    courtyard and it is right to: an open outline encloses no area, so there
    is nothing for an overlap test to test.
    """
    out = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        out.append('  (fp_line (start %.3f %.3f) (end %.3f %.3f) (stroke '
                   '(width 0.05) (type solid)) (layer "%s"))\n'
                   % (ax, ay, bx, by, layer))
    return out


def _pad_row(n, pitch, sx, sy):
    out = []
    x0 = -(n - 1) * pitch / 2.0
    for i in range(n):
        out.append('  (pad "%d" smd roundrect (at %.4f 0) (size %.2f %.2f) '
                   '(layers "F.Cu" "F.Mask" "F.Paste") '
                   '(roundrect_rratio 0.2))\n'
                   % (i + 1, x0 + i * pitch, sx, sy))
    return out, x0


# ==========================================================================
# THE PATTERNS
# ==========================================================================
def _tooth_depth():
    """Solve the tooth depth so the element is EXACTLY a quarter wave.

    Set by hand at 0.88 mm first, which gave 24.056 mm against a 24.491 mm
    target - 0.435 mm short, which is 1.8 % of the length and therefore
    about 1.8 % of the resonant frequency, or 44 MHz. Half the ISM band. A
    dimension that has to hit a number is solved for, not estimated and left.

    Bisection on the path length, because the relation between depth and
    length is not quite linear: a tooth replaces some arc as well as adding
    two radial runs.
    """
    lo, hi = 0.0, ANT_TOOTH_MAX
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if path_length_mm(element_path(mid)) < QUARTER_MM:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def element_path(depth=None):
    """The 2.4 GHz element as (radius, angle) waypoints — A MEANDER, not an arc.

    WHY IT MEANDERS, and the number that forced it. openEMS solved the first
    geometry - a plain arc plus an inward fold, 20.71 mm of conductor sized
    for an assumed eps_eff of 2.2 - and returned a series resonance of
    2.886 GHz against a 2.400-2.4835 GHz target. The same run reported
    eps_eff_implied = 1.573. A thinner board with its ground plane cleared
    away holds less field in the substrate than the textbook figure assumes,
    so the quarter wave is LONGER than 20.71 mm:

        c / (4 x 2.44 GHz x sqrt(1.573)) = 24.49 mm

    That is 3.78 mm more conductor than the first attempt and there is
    nowhere to put it as arc: 84 degrees at R11.90 is 17.45 mm and the
    keying notches take everything past that. The radial direction has about
    1 mm before the element would sit over the NFC winding.

    So the element MEANDERS. Four teeth, each reaching inward by a depth
    SOLVED so the whole path is exactly the quarter wave - see
    _tooth_depth(), which bisects rather than estimating, because 0.435 mm
    of error here is 44 MHz of resonance and half the ISM band.
    A meander is not free - it couples to itself and radiates a little less
    efficiently than a straight run of the same length - and that cost is
    real and unmeasured here. It is still the only way this length fits this
    board, and the alternative (accepting 2.886 GHz) is not an antenna.

    Returns waypoints in (radius_mm, angle_deg); board.py turns them into
    tracks and make_rf_specs.py into a staircase, so there is one path.
    """
    depth = globals().get("ANT_TOOTH_DEPTH") if depth is None else depth
    if depth is None:
        raise RuntimeError("element_path() needs a depth before "
                           "ANT_TOOTH_DEPTH is solved")
    arc_deg = ANT_ARC_MAX_DEG
    pts = [(ANT_R, 0.0)]
    # Teeth are spread over the arc, each one an inward excursion and back.
    for k in range(ANT_TEETH):
        a = arc_deg * (k + 0.5) / ANT_TEETH
        w = arc_deg / (ANT_TEETH * 3.0)          # the tooth's angular width
        pts.append((ANT_R, a - w / 2.0))
        pts.append((ANT_R - depth, a - w / 2.0))
        pts.append((ANT_R - depth, a + w / 2.0))
        pts.append((ANT_R, a + w / 2.0))
    pts.append((ANT_R, arc_deg))
    return pts


def path_length_mm(pts):
    """The conductor length of a (radius, angle) path, arcs measured as arcs."""
    total = 0.0
    for (r0, a0), (r1, a1) in zip(pts, pts[1:]):
        if abs(r1 - r0) < 1e-9:
            total += abs(math.radians(a1 - a0)) * r0      # an arc
        elif abs(a1 - a0) < 1e-9:
            total += abs(r1 - r0)                         # a radial run
        else:
            x0, y0 = r0 * math.cos(math.radians(a0)), r0 * math.sin(math.radians(a0))
            x1, y1 = r1 * math.cos(math.radians(a1)), r1 * math.sin(math.radians(a1))
            total += math.hypot(x1 - x0, y1 - y0)
    return total


def batt_contact():
    """Three lands where the sprung C5191 fingers meet the board.

    SPEC.md §4: "no coin-cell holder fits" — the lowest-profile surface-mount
    retainer stands 2 mm above the board and the stack has about 1.5 mm. So
    the cell is held by fingers insert-moulded into lane M's carrier, and the
    board's job is three solder lands under their roots. Pad 1 is the
    positive finger that carries current, pad 3 the positive finger that only
    senses (rev A D-5), pad 2 the negative return.

    AUTHORED FRONT-SIDE, which is KiCad's convention for every footprint in
    every library, and it is not cosmetic: `Board.place(side="bottom")` calls
    Flip(), and Flip() on a footprint already declared B.Cu is a no-op the
    kernel accepts silently — cepcb catches that and refuses, which is how it
    was found. Flipping mirrors X, so the authored spokes 90/210/330 land at
    90/330/210. The three spokes are identical, so which pad number sits on
    which is this file's free choice; what is NOT free is that they move, and
    they are printed both ways.
    """
    order = [("1", SPOKE_ANGLES[0]), ("3", SPOKE_ANGLES[1]),
             ("2", SPOKE_ANGLES[2])]
    body = ['(footprint "HALO_BATT_CONTACT_3PAD"\n',
            '  (version 20240108)\n  (generator "halo/footprints.py")\n',
            '  (layer "F.Cu")\n',
            '  (descr "halo CR2032 three sprung-finger lands. Source: %s. '
            'Pad 1 = P+ current, pad 2 = P- return, pad 3 = P+ sense (rev A '
            'D-5). Authored F.Cu and PLACED side=bottom, because the cell '
            'sits below the board.")\n' % SRC,
            '  (tags "halo cr2032 sprung contact no-holder")\n',
            '  (attr smd exclude_from_pos_files)\n']
    for num, ang in order:
        a = math.radians(ang)
        x, y = R_SPRING_ARC * math.cos(a), -R_SPRING_ARC * math.sin(a)
        # ROTATION IS ang + 90, NOT ang, and the difference is 1.2 mm of
        # copper in the wrong direction. A pad at position angle t has its
        # radius along (cos t, -sin t) in KiCad's Y-down frame; a pad rotated
        # by phi has its LONG axis along (cos phi, -sin phi). Setting
        # phi = t therefore points the 2.40 mm strip RADIALLY, so each land
        # spanned R10.4 to R12.8 instead of R11.0 to R12.2 - into the NFC
        # winding on one side and to within 0.35 mm of the routed edge on the
        # other. Measured, from the DRC's own coordinates: "Pad 3 of BT1
        # @r11.60/150deg" shorting "Track [NFC1] @r10.75/148deg", and a board
        # edge clearance of 0.3478 mm against a 0.5 mm rule. Tangential is
        # phi = t + 90.
        body.append('  (pad "%s" smd roundrect (at %.4f %.4f %.1f) '
                    '(size %.4f %.4f) (layers "F.Cu" "F.Mask" "F.Paste") '
                    '(roundrect_rratio 0.15))\n'
                    % (num, x, y, ang + 90.0, W_SPRING, PAD_RADIAL))
    # COURTYARD: three small rectangles, one per land, and NOT the Ø26.4
    # circle drawn here first. A courtyard is "the area this part occupies,
    # that nothing else may occupy", and a circle enclosing the whole board
    # claimed all of it — KiCad's DRC dutifully reported every other part on
    # the board overlapping it, 28 violations that were entirely an artefact
    # of the drawing. The cell outline is still shown, on F.Fab, where it
    # informs a reviewer without forbidding anything.
    for num, ang in order:
        a = math.radians(ang)
        cx, cy = R_SPRING_ARC * math.cos(a), -R_SPRING_ARC * math.sin(a)
        hw, hh = W_SPRING / 2.0 + 0.15, PAD_RADIAL / 2.0 + 0.15
        ca, sa = math.cos(-a - math.pi / 2.0), math.sin(-a - math.pi / 2.0)
        rect = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh), (-hw, -hh)]
        body.extend(_courtyard([(cx + px * ca - py * sa,
                                 cy + px * sa + py * ca) for px, py in rect]))
    body.append('  (fp_circle (center 0 0) (end 10.0 0) (stroke (width 0.10) '
                '(type dash)) (fill none) (layer "F.Fab"))\n')
    body.append('  (fp_text user "CR2032 O20, 0.578 mm below this face" '
                '(at 0 6.0) (layer "F.Fab") (effects (font (size 0.6 0.6) '
                '(thickness 0.1))))\n')
    body.append(')\n')
    return "".join(body)


def antenna_2g4():
    """AE1 — the 2.4 GHz element's FEED LAND. The element itself is tracks.

    WHY THE ELEMENT IS NOT IN THIS FOOTPRINT, after two attempts to put it
    here. A custom pad is the only footprint construct that is both an
    arbitrary shape and on a net, and KiCad refuses this one by name:

        "Padstack is not valid (custom pad shape must resolve to a single
         polygon)"

    A 20 mm arc of 0.6 mm trace is a long thin ribbon; its primitive and the
    anchor rect do not overlap into one polygon, so the padstack is invalid
    and the DRC falls back to something disc-like that shorted against every
    pad inside R10.9 — L1, C11, X1 and eight of the SoC's own. Attempt two,
    footprint graphics on a copper layer, strokes correctly but carries no
    net, so the DRC demanded clearance between the antenna and its own feed.

    A TRACK is the construct KiCad has for exactly this: arbitrary shape, on
    a net, plotted as copper. So the element is drawn in board.py with
    `Board.track()` on ANT_FEED, from the geometry in THIS file
    (ANT_R, ANT_W, ANT_ARC_MAX_DEG, QUARTER_MM), which board.py imports
    rather than re-derives. One source, two consumers.

    WHY A MONOPOLE AND NOT AN INVERTED-F, which is what the AirTag uses and
    what SPEC.md §3 records at -3.2 dBi. An inverted-F is one piece of copper
    galvanically joined to BOTH the feed and the ground plane, which KiCad's
    connectivity would call a short. All of the monopole's tuning lives in
    the pi network the schematic carries for the purpose (D-2).

    WHY IT IS BENT, and this is the real finding. A quarter wave at 2.44 GHz
    in an eps_eff of 2.2 is 20.71 mm; as an arc at R11.90 that is 99.7
    degrees, and the three keying notches leave 84 usable. A STRAIGHT ARC
    QUARTER WAVE DOES NOT FIT — short by 15.7 degrees, 3.26 mm of conductor —
    so the element turns inward to make it up. An element short of a quarter
    wave resonates HIGH, and high is the direction ce-rf's two existing cases
    already failed in (4.0 and 5.8 GHz against 2.44). That does not prove it
    is the cause; it does mean length is the first thing to check.
    """
    body = ['(footprint "HALO_ANT_2G4_FEED"\n',
            '  (version 20240108)\n  (generator "halo/footprints.py")\n',
            '  (layer "F.Cu")\n',
            '  (descr "halo 2.4 GHz antenna FEED LAND. The radiating element '
            'is drawn as TRACKS by board.py from this file geometry - a '
            'custom pad cannot hold a long thin arc (KiCad: custom pad shape '
            'must resolve to a single polygon). Bent quarter wave, %.2f mm '
            'total at eps_eff %.1f, NOT TUNED.")\n' % (QUARTER_MM, EPS_EFF),
            '  (tags "halo antenna 2g4 monopole feed")\n',
            '  (attr smd exclude_from_pos_files exclude_from_bom)\n',
            '  (pad "1" smd roundrect (at 0 0) (size %.2f %.2f) '
            '(layers "F.Cu" "F.Mask") (roundrect_rratio 0.2))\n'
            % (ANT_W, ANT_W),
            '  (fp_text user "AE1 feed" (at 0 -0.9) (layer "F.Fab") '
            '(effects (font (size 0.4 0.4) (thickness 0.06))))\n']
    body.extend(_courtyard([(-0.45, -0.45), (0.45, -0.45), (0.45, 0.45),
                            (-0.45, 0.45), (-0.45, -0.45)]))
    body.append(')\n')
    return "".join(body)


# THE NFC COIL HAS NO FOOTPRINT HERE. It uses KiCad's own
# `NetTie:NetTie-2_SMD_Pad0.5mm`, placed mid-winding, with the two halves of
# the coil drawn as TRACKS on NFC1 and NFC2 by board.py.
#
# A coil is a short circuit at DC and KiCad is right to say so; a net tie is
# the construct that means "these two nets are deliberately joined by this
# piece of metal", and KiCad ships twelve of them. Writing a bespoke one was
# tried and failed for the same reason the antenna's did - a 3-turn winding
# is not a single polygon, so the padstack is invalid. Using the stock part
# also means the winding is ordinary track copper that the DRC, the Gerber
# plotter and a human reviewer all already understand.
#
# The geometry lives here (NFC_R_OUT, NFC_W, NFC_GAP, NFC_TURNS) and board.py
# imports it, so there is one source for it.


def piezo_pads():
    """LS1 — two solder lands for the bender's flying leads.

    D11a bonds a bare Murata 7BB-20-3 to the INSIDE OF THE SHELL, not to the
    board, so the board's part in it is two lands: one for the brass shim's
    lead and one for the PZT face's. 1.2 x 0.8 mm is solderable for 32 AWG
    wire, and 2.0 mm apart the two leads cannot bridge.

    THE PART ITSELF IS NOT SOURCED. research/05 §11.7 and the factory lane
    both return CANNOT DETERMINE at every quantity: the 7BB-20-3 is in
    neither LCSC nor the assembly catalogue, Digi-Key answers 403 and Mouser
    a captcha. The land pattern is deliberately generic — ANY Ø20 mm
    two-terminal bender lands on it — so a substitute costs no board spin.
    """
    body = ['(footprint "HALO_PIEZO_LEADS_2"\n',
            '  (version 20240108)\n  (generator "halo/footprints.py")\n',
            '  (layer "F.Cu")\n',
            '  (descr "halo piezo bender leads: two wire lands for a O20 mm '
            'two-terminal bender bonded to the shell (DECISIONS.md D11a). '
            'GENERIC ON PURPOSE - the Murata 7BB-20-3 is unsourced at every '
            'quantity, so any O20 bender must land here without a respin. '
            'The bender is NOT mounted on the board.")\n',
            '  (tags "halo piezo bender wire land generic")\n',
            '  (attr smd exclude_from_pos_files)\n']
    for n, x in (("1", -1.0), ("2", 1.0)):
        body.append('  (pad "%s" smd roundrect (at %.2f 0) (size 1.20 0.80) '
                    '(layers "F.Cu" "F.Mask" "F.Paste") '
                    '(roundrect_rratio 0.2))\n' % (n, x))
    body.append('  (fp_text user "LS1 bender" (at 0 -1.1) (layer "F.Fab") '
                '(effects (font (size 0.5 0.5) (thickness 0.08))))\n')
    body.extend(_courtyard([(-1.9, -0.7), (1.9, -0.7), (1.9, 0.7),
                            (-1.9, 0.7), (-1.9, -0.7)]))
    body.append(')\n')
    return "".join(body)


def test_pad():
    """A Ø0.80 mm probe land — because KiCad's is too big for this board.

    `TestPoint:TestPoint_Pad_D1.0mm` is a 1.0 mm pad inside a 2.05 x 2.05 mm
    courtyard, so it claims a 1.45 mm circumradius. Eleven of those plus two
    fiducials do not fit on the top face of a Ø26 mm disc that already
    carries 34 passives, an antenna, a coil and two land rows: the placer
    searched the whole board and REFUSED five of them.

    The answer is not to drop the test points - the production test lane
    needs every one, and stage two probes this board before the shell is
    bonded and seals them in forever. The answer is that a 26 mm product
    gets a 26 mm fixture. A 0.80 mm land takes a 0.5 mm pogo tip with
    0.15 mm of registration error to spare, which is inside what the two
    fiducials buy, and its courtyard is 1.10 mm square - a 0.78 mm
    circumradius instead of 1.45.
    """
    body = ['(footprint "HALO_TP_D0.8"\n',
            '  (version 20240108)\n  (generator "halo/footprints.py")\n',
            '  (layer "F.Cu")\n',
            '  (descr "halo probe land, 0.80 mm round, for a 0.5 mm pogo '
            'tip. Smaller than KiCad TestPoint_Pad_D1.0mm because eleven of '
            'those do not fit on a O26 mm board - see the docstring.")\n',
            '  (tags "halo test point probe pad pogo")\n',
            '  (attr smd exclude_from_pos_files exclude_from_bom)\n',
            '  (pad "1" smd circle (at 0 0) (size 0.80 0.80) '
            '(layers "F.Cu" "F.Mask"))\n']
    body.extend(_courtyard([(-0.55, -0.55), (0.55, -0.55), (0.55, 0.55),
                            (-0.55, 0.55), (-0.55, -0.55)]))
    body.append(')\n')
    return "".join(body)


def nfc_tie():
    """AE2 — a net tie AS WIDE AS THE CONDUCTOR IT JOINS, and not one micron more.

    KiCad's `NetTie:NetTie-2_SMD_Pad0.5mm` is two Ø0.50 mm pads. Put one of
    those on this winding and it reaches 0.325 mm from its own centre, while
    the spiral's turn-to-turn pitch is 0.30 mm — so the tie ALWAYS touches the
    neighbouring turn, which is the other half of the coil, which is the other
    net. Measured, twice: "Items shorting two nets (nets NFC1 and NFC2)" with
    0.013 mm and 0.031 mm of air. There is no place on a 0.30 mm pitch spiral
    where a 0.50 mm pad is legal, so moving it was never going to work.

    A net tie is not a component. It is the declaration that two named nets
    are one conductor here, and its copper should be the conductor: two
    0.15 x 0.30 mm rectangles butted at the origin, 0.15 mm being NFC_W. Total
    length 0.60 mm, total width 0.15 mm — narrower than the 0.50 mm pad by a
    factor of three and exactly as wide as the trace on either side of it.

    `net_tie_pad_groups "1, 2"` is what makes KiCad's DRC allow the two nets to
    touch HERE and nowhere else. Without it this footprint is a short.
    """
    body = ['(footprint "HALO_NFC_TIE_2"\n',
            '  (version 20240108)\n  (generator "halo/footprints.py")\n',
            '  (layer "F.Cu")\n',
            '  (descr "halo NFC coil net tie: two 0.15 x 0.30 mm pads butted, '
            'the width of the winding. KiCad NetTie-2_SMD_Pad0.5mm is 0.50 mm '
            'and shorts the neighbouring turn on a 0.30 mm pitch spiral.")\n',
            '  (tags "halo net tie nfc coil")\n',
            '  (attr smd exclude_from_pos_files exclude_from_bom)\n',
            '  (pad "1" smd rect (at -0.15 0) (size 0.30 %.2f) '
            '(layers "F.Cu"))\n' % NFC_W,
            '  (pad "2" smd rect (at 0.15 0) (size 0.30 %.2f) '
            '(layers "F.Cu"))\n' % NFC_W,
            '  (net_tie_pad_groups "1, 2")\n']
    body.extend(_courtyard([(-0.32, -0.10), (0.32, -0.10), (0.32, 0.10),
                            (-0.32, 0.10), (-0.32, -0.10)]))
    body.append(')\n')
    return "".join(body)


def serial_mark():
    """M1 — the land a factory laser-marks the serial into, on the probed face.

    ASKED FOR BY THE PRODUCTION LANE, and it is not decoration: a Find My tag
    ships with a per-unit identity, and a unit that cannot be identified after
    the shell is bonded cannot be RMA'd, recalled, or matched to its own test
    record. The mark has to be machine-readable, so it needs a KNOWN, FLAT,
    UNIFORM patch of board with nothing in it - a DataMatrix laid over a
    silkscreen legend or a via tent does not decode.

    WHAT IT IS, PHYSICALLY. A 1.8 x 1.8 mm copper land with the solder mask
    OPENED over it, on F.Cu, the same face as the probe pads and the two
    fiducials - one fixture, one side, one setup. Bare plated copper under a
    fiber laser gives the contrast a DataMatrix reader needs; marking the
    solder mask instead is the other common choice and it is greener, lower
    contrast and not what this land is for. At 1.8 mm a 12x12 ECC200 symbol
    has 0.15 mm cells, which is inside what a 20 W fiber marker holds.

    ON A NET, NOT FLOATING. It is tied to GND in board.py. An isolated 3.2 mm2
    island of copper on the top face is an antenna nobody designed, and the
    zone filler would report it as isolated copper - correctly.
    """
    body = ['(footprint "HALO_SERIAL_MARK_1X8"\n',
            '  (version 20240108)\n  (generator "halo/footprints.py")\n',
            '  (layer "F.Cu")\n',
            '  (descr "halo serial mark land: 1.8 x 1.8 mm bare copper, mask '
            'opened, for a laser-marked ECC200 DataMatrix. Probed face, same '
            'side as the fiducials.")\n',
            '  (tags "halo serial mark datamatrix laser traceability")\n',
            '  (attr smd exclude_from_pos_files exclude_from_bom)\n',
            '  (pad "1" smd rect (at 0 0) (size 1.80 1.80) '
            '(layers "F.Cu" "F.Mask"))\n']
    body.extend(_courtyard([(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0),
                            (-1.0, 1.0), (-1.0, -1.0)]))
    body.append(')\n')
    return "".join(body)


def swd_pads():
    """J1 — six SWD lands, because a Tag-Connect does not fit a Ø26 mm board.

    A TC2030 was placed first, per the schematic's reasoning that pogo-pin
    pads cost no height. That is true, and it is still the reason there is no
    connector here. What is also true, and only became visible once it was on
    the board, is that the TC2030 land pattern is about 80 mm2 with TWO NPTH
    ALIGNMENT HOLES through it. On a 26 mm disc that is a sixth of the area,
    and the DRC found its holes drilled through the SoC's pads and its
    courtyard overlapping six other parts.

    Six 0.8 x 1.4 mm lands on a 1.27 mm pitch carry the same six signals in
    about 9 mm2, with no holes at all. Pin order is Tag-Connect's own, so a
    fixture built for one reads the other: 1 VDD, 2 SWDIO, 3 nRESET,
    4 SWDCLK, 5 GND, 6 SWO.
    """
    body = ['(footprint "HALO_SWD_PADS_1x06_P1.27"\n',
            '  (version 20240108)\n  (generator "halo/footprints.py")\n',
            '  (layer "F.Cu")\n',
            '  (descr "halo SWD programming lands, 6 at 1.27 mm pitch. Order '
            'follows Tag-Connect TC2030: 1 VDD, 2 SWDIO, 3 nRESET, 4 SWDCLK, '
            '5 GND, 6 SWO. No connector, no holes - a TC2030 pattern is '
            '80 mm2 with two NPTH and does not fit a O26 mm board.")\n',
            '  (tags "halo swd pogo programming lands")\n',
            '  (attr smd exclude_from_pos_files exclude_from_bom)\n']
    pads, x0 = _pad_row(6, 1.27, 0.80, 1.40)
    body.extend(pads)
    body.append('  (fp_text user "SWD" (at 0 -1.4) (layer "F.Fab") '
                '(effects (font (size 0.5 0.5) (thickness 0.08))))\n')
    hx, hy = x0 - 0.60, 1.05
    body.extend(_courtyard([(hx, -hy), (-hx, -hy), (-hx, hy), (hx, hy),
                            (hx, -hy)]))
    body.append(')\n')
    return "".join(body)


def uwb_lands():
    """J2 — the halo-uwb expansion lands of D12.

    NOT CASTELLATIONS IN REVISION A, and the change is deliberate. Plated
    half-vias have to sit ON the routed edge, which puts every one of them in
    permanent violation of copper-edge clearance: the DRC reported 16, and
    there is then no way to tell those — which are correct and intended —
    from a real edge-clearance mistake somewhere else. A check whose alarms
    you have to learn to ignore is not a check.

    So rev A uses eight ordinary SMD lands inboard of the edge. A
    daughtercard reaches them with a flex tail or pogo pins, which is what a
    stuffing option needs anyway. Edge castellation is a rev B option and it
    costs an edge-plating process step at the board house — a real decision
    with a real price, which should be made deliberately rather than
    inherited from a footprint.

    IT IS NOT A DW3110 LAND PATTERN. schematic.py X-1 gives the two measured
    reasons one is not drawn.
    """
    body = ['(footprint "HALO_UWB_LANDS_1x08_P1.00"\n',
            '  (version 20240108)\n  (generator "halo/footprints.py")\n',
            '  (layer "F.Cu")\n',
            '  (descr "halo-uwb expansion lands (DECISIONS.md D12): 8 SMD '
            'pads at 1.00 mm pitch, inboard of the edge. NOT a DW3110 land '
            'pattern - see schematic.py X-1. Castellation is a rev B option; '
            'see the docstring for why rev A does not use it.")\n',
            '  (tags "halo uwb expansion stub lands")\n',
            '  (attr smd exclude_from_pos_files exclude_from_bom)\n']
    pads, x0 = _pad_row(8, 1.00, 0.60, 1.20)
    body.extend(pads)
    body.append('  (fp_text user "UWB - not fitted" (at 0 -1.3) '
                '(layer "F.Fab") (effects (font (size 0.5 0.5) '
                '(thickness 0.08))))\n')
    hx, hy = x0 - 0.50, 0.95
    body.extend(_courtyard([(hx, -hy), (-hx, -hy), (-hx, hy), (hx, hy),
                            (hx, -hy)]))
    body.append(')\n')
    return "".join(body)


#: Solved once, at import, so every consumer sees the same element.
ANT_TOOTH_DEPTH = _tooth_depth()

def write_fp_lib_table(outdir):
    """Write the project's footprint library table beside the board.

    WHY THE PROJECT NEEDS ITS OWN. This machine has NO global KiCad footprint
    table - KiCad has never been opened interactively here, so
    ~/Library/Preferences/kicad/*/fp-lib-table does not exist. Without a
    project table, ERC and DRC cannot resolve a single footprint and report
    one warning per part.

    WHY IT IS WRITTEN AT THE END OF THE PIPELINE. `bin/sch build` writes its
    own minimal table over whatever is there - 8 libraries and no halo - so
    anything that writes this before the schematic is rebuilt is silently
    discarded. board.py calls this last.

    It lists KiCad's own 155 libraries AND halo's, so the project is
    self-contained, which is what a factory handoff wants anyway.
    """
    import glob
    root = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
    rows = ['(fp_lib_table', '  (version 7)',
            '  (lib (name "halo")(type "KiCad")'
            '(uri "${KIPRJMOD}/../halo.pretty")(options "")'
            '(descr "halo own land patterns, generated by footprints.py"))']
    for path in sorted(glob.glob(os.path.join(root, "*.pretty"))):
        n = os.path.basename(path)[:-len(".pretty")]
        rows.append('  (lib (name "%s")(type "KiCad")'
                    '(uri "${KICAD10_FOOTPRINT_DIR}/%s.pretty")'
                    '(options "")(descr ""))' % (n, n))
    rows.append(')')
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    with open(os.path.join(outdir, "fp-lib-table"), "w") as fh:
        fh.write("\n".join(rows) + "\n")
    return len(rows) - 3


PATTERNS = [
    ("HALO_BATT_CONTACT_3PAD", batt_contact),
    ("HALO_ANT_2G4_FEED", antenna_2g4),
    ("HALO_PIEZO_LEADS_2", piezo_pads),
    ("HALO_SWD_PADS_1x06_P1.27", swd_pads),
    ("HALO_TP_D0.8", test_pad),
    ("HALO_NFC_TIE_2", nfc_tie),
    ("HALO_SERIAL_MARK_1X8", serial_mark),
    ("HALO_UWB_LANDS_1x08_P1.00", uwb_lands),
]


if __name__ == "__main__":
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    # A stale .kicad_mod from an earlier name is a footprint the board can
    # still load and nobody is generating any more. Clear them out.
    keep = {n + ".kicad_mod" for n, _ in PATTERNS}
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".kicad_mod") and f not in keep:
            os.remove(os.path.join(OUT, f))
            print("removed stale", f)
    for name, fn in PATTERNS:
        with open(os.path.join(OUT, name + ".kicad_mod"), "w",
                  encoding="utf-8") as fh:
            fh.write(fn())
        print("wrote", name)

    print("\n--- from lane M, not chosen here ---")
    print("  " + SRC)
    _want = math.degrees(QUARTER_MM / ANT_R)
    print("\n--- the etched parts, computed not chosen ---")
    print("  quarter wave at %.2f GHz, eps_eff %.1f -> %.3f mm"
          % (F0 / 1e9, EPS_EFF, QUARTER_MM))
    print("  as an arc at R%.2f                    -> %.1f deg wanted"
          % (ANT_R, _want))
    print("  clear of the three keying notches     -> %.1f deg available"
          % ANT_ARC_MAX_DEG)
    if _want > ANT_ARC_MAX_DEG:
        print("  SHORT BY %.1f deg = %.2f mm -> the element is BENT INWARD "
              "by that much"
              % (_want - ANT_ARC_MAX_DEG,
                 math.radians(_want - ANT_ARC_MAX_DEG) * ANT_R))
    # %d TRUNCATED 2.106 TO "2" and (NFC_TURNS - 1) is one turn's worth of
    # pitch short of the innermost radius, so this line reported R10.42 for a
    # winding that ends at R10.118 - a report that disagreed with the copper
    # by 0.3 mm and read as agreement.
    _r_in = NFC_R_OUT - NFC_TURNS * (NFC_W + NFC_GAP)
    print("  NFC coil: %.3f turns, %.2f/%.2f mm, outer R%.3f, inner R%.3f "
          "(copper edge R%.3f vs the Ø20.0 cell can at R10.000), NET TIE 1-2"
          % (NFC_TURNS, NFC_W, NFC_GAP, NFC_R_OUT, _r_in, _r_in - NFC_W / 2))
    print("  turns raised from 2.000 for the 1.0 nF capacitor S1 could "
          "actually buy: L target %.4f uH from ce-rf's measured %.4f uH, "
          "N-squared -> %.4f turns. THE INDUCTANCE AT THIS LENGTH IS NOT "
          "MEASURED." % (NFC_TURNS_TARGET_UH, NFC_TURNS_MEASURED_UH,
                         NFC_TURNS))
    print("  NEITHER IS TUNED. ce-rf owns S11 and the coil's inductance.")

    print("\n--- contact lands, and where the flip puts them ---")
    print("  PAD_RADIAL = %.2f mm; far corner reaches R%.2f, against the "
          "notch bottom at R%.2f"
          % (PAD_RADIAL, math.hypot(R_SPRING_ARC + PAD_RADIAL / 2.0,
                                    W_SPRING / 2.0), R_PCB_NOTCH))
    for num, ang in [("1", SPOKE_ANGLES[0]), ("3", SPOKE_ANGLES[1]),
                     ("2", SPOKE_ANGLES[2])]:
        print("  pad %s authored at %5.1f deg -> lands on the %5.1f deg spoke"
              % (num, ang, (180.0 - ang) % 360.0))
