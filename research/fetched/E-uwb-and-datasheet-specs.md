# E — UWB pricing and silicon datasheet specs (fetched 2026-09-03)

## Qorvo UWB — Digi-Key price breaks

### DW3110TR13 — https://www.digikey.com/en/products/detail/qorvo/DW3110TR13/24717583 (2026-09-03)
> IC RF TxRx Only 802.15.4 IR-UWB 6.5GHz, 8GHz 52-UFBGA, WLCSP
> In Stock: 7,406. Lead time 33 weeks (manufacturer standard).
| Qty | Unit price |
|---|---|
| 1 | $10.31 |
| 10 | $8.95 |
| 25 | $8.48 |
| 100 | $7.83 |
| 250 | $7.44 |
| 500 | $7.17 |
| 1,000 | $6.91 |
| 3,000 (T&R) | $5.84 |
Specs quoted on the same page: Frequency 6.5 GHz / 8 GHz; sensitivity −100 dBm; 6.8 Mbps max; supply 1.5 V–3.6 V; output power 14 dBm.

### DW3120TR13 — https://www.digikey.com/en/products/detail/qorvo/DW3120TR13/24611314 (2026-09-03)
> Stock 1,822. Package 52-UFBGA, WLCSP.
| Qty | Unit price |
|---|---|
| 1 | $11.28 |
| 25 | $10.05 |
| 100 | $9.23 |
| 250 | $8.61 |
| 500 | $8.00 |
| 1,000 | $7.22 |
| 3,000 (T&R) | $6.15 |

### DW1000-I-TR13 — https://www.digikey.com/en/products/detail/decawave-limited/DW1000-I-TR13/4499859 (2026-09-03)
> Lifecycle: Active. Stock 2,036. Package 48-VFQFN Exposed Pad (6x6).
| Qty | Unit price |
|---|---|
| 1 | $9.63 |
| 25 | $8.90 |
| 4,000 (T&R) | $7.28 |
Specs: 3.5–6.5 GHz, 6.8 Mbps max, supply 2.8–3.6 V.

### DWM3001C module — https://store.qorvo.com/products/detail/dwm3001c-qorvo/692453/ (2026-09-03)
> "UWB Module, 6.5 & 8 GHz, BLE SoC and Motion Sensor", 27 x 19.13 x 3.2 mm, 2.5–3.6 V.
| Qty | Unit price |
|---|---|
| 1–24 | $59.37 |
| 25–99 | $50.75 |
| 100–249 | $43.18 |
> In Stock: 32. Factory Stock: 0.
Digi-Key listed the same module at $49.47 (1 pc) — https://www.digikey.com/en/products/detail/qorvo/DWM3001C/16674526 (via search result snippet, 2026-09-03).

## DW3110 / DW3000 DC characteristics
Source: Qorvo DW3000 family datasheet as hosted by LCSC for C3040882 —
https://datasheet.lcsc.com/datasheet/pdf/43fb81298ea34a7c3613c2947bd4e739.pdf?productCode=C3040882
Table 5 "DC Characteristics", Tamb = 25 °C, all supplies at 3.0 V:

| Parameter | Typ. | Unit |
|---|---|---|
| Supply current DEEP SLEEP mode | 260 | nA |
| Supply current SLEEP mode | 850 | nA |
| Supply current IDLE mode channel 5 | 18 | mA |
| Supply current IDLE mode channel 9 | 32 | mA |
| Supply current IDLE-RC mode | 8 | mA |
| Supply current OSC start-up | 1.5 | mA |
| Current single frame TX CH5 (47 µF cap) | 14 | mA |
| Current single frame TX CH9 | 17 | mA |
| Current single frame RX CH5 | 16 | mA |
| Current single frame RX CH9 | 19 | mA |
| Peak continuous TX CH5 nominal power VDD2 | 23 | mA |

## nRF52832 (the AirTag BLE SoC) — power
Source: nRF52832 Product Specification as hosted by LCSC for C77540 —
https://datasheet.lcsc.com/datasheet/pdf/1aa6d7c89b6eb7e9c334420a8d103737.pdf?productCode=C77540

> "5.3 mA peak current in TX (0 dBm)"
> "0.3 μA at 3 V in System OFF mode"
> "0.7 μA at 3 V in System OFF mode with full 64 kB RAM retention"
> "1.9 μA at 3 V in System ON mode, no RAM retention, wake on RTC"

Current-consumption table (p. 77):
| Symbol | Description | Typ. |
|---|---|---|
| ION_RAMOFF_EVENT | System ON, no RAM retention, wake on any event | 1.2 µA |
| ION_RAMON_EVENT | System ON, full RAM retention, wake on any event | 1.5 µA |
| ION_RAMOFF_RTC | System ON, no RAM retention, wake on RTC | 1.9 µA |
| IOFF_RAMOFF_RESET | System OFF, no RAM retention, wake on reset | 0.3 µA |
| IOFF_RAMOFF_NFC | System OFF, no RAM retention, wake on NFC field | 0.7 µA |
| IOFF_RAMON_RESET | System OFF, full 64 kB RAM retention, wake on reset | 0.7 µA |

Also from https://www.nordicsemi.com/Products/nRF52832 (2026-09-03): "512/256 KB" flash,
"64/32 KB" RAM, "64 MHz Cortex-M4 with FPU", packages "QFN48 6x6mm" and "WLCSP 3.0x3.2mm",
supply "1.7 to 3.6 V", "NFC-A Tag" present.

## Other BLE SoC vendor pages (all fetched 2026-09-03)

- nRF52810 — https://www.nordicsemi.com/Products/nRF52810 : "192 KB Flash, 24 KB RAM",
  "64 MHz Cortex-M4", packages "QFN48 6x6mm", "QFN32 5x5mm", "WLCSP 2.5x2.5mm", 1.7–3.6 V.
  No NFC-A listed in key features.
- nRF52811 — https://www.nordicsemi.com/Products/nRF52811 : "192 KB Flash, 24 KB RAM",
  "6x6 mm QFN48 with 32 GPIOs", "5x5 mm QFN32 with 17 GPIOs", "2.48x2.46 mm WLCSP32 with 15 GPIOs",
  1.7–3.6 V, "Bluetooth Direction Finding". NFC-A not mentioned.
- nRF52833 — https://www.nordicsemi.com/Products/nRF52833 : "512 KB flash and 128 KB RAM",
  packages "aQFN73 7x7mm", "QFN405X5", "WLCSP3.175X3.175", "1.7 V to 5.5 V supply voltage range",
  "NFC-A" present.
- nRF54L15 — https://www.nordicsemi.com/Products/nRF54L15 : "1.5 MB NVM and 256 KB RAM",
  "128 MHz Arm Cortex-M33", packages "CSP47, QFN52, QFN48, QFN40" (CSP47 2.45 x 2.25 mm,
  QFN40 5 x 5 mm), "4.8 mA for TX @ 0 dBm (@ 3 V)", "3.4 mA for RX", sleep "from 0.7 μA to
  2.9 μA (@ 3 V)", 1.7–3.6 V, NFC yes, Bluetooth Channel Sounding yes.
- TI CC2340R5 — https://www.ti.com/product/CC2340R5 : "Up to 512KB of in-system programmable
  flash", "Up to 64KB of ultra-low leakage SRAM", "Optimized 48MHz Arm Cortex-M0+ processor",
  "5mm × 5mm RKP QFN40", "4mm × 4mm RGE QFN24", "2.2mm × 2.6mm YBG WCSP", "5.1mA TX at 0dBm",
  "5.3mA RX", "< 710nA standby mode", "165nA shutdown mode", "1.71V to 3.8V". No NFC.
- Silicon Labs EFR32BG22 — https://www.silabs.com/wireless/bluetooth/efr32bg22-series-2-socs :
  "Up to 512 kB flash program memory" with 32 kB RAM, "4.1 mA TX current @ 0 dBm output power",
  "3.6 mA RX current (1 Mbps GFSK)", "1.40 μA EM2 DeepSleep current (32 kB RAM retention and
  RTC running from LFXO)", QFN40 5x5x0.85 mm / QFN32 4x4x0.85 mm / TQFN32 4x4x0.30 mm,
  "1.71 V to 3.8 V". No NFC.
- Renesas DA14531 — https://www.renesas.com/en/products/wireless-connectivity/bluetooth-low-energy/da14531-smartbond-tiny-ultra-low-power-bluetooth-51-system-chip :
  "ROM (KB): 144", "RAM (KB): 48", "Memory Size (OTP) (KB): 32", "CPU: M0+",
  "FCGQFN: 2.2 x 3 x 0.65 mm, 24 leads", "WLCSP: 1.7 x 2 x 0.328 mm, 17 leads",
  "Tx Current (mA): 3.5", "Rx current (mA): 2.2", "Vcc (V): 1.1-3.6". No NFC.
  Note: OTP, not flash — field key rotation / reflash is constrained.

## Apple U1 interoperability (Nearby Interaction) — status
- Qorvo newsroom, "Qorvo UWB Solutions Certified for Apple U1 Interoperability" (2022-07-20),
  https://www.qorvo.com/newsroom/news/2022/qorvo-uwb-solutions-certified-for-apple-u1-interoperability
  — MFi certification was awarded for the **DW3110**; accessory makers integrate it and use
  Apple's Nearby Interaction. (Retrieved via search-result summary 2026-09-03; the Qorvo
  product page https://www.qorvo.com/products/p/DW3110 returned HTTP 429 on direct fetch.)
- Apple Find My network accessory program — https://developer.apple.com/find-my/ (2026-09-03):
  > "Whether you're a developer or manufacturer looking to connect an existing or new accessory
  > to the Find My network, enroll in the MFi Program to access the technical specifications and
  > resources needed to create your product."
  The page gives no chipset list and no UWB/Precision-Finding detail for third parties.
