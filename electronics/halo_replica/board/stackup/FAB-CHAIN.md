# FAB-CHAIN — the release pack is checked at one link of three

*halo Replica lane L4 (stackup **and fabrication**), 2026-09-05.
Tool: `../../tools/s_fabchain.py`. Exit code is the verdict — 0 / 1 / 2.*

## The finding

`docs/VERIFICATION-DEBT.md` **V2** is the top blocker on release-pack item 1.
Its closing condition is *"re-export from the routed board, then get
`check_fabset` to exit 0."* **Doing exactly that would produce a false green.**

A fabrication release is a **chain**, not a pair:

```
board.py  ──►  halo_rev_a.kicad_pcb  ──►  gerbers + drill
          └──── NOT CHECKED ────┘   └──── checked (F11) ────┘
```

`tools/check_fabset.py` calls the `.kicad_pcb` **"the source"** (line 13, and
`--board` is documented as *"the source .kicad_pcb the set claims to be"*). It
is not the source. It is an intermediate. `board.py` is the source — line 147
of it reads `OUT = .../out/halo_rev_a.kicad_pcb`.

## Measured, by git content hash — not by mtime

```
$ s_fabchain.py check
FAIL   board.py -> halo_rev_a.kicad_pcb
       blob 5da01fa -> 4b1dffb in 1 commit (b324645). Not rebuilt.
FAIL   halo_rev_a.kicad_pcb -> halo_rev_a-B_Cu.gbl
       blob 5a9863a -> ce4a680 in 2 commits (5a65d8f, a1d31ae). Not rebuilt.
```

- The board's last commit is `5a65d8f`; `b324645` post-dates it and changed
  **21 lines** of `board.py` — *"stop calling AE1 three different topologies in
  one file"*, a topology change, not a comment.
- `halo_rev_a.kicad_pcb`'s blob is **unchanged** since `5a65d8f`. The board was
  never rebuilt.

**Why blob hashes and not mtimes.** `git checkout` rewrites mtimes, so an
mtime comparison raises false alarms on any tree checked out in an unlucky
order — and a check that cries wolf gets ignored, which fails the same way as
one that never fires. The mtime delta here (24 972 s) agrees, and is reported
as corroboration only.

## Why this matters more than an ordinary stale file

`check_fabset` currently reports **14 PASS / 1 FAIL**, and its one FAIL is F11
`export_is_fresh`. Re-export the gerbers and F11 goes green, the runner exits
0, and release-pack item 1 flips to **READY** — describing a board one design
revision behind its own source. **The check goes green exactly when it stops
being true.**

This is the `TOOLS-THAT-LIE.md` family, in a new position: not a check that
measures the wrong thing, but a check that measures **the right thing at the
wrong link**, so closing it honestly still produces a false pass.

## The patch, for the lane that owns `tools/check_fabset.py`

**Not applied by this lane** — `tools/` is outside `halo_replica/` and held by
another session. Writing there is an outage, so the instrument is delivered
instead of the edit.

Add a check `F16 board_is_fresh_vs_source`, mirroring F11 one link up:

- new argument `--source electronics/halo_rev_a/board.py`
- with no `--source`: **CANNOT DETERMINE**, *"no --source given: cannot tell a
  board built from the current design from one built from an older one"* —
  the same shape F11 already uses when `--board` is absent, and **not** a PASS
- with `--source`: FAIL when the source's blob changed in any commit after the
  last commit that wrote the board
- when the source is **dirty**, CANNOT DETERMINE, not PASS — an uncommitted
  source cannot be identified

`s_fabchain.py link_verdict()` is the whole implementation, ~30 lines, and its
selftest already carries the cases.

## What the tool was watched to do

`selftest` → **7/7**, and **three breaks fired on purpose**:

| break | result |
|---|---|
| compare the downstream file's history to itself — direction ignored | **3 red** |
| never call a changed blob stale — the "plausible default" shape | **3 red** |
| let an untracked file through instead of CANNOT DETERMINE | **1 red** |

The third break **did not go red at first.** Case 4 asserted only the verdict
*code*, and with the `tracked()` guard deleted the same CANNOT still came back
from `last_commit()` returning `None` — a different route to the same answer.
**A test satisfied by a fallback does not test the guard it names.** Case 4 now
asserts the *reason string* as well, and the break goes red.

That is the third time this session the same shape has been caught, and only
ever by firing a break: the stackup budget's "the total went up" (copper grew
while the dielectric had stopped), the layer probe's FFT control (blank paper
scored higher than the real grid), and this one.

## Also open, from the same run

`s_register.py` was built to answer the via question — through-hole or
blind/buried — by putting the four delayered layer photographs in one frame.
**It fails its own independent residual and is not usable.** `hole/extent`
should be a board property and agree across all four images; it spread
**89.8 %** (0.0990, 0.0530, 0.1001, 0.1413).

**Diagnosis, which is the useful part:** the invariant was bad, not just the
fit. Inner radius measured from copper tracks *copper coverage*, which differs
per layer by construction — on a delayered board the ground-away regions expose
laminate and the outer copper does not reach the rim uniformly. A background-
subtraction attempt then measured the letterbox border instead of the board.

**The tooling-hole route was then tried, and also failed.** Three plated holes
at fixed board positions would give a similarity transform including rotation.
Detecting them as *background enclosed by board* — you see the table through a
through-hole — recovered the centre hole on `layer3` and `layer4` (26 303 and
30 251 px at fill 0.62–0.63) but **not on `layer1` or `layer2`**, where the
centre region drains to the frame edge through a notch, and **no tooling holes
on any layer**: every other enclosed component came back at fill 0.22–0.45,
irregular ground-away patches rather than round holes. The plated holes do not
read as background, presumably because the barrel is plated and lit.

**Stopped here, and the reason is not that it was hard.** Three methods failed;
searching method-space until one produces an answer, with no control saying the
answer is right, is the same defect as tuning a threshold until it agrees.

**The deeper reason, which would have applied even if registration had worked.**
The via test is *"a land on the component side with no counterpart on the other
outer face is a blind via."* That is a claim about an **absence**. On `layer4`
the copper is sparse and ground, so a land the detector simply missed and a land
that is genuinely not there produce **the same output**. A test whose negative
result is indistinguishable from a broken instrument is not a test — and it
would have failed silently in the direction that flatters, because "blind vias
found" is the more interesting answer.

**What would actually settle it:** a cross-section, or an X-ray at a resolution
that separates a blind barrel from a through barrel. Both are bench work, not
image work. `s_register.py` stays committed with its residual check going red:
a tool that reports its own failure is worth more than a deleted one.
