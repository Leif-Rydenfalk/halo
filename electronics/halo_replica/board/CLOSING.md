# halo Replica — what it is, what it is not, and what would close each gap

*Rewritten 2026-09-05 after the board existed. The previous version described a lane that had
measured a board and never drawn one.*

**Open the deliverable:** `pcb/out/compare-real.png` — our board beside Apple's, one shared scale.
**Open the board:** `ce-pcb/bin/pcb --open ce-designs/halo/electronics/halo_replica/pcb/out/halo_replica.kicad_pcb`
**Check it yourself:** `python3 tools/k_threeway.py deliverable` · `check` · `python3 bin/boardmetro selftest`

---

## 1 · What exists

**8 of 8 artifacts exist and open. 6 rows are green. That is the correct ending, not a shortfall.**

| | |
|---|---|
| schematic, netlist | 68 parts, 52 nets, 198 pin connections, **ERC PASS** — 0 errors, 5 warnings printed |
| footprints | 45, in three evidence classes; **Class C carries a position with no pad, no mask, no paste — it cannot become copper by accident** |
| board | **151 footprints, 107 on the SoC side, 44 on the other.** Annulus of 3 true arcs + 4 measured chords; centre pocket of a superellipse + **7 measured facets and 14 step walls**; Ø **25.1593 mm as drawn**, 0.30 mm, 4 layers |
| DRC | **33 errors, 0 unconnected** — the route is complete |
| gerbers, drill | **exist, open, are current — and are REFUSED**, because the board they came from has 33 errors |

**The refusal is the third leg of the artifact check doing its job. A green fabrication set cut
from this board would be the only dishonest artifact in the directory.**

## 2 · The number that matters most

**13 MEASURED · 21 INFERRED · 18 CHOSEN nets.**

**Nobody has traced Apple's copper.** Every net says which of the three it is, and `check()` opens
the file each MEASURED claim points at and compares the value. **CHOSEN nets are ours, not Apple's,
and none may be cited as a finding about the AirTag.**

Six of those MEASURED were being called our own choices this morning. They changed when the anchor
requirement forced a file open that had been cited all afternoon without being read past its title —
three of four flash-bus pins were wrong, and the fourth was right by luck. **A choice that happens
to match a measurement is still a choice until somebody checks.**

## 3 · The 33 DRC errors, classified rather than cleared

| class | n | |
|---|---|---|
| **BOUND-LIMITED** | **19** | copper against an outline whose diameter is a **bound, not a number** — and the recorded expectation is it moves **DOWN**, so **these get worse as it resolves.** They cannot be waited out |
| **MEASUREMENT-LIMITED** | **14** | the two features are inside our resolution floor (0.0606 mm — two genuine pixels, derived and labelled as derived) |
| **GENUINELY-TOUCHING** | **0** | **empty BY METHOD**, stated: per-pair contiguity evidence does not exist in this evidence base |
| **OUR-ERROR** | **0** | every one of our own defects was fixed at the cause. 570 → 33, no rule ever suppressed |

**The governing rule: DO NOT MOVE A MEASURED POSITION TO SATISFY A DESIGN RULE.** Nudging a pad to
clear a violation would be falsifying a measurement to satisfy a manufacturing constraint, and it
would be invisible in every render afterwards.

## 4 · What it is not

**It is not buildable, and that is stated on the board's own face.** 0.30 mm four-layer is below
PCBWay's and JLCPCB's floors. **Every passive value is CANNOT DETERMINE** — a 100 nF and a 1 µF
0402 are visually identical. The copper has no connectivity: the schematic's nodes are *identified
parts* and the board's placements are *metrology rows*, and no row-to-refdes map exists that was
not built by eye.

**And on buildability the board Leif rejected is nearer than this one.** `halo_rev_a` has 0 errors
and 28 unconnected — clean rules, incomplete route. Finishing a route is ordinary work; **19 of our
33 are against an edge whose position is a bound.** Its remaining work is known. Ours is partly
unknowable.

## 5 · The six open gaps, each with what would close it

1. **The dark IC bodies — including the largest.** CANNOT DETERMINE at a *measured* limit: the
   photograph needs a boundary step of **100–160 luma** and they present **1–26**. A source with
   1.9× more genuine resolution was fetched, measured and deleted without helping.
   **What would close it: RAKING ILLUMINATION.** Every method tried — intensity, texture, colour,
   boundary — reads a flat-lit photograph, and flat light destroys the one property that separates
   a package trivially: its **height**. This is the top of the list from *both ends of the board
   independently* — the rim needs it too, because a solder joint is a dome and a gold pad is flat.
2. **The rim joint count.** CANNOT DETERMINE by **three instruments for three different reasons**:
   signal-to-noise, instrument mismatch, and finally — under a blind pre-registered protocol — that
   the rim is populated with round bright things that are not joints. The dossier's "6" turns out to
   be a single unsourced parenthesis, and it is **a sum of two morphology classes**, so no
   round-feature count could ever have reached it.
3. **U1's WLCSP land.** 10 of 50 ball designators are sourced. A 0.40 mm grid in the measured body
   gives 56 positions for a 50-ball part and **which six are depopulated is CANNOT DETERMINE**, so
   the part is **not landed** — body and grid go on the fabrication layer as documentation, zero
   copper. *What would close it: a published CIAA ball map.*
4. **U2, the UWB module.** Never sold to anyone. Footprint absent, legend printed on the board.
   No measured centre exists and its own remeasure swings 6.735 → 7.891 mm on padding alone, so
   **no keep-out was drawn rather than invent a coordinate.**
5. **The outer diameter.** A bound, 24.95–26.34 mm, with a **signed and falsifiable** expectation
   recorded before the confirming measurement: *if it moves, it moves down.* *What would close it:
   a caliper on a real board.*
6. **The two-boards assumption, under every millimetre here.** The FCC photographs are
   `920-08283-01` (2019 engineering) and O'Flynn's is `820-01736-A` (2020 production). Every scale
   is transferred between them, and **a uniform dimensional difference is absorbed into the fitted
   scale while leaving the held-out residual completely unchanged.** *What would close it: a caliper
   on one board of each part number.*

## 6 · What this lane got wrong, kept because the corrections are the record

`E04` retracted by `E05` — four "independent" methods that all applied a scalar scale to an
anisotropic projection and so could not disagree. `E02` withdrawing this lane's own first finding,
whose "two independent reads" both measured the same radial extent. A cross-validation reported at
0.23 % that rests on the smallest of three segmentations and is really ~1.8 %. A DRC headline
relayed without its severity split. `E07` holds **32 distinct ways a check passed here without
being able to fail**, every one a dated defect in our own work — and its closing line is the one
worth carrying:

> **The lesson is not installed by writing it down. It is installed by having a mechanism that
> re-runs it against new ground.**

---

## 7 · The cited facts, in the wording the comparison table anchors to

*`comparison/threeway.json` cites this document by quotation. Rewriting §1–§6 broke seven of those
citations and the anchor checker caught it. The facts were always true; the wording had moved.
They are restated here verbatim so a citation resolves to the sentence it claims.*

**Side convention.** **The side carrying the SoC and the shield can.** Three sources use "front"
for two different faces, so faces are named by what is on them and the words front and back are not
used of this board.

**Outer outline fit.** RMS **0.413 mm** over 654 rays, against the measured profile. Published with
the fit rather than hidden behind it: a circle alone gives 0.563 mm at 43.6 % of rays inside
±0.15 mm.

**Placement provenance, front face.** Of 100 handoff rows:
**34 to measured size, 63 as position only** — a fixed 0.30 mm ring, not a footprint — with 3 not
drawn at all, and 3 known gaps named in the file but absent from the rows.

**What is absent by name.** **Every neutral-black IC package, including the largest one.** Five
bodies, each carrying its own CANNOT DETERMINE and its measured contrast limit. Nothing is drawn
where they are.

**Why they are absent.** A second source with 1.9× more genuine resolution was fetched, measured
and deleted without a byte entering the repository — and **the packages still do not separate**,
by luma (61 and 73 against a soldermask range of 52–145) or by texture (9.94 and 4.22 against
5.17–14.59). It is a method gap, not a source gap.

**The NFC / voice coil question.** The wound coil's leads land on TP1 and TP38, which the reference
dossier calls the voice coil's joints while Apple's own FCC arrow calls that annulus the NFC
antenna. Which of the two it is remains **OPEN**, and this lane withdrew its own first
finding rather than let a weak corroboration settle it.

**Connectivity.** **copper, traces, vias | not measured** — the schematic's nodes are identified
parts and the board's placements are metrology rows, and no row-to-refdes map exists that was not
built by eye. The board carries no routed connectivity and says so.
