# R11 — R09 was wrong on two of its three conclusions, and both errors were the same error

*halo Replica, lane L2, 2026-09-05. Corrects [R09](R09-WHAT-THE-BACK-FACE-MISFIT-ACTUALLY-IS.md).*

> **SIDE CONVENTION. FRONT = the COMPONENT side** (Apple's FCC caption "MLB – Front").
> O'Flynn's `backside-fullres.jpeg` is this project's FRONT.

R09 concluded that the BACK face's registration misfit was **landmark coverage and noise**,
and that a **smooth geometric cause was RULED OUT**. Both claims are refuted. The third —
that no *localised* defect exists — survives.

## The measurement that overturned it

Nothing changed but the density of the landmark grid.

| pair | landmarks | coherence z | detection limit | reading |
|---|---|---|---|---|
| BACK, step 14 | **58** | **+1.4** | **0.84 px** (70 % of residual RMS) | R09 read this as "no structure" |
| BACK, step 8 | **192** | **+8.5** | **0.11 px** (8 %) | **spatially coherent** |
| FRONT, step 8 | **274** | **+11.1** | **0.11 px** (8 %) | spatially coherent |

**The 58-landmark set could not see a smooth field smaller than 0.84 px. The field is real
and it is smaller than that.** A low score there was never evidence of absence — it was
absence of power, and nothing in the output said so. That is the whole error.

## Error 1 — "a smooth geometric cause is RULED OUT". REFUTED.

Both faces carry a smooth, spatially coherent deviation from a homography, at z = +8.5 and
z = +11.1 against permutation nulls, measured on landmark sets that can resolve a coherent
component down to 0.11 px. The candidates R09 dismissed for the back — a board that is not
flat, uncorrected lens distortion — are back on the table for **both** faces, and which one
it is remains CANNOT DETERMINE.

## Error 2 — "the misfit is landmark COVERAGE". REFUTED.

More landmarks do not reduce the error. Worst held-out fold on the BACK:

| landmarks | offset 0° | offset 90° |
|---|---|---|
| 58 | 0.7050 mm | 1.0366 mm |
| 192 | 0.7667 mm | **1.0258 mm** |

**Tripling the coverage changed the hold-out error by under 10 %, in both directions.**
Coverage governs what structure you can *detect*; it does not govern the error itself.

## What survives — "no LOCALISED defect". STILL TRUE, but the reasoning was wrong.

R09 observed that rotating the fold boundary 90° moves the failing fold instead of leaving
it on a fixed arc, and concluded "no fixed defective region". The observation holds and so
does that narrow conclusion: **a single displaced component would stay put, and it does not.**

But R09 then went further and read the moving failure as evidence *for* coverage. It is not.
**A smooth global warp produces exactly the same signature** — whichever half you hold out
is the half the extrapolation gets wrong. The observation never discriminated between the
two, and it was used as though it did.

## The first fix was wrong too, and that is the instructive part

The obvious repair was a power probe: inject a smooth warp into the real residuals and
report POWERED / UNDERPOWERED. Sized to the **full residual RMS**, it scored the
58-landmark back set at injected z = +5.1 and pronounced it **POWERED** — *it passed the
very set that had just got the answer wrong.* The real coherent component is a fraction of
the residual RMS, most of which is landmark localisation noise, so a probe at full RMS tests
for a warp far larger than the one in question. **A yes/no at one over-large effect size is
not power.**

What ships instead sweeps the injected amplitude **down** and reports the smallest smooth
warp the set can still separate from its null. A null result then says something a reader
can use — *no coherent component larger than 0.84 px* — instead of *none*.

## Revised numbers, and this is the third upward revision today

Worst held-out fold over **both** split orientations, at the denser grid, which samples the
board more representatively:

| | quote for the transform | quote for any ONE position |
|---|---|---|
| **FRONT** | **0.181 mm RMS** | **0.288 mm p95** |
| **BACK** | **1.026 mm RMS** | **1.703 mm p95** |

Against the figures the handoffs still carry — 0.1029 mm front, 0.1256 mm back — that is
**1.8× and 8.2×**.

**What these still say nothing about.** Scale accuracy. A wrong px/mm divides both sides of
every hold-out equally and cancels, so the 2.07 % rule-to-rule disagreement in photo 6 and
the question of whether the FCC sample `920-08283-01` and the retail `820-01736-A` differ
uniformly in size are invisible to every number in R08, R09 and R11 alike.

## The pattern in all three of today's corrections

R00's hold-out was optimistic. R08's diagnosis was wrong. R09's refutation was wrong. Every
one was a **confident negative taken from an underpowered test**, and every one flattered.
The instrument now refuses to produce that shape of answer: a null coherence result cannot
be printed without the amplitude it was blind to.

## Reproduce

```
tools/c_register.py validate --source oflynn-back --target fcc7-back --folds 2                       # 58 landmarks
tools/c_register.py validate --source oflynn-back --target fcc7-back --folds 2 --split-offset 90 --step 8 --search 6
tools/c_register.py validate --folds 2 --split-offset 90 --step 8 --search 6                          # FRONT
tools/c_register.py selftest    # 9/9
```

**Provenance note.** The detection-limit code landed in commit `2e173ff`, which is another
lane's — several sessions run `git add -A` at this repo's root and swept these edits in
mid-edit. Nothing was lost; the explanation simply lives here rather than in that commit's
message.
