# FINDING — the Replica fab board declares 1.6 mm, against 0.30 mm as-drawn

*halo Replica lane L4 (stackup and fabrication), 2026-09-05.
Re-run: `s_stackup_budget.py verify <board.kicad_pcb>` — exit 0/1/2.*

## The measurement

```
$ s_stackup_budget.py verify electronics/halo_replica/fab/out/halo_replica_fab.kicad_pcb
  FAIL   board thickness   declared=1.6   spec=0.3
         declared 1.6mm, as-drawn is 0.3mm — 5.33x.
         1.6 mm is KiCad's DEFAULT: this reads as never set, not as chosen
  PASS   copper layers     declared=4     spec=4
FAIL — a fabricator quotes from the BOARD, not from the document.
```

Read straight out of the file: `(general (thickness 1.6))` at line 6, and four
copper layers `F.Cu / In1.Cu / In2.Cu / B.Cu`.

**The layer count is right.** This is not a board that is simply wrong — it is a
board with one field never set.

## Why 1.6 mm specifically matters

**1.6 mm is KiCad's default for a new board.** It is not a number anybody chose;
it is the number that appears when nobody chooses. That makes it silent — it
survives routing, survives export, and is what a fabricator quotes from.

**This trap has already been sprung once in this project.** Lane B1 on
`halo_rev_a`, in `out/release/board/STACKUP.md` §1:

> *"KiCad's default is 1.6 mm, and this board carried that default until
> ce-fab's DFM report printed the thickness it had measured — a fab quoting
> from an uncorrected file would have built a board nearly three times too
> thick for its enclosure."*

`halo_rev_a` now declares `(thickness 0.6)`. **The Replica board was not
corrected**, and its error is larger: **5.33×**, not 3×.

## Why it matters more here than anywhere else

The Replica exists to be a faithful copy of a **0.30 mm** board. Thickness is
the single most-cited number in this lane — it is the one decision that was
settled before the lane began, and the reason it was settled at 0.30 mm rather
than at whatever a process allows is that **the Replica is the reference the
other five variants are measured against**.

A board file saying 1.6 mm is that reference, as a fabricator would receive it,
diverged by more than five times. And every RF or impedance number computed
from this board's stackup is computed at 1.6 mm.

## What this does NOT say

- **Not that anyone chose wrongly.** A default that was never overridden is a
  different failure from a bad decision, and the fix is different too.
- **Not that the board is otherwise wrong** — the layer count matches the
  COUNTED 4.
- **Not a claim about Apple.** Apple's 0.30 mm is unaffected; this is about
  our file.
- The board may be mid-flight — a route was running on it when this was
  measured. That changes the urgency, not the fact: `1.6` is exactly what
  survives to the fab if nobody looks.

## The check that would have caught it, and now does

`s_stackup_budget.py verify <board>` reads the two declarations a fabricator is
quoted from — board thickness and copper layer count — and compares them to
`stackup.json`'s `replica_as_drawn`. Deliberately regex-based, with no `pcbnew`
import, so it runs under the system python as a cheap gate anywhere.

`selftest` **18/18**.

### The control that was missing, found by firing the break

The first version had two cases: the Replica board *reads* as 1.6 mm, and a
synthetic good board *passes*. I broke `verify` so every comparison matched —
and **all sixteen cases stayed green** while the Replica board reported
`PASS — the board declares the stackup this lane established` at 1.6 mm against
a 0.30 mm spec.

Both existing cases could only fail in one direction. Case 17 adds the other:
**the Replica board must FAIL `verify`**. The same break now goes **1 red**.

**A control that can only fail in one direction is half a control.** Third
sighting today, all three caught only by firing a break on purpose:

| | the control that could not go red |
|---|---|
| `s_stackup_budget` | "the total went up" — copper still grew while the dielectric had stopped |
| `s_layerprobe` | an FFT control that scored blank paper *above* the real land grid |
| `s_fabchain` | an untracked-file case satisfied by a fallback, not by the guard it named |
