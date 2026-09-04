# DFM — halo_rev_a.kicad_pcb against `jlc-4layer`

**FAIL** — 26 PASS, 2 FAIL, 0 CANNOT DETERMINE, of the PASSes 3 VACUOUS (the board carries no item the rule governs — satisfied, not covered). Generated 2026-09-04T22:06:53Z.

*Rule set: JLCPCB 4-layer FR4, 1 oz outer / 0.5 oz inner — published capability limits*

Board: 25.6138 x 26.0 mm, 4 copper layers, 0.6 mm, 62 footprints, 49 vias, 255 track segments.

> **81 unconnected item(s)** — the ratsnest. Not a fab-capability failure and not counted above, but this board is not finished.

> Netclass `Default` was **replaced** for this run: clearance=0.127, track_width=0.127, via_diameter=0.45, via_drill=0.25 -> clearance=0.09, track_width=0.09, via_diameter=0.25, via_drill=0.15. KiCad enforces the NETCLASS clearance, not the board setup floor, so a run against the designer's own netclass measures the designer's preference and not the fab's limit.

| Rule | Limit | Measured | Verdict | How | Why |
|---|--:|--:|---|---|---|
| **smd_pad_min** — Minimum SMD pad size (each side) | 0.25 | 0.15 | FAIL | geometry | narrowest side of any of 254 SMD pads. Solderable lands: 0.2 mm over 175; net-tie pads (copper join, nothing soldered to them): 0.15 mm over 2; unnumbered paste-relief apertures (no land): 0.318 mm over 77 |
| **smt_min_package** — Smallest component package | — | C_0201_0603Metric, L_0201_0603Metric, R_0201_0603Metric | FAIL | footprint names | 3 footprint(s) smaller than the Economic 0402 floor: ['C_0201_0603Metric', 'L_0201_0603Metric', 'R_0201_0603Metric'] |
| **blind_buried_vias** — Blind / buried vias | — | 0 | PASS | geometry | 0 blind/buried/micro via(s); the fab makes through holes only |
| **board_size_max** — Maximum board dimensions, 4-layer FR4 | 663 x 593 | 25.6138 x 26.0 | PASS | geometry | 25.6138 x 26.0 mm against 663 x 593 mm |
| **board_size_min** — Minimum board dimension (fabrication) | 3.0 | 25.6138 x 26.0 | PASS | geometry | 25.6138 x 26.0 mm against a 3.0 mm floor |
| **board_thickness_options** — Selectable FR4 thicknesses | 0.4, 0.6, 0.8, 1.0, 1.2, 1.6, 2.0 | 0.6 | PASS | geometry | 0.6 mm is one of the selectable FR4 thicknesses |
| **castellated_hole_min** — Minimum castellated (half) hole diameter | 0.5 | 0 | PASS | geometry | no plated hole straddles the board outline, so the board declares no castellations |
| **copper_to_edge_min** — Copper clearance from routed board edge | 0.2 | — | PASS | kicad-cli pcb drc | KiCad DRC, constraint `min_copper_edge_clearance` = 0.2 mm: no violation |
| **drill_min** — Minimum plated drill diameter | 0.15 | — | PASS | kicad-cli pcb drc | KiCad DRC, constraint `min_through_hole_diameter` = 0.15 mm: no violation |
| **inner_pth_to_copper_min** — Inner-layer PTH pad hole to copper clearance | 0.3 | — | PASS | kicad-cli pcb drc (custom) | KiCad DRC, custom rule `jlc_inner_pth_to_copper` from the .kicad_dru written beside the board: no violation  — the rule never fired even with its limit multiplied by 40, AND THIS BOARD CARRIES NO ITEMS IT GOVERNS: 0 plated through-hole pad(s) on a 4-layer board. Nothing was checked because there is nothing to check; this is not coverage. |
| **inner_via_to_copper_min** — Inner-layer via hole to copper clearance | 0.2 | — | PASS | kicad-cli pcb drc (custom) | KiCad DRC, custom rule `jlc_inner_via_to_copper` from the .kicad_dru written beside the board: no violation |
| **pad_hole_to_hole_min** — PTH pad hole-to-hole spacing | 0.45 | — | PASS | kicad-cli pcb drc (custom) | KiCad DRC, custom rule `jlc_pad_hole_to_hole` from the .kicad_dru written beside the board: no violation  — the rule never fired even with its limit multiplied by 40, AND THIS BOARD CARRIES NO ITEMS IT GOVERNS: 0 pad(s) with a hole. Nothing was checked because there is nothing to check; this is not coverage. |
| **pad_to_silk_min** — Pad to silkscreen clearance | 0.15 | — | PASS | kicad-cli pcb drc | KiCad DRC, constraint `min_silk_clearance` = 0.15 mm: no violation |
| **pad_to_track_min** — Pad to track clearance | 0.1 | — | PASS | kicad-cli pcb drc (custom) | KiCad DRC, custom rule `jlc_pad_to_track` from the .kicad_dru written beside the board: no violation |
| **pth_to_track_min** — PTH to track clearance | 0.28 | — | PASS | kicad-cli pcb drc (custom) | KiCad DRC, custom rule `jlc_pth_to_track` from the .kicad_dru written beside the board: no violation  — the rule never fired even with its limit multiplied by 40, AND THIS BOARD CARRIES NO ITEMS IT GOVERNS: 0 plated through-hole pad(s) and 255 track segment(s). Nothing was checked because there is nothing to check; this is not coverage. |
| **silk_line_width_min** — Minimum silkscreen line width | 0.15 | — | PASS | kicad-cli pcb drc | KiCad DRC, constraint `min_text_thickness` = 0.15 mm: no violation |
| **silk_text_height_min** — Minimum silkscreen text height | 1.0 | — | PASS | kicad-cli pcb drc | KiCad DRC, constraint `min_text_height` = 1.0 mm: no violation |
| **smd_pad_to_pad_min** — SMD pad to pad clearance, different nets | 0.15 | — | PASS | kicad-cli pcb drc (custom) | KiCad DRC, custom rule `jlc_smd_pad_to_pad` from the .kicad_dru written beside the board: no violation |
| **smt_board_size** — Single board size accepted for SMT assembly | — | 25.6138 x 26.0 | PASS | geometry | Economic PCBA accepts it; BELOW the 70 x 70 mm Standard-PCBA floor — this board must be panelized to be assembled on the Standard line |
| **smt_layers** — Layer counts accepted for assembly | — | 4 | PASS | geometry | board has 4 copper layers; this rule set is the 4-layer process |
| **smt_sides** — Sides assembled | — | 2 | PASS | geometry | 13 part(s) on the bottom — Economic PCBA is single-sided only, so this is Standard PCBA |
| **track_spacing_min** — Minimum track-to-track spacing | 0.09 | — | PASS | kicad-cli pcb drc | KiCad DRC, constraint `min_clearance` = 0.09 mm: no violation |
| **track_width_min** — Minimum track width | 0.09 | 0.15 | PASS | geometry (KiCad DRC checks this too) + kicad-cli pcb drc | KiCad DRC, constraint `min_track_width` = 0.09 mm: no violation  ||  geometry: narrowest of 255 track segments |
| **via_annular_ring_min** — Minimum via annular ring (per side) | 0.05 | 0.1 | PASS | geometry + kicad-cli pcb drc | KiCad DRC, constraint `min_via_annular_width` = 0.05 mm: no violation  ||  geometry: (diameter - drill) / 2, per side |
| **via_diameter_min** — Minimum via pad diameter | 0.25 | 0.45 | PASS | geometry + kicad-cli pcb drc | KiCad DRC, constraint `min_via_diameter` = 0.25 mm: no violation  ||  geometry: smallest via pad diameter |
| **via_drill_min** — Minimum via hole (drill) diameter | 0.15 | 0.25 | PASS | geometry | smallest via drill on the board, over 49 vias |
| **via_hole_to_hole_min** — Via hole-to-hole spacing (edge to edge) | 0.2 | — | PASS | kicad-cli pcb drc | KiCad DRC, constraint `min_hole_to_hole` = 0.2 mm: no violation |
| **via_to_track_min** — Via hole to track clearance | 0.2 | — | PASS | kicad-cli pcb drc | KiCad DRC, constraint `min_hole_clearance` = 0.2 mm: no violation |

## PASSes that measured nothing

These rules could not be broken by this board because it carries no item they govern. The count is the proof, and it is stated so the row is never read as coverage.

- **inner_pth_to_copper_min** — governs 0 plated through-hole pad(s) on a 4-layer board; 0 item(s) on this board
- **pad_hole_to_hole_min** — governs 0 pad(s) with a hole; 0 item(s) on this board
- **pth_to_track_min** — governs 0 plated through-hole pad(s) and 255 track segment(s); 0 item(s) on this board

## The published lines these rules were transcribed from

- **smd_pad_min** — “Minimum SMD pad: 0.25mm × 0.25mm”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **smt_min_package** — “Minimum Package — 0402 / 0201”  [https://jlcpcb.com/capabilities/pcb-assembly-capabilities retrieved 2026-09-03]
- **blind_buried_vias** — “Not supported — Currently we don't support Blind/Buried Vias, only make through holes.”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **board_size_max** — “FR4(4-layer): 663 × 593 mm ... These limits apply to PCBs with thickness ≥ 0.8 mm. The thinner FR4 PCBs are 599 × 497 mm maximum. ... 4-layer FR4 PCBs can reach a maximum size of 1016 × 596 mm.”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **board_size_min** — “Minimum Dimensions — FR4/Rogers/PTFE: 3 × 3 mm; Castellated / Plated Edges: 10 × 10 mm ... These limits apply to PCBs with thickness ≥ 0.6 mm. Manual review required for thinner PCBs. Panelization is recommended for small-sized boards.”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **board_thickness_options** — “Thickness — 0.4 – 4.5 mm — Thickness for FR4 are: 0.4/0.6/0.8/1.0/1.2/1.6/2.0 mm (2.5 mm and above are for 12+ layer PCBs only)”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **castellated_hole_min** — “Min. Castellated Holes — 0.5mm — Castellated holes are metalized half-holes on PCB edges… ① Hole diameter (Φ): ≥ 0.5 mm”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **copper_to_edge_min** — “① Copper clearance from routed board edges: ≧0.2 mm ② Copper clearance from routed slots: ≧0.2 mm”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **drill_min** — “Drill Diameter ... Multilayer: 0.15 – 6.3 mm ... Min. drill diameter for 2- or more-layer PCBs is 0.15 mm (more costly!)”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **inner_pth_to_copper_min** — “Inner layer PTH pad hole to copper clearance — 0.3mm”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **inner_via_to_copper_min** — “Inner layer via hole to copper clearance — 0.2mm”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **pad_hole_to_hole_min** — “Pad Hole-to-Hole Spacing — 0.45mm”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **pad_to_silk_min** — “Pad To Silkscreen — 0.15mm”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **pad_to_track_min** — “Pad to track clearance — 0.1mm — Min. 0.1 mm (stay well above if possible). Min. 0.09 mm locally for BGA pads”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **pth_to_track_min** — “PTH to Track — 0.28mm — 0.35mm is recommended, minimum 0.28mm”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **silk_line_width_min** — “Minimum Line Width — ≥0.15mm — Characters width less than 0.15mm will be unidentifiable.”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **silk_text_height_min** — “Minimum text height — 40 mil (1.0mm) — Characters height less than 40 mil(1.0mm) will be unidentifiable.”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **smd_pad_to_pad_min** — “SMD pad to pad clearance (different nets) — 0.15mm ... Minimum SMD pad: 0.25mm × 0.25mm”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **smt_board_size** — “Economic PCBA 'Single PCB Size: 10x10mm - 470x500mm'; Standard PCBA 'Single PCB Size: 70x70mm - 460x500mm'”  [https://jlcpcb.com/capabilities/pcb-assembly-capabilities retrieved 2026-09-03]
- **smt_layers** — “PCB Layer — 2,4,6-layers / 1 - 32 layers”  [https://jlcpcb.com/capabilities/pcb-assembly-capabilities retrieved 2026-09-03]
- **smt_sides** — “Assembly Types — Single sided placement (SMT/Thru-hole) / Single & double sided placement (SMT/Thru-hole)”  [https://jlcpcb.com/capabilities/pcb-assembly-capabilities retrieved 2026-09-03]
- **track_spacing_min** — “Min. track width and spacing (1 oz) ... Multilayer: 0.09 / 0.09 mm (3.5 / 3.5 mil)”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **track_width_min** — “Min. track width and spacing (1 oz) ... 1- and 2-layer: 0.10 / 0.10 mm (4 / 4 mil) — Multilayer: 0.09 / 0.09 mm (3.5 / 3.5 mil). 3 mil is acceptable in BGA fan-outs.”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **via_annular_ring_min** — “① Via diameter should be 0.1mm(0.15mm preferred) larger than Via hole size.”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **via_diameter_min** — “Multilayer: 0.15 mm hole size / 0.25 mm via diameter. ① Via diameter should be 0.1mm(0.15mm preferred) larger than Via hole size.”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **via_drill_min** — “Min. Via hole size/diameter — 0.15mm / 0.25mm ... Multilayer: 0.15 mm hole size / 0.25 mm via diameter. ② Preferred Min. Via hole size: 0.2mm ③ 0.15mm hole size with any size via diameter, and 0.2mm or 0.25mm hole size with via diameter less than 0.45mm, will cost more.”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **via_hole_to_hole_min** — “Via Hole-to-Hole Spacing — 0.2mm”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]
- **via_to_track_min** — “Via hole to Track — 0.2mm”  [https://jlcpcb.com/capabilities/pcb-capabilities retrieved 2026-09-03]

## Other DRC violations, not governed by an encoded rule

- `track_dangling` x3

## Caveats carried by the rule set

- JLCPCB publishes NO official machine-readable rule file (no .kicad_dru, no JSON). Its own machine check is the hosted JLCDFM tool. This file is ce-fab's transcription of the published HTML tables, and each rule carries the quote it came from so a reader can check the transcription.
- The community rule set Cimos/kicad-druid (capabilities/JLCPCB.toml) has drifted from the current page — it still uses 0.2 mm via drill, 0.6 mm castellated, 0.3 mm edge clearance and 0.2 mm pad-to-trace where the page now says 0.15 / 0.5 / 0.2 / 0.1 mm. Those look like deliberate conservative margins. Where the two disagree, this file follows the JLCPCB page.
- JLCPCB publishes ONE track width/spacing figure covering all copper layers on a multilayer board; there is no separate inner-layer number to encode.
- The page's own FAQ says thicknesses run 0.4-3.2 mm while its table says 0.4-4.5 mm. The table is encoded.

## Sources

- [JLCPCB Rigid PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — retrieved 2026-09-03. Server-rendered; the capability tables are in the raw HTML and were read directly, not through a summarizer. The legacy path /capabilities/Capabilities serves byte-identical text.
- [JLCPCB PCB Assembly Capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) — retrieved 2026-09-03. Source for the Economic vs Standard PCBA split.
- [Multi-Layer PCB Standard Laminated Structures (archived 2024-05-19)](https://web.archive.org/web/20240519231318/https://jlcpcb.com/help/article/364-multi-layer-pcb-standard-laminated-structures) — retrieved 2026-09-03. Live jlcpcb.com/help/article/* pages are client-rendered shells that return no body; this is the archived text. Source for the JLC04161H-7628 stackup naming scheme only.

> A PASS here means MANUFACTURABLE against the transcribed capability lines, not CORRECT. Unrouted copper is reported separately as unconnected_items and does not vote.
