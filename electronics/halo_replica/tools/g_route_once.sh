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
if pgrep -f freerouting >/dev/null 2>&1; then
  echo "NOTE: another freerouting is running on a different board:"
  pgrep -fl freerouting | head -2
fi

# 2. IS THERE MEMORY TO RUN A JVM? Measured, not assumed.
SWAP_USED=$(sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/')
SWAP_TOT=$(sysctl -n vm.swapusage | sed -E 's/.*total = ([0-9.]+)M.*/\1/')
PCT=$(python3 -c "print(int(100*$SWAP_USED/$SWAP_TOT))" 2>/dev/null || echo 0)
echo "swap ${SWAP_USED}M of ${SWAP_TOT}M used (${PCT}%)"
if [ "$PCT" -ge 70 ]; then
  echo "REFUSED: swap ${SWAP_USED}M of ${SWAP_TOT}M = ${PCT}%, against a 70% bar."
  echo "  (marginally over and catastrophically over want different responses, so the"
  echo "   measured number is here as well as the rule.)"
  echo "  Starting a JVM into that is the precondition"
  echo "  for the kernel panics this machine has had twice this week."
  echo "  Free memory first (idle terminals hold it), then re-run."
  exit 1
fi

# 3. Route, nice'd, one only.
echo "routing $(basename "$BOARD") — one process, nice 10"
nice -n 10 "$WS/ce-pcb/bin/route" "$BOARD" "$@"
