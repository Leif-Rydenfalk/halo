# M08 — the dark packages, the nRF52832 control, and the UWB can

*halo Replica, L1 PHOTOGRAPH METROLOGY lane, 2026-09-05.*

**SIDE NAMING:** FRONT = the COMPONENT side. O'Flynn's `backside-fullres.jpeg` **is** it.

**Reproduce:** `tools/m_dark_packages.py control` (exit 0) then
`tools/m_dark_packages.py run --png … --json metrology/dark-packages-front.json`.

---

## 1. THE POSITIVE CONTROL PASSES, AND IT VALIDATES THE SCALE TOO

nRF52832-CIAA, published body **2.956 × 3.226 mm** — Nordic PS v1.4, Table 132,
p.541, *fetched* by lane L3, not recalled. A dark package, in this photograph, at
this noise, with a truth value that came from a datasheet rather than from me.

| | long | short | aspect |
|---|---|---|---|
| published | 3.226 mm | 2.956 mm | 1.0913 |
| **measured** | **3.218 mm** | **2.940 mm** | **1.0947** |
| **error** | **−0.23 %** | **−0.54 %** | **+0.31 %** |

The candidate was chosen as **the most rectangular** in the search box — not the
biggest, and *not the closest to the published size*, which would have made the
control agree with itself.

### It is also an independent check on the scale, and the scale survives

Reaching that size uses the **registration-derived** 106.313 px/mm. Making the
nRF *exactly* its published size would need **106.06 px/mm** — **0.23 %** away.

> **Two entirely unrelated routes agree to 0.23 %:** a steel rule in a *different
> photograph* carried through a homography, and a package dimension from a
> datasheet. Neither is fitted to the other.

**L3's nRF-derived 110.3 px/mm is the outlier at +3.9 %** against both. On the
evidence here the registration scale stands and L3's should be re-derived.

### Three deliberate breaks, all seen to go red

- remove the colour criterion → the package **merges into the board**: the blob
  fills **100.0 %** of the ROI against the control's 82.9 %
- an impossible fill requirement (> 1.0) → **0 found**
- an empty mask → **0 found**

## 2. THE DETECTOR GOT THERE BY FAILING THREE TIMES, AND ATTEMPT 3 IS THE WARNING

| attempt | outcome |
|---|---|
| dark + smooth + rectangular | **FAILED** — bare soldermask is also dark and smooth; the package merged with it and nothing survived the fill gate |
| "darker than its local surround" (black top-hat) | **FAILED** — large dark stretches of board connect into a single **1.76 Mpx** blob spanning the whole board |
| **a stated ROI with Otsu inside it** | **FAILED, AND INSTRUCTIVELY** — see below |
| **colour (B−R)** | **WORKS** — the nRF's epoxy is blue: **B−R = +43** against a board median of **+1** |

**Attempt 3 returns an answer, and the answer is the box.** Padding the ROI by
0, 20, 40, 60 px gives **3.35, 3.98, 4.09, 4.50 mm** for the same package — a
**34 % swing driven entirely by my choice of box** — and the blob touches the ROI
edge at every padding. That is M01's *"394 px was the crop frame"* in a new
costume: **a number that looks like a measurement of the board and is a
measurement of the operator.**

## 3. What was found — 5 packages, all located AND sized

| x mm | y mm | r mm | θ° | long | short | area mm² | fill | short in genuine px |
|---|---|---|---|---|---|---|---|---|
| −3.037 | −8.667 | 9.184 | 250.7 | 3.283 | 3.030 | 9.951 | **1.000** | 62.7–83.0 |
| 1.538 | −8.594 | 8.731 | 280.1 | 3.449 | 0.841 | 2.251 | 0.776 | 17.4–23.0 |
| −9.079 | 2.949 | 9.546 | 162.0 | 1.181 | 0.906 | 1.068 | 0.998 | 18.7–24.8 |
| −6.869 | −2.538 | 7.323 | 200.3 | 0.952 | 0.938 | 0.711 | 0.797 | 19.4–25.7 |
| −1.001 | −12.555 | 12.595 | 265.4 | 1.528 | 0.513 | 0.595 | 0.759 | 10.6–14.0 |

All five clear the 10-genuine-pixel bar, unlike 63 of the 95 bright features in
M07. **A ~2 % honesty note:** the whole-board `run` measures the nRF at
3.283 × 3.030 mm while the ROI-restricted `control` measures it at
3.218 × 2.940 mm. Same part, two segmentations, **2 % apart** — that spread is
the real uncertainty and the control's −0.23 % should not be read as this
method's accuracy everywhere.

## 4. WHAT THIS DETECTOR CANNOT DO

**Neutral-black packages remain CANNOT DETERMINE.** The large black package at
9 o'clock has **B−R = +0.5** against the board's +1 — it is invisible to a colour
criterion, and attempts 1–3 above are why nothing else worked. The evidence that
this is the *photograph* and not the effort is attempt 3's ROI table.

## 5. THE UWB CAN — L3's puzzle resolves, and it was a clipped box

**Disclosure: I was told L3's figure (6.16 × 3.37 mm = 20.8 mm²) before I
measured. I could not measure blind, and the reader should discount accordingly.**

| ROI pad | long | short | L×W | filled area | touches ROI edge |
|---|---|---|---|---|---|
| 0 | 6.735 | 3.560 | 23.98 | 19.13 | no |
| 25 | 7.144 | 3.595 | 25.68 | 20.41 | no |
| 50 | 7.463 | 3.625 | 27.06 | 21.46 | no |
| 75 | 7.683 | 3.641 | 27.97 | 22.26 | no |
| 100 | 7.891 | 3.665 | 28.92 | 22.87 | no |

- **short side 3.56–3.67 mm — STABLE (2.9 %) and MEASURED**
- **long side 6.74–7.89 mm — 15.6 %, CANNOT DETERMINE**; 6.735 mm is a lower
  bound from the least-inclusive ROI
- **bounding rectangle 23.98–28.92 mm²**

> **L3's coincidence was an artifact of a clipped box.** TechInsights' U1 **die**
> is 20.58 mm², and a SiP module must exceed its die. L3's 20.8 mm² sat 1 %
> above it, which is impossible for a real module. **My bounding rectangle is
> 24–29 mm², comfortably above the die** — and my short side is 5.6–8.9 % larger
> than L3's, my long side at least 9.4 % larger, both in the direction that
> resolves it. The near-equality with the die area was not meaningful; it was a
> box that stopped short.

## 6. AUDIT — what already published inherits the rule's scale rather than the board's

M07 found `c_register`'s default basis is **1.29 % high**. Grepping for it:

| file | carries |
|---|---|
| `metrology/compside/R00-DATUM-TRANSFER.md` | **107.686 px/mm** — the uncorrected transferred scale |
| `metrology/compside/R01,R02,R03-*.json` | `px_per_mm 15.887545…` |
| `board/HANDOFF.md` | `--px-per-mm 15.887545712881764`, and credits it as L1's scale |
| `evidence/E01-ARE-THE-ANTENNAS-ON-THE-BOARD.md` | "L1 calibrated that photograph … **15.8875 px/mm**" |
| `metrology/board-outline-photo6.json`, `ellipse-test.json` | `px_per_mm 15.8875` |

**Every millimetre in those is 1.29 % small.** M02's own tables legitimately quote
15.8875 as *the bottom rule's measured value* and are not wrong. Routed to the
orchestrator rather than edited here — `compside/`, `board/` and `evidence/`
belong to other lanes.

## 7. Status

| # | quantity | verdict |
|---|---|---|
| 1 | nRF52832 body size | **MEASURED**, −0.23 % / −0.54 % against the datasheet |
| 2 | registration scale, independently checked | **CONFIRMED** to 0.23 % by the datasheet route |
| 3 | L3's 110.3 px/mm | **OUTLIER**, +3.9 % against two agreeing routes |
| 4 | blue-bodied package positions and sizes | **MEASURED**, 5 parts, all ≥ 10 genuine px |
| 5 | neutral-black package extents | **CANNOT DETERMINE** — colour cannot see them, and attempts 1–3 failed |
| 6 | UWB can short side | **MEASURED** 3.56–3.67 mm |
| 7 | UWB can long side | **CANNOT DETERMINE** — 15.6 % ROI-dependent; ≥ 6.735 mm |
| 8 | L3's can ≈ die-area coincidence | **RESOLVED** — a clipped box, not a coincidence |
