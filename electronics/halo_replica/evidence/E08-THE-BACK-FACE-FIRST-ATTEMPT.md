# E08 — the back face: the scale arrived, the parts did not

*halo Replica lane L9, 2026-09-05. Two results, and they should not be read as one.
**The scale transfer WORKED and is usable now. The capacitor measurement DID NOT, and
its own controls are what say so.***

---

## 1 · What was unblocked, and it is the important half

`THREE-WAY.md` row 24: the Replica has drawn **one of Apple's two populated faces**, and
four axes are UNSTARTED for that single reason — battery contacts, the five bulk
capacitors, the ~38 test points, and half of coverage itself.

**The blocker was never the photograph.** `oflynn-frontside-fullres.jpeg` is the
*sharpest source in the project*: M06 measures **0.445–0.570 of Nyquist, 33–42 genuine
px/mm**, against the component face's 0.195–0.258 and ≈20–27. The better picture has
always been of the face nobody measured.

The blocker was that **`c_register`'s catalogue held no ruler-bearing view of this face**,
so no scale could reach it. Fixed:

| | |
|---|---|
| new view | `fcc7-back` — FCC internal photo 7, "MLB – Back" |
| its scale | **15.0719 px/mm**, `metrology/scale-at-board-photo7.json`, measured **at the board**, two routes 0.45 % apart |
| seed corrected | `oflynn-back` r 1090 → **962**. 1090 traces the plastic carrier. It put the true scale ratio **13.3 % out** — outside the fit's ±10 % refine window — so a BACK registration could not have converged even with a target present |
| registration | NCC **0.5066** against a wrong-rotation null of max **0.1449** — **3.50×**, floor 2.50× |
| landmarks | 58 kept of 402; **344 discarded and counted by reason** |
| **transferred scale** | **69.557 px/mm**, spread 69.350–69.754 over the board (0.18 %) — a tilted view has no one scale |
| **held out** | **0.1256 / 0.0931 / 0.1035 / 0.1170 mm** on four spatial folds, tolerance 0.20 mm. **PASS** |

**The assumption this shares with its own control, written into the view entry rather than
left implicit.** Photo 7's silkscreen reads **920-08283-01**, data code 3119 — a 2019
engineering build. O'Flynn's reads **820-01736-A**, data code 2920 17 — 2020 production.
**These are two different boards.** A uniform dimensional difference between them is
absorbed into the fitted scale and leaves the held-out residual **completely unchanged**,
because the check divides both sides by the same number. *Registration consistency is not
scale accuracy.* Unsettleable from here; a caliper on one board of each part number
settles it. **The same caveat already applied, unstated, to the FRONT pair
`fcc6-front` / `oflynn-front`, and therefore to the Replica's 106.313 px/mm.**

Two defects fixed in `c_register` on the way (P11 — a gap in a core tool is fixed there):

1. **The scale-basis note was hardcoded to photo 6 and printed under every target.**
   Pointing the tool at `fcc7-back` produced a correct scale wearing photo 6's
   provenance — "this is the rule's value AT THE RULE… 1.29 % lower", which is false of
   photo 7, whose value is already at the board and whose two routes differ by 0.45 %, not
   2.07 %. A right number with the wrong reason printed over it is `TOOLS-THAT-LIE.md`'s
   family. The note is now a property of the view.
2. **The same string was written into every output JSON** as `transferred_scale.inherits`.
   It now quotes the target's own basis.

`c_register selftest` still passes 5/5 after both, including the hold-out break that must
go red on a radial warp a homography cannot absorb.

---

## 2 · What did not work, and every step of it was caught by a control

`tools/k_backface.py` set out to measure the five bulk capacitors — the right first
target, because they are the largest discrete parts on either face and the row where
`halo_rev_a` sits at **one twelfth** of Apple's bulk with **no package to compare
against**. They are also the opposite of M08's problem: a tantalum brick is a **dark body
between two bright metal terminations** (measured: body luma 40.8 sd 15.7, terminations
200–225), so the discriminator is structural, not "it is dark".

**It refuses all five, and `selftest` fails. Four things went wrong and each was found by
a control rather than by inspection.**

### 2.1 The first null could not discriminate — and it was replaced, not re-thresholded

The gate compared the profile's range against a null built by **permuting its
increments**. A clean synthetic part scored **z = 2.48**; bare ground **z = −3.88**; a
single stray bright bar **z = 2.00**. The real part sat *below any threshold that would
have rejected the stray bar.*

A profile with two sharp peaks has large increments, so permuting them builds a random
walk with a large range: **the null manufactures the property under test**, which is
E07 §2's failure exactly. Replaced. *Lowering the threshold until the answer appeared was
available and is the defect, not the fix.*

### 2.2 The second estimator measured the signal and called it noise

Contrast-to-noise, with noise as the MAD of the off-peak samples. A clean synthetic
3.5 mm part scored **CNR 1.00** — because a 3.5 mm body fills two thirds of the window, so
the "off-peak" set was mostly the part's own flanks and the estimator returned **sd 11.7
against bare ground's 0.7**. Replaced with the MAD of successive differences, which is
blind to smooth structure of any amplitude.

### 2.3 The calibration population was not a null, and looking is what showed it

`calibrate` sampled 120 random annulus windows to set the floor from the control rather
than from the answer. It returned **median 116, p95 971, max 1341**. A threshold of 1341
rejects every real part.

The 12 lowest-variance windows were rendered and **looked at**. Every one still holds test
pads, silkscreen (`2920 17`, `-A`) and an IC marked `4BU LA`. **There is no bare
soldermask on this face.** So the sample was a population of real structure, not of
nothing, and **no z threshold can be calibrated from this photograph at all.** Recorded as
the limit it is: the z gate now only excludes featureless noise, and admission is decided
by two structural gates instead.

*The instinct that was wrong before it was tested, and is worth writing down:* the obvious
null here is L7's row-roll — roll each row independently. **It cannot fire against this
statistic.** The statistic is a profile of **row means**, and rolling a row horizontally
leaves its mean exactly unchanged. The null that does work permutes the **rows**, and only
because the statistic was rebuilt on the **contiguity** of a band rather than its peak
value — a peak-height statistic survives row permutation untouched. *The null and the
statistic have to be designed against each other.*

### 2.4 And the answer was a function of the operator's window — the M08 attempt-3 failure

With a good seed, C1 measured:

| window span | result |
|---|---|
| 1.6 mm | **3.192 × 1.581 mm** |
| 2.0 mm | REFUSED |
| 2.4 mm | 4.699 × 4.414 mm |

**3.192 × 1.581 mm is EIA 3216 / Case A (3.2 × 1.6 mm) to 0.25 % and 1.2 %.** It is
almost certainly the right answer. **It is not published, and the reason it is not
published is the whole point of this section:** the same seed returns 4.70 × 4.41 mm two
window sizes later. That is M08 attempt 3 — a stated ROI plus Otsu whose answer swung
3.35 → 4.50 mm on padding alone — and **landing on a plausible standard case code makes
the temptation worse, not better.** A number that matches what you expected, produced by a
method that also produces numbers that do not, is not a measurement.

`caps` now admits a part **only if the same size returns through all three spans**, and on
that gate **all five are refused**. `selftest` S6/S7 are the same gate on synthetic ground:
S7 confirms it fires (a 6 mm part clipped by a 2 mm window disagrees, 3.997 vs 5.923), and
**S1/S6 confirm the width estimator is broken** — a synthetic part 2.200 mm wide measures
0.855 mm at one orientation.

### 2.5 The negative control fired, and its first name was wrong

Six seeds on what were called "bare soldermask": **three were admitted as parts**
(1.571 × 5.183, 1.911 × 4.349, 4.978 × 2.588 mm). They are not bare — §2.3 — so the
control is asking a harder and better question: *can the refiner tell a capacitor from
this board's ordinary structure?* **Measured answer: no.** `caps` exits **FAIL** on it.

---

## 3 · The candidates, recorded and NOT published

In `metrology/backface-caps.json` under `candidates_not_published`. They are leads for the
next lane **with the reason each was refused attached**, and they are not sizes:

| ref | span | result |
|---|---|---|
| C1 | 1.6 mm | 3.192 × 1.581 mm |
| C4 | 2.0 mm | 3.508 × 2.200 mm |
| C5 | 2.0 mm | 3.465 × 2.121 mm |
| C2 | 2.0 / 2.4 mm | 1.363 × 3.285 / 1.366 × 3.436 mm |

Three of them cluster near **3.2–3.5 × 1.6–2.2 mm**. That is suggestive and it is not
evidence: they share a method, a scale and an operator's seed, so they could not have
disagreed about any of those. **What would settle it is in §4, not in another read of
this table.**

---

## 4 · What would close it, in order of value

1. **Fix the width estimator.** It reads the bright run across columns at the band row and
   is orientation-sensitive; S1 is the failing case and it is synthetic, so it can be
   iterated on without touching the photograph. Until S1 and S6 pass there is no reason to
   believe any width off this tool.
2. **Mask to the part before profiling.** Every window failure above is contamination by
   neighbours — C1, C2 and C3 sit within 2 mm of each other on the left rim. A two-pass
   refine that restricts the columns to the part's own width after the first orientation
   estimate addresses the cause rather than the symptom.
3. **Then, and only then, the EIA case-code check.** If a fixed body size survives the
   window-invariance gate, comparing it to the standard case codes is a **scale check that
   does not pass through the FCC rulers or the 920-/820- board-identity assumption** — the
   first independent scale evidence this project would have. `k_backface` already
   implements it and refuses to quote it when the nearest two codes are ambiguous.
4. **The rest of the face is easier than the capacitors and is untouched:** the three
   battery contacts are large bright metal, the ~38 test points are round gold pads with
   `oflynn-frontside-tpnames.jpg` already annotating every one, and the wound coil was
   measured by M01 in a **12 genuine px/mm** crop when a **33–42** one is now registered.
   **Re-measuring the coil in this frame is the cheapest real result on this face** and it
   bears directly on THREE-WAY row 7's 2.1× radial difference against `halo_rev_a`.

---

## 4b · The coil, re-measured in the new frame — and L1's threshold does not transfer

§4 item 4 called this "the cheapest real result on this face". It was cheap and it is a
result; it is not the one expected.

M01 measured the wound coil at **ID 9.380 / OD 10.834 mm, band width 0.727 mm**, in
`oflynn-frontside-26mm-cropped.jpg` at **30.2762 px/mm** on a datum of *"787.18 px =
26 mm APPROXIMATE"* — O'Flynn's own tilde, which E04→E05 later retracted as a figure.
`k_backface coil` reproduces **L1's exact copper criterion** (R−B > 28, R > 90, luma < 250)
in the registered full-resolution frame at **69.557 px/mm**, whose scale comes from two
FCC steel rulers instead.

**The design point, stated before the numbers:** the 26 mm crop is *a crop of this same
photograph*. The two measurements share every pixel and **cannot disagree about the coil**.
What they do not share is the **scale**. So this was built as a comparison of **two
independent scale routes** on one object — a teardown page's tilde against an FCC
exhibit's rulers — and that is the only claim it could have supported.

**It supports nothing, and the control is what says so.**

| | band width | verdict |
|---|---|---|
| M01, 26 mm crop, 30.2762 px/mm | **0.727 mm** | the winding |
| here, full frame, 69.557 px/mm | **2.732 mm** | **not the winding** |

The band runs r 3.818 → 6.549 mm. Peak copper fraction inside it is **0.314**; the peak in
a control annulus at r 9–11 mm, where there is no coil, is **0.230**. **Separation 1.37×
against a 2.00× floor.**

**L1's 0.25 threshold was set in a tight 26 mm crop at 12 genuine px/mm, where the frame
holds little but the coil. In the full frame the whole board's gold pads and traces are in
view, and the same criterion fires on all of them.** A threshold is not a property of a
material; it is a property of a material *and a field of view*, and this one did not
travel. The 18.6 % / 20.9 % difference against M01 is therefore **not** a measurement of
the two scale routes and must never be quoted as one — it is this detector failing.

*What would do it:* the winding's turns are individually resolvable at this scale — M01
resolved them at a third of it — so a **radial periodicity test at the ~0.145 mm turn
pitch of AWG 35** separates a wound coil from a field of pads in a way a colour threshold
cannot. That also re-opens the honest version of the scale comparison.

**And it leaves THREE-WAY row 7 exactly where it was.** The 2.1× radial difference between
`halo_rev_a`'s etched coil at R10.043–10.825 and Apple's wound coil at R4.690–5.417 still
rests on M01's numbers alone. This attempt did not confirm them and did not overturn them.

---

## 4c · The pads — the one thing on this face that IS measured

Reordered ahead of the capacitors by the orchestrator, for the right reason: the
capacitors would move a BOM line, but the pads and contacts move **the picture**, and
`oflynn-frontside-tpnames.jpg` supplies **a positive control that cannot be made easy** —
Colin O'Flynn numbered every pad in 2021, with no knowledge of this detector, and his
positions can therefore disagree with it.

That image is the **same photograph rescaled**: measured **NCC 0.9993** against the
full-resolution frame with the red annotation pixels masked out. So the mapping is exact
and the annotation is genuinely external.

| | |
|---|---|
| **circular gold pads found** | **43** (55 gold components rejected on shape) |
| **median diameter** | **0.5985 mm** |
| spread | IQR 0.034 mm = **5.7 % of the median**, p25 0.573 / p75 0.607 |
| resolution | 20–25 **genuine** px across at M06's 33–42 genuine px/mm — a resolved feature, not an interpolation |
| **negative control** | the same detector off the board, r > 1000 px: **0 pads.** It can come back empty |
| **positive control** | O'Flynn's label positions sit a median **0.462 mm** from a detection; **4000 random points on the same annulus sit 1.973 mm** away. **Separation 4.27×**, floor 2.00× |

**The null is the load-bearing part of that positive control.** O'Flynn writes each number
*beside* its pad rather than on it, and this annulus is dense enough that any point is near
something — so a small absolute distance would have proved nothing. Only the comparison
against chance does.

**Shape is what selects a pad, never colour.** The colour criterion alone catches every
gold feature on the board — which is exactly what defeated the coil in §4b, in the same
frame, on the same day. Nothing in this section rests on colour alone, and that is a
direct consequence of that failure rather than a precaution written in advance.

**Apple's test-pad diameter is now a number and it was not one this morning.** It is fed
back into `THREE-WAY.md` row 17. `halo_rev_a`'s 11 named test points have no published pad
diameter in any file this lane read, so the two still cannot be compared on pad geometry —
but the Apple side of that row is no longer empty.

## 4d · The battery contacts — SOLVED, after a gate that passed for the wrong reason

**MEASURED**, and it took inverting the whole association. Three attempts; the first two
were stopped by a control rather than by inspection.

A stamped contact is **grey**, so the gold criterion cannot find these at all; they are
selected on being bright **and unsaturated**. The overexposed centre dome qualifies too and
is **excluded by name** — M01 §4 already records that the saturated white core is the
magnet/dome assembly — rather than by a size threshold picked to make the answer come out.

1. **Plain nearest-neighbour association walked uphill.** O'Flynn writes each name *above*
   the feature it names, so the nearest neutral metal to the text is the rim, not the
   contact. Caught by the VCC area-symmetry check at **83.3 %**.
2. **Associating downward fixed the direction and the symmetry check then passed at
   10.9 % — for the wrong reason.** The pair it accepted sits at **r 10.63 mm and
   r 8.07 mm**. Apple's two positive tabs are one part in one symmetric scheme; those are
   two unrelated features whose *areas* happened to agree. **Area is one number, and two
   wrong features can share it.**
3. **So the gate was given the geometry the scheme actually requires** — same radius,
   mirrored about the board's vertical axis. It now fires: **radius difference 2.567 mm
   against a 0.600 floor, midpoint 4.231 mm off axis against a 1.200 floor.**

4. **So the association was INVERTED, and that is the fix.** Instead of driving it from
   O'Flynn's labels, **the physics finds the pair and O'Flynn validates it.** Apple's two
   positive tabs are one part in one symmetric scheme, so a search over every pair of
   neutral-metal features above the board centre, one each side of the vertical axis,
   scored on same-radius + mirrored + equal-area, has a **two-parameter constraint no
   random pair satisfies**. O'Flynn's names then become a check that can still fail.

**It converges, and on the pair that had only been eyeballed before:**

| | extent | area | r from centre | θ |
|---|---|---|---|---|
| **VCC1** | 1.495 × 1.423 mm | 1.625 mm² | 8.30 mm | 251.1° |
| **GND** | 3.321 × 2.070 mm | 5.017 mm² | 8.56 mm | 269.1° |
| **VCC2** | 1.682 × 1.409 mm | 1.680 mm² | 8.26 mm | 286.6° |

Areas **3.3 %** apart, radii **0.253 mm** apart, midpoint **0.487 mm** off axis — all inside
their floors. All three sit within **2.44 mm** of a name O'Flynn wrote. And the three angles
are **symmetric about 269°**, 18° either side: three contacts at the top of the board, which
is the scheme the dossier describes and which nothing in this method was told to look for.

**One more selection defect on the way, and it is the same shape as the area one.** GND was
first taken as the feature *between* the two tabs in x. That picked a rim feature at
**r 11.03 mm** while the tabs sat at 7.94 and 7.68. **Being between two things in one
coordinate is not being with them.** Constraining GND to within 1.50 mm of the tabs' own
radius finds the central clip.

**The extents are still not pad dimensions.** Whether each extent is the **board pad** or the
**sprung contact sitting on it** is not separable in an assembled photograph — the two are
coincident in plan view. **FCC internal photo 4**, the battery cavity with the contacts and
no board, is the frame that separates them, and it is already on disk. The handoff carries
the positions with that stated on every contact row.

**And one thing is not separable in this frame at all, stated rather than glossed:** whether
the measured extent is the **board pad** or the **sprung contact sitting on it**. This
photograph shows the board assembled in the shell and the two are coincident in plan view.
**FCC internal photo 4** shows the battery cavity with the contacts and no board, and is the
frame that would separate them.

---

## 5 · Status

| # | quantity | verdict |
|---|---|---|
| 1 | a metric scale on Apple's BACK face | **MEASURED — 69.557 px/mm, held out at 0.1256 mm** |
| 2 | whether the 920- and 820- boards share dimensions | **CANNOT DETERMINE**, named, and unsettleable from here |
| 3 | the five capacitors' body size | **CANNOT DETERMINE** — the method's answer moves with the window |
| 4 | a null population on this face | **THERE IS NONE.** No bare soldermask exists on this annulus |
| 5 | can the refiner separate a part from ordinary board here | **NO** — 3 of 6 control seeds admitted |
| 6 | the coil, re-measured at 69.557 px/mm | **CANNOT DETERMINE** — L1's copper threshold does not transfer out of the 26 mm crop; separation 1.37× against a 2.00× floor |
| 7 | do the two scale routes (O'Flynn's tilde vs the FCC rulers) agree | **NOT TESTED.** The instrument that would have tested it failed first |
| 8 | the round gold pads on this face | **MEASURED — 43 pads, median Ø 0.5985 mm, IQR 5.7 %.** Negative control empty off the board; positive control 4.27× against chance |
| 9 | the three battery contacts | **MEASURED** — found by symmetric-pair search, validated against O'Flynn; areas 3.3 % apart, radii 0.253 mm apart, θ symmetric about 269° |
| 10 | board pad vs sprung contact | **NOT SEPARABLE** in an assembled frame. FCC internal photo 4 would separate them |
