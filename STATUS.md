# STATUS

*Updated as lanes land. 2026-09-05.*

## QC close-out, 2026-09-05 (background lane)

Three open defects from the 2026-09-04 factory-pack audit
(changelog `2026-09-04-...-antenna-match-off` and `2026-09-04-...-ten-of-fifteen`),
closed by measurement, not by assertion:

**1. Empty drill files — root cause found, fixed at source, pack regenerated.**
The 2026-09-04 pack was cut at 18:40 from a board that was not routed yet.
Vias do not exist before routing, so KiCad exported PTH/NPTH drill files with
zero holes — correctly. The exporter was never broken (same flags on the
routed board produce all 50 holes, measured). What was broken is the
pipeline: nothing re-cut the pack after routing finished at 22:11, and
nothing gated the pack on its own read-back. `tools/build_fabset.sh` now does
the export and the read-back in one step and refuses to exit 0 unless the
pack provably describes the board. Measured 2026-09-05: `check_fabset`
11 PASS / 0 FAIL — `drill_has_hits` 50 holes, `drill_covers_board` 50 vs the
board's 50 vias + 0 thru-hole pads, `export_is_fresh` export ≥ board,
zip byte-identical to the loose files. Anchor:
`out/release/board/fabset-check.json`.

**2. Antenna MATCH off a run that never resonated — re-solved.** See §The
antenna, measured 2026-09-05 below.

**3. Ten-of-fifteen wrong LCSC codes — the class is closed on the sheet, not
just patched.** The 22:18 fix wrote S1's verified codes into
`spec/bom-resolved.json` but never onto `schematic.py`; the next board
regeneration exported the old wrong codes into the netlist again (regression
measured 2026-09-05 02:05 on the 00:15 netlist: C1546/C1568/C2827888/C1046/
C1523/C25076/C25744/C25765/C1046539/C7498149 all still wrong there). The
corrected codes are now applied to the schematic itself, the board and
netlist were regenerated, and the check is re-runnable against the netlist
(a different artifact from a different tool):
`python3 tools/check_lcsc_netlist.py --json out/verify/lcsc-netlist-check.json`
— **23 of 23 distinct order codes match the catalogue on MPN and package**,
self-test 5/5 (each assertion proved to fire by breaking a fixture on
purpose). BT1 carries no code and says why: the code it had was a battery
holder that must not be fitted. Anchor: `out/verify/lcsc-netlist-check.json`.

**Two more defects found and recorded while re-verifying:**
- ce-fab's `--check-against-kicad` mis-grades bottom-side parts carrying a
  rotation correction: its expectation omits the `180 − rot` flip its own
  writer applies (cefab/jlc.py:214-217 vs :592-594). 9 rows on halo_rev_a,
  all B.Cu. The shipped CPL is correct — re-derived 40/40 from
  `kicad-cli pcb export pos` with the flip included
  (`tools/check_cpl_rotations.py`, negative-tested). Defect recorded for the
  ce-fab lane; not edited from here.
- `check_bom_identity.py` refused a 0 Ω jumper on an inductor ref (L10) —
  a logic fix with the reason in the source: a 0 Ω link is a resistor
  wherever the sheet puts it; crystal package sizes (2016/3215) added to its
  package rules, which took X1/X2 from CANNOT DETERMINE to PASS.

**Pack state** (`out/release/`, regenerated 2026-09-05): INDEX 6 READY ·
5 PARTIAL · 0 NOT STARTED. Artifact 1 (gerbers/drill/netlist) is READY with
the gate; artifact 4 (CPL) READY with rotations verified; artifact 3 (BOM)
still PARTIAL only for sourcing reasons (SoC stock 212 against 1k MOQ; the
NFC re-tune is a board change, not a purchase). The board itself is part-
routed: 50 vias, 9 DRC violations, 80 unconnected — lane B1's list, stated
in `out/release/board/README.md` §5.1. **Do not fabricate until that list
is empty.**

## Interruption and recovery, 2026-09-03 18:47

The machine restarted and killed the orchestrator and twelve agents mid-run.
Nothing was lost: every research dossier had already been committed, and the
tool repositories keep their working trees. All four simulators pass their own
self-checks after the restart — `ce-pcb --doctor`, `ce-spice doctor`,
`ce-rf doctor` and `ce-fwsim doctor` all exit 0 — and KiCad, ngspice, openEMS,
the ARM toolchain and Zephyr's build tool all survived. The eight killed lanes
were relaunched as continuations, told what their predecessors had already
built so none of them starts over.

The project was also renamed in that window. Leif: *"my friend coined the term
halo instead of haytag, because a halo is always visible and you can find it
easily, which is what the project does."* Files under `ce-spice/out`,
`ce-rf/out` and `ce-fwsim/out` deliberately keep their old `haytag-` names:
they are logs of commands that really ran under that name, and rewriting them
would falsify the record. They take the new name when a lane regenerates them.

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
| T1 | KiCad 10 live, ce-pcb end-to-end, freerouting, round 4-layer example | KiCad live and six examples build; **relaunched** to install a JDK (freerouting has never actually run — there is no Java runtime), finish the Ø31.87 mm round board, and add a keep-out primitive |
| T2 | `ce-spice/` — ngspice with verdicts; CR2032, sounder, NFC tank | **done** — four examples, all PASS: coin-cell pulse load, sounder drive, decoupling, NFC tank |
| T3 | `ce-rf/` — openEMS antenna/coil/matching, validated | openEMS built and passing; NFC coil PASSES at 1.33 µH, Q 143. halo-rev-a-2g4 spec hardened 2026-09-04 23:25 (min_cell 0.15 to buy back the Courant timestep; farfield S11 threshold −0.9 dB with its reason in `sim.why`); the board's own re-solve re-run 2026-09-05 — see §QC close-out |
| T4 | `ce-fwsim/` — firmware build, Renode, payload decode | milestone reached (see below). **Relaunched** for the nRF54L port that D12 requires, rolling keys, the Google beacon, and DULT |
| T5 | schematic-from-code → `.kicad_sch` + ERC + design block | `bin/sch` and a `halo_core_sketch` example exist. **Relaunched** to finish ERC, the PDF export, and the KiCad 10 design block that carries layout as well as schematic |
| T6 | `ce-fab/` — LCSC parts DB, BOM cost, JLC export, panel, DFM, quote | least advanced: a 391 MB parts cache and a fetch script. **Relaunched** — this is the lane the factory pack depends on. 2026-09-05: its CPL cross-check's bottom-flip gap recorded as a defect (see changelog); halo now verifies CPL independently |

## Milestone: the firmware advertises correctly, in emulation, with no hardware

`ce-fwsim` built a halo firmware, injected a rolling key, and ran it on an
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
D6 halo competes on openness, not on unit price · D7 dual network from
revision A · D8 DULT is in the BOM · D9 redraw the copper, never copy it ·
D10 parity target is AirTag 2 · D11a a bare piezo bender bonded to the shell ·
D12 nRF54L Channel Sounding instead of UWB, superseding D10 · D13 bayonet door
and single-shot tooling. See DECISIONS.md.

## Design lanes

| lane | deliverable | state |
|---|---|---|
| M | the puck enclosure in ce-cad: shell, carrier, bayonet door, sprung contacts, printed variant | running |
| E2 | re-cost the whole BOM on nRF54L, and settle whether a pre-certified nRF54L module exists | running |

## Next after these

SPEC.md → schematic → simulate → layout → verify → factory release pack
(MISSION.md lists the eleven artifacts that define done).
