#!/usr/bin/env python3
"""check_routed — grade an autorouted board against the board it came from.

Lane B1, 2026-09-05. `route()` already re-runs KiCad's DRC on what came back,
which is the right verdict for "is this manufacturable". It is not the verdict
for **"is this still my board"**.

Two pieces of copper on halo_rev_a were computed, not drawn: the 2.4 GHz
inverted-F, whose length is a solved quarter wave, and the NFC spiral, whose
218 chords are 0.0154 % from the true involute and whose inductance sets
C24/C25. `dsnfix.py` marks both `(type protect)` in the Specctra file so
freerouting will not rip them. **A flag that says "do not touch" is not a
measurement that nothing was touched** — that is this whole repository's
standard, applied to the one tool we hand the board to wholesale.

    python3 tools/check_routed.py BEFORE.kicad_pcb AFTER.kicad_pcb \\
        [--protect ANT_FEED,NFC1,NFC2] [--json out.json] [--quiet]

Exit 0 PASS · 1 FAIL · 2 CANNOT DETERMINE.

A NOTE ON EXACTNESS, AND THE FALSE FAIL THAT PUT IT HERE. The first
version of R1 required the protected segments to be geometrically IDENTICAL,
rounded to 1 nm. On the first real routed board it reported **235 segments
lost — the whole antenna and both halves of the NFC coil** — and that was
wrong. The measured worst displacement of any protected segment was
**0.000071 mm**. Specctra's own header on this board says `(resolution um 10)`:
one integer step in the DSN and the SES is 0.1 um = 0.0001 mm, so 71 nm is
LESS THAN ONE UNIT of the format the copper travelled through. Nothing was
rerouted; the coordinates were quantised and came back.

So the match tolerance is **read from the interchange file's own resolution**
and is one unit. That is a fact about the format, not a knob — it is not
widened to make a board pass, and `--dsn` is required for R1 to be graded at
all, because a tolerance nobody can point at a source for is the defect
`docs/TOOLS-THAT-LIE.md` records as a physical law becoming a tolerance.
A false FAIL costs exactly what a false PASS costs: this one would have made
the lane revert a routing run that was correct.

The eight assertions, each with the sentence it defeats:

  R1 protected_copper_preserved  could PASS while the router rerouted the
                                 antenna and the DRC stayed green, because a
                                 rerouted antenna is still electrically
                                 connected — it just is not an antenna.
                                 Matched WITHIN ONE INTERCHANGE UNIT, not
                                 exactly: see quantisation below
  R8 protected_length_preserved  could PASS while every segment matched a
                                 neighbour and the conductor still came back
                                 a different length
  R9 antenna_arm_not_shadowed    could PASS while the router ran a signal
                                 track UNDER the 2.4 GHz arm on an inner
                                 layer. The board's own keep-out forbids
                                 pours and vias there and ALLOWS TRACKS, so
                                 this is a hole a router walks straight
                                 through, and it costs 668 MHz
  R2 protected_vias_identical    the same, for the vias inside those nets
  R3 unconnected_improved        could PASS while the router achieved nothing
                                 and the import silently wrote the old board
  R4 no_new_drc_errors           could PASS while routing traded 81 ratlines
                                 for 81 clearance errors
  R5 copper_actually_added       could PASS while the SES imported zero new
                                 segments — the shape of an import that
                                 half-failed
  R6 board_outline_unchanged     could PASS while the SES moved the Edge_Cuts,
                                 which is how a routed board comes back the
                                 wrong size
  R7 same_rules_both_sides       could FAIL because the two boards were graded
                                 against two different netclasses — measured:
                                 the same copper is 0 errors with its project
                                 beside it and 467 without
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timezone

PASS, FAIL, CD = "PASS", "FAIL", "CANNOT DETERMINE"
RANK = {PASS: 0, CD: 1, FAIL: 2}


def row(name, value, rule, why, verdict, unit=""):
    return {"name": name, "value": value, "unit": unit, "rule": rule,
            "why": why, "verdict": verdict}


def _blocks(text, tag):
    """Balanced s-expression blocks for `(tag ...)`.

    A regex that stops at the first `)` truncates a via at its `(at ...)`,
    which is how two different vias compare equal.
    """
    for m in re.finditer(r"\(%s\b" % tag, text):
        depth, i = 0, m.start()
        while i < len(text):
            c = text[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    yield text[m.start():i + 1]
                    break
            i += 1


def _num(blk, tag, n=1):
    m = re.search(r"\(%s ([-\d.]+)(?: ([-\d.]+))?\)" % tag, blk)
    if not m:
        return None
    return m.group(n)


#: `(net "GND")` is what KiCad 10 writes on a segment, but `(net 2 "GND")` and
#: a bare `(net 2)` are both legal and both appear in files this project has
#: handled. A net regex that only matched the first form did not ERROR on the
#: others — it dropped the segment into the "" bucket or out of the map
#: entirely, and copper a check cannot see is copper a check cannot grade. Found
#: 2026-09-05 when a negative-control fixture written as `(net 2 "GND")`
#: vanished and R9 reported PASS on a board with a track laid deliberately under
#: the antenna. The fixture was the malformed thing that time; the silent loss
#: was not, and `segments()` now COUNTS what it read against what is there.
NET_RE = re.compile(r'\(net\s+(?:\d+\s+)?"([^"]*)"\)|\(net\s+(\d+)\s*\)')


def _net_of(blk):
    m = NET_RE.search(blk)
    if not m:
        return None
    return m.group(1) if m.group(1) is not None else "#" + m.group(2)


def segments(text, strict=True):
    """{net: frozenset of (x0,y0,x1,y1,width,layer)} — geometry, not order.

    Rounded to 1 nm. KiCad rewrites coordinates on every save, so comparing
    the strings would report every board different from itself.

    `strict` raises if the number of segments read back differs from the number
    of `(segment` blocks in the file. A parser that silently skips what it
    cannot read reduces a check's coverage without reducing its confidence,
    which is the failure this whole repository is written against.
    """
    out, n_read = {}, 0
    for blk in _blocks(text, "segment"):
        s = re.search(r"\(start ([-\d.]+) ([-\d.]+)\)", blk)
        e = re.search(r"\(end ([-\d.]+) ([-\d.]+)\)", blk)
        w = re.search(r"\(width ([-\d.]+)\)", blk)
        lay = re.search(r'\(layer "([^"]*)"', blk)
        if not (s and e):
            continue
        n_read += 1
        key = (round(float(s.group(1)), 6), round(float(s.group(2)), 6),
               round(float(e.group(1)), 6), round(float(e.group(2)), 6),
               round(float(w.group(1)), 6) if w else None,
               lay.group(1) if lay else None)
        out.setdefault(_net_of(blk) or "", set()).add(key)
    n_blocks = len(re.findall(r"\(segment\b", text))
    if strict and n_read != n_blocks:
        raise ValueError(
            "read %d segment(s) out of %d `(segment` block(s) in the file. "
            "The %d that did not parse are copper this check cannot see, and a "
            "check that silently covers less than it claims is worse than one "
            "that fails." % (n_read, n_blocks, n_blocks - n_read))
    return {k: frozenset(v) for k, v in out.items()}


def vias(text):
    out = {}
    for blk in _blocks(text, "via"):
        at = re.search(r"\(at ([-\d.]+) ([-\d.]+)\)", blk)
        sz = re.search(r"\(size ([-\d.]+)\)", blk)
        dr = re.search(r"\(drill ([-\d.]+)\)", blk)
        if not at:
            continue
        key = (round(float(at.group(1)), 6), round(float(at.group(2)), 6),
               round(float(sz.group(1)), 6) if sz else None,
               round(float(dr.group(1)), 6) if dr else None)
        out.setdefault(_net_of(blk) or "", set()).add(key)
    return {k: frozenset(v) for k, v in out.items()}


def edge_cuts(text):
    """Every Edge_Cuts primitive's coordinates, as one frozenset."""
    keys = set()
    for tag in ("gr_line", "gr_arc", "gr_circle", "gr_poly"):
        for blk in _blocks(text, tag):
            if '"Edge.Cuts"' not in blk:
                continue
            keys.add(tuple(round(float(x), 6)
                           for x in re.findall(r"[-\d]+\.\d+", blk)))
    return frozenset(keys)


def interchange_tolerance_mm(dsn_or_ses):
    """One integer step of the Specctra file, in mm. -> (mm, why)

    `(resolution um 10)` means the unit is the micrometre and there are 10
    steps to it, so one step is 0.1 um = 0.0001 mm. Copper that goes out
    through this file and comes back is quantised to that grid, and a check
    that demands more precision than the format carries reports every routed
    board as destroyed.
    """
    p = pathlib.Path(dsn_or_ses)
    if not p.is_file():
        return None, f"no interchange file at {p}"
    m = re.search(r"\(resolution\s+(\w+)\s+([\d.]+)\)", p.read_text(errors="replace"))
    if not m:
        return None, f"{p.name} declares no (resolution ...)"
    unit, steps = m.group(1).lower(), float(m.group(2))
    per_unit_mm = {"um": 1e-3, "mm": 1.0, "mil": 0.0254, "inch": 25.4,
                   "cm": 10.0}.get(unit)
    if per_unit_mm is None or steps <= 0:
        return None, f"{p.name} declares (resolution {unit} {steps}), which is not a length"
    return per_unit_mm / steps, f"{p.name}: (resolution {unit} {steps:g}) = one step is {per_unit_mm / steps:g} mm"


def _match(seg, pool, tol):
    """The pool segment that is `seg` moved by less than `tol`, or None.

    Same layer and same width required exactly — those are not quantised the
    way coordinates are, and a 0.127 mm route standing in for a 0.6 mm feed is
    not the same conductor. Endpoints are compared both ways round because
    nothing promises the round trip keeps a segment's direction.
    """
    best, bestd = None, None
    for c in pool:
        if c[5] != seg[5] or c[4] != seg[4]:
            continue
        fwd = max(abs(c[0] - seg[0]), abs(c[1] - seg[1]),
                  abs(c[2] - seg[2]), abs(c[3] - seg[3]))
        rev = max(abs(c[2] - seg[0]), abs(c[3] - seg[1]),
                  abs(c[0] - seg[2]), abs(c[1] - seg[3]))
        d = min(fwd, rev)
        if bestd is None or d < bestd:
            best, bestd = c, d
    return (best, bestd) if (bestd is not None and bestd <= tol) else (None, bestd)


#: The smallest in-plane gap between the 2.4 GHz arm and foreign copper that
#: lane T3 has actually solved and found acceptable: the Ø25.2 mm NFC coil at
#: 0.30 mm from the arm resonates at 2.4321 GHz, in band. The same coil placed
#: UNDER the arm drags it to 1.7666 GHz — a 668 MHz shift T3 states is not
#: recoverable by tuning. So 0.30 mm is a MEASURED floor, not a guess, and
#: anything closer than it has never been solved.
ANT_MIN_GAP_MM = 0.30

#: The antenna's OWN conductors. schematic.py:487-490,517 gives the chain
#: U1.31 -> RF_ANT -> RF_A -> RF_B -> RF_50 -> L10 -> ANT_FEED -> AE1.1: the
#: pi/L matching network arrives AT the feed, so its copper is near the arm by
#: construction and counting it as an intruder makes this check cry wolf on
#: the one board it was written for. ce-rf's own model draws the same line —
#: "the feed tap and any copper past the short are NOT in" the resonant arm.
#: Everything not on this list is foreign copper and is graded.
ANT_OWN_NETS = ("ANT_FEED", "RF_ANT", "RF_A", "RF_B", "RF_50")

#: THE ARM IS NOT THE WHOLE NET, and grading it as if it were produced a false
#: FAIL on the first board that had a routed feed. `ANT_FEED` also carries the
#: run from L10 out to the element's tap, which the autorouter draws at the
#: NETCLASS width — measured 2026-09-05: 37 segments at 0.600 mm forming the
#: radiator at theta 20-104 deg, and 2 at 0.127 mm running out at theta 254-259
#: deg, 150 degrees away. R9 reported the coil 0.0262 mm from "the arm" when
#: what it was near was that feed run. ce-rf's own model draws the same line in
#: its own words: "the feed tap and any copper past the short are NOT in" the
#: resonant arm. So the arm is the copper drawn at the ELEMENT'S OWN width, and
#: the split is reported on every run so a change in it cannot pass unseen.
ANT_ARM_WIDTH_MM = 0.60
ANT_GAP_WHY = ("lane T3, 2026-09-05: the Ø25.2 mm coil at a 0.30 mm gap solves "
               "to 2.4321 GHz in band; the same coil under the arm solves to "
               "1.7666 GHz, a 668 MHz shift that is not recoverable by tuning")


def _seg_seg_mm(a, b):
    """Minimum distance between two 2-D segments, in mm. Plan view, any layer.

    Plan view on purpose. Coupling between the arm and copper beneath it is
    vertical through 0.6 mm of FR4; a check that only looked at the same layer
    would miss exactly the case that costs 668 MHz.
    """
    def d_pt_seg(px, py, x0, y0, x1, y1):
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        if L2 == 0:
            return ((px - x0) ** 2 + (py - y0) ** 2) ** 0.5
        u = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / L2))
        return ((px - x0 - u * dx) ** 2 + (py - y0 - u * dy) ** 2) ** 0.5
    return min(d_pt_seg(a[0], a[1], b[0], b[1], b[2], b[3]),
               d_pt_seg(a[2], a[3], b[0], b[1], b[2], b[3]),
               d_pt_seg(b[0], b[1], a[0], a[1], a[2], a[3]),
               d_pt_seg(b[2], b[3], a[0], a[1], a[2], a[3]))


def _seglen(s):
    return ((s[2] - s[0]) ** 2 + (s[3] - s[1]) ** 2) ** 0.5


def drc(pcb, project=None):
    """kicad-cli's own DRC on this file. -> (report, error)

    `project` is not a convenience. KiCad takes its netclass from the
    `.kicad_pro` beside the board, and falls back to its OWN defaults (0.2 mm
    clearance, 0.6 mm via) when there is none. halo_rev_a routes at 0.127 mm,
    so the same copper graded without its project reports **467 errors instead
    of 0** — measured 2026-09-05 by running this check on the board against a
    byte-identical copy of itself, which is what a negative control is for.
    A routed board almost always lands in a temp directory, so this is the
    normal case, not the corner case: the project is copied beside it and the
    fact is recorded in the report.
    """
    pcb = pathlib.Path(pcb)
    borrowed = None
    own_pro = pcb.with_suffix(".kicad_pro")
    if project and not own_pro.exists():
        own_pro.write_text(pathlib.Path(project).read_text())
        borrowed = str(project)
    out = pcb.with_suffix(".checkrouted.drc.json")
    r = subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json",
                        "--severity-all", "--output", str(out), str(pcb)],
                       capture_output=True, text=True)
    if not out.exists():
        return None, (r.stderr or r.stdout or "")[:300]
    d = json.loads(out.read_text())
    v = d.get("violations") or []
    return {"violations": len(v),
            "errors": sum(1 for x in v if x.get("severity") == "error"),
            "warnings": sum(1 for x in v if x.get("severity") == "warning"),
            "unconnected": len(d.get("unconnected_items") or []),
            "by_type": sorted({x.get("type") for x in v}),
            "project": str(own_pro) if own_pro.exists() else None,
            "project_borrowed_from": borrowed}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--protect", default="ANT_FEED,NFC1,NFC2",
                    help="comma-separated nets whose copper must be unchanged")
    ap.add_argument("--arm-width", type=float, default=ANT_ARM_WIDTH_MM,
                    help="the radiating element's own trace width, in mm. Only "
                         "ANT_FEED copper AT THIS WIDTH is graded as the arm; "
                         "the feed run is drawn at the netclass width and is "
                         "not the radiator")
    ap.add_argument("--dsn", help="the .dsn or .ses the copper travelled "
                                  "through. Its (resolution ...) IS the match "
                                  "tolerance for the protected nets; without "
                                  "it R1 and R8 are CANNOT DETERMINE")
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    bp, ap_ = pathlib.Path(a.before), pathlib.Path(a.after)
    for p in (bp, ap_):
        if not p.is_file():
            print(f"CANNOT DETERMINE: {p} is not a file", file=sys.stderr)
            return 2
    bt, at = bp.read_text(errors="replace"), ap_.read_text(errors="replace")
    prot = [n for n in a.protect.split(",") if n]
    rows = []

    # ---- R1 protected_copper_preserved / R8 protected_length_preserved --
    bs, as_ = segments(bt), segments(at)
    tol, tolwhy = (None, "no --dsn given")
    if a.dsn:
        tol, tolwhy = interchange_tolerance_mm(a.dsn)
    if tol is None:
        for nm in ("protected_copper_preserved", "protected_length_preserved"):
            rows.append(row(nm, None, {},
                            f"the match tolerance must come from the interchange "
                            f"file's own (resolution ...) and it could not: "
                            f"{tolwhy}. Copper that went through Specctra is "
                            f"quantised to that grid; demanding more precision "
                            f"than the format carries reports every routed board "
                            f"as destroyed, and inventing a tolerance instead is "
                            f"how a limit stops meaning anything", CD, "mm"))
    else:
        lost, worst, matched_len_b, matched_len_a, extra = {}, 0.0, 0.0, 0.0, {}
        for n in prot:
            b, c = bs.get(n, frozenset()), as_.get(n, frozenset())
            used = set()
            for s in b:
                m, d = _match(s, [x for x in c if x not in used], tol)
                if d is not None:
                    worst = max(worst, d) if m is not None else worst
                if m is None:
                    lost[n] = lost.get(n, 0) + 1
                else:
                    used.add(m)
                    matched_len_b += _seglen(s)
                    matched_len_a += _seglen(m)
            if len(c) - len(used):
                extra[n] = len(c) - len(used)
        n_in = sum(len(bs.get(n, ())) for n in prot)
        rows.append(row(
            "protected_copper_preserved", round(worst, 7), {"lte": tol},
            (f"all {n_in} segment(s) on {', '.join(prot)} came back, each within "
             f"{worst * 1e6:.0f} nm of where it was sent — under the {tol * 1e6:.0f} nm "
             f"the format can carry ({tolwhy})"
             + (f". {sum(extra.values())} segment(s) ADDED on those nets "
                f"({extra}) — the router extending a protected net to reach its "
                f"pads, which is routing, not rerouting" if extra else ""))
            if not lost else
            (f"THE ROUTER CHANGED COPPER IT WAS TOLD NOT TO TOUCH. Segments with "
             f"no match within {tol * 1e6:.0f} nm, per net: {lost}. These shapes "
             f"were solved (a quarter-wave element, an involute spiral); a "
             f"rerouted one is still electrically connected and is no longer the "
             f"thing that was simulated"),
            PASS if not lost else FAIL, "mm worst displacement"))
        d_len = abs(matched_len_a - matched_len_b)
        # One quantisation step per endpoint, per matched segment: the most the
        # grid can move a length without anything having been redrawn.
        budget = 2 * tol * max(1, sum(len(bs.get(n, ())) for n in prot))
        rows.append(row("protected_length_preserved", round(d_len, 7),
                        {"lte": round(budget, 7)},
                        f"the matched conductor is {matched_len_b:.4f} mm going out "
                        f"and {matched_len_a:.4f} mm coming back, a difference of "
                        f"{d_len * 1e6:.0f} nm against a quantisation budget of "
                        f"{budget * 1e6:.0f} nm (two grid steps per segment). The "
                        f"NFC coil's inductance and the element's resonance are "
                        f"both functions of this length"
                        + ("" if d_len <= budget else
                           " — MORE THAN QUANTISATION CAN EXPLAIN"),
                        PASS if d_len <= budget else FAIL, "mm"))

    # ---- R2 protected_vias_identical ------------------------------------
    bv, av = vias(bt), vias(at)
    vlost = {n: len(bv.get(n, frozenset()) - av.get(n, frozenset()))
             for n in prot if bv.get(n, frozenset()) - av.get(n, frozenset())}
    rows.append(row("protected_vias_identical", sum(vlost.values()), {"eq": 0},
                    f"every via on {', '.join(prot)} is still where it was "
                    f"({sum(len(bv.get(n, ())) for n in prot)} via(s))"
                    if not vlost else f"vias removed from protected nets: {vlost}",
                    PASS if not vlost else FAIL, "vias lost"))

    # ---- R5 copper_actually_added ---------------------------------------
    bs, as_ = segments(bt), segments(at)
    nb = sum(len(v) for v in bs.values())
    na = sum(len(v) for v in as_.values())
    nvb = sum(len(v) for v in bv.values())
    nva = sum(len(v) for v in av.values())
    rows.append(row("copper_actually_added", na - nb, {"gt": 0},
                    f"{nb} segment(s) + {nvb} via(s) in, {na} + {nva} out: "
                    f"{na - nb:+d} segments, {nva - nvb:+d} vias"
                    + ("" if na > nb else
                       " — THE IMPORT ADDED NOTHING. An SES that imports zero "
                       "copper looks exactly like a router that had nothing to "
                       "do, and on a board with unrouted nets it is neither"),
                    PASS if na > nb else FAIL, "segments"))

    # ---- R6 board_outline_unchanged -------------------------------------
    eb, ea = edge_cuts(bt), edge_cuts(at)
    rows.append(row("board_outline_unchanged", len(eb ^ ea), {"eq": 0},
                    f"Edge.Cuts identical: {len(eb)} primitive(s)"
                    if eb == ea else
                    f"THE OUTLINE MOVED: {len(eb - ea)} primitive(s) gone, "
                    f"{len(ea - eb)} new. A routed board that came back a "
                    f"different shape is scrap, and the DRC would not say so",
                    PASS if eb == ea else FAIL, "primitives changed"))

    # ---- R3 unconnected_improved / R4 no_new_drc_errors ------------------
    # The BEFORE board's project is the rule set both sides are graded by.
    # Grading two boards against two different netclasses answers nothing.
    pro = bp.with_suffix(".kicad_pro")
    pro = str(pro) if pro.exists() else None
    db, eb_err = drc(bp, project=pro)
    da, ea_err = drc(ap_, project=pro)
    if db is None or da is None:
        for nm in ("unconnected_improved", "no_new_drc_errors"):
            rows.append(row(nm, None, {}, f"kicad-cli DRC did not run: "
                                          f"{eb_err or ea_err}", CD))
    else:
        rows.append(row("unconnected_improved",
                        db["unconnected"] - da["unconnected"],
                        {"gt": 0},
                        f"unconnected items {db['unconnected']} -> "
                        f"{da['unconnected']}"
                        + ("" if da["unconnected"] < db["unconnected"] else
                           " — the router did not connect anything it had not "
                           "already"),
                        PASS if da["unconnected"] < db["unconnected"] else FAIL,
                        "items closed"))
        rows.append(row("no_new_drc_errors", da["errors"] - db["errors"],
                        {"lte": 0},
                        f"DRC errors {db['errors']} -> {da['errors']} "
                        f"(warnings {db['warnings']} -> {da['warnings']}, "
                        f"types {da['by_type']})"
                        + ("" if da["errors"] <= db["errors"] else
                           " — routing traded ratlines for rule breaches, "
                           "which is not progress"),
                        PASS if da["errors"] <= db["errors"] else FAIL,
                        "new errors"))

    # ---- R7 same_rules_both_sides ---------------------------------------
    pb = (db or {}).get("project")
    pa = (da or {}).get("project")
    same = bool(pb and pa)
    rows.append(row("same_rules_both_sides", None, {},
                    f"both boards graded with a .kicad_pro beside them"
                    + (f"; the AFTER board borrowed "
                       f"{pathlib.Path((da or {}).get('project_borrowed_from') or '').name}"
                       if (da or {}).get("project_borrowed_from") else "")
                    if same else
                    "at least one board was graded with NO .kicad_pro beside "
                    "it, so KiCad used its own default netclass and the two "
                    "DRC numbers are not comparable",
                    PASS if same else CD))

    # ---- R9 antenna_arm_not_shadowed ------------------------------------
    ant = list(as_.get("ANT_FEED", frozenset()))
    arm = [s for s in ant if s[4] is not None
           and abs(s[4] - a.arm_width) < 1e-6]
    feed = [s for s in ant if s not in arm]
    if not arm:
        rows.append(row("antenna_arm_not_shadowed", None, {},
                        f"no ANT_FEED copper at the element width "
                        f"{a.arm_width} mm on the routed board "
                        f"({len(ant)} ANT_FEED segment(s) exist at other widths), "
                        f"so there is no arm to grade. A board that lost its "
                        f"antenna is a different problem, which R1 grades", CD, "mm"))
    else:
        worstd, offender = None, None
        av_ = vias(at)
        per_net = {}
        for net, segs in as_.items():
            if net in ANT_OWN_NETS or net == "":
                continue
            for s in segs:
                for aseg in arm:
                    d = _seg_seg_mm(s, aseg) - (s[4] or 0) / 2.0 - (aseg[4] or 0) / 2.0
                    if worstd is None or d < worstd:
                        worstd, offender = d, (net, s[5], round(s[0], 3), round(s[1], 3))
                    if net not in per_net or d < per_net[net]:
                        per_net[net] = d
        for net, vs in av_.items():
            if net in ANT_OWN_NETS:
                continue
            for v in vs:
                for aseg in arm:
                    d = (_seg_seg_mm((v[0], v[1], v[0], v[1]), aseg)
                         - (v[2] or 0) / 2.0 - (aseg[4] or 0) / 2.0)
                    if worstd is None or d < worstd:
                        worstd, offender = d, (net + " (via)", "all", round(v[0], 3), round(v[1], 3))
                    if net not in per_net or d < per_net[net]:
                        per_net[net] = d
        ok = worstd is not None and worstd >= ANT_MIN_GAP_MM
        rows.append(row("antenna_arm_not_shadowed", round(worstd, 4),
                        {"gte": ANT_MIN_GAP_MM},
                        (f"the closest foreign copper to the 2.4 GHz arm "
                         f"({len(arm)} segment(s) at {a.arm_width} mm; "
                         f"{len(feed)} further ANT_FEED segment(s) are the feed "
                         f"run and are NOT the radiator), IN PLAN VIEW ACROSS "
                         f"ALL LAYERS, is {worstd:.4f} mm — net "
                         f"{offender[0]} on {offender[1]} at ({offender[2]}, "
                         f"{offender[3]}). Floor is {ANT_MIN_GAP_MM} mm: {ANT_GAP_WHY}")
                        if ok else
                        (f"COPPER IS SHADOWING THE 2.4 GHz ARM at {worstd:.4f} mm, "
                         f"under the {ANT_MIN_GAP_MM} mm floor: net {offender[0]} on "
                         f"{offender[1]} at ({offender[2]}, {offender[3]}). The "
                         f"board's own keep-out forbids pours and vias in the "
                         f"antenna sector and ALLOWS TRACKS, so a router walks "
                         f"straight through it. {ANT_GAP_WHY}. Closest per net: "
                         + ", ".join("%s %+.4f" % (n, d) for n, d in
                                     sorted(per_net.items(), key=lambda kv: kv[1])[:5])),
                        PASS if ok else FAIL, "mm"))

    verdict = max((r["verdict"] for r in rows), key=lambda v: RANK[v])
    counts = {v: sum(1 for r in rows if r["verdict"] == v)
              for v in (PASS, FAIL, CD)}
    out = {"$halo": 1, "tool": "tools/check_routed.py",
           "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "before": str(bp.resolve()), "after": str(ap_.resolve()),
           "protected_nets": prot,
           "interchange_file": a.dsn,
           "drc_before": db, "drc_after": da,
           "verdict": verdict, "counts": counts, "rows": rows}
    if not a.quiet:
        print(f"# check_routed — {ap_.name} against {bp.name}")
        for r in rows:
            print(f"  {r['verdict']:<5} {r['name']:<28} "
                  f"{str(r['value']):>8} {r['unit']:<16} {r['why']}")
        print(f"{verdict}: {counts[PASS]} pass, {counts[FAIL]} fail, "
              f"{counts[CD]} cannot determine")
    if a.json:
        pathlib.Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.json).write_text(json.dumps(out, indent=1) + "\n")
    return {PASS: 0, FAIL: 1, CD: 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
