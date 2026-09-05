# R04 — the comparison, after disclosure

*halo Replica, lane L10. Written **after** `R02`'s CANNOT DETERMINE was committed and pushed
(495469f) and after the orchestrator disclosed the withheld figure. The ordering is in
`git log` on `rimblind-99cab5fe` and this file changes nothing above it.*

## What was withheld, now disclosed

- **`docs/REFERENCE-TEARDOWN.md` §2.3: "6 tear-off joints"** — a single unsourced parenthesis in
  a line about the antennas, citing no photograph, no count and no method. Never verified here.
- **`M12 §5`**: at native resolution the previous lane could see **4 bright solder joints across
  the top rim and 2 rectangular copper pads at the bottom**, noted 4 + 2 = 6, and refused to
  publish it — *"the number I expected is the number I saw."*
- **`M03` / `M05`**: 15 candidates against a control mean of 19.5 on one face, 13 against 23.0 on
  the other; closed CANNOT DETERMINE on signal-to-noise. **Both counts later withdrawn** when the
  blob detector failed a positive control of **six** synthetic pads, finding one.

## Do I agree? — **I neither confirm nor refute it, and that is the honest answer**

**My verdict stands unchanged: CANNOT DETERMINE.** I did not measure a number smaller than six. I
**failed to separate joints from confusers at all** — 13 of 15 detections above the bar are
visibly gold annular pads, SMD capacitor pads and grey rim gasket. A disagreement would require a
count I believed, and I have none. **The dossier's six is now unverified for a third time, by a
third distinct mechanism** — signal-to-noise (M05), instrument mismatch (M12), and confuser
population (here). Three instruments, three reasons, no count.

## Four things the comparison does establish

### 1 · A weak independent corroboration of WHERE, reached blind
The only two detections I judged plausibly solder joints are **#6 at θ 286.4°** and **#8 at
θ 263.8°** — both **above the board centre**, i.e. the **top rim**. `M12 §5` puts its four bright
solder joints "across the top rim". **I did not know that when I looked**, and the location came
out of the locator, not out of me. It corroborates the *place*, not the *number*, and two is not
four.

### 2 · The dossier's six is a SUM OF TWO MORPHOLOGY CLASSES, and no round-feature count can reach it
`M12 §5` resolves six as **4 bright solder joints + 2 rectangular copper pads**. My locator
rejects elongated rectangles **by construction** — a pasted 2:1 rectangle scores median closure
**≈0.0** against a disc's **5.6**. **So my instrument could not have found two of the six however
well it worked.** Anyone comparing a round-feature count against "6" is comparing against a total
that includes objects the instrument is structurally blind to.

> **This is the single most useful thing in this file for the next lane.** `R00` registered class
> **S** (straight-sided pads, via the `d_rect` engine) to be run and reported separately —
> **and I did not run it.** That is a gap in my own execution, not a finding, and I cannot close
> it now: any class-S count I produce from here is post-disclosure and worthless as a blind
> result. **It has to be run by someone who has not read this file.**

### 3 · `M12 §5` and the dossier are NOT two agreeing sources — they are one observation
The lane that made the eyeball observation already knew the dossier said six. Its own words are
the correct verdict on it. **So "4 + 2 = 6 matches the dossier" is one measurement, not a
corroboration** — E07's rule in its original form: *when you claim two measurements corroborate,
name what each would have had to see to disagree.* The eyeball observation could not have
disagreed, because the expectation was already in the room. **My count is the first look at this
question that could have come out differently, and it came out CANNOT DETERMINE.**

### 4 · The withheld figure had propagated INTO THE TOOLING
`M03`/`M05`'s replacement positive control built a synthetic rim carrying **six** pads — the
dossier's number, encoded in a selftest. That is the redacted **N** in this worktree's `E07 §4`,
and it is why the allow-list was the right shape: the figure was not only in prose, it was in
code that a counting lane would reasonably read. **An allow-list controls which files are read,
not what is inside them** — the redaction I flagged in `R00 §0` was the same defect one level
down, and this is a third instance one level below that.

## The second pass, registered in `R03`, ran and FAILED ITS OWN BREAK

Having seen that the three top-scoring confusers were **gold annular pads** — bright ring, dark
centre, where a joint is filled — I registered a **polarity** statistic in `R03` before running
it, labelled as weaker evidence because it was chosen downstream of the answer, and listed as
**break 3** the one result that could embarrass it: *the three gold rings must come back ANNULAR.*

    calibration, 24 pasted controls at measurably-empty real rim sites, 120 luma:
      disc     annularity p10 -0.288  p50 -0.031  p90 +0.105
      annulus  annularity p10 +0.464  p50 +1.006  p90 +1.118      SEPARATES

    BREAK 3:  #1 -0.634  #2 -0.277  #3 -0.039   ->  FILLED, FILLED, FILLED

**The statistic separates a pasted annulus from a pasted disc cleanly, and then classifies the
three real gold rings as FILLED. Break 3 fails. Per `R03`, the statistic is DISCARDED.** It is
not tuned, and no count is drawn from it. The 3 ANNULAR / 9 FILLED / 3 UNMEASURED split it
produced is recorded in `out/r-polarity.json` and **must not be used.**

> **The pass I designed from the answer, and was most tempted to believe, is the one that failed
> the test I wrote against it.** That is what break 3 was for, and it is the reason a
> downstream-of-the-answer analysis needs a break aimed at its own motivating observation. A
> clean calibration against pasted ground truth was not enough — the synthetic annulus is not
> the thing on the board.

## What this lane leaves behind

**Answered:** the rim question is **CANNOT DETERMINE for a third time, for a new reason**, with
the sensitivity margin measured (**8–70 luma needed against 166–208 available**) so it can never
again be closed as a signal-to-noise problem.

**Unanswered and now unblindable by me:** the class-S (rectangular pad) count, and the count
after a confuser discriminator that survives its own break.

**The two things that would close it**, unchanged from `R02` and now sharper given that six is
4 + 2: an instrument for **each** class, and — the one that would end the argument —
**a raking-light photograph**, because a solder joint is a dome and a gold pad is flat, and every
source this project holds was lit in the one way that hides the difference.
