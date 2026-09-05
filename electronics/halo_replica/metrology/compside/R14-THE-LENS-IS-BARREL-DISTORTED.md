# R14 — one of R11's three candidates is now measured: **photo 7's lens is barrel-distorted**

> **⚠ FULLY SUPERSEDED BY [R17](R17-THE-RULE-EDGES-ARE-STRAIGHT.md).** Its per-edge sagittas (1.137 and 4.310 px) are CONTAMINATION: the
> tracker was following the rule's TICK MARKS and, past x ~ 1700, the rule's far end
> rather than its edge. With a continuity gate, a two-level refusal and the clean span,
> both bottom edges measure **0.194 px and 0.123 px, neither clearing its null**, and
> both right edges are **refused as two-level traces**. There is no measurable lens
> distortion. Nothing numeric in this file stands.


> **⚠ THIS FILE'S HEADLINE IS WRONG — read [R15](R15-NOT-SIMPLE-BARREL-R14-CORRECTED.md).**
> The sign test below passed and I published on it. The **magnitude** test, which this file
> never ran, fails: photo 7's bottom edge implies a barrel coefficient of **k = −0.00646**
> and its right edge **k = −0.06259**, **163 % apart**. No single radial term produces both,
> so this is **not** simple radial lens distortion and the verdict returns to **CANNOT
> DETERMINE**. "Both edges bow away from the centre" is necessary for radial distortion and
> nowhere near sufficient — it has two outcomes and one is 50 % likely by chance. The
> measurements of the individual edges below are unaffected and still stand; only the
> conclusion drawn from them is withdrawn.


*halo Replica, lane L2, 2026-09-05. New instrument: `tools/c_distortion.py`.*

> **SIDE CONVENTION. FRONT = the COMPONENT side** (Apple's FCC caption "MLB – Front").

R11 found a smooth, spatially coherent misfit in the registration between the FCC
photographs and O'Flynn's, on **both** faces, and left three causes open: a board that is
not flat, **uncorrected lens distortion**, or a difference between two physically different
boards. Adding free parameters did not separate them — `poly2` came out 3.8× worse.

One of the three can be measured **without touching the board**, because the FCC frames
contain steel rules, and **a steel rule's edge is straight by construction.** A straight
edge that images curved is the lens.

## Measured

| edge | span | line-fit resid sd | **sagitta** | null (positions permuted) | z | reading |
|---|---|---|---|---|---|---|
| photo6-bottom | 1596 px | 2.954 px | 1.415 px | 0.162 ± 0.120 | +2.6 | **CANNOT DETERMINE** |
| photo6-right | 799 px | 5.988 px | 0.952 px | 0.198 ± 0.146 | +0.8 | **CANNOT DETERMINE** |
| **photo7-bottom** | 1596 px | 3.442 px | **1.137 px** | 0.078 ± 0.059 | **+5.1** | **MEASURED** |
| **photo7-right** | 799 px | 5.855 px | **4.310 px** | 0.236 ± 0.176 | **+6.6** | **MEASURED** |

**RADIAL CONSISTENCY, photo 7: both edges bow AWAY from the frame centre → BARREL, and it
is consistent with a single radial centre.** The bottom rule's top edge lies below the
centre and the right rule's left edge lies right of it; under barrel both depart outward,
and both do.

**Photo 6 — the FRONT face's scale donor — cannot confirm it.** Neither of its rule edges
stands clear of its own null. That is CANNOT DETERMINE, not "photo 6 is undistorted": its
edges are noisier (line-fit residual sd up to 5.99 px) and the Apple watermark crosses
them. Photo 6 and photo 7 are the same exhibit and very likely the same camera, but this
lane does not measure "very likely".

## What this does and does not settle

**Settles:** the FCC frames carry real optical distortion, so R11's candidate 2 is not
hypothetical. On the BACK pair, where the scale donor is photo 7, a barrel-distorted target
frame is a sufficient explanation for a smooth coherent registration misfit, and no
appeal to a bowed board or a different board build is needed to explain it.

**Does not settle:** how much of the misfit it accounts for. That needs the distortion
*undone* and the registration re-run — the sagitta here is 1–4 px over the rule's span,
while the registration residual is 1.4–2.0 px over the board's much smaller span, so the
two are not directly comparable and this file does not compare them.

**Does not settle anything for the FRONT.** Photo 6 is CANNOT DETERMINE.

## Honesty about the noise

The straight-line residual sd is **2.95–5.99 px**, larger than three of the four sagittas.
The quadratic term is nonetheless well determined because there are 747–1594 samples: a
systematic curvature is estimable far below the per-sample scatter. But it means these
edges are **not clean steps** — scratches, the rule's bevel, the watermark — and a reader
should treat the sagitta as a mean curvature, not as a profile.

## The control was WRONG on its first run, and that is the finding under the finding

The radial-consistency test originally demanded **opposite** signs from the two edges and
duly reported *"NOT consistent with a single radial centre — so whatever is bowing these
edges is not simple radial distortion."*

That verdict was backwards. Under barrel distortion a straight line bows **away from the
image centre**; the bottom edge is below the centre and the right edge is right of it, so
both depart in the **same** sense in image coordinates. Requiring them to differ inverted
the answer and would have buried a clean positive result as a null.

It was caught by re-deriving the geometry rather than by any test, which is exactly the
weakness. The logic is now a separate function with **four selftest cases** — barrel read
as barrel, pincushion as pincushion, the control firing on genuinely inconsistent edges,
and an edge on the far side of the centre flipping correctly. A control that has never been
exercised is how a backwards one survives to be printed.

## Two other defects fixed on the way, both found by controls

- **The smoothing manufactured a fake edge at every box boundary.** `np.convolve(mode='same')`
  zero-pads, which puts a large gradient at both ends of every column — a false edge exactly
  where a real one is hardest to see. Caught by the blank-field case, which discarded all
  800 samples as `on_box_boundary` instead of `weak_gradient`. Now padded by replication.
- **The synthetic edge I was grading against was itself bent.** The fixture set the partial
  pixel to `40(1−f) + 200f`, the anti-aliasing blend **inverted**. The bias is sub-pixel but
  varies with `f`, and `f` varies systematically along a bowed edge, so a known 4.0 px bow
  read as 3.07 px while 1.0 px read as 1.02. Replaced with a coverage model: 4.0 px now
  reads **4.004 px**. *The tool was right; the ruler I was grading it against was bent.*

## Instrument

`tools/c_distortion.py` — `doctor` (canary: a known 2.50 px bow read back as 2.493 px),
`selftest` (**10/10**), `edge`. Exit code is the verdict.

```
tools/c_distortion.py doctor
tools/c_distortion.py selftest
tools/c_distortion.py edge --json-out metrology/compside/R14-lens-distortion-from-rule-edges.json
```

## Next

Undistort photo 7 with the measured barrel term, re-run the BACK registration, and see
whether the 1.026 mm hold-out falls. If it does, the misfit was the lens and the board is
exonerated. If it does not, a bowed board or a build difference is back in play — and that
would be worth knowing, because it is the only one of the three that a caliper could settle.
