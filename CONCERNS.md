# CONCERNS — things that feel off, for Leif

*Opened 2026-09-05 at Leif's instruction, verbatim: "i have to know stuff like
this and be properly informed when something feels off. continue working always
but tell me when something is wierd."*

**The rule this file enforces.** A measurement that contradicts the goal is not a
data point. It is an escalation, and it goes here **and** into the next message
to Leif — not into a table for him to notice. Work continues; the concern is
raised in parallel, never instead.

**Why it exists.** The comparison lane measured that halo matched 6 of 18 AirTag
parts by number. I relayed that as a statistic. It was evidence the project had
walked off its own goal, and Leif had to see the renders himself to catch it.
The full account is `docs/THE-DRIFT.md`. This file is so that never depends on
him looking.

## What raises a concern

| trigger | why |
|---|---|
| a measurement contradicts `GOAL.md` | the drift failure, in one line |
| a divergence count crosses its ceiling | a ratchet with no counter is how drift happens |
| a number is impossible, not merely bad | permittivity below 1, efficiency above 100%, a meander resonating higher than a straight trace |
| a requirement turns out untestable | the mandated loudness has no production limit |
| a chosen part cannot be bought | the sounder; the chip at volume |
| a cost or size assumption moves by more than half | the thing being designed is no longer the thing specified |
| a decision was reversed by evidence | Leif should know what changed his product |
| **something simply feels wrong and cannot be named yet** | the whole point — say it early and unformed rather than late and proven |

---

## OPEN

### C-1 · About 16 µA of the power budget is unexplained
**Raised 2026-09-05.** "About a year on a CR2032" implies **≈26 µA average**.
Our own component model predicts **6.0 µA** at a 5-second advertising interval
and **9.9 µA** at 2 seconds. Nothing accounts for the difference, which is
roughly **three times** the modelled draw.

Either the year is pessimistic and the tag lasts far longer, or there is a
consumer nobody has named. **Both possibilities matter to the product**: the
first is a marketing claim we are underselling, the second is a defect hiding in
a number that looks reassuring. It has sat in the research since the energy study
and was never raised, because a conservative-looking figure does not feel like a
problem. That is precisely why it belongs here.

**What settles it:** a measured current profile on real silicon, which is
verification debt V4 and needs hardware.

### C-2 · The antenna match clears by 0.39 dB
**Raised 2026-09-05.** With the coil at its working distance the best buildable
network reaches −6.39 dB against a −6 dB requirement. That is not margin; it is
the width of a manufacturing tolerance. Any later change near the annulus — a
ground pour, a via, a component moved — can spend it, and nobody would notice
until units failed.

### C-3 · The mandated sound level cannot be tested on a production line
**Raised 2026-09-04, restated.** The anti-stalking standard specifies 60 phon, a
psychoacoustic loudness. A sound level meter measures decibels, and there is no
fixed conversion. **The loudest legal requirement in the product currently has no
line test**, and closing it needs a reference unit characterised in phon plus a
gauge study.

---

### C-5 · I quoted a beat-Apple antenna number the board's own source withdraws
**Raised 2026-09-05.** I told Leif more than once that halo's antenna measures
+0.521 dBi against Apple's filed −3.2 dBi, 3.7 dB better. The replica lane read
both files and found `board.py` says, under its own heading *what this board does
not claim*, that the element is a **parametric placeholder** whose S11 is
CANNOT DETERMINE until the real copper is solved.

Worse, the comparison was never valid even had the number been right. Apple's
−3.2 dBi is a **measured** figure for a **shipped** antenna in a regulatory test
report. Ours was a **model** of a **placeholder** on a **different outline**.
Differencing those produces a headline, not a result — and it is the same defect
as every other entry in `docs/TOOLS-THAT-LIE.md`, committed by me rather than by
a tool.

Withdrawn from `spec/comparison.json`. halo has **no antenna number** until the
solve on the real board returns.

## CLOSED

### C-0 · halo was not a copy of the AirTag
**Raised by Leif, 2026-09-05, from the renders — which is the failure.** Closed
by decision D23 (the variant family) and by a dedicated terminal now building the
part-for-part replica. Recorded in `docs/THE-DRIFT.md`.

### C-4 · A finding I reported to Leif has weakened
**Raised 2026-09-05.** I told Leif that Apple's NFC coil is wound wire and that
this dropped the Replica's unbuildable-antenna count from three to two. The
lane that found it has since **withdrawn its own supporting argument**: the two
"independent" measurements were measuring the same radial band, because a
solenoid and a flat spiral look identical from above, so they could not have
disagreed. What survives is a direct observation that the conductors are
individually resolved and coplanar, plus a resistance argument that favours NFC.

**Why it is a concern rather than a correction:** the coil's leads land on pads
this repository attributes to the **voice coil**, while Apple's own arrow labels
that annulus the **NFC antenna**. Both cannot be true, and the voice-coil
attribution turns out to be our own assertion rather than a quotation from the
source. If it is the voice coil, the Replica's gap returns to three antennas and
what I told Leif was wrong.

**What settles it:** DC resistance across TP1/TP38 on a live unit, or a
photograph of the front dome's inner face. Neither is available here — this one
needs a physical AirTag.

### C-6 · A stale rule-check was reporting PASS on a board that does not exist
**Raised 2026-09-05 by the replica lane, confirmed by re-running it.** The
design-rule report in the release pack was **17,616 seconds — 4.9 hours — older
than the board**. A stale gerber wastes a fabrication run and is at least
visible as a bad board; **a stale rule-check reports PASS on copper it never
saw**, nothing about it looks wrong, and a green rule-check is precisely what a
release gate reads. It fails earlier and far more quietly.

**And re-running it exposed something else: there are three artifacts here and no
two describe the same copper.** The source board that `board.py` regenerates is
**unrouted at 83 unconnected**. The routed board is a **separate derived file at
28**. The gerbers are older than both. The "28 unconnected" figure I have been
reporting is the routed file; anyone cutting a package from the source board
would get the 83.

Fresh reports now sit in `out/verify/`. The row cannot move until routing reaches
zero, the source and routed files stop diverging, and the package passes a
freshness gate against the board it was actually cut from.

### C-7 · A retune scaled from a number that was never measured
**Raised 2026-09-05 from the finished rt2 solve, confirmed by searching every
verdict on disk.** The rt2 spec states its premise in its own `why`:

> *"The law is f ~ 1/L at fixed eps_eff: measured 2.5565 GHz, target 2.4418 GHz,
> so scale 1.04696."*

**There is no measurement of 2.5565 GHz.** Every `verdict.json` under
`ce-rf/out/` was searched for any row between 2.55 and 2.56 GHz; none exists.
But `2.6763 × (24.491 / 25.641) = 2.5563`. The premise is the 1/L law's **own
output**, written into the spec in the grammar of an observation and then used
as the basis for scaling. The loop fed its prediction back to itself as
evidence.

This is worse than a wrong number, because a wrong measurement can be
contradicted by a better one. A prediction wearing the word *measured* agrees
with the model by construction, so no amount of further solving can dislodge it.

**And the law it was steering by does not hold.** All three bare cases converged,
so the comparison is like-for-like:

| case | conductor | 1/L predicts | measured | law short by |
|---|---|---|---|---|
| meander9-bare | 24.491 mm | — | 2.6763 GHz | baseline |
| rt1-bare | 20.731 mm (−15.4%) | 3.1617 GHz | **2.7058 GHz** | 16× |
| rt2-bare | 25.641 mm (+4.7%) | 2.5563 GHz | **2.6630 GHz** | 9× |

Shortening the conductor 15% moved the resonance 1.1%. Whatever sits at
~2.67 GHz in the bare case **does not move when the conductor moves**, so it is
not the conductor's mode, and no length change will tune it. Three solves were
spent scaling the wrong resonator.

**A third defect, structural:** rt1 and rt2 both scale from the *same*
24.49100 mm baseline — rt2 did not start from rt1's result. That is two
independent guesses from one point, not the iterate → simulate → fix loop the
project was asked for. A loop that never reads its own previous output cannot
converge; it can only sample.

**Not a near miss, before anyone reads one into the table:** rt1-passive lands at
2.3730 GHz, 1.1% below the band, which looks tantalising. Its `mode_identified`
is **0** and its `gain_dBi` is **−11.81** against a −3.2 target. It is an
unidentified zero over a dead radiator — exactly what D26 exists to refuse.

**What settles it:** identify the ~2.67 GHz mode before proposing any geometry.
Sweep a structural parameter that is *not* the conductor — the pour radius, the
feed tab, the board diameter — and see which one moves that zero. Whichever
moves it, owns it. One solve answers this; three more length guesses answer
nothing.
