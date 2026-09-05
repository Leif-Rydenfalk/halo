# R15 — R14's "the lens is barrel-distorted" does not survive the magnitude check

> **⚠ FULLY SUPERSEDED BY [R17](R17-THE-RULE-EDGES-ARE-STRAIGHT.md).** Its k values (-0.00646, -0.06259) came from contaminated traces: the
> tracker was following the rule's TICK MARKS and, past x ~ 1700, the rule's far end
> rather than its edge. With a continuity gate, a two-level refusal and the clean span,
> both bottom edges measure **0.194 px and 0.123 px, neither clearing its null**, and
> both right edges are **refused as two-level traces**. There is no measurable lens
> distortion. Nothing numeric in this file stands.


*halo Replica, lane L2, 2026-09-05. Corrects [R14](R14-THE-LENS-IS-BARREL-DISTORTED.md).*

R14 measured two genuinely bowed rule edges in FCC internal photo 7, found that **both bow
away from the frame centre**, and called it **BARREL, consistent with a single radial
centre.** The sign test passed. **The magnitude test, which R14 never ran, fails.**

## What each edge implies on its own

Ask each edge what single barrel coefficient would produce the bow it actually shows
(`r' = r(1 + k·rn²)`, `rn = r/(W/2)`, about the frame centre):

| edge | sagitta | implied k |
|---|---|---|
| photo7-bottom | 1.137 px over 1596 px | **−0.00646** |
| photo7-right | 4.310 px over 799 px | **−0.06259** |

**163 % apart — a factor of 9.7.** No single radial term produces both. So what R14 called
barrel distortion is **not** simple radial lens distortion, and the coefficient it implied
cannot be used to undistort anything.

## Why the sign test was not enough, and this is the general lesson

"Both edges bow away from the centre" is **necessary** for radial distortion and nowhere
near **sufficient**. It has only two outcomes and one of them is 50 % likely by chance.
The magnitude is where the information is: the two edges sit at different radii and
different orientations, so a single radial term constrains their sagittas to a specific
*ratio*, and that ratio is the real test. R14 stopped at the cheap half.

**What would have had to happen for the two to disagree** — the question I did not ask
before publishing R14 — is exactly this: a bow from anything other than one radial term
about the frame centre (a bent or damaged rule, a rendering artifact, a contaminated edge
trace) gives the two edges different k. They do.

## The arithmetic is not the problem

A disagreement is only publishable if the inversion is sound, so it is now round-tripped in
the selftest: a synthetic k = −0.030 produces sagittas of **5.58 px** on the bottom geometry
and **1.92 px** on the right — very different numbers — and both invert back to k = −0.030,
**0.0 % apart**. The agreement test *can* pass. On photo 7 it does not.

## Verdict

**CANNOT DETERMINE for lens distortion in the FCC frames.**

- **photo 6** (the FRONT face's scale donor): neither edge clears its own null.
  z = +2.6 and +0.8. Nothing measured.
- **photo 7** (the BACK face's scale donor): both edges are genuinely bowed
  (z = +5.1, +6.6) and bow in the same radial sense, but no single radial coefficient
  fits both. **Something is bowing them; it is not one lens term.**

Most likely candidates for photo 7's right edge, which carries the large 4.31 px bow and the
worst noise (line-fit residual sd 5.86 px, 53 samples discarded at the box boundary): a
contaminated edge trace, or a physically bent rule. Note that **perspective cannot do it** —
a projective camera images a straight line as a straight line however the rule is tilted —
so the cause is either the optics, the rule itself, or my trace.

## Consequence for R11's three candidates

**Unchanged. All three remain open.** R14 briefly appeared to settle "uncorrected lens
distortion" as measured-and-present; it is back to CANNOT DETERMINE. The smooth coherent
registration misfit on both faces (z = +8.5 and +11.1) still has no identified cause, and
the numbers downstream stand where R11 left them: **FRONT 0.181 mm RMS / 0.288 mm p95,
BACK 1.026 / 1.703.**

## The fourth correction today, and they are all one mistake

R00's hold-out interpolated. R08's diagnosis was wrong. R09's refutation was wrong. R14's
positive claim rested on a test that was necessary but not sufficient. Every one was **a
verdict taken from a check that could not have contradicted it**, and every one flattered —
three as falsely reassuring nulls, this one as a falsely confident positive.

The instrument now carries the missing half: `solve-k` reports the coefficient each edge
implies *and* whether the edges agree, and the agreement test is round-tripped against a
known k so a disagreement is a fact about the photograph rather than about my arithmetic.

## Reproduce

```
tools/c_distortion.py edge      --json-out metrology/compside/R14-lens-distortion-from-rule-edges.json
tools/c_distortion.py solve-k   --json-out metrology/compside/R15-barrel-k.json
tools/c_distortion.py selftest    # 12/12
```
