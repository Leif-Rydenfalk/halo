# STACKUP — what the AirTag's PCB is made of, and what the Replica is drawn as

*halo Replica lane L4, 2026-09-05. Machine-readable twin: `stackup.json`.
Material data with its sources: `materials.json`. Tools: `../../tools/s_*.py`.*

> **CONVENTION.** **FRONT = the component side**, per Apple's own FCC filing,
> which labels it "MLB - Front". Colin O'Flynn calls that same physical face
> "backside". Where it matters below the face is named by what is on it —
> *component side* or *battery-contact side* — which is unambiguous under either
> convention.

> **THE RULE THIS FILE EXISTS TO ENFORCE.** **What Apple did** and **what we can
> make** are two facts and are never merged into one row. The Replica is the
> reference the other five variants are measured against. If it were drawn at
> whatever a process happens to allow, the reference would have already
> diverged and every downstream comparison would silently inherit that
> divergence with no document recording it. So both numbers, side by side,
> always.

---

## The answer in one table

| | **WHAT APPLE DID** | how well known | **WHAT WE DRAW** |
|---|---|---|---|
| board thickness | **0.30 mm** | REPORTED, never measured | **0.30 mm** as-drawn |
| layer count | **4** | **COUNTED**, confidence HIGH | **4** |
| construction | rigid glass laminate | consistent with the photograph | rigid FR-4 |
| surface finish | gold-bearing | **MEASURED**, in-frame control | ENIG |
| soldermask | dark and neutral | bounded; colour CANNOT DETERMINE | black |
| silkscreen | white | observed | white |
| copper weight | — | **CANNOT DETERMINE** | — |
| **orderable at 0.30 mm?** | — | — | **NO** — see the delta below |

---

## 1. Layer count — 4, and it was published all along

**This closes what `docs/REFERENCE-TEARDOWN.md` §3 and §7 carried as CANNOT
DETERMINE.** §3's words were *"never published. Likely 4."* It **was** published
— in a form the dossier read as carrying no count.

`github.com/stacksmashing/airtag-hardware` holds four files — `pcb/layer1.jpg`,
`layer2.jpeg`, `layer3.jpeg`, `layer4.jpeg` — with a README reading *"Contains
the merged PCB pictures of all the layers. All credits to David Hulton, who
delayed the PCB :)"*. The repo **states no licence**, so the images are cited
here and **not redistributed into this repo**; fetch them to reproduce anything
below. The directory would not render through WebFetch and was listed with
`gh api repos/stacksmashing/airtag-hardware/git/trees/HEAD?recursive=1`.

### The word that kept this open

Everything turned on **"merged"**. The dossier read it as *superposition* —
every layer visible in every image — which would make four files carry no count
at all. The other reading is that each image is stitched from several shots of
**one** layer.

The readings make opposite predictions at one spot, so it is testable:

| reading | prediction at a given board location |
|---|---|
| superposition | a feature on **any** layer appears in **every** image |
| delayering | a feature on one layer is **absent** from the others |

**The test.** `layer1` carries a fine-pitch **square land grid** with fanout
traces at box `[1330,1080,1600,1330]` — a feature only an *outer* layer can
have. The same board location on the others is box `[845,686,1017,845]` (they
are 1280 px wide against layer1's 2014, so the box is scaled, not moved).

**The result.** At that location `layer2` shows **no land grid at all** —
round via lands linked by thin traces cut out of a copper field. The grid is
absent exactly where superposition requires it to be present.

**These are four separate physical layers.**

### What each one shows

| file | reading |
|---|---|
| `layer1` | **OUTER, component side.** Dense fine routing, component footprints, a fine-pitch land grid consistent with the nRF52832 WLCSP, a second land array, three plated tooling/clip holes |
| `layer2` | **INNER.** Largely a copper pour with antipads and isolated islands, light routing, a cross fiducial. Plane-like |
| `layer3` | **INNER.** Long parallel traces running round the annulus, a pour on one side, the same fiducial. Routing-like |
| `layer4` | **OUTER, the other face.** Large round pads consistent with battery contacts and bulk capacitors, a small dense footprint, no fine land grid |

### Why the set is read as complete

- The sequence is **structurally closed**: outer-with-pads, inner, inner,
  outer-with-pads. A missing layer would have to be an inner one.
- All four share the same outline, the same centre hole and the same three
  plated tooling holes at the same positions — **one board, successively ground
  down, at consistent registration**.
- The author's own README says *all* the layers.
- Each image carries features the others do not, which is what rules out
  superposition in the first place.

### The corroboration, and why its timing matters

Two independent lines were derived **before these images were found**, and
committed at `98c6663` — timestamped, so neither can have been fitted to this
evidence:

- **thickness arithmetic → at most 4** in rigid FR-4 at 0.30 mm (§2)
- **routing necessity → more than 2** (§2)

Both brackets close on **4**. Three independent lines agreeing is what a real
confirmation looks like.

### Could these three have disagreed? — the test this claim has to pass

The orchestrator withdrew a finding today for calling two measurements
independent corroboration when both measured the same radial extent and so
**could not have disagreed**. The rule that came out of it: *name what each line
would have had to see to contradict the others, or they are one measurement.*

| line | what it would have had to show to contradict | could it have? |
|---|---|---|
| thickness arithmetic | 6 layers fitting comfortably in 0.30 mm | **yes** — and it nearly did: it only excludes 6 for *stocked rigid FR-4*, and the ultra-thin HDI rows are still null |
| routing necessity | a 2-layer escape and a usable reference plane | **yes** — a different layout would have falsified it |
| the delayering | six files, or the land grid present in every image | **yes** — superposition was the dossier's reading and was the expected outcome |

Their inputs do not overlap: laminate thicknesses off fabricator pages, package
escape geometry, and photographs of a ground-down board. **Three lines that
could each have gone the other way, and did not.**

### What is still not known

- **Which board was delayered.** The repo does not say whether it was
  production `820-01736-A` or the FCC sample `920-08283-01`. Whether those two
  share a stackup remains CANNOT DETERMINE and is not assumed anywhere.
- **Whether the vias are all through-holes**, or include blind/buried ones.
  Not tested. This decides whether the build is ordinary 4-layer or HDI.
- One person, one unit, not independently repeated.

**What would overturn it:** a cross-section showing copper the delayering did
not photograph. Note that a 6-layer board would *additionally* have to be an
ultra-thin HDI build to fit 0.30 mm — the arithmetic and this count would both
have to be wrong together.

### Two instruments were built for this and both were rejected

Recorded so nobody re-treads them.

1. **FFT periodicity probe.** A land grid is periodic; a pour is not.
   **Rejected because its negative control went red**: blank off-board
   background scored **10.55** against the real land grid's **8.28** — higher.
   On a nearly flat patch the whole spectral band sits near zero, so one
   JPEG-noise bin towers over the band average. Detrending and a median
   baseline were added; then *every* patch, background included, returned the
   lowest bin in the band at a suspiciously round 32.0 px. **Abandoned rather
   than tuned** — tuning a threshold until the answer comes out right is the
   defect, not the fix.
2. **Edge-density probe.** Its controls *do* pass — blank background 0.0153 and
   0.0294 against 0.2541–0.4684 for any patch of board, better than tenfold.
   But it cannot separate a land grid (0.4684) from ordinary inner-layer
   routing (0.2541–0.3492); that is one continuum, not two categories. **Kept**
   as `s_layerprobe.py`, which **exits 2** on the layer question and says so.
   Its honest contribution is the negative control: it proves the compared
   patches all hold real copper rather than blank photograph, which is the one
   way the visual reading could have been trivially wrong.

What settled it was **the eye on named, reproducible crops**. That is written
down because an automated instrument was tried twice and neither earned the
answer.

---

## 2. The arithmetic that bracketed it — and still bounds the build

`s_stackup_budget.py` never takes a layer count as an input to be confirmed.
**Thickness in, layer counts out.** A tool that starts from an assumed count
and concludes that count is a check that can agree with what it checks.

```
$ s_stackup_budget.py bounds 0.30
construction      N  cores  preg    diel      Cu  laminate           +mask   verdict
fr4-economy       2      0     1   0.065   0.070     0.135   0.155-0.175    FITS
fr4-economy       4      1     2   0.230   0.105     0.335   0.355-0.375    DOES NOT FIT
fr4-thin          2      0     1   0.050   0.050     0.100   0.120-0.140    FITS
fr4-thin          4      1     2   0.200   0.074     0.274   0.294-0.314    FITS
fr4-thin          6      2     3   0.350   0.098     0.448   0.468-0.488    DOES NOT FIT
fr4-thin          8      3     4   0.500   0.122     0.622   0.642-0.662    DOES NOT FIT
hdi-ultrathin     *   CANNOT DETERMINE — core.ultrathin_hdi has no thickness
```

**Provenance, and it now travels with the number.** `materials.json` tags
`outer_finished_copper.thin` and `copper_foil.0.33oz` as **inferences** — the
first is arithmetic on a foil weight with no fabricator page behind it, the
second is IPC-4562's nominal 12 µm, not fetched. **`fr4-thin` pulls both**, and
`fr4-thin` carries this lane's entire upper bound. That tag was sitting in
`materials.json` and **was not reaching this page** until an audit on
2026-09-05 — the exact shape this lane criticised in someone else's document on
the same day. `bounds` now prints `C!` against every row whose copper leans on
an inference, so the caveat cannot walk away from the number again.

**What that does and does not touch.** It touches the **laminate totals**
(0.274, 0.448, 0.622 mm). It does **not** touch the dielectric column: `core`
and `prepreg` are published rows in every construction, and no row carries
`D!`. So the load-bearing sentence below — *0.350 mm of dielectric alone,
before a micron of copper* — rests on published thicknesses only, which is why
it was written that way.

**Upper bound.** Six layers needs 2 cores and 3 prepreg sheets. At the
published thin end of stocked rigid FR-4 — 0.10 mm core, 0.050 mm type-106
prepreg — that is **0.350 mm of dielectric alone**, already over target before
a micron of copper. Eight needs 0.622 mm of laminate. Four lands at **0.274
mm**, *at* the target rather than comfortably inside it — which is itself a
finding: **0.30 mm is not a relaxed choice for a 4-layer board, it is close to
the floor.**

**Lower bound — labelled an inference, not a measurement.** More than 2:

- The nRF52832-CIAA is a 50-ball WLCSP. On a fine-pitch WLCSP only the outer
  ball rings escape on the component layer; interior balls must drop through
  vias. *(The ball-array geometry was not confirmed against Nordic's datasheet
  — that fetch redirected and was not chased.)*
- On a 2-layer board those vias land on the battery-contact face: 3 sprung
  contacts, the wound NFC coil pads, 5 × 100 µF bulk capacitors, 38 named test
  points, two speaker-coil joints. Not free routing area.
- A 2-layer board has no interior reference plane. The BLE feed, the UWB feed
  at 6.5/8 GHz and a 32 MHz crystal would all reference a face that is
  populated, split and covered in test points. Apple's FCC-reported gains
  (−3.2 dBi BLE, −1.6/−0.6 dBi UWB) are not what such a board produces.

### The hole is now smaller, and HDI turned out not to rescue 6 layers

*Added 2026-09-05, closing handoff item 2. It does not change the count — §1
counted it — it changes how strong the arithmetic that agreed was.*

PCBWay publishes HDI floors, verbatim: *"the minimum core thickness for laser
blind vias is 0.1mm"* and *"the minimum PP thickness for laser blind vias is
0.06mm"*
([hdi-pcb.html](https://www.pcbway.com/hdi-pcb.html), fetched 2026-09-05).

**The surprise: HDI is not thinner.** Its minimum core is the *same* 0.10 mm as
stocked rigid FR-4, and its minimum laser-drillable prepreg at 0.060 mm is
**thicker** than the 0.050 mm type-106 used in `fr4-thin`. So:

```
$ s_stackup_budget.py bounds 0.30
hdi-pcbway-published  4      1     2   0.220   0.060     0.280   0.300-0.320    FITS
hdi-pcbway-published  6      2     3   0.380   0.084     0.464   0.484-0.504    DOES NOT FIT
```

**6-layer HDI is worse than 6-layer thin FR-4** — 0.464 mm of laminate against
0.448 mm. At *every* construction whose material thicknesses anybody publishes,
**6 layers does not fit in 0.30 mm.**

The `hdi-ultrathin` rows **stay null**. Any-layer HDI with cores below any
published prototype floor is a real thing that Apple's suppliers run, and no
page giving such a number has been fetched. What narrowed is the gap between
"published capability" and "unpublished", not the gap itself. And this settles
the arithmetic only — it does not raise the confidence of any neighbouring row.

**The hole that was left open, honestly.** The upper bound assumes stocked
rigid FR-4 with a 0.10 mm core floor; Apple's suppliers are not prototype
houses. The `hdi-ultrathin` rows in `materials.json` are **deliberately null**
and the tool **exits 2** rather than evaluate them. Filling that row from
memory would have manufactured exactly the certainty this lane exists to
refuse. The delayering evidence closed the question from a different direction
instead.

`s_stackup_budget.py doctor` → 0. `selftest` → 9/9, and **two deliberate breaks
were watched to go red**: defaulting a null row to a plausible 0.05 mm went 1
red, and pinning cores and prepreg to constants went 2 red. That second break
**sailed through the first version of the test**, because copper alone still
grew with the layer count while the dielectric had stopped. *"The total went
up" is not a test that the thing depends on the variable.*

---

## 3. Thickness — 0.30 mm, reported and never measured

Colin O'Flynn, in passing: *"it's 0.3mm PCB so I'm pretty sure I broke some
solder joints getting it out."* Adam Catley corroborates independently —
*"Removing the PCB is likely to cause damage due to the thin PCB"* — but that
corroborates **thin**, not **0.30**. No error bar was ever published with it.

**Attempted and failed.** No published photograph shows the board edge-on. FCC
internal photo 6 is the best-scaled frame at 15.887 px/mm (L1), where 0.30 mm
spans **4.8 px** and the board lies flat. O'Flynn's backside scan at ~90–110
px/mm would resolve 0.30 mm as 27–33 px, but it is flat-on too. **Discarded on
the resolution arithmetic, stated before interpreting, not on a failed
eyeball.**

**What would settle it:** a caliper on a bare MLB, a scale-referenced edge-on
photograph, or a cross-section.

---

## 4. Surface finish — gold-bearing, measured against an in-frame control

A finish cannot be read off a colour *name*. It can be read off a **hue
difference between two metals in the same frame under the same light**, because
a white-balance error moves both together. That is why the control is not
optional.

`s_colour.py` on `oflynn-backside-fullres.jpeg`:

**Two statistics, in order.** **Warm fraction** says whether the region is bare
metal at all; **hue** then says which metal. The first version of this
measurement reported hue only — over a *warm-pixel selection* — so it could
never say "this region is grey", because the selection had already discarded
the grey.

| region | **warm %** | **hue** | sat | reading |
|---|---|---|---|---|
| **copper CONTROL** — the winding of a wirewound inductor | **64.9 %** | **21.8°** | 0.480 | bare metal, copper |
| plated hole rim, right | **66.0 %** | **43.8°** | 0.575 | bare metal, gold-bearing |
| plated hole rim, left | **98.8 %** | **40.5°** | 0.567 | bare metal, gold-bearing |
| grey solder fillet — **negative control** | **4.6 %** | 35.0° | 0.413 | **not bare metal** |
| dark soldermask — **negative control** | **8.8 %** | 52.9° | 0.187 | **not bare metal** |

**The negative controls were asserted here for a day before anyone ran them.**
This page used to say HASL, tin and silver are *"grey, R≈G≈B, with no warm
pixels at all"*. Measured, both non-metal regions are rejected **by warm
fraction** — 4.6 % and 8.8 % against a 40 % floor — and **not by hue**. On hue
alone the dark soldermask sits at **52.9°, inside the gold band**: hue alone
would have called soldermask a gold finish. The grey solder at 35.0° would have
landed in the uncalled gap. One false positive and one refusal.

*The control is the winding of a wirewound inductor — magnet wire, whose thin
enamel reads as copper — not literally bare copper. The conclusion survives the
enamel: any tint it adds pushes toward red, i.e. **lower** hue, widening the
separation rather than creating it.*

**19–22° of hue separation from the in-frame copper control, *and* both rims at
66–99 % warm fraction against 4.6–8.8 % for the two non-metal controls.** The
rims are bare metal and they are not copper. HASL, immersion tin and immersion
silver are excluded because they are grey and fail the warm-fraction floor —
which is now measured rather than asserted.

**Still CANNOT DETERMINE: *which* gold finish.** ENIG, ENEPIG, immersion gold
and hard gold are indistinguishable by hue in a JPEG. XRF or a cross-section
would separate them.

*Supporting inference, labelled as such and not used to reach the result:* a
50-ball WLCSP and 0201 passives need a coplanar finish, and HASL cannot hold
coplanarity at that scale.

---

## 5. Soldermask and silkscreen

**Soldermask: dark and neutral. Colour CANNOT DETERMINE.** Flat mask patches
read V = 65–128 against a white background control at V = 224 in the same
frame, R, G and B within about 10 counts. It is **not** green, blue, red or
white. It goes no finer than that: the apparent violet cast (hue ≈ 270° at
saturation 0.14) is **inside what an unknown camera white balance produces on a
near-neutral dark surface**, so calling it purple would be *reading a camera
setting as a material property*. Settled by the board beside a colour checker,
or in hand.

**Silkscreen: white.** `820-01736-A` and `2920 17` are legible light-on-dark in
O'Flynn's front-side scan; on a dark mask, legible legend is white.

**Copper weight: CANNOT DETERMINE.** Copper weight is a thickness and no
photograph of this board shows a thickness. No teardown states it. A
cross-section or a fab drawing settles it.

---

## 6. Apple's board part numbers — these are TWO boards

**They are not merged anywhere in this project.**

| | **production** | **FCC sample** |
|---|---|---|
| legend | `820-01736-A` | `920-08283-01` |
| data code | `2920 17` | `3119` |
| face | component side | the NFC side |
| source | O'Flynn front-side scan | FCC internal photo 5 |

Different Apple number series, and a **2019** data code against production's
**2020**. This is an earlier engineering build, not the same board with a
second marking. `REFERENCE-TEARDOWN.md` §7 lists *"whether the FCC-sample board
differs electrically from production"* as open, and it still is.

**Consequence for this lane:** every stackup fact here comes from photographs
of the production board except where an FCC photo is named — and the delayered
board's identity is itself unstated (§1).

---

## 7. Antennas, and what they do and do not constrain

L1 tested the hypothesis that the BLE and UWB antennas are etched in board
copper — raised by Apple's own arrows in FCC photo 6 — and **refuted it** at
~90–110 px/mm: no meander, no inverted-F, no patch in the outer copper of
either face. They are on the plastic carrier.
(`evidence/E01-ARE-THE-ANTENNAS-ON-THE-BOARD.md`, commit `52d2931`.)

For the stackup this **removes an antenna-clearance constraint** — no layer has
to be kept clear under an on-board radiator. It **does not remove the
reference-plane requirement**: the feeds still cross the board to the rim
joints, and that is what carries the lower-bound argument in §2.

---

## 8. The fabrication delta — WHAT WE CAN MAKE

Published capability pages only. **No account was created, no quote requested,
nobody contacted, no money spent.** A number that needs an account to see is
CANNOT DETERMINE.

| house | 1–2 layer min | **4 layer min** | 6 layer min | 0.30 mm at 4 layers? |
|---|---|---|---|---|
| [PCBWay](https://www.pcbway.com/capabilities.html) | 0.20 mm | **0.40 mm** (0.60 normal) | 0.70 mm | **NO** |
| [JLCPCB](https://jlcpcb.com/capabilities/pcb-capabilities) | 0.40 mm overall min | — *(row unverified)* | — | **NO — below their minimum at any layer count)** |

PCBWay's listed thicknesses are 0.2, 0.4, 0.6, 0.8, 1.0 … — **0.30 mm is not
one of them at any layer count.**

> **The delta in one line:** the Replica as drawn — **0.30 mm, 4 layers** — is
> **not orderable from either house**. Building it needs an HDI house whose
> capability page has not been read, or a stated departure from as-drawn.

**A departure is PROPOSED and NOT ADOPTED.** 0.40 mm is the nearest orderable
thickness above 0.30 at both houses and is PCBWay's 4-layer floor — a **+0.10
mm, +33 %** departure. **The drawing does not move.** The as-drawn number is
Apple's; the delta is ours; collapsing them is the precise failure
`THE-DRIFT.md` is about. Whether to spend money on a board at all is the halo
lane's call, not this one's.

**And what none of this means:** *nothing about Apple.* These are prototype
houses. Apple's suppliers build at volumes and tolerances no prototype
capability page describes. A capability page bounds **what we can order**; it
does not bound **what Apple built**.

---

## 9. What was considered and thrown out

| hypothesis | why discarded |
|---|---|
| **"4 layers, because 4 is plausible"** | Discarded **as a reason**, while the number turned out right. §3 said "likely 4" with nothing behind it; this lane refused it and recorded [4,6]. Had the answer been 6, plausibility would have written the wrong number into every downstream document permanently. **A guess that lands on the truth is still a guess.** |
| "*Merged* means superposition, so four files carry no count" | The dossier's reading, and wrong. Tested at a named spot: layer1's land grid is **absent** from layer2. "Merged" means each image is stitched from several shots of **one** layer. **One word read the wrong way kept this open.** |
| 6+ layers, from the board's density | Not discarded — **bounded**. 6 needs 0.350 mm of dielectric alone in rigid FR-4; 8 needs 0.622 mm of laminate. Then counted at 4. |
| Flex or rigid-flex construction | Considered — 0.30 mm is flex territory and it would have made 6 layers easy. Discarded on the **pale yellow cut-laminate edge** visible under the dark mask (polyimide cuts amber-translucent), and on a component load — shield can, 50-ball WLCSP, 5 bulk caps — that is not put on flex without a stiffener, and no photograph shows one. **Not** discarded for an ultra-thin core *inside* a rigid stack. |
| Measuring thickness off a photograph | 4.8 px at the best-scaled frame, and no edge-on view exists. Discarded on resolution arithmetic. |
| "The soldermask is purple (hue ≈ 270°)" | Saturation 0.14 on a near-neutral dark surface is inside white-balance error. Would be **reading a camera setting as a material property**. |
| "A prototype house's minimum tells us what Apple could build" | It tells us what **we** can order. Fusing the two is the error §8's structure exists to prevent. |

---

## 10. Still open

| item | state | what settles it |
|---|---|---|
| Vias — through-hole, or blind/buried? | **CANNOT DETERMINE**, not tested | compare via land positions between `layer1` and `layer4`. Images already in hand — real work, not an escalation |
| Board thickness | REPORTED 0.30 mm, never measured | a caliper on a bare MLB |
| Copper weight | **CANNOT DETERMINE** | a cross-section |
| *Which* gold finish | **CANNOT DETERMINE** within the family | XRF or a cross-section |
| Whether `920-08283-01` shares production's stackup | **CANNOT DETERMINE**, not assumed | a 2019 EVT unit against a retail unit |
| Which board was delayered | **CANNOT DETERMINE** | the repo author |

---

## Tools

| tool | what it does |
|---|---|
| `s_stackup_budget.py` | the layer arithmetic. `doctor` `budget` `bounds` `selftest`. Exit code **is** the verdict — 0 / 1 / 2. Never takes a layer count as an input. 9 selftest cases, breaks watched to go red |
| `s_colour.py` | hue of a metal region **against an in-frame control**. Refuses a box with no warm pixels rather than averaging shadow |
| `s_layerprobe.py` | structure-vs-blank control for §1. **Exits 2 on the layer question by design.** Its docstring records the FFT probe rejected when its negative control went red |
| `s_crop.py` | crop + Lanczos upscale. No sharpening, no contrast stretch, no gamma |

---

## Handoff — what this lane was about to do and did not

Stood down mid-lane on a fleet quota stop, not because the work ran out. In
priority order:

1. **Are the vias through, or blind/buried?** The single highest-value open
   item, and it needs **no new evidence** — compare via land positions between
   `layer1` and `layer4` in the delayering set. A land on one outer face with no
   counterpart on the other is a blind via, which would make this an HDI build
   and would bear on copper weights and on how aggressive 0.30 mm was for Apple.
   The images are already fetchable; `s_layerprobe.py` has the registration
   boxes.
2. ~~**The HDI capability page.**~~ **DONE 2026-09-05** — see §2. PCBWay's
   published HDI floors are in `materials.json` as `hdi-pcbway-published`, and
   the result is that HDI does *not* rescue 6 layers. Three further pages
   (Würth, Hemeixin, NextPCB) publish no dielectric minima; two of them invite
   you to email their engineers, which this lane does not do. **What is still
   missing is an any-layer HDI floor below 0.10 mm**, and `hdi-ultrathin` stays
   null until a page gives one.
3. **Confirm the nRF52832-CIAA ball array** against Nordic's datasheet, to firm
   up the §2 lower bound. That fetch returned a redirect that was not followed:
   `http://docs.nordicsemi.com/r/bundle/ps_nrf52832/page/pin.html`. The bound
   does not depend on it now that the count is settled, but the inference is
   quoted and should be sourced or softened.
4. **A contradiction inside `docs/REFERENCE-TEARDOWN.md`, not this lane's to
   fix.** Its header says *front = the component side* (Apple's filing), while
   §2's legend says *"**F** = front/top side (battery contacts, coil, NFC)"* —
   the opposite face. One of the two is stale. Flagged, not edited: it belongs
   to the lane that owns that document.

Nothing here is blocked. Every item is a reading or a measurement available
from this machine.
