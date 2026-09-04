# JLCPCB assembly files — halo_rev_a.kicad_pcb

**CANNOT DETERMINE** — 4 placed part(s) carry no LCSC number; JLC cannot source them. Generated 2026-09-04T10:40:07Z.

- 24 BOM lines, 44 CPL rows
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

## Notes

- [SKIPPED] `AE1` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP5` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `J2` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [POS-ONLY] `FID2` — exclude_from_bom: placed but not ordered
- [SKIPPED] `TP1` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP2` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP10` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP3` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP11` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP4` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [POS-ONLY] `FID1` — exclude_from_bom: placed but not ordered
- [SKIPPED] `TP7` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP9` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP8` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `TP6` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `LS1` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `J1` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [CANNOT DETERMINE] `C15` — no LCSC part number on C_0201_0603Metric. Looked for fields: LCSC Part #, LCSC Part, LCSC PN, LCSC P/N, LCSC Part No., LCSC Part Number, ...
- [CANNOT DETERMINE] `C17` — no LCSC part number on C_0201_0603Metric. Looked for fields: LCSC Part #, LCSC Part, LCSC PN, LCSC P/N, LCSC Part No., LCSC Part Number, ...
- [CANNOT DETERMINE] `C14` — no LCSC part number on C_0201_0603Metric. Looked for fields: LCSC Part #, LCSC Part, LCSC PN, LCSC P/N, LCSC Part No., LCSC Part Number, ...
- [CANNOT DETERMINE] `C16` — no LCSC part number on C_0201_0603Metric. Looked for fields: LCSC Part #, LCSC Part, LCSC PN, LCSC P/N, LCSC Part No., LCSC Part Number, ...
- [SKIPPED] `AE2` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
- [SKIPPED] `BT1` — footprint carries KiCad's exclude_from_pos attribute (a virtual/mechanical part)
