# 05 — Components and cost model

> **SUPERSEDED IN PART BY §10–§11.** Decision **D12** (2026-09-03) drops the DW3110 chain and
> makes **nRF54L10** the v1 SoC, superseding D10's nRF52840. Sections 1–9 below remain the record
> of the AirTag substitution map and the nRF52/UWB costing that D12 was decided against — kept
> deliberately visible, because they are the option the nRF54L baseline beat and the delta in
> §10.3 is only meaningful against them. **§10 is the current cost model. §11 is its
> verification**: every §10 price re-pulled live, plus the answer to lane I's module question and
> seven corrections to §10 (see the table in §11.5). Lane G has since settled the sounder as a
> bare **Murata 7BB-20-3** piezo bender bonded to the shell, and lane A confirmed **LIS2DW12TR**
> as the accelerometer.
>
> **Read in this order if you only want the current answer: §10.1 → §10.3 → §11.1 → §11.3.**

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

The AirTag chip list comes from lane A's dossier, [`research/01-airtag-hardware.md`](01-airtag-hardware.md),
which read the part markings off full-resolution board photographs, corroborated by three
independent teardowns that agree:
[iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks),
[Adam Catley](https://adamcatley.com/AirTag.html) and
[TechInsights](https://www.techinsights.com/blog/apple-airtag-teardown) (all fetched 2026-09-03;
copies in `research/fetched/`). Where lane A and a teardown disagree, lane A's marking wins.

`*` = no price break published beyond 100 pieces at pull time (LCSC $4.1407 @100; JLCPCB listed $4.0966 @100 for the same code).

| # | AirTag function | Apple's exact part | Sourceable equivalent (the pick) | LCSC/JLC | @100 | @1k | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | BLE SoC + NFC-A tag | **Nordic nRF52832-CIAA** (WLCSP) — lane A read the marking | **NRF52840-QIAA-R** (aQFN73 7x7) — parity target per D10 | [C190794](https://www.lcsc.com/product-detail/C190794.html) | $4.1407 | $4.1407* | **upgrade**, see note |
| 1b | (gen-1 exact silicon, for reference) | nRF52832-CIAA | NRF52832-QFAA-R (QFN48 6x6) | [C77540](https://www.lcsc.com/product-detail/C77540.html) | $2.8144 | $2.6440 | exact die, different package |
| 2 | UWB transceiver | **Apple U1** SiP (AirTag 2: **U2**) | **Qorvo DW3110TR13** | [DK 24717583](https://www.digikey.com/en/products/detail/qorvo/DW3110TR13/24717583) / [C3040882](https://www.lcsc.com/product-detail/C3040882.html) | $7.83 | $6.91 | functional stand-in only — see §4 |
| 3 | NFC front end | **NO CHIP** — the Nordic SoC's own NFC-A peripheral drives the coil from **P0.09 / P0.10** (lane A) | same: on-chip NFC-A + PCB coil + 2 tuning caps | — | **$0** (+2 x $0.0029) | **$0** | **exact — this BOM line does not exist** |
| 4 | Accelerometer | **Bosch BMA280** | **ST LIS2DW12TR** | [C189624](https://www.lcsc.com/product-detail/C189624.html) | $0.8031 | $0.7408 | substitute (BMA280 unbuyable, see §3.4) |
| 5 | Speaker driver | **Maxim MAX98357AEWL** class-D | **MAX98357AEWL+T** | [C2682619](https://www.lcsc.com/product-detail/C2682619.html) | $0.3171 | $0.2534 | **exact part, in stock** |
| 6 | Speaker sense op-amp | **TI TLV9001IDPWR** | **TLV9001IDBVR** (SOT-23-5) | [C398363](https://www.lcsc.com/product-detail/C398363.html) | $0.0682 | $0.0604 | **same die**, different package |
| 7 | Transducer | **custom voice coil** glued to the shell, driving it as a diaphragm | **Huaneng MLT-8530** magnetic transducer, or KLJ-8530-3627 at 86 dB | [C94599](https://www.lcsc.com/product-detail/C94599.html) | $0.1423 | $0.1137 | substitute — no one sells Apple's coil |
| 8 | External NOR flash | **GigaDevice GD25LE32 / GD25LQ32** 32 Mbit SPI NOR (lane A) | **omit** (or GD25LQ32EEIGR) | [C2939873](https://jlcpcb.com/partdetail/GigaDeviceSemiconductor-GD25LQ32EEIGR/C2939873) | $0.7301 | $0.4105 | **drop it** — see §3.7 |
| 9 | Buck converter | **TI TPS62746** 300 mA | **none — run direct from the cell** | — | $0 | $0 | see §3.8 |
| 10 | OVP load switch | **onsemi FPF2487** | **not in the LCSC/JLCPCB catalogue at all** — searched 2026-09-03, zero hits | — | no price | no price | dropped with the U1 |
| 10b | Bulk energy store | **five 100 uF capacitors** (lane A) | TCC0805X5R107M6R3FT x5 | [C49215609](https://www.lcsc.com/product-detail/C49215609.html) | 5 x $0.3574 | 5 x $0.3082 | equivalent — see §3.10 |
| 11 | Crystals | 32 MHz + 32.768 kHz | NX2016SA-32MHZ + X321532768KGD2SI | [C843260](https://www.lcsc.com/product-detail/C843260.html) / [C620155](https://www.lcsc.com/product-detail/C620155.html) | $0.2922 / $0.1888 | $0.2333 / $0.1347 | equivalent |
| 12 | Antennas (BLE/NFC/UWB) | three LDS antennas on one moulded plastic frame, soldered to the PCB edge | PCB trace antennas on a 4-layer board, chip antenna optional | [C89334](https://www.lcsc.com/product-detail/C89334.html) | $0 / $0.6321 | $0 / $0.5390 | substitute — LDS needs tooling |
| 13 | Battery | CR2032, ~0.66 Wh, user-replaceable | Panasonic CR2032 + SMD holder | [C7498149](https://www.lcsc.com/product-detail/C7498149.html) | $0.39 + $0.1611 | $0.39 + $0.1350 | **exact** |

The three parts that do **not** have a faithful copy are the U1, the voice coil and the LDS
antenna frame. Everything else in an AirTag is off-the-shelf — which is exactly what Catley
found: *"Uses off the shelf components, apart from Apple's U1 chip for UWB."*

---

## 2. The two variants (per DECISIONS.md D1)

| | **halo-core** | **halo-uwb** |
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

**Parity target is nRF52840-class, not nRF52832 (DECISIONS.md D10).** Apple's gen-1 die is an
**nRF52832-CIAA**; the second-generation AirTag moved up, and DULT behaviour plus a Google Find
Hub beacon plus the Find My stack together need the headroom. So the roll-up costs
**nRF52840-QIAA-R**, and the nRF52832 row stays in the table as the gen-1 reference and as the
cheaper option for a build that only ever speaks Find My.


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

**Pick: nRF52840-QIAA-R** (D10). It is the only candidate that is simultaneously (a) the
parity target, (b) NFC-A-capable so the tap-to-see-owner flow needs no extra chip at all,
(c) supported by existing Find-My firmware through the Zephyr port, (d) big enough (1 MB flash)
to delete the external NOR, and (e) in 51 240-piece LCSC stock. Its costs are the 7x7 aQFN73
footprint — large on a 30 mm board — and a price ladder that stops at 100 pieces.

**Second choice: nRF52832-QFAA-R**, the gen-1 exact die, $1.50/unit cheaper at 1k in a smaller
QFN48. Take it if the build only ever needs Find My and not the DULT + Find Hub headroom D10 is
protecting. **Third: CC2340R5**, $3.20/unit cheaper than nRF52840 at 1k with real stock — but no
NFC (add ~$0.33 of NT3H2111) and no published Find-My firmware, so it buys a firmware project.

### 3.2 Pre-certified BLE modules (the halo-core default form)

| Module | SoC | Size | Certs | JLC/LCSC | Stock | @1 | @100 | form |
|---|---|---|---|---|---|---|---|---|
| **E73-2G4M08S1C** | **nRF52840** | 18 x 13 mm | **NOT VERIFIED — see below** | [C356849](https://jlcpcb.com/partdetail/ChengduEbyteElectronic-E73_2G4M08S1C/C356849) | 2 093 | $8.1607 | $5.9347 | module |
| MDBT50Q-P1MV2 | nRF52840 | 10.5 x 15.5 x 2.05 mm | FCC, IC, CE, **Telec (MIC) = Giteki**, KC, SRRC, NCC, RCM, WPC | [C5119772](https://jlcpcb.com/partdetail/RAYTAC-MDBT50Q_P1MV2/C5119772) | **0** | $7.8962 | — | module |
| DA14531MOD-00F01002 | DA14531 | LCC-16 14.5 x 12.5 mm | — | [C5360767](https://www.lcsc.com/product-detail/C5360767.html) | 557 | $5.7513 | $4.1610 | module |
| E73-2G4M04S1B | nRF52832 | 28.7 x 17.5 mm | not verified | [C411306](https://jlcpcb.com/partdetail/ChengduEbyteElectronic-E73_2G4M04S1B/C411306) | 180 | $5.4107 | $4.9386 | module |
| ESP32-C3-MINI-1-H4 | ESP32-C3 | 16.6 x 13.2 mm | — | [C2934569](https://www.lcsc.com/product-detail/C2934569.html) | 1 047 | $3.3573 | $2.6748 | module |

**Which SoC is in the Ebyte module?** Confirmed by reading the JLCPCB part page HTML on
2026-09-03: **E73-2G4M08S1C contains an nRF52840** (the "08" is its +8 dBm TX, which nRF52832
cannot reach), and **E73-2G4M04S1B contains an nRF52832**. So the module already on the
shortlist happens to hit D10's nRF52840 parity target.

**Giteki flag (per lane F).** Raytac's [MDBT50Q-1MV2 page](https://www.raytac.com/product/ins.php?index_id=24)
(fetched 2026-09-03) lists *"FCC, IC, CE, Telec (MIC), KC, SRRC, NCC, RCM, WPC"* — Telec/MIC **is**
the Japanese Giteki mark, so a Raytac module clears Japan. Ebyte's
[E73-2G4M08S1C page](https://www.cdebyte.com/products/E73-2G4M08S1C) has a "Certifications"
heading but **rendered no certification content**, so its FCC/CE status is unverified and its
Giteki status is **unknown — flag it**. Raytac's own MDBT42Q (nRF52832) page could not be located
by index sweep; **its cert list was not fetched.**

**The module-vs-bare-SoC economics.** The E73 module costs **+$1.31/unit at 100** and
**+$1.40/unit at 1k** over the bare nRF52840 + two crystals + matching + antenna it replaces
(see §5) — a much narrower gap than at nRF52832 parity, because the aQFN73 nRF52840 is itself
$4.10. Against that it
removes the intentional-radiator test campaign: under 47 CFR 15.212 single modular approval the
module vendor holds the grant and the host inherits it. **No test-lab quote was fetched for this
lane**, so the crossover is stated as a break-even rather than a dollar figure: at a $3/unit
premium, the module pays for itself against any certification campaign costing more than
`$3 × units`. Below ~1 000 units the module is almost certainly cheaper overall; above ~5 000
units the bare SoC starts to win, *if* someone will own the test campaign. For an open design
where every downstream builder would otherwise have to certify their own board, the module is
the right default — which is what D1 already decided.

### 3.3 NFC — the BOM line that does not exist

Lane A read the board: **there is no NFC front-end IC in an AirTag.** The Nordic SoC's own NFC-A
peripheral drives the coil directly from **P0.09 and P0.10**. The entire NFC cost is therefore
**one PCB coil (copper, $0) and two tuning capacitors (2 x $0.0029 at 1k = $0.006)**. That is the
single largest structural saving available to any clone, and it is free because we already chose
an NFC-A-capable Nordic part.

The discrete NFC ICs below are priced only as the **fallback if a non-NFC SoC is ever chosen**
(CC2340R5, EFR32BG22, DA14531 all lack NFC-A). None of them appears in the halo BOM.

| Part | Pkg | Interface | LCSC | Stock | @1 | @100 | @1k |
|---|---|---|---|---|---|---|---|
| **on-chip NFC-A (nRF52832/40) — what Apple does** | — | read-only MIFARE Plus Type 4 | — | — | **$0** | **$0** | **$0** |
| NT3H2111W0FHKH | XQFN-8 1.6x1.6 | NTAG I2C plus | [C710403](https://www.lcsc.com/product-detail/C710403.html) | 53 047 | $0.6281 | $0.3838 | $0.3280 |
| NT2H1311F0DTLH (NTAG213) | HXSON-4 1.5x2 | passive NDEF | [C2654853](https://www.lcsc.com/product-detail/C2654853.html) | 103 | $1.1371 | $0.6927 | $0.6116 |
| NT3H2111W0FT1X | SO-8 | NTAG I2C plus | [C2654859](https://www.lcsc.com/product-detail/C2654859.html) | 17 | $1.9567 | $1.2740 | $1.1499 |
| ST25DV04K-JFR6D3 | UDFN-12 3x3 | ISO 15693 + I2C | [C2654815](https://www.lcsc.com/product-detail/C2654815.html) | 1 092 | $0.9135 | $0.5461 | $0.4641 |

NTAG213/216 **in wafer/die form** (NT2H1311G0DUDZ etc.) appears in the JLCPCB catalogue only with
placeholder prices at zero stock — **no real die price was obtained**. Die is a
sticker-inlay format anyway; a puck wants the packaged part or the SoC's own radio.

The coil is PCB copper: a 3–5 turn spiral on the outer layers, tuned with two capacitors on
P0.09/P0.10. Free in parts, costly in board area — the reason the AirTag put its coil on a
separate LDS frame rather than on the PCB.

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
There is no purchasable equivalent. **Apple publishes no dB figure** — only that AirTag 2 is
*"50% louder"* ([apple.com/airtag](https://www.apple.com/airtag/), 2026-09-03). Lane G found the
one real measurement: iFixit measured AirTag 1 at **about 78–80 dB** at roughly one
iPhone-Mini-length, and lane G's own acoustics work
([`research/fetched/G-acoustics-cells-and-holders.md`](fetched/G-acoustics-cells-and-holders.md))
is the authority on this, not this lane. The useful read-across for costing is that an 80 dB
magnetic transducer is in the right class and an 86 dB one is above it — but buzzer datasheet dB
is quoted at 10 cm, which is not iFixit's distance, so **do not compare the two numbers
directly.** iFixit's own comparison is the useful data point: *"the piezoelectric
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

Lane A read the marking as **GigaDevice GD25LE32 or GD25LQ32, 32 Mbit SPI NOR**. Apple carried it
because the U1 needs firmware, the sound assets need storage, and there are ARM64 instructions in
that image the nRF52832 cannot even execute (Catley). halo needs none of that: OpenHaystack-class
firmware plus the key set fits inside the **nRF52840's 1 MB**. **Deleting the flash saves
$0.41–1.45 and 8 solder joints.**

If it is ever needed, in ascending price at 1k:

| Part | Pkg | LCSC/JLC | Stock | @100 | @1k |
|---|---|---|---|---|---|
| GD25LQ32EEIGR | USON-8-EP 2x3 | [C2939873](https://jlcpcb.com/partdetail/GigaDeviceSemiconductor-GD25LQ32EEIGR/C2939873) | 3 001 | $0.7301 | **$0.4105** |
| GD25LQ32DSIG | SOIC-8 | [C6626515](https://jlcpcb.com/partdetail/GigaDeviceSemiconductor-GD25LQ32DSIG/C6626515) | 0 | $0.5922 (200) | $0.5630 |
| GD25LQ32ESIGR | SOIC-8 | [C2928890](https://jlcpcb.com/partdetail/GigaDeviceSemiconductor-GD25LQ32ESIGR/C2928890) | 425 | $0.8972 | $0.6020 |
| W25Q32JWSSIQ TR | SOIC-8 | [C2456252](https://www.lcsc.com/product-detail/C2456252.html) | 11 903 | $1.1588 | $1.0654 |
| GD25LE32ESIGR | SOIC-8 | [C7281238](https://www.lcsc.com/product-detail/C7281238.html) | 37 | $1.4539 | no break |

**GD25LQ32EEIGR is the pick if flash comes back** — same family as Apple's, USON-8 2x3 mm, 3 001
in stock, $0.41 at 1k.

### 3.8 Power

Apple used a **TPS62746 buck** and an **onsemi FPF2487 OVP load switch** (both confirmed by lane
A off the board photos) because the U1 and the 1.8 V flash
needed rails a coin cell cannot hold. halo-core has neither, and the Nordic supply range —
**1.7–3.6 V** on nRF52832, **1.7–5.5 V** on nRF52840 — covers the whole useful life of a CR2032;
Catley measured the AirTag itself powering up from 2 V. So **halo-core runs straight off the
cell: no regulator, $0, and no quiescent current to pay for.** What it does need instead is the
bulk capacitance of §3.10.

halo-uwb does need help: DW3110 draws 14–23 mA in bursts and the DW3000 datasheet's own DC
table qualifies single-frame TX/RX **"with 47uF capacitor"**. Budget a 47 µF bulk cap and, if the
UWB rail is switched, TPS7A0233PDBVR [C2887324](https://www.lcsc.com/product-detail/C2887324.html)
($0.3587@100 / $0.3341@1k, 5 649 in stock). The Apple buck TPS62746YFPR
[C2072479](https://www.lcsc.com/product-detail/C2072479.html) is $0.7387@100 but **LCSC stock 0**.

**FPF2487 is not in the LCSC or JLCPCB catalogue at all** — a keyword search of the JLCPCB parts
API on 2026-09-03 returned zero results. **No price could be fetched for it.** It does not matter:
its job was to protect the U1's rail, and halo-core has no U1.

### 3.10 Bulk capacitance — the line Apple needs and so do we

Lane A counted **five 100 uF capacitors** on the AirTag board. That is not decoration: a CR2032
has 10-15 ohm of internal resistance fresh and far more when aged, so every milliamp of pulse
current turns into millivolts of droop. Apple's ~500 uF is what lets a coin cell drive a voice
coil and a UWB transmitter without browning out the SoC.

| Part | Pkg | LCSC | Stock | @100 | @1k | 5x @1k |
|---|---|---|---|---|---|---|
| **TCC0805X5R107M6R3FT** | 0805 100 uF 6.3 V | [C49215609](https://www.lcsc.com/product-detail/C49215609.html) | 11 262 | $0.3574 | $0.3082 | **$1.54** |
| CGA0805X5R107M6R3MT | 0805 100 uF 6.3 V | [C23692977](https://jlcpcb.com/partdetail/HRE-CGA0805X5R107M6R3MT/C23692977) | 2 057 | $0.2823 | $0.2077 | $1.04 |
| CL21A107MQYNNWE | 0805 100 uF 6.3 V (Samsung) | [C6882730](https://www.lcsc.com/product-detail/C6882730.html) | 11 620 | $0.4476 | $0.3804 | $1.90 |
| CA45-B-6.3V-100uF-M | tantalum 3528 | [C140373](https://jlcpcb.com/partdetail/CEC-CA45_B_6_3V_100uF_M/C140373) | 4 218 | $0.1589 (150) | $0.1349 (500) | $0.67 |

**This is the second-largest line in the BOM after the SoC** — $1.54/unit at 1k for five ceramics.
Sensitivity: switching to the HRE part saves **$0.50/unit** (but stock is only 2 057); dropping to
two 100 uF in halo-core, which drives an 80 mA magnetic transducer rather than a voice coil and
a UWB burst, saves **$0.92/unit** and is defensible — but it is no longer parity. The roll-up
below keeps all five.

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

**What DW3000 does give halo-uwb for free:** two-way ranging between halos, with no Apple
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

**What that does to a CR2032.** Baseline BLE-only draw, using the nRF52832 datasheet's 1.9 µA
System-ON-with-RTC (the nRF52840 is in the same class; its own figure was not fetched),
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

Parity notes: SoC is **nRF52840-class per D10**; **there is no NFC line item** (on-chip NFC-A,
coil in copper, two tuning caps counted among the 0402s); **no external flash** (1 MB on-chip);
**no buck and no OVP switch** (no U1 rail to make); **five 100 uF bulk capacitors** kept, as on
Apple's board.

### 5.1 halo-core, module form (the shipping default)

| Ref | Part | LCSC/JLC | Qty | @100 ea | @100 ext |
|---|---|---|---|---|---|
| M1 | E73-2G4M08S1C (**nRF52840** module, incl. antenna + both crystals) | C356849 | 1 | $5.9347 | $5.9347 |
| U2 | LIS2DW12TR accelerometer | C189624 | 1 | $0.8031 | $0.8031 |
| U3 | MAX98357AEWL+T class-D driver | C2682619 | 1 | $0.3171 | $0.3171 |
| LS1 | MLT-8530 magnetic transducer | C94599 | 1 | $0.1643 | $0.1643 |
| BT1 | BS-CR2032-8 holder | C7498149 | 1 | $0.1839 | $0.1839 |
| C1–C5 | 100 uF 6.3 V 0805 bulk (Apple parity) | C49215609 | 5 | $0.3574 | $1.7870 |
| — | 16 x 0402 (decoupling, 2 x NFC tuning, RC) | C1525 | 16 | $0.0039 | $0.0624 |
| — | NFC coil (PCB copper) | — | 1 | $0 | $0 |
| BAT1 | Panasonic CR2032 (qty-1 price, upper bound) | — | 1 | $0.39 | $0.39 |
| | **BOM subtotal @100** | | | | **$9.64** |
| | **BOM subtotal @1 000** | | | | **$9.16** |

### 5.2 halo-core, bare-SoC form

| Ref | Part | LCSC | Qty | @100 ea | @100 ext |
|---|---|---|---|---|---|
| U1 | NRF52840-QIAA-R (aQFN73 7x7) | C190794 | 1 | $4.1407 | $4.1407 |
| Y1 | NX2016SA 32 MHz | C843260 | 1 | $0.2922 | $0.2922 |
| Y2 | X321532768KGD2SI 32.768 kHz | C620155 | 1 | $0.1888 | $0.1888 |
| U2 | LIS2DW12TR | C189624 | 1 | $0.8031 | $0.8031 |
| U3 | MAX98357AEWL+T | C2682619 | 1 | $0.3171 | $0.3171 |
| LS1 | MLT-8530 | C94599 | 1 | $0.1643 | $0.1643 |
| BT1 | BS-CR2032-8 | C7498149 | 1 | $0.1839 | $0.1839 |
| C1–C5 | 100 uF 6.3 V 0805 bulk | C49215609 | 5 | $0.3574 | $1.7870 |
| — | 26 x 0402/0603 (decoupling, DC/DC L+C, pi-match, 2 x NFC tuning) | C1525 | 26 | $0.0039 | $0.1014 |
| ANT1 | PCB trace antenna | — | 1 | $0 | $0 |
| BAT1 | CR2032 (upper bound) | — | 1 | $0.39 | $0.39 |
| | **BOM subtotal @100** | | | | **$8.37** |
| | **BOM subtotal @1 000** | | | | **$7.76** |

> **The nRF52840 has no published price break past 100 pcs** on either LCSC or JLCPCB
> ($4.0966 flat from 100 upward at pull time). The 1 000 and 10 000 rows therefore carry the
> 100-piece price for the SoC — an upper bound of roughly +$0.60/unit versus what a reel quote
> would give. Dropping to nRF52832 (which *does* have a 1k break at $2.6440) would save
> **$1.50/unit at 1k**, at the cost of D10 parity.

### 5.3 halo-uwb (nRF52840 + DW3110)

Everything in 5.2, plus:

| Ref | Part | Source | @100 ea | @1k ea |
|---|---|---|---|---|
| U4 | DW3110TR13 | Digi-Key | $7.83 | $6.91 |
| Y3 | 38.4 MHz crystal (placeholder) | C409422 | $0.1278 | $0.0941 |
| ANT2 | ACS5200HFAUWB UWB chip antenna | C224424 (JLC, **stock 0**) | $0.7788 | $0.6312 |
| U5 | TPS7A0233PDBVR UWB rail LDO | C2887324 | $0.3587 | $0.3341 |
| — | +12 passives | C1525 proxy | $0.0396 | $0.0348 |
| | **BOM subtotal @100** | | **$17.49** | |
| | **BOM subtotal @1 000** | | | **$15.76** |

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
minimum (avoided by panelising). Joint counts: core-module 99, core-bare 166 (aQFN73 alone is 73),
uwb 253.

**Enclosure and labour**: tooling now uses lane G's sourced China figure (two single-cavity
tools at ~$2 000 each = $4 000, amortised at 10 000 units = $0.40/unit); piece price and labour
remain estimates — see §7.

| Variant | Qty | BOM | PCB | Assembly | Enclosure | Tooling amort. | Labour | **Total/unit** |
|---|---|---|---|---|---|---|---|---|
| **halo-core (E73 nRF52840 module)** | 10 | $11.99 | $6.211 | $3.278 | $1.20 | $0 | $0.30 | **$22.98** |
| | 100 | $9.64 | $0.692 | $0.470 | $1.20 | $0 | $0.30 | **$12.30** |
| | 1 000 | $9.16 | $0.140 | $0.190 | $0.90 | $0 | $0.15 | **$10.53** |
| | 10 000 | $9.12 | $0.085 | $0.162 | $0.30 | $0.40 | $0.08 | **$10.15** |
| **halo-core (bare nRF52840)** | 10 | $10.59 | $6.211 | $3.693 | $1.20 | $0 | $0.30 | **$21.99** |
| | 100 | $8.37 | $0.692 | $0.608 | $1.20 | $0 | $0.30 | **$11.17** |
| | 1 000 | $7.76 | $0.140 | $0.300 | $0.90 | $0 | $0.15 | **$9.25** |
| | 10 000 | $7.69 | $0.085 | $0.269 | $0.30 | $0.40 | $0.08 | **$8.82** |
| **halo-uwb (nRF52840 + DW3110)** | 10 | $21.25 | $6.211 | $5.060 | $1.20 | $0 | $0.30 | **$34.02** |
| | 100 | $17.49 | $0.692 | $0.870 | $1.20 | $0 | $0.30 | **$20.55** |
| | 1 000 | $15.76 | $0.140 | $0.451 | $0.90 | $0 | $0.15 | **$17.40** |
| | 10 000 | $14.61 | $0.085 | $0.409 | $0.30 | $0.40 | $0.08 | **$15.88** |

For reference, the same model run at **nRF52832 parity** (gen-1 exact silicon, before D10) and
without the five bulk capacitors gave $8.98 / $6.14 / $14.30 per unit at 1 000 for the three
variants. **D10 plus Apple parity on bulk capacitance costs about $1.55–3.10 per unit.**

Caveats that inflate every 10 000-unit row:

1. **Most LCSC ladders stop at 1 000–6 000, and the nRF52840's stops at 100.** The deeper columns
   reuse the deepest published break, so they are **upper bounds**; real 10 k pricing needs a quote.
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
| halo-core, module, 1 000 | **$10.53** (10 000: **$10.15**) |
| halo-core, bare nRF52840, 1 000 | **$9.25** (10 000: **$8.82**) |
| halo-uwb, 1 000 | **$17.40** (10 000: **$15.88**) |

So: **halo-core at 1 000 units lands at 32–36 % of AirTag's retail price**, and at roughly
Apple's own estimated build cost — which is a striking result, because Apple builds tens of
millions and we are costing a thousand. It is possible only because the clone deletes four of
Apple's most expensive lines: the **U1** (unbuyable), the **32 Mbit flash** ($0.41–1.45), the
**buck + OVP switch**, and the **LDS antenna frame**, and because the **NFC front end never
existed**. Even at 100 units the bare-SoC build ($11.17) beats the 4-pack price per tag less
comfortably than the pre-D10 numbers did — the nRF52840 and the five bulk capacitors are what
moved it.

halo-uwb never competes on price with an AirTag and is not meant to: at $17.40 it buys
peer-to-peer ranging that an AirTag cannot do at all, because Apple's UWB only talks to Apple.

---
## 7. Enclosure and final assembly — where the numbers are weakest

**This section contains the least-sourced figures in the document. Treat them as estimates.**

- **Injection moulding.** Two sources, one Western and one Chinese. Xometry's guide
  ([xometry.com](https://www.xometry.com/resources/injection-molding/injection-molding-cost/),
  2026-09-03) gives tooling *"up to $10,000"* for mid-level orders of 1 000–2 000 small parts,
  material at **0.90–2.30 USD/lb**, and notes cycle time is *"about 60% of final part cost"*,
  but publishes **no per-part price**. Lane G's dossier
  ([`research/fetched/G-moulding-cost-and-battery-door.md`](fetched/G-moulding-cost-and-battery-door.md))
  found the number that actually applies here: Haizol quotes *"single-cavity prototype molds at
  verified Chinese factories cost $1,000-3,000"* and *"$1,000 to $15,000+ by steel grade and
  cavity count"*. **The roll-up therefore amortises $4 000 (two single-cavity Chinese tools at
  ~$2 000 each) over 10 000 units = $0.40/unit**, and keeps a **$0.30 piece price** as an
  unverified estimate. Lane G also rules two-shot tooling out below ~100 000 units/yr.
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

1. **halo-core ships on the E73-2G4M08S1C module** — which, confirmed from the JLCPCB part page
   on 2026-09-03, carries an **nRF52840** and therefore already meets D10's parity target. Ship it
   only after its FCC/CE/Giteki certificates are obtained from Ebyte; the vendor's own page
   renders no certification content. If they do not exist, switch to a **Raytac MDBT50Q**, which
   demonstrably holds *"FCC, IC, CE, Telec (MIC), KC, SRRC, NCC, RCM, WPC"* — Telec/MIC being the
   Japanese Giteki mark — and accept ~$1.96/unit more and a Digi-Key/Mouser supply line.
2. **Publish the bare-nRF52840 BOM alongside it.** It is $1.28/unit cheaper at 1 k and it is the
   version that goes into someone else's board — but it hands them the radio certification. At
   nRF52840 parity the module premium is small enough that the module should be the default for
   almost everyone.
3. **Keep Apple's part where Apple's part is cheap and available**: MAX98357A (exact part, $0.25
   at 1 k), TLV9001, CR2032, 100 uF bulk ceramics. Substitute only where forced: nRF52832-CIAA →
   nRF52840-QIAA (D10), BMA280 → LIS2DW12 (Apple's part is unbuyable), voice coil → MLT-8530,
   LDS antenna frame → PCB trace.
4. **There is no NFC BOM line.** Apple drives the coil from the SoC's own NFC-A on P0.09/P0.10;
   so do we. Budget a PCB coil and two tuning capacitors, and nothing else.
5. **Delete the external flash, the buck converter and the OVP switch.** They existed for the U1
   and the 1.8 V flash rail; none survives into halo-core. That is roughly $1.15–2.20/unit and
   ~16 joints gone. FPF2487 is not even in the LCSC/JLCPCB catalogue.
6. **Keep the five 100 uF bulk capacitors.** At $1.54/unit at 1 k they are the second-largest BOM
   line, and they are the reason a coin cell can drive a transducer or a UWB burst at all. If cost
   pressure forces a cut, two are defensible in halo-core (saving $0.92) — but that is a
   deliberate departure from parity, not an oversight.
7. **halo-uwb uses DW3110TR13**, ranging **no faster than once a minute** on a CR2032, and buys
   the UWB antenna from Digi-Key/Mouser because JLCPCB's ACS5200HFAUWB stock is zero. If lane H
   shows Bluetooth Channel Sounding on **nRF54L15** reaches useful accuracy, the whole DW3110 line
   item — $6.91 of silicon plus antenna, crystal, LDO and 12 passives, about **$8.00/unit at
   1 k** — disappears, and halo-uwb collapses back into halo-core with a different SoC. That
   is the single biggest cost lever in this document.
8. **Do not quote a dB figure for the AirTag speaker from Apple** — none is published. Use lane
   G's iFixit measurement (~78–80 dB) and its acoustics dossier, and note that transducer
   datasheet dB is specified at 10 cm, a different distance.

## 9. Open items this lane could not close

| Item | Why | Who should close it |
|---|---|---|
| CR2032 cell price at 100/1k/10k | Digi-Key filter page exposed only the qty-1 price; product URLs 404'd | re-pull, or quote a cell vendor |
| PCB quote for the actual 30 mm round 4-layer board | JLCPCB/PCBWay quote engines need the browser client and a board file | run it once the board exists |
| ENIG surface-finish adder | not a published JLCPCB line item | same quote |
| Injection-mould **piece** price | tooling is now sourced (lane G / Haizol) but no per-part price is | one RFQ to a Shenzhen moulder |
| FCC/CE/Giteki test-lab cost | no lab price fetched; needed to price the module-vs-bare-SoC crossover | lane F |
| Ebyte E73 certification status | Ebyte's page renders no certification content | ask Ebyte for the cert PDFs |
| Raytac MDBT42Q (nRF52832) certification list and price | page not found by index sweep; LCSC stock 0 | Raytac / Digi-Key |
| 38.4 MHz crystal spec match for DW3000 | picked on price class only | lane H with the DW3000 app notes |
| NTAG die/wafer pricing | JLCPCB shows placeholders on zero stock | only matters if an inlay format is wanted |
| Ranging energy per two-way exchange | derived from datasheet currents, not measured | lane H on the bench |
| nRF52840 price beyond 100 pcs | no break published on LCSC or JLCPCB at pull time | reel quote from Nordic/Arrow/Digi-Key |
| onsemi FPF2487 price | not in the LCSC/JLCPCB catalogue at all | only matters if the U1 rail is ever reproduced |
| Whether five 100 uF is the right number for halo-core | Apple sized it for a voice coil + U1, not an 80 mA transducer | bench measurement of cell droop |


---

# 10. Post-D12 re-run — halo-core on nRF54L (2026-09-03)

Three things changed after §1–9 were written:

- **D12**: Channel Sounding on coin-cell nRF54L15 measures 6–10 cm mean error, so the DW3110
  chain is deleted and **nRF54L10 is the v1 SoC**, with **nRF54L05** as fallback and **nRF54L15**
  as step-up. A DW3110 footprint stays on the board, unpopulated.
- **Lane G**: the sounder is a bare **Murata 7BB-20-3** piezo bender bonded to the shell — not a
  housed buzzer and not a micro-speaker.
- **Lane A**: the accelerometer substitute is **LIS2DW12TR** (Bosch BMA280 unbuyable). Unchanged
  from §3.4.

Everything else — no NFC IC, no external flash, no buck, no OVP switch, five 100 uF bulk caps,
MAX98357A driver, CR2032 + SMD holder, 4-layer 30 mm round board — carries over from §5.

## 10.1 nRF54L silicon — live pull

| Part | Pkg | Flash / RAM | LCSC/JLC | LCSC stock | JLC stock | @1 | @100 | @1k |
|---|---|---|---|---|---|---|---|---|
| **NRF54L10-QFAA-R7** (v1) | VFQFN-48 6x6 | 1.0 MB / 192 kB | [C44800139](https://www.lcsc.com/product-detail/C44800139.html) | **669** | 1 003 | $3.7943 | **$2.6175** | **$2.4012** |
| NRF54L05-QFAA-R (fallback) | VFQFN-48 6x6 | 0.5 MB / 96 kB | [C45022042](https://www.lcsc.com/product-detail/C45022042.html) | **1 775** | 1 775 | $3.2315 | $2.2020 | $2.0134 |
| NRF54L15-QFAA-R (step-up) | QFN-48 6x6 | 1.5 MB / 256 kB | [C42458750](https://www.lcsc.com/product-detail/C42458750.html) | **0** | 0 | $3.9896 | $2.7178 | $2.4852 |
| NRF54L10-QFAA-R (non-R7 reel) | VFQFN-48 | 1.0 MB / 192 kB | [C45022043](https://jlcpcb.com/partdetail/NordicSemicon-NRF54L10_QFAAR/C45022043) | 0 | 0 | $3.6910 | $3.4882 | $3.4882 |

Two sourcing notes that matter more than the cents. **Only the R7 reel of the nRF54L10 is in
stock** (669 at LCSC / 1 003 at JLCPCB) and its minimum packet is 1 000 — so a 100-piece build
buys a full reel or pays cut-tape. And **the nRF54L15, the part lane H actually measured Channel
Sounding on, is at zero stock everywhere**: the step-up is a paper option today. The L05 has the
deepest stock of the three (1 775) and the lowest price; whether the firmware fits its 0.5 MB /
96 kB is the question that decides $0.39/unit.

All three carry NFC-A, so **the "no NFC BOM line" result of §3.3 survives the SoC change intact.**

## 10.2 Sounder — Murata 7BB-20-3 piezo bender (lane G)

**The 7BB-20-3 itself is not in the LCSC or JLCPCB catalogue.** Searched 2026-09-03: zero hits.
The nearest sourced siblings — same 20.0 mm brass disc, same family, different resonance and
ceramic thickness — are:

| Part | Res. freq | Disc | LCSC/JLC | Stock | @1 | @1k | @5k |
|---|---|---|---|---|---|---|---|
| **7BB-20-6C** (price proxy) | 6.3 kHz | 20.0 mm brass | [C3812347](https://jlcpcb.com/partdetail/muRata-7BB_20_6C/C3812347) | **0** | $0.2079 | **$0.0805** | $0.0763 |
| 7BB-20-6L0 (pre-wired) | 6.3 kHz | 20.0 mm | [C3812354](https://jlcpcb.com/partdetail/muRata-7BB_20_6L0/C3812354) | 0 | $0.4778 | $0.1850 | $0.1752 |
| 7BB-27-4C | 4.6 kHz | 27.0 mm | [C3812329](https://jlcpcb.com/partdetail/muRata-7BB_27_4C/C3812329) | 0 | $0.3355 | $0.1298 | $0.1230 |
| 7BB-15-6 | 6.3 kHz | 15.0 mm | [C3812440](https://jlcpcb.com/partdetail/muRata-7BB_15_6/C3812440) | 0 | $0.1334 | $0.0516 | $0.0489 |

The roll-up prices the sounder at the **7BB-20-6C ladder ($0.2079 @1, $0.0805 @1k)** and labels it
a proxy. Every 7BB part is **zero stock at LCSC and JLCPCB**, so the disc is a Digi-Key / Mouser /
Murata-direct line item, and lane G's catalogue note records a **1 800-piece minimum order for the
7BB-20-6**. Neither a Digi-Key nor a Mouser price for the 7BB-20-3 could be fetched
(wrong-part and timeout responses) — **so this line is a price class, not a quote.**

Against the housed magnetic buzzer of §3.5 (MLT-8530, $0.1137 @1k) the bare bender saves
**$0.03/unit** — the reason to choose it is height and the shell-as-diaphragm acoustics lane G
owns, not money. It does change the drive problem: a bare bender is a ~20–30 nF capacitive load,
not an 8 ohm coil, so the MAX98357A's bridge-tied class-D output is being used as a
high-slew voltage source rather than a current source. That is lane G's call; the BOM line is
unchanged either way.

## 10.3 Roll-up — nRF54L10 v1, with L05 fallback and L15 step-up

Same model as §6: PCB = $35.70 + $25 ENIG + panels x $0.706 (nine 30 mm rounds per 100 x 100 mm
4-layer panel, [JLCPCB $70.60/m²](https://jlcpcb.com/news/discount-on-quality-4-layer-pcbs));
assembly = $8.18 setup + $1.53 stencil + $3.07 x extended parts + $0.0016/joint
([JLCPCB fee schedule](https://jlcpcb.com/help/article/pcb-assembly-price)); joints 140 bare
(QFN48) / 109 module (42 pads); 8 and 7 extended parts. Tooling $4 000 over 10 000 units per
lane G's Chinese single-cavity figure. CR2032 at its qty-1 $0.39 upper bound throughout.

| Variant | Qty | BOM | PCB | Assembly | Enclosure | Tooling | Labour | **Total/unit** |
|---|---|---|---|---|---|---|---|---|
| **halo-core v1, bare nRF54L10** | 10 | $8.61 | $6.211 | $3.651 | $1.20 | $0 | $0.30 | **$19.97** |
| | 100 | $6.89 | $0.692 | $0.567 | $1.20 | $0 | $0.30 | **$9.65** |
| | 1 000 | $5.99 | $0.140 | $0.258 | $0.90 | $0 | $0.15 | **$7.43** |
| | 10 000 | $5.92 | $0.085 | $0.227 | $0.30 | $0.40 | $0.08 | **$7.01** |
| *fallback, bare nRF54L05* | 10 | $8.11 | $6.211 | $3.651 | $1.20 | $0 | $0.30 | *$19.48* |
| | 100 | $6.47 | $0.692 | $0.567 | $1.20 | $0 | $0.30 | *$9.23* |
| | 1 000 | $5.60 | $0.140 | $0.258 | $0.90 | $0 | $0.15 | *$7.05* |
| | 10 000 | $5.53 | $0.085 | $0.227 | $0.30 | $0.40 | $0.08 | *$6.62* |
| *step-up, bare nRF54L15* | 10 | $8.76 | $6.211 | $3.651 | $1.20 | $0 | $0.30 | *$20.12* |
| | 100 | $6.99 | $0.692 | $0.567 | $1.20 | $0 | $0.30 | *$9.75* |
| | 1 000 | $6.07 | $0.140 | $0.258 | $0.90 | $0 | $0.15 | *$7.52* |
| | 10 000 | $6.00 | $0.085 | $0.227 | $0.30 | $0.40 | $0.08 | *$7.10* |
| **halo-core, Raytac AN54LQ module** | 10 | $9.64 | $6.211 | $3.294 | $1.20 | $0 | $0.30 | **$20.64** |
| | 100 | $8.54 | $0.692 | $0.486 | $1.20 | $0 | $0.30 | **$11.22** |
| | 1 000 | $7.97 | $0.140 | $0.206 | $0.90 | $0 | $0.15 | **$9.37** |
| | 10 000 | $7.95 | $0.085 | $0.178 | $0.30 | $0.40 | $0.08 | **$8.99** |

**Spread across the whole nRF54L family is $0.47/unit at 1 000** (L05 $7.05 → L15 $7.52). The SoC
choice inside the family is a firmware-fit decision, not a cost decision.

### Delta against the nRF52840 numbers of §6

| Variant | Qty | nRF52840 (§6) | nRF54L10 (§10) | **Delta** |
|---|---|---|---|---|
| bare SoC | 10 | $21.99 | $19.97 | **−$2.02** |
| | 100 | $11.17 | $9.65 | **−$1.52** |
| | 1 000 | $9.25 | $7.43 | **−$1.82** |
| | 10 000 | $8.82 | $7.01 | **−$1.81** |
| pre-certified module | 10 | $22.98 | $20.64 | **−$2.34** |
| | 100 | $12.30 | $11.22 | **−$1.08** |
| | 1 000 | $10.53 | $9.37 | **−$1.16** |
| | 10 000 | $10.15 | $8.99 | **−$1.16** |
| halo-uwb (deleted by D12) | 1 000 | $17.40 | — | **−$9.97 vs bare v1** |

At 1 000 units the BOM alone falls **$7.76 → $5.99 (−$1.77)**, of which **−$1.74 is the SoC**
($4.1407 → $2.4012) and −$0.03 the sounder. The rest of the per-unit delta is assembly: the
QFN48 has 26 fewer joints than the aQFN73. **D12 was correct on price as well as on accuracy —
Channel Sounding is not a feature you pay for, it is a feature that arrives with a cheaper part.**

**Value-engineering line, stated separately so it does not contaminate the comparison.** The five
100 uF bulk capacitors are Apple parity, sized for a voice coil and a U1. halo v1 has neither —
a piezo bender is a capacitive load and the UWB burst is gone. Dropping to **two 100 uF** gives
bare-nRF54L10 totals of **$18.57 / $8.58 / $6.51 / $6.09** — a further **−$0.92/unit**. That is a
real decision for lane G to make against measured cell droop, not a free saving.

### Against Apple, restated

| | per unit |
|---|---|
| AirTag 1-pack retail | $29.00 |
| AirTag 4-pack retail | $24.75 |
| AirTag estimated manufacturing cost (TechInsights) | ~$10 |
| **halo-core v1, bare nRF54L10, 1 000** | **$7.43** (26 % of retail) |
| **halo-core v1, module, 1 000** | **$9.37** (32 % of retail) |
| halo-core v1, bare, 10 000 | $7.01 |

The v1 build now sits **below Apple's own estimated build cost at a thousand units**, and it does
local relative positioning, which an AirTag cannot do for anyone but Apple.

## 10.4 Lane I's question, closed: pre-certified nRF54L modules exist

**Yes. Raytac ships a full nRF54L module line, it is certified in nine regimes, and it brings out
NFC1 and NFC2.** Lane I's fallback to an nRF52832 MDBT42Q is not necessary — the choice between
"a certified module" and "the positioning feature" does not have to be made.

| Vendor | nRF54L module? | Part(s) | Size (mm) | Pads | NFC1/NFC2 out? | Certifications | Price seen | Stock |
|---|---|---|---|---|---|---|---|---|
| **Raytac** | **YES** | **AN54LQ-10** (chip ant.), **AN54LQ-P10** (PCB ant.), **AN54LQ-U10** (u.FL); same in -05 and -15 | **13.7 x 9.5 x 1.8** | **42** | **YES — pad 15 = P1.02/NFC1, pad 16 = P1.03/NFC2**; SWDIO pad 36, SWDCLK pad 37 | **FCC (ID SH6AN54LQ), IC, CE/RED, Telec (MIC) = Giteki, KC, SRRC, NCC, RCM, WPC**; BT6 qualified; "a recommended 3rd-party module by Nordic Semiconductor" | **AN54LQ-10: no price fetched.** Siblings in the LCSC/JLC catalogue: AN54LQ-15 **$4.7861 @100 and @1k**; AN54LQ-U15 $4.2945 @1k; AN54LQ-P05 $3.9489 @1k | **0 everywhere** (LCSC, JLCPCB, Digi-Key filter returned no AN54LQ results; Mouser timed out) |
| **Insight SiP** | **YES (L15 only)** | **ISP2454** | **8.0 x 8.0 x 1.0** — smallest found | LGA, **not castellated** | not stated on the overview page | "full certified by the Bluetooth SIG and by global regulatory bodies such as the FCC, CE, Telec, etc." (generic wording, per-model list not given) | ISP2454-LX-RS **$8.159 @200, $7.7518 @1k** | **0** |
| **Minew (Minewsemi)** | **YES (L15 only)** | ME54BS01-nRF54L15, ME54BS12-nRF54L15 (12 x 15.8), ME54BS0A | 12 x 15.8 and n/s | not stated | not stated | not fetched — vendor page fetch failed (socket closed) | **placeholder prices only** ($0.0395/$0.0203 on zero stock — not real) | **0** |
| **Ezurio (Laird)** | no nRF54L found | BL654 family is nRF52840 | 15 x 10 x 2.2 | castellated | yes (NFC1/NFC2 documented) | FCC, ISED, EU, UKCA, MIC, KC, AS-NZS, Taiwan, Brazil, BT SIG | JLC listing is a zero-stock placeholder | 0 |
| **Fanstel** | **not found** | BT840F etc. are nRF52840 | 15.0 x 20.8 | 16 castellated + 43 LGA | not stated | FCC X8WBT840F, IC, TELEC, KCC, NCC, ANATEL | BT840F **$19.8856 @100** (JLC) | 0 |
| **Holyiot** | **not found** | — | | | | | zero catalogue hits at LCSC/JLCPCB | — |
| **Ebyte** | **not found** | E73 family is nRF52832/nRF52840 | | | | page renders no certification content | E73-2G4M08S1C $5.9347 @100 | 2 093 |

Evidence for the Raytac claims: product pages
[AN54LQ-P10](https://www.raytac.com/product/ins.php?index_id=163) and
[AN54LQ-10](https://www.raytac.com/product/ins.php?index_id=165) (both fetched 2026-09-03), and
the family specification **"[nRF54L15_10_05] AN54LQ-15_AN54LQ-10_AN54LQ-05 Spec (Ver.1.1)"**
([raytac.com/download/index.php?index_id=81](https://www.raytac.com/download/index.php?index_id=81),
8.2 MB PDF, fetched and text-extracted 2026-09-03), whose pin table reads:

> `(15)  P1.02  Digital I/O  General-purpose I/O` / `NFC1  NFC input  NFC antenna connection`
> `(16)  P1.03  Digital I/O  General-purpose I/O, Clock pin` / `NFC2  NFC input  NFC antenna connection`

and whose labelling clause reads *"The final end product must be labeled in a visible area with
the following: 'Contain FCC ID: SH6AN54LQ'."* The same PDF carries TELEC (Japan), NCC (Taiwan),
CE/RCM, SRRC (China), KC (Korea) and WPC (India) certificate sections, and notes
*"When NOT using NFC, please remove NFC1 / C19 / C20."*

**Two caveats, both real.**

1. **Pad style is unconfirmed.** The specification's pad geometry lives in a drawing that text
   extraction cannot read, so I can confirm **42 pads with a documented recommended land pattern**
   but **not** that they are half-hole castellations. Raytac's MDBT42Q in the same size class is
   castellated (lane I verified pads 22/23 = NFC1/NFC2 there), which makes castellation likely but
   not proven. **Someone should open the AN54LQ footprint drawing before lane I commits.**
2. **Nothing is in stock.** Every nRF54L module from every vendor shows zero at LCSC, JLCPCB and
   the Digi-Key filter. The bare **nRF54L10 silicon is in stock (669/1 003) and the modules are
   not** — so a module-based v1 is a Raytac-direct purchase with a lead time, while a bare-SoC v1
   can be built this week.

## 10.5 Bare-SoC route priced against the certification difference

| | bare nRF54L10 | AN54LQ module | premium |
|---|---|---|---|
| SoC / module | $2.4012 | $4.7861* | |
| 32 MHz + 32.768 kHz crystals | $0.3680 | included | |
| matching + antenna (PCB trace) | ~$0.023 in 0402s, $0 antenna | included | |
| **radio subtotal @1 000** | **$2.79** | **$4.79** | **+$2.00/unit** |
| radio subtotal @100 | $3.13 | $4.79 | +$1.66/unit |
| radio subtotal @10 000 | $2.76 | $4.79 | +$2.03/unit |
| joints | 140 | 109 (−31, ≈ −$0.05/unit) | |
| **total/unit @1 000** | **$7.43** | **$9.37** | **+$1.94/unit** |

`*` AN54LQ-15 catalogue price stands in for the AN54LQ-10, which is not listed anywhere I could
reach. The -10 is the smaller-memory part in the same package, so **$4.7861 is an upper bound**
and the true premium is probably lower.

**What the premium buys.** Under single modular approval the module holder's grant covers the
host, so the bare-SoC route must instead reproduce, at the builder's own cost: **FCC Part 15
intentional radiator, ISED, CE/RED (EN 300 328 + EN 301 489 + EN 62479), MIC/Giteki, KC, SRRC,
NCC, RCM and WPC** — nine regimes that Raytac has already paid for and that the AN54LQ spec
documents individually.

**I still have no fetched test-lab price**, and I will not invent one; lane F owns that number.
What the data does support is the break-even shape:

> The module pays for itself whenever the whole certification campaign costs more than
> **$1.94 x units**. That is **$194 at 100 units, $1 940 at 1 000, and $19 400 at 10 000.**

At 100 and 1 000 units the module is almost certainly cheaper all-in, because no plausible
nine-regime campaign costs under $2 000. Somewhere in the tens of thousands the bare SoC wins —
and only there. **For an open design, the argument is stronger still than the arithmetic**: every
downstream builder who drops the block into their own outline inherits Raytac's grant instead of
running their own campaign, so the $1.94 is paid once per tag and saves a campaign per *builder*.

**Recommendation.** Ship the block in both forms, as D1 already said, but flip which is the
default sourcing risk: **bare nRF54L10 is the only version buildable today** (silicon in stock,
modules at zero), so bring-up runs on bare silicon, and the **AN54LQ-P10 module is the shipping
form once Raytac confirms stock, lead time, MOQ and — critically — that the 42 pads are
castellated.** Both use the same SoC, the same NFC-A coil drive and the same firmware, so the
switch costs a footprint, not a port.

## 10.6 What §10 could not close

| Item | Why |
|---|---|
| AN54LQ-10 / AN54LQ-P10 unit price | not listed at LCSC, JLCPCB or the Digi-Key filter; Mouser timed out; Raytac quotes direct |
| Whether AN54LQ pads are castellated or LGA | the pad drawing is an image in the spec PDF; text extraction gives 42 pads and a land pattern but not the style |
| Murata 7BB-20-3 price | not in the LCSC/JLCPCB catalogue; 7BB-20-6C used as a labelled proxy; no Digi-Key or Mouser quote obtained |
| Minew nRF54L module specs and certs | vendor page fetch failed; JLCPCB shows placeholder prices on zero stock |
| Certification campaign cost | no lab quote fetched — lane F |
| nRF54L10 sleep / TX current | vendor page gives L15 figures only (4.8 mA TX @0 dBm, 3.4 mA RX, 0.7–2.9 uA sleep); the L10's own numbers were not fetched |

---

# 11. Second pass — every §10 price re-verified, and lane I's module question actually closed (2026-09-03, later)

§10 was written and then the session died before it could be checked or before
`research/sources.tsv` could be appended. This section is the check. **Every price in §10.1 was
re-pulled from the live endpoints and is confirmed**; two numbers drifted, three facts in §10.4
were wrong or incomplete, and the pad-style question §10.6 left open is now **settled from the
vendors' own drawings** — with an answer that changes what lane I should do.

## 11.1 Re-verification of §10.1 — the nRF54L ladders hold

Re-pulled 2026-09-03 by GET on `lcsc.com/product-detail/<code>.html` (reading `productPriceList`,
`stockNumber`, `minPacketNumber` out of the `__NEXT_DATA__` blob) and by POST on
`jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`.

| Part | LCSC | LCSC ladder (1 / 10 / 30 / 100 / 500 / 1 000) | LCSC stock | **min packet** | JLC @1k | JLC stock | vs §10 |
|---|---|---|---|---|---|---|---|
| **NRF54L10-QFAA-R7** | [C44800139](https://www.lcsc.com/product-detail/C44800139.html) | 3.7943 / 3.2583 / 2.9404 / **2.6175** / 2.4684 / **2.4012** | **669** | **1 000** | $2.3768 | 1 003 | **identical** |
| NRF54L05-QFAA-R | [C45022042](https://www.lcsc.com/product-detail/C45022042.html) | 3.2315 / 2.7615 / 2.4834 / **2.2020** / 2.0719 / **2.0134** | **1 775** | **3 000** | $2.0086 | 1 775 | **identical** |
| NRF54L15-QFAA-R | [C42458750](https://www.lcsc.com/product-detail/C42458750.html) | 3.9896 / 3.4106 / 3.0658 / **2.7178** / 2.5584 / **2.4852** | **0** | **3 000** | $2.4791 | 0 | **identical** |
| NRF54L10-QFAA-R (non-R7) | [C45022043](https://www.lcsc.com/product-detail/C45022043.html) | 3.7030 / 3.6151 / 3.5582 / **3.4996** (ladder ends at 100) | 0 | 3 000 | $3.4882 @104 | 0 | drifted +$0.012 @1, +$0.011 @100 |

Two corrections to §10, both about **minimum packet, not price**:

- §10 recorded the nRF54L10-R7's 1 000-piece minimum packet. It did **not** record that
  **the L05 and the L15 both have a 3 000-piece minimum packet.** So the "L05 saves $0.39/unit"
  line in §10.1 comes with a **$6 040 minimum buy-in**; at a 100- or 1 000-unit build the L05 is
  cheaper per part and more expensive in cash. **At 1 000 units the L10-R7 is the only nRF54L
  whose minimum packet you actually consume.** That reverses §10.1's "the L05 has the deepest
  stock and the lowest price" framing for every build below 3 000 units.
- The non-R7 L10 reel is still zero-stock and still $1.10/unit more expensive at 100 than the R7.
  Nothing to do; the R7 is the part.

## 11.2 nRF54L currents — §10.6's open item, closed from the datasheet

§10.6 recorded "the L10's own numbers were not fetched" and carried the vendor page's L15
figures. The **nRF54L15 / nRF54L10 / nRF54L05 preliminary datasheet v0.10** (`4503_018 v0.10`,
906 pp, Table 86 and §11.1.2) covers all three parts in one document, and its numbers are
**better than the marketing page's**:

| Symbol | Description | Typ. |
|---|---|---|
| `IOFF0` | System OFF, wake on pin, 0 KB RAM retained | **0.6 µA** |
| `IOFF1` | System OFF, wake on pin + GRTC, LFXO, 0 KB RAM retained | **0.8 µA** |
| `ION_IDLE0` | System ON, wake on pin, 0 KB RAM retained | 0.7 µA |
| `ION_IDLE2` | System ON, wake on pin, **96 KB** RAM retained (**= L05's full RAM**) | **1.5 µA** |
| `ION_IDLE4` | System ON, wake on pin, **192 KB** RAM retained (**= L10's full RAM**) | **2.4 µA** |
| `ION_IDLE5` | System ON, wake on pin, **256 KB** RAM retained (**= L15's full RAM**) | 3.0 µA |
| `ION_IDLE6` / `7` / `8` | System ON + GRTC + LFXO, 64 / 128 / 256 KB retained | 1.5 / 2.0 / **3.1 µA** |
| `ITX,0dBM` | TX only run current, P<sub>RF</sub> = 0 dBm | **3.7 mA** |
| `ITX,MaxdBm,QFN` | TX only, maximum power setting, QFN package | 9.1 mA |
| `IRX,1M` | RX only, 1 Mbps Bluetooth LE | **2.1 mA** |
| `IAPPCPU0` | CPU running CoreMark at 128 MHz from NVM, cache on | 2.6 mA |

Three things fall out of that table that no other lane has recorded:

1. **TX at 0 dBm is 3.7 mA, not 4.8 mA.** The 4.8 mA on Nordic's product page is a
   whole-device figure; the datasheet's radio-only figure is 3.7 mA and RX is 2.1 mA. Both are
   **below the nRF52832's 5.3 mA / nRF52840-class numbers used in §4's battery table**, so every
   CR2032 life figure in §4 is a floor, not a ceiling, on nRF54L.
2. **The L05 sleeps 0.9 µA lower than the L10** (1.5 vs 2.4 µA with full RAM retained) purely
   because there is less RAM to hold. On a tag whose average current is single-digit microamps
   that is a **~15–20 % battery-life difference** — a bigger lever than the $0.39 of silicon.
   Whether the firmware fits 0.5 MB / 96 KB is therefore a *battery* question as well as a cost one.
3. **There is no published 192 KB + GRTC + LFXO row.** The advertising sleep state halo actually
   uses on an L10 is bracketed by `ION_IDLE7` (2.0 µA) and `ION_IDLE8` (3.1 µA) and is
   **not stated by Nordic**. Do not quote a single number for it; lane H should measure it.

## 11.3 Lane I's question, properly closed: certified **or** castellated — not both

§10.4 answered "yes, Raytac ships a certified nRF54L module" and left pad style unconfirmed. The
pad style is the whole point of lane I's request, so it was resolved by rendering the vendors'
own mechanical drawings out of the PDFs and reading them. **The answer is no: as of 2026-09-03 no
module is simultaneously pre-certified and castellated on nRF54L silicon.**

### The castellation verdict, with the evidence

**Raytac AN54LQ — NOT castellated. It is a bottom-terminated LGA-style module.**
The spec PDF's §2.1 bottom view ([`raytac.com/download/index.php?index_id=81`](https://www.raytac.com/download/index.php?index_id=81),
p. 6) draws **43 small rectangular pads set in from the module outline with a visible gap**, and
§2.2's *"Recommended layout of solder pad"* (p. 7) draws every land **entirely inside the
9.5 × 13.7 mm outline**. Compare Raytac's own MDBT42Q datasheet in the same document format
([the 64-page PDF lane I already read](https://www.raytac.com/upload/download_files/38a8a4a0aff945d8484507d60058109b.pdf),
pp. 6 and 8): its bottom-view pads are **long rectangles running to the module edge**, and its
recommended lands **protrude outward past the outline** — the toe fillet a half-hole castellation
needs. Two drawings, one vendor, one format, opposite geometry. **The AN54LQ cannot be
hand-soldered or optically inspected the way the MDBT42Q can.**

Also, §10.4 said 42 pads. **It is 43**: the pin table's last row is `(42) (43) GND`, and the
drawing labels 43 top-left and 42 top-right. NFC1 = pad 15 (P1.02), NFC2 = pad 16 (P1.03),
SWDIO = 36, SWDCLK = 37 — those four were right.

**Minew ME54BS11 — castellated, and the vendor says so in words.**
The ME54BS11-nRF54L10 datasheet's §5 mechanical drawing shows **half-round notches along both
long edges** and carries the note, verbatim:

> *"Note: The recommended pad size is 1.4*0.8mm, with the pad extending outward by 0.5mm."*

A land that extends outward past the body is a castellation, stated by the manufacturer rather
than inferred from a picture. Its §6 schematic labels the module's J1 pins **6 = P1.03/NFC2** and
**7 = P1.02/NFC1**, so the NFC pins are exposed *and* documented — though the §4 pin-definition
table lumps them in as *"2~9 P1.11-P1.14 P1.03 P1.02 P1.06 P1.05 — General-purpose IO"*, the same
under-documentation lane I found on Minew's MS88SF2. The bigger sibling **ME54BS01** shows the
same castellated profile and names NFC1/NFC2 on its schematic's pins 10/11.

**What Minew does not have is certification.** The ME54BS01-nRF54L10 datasheet's CERTIFICATION
page (p. 3) carries **the Bluetooth logo and nothing else** — no FCC, no CE, no MIC — and the
store's spec table reads `Certification: /` on the nRF54L10, nRF54L05 and ME54BS11 parts and
`BQB` on the nRF54L15 ME54BS01. The product page's own words are
*"Planned Certifications: BQB, FCC, CE, IC, TELEC, KC, RCM…"*. **Planned is not held**, and a
module with no grant confers no modular approval on a host — which is the entire reason lane I
wanted a module.

### The full nRF54L module survey, second pass

Vendors checked: Raytac, Fanstel, Insight SiP, Ezurio, Minew, Holyiot, Ebyte **and u-blox**
(missing from §10.4 entirely). Two vendors §10.4 reported as having nothing turned out to have
something.

| Vendor | nRF54L part | Size (mm) | Pads | Pad style | NFC pins out? | Certifications **held** | Price **fetched** | Stock |
|---|---|---|---|---|---|---|---|---|
| **Raytac** | **AN54LQ-15 / -10 / -05**, and -P / -U antenna variants | **13.7 × 9.5 × 1.8** — smallest that fits a 30 mm puck comfortably | **43** | **LGA — pads inset, lands inside outline** | **YES, documented**: pad 15 = P1.02/NFC1, pad 16 = P1.03/NFC2 | **FCC ID SH6AN54LQ, IC, CE/RED, Telec(MIC)/Giteki, KC, SRRC, NCC, RCM, WPC; BT6** | AN54LQ-15 **$5.0505@1 → $4.7861@100 and @1k** ([C49419243](https://jlcpcb.com/partdetail/RAYTAC-AN54LQ_15/C49419243)); AN54LQ-U15 $4.2945@1k; AN54LQ-P05 $3.9489@1k. **-10 and -05 are placeholder rows ($0.0395/$0.0203) — no price** | **0** everywhere |
| **Minew** | **ME54BS11** (L10/L05), **ME54BS01** (L15/L10/L05), ME54BS12 (L15) | BS11 **15.8 × 12 × 2.0** (fits); BS01 23.2 × 17.4 × 2.0 (29.0 mm diagonal — **does not fit** a 30 mm board) | BS11 **18**; BS01 ~28 | **CASTELLATED — vendor note: lands "extending outward by 0.5mm"** | **YES**: BS11 J1 pins 6/7 = NFC2/NFC1; BS01 pins 10/11. Named on the schematic, **not** in the pin table | **NONE — "Planned Certifications: BQB, FCC, CE, IC, TELEC, KC, RCM…"**; datasheet cert page shows only the Bluetooth logo | **ME54BS11 $4.20 @1**, **ME54BS01-nRF54L10 $4.00 @1** (Minew store, direct); ME54BS01-1Y10TI **$11.7932@1 → $4.4713@1 000** ([C50088408](https://jlcpcb.com/partdetail/Minewsemi-ME54BS01_1Y10TI/C50088408)); ME54BS03-3Y15TI $5.1592@1k | **0** in the JLC catalogue; store sells singles |
| **u-blox** | **NORA-B201/206 (L15), B211/216 (L10), B221/226 (L05)**, B261/266/276 (u-connectXpress) | **10.4 × 11.2 × 1.9** (antenna pin) / **10.4 × 14.3 × 1.9** (PCB antenna) | not published | **not published** | **NFC listed as a hardware interface** ("1 × NFC"); **pin numbers not published** | **NONE YET — the product summary's footnote reads "1 = Certifications are pending"** over a list of RED/UKCA/FCC/ISED/MIC/KCC/NCC/ACMA/NZ. Doc is stamped **"Early Product Information"** | **NORA-B216-00B $8.2661@1** (stock 10), **NORA-B206-00B $10.0945@10** (**stock 100**), NORA-B201-00B $6.2446@1k, NORA-B266-00B $6.7557@1k | **B206: 100. B216: 10.** The only nRF54L modules with any stock anywhere |
| **Insight SiP** | ISP2454 (L15 only) | 8.0 × 8.0 × 1.0 — smallest of all | LGA 0.65 mm pitch | **LGA, not castellated** | not stated on the overview page | generic wording only: *"full certified … FCC, CE, Telec, etc."*, no per-model list | $20.4454@1 → $7.7518@1k ([C44975104](https://jlcpcb.com/partdetail/InsightSiP-ISP2454_LX_RS/C44975104)) | 0 |
| **Holyiot** | **HOLYIOT-24005-nRF54L15** — **§10.4 said "not found"; it exists** | not fetched | not fetched | not fetched | not fetched | not fetched | **placeholder rows only** (codes `C9900176029` and `C9900261373`, returned by the JLCPCB parts API on the keyword `HOLYIOT`) — **no price** | 0 |
| **Ezurio (Laird)** | none found | — | — | — | — | — | — | — |
| **Fanstel** | none found | — | — | — | — | — | — | — |
| **Ebyte** | none found (E73 family is nRF52832/840) | — | — | — | — | — | — | — |

### What that means for lane I

Lane I asked for two properties in one part. **They are not available in one part today.**

| | pre-certified | castellated | fits 30 mm | NFC pins documented | buyable now |
|---|---|---|---|---|---|
| **Raytac AN54LQ-P10** | **YES, 9 regimes** | no (LGA) | **yes, 13.7 × 9.5** | **yes** | no (stock 0, Raytac-direct) |
| **Minew ME54BS11** | **no** (planned) | **YES** | **yes, 15.8 × 12** | yes (schematic) | **yes, $4.20 singles** |
| **u-blox NORA-B216** | **no** (pending) | unknown | yes, 10.4 × 14.3 | interface only | **yes, 10 pcs** |
| **bare NRF54L10-QFAA-R7** | no | n/a (QFN48) | yes, 6 × 6 | n/a (P1.02/P1.03) | **yes, 669 + 1 003** |

**The two requirements are not equally load-bearing, and this is the point lane I should take
away.** Under 47 CFR 15.212 the grant travels with the module regardless of how it is
terminated — **castellation is a manufacturability and inspectability preference, not a
certification requirement.** So the honest ordering is:

1. **If the certification inheritance is what matters** (and for an open design it is: it is the
   thing that saves a campaign per *downstream builder*, not per tag), the pick is
   **Raytac AN54LQ-P10** and lane I should accept LGA — which means paste-and-reflow assembly,
   X-ray or electrical test rather than visual inspection of the joints, and no hand rework.
   That is a real cost to a hobbyist builder and it should be stated in the block's README.
2. **If hand-solderability is what matters** (bring-up boards, a hackable block, the version
   someone tacks onto a breadboard), the pick is **Minew ME54BS11** at $4.20 — and the host
   builder owns the whole radio campaign, exactly as with bare silicon. In that case the module
   buys layout convenience only, and the **bare NRF54L10-QFAA-R7 at $2.40 is strictly better
   value**, because it costs $1.80 less and hands over the same certification obligation.
3. **u-blox NORA-B2 is the one to re-check in a quarter.** It is the only nRF54L module line
   with stock at a catalogue distributor today, it is 10.4 × 11.2 mm, it names Channel Sounding
   and NFC explicitly, and its certifications are *pending* rather than absent. When they land it
   becomes a direct competitor to the AN54LQ. Two caveats, both stated verbatim from the sources:
   the product summary is **"Early Product Information"** with **"Certifications are pending"**,
   and the u-blox product page renders **"This product is not longer available"** *(sic)* against
   **all nine variants** while JLCPCB shows 100 pieces of NORA-B206 in stock. Those two
   statements cannot both be the current commercial status; **CANNOT DETERMINE — ask u-blox.**

## 11.4 The module premium, re-priced against what was actually fetched

Same method as §10.5. Bare radio subtotal = SoC + 32 MHz + 32.768 kHz crystals ($0.3680 at 1 000)
+ ~$0.023 of matching 0402s, PCB trace antenna at $0.

| Route @1 000 | radio subtotal | premium over bare L10 | certified? | derived total/unit |
|---|---|---|---|---|
| **bare NRF54L10-QFAA-R7** | **$2.79** | — | no | **$7.43** (§10.3) |
| bare NRF54L05-QFAA-R | $2.40 | −$0.39 | no | $7.05 (§10.3) — but a **3 000-piece minimum packet** |
| **Raytac AN54LQ-15** (upper bound for the -10) | **$4.79** | **+$2.00** | **YES, 9 regimes** | **$9.37** (§10.3) |
| Raytac AN54LQ-P05 (nRF54L05, PCB antenna) | $3.95 | +$1.16 | **YES** | ≈ **$8.53** *(derived: $9.37 − $0.84)* |
| Minew ME54BS01-1Y10TI (nRF54L10) | $4.47 | +$1.68 | no | ≈ **$9.05** *(derived: $9.37 − $0.32)* |
| u-blox NORA-B201-00B (nRF54L15, antenna pin) | $6.24 | +$3.45 | pending | ≈ **$10.82** *(derived)* |

The `≈` rows are **derived by substituting one line into §10.3's module roll-up**, not
independently re-modelled; the joint count and every other line is unchanged. They are labelled
derived for that reason.

**The break-even is unchanged in shape and cheaper in fact.** §10.5 put the module premium at
$1.94/unit against the AN54LQ-15 price. Against the **AN54LQ-P05** — a *certified* module on the
*fallback* SoC, with a PCB antenna, at $3.9489 — the premium over bare nRF54L10 is **$1.16/unit**:
**$116 at 100 units, $1 160 at 1 000, $11 600 at 10 000.** No nine-regime certification campaign
costs under $1 160, so **the certified module wins outright at 1 000 units and below**, and the
crossover moves out past 10 000. **Still no test-lab price was fetched; lane F owns that number
and I will not invent it.**

## 11.5 What §11 corrects in §10

| §10 said | §11 found |
|---|---|
| AN54LQ has **42 pads** | **43** — pin table's last row is `(42) (43) GND` |
| AN54LQ pad style *"castellation likely but not proven"* | **not castellated** — LGA; lands drawn wholly inside the outline, unlike Raytac's own MDBT42Q |
| Holyiot: **not found** | **HOLYIOT-24005-nRF54L15 exists** (JLC catalogue, placeholder price, zero stock) |
| u-blox: **not surveyed at all** | **NORA-B2 series is nRF54L15/L10/L05**, Channel Sounding + NFC, 10.4 × 11.2 mm, and the only nRF54L modules with stock — certifications **pending** |
| *"nothing is in stock anywhere"* | true of Raytac/Minew/Insight SiP; **false** for u-blox — NORA-B206 shows 100 pcs, NORA-B216 10 pcs |
| L05 is *"the deepest stock and the lowest price"* | its **minimum packet is 3 000**, so below 3 000 units the L10-R7 (min 1 000) is the only one you can buy without overbuying |
| nRF54L10 currents *"not fetched"* | fetched: TX@0 dBm **3.7 mA**, RX **2.1 mA**, System OFF+GRTC **0.8 µA**, System ON 192 KB retained **2.4 µA** |
| §10.1 prices | **all re-pulled, all identical**; only the dead non-R7 reel drifted a cent |

## 11.6 Still open after two passes

| Item | Why | Who |
|---|---|---|
| AN54LQ-**10** / -P10 unit price | placeholder rows at JLCPCB; Digi-Key returns **403** and Mouser **"Access Denied"/captcha** to automated fetch; Raytac quotes direct | one email to Raytac |
| AN54LQ stock, MOQ, lead time | zero at every catalogue distributor | same email |
| u-blox NORA-B2 commercial status | product summary says certifications pending; the web page says all nine variants *"not longer available"*; JLCPCB shows 100 in stock. Irreconcilable from outside | ask u-blox |
| u-blox NORA-B2 pad style and NFC pin numbers | **no data sheet is published** — only a 2-page product summary marked *"Early Product Information"* | ask u-blox, or wait for the data sheet |
| Murata **7BB-20-3** price | still not in the LCSC/JLCPCB catalogue (re-searched: only 7BB-20-6C / -6L0 / -6CL0, all zero stock); Digi-Key 403, Mouser captcha | Murata or a rep quote |
| Certification campaign cost | no lab quote fetched — the one number that decides §11.4's crossover | lane F |
| Holyiot 24005 specs, certs, price | vendor site did not answer (connection closed) | retry or email |
| nRF54L10 sleep current with 192 KB retained **and** GRTC + LFXO | Nordic publishes 128 KB (2.0 µA) and 256 KB (3.1 µA) but not 192 KB | lane H, on the bench |
| Minew ME54BS11 certification date | *"Planned"* with no schedule given | ask Minew |
