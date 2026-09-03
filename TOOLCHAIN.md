# TOOLCHAIN — what we have, what we are building, how the board gets made

*Written 2026-09-03, answering Leif: "what tools do we currently have for pcb
generation by ai agents? what open source simulation software is available for
this and what is your plan to do this properly? … what tools do you want to
have available? put agents on making those tools"*

Everything here is **measured on this Mac on 2026-09-03**, not assumed.

## What already existed (measured)

| repo | what it does for a board | state today |
|---|---|---|
| `ce-pcb/` | `cepcb.Board` drives **KiCad's own kernel** (`pcbnew`) from Python: place footprints, bind a netlist, nets, multilayer stackup, then `kicad-cli` for DRC / render / gerbers / drill / pos. Plus a triad layer (`bin/board`) that writes a board back as one assembly + one generated part. | code present; **KiCad was not installed** — `import pcbnew` failed, `kicad-cli` absent, so every kernel verb was dead. Lane T1 is fixing that. |
| `ce-elec/` | the electrical layer above boards: GPIO/port assignment, netlist emission, system → PCB → chip decision order | live, stdlib |
| `ce-wire/` | what is connected to what, as folders an AI can open | live |
| `ce-elec-sim/` | rail budgets, pin-map reconciliation, unify graph | live |
| `ce-board-sim/` | per-layer IPC-2221B current / resistance / voltage drop on a real multilayer board | live — this is the model every new sim app copies |
| `ce-cad/` | the mechanical kernel (OpenCascade), FEA, drawings, BOMs, release packs | live |
| `ce-fluid/`, `ce-struct/` | CFD and structural studies | live |

So: **a board *generator* existed, no board *simulator* stack existed, and the
generator's kernel was not installed.** No SPICE, no EM/antenna solver, no
firmware emulation, no factory-facing parts/DFM tooling. Nothing on this
machine could answer "will this antenna resonate at 2.44 GHz", "will a CR2032
survive the TX pulse at end of life", or "what does JLCPCB charge for this".

Installed radio/EDA software found on 2026-09-03: **none** — no kicad-cli, no
ngspice, no openEMS, no gmsh/Elmer/CalculiX, no `pcbnew` module, no `skidl`,
no Java. FreeCAD and Docker 29 were present.

## The open-source simulation stack we are standing up

| need | tool | licence | why this one |
|---|---|---|---|
| PCB CAD kernel, DRC, gerbers, 3D render | **KiCad 10** (`pcbnew` + `kicad-cli`) | GPL | already the kernel `ce-pcb` drives; scriptable and headless |
| autorouting | **freerouting** (Java, headless DSN→SES) | GPL | the only maintained open router that takes Specctra out of KiCad |
| circuit / power simulation | **ngspice** | BSD | the reference open SPICE; batch mode gives an agent numbers, not a GUI |
| RF, antennas, NFC coil | **openEMS** (FDTD) + **scikit-rf** | GPL / BSD | the only credible open 3-D EM solver with Python bindings; scikit-rf does S-parameters and matching |
| firmware build + emulation | **Zephyr / nRF Connect SDK**, arm-none-eabi-gcc, **Renode** | Apache / GPL / MIT | Renode runs an nRF52 image headless so the Find My advertisement can be decoded before a board exists |
| factory data | **jlcparts** catalogue, **KiKit** (panelization), JLCPCB rule sets | MIT / MIT | turns a board into a quote, a BOM, a CPL and a panel without a human clicking a website |
| thermal / structural of the board | `ce-board-sim` + `ce-struct` (existing) | — | already ours |

## The six agent lanes building it (launched 2026-09-03)

| lane | deliverable |
|---|---|
| **T1** | KiCad 10 installed; `ce-pcb/bin/pcb --doctor` PASS; every example builds → DRC → render → gerbers; freerouting wired in as `bin/route`; a Ø 32 mm 4-layer round-board example; `ce-pcb/docs/agent-workflow.md` |
| **T2** | new app **`ce-spice/`** — `bin/spice run` over ngspice with asserts and PASS/FAIL verdicts; CR2032 pulse-load + battery-life model, speaker H-bridge, decoupling, NFC tank |
| **T3** | new app **`ce-rf/`** — `bin/rf antenna` / `nfc-coil` / `match` over openEMS + scikit-rf; validated against a published TI/Nordic reference antenna; the round-puck antenna case |
| **T4** | new app **`ce-fwsim/`** — ARM toolchain + Zephyr, builds the OpenHaystack nRF52 firmware, runs it in Renode, decodes the Find My advertisement bytes, and a `bleak` scanner to verify a real board |
| **T5** | **schematics from code** — evaluate SKiDL / atopile / kicad-sch writers, implement `bin/sch` producing a real `.kicad_sch` with ERC, PDF, and a hierarchical **design block** other projects can drop in |
| **T6** | new app **`ce-fab/`** — LCSC/JLC parts database offline, BOM costing at 10/100/1k/10k, JLC BOM+CPL+gerber export, KiKit panelization, DFM rule checks, quote estimator |

Every one is a self-declared app (`ceapp.toml`) under house rule 6: adding it
diffs no shared file.

## The plan for the product

1. **Research** (lanes A–I, running) — the AirTag internals function by function,
   the Find My protocol, existing open designs, commercial clones, components
   and cost, legal/DULT/certification, mechanics, local positioning, embedding.
2. **Specify** — `SPEC.md`: every function of the real AirTag with the part that
   reproduces it, sourced; the envelope; the cost target; the anti-stalking
   minimum; the block interface.
3. **Schematic** — `bin/sch` emits `.kicad_sch`, ERC clean, PDF for the factory.
4. **Simulate before layout** — `ce-spice` proves the power path on a CR2032 at
   end of life and the sounder drive; `ce-rf` sizes the 2.4 GHz antenna, the NFC
   coil and the UWB feed on the real outline.
5. **Lay out** — `ce-pcb` places and routes the Ø 32 mm 4-layer board; freerouting
   finishes; DRC and `ce-board-sim` per-layer current checks must pass.
6. **Verify** — `ce-fwsim` runs the firmware in Renode and decodes the Find My
   payload; `ce-fab dfm` grades the board against JLCPCB's real capabilities.
7. **Release to the factory** — gerbers, drill, BOM with LCSC ids and prices,
   CPL, panel, stackup, assembly drawing, test plan, enclosure files, and the
   quote at 10 / 100 / 1 000 / 10 000.

Nothing in that chain is a claim: each step ends in a `verdict.json` of
PASS / FAIL / CANNOT DETERMINE, and a CANNOT DETERMINE is a work item, never a
question for Leif.
