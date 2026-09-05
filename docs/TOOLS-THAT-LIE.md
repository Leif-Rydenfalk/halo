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

## The sixth direction: a clearance measured from a centre, and a number nobody asked for

*Added 2026-09-05 by lane B1, from the NFC coil's ground clearance. Three
findings, and the first two generalise past this board.*

### 1 · A clearance test on a CENTRE passes things a clearance does not

The new `nfc-coil-clearance` keep-out caught a via on its first run that this
lane's own point-in-polygon test had just declared clean. The via's **centre**
sits at r 9.5389, outside a band starting at r 9.7431 — so a centre test says
0.20 mm of margin. Its **0.45 mm pad reaches r 9.7639** and intrudes
**0.0208 mm**.

Both numbers are right. Only one of them is a clearance.

**The rule.** A clearance is between COPPER and COPPER, never between a centre
and a boundary. Every item in a clearance test has an extent — a via has a pad
diameter, a track has a width, a pad is a capsule — and the test must subtract
half of each. This project has now been bitten by the same arithmetic twice
from opposite directions: here, a centre test that passed an intruding via; and
earlier, `_obstacles()` treating a 0.25 × 0.60 mm QFN land as a disc of its own
DIAGONAL, which forbade every escape route from every fine-pitch pin. Under-
and over-stating an extent are the same defect.

Grep for the shape of it: any comparison of `hypot(...)` or a point-in-polygon
result against a limit, where the thing being located has a size.

### 2 · A polygon drawn as chords is smaller than the circle it is named after

`annulus_polygon` drew 180 chords. A chord ring sits inside its circle by
`r · (1 − cos(π/steps))` — at r 9.74 that is **0.0015 mm**, so a band asked for
**0.30 mm was drawn at 0.2983 mm**, and every report of that keep-out would
have quoted a number nobody had asked for. Immaterial against a 0.15 mm mesh;
not immaterial as a habit, because the next such band might be checked against
a limit it now silently fails.

**The rule.** When a curve is approximated by segments, the approximation has a
SIGN — inscribed chords always fall short — and the error is `r(1−cos(π/n))`,
computable before you draw. Either compute it and add it, or use enough
segments that it is below the precision you report at. 360 chords put it at
0.0004 mm. And say which you did, because a reader cannot tell a drawn 0.30
from a drawn 0.2983 by looking at the constant that asked for it.

### 3 · A cost is not a regression, and the difference has to be stated

Cutting the planes out from under the coil took the board from **81 unconnected
items to 83**: two connections the pour used to make now need routing. That is
the price of the fix, it was predicted, and it is closed by the router.

It matters that this is written down next to the fix. An unconnected count that
rises is exactly what a regression looks like from the outside, and the next
person to read the numbers without the reason has every ground to revert the
change that made the board work. **A measured cost, named and attributed, is
part of the result. An unexplained one is a defect report.**

## The fifth direction: a reader that silently covers less than it claims

*Added 2026-09-05 by lane B1, from a check of its own.*

`check_routed.segments()` pulled a segment's net with
`re.search(r'\(net "([^"]*)"', blk)`. KiCad 10 writes `(net "GND")`, so it
worked. But `(net 2 "GND")` and a bare `(net 2)` are both legal Specctra-era
KiCad forms, and on those the regex did not raise — it returned `None`, the
segment fell into the `""` bucket or out of the map, and **the check went on
reporting PASS over copper it could no longer see.**

Coverage fell and confidence did not. That is the shape of it, and it is
different from every other entry on this page: no wrong number, no dead rule,
no unreferenced capability, no polluted stream. A **reader** that skips what it
does not understand, on an input format with more than one legal spelling.

**The rule.** A parser used by a check must be **total or loud**. Count what
you read against what is there, and refuse when they differ:

```python
n_blocks = len(re.findall(r"\(segment\b", text))
if strict and n_read != n_blocks:
    raise ValueError("read %d of %d ..." % (n_read, n_blocks))
```

That guard fires on a single dropped segment out of 649. Without it, the only
symptom is a check that grades less of the board every time the input format
drifts — and input formats drift.

### And a lesson about fixtures, which cost three attempts

The negative control for the assertion above was placed **on the opposite side
of the board, twice**, and both times it read as *"the check is broken."*
KiCad's Y axis points **down**, so an element drawn at a design angle of
20–104° lives at **256–340°** in board coordinates. The fixture was wrong, the
check was fine, and the wrong conclusion was one step away both times.

**A negative control is an artifact like any other: measure where you put the
break, do not assume it.** The third attempt located the arm by reading its own
segments back — bbox, radius and angle — before placing anything, and the
assertion fired immediately. The habit that saves this is the same one the rest
of the page teaches, turned on the test instead of the thing under test.

## The fourth direction: a channel carrying two kinds of content where the reader expects one

*Added 2026-09-05 by lane B1. The sharpest of the three defects that session,
and the only one with no wrong number in it anywhere.*

`ce-pcb/bin/route --json > route-run.json` does not produce JSON.

Nothing in that sentence is a bug in `route`. It builds a report, calls
`json.dumps`, and prints it. But the DSN export and the SES import run inside
**pcbnew**, whose wxWidgets layer writes lines like

```
06:43:41 AM: Debug: Adding duplicate image handler for 'PNG file'
```

to **stdout, from C++**, where no Python-level redirect reaches them. So the
file is forty lines of noise followed by a valid JSON document, and
`json.load` answers `Extra data: line 1 column 2 (char 1)`.

**What that cost.** The caller was a shell line:

```bash
SES="$(python3 -c "...json.load(...)['ses']" "$VERIFY/route-run.json")"
```

`$( )` swallowed the traceback, `$SES` came back **empty**, the `--dsn`
argument was never passed, and `check_routed` graded a freshly routed board
**without the interchange file its tolerance comes from**. Its two
protected-copper assertions reported CANNOT DETERMINE — correctly, and for a
reason that had nothing whatever to do with the board. Every other row passed.
A reader skimming that report would have seen eight greens and two shrugs and
concluded the antenna had not been checked because it *could* not be, rather
than because a debug line from a graphics toolkit had eaten the argument.

**Why it belongs on this page.** It is the same family as the rest and the
giveaway is new. Elsewhere: a wrong number, or a capability nobody called.
Here the number is right, the tool is right, the caller is right, and the
**medium** is wrong — one stream carrying two kinds of content, where the
reader was built expecting one. It fails silently by construction, because
every participant is behaving correctly.

**The rule.** **Never parse a stream that something else can also write to.**
Machine-readable output goes to a **file the producer names**, or to a stream
nothing else touches. `--json > file` is a request for trouble the moment any
dependency links a C or C++ library, and you rarely know which ones do.
`route` now takes `--json-out PATH` and writes the report there, where no
library can reach it.

Three cheap habits that come with it:

1. **A flag that emits structured data should write a file, not a stream.**
   If it must use a stream, use stderr for logs and stdout for data *and say
   so*, then check that the dependencies honour it — measure, do not assume.
2. **Never let `$( )` swallow a parse.** The shell hands you an empty string
   and carries on. `route_board.sh` now REFUSES when the SES path comes back
   empty or names a file that is not there, and says why.
3. **An argument that silently defaults to absent is a hazard.** The reason
   this was caught at all is that `check_routed` treats a missing `--dsn` as
   CANNOT DETERMINE rather than picking a tolerance. Had it defaulted to a
   plausible number, the board would have been graded against an invented
   limit and the row would have been green.

## The third direction: a fix that was correct, and was never wired in

*Added 2026-09-05 by lane B1. Distinct from everything above, and the giveaway
is different.*

The entries on this page are checks that measured the wrong thing, plus one
capability wrongly declared absent. This is neither. Here the tool was
**right**, its diagnosis was **right**, it was **committed**, and there was no
way to invoke it from the place that needed it — so it was run by hand, or not
at all, and the failures it existed to prevent kept happening.

`ce-designs/halo/electronics/halo_rev_a/dsnfix.py` was written 2026-09-04 after
three autoroutes of halo_rev_a timed out at **900, 3300 and 2400 seconds**
while the same jar finished a Ø31.87 mm puck in 96 s. Its docstring names four
things KiCad's Specctra export says that are false about that board, and the
numbers are exact:

- `In1.Cu` and `In2.Cu` are **solid poured planes** and come out
  `(type signal)`, so the router carves channels through plane copper on two
  extra layers;
- GND (39 pins) and VDD (24 pins) arrive in `(network)` as **63 pin-to-pin
  connections** the pours and the stitching vias already make — 36 % of the
  pins, all of it wrong;
- the antenna and the NFC spiral come out `(type route)`, which in freerouting
  means **rippable**, so the only two pieces of copper on that board whose
  shape was *solved* are the two the router is free to destroy;
- (added 2026-09-05) the **fiducials have no clear field**, and every DRC error
  on the first successful autoroute was copper crowding one.

All of that was correct. And `cepcb.route.route()` went
`export_dsn → run_freerouting → import_ses` with **no seam between the first
two**, so nothing in the routing path could call it. The lane that wrote it ran
it by hand once; the lane that inherited the board did not know it existed and
concluded the board could not be routed.

**Measured after wiring it in** (`--dsn-filter`, one flag): 176 pins → **113
across 48 nets**, planes retyped `power`, 298 existing wires `protect`. The
route completed in **856 s** and took unconnected items **81 → 31**.

**The giveaway.** The other defects on this page announce themselves as a
suspicious green result — a PASS you can interrogate. This one has no result at
all. It looks like **a capability sitting in the tree unreferenced**: a module
nothing imports, a script no pipeline calls, a function with no caller. Nothing
is red, nothing is green, and the symptom shows up somewhere else entirely as a
job that is inexplicably slow or a lane that concludes the thing cannot be done.

**The rule.** When a tool exists to correct another tool's output, **the
correction belongs in the seam, not beside it.** If the fix has to be
remembered, it will not be. Two cheap tests:

1. **Grep for the caller.** A fix with no caller outside its own `__main__` is
   not deployed, it is available. `grep -rn "dsnfix" --include=*.py` returned
   the file itself and nothing else for a full day.
2. **Ask what the pipeline does if nobody remembers.** If the answer is "it
   silently produces the unfixed artifact", the seam needs the hook — and the
   hook must **refuse** when the fix was asked for and did not run, because a
   filter that failed leaves an artifact identical to one that needed no
   filtering. `apply_dsn_filter` raises on a non-zero exit for exactly that
   reason, and that refusal is negative-tested.

## The other direction: a capability declared ABSENT because the probe looked in the wrong place

*Added 2026-09-05 by lane B1, correcting lane B1, after the coordinator
measured the thing I had asserted.*

Everything above is a tool reporting success it had not earned. This is the
mirror image, and it is on the same page because **it is the same defect and it
costs the same night's work.**

I reported, in `STATUS.md`, in the factory pack's README and in a published
changelog entry, that **"there is no autorouter on this machine."** My evidence
was two commands:

```
java -version                       -> "Unable to locate a Java Runtime"
find ~/dev/ce-workshop -iname "*freerouting*"   -> nothing
```

Both outputs were real. Both conclusions were wrong.

- `/usr/bin/java` on macOS is **Apple's stub**, whose entire job is to print
  that sentence. Homebrew's openjdk is **keg-only** — deliberately not on
  `PATH`. `/opt/homebrew/opt/openjdk/bin/java -version` answers
  **openjdk 26.0.2.1**.
- The jar is not in the workshop tree because it is not workshop source. It
  lives at `~/.local/share/freerouting/freerouting-2.3.0.jar`, which is exactly
  where `cepcb.route.JAR_CANDIDATES` says to look — **the code I was about to
  give up on already documented the answer.**

**`ce-pcb/bin/route --doctor` exits 0 and prints five rows**, one of which reads
`jar runs → Freerouting v2.3.0 (build-date: 2026-08-07)`. That row exists
*precisely because a path is not a running program*, and it was green the whole
time. It was one command away and I did not run it.

**The rule.** A false negative and a false positive are the same failure of
method: a verdict inferred from a probe that was never shown to be able to
answer the question. Before reporting a capability ABSENT, ask **the tool that
owns it** — `--doctor`, `--selftest`, `health`, whatever that project's own
entry point is — and quote its answer. A generic probe (`which`, `java
-version`, a `find` rooted where you happened to be standing) is evidence about
*your search*, not about the machine. And the absence has to clear the same bar
as the presence: *"I could not find it"* is CANNOT DETERMINE, and I published it
as FAIL.

The tell, in hindsight: I wrote **"there is no autorouter"** and cited a
`find` over a single directory. If a claim's evidence is the *absence* of
output, name the places you looked and say the claim is bounded by them — or go
and ask the owner.

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


## The sixth direction: an HONEST sentence under a DISHONEST verdict

*Found 2026-09-05 by lane S2 (availability). The tool is `ce-fab/bin/fab bom cost --live`.*

`--live` promises to ask lcsc.com and jlcpcb.com about the bill of materials. It does — **for the
lines the local catalogue snapshot could not match.** Every line the snapshot *did* match is graded
against the snapshot, which was built 2026-09-03. The per-line prose says so, plainly and honestly:

> `` `U1` **FAIL** — needs 1000 but only 212 in stock **as of 2026-09-03** ``

**And the verdict above it does not.** It says `## 1,000 boards — FAIL`, in a report whose header
says `--live`, on a page whose whole subject is stock. **Nobody reads the footnote. Everybody reads
the verdict**, and the verdict is the thing that goes into a release pack.

Re-probing all 23 picks against both live endpoints on 2026-09-05 moved four of them:

| line | code | snapshot 09-03 | **live 09-05** | what the tool said |
|---|---|--:|--:|---|
| C19 | `C668326` | 5,874 | **29,352** | **FAIL** — it is a PASS, by 5× |
| X2 | `C843260` | 6,665 | **13,596** | **FAIL** — it is a PASS |
| L3, L4 | `C3911055` | 18,376 | **8,441** | PASS at 1k — stock had **halved in two days** |
| U1 | `C44800139` | 212 | **927** | FAIL — correct, but by 4.4× the wrong margin |

and two candidate parts read further out than any of those: `C423341` at **29,417 live against 1,167
in the snapshot — 25× low**, and `C237447` at **7,693 against 36,092 — a 79 % collapse.**

**Why this belongs on this page rather than in a bug report.** Every other entry here is a tool that
produced a number it had not derived. This one derives its number correctly — from the wrong
*epoch*. The snapshot was a true measurement of 2026-09-03. **Stock and price are the most perishable
numbers in this project**, and a two-day-old truth about them is indistinguishable in the output from
a live one. That is the same defect wearing a different coat: **a report not derived from the thing
it claims to have done.**

**It cost a whole lane's premise.** This lane was spawned to find alternates for two parts that had
already been fixed and four lines, two of which had restocked. Working the handed-down list instead
of re-measuring would have produced a second source for a screw terminal block.

**The rule.** *A verdict inherits the freshness of its weakest input, and it must say so where the
verdict is, not in a footnote.* Concretely, for this tool:

- a stock-based PASS/FAIL computed from a snapshot must **carry the snapshot date in the verdict
  line**, not only in the per-line reason — `## 1,000 boards — FAIL (stock as of 2026-09-03)`;
- `--live` should mean **live for every line the verdict depends on**, or be renamed to what it does;
- and the honest third state exists: a line whose stock could not be read live is **CANNOT
  DETERMINE**, never a snapshot number wearing a live label.

**The fix belongs in `ce-fab`, not in a warning.** Until it lands, `halo/tools/livestock.py` re-reads
any list of order codes from both endpoints with a per-run cache directory — because
`resolve_bom.py` caches to `/tmp/halo-sourcing` and will re-serve a stale page forever, **which is
this same defect one layer down.** Evidence:
`out/verify/alternates-live-2026-09-05.json`, 50 codes, each with its endpoint and the second it was
read.

**A second lesson from the same lane, and it is the sharper one.** Having re-measured, this lane then
wrote that L3/L4 had *no qualified alternate at 10,000 and would force a value change* — a
conclusion drawn from JLCPCB's catalogue alone. DigiKey holds **398,982** of that exact part.
**Measuring one channel carefully and then writing a verdict about all of them is the same error as
reading a stale snapshot: a true number, and a claim wider than the thing that was measured.** The
question to ask a verdict is not only *when* was this read, but *where did I look, and what did I not
look at.*

---

## An empty answer is not a measurement — and the tell is that it cost nothing

*Added 2026-09-05, after the same shape bit three different people on this
machine in one morning. It has its own section because it is the most common
of all the directions on this page and the easiest to miss: nothing is wrong
with the output, because there is no output.*

| the probe | what it returned | what it meant | what it nearly caused |
|---|---|---|---|
| `lsof` with no `timeout` binary present | rc 127, **empty** | the command did not exist | a liveness probe read the absence of output as "nothing is holding this file" |
| `fab bom cost --live` on a matched line | a confident verdict | it never fetched anything for that line | a stock verdict wrong in **both** directions, quoted as live |
| `find … -newermt '-40 minutes'` | **empty** | BSD `find` rejects that relative format and printed nothing | "no launchers were created", escalating a benign fan-out into a security question |

**The tell, and it generalises:** *the negative result required no work to
produce.* A search that genuinely looked and found nothing takes about as long
as one that finds something. A search that failed to start returns instantly.
When a probe comes back empty and fast, ask what it would have had to do to
answer, and whether it did any of it.

**The three cheap defences:**

1. **Check the exit status, always.** An empty result with a non-zero status is
   a failed probe, not a clean one. Two of the three above announce themselves
   this way and nobody looked.
2. **Give every probe a positive control.** Run it once against something you
   know it should find. A probe that has never returned a hit is not known to
   be capable of returning one — the same rule as an assertion never seen to
   fail.
3. **Prefer a tool that must name what it examined.** `ls -lt` on the directory
   answered in one command what the broken `find` could not, because it reports
   the contents rather than a filtered opinion about them.

This is the sibling of the rule at the top of this page. There, a tool reported
success it had not earned. Here, a tool reports an **absence** it has not earned
— and absence is more persuasive, because it looks like the world being simple.


---

## A setting that is read by nothing — the knob with no wire behind it

*Added 2026-09-05 by lane T3, from `ce-rf`'s `sim.min_cell_mm`. This one has no
false report at all: the tool never claimed anything. The lie was in the SPEC
FILES, written by people who believed they were configuring something.*

`sim.min_cell_mm` is ce-rf's mesh-line merge threshold — the number that decides
which of two nearly-coincident grid lines survives, and therefore the smallest
cell in the model, and therefore the Courant timestep the whole run pays. **13
antenna specs in that repo declared it. It was read by nothing.**
`fdtd.build_model` normalises a spec's `sim` block into the dict the runner
actually reads, and that dict did not carry the key, so
`s.get("min_cell_mm", fine / 3.0)` returned the default on every run ever made.

Three of those specs carry a paragraph of reasoning about the value:

> *"min_cell_mm 0.15 instead of the fine_res/3 = 0.0833 default. … The smallest
> cell sets the Courant timestep for the whole domain; merging mesh lines at
> 0.15 mm buys back the timestep."*

and one of the validation specs says a coarser mesh "would merge the staircase
into a smooth diagonal and **answer the question by construction**". Every one
of those runs wrote, in its own `solver.log`, one line above its own result:

```
[sim] mesh-line merge at 0.0833 mm: x 661->196, y 671->190, z 6->6
```

**Nobody had ever compared the two lines.** The spec said 0.15; the log said
0.0833; the log was right; the reasoning in the spec described a run that never
happened.

**What it cost, measured on the same spec with nothing else changed:**

| | before (default in force) | after (the declared value in force) |
|---|---|---|
| merge threshold | 0.0833 mm | **0.1500 mm** |
| cells | 1 584 128 | **1 065 792** (−33 %) |
| smallest cell | 0.08338 mm | **0.15000 mm** |
| timestep | 1.859 × 10⁻¹³ s | **3.061 × 10⁻¹³ s** (1.65×) |

And the consequence that mattered: with 0.083 mm cells sitting beside 3.70 mm
cells, the residual energy of every run in this family **floored**.
`halo-rev-a-2g4-meander9-bare` sat at **−34.87 dB from timestep 41 745 to
459 690 — flat to 0.01 dB over 418 000 timesteps** — against a −40 dB end
criterion. That is not slow convergence, and the standing fix in this repo
("let it run, the criterion is not lowered to meet it") could never have worked:
no number of extra timesteps reaches a floor it has already been sitting on for
90 % of the run.

### Why this shape is worth its own entry

The seven directions above are all *a report not derived from its effect*. This
one is **an input not connected to its effect** — the same break, upstream. It
is harder to see, because:

- **there is no error.** Unknown keys in a config are normally ignored on
  purpose, so the mechanism that swallows the setting is a feature everywhere
  else;
- **the prose around it is persuasive.** A paragraph explaining *why* 0.15 was
  chosen reads exactly like evidence that 0.15 was used;
- **and the default is usually reasonable**, so nothing looks broken. Here the
  default was *finer* than what was asked for — slower and more expensive, never
  visibly wrong.

### The three defences, and only the second one is new

1. **Log the value AND where it came from.** `mesh-line merge at 0.1500 mm
   (sim.min_cell_mm)` versus `at 0.0833 mm (fine_res_mm/3 default — the spec
   declared no min_cell_mm)`. A number with no provenance cannot be checked
   against the file that was supposed to supply it.
2. **Make the consumer refuse a mismatch.** The runner now raises if the
   threshold it merged at is not the one the spec named. A setting that can be
   silently dropped will be.
3. **Count over every input file, not over one.** The new self-test row walks
   *all* the specs on disk and reports "13 of 13 carry it into the model". Broken
   on purpose it reads "0 of 13" and names the files — which is the row that
   would have caught this on any one of thirteen occasions.

**The question to ask, and it is cheap:** for each knob a config file exposes,
*what would the run do differently if this line were deleted?* If you cannot
name the difference, grep for the key. If the only hit is the file you just
wrote, you have found one of these.

---

## The eighth direction: a checker looking at a channel the evidence never travels on

*Added 2026-09-05 by lane T3, from `ce-rf`'s `_run_capturing_fd`. The parser was
right. The self-test group grading the parser was right, and eight of its rows
were green for the right reason. What was wrong was the **text** the parser was
handed: it came from a pipe the evidence does not use.*

`ce-rf/out/halo-rev-a-2g4-meander4-bare/solver.log` says this on line 508:

```
[sim] convergence: OK -- openEMS ran to its energy end-criteria with a complete excitation
```

and this on line 547, in the same file, thirty-nine lines below it:

```
RunFDTD: Warning: Max. number of timesteps was reached before the end-criteria of -40dB was reached...
```

Two lines in one file, one of them the wrapper's summary of the other's author.
The same pair is in `-meander9-bare` and `-meander9-passive`.

**The cause, measured rather than reasoned about.**
`ce-rf/tools/prove_fd2_capture.py` runs a 200-timestep openEMS solve with file
descriptors 1 and 2 `dup2()`'d into two *separate* files and reports which file
each line landed in:

```
fd1.txt: 2660 chars, banner=True,  MARK=False
fd2.txt:  474 chars, banner=False, MARK=True
    >> openEMS::SetupFDTD: Warning, max. number of timesteps is smaller than three times the excitation.
    >> RunFDTD: Warning: Max. number of timesteps was reached before the end-criteria of -90dB was reached...
```

openEMS writes its banner, its mesh summary and its `Energy:` trace to **fd 1**,
and **every one of its warnings to fd 2**. `_run_capturing_fd` captured fd 1.
All four strings the convergence parser looks for are warnings. So the text the
parser received could not contain any of them, on any run, ever — and the
parser answered the only thing that text supports.

**The record was not a reading. It was the constant `True`.**

### What makes this one hard to see

This is the shape of *"an empty answer is not a measurement"* one level down,
and it defeats the usual tells:

- **the text was not empty.** 2 660 characters, the real openEMS banner, the
  real progress lines, the real `Energy:` trace. A `log_chars` field on the
  record showed a healthy number. The predecessor defect on this same function —
  `contextlib.redirect_stdout`, which cannot see a C extension at all — returned
  `""` and was caught by a fail-closed check on the banner. **This one passes
  that check.** It is a real engine log; it is just not the half with the
  evidence in it.
- **the parser was already under test, and its tests were already good.** Eight
  rows, including one built from the engine's warning verbatim, all green, all
  correct. They graded `convergence_from_log(text)`. Not one of them asked where
  `text` comes from.
- **the verdict was right anyway,** which is the worst part. `cerf.cli.
  _reconcile_convergence` re-derives the record from `solver.log`, and
  `solver.log` is stdout+stderr concatenated by the parent, so `solver_converged`
  graded **0.0 FAIL** on all three runs. Nothing was ever published wrongly.
  A wrong line under a right verdict has nothing to make it fall over.

### The defence

**Ask what channel the evidence travels on, and prove you are reading it — by
producing the evidence on purpose.** The new self-test rows do not mock a log
string; they run a fake engine that writes the banner to fd 1 and the warning to
fd 2 with `os.write`, and grade the capture:

```
capture-reads-fd-2              the capture is 181 chars and carries it
captured-fd-2-warning-goes-red  trustworthy=False
capture-keeps-fd-1              banner and Energy line still present
```

Deleting the one added `dup2` turns the first two red — `77 chars and DOES NOT
CARRY it`, `trustworthy=True` — which is exactly the failing form, and exactly
what three published runs had been printing. The third row exists because a fix
that gains fd 2 by losing fd 1 would satisfy the first two.

**The question to ask:** when a check reads *someone else's output*, what
produced the bytes, and would the thing you are looking for have been able to
reach you? Write a case that emits it deliberately. A checker that has never
once seen the string it searches for is not known to be able to find it.

---

## The inverse: measure the thing the tool cannot lie about

*Added 2026-09-05. Every other section here is about a report that cannot be
trusted. This one is about the answer you can get **without** asking the tool
anything.*

**A failing computation consumes proportionally more resources than a
succeeding one.** That makes resource usage a progress signal that no bug in the
tool's own reporting can corrupt, because nothing has to report it.

**The case that produced the rule.** An antenna solve wrote 9.1 GB of near-field
scratch across twelve surfaces, seven times any previous case, and the disk
pressure looked like a separate nuisance to be managed. It was not a separate
problem: the case **floors** at −34.87 dB against a −40 dB convergence
criterion, so it runs to its 460,000-timestep cap and records every one of those
timesteps. A converged case stops early and writes proportionally less.
**The disk symptom and the convergence defect had one root.**

The useful consequence is a free early signal: watching the scratch directory
grow tells you within minutes whether a run is converging, without waiting out
an eleven-minute solve and without reading the solver's own output — which in
this app is not even readable while a run is in flight, because it writes into an
unlinked temporary file.

**The same shape, elsewhere in this project:**

| what you want to know | what the thing itself says | what you measure instead |
|---|---|---|
| is this agent alive? | its status field says "running" | the **mtime of its transcript** — an agent that died at spawn holds its slot and reports running forever |
| is this solve converging? | nothing, until it finishes | the **growth curve of its scratch** |
| did this push succeed? | exit 0, because the pipeline's status is the last stage's | **`git ls-remote`** — ask the remote what it has |
| is this drill file this board's? | the exporter exited cleanly | **count the holes against the vias** |

**The rule.** When a tool's self-report is the only evidence, look for a physical
side effect of the work that the tool does not mediate — a file's size, a
timestamp, a count on the far side. It cannot be wrong about something it does
not know it is producing.

