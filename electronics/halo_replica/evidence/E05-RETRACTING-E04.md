# E05 — retracting E04. The board is **not** smaller than 26 mm, and I made the exact error I had been warning about

*halo Replica lane (orchestrator), 2026-09-05. Supersedes `E04-HOW-BIG-IS-THE-BOARD.md`.*

**E04 concluded "about 25 mm, not 26". That conclusion is WITHDRAWN.** Lane L1 retracted its
own 24.6 mm and, in doing so, dismantled mine. The bare MLB outer diameter is **bounded
24.95 – 26.34 mm**, and **O'Flynn's "~26 mm" is not contradicted by anything.**

## The single fact that breaks E04

**The two image axes do not share a scale.** FCC-6's bottom rule gives 15.8875 px/mm and its
right rule 15.5651 px/mm — and L1 has now shown that is not noise: local tick pitch varies
0.67–1.72 % along the bottom rules and 2.47–4.70 % along the right ones, with the right rule
*always* lower, in every photograph.

So a diameter must be measured as **width ÷ x-scale** and **height ÷ y-scale**, separately.
Do that, and two photographs at different magnifications, with the board in different frame
positions, agree:

| | horizontal | vertical |
|---|---|---|
| photo 6 (side with the SoC and shield can) | **26.335 mm** | **24.993 mm** |
| photo 7 (side with the battery contacts and coil) | **26.231 mm** | **24.946 mm** |
| agreement between photographs | **0.40 %** | **0.19 %** |

## Why every one of my "four independent methods" landed near 25

They did not measure four things. **They measured the vertical extent, or used a scale
dominated by one axis, and I called their agreement independence.**

| E04's row | value | vs L1 vertical 24.993 | vs L1 horizontal 26.335 |
|---|---|---|---|
| L5 ours | 24.997 mm | **0.02 %** | 5.1 % |
| L5 Apple's silhouette | 24.832 mm | 0.64 % | 5.7 % |

L5's headline number matches L1's *vertical* extent to **two hundredths of a percent**. That
is not four routes converging on a board dimension. That is one systematic, reproduced four
times, and O'Flynn's ~26 sits **1.3 % from the horizontal extent** — the closest agreement in
the whole exercise, from the source I had written down as "his tilde, not a measurement".

## The part that matters more than the number

E04 contains this sentence, which I wrote:

> *"the datasheet ruler could have returned 26 mm and did not, and its scale source shares
> nothing with the steel rule's — different photographs, different failure modes. Nothing
> links them."*

**Something linked them: the anisotropy.** Every method inherited it, because every method
applied a scalar px/mm to an anisotropic projection. They could not have disagreed about that,
so their agreement carried no information about it.

This is the *same defect* I found in my own coil finding four hours earlier and wrote a rule
against — *name what each read would have had to see to disagree; if you cannot, they are one
measurement.* I then applied that rule in E04, in writing, **and got the answer wrong**,
because I checked whether the *scale sources* were independent and never asked whether the
*projection assumption* was shared. Twice in one session, at two different levels.

**The rule needs the sharper form:** independence must be checked against the assumption every
method has in common, not only against the inputs they do not share. A shared *assumption* is
harder to see than a shared input precisely because nobody writes it down.

## What now stands

| claim | status |
|---|---|
| Bare MLB OD | **BOUNDED 24.95 – 26.34 mm** (L1, two photographs, per-axis) — `REFERENCE-TEARDOWN` §7's CANNOT DETERMINE is narrowed, nothing overturned |
| "The board is smaller than 26 mm" | **WITHDRAWN** (E04) |
| "24.6 mm" | **RETRACTED at source** by L1 — a shadow-inflated area-equivalent diameter over a single x-dominated scale |
| The board images 4.7–5.1 % wider than tall, long axis 12–14° in both photos | **MEASURED, CAUSE CANNOT DETERMINE.** L1 built the right control — the steel rule's punched hanging hole, round by manufacture, same photo, same lens — and **the control is noisier than the effect** (1.083 and 1.027 for the same hole; its own caliper ratio 1.155/1.219 where round must give 1.000). Stated, not corrected for |
| Centre hole | **SUPERELLIPSE, n = 2.70** — and a circle is measurably the worse primitive (resid sd 6.59 vs 5.66 px). Two photographs differ ~6 % on the hole, so **PARTIALLY DETERMINED — publish no single hole diameter** |
| The notch at top centre | **EYEBALLED ONLY** — no residual excursion beyond −2σ, because the flood-fill boundary tracks around it rather than cutting across |

Three numbers still must not travel: **24.6 mm**, **~25 mm as a board diameter**, and L2's
**23.9 mm** search seed.

## What would settle the anisotropy

Any object of **known diameter lying flat on that table** — the one thing the photographs do
not contain. The CR2032 in photo 3 is 20.0 mm by IEC 60086 but sits ~6 mm up inside the
AirTag, carrying an unknown magnification. Failing that, a caliper on a real board.
