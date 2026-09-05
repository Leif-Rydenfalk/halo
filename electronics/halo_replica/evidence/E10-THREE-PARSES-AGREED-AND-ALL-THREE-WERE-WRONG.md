# E10 — Three parses agreed to 0.01 mm, and all three were wrong

**Date:** 2026-09-05 · **Lane:** fab · **Verdict:** a measurement retracted,
the correct value proved analytically, the method rule changed.

## The claim I made, and acted on

I surveyed every CR2032 holder in KiCad's `Battery.pretty` and told L11 that
`BatteryHolder_MYOUNG_BS-07-A1BJ001_CR2032` was **27.41 × 6.30 mm, diagonal
28.13** — the one real holder that fits a Ø30 mm board. **L11 changed the
schematic on that number.**

It is **27.50 × 24.42 mm, diagonal 36.78.** It does not fit. The height was
wrong by **3.9×**.

## Why the confirmation was worthless

L11 did not take my word for it. They re-measured all ten holders out of the
footprint files themselves and **reproduced my numbers to 0.01 mm on every
row.** That is as strong as agreement gets, and it established nothing:

> **We did not take two measurements. We took the same measurement twice.**

Both of us parsed coordinates out of the `.kicad_mod`. Both of us were blind in
exactly the same place.

I then ran a **third** parse — properly paren-balanced, fixing a real regex bug
I had already found in the first — and **it also returned 6.30.** Three
agreeing text parses. One geometry engine disagreeing. The geometry engine was
right.

## The blind spot, and the arithmetic that settles it

MYOUNG's courtyard is three `fp_line`s and one `fp_arc`:

```
(fp_arc (start 0.65 -3.15) (mid 24.564907 0) (end 0.65 3.15) (layer "F.CrtYd"))
```

Any parser reading coordinates sees `y ∈ [-3.15, 3.15]` and reports height
6.30. **The arc's three control points are not its extent.**

Circle through those points: centre **(12.4000, 0)**, radius **12.1649**. The
endpoints sit at **−164.99°** and **+164.99°**, and the sweep goes the *long*
way through 0°, so it crosses **both −90° and +90°** — where `y = 0 ± r`.

| | height |
|---|---|
| control points only (all three of my parses, and L11's) | 6.30 mm |
| `2r` + 0.05 stroke each side, computed analytically | **24.4298 mm** |
| `pcbnew` `GetCourtyard().BBox()` | **24.42 mm** |

The analytic value and KiCad's agree to 0.01 mm. The 6.30 is the arc's
**chord**.

## The part I have no excuse for

**I had fixed this exact defect four hours earlier**, in `z_fabcheck.py`, and
written this in the docstring:

> *"The height of a circle is not written down anywhere in the file; it is
> implied by the arc centre and radius."*

That was about `Edge.Cuts`, where two G02 semicircles made a Ø30 mm board
measure `30000000 × 0`. Then I wrote a footprint survey that read arc control
points and changed a schematic with it.

**Knowing the principle in one file did not stop me applying the wrong method in
the next**, because I did not recognise the second problem as the same problem.
A lesson attached to a file is not attached to the class.

## What caught it

Not review, and not the third parse. **The build refused.** `board_fab.py` read
BT1's courtyard back *out of the board* through `pcbnew` and got 27.5 × 24.42,
contradicting the survey that had chosen the part.

An artifact-level check caught a defect in the measurement that fed it. That is
the same argument as E09, one level up: **read it back off the built thing, not
off the number you computed on the way in.**

## Corrected result

| footprint | W × H | diag | Ø30? |
|---|---|---|---|
| Battery_Panasonic_CR2032-VS1N_Vertical | 20.70 × 6.32 | **21.64** | **FITS** (solder-tab **cell**, not a holder) |
| Battery_Panasonic_CR2032-HFN_Horizontal | 22.68 × 20.62 | 30.65 | no |
| BatteryHolder_MYOUNG_BS-07-A1BJ001 | 27.50 × 24.42 | 36.78 | no |
| BatteryHolder_Keystone_3002 | 31.79 × 21.73 | 38.51 | no |
| BatteryHolder_Multicomp_BC-2001 | 31.99 × 21.54 | 38.57 | no |
| BatteryHolder_Keystone_1060 | 32.99 × 21.50 | 39.38 | no |
| BatteryHolder_Renata_SMTU2032-LF | 33.09 × 23.45 | 40.56 | no |
| BatteryHolder_Keystone_1058 | 32.99 × 23.68 | 40.61 | no |
| BatteryHolder_Keystone_1057 | 34.39 × 23.63 | 41.73 | no |
| BatteryHolder_MPD_BC2003 | — | — | **declares no courtyard at all** |

**Nine of nine measurable CR2032 holders are too big for a Ø30 mm disc.** The
only fitting row is a cell you solder in permanently. This is a fact about the
board's size, not about the part chosen.

## What changed as a result

- **`board_fab.py` refuses** any footprint whose courtyard diagonal exceeds the
  board diameter, naming ref, width, height and diagonal. A rectangle fits a
  circle only if its **diagonal** does, so no rotation or position can rescue
  it — and a placement solver cannot report this, it just pushes the part
  around and reports convergence.
- **A footprint with NO courtyard is now CANNOT DETERMINE (exit 2), not a
  silent skip.** `MPD_BC2003` would have passed this check without ever being
  measured. Unmeasurable is not compliant.
- **The method rule:** *a geometry question goes to a geometry engine.* Reading
  coordinates out of a file answers "what points are written down", which is a
  different question and fails toward a **smaller** answer — the worst
  direction, because an under-measurement looks like a measurement while an
  empty result looks like a failure.

## What is not claimed here

That the corrected table is complete for all vendors — it covers KiCad's own
`Battery.pretty` only. And the replacement part is **not chosen**: that is a
design decision, and after getting this wrong once I am not making it.
