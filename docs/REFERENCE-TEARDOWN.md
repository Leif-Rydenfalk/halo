# REFERENCE-TEARDOWN — the AirTag as the copy target

*Written 2026-09-03 by research lane A. This is the **reference BOM**: not what halo buys, but
what halo is copying. Every other BOM in this repo (`docs/BOM.md`, `spec/bom-candidates.json`,
lane E's substitution map) must map back to a row in §2 here.*

**Full evidence and sources:** `research/01-airtag-hardware.md`. Archived primary pages:
`research/fetched/A-*`. Photographs: `images/airtag/` + `images/airtag/CATALOG.md`. All sources
also in `research/sources.tsv`, lane tag `A`.

Target device: **Apple AirTag, 1st generation, model A2187, FCC ID BCGA2187** (2021). This is the
generation that is fully torn down, glitched, dumped and photographed. AirTag 2 (2026, nRF52840 +
Apple U2) is noted in §6.

Verdict key, used in every table:
- **1:1** — the exact part is a catalogue part anyone can buy. Copy it.
- **SUB** — the function is reproducible, the exact part is not ideal/available; lane E picks the substitute.
- **GAP** — cannot be reproduced. Written down, not glossed (GOAL.md's rule).
- **CANNOT DETERMINE** — nobody has published it. What would settle it is named.

---

## 1. The device we are copying

| | value | source |
|---|---|---|
| Envelope | Ø **31.9 mm × 8.0 mm**, **11 g**, IP67 | Wikipedia; Catley |
| Battery | user-replaceable **CR2032**, 3 V, ~225 mAh | FCC internal photo 3; Catley |
| Retail | **$29** | Apple |
| Est. manufacturing cost | **~USD 10** (excl. software/R&D) | [TechInsights](https://www.techinsights.com/blog/apple-airtag-teardown) |
| Custom silicon content | **exactly one part** (Apple U1) | Catley: *"Uses off the shelf components, apart from Apple's U1 chip for UWB"* |
| Sleep current | **2.3 µA** → *"maximum battery life of at least 11 years"* if never woken | Catley |
| Radios | BLE 2.4 GHz (+4.5 dBm, IFA −3.2 dBi) · NFC 13.56 MHz · UWB 6.5/8 GHz (patch, −1.6/−0.6 dBi) | FCC test reports E1V2 / E2V3 |

**The one-line finding that shapes the whole project:** the AirTag is 95 % catalogue parts around a
CR2032. Only the U1 is unobtainable. Everything else on this page is buyable today.

---

## 2. Reference BOM — every part inside an AirTag

**F** = front/top side (battery contacts, coil, NFC), **B** = back/bottom side (the ICs).
"Marking" = text actually read off the part in a photograph by lane A where noted.

### 2.1 Active silicon

| # | function | Apple's part | package / marking | verdict | note for halo |
|---|---|---|---|---|---|
| U1 | MCU + BLE 5 + **NFC tag peripheral** | Nordic **nRF52832-CIAA** | WLCSP-50, 90 nm; marking `N52832 CIAAE0 2102JK` (B) | **1:1** | The single most important copy decision: one chip is CPU **and** BLE **and** NFC. Stocked at LCSC. nRF52833/52840 are drop-in-ish upgrades |
| U2 | UWB transceiver (Precision Finding) | **Apple U1**, die `TMKA75`, TSMC 16 nm, in a **USI** SiP (20.58 mm², embedded xtal + Sony RF switch) | shield can (B) | **GAP** | Never sold to anyone. Not a sourcing problem — a *does-not-exist-for-us* problem. Lane H/E pick a third-party UWB (DW3xxx class) for **peer-to-peer** ranging; Apple-side Precision Finding stays a **known gap** |
| U3 | firmware storage (nRF firmware **+** U1 "Rose" firmware), **unencrypted** | GigaDevice **GD25LE32D** / **GD25LQ32C** 32 Mbit SPI NOR | WLCSP-10, 1.8 V | **1:1** | 4 MB is generous because it also holds U1 firmware. Without UWB, halo needs far less |
| U4 | 3-axis accelerometer (motion wake, anti-stalk trigger) | Bosch **BMA280** | metal-lid LGA (B) | **1:1 / SUB** | BMA280 is aging; any low-power 3-axis accel serves. DULT needs it (docs/ANTI-STALKING.md) |
| U5 | audio amplifier → voice coil | Maxim **MAX98357A** | WLCSP (B) | **1:1 / SUB** | Class-D I²S amp. A cheaper amp or direct PWM drive is viable |
| U6 | main DC-DC buck (3 V → 1.8 V) | TI **TPS62746** 300 mA | marking `98C0051 / TPS746` (B) | **1:1 / SUB** | |
| U7 | op-amp (speaker/analog path) | TI **TLV9001** | small (B) | **1:1 / SUB** | |
| U8 | load switch / OVP (gates U1 + flash) | onsemi **FPF2487** | small (B) | **1:1 / SUB** | Power-gating is *why* sleep is 2.3 µA. Copy the intent even if not the part |
| U9 | secondary LDO/regulator | marking `1A8` / `1950`; iFixit lists "likely onsemi DC-DC" + "likely TI DC-DC" | SOT (B) | **CANNOT DETERMINE** | Exact PN never published. A die-shot or a decapped board would settle it |

### 2.2 Passives, timing, storage

| # | function | part | marking | verdict |
|---|---|---|---|---|
| X1 | HF clock, 32 MHz (BLE) | crystal | `T320 / RBEV` (B) | **1:1** |
| X2 | LF clock, 32.768 kHz (RTC, low-power timing) | crystal | `A048L` (B) | **1:1** |
| C1–C5 | bulk hold-up — keeps the tag alive seconds after battery removal (enables the 5×-remove reset ritual) and buffers speaker transients | **5 × 100 µF** | `J107S`, around the rim (F) | **1:1** |
| — | decoupling, RF matching, schottky pairs (`K11`) | 0201/0402 R/L/C | both sides | **1:1** |

### 2.3 Antennas — all three on one part

All three are **laser-direct-structured (LDS) onto a single plastic carrier** and soldered to the
board edge (6 tear-off joints). The NFC coil has an extra return trace on the far side of the
plastic with a via at each end.

| # | band | Apple's implementation | measured gain (FCC) | verdict |
|---|---|---|---|---|
| ANT1 | BLE 2.4 GHz | LDS trace, **IFA** (inverted-F) | **−3.2 dBi** max | **SUB** — LDS needs tooling; a PCB IFA or chip antenna is the open-hardware answer (lane I) |
| ANT2 | NFC 13.56 MHz | LDS coil, behind the white cover | — | **SUB** — a normal PCB spiral coil works |
| ANT3 | UWB 6.5 / 8 GHz | LDS trace, **1 integral patch** | **−1.6 dBi @6.5 GHz, −0.6 dBi @8 GHz** | **GAP/SUB** — only if a UWB chip is fitted |

**Copy note:** LDS is the single most expensive process choice in the AirTag and the least
reproducible in open hardware. Replacing one LDS carrier with printed-on-PCB antennas is the
biggest cost lever halo has, and it is a *manufacturing* substitution, not a functional one.

### 2.4 The "speaker" — the cleverest part, and optional

| element | what it is | verdict |
|---|---|---|
| voice coil | copper coil **glued to the plastic dome**; two solder joints to the board (TP1, TP38) | **1:1** |
| magnet | fixed rare-earth magnet in the centre of the donut PCB | **1:1** |
| diaphragm | **the housing itself** — iFixit: *"the AirTag's body is essentially a speaker driver"* | **SUB** |

Measured **78–80 dB**; costs **~8 mA** while sounding (>3000× sleep). Drilling a keyring hole
through the shell changed loudness by ±1 dB — the whole dome radiates.

**Copy note:** iFixit found the piezos in Tile/SmartTag *"made just as much, if not more, noise."*
So the housing-as-diaphragm is an acoustic-quality choice, not a loudness one. halo should copy
the *function* (a loud, hard-to-silence sounder — DULT requires it) and is free to use a coin
speaker or magnetic buzzer. **Known anti-stalk defect to NOT copy:** the AirTag runs identically
with the coil disconnected, so the speaker can be silently disabled. halo should detect an open
coil (Catley's own suggested fix) — see `docs/ANTI-STALKING.md`.

### 2.5 Mechanical and connector-less interfaces

| element | detail | verdict |
|---|---|---|
| battery contacts | **3 sprung contacts**: 1 negative on the well floor, **2 positive** tabs on the wall. **Both** positives must see 3 V to boot; only the left powers the logic, the right is sensed at **~50 nA** | **1:1** (the dual-sense is a nicety, cheap to copy) |
| big pads under the terminals | **NOT connected** — the real contacts are the small pads under the tabs (O'Flynn) | note for anyone probing |
| battery door | stainless-steel **press-and-twist** cover — the child-safety mechanism | **1:1** (D3 in DECISIONS.md; Reese's Law) |
| housing join | front + back plastic on **3 clips + glue**; PCB is glued/soldered to the antenna tray | **SUB** — screws or snap-fit are friendlier for open hardware |
| connectors | **none anywhere** | **1:1** — copy this |

---

## 3. The PCB itself

| property | value | verdict |
|---|---|---|
| shape | **donut / annular** — central hole for magnet + voice coil | **SUB** (GOAL.md §2 wants an *embeddable block* in any outline) |
| outer diameter | **~26 mm** bare board (32 mm assembled puck) | **SUB** |
| thickness | **0.3 mm** — O'Flynn: *"it's 0.3mm PCB so I'm pretty sure I broke some solder joints getting it out"* | **SUB** — 0.3 mm is exotic; 0.6–0.8 mm is the JLCPCB-friendly answer |
| layer count | **CANNOT DETERMINE** — never published. Likely 4. stacksmashing hosts merged layer photos but states no count | a cross-section of a scrapped board would settle it |
| Apple board PN | `820-01736-A` (front silkscreen); `920-08283-01` on the NFC side | — |
| date coding | wk/yr + batch, e.g. `2920 17`; US `2920/3020/3120`, EU `5220`, Asia `1021` | — |
| populated sides | **2** — ICs on the back, battery contacts/coil/NFC on the front | **1:1** |

---

## 4. Function map — what a "perfect copy" actually means

The full version with interfaces is §4 of `research/01-airtag-hardware.md`. Condensed verdicts:

| AirTag function | verdict | why |
|---|---|---|
| Run firmware, be the CPU | **1:1** | nRF52832 is catalogue |
| BLE Find My broadcast | **1:1** | native nRF52832; exactly what OpenHaystack does (lane B) |
| NFC "found it" tag with the owner URL | **1:1** | nRF52832 has the NFC-A tag peripheral built in |
| Play the alert sound | **1:1 / SUB** | amp + coil, or any sounder |
| Motion wake / anti-stalk trigger | **1:1** | any 3-axis accel |
| Store firmware + keys | **1:1** | generic SPI NOR |
| Power management, 2.3 µA sleep | **1:1** | catalogue PMIC parts + aggressive gating |
| CR2032 interface, 5×-remove reset | **1:1** | contacts + 5×100 µF |
| Firmware update mechanism | **SUB** | UARP-over-L2CAP is reproducible; Apple's OTA feed is not |
| **UWB Precision Finding (Apple-side)** | **GAP** | no U1. Peer-to-peer UWB with a third-party chip is a *different* capability (lane H) |
| **Appearing in the stock Find My app** | **GAP** | needs a per-unit Apple **Token** burned at an MFi factory (lane D "Door 1"); D5 says clean-room, no MFi |

**Two gaps, both commercial/IP, neither an engineering failure.** Everything else copies.

---

## 5. What we know about the firmware (and why it does not block us)

- nRF runs Apple firmware on a Nordic **SoftDevice** (likely S112). The **U1 is a coprocessor** —
  its firmware ("Rose") lives in the shared SPI flash and is loaded by the nRF over the "Durian"
  L2CAP opcode set (`Rose Init`, `Rose Start Ranging`, …; full list in
  `research/fetched/A-seemoo-airtag-firmware-and-opcodes.md`).
- **SWD is on exposed test pads** (TP30 nRST / 35 SWCLK / 36 SWDIO / 31 SWO). APPROTECT is enabled
  but is defeated by the LimitedResults nRF52 voltage glitch on **TP28** (the nRF core rail), which
  *"cannot be patched without Silicon redesign."* The SPI flash is readable in place and unencrypted.
- **There is no secure boot** — modified firmware boots. This is how stacksmashing changed the
  Lost-Mode NFC URL in May 2021.

**Why this does not block halo:** we write our own firmware on our own nRF. This section is
evidence that the platform is fully open to us, and a warning about what *our* threat model should
be (an attacker can glitch our tags too — see `docs/ANTI-STALKING.md`).

---

## 6. AirTag 2 (2026), for completeness

nRF52832 → **nRF52840**; U1 → **Apple U2**; louder speaker nested inside the UWB antenna ring
(harder to remove, **still disableable**); same CR2032, same twist cover, 11.8 g, firmware 3.0.41.
Architecture unchanged in principle — an nRF52-based clone stays faithful to both generations.

---

## 7. Open questions this document cannot close

| question | what would settle it | who |
|---|---|---|
| PCB layer count and stackup | cross-section a scrapped AirTag board, or a lab report | G / a bench teardown |
| Exact PN of U9 (`1A8`/`1950`) | decap or a higher-res die shot | — |
| Whether the FCC-sample board (`920-08283-01`, date `3119`) differs electrically from production (`820-01736-A`) | compare a 2019 EVT unit to a retail unit | — |
| Exact bare-board diameter (~26 mm is inferred from Catley's figure and O'Flynn's crop) | measure a real board | G |
| Line-item BOM cost | Counterpoint's AirTag BoM report is paywalled | E |

Nothing above is guessed. Where a number is not in a source it says **CANNOT DETERMINE** and names
what would settle it.
