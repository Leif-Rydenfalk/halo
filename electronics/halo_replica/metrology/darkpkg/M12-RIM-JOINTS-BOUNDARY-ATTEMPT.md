# M12 — the rim tear-off joints: what the boundary engine says, and where it is the wrong instrument

*halo Replica, L7 DARK-PACKAGE DETECTOR lane, 2026-09-05.*
*Predictions written and committed **first**:
`P01-RIM-PADS-PREDICTIONS-BEFORE-MEASURING.md` (commit 47443bc). This file does
not edit them.*

**Reproduce:** `tools/d_rim.py step | null | limit | probe | count`.

---

## 0. The result

**No count is published.** The six visible joints present |z| **8–27** per
boundary against a rim bar of **23.7** — **2 of 20 boundaries clear**. The
`count` verb returns 5, and **drawing it showed those 5 are SMD capacitor pads
near the rim, not tear-off joints**; that number is withdrawn.

**But the cause has moved, and that is the finding.** M05 closed this on
**signal-to-noise** at 4.6 genuine px/mm. On this source, at 20–27 genuine px/mm,
**the joints are unmistakable** — core luma **222–242** against a surrounding
board ring of **34–56**. They are not lost in noise. They are lost because **a
straight-sided rectangle is the wrong model for a round solder blob**, which is a
statement about my instrument, not about the source.

## 1. The predictions, scored

| | prediction | outcome |
|---|---|---|
| **P1** contrast 100–200 luma, falsified below 60 | **HOLDS, but I over-predicted** — largest per-side step 64–99 luma, the bottom of the band |
| **P2** pads fail on edge LENGTH; falsified if the pad-scale limit lands below the measured step | **HOLDS on the verdict, WRONG on the reason** — see §3 |
| **P3** the rim null is *higher* than the board-average 33.4 | **FALSIFIED** — the rim null at pad scale is **23.7**, clearly *below* it |
| **P4** my bias is pessimism | **it cut both ways** — see §3 |
| **P5** no count predicted | held: none published |
| **P6** check for L1's disjoint-arc tell | applied; see §4 |

## 2. The numbers

**The bar is not a property of the board — it scales with the object.** The dark
packages' 100–160 luma was measured on a 3.2 mm object and **must not be quoted
at 1.1 mm**. Everything below is measured at pad scale, at the rim.

| quantity | value |
|---|---|
| rim null, phase-scrambled, pad scale | \|z\| p99 **13.8**, max 14.5 |
| **rim null, real rim, random place and angle** | \|z\| p99 **23.7**, max 27.5 → **the bar** |
| board-average null at package scale, for contrast | 33.4 |
| **pad-scale limit, pasted into the rim** | **140–170 luma** for 3 of 4 sides, **170–200** for 4 of 4, 5/5 sites reaching it |
| the six joints, per-boundary | \|z\| **8–27**, **2 of 20** clear the bar |

## 3. I corrected myself twice here, and the second correction was the wrong way

This is the part worth reading.

1. A per-side step measured at my **rough eyeballed seed** gave **64–99 luma**.
   A rough outline puts the "inside" band partly outside and vice versa, so that
   number is **diluted** — and the whole verdict was resting on it.
2. So I measured the same thing a second way that does not depend on my outline
   at all: brightest core against the board ring just beyond. That gave
   **174–191 luma** — *above* the 140–170 limit. I read that as **P2 falsified,
   the bar cleared, the count is on**, and said so.
3. **That was wrong, and the direct measurement settled it.** Core-minus-ring is
   a **peak-to-median** statistic and is a *loose upper bound* on a boundary
   **step**. What the detector integrates is the step, and measuring it directly
   — `d_rim probe`, per side, at the fit — gives **|z| 8–27 against a bar of
   23.7**.

> **A quantity measured a second way is not automatically the better one.** The
> outline-independent estimate was more robust *and further from what the method
> actually uses*. The number that decides a verdict has to be the number the
> method consumes, not a proxy that correlates with it.

P4 predicted my bias would be pessimism. It was pessimism first (a diluted step),
then optimism (a loose upper bound), and only the direct measurement was neither.

## 4. A mask that made an absence out of a coverage failure

The first `probe` returned **|z| = 0.0 on 11 of 20 sides** and I nearly reported
that as "no boundary". It is not. **A rim feature straddles the board edge**, and
fitting against the eroded board mask cuts its outer boundary, so the scan
returns nothing and prints a zero.

**That is this morning's saturated-check defect wearing a new face**: a number
that looks like strong evidence of absence and is actually the absence of a
measurement. Fixed by dilating the mask 1.5 mm outward, into the gasket and
background where a rim pad's outer boundary legitimately is. After the fix
**0 of 20 sides are unmeasured**, and `probe` now reports which sides were not
measured rather than scoring them zero.

**P6, the disjoint-arc tell:** the `count` verb's five detections span 45–322°
over 5 of 8 octants — *not* disjoint, so they pass L1's tell. **They still are not
joints.** Passing the tell is necessary and nowhere near sufficient, and that is
worth recording: a control that L1 built to catch a specific artifact does not
catch a detector that is simply looking at the wrong objects.

## 5. What I am NOT publishing, and why it is written down anyway

Looking at the photograph at native resolution, I can see **four bright solder
joints across the top rim and two rectangular copper pads at the bottom rim**.
Four plus two is six, and `docs/REFERENCE-TEARDOWN.md` says six.

> **This is NOT a count and must not be drawn or cited as one.** It is an
> eyeballed observation, and it is the single most suspect kind: **the number I
> expected is the number I saw.** The dossier's six is *still* neither confirmed
> nor refuted, exactly as M03 and M05 left it. It is recorded here only so the
> orchestrator knows the question is live on this source, and so that a later
> measurement can disagree with me.

The five `count` detections are withdrawn as joints and are on disk labelled as
capacitor pads.

## 6. What would settle it, and it is cheap

**A round-feature detector, not a rectangle one.** The joints are circular solder
blobs 1.3–1.6 mm across at 174–191 luma of core-to-surround contrast, in a source
with ~5× the genuine resolution of the one M05 closed on. `bin/boardmetro circle`
already fits circles with an inlier-fraction shape test that a square fails.

**That is a different instrument and it needs its own predictions written first,
its own rim-local null, and its own limit ladder.** Not run here: running it
straight after seeing six by eye is exactly how a count gets fitted to an
expectation, and this file exists partly to make that impossible to do quietly.

## 7. Status

| # | quantity | verdict |
|---|---|---|
| 1 | rim tear-off joint count | **CANNOT DETERMINE** — 2 of 20 boundaries clear the bar |
| 2 | the cause | **MOVED** — no longer signal-to-noise (M05); it is instrument–morphology mismatch on this source |
| 3 | the rim bar at pad scale | **MEASURED** — \|z\| 23.7, and *below* the board average, falsifying P3 |
| 4 | the pad-scale detection limit | **MEASURED** — 140–170 luma for 3 of 4 sides, 5/5 sites |
| 5 | the joints' visibility in this source | **MEASURED** — core 222–242 against ring 34–56; they are not lost in noise |
| 6 | the `count` verb's 5 | **WITHDRAWN as joints** — drawing them showed SMD capacitor pads |
| 7 | the dossier's six | **still neither confirmed nor refuted.** Do not cite this file as either |
