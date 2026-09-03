# nRF52 module datasheet extracts — pins, pitch, NFC, keep-out, certs
Lane I. Fetched 2026-09-03. Everything below is quoted or read directly from the named source.

---
## Raytac MDBT42Q / MDBT42Q-P (nRF52832)
Source: Raytac datasheet PDF (64 pp),
<https://www.raytac.com/upload/download_files/38a8a4a0aff945d8484507d60058109b.pdf>;
product page <https://www.raytac.com/product/ins.php?index_id=31> (MDBT42Q-512KV2);
Digi-Key <https://www.digikey.com/en/products/detail/raytac/MDBT42Q-512KV2/13677592>.

- "Compact size with (L) 16 x (W) 10 x (H) 2.2 mm." Antenna: **chip antenna**.
- **41 pads.** Digi-Key package/case: **"41-SMD Module"**.
- **NFC1 = pad (22) (P0.09), NFC2 = pad (23) (P0.10)** — "NFC antenna connection", both exposed.
- **SWDCLK = pad (36), SWDIO = pad (37)**. RESET on pad (35) region (P0.21/RESET).
- 32 GPIO; XL1/XL2 (32.768 kHz) on pads (13)/(14) — the LF crystal is *not* on the module.
- Certifications, verbatim: *"Granted main regional certification such as FCC (USA), CE(EU), TELEC
  (Japan), SRRC (China), IC (Canada), NCC (Taiwan), and KC (South Korea)"*; the datasheet reproduces
  each certificate in §9. Product page adds WPC/UKCA and BT 5.4 qualification.
- **FCC ID: SH6MDBT42Q.** §9.10.1, verbatim: *"The final end product must be labeled in a visible area
  with the following: 'Contain FCC ID: SH6MDBT42Q'."*
- §2.3 *RF layout suggestion (AKA, antenna keep-out area)*, verbatim:
  > Make sure to keep the "No Ground Pad" as wider as you can regardless of the size of your PCB.
  > **No Ground Pad should be included in the corresponding position of the antenna in EACH LAYER.**
  > Place the module towards the edge of PCB to have better performance than placing it on the center.
  > Welcome to send us your layout in PDF for review at sales@raytac.com …
  The datasheet then shows a page of *"Examples of 'NOT RECOMMENDED' layout"*.
- §2.4: *"Footprint & Design guide — Please visit 'Support' page of our website to download. The package
  includes footprint, 2D/3D drawing, reflow graph and recommended spec for external 32.768KHz."*
- §2.6 *GPIO located near the radio*, verbatim: *"Some GPIO have recommended usage. To maximize RF
  performance, these GPIO are only available to use as low drive, low frequency I/O only. Wrong usage may
  lead to undesirable performance. … Low frequency I/O is a signal with a frequency up to 10 KHz. SPI,
  I2C, UART, PWM are NOT low frequency I/O."*
- Price: Digi-Key **$4.95 @ qty 1**, 18 in stock, *marketplace* item — "Will ship in approximately 14 days
  from Raytac" with a **$25.00 flat rate shipping fee**. No 10/100/1000 breaks shown on that page.
- Variant MDBT42Q-ATM (<https://www.raytac.com/product/ins.php?index_id=87>): same 10×16×2.2 mm, chip
  antenna, AT-command firmware preloaded, **"NFC: Not available"** on that variant.

---
## Insight SiP ISP1807 (nRF52840)
Source: datasheet `isp_ble_DS1807_R19.docx` →
<https://www.insightsip.com/fichiers_insightsip/pdf/ble/ISP1807/isp_ble_DS1807.pdf>

- *"This ultra-small **LGA module, 8 x 8 x 1 mm**, is based on the nRF52840 Chip."*
- Integrates decoupling, **32 MHz and 32.768 kHz crystals**, load caps, DC-DC, RF matching and antenna.
- §3 Pin Description, verbatim: *"The module uses an **LGA format with a double row of pads on a 0.65 mm
  pitch**. The pad layout follows the QFN Jedec standard for 2 row LGA parts. The NC pads are to be
  connected to isolated metal pads on the application PCB for mechanical stability and reliability
  (drop test)."* → **not castellated**; not hand-solderable.
- **51 pins.** NFC1 = pin 2 (P0_09), NFC2 = pin 4 (P0_10). **SWDIO = pin 28, SWDCLK = pin 30.**
  Pin 20 OUT_ANT and pin 22 OUT_MOD must be strapped together for normal operation (so an external
  antenna can be substituted). VCC_nRF = pin 26. "Configurable 46 GPIOs including 8 ADC".
- §4.3 *Antenna Keep-Out Zone*, verbatim:
  > For optimal antenna performance, it is recommended to respect a metal exclusion zone to the edge of
  > the board: **no metal, no traces and no components on any application PCB layer except mechanical LGA
  > pads.** … **18.0 mm min** [along the edge] … **4.0 mm** [depth].
- *"The antenna was designed to be optimized with several standard ground plane sizes. **The NFC tag
  antenna can be connected externally.**"* Ground-plane simulations published for 18 × 30 mm (USB dongle)
  and 40 × 100 mm (phone) planes.
- Certifications listed on the front page: **Bluetooth SIG certified · CE certified · FCC, IC certified ·
  TELEC, KCC certified · PSA Certified Level 1 · RoHS and Reach**.
- Price: **not verified this session** — Mouser product pages timed out twice, everythingrf returned 403.

---
## Minew MS88SF2 / MS88SF3 (nRF52840)
Sources: datasheet <https://store.minewsemi.com/wp-content/uploads/2024/03/MS88SF2-nRF52840_Datasheet_K_EN.pdf>;
LCSC <https://www.lcsc.com/product-detail/C20416747.html>;
JLCPCB <https://jlcpcb.com/partdetail/Minew-MS88SF2nRF52840/C20616655>.

- MS88SF2: **23.2 × 17.4 × 2 mm**, PCB antenna *or* IPEX, **20 GPIO**, 1 MB flash / 256 kB RAM,
  1.7–5.5 V (VDD 1.7–3.6 V, VDDH 2.5–5.5 V), −40…+8 dBm, RX 4.6 mA, TX 4.8 mA @ 0 dBm.
- Pins: 28 numbered. GND = 1/13, VDD = 14, VDDH = 15, **SWCLK/SWDIO = 26/25 ("Burn Pins")**,
  D− = 16, D+ = 17, I/O = 2–12 / 18–24 / 27–28 carrying P0.02–P0.31 and P1.00–P1.09.
  **The datasheet's pin table never names NFC1/NFC2** — the nRF52840's NFC pins are P0.09/P0.10, inside
  the quoted range, so they are *probably* reachable, but this is **CANNOT DETERMINE** from the datasheet.
- Land pattern, verbatim: *"Notice: The recommended pad size is **1.8\*0.8mm** with a pad extension of
  **0.5mm outward**."* → castellated pads intended to be soldered with a visible fillet.
- §7 PCB LAYOUT, verbatim: *"**There should be no GND plane or metal cross wiring in the module antenna
  area, and components should not be placed nearby. It is best to make a hollow or clear area, or place
  it on the edge of the PCB board.**"* Then eight numbered layout notes, including
  *"5) Do not cover copper under module's antenna…"*, *"7) Module should be placed on edge of circuit
  board and keep a distance away from other circuits."*
  **Documentation defect worth knowing:** note 3 reads *"It is preferred to have a clearance area of
  4 square meter or more area around the module antenna"* — a mistranslation; the unit is certainly not
  m². Treat the number as unusable and use the ESP32 15 mm rule instead.
- Certifications (datasheet cover + minewsemi product page): CE, FCC, QDID/BQB, TELEC, WPC, RCM, IC, KC,
  RoHS, REACH.
- Price, MS88SF3-nRF52840 (**18.5 × 12.5 × 2.0 mm** SMD), LCSC **C20416747**, read 2026-09-03:
  **$2.374 @1 · $0.9481 @200 · $0.917 @500 · $0.900 @1000**, standard packaging 1000/full reel —
  **but "Out of Stock" on the day it was read.**
- MS88SF2-nRF52840 is JLCPCB **C20616655**, package "SMD, 23.2x17.4mm", **Extended** part;
  the JLCPCB part page showed **no stock and no price** on 2026-09-03.

---
## Ezurio (formerly Laird Connectivity) BL654 (nRF52840)
Source: <https://www.ezurio.com/wireless-modules/bluetooth-modules/bluetooth-5-modules/bl654-series-bluetooth-module-nfc>

- **15 × 10 × 2.2 mm**, "micro module with **castellated pads**".
- Variants 451-00001 / 451-00001C (integrated antenna) and 451-00002 / 451-00002C (IPEX MHF4).
- **NFC: yes, with the differential antenna pins NFC1 and NFC2 exposed**; an external NFC antenna is
  sold separately.
- Interfaces: UART, I2C, SPI, ADC, GPIO, PWM, FREQ, USB, NFC; up to 20 simultaneous BLE connections.
- Regulatory: **FCC, ISED, EU, UKCA, MIC, KC, AS-NZS, Taiwan, Brazil, Bluetooth SIG.**
- Price: the page renders 1K pricing as `$0.00000` — **no usable price**; distributor lookup needed.

---
## Fanstel BT832 / BT840 family (nRF52832 / nRF52840)
Sources: <https://www.fanstel.com/bt840> and <https://www.fanstel.com/bluenor-summaries-copy>

| part | SoC | size (mm) | antenna | pins | price |
|---|---|---|---|---|---|
| BT832 | nRF52832 | 14 × 16 × 1.9 | integrated PCB | 40 | **$4.46 @1k** |
| BT832F | nRF52832 | 15 × 20.8 × 1.9 | integrated PCB | 40 | **$4.93 @1k** |
| BT840F | nRF52840 | **15.0 × 20.8 × 1.9** | integrated PCB | 61 | **$7.17 @1k** |
| BT840 | nRF52840 | — | integrated PCB | 61 | **$6.88 @1–999, $6.09 @1k reel** |
| BT840E | nRF52840 | 14 × 16 × 1.9 | PCB **+ u.FL** | 61 | **$7.94 @10, $7.59 @100, $6.90 @1k** |
| BT840N / NE | nRF52840 | — | integrated (+u.FL on NE) | — | $8.81 / $9.91 @1k |
| BM833 | nRF52833 | 10.2 × 15 × 1.9 | integrated PCB | 42 GPIO | not listed |
| BC840M | nRF52840 | **7.1 × 12.2 × 1.5** (antenna area 10.1 mm wide) | integrated PCB | 48 GPIO | **$8.49 @10, $8.12 @100** |

BT840 page, verbatim: *"For applications needing limited number of IO pins, prototyping and production
are easier using **16 castellated pins**. Additional **43 LGA** pins provide full access to 48 GPIOs of
nRF52840."* — i.e. a hybrid: hand-solderable castellations for the common signals, LGA for the rest.
Certifications for BT840F, verbatim IDs: **FCC X8WBT840F · IC 4100A-BT840F · TELEC 201-190710/00 ·
KCC R-C-F8A-BT840 · Taiwan NCC CCAL22LP0381T0 · Brazil ANATEL 03583-22-14656 · BT QDID 108621.**

---
## u-blox ANNA-B112 (nRF52832)
Sources: <https://www.u-blox.com/en/product/anna-b112-open-cpu>;
Digi-Key <https://www.digikey.com/en/products/detail/u-blox/ANNA-B112-02B/26581133>

- **6.5 × 6.5 mm** form factor, internal antenna — the smallest fully certified nRF52 module found.
- Digi-Key package: **52-SMD Module**. nRF52832, 512 kB flash / 64 kB RAM, 1.7–3.6 V, +9 dBm, −96 dBm.
- Price at Digi-Key on 2026-09-03: **$6.99 @1**, **$5.71 @500 (tape & reel)**;
  **out of stock, 500 units expected 2026-12-22.**
- The EVK page (EVK-ANNA-B112C) advertises **NFC at 13.56 MHz**, so the NFC pins are usable.

---
## Holyiot 18010 (nRF52840)
Sources: AliExpress Holyiot Official Store <https://www.aliexpress.com/item/32868002366.html>;
Alibaba <https://www.alibaba.com/product-detail/Holyiot-Nordic-nRF52840-module-bt-low_60765200512.html>

- **18 × 14 × 1.6 mm**, nRF52840, certified **CE, FCC, RoHS** (per the listings).
- AliExpress price read 2026-09-03: **$6.58** sample price; the store's own range is **$4.30–$6.58**,
  MOQ 5 pcs.
- The detailed datasheet (manuals.plus mirror) returned **403** to automated fetch — pin list, pitch and
  NFC pin exposure are **NOT VERIFIED**.
- **Holyiot 21014 was not reached this session — no verified data. Do not quote numbers for it.**

---
## Ebyte E73-2G4M08S1C (nRF52840)
Source: <https://www.cdebyte.com/products/E73-2G4M08S1C>

- **13.0 × 18.0 mm**, 1.0 ± 0.1 g, nRF52840, four-layer module PCB, integrated antenna, SMD pads,
  "The module leads to most IO ports". BLE 4.2 / 5.0, 2.360–2.500 GHz.
- Certifications: the page says only *"pass various certifications"* — **no IDs, treat as UNVERIFIED**.
- Price: the page shows tier brackets (1–99, 100–999, 1000–2999, ≥3000) but **no numbers without a
  quotation request**. Not verified.
- Note (from lane C): the `nrfmicro` project already ships a KiCad footprint
  `E73-2G4M08S1C-52840.kicad_mod`, so this module has a ready open footprint.

---
## Seeed XIAO nRF52840 (a dev module, not a certified radio module)
Sources: <https://wiki.seeedstudio.com/XIAO_BLE/>, <https://www.seeedstudio.com/Seeed-XIAO-BLE-nRF52840-p-5201.html>

- **21 × 17.8 mm**, "single-sided components, surface mounting design", on-board Bluetooth antenna,
  11 × GPIO (PWM), 6 × ADC, UART/I2C/SPI/NFC.
- Price 2026-09-03: **$9.99 @1, $7.99 @10+.**
- Castellated pads exist (the wiki's "single-sided surface-mountable design"), but the wiki does not
  state a pitch, and **the XIAO is not itself a certified radio module** — it is a board built around one.
  Cost per unit is 2–10× the bare modules above. Useful as a bring-up vehicle, not as the block.
