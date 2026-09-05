# halo Replica — the PCB

**A KiCad user can open this.** That was the gap: 130 measurement JSONs, 40
measuring tools, a JSON outline and a PNG. No footprints, no `.kicad_pcb`, no
gerbers, no drill file.

```bash
ce-pcb/bin/pcb ce-designs/halo/electronics/halo_replica/pcb/board.py   # build
ce-pcb/bin/pcb --open .../pcb/out/halo_replica.kicad_pcb               # look
python3 tools/f_placement_check.py   # positions + angles, read back off the board
python3 tools/f_backface_handedness.py   # is the back mirrored or rotated?
python3 tools/f_render.py            # renders BOTH faces and measures the picture
python3 tools/f_drc_classify.py      # whose unmanufacturability is each error?
python3 tools/f_fab.py               # the fab set, stamped NOT FOR FABRICATION
```

## What is on it

| | |
|---|---|
| outline | 3 true arcs + 4 straight chords. Endpoints solved exactly. |
| pocket | superellipse n=2.4491 + 7 measured facets + 14 radial step walls |
| OD | **a BOUND, 24.95–26.34 mm.** A parameter from `board.json`, never a literal. If it moves it moves DOWN. |
| stack | 4 layers COUNTED, **0.30 mm as-drawn**, ENIG, black mask |
| front | 31 measured metal lands at measured angles, 69 refusals-with-a-position |
| back | 41 measured gold pads (median Ø 0.5985 mm) + 3 contact positions |
| nets | 65 READ from L11's schematic. **0 pads bound.** |
| DRC | 33 errors, **classified not cleared**: 14 measurement-limited, 19 bound-limited, 0 genuinely-touching, 0 our-error |
| fab | 29 files, freshness-checked, **NOT FOR FABRICATION in every file** |

## The three evidence classes, and why a pad carries one

**CLASS A** package geometry — a fact about the PART (EIA case sizes, a
datasheet pitch), not a measurement of Apple's board.
**CLASS B** measured metal — a real land at the measured extent. The
producing lane's words: the handoff is *"A LIST OF METAL AND BLUE. It is NOT
a list of components."*
**CLASS C** a refusal with a position — **no pad, no mask, no paste.** It
cannot become copper by accident. That is a guarantee, not a convention.

## REFUSALS — what is deliberately not here

- **U1, the nRF52832 WLCSP-50, has no land pattern.** A 0.40 mm grid in the
  measured body is 56 positions for 50 balls and no ball map exists here or
  in KiCad's 179 `Package_CSP` footprints. Six lands that do not exist on the
  part are six lands a fab would make. Body + grid are on `F.Fab` only.
  **10 of 50 ball designators ARE sourced** (O'Flynn's test-point table) and
  are ringed and labelled there; the other 46 carry no designator, so the gap
  is visible on the drawing. Ten of fifty is not a ball map.
- **U2, the Apple U1 UWB module** — never sold, **UNPOPULATED, and the board
  says so in silkscreen.** No land pattern and no keep-out: no handoff gives
  the can a measured centre and its own remeasure swings 6.735 → 7.891 mm on
  the operator's padding alone.
- **5 dark bodies**, including the largest package on the board — CANNOT
  DETERMINE at a measured contrast limit. Named on the board, drawn nowhere.
  **The dark areas SHOULD look sparse.**
- **Rim pads** (count CANNOT DETERMINE and CLOSED), **antennas** (on a
  moulded carrier, not this PCB), **the coil** (wound wire, not a trace),
  **the 5 bulk capacitors** (size is a function of the operator's window),
  **U3/X1/X2** (package NOT YET MEASURED).

## Three things that were verified against the picture, not the file

1. **A square board.** Zero-length outline segments made KiCad report 46
   `invalid_outline` and then **silently fall back to the bounding box.** A
   malformed annulus and a rectangle are the same picture until you look.
2. **A green board.** `(color "black")` was written into the stackup and read
   back from the file — and the render was still green, because `kicad-cli`
   ignores the stackup without `--use-board-stackup-colors`. The check moved
   to the PNG.
3. **A control that agreed with itself.** The first back-face handedness test
   swapped the two frames — but a reflection is its own inverse, so it
   returned MIRROR both ways. Replaced by one that synthesises a *rotated*
   back face; MIRROR is refused at 12°, 40° and 90°.

## The rule the DRC classification exists to protect

**DO NOT MOVE A MEASURED POSITION TO SATISFY A DESIGN RULE.** Every land here
is a metrology row. Nudging one to clear a rule falsifies a measurement to
satisfy a manufacturing constraint, and it is invisible in every render
afterwards. So: classified, not cleared. `BOUND-LIMITED` is **not** "will
resolve when the bound resolves" — the OD is expected to move DOWN, so those
19 get **worse**.
