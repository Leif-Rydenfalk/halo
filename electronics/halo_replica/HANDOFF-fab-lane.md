# Fab lane — handoff, paused 2026-09-05

**Paused at Leif's instruction; microduck is the priority.** Nothing here is
abandoned and nothing is mid-edit. Every process this lane started is stopped.

## Where to resume

```bash
cd ~/dev/ce-workshop/ce-designs/halo
bin/halo status          # what exists, and is anything stale
bin/halo doctor          # is everything reachable
bin/halo all             # sheet → board → DRC → route → render → pack
```

Exit code **is** the verdict: `0 PASS · 1 FAIL · 2 CANNOT DETERMINE`.
Stages, and the four traps the pipeline prevents: `WORKFLOW.md`.

## Two boards, both real, both committed

| | `fab/` | `apple/` |
|---|---|---|
| outline | Ø30 mm disc | **Apple's measured 75-point profile, 24.6624 × 24.7263 mm** |
| DRC errors | **0** | **0** |
| nets bound | 63 / 63 | 63 / 63 |
| routed | **yes** — 565 tracks, 58 vias, 4 layers | **not yet** |
| unconnected | **5** | 112 (unrouted) |
| package | `halo_replica_jlc_0.8mm.zip`, `z_fabcheck` PASS | not cut |

`apple/` is the closer answer to "the Apple replica board" and is the one to
finish. It is placed, DRC-clean and net-bound; **it has never been routed.**

## The single next action

```bash
~/dev/ce-fleet/bin/heavy && \
ce-pcb/bin/route electronics/halo_replica/apple/out/halo_replica_apple.kicad_pcb \
                 --passes 30 --timeout 1200
```

Then `bin/halo render` and a package. Expect it to route: the fab board, same
parts and same rules, went 112 → 5 in 251 s once its placement was correct.

## What is NOT true, and must not be claimed

- **Nobody has built one.** Neither board has been fabricated or powered on.
- **`fab/` has 5 unconnected nets.** Four are U1 pads — QFN-48 escape routing.
  30 and 120 passes both stop at exactly 5, so *this router is finished, not
  slow*. Fanout gets 5 → 4 and introduces 13 DRC errors: net worse.
- **The assembly is not orderable.** 5 real LCSC codes against 20 blank. A blank
  is an **honest refusal** naming an MPN a human must look up — JLC's importer
  reads that column literally and silently drops any line it cannot match.
- **0.4 mm is not orderable at 4 layers** (measured live in JLC's configurator,
  with both controls). Order the **0.8 mm** zip.
- **`apple/` swaps four connectors to 1.27 mm SMD** — pin counts unchanged, so
  nets are untouched, but it is a departure from the fab sheet.

## The three findings worth carrying, whatever happens to this board

1. **An optimiser returning the same score repeatedly is not slow — it cannot
   move.** Four identical freerouting passes were read as "needs more passes"
   and cost 3502 s for no output. The board was unroutable because **33 of 45
   parts were not on it.** Same rule across runs: 30 and 120 passes giving
   identical results means finished.
2. **A check that shares a frame, an input, or an assumption with the thing it
   checks cannot fail on it.** A keep-in test in the bug's own coordinate frame;
   a courtyard test measuring relative distances, exactly invariant under the
   translation that *was* the defect; an outline check counting ops where a
   correct circle and two disjoint arcs both give 2.
3. **A geometry question goes to a geometry engine.** Three text parses of a
   footprint agreed to 0.01 mm and all three were wrong — arc *control points*
   are not arc *extent*. `pcbnew` disagreed and was right. Agreement between
   methods that share a blind spot is one measurement, not three.

Evidence: `evidence/E09`, `evidence/E10`. Tools: `ce-pcb/cepcb/place.py`,
`tools/z_fabcheck.py`, `tools/g_package.py`, `tools/g_route_once.sh`.
