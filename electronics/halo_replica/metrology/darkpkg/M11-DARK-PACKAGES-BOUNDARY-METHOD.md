# M11 — the dark packages by BOUNDARY evidence: the method, and the limit that closes it

*halo Replica, L7 DARK-PACKAGE DETECTOR lane, 2026-09-05.*
*SIDE NAMING: the side carrying the SoC and the shield can. O'Flynn's
`oflynn-backside-fullres.jpeg` IS that side.*

**Reproduce:** `bin/boardmetro rect-selftest` (10 cases, exit 0) then
`tools/d_darkpkg.py probe --down 3` and `tools/d_darkpkg.py limit --down 3`.
The handoff is generated, never typed: `tools/d_handoff.py`.

---

## 0. The one-line result

**This photograph needs a boundary step of about 120 luma before 3 of a package's
4 sides become exceptional among the board's own straight structures. The
packages present 1–26 luma on most of their sides. So the black packages are
CANNOT DETERMINE — not "we could not see them", but *at the boundary contrast
they actually present, they could not have been seen by any boundary method on
this source.***

No position and no size is published. Five dark bodies are named and absent.

## 1. Why a boundary method, and why it was worth the attempt

M08 ruled out intensity four ways and M10 confirmed it on an independent source
with **1.9× more genuine resolution**, where the packages' luma (61, 73) sits
*inside* bare soldermask's range (52–145) and their local-sd (9.94, 4.22) sits
*inside* soldermask's (5.17–14.59). M10's named next step was a boundary method,
because straight edges and right-angled corners are what the eye seems to use.

The statistic has a real physical basis rather than a heuristic one:

> **A straight edge integrates the directional derivative COHERENTLY along its
> length — the sum grows like L. Unaligned texture of the same local contrast
> sums INCOHERENTLY — it grows like √L.** So the discriminator is a line integral
> against the null distribution of that same integral. **No absolute intensity,
> no colour and no texture threshold appears anywhere in it.**

The null is **empirical, not assumed**: √L is only true for white noise and this
is a JPEG, so the null is built by rolling **each row of the gradient field
independently** — identical per-row statistics, identical along-row correlation,
only the alignment *between* rows destroyed. That is the fix `E07 sec.2` records
for L1's rim-pad control, which permuted the wrong thing twice.

## 2. The finding that killed closure, and it is a measurement

The first design required **four** supported sides with **consistent polarity** —
a closed rectangle. It is refuted on this board.

Perpendicular luma profiles across the nRF52832's visible outline, 41 samples
averaged along each side:

| side | interior | exterior | step |
|---|---|---|---|
| left | ~90 | ~22 | **−75 luma** |
| right | ~41 | ~31 | −10 |
| top | ~66 | ~74 | +8 |
| bottom | 36 | 37 | **+1 — no boundary at all** |

**The interior luma runs 90 / 41 / 66 / 36 around a single 3 mm package.** The
illumination gradient across one part is larger than most of its boundary steps,
so the surround is brighter on one side and darker on another and a
consistent-polarity test is contradicted by the data. A four-side requirement
cannot recover a part whose fourth side is not in the image.

### The stable wrong answer, which is the more important half

Asked for the best *closed* rectangle near the nRF, the detector returns an inner
rectangle of **2.45 × 2.18 mm, score 18.8 — stable to −26 % across downsample
2/3/4, band width 1/2/3 and peak count 30/40/60.** An exhaustive local search
with the peak-picking stage removed entirely (`d_rect.score_grid`) confirms it is
not a proposal failure: no rectangle at the published 3.226 × 2.956 mm has four
supported sides anywhere within ±42 stored px.

> **This project has used parameter-invariance as its defence against "the answer
> is the box", because that failure showed a 34 % swing on ROI padding alone.
> A wrong answer that is a genuine feature of the image is stable *precisely
> because it is genuinely there*. Sweep-stability rules out one failure mode and
> establishes nothing on its own.** It is not published.

## 3. So each side is fitted, and judged, on its own

`d_rect.fit_sides` scans each of the four boundaries independently and reports
each one's own |z|. A **dimension exists only when BOTH sides of its axis are
supported**; otherwise the row is position-only, and with no supported side, absent.
That lands on the located-not-sized distinction `HANDOFF-positions-front.json`
already carries on 63 of its 100 rows.

### Two nulls, and the second is the one that decides

| null | what it asks | |z| p50 | p90 | p99 | max |
|---|---|---|---|---|---|
| **N1** phase-scrambled board | does the boundary beat texture of the *same power spectrum*? | 9.2 | 14.5 | 17.8 | 20.0 |
| **N3** real board, random place, random angle | is the boundary **exceptional among the straight structures this board already has** — traces, pad rows, silkscreen, the rim? | 7.0 | 19.1 | **33.4** | 45.4 |

N1 has no operator in it (identical spectrum, no straight edge survives) and N3
has none either (random locations, random angles). **N3 is the bar**, because a
detector's job is to pick packages out of everything else on the board.

## 4. What the five dark bodies actually carry

Bar = N3 p99 = **33.4**. Steps are measured at the eyeballed seed outline, per side.

| body | \|z\| L / R / T / B | sides clearing | step luma L / R / T / B |
|---|---|---|---|
| nRF52832-CIAA *(control)* | **37.2** / 15.4 / 9.2 / 13.5 | **1 of 4** | −75 / −10 / +8 / +1 |
| black package at 9 o'clock | 3.3 / 5.4 / 6.7 / 10.0 | 0 of 4 | −3 / −5 / +1 / −8 |
| "+AKN 8H7" | 6.1 / 8.3 / 8.2 / 8.4 | 0 of 4 | +5 / +2 / +18 / +20 |
| "05I 1A8" | 12.4 / 10.8 / 3.5 / 6.5 | 0 of 4 | +145 / 0 / +26 / +5 |
| black diode-like body | 5.4 / 1.5 / 2.0 / 10.2 | 0 of 4 | +5 / +1 / +6 / +2 |

**1 supported boundary out of 20 examined.** The one that clears is the nRF's,
and it clears the 99th percentile but **not** the null's maximum (45.4) — one
boundary is a line, not a position, and a line at the 99th percentile of the
board's own straight structures is not a datum. Nothing is published from it.

### The nRF's own agreement with its datasheet, and why it is not used

The per-side fit, seeded from a 3 × 3 grid of start points, gives **3.076 ×
2.878 mm** (spread 0.226 / 0.282 mm, centre wandering 0.242 mm) against a
published 3.226 × 2.956 — **−4.6 % / −2.6 %**. That is close, and it is **not**
admitted, because only one of the four boundaries clears the bar. *Its agreement
with the datasheet is not a reason to believe it*: admitting it for that reason
is a control agreeing with itself, which is the defect this project keeps
catching.

## 5. The limit, which is what turns a refusal into an answer

`E07 sec.4`: a synthetic control cleaner than the photograph is not evidence —
L1's synthetic rim came out **19× cleaner** than the image it stood in for. So
this control is made **of** the photograph: a 3.226 × 2.956 mm rectangle of known
boundary step, pasted at **the quietest 4.2 mm window that lies wholly on the
board, chosen by the code and not by me** (1188, 2697 stored px).

| pasted step | \|z\| L / R / T / B | sides clearing | recovered size |
|---|---|---|---|
| 160 luma | 44.4 / 43.3 / 54.0 / 39.5 | **4 of 4** | **3.217 × 2.963 mm** (−0.3 % / +0.2 %) |
| 120 | 35.6 / 34.5 / 42.5 / 27.6 | 3 of 4 | 3.245 × 2.963 |
| 80 | 24.4 / 23.6 / 29.2 / 26.5 | 0 of 4 | 3.048 × 2.963 |
| 60 | 17.9 / 17.3 / 26.0 / 26.7 | 0 of 4 | 3.386 × 2.963 |
| 45 | 13.7 / 13.2 / 26.1 / 26.8 | 0 of 4 | 3.386 × 2.963 |
| 25 | 8.0 / 7.6 / 26.1 / 26.8 | 0 of 4 | 3.386 × 2.935 |
| 8 | 3.1 / 2.7 / 25.9 / 26.7 | 0 of 4 | 3.386 × 2.963 |

**The method works — at 160 luma it recovers the size to 0.3 %.** It is the
photograph that does not reach: **~120 luma for 3 sides, ~160 for 4**, against
the **1–26 luma** the real packages present on most of their sides and the 75
luma the nRF reaches on its best one.

*(The top and bottom |z| plateau at ~26 even at 8 luma: those two scans latch
onto pre-existing board structure at the paste site, which is exactly the effect
N3 is measuring and is the reason N3 is the bar.)*

## 6. What was discarded, and why

| tried | outcome |
|---|---|
| four-side closure with consistent polarity | **REJECTED** — refuted by the per-side luma profiles in §2 |
| taking the best closed rectangle anyway | **REJECTED** — a stable −26 % wrong answer, §2 |
| a polarity filter (dark-inside) | **REJECTED** — the nRF is *brighter* than its surround on one side and darker on another; polarity is reported, never required |
| high-passing the gradient field to kill illumination ramps (`hp` 15/25/41) | **NO HELP** — N3 fell only 33 → 29, the nRF's best side fell 21 → 17. Kept in the engine as an option, off by default, with the measurement recorded |
| a hand-picked patch of bare soldermask as the bar | **REJECTED before it was run** — picking an easy patch sets the bar low and admits junk, which is M08 attempt 3 in a new costume. Both nulls are operator-free |
| N1 (phase scramble) as the bar | **kept, but not decisive** — it asks the easier question |
| `--down 4` as the working resolution | kept for the whole-board pass; `--down 3` (35.4 px/mm, above the 20–27 genuine band) for the per-side work |

## 7. The instruments, and the four checks watched failing

`tools/d_rect.py` (engine) · `tools/d_darkpkg.py` (bar / control / probe / limit) ·
`tools/d_handoff.py` (generator) · `bin/boardmetro rect` and `rect-selftest`
(extended, not forked).

`bin/boardmetro rect` **refuses to invent a threshold**: with no `--bar` it exits
2 and tells you to run `--null` on the same image first.

Selftest: 10 cases, all green. **Four were watched going red on purpose:**

| break | case that must fail | it did |
|---|---|---|
| undo the null-sd mask fix | 6 | `sd = 0.0000` |
| make `maximal()` a no-op | 8 | `3 of 3 kept` |
| remove the side-crossing bound | 7 | `3.423 × 0.000 mm` |
| score = MAX of four sides instead of MIN | 2 | null 112.5 against a real 62.1 |

### Two engine defects, both found by pointing a diagnostic at a known answer

1. **A single-column line integral** loses a boundary blurred over 2–4 px that
   drifts ~1 px along a long side at a 2° angle step, so a short high-contrast
   marking stroke outscores a long package edge. Now a **band**, with the null
   measured through the same band.
2. **`_null_sd_table` took its robust sd over spans lying off the board**, where
   the derivative is identically zero. **Past 50 % zeros the MAD is ZERO, every
   z-score goes to infinity, and every rectangle scores the same.** It produced
   z ≈ 1e11. *That is not a check that fails; it is a check that **saturates**,
   and a saturated check reports maximum confidence in everything.* Selftest
   case 6 is its regression.

### And a check of mine that could not fail

Selftest case 7 (the side-crossing regression) originally used the clean
four-edged synthetic. Removing the bound it was written to protect **changed
nothing** — on a clean synthetic the sides never have a reason to wander. It was
rebuilt on a `onesided` synthetic that reproduces the nRF's real situation (one
strong boundary, three nearly absent), and only then did removing the bound
produce `3.423 × 0.000 mm`. **A regression test written against an easy case is
not a regression test.**

## 8. Status

| # | quantity | verdict |
|---|---|---|
| 1 | boundary method works in principle | **PASS** — recovers 3.217 × 2.963 mm against a true 3.226 × 2.956 at 160 luma |
| 2 | four-side closure on this board | **REFUTED** by per-side luma profiles |
| 3 | positions of the neutral-black packages | **CANNOT DETERMINE** — 0 of 16 boundaries supported |
| 4 | nRF52832 position and size by this route | **CANNOT DETERMINE** — 1 of 4 boundaries, and that one clears p99 but not the null maximum |
| 5 | the boundary step this photograph needs | **MEASURED** — ~120 luma for 3 sides, ~160 for 4 |
| 6 | the step the packages present | **MEASURED** — 1–26 luma on most sides; 75 on the nRF's best |
| 7 | what would close it | **NAMED** — boundary *contrast*, not resolution: raking illumination, or X-ray / die-level imagery. M10 already showed 1.9× more resolution does not do it |
