# images/airtag — image catalogue (research lane A)

All images downloaded 2026-09-03. Each entry: filename — what it shows — source URL — license/attribution.

## Colin O'Flynn — `github.com/colinoflynn/airtag-re` (licensed **CC-BY-4.0**; commercial use OK with attribution to *Colin O'Flynn*, no permission request needed — stated in the repo README). Redistribution here is compliant.

- `oflynn-frontside-tpnames.jpg` — **Top ("front") side of the AirTag PCB with every test point numbered 1–38 plus VCC1/GND/VCC2 battery pads.** This is the master pin map. Silkscreen "820-01736-A", data code "2920 17", letter "C" visible. NFC coil, magnet well and speaker-coil solder pads (TP1/TP38) all visible. Source: https://github.com/colinoflynn/airtag-re/blob/master/images/frontside-tpnames.jpg
- `oflynn-frontside-1000px.jpeg` — Same top side, un-annotated, 1000 px. Source: https://raw.githubusercontent.com/colinoflynn/airtag-re/master/images/frontside-1000px.jpeg
- `oflynn-frontside-fullres.jpeg` — Same top side, full resolution (~2900 px). For reading fine silkscreen. Source: https://raw.githubusercontent.com/colinoflynn/airtag-re/master/images/frontside-fullres.jpeg
- `oflynn-frontside-26mm-cropped.jpg` — Top side cropped to the ~26 mm PCB diameter (plastic antenna carrier removed), showing the true board outline. Source: https://raw.githubusercontent.com/colinoflynn/airtag-re/master/images/frontside-26mm-cropped.jpg
- `oflynn-backside-1000px.jpeg` — **Bottom side of the PCB — the "heavy hitters" side.** nRF52832 (marked "N52832 CIAAE0 2102JK"), 32 MHz crystal ("T320 RBEV"), 32.768 kHz can ("A048L"), TPS62746 buck ("98C0051 TPS746"), U1 UWB shield-can (large rectangle, bottom), accelerometer, opamp. 1000 px. Source: https://raw.githubusercontent.com/colinoflynn/airtag-re/master/images/backside-1000px.jpeg
- `oflynn-backside-fullres.jpeg` — Same bottom side, full resolution (~2900×3400). Component markings are legible here. Source: https://raw.githubusercontent.com/colinoflynn/airtag-re/master/images/backside-fullres.jpeg
- `oflynn-airtag-tests.jpeg` — Bench photo: probing the SPI flash / test points with wires, used to prove connectivity. Source: https://raw.githubusercontent.com/colinoflynn/airtag-re/master/images/airtag-tests.jpeg

## FCC ID BCGA2187 internal photos — **US Government public record** (FCC filing; not copyrightable as a government-published record). Photo frames carry an Apple "Proprietary and Confidential" watermark but the exhibit was filed to the public FCC database with no confidentiality request. Rendered from the official 8-page PDF (`A2187_Internal_Photos_v1.0`, doc 5130978) at 150 dpi.

- `fcc-BCGA2187-internal-photo-1.jpg` — AirTag "Front" (white dome) beside a ruler, ~31–32 mm across.
- `fcc-BCGA2187-internal-photo-2.jpg` — AirTag "Back" — stainless battery cover with the two-circle logo/twist marks.
- `fcc-BCGA2187-internal-photo-3.jpg` — "Cover Removed – Back": Panasonic **CR2032 3V** coin cell in the battery well ("Made in Indonesia").
- `fcc-BCGA2187-internal-photo-4.jpg` — "Battery Removed": battery cavity showing the **3 sprung battery contacts** (one negative on the floor, two positive tabs on the wall) — the connector-less battery interface.
- `fcc-BCGA2187-internal-photo-5.jpg` — "Open back case with MLB": the assembled donut PCB in the white shell, **NFC Antenna** labelled (ring around the centre). Silkscreen "**920-08283-01**" and data code "3119" readable near the magnet well.
- `fcc-BCGA2187-internal-photo-6.jpg` — "MLB – Front": bare board out of the shell, labelled **Bluetooth Antenna**, **Bluetooth Module**, **UWB Module**, **UWB Antenna** — Apple's own functional labelling of the antenna carrier.
- `fcc-BCGA2187-internal-photo-7.jpg` — "MLB – Back": reverse of the bare board.
- `fcc-BCGA2187-internal-photo-8.jpg` — "Removed MLB": board with the central magnet/voice-coil assembly, "P1" marking.

Source for all 8: https://fccid.io/BCGA2187/Internal-Photos/A2187-Internal-Photos-v1-0-5130978

## Linked, NOT downloaded (license unclear or forbids redistribution — reference only)

- iFixit high-res teardown photos (front `AirTags_33.jpg`, back `AirTags_48.jpg`) and the drill/X-ray video — iFixit content is CC BY-NC-SA but the teardown *images* are not clearly relicensable; link only:
  - https://valkyrie.cdn.ifixit.com/media/2021/05/03133827/AirTags_33.jpg
  - https://valkyrie.cdn.ifixit.com/media/2021/05/03133839/AirTags_48.jpg
  - X-ray video: https://valkyrie.cdn.ifixit.com/media/2021/05/01153224/drill-xray-1.mp4
- Creative Electron X-ray + 360° spin of the AirTag (via the iFixit article) — Creative Electron imagery, all rights reserved; link only (in the iFixit article).
- Adam Catley PCB annotation, antenna photo, U1 photo, sound-energy plots — on https://adamcatley.com/AirTag.html ; no explicit reuse license, so linked in the dossier, not copied.
- siliconpr0n U1 die photo (`TMKA75` marking) — https://siliconpr0n.org/archive/doku.php?id=h1kari:apple:u1 ; CC terms vary per-submission, link only.
