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
