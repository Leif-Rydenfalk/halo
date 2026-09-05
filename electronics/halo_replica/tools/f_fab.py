"""f_fab — the fabrication set, cut from the CURRENT board, marked NOT FOR
FABRICATION on the face of every file.

    python3 electronics/halo_replica/tools/f_fab.py
    ... --break-stale     cut, then touch the board, and watch freshness fail

Exit 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

---------------------------------------------------------------------------
WHY THIS SET EXISTS AND WHY IT IS NOT ORDERABLE
---------------------------------------------------------------------------
The set is cut so the row exists and so a reader can open the actual output
rather than take a description of it. It is NOT a fabrication package, and
three separate facts say so:

  1  0.30 mm at four layers is BELOW PCBWay's 0.40 mm four-layer floor and
     JLCPCB's 0.40 mm minimum. The Replica AS DRAWN cannot be ordered at
     either house. The drawing is not moved to 0.40 to make a quote come
     back; that is a fact about US, not about Apple.
  2  The board's own DRC has ERRORS, classified in
     pcb/out/drc-classification.json. A gerber set whose precondition is a
     clean DRC is INVALID here, and that is the correct outcome.
  3  There is NO NETLIST BINDING. 65 nets are read from the schematic and
     zero pads are attached to any of them, so the copper's connectivity is
     unknown. Every passive value is CANNOT DETERMINE.

So every Gerber gets a `G04` comment block naming all three, and the drill
file gets the same in its own comment syntax. A statement in a README beside
the files is a statement somebody can fail to open; a statement in the file
travels with it.

---------------------------------------------------------------------------
FRESHNESS, BECAUSE AN EXISTENCE CHECK CANNOT SEE IT
---------------------------------------------------------------------------
halo_rev_a's gerbers turned out to be 6,460 seconds OLDER than the board
they describe, which no "does the file exist" check can detect. So this
records the board's SHA-256 at cut time INSIDE the gerber comments and in
fab-manifest.json, and re-checks it afterwards. `--break-stale` touches the
board after cutting and the check must go red.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
OUT = os.path.join(REPLICA, "pcb", "out")
PCB = os.path.join(OUT, "halo_replica.kicad_pcb")
FAB = os.path.join(OUT, "fab")
DRCJ = os.path.join(OUT, "halo_replica.drc.json")
CLASSJ = os.path.join(OUT, "drc-classification.json")
BOARDJSON = os.path.join(REPLICA, "board", "board.json")

BANNER = [
    "NOT FOR FABRICATION. halo REPLICA - a reconstruction from photographs.",
    "1. 0.30 mm at 4 layers is BELOW PCBWay's 0.40 mm four-layer floor and",
    "   JLCPCB's 0.40 mm minimum. AS DRAWN THIS CANNOT BE ORDERED AT EITHER",
    "   HOUSE. The drawing is not moved to suit a process.",
    "2. The board's own DRC HAS ERRORS. See drc-classification.json:",
    "   they are classified, not cleared, because moving a MEASURED position",
    "   to satisfy a design rule would falsify a measurement.",
    "3. NO NETLIST BINDING. 65 nets read from the schematic, ZERO pads",
    "   attached. The copper's connectivity is UNKNOWN and every passive",
    "   value is CANNOT DETERMINE.",
    "4. U1 (nRF52832 WLCSP-50) has NO LAND PATTERN - the ball map is CANNOT",
    "   DETERMINE. U2 (Apple U1 UWB) is UNPOPULATED and has none either.",
    "5. The outer diameter is a BOUND, 24.95-26.34 mm. The drawn value is",
    "   not a settled diameter, and if it moves it moves DOWN.",
]


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _stamp(path, board_sha):
    """Put the banner into the file, in its own comment syntax."""
    txt = open(path, "r", encoding="utf-8", errors="replace").read()
    lines = BANNER + ["Board SHA-256 at cut time: %s" % board_sha,
                      "Cut by tools/f_fab.py at %s"
                      % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())]
    if path.endswith(".drl"):
        block = "".join("; %s\n" % l for l in lines)
        # Excellon: comments go after M48, before the tool table is read.
        i = txt.find("M48")
        j = txt.find("\n", i) + 1 if i >= 0 else 0
        txt = txt[:j] + block + txt[j:]
    elif path.endswith(".gbrjob"):
        return False
    else:
        block = "".join("G04 %s*\n" % l.replace("*", "") for l in lines)
        txt = block + txt
    open(path, "w", encoding="utf-8").write(txt)
    return True


def main():
    brk = "--break-stale" in sys.argv[1:]
    for p in (PCB, DRCJ, CLASSJ):
        if not os.path.exists(p):
            print("CANNOT DETERMINE — missing %s" % p)
            return 2

    sha_before = _sha(PCB)
    if os.path.isdir(FAB):
        shutil.rmtree(FAB)
    os.makedirs(FAB)

    r = subprocess.run(["kicad-cli", "pcb", "export", "gerbers",
                        "--output", FAB, "--no-protel-ext", PCB],
                       capture_output=True)
    if r.returncode != 0:
        print("CANNOT DETERMINE — gerber export failed: %s"
              % (r.stderr.decode() or r.stdout.decode())[-300:])
        return 2
    r = subprocess.run(["kicad-cli", "pcb", "export", "drill",
                        "--output", FAB, "--format", "excellon",
                        "--drill-origin", "absolute", "--excellon-units",
                        "mm", "--generate-map", "--map-format", "gerberx2",
                        PCB], capture_output=True)
    if r.returncode != 0:
        print("CANNOT DETERMINE — drill export failed: %s"
              % (r.stderr.decode() or r.stdout.decode())[-300:])
        return 2

    files = sorted(os.listdir(FAB))
    stamped = [f for f in files if _stamp(os.path.join(FAB, f), sha_before)]

    if brk:
        time.sleep(1.1)
        with open(PCB, "a") as f:
            f.write("\n")

    sha_after = _sha(PCB)
    fresh = sha_after == sha_before

    drc = json.load(open(DRCJ))
    cls = json.load(open(CLASSJ))
    n_err = sum(1 for v in drc["violations"] if v.get("severity") == "error")
    bj = json.load(open(BOARDJSON))

    manifest = {
        "tool": "tools/f_fab.py",
        "cut_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "board": os.path.relpath(PCB, REPLICA),
        "board_sha256_at_cut": sha_before,
        "board_sha256_now": sha_after,
        "freshness": "PASS — the gerbers describe this board"
                     if fresh else
                     "FAIL — the board changed after the set was cut. These "
                     "files describe a board that no longer exists.",
        "files": files,
        "files_stamped_with_the_banner": stamped,
        "verdict": "NOT FOR FABRICATION",
        "why_not_for_fabrication": BANNER,
        "drc_errors_at_cut": n_err,
        "drc_classification": cls["counts"],
        "thickness_mm_as_drawn": bj["parameters"]["thickness_mm"]["value"],
        "fabrication_delta": bj["parameters"]["thickness_mm"][
            "fabrication_delta"],
        "outer_diameter_bound_mm": bj["parameters"]["outer_diameter_mm"][
            "bound_mm"],
    }
    json.dump(manifest, open(os.path.join(FAB, "fab-manifest.json"), "w"),
              indent=1)

    print("f_fab — %d files in %s" % (len(files), os.path.relpath(FAB,
                                                                  REPLICA)))
    print("  banner stamped into %d of %d files (the .gbrjob is JSON and "
          "takes no comment; it is named in the manifest instead)"
          % (len(stamped), len(files)))
    print("  board sha at cut  %s" % sha_before[:16])
    print("  board sha now     %s" % sha_after[:16])
    print("  FRESHNESS %s" % ("PASS" if fresh else "FAIL — the board changed "
                              "after the cut; these files describe a board "
                              "that no longer exists"))
    print("  DRC at cut: %d errors — %s" % (n_err, cls["counts"]))
    print("  VERDICT NOT FOR FABRICATION, and the reason is in every file.")
    if brk:
        print("  BREAK ACTIVE: the board was touched after the cut.")
    return 0 if fresh else 1


sys.exit(main())
