# STATUS

*Updated automatically as lanes land. 2026-09-03.*

## Research lanes (dossiers into research/)

| lane | topic | state |
|---|---|---|
| A | AirTag hardware teardown, chips, PCB, function map | running |
| B | Find My protocol + OpenHaystack ecosystem | running |
| C | open-source tag/beacon PCB designs, ranked | running |
| D | commercial Find My tags and clones, what is inside | running |
| E | components and cost model, 1:1 substitution map | running |
| F | legal, IP, Find My program, DULT, FCC/CE, Reese's Law | **done** — 867-line dossier, 30-item constraint checklist, ANTI-STALKING.md |
| G | mechanical, enclosure, speaker, open 3D models | running |
| H | local positioning: UWB ranging, BLE channel sounding | running |
| I | embeddable block, castellated module, antenna rules | running |

## Toolchain lanes (into ce-workshop siblings)

| lane | deliverable | state |
|---|---|---|
| T1 | KiCad 10 live, ce-pcb end-to-end, freerouting, round 4-layer example | running |
| T2 | `ce-spice/` — ngspice with verdicts; CR2032, sounder, NFC tank | running |
| T3 | `ce-rf/` — openEMS antenna/coil/matching, validated | running |
| T4 | `ce-fwsim/` — ARM+Zephyr, OpenHaystack build, Renode, payload decode | running |
| T5 | schematic-from-code → `.kicad_sch` + ERC + design block | running |
| T6 | `ce-fab/` — LCSC parts DB, BOM cost, JLC export, panel, DFM, quote | running |

## Decisions taken

D1 two variants (haytag-core BLE-only, haytag-uwb for peer ranging) · D2 no
Bluetooth word mark · D3 press-and-twist battery door (Reese's Law) · D4 licence
split CERN-OHL-S / AGPL / Apache / CC-BY-SA · D5 clean-room, no MFi enrolment.
See DECISIONS.md.

## Next after these

SPEC.md → schematic → simulate → layout → verify → factory release pack
(MISSION.md lists the eleven artifacts that define done).
