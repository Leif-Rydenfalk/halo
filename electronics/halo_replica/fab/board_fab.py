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
    side = "bottom" if ref in BACK_SIDE else "top"
    if ref in BACK_SIDE: x, y = 0.0, 0.0            # centred on the back
    b.place(ref, fp_of[ref], at=(BCX + x, BCY + y), rot=0.0,
            value=val_of.get(ref, ""), side=side)

# ---------------------------------------------------------------------------
# COURTYARD-AWARE RELAXATION. A fixed centre-to-centre minimum is the wrong
# check: it treated a 6 mm QFN and an 0402 as the same object, and the first
# attempt produced 46 courtyard overlaps and 26 shorts. Read each part's REAL
# courtyard from the board and push overlapping pairs apart until none remain.
# ---------------------------------------------------------------------------
import pcbnew as _pn
def boxes():
    out = {}
    for fp in b._pcb.GetFootprints():
        r = fp.GetCourtyard(_pn.F_CrtYd).BBox()
        if r.GetWidth() == 0: r = fp.GetBoundingBox(False, False)
        out[fp.GetReference()] = (r.GetWidth()/1e6, r.GetHeight()/1e6)
    return out

CLEAR = 0.20            # mm of air between courtyards. JLC min trace/space is 0.09,
                        # so 0.20 mm of courtyard air is comfortable, not marginal.
R_KEEP = D_BOARD/2 - R_EDGE_KEEP
sz = boxes()
pos = {r: list(p) for r, p in coords.items() if r not in BACK_SIDE}
moved, it = 0, 0
DAMP = 0.55   # under-relax: full-step pushes made pairs oscillate past each other
for it in range(3000):
    worst = 0.0; any_push = False
    refs = sorted(pos)
    for i, r1 in enumerate(refs):
        w1, h1 = sz.get(r1, (1.0, 1.0))
        for r2 in refs[i+1:]:
            w2, h2 = sz.get(r2, (1.0, 1.0))
            dx = pos[r2][0] - pos[r1][0]; dy = pos[r2][1] - pos[r1][1]
            need_x = (w1 + w2)/2 + CLEAR; need_y = (h1 + h2)/2 + CLEAR
            ox = need_x - abs(dx); oy = need_y - abs(dy)
            if ox > 0 and oy > 0:                      # boxes overlap
                any_push = True; worst = max(worst, min(ox, oy))
                if ox < oy:
                    s_ = DAMP * (ox/2 + 1e-3) * (1 if dx >= 0 else -1)
                    pos[r1][0] -= s_; pos[r2][0] += s_
                else:
                    s_ = DAMP * (oy/2 + 1e-3) * (1 if dy >= 0 else -1)
                    pos[r1][1] -= s_; pos[r2][1] += s_
                moved += 1
    # pull everything back inside the copper keep-in
    for r in refs:
        w, h = sz.get(r, (1.0, 1.0)); lim = R_KEEP - max(w, h)/2
        d = math.hypot(*pos[r])
        if d > lim and d > 0:
            k = lim / d; pos[r][0] *= k; pos[r][1] *= k
    if not any_push: break
print(f"RELAX      {it+1} iterations, {moved} pushes, courtyard clearance {CLEAR} mm")

# THE FRAME HANDOFF. Everything above is in a frame centred on (0,0): the rings
# are radii, R_KEEP is a radius, and `math.hypot(*pos[r])` is a distance from the
# centre. The BOARD is not centred there. `Board(diameter=d)` puts the disc at
# (d/2, d/2), so a part handed its ring coordinate raw lands off the copper.
# MEASURED 2026-09-05: without this translation 33 of 45 footprints sat outside
# Edge.Cuts, and freerouting reported 106 of 111 nets unrouted with an identical
# score on four consecutive passes - it was being asked to route parts that were
# not on the board.
CX, CY, _R = b.round          # ce-pcb's own centre, not a typed-in 15.0
for r, (x, y) in pos.items():
    b.component(r).SetPosition(_pn.VECTOR2I(int((CX + x)*1e6),
                                            int(b._y(CY + y)*1e6)))
sz = boxes(); bad = []
for i, r1 in enumerate(sorted(pos)):
    w1, h1 = sz.get(r1, (1,1))
    for r2 in sorted(pos)[i+1:]:
        w2, h2 = sz.get(r2, (1,1))
        dx = abs(pos[r2][0]-pos[r1][0]); dy = abs(pos[r2][1]-pos[r1][1])
        if dx < (w1+w2)/2 and dy < (h1+h2)/2: bad.append((r1, r2))
if bad:
    print(f"PLACEMENT  REFUSED: {len(bad)} courtyard overlaps survive relaxation: {bad[:6]}")
    raise SystemExit(1)
outside = [(r, round(math.hypot(*p),2)) for r, p in pos.items() if math.hypot(*p) > R_KEEP]
if outside:
    print(f"PLACEMENT  REFUSED: outside the keep-in: {outside[:5]}"); raise SystemExit(1)

# THE SAME QUESTION ASKED OF THE ARTIFACT. The check above measures `pos`, which
# is the intermediate we just computed - it agrees with itself by construction
# and stayed green through the whole frame bug. This one reads every footprint
# POSITION BACK OUT OF THE BOARD and compares it to the REAL Edge.Cuts circle,
# so it can fail on a bad frame handoff. It is the check that would have caught
# what the one above could not.
_eb = b._pcb.GetBoardEdgesBoundingBox()
_ecx = (_eb.GetLeft() + _eb.GetRight()) / 2e6
_ecy = (_eb.GetTop() + _eb.GetBottom()) / 2e6
_er  = min(_eb.GetWidth(), _eb.GetHeight()) / 2e6
_off = []
for _fp in b._pcb.GetFootprints():
    _p = _fp.GetPosition()
    _d = math.hypot(_p.x/1e6 - _ecx, _p.y/1e6 - _ecy)
    if _d > _er:
        _off.append((_fp.GetReference(), round(_d, 2)))
if _off:
    print(f"PLACEMENT  REFUSED: {len(_off)} of {len(list(b._pcb.GetFootprints()))} "
          f"footprints read back OUTSIDE the Ø{2*_er:.2f} mm Edge.Cuts circle at "
          f"({_ecx:.2f},{_ecy:.2f}): {sorted(_off)[:6]}")
    raise SystemExit(1)
_t_read = b.board_thickness()
if abs(_t_read - T_BOARD) > 1e-6:
    print(f"THICKNESS  REFUSED: asked for {T_BOARD} mm, the board declares "
          f"{_t_read} mm. 1.6 mm means it was never set — that is KiCad's "
          f"default and it is what a fabricator would quote from.")
    raise SystemExit(1)
print(f"THICKNESS  board declares {_t_read} mm (read back from the board), "
      f"{_t_read - 0.30:+.2f} mm from the 0.30 mm the Replica is drawn to")
# CAN EACH PART EVEN FIT ON THIS BOARD? Distinct from "is it inside the
# outline": a footprint whose COURTYARD is larger than the board can never be
# placed legally no matter where it goes, and no amount of relaxation will
# report that — the solver just pushes it around forever. MEASURED: BT1's
# Keystone 1060 courtyard is 32.90 x 21.40 mm on a Ø30 mm board, so every
# through-hole pad on the board fell inside it and KiCad reported 9
# pth_inside_courtyard violations that looked like a placement problem and were
# a PART CHOICE problem.
_toobig = []
for _fp in b._pcb.GetFootprints():
    _bb = None
    for _ly in (_pn.F_CrtYd, _pn.B_CrtYd):
        _r = _fp.GetCourtyard(_ly).BBox()
        if _r.GetWidth() > 0 and (_bb is None or _r.GetWidth() > _bb[0]):
            _bb = (_r.GetWidth()/1e6, _r.GetHeight()/1e6)
    if _bb is None: continue
    _diag = math.hypot(*_bb)
    if _diag > D_BOARD:
        _toobig.append((_fp.GetReference(), round(_bb[0], 2), round(_bb[1], 2),
                        round(_diag, 2)))
if _toobig:
    print(f"FOOTPRINT  REFUSED: {len(_toobig)} part(s) have a courtyard that "
          f"cannot fit a Ø{D_BOARD} mm board at any position "
          f"(ref, w, h, diagonal): {sorted(_toobig)}")
    raise SystemExit(1)
print(f"FITS       every courtyard fits inside Ø{D_BOARD} mm")
print(f"ONBOARD    45/45 footprints read back inside Edge.Cuts "
      f"(Ø{2*_er:.2f} mm at {_ecx:.2f},{_ecy:.2f}) - measured from the board")
placed = sorted(set(pos) | BACK_SIDE)
print(f"PLACED     {len(placed)} parts on a Ø{D_BOARD} mm disc, NO courtyard overlaps")


# ---------------------------------------------------------------------------
# THE NETLIST, BOUND FROM THE SHEET. Never retyped.
# ---------------------------------------------------------------------------
on_board = set(placed)
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
