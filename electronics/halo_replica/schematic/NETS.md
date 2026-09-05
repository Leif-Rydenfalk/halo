# NETS.md — every net on the halo Replica schematic, and what it rests on

**GENERATED FILE.** Written by `schematic/schematic.py`, from the same
`N()` calls that build the netlist. Do not edit it by hand; edit the
schematic and rebuild, or the two will disagree and the netlist wins.

## The one thing to read first

**Nobody in this project has traced Apple's copper.** Not one net below
was read off a board. The parts come from `bom/bom.json` — photographs
and package markings — and the *connections* are reconstructed from what
each part is for. The `basis` column is not decoration; it is the whole
epistemic content of this document.

| basis | meaning |
|---|---|
| `MEASURED` | read off the hardware by a named source in this repo |
| `INFERRED` | required by the part's own datasheet family once the part is accepted. Wrong only if the part identification is wrong |
| `CHOSEN` | this sheet picked it. Apple's assignment is unknown and a different one would be equally consistent with every photograph. **Never cite one of these as a finding about Apple.** |

Counts: **7 MEASURED**, **21 INFERRED**, **23 CHOSEN**.  **7 of 51 nets are MEASURED**, and they are the only ones: `GND`, `SWDCLK`, `SWDIO`, `SWO`, `VBAT_RAW`, `VBAT_SNS_P2`, `nRESET` — the three battery contacts and the four SWD pads O'Flynn published. Everything else on this board is reconstruction.

## The nets

| net | basis | driven by | feeds | why it is drawn this way |
|---|---|---|---|---|
| `ACC_INT1` (2 pins) | **CHOSEN** | U4 INT1 | U1.10 (P0.08) | Motion wake is a real requirement - DULT anti-stalking needs it (docs/ANTI-STALKING.md) - so an interrupt line exists. Which pin is this sheet's. |
| `ACC_SCL` (3 pins) | **CHOSEN** | U1.8 (P0.06) | U4 SCL/SPC | I2C is CHOSEN over SPI: it costs two pins instead of four and lets the sensor answer while the flash is deselected. Nothing in the record says which bus Apple used. |
| `ACC_SDA` (3 pins) | **CHOSEN** | U1.9 (P0.07) and U4 SDA/SDI | both | Same. R5 pulls it up. |
| `AMP_GAIN` (2 pins) | **CHOSEN** | R8 to GND | U5 GAIN_SLOT | A gain strap has to go somewhere. Value missing. |
| `AMP_nSD` (2 pins) | **CHOSEN** | U1.23 (P0.20) | U5 nSD_MODE | Shutdown control. A tag that sleeps at 2.3 uA does not leave a class-D amplifier enabled, so a shutdown line is an argument; the pin is a choice. |
| `ANT_FEED` (3 pins) | **INFERRED** | L3 | C9 shunt, ANT1 | The feed point of the printed inverted-F. |
| `ANT_SOC` (3 pins) | **INFERRED** | U1.30 (ANT) | C8 shunt, L3 series | The radio comes out of the ANT pin. Everything after it is topology with no measured values. |
| `DCC` (2 pins) | **INFERRED** | U1.47, the SoC's own switching node | L2 | See L2's note. This is the least-supported component on the sheet and it is drawn because omitting it would silently assert LDO mode. |
| `DEC1` (3 pins) | **INFERRED** | U1 internal regulator, pin 1 | its decoupling capacitor and TP28 | The DEC pins are the on-die regulator's decoupling nodes. That they need capacitors is the part's own requirement; the values are CANNOT DETERMINE. |
| `DEC2` (2 pins) | **INFERRED** | U1 internal regulator, pin 32 | its decoupling capacitor | The DEC pins are the on-die regulator's decoupling nodes. That they need capacitors is the part's own requirement; the values are CANNOT DETERMINE. |
| `DEC3` (2 pins) | **INFERRED** | U1 internal regulator, pin 33 | its decoupling capacitor | The DEC pins are the on-die regulator's decoupling nodes. That they need capacitors is the part's own requirement; the values are CANNOT DETERMINE. |
| `DEC4` (3 pins) | **INFERRED** | U1 internal regulator, pin 46 | its decoupling capacitor and L2 from DCC | The DEC pins are the on-die regulator's decoupling nodes. That they need capacitors is the part's own requirement; the values are CANNOT DETERMINE. |
| `EN_BUCK` (2 pins) | **CHOSEN** | VBAT through R7 | U6.EN | Nothing in the record says how the buck is enabled. Tied always-on here because a tag with no rail cannot enable anything. |
| `EN_PERIPH` (2 pins) | **CHOSEN** | U1.P0.15 (pin 18) | U8.EN | WHICH GPIO is entirely this sheet's choice - Apple's assignment is unknown and every nRF52832 GPIO could serve. THAT there is a gate under firmware control is the part with an argument behind it: 2.3 uA sleep with a 4 MB NOR on the same rail is not otherwise reachable. |
| `FLASH_nCS` (2 pins) | **CHOSEN** | U1.14 (P0.11) | U3 nCS | Separate chip selects for the flash and the UWB module is what makes one bus serve two devices. Pin choice is this sheet's. |
| `GND` (41 pins) | **MEASURED** | BT1.3, the negative dome on the well floor | every ground pin on this sheet | The negative contact is a direct observation. |
| `I2S_BCLK` (2 pins) | **CHOSEN** | U1.19 (P0.16) | U5 BCLK | A class-D amplifier of this family takes I2S. THAT the MCU drives it digitally follows from the part; WHICH PINS is this sheet's choice. |
| `I2S_DIN` (2 pins) | **CHOSEN** | U1.22 (P0.19) | U5 DIN | Same. |
| `I2S_LRCLK` (2 pins) | **CHOSEN** | U1.20 (P0.17) | U5 LRCLK | Same. |
| `NFC1` (2 pins) | **INFERRED** | U1.11 (NFC1/P0.09) | C6 | The NFC-A tag peripheral is the SoC's own, on pins P0.09/P0.10. There is NO separate NFC chip in an AirTag - that deletes a line most clone BOMs carry. |
| `NFC2` (2 pins) | **INFERRED** | U1.12 (NFC2/P0.10) | C7 | Same. |
| `NFC_COIL_A` (2 pins) | **INFERRED** | C6 | ANT2 pin 1 | Series tuning into the coil. See ANT2's open conflict about what that annulus actually is. |
| `NFC_COIL_B` (2 pins) | **INFERRED** | C7 | ANT2 pin 2 | Same. |
| `SPI_MISO` (3 pins) | **CHOSEN** | U3 SO/IO1 (and U2, DNP) | U1.17 (P0.14) | Same. |
| `SPI_MOSI` (3 pins) | **CHOSEN** | U1.16 (P0.13) | U3 SI/IO0; U2 SPI_MOSI (DNP) | Same. |
| `SPI_SCK` (3 pins) | **CHOSEN** | U1.15 (P0.12) | U3 SCLK; U2 SPI_SCK (DNP) | The bus exists - the flash holds BOTH the nRF firmware and the U1's 'Rose' firmware, so the MCU must be able to read it. WHICH GPIO is this sheet's choice; on nRF52832 any SPIM instance routes to any pin. |
| `SPK_DIV` (3 pins) | **CHOSEN** | R9/R10 divider on SPK_P | U7 non-inverting input | Entirely this sheet's reconstruction of U7's role. |
| `SPK_N` (2 pins) | **INFERRED** | U5 OUTN | LS1 pin 2 | Same. |
| `SPK_P` (3 pins) | **INFERRED** | U5 OUTP | LS1 pin 1; R9 (sense divider) | A class-D bridge drives the coil differentially. Inferred from the part family. |
| `SPK_SENSE` (3 pins) | **CHOSEN** | U7 output (unity buffer) | U1.40 (P0.28/AIN4) | Same. Wired as a follower - output to inverting input - so the drawing is at least self-consistent. |
| `SWDCLK` (2 pins) | **MEASURED** | U1 pin 25 | TP35 (exposed test pad) | O'Flynn's TP35 = SWCLK. |
| `SWDIO` (2 pins) | **MEASURED** | U1 pin 26 | TP36 (exposed test pad) | O'Flynn's TP36 = SWDIO. |
| `SWO` (2 pins) | **MEASURED** | U1 pin 21 | TP31 (exposed test pad) | O'Flynn's TP31 = SWO, P0.18 on this die. |
| `SW_BUCK` (2 pins) | **INFERRED** | U6.SW | L1 | A buck with an external wirewound inductor switches into it. Which inductor is the buck's is bom.json's 'almost certainly, given its position' - position, again, not a trace. |
| `U9_OUT_DESTINATION_UNKNOWN` (1 pins) | **CHOSEN** | U9.OUT? | NOTHING ON THIS SHEET | A one-terminal net, deliberately. The public record contains no statement about what U9 drives. What would settle it: a die-shot, a decapped board, or continuity on a live unit. |
| `UWB_IRQ` (2 pins) | **CHOSEN** | U2 IRQ (DNP) | U1.28 (P0.23) | Same. |
| `UWB_RF` (3 pins) | **CHOSEN** | U2 RF (DNP) | ANT3; J1 centre | THE WEAKEST NET ON THIS SHEET AND IT IS LABELLED SO. bom.json J1: 'its position beside the UWB module is consistent with a UWB conducted-test port, but THE NET IT LANDS ON IS NOT ESTABLISHED'. Worse: UNK-B sits between U2 and J1 and is 'consistent with an RF switch, filter or balun'. If UNK-B is a switch then J1 and ANT3 are NOT one net and this net is wrong in a way this sheet cannot detect. |
| `UWB_nCS` (2 pins) | **CHOSEN** | U1.27 (P0.22) | U2 SPI_nCS (DNP) | See SPI_SCK. Every UWB control line here is CHOSEN and lands on a part that is not populated. |
| `UWB_nRESET` (2 pins) | **CHOSEN** | U1.29 (P0.24) | U2 nRESET (DNP) | Same. |
| `V1V8` (16 pins) | **INFERRED** | U6.VOUT through L1 | U1 (nRF52832) VDD x3; U4 accelerometer; U7 op-amp V+; U8.VIN; C10-C13 | 1.8 V because the flash Apple fitted is a 1.65-2.0 V part (O'Flynn read GD25LQ32C off the live chip over SPI with a J-Flash) and the teardown names the buck 3 V -> 1.8 V. The nRF52832's own range is 1.7-3.6 V, so 1.8 V is legal for it too. |
| `V1V8_SW` (5 pins) | **CHOSEN** | U8.VOUT | U3 flash VCC/nWP/nHOLD; U2 UWB VDD (DNP) | The gated branch. See EN_PERIPH for what is chosen and what is argued. |
| `VBAT` (11 pins) | **CHOSEN** | D3 cathode | C1-C5 bulk; U6.VIN (buck); U9.IN; U5.VDD (amplifier) | The rail behind D24's diode. That the bulk sits BEHIND the diode rather than in front of it is this sheet's choice and it is the choice that makes the diode work: hold-up capacitance in front of a blocking diode holds up the cell, not the load. |
| `VBAT_RAW` (3 pins) | **MEASURED** | BT1.1, the positive POWER finger | D3 anode; R1 (sense divider for AIN0) | Three sprung contacts with two positives is a direct observation (REFERENCE-TEARDOWN 2.5, iFixit had the tag in their hands). WHICH finger carries the current is O'Flynn's reading, not this lane's. |
| `VBAT_SNS_1` (3 pins) | **INFERRED** | R1/R2 divider on VBAT_RAW | U1.4 (P0.02/AIN0) | The FIRST positive is sensed. Both positives being sensed is the measured fact; the divider and the ADC pin are this sheet's shape for it. |
| `VBAT_SNS_2` (3 pins) | **INFERRED** | R3/R4 divider on VBAT_SNS_P2 | U1.5 (P0.03/AIN1) | The SECOND positive is sensed, and THIS IS THE POINT OF THE WHOLE BLOCK. Pull the cell and both dividers collapse in well under a millisecond while C1-C5 hold VBAT up for seconds - which is exactly the window the five-removals factory reset counts in. |
| `VBAT_SNS_P2` (2 pins) | **MEASURED** | BT1.2, the positive SENSE finger | R3 (divider to AIN1) | REFERENCE-TEARDOWN 2.5: 'Both positives must see 3 V to boot; only the left powers the logic, the right is sensed at ~50 nA.' A ~50 nA sense current is a very large divider, which is why R3/R4 are megohms and why their exact values are CANNOT DETERMINE. |
| `XC1` (3 pins) | **INFERRED** | U1.34 (XC1) | X1 pin 1, C18 | The HFXO goes on the HFXO pins. Inferred from the part, not traced. |
| `XC2` (3 pins) | **INFERRED** | U1.35 (XC2) | X1 pin 2, C19 | Same. |
| `XL1` (3 pins) | **INFERRED** | U1.2 (P0.00/XL1) | X2 pin 1, C20 | The LFXO goes on the LFXO pins. On nRF52832 these are P0.00/P0.01, which is why the two lowest GPIO are unavailable for anything else. |
| `XL2` (3 pins) | **INFERRED** | U1.3 (P0.01/XL2) | X2 pin 2, C21 | Same. |
| `nRESET` (2 pins) | **MEASURED** | U1 pin 24 | TP30 (exposed test pad) | O'Flynn's TP30 = nRST. On nRF52832 that is P0.21/nRESET. |

## Consistency with the netlist itself

Every net in the netlist is described above.

Every net described above is in the netlist.

## What was discarded, and why

- iFixit's 'GD25LE32D' for the flash - DISCARDED for O'Flynn's GD25LQ32C, which came from a Segger J-Flash SPI interrogation of the LIVE CHIP. A JEDEC ID read out of silicon outranks a visual identification, every time.
- iFixit's 'U8 gates U1 + flash' (U1 = the MCU) - DISCARDED for U8 gating the flash and the UWB module only. A load switch whose enable comes from the MCU it powers can never be turned on. iFixit's line is single-source and bom.json grades U8 LOW / SILICON CITED.
- D1/D2 as 'schottky pairs' (RESEARCH-A, from the K11 marking) - DISCARDED and the parts left OFF the sheet. bom.json: CANNOT DETERMINE for the part AND the function.
- CT1 as a tantalum capacitor (RESEARCH-A, 'a blue tantalum / 6X A75 cap') - DISCARDED and left off. 'Blue body' is a colour, not a technology, and bom.json cannot establish that it is a capacitor at all.
- UNK-A and UNK-B - left off. Seen, unmarked, unidentified. UNK-B's position between U2 and J1 is 'consistent with' an RF switch and position is not evidence of function.
- TP1/TP38 as the voice coil's joints (REFERENCE-TEARDOWN 2.4) - DISCARDED as unresolved, not as wrong: Apple's own FCC arrow labels that annulus the NFC antenna. Both cannot be true, so neither is drawn.
- The E02 turn-count corroboration for ANT2 - already withdrawn by its own author on 2026-09-05, because a solenoid and a flat spiral present the same radial band width from above, so the 'two agreeing measurements' were one measurement twice. Only the >=9-turn lower bound and the direct observation of resolved coplanar conductors survive.
- Filling any capacitor or resistor value with a plausible number - refused throughout. A 100 nF and a 1 uF 0402 are visually identical, so every value here is CANNOT DETERMINE and stays that way.

## CANNOT DETERMINE, carried openly

- APPLE'S ACTUAL NETLIST. Nobody has traced the copper. This whole sheet is a reconstruction from function and the basis field on every net says which kind.
- Every GPIO assignment on U1 except the four SWD pads. nRF52832 routes most peripherals by PSEL, so the assignments are free and therefore unverified against anything Apple did.
- Every passive value. See DISCARDED.
- Whether the nRF52832's internal DC/DC is enabled at all. If it is not, L2 does not exist.
- The DEC2/DEC3 arrangement - no copy of the nRF52832 reference circuit is in this repository, so only the topology is drawn.
- U4's part, U4's bus (I2C vs SPI), and which of the two metal-lid parts it even is.
- U9's part number AND U9's function AND what its output feeds.
- U7's role. Drawn as a unity buffer from a divider on SPK_P; could equally be a current-sense amp, a filter or a bias buffer.
- Whether J1 and ANT3 are one net. UNK-B sits between them and may be a switch.
- Which annulus TP1/TP38 belong to - NFC coil or voice coil. Two sources contradict and one of them is Apple.
- The crystals' frequencies (Catley's assignment, untested), their load capacitances, their part numbers and their case sizes.
- The five bulk capacitors' technology and their actual capacitance - '100 uF' is MEDIUM and the marking J107S is what is HIGH.
- The forward drop D3 costs, because the diode has not been chosen; D24 requires both a Schottky and an ideal-diode controller to be priced.

## Symbol substitutions

| ref | what the AirTag has | what this sheet draws | why |
|---|---|---|---|
| U1 | nRF52832-CIAA, WLCSP-50 (marking read: N52832 CIAAE0 2102JK) | `MCU_Nordic:nRF52832-QFxx` | the SAME DIE in QFN-48. No CIAA ball map is sourced anywhere in this repository, and inventing 50 ball designators is what D9 forbids. The netlist is right by signal; the pin numbers are QFAA's |
| U2 | Apple U1 UWB SiP (die TMKA75, USI package) | `local:APPLE_U1_SIP_PLACEHOLDER` | no pinout has EVER been published for this module, and the part is not sold. Pin numbers are this sheet's own and are not a land pattern |
| U3 | GD25LQ32C, WLCSP-10 (ten pads, centre pads absent) | `Memory_Flash:GD25QxxxEY` | KiCad ships no WLCSP-10 NOR symbol. The WSON-8 symbol carries the same eight signals under different numbers |
| U4 | the accelerometer, part unidentified, metal-lid LGA | `local:ACCEL_3AXIS_GENERIC` | the part is CANNOT DETERMINE, so a named symbol would assert an identification this project could not make. The pin set is the intersection BMA280/LIS2DH/LIS2DW12/SC7A20 all share |
| U5 | MAX98357A/B, WLCSP | `Audio:MAX98357A` | KiCad's symbol is the TQFP-16 pinout. Signals travel; pin numbers do not. The suffix itself is disputed between sources |
| U6 | TPS62746-class buck, package CANNOT DETERMINE | `local:BUCK_TPS62746_CLASS` | the evidence is a board LEGEND ('98C0051 / TPS746'), not a package marking. A named symbol would over-claim |
| U8 | FPF2487-class load switch | `local:LOADSWITCH_FPF2487_CLASS` | single-source (iFixit), LOW confidence, uncorroborated by any photograph here |
| U9 | the part marked 1A8 / 1950 | `local:UNKNOWN_REGULATOR_1A8_1950` | CANNOT DETERMINE, including whether 'regulator' is its function. Every pin name on that symbol ends in a question mark for that reason |
| X1/X2 | two seam-sealed ceramic crystals, sizes unmeasured | `Device:Crystal + Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm` | the markings T320/RBEV and A048L were read; the manufacturers, part numbers, load capacitances and CASE SIZES were not |
| BT1 | three sprung metal battery contacts | `local:BATT_CONTACTS_3` | a connector-less battery interface has no catalogue land pattern, and the two positive fingers must be two separate nets in copper |
| LS1 | a voice coil glued to the housing dome | `Device:Speaker` | there is no speaker. There is a coil against a fixed magnet and the HOUSING IS THE DIAPHRAGM |
| ANT1/ANT2/ANT3 | structures printed or wound on the plastic carrier | `Device:Antenna / Device:Antenna_Loop` | not bought parts and not PCB copper - the symbols are terminals so the networks have somewhere to end |

