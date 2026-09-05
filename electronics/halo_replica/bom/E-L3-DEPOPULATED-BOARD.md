# E-L3 — a board with the chips pulled off, and why it still cannot answer the question

*L3 (BOM identification), 2026-09-05. Side convention: **FRONT = the component side**, per
Apple's FCC filing.*

## The find

`images/airtag/oflynn-airtag-tests.jpeg` has been in this project since 2026-09-03, catalogued
as *"Bench photo: probing the SPI flash / test points with wires."* That description is true and
it buried the interesting part.

**The centre board in that photograph has packages PULLED OFF.** O'Flynn, verbatim: *"I pulled
some of the chips off to investiate any connections between the test points and the chips, using
a printed view of the nrf chip while I looked under a microscope as a reference."*

So it is the only photograph in this project in which **land patterns are bare** — including the
Apple U1 module's, which is covered by a metal can in every other image. That matters because
four of this BOM's lines (`U3` flash, `U5` amplifier, `U7` op-amp, `U8` load switch) are
**SILICON CITED** purely because nobody can point at the part, and a land pattern is a way to
point at one. A pad count is also the strongest evidence a photograph can give: unlike a length
it cannot be 4 % wrong, it is either right or it is a different integer.

## The attempt, and the answer I nearly published

`tools/b_padcount.py` counts an exposed land pattern by **two independent routes** — blob count
(threshold, label, filter by area) and lattice prediction (from the centroids alone, find the two
lattice vectors and count the lines). Route A knows nothing about periodicity; route B knows
nothing about how many blobs there were. They can refute each other.

On the U1 land pattern they agreed, and beautifully:

> **69 pads in a 6 × 12 lattice, 3 cells empty (4 %).**

That passed every reconciliation gate the tool has — nearest-neighbour spacing regular, pads
sitting on the fitted lattice, 96 % occupancy. A footprint with three depopulated corners is
exactly what a real SiP looks like. **I would have written it into the reference BOM.**

## What refused it

`--sweep`. E07 family 11: *a result that tracks a parameter of the search rather than a property
of the subject.* Re-run over 4 box paddings × 5 threshold offsets:

| quantity | range over 20 combinations | spread |
|---|---|---|
| blob count | 65 – 78 | **18 %** |
| extent across | 63.1 – 89.0 px | **33 %** |
| extent along | 30.9 – 62.4 px | **69 %** |
| aspect (scale-free) | 0.41 – 0.76 | **59 %** |
| lattice shape | 5×12, 6×12, 6×13, 6×14, 7×13, 7×14, 8×13, 9×14, 10×14 | **nine shapes** |

**Nine different lattice shapes.** Not the count, not the extent, not even the scale-free aspect
ratio survives. **Verdict: CANNOT DETERMINE, for all of it.**

### The physical reason, so nobody retries it blind

The array is about **47 × 71 source pixels** at a **5.71 px lattice pitch**, with pads about
**3 px** across, in a JPEG. Pads merge and split as the threshold moves. This is a resolution
floor, not a method defect — no threshold choice recovers information the photograph does not
contain.

**What would settle it:** a higher-resolution photograph of a depopulated component-side board.
**It does not exist in the public record reachable from here.** O'Flynn's repository was
enumerated on 2026-09-05: `images/` holds exactly eight files, seven of them images, and this
project already has all seven. `airtag-tests.jpeg` is the only one showing a depopulated board
and it is the low-resolution one.

## Why this belongs in E07's catalogue

**Three independent reconciliation gates passed and the answer was still wrong.** Regular
spacing, on-lattice position, and 96 % occupancy are all real properties, all measured, all
agreeing — and the number they agreed on moved by 18 % when the box moved by 9 px.

The gates test *whether these points form a lattice*. They do. What they cannot test is *whether
the tool found the same points twice*. Only re-running the whole pipeline with the arbitrary
parameters perturbed asks that, and it is the only test here that could have failed.

**The near-miss is the lesson: agreement among checks that share an input is not independence.**
This is the same shape as the coil error this project already recorded — a turn count and a band
width that were the same radial extent twice — arriving in a new costume, and it very nearly got
into the reference BOM as "what Apple did".

## Still open on this photograph

Two further exposed land patterns are visible on the same centre board — one near the crystals,
one lower-left — and **have not been examined.** They are smaller and denser than the U1's, so
the resolution floor above almost certainly applies to them too, but that is a prediction and it
has not been measured. If one of them is the `U3` flash it would be a **10-pad WLCSP with absent
centre pads** — O'Flynn identified the part that way, *"The SPI flash chip had 10 pins on it – it
was missing some center pins"* — which is a distinctive, countable signature and the one land
pattern in this project worth the most.

---

## The positive control, and the near-hit that would have fooled me

The section above ends by saying the two remaining land patterns *probably* hit the same
resolution floor. **That was a prediction, so I measured it** — and the second land pattern turned
out to be the best possible thing to measure, because it may have a **published answer**.

It sits beside a gold-framed part of crystal proportions, which is the nRF52832's neighbour
relationship on the populated component side. If it is the nRF's land pattern, the answer is
already known: **50 pads in a 7 × 8 grid**, 0.4 mm pitch (Nordic PS v1.4, Table 132, and the FICR
`PACKAGE` field: *"CIxx - 7x8 WLCSP 56 balls"*).

**Route A returned 49.**

A 2 % miss against a known 50. Reported on its own it would have read as a validated method *and*
a newly located part — and it would have implicitly certified the same method's answer for the
Apple U1 module in the section above.

**Every control refused it:**

| control | result |
|---|---|
| route B lattice | **5 × 8 = 40 cells** — irreconcilable with 49 blobs; the tool failed it before the sweep was reached |
| sweep, 20 combinations | blob count **5 – 56**, spread **108 %** |
| lattice shapes seen | **fifteen**: 2×4, 5×8, 5×10, 6×9, 6×13, 7×9, 7×10, 7×11, 8×11, 9×9, 9×11, 9×13, 10×9, 10×10, 10×11 |
| was the true 7 × 8 ever fitted? | **no — not once** |
| is the true 50 inside the count range? | **yes, trivially** |

**A prediction that cannot be missed is not confirmed by being hit.** 50 sits comfortably inside
5–56. The 49 carried no information whatsoever, and it is recorded here as a warning rather than
as a result.

**The conclusion does not depend on the identification.** If this is the nRF land pattern, the
method missed a known shape fifteen times out of fifteen and its count range spans an order of
magnitude, so the 49 was luck. If it is not the nRF, a 108 % spread and fifteen shapes condemn
the measurement on their own. Either way it stands.

## Consequence — this question is closed, do not spend more quota on it

Pad counting from `oflynn-airtag-tests.jpeg` is **demonstrated impossible**, against a control
with a known answer, not merely declined. The `U2` refusal above is upheld by stronger evidence
than its own sweep. **What would reopen it:** only a higher-resolution photograph of a
depopulated component-side board, and none exists in the public record reachable from here.

## What is still worth taking from this photograph

The *positions* of the bare land patterns survive even though their pad counts do not — a
position is one coarse measurement where a count needs every pad resolved. E07 §10 records that
L1's component detector *"finds metal and is blind to dark IC bodies … it is the gap that matters
most for the deliverable, because the dark packages are what make the photograph read as an
AirTag at all."* A depopulated board shows exactly where the dark packages were.

**And the tool for the populated board already exists in this lane:** `tools/b_pkgsize.py`
isolates a dark IC body on a dark PCB using a blue-minus-red channel, because luminance alone
cannot separate dark navy silicon from dark maroon laminate — that case is selftest case 10, with
a synthetic part built at *exactly* equal luminance to the ground so the luminance route provably
fails and the colour route provably succeeds. It found the nRF52832 at rectangularity 0.969. It is
offered to L1 rather than rebuilt there.
