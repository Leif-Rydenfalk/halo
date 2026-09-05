# PROTOCOL — counting the rim tear-off joints, BLIND

*halo Replica. Written by the L7 lane, 2026-09-05, for a **different** session to
execute. L7 is standing down from this question and is not the right lane to
answer it.*

---

## 0. Read this section before anything else

**A number is being deliberately withheld from you, and so are some observations.**

The L7 lane attempted this count, produced no answer, and in the course of trying
**looked at the rim of the photograph at native resolution and formed an
impression of how many features are there.** It also knows what figure an
existing project document states.

Those two things landed in the same head, and **they agreed**. That is precisely
the condition under which a person stops being able to produce an independent
count: any number that lane now reports — even from a correctly-matched
instrument, even with predictions registered in advance — cannot be separated
from the number it already expected to find.

**So the count is withheld from you on purpose.** Not because it is secret, and
not because you are less trusted. Because **your count is only worth having if it
was reached without it.** L7's observation is on disk, timestamped, marked
never-to-be-drawn, and it will be compared against your result **after** you
commit yours. If you disagree with it, that disagreement is the most valuable
thing this exercise can produce, and it only exists if you never saw it.

If at any point you find yourself thinking *"that is close to what I'd expect"* —
you have been contaminated by something. Say so in your write-up. A contaminated
count reported as contaminated is worth more than a clean-looking one that isn't.

## 1. The reading allow-list — and why it is an allow-list

**Read ONLY the files below until your count is committed.**

L7 grepped this repository for statements of the withheld figure and found it in
**more than twenty files**, across `docs/`, `metrology/` and `tools/` — including
places nobody would think to check, such as a selftest that builds a synthetic
rim carrying a specific number of pads, and log files that quote a document title.

> **A deny-list has to be complete to work. An allow-list does not.** That is the
> whole reason this section is shaped the way it is, and it is the transferable
> part: when you are protecting against leakage you cannot enumerate, enumerate
> what is permitted instead.

**Permitted:**

| file | for |
|---|---|
| this protocol | the method |
| `images/airtag/oflynn-backside-fullres.jpeg` | **the source.** The side carrying the SoC and the shield can |
| `metrology/c_register-fit-boardscale.json` | the frame: origin, homography, scale basis |
| `metrology/outline-raw-photo6.json` | the board outline the frame transfers |
| `tools/m_dark_packages.py` | `board_frame()` — gives luma, board mask, outline, origin, px/mm in one call |
| `tools/d_rect.py` | the boundary engine, its nulls, `fit_sides`, `side_bar`, `phase_scramble`, and its 10-case selftest |
| `tools/d_darkpkg.py` | `prep`, `side_steps`, `run_id` helpers |
| `tools/d_rim.py` | the rim harness. **Verified blind-safe**: states no count, cites no count, carries no feature positions |
| `bin/boardmetro` | `circle`, `radial`, `scale-ruler`, `rect`, and their selftests |
| `evidence/E07-CHECKS-THAT-CANNOT-FAIL.md` | **required.** The catalogue of ways a check passed here without being able to fail |

**Forbidden until your count is committed** — this list is *illustrative, not
exhaustive*, which is why the allow-list is the operative rule:
`docs/REFERENCE-TEARDOWN.md` and everything else under `docs/`;
`metrology/M03-*`, `metrology/M05-*`, `metrology/darkpkg/M12-*`,
`metrology/darkpkg/P01-*`; every `metrology/darkpkg/r-*.json` and `r-*.log`;
`metrology/darkpkg/r-seeds-WITHHELD.json`; `tools/m_rim_*.py`,
`tools/m_pad_registration.py`, `tools/m_selftest.py`.

`d_rim.py`'s `step` and `probe` verbs **refuse to run** without
`--i-am-not-counting`, because their seeds reveal how many rim features one
person found by eye and where. **You are counting. Do not pass that flag.** Use
`null`, `limit` and `count`, which need no seeds.

## 2. The question

**How many tear-off joints attach the antenna carrier to the board rim?**

No expected value is given. It may be any number including zero, and *"the
photograph cannot support a count"* remains a legitimate and complete answer —
two earlier attempts reached exactly that, and closing it a third time **with a
number attached to the refusal** is a better outcome than a count you don't
believe.

## 3. What is already established, and what it is safe to reuse

- **Source and scale.** `oflynn-backside-fullres.jpeg`, **106.313 px/mm stored**,
  registration-derived, cross-checked to 0.23 % against a package dimension from
  a datasheet. **Genuine resolution 20.7–27.4 px/mm** — roughly 5× the source the
  earlier attempts used. Do not re-derive the scale; do not use 15.8875 (that is
  a different photograph's rule) or 110.3 (an outlier).
- **The floor.** Registration held-out error 0.1029 mm, 2–3 genuine px.
  **Quote no position to 0.01 mm.** Report every size with its short side in
  *genuine* pixels.
- **The rim annulus.** `d_rim.rim_mask()` — 0.86–1.01 of the **local** edge
  radius r(θ). A constant-radius ring is wrong: this board's apparent radius
  varies ~5 % with angle and such a ring drifts on and off the board.
- **The rim annulus is ~1.8 mm wide.** Windows larger than that do not fit inside
  it, and requiring them to is a statement about your mask rather than the board.

## 4. Method

### 4.1 Do not assume a morphology, and do not assume only one

L7's instrument models a feature as **a rectangle with four straight sides**. It
returned detections that scored well above its bar and **were the wrong objects
entirely** — verified by drawing them onto the photograph and looking.

> **A detector matched to one morphology misses another SILENTLY, and what it
> returns instead still looks like a result.** Before you count, characterise
> what is actually at the rim, and **pre-register the morphology classes you will
> accept and the instrument you will use for each.** If you find more than one
> class, you need more than one instrument, and a count from one of them is a
> count of that class and must be labelled as such.

### 4.2 The bar is measured, never invented, and it is not portable

Two nulls, both with **no operator choice in them**:

- **N1 — phase-scrambled.** `d_rect.phase_scramble` on the same image: identical
  power spectrum, so every texture statistic survives, and no straight edge or
  closed corner does. Asks: does the feature beat texture of the same spectrum?
- **N3 — the real rim.** The identical scan at random places and random angles
  with centres sampled **in the annulus**. Asks the question a *detector* must
  answer: is this feature exceptional among the structures the rim already has?
  **N3 is the bar.** Use its p99, and report its maximum too.

> **A bar measured for one object size does not transfer to another.** L7
> measured 100–160 luma for a 3.2 mm object and, at 1.1 mm, the same photograph
> needed **140–170**. Quoting the first number at the second scale would have been
> a borrowed constant. **Measure your bar at the size of the thing you are
> counting**, and if you accept two size classes, measure it for both.

### 4.3 Sample in the annulus, fit against the whole board

`d_rect.side_bar(..., sample_mask=<annulus>, mask=<whole board>)`. Masking the
*fit* to a narrow annulus makes the fitter fight an artificial boundary of your
own making. Sampling centres in the annulus while fitting against the board asks
the rim question without inventing an edge.

### 4.4 The mask must be dilated outward, and this one nearly produced a fake result

**A rim feature straddles the board edge.** Fitting against the eroded board mask
cuts its outer boundary, the scan returns nothing, **and prints a zero**.

L7's first run returned **|z| = 0.0 on 11 of 20 boundaries** and was one step from
reporting that as *"no boundary"*. It was **the absence of a measurement wearing
the costume of strong evidence of absence.** Fixed by dilating the board mask
**1.5 mm outward**, into the gasket and background where a rim feature's outer
boundary legitimately is (`d_rim --dilate-mm`).

> **An unmeasured thing must never be representable in the same field as a
> measured zero.** `d_rim probe` now *names* its unmeasured sides. Whatever you
> build must do the same. Check your own output for zeros and ask, for each one,
> whether it is a measurement.

### 4.5 The limit ladder — a positive control made OF the photograph

A synthetic control cleaner than the source is not evidence; one built here came
out **19× cleaner** than the photograph it stood in for. So: paste a feature of
**known size and known contrast** into the photograph itself, at the quietest
non-overlapping windows **chosen by code**, and find the contrast at which its
boundaries clear your bar. That converts *"we could not see them"* into
*"at the contrast they present, they could not have been seen"* — which closes a
question instead of leaving it open.

> **The site is a parameter too.** L7's first ladder used the *single* quietest
> window and it landed on a metal shield can — smooth at that scale, so it won a
> gradient-energy contest while being nothing like the surface the features
> actually sit on. **Nothing in the numbers said so; only drawing it and looking
> did.** Sweeping the site moved the answer. *An automatic choice is not the same
> as a controlled one:* "chosen by the code, not by me" removes your hand and
> leaves the criterion's own blind spot exactly where it was — and it feels more
> objective, which is what makes it dangerous.

### 4.6 The number that decides must be the number the method uses

L7's sharpest self-inflicted error, and the one most likely to catch you:

A per-side boundary step measured at a rough hand-placed outline came out low, and
was visibly **diluted** by the bad outline. So it was measured a second way that
did not depend on the outline at all — brightest core against the surround just
beyond — which came out **roughly twice as high**, above the limit. That was read
as *the bar is cleared*, and said out loud. **It was wrong.** Core-minus-surround
is a **peak-to-median** statistic and a loose upper bound on a boundary **step**,
and the step is what the detector integrates. The direct per-side measurement
settled it, in the other direction.

> **A quantity measured a second way is not automatically the better one.** The
> outline-independent estimate was more robust *and further from what the method
> consumes*. **The number that decides a verdict has to be the number the method
> uses, not a proxy that correlates with it.** The tell is that the second
> measurement was of a *different quantity*, not a second look at the same one.

## 5. What you must commit BEFORE looking at the rim

A pre-registration file, committed and pushed, containing:

1. **The instrument(s)**, named, with the morphology class each covers.
2. **Quantitative predictions with their falsification conditions** — "predicted
   X–Y, falsified below Z". A prediction that cannot be wrong is not one.
3. **The bar methodology**, stated before the bar is measured.
4. **Your own bias, named in advance, with its direction.** L7 predicted its bias
   would be pessimism; it was pessimism, then optimism, and only the direct
   measurement was neither. Scoring that was worth more than getting it right.
5. **NO PREDICTED COUNT.** You do not have one and must not invent one to have
   something to register. Register the *method*, not the answer.
6. **The stopping rule**: what result makes you stop and report CANNOT DETERMINE.
   Decide it now, while it costs nothing.

## 6. Controls you inherit — and what one of them does not cover

An earlier lane found candidate features clustering in **disjoint arcs** between
two views of the same board, which two views of one board cannot honestly
produce, and correctly used that as a disqualifying tell for a detector following
per-photograph illumination. **Apply it.**

> **But know what it does not cover.** L7's five detections spanned five of eight
> octants and **passed that tell comfortably while being entirely the wrong
> objects.** It catches a detector following illumination. It does not catch a
> detector looking at the wrong things. **Passing it is necessary and nowhere near
> sufficient**, and the only thing that caught the wrong objects was drawing them
> on the photograph and looking.

Also inherit, from `E07`: a check that agrees with what it checks; a control that
cannot lose *or* cannot pass; a positive control that is too easy; and a check
that **saturates** — a null whose variance estimate collapses to zero, sending
every score to infinity and reporting maximum confidence in everything.

**Break every check you write, on purpose, and watch it go red before you trust
it.** And note the trap L7 fell into *inside its own selftest*: a regression case
written against a clean synthetic **passed with the guard it protects removed**,
because on an easy case the failure has no reason to occur. **A regression test
written against an easy case is not a regression test.**

## 7. Draw it and look

Non-negotiable, and it caught two separate errors here that no number did: the
paste site on the wrong material, and five confident detections of the wrong
objects. **Render your detections onto the photograph and look at them before you
report a count.**

## 8. Reporting

1. **Commit your count — or your refusal, with the number attached — first.**
2. **Then, and only then**, read `metrology/darkpkg/M12-...md` §5, then
   `metrology/M03-*`, `metrology/M05-*`, and `docs/REFERENCE-TEARDOWN.md`.
3. **Report the comparison as a separate, later commit**, so the record shows
   your count was fixed before you saw theirs.
4. If your count differs from any of them, **that corrects a document** — route it
   to the orchestrator rather than editing another lane's file.
5. Draw nothing as a pad or a joint until it clears your bar. Withdrawn
   candidates from earlier lanes are on disk marked never-to-be-drawn; anything
   that does not clear joins them.
