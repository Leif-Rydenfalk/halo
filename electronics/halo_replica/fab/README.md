# halo Replica — FAB VARIANT. The branch you can order.

## NOBODY HAS BUILT ONE.

This board has never been fabricated, never been populated, and never been powered on. Everything
below is a paper claim until one exists. Read that line before any other.

---

## What to upload

```
fab/out/halo_replica_jlc_0.4mm.zip     # closest to Apple's 0.30 mm
fab/out/halo_replica_jlc_0.8mm.zip     # the thickness JLC's 4-layer list unambiguously contains
```

Each zip contains the gerbers, the Excellon drill, and an `ORDER-SETTINGS.txt` naming the settings
to choose. Upload **one** of them — they differ only in the thickness you should select at order
time; the copper is identical.

**Which one: use the 0.8 mm zip at JLCPCB.** This was an open question in an earlier revision of
this file, which told you to *"try 0.4 first"*. **That advice was wrong and is withdrawn.**

**MEASURED 2026-09-05, in JLCPCB's live quote configurator**, not read off a capability page:

| layers selected | PCB Thickness offered |
|---|---|
| **4** | 0.8 · 1.0 · 1.2 · 1.6 · 2.0 — **0.4 and 0.6 are greyed out** |
| **2** | **0.4** · 0.8 · 1.0 · 1.2 · 1.6 · 2.0 — 0.6 greyed |

Both controls were run, because a greyed button and an unselected button look similar:

- **Negative control** — clicking `0.4mm` while 4 layers is selected changes nothing; the
  selection stays on 1.6 mm. It is genuinely disabled, not merely unstyled.
- **Positive control** — switching 4 → 2 layers **re-enables** `0.4mm` in the same page without a
  reload. The disable tracks the layer count, so it is a real constraint and not static styling.

**This board is 4 layers, so 0.4 mm is not orderable at JLCPCB. Order the 0.8 mm zip.**

Two further things the configurator did that a capability table does not tell you. Selecting
0.4 mm (at 2 layers) **forces the rest of the order**: `Surface Finish` jumps to **ENIG** with
**HASL greyed out** — you cannot hot-air-level a board that thin — `Material Type` collapses to
**FR4 TG135 alone**, and `Panel by JLCPCB` is refused. And it is not a small surcharge: the same
5-off order went from **$4.10 at 1.6 mm to ~$66** at 0.4 mm, the jump being an **engineering fee
$33 + via covering $16 + surface finish $16**. Thin is a different product, not a checkbox.

**If 0.4 mm matters more than the vendor does, PCBWay documents 0.40 mm at four layers**
("medium difficulty"). **That is a documentation claim only — it has NOT been put through
PCBWay's order form, so it is not the same grade of evidence as the table above.**

Settings: **4 layers · ENIG preferred · min trace/space 0.09 mm · min via 0.25 mm pad / 0.15 mm
drill** — all inside JLC's published four-layer capability.

---

## THIS IS NOT A 1:1 REPLICA, AND THE REASON IS A FORK RATHER THAN A COMPROMISE

> Apple's **WLCSP-50 fits** the ~6 mm annular ring and **cannot be landed**, because no complete
> ball map for it has ever been published. The **QFN-48 is the same die**, **can be landed**, and
> is **6 × 6 mm** — which does not fit that ring. **There is no arrangement that is both.**

This is the **buildable branch**. The **dimensional branch is `pcb/`**, which holds Apple's 25 mm
annulus at 0.30 mm with wafer-scale packages at measured positions — and **0 nets, 0 tracks, 0
vias**, because it is a transcription of photographs and not a circuit. Ordering *that* would give
you disconnected copper.

**A person holding a board that works but is the wrong shape should not have to work out why.**

### Every departure, with its reason

| | Apple | here | why |
|---|---|---|---|
| outline | Ø~25 mm **annulus** | **Ø30 mm disc** | a 6 mm QFN and a coin-cell holder need the area; still inside the AirTag's Ø31.9 mm shell |
| thickness | **0.30 mm** | 0.4 or 0.8 mm | below every fab floor we could find published |
| SoC package | nRF52832 **WLCSP-50** | same die, **QFN-48** | no published ball map — 56 grid positions for 50 balls and **which six are depopulated is CANNOT DETERMINE** |
| 1.8 V rail | buck + load switch | **deleted; runs from the cell** | the nRF52832 spans 1.7–3.6 V across the whole CR2032 curve. It was also the highest-risk block on a board built to answer "does it work" |
| flash | GD25LQ32C | **MX25R3235F** | Apple's part is 1.65–2.0 V and **cannot run at 3 V**. This follows necessarily from the line above |
| load switch | FPF2487 | **MIC94090**, 0.5 µA | kept, because O'Flynn *measured* that the nRF controls flash power and the flash is off most of the time |
| UWB (U1/U2) | Apple U1 | **absent entirely** | never sold to anyone, at any price. A DNP part with a land pattern invites someone to try to buy one |
| antennas | 3, laser-structured on a moulded carrier | not reproduced | measured: they are **not on Apple's board** |
| passive values | unknown | **all CHOSEN from function** | a 100 nF and a 1 µF 0402 are visually identical — **no photograph can give a value** |
| five-removals reset | 3 sprung contacts, both positives sensed | **not reproduced** | a catalogue CR2032 holder has two terminals. A real loss of function, not a simplification |
| op-amp U7, regulator U9 | present | absent | U7's role is this project's *reconstruction*, not an observation; U9 is CANNOT DETERMINE down to its function |

---

## What a working board would and would not prove

**Would:** that the reconstruction of Apple's circuit is sound — that this arrangement of SoC,
flash, load switch, crystals and power path boots, advertises and runs from a coin cell.

**Would not:** that any value matches Apple's, that the RF match is right, or that an AirTag works
this way. Those are separate claims and none of them is tested by this board.

## Not verified

- **Nobody has built one.**
- **No LCSC part codes.** Every line carries a real manufacturer part number; a code with no pull
  date is a rumour. **JLC's own BOM tool will check stock in one click when you upload** — that
  question could not be answered from here without an account.
- The 2.4 GHz match **has never seen a VNA**. Fit `L1 = 0R` and leave the shunts off for a first
  article.
- The NFC capacitors assume a coil nobody has wound.
- The crystal load capacitors assume ~4 pF of stray on a board nobody has laid out.

## A designator warning

**`J1` and `U2` mean different parts on the two sheets.** On the **fab** sheet J1 is the sounder-coil
header and U2 is the load switch. On the **fidelity** sheet J1 is the coax receptacle and U2 is
Apple's UWB module. **Nobody may carry a designator between them.**

## Rebuild it yourself

```bash
ce-pcb/bin/sch  all .../schematic/schematic_fab.py -o .../out/schematic-fab
ce-pcb/bin/pcb  .../fab/board_fab.py
ce-pcb/bin/route .../fab/out/halo_replica_fab.kicad_pcb
python3 tools/g_package.py .../fab/out/halo_replica_fab-routed.kicad_pcb fab/out
python3 tools/z_fabcheck.py fab/out/halo_replica_jlc_0.4mm.zip
```

`z_fabcheck` refuses a package whose copper layers exist and contain **nothing** — a valid gerber
header with no apertures opens fine, passes every existence test, and would waste the order.
