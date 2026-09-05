# M02 — the FCC steel rules, and the bare MLB's outer diameter

*halo Replica, L1 PHOTOGRAPH METROLOGY lane, 2026-09-05.*

**SIDE NAMING, used in every file this lane writes.** **FRONT = the COMPONENT
side**, following Apple's own caption in the FCC filing ("A2187 MLB - Front").
O'Flynn's "frontside" (battery contacts, NFC coil) is therefore this project's
**BACK**. Convention settled by the halo lane, commit `391f676`.

**Source.** `images/airtag/fcc-BCGA2187-internal-photo-6.jpg` and `-7.jpg`, FCC
ID BCGA2187 internal photos, a public regulatory filing. Each frame carries an
Apple *"Proprietary and Confidential"* watermark; it is cited as the filing and
the watermark is not stripped.

**Reproduce every number here:**

```
tools/m_ruler_calib.py   --json metrology/ruler-calibration.json
tools/m_scale_field.py   --json metrology/scale-field.json
tools/m_scale_at.py      --photo photo6 --at 952,678
tools/m_outline_fit.py   --image fcc-BCGA2187-internal-photo-6.jpg --box 700,440,1210,930 ...
tools/m_aspect_control.py --json metrology/aspect-control.json
tools/m_silhouette.py    --image ... --box ... --thr 60,160
```

---

## 0. CATALOG.md was wrong, and that is the whole reason this file exists

`images/airtag/CATALOG.md` lists FCC internal photo 6 with no scale reference.
**It has two steel rules** — one along the bottom (cm 1..11 with mm ticks, plus
an inch/16ths scale) and one up the right side. So do photos 1, 2, 3, 4, 5, 7
and 8. Photo 6 also shows the **bare annular board with both its outer edge and
its centre hole unobstructed** — the two things M01 had to write off as CANNOT
DETERMINE from O'Flynn's photograph, because a foam gasket overlaps the edge
there and the magnet assembly covers the hole.

---

## 1. px/mm from the rules — MEASURED

Not from two picked ticks. `m_ruler_calib.py` finds the rule's edge, scans for
the band where the mm comb is the strongest periodic signal, deskews by
projection variance, takes an FFT for a coarse pitch, locates **every** tick as
a sub-pixel dark centroid, assigns integer indices and least-squares fits
`position = a·index + b` over the whole span.

| rule | px/mm | ± (fit) | ticks | span | resid sd | resid max |
|---|---|---|---|---|---|---|
| photo 6 bottom | **15.8875** | 0.0022 | 107 | 107 mm | 0.617 px | 1.564 px |
| photo 6 right | **15.5651** | 0.0082 | 48 | 56 mm | 1.049 px | 2.789 px |
| photo 7 bottom | **15.2585** | 0.0020 | 99 | 99 mm | 0.574 px | 1.654 px |
| photo 7 right | **15.0074** | 0.0083 | 52 | 51 mm | 0.894 px | 1.918 px |
| photo 3 bottom | 16.0157 | 0.0043 | 98 | 98 mm | 1.200 px | 2.862 px |
| photo 3 right | 15.6948 | 0.0087 | 49 | 49 mm | 0.859 px | 1.887 px |
| photo 8 bottom | 14.5145 | 0.0032 | 100 | 102 mm | 0.943 px | 2.725 px |
| photo 8 right | 14.0450 | 0.0122 | 55 | 54 mm | 1.431 px | 3.019 px |

The magnification differs per photograph (13.8 to 16.0 px/mm), so **every
photograph is its own calibration**; a scale from one may not be carried to
another.

### Three checks, all of which can fail, and one of which did

- **split-half** — first and second halves fitted separately; 0.26–1.42 % apart.
- **tick coverage** — `n_ticks / (span+1)`. **This rejected `photo1_right`**
  (10 ticks over 41 mm, coverage 0.24): its integer index assignment could not
  be trusted and it is reported as CANNOT DETERMINE, not as 16.63 px/mm.
- **an independent 5-mm comb** in a deeper band, whose pitch must come out 5×
  the mm pitch. Measured ratios 0.99939–1.00151 on every accepted rule, and
  **0.873 on the rejected one** — the same row failed two unrelated gates.

---

## 2. The two rules disagree, and that is a measurement

| photo | bottom | right | apart |
|---|---|---|---|
| 6 | 15.8875 | 15.5651 | **2.05 %** |
| 7 | 15.2585 | 15.0074 | **1.66 %** |
| 8 | 14.5145 | 14.0450 | **3.29 %** |
| 3 | 16.0157 | 15.6948 | **2.05 %** |

**The right rule is lower in every photograph.** It is not averaged away.
`m_scale_field.py` fits a cubic to tick position vs tick index and
differentiates it, giving local px/mm as a function of position along each
rule: it varies **0.67–1.72 %** along the bottom rules and **2.47–4.70 %**
along the right ones.

So "the px/mm of a photograph" is not one number, and both rules lie near the
frame edges while the board lies near the centre.

### px/mm AT THE BOARD — `m_scale_at.py`

First-order field `s(x,y) = s(rule) + a·dx + b·dy`, with `a = ds/dx` measured on
the bottom rule and `b = ds/dy` measured on the right rule. The target is
reached by **two routes that share no tick, no rule, no direction and no travel
path** — along the bottom rule then up in y, and along the right rule then
across in x. *(Naming what would make them disagree, so their agreement means
something: an anisotropic field at the target, a wrong gradient, or a field that
is not first-order over that distance.)*

| photo | at | route 1 (x-scale carried) | route 2 (y-scale carried) | apart |
|---|---|---|---|---|
| 6 | (952, 678) | **15.6672** | **15.7029** | **0.23 %** |
| 7 | (932, 752) | **15.0380** | **15.1059** | **0.45 %** |

---

## 3. Bare MLB outer diameter — MEASURED, and it is NOT 24.6 mm

Edge = the **steepest luma gradient** along each of 1440 rays, sub-pixel, in a
window bootstrapped from the azimuthal profile. Width = **trimmed caliper**
(99.5th − 0.5th percentile of the projection), which needs no centre and which
one bad ray cannot set.

**The width is divided by the x-scale and the height by the y-scale.** That is
the physically correct thing to do for an image whose two axes may not share a
scale, and it is what makes the two photographs agree.

| | photo 6 (FRONT) | photo 7 (BACK) | agreement |
|---|---|---|---|
| horizontal | 412.60 px → **26.335 mm** | 394.46 px → **26.231 mm** | **0.40 %** |
| vertical | 392.46 px → **24.993 mm** | 376.83 px → **24.946 mm** | **0.19 %** |
| w/h in pixels | 1.0513 | 1.0468 | |
| rays used | 1364/1440 | 1434/1440 | |

**Two independent photographs of the same board, taken at different
magnifications (15.9 vs 15.3 px/mm) and with the board in different places in
the frame, agree to 0.4 % and 0.19 %.** That is the strongest statement in this
document.

### VERDICT

> **Bare MLB outer diameter: between 24.95 mm and 26.34 mm.**
> The horizontal figure, **26.3 mm**, is within 1.3 % of O'Flynn's "~26 mm".
> **`REFERENCE-TEARDOWN.md` §7's "CANNOT DETERMINE" is now bounded, and nothing
> in it is overturned. 26 mm is not contradicted.**

The residual 5 % is stated below, unresolved, rather than split.

### The 5 % that is not settled — and it CANNOT DETERMINE, honestly

The board images **4.7–5.1 % wider than tall**, in *both* photographs, with the
long direction at φ = 12–14° in both. A fixed camera tilt or an anisotropic
render would do exactly that; a non-circular board would not do it identically
in two separate placements.

**The control I built to settle it does not settle it.** `m_aspect_control.py`
measures the punched hanging hole in the bottom steel rule — **round by
manufacture, same photograph, same table, same lens**:

| photo | hole w/h | board w/h | residue |
|---|---|---|---|
| 6 | 1.0828 | (contaminated, see §5) | — |
| 7 | 1.0272 | 1.0495 | +2.23 pp |

The two photographs give **1.083 and 1.027 for the same physical hole**, and the
hole's own caliper max/min is 1.155 and 1.219 where a round object must give
1.000. **The control is noisier than the effect it is meant to measure** — the
hole is ~100 px across at a low paper-through-steel contrast — so it is reported
as CANNOT DETERMINE and not used to correct anything.

**What would settle it:** any object of accurately known diameter lying flat on
that same table — or a caliper on a real bare MLB. The CR2032 in photo 3 is
20.0 mm by IEC 60086, but it sits ~6 mm above the table inside the AirTag, so
its apparent size carries an unknown magnification and it cannot be used
without the camera distance.

---

## 4. Centre hole — it is NOT a circle

Segmented as the **bright region connected to the board centre** (the hole shows
over-exposed white paper; the board around it is dark). This cannot saturate at
a search-window boundary — there is no window — and a pale component beside the
hole matters only if it is *connected*, which the labelling decides rather than
a threshold guess.

| | photo 6 (FRONT) | photo 7 (BACK) |
|---|---|---|
| horizontal | 194.00 px → **12.38 mm** | 198.00 px → **13.17 mm** |
| vertical | 205.00 px → **13.06 mm** | 202.00 px → **13.37 mm** |
| superellipse `n` | **2.70** | 2.00 |
| 2a × 2b | 191.8 × 194.5 px | 204.0 × 196.3 px |
| corner radius | 62.1 px ≈ **3.96 mm** | 94.5 px |
| fit residual sd | 5.66 px | 5.52 px |

`n = 2.00` is an ellipse and `n → ∞` a rectangle. **Photo 6 measures n = 2.70 —
a rounded square, not a circle.** A circle fitted to the same boundary points is
the worse primitive (residual sd 6.59 px vs the superellipse's 5.66 px).

**The two photographs disagree by ~6 % on the hole and by 0.7 on `n`.** The hole
is bounded by different structures on the two sides of the board, so this is not
yet one number. **Hole geometry: PARTIALLY DETERMINED. Do not publish a single
hole diameter from this file.**

**The notch is NOT confirmed.** No run of ≥3° with a fit residual beyond −2 σ
was found in either photograph. It is visible by eye at top centre in photo 6;
the flood-fill boundary tracks around it rather than cutting across it, so the
superellipse residual never records it. **Stated as eyeballed, not measured.**

---

## 5. WHAT I DISCARDED, AND WHY

Four wrong numbers were produced on the way here. Each is recorded so nobody
re-derives it.

1. **A hardcoded ruler strip → 4 % error.** Photos 6 and 7 place the *same*
   rule ~18 px apart in y. A fixed band read photo 7's **5-mm** ticks instead of
   its mm ticks: 15.265 px/mm where the mm comb gives 15.2585 only after the
   band is found per image. `m_ruler_calib.py` now auto-finds the rule edge.

2. **Half-max edge detection followed the CONTACT SHADOW, not the board.** The
   half-way level between the board's dark and the paper's bright lands inside
   the penumbra. It gave r sd 6.8 px on a board round to ~1 px, and because the
   error is one-sided it also faked an ellipse whose major axis pointed −40° in
   photo 6 and +13° in photo 7 — **a different direction in each photograph,
   which no real board shape does.** That is how it was caught: by drawing the
   measured points back onto the photograph (`m_overlay.py`) and *looking*.
   `halfmax` is kept in `m_outline_fit.py` as the **named negative control**.

3. **"Largest dark blob" segmentation is cut by BRIGHT PADS ON THE RIM.**
   Measured on photo 7: r = 136 px against a mean of 185 px at 100°, exactly
   where a pale metal rim pad sits. **That is the 30 % excursion the
   orchestrator flagged — it is the detector, not the board.**

4. **THE NUMBER I ALMOST PUBLISHED: 24.6 mm.** It came from dividing a
   shadow-inflated *area-equivalent* diameter by a single scale that was
   derived mostly from the x-direction. Mixing an x-derived scale with a
   direction-averaged diameter, in an image that is 5 % anisotropic, moves the
   answer by more than the whole disagreement with O'Flynn. **The board is not
   24.6 mm. Any downstream document carrying 24.6 mm from this lane is wrong
   and should be corrected to the 24.95–26.34 mm bound above.**

5. **A coordinate bug that mislabelled every position.** `m_ruler_calib.comb()`
   returned tick positions in *strip* coordinates and never added the strip
   origin back, so every position was short by 400 px (bottom rules) or 100 px
   (right rules). Harmless for a *pitch*; wrong for anything asking *where* a
   pitch was measured — which is exactly what `m_scale_at.py` asks. Caught by
   noticing that a rule which visibly reaches x = 2000 reported its last tick
   at 1587.

---

## 6. Status

| # | quantity | verdict |
|---|---|---|
| 1 | px/mm of photos 1–8 from the steel rules | **MEASURED**, resid sd 0.57–1.43 px |
| 2 | px/mm at the board, two independent routes | **MEASURED**, routes 0.23 % / 0.45 % apart |
| 3 | bare MLB outer diameter | **BOUNDED: 24.95–26.34 mm**, reproducible to 0.4 % across two photographs |
| 4 | whether the imaging is anisotropic | **CANNOT DETERMINE** — the round-hole control is noisier than the 5 % effect |
| 5 | centre-hole shape: a rounded square, not a circle | **MEASURED** (n = 2.70, photo 6) |
| 6 | centre-hole dimensions as one number | **CANNOT DETERMINE** — the two photographs differ by ~6 % |
| 7 | the notch at top centre of the hole | **EYEBALLED ONLY**, not measured |
| 8 | edge solder pads: count and angular positions | **NOT YET MEASURED** |
| 9 | board thickness | **NOT ATTEMPTED** — no edge-on photograph in the set |

---

## 7. Regression, 2026-09-05, after the tools were changed

The tools were edited after this file was written (a NaN guard, the `halfmax`
negative control moved into `m_outline_fit.py`, a differential rim detector).
Every published number here was re-derived afterwards and reproduces:

| quantity | published | re-run |
|---|---|---|
| photo 6 bottom rule | 15.8875 px/mm | **15.8875** |
| photo 6 right rule | 15.5651 px/mm | **15.5651** |
| px/mm at the board | 15.6850 ± 0.0179 | **15.6850 ± 0.0179** |
| hole superellipse `n` | 2.70 | **2.70** |
| hole corner radius | 62.08 px | **62.08 px** |

**One correction:** the fit standard error on the photo 6 bottom rule was first
written as ±0.0019 and re-runs as **±0.0022**. The px/mm value itself is
unchanged and nothing downstream moves; the table above has been corrected.


---

## 8. IS THE MEASURED EDGE THE SUBSTRATE, OR THE GASKET? — 2026-09-05

A grey fibrous material laps over the board's rim (the same material that
defeated luminance edge-finding in M01 §2; E01 calls it a conductive gasket or
adhesive). If this lane's outer diameter were the **gasket's** boundary rather
than the **substrate's**, every OD would be too large in *both* photographs by the
same amount — and their 0.40 % agreement would not detect it, because a shared
bias is not a disagreement. It is additive: a gasket can only make the board look
bigger.

**Measured** with `tools/m_rim_step.py`: cast rays, locate the edge exactly as
`m_outline_fit` does, then average luma at fixed offsets around it with the edge
**aligned**, over more than a thousand rays. A gasket lip reads as
*dark substrate → grey plateau → bright paper*: two steps with a flat between.
The prediction from M06 is printed **before** the result so it cannot be fitted
afterwards.

| | FCC photo 6 | O'Flynn component side |
|---|---|---|
| genuine px/mm (M06) | 4.6 | ~24 |
| a 0.3 mm lip would be | **1.4 genuine px** | **7.2 genuine px** |
| prediction | below resolution | resolvable |
| strongest luma rise | +0.000 mm, slope **11.51** | +0.001 mm, slope **6.30** |
| next rise | +0.104 mm, slope 5.46 (**47 %**) | +0.370 mm, slope 0.36 (**6 %**) |
| separation | 0.112 mm = **0.5 genuine px** | 0.369 mm = **8.9 genuine px** |
| verdict | **CANNOT DETERMINE** | **CANNOT DETERMINE** |

**FCC photo 6 behaves exactly as predicted** — the two candidate boundaries are
0.5 genuine pixels apart and cannot be separated.

**O'Flynn's image does show the structure**, and it still cannot settle the
question. The edge-aligned profile is dark board ≈70 → a sharp rise to a **grey
plateau at ≈175 running to +0.29 mm** → a gentle ramp to the paper level ≈205.
There is genuinely a ~0.25–0.30 mm grey band outside the steep edge. **But a
contact shadow produces exactly the same thing** — a darker band immediately
outside the board that brightens outward — and nothing here separates gasket
overhang from penumbra.

### The reassuring part, which is the actual answer to the concern

> **The steepest gradient is the INNER boundary, not the outer, by a factor of
> 17** (6.30 against 0.36 luma/sample). `m_outline_fit` selects the steepest
> gradient, so **the published edge is the dark→grey transition — the innermost
> of the two.** If the grey band is gasket lapping over the rim, this lane's OD
> **excludes** it.

So the feared bias runs the **opposite way** to the fear: the risk is not that
the published OD is inflated by the gasket, but that on a photograph where the
two boundaries are unresolved (FCC photo 6, 0.5 genuine px) the detector settles
on a *blended* edge somewhere between them, biasing that photograph's OD
slightly **outward** relative to a sharp one.

### A third, partly independent diameter

The outline was then measured on **O'Flynn's own image** rather than transferred
(`metrology/outline-raw-oflynn-front.json`, 1194/1440 rays):

> **median diameter 24.631 mm**

This is *not* fully independent — its scale came from FCC photo 6 through the
registration — but the *outline* is measured on the sharper photograph. It sits
just below the 24.95 mm low end of §3's bound, in the direction the blended-edge
argument predicts. **The §3 bound is not revised on one figure**; it is recorded
as the third estimate and as consistent with the low end.

**Still CANNOT DETERMINE: whether the published edge is substrate or gasket.**
What would settle it: a cross-section, or a caliper on a real board with and
without the gasket.

### A SIGNED EXPECTATION, so it can be proved wrong

Two independent arguments now point the same way, and both were in place before
the third estimate was measured:

1. where the two boundaries are **unresolved** (FCC photo 6, 0.5 genuine px) the
   steepest-gradient detector settles on a **blended** edge, biasing that
   photograph **outward** — and FCC photo 6 is where §3's bound came from;
2. the outline measured on the **sharper** photograph came in at 24.631 mm, below
   the bound's 24.95 mm floor.

> **IF THE §3 BOUND EVER MOVES, IT MOVES DOWN.** Recorded as a falsifiable claim
> about future work, not as a hedge. A better datum that lands *above* 26.34 mm
> would show this reasoning to be wrong, and that is the point of writing it down.

The bound is **not** revised now: the third estimate's scale still comes from FCC
photo 6 through the registration, so it is not independent and cannot carry a
revision by itself.
