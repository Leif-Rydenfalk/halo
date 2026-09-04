#!/usr/bin/env python3
"""prove_checks — break every assertion on purpose and require it to go red.

Lane V1, 2026-09-04. docs/TOOLS-THAT-LIE.md, rule 2: *an assertion never seen
to fail is not known to work.* Every check this project trusts was, at some
point, a check that had never once fired. The keep-out containment test
returned None on every board for weeks and nobody could tell, because nobody
had handed it a board it should have rejected.

So: take a real, currently-passing artifact, make one specific thing wrong, and
require the named assertion to report FAIL. If it still passes, the assertion
is decoration and this harness says so.

    python3 tools/prove_checks.py [--keep] [--json out.json]

Exit 0 only if EVERY assertion fired on its own mutation. A mutation that a
check sails through is a FAIL of this harness, not a warning.

Each case below states the mutation and the assertion it must trip. Cases are
paired to their check by name, so an assertion with no case here is reported
as UNPROVEN rather than silently trusted.
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone

HALO = pathlib.Path(__file__).resolve().parent.parent
CHECK = HALO / "tools" / "check_fabset.py"
FABSET = HALO / "out" / "release" / "board"
BOARD = HALO / "electronics" / "halo_rev_a" / "out" / "halo_rev_a.kicad_pcb"
# 2026-06-01T00:00Z. The frozen board is dated BEFORE the real export (so the
# control is fresh) and AFTER m_stale_export's back-dated year (so the mutation
# is genuinely stale). Both directions have to be reachable or F11 is untestable.
FROZEN_MTIME = 1780272000


# ---------------------------------------------------------------- mutations --
def _gerber(d, pat):
    hits = [p for p in d.rglob("*") if p.is_file() and re.search(pat, p.name)]
    if not hits:
        raise FileNotFoundError(f"no file matching {pat} in {d}")
    return hits[0]


def m_break_job(d, b):
    _gerber(d, r"\.gbrjob$").write_text("{ this is not json")
    return "the .gbrjob is replaced with text that is not JSON"


def m_drop_a_copper_layer(d, b):
    p = _gerber(d, r"In2_Cu")
    p.unlink()
    return "the In2.Cu Gerber is deleted, so 4 declared layers have 3 files"


def m_empty_a_copper_layer(d, b):
    p = _gerber(d, r"In1_Cu")
    t = p.read_text()
    head = t.split("G04 APERTURE LIST")[0]
    p.write_text(head + "G04 APERTURE LIST*\nM02*\n")
    return "In1.Cu keeps its header and loses every draw/flash op — a layer with no copper"


def m_strip_format_spec(d, b):
    p = _gerber(d, r"F_Cu")
    t = p.read_text()
    t = re.sub(r"%FSLA?X\d\dY\d\d\*%\n?", "", t)
    t = re.sub(r"%MO(MM|IN)\*%\n?", "", t)
    p.write_text(t)
    return "F.Cu loses %FSLAX46Y46% and %MOMM% — no units, no coordinate format"


def m_undefined_aperture(d, b):
    p = _gerber(d, r"F_Cu")
    t = p.read_text()
    # select an aperture that is never defined, right after the aperture list
    t = t.replace("G04 APERTURE LIST*", "G04 APERTURE LIST*\nD99*", 1)
    p.write_text(t)
    return "F.Cu selects aperture D99, which no %ADD ever defines"


def m_empty_drill(d, b):
    """The live defect, reproduced from a KNOWN-GOOD drill file.

    The shipped pack already has empty drill files, so proving F6 on it would
    prove nothing about the check — it would only re-observe the bug. This case
    starts from a synthesised drill file WITH holes, confirms the check passes,
    then removes the holes.
    """
    p = _gerber(d, r"PTH\.drl$")
    p.write_text("M48\n; synthetic\nFMAT,2\nMETRIC\n%\nG90\nG05\nM30\n")
    return "the PTH drill file's holes are removed, leaving header and M30"


def m_drill_short_of_board(d, b):
    """F7: a drill file with SOME holes but fewer than the board needs.

    The board argument is rewritten too: the live halo_rev_a board is unrouted
    and has zero vias, so `1 hole >= 0 needed` is a legitimate pass and would
    prove nothing. This case writes a board carrying 40 vias beside a drill
    file carrying one — the shape of a drill export that ran but dropped most
    of its holes.
    """
    p = _gerber(d, r"PTH\.drl$")
    p.write_text("M48\n; synthetic\nFMAT,2\nMETRIC\nT01C0.300\n%\nG90\nG05\nT01\n"
                 "X1.000Y1.000\nT00\nM30\n")
    b.write_text(b.read_text() + "\n" + "\n".join(
        f'  (via (at {i} {i}) (size 0.4) (drill 0.2) (layers "F.Cu" "B.Cu") (net 1))'
        for i in range(40)))
    return "the drill file carries 1 hole against a board that declares 40 vias"


def m_point_outline(d, b):
    p = _gerber(d, r"Edge_Cuts")
    t = p.read_text()
    head = t.split("G04 APERTURE LIST")[0]
    add = re.search(r"%ADD\d+[^%]*%", t)
    p.write_text(head + "G04 APERTURE LIST*\n" + (add.group(0) if add else "") +
                 "\nX0Y0D02*\nM02*\n")
    return "the outline is reduced to a single coordinate — extent zero by zero"


def m_wrong_size_outline(d, b):
    """F9: shrink every outline coordinate by half."""
    p = _gerber(d, r"Edge_Cuts")
    t = p.read_text()

    def half(m):
        return m.group(1) + str(int(int(m.group(2)) / 2))
    t = re.sub(r"([XY])(-?\d{4,})", half, t)
    p.write_text(t)
    return "every outline coordinate is halved — the board is now half its stated size"


def m_zip_truncated_member(d, b):
    src = list(d.glob("*.zip"))[0]
    tmp = src.with_suffix(".zip.new")
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w") as zout:
        for i, info in enumerate(zin.infolist()):
            data = zin.read(info.filename)
            if i == 0:
                data = b""          # one member shipped empty
            zout.writestr(info.filename, data)
    tmp.replace(src)
    return "one member of the fab zip is rewritten as zero bytes"


def m_stale_export(d, b):
    """F11: date every Gerber a year before the board was saved."""
    n = 0
    for p in d.rglob("*"):
        if not p.is_file() or p.suffix.lower() == ".zip":
            continue
        t = p.read_text(errors="replace")
        if "CreationDate" not in t:
            continue
        t = re.sub(r"(CreationDate,)2026", r"\g<1>2025", t)
        p.write_text(t)
        n += 1
    return f"the CreationDate in {n} file(s) is moved back a year — a pack older than its board"


def m_oval_outline(d, b):
    """F12: stretch the outline in X only, keeping the extent story plausible."""
    p = _gerber(d, r"Edge_Cuts")
    t = p.read_text()
    t = re.sub(r"X(-?\d{4,})", lambda m: "X" + str(int(int(m.group(1)) * 1.15)), t)
    p.write_text(t)
    return "the outline is stretched 15% in X only — a round board turned into an oval"


CASES = [
    ("job_file_parses",      m_break_job,             []),
    ("layer_count",          m_drop_a_copper_layer,   []),
    ("copper_has_geometry",  m_empty_a_copper_layer,  []),
    ("format_spec_present",  m_strip_format_spec,     []),
    ("apertures_defined",    m_undefined_aperture,    []),
    ("drill_has_hits",       m_empty_drill,           []),
    ("drill_covers_board",   m_drill_short_of_board,  []),
    ("outline_has_extent",   m_point_outline,         []),
    ("outline_matches_spec", m_wrong_size_outline,    ["--expect-outline-mm", "26.0"]),
    ("zip_matches_disk",     m_zip_truncated_member,  []),
    ("export_is_fresh",      m_stale_export,          []),
    ("outline_is_round",     m_oval_outline,          ["--round", "--round-tol", "1.5"]),
]


# ----------------------------------------------- BOM identity mutations ------
# check_bom_identity's assertions are proved the same way: take the BOM, make one
# line specifically wrong, require the named check to go red. The control here is
# a HAND-BUILT CORRECT BOM, not the shipped one -- the shipped one already fails
# 40 assertions, and a check proven only on a broken artifact is not proven.
GOOD_BOM = """Comment,Designator,Footprint,LCSC Part #,Quantity,Value
100pF,C1,C_0402_1005Metric,C1546,1,100pF
20k,R1,R_0402_1005Metric,C25765,1,20k
10uF,C2,C_0402_1005Metric,C15525,1,10uF
100R,R2,R_0402_1005Metric,C25076,1,100R
"""


def b_unknown_code(t):
    return t.replace("C1546", "C999999999"), "the LCSC code names a part not in the catalogue"


def b_wrong_class(t):
    return t.replace("100pF,C1,C_0402_1005Metric,C1546",
                     "100pF,C1,C_0402_1005Metric,C2827888"), \
        "a capacitor line is given C2827888, a 3.5 mm screw terminal block"


def b_wrong_value(t):
    return t.replace(",C1546,1,100pF", ",C1546,1,100nF"), \
        "a 100 pF part is ordered on a line whose value says 100 nF"


def b_wrong_package(t):
    return t.replace("C1,C_0402_1005Metric", "C1,C_0201_0603Metric"), \
        "an 0201 land pattern is given an 0402 part"


def b_code_two_values(t):
    return t + "1nF,C3,C_0402_1005Metric,C1546,1,1nF\n", \
        "the same LCSC code is ordered for two different values"


def b_no_part(t):
    return t.replace(",C1546,1,100pF", ",,1,100pF"), \
        "a fitted line names no LCSC code at all"


BOM_CASES = [
    ("part_resolves",      b_unknown_code,   "CANNOT DETERMINE"),
    ("class_matches",      b_wrong_class,    "FAIL"),
    ("value_matches",      b_wrong_value,    "FAIL"),
    ("package_matches",    b_wrong_package,  "FAIL"),
    ("one_code_one_value", b_code_two_values, "FAIL"),
    ("line_has_a_part",    b_no_part,        "CANNOT DETERMINE"),
]

BOMCHECK = HALO / "tools" / "check_bom_identity.py"


def run_bom(path):
    out = pathlib.Path(tempfile.mkdtemp()) / "b.json"
    subprocess.run([sys.executable, str(BOMCHECK), str(path), "--json", str(out), "--quiet"],
                   capture_output=True, text=True)
    try:
        return json.loads(out.read_text())
    except Exception:
        return None


def bom_verdicts(res, name):
    """Every verdict this assertion produced across the BOM's lines."""
    if not res:
        return []
    return [c["verdict"] for r in res["rows"] for c in r["checks"] if c["name"] == name]


def prove_bom(results):
    d = pathlib.Path(tempfile.mkdtemp(prefix="halo-bom-"))
    good = d / "good.csv"
    good.write_text(GOOD_BOM)
    ctl = run_bom(good)
    print("# prove_checks — BOM identity, 6 assertions on a hand-built correct BOM")
    if ctl is None or ctl["verdict"] != "PASS":
        bad = [(r["designator"], c["name"], c["verdict"], c["why"])
               for r in (ctl or {}).get("rows", []) for c in r["checks"]
               if c["verdict"] != "PASS"]
        print(f"  CANNOT DETERMINE: the control BOM does not pass clean: {bad}")
        results.append({"suite": "bom", "proved": False,
                        "why": f"control BOM verdict is {(ctl or {}).get('verdict')}, not PASS"})
        return 0, len(BOM_CASES)
    proved = 0
    for name, mutate, want in BOM_CASES:
        text, what = mutate(GOOD_BOM)
        f = d / f"{name}.csv"
        f.write_text(text)
        got = bom_verdicts(run_bom(f), name)
        ok = want in got
        proved += ok
        results.append({"suite": "bom", "assertion": name, "mutation": what,
                        "expected": want, "verdicts_seen": got, "proved": ok})
        print(f"  {'FIRED' if ok else 'SILENT':<6}{name:<22} {what}"
              + ("" if ok else f"   -> saw {got}, expected {want}"))
    return proved, len(BOM_CASES) - proved


# ------------------------------------------------------------------ harness --
def rebuild_zip(fabset):
    """Rewrite the fab zip from what is on disk, so F10's control is honest.

    Repairing the drill file changes its byte count; without this the zip
    comparison goes red for a reason that has nothing to do with the mutation
    under test, and a check whose control is already red cannot be proven.
    """
    zips = list(fabset.glob("*.zip"))
    if not zips:
        return
    z = zips[0]
    keep = {".gtl", ".gbl", ".g1", ".g2", ".gts", ".gbs", ".gto", ".gbo",
            ".gm1", ".gko", ".gbr", ".drl", ".xln"}
    loose = [p for p in fabset.rglob("*")
             if p.is_file() and p != z and p.suffix.lower() in keep]
    with zipfile.ZipFile(z, "w") as out:
        for p in loose:
            out.writestr(str(p.relative_to(fabset)), p.read_bytes())


def run_check(fabset, board, extra):
    out = pathlib.Path(tempfile.mkdtemp()) / "v.json"
    cmd = [sys.executable, str(CHECK), str(fabset), "--board", str(board),
           "--expect-layers", "4", "--json", str(out), "--quiet"] + extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(out.read_text()), r
    except Exception:
        return None, r


def verdict_of(res, name):
    if not res:
        return None
    for row in res["rows"]:
        if row["name"] == name:
            return row["verdict"]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="leave the mutated copies on disk")
    ap.add_argument("--json")
    a = ap.parse_args()

    if not FABSET.is_dir():
        print(f"CANNOT DETERMINE: no fabrication set at {FABSET}", file=sys.stderr)
        return 2

    # A drill file WITH holes, so drill_has_hits has something to lose. The
    # shipped pack's drill file is empty (that is the defect V1 found), and a
    # check proven only against an already-broken artifact is not proven.
    base = pathlib.Path(tempfile.mkdtemp(prefix="halo-fabset-base-"))
    shutil.copytree(FABSET, base / "board")
    good = base / "board"
    pth = next(p for p in good.rglob("*PTH.drl"))
    holes = "\n".join(f"X{1.0 + 0.5 * i:.3f}Y2.000" for i in range(8))
    pth.write_text("M48\n; synthetic, prove_checks.py\n"
                   "; #@! TF.CreationDate,2026-09-04T18:29:08+08:00\n"
                   "FMAT,2\nMETRIC\nT01C0.300\n%\n"
                   "G90\nG05\nT01\n" + holes + "\nT00\nM30\n")
    rebuild_zip(good)

    # Freeze the board: lane B1 is writing halo_rev_a.kicad_pcb while this runs,
    # and a moving mtime turns export_is_fresh red for a reason unrelated to any
    # mutation. Copy it, and back-date it to before the export it is compared to.
    board = base / "board.kicad_pcb"
    board.write_text(BOARD.read_text())
    os.utime(board, (FROZEN_MTIME, FROZEN_MTIME))

    control, cr = run_check(good, board, ["--expect-outline-mm", "26.0",
                                          "--round", "--round-tol", "1.5"])
    if control is None:
        print("CANNOT DETERMINE: the checker itself did not produce JSON\n" + cr.stderr,
              file=sys.stderr)
        return 2

    results, proved, unproven = [], 0, 0
    ctl = {r["name"]: r["verdict"] for r in control["rows"]}
    print(f"# prove_checks — {len(CASES)} assertions, each fed something that should fail")
    print(f"  control (unmutated, drill file repaired): "
          + ", ".join(f"{k}={v}" for k, v in ctl.items() if v != "PASS") or "  control: all PASS")

    for name, mutate, extra in CASES:
        if ctl.get(name) != "PASS":
            results.append({"assertion": name, "proved": False,
                            "why": f"control verdict is {ctl.get(name)}, not PASS — a check "
                                   f"already red cannot be shown to go red"})
            unproven += 1
            print(f"  SKIP  {name:<22} control is {ctl.get(name)}")
            continue
        d = pathlib.Path(tempfile.mkdtemp(prefix=f"halo-mut-{name}-"))
        shutil.copytree(good, d / "board")
        mb = d / "board.kicad_pcb"
        mb.write_text(board.read_text())
        os.utime(mb, (FROZEN_MTIME, FROZEN_MTIME))
        try:
            what = mutate(d / "board", mb)
        except Exception as e:
            results.append({"assertion": name, "proved": False,
                            "why": f"mutation could not be applied: {e}"})
            unproven += 1
            print(f"  ERR   {name:<22} mutation failed: {e}")
            continue
        res, _ = run_check(d / "board", mb, extra)
        got = verdict_of(res, name)
        ok = got == "FAIL"
        proved += ok
        unproven += (not ok)
        results.append({"assertion": name, "mutation": what, "verdict_after": got,
                        "proved": ok,
                        "why": (f"FAIL as required" if ok else
                                f"the assertion returned {got} on an input that is definitely "
                                f"wrong — it does not measure what its name claims")})
        print(f"  {'FIRED' if ok else 'SILENT':<6}{name:<22} {what}"
              + ("" if ok else f"   -> got {got}, expected FAIL"))
        if not a.keep:
            shutil.rmtree(d, ignore_errors=True)

    if not a.keep:
        shutil.rmtree(base, ignore_errors=True)

    bp, bu = prove_bom(results)
    proved += bp
    unproven += bu

    out = {
        "$halo": 1,
        "tool": "tools/prove_checks.py",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target": "tools/check_fabset.py",
        "assertions": len(CASES) + len(BOM_CASES),
        "proved_to_fire": proved,
        "unproven": unproven,
        "verdict": "PASS" if unproven == 0 else "FAIL",
        "cases": results,
    }
    if a.json:
        pathlib.Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.json).write_text(json.dumps(out, indent=1) + "\n")
    print(f"{out['verdict']}: {proved} of {len(CASES) + len(BOM_CASES)} "
          f"assertions proved to fire")
    return 0 if unproven == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
