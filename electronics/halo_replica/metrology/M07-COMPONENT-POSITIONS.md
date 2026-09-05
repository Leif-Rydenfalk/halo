# M07 — component positions on the project FRONT, in mm and in genuine pixels

*halo Replica, L1 PHOTOGRAPH METROLOGY lane, 2026-09-05.*

**SIDE NAMING:** FRONT = the COMPONENT side (Apple's FCC caption). O'Flynn's
`backside-fullres.jpeg` **is** this project's FRONT.

**Reproduce:** `tools/m_components.py --png <out.png> --json metrology/components-front.json`
→ exit 0. Raw: `metrology/components-front.json`.

---

## 1. L2's `c_register` was run, not trusted — doctor, selftest, validate first

| verb | result |
|---|---|
| `doctor` | **6/6**, canary a real measurement (known transform θ=−63, scale 0.35 → NCC 0.9972, centre error 2.71 px) |
| `selftest` | **5/5**, including three deliberate breaks: a noise target yields no registration (NCC 0.034 against a 0.30 floor); a featureless target has **all 160** landmarks discarded; the hold-out goes red on a radial warp a homography cannot absorb (0.048 → 0.882 px) |
| `fit` | **PASS**, NCC 0.6861, **3.38×** its own worst wrong-rotation null |
| `validate` | **PASS**, worst held-out fold **0.1029 mm** over four spatial folds |

It is a well-built tool and its controls fire.

## 2. THE DEFECT I COULD SUPPLY AND ITS AUTHOR COULD NOT

Its built-in scale basis is `ruler-calibration.json photo6_bottom` = **15.8875
px/mm** — the bottom rule's value **at the rule**, near the frame edge. M02
measures **15.6850 at the board**, by two routes 0.23 % apart. That is **1.29 %
low**, and it propagates to every millimetre:

> transferred source scale **107.686 → 106.313 px/mm**

### And the held-out error is blind to it — demonstrated, not argued

`validate` re-run with the corrected scale gives the worst fold **0.1029 mm —
identical to four decimals.** It converts the fitted and the held-out landmarks
to mm with the *same* px/mm, so a wrong scale divides both sides equally and
cancels exactly.

> **0.1029 mm is a statement about REGISTRATION CONSISTENCY and carries no
> information about SCALE ACCURACY.** A 1.29 % scale error and a 0.1029 mm
> held-out error coexist happily, and the second never warns you about the first.
> Same family as E04: the check shares its assumption with the thing it checks.

Fixed by extension, not by forking: `--target-px-per-mm` / `--target-px-per-mm-basis`,
and when the default is used the tool now **prints** that it is the rule's value
and names the board-located alternative. Default behaviour unchanged.

**Independent cross-check that the scale is otherwise sound:** O'Flynn's board
bbox 2672 × 2888 px against M02's geometric-mean diameter 25.65 mm gives 108.3
px/mm, within **1.9 %** of 106.313 — and the bbox of a *rotated* board
overestimates its diameter, so 108.3 is an upper bound and the two agree.

## 3. The result

The board frame is **transferred** through the validated homography (FCC6 →
O'Flynn), because O'Flynn's image has no scale reference and no measurable
outline of its own — its surround is not uniform (dark clamp bars touch the
board) and an azimuthal edge finder returns CANNOT DETERMINE on it, as it did.

| | |
|---|---|
| stored scale | **106.313 ± 0.440 px/mm** |
| **genuine scale (M06)** | **20.7–27.4 px/mm** — stored/genuine = **3.9–5.1×** |
| registration hold-out | 0.1029 mm = **2.1–2.8 genuine px** |
| bright features located | **95** |
| **with a short side ≥ 10 genuine px** | **32** |
| median detection area | **0.178 mm²** |
| threshold plateau | count varies **13.0 %** across a 95–155 luma sweep |
| centre-hole control | **0 objects** |

**The median detection is 0.178 mm², which is 0201 nominal (0.6 × 0.3 mm) to
1 %.** Per M06 an 0201 is 6–8 genuine px on its short side, so **most of these 95
are located but not sized.** Only the 32 flagged SOUND carry a size claim; the
other 63 carry a *position* and nothing more. Every row prints its short side in
genuine pixels so the distinction cannot be lost downstream.

## 4. LIMITATIONS, stated because they change what may be built on this

- **The detector finds BRIGHT features and misses DARK IC bodies.** The
  nRF52832, the black package at 9 o'clock and the other dark plastic packages
  are **not** in the 95. What is detected is metal: pads, terminations, cans,
  solder. For a footprint that is arguably the right thing; for a placement list
  it is a hole, and it is a hole with names in it.
- **Two objects longer than 7 mm are merges**, not parts: 14.48 × 7.55 mm and
  7.30 × 3.96 mm. Adjacent pads join at these thresholds. Nothing above ~7 mm in
  the list is a single component.
- **Do not quote these positions to 0.01 mm.** At 20.7–27.4 genuine px/mm the
  registration floor alone is 2.1–2.8 genuine pixels.

## 5. WHAT I DISCARDED

1. **The transferred FCC6 centre hole — visibly wrong, and the overlay is the
   evidence.** Drawn onto O'Flynn's image it is offset and too small, cutting
   across real board on the right and excluding components there. That is what
   M02 §4's *"PARTIALLY DETERMINED, do not publish a single hole diameter"* looks
   like when you draw it. Replaced by segmenting O'Flynn's **own** hole.
2. **A negative control that could never pass.** The first version ran the
   detector inside the centre hole and required zero objects — but the hole is
   **bright background seen through the board**, so an unbounded detector always
   returns exactly one object (the whole hole). It reported 1 at every threshold.
   Fixed with a **physical** upper size bound (60 mm²; the largest real part, the
   UWB can, is ~35 mm²) rather than by lowering the requirement. **A control that
   can never pass is as useless as one that can never fail, and it is the same
   defect wearing the opposite sign.**
3. **The hole on O'Flynn's image is still not cleanly measurable, so M02 §4
   stands.** Segmenting it there gives a superellipse residual sd of 0.34 mm, a
   circle that fits marginally *better* than the squircle (34.66 vs 35.80 px),
   `n` pinned at its lower clamp of 2.00 — contradicting FCC photo 6's n = 2.70 —
   and no threshold plateau (area moves 30 % between luma 190 and 210). Its
   boundary abuts bright components and the segmentation bleeds into them.
   **Two independent photographs now fail to pin the hole, in different
   directions. It remains PARTIALLY DETERMINED.**

## 6. Status

| # | quantity | verdict |
|---|---|---|
| 1 | `c_register` doctor / selftest / validate | **PASS**, controls fire |
| 2 | its scale basis | **CORRECTED** — was at the rule, 1.29 % high |
| 3 | that the held-out error cannot see a scale error | **DEMONSTRATED** — identical 0.1029 mm both ways |
| 4 | positions of 95 bright features, in mm and genuine px | **MEASURED**, plateau 13.0 %, control 0 |
| 5 | sizes of those features | **32 of 95 SOUND**; the rest are located, not sized |
| 6 | dark IC package positions | **NOT MEASURED** — the detector is blind to them |
| 7 | centre-hole geometry | **PARTIALLY DETERMINED** — now failed from two photographs |
