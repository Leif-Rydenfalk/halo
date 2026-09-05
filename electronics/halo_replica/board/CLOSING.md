# halo Replica — the board, closed

*Lane L5b BOARD BUILD, 2026-09-05. **The side carrying the SoC and the shield can.***
Three sources use "front" for two different faces; the word is not used here.

**The deliverable is `board/out/compare-front.png`** — ours | Apple's | overlay at one
shared 48 px/mm — and, equally, **the list of what is absent and why.** A board that
looks complete when it is not is the one failure this lane could not have recovered from.

---

## 1 · What the Replica is

A parameterised annular board. **One number** — `board.json`
`parameters.outer_diameter_mm.value` — scales the fitted shape, the hole and every
component position together. No diameter is hard-coded in any tool.

Everything is in **one frame**: board centre in `oflynn-backside-fullres.jpeg` at
`origin_px (1522.56, 1738.80)`, `106.313 px/mm`, `+x right, +y DOWN`. Every millimetre
inherits that scale, which came from M02 at the board and was transferred by
`c_register`'s homography.

**Registration in the comparison is by construction, not by alignment.** The photo crop
is taken about the stated origin at the stated scale. Nothing was fitted to make the
panels agree.

---

## 2 · What is measured

| | value | how it is known |
|---|---|---|
| outer outline | circle **D 25.1593 mm** + **4 straight chords** | fit to 1194 measured rays; resid sd **0.2771 mm**, 55.8 % within ±0.15 mm, against a plain circle's 0.5629 mm / 43.6 % |
| centre hole | superellipse + **7 straight facets** — a routed pocket | resid **0.3342 → 0.1987 mm**, earned against a fabrication floor of −0.31 % |
| thickness | **0.30 mm as-drawn** | below PCBWay's and JLCPCB's 0.40 mm floors — **a fact about us, not about Apple** |
| layers | **4, COUNTED** | published delayering; not a Replica choice |
| components | **34 to measured size, 63 as position only** | L1's 100-row handoff, one drawing rule per flag |
| component positions | **4.23× enrichment** over 4000 random annulus positions | X5; collapses to 1.44× under a 12° rotation |
| ours vs Apple's | X1 **0.97 %**, X4 RMS **0.413 mm** over 654 rays | measured off the finished panels |
| where it disagrees | ≤0.15 mm **51 %** of perimeter · 0.15–0.40 mm 26 % · >0.40 mm 12 % · no ray 9 % | X6, **drawn onto the overlay in colour** |

**The outer diameter is a BOUND, 24.95–26.34 mm, and if it moves it moves DOWN.** The
25.1593 mm drawn value is a **shape result** that inherits the same registration scale
as everything else. It is not a fourth opinion on the OD and must never be quoted as one.

**No centre-hole diameter is published.**

---

## 3 · What is refused, and each for a different reason

| refused | reason |
|---|---|
| 3 handoff rows | flagged `do_not_draw_as_component`: 2 merged pad runs (7.30 and 14.48 mm long sides) and D001, an edge-bright strip at 4.1 : 1 that an IC body cannot be |
| rim pads | count **CANNOT DETERMINE and CLOSED**. The withdrawn 15- and 13-pad angle sets failed a positive control |
| the three antennas | **not on this PCB at all** — a moulded carrier. Never in copper |
| the NFC / voice coil | wound magnet wire, not a trace. Which of the two it is remains **OPEN** |
| the U1 footprint | size **CANNOT DETERMINE** — an independent remeasure swings **6.735 → 7.891 mm on operator padding alone**. **U1 is UNPOPULATED and the legend says so ON THE BOARD** |
| copper, traces, vias | not measured |
| part colour sampled from Apple's photograph | it **is** a measurement — and it makes the comparison **circular**. Two panels forced to agree on colour because we copied it |
| a flat across 115–118.5° | it sits on a **13.75° hole in the ray data**. Later re-measurement showed the excursion was largely the detector — the refusal was right |
| the re-extracted whole-circle profile | **more data, not taken.** 1428 rays against 1194, 246 of them new — and the refit was worse (0.4914 vs 0.2771 mm). N4 fired and the tool refused to write it |

---

## 4 · What is absent and named

**The board is knowingly incomplete in the dark regions, and the picture says so.**

- **Every neutral-black IC package, including the largest one.** M08 CANNOT DETERMINE.
- **Two gold-ringed round parts** and **the large silver clip** beside the hole — drawn
  as magenta `?` absence markers from `position_eyeballed_mm`, `measured: false`,
  `do_not_draw_as_measured: true`. All three fields are honoured.
- **The grey rim material.** A large visual feature on Apple's board with no geometry
  behind it — `m_rim_step`'s verdict is CANNOT DETERMINE.

**Nothing in these gaps was filled by eye.** An eyeballed position among measured ones
is invisible in a render, which is exactly why it must not happen.

---

## 5 · The five open gaps, each with what would close it

1. **The 82.75–101.0° outward excursion is REAL** — a second independent extractor moves
   it only 0.119 mm — and the model has no feature there. **Board, or the grey rim
   material lapping over it, and this lane cannot separate them.** *Would close it:* a
   source that images the rim in section, or an X-ray. Optical cannot do it.
2. **The dark packages are a METHOD gap, not a source gap.** A link-only source with
   **1.9× more genuine resolution** was measured and the packages still do not separate
   by luma (61, 73 against a soldermask range 52–145) or texture (9.94, 4.22 against
   5.17–14.59) — but they are **unmistakable to the eye** by their straight boundaries.
   *Would close it:* a boundary-based detector — line detection and rectangle assembly —
   with the same sweep-stability admission rule, plus **mirror-aware** registration,
   since that source is flipped and carries no scale of its own.
3. **The hole facet side walls are not measured.** Each facet ends in a radial step at
   the ±0.30 mm crossing, which is the right *kind* of geometry for a pocket wall but is
   not where the wall is. *Would close it:* a perpendicular-edge detector.
4. **The pocket hypothesis is neither established nor refuted.** Two nulls, the second
   from a pre-registered test that **my own negative control showed had almost no power**
   — chance scores 2.61 of a possible 3. *Would close it:* the properly powered design
   in `HANDOFF.md`, pre-registered before extraction.
5. **D004 is a candidate 15th rim-suspect** — a blue-body row outside the fitted outline
   that L1's bright-row-only test could never have flagged. Reported, never drawn as a
   confirmed part, and unchased.

---

## 6 · The lane's own defects, kept because the fix is the lesson

**Nine, and every one was found by a control rather than by inspection.**

1. **R3 fired at 1.42 % on a correct render** — it averaged over chorded arcs, comparing
   a chord-shortened mean against a circle diameter.
2. **X3 never reached X4.** Panel 1 is rendered by a subprocess that knows nothing about
   the break, so X4 sat unchanged at 0.413 mm under a 12° rotation. *A control severed
   from its subject by a process boundary.*
3. **R5 could not fire** — `--break-drop` truncated the input rows, so the accounting
   identity balanced.
4. **H3 returned −3836 %, then −221 %.** The first was a broken synthetic generator. The
   second was **not** the control failing: it exposed near-tangential facets whose
   `d/cos(θ−n)` diverges inside their own arc.
5. **The H3 EARNED test inverted on a negative floor** — `gain > 2 × floor` passes on any
   positive gain once the floor goes below zero, because multiplying by a negative flips
   the inequality. *A threshold that silently inverts.*
6. **The near-tangential guard went into the hole facets and not the outer chords.**
   Latent, not active — it changed nothing on the published profile, which is why nothing
   went red until a second profile was fitted. *A fix applied in one place and not the
   other. Latent defects are the ones that survive.*
7. **E2 caught the gradient-peak estimator at 4.21 px of bias** — 40 µm, larger than the
   thing being measured, because a boxcar smoother turns a step into a ramp.
8. **E1's first version straddled the centre hole** and fired 72 of 72 — **correctly.**
   It was shown genuine background and asked to find nothing. *The control was wrong,
   not the finder.*
9. **The pre-registered pocket statistic was saturated before either photograph was
   touched.** Fixing the procedure honestly did not make the procedure able to
   discriminate.

**And one judgement corrected without a test:** L1's *three* disagreeing hole exponents
are **two**. n = 2.00 (pinned) and n = 2.449 come from the same photograph and the same
boundary points. Routed to L1, not edited.

---

## 7 · What would have to be true for this to be wrong

Every millimetre here rests on **one scale**, transferred from FCC photo 6 by a
homography fitted on 80 interior landmarks (NCC 0.6861 against a null-control max of
0.2027). **If that scale is wrong, everything scales with it** — which is why the board
is parameterised by one number and why the OD is published as a bound with a signed
direction rather than as a figure.

The strongest thing that is *not* scale-dependent: **two independent edge extractors,
never tuned to each other, agree to a median 0.0158 mm across 1182 shared rays.**

---

## 8 · Reproduce it

```bash
python3 tools/p_fit.py --selftest                 # and --selftest-break N1|N1b|N2
python3 tools/p_fit.py --px-per-mm 106.31295578013115 \
  --scale-basis "M02 m_scale_at photo6 at the board, transferred by c_register"
python3 tools/p_render.py                        # and --break-scale 1.10, --break-drop 5
python3 tools/p_compare.py && open board/out/compare-front.png   # and --break-rotation 12
```

Every one of those breaks has been watched going red. `board/HANDOFF.md` carries the
control table, the numbers with their inputs, and the next lane's first three jobs.
