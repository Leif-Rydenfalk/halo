# Antenna, NFC coil and coin-cell mechanical resources — lane C
Fetched 2026-09-03.

## What the AirTag actually does (target to beat)
Adam Catley, https://adamcatley.com/AirTag (fetched 2026-09-03):
NFC (13.56 MHz) on the back, BLE (2.4 GHz) on the left, and a smaller antenna on the right
believed to be UWB (6.24 / 8.23 GHz). All three are etched onto a **single piece of plastic
using Laser Direct Structuring (LDS)** and soldered to the PCB around the edge. Components:
nRF52832 (BLE + NFC) with 32 MHz and 32.768 kHz crystals, Apple U1 UWB, GigaDevice
GD25LE32D 32 Mbit NOR flash, Bosch BMA280 accelerometer, Maxim MAX98357A audio amp,
TI TPS62746 buck. Speaker = voice coil glued to the outer plastic shell, which is the
diaphragm, driven against a fixed magnet. Playing sound draws ~8 mA, ">3000x more power
than being asleep".
Hackaday 2026-02-02 "Teardown Of An Apple AirTag 2 With Die Shots" (fetched 2026-09-03):
AirTag 2 moves to an **nRF52840**, keeps a UWB module, a Bosch accelerometer and an SPI
EEPROM; the speaker sits in a sandwiched ring surrounded by the UWB antenna, PCB beneath.
=> LDS is not reproducible cheaply. A haytag must use a PCB-etched 2.4 GHz antenna (or a
module with one) plus a PCB-spiral NFC coil.

## 2.4 GHz PCB antenna, open sources
- https://github.com/harsh-hw-dev/2.4ghz-ifa-antenna — reusable 2.4 GHz inverted-F, 50 Ω,
  FR-4, edge placement; ships an **Altium** schematic symbol, footprint and integrated library.
- https://github.com/TobleMiner/kicad-ifa — IFAs designed for KiCad (footprint library).
- https://github.com/prasad-dot-ws/ESP32_MIFA_PCB_ANTENNA — recommended ESP32 meandered-IFA
  footprint for KiCad.
- https://github.com/tommag/kicad-lib .../PCB_IF_ANT_2.4G.kicad_mod and
  tessel/tm-kicad-library .../2.4GHz-INVERTED-F-ANTENNA.kicad_mod — single-file KiCad
  footprints, the tessel one derived from TI DN0007.
- Silicon Labs AN1088 "Designing with an Inverted-F 2.4 GHz PCB Antenna"
  https://www.silabs.com/documents/public/application-notes/an1088-designing-with-pcb-antenna.pdf
Design rule repeated everywhere: IFA/MIFA is a quarter-wave printed structure, must sit at
the board edge with **no ground or copper under or beside it**. On a 30 mm round board with a
20 mm coin cell in the middle, that keep-out is the hardest geometric constraint.

## NFC coil
- https://github.com/nideri/nfc_antenna_generator — generates an NFC antenna module for KiCad
  (parametric spiral).
- KiCad.info "KiCad Antenna Line Generator" thread — generator built around the
  STMicroelectronics NFC inductance RF design tool.
- Nordic's own reference designs include an `nRF52832_qfaa_nfc` variant (Eagle) in
  NordicPlayground/nrf5-eagle-reference-design.
- RuuviTag ships a working NFC-A tag antenna in KiCad under CC BY-SA 4.0 — the most directly
  reusable open NFC coil for an nRF52 (see C-ruuvitag.md).

## Coin cell mechanical
- KiCad official footprint `BatteryHolder_Keystone_3034_1x20mm.kicad_mod`
  (Battery.pretty) — SMD retainer for 2020/2025/2032.
  **Known defect**: KiCad/kicad-footprints issue #1896 "BatteryHolder_Keystone_3034 does not
  make contact" — boards built with it failed to contact the cell, probably soldermask
  thickness. Check the pad/soldermask stack before using it.
- AirTag itself uses no holder: the shell presses the cell onto board contacts (see Catley
  teardown and the Commons internal photos in images/designs/). That saves the holder BOM
  line and ~1.5 mm of height but pushes cost into the enclosure.
- Keystone 3002 / spring-finger contacts are the alternative when the enclosure does the
  retaining. (Part choice not researched further here — lane D covers BOM cost.)

## Speaker / sounder
- AirTag: custom voice coil + shell diaphragm. Not buyable.
- Practical open substitutes seen in the surveyed projects: piezo buzzer (PinPoint),
  active magnetic buzzer (Circuit-Digest DIY-AirTag), or a MAX98357A-class amp + micro
  speaker as Apple does (CUI/Same Sky CDS-20144-L100, 4 Ω 1 W 92 dB, $5.45 at DigiKey — used
  in Will Siffer's wallet-AirTag build, DigiKey maker.io, 2023-01-24). A $5.45 speaker blows
  the BOM; a piezo is cents but much quieter and needs a resonant cavity in the enclosure.
