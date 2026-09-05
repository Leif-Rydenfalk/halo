# M06 — what each source photograph actually resolves, per millimetre of board

*halo Replica, L1 PHOTOGRAPH METROLOGY lane, 2026-09-05. Extends M04 from one
photograph to all of them. **This is the gate for L2, L3 and L5.***

**SIDE NAMING:** FRONT = the **component** side (Apple's FCC caption). Note the
consequence for O'Flynn's filenames: **O'Flynn's `backside` (nRF52832, crystal,
UWB can) is this project's FRONT**, and his `frontside` (NFC coil, battery
contacts) is this project's **BACK**.

**Reproduce:** `tools/m_resolution_probe.py --image <f> --box <x0,y0,x1,y1>`.
Raw results in `metrology/respro-*.json`.

---

## The number that matters is GENUINE PIXELS ACROSS THE BOARD

A file's pixel count is not its information. `m_resolution_probe.py` measures how
far real detail reaches as a fraction of each image's own Nyquist, calibrated
against the same region deliberately destroyed to 1/2, 1/3, 1/4 and 1/6. Multiply
that fraction by **the board's span in that image** — not by the file width — and
you get the only figure the other lanes can act on.

| source | side | file | board span | rolloff | **genuine px across the board** | **genuine px/mm** |
|---|---|---|---|---|---|---|
| `oflynn-frontside-fullres` (right region) | **BACK** | 2347×2344 | 1924 px | 0.570 | **1097** | **≈ 42** |
| `oflynn-frontside-fullres` (upper-left) | **BACK** | 2347×2344 | 1924 px | 0.445 | **856** | ≈ 33 |
| `oflynn-backside-fullres` (left annulus) | **FRONT** | 2916×3412 | 2672 px | 0.258 | **689** | ≈ 27 |
| `oflynn-backside-fullres` (top-right annulus) | **FRONT** | 2916×3412 | 2672 px | 0.195 | **521** | ≈ 20 |
| `oflynn-frontside-26mm-cropped` (M01's datum) | **BACK** | 788×788 | 787 px | 0.398 | **313** | ≈ 12 |
| `fcc-…-photo-6` board | **FRONT** | 2134×1600 | 412 px | 0.289 | **119** | **≈ 4.6** |
| `fcc-…-photo-7` board | **BACK** | 2134×1600 | 392 px | 0.273 | **107** | ≈ 4.1 |
| `fcc-…-photo-6` steel rule *(within-image control)* | — | 2134×1600 | — | 0.383 | — | — |

*(genuine px/mm assumes a 26 mm board; see M02 for that bound)*

## What this unblocks, and what it caps

> **O'Flynn's full-resolution photographs carry 5 to 9 times more genuine detail
> across the board than the FCC internal photos.** ≈ 20–42 genuine px/mm against
> the FCC's ≈ 4–4.6.

- **L2's component positions and L3's package sizing are SAFE to run on
  O'Flynn's full-res images.** At 20–42 genuine px/mm, an 0402 package (1.0 ×
  0.5 mm) is 20–42 px on its long side. L2's held-out error of 0.1029 mm is
  ≈ 2–4 genuine pixels — demanding, but not below the source's resolution, so it
  is a real number rather than one measuring its own softness.
- **Prefer the BACK image (`oflynn-frontside-fullres`) WHERE A CHOICE EXISTS**:
  it measures 0.445–0.570 of Nyquist against the FRONT image's 0.195–0.258,
  despite having *fewer* pixels. More pixels is not more information.

  > ### ⚠ AND FOR COMPONENT WORK THERE IS NO CHOICE — read this before acting on the line above
  >
  > **The components are on the project FRONT, and the FRONT is imaged by
  > `oflynn-backside-fullres` — the SOFTER source, at 0.195–0.258 and ≈20–27
  > genuine px/mm.** The sharper image, `oflynn-frontside-fullres`, shows the
  > battery-contact and coil face: the side with almost nothing to locate.
  > **The better picture is of the emptier face.**
  >
  > So component metrology is capped at **≈20–27 genuine px/mm** and cannot be
  > improved by choosing a different photograph. "Prefer the BACK image" applies
  > only where a lane genuinely has both options, and component positioning does
  > not. Read without this caveat it sends someone to measure components in a
  > photograph that does not show them.
- **PACKAGE SIZING BY RATIO — the boundary, as a number rather than discovered
  per line.** At the 20–27 genuine px/mm that the component face actually offers:

  | package | nominal | long side | short side | verdict |
  |---|---|---|---|---|
  | 0402 | 1.0 × 0.5 mm | **20–27 px** | 10–14 px | **SOUND** |
  | 0201 | 0.6 × 0.3 mm | **12–16 px** | **6–8 px** | **MARGINAL — do not discriminate package size on a 6-pixel width** |

  **The AirTag uses 0201s.** So sizing unmarked parts by ratio against a known
  package is sound for **0402 and larger** and marginal below it. L3's nRF52832
  ruler sits comfortably in the sound region — its 0.4 % aspect agreement against
  the datasheet says that segmentation is real — but the same method applied to
  an 0201 is resting on 6–8 px, and a BOM line derived that way must say so.

- **Position uncertainty must be quoted in GENUINE pixels as well as
  millimetres.** L2's transform validates to 0.1029 mm on held-out spatial folds,
  which at 20–27 genuine px/mm is **2–4 genuine pixels**. That is a real number
  and it is also the floor: do not push the transform finer, and **a position
  quoted to 0.01 mm off this source has three digits of decoration on it.**

- **Do not use the FCC photos for anything smaller than ~1 mm.** At 4.6 genuine
  px/mm a 1 mm feature is under 5 px. That is M03/M05's rim-pad CANNOT DETERMINE
  restated as a number, and it is why M02's px/mm (measured on the *steel rule*,
  the sharpest content in frame) is solid while the rim count was never going to be.
- **M01's datum crop resolves ≈ 12 genuine px/mm** — fine for the scale fit it
  was used for, marginal for anything finer.

## WHAT I DISCARDED — a "SHARP" reading that was the BACKGROUND

The first pass on `oflynn-backside-fullres` sampled (900,1100)–(1700,1900) and
returned **0.992 of Nyquist — "SHARP: essentially to the file's own limit"**. It
was nearly published as the headline.

**That region is mostly not the board.** The board there spans x 416–2832,
y 1160–3168, so the box sat largely on the background. Its luma sd was 36 against
64–66 for the on-board regions: **a low-contrast field of fine-grained sensor and
JPEG noise, which is exactly what a resolution probe rewards.** Noise is
broadband; it reaches Nyquist by definition and resolves nothing.

On-board regions of the same file measure **0.195–0.258** — the file is
*softer* than the FCC photo per pixel, and only wins because the board fills the
frame. **A resolution probe measures the content it is pointed at, not the
camera.** Every row in the table above names its region for that reason, and the
region's luma sd is in the JSON.

## And a verdict rule keyed to the wrong thing

`m_resolution_probe.py` first bucketed its verdict on *"the first ladder step
that costs detail"*. That step is ≥2 even for a perfectly sharp image, so the
tool labelled the 0.992 reading **"ALREADY SOFT / UPSAMPLED"** — the opposite of
what it had measured. **`k_first` says where detail stops being free to throw
away; it does not say how much there is.** The verdict now keys off the as-held
rolloff. This is the *second* verdict-logic defect in this one tool (M04 §4 has
the first, where a monotonic-ordering assumption was smuggled into the verdict
rather than being part of the physics), and both had the same shape: **the
measurement was right and the sentence printed over it was not.**

## Status

| # | quantity | verdict |
|---|---|---|
| 1 | genuine px/mm of every candidate source | **MEASURED**, table above |
| 2 | are O'Flynn's images good enough for L2/L3/L5 | **YES** — 20–42 genuine px/mm |
| 3 | which O'Flynn image is sharper | **the BACK one** (`oflynn-frontside-fullres`), despite fewer pixels |
| 4 | are the FCC photos good enough for sub-mm features | **NO** — ≈ 4–4.6 genuine px/mm |
| 5 | rolloff as an absolute camera property | **it is not** — it measures the content sampled; every figure names its region |
