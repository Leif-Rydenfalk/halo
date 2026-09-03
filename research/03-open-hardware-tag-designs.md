# 03 — Open-source hardware designs we could start from

Lane C. All research done **2026-09-03**; every URL below was fetched or returned by search
on that date, and last-commit dates were read from each repository's
`commits/<branch>.atom` feed on that date. Anything I could not confirm is marked
**unverified** rather than asserted.

**Scope, and how this complements lane B.** `research/02-findmy-protocol-and-openhaystack.md`
already carries a 23-row table of the Find My **software and firmware** projects with their
licences and last-push dates. This document deliberately does not repeat it. Lane C's subject
is the **boards**: which EDA source files actually exist in each repo, under which licence, in
what shape, and how separable the RF section is. Where a project has both halves (Everytag,
heystack-nrf5x, FakeTag) lane B is authoritative on the firmware half and this document only
notes the hardware.

## The headline

**There is no open-source AirTag.** After ~30 searches and ~40 page fetches, the field
contains exactly **one** project that is simultaneously (a) a purpose-built Apple Find My
tag, (b) published as editable EDA source rather than gerbers-only, and (c) under a real
open-hardware licence: **[PinPoint tracker](https://github.com/pinpoint-dev/tracker)** —
KiCad, TAPR OHL, Ebyte E73 module, buzzer, RGB LED, zero stars, last touched 2024-07-09.
Everything else splits into two piles: **excellent open coin-cell beacons that are not Find
My tags** (RuuviTag, rayBeacon, Squall, Sensirion SHTC3) and **excellent Find My firmware
with no hardware at all** (OpenHaystack, heystack-nrf5x, Everytag's firmware half, FakeTag,
Macless Haystack).

That gap is the opportunity. It also means halo cannot be a fork — it is a synthesis:
RuuviTag's KiCad round-board + NFC coil + accelerometer, PinPoint's Find My intent and
sounder, Everytag's firmware, rayBeacon's 25 mm two-layer round geometry, and a module/block
split that **nobody in the field has published**.

## Reading the "embeddable?" column

GOAL.md §2 asks whether the RF section can be dropped into someone else's outline. I score
each design as:

- **module** — RF is a bought castellated module (E73, MDBT42Q, MDBT50Q). Trivially
  re-hostable, pre-certified, costs a few dollars and a few mm. This is the pragmatic answer.
- **monolith** — bare chip + antenna welded into one board outline; reuse means re-laying out.
- **block** — published as a separable KiCad hierarchical sheet / design block / castellated
  sub-board you can instantiate. **No surveyed project scores this.**

## The table

| # | Name | URL | Maintainer | MCU / radio | Battery | Size / shape | EDA + formats present | Licence | Last activity | Missing vs AirTag | **Embeddable?** | Score |
|---|------|-----|-----------|-------------|---------|--------------|----------------------|---------|---------------|-------------------|-----------------|-------|
| 1 | **PinPoint tracker** | [github](https://github.com/pinpoint-dev/tracker) | pinpoint-dev (solo) | nRF52832 via **Ebyte E73-2G4M08S1E** module | coin cell holder on board (type not stated) | "<30x30x10 mm", map-pin outline | **KiCad** `.kicad_sch/.kicad_pcb/.kicad_pro` + `lib/` + `production/` | **TAPR OHL v1.0** | 2024-07-09 | UWB, NFC, accelerometer; buzzer is piezo not voice-coil; README promises a `cad/` dir that is not in the tree (unverified whether removed) | **module** — E73 carries the radio + antenna, so the RF is already separable and pre-certified | **4** |
| 2 | **RuuviTag** (Rev B1–B8) | [github](https://github.com/ruuvi/ruuvitag_hw) | Ruuvi Innovations Ltd / Lauri Jämsä | nRF52832 (bare chip) | CR2477, 1000 mAh | **45 mm round PCB**, 52 mm enclosure, 12.5 mm high | **KiCad** (v5-era: `.sch`, `.kicad_pcb`, `.pro`, `-cache.lib`) + schematic **PDF**; **no gerbers/BOM in-tree** | **CC BY-SA 4.0** (+ name restriction) | 2021-07-14 | Find My, UWB, speaker; too big at 45 mm | **monolith** — bare nRF52832 + its own antenna, one outline | **5** |
| 3 | **Everytag** (firmware + `hardware/`) | [github](https://github.com/vasimv/Everytag) | vasimv | nRF52833 on the board; firmware covers nRF52805/810/832/833, nRF54L15 | **LIR2016 Li-ion** (rechargeable) | 50x20x2 mm thin, or 30x20 mm | **KiCad** sources + **full gerber set** + drill + P&P + Altium 3D models | **GPL-3.0** | **2026-04-22** (most active) | Speaker, NFC, accelerometer, round shape; rectangular Qi-charging beacon | **monolith** — but the Qi coil + BQ25121A charger sub-circuit is a genuinely reusable idea | **4** |
| 4 | **rayBeacon** | [openhardware.io/view/742](https://www.openhardware.io/view/742/Raybeacon-nRF52-on-the-go-Development-Kit) | "Mishka" | nRF52833 / nRF52840 (bare chip) | CR2032 / CR2025 | **25 mm round, 2-layer** | Gerbers + drill + schematic PDF + PCB layout (native source not published) | **BSD** | ~2019 (rev6, "6 years ago") | Find My, UWB, speaker, accelerometer, on-board NFC coil (has a flex-antenna socket instead) | **monolith**, gerber-only | **3** |
| 5 | **Squall** | [github](https://github.com/helena-project/squall) | Lab11 / helena-project (Univ. Michigan) | nRF51822 | coin cell clip; USB variant rechargeable | **1 inch (25.4 mm) round** | Not stated in README (unverified — `hardware/` dirs exist, e.g. `hardware/squall-breakout/rev_b`) | **No LICENSE file found** ⇒ all rights reserved | 2017-09-30 | Everything: Find My, UWB, speaker, NFC, accelerometer; nRF51 is obsolete | **monolith**, but explicitly designed as a *base* with shield daughterboards (Rain, BLEES) — the closest anyone got to the halo "block" idea | **2** |
| 6 | **Sensirion SHTC3 BLE beacon** | [github](https://github.com/Sensirion/shtc3_ble_beacon) | Sensirion AG | nRF52 (nRF5 SDK 17 `ble_app_beacon`) | CR2032 | not stated | schematics + PCB layout + **gerbers** + STEP housing + firmware | **BSD-3-Clause** | 2020-11-30 | Find My, UWB, speaker, NFC, accelerometer; it is a temp/RH beacon | **monolith** | **3** |
| 7 | **Circuit-Digest DIY-AirTag** | [github](https://github.com/Circuit-Digest/DIY-AirTag) | Circuit Digest | **Raytac MDBT50Q-1MV2** (nRF52840) | CR2032 | not stated | `PCB/Airtag/` + **`Airtag Gerber.zip`** + PNG; native format unstated | **No LICENSE file (404)** ⇒ not safe to vendor | 2024-07-31 | Find My (it's a plain key-finder, not OpenHaystack), UWB, NFC; **does have** ADXL345 + active buzzer | **module** (MDBT50Q) | **2** |
| 8 | **Puck.js / EspruinoBoard** | [github](https://github.com/espruino/EspruinoBoard) | Gordon Williams / Pur3 Ltd | nRF52832 via **Raytac MDBT42Q** | CR2032, ~1 yr | round puck (~36 mm) | Eagle libraries + board schematics + Fritzing parts + case files | Custom Pur3 licence ("apart from Eagle Libraries…") — **verify before vendoring** | 2025-03-12 | Find My, UWB, speaker, NFC, accelerometer (has magnetometer + IR) | **module** — and the repo ships an **Eagle part library for the MDBT42Q**, i.e. a reusable RF footprint | **3** |
| 9 | **Holyiot 21014** | [Zephyr board doc](https://nrfconnectdocs.nordicsemi.com/ncs/3.3.0-preview2/zephyr/boards/holyiot/holyiot_21014/doc/index.html) · [zephyr src](https://github.com/zephyrproject-rtos/zephyr/blob/main/boards/holyiot/holyiot_21014/doc/index.rst) | Holyiot (vendor); board port upstream in Zephyr | nRF52810 | CR2032 | **30 mm dia x 8.4 mm, 6.5 g, IP66** | **No schematic published.** The open artefact is the Zephyr devicetree board definition (a reverse-drawn partial pin map) | Zephyr board files Apache-2.0; hardware closed | Zephyr tree is live | Find My out of the box, UWB, speaker, NFC; **has** LIS2DH12 accelerometer, RGB LED, button | **n/a** (closed) | **3** as a *hardware target*, 1 as a *design source* |
| 10 | **makerdiary nRF52832-MDK** | [github](https://github.com/makerdiary/nrf52832-mdk) | makerdiary | nRF52832 | USB / Li-po | USB-dongle | Schematic PDF + PCB PDF + STEP (V1.0/V1.1/V2.0) | **MIT** | 2020-09-07 | Coin cell, everything tag-specific | **monolith**, PDF-only | **2** |
| 11 | **Adafruit nRF52 Bluefruit Feather / nRF52840 Feather Express** | [github](https://github.com/adafruit/Adafruit-nRF52-Bluefruit-Feather-PCB) | Adafruit | nRF52832 / nRF52840 | Li-po | Feather | **EagleCAD** `.sch`/`.brd` | CC BY-SA (README); OSHWA cert [US000246](https://certification.oshwa.org/us000246.html) records HW "Other", SW MIT, docs CC BY-SA, certified 2020-04-03 | 2025-07-07 | README itself says the design is **"not intended for low power usage"** — disqualifying | **monolith** | **1** |
| 12 | **SparkFun Pro nRF52840 Mini** | [github](https://github.com/sparkfun/nRF52840_Breakout_MDBT50Q) | SparkFun | nRF52840 via **MDBT50Q** | Li-po | breakout | Eagle `.sch`/`.brd` + production panels | LICENSE.md in repo; SparkFun house licence is normally CC BY-SA 4.0 — **unverified** | 2020-06-17 | Coin cell, everything tag-specific | **module** | **2** |
| 13 | **Seeed XIAO nRF52840 (Sense)** | [github](https://github.com/Seeed-Studio/OSHW-XIAO-Series) | Seeed Studio | nRF52840 | Li-po via BQ25101 | 21 x 17.5 mm | vendor OSHW package (schematic/PCB) | **MIT** | 2026-07-16 | Coin cell, Find My, UWB, speaker, NFC; **has** LSM6DS3TR-C IMU + PDM mic on Sense | **monolith** (but small enough to solder down as a de-facto module) | **3** |
| 14 | **Nordic nRF5 Eagle reference designs** | [github](https://github.com/NordicPlayground/nrf5-eagle-reference-design) | Nordic Semiconductor ASA | nRF52832 QFAA / QFAA-DCDC / **QFAA-NFC** | n/a | reference layout | **Eagle** + PDF printouts | "Copyright (c) 2016 Nordic Semiconductor ASA, All rights reserved" + BSD-style clauses — **verify** | 2022-03-22 | It's a reference layout, not a product | **monolith reference**; Nordic warns only the **Altium** layouts are tested/verified | **4** as the RF starting point |
| 15 | **jacobrosenthal/nrf52-kicad** | [github](https://github.com/jacobrosenthal/nrf52-kicad) | jacobrosenthal | nRF52832 QFAA-DCDC | n/a | reference | **KiCad**, converted with altium2kicad and cleaned up | not stated (**unverified**) | not checked | reference only | **monolith** | **3** |
| 16 | **hlord2000/nordic-lib-kicad** | [github](https://github.com/hlord2000/nordic-lib-kicad) | hlord2000 | all modern Nordic parts | n/a | library | **KiCad** symbols + footprints + "reference design blocks" | not stated (**unverified**) | not checked | library only | closest thing to a **block** source in the Nordic world | **4** as a library |
| 17 | *Find My firmware projects (OpenHaystack, Macless-Haystack, heystack-nrf5x, acalatrava, FakeTag, Everytag fw, …)* | see `research/02-findmy-protocol-and-openhaystack.md` | — | nRF51/52/54, ESP32, and cheap non-Nordic silicon | — | — | **no hardware design files in any of them** | see lane B's table | see lane B's table | — | n/a | **lane B owns this** |
| 18 | **stacksmashing/airtag-hardware** | [github](https://github.com/stacksmashing/airtag-hardware) | stacksmashing (PCB work: David Hulton) | — | — | — | merged **PCB layer images** of the real AirTag | **none stated** — reference only, do not vendor | 2021-08-08 | it's a teardown artefact | n/a | **3** as reference |
| 19 | **Bitcraze Loco Positioning deck** *(UWB — lane H owns this)* | [schematic PDF](https://www.bitcraze.io/documentation/hardware/loco_deck/loco_deck_revd.pdf) | Bitcraze AB | STM32 + **DWM1000** | from host | Crazyflie deck | schematic states **KiCad 4.0.2**, published as PDF | **CC-BY 4.0** (on the schematic sheet) | rev D dated 2016-03-31 | it's a drone deck, ~10 cm accuracy | **module** (DWM1000) on a **deck** = physically separable | **3** *(defer to lane H)* |
| 20 | **Makerfabs ESP32-UWB / ESP32-UWB-DW3000** *(UWB — lane H)* | [DW3000](https://github.com/Makerfabs/Makerfabs-ESP32-UWB-DW3000) · [DW1000](https://github.com/Makerfabs/Makerfabs-ESP32-UWB) | Makerfabs | ESP32 + DW1000/DW3000 | Li-po | dev board | vendor hardware repo | not verified; the DW3000 Arduino lib is by **NConcepts**, not Makerfabs | active | **ESP32 cannot run from a coin cell** (see below) | **monolith** | **2** *(defer to lane H)* |
| 21 | **qqice/UWB-DW3000-NRF52**, **foldedtoad/dwm3000** *(UWB — lane H)* | [board](https://github.com/qqice/UWB-DW3000-NRF52) · [fw](https://github.com/foldedtoad/dwm3000) | qqice / foldedtoad | nRF52 + DW3000 | — | — | not inspected | not inspected | not inspected | — | — | *lane H* |

## Top 5 starting points, ranked, and what has to change

### 1. RuuviTag Rev B8 — the layout donor (score 5)
[github.com/ruuvi/ruuvitag_hw](https://github.com/ruuvi/ruuvitag_hw), CC BY-SA 4.0,
last commit 2021-07-14.

It is the only open design that already solves three of halo's five hard problems **in
KiCad, in copper, under a licence we can use**: a round board, a working NFC-A tag antenna
next to an nRF52832, and a routed accelerometer. Eight production revisions mean the
mistakes are already out of it — the B8 changelog alone ("make all the vias smaller",
"power sensors using GPIO pins", "100 nF caps to 1 µF") is a free lessons-learned document.

To reach AirTag parity: shrink 45 mm → ~31.9 mm (AirTag's puck diameter; RuuviTag's own
enclosure is 52 mm); swap CR2477 → CR2032, which costs ~2/3 of the energy budget and forces
the Find My duty cycle to be recomputed; delete BME280/DPS310/TMP117 and the second button;
**add** a sounder (RuuviTag has none) and the driver for it; add Find My/OpenHaystack
firmware (RuuviTag runs its own sensor firmware, though it is a documented OpenHaystack
target); and add DULT anti-stalking behaviour. Licence consequence: CC BY-SA 4.0 is
share-alike, so a derived halo board must also be CC BY-SA 4.0 — that conflicts with
GOAL.md's stated CERN-OHL preference. **Decide early whether to copy RuuviTag copper
(inheriting BY-SA) or only to read it and redraw** (clean-room, keeps CERN-OHL free). The
name restriction is explicit: no "Ruuvi" in a derived product's name.

### 2. PinPoint tracker — the intent donor (score 4)
[github.com/pinpoint-dev/tracker](https://github.com/pinpoint-dev/tracker), TAPR OHL,
last commit 2024-07-09.

The only project that already *is* what halo is: a KiCad Find My tag with a buzzer, a
battery holder, an SWD connector and a push button, all ticked off in its own README
checklist. TAPR OHL is a real reciprocal open-hardware licence and is compatible in spirit
with CERN-OHL-S. Its E73 module choice is exactly the "module" answer to GOAL.md §2.

Weaknesses to fix: one contributor, zero stars, quiet for two years, and the README
advertises a `cad/` directory that is not in the tree. No NFC, no accelerometer, no UWB, and
the "location pin" outline comes from a generic SVG Repo map-pin icon rather than a
mechanical study. Treat it as a **reference implementation to read and beat**, not a base to
fork: it proves the E73-plus-buzzer approach works and nothing more.

### 3. Everytag — the firmware base and the charging sub-circuit (score 4, firmware 5)
[github.com/vasimv/Everytag](https://github.com/vasimv/Everytag), GPL-3.0, last commit
**2026-04-22** — the most actively maintained thing in this survey.

Its firmware emulates **both** Apple Find My (up to 40 rotating keys, 10 min default) and
Google FMDN, on Zephyr/nRF Connect SDK, across nRF52805/810/832/833 and nRF54L15, and is
reconfigurable over BLE without reflashing. That is a straight-up better firmware starting
point than OpenHaystack's own nRF firmware. Its `hardware/` folder is complete KiCad plus a
full gerber/drill/P&P set — the only surveyed tag repo with production-ready outputs
committed.

But the board is a 50x20x2 mm rectangular Qi-charging beacon on a LIR2016: no speaker, no
NFC, no accelerometer, not round. Take the **firmware wholesale** and the **Qi receive-coil +
BQ25121A block** as an optional halo variant (rechargeable halo for sensors that live in
a fixture), and draw new copper for the puck. GPL-3.0 on the firmware is a licence decision
for research/06 — and note that lane B's table rates **acalatrava/openhaystack-firmware
(MIT, dormant since 2023-12-21)** as legally the best firmware base and **pix/heystack-nrf5x
(no licence declared, last push 2024-11-02)** as the closest match to an nRF52 halo. Lane B
is authoritative on that choice; lane C only observes that Everytag is the only one of the
three that also ships a board.

### 4. rayBeacon — the geometry proof (score 3)
[openhardware.io/view/742](https://www.openhardware.io/view/742/Raybeacon-nRF52-on-the-go-Development-Kit),
BSD, dormant since ~2019.

A **25 mm round, two-layer** nRF52833/40 board on a CR2032 with a published gerber+drill+PDF
set. Two-layer matters enormously for cost — it is the difference between a $2 and a $6 bare
board at JLCPCB quantities. It proves a full nRF52 + coin cell + PCB antenna + buttons + LEDs
fits inside a circle smaller than an AirTag on two layers. What it lacks is everything
tag-specific (no Find My, no sounder, no accelerometer, no on-board NFC coil — only a flex
socket) and it publishes no editable source. Use it as a **feasibility and stack-up
reference**, and to sanity-check any claim that we need four layers.

### 5. The Nordic reference chain — the RF starting point (score 4)
[NordicPlayground/nrf5-eagle-reference-design](https://github.com/NordicPlayground/nrf5-eagle-reference-design)
→ [jacobrosenthal/nrf52-kicad](https://github.com/jacobrosenthal/nrf52-kicad) →
[hlord2000/nordic-lib-kicad](https://github.com/hlord2000/nordic-lib-kicad).

If halo ships a **bare-chip** variant (cheapest BOM, best embeddability story), the matching
network and antenna must come from Nordic's own reference layout, including the `_nfc` variant
that already accounts for the NFC pins. Two caveats found in Nordic's own material: the
**Eagle** files are conversions and Nordic states only the **Altium** reference layouts are
tested and verified (so a KiCad-of-an-Eagle-of-an-Altium chain is three conversions deep —
re-verify against the Altium PDF); and Nordic's Altium/Gerber/PDF reference packs live behind
the product download pages, not in a repo. `hlord2000/nordic-lib-kicad` is the most useful
single artefact here because it already packages Nordic parts as KiCad symbols + footprints
**with reference-design blocks**, which is the shape halo's own deliverable should take.

## What nobody has done — and what halo must therefore invent

**The embeddable block does not exist.** Every project surveyed is a board. The two available
mechanisms are (a) KiCad 9's design blocks / hierarchical sheets — schematic reuse only, the
copper still has to be re-laid; the `edgy_boards` project is the only prior art aiming at
"what library code provides for software" — and (b) buying a castellated module, which is
what PinPoint (E73), Circuit-Digest (MDBT50Q), SparkFun (MDBT50Q), Puck.js (MDBT42Q) and
nrfmicro (E73) all do. Espruino ships an **Eagle part library for the MDBT42Q** and nrfmicro
ships `E73-2G4M08S1C-52840.kicad_mod`; those footprints are the entire existing state of the
art in "RF as a reusable part".

So halo's §2 deliverable should be **both**:
- a `halo-core` **KiCad hierarchical sheet + footprint set + documented antenna keep-out**
  for people who will do their own RF, built on the Nordic reference layout; and
- a **castellated solder-down halo-core module** (or a blessed E73/MDBT42Q configuration)
  for everyone else — pre-certified, no RF layout required, works in any host outline.

That module path is also the only realistic way a third party's arbitrary-shaped sensor board
gets a working 2.4 GHz antenna, because the one universal layout rule found across every
antenna source is that an IFA/MIFA must sit at a board edge with **no copper under or beside
it** — a constraint the host board's designer will violate the moment they choose their own
outline.

## AirTag parity: the four things every open design is missing

1. **Speaker.** Apple uses a voice coil glued to the shell, which *is* the diaphragm, driven
   through a MAX98357A. Not purchasable. Playing sound costs ~8 mA, ">3000x more power than
   being asleep" (Catley). Open substitutes: piezo (PinPoint, cents, quiet, needs a resonant
   cavity), active magnetic buzzer (Circuit-Digest), or amp + micro speaker as Apple does —
   the CDS-20144-L100 used in the DigiKey wallet-AirTag build is **$5.45 alone**, which by
   itself would exceed a sane halo BOM. This is the single hardest parity item and it is a
   mechanical/enclosure problem more than an electrical one.
2. **Accelerometer.** Solved and cheap: RuuviTag routes a LIS2DH12 (and publishes it under
   CC BY-SA), Holyiot 21014 uses the same part, Circuit-Digest uses an ADXL345. Needed for
   DULT motion-triggered behaviour, not optional.
3. **NFC.** nRF52832/840 have the NFC-A tag peripheral built in; the coil is the work.
   RuuviTag's KiCad NFC-A antenna is directly reusable, Nordic ships an `_nfc` reference
   variant, and `nideri/nfc_antenna_generator` generates coils parametrically. Apple's coil is
   LDS on plastic; ours must be PCB spiral, which competes for the same board area as the
   BLE antenna keep-out and the 20 mm cell.
4. **Round ~30 mm form factor.** rayBeacon proves 25 mm round on two layers with a CR2032.
   Holyiot 21014 proves 30 mm x 8.4 mm with an accelerometer in production. The real
   constraint is that a 20 mm cell in the middle of a 30 mm disc leaves a 5 mm annulus for the
   antenna keep-out, the NFC coil and every part — which is exactly why Apple went to LDS on
   the shell. Expect either four layers, or parts under the cell, or a slightly larger disc.
5. *(Not parity, but GOAL.md §3)* **UWB.** No open coin-cell UWB tag exists. The open UWB
   boards are host-powered dev boards (Bitcraze deck, Makerfabs ESP32). **Lane H owns this.**

**And a moving target:** Hackaday's 2026-02-02 AirTag 2 teardown reports Apple has moved to
an **nRF52840** with a UWB module, a Bosch accelerometer and an SPI EEPROM, with the speaker
in a ring surrounded by the UWB antenna. Parity is now nRF52840-class, not nRF52832.

## Why not ESP32
Hackaday's 2022 AirTag clone was an ESP32 "with no speaker and no serial number"; Make:'s DIY
AirTag offers the ESP32 path **only with a USB power bank**; and a CR2032 on an unconfigured
ESP32 "dies by lunchtime" (Hubble Network). A BLE tag draws 5–15 mA for a few ms per
advertisement, which is why nRF5x tags last years on the same cell. ESP32 Find My tags are
demos, not products. Detail in `research/fetched/C-uwb-and-embeddability.md`.

## Licence map (matters for what we can copy)

| Licence | Projects | Consequence for halo |
|---|---|---|
| CC BY-SA 4.0 | RuuviTag, Bitcraze deck (CC-BY 4.0) | Copying copper makes halo BY-SA, clashing with GOAL.md's CERN-OHL. Read-and-redraw to stay free. |
| TAPR OHL v1.0 | PinPoint | Reciprocal, CERN-OHL-S-compatible in spirit; safe to build on. |
| BSD / BSD-3 | rayBeacon, Sensirion SHTC3 | Permissive; safest to copy from. |
| MIT | makerdiary, Seeed XIAO, FakeTag | Permissive. |
| GPL-3.0 | Everytag (firmware + HW) | Fine for firmware; unusual for hardware — check the `hardware/LICENSE` scope before copying copper. |
| **None** | Circuit-Digest DIY-AirTag, Squall, heystack-nrf5x, stacksmashing/airtag-hardware | **All rights reserved by default. Do not vendor. Read only.** |
| Vendor / custom | Espruino (Pur3), Nordic reference, SparkFun (unverified) | Read the exact file before use. |

## Sources
Every URL in this document, with fetch dates, is appended to `research/sources.tsv` under
lane `C`. Extended notes and verbatim quotes are in:
`research/fetched/C-pinpoint-tracker.md`, `C-ruuvitag.md`, `C-everytag.md`,
`C-other-open-tag-boards.md`, `C-antennas-and-mechanical.md`,
`C-uwb-and-embeddability.md`.

Repositories worth vendoring are appended to `reference/CLONE-LIST.tsv`.
Images are in `images/designs/` with `images/designs/CATALOG.md`.
