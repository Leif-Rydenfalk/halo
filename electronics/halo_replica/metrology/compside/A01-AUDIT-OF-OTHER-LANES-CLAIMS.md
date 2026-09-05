# A01 — auditing other lanes for the failure shape that cost me five findings today

*halo Replica, lane L2, 2026-09-05. Read-only audit; nothing outside `compside/` was touched.*

I published and withdrew five findings today, and every one was the same mistake: **a verdict
the check could not have contradicted.** Having built two instruments for exactly that, I
swept the other lanes' published claims for the same shape. **The result is mostly a
confirmation, and it is reported as readily as a refutation would have been.**

## What I looked for

Claims of the form *ruled out · no evidence of · not detected · corroborated · consistent
with* — the phrasings that hide either an underpowered null or a check with only one possible
outcome.

## L5 · `p_render.py` R7, "CORROBORATED: L1's set is CONTAINED in mine" — **CONFIRMED, and now with a number**

L5 cross-checks L1's 14 `on_rim_material_suspect` rows using a **different denominator** —
`r / fitted outline radius` against L1's `r / raw measured local edge radius` — and the code
says outright *"The two could disagree; that is the point."* That is the right instinct.

But **containment is asymmetric**, and the verdict carried no null. If L5's set were large
enough, containing L1's 14 would be nearly automatic and would mean nothing.

So I computed the null, read-only, by replicating the calculation:

| | |
|---|---|
| rows total | **100** |
| L5's set (`r/fitted > 0.95`) | **16** |
| L1's flagged set | **14** |
| in both | **14** — L1's set is fully contained |
| **P(containment by chance, if L5's set were a random 16 of 100)** | **2.7 × 10⁻¹⁵** |

**The claim is sound and strongly so.** With only 16 of 100 rows selected, containing all 14
of an independently derived set is not something that happens by accident. L5 was right; the
verdict simply had no way to say *how* right, and now it does.

**Two constructive notes for whoever owns `p_render.py`** (it is outside my write scope):

1. **The R7 result is never persisted.** It is computed, drawn into the PNG caption, and
   discarded — `board/out/` holds only `board-front.png` and `compare-front.png`. A number a
   reader cannot get at without re-running a renderer is hard to check and easy to lose.
   Writing `r7` to JSON beside the image would fix it.
2. **The one-line null**, if it is wanted:
   `p = comb(len(mine), len(l1)) / comb(total, len(l1))` — the probability of containment if
   `mine` were a random subset of its own size. It turns "CORROBORATED" into "CORROBORATED,
   p = 2.7e-15", and it goes red on its own if `mine` ever grows large.

## L7 · `d_rect.py`, "INTENSITY AND TEXTURE ARE RULED OUT BY MEASUREMENT" — **SOUND, no action**

This one reads like the failure shape and is not. It is not an underpowered null; it is a
**demonstrated overlap**, which is the strongest form this claim can take:

> package luma **61 and 73** sit INSIDE the bare-soldermask range **52–145**; package
> local-sd **9.94 and 4.22** sit INSIDE the soldermask range **5.17–14.59**.

A discriminator whose two populations demonstrably overlap is ruled out *positively*, not for
want of power. And the replacement measurement carries an **empirical** null built by rolling
each row of the gradient independently — identical per-row statistics and along-row
correlation, only the between-row alignment destroyed. That is the correct permutation, and
the file even says why: it is the fix `E07 §2` records after L1's rim-pad control permuted the
wrong thing twice.

## What the sweep says overall

The phrasing that worries me is largely absent from finished claims here, and where it
appears it is usually attached to a withdrawal someone already made (the E02 turn-count
corroboration, withdrawn by its own author because a solenoid and a flat spiral present the
same radial extent — the same "two measurements that could not have disagreed" that cost the
coil finding). **This project is already policing the failure mode; my five were an outlier,
not a house style.**

## The two questions worth asking any claim here

1. **"What would this check have had to see to fail?"** If the answer is *nothing*, it is not
   a check. Containment by a large set, a coherence null from a blind statistic, a sign test
   with two outcomes — all fail this.
2. **"If it is a null, what amplitude was it blind to?"** A null without a detection limit is
   not a result. My R09 published *"a smooth cause is RULED OUT"* from a landmark set that
   could not have seen one; the identical face measured z = +8.5 once it had enough landmarks.
