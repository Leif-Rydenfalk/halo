# halo — an open-source, cheaper AirTag-compatible tracker PCB

*A ce-designs project (`design:halo`) and a triad root. Started 2026-09-03.*

Leif, 2026-09-03, verbatim: *"its a clone of the apple airtag pcb but so we can
open source it and manufacture it for cheaper. do a whole lot of research and
find out a lot of open source projehcts which already tries to do this and
potential pcb designs and all available documentation and research out there
for this and place it all in this repo"*

Apple sells the AirTag for $29 with the hardware closed and the Find My network
gated behind an accessory program. This repo collects **everything public** about
the AirTag hardware, the Find My protocol, the open-source firmware that already
lets non-Apple boards ride the network (OpenHaystack and its successors), every
open coin-cell tracker PCB that could be a starting point, the chips that can
reproduce each function and what they cost, and the legal / certification /
child-safety / anti-stalking constraints — then designs an open board from it.

**Name.** "AirTag" and "Find My" are Apple trademarks, so the project is not
called that. *halo*: a tag for the haystack (the Find My network is the
haystack; OpenHaystack is the needle-finder). Rename is one `gh repo rename`.

## What is where

```
README.md            this page
DECISIONS.md         every design question resolved by evidence, and what each option beat
MISSION.md           the definition of done: the eleven-artifact factory release pack
TOOLCHAIN.md         the tools we have, the open-source sim stack, the lanes building it
GOAL.md              what it is for — puck, embeddable block, local relative positioning (Leif's words)
research/            the dossiers — one per lane, every claim sourced with URL + date
  08-local-positioning-uwb-ble.md        peer-to-peer ranging: UWB TWR, BLE RSSI/AoA, open RTLS projects
  09-embeddable-block-and-modules.md     how to ship it as a KiCad sheet + castellated module
  01-airtag-hardware.md                  teardowns, chips, PCB, firmware, debug ports
  02-findmy-protocol-and-openhaystack.md the BLE payload, key rotation, every OSS project
  03-open-hardware-tag-designs.md        existing open PCBs (KiCad/Eagle/EasyEDA) ranked
  04-commercial-tags-and-clones.md       certified tags + AliExpress clones, what's inside
  05-components-and-cost-model.md        part candidates, BOM roll-up at 10/100/1k/10k
  06-legal-ip-certification-safety.md    trademark, patents, Find My program, DULT, FCC/CE, Reese's Law
  07-mechanical-enclosure-and-3d-models.md dimensions, speaker, battery door, open 3D models
  fetched/           raw text of the key pages, so the record survives link rot
  sources.tsv        every source any lane used: lane, url, title, date, note
reference/           vendored snapshots of the open-source repos (CLONE-LIST.tsv → MANIFEST.md)
  models/            freely-licensed 3D models and drawings
images/              teardown / FCC / design photos with CATALOG.md per folder (source + license)
spec/                machine-readable: bom-candidates.json, later specs.json
docs/                ANTI-STALKING.md and the design documents that follow
electronics/         schematic + netlist (ce-pcb) — next phase
hardware/            KiCad project — next phase
firmware/            pointers to upstream + our port — next phase
ce-parts/ ce-connections/ ce-assemblies/   the triad shelf for this design — next phase
evidence/            ledger.jsonl, append-only
out/                 renders, gerbers, reports — COMMITTED, they are data
```

## Method

1. **Research** (this commit) — collect every public fact with its source.
2. **Specify** — SPEC.md: what the clone must do (Find My via OpenHaystack keys
   first, official program path documented), the DULT anti-stalking minimum,
   target cost, target envelope (Ø ≈ 32 mm, 8 mm).
3. **Design** — ce-pcb board.py → KiCad → JLCPCB assembly; enclosure in ce-cad.
4. **Evidence** — every check lands in the ledger; the design is born T0.

## Status

Research lanes A–G running 2026-09-03. See research/ as they land.
