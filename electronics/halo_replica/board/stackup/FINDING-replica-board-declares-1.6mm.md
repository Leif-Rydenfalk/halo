# FINDING — the Replica fab board declares 1.6 mm, against 0.30 mm as-drawn

*halo Replica lane L4 (stackup and fabrication), 2026-09-05.
Re-run: `s_stackup_budget.py verify <board.kicad_pcb>` — exit 0/1/2.*

## The measurement

```
$ s_stackup_budget.py verify electronics/halo_replica/fab/out/halo_replica_fab.kicad_pcb
  FAIL   board thickness   declared=1.6   spec=0.3
         declared 1.6mm, as-drawn is 0.3mm — 5.33x.
         1.6 mm is KiCad's DEFAULT: this reads as never set, not as chosen
  PASS   copper layers     declared=4     spec=4
FAIL — a fabricator quotes from the BOARD, not from the document.
```

Read straight out of the file: `(general (thickness 1.6))` at line 6, and four
copper layers `F.Cu / In1.Cu / In2.Cu / B.Cu`.

**The layer count is right.** This is not a board that is simply wrong — it is a
board with one field never set.

## Why 1.6 mm specifically matters

**1.6 mm is KiCad's default for a new board.** It is not a number anybody chose;
it is the number that appears when nobody chooses. That makes it silent — it
survives routing, survives export, and is what a fabricator quotes from.

**This trap has already been sprung once in this project.** Lane B1 on
`halo_rev_a`, in `out/release/board/STACKUP.md` §1:

> *"KiCad's default is 1.6 mm, and this board carried that default until
> ce-fab's DFM report printed the thickness it had measured — a fab quoting
> from an uncorrected file would have built a board nearly three times too
> thick for its enclosure."*

`halo_rev_a` now declares `(thickness 0.6)`. **The Replica board was not
corrected**, and its error is larger: **5.33×**, not 3×.

## Why it matters more here than anywhere else

The Replica exists to be a faithful copy of a **0.30 mm** board. Thickness is
the single most-cited number in this lane — it is the one decision that was
settled before the lane began, and the reason it was settled at 0.30 mm rather
than at whatever a process allows is that **the Replica is the reference the
other five variants are measured against**.

A board file saying 1.6 mm is that reference, as a fabricator would receive it,
diverged by more than five times. And every RF or impedance number computed
from this board's stackup is computed at 1.6 mm.

## What this does NOT say

- **Not that anyone chose wrongly.** A default that was never overridden is a
  different failure from a bad decision, and the fix is different too.
- **Not that the board is otherwise wrong** — the layer count matches the
  COUNTED 4.
- **Not a claim about Apple.** Apple's 0.30 mm is unaffected; this is about
  our file.
- The board may be mid-flight — a route was running on it when this was
  measured. That changes the urgency, not the fact: `1.6` is exactly what
  survives to the fab if nobody looks.

## The sweep: 45 boards, and only TWO are ours and wrong

Running `verify`'s reader over every `.kicad_pcb` in `ce-designs/halo`,
`ce-pcb/out` and `ce-fab/out` finds **26 of 45 at 1.6 mm** — a number that means
almost nothing until it is split, and reporting it unsplit would have been the
same over-flagging mistake as the 17 antenna cases.

| group | at 1.6 mm | verdict |
|---|---|---|
| **halo Replica boards** — `fab/out/halo_replica_fab`, `pcb/out/halo_replica` | **2** | **DEFECT.** Both carry the default against a 0.30 mm spec |
| third-party reference designs — `reference/ruuvitag_hw`, `reference/nordic-lib-kicad` | 12 | **not ours.** 1.6 mm is their choice |
| toolchain fixtures — `aht20_breakout`, `esp32_carrier`, `hexdrive`, `netstep`, `round32_4layer`, `round32-dfm-violations` | 12 | **not defects.** 1.6 mm is a sensible default for a test board |

**So the finding is two boards, not twenty-six** — and it is one more than I
started with: `pcb/out/halo_replica.kicad_pcb` carries it too.

### And the positive control, which is the encouraging half

**Every `halo_rev_a` board reads 0.6 mm — all seven of them:** the source board,
the routed board, `out/verify/`, `out/release/quote/dfm/`, both design-block
copies in `ce-pcb/out/blocks/`, and `ce-fab/out/halo_rev_a/dfm/`. B1's single
correction propagated to every derived copy.

That matters twice over: it proves the fix propagates cleanly when it is made,
and it proves this sweep can distinguish corrected boards from uncorrected ones
rather than flagging everything.

*(`round32_4layer` at 1.6 mm is worth one line: it is the Ø31.87 mm placeholder
that release item 5's panel evidence was actually measured on — see
`FINDING-pack-status-is-asserted.md` §3b. Correctly a fixture, and correctly not
this project's board.)*

## The check that would have caught it, and now does

`s_stackup_budget.py verify <board>` reads the two declarations a fabricator is
quoted from — board thickness and copper layer count — and compares them to
`stackup.json`'s `replica_as_drawn`. Deliberately regex-based, with no `pcbnew`
import, so it runs under the system python as a cheap gate anywhere.

`selftest` **18/18**.

### The control that was missing, found by firing the break

The first version had two cases: the Replica board *reads* as 1.6 mm, and a
synthetic good board *passes*. I broke `verify` so every comparison matched —
and **all sixteen cases stayed green** while the Replica board reported
`PASS — the board declares the stackup this lane established` at 1.6 mm against
a 0.30 mm spec.

Both existing cases could only fail in one direction. Case 17 adds the other:
**the Replica board must FAIL `verify`**. The same break now goes **1 red**.

**A control that can only fail in one direction is half a control.** Third
sighting today, all three caught only by firing a break on purpose:

| | the control that could not go red |
|---|---|
| `s_stackup_budget` | "the total went up" — copper still grew while the dielectric had stopped |
| `s_layerprobe` | an FFT control that scored blank paper *above* the real land grid |
| `s_fabchain` | an untracked-file case satisfied by a fallback, not by the guard it named |


---

## RESOLVED 2026-09-05 — and my own departure figure was wrong

`ce-workshop-9a` fixed **both** boards, and fixed the **generators** rather than
the files, on the grounds that a value patched into an output is one rebuild
from coming back. `pcb/board.py` now reads the number out of
`stackup.json` → `replica_as_drawn.board_thickness_mm` rather than having 0.3
typed into it — *a typed constant is the same defect one level up*. The root
cause was named too: **ce-pcb had no thickness API**, so no board here could
declare one; `Board.thickness(mm, why=)` now exists.

| board | was | now | verdict |
|---|---|---|---|
| `pcb/out/halo_replica.kicad_pcb` | 1.6 | **0.30** | PASS `--spec as-drawn` |
| `fab/out/halo_replica_fab.kicad_pcb` | 1.6 | **0.80** | PASS `--spec as-ordered` |

### My 0.40 mm proposal was wrong, and I had flagged the row that proved it

This file previously proposed **0.40 mm** as the departure, *"the nearest
orderable thickness above 0.30 **at both houses**"*. **JLCPCB does not offer
0.4 or 0.6 at four layers.** 9a measured it in the live quote configurator with
both controls — negative: clicking 0.4 at 4 layers does nothing; positive:
switching 4 → 2 layers re-enables 0.4 in the same page, so the disable tracks
layer count and is a real constraint rather than styling. **0.80 mm is the
thinnest orderable at 4 layers.**

The row that would have caught me is the one **this very file already carried as
UNVERIFIED** — *"the fetch returned 0.8/1.0/1.2/1.6/2.0 for 4-layer but flagged
it as inferred rather than quoted. Not treated as a fact here."* I wrote the
caveat and then reasoned past it in the next field. That row is now **MEASURED**.

### Two specs, and why the second is not a tautology

`fab/` departs from as-drawn **on purpose**; measuring it against as-drawn fails
forever, and a permanent expected-red is a check people learn to ignore. So
`stackup.json` now carries **`fab_as_ordered`** (0.80 mm, 4 layers) beside
`replica_as_drawn` (0.30 mm, 4 layers), and `verify` takes `--spec`.

9a declined to add that row themselves — *"a lane inventing the spec it is then
measured against"* — which is exactly right, so it is built to be contradictable.
`--spec as-ordered` checks the **vendor's offer list**, which is external
evidence, in three separate rows:

1. **`spec_is_orderable`** — the recorded spec must itself be a thickness the
   vendor offers at that layer count. **Invent a convenient 0.5 mm and this row
   goes red first**, before anything about the board is considered.
2. **`board_is_orderable`** — the same test on the board.
3. **`board thickness` / `copper layers`** — and only then, do they agree.

`--spec as-drawn` on the transcription branch is unchanged and still holds the
board to Apple's 0.30 mm.

### The half-control, for the fourth time in one session

I wrote three anti-tautology cases, broke the guard, and **all 25 stayed green.**

- Case 18 fed an unorderable *spec* — but `board_is_orderable` failed on the
  same input for a different reason, so the case passed through a **neighbouring
  row**.
- Case 19 fed an unorderable *board* — but the equality row failed anyway.

Each case was satisfied by a row it was not testing. The fix was to expose
`LAST_ROWS` and assert **which row fired**, not the exit code. Both breaks now
go **1 red**. `selftest` **25/25**.

> **Asserting an exit code tests the union of every row. It cannot tell you that
> the row you meant to test still works.**

That is the same shape as `s_fabchain`'s untracked-file case passing through a
`last_commit()` fallback, `s_layerprobe`'s FFT control, and `s_stackup_budget`'s
own "the total went up" — **four in one session, every one found only by firing
a break.**
