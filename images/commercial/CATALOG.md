# images/commercial — FCC internal photographs of commercial Find My / Find Hub tags

Downloaded 2026-09-03 by research lane D.

## Licence / provenance

Every file here comes from an **FCC equipment-authorisation filing**. Exhibits filed with the
FCC's Office of Engineering and Technology are **US federal public records**, published by the
FCC at <https://www.fcc.gov/oet/ea/fccid> and mirrored by fccid.io. They are quoted here for
technical reference and are cited by FCC ID, applicant and exhibit number, as the FCC
publishes them. They are NOT under an open licence — they are public-record disclosures, and
the test-lab report layouts around them carry the labs' own branding (CTC advanced, Anbotek,
Sporton). Redistribute with the FCC ID attached, as below. Nothing here is Apple property and
no AirTag exhibit is included (Apple's AirTag internal photos are short-term confidential).

The `*_p-NN.png` files are page renders I made locally with `pdftoppm -png -r 150` from the
PDF beside them — same provenance, no new content.

## Files

| file | device | FCC ID | applicant / grant | exhibit | what is visible |
|---|---|---|---|---|---|
| `FCC_2AD85-C21M_Chipolo-ONE-Spot_internal-photos.pdf` (+ `_p-1..4.png`) | Chipolo ONE Spot | 2AD85-C21M | CHIPOLO d.o.o. (SI), grant 2021-05-05 | Internal Photos 5232705, lab CTC advanced doc 1-1830/21-01-01_AnnexB | p2: shell halves + Panasonic Industrial CR2032. p3: single small green PCB with a **meandered printed trace antenna** along one edge, one dominant QFN/WLCSP SoC, gold annular transducer pad on the rear. No LDS frame, no UWB, no NFC coil. Chip markings not legible at exhibit resolution. |
| `FCC_2AOKB-T87B0_eufy-SmartTrack-Link_internal-photos.pdf` (+ `_p-1..4.png`) | eufy SmartTrack Link (T87B0) | 2AOKB-T87B0 | Anker Innovations Ltd, grant 2022-05-25, 2402-2480 MHz, 0.0023 W | Internal Photos 5895281, lab Shenzhen Anbotek | p3: ~25 mm black-soldermask PCB, silkscreen "TTB2H-MAX-V07" + UL "E358074 94V-0", **silkscreened debug pads CLK / DIO / TX / RX / GND / 3V3**, tact switch marked KEY, gold buzzer contact ring. |
| `FCC_2AQI5-CM816_UGREEN-Smart-Finder_internal-photos.pdf` (+ `_p-1..3.png`) | UGREEN FineTrack Smart Finder CM816 | 2AQI5-CM816 | Ugreen Group Ltd, grant 2024-11-20, 0.002 W | Internal Photos 7833668 | p2: the lab's own red callouts read **"RF Chip"** (one ~4x4 mm QFN) and **"PCB Antenna"** (short meandered trace, silkscreen "UGREEN FM21-CM816 V1.0"). Rear view shows the CR2032 gold contact ring + a row of edge test pads. Board ~25 mm against the mm ruler in frame. |
| `FCC_IHDT6AB3_moto-tag_internal-photos.pdf` (+ `_p-01..08.png`) | Motorola moto tag (XT2445-1) | IHDT6AB3 | Motorola Mobility LLC, Sporton Intl report EP441117A, 2024-05-28 Rev 01 | Internal Photos 7355558 | p19 (`p-03`): enclosure halves + CR2032, ~32 mm disc. p21 (`p-05`): round ~26 mm green PCB, lab-annotated **"UWB Antenna"** and **"BLE Antenna"** as two SEPARATE edge antennas; test pads silkscreened **GND VBAT RST TXD RXD SWCLK SWDIO**; date code 2024-04-08; large gold piezo disc on the mating half. |
| `FCC_2AG5O-PB-531-BG_Pebblebee-Clip_internal-photos.pdf` (+ `_p-1..4.png`) | Pebblebee Clip (PB-531-BG) | 2AG5O-PB-531-BG | PB Inc, Issaquah WA, grant 2023-04-04, 0.00154 W | Internal Photos 6455481 | Rechargeable clip-form tracker internals. Block diagram and schematics were filed **metadata-only** (withheld from public view) — only the photographs are public. |

## What the photographs are evidence FOR

Read together they show the shape of the whole certified-third-party category: **one BLE SoC
in a small QFN or WLCSP, a printed or chip antenna, a piezo transducer, a coin cell or small
LiPo, one tact switch — on a single ~25 mm two-layer board.** Nobody except Apple builds a
voice-coil speaker or an LDS-plated antenna carrier, and only the moto tag carries UWB (and
does it with a second discrete antenna, not a shared frame).

They are NOT evidence for chip part numbers. Silicon identifications in
`research/04-commercial-tags-and-clones.md` come from vendor press releases and third-party
teardowns, cited there — not from these exhibits.
