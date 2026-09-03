# images/designs — lane C catalogue

All items collected 2026-09-03. Nothing here is redistributed beyond what its licence allows;
attribution as recorded below must travel with any reuse.

| File | What it is | Source URL | Author | Licence | Why we kept it |
|---|---|---|---|---|---|
| `C-airtag-inside-3.jpg` | Photograph of a disassembled Apple AirTag, interior, showing the PCB and the coin cell seat (1280 px derivative of the Commons original) | https://commons.wikimedia.org/wiki/File:Inside_of_Airtag_-_3.jpg | KKPCW (Kyu3) | **CC BY-SA 4.0** | The parity target, photographed under a licence we may actually publish. Shows the connector-less battery contacts and the LDS antenna carrier that lane C's report says we cannot reproduce cheaply. |
| `C-airtag-inside-4.jpg` | Second interior photograph of a disassembled AirTag (1280 px derivative) | https://commons.wikimedia.org/wiki/File:Inside_of_Airtag_-_4.jpg | KKPCW (Kyu3) | **CC BY-SA 4.0** | Second angle on the same teardown. |
| `C-airtag-buttoncells-scale.jpg` | AirTag photographed next to loose button cells (1280 px derivative) | https://commons.wikimedia.org/wiki/File:Button_cells_and_Airtag.jpg | KKPCW (Kyu3) | **CC BY-SA 4.0** | Scale reference: how little annulus is left around a 20 mm CR2032 inside a ~32 mm puck. That annulus is the whole mechanical argument in `research/03-open-hardware-tag-designs.md`. |
| `C-ruuvitag-revb8-schematic.pdf` | RuuviTag Rev B8 full schematic, 1 page, exported from KiCad by Ruuvi | https://raw.githubusercontent.com/ruuvi/ruuvitag_hw/master/ruuvitag_revb8/ruuvitag_revb8_schematic.pdf | Lauri Jämsä / Ruuvi Innovations Ltd | **CC BY-SA 4.0** (per repo README; derived products may not use the name "Ruuvi") | The reference open coin-cell nRF52832 design: NFC-A antenna, LIS2DH12, DPS310/TMP117, CR2477 front end. Read it before drawing haytag's sheet. Share-alike — copying from it makes our board BY-SA. |
| `C-pinpoint-board-outline.svg` | The PCB outline artwork the PinPoint tracker uses — a generic map-pin icon, not a board render | https://raw.githubusercontent.com/pinpoint-dev/tracker/main/resources/board_outline.svg | Original icon from SVG Repo (svgrepo.com), committed into pinpoint-dev/tracker | Repo is **TAPR OHL v1.0**; the icon itself carries an SVG Repo provenance header and its own upstream terms were **not verified** — treat as reference only, do not ship | Documents an honest finding: the one open Find My tag's "location pin shape" is a downloaded icon, not a mechanical study. Useful as a caution, not as a source. |

## Things deliberately NOT downloaded
- `stacksmashing/airtag-hardware` merged PCB layer images — **no licence stated** in that repo.
  Excellent layout study material, but not redistributable. Read in place:
  https://github.com/stacksmashing/airtag-hardware
- Any image from `Circuit-Digest/DIY-AirTag` — repo has **no LICENSE file** (verified 404 on
  `raw.githubusercontent.com/Circuit-Digest/DIY-AirTag/main/LICENSE`), so all rights reserved.
- rayBeacon renders from openhardware.io — the design is BSD but the site's image terms were
  not verified.
- Commons has **no** RuuviTag, Puck.js or nRF52-beacon photographs (searched 2026-09-03);
  the schematic PDF above is the best freely-licensed artefact of an open tag that exists.
