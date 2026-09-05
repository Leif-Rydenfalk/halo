# R01 — AMENDMENT to the pre-registration: P3 IS FALSIFIED, and the gate that replaces it

*halo Replica, lane L10. Committed **before any pixel of the real rim was extracted** — the
falsification below was established entirely on synthetic ground truth, so nothing in this
amendment was chosen downstream of a result. `git log` carries the ordering.*

---

## 1. P3, as pre-registered, is FALSIFIED — and it is a finding about `bin/boardmetro`

**R00 P3 predicted:** the circle-fit **inlier fraction** would separate a pasted **disc**
(≥0.85) from an equal-area **square** (≤0.30) with a separation ratio **≥2.5×**.

**Measured, on noise-matched synthetic ground truth (texture 35 luma, 1.4 mm feature, 120 luma
contrast), sweeping every parameter the statistic has:**

| IRLS band px | 1.5 | 2.0 | 2.5 | 3.0 | 4.0 | 5.0 | 6.0 | 8.0 |
|---|---|---|---|---|---|---|---|---|
| filled **disc** | 0.303 | 0.380 | 0.511 | 0.551 | 0.643 | 0.711 | 0.757 | 0.837 |
| filled **square** | 0.300 | 0.361 | 0.424 | 0.469 | 0.557 | 0.642 | 0.706 | 0.812 |
| **ratio** | 1.01× | 1.05× | 1.21× | 1.17× | 1.15× | 1.11× | 1.07× | 1.03× |

Pre-smoothing the contour extraction (σ 0…5 px) moves both together; the best ratio anywhere in
the two-parameter sweep is **1.45×**, and **the square never goes below 0.37.**
**P3 is falsified at every band and every smoothing. It is not close.**

### Why — and this is the transferable part
`bin/boardmetro`'s published separation (**square 0.055, ring 1.000**) is real, and its selftest
case 7 still passes. **But it was measured on a square OUTLINE against a thin RING** — four thin
lines whose corners sit far from any circle. A **FILLED** square of equal area to a disc has a
boundary that deviates from its own best-fit circle by at most **±17 % of the radius**
(inscribed a/2 to circumscribed a/√2), which at a 1.4 mm feature is **±3.5 px** — comparable to
any usable IRLS band. So the statistic has almost nothing to separate.

> **E07 §20 arriving on a shape statistic: a threshold is a property of a material AND A FIELD
> OF VIEW.** I inherited 0.055 / 1.000 from a tool that measures it honestly, set my
> pre-registered threshold from it, and it did not travel from outlines to filled blobs.
> **Nothing in the output would have looked wrong** — 0.55 against 0.47 is just a number, and
> if I had not registered 0.85 / 0.30 in advance I could have called it a separation.

**Fixed in `bin/boardmetro` itself, by extension and not by forking**: a new selftest case
(`selftest` case 10) drives filled disc against filled square through the same `fit_circle` and
records **0.36 vs 0.41 = 0.89×**, next to case 7's 18× on outlines, with the reason. The
existing case, its threshold and every existing verb are unchanged. **A gap in the shared tool
is fixed there, with docs** (PROTOCOLS P11) — routed to the orchestrator with this file.

## 2. The replacement gate, registered here with its threshold PROCEDURE

**Statistic — non-circular energy of the half-max radius profile.** R(θ) is the half-max
crossing radius about the candidate centre; Fourier-decompose it; k=0 is size and k=1 is a
centring error, so the shape lives in k ≥ 2:

    noncirc = sqrt( 2 · Σ_{k≥2} |F_k|² ) / mean(R)

Rotation-invariant by construction. Synthetic ground truth, σ 3, contrast 120, texture 35:

| feature | disc | **octagon** | square | rect 2:1 | rect 3:1 |
|---|---|---|---|---|---|
| `noncirc` | **0.033** | 0.038 | 0.104 | 0.276 | 0.435 |
| ratio vs disc | 1.0× | 1.2× | **3.2×** | **8.4×** | **13×** |

**Why not the 4-fold amplitude, which separates disc from square by 40×:** it scores a **2:1
rectangle at 0.022 against the disc's 0.003** — i.e. **as round**. A 2:1 rectangle is the SMD
capacitor pad class that produced five confident wrong detections in this project, so a gate
blind to it is a gate blind to the failure it exists for. `a4` is kept as a diagnostic only.
Selftest case 11 fires this on purpose.

### The threshold is a PROCEDURE, not a number carried across a field of view
Having just been bitten by exactly that, I am not registering 0.07 as a constant. **Registered
now:** the admit/reject thresholds are set from **pasted controls in the real rim, at the
contrast the real candidates present**, as `disc p90` and `square p10` over ≥24 pastes at
≥5 swept sites. A candidate is:

- **ROUND** if `noncirc ≤ disc_p90`
- **NOT ROUND** if `noncirc ≥ square_p10`
- **UNDECIDED** otherwise — **named and counted on its own line, never as a joint**

**FALSIFICATION, unchanged in spirit from P3:** if `disc_p90 ≥ square_p10` in the real rim, or
the median ratio is under **2.0×**, the gate is declared **non-separating on this source** and
the answer is a count of **compact bright features**, explicitly not of round joints.

### The gate has a measured CONTRAST FLOOR and must declare it
Synthetic, 24 pastes per contrast — the separation dies, and it dies fast:

| contrast luma | 200 | 160 | 120 | 90 | **70** | 50 | 35 |
|---|---|---|---|---|---|---|---|
| disc p90 | 0.023 | 0.029 | 0.040 | 0.070 | 0.232 | 0.368 | 0.554 |
| square p10 | 0.087 | 0.086 | 0.085 | 0.088 | 0.099 | 0.170 | 0.319 |
| verdict | SEP | SEP | SEP | SEP | **OVERLAP** | OVERLAP | OVERLAP |

**Below ~90 luma of contrast this gate separates nothing**, and a gate that is silently useless
at low contrast is worse than no gate. Selftest case 12 asserts both the separation at 120/90
**and the overlap at 50** — so the case goes red if either half stops being true.
**Registered consequence:** any candidate whose own measured contrast is below the floor
measured in the real rim is **UNDECIDED**, not ROUND.

## 3. A second amendment: R00 §4 break 7 was not a regression test, and I watched it fail

R00 registered: *"with the polarity-consistency guard removed, the straight edge must then be
accepted."* **It is not.** Removing the guard leaves the edge at **0.48** against a null p99 of
**0.64** — still rejected. The straight edge is killed by the ring integral being *structurally*
zero and by the **closure** requirement; **it tests neither guard.**

> That is E07 §27 in my own selftest before I had measured anything: **a regression case must
> reproduce the conditions the guard exists for.** Written against the easy case, the failure
> has no reason to occur.

**Rebuilt** on the case the polarity guard actually exists for — a **bipolar** feature, one
boundary, brighter than ground on one side of it and darker on the other. Every octant is
strongly supported, so closure alone admits it; only polarity consistency rejects it.
**Guard on: −1.20, rejected. Guard off: 1.64, above the 0.64 null p99, accepted.** Now it is a
test.

## 4. What is unchanged
P1, P2, P4, **P5 (my bias: optimism, biased to count too high)**, P6, the whole of §3's bar
methodology, the sweep, and **all six stopping-rule conditions** stand exactly as committed in
R00. **No count is registered, and none has been formed.** I have not looked at the rim.

## 5. Instrument state at this commit
`tools/r_circ.py` — **12/12 selftest**, every case noise-matched at texture 35, with the seven
registered breaks plus five shape-gate cases. Cases **7 and 9 were watched go red** for the
reasons above before they were rebuilt. `bin/boardmetro circles` / `circles-selftest` reach it;
`bin/boardmetro selftest` **14/14** with the new filled-blob case.
