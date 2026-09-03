# SPEC — what halo must be

*The specification the design is judged against. Every row is either SETTLED
(with its source) or PENDING with the lane that will settle it. Nothing here is
an assumption: a PENDING row is a work item, never a guess left to harden into
a fact. Companion documents: GOAL.md (why), MISSION.md (definition of done),
DECISIONS.md (how each question was resolved), docs/ANTI-STALKING.md (the
safety behaviour, non-optional).*

Started 2026-09-03. Revision: draft 0.

## 1. Product definition

halo is a coin-cell Bluetooth tracker that reproduces the Apple AirTag
function for function from public information only, published openly, and
manufacturable cheaply. It ships in two variants (DECISIONS.md D1):

| | halo-core | halo-uwb |
|---|---|---|
| radios | 2.4 GHz BLE, Channel Sounding | same, plus an ultra-wideband transceiver in the reserved footprint |
| purpose | the open product: find your things through Apple's Find My network, **and** range to other halos at 6–20 cm line of sight | a high-precision stuffing option, if Channel Sounding proves insufficient in a real room |
| certification | pre-certified module, modular approval, RED self-declaration | owner-operated, not a sold consumer product |
| status | the shipping default | second board revision |

The circuit is published three ways so it can be embedded in any host board in
any outline (GOAL.md deliverable 2): a KiCad hierarchical design block, a
castellated solder-down module, and the Ø 32 mm puck as the first host.

## 2. Functional requirements, against the real AirTag

Each row: what the AirTag does, what halo must do, and where the number comes
from. The part that implements each is section 3.

| # | function | requirement | state |
|---|---|---|---|
| F1a | Google Find Hub advertising | advertise concurrently on Google's network: service `0xFEAA`, frame `0x40/0x41`, ~1024 s ephemeral-ID rotation | SETTLED lane B (public spec); DECISIONS.md D7 |
| F1 | Find My advertising | non-connectable advertisement, 37 bytes on air: address = `p[0]\|0b11000000 ‖ p[1..5]`, then `1E FF 4C 00 12 19 <status> p[6..27] p[0]>>6 <hint>`, where p is the X coordinate of the rolling NIST P-224 public key | SETTLED lane B (PETS 2021 Table 2, cross-checked against OpenHaystack source) |
| F2 | key rotation | rotate the advertised key on the DULT schedule; MAC address rotation likewise | SETTLED lane F: 15 min key, 24 h MAC |
| F3 | sound maker | audible alert, **≥60 Phon at 25 cm (ISO 532-1:2017)**, mandatory, four non-owner sound opcodes | requirement SETTLED lane F; mechanism OPEN, see DECISIONS.md D11 |
| F4 | separated-state behaviour | near-owner → separated after >30 min; random 8–24 h alert timeout with 6 h back-off | SETTLED lane F |
| F5 | identifier retrieval | serial readable over NFC or BLE, behind a physical button, 5-minute window; printed unique serial on the housing | SETTLED lane F |
| F6 | owner information page | obfuscated owner-info page, ≥25-day retention | SETTLED lane F |
| F7 | motion detection | wake and change advertising behaviour on movement | SETTLED lane A: AirTag samples every 10 s at rest and 0.5 s once moving; DULT additionally requires ±10° accuracy |
| F8 | NFC tap | phone tap reads the tag and opens the owner page | SETTLED lane A: the Nordic SoC's own NFC-A peripheral emulates a read-only Type-4 tag holding the owner URL; only the coil and two tuning capacitors are external |
| F9 | precision finding | AirTag does this with Apple's U1 | **known gap** — not reproducible without MFi (DECISIONS.md D1, D5) |
| F10 | peer ranging | range to other halos with Bluetooth Channel Sounding, 6–20 cm line of sight, 30 s update, deterministically scheduled, reporting raw ranges with quality metadata and an orientation vector | SETTLED lane H; DECISIONS.md D12 |
| F11 | battery life | about a year on a CR2032 | model PASSES in ce-spice: fresh-cell droop 68 mV under a transmit pulse against a 400 mV limit, five scenarios fresh to end of life, all asserts held |
| F12 | battery replacement | user-replaceable CR2032 behind a compliant door | SETTLED lane F: tool or two independent simultaneous movements (16 CFR 1263) |

## 2a. Budget floors (from lane B)

A Find My stack alone measures **116.7 KB flash / 21.5 KB RAM** (Goodix FMNA
figures, lane D). DULT adds a connectable advertisement set and a GATT service;
Google Find Hub adds a second beacon. The SoC is chosen with headroom over
those three together, not over the first (DECISIONS.md D8).

## 3. Component map — one row per function

From lane A's function map (research/01-airtag-hardware.md §4), which read the
part markings off Colin O'Flynn's full-resolution board photographs and Apple's
own regulatory filing. The halo column is lane E's substitution work; rows
marked PENDING lane E are awaiting its sourced pick.

| function | AirTag part (identified) | halo part | note |
|---|---|---|---|
| CPU, Bluetooth radio **and NFC tag in one** | Nordic **nRF52832-CIAA**, WLCSP-50, marking `N52832 CIAAE0 2102JK` | **nRF54L10**, falling back to L05 or up to L15 on memory (D12) — the family keeps the NFC-A tag peripheral and adds Channel Sounding | the NFC tag is the SoC's own peripheral on pins P0.09/P0.10 — **no separate NFC chip exists in an AirTag**, which deletes a line most clone BOMs carry |
| UWB ranging | Apple **U1**, die `TMKA75`, TSMC 16 nm, in a USI system-in-package with its own processor running "Rose" firmware side-loaded by the Nordic part | **not reproducible** — never sold. halo-uwb uses a sourceable transceiver for peer ranging only (D1) | the only true hard wall in the whole design |
| firmware and key storage | GigaDevice **GD25LE32/LQ32**, 32 Mbit SPI NOR, WLCSP-10, 1.8 V | PENDING lane E — generic SPI NOR | holds both the Nordic firmware and the U1's firmware, unencrypted |
| motion detection | Bosch **BMA280** | PENDING lane E | sampled every 10 s at rest, 0.5 s once moving |
| sound | Maxim **MAX98357A** class-D amplifier driving a copper voice coil glued to the shell, against a fixed central magnet, with a **TI TLV9001** op-amp in the analogue path | **bare Murata 7BB-20-3 piezo bender, Ø20.0 × 0.22 mm**, bonded to the shell and driven anti-phase from two SoC pins (D11) | about 8 mA while sounding, over three thousand times the sleep current |
| power | TI **TPS62746** buck to a 1.8 V rail, onsemi **FPF2487** load switch gating the UWB and flash, a small LDO, and **five 100 µF** bulk capacitors marked `J107S` | PENDING lane E | the bulk capacitance is what keeps the tag alive for seconds after the cell is pulled, which is how the five-removals reset works |
| timing | 32 MHz crystal marked `T320/RBEV`, 32.768 kHz crystal marked `A048L` | PENDING lane E | |
| antennas | three laser-direct-structured traces on the plastic carrier: Bluetooth inverted-F at **−3.2 dBi**, an NFC coil, a UWB patch at **−1.6 dBi at 6.5 GHz** | PENDING ce-rf | gains are from Apple's own filed test reports, not estimates |
| battery | CR2032 on three sprung contacts, two positive rails both sensed before boot | PENDING lane E | |

**The bottom line of the map:** every function is reproducible from catalogue
parts except precision finding, which needs Apple's chip, and appearing in
Apple's own Find My application, which needs a per-unit token Apple burns into
the flash at the factory. Both walls are commercial, not technical.

## 4. Physical envelope

From Apple's own dimensioned accessory drawing (lane G found it published free
at developer.apple.com, outside the login-walled Accessory Design Guidelines)
and from teardown measurements. Apple forbids redistributing that sheet, so the
numbers are transcribed here and the redistributable geometry in
`reference/models/` is a CC BY 4.0 drawing that reproduces every callout.

| feature | value | note |
|---|---|---|
| maximum outer diameter | **31.87 mm** | occurs at z = 4.34 mm, derived from the drawing's profile |
| overall height | **7.98 mm** | |
| stepped diameters | 28.94 / 27.90 / 27.84 / 25.55 / 23.11 mm | 0.05 mm chamfer |
| speaker keep-out | **Ø25.75 mm**, "do not obstruct" | Apple's own callout |
| antenna keep-out | **Ø37.31 mm**, no metal above or below | larger than the tag itself |
| steel cover | approximately a spherical cap of radius 92 mm | not a battery terminal — all three contacts are on the carrier |
| mass | 11 g first generation, 11.8 g second | otherwise dimensionally identical |
| environment | IP67, −20 to +60 °C | |

**The stack budget is the binding constraint.** A CR2032 is 3.2 mm and the
disassembled internal module measures 3.3 mm, so 6.5 of the 7.98 mm are spent
before the cover, the clearances and the shell wall. About 1.5 mm remains.

Two consequences follow directly, and both are now design rules:

- **No coin-cell holder fits.** The lowest-profile surface-mount retainer still
  stands 2 mm above the board. Sprung fingers on the carrier, clamped by the
  door, is the only scheme that fits — which is what Apple does.
- **No housed buzzer fits.** The obvious catalogue part reaches exactly the
  required loudness at three volts but is 3.5 mm tall.

Lane C's warning still holds on the copper side: a 20 mm cell inside a 30 mm
board leaves about a 5 mm annulus for the Bluetooth antenna keep-out and the
NFC coil together. The electromagnetic solver decides whether they share it,
the cell moves off-centre, or the puck grows.

The embedded block variant is not bound by this envelope. Only the puck is.

## 5. Electrical requirements

| # | requirement | source |
|---|---|---|
| E1 | operate from a CR2032 across its full discharge curve, including the rising internal resistance at end of life | ce-spice model, lane T2 |
| E2 | survive the radio transmit current pulse without the rail dropping below the SoC minimum at end of life | ce-spice, asserted |
| E3 | sounder drive that reaches F3's loudness inside an 8 mm puck | lane G (mechanism) + ce-spice (drive current) |
| E4 | 2.4 GHz antenna matched on the real board outline, with the battery's copper in place | ce-rf, lane T3 |
| E5 | NFC coil tuned to 13.56 MHz for the chosen tag IC's input capacitance | ce-rf |
| E6 | per-layer current and voltage drop within IPC-2221B limits | ce-board-sim |

## 6. Manufacturing requirements

| # | requirement | source |
|---|---|---|
| M1 | 4-layer board, DRC-clean against JLCPCB's published capabilities | ce-fab dfm, lane T6 |
| M2 | every part in stock at LCSC with a named alternate | ce-fab bom, lane T6 |
| M3 | assembly files (BOM + pick-and-place) accepted by JLCPCB without manual correction | ce-fab jlc |
| M4 | panelized for volume | ce-fab panel |
| M5 | cost per unit at 10 / 100 / 1 000 / 10 000, compared to Apple's $29 retail | lane E |

## 7. Compliance requirements

The 30-item constraint checklist in research/06-legal-ip-certification-safety.md
is normative. The headline constraints: pre-certified radio module for modular
approval; no Bluetooth word mark (DECISIONS.md D2); Reese's Law battery door
(D3); DULT behaviour non-optional (docs/ANTI-STALKING.md); clean-room only,
no MFi (D5); licence split (D4).

## 8. Out of scope

Apple Precision Finding (F9), the "Works with Apple Find My" badge, and any
stealth or silent build target. The last is refused on principle, not omitted.
