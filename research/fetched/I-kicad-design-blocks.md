# KiCad design blocks — the reuse mechanism, KiCad 9 vs KiCad 10
Lane I. Fetched 2026-09-03 (HTML pulled with curl, tags stripped locally).

Sources:
- KiCad 9.0 Schematic Editor manual, <https://docs.kicad.org/9.0/en/eeschema/eeschema.html> (853 KB HTML)
- KiCad 10.0 Schematic Editor manual, <https://docs.kicad.org/10.0/en/eeschema/eeschema.html> (1.05 MB HTML)

## KiCad 9.0 — schematic only

> **Schematic design blocks** allow you to save a portion of a schematic and reuse it later. You can
> reuse design blocks within the same schematic or in different schematics. Design blocks are saved and
> organized in design block libraries, much like symbols and footprints. When you use a design block,
> the saved schematic fragment is inserted into the current schematic, either in the current sheet or in
> a new subsheet.

Placement options in KiCad 9: `Place as sheet` (two clicks, contents go into a new hierarchical sheet),
`Place repeated copies`, `Keep annotations`.

> If the **Keep annotations** checkbox is enabled, KiCad will insert the design block without changing
> the symbol annotations as defined in the saved design block. If it is not enabled, KiCad will reset the
> symbol annotations while inserting the design block and reannotate all of the symbols in the block
> according to the current annotation settings.

Saving: `Save Current Sheet as Design Block…` or `Save Selection as Design Block`; libraries are
registered in a **global** or **project** design block library table, exactly like symbol libraries.
Properties carried: Name, Keywords, Description, **Default Fields** (key/value pairs applied as
hierarchical sheet fields when placed as a sheet).

**KiCad 9 limitation that decides haytag's architecture: no copper.** The 9.0 manual describes only
schematic fragments. The layout half has to be redone by hand in every host board.

## KiCad 10.0 — schematic **and** a PCB layout fragment

> Design blocks are a design-reuse feature that lets you save a portion of a schematic (**and optionally
> a corresponding PCB layout**) as a named, reusable fragment stored in a design block library. You can
> instantiate a design block any number of times within the same project or across different projects.
>
> **A single design block can contain a schematic fragment, a PCB layout fragment, or both.** When you
> place a schematic design block, the saved schematic fragment is inserted into the current schematic
> sheet or into a new hierarchical subsheet. **If the design block also contains a layout fragment, you
> can later apply that layout to the footprints that were placed as a result of the schematic fragment.**
> This makes design blocks well suited for circuits that appear repeatedly across projects, such as power
> supply subcircuits, filter networks, protection circuits, and interface conditioning stages.
>
> Typically, design blocks are created first as a schematic fragment, with the layout added later once
> the circuit has been placed and routed on a board.

Placement modes (KiCad 10): **Place inline (no sheet)** or **Place as sheet**, each optionally with
`Place as group`.

> In either mode, also enable the **Place as group** option to wrap the placed content in a group with a
> library link. Without a group, features including saving changes back to the library, placing additional
> linked instances, and **applying the stored layout to the corresponding footprints in the PCB editor**
> are not available.

Group actions once linked: `Save to Linked Design Block`, `Place Linked Design Block`,
**`Apply Design Block Layout` — "in the PCB editor, apply the layout stored in the linked design block
to the group of footprints corresponding to this design block instance."**

The library link is a group field: `<library>:<block>`, e.g. `analog_filters:sallen_key_lowpass`.

### Hard limitation
> **Design blocks do not support nested hierarchical sheets.** If the sheet you are saving as a design
> block contains hierarchical sheet symbols (subsheets), the save operation will be rejected.

### Library structure — verbatim
> Design block libraries are stored as directories on the filesystem. The directory structure has two
> levels of nesting:
> - The library itself is a directory whose name ends with **`.kicad_blocks`** (for example,
>   `my_power_circuits.kicad_blocks`).
> - Each design block within the library is a subdirectory inside the library directory, with the suffix
>   **`.kicad_block`** (for example, `ldo_3v3.kicad_block`).
>
> Inside each design block directory, KiCad stores:
> - A schematic file (`<block_name>.kicad_sch`) — present if the design block contains a schematic fragment.
> - A board file (`<block_name>.kicad_pcb`) — present if the design block contains a layout fragment.
> - A metadata file (`<block_name>.json`) — always present; stores the design block's description,
>   keywords, and default fields.
>
> **Because libraries and design blocks are plain filesystem directories, they can be managed with
> ordinary file manager tools, version control systems, or shared over a network filesystem.**

## Consequence for haytag
A `haytag.kicad_blocks/haytag-core.kicad_block/` directory containing `haytag-core.kicad_sch` +
`haytag-core.kicad_pcb` + `haytag-core.json` is a **git-versionable, cross-project, schematic+copper**
artefact — the exact "drop the RF section into your own board in any outline" object GOAL.md asks for,
using nothing but stock KiCad 10. It is the only mechanism found in this lane that carries the routed
antenna and matching network, not just the netlist.

Constraint to design around: the block must be **flat** (no nested subsheets) to be savable.
