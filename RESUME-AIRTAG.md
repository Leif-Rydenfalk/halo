# RESUME — the AirTag / halo Replica lanes, paused 2026-09-05

*Paused on Leif's instruction: "we should focus on the microduck and not the airtag ... stop the
airtag stuff so we easily can resume it later." NOTHING WAS DISCARDED. Every lane's work was
committed before its process was stopped — see the checkpoint commit immediately below this file
in `git log`.*

## Why it was stopped, measured

    load average 13.48 / 13.77 / 15.80 on 8 cores
    swap 5648 MB used of 6144 MB - 495 MB free, on 8 GB physical
    AirTag lanes: 14 claude processes, 71.6 % CPU combined
    microduck:     2 processes, ~0 % CPU

`electronics/halo_replica/metrology/darkpkg/SCALE.md` records TWO KERNEL PANICS this week at this
swap pressure. A panic takes every session down, including the microduck lanes that were mid-print
on two 3D printers. The AirTag work was the entire load on the machine.

## The lanes that were live, and how to bring each back

| lane | role | age at pause |
|---|---|---|
| `?` | orchestrator / shell | 05:03 |
| `?` | orchestrator / shell | 00:00 |
| `?` | orchestrator / shell | 07:46:57 |
| `?` | orchestrator / shell | 12:52:53 |
| `?` | orchestrator / shell | 12:39:25 |
| `?` | orchestrator / shell | 12:29:38 |
| `?` | orchestrator / shell | 14:21:05 |
| `?` | orchestrator / shell | 07:46:55 |
| `?` | orchestrator / shell | 05:22:05 |
| `L1` | PHOTOGRAPH METROLOGY | 12:29:32 |
| `L2` | COMPONENT-SIDE METROLOGY | 12:15:26 |
| `L3` | BOM IDENTIFICATION | 12:29:29 |
| `L4` | STACKUP AND FABRICATION | 12:28:21 |
| `L7` | DARK-PACKAGE DETECTOR | 07:46:59 |

Each lane was launched with a full brief in its command line. To resume one, relaunch it with the
same brief — the briefs are recoverable from this file's sibling `RESUME-AIRTAG-briefs.txt`, which
holds each process's verbatim launch prompt as captured before the stop.

## What was already finished and needs no resumption

- **L10 BLIND RIM COUNT** — complete and pushed on branch `rimblind-99cab5fe`:
  `metrology/rimcount/R00-PREREGISTRATION.md` through `R04-COMPARISON.md`. Verdict CANNOT DETERMINE
  with four deciding numbers, and the post-disclosure comparison against the dossier's six. The
  instruments (`tools/r_circ.py` 16/16 selftest, `r_rimcount.py`, `r_frame.py`) are on that branch,
  as is `bin/boardmetro circles`. **That branch is a sanitised worktree: merge its NEW FILES only,
  never its deletions.**

## The state to check first on resume

Run `git log --oneline -5` and `git status` here before restarting any lane: the checkpoint commit
below captured 25 files that were in flight, including a modified
`electronics/halo_replica/tools/c_register.py`. Whoever resumes should read that diff first — it was
committed to avoid losing it, NOT because it was finished.
