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
    body.append('  (layer "B.Cu")\n')
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
        body.append(sexpr_pad(num, x, y, W_SPRING, PAD_RADIAL, ang, '"B.Cu" "B.Mask" "B.Paste"'))
    # Courtyard: the annulus the fingers sweep. Drawn as a circle so a
    # reviewer sees the cell's footprint on the board, not three islands.
    body.append('  (fp_circle (center 0 0) (end %.3f 0) (stroke (width 0.05) '
                '(type solid)) (fill none) (layer "B.CrtYd"))\n'
                % (R_SPRING_ARC + PAD_RADIAL))
    body.append('  (fp_circle (center 0 0) (end 10.0 0) (stroke (width 0.10) '
                '(type dash)) (fill none) (layer "B.Fab"))\n')
    body.append('  (fp_text user "CR2032 Ø20 cell outline, 0.578 mm below" '
                '(at 0 12.6) (layer "B.Fab") (effects (font (size 0.6 0.6) '
                '(thickness 0.1)) (justify mirror)))\n')
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
                       ("HALO_CASTELLATED_1x08_P1.00", castellated())):
        path = os.path.join(OUT, name + ".kicad_mod")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote", path)
    print("\nnumbers taken from lane M, not chosen here:")
    print("  " + SRC)
    print("\nhalo's own, argued in the docstring:")
    print("  PAD_RADIAL = %.2f mm  (> 0.400 deflection + 0.250 detent)"
          % PAD_RADIAL)
    for num, ang in [("1", SPOKE_ANGLES[0]), ("3", SPOKE_ANGLES[1]),
                     ("2", SPOKE_ANGLES[2])]:
        a = math.radians(ang)
        print("  pad %s at %5.1f deg -> (%+.3f, %+.3f) mm, r = %.2f"
              % (num, ang, R_SPRING_ARC * math.cos(a),
                 -R_SPRING_ARC * math.sin(a), R_SPRING_ARC))
