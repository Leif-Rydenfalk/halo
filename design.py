"""halo puck — the enclosure, as ONE parametric source (lane M, mechanical).

    bin/cad ce-designs/halo/design.py

WHAT THIS FILE IS. Every mechanical number in halo lives here once. The
triad folders under ce-parts/ import their builders from this file
(cad/part.py -> load_design().shell_top(...)), so a dimension is typed in
exactly one place and the shelf, the assembly, the renders and the exports
all read the same variable.

THE FRAME, and it is Apple's own. Origin on the axis of revolution at the
LOWEST POINT of the battery door's outer face; +z up toward the crown apex
at z = 7.980; +x through the 6 o'clock bayonet ledge, so D13's three
ledges sit at 0 / 120 / 240 deg (6, 10 and 2 o'clock). Millimetres and
degrees, everywhere.

WHERE THE OUTER GEOMETRY COMES FROM. The revolved profile is the ordinate
table in research/fetched/G-airtag-profile-from-dxf.md, decoded from
reference/models/airtag-classicgod/airtag_dimensions.dxf (CC BY 4.0,
Printables 629265). That DXF reproduces every callout on Apple's own
dimensional drawing to the hundredth of a millimetre, which is what makes
it a redistributable source; Apple's sheet forbids reproduction and is not
in this repo. The DXF's convention is x = radial ordinate measured INWARD
from the max diameter (radius = 15.93 - x), y = height above the datum.
Converted to (diameter, z) pairs below.

WHAT IS halo'S OWN, and why. Five things Apple's drawing does not contain,
each argued in docs/MECHANICAL.md:
  1. the wall thickness (0.80 mm on the acoustic surround, 1.20 on the
     skirt, 1.430 at the axis because the INSIDE is flat) - nobody has
     sectioned an AirTag shell;
  2. the flat internal land the piezo bonds to - conforming a Murata
     7BB-20-3 to the crown's R91.2 inner radius strains its PZT to
     0.138 %, past the ~0.1 % tensile limit of hard PZT;
  3. the bayonet: three carrier legs with inward feet at 0/120/240 deg, a
     detent ridge, and three outward tabs on the door - press AND twist,
     16 CFR 1263;
  4. the sprung contacts - no coin-cell retainer under 2 mm exists;
  5. the split of parts: the SHELL is a straight-pull moulding with no
     undercut anywhere (it is the cosmetic diaphragm), and every undercut
     - the bayonet feet - is on the CARRIER, which nobody sees.
"""
import math
import os
import sys

from cecad import *
from cecad.fits import MATERIALS, Material

# --------------------------------------------------------------------------
# Materials this design needs that ce-cad's table does not carry. Declared
# here, with the source, rather than by editing ce-cad while another session
# holds that repo open (reported as a P11 item instead).
# --------------------------------------------------------------------------
def _material(tok, density, yield_mpa, e_gpa):
    if tok not in MATERIALS:
        MATERIALS[tok] = Material(tok, density, yield_mpa, e_gpa)
    return tok

M_SHELL   = "PC"                                   # ce-cad: 1.20 g/cm3, 65 MPa, 2.4 GPa
M_CARRIER = _material("LCP_LDS", 1.61, 130, 12.0)  # Vectra E840i LDS class
M_DOOR    = _material("SS301", 7.90, 520, 193.0)   # 301 full hard, stamped
M_SPRING  = _material("C5191", 8.80, 590, 110.0)   # phosphor bronze, spring temper
M_CELL    = _material("CR2032", 2.985, None, None) # 3.0 g / 1005 mm3, Maxell datasheet
M_PZT     = _material("PZT", 7.50, None, 60.0)
M_SEAL    = _material("LSR70", 1.15, None, 0.005)  # liquid silicone, 70 Shore A

# ==========================================================================
# 1. APPLE'S PUBLISHED PROFILE  (diameter mm, z mm) — transcribed, not fitted
# ==========================================================================
# The white shell / crown: DXF SPLINE, 125 points sampled to 32, apex -> the
# underside lip. The true maximum radial ordinate in the DXF is x = -0.007
# (Ø31.874 at z = 4.339); the 32-point sample misses it, so it is inserted.
CROWN_PROFILE = [
    (0.00, 7.980), (0.66, 7.977), (1.99, 7.968), (3.32, 7.960),
    (4.64, 7.954), (5.97, 7.933), (7.30, 7.909), (8.62, 7.883),
    (9.93, 7.850), (11.26, 7.820), (12.59, 7.776), (13.90, 7.726),
    (15.22, 7.678), (16.55, 7.621), (17.86, 7.558), (19.18, 7.483),
    (20.50, 7.398), (21.81, 7.308), (23.12, 7.202), (24.42, 7.070),
    (25.71, 6.912), (26.97, 6.725), (28.21, 6.489), (29.39, 6.185),
    (30.46, 5.793), (31.30, 5.284), (31.80, 4.669),
    (31.874, 4.339),                       # the max OD, from x = -0.007
    (31.83, 4.006), (31.39, 3.379), (30.57, 2.859), (29.52, 2.453),
    (28.94, 2.290),                        # the underside lip, Ø28.94
]

# The steel battery door's outer dome: DXF SPLINE, 70 points sampled to 36.
DOOR_DOME_PROFILE = [
    (25.44, 0.880), (25.21, 0.864), (24.67, 0.826), (23.89, 0.775),
    (23.11, 0.725), (22.32, 0.677), (21.54, 0.630), (20.76, 0.585),
    (19.99, 0.541), (19.21, 0.499), (18.42, 0.459), (17.64, 0.420),
    (16.86, 0.382), (16.07, 0.346), (15.29, 0.315), (14.51, 0.287),
    (13.72, 0.260), (12.94, 0.232), (12.17, 0.203), (11.39, 0.177),
    (10.60, 0.153), (9.82, 0.130), (9.03, 0.108), (8.25, 0.088),
    (7.46, 0.073), (6.68, 0.061), (5.90, 0.050), (5.11, 0.037),
    (4.32, 0.025), (3.53, 0.016), (2.74, 0.012), (1.96, 0.010),
    (1.18, 0.008), (0.47, 0.004), (0.08, 0.001), (0.00, 0.000),
]

# ==========================================================================
# 2. THE CALLOUTS (SPEC.md §4) — every one is used, and used for something
# ==========================================================================
D_MAX          = 31.874   # max outer diameter, at Z_MAX_D
Z_MAX_D        = 4.339
H_TOTAL        = 7.980    # overall height
D_LIP          = 28.94    # shell underside lip, outer edge, at Z_PARTING
D_BORE         = 27.90    # the shell's bore: what the door assembly sits in
D_LEG          = 27.84    # the carrier's three bayonet legs, inside that bore
D_DOOR_WALL    = 25.55    # the door's cylindrical wall
D_DOOR_BAND    = 25.45    # the same wall at each end of the 0.05 chamfer
D_SEAL_BAND    = 23.11    # the carrier lip's visible band, z 1.890..2.290
D_SPEAKER_KO   = 25.75    # Apple: "DO NOT OBSTRUCT THIS AREA"
D_ANTENNA_KO   = 37.31    # Apple: no metal, above or below
CHAMFER        = 0.05     # "0.05 mm chamfer" — the drawing's edge break
Z_PARTING      = 2.290    # the shell's underside face
Z_DOOR_RIM     = 1.890    # the door wall's top edge = the bayonet bearing plane
R_CROWN_CAP    = 92.0     # the crown's outer radius of curvature (derived R92)

# ==========================================================================
# 3. halo'S OWN PARAMETERS
# ==========================================================================
# --- the shell (part:halo-shell-top) --------------------------------------
WALL_CROWN     = 0.800    # the ACOUSTIC wall: surround thickness Ø21.2..Ø25.75
WALL_SKIRT     = 1.200    # structural, outboard of the speaker keep-out
D_LAND         = 21.20    # the flat internal land the bender bonds to
DRAFT_BORE_DEG = 1.0      # mould draft on the Ø27.90 bore
Z_BORE_TOP     = 5.000    # bore -> cavity shoulder
Z_STIFFENER    = 5.710    # the step where the 1.20 skirt becomes the 0.80 surround

# --- the cell and its seat ------------------------------------------------
D_CELL         = 20.00
H_CELL         = 3.200
D_CELL_SEAT    = 19.60    # where the cell's positive can rests on the dome
T_DOOR         = 0.300    # stamped 301 stainless, halo's choice

# --- the sprung contacts (part:halo-battery-contact) ---------------------
T_SPRING       = 0.150    # C5191 stock
W_SPRING       = 2.400    # strip width
R_SPRING_ARC   = 11.60    # mean radius of the arc cantilever
A_SPRING_DEG   = 30.0     # arc subtended -> the cantilever length
R_CONTACT_POS  = 9.50     # two positive fingers, on the can's rim
R_CONTACT_NEG  = 6.00     # one negative finger, on the negative face
T_DIMPLE       = 0.100    # embossed contact dimple, tip on the cell's face
DEFLECT_NOM    = 0.400    # working deflection at the closed position
DEFLECT_DETENT = 0.250    # extra travel the detent demands to open

# --- the board ------------------------------------------------------------
D_PCB          = 26.00
T_PCB          = 0.600
PCB_NOTCH_DEG  = 26.0
R_PCB_NOTCH    = 12.60

# --- the bender (part:halo-piezo-7bb-20-3) -------------------------------
D_PIEZO        = 20.00    # Murata 7BB-20-3
T_PIEZO        = 0.220
T_PIEZO_BRASS  = 0.120
D_PIEZO_PZT    = 14.00
T_BOND         = 0.050    # structural bond line to the flat land

# --- the bayonet (D3, D13, 16 CFR 1263) ----------------------------------
N_TAB          = 3
TAB_ANGLES     = (0.0, 120.0, 240.0)          # 6, 10 and 2 o'clock
TAB_ARC_DEG    = 45.0
LEG_ARC_DEG    = 60.0
D_TAB          = 26.60    # the door's tabs, outward from the Ø25.55 wall
R_FOOT_IN      = 12.90    # the carrier foot's inner radius
R_FOOT_OUT     = 13.40    # ... and its outer radius (the bearing land)
Z_FOOT_BOT     = 1.290
DETENT_H       = 0.250    # ridge height = the press the user must apply
DETENT_ARC_DEG = 4.0
RAMP_DEG       = 12.0     # closing cam on the foot's leading edge

# --- the carrier (part:halo-carrier) -------------------------------------
D_CARRIER_OD   = 27.60
D_CARRIER_RIM  = 26.20    # PCB locating rim ID (Ø26.00 board + 0.10 clearance)
Z_DECK_BOT     = 4.270
Z_DECK_TOP     = 4.600    # the PCB seat
Z_CARRIER_TOP  = 4.900
Z_FLOOR_BOT    = 2.290
Z_FLOOR_TOP    = 2.590
D_LIP_ID       = 21.40
D_SEAL_LAND    = 24.15
Z_LIP_BOT      = 1.400
Z_SEAL_BOT     = 1.500
N_SPOKE        = 3
SPOKE_ANGLES   = (90.0, 210.0, 330.0)
W_SPOKE        = 2.400
R_SPOKE_IN     = 10.70

# --- the door seal --------------------------------------------------------
T_SEAL_FREE    = 0.500    # moulded-in-place LSR bead, free radial section
H_SEAL         = 0.350
D_DOOR_ID      = D_DOOR_WALL - 2 * T_DOOR      # 24.95

# --- FDM prototype variant ------------------------------------------------
FDM_WALL       = 1.200    # 3 perimeters at 0.4 mm
FDM_FIT        = 0.200    # opened clearance on every sliding fit
FDM_FOOT_T     = 0.600    # the feet cannot be thinner than this on FDM
FDM_DETENT_H   = 0.350


# ==========================================================================
# 4. DERIVED — computed once, never typed twice
# ==========================================================================
def z_crown(d):
    """The crown's OUTER surface height at diameter d, interpolated on
    Apple's own ordinate table. Not a fitted sphere: the table."""
    pts = CROWN_PROFILE
    if d <= pts[0][0]:
        return pts[0][1]
    for (d0, z0), (d1, z1) in zip(pts, pts[1:]):
        if d0 <= d <= d1:
            return z0 + (z1 - z0) * (d - d0) / (d1 - d0)
    return pts[-1][1]


def z_door(d):
    """The door dome's OUTER surface height at diameter d."""
    pts = list(reversed(DOOR_DOME_PROFILE))          # ascending in d
    if d <= pts[0][0]:
        return pts[0][1]
    for (d0, z0), (d1, z1) in zip(pts, pts[1:]):
        if d0 <= d <= d1:
            return z0 + (z1 - z0) * (d - d0) / (d1 - d0)
    return pts[-1][1]


Z_LAND      = round(z_crown(D_LAND) - WALL_CROWN, 4)   # 6.550
T_APEX      = round(H_TOTAL - Z_LAND, 4)               # 1.430
Z_PIEZO_TOP = round(Z_LAND - T_BOND, 4)                # 6.500
Z_PIEZO_BOT = round(Z_PIEZO_TOP - T_PIEZO, 4)          # 6.280
Z_CELL_BOT  = round(z_door(D_CELL_SEAT) + T_DOOR, 4)   # 0.822 — cell on the dome
Z_CELL_TOP  = round(Z_CELL_BOT + H_CELL, 4)            # 4.022
Z_SPRING    = round(Z_CELL_TOP + T_DIMPLE, 4)           # finger underside, compressed
DEAD_AIR    = round(Z_CELL_BOT - T_DOOR, 4)            # 0.522, the dome's sagitta
R_INNER_CAP = round(R_CROWN_CAP - WALL_CROWN, 4)       # 91.2

# the spring, from the geometry above (Euler-Bernoulli cantilever)
L_SPRING    = math.radians(A_SPRING_DEG) * R_SPRING_ARC          # mm
I_SPRING    = W_SPRING * T_SPRING ** 3 / 12.0                    # mm^4
E_SPRING    = MATERIALS[M_SPRING].youngs_gpa * 1000.0            # MPa
K_SPRING    = 3.0 * E_SPRING * I_SPRING / L_SPRING ** 3          # N/mm
F_NOM       = K_SPRING * DEFLECT_NOM                             # N per finger
F_PRESS     = K_SPRING * (DEFLECT_NOM + DEFLECT_DETENT)
SIG_NOM     = 1.5 * E_SPRING * T_SPRING * DEFLECT_NOM / L_SPRING ** 2
SIG_PRESS   = 1.5 * E_SPRING * T_SPRING * (DEFLECT_NOM + DEFLECT_DETENT) / L_SPRING ** 2

# the PZT's strain if it were conformed to the crown's inner radius: the
# reason the land is flat. Neutral axis of the brass+PZT laminate, then y/R.
_EB, _EP = 110.0, 60.0                                   # GPa
_TB, _TP = T_PIEZO_BRASS, T_PIEZO - T_PIEZO_BRASS
_NA = (_EB * _TB * _TB / 2 + _EP * _TP * (_TB + _TP / 2)) / (_EB * _TB + _EP * _TP)
PZT_STRAIN_IF_CONFORMED = (T_PIEZO - _NA) / R_INNER_CAP  # dimensionless


# ==========================================================================
# 5. PARTS
# ==========================================================================
def _sector(part, r_in, r_out, z0, z1, angle_deg, arc_deg, op="add",
            n=24):
    """An annular sector as a prism — the primitive a bayonet foot, a leg
    and a spoke are actually made of. cecad has no sector primitive."""
    a0 = math.radians(angle_deg - arc_deg / 2.0)
    a1 = math.radians(angle_deg + arc_deg / 2.0)
    pts = [(r_out * math.cos(a0 + (a1 - a0) * i / n),
            r_out * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    pts += [(r_in * math.cos(a1 - (a1 - a0) * i / n),
             r_in * math.sin(a1 - (a1 - a0) * i / n)) for i in range(n + 1)]
    part.prism(pts, z1 - z0, at=(0, 0, z0), axis="z", op=op)
    return part


def shell_top(wall=WALL_CROWN, fdm=False):
    """part:halo-shell-top — the crown, which IS the diaphragm.

    A straight-pull moulding: no undercut anywhere. The outer surface is
    Apple's ordinate table revolved; the inner surface is a FLAT LAND at
    Z_LAND over Ø21.2 (so a flat Ø20 bender can be bonded without
    cracking its ceramic), a `wall`-thick offset surround out to the
    Ø25.75 speaker keep-out, a stiffener step, and then a Ø27.90 bore
    with 1 deg of draft down to the Ø28.94 parting face at z = 2.290.
    """
    name = "halo-shell-top-fdm" if fdm else "halo-shell-top"
    p = Part(name, material=M_SHELL)
    w = FDM_WALL if fdm else wall
    land_z = round(z_crown(D_LAND) - w, 4)

    # ---- the closed revolve profile, (r, h) pairs, apex -> inside -> apex
    prof = [(0.0, H_TOTAL)]
    for d, z in CROWN_PROFILE[1:-1]:                     # outer surface, down
        prof.append((d / 2.0, z))
    prof += [(D_LIP / 2.0, Z_PARTING + CHAMFER),         # the 0.05 chamfer
             (D_LIP / 2.0 - CHAMFER, Z_PARTING),
             (D_BORE / 2.0, Z_PARTING)]                  # the parting face
    r_bore_top = D_BORE / 2.0 - (Z_BORE_TOP - Z_PARTING) * math.tan(
        math.radians(DRAFT_BORE_DEG))
    prof += [(r_bore_top, Z_BORE_TOP),                   # up the drafted bore
             (D_SPEAKER_KO / 2.0, Z_STIFFENER),          # cavity shoulder
             (D_SPEAKER_KO / 2.0, z_crown(D_SPEAKER_KO) - w)]   # stiffener step
    for d in (25.20, 24.40, 23.60, 22.80, 22.00, D_LAND):       # the surround
        prof.append((d / 2.0, round(z_crown(d) - w, 4)))
    prof.append((0.0, land_z))                           # the flat land
    p.revolve(prof, axis="z")

    # ---- what must stay empty inside it
    p.keepout("diaphragm-clearance", d=D_SPEAKER_KO, h=GAP_DIAPHRAGM,
              at=(0, 0, Z_PIEZO_BOT - GAP_DIAPHRAGM), axis="z",
              reason="Apple's Ø25.75 'DO NOT OBSTRUCT THIS AREA' as a volume: "
                     "the gap the bonded bender needs to move the crown")
    return p.clean()


def carrier():
    """part:halo-carrier — the LDS frame: the PCB seat, the three sprung
    contacts' roots, the Ø23.11 seal land, the door's bayonet feet, and the
    BLE / NFC / UWB antenna traces on its Ø27.60 outer wall.

    Every undercut in halo is on THIS part, so the cosmetic shell needs no
    side action. The three feet are formed by three lifters.
    """
    p = Part("halo-carrier", material=M_CARRIER)

    # ---- axisymmetric body: lip -> floor -> outer wall -> PCB rim
    r_id = D_LIP_ID / 2.0
    prof = [
        (r_id, Z_LIP_BOT),
        (D_SEAL_LAND / 2.0 - 0.150, Z_LIP_BOT),          # lead-in chamfer
        (D_SEAL_LAND / 2.0, Z_SEAL_BOT),
        (D_SEAL_LAND / 2.0, Z_DOOR_RIM),                 # the seal land
        (D_SEAL_BAND / 2.0, Z_DOOR_RIM),
        (D_SEAL_BAND / 2.0, Z_FLOOR_BOT),                # the Ø23.11 band
        (D_CARRIER_OD / 2.0, Z_FLOOR_BOT),               # the floor, out
        (D_CARRIER_OD / 2.0, Z_CARRIER_TOP),             # the outer wall, up
        (D_CARRIER_RIM / 2.0, Z_CARRIER_TOP),            # PCB locating rim
        (D_CARRIER_RIM / 2.0, Z_DECK_TOP),
        (D_CARRIER_OD / 2.0 - 0.600, Z_DECK_TOP),        # the PCB seat land
        (D_CARRIER_OD / 2.0 - 0.600, Z_FLOOR_TOP),       # inner face of wall
        (D_SEAL_BAND / 2.0, Z_FLOOR_TOP),                # the floor, back in
        (D_SEAL_BAND / 2.0, Z_DECK_BOT),
        (r_id, Z_DECK_BOT),                              # deck inner face
    ]
    p.revolve(prof, axis="z")

    # ---- the PCB seat deck: an outer ring plus three spokes
    _sector(p, D_CARRIER_RIM / 2.0 - 1.20, D_CARRIER_RIM / 2.0,
            Z_DECK_BOT, Z_DECK_TOP, 0.0, 360.0)
    for a in SPOKE_ANGLES:
        arc = math.degrees(W_SPOKE / R_SPOKE_IN)
        _sector(p, R_SPOKE_IN, D_CARRIER_RIM / 2.0, Z_DECK_BOT, Z_DECK_TOP,
                a, arc)

    # ---- three board-orientation ribs (the PCB's three notches key on these)
    for a in TAB_ANGLES:
        arc = math.degrees(2.0 / R_PCB_NOTCH)
        _sector(p, R_PCB_NOTCH + 0.10, D_CARRIER_RIM / 2.0,
                Z_DECK_TOP, Z_CARRIER_TOP, a, arc)

    # ---- the bayonet: three legs, each with an inward foot
    for a in TAB_ANGLES:
        _sector(p, R_FOOT_OUT, D_LEG / 2.0, Z_FOOT_BOT, Z_FLOOR_BOT,
                a, LEG_ARC_DEG)                                # the leg
        _sector(p, R_FOOT_IN, R_FOOT_OUT, Z_FOOT_BOT, Z_DOOR_RIM,
                a, LEG_ARC_DEG)                                # the foot
        _sector(p, R_FOOT_IN, R_FOOT_OUT, Z_DOOR_RIM,
                Z_DOOR_RIM + DETENT_H,
                a + TAB_ARC_DEG / 2.0 + DETENT_ARC_DEG / 2.0,
                DETENT_ARC_DEG)                                # the detent ridge
        # the closing cam: 12 deg ramp on the leading edge of the foot
        _sector(p, R_FOOT_IN - 0.05, R_FOOT_OUT + 0.05,
                Z_DOOR_RIM - math.tan(math.radians(RAMP_DEG)) * 1.5,
                Z_DOOR_RIM,
                a - LEG_ARC_DEG / 2.0 + 3.5, 8.0, op="cut")

    # the three contacts are INSERT-MOULDED: the metal displaces plastic, so
    # cut them out rather than let the checker find 0.89 mm3 of shared volume
    for reach, ang in ((R_CONTACT_POS, 60.0), (R_CONTACT_POS, 180.0),
                       (R_CONTACT_NEG, 300.0)):
        f = battery_contact(reach, ang, "cut")
        p.shape = p.shape.cut(f.shape.makeOffsetShape(0.020, 1e-3))
    return p.clean()


def battery_door(fdm=False):
    """part:halo-battery-door — stamped 301 stainless, 0.30 mm.

    R92 dome (the z datum), Ø25.55 wall with the drawing's 0.05 chamfer at
    each end, and three outward bayonet tabs at 0/120/240 deg that bear on
    the carrier's feet. Not a battery terminal: all three contacts are on
    the carrier (Catley), and the door's job is retention, clamping force
    and the radial seal face.
    """
    name = "halo-battery-door-fdm" if fdm else "halo-battery-door"
    t = FDM_WALL if fdm else T_DOOR
    p = Part(name, material=M_SHELL if fdm else M_DOOR)

    prof = [(d / 2.0, z) for d, z in reversed(DOOR_DOME_PROFILE)]   # outer dome
    prof += [
        (D_DOOR_BAND / 2.0, z_door(D_DOOR_BAND)),
        (D_DOOR_WALL / 2.0, z_door(D_DOOR_BAND) + CHAMFER),
        (D_DOOR_WALL / 2.0, Z_DOOR_RIM - CHAMFER),
        (D_DOOR_BAND / 2.0, Z_DOOR_RIM),
        (D_DOOR_WALL / 2.0 - t, Z_DOOR_RIM),                        # rim, in
        (D_DOOR_WALL / 2.0 - t, z_door(D_DOOR_BAND) + t),           # bore, down
    ]
    prof += [(d / 2.0, z + t) for d, z in DOOR_DOME_PROFILE
             if d / 2.0 <= D_DOOR_WALL / 2.0 - t]                   # inner dome
    p.revolve(prof, axis="z")

    for a in TAB_ANGLES:                                            # the tabs
        _sector(p, D_DOOR_WALL / 2.0 - 0.20, D_TAB / 2.0,
                Z_DOOR_RIM, Z_DOOR_RIM + t, a, TAB_ARC_DEG)
    return p.clean()


def battery_contact(reach=R_CONTACT_POS, angle=0.0, name=None):
    """part:halo-battery-contact — one formed C5191 finger.

    An arc cantilever of `A_SPRING_DEG` at `R_SPRING_ARC`, insert-moulded
    into a carrier spoke, ending in a tongue that reaches to `reach`. Two
    are placed on the cell's positive can rim, one on its negative face
    (Catley: 2 positive + 1 negative, all carrier-side). Drawn at the
    COMPRESSED height: the free tip is DEFLECT_NOM lower.
    """
    p = Part(name or "halo-battery-contact", material=M_SPRING)
    z0 = Z_SPRING
    arc = math.degrees(W_SPRING / R_SPRING_ARC)
    _sector(p, R_SPRING_ARC - W_SPRING / 2.0, R_SPRING_ARC + W_SPRING / 2.0,
            z0, z0 + T_SPRING, angle + A_SPRING_DEG / 2.0, A_SPRING_DEG)
    _sector(p, reach - 0.45, R_SPRING_ARC + W_SPRING / 2.0,
            z0, z0 + T_SPRING,
            angle + A_SPRING_DEG, arc)                    # the contact tongue
    p.cyl(0.90, T_SPRING + T_DIMPLE, at=(
        reach * math.cos(math.radians(angle + A_SPRING_DEG)),
        reach * math.sin(math.radians(angle + A_SPRING_DEG)),
        z0 - T_DIMPLE), axis="z")                         # the contact dimple
    return p.clean()


def pcb_blank():
    """part:halo-pcb-blank — the mechanical outline of the 4-layer board.

    Ø26.00 x 0.60 mm with three 26 deg notches at 0/120/240 deg that key on
    the carrier's ribs, so the board can only go in one way round and the
    antenna feeds land on the right LDS traces. The copper is the
    electronics lane's; this folder owns the outline and the keep-outs.
    """
    p = Part("halo-pcb-blank", material="FR4")
    p.cyl(D_PCB, T_PCB, at=(0, 0, Z_DECK_TOP), axis="z")
    for a in TAB_ANGLES:
        _sector(p, R_PCB_NOTCH, D_PCB / 2.0 + 0.5,
                Z_DECK_TOP - 0.05, Z_DECK_TOP + T_PCB + 0.05,
                a, PCB_NOTCH_DEG, op="cut")
    p.keepout("no-tall-parts-under-the-bender", d=D_LAND, h=0.400,
              at=(0, 0, Z_DECK_TOP + T_PCB), axis="z",
              reason="top-side components inside Ø21.2 are limited to 0.40 mm; "
                     "the bulk caps and the crystals go on the bottom face")
    return p.clean()


def piezo_7bb_20_3():
    """part:halo-piezo-7bb-20-3 — Murata 7BB-20-3, Ø20.0 x 0.22 mm.

    Brass shim Ø20.0 x 0.12 bonded to the shell's flat land; PZT disc
    Ø14.0 x 0.10 on the free face, driven anti-phase from two SoC pins
    (D11a). 3.6 kHz free resonance, 500 ohm.
    """
    p = Part("halo-piezo-7bb-20-3", material="BRASS")
    p.cyl(D_PIEZO, T_PIEZO_BRASS, at=(0, 0, Z_PIEZO_TOP - T_PIEZO_BRASS),
          axis="z")
    p.cyl(D_PIEZO_PZT, T_PIEZO - T_PIEZO_BRASS, at=(0, 0, Z_PIEZO_BOT),
          axis="z")
    return p.clean()


def cr2032():
    """part:halo-cr2032 — the cell. Ø20.0 x 3.2 mm, 3.0 g (Maxell)."""
    p = Part("halo-cr2032", material=M_CELL)
    p.cyl(D_CELL, H_CELL, at=(0, 0, Z_CELL_BOT), axis="z")
    return p.clean()


def door_seal():
    """part:halo-door-seal — a moulded-in-place LSR bead on the carrier's
    Ø24.15 seal land, squeezed 20 % radially by the door's Ø24.95 bore.

    Drawn INSTALLED (compressed to the 0.40 mm gap), which is why its
    section here is smaller than its free section T_SEAL_FREE.
    """
    p = Part("halo-door-seal", material=M_SEAL)
    p.tube(D_DOOR_ID, D_SEAL_LAND, H_SEAL,
           at=(0, 0, Z_SEAL_BOT + 0.020), axis="z")
    return p.clean()


# ==========================================================================
# 6. THE ASSEMBLY
# ==========================================================================
def build():
    shell   = shell_top()
    carr    = carrier()
    door    = battery_door()
    pcb     = pcb_blank()
    piezo   = piezo_7bb_20_3()
    cell    = cr2032()
    seal    = door_seal()
    cp1     = battery_contact(R_CONTACT_POS,  60.0, "halo-battery-contact-pos")
    cp2     = battery_contact(R_CONTACT_POS, 180.0, "halo-battery-contact-pos-b")
    cn1     = battery_contact(R_CONTACT_NEG, 300.0, "halo-battery-contact-neg")

    a = Assembly("halo-puck")
    # Every part is BUILT in the product frame, so every placement is the
    # identity — a concentric product has one datum and no transforms to get
    # wrong. What holds each part is declared.
    a.add("shell",       shell, color="grey",
          joint="rigid")          # the datum body
    a.add("carrier",     carr,  color="gold",
          joint="glued")          # structural adhesive in the Ø27.90 bore;
                                  # the bead is also the parting-line seal
    a.add("seal",        seal,  color="red",   joint="glued")
    a.add("door",        door,  color="steel", joint="bayonet")
    a.add("cell",        cell,  color="blue",  joint="clamped")
    a.add("contact_pos_a", cp1, color="orange", joint="glued")
    a.add("contact_pos_b", cp2, color="orange", joint="glued")
    a.add("contact_neg",   cn1, color="orange", joint="glued")
    a.add("pcb",         pcb,   color="green", joint="soldered")
    a.add("piezo",       piezo, color="purple", joint="glued")

    a.insertion("door", moves="press +z 0.25 mm and rotate 60 deg",
                direction="+z then about z",
                why="16 CFR 1263: the detent ridge blocks rotation until the "
                    "door is pressed in against the contact springs, so "
                    "opening needs two independent simultaneous movements")

    print(report_stack())
    ok = check(shell, carr, door, pcb, piezo, cell, seal, cp1, cp2, cn1, a)
    print("check() ->", ok)

    os.makedirs("out/mech", exist_ok=True)
    render(a, "out/mech/halo-puck-iso.png", view="iso", title="halo puck")
    render(a, "out/mech/halo-puck-section.png",
           section=("y", 0.0), view=view_for_section(("y", 0.0)),
           title="halo puck — the 7.98 mm stack")
    contact_sheet(shell, "out/mech/halo-shell-top.png")
    contact_sheet(carr,  "out/mech/halo-carrier.png")
    contact_sheet(door,  "out/mech/halo-battery-door.png")

    a.export_step("out/mech/halo-puck.step")
    for part in (shell, carr, door, pcb, piezo, seal, cp1, cn1,
                 shell_top(fdm=True), battery_door(fdm=True)):
        part.export_step("out/mech/%s.step" % part.name)
        part.export_stl("out/mech/%s.stl" % part.name)
    return a


def report_stack():
    """The stack budget, read off the PARAMETERS that build the solids, and
    the checks it has to pass. Printed on every build."""
    rows = [
        ("door skin at the axis (301 SS)",          0.0,          T_DOOR),
        ("dome sagitta under the cell (dead air)",  T_DOOR,       Z_CELL_BOT),
        ("CR2032",                                  Z_CELL_BOT,   Z_CELL_TOP),
        ("contact finger, compressed",              Z_CELL_TOP,   Z_CELL_TOP + T_SPRING),
        ("carrier deck: finger roots + PCB seat",   Z_CELL_TOP + T_SPRING, Z_DECK_TOP),
        ("PCB",                                     Z_DECK_TOP,   Z_DECK_TOP + T_PCB),
        ("top-side component allowance",            Z_DECK_TOP + T_PCB, Z_PIEZO_BOT - 0.680),
        ("diaphragm moving gap",                    Z_PIEZO_BOT - 0.680, Z_PIEZO_BOT),
        ("Murata 7BB-20-3 + bond line",             Z_PIEZO_BOT,  Z_LAND),
        ("PC crown wall at the axis",               Z_LAND,       H_TOTAL),
    ]
    out = ["", "STACK BUDGET (mm, on the axis, closed)",
           "  %-42s %7s %7s %7s" % ("layer", "from", "to", "dz")]
    tot = 0.0
    for label, z0, z1 in rows:
        out.append("  %-42s %7.3f %7.3f %7.3f" % (label, z0, z1, z1 - z0))
        tot += z1 - z0
    out.append("  %-42s %7s %7s %7.3f" % ("TOTAL", "", "", tot))
    out.append("  target %.3f  ->  %s" %
               (H_TOTAL, "PASS" if abs(tot - H_TOTAL) < 5e-4 else "FAIL"))
    out += ["", "DERIVED",
            "  flat land z                 %.4f  (Ø%.2f)" % (Z_LAND, D_LAND),
            "  crown wall at the axis      %.4f" % T_APEX,
            "  crown wall at the land edge %.4f" % WALL_CROWN,
            "  reclaimable dead air        %.4f" % DEAD_AIR,
            "  spring: L %.3f mm  k %.4f N/mm" % (L_SPRING, K_SPRING),
            "  spring force  nominal %.3f N/finger, %.3f N total"
            % (F_NOM, 3 * F_NOM),
            "  spring force  pressed %.3f N/finger, %.3f N total"
            % (F_PRESS, 3 * F_PRESS),
            "  spring stress nominal %.1f MPa (%.0f%% of yield)"
            % (SIG_NOM, 100 * SIG_NOM / MATERIALS[M_SPRING].yield_mpa),
            "  spring stress pressed %.1f MPa (%.0f%% of yield)"
            % (SIG_PRESS, 100 * SIG_PRESS / MATERIALS[M_SPRING].yield_mpa),
            "  PZT strain if conformed to R%.1f  %.4f %%  (limit ~0.1 %%)"
            % (R_INNER_CAP, 100 * PZT_STRAIN_IF_CONFORMED),
            ""]
    return "\n".join(out)


if __name__ == "__main__":
    build()
