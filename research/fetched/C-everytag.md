# Everytag — github.com/vasimv/Everytag
Fetched 2026-09-03. Last commit (commits/main.atom): 2026-04-22. License: GPL-3.0.

## What it is
AirTag / Google FMDN tag emulation firmware (Zephyr, nRF Connect SDK), fully
reconfigurable over BLE (no reflash to change settings). Emulates Apple AirTag
(up to 40 rotating public keys, default 10 min rotation) and Google Find My Device.

Supported targets listed in README: NRF52DK (nRF52832), NRF54L15DK (nRF54L15),
KKM C2 (nRF52805), KKM K4P, KKM P1 (nRF52810), KKM P11, Fanstel NRF52805EVM,
Minew HCB22E (nRF52832). OTA does not work on nRF52805/nRF52810 (flash size).

## hardware/ directory (fetched 2026-09-03)
EDA tool: **KiCad**. Files present:
- `Beacon-WirelessCharge.kicad_pcb`, `.kicad_sch`, `.kicad_pro`, `.kicad_prl`
- full Gerber set (*.gbr), `Beacon-WirelessCharge-job.gbrjob`, pnp_top/pnp_bottom
- drill: `Beacon-WirelessCharge-PTH.drl`, `-NPTH.drl`
- `ALTIUM_EMBEDDED_MODELS/`, `pcb_coils/`, `fp-lib-table`, `README.md`, `LICENSE`

## hardware/README.md content (fetched 2026-09-03)
- Beacon is 50x20x2 mm in the thin variant; 30x20 mm if height allows the battery
  to sit above the board. Battery: LIR2016 Li-ion (rechargeable).
- Qi/WPC wireless charging: Wurth 760308101104 receiving coil, Adafruit 2162
  charging module referenced; ferrite gasket + small magnet for self-alignment.
- Charge controller BQ25121A wired I2C-only to simplify layout.
- "reset pulse will be generated for the MCU" when placed on a charger — firmware
  must handle this.
- Small receive coil means it will not work with every Qi charger; recommends
  replacing the transmitter coil with a 20 mm one.
- BQ25121A + 0402 parts are hard to hand-solder; author recommends ordering
  assembled from PCBWay (~35 USD/board per the top-level README).

## Assessment
Firmware is the strongest part (actively maintained 2026, both Apple and Google
networks, BLE reconfiguration). The hardware is a rectangular wireless-charging
beacon, not an AirTag-shaped puck: no speaker, no NFC, no accelerometer on the board.
