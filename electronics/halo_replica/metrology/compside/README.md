# `metrology/compside/` — lane L2, component-side metrology

**Read this before quoting any number from this directory. Several of these documents are
WITHDRAWN, and they are kept rather than deleted.**

> **SIDE CONVENTION, on every file here. FRONT = the COMPONENT side**, following Apple's own
> FCC caption "A2187 MLB – Front". Colin O'Flynn calls that same face *"backside"*, so
> `oflynn-backside-fullres.jpeg` **is this project's FRONT**.

## The numbers that are current

| quantity | value | file |
|---|---|---|
| **FRONT registration hold-out** — quote for the transform | **0.181 mm RMS** | R11 |
| **FRONT** — quote for any ONE component position | **0.288 mm p95** | R11 |
| **BACK registration hold-out** — transform | **1.026 mm RMS** | R11 |
| **BACK** — any ONE position | **1.703 mm p95** | R11 |
| lens distortion in the FCC frames | **none measurable**; bow < ~0.2 px over 1250 px | R17 |
| a dome about the board centre | **CANNOT DETERMINE** — the test is blind there | R18 |

**Two handoff files still carry superseded figures** and are outside this lane's write scope:
`metrology/HANDOFF-positions-front.json` states **0.1029 mm** (measured: 0.181) and
`metrology/HANDOFF-positions-back.json` states **0.1256 mm** (measured: 1.026).

## What each document is, and whether it stands

| file | what | status |
|---|---|---|
| **R00** | the datum transfers from FCC photo 6's rulers onto O'Flynn's sharp photograph | **STANDS**, with two correction banners (scale basis; the hold-out figure) |
| R08 | the 4-fold hold-out interpolates; halves are much worse | superseded in part by R09/R11 — its *measurements* stand, its *diagnosis* does not |
| R09 | claimed the back's misfit was coverage and ruled out a smooth cause | **REFUTED by R11.** Both claims wrong |
| **R11** | both faces carry a smooth coherent misfit; a null needs a DETECTION LIMIT; final hold-out numbers | **STANDS — the current source for all hold-out figures** |
| R14 | claimed the lens is barrel-distorted | **FULLY WITHDRAWN** (R15, then R17) |
| R15 | withdrew R14's single-k claim on a magnitude check | superseded by R17; its *reasoning* stands, its k values do not |
| **R17** | the rule edges are STRAIGHT; every earlier sagitta was contamination | **STANDS — final on lens distortion** |
| **R18** | the dome test cannot see a dome about the board centre, and reports that | **STANDS** |

## The instruments

Both are exit-code-as-verdict: `0` PASS · `1` FAIL · `2` CANNOT DETERMINE.

- **`tools/c_register.py`** — `doctor` · `selftest` (**12/12**) · `fit` · `validate`.
  Registers two views of one board and carries a metric datum across. Controls: a null
  distribution from deliberately wrong rotations, a landmark ambiguity gate that discards
  and counts, a spatial hold-out (`--split angular|radial`, `--split-offset`), residual
  coherence with a permutation null **and a detection limit**, and a radial decomposition
  **with its own dome detection limit**.
- **`tools/c_distortion.py`** — `doctor` · `selftest` (**17/17**) · `edge` · `solve-k` ·
  `profile`. Measures distortion from something straight by construction. Controls: a
  permutation null, a continuity gate, a two-level refusal, radial sign consistency, and a
  k-inversion round-trip.

## The pictures, and why they are kept

`img/R16-edge-profiles.png` (ungated), `img/R16-edge-profiles-gated.png` (continuity gate
on), `img/R17-edge-profiles-span.png` (final). **These are the evidence that the scalars
were lying.** A sagitta of 2.59 px at **z = +26.5** was a perfectly determined fit to a
square wave, invisible in every statistic the tool printed and obvious the instant the
residual profile was drawn. Anyone about to trust a number from `c_distortion` should look
at these first.

## What is still open

1. **Whether the board is flat.** Untested — R18's statistic is blind about the board centre
   because the landmarks occupy a narrow annulus (0.42 R–0.95 R) and give it no lever arm.
   Settling it needs landmarks over a wider range of radii, or an edge-on profile photograph,
   which the catalogue does not contain.
2. **Whether the two boards are the same size.** `fcc6-front`/`fcc7-back` are the FCC sample
   `920-08283-01` (data code 3119, a 2019 engineering build); `oflynn-front`/`oflynn-back`
   are the retail `820-01736-A` (2920 17, 2020 production). **A uniform difference is
   absorbed into the fitted scale and is invisible to every hold-out in this directory** —
   registration consistency is not scale accuracy. Only a caliper on one board of each part
   number settles it.
3. **The 2.07 % rule-to-rule disagreement inside photo 6** (bottom 15.8875 px/mm, right
   15.5651). `m_scale_at` interpolates to the board at 15.6850, which is what these tools now
   default to, but the disagreement itself is unresolved.
4. **Neither handoff file has been corrected.** They belong to other lanes.

## The one lesson worth carrying out of this directory

Five findings were published here and withdrawn in a single day. Every one was **a verdict
that the check could not have contradicted**:

- a hold-out that interpolated instead of extrapolating;
- a coherence null from a landmark set that could not see the field;
- a diagnosis read from an observation that never discriminated;
- a positive from a test that was necessary but nowhere near sufficient;
- and a fit with a z of +26.5 to entirely the wrong signal.

Hence the two rules the instruments now enforce: **a null result must carry the amplitude it
was blind to**, and **the residual PROFILE must be looked at, not just the residual
STATISTIC.**
