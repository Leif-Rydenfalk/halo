> **⚠ TWO DIFFERENT BOARDS — an unstated systematic under every millimetre here (L9, 2026-09-05).**
> The FCC photographs show **920-08283-01, data code 3119** — a **2019 engineering build**.
> O'Flynn's show **820-01736-A, data code 2920 17** — **2020 production**. Every scale in this
> lane is transferred from one to the other. **A uniform dimensional difference between two
> different boards is absorbed into the fitted scale and leaves the held-out residual COMPLETELY
> unchanged**, because the check divides both sides by the same number. This applies to the
> Replica's 106.313 px/mm and therefore to every absolute millimetre downstream of it.
> **CANNOT DETERMINE here.** A caliper on one board of each part number settles it.

# M01 — the scale basis, and the first four measurements

*halo Replica lane, 2026-09-05. Every number below names the photograph it came from
and the scale basis used. A number without those is not a measurement and is not here.*

**Reproduce any of this with:** `tools/calib_fit.py`, `tools/measure_outline.py`,
`tools/measure_coil.py`. Raw results in `metrology/*.json`.

---

> **⚠ §3 IS PARTLY SUPERSEDED — read `evidence/E02-THE-COIL-CORRECTION.md` first.**
> The band geometry below stands. The supporting argument ("~5 turns … agreeing to 1.4 %")
> is **WITHDRAWN**: the count was an undercount (≥9 measured at full resolution) and the two
> reads were **not independent** — a solenoid and a flat spiral present the same radial band
> width from above, so they could not have disagreed. Whether this coil is the NFC antenna or
> the voice coil is **OPEN**.

## 1. The datum, measured rather than assumed

Source photograph: `images/airtag/oflynn-frontside-26mm-cropped.jpg`, 788 × 788 px,
Colin O'Flynn, CC-BY-4.0.

The crop is **not** tight to the board. O'Flynn drew a thin marker circle on it, and
that circle — not the frame, and not the board's visible edge — is the datum. It was
fitted, not eyeballed:

| quantity | value |
|---|---|
| selection | pixel dark (`<190`) while its 15 px neighbourhood median is white shell (`>225`) — this excludes the PCB entirely, whose ground is never white |
| fit | Kasa algebraic circle + IRLS, hard 2 px band |
| **centre** | **(393.50, 393.50) px** — the frame centre, to 0.01 px |
| **radius** | **393.59 px** → diameter **787.18 px** |
| residual | **sd 0.388 px**, p95 |res| 0.66 px, 391 inliers of 415 candidates |
| stability | re-run at three thresholds (`a<180/190/200`): centre moved ≤0.02 px, radius ≤0.01 px |

The circle is **inscribed in the square crop, tangent at all four cardinal points**.
That is why a naive ray-cast reports "board edge at 394 px" — it is finding the frame,
not the board. Recorded so nobody repeats it.

### SCALE BASIS — quote this with every millimetre derived from this photograph

```
787.18 px  =  26 mm   (APPROXIMATE)
30.2762 px/mm   =   0.033029 mm/px
centre (393.50, 393.50) px
```

### The systematic nobody can remove from here

O'Flynn wrote **"~26 mm"**. The tilde is his. `docs/REFERENCE-TEARDOWN.md` §7 lists
*"exact bare-board diameter"* as **CANNOT DETERMINE**, settled only by measuring a real
board. Therefore:

- **relative** numbers (ratios of the datum diameter) carry only the fit residual, ≈0.1 %;
- **absolute** millimetres inherit the datum's unbounded error. If the true diameter is
  25.5 or 26.5 mm, every mm below moves ~2 %.

So every table here prints **both**, and the ratio is the one that survives a better datum.

---

## 2. Outer board edge — CANNOT DETERMINE, and why

Ray-casting for "outermost sustained dark" returned a median exactly equal to the search
cap. The distribution was piled at the boundary, so **that number was an artifact and is
discarded**, not reported.

Looking at the region at 4× (`edge_topleft`) shows why the automatic test cannot work.
Going outward from the copper, the photograph contains, in order: dark PCB → gold copper
ring → an olive translucent film → a **dark grey foam gasket** → O'Flynn's drawn arc →
white plastic shell. The gasket is as dark as the board and overlaps the edge.

**Verdict: exact bare-board outer diameter — CANNOT DETERMINE from this photograph.**
Consistent with `REFERENCE-TEARDOWN.md` §7. What would settle it: a caliper on a real
board, or a scale-referenced photograph of a bare MLB. FCC internal photo 6 shows a bare
MLB but carries no ruler; photo 1 has a ruler but shows the assembled dome.

The drawn circle sits **within a gasket's width** of the board edge, so 26 mm remains the
working figure — as a working figure, labelled, not as a measurement.

---

## 3. NFC coil — MEASURED, and it is not what the dossier says

`tools/measure_coil.py`, copper chroma (R−B > 28, R > 90, not blown out), radial histogram.

| quantity | px | mm (datum-limited) | ratio of board dia |
|---|---|---|---|
| winding inner radius | 142.0 | 4.690 | — |
| winding outer radius | 164.0 | 5.417 | — |
| **coil ID** | — | **9.380 mm** | **0.3608** |
| **coil OD** | — | **10.834 mm** | **0.4167** |
| **radial width of winding** | 22.0 | **0.727 mm** | — |

### The construction is wound wire, not a laser-structured trace

`docs/REFERENCE-TEARDOWN.md` §2.3 lists ANT2 (NFC) as *"LDS coil"* on the moulded carrier,
alongside the BLE and UWB antennas. **At 2× the individual turns of round magnet wire are
directly resolvable**, with the two ends brought out to red-lacquered terminations. It is
a wound bobbin coil.

**Independent corroboration, which is why this is stated rather than suspected:** ~5 turns
are visually countable, and the measured band width 0.727 mm ÷ 5 = **0.145 mm per turn** —
AWG 35 magnet wire is 0.143 mm. The turn count read off the picture and the band width
measured off the pixels agree to 1.4 % without either being fitted to the other.

**Confidence: HIGH** for "wound wire" on this unit. **CANNOT DETERMINE** whether all three
antennas are on one carrier as §2.3 states — the front photograph shows only this coil.
This resolves the discrepancy the halo lane flagged, in favour of the photograph.

Consequence for the Replica: the NFC antenna is a **wound coil**, so it is reproducible
without LDS tooling. That removes one of the three antennas from the "needs tooling we do
not have" list.

---

## 4. Centre hole — CANNOT DETERMINE, and the number that looked like it

The saturated white core is the magnet/dome assembly, over-exposed, and the grey moulding
around it covers the board's inner edge. **The PCB centre hole is not visible in this
photograph.**

An earlier pass reported "inner hole diameter 10.834 mm". That is the **inner edge of the
copper coil winding** and is now labelled as such in §3. It is the same 164.0 px. Recorded
here because the two would be indistinguishable in any downstream document, and the
annulus is the headline difference between the Replica and `halo_rev_a`.

**What would settle it:** FCC internal photo 8 ("Removed MLB", board with the magnet
assembly) or photo 6 ("MLB – Front", bare board) — neither yet measured, and neither
carries a scale reference, so each needs the board outline itself as its datum.

---

## Status of this document

| # | quantity | verdict |
|---|---|---|
| 1 | scale basis of the front photograph | **MEASURED**, sd 0.388 px |
| 2 | board outer diameter | **CANNOT DETERMINE** (gasket overlaps the edge) |
| 3 | NFC coil ID / OD / width, and that it is wound wire | **MEASURED**, corroborated two ways |
| 4 | board centre-hole diameter | **CANNOT DETERMINE** (obscured by the magnet assembly) |

Two of the first four are CANNOT DETERMINE. That is the expected shape of this lane and
they are named with what would close them, not filled with plausible numbers.
