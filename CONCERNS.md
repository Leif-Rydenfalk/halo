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

## CLOSED

### C-0 · halo was not a copy of the AirTag
**Raised by Leif, 2026-09-05, from the renders — which is the failure.** Closed
by decision D23 (the variant family) and by a dedicated terminal now building the
part-for-part replica. Recorded in `docs/THE-DRIFT.md`.
