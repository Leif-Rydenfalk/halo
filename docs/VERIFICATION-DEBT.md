# Verification debt — things reported as working that have not been proven

*Opened 2026-09-03. The rule this file exists to enforce: **a tool is not
working because a document says so; it is working because it ran and produced a
number.** MISSION.md requires every artifact in the release pack to be generated
by a tool on this machine and graded PASS. This page tracks the gap between what
the repository claims and what has actually executed.*

## Why this page exists

On 2026-09-03 the autorouter was found in the toolchain documentation as a
working step of the board pipeline. The jar was downloaded, the wrapper script
was written, and the workflow document described the command. **It had never
once run**, because this Mac has no Java runtime — `/usr/bin/java` is Apple's
stub, which prints "Unable to locate a Java Runtime" and exits. Nothing in the
project noticed, because nothing had asked it to route a board and checked the
result.

That is the failure mode this page is for: not a bug, but a claim that was never
tested. It is exactly what would sink a factory release pack, because the pack
is a set of claims about a board nobody has built.

## Open debt

| # | claim | status | what would close it |
|---|---|---|---|
| V1 | the autorouter routes a board | **CLOSED 2026-09-04.** OpenJDK installed; `bin/route --doctor` exits 0 and now asserts *the jar runs*, not that a path exists. Measured on the Ø31.87 mm puck: **11 unconnected → 0, with 0 violations**, reproduced three times | done |
| V2 | the Ø31.87 mm four-layer round board builds, routes and passes design-rule checks | **CLOSED 2026-09-04** for the outline and stackup: true circle on the edge layer, four layers, both planes, a 9-via array under the exposed pad, both keep-outs, routed clean, **29-file fabrication set exported**. Still open for *our circuit* rather than a placeholder | one fabrication set from the halo schematic |
| V3 | the electromagnetic solver is trustworthy | **being closed by lane T3** — the validation case reproducing a published reference antenna had not finished | the delta between simulated and published resonant frequency and bandwidth |
| V4 | the coin-cell model reflects a real cell | passes against its own datasheet-derived assertions, but has never been compared to a physical measurement | a real cell under a real pulse load, when hardware exists |
| V5 | the firmware advertises correctly | **proven in emulation only** — verified field by field against SPEC F1, but no radio has transmitted | a live scan seeing our own board, and a location report coming back |
| V6 | the parts database prices are current | the cache is dated; prices move | a re-pull with the date recorded on every line |
| V7 | the sounder reaches 60 Phon at 25 cm | **unproven and load-bearing** — DULT makes it mandatory, and lane G could only find one published AirTag figure (78–80 dB at about 13 cm) | a bonded bender in a real shell against a calibrated meter |
| V8 | Channel Sounding reaches 6–20 cm between two halos | taken from a published study on other hardware, not ours | two boards ranging to each other |

## The rule for every lane

When a lane reports something works, the report says **which command it ran and
what number came back**. "The pipeline is wired up" is not a result. A lane that
cannot run its step says CANNOT DETERMINE and names what is missing — which is
how V1 was found, and how the rest will be.
