# M13 — CORRECTION: the "1–26 luma presented" half of my own headline was not a measurement

*halo Replica, L7 lane, 2026-09-05. **Corrects M11 §0 and §4.** M11 is not edited;
this is the correction beside it. **The verdict does not change. The sentence I
used to justify it does.***

**Reproduce:** `tools/d_darkpkg.py stepaudit --audit-control-n 40`.

---

## What I published

> *"This photograph needs a boundary step of 100–160 luma… The packages present
> **1–26 luma** on most of their sides."*

Read as a comparison of two like quantities, it says the source falls short by
roughly an order of magnitude. **It is not a comparison of two like quantities,
and I should have caught that before publishing it.**

## Why I went looking

Relayed today: three numbers were amplified upward and all three flattered,
each caught by someone recounting rather than by the relayer checking — *apply
the check hardest to results you are pleased with.*

The "1–26" is a result I was pleased with, **and it flatters my conclusion**: a
small presented step makes the gap to the limit look large, which makes the
CANNOT DETERMINE look inevitable rather than arguable. And I already knew the
construction was suspect, because **the same construction had fooled me at the
rim four hours earlier**: a per-side step measured at a rough hand-placed outline
reads low, because a bad outline puts the inside band partly outside and the
outside band partly inside.

## What the audit found

Sweeping the outline (position ±24 px, angle ±8°, size ±15 % — 4275 outlines per
package) and keeping the largest step obtainable:

| package | seed largest | swept largest | seed median side | swept median side |
|---|---|---|---|---|
| nRF52832 (control) | 75 | 171 | 9 | 84 |
| black at 9 o'clock | 8 | **130** | 4 | 62 |
| "+AKN 8H7" | 20 | 60 | 12 | 44 |
| "05I 1A8" | 145 | 165 | 16 | 130 |
| black diode-like | 6 | **77** | 4 | 52 |

**Up to 16× on one package.** So yes — the published number was diluted by my own
rough outlines, exactly as suspected.

## And then the control, which stopped me correcting the wrong way

**Sweeping 4275 outlines and keeping the best takes the maximum of a noisy field.**
So the identical sweep was run at 40 **random on-board locations with no package
stated**, random size, random angle:

| | p50 | p90 | p99 | max |
|---|---|---|---|---|
| swept median side, **no package** | **98** | 144 | **181** | 192 |
| swept largest side, **no package** | 146 | 179 | 201 | 207 |

> **Bare board sweeps HIGHER than the packages do.** The five packages' swept
> median sides are 44–130; the no-package control's median is 98 and its 99th
> percentile is 181. **Zero of five packages beat the control's p99.**

So the swept numbers are **almost entirely selection**, and had I published
*"the packages actually present 44–130 luma"* I would have repeated the rim
mistake precisely — abandoning a diluted number for a looser upper bound and
calling the second one better.

## The correction

**Neither number is a measurement of the packages' boundary step.**

> The per-side luma step at a hand-placed outline is **not a well-defined quantity
> on this photograph.** It runs from 1 to 130 luma depending on where the outline
> is put, and a **no-package control covers the same range**. It should never have
> appeared in a headline beside the 100–160, which *is* measured — with a stated
> control, at a code-chosen site, swept across five sites.
>
> **I compared a measured quantity with an unmeasured one and the comparison read
> as evidence.** That is the defect. The 100–160 keeps its standing; the 1–26
> loses all of it.

## What does NOT change, and why

Everything M11 actually rests on is untouched, because **none of it uses the luma
step**:

- **1 of 20 boundaries supported** — |z| against a null measured on this image.
- **The detection limit, 100–160 luma** — a rectangle of *known* step pasted into
  this photograph at five code-chosen sites.
- **The verdict: CANNOT DETERMINE**, with no position and no size published.

The dark packages are still not placeable, for the reasons M11 gives. What is
withdrawn is one sentence that made the shortfall sound quantified when half of
it was not.

## The shape of this failure, for the catalogue

E07 already carries *"a check that agrees with what it checks"* and *"a positive
control that is too easy"*. This is a third relative:

> **A COMPARISON BETWEEN A MEASURED QUANTITY AND AN UNMEASURED ONE, PRESENTED AS
> A RATIO.** Both numbers were real, both were in the same unit, and the
> arithmetic was right. Neither of those makes them comparable. **The unit matching
> is what made it invisible** — a luma step beside a luma step looks like a
> like-for-like comparison, and only asking *"was this one measured the way that
> one was?"* separates them.

And the audit's own control is the general lesson restated: **when you sweep a
parameter and keep the best, run the sweep where the answer is known to be
absent, or the sweep's maximum is your result.**

## Status

| # | quantity | verdict |
|---|---|---|
| 1 | M11's detection limit, 100–160 luma | **STANDS** — measured, controlled, site-swept |
| 2 | M11's "packages present 1–26 luma" | **WITHDRAWN** — diluted by my outlines, and not a measurement |
| 3 | the swept alternative, 44–130 luma | **ALSO WITHDRAWN** — a no-package control reaches 98 median / 181 p99 |
| 4 | the packages' true boundary step | **CANNOT DETERMINE** — outline-dependent over 1–130 luma on this source |
| 5 | M11's verdict and all its per-side \|z\| evidence | **UNCHANGED** |
