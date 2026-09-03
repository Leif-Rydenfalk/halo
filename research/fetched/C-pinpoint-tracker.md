# PinPoint tracker — github.com/pinpoint-dev/tracker
Fetched 2026-09-03 (raw README + repo tree via WebFetch/curl)
Last commit (commits/main.atom): 2024-07-09

## README (verbatim, raw.githubusercontent.com/pinpoint-dev/tracker/main/README.md)

```
# tracker
The PinPoint tracker module pcb and cad files

This repository contains all the KiCAD EDA files and Fusion 360 CAD designs for the PinPoint tracker modules

### Features
- nRF52832-based board - [Ebyte E73-2G4M08S1E](https://www.cdebyte.com/products/E73-2G4M08S1E/2)
- Compatible with Apple's FindMy network through [OpenHaystack](https://github.com/seemoo-lab/openhaystack)
- Small form factor (ideally less than 30x30x10mm)
- Location Pin shape
- RGB led for flair
- piezo buzzer for finding

### Repository structure
- `pcb/` contains the KiCAD EDA files for the tracker module
- `cad/` contains the Fusion 360 CAD files for the tracker module
- `docs/` contains the datasheets and other documentation for the components used in the tracker module
- `LICENSE` contains the license information for the repository
- `README.md` contains the information about the repository

### Board To-Do
- [x] battery holder
- [x] mounting holes
- [x] SWD connector
- [x] piezo buzzer
- [x] USB interface
- [x] RGB led
- [x] Push button

### License
This project is licensed under the TAPR Open Hardware License. See [LICENSE.txt](/LICENSE.txt) for more information.
```

## Repo tree (fetched 2026-09-03)
Root: `docs/`, `pcb/`, `resources/`, `.gitignore`, `LICENSE.txt`, `README.md`
(NOTE: README mentions `cad/` but the root listing shows no `cad/` dir — Fusion360 files
appear NOT to be present. Unverified whether they were removed or never committed.)

`pcb/`: `lib/`, `production/`, `PinPoint.kicad_pcb`, `PinPoint.kicad_pro`, `PinPoint.kicad_sch`,
`fabrication-toolkit-options.json`, `fp-lib-table`, `sym-lib-table`

`resources/`: `board_outline.svg` — this is a generic map-pin icon from SVG Repo
(header: "Uploaded to: SVG Repo, www.svgrepo.com"), used as the PCB outline.

## LICENSE.txt first lines (curl, 2026-09-03)
```
The TAPR Open Hardware License
Version 1.0 (May 25, 2007)
Copyright 2007 TAPR - http://www.tapr.org/OHL
```

## Assessment
- Only open project found that is *simultaneously*: a purpose-built Find My tag,
  a full KiCad source design (not just gerbers), and licensed under a real OSHW licence.
- Uses an Ebyte E73 module, so no RF layout of our own is proved — but that also means
  the design is trivially portable and the RF section is a pre-certified block.
- Zero stars, 17 commits, single maintainer, quiet since 2024-07 — low community trust.
