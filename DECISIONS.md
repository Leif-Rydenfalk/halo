# DECISIONS — resolved by evidence, with what each one beat

*Every entry: the question, the evidence, the decision, and the option it beat.
A question is only escalated to Leif if it is a genuine product preference; a
matter of fact is resolved here (ce-workshop rule "resolve, don't escalate").*

## D1 — UWB: in or out? (2026-09-03)

**The tension.** Leif wants "a perfect copy of the internal airtag stuff", and
he wants his own sensors to know their position relative to each other. The
AirTag's Apple U1 does both jobs. Lane F's certification research recommends
**BLE only, no UWB**: a second radio means a second certification regime
(FCC §15.250 / ETSI EN 302 065), it is the densest part of Apple's patent
thicket, and the Apple side of Precision Finding is reachable only through the
MFi NDA — which is structurally incompatible with publishing the design.

**Decision: two variants from one design, not one compromise.**

| variant | radios | who it is for | cert path |
|---|---|---|---|
| **halo-core** | BLE only (nRF52-class, pre-certified module) | the open product anyone can build, sell or embed | modular approval, self-declared RED; the shipping default |
| **halo-uwb** | BLE + a sourceable UWB transceiver | Leif's own sensor fleet doing peer-to-peer ranging in his digital twin, and anyone doing the same on their own premises | not a sold consumer product; ranging is halo-to-halo, so no Apple handshake and no MFi is involved |

**Why this resolves it rather than splitting the difference.** The two uses do
not actually share a requirement. Apple's Precision Finding needs Apple's
blessing and gives Leif nothing for a sensor mesh, because it is a phone
walking up to one tag. Peer-to-peer two-way ranging between his own devices
needs no Apple involvement at all. So the copy stays faithful at the *function*
level — the UWB slot exists on the board, with a footprint and a feed — while
the shipped default populates it only in the variant that needs it.

**What it beat.** (a) UWB in the base design: it would push the open product
into a certification and patent regime that most builders cannot clear, for a
feature that does not work without Apple. (b) No UWB at all: it would leave
Leif's actual use case unbuilt, and lane F's recommendation was scoped to a
sold consumer tag, not an owner-operated sensor mesh.

**Open, for lane H to settle with numbers:** which UWB part, whether a CR2032
can support the ranging duty cycle, and whether Bluetooth Channel Sounding on
an nRF54L-class part reaches useful accuracy — in which case halo-uwb may not
need a second radio at all. That is a matter of fact and will be measured.

## D2 — the Bluetooth word mark (2026-09-03)

Lane F: Bluetooth SIG product qualification is **$12,000** under the schedule
effective 1 March 2026. **Decision: do not use the Bluetooth word mark or logo
anywhere in the product, packaging or documentation.** The radio is described
functionally ("2.4 GHz, compatible with Apple's Find My network"). Anyone
selling halo commercially at volume can qualify on their own account.
Beat: paying $12k so an open design may print a logo it does not need.

## D3 — battery door (2026-09-03)

Lane F: 16 CFR 1263 (Reese's Law) requires a tool, or two independent and
simultaneous hand movements, to open a coin-cell compartment on anything made
or imported after 19 March 2024. **Decision: press-and-twist bayonet (the
AirTag's own scheme) as the default, with a screw-down variant for the printed
enclosure.** A snap-fit printed lid is out — it fails the rule outright.
Beat: the easy snap-fit that every hobby enclosure uses.

## D4 — licences (2026-09-03)

Lane F's split is adopted: **CERN-OHL-S-2.0** for board and CAD,
**AGPL-3.0-or-later** for firmware and report tooling (OpenHaystack and
macless-haystack are AGPL, so derived firmware inherits it), **Apache-2.0** for
clean-room tools, **CC-BY-SA-4.0** for documentation. OSHWA self-certification
is free and will be filed once a module with a public datasheet is chosen.

## D5 — no MFi enrolment (2026-09-03)

Lane F: the MFi programme's terms make its Find My specification Apple
Confidential, so reading it and then publishing an implementation cannot both
happen. **Decision: clean-room only** — the design is derived from the PoPETs
2021 academic paper and public reverse-engineering, never from a leaked spec
mirror. Any contributor who has read the MFi spec must not touch the firmware.

## D6 — where halo actually wins (2026-09-03)

**The evidence.** Lane D priced the whole market bottom-up and top-down and
they agree: a Find My beacon is **about $1 in parts** (the AliExpress tags are
one Lenze ST17H66, a crystal and two capacitors, with *no antenna matching at
all*), a certified-class tag is **$3.50–$5**, Chinese B2B finished tags sell at
**$2.22–$2.52 at MOQ 100**, and Apple's own gen-1 manufacturing cost was about
**$10** against $29 retail. Lane D's verdict, adopted here: *"halo cannot win
on unit cost; that race is over."*

**Decision: halo competes on what is closed, not on price.** Being cheaper
than Apple is easy and is still a stated goal — the target is the $3.50–$5
certified-class band, roughly a sixth of Apple's retail — but it is not the
reason to build it. The reasons are the five things no tag on the market gives
you:

1. **Your own keys and your own backend.** Every commercial tag binds you to a
   vendor app and, for certified ones, to a per-unit Apple Token burned in at
   the factory. halo's keys are yours.
2. **Simultaneous Apple and Google broadcasting.** Every "dual network" product
   on sale makes you pick one at pairing. Lane D found this works in practice,
   and lane B found Google's Find Hub specification is public with **no
   open-source tag firmware in existence** — an unoccupied position.
3. **A documented debug header.** Certified tags from eufy and Motorola ship
   with debug pads on the board but undocumented; ours is a header with a pinout.
4. **A published bill of materials and design files** anyone can fork, in any
   outline, as an embeddable block.
5. **Peer-to-peer ranging between your own devices** (D1), which no consumer
   tag offers at all.

**What it beat.** Chasing the $1 board. It is reachable and it is pointless:
it means one unmatched antenna, no sounder, no DULT compliance, and a product
we said in docs/ANTI-STALKING.md we would not ship.

## D7 — dual network from the first board revision (2026-09-03)

Lane B: Google's Find Hub tag specification is public (service `0xFEAA`, frame
type `0x40/0x41`, roughly 1024 s ephemeral-ID rotation, DULT mandatory) and no
open-source implementation of a Find Hub tag exists. Lane D: no shipping
product broadcasts both networks at once, though it is technically possible.
**Decision: the firmware advertises on both networks concurrently**, and the
hardware is specified with the flash, RAM and current budget to do so from
revision A rather than being retrofitted. Beat: Apple-only first, Google later,
which would have frozen the BOM around the smaller flash part.

## D8 — DULT changes the BOM, and that is accepted (2026-09-03)

Lane B: DULT compliance is not a firmware checkbox on top of the OpenHaystack
advertisement. It needs a **connectable** advertisement set and a GATT service
alongside the non-connectable Find My beacon, plus an accelerometer accurate to
±10° and a sounder reaching **60 Phon at 25 cm**. That is flash, RAM, average
current and two parts. Lane B also notes DULT's own size test makes compliance
**required** for a 32 mm puck, not optional. **Decision: budget for it up
front** — the SoC is chosen with headroom over the 116.7 KB flash / 21.5 KB RAM
that a Find My stack alone needs, and the accelerometer and sounder are in the
core BOM, not the deluxe variant.

## D9 — redraw the copper, do not copy it (2026-09-03)

Lane C found the best layout donor is **RuuviTag Rev B8**: KiCad sources, a
round board, a working NFC-A antenna, a routed accelerometer, eight production
revisions. It is **CC BY-SA 4.0**, so copying its copper would make halo's
hardware share-alike under a documentation licence, colliding with the
CERN-OHL-S choice in D4. **Decision: study RuuviTag and Nordic's reference
layouts, then redraw every trace from the datasheets and application notes.**
The design files record which reference each block was informed by, so the
lineage is honest without the licence entanglement.

**Also refused as sources:** four projects lane C checked have **no licence
file at all** — Circuit-Digest's DIY-AirTag, Squall, heystack-nrf5x and
stacksmashing's airtag-hardware. No licence means all rights reserved. They are
read-only reference; nothing from them is vendored or copied.

## D10 — parity target is AirTag 2, not AirTag 1 (2026-09-03)

Lane C surfaced a February 2026 teardown of the second-generation AirTag: Apple
moved to an **nRF52840**, a UWB module, a Bosch accelerometer and an SPI
EEPROM. **Decision: the SoC target is nRF52840-class**, which also happens to
be what decision D8's flash and RAM budget demands once the Find My stack, DULT
and the Google network beacon are all resident. Beat: an nRF52810 or nRF52832
chosen for the older teardown, which would have been out of date on arrival and
short of flash.

## D11 — the sounder is the hard part (2026-09-03)

Lane C: Apple's voice-coil-driving-the-shell is not buyable as a part, a real
micro-speaker costs about $5.45 which is more than the rest of the board, and a
piezo costs cents but is quiet. Yet DULT makes **60 Phon at 25 cm** mandatory
(lane F). **Decision: the sounder is treated as an engineering problem with a
measured answer, not a part-picking exercise** — a piezo bender driven at its
resonance from a boost rail, with the enclosure cavity tuned as a Helmholtz
resonator, simulated in ce-spice for drive current and measured on a real board
against a calibrated meter before the design is released. If the measurement
fails, the fallback is a micro-speaker and the cost model absorbs it.

## D12 — the SoC is nRF54L-class with Channel Sounding; UWB is a reserved footprint (2026-09-03)
### This supersedes the nRF52840 pick in D10

**The measurement that decided it.** Lane H found a published study of Bluetooth
Channel Sounding on eight coin-cell-powered nRF54L15 devices: **6–10 cm mean
absolute error and 16–20 cm at the 90th percentile** over half a metre to five
and a half metres, line of sight. That is the same accuracy band as ultra-wideband
two-way ranging, from a radio that is already on the tag.

**The sourcing fact that closed it.** There is no ultra-wideband transceiver you
can buy a hundred of at LCSC today: the DW3110 shows 30 in stock, the DW3220
shows 9, and the DW1000, DW3210, DW3120, the DWM3000 module and the matching
antenna all show zero. NXP's parts are not in the catalogue at all. A design that
cannot be built is not a design.

**And the price runs the right way.** nRF54L05 is **$2.20** and nRF54L10 **$2.59**
at a hundred units, against **$2.81** for the nRF52832 and **$3.69** for the
nRF52833. Channel Sounding therefore costs **minus 61 cents per tag**, while
adding ultra-wideband costs **plus $8.86** — transceiver, antenna, crystal,
matching and bulk.

**Decision.** The v1 SoC is **nRF54L10**, falling back to the L05 if the firmware
fits its smaller memory and up to the L15 if it does not. Local relative
positioning is done with **Channel Sounding**, specified at 6–20 cm line of sight
and sub-metre in a real room, on a 30 second update, with the accelerometer's
orientation vector attached to every range. A **DW3110 footprint is reserved** on
the board as an unpopulated stuffing option for a high-precision variant.

**What it beat, and what this costs us.**
- It beat ultra-wideband in the base design, on stock, price and licence. The
  licence point matters for an open project: the Qorvo driver everyone vendors
  is under a licence with a *"Qorvo silicon only"* field-of-use clause and an
  anti-reverse-engineering clause. It is redistributable but **it is not open
  source and it is incompatible with the GPL**, so it cannot sit inside an
  AGPL firmware.
- It beat the nRF52840 of D10, and the honest cost is **a firmware port**. Every
  existing Find My implementation targets nRF52 silicon. Moving to the nRF54L
  family means porting rather than flashing something that already works, and
  the bring-up plan must budget for it. That is accepted because the alternative
  is shipping a tag that cannot do the one thing Leif needs it for.

**Two design consequences recorded now.** Use clock-offset-compensated
single-sided two-way ranging, never time-difference-of-arrival, because that
needs wired clock-synchronised anchors and GOAL.md rules out infrastructure.
And **tags report raw ranges with quality metadata, never solved positions** —
no tag can see the whole graph, and the solver belongs in the digital twin.

**Known gap, carried openly:** Channel Sounding accuracy degrades badly when
channels collide, 25 cm becoming 331 cm without deterministic scheduling, and a
single-antenna device can lose metres to orientation. The firmware must schedule
ranging deterministically, and that is now a requirement, not an optimisation.

## D11a — the sounder is settled: a bare piezo bender bonded to the shell (2026-09-03)
### Closes the open mechanism in D11

Lane G measured the problem and found the part. The stack budget leaves about
1.5 mm above the internal module, and the obvious catalogue buzzer — a TDK
PS1240P02CT, which gives exactly **60 dB(A) at 10 cm at 3 V**, precisely the
DULT requirement — is **3.5 mm tall** and does not fit. Apple's answer was a
voice coil bonded to the shell, which is not a part anyone sells.

**Decision: a bare Murata 7BB-20-3 piezo bender, Ø20.0 × 0.22 mm, bonded to the
inside of the shell**, driven anti-phase from two SoC pins so no boost converter
and no inductor are needed. This is Apple's trick — make the housing the
radiating surface — done with a catalogue part a fifth of a millimetre thick.

**What it beat.** A housed buzzer, on height. A micro-speaker, on cost, at about
$5.45 against the rest of the board. Apple's voice coil, on availability.

**What must still be measured, not assumed.** The only published AirTag loudness
figure is iFixit's **78–80 dB at about 13 cm**; Apple's "50% louder" for the
second generation carries no decibel figure or distance and must not be
converted into one. Our own board is measured against a calibrated meter before
release, and if the bonded bender misses 60 Phon at 25 cm the fallback is a
micro-speaker and the cost model absorbs it. Note also iFixit's finding that
piezo rivals were *"just as much, if not more, noise"* than the AirTag — Apple
chose the coil for sound quality, not for volume, and we are not selling sound
quality.

## D13 — enclosure and tooling (2026-09-03)

Lane G: **press-and-twist bayonet with three tabs at two, six and ten o'clock**
is the battery door, because it is the only Reese's-Law-compliant scheme that
costs **zero vertical height**. A screw costs 1.5 to 2.5 mm of the 1.5 mm we
have and puts metal inside Apple's Ø37.31 mm antenna keep-out.

**No two-shot moulding.** Tooling runs $45–95k and only repays above roughly
100,000 to 500,000 units a year. Two single-material mouldings plus a stamped
cover, with a first article off a $1,500–3,000 single-cavity aluminium tool.

## D14 — place the chip bare; no nRF54L module is both certified and castellated (2026-09-03)

Lane I wanted a pre-certified castellated module, because under 47 CFR 15.212 a
module carries its own radio grant and soldering it into any host outline does
not disturb it — which is exactly what halo's embeddable-block goal needs. Lane E
went to find one on the nRF54L silicon that decision D12 requires. **There is no
such part today.** The evidence, from vendor drawings read directly:

| module | silicon | pads | NFC pins | certification | stock |
|---|---|---|---|---|---|
| Raytac AN54LQ | nRF54L | **land-grid, not castellated** — its pads sit wholly inside the body, where the same vendor's older castellated part has lands protruding outward | yes, pads 15/16 | **certified**, nine regimes | — |
| Minew ME54BS11 | nRF54L | **castellated**, vendor says "the pad extending outward by 0.5 mm" | yes, pins 6/7 | **none — "planned"** | — |
| u-blox NORA-B2 | nRF54L15/L10/L05 | — | yes | **pending** | the only one with stock, 100 pieces |

**Decision: place the nRF54L10 bare on the halo board.** The certified module
route costs **+$1.16 per unit**, which is $1,160 at a thousand units and more
than a certification campaign; and an *uncertified* module is strictly worse than
bare silicon, since it costs more than the $2.40 chip and carries no grant.

**The distinction that settled it, and worth remembering:** castellation is a
*manufacturability* property, certification is a *legal* one, and the radio grant
travels with the module regardless of how it is terminated. So the two things
lane I bundled together are separable, and neither module offers both.

**What it beat.** The Raytac AN54LQ, on cost and on the fact that a land-grid
array cannot be hand-soldered into a hobbyist's board, which defeats the
embeddable-block purpose the module was chosen for in the first place.

**Revisit when:** any nRF54L module ships certified *and* castellated — the
u-blox part is the one to watch, since its certifications are pending rather than
absent. Until then the embeddable-block deliverable is served by the KiCad design
block that carries the routed antenna, not by a bought module.

## D15 — the cost target is met, and by more than expected (2026-09-03)

Lane E's second pass, re-pulled live: **bare nRF54L10 is $7.17 per unit at a
thousand**, against $9.25 for the nRF52840 build it replaces, $17.40 for the
abandoned ultra-wideband variant, Apple's roughly **$10** manufacturing cost and
their **$29** retail price. At ten thousand units it is $6.75.

Two smaller findings inside that number are worth keeping: the nRF54L05 sleeps
**0.9 µA lower** than the L10, which is a larger battery-life lever than its 39
cent saving, but it ships in a **3,000-piece minimum packet**; and the datasheet
transmit current is **3.7 mA at 0 dBm**, not the 4.8 mA the first pass assumed,
which feeds straight into the coin-cell model.

## D16 — the embeddable block ships as a KiCad design block, and the keep-out travels as words (2026-09-04)

GOAL.md deliverable 2 is that anyone can drop halo's circuit into their own board
in any outline. Lane T5 proved the mechanism and found its one real limit.

**What works, measured.** A KiCad 10 design block is a directory
`x.kicad_blocks/y.kicad_block/` holding a schematic, **a board fragment** and a
JSON descriptor. The format was read out of the KiCad library's own error
strings rather than from documentation, and the decisive sentence is *"Design
block does not have a schematic or board file"* — the layout is first class. A
test block carrying 9 footprints and 27 routed segments was applied into a host
board of a **different outline**, offset in both axes: worst pairwise footprint
error **0.000000 mm**, rotations unchanged, and the host's own design-rule check
clean at 0 and 0. So the routed antenna really can travel with the schematic,
which supersedes lane C's earlier finding that the copper always has to be
re-laid by hand.

**The limit, and it matters.** A design block carries **no design rules** and
**no symbol library**. Measured: the fragment's own check reported five clearance
errors that turn out to be KiCad's 0.2 mm fallback rather than anything the block
declares. **So halo's antenna keep-out cannot travel inside the block.** It must
ship as documentation the integrator reads and applies — the Ø37.31 mm region
with no metal above or below, and lane I's harmonised rule that the antenna end
sits on the host outline with 16 by 6 mm clear on every layer and ground pour
with via stitching on the other three sides.

**Decision:** publish the block *and* a one-page integration sheet stating the
keep-out and the ground requirements, and treat that sheet as part of the
deliverable rather than as supporting material. A block that places perfect
copper into a host that then floods ground over the antenna is worse than no
block at all, because it looks correct.
