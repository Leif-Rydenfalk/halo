# E — AirTag part list, published cost estimates, PCB/assembly fees, mechanical (fetched 2026-09-03)

## The AirTag (gen 1) chip list

iFixit, "AirTag Teardown: Yeah, This Tracks" — https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks (fetched 2026-09-03):
- "Apple U1 ultra-wideband transceiver"
- "Nordic Semiconductor nRF52832 Bluetooth low-energy SoC w/NFC controller"
- "GigaDevice GD25LE32D" — "32 Mb serial NOR flash"
- "Maxim MAX98357B" — "class AB digital audio amplifier"
- "Texas Instruments TLV9001" — "1-MHz, rail-to-rail I/O operational amplifier"
- "ON Semiconductor FPF2487" — "over-voltage protection load switch"
- "Texas Instruments TPS62746" — "300 mA DC-DC buck converter"
- Battery: "CR2032", 3 V, "approximately 0.66 Wh"
- Speaker: copper voice coil centred in the donut-shaped PCB, magnet drives the plastic
  battery cover as a diaphragm.

Adam Catley, "Apple AirTag Reverse Engineering" — https://adamcatley.com/AirTag.html
(copy in research/fetched/A-catley-airtag-reverse-engineering.md):
- "Nordic nRF52832 SoC with BLE and NFC, plus 32MHz and 32.768kHz crystals"
- "Apple U1 UWB Transceiver"
- "GigaDevice GD25LE32D 32Mbit NOR flash"
- "Bosch BMA280 accelerometer"   ← the exact Apple accelerometer part
- "Maxim MAX98357AEWL audio amplifier"
- "TI TPS62746 DC-DC buck converter"
- "TI TLV9001IDPWR opamp"
- Three antennas (BLE 2.4 GHz, NFC 13.56 MHz, UWB) laser-direct-structured onto one plastic
  frame and soldered to the PCB edge.
- NFC: "The AirTag uses the NFC-A peripheral of the nRF52832 to implement an NXP MIFARE Plus
  (Type 4) tag in read-only mode." — i.e. **no separate NFC IC**.
- Measured idle draw: "I measure a 2.3µA load on the battery while the AirTag is idle."
  Panasonic CR2032 at that load ≈ "almost the whole 225mAh". Powers up from ≥ 2 V.
- Speaker behaviour when separated: loud beep on motion, max 20 s, then silent 6 h.

TechInsights, "Apple AirTag Teardown" — https://www.techinsights.com/blog/apple-airtag-teardown
(fetched 2026-09-03):
- Retail price: "less than USD 30"
- **"estimated manufacturing cost of USD 10 (not including software costs and R&D)"**
- nRF52832 identified as 90 nm, WLCSP50 package; Apple U1 SiP on TSMC 16 nm, package area
  20.58 mm²; "Radio ICs occupy less than 30 mm2, or 6%, of the entire available PCB area".
- No line-by-line BOM is public without a TechInsights subscription
  (https://www.techinsights.com/technology/bom-database).

Apple retail price — https://www.apple.com/shop/buy-airtag/airtag (fetched 2026-09-03):
- 1 pack: "$29.00"; 4 pack: "$99.00"  → **$24.75/tag in the 4-pack**.

AirTag 2 (2026) — https://www.apple.com/airtag/ and
https://9to5mac.com/2026/02/05/ifixit-tears-down-new-airtag-finds-50-louder-speaker-still-100-easy-to-disable/
(both fetched 2026-09-03): "expanded Precision Finding range", speaker "50% louder",
teardown identifies "Apple's U2 Ultra Wideband chip"; the speaker is still two fine wires from
the coil to the PCB and is trivially disabled. No published dB figure for either generation was
found — Apple states only relative loudness. **We have no sourced absolute dB number for the
AirTag sounder; do not quote one.**

## JLCPCB fabrication and assembly fees

https://jlcpcb.com/help/article/pcb-assembly-price (fetched 2026-09-03):
- Setup fee: Economic PCBA **$8.18**; Standard PCBA **$25.56** single-side / **$51.12** double-side
- SMT assembly: **$0.0016/joint** (Economic, 1–100,000 joints; Standard same to 50,000, then
  $0.0013 and $0.0012)
- Stencil: Economic **$1.53**; Standard **$8.21** single-side / **$16.42** double-side
- Extended-component feeder labour: **$3.07** per extended part (Economic); $1.53 (Standard)
- Minimum **$0.48 per board** assembly surcharge; "Panelizing PCBs can help avoid this surcharge"

https://jlcpcb.com/news/discount-on-quality-4-layer-pcbs (announcement dated 2024-03-06,
fetched 2026-09-03):
- 4-layer board charge **$70.60 per square metre** (reduced from $75.1/m²)
- Worked example: 100 mm × 100 mm × 100 pcs (= 1 m²) → board price **$70.60**, total **$106.30**
- Worked example: 100 mm × 100 mm × 500 pcs (= 5 m²) → board price **$353**, total **$421.10**

PCBWay's online quote page (https://www.pcbway.com/orderonline.aspx, fetched 2026-09-03) shows
no default price: "Please click on Calculate to show price". **No PCBWay price was fetched.**

## Battery

Panasonic CR2032, Digi-Key (fetched 2026-09-03 from the coin-cell filter listing):
- Unit price at qty 1: **$0.39000**
- Capacity **225 mAh**, 3 V, lithium manganese dioxide, 20.0 × 3.2 mm, "Requires Holder"
- Stock 1,204,333
**Volume price breaks for the cell were not fetched** — the filter page showed only the qty-1
price and the direct product-detail URLs tried returned 404/wrong part. Treat $0.39 as an upper
bound at every quantity in the roll-ups below and label it as such.

## Mechanical / enclosure

Xometry, injection-moulding cost guide —
https://www.xometry.com/resources/injection-molding/injection-molding-cost/ (fetched 2026-09-03):
- Tooling for "mid-level orders (1,000-2,000 small parts)": "up to $10,000"
- Complex geometries / large orders: "up to $100,000"
- Overall: "range from $10,000 or less to $100,000, depending on order size, part complexity"
- Materials table 0.90–2.30 USD/lb; "injection molding cycle time takes up about 60% of final
  part cost"
- **No per-part price at a given volume is published in that guide** — the per-part figures in
  the roll-up are derived (tooling ÷ volume + a material/cycle estimate) and are labelled as
  estimates, not fetched prices.

JLC3DP's quote page (https://jlc3dp.com/3d-printing-quote, fetched 2026-09-03) shows no prices
without uploading a model: "Total Price" renders as "--". **No 3D-printing price was fetched.**

## Regulatory / module note (for the module-vs-bare-SoC cost delta)

Raytac module page https://www.raytac.com/product/ins.php?index_id=24 (fetched 2026-09-03),
MDBT50Q-1MV2 (nRF52840): certifications "FCC, IC, CE, Telec (MIC), KC, SRRC, NCC, RCM, WPC";
"10.5 x 15.5 x 2.05 mm"; "Chip Antenna". Raytac's MDBT42Q (nRF52832) page could not be located
by index sweep; **its certification list was not fetched.**

Ebyte E73-2G4M08S1C page https://www.cdebyte.com/products/E73-2G4M08S1C (fetched 2026-09-03):
"13.0*18.0mm", "1.0±0.1g". The page has a "Certifications" heading but **no certification
detail rendered** — so its FCC/CE/Giteki status is UNVERIFIED and must be treated as a risk.

47 CFR 15.212 (modular transmitters) could not be fetched — ecfr.gov redirected to
unblock.federalregister.gov. Lane F owns the legal text; this lane only carries the cost delta.
