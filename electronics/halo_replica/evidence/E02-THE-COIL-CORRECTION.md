# E02 — correcting my own coil finding: the turn count was wrong, and the two reads were not independent

*halo Replica lane (orchestrator), 2026-09-05. Written under a RED capacity signal because a
correction that is not on disk is not a correction. **M01 §3's supporting argument is
withdrawn. Its measured band geometry stands. The construction claim is now weaker than I
stated and one alternative is live.***

## What I claimed in M01 §3

That the AirTag's front coil is wound magnet wire rather than a laser-structured trace, with
this as the corroboration:

> ~5 turns are visually countable, and the measured band width 0.727 mm ÷ 5 = 0.145 mm per
> turn — AWG 35 magnet wire is 0.143 mm. The turn count read off the picture and the band
> width measured off the pixels agree to 1.4 % **without either being fitted to the other**.

`docs/REFERENCE-TEARDOWN.md` §2.3 and `spec/variants.json` were both amended on the strength
of it (halo lane, commit 2624105).

## Two things wrong with that, one raised by lane L3 and one found by measuring

**1 · The two reads were not independent.** L3 pointed out that a **voice coil is a solenoid,
wound in depth on a former**. Seen from above, a solenoid and a flat spiral can present the
*same radial band width*. So "count the turns from above" and "measure the band width" are
**two measurements of the same radial extent**. They could not have disagreed. Calling their
agreement independent corroboration was wrong, and it is the exact defect this tool's own
selftest caught elsewhere — a check that cannot disagree with what it checks.

**2 · The turn count was an undercount.** Measured properly at full resolution
(`oflynn-frontside-fullres.jpeg`, 2347 × 2344, ~6× the crop I originally used) with the new
`bin/boardmetro turns` verb, counting resolved conductors per angular sector:

| sector | conductors counted | band | implied pitch |
|---|---|---|---|
| 0° | 2 | 0.998 mm | 499 µm |
| 90° | 6 | 0.998 mm | 166 µm |
| **180°** | **9** | 0.998 mm | **111 µm** |
| 270° | 6 | 0.998 mm | 166 µm |

**It is not 5.** The best-resolved sector gives **9** conductors at ~111 µm pitch — near AWG 38
(0.1007 mm), not AWG 35. The spread of 2–9 across sectors means the coil is **not concentric
with the centre I assumed**, so the count is not yet settled either; 9 is a *lower* bound from
the sector where the conductors are actually resolved. Averaging all 96 rays around the circle
returns **1** peak — the turns smear out — which is itself the proof of non-concentricity.

## What survives, and what does not

| claim | status |
|---|---|
| Band geometry: ID 9.380 mm, OD 10.834 mm, radial width 0.727 mm (788 px crop) | **STANDS** — independent of turn count |
| The conductors are **individually resolved, coplanar, and equally lit** at full resolution | **STANDS** — this is now the actual evidence for wound wire, and it is a direct observation rather than an inference from arithmetic |
| "~5 turns, 0.145 mm/turn, AWG 35, agreeing to 1.4 %" | **WITHDRAWN.** Wrong count, and not an independent check |
| Turn count | **CANNOT DETERMINE** — ≥9 in the best-resolved sector; blocked on the coil's true centre |
| Whether this coil is the **NFC antenna** or the **voice coil** | **OPEN** — see below |

## The open question L3 raised, and why it is serious

The coil's two leads terminate on **TP1 and TP38**. `REFERENCE-TEARDOWN.md` §2.4 says TP1/TP38
are the **voice coil's** two solder joints. Apple's own arrow in FCC internal photo 5 labels
that annulus the **NFC Antenna**. Both cannot be true.

L3 also established that the voice-coil attribution for TP1/TP38 is **an assertion inside this
repo, not a quotation from O'Flynn** — his text does not say what those pads are.

**A DC resistance argument bears on it, and it currently points away from a voice coil.** At 9
turns of ~111 µm wire on a ~10.1 mm mean diameter, the conductor is ~286 mm and the DC
resistance ~**0.50 Ω**. A voice coil driven by a class-D amplifier into 4–8 Ω needs *several*
ohms — roughly a hundred turns at this wire gauge, which would need ~12 layers in depth and a
radial band far wider than the 0.727 mm measured. **The measured geometry is not consistent
with a voice coil.** But this is an inference from a photograph, not a meter reading, and it
rests on a turn count that is itself a lower bound.

**What would settle it:** DC resistance across TP1/TP38 on a live unit — sub-ohm says NFC
loop, several ohms says voice coil — or a photograph of the front dome's inner face showing
whether a coil is glued there. Neither is available here.

## Consequence, stated plainly

**If this coil turns out to be the voice coil, then REFERENCE-TEARDOWN §2.3's amended ANT2
line and `spec/variants.json`'s antenna row are both wrong, and the NFC antenna returns to the
LDS list** — taking the Replica's LDS gap back to three antennas. The halo lane has been told
directly rather than through a document, because it acted on my finding within the hour and a
wrong correction propagating is worse than the original error.

## The thing worth keeping

My first finding in this lane was accepted by two other sessions and written into two files
partly *because* I described its evidence as two independent reads that could have disagreed.
That description was the strongest sentence in the report and it was the false one. **The
failure was not the measurement; it was the claim about the measurement's structure.** When
asserting independence, name what each read would have had to see to disagree — had I done
that here, "both measure the same radial extent" would have been obvious before it propagated.
