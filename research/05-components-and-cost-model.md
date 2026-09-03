# 05 — Components and cost model

**Lane E. All prices pulled 2026-09-03.** Every number below carries a link and a date.
Where a price could not be fetched it says so; nothing here is invented.

How the prices were obtained (so anyone can re-run them):

- **LCSC** — HTTP GET on `https://www.lcsc.com/product-detail/<code>.html`; the page ships a
  `__NEXT_DATA__` blob containing `productPriceList` (the full qty ladder), `stockNumber` and
  `minPacketNumber`. Raw dump: [`research/fetched/E-lcsc-price-pull-2026-09-03.md`](fetched/E-lcsc-price-pull-2026-09-03.md).
- **JLCPCB parts library** — HTTP POST on
  `https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`
  with `{"keyword": ...}`; returns `componentPrices`, `stockCount` and `componentLibraryType`
  (`base` = Basic part, `expand` = Extended part). Raw dump:
  [`research/fetched/E-jlcpcb-search-2026-09-03.md`](fetched/E-jlcpcb-search-2026-09-03.md).
- **Digi-Key / Qorvo store** — page fetch, quoted verbatim in
  [`research/fetched/E-uwb-and-datasheet-specs.md`](fetched/E-uwb-and-datasheet-specs.md).

> **Two traps in the JLCPCB data.** A JLCPCB price of `$0.0395 / $0.0203` or `$0.0007 / $0.0003`
> on a part with `stockCount: 0` is a **placeholder**, not a price. Every such row is excluded
> from the tables below. And a JLCPCB "Extended" part costs an extra **$3.07 feeder fee per
> distinct part per order** — which at 10 units matters more than the part itself.

Machine-readable version of every candidate table: [`spec/bom-candidates.json`](../spec/bom-candidates.json).

---

## 1. The substitution map — what Apple used, what we can buy

The AirTag chip list is settled by three independent teardowns that agree:
[iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks),
[Adam Catley](https://adamcatley.com/AirTag.html) and
[TechInsights](https://www.techinsights.com/blog/apple-airtag-teardown) (all fetched 2026-09-03;
copies in `research/fetched/`).

| # | AirTag function | Apple's exact part | Sourceable equivalent (the pick) | LCSC/JLC | @100 | @1k | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | BLE SoC + NFC-A tag | **Nordic nRF52832** (WLCSP50) | **NRF52832-QFAA-R** (QFN48 6x6) | [C77540](https://www.lcsc.com/product-detail/C77540.html) | $2.8144 | $2.6440 | **exact silicon**, different package |
| 2 | UWB transceiver | **Apple U1** SiP (AirTag 2: **U2**) | **Qorvo DW3110TR13** | [DK 24717583](https://www.digikey.com/en/products/detail/qorvo/DW3110TR13/24717583) / [C3040882](https://www.lcsc.com/product-detail/C3040882.html) | $7.83 | $6.91 | functional stand-in only — see §4 |
| 3 | NFC front end | **none** — the nRF52832's own NFC-A peripheral, read-only MIFARE Plus Type 4 | same: on-chip NFC-A + PCB coil | — | $0 | $0 | **exact** |
| 4 | Accelerometer | **Bosch BMA280** | **ST LIS2DW12TR** | [C189624](https://www.lcsc.com/product-detail/C189624.html) | $0.8031 | $0.7408 | substitute (BMA280 unbuyable, see §3.4) |
| 5 | Speaker driver | **Maxim MAX98357AEWL** class-D | **MAX98357AEWL+T** | [C2682619](https://www.lcsc.com/product-detail/C2682619.html) | $0.3171 | $0.2534 | **exact part, in stock** |
| 6 | Speaker sense op-amp | **TI TLV9001IDPWR** | **TLV9001IDBVR** (SOT-23-5) | [C398363](https://www.lcsc.com/product-detail/C398363.html) | $0.0682 | $0.0604 | **same die**, different package |
| 7 | Transducer | **custom voice coil** glued to the shell, driving it as a diaphragm | **Huaneng MLT-8530** magnetic transducer, or KLJ-8530-3627 at 86 dB | [C94599](https://www.lcsc.com/product-detail/C94599.html) | $0.1423 | $0.1137 | substitute — no one sells Apple's coil |
| 8 | External NOR flash | **GigaDevice GD25LE32D** 32 Mbit | **omit** (or Winbond W25Q32JW) | [C2456252](https://www.lcsc.com/product-detail/C2456252.html) | $1.1588 | $1.0654 | **drop it** — see §3.7 |
| 9 | Buck converter | **TI TPS62746** 300 mA | **none — run direct from the cell** | — | $0 | $0 | see §3.8 |
| 10 | OVP load switch | **ON Semi FPF2487** | not reproduced (no U1 rail to protect) | — | $0 | $0 | dropped with the U1 |
| 11 | Crystals | 32 MHz + 32.768 kHz | NX2016SA-32MHZ + X321532768KGD2SI | [C843260](https://www.lcsc.com/product-detail/C843260.html) / [C620155](https://www.lcsc.com/product-detail/C620155.html) | $0.2922 / $0.1888 | $0.2333 / $0.1347 | equivalent |
| 12 | Antennas (BLE/NFC/UWB) | three LDS antennas on one moulded plastic frame, soldered to the PCB edge | PCB trace antennas on a 4-layer board, chip antenna optional | [C89334](https://www.lcsc.com/product-detail/C89334.html) | $0 / $0.6321 | $0 / $0.5390 | substitute — LDS needs tooling |
| 13 | Battery | CR2032, ~0.66 Wh, user-replaceable | Panasonic CR2032 + SMD holder | [C7498149](https://www.lcsc.com/product-detail/C7498149.html) | $0.39 + $0.1611 | $0.39 + $0.1350 | **exact** |

The three parts that do **not** have a faithful copy are the U1, the voice coil and the LDS
antenna frame. Everything else in an AirTag is off-the-shelf — which is exactly what Catley
found: *"Uses off the shelf components, apart from Apple's U1 chip for UWB."*

---

## 2. The two variants (per DECISIONS.md D1)

| | **haytag-core** | **haytag-uwb** |
|---|---|---|
| radios | BLE only | BLE + Qorvo DW3110 |
| purpose | the open product anyone can build, sell or embed | Leif's sensor fleet ranging peer-to-peer into Twinton |
| SoC form | **pre-certified module preferred** (bare-SoC option costed too) | bare SoC — no pre-certified BLE+UWB module fits 30 mm |
| certification | modular approval under 47 CFR 15.212 (module) or full intentional-radiator test (bare SoC) | second radio regime on top; not a sold consumer product |

---

## 3. Candidate tables per function

Legend: **lib** = JLCPCB library type (basic = no feeder fee, ext = $3.07/order feeder fee).
**form** = bare SoC (you own the RF layout and the radio certification) vs module (vendor owns both).
Stock is LCSC stock at the moment of the pull unless the row says JLC.

### 3.1 BLE SoC — bare silicon

| Part | Pkg | Flash/RAM | NFC-A | TX @0 dBm | Sleep | LCSC/JLC | Stock | @1 | @100 | @1k | form |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **NRF52832-QFAA-R** | QFN48 6x6 | 512/64 kB | **yes** | 5.3 mA | 1.9 µA (ON+RTC), 0.3 µA (OFF) | [C77540](https://www.lcsc.com/product-detail/C77540.html) | 29 868 | $3.9936 | $2.8144 | $2.6440 | bare |
| nRF52810-QCAA-R | QFN32 5x5 | 192/24 kB | no | — | — | [C519278](https://www.lcsc.com/product-detail/C519278.html) | **0** | $3.1885 | $1.9808 | $1.7977 | bare |
| NRF52811-QFAA-R | QFN48 6x6 | 192/24 kB | no | — | — | [C556895](https://www.lcsc.com/product-detail/C556895.html) | 238 | $3.0927 | $2.1154 | $1.9367 | bare |
| nRF52833-QIAA-R | aQFN73 7x7 | 512/128 kB | yes | — | — | [C504799](https://www.lcsc.com/product-detail/C504799.html) | 5 377 | $5.9677 | $4.0955 | $3.7527 | bare |
| NRF52840-QIAA-R | aQFN73 7x7 | 1024/256 kB | yes | — | — | [C190794](https://www.lcsc.com/product-detail/C190794.html) | 51 240 | $5.8937 | $4.1407 | (no 1k break) | bare |
| **NRF54L15-QFAA-R** | QFN48 6x6 | 1.5 MB/256 kB | yes | 4.8 mA | 0.7–2.9 µA | [C42458750](https://jlcpcb.com/partdetail/NordicSemicon-NRF54L15_QFAAR/C42458750) (JLC) | **0** | $3.9798 | $2.7111 | $2.4791 | bare |
| CC2340R52E0RGER | VQFN24 4x4 | 512/64 kB | **no** | 5.1 mA | 710 nA standby, 165 nA shutdown | [C20416850](https://jlcpcb.com/partdetail/TexasInstruments-CC2340R52E0RGER/C20416850) (JLC) | 13 539 | $1.5721 | $1.0368 | $0.9378 | bare |
| EFR32BG22C224F512IM40-CR | QFN40 5x5 | 512/32 kB | no | 4.1 mA | 1.40 µA EM2 | [C1864136](https://www.lcsc.com/product-detail/C1864136.html) | 83 | $3.7697 | $2.6007 | $2.3854 | bare |
| DA14531-00000FX2 | FCGQFN24 2.2x3 | 144 kB ROM / 32 kB OTP / 48 kB RAM | no | 3.5 mA | — | [C509077](https://www.lcsc.com/product-detail/C509077.html) | 2 091 | $2.6273 | $1.8860 | $1.7504 | bare |
| TLSR8258F512ET32 | QFN32 5x5 | 512 kB | no | — | — | [C2836053](https://www.lcsc.com/product-detail/C2836053.html) | **0** | $5.8680 | (200) $2.2714 | $2.1527 | bare |
| PHY6222AAQC | QFN32 4x4 | — | no | — | — | [C2836482](https://www.lcsc.com/product-detail/C2836482.html) | **0** | $1.7501 | (200) $0.6788 | $0.6428 | bare |
| ESP32-C3FH4 | QFN32 5x5 | 4 MB/400 kB | no | — | ~5 µA class deep sleep | [C2858491](https://www.lcsc.com/product-detail/C2858491.html) | 5 000 | $2.1754 | $1.4976 | $1.3817 | bare |
| ESP32-H2FH4 | QFN32 4x4 | — | no | — | — | [C22470214](https://jlcpcb.com/partdetail/EspressifSystems-ESP32_H2FH4/C22470214) (JLC) | 3 441 | $2.2341 | $1.6776 | $1.5478 | bare |
| ESP32-C6 | QFN40 5x5 | — | no | — | — | [C5364646](https://jlcpcb.com/partdetail/EspressifSystems-ESP32_C6/C5364646) (JLC) | 764 | $2.6510 | $1.9485 | $1.7847 | bare |

Spec sources: [nRF52832 PS via LCSC](https://datasheet.lcsc.com/datasheet/pdf/1aa6d7c89b6eb7e9c334420a8d103737.pdf?productCode=C77540),
[nordicsemi.com/Products/nRF52832](https://www.nordicsemi.com/Products/nRF52832),
[nRF54L15](https://www.nordicsemi.com/Products/nRF54L15), [ti.com/product/CC2340R5](https://www.ti.com/product/CC2340R5),
[EFR32BG22](https://www.silabs.com/wireless/bluetooth/efr32bg22-series-2-socs),
[DA14531](https://www.renesas.com/en/products/wireless-connectivity/bluetooth-low-energy/da14531-smartbond-tiny-ultra-low-power-bluetooth-51-system-chip) — all fetched 2026-09-03.

**Firmware support today.** OpenHaystack ships firmware for **nRF51822 (micro:bit v1)** and
**ESP32** only ([README](https://github.com/seemoo-lab/openhaystack)); the community
[openhaystack-zephyr](https://github.com/koenvervloesem/openhaystack-zephyr) port runs on *any*
Zephyr-supported BLE part, which covers nRF52832/833/840, nRF54L15 and EFR32BG22;
[macless-haystack](https://github.com/dchristl/macless-haystack) ships prebuilt **nRF5x** and
**ESP32** images. CC2340, TLSR825x, PHY6222 and DA14531 have **no published Find-My firmware** —
picking one buys a cheaper BOM and a firmware project.

**Pick: nRF52832.** It is the only candidate that is simultaneously (a) Apple's own choice,
(b) NFC-A-capable so the tap-to-see-owner flow needs no extra chip, (c) supported by existing
Find-My firmware, and (d) in five-figure stock at LCSC. CC2340R5 is $1.68/unit cheaper at 1k and
is the part to revisit if the firmware effort is ever funded; it has no NFC, so it would add
~$0.33 of NT3H2111 back.

### 3.2 Pre-certified BLE modules (the haytag-core default form)

| Module | SoC | Size | Certs | JLC/LCSC | Stock | @1 | @100 | form |
|---|---|---|---|---|---|---|---|---|
| **E73-2G4M08S1C** | nRF52832 | 18 x 13 mm | **NOT VERIFIED — see below** | [C356849](https://jlcpcb.com/partdetail/ChengduEbyteElectronic-E73_2G4M08S1C/C356849) | 2 093 | $8.1607 | $5.9347 | module |
| MDBT50Q-P1MV2 | nRF52840 | 10.5 x 15.5 x 2.05 mm | FCC, IC, CE, **Telec (MIC) = Giteki**, KC, SRRC, NCC, RCM, WPC | [C5119772](https://jlcpcb.com/partdetail/RAYTAC-MDBT50Q_P1MV2/C5119772) | **0** | $7.8962 | — | module |
| DA14531MOD-00F01002 | DA14531 | LCC-16 14.5 x 12.5 mm | — | [C5360767](https://www.lcsc.com/product-detail/C5360767.html) | 557 | $5.7513 | $4.1610 | module |
| ESP32-C3-MINI-1-H4 | ESP32-C3 | 16.6 x 13.2 mm | — | [C2934569](https://www.lcsc.com/product-detail/C2934569.html) | 1 047 | $3.3573 | $2.6748 | module |

**Giteki flag (per lane F).** Raytac's [MDBT50Q-1MV2 page](https://www.raytac.com/product/ins.php?index_id=24)
(fetched 2026-09-03) lists *"FCC, IC, CE, Telec (MIC), KC, SRRC, NCC, RCM, WPC"* — Telec/MIC **is**
the Japanese Giteki mark, so a Raytac module clears Japan. Ebyte's
[E73-2G4M08S1C page](https://www.cdebyte.com/products/E73-2G4M08S1C) has a "Certifications"
heading but **rendered no certification content**, so its FCC/CE status is unverified and its
Giteki status is **unknown — flag it**. Raytac's own MDBT42Q (nRF52832) page could not be located
by index sweep; **its cert list was not fetched.**

**The module-vs-bare-SoC economics.** A module costs **+$3.12/unit at 100** and **+$2.90/unit at
1k** over the bare nRF52832 + crystals + matching + antenna it replaces (see §5). Against that it
removes the intentional-radiator test campaign: under 47 CFR 15.212 single modular approval the
module vendor holds the grant and the host inherits it. **No test-lab quote was fetched for this
lane**, so the crossover is stated as a break-even rather than a dollar figure: at a $3/unit
premium, the module pays for itself against any certification campaign costing more than
`$3 × units`. Below ~1 000 units the module is almost certainly cheaper overall; above ~5 000
units the bare SoC starts to win, *if* someone will own the test campaign. For an open design
where every downstream builder would otherwise have to certify their own board, the module is
the right default — which is what D1 already decided.

### 3.3 NFC

| Part | Pkg | Interface | LCSC | Stock | @1 | @100 | @1k |
|---|---|---|---|---|---|---|---|
| **on-chip NFC-A (nRF52832)** | — | read-only Type 4 tag | — | — | **$0** | **$0** | **$0** |
| NT3H2111W0FHKH | XQFN-8 1.6x1.6 | NTAG I2C plus | [C710403](https://www.lcsc.com/product-detail/C710403.html) | 53 047 | $0.6281 | $0.3838 | $0.3280 |
| NT2H1311F0DTLH (NTAG213) | HXSON-4 1.5x2 | passive NDEF | [C2654853](https://www.lcsc.com/product-detail/C2654853.html) | 103 | $1.1371 | $0.6927 | $0.6116 |
| NT3H2111W0FT1X | SO-8 | NTAG I2C plus | [C2654859](https://www.lcsc.com/product-detail/C2654859.html) | 17 | $1.9567 | $1.2740 | $1.1499 |
| ST25DV04K-JFR6D3 | UDFN-12 3x3 | ISO 15693 + I2C | [C2654815](https://www.lcsc.com/product-detail/C2654815.html) | 1 092 | $0.9135 | $0.5461 | $0.4641 |

NTAG213/216 **in wafer/die form** (NT2H1311G0DUDZ etc.) appears in the JLCPCB catalogue only with
placeholder prices at zero stock — **no real die price was obtained**. Die is a
sticker-inlay format anyway; a puck wants the packaged part or the SoC's own radio.

The coil is PCB copper: a 3–5 turn spiral on the outer layers tuned with 2 caps. Free in parts,
costly in board area — the reason the AirTag put it on a separate LDS frame.

### 3.4 Accelerometer

| Part | Pkg | Low-power current | LCSC | Stock | @1 | @100 | @1k |
|---|---|---|---|---|---|---|---|
| **BMA280 (Apple's part)** | LGA-12 2x2 | — | [C189508](https://www.lcsc.com/product-detail/C189508.html) | **29**, min packet 10 000 | $2.7365 | $2.6044 | no break |
| **LIS2DW12TR (pick)** | LGA-12 2x2 | <1 µA low-power / 90 µA HR | [C189624](https://www.lcsc.com/product-detail/C189624.html) | 14 651 | $1.1947 | $0.8031 | $0.7408 |
| LIS2DH12TR | LGA-12 2x2 | ~2 µA | [C110926](https://www.lcsc.com/product-detail/C110926.html) | 297 | $0.9670 | $0.6507 | $0.5999 |
| BMA400 | LGA-12 2x2 | 160 nA (LCSC parametric) | [C437655](https://www.lcsc.com/product-detail/C437655.html) | **0** (JLC 113) | $3.7147 | $2.6240 | $2.4493 |
| BMA456 | LGA-12 2x2 | — | [C189518](https://www.lcsc.com/product-detail/C189518.html) | 2 839 | $4.9012 | $3.4679 | $3.2065 |
| MC3635 | LGA-10 1.6x1.6 | — | [C3040827](https://jlcpcb.com/partdetail/MEMSIC-MC3635/C3040827) (JLC) | **0** | $2.1027 | $1.9940 | no break |

Apple's BMA280 is a **dead end for a clone**: 29 pieces in stock and a 10 000-piece minimum
packet. LIS2DW12 is the closest functional match — same 2x2 LGA-12 land pattern, same
motion/wake interrupt engine, sub-1 µA, one third the price, and 14 651 in stock. BMA400 is the
lowest-power part on the list and is worth a second look if 160 nA ever matters more than $1.70.

### 3.5 Sound

The AirTag makes sound by gluing a **copper voice coil to the plastic shell** and driving it
against a magnet nested in the donut PCB — the shell *is* the diaphragm (iFixit, Catley).
There is no purchasable equivalent, and **no absolute dB figure for the AirTag has been
published** — Apple only says AirTag 2 is *"50% louder"*
([apple.com/airtag](https://www.apple.com/airtag/), 2026-09-03). Do not quote "~60 dB": we
could not source it. iFixit's own comparison is the useful data point: *"the piezoelectric
speakers in competing products like the Tile Mate and SmartTag made just as much, if not more,
noise"* — so an off-the-shelf transducer costs timbre, not loudness.

| Transducer | Type | SPL | Size | LCSC | Stock | @1/5 | @100/150 | @1k |
|---|---|---|---|---|---|---|---|---|
| **MLT-8530** | magnetic, passive | **80 dB** | 8.5x8.5 mm | [C94599](https://www.lcsc.com/product-detail/C94599.html) | 74 575 | $0.2095 | $0.1423 | $0.1137 |
| KLJ-8530-3627 | magnetic, passive | **86 dB** | 8.5x8.5 mm | [C189206](https://www.lcsc.com/product-detail/C189206.html) | 4 478 | $0.5770 | $0.3344 | $0.2754 |
| MLT-7525 | magnetic | 80 dB | 7.5x7.5 mm | [C95299](https://www.lcsc.com/product-detail/C95299.html) | 33 840 | $0.2388 | $0.1594 | $0.1361 (500) |
| MLT-5020 | magnetic | not stated | 5x5 mm | [C94598](https://www.lcsc.com/product-detail/C94598.html) | 34 915 | $0.4397 | $0.2541 | $0.1971 |
| KLJ-1102 | piezo | 70 dB | 9x11 mm | [C201047](https://www.lcsc.com/product-detail/C201047.html) | 535 | $0.4966 | $0.3822 | $0.3561 |
| custom voice coil (Apple) | electrodynamic | — | — | — | — | **no price fetched** | | |

Driver: keep **MAX98357AEWL+T** ([C2682619](https://www.lcsc.com/product-detail/C2682619.html),
$0.3171@100 / $0.2534@1k, 6 494 in stock) — it is literally Apple's part, it is a bridge-tied
class-D output so it swings ±Vbat into the load without a boost, and it takes I²S straight from
the nRF52832. The AirTag's **TLV9001** op-amp is the *feedback* path Apple used to sense the coil;
the SOT-23-5 version is [C398363](https://www.lcsc.com/product-detail/C398363.html) at
$0.0604@500. Keep it only if the design senses the transducer to detect a sabotaged speaker
(Catley's suggested anti-tamper measure); a magnetic transducer with no sense path can drop it.

### 3.6 Clocks, antenna, RF

| Part | Function | LCSC | Stock | @5/1 | @150/100 | @500 | @3k/1k |
|---|---|---|---|---|---|---|---|
| NX2016SA-32MHZ-STD-CZS-5 | 32 MHz, 2016 | [C843260](https://www.lcsc.com/product-detail/C843260.html) | 12 690 | $0.3534 | $0.2660 | $0.2333 | $0.2187 |
| X321532768KGD2SI | 32.768 kHz, 3215 | [C620155](https://www.lcsc.com/product-detail/C620155.html) | 6 010 | $0.2475 | $0.1602 | $0.1347 | $0.1279 |
| NX3215SA-32.768K-STD-MUA-8 | 32.768 kHz, NDK | [C156245](https://www.lcsc.com/product-detail/C156245.html) | 17 115 | $0.2724 | $0.1917 | $0.1615 | $0.1481 |
| K2C384001010 | **38.4 MHz for DW3000** | [C409422](https://jlcpcb.com/partdetail/KYX-K2C384001010/C409422) | 585 | $0.1627 | $0.1128 | $0.0941 | $0.0858 |
| 2450AT18A100E | 2.4 GHz chip antenna, 1206 | [C89334](https://www.lcsc.com/product-detail/C89334.html) | 6 578 | $1.0289 | $0.6321 | $0.5618 | $0.5390 |
| AH316M245001-T | 2.4 GHz chip antenna, 1206 | [C3285031](https://www.lcsc.com/product-detail/C3285031.html) | 1 513 | $0.7599 | $0.5007 | $0.4618 | $0.4423 |
| 2450BM15A0002E | balun/filter 2x1.3 mm | [C114062](https://www.lcsc.com/product-detail/C114062.html) | 167 | $0.9775 | $0.6381 | $0.5108 | $0.4847 |
| ACS5200HFAUWB | **UWB chip antenna** 8x6 mm | [C224424](https://jlcpcb.com/partdetail/Partron-ACS5200HFAUWB/C224424) | **0** | $1.2233 | $0.7788 | $0.6571 | $0.6312 |
| CL05B104KO5NNNC | 0402 100 nF, **JLC Basic** | [C1525](https://www.lcsc.com/product-detail/C1525.html) | 6 842 900 | $0.0051 | — | — | $0.0039 (1k), $0.0026 (100k) |

The 38.4 MHz crystal above is a **price-class placeholder**: its ppm and load capacitance have
not been checked against Qorvo's DW3000 requirement. Do not order it on this table's authority.

A **PCB trace antenna costs $0** and is what the roll-up assumes; the chip antennas are priced so
the embeddable-block variant (lane I) can trade $0.44–0.63 for keep-out area on a host board.

### 3.7 Flash — the part to delete

Apple carried a 32 Mbit GD25LE32D because the U1 needs firmware, the sound assets need storage
and there are ARM64 instructions in that image the nRF52832 cannot even execute (Catley).
haytag needs none of that: OpenHaystack-class firmware plus the key set fits comfortably in the
nRF52832's 512 kB. **Deleting the flash saves $1.06–1.45 and 8 solder joints.** If it is ever
needed: GD25LE32ESIGR [C7281238](https://www.lcsc.com/product-detail/C7281238.html) ($1.4539@100,
37 in stock) or Winbond W25Q32JWSSIQ TR [C2456252](https://www.lcsc.com/product-detail/C2456252.html)
($1.1588@100, 11 903 in stock).

### 3.8 Power

Apple used a **TPS62746 buck** and an **FPF2487 OVP switch** because the U1 and the 1.8 V flash
needed rails a coin cell cannot hold. haytag-core has neither, and the nRF52832's supply range is
**1.7–3.6 V** — the whole useful life of a CR2032, and Catley measured the AirTag itself powering
up from 2 V. So **haytag-core runs straight off the cell: no regulator, $0, and no quiescent
current to pay for.**

haytag-uwb does need help: DW3110 draws 14–23 mA in bursts and the DW3000 datasheet's own DC
table qualifies single-frame TX/RX **"with 47uF capacitor"**. Budget a 47 µF bulk cap and, if the
UWB rail is switched, TPS7A0233PDBVR [C2887324](https://www.lcsc.com/product-detail/C2887324.html)
($0.3587@100 / $0.3341@1k, 5 649 in stock). The Apple buck TPS62746YFPR
[C2072479](https://www.lcsc.com/product-detail/C2072479.html) is $0.7387@100 but **LCSC stock 0**.

### 3.9 Battery and contacts

Panasonic **CR2032**: **225 mAh**, 3 V, 20.0 x 3.2 mm, **$0.39000 at qty 1**, 1 204 333 in stock
at [Digi-Key](https://www.digikey.com/en/products/filter/coin-button-cell-batteries/90)
(2026-09-03). **Volume price breaks for the cell were not fetched** — the filter page exposed only
the qty-1 price and the direct product URLs tried returned the wrong part or 404. Every roll-up
below therefore carries $0.39 for the cell at *all* quantities, which is an **upper bound**;
real 10 k pricing will be materially lower. LCSC does not stock CR2032 cells at all (only
holders and contacts).

| Contact | Type | LCSC/JLC | Stock | @1/5 | @500 | @2.5k/5k |
|---|---|---|---|---|---|---|
| **BS-CR2032-8** | SMD holder | [C7498149](https://www.lcsc.com/product-detail/C7498149.html) | 10 300 | $0.2328 | $0.1350 | $0.1163 |
| CR2032-BS-6-1 | THT holder | [C70377](https://jlcpcb.com/partdetail/-CR2032BS61/C70377) | 36 697 | $0.1380 | (1k) $0.1079 | $0.1039 |
| XDBS-CR2032-5 | THT holder | [C48687404](https://www.lcsc.com/product-detail/C48687404.html) | 12 315 | $0.1225 | $0.0755 | $0.0642 |
| **CR2032 bent contact** | stamped spring | [C70373](https://jlcpcb.com/partdetail/-CR2032BentBatteryContact/C70373) | 26 364 | $0.0495 | (300) $0.0331 | **$0.0241 @10k** |

The bent stamped contact is both the cheapest ($0.0241 at 10 k) and the closest to Apple's
method — a spring against a cell held by the shell. It only works once there is a moulded shell
to retain the cell, and D3 (Reese's Law) requires that shell to be a press-and-twist bayonet.

---

## 4. UWB: the honest verdict

**Can a non-Apple UWB chip do Apple Precision Finding?** The path exists but it is not open to
this project.

- Qorvo announced in July 2022 that its **DW3110** was awarded **MFi certification for Apple U1
  interoperability**, so accessory makers can integrate it and use Apple's Nearby Interaction
  ([Qorvo newsroom, 2022-07-20](https://www.qorvo.com/newsroom/news/2022/qorvo-uwb-solutions-certified-for-apple-u1-interoperability)).
  Qorvo's own product page for DW3110 returned HTTP 429 on direct fetch on 2026-09-03.
- Apple's own [Find My network accessory page](https://developer.apple.com/find-my/) says only:
  *"enroll in the MFi Program to access the technical specifications and resources needed to
  create your product."* No chipset list, no UWB detail, nothing usable without the NDA.
- So the sequence for real Precision Finding is: MFi membership → NDA → Find My Network
  accessory spec → per-product certification. **That NDA is structurally incompatible with
  publishing the design**, which is why D1 sends UWB to a separate variant used tag-to-tag.
- AirTag 2 (Feb 2026) moved to **Apple U2**
  ([iFixit via 9to5Mac](https://9to5mac.com/2026/02/05/ifixit-tears-down-new-airtag-finds-50-louder-speaker-still-100-easy-to-disable/)),
  so even a licensed DW3110 accessory is chasing a moving target.

**What DW3000 does give haytag-uwb for free:** two-way ranging between haytags, with no Apple
involvement at all. Prices and power (all fetched 2026-09-03, full quotes in
[`E-uwb-and-datasheet-specs.md`](fetched/E-uwb-and-datasheet-specs.md)):

| Part | Pkg | @1 | @100 | @1k | @3k–4k | Stock | Notes |
|---|---|---|---|---|---|---|---|
| **DW3110TR13** (Digi-Key) | 52-UFBGA WLCSP | $10.31 | $7.83 | $6.91 | $5.84 | 7 406 | MFi U1-interop cert; 33-week factory lead time |
| DW3110TR13 (LCSC) | WLCSP | $10.2268 | $7.2316 | — | — | 27 | cheaper at 100 than Digi-Key, but 27 in stock |
| DW3120TR13 | 52-UFBGA WLCSP | $11.28 | $9.23 | $7.22 | $6.15 | 1 822 | **two RX ports → angle of arrival**, not just range |
| DW1000-I-TR13 (LCSC) | QFN48 6x6 | $7.8901 | $5.5332 | — | — | 6 861 | cheapest, hand-solderable QFN, but no 802.15.4z, no Apple interop, worse sleep |
| DWM3001C module | 27 x 19.13 mm | $59.37 | $43.18 | — | — | 32 | DW3110 + nRF52833 + antenna + accel, pre-certified; too big for a 30 mm puck |

**DW3110 power** (datasheet Table 5, 3.0 V): deep sleep **260 nA**, sleep **850 nA**,
IDLE ch5 **18 mA**, single-frame **TX ch5 14 mA / RX ch5 16 mA**, peak continuous TX 23–29 mA.

**What that does to a CR2032.** Baseline BLE-only draw, using nRF52832's 1.9 µA System-ON-with-RTC,
~1 µA for the accelerometer in low-power mode, 0.5 µA of leakage, and ~13 µC per 3-channel
advertising event:

| Duty cycle | Average current | CR2032 (225 mAh) life |
|---|---|---|
| advertise every 5 s | 6.0 µA | **4.3 years** |
| advertise every 2 s (AirTag-like) | 9.9 µA | **2.6 years** |
| advertise every 1 s | 16.4 µA | 1.6 years |
| + UWB range every 5 min | 10.6 µA | **2.4 years** |
| + UWB range every 60 s | 12.2 µA | **2.1 years** |
| + UWB range every 10 s | 22.2 µA | **1.2 years** |
| + UWB range every 1 s | 130 µA | **0.2 years** |

Method: one two-way-ranging exchange is charged at ~120 µC (≈5 ms of RX/TX at 14–18 mA plus
~2 ms of oscillator/PLL wake), advertising at 2 s. These are **derived estimates from the
datasheet currents above, not measurements** — lane H should replace them with bench numbers.
The engineering conclusion is robust though: **UWB ranging up to about once a minute is free on
a coin cell; once a second is not.** For a static sensor fleet in a digital twin, once a minute
is plenty — positions do not move.

The second constraint is not energy but **impedance**: a CR2032 has 10–15 Ω fresh and far more
when aged, so a 23 mA pulse drops hundreds of millivolts. That is exactly why Qorvo qualifies
its own single-frame numbers *"with 47uF capacitor"*. The 47 µF bulk cap is not optional.

---

## 5. The BOMs

### 5.1 haytag-core, module form (the shipping default)

| Ref | Part | LCSC/JLC | Qty | @100 ea | @100 ext |
|---|---|---|---|---|---|
| M1 | E73-2G4M08S1C (nRF52832 module, incl. antenna + crystals) | C356849 | 1 | $5.9347 | $5.9347 |
| U2 | LIS2DW12TR accelerometer | C189624 | 1 | $0.8031 | $0.8031 |
| U3 | MAX98357AEWL+T class-D driver | C2682619 | 1 | $0.3171 | $0.3171 |
| LS1 | MLT-8530 magnetic transducer | C94599 | 1 | $0.1423 | $0.1423 |
| BT1 | BS-CR2032-8 holder | C7498149 | 1 | $0.1611 | $0.1611 |
| — | 14 x 0402 passives (C1525 proxy) | C1525 | 14 | $0.0039 | $0.0546 |
| BAT1 | Panasonic CR2032 (qty-1 price, upper bound) | — | 1 | $0.39 | $0.39 |
| | **BOM subtotal @100** | | | | **$7.85** |

### 5.2 haytag-core, bare-SoC form

| Ref | Part | LCSC | Qty | @100 ea | @100 ext |
|---|---|---|---|---|---|
| U1 | NRF52832-QFAA-R | C77540 | 1 | $2.8144 | $2.8144 |
| Y1 | NX2016SA 32 MHz | C843260 | 1 | $0.2922 | $0.2922 |
| Y2 | X321532768KGD2SI 32.768 kHz | C620155 | 1 | $0.1888 | $0.1888 |
| U2 | LIS2DW12TR | C189624 | 1 | $0.8031 | $0.8031 |
| U3 | MAX98357AEWL+T | C2682619 | 1 | $0.3171 | $0.3171 |
| LS1 | MLT-8530 | C94599 | 1 | $0.1423 | $0.1423 |
| BT1 | BS-CR2032-8 | C7498149 | 1 | $0.1611 | $0.1611 |
| — | 22 x 0402 (decoupling, pi-match, NFC tuning) | C1525 | 22 | $0.0039 | $0.0858 |
| ANT1 | PCB trace antenna | — | 1 | $0 | $0 |
| BAT1 | CR2032 (upper bound) | — | 1 | $0.39 | $0.39 |
| | **BOM subtotal @100** | | | | **$5.24** |

### 5.3 haytag-uwb (bare SoC + DW3110)

Everything in 5.2, plus:

| Ref | Part | Source | @100 ea |
|---|---|---|---|
| U4 | DW3110TR13 | Digi-Key | $7.83 |
| Y3 | 38.4 MHz crystal (placeholder) | C409422 | $0.1128 |
| ANT2 | ACS5200HFAUWB UWB chip antenna | C224424 (JLC, **stock 0**) | $0.7788 |
| U5 | TPS7A0233PDBVR UWB rail LDO | C2887324 | $0.3587 |
| — | +12 passives incl. 47 µF bulk | C1525 proxy | $0.0396 |
| | **BOM subtotal @100** | | **$14.36** |

---

## 6. Cost roll-up at 10 / 100 / 1 000 / 10 000

**PCB model.** 30 mm round, 4-layer, 1.0 mm, ENIG. Nine boards panelised on a 100 x 100 mm
panel. JLCPCB's published 4-layer rate is **$70.60 per m²** with a worked example of 100 pcs of
100 x 100 mm = **$70.60 board / $106.30 total**
([JLCPCB, 2024-03-06](https://jlcpcb.com/news/discount-on-quality-4-layer-pcbs)), so the
non-area charges on that order were **$35.70**. Model: `PCB(qty) = $35.70 + $25 ENIG adder +
panels x $0.706`. The $25 ENIG adder is an **estimate** — JLCPCB does not publish a surface-finish
line item, and no live quote could be pulled (their quote endpoint is not reachable without the
browser client; PCBWay's page returns *"Please click on Calculate to show price"*).

**Assembly model.** JLCPCB Economic PCBA published fees
([help article](https://jlcpcb.com/help/article/pcb-assembly-price), 2026-09-03): setup **$8.18**,
stencil **$1.53**, **$0.0016 per joint**, **$3.07 per Extended part** feeder fee, **$0.48/board**
minimum (avoided by panelising). Joint counts: core-module 95, core-bare 130, uwb 220.

**Enclosure and labour are estimates, not fetched prices** — see §7.

| Variant | Qty | BOM | PCB | Assembly | Enclosure | Tooling amort. | Labour | **Total/unit** |
|---|---|---|---|---|---|---|---|---|
| **haytag-core (module)** | 10 | $9.64 | $6.211 | $2.965 | $1.20 | $0 | $0.30 | **$20.32** |
| | 100 | $7.85 | $0.692 | $0.433 | $1.20 | $0 | $0.30 | **$10.47** |
| | 1 000 | $7.61 | $0.140 | $0.180 | $0.90 | $0 | $0.15 | **$8.98** |
| | 10 000 | $7.58 | $0.085 | $0.155 | $0.30 | $0.80 | $0.08 | **$9.00** |
| **haytag-core (bare SoC)** | 10 | $6.51 | $6.211 | $3.328 | $1.20 | $0 | $0.30 | **$17.55** |
| | 100 | $5.24 | $0.692 | $0.520 | $1.20 | $0 | $0.30 | **$7.95** |
| | 1 000 | $4.71 | $0.140 | $0.239 | $0.90 | $0 | $0.15 | **$6.14** |
| | 10 000 | $4.64 | $0.085 | $0.211 | $0.30 | $0.80 | $0.08 | **$6.12** |
| **haytag-uwb** | 10 | $17.17 | $6.211 | $4.700 | $1.20 | $0 | $0.30 | **$29.58** |
| | 100 | $14.36 | $0.692 | $0.787 | $1.20 | $0 | $0.30 | **$17.34** |
| | 1 000 | $12.71 | $0.140 | $0.395 | $0.90 | $0 | $0.15 | **$14.30** |
| | 10 000 | $11.56 | $0.085 | $0.356 | $0.30 | $0.80 | $0.08 | **$13.18** |

Caveats that inflate every 10 000-unit row:

1. **Most LCSC ladders stop at 1 000–6 000.** The 10 000 column reuses the deepest published
   break, so it is an **upper bound**; real 10 k pricing needs a quote.
2. **The CR2032 is carried at its qty-1 price of $0.39** at every quantity because volume breaks
   were not fetched. At a realistic bulk price of ~$0.12 the 10 k rows drop by ~$0.27.
3. **JLCPCB's fee schedule is a prototype-house schedule.** Nobody builds 10 000 units there;
   a real CM quote replaces both the PCB and the assembly line.

### Against Apple

| | per unit |
|---|---|
| AirTag, 1-pack retail | **$29.00** ([apple.com](https://www.apple.com/shop/buy-airtag/airtag), 2026-09-03) |
| AirTag, 4-pack retail | **$24.75** ($99.00 / 4, same source) |
| AirTag estimated manufacturing cost | **~$10** ([TechInsights](https://www.techinsights.com/blog/apple-airtag-teardown): *"estimated manufacturing cost of USD 10 (not including software costs and R&D)"*) |
| haytag-core, module, 1 000 | **$8.98** |
| haytag-core, bare SoC, 1 000 | **$6.14** |
| haytag-uwb, 1 000 | **$14.30** |

So: **haytag-core at 1 000 units lands at 21–31 % of AirTag's retail price and roughly at or
below Apple's own estimated build cost** — while dropping the U1, the 32 Mbit flash, the buck
converter and the LDS antenna frame. Even at 100 units the module build ($10.47) undercuts the
4-pack price per tag. The one place Apple is unbeatable is the enclosure: their moulding and
LDS tooling is amortised over tens of millions of units, and it is the enclosure, not the
silicon, that keeps the 10 000-unit row from falling below $6.

haytag-uwb never competes on price with an AirTag and is not meant to: at $14.30 it buys
peer-to-peer ranging that an AirTag cannot do at all, because Apple's UWB only talks to Apple.

---

## 7. Enclosure and final assembly — where the numbers are weakest

**This section contains the least-sourced figures in the document. Treat them as estimates.**

- **Injection moulding.** Xometry's guide
  ([xometry.com](https://www.xometry.com/resources/injection-molding/injection-molding-cost/),
  2026-09-03) gives tooling *"up to $10,000"* for mid-level orders of 1 000–2 000 small parts and
  *"$10,000 or less to $100,000"* overall, material at **0.90–2.30 USD/lb**, and notes cycle time
  is *"about 60% of final part cost"*. It publishes **no per-part price**. The roll-up assumes a
  **$8 000 two-cavity tool for the shell pair** and a **$0.30 piece price** — both derived, both
  unverified.
- **Steel back plate.** The AirTag's stainless back is a stamped part. **No quote obtained.**
- **3D-printed alternative** for the 10 / 100 rows: **no price fetched** — JLC3DP's quote page
  renders `Total Price: --` without an uploaded model. The $1.20/unit used is an estimate for a
  resin-printed two-part shell.
- **Snap-fit is ruled out anyway** by D3: 16 CFR 1263 requires a tool or two simultaneous hand
  movements to open a coin-cell compartment, so the shell must be a press-and-twist bayonet or a
  screw-down lid.
- **Final assembly labour**: $0.30/unit at 10–100, $0.15 at 1 000, $0.08 at 10 000 — estimates
  based on roughly one minute of manual work per unit at low volume; **no labour rate was fetched.**

Getting real numbers here is the single highest-leverage follow-up for this lane: the enclosure
is 4–13 % of the module build at 1 000 units but is the dominant uncertainty at 10 000.

---

## 8. What this lane recommends

1. **haytag-core ships on the E73-2G4M08S1C module** — but only after its FCC/CE/Giteki
   certificates are obtained from Ebyte. If they do not exist, switch to a **Raytac MDBT42Q/
   MDBT50Q**, which demonstrably holds *"FCC, IC, CE, Telec (MIC), KC, SRRC, NCC, RCM, WPC"*,
   and accept roughly $1.50–2/unit more and a Digi-Key/Mouser supply line instead of JLCPCB.
2. **Publish the bare-SoC BOM alongside it.** It is $2.90/unit cheaper at 1 k and it is the
   version that goes into someone else's board — but it hands them the radio certification.
3. **Keep Apple's part where Apple's part is cheap and available**: nRF52832, MAX98357A, TLV9001,
   CR2032. Substitute only where forced: BMA280 → LIS2DW12, voice coil → MLT-8530, LDS antenna →
   PCB trace.
4. **Delete the external flash and the buck converter.** They existed for the U1 and the 1.8 V
   rail; neither survives into haytag-core. That is $1.80–2.20/unit and 16 joints gone.
5. **haytag-uwb uses DW3110TR13 with a 47 µF bulk cap**, ranging **no faster than once a minute**
   on a CR2032, and buys the UWB antenna from Digi-Key/Mouser because JLCPCB's ACS5200HFAUWB
   stock is zero. If lane H shows Bluetooth Channel Sounding on **nRF54L15** reaches useful
   accuracy, the whole DW3110 line item — $6.91 of silicon plus antenna, crystal, LDO and 12
   passives, about **$8.20/unit at 1 k** — disappears, and haytag-uwb collapses back into
   haytag-core with a different SoC. That is the single biggest cost lever in this document.
6. **Do not quote a dB figure for the AirTag speaker.** None is published.

## 9. Open items this lane could not close

| Item | Why | Who should close it |
|---|---|---|
| CR2032 cell price at 100/1k/10k | Digi-Key filter page exposed only the qty-1 price; product URLs 404'd | re-pull, or quote a cell vendor |
| PCB quote for the actual 30 mm round 4-layer board | JLCPCB/PCBWay quote engines need the browser client and a board file | run it once the board exists |
| ENIG surface-finish adder | not a published JLCPCB line item | same quote |
| Injection-mould tooling and piece price | Xometry publishes no per-part price | one RFQ to a Shenzhen moulder |
| FCC/CE/Giteki test-lab cost | no lab price fetched; needed to price the module-vs-bare-SoC crossover | lane F |
| Ebyte E73 certification status | Ebyte's page renders no certification content | ask Ebyte for the cert PDFs |
| Raytac MDBT42Q (nRF52832) certification list and price | page not found by index sweep; LCSC stock 0 | Raytac / Digi-Key |
| 38.4 MHz crystal spec match for DW3000 | picked on price class only | lane H with the DW3000 app notes |
| NTAG die/wafer pricing | JLCPCB shows placeholders on zero stock | only matters if an inlay format is wanted |
| Ranging energy per two-way exchange | derived from datasheet currents, not measured | lane H on the bench |
