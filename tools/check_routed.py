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

The seven assertions, each with the sentence it defeats:

  R1 protected_copper_identical  could PASS while the router rerouted the
                                 antenna and the DRC stayed green, because a
                                 rerouted antenna is still electrically
                                 connected — it just is not an antenna
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


def segments(text):
    """{net: frozenset of (x0,y0,x1,y1,width,layer)} — geometry, not order.

    Rounded to 1 nm. KiCad rewrites coordinates on every save, so comparing
    the strings would report every board different from itself.
    """
    out = {}
    for blk in _blocks(text, "segment"):
        s = re.search(r"\(start ([-\d.]+) ([-\d.]+)\)", blk)
        e = re.search(r"\(end ([-\d.]+) ([-\d.]+)\)", blk)
        w = re.search(r"\(width ([-\d.]+)\)", blk)
        lay = re.search(r'\(layer "([^"]*)"', blk)
        net = re.search(r'\(net "([^"]*)"', blk)
        if not (s and e):
            continue
        key = (round(float(s.group(1)), 6), round(float(s.group(2)), 6),
               round(float(e.group(1)), 6), round(float(e.group(2)), 6),
               round(float(w.group(1)), 6) if w else None,
               lay.group(1) if lay else None)
        out.setdefault(net.group(1) if net else "", set()).add(key)
    return {k: frozenset(v) for k, v in out.items()}


def vias(text):
    out = {}
    for blk in _blocks(text, "via"):
        at = re.search(r"\(at ([-\d.]+) ([-\d.]+)\)", blk)
        sz = re.search(r"\(size ([-\d.]+)\)", blk)
        dr = re.search(r"\(drill ([-\d.]+)\)", blk)
        net = re.search(r'\(net "([^"]*)"', blk)
        if not at:
            continue
        key = (round(float(at.group(1)), 6), round(float(at.group(2)), 6),
               round(float(sz.group(1)), 6) if sz else None,
               round(float(dr.group(1)), 6) if dr else None)
        out.setdefault(net.group(1) if net else "", set()).add(key)
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

    # ---- R1 protected_copper_identical ----------------------------------
    bs, as_ = segments(bt), segments(at)
    lost, gained = {}, {}
    for n in prot:
        b, c = bs.get(n, frozenset()), as_.get(n, frozenset())
        if b - c:
            lost[n] = len(b - c)
        if c - b:
            gained[n] = len(c - b)
    n_prot_before = sum(len(bs.get(n, ())) for n in prot)
    rows.append(row(
        "protected_copper_identical", sum(lost.values()), {"eq": 0},
        (f"every segment on {', '.join(prot)} survives the round trip "
         f"byte-for-geometry: {n_prot_before} segment(s) in, "
         f"{sum(len(as_.get(n, ())) for n in prot)} out"
         + (f"; {sum(gained.values())} ADDED, which is the router extending a "
            f"protected net rather than rerouting it: {gained}"
            if gained else ""))
        if not lost else
        (f"THE ROUTER CHANGED COPPER IT WAS TOLD NOT TO TOUCH. Segments lost "
         f"per net: {lost}. These shapes were solved (a quarter-wave element, "
         f"an involute spiral); a rerouted one is still electrically "
         f"connected and is no longer the thing that was simulated"),
        PASS if not lost else FAIL, "segments lost"))

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

    verdict = max((r["verdict"] for r in rows), key=lambda v: RANK[v])
    counts = {v: sum(1 for r in rows if r["verdict"] == v)
              for v in (PASS, FAIL, CD)}
    out = {"$halo": 1, "tool": "tools/check_routed.py",
           "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "before": str(bp.resolve()), "after": str(ap_.resolve()),
           "protected_nets": prot,
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
