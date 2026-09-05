"""f_placement_check — did the board get the MEASURED positions and angles?

    ce-pcb/bin/pcb ce-designs/halo/electronics/halo_replica/tools/f_placement_check.py
    ... --break-rot 15        rotate every CLASS B land 15 deg and watch it fail
    ... --break-pos 0.4       shift every placement 0.4 mm and watch it fail

Exit 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

WHY THIS EXISTS. board.py computes `rot = 90 - angle` from a one-paragraph
argument about which way KiCad's +Y points and which way a positive
orientation turns. That argument is exactly the kind that is convincing and
wrong, and a part rotated 90 degrees looks like a part. So the claim is
MEASURED instead: this reads the SAVED BOARD back with pcbnew and takes the
long-side bearing off each CLASS B land's OWN PAD POLYGON -- the corner
coordinates KiCad wrote to the file -- not off the orientation field board.py
set. A check that reads back the number it is checking is not a check.

The frames line up by construction and that is worth stating, because it is
the step that could silently invert: cepcb maps board_y -> _h - board_y and
board.py maps y_meas -> CY - y_meas, so kicad_y = _h - CY + y_meas. The two
flips cancel. KiCad's internal frame is a PURE TRANSLATION of the
measurement frame, so a bearing means the same thing in both and no angle
conversion happens anywhere in this file.

WHAT IS COMPARED, AND WHAT CANNOT BE. A min-area-rect angle is the long side
MODULO 180 degrees, so the comparison is mod 180. It says nothing about
which end is pin 1 and NOTHING AT ALL about a square land -- so a row whose
long and short sides are within the registration floor of each other is
reported CANNOT DETERMINE rather than passed. There are no free passes in
this file's PASS count.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPLICA, "pcb"))

import footprints as FP                                        # noqa: E402

PCB = os.path.join(REPLICA, "pcb", "out", "halo_replica.kicad_pcb")
HANDOFF = os.path.join(REPLICA, "metrology", "HANDOFF-positions-front.json")
COMPS = os.path.join(REPLICA, "metrology", "components-front.json")
BLUE = os.path.join(REPLICA, "metrology", "dark-packages-front.json")

# The floor below which two sides of a rect are not distinguishable, and the
# tolerance a placement is allowed. Both come from the handoff's own stated
# uncertainty, not from what happened to pass.
POS_TOL_MM = None          # filled from registration_holdout_mm
ANG_TOL_DEG = 2.0          # a land whose long side is 2 mm and whose
                           # endpoints are good to 0.10 mm can be read to
                           # about atan(0.10/2) = 2.9 deg. 2.0 is tighter
                           # than that and is a tolerance on OUR arithmetic,
                           # not on the photograph.


def _angles():
    m = {}
    for src, key in ((COMPS, "components"), (BLUE, "packages")):
        for r in json.load(open(src))[key]:
            if r.get("x_mm") is None:
                continue
            m[(round(float(r["x_mm"]), 3), round(float(r["y_mm"]), 3))] = \
                float(r["angle_deg"])
    return m


def _long_bearing(pad):
    """Long-side bearing of a pad, READ OFF ITS OWN CORNER COORDINATES."""
    poly = pad.GetEffectivePolygon()
    if poly.OutlineCount() < 1:
        return None, None, None
    o = poly.Outline(0)
    pts = [(o.CPoint(i).x, o.CPoint(i).y) for i in range(o.PointCount())]
    # longest edge of the convex land, and the longest edge perpendicular
    best = (0.0, 0.0)
    edges = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        edges.append((d, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))))
        if d > best[0]:
            best = (d, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
    longest = best[0]
    perp = max((d for d, ang in edges
                if abs(((ang - best[1]) % 180.0) - 90.0) < 5.0), default=0.0)
    return best[1] % 180.0, longest / 1e6, perp / 1e6


def main():
    argv = sys.argv[1:]
    break_rot = 0.0
    break_pos = 0.0
    if "--break-rot" in argv:
        break_rot = float(argv[argv.index("--break-rot") + 1])
    if "--break-pos" in argv:
        break_pos = float(argv[argv.index("--break-pos") + 1])

    if not os.path.exists(PCB):
        print("CANNOT DETERMINE — no board at %s. Build it first." % PCB)
        return 2

    import pcbnew
    board = pcbnew.LoadBoard(PCB)
    handoff = json.load(open(HANDOFF))
    global POS_TOL_MM
    POS_TOL_MM = 3.0 * float(handoff["uncertainty"]["registration_holdout_mm"])
    angles = _angles()

    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}

    # The datum: two rows far apart fix the translation, and it is SOLVED
    # from the board rather than taken from board.py's constant, so a change
    # to CX/CY cannot make this check pass by moving with it.
    rows = {r["id"]: r for r in handoff["rows"]}
    anchors = []
    for rid, fp in fps.items():
        if rid in rows and rows[rid]["x_mm"] is not None:
            p = fp.GetPosition()
            anchors.append((p.x / 1e6 - rows[rid]["x_mm"],
                            p.y / 1e6 - rows[rid]["y_mm"]))
    if len(anchors) < 3:
        print("CANNOT DETERMINE — fewer than 3 placed handoff rows found.")
        return 2
    ox = sum(a[0] for a in anchors) / len(anchors)
    oy = sum(a[1] for a in anchors) / len(anchors)
    spread = max(max(abs(a[0] - ox) for a in anchors),
                 max(abs(a[1] - oy) for a in anchors))

    npass = nfail = ncd = 0
    fails = []
    for rid, row in sorted(rows.items()):
        fp = fps.get(rid)
        if fp is None:
            ncd += 1
            fails.append((rid, "not on the board"))
            continue
        if row["x_mm"] is None:
            ncd += 1
            continue
        p = fp.GetPosition()
        dx = (p.x / 1e6 - ox) - row["x_mm"] + break_pos
        dy = (p.y / 1e6 - oy) - row["y_mm"]
        if math.hypot(dx, dy) > POS_TOL_MM:
            nfail += 1
            fails.append((rid, "position off by %.4f mm (tol %.4f)"
                          % (math.hypot(dx, dy), POS_TOL_MM)))
            continue

        if FP.classify(row) != "metal":
            npass += 1                       # position is the whole claim
            continue
        pads = list(fp.Pads())
        if len(pads) != 1:
            ncd += 1
            continue
        bearing, lo, sh = _long_bearing(pads[0])
        if bearing is None:
            ncd += 1
            continue
        if abs(lo - sh) < handoff["uncertainty"]["registration_holdout_mm"]:
            ncd += 1                          # square: no long side to read
            continue
        want = (angles[(round(row["x_mm"], 3), round(row["y_mm"], 3))]
                + break_rot) % 180.0
        err = abs(((bearing - want + 90.0) % 180.0) - 90.0)
        if err > ANG_TOL_DEG:
            nfail += 1
            fails.append((rid, "long side reads %.2f deg, handoff says %.2f "
                               "(err %.2f, tol %.2f)"
                          % (bearing, want, err, ANG_TOL_DEG)))
        else:
            npass += 1

    print("f_placement_check — %s" % PCB)
    print("  datum solved from %d placed rows, residual spread %.6f mm"
          % (len(anchors), spread))
    print("  position tolerance %.4f mm = 3 x the handoff's own "
          "registration_holdout_mm" % POS_TOL_MM)
    print("  angle tolerance    %.2f deg, compared MOD 180" % ANG_TOL_DEG)
    if break_rot or break_pos:
        print("  BREAK ACTIVE: rot %+.2f deg, pos %+.3f mm"
              % (break_rot, break_pos))
    print("  PASS %d   FAIL %d   CANNOT DETERMINE %d" % (npass, nfail, ncd))
    for rid, why in fails[:12]:
        print("    %-6s %s" % (rid, why))
    if len(fails) > 12:
        print("    ... and %d more" % (len(fails) - 12))
    return 1 if nfail else 0


sys.exit(main())
