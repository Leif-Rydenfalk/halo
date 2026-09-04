# JLCPCB assembly files — halo_rev_a.kicad_pcb

**FAIL** — 23 BOM lines, all with an LCSC number. Generated 2026-09-04T22:06:39Z.

- 23 BOM lines, 40 CPL rows
- place-file origin: [0.0, 0.0] mm (KiCad's aux axis origin; JLC coordinates are relative to it)
- rotation table: data/vendor/transformations.csv (bennymeg/JLC-Plugin-for-KiCad @038cd1d, retrieved 2026-09-03)
- transform: plugins/process.py:222-252, reimplemented

- gerber zip: `halo_rev_a-gerber-jlc.zip` — 13 files, named for JLCPCB published table, layer check **PASS**: every layer JLCPCB's published table names is in the zip under its published extension, plus 2 Excellon drill file(s) and a drill map
- origin: aux (drill/place) origin, shared with the CPL: gerbers --use-drill-file-origin, drill --drill-origin plot
- layers exported: `F.Silkscreen,F.Mask,F.Cu,In1.Cu,In2.Cu,B.Cu,B.Mask,B.Silkscreen,Edge.Cuts`

| KiCad wrote | in the zip as |
|---|---|
| halo_rev_a-B_Cu.gbl | **halo_rev_a.GBL** |
| halo_rev_a-B_Mask.gbs | **halo_rev_a.GBS** |
| halo_rev_a-B_Silkscreen.gbo | **halo_rev_a.GBO** |
| halo_rev_a-Edge_Cuts.gm1 | **halo_rev_a.GKO** |
| halo_rev_a-F_Cu.gtl | **halo_rev_a.GTL** |
| halo_rev_a-F_Mask.gts | **halo_rev_a.GTS** |
| halo_rev_a-F_Silkscreen.gto | **halo_rev_a.GTO** |
| halo_rev_a-In1_Cu.g1 | **halo_rev_a.G2L** |
| halo_rev_a-In2_Cu.g2 | **halo_rev_a.G3L** |
| halo_rev_a-NPTH-drl_map.gbr | **halo_rev_a-NPTH-drill-map.gbr** |
| halo_rev_a-NPTH.drl | **halo_rev_a-NPTH.XLN** |
| halo_rev_a-PTH-drl_map.gbr | **halo_rev_a-PTH-drill-map.gbr** |
| halo_rev_a-PTH.drl | **halo_rev_a-PTH.XLN** |
- dropped `halo_rev_a-job.gbrjob` — Gerber job file — not one of the layers JLCPCB's table names, and 'any other layers ... should be remarked' when ordering

> "Recommended layer names in the Gerber file ... boardname.GTL Top Layer ... boardname.GKO/GM1 Board Outline" — jlcpcb.com/help/article/592-gerber-files-preparation, read via web.archive.org/web/20240324142101 on 2026-09-03

## Rotation corrections applied

| Ref | Footprint | KiCad rot | + correction | JLC rot | matched pattern |
|---|---|--:|--:|--:|---|
| U1 | QFN-48-1EP_6x6mm_P0.4mm_EP4.4x4.4mm | 0.0 | 90.0 | 270.0 | `^QFN-` |

## Cross-check against `kicad-cli pcb export pos`

**FAIL** — 31 designator(s) agree, 9 disagree

> kicad-cli applies no JLC rotation correction; rows with a correction are compared against kicad_rot + correction.
- `C9` DISAGREE {'ref': 'C9', 'verdict': 'DISAGREE', 'dx_mm': 0.0, 'dy_mm': 0.0, 'drot_deg': 16.0, 'kicad': ['21.417279', '-14.182971', '-82.000000'], 'cefab': [21.4173, -14.183, 262.0]}
- `U1` DISAGREE {'ref': 'U1', 'verdict': 'DISAGREE', 'dx_mm': 0.0, 'dy_mm': 0.0, 'drot_deg': 180.0, 'kicad': ['13.187500', '-13.000000', '0.000000'], 'cefab': [13.1875, -13.0, 270.0]}
- `L1` DISAGREE {'ref': 'L1', 'verdict': 'DISAGREE', 'dx_mm': 0.0, 'dy_mm': 0.0, 'drot_deg': 100.0, 'kicad': ['18.592124', '-8.307650', '-40.000000'], 'cefab': [18.5921, -8.3077, 220.0]}
- `C12` DISAGREE {'ref': 'C12', 'verdict': 'DISAGREE', 'dx_mm': 0.0, 'dy_mm': 0.0, 'drot_deg': 110.0, 'kicad': ['8.124600', '-19.962792', '35.000000'], 'cefab': [8.1246, -19.9628, 145.0]}
- `U2` DISAGREE {'ref': 'U2', 'verdict': 'DISAGREE', 'dx_mm': 0.0, 'dy_mm': 0.0, 'drot_deg': 180.0, 'kicad': ['12.064784', '-20.648537', '0.000000'], 'cefab': [12.0648, -20.6485, 180.0]}
- `C10` DISAGREE {'ref': 'C10', 'verdict': 'DISAGREE', 'dx_mm': 0.0, 'dy_mm': 0.0, 'drot_deg': 148.0, 'kicad': ['15.342918', '-21.170724', '-16.000000'], 'cefab': [15.3429, -21.1707, 196.0]}
- `C11` DISAGREE {'ref': 'C11', 'verdict': 'DISAGREE', 'dx_mm': 0.0, 'dy_mm': 0.0, 'drot_deg': 16.0, 'kicad': ['4.582721', '-11.817029', '-82.000000'], 'cefab': [4.5827, -11.817, 262.0]}
- `X2` DISAGREE {'ref': 'X2', 'verdict': 'DISAGREE', 'dx_mm': 0.0, 'dy_mm': 0.0, 'drot_deg': 60.0, 'kicad': ['19.408588', '-16.700000', '-60.000000'], 'cefab': [19.4086, -16.7, 240.0]}
- `X1` DISAGREE {'ref': 'X1', 'verdict': 'DISAGREE', 'dx_mm': 0.0, 'dy_mm': 0.0, 'drot_deg': 68.0, 'kicad': ['7.196737', '-9.085650', '-56.000000'], 'cefab': [7.1967, -9.0856, 236.0]}

## Notes

- [POS-ONLY] `FID1` — exclude_from_bom: placed but not ordered
- [SKIPPED] `TP9` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `M1` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `J1` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `LS1` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP1` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `AE1` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP7` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP11` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP10` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [POS-ONLY] `FID2` — exclude_from_bom: placed but not ordered
- [SKIPPED] `TP2` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP3` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP8` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `J2` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP5` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP6` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP4` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `AE2` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [DNP] `C17` — marked do-not-place; left out of both files
- [SKIPPED] `BT1` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [DNP] `C15` — marked do-not-place; left out of both files
- [DNP] `C14` — marked do-not-place; left out of both files
- [DNP] `C16` — marked do-not-place; left out of both files
