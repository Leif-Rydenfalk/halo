# P01 — what I expect the rim pads to do, WRITTEN BEFORE MEASURING THEM

*halo Replica, L7 DARK-PACKAGE DETECTOR lane, 2026-09-05.*
*Committed before any rim measurement was taken, so the answer cannot be fitted
to it afterwards. Whatever the numbers say, this file is not edited — a
correction is a new section at the bottom.*

**The question (from the orchestrator):** `docs/REFERENCE-TEARDOWN.md` says
**six** tear-off joints hold the antenna carrier to the board rim. Nobody has
counted them. M03 and M05 closed it CANNOT DETERMINE using **intensity and blob**
methods on the FCC photos, and M05's closing statement was explicitly about
**signal-to-noise**, not about the board.

**Why it is worth re-asking with this engine, in one line:** the engine is not an
intensity method, it carries a bar measured from a phase-scrambled copy of the
same photograph, and it will be pointed at a **different and sharper source** —
`oflynn-backside-fullres.jpeg` at 20–27 genuine px/mm, against the FCC photos'
**4.6 genuine px/mm** that M05's verdict was about. That is **~5× more genuine
resolution than the source M05 closed on**, and M03 named exactly this kind of
step ("re-render at 600 dpi") as the highest-value unblocking action.

---

## What I have NOT done yet

I have not looked at the rim of this photograph at native resolution, I have not
measured a pad step, and I have not run the detector anywhere near the edge. The
numbers below come from measurements I already made **for a different question**
(the dark packages) plus the physics.

## P1 — CONTRAST: the pads will be bright, and by a lot

A solder pad is **metal on dark soldermask** — the opposite of the case that
defeated me. On this same photograph I have already measured soldermask at luma
**22–66** and bright solder/pads at **140–180**.

> **Predicted boundary step: 100–200 luma**, against the **1–26 luma** the dark
> packages present. **Falsified if the measured pad step is below 60 luma.**

## P2 — LENGTH: and this is where I expect it to fail anyway

**The bar is not a property of the board. It scales with the length of the edge
being integrated.** My published limit — 100–160 luma — was measured for a
3.226 × 2.956 mm rectangle whose sides integrate over ~3 mm. Coherent gain goes
as √L, so a **1.0–1.6 mm** tear-off tab (M05's own synthetic used those two arc
lengths) needs roughly **√(3.2/1.0) ≈ 1.8×** the step to reach the same |z|.

> **Predicted required step at pad scale: 180–290 luma.** The achievable step on
> this board is capped near **170** (soldermask ~30 to brightest solder ~200).
>
> **So I predict the rim pads will NOT clear a pad-scale bar, and that the reason
> will be edge LENGTH, not contrast** — the opposite failure mode from the dark
> packages, and a different one from M05's signal-to-noise.
>
> **Falsified if the measured pad-scale limit comes out BELOW the measured pad
> step.** In that case the bar is cleared and the count is on.

**I must not reuse the 100–160 number here.** It was measured for a 3 mm object
and quoting it at 1 mm would be exactly the kind of borrowed constant this lane
exists to catch. The pad-scale limit gets its own ladder, at pad size.

## P3 — THE RIM IS THE WORST PLACE ON THE BOARD FOR THIS STATISTIC

A pad at the rim sits within its own search range of two strong competing
straight-ish structures: the **board outline** itself, and the **grey gasket that
laps over the board edge** — which the outline fitter prefers by a factor of 17
(M02 §8, E01).

> **Predicted rim-local null: HIGHER than the board-average N3 of 33.4.**
> **Falsified if the rim-local null p99 comes out below 33.4.**

## P4 — MY OWN BIAS, NAMED IN ADVANCE

I have just closed one question CANNOT DETERMINE, and the cheapest thing I can do
now is close another one the same way. **P2 is therefore the prediction I am most
likely to be wrong about, in the direction of pessimism.** The guard is that the
pad-scale limit ladder gets run **whatever the step measurement says**, and that
a limit below the measured step falsifies P2 outright and puts the count on.

## P5 — I AM NOT PREDICTING A COUNT

I am **not** predicting six, and I am not predicting any other number. If the bar
is cleared the count is whatever the detector returns, reported before I compare
it with the dossier. If the bar is not cleared there is no count at all, only a
number saying how far short the source falls.

## P6 — THE TELL I WILL CHECK EVEN IF EVERYTHING PASSES

L1 found FRONT candidates clustering at **147–199°** and BACK at **210–308°** —
disjoint arcs, which two views of one board cannot honestly produce, and which is
the signature of a detector following per-photograph illumination.

> **If my per-side support is similarly lopsided by angle, that is the same tell
> and it disqualifies the count regardless of how it scores.** I will report the
> angular distribution of support whether or not it looks good.

## Nothing is drawn

L1's withdrawn 15 and 13 candidate angles are on disk marked never-to-be-drawn.
Anything this lane produces is reported the same way until it clears.
