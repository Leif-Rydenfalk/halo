# L5 BOARD BUILD — handoff, 2026-09-05 (stood down at fleet quota RED)

**FRONT = COMPONENT SIDE** (Apple FCC caption "MLB - Front"). O'Flynn's "frontside" is
this project's BACK. State this at the top of every file you add here.

## What exists and works

| file | what it is | verdict |
|---|---|---|
| `board/board.json` | the parameterised board. ONE scale parameter; the shape is a normalised profile. No diameter is hard-coded in any tool. | on disk |
| `board/outline/outline-photo6.json` | RAW measured silhouette off FCC photo 6, outer + centre hole, r(theta) in mm, 1440 rays | evidence — **never merge a fit into this file** |
| `board/out/board-front.png` | the render | PASS |
| `board/out/compare-front.png` | **the side-by-side: OURS \| APPLE'S \| OVERLAY** | PASS |
| `tools/p_outline.py` | photo → silhouette in mm, or refuse | exit 0/1/2 |
| `tools/p_render.py` | board.json → picture | exit 0/1/2 |
| `tools/p_compare.py` | the comparison harness | exit 0/1/2 |

```bash
python3 tools/p_outline.py ../../images/airtag/fcc-BCGA2187-internal-photo-6.jpg \
  --box 660 400 1250 960 --px-per-mm 15.887545712881764 \
  --scale-basis "photo6 bottom steel rule (L1 scale-field.json)" \
  --json-out board/outline/outline-photo6.json
python3 tools/p_render.py
python3 tools/p_compare.py && open board/out/compare-front.png
```

## Numbers, each with its input

Scale basis for every millimetre below: **photo6 BOTTOM steel rule, 93 mm ticks, linear
fit resid sd 0.573 px, 15.8875 px/mm** (L1 `metrology/scale-field.json`). Perspective
error between the rule plane and the board top face is **NOT bounded by that residual**.

- **outer, 2 × mean radius = 24.984 mm — PROVISIONAL AND IN DISPUTE.** O'Flynn's
  "~26 mm" is his tilde; L1's ruler work suggests ~24.6; this is 24.98. Three numbers,
  no agreement, not settled.
- **centre hole roundness r_max/r_min = 1.380** (1.000 = circle, 1.414 = square). It is
  a rounded square with a notch at top centre. **This lane publishes no hole diameter.**
- **hole centre offset from board centroid: (+0.173, +0.458) mm** — the hole is not
  concentric.
- **inner mean r / outer mean r = 0.5367**, annulus mean width 5.787 mm. Ratios do not
  inherit the scale; the millimetres do.
- **overlay residual, ours vs Apple's own silhouette: RMS 0.281 mm, p95 0.417 mm,
  max 1.594 mm over 720 rays.** Panel-scale agreement 0.66%.
- **44.2° of outer arc is INTERPOLATED** across rays that crossed Apple's orange leader
  arrows. Those arcs are drawn in the provisional colour, so the picture says where it
  is guessing.

## Item 1 — THE THING TO FIX NEXT, and it is the only one that matters

**The outline is a per-degree silhouette and it carries the edge detector's noise into
the geometry.** Apple's board is a *manufactured* outline — routed or punched: circular
arcs, straight segments, corner fillets. It does not have a bumpy edge. Two consequences,
both fatal:

1. Beside Apple's crisp machined ring, a noisy blob reads as "not even close" **for
   reasons unrelated to our dimensions** — and that comparison is the test Leif applies.
2. A per-degree polygon from noisy data **cannot be dimensioned, toleranced, or made.**

**Fit geometric primitives to the measured profile and draw the fit, not the samples.
Publish the fit residual — it is worth more than the raw profile, because it says how
well a manufacturable shape describes what was photographed. Keep the raw profile on
disk as evidence. Never merge the two files.**

Groundwork already measured, so you do not repeat it:

- **A plain circle is a poor model of the outer edge and here is the proof:**
  robust circle fit gives R = 12.5503 mm, centre offset (+0.122, −0.277) mm,
  **residual sd 0.402 mm, max 1.334 mm, and only 49.0% of rays within ±0.15 mm.**
  Inlier fraction is the discriminator here, not residual — a fit chooses the inliers
  that make its own residual small, so residual can agree with what it checks.
- **The outer edge deviates from that circle over these arcs** (|res| > 0.20 mm), which
  are the candidate straight segments / notches to model explicitly:
  `0–22°, 25.8–31°, 85.2–91.2°, 126.8–155.5°, 157.3–201.5°, 261.8–302.5°, 345.5–356.2°`.
- **Circle fitted to the centre hole — the deliberately WRONG model, kept for contrast:**
  R = 6.7050 mm, residual sd 0.365 mm, max 1.179 mm. Any rounded-rectangle fit must beat
  this by a wide margin or it has not earned the extra parameters.

Proposed model, manufacturable and dimensionable: outer = circle + explicit chords/notch
features on the arcs above; inner = rounded rectangle (w, h, corner radius, rotation)
plus one explicit notch feature at top centre. **The check that would catch a fit that
merely improved rather than described: the rounded-rectangle fit must beat the circle
fit's residual AND its inlier fraction must separate cleanly, the way boardmetro's square
vs ring test does.** "The residual went down" is not evidence the model is right — extra
parameters always lower a residual. That is the same trap L4's layer-count check fell
into when copper grew while the dielectric had stopped.

## Item 2 — the layer count changed under this lane, mid-session

The brief said 4 layers was a *stated replica choice* against Apple's true count being
CANNOT DETERMINE in {4, 6}. **Commit `e84ffea` supersedes that: 4 layers, COUNTED,
confidence HIGH**, from a published delayering. `board.json` is updated.
**`board/out/board-front.png` still carries the old caption "STATED REPLICA CHOICE, not
Apple's fact" and is therefore now wrong on that one line — re-run `p_render.py` and
`p_compare.py` first thing.** Thickness 0.30 mm as-drawn is unchanged, and the fab-floor
delta (below PCBWay's and JLCPCB's 0.40 mm) stays a separate fact about us.

## Not yet drawn at all

Rim pads (the antenna carrier's solder pads — three antennas are **not** on this board,
`evidence/E01`), component footprints, silkscreen, copper, the U1 footprint that must be
placed UNPOPULATED **and say so in board legend, not only in a document**. The NFC coil
is wound magnet wire (ID 9.380 / OD 10.834 mm), not a trace: it is not copper on this
board.

## Controls, and each one was watched to go red on purpose

An assertion never seen to fail is not known to work.

| control | fired by | verdict seen |
|---|---|---|
| C1 clip — board touches the crop box | `--box 780 500 1120 840` | exit 1 FAIL |
| C2 bimodality — histogram not two-humped | bare-background patch | CANNOT DETERMINE |
| C3 annotation mask | 200/1440 outer rays discarded and named | reported, not averaged in |
| C4 negative — must find nothing | on bare paper → PASS; **on a ruler patch → exit 1 FAIL** | both seen |
| C5 hole enclosed | — | not yet fired; a solid disc would fire it |
| R1 non-blank, read back off disk | — | not yet fired |
| R2 annulus, not a filled disc | — | not yet fired |
| R3 scale | `--break-scale 1.10` → 9.80% | exit 1 FAIL |
| missing `--scale-basis` | — | exit 2 CANNOT DETERMINE |

**R3 is the one worth copying.** The picture is drawn at `ppm`, and the control measures
it at the px/mm *the caller asked for*. Those two deliberately do not share the broken
number. Feeding the same wrong scale to both sides cancels and passes a broken build —
which is exactly what happened the first time it was written.

**Still owed, and it is a real gap:** `p_compare.py --break-rotation` exists and is
documented as control X3 (rotate our outline, the residual must get worse) but **it has
not been run, so X3 is a claim, not a control.** Run it before trusting the RMS number.

## What was discarded, and why

- **No circle is fitted to the centre hole anywhere in this lane.** A circle there
  returns a small clean residual while being the wrong shape, and a number that looks
  well-measured is more dangerous than one that is merely imprecise.
- **L1's `board-outline-photo6.json` inner profile was not used.** It reports
  r_min 73 px against r_max 172 px — a 2.34× excursion where a rounded square gives at
  most 1.41× — so it is contaminated. This lane re-extracted the profile rather than
  inherit it. L1's *scale* (15.8875 px/mm) is used and credited.
- **Bounding-box extent was discarded as the scale check.** For a non-circular outline
  that compares a max against a mean. R3 measures 2 × mean radius, the same operator
  that defines the parameter.
- **The half-scale whole-frame view was discarded for measurement** and kept only for
  looking; every number comes from the full-resolution file.

## The lesson this lane was handed and should keep

From the halo lane, after it withdrew its own coil finding: **when you claim two
measurements corroborate, name what each would have had to SEE to disagree. If you
cannot name it, they are one measurement.** Nothing in this handoff is claimed as
corroborated — the outer diameter has three disagreeing sources and is labelled in
dispute everywhere it appears, including on the picture.
