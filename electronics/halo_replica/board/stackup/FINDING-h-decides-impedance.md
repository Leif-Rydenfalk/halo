# FINDING — "not manufacturable" is a property of the assumed prepreg, not of the 0.60 mm stack

*halo Replica lane L4 (stackup **and fabrication**), 2026-09-05.
A finding about **`halo_rev_a`**, not about the Replica. Raised here because
this lane owns fabrication and cannot write into `out/release/`.
Re-run: `s_stackup_budget.py solve 0.60 4`.*

## What lane B1 wrote, and it is honest

`out/release/board/STACKUP.md` §1 states its dielectric heights and marks all
three **CANNOT DETERMINE**, saying plainly that *"the three heights above are a
plausible set that sums to 0.60 mm with the stated copper weights — they are
arithmetic, not a quote"*, and that this is *"the number to ask the factory for
first, because §2 depends on it entirely."* Everything in that paragraph is
correct, including the refusal.

Their arithmetic checks out: 2×0.035 + 2×0.0175 copper + (0.0685 + 0.36 +
0.0685) dielectric = **0.6020 mm**.

## What is new

**The set sums correctly and is not made of materials anyone stocks.**

- **0.0685 mm is not a pressed prepreg thickness.** The sourced styles are
  106 = 0.050, 1080 = 0.065, 2116 = 0.100, 7628 = 0.180 mm (MADPCB, fetched).
- **0.360 mm is not a stocked core.** The published series is 0.1, 0.2, 0.3,
  0.4, 0.5, 0.7, 1.0, 1.5 mm (allpcb, fetched).

Enumerating every stackup of **sourced materials only** that reaches 0.600 mm
within ±0.030 mm gives 19 combinations, and the closest fits are ±5 µm. Across
them:

> **h — the outer dielectric that sets microstrip impedance — ranges 0.050 to
> 0.200 mm on stackups that all hit 0.600 mm.**

h is not determined by the board thickness. That is the whole finding.

## Why it matters: §2's conclusion reverses inside that range

Using **B1's own formula and constants**, `Z0 = (87/√(εr+1.41))·ln(5.98h /
(0.8w + t))` with εr = 4.3 and t = 0.035 mm. **Control first:** at their
h = 0.0685 mm this reproduces **w = 0.0859 mm** against their stated 0.086 mm,
so the implementation is theirs and not a different calculation.

| h (mm) | a real stackup that gives it | w for 50 Ω | vs the 0.127 mm design minimum |
|---|---|---|---|
| 0.050 | 1×106 prepreg, 0.400 core | 0.0509 | **below** |
| 0.065 | 1×1080 prepreg, 0.400 core | 0.0793 | **below** |
| **0.100** | **1×2116 (or 2×106), 0.300 core** | **0.1456** | **ABOVE — manufacturable** |
| 0.200 | 2×2116, 0.100 core | 0.3349 | **ABOVE — comfortably** |

§2 concludes *"a 50 Ω microstrip referenced to L2 is not manufacturable on a
0.60 mm four-layer stack. That is a property of the stack, not a mistake in the
layout."*

**It is a property of the assumed prepreg.** The 2116 stackup lands at
0.6050 mm — one of the closest fits to target — and puts the 50 Ω width at
0.1456 mm, above both the 0.127 mm design minimum and JLCPCB's 0.09 mm floor.
On roughly half the buildable stackups, option 1 is available and no plane slot
is needed.

**This does not make rev A's choice wrong.** Option 2 — keep the run short and
absorb it in the pi network — is defensible at ~0.1 λ whatever h turns out to
be. What changes is the *reason* recorded for it, and that matters because the
recorded reason is what a revision B decision would be built on.

## What this strengthens

B1's own instruction to ask the factory for the stackup first. It is stronger
than they put it: the answer does not merely feed §2, **it decides §2**, and it
decides it across a boundary rather than shifting a margin.

## The limits of this finding, stated

- The formula is B1's, and it is a closed-form microstrip approximation.
  **`ce-rf` owns real impedance**; this shows a *sensitivity*, not a design value.
- εr = 4.3 is their assumption too, marked in their §3 as *"generic, not
  fab-quoted — the single largest uncertainty in every RF frequency in this
  pack"*. It moves w as well, and this does not touch it.
- The core series is **one vendor's published stock**. Another house stocks
  another series, and a fab-quoted stackup beats this list. It answers *"is
  this height made of a material that exists"*, not *"build this."*
- A real 4-layer press also has resin flow and copper-coverage dependence that
  a sum of nominal sheet thicknesses does not capture.

## The instrument

`s_stackup_budget.py solve <target> <layers>` — enumerates stackups of sourced
materials only, and reports the h range. `selftest` **14/14**, with two breaks
fired on purpose:

| break | result |
|---|---|
| let the HDI process-minimum back into the stock list | **1 red** |
| ignore the tolerance, so every combination is returned | **2 red** |

The first break is the one worth naming. `hdi_laser_blind_min` is a **process
minimum** — the thinnest sheet that may be laser-drilled — not a sheet anyone
orders by name, and it had leaked into the stock list on the first run,
inventing a `1×hdi_laser_blind_min` stackup no fabricator could quote. A
solver that answers with a material that cannot be ordered is worse than one
that answers nothing, because the row looks exactly like the real ones.
