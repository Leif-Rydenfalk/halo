"""halo's own land patterns — the two KiCad does not have, generated.

    python3 ce-designs/halo/electronics/halo_rev_a/footprints.py

Writes `electronics/halo_rev_a/halo.pretty/*.kicad_mod`. Both patterns exist
because SPEC.md and DECISIONS.md forced parts that no catalogue sells, and
the honest response to "there is no footprint for this" is to draw one from
the mechanical source, not to borrow a similar-looking one.

1. HALO_BATT_CONTACT_3PAD — where the three sprung C5191 fingers meet the
   board. SPEC.md §4: "no coin-cell holder fits", because the lowest-profile
   surface-mount retainer stands 2 mm above the board and the stack has about
   1.5 mm. So the cell is held by fingers insert-moulded into lane M's
   carrier, and the board's job is three solder lands under their roots.
   EVERY NUMBER HERE IS READ OUT OF ce-designs/halo/design.py, lane M's
   single mechanical source, and is printed by this script so a reviewer can
   diff it against that file rather than trust this one:
     R_SPRING_ARC = 11.60   mean radius of the arc cantilever = the root
     W_SPRING     =  2.40   strip width -> the pad's tangential size
     SPOKE_ANGLES = 90/210/330 deg, the three carrier spokes
   Pad 1 is the positive finger that carries current, pad 3 is the positive
   finger that only senses (rev A D-5), pad 2 is the negative return.

2. HALO_CASTELLATED_1x08_P1.00 — the halo-uwb expansion stub of D12, as
   eight plated half-vias on the board edge at 1.00 mm pitch. It is NOT a
   DW3110 land pattern and must not be mistaken for one; schematic.py X-1
   gives the two measured reasons a DW3110 pattern is not drawn.
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "halo.pretty")

# --- lane M's numbers, ce-designs/halo/design.py --------------------------
R_SPRING_ARC = 11.60
W_SPRING = 2.40
SPOKE_ANGLES = (90.0, 210.0, 330.0)
D_PCB = 26.00
SRC = ("ce-designs/halo/design.py (lane M): R_SPRING_ARC=11.60, "
       "W_SPRING=2.40, SPOKE_ANGLES=(90,210,330), D_PCB=26.00")

PAD_RADIAL = 1.60          # radial length of the land, halo's own choice:
                           # 1.6 mm gives the formed tongue a wiping landing
                           # zone wider than lane M's 0.400 mm working
                           # deflection plus the 0.250 mm detent travel.



# ==========================================================================
# THE ETCHED PARTS — an antenna, a coil and two solder lands
# ==========================================================================
# These are the three "parts" on the schematic that carry no footprint,
# because nobody sells them: AE1 is a shape in copper, AE2 is a shape in
# copper, and LS1 is a bender bonded to the shell with two flying leads.
# Drawing them as FOOTPRINTS rather than as loose tracks buys four things
# that loose tracks do not:
#   * they carry nets, so DRC checks their connectivity like any other part;
#   * they appear in the netlist compare (`bin/sch check`), so the drawing
#     and the copper are graded against each other;
#   * they export into the Gerbers as copper the fab will actually etch;
#   * and they can be dropped into somebody else's board, which is
#     GOAL.md deliverable 2 — "an embeddable block, not only a puck".
#
# The element geometry is a CUSTOM PAD (KiCad's `(options (anchor rect))`
# plus `(primitives ...)`), which is the only KiCad construct that is both
# an arbitrary shape AND on a net.

C0 = 299792458.0
F0 = 2.44e9
EPS_EFF = 2.2              # a surface trace with its reference plane cleared
                           # away is closer to the air/substrate average than
                           # to FR4's eps_r = 4.3
QUARTER_MM = (C0 / F0) * 1000.0 / math.sqrt(EPS_EFF) / 4.0

ANT_R = 12.10              # mid-annulus: R10.0 is the cell's edge, R13.0 the
                           # board's, so this is the middle of the only band
                           # with no battery under it
ANT_W = 0.60
ANT_ARC_MAX_DEG = 84.0     # what actually fits: the three 26 deg keying
                           # notches at 0/120/240 leave clear arcs of 94 deg,
                           # and 5 deg of margin at each end keeps the element
                           # off the routed edge. A quarter wave at R12.10
                           # wants 98.1 deg, so IT DOES NOT FIT AS AN ARC -
                           # which is a finding, not a nuisance, and the
                           # element is bent inward to make up the rest.
NFC_R_OUT = 12.70
NFC_W = 0.25
NFC_GAP = 0.25
NFC_TURNS = 3


def _arc_primitive(r, a0_deg, a1_deg, width, steps=64):
    """An arc as a chain of `gr_line` primitives, in the footprint's frame.

    Chained lines rather than one `gr_arc` because a custom pad's primitives
    have to close into a fillable outline, and a stroked arc does not.
    """
    out = []
    prev = None
    for i in range(steps + 1):
        t = a0_deg + (a1_deg - a0_deg) * i / steps
        a = math.radians(t)
        pt = (r * math.cos(a), -r * math.sin(a))
        if prev is not None:
            out.append('      (gr_line (start %.4f %.4f) (end %.4f %.4f) '
                       '(width %.4f) (fill none))\n'
                       % (prev[0], prev[1], pt[0], pt[1], width))
        prev = pt
    return out


def antenna_2g4():
    """AE1 — a quarter-wave BENT monopole in the cleared sector.

    WHY A MONOPOLE AND NOT AN INVERTED-F, which is what the AirTag uses and
    what SPEC.md §3 records at -3.2 dBi. An inverted-F is ONE piece of copper
    galvanically joined to BOTH the feed and the ground plane. KiCad's
    connectivity has no way to express that: two nets on one conductor is a
    short, and the usual workarounds are a net tie (which would lie about the
    ground plane) or a DRC exclusion (which switches off the check that would
    catch a real short somewhere else). A monopole is one conductor on one
    net and needs neither. All of its tuning lives in the pi network the
    schematic carries for exactly this purpose (D-2). If ce-rf measures that
    an IFA beats it by enough to be worth a net tie, the shorting stub is one
    more pad and this paragraph is the record of why it was not drawn first.

    WHY IT IS BENT, and this is the real finding. A quarter wave at 2.44 GHz
    in an eps_eff of 2.2 is 20.71 mm. As an arc at R12.10 that is 98.1
    degrees. The board's three 26-degree keying notches at 0/120/240 leave
    clear arcs of only 94 degrees, and 5 degrees of margin at each end for
    the router bit leaves 84. SO A STRAIGHT ARC QUARTER WAVE DOES NOT FIT ON
    THIS BOARD — it is short by 14.1 degrees, which is 2.98 mm of conductor.
    The element therefore runs 84 degrees around the annulus and then turns
    inward for the remaining length, which is an ordinary bent (inverted-L)
    monopole and costs a little efficiency for the fold.

    That shortfall is worth stating plainly because ce-rf's two existing
    cases resonate HIGH — 4.0 and 5.8 GHz against a 2.44 target — and an
    element short of a quarter wave is exactly what resonates high. This
    geometry does not prove that is the cause; it does mean the length is
    the first thing to check.

    THE LENGTH IS COMPUTED, NOT TUNED. Whether it resonates in band ON THIS
    BOARD, with a Ø20 mm battery can 0.578 mm below the annulus and a ground
    plane edge about 2 mm away, is ce-rf's measurement. Nothing here asserts
    it.
    """
    arc_deg = min(math.degrees(QUARTER_MM / ANT_R), ANT_ARC_MAX_DEG)
    used = math.radians(arc_deg) * ANT_R
    tail = max(0.0, QUARTER_MM - used)          # the inward fold
    body = ['(footprint "HALO_ANT_2G4_MONOPOLE"\n',
            '  (version 20240108)\n  (generator "halo/footprints.py")\n',
            '  (layer "F.Cu")\n',
            '  (descr "halo 2.4 GHz bent quarter-wave monopole on F.Cu: '
            '%.2f mm arc at R%.2f (%.1f deg) + %.2f mm inward fold = %.2f mm '
            'total. Length COMPUTED at eps_eff %.1f, NOT TUNED. A straight '
            'arc quarter wave needs %.1f deg and only %.1f deg is clear of '
            'the keying notches, which is why it is bent.")\n'
            % (used, ANT_R, arc_deg, tail, used + tail, EPS_EFF,
               math.degrees(QUARTER_MM / ANT_R), ANT_ARC_MAX_DEG),
            '  (tags "halo antenna 2g4 monopole bent etched")\n',
            '  (attr smd exclude_from_pos_files exclude_from_bom)\n']
    prim = _arc_primitive(ANT_R, 0.0, arc_deg, ANT_W)
    if tail > 0.05:
        a = math.radians(arc_deg)
        x0, y0 = ANT_R * math.cos(a), -ANT_R * math.sin(a)
        r1 = ANT_R - tail
        x1, y1 = r1 * math.cos(a), -r1 * math.sin(a)
        prim.append('      (gr_line (start %.4f %.4f) (end %.4f %.4f) '
                    '(width %.4f) (fill none))\n' % (x0, y0, x1, y1, ANT_W))
    body.append('  (pad "1" smd custom\n'
                '    (at %.4f %.4f)\n'
                '    (size %.4f %.4f)\n'
                '    (layers "F.Cu" "F.Mask")\n'
                '    (options (clearance outline) (anchor rect))\n'
                '    (primitives\n' % (ANT_R, 0.0, ANT_W, ANT_W))
    body.extend(prim)
    body.append('    )\n  )\n')
    body.append('  (fp_text user "AE1 2G4 %.1fmm bent" (at %.3f 1.6) '
                '(layer "F.Fab") (effects (font (size 0.5 0.5) '
                '(thickness 0.08))))\n' % (used + tail, ANT_R - 3.0))
    body.append(')\n')
    return "".join(body)


def nfc_coil():
    """AE2 — a 3-turn NFC loop, as a KiCad NET TIE.

    A coil is a short circuit at DC, and KiCad is right to say so. The
    construct that expresses "these two nets are deliberately joined by this
    piece of copper" is `net_tie_pad_groups`, which KiCad's DRC understands
    and which does NOT switch off shorting checks anywhere else on the board.
    Using it is the difference between telling the tool the truth and hiding
    from it.

    Three turns at %.2f mm width and %.2f mm gap, outermost at R%.2f. The
    turn count is what makes an inductance measurable at all; WHAT that
    inductance is, is ce-rf's number, and the schematic's 130 pF tuning
    capacitors depend on it (X-2).
    """ % (NFC_W, NFC_GAP, NFC_R_OUT)
    a0, a1 = 0.0, 320.0
    body = ['(footprint "HALO_NFC_COIL_3T"\n',
            '  (version 20240108)\n  (generator "halo/footprints.py")\n',
            # Authored F.Cu and PLACED side="bottom", the same rule
            # HALO_BATT_CONTACT_3PAD follows and for the same measured
            # reason: Flip() on a footprint already declared B.Cu is a
            # silent no-op. The flip mirrors X, so the winding spirals the
            # other way round - which swaps the coil's sense and nothing
            # else, because a tag antenna has no polarity to get wrong.
            '  (layer "F.Cu")\n',
            '  (descr "halo NFC coil, %d turns, %.2f mm trace / %.2f mm gap, '
            'outermost R%.2f, on B.Cu. A NET TIE: pads 1 and 2 are joined by '
            'the winding, which is what a coil is. Inductance UNMEASURED - '
            'ce-rf owns it and C24/C25 depend on it.")\n'
            % (NFC_TURNS, NFC_W, NFC_GAP, NFC_R_OUT),
            '  (tags "halo nfc coil 13.56MHz net-tie")\n',
            # `(net_tie_pad_groups ...)` is the whole net-tie declaration in
            # KiCad 10. An `allow_bridged_nets` token in `(attr ...)` was
            # tried first and KiCad's own parser REFUSED the file - measured
            # by bisecting the four combinations through FootprintLoad, which
            # returned None for every variant carrying it. A footprint that
            # does not load is a hole in the board that only the pad count
            # reveals, so it is recorded here rather than left as folklore.
            '  (attr smd exclude_from_pos_files exclude_from_bom)\n',
            '  (net_tie_pad_groups "1, 2")\n']
    prim = []
    for t in range(NFC_TURNS):
        rr = NFC_R_OUT - t * (NFC_W + NFC_GAP)
        prim.extend(_arc_primitive(rr, a0 + t * 3.0, a1 - t * 3.0, NFC_W,
                                   steps=120))
        if t + 1 < NFC_TURNS:            # the crossover into the next turn
            rn = NFC_R_OUT - (t + 1) * (NFC_W + NFC_GAP)
            aa = math.radians(a0 + t * 3.0)
            ab = math.radians(a0 + (t + 1) * 3.0)
            prim.append('      (gr_line (start %.4f %.4f) (end %.4f %.4f) '
                        '(width %.4f) (fill none))\n'
                        % (rr * math.cos(aa), -rr * math.sin(aa),
                           rn * math.cos(ab), -rn * math.sin(ab), NFC_W))
    # Pad 1 carries the whole winding; pad 2 is a land at the inner end that
    # the winding reaches, which is what makes the two a tied pair.
    a_out = math.radians(a1)
    body.append('  (pad "1" smd custom\n'
                '    (at %.4f %.4f)\n    (size %.4f %.4f)\n'
                '    (layers "F.Cu" "F.Mask")\n'
                '    (options (clearance outline) (anchor rect))\n'
                '    (primitives\n'
                % (NFC_R_OUT * math.cos(0.0), 0.0, NFC_W, NFC_W))
    body.extend(prim)
    body.append('    )\n  )\n')
    r_in = NFC_R_OUT - (NFC_TURNS - 1) * (NFC_W + NFC_GAP)
    body.append('  (pad "2" smd rect\n'
                '    (at %.4f %.4f)\n    (size 0.60 0.35)\n'
                '    (layers "F.Cu" "F.Mask" "B.Paste")\n  )\n'
                % (r_in * math.cos(a_out), -r_in * math.sin(a_out)))
    body.append(')\n')
    return "".join(body)


def piezo_pads():
    """LS1 — two solder lands for the bender's flying leads.

    D11a bonds a bare Murata 7BB-20-3 to the INSIDE OF THE SHELL, not to the
    board. So the board's part in it is two lands: one for the brass shim's
    lead and one for the PZT face's. They are 1.2 x 0.8 mm, which is a hand-
    or robot-solderable land for 32 AWG wire, and they sit 2.0 mm apart so
    the two leads cannot bridge.
    """
    body = ['(footprint "HALO_PIEZO_LEADS_2"\n',
            '  (version 20240108)\n  (generator "halo/footprints.py")\n',
            '  (layer "F.Cu")\n',
            '  (descr "halo piezo bender leads: two wire lands for a Murata '
            '7BB-20-3 bonded to the shell (DECISIONS.md D11a). The bender is '
            'NOT mounted on the board and carries no land pattern of its '
            'own.")\n',
            '  (tags "halo piezo bender wire land")\n',
            '  (attr smd exclude_from_pos_files)\n']
    for n, x in (("1", -1.0), ("2", 1.0)):
        body.append('  (pad "%s" smd roundrect (at %.2f 0) (size 1.20 0.80) '
                    '(layers "F.Cu" "F.Mask" "F.Paste") '
                    '(roundrect_rratio 0.2))\n' % (n, x))
    body.append('  (fp_text user "LS1 bender" (at 0 -1.1) (layer "F.Fab") '
                '(effects (font (size 0.5 0.5) (thickness 0.08))))\n')
    body.append(')\n')
    return "".join(body)


def sexpr_pad(n, x, y, sx, sy, rot, layers, net_note=""):
    return (
        '  (pad "%s" smd roundrect\n'
        '    (at %.4f %.4f %.1f)\n'
        '    (size %.4f %.4f)\n'
        '    (layers %s)\n'
        '    (roundrect_rratio 0.15)\n'
        '  )\n' % (n, x, y, rot, sx, sy, layers))


def batt_contact():
    """Three lands under the finger roots, on the BOTTOM copper.

    Bottom, because the cell is below the board: lane M puts the cell's top
    face at z = 4.022 and the board's bottom face at z = 4.600, so the
    fingers approach from underneath and a top-side land would need a via
    and a barrel the finger cannot reach.
    """
    body = []
    body.append('(footprint "HALO_BATT_CONTACT_3PAD"\n')
    body.append('  (version 20240108)\n  (generator "halo/footprints.py")\n')
    # AUTHORED FRONT-SIDE, which is KiCad's convention for every footprint
    # in every library, and it is not cosmetic: `Board.place(side="bottom")`
    # calls Flip(), and Flip() on a footprint already declared B.Cu is a
    # no-op the kernel accepts silently - cepcb catches that and refuses,
    # which is how this was found. Flipping MIRRORS X, so the authored
    # spokes 90/210/330 land at 90/330/210. The three spokes are identical,
    # so which pad number sits on which is this file's free choice; what is
    # NOT free is that the numbers move, and they are printed both ways.
    body.append('  (layer "F.Cu")\n')
    body.append('  (descr "halo CR2032 three sprung-finger lands. Source: %s. '
                'Pad 1 = P+ current, pad 2 = P- return, pad 3 = P+ sense '
                '(rev A D-5). BOTTOM copper: the cell sits below the board.")\n'
                % SRC)
    body.append('  (tags "halo cr2032 sprung contact no-holder")\n')
    body.append('  (attr smd exclude_from_pos_files)\n')
    # pad n -> spoke angle. 1 = current, 3 = sense, 2 = negative.
    order = [("1", SPOKE_ANGLES[0]), ("3", SPOKE_ANGLES[1]),
             ("2", SPOKE_ANGLES[2])]
    for num, ang in order:
        a = math.radians(ang)
        x = R_SPRING_ARC * math.cos(a)
        y = -R_SPRING_ARC * math.sin(a)     # KiCad y is down
        # The pad's long axis is TANGENTIAL, so rotate by the spoke angle.
        body.append(sexpr_pad(num, x, y, W_SPRING, PAD_RADIAL, ang,
                              '"F.Cu" "F.Mask" "F.Paste"'))
    # Courtyard: the annulus the fingers sweep. Drawn as a circle so a
    # reviewer sees the cell's footprint on the board, not three islands.
    body.append('  (fp_circle (center 0 0) (end %.3f 0) (stroke (width 0.05) '
                '(type solid)) (fill none) (layer "F.CrtYd"))\n'
                % (R_SPRING_ARC + PAD_RADIAL))
    body.append('  (fp_circle (center 0 0) (end 10.0 0) (stroke (width 0.10) '
                '(type dash)) (fill none) (layer "F.Fab"))\n')
    body.append('  (fp_text user "CR2032 Ø20 cell outline, 0.578 mm below" '
                '(at 0 12.6) (layer "F.Fab") (effects (font (size 0.6 0.6) '
                '(thickness 0.1))))\n')
    body.append(')\n')
    return "".join(body)


def castellated():
    """Eight plated half-vias at 1.00 mm pitch on the board edge."""
    pitch, n = 1.00, 8
    body = []
    body.append('(footprint "HALO_CASTELLATED_1x08_P1.00"\n')
    body.append('  (version 20240108)\n  (generator "halo/footprints.py")\n')
    body.append('  (layer "F.Cu")\n')
    body.append('  (descr "halo-uwb expansion stub (DECISIONS.md D12): 8 '
                'plated half-vias, 1.00 mm pitch, on the board edge. THIS IS '
                'NOT A DW3110 LAND PATTERN - see schematic.py X-1. Place so '
                'the pad centres sit ON the Edge.Cuts arc; the board house '
                'routes through them.")\n')
    body.append('  (tags "halo castellated edge uwb stub")\n')
    body.append('  (attr through_hole exclude_from_pos_files)\n')
    x0 = -(n - 1) * pitch / 2.0
    for i in range(n):
        x = x0 + i * pitch
        body.append(
            '  (pad "%d" thru_hole circle\n'
            '    (at %.4f 0)\n'
            '    (size 0.80 0.80)\n'
            '    (drill 0.50)\n'
            '    (layers "*.Cu" "*.Mask")\n'
            '    (property pad_prop_castellated)\n'
            '  )\n' % (i + 1, x))
    body.append('  (fp_text user "UWB STUB - not fitted" (at 0 -1.6) '
                '(layer "F.Fab") (effects (font (size 0.5 0.5) '
                '(thickness 0.08))))\n')
    body.append('  (fp_line (start %.3f -1.0) (end %.3f -1.0) (stroke '
                '(width 0.05) (type solid)) (layer "F.CrtYd"))\n'
                % (x0 - 0.6, x0 + (n - 1) * pitch + 0.6))
    body.append(')\n')
    return "".join(body)


if __name__ == "__main__":
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    for name, text in (("HALO_BATT_CONTACT_3PAD", batt_contact()),
                       ("HALO_CASTELLATED_1x08_P1.00", castellated()),
                       ("HALO_ANT_2G4_MONOPOLE", antenna_2g4()),
                       ("HALO_NFC_COIL_3T", nfc_coil()),
                       ("HALO_PIEZO_LEADS_2", piezo_pads())):
        path = os.path.join(OUT, name + ".kicad_mod")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote", path)
    print("\nnumbers taken from lane M, not chosen here:")
    print("  " + SRC)
    print("\n--- the etched parts, computed not chosen ---")
    print("  quarter wave at %.2f GHz, eps_eff %.1f  -> %.3f mm"
          % (F0 / 1e9, EPS_EFF, QUARTER_MM))
    _want = math.degrees(QUARTER_MM / ANT_R)
    _fit = min(_want, ANT_ARC_MAX_DEG)
    print("  as an arc at R%.2f                      -> %.1f deg wanted"
          % (ANT_R, _want))
    print("  clear of the three keying notches       -> %.1f deg available"
          % ANT_ARC_MAX_DEG)
    if _want > ANT_ARC_MAX_DEG:
        print("  SHORT BY %.1f deg = %.2f mm of conductor -> the element is "
              "BENT INWARD by that much" % (_want - _fit,
                                            math.radians(_want-_fit)*ANT_R))
    print("  NFC coil: %d turns, %.2f/%.2f mm, outer R%.2f, NET TIE 1-2"
          % (NFC_TURNS, NFC_W, NFC_GAP, NFC_R_OUT))
    print("  NEITHER IS TUNED. ce-rf owns S11 and the coil's inductance.")
    print("\nhalo's own, argued in the docstring:")
    print("  PAD_RADIAL = %.2f mm  (> 0.400 deflection + 0.250 detent)"
          % PAD_RADIAL)
    for num, ang in [("1", SPOKE_ANGLES[0]), ("3", SPOKE_ANGLES[1]),
                     ("2", SPOKE_ANGLES[2])]:
        a = math.radians(ang)
        print("  pad %s authored at %5.1f deg -> lands on the %5.1f deg "
              "spoke after the flip  (x,y = %+.3f, %+.3f, r = %.2f)"
              % (num, ang, (180.0 - ang) % 360.0,
                 R_SPRING_ARC * math.cos(a),
                 -R_SPRING_ARC * math.sin(a), R_SPRING_ARC))
