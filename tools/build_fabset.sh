#!/bin/bash
# build_fabset — cut the factory's board pack, then REFUSE to let it ship
# unless the pack provably describes the board.
#
# THE DEFECT THIS GATE EXISTS FOR (2026-09-04, changelog 2026-09-04-...-antenna-match-off):
# the pack was cut at 18:40 from a board that had not been routed yet. Vias do
# not exist before routing, so kicad-cli exported PTH/NPTH drill files with
# ZERO holes — a four-layer board no fab can drill. The exporter exited 0, the
# pack index said READY, and check_fabset.py had to be written afterwards to
# catch it. The pack was also 12 669 s older than the board it claimed to be.
# Nothing re-cut the pack after routing, and nothing gated READY on the check.
#
# The fix at source: one script that does BOTH — export, then check, and the
# export only counts if the check exits 0. Run this, never `fab jlc` alone.
#
#   ce-designs/halo/tools/build_fabset.sh [--board out/halo_rev_a.kicad_pcb]
#
# Exit 0: every gate PASS. Exit 1: a gate failed — the pack on disk says FAIL
# in its own JSON and must not be re-indexed as READY.
set -uo pipefail
HALO="$(cd "$(dirname "$0")/.." && pwd)"
WS="$(dirname "$(dirname "$HALO")")"
BOARD="$HALO/electronics/halo_rev_a/out/halo_rev_a.kicad_pcb"
PACK="$HALO/out/release/board"
NETLIST="$HALO/electronics/halo_rev_a/out/halo_rev_a.net"
VERIFY="$HALO/out/verify"
rc=0

while [ $# -gt 0 ]; do
  case "$1" in
    --board) BOARD="$2"; shift 2 ;;
    *) echo "unknown arg $1" >&2; exit 3 ;;
  esac
done

[ -f "$BOARD" ] || { echo "REFUSED: no board at $BOARD" >&2; exit 3; }
mkdir -p "$VERIFY"

echo "== 1/4 fab jlc: BOM + CPL + gerbers + drills from $BOARD"
( cd "$WS" && ce-fab/bin/fab jlc "$BOARD" --out "$PACK" --check-against-kicad \
    > "$VERIFY/fab-jlc.log" 2>&1 )
if [ $? -ne 0 ]; then
  # ce-fab's own --check-against-kicad mis-grades bottom-side parts that carry
  # a rotation correction: its expected value omits the 180-rot bottom flip
  # its own writer applies (cefab/jlc.py:214-217 vs :592-594). Measured
  # 2026-09-05 on halo_rev_a: 9 rows, all B.Cu. The files are still graded by
  # steps 3/4 below, which re-derive every row from kicad-cli pos with the
  # flip included — do NOT edit ce-fab from this lane to make it green.
  echo "   note: fab jlc exited non-zero (its own cross-check's bottom-flip"
  echo "   gap); the pack is judged by check_cpl_rotations below."
fi

echo "== 2/4 check_fabset: read the pack back, cross-check vs the board"
# NO --round: the outline is Ø26.00 with THREE 26° keying notches cut to
# R12.60 at 0/120/240° (board.py, lane M's design.py). Measured extent
# 25.6138 x 26.0000 mm — 26.000 - 25.6138 = 0.386 mm is the notch depth at
# the measured angle, not an oval board. A round-only check would grade the
# keying as a defect. outline_matches_spec (26.0 ±0.5) still applies.
python3 "$HALO/tools/check_fabset.py" "$PACK" \
  --board "$BOARD" --expect-layers 4 --expect-outline-mm 26.0 \
  --json "$PACK/fabset-check.json" || rc=1

echo "== 3/4 check_bom_identity + check_lcsc_netlist + check_cpl_rotations"
python3 "$HALO/tools/check_bom_identity.py" "$PACK/halo_rev_a-BOM.csv" \
  --json "$VERIFY/bom-identity-check.json" --quiet || rc=1
echo "   bom identity: $(python3 -c "import json;print(json.load(open('$VERIFY/bom-identity-check.json'))['verdict'])")"
python3 "$HALO/tools/check_cpl_rotations.py" "$PACK" --board "$BOARD" \
  --json "$VERIFY/cpl-rotations-check.json" --quiet || rc=1
echo "   cpl rotations: $(python3 -c "import json;print(json.load(open('$VERIFY/cpl-rotations-check.json'))['verdict'])")"

echo "== 4/4 check_lcsc_netlist: the exported netlist's codes vs the catalogue"
python3 "$HALO/tools/check_lcsc_netlist.py" --net "$NETLIST" \
  --json "$VERIFY/lcsc-netlist-check.json" --quiet || rc=1
echo "   netlist codes: $(python3 -c "import json;print(json.load(open('$VERIFY/lcsc-netlist-check.json'))['verdict'])")"

if [ "$rc" -eq 0 ]; then
  echo "FABSET GATE: PASS — the pack describes the board"
else
  echo "FABSET GATE: FAIL — do NOT mark the fabrication artifact READY"
fi
exit "$rc"
