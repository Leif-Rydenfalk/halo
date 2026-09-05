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
