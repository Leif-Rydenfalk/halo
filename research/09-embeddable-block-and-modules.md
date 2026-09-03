# 09 — The embeddable block: how to ship halo as a circuit other people can drop in

Lane I. Written 2026-09-03. Every claim below carries its source and the date it was read.
Where a number could not be verified this session it says so; nothing here is estimated.

Answering GOAL.md deliverable 2: *"a reusable circuit block that anyone can drop into their own board
in any outline: a KiCad hierarchical sheet + footprints + a documented antenna keep-out, and a
castellated/solder-down module variant for people who do not want to do RF layout."*

---

## 0. The one-paragraph answer

Ship **three artefacts, in this order**: (1) a **KiCad 10 design block**
`halo.kicad_blocks/halo-core.kicad_block/` carrying *both* `halo-core.kicad_sch` and
`halo-core.kicad_pcb` — KiCad 10 added layout fragments to design blocks, so for the first time the
routed antenna and matching network travel with the schematic across projects, as plain directories in
git; (2) a **15 × 20 mm castellated `halo-core` module** whose v1 is a *carrier* for a pre-certified
Raytac MDBT42Q (nRF52832, FCC ID SH6MDBT42Q), so that the radio approval and the RF layout are both
inherited rather than earned; (3) the **round 32 mm puck as the first host board**, which is directly
expressible in `ce-pcb` today (`cepcb.circle_outline`). Nobody in the surveyed open-hardware field ships
all three; SparkFun's Artemis is the closest and it ships (2) only.

---

## 1. Pre-certified nRF52 modules you can solder down

Every row is read from the source named in the last column. Blank = the source did not state it;
"—" = not applicable. **Prices are what the page showed on 2026-09-03 and nothing else.**

### 1.1 The comparison table

| module | SoC | size (mm) | antenna | pads | NFC1/NFC2 out? | SWD out? | certifications | price seen 2026-09-03 | source |
|---|---|---|---|---|---|---|---|---|---|
| **Raytac MDBT42Q-512KV2** | nRF52832 | **16 × 10 × 2.2** | chip | **41** ("41-SMD Module") | **YES** — pad 22 = NFC1/P0.09, pad 23 = NFC2/P0.10 | YES — 36 SWDCLK, 37 SWDIO | FCC **SH6MDBT42Q**, CE, TELEC(MIC), SRRC, IC, NCC, KC, WPC/UKCA, BT 5.4 | **$4.95 @1** Digi-Key (marketplace, 18 in stock, ships ~14 d from Raytac, **$25 flat shipping**) | [Raytac DS](https://www.raytac.com/upload/download_files/38a8a4a0aff945d8484507d60058109b.pdf) · [product](https://www.raytac.com/product/ins.php?index_id=31) · [Digi-Key](https://www.digikey.com/en/products/detail/raytac/MDBT42Q-512KV2/13677592) |
| Raytac MDBT42Q-ATM | nRF52832 | 16 × 10 × 2.2 | chip | | **NO** ("NFC: Not available" on this AT-command variant) | | FCC, IC, CE, Telec, KC, SRRC, NCC | | [Raytac](https://www.raytac.com/product/ins.php?index_id=87) |
| **Insight SiP ISP1807-LR** | nRF52840 | **8.0 × 8.0 × 1.0** (smallest found with an antenna) | integrated, + OUT_ANT/OUT_MOD strap for external | **51, LGA two rows @ 0.65 mm — NOT castellated** | **YES** — pin 2 NFC1, pin 4 NFC2 | YES — 28 SWDIO, 30 SWDCLK | BT SIG, CE, FCC, IC, TELEC, KCC, PSA L1 | **not verified** (Mouser timed out ×2, everythingrf 403) | [ISP1807 DS R19](https://www.insightsip.com/fichiers_insightsip/pdf/ble/ISP1807/isp_ble_DS1807.pdf) |
| **Ezurio (Laird) BL654** | nRF52840 | **15 × 10 × 2.2** | integrated or IPEX MHF4 | castellated (count not stated) | **YES** — "differential antenna pins exposed (NFC1 and NFC2)" | yes (SWD listed) | FCC, ISED, EU, UKCA, MIC, KC, AS-NZS, Taiwan, Brazil, BT SIG | page renders 1K price as `$0.00000` — **unusable** | [Ezurio BL654](https://www.ezurio.com/wireless-modules/bluetooth-modules/bluetooth-5-modules/bl654-series-bluetooth-module-nfc) |
| **Fanstel BT832** | nRF52832 | 14 × 16 × 1.9 | integrated PCB | 40 | not stated | not stated | FCC/ISED/CE/RCM/TELEC/QDID (family) | **$4.46 @1k** | [Fanstel summary](https://www.fanstel.com/bluenor-summaries-copy) |
| Fanstel BT832F | nRF52832 | 15 × 20.8 × 1.9 | integrated PCB | 40 | | | as above | $4.93 @1k | same |
| **Fanstel BT840F** | nRF52840 | 15.0 × 20.8 × 1.9 | integrated PCB | 61 = **16 castellated + 43 LGA** | not stated | | FCC **X8WBT840F**, IC 4100A-BT840F, TELEC 201-190710/00, KCC R-C-F8A-BT840, NCC CCAL22LP0381T0, ANATEL 03583-22-14656, QDID 108621 | **$7.17 @1k** | [Fanstel BT840](https://www.fanstel.com/bt840) |
| Fanstel BT840 / BT840E | nRF52840 | (E: 14 × 16 × 1.9) | PCB / PCB+u.FL | 61 | | | as above | BT840 $6.88 @1–999, $6.09 @1k reel; BT840E $7.94 @10, $7.59 @100, $6.90 @1k | same |
| Fanstel BC840M | nRF52840 | **7.1 × 12.2 × 1.5** | integrated PCB (antenna area 10.1 mm wide) | 48 GPIO | | | (family) | $8.49 @10, $8.12 @100 | [Fanstel BC840M](https://www.fanstel.com/bc840m-compact-nrf52840-module) |
| **Minew MS88SF2** | nRF52840 | 23.2 × 17.4 × 2 | PCB or IPEX | **28**, pads 1.8 × 0.8 mm + 0.5 mm outward | **CANNOT DETERMINE** — pin table lists only "P0.02–P0.31, P1.00–P1.09" and never names NFC1/NFC2 | YES — 26 SWCLK, 25 SWDIO ("Burn Pins") | CE, FCC, QDID/BQB, TELEC, WPC, RCM, IC, KC, RoHS, REACH | JLCPCB C20616655, **Extended**, no stock/price shown | [Minew DS](https://store.minewsemi.com/wp-content/uploads/2024/03/MS88SF2-nRF52840_Datasheet_K_EN.pdf) · [JLCPCB](https://jlcpcb.com/partdetail/Minew-MS88SF2nRF52840/C20616655) |
| **Minew MS88SF3** | nRF52840 | 18.5 × 12.5 × 2.0 | PCB | | as MS88SF2 | | as MS88SF2 | **$2.374 @1 · $0.9481 @200 · $0.917 @500 · $0.900 @1000** — LCSC C20416747, **OUT OF STOCK** on the day | [LCSC C20416747](https://www.lcsc.com/product-detail/C20416747.html) |
| **u-blox ANNA-B112** | nRF52832 | **6.5 × 6.5** | internal | 52-SMD | NFC 13.56 MHz advertised on the EVK | | (u-blox global set) | **$6.99 @1, $5.71 @500 reel**, out of stock, 500 due 2026-12-22 | [u-blox](https://www.u-blox.com/en/product/anna-b112-open-cpu) · [Digi-Key](https://www.digikey.com/en/products/detail/u-blox/ANNA-B112-02B/26581133) |
| Holyiot 18010 | nRF52840 | 18 × 14 × 1.6 | | | **not verified** (datasheet mirror 403) | | CE, FCC, RoHS *per listing* | **$6.58** sample; store range $4.30–6.58, MOQ 5 | [AliExpress](https://www.aliexpress.com/item/32868002366.html) |
| Holyiot 21014 | — | — | — | — | — | — | — | **NOT REACHED THIS SESSION — no data. Do not quote.** | — |
| Ebyte E73-2G4M08S1C | nRF52840 | 13.0 × 18.0 | integrated | SMD, "most IO ports" | not stated | | *"pass various certifications"* — **no IDs, UNVERIFIED** | tier brackets shown, **no numbers without a quote** | [Ebyte](https://www.cdebyte.com/products/E73-2G4M08S1C) |
| SparkFun Artemis (not nRF52) | Ambiq Apollo3 | 15.5 × 10.5 × 2.3 | chip (Abracon) | **59** | no NFC on Apollo3 | YES — pad 2 SWDCK, pad 10 SWDIO, pad 7 BOOT, pad 50 nRESET | **FCC/IC/CE ID 2ASW8-ART3MIS** | **$9.95** | [SparkFun 15484](https://www.sparkfun.com/products/15484) · [Integration Guide v1p0p0](https://cdn.sparkfun.com/assets/learn_tutorials/9/0/9/Artemis_Integration_Guide.pdf) |
| Seeed XIAO nRF52840 (*dev board*) | nRF52840 | 21 × 17.8 | on-board | castellated, pitch not stated | NFC listed | | not a certified radio module | **$9.99 @1, $7.99 @10+** | [wiki](https://wiki.seeedstudio.com/XIAO_BLE/) · [store](https://www.seeedstudio.com/Seeed-XIAO-BLE-nRF52840-p-5201.html) |

Full extracts, including the pin tables and every keep-out sentence:
`research/fetched/I-nrf52-module-datasheet-extracts.md`.

### 1.2 What the table decides

- **Only three modules document NFC1/NFC2 as exposed pins**: MDBT42Q (pads 22/23), ISP1807 (pins 2/4),
  BL654 ("differential antenna pins exposed"). Since halo needs an NFC-A tag on the host board
  (AirTag has one; DULT wants one), **that is the whole shortlist.**
- **ISP1807 is the smallest but is 0.65 mm-pitch LGA, not castellated** — *"The module uses an LGA format
  with a double row of pads on a 0.65 mm pitch"*. That is a stencil-and-reflow-only part on a host board
  that will often be a hobbyist's 2-layer board. It fails the "anyone can integrate it" test.
- **MDBT42Q and BL654 are both 10 × 15/16 × 2.2 mm castellated with NFC out.** MDBT42Q has a *verified
  price and a published FCC ID with the end-product label wording written into its own datasheet*;
  BL654 has neither a usable price from its own page nor a published pad count.
- **MS88SF3 at $0.900 @1000 is the volume answer if two things get resolved**: it was out of stock, and
  its datasheet never names NFC1/NFC2. Both are answerable questions, not guesses — see §7.
- Fanstel's **BT840F 16-castellated-plus-43-LGA** hybrid is the interesting middle: hand-solderable for
  the signals that matter, LGA for the rest. Worth copying as a *pattern* even if not the part.

### 1.3 UWB modules — noted only, lane H owns this
Lane H's material (`research/fetched/H-*.md`) covers DW1000/DW3000 in depth. Two facts relevant here:
Bitcraze's **Loco Positioning deck** publishes only a **PDF schematic** (`loco_deck_revd.pdf`, drawn in
KiCad 4.0.2, **CC-BY 4.0**) — a deck with a defined header, so the DWM1000 block is physically separable
but is not a reusable KiCad artefact; and **Makerfabs** publish full ESP32+DW3000 hardware repos
(`Makerfabs-ESP32-UWB-DW3000`). Qorvo's own DWM3000/DWM3001C pages could not be fetched this session
(`www.qorvo.com` blocked, Digi-Key link mismatched) — **no dimensions or prices for those are asserted
here.** The consequence for the pin list is in §6.3: the same 24 pads must be able to become an SPI bus.

---

## 2. Castellated-module precedents from open hardware

### 2.1 SparkFun Artemis — the closest thing to what halo should be
Verbatim from the repo README
(<https://raw.githubusercontent.com/sparkfun/SparkFun_Artemis/master/README.md>, read 2026-09-03):

> We're proud to say the SparkFun Artemis module is **the first open source hardware module with the
> design files freely and easily available here (on this repo)**. We've carefully designed the module so
> that **routing to the module can be done with low-cost 2-layer PCBs with 8mil trace/space**.

> This repo contains the design files for the 4-layer PCB. This design is pretty reliant on sophisticated
> manufacturing tools. We *do not* recommend that you order PCBs and attempt to hand stencil or hand
> place these components.

That is the exact division halo needs: **a 4-layer machine-assembled module so that every host board
can be a cheap 2-layer board.** Published: Eagle `.brd`/`.sch`, a **STEP and STL of the module** for the
host's 3D view, the chip-antenna datasheet, the Apollo3 pad map — all **CC BY-SA 4.0**. Host rules, from
the integration guide: *"A good ground connection is essential. Routing under the module is allowed.
Keep all ground pours away from the antenna area. If mechanical exposure allows for it the antenna can
be extended over the edge of the PCB for increased reception."*
Full extract: `research/fetched/I-sparkfun-artemis-open-castellated-module.md`.

### 2.2 Raspberry Pi Pico — the carrier-board precedent
*Hardware design with RP2040* (<https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf>)
publishes a **minimal 2-layer KiCad reference**, and then a second reference whose stated purpose is
Pico *"used simply as a component on a larger design"*, with **the Pico footprint itself provided in
KiCad format**. Three things to steal:

> Each pin … has two soldering options. You can either solder 0.1″ headers using the through-holes, or
> alternatively, as both have **castellated edges** …, a pin can be soldered down directly to a PCB.
> **If the SWD pins are used then they should have an extra pin added to ensure a good connection.**

> In Raspberry Pi Pico W there is a cutout for the antenna (**14 mm × 9 mm**). If anything is placed close
> to the antenna (in any dimension) the effectiveness of the antenna is reduced. Raspberry Pi Pico W
> should be placed on the edge of a board and not enclosed in metal to avoid creating a Faraday cage.

> **KiCad currently doesn't have a keepout layer in its footprints. The recommended approach, and the one
> we've used here, is to show the keepout zones on the `dwgs.user` layer, and the user must then manually
> remove the copper on the PCB layout itself.**

That last one is a live constraint for halo: **a footprint cannot enforce the antenna keep-out.**
It has to be drawn on `dwgs.user`, stated in the README, and — see §5 — turned into a check.
Full extract: `research/fetched/I-rp2040-pico-as-a-solder-down-module.md`.

### 2.3 ESP32-WROOM-32 — the antenna keep-out rule everyone copies
Espressif publish both the module reference and a separate *Hardware Design Guidelines* document.
§1.4.8, verbatim:

> It is suggested to place the module's on-board PCB antenna **outside the base board**, and the feed
> point of the antenna close to the edge of the base board. … If the antenna cannot extend beyond the
> board edge … **cut off the base board on both sides of the antenna and below it** … Note that **the
> module should not be placed in the center of the board with clearance created by hollowing out on all
> four sides.** … **sufficient ground copper and dense ground vias should be placed on the base board
> near the antenna.** … **A clearance of at least 15 mm is recommended in all directions** [inside the
> end-product housing].

And the numbers behind it, from the ESP32-WROOM-32 datasheet v3.7 (marked NRND):
module **18.00 × 25.50 × 3.10 mm**; **38 pads at 1.27 mm pitch**, pads 1.50 × 0.90 mm; the recommended
land pattern carries an explicit **"Antenna Area"** rectangle 5.94 mm deep across the 18 mm width; the
pinout drawing labels the top of the module **"Keepout Zone"**; and Espressif ship *"Source files of
recommended PCB land patterns"*. Full extract:
`research/fetched/I-esp32-hardware-design-guidelines-keepout.md`.

### 2.4 Fab rules for the castellations themselves
| | JLCPCB | PCBWay |
|---|---|---|
| min half-hole diameter | **≥ 0.5 mm** | **0.4 mm** ("Design Half-Holes greater than 0.4mm to ensure better connection between boards") |
| min hole-to-hole | ≥ 0.5 mm | edge-to-edge ≥ 0.3 mm |
| min hole-to-board-edge | ≥ 1 mm | — |
| min board size / thickness | 10 × 10 mm / 0.6 mm | 0.2–3.2 mm thickness range |
| edge plating | ≥ 3 breaks for support tabs; **ENIG only, HASL not supported** | 0.4–0.7 mm = medium difficulty, may need review |
| surcharge | none published | none published; quote required |

Sources: <https://jlcpcb.com/capabilities/pcb-capabilities>, <https://www.pcbway.com/capabilities.html>,
both read 2026-09-03. **A 1.27 mm pitch with 0.6 mm plated half-holes clears both houses with margin**
(0.6 ≥ 0.5/0.4; gap 0.67 ≥ 0.5/0.3) and is the pitch ESP32-WROOM already made universal.
Full extract: `research/fetched/I-castellation-fab-rules-and-pinout-standards.md`.

---

## 3. KiCad reuse mechanics — the finding that changes the plan

**KiCad 9 design blocks are schematic-only. KiCad 10 design blocks carry a PCB layout fragment too.**
Both manuals were fetched and diffed this session.

KiCad 9.0 (<https://docs.kicad.org/9.0/en/eeschema/eeschema.html>):
> Schematic design blocks allow you to save a portion of a schematic and reuse it later. … the saved
> schematic fragment is inserted into the current schematic, either in the current sheet or in a new
> subsheet.

KiCad 10.0 (<https://docs.kicad.org/10.0/en/eeschema/eeschema.html>):
> Design blocks are a design-reuse feature that lets you save a portion of a schematic (**and optionally
> a corresponding PCB layout**) as a named, reusable fragment … **A single design block can contain a
> schematic fragment, a PCB layout fragment, or both.** … **If the design block also contains a layout
> fragment, you can later apply that layout to the footprints that were placed as a result of the
> schematic fragment.**

The PCB-editor action is literally named: **`Apply Design Block Layout` — "in the PCB editor, apply the
layout stored in the linked design block to the group of footprints corresponding to this design block
instance."** It requires the block to have been placed with **`Place as group`**; without a group,
*"applying the stored layout to the corresponding footprints in the PCB editor"* is not available.

Library format, verbatim:
> Design block libraries are stored as directories on the filesystem. … The library itself is a directory
> whose name ends with **`.kicad_blocks`** … Each design block … is a subdirectory … with the suffix
> **`.kicad_block`** … Inside each design block directory, KiCad stores: a schematic file
> (`<block_name>.kicad_sch`) …, a board file (`<block_name>.kicad_pcb`) …, a metadata file
> (`<block_name>.json`) … **Because libraries and design blocks are plain filesystem directories, they
> can be managed with ordinary file manager tools, version control systems, or shared over a network
> filesystem.**

One hard limit to design around:
> **Design blocks do not support nested hierarchical sheets.** If the sheet you are saving as a design
> block contains hierarchical sheet symbols (subsheets), the save operation will be rejected.

**Measured on this machine, 2026-09-03:** `ce-pcb/bin/pcb --doctor` exits **0** with
`kicad-cli 10.0.6`, `pcbnew 10.0.6`, KiCad.app at `/Applications/KiCad/KiCad.app`, 15450 footprints in
155 libraries. So KiCad 10 design blocks are available here **today**, not in principle.
(The ce-pcb README/`docs/boards.md` snapshot of 2026-08-23 says KiCad was absent and `bin/board` did not
exist; both statements are now stale — `bin/board doctor` exits 0 and reports every verb as runnable.)

Full extract: `research/fetched/I-kicad-design-blocks.md`.

### 3.1 The other reuse mechanisms, and why they lose
| mechanism | carries schematic | carries copper | cross-project | git-friendly | verdict |
|---|---|---|---|---|---|
| **KiCad 10 design block** | yes | **yes** | yes (global lib table) | yes (plain dirs) | **use this** |
| KiCad 9 design block | yes | no | yes | yes | superseded |
| Hierarchical sheet (`.kicad_sch` file per sheet) | yes | no | by copying the file | yes | the fallback for pre-10 users; also the *shape* a design block is placed into ("Place as sheet") |
| Shared symbol/footprint libs via git submodule | symbols/footprints only | no | yes | yes | necessary but not sufficient — carries the *parts*, not the *circuit* |
| A castellated module | n/a | n/a — it *is* the copper | yes | n/a | the answer for people who will not touch RF layout |

**KiCad has no footprint-level keep-out layer** (Raspberry Pi, above). The workaround — draw it on
`dwgs.user`, tell the user to delete the copper — is what every open project does, and it is why the
keep-out has to also exist as a *check*, not only as a drawing.

### 3.2 How the open field actually publishes today
| project | what is published | format | licence |
|---|---|---|---|
| **RuuviTag** (`ruuvi/ruuvitag_hw`, via lane C) | full board: `.sch`, `.kicad_pcb`, `.pro`, `-cache.lib`, schematic PDF, fp/sym-lib-tables; **includes a working NFC-A tag antenna** | KiCad 5 era | **CC BY-SA 4.0** |
| **SparkFun Artemis** | the *module itself* + 4 carrier boards + STEP/STL | Eagle | CC BY-SA 4.0 |
| **Raspberry Pi Pico** | minimal reference + carrier reference + **Pico footprint** | KiCad | Raspberry Pi's own terms |
| **Espruino** (`espruino/EspruinoBoard`) | schematics for Espruino, Pico, WiFi, **Puck.js**, Pixl.js, **MDBT42Q breakout**, Bangle.js, Jolt.js; an **Eagle library for the MDBT42 part** | Eagle (at least for MDBT42) | "see LICENSE" — not named on the repo page |
| **Bitcraze Loco deck** (lane C) | `loco_deck_revd.pdf` only | PDF, drawn in KiCad 4.0.2 | CC-BY 4.0 |
| **PineTime** | "PineTime Schematic ver1.0a" + GPIO port assignment | **PDF only, no PCB files**, no OSHW licence statement on the wiki | unstated |
| `ruuvi/ruuvitag_fw` | firmware + board-support headers only — **no hardware files** | — | — |

**Not one of them publishes the RF section as a drop-in block.** Espruino comes closest by shipping a
*part library* for the MDBT42Q; Ruuvi comes closest by shipping a *complete competing board* you can
copy from. The gap GOAL.md points at is real.

---

## 4. Antenna integration rules for a block that moves into someone else's outline

### 4.1 The physics that makes this hard, in three sourced sentences
1. **A printed quarter-wave antenna is tuned by the whole board it sits on.** TI AN043 measured the same
   IFA at *"approximately 250 MHz"* bandwidth in free space and *"around 100 MHz"* once the dongle was
   plugged into a laptop ground plane (<https://www.ti.com/lit/an/swra117d/swra117d.pdf>).
2. **A chip antenna does not escape this** — it only moves the dependence into a π-network. TI AN058:
   *"the performance and required matching will change if the chip antenna is implemented on a PCB with
   different size and shape of the ground plane"*; Johanson's own datasheet says *"The matching values
   and topology on client's PCB will be different."*
3. **Therefore the antenna must be inside a fixed, self-contained ground plane that travels with the
   block.** That is precisely what a certified module is, and it is also why 47 CFR 15.212(a)(1)(iv)
   says *"All single or split modular transmitters are approved with an antenna"* and *"The antenna must
   either be permanently attached or employ a 'unique' antenna coupler"*.

### 4.2 The keep-out rule, harmonised across five vendors
| vendor | rule as written |
|---|---|
| **Espressif** | antenna outside the base board; feed point at the edge; if not, cut the base board on both sides and below; **never centre-and-hollow-four-sides**; ground copper + dense vias nearby; **≥ 15 mm clearance in all directions inside the housing** |
| **Raytac** | *"No Ground Pad should be included in the corresponding position of the antenna in **EACH LAYER**. Place the module towards the edge of PCB…"* — and Raytac will review your layout PDF free |
| **Minew** | *"There should be no GND plane or metal cross wiring in the module antenna area, and components should not be placed nearby. It is best to make a hollow or clear area, or place it on the edge of the PCB board."* (its note 3, "4 square meter", is a mistranslation — do not use that number) |
| **Insight SiP** | a dimensioned rectangle: *"no metal, no traces and no components on any application PCB layer except mechanical LGA pads"*, **18.0 mm min × 4.0 mm** to the board edge |
| **Raspberry Pi** | Pico W cut-out **14 mm × 9 mm**; *"placed on the edge of a board and not enclosed in metal to avoid creating a Faraday cage. Adding ground to the sides of the antenna improves the performance slightly."* |

**The single rule halo should publish** (it is the intersection of all five, and it survives any host
outline): *the module's antenna end must sit on the host board's outline; a rectangle 16 mm wide × 6 mm
deep measured from that edge must be free of copper, traces and components on **every** layer; the host
must pour ground and stitch vias on the other three sides of the module; and the enclosure must give the
antenna ≥ 15 mm of clear space in all directions.* (16 × 6 mm is sized to cover the 15.2 × 5.7 mm that
TI AN043 needs for a small IFA and the 5.94 mm-deep antenna area of ESP32-WROOM-32; it is a halo
choice, not a vendor number.)

### 4.3 Chip vs PCB vs module antenna — the trade table
| | PCB (etched IFA/MIFA) | chip antenna | module with its own antenna |
|---|---|---|---|
| BOM cost | **$0** | **$0.10–$0.50** (TI AN058) + matching parts + placement | $4–$7 (the whole radio) |
| tuning travels with the block? | **no** — retunes with every host outline | **no** — π-network must be re-derived per host | **yes** |
| host must do RF layout? | yes, exactly (AN043: *"strongly recommended to make an exact copy of the reference design"*, import the gerber/DXF, same laminate thickness) | yes (50 Ω feed line, π-network) | **no** |
| certification | host owns the whole radio approval | host owns the whole radio approval | **inherited**, host adds a label (§5) |
| efficiency (TI DN035, 2.4 GHz) | 68 % @ 15 × 6 mm, 80 % @ 26 × 8 mm | Johanson 2450AT18A100: 0.5 dBi peak / −0.5 dBi average | as measured by the module vendor |
| size cost on the host | 15 × 6 mm of dead board | 3.2 × 1.6 mm part + a no-ground region (Johanson's EVB uses 6.5 × 6.5 mm) | 10 × 16 mm of module |

**For a block that must land in an arbitrary outline, only the third column keeps its promise.**

### 4.4 NFC — the one part that *cannot* live in the module
The NFC-A coil's inductance is set by turns and enclosed area, both properties of the host outline.
ST AN2866 gives the target and the arithmetic: `L_ant = 31.33 · µ0 · N² · a² / (8a + 11c)` for a spiral;
K1/K2 = 2.34/2.75 (square), 2.25/3.55 (octagonal), 2.33/3.82 (hexagonal); and the required inductance is
a function of the chip's Ctun (ST25TA: 2.58 µH @ 50 pF, 4.70 µH @ 27.5 pF). Tuning must then be
**measured** — network analyser, or an ISO standard loop plus an oscilloscope (AN2866 §5).

Consequence: **halo-core exposes NFC1/NFC2 and ships a parametric coil generator plus a stated target
inductance and the measurement procedure — it does not ship a fixed coil.** Lane C already found the
tooling: `nideri/nfc_antenna_generator` (parametric spiral for KiCad) and RuuviTag's working NFC-A coil
under CC BY-SA 4.0. **The nRF52840/nRF52832 target inductance is not verified in this lane** — Nordic's
docs (docs.nordicsemi.com) returned 403 to every automated fetch attempt. That is a work item, not a
guess (§7).

---

## 5. What modular certification actually buys, and what it does not

Read the full rule in `research/fetched/I-fcc-15-212-modular-transmitters.md`
(47 CFR § 15.212, eCFR, read 2026-09-03).

The eight requirements for **single modular approval** — the module must have (i) **its own shielding**,
(ii) buffered modulation/data inputs, (iii) **its own power supply regulation**, (iv) a **permanently
attached antenna or a "unique" antenna coupler**, (v) stand-alone testing, (vi) **a permanently affixed
FCC ID label or electronic display**, (vii) instructions to the integrator, (viii) an RF-exposure
statement.

Two clauses decide halo's architecture:

- **(a)(1)(iv)** — "All single or split modular transmitters are **approved with an antenna**. … The
  antenna must either be **permanently attached** or employ a 'unique' antenna coupler." A module whose
  antenna is on the module is approved *as a unit*, so **soldering it into a different host outline does
  not disturb the radio grant** — which is exactly the property GOAL.md needs.
- **(a)(1)(vi)(A)** — "if the FCC identification number is not visible when the module is installed
  inside another device, then the outside of the device into which the module is installed **must also
  display a label** … 'Contains Transmitter Module FCC ID: XYZMODEL1'". Raytac writes this into its own
  datasheet §9.10.1: *"The final end product must be labeled in a visible area with the following:
  'Contain FCC ID: SH6MDBT42Q'."*

So the honest statement to put in halo's README is: **the radio approval is inherited; the host still
owns the label, the Part 15B unintentional-radiator compliance of its own board, and the RF-exposure
statement in its final configuration.** Nothing here removes CE/RED, DULT or battery-shipping duties —
lane F owns those.

**What self-certifying a bare-SoC halo-core would require**: a shield can over the radio (i), its own
regulation (iii), a permanently attached antenna (iv), an FCC ID, and a stand-alone test campaign (v).
**No verified dollar figure for that campaign was obtained this session** — do not quote one. What *is*
verified is that SparkFun did it once and the resulting module retails at **$9.95** with FCC/IC/CE ID
2ASW8-ART3MIS, versus **$4.95 @1 / $0.90 @1000** for buying somebody else's.

---

## 6. Recommendation — three artefacts

### 6.1 Artefact 1 — `halo-core` as a KiCad 10 design block *(do this first, it costs nothing)*
```
hardware/halo.kicad_blocks/
  halo-core.kicad_block/
    halo-core.kicad_sch     # the whole tag: radio, accel, sounder drive, battery, NFC ports
    halo-core.kicad_pcb     # the layout fragment: placement + routing + the antenna keep-out on dwgs.user
    halo-core.json          # description, keywords, default fields
```
- Registered in the **project** design block library table in the repo, so a `git clone` + one library
  table entry is the whole install; and in a user's **global** table if they want it everywhere.
- **Flat, no subsheets** — KiCad refuses to save a block containing hierarchical sheet symbols.
- Placed with **`Place as sheet` + `Place as group`**: the sheet gives the host a black box with named
  ports; the group is what makes **`Apply Design Block Layout`** legal in the PCB editor, which is how
  the routed RF section arrives in a stranger's board without being redrawn.
- Ship a second, hierarchical-sheet copy (`hardware/sheets/halo-core.kicad_sch`) for anyone on KiCad 9
  or earlier, and say plainly in the README that it carries **no copper**.
- Licence CERN-OHL per GOAL.md; note that the two nearest precedents (SparkFun, Ruuvi) both chose
  CC BY-SA 4.0 — lane F owns the final call.

### 6.2 Artefact 2 — the `halo-core` castellated module, 15 × 20 mm

**Construction, v1: a carrier for a Raytac MDBT42Q.** Argued, not assumed:

| criterion | MDBT42Q (v1) | bare nRF52832 + etched IFA (v2 candidate) |
|---|---|---|
| NFC1/NFC2 documented as exposed pins | **yes**, pads 22/23 | yes (they are SoC pins) |
| RF layout risk to halo | **none** | the whole thing |
| FCC/IC/CE/MIC/KC/SRRC/NCC | **inherited**, ID SH6MDBT42Q, label wording in the datasheet | must be earned; needs shield, regulation, campaign |
| host board keep-out burden | *"No Ground Pad … in EACH LAYER"* under a **chip** antenna, and place at the edge | full IFA keep-out + laminate-thickness matching (AN043) |
| verified unit price | **$4.95 @1** (Digi-Key marketplace, +$25 shipping); MS88SF3-class volume floor **$0.900 @1000** | bare **nRF52832-QFAA-R $2.644 @1000** (LCSC C77540, 29 868 in stock) — lane E's price pull, `research/fetched/E-lcsc-price-pull-2026-09-03.md` |
| footprint availability | Raytac publish footprint + 2D/3D + reflow profile + external-32.768 kHz spec | must be drawn |
| free layout review | **yes** — *"Welcome to send us your layout in PDF for review at sales@raytac.com"* | no |
| proven in this application | Espruino Puck.js uses MDBT42Q; the AirTag itself is nRF52832 (lane C) | — |

**The cost crossover, with only verified numbers.** Lane E's LCSC pull (2026-09-03) gives the bare
silicon: **nRF52832-QFAA-R $2.644 @1000** (C77540, 29 868 in stock), nRF52833-QIAA-R $3.7527 @1000,
nRF52840-QIAA-R $4.1407 @100. A pre-certified nRF52832 module at Fanstel's **$4.46 @1k** (BT832) is
therefore roughly **$1.8/unit** more than the bare chip — before the crystal, the matching network, the
shield can and the antenna the bare chip still needs, and before any certification. At the other end,
Minew's **MS88SF3 at $0.900 @1000** is *cheaper than the bare nRF52840 it contains*, which is a
distributor-inventory artefact rather than a durable price, and it was out of stock. **Conclusion: at
halo's volumes there is no cost case for a bare-SoC module at all.** The bare-SoC route only becomes
interesting if the block must shrink below ~10 × 15 mm, which is a mechanical argument, not a cost one.

**Verdict: use the pre-certified module for v1.** The two things halo is actually trying to sell —
"anyone can drop this in" and "it undercuts $29" — are both better served by inheriting a $4.95
certified radio than by spending the project's first six months on an antenna and a test lab. Revisit a
bare-SoC v2 only when (a) volume is real and (b) MS88SF3-class pricing ($0.900 @1000) is in stock, at
which point the crossover arithmetic can be done against a real quote instead of a guess.

**Physical spec**
- Outline **15.0 × 20.0 mm**, 4 layers, 0.8 mm thick (so a host's 1.6 mm board + module stays under
  3.2 mm before the coin cell).
- **24 castellated pads, 1.27 mm pitch, 0.6 mm plated half-holes**, 12 per long edge, spanning
  13.97 mm centred on each 20 mm side → ≥ 3.0 mm clear at both corners.
  Clears JLCPCB (≥0.5 mm hole, ≥0.5 mm gap, ≥1 mm to edge) and PCBWay (≥0.4 mm, ≥0.3 mm).
- Host land pattern **1.8 × 0.9 mm pads with 0.5 mm outward extension** (Minew's published rule), so
  every joint gets an inspectable fillet.
- **Both short edges carry no pads**: one is the antenna end (must be flush with the host outline), the
  other is where a host puts its coin-cell holder or transducer.
- Ship, like SparkFun does: the module's own source, a **STEP + STL** for the host's 3D view, and a host
  footprint with **castellation pads *and* a matching top-side pad row** (Raspberry Pi's dual-option
  trick) so SWD gets a redundant joint.
- Keep-out drawn on **`dwgs.user`**, because KiCad footprints have no keep-out layer, plus the sentence
  from §4.2 in the README, plus a check (§6.5).

### 6.3 Proposed pin list — 24 pads, with the reason for each

Pin 1 at the antenna-end of the left edge, numbering counter-clockwise (KiCad/IPC convention).

| pad | name | nRF52 function | why it is here |
|---|---|---|---|
| 1 | **GND** | — | corner anchor. ISP1807's datasheet makes the mechanical case: pads exist *"for mechanical stability and reliability (drop test)"*. Also the RF return closest to the antenna. |
| 2 | **VBAT** | VDD, 1.8–3.6 V | straight from a CR2032. No regulator on the module — the nRF52's own DC/DC does the work; a regulator would burn quiescent current a coin cell cannot spare. |
| 3 | **NFC1** | P0.09/NFC1 | the host's coil. Adjacent to 4 because it is a **differential pair** and must be routed as one. |
| 4 | **NFC2** | P0.10/NFC2 | as above. Placed at the VBAT end so the coil can run around the host outline without crossing the digital escape. |
| 5 | GND | — | return between the NFC pair and the sounder drive; stops the 13.56 MHz pair coupling into a PWM edge. |
| 6 | **SND_A** | PWM ch0 | piezo drive, phase A. |
| 7 | **SND_B** | PWM ch1 | piezo drive, **anti-phase** — doubles the swing across the transducer without a boost converter, so no inductor and no extra BOM line. The transducer itself stays on the host, because it is a mechanical part matched to the host's cavity (lane C: AirTag's diaphragm *is* the shell). |
| 8 | GND | — | return for the two highest-di/dt pins on the module. |
| 9 | **IO0 / AIN** | P0.02–P0.05 class | general host I/O, ADC-capable so a host can read a battery divider or its own sensor with no ADC of its own. Remappable to **SPI SCK** for a DW3000 host (§1.3). |
| 10 | **IO1 / AIN** | " | as above; remappable to **SPI MOSI**. |
| 11 | **IO2** | " | as above; remappable to **SPI MISO**. |
| 12 | GND | — | corner anchor. |
| 13 | GND | — | corner anchor (opposite edge). |
| 14 | **nRESET** | P0.21/RESET | grouped with 15/16 so a **Tag-Connect TC2030** footprint on the host is a straight, crossing-free escape — 6 pads, ~0.02 in², no connector, $33.95 of one-off tooling for the developer and $0 per board. |
| 15 | **SWDCLK** | SWDCLK | " |
| 16 | **SWDIO** | SWDIO | " |
| 17 | GND | — | shields the SWD group from the LED/button pins and gives the TC2030 its ground pad. |
| 18 | **LED** | GPIO (sink) | host status LED; Find My / DULT both want a visible indicator. |
| 19 | **BTN_n** | GPIO, internal pull-up | host button — pairing, sound-on-demand, DULT disable. Internal pull-up means the host adds **zero** parts. |
| 20 | GND | — | return. |
| 21 | **INT** | GPIO with sense | the on-module accelerometer's interrupt, brought out so a host can also use it as its own IRQ line. Remappable to **DW3000 IRQ**. |
| 22 | **SCL** | TWI SCL | the module's *own* accelerometer bus, exposed so a host sensor board joins the existing bus instead of needing a second one. Remappable to **SPI CSn**. |
| 23 | **SDA** | TWI SDA | " Remappable to **DW3000 RSTn**. |
| 24 | GND | — | corner anchor. |

**Totals: 8 GND, 16 signal/power.** Ground on all four corners and never more than three signals
between grounds — that is what makes a **2-layer host board** routable, which is the Artemis lesson
(*"routing to the module can be done with low-cost 2-layer PCBs with 8mil trace/space"*).

What is deliberately **on** the module: nRF52832 (as MDBT42Q), 32.768 kHz crystal, accelerometer,
decoupling. What is deliberately **off**: the coin cell and its holder, the NFC coil, the transducer,
the LED, the button, the enclosure. Every off-module item is one whose value is set by the host's shape
— which is the whole point of the split.

Because every nRF52 GPIO is function-remappable, **the same 24 pads become a UWB host** by re-tasking
9/10/11/21/22/23 as SCK/MOSI/MISO/IRQ/CSn/RSTn. No second module variant is needed for lane H's DW3000
work; the firmware pinmap changes and the pads do not.

### 6.4 Artefact 3 — the round puck as first host, and it is expressible in ce-pcb today
Measured 2026-09-03 on this machine: `ce-pcb/bin/pcb --doctor` → **exit 0**, kicad-cli/pcbnew **10.0.6**,
15450 footprints; `ce-pcb/bin/board doctor` → **exit 0**, *"kernel-free verbs … run today / kernel verbs
build validate export publish — run today"*.

What ce-pcb already supports, read from the code:
- **Arbitrary outlines including the 32 mm circle** — `cepcb.circle_outline(diameter, center, segments)`
  and `Board(name, w, h, outline=…, layers=…)` (`ce-pcb/cepcb/board.py:39, :79–111`). The puck is a
  one-liner; so is any customer's odd shape.
- **Placement by footprint id** — `Board.place(ref, fpid, at, rot, side)` (`:148`). So `part:halo-core`
  needs a `cad/pcb_land.kicad_mod` on the shelf (`ce-parts/SCHEMA.md` v2.4 b), which `board sync` then
  reads for pads (`ce-pcb/docs/boards.md` §4).
- **Copper pours on an explicit polygon** — `Board.pour(net, layer, outline=…)` (`:401`). This is how the
  antenna keep-out gets expressed **negatively**: pour ground over a polygon that excludes the 16 × 6 mm
  antenna rectangle, on every layer.
- Tracks, vias, routing by pad reference, netclass rules, `confirm(ref, cite)`, DRC → a `sim` ledger row,
  gerber export → an `export` row (`docs/boards.md` §6).

Two gaps, both **P11 "improve the core"** items rather than reasons to work around ce-pcb:
1. **No keep-out / rule-area primitive.** `grep` over `ce-pcb/cepcb/*.py` finds none (measured
   2026-09-03). KiCad itself has rule areas; `Board.pour()` can only *avoid* a region, and nothing checks
   that the host actually did. **Proposal: `Board.keepout(polygon, layers, why)`** that writes a KiCad
   rule area *and* a `dwgs.user` outline, plus a `board check` rule that FAILs when a placed
   `part:halo-core` has copper inside its declared antenna rectangle. That check is the thing that
   makes the keep-out real instead of a sentence in a README — and it is exactly the defect Raspberry Pi
   describe and then have to fix by hand.
2. **No hierarchical sheets and no design blocks.** `cepcb.schematic.Schematic` is documented as
   *"A one-sheet schematic"* (`ce-pcb/cepcb/schematic.py:222`), and at `:437` it raises when a sheet
   outgrows A0 with the advice *"Split it into hierarchical sheets"* — a thing it cannot do.
   `grep -rl "kicad_blocks\|design_block" ce-pcb/cepcb ce-pcb/bin` → **nothing**.
   **Proposal: `cepcb.blocks` — read a `.kicad_blocks/<name>.kicad_block/` directory, place its
   `.kicad_sch` as a subsheet and apply its `.kicad_pcb` fragment to the matching footprint group**,
   so a halo design block is usable from a ce-pcb `board.py` and not only from the KiCad GUI.

### 6.5 The three checks that make the block real
A block whose keep-out is only prose will be violated. Each of these is a PASS/FAIL/CANNOT DETERMINE
check, in the ce-workshop sense:
1. **antenna keep-out** — no copper, no track, no footprint courtyard inside the declared 16 × 6 mm
   rectangle on any layer, and the rectangle's outer edge coincident with the host `Edge.Cuts`.
   CANNOT DETERMINE if the host board declares no antenna rectangle.
2. **module escape routability** — every one of the 16 signal pads reaches a host net on ≤ 2 layers at
   ≥ 0.2 mm/0.2 mm; this is the promise Artemis makes and halo must keep.
3. **NFC coil inductance** — the generated coil's computed inductance (AN2866 §4.1/4.2) is inside the
   band the SoC needs, and the ledger carries a **measured** resonance, not a computed one. Until the
   nRF52 target inductance is verified (§7), this check reports CANNOT DETERMINE by name, never a pass.

---

## 7. Open questions this lane could not close (work items, not questions for Leif)
1. **Nordic's own antenna / reference-layout / NFC-coil guidance.** `docs.nordicsemi.com` and
   `docs-be.nordicsemi.com` returned **403** to every automated fetch (5 URLs tried). The nRF52832/52840
   NFC-A target coil inductance and Nordic's "copy the reference layout exactly" wording are therefore
   **unverified here**. Get them from a manual download of the nRF52840 Product Specification.
2. **Does MS88SF2/SF3 expose NFC1/NFC2?** Its datasheet pin table names only P0.02–P0.31 / P1.00–P1.09.
   Ask Minew, or read the module's own reference schematic (§6 of its datasheet is a figure).
   This decides whether the $0.900 @1000 part is a candidate at all.
3. **ISP1807 and BL654 prices.** Mouser timed out twice, everythingrf 403, Ezurio prints `$0.00000`.
4. **Holyiot 21014** — not reached. **Ebyte E73 certification IDs and prices** — the vendor publishes
   neither.
5. **Cost of self-certifying a bare-SoC module** (FCC + IC + CE/RED + BQB). No verified figure; do not
   quote one until a test house quotes it.
6. **Tag-Connect TC2030 pad geometry** — the product page gives only "0.02 sq inch"; take the real
   dimensions from Tag-Connect's footprint drawing before laying out.
7. **DWM3000 / DWM3001C dimensions and price** — `www.qorvo.com` is blocked from here. Lane H owns it.

---

## 8. Files this lane wrote
- `research/09-embeddable-block-and-modules.md` (this file)
- `research/fetched/I-esp32-hardware-design-guidelines-keepout.md`
- `research/fetched/I-kicad-design-blocks.md`
- `research/fetched/I-fcc-15-212-modular-transmitters.md`
- `research/fetched/I-sparkfun-artemis-open-castellated-module.md`
- `research/fetched/I-rp2040-pico-as-a-solder-down-module.md`
- `research/fetched/I-nrf52-module-datasheet-extracts.md`
- `research/fetched/I-antenna-and-nfc-app-notes.md`
- `research/fetched/I-castellation-fab-rules-and-pinout-standards.md`
- appended to `research/sources.tsv` and `reference/CLONE-LIST.tsv`
