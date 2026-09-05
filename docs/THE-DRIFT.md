# The drift: how a project built the wrong thing while every step was right

*Written 2026-09-05 by the orchestrator, about its own failure, at Leif's
insistence. It belongs beside `TOOLS-THAT-LIE.md` and `VERIFICATION-DEBT.md`
because it is the same family — a system that reports success it has not earned
— except here the failing instrument was judgement rather than a tool.*

## What happened

Leif asked for a copy of the Apple AirTag. Twenty-two numbered decisions later,
halo was a **functional equivalent that looks nothing like an AirTag**. He said
so himself, on seeing the renders: *"our current version doesnt look visually
similar at all. not even close."*

He was right, and our own measurements had said so for hours:

| | Apple | halo |
|---|---|---|
| lines matching **by function** | — | 17 of 18 |
| lines matching **by part number** | — | **6 of 18** |
| board | annular ring, centre hole, 0.30 mm | solid disc, 0.60 mm |
| antennas | three, laser-structured on a moulded carrier | two, etched in board copper |
| passives | wafer-scale | 0402 and 0201 |

## Why nobody caught it

**Every individual decision was defensible, and most were correct.** The flash
was deleted because it was out of spec on the cell rail. The amplifier went
because a bare piezo needs none. The chip changed because the new one gives peer
ranging and costs less. The board thickened because deleting Apple's motor
returned 1.742 mm and a 0.30 mm board is fragile. Redrawing rather than copying
copper avoided a licence that would have infected ours. Each of those would
survive review on its own.

**What nobody did was ask what they added up to.** There is a decision log with
twenty-seven entries and it records each choice with its evidence and what it
beat. Nothing in the process ever re-read the accumulation against `GOAL.md`.
The log is a ratchet: every entry justifies a step away from the reference, and
no entry ever asks how far we now are from it.

**The damning part is that I noticed and did not act.** Decision D23, written
hours before Leif's message, contains the sentence *"halo was one board that had
diverged from the AirTag in seven places, each defensible in isolation, which
together made it a functional equivalent rather than a copy."* I wrote that,
committed it, and then carried on routing the equivalent. I reported the 6-of-18
figure to Leif as an interesting statistic in a comparison table rather than as
what it was: **evidence that the project had drifted off its stated goal.**

Seeing it and filing it is worse than missing it. A finding that changes what you
should be doing, and does not change what you do, is not a finding — it is a
note.

## The general shape

This is the third failure family this project has found, and it completes them:

1. **A tool reports success it has not earned** — the check that measured the
   wrong quantity, the router that never ran, the drill file with the wrong
   board's holes. `TOOLS-THAT-LIE.md`.
2. **A claim is carried as fact although nothing ever executed it** —
   `VERIFICATION-DEBT.md`.
3. **A sequence of locally-correct decisions arrives somewhere nobody chose.**
   This page. No single step is wrong, so no step triggers a check, and the
   destination is never compared to the intent.

The third is the hardest because there is nothing to catch. Each decision passes
its own review. The defect only exists at the level of the whole, and nothing was
looking there.

## The fix, and it has to be mechanical

Judgement did not catch this, so a resolution to use better judgement will not
either. Two concrete changes:

1. **A drift check, on a schedule rather than on a trigger.** Periodically —
   every ten decisions, or whenever a comparison artifact regenerates — read
   `GOAL.md` and ask one question in writing: *does what we are building still
   answer this?* Record the answer even when it is yes, because a check that only
   produces output when something is wrong is a check nobody trusts.
2. **A divergence budget, made visible.** `spec/comparison.json` already counts
   SAME / EQUIVALENT / DIVERGED / MISSING. That count belongs on the convergence
   scoreboard as a tracked row with a stated ceiling, so the thirteenth
   divergence is visibly the thirteenth rather than just the next one. A ratchet
   with no counter is how you get here.

## Revision, 2026-09-05: this document was too harsh on the board and too kind to the process

*Added after the replica lane re-read `GOAL.md` against the accumulation, which
is the check this document asks for — and the check found the document itself
wrong.*

**The board answers three of the four aims `GOAL.md` actually states.** The
embeddable block: yes. Peer ranging: yes. Cost as a first-class spec: yes. A
perfect copy: no. The Replica, meanwhile, answers **none of the four**, and
structurally cannot answer the block or the ranging, because it has no
schematic, no netlist and no nets.

So "built the wrong thing while every step was right" is not accurate. **The
defect was never that the board diverged** — it diverged toward the goal Leif
wrote down. The defect was that **the recreation he also asked for went unbuilt
until he said so twice**, and that nothing counted the divergences in between.
That is a narrower failure and a more useful one, because the remedy is
different: not "stop diverging", but "build both, and count".

**And the count in D23 was wrong.** It said the board had diverged in seven
places. **The measured count is 13** — nearly double, stated in the very
document that named the ratchet. The board reads 5 same, 2 equivalent,
**12 diverged**, 1 missing, 3 undetermined across 24 axes. The Replica reads
9 same, 1 diverged, 1 missing, **8 undetermined and 4 unstarted**.

**Both columns must be quoted together, always.** "2 divergences against 13"
read alone is precisely this project's favourable-half headline, appearing
inside the document written to catch it. The Replica's two departures come with
**twelve no-answers**. And its nine matches are all in one region — outline,
shape, thickness, layers, hole, finish, and three refusals where drawing nothing
was correct. It matches Apple on the **bare board** and has almost no answer on
anything mounted to it. Leif's word was *internals*.

## What it cost

Not the work — the board, the enclosure, the firmware and the tooling are real
and most of it serves any variant. What it cost was **direction**: hours spent
routing and re-solving a board that answers a question Leif did not ask, while
the recreation he did ask for did not exist as a single file until he said so
twice.

**And it cost the thing this project trades on.** Every page here argues that a
number must be measured and a check must be able to fail. The same standard
applies to the goal: it has to be re-read, and the project has to be able to
fail against it. Ours could not, because nothing was asking.
