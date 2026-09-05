# L5b BOARD BUILD — handoff, 2026-09-05

**SIDE NAMING.** Every file in this folder describes **the side carrying the SoC and
the shield can**. Three sources use "front" for two different faces; the word is not
used here. Apple's FCC caption "MLB - Front", O'Flynn's `backside-fullres.jpeg` and
this folder's geometry are all THIS face.

**THE FRAME.** Board centre in `images/airtag/oflynn-backside-fullres.jpeg` at
`origin_px (1522.56, 1738.80)`, `106.313 px/mm`, `+x right, +y DOWN`, theta from +x
through +y. Every millimetre in this folder is in that frame and inherits its scale.
The scale basis is M02's `m_scale_at` at the board, transferred by `c_register`.

---

## What exists

| file | what it is | verdict |
|---|---|---|
| `board.json` | the parameterised board — ONE scale number drives everything | on disk |
| `outline/outline-fit-oflynn.json` | **the FIT**: circle + 4 chords, superellipse + 7 facets, with every residual and every control | exit 0 PASS |
| `outline/outline-photo6.json` | raw silhouette, FCC photo 6 — **evidence, never merged into a fit** | — |
| `out/board-front.png` | the render: fitted outline + 97 markers + the on-board legend | exit 0 PASS |
| `out/compare-front.png` | **OURS \| APPLE'S \| OVERLAY** at one shared 48 px/mm | exit 0 PASS |
| `../tools/p_fit.py` | photo profile → manufacturable primitives, or refuse | 0/1/2 |
| `../tools/p_render.py` | board.json + fit + handoff → picture | 0/1/2 |
| `../tools/p_compare.py` | the comparison harness | 0/1/2 |

```bash
python3 tools/p_fit.py --px-per-mm 106.31295578013115 \
  --scale-basis "M02 m_scale_at photo6 at the board, transferred by c_register"
python3 tools/p_render.py
python3 tools/p_compare.py && open board/out/compare-front.png
```

---

## The numbers, each with its input

**Outer.** Circle **D = 25.1593 mm** clipped by **4 straight chords**, largest
`145.25–189.50°` at 11.521 mm offset, 9.461 mm span.

| model | resid sd | p95 | inliers ±0.15 mm |
|---|---|---|---|
| plain circle | 0.5629 mm | 1.474 mm | **43.6 %** |
| circle + 4 chords | **0.2771 mm** | 0.713 mm | **55.8 %** |

That diameter is **DERIVED, NOT INDEPENDENT** — it inherits the same registration
scale as everything else in this frame and must never be quoted as a fourth opinion
on the OD. **The OD is a BOUND, 24.95–26.34 mm, and if it moves it moves DOWN.**

**Hole.** Superellipse (2a 13.497, 2b 13.283 mm, n 2.449, φ 5.35°) + **7 straight
facets**. Residual **0.3342 → 0.1987 mm**. **NO hole diameter is published.**

**Comparison, measured off the montage.**

| | value |
|---|---|
| X1 scale match | OURS 24.543 mm vs APPLE'S 24.783 mm, **0.97 %** |
| X4 outline residual | **RMS 0.413 mm**, p95 0.843 mm, 654 rays |
| X5 component landing | **4.23× enrichment** over 4000 random annulus positions |
| X6 disagreement map | ≤0.15 mm **51 %** of perimeter · 0.15–0.40 mm 26 % · >0.40 mm 12 % · no ray 9 % |
| X6 worst arcs | 82.8–101.0° peak 0.901 · 114.0–119.5° peak 0.979 · 282.9–286.0° peak 0.878 · 74.9–79.1° peak 0.746 mm |

---

## Every control, and what was seen when it fired

An assertion never seen to fail is not known to work. **All of these were watched.**

| control | what it tests | fired by | seen |
|---|---|---|---|
| N1 | the fitter invents a flat where there is none | `--selftest-break N1` (perfect circle + a real 1.4 mm flat) | 1 chord found, exit 1 |
| N1b | pixel noise promoted to geometry | `--selftest-break N1b` (noisy circle + a real 1.0 mm flat) | 1 chord found, exit 1 |
| N2 | the fitter cannot recover a flat it was handed | `--selftest-break N2` (plain circle in place of the chord input) | 0 recovered, exit 1 |
| N3 | **a line must beat the circle on INLIER FRACTION**, not on residual | a 0.5 mm curved Gaussian dent | **REFUSED as not-a-flat** — unplanned, and it is a second demonstration that N3 has teeth |
| N4 | the residual describes the chords | chords displaced +0.30 mm | sd 0.2771 → 0.3161, inliers 0.558 → 0.482 |
| H2 | the superellipse earns 2 extra parameters over a circle | fitting both to a synthetic PURE CIRCLE | floor 1.53 % vs real 7.50 % → EARNED |
| H3 | 7 facets earn 14 extra parameters | the same detector on a synthetic PURE superellipse | floor −0.31 % (1 fabricated facet) vs real 40.53 % → EARNED |
| R1 | blank render | — | not fired |
| R2 | a filled disc passing as an annulus | — | not fired |
| R3 | wrong drawn scale | `--break-scale 1.10` | 8.80 %, exit 1 |
| R5 | a silently dropped marker | `--break-drop 5` | accounting identity broke, exit 1 |
| R7 | **independent rim cross-check** | — | **CORROBORATED, see below** |
| X1 | the two panels are not at the same scale | see the defect log | fired at 3.20 % and was fixed at its cause |
| X3 | the comparison numbers do not depend on the alignment | `--break-rotation 12` | X4 0.413 → 0.470 mm, **X5 4.23× → 1.44× and X5 FIRES** |
| X5 | the markers are decoration | the same rotation | fires |

---

## R7 — a corroboration that could have failed and did not

L1 flags **14 of 95** bright rows `on_rim_material_suspect` using *r ÷ their RAW
measured local edge radius*. R7 uses *r ÷ the FITTED outline radius* — a different
denominator, from a model L1 never saw, and it also covers the blue rows their test
never ran on.

**16 of 100 rows beyond 0.95. Intersection 14. L1-only 0 — L1's set is CONTAINED in
mine.** Two methods that could have disagreed did not.

My two extras: **B011 at 0.9648** (marginal) and **D004 at 1.0413** — a *blue-body*
row sitting **outside the fitted outline**, which L1's radial test could never have
flagged because it ran on the 95 bright rows only. **Candidate 15th rim-suspect,
reported and not assumed.**

---

## What is NOT drawn, and each has a different reason

- **3 handoff rows** flagged `do_not_draw_as_component` — 2 merged pad runs (B000
  7.30 mm, B001 14.48 mm long side) and D001, an edge-bright strip at 4.1:1 that an
  IC body cannot be. Counted on the picture with their reasons.
- **Every neutral-black IC package, INCLUDING THE LARGEST ONE** — CANNOT DETERMINE
  after three detectors, one of which returned an answer that was purely a function
  of the operator's box (34 % swing on padding alone). **The dark areas of our board
  SHOULD look sparse. That is the data being honest, not the drawing being broken.**
- **4 named absences**, drawn as magenta `?` — two gold-ringed round parts, the large
  silver clip beside the hole. `position_eyeballed_mm`, `measured:false`,
  `do_not_draw_as_measured:true`, and the render honours all three.
- **Rim pads** — count CANNOT DETERMINE and CLOSED. The withdrawn 15- and 13-pad
  candidate angle sets failed a positive control and must never be drawn.
- **The three antennas** — not on this PCB at all (E01). Never in copper.
- **The NFC / voice coil** — wound magnet wire, not a trace (E02, and which of the
  two it is remains OPEN).
- **The U1 footprint** — size CANNOT DETERMINE: an independent remeasure of the can
  swings **6.735 → 7.891 mm on the operator's padding alone**, and the only handoff
  row at that location is flagged `merged_pad_run`. **U1 IS UNPOPULATED and the board
  legend says so ON THE BOARD**, in the measured quietest arc of the annulus.
- **Copper, traces, vias, silkscreen beyond that legend** — not measured, not drawn.

---

## What was discarded, and why

- **Painting our parts with median RGB sampled from Apple's photograph.** It IS a
  measurement — that is not the objection. It makes the comparison **CIRCULAR**: the
  two panels would have to agree on colour because we copied it, and a similarity
  manufactured by transcription measures nothing. Raised by ce-workshop-9a, accepted.
  The real reason ours reads as a schematic is that **we do not know what most of
  these parts are**, and no palette fixes that.
- **Re-thresholding the crop to get Apple's silhouette.** The dark wooden blocks
  behind the board merge into the blob and inflated Apple's diameter by 3.20 %.
  Apple's outline is L1's own measurement of this photograph; 66 of 720 comparison
  rays fall in a measurement gap and are **dropped, never interpolated**.
- **Modelling a flat across the 115–118.5° inward excursion** (1.02 mm). It sits on
  the edge of a **13.75° hole in the ray data**. 63.0° of arc over 14 gaps carries no
  ray at all; those arcs are listed in the fit file and drawn in the provisional
  colour.
- **Extending the hole facets to their natural tangency** (±25°): residual
  0.3342 → 0.4428 mm, WORSE, H3 turned NOT EARNED.
- **Inward facets as global half-plane clips**: 0.3342 → 0.4267 mm, also WORSE.
- **L1's `centre_px` for the hole.** It disagrees with that file's own `boundary`
  points — stated centre 2.76 mm from the board centre, boundary points imply
  0.622 mm, which matches FCC photo 6's 0.4625 mm. Looks like an (x,y) vs (row,col)
  swap **in the reported field only**; the points are fine. The points were used, the
  stated centre was not, and it is **reported upstream, not edited**.

---

## Defects found in my own controls, kept because the fix is the lesson

1. **R3 fired at 1.42 % on a correct render.** It averaged 2 × mean radius over ALL
   rays including the chorded ones, comparing a chord-shortened mean against a circle
   diameter. It now measures only the 893/1440 rays no chord cuts — **the same
   quantity the parameter defines**.
2. **X3 did not reach X4.** Panel 1 is rendered by a subprocess that knows nothing
   about `--break-rotation`, so X4 sat at 0.413 mm under a 12° rotation. The control
   was a decoration on that number until the break was applied to the profile read
   off the panel.
3. **R5 could not fire.** `--break-drop` truncated the INPUT rows, so the accounting
   identity balanced. It now loses markers at DRAW time with the row count whole.
4. **H3 returned −3836 %, then −221 %.** The first was a broken synthetic generator
   (wrong frame); it was rebuilt with a zero-noise self-check. The second exposed a
   **real defect in the detector**: a line fitted to a short noisy arc comes out
   nearly TANGENTIAL, and `d/cos(θ−n)` diverges at 90°, so applying such a "facet"
   throws the radius to infinity inside its own arc. Facets more than 60° from their
   own normal are now refused with that reason.
5. **The H3 EARNED test was weak.** With a negative floor, "gain > 2 × floor" passed
   on any positive gain. It now also demands a 5 % absolute improvement.

---

## The next lane's first three jobs

1. **The outer outline's worst arcs are 82.8–101.0° (0.901 mm) and 114.0–119.5°
   (0.979 mm).** Both sit next to the largest data gaps. Re-extract the profile there
   on the sharper photograph before adding any more primitives.
2. **The facet side walls are not measured.** Each hole facet ends in a radial step
   at the ±0.30 mm crossing, which is not where the wall is. A perpendicular-edge
   detector would close that.
3. **D004 is a candidate 15th rim-suspect** and nothing has chased it.

**And the standing one:** the board is knowingly incomplete in the dark regions and
the picture says so. **Do not fill those gaps by eye.** An eyeballed position among
measured ones is invisible in a render, which is exactly why it must not happen.
