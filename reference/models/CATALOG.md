# reference/models — CATALOG

Downloaded 2026-09-03 by research lane G. **Only files whose licence permits redistribution
are stored here** (CC0 / CC-BY / CC-BY-SA / MIT / GPL). Everything else is linked, not copied.

## Stored here

| Directory / file | Source URL | Author | Licence | Format | What it models | Fidelity |
|---|---|---|---|---|---|---|
| `airtag-classicgod/airtag_dimensions.dxf` | https://www.printables.com/model/629265-yet-another-airtag-model | ClassicGOD | CC BY 4.0 | DXF (2D half-section) | The AirTag revolved profile as splines + polylines. **The single most useful file here** — its ordinates reproduce Apple's own drawing callouts (Ø31.87 / Ø28.94 / Ø25.55 / Ø23.11, z = 0.88 / 1.89 / 2.29 / 7.98) and it resolves which end of Apple's Detail A ordinate run is the axis. Decoded in `research/fetched/G-airtag-profile-from-dxf.md`. | High — every callout cross-checks against Apple |
| `airtag-classicgod/airtag.step` | ditto | ClassicGOD | CC BY 4.0 | STEP AP214 | Solid revolve of the outer envelope from the DXF profile. No internals. | High (outer envelope only) |
| `airtag-classicgod/airtag.f3d` | ditto | ClassicGOD | CC BY 4.0 | Fusion 360 archive | Parametric source of the above. | High |
| `airtag-classicgod/airtag.stl`, `airtag.3mf` | ditto | ClassicGOD | CC BY 4.0 | STL / 3MF | Meshed envelope for printing / boolean subtraction. | High |
| `airtag-gustav-hires/AirTag.step`, `.f3d`, `.stl` | https://www.printables.com/model/255519-hi-res-apple-airtag-model-for-fusion-360-and-more | Gustav | CC BY 4.0 | STEP / F3D / STL | "High definition 3d model of an Apple AirTag made from the specs Apple provides." Outer envelope; author notes it omits "the flange between battery compartment and AirTag main body". | Medium-high — no flange |
| `airtag-gustav-hires/AirTag with cutouts.step`, `.f3d` | ditto | Gustav | CC BY 4.0 | STEP / F3D | The envelope plus negative-space bodies. | Medium-high |
| `airtag-gustav-hires/Cutout 0.15mm margin.stl`, `Cutout 0.30mm margin.stl` | ditto | Gustav | CC BY 4.0 | STL | Ready-made negative solids at +0.15 mm and +0.30 mm for boolean-subtracting an AirTag pocket out of a holder. Useful as a direct statement of the **fit tolerance the accessory world actually uses**. | Medium-high |
| `airtag-mediaman3d/Apple_AirTag_V2.stl` | https://www.printables.com/model/217805-apple-airtag-model | MediaMan3D | CC BY 4.0 | STL | Envelope built from the published 31.9 x 8 mm plus press photos, not from the drawing. The most-downloaded AirTag reference on Printables (4 428 downloads at fetch). | Medium — photo-derived, pre-dates the drawing |
| `ruuvitag-enclosure/ruuvitag-enclosure-base.step`, `-lid.step` | https://github.com/ruuvi/mechanics | Ruuvi Innovations | CC BY-SA 4.0 | STEP | The RuuviTag production enclosure, base + lid, from the vendor. Genuinely open-source hardware mechanics for a CR2477-class sensor puck; the clearest public example of a two-part snap-together open tracker case. | High (it is the vendor's own file) |
| `ruuvitag-enclosure/ruuvitag-pro-simplified-enclosure.step` | ditto | Ruuvi Innovations | CC BY-SA 4.0 | STEP | RuuviTag Pro enclosure, simplified. | High |
| `ruuvitag-enclosure/ruuvitag-ruuvitag-pro-main-dimensions.pdf` | ditto | Ruuvi Innovations | CC BY-SA 4.0 | PDF drawing | Dimensioned drawing, drawn 2022-06-08 per ASME Y14.5M-1994. | High |
| `ruuvitag-enclosure/README.md` | ditto | Ruuvi Innovations | CC BY-SA 4.0 | text | Licence statement. | — |

Attribution required for every file above. CC BY-SA files (Ruuvi) additionally require that
derivatives be released under CC BY-SA 4.0 — **do not merge Ruuvi geometry into a halo part
unless halo's mechanical files are themselves CC BY-SA**, or the share-alike propagates.

## Deliberately NOT stored — linked only

| Item | URL | Why not stored |
|---|---|---|
| Apple, *AirTag Dimensional Drawings* (the authoritative source) | https://developer.apple.com/download/files/accessories/dimensional-drawings/airtag.pdf (index: https://developer.apple.com/accessories/dimensional-drawings/) | Apple's own notice on the sheet forbids reproduction, copying and publication in whole or part. Numbers extracted into `research/fetched/G-apple-airtag-dimensional-drawing.md`; dimensions themselves are facts, the drawing is not ours to redistribute. |
| Apple, *Accessory Design Guidelines for Apple Devices*, R30 (2026-06-08) | https://developer.apple.com/accessories/Accessory-Design-Guidelines.pdf | Same. Note: as of R30 the guidelines no longer embed the drawings; §1.1 now says "Dimensional drawings are available at https://developer.apple.com/accessories/dimensional-drawings/". Earlier releases (R14, 2021-04-23, first to include AirTag) carried the AirTag sheet inline — a Printables author records it at **page 400**. |
| Printables 460110, "Apple AirTag Reference Model" by blake-rohde | https://www.printables.com/model/460110-apple-airtag-reference-model | CC BY-**NC**-SA. Non-commercial clause is outside the redistribution set for this repo. Content: STL **and STEP** of the AirTag plus **separate keepout solids for the speaker and antenna keepouts**, explicitly derived from the Apple guidelines. If a licence-compatible keepout solid is ever needed, rebuild it from the Ø25.75 / Ø37.31 numbers rather than copying this. |
| GrabCAD: `apple-airtag-2` ("Dimensionally accurate 3D solid model of the Apple AirTag as released April 30, 2021. Dimensions derived from Apple Accessory-Design-Guidelin[es]"), `apple-airtag-1` ("Apple AirTag Sizes from official site"), `airtag-gen1-1` ("AirTag - gen1. No internals. Enclosure only") | https://grabcad.com/library/apple-airtag-2 , https://grabcad.com/library/apple-airtag-1 , https://grabcad.com/library/airtag-gen1-1 | GrabCAD requires a login to download and its Terms of Service, not an open licence, govern the files. Descriptions above are from search-result snippets; the pages themselves are JavaScript-only. |
| Cults3D: "Apple AirTag Model from Official Apple Measurements (Fusion360 Source Files)" by Xuis | https://cults3d.com/en/3d-model/gadget/apple-airtag-model-from-official-apple-measurements-fusion360-source-files | Cults3D per-model licence, not verified as redistributable. Same lineage as the Printables files above (built from the Apple engineering drawing) so it adds nothing we do not already have under CC BY. |
| Thingiverse 4835415 (MediaMan, the original of the Printables entry), 5892530 | https://www.thingiverse.com/thing:4835415 , https://www.thingiverse.com/thing:5892530 | Same geometry as the CC BY Printables copy we already hold. |
| MakerWorld AirTag collections and models (e.g. 738242, 772185) | https://makerworld.com/en/collections/26173553-airtag , https://makerworld.com/en/models/772185-airtag | Holder/subtraction bodies rather than reference models; MakerWorld's default licence terms are not in the redistribution set. Useful only as further evidence of the outer envelope. |
| Sketchfab "Airtag" by lanrydersflus198 | https://sketchfab.com/3d-models/airtag-045e724fe63c4905ab580aca4b9ce669 | Visual/appearance mesh, no engineering value; licence per-model. |
| Espruino Puck.js case | https://github.com/espruino/EspruinoBoard/tree/master/Puck.js/case | Worth reading as the other open coin-cell-puck enclosure, but it is a CR2032 puck ~36 mm across and ~9 mm thick — larger than our envelope. Not copied because we do not need the geometry, only the precedent. |
| RuuviTag PCB-with-battery STEP (`ruuvitag-b5-pcb-with-battery.step`, 24.6 MB; `ruuvitag-b8-...zip`, 19.6 MB) | https://github.com/ruuvi/mechanics/tree/master/ruuvitag-pcb | CC BY-SA and freely downloadable, but 44 MB of solid model for a board we are not cloning. Fetch on demand. |

**No public model of the AirTag *internals* was found.** Every AirTag CAD file located in this
survey is an outer-envelope model intended for designing holders. There is no published
reconstruction of the PCB, the LDS antenna carrier, the magnet or the voice coil. That gap is a
measurement task for halo, not a search failure — see
`research/07-mechanical-enclosure-and-3d-models.md`, "What is not published".
