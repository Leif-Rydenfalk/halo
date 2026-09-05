# R02 — THE BLIND RIM COUNT: **CANNOT DETERMINE**, with four deciding numbers

*halo Replica, lane L10, 2026-09-05. Committed **before** reading `M12 §5`, `M03`, `M05`,
`docs/REFERENCE-TEARDOWN.md` or anything else outside the protocol's allow-list. Predictions in
`R00`, amended in `R01`, both committed before any pixel of the rim was extracted.*

---

## THE ANSWER

**How many tear-off joints attach the antenna carrier to the board rim?**

## **CANNOT DETERMINE.**

**And it is a different refusal from the two before it.** M05 closed this on **signal-to-noise**.
M12 closed it on **instrument mismatch** — a rectangle fitted to a round thing. Neither holds now:

- **the instrument is matched** — a circular boundary integral, structurally zero on a straight
  edge, and the board's own outer edge scores **p50 −0.11, max 0.83** against a pasted disc's
  **5.9** (P4, 200 outline positions, 100 % below the bar);
- **and it is sensitive enough by a factor of 2.4–26×** — a 1.4 mm round feature clears the bar
  at **8–70 luma** at **10 of 10** rim sites, against the **166–208 luma** the joints present.

**The limit is not the photograph's noise and is not the detector's shape model. It is that the
rim is populated with round bright things that are not joints, and no shape statistic available
on this source separates them from joints.** That is a third, new reason, and it names what
would close the question.

---

## The four numbers that decide it, against the stopping rule fixed in `R00 §3.4`

### 1 · Stopping rule (f) — **13 of 15 detections are visibly not joints.** Threshold: 1 in 4.
Every detection rendered at native resolution and looked at (`out/detections-tiles.png`):

| # | closure | what it actually is |
|---|---|---|
| 1, 2, 3 | **23.2, 9.8, 7.9** | **GOLD ANNULAR PADS** — and they are the three highest scores by a wide margin |
| 5, 9, 12, 14 | 2.1, 1.6, 1.5, 1.5 | **SMD capacitor pads** — the exact wrong-object class of E07 §30 |
| 7, 10, 11, 15 | 1.9, 1.6, 1.6, 1.5 | **grey rim gasket texture** |
| 13 | 1.5 | a 2.0 mm circle spanning two unrelated features |
| 4 | 2.4 | clipping the edge of another gold ring |
| **6, 8** | 2.1, 1.7 | **the only two plausibly solder joints** — and they are near the bottom of the list |

**The instrument is working exactly as designed. It finds the roundest features on the board, and
the roundest features on this board are gold ring pads.** A perfect detector for the morphology I
registered returns predominantly the wrong objects, because the morphology is not unique to the
subject.

### 2 · Stopping rule (d) — **the count moves from 85 to 3 across the pre-registered sweep.**

| bar → | **0.63**<br>N3 p99 | **1.42**<br>N1 p99 | **2.03**<br>N3 max | **2.57**<br>N1 max | 4.0 | 7.0 |
|---|---|---|---|---|---|---|
| down 2, nφ 64 | 66 | 9 | 3 | 3 | **3** | **3** |
| down 3, nφ 64 | 62 | 15 | 6 | 3 | **3** | **3** |
| down 3, nφ 128 | 85 | 29 | 15 | 7 | **3** | **3** |
| down 4, nφ 64 | 66 | 17 | 9 | 6 | **3** | **3** |

Registered condition was **≥2**. Measured: **9–29 at the primary bar alone.**

> **AND THE COLUMN THAT MATTERS IS THE STABLE ONE.** At bar ≥4.0 **every configuration returns
> exactly 3**, invariant across downsample, ring sampling and bar. **Those three are the gold
> annular pads.** This is control 3 of my brief and E07 §24 realised in full: *a stable answer can
> be a stable WRONG answer.* Perfect sweep-invariance, and it is the wrong objects. Had I reported
> the invariant number I would have reported **3** with a clean-looking stability table behind it.

### 3 · Stopping rule (b) — **no shape gate separates, at any setting.**
- **P3 as pre-registered (circle-fit inlier fraction) FALSIFIED on synthetic ground truth**: filled
  disc vs equal-area filled square, best ratio **1.45×** against a required 2.5×, square never
  below 0.37, across IRLS band 1.5–8.0 px and smoothing σ 0–5. `boardmetro`'s published
  **0.055 / 1.000** is an **outline** result and does not transfer to filled blobs (`R01 §1`;
  fixed in `bin/boardmetro`'s own selftest, case 10).
- **The replacement (non-circular energy of the half-max radius profile) FALSIFIED in the real
  rim**: σ 2/3/4/6 × three surround annuli = **12 settings, none separates**. Ratio **1.10–1.63×**
  against a required 2.0×; disc p90 **0.256–0.301** always above square p10 **0.097–0.109**.
- It separates cleanly on synthetic (disc 0.033, square 0.104, rect 2:1 0.276 — **3.2× and 8.4×**).
  **The rim destroys it**: a 1.4 mm feature's radius profile is contaminated by neighbours 1–2 mm
  away, and the rim is that crowded.

### 4 · Not a stopping-rule item but it decides the class label
The **locator** rejects a 2:1 rectangle **outright** — median closure **≈0.0** (and negative at 70
and 120 luma) against a disc's **5.6**. So the elongated-pad class is excluded *by construction*.
It does **not** separate a disc from an **equal-area square**: median ratio **2.29 / 2.44 / 2.79×**
at 200 / 120 / 70 luma, with **overlapping distributions** (disc p10 3.36 < square p90 3.69).

---

## The predictions, scored

| | prediction | outcome |
|---|---|---|
| **P1** | limit 25–100 luma; falsified above 160 **and** below 10 | **HOLDS on the site-worst limit (70).** The site-best (8) is below the "too easy" boundary — and it is the **one site of ten where the ring-sd floor binds at every ladder step**, i.e. where the guard rather than the image sets the denominator. Reported, not averaged away. |
| **P2** | N3 (real rim) p99 > N1 (scramble) p99 | **FALSIFIED. 0.63 vs 1.42 — ratio 0.44×.** The real rim is a *weaker* null than a spectrum-matched one for this statistic, because the rim is dominated by **edges** and a straight edge integrates to zero around a circle with alternating octant signs. **I took the stricter bar (1.42), never the one my own prediction pointed at.** |
| **P3** | inlier fraction separates ≥2.5× | **FALSIFIED** (above). Replacement also falsified. |
| **P4** | the board's own outer edge must not score | **HOLDS.** 200 outline positions: p50 **−0.11**, p90 0.03, p99 0.33, **max 0.83**; 100 % below every bar tested; 0 unmeasured. |
| **P5** | **my bias: optimism, biased to COUNT TOO HIGH** | **CORRECT, and it is the reason this report exists.** At the primary bar I had 15 detections and every temptation to call them joints; 13 were not. The bias landed exactly where I said it would — admitting bright non-joint metal — and the countermeasure I registered against it (draw and look) is the only thing that caught it. |
| **P6** | count invariant to ≤1 across the sweep | **FALSIFIED**, 85→3. |

**A prediction that could only be confirmed would have told me nothing here. Four of six were
falsified and the falsifications carry the result.**

---

## What was measured and stands, regardless of the refusal

- **The frame.** `m_dark_packages.board_frame()` is unimportable in this sanitised worktree
  (`c_register`, `m_components` were removed); recovering them is forbidden, so `tools/r_frame.py`
  rebuilds the transform from the two permitted JSONs and verifies it: scale **+0.085 %** against
  the stored 106.313 px/mm, outline diameter **24.960 mm**, with a deliberate break that reddens
  all three checks.
- **The bar**, at the size counted and at the rim: N1 p99 **1.42**, N1 max **2.57**, N3 p99
  **0.63**, N3 max **2.03**. Ring-sd floor **3.041** luma/px at down 3 (p5 of 600 draws, 600/600
  measurable). Nothing borrowed from the 3.2 mm dark-package work.
- **Coverage: 0.00 % of the annulus is UNMEASURED** (0 of 156 768 positions), with the board mask
  dilated 1.5 mm outward. **1.95 %** of the annulus is bright background connected to outside the
  outline — the documented 2–4 o'clock overshoot — **labelled, never deleted**, because a rim
  joint straddles the edge and a flood mask would swallow it silently.
- **The ladder**, PSF-blurred to the source's own 4.42 stored-px resolution cell and clipped to 8
  bits, at 10 **measurably empty** rim sites (unpasted closure −0.45 to +0.25) across two swept
  site selections: clears at **8–70 luma**, 10/10.

## What I discarded, and why

- **A hard-edged, unclipped paste.** It gave a core of **333 luma**, which no photograph can hold,
  and cleared at 8 luma everywhere. Discarded as a positive control easier than the source.
- **`step_to_clear` = the lowest clearing step.** With **6 of 10** ladders non-monotonic it read as
  high sensitivity while the ladder said the detector failed at higher contrast. Replaced by *the
  lowest step above which every higher step also clears*, and non-monotonicity is printed.
- **The quiet-window site criterion, unqualified.** It selects **background**, because background
  is smooth. Sites must now be on board material **and measurably empty**.
- **The whole-board survey's 40 maxima.** The closure landscape is a continuum from 21.2 to 1.9
  with detections at r **7.3–12.9 mm**, i.e. no separation between the annulus and the rest of the
  board. It is reported as a diagnostic and no count is drawn from it.
- **A shape gate tuned to pass.** Twelve settings were swept against a criterion fixed in advance;
  none met it; none was adopted.
- **The invariant 3.** The most publishable number I produced, and it is three gold ring pads.

## Three defects I put into my own instrument, each caught only by the thing E07 says catches it

1. **`r_frame` check 3 could not fail.** "Mapped centre within two board radii of the seed" passed
   a **179 px** displacement. I wrote it after reading E07 §9. The picture caught what all three of
   my checks missed — and the picture also showed the frame was *right* and my ray-cast fit was the
   wrong one, so the check being useless and the frame being sound were separate facts.
2. **`R00` break 7 was not a regression test.** Removing the polarity guard left the straight edge
   **rejected** (0.48 vs a 0.64 null p99) — the edge dies to the structural zero and to closure, so
   it tested neither guard. Rebuilt on a **bipolar** feature: guard on **−1.20** rejected, guard off
   **1.64** accepted.
3. **Selftest case 13 took three tries, and the third is the worst family in E07.** v1: backdrop on
   35 % of the surround — **0.0325 → 0.0325**, no movement, because a *median* is robust until the
   backdrop is the majority. v2: white backdrop on 65 % — **both** versions refused, for different
   correct reasons. v3: a **mid-grey** backdrop covering feature and surround makes the
   un-excluded profile return **noncirc = 0.0000 — a perfect roundness score from a destroyed
   measurement** (E07 §7: a failure mode indistinguishable from the ideal result). The excluded one
   refuses.

## What would close it — in priority order, and the first is cheap

1. **Separate a filled bright dome from a flat gold annulus by POLARITY, not by shape.** Gold ring
   pads are **annular** — bright ring, dark centre — and solder joints are **filled**. A
   core-versus-mid-annulus polarity test is a one-parameter measurement that would have removed
   the three highest-scoring confusers here. **I did not add it**, because I discovered the confuser
   class *from the result*, and a filter chosen downstream of the answer is E07 §17. It must be
   registered, given a control, and run by someone who has not seen this list — or run here and
   reported as a *second* pass, labelled as such.
2. **A raking-light photograph.** A solder joint is a **dome**; a gold pad is **flat**. Every source
   this project holds is flat-lit, and flat lighting destroys height — the one property that makes
   the two trivially separable. This is the same conclusion the dark-package work reached from the
   opposite end of the board, arrived at independently here, which is the kind of agreement worth
   having: the two analyses share no method and could have disagreed.
3. **An instrument matched to an irregular saturated dome**, which is what the candidate joints
   actually look like — **not** the clean circular blob my `R00` registered. That mis-registration
   is itself a scored result: I predicted the morphology and the morphology is wrong.

## Contamination disclosure, as pre-committed in `R00 §0`

The numbers **22** and **26** appear in the permitted `E07 §2` in a rim-counting context and I
recorded before measuring that I had seen them. **My count is not 22 and not 26.** The only
sweep-stable number I produced is **3**, and I am reporting it as *wrong* rather than as an answer.
I did not read any forbidden file, did not `git checkout` anything, and did not open the main
repository. `git log` on `rimblind-99cab5fe` carries the ordering: predictions, then amendment,
then instrument, then measurement, then this.
