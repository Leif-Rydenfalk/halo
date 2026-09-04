# REFERENCE-TEARDOWN — the AirTag as the copy target

> **NAMING TRAP — read this before any (F) or (B) tag below.**
>
> Three sources use *front* for two different faces. Apple's FCC filing labels
> the IC side **"MLB - Front"**. Colin O'Flynn calls that same physical side
> **"backside"**. And **this document's own legend (§2) is a third convention**:
> `F` = the battery-contact and coil side, `B` = the IC side — i.e. the opposite
> of Apple's word.
>
> **This document keeps its own legend.** Every `(F)` and `(B)` tag in the tables
> below was written under it, so redefining the header would silently invert the
> whole document. An earlier edit of mine (commit 391f676) did exactly that for
> about an hour and propagated into five downstream lane briefs before it was
> caught — the correction is why this box is now three lines longer than it was.
>
> **Do not adopt any of the three words. Name faces by what is on them:** "the
> side carrying the SoC and the shield can", "the side carrying the battery
> contacts and the coil". That is unambiguous under every convention and it
> survives this document changing. House style for the replica lane and
> recommended everywhere.

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

**⚠ ANT2 IS OPEN, NOT SETTLED. The supporting argument below was WITHDRAWN by
its own author on 2026-09-05** (`electronics/halo_replica/evidence/E02-THE-COIL-CORRECTION.md`,
commit 6d84ac7). The withdrawn part was the strongest-sounding: "a turn count and
a band width agreeing to 1.4 % with neither fitted to the other". A voice coil is
a **solenoid**, and seen from above a solenoid and a flat spiral present the
**same radial band width** — so those were two measurements of one quantity and
**could not have disagreed**. The count was also wrong: at full resolution the
per-sector conductor counts are 2, 6, 9, 6 across a 0.998 mm band, so at least 9
turns at about 111 µm pitch, nearer AWG 38 than AWG 35, and 9 is a lower bound
because the turns smear when averaged, which itself shows the coil is not
concentric with the assumed centre.

**What survives, and it is a direct observation rather than an inference:** at
full resolution the conductors are individually resolved, coplanar and equally
lit. That is what wound wire looks like. The band geometry is unaffected.

**The unresolved conflict:** the coil's two fine leads terminate on TP1 and TP38,
and §2.4 of this document calls those the **voice coil's** solder joints, while
Apple's own arrow in FCC photo 5 labels that annulus the **NFC Antenna**. Both
cannot be true. Note that the voice-coil attribution for those pads is an
assertion made inside this repository, not a quotation from O'Flynn — his text
does not say what they are.

**The physics currently favours NFC:** 9 turns of 111 µm wire on a 10.1 mm mean
diameter is roughly 286 mm of conductor and about **0.50 Ω**, where a voice coil
driven by a class-D amplifier into 4–8 Ω needs several ohms — around a hundred
turns at this gauge, needing a dozen layers of depth and a radial band far wider
than the 0.727 mm measured. **If it is nonetheless the voice coil, ANT2 returns
to the laser-structured list and the Replica's gap goes back to three antennas.**

**What would settle it and is not available here:** DC resistance across TP1/TP38
on a live unit — sub-ohm for a loop against several ohms for a voice coil — or a
photograph of the front dome's inner face showing whether a coil is glued there.

The measured geometry, which stands regardless: The replica lane measured the front
photograph and the NFC coil is **wound magnet wire**, not a structured trace:
individual turns resolve at 2x, the copper band measures 0.727 mm radially, and
about 5 turns are countable, giving **0.145 mm per turn against AWG 35 magnet
wire at 0.143 mm — 1.4 % apart, with neither number fitted to the other**.
Inner diameter 9.380 mm, outer 10.834 mm (ratios to the datum 0.3608 and 0.4167,
which are the figures to quote since the datum itself is approximate). Method:
`electronics/halo_replica/metrology/M01-SCALE-AND-DATUM.md` §3, commit 4abdc99.
Confidence HIGH for this unit. **Whether ANT1 and ANT3 share one carrier is
still CANNOT DETERMINE** — the front photograph shows only the coil.

**ANT1 and ANT3 CORROBORATED 2026-09-05, after a hypothesis that they might be
on the board was tested and refuted.** Apple's own arrows in FCC photo 6 label
Bluetooth and UWB antennas at the rim, which raised the possibility that they
are etched in board copper and that the laser-structuring obstacle was
imaginary. It is not. That photograph calibrates at 15.887 px/mm against the
steel rule in frame, so one pixel is 0.063 mm and antenna trace geometry of
0.2–0.5 mm spans three to eight pixels — at which scale an etched trace, a
structured trace and a solder joint to a carrier are indistinguishable. Apple's
labels establish **where** the antennas are, not **what they are on**.

The instrument that answers it is O'Flynn's backside scan at roughly 90–110
px/mm, six to seven times better, and taken with the plastic carrier removed:
**there is no antenna structure of any kind in the outer copper of either
side** — no meander, no inverted-F, no patch. Every copper feature resolves as
routing, a pad or a via. What lines the rim is a fibrous grey conductive gasket
or adhesive, the same material that defeats edge-detection on the board outline,
so the two findings corroborate from opposite directions.

The reasoning was stated before the images were interpreted, deliberately,
because the prize was large enough to bias the reading: a 2.4 GHz antenna on a
26 mm board is a **large** feature, hundreds of pixels at this scale. Low
resolution misleads about fine detail; the absence of a large feature is not
that kind of claim. Full argument: `electronics/halo_replica/evidence/E01-ARE-THE-ANTENNAS-ON-THE-BOARD.md`, commit 52d2931.

**Still open:** whether an antenna exists on an **inner** layer. No photograph
sees inner layers; an X-ray or a cross-section would settle it.

The original claim, corroborated for ANT1 and ANT3 and superseded for ANT2:
all three are **laser-direct-structured (LDS) onto a single plastic carrier** and soldered to the
board edge (6 tear-off joints). The NFC coil has an extra return trace on the far side of the
plastic with a via at each end.

| # | band | Apple's implementation | measured gain (FCC) | verdict |
|---|---|---|---|---|
| ANT1 | BLE 2.4 GHz | LDS trace, **IFA** (inverted-F) | **−3.2 dBi** max | **SUB** — LDS needs tooling; a PCB IFA or chip antenna is the open-hardware answer (lane I) |
| ANT2 | NFC 13.56 MHz | **wound magnet wire, ~AWG 35, ~5 turns, ID 9.380 / OD 10.834 mm** (measured 2026-09-05) — NOT LDS | — | **REPRODUCIBLE** — winding needs no LDS tooling; a PCB spiral is an alternative, not a necessity |
| ANT3 | UWB 6.5 / 8 GHz | LDS trace, **1 integral patch** | **−1.6 dBi @6.5 GHz, −0.6 dBi @8 GHz** | **GAP/SUB** — only if a UWB chip is fitted |

**Copy note, revised:** the LDS gap is **two antennas, not three** — the BLE
inverted-F and the UWB patch. The NFC coil is wound and can be reproduced
exactly. LDS remains the single most expensive process choice in the AirTag and the least
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
| layer count | **4 — COUNTED, 2026-09-05.** Both halves of the old entry were wrong: it *was* published, and it is not merged. stacksmashing/airtag-hardware holds `pcb/layer1..layer4`, credited to David Hulton. The README's "merged PCB pictures of all the layers" had been read as *superposition* — every layer visible in every image — which would make four files carry no count at all. **That reading is falsifiable and false:** `layer1` shows a fine-pitch square land grid with fanout, a feature only an outer layer can have, and `layer2` at the same board location has none — round via lands in a copper field. Superposition requires the grid to appear in every image; it is absent exactly where that reading demands it. Four physical layers: outer-with-pads, inner pour, inner routing, outer-with-pads, sharing one outline, one centre hole and three plated tooling holes at identical positions. Images **cited, not redistributed** — the source repo states no licence | settled; a cross-section would still confirm the stackup thicknesses |
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
