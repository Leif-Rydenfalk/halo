> **⚠ HOLD-OUT SUPERSEDED (L2, 2026-09-05, later the same day) — see
> [R08](R08-THE-HOLDOUT-WAS-OPTIMISTIC.md).** The "0.103 mm, worst of four folds" headline
> below is an **INTERPOLATION** error: with four 90° folds, three quarters of the board
> still surround every held-out sector, so the fit never extrapolates. Holding out a
> **half** gives **0.1298 mm RMS / 0.2266 mm p95** on this FRONT pair. Quote **0.130 mm**
> for the transform and **0.227 mm** for any single position. (The same test applied to the
> BACK pair, added later by L9, degrades 5.6× and FAILS: 0.705 mm. R08 has it.)

> **⚠ THE CAVEAT THIS FILE ORIGINALLY OMITTED (L2, 2026-09-05).** *The two photographs are
> of TWO DIFFERENT PHYSICAL BOARDS.* `fcc6-front` is the FCC sample **920-08283-01**, data
> code 3119, a 2019 engineering build; `oflynn-front` is the retail unit **820-01736-A**,
> data code 2920 17, 2020 production. A **uniform** size difference between them is absorbed
> into the fitted scale and leaves every number below completely unchanged — **registration
> consistency is not scale accuracy.** A **non-uniform** layout difference is not absorbed,
> so the smooth 0.13 mm hold-out is genuine evidence the two builds share a component layout
> to about that tolerance. The project states this caveat in M01, E01, E08, STACKUP.md,
> bom.json and both handoffs; it was missing from the file that publishes the transfer.

> **⚠ SCALE CORRECTION (L1/M08, 2026-09-05):** any millimetre in this file derived from
> **15.8875 px/mm** (FCC photo 6 bottom rule) is **1.29 % small**. That is the rule's value
> **at the rule**, near the frame edge; **at the board** M02 measures **15.6850 px/mm**, by two
> routes agreeing to 0.23 %. Transferred source scale **107.686 → 106.313 px/mm**. The 15.8875
> figure is CORRECT as a measurement *of the rule* — what was wrong was using it *at the board*.

# R00 — Can the metric datum be transferred onto O'Flynn's component side?

**Answer: YES. Held-out error, worst of four folds, 0.103 mm RMS (0.049–0.103 mm).**
Lane L2, component-side metrology. Measured 2026-09-05.

> **SIDE CONVENTION, stated because the two sources disagree on the word.**
> **FRONT = THE COMPONENT SIDE**, following Apple's own FCC filing, which captions
> internal photo 6 **"MLB – Front"**. Colin O'Flynn calls that same face *"backside"*,
> so O'Flynn's file `oflynn-backside-fullres.jpeg` **is this project's FRONT**.
> Every file this lane writes carries this line.

## The blocker, and what dissolved it

O'Flynn's component-side photograph is the only one in which the package markings are
legible — `N52832 CIAAE0 2102JK`, `T320 RBEV`, `A048L` — and it carries **no scale
reference of any kind**. Nothing could be measured from it. FCC internal photo 6 shows
the **same face between two steel rulers**, and lane L1 has already calibrated that frame
(`metrology/ruler-calibration.json`, photo6_bottom, 15.8875 px/mm, 93 ticks over 97 mm).

So the datum is not measured on O'Flynn's photograph — it is **carried there** by
registering the two views of the same rigid planar board.

## What was measured

| quantity | value | input |
|---|---|---|
| alignment score (gradient-magnitude NCC, homography) | **0.6861** | O'Flynn front → FCC photo 6, board disc r ≤ 0.985 R |
| same score at 11 deliberately wrong rotations (**null**) | max **0.2027**, mean 0.1622 | identical mask, identical metric |
| fit over worst-case null | **3.38×** | floor set at 2.50× |
| usable landmarks | **80** kept of 448 nodes | 15 px patches, ±5 px search |
| landmarks discarded | **368** — `no_texture` 179, `ambiguous` 124, `on_boundary` 46, `low_peak` 19 | see "what was discarded" |
| in-sample landmark residual | 1.047 target px = 0.066 mm | *not* a validation |
| **held-out residual, worst of 4 angular folds** | **1.635 target px = 0.1029 mm RMS** | sector 270–360° |
| held-out residual, best fold | 0.777 target px = 0.0489 mm RMS | sector 90–180° |
| **transferred scale on O'Flynn's component side** | **107.686 px/mm**, spread 106.784–108.545 (sd 0.41 %) | `metrology/compside/R01-datum-transfer-fit.json` |

Tool: `tools/c_register.py` (`fit`, `validate`, `doctor`, `selftest`).
Raw output: `R01-datum-transfer-fit.json`, `R02-holdout-validation.json`,
`R03-wrongface-control.json`.

## The hold-out is a genuine hold-out

The transform is fitted on landmarks in three angular sectors and its error is measured on
landmarks in the **fourth sector, which it never saw**. Four folds, each sector held out
once. **What each fold would have had to see to disagree:** if the registration were only
locally right — matching where it was fitted and drifting elsewhere — the held-out sector's
residual would blow up while the in-sample one stayed small. That is the disagreement this
test can see, and it did not happen: held-out (0.049–0.103 mm) sits just *above* in-sample
(0.066 mm), which is the correct ordering and the reason the numbers are believable.

## A wrong number that got as far as being printed

The first version of `validate` returned **0.0151 mm** — *better* than the in-sample
residual of 0.066 mm, which is impossible. The cause: it put the measured local shift on
the **target** side and evaluated the transform at the **unshifted** grid node, so the
points being fitted were generated by the very homography under test. A homography fits
points generated by a homography exactly. **It was a check that could agree with what it
checked**, and the only thing that caught it was that the answer was too good. Fixed at
`tools/c_register.py`, `run_validate`, with the defect written into the code beside it.

## Negative controls, all watched to fire

- **WRONG FACE.** Registering O'Flynn's *opposite* face (`oflynn-frontside-fullres.jpeg`,
  the test-point side) against the same FCC photo 6 returns **CANNOT DETERMINE**:
  NCC 0.1451, only **1.42×** its own null, 17 usable landmarks against a floor of 40.
  Same board, same photographer, same lighting — the only difference is that it is not the
  same face, and the tool refuses. `R03-wrongface-control.json`.
- **NULL DISTRIBUTION.** The same score at 11 wrong rotations never exceeds 0.2027.
- **`selftest`, 5/5.** A known transform recovered (θ=37°, s=0.42 → NCC 0.9975, centre
  error 1.23 px); a noise target yields NCC 0.0336; a featureless target has all 160
  landmarks discarded; and the hold-out **goes red** on a radial warp.
  That last case failed first time round on a uniform 3 % scale error — correctly, because
  a uniform scale **is** a homography and the fit absorbs it exactly. **The test was wrong,
  not the hold-out**, and it was replaced with a distortion a homography cannot represent
  (max point move 4.87 px: clean 0.048 px → broken 0.882 px), not loosened.
- **`doctor` canary** is a real registration against a known answer, not a ping.

## What was discarded, and why

368 of 448 grid nodes produced no landmark. This is not a failure; it is the gate working.

- **179 `no_texture`** — the centre hole and the bare soldermask carry nothing to lock onto.
- **124 `ambiguous`** — a second correlation peak rivalled the best one. This is the rim
  pad arrays: a regular row of identical pads correlates equally well one pad over.
  Averaging those in would have quietly biased the fit; they are counted instead.
- **46 `on_boundary`** — the peak sat on the edge of the ±5 px search window, so the shift
  is a *lower bound*, not a measurement of it.
- **19 `low_peak`** — the best local correlation was below 0.45.

## What this number does and does not inherit

**Inherits.** Every error in FCC photo 6's own scale, **including the 2.07 % disagreement
between that frame's bottom rule (15.8875 px/mm) and its right rule (15.5651 px/mm)**.
This lane does not resolve that and does not hide it: a millimetre from O'Flynn's
photograph is uncertain by *at least* that 2.07 %, on top of the 0.103 mm transfer error.
**Ratios to the board diameter do not inherit it** — which is why this lane prints a ratio
beside every millimetre.

**Does not inherit.** The board-diameter dispute. Nothing here assumes 26 mm or 24.6 mm.

**Not a measurement, and must not be used as one:** the board-circle *seeds*
(O'Flynn centre 1405,1700 r 1287.5) were read off a grid overlay to start the search.
They are inputs to a search, not outputs of one. **A board diameter must not be computed
from them**, and none is published here.

## The transferred scale has a spread, and that is the point

107.686 px/mm is a **mean over the board area, with a 0.41 % spread (106.784–108.545)**.
A homography has no single scale: the board is tilted in O'Flynn's frame, so the scale is
genuinely different at different points on it. The spread is the honest statement of that.
Component positions in this lane are therefore computed **through the transform**, never by
dividing a pixel distance by one number.

## What is now unblocked

Component positions and package sizes may now be measured on the *sharp* photograph and
reported in millimetres, each carrying: the photograph, the region, the scale basis
(this transfer), and an uncertainty of **0.103 mm (transfer) ⊕ 2.07 % (ruler dispute)**.
That work had not started when this lane stood down on quota.
