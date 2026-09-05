# E07 — the four ways a check passed today without being able to fail

*halo Replica lane, 2026-09-05. A running catalogue, because this lane produced four distinct
instances in one session and they do not look alike from the outside. Three were found by
lanes beneath me; one was mine, and I had already written the rule against it.*

Every entry is a real, dated defect in this project's own work, with the fix that caught it.

---

## 1 · A check that agrees with what it checks — the fitted-residual test

`bin/boardmetro circle` judged whether a feature was circular by the **residual of the fitted
inliers**. Its selftest fed it a **SQUARE**, which passed at **residual sd 1.15 px** under a
2.0 px threshold — because IRLS *chooses* the inliers that make the residual small.

**Fix:** judge shape on evidence the fit cannot manufacture. **Inlier fraction** separates
cleanly: square **0.055**, ring **1.000**.

**Also:** the first fix was itself wrong. It gated on angular uniformity and rejected the real
O'Flynn marker circle, which is *legitimately* clipped by the crop. **Angular completeness is
not circularity.** Selftest case 9 is now a clipped circle that must still be accepted.

## 2 · A negative control that cannot lose — L1's rim-pad permutation controls

Two in one hour, both in `m_rim_*`:
- The control permuted the **smoothed** signal, giving a jagged control where the real signal
  is smooth. The peak-finder invented ~22 peaks from it and **nothing could ever have beaten
  it.** Fix: permute raw, then smooth identically.
- The control permuted angular **columns**. For a "reaches the edge" criterion every permuted
  column is a full-height stripe, so **the control manufactured the property under test** and
  returned 46.8 against a real 26. Fix: roll each radius row independently — same pixels, same
  per-row runs, only the radial alignment destroyed.

The verdict did not change. **The reasoning behind it was worthless.** A right answer reached
through a control that cannot fail is not a measurement.

## 3 · Methods that cannot disagree — my own, E04, and I had written the rule against it

I concluded from "four independent methods" that the board was ~25 mm and not 26. Every method
applied a **scalar px/mm to an anisotropic projection**, so none could disagree about the thing
I used their agreement to establish. L5's 24.997 mm matched L1's *vertical* extent to **0.02 %**
and sat 5.08 % off horizontal. One systematic reproduced four times. **Retracted in E05.**

I had written the rule after the coil retraction four hours earlier, applied it in E04 **in
writing**, and still got it wrong: I checked whether the scale *sources* were independent and
never asked whether the *projection assumption* was shared.

## 4 · A positive control that is too easy — L1's synthetic rim, and the subtlest of the four

The blob detector **failed** its positive control outright: six synthetic pads at photo 6's
exact scale, **one found**. That withdrew M03's counts. But the replacement's positive control
was still not representative — **the synthetic was 19× cleaner than the photograph**
(differential robust sd 1.8 luma against 34.6 and 37.3). A pad at the synthetic's full 111-luma
contrast sits at **3.2 σ** in photo 6, under a 4 σ gate, and *no larger than the 4.0 σ the real
rim already throws from nothing.*

**Fix:** a noise-matched case where the same detector finds **zero** of six pads that are
certainly there.

**Why this one is the subtlest, in L1's words: passing feels like evidence.** A negative control
that cannot lose leaves you uneasy. A positive control that sails through leaves you confident.

**It also upgraded the verdict**: from *"we could not see them"* to *"at this signal-to-noise
they could not have been seen"* — which CLOSES the rim question instead of leaving it hanging.

---

## 5 · The near-miss family: a bad input dressed as a better one

Not a check, but it would have defeated all of the above. Re-rendering the FCC exhibit at
600 dpi would have resampled a 27 px rim band to 110 px, producing **more** candidates with
**higher** confidence from **no new evidence** — and nothing in that output would have looked
wrong. Caught by measuring the prior first (`E06`): no competitor FCC exhibit embeds above
2048 × 1536, ours is already 2134 × 1600. L1 then closed it independently by power-spectrum
rolloff — the board region's real detail **dies below half Nyquist**, so destroying everything
above half Nyquist costs nothing.

## 6 · And the inverse: a tool that refused when it had actually measured

L1's resolution probe demanded `as_held > /2 > /4` and, when /2 came out *equal*, reported
"cannot separate the controls". **Wrong.** If real detail already dies below half Nyquist then
destroying everything above it MUST cost nothing — **/2 failing to separate IS the answer.** A
monotonic-ordering assumption had been smuggled into the verdict logic rather than the physics.

**This is rarer and harder to notice than the reverse, because the output is the safe-looking
one and nobody audits a refusal.**

---

## The rule, in its current form

Started as: *when you claim two measurements corroborate, name what each would have had to
SEE to disagree; if you cannot name it, they are one measurement.*

Sharpened after E04: *check independence against the assumption every method has in common,
not only against the inputs they do not share — a shared assumption is harder to see than a
shared input because nobody writes it down.*

**L1's form is better and is the one this lane now uses:** *check the assumption the method
shares with **its own control**, not only the inputs they do not share.* It covers the
method-and-control case, which is the one that actually bit both of us today.

## 7 · A check whose failure mode returns the BEST possible score — noise is broadband

The worst of the set, and the one nearest to being published as a headline.

L1's resolution probe, pointed at a box on `oflynn-backside-fullres` that sat mostly **off the
board**, returned **0.992 of Nyquist** — "SHARP, essentially to the file's own limit". It was
drafted as the good news. On-board regions of the *same file* measure **0.195–0.258**.

**Sensor and JPEG noise reaches Nyquist by definition and resolves nothing.** So a resolution
probe aimed at empty background does not merely fail — **it returns the best possible score.**
This is worse than a check that cannot fail: it is a check whose failure mode is
*indistinguishable from the ideal result*. The only thing separating them was the region's
luma sd — **36** for the background box against **64–66** on board.

**Fix:** every row now names its region and carries that region's luma sd. What caught it was
drawing the sample box back onto the photograph and **looking** — the same move that caught the
half-max contact-shadow artifact, whose faked ellipse pointed a *different* direction in each
photograph, which no real board shape can do.

## 8 · A correct measurement with a wrong verdict printed over it

Distinct from all of the above: the number was right and the sentence above it was not. Two
instances in one tool:

- `k_first`, "the first ladder step that costs detail", is ≥2 even for a perfectly sharp
  image — so the tool printed **"ALREADY SOFT / UPSAMPLED" over a 0.992 measurement.**
- The verdict demanded `as_held > /2 > /4` and, when /2 came out *equal*, reported "cannot
  separate the controls" — when **/2 failing to separate WAS the answer.** A monotonic-ordering
  assumption had been smuggled into the verdict logic rather than the physics.

**L1's line, kept verbatim: nobody audits a refusal, and nobody audits a confident label
either.**

---

## The resolution table, because it is the fact these lessons produced

Genuine pixels across the board — rolloff × board span — not pixels per file:

| source | side shown | board span | rolloff | genuine px | genuine px/mm |
|---|---|---|---|---|---|
| `oflynn-frontside-fullres` (right) | BACK | 1924 px | 0.570 | 1097 | ~42 |
| `oflynn-frontside-fullres` (upper-left) | BACK | 1924 px | 0.445 | 856 | ~33 |
| `oflynn-backside-fullres` (left annulus) | **FRONT** | 2672 px | 0.258 | 689 | ~27 |
| `oflynn-backside-fullres` (top-right) | **FRONT** | 2672 px | 0.195 | 521 | ~20 |
| `oflynn-frontside-26mm-cropped` (M01 datum) | BACK | 787 px | 0.398 | 313 | ~12 |
| FCC photo 6, board | FRONT | 412 px | 0.289 | 119 | ~4.6 |
| FCC photo 6, **steel rule** (within-image control) | — | — | **0.383** | — | — |

**Three consequences, and the third is the one people will get wrong:**

1. **More pixels is not more information.** The 2916 × 3412 file is *softer per pixel* than the
   2347 × 2344 one and only wins because the board fills more of the frame.
2. **The steel rule is sharper than the board in the same frame** (0.383 vs 0.289). That single
   within-image number explains why the px/mm datum is solid and the rim count never was.
3. **"Prefer the sharper image" does not apply to component work, because there is no choice.**
   The components are on the FRONT, and the FRONT is imaged only by the *softer* source. The
   sharper photograph shows the side with the battery contacts and the coil — **the better
   picture is of the emptier face.** Component metrology is stuck at 20–27 genuine px/mm.
   At that scale an 0402 is 20–27 px long and workable; an **0201 is 12–16 px long and 6–8 px
   wide, and a 6-pixel width cannot support package-size discrimination.** The AirTag uses
   0201s. That boundary belongs in the BOM as a number, not discovered per line.
