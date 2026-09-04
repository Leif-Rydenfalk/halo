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

Four more, found the same night by the same method — running the thing and
counting the result:

| what reported success | what was actually true | how it was caught |
|---|---|---|
| Gerber export, as part of a working fabrication pipeline | **No export had ever succeeded.** The exporter passed a flag that does not exist in KiCad 10 | Looking for the files |
| A design-rule report naming the factory's 0.09 mm limit | The check was running against a **0.2 mm default netclass**; the report named a rule that never fired | Comparing the named rule to the loaded one |
| The keep-out containment test | It **never ran once**. A method gained an argument in KiCad 10, and a bare `except` swallowed the resulting error, so the test returned null on every board | Using the primitive and finding it accepted everything |
| `bin/exercise` printing `DRC: None violations` | The board file had been **rejected outright** by KiCad; there were no violations because there was no check | Asking what "None" meant |

Eight more, found 2026-09-04 by lane V1 by running each tool's output back
through a **second** reader, and each one **proved** by breaking something on
purpose and watching the check go red:

| what reported success | what was actually true | how it was caught |
|---|---|---|
| The factory Gerber pack — 14 files, exporter exit 0, pack index READY | The **PTH and NPTH drill files contain zero holes** on a four-layer board, which cannot exist without vias | Counting the coordinate lines after the Excellon header. Nothing had ever asserted a drill file has holes in it |
| `CONVERGENCE.md`: *Bluetooth antenna resonant frequency · 2.44 GHz · 2.425 GHz · **MATCH***, weight 10 | The case's own `verdict.json` says **FAIL**. `solver.log` says the run hit max timesteps before the −40 dB end criterion. `raw.json` has **no convergence block**. And there are **zero upward reactance zero-crossings in the whole 1–6 GHz sweep** — the reactance is +23.7j…+25.5j across the BLE band. There is no resonance; 2.425 GHz is the minimum of a smooth \|S11\| curve | `gen_convergence.py` reads `measurements.json` and never opens `verdict.json`. Opening it, then reading the impedance instead of the verdict |
| `eps_eff_implied = 0.9657` **PASS** — the physics check written to catch exactly this | The spec's floor had been widened from **1.0 to 0.64**. A physical law had become a tolerance, so the impossible value cleared it | Comparing the assertion's limit to the law it was named after |
| The physics-sanity row on the convergence table | Its target is text and its current is a number, and the state machine has **no branch for that pair**. `state` stays at its initialised `"OPEN"` forever. It can never go green and can never go red | Feeding the state machine a correct value and a deliberately wrong one and finding the answer identical |
| `fab bom cost`, most lines **PASS** | The parts are not the parts. **C2827888**, ordered as 2.2 µF / 10 nF / 2.2 nF, is a **3.5 mm screw terminal block**. **C1046539**, ordered as 2.7 nH and 3.5 nH, is a **33 MHz MEMS oscillator** at $14.73. **C1546** is 100 pF and is ordered as 100 nF *and* as 1.1 nF. Every 0201 land pattern is fitted with an 0402 part | Asking a question the tool never asks. It grades stock and price; nothing compared the catalogue's own description to the schematic's value |
| `speaker_hbridge` **PASS**, 16 assertions over four corners | **`f_audio_Hz` appears in zero `measure()` expressions.** Every assertion is an amplitude, and amplitudes hold at any frequency. Drive the H-bridge at 7 kHz and `i_coil_peak_mA`, `i_batt_avg_mA` and `efficiency_pct` **all still pass** | Grepping the measurement expressions for the quantity in the study's own title. This is the antenna case, in the audio band, eleven months of assertions later |
| `fab dfm` on halo_rev_a: **21 PASS / 2 FAIL / 5 CD** | **10 live DRC violations vote zero.** Any violation whose type is not in `CONSTRAINT_MAP` goes to a counter that never enters `rows`, and the verdict is `worst(*rows)`. Also: `smt_sides` is a **hardcoded `PASS`** while measuring 2 sides; three via rows report `PASS, measured 0` because the board has no vias; `castellated_hole_min` reports PASS on a loop that never ran; and **11 of 52 rules produce no row at all**, so the counts read as full coverage of a set they cover 28 of | Adding the violation counts by hand and finding they did not reach the verdict |
| Two keep-out regions on halo_rev_a, both **PASS** | Both declare `tracks/vias/pads/copperpour/footprints **allowed**`. `forbids == []`, so every hit loop `continue`s and zero hits reads as clean. Separately, if the board outline cannot be read at all, `outline_error` is recorded and the region is **still graded PASS** | Reading what the region actually forbids. The original keep-out bug's alarm was rewired; the sprinkler was not |

Five more, found 2026-09-05 by lane B1 while trying to make a fabrication
package pass its own gate. Every one was found by **running the tool and
counting the result**, and every one is now negative-tested:

| what reported success | what was actually true | how it was caught |
|---|---|---|
| `check_fabset`'s `drill_covers_board`, **PASS** — 50 drill hits against a board needing 49 | The rule was `total_hits **>=** board holes`. **The 50th hole belonged to a board revision that no longer existed** — the pack was cut at 02:27 and the board rewritten at 03:31. A `>=` rule passes a drill program cut from a *different* board as long as that board had at least as many holes, and it added the PTH and NPTH totals together, so swapping the two files was invisible. The handover into the session said 50 "looked plausible, a PTH file also carries through-hole pads": halo_rev_a has **0** through-hole pads | Counting per file class and per hole DIAMETER instead of in total. Now four exact assertions: class read from each file's own `TF.FileFunction` and never its filename, PTH == vias + thru-hole pads, NPTH == np_thru_hole pads, and the multiset of diameters equal per class |
| `fab dfm`, **CANNOT DETERMINE** on four rules: *"this rule never fired even at 40× its limit, so either the board has no items it matches, or the condition is one KiCad cannot evaluate"* | One of the four, `jlc_smd_pad_to_pad`, **fires 258 times.** The probe reads the rule's NAME out of the violation description, and `kicad-cli pcb drc --all-track-errors` changes ATTRIBUTION: with the flag all 499 clearance violations name `jlc_pad_to_track`; without it, 241 name that and **258 name `jlc_smd_pad_to_pad`**. Same board, same `.kicad_dru`, same project. For the other three, "the board has no items it matches" was a **number nobody counted** — 0 plated through-hole pads, measured in one line | Running the same provocation file by hand without the flag the tool passes, and comparing the two attributions. The probe now runs both ways and unions; a rule that cannot fire is CANNOT DETERMINE only if the board really carries items it governs, and a vacuous PASS is labelled `vacuous` with the count |
| `check_convergence`'s `high_weight_measured`, **PASS** on two weight-10 antenna rows | It compared the `from` field to the string `"literal"` and passed **everything else**, so a row naming a source that produced **no value at all** scored better than one that honestly typed its number in. Both rows had `current: null` | Listing the rows that were PASS and asking what number they had passed on. There wasn't one |
| `prove_checks.py` reporting **FIRED** for `drill_has_hits` and `drill_npth_count_exact` | `_gerber(d, r"PTH\.drl$")` also matches `halo_rev_a-**N**PTH.drl`, and rglob order on this machine handed it the NPTH file — so two mutations were being applied to the wrong artifact. They had reported FIRED for months; they reported SILENT the moment a new assertion made the difference visible | Adding checks that could tell the two files apart, and watching the prover's control go red for a reason no mutation explained |
| The pack README, in prose: *"the 0.16 mm item is U3's unnumbered paste-relief aperture, which carries no copper — the narrowest real copper pad is 0.200 mm"* | The narrowest paste-relief aperture is **0.318 mm**, the *widest* of the three kinds. The 0.15 mm pads are the NFC net tie's, real copper. The exoneration was backwards, and it had been read and re-read by three sessions | Measuring all 254 pads and grouping them by kind instead of trusting the sentence. `fab dfm` now reports the three numbers separately, and the verdict still rests on the worst |

## Why they are one defect

In every case the tool's report describes its *intent*, not its *effect*. The
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

## 6 · Prove it fires, or it is not a check

Added 2026-09-04. Every one of the eight incidents above was a check somebody
wrote and nobody ever watched fail. **An assertion never seen to fail is not
known to work.**

So a new check is not finished when it goes green on the good artifact. It is
finished when it has gone **red** on an artifact you broke on purpose, and the
break is committed beside it so the next person can re-run it.

`ce-designs/halo/tools/prove_checks.py` is the pattern: it copies a real
passing artifact, applies one named mutation per assertion, and requires that
assertion — by name, not the overall verdict — to report FAIL. It exits
non-zero if any assertion stays silent. **25 of 25 fired** when it was written.

Two traps it hit on its own first run, both worth knowing:

- **A control that is already red proves nothing.** Three assertions had to be
  skipped until the control artifact was repaired, because you cannot show a
  check going red if it was red before you touched anything.
- **The probe has to be the shape of the real measurement.** The convergence
  check's state-machine test first passed its target a *string* while the row
  really produces a *number*, and the broken row looked fine. The check that
  hunts decorations was briefly a decoration itself.

## 7 · `>=` is not `==`, and a tool's own flags can blind its own probe

*Added 2026-09-05, from the drill-count and liveness incidents above.*

Two habits, both cheap, both of which would have caught something here.

**Ask whether the check's comparison is the claim.** "At least as many holes as
the board needs" is not "the drill program for this board". `>=`, `<=`, "contains"
and "not empty" are all weaker than the sentence a reader will infer from a
green row, and the gap between them is exactly where a stale artifact lives. If
the true relation is equality, write equality — and if you cannot write
equality, say in the row why you could not.

**A probe that reads a tool's own output is bound by that tool's flags.** The
liveness probe here decided whether a rule was alive by looking for the rule's
name in a violation description; a flag on the same command changed which rule
got named, and the probe went blind without erroring. Whenever a check works by
parsing another tool's report, run that tool **two different ways** and require
the answers to agree — or take the union, if one way can hide what the other
shows. Two readings that agree are worth more than one that passes, and this is
the case where the two readings come from the same tool.

---

## The sibling rule: do not prune a row you cannot yet explain

*Added 2026-09-05, from an error I made and a peer session endorsed.*

The convergence table carried a row for a round-board antenna variant sitting at
5.54 GHz against a 2.44 GHz target — 127 percent out, with no explanation. Both
I and a peer session judged it noise. The peer wrote: *"either fix it or retire
it explicitly as a dead variant, an OPEN row nobody intends to close is noise on
the scoreboard."* I passed that instruction to the lane.

**That variant is the one that worked.** `halo-round-rim-ifa` now passes every
assertion at 2.4469 GHz with **+0.521 dBi of realized gain against Apple's own
filed −3.2 dBi**, a 3.7 dB improvement, and it is the antenna halo ships. Had the
lane obeyed promptly, the geometry carrying the answer would have been deleted
from the board while three explained-looking failures stayed.

**The rule.** A row that is red and *unexplained* is not the same as a row that is
red and *understood to be dead*. Retiring the second is housekeeping. Retiring the
first destroys information, and it is tempting precisely because an unexplained
row is uncomfortable to look at.

This is the same defect as the rest of this page seen from the other side.
Elsewhere a tool reported success it had not earned; here a **clean scoreboard**
would have reported completeness it had not earned. Both trade a true, awkward
record for a tidy, false one.

**In practice:** never retire a row on the grounds that nobody is working on it.
Retire it only when someone can say *why* it is dead — and write that reason
down, because the reason is the thing that makes the removal safe.

