#!/bin/bash
# route_board — autoroute halo_rev_a, then prove the router did not eat the
# copper that was solved rather than drawn.
#
#   ce-designs/halo/tools/route_board.sh [--passes N] [--timeout S]
#
# ONE COMMAND, because the pieces were three and the middle one was optional.
# `ce-pcb/bin/route` exports Specctra, routes and imports the SES; halo's
# `dsnfix.py` corrects three things KiCad's export says that are false about
# THIS board (In1/In2 are poured planes and come out `signal`; GND and VDD
# arrive as 63 pin-to-pin connections the pours already make; the antenna and
# the NFC spiral come out `route`, meaning rippable). dsnfix existed and had
# no way to be invoked from the seam, so it was run by hand or not at all —
# and the three autoroutes that timed out at 900, 3300 and 2400 s were run on
# the unfiltered file. `--dsn-filter` is the hook that closes that gap.
#
# THE VERDICT IS NOT FREEROUTING'S. `route` re-runs KiCad's DRC, which answers
# "is this manufacturable". `check_routed.py` answers the other question — is
# this still my board — by comparing the protected nets' geometry before and
# after. A rerouted antenna is still electrically connected and still passes
# the DRC; it is just no longer the thing that was simulated.
#
# Exit 0: the routed board is on disk AND check_routed PASSes.
# Exit 1: it routed and something is wrong with the result — read the rows.
# Exit 2: a tool is missing or the filter refused; nothing was routed.
set -uo pipefail
HALO="$(cd "$(dirname "$0")/.." && pwd)"
WS="$(dirname "$(dirname "$HALO")")"
BOARD="$HALO/electronics/halo_rev_a/out/halo_rev_a.kicad_pcb"
FILTER="$HALO/electronics/halo_rev_a/dsnfix.py"
OUT="$HALO/electronics/halo_rev_a/out/halo_rev_a-routed.kicad_pcb"
VERIFY="$HALO/out/verify"
PASSES=10
TIMEOUT=1800

while [ $# -gt 0 ]; do
  case "$1" in
    --passes)  PASSES="$2";  shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    -o|--out)  OUT="$2";     shift 2 ;;
    *) echo "unknown arg $1" >&2; exit 3 ;;
  esac
done

[ -f "$BOARD" ]  || { echo "REFUSED: no board at $BOARD" >&2; exit 3; }
[ -f "$FILTER" ] || { echo "REFUSED: no DSN filter at $FILTER" >&2; exit 3; }
mkdir -p "$VERIFY"

echo "== 0/3 the tools, asked of the tool that owns them"
"$WS/ce-pcb/bin/route" --doctor || {
  echo "REFUSED: ce-pcb/bin/route --doctor did not exit 0. NOTE, 2026-09-05:" >&2
  echo "  do NOT conclude from a bare \`java -version\` that there is no Java" >&2
  echo "  here. /usr/bin/java is Apple's stub and Homebrew's openjdk is" >&2
  echo "  keg-only, off PATH, at /opt/homebrew/opt/openjdk/bin/java. The jar" >&2
  echo "  is at ~/.local/share/freerouting, outside the workshop tree." >&2
  exit 2; }

echo "== 1/3 route: export DSN -> dsnfix -> freerouting -> SES -> DRC"
"$WS/ce-pcb/bin/route" "$BOARD" -o "$OUT" \
  --dsn-filter "$FILTER" --passes "$PASSES" --timeout "$TIMEOUT" \
  --json-out "$VERIFY/route-run.json"
rc=$?
if [ ! -f "$OUT" ]; then
  echo "FAIL: no routed board was written (route exit $rc)" >&2
  exit 2
fi
# --json-out, NOT `--json > file`. MEASURED 2026-09-05: pcbnew's wxWidgets
# layer writes "Debug: Adding duplicate image handler" to stdout from C++, so
# the redirect captured 40 lines of noise and then the JSON. The parse threw
# "Extra data: line 1 column 2", $SES came back empty, --dsn never reached
# check_routed, and R1 and R8 reported CANNOT DETERMINE for a reason that had
# nothing to do with the board. The refusal below is why that cannot recur
# silently.
SES="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['ses'])" \
        "$VERIFY/route-run.json")" || SES=""
if [ -z "$SES" ] || [ ! -f "$SES" ]; then
  echo "REFUSED: could not read the SES path out of $VERIFY/route-run.json." >&2
  echo "  check_routed's protected-copper tolerance comes from that file's" >&2
  echo "  own (resolution ...); without it R1 and R8 are CANNOT DETERMINE," >&2
  echo "  and a routed board nobody checked for protected copper is not a" >&2
  echo "  routed board this lane will publish." >&2
  exit 2
fi

echo "== 2/3 check_routed: is this still my board?"
# --dsn is REQUIRED, not optional. The protected-net match tolerance is one
# step of the interchange format's own (resolution ...), read out of the file
# the copper actually travelled through. Without it check_routed reports
# CANNOT DETERMINE rather than inventing a number — measured 2026-09-05, the
# round trip moves a protected segment by up to 71 nm and an exact compare
# called 235 surviving segments destroyed.
python3 "$HALO/tools/check_routed.py" "$BOARD" "$OUT" \
  --protect ANT_FEED,NFC1,NFC2 --dsn "$SES" \
  --json "$VERIFY/routed-check.json"
crc=$?

echo "== 3/3 verdict"
python3 - "$VERIFY/routed-check.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
b, a = d["drc_before"], d["drc_after"]
print("  unconnected  %d -> %d   (%+d)" % (b["unconnected"], a["unconnected"],
                                           a["unconnected"] - b["unconnected"]))
print("  DRC errors   %d -> %d   warnings %d -> %d"
      % (b["errors"], a["errors"], b["warnings"], a["warnings"]))
print("  check_routed %s  %s" % (d["verdict"], d["counts"]))
PY
[ "$crc" -eq 0 ] && echo "ROUTE GATE: PASS" || echo "ROUTE GATE: not clean — read the rows above"
exit "$crc"
