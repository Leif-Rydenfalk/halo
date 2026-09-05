# M03 — the rim solder pads: COUNT NOT ESTABLISHED, and why

*halo Replica, L1 PHOTOGRAPH METROLOGY lane, 2026-09-05.*

**SIDE NAMING:** FRONT = the COMPONENT side, per Apple's FCC caption
("A2187 MLB - Front"). O'Flynn's "frontside" is this project's BACK. See M02.

**Sources:** `fcc-BCGA2187-internal-photo-6.jpg` (FRONT) and `-7.jpg` (BACK),
FCC ID BCGA2187 internal photos, a public regulatory filing, watermarked
*"Apple Proprietary and Confidential"* and cited as the filing.

**Reproduce:**

```
tools/m_rim_pads.py --image fcc-BCGA2187-internal-photo-6.jpg \
    --centre 953.04,678.39 --profile metrology/outline-raw-photo6.json \
    --px-per-mm 15.685 --max-span-mm 2.5 --json metrology/rim-pads-photo6.json
tools/m_pad_registration.py --front metrology/rim-pads-photo6.json \
    --back metrology/rim-pads-photo7.json --json metrology/pad-registration.json
```

---

## The question

`docs/REFERENCE-TEARDOWN.md` says **six** tear-off joints hold the antenna
carrier to the board's rim. Nobody in this project has counted them — the
number is inherited. A count is a check that can fail, so it was worth doing.

## VERDICT: CANNOT DETERMINE — and the dossier's "six" is neither confirmed nor refuted

**Nothing here contradicts six.** What is established is that **these two
photographs cannot settle it**, and exactly why.

---

## 1. What the single-image detector finds, and why it is not published

`m_rim_pads.py` resamples the rim into (angle × radius-fraction) with the radius
normalised to the **measured** `r(θ)` — a constant-radius ring is wrong, because
the board's apparent radius varies ~5 % with angle (M02 §3) and such a ring
drifts on and off the board. It then labels bright connected blobs and separates
an edge pad from a nearby component by **how far out the blob reaches**, as a
fraction of the local edge radius.

| | FRONT (photo 6) | BACK (photo 7) |
|---|---|---|
| bright blobs in the annulus | 64 | 26 |
| reaching ≥ 0.975 of the edge | 26 | 15 |
| …and ≤ 2.5 mm of arc (pad-sized) | **15** | **13** |
| **CONTROL: rows rolled independently** | **mean 19.5, max 24** | **mean 23.0, max 31** |

**The control beats the measurement in both photographs.** At 0.218 mm per
degree of rim arc, chance alignment of the same brightness statistics produces
as many edge-reaching blobs as the board does. **The counts 15 and 13 are
therefore NOT published as counts**, and no threshold was moved to make them
pass.

Feature angles are on disk regardless (`rim-pads-photo6.json`,
`rim-pads-photo7.json`) — as candidates, labelled as such — because L5 asked for
positions. **They must not be drawn as pads.**

## 2. The stronger test, which also fails — and its failure is informative

An edge-plated pad or a tear-off stub goes **through** the board, so it must
appear at the same angular position on the FRONT and on the BACK. A surface
component appears on one side only. The board is flipped between the two
photographs, so angles mirror: `θ_back = (axis − θ_front) mod 360`, axis unknown
and therefore searched.

**The search maximises over 720 alignments, so the null must contain the same
optimism.** It does: the back angles are replaced by uniform random angles and
the identical search is re-run, 2000 times.

| | |
|---|---|
| best alignment | axis 24.5°, **8 of 13** possible features agree |
| null (same search, random angles) | mean **7.45**, p99 9, max 10 |
| **p(null ≥ 8)** | **0.4295** |

**Eight matches is what this search finds against noise.** This does *not* show
the two sides disagree — it shows these photographs cannot register them.

A detail worth recording: the FRONT candidates cluster at 147–199° and the BACK
candidates at 210–308°. Two views of one board should not put their features in
disjoint arcs. That asymmetry is consistent with the detector responding to
per-photograph illumination rather than to board features, and it is a second,
independent reason not to publish either count.

---

## 3. WHAT I DISCARDED — two controls I built WRONG, both caught by watching them

This is the substance of the section. Neither error would have been visible in
the output; both were found by asking what the control was actually doing.

1. **`m_rim_unwrap.py` permuted the SMOOTHED signal.** The real signal is
   smoothed over 1.5° before peak finding; the control permuted it *after*
   smoothing, so the control was jagged where the real signal was smooth. The
   finder invented ~22 peaks from it and **nothing could ever have beaten it.**
   Fixed: permute the RAW columns, then smooth exactly as the real signal was
   smoothed — same histogram, same pipeline, no features.

2. **`m_rim_pads.py` permuted the angular COLUMNS**, which is broken for a
   *"reaches the edge"* criterion: a permuted column is a **full-height stripe**,
   every full-height stripe trivially reaches the edge, so **the control
   manufactured the very property under test** and returned 46.8 features
   against a real 26. Fixed: roll each radius row independently — same pixels,
   same per-row runs, and only the **radial alignment** that makes a pad a pad
   is destroyed.

   With the broken control the answer was still CANNOT DETERMINE, so the
   *verdict* did not change. **The reasoning behind it was worthless, and a
   right answer reached through a control that cannot fail is not a measurement.**

3. **A resolution limit, stated rather than worked around.** The first attempt
   unwrapped the rim into a strip to be counted by eye. The rim band is ~27 px
   deep and the strip is mush. These JPEGs are 150 dpi renders of the FCC PDF;
   at ~15.4 px/mm a 1 mm tear-off tab is ~15 px across a soft, JPEG-blocked edge.

---

## 4. What WOULD settle it

- **Re-render the FCC exhibit at 600 dpi.** `images/airtag/CATALOG.md` records
  that these eight JPEGs were rendered from `A2187_Internal_Photos_v1.0`
  (doc 5130978) **at 150 dpi**. Four times the linear resolution puts a 1 mm tab
  at ~60 px. The source PDF is **not** in this repo — only the derived JPEGs are
  — although the equivalent PDFs for six competitor trackers are, under
  `images/commercial/`, so this is an established action in this project rather
  than a new one. **Not done here: it needs a network fetch, and that is the
  orchestrator's call, not mine.** This is the single highest-value unblocking
  step for the whole rim question.
- A caliper or a microscope on a real bare MLB.
- An edge-on photograph, which would also give the board thickness — no
  photograph in this set shows the board edge-on.

---

## 5. Status

| # | quantity | verdict |
|---|---|---|
| 1 | number of rim tear-off / edge pads | **CANNOT DETERMINE** — both single-image counts lose to their own controls |
| 2 | whether FRONT and BACK agree on rim feature positions | **CANNOT DETERMINE** — 8 matches, p = 0.43 against the identical search on random angles |
| 3 | the dossier's "six" | **neither confirmed nor refuted.** Do not cite this file as either |
| 4 | candidate angular positions | on disk, **labelled candidates**, not to be drawn as pads |
| 5 | board thickness | **NOT MEASURABLE** — no edge-on photograph exists in the set |
