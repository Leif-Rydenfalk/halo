# C4 — The self-locating mesh

*Researched 2026-09-05. Every number below is either quoted from a primary
source that was fetched and read, or **measured on this machine** and marked so.
This is the concept that serves Leif's stated reason for the project: sensors
that know where they are relative to each other, for the digital twin.*

## Verdict: PROVEN, with one hard design rule

The algorithm is settled, it fits on the chip halo already carries, and the
accuracy at building scale is good. But there is a threshold below which the
answer is not merely worse — it is **wrong by metres**, and the design must
refuse rather than publish through it.

## The result that matters

**Measured here**, 3D, nodes uniform in a 30 × 30 × 10 m box, classical
multidimensional scaling to initialise then Levenberg–Marquardt on the range
residuals, aligned to truth with reflection allowed so these are true
anchor-free relative errors:

| tags | range error σ | mean degree | **RMS position error** | Cramér–Rao bound |
|---|---|---|---|---|
| 10 | 10 cm | 9 | 15.8 cm | 15.8 cm |
| 20 | 10 cm | 19 | 9.9 cm | 10.4 cm |
| **50** | **10 cm** | 49 | **6.1 cm** | 6.1 cm |
| 50 | 30 cm | 49 | **18.3 cm** | 18.3 cm |

Two things to take from this. **The estimator hits the Cramér–Rao bound
exactly**, so no semidefinite relaxation is needed anywhere in the loop —
multidimensional scaling plus Levenberg–Marquardt is provably as good as it
gets. And **more tags make every tag better**: fifty tags at 10 cm ranging land
at 6.1 cm, better than the ranges themselves, because averaging over a denser
graph beats the individual measurement.

Plan against **σ = 30 cm**, which is Silicon Labs' measured figure for their
own Channel Sounding silicon, rather than the Bluetooth SIG's ±20 cm claim. At
fifty tags that still gives **18 cm relative accuracy across a 30 m building**.

## The hard rule: density, not precision, decides whether it works

Range-limited to 15 m, same setup:

| tags | mean degree | RMS error | bound |
|---|---|---|---|
| 10 | 3.6 | **508 cm** | 82 cm |
| 20 | 7.7 | **310 cm** | 173 cm |
| 50 | 21.0 | **10.4 cm** | 9.9 cm |

A sparse network is not "less accurate". It is **five metres wrong**, because
the range graph is not globally rigid and sub-clusters **flip** about a mirror
plane. This was cross-checked against rigidity theory rather than guessed: the
Fisher information matrix of a rigid framework has rank exactly
`n·d − d(d+1)/2`, and the failing rows are precisely the rows where the measured
rank fell below it. A tag with three neighbours in three dimensions sits on a
mirror plane and will flip.

**The rule the firmware must enforce: in 3D, require mean degree ≥ 10–12 before
publishing any position, and return CANNOT DETERMINE below it.** Global rigidity
is checkable in polynomial time by a randomised algorithm (Gortler, Healy and
Thurston, *American Journal of Mathematics* 132, 2010: a generic framework is
globally rigid **if and only if** it has a stress matrix whose kernel has the
minimum possible dimension `d+1`). So the network can *know* whether its own
graph admits a unique answer, before it claims one. **Build that check.**

## Where the computation goes

**Measured** working-set memory for the matrix-free normal-equations solve:

| case | total |
|---|---|
| 2D, 50 nodes | 58.8 KB |
| **3D, 50 nodes** | **107.8 KB** |
| 3D, 20 nodes | 17.3 KB |

The nRF54L15 carries **256 KB of RAM** and a Cortex-M33 with a floating-point
unit at 128 MHz, so 3D with fifty nodes fits with about 150 KB to spare. The
whole solve is roughly 15 MFLOP, estimated at **0.4 to 0.6 s** on that part —
an estimate from measured iteration counts and a stated throughput assumption,
**not a benchmark**; flashing it to real silicon would settle it.

**Recommendation nonetheless: the tag computes nothing global.** It ranges,
timestamps and reports. The global solve is trivial for a phone or a hub, and
the hub is the only place that can see the whole graph to run the rigidity check
and reject outliers. Keep an on-tag solver only as a degraded mode with no hub
reachable, capped at about twenty nodes in 3D.

## The architecture that makes it scale

Standard Channel Sounding is **point-to-point**: the Bluetooth SIG has adopted a
Ranging Service and Ranging Profile, both version 1.0, and both describe two
devices. Nordic's own sample is one initiator and one reflector. Neither the SIG
nor any vendor publishes a multi-node ranging profile.

The nearest published work is aimed squarely at this problem and runs on **the
exact chip halo uses**: Schex, Cremer and Dettmar, *"Connectionless Bluetooth
Channel Sounding via PAwR for Scalable and Energy-Efficient Ranging"*
(arXiv:2605.17094). It combines the Channel Sounding test command with Periodic
Advertising with Responses so that no per-pair connection is needed at all; each
device derives its role, its channel sequence and its response slot from its own
index and a shared assignment matrix. Measured on an nRF54L15: **40–48 % less
steady-state charge** than a connected baseline, **98 %** less per-switch
overhead, up to **88 % lower total charge over 24 hours** under per-cycle partner
switching, and a projection of **up to 14,080 active devices per advertising
train**.

That dissolves the per-pair connection limit that would otherwise cap a tag at a
handful of peers — which is exactly what is needed to reach the mean degree of
10 to 12 the rigidity result demands.

## Two things this forces into the hardware

1. **Put an inertial sensor on the tag.** Orientation is a first-order error
   source in Channel Sounding: a 2026 study reports a **74.6 % reduction in mean
   absolute error** from a model trained on inertial-derived orientation. A tag
   on a moving asset tumbles. halo already carries an accelerometer for the
   anti-stalking requirement, so this is nearly free — but the ranging firmware
   must actually use it.
2. **Report raw ranges with quality metadata, never solved positions.** No tag
   sees the whole graph, and the three estimators Nordic's own sample computes
   disagree — its log shows 1.04, 1.58 and 3.08 m for one measurement by
   inverse-FFT, phase-slope and round-trip-time respectively. Use the
   phase-based pair; treat round-trip time as a coarse ambiguity resolver only.

## The opportunity

A search of open repositories returned **no established open-source anchor-free
range-network solver**. GTSAM is the closest usable foundation — 3,666 stars,
BSD licensed, with a first-party range factor and incremental solving — but the
anchor-free network solver on top of it does not exist. halo would be writing
it, and the measurements above say multidimensional scaling plus
Levenberg–Marquardt is sufficient.

## What is not settled

The Cramér–Rao formula from the most-cited paper in this area could not be
quoted, because it is paywalled and the author's mirror refuses connections; the
bound used here comes from a different paper that was read in full. The absolute
figures behind the orientation result are in a PDF only the abstract of which
was fetchable. And the on-chip solve time is an estimate, not a benchmark.
