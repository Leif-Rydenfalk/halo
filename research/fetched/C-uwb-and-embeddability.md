# UWB boards seen in passing + embeddability notes — lane C
Fetched 2026-09-03. **Lane H covers UWB in depth — this is only what lane C bumped into.**

## Open UWB boards
- **Bitcraze Loco Positioning deck** — Crazyflie 2.x expansion deck, Decawave DWM1000,
  ~10 cm accuracy. Schematic `loco_deck_revd.pdf` states it was drawn in **KiCad 4.0.2** and
  is licensed **CC-BY 4.0** (https://www.bitcraze.io/documentation/hardware/loco_deck/loco_deck_revd.pdf,
  also wiki.bitcraze.io/_media/projects:lps:loco_deck_revd.pdf). Drivers, node firmware and
  deck driver are open on Bitcraze's GitHub. Anchors/nodes are separate boards.
  Embeddable: it is a deck (a daughterboard with a defined header), so the DWM1000 block is
  physically separable, but the published artefact is a PDF schematic, not a KiCad module.
- **Makerfabs ESP32 UWB (DW1000)** and **Makerfabs ESP32 UWB DW3000** —
  https://github.com/Makerfabs/Makerfabs-ESP32-UWB-DW3000 and .../Makerfabs-ESP32-UWB.
  Hardware repos published by the vendor; ESP32 + DW3000 on one board. The DW3000 Arduino
  library in the repo was written by NConcepts, not Makerfabs, who only maintain the repo —
  so the library's licence needs separate checking. ESP32 power draw rules this class out for
  a coin cell (see below).
- **qqice/UWB-DW3000-NRF52** — DW3000 paired with an nRF52; the only nRF52+DW3000 board repo
  lane C saw. Not inspected in detail — lane H.
- **foldedtoad/dwm3000** — port of Qorvo/Decawave's DWM3000 module driver onto the DWS3000
  Arduino shield with nRF52840 (PCA10056) support. Firmware, not a board.
- Qorvo DWM3000EVB / DWS3000 shields are vendor evaluation hardware, not open designs.

## Why ESP32-class tags fail the coin-cell test
Hubble Network, "ESP32 Power Consumption in BLE Mode" (fetched 2026-09-03): a CR2032 on an
unconfigured ESP32 "dies by lunchtime"; datasheet light sleep is 0.8 mA and the real gap
between 100 mA and 0.15 mA is a configuration problem, not silicon. A BLE tag draws 5-15 mA
for a few milliseconds per advertisement, which is why nRF5x tags last years on the same cell.
Hackaday's 2022 AirTag clone (hackaday.com/2022/02/22/no-privacy-cloning-the-airtag/) was an
ESP32 "with no speaker and no serial number", and Make:'s DIY AirTag offers ESP32 **only with
a USB power bank**. Conclusion: ESP32/ESP32-S3 Find My tags are demo hardware, not products.

## Embeddability: what "publishable as a reusable block" looks like today
Nothing in the surveyed field publishes an RF section as a drop-in block. The two mechanisms
that exist:
1. **KiCad design blocks / hierarchical sheets.** KiCad 9 added reusable schematic design
   blocks that get *copied* into a new project (gitlab.com/kicad/code/kicad issue #2263 tracks
   the feature). Hierarchical sheets already let a subcircuit be a black box with hierarchical
   labels as its ports. This gives the schematic half of an embeddable block; the copper half
   still has to be re-laid or imported as a layout group.
   Related prior art: **skunkforce/edgy_boards**, which explicitly sets out to "decompose
   electronic circuits into testable, shareable and reusable basic blocks... what library code
   provides for software", built on KiCad hierarchical sheets.
2. **Buy the RF block as a module.** Every serious open tag surveyed does this: PinPoint uses
   Ebyte E73-2G4M08S1E, Circuit-Digest uses Raytac MDBT50Q-1MV2, SparkFun uses MDBT50Q,
   Puck.js uses Raytac MDBT42Q (and Espruino ships an **Eagle part library** for it), nrfmicro
   uses E73-2G4M08S1C (KiCad footprint `E73-2G4M08S1C-52840.kicad_mod` in the repo).
   A module is castellated, pre-certified (FCC/CE/BLE), and needs no RF layout from the host
   board — which is exactly the "anyone can drop it into their own outline" property GOAL.md
   asks for, at the cost of a few dollars and a few millimetres.
Implication for halo: ship BOTH — a bare-chip nRF5x sheet with a documented antenna keep-out
for people who can do RF, and a castellated halo-core module (or a blessed E73/MDBT42Q
variant) for everyone else. No existing project does this, so it is genuine new ground.
