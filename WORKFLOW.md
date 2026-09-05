# The halo board workflow

**One command per stage, one verdict per stage, and the exit code *is* the
verdict.** `0 PASS · 1 FAIL · 2 CANNOT DETERMINE` — and CANNOT DETERMINE is not
a pass.

```bash
bin/halo doctor          # is everything this needs reachable?
bin/halo status          # what exists, and is anything stale?
bin/halo all             # sheet -> board -> DRC -> route -> pack
bin/halo selftest        # break every guard on purpose
```

Individual stages: `bin/halo build`, `bin/halo route`, `bin/halo pack`.
Variant defaults to `fab`.

---

## The pipeline

| stage | reads | writes | the question it answers |
|---|---|---|---|
| **sheet** | `schematic/schematic_fab.py` | `.kicad_sch`, **`.net`** | do the parts and nets exist |
| **board** | `.net`, `board_fab.py` | `.kicad_pcb` | is every part **on the board**, on a face, not overlapping |
| **drc** | `.kicad_pcb` | — | does **KiCad** agree |
| **route** | `.kicad_pcb` | `.ses`, `-routed.kicad_pcb` | are the nets **connected** |
| **pack** | `-routed.kicad_pcb` | `*.zip` | can a fab **build it** |

## Four traps this exists to prevent

Each cost a real half-hour on this board.

**1 · Stale inputs are silent.** `bin/sch all` refreshes the sheet, the PDF and
the SVG — and **not the netlist**. `board_fab.py` reads the *netlist*. So a
schematic edit landed, every command exited 0, and the board was built from the
previous part. Every stage now compares its inputs' mtimes against its outputs'
and **refuses on a stale one, naming the file and by how many seconds**.

**2 · A router that repeats itself is not slow.** freerouting ran four completed
passes reporting an identical score — `0.00, 106 unrouted` — every time. That
was read as "needs more passes" and given `-mp 100`: **3502 s of wall clock and
1913 s of CPU for no artifact at all.** An optimiser returning the same score
four times is not converging slowly, it is saying it cannot move. `route` now
watches for a score that does not change and reports **CANNOT ROUTE** rather
than letting a bigger budget hide it.

> The board was unroutable because **33 of 45 parts were not on the board.**
> Once placement was correct the *same router on the same settings* finished in
> **44.4 seconds**.

**3 · A timeout is a verdict, not a traceback.** `ce-pcb`'s route raised a bare
`subprocess.TimeoutExpired` stack trace. A timeout means CANNOT DETERMINE, with
what was learned attached.

**4 · Gerbers default to no copper.** `kicad-cli pcb export gerbers` with no
`--layers` writes User layers and **no copper**, and the directory looks
complete — plausible names, non-zero sizes, twenty-odd files. The 13
fabrication layers are named explicitly and the zip is verified after writing.

---

## Where the reusable engineering lives

**`ce-pcb/cepcb/place.py` — `Placer`.** Board scripts used to hand-roll ~230
lines of seeding, relaxation and side handling. `board_fab.py` is now **191
lines total**, and the placement is:

```python
p = Placer(b)
p.rings(RINGS, group_of, refs=sorted(fp_of))
p.keep_front(lambda r: r.startswith("U") or r == "AE1")
p.solve(clearance=0.20, edge_keep=R_EDGE_KEEP)
p.verify()          # reads back off the board; three verdicts
```

It owns the six ways placement silently goes wrong — the frame handoff, the
origin-vs-courtyard-centre offset, reading a courtyard from the face it is
actually on, polygon-vs-bounding-box, through-hole parts having no face, and
parts that cannot fit at any position. Its docstring carries the measurement
behind each.

**`ce-pcb/cepcb/board.py` — `Board.thickness()` / `.rules()`.** Both existed as
defaults nobody set: every board carried KiCad's **1.6 mm** and **0.20 mm**
clearance. Neither is a number anyone chose.

---

## The rule that produced all of it

**Read it back off the artifact, never off the variable you computed on the way
in.** Every check in this pipeline that could fail on a real defect is one that
asks the *board*, or asks *KiCad*, rather than asking the placement code what
it intended.

Two of today's defects were found by exactly that and by nothing else:

- 33 of 45 parts off the board — invisible to a keep-in test **sharing the
  coordinate frame with the bug**, and to a courtyard test measuring **relative
  distances**, which a rigid translation leaves *exactly* invariant.
- A battery holder that could not fit the board **at any position** — the
  survey that chose it read arc *control points* instead of arc *extent* and
  under-measured a courtyard by 3.9×. Three independent-looking text parses
  agreed to 0.01 mm and all three were wrong. `pcbnew`'s own geometry
  disagreed, and was right.

> **A geometry question goes to a geometry engine.** Reading coordinates out of
> a file answers "what points are written down", which is a different question
> and fails toward a *smaller* answer — the worst direction, because an
> under-measurement reads as a measurement while an empty result reads as a
> failure.
