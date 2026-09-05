"""halo Replica — THE BUILDABLE BRANCH. A board you can order and populate.

    ce-pcb/bin/pcb ce-designs/halo/electronics/halo_replica/fab/board_fab.py

THIS IS NOT THE METROLOGY RECORD. `pcb/` holds that: Apple's 25 mm annulus at
0.30 mm with wafer-scale packages at measured positions, 0 nets and 0 tracks,
because it is a transcription of photographs and not a circuit.

THIS IS THE OTHER BRANCH, AND THE FORK IS REAL RATHER THAN A COMPROMISE:
Apple's WLCSP-50 FITS the ~6 mm annular ring and CANNOT BE LANDED, because no
complete ball map for it has ever been published. The QFN-48 is the same die,
CAN be landed, and is 6x6 mm — which does not fit that ring. There is no
arrangement that is both. A person holding a board that works but is the wrong
shape should not have to work out why.

So the outline here is a Ø30 mm DISC — inside an AirTag's Ø31.9 mm shell
envelope, solid rather than annular, because a 6 mm QFN and a coin-cell holder
need the area. Every departure is recorded in fab/README.md.

The netlist is READ from out/schematic-fab/halo_replica_fab.kicad_sch and never
retyped, so copper and sheet cannot drift.
"""
import json, math, os, sys

from cepcb import Board
from cepcb.schematic import netlist_of_sch

HERE = os.path.dirname(os.path.abspath(__file__))
R    = os.path.dirname(HERE)
SCH  = os.path.join(R, "out", "schematic-fab", "halo_replica_fab.kicad_sch")
OUT  = os.path.join(HERE, "out", "halo_replica_fab.kicad_pcb")

D_BOARD = 30.0          # mm. Inside the AirTag shell envelope (31.9 mm).
R_EDGE_KEEP = 0.5       # mm of copper-free margin at the rim

if not os.path.exists(SCH):
    raise SystemExit(f"REFUSED: no fab schematic at {SCH}\n"
                     "  build it: ce-pcb/bin/sch all .../schematic/schematic_fab.py "
                     "-o .../out/schematic-fab")

nets = netlist_of_sch(SCH)
refs_in_sch = sorted({p.split(".")[0] for pins in nets.values() for p in pins})
print(f"SCHEMATIC  {len(refs_in_sch)} refs, {len(nets)} nets, "
      f"{sum(len(v) for v in nets.values())} pin connections")

# ---------------------------------------------------------------------------
# FOOTPRINTS, taken from the SHEET rather than guessed here.
# ---------------------------------------------------------------------------
# Read them from the NETLIST, which states ref/footprint/value per component in a
# flat, unambiguous form. A regex over the .kicad_sch's nested symbol blocks got 0 of
# 45 and looked like "the sheet has no footprints" rather than like a parser failure.
import re
NET = os.path.join(R, "out", "schematic-fab", "halo_replica_fab.net")
if not os.path.exists(NET):
    raise SystemExit(f"REFUSED: no netlist at {NET}")
nt = open(NET).read()
fp_of, val_of = {}, {}
for m in re.finditer(r'\(comp\s*\(ref "([^"]+)"\)(.*?)(?=\(comp\s*\(ref |\Z)', nt, re.S):
    ref, body = m.group(1), m.group(2)
    f = re.search(r'\(footprint "([^"]*)"\)', body)
    v = re.search(r'\(value "([^"]*)"\)', body)
    if f and f.group(1).strip():
        fp_of[ref] = f.group(1).strip(); val_of[ref] = v.group(1) if v else ""
print(f"FOOTPRINTS {len(fp_of)} of {len(refs_in_sch)} refs carry one (from the netlist)")
missing_fp = [r for r in refs_in_sch if r not in fp_of]
if missing_fp:
    print(f"           NO FOOTPRINT (not placed): {missing_fp}")

# ---------------------------------------------------------------------------
# PLACEMENT — by function group, on rings, with a separation refusal.
# Hand-placing into a crowded board is guesswork with a plausible face on it;
# this places by rule and REFUSES when two parts are too close, so a bad
# placement is a failure rather than a picture.
# ---------------------------------------------------------------------------
def group_of(ref):
    if ref == "U1":                          return 0      # the SoC, centre
    if ref.startswith(("X", "U")):           return 1      # crystals and other silicon
    if ref.startswith("C"):                  return 2      # decoupling / bulk
    if ref.startswith(("R", "L", "D")):      return 3
    return 4                                                # connectors, holder, misc

RINGS = {0: 0.0, 1: 5.4, 2: 8.0, 3: 10.2, 4: 12.4}

place_list = [r for r in refs_in_sch if r in fp_of]
by_group = {}
for r in place_list: by_group.setdefault(group_of(r), []).append(r)

coords = {}
for g in sorted(by_group):
    members = sorted(by_group[g]); rad = RINGS.get(g, 12.4)
    if rad == 0.0:
        coords[members[0]] = (0.0, 0.0)
        for extra in members[1:]: by_group.setdefault(1, []).append(extra)
        continue
    n = len(members)
    for i, ref in enumerate(members):
        a = 2 * math.pi * i / max(n, 1) + 0.7 * g
        coords[ref] = (rad * math.cos(a), rad * math.sin(a))

# THE BATTERY HOLDER GOES ON THE BACK, as every coin-cell design does. A Keystone
# 1060 is ~20 mm across; on a Ø30 mm board it cannot share a face with 44 other parts,
# and the first relaxation proved it - 400 iterations, 50k pushes, 127 overlaps left,
# nearly all of them against BT1. That is the solver reporting an impossible request
# rather than converging on a bad answer.
BACK_SIDE = {"BT1"}
b = Board("halo_replica_fab", diameter=D_BOARD, layers=4)

# THE THICKNESS A FABRICATOR QUOTES FROM. Without this line the board carried
# KiCad's default 1.6 mm — 5.33x the 0.30 mm the Replica is drawn to — and it
# was found by another lane sweeping every board in the tree, not by anything
# here. A default nobody overrode is not a decision; it is what survives when
# nobody looks, and it is what reaches the fab.
#
# 0.8 mm rather than 0.30 mm, and that is a DEPARTURE, not the spec:
# MEASURED 2026-09-05 in JLCPCB's live quote configurator, at 4 layers the
# Thickness row offers 0.8/1.0/1.2/1.6/2.0 and GREYS OUT 0.4 and 0.6. Clicking
# the greyed value does nothing; switching to 2 layers re-enables 0.4, so the
# disable tracks layer count and is a real constraint. This board is 4 layers,
# so 0.8 mm is the thinnest orderable — 0.50 mm from Apple, and recorded as such
# in fab/README.md's departures table.
# THE DESIGN RULES, SET RATHER THAN DEFAULTED — the same defect as the thickness.
# Nothing here called b.rules(), so the board carried KiCad's 0.20 mm minimum
# clearance. MEASURED: U4 is an LGA-12 at 0.5 mm pitch whose own pads sit
# 0.150 mm apart, so a 0.20 mm rule forbids the manufacturer's own land pattern
# and produced 12 "clearance errors" that no placement could ever fix. The rule
# was also tighter than what fab/README.md and ORDER-SETTINGS.txt tell the fab
# we need (0.09 mm), so the board was being held to a standard we do not order to.
# 0.09 mm is JLCPCB's published 4-layer minimum trace/space. This is not a check
# loosened to pass: it is the rule being set to the process we are actually
# buying, instead of a number nobody chose.
b.rules(clearance=0.09, track=0.127, via=0.6, via_drill=0.3,
        why="JLCPCB 4-layer: 0.09 mm min trace/space; vias 0.6 mm pad / 0.3 mm "
            "drill. The previous 0.20 mm was KiCad's default and forbade U4's "
            "own 0.150 mm pad gaps.")

T_BOARD = 0.8
b.thickness(T_BOARD, why="thinnest orderable at 4 layers at JLCPCB, measured "
                         "2026-09-05 in the live configurator; the Replica is "
                         "drawn to 0.30 mm, which no 4-layer process here offers")
# `at=` is in the board's own frame - origin at the corner of the bounding box,
# NOT at the disc centre. `coords` is centred on (0,0). Add the centre, or every
# part is placed hypot(15,15) = 21.21 mm away from where it was meant to go.
BCX, BCY, _BR = b.round
for ref, (x, y) in sorted(coords.items()):
    side = "bottom" if ref in BACK_SIDE else "top"   # provisional; set_side below
    if ref in BACK_SIDE: x, y = 0.0, 0.0            # centred on the back
    b.place(ref, fp_of[ref], at=(BCX + x, BCY + y), rot=0.0,
            value=val_of.get(ref, ""), side=side)

# ---------------------------------------------------------------------------
# PLACEMENT. All of it is cepcb.place.Placer now — the frame handoff, the side
# assignment, the through-hole rule, the courtyard reads and the readback
# verdict. This file used to carry 230 lines of it, and every one of the six
# defects those lines had is written up in that module's docstring.
# ---------------------------------------------------------------------------
import pcbnew as _pn
from cepcb.place import Placer

p = Placer(b)
p.rings(RINGS, group_of, refs=sorted(fp_of))
p.keep_front(lambda r: r.startswith("U") or r == "AE1")
st = p.solve(clearance=0.20, edge_keep=R_EDGE_KEEP)
print("RELAX      %(iterations)d iterations, %(pushes)d pushes; "
      "top %(top_mm2).1f mm2 / bottom %(bottom_mm2).1f mm2, "
      "%(tht)d through-hole parts collide with both faces" % st)

# THE SILKSCREEN, MADE READABLE. 45 parts on a Ø30 mm disc at KiCad's default
# 1.0 mm text produced 39 silk_overlap and 37 silk_over_copper warnings, with
# reference strings printed on top of each other. Values move to the Fab layer,
# which is documentation and is not manufactured; the value belongs in the BOM.
_silk = b.tidy_silkscreen(ref_mm=0.5)
print("SILK       %(references_resized)d references at %(ref_mm)s mm / "
      "%(thickness_mm).3f mm stroke%(_c)s, %(values_moved_to_fab)d values moved "
      "off the silkscreen to *.Fab"
      % dict(_silk, _c=(" (CLAMPED UP to the board's own %.1f mm floor - 0.5 mm "
                        "is not manufacturable)" % _silk["floor_mm"])
                    if _silk["clamped"] else ""))

print("PLACEMENT  measured from the board:")
_v, _rows = p.verify()
if _v != 0:
    raise SystemExit(_v)


# ---------------------------------------------------------------------------
# THE NETLIST, BOUND FROM THE SHEET. Never retyped.
# ---------------------------------------------------------------------------
on_board = {f.GetReference() for f in b._pcb.GetFootprints()}
bound, deferred = 0, {}
for name, pins in sorted(nets.items()):
    have = sorted(p for p in pins if p.split(".")[0] in on_board)
    miss = sorted(p for p in pins if p.split(".")[0] not in on_board)
    if miss: deferred[name] = miss
    if have:
        b.net(name, *have); bound += 1
print(f"BOUND      {bound} of {len(nets)} nets")
if deferred:
    print(f"DEFERRED   {len(deferred)} nets touch an unplaced part: "
          f"{sorted(deferred)[:6]}{' ...' if len(deferred) > 6 else ''}")

path = b.save(OUT)
print(f"\nwrote {path}")
print("NEXT: ce-pcb/bin/route " + os.path.relpath(path, "/Users/leifrydenfalk/dev/ce-workshop"))
