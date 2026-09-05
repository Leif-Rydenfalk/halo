#!/bin/zsh
# g_route_once — route a board, and REFUSE if one is already routing it.
#
# Written after four identical freerouting JVMs ran on one .dsn writing one .ses,
# at 0.1 GB free with swap 92% full, on a machine that has kernel-panicked twice
# this week. The cause was a retry path that checked THE OUTPUT FILE and never
# checked FOR A RUNNING PROCESS — testing the wrong thing and getting a plausible
# answer. They do not merely duplicate work: they RACE on one .ses, and a
# partially-written .ses read back as a routing result looks valid and is not.
#
#   tools/g_route_once.sh <board.kicad_pcb> [extra route args...]
#
# Exit 0 routed · 1 refused or failed · 2 a precondition could not be measured.
set -uo pipefail
BOARD="${1:?usage: g_route_once.sh <board.kicad_pcb> [args...]}"; shift || true
DSN="${BOARD%.kicad_pcb}.dsn"
WS="$HOME/dev/ce-workshop"

# 1. IS ONE ALREADY RUNNING ON THIS BOARD? Check the PROCESS, not the file.
#
# MATCH ON THE TOOL'S ACTUAL ARGUMENTS, NEVER ON A BARE NAME. Every Claude session
# on this machine carries its entire briefing document in its argv, so a bare
# `pgrep -f freerouting` matches any session whose brief mentions the word — and
# for as long as that session lives, because an argv is fixed at exec. That is how
# this guard's own author reported "no router is running" while one had been going
# for seventeen minutes. The pattern below requires the jar name AND this board's
# .dsn path together, which a prompt will never contain.
#
# THE FIRST THING THIS GUARD DID WAS CATCH ITS AUTHOR'S OWN FALSE REPORT.
if pgrep -f "freerouting.*$(basename "$DSN")" >/dev/null 2>&1; then
  echo "REFUSED: a router is already running on $(basename "$DSN"):"
  pgrep -fl "freerouting.*$(basename "$DSN")" | head -3
  echo "  Four of these once raced on one .ses. Wait for it, or kill it deliberately."
  exit 1
fi
# any freerouting at all is also worth naming — this machine has 8 GB
# NOTE-ONLY, and it MISFIRES BY CONSTRUCTION: `pgrep -f freerouting` matches any
# process whose argv contains the word, which includes the zsh wrapper that
# launched the router and any Claude session whose brief mentions it. Measured:
# it named pid 56691, a /bin/zsh -c line, as "another freerouting". Restricted to
# processes whose executable is actually java; ce-fleet/bin/heavy does this
# properly, by executable path, and is the leg that refuses.
if pgrep -f "openjdk.*freerouting-.*\.jar" >/dev/null 2>&1; then
  echo "NOTE: another freerouting is running on a different board:"
  pgrep -fl "openjdk.*freerouting-.*\.jar" | head -2
fi

# 2. IS THE MACHINE ABLE TO TAKE ANOTHER HEAVY TOOL AT ALL?
#
# THE OLD LEG HERE GATED ON SWAP RATIO AND WAS WRONG. macOS grows its swap file
# on demand, so a high ratio is not a shortage: measured 2026-09-05, swap went
# 7168M -> 9216M inside an hour on a healthy machine, and this leg would have
# refused a launch at 34% memory free with 18 GiB of VM space spare. The signals
# that actually cap a JVM are memory_pressure free % and free space on
# /System/Volumes/VM, not the ratio.
#
# AND THE HOLE THIS LEG COULD NOT SEE, which is the more important one: legs 0
# and 1 look for A ROUTER. They are blind to a heavy tool of a DIFFERENT KIND -
# FreeCAD, openEMS, a solver - already mid-flight, because no lane can see
# another lane's processes. Load hit 37 with three heavy tools running from
# three sessions, none of which knew about the others. ce-fleet/bin/heavy counts
# them machine-wide BY EXECUTABLE PATH, never by command line (every Claude
# session's argv contains its whole brief, so `pgrep -f <word>` is unreliable by
# construction - measured there at 14 Claude processes live, 0 miscounted).
# THE CONTRACT (ce-workshop-d1, 2026-09-05), and the two absences are opposite:
#   exit 0  proceed
#   exit 1  refuse - the machine is measurably too busy
#   exit 2  REFUSE - it RAN and could not read memory_pressure or the VM volume,
#           so the machine's state is UNKNOWN, and unknown is exactly when not to
#           add a JVM. A tool that could not measure is a worse position than
#           either green or red.
#   absent  PROCEED, loudly. A capacity gate is not an authorization gate; if
#           ce-fleet is missing or this is a machine without it, hard-refusing
#           would stop all work to prevent a POSSIBLE overload. The absence is
#           named instead, so it is visible rather than silently "no check".
HEAVY="${HEAVY_BIN:-$HOME/dev/ce-fleet/bin/heavy}"
if [ -x "$HEAVY" ]; then
  # Our own per-dsn lock and this are different questions; machine-wide capacity
  # is the cheaper refusal, so it goes first.
  # CAPTURE THE STATUS DIRECTLY. `if ! OUT=$(cmd); then RC=$?` records the
  # NEGATION's status, which is 0 exactly when the command failed - so this
  # printed "REFUSED ... (exit 0)" while refusing. A guard that reports success
  # while refusing is the same defect as a pipe returning head's exit code.
  OUT=$("$HEAVY" 2>&1); RC=$?
  if [ "$RC" -ne 0 ]; then
    echo "$OUT"
    echo "REFUSED by ce-fleet/bin/heavy (exit $RC): the MACHINE cannot take"
    echo "  another heavy tool right now, whatever this .dsn's own state is."
    exit "$RC"
  fi
  echo "$OUT"
  unset OUT RC
else
  echo "CANNOT DETERMINE: $HEAVY is not executable, so machine-wide capacity was"
  echo "  NOT checked. Proceeding on the per-dsn lock alone, which is blind to"
  echo "  FreeCAD, openEMS and solvers. Install ce-fleet to close this."
fi

# 3. Route, nice'd, one only.
echo "routing $(basename "$BOARD") — one process, nice 10"
nice -n 10 "$WS/ce-pcb/bin/route" "$BOARD" "$@"
