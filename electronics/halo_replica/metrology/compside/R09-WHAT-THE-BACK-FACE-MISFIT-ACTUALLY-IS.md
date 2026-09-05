# R09 — the back face's misfit is landmark COVERAGE, not a warped board and not a different layout

*halo Replica, lane L2, 2026-09-05. Follows [R08](R08-THE-HOLDOUT-WAS-OPTIMISTIC.md),
which measured the failure; this one names it and rules two causes out.*

> **SIDE CONVENTION. FRONT = the COMPONENT side** (Apple's FCC caption "MLB – Front").
> O'Flynn's `backside-fullres.jpeg` is this project's FRONT.

R08 left the cause of the BACK pair's 5.6× hold-out failure as CANNOT DETERMINE with three
candidates: a non-flat board, uncorrected lens distortion, or two genuinely different
physical boards. **Two of the three are now ruled out, and the remaining explanation is
mundane: the back face's landmarks are fewer, noisier, and unevenly spread.**

## Test 1 — is the residual field SMOOTH? Measured, without adding a parameter

Fit the homography on all landmarks, take each one's residual **vector**, and measure how
well it agrees with the mean residual of its 4 nearest neighbours. A smooth cause — a bowed
board, lens distortion — moves neighbours **together**. Parts sitting differently on two
different boards move **independently**. Control: recompute with the residuals **permuted
among the positions**, 400 times, which destroys every spatial relationship and keeps the
magnitudes exactly as they are.

| pair | I | null | z | reading |
|---|---|---|---|---|
| **FRONT** | +0.1460 | −0.0100 ± 0.0488 | **+3.2** | spatially coherent — a smooth field, but a small one |
| **BACK** | +0.0735 | −0.0165 ± 0.0656 | **+1.4** | **not distinguishable from no spatial structure at all** |

**The face with the far larger misfit has the LESS structured one.** A smooth warp or a
coherent layout shift would have raised the back's z, not the front's. It did not.

The statistic is trustworthy because it was watched to move both ways on synthetic data
before it was pointed at a board: **z = +15.8** for an injected smooth radial warp,
**z = −1.8** for independent per-landmark scatter. Both are selftest cases.

## Test 2 — does the failure follow a FIXED REGION of the board? No: it follows the SPLIT

Rotating the fold boundary by 90° moves which half is held out. If a real region of the
board were wrong, the failure would stay with that region.

| pair | offset | fold A (n held) | fold B (n held) | worst |
|---|---|---|---|---|
| **BACK** | 0° | 0–180 (33) **0.1766** | 180–360 (25) **0.7050** | 0.7050 mm |
| **BACK** | 90° | 90–270 (22) **1.0366** | 270–450 (36) **0.1940** | **1.0366 mm** |
| **FRONT** | 0° | 0–180 (33) 0.1298 | 180–360 (47) 0.1189 | 0.1298 mm |
| **FRONT** | 90° | 90–270 (36) **0.1708** | 270–450 (44) 0.1423 | **0.1708 mm** |

At 0° the back's ten worst landmarks all sat at **θ 281–302°**. At 90° that same arc falls
inside the fold that scores **0.1940 mm** — the *good* one. **The bad arc did not stay bad;
the bad FOLD moved with the boundary.** There is no fixed defective region.

What the bad folds share is not a place but a **count**: both times the failing fold is the
one holding out **fewer** landmarks (25, then 22), i.e. the fit is being asked to predict
**into the sparsely covered part of the board**. The back's coverage is 58 landmarks
against the front's 80, and it is unevenly spread.

## Test 3 — how much does noise alone buy?

| | in-sample landmark residual | landmarks |
|---|---|---|
| FRONT | 1.047 target px = **0.0659 mm** | 80 |
| BACK | 1.429 target px = **0.0948 mm** | 58 |

The back is **1.44× noisier with 1.38× fewer landmarks** — worth roughly **1.7×** in
extrapolation variance. The observed front-to-back ratio under halves is **5.4×**. So noise
and count account for about a third of it and the rest is **conditioning**: predicting into
a sparse arc puts the held-out points at high leverage, far outside the fitted data.

## What is ruled out, what is not

**RULED OUT for the BACK face**, on the evidence above:
- a smooth geometric cause — a bowed board or lens distortion (Test 1: no detectable
  coherence, on a statistic shown to reach z = +15.8 when one is present);
- a localised layout difference between `920-08283-01` (2019 engineering) and
  `820-01736-A` (2020 production) — Test 2: the bad arc moves with the split, and Test 1
  finds no coherent displacement field.

**NOT ruled out, and it never can be from these photographs:** a **uniform** dimensional
difference between the two builds. It is absorbed into the fitted scale and leaves every
number in R08 and R09 completely unchanged. **Registration consistency is not scale
accuracy.** A caliper on one board of each part number settles it; nothing on this machine does.

**Still true of the FRONT:** its misfit *is* spatially coherent (z = +3.2). It is small —
0.17 mm worst-case — and it is consistent with mild non-planarity or lens distortion. The
same causes are therefore *not* ruled out on the front; they are merely too small to matter
at this tolerance.

## A discriminator I built, tested, and THREW AWAY

Before Test 1 I wrote a second-order polynomial fitter to separate smooth from
component-wise causes: a low-order model should absorb a smooth warp and cannot absorb
per-part scatter. **It failed its own positive control and was discarded.** Given a 5 %
radial warp injected on purpose, poly2's held-out error came out *worse* than the
homography's under both splits — 3.759 px vs 3.393 px extrapolating, 1.834 px vs 1.473 px
interpolating. With ~60 noisy landmarks the four extra parameters cost more than the warp
they were meant to capture.

Shipping it would have been worse than useless: "poly2 did not help" on the real data would
have read as evidence about the **board** when it is only evidence about the **method**.
The function stays in `c_register.py` with that measurement in its docstring so the route is
not retried.

## Revised numbers for downstream

| | quote for the transform | quote for any ONE position |
|---|---|---|
| **FRONT** | **0.171 mm RMS** (worst over both split orientations) | **0.255 mm p95** |
| **BACK**, dense coverage | **0.126 mm RMS** | **0.167 mm p95** |
| **BACK**, sparse coverage | **up to 1.04 mm RMS** | **up to 1.62 mm p95** |

Quoting one split orientation understates: the front's halves figure moves from 0.1298 to
0.1708 mm simply by rotating the fold boundary 90°. **Take the worst over orientations.**

The back's spread is not a defect in the transform — it is a map of where the photograph
supports a measurement and where it does not. **A back-face position in a sparsely
landmarked arc is the least trustworthy number this project publishes**, and it is the one
place a third ruler-bearing photograph of that face would pay for itself immediately.

## Reproduce

```
tools/c_register.py validate --folds 2 --split angular --split-offset 0
tools/c_register.py validate --folds 2 --split angular --split-offset 90
tools/c_register.py validate --source oflynn-back --target fcc7-back --folds 2 --split-offset 0
tools/c_register.py validate --source oflynn-back --target fcc7-back --folds 2 --split-offset 90
tools/c_register.py selftest          # 7/7, coherence controls fire in both directions
```
