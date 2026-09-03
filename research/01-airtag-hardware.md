# 01 — The Apple AirTag hardware: a function-for-function reference for halo

**Research lane A.** Topic: the Apple AirTag hardware itself — every public teardown,
reverse-engineering result, chip identification and PCB detail, assembled into the master
reference for building a "perfect copy of the internal AirTag stuff" (Leif, GOAL.md).

All fetches **2026-09-03** unless noted. Raw page text is archived under `research/fetched/A-*`.
Public teardown/X-ray/FCC images are in `images/airtag/` with `images/airtag/CATALOG.md`.
Every source is also in `research/sources.tsv` (lane tag `A`).

Confidence tags used in tables:
- **[primary]** — I read the primary artefact myself (the RE page, the FCC PDF, the chip marking in a photo, the repo).
- **[teardown]** — asserted by a reputable teardown (iFixit / TechInsights / O'Flynn / Catley) that physically had the part; I did not independently re-read the die.
- **[secondary]** — a credible third party asserts it; primary not seen.
- **[unverified]** — plausible, not confirmed. Never build a decision on it.

Scope note: this file is about **first-generation AirTag (model A2187, `AirTag1,1`)** unless a
section is explicitly about **AirTag 2 (2026)**. The clone target is the 2021 A2187 — it is the
one that is fully torn down, glitched, dumped and documented. AirTag 2 is covered at the end.

> **Cross-lane:** the Find My radio protocol and the exact BLE advertisement byte layout are in
> `research/02-findmy-protocol-and-openhaystack.md` (lane B). Commercial clones, the MFi/Token
> moat and five more FCC exhibits are in `research/04-commercial-tags-and-clones.md` (lane D).
> Substitute-part selection is lane E's job — this file names the genuine part and only points at
> the nearest sourceable equivalent; it does not evaluate substitutes in depth.

---

## 0. The one-paragraph answer

The AirTag is a ~31.9 mm coin, essentially a CR2032 with a radio wrapped around it. **One**
component is not off-the-shelf: Apple's **U1** ultra-wideband transceiver (die marking `TMKA75`,
in a USI module). **Everything else is a catalogue part**: a Nordic **nRF52832** (WLCSP) runs the
whole show — it is the CPU, the BLE 5 radio *and* the NFC tag — plus a **GigaDevice GD25LE32/LQ32
32 Mbit SPI NOR flash**, a **Bosch BMA280** accelerometer, a **Maxim MAX98357A** class-D audio amp,
a **TI TPS62746** buck converter, a **TI TLV9001** op-amp, an **onsemi FPF2487** load switch, two
crystals (32 MHz + 32.768 kHz), five 100 µF bulk caps, and a **3-antenna LDS carrier** (BLE 2.4 GHz,
NFC 13.56 MHz, UWB 6.5/8 GHz) laser-etched onto the plastic frame and soldered to the board edge.
The "speaker" is not a speaker: a **voice coil glued to the plastic dome** moves against a fixed
central **magnet**, so the whole housing is the diaphragm. The nRF52's debug port (SWD) is on
accessible test pads; its flash read-protection (APPROTECT) is enabled but defeatable by a
well-known **voltage glitch on one nRF power pin**, which is how the firmware was dumped, modified,
and how the Lost-Mode NFC URL was changed. Estimated manufacturing cost **~USD 10**. **A clone can
reproduce ~95% of this 1:1; the U1 (and therefore Precision Finding) cannot be sourced — that is
the single hard wall.**

---

## 1. Physical specification

| Property | Value | Source | Conf. |
|---|---|---|---|
| Diameter | **31.9 mm** (1.26 in) | [Wikipedia AirTag](https://en.wikipedia.org/wiki/AirTag) | [secondary] |
| Height / thickness | **8.0 mm** (0.31 in) | [Wikipedia](https://en.wikipedia.org/wiki/AirTag); Catley "Stock 32 mm × 8.0 mm" ([adamcatley](https://adamcatley.com/AirTag.html)) | [secondary]/[primary] |
| Weight | **11 g** (0.39 oz) | [Wikipedia](https://en.wikipedia.org/wiki/AirTag) | [secondary] |
| Water/dust rating | **IP67** (30 min immersion, up to 1 m) | [Wikipedia](https://en.wikipedia.org/wiki/AirTag) | [secondary] |
| Model number | **A2187** | [FCC BCGA2187](https://fccid.io/BCGA2187); iFixit | [primary] |
| FCC ID | **BCGA2187** (grantee BCG, product A2187) | [fccid.io](https://fccid.io/BCGA2187) | [primary] |
| Battery | user-replaceable **CR2032** 3 V Li coin cell (test unit: Panasonic, "Made in Indonesia") | [FCC internal photo 3](images/airtag/fcc-BCGA2187-internal-photo-3.jpg); Catley (Panasonic 225 mAh/3 V) | [primary] |
| Housing | white polycarbonate dome (front) + **stainless-steel** battery cover (back), twist-lock | iFixit; FCC photos | [teardown] |
| Enclosure joining | front + back plastic held by **3 plastic clips + glue**; battery cover is a separate steel twist-off child-safety cover | [iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks) | [teardown] |
| "Disassembled" min. envelope (Catley, coil re-attached to a new diaphragm) | **26 mm dia × 3.3 mm** | [adamcatley](https://adamcatley.com/AirTag.html) | [primary] |

> iFixit, verbatim: *"About the size of a half-dollar coin, it's not much larger than the battery
> that powers it."* and *"the AirTag's body is essentially a speaker driver."*
> ([iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks))

The X-ray (Creative Electron, via iFixit) shows the density is dominated by *"a hefty central
speaker magnet and its steel battery cover — both fairly opaque to X-rays"*
([iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks)).

---

## 2. The PCB itself

What is physically known about the board (this is the part Leif asked to nail down):

| PCB property | Value | Source | Conf. |
|---|---|---|---|
| Shape | **donut / annular ring** — round board with a large central hole for the magnet + voice coil | iFixit; O'Flynn; FCC MLB photos | [primary] |
| Outer diameter (bare board, carrier removed) | **~26 mm** (Catley's "disassembled" diameter; O'Flynn's `frontside-26mm-cropped` frames the bare board to ~26 mm) | [adamcatley](https://adamcatley.com/AirTag.html); [airtag-re](https://github.com/colinoflynn/airtag-re) | [primary]/[unverified exact] |
| Thickness | **0.3 mm** — *"it's 0.3mm PCB so I'm pretty sure I broke some solder joints getting it out"* | [O'Flynn blog](https://colinoflynn.com/2021/05/apple-airtag-teardown-test-point-mapping/) | [primary] |
| Layer count | **not published.** A 0.3 mm two-sided assembly with routed nets on both faces; likely 4-layer (unconfirmed). stacksmashing hosts *"merged PCB pictures of all the layers"* ([airtag-hardware](https://github.com/stacksmashing/airtag-hardware)) but the count is not stated in text. | — | [unverified] |
| Apple board part number (silkscreen) | **`820-01736-A`** (front/top silkscreen) — Apple's internal MLB part + rev `A` | Catley, visible in [`oflynn-frontside-tpnames.jpg`](images/airtag/oflynn-frontside-tpnames.jpg) | [primary] |
| Second board marking | **`920-08283-01`** on the NFC-antenna side (readable in FCC internal photo 5) | [FCC internal photo 5](images/airtag/fcc-BCGA2187-internal-photo-5.jpg) | [primary] |
| Manufacturing data code | bottom-right numbers = week/year + batch, e.g. **"2920 17"** = wk 29 of 2020, batch 17. US: `2920/3020/3120`; EU: `5220`; Asia: `1021` | [adamcatley](https://adamcatley.com/AirTag.html) | [primary] |
| Board is soldered to the plastic tray | Yes — *"Removing the PCB is likely to cause damage due to the thin PCB and being soldered to the plastic tray."* The **antenna solder joints tear** if you lift the board off the carrier. | Catley; O'Flynn | [primary] |
| Component sides | **2 populated sides.** "Top/front" = battery contacts, voice-coil pads, magnet well, NFC coil area, most passives. "Bottom/back" = the ICs (nRF52832, U1, flash, accel, amp, buck, opamp) + crystals + the 100 µF caps. | O'Flynn (`frontside`/`backside` images); iFixit | [primary] |

### 2.1 Component-side layout (read off the photos)

**Bottom / "back" side** (`images/airtag/oflynn-backside-fullres.jpeg`, read directly by lane A):
going around the ring — the **nRF52832** (marking `N52832 CIAAE0 2102JK`) sits next to the **32 MHz
crystal** (marked `T320 / RBEV`) and the **32.768 kHz** can (marked `A048L`); the **TPS62746 buck**
is nearby (marking `98C0051 / TPS746`); a small metal-lid sensor (the **BMA280 accelerometer**) and a
blue tantalum/`6X A75` cap sit mid-ring; a `1A8` / `1950`-marked small SOT device (an LDO/regulator)
and diode pairs are clustered around the buck; the **large shield can at the bottom is the U1 UWB
module**. The five **100 µF electrolytic caps** ring the edge.

**Top / "front" side** (`images/airtag/oflynn-frontside-tpnames.jpg`): the **VCC1 / GND / VCC2**
battery pads sit at the top; **TP1 and TP38** (the two voice-coil ends) flank them; the central hole
holds the **NFC coil** and the **magnet well**; multiple `J107S`-marked parts (the 100 µF caps) sit
around the rim; silkscreen `820-01736-A` and data code `2920 17` and a lone `C` are on the copper.

**FCC "MLB – Front"** ([internal photo 6](images/airtag/fcc-BCGA2187-internal-photo-6.jpg)) is Apple's
own labelled view: it names **Bluetooth Antenna**, **Bluetooth Module**, **UWB Module**, **UWB
Antenna** around the ring — confirming the BLE and UWB front-ends each have their own antenna segment
on the carrier, arranged on opposite sides of the donut.

### 2.2 Connector-less contacts

There are **no connectors** anywhere. Every off-board connection is a spring contact or a soldered
antenna tab:

- **Battery:** 3 sprung metal contacts in the CR2032 well — **1 negative** on the floor, **2 positive**
  tabs on the wall. Visible in [FCC internal photo 4](images/airtag/fcc-BCGA2187-internal-photo-4.jpg).
  *"slightly sprung to maintain good connection with the battery"* (Catley). **Both** positive tabs
  must see 3 V for the tag to boot; only the left one actually powers the electronics, the right one
  is sensed at ~50 nA (see §6).
- **Antennas:** the LDS carrier's three antenna traces are **soldered to pads at the board edge** (O'Flynn
  counts 6 tear-off joints: *"4x at upper center and 2x bottom left-of-center"*). NFC has an extra
  return trace on the far side of the plastic with a via at each end.
- **Voice coil:** two solder joints (TP1, TP38) to the coil that is glued into the dome (§5).

---

## 3. Components table — exhaustive BOM (first-gen A2187)

Legend: **F** = front/top side, **B** = back/bottom side. "Marking" = the text actually read off the
part in a photo where available.

| # | Function | Part (as identified) | Package / marking | Who identified it | Source | Conf. |
|---|---|---|---|---|---|---|
| U1 | **MCU + BLE 5 radio + NFC tag** (the brain — runs firmware, BLE, NFC) | Nordic Semiconductor **nRF52832** (variant **nRF52832-CIAA**, i.e. `nRF52832CIAAE`, WLCSP-50, 90 nm) | WLCSP, marking `N52832 CIAAE0 2102JK` (B) | Catley; iFixit; O'Flynn; TechInsights; lane A read the marking | [adamcatley](https://adamcatley.com/AirTag.html); [TechInsights](https://www.techinsights.com/blog/apple-airtag-teardown); [`oflynn-backside-fullres`](images/airtag/oflynn-backside-fullres.jpeg) | [primary] |
| U2 | **UWB transceiver** (Precision Finding) | Apple **U1** (die `TMKA75`, TSMC 16 nm) in a **USI** SiP module | shield-can module (B), ~20.58 mm² die area | Catley (die marking via siliconpr0n); iFixit; TechInsights | [adamcatley](https://adamcatley.com/AirTag.html); [TechInsights](https://www.techinsights.com/blog/apple-airtag-teardown) | [teardown] |
| U3 | **Firmware storage** (holds nRF firmware **and** the U1 "Rose" firmware; unencrypted) | GigaDevice **GD25LE32D** (iFixit) / **GD25LQ32C/GD25LQ32DLIGR** (O'Flynn, from the WLCSP-10 pinout) — **32 Mbit (4 MB) SPI NOR** | WLCSP-10, 1.8 V | iFixit; O'Flynn (identified via Digikey 10-pad WLCSP search) | [iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks); [O'Flynn](https://colinoflynn.com/2021/05/apple-airtag-teardown-test-point-mapping/) | [primary] |
| U4 | **3-axis accelerometer** (motion wake, anti-stalk sound trigger) | Bosch Sensortec **BMA280** (iFixit: "BMA28x") | metal-lid LGA (B) | Catley; iFixit; EDN | [adamcatley](https://adamcatley.com/AirTag.html); [iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks) | [teardown] |
| U5 | **Audio amplifier** (drives the voice coil) | Maxim Integrated **MAX98357A** (iFixit: MAX98357B), class-D / class-AB digital audio amp | WLCSP, marking region (B) | Catley; iFixit | [adamcatley](https://adamcatley.com/AirTag.html); [iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks) | [teardown] |
| U6 | **Main DC-DC buck** (steps 3 V cell to 1.8 V rail) | TI **TPS62746** 300 mA step-down converter | marking `98C0051 / TPS746` (B) | Catley; iFixit; lane A read the marking | [adamcatley](https://adamcatley.com/AirTag.html); [`oflynn-backside`](images/airtag/oflynn-backside-1000px.jpeg) | [primary] |
| U7 | **Op-amp** (speaker feedback / analog conditioning) | TI **TLV9001IDPWR** — 1 MHz rail-to-rail I/O op-amp | small (B) | Catley; iFixit | [adamcatley](https://adamcatley.com/AirTag.html); [iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks) | [teardown] |
| U8 | **Load switch / OVP** (power-path gating to U1/flash) | onsemi **FPF2487** over-voltage-protection load switch | small (B) | iFixit | [iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks) | [teardown] |
| U9 | **LDO / secondary regulator** (likely 1.8 V for flash) | small SOT, marking `1A8` / `1950` (unconfirmed exact PN) — iFixit lists "Likely onsemi DC-DC" + "Likely TI DC-DC" | SOT-23-ish (B) | iFixit ("likely"); lane A read `1A8`/`1950` marking | [iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks) | [unverified] |
| X1 | **HF crystal** (32 MHz for BLE/radio) | 32 MHz crystal | 2-pad SMD, marking `T320 / RBEV` (B) | Catley; lane A read the marking | [adamcatley](https://adamcatley.com/AirTag.html) | [primary] |
| X2 | **LF crystal** (32.768 kHz RTC / low-power timing) | 32.768 kHz crystal | can, marking `A048L` (B) | Catley; lane A read the marking | [adamcatley](https://adamcatley.com/AirTag.html) | [primary] |
| C1–C5 | **Bulk energy storage** (hold-up for reset-by-battery-removal + speaker transients) | **5 × 100 µF** electrolytic/tantalum | marked `J107S` around the rim | Catley; EDN ("five 100 µF … labeled J107S") | [adamcatley](https://adamcatley.com/AirTag.html) | [primary] |
| — | many decoupling / matching passives | 0201/0402 R, L, C incl. antenna matching networks and diode pairs (`K11` marked schottky pairs seen mid-ring) | both sides | O'Flynn/Catley photos | [`oflynn-backside-fullres`](images/airtag/oflynn-backside-fullres.jpeg) | [primary] |
| ANT1 | **BLE antenna** — 2.4 GHz, IFA (inverted-F) | LDS trace on the plastic carrier; test report gives **IFA, max gain −3.2 dBi** | on carrier, soldered to edge (F) | Catley; FCC BLE report | [adamcatley](https://adamcatley.com/AirTag.html); [FCC E1V2](https://fccid.io/BCGA2187/Test-Report/12791034-E1V2-FCC-IC-BLE-Report-Final-5130965) | [primary] |
| ANT2 | **NFC antenna** — 13.56 MHz coil | LDS coil + return trace/via on carrier (behind white cover) | centre ring (F) | Catley; FCC photo labels "NFC Antenna" | [adamcatley](https://adamcatley.com/AirTag.html); [FCC photo 5](images/airtag/fcc-BCGA2187-internal-photo-5.jpg) | [primary] |
| ANT3 | **UWB antenna** — 6.5–8 GHz, integral patch | LDS trace on carrier; **1 antenna**, gain **−1.6 dBi @6.5 GHz, −0.6 dBi @8 GHz** | on carrier (F) | Catley; FCC UWB report | [adamcatley](https://adamcatley.com/AirTag.html); [FCC E2V3](https://fccid.io/BCGA2187/Test-Report/12791034-E2V3-FCC15-519-Final-Report-5130980) | [primary] |
| SPK | **"Speaker"** — voice coil + fixed magnet, dome is the diaphragm | copper voice coil glued to plastic dome, driven by MAX98357A across TP1/TP38; central rare-earth magnet fixed to the board/ring | centre (F) | iFixit; Catley | [iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks); [adamcatley](https://adamcatley.com/AirTag.html) | [primary] |
| BATT | **Power source** | CR2032 3 V coin cell, 3 sprung contacts | back well | FCC photos; Catley | [FCC photo 4](images/airtag/fcc-BCGA2187-internal-photo-4.jpg) | [primary] |

> Note on the U1's "why 64-bit ARM in the flash": the SPI flash contains 64-bit ARM instructions the
> nRF52832 (Cortex-M4, 32-bit) cannot run, so **the U1 contains its own processor** and its firmware
> ("Rose") is stored in the shared flash and side-loaded to the U1 by the nRF. (Catley, citing
> ghidraninja.) This matters for the clone: the U1 is a full subsystem, not a peripheral.

---

## 4. Function map — AirTag function → parts → interfaces → can we clone it 1:1?

This is the table nothing else in the repo provides. "Interfaces" are as far as published; some
nRF↔peripheral nets are inferred from the test-point map and standard usage.

| AirTag function | Part(s) implementing it | Interfaces / pins between them (as published) | Reproducible 1:1? |
|---|---|---|---|
| **Run firmware / be the CPU** | nRF52832 (Cortex-M4F) | — | **Yes** — nRF52832 is a stock catalogue part |
| **BLE Find My broadcast** | nRF52832 radio → ANT1 (IFA) via matching network | nRF RF pins → π-match → LDS BLE trace; SoftDevice S112 stack (Catley) | **Yes** — this is exactly what OpenHaystack/clones do (lane B/D) |
| **NFC "found it" tag** | nRF52832 **NFC-A peripheral** → ANT2 coil | nRF `NFC1`/`NFC2` pins (P0.09/P0.10) → tuning caps → LDS coil; emulates an NXP MIFARE-Plus (Type-4) read-only tag holding the `found.apple.com/airtag?...` URL | **Yes** — nRF52832 has the NFC tag peripheral built in; the URL is just tag data |
| **Precision Finding (UWB ranging + direction)** | Apple **U1** → ANT3 patch; U1 talks to nRF | U1 in USI SiP; nRF loads U1 "Rose" firmware from flash, commands it over the "Durian" L2CAP/SPI path (opcodes: Rose Init/Ready/Start Ranging/… in seemoo list) | **NO — hard wall.** U1 is Apple-custom, never sold. See §9. Closest = NXP/Qorvo DW3xxx UWB, but not pin/protocol compatible (lane E) |
| **Play the alert sound** | MAX98357A amp → voice coil (TP1/TP38) → magnet → dome diaphragm; TLV9001 op-amp in the analog path | nRF I²S/PWM audio → MAX98357A → coil; ~8 mA while sounding (>3000× sleep) | **Yes** (electrically). The *acoustic* trick (housing = diaphragm) is a mechanical design choice a clone can copy or replace with a cheap speaker |
| **Detect motion / wake / anti-stalk** | Bosch BMA280 accelerometer | I²C or SPI to nRF (BMA280 supports both); sampled every 10 s waiting, 0.5 s once moving | **Yes** — BMA280 is catalogue (or any modern 3-axis accel) |
| **Store firmware + keys** | GD25LE32/LQ32 32 Mbit SPI NOR | SPI: nRF SCLK/CS/COPI/CIPO on TP22/24/19/20; flash Vcc 1.8 V forced via TP21; nRF gates flash power | **Yes** — generic SPI NOR |
| **Power management** | TPS62746 buck (→1.8 V), FPF2487 load switch, LDO(`1A8`), 5×100 µF bulk | 3 V cell → buck → 1.8 V system; load switch gates U1/flash; caps hold up through battery-swap reset | **Yes** — all catalogue PMIC parts |
| **Timing** | 32 MHz + 32.768 kHz crystals | nRF HFXO / LFXO pins | **Yes** |
| **Boot from battery** | 3 sprung contacts, 2 positive rails sensed | both VCC1 & VCC2 need 3 V to boot; left rail powers logic, right sensed @~50 nA | **Yes** — trivial to replicate; the dual-sense is a design nicety |
| **Reset-by-battery-removal (5×)** | 5×100 µF bulk caps keep it alive seconds after removal | — | **Yes** |
| **Firmware update** | UARP over BLE/L2CAP "Durian" service, image staged from the iPhone; U1 firmware in the same super-binary | opcodes 32 "Abort FWDL", 219 "Send UARP message", etc. (seemoo) | **Partial** — the *mechanism* is reproducible; joining Apple's real OTA feed needs Apple's servers + a paired account |
| **Get on the real Find My app / map** | per-unit Apple **Token** pre-burned to flash at factory (MFi) | — | **NO for the certified path** (lane D's "Door 1"). The unregistered OpenHaystack path works but is not in the stock Find My app |

**Bottom line of the map:** every row is **Yes** except **UWB/Precision Finding** (no U1) and the
**certified Find My onboarding** (no Apple Token). Those two are the only walls; both are commercial/IP
walls, and the UWB one is also a silicon-availability wall.

---

## 5. The speaker mechanism (mechanical detail, since it defines the housing)

- The **voice coil is glued to the outer plastic shell, which acts as the diaphragm**; a **fixed
  central magnet** sits inside the donut hole. Energising the coil moves coil-vs-magnet, flexing the
  dome to make sound. (Catley; iFixit.)
- iFixit: *"That's not a clickable button … but rather the magnet … It sits right inside the
  donut-shaped logic board, nested into a coil of copper to form a speaker."* and
  *"a very fragile copper voice coil lines the middle of the donut."*
- **The AirTag works identically with the coil disconnected** — all sound events still fire, silently.
  This is the documented anti-stalking weakness (disable the speaker without breaking function). Catley:
  the magnet can even be removed if the firmware is patched to not check for an open circuit.
- Power cost: playing sound draws **~8 mA (>3000× the 2.3 µA sleep)** — Catley attributes this to the
  nRF rapidly feeding audio samples to the DAC.
- Loudness: iFixit measured **~78–80 dB** at one iPhone-mini length; drilling a keyring hole through
  the plastic changed it by only ±1 dB, confirming the whole dome radiates.
- **For a clone:** the housing-as-diaphragm is elegant but optional. A cheap coin speaker or piezo
  makes equal or louder noise (iFixit: the Tile/SmartTag piezos were as loud). Copy it 1:1 for
  fidelity, or substitute a standard speaker to de-risk manufacturing.

---

## 6. Power path & battery

| Item | Detail | Source |
|---|---|---|
| Cell | CR2032, 3 V nominal, ~225 mAh (Panasonic in test unit) | Catley; FCC photo 3 |
| Two positive terminals | **both** need 3 V to boot; **left powers the electronics**, **right is only sensed (~50 nA all modes)** | [Catley](https://adamcatley.com/AirTag.html); [O'Flynn README](https://github.com/colinoflynn/airtag-re) |
| Big pads not connected | The large pads *under* the battery terminals are **NOT** the electrical contacts — you must solder to the smaller pads where the terminals sit (O'Flynn) | [airtag-re](https://github.com/colinoflynn/airtag-re) |
| System rail | ~**1.8 V** from TPS62746 buck; flash forced on with 1.8 V at TP21 | Catley; O'Flynn |
| Min boot voltage | nRF needs **~1.9–2.0 V** to boot; works down to the cell's 2.0 V cutoff | Catley |
| Hold-up | 5×100 µF keep it powered several seconds after battery removal (enables the 5× reset ritual) | Catley |
| Sleep current | **2.3 µA** idle → *"maximum battery life of at least 11 years if it never woke"*; nRF alone is 1.9 µA, so the rest of the board is aggressively power-gated | Catley |

---

## 7. Test points, debug port, and how the firmware was dumped

### 7.1 Test-point map (Colin O'Flynn's numbering — the de-facto standard)

Top-side pads, accessible **after popping off just the back plastic cover, without removing the PCB**
(O'Flynn). Full annotated image: [`images/airtag/oflynn-frontside-tpnames.jpg`](images/airtag/oflynn-frontside-tpnames.jpg).

| TP | Function | nRF ball (O'Flynn) |
|---|---|---|
| VCC1 / 6 | +3.0 V input rail 1 (powers logic) | — |
| VCC2 / 5 | +3.0 V input rail 2 (sensed) | — |
| GND / 7, 29 | Ground (29 = under the Apple logo) | — |
| 1 | One end of the voice coil | — |
| 38 | Other end of the voice coil | — |
| 8 | nRF P0.16 | E2 |
| 9 | nRF P0.26 | D3 |
| 19 | SPI flash **Data In (COPI)** | H3 / P0.16 |
| 20 | SPI flash **Data Out (CIPO)** | H4 / P0.15 |
| 21 | SPI flash **Vcc (1.8 V)** — force high to power flash | — |
| 22 | SPI flash **SCLK** | G3 / P0.17 |
| 23/24 | SPI flash **CS** | F4 / P0.11 |
| 28 | **The glitch injection pad** (nRF power pin next to the pads) | — |
| 30 | nRF **nRST** | H1 / P0.21 |
| 31 | SWO | H2 / P0.18 |
| 34 | 1.8 V from nRF (used as glitch **trigger**) | — |
| 35 | **SWCLK** | F1 |
| 36 | **SWDIO** | G1 |

So the **SWD debug port is fully exposed** on TP30/35/36 (+SWO 31), and the SPI flash is fully exposed
on TP19–24. *"nRF programming interface (SWD) easily accessible via test pads and can be unlocked."*
(Catley.)

### 7.2 Flash read is trivial

The SPI NOR can be read in place: power the tag, force 1.8 V on TP21, hang a J-Link/SPI reader on the
SPI pads. O'Flynn read it twice and verified with `Segger J-Flash SPI` (detected as `GD25LQ32C`). The
flash is **unencrypted** and contains both nRF firmware and the U1 "Rose" firmware. The dump even opens
with an Apple ASCII warning banner (O'Flynn: *"Apple gives you a good warning at the start of the
file"*).

### 7.3 APPROTECT and the glitch (how the nRF flash was dumped and modified)

- The nRF52832 has **APPROTECT** (Access Port Protection) **enabled** — SWD reads of internal flash are
  blocked. Confirmed enabled on AirTags (Catley, citing O'Flynn).
- APPROTECT is defeated by **LimitedResults' 2020 voltage-glitch** (archived
  `research/fetched/A-limitedresults-nrf52-approtect-bypass.md`). Mechanism, verbatim-sourced:
  - *"This security investigation presents a way to bypass the APPROTECT on a protected nRF52840 …
    All the nRF52 versions are impacted."*
  - *"the vulnerability cannot be patched without Silicon redesign, leading to a countless number of
    vulnerable devices on the field forever."*
  - The glitch targets the **DEC1 pin (the CPU 0.8–0.9 V core rail)** with a short pulse **during the
    early-boot window where the NVMC transfers the UICR APPROTECT value to the debug block**, before
    the CPU runs code (there is no bootROM). A successful glitch leaves the AHB-AP debug port enabled;
    OpenOCD then dumps flash (`dump_image nrf52_dumped.bin 0x0 0x100000`).
  - On the **AirTag**, the glitched pin is exposed as **TP28**, right next to the test pads; the
    trigger is TP34 (1.8 V). Tooling that industrialised this: **stacksmashing's Pi-Pico glitcher**
    ([airtag-glitcher](https://github.com/stacksmashing/airtag-glitcher)), **pd0wm's STM32 version**
    ([airtag-dump](https://github.com/pd0wm/airtag-dump): glitch→TP28 via NFET, trigger TP34, power
    VCC1+VCC2), and **itewqq's Raspberry-Pi version**. All credit LimitedResults + O'Flynn's TP map.
- **No secure boot:** modifying the firmware does not brick the tag → the firmware signature is **not**
  checked against an Apple certificate (Catley). This is what let **stacksmashing change the Lost-Mode
  NFC URL** to `stacksmashing.net` in May 2021 (the first public AirTag firmware mod) and let others
  run custom firmware.

**For a clone:** since halo would run *our own* nRF firmware, none of this is an obstacle — it is
simply proof the platform is fully open to us. We can (and should) either leave APPROTECT off during
development or enable it knowing it is glitchable.

---

## 8. Firmware & how the U1 is talked to

- **What the nRF runs:** Apple firmware on top of a Nordic **SoftDevice** (Catley: *"likely S112"*)
  for the BLE stack. The nRF is the master; it drives BLE, NFC, the accelerometer, the audio amp, and
  commands the U1.
- **How the U1 is talked to:** the U1 ("Rose") is a coprocessor. Its firmware lives in the shared SPI
  flash and is loaded by the nRF. The control protocol is the **"Durian"** service — a set of L2CAP
  opcodes reverse-engineered by SEEMOO (archived `research/fetched/A-seemoo-airtag-firmware-and-opcodes.md`),
  e.g. `1 Rose Init`, `2 Rose Ready`, `3 Rose Start Ranging`, `4 Rose Ranging Complete`, `6 Rose Stop`,
  `21 Rose Set Parameters`, `36 Rose P2P Timestamp`. Sound/accel/battery/key-rotation are other opcodes
  in the same list (`40 Play Sound Sequence`, `39 Get Battery Status`, `43 Roll Wild Key`, …).
- **Firmware update mechanism:** OTA via **UARP** (Apple's accessory update protocol) tunnelled over
  BLE/L2CAP; the iPhone stages a **super-binary** (`DurianFirmware.acsw` / `DurianFirmwareMobileAsset.bin`)
  that contains both the nRF image and the U1 `ftab`. SEEMOO demonstrated **downgrades** by TOCTOU-swapping
  the staged file (jailbroken iPhone + Frida). Opcodes `32 Abort FWDL`, `219 Send UARP message to
  accessory` gate the flow. Rollout is staged by `deploymentLimit` percentages in the Mesu XML.
- **Debug interfaces:** SWD on TP30/35/36 (APPROTECT-locked but glitchable); SPI flash on TP19–24
  (open). No JTAG.

---

## 9. Firmware / hardware revision history that matters

Firmware history (from The iPhone Wiki OTA list, via Wayback; archived
`research/fetched/A-airtag-firmware-ota-history.md`), extended with Wikipedia for post-2022:

| Version | Build | Codename | Rollout | Release date | Source |
|---|---|---|---|---|---|
| **1.0.225** | ? | **VanBuren** | pre-installed (never OTA'd) | at launch (Apr 2021) | iPhone Wiki; seemoo (*"the very first stock version (1.0.225) was never released as OTA"* — so you cannot downgrade to the no-anti-stalking original) |
| 1.0.276 | 1A276d | — | 2% | 3 Jun 2021 | iPhone Wiki |
| 1.0.276 | 1A287a / 1A287b | — | 10% / 100% | 12 / 22 Jun 2021 | iPhone Wiki |
| 1.0.291 | 1A291a…1A291f | — | 1%→100% | 26 Aug – 14 Sep 2021 | iPhone Wiki |
| 1.0.301 | 1A301 | — | 1%→100% | 26 Apr – 13 May 2022 | iPhone Wiki |
| **2.0.24** | 2A24e | **Burr** | 1%→100% (**pulled during 100% week**) | 10 Nov – 1 Dec 2022 | iPhone Wiki |
| 2.0.36 | 2A36 | Burr | 25% / 100% | 12 / 16 Dec 2022 | iPhone Wiki |
| … later 2.0.x … | e.g. **2.0.73 (2A73)** | — | — | 19 Mar 2024 | [Wikipedia](https://en.wikipedia.org/wiki/AirTag) |
| **FCC-cert firmware** | **1A186** | — | (test firmware at certification, Oct 2020) | — | [FCC E2V3/E1V2](https://fccid.io/BCGA2187) |

- The `fv=00100e10` parameter Catley saw in the NFC URL is the firmware version field.
- **Hardware revisions of gen-1** are limited to PCB copper-marking / data-code variations by region
  (US `2920/3020/3120`, EU `5220`, Asia `1021`) and a letter (`A`+3 digits for EU, `C` for RoW) left of
  the big U1 pads — Catley flags these as the only visible board variations, possibly tracking which
  early runs had all security features enabled.

---

## 10. AirTag 2 (2026) — what changed

Second generation, **released 2026-01-26** ([MacRumors](https://www.macrumors.com/2026/02/05/ifixit-shares-airtag-2-teardown/);
Wikipedia). Same ~coin form factor, same user-replaceable **CR2032**, same twist-off steel cover,
weight **11.8 g**, firmware **3.0.41**.

| Subsystem | Gen 1 (A2187) | Gen 2 (2026) | Source | Conf. |
|---|---|---|---|---|
| MCU/BLE/NFC | nRF52832 | **nRF52840** (more flash/RAM, USB, Cortex-M4F) | [Hackaday/electronupdate](https://hackaday.com/2026/02/02/teardown-of-an-apple-airtag-2-with-die-shots/); [9to5Mac](https://9to5mac.com/2026/02/05/ifixit-tears-down-new-airtag-finds-50-louder-speaker-still-100-easy-to-disable/) | [teardown] |
| UWB | Apple U1 | **Apple U2** (2nd-gen UWB; Precision Finding "up to 50% farther") | iFixit via MacRumors; Hackaday | [teardown] |
| Storage | GD25 SPI NOR | "SPI memory device, likely an EEPROM" | Hackaday/electronupdate | [secondary] |
| Accelerometer | Bosch BMA280 | Bosch accelerometer (die-shot confirmed) | Hackaday | [teardown] |
| Speaker | coil+magnet, easy to remove | **redesigned, ~50% louder, nested deep inside the UWB antenna ring → harder to remove but still disableable with a soldering iron** | [iFixit via MacRumors](https://www.macrumors.com/2026/02/05/ifixit-shares-airtag-2-teardown/); 9to5Mac | [teardown] |
| Construction | 3 sandwiched boards + LDS antenna carrier | *"individual layers of sandwiched rings"*; speaker → UWB antenna ring → PCB | [electronupdate](https://electronupdate.blogspot.com/2026/01/reverse-engineering-apple-airtag-2.html) | [secondary] |

For halo targeting the **well-documented gen-1**, AirTag 2 mainly signals: the platform choice
(nRF52 + Apple UWB + CR2032 + coil speaker) is unchanged in principle; a clone built around nRF52 stays
architecturally faithful to both generations.

---

## 11. Cost / BOM estimates

- **TechInsights:** *"estimated manufacturing cost of USD 10 (not including software costs and R&D)"*
  against a sub-USD-30 retail. Radio ICs occupy *"less than 30 mm², or 6%, of the entire available PCB
  area."* nRF52832 = **WLCSP50, 90 nm** (*"75% smaller than the 48-pin QFN alternative"*). U1 SiP =
  **TSMC 16 nm, 20.58 mm²**, containing the Apple UWB transceiver + embedded crystal oscillator + a
  **Sony RF switch** + discretes. ([techinsights](https://www.techinsights.com/blog/apple-airtag-teardown))
- **Counterpoint Research** has a full "BoM Analysis of Apple AirTag" report — **paywalled**, figures
  not extractable ([counterpointresearch](https://www.counterpointresearch.com/research_portal/bom-analysis-of-apple-airtag/)).
  Marked **[unverified]** for line items.

---

## 12. What this means for a clone (summary — substitutes are lane E's job)

**Reproducible 1:1 (all catalogue parts, all publicly documented):**
- The whole digital/analog core: **nRF52832** (MCU+BLE+NFC), **GD25 32 Mbit SPI NOR**, **BMA280**
  accelerometer, **MAX98357A** amp, **TPS62746** buck, **FPF2487** load switch, **TLV9001** op-amp,
  32 MHz + 32.768 kHz crystals, 5×100 µF bulk.
- The **BLE Find My broadcast** and the **NFC "found-it" tag** — both are native nRF52832 functions and
  are exactly what OpenHaystack and the clone flood already do (see lanes B and D).
- The **coil-and-magnet speaker** (or substitute a coin speaker — acoustically equivalent, cheaper to
  build).
- The **power path**, **dual-sense battery contacts**, **hold-up caps / 5× reset**, **CR2032** interface,
  and the **antenna set** (BLE IFA + NFC coil + — if UWB is dropped — the carrier can be simpler). LDS
  antennas can be replaced by a normal FR4/flex antenna or a chip antenna.
- The **connector-less assembly** (spring battery contacts + soldered antenna tabs) — straightforward.
- Our **own firmware** on the nRF — no Apple secure boot or signing stands in the way.

**Cannot be reproduced:**
- **Apple U1 / U2 UWB → Precision Finding.** The U1 is Apple-custom silicon (TMKA75 die, TSMC 16 nm, in
  a USI SiP), **not sold to anyone**. There is no drop-in. The closest *category* substitute is a
  standard UWB transceiver (Qorvo/NXP DW3xxx class) — **not pin-, protocol-, or Find-My-compatible**, and
  it will not do Apple Precision Finding. Evaluating whether/how to add third-party UWB is **lane E's**
  call; this file only marks it as the single hard silicon wall.
- **Appearing in the stock Find My app** (the certified path) needs a per-unit **Apple Token** burned at
  an MFi factory — a commercial/contractual wall, not a hardware one (lane D, "Door 1"). The
  **unregistered OpenHaystack path** works with off-the-shelf hardware but does not show in the stock app.

**Net:** halo can be a near-exact internal copy of the AirTag minus UWB. Drop the U1 and its antenna,
keep the nRF52832 + flash + accel + speaker + power + BLE/NFC, and you have a manufacturable, cheaper
Find-My-class tag that is faithful to the AirTag's internals in every reproducible respect.

---

## 13. Archived primary sources (in `research/fetched/`)

- `A-catley-airtag-reverse-engineering.md` — full text of adamcatley.com/AirTag (the master RE page).
- `A-oflynn-testpoints-and-glitch-repos.md` — O'Flynn teardown blog + airtag-re README (CC-BY) + pd0wm + itewqq READMEs.
- `A-ifixit-airtag-teardown.md` — full iFixit teardown article text.
- `A-limitedresults-nrf52-approtect-bypass.md` — the nRF52 APPROTECT glitch, part 1.
- `A-seemoo-airtag-firmware-and-opcodes.md` — firmware update/downgrade + full L2CAP opcode list.
- `A-airtag-firmware-ota-history.md` — the OTA firmware version table.
- `A-fcc-bcga2187-extracts.md` — FCC UWB + BLE test-report EUT descriptions (antennas, gains, freqs, firmware).

Images: `images/airtag/` (7 O'Flynn CC-BY photos incl. the annotated TP map + full-res both sides;
8 FCC internal-photo pages incl. Apple's own antenna/module labelling and the battery-contact view),
catalogued in `images/airtag/CATALOG.md`.
