# E09 — The parts were not on the board, and every check I had agreed they were

**Date:** 2026-09-05 · **Lane:** fab · **Verdict:** FAIL found, fixed, both
directions broken on purpose.

## What I believed

`fab/out/halo_replica_fab.kicad_pcb` was built, checked and reported:

```
RELAX      636 iterations, 15973 pushes, courtyard clearance 0.2 mm
PLACED     45 parts on a Ø30.0 mm disc, NO courtyard overlaps
BOUND      63 of 63 nets
```

Three numbers, all true, all measured. The board was still unroutable.

## What freerouting was actually telling me

Four consecutive auto-routing passes, each running to completion:

| pass | seconds | score | unrouted | violations |
|---|---|---|---|---|
| 1 | 505.9 | 0.00 | 106 | 54 |
| 2 | 764.3 | 0.00 | 106 | 54 |
| 3 | 453.8 | 0.00 | 106 | 54 |
| 4 | 1618.6 | 0.00 | 106 | 54 |

**I read this as "needs more passes" and gave it `-mp 100`.** It is not that.
An optimiser that returns a byte-identical score four times is not converging
slowly — it is reporting that it cannot move. 3502 s of wall time and 1913 s of
CPU bought exactly nothing, and no `.ses` was ever written, because freerouting
emits only at the end of its full pass budget.

**The reading rule:** identical unrouted/violation counts across passes means
CANNOT ROUTE. Only a *changing* score means slow. Do not raise the pass budget
against a flat score; diagnose the input.

## The defect

`Board(diameter=30)` places the disc at centre **(15, 15)** — origin at the
corner of the bounding box, not at the centre. `board_fab.py` computed every
position on rings centred on **(0, 0)** (`RINGS = {0: 0.0, 1: 5.4, … 4: 12.4}`,
`R_KEEP` a radius, `math.hypot(*pos[r])` a distance from the centre) and handed
those numbers straight to `place()` and `SetPosition()` without ever adding the
centre.

Measured off the built board:

```
EDGE.CUTS bbox mm: x -0.050..30.050  y -0.050..30.050
FOOTPRINTS: 45      x -11.932..10.876   y 19.782..41.714
OUTSIDE edge-cuts bbox: 33 of 45
```

The whole cloud sat off the copper. Freerouting was being asked to route parts
that were not on the board — so it routed 5 of 111 connections and flatlined.

## Why every check I had said it was fine

```python
outside = [(r, …) for r, p in pos.items() if math.hypot(*p) > R_KEEP]
```

`pos` is the intermediate the relaxation loop just computed, and `R_KEEP` is a
radius in that same origin-centred frame. **The check and the thing it checks
share a frame, so it is true by construction and stayed green through the entire
bug.** Same for the courtyard-overlap check: relative distances between parts are
invariant under a translation, so a rigid shift of all 45 parts off the board
changes not one of its numbers. Both checks were correct. Neither could fail on
this defect.

This is E07's shape — a check that cannot fail — arriving through a **frame**
rather than through an estimator. The two checks were not weak; they were asking
about the intermediate when the defect was in the handoff to the artifact.

## The check that can fail

Read every footprint position **back out of the board** and compare it to the
**real Edge.Cuts circle**, measured from the board, not from any variable the
placement code produced:

```python
_eb  = b._pcb.GetBoardEdgesBoundingBox()
_ecx = (_eb.GetLeft() + _eb.GetRight()) / 2e6
_ecy = (_eb.GetTop()  + _eb.GetBottom()) / 2e6
_er  = min(_eb.GetWidth(), _eb.GetHeight()) / 2e6
for _fp in b._pcb.GetFootprints():
    _p = _fp.GetPosition()
    if math.hypot(_p.x/1e6 - _ecx, _p.y/1e6 - _ecy) > _er:
        REFUSE
```

Nothing in it comes from `pos`, `RINGS`, `R_KEEP` or `coords`.

## Broken on purpose, twice, in the two shapes that matter

- **Global shift** — removed the translation in `SetPosition`:
  `PLACEMENT REFUSED: 36 of 45 footprints read back OUTSIDE the Ø30.10 mm
  Edge.Cuts circle at (15.00,15.00): [('AE1', 29.77), ('C10', 18.68), …]`
- **One single part** — this one was *not* staged; it was found. With the
  `SetPosition` frame fixed but `place()` still unfixed, the check caught
  **`BT1` alone at 21.21 mm** — exactly `hypot(15, 15)`, the signature of a part
  left at raw `(0, 0)`. `BT1` is in `BACK_SIDE`, excluded from `pos`, so the
  relaxation loop never touched it and it kept its wrong `place()` position.
  **A second, independent defect that the old checks also could not see.**

A check that fires only on a global shift could be passed by any localised
error. This one fired on both.

## After

```
ONBOARD    45/45 footprints read back inside Edge.Cuts (Ø30.10 mm at 15.00,15.00)
           - measured from the board
PLACED     45 parts on a Ø30.0 mm disc, NO courtyard overlaps
BOUND      63 of 63 nets
```

## What is not settled here

That the parts are now *on* the board is not a claim that the board routes. The
routing result is a separate measurement and is recorded separately.
