#!/usr/bin/env python3
"""check_fabset — read a fabrication set BACK and grade it against the board it claims to be.

Lane V1, 2026-09-04. Written because the halo factory pack shipped a Gerber set
whose PTH and NPTH drill files contained **zero holes**, on a four-layer board
that cannot exist without vias, and nothing in the project noticed. Fourteen
files were exported, the exporter exited 0, the pack index said READY, and the
board house would have received a board with no drilling.

The rule from docs/TOOLS-THAT-LIE.md, applied: a report must be DERIVED from the
effect, not from the intent. `bin/fab jlc` reports the export it performed.
This tool reports what is IN the files afterwards, and cross-checks it against
the source .kicad_pcb, which is a different artifact produced by a different
tool. Two independent readings that agree are worth more than one that passes.

    python3 tools/check_fabset.py <fabset_dir> [--board X.kicad_pcb]
        [--expect-layers N] [--expect-outline-mm D --outline-tol MM]
        [--json out.json] [--quiet]

Exit codes are the verdict: 0 PASS · 1 FAIL · 2 CANNOT DETERMINE.
A check that could not be evaluated is 2 and 2 is never a pass.

The fifteen assertions below, each with the sentence it defeats
(F12 outline_is_round is a sixteenth, evaluated only with --round):

  F1  job_file_parses        could PASS while the set is a pile of files no fab can index
  F2  layer_count            could PASS while a four-layer board shipped two copper files
  F3  copper_has_geometry    could PASS while a copper layer is a header with no copper
  F4  format_spec_present    could PASS while a Gerber has no units and no coordinate format
  F5  apertures_defined      could PASS while a file references a D-code it never defined
  F6  drill_has_hits         could PASS while the drill file has no holes at all   <-- the live defect
  F7  drill_covers_board     could PASS while the drill file has holes but not OUR holes
  F13 drill_files_declare_class  could PASS while PTH and NPTH were told apart by FILENAME
  F14 drill_pth_count_exact  could PASS while the PTH file has MORE holes than the board has
  F15 drill_npth_count_exact could PASS while NPTH holes were counted in the plated total
  F16 drill_sizes_match      could PASS while every hole is drilled at the wrong diameter
  F8  outline_has_extent     could PASS while the board outline is a single point
  F9  outline_matches_spec   could PASS while the board is 26 mm and the spec says 31.87 mm
  F10 zip_matches_disk       could PASS while the zip a fab downloads differs from what we checked
  F11 export_is_fresh        could PASS while the pack was exported from a board since redrawn
"""
import argparse
import json
import os
import pathlib
import re
import sys
import zipfile
from datetime import datetime, timezone

PASS, FAIL, CD = "PASS", "FAIL", "CANNOT DETERMINE"
RANK = {PASS: 0, CD: 1, FAIL: 2}

COPPER_EXT = {".gtl", ".gbl", ".g1", ".g2", ".g3", ".g4", ".gp1", ".gp2"}
DRILL_EXT = {".drl", ".xln", ".txt"}
GERBER_EXT = COPPER_EXT | {".gts", ".gbs", ".gto", ".gbo", ".gm1", ".gbr", ".gko"}

# a Gerber draw/flash op: an optional coordinate block ending in D01 (draw),
# D02 (move) or D03 (flash). D01 and D03 put metal down; D02 does not.
OP_RE = re.compile(r"^(?:G\d+\*?)?(?:X(-?\d+))?(?:Y(-?\d+))?"
                   r"(?:I(-?\d+))?(?:J(-?\d+))?D0([123])\*", re.M)
FS_RE = re.compile(r"%FSLA?X(\d)(\d)Y(\d)(\d)\*%")
MO_RE = re.compile(r"%MO(MM|IN)\*%")
ADD_RE = re.compile(r"%ADD(\d+)", re.M)
DSEL_RE = re.compile(r"^D(\d{2,})\*", re.M)
CREATED_RE = re.compile(r"%TF\.CreationDate,([0-9T:+\-\.]+)\*%")
DRILL_CREATED_RE = re.compile(r"TF\.CreationDate,([0-9T:+\-\.]+)")
# an Excellon hole: X and/or Y on a line, after the header
DRILL_HIT_RE = re.compile(r"^(?:X-?[\d.]+)?(?:Y-?[\d.]+)?\s*$", re.M)
DRILL_TOOL_RE = re.compile(r"^T(\d+)C([\d.]+)", re.M)


def row(name, value, rule, why, verdict, unit=""):
    return {"name": name, "value": value, "unit": unit, "rule": rule,
            "why": why, "verdict": verdict}


def read(p):
    return pathlib.Path(p).read_text(errors="replace")


def gerber_ops(text):
    """Count coordinate operations that actually put metal down (D01/D03)."""
    n = 0
    for m in OP_RE.finditer(text):
        if m.group(5) in ("1", "3"):
            n += 1
    return n


def gerber_points(text, scale):
    """Every coordinate visited, in mm, with modal X/Y carried forward."""
    pts, cx, cy = [], 0.0, 0.0
    for m in OP_RE.finditer(text):
        x, y = m.group(1), m.group(2)
        if x is not None:
            cx = int(x) / scale
        if y is not None:
            cy = int(y) / scale
        if m.group(5) in ("1", "2"):
            pts.append((cx, cy))
    return pts


def drill_hits(text):
    """Count Excellon hole coordinates, ignoring the header block.

    The header ends at the lone `%` line; before it, `T01C0.3` lines define
    tools and are not holes. Counting the whole file would score a header as
    drilling, which is exactly the kind of derivation this file exists to
    forbid.
    """
    body = text.split("\n%\n", 1)
    body = body[1] if len(body) == 2 else text
    n = 0
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith(("M", "G", "T", ";", "%")):
            continue
        if line[0] in "XY":
            n += 1
    return n


def drill_class(text):
    """PTH or NPTH, read from the FILE'S OWN declaration — never its name.

    Excellon files KiCad writes carry `TF.FileFunction,Plated,1,4,PTH` or
    `...,NonPlated,1,4,NPTH` in the header. That is the file saying what it is.
    A check that split the two by looking for "NPTH" in the filename would
    grade a mislabelled export as correct, which is the whole failure mode
    this file exists for: the file existing is not the file describing the
    board. Returns None when the file does not say, and None is not a guess.
    """
    m = re.search(r"TF\.FileFunction,(\w+),[^\n]*", text)
    if not m:
        return None
    kind = m.group(1).lower()
    if kind.startswith("nonplated"):
        return "NPTH"
    if kind.startswith("plated"):
        return "PTH"
    return None


def drill_holes_by_size(text):
    """-> (total, {diameter_mm: count}, n_slots, note)

    Walks the Excellon body carrying the SELECTED TOOL forward, so every hole
    is attributed to the diameter it is actually drilled at. Units come from
    the file's own METRIC/INCH line; an INCH file is converted, because a
    diameter comparison across units is a comparison of nothing.

    A routed slot (`G85`) is one hole for counting purposes and is reported
    separately, so a board with slots cannot silently inflate the plain-hole
    count.
    """
    inch = bool(re.search(r"^INCH", text, re.M)) and not re.search(r"^METRIC", text, re.M)
    k = 25.4 if inch else 1.0
    tools = {}
    for m in DRILL_TOOL_RE.finditer(text):
        tools[m.group(1).lstrip("0") or "0"] = round(float(m.group(2)) * k, 4)
    body = text.split("\n%\n", 1)
    body = body[1] if len(body) == 2 else text
    sizes, cur, slots, total = {}, None, 0, 0
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        mt = re.match(r"^T(\d+)$", line)
        if mt:
            n = mt.group(1).lstrip("0") or "0"
            cur = tools.get(n)
            continue
        if line.startswith(("M", "G9", "G0", ";", "%", "T")):
            # G85 slots are written as `X..Y..G85X..Y..`; catch those below.
            if "G85" not in line:
                continue
        if line[0] not in "XY":
            continue
        total += 1
        if "G85" in line:
            slots += 1
        if cur is None:
            sizes.setdefault(None, 0)
            sizes[None] += 1
        else:
            sizes[cur] = sizes.get(cur, 0) + 1
    note = ""
    if None in sizes:
        note = (f"{sizes[None]} hole(s) appear before any T-code selection, so "
                f"their diameter is unknown")
    return total, sizes, slots, note


def board_holes_by_size(board_path):
    """The board's own holes, by class and diameter, read as text.

    Independent of the exporter on purpose (docs/TOOLS-THAT-LIE.md item 5):
    the .kicad_pcb is a different artifact written by a different tool, so if
    it and the Excellon agree on 49 holes at 0.250 mm, two readers agree.

    A via is a plated hole. A `thru_hole` pad is a plated hole. An
    `np_thru_hole` pad is a NON-plated hole and belongs in the NPTH file, not
    in the plated total — lumping them was how the old `>= board holes` rule
    could pass with the two files swapped.
    """
    t = read(board_path)
    plated, nonplated, oval = {}, {}, 0

    def add(d, dia):
        dia = round(float(dia), 4)
        d[dia] = d.get(dia, 0) + 1

    # vias: (via ... (drill D) ...) — the drill token inside the via's own block
    for m in re.finditer(r"\(via\b", t):
        blk = _sexp_block(t, m.start())
        dm = re.search(r"\(drill\s+([\d.]+)", blk)
        if dm:
            add(plated, dm.group(1))
        else:
            add(plated, 0.0)
    for kind, bucket in (("thru_hole", plated), ("np_thru_hole", nonplated)):
        for m in re.finditer(r'\(pad\s+"[^"]*"\s+%s\b' % kind, t):
            blk = _sexp_block(t, m.start())
            dm = re.search(r"\(drill\s+(oval\s+)?([\d.]+)", blk)
            if dm:
                if dm.group(1):
                    oval += 1
                add(bucket, dm.group(2))
            else:
                add(bucket, 0.0)
    return {"plated": plated, "nonplated": nonplated, "oval_pads": oval,
            "plated_total": sum(plated.values()),
            "nonplated_total": sum(nonplated.values())}


def _sexp_block(text, start):
    """The balanced s-expression beginning at `start`, capped so a runaway
    scan cannot swallow the file. Used to keep a via's `(drill ...)` attached
    to that via instead of to whatever token happened to come next."""
    depth, i, n = 0, start, len(text)
    while i < n and i - start < 4000:
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1
    return text[start:start + 4000]


def _sizes_str(d):
    return ", ".join(f"{k if k is not None else 'unknown'}mm x{v}"
                     for k, v in sorted(d.items(), key=lambda kv: (kv[0] is None, kv[0])))


def parse_ts(s):
    try:
        return datetime.fromisoformat(s.strip()).timestamp()
    except Exception:
        return None


def board_hole_count(board_path):
    """Read the source .kicad_pcb and count what MUST appear in the drill file.

    s-expression text scan, not a KiCad API call, on purpose: the point is a
    reading independent of the tool that wrote the Gerbers. A via is a hole. A
    pad of type thru_hole or np_thru_hole is a hole.
    """
    t = read(board_path)
    vias = len(re.findall(r"\(via\b", t))
    pth = len(re.findall(r'\(pad\s+"[^"]*"\s+thru_hole\b', t))
    npth = len(re.findall(r'\(pad\s+"[^"]*"\s+np_thru_hole\b', t))
    return {"vias": vias, "thru_hole_pads": pth, "np_thru_hole_pads": npth,
            "plated_total": vias + pth, "nonplated_total": npth}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fabset")
    ap.add_argument("--board", help="the source .kicad_pcb the set claims to be")
    ap.add_argument("--expect-layers", type=int)
    ap.add_argument("--expect-outline-mm", type=float,
                    help="expected outline extent (diameter for a round board)")
    ap.add_argument("--outline-tol", type=float, default=0.5)
    ap.add_argument("--round", action="store_true",
                    help="the outline is specified as a circle: assert it actually is one")
    ap.add_argument("--round-tol", type=float, default=0.05,
                    help="max allowed peak-to-peak radius variation, mm")
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    d = pathlib.Path(a.fabset)
    if not d.is_dir():
        print(f"CANNOT DETERMINE: {d} is not a directory", file=sys.stderr)
        return 2

    files = sorted(p for p in d.rglob("*") if p.is_file())
    gerbers = [p for p in files if p.suffix.lower() in GERBER_EXT]
    drills = [p for p in files if p.suffix.lower() in DRILL_EXT
              and "drl_map" not in p.name and "drill-map" not in p.name]
    zips = [p for p in files if p.suffix.lower() == ".zip"]
    jobs = [p for p in files if p.suffix.lower() == ".gbrjob"]

    rows = []

    # ---- F1 job_file_parses -------------------------------------------------
    job = None
    if not jobs:
        rows.append(row("job_file_parses", 0, {"gte": 1},
                        "no .gbrjob in the set: a fab has no index of which file is which layer",
                        FAIL, "files"))
    else:
        try:
            job = json.loads(read(jobs[0]))
            n = len(job.get("FilesAttributes", []))
            rows.append(row("job_file_parses", n, {"gte": 1},
                            f"{jobs[0].name} parses and names {n} file(s)",
                            PASS if n else FAIL, "files"))
        except Exception as e:
            rows.append(row("job_file_parses", 0, {"gte": 1},
                            f"{jobs[0].name} is not valid JSON: {e}", FAIL, "files"))

    # ---- F2 layer_count -----------------------------------------------------
    declared = job.get("GeneralSpecs", {}).get("LayerNumber") if job else None
    copper_named = []
    if job:
        for f in job.get("FilesAttributes", []):
            if str(f.get("FileFunction", "")).startswith("Copper"):
                copper_named.append(f["Path"])
    copper_on_disk = [p for p in gerbers if p.suffix.lower() in COPPER_EXT]
    if declared is None:
        rows.append(row("layer_count", None, {"eq": a.expect_layers},
                        "the job file declares no LayerNumber", CD, "layers"))
    else:
        ok = (len(copper_named) == declared == len(copper_on_disk))
        why = (f"job declares {declared} layers, names {len(copper_named)} copper file(s), "
               f"{len(copper_on_disk)} copper file(s) on disk")
        v = PASS if ok else FAIL
        if a.expect_layers is not None and declared != a.expect_layers:
            v = FAIL
            why += f"; expected {a.expect_layers}"
        rows.append(row("layer_count", declared,
                        {"eq": a.expect_layers} if a.expect_layers else {"self_consistent": True},
                        why, v, "layers"))

    # ---- F3 copper_has_geometry --------------------------------------------
    empty_copper, cu_ops = [], {}
    for p in copper_on_disk:
        n = gerber_ops(read(p))
        cu_ops[p.name] = n
        if n == 0:
            empty_copper.append(p.name)
    if not copper_on_disk:
        rows.append(row("copper_has_geometry", None, {"gte": 1},
                        "no copper Gerbers found to measure", CD, "ops"))
    else:
        rows.append(row("copper_has_geometry", min(cu_ops.values()), {"gte": 1},
                        ("every copper layer carries metal: "
                         + ", ".join(f"{k}={v}" for k, v in sorted(cu_ops.items())))
                        if not empty_copper else
                        f"copper layer(s) with ZERO draw/flash ops: {', '.join(empty_copper)}",
                        PASS if not empty_copper else FAIL, "ops"))

    # ---- F4 format_spec_present --------------------------------------------
    missing_fmt = []
    for p in gerbers:
        t = read(p)
        if not FS_RE.search(t) or not MO_RE.search(t):
            missing_fmt.append(p.name)
    if not gerbers:
        rows.append(row("format_spec_present", None, {"eq": 0}, "no Gerbers found", CD, "files"))
    else:
        rows.append(row("format_spec_present", len(missing_fmt), {"eq": 0},
                        f"{len(gerbers)} Gerber(s) checked; "
                        + ("all carry %FSLA..% and %MO..%" if not missing_fmt
                           else f"missing format/unit spec: {', '.join(missing_fmt)}"),
                        PASS if not missing_fmt else FAIL, "files"))

    # ---- F5 apertures_defined ----------------------------------------------
    undefined = []
    for p in gerbers:
        t = read(p)
        defined = {int(m) for m in ADD_RE.findall(t)}
        used = {int(m) for m in DSEL_RE.findall(t) if int(m) >= 10}
        miss = used - defined
        if miss:
            undefined.append(f"{p.name}:D{sorted(miss)}")
    rows.append(row("apertures_defined", len(undefined), {"eq": 0},
                    "every D-code selected is defined by an %ADD" if not undefined
                    else f"aperture used but never defined: {'; '.join(undefined)}",
                    PASS if not undefined else FAIL, "files"))

    # ---- F6 drill_has_hits --------------------------------------------------
    per_drill = {p.name: drill_hits(read(p)) for p in drills}
    total_hits = sum(per_drill.values())
    layers = declared or a.expect_layers or 0
    if not drills:
        rows.append(row("drill_has_hits", None, {"gte": 1},
                        "no drill file in the set at all", FAIL, "holes"))
    elif layers > 2:
        rows.append(row("drill_has_hits", total_hits, {"gte": 1},
                        f"{layers}-layer board: it cannot exist without vias. "
                        + ", ".join(f"{k}={v}" for k, v in sorted(per_drill.items())),
                        PASS if total_hits >= 1 else FAIL, "holes"))
    else:
        rows.append(row("drill_has_hits", total_hits, {"gte": 0},
                        f"2-layer or fewer; {total_hits} hole(s) is allowed to be zero",
                        PASS, "holes"))

    # ---- F7 drill_covers_board ---------------------------------------------
    if not a.board:
        rows.append(row("drill_covers_board", None, {"gte": "board holes"},
                        "no --board given: cannot cross-check the drill file against a source",
                        CD, "holes"))
    elif not pathlib.Path(a.board).is_file():
        rows.append(row("drill_covers_board", None, {"gte": "board holes"},
                        f"--board {a.board} is not a file", CD, "holes"))
    else:
        bh = board_hole_count(a.board)
        need = bh["plated_total"] + bh["nonplated_total"]
        rows.append(row("drill_covers_board", total_hits, {"eq": need},
                        f"source board has {bh['vias']} via(s) + {bh['thru_hole_pads']} thru-hole "
                        f"pad(s) + {bh['np_thru_hole_pads']} NPTH pad(s) = {need} hole(s) that must "
                        f"be drilled; the drill file(s) carry {total_hits}"
                        + ("" if total_hits == need else
                           f" — a difference of {total_hits - need:+d}. `>=` was the old rule "
                           f"and it would have graded a drill file from a DIFFERENT board as "
                           f"covering this one"),
                        PASS if total_hits == need else FAIL, "holes"))

    # ---- F13/F14/F15/F16 the drill files must DESCRIBE THIS BOARD ----------
    # `drill_covers_board` above answers "are there at least as many holes as
    # the board needs, in total". That was never the same question as "is this
    # the drill program for this board". Four things it cannot see:
    #   * PTH and NPTH told apart by FILENAME rather than by the file's own
    #     TF.FileFunction — swap the two names and the total is unchanged;
    #   * MORE holes than the board has, which a `>=` rule reads as covered;
    #   * NPTH pads counted inside the plated total;
    #   * every hole drilled at the wrong DIAMETER, which no count can see.
    # Measured on halo_rev_a 2026-09-05: 49 vias + 0 thru-hole pads, all at
    # 0.250 mm, against PTH.drl 49 holes all T1C0.250, NPTH.drl 0 holes.
    by_class = {}
    unnamed = []
    for pth in drills:
        txt = read(pth)
        cls = drill_class(txt)
        if cls is None:
            unnamed.append(pth.name)
        by_class.setdefault(cls, []).append((pth.name, txt))
    rows.append(row("drill_files_declare_class", len(drills) - len(unnamed),
                    {"eq": len(drills)},
                    (f"every drill file states its own function: "
                     + "; ".join(f"{n}={c}" for c, v in by_class.items() for n, _ in v))
                    if not unnamed else
                    (f"{len(unnamed)} drill file(s) carry no TF.FileFunction and were "
                     f"NOT classified by filename: {', '.join(unnamed)}"),
                    PASS if not unnamed and drills else (CD if not drills else FAIL),
                    "files"))

    if not a.board or not pathlib.Path(a.board).is_file():
        for nm in ("drill_pth_count_exact", "drill_npth_count_exact", "drill_sizes_match"):
            rows.append(row(nm, None, {},
                            "no readable --board: nothing to compare the drill program to",
                            CD, "holes"))
    else:
        bsz = board_holes_by_size(a.board)
        got = {}
        for cls in ("PTH", "NPTH"):
            tot, sizes, slots, note = 0, {}, 0, []
            for nm, txt in by_class.get(cls, []):
                tt, ss, sl, nt = drill_holes_by_size(txt)
                tot += tt
                slots += sl
                for k, v in ss.items():
                    sizes[k] = sizes.get(k, 0) + v
                if nt:
                    note.append(f"{nm}: {nt}")
            got[cls] = {"files": [nm for nm, _ in by_class.get(cls, [])],
                        "holes": tot, "sizes": sizes, "slots": slots,
                        "note": "; ".join(note)}

        want_p = bsz["plated_total"]
        rows.append(row("drill_pth_count_exact", got["PTH"]["holes"], {"eq": want_p},
                        f"board declares {want_p} plated hole(s) "
                        f"({bsz['plated_total']} = vias + thru-hole pads); the file(s) that "
                        f"DECLARE THEMSELVES PTH ({', '.join(got['PTH']['files']) or 'none'}) "
                        f"carry {got['PTH']['holes']}"
                        + (f", of which {got['PTH']['slots']} slot(s)" if got["PTH"]["slots"] else "")
                        + (". " + got["PTH"]["note"] if got["PTH"]["note"] else ""),
                        PASS if got["PTH"]["holes"] == want_p else FAIL, "holes"))

        want_n = bsz["nonplated_total"]
        rows.append(row("drill_npth_count_exact", got["NPTH"]["holes"], {"eq": want_n},
                        f"board declares {want_n} non-plated hole(s) (np_thru_hole pads); the "
                        f"file(s) that DECLARE THEMSELVES NPTH "
                        f"({', '.join(got['NPTH']['files']) or 'none'}) carry "
                        f"{got['NPTH']['holes']}"
                        + (". A board with no NPTH pads must ship an NPTH file with no holes, "
                           "not an NPTH file carrying the plated ones"
                           if want_n == 0 else ""),
                        PASS if got["NPTH"]["holes"] == want_n else FAIL, "holes"))

        mism = []
        for cls, want in (("PTH", bsz["plated"]), ("NPTH", bsz["nonplated"])):
            have = {k: v for k, v in got[cls]["sizes"].items()}
            w = {round(k, 3): v for k, v in want.items()}
            h = {round(k, 3) if k is not None else None: v for k, v in have.items()}
            if w != h:
                mism.append(f"{cls}: board {_sizes_str(w) or 'none'} vs file "
                            f"{_sizes_str(h) or 'none'}")
        rows.append(row("drill_sizes_match", len(mism), {"eq": 0},
                        "every hole diameter in the drill program matches a hole the board "
                        f"declares — PTH {_sizes_str(bsz['plated']) or 'none'}, "
                        f"NPTH {_sizes_str(bsz['nonplated']) or 'none'}"
                        if not mism else "; ".join(mism),
                        PASS if not mism else FAIL, "mismatched size classes"))

    # ---- F8/F9 outline ------------------------------------------------------
    prof = [p for p in gerbers if p.suffix.lower() in (".gm1", ".gko")
            or "Edge_Cuts" in p.name or "Profile" in p.name]
    if not prof:
        rows.append(row("outline_has_extent", None, {"gt": 0},
                        "no board outline / profile layer found", FAIL, "mm"))
        rows.append(row("outline_matches_spec", None, {}, "no outline to compare", CD, "mm"))
    else:
        t = read(prof[0])
        m = FS_RE.search(t)
        scale = 10 ** int(m.group(2)) if m else 1e6
        pts = gerber_points(t, scale)
        if len(pts) < 2:
            rows.append(row("outline_has_extent", len(pts), {"gte": 2},
                            f"{prof[0].name} has {len(pts)} coordinate(s): that is not an outline",
                            FAIL, "points"))
            rows.append(row("outline_matches_spec", None, {}, "no extent to compare", CD, "mm"))
        else:
            sx = max(x for x, _ in pts) - min(x for x, _ in pts)
            sy = max(y for _, y in pts) - min(y for _, y in pts)
            rows.append(row("outline_has_extent", round(min(sx, sy), 4), {"gt": 0.0},
                            f"{prof[0].name}: {len(pts)} points, extent {sx:.4f} x {sy:.4f} mm",
                            PASS if min(sx, sy) > 0 else FAIL, "mm"))
            if a.expect_outline_mm is None:
                rows.append(row("outline_matches_spec", round(max(sx, sy), 4), {},
                                "no --expect-outline-mm given: the set's size is unjudged",
                                CD, "mm"))
            else:
                dx = abs(sx - a.expect_outline_mm)
                dy = abs(sy - a.expect_outline_mm)
                worst = max(dx, dy)
                rows.append(row("outline_matches_spec", round(worst, 4),
                                {"lte": a.outline_tol, "target": a.expect_outline_mm},
                                f"outline {sx:.4f} x {sy:.4f} mm vs spec {a.expect_outline_mm} mm: "
                                f"worst deviation {worst:.4f} mm, allowed {a.outline_tol} mm",
                                PASS if worst <= a.outline_tol else FAIL, "mm"))
            if a.round:
                # F12 outline_is_round — could PASS while a "round board" is an
                # oval, a polygon or a circle with an unintended flat. Extent
                # alone cannot see this: a square 26 mm across passes F9.
                ox = (max(x for x, _ in pts) + min(x for x, _ in pts)) / 2
                oy = (max(y for _, y in pts) + min(y for _, y in pts)) / 2
                rr = [((x - ox) ** 2 + (y - oy) ** 2) ** 0.5 for x, y in pts]
                span = max(rr) - min(rr)
                rows.append(row("outline_is_round", round(span, 4),
                                {"lte": a.round_tol},
                                f"radius about ({ox:.3f},{oy:.3f}) runs {min(rr):.4f}..{max(rr):.4f} mm, "
                                f"peak-to-peak {span:.4f} mm, allowed {a.round_tol} mm",
                                PASS if span <= a.round_tol else FAIL, "mm"))

    # ---- F10 zip_matches_disk ----------------------------------------------
    if not zips:
        rows.append(row("zip_matches_disk", None, {"eq": 0},
                        "no .zip in the set: nothing to compare (a fab would be sent loose files)",
                        CD, "files"))
    else:
        try:
            with zipfile.ZipFile(zips[0]) as z:
                members = {i.filename: i.file_size for i in z.infolist()}
            zero = [k for k, v in members.items() if v == 0]
            disk_sizes = sorted(p.stat().st_size for p in gerbers + drills)
            zip_sizes = sorted(members.values())
            # match by size multiset: names are renamed to JLC extensions on export,
            # so the byte count is the invariant a rename cannot fake.
            missing = []
            pool = list(zip_sizes)
            for s in disk_sizes:
                if s in pool:
                    pool.remove(s)
                else:
                    missing.append(s)
            ok = not missing and not zero
            rows.append(row("zip_matches_disk", len(missing) + len(zero), {"eq": 0},
                            f"{len(members)} member(s) in {zips[0].name}; "
                            + ("every loose Gerber/drill has a byte-identical member"
                               if ok else
                               f"{len(missing)} disk file(s) with no matching member, "
                               f"{len(zero)} zero-length member(s) {zero}"),
                            PASS if ok else FAIL, "files"))
        except Exception as e:
            rows.append(row("zip_matches_disk", None, {"eq": 0},
                            f"{zips[0].name} could not be read: {e}", FAIL, "files"))

    # ---- F11 export_is_fresh -----------------------------------------------
    if not a.board or not pathlib.Path(a.board).is_file():
        rows.append(row("export_is_fresh", None, {"gte": 0},
                        "no --board given: cannot tell a fresh export from a stale one", CD, "s"))
    else:
        bmt = pathlib.Path(a.board).stat().st_mtime
        stamps = []
        for p in gerbers + drills:
            t = read(p)
            m = CREATED_RE.search(t) or DRILL_CREATED_RE.search(t)
            ts = parse_ts(m.group(1)) if m else None
            if ts is not None:
                stamps.append((p.name, ts))
        if not stamps:
            rows.append(row("export_is_fresh", None, {"gte": 0},
                            "no file carries a CreationDate to compare", CD, "s"))
        else:
            worst_name, worst_ts = min(stamps, key=lambda kv: kv[1])
            age = worst_ts - bmt   # negative means exported BEFORE the board was last saved
            rows.append(row("export_is_fresh", round(age, 1), {"gte": 0},
                            f"oldest export {worst_name} at "
                            f"{datetime.fromtimestamp(worst_ts, timezone.utc).isoformat()} vs board "
                            f"saved {datetime.fromtimestamp(bmt, timezone.utc).isoformat()}: "
                            + ("export is at or after the board" if age >= 0 else
                               f"THE PACK IS {-age:.0f} s OLDER THAN THE BOARD — it was exported "
                               f"from a board that has since been redrawn"),
                            PASS if age >= 0 else FAIL, "s"))

    worst = max(rows, key=lambda r: RANK[r["verdict"]])["verdict"]
    out = {
        "$halo": 1,
        "tool": "tools/check_fabset.py",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fabset": str(d.resolve()),
        "board": str(pathlib.Path(a.board).resolve()) if a.board else None,
        "verdict": worst,
        "counts": {k: sum(1 for r in rows if r["verdict"] == k) for k in (PASS, FAIL, CD)},
        "rows": rows,
        "command": "python3 " + " ".join(sys.argv[0:1] + sys.argv[1:]),
    }
    if a.json:
        pathlib.Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.json).write_text(json.dumps(out, indent=1) + "\n")
    if not a.quiet:
        print(f"# check_fabset — {d}")
        for r in rows:
            v = {PASS: "PASS", FAIL: "FAIL", CD: "CD  "}[r["verdict"]]
            val = r["value"] if r["value"] is not None else "—"
            print(f"  {v}  {r['name']:<22} {str(val):>12} {r['unit']:<6} {r['why']}")
        print(f"{worst}: {out['counts'][PASS]} pass, {out['counts'][FAIL]} fail, "
              f"{out['counts'][CD]} cannot determine")
    return {PASS: 0, FAIL: 1, CD: 2}[worst]


if __name__ == "__main__":
    sys.exit(main())
