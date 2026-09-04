# halo revision A — stackup and impedance targets

*Lane B1. Generated alongside the Gerbers in this directory. Every number
here is either taken from a named source or computed from one, and the
places where no source could be reached say so.*

---

## 1. The stack

Four copper layers, **0.60 mm total thickness**, FR-4.

| # | layer | copper | function |
|---|---|---|---|
| L1 | `F.Cu` | 1 oz (35 µm) | signals, the 2.4 GHz element, all passives, all test access |
| L2 | `In1.Cu` | 0.5 oz (17.5 µm) | **GND plane** — the return path under every top-side signal |
| L3 | `In2.Cu` | 0.5 oz (17.5 µm) | **VDD plane** — the cell's rail |
| L4 | `B.Cu` | 1 oz (35 µm) | the SoC and every other active, the NFC winding, the battery lands |

**Why 0.60 mm and not 1.6 mm.** SPEC.md §4's stack budget leaves about
1.5 mm above the internal module for everything, and lane M's `design.py`
allocates `T_PCB = 0.600`. KiCad's default is 1.6 mm, and this board carried
that default until ce-fab's DFM report printed the thickness it had measured —
a fab quoting from an uncorrected file would have built a board nearly three
times too thick for its enclosure.

**Why four layers on a Ø26 mm disc**, which is the expensive half of the
decision: there is no room to run a ground trunk around a QFN-48's four sides
and still escape the signals. The plane is what buys the escape. Quoted from
`ce-cad/cecad/data/fab_rules.json`, `stackups["4layer-1.6mm-1oz"]`: *"the
uninterrupted ground plane directly under every signal — which is the return
path, and the return path is the circuit"*.

### Dielectric heights — **NOT CONFIRMED**

| gap | nominal | state |
|---|---|---|
| L1→L2 prepreg | ~0.0685 mm | **CANNOT DETERMINE** |
| L2→L3 core | ~0.36 mm | **CANNOT DETERMINE** |
| L3→L4 prepreg | ~0.0685 mm | **CANNOT DETERMINE** |

JLCPCB publishes its laminated structures per thickness, and the live
`jlcpcb.com/help/article/*` pages are client-rendered shells that return no
body to a fetch (ce-fab records this and reads an archived copy for the
1.6 mm naming scheme only). **No 0.60 mm 4-layer stackup table was
retrieved**, so the three heights above are a plausible set that sums to
0.60 mm with the stated copper weights — they are arithmetic, not a quote.

**This is the number to ask the factory for first**, because §2 depends on it
entirely.

---

## 2. Impedance — the target, and the reason it is not met yet

### The requirement

The 2.4 GHz path from the SoC's `ANT` pin (U1 pad 31) through the matching
network to the antenna feed should be a **50 Ω** controlled line, ±10 %.

### What a microstrip over L2 would need

Standard microstrip, `Z0 ≈ (87/√(εr+1.41)) · ln(5.98h / (0.8w + t))`, with
εr = 4.3, t = 35 µm and h = 0.0685 mm (L1 referenced to the L2 ground plane):

```
50 Ω  →  w = 0.086 mm
```

**0.086 mm is below the 0.127 mm minimum track this board is designed to and
below JLCPCB's own 0.09 mm floor.** A 50 Ω microstrip referenced to L2 is not
manufacturable on a 0.60 mm four-layer stack. That is a property of the stack,
not a mistake in the layout: the thinner the board, the closer the plane, the
narrower a 50 Ω line has to be.

### The two ways out, and which one rev A takes

1. **Reference the RF trace to L3 instead**, by clearing L2's copper beneath
   it. h becomes ≈ 0.486 mm and the same formula gives **w ≈ 0.88 mm**, which
   is comfortably manufacturable. The cost is a slot in the ground plane,
   which has to be managed so it does not become a return-path discontinuity
   for anything else crossing it.
2. **Keep the RF run short enough not to need it.** From U1 pad 31 to the
   antenna feed is about 8 mm, which at 2.44 GHz in this medium is roughly
   0.1 λ. A tenth of a wavelength of uncontrolled line is a small
   perturbation, and it sits inside the pi network (C20/L10/C21) whose whole
   job is to absorb exactly that.

**Revision A takes option 2 and states it, and the board does not yet
implement option 1.** The RF chain is drawn as ordinary tracks. This is an
**OPEN ITEM**, not a solved one: the honest position is that the match will be
set empirically through the pi network against a measured S11, and that a
controlled-impedance build is a revision B question once the fab's real
stackup is known.

**A further complication, recorded because it is easy to miss:** the SoC is on
L4 and the whole matching network is on L1, so the RF signal crosses the board
through a via before it reaches the pi. A via at 2.44 GHz is a discontinuity
with its own inductance, and it needs a ground-via fence beside it. Neither is
modelled in anything run so far.

---

## 3. Materials and finish

| item | value | note |
|---|---|---|
| base | FR-4, TG130 or better | standard |
| εr | 4.3 (assumed) | **generic, not fab-quoted** — the single largest uncertainty in every RF frequency in this pack |
| loss tangent | 0.02 (assumed) | same |
| surface finish | **ENIG** | required: the board carries 0.4 mm pitch QFN lands and 0201 passives, and HASL's coplanarity is not good enough for either |
| solder mask | any colour | the mask is **deliberately merged** between adjacent lands at 0.4 mm pitch — see §4 |
| silkscreen | present, no designators | see §4 |
| copper weight | 1 oz outer / 0.5 oz inner | the inner layers are thinner, so any current calculation done at 35 µm on an inner layer is wrong by about 40 % |

---

## 4. Two deliberate deviations the factory should not "fix"

**Solder mask webs are absent between fine-pitch lands.** The web between two
adjacent lands on a 0.4 mm pitch QFN is about 0.2 mm and on an 0201 about
0.3 mm. KiCad's default asks for a web it cannot have there and reported 23
`solder mask aperture bridges items with different nets`. Those reports are
true and also normal: at 0.4 mm pitch the fab uses mask-defined openings and
does not attempt a web. `solder_mask_min_width` is set to 0 in the project
file to record that the apertures are deliberately merged. **The copper
clearance check is untouched** — that is the one that would catch a real
short.

**There are no reference designators on the silkscreen.** Fifty-one parts do
not fit on a Ø26 mm disc: the DRC found 45 designators over copper and 7
overlapping each other, and every report was true. A designator printed on
another designator identifies nothing. **`F.Fab` and `B.Fab` carry every
reference** for the assembly drawing, and the pick-and-place file is what the
machine uses.

---

## 5. What is not in this document

- **A panel.** `fab panel` has not been run on this outline. The factory lane
  reports a 3×3 panel clearing the minimum size **on the Ø31.87 mm outline**,
  which is the shell's diameter and not this board's — a Ø26.00 mm board
  panelizes more easily, but that has not been measured here and is not
  claimed.
- **Impedance coupons.** None are drawn. They are only meaningful once §1's
  dielectric heights are confirmed and §2 is resolved.
- **A per-layer current and voltage-drop analysis** (SPEC.md E6). Not run.
