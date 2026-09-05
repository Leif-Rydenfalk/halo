"""halo Replica — APPLE-SHAPED AND WORKING. The synthesis branch.

    ce-pcb/bin/pcb ce-designs/halo/electronics/halo_replica/apple/board_apple.py

THIS EXISTS BECAUSE THE PROJECT HAD DECIDED IT WAS IMPOSSIBLE, and the reason it
gave was true only of a shape this board no longer has.

  pcb/  is Apple's outline MEASURED FROM PHOTOGRAPHS — an annulus, 0.30 mm,
        151 markers, and ZERO nets, tracks and vias. It is a transcription, not
        a circuit. Ordering it gives disconnected copper.
  fab/  is a board that WORKS — but a Ø30 mm disc, which is not Apple's shape.

The stated fork was: Apple's WLCSP-50 fits the annular ring and cannot be landed
(no ball map has ever been published); the QFN-48 is the same die and CAN be
landed, but is 6x6 mm and does not fit that ring. Measured, that is exactly
right — and only for the RING:

    Apple's outline    476.3 mm2, bbox 24.6624 x 24.7263 mm
    centre hole        146.0 mm2
    ANNULAR RING       5.49 mm wide
    U1 QFN-48 courtyard 7.29 mm            7.29 > 5.49, so it cannot go in a ring

BUT THE HOLE IS THERE FOR A BATTERY THIS BOARD NO LONGER CARRIES. BT1 became a
2-pin header for an off-board cell when every CR2032 holder in KiCad's library
turned out to be too big for the board (nine of nine measurable ones). With no
cell in the centre, the hole is a hole for nothing.

FILL IT AND THE CONSTRAINT DISSOLVES. Apple's exact outer profile — the 75-point
polygon carrying L2's three true arcs, four measured chords and the measured
facets — enclosing 476.3 mm2 per face, on two faces, for 368.9 mm2 of parts.

WHAT THIS IS AND IS NOT. It is Apple's MEASURED OUTLINE at Apple's MEASURED SIZE
with parts a person can buy and a fab can place, routed. It is NOT Apple's board:
the centre is solid, the packages are landable rather than wafer-scale, the
thickness is what a 4-layer process will actually build, and every value is
CHOSEN because no photograph can give a capacitance. Every departure is in
apple/README.md, which is the only honest way to ship this.
"""
import json, math, os, re, sys

from cepcb import Board
from cepcb.schematic import netlist_of_sch
from cepcb.place import Placer

HERE = os.path.dirname(os.path.abspath(__file__))
R    = os.path.dirname(HERE)
SCH  = os.path.join(R, "out", "schematic-fab", "halo_replica_fab.kicad_sch")
NET  = os.path.join(R, "out", "schematic-fab", "halo_replica_fab.net")
OUT  = os.path.join(HERE, "out", "halo_replica_apple.kicad_pcb")
OUTLINE = os.path.join(HERE, "apple_outline.json")

for need in (SCH, NET, OUTLINE):
    if not os.path.exists(need):
        raise SystemExit("REFUSED: missing %s" % need)

# THE OUTLINE IS APPLE'S, MEASURED, NOT REDRAWN. Extracted from
# pcb/out/halo_replica.kicad_pcb - the metrology record - through KiCad's own
# GetBoardPolygonOutlines, so it carries whatever that board carries and cannot
# drift from it by being retyped here.
poly = [tuple(p) for p in json.load(open(OUTLINE))]
W = max(p[0] for p in poly); H = max(p[1] for p in poly)
print(f"OUTLINE    {len(poly)} points from the metrology board, "
      f"{W:.4f} x {H:.4f} mm - APPLE'S MEASURED PROFILE")

nets = netlist_of_sch(SCH)
refs_in_sch = sorted({p.split(".")[0] for pins in nets.values() for p in pins})
print(f"SCHEMATIC  {len(refs_in_sch)} refs, {len(nets)} nets, "
      f"{sum(len(v) for v in nets.values())} pin connections")

nt = open(NET).read()
fp_of, val_of = {}, {}
for m in re.finditer(r'\(comp\s*\(ref "([^"]+)"\)(.*?)(?=\(comp\s*\(ref |\Z)', nt, re.S):
    ref, body = m.group(1), m.group(2)
    f = re.search(r'\(footprint "([^"]*)"\)', body)
    v = re.search(r'\(value "([^"]*)"\)', body)
    if f and f.group(1): fp_of[ref] = f.group(1)
    if v: val_of[ref] = v.group(1)
# CONNECTOR OVERRIDE, THIS VARIANT ONLY, AND MEASURED RATHER THAN PREFERRED.
# The fab sheet specifies 2.54 mm THROUGH-HOLE pin headers. On a Ø30 mm disc that
# is fine. On Apple's 24.66 x 24.73 mm outline it is not, and the solver said so
# in the only way it can: 25 overlapping pairs at 8000 iterations and 29 at
# 14000 - the same count at nearly twice the budget, which means finished rather
# than slow.
#
# WHY THEY COST SO MUCH: a THT part's pads pierce both faces, so its courtyard is
# spent TWICE. J1+J2+J3+BT1 are 117.3 mm2, and on both faces that is 234.6 mm2 of
# a 952.6 mm2 two-face budget - a quarter of the board for four connectors. J3
# alone is 13.79 mm long, 56% of the board's width.
#
#   1x02 2.54 THT   3.63 x  6.18 =  22.4 mm2   costs BOTH faces
#   1x05 2.54 THT   3.63 x 13.79 =  50.1 mm2   costs BOTH faces
#   1x02 1.27 SMD   7.09 x  3.63 =  25.7 mm2   one face
#   1x05 1.27 SMD   7.09 x  7.45 =  52.8 mm2   one face
#
# Almost the same area each, and half the cost, because SMD occupies one side.
# PIN COUNTS ARE UNCHANGED, so every net and every pin number is untouched and
# `sch check` still grades this board against the same sheet. This is a
# FOOTPRINT choice, which is a board decision, not a schematic one.
SMALLER_CONNECTORS = {
    "J1":  "Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left",
    "J2":  "Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left",
    "J3":  "Connector_PinHeader_1.27mm:PinHeader_1x05_P1.27mm_Vertical_SMD_Pin1Left",
    "BT1": "Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left",
}
_swapped = []
for _r, _new in SMALLER_CONNECTORS.items():
    if _r in fp_of and fp_of[_r] != _new:
        _swapped.append((_r, fp_of[_r].split(":")[-1], _new.split(":")[-1]))
        fp_of[_r] = _new
if _swapped:
    print("CONNECTORS %d swapped to 1.27 mm SMD for this variant "
          "(pin counts unchanged, nets untouched):" % len(_swapped))
    for _r, _a, _b in _swapped:
        print("             %-4s %s -> %s" % (_r, _a, _b))

print(f"FOOTPRINTS {len(fp_of)} of {len(refs_in_sch)} refs carry one (from the netlist)")

def group_of(ref):
    if ref in ("U1",): return 0
    if ref.startswith("U") or ref.startswith("X") or ref == "AE1": return 1
    if ref.startswith(("C", "R", "L", "D")): return 2
    return 3

# Rings sized to THIS board, which is smaller than the fab disc: the inscribed
# radius is ~12.33 mm, so the outermost ring must stay well inside it.
RINGS = {0: 0.0, 1: 4.2, 2: 7.4, 3: 9.6}
# THE KEEP-IN MARGIN IS BIGGER HERE THAN ON THE DISC, and for a measured reason:
# the seeding frame treats the board as a circle of the inscribed radius, and
# Apple's outline is NOT one - it has flats and facets, so a part that clears an
# imagined circle can still hang over a real chord. J1 did, by 0.3 mm2. The
# courtyard-vs-edge row catches it against the REAL polygon; this just stops the
# solver walking into it.
R_EDGE_KEEP = 1.1

b = Board("halo_replica_apple", outline=poly, layers=4,
          title="halo Replica — Apple's measured outline, landable parts")

b.rules(clearance=0.09, track=0.127, via=0.6, via_drill=0.3,
        why="JLCPCB 4-layer: 0.09 mm min trace/space; vias 0.6/0.3. The 0.45 mm "
            "via was tried on the fab board and REFUTED - 5 unconnected became "
            "11 and 0 DRC errors became 51, because 0.45/0.30 leaves 0.075 mm of "
            "annular ring.")

T_BOARD = 0.8
b.thickness(T_BOARD, why="thinnest orderable at 4 layers at JLCPCB, measured "
                         "2026-09-05 in the live configurator. Apple's board is "
                         "0.30 mm, which no 4-layer process offers.")

for ref, fpid in sorted(fp_of.items()):
    b.place(ref, fpid, at=(W / 2, H / 2), rot=0.0, value=val_of.get(ref, ""))

_silk = b.tidy_silkscreen(ref_mm=0.5)
print("SILK       %(references_resized)d refs at %(ref_mm)s mm, "
      "%(values_moved_to_fab)d values moved to *.Fab" % _silk)

p = Placer(b)
p.rings(RINGS, group_of, refs=sorted(fp_of))
# ONLY U1 AND THE ANTENNA ARE PINNED TO THE FRONT. On the Ø30 fab disc every IC
# could sit on one face; here that pinned 254.2 mm2 onto a 476.3 mm2 face and the
# relaxation could not converge (32 overlapping pairs after 6000 iterations).
# U1 stays front because it is the part everything else fans out from, and AE1
# because an antenna under a ground pour is not an antenna. Everything else is
# free to take whichever face has room.
p.keep_front(lambda r: r in ("U1", "AE1"))
st = p.solve(clearance=0.15, edge_keep=R_EDGE_KEEP, max_iter=10000)
print("RELAX      %(iterations)d iterations, %(pushes)d pushes; "
      "top %(top_mm2).1f mm2 / bottom %(bottom_mm2).1f mm2, "
      "%(tht)d through-hole" % st)

print("PLACEMENT  measured from the board:")
_v, _rows = p.verify()
if _v != 0:
    raise SystemExit(_v)

on_board = {f.GetReference() for f in b._pcb.GetFootprints()}
bound, deferred = 0, {}
for name, pins in sorted(nets.items()):
    have = sorted(q for q in pins if q.split(".")[0] in on_board)
    miss = sorted(q for q in pins if q.split(".")[0] not in on_board)
    if miss: deferred[name] = miss
    if have:
        b.net(name, *have); bound += 1
print(f"BOUND      {bound} of {len(nets)} nets"
      + (f"  ({len(deferred)} carry a pin no part on this board has)"
         if deferred else ""))
if bound != len(nets):
    print(f"NETS       REFUSED: {len(nets) - bound} net(s) bound to nothing: "
          f"{sorted(set(nets) - set(n for n in nets if any(q.split('.')[0] in on_board for q in nets[n])))[:6]}")
    raise SystemExit(1)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
b.save(OUT)
print(f"\nwrote {OUT}")
