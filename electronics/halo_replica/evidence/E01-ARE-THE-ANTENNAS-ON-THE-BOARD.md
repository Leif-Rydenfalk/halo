# E01 — are Apple's antennas on the board, or on the carrier?

*halo Replica lane (orchestrator), 2026-09-05. Question raised by the halo lane after Apple's
own labels were found in FCC internal photo 6. **Answer: NO. The LDS gap stays at two
antennas.** This document exists because the hopeful answer was the other one.*

## The question, and why it was worth an hour

`docs/REFERENCE-TEARDOWN.md` §2.3 says all three antennas are laser-direct-structured onto a
single moulded plastic carrier, soldered to the board across six tear-off joints. LDS needs
tooling nobody here has, so that claim is the single largest "the Replica cannot reproduce
this" in the project.

Then Apple's own regulatory filing appeared to contradict it. In
`fcc-BCGA2187-internal-photo-6.jpg` ("A2187 MLB – Front") **Apple has drawn arrows and
labelled four things: "Bluetooth Antenna", "Bluetooth Module", "UWB Antenna", "UWB Module"** —
and both labelled antennas sit at the **rim of what looks like a bare board**. If the antennas
were in the board's own copper, the LDS gap would go from two antennas to **none**, and the
biggest unbuildable item in the Replica would disappear.

That is a large enough prize to be worth testing properly rather than hoping.

## Why FCC photo 6 cannot answer it — measured, not asserted

Lane L1 calibrated that photograph against the steel rule in frame: **15.8875 px/mm**
(93 ticks over 97 mm, stderr 0.0022, split-half agreement 0.33 %). So one pixel is
**0.063 mm**, and antenna trace geometry of 0.2–0.5 mm spans **3–8 px** — in a JPEG render of
a PDF at 150 dpi. **At that scale an etched trace and a solder joint to a carrier are not
distinguishable**, and neither is a laser-structured trace. Photo 6 establishes *where* Apple
says the antennas are. It cannot establish *what they are on*.

## The instrument that can — and the argument that makes it safe

O'Flynn's `oflynn-backside-fullres.jpeg` is 2916 × 3412 px for a ~26 mm board, roughly
**90–110 px/mm — six to seven times better** — and, decisively, it is a photograph of the
board **with the plastic antenna carrier removed** (CATALOG.md states the removal explicitly
for the matching front crop).

The reasoning that makes the conclusion robust despite any remaining image-quality doubt:
**a 2.4 GHz antenna on a 26 mm board is a LARGE feature, not a fine one.** An inverted-F at
2.4 GHz is several millimetres of conductor — hundreds of pixels here. Fine detail is where
low resolution misleads you; **the absence of a large feature is not that kind of claim.**

## What the photographs actually show

Examined: the whole component side at 1000 px, and the left rim and bottom rim at native
resolution.

- **No antenna structure of any kind in the outer copper.** No meander, no inverted-F, no
  patch. Every copper feature resolves as routing, a pad, or a via.
- The rim carries a **grey, visibly fibrous/foamed material** — a conductive gasket or grey
  adhesive, not metal — lapping over the board edge. (This is also the material that defeated
  the luminance edge-detection in `metrology/M01-SCALE-AND-DATUM.md` §2, so the two findings
  corroborate each other.)
- A **gold pad ringed in yellow soldermask** sits at the extreme left rim — the shape of an
  antenna FEED point where a carrier connects, though that identification is not established
  here.
- Also legible in the same frame, and useful to lane L3: the **`1A8` / `1950` part**
  (REFERENCE-TEARDOWN's CANNOT DETERMINE U9), a metal-lid square package, blue parts marked
  `6X A75`, and `K11`-marked pairs.

## Verdict

| claim | verdict | rests on |
|---|---|---|
| No 2.4 GHz antenna is etched in the **outer copper of either side** | **PASS** — established | absence of a LARGE feature at 90–110 px/mm on the carrier-removed board, both sides |
| Apple's photo-6 labels mark antenna **positions/feeds**, not on-board antennas | **PASS** — established | the labelled positions coincide with rim pads and gasket, not with copper geometry |
| The Replica's LDS gap is **two antennas** (BLE IFA, UWB patch), not zero | **PASS** — unchanged | the above; NFC is off the list separately, being wound wire (M01 §3) |
| Whether an antenna exists on an **INNER layer** | **CANNOT DETERMINE** | inner layers are not visible in any photograph. An X-ray, or a cross-section, would settle it. Lane L4's layer-count work bears on it |
| Whether the yellow-ringed rim pad is the BLE **feed** | **CANNOT DETERMINE** | shape is suggestive; nothing measured. Continuity to the nRF's RF pin would settle it, and O'Flynn's test-point map may already carry it |

## The thing worth keeping

This lane went looking for evidence that would have removed its biggest obstacle, and found
evidence that the obstacle is real. **The prize was large enough to bias the reading, which is
exactly why the resolution argument was made explicit before the images were interpreted
rather than after.** REFERENCE-TEARDOWN §2.3 is corroborated on ANT1 and ANT3; it was wrong
only about ANT2, and that correction stands on its own separate measurement.
