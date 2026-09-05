# R08 — the hold-out number two handoffs quote is an INTERPOLATION error, and the back face's is 5.6× optimistic

*halo Replica, lane L2 (component-side metrology), 2026-09-05. Measured, not argued.*

> **SIDE CONVENTION.** **FRONT = the COMPONENT side**, per Apple's own FCC caption
> "A2187 MLB – Front". O'Flynn's `backside-fullres.jpeg` **is** this project's FRONT.

I published **0.1029 mm** as the registration hold-out for the FRONT face this morning.
`HANDOFF-positions-front.json` quotes it under `uncertainty.registration_holdout_mm`,
`HANDOFF-positions-back.json` quotes L9's **0.1256 mm** the same way, and 146 published
positions rest on the pair. Both were produced by the same 4-fold angular split, and
**that split interpolates.** Told to check hardest the result I was most pleased with, I
did, and it does not hold.

## What was measured

Same images, same transform, same tool — only the hold-out geometry changes.

| pair | split | worst fold RMS | worst fold p95 | file |
|---|---|---|---|---|
| **FRONT** `oflynn-front` ← `fcc6-front` | angular K=4 *(as published)* | 0.1043 mm | 0.1808 mm | `R02` |
| **FRONT** | **angular K=2 — halves** | **0.1298 mm** | **0.2266 mm** | `R04` |
| **FRONT** | radial K=2 | 0.0806 mm | 0.1468 mm | `R05` |
| **BACK** `oflynn-back` ← `fcc7-back` | angular K=4 *(as published by L9)* | 0.1256 mm | — | `metrology/c_register-validate-back.json` |
| **BACK** | **angular K=2 — halves** | **0.7050 mm** | **1.1112 mm** | `R06` — **FAIL** |
| **BACK** | radial K=2 | 0.1257 mm | 0.1673 mm | `R07` |

**FRONT degrades 1.26×. BACK degrades 5.6× and fails the 0.20 mm tolerance outright.**

## Why K=4 flatters

With four 90° folds, three quarters of the board still *surround* every held-out sector,
so the fit never extrapolates — it interpolates into a hole it is enclosing. Holding out a
half removes that enclosure and asks the transform to reach 180° it has never seen. That is
the question a published position actually poses in any region where landmarks are thin.

## And the failure is AZIMUTHAL, not radial — which is the informative part

On the BACK, holding out an **annulus** costs almost nothing (0.1257 mm; each fold still
spans all 360°), while holding out a **half** costs 5.6× (0.7050 mm). The structure the
homography cannot represent therefore varies **with angle around the board**, not with
radius. The FRONT shows the same signature, 5× milder: 0.0806 mm radial against 0.1298 mm
angular.

**What this would have had to look like to mean something else.** A localised cluster of
large residuals over a few features — a moved part — would have shown up in the K=4 split
too, in whichever 90° fold contained it. It did not: the BACK's four K=4 folds are flat
at 0.0931–0.1256 mm, and the K=2 failing half is **broadly** elevated (median 0.572 mm,
deciles 0.137 / 0.390 / 0.572 / 0.884 / 1.077). This is a whole-half misfit, not a
displaced component. The FRONT's residuals are smoothly distributed with no cluster
(median 0.092–0.116 mm, max 0.254 mm).

## What causes the azimuthal structure — CANNOT DETERMINE, and here is why

Three candidates, and these two photographs cannot separate them:

1. **The board is not flat.** A homography maps plane to plane; any dome or bow deviates
   from it in a way that varies around the rim.
2. **Lens distortion in one of the two frames**, uncorrected in either.
3. **The two boards genuinely differ.** `fcc7-back` is `920-08283-01`, data code 3119 — a
   2019 engineering build. `oflynn-back` is `820-01736-A`, data code 2920 17 — 2020
   production. **They are different physical objects.**

What would settle it: a third view of either face with its own ruler, or a caliper on one
board of each part number. Neither is available from this machine.

## THE CAVEAT MY OWN R00 NEVER STATED

**The FRONT pair is two different physical boards too.** `fcc6-front` and `fcc7-back` are
the same FCC sample `920-08283-01`; `oflynn-front` and `oflynn-back` are the same retail
unit `820-01736-A`. The project states this under the BACK handoff, under `bom.json`,
under `M01`, `E01`, `E08` and `STACKUP.md`. **It was not in `R00-DATUM-TRANSFER.md`, which
is the document that publishes the transfer.** Corrected here.

It matters in a specific way that is easy to get backwards:

- A **uniform** size difference between the two builds is **absorbed into the fitted
  scale** and leaves the hold-out residual completely unchanged, because the check divides
  both sides by the same number. **Registration consistency is not scale accuracy.**
- A **non-uniform** layout difference is **not** absorbed, and would raise the residual.
  So the FRONT's smooth 0.13 mm hold-out is genuine evidence that the 2019 engineering
  build and the 2020 production board carry the same component layout to within about
  0.13 mm RMS across 80 landmarks — a positive result, and one nothing else in the project
  had measured.

## A 1.29 % scale error, in the flattering direction, fixed

`c_register`'s `fcc6-front` view defaulted to **15.887546 px/mm** — photo 6's bottom rule
measured **at the rule**. The board does not sit on that rule. `M02`/`scale-at-board-photo6.json`
measures **15.6850 px/mm at the board** (two routes 0.228 % apart). Its sibling view
`fcc7-back` had already been corrected to an at-the-board scale by L9, so **the two entries
of one catalogue defaulted to different kinds of number, and only the FRONT one was wrong.**

Every FRONT millimetre computed against the old default came out **1.29 % smaller than the
truth** — which is why the published 0.1029 mm becomes 0.1043 mm on the same data. Default
corrected; `--target-px-per-mm 15.887546` restores the old behaviour.

## What downstream should use

| | quote for the transform | quote for any ONE position |
|---|---|---|
| **FRONT** | **0.130 mm RMS** | **0.227 mm p95** |
| **BACK** | **0.126 mm RMS where landmarks are dense**; up to **0.705 mm** where they are not | **0.167 mm p95** dense; **1.11 mm** sparse |

`HANDOFF-positions-front.json` currently states 0.1029 mm and understates by 26 %.
`HANDOFF-positions-back.json` states 0.1256 mm, which is its **interpolation** figure only.

**The honest framing, and it is not "the error is 0.705 mm".** The K=4 number is an
interpolation error and the K=2 number is an extrapolation error. A published position
comes from a fit that used *all* landmarks, so its error sits between the two — near the
interpolation figure where landmarks are dense, near the extrapolation figure where they
are thin. What the halves test proves is that **the residual field contains structure a
homography cannot represent.** That structure is present in the full fit as well; being
averaged is not the same as being removed.

**And it remains true, unchanged by any of the above, that neither number says anything at
all about scale accuracy.** A wrong px/mm divides both sides of the check equally and
cancels. The 2.07 % rule-to-rule disagreement in photo 6, and the two-different-boards
question, are both invisible to every figure in this file.

## Reproduce

```
tools/c_register.py validate --folds 2 --split angular          # FRONT halves
tools/c_register.py validate --folds 2 --split radial           # FRONT annuli
tools/c_register.py validate --source oflynn-back --target fcc7-back --folds 2 --split angular
tools/c_register.py validate --source oflynn-back --target fcc7-back --folds 2 --split radial
tools/c_register.py selftest                                     # 5/5, every control watched to fire
```

`--split radial` and the per-landmark residual dump were added by this lane today; the
selftest still passes 5/5, including the case that goes red on a radial warp a homography
cannot absorb.
