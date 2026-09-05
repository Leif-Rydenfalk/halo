# R17 — the FCC rule edges are STRAIGHT: no measurable lens distortion, and every earlier sagitta was contamination

*halo Replica, lane L2, 2026-09-05. Final on this thread. Supersedes the numbers in
[R14](R14-THE-LENS-IS-BARREL-DISTORTED.md) and [R15](R15-NOT-SIMPLE-BARREL-R14-CORRECTED.md).*

## The answer

| edge | samples kept | sagitta | null | z | verdict |
|---|---|---|---|---|---|
| photo6-bottom | 1187 / 1600 | **0.194 px** over 1250 px | 0.134 ± 0.099 | −0.7 | **straight — CANNOT DETERMINE any bow** |
| photo7-bottom | 1164 / 1600 | **0.123 px** over 1245 px | 0.018 ± 0.015 | +1.2 | **straight — CANNOT DETERMINE any bow** |
| photo6-right | 461 / 800 | — | — | — | **REFUSED: two-level trace** |
| photo7-right | 520 / 800 | — | — | — | **REFUSED: two-level trace** |

**Both usable edges are straight to within about 0.2 px over 1250 px.** There is no
measurable lens distortion along the bottom rule in either frame.

## Everything I published before this was contamination

R14 reported sagittas of 1.14 and 4.31 px with z = +5.1 and +6.6. R16, after a continuity
gate, reported 2.40 and 2.59 px with z = +5.6 and **+26.5**. **All of it was the tracker
leaving the edge**, and none of it survives.

Two distinct contaminations, and only a picture found either:

1. **The tracker was following the rule's TICK MARKS, not its edge.** It takes the strongest
   gradient in each column, and on a steel rule that alternates between the edge and the
   ticks a few pixels away. The trace is a square wave jumping 10–15 px. A quadratic fitted
   through it returns a confident bow. **Invisible in every scalar the tool printed** —
   sagitta, z, residual sd — and unmistakable the instant the profile was drawn.
2. **The far end of the box is not the rule.** Past x ≈ 1700 both bottom traces dive 4–7 px,
   where the rule's end and its inch scale enter the box. That tail alone produced the
   entire 2.4–2.6 px "bow": restricted to the clean span, the same edges measure 0.19 and
   0.12 px.

**A z of +26.5 was the most confident number this lane has ever produced and it was junk.**
A high z says a systematic term is well determined; it says nothing about whether the thing
being fitted is what you think it is.

## The two gates that now stop it, both watched to fire

- **CONTINUITY.** A real edge is continuous: adjacent samples differ by a fraction of a pixel.
  Samples far from a robust local median are discarded and counted (197–312 per edge).
  Selftest: a trace contaminated by synthetic tick marks is rescued to within 0.25 px of a
  known 2.0 px bow, and the gate stays silent on a clean edge.
- **TWO-LEVEL.** The continuity gate cannot reject a long *run* at a second level, because a
  local median follows it. So: 1-D 2-means on the residuals; two levels more than 3 px apart
  each holding ≥5 % of samples means the trace is switching between two features and the
  measurement is **refused, never averaged**. Both right edges fire it — 7.3 px apart with
  45 % on the minority level, and 8.3 px with 40 %.
  The 5 % threshold was tightened from 0.15 after a selftest put 14 % of a trace 21 px away
  and the gate stayed quiet. **The gate was made to fire more readily; the synthetic was not
  made easier to catch.**

## What this does for R11's three candidates

R11 left the smooth coherent registration misfit with three possible causes. This narrows it:

- **Lens distortion — now bounded, and small.** Along the bottom rule, at radii of roughly
  330–745 px from the frame centre, distortion produces under ~0.2 px of bow across
  1250 px. **Caveat, and it is a real one:** the bottom rule sits at y ≈ 1131 while the board
  sits near (952, 678). The bound is measured where the rule is, not where the board is, and
  no edge in these frames crosses the board's own neighbourhood. A lens this straight over
  that span is unlikely to be badly distorted nearer the centre, but "unlikely" is not a
  measurement and this lane does not publish it as one.
- **A board that is not flat** — untouched, still open.
- **Two different physical boards** (`920-08283-01` 2019 engineering vs `820-01736-A` 2020
  production) — untouched, still open, and still only settleable with a caliper.

Downstream numbers are unchanged: **FRONT 0.181 mm RMS / 0.288 mm p95, BACK 1.026 / 1.703.**

## Instrument

`tools/c_distortion.py` — `doctor` · `selftest` (**17/17**) · `edge` · `solve-k` · `profile`.
Exit code is the verdict. `profile` writes the picture, and the picture is the reason this
file exists.

```
tools/c_distortion.py profile --png metrology/compside/img/R17-edge-profiles-span.png
tools/c_distortion.py edge    --json-out metrology/compside/R17-edges-final.json
tools/c_distortion.py selftest
```

Pictures: `img/R16-edge-profiles.png` (ungated — the square waves that produced R14's
numbers), `img/R16-edge-profiles-gated.png` (continuity gate on; the bottom edges become
clean and the contaminated tail is visible), `img/R17-edge-profiles-span.png` (final).
**Keep all three. They are the evidence that the scalars were lying.**

## The lesson, and it is the fifth of the day in the same family

R00's hold-out interpolated. R08's diagnosis was wrong. R09's refutation was wrong. R14's
positive rested on a necessary-but-not-sufficient test. And R16's z = +26.5 was a perfectly
determined fit to the wrong signal. Every one of them was **a verdict a check could not have
contradicted** — and this last one was invisible to every number and obvious in one picture.

*LOOK at it. The scalars had no way to tell me.*
