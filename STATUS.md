# STATUS

*Updated automatically as lanes land. 2026-09-03.*

## Research lanes (dossiers into research/)

| lane | topic | state |
|---|---|---|
| A | AirTag hardware teardown, chips, PCB, function map | **done** — 416-line dossier, exhaustive BOM read off the board, function map |
| B | Find My protocol + OpenHaystack ecosystem | **done** — 927 lines, exact advertisement layout, 23-project table |
| C | open-source tag/beacon PCB designs, ranked | **done** — 21 designs; no open-source AirTag exists |
| D | commercial Find My tags and clones, what is inside | **done** — 26-row table, five FCC exhibits read, price floor |
| E | components and cost model, 1:1 substitution map | **done** — live LCSC/JLC pricing; re-costing on nRF54L per D12 |
| F | legal, IP, Find My program, DULT, FCC/CE, Reese's Law | **done** — 867-line dossier, 30-item constraint checklist, ANTI-STALKING.md |
| G | mechanical, enclosure, speaker, open 3D models | **done** — Apple's own dimensioned drawing, stack budget closes at 81% |
| H | local positioning: UWB ranging, BLE channel sounding | **done** — Channel Sounding wins on accuracy, price and stock (D12) |
| J | Find My viability in 2026, measured | **done** — PASS with conditions; live scan decoded 471 advertisements |
| I | embeddable block, castellated module, antenna rules | **done** — KiCad 10 design blocks carry layout; 24-pad pinout proposed |

## Toolchain lanes (into ce-workshop siblings)

| lane | deliverable | state |
|---|---|---|
| T1 | KiCad 10 live, ce-pcb end-to-end, freerouting, round 4-layer example | running |
| T2 | `ce-spice/` — ngspice with verdicts; CR2032, sounder, NFC tank | running |
| T3 | `ce-rf/` — openEMS antenna/coil/matching, validated | running |
| T4 | `ce-fwsim/` — ARM+Zephyr, OpenHaystack build, Renode, payload decode | running |
| T5 | schematic-from-code → `.kicad_sch` + ERC + design block | running |
| T6 | `ce-fab/` — LCSC parts DB, BOM cost, JLC export, panel, DFM, quote | running |

## Milestone: the firmware advertises correctly, in emulation, with no hardware

`ce-fwsim` built a haytag firmware, injected a rolling key, and ran it on an
emulated nRF52840 in Renode. It configured the radio and transmitted on all
three advertising channels. The advertisement was then verified field by field
against SPEC F1 and every field matches: the 28-byte key, the air address
derived as `p[0]|0xC0` followed by `p[1..5]` little-endian, the
`1E FF 4C 00 12 19` header, the 22 payload key bytes, and `p[0] >> 6` in the
penultimate position. Ledger row written in `evidence/ledger.jsonl`.

## Decisions taken

D1 two variants · D2 no
Bluetooth word mark · D3 press-and-twist battery door (Reese's Law) · D4 licence
split CERN-OHL-S / AGPL / Apache / CC-BY-SA · D5 clean-room, no MFi enrolment ·
D6 haytag competes on openness, not on unit price · D7 dual network from
revision A · D8 DULT is in the BOM · D9 redraw the copper, never copy it ·
D10 parity target is AirTag 2 · D11a a bare piezo bender bonded to the shell ·
D12 nRF54L Channel Sounding instead of UWB, superseding D10 · D13 bayonet door
and single-shot tooling. See DECISIONS.md.

## Next after these

SPEC.md → schematic → simulate → layout → verify → factory release pack
(MISSION.md lists the eleven artifacts that define done).
