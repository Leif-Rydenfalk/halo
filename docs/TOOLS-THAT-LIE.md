# Tools that lie: a report not derived from the thing it claims to have done

*Written 2026-09-04, from three incidents in one night. Sibling of the rule
already in this repo that an empty answer is not a measurement, and of
`VERIFICATION-DEBT.md`, which tracks claims that never executed.*

## The defect

A tool reports success. The report is real, well-formed, and green. But it was
not **derived from** the thing the tool claims to have done. Nothing errors,
nothing is missing, and the result is worse than a failure — a failure stops
you, a false pass carries a wrong number downstream into a factory pack.

Three instances, all in one night, all found by different means:

| what reported success | what was actually true | how it was caught |
|---|---|---|
| The board pipeline documented autorouting as a working step; the jar was downloaded and the wrapper written | Autorouting had **never once run**. This Mac has no Java runtime, only Apple's stub that prints an error and exits | Asking what number the step had produced. There wasn't one |
| Two antenna simulations returned **PASS** | They resonated at 4.0 and 5.8 GHz against a 2.44 GHz target. The assertions tested only how deep the impedance match was and how efficient the radiator was — never the frequency | Reading the measured values instead of the verdict |
| A patch script reported files patched (peer session) | It had changed nothing. The regular expression skipped every option object containing an interpolation | Counting the occurrences afterwards |

## Why the three are one defect

In each case the tool's report describes its *intent*, not its *effect*. The
router wrapper reported the pipeline it would run. The antenna assertion
reported the properties it chose to test. The patch script reported the files it
had opened. None of them measured the thing the reader would infer from a pass.

## The rule

**Derive the report from the effect, then check it independently.**

1. **A pass must name the number it passed on.** "Design rules clean" is not a
   result; "0 violations, 1 unconnected, from this file" is. Every verdict in
   this project carries the measured value and the command that produced it.
2. **Assert the quantity that would make you wrong.** An antenna's job is to
   resonate in its band. If the band is not in the assertion, the assertion is
   decoration. Ask: what is the cheapest way this could pass while being useless?
   Then assert against exactly that.
3. **Count afterwards.** After a patch, count the occurrences. After a run,
   count the outputs. The count is derived from the effect; the log line is not.
4. **Add a physics or sanity assert that no wrong answer can satisfy.** The
   antenna case had one available for free: the effective permittivity implied
   by the resonant frequency and the trace length must be greater than one,
   because a dielectric cannot speed a wave up. That single check would have
   caught both failing geometries the moment they were solved — their implied
   values were **0.676 and 0.216**. A second free check: a meandered trace is
   longer than a straight one in the same space, so it must resonate lower. Ours
   resonated 45 percent higher, which is impossible.
5. **Two tools that agree are worth more than one that passes.** The coil is
   cross-checked between an analytic formula and the solver, and the spread is
   itself an asserted number.

## Applying it

When adding any check to this project, write down the sentence "this could
report PASS while ___ is badly wrong" and fill the blank. If you can fill it,
the check is incomplete. `VERIFICATION-DEBT.md` is the standing list of blanks
not yet filled.
