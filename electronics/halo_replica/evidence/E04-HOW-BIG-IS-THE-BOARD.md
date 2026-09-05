> # ⛔ RETRACTED — see `E05-RETRACTING-E04.md`
> **The conclusion below ("about 25 mm, not 26") is WITHDRAWN.** The two image axes do not
> share a scale. Measured per-axis, the board is **26.3 mm wide and 25.0 mm tall**, bounded
> 24.95–26.34 mm, and O'Flynn's "~26 mm" is NOT contradicted. My "four independent methods"
> all inherited one shared assumption — a scalar px/mm on an anisotropic projection — so they
> could not have disagreed about the thing I used their agreement to establish. Kept unedited
> as the record of the error.

# E04 — how big is the board, and how well do we actually know it

*halo Replica lane (orchestrator), 2026-09-05. A cross-lane reconciliation: each lane below
me sees one scale method, and only this level sees all four disagreeing.*

**Answer: about 25 mm, not 26 — but at 1.65–1.94× the worst systematic we can observe, which
is evidence, not proof.** Nobody should quote 26 mm as measured. Nobody should quote 25 mm as
settled either.

## The four determinations

| # | method | photograph | result |
|---|---|---|---|
| 1 | O'Flynn's stated figure | — | **"~26 mm"** — his tilde. Not a measurement; `REFERENCE-TEARDOWN` §7 already lists true diameter as CANNOT DETERMINE |
| 2 | steel rule, bottom, 93 ticks / 97 mm (L1) | FCC-6 | **15.8875 px/mm**, stderr 0.0022, split-half 0.33 % |
| 3 | outline fit against Apple's own silhouette (L5) | FCC-6 | ours **24.997 mm**, Apple's **24.832 mm**, RMS 0.281 mm over 720 rays |
| 4 | nRF52832-CIAA published package as an in-photo ruler (L3) | O'Flynn comp. side | **110.3 px/mm** — measured aspect 1.087 vs datasheet 1.0914, **0.4 % apart with nothing fitted** |
| 5 | ruler datum transferred by homography (L2) | O'Flynn comp. side | **107.686 px/mm**, held-out fold RMS 0.1029 mm |

## The two disagreements that set the real uncertainty

Both are *within* a single photograph or *between two methods on one photograph*, so neither
can be blamed on comparing different things.

- **FCC-6's two steel rules disagree by 2.03 %** — 15.8875 px/mm (bottom) against 15.5651
  px/mm (right). Two rules in *one frame*. The board and the rules are not coplanar, or the
  camera is off-axis. **Found by L2; not resolved by anyone.**
- **Two independent scales on O'Flynn's component side disagree by 2.43 %** — 110.3 px/mm
  from a datasheet package against 107.686 px/mm transferred from the ruler photograph.

**Worst observed systematic: 2.43 %.** That is the floor on any absolute millimetre this lane
publishes. It is not statistical noise that averaging removes — it is perspective, and it is
one-sided in a way nobody here has bounded.

## Does "smaller than 26 mm" survive it?

| estimate | ±2.43 % band | is 26 mm inside? | distance |
|---|---|---|---|
| ours, 24.997 mm | 24.390 – 25.604 | **outside** | +4.0 %, **1.65×** the systematic |
| Apple's silhouette, 24.832 mm | 24.229 – 25.435 | **outside** | +4.7 %, **1.94×** the systematic |

**It survives, and not comfortably.** At 1.65–1.94× a systematic whose sign nobody has
determined, this is a *strong indication* that 26 mm is too large, not a refutation. Anyone
quoting this must quote the multiple.

## Why the agreement is worth something anyway

Applying this lane's own corroboration rule — *name what each read would have had to see to
disagree* — these are genuinely independent:

- **The datasheet ruler could have returned 26 mm and did not.** Its scale comes from Nordic's
  published package dimensions on O'Flynn's photograph; the steel rule's comes from a
  machined artifact in Apple's photograph. Different scale sources, different photographs,
  different failure modes. Nothing links them.
- **L3's method self-corroborated before it was used**: measured package aspect 1.087 against
  published 1.0914, 0.4 % apart, with the segmentation knowing nothing about the datasheet.
- **L2's transfer was validated on held-out spatial folds** — fit on three angular sectors,
  error measured on the sector never seen — and the held-out error sits *just above*
  in-sample, which is the correct ordering.

Four routes, two photographs, two kinds of ruler, all landing **below 26** and none landing
above. That is what makes it evidence rather than a coincidence of one contaminated pipeline.

## Numbers that must NOT travel

- **23.9 mm.** L2's board-circle seed (O'Flynn centre 1405,1700, r 1287.5) divided by its
  transferred scale. It is a **search seed, not an edge fit**. L2 flagged it explicitly.
- **L1's raw r(θ) profile.** It reaches 125 px against a mean of 179.5 — a 30 % excursion no
  manufactured outline has — and I ruled out perspective as the cause (cos 2θ explains 7.5 %).
  It is contaminated. L5 re-extracted rather than inheriting it, and was right to.
- **The UWB can at 20.8 mm²**, suspiciously equal to TechInsights' 20.58 mm² for the U1 *die*.
  A SiP must exceed its die. L3 labelled it "do not repeat without re-measuring".

## What would settle it

A caliper on a real board. Failing that: **resolve FCC-6's 2.03 % inter-ruler disagreement**,
which is the cheapest real gain available — it is one photograph, both rules are in it, and
whoever bounds the perspective there tightens every absolute millimetre in this lane at once.
