# HANDOFF — L3 (BOM identification), halted mid-measurement 2026-09-05

Stopped by a fleet quota stand-down, not by a finished work item. Everything below is
committed. **Read `bom/BOM-RECONSTRUCTED.md` first; it is generated from `bom/bom.json`,
which is the source of truth. Never hand-edit the markdown.**

Side convention throughout: **FRONT = the component side** (Apple's FCC filing). O'Flynn's
`backside-*` files show Apple's FRONT.

## The tools, and run them before you trust them

| tool | what | controls |
|---|---|---|
| `tools/b_bom_check.py` | six rules over `bom.json`; exit 0/1/2 | `--self-test` breaks every rule on purpose, 7/7 fire, plus a negative control that a clean line yields nothing. It caught two real dangling citations on its first run against live data. |
| `tools/b_pkgsize.py` | package outline off a photograph, in pixels | `--self-test` 10/10. Every control watched firing: box-clip, flat box, noise-only box, a neighbour that must not join the component, and a colour case where luminance provably cannot see the part. |
| `tools/b_bom_render.py` | `bom.json` → `BOM-RECONSTRUCTED.md` | none needed; it is a projection |
| `tools/b_crop.py` | Lanczos-only crop/upscale, plus `grid()` which burns SOURCE pixel coordinates into the picture so a human can hand a correct `--box` back | no sharpening, no contrast stretch: what is read off a crop is what is in the photograph |

Two defects `b_pkgsize` found in itself, both worth knowing before you extend it:

1. **PCA is wrong for a square.** The first version took principal axes; on a 150×150 square
   rotated 31° the covariance is degenerate, the axes came out arbitrary and it reported
   **206×206**. Minimum-area rotated rectangle over the convex hull instead. Selftest case 2.
2. **Otsu separability does not catch texture.** On pure Gaussian noise Otsu scores **0.64**,
   above any sane floor, because splitting a unimodal distribution at its mean always looks
   separable. The gate that works is **rectangularity** — a package fills its own bounding
   rectangle (rectangle 1.00, round connector π/4 = 0.79), a noise blob does not. Selftest
   case 6, and it went red before it went green.

## The ruler — use this one, do not invent another

`U1`, the nRF52832-CIAA WLCSP, body **2.956 × 3.226 mm** nominal (Nordic nRF52832 PS v1.4,
Table 132, p.541), measured at **355.1 × 326.6 px** in `oflynn-backside-fullres.jpeg` →
**110.3 px/mm**, local to the nRF's neighbourhood.

**Why this is a measurement and not an assumption:** the measured aspect 1.087 lands within
**0.4 %** of the published aspect 1.0914, and nothing was fitted to make it — the
segmentation knew nothing about the datasheet. It corroborates the part identification and
validates the segmentation in one step.

**What it cannot remove:** `IMG-BACK` is a strongly perspective photograph; the board images
about **14 % wider one way than the other**, so parts far from the nRF inherit up to roughly
that much anisotropic error. Aspect ratios are the robust output. Absolute millimetres at
the far rim are not.

## Measured (8 parts)

| ref | px | mm | aspect | trust |
|---|---|---|---|---|
| U1 nRF52832 | 355.1 × 326.6 | 3.226 × 2.956 | 1.087 | it IS the ruler |
| X2 `A048L` | 179.3 × 115.4 | 1.626 × 1.046 | 1.554 | good |
| metal-lid A (by the `TPS746` legend) | 242.2 × 199.3 | 2.196 × 1.807 | 1.215 | good |
| metal-lid B (mid-left) | 177.1 × 136.9 | 1.606 × 1.241 | 1.293 | good |
| U2 UWB can | 679.4 × 371.8 | 6.16 × 3.37 | 1.827 | **millimetres LOW trust** — far rim |
| CT1 blue `6X A75` | 90.5 × 90.4 | 0.82 × 0.82 | 1.001 | **suspect, do not quote** |

### The one result that changes a conclusion

**Neither metal-lid part is square, and a BMA280 is.** 2.0 × 2.0 mm LGA against measured
aspects of 1.215 and 1.293. Perspective alone could stretch a square to about 1.14, so 1.215
is arguably within reach and 1.293 is not comfortably so; lid B at **1.61 × 1.24 mm** is too
small to be a BMA280 at all. This is a check that *could have agreed and did not*. It does
not refute an accelerometer being on the board — it refutes the idea that anyone in this
project has pointed at it. `U4`'s confidence is now CANNOT DETERMINE for *which* part.

### The one number to re-measure before anyone repeats it

`U2` at 6.16 × 3.37 mm = **20.8 mm²**, suspiciously equal to the **20.58 mm²** TechInsights
report for the U1 **die**. A SiP module must be larger than its die, so either the
coincidence is meaningless or the box captured less than the whole can. **Do not repeat this
number without re-measuring it.**

## Where it stopped — the next four commands

These boxes are wrong in a *known* way: `b_pkgsize`'s edge control fired on each, which means
the box clipped the part. Widen and re-run. Image is
`../../images/airtag/oflynn-backside-fullres.jpeg` throughout.

```bash
# X1 T320/RBEV — the one that TESTS Catley's 32 MHz vs 32.768 kHz assignment
tools/b_pkgsize.py $B --box 780 920 1130 1210 --pick bright --label "X1 T320"
# UNK-A, the large unmarked matte-black rectangle — the highest-value measurement left
tools/b_pkgsize.py $B --box 350 1210 800 1640 --pick dark  --label "UNK-A"
# U9 1A8/1950
tools/b_pkgsize.py $B --box 550 1570 780 1840 --pick dark  --label "U9"
# L1x wirewound inductor
tools/b_pkgsize.py $B --box 850 550 1090 740  --pick bright --label "L1x"
```

`J1`, the coaxial connector, returned CANNOT DETERMINE — a U.FL is a bright ring on a bright
pad field and there is no single component to isolate. It needs a different approach (fit the
outer shell as a circle with `bin/boardmetro circle`, which already exists — do not rebuild).

### What each of those would settle

- **X1 vs X2 is a real test with a possible FAIL.** X2 `A048L` measures **1.626 × 1.046 mm,
  aspect 1.554**. If X1 `T320` comes back squarer and larger, that is consistent with
  Catley's assignment (a 32 MHz AT-cut part in a squarer package, a 32.768 kHz tuning-fork
  part in a long narrow one). If it comes back *longer and narrower than X2*, Catley's
  assignment is contradicted and the two frequencies swap. Nobody has ever tested this.
- **UNK-A is the only measurement left that could CLOSE a gap rather than describe one.**
  Size it against the published body sizes of the four parts nobody can point at — U3 flash,
  U5 amp, U7 op-amp, U8 load switch. Hold O'Flynn's own words in mind while you do: he
  describes cutting through *"the black plastic"* to reach the SPI flash, so a matte black
  rectangle on this board might be the antenna carrier and not a package at all. Confusing a
  carrier for an IC would be exactly the error this document exists to prevent.

## Open, and not mine to close alone

- **Is the front coil the NFC antenna or the voice coil?** Raised here, acted on in
  `evidence/E02-THE-COIL-CORRECTION.md`. The sub-ohm resistance argument favours the NFC
  loop but rests on a lower-bound turn count. Settled by a DC resistance across TP1/TP38 on a
  live unit, or a photograph of the front dome's inner face.
- **Are ANT1 and ANT3 on the carrier or on the board?** O'Flynn is primary and verbatim —
  *"The plastic part includes the various antennas which are printed onto it."* My reading is
  that Apple's FCC-6 arrows point at the antenna FEED region on the rim, not at the
  radiators. That is a reading, not a measurement. **Do not tell anyone the LDS gap has
  closed on the strength of it.**
- **Board diameter.** At 110.3 px/mm the board's least-foreshortened extent in IMG-BACK works
  out near **25 mm**, not 26 — a rough frame extent, not a fitted outline, and outline is
  L1's item. Recorded only because a datasheet package on one photograph and a steel ruler on
  a different photograph both land **below 26**. Two methods, two photographs, same direction.
