# halo concept portfolio

*twelve researched ways to close the last gap to the AirTag and get further ahead than Apple*

> concept docs with ideas and different approaches to close the gaps further and get even further ahead than apple themselves

halo is at functional parity with the AirTag on every row of SPEC.md section 2 except F9, Precision Finding, which needs Apple's own ultra-wideband silicon behind an NDA that cannot coexist with publishing the design. It is already ahead in five measured ways: both Apple's and Google's networks in one advertising event, an antenna simulated at +0.521 dBi against Apple's filed -3.2 dBi, peer-to-peer ranging between the owner's own devices, about a sixth of Apple's retail price, and every file open.

This portfolio is what comes after parity. Each concept is researched and costed, not brainstormed: what it is, why it beats the alternative, the evidence with sources and dates, the cost in money and current and size and complexity, what it would break in the design that exists today, a verdict, and the smallest experiment that would settle it.

Nothing here is a commitment. A concept that reaches PROVEN is a thing somebody has already made work, not a thing halo has shipped.

**4 concepts: 1 PROVEN · 3 PLAUSIBLE · 0 SPECULATIVE.**

## What the three verdicts mean here

| verdict | means |
|---|---|
| **PROVEN** | Somebody has already made this work and the artifact is readable — a paper with measurements, a repository whose source says so, a datasheet number. The remaining risk is integration, not physics. |
| **PLAUSIBLE** | Every component of the argument is sourced, but the combination has not been demonstrated in the shape halo needs. The arithmetic closes; the experiment has not been run. |
| **SPECULATIVE** | A reasoned idea whose load-bearing claim has no source I could reach. It is written down with what would settle it, and it must not be quoted as a finding. |

A concept with no source is SPECULATIVE and says what would settle it. That rule is `docs/TOOLS-THAT-LIE.md` applied to ideas rather than to tools: a portfolio that reads as all-green would be reporting completeness it had not earned.

## Where halo stands before any of this

| fact | number | source |
|---|---|---|
| Average cell current, Find My advertising baseline (2 s period, 1 ms TX at 3.7 mA, 2.4 uA sleep) | **4.2506 uA  =  12.75 uW at 3.0 V** | ce-spice rail_droop, out/release/board/sim/rail_droop/measurements.json, i_avg_uA, 2026-09-04 |
| Battery life on a 235 mAh CR2032 at that current, derated for pulsed draw and self-discharge | **64.5 months (5.4 years)** | same file, life_months_derated; derations cited to TI SWRA349 Fig 3 and Energizer 2032NA0618 |
| SoC currents that drive every power figure here | **TX 3.7 mA at 0 dBm, RX 2.1 mA, System-ON 192 kB retained 2.4 uA** | nRF54L10 datasheet 4503_018 v0.10 Table 86, transcribed research/fetched/E-nrf54l-datasheet-currents.md |
| Unit cost at 10 / 100 / 1 000 / 10 000 against Apple's $29 retail and ~$10 build | **$19.25 / $9.28 / $7.17 / $6.75** | DECISIONS.md D15; spec/bom-resolved.json cost.model.d15_baseline_usd_per_unit |
| Board, and what is on it | **D26.00 x 0.60 mm, 4 layer, 38 placed refs, 131 joints; part-routed at 49 vias, 255 track segments, 81 unconnected** | electronics/halo_rev_a/schematic.py; STATUS.md board measurement 2026-09-05 06:06 — DO NOT FABRICATE until unconnected reaches 0 |
| Peer ranging accuracy specified for v1 | **6-10 cm MAE, 16-20 cm P90, line of sight, static, <=5.5 m** | arXiv:2605.17094 Table I (eight CR2032 nRF54L15 devices); research/08 section 1; DECISIONS.md D12 |
| Energy per pairwise Channel Sounding range, 0 dBm, 37 channels | **~19 uC = ~57 uJ  [derived in research/08 section 9.3 from the paper's 79 uC/cycle for four peers]** | arXiv:2605.17094 section IV-C; research/08 section 9.3 |
| Antenna, study geometry (D30 x 1.0 mm round rim inverted-F) | **PASS: 2.4469 GHz, +0.521 dBi realized gain against Apple's filed -3.2 dBi** | ce-rf out/halo-round-rim-ifa/verdict.json, verdict PASS |
| Antenna, the board this pack actually ships (D26.00 x 0.60 mm) | **FAIL — 2.4927 GHz, solver_converged 0. The +0.521 dBi is NOT this geometry** | ce-rf out/halo-rev-a-2g4/verdict.json; spec/convergence.json refuses a value from a FAIL case |
| Firmware footprint with all three protocol layers resident | **13,164 bytes flash (1.27 %) and 704 bytes RAM (0.36 %) on nRF54L10** | SPEC.md section 2a; DECISIONS.md D18 — the DULT transport is NOT yet written and is the expensive part |
| Stack budget, closed | **31.874 x 31.874 x 7.980 mm assembly, 0.542 mm of dead air left under the cell** | DECISIONS.md D17; design.py stack budget check |
| Find My location quality, for comparison with anything local | **raw report mean error ~100 m walking; median 26 min from generation to upload; 4 reports per key; 7 day retention** | PETS 2021 Tables 5-7 and sections 6.3-6.4, quoted in research/02 sections 1.6 and 10.4 |

## The portfolio

| # | concept | verdict | value | effort | one line |
|---|---|---|---|---|---|
| C3 | [Sensor telemetry over the finding network, with no gateway of its own](C3-sensor-telemetry-over-the-finding-network.md) | **PROVEN** | 5 | 1 | The status byte is copied into the location report and encrypted to the owner's key, so a halo can report sensor state through a stranger's phone and Apple cannot read it. |
| C8 | [Form factors the embeddable block enables — and the one rule that decides each](C8-form-factors-the-block-enables.md) | **PLAUSIBLE** | 4 | 2 | A card, a sticker, a bolt-on asset tag and a solder-down module are four different products, and DULT's own applicability test — not the electronics — is what changes between them. |
| C11 | [The tag you can audit — open debug, reproducible firmware, and why it costs almost no secrecy](C11-the-tag-you-can-audit.md) | **PLAUSIBLE** | 3 | 1 | Nobody can prove what an AirTag does. A halo whose firmware hash an owner can verify against a published build is a procurement answer no commercial tracker can give — and with pre-generated keys it gives away almost nothing. |
| C12 | [The flight recorder — an on-tag event log, read at an NFC tap](C12-the-flight-recorder.md) | **PLAUSIBLE** | 4 | 2 | An AirTag remembers nothing. A halo has 1 MB of NVM and uses 13 kB of it, so it can keep the last several thousand motion and ranging events and hand them over when somebody taps it. |

## Ranked by value against effort

Value is what it is worth to the goal in `GOAL.md`; effort is what it costs to find out, not what it costs to ship. A cheap experiment on a big idea outranks an expensive certainty.

| rank | concept | value/effort | verdict | the first move |
|---|---|---|---|---|
| 1 | C3 Sensor telemetry over the finding network, with no gateway of its own | 5/1 = 5.00 | PROVEN | Write the 3-bit counter firmware and leave two tags out for 48 hours. Costs one evening and answers the density question too. |
| 2 | C11 The tag you can audit — open debug, reproducible firmware, and why it costs almost no secrecy | 3/1 = 3.00 | PLAUSIBLE | Build the firmware twice and diff. If it is reproducible, say so in the README with the hash; if it is not, that is a defect worth a line in VERIFICATION-DEBT.md. |
| 3 | C12 The flight recorder — an on-tag event log, read at an NFC tap | 4/2 = 2.00 | PLAUSIBLE | Read the NVM write current out of the datasheet and add one scenario to the rail_droop study. The answer is a number in the units this project already reports. |
| 4 | C8 Form factors the embeddable block enables — and the one rule that decides each | 4/2 = 2.00 | PLAUSIBLE | Drop the existing design block into a card outline and run one antenna solve on it. The block is already measured to transfer; what is unmeasured is whether the antenna is happier in a bigger space. |

## What was considered and left out

- **A GNSS receiver on the tag** — A first fix costs tens of milliamps for tens of seconds against a 4.2506 uA budget, and Find My already answers the question GNSS would answer — which city block — for free. The gap in this project is room scale, and GNSS does not close it.
- **A LoRaWAN or NB-IoT backhaul** — It adds a second radio, a second certification regime and a gateway, to buy uplink from places nobody walks past. C9 buys the same thing with hardware halo already has.
- **A USB port for recharging** — A port is a hole, and IP67 and Reese's Law both fight it. The measured life is 64.5 months; the problem this would solve is not the problem halo has.
- **BLE 5.1 angle of arrival** — The tag side is free but the anchor side needs a multi-element switched antenna array in every room. GOAL.md rules out per-room infrastructure. research/08 section 10.
- **Appearing inside Apple's own Find My application** — It needs a per-unit Apple Token burned into flash at the factory under MFi, and D5 refuses MFi on principle because its terms make the specification confidential and publishing an implementation would breach them. This is a commercial wall, not a technical one, and it is not going to move.
- **A display, an e-paper panel or an LED ring on the puck** — Every one of them puts a conductor inside the D37.31 mm antenna keep-out and spends stack height, to deliver something GOAL.md does not ask for. The measured cost of violating that keep-out is in C4.
- **A stealth or silent build target** — SPEC.md section 8 refuses it on principle, not by omission, and this portfolio does not reopen it.

---

Generated from `spec/concepts.json` by `tools/gen_concepts.py` on 2026-09-05, commit `cdaa1dc`. The HTML page is `out/concepts/INDEX.html`. Do not edit these files; edit the JSON.
