# BOM-RECONSTRUCTED — every line of the AirTag's bill of materials

<!-- GENERATED FILE. Source of truth is bom/bom.json; regenerate with
     tools/b_bom_render.py. Hand edits here will be overwritten. -->

*L3 — BOM identification, halo Replica, 2026-09-05. Reconstructed bill of materials — Apple AirTag A2187 (1st gen, FCC ID BCGA2187).*

**Status:** THIRD PASS (L8, 2026-09-05) — the SCALE IS CORRECTED and every size re-derived on it. L3's 110.3 px/mm is RETRACTED: it was one segmentation of one part divided by one datasheet number, and three segmentations of that same part span 3.8%, so the datasheet route cannot pin a scale to better than about 2%. The scale now used is 106.313 px/mm, registration-derived from a steel rule in a DIFFERENT photograph carried through a validated homography — an external physical datum that no package outline enters. See `ruler`. X1 vs X2 has been TESTED and Catley's frequency assignment is SUPPORTED. UNK-A was attempted and REFUSED with a measured reason. The resolution boundary that decides which lines can ever carry a size is now stated once, at `resolution_limit`, instead of being rediscovered per line.

**Checked by** `tools/b_bom_check.py` — six rules, each watched failing on
purpose by `--self-test`. Exit code is the verdict: 0 PASS, 1 FAIL,
2 CANNOT DETERMINE.

---

## Read this before the table

**side** — Follows Apple's FCC filing (halo commit 391f676): FRONT = the component side (the ICs). BACK = the battery-contact / coil / test-point side. Colin O'Flynn's photo filenames use the OPPOSITE words: his 'backside-*' images are Apple's FRONT, his 'frontside-*' images are Apple's BACK. Every citation below names the file, so the file name and the side word will look contradictory. They are not.

**designators** — The board carries NO visible RefDes silkscreen. Designators here are this document's own and are inherited from docs/REFERENCE-TEARDOWN.md §2 where a line exists there; lines this lane added are prefixed with their own letters and marked new_in_this_document.

**designator collision warning** — U1 in this file is the NORDIC MCU, following REFERENCE-TEARDOWN. Apple's UWB chip — universally called 'the U1' in the press — is U2 here. Never write bare 'U1' about the UWB part; write 'Apple U1'.

**units** — mm and degrees.

**Confidence scale**

- **HIGH** — the part is locatable in a photograph AND its own package marking was read there by this lane
- **MEDIUM** — locatable in a photograph but the marking is not decisive, OR identified by an instrument reading rather than a marking
- **LOW** — NOT locatable in any photograph available here — rests on a teardown's assertion only
- **CANNOT DETERMINE** — the public record does not contain it; what would settle it is named

**The rule that shapes this document:** Every line states SILICON SEEN or SILICON CITED. A SILICON CITED line cannot be HIGH confidence no matter how good the literature is. Twelve of the nineteen REFERENCE-TEARDOWN parts are SEEN; the four that halo deleted (flash, amplifier, op-amp, load switch) are all CITED, which is not a coincidence and is not evidence.

---

## The table

| ref | function | part | package | size | marking READ | seen? | confidence |
|---|---|---|---|---|---|---|---|
| **U1** | MCU (Cortex-M4F) + BLE 5 radio + NFC-A tag peripheral | Nordic Semiconductor nRF52832, variant CIAA | WLCSP-50 | **MEASURED — and it is NO LONGER THE RULER. Use the published body when you need U1's size; use `ruler` when you need the scale.** — long_mm 3.34 mm, short_mm 3.072 mm, long_px 355.1 px, short_px 326.6 px, aspect 1.087, short_side_genuine_px 63.6–84.2 px | `N52832 CIAAE0 2102JK` | SEEN | HIGH |
| **U2** | UWB transceiver (Precision Finding) | Apple U1 (die TMKA75) in a USI system-in-package | shielded SiP, rectangular metal can | **SHORT SIDE MEASURED** — short_mm 3.56–3.665 mm, long_mm CANNOT DETERMINE, long_mm_lower_bound 6.735 mm, filled_area_mm2 19.13–22.87 mm^2, short_side_genuine_px 73.7–97.5 px | `CANNOT DETERMINE` | SEEN | HIGH that this can is the UWB module (Apple labelled it in a |
| **U3** | firmware storage — holds the nRF firmware AND the Apple U1 'Rose' firmware, unen | GigaDevice GD25LQ32C-class 32 Mbit (4 MB) SPI NOR | WLCSP-10 (ten pads; centre pads absent) | **NOT YET MEASURED** | `CANNOT DETERMINE` | cited | MEDIUM — and the reason it is not LOW is worth stating: O'Fl |
| **U4** | 3-axis accelerometer — motion wake, anti-stalk sound trigger | Bosch Sensortec BMA280 (asserted) | metal-lid LGA | **MEASURED — AND THE RESULT DOES NOT CORROBORATE THE BMA280** — metal_lid_A_beside_the_TPS746_legend {long_mm 2.278 mm, short_mm 1.875 mm, long_px 242.2 px, short_px 199.3 px, aspect 1.215, short_side_genuine_px 38.8–51.4 px}, metal_lid_B_mid_left {long_mm 1.666 mm, short_mm 1.288 mm, long_px 177.1 px, short_px 136.9 px, aspect 1.294, short_side_genuine_px 26.7–35.3 px} | `NONE VISIBLE` | SEEN | CANNOT DETERMINE which part is the accelerometer. LOW for 'B |
| **U5** | audio amplifier driving the voice coil | Maxim MAX98357A (asserted; iFixit wrote MAX98357B) | WLCSP | **CANNOT DETERMINE** | `CANNOT DETERMINE` | cited | LOW |
| **U6** | main DC-DC buck, 3 V cell to 1.8 V rail | TI TPS62746 (asserted) | CANNOT DETERMINE | **CANNOT DETERMINE** | `NO PACKAGE MARKING WAS READ.` | cited | MEDIUM for 'there is a TPS746-family buck on this board' — a |
| **U7** | op-amp in the speaker/analog path | TI TLV9001 (asserted) | CANNOT DETERMINE | **CANNOT DETERMINE** | `CANNOT DETERMINE` | cited | LOW |
| **U8** | load switch / OVP gating power to the MCU and flash | onsemi FPF2487 (asserted by iFixit only) | CANNOT DETERMINE | **CANNOT DETERMINE** | `CANNOT DETERMINE` | cited | LOW. Single-source (iFixit) and not corroborated by Catley,  |
| **U9** | secondary regulator / LDO (function itself inferred, not established) | CANNOT DETERMINE | leadless moulded package, roughly square, with a large round pin-1 dim | **NOT YET MEASURED** | `1A8 / 1950` | SEEN | CANNOT DETERMINE for the part number. HIGH only for 'a part  |
| **X1** | clock crystal — assigned to 32 MHz (HFXO) by Catley | CANNOT DETERMINE — no manufacturer named anywhere | seam-sealed ceramic package with a gold-plated seal ring and a metal l | **MEASURED — and it is the first measurement in this project to TEST somebody else's claim rather than repeat it** — long_mm 2.466 mm, short_mm 1.989 mm, long_px 262.2 px, short_px 211.5 px, aspect 1.24, short_side_genuine_px 41.2–54.5 px | `T320 / RBEV` | SEEN | HIGH that the marking is T320 / RBEV. CANNOT DETERMINE for t |
| **X2** | clock crystal — assigned to 32.768 kHz (LFXO) by Catley | CANNOT DETERMINE | seam-sealed ceramic package with a gold-plated seal ring and a metal l | **MEASURED** — long_mm 1.687 mm, short_mm 1.085 mm, long_px 179.3 px, short_px 115.4 px, aspect 1.554, short_side_genuine_px 22.5–29.7 px | `A048L` | SEEN | HIGH for the marking. CANNOT DETERMINE for the part. MEDIUM  |
| **C1..C5** | bulk hold-up — keeps the tag alive for seconds after the battery is removed (thi | CANNOT DETERMINE — manufacturer and technology both unnamed | rectangular chip package, roughly 3:1 aspect, DARK body with light met | **NOT YET MEASURED** | `J107S` | SEEN | HIGH for the marking, the count of five and the location. ME |
| **L1x** | inductor — almost certainly the buck's, given its position | CANNOT DETERMINE | WIREWOUND chip inductor. Individual turns of copper wire are directly  | **NOT YET MEASURED** | `NONE VISIBLE` | SEEN | HIGH that a wirewound chip inductor is fitted at this locati |
| **J1** | coaxial RF connector — a conducted-measurement port. Its position beside the UWB | CANNOT DETERMINE — a U.FL / IPEX MHF-class receptacle by construction | circular RF receptacle: metal outer shell, four solder tabs, a dark di | **NOT YET MEASURED** | `NONE VISIBLE` | SEEN | HIGH that a coaxial RF receptacle is fitted at this location |
| **D1, D2** | CANNOT DETERMINE. RESEARCH-A calls the K11-marked parts 'schottky pairs'; nothin | CANNOT DETERMINE | small two-terminal-looking moulded chip parts, a matched pair placed s | **NOT YET MEASURED** | `K11` | SEEN | HIGH for the marking and the pairing. CANNOT DETERMINE for t |
| **CT1** | CANNOT DETERMINE. RESEARCH-A §2.1 describes 'a blue tantalum / 6X A75 cap'. | CANNOT DETERMINE | blue-bodied moulded chip package with a printed polarity/pin-1 dot | **MEASURED BUT NOT TRUSTED — unchanged by the scale correction** — long_mm 0.851 mm, short_mm 0.85 mm, long_px 90.5 px, short_px 90.4 px, aspect 1.001, short_side_genuine_px 17.6–23.3 px | `6X A75` | SEEN | HIGH for the marking. CANNOT DETERMINE for the part, the val |
| **UNK-A** | CANNOT DETERMINE | CANNOT DETERMINE | large matte-black moulded rectangle, roughly 2:1 aspect, no marking of | **CANNOT DETERMINE — ATTEMPTED, and refused by its own controls** | `NONE VISIBLE` | SEEN | CANNOT DETERMINE |
| **UNK-B** | CANNOT DETERMINE. Position — between the UWB module and the coaxial connector J1 | CANNOT DETERMINE | pale beige/ivory ceramic-looking square package with a single small da | **NOT YET MEASURED** | `NONE VISIBLE` | SEEN | CANNOT DETERMINE |
| **R/C/L bulk** | decoupling, RF matching networks, pull-ups | CANNOT DETERMINE, individually and collectively | two-terminal chip passives, several distinct sizes present on both sid | **NOT YET MEASURED** | `NONE — chip passives of this size carry no marking` | SEEN | CANNOT DETERMINE for every individual value. This is not a g |
| **ANT1** | BLE antenna, 2.4 GHz, inverted-F | Apple's own structure | printed onto the plastic carrier, per O'Flynn | **CANNOT DETERMINE** | `n/a` | SEEN | HIGH that Apple labels a Bluetooth antenna at that rim posit |
| **ANT2** | NFC antenna, 13.56 MHz | wound magnet wire coil (NOT a laser-structured trace) | wound coil | **BAND GEOMETRY MEASURED (M01 §3) AND IT STANDS. The supporting turn-count argument is WITHDRAWN — see evidence/E02-THE-COIL-CORRECTION.md.** — inner_diameter 9.38, outer_diameter 10.834, radial_band_width 0.727 | `n/a` | SEEN | HIGH that the conductors are individually resolved, coplanar |
| **ANT3** | UWB antenna, 6.5 / 8 GHz, one integral patch | Apple's own structure | printed onto the plastic carrier, per O'Flynn | **CANNOT DETERMINE** | `n/a` | SEEN | HIGH for the label. CANNOT DETERMINE for the geometry. |
| **SPK-COIL** | voice coil — the moving half of the sounder | wound magnet wire, glued to the plastic dome per iFixit and Catley | wound coil | **CANNOT DETERMINE** | `n/a` | cited | LOW for anything geometric. HIGH for the mechanism (coil aga |
| **SPK-MAGNET** | fixed magnet at the centre of the annular board | rare-earth magnet, grade and dimensions unpublished | disc | **NOT YET MEASURED** | `n/a` | SEEN | MEDIUM |
| **BATT** | power source | CR2032 3 V lithium coin cell; the FCC sample carried a Panasonic cell marked 'Made in Indonesia' | CR2032, 20 mm x 3.2 mm by definition of the standard | **DEFINED BY THE IEC CR2032 STANDARD** — diameter 20.0, height 3.2 | `Panasonic CR2032 3V` | SEEN | HIGH |
| **BATT-CONTACTS** | connector-less battery interface | 3 sprung metal contacts — 1 negative dome on the well floor, 2 positive tabs on the wall | stamped spring contacts | **NOT YET MEASURED** | `n/a` | SEEN | HIGH for the arrangement. |
| **PCB** | the annular main logic board | Apple MLB 820-01736-A (retail, O'Flynn's unit) / 920-08283-01 (FCC sample) | annular, 2 populated sides, 0.3 mm thick per O'Flynn | **CANNOT DETERMINE for the outer diameter — M01 §2, the gasket overlaps the edge in IMG-CROP26. A ruler-derived datum from FCC-6 is lane L1's work item, not this lane's.** | `820-01736-A; 2920 17; a lone 'C'; an Apple logo; a 2D data-matrix code; legend 'FB1P'; legend '4BU / LA'; legend '98C0051 / TPS746'` | SEEN | HIGH for the strings. |

---

## Every line in full

### U1 — MCU (Cortex-M4F) + BLE 5 radio + NFC-A tag peripheral

- **part** — Nordic Semiconductor nRF52832, variant CIAA
- **package** — WLCSP-50
- **size** — **MEASURED — and it is NO LONGER THE RULER. Use the published body when you need U1's size; use `ruler` when you need the scale.** — long_mm 3.34 mm, short_mm 3.072 mm, long_px 355.1 px, short_px 326.6 px, aspect 1.087, short_side_genuine_px 63.6–84.2 px
  - **published_body_mm**
    - **long** — 3.226
    - **short** — 2.956
    - **aspect** — 1.0914
    - **source** — Nordic nRF52832 PS v1.4, Table 132, p.541 (nominal). The datasheet gives min/max on thickness only, not on D or E.
  - **method** — tools/b_pkgsize.py, minimum-area rotated rectangle of the largest connected component. 17/17 selftest, every negative control watched firing on purpose, including the ROI padding sweep and the median-cross-section limit case.
  - **ruler** — 106.313 px/mm, registration-derived (see the document's `ruler` block). Carries about +/-1% of scale and about +/-4% of segmentation method; b_pkgsize leans HIGH by 3.5-3.9% on the one part with a published body.
  - **aspect agreement stands** — 1.087 measured against 1.0914 published, 0.4% apart, with nothing fitted to make it happen. Aspect is scale-free, so this survives the scale retraction intact and it still corroborates both the identification and the segmentation.
  - **the disagreement that does NOT go away** — At 106.313 px/mm this outline reads 3.340 x 3.072 mm against a published 3.226 x 2.956 — +3.54% and +3.92%. Neither the ROI (0.00% over a 0/20/40/60 px pad sweep) nor the threshold (a 351-359 px plateau across 17 luma units) explains it. It is the segmentation's outline convention, and it is the measured basis for the +/-4% attached to every size in this file.
  - **pad_sweep** — 0/20/40/60 px -> 355.1 x 326.6 px at every padding, spread 0.00%. STABLE.
- **marking** — `N52832 CIAAE0 2102JK`, read by L3, off IMG-BACK crop [818:1432, 477:1125] at 2x
  - *legibility* — fully legible, three lines, laser-marked on dark blue silicon
- **locatable in a photograph** — YES — Apple FRONT side, upper-left arc, immediately right of the T320/RBEV crystal and below the A048L crystal
- **evidence class** — SILICON SEEN
- **confidence** — HIGH
- **what the marking establishes** — Nordic nRF52832. Read against Figure 165 of NRF-PS, which gives the marking layout as N52832 / <PP><VV><H><P> / <YY><WW><LL>, the observed 'N52832 CIAAE0 2102JK' decodes as package CI, variant AA, hardware E, production 0, year 21, week 02, lot JK — a wk02-2021 part, consistent with a 2021 retail unit. Table 10 of the same document gives nRF52832-CIAA as 64 kB RAM / 512 kB flash, so the memory size now rests on a datasheet rather than on an inference from the ordering code.
- **what it does NOT establish** — The build code 'E0' is decoded here only as far as Figure 165's field layout goes — Nordic publishes no table of hardware/production code VALUES in v1.4, so 'hardware revision E' is the field's name, not a looked-up meaning.
- **what would settle it** — Nordic's nRF52832 PS/ordering-code table for the CIAAE0 build code.
- **Replica verdict** — 1:1 — catalogue part, buyable.

### U2 — UWB transceiver (Precision Finding)

- **part** — Apple U1 (die TMKA75) in a USI system-in-package
- **package** — shielded SiP, rectangular metal can
- **size** — **SHORT SIDE MEASURED** — short_mm 3.56–3.665 mm, long_mm CANNOT DETERMINE, long_mm_lower_bound 6.735 mm, filled_area_mm2 19.13–22.87 mm^2, short_side_genuine_px 73.7–97.5 px
  - **method** — L1, metrology/uwb-can-remeasure.json — a five-step ROI padding sweep at 0/25/50/75/100 px, none of which clipped.
  - **ruler** — 106.313 px/mm, registration-derived (see the document's `ruler` block). Carries about +/-1% of scale and about +/-4% of segmentation method; b_pkgsize leans HIGH by 3.5-3.9% on the one part with a published body.
  - **what the sweep said** — Short side moves 2.9% across the sweep and is a measurement. Long side moves 15.6% (6.735 -> 7.891 mm) and is a measurement of the ROI, so it is refused with 6.735 mm published as the lower bound.
  - **L3's 6.16 x 3.37 mm = 20.8 mm^2 is RETRACTED** — It was physically impossible, not a meaningful coincidence: TechInsights measure the Apple U1 DIE at 20.58 mm^2 and a SiP module must exceed its own die. The box had stopped short. The corrected filled area is 19.1-22.9 mm^2 and the bounding rectangle is larger still.
- **marking** — `CANNOT DETERMINE`, read by L3, off IMG-BACK crop [700:1600, 2350:2950] at 2.5x
  - *legibility* — The can carries faint embossed characters and a fine cross-hatch texture. Individual glyph shapes are visible but this lane could not resolve them into text at any magnification available. NOT read.
- **locatable in a photograph** — YES — Apple FRONT side, lower-left, the largest single object on the board. Corroborated by Apple's own arrow 'UWB Module' in FCC-6.
- **evidence class** — SILICON SEEN (the module). SILICON CITED (the die inside it).
- **confidence** — HIGH that this can is the UWB module (Apple labelled it in a regulatory filing). MEDIUM that the die is TMKA75 — that rests on Catley via siliconpr0n, not on anything visible here.
- **what the marking establishes** — nothing — no marking was read.
- **what it does NOT establish** — everything.
- **what would settle it** — A decapsulated module photograph, or the siliconpr0n die shot read directly.
- **Replica verdict** — GAP — DECISIONS.md D23. Apple's U1 is never sold to anyone at any price. The Replica records this footprint as PRESENT AND UNPOPULATED. This is not a sourcing problem to be worked; it is a wall, and no effort is spent on it.

### U3 — firmware storage — holds the nRF firmware AND the Apple U1 'Rose' firmware, unencrypted

- **part** — GigaDevice GD25LQ32C-class 32 Mbit (4 MB) SPI NOR
- **package** — WLCSP-10 (ten pads; centre pads absent)
- **size** — **NOT YET MEASURED**  
  Cannot be measured because the part cannot be located in any photograph here.
- **marking** — `CANNOT DETERMINE`
  - *legibility* — The part is not locatable, so no marking was read.
- **locatable in a photograph** — NO. This is one of the four parts nobody here can point at. O'Flynn states it is reachable by cutting through the black plastic carrier, which means it sits under the carrier in an assembled unit and is not necessarily in the field of view of IMG-BACK.
- **evidence class** — SILICON CITED
- **confidence** — MEDIUM — and the reason it is not LOW is worth stating: O'Flynn did not read a marking either, he read the chip. Segger J-Flash SPI reported the device as a GD25LQ32C over SPI (OFLYNN-BLOG). That is a JEDEC device-ID readout from the live silicon — an instrument reading, which is better evidence than a photographed marking, but it is HIS instrument reading and not one this lane took, and it identifies a device ID, not an orderable part number.
- **what the marking establishes** — n/a
- **what it does NOT establish** — n/a
- **what would settle it** — Reading the JEDEC ID off a unit here, or a photograph that resolves the WLCSP-10 with its marking.
- **considered and rejected**
  - *GigaDevice GD25LE32D* (source: iFixit, repeated in REFTEAR §2.1 and RESEARCH-A §3) — It conflicts with an instrument reading. O'Flynn's J-Flash reported GD25LQ32C; iFixit's GD25LE32D appears to be a visual/parts-list assertion. When a photograph-or-catalogue claim and a JEDEC ID readout disagree, the readout wins. Recorded rather than deleted because the two are different families (LE vs LQ) and a Replica that buys the wrong one would still appear to work.
- **Replica verdict** — 1:1 by function — generic 32 Mbit SPI NOR. Note that halo deleted this part; that is why nobody in this project has ever had to point at it.

### U4 — 3-axis accelerometer — motion wake, anti-stalk sound trigger

- **part** — Bosch Sensortec BMA280 (asserted)
- **package** — metal-lid LGA
- **size** — **MEASURED — AND THE RESULT DOES NOT CORROBORATE THE BMA280** — metal_lid_A_beside_the_TPS746_legend {long_mm 2.278 mm, short_mm 1.875 mm, long_px 242.2 px, short_px 199.3 px, aspect 1.215, short_side_genuine_px 38.8–51.4 px}, metal_lid_B_mid_left {long_mm 1.666 mm, short_mm 1.288 mm, long_px 177.1 px, short_px 136.9 px, aspect 1.294, short_side_genuine_px 26.7–35.3 px}  
  A BMA280 is a SQUARE 2.0 x 2.0 mm LGA. Neither lid measures square: aspects 1.215 and 1.293, and aspect is SCALE-FREE so the scale correction does not touch this conclusion at all. At 106.313 px/mm lid A is 2.278 x 1.875 mm and lid B is 1.666 x 1.288 mm; lid B is still too small to be a BMA280. The re-derivation made lid A LARGER and therefore slightly closer to 2.0 x 2.0 on its long axis and further on its short — it did not rescue the identification. This is a check that could have agreed and did not, before and after the correction. It does not refute an accelerometer being on the board; it refutes anyone here having pointed at it.
  - **method** — tools/b_pkgsize.py, lum/bright, boxes [1760:2050,690:1010] and [420:630,1560:1790]
  - **ruler** — 106.313 px/mm, registration-derived (see the document's `ruler` block). Carries about +/-1% of scale and about +/-4% of segmentation method; b_pkgsize leans HIGH by 3.5-3.9% on the one part with a published body.
- **marking** — `NONE VISIBLE`, read by L3, off IMG-BACK
  - *legibility* — The metal-lid parts carry a single dark dimple and no readable text at any magnification available.
- **locatable in a photograph** — AMBIGUOUS, and this is a finding. IMG-BACK contains at least TWO visually identical bare-metal-lid parts with a single dark dimple: one at crop [1705:2450, 545:1100] (beside the 98C0051/TPS746 board legend) and one at crop [440:620, 1570:1780] (mid-left). RESEARCH-A §2.1 says 'a small metal-lid sensor (the BMA280 accelerometer)' as if there were one. This lane cannot say which of the two is the accelerometer, and neither can the literature as written.
- **evidence class** — SILICON SEEN (a metal-lid part is seen). SILICON CITED (that it is a BMA280).
- **confidence** — CANNOT DETERMINE which part is the accelerometer. LOW for 'BMA280' — it is a teardown assertion that this lane tried to corroborate by size and could not.
- **what the marking establishes** — nothing — there is no marking.
- **what it does NOT establish** — the manufacturer, the part, or the function.
- **what would settle it** — Measuring both parts (a BMA280 is 2.0 x 2.0 mm square; a part that measures 1.5 x 2.0 mm is not one), or a teardown that photographs the lid removed.
- **Replica verdict** — 1:1 / SUB — any low-power 3-axis accelerometer serves; DULT requires the function.

### U5 — audio amplifier driving the voice coil

- **part** — Maxim MAX98357A (asserted; iFixit wrote MAX98357B)
- **package** — WLCSP
- **size** — **CANNOT DETERMINE**  
  not locatable, so not measurable
- **marking** — `CANNOT DETERMINE`
  - *legibility* — part not locatable
- **locatable in a photograph** — NO — one of the four parts nobody can point at.
- **evidence class** — SILICON CITED
- **confidence** — LOW
- **what the marking establishes** — n/a
- **what it does NOT establish** — n/a
- **what would settle it** — A component-side photograph at higher magnification with the plastic carrier removed, or a teardown that names where it sits.
- **considered and rejected**
  - *MAX98357B* (source: iFixit) — Not rejected — recorded as an unresolved disagreement with Catley's MAX98357A. The A and B differ in gain/output configuration. Neither is confirmed by anything visible here, so writing either one as fact would be a guess.
- **Replica verdict** — 1:1 / SUB. halo deleted this part.

### U6 — main DC-DC buck, 3 V cell to 1.8 V rail

- **part** — TI TPS62746 (asserted)
- **package** — CANNOT DETERMINE
- **size** — **CANNOT DETERMINE**
- **marking** — `NO PACKAGE MARKING WAS READ.`, read by L3, off IMG-BACK crop [1705:2450, 545:1100] at 2x
  - *legibility* — TRAP, MEASURED AND CONFIRMED BY THIS LANE'S OWN EYES: the string '98C0051 / TPS746' that REFTEAR and RESEARCH-A both record as this part's package marking is WHITE BOARD LEGEND. It is printed in the same white silkscreen ink and the same font as other board legend, it sits on the laminate and not on any component, and it carries a printed pin-1 dot of its own. It is adjacent to a bare-metal-lid part that carries no text at all. A board legend beside a part is a designer's note, not a package marking, and the two are not interchangeable evidence.
- **locatable in a photograph** — The LEGEND is locatable. The PART the legend refers to is presumed to be the adjacent metal-lid device, but 'the legend points at the nearest part' is an assumption, not a measurement.
- **evidence class** — SILICON CITED
- **confidence** — MEDIUM for 'there is a TPS746-family buck on this board' — a board legend is authored by Apple's own layout engineer and is decent evidence of intent. LOW for 'the metal-lid part next to it is that buck'. The identification may well stand; the DESCRIPTION of how it was identified, in REFTEAR §2.1 and RESEARCH-A §3, is wrong and is corrected here.
- **what the marking establishes** — That the board's designer wrote 'TPS746' next to this location. That is a strong hint at the intended part family.
- **what it does NOT establish** — What is actually fitted. Legend and fit diverge on real boards. It also does not establish the package, since no package was read.
- **what would settle it** — A photograph resolving the fitted part's own marking, or a continuity/voltage measurement on a live unit.
- **Replica verdict** — 1:1 / SUB

### U7 — op-amp in the speaker/analog path

- **part** — TI TLV9001 (asserted)
- **package** — CANNOT DETERMINE
- **size** — **CANNOT DETERMINE**
- **marking** — `CANNOT DETERMINE`
  - *legibility* — part not locatable
- **locatable in a photograph** — NO — one of the four parts nobody can point at.
- **evidence class** — SILICON CITED
- **confidence** — LOW
- **what the marking establishes** — n/a
- **what it does NOT establish** — n/a
- **what would settle it** — A higher-magnification component-side photograph, or a teardown that says where it is.
- **Replica verdict** — 1:1 / SUB. halo deleted this part.

### U8 — load switch / OVP gating power to the MCU and flash

- **part** — onsemi FPF2487 (asserted by iFixit only)
- **package** — CANNOT DETERMINE
- **size** — **CANNOT DETERMINE**
- **marking** — `CANNOT DETERMINE`
  - *legibility* — part not locatable
- **locatable in a photograph** — NO — one of the four parts nobody can point at.
- **evidence class** — SILICON CITED
- **confidence** — LOW. Single-source (iFixit) and not corroborated by Catley, O'Flynn or any photograph here.
- **what the marking establishes** — n/a
- **what it does NOT establish** — n/a
- **what would settle it** — A second independent teardown naming the same part, or a marking read off a photograph.
- **Replica verdict** — SUB by intent — aggressive power gating is WHY sleep is 2.3 uA. Copy the intent, not necessarily the part. halo deleted this part.

### U9 — secondary regulator / LDO (function itself inferred, not established)

- **part** — CANNOT DETERMINE
- **package** — leadless moulded package, roughly square, with a large round pin-1 dimple at one corner and pads on at least two sides. Not resolved to a JEDEC package name.
- **size** — **NOT YET MEASURED**  
  Measurable — the part is located and its outline is crisp.
- **marking** — `1A8 / 1950`, read by L3, off IMG-BACK crop [580:760, 1600:1820] at 6x
  - *legibility* — Two short lines, laser-marked, read with the crop rotated: '1A8' and '1950'. Matches what RESEARCH-A recorded. The glyphs are at the limit of this photograph — '1A8' could be '1AB' and the leading '1' of '1950' is the least certain character.
- **locatable in a photograph** — YES — Apple FRONT side, mid-left cluster, immediately right of a metal-lid part and left of a large olive-bodied capacitor.
- **evidence class** — SILICON SEEN
- **confidence** — CANNOT DETERMINE for the part number. HIGH only for 'a part bearing these two lines exists at this location'.
- **what the marking establishes** — That the fitted part is marked 1A8 / 1950. Nothing more. A three-character top mark is a manufacturer's private code; it identifies a part only against that manufacturer's own marking table.
- **what it does NOT establish** — The manufacturer, the function, or even that it is a regulator. iFixit's own note is 'likely onsemi DC-DC' and 'likely TI DC-DC' — two different guesses, in one document, about parts in this cluster. That is what an unidentified marking looks like when it is written down honestly.
- **what would settle it** — A marking-code lookup against onsemi's and TI's device-marking tables — searchable, but this lane did not find an authoritative one and will not assert one from memory. Failing that, a decapsulation or a die shot.
- **considered and rejected**
  - *Any specific LDO part number* (source: the temptation to fill the cell) — This is the exact cell the brief warns about. The obvious answer for the function is not evidence about the part. It stays empty, and it stays empty on purpose.
- **Replica verdict** — CANNOT DETERMINE. The Replica cannot copy a part nobody has named.

### X1 — clock crystal — assigned to 32 MHz (HFXO) by Catley

- **part** — CANNOT DETERMINE — no manufacturer named anywhere
- **package** — seam-sealed ceramic package with a gold-plated seal ring and a metal lid, two visible pads; the classic SMD crystal package family
- **size** — **MEASURED — and it is the first measurement in this project to TEST somebody else's claim rather than repeat it** — long_mm 2.466 mm, short_mm 1.989 mm, long_px 262.2 px, short_px 211.5 px, aspect 1.24, short_side_genuine_px 41.2–54.5 px
  - **median_cross_section**
    - **long_px** — 232.5 px
    - **short_px** — 206.3 px
    - **aspect** — 1.127
    - **p25_long_px** — 228.2 px
    - **p25_short_px** — 172.3 px
    - **p25_aspect** — 1.324
    - **protrusion_over_median**
      - **long_frac** — 0.128
      - **short_frac** — 0.025
  - **method** — tools/b_pkgsize.py, minimum-area rotated rectangle of the largest connected component. 17/17 selftest, every negative control watched firing on purpose, including the ROI padding sweep and the median-cross-section limit case. Box 700,830,1110,1290, lum/bright. The overlay was LOOKED at: the segmentation traces the ceramic body and its gold seal ring and then bulges out into the four white solder fillets at the corners, which is why the median cross-section is reported beside the rectangle.
  - **ruler** — 106.313 px/mm, registration-derived (see the document's `ruler` block). Carries about +/-1% of scale and about +/-4% of segmentation method; b_pkgsize leans HIGH by 3.5-3.9% on the one part with a published body.
  - **pad_sweep** — 0/20/40/60 px -> long spread 1.29%, short 0.05%, aspect 1.224-1.240. STABLE.
  - **package code** — 2.466 x 1.989 mm is the 2520 code (2.5 x 2.0 mm) to -1.4% / -0.6%. 2520 is the canonical package for a MHz-range AT-cut crystal.
  - **raw** — bom/measurements/X1-T320.json
- **marking** — `T320 / RBEV`, read by L3, off IMG-BACK crop [818:1432, 477:1125] at 2x
  - *legibility* — Both lines fully legible.
- **locatable in a photograph** — YES — Apple FRONT side, immediately left-below the nRF52832.
- **evidence class** — SILICON SEEN
- **confidence** — HIGH that the marking is T320 / RBEV. CANNOT DETERMINE for the manufacturer, the part number, the load capacitance and the tolerance. MEDIUM for 'this is the 32 MHz one' — Catley's assignment, now TESTED by package geometry and SUPPORTED (see X1_vs_X2_TEST). Tested-and-supported, not HIGH: a 2520 package is strongly skewed to MHz parts, not exclusive to them.
- **what the marking establishes** — The two lines exist on this part. 'T320' is suggestive of 32.0 MHz but a top mark that looks like a frequency is not a frequency; crystal top marks are routinely lot codes.
- **what it does NOT establish** — Frequency, load capacitance (which the Replica MUST have to match the nRF's internal caps), tolerance, or drift. All four are needed to build and none is available.
- **what would settle it** — A crystal-vendor marking table, or measuring a live unit's clock.
- **Replica verdict** — SUB — any 32 MHz crystal meeting Nordic's nRF52832 HFXO spec. The exact Apple part is unbuyable because it is unnamed.

### X2 — clock crystal — assigned to 32.768 kHz (LFXO) by Catley

- **part** — CANNOT DETERMINE
- **package** — seam-sealed ceramic package with a gold-plated seal ring and a metal lid; visibly a LONGER, narrower outline than X1 in the same photograph at the same scale
- **size** — **MEASURED** — long_mm 1.687 mm, short_mm 1.085 mm, long_px 179.3 px, short_px 115.4 px, aspect 1.554, short_side_genuine_px 22.5–29.7 px
  - **median_cross_section**
    - **long_px** — 173.5 px
    - **short_px** — 111.3 px
    - **aspect** — 1.559
    - **p25_long_px** — 167.3 px
    - **p25_short_px** — 110.4 px
    - **p25_aspect** — 1.516
    - **protrusion_over_median**
      - **long_frac** — 0.033
      - **short_frac** — 0.037
  - **method** — tools/b_pkgsize.py, minimum-area rotated rectangle of the largest connected component. 17/17 selftest, every negative control watched firing on purpose, including the ROI padding sweep and the median-cross-section limit case. Box 990,470,1250,700, lum/bright.
  - **ruler** — 106.313 px/mm, registration-derived (see the document's `ruler` block). Carries about +/-1% of scale and about +/-4% of segmentation method; b_pkgsize leans HIGH by 3.5-3.9% on the one part with a published body.
  - **pad_sweep** — 0/20/40/60 px -> long spread 0.08%, short 0.00%, aspect 1.554-1.555. STABLE.
  - **package code** — 1.687 x 1.086 mm is the 1610 code (1.6 x 1.0 mm) to +5.4% / +8.6% — inside the +/-4% segmentation and +/-1% scale bands only marginally, so 1610 is the nearest standard code and is NOT proven. 1610 is the canonical package for a 32.768 kHz tuning-fork crystal.
  - **raw** — bom/measurements/X2-A048L.json
- **marking** — `A048L`, read by L3, off IMG-BACK crop [818:1432, 477:1125] at 2x
  - *legibility* — Single line, fully legible.
- **locatable in a photograph** — YES — Apple FRONT side, directly above the nRF52832.
- **evidence class** — SILICON SEEN
- **confidence** — HIGH for the marking. CANNOT DETERMINE for the part. MEDIUM for the frequency assignment, now TESTED by package geometry and SUPPORTED (see X1_vs_X2_TEST). Its aspect 1.554 and 1610-code size are what a 32.768 kHz tuning-fork part looks like; neither is exclusive to one.
- **what the marking establishes** — The one line exists on this part.
- **what it does NOT establish** — Frequency, load capacitance, tolerance (a 32.768 kHz part's ppm rating sets the Find My timing budget), manufacturer.
- **what would settle it** — As X1.
- **Replica verdict** — SUB

### C1..C5 — bulk hold-up — keeps the tag alive for seconds after the battery is removed (this is what makes the 5x-remove reset ritual work) and buffers speaker transients

- **part** — CANNOT DETERMINE — manufacturer and technology both unnamed
- **package** — rectangular chip package, roughly 3:1 aspect, DARK body with light metallised end terminations and a light laser-etched top mark
- **size** — **NOT YET MEASURED**
- **marking** — `J107S`, read by L3, off IMG-FRONT crop [200:700, 1050:1800] at 3x
  - *legibility* — Fully legible on multiple parts.
- **locatable in a photograph** — YES — Apple BACK side (battery-contact side), around the rim. COUNT VERIFIED BY THIS LANE: five parts bearing J107S are countable in IMG-TP — three in the 8-to-10-o'clock arc, one at 3 o'clock, one at 5 o'clock. The number five is Catley's and EDN's; it is also this lane's own count off the photograph.
- **evidence class** — SILICON SEEN
- **confidence** — HIGH for the marking, the count of five and the location. MEDIUM for '100 uF'. CANNOT DETERMINE for the technology.
- **what the marking establishes** — That the parts are marked J107S, five of them. In the EIA three-digit code 107 reads as 10 x 10^7 pF = 100 uF, which INDEPENDENTLY CORROBORATES Catley's and EDN's 100 uF — the value was not taken on their word alone.
- **what it does NOT establish** — Voltage rating, ESR, or technology. RESEARCH-A and EDN both say 'electrolytic'; REFTEAR says 'electrolytic/tantalum'. The photographed body is dark with metallised ends, which is not what a 100 uF MLCC looks like, but this lane will not name a technology off a body colour.
- **what would settle it** — A capacitor-vendor marking table for J107S, or a measurement on a live unit.
- **considered and rejected**
  - *'100 uF MLCC'* (source: plausible for the size) — The photographed body is dark, not the pale ceramic of an MLCC of this size. Recorded as an observation, not promoted to an identification.
- **Replica verdict** — SUB — the FUNCTION (about 500 uF of hold-up on the 3 V rail) is what the Replica must copy; five identical parts is a layout choice.

### L1x — inductor — almost certainly the buck's, given its position  *(added by this lane; not in REFERENCE-TEARDOWN)*

- **part** — CANNOT DETERMINE
- **package** — WIREWOUND chip inductor. Individual turns of copper wire are directly resolvable over the core between two metallised end caps. This is a construction observation, not an inference.
- **size** — **NOT YET MEASURED**
- **marking** — `NONE VISIBLE`, read by L3, off IMG-BACK crop [818:1432, 477:1125] at 2x
  - *legibility* — no top mark; wirewound chip inductors of this class usually carry none
- **locatable in a photograph** — YES — Apple FRONT side, upper-left, between the A048L crystal and the board rim.
- **evidence class** — SILICON SEEN
- **confidence** — HIGH that a wirewound chip inductor is fitted at this location. CANNOT DETERMINE for inductance, current rating, DCR and manufacturer.
- **what the marking establishes** — n/a — the CONSTRUCTION is the evidence here, not a marking. Wirewound and multilayer inductors of the same footprint have very different DCR and saturation behaviour, so this observation is worth something to a Replica builder even with no part number.
- **what it does NOT establish** — the value.
- **what would settle it** — An LCR measurement on a live unit.
- **Replica verdict** — SUB. Not in REFERENCE-TEARDOWN at all; added by this lane.

### J1 — coaxial RF connector — a conducted-measurement port. Its position beside the UWB module is consistent with a UWB conducted-test port, but the net it lands on is not established here.  *(added by this lane; not in REFERENCE-TEARDOWN)*

- **part** — CANNOT DETERMINE — a U.FL / IPEX MHF-class receptacle by construction
- **package** — circular RF receptacle: metal outer shell, four solder tabs, a dark dielectric annulus and a gold centre contact. Unambiguous at 5x.
- **size** — **NOT YET MEASURED**  
  Worth measuring: U.FL-R-SMT is 2.6 mm across, MHF4 is 2.0 mm. The measurement would name the family.
- **marking** — `NONE VISIBLE`, read by L3, off IMG-BACK crop [1540:1950, 2600:2820] at 5x
  - *legibility* — connectors of this class carry no marking
- **locatable in a photograph** — YES — Apple FRONT side, immediately right of the UWB module can.
- **evidence class** — SILICON SEEN
- **confidence** — HIGH that a coaxial RF receptacle is fitted at this location on this unit.
- **what the marking establishes** — n/a
- **what it does NOT establish** — Which net it is on, and whether it is fitted on every production unit.
- **what would settle it** — Continuity from the connector to the UWB module on a live unit; or the same region in FCC-6 at sufficient resolution to confirm it on a second board.
- **⚠ contradicts an existing document** — REFTEAR §2.5 states 'connectors: none anywhere — 1:1, copy this', and RESEARCH-A §2.2 opens 'There are no connectors anywhere.' There is a connector, on the retail board O'Flynn photographed (silkscreen 820-01736-A, date 2920 17), and it is one of the more conspicuous objects on the component side. The claim was almost certainly meant as 'no off-board wiring connectors', which is still true and still the interesting point. Corrected here rather than argued: the sentence as written is refuted by the photograph the same document cites.
- **Replica verdict** — SUB / OMIT.

### D1, D2 — CANNOT DETERMINE. RESEARCH-A calls the K11-marked parts 'schottky pairs'; nothing visible here establishes that.  *(added by this lane; not in REFERENCE-TEARDOWN)*

- **part** — CANNOT DETERMINE
- **package** — small two-terminal-looking moulded chip parts, a matched pair placed side by side
- **size** — **NOT YET MEASURED**
- **marking** — `K11`, read by L3, off IMG-BACK crop [660:830, 1770:1890] at 8x
  - *legibility* — legible on both parts of the pair
- **locatable in a photograph** — YES — Apple FRONT side, mid-left cluster, below and right of the 1A8/1950 part.
- **evidence class** — SILICON SEEN
- **confidence** — HIGH for the marking and the pairing. CANNOT DETERMINE for the part and the function.
- **what the marking establishes** — Two parts marked K11 sit side by side. A shared top mark plus adjacent placement is good evidence they are the same part used twice.
- **what it does NOT establish** — That they are Schottky diodes, or diodes at all.
- **what would settle it** — A marking table; or a diode test on a live unit.
- **Replica verdict** — CANNOT DETERMINE

### CT1 — CANNOT DETERMINE. RESEARCH-A §2.1 describes 'a blue tantalum / 6X A75 cap'.  *(added by this lane; not in REFERENCE-TEARDOWN)*

- **part** — CANNOT DETERMINE
- **package** — blue-bodied moulded chip package with a printed polarity/pin-1 dot
- **size** — **MEASURED BUT NOT TRUSTED — unchanged by the scale correction** — long_mm 0.851 mm, short_mm 0.85 mm, long_px 90.5 px, short_px 90.4 px, aspect 1.001, short_side_genuine_px 17.6–23.3 px  
  Square to 0.1%, which for a two-terminal chip part is wrong-looking, and aspect is scale-free so re-deriving changed nothing about why. The b-r segmentation most likely found only the blue body between two metallised ends rather than the whole package. Its short side is 16.6-22.0 genuine px, above the 10 px floor, so the refusal is about the segmentation and not about resolution. Recorded as suspect, not promoted to a size.
  - **ruler** — 106.313 px/mm, registration-derived. Re-derived from 0.82 x 0.82 mm.
- **marking** — `6X A75`, read by L3, off IMG-BACK crop [720:870, 1400:1550] at 8x
  - *legibility* — two short lines, legible
- **locatable in a photograph** — YES — Apple FRONT side, mid-left, above the metal-lid part.
- **evidence class** — SILICON SEEN
- **confidence** — HIGH for the marking. CANNOT DETERMINE for the part, the value, and whether it is a capacitor at all — 'blue body' is a colour, not a technology.
- **what the marking establishes** — the two lines exist.
- **what it does NOT establish** — anything else.
- **what would settle it** — A marking table, or a measurement on a live unit.
- **Replica verdict** — CANNOT DETERMINE

### UNK-A — CANNOT DETERMINE  *(added by this lane; not in REFERENCE-TEARDOWN)*

- **part** — CANNOT DETERMINE
- **package** — large matte-black moulded rectangle, roughly 2:1 aspect, no marking of any kind, sitting over the mid-left cluster
- **size** — **CANNOT DETERMINE — ATTEMPTED, and refused by its own controls**
  - **what was tried** — Three criteria, in order. (1) Otsu on luminance, dark: the component merges with the dark board and fills the box — the clip control fires at every box tried. (2) Colour: M08 measured this package at B-R = +0.5 against a board median of +1, so the colour route that isolated the nRF is blind to it, and sampling here confirms it — the body is R44.3 G44.1 B44.0, neutral to 0.3 units. (3) Dark AND SMOOTH, built into b_pkgsize as --smooth-dark: the body's local sd is 7.1 against 36.9-59.1 for the board around it, a 5-8x separation, which is the only real discriminator this photograph offers.
  - **why the third attempt was refused too**
    - **the parameter sweep** — Three operator-chosen numbers (luminance ceiling, texture ceiling, window), so all three were swept: 27 settings, 22 unclipped. The LONG axis moves 90.4% (212.6 - 478.6 px) while the SHORT axis moves 11.3% (210.6 - 236.2 px). An extent that moves 90% with the settings is a measurement of the settings.
    - **AND THE POSITIVE CONTROL FAILS, which is the decisive one** — The same criteria run on U1 — a part that is certainly a rectangular package — return rectangularity 0.341 and a CLIPPED blob. So the reading 'UNK-A scores 0.574, therefore it is not a rectangular package' compares against a criterion that cannot recognise a rectangular package either. Without that control it would have been published, and it would have meant nothing. The negative control (bare board at 1750,1900,2150,2300) correctly found nothing.
    - **the control cannot be fixed here** — A fair positive control needs a DARK, SMOOTH, NEUTRAL package of known shape on this same photograph. The only dark packages on this face are the ones under question. Reported as un-runnable on this subject rather than tuned until it passed — E07 s19.
  - **what IS established, and it is thin** — Across every unclipped setting the component is at least 212.6 x 210.6 px = 2.00 x 1.98 mm with a filled area of at least 2.24 mm^2. That is a floor, not a size. Its long extent is somewhere between 2.0 and 4.5 mm and this photograph will not narrow it.
  - **does it close a line? NO** — The four parts nobody can point at are U3 (flash), U5 (amplifier), U7 (op-amp) and U8 (load switch). A dark object at least 2.0 x 2.0 mm whose long side is anywhere in 2.0-4.5 mm is consistent with several of them and excludes none. This measurement was the best remaining candidate for closing a line and it does not close one. It is recorded as a measured refusal rather than an unattempted gap, which is the only thing it improves.
  - **L3's caution stands, and is now supported by a picture** — O'Flynn describes cutting through 'the black plastic' to reach the SPI flash, so a matte black rectangle here may be a carrier or an adhesive and not a package. Five parameter settings were drawn back onto the photograph and looked at (the overlay is a scratch artefact, the observation is here): they agree closely on the lower-left, lower and right boundaries and diverge only at the upper left, and the outline they agree on is NOT a rectangle — it appears notched at the upper right where board with a visible white trace shows through. That is a READING OF A PICTURE, not a measurement, and it is written down as one. It cannot be promoted to a shape claim while the criterion that produced it fails its own positive control.
  - **what would settle it** — A photograph of this region at higher genuine resolution, or any photograph of this face taken with the part removed. Nothing in the public record here provides either.
  - **raw** — bom/measurements/UNK-A.json
- **marking** — `NONE VISIBLE`, read by L3, off IMG-BACK crop [380:800, 1250:1600] at 4x
  - *legibility* — no text at any magnification available
- **locatable in a photograph** — YES — Apple FRONT side, mid-left, the largest unmarked object outside the UWB can.
- **evidence class** — SILICON SEEN, IDENTITY UNKNOWN
- **confidence** — CANNOT DETERMINE
- **what the marking establishes** — nothing
- **what it does NOT establish** — everything
- **what would settle it** — Measuring it against the nRF52832 as an in-photograph ruler, then comparing to the published body sizes of the four unlocated parts (U3 flash, U5 amp, U7 op-amp, U8 load switch). That is this lane's next work item and is NOT escalated.
- **considered and rejected**
  - *the black plastic antenna carrier overhanging the board* (source: O'Flynn describes cutting through 'the black plastic' to reach the SPI flash) — Not rejected — held open. The object has the crisp straight edges and uniform matte finish of a moulded IC package, but O'Flynn's own text puts black plastic over this board, and confusing a carrier for a package would be exactly the kind of error this document exists to avoid.
- **Replica verdict** — CANNOT DETERMINE

### UNK-B — CANNOT DETERMINE. Position — between the UWB module and the coaxial connector J1 — is consistent with an RF part (switch, filter or balun) but position is not evidence of function.  *(added by this lane; not in REFERENCE-TEARDOWN)*

- **part** — CANNOT DETERMINE
- **package** — pale beige/ivory ceramic-looking square package with a single small dark square inset near one corner
- **size** — **NOT YET MEASURED**
- **marking** — `NONE VISIBLE`, read by L3, off IMG-BACK crop [1540:1950, 2600:2820] at 5x
  - *legibility* — no text
- **locatable in a photograph** — YES — Apple FRONT side, immediately left of J1.
- **evidence class** — SILICON SEEN, IDENTITY UNKNOWN
- **confidence** — CANNOT DETERMINE
- **what the marking establishes** — nothing
- **what it does NOT establish** — everything
- **what would settle it** — A higher-resolution photograph, or Catley's annotated board image read directly.
- **Replica verdict** — CANNOT DETERMINE

### R/C/L bulk — decoupling, RF matching networks, pull-ups

- **part** — CANNOT DETERMINE, individually and collectively
- **package** — two-terminal chip passives, several distinct sizes present on both sides
- **size** — **NOT YET MEASURED**  
  Package SIZE is determinable by ratio against the nRF52832 as an in-photograph ruler and is worth doing as a distribution (how many 0402, how many 0201) rather than part by part.
- **marking** — `NONE — chip passives of this size carry no marking`, read by L3, off IMG-BACK
  - *legibility* — n/a
- **locatable in a photograph** — YES, in bulk, both sides
- **evidence class** — SILICON SEEN
- **confidence** — CANNOT DETERMINE for every individual value. This is not a gap that any photograph can close: a 100 nF and a 1 uF 0402 are visually identical.
- **what the marking establishes** — n/a
- **what it does NOT establish** — n/a
- **what would settle it** — Nothing available here. Values come from designing the Replica's own power and RF networks to the same reference designs, not from copying Apple's.
- **considered and rejected**
  - *reporting an impression that a part 'looks like an 0402'* (source: the obvious shortcut) — An impression is not a size. Where sizes are reported they will be ratios against the nRF52832's published body size, with the ruler part named.
- **Replica verdict** — SUB — designed, not copied.

### ANT1 — BLE antenna, 2.4 GHz, inverted-F

- **part** — Apple's own structure
- **package** — printed onto the plastic carrier, per O'Flynn
- **size** — **CANNOT DETERMINE**
- **marking** — `n/a`
  - *legibility* — n/a
- **locatable in a photograph** — Apple's own arrow in FCC-6 labels 'Bluetooth Antenna' at the board rim.
- **evidence class** — SEEN (labelled by the manufacturer in a regulatory filing)
- **confidence** — HIGH that Apple labels a Bluetooth antenna at that rim position. CANNOT DETERMINE for the geometry.
- **what the marking establishes** — n/a
- **what it does NOT establish** — n/a
- **measured gain** — -3.2 dBi max, FCC test report E1V2 — a measured number from a filing, the only hard antenna number in the whole reference.
- **what would settle it** — For the geometry: a scaled photograph of the carrier's antenna face, which does not exist in this image set. DECISIONS.md D23 records this as a wall and no effort is spent chasing it.
- **open question** — O'Flynn, primary and verbatim: 'The plastic part includes the various antennas which are printed onto it - if you remove the PCB from the black plastic enclosure you will rip the antenna solder points.' That is a first-hand statement that the antennas are on the carrier, and it is stronger evidence than anything in the FCC photo captions. But Apple's arrows in FCC-6 point at the BOARD RIM. The orchestrator has flagged this: if the BLE and UWB antennas were on the board, the Replica's LDS gap would vanish. This lane's reading is that O'Flynn's text is decisive for the carrier and the FCC arrows are pointing at the antenna FEED region on the board, but that is a reading and not a measurement, and it is recorded as an open question, not resolved.
- **Replica verdict** — SUB — a PCB inverted-F or a chip antenna. The Apple structure is not reproducible and not worth chasing.

### ANT2 — NFC antenna, 13.56 MHz

- **part** — wound magnet wire coil (NOT a laser-structured trace)
- **package** — wound coil
- **size** — **BAND GEOMETRY MEASURED (M01 §3) AND IT STANDS. The supporting turn-count argument is WITHDRAWN — see evidence/E02-THE-COIL-CORRECTION.md.** — inner_diameter 9.38, outer_diameter 10.834, radial_band_width 0.727  
  Quote the RATIOS. The absolute millimetres inherit O'Flynn's '~26 mm', whose tilde is his and whose error is unbounded; the ratios carry only the 0.388 px fit residual.
  - **ratios_to_datum**
    - **inner** — 0.3608
    - **outer** — 0.4167
  - **superseded** — E02: the count is at least 9, not ~5, at about 111 um pitch (near AWG 38, not AWG 35), and the two reads were NOT independent — a solenoid and a flat spiral present the same radial band width from above, so they could not have disagreed. Turn count is now CANNOT DETERMINE, blocked on the coil's true centre.
- **marking** — `n/a`
  - *legibility* — n/a
- **locatable in a photograph** — YES — Apple BACK side, the annulus around the central magnet well.
- **evidence class** — SEEN AND MEASURED
- **confidence** — HIGH that the conductors are individually resolved, coplanar and equally lit at full resolution, which is the direct observation supporting wound wire. CANNOT DETERMINE for the turn count and the wire gauge. OPEN for whether this is the NFC antenna or the voice coil.
- **what the marking establishes** — n/a
- **what it does NOT establish** — The turn count to better than 'about five', the wire gauge to better than 'about AWG 35', the inductance, or the tuning network.
- **what would settle it** — For the electrical values: an LCR measurement on a live unit.
- **open question** — WHICH COIL IS THIS — and this lane raises it rather than settling it. FCC-5 carries Apple's own arrow reading 'NFC Antenna' and it points at this annulus, which supports the identification. But in IMG-FRONT at 3x, the coil's two fine magnet-wire leads run out past two red lacquer anchor dots and terminate on two round solder pads flanking the central battery-negative dome — and REFTEAR §2.4 states that the two pads at those positions, TP1 and TP38, are the VOICE COIL's two solder joints. Both cannot be true. Nothing in O'Flynn's blog text says what TP1 and TP38 are; the TP1/TP38-is-the-voice-coil claim is an assertion inside this repo, not a quote from him. The measurement in M01 stands either way — it is a measurement of a coil, and the numbers do not change. What is in question is which coil it measured, and therefore whether REFTEAR §2.3's amended ANT2 line describes the NFC antenna or the speaker. — UPDATE 2026-09-05: acted on and recorded in evidence/E02-THE-COIL-CORRECTION.md. The DC resistance argument now favours the NFC loop: at 9 turns of ~111 um wire on a ~10.1 mm mean diameter the conductor is ~286 mm and about 0.50 ohm, and a class-D amplifier into 4-8 ohm needs a hundred-odd turns and a far wider radial band than the 0.727 mm measured. That is an inference from a photograph resting on a lower-bound turn count, not a meter reading, so the question stays OPEN.
  - *what would settle it* — A photograph of the front dome's inner face (if the voice coil is glued there, this coil is not it); or the DC resistance of the pair at TP1/TP38 on a live unit — a five-turn 10 mm coil of AWG 35 is about 0.4 ohm and cannot be a voice coil for a 4-to-8 ohm class-D amplifier, whereas a real voice coil would read several ohms. This lane raises it to the orchestrator as a possible correction to M01 §3 and REFTEAR §2.3.
- **Replica verdict** — REPRODUCIBLE — winding needs no LDS tooling, subject to the open question above.

### ANT3 — UWB antenna, 6.5 / 8 GHz, one integral patch

- **part** — Apple's own structure
- **package** — printed onto the plastic carrier, per O'Flynn
- **size** — **CANNOT DETERMINE**
- **marking** — `n/a`
  - *legibility* — n/a
- **locatable in a photograph** — Apple's own arrow in FCC-6 labels 'UWB Antenna' at the board rim.
- **evidence class** — SEEN (manufacturer-labelled)
- **confidence** — HIGH for the label. CANNOT DETERMINE for the geometry.
- **what the marking establishes** — n/a
- **what it does NOT establish** — n/a
- **measured gain** — -1.6 dBi at 6.5 GHz, -0.6 dBi at 8 GHz, FCC test report E2V3.
- **what would settle it** — As ANT1. DECISIONS.md D23 records the carrier geometry as published nowhere.
- **Replica verdict** — GAP in practice — irrelevant to the Replica while U2 is unpopulated.

### SPK-COIL — voice coil — the moving half of the sounder

- **part** — wound magnet wire, glued to the plastic dome per iFixit and Catley
- **package** — wound coil
- **size** — **CANNOT DETERMINE**
- **marking** — `n/a`
  - *legibility* — n/a
- **locatable in a photograph** — CANNOT DETERMINE — see the ANT2 open question. Either this is the coil visible in IMG-FRONT, in which case ANT2 is not, or it is on the dome and no photograph here shows it.
- **evidence class** — SILICON CITED
- **confidence** — LOW for anything geometric. HIGH for the mechanism (coil against a fixed central magnet, housing as diaphragm) — iFixit had it in their hands.
- **what the marking establishes** — n/a
- **what it does NOT establish** — n/a
- **what would settle it** — A photograph of the dome's inner face.
- **Replica verdict** — SUB — the Replica needs a loud, hard-to-silence sounder (DULT). iFixit measured Tile's and SmartTag's piezos as no quieter, so the housing-as-diaphragm is an acoustic-quality choice, not a loudness one.

### SPK-MAGNET — fixed magnet at the centre of the annular board

- **part** — rare-earth magnet, grade and dimensions unpublished
- **package** — disc
- **size** — **NOT YET MEASURED**  
  FCC-5 and FCC-8 both show the central disc with two steel rulers in frame, so this IS measurable and is a work item, not a gap.
- **marking** — `n/a`
  - *legibility* — n/a
- **locatable in a photograph** — YES — the bright disc at the centre of FCC-5 and FCC-8.
- **evidence class** — SEEN
- **confidence** — MEDIUM
- **what the marking establishes** — n/a
- **what it does NOT establish** — n/a
- **what would settle it** — Measuring it against the rulers in FCC-5 / FCC-8.
- **Replica verdict** — SUB

### BATT — power source

- **part** — CR2032 3 V lithium coin cell; the FCC sample carried a Panasonic cell marked 'Made in Indonesia'
- **package** — CR2032, 20 mm x 3.2 mm by definition of the standard
- **size** — **DEFINED BY THE IEC CR2032 STANDARD** — diameter 20.0, height 3.2
- **marking** — `Panasonic CR2032 3V`, read by research lane A off FCC-3; not independently re-read by L3
  - *legibility* — legible in the filing
- **locatable in a photograph** — YES — FCC-3.
- **evidence class** — SEEN
- **confidence** — HIGH
- **what the marking establishes** — The cell fitted to the FCC sample. Not that every retail unit ships a Panasonic.
- **what it does NOT establish** — capacity of the retail cell.
- **what would settle it** — n/a
- **Replica verdict** — 1:1

### BATT-CONTACTS — connector-less battery interface

- **part** — 3 sprung metal contacts — 1 negative dome on the well floor, 2 positive tabs on the wall
- **package** — stamped spring contacts
- **size** — **NOT YET MEASURED**
- **marking** — `n/a`
  - *legibility* — n/a
- **locatable in a photograph** — YES — FCC-4 shows the well; IMG-TP shows the board-side pads labelled VCC1 / GND / VCC2.
- **evidence class** — SEEN
- **confidence** — HIGH for the arrangement.
- **what the marking establishes** — n/a
- **what it does NOT establish** — n/a
- **primary quote** — O'Flynn, OFLYNN-BLOG, verbatim: 'be sure to power BOTH positive battery tabs - they are NOT connected on the PCB even though you would expect that.' That is first-hand and it is the strongest available evidence for the dual-positive design. Catley's '~50 nA sense on the right rail' is a separate claim this lane has not corroborated.
- **what would settle it** — n/a
- **Replica verdict** — 1:1 — cheap to copy.

### PCB — the annular main logic board

- **part** — Apple MLB 820-01736-A (retail, O'Flynn's unit) / 920-08283-01 (FCC sample)
- **package** — annular, 2 populated sides, 0.3 mm thick per O'Flynn
- **size** — **CANNOT DETERMINE for the outer diameter — M01 §2, the gasket overlaps the edge in IMG-CROP26. A ruler-derived datum from FCC-6 is lane L1's work item, not this lane's.**
- **marking** — `820-01736-A; 2920 17; a lone 'C'; an Apple logo; a 2D data-matrix code; legend 'FB1P'; legend '4BU / LA'; legend '98C0051 / TPS746'`, read by L3, off IMG-TP and IMG-BACK
  - *legibility* — all legible; the data-matrix code is present but not decoded here
- **locatable in a photograph** — YES
- **evidence class** — SEEN
- **confidence** — HIGH for the strings.
- **what the marking establishes** — Apple's internal MLB part number and revision, and a wk29-2020 batch-17 date code.
- **what it does NOT establish** — Layer count or stackup — never published; REFTEAR §7 and RESEARCH-A both say so, and this lane adds nothing. The centre hole is a rounded square with a notch, not a circle (CATALOG.md, FCC-6), so any 'centre hole diameter' is the wrong shape of number.
- **what would settle it** — A cross-section of a scrapped board.
- **Replica verdict** — SUB — 0.3 mm is exotic; 0.6 mm is the fab-friendly answer.

---

## ruler

- **what** — The scale for every millimetre in this file's size_mm fields, on IMG-BACK (the component side).
- **px_per_mm** — 106.313 px/mm
- **sd_px_per_mm** — 0.44 px/mm
- **basis** — REGISTRATION, not a package. c_register.py fitted a homography from FCC photo 6 (which has two steel rulers in frame) onto O'Flynn's backside-fullres, NCC 0.6861 against a worst wrong-rotation null of 0.2029 (3.38x), held-out error 0.1029 mm over four spatial folds. The target scale is M02's 15.6850 px/mm measured AT THE BOARD, not the 15.8875 measured at the rule near the frame edge. Transferred to the source over 79 landmark samples: mean 106.313, min 105.423, max 107.161, sd 0.440, spread 0.41%. File: metrology/c_register-fit-boardscale.json (lane L1/L2).
- **WHAT ITS UNCERTAINTY REALLY IS** — NOT the 0.41% transfer spread. The transfer inherits the 2.07% disagreement between FCC photo 6's BOTTOM rule (15.8875 px/mm) and its RIGHT rule (15.5651 px/mm), which nothing in this project has resolved. Treat the scale as 106.3 px/mm +/- about 1%. It also assumes the FCC sample board 920-08283-01 and the retail board 820-01736-A that O'Flynn photographed are the same size; they are different units and that has never been checked.
- **RETRACTED — L3's 110.3 px/mm, and WHY it arose**
  - **what L3 did** — Measured U1 (nRF52832-CIAA WLCSP) with b_pkgsize at 355.1 x 326.6 px and divided by Nordic's published body 3.226 x 2.956 mm (PS v1.4, Table 132, p.541), giving 110.07 and 110.49 px/mm, used as 110.3.
  - **why it is not a scale** — It is one segmentation's outline convention divided by a datasheet number. THREE segmentations of that same package on that same photograph exist and they span 3.8%: b_pkgsize b-r/bright 355.1 x 326.6 px; L1's m_dark_packages whole-board run 349.1 x 322.1 px; L1's ROI-restricted control 342.1 x 312.6 px. Divided by the published body those imply 110.1, 108.2 and 106.1 px/mm. The datasheet route therefore cannot pin the scale better than about +/-2%, and 110.3 is simply the top of that range.
  - **what was checked and did NOT explain it** — Two hypotheses were tested and both failed, which is why they are recorded rather than asserted. (a) ROI choice: b_pkgsize --pad-sweep on L3's exact box at 0/20/40/60 px padding returns 355.1 x 326.6 px at every padding, IDENTICAL to the pixel — 0.00% spread. The box is not the cause. (b) Threshold placement: the 50% crossing between the package (b-r 172.5) and the board (b-r 127.0) sits at 149.8, only 0.9 units off Otsu's 148.9, and moves the extent by 0.5 px. A threshold sweep across the middle 60% of the contrast shows a PLATEAU of 351-359 px over 17 luma units, never approaching the 343.0 px the published body would need. The threshold is not the cause either. What remains is that the three methods disagree about which pixels are the package, and that disagreement is about 4%.
  - **the additive-vs-multiplicative test, and why it is NOT quoted as evidence** — The excess over the published body is +12.13 px long and +12.34 px short — agreeing to 1.7% in PIXELS and only to 10.4% in PERCENT, which looks like the signature of an additive outline bias rather than a multiplicative scale error. It is not quoted as evidence because the two axes differ in length by only 9%, so the additive and multiplicative models are nearly degenerate: the residuals are 0.1 px and 0.7 px respectively, and 0.7 px on a photograph this soft separates nothing. Naming a test that cannot really fail is E07's whole subject, and this one was caught before it was published, not after.
  - **routed, not edited** — M08's headline — 'two entirely unrelated routes agree to 0.23%' — rests on the SMALLEST of the three segmentations of U1, and M08 itself records a 2% spread between its own two. The agreement is real but weaker than the headline reads; on the whole-board run the same route gives 108.2 px/mm, 1.8% away, not 0.23%. metrology/ is L1/L7's folder and this is reported to the parent lane rather than edited here.
- **THE CORROBORATION THAT CAME FREE, and it can fail** — Two crystals never used to derive any scale land on STANDARD package codes at 106.313 px/mm. X1 measures 2.466 x 1.989 mm against the 2520 code's nominal 2.5 x 2.0 mm (-1.4% / -0.6%); at L3's 110.3 px/mm it would read 2.378 x 1.918 mm (-4.9% / -4.1%). X2 measures 1.687 x 1.086 mm against the 1610 code's nominal 1.6 x 1.0 mm (+5.4% / +8.6%), which at 110.3 would read 1.626 x 1.046 (+1.6% / +4.6%). SO THE TWO CRYSTALS DISAGREE WITH EACH OTHER about which scale they prefer, and neither is quoted as settling it. What they jointly support is that both crystals sit within a few percent of a nominal code at 106.313, which is the sanity check, not a calibration.
- **THE SYSTEMATIC THIS SCALE CANNOT REMOVE** — It is a single scalar for the whole board. The homography flattens the perspective before the scale is taken — the transferred scale varies only 105.42-107.16 px/mm across 79 samples spread over the board, a 0.41% spread — so the '14% anisotropy' warning L3 attached to the old ruler does NOT apply to this one. What remains is the 2.07% ruler disagreement above and the ~4% segmentation spread on any individual part.
- **PER-PART UNCERTAINTY, the number to actually use** — Every size below carries roughly +/-4% from segmentation method (measured on U1, the only part with a published body) on top of ~+/-1% of scale. A size quoted here to three decimals has two significant figures of truth. b_pkgsize's outline sits at the TOP of the segmentation range on the one part where truth is known — it read 3.5-3.9% over the published body — so read these as leaning high.

---

## resolution limit

- **rule** — STATED ONCE HERE so it is not rediscovered per line. A size claim on the component side is only possible for packages at or above 0402.
- **stored vs genuine** — IMG-BACK stores 106.313 px/mm. Its GENUINE resolution on the board is 20.7-27.4 px/mm, measured by power-spectrum rolloff (metrology/M06, M04). Stored/genuine is 3.9-5.1x: most of the file's pixels carry no information.
- **why the component side is the soft one** — The components are on the FRONT and the FRONT is imaged only by the softer source. O'Flynn's frontside-fullres (Apple's BACK — battery contacts and coil) resolves ~33-42 genuine px/mm. The better photograph is of the emptier face, and there is no choice to make.
- **what that means per package**
  - **0603 and larger** — 45+ genuine px long — sized
  - **0402 (1.0 x 0.5 mm)** — 20-27 px long, 10-14 px wide — sized, with the ~4% segmentation spread above
  - **0201 (0.6 x 0.3 mm)** — 12-16 px long, 6-8 px WIDE. A six-pixel width cannot support package-size discrimination. These parts are LOCATABLE and NOT SIZABLE, and the AirTag uses them.
  - **01005** — below the noise; not even locatable as a distinct object
- **consequence for this document** — Every measured line states short_side_genuine_px. A line whose short side is under 10 genuine px carries a POSITION and no size, however confident the number looks. Of the 95 bright features L1 located on this face, only 32 clear 10 genuine px; the median detection is 0.178 mm², which is 0201 nominal to 1%.
- **source** — metrology/M04, M06, M07; evidence/E07 section 8. Measured, not assumed: a resolution probe aimed at empty background returns 0.992 of Nyquist because noise is broadband, so every rolloff figure names its region and that region's luma sd.

---

## X1 vs X2 TEST

- **question** — Catley (via siliconpr0n) assigns 32 MHz to X1 (marked T320 / RBEV) and 32.768 kHz to X2 (marked A048L). Nobody in this project had ever tested it. The two frequencies live in different package families: a MHz AT-cut part sits in a squarer, larger package, a 32.768 kHz tuning-fork part in a long narrow one.
- **pre-registered outcomes** — If X1 comes back SQUARER AND LARGER than X2, Catley is supported. If X1 comes back LONGER AND NARROWER than X2, the two assignments swap and Catley is contradicted.
- **result** — X1 IS SQUARER AND LARGER. Catley's assignment is SUPPORTED.
- **the numbers, all three estimators, none chosen after the fact**
  - **min-area rectangle**
    - **X1_aspect** — 1.24
    - **X2_aspect** — 1.554
  - **median cross-section**
    - **X1_aspect** — 1.127
    - **X2_aspect** — 1.559
  - **25th percentile**
    - **X1_aspect** — 1.324
    - **X2_aspect** — 1.516
  - **size**
    - **X1_mm**
      - 2.466
      - 1.989
    - **X2_mm**
      - 1.687
      - 1.086
- **verdict taken on the WEAKEST estimator** — The p25 is the narrowest margin: X1 1.324 against X2 1.516, so X1 is 13% squarer even there. All three estimators agree in DIRECTION and the direction is the whole test. Reporting all three, and taking the verdict on the weakest, is E07 s17 — a verdict chosen after seeing which analysis wins is not a verdict.
- **the second, independent agreement** — Both parts land on standard package codes and the codes match the assignment: X1 on 2520 (2.5 x 2.0 mm) to 1.4%, which is the canonical MHz AT-cut package; X2 on 1610 (1.6 x 1.0 mm) to 5-9%, which is the canonical 32.768 kHz tuning-fork package. Nothing in the measurement knew about either code.
- **what it does NOT establish** — It does not read a frequency. It supports the ASSIGNMENT of two frequencies between two parts, given that the board carries a 32 MHz and a 32.768 kHz crystal — which itself rests on Catley plus the nRF52832's own requirements, not on anything measured here. The manufacturer, part number, load capacitance and tolerance of both crystals remain CANNOT DETERMINE. X1's and X2's confidence for the frequency assignment moves from MEDIUM-untested to MEDIUM-tested-and-supported, not to HIGH: the package family is consistent with the assignment, it does not uniquely determine it.
- **how it could still be wrong** — A 2520 package is not exclusively MHz and a 1610 is not exclusively kHz — both codes exist in both families, they are merely strongly skewed. A 32.768 kHz part in a 2520 can and a 32 MHz part in a 1610 can would reverse this and no photograph could tell. That is why the verdict is SUPPORTED and not CONFIRMED.

---

## Sources, and what each one is

- **`IMG-BACK`** — images/airtag/oflynn-backside-fullres.jpeg — 2916x3412 px, Colin O'Flynn, CC-BY-4.0. Apple's FRONT (component) side. Retail unit: silkscreen 820-01736-A, date code 2920 17.
- **`IMG-BACK-1K`** — images/airtag/oflynn-backside-1000px.jpeg — same view, 855x1000 px.
- **`IMG-FRONT`** — images/airtag/oflynn-frontside-fullres.jpeg — 2347x2344 px, Colin O'Flynn, CC-BY-4.0. Apple's BACK (battery-contact) side.
- **`IMG-TP`** — images/airtag/oflynn-frontside-tpnames.jpg — 1000x999 px, the same view annotated with TP1..TP38 and VCC1/GND/VCC2.
- **`IMG-CROP26`** — images/airtag/oflynn-frontside-26mm-cropped.jpg — 788x788 px, the scale datum of metrology/M01.
- **`FCC-3`** — images/airtag/fcc-BCGA2187-internal-photo-3.jpg — 'Cover Removed – Back': the Panasonic CR2032 in the battery well.
- **`FCC-4`** — images/airtag/fcc-BCGA2187-internal-photo-4.jpg — 'Battery Removed': the three sprung battery contacts.
- **`FCC-5`** — images/airtag/fcc-BCGA2187-internal-photo-5.jpg — 'Open back case with MLB'. Apple's own arrow labels NFC Antenna. Two steel rulers in frame. Watermarked 'Apple Proprietary and Confidential'; it is nonetheless a public FCC filing (doc 5130978) and the watermark must not be stripped.
- **`FCC-6`** — images/airtag/fcc-BCGA2187-internal-photo-6.jpg — 'MLB - Front', bare board, component side, TWO steel rulers in frame. Apple's own arrows label Bluetooth Antenna, Bluetooth Module, UWB Module, UWB Antenna. FCC sample board 920-08283-01, date code 3119 — NOT necessarily electrically identical to the retail board 820-01736-A that O'Flynn photographed.
- **`FCC-7`** — images/airtag/fcc-BCGA2187-internal-photo-7.jpg — 'MLB - Back', bare board, battery-contact side, two rulers.
- **`FCC-8`** — images/airtag/fcc-BCGA2187-internal-photo-8.jpg — 'Removed MLB', board with the central magnet assembly.
- **`OFLYNN-BLOG`** — research/fetched/A-oflynn-testpoints-and-glitch-repos.md — full text of colinoflynn.com/2021/05/apple-airtag-teardown-test-point-mapping/, fetched 2026-09-03.
- **`M01`** — electronics/halo_replica/metrology/M01-SCALE-AND-DATUM.md — this project's scale datum and the wound-coil measurement.
- **`REFTEAR`** — docs/REFERENCE-TEARDOWN.md — research lane A's reference BOM.
- **`RESEARCH-A`** — research/01-airtag-hardware.md — research lane A's full evidence file.
- **`E02`** — electronics/halo_replica/evidence/E02-THE-COIL-CORRECTION.md — the orchestrator's withdrawal of M01 §3's supporting argument, after this lane pointed out that a voice coil is a solenoid and the two 'independent' reads measured the same radial extent.
- **`NRF-PS`** — nRF52832 Product Specification v1.4, Nordic Semiconductor — Table 132 (WLCSP body 2.956 x 3.226 mm nominal, 0.4 mm pitch, p.541), Table 10 (nRF52832-CIAA = 64 kB RAM / 512 kB flash), Figure 165 (package marking layout N52832 / <PP><VV><H><P> / <YY><WW><LL>). Fetched via the distributor mirror at resources.ampheo.com/static/datasheets/nordic-semiconductor/nrf52832-ciaa-r7.pdf.
