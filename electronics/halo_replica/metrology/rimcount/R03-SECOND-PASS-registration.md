# R03 — SECOND PASS, registered before it is run, and labelled weaker than the first

*halo Replica, lane L10. Written **after** `R02`'s CANNOT DETERMINE was committed and pushed
(495469f). **This pass is chosen downstream of the answer and is therefore weaker evidence than
anything in R00–R02.** E07 §17: a verdict chosen after seeing which analysis wins is not a
verdict. It is run and reported anyway because the alternative — knowing the confuser class and
not measuring it — is worse; but the label travels with the number and `R02`'s verdict is not
withdrawn by it.*

## What R02 found and this tests

The three highest-scoring detections, by a wide margin (closure 23.2 / 9.8 / 7.9), are **gold
annular pads**: a bright ring around a **dark** centre. A tear-off solder joint is **filled**:
bright at the centre. **That is a polarity difference, not a shape difference**, and the shape
statistics that failed in `R02` are all blind to it by construction — `noncirc` reads the
half-max radius profile, which an annulus and a disc of the same outer diameter share.

## The statistic, fixed now

For a candidate at (cx, cy) with locator radius r:

    core = median luma over  rho <= 0.35 r
    ring = median luma over  0.70 r <= rho <= 1.05 r
    annularity = (ring - core) / (ring - surround)

with `surround` the background-excluded median over 1.35–1.85 r, exactly as `radial_profile`
computes it. **FILLED** is annularity ≈ 0 (core as bright as the ring); **ANNULAR** is
annularity → 1 (core down at the surround level). Denominator guarded: if `ring - surround` is
not positive and at least 8 luma, the candidate is **UNMEASURED and named**, never scored 0.

## Thresholds — a PROCEDURE again, measured where it is used

Set from **pasted controls in the real rim**: a filled **disc** and an **annulus** of the same
outer diameter and the same 120 luma contrast, ≥20 pastes each at measurably-empty sites in two
swept site selections. **FILLED** if annularity ≤ disc p90; **ANNULAR** if ≥ annulus p10;
between = **UNDECIDED**, named, never counted as a joint.

**FALSIFICATION:** if disc p90 ≥ annulus p10, or the median ratio is under **2.0×**, the polarity
test is declared **non-separating on this source** and `R02`'s CANNOT DETERMINE stands unchanged
with nothing added.

## Deliberate breaks, to be watched red before the numbers are believed

1. A pasted **annulus** must be classified ANNULAR and a pasted **disc** FILLED — and with the
   statistic inverted, both must flip. A test whose inversion changes nothing is not a test.
2. A **flat** paste (zero contrast) must return **UNMEASURED**, not a polarity.
3. The three gold rings of `R02` must come back **ANNULAR**. If they do not, the statistic does
   not describe the thing it was written from, and it is discarded.
   **Break 3 is the one that can embarrass this pass, and it is the reason it is listed.**

## What a pass would and would not license

A pass licenses **one** sentence: *of the detections above the bar, N are FILLED.* It does **not**
license calling them joints — the SMD capacitor pads and the grey gasket patches in `R02`'s tile
sheet are also filled, and no statistic here separates those. **The count of tear-off joints
remains CANNOT DETERMINE regardless of this pass's outcome.**
