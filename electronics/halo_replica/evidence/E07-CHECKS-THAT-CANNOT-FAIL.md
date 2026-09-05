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

## 9 · A control that can NEVER PASS — the same defect wearing the opposite sign

L1's centre-hole negative control required **zero detected objects inside the hole**. But the
hole is **bright background seen through the board**, so an unbounded intensity detector must
always return exactly one object there. It reported **1 at every threshold**. The requirement
was not a test of anything.

**Fix:** a **physical** upper size bound — 60 mm², against a largest real part (the UWB can) of
~35 mm². **Not** by lowering the requirement.

A control that can never pass is as useless as one that can never fail, and it is more likely
to survive review because it looks strict.

## 10 · A validation blind to the very quantity it appears to certify — and the cleanest demo of all

`c_register.validate` reported a worst held-out fold of **0.1029 mm**, which reads like a
statement of accuracy. Its scale basis was `photo6_bottom = 15.8875 px/mm` — the bottom rule's
value **at the rule, near the frame edge**. M02 measures **15.6850 px/mm at the board**, by two
routes agreeing to 0.23 %. **The basis was 1.29 % high**, and every millimetre downstream moved
with it (transferred source scale 107.686 → **106.313 px/mm**).

**The held-out error cannot see this, and L1 demonstrated it rather than arguing it.** Re-running
`validate` with the corrected scale gives **0.1029 mm in both runs, identical to four decimals** —
because validate converts the fitted *and* the held-out landmarks with the same px/mm, so a wrong
scale divides both sides equally and cancels exactly.

**0.1029 mm is a statement about REGISTRATION CONSISTENCY and carries no information about SCALE
ACCURACY.** A 1.29 % scale error and a 0.1029 mm held-out error coexist happily, and the second
never warns you about the first.

This is family 3 (methods that cannot disagree) in its purest form: **two runs differing in
exactly one number, and the check does not move.** It is the strongest single demonstration this
project has produced that a passing validation is not automatically evidence about the thing you
hoped it was evidence about.

**Fixed by extension, not forking:** `--target-px-per-mm` with a named `--target-px-per-mm-basis`,
and when the default is used the tool now *prints* that it is the rule's value and names the
board-located alternative. Default behaviour unchanged. That shape — make the assumption visible
rather than silently changing it — is the one to copy.

---

## Where this leaves the component work

**95 bright features located on the project FRONT; only 32 with a short side over 10 genuine
pixels.** Median detection area **0.178 mm²** — 0201 nominal (0.6 × 0.3 mm) **to 1 %**. So most
are **located but not sized**, exactly as the 0402/0201 boundary in §8 predicted. Every row
prints its short side in genuine pixels so the distinction cannot be lost downstream.

**The known hole, with names in it:** the detector finds *metal* — pads, terminations, cans,
solder — and is **blind to dark IC bodies**. The nRF52832 is not among the 95. For a footprint
list that is arguably correct; for a placement list it is a gap, and it is the gap that matters
most for the deliverable, because the dark packages are what make the photograph read as an
AirTag at all.

## 11 · A number that measures the operator, not the board — "the answer is the box"

L1's third dark-package attempt stated a region of interest and ran Otsu inside it. **It returns
an answer, and the answer is the box.** Padding the ROI 0 / 20 / 40 / 60 px gave **3.35 / 3.98 /
4.09 / 4.50 mm for the same package** — a **34 % swing driven entirely by the choice of box**,
touching the ROI edge at every padding.

**This is M01's "394 px was the crop frame" in a new costume**, and it would have passed
unnoticed on a single run. The tell is the same one: a result that tracks a parameter of the
*search* rather than a property of the *subject*.

**The general test: sweep the arbitrary parameter and see whether the answer moves with it.**
L1 now does this everywhere — and it is what converted the UWB can from one number into an
honest split: short side **3.56–3.67 mm, stable at 2.9 %, MEASURED**; long side **15.6 %
ROI-dependent, CANNOT DETERMINE**, with 6.735 mm as a lower bound.

## 12 · An assertion in a deliberate break that could not fire

L1's merge-detection break asserted "the merged blob must be 3× bigger than the package". **It
cannot fire**: the search box caps the blob at the ROI's own area, so a fully merged blob and a
3×-too-big one are *the same number*. Caught only because it went red when the merge had
actually happened.

**Correct evidence of merging: the blob fills the WHOLE ROI — 100.0 % against the control's
82.9 %.** A deliberate break is itself a check, and it needs the same audit as the check it
tests.

---

## The cross-validation that came free, and is the strongest result in this lane

The nRF52832-CIAA positive control measured **3.218 × 2.940 mm** against a published
**2.956 × 3.226 mm** — long **−0.23 %**, short **−0.54 %**, aspect **+0.31 %**. The candidate is
selected as the **most rectangular** in the search box, *not* the closest to the published size,
because selecting on the answer would make the control agree with itself.

**And it validates the scale, which nobody designed it to do.** That size is reached with the
*registration-derived* 106.313 px/mm; making the nRF exactly its published size would need
106.06 px/mm — **0.23 % away**. **A steel rule in a different photograph carried through a
homography, and a package dimension from a datasheet, agree to 0.23 % with neither fitted to the
other.** Applying this lane's own rule: each could have disagreed, and the assumption they share
is only that the board is rigid.

Consequence: **L3's nRF-derived 110.3 px/mm is +3.9 % against two agreeing routes and must be
re-derived.** Its 0.4 % aspect agreement still stands — aspect is scale-free — so the
segmentation was sound and the *scale it inferred* was not.

And it resolves the UWB puzzle: L3's 20.8 mm² was **physically impossible**, not a meaningful
coincidence, since TechInsights' U1 *die* is 20.58 mm² and a SiP must exceed its die. L1's
rectangle (23.98–28.92 mm²) sits comfortably above it. **The near-equality was a box that
stopped short** — family 11 again.

## 13 · A similarity you manufactured by transcription — the colour-sampling trap

The board lane proposed sampling **median RGB from Apple's photograph inside each marker** and
painting our parts that colour, to fix "ours reads as a schematic". It asked, correctly, whether
that was a measurement or an invention.

**It is a measurement — and that is not the problem.** The problem is that it makes the
comparison **circular**. Paint our board with pixels taken from Apple's photograph, set the two
side by side, and they *must* agree on colour, because we copied it. Leif's test is whether ours
looks like theirs; **a similarity manufactured by transcription measures nothing.**

This would have been the most *visually persuasive* instance of the whole family, which is
exactly what makes it the most dangerous — every other entry here is caught by a number, this one
is caught only by asking where the agreement came from.

**Ruling:** the primary comparison stays **uncoloured** — that is the render Leif's test applies
to. A coloured version may exist as a **separate** file, labelled on its face that appearance was
sampled from Apple's photograph and that the panel cannot be used to judge colour fidelity, and
no similarity metric may touch it.

**The non-circular fix is to colour by part TYPE** — ENIG gold for a pad, silver for a can, olive
or white for an MLCC — from a palette derived from the material rather than from the target
image. That **can disagree** with the photograph, which is what makes it worth drawing.

**And the honest cause is not colour at all:** ours reads as a schematic mostly because we do not
*know what most of these parts are*. A palette cannot fix that, and must not be allowed to paper
over the identification gap.

---

## The state of the deliverable when this was written

`board/out/compare-front.png` — ours | Apple's | overlay at one shared 48 px/mm, **registration
by construction rather than by alignment**, so nothing was fitted to make the panels agree.

**The one number that matters:** median luma under our 97 markers **185.0**, against **60.0** at
4000 random annulus positions; **42.3 % of markers above the random 90th percentile against 10 %
by construction — 4.23× enrichment.** The random draw is the negative control and it is printed
on the picture. The positions are not decoration.

**What is still wrong, worst first, in the board lane's own assessment:** Apple's centre hole has
a step/notch at 3–5 o'clock that our fitted superellipse rounds straight over, so our line runs
through Apple's board material there — a real geometric miss. The dark regions are **empty**, and
knowingly so. Ours reads as a schematic. The grey rim material is absent (no geometry exists for
it — CANNOT DETERMINE). The outer outline overshoots at 2–4 o'clock, fit residual sd 0.277 mm
with 55.8 % of rays inside ±0.15 mm (a plain circle gives 0.563 mm / 43.6 %). And **X1 is firing
at 3.20 % and the montage exits FAIL** — diagnosed as the instrument, not the board: dark wooden
blocks in the photograph's background merge into the thresholded silhouette. **Not loosened. A
failing check that names its own cause is worth more than a passing one.**

## 14 · A break severed from its subject by a process boundary

Distinct from family 12 (an assertion inside a break that cannot fire). Here **the break was
real, the check was real, and the break never reached the check.**

- `X3` displaced the geometry, but **panel 1 is rendered by a subprocess that knows nothing
  about the break**, so `X4` sat unmoved at 0.413 mm under a 12° rotation. The break was a
  decoration on that number. Fixed; X4 now moves 0.413 → 0.470.
- `R5`'s `--break-drop` **truncated the input rows**, so the accounting balanced and the check
  had nothing to notice. Fixed to lose markers at draw time instead.

**A break that runs in one process and a check that runs in another are not connected by
intention.** Anywhere a deliberate break crosses a subprocess, a file write, or a regenerate
step, verify the number on the far side actually moves.

## 15 · A threshold that silently inverts when its reference goes negative

The "does this model earn its extra parameters" gate read **gain > 2 × floor**, where the floor
was the same improvement measured on a synthetic shape known to have no such feature.

When the floor came out **negative**, `2 × floor` is *more negative*, so **the test passed on any
positive gain whatsoever.** A ratio test against a signed reference inverts silently, and nothing
in its output says so.

**Fix:** demand an absolute margin as well — 5 % — not only a ratio.

**And getting to that floor took two rejected controls.** The first returned **−3836 %** and was
correctly binned as nonsense rather than reported. The rebuilt one returned **−221 %**, which
turned out to be **the detector, not the control**: a line fitted to a short noisy arc comes out
nearly tangential, `d/cos(θ−normal)` diverges at 90°, and such a "facet" throws its own radius to
infinity inside its own arc. Facets more than 60° from their own normal are now refused *with
that reason*. Final floor **−0.31 %** against a real gain of **40.53 %**.

---

## The corroboration that worked — control R7

Set against the recurring failures, one clean success, and it came from asking two methods with
**different blind spots** the same question.

Markers falling outside the drawn outline is a self-consistency check that can fail. The board
lane found **16 of 100 rows** beyond 0.95 of the *fitted outline radius*. L1 had independently
flagged **14** as `on_rim_material_suspect`, by a *radial* criterion against the local edge
radius. **Intersection 14. L1-only 0.** L1's set is strictly contained in the geometric one, and
neither model was fitted to the other.

The two extras are the interesting part. B011 at 0.9648 is marginal. **D004 at 1.0413 is a
BLUE-body row outside the fitted outline — and L1's radial test ran on the 95 *bright* rows only,
so it could never have flagged it.** A genuine 15th candidate, visible only because the two
methods fail in different places. Reported, not chased, and not drawn as a confirmed part.

## The finding that may reopen a closed verdict

**Apple's centre hole is a routed pocket — arcs and straight walls — not a smooth curve.** Seven
facets admitted; line inlier fraction **0.86–1.00** against the superellipse's **0.00 on the same
arcs**; residual **0.3342 → 0.1987 mm**.

**If that is right, the three disagreeing superellipse exponents were never noise.** L1 closed
the hole as PARTIALLY DETERMINED because two photographs gave n=2.70 and n pinned at 2.00, and a
refit gave 2.449 — reasoning that assumes the shape *is* a superellipse and the spread is
measurement error. Under a pocket, **n is not a property of the hole at all**: it is whatever
exponent best splits the difference across whichever facets each photograph sampled well, so two
photographs would disagree **by construction**.

**The test, and it can fail:** fit the pocket model to FCC photo 6's hole boundary — different
photograph, different scale, different segmentation — and compare **facet angles, not n, and not
residuals**. Agreement moves the hole from PARTIALLY DETERMINED to MEASURED. Disagreement leaves
L1's verdict standing for a better reason than it currently has.
