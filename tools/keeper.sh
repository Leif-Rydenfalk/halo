#!/bin/bash
# keeper — every 5 minutes: push anything unpushed, and report lane liveness.
#
# Three failure modes cost this project work tonight, and this watches for the
# quietest one. Print-mode's 600 s background ceiling and upstream 500s both
# announce themselves. An agent that dies AT SPAWN does not: it holds its slot,
# reports "running", and writes nothing ever again. The only reliable signal is
# the mtime of its own transcript, so that is what this reads — never the
# agent's self-reported status, and never the commit rate.
SESSION=77728a87-0ee7-4382-a5f0-359f5220d100
SUB=~/.claude/projects/-Users-leifrydenfalk/$SESSION/subagents
LOG=/tmp/halo-keeper.log
GA=(-c user.name="Leif Rydenfalk" -c user.email="leif@rydenfalk.com")

push_repo() {
  local d=$1 n
  cd "$d" 2>/dev/null || return
  n=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
  [ "$n" = "0" ] && return
  if git push -q 2>/dev/null; then
    echo "$(date +%H:%M) pushed $n from $(basename $d)" >> $LOG
  else
    git pull --rebase -q 2>/dev/null && git push -q 2>/dev/null \
      && echo "$(date +%H:%M) pushed $n from $(basename $d) after rebase" >> $LOG \
      || echo "$(date +%H:%M) PUSH FAILED in $(basename $d) ($n unpushed)" >> $LOG
  fi
}

while true; do
  push_repo ~/dev/ce-workshop/ce-designs/halo
  push_repo ~/dev/ce-workshop
  # lane liveness: any transcript silent over 45 min while its agent still holds
  # a slot is a candidate for having died at spawn or stalled.
  now=$(date +%s)
  for f in $SUB/agent-*.jsonl; do
    [ -e "$f" ] || continue
    m=$(( (now - $(stat -f %m "$f")) / 60 ))
    if [ "$m" -gt 45 ] && [ "$m" -lt 10000 ]; then
      id=$(basename "$f" .jsonl)
      grep -q "^$(date +%F) .*$id" $LOG 2>/dev/null || \
        echo "$(date '+%F %H:%M') SILENT ${m}m $id" >> $LOG
    fi
  done
  sleep 300
done
