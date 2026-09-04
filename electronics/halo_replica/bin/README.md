# `boardmetro` — measure a board off a photograph, or refuse

Built by the halo Replica lane because no instrument for this existed in the workshop.
Leif, 2026-09-05: *"always manage its own tools and create any tools that might be missing."*

**Exit code is the verdict: `0` PASS · `1` FAIL · `2` CANNOT DETERMINE.**
CANNOT DETERMINE is never a default and never a soft pass.

```bash
bin/boardmetro doctor       # deps, catalogue, and a CANARY measurement with a known answer
bin/boardmetro selftest     # 13 cases: synthetic ground truth + deliberate breaks
bin/boardmetro circle IMG --mm 26 --json-out out.json
bin/boardmetro scale-ruler IMG --region X0 Y0 X1 Y1 --pitch-mm 1
bin/boardmetro radial IMG --copper --px-per-mm 30.2762
```

## Why the controls exist — two defects this tool caught, one of them its own

**1 · The frame is not the board.** Measuring this project's first board edge produced
**394 px**, which was the *crop boundary*: O'Flynn's marker circle is inscribed tangent to
the square frame, so any search for "the outermost dark thing" finds the frame every time.
It was caught only because the number landed exactly on a search cap and a human noticed.
`circle` now refuses a fit tangent to ≥3 frame edges by default and names the reason; pass
`--expect-frame` when the crop marker is what you actually mean to measure.

**2 · A check that could agree with what it checked.** The first `circle` verb judged shape
by the residual of the fitted inliers. The selftest fed it a **square** and it passed at
**residual sd 1.15 px**, under the 2.0 px threshold — because IRLS *chooses* the inliers
that make the residual small. Shape is now judged on evidence the fit cannot manufacture:
**inlier fraction**, which separates cleanly (square **0.055**, ring **1.000**).

**3 · And the fix was itself wrong once.** The replacement also gated on *angular
uniformity*, which promptly rejected the real O'Flynn circle — legitimately clipped by the
crop, so it occupies 7 of 36 bins. **Angular completeness is not circularity.** Uniformity
is now a printed diagnostic, opt-in via `--min-uniformity` only where a complete ring is
genuinely expected. Selftest case 9 is a clipped circle that must still be accepted.

## What every verb guarantees

- **Prints the INPUT** — filename, region, method, basis — because three antenna results in
  this project were correct computations on the *wrong board*, and the input line is the
  only thing that catches that.
- **Carries a negative control**: `circle` has the frame test; `scale-ruler` requires the
  autocorrelation peak to beat a shuffled version of the same signal.
- **Says what a number does and does not inherit.** `circle --mm` warns that absolute
  millimetres inherit any error in the assumed diameter and that ratios do not.
  `scale-ruler` states that perspective error is *not* bounded by it.

## Selftest — run it before trusting output

13 cases, every control fired on purpose at least once: three drawn circles recovered to
<0.01 px; the frame control fires on an inscribed circle and stays quiet on an inner one;
three ruler pitches recovered; noise yields no periodicity; a blank image yields no
candidates; a square is rejected by inlier fraction; a genuine ring is accepted; a clipped
circle is accepted. **An assertion never seen to go red is not known to work.**
