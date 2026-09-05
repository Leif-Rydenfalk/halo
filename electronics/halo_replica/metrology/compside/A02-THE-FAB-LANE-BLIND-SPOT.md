# A02 — a part can hang 4.4 mm off the board and every fab check returns PASS

*halo Replica, lane L2, 2026-09-05. Audit requested by the parent lane. **Demonstrated, not
argued: the break was performed and the checks were run on it.***

## The question I was asked to put to the fab lane

> *"What transformation of the board would leave these numbers unchanged?"*

Applied to `cepcb/place.py`'s two load-bearing rows — **"45 of 45 footprints read back inside
Edge.Cuts"** and **"no two courtyard POLYGONS intersect"**.

## The answer: displace a part's BODY relative to its ORIGIN

**Nothing in `verify()` tests a COURTYARD against Edge.Cuts.**

- **"on the board"** tests footprint **origins** (`GetPosition()`) against a disc.
- **"courtyards clear"** tests courtyards **against each other**.
- **"origin vs centre"** measures the gap between the two and is explicitly, correctly
  labelled a report rather than a check.

So the board edge is checked against origins, and courtyards are checked against neighbours,
and **the pair a fab actually cares about — courtyard against board edge — is checked by
nothing.**

## Demonstrated on the real board

Measured first, on `fab/out/halo_replica_fab.kicad_pcb` as committed:

| | |
|---|---|
| Edge.Cuts inscribed radius | 15.050 mm |
| origins outside it | **0 of 45** |
| courtyards reaching outside it | **0 of 45** — *the board as it stands is fine* |
| worst courtyard reach | J1 at 14.421 mm (0.63 mm of headroom) |
| **worst origin-to-courtyard-reach gap** | **J1, 4.52 mm** (U3 4.29 mm) |

That gap is the size of the blind spot. So I made it bite. **J1 pushed radially outward until
its origin sits 0.10 mm inside the edge:**

```
AFTER THE BREAK, J1:
  origin radius     14.950 mm   (edge is 15.050)  -> INSIDE, row 1 passes
  courtyard reaches 19.452 mm   -> 4.402 mm OFF THE BOARD

cepcb.place.Placer.verify() ON THE BROKEN BOARD:
  on the board        PASS    45 of 45 inside the Ø30.10 mm Edge.Cuts, measured from the board
  courtyards present  PASS    every part declares a courtyard
  courtyards clear    PASS    no two courtyard POLYGONS intersect
  origin vs centre    report  4 part(s) have a courtyard centre away from their origin (max 5.08 mm)
  sides               PASS    10 top, 35 bottom

  OVERALL VERDICT: PASS
```

**A connector hanging 4.4 mm off a Ø30 mm board, and the suite is green on every row.**

This is the same defect family as the translation invariance that once hid 33 of 45 parts:
not the same transformation, but the same shape — *a quantity the check never looks at.* And
the module already prints the magnitude of its own blind spot: **"max 5.08 mm"**, in the very
row below.

## The fix, one row

Test the **courtyard polygon** against **Edge.Cuts**, and make it fail on the board above:

```python
# for each footprint: the greatest radius its courtyard reaches
rmax = max(hypot(pt - edge_centre) for pt in courtyard_outline_points)
outside = [ref for ref, rmax in ... if rmax > er]
```

**And it should not use `er` for long.** `er = min(bbox.width, bbox.height)/2` models Edge.Cuts
as a **disc**. That is right for this Ø30 disc and **wrong for the halo replica board, which
is ANNULAR**: a part sitting in the centre hole is at small radius and would pass a disc test
cleanly. Not a defect today — the fab board is solid — but it is a defect the moment this
module is pointed at the real outline, which is the whole direction of this project.
(Also minor: the Ø30 board reads as Ø30.10 because Edge.Cuts' 0.1 mm stroke width is inside
the bounding box, so `er` is 0.05 mm optimistic.)

## What I did NOT find

I looked for a way to make **"courtyards clear"** wrong on its own and did not find one worth
reporting. It uses KiCad's own `BooleanIntersection` on the real polygons, reads the courtyard
from whichever face carries it, and includes cross-face pairs when either part is
through-hole. Its one soft edge: `_overlap_mm2` returns `None` when either part lacks a
courtyard and the caller's `if a:` treats that as *no overlap*, so such pairs are silently
skipped while the row still says *"no two courtyard POLYGONS intersect"*. Today the separate
**"courtyards present"** row catches that with CANNOT DETERMINE, so the overall verdict is
safe — but the two rows are coupled and nothing enforces the coupling. Worth a word, not a
code change.

The module's docstring is unusually honest about its own history — the wrong face, boxes not
being courtyards, through-hole having no face, a part that cannot fit, unmeasurable not being
compliant. **Every one of those was found the hard way and written down. This is one more of
the same kind, and it is the last one I can find.**

## Method

Read-only on `cepcb/place.py`; the break was made on a **scratch copy** of the board in the
session scratchpad, never on the committed file. `verify()` was invoked directly — not
reimplemented — with a minimal board wrapper, so the output above is that module's own, on
KiCad's own geometry engine (KiCad's Python 3.9, `pcbnew`).
