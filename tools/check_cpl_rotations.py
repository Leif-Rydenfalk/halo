#!/usr/bin/env python3
"""check_cpl_rotations — verify the pack's CPL rotations and positions against
KiCad's own placement export, applying the vendored JLC transform INCLUDING
the bottom-side flip.

Why this exists (measured 2026-09-05): ce-fab's built-in cross-check
(`fab jlc --check-against-kicad`) grades a bottom-side part that carries a
rotation-table correction as DISAGREE, because its expected value omits the
`180 - rot` bottom flip its own writer applies (cefab/jlc.py:214-217 vs
:592-594). On halo_rev_a that mis-graded 9 rows — every one a B.Cu part with
a table offset (U1, U2, L1, X1, X2, C9..C12) — and turned a correct CPL into
a headline FAIL. The defect belongs to ce-fab and is recorded in the
changelog; this tool is halo's independent re-grade, not a waiver: it
re-derives every row from kicad-cli's own export and the vendored
transformations.csv, with the flip the JLC plugin documents
(plugins/process.py:245-246: "the bottom side inverts and lands 180 out").

    python3 tools/check_cpl_rotations.py <pack_dir> --board <board.kicad_pcb>
        [--json out.json]

Exit 0 PASS · 1 FAIL · 2 CANNOT DETERMINE.

  P1 pos_export_runs   the oracle must answer, not the tool's memory of it
  P2 positions_match   a part in the wrong place is wrong however it is rotated
  P3 rotations_match   a part at the wrong angle is a dead board
"""
import argparse, csv, json, math, pathlib, re, subprocess, sys, tempfile, shutil
from datetime import datetime, timezone

PASS, FAIL, CD = "PASS", "FAIL", "CANNOT DETERMINE"
RANK = {PASS: 0, CD: 1, FAIL: 2}
TABLE = pathlib.Path.home() / \
    "dev/ce-workshop/ce-fab/data/vendor/transformations.csv"


def load_table(path=TABLE):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                rows.append((re.compile(r["Regex To Match"]),
                             float(r["Rotation"]),
                             float(r["Delta X"]), float(r["Delta Y"]),
                             r["Regex To Match"]))
            except (KeyError, ValueError, re.error):
                continue
    return rows


def correction_for(footprint, table):
    for rx, rot, dx, dy, src in table:
        if rx.search(footprint or ""):
            return rot, dx, dy, src
    return 0.0, 0.0, 0.0, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pack")
    ap.add_argument("--board", required=True)
    ap.add_argument("--tol-mm", type=float, default=0.002)
    ap.add_argument("--tol-deg", type=float, default=0.01)
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    cpl_path = pathlib.Path(a.pack) / "halo_rev_a-CPL.csv"
    if not cpl_path.is_file():
        print(f"CANNOT DETERMINE: no CPL at {cpl_path}", file=sys.stderr)
        return 2
    with open(cpl_path, newline="", encoding="utf-8-sig") as fh:
        cpl = {r["Designator"]: r for r in csv.DictReader(fh)}

    cli = shutil.which("kicad-cli")
    if not cli:
        print("CANNOT DETERMINE: kicad-cli not found", file=sys.stderr)
        return 2
    tmp = tempfile.mkdtemp(prefix="halo-poscheck-")
    pos_csv = pathlib.Path(tmp) / "pos.csv"
    p = subprocess.run([cli, "pcb", "export", "pos", "-o", str(pos_csv),
                        "--format", "csv", "--units", "mm", "--side", "both",
                        "--use-drill-file-origin", a.board],
                       capture_output=True, text=True, timeout=600)
    if p.returncode != 0 or not pos_csv.is_file():
        print(f"CANNOT DETERMINE: pos export failed: "
              f"{(p.stderr or p.stdout)[:200]}", file=sys.stderr)
        return 2
    with open(pos_csv, newline="", encoding="utf-8-sig") as fh:
        pos = {r["Ref"]: r for r in csv.DictReader(fh)}
    shutil.rmtree(tmp, ignore_errors=True)

    table = load_table()
    rows, n_ok = [], 0
    for ref, c in sorted(cpl.items()):
        k = pos.get(ref)
        if not k:
            rows.append({"rule": "pos_export_runs", "ref": ref,
                         "verdict": FAIL,
                         "why": "kicad-cli pos did not emit this designator"})
            continue
        side = (k.get("Side") or "top").lower()
        bottom = side.startswith("bottom")
        rot_db, dx, dy, matched = correction_for(k["Package"], table)

        # the vendored transform, WITH the bottom flip (process.py:245-246)
        exp_rot = 180.0 - float(k["Rot"]) if bottom else float(k["Rot"])
        exp_rot %= 360.0
        exp_rot = (exp_rot + rot_db) % 360.0
        drot = min(abs(exp_rot - float(c["Rotation"])),
                   360.0 - abs(exp_rot - float(c["Rotation"])))

        # position: same frame as the pack (ce-fab shares the aux/drill origin
        # with the pos export; measured 2026-09-05: pack Mid X/Y equal pos
        # PosX/PosY exactly, y-down, so the deltas cancel and the only thing
        # left to verify is the table delta and the rotation).
        exp_x = float(k["PosX"])
        exp_y = float(k["PosY"])
        r = math.radians(float(k["Rot"]))
        rs, rc = math.sin(r), math.cos(r)
        ox, oy = (dx * rc + dy * rs, dx * rs - dy * rc) if bottom \
            else (dx * rc - dy * rs, dx * rs + dy * rc)
        dxmm = abs(exp_x + ox - float(c["Mid X"]))
        dymm = abs(exp_y + oy - float(c["Mid Y"]))

        ok = dxmm <= a.tol_mm and dymm <= a.tol_mm and drot <= a.tol_deg
        n_ok += ok
        rows.append({"ref": ref, "side": side, "matched": matched,
                     "dx_mm": round(dxmm, 4), "dy_mm": round(dymm, 4),
                     "drot_deg": round(drot, 3),
                     "kicad_rot": float(k["Rot"]),
                     "cpl_rot": float(c["Rotation"]),
                     "expected_jlc_rot": round(exp_rot, 3),
                     "verdict": PASS if ok else FAIL,
                     "why": (f"{'bottom' if bottom else 'top'} side, "
                             f"table {matched or 'none'}: expected "
                             f"{exp_rot:.2f} deg, CPL says "
                             f"{c['Rotation']}; pos dx {dxmm:.4f} dy "
                             f"{dymm:.4f} mm")})
        # P1 sanity: the oracle must know the side it reported
        if (c.get("Layer") or "").lower().startswith("bottom") != bottom:
            rows[-1]["verdict"] = FAIL
            rows[-1]["why"] += "; CPL layer disagrees with kicad-cli side"

    bad = sum(1 for r in rows if r["verdict"] != PASS)
    out = {"$halo": 1, "tool": "tools/check_cpl_rotations.py",
           "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "cpl": str(cpl_path.resolve()), "board": str(pathlib.Path(a.board).resolve()),
           "table": str(TABLE), "rows_checked": len(rows), "agree": n_ok,
           "disagree": bad,
           "verdict": PASS if rows and bad == 0 else (FAIL if rows else CD),
           "why": ("every CPL row re-derived from kicad-cli pos + the vendored "
                   "transform incl. the bottom flip agrees with the pack"
                   if bad == 0 else
                   f"{bad} row(s) disagree with the re-derived transform"),
           "rows": rows,
           "command": "python3 " + " ".join(sys.argv[0:1] + sys.argv[1:])}
    if a.json:
        pathlib.Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.json).write_text(json.dumps(out, indent=1) + "\n")
    if not a.quiet:
        print(f"# check_cpl_rotations — {len(rows)} CPL rows vs kicad-cli pos")
        for r in rows:
            if r["verdict"] != PASS:
                print(f"  [{r['verdict']}] {r['ref']}: {r['why']}")
        print(f"{n_ok}/{len(rows)} agree — {out['verdict']}"
              + ("  (ce-fab's own --check-against-kicad omits the bottom flip"
                 " and mis-grades these rows; see this file's docstring)"
                 if any(r["verdict"] == PASS for r in rows) and bad == 0 else ""))
    return {PASS: 0, FAIL: 1, CD: 2}[out["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
