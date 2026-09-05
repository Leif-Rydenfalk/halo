> **⚠ TWO DIFFERENT BOARDS — an unstated systematic under every millimetre here (L9, 2026-09-05).**
> The FCC photographs show **920-08283-01, data code 3119** — a **2019 engineering build**.
> O'Flynn's show **820-01736-A, data code 2920 17** — **2020 production**. Every scale in this
> lane is transferred from one to the other. **A uniform dimensional difference between two
> different boards is absorbed into the fitted scale and leaves the held-out residual COMPLETELY
> unchanged**, because the check divides both sides by the same number. This applies to the
> Replica's 106.313 px/mm and therefore to every absolute millimetre downstream of it.
> **CANNOT DETERMINE here.** A caliper on one board of each part number settles it.

# E08 — what the Replica actually is, measured against our own other board

*halo Replica lane (orchestrator), 2026-09-05. The comparison lane set our two boards against
Apple's and against each other across 24 axes. This is the part that is about **us**, and it is
less flattering than the picture.*

## The headline, and it is a self-criticism

**We have a bare-board replica, not a replica of the internals.** Leif's word was *internals*.

The Replica scores SAME on nine axes — **and all nine are in one region**: outline, shape,
thickness, layer count, centre hole, surface finish, and three refusals where drawing nothing was
the correct answer. **It matches Apple on the bare board and has no answer on almost anything
mounted to it.**

| board | SAME | EQUIV | DIVERGED | MISSING | CANNOT DETERMINE | UNSTARTED | → |
|---|---|---|---|---|---|---|---|
| `halo_rev_a` | 5 | 2 | 12 | 1 | 3 | 0 | **13 departures**, 3 no-answer |
| `halo_replica` | 9 | 0 | 1 | 1 | 8 | 4 | **2 departures, 12 NO ANSWER** |

**Neither right-hand column may be quoted alone.** "2 versus 13" is exactly this project's
favourable-half headline, and it would be appearing inside the document written to catch it. Two
departures looks like discipline only until you count the twelve no-answers beside them.

## `halo_rev_a` wins 12 of 24 axes, and four of those are uncomfortable

Primary-axis tally: **rev_a 12 · replica 7 · CANNOT DETERMINE 3 · tie 1 · tie-at-zero 1**, judged on
three named axes per row — fidelity to Apple, buildability, fitness for `GOAL.md`. Five rows reverse
on a second axis and say so. **"Closer to Apple" is never used as a synonym for better.**

- **Antenna.** The Replica wins on fidelity *by having none*, because Apple's are on a carrier.
  rev_a wins buildability and goal-fitness decisively: an LDS carrier needs a mould tool and a
  plating line, and a distributable block cannot require one. **This is the strongest rev_a
  survivor in the file — stronger than the amplifier D23 predicted.**
- **Flash + LDO + load switch**, and **the audio path.** Both rev_a divergences survive, on
  arithmetic: 1.27 % of the SoC's internal flash used, and a BTL class-D and two anti-phase GPIO
  swing the same 6 Vpp into a 21 nF capacitive load. D23's own named prediction holds.
- **Coverage.** The Replica has drawn **one of Apple's two populated faces**. Coverage is part of
  fidelity, and it loses that row.
- **Cost and manufacturability.** No price, no sourced part, and 0.30 mm sits below both fab
  houses' four-layer floors. **The Replica is unbuildable *because* it is faithful.**

## Two measured differences nobody had stated

1. **rev_a's NFC coil sits at R10.043–10.825 mm; Apple's central wound coil at R4.690–5.417 mm
   (ID 9.380 / OD 10.834)** — a **2.1× radial difference**. Caveated on `E02`: whether Apple's
   central coil is the NFC antenna or the *voice coil* is still open. Settling E02 settles the
   interpretation, not the number.
2. **The Replica's four UNSTARTED axes are ONE job — Apple's other populated face.** The battery
   contacts, the five 100 µF bulk capacitors, all ~38 test points and half the coverage are on it,
   and `oflynn-frontside-fullres.jpeg` already carries every one — at **33–42 genuine px/mm**,
   *sharper* than the face we did measure. **The better photograph is of the face nobody
   measured.** A lane is on it now.

**UNSTARTED is deliberately a distinct verdict from CANNOT DETERMINE, so that a job cannot hide as
a limit.**

## The correction to `THE-DRIFT.md`, which I think is right

That document says halo "built the wrong thing while every step was right". Re-reading `GOAL.md`
against the accumulation, as it asks: **rev_a answers 3 of the 4 aims GOAL.md actually states** —
embeddable block, peer ranging, cost-as-spec; not perfect copy. **The Replica answers 0**, and
structurally cannot answer the block or the ranging, having no schematic, no netlist and no nets.

So the framing is **too harsh on rev_a and too kind to the process.** The defect was never that
rev_a diverged — it answers the goal that was written down. **It was that the recreation Leif also
asked for went unbuilt until he said so twice, and that nothing counted the divergences in
between.** D23 says "seven places"; **the measured count is 13.**

## Routed, not edited — three items in another lane's files

1. **`spec/comparison.json` overstates rev_a's antenna, and `board.py` withdraws it.** The page
   credits AE1 "+0.521 dBi, 3.7 dB above Apple's". `board.py` calls the element "a PARAMETRIC
   PLACEHOLDER" whose "S11 is CANNOT DETERMINE until ce-rf measures THIS copper. It is not asserted
   to work." It is the one row claiming rev_a beats Apple on a physical number — and the comparison
   was never valid anyway: Apple's −3.2 dBi is a *measured, shipped* antenna; +0.521 dBi models a
   placeholder on a different outline.
2. **AE1 is called four things in two files** — meandered quarter-wave monopole, inverted-F,
   inverted-L monopole, rim inverted-F. Different topologies, different counterpoise requirements.
3. **The divergence ceiling is unset.** `THE-DRIFT.md`'s own remedy asks for "a stated ceiling" and
   no document states a number. **The counter now exists; the threshold does not.** How far a family
   member may drift before it stops being a member is a product decision, and `variants.json` is not
   this lane's file.
