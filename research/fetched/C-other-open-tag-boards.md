# Other open coin-cell / beacon boards examined — lane C
All fetched 2026-09-03. Last-commit dates read from each repo's commits/<branch>.atom feed.

## Circuit-Digest/DIY-AirTag — https://github.com/Circuit-Digest/DIY-AirTag
Last commit 2024-07-31. **No LICENSE file** (raw .../main/LICENSE → 404) ⇒ all rights
reserved by default; NOT safe to vendor.
Hardware: Raytac MDBT50Q-1MV2 module (nRF52840), ADXL345 accelerometer, active buzzer,
multiple LEDs, CR2032. `PCB/` contains: `Airtag/` (folder), `Airtag Gerber.zip`, `Airtag.png`.
The EDA source format is not stated on the listing — gerbers are present, native sources unclear.
Firmware is a key-finder/loss-prevention app, *not* Find My / OpenHaystack.

## Sensirion/shtc3_ble_beacon — https://github.com/Sensirion/shtc3_ble_beacon
Last commit 2020-11-30. BSD-3-Clause. README (verbatim):
"Small CR2032 battery driven BLE beacon with Sensirion's humidity and temperature sensor"
Repository content: firmware (hex + source), schematics (schematics, PCB layout and gerber
files), housing (STEP file), software (Raspberry Pi readout).
Firmware based on Nordic nRF5 SDK v17 `ble_app_beacon` (so nRF52832-class, S132 softdevice).
No sounder, no NFC, no accelerometer. Board dimensions not stated in README.

## helena-project/squall — https://github.com/helena-project/squall
Last commit 2017-09-30. **No LICENSE file found** (LICENSE/LICENSE.md/COPYING all 404).
README (verbatim excerpt): "Squall is a low cost, 1 inch round BLE sensor tag based on the
Nordic nRF51822 BLE / Cortex M0 SoC. It is designed to be the basis for experimenting with
BLE tag platforms." Two variants: a stripped version at "raw cost just over $5" (SoC,
antenna, expansion headers, battery clip) and a USB version with serial bootloader, reset
button, 32 kHz crystal and rechargeable-battery charging. Daughter boards: Rain (wearable),
BLEES (environmental). Breakout + J-Link-to-tag-connect adapter boards also in the org.
=> The closest thing to a round, shield-expandable open coin tag, but nRF51 and 9 years stale.

## espruino/EspruinoBoard (Puck.js) — https://github.com/espruino/EspruinoBoard
Last commit 2025-03-12. LICENSE opens: "Copyright (c) 2013 Gordon Williams, Pur3 Ltd
All work in this repository (apart from Eagle Libraries) ..." (full terms in file; treat as
custom, verify before vendoring). Board folders: Original, Pico, WiFi, Puck.js, Pixl.js,
MDBT42, Bangle.js, Bangle.js2, Jolt.js, plus boxes and a Fritzing parts library.
Puck.js: nRF52832, CR2032, ~1 year battery, IR transmitter, magnetometer (LIS3MDLTR on v2,
MMC5603NJ on v2.1), LEDs, GPIO, round puck ~36 mm. Uses the Raytac MDBT42Q module — for which
this repo also carries an Eagle part library, i.e. a reusable module footprint.

## makerdiary/nrf52832-mdk — https://github.com/makerdiary/nrf52832-mdk
Last commit 2020-09-07. MIT ("Copyright (c) 2018 makerdiary.co"). docs/hardware/ carries
`nRF52832-MDK_SCH_V1.0.pdf`, `nRF52832-MDK_PCB_V1.0.pdf` and equivalents for V1.1/V2.0 plus
3D STEP. USB-dongle form factor, not coin-cell.

## adafruit/Adafruit-nRF52-Bluefruit-Feather-PCB
Last commit 2025-07-07. "Creative Commons Attribution, Share-Alike license" per README.
EagleCAD .sch/.brd for the nRF52832 Bluefruit Feather and nRF52840 Feather Express.
README explicitly warns the designs prioritise functionality over power efficiency and are
"not intended for low power usage" — disqualifying as a coin-cell tag reference.
OSHWA cert US000246 (Adafruit Feather nRF52840 Express, certified 2020-04-03): hardware
licence recorded as "Other", software MIT, documentation CC BY-SA.

## sparkfun/nRF52840_Breakout_MDBT50Q (SparkFun Pro nRF52840 Mini, DEV-15025)
Last commit 2020-06-17. Eagle .brd/.sch + production panels; SparkFun hardware is normally
CC BY-SA 4.0 (see LICENSE.md in repo — not individually re-verified here, mark unverified).
Raytac MDBT50Q module ⇒ another pre-certified nRF52840 module reference.

## Seeed-Studio/OSHW-XIAO-Series
Last commit 2026-07-16. MIT ("Copyright (c) 2024 Seeed-Projects").
XIAO nRF52840 (Sense): 21 x 17.5 mm, nRF52840, BQ25101 Li-ion charger, QSPI flash, USB-C,
onboard LSM6DS3TR-C IMU + PDM mic on the Sense. Li-po, not coin cell.

## NordicPlayground/nrf5-eagle-reference-design
Last commit 2022-03-22. LICENSE opens "Copyright (c) 2016, Nordic Semiconductor ASA
All rights reserved." (BSD-style clause list follows — verify exact terms before vendoring).
Contains nRF52832 QFAA, QFAA-DCDC and NFC variants as Eagle files + PDF printouts. Nordic
states only the **Altium** reference layouts are tested/verified; Eagle ones are conversions.
KiCad ports: jacobrosenthal/nrf52-kicad (QFAA-DCDC via altium2kicad) and
hlord2000/nordic-lib-kicad (symbols + footprints + reference-design blocks).

## Holyiot 21014 (nRF52810 beacon tag)
Zephyr board support exists upstream: boards/holyiot/holyiot_21014 in zephyrproject-rtos/zephyr
(nrfconnectdocs / docs.zephyrproject.org, fetched 2026-09-03): nRF52810, 192 KiB flash,
24 KiB RAM, one user button, RGB LED. Vendor listing: 30 mm diameter x 8.4 mm, 6.5 g, IP66,
CR2032, LIS2DH12 accelerometer, BLE 5.0, iBeacon/Eddystone.
**No public schematic found** — the only "open" artefact is the Zephyr board definition
(devicetree pin map), which is effectively a reverse-drawn partial netlist. This is the
closest off-the-shelf hardware match to an AirTag puck (30 mm round, CR2032, accelerometer)
and heystack-nrf5x lists Holyiot as tested.

## pix/heystack-nrf5x
Last commit 2024-10-18. **No LICENSE file found.** Firmware only, no hardware files.
Tested hardware per README: nRF51822 (AliExpress tags), nRF52810 (original Tile Tag and
Holyiot devices), nRF52832 (YJ-17024, YJ-17095 boards). Claims up to ~3 years on CR2032.

## dakhnod/FakeTag
Last commit 2026-06-22. MIT. nRF51 firmware, FindMy-compatible, no hardware files.
Author warns key generation / date decoding are undisclosed and it is "not meant to be used
by beginners".

## stacksmashing/airtag-hardware
Last commit 2021-08-08. **No licence stated.** Contains `pcb/` with merged PCB layer images
of the real AirTag; PCB work credited to David Hulton. Reference material for layout study
only — do not vendor.

## rayBeacon (openhardware.io/view/742)
nRF52833/nRF52840, CR2032/CR2025, **25 mm diameter round**, 2-layer PCB, 2 IP67 buttons,
RGB LED, 850 nm IR LED, NFC flex-antenna socket, 6 GPIO on an extension connector, 12-bit
ADC, USB pads. Gerbers + drill + schematic PDF + PCB layout published. **BSD licence.**
Author "Mishka"; created ~7 years ago, rev6 ~6 years ago (i.e. ~2019 — dormant).
The 25 mm 2-layer round nRF52 board with published gerbers is a very close geometric
precedent for a 30-32 mm haytag puck.

## Note on date discrepancies
Lane C read last-activity from each repo's `commits/<branch>.atom` feed on 2026-09-03;
lane B (research/02) used GitHub's last-push timestamp. These differ slightly, e.g.
pix/heystack-nrf5x: lane C 2024-10-18 (atom), lane B 2024-11-02 (push). Both are "dormant
since late 2024"; neither is wrong, they measure different events.
