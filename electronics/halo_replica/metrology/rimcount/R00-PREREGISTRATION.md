# R00 — PRE-REGISTRATION for a BLIND count of the rim tear-off joints

*halo Replica, lane L10 (`rimblind-99cab5fe`). Written and committed **before any pixel of the
rim was extracted**, as PROTOCOL-rim-count-blind.md §5 requires. Nothing below was written
after seeing a result; the commit that carries this file carries no measurement.*

**THE QUESTION.** How many tear-off joints attach the antenna carrier to the board rim?

**I DO NOT HAVE A PREDICTED COUNT AND HAVE NOT INVENTED ONE.** §5.5 of the protocol forbids it
and I am not registering one. Every prediction below is about the **method**.

---

## 0. The blindness, and its state at the time of writing

I am working in a **sanitised worktree**. The files that state the withheld figure are not
merely off-limits, they are **absent from the tree**. I have read, in full:
`trash/leifsays.md`, `PROTOCOL-rim-count-blind.md`, `evidence/E07-CHECKS-THAT-CANNOT-FAIL.md`
(redacted copy), `tools/d_rim.py`, `tools/d_rect.py` (engine + `side_bar`),
`tools/d_darkpkg.py` (headers), `tools/m_dark_packages.py` (`board_frame`), `bin/boardmetro`
(`circle`, `shape_evidence`, `selftest`).

**Numbers I have been given and am treating as method inputs, not as the answer:**
joint core luma **222–242** against a board ring of **34–56**; joint size **~1.3–1.6 mm**;
the rectangle attempt cleared **2 of 20** boundaries; genuine resolution **20.7–27.4 px/mm**;
stored scale **106.313 px/mm**; registration floor **0.1029 mm**; rim annulus **~1.8 mm** wide
at **0.86–1.01 r(θ)**.

**One number I met and am flagging rather than absorbing** (the protocol says to say so):
E07 §4 in this worktree has had two synthetic-pad counts replaced with **N**. I read the
redacted text. I did not attempt to recover them. E07 §2 also contains "invented ~22 peaks"
and "returned 46.8 against a real 26" — those are *rim-pad control* figures from a withdrawn
M03 analysis on a 4.6 genuine px/mm source. **They are in a rim-counting context and I am
recording that I saw them.** I do not believe either is the withheld figure (both are
explicitly described as products of controls that could not fail, on a source whose counts
were withdrawn), but **an allow-list controls which files are read, not what is inside them**,
and the honest move is to write down what I met. `d_rim.py`'s `detect(..., npeak=22)` carries
the same 22 as a search parameter. If my count lands on 22 or 26 I will say explicitly that I
had seen those numbers.

---

## 1. The instruments, and the morphology class each covers

Protocol §4.1: do not assume a morphology, and do not assume only one. I pre-register **three**
classes and refuse to merge their counts.

| class | morphology | instrument | status |
|---|---|---|---|
| **R** | round bright blob, **1.0–2.2 mm diameter** | `tools/r_circ.py` — circular-boundary-integral detector + circle-fit inlier-fraction shape gate, reached through a new `bin/boardmetro circles` verb | **this is the counting instrument** |
| **S** | straight-sided bright pad, 0.4–2.2 mm | existing `d_rect` engine via `d_rim count` | run, reported **separately and labelled**, never added to R |
| **X** | anything compact and bright that clears R's locator but **fails** R's shape gate | — | **named and counted as a separate line**, never as joints |

### 1.1 Why a circular boundary integral, and what it is

`d_rect` integrates a directional derivative along a **straight span**: a real edge sums
coherently (∝L), texture sums incoherently (∝√L). A circle's tangent is straight only over a
short arc, which is exactly why 2 of 20 boundaries cleared.

The round analogue: for a candidate centre (cx,cy) and radius r, sample the **outward radial
derivative** D(φ) = Gx·cosφ + Gy·sinφ around the circle and integrate.

- A round blob brighter than its ground gives D(φ) **negative at every φ** — it sums coherently.
- **A straight edge gives D(φ) = |g|·cos(φ−φ_n), which integrates to ZERO around a full circle.**
  The statistic is *structurally* blind to the failure mode `d_rect` is structurally blind to,
  and that is the whole reason for building it rather than re-tuning the rectangle.

Closure, the part texture cannot fake, is the round analogue of `d_rect`'s min-of-four-sides:
the ring is cut into **8 octants**, each octant's integral is z-scored, and the feature's
closure score is the **minimum octant z of consistent polarity**. Three good octants and five
absent is rejected.

### 1.2 The shape gate, and why the locator alone is not enough

**A filled square is also a compact bright blob and will score on the locator.** That is the
detector-looks-at-the-wrong-things failure (E07 §30, and this lane's control 2: five detections
spanning five of eight octants that were SMD capacitor pads). So every candidate that clears
the locator is passed to a second, independent test: its boundary contour is extracted at
half-max and a circle is fitted with `bin/boardmetro`'s `fit_circle` / `shape_evidence`, whose
**inlier fraction** is the published discriminator (square **0.055**, ring **1.000**).
**Extending `bin/boardmetro`, not forking it**, as instructed.

---

## 2. Quantitative predictions, each with its falsification condition

**P1 — the pad-scale detection limit, measured in the rim itself.** A synthetic **disc** of
1.4 mm diameter pasted into the quietest rim windows (site **swept**, ≥5 sites, E07 §26) will
clear the measured bar at a boundary step of **25–100 luma**.
*FALSIFIED above 160* — the instrument then cannot reach the 166–208 luma the joints are said
to present, and the answer is CANNOT DETERMINE with that number attached.
*ALSO FALSIFIED below 10* — a control that sails through is E07 §4's subtlest defect; a limit
that low means my paste is easier than the photograph and the ladder is not evidence.

**P2 — the rim's own null is harder than a spectrum-matched one.** N3 (identical scan at random
centres and random radii **sampled in the annulus** of the real image) p99 **>** N1
(phase-scrambled, same annulus) p99. *FALSIFIED if N3 p99 ≤ N1 p99* — which would mean the rim
carries no structure beyond its power spectrum, and I would not trust N3 as a bar.
**N3 p99 is the bar. N3 max is reported alongside it.**

**P3 — the shape gate separates, in the real rim, at the limit contrast.** Pasted **disc**
inlier fraction **≥0.85**; pasted **square** of equal area **≤0.30**; separation ratio **≥2.5×**.
*FALSIFIED if the two ranges overlap or the ratio is under 2.5* (E07 §21: a control passes by
being far from the signal, not by squeaking under a bar). On falsification I may report a count
of **"compact bright features"** and must **not** call them round joints.

**P4 — the board's own outer edge does not score.** The locator, centred on the board outline
itself (a locally straight boundary), returns a closure score **below the bar** at ≥90 % of 200
outline positions. *FALSIFIED if the edge scores above the bar* — the detector would then be
following the board edge and every count it produces is worthless. This is the negative control
that can lose, and I will fire it on purpose first (§4).

**P5 — MY OWN BIAS, NAMED IN ADVANCE, WITH ITS DIRECTION: OPTIMISM, biased to COUNT TOO HIGH.**
I have been told the joints are "unmistakable" at 222–242 against 34–56 and that the prior
failure was the *instrument*, not the signal. That framing primes me to believe a matched
instrument must work, to admit marginal detections, and to accept bright non-joint metal —
which is precisely how the earlier lane got five confident detections of SMD capacitor pads.
**Predicted direction: too many, not too few.** Countermeasures, fixed now: the class-X line
(clears the locator, fails the shape gate) is reported as a *number*, not discarded silently;
and §5's draw-and-look is a gate, not a formality.

**P6 — the count does not move with the search.** Across the sweep in §3.3 the count changes by
**≤1**. *If it moves by ≥2 the answer is CANNOT DETERMINE*, per §3.4(d). And, per E07 §24,
**invariance alone settles nothing** — it is paired with P3 (shape) and §5 (draw and look),
which tie the answer to the intended subject.

---

## 3. The bar, the sweep, and the stopping rule

### 3.1 The bar methodology — stated before the bar is measured
Two nulls, no operator choice in either:
- **N1** — `d_rect.phase_scramble` of the same image; identical power spectrum, no coherent
  round structure. Sampled in the annulus.
- **N3** — **the real rim**: identical scan, random centres in the annulus, radii drawn
  uniformly from the same 0.5–1.1 mm grid the real scan uses. **N3 p99 is the bar.**

**The bar is measured at the size of the thing being counted** (1.0–2.2 mm diameter) and at the
rim. The dark packages' 100–160 luma was measured on a 3.2 mm object and **is not reused**.
The rectangle lane's 23.7 / 33.4 side-bars are **not reused** either: different statistic,
different geometry. E07 §22 — a null is only a null with respect to a particular statistic.

**Denominator guard (E07 §25):** any octant whose null sd is not finite and positive, or whose
sampling ring is not fully covered by the validity mask, returns **None and is NAMED
UNMEASURED**. It is never scored 0.0. A candidate with any unmeasured octant is reported in a
separate unmeasured list and is **not counted either way**.

**Mask (E07 §29):** the validity mask is the board dilated **1.5 mm outward**, because a rim
joint straddles the board edge and the eroded mask manufactures an absence.

### 3.2 What must be true before the count is even run
`limit` must show the required step is **below** the available contrast at **≥4 of 5 sites**.
If it is not, no count is run and the answer is CANNOT DETERMINE with the limit attached.

### 3.3 The pre-registered sweep (fixed now, so it cannot be chosen later)
`down` **2 / 3 / 4**; radius grid step **0.05 / 0.10 mm**; angular samples per ring
**64 / 128**; bar taken as **N3 p99** and, separately, **N3 max**; annulus **0.86–1.01** and
**0.84–1.03** of r(θ). The count is reported as its **range over the whole sweep**.

### 3.4 THE STOPPING RULE — decided now, while it costs nothing
Report **CANNOT DETERMINE, with the deciding number attached**, if any of:
- **(a)** the limit ladder needs a step above the available contrast at ≥2 of 5 sites;
- **(b)** P3 falsified — the shape gate cannot separate disc from square in the real rim;
- **(c)** P4 falsified — the board edge scores above the bar;
- **(d)** the count moves by **≥2** across §3.3;
- **(e)** more than **10 %** of annulus area is UNMEASURED;
- **(f)** drawing the detections on the photograph shows **≥1 in 4** are visibly not rim joints.
**A refusal carrying its number is an acceptable and complete outcome and I will not tune to
avoid one.** Equally (E07 §6) I will not refuse when I have actually measured: if the limit is
cleared and the controls hold, I report the count.

### 3.5 Octant spread — a flag, not an automatic refusal
The disjoint-arc tell is applied. But **passing it is necessary and nowhere near sufficient**
(E07 §30) and I will not let ≤3 octants auto-refuse a count either, because I do not know how
the real joints are distributed and inventing a distribution would be assuming the answer. Low
spread is **reported prominently** and forces §5 to carry the verdict.

---

## 4. Breaks I will run on purpose and must WATCH GO RED before trusting anything
Every one has a named expected failure. A check never seen red is not known to work (E07 §27:
and a regression case on an easy synthetic is not a regression case).
1. **A filled SQUARE** of equal area at equal contrast → must **fail the shape gate**.
   Written against a *noise-matched* case, not a clean one.
2. **A straight EDGE** through the ring centre → locator closure must **not** clear the bar.
3. **Zero contrast** (`step = 0`) pasted at every site → **nothing** detected.
4. **Denominator break**: force the null sd to zero and require the tool to **refuse**, not to
   emit 1e11 (E07 §25).
5. **Mask break**: run undilated and require the unmeasured-octant count to **rise and be named**
   rather than scoring 0.0 (E07 §29).
6. **Coverage break**: shrink the annulus below the ring diameter → **CANNOT DETERMINE**, not an
   empty count. An empty count and an impossible search must not print the same thing.
7. **Guard-removal regression**: with the polarity-consistency guard removed, case 2 must pass
   (i.e. the straight edge must then be *accepted*) — otherwise case 2 is not testing the guard.

## 5. DRAW IT AND LOOK — a gate, not a formality
Before any count is reported: every detection, every class-X rejection, every unmeasured
region, and every paste site is rendered onto `oflynn-backside-fullres.jpeg` and **looked at**.
Both of the worst defects in this project today were caught only this way and by no number.
If what is drawn is not what I think I counted, the count does not ship.

## 6. Reporting order, fixed
1. This file, committed **first**, alone.
2. The instrument and its selftest, with the breaks seen red.
3. The nulls, the limit, the count **or the refusal with its number** — committed.
4. **Only then** read `M12 §5`, `M03`, `M05`, `docs/REFERENCE-TEARDOWN.md`, and report the
   comparison as a **separate, later commit**. A disagreement is a result, not an error.
