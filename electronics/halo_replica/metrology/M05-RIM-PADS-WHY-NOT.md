# M05 — the rim pads: the detector was broken, then fixed, and the answer still stands

*halo Replica, L1 PHOTOGRAPH METROLOGY lane, 2026-09-05. Supersedes M03 §3's
explanation; **M03's verdict is unchanged**.*

**SIDE NAMING:** FRONT = the COMPONENT side (Apple's FCC caption). See M02.

**Reproduce:** `tools/m_selftest.py` — 19 cases, synthetic ground truth and
deliberate breaks, exit 0/1.

---

## What M03 claimed, and why that claim was not earned

M03 concluded the rim-pad count is CANNOT DETERMINE and blamed **resolution**.
That is a claim about the *detector* — that it would have found the pads had they
been resolvable — and M03 asserted it without testing it. So I built the test.

## 1. The detector failed a POSITIVE control — it was broken

`m_selftest.py` builds a synthetic rim at photo 6's exact scale (r = 196 px,
15.685 px/mm) with 26 clutter components set back from the rim and **six pads of
stated arc length running out to the edge**. The original blob detector, run on
that, **found ONE of six.**

**Cause:** its threshold was the 80th percentile of the annulus, which on that
image came out **9 luma above the board's own level**, so every bright thing in
the annulus merged into a handful of giant connected regions — each of which both
reaches the edge *and* is set back, so no reach criterion could separate them.
Raising the percentile to 95 recovered all six — which is precisely the number one
would then be tempted to tune against the real image until it gave the expected
answer.

**The failing case is kept** (`--mode blob`) so the defect stays reproducible.

## 2. The replacement passes both controls

`--mode differential` (now the default): the pad signal is the mean luma at the
very edge (0.955–1.00 of the local edge radius) **minus** the mean just behind it
(0.88–0.94). It cannot merge, because it is per-column and it is a *difference*:
a pad is bright at the edge and dark behind → positive; a component set back is
the reverse → negative; a uniformly bright arc → zero. It is also immune to the
annulus's overall brightness, which differed between the two photographs.

| case | result |
|---|---|
| 6 pads of 1.0 mm arc | **6 found, 6/6 at the right angles**, control max 0 |
| 6 pads of 1.6 mm arc | **6 found, 6/6 at the right angles**, control max 0 |
| 12 pads of 1.0 mm arc | **12 found, 12/12 at the right angles**, control max 4 |
| **0 pads, clutter only** | **0 found**, control max 0 — it does not invent pads |

## 3. AND THE POSITIVE CONTROL WAS STILL NOT REPRESENTATIVE — measured, not assumed

A detector that passes on a clean synthetic has been shown to have correct
*logic*, and **nothing** about whether it can work on *this source*. So the two
were compared on the one quantity that decides it — the noise in the very signal
the detector thresholds:

| | differential signal, robust sd |
|---|---|
| clean synthetic rim | **1.8 luma** |
| **FCC photo 6 (FRONT)** | **34.6 luma** |
| **FCC photo 7 (BACK)** | **37.3 luma** |

**The synthetic was 19× cleaner than the photograph.** A pad carrying the
synthetic's full 111-luma contrast would therefore stand at only
**111 / 34.6 ≈ 3.2 σ** in photo 6 — below the 4 σ gate, and no larger than the
biggest excursion the real rim already produces from nothing (max 139.5 ≈ 4.0 σ).

**The selftest now contains that case.** The same detector, on a synthetic with
texture raised to a real-like differential sd of 52 luma, carrying six pads that
are certainly there, **finds zero.**

## 4. On the real photographs

| | features found | control (rows rolled) | verdict |
|---|---|---|---|
| photo 6 (FRONT) | **0** | mean 0.07, max 2 | **CANNOT DETERMINE** |
| photo 7 (BACK) | **0** | mean 0.03, max 1 | **CANNOT DETERMINE** |

## VERDICT — unchanged from M03, but now for a reason that was measured

> **The number of rim tear-off / edge pads is CANNOT DETERMINE, and the cause is
> the source's signal-to-noise, not the detector.** A detector validated to find
> 6 of 6 and 12 of 12 pads at this exact scale finds none — and is *shown*, on a
> noise-matched synthetic, to be unable to find pads that are certainly there at
> this photograph's noise level.
>
> **The dossier's "six" is still neither confirmed nor refuted.** Nothing in M03
> or M05 should be cited as either.

Combined with M04 — the board region of these 2134 px files carries the real
detail of only ~711–1067 px of width — the rim question is **closed on the
available evidence**, not left hanging on an unexplored option.

## 5. WHAT I DISCARDED

- **The 15 and 13 counts of M03 are withdrawn as measurements of anything.**
  They came from the blob detector now shown to fail its positive control. They
  remain on disk as candidates and must not be drawn.
- **M03 §3's attribution to "resolution" was unearned when written.** It happened
  to be right; it was not established. It is established now, and the difference
  is a number.
- **A positive control that is too easy is the same defect as a negative control
  that cannot lose** — the two failures I recorded earlier today. All three are
  checks that cannot fail. This one is the subtlest, because a *passing* positive
  control feels like evidence, and the only way to catch it was to measure
  whether the synthetic resembled the thing it stood in for.

## 6. Status

| # | quantity | verdict |
|---|---|---|
| 1 | rim pad count | **CANNOT DETERMINE**, cause measured: 3.2 σ against a 4 σ gate |
| 2 | the differential detector's logic | **VALIDATED** — 6/6, 12/12, and 0 on clutter |
| 3 | the original blob detector | **BROKEN, and kept so the break is reproducible** |
| 4 | the dossier's "six" | **neither confirmed nor refuted** |
| 5 | what would settle it | a real board under a microscope; not another look at this source |
