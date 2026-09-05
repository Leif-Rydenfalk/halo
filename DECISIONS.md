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

## D17 — the stack closes with 1.742 mm recovered, and the shell is flat inside (2026-09-04)

**The budget was wrong in our favour.** SPEC section 4 said about 1.5 mm remained
after the cell and the internal module. That figure measured *Apple's* 3.30 mm
module, which contains a magnet and a voice coil. Decision D11a's 0.22 mm piezo
bender deletes both, so halo's equivalent row is **1.558 mm** and **1.742 mm
comes back**. Lane M spent it on a **0.60 mm PCB** instead of Apple's fragile
0.30 mm, a 0.680 mm diaphragm gap and a 1.430 mm crown, leaving 0.542 mm of dead
air under the cell that a flat pad embossed in the door could still recover.

The assembly measures **31.874 by 31.874 by 7.980 mm**, matching Apple's drawing
to a thousandth of a millimetre, with the maximum diameter falling at z 4.263 to
4.384 where Apple's drawing puts 4.339. Mass is 7.8 g against the AirTag's 11 g;
the difference is Apple's motor.

**The constraint that would have broken parts on the line.** The shell keeps
Apple's R92 spherical cap on the *outside* for looks, but its **inside is a flat
land**. Conforming a 20 mm piezo bender to R91.2 strains its ceramic to
**0.1377 percent**, past the roughly 0.1 percent limit for the material — it
would crack during assembly, in a way that would pass every visual inspection and
fail in the field. The wall is 0.800 mm, chosen so the bender still keeps 66
percent of the crown's bending stiffness. Every undercut sits on the carrier, so
the cosmetic shell is a pure straight pull with no side action.

**Three checks went red before they went green**, and all three were real: a door
that could not be opened, 0.134 mm³ of the cell intersecting the door, and a
printed variant whose thicker wall buried it in the seal land. Each was fixed by
moving geometry. **No check was loosened**, and both failure rows stay in the
ledger.

**Two divergences from the brief, on purpose.** The piezo bonds to the shell, not
the carrier, because the shell is the diaphragm. And the printed variant keeps
the bayonet rather than a screw, because a printed bayonet needs no tooling and
still satisfies the two-independent-movements rule.

**Two of lane G's six open bench measurements are now moot** — the magnet and the
coil are deleted by D11a. Two more, the PCB outline and the wall thickness, turn
out to be halo's own choices rather than measurements of Apple. A seventh is
added: Apple's plan-view callouts Ø27.90 and Ø27.84, which the redistributable
half-section omits, are read here as the shell's bore and the carrier's leg
circle and should be confirmed against a real part.

## D18 — the memory budget was never the constraint (2026-09-04)

D8 budgeted the chip for DULT, Find My and Google Find Hub together, over a
quoted 116.7 KB flash and 21.5 KB RAM. **Measured, halo's firmware on an
nRF54L10 uses 13,164 bytes of flash — 1.27 percent — and 704 bytes of RAM.**

The two numbers answer different questions and both are right. The quoted figure
is a full stack including the Bluetooth link layer and connection handling.
halo's is the protocol layers only: no link layer, no connection established, the
DULT opcodes graded as a pure function. **The expensive part of DULT is the
transport, and it is not written yet.** When it is, this row must be re-measured
rather than assumed still fine.

Consequence: the nRF54L05 fallback in D12 is not forced by memory, and the
choice between L05 and L10 comes down to the L05's 0.9 µA lower sleep current
against its 3,000-piece minimum packet (D15). That is a sourcing question for the
factory, not a firmware one.

## D19 — halo implements the Google Find Hub tag, and it appears to be the first open one (2026-09-04)

Lane B found no open-source implementation of the Google network's *tag* side
anywhere, and lane D found no shipping product that advertises both networks at
once. Lane T4 wrote it from Google's published specification, byte for byte
against its Tables 15 and 17, with the specification archived locally, and
verified it against a reference implementation using independent cryptography.
Cost: **2,888 bytes of flash and 116 of RAM.** Both networks now transmit in the
**same advertising event** on all three channels, so the interval is one event
period rather than three.

That makes decision D7 real rather than planned, and it is the sharpest edge in
D6's list of what halo offers that nothing on sale does.

**One row cannot be closed and is left open on purpose:** the DULT Network ID.
The draft points at a registry it subsequently removed, so halo advertises `0x00`
meaning UNREGISTERED rather than borrowing Google's `0x02`, which would be a
false claim about who we are. `check-dult` therefore reports 16 rows passing and
one CANNOT DETERMINE, and its overall verdict is deliberately exit 2 rather than
a pass.

## D20 — the sounder part is Same Sky CEB-2021; the Murata is obsolete (2026-09-04)
### Supersedes the part choice in D11a; the acoustic reasoning in D11a stands unchanged

**D11a's part cannot be bought.** The Murata 7BB-20-3 is dimensionally perfect —
Ø20 mm brass, 0.22 mm, 3.6 kHz, 20 nF — and Digi-Key lists it **obsolete with
zero stock**. It is not on LCSC at all. Four related Murata parts were **delisted
from LCSC**, and JLCPCB's parts library still lists them at zero stock, which is
a stale catalogue rather than availability. Sourcing lane verified nine candidates
against manufacturer mechanical drawings rather than listing titles, on 2026-09-04.

**The physical finding that constrains the choice.** At Ø20 mm, **thin and
high-frequency are mutually exclusive**. Every 6.3 to 7.2 kHz element checked —
across Murata, PUI and Same Sky — measures **0.42 to 0.43 mm**. Elements in our
0.15 to 0.30 mm window all land at **3.6 to 4.2 kHz**. The stack decides the
frequency, and the stack has already spent 0.372 mm of D17's 0.542 mm of slack
on a part-height conflict, so thickness is the binding constraint.

**Decision: Same Sky CEB-2021** — Ø20.0 × **0.21 mm**, brass, 3.6 kHz
(3.1–4.1), 21 nF, ≤300 Ω, **3,756 in stock**, $0.62 at ten and **$0.299 at eight
thousand**. It is chosen over the alternatives because at 0.21 mm it is
**thinner than the 0.22 mm D11a assumed**, so it costs the stack nothing and
carries no risk to a budget that is already tight.

**Alternates, in order.** PUI **AB2040B** — 0.28 mm, 4.0 kHz, 25 nF, **14,125 in
stock**, the deepest supply and slightly better placed for perceived loudness,
but it spends 0.06 mm of stack. And **FUET FT-20T-4.0A1** (LCSC C48542877) at
about **$0.05 per piece at ten thousand**, six to ten times cheaper than the
Western parts — but LCSC holds only 75 pieces, so a production run means ordering
direct from the manufacturer and the LCSC listing is sourcing proof, not a
supply channel.

**Two parts rejected for a reason worth recording:** PUI AB2036AF has an alloy
rather than brass plate **and a feedback electrode**, making it a three-terminal
self-drive element; and FUET FT-20T-4.2B1-C25 lists a second capacitance, which
strongly implies the same. Our drive is two GPIO in anti-phase (D11a), so a
three-terminal feedback element is the wrong topology and would need an approval
drawing before anyone committed to it.

**Frequency note for the loudness question.** Human hearing is most sensitive
around 3 to 4 kHz, so a 3.6 kHz element is well placed for the phon measurement
the anti-stalking standard demands, despite being the low end of what the
thickness allows. That remains a measurement, not an argument — see the
hardware-required section of the verification debt.

**Sourcing caution recorded for every lane:** JLCPCB's parts search works
unauthenticated and is the only usable free-text search over the LCSC catalogue,
but its stock figures are JLC assembly stock and it **retains delisted parts**.
Always re-verify a part number against LCSC's own detail endpoint before trusting
it.

---

## D21 — controlled impedance: 0.127 mm is 51.9 Ω, and JLCPCB will not sell it at 0.60 mm (lane B1, 2026-09-05)

**The premise this lane inherited was wrong.** The open item read *"a 50 Ω
microstrip needs 0.086 mm on this stack, below the process floor"*. It does not.
0.086 mm came from a dielectric height nobody had retrieved —
`electronics/README.md` §11 says so in as many words: *"the fab's 0.60 mm
4-layer dielectric heights were never retrieved."* Retrieved now, from the two
houses that publish them.

### What a 0.60 mm four-layer board actually is

| house | 0.60 mm 4-layer offered? | impedance CONTROLLED at 0.60 mm? | L1→L2 dielectric |
|---|---|---|---|
| **JLCPCB** | yes, as a thickness | **NO** | not published |
| **PCBWay** | yes, six published builds | yes | **0.0855 – 0.1375 mm**, set by inner-layer residual copper |
| Eurocircuits | no — defined-impedance pool is 1.00 and 1.55 mm only | — | — |

JLCPCB's own impedance stackup page and the thickness dropdown in its own
impedance calculator both list **0.8 / 1.0 / 1.2 / 1.6 / 2.0 mm and nothing
else** for four layers; every published 4-layer stackup they carry is
`JLC04161H-*`, i.e. 1.6 mm. They will *build* 0.60 mm four-layer — it is on the
capabilities page — they simply do not publish or control the stackup there.
<https://jlcpcb.com/impedance> · <https://cart.jlcpcb.com/client/template/placeOrder/impedanceCalculation.html>

PCBWay publishes the build sheet, and **the height is a function of the inner
layers' residual copper ratio**, not of the order:
<https://www.pcbway.com/multi-layer-laminated-structure.html>

| PCBWay build | inner residual | L1→L2 prepreg | pressed h | Dk |
|---|---|---|---|---|
| #35 | 70 % | 3313 RC58% | **0.0925 mm** | 4.45 |
| #36 | 50 % | 3313 RC58% | 0.0855 mm | 4.45 |
| #112 | 30 % | 2 × 1080 RC68% | 0.1375 mm | 4.21 |

### The number, computed two ways because one formula is not a measurement

| build | h | Dk | w for 50 Ω | **Z0 at the board's 0.127 mm** |
|---|---|---|---|---|
| #35 | 0.0925 | 4.45 | 0.1378 mm | **51.93 Ω** (Hammerstad–Jensen) · **50.26 Ω** (IPC-2141) |
| #36 | 0.0855 | 4.45 | 0.1254 mm | 49.70 Ω · 47.44 Ω |
| #112 | 0.1375 | 4.21 | 0.2299 mm | 65.37 Ω · 65.87 Ω |

Two independent closed forms, 1.7 Ω apart on the chosen build. The solver was
sanity-checked against a case with a published answer — bare 2-layer, h 1.5 mm,
εr 4.5 → 2.754 mm for 50 Ω, inside the textbook 2.7–2.9 mm band.

### The decision

1. **The RF trace stays at 0.127 mm.** It is the netclass width already, it is
   what the QFN-48's 0.40 mm pitch escape needs anyway, and on PCBWay build #35
   it is **51.9 Ω bare, about 49–50 Ω under solder mask** (green mask pulls
   1.5–2.5 Ω out of a line this thin). 50 Ω is REACHABLE on this stack; nothing
   has to be restacked and no process floor is crossed. JLCPCB's multilayer
   minimum is 0.09 / 0.09 mm and 0.127 mm is standard-price — the +20 % of
   order-value surcharge starts below 0.0889 mm (3.5 mil).
2. **A controlled-impedance order goes to PCBWay, build #35, named in writing.**
   Not JLCPCB, which cannot sell impedance control at this thickness at all.
3. **If the board is built at JLCPCB anyway, THE IMPEDANCE IS UNCONTROLLED and
   the number to hand the factory is a range, not a value: 47 – 66 Ω.** That is
   the spread of the same 0.127 mm trace across the three real builds above.

### What the uncontrolled case costs the match, measured rather than waved at

At the worst corner (65.4 Ω into a 50 Ω system) the reflection coefficient is
Γ = 0.133: **return loss 17.5 dB, 1.8 % of the power reflected, 0.077 dB of
mismatch loss.** That is small in amplitude and the pi network C20/L10/C21
exists precisely to absorb it. What it is NOT small in is PHASE: the guided
wavelength here is about 68 mm, so the ~8 mm feed run is 0.12 λ and rotates the
impedance it presents by roughly 85°. **A pi network tuned on one build lands
somewhere else on another.** So the real cost is not decibels, it is that the
match must be re-tuned per fabrication house, and the tuning cannot be
transferred.

Separately and independently of the stackup: JLCPCB's **track width tolerance
is ±20 %**, so a 0.127 mm line ships 0.102–0.152 mm, which on this stack is
**57.2 – 47.6 Ω, ±10 % on its own** — the same as the ±10 % impedance tolerance
a controlled-impedance order would have bought.

### Still open, and named

- **εr 4.45 is PCBWay's published figure for 3313 RC58% and NO TEST FREQUENCY
  IS STATED**, by either house. At 2.44 GHz the real value is lower than a
  1 MHz figure. JLCPCB's own two pages disagree with each other about the same
  prepregs (7628 as 4.4 on one page and 4.6 on another), which is a fair
  measure of how much these numbers are worth.
- The 51.9 Ω is a closed form of the ±10 % accuracy class, not a 2D field
  solve and not a TDR. **A number for a factory quote comes from the fab's own
  calculator against a named stackup.** This one is what to ask them to confirm.

## D22 — the passives stay 0201, and the reason is height, not money (lane B1, 2026-09-05)

Lane S1 measured that **zero of the 9,030 0201 parts in the LCSC catalogue is a
JLCPCB Basic part**, while 0402 has 51 and 0603 has 118. Every 0201 line
therefore carries the $3.07 per-order feeder fee, and this board carries **20 of
them = $61.40 per order** (`docs/SOURCING.md`). Moving the passives to 0402
would delete most of that.

**It cannot be done, and the reason is in `height_check()` on every build.**
Lane M's stack (`design.py`, D17) allows **0.400 mm** on the top face inside
Ø21.2 mm — the moving gap the piezo bender needs. An 0201 body is 0.33 mm and
fits with 0.07 mm to spare. **An 0402 body is 0.55 mm and misses by 0.15 mm.**
Twenty-two of the parts in question sit in exactly that circle. Converting them
to 0402 does not cost money, it costs the sounder: the bender's diaphragm
touches the tallest part and stops moving.

The four 0402s already on the board (C9–C12, the 10 µF bulk) are on the BOTTOM
face over the cell, where the allowance is 0.578 mm — they clear by 0.028 mm,
and they are also **the only JLCPCB Basic part on this board**.

**The fee is per ORDER, not per unit, and that is what settles the money half.**

| build quantity | $61.40 amortised |
|---|--:|
| 10 | $6.140 / unit |
| 100 | $0.614 / unit |
| 1,000 | $0.061 / unit |
| 10,000 | $0.006 / unit |

Against a $6.09/unit bill of materials at 1k, the feeder fee is **1.0 % at the
volume this product is for** and 100 % of the argument at ten. A partner factory
building thousands pays it once. So: **0201 stays**, the $61.40 is a
prototype-run cost recorded rather than absorbed, and anyone quoting a ten-piece
run should be told the per-unit figure doubles for that reason alone.


## D23 — halo is a family, and one member is a part-for-part replica (2026-09-05)

Leif, verbatim: *"so create many different versions including one which is a
perfect recreation."* Preceded by: *"first step is recreating it exactly."*

**Why this changes something real.** Until now halo was one board that had
diverged from the AirTag in seven places, each defensible in isolation, which
together made it a functional equivalent rather than a copy. Every divergence
was an assertion — "the piezo is good enough", "the flash is unnecessary" —
and an assertion is not a measurement. A replica turns each one into a
**measured difference**, because both boards can be built and compared.

**The family**, in `spec/variants.json`:

| variant | what it is for |
|---|---|
| **Replica** | part-for-part recreation of the AirTag internals; the reference every other variant is measured against |
| **Core** | the open product that ships — cheapest, embeddable, functionally equivalent |
| **Block** | the circuit as a castellated solder-down module for anyone's board |
| **Ranger** | Core plus the ultra-wideband transceiver, for the owner's own fleet |
| **Plus** | the ideas that get ahead of Apple rather than level with them |
| **Card** | wallet thickness — the form Apple does not make at all |

**What the Replica genuinely cannot have**, and no effort closes these: Apple's
**U1 is never sold to anyone**, so Precision Finding is out and the footprint
stays unpopulated; and appearing inside Apple's own Find My application needs a
per-unit token burned into flash on Apple's own production line under a
programme whose terms forbid publishing what you learn. Everything else in the
AirTag is catalogue silicon and can be bought.

**What the Replica must fix rather than copy.** Apple puts its SPI flash on a
regulated 1.8 V rail through a buck and a load switch. Our first board put the
same class of part straight on the 3.0 V cell, out of spec — the verification
lane caught it and the part was deleted. **The Replica restores the flash and
copies Apple's power path**, which is the correct recreation and also the
correct engineering. Where an Apple part is obsolete or unbuyable, the closest
functional substitute is used and **named as a substitution**, never passed off
as the original.

**The honest caution.** A replica is the reference, not automatically the
product. Some of Core's divergences will survive comparison — the deleted
amplifier looks likely, since the firmware measures 1.27 percent of the SoC's
own flash and a bare bender needs no amplifier at all. Others may not. The
point of building both is that the argument stops being about opinions.

## D24 — an NFC field can push current backwards into the cell (2026-09-05)

**Nordic's own product specification, §42.10, verbatim:**

> *"If the antenna is exposed to a strong NFC field, current may flow in the
> opposite direction on the supply due to parasitic diodes and ESD structures.
> If the battery used does not tolerate return current, a series diode must be
> placed between the battery and the device in order to protect the battery."*

**A CR2032 does not tolerate reverse current.** A phone held against the tag is
a strong field by design — it is the whole point of the NFC feature.

**Decision: carry a series Schottky or ideal-diode controller between the cell
and the device** until the nRF54L product specification is read and proves it
unnecessary. This is a bill-of-materials line and a forward drop the power
budget has not accounted for, on a cell whose end-of-life headroom the coin-cell
model already tracks to 68 mV of droop. An ideal-diode controller costs more
than a Schottky but drops millivolts rather than a few hundred, which matters
here. The board lane must price both against the measured discharge curve.

**Confidence.** The quotation is from the nRF52832 specification, which is the
part Apple used and the part the Replica copies. Whether the nRF54L repeats the
warning is **CANNOT DETERMINE** — Nordic's documentation site is gated and the
page could not be fetched. The underlying parasitic-diode behaviour is
silicon-level and shared, so the safe reading is to assume it applies.

## D25 — an NFC tap on a sleeping halo is a reset, not an interrupt (2026-09-05)

Same specification, §42.1, verbatim:

> *"In system OFF, the NFC Low Power Field Detect function can wake the system
> up **through a reset**… Note that as a consequence of reset, NFC is disabled,
> so the reset handler will have to activate NFC again and set it up properly."*

**This constrains the firmware, not just its implementation.** Everything a tap
must serve — the encrypted identifier, the battery byte, any pointer into a log
— has to be **re-derivable from non-volatile state inside the reset handler**,
and the whole boot path has to finish while the phone is still in the field. The
specification's ≤500 µs activation figure explicitly **excludes supply and
oscillator startup**, so the real budget is larger and unmeasured.

Consequence: the record format and the key schedule are constrained by a
hardware behaviour, and any concept that assumes a tap can interrupt a running
tag is wrong. Recorded now so it is not discovered during bring-up.

## D26 — the coil and the antenna can share the annulus (2026-09-05)

The question the whole layout rested on: can the NFC coil and the 2.4 GHz
antenna both live in the ~5 mm ring around a 20 mm cell, or must the cell move
off centre, the coil change layer, or the puck grow?

**They can share it.** Keep the Ø25.2 mm coil at a **0.30 mm gap** and shorten
the antenna's open-end tail by **1.5 mm**. Solved: **2.4321 GHz, in band**, with
the best buildable matching network at **−6.39 dB** against a −6 dB requirement.
The cell stays centred and the puck keeps its dimensions.

**The coupling, measured** (antenna's own mode, not the coil's):

| gap | antenna resonance | shift from no coil |
|---|---|---|
| no coil | 2.4346 GHz | — |
| 0.30 mm | 2.3278 GHz | −107 MHz |
| 0.55 mm | 2.3336 GHz | −101 MHz |
| 0.80 mm | 2.3534 GHz | −81 MHz |
| **coil under the antenna arm** | **1.7666 GHz** | **−668 MHz** |

**+51.3 MHz per mm of gap** over 0.30–0.80 mm. The last row is the one to
remember: the coil cannot go on any layer beneath the arm, and no tuning
recovers a 668 MHz shift.

**The real cost is headroom, not frequency.** The match goes from −7.79 dB to
−6.39 dB, clearing the requirement by **0.39 dB**. That is thin. Any later
change near the annulus — a ground pour, a via, a component moved — can spend
it, so the match must be re-measured after any such edit rather than assumed.

**Why the earlier alarm was wrong, and it is instructive.** The first reading
said the coil detuned the antenna to 2.208 GHz. It did not: **the coil was
welded to the antenna in nineteen places**, 1.39 mm² of shorting copper, because
nothing in the tool compared passive copper against anything. Cutting the
crossings gave 1.8131 GHz — also wrong, because that is the **coil's own
half-wave mode** at 82–126 Ω rather than the antenna's at 7–9 Ω. Read that way, a
0.5 mm change moved the "resonance" by −25.5, −28.0 and −3.3 percent, which is
not physics.

**Mode identity is now an assertion**, not an observation: a radiator's mode must
be an upward reactance zero **and** sit in a stated resistance band, and finding
none or two candidates is a **failure** rather than a nearest-match guess. It was
proved to fire both ways, and it immediately caught three more things — including
one geometry publishing a −34.46 dB "matched" figure with **no reactance zero
anywhere**, and a mutual-inductance tool printing **−2.70 × 10¹² nH**, a
divergent integral sitting beside its own claim of no singularity.

Checks in that app went from 91 to 115 across 16 groups, every one broken on
purpose and restored.

## D26a — correction: the 1.5 mm does not transfer, and the shipping board has the bad geometry

*Written 2026-09-05. Two corrections to D26, both found by lane B1, and the first
of them is my error.*

**1. I passed a number to the board lane that does not apply to the board.**
D26's "shorten the antenna's open-end tail by 1.5 mm" was solved on a **Ø30 mm,
1.00 mm-thick study puck** whose tail is 2.5 mm — so the change removed 60
percent of that tail and 4.7 percent of the conductor. **The shipping board's
tail is 1.4539 mm.** On it, 1.5 mm is **103 percent of the tail** and 6.1 percent
of the conductor: it deletes the tail outright and cuts 0.046 mm into the last
meander tooth. Different outline, different thickness, different effective
permittivity. The lane refused to apply it and recorded the reason rather than
cutting the copper, which was correct. **The direction may still be right; the
number does not transfer**, and I should have checked that before relaying it.

**2. The 668 MHz condition is present on the shipping board right now.**
D26 recorded that the coil must not sit under the antenna arm, because that costs
668 MHz and no tuning recovers it. Measured on the real copper, plan view, all
layers:

| net | clearance to the antenna arm |
|---|---|
| **NFC1** | **−0.1746 mm — the coil's copper OVERLAPS the arm** |
| **NFC2** | **+0.1473 mm — inside the 0.30 mm floor** |
| GND | +1.4928 mm |
| VDD | +10.3810 mm |

Identical before and after routing, so this is the **design**, not the router.
And it explains the 2.71 Ω radiation resistance that looked wrong on
`halo-rev-a-2g4`: a radiator welded over a large passive conductor shows exactly
that signature. The electromagnetic study did not see it because that case
carries an empty passive-copper list — **it solved the arm with no coil present
at all.**

**How it got through:** the board's `antenna-ground-clearance` keep-out forbids
pours and vias but **allows tracks**, because the antenna is itself a track
there. The coil walked through the hole that exemption left. It is now assertion
R9, graded in plan view because the coupling is vertical through 0.6 mm of
laminate rather than lateral.

**What follows:** the coil must move off the arm before the antenna result means
anything on this board, and the electromagnetic re-solve is owed with the real
passive copper present. Until then the antenna's numbers describe a board we are
not building.

## D27 — nine meander teeth, and the antenna model is missing more than the coil (2026-09-05)

**The coil is off the arm.** The overlap D26a recorded is closed, and the way it
closed is worth keeping because the obvious levers were all too small.

The coil is trapped between the cell can at R10.00 — copper over steel is a
shorted turn — and the arm's inner edge. At four meander teeth the arm needs
0.9379 mm of depth, which puts that edge at R10.6621 and leaves the coil
**0.6621 mm for the 0.782 mm it needs**. It had been taking the 0.4197 mm
difference by lying under the arm. Every other lever measured too small: moving
the arm outward buys 0.050 mm to the notch cap, narrowing it from 0.60 to
0.40 mm buys 0.100, thinning the coil trace to 0.127 buys 0.120. Only cutting
turns closes it, and that costs inductance the NFC tank cannot spare.

**The free variable nobody had swept was the tooth count** — free because the
bisection holds the conductor at exactly a quarter wavelength whatever the count:

| teeth | arm inner radius | gap to coil |
|---|---|---|
| 4 | 10.6621 | **−0.1197 — overlapping** |
| 6 | 10.9747 | +0.1929 |
| 8 | 11.1386 | +0.3567 |
| **9** | **11.1977** | **+0.4158 — shipped** |

**Nine, not eight.** Eight measured **0.3096 mm** on the real drawn copper, which
is 9.6 µm above the 0.30 mm floor — inside JLCPCB's own ±20 % track-width
tolerance, and therefore **not a margin at all**. Nine measures **0.3627 mm**.
Conductor drawn 24.49100 mm, error −0.00000.

A check on the tooth slot fraction caught a defect before it shipped: at nine
teeth with the old divisor, the two walls of one tooth would have fallen under
the 0.127 mm process minimum and **the element would have shorted to itself**.

**Stated honestly: this is not free RF.** A finer meander couples to itself more.
That cost is real and unmeasured, exactly as the four-tooth version's was.

**The keep-out now makes the geometry impossible rather than merely graded**, and
it needed no net exception — because the element is on F.Cu alone. On the inner
layers and the bottom it has no copper at all, so a keep-out there can forbid
everything without forbidding the antenna. And those three layers are precisely
where the 668 MHz comes from, since the coupling is vertical through 0.60 mm of
laminate.

**On its first run it found something else: the cell's negative contact land, on
the bottom layer directly under the arm.** That is where a CR2032's rim touches,
so it is mechanical and cannot move. It was excluded as a pad and recorded rather
than left permanently red — because a rule that is always red is a rule people
learn to skip, which is how the original blanket exemption survived.

**The consequence for the electromagnetic model is the real finding:** the
antenna case's empty passive-copper list is missing **at least two** large
grounded conductors within a millimetre of the radiator — the coil *and* the
battery contact. Any re-solve must carry both, or it will again describe a board
we are not building.

## D26b — the tail does not exist, and every antenna solve before 2026-09-05 12:xx is void

Two corrections, both from the antenna lane, and the second one voids results.

**1. "Shorten the tail by N mm" cannot be applied to this board for any N.**
D26a corrected my 1.5 mm figure as being 103 % of a 1.4539 mm tail. That tail
belonged to an arc-plus-fold geometry **that no longer exists**. The shipped
element bisects its tooth depth so the meander's whole path *is* the quarter
wave: conductor 24.49100 mm against a 24.49100 mm target, error −0.00000,
**tail 0.00000 mm**. Any future retune is expressed through
`ce-rf/tools/retune_for_board.py`, which reports the four numbers that can
actually be acted on — quarter-wave target, tooth depth, arm inner radius, and
the resulting coil gap — each absolute and as a fraction.

**2. `sim.min_cell_mm` was declared in 13 specifications and read by nothing.**
The model builder normalises a spec's simulation block into the dictionary the
runner reads, and that dictionary never carried the key. So the runner's
fallback default was used on **every run this project has ever made**. Each
affected run printed `mesh-line merge at 0.0833 mm` one line above its own
result, under a specification saying `0.15`, and nobody compared the two lines.

Measured on one spec with nothing else changed: cells **1,584,128 → 1,065,792**
(−33 %), smallest cell **0.08338 → 0.15000 mm**, timestep **1.859e-13 →
3.061e-13 s**, a 1.65× speed-up.

**Why "let it run longer" was never going to work.** The earlier runs did not
converge slowly — their residual energy **floored**. One sat at **−34.87 dB from
timestep 41,745 to 459,690, flat to 0.01 dB across 418,000 timesteps**, against a
−40 dB criterion. A previous fix raised the timestep cap and bought 418,000
timesteps of a horizontal line. Cells of 0.083 mm beside cells of 3.70 mm is the
working hypothesis, and it is exactly what this fix removes.

**Consequence: the numbers 2.3547 / 2.7016 / 2.4871 GHz and −1.513 dBi are
VOID** — solved on the wrong pours *and* the wrong mesh. Nothing from them
travels. This is recorded here because a void number that stays in a document
becomes a fact by repetition, which is how +0.521 dBi survived as long as it did.

**Also fixed while chasing it:** the copper pours sat 0.157 mm inside their own
keep-out. Re-measured independently from every filled-polygon vertex, the closest
plane fill to the coil is **+0.2996 mm** — confirming the board lane's figure
exactly — but the models had been built from 19.80 and 19.74 mm discs, leaving
the bottom pour **1.15 cells** from the coil. Both discs are now R9.74310.

The lane added a `mesh-plumbing` self-test group of five checks and watched four
of them go red on a deliberate break, one reading *"0 of 13 antenna specs
declaring min_cell_mm carry it into the model"* and naming the files. Checks in
that app go 115 → 120.

## D26c — the mesh hypothesis is REFUTED. halo has no antenna number, and this is the honest state

`halo-rev-a-2g4-meander9-passive` completed at 05:04:07Z on the corrected mesh,
the corrected pours and both passive conductors present. **It FAILED**, and the
failure is clean rather than ambiguous:

| assertion | result |
|---|---|
| `solver_converged` | **FAIL, 0.0** — it floored again |
| `f_series_res_GHz` | **FAIL, 2.0701 GHz** against a 2.400–2.4835 band |
| `mode_identified` | **FAIL, 0.0** — no candidate met both the reactance-zero and radiator-resistance tests |
| `s11_worst_in_ble` | **FAIL, −4.81 dB** against −6 |
| `gain_dBi` | **CANNOT DETERMINE** — no identified mode to report gain for |
| `radiation_efficiency_physical` | **CANNOT DETERMINE**, same reason |
| `eps_eff_implied` | PASS, 1.3148 |
| `passive_copper_declared` | **PASS, 1.0** — the assertion added after the retraction is doing its job |

**The mesh fix was the leading hypothesis and it is now refuted, not merely
unproven.** D26b established that `min_cell_mm` was declared in thirteen specs
and read by nothing, that fixing it cut the cell count by a third and lengthened
the timestep 1.65×, and that the earlier failures were a floor rather than slow
convergence. That was a real defect and fixing it was right. **It was not the
cause of the floor.** A refuted hypothesis is a stronger result than an open one
and is recorded as such.

**What halo has, stated plainly: no antenna number.** Not a bad one — none. The
figures that would matter, gain and efficiency, are CANNOT DETERMINE because
nothing identified a radiator mode to compute them for. Every earlier figure is
void (D26b). The +0.521 dBi that was reported to Leif is withdrawn (C-5).

**What is now suspected**, and it must be tested rather than assumed after two
wrong hypotheses in a row: the element may not be resonating in band **on this
board at all**. A series resonance at 2.0701 GHz with no identifiable radiator
mode is consistent with an element detuned by its surroundings rather than with
a solver artefact — and the surroundings changed twice, when the coil moved and
when the pours were cut back. The retune path exists
(`ce-rf/tools/retune_for_board.py`, reporting quarter-wave target, tooth depth,
arm inner radius and resulting coil gap, each absolute and as a fraction) and it
is the next thing to try. **It is a hypothesis, not a conclusion.**

## D26d — the control changes the reading: the surroundings pull 604 MHz, and the floor is common

`halo-rev-a-2g4-meander9-bare` — same board, same mesh, **no passive copper** —
completed. Read against case one, the two together say more than either alone:

| | with coil + contact | **bare** |
|---|---|---|
| series resonance | 2.0701 GHz | **2.6744 GHz** |
| mode identified | **no** | **yes** |
| worst in-band match | −4.81 dB FAIL | **−6.35 dB PASS** |
| solver converged | no, floored | no, floored at −35.34 dB |

**I was too quick when I said case two flooring eliminates the surroundings.**
That is true only of the *floor*. It is emphatically false of the *tuning*: the
coil and the battery contact pull the resonance **604 MHz downward** and destroy
mode identity altogether. On the bare board a clean radiator mode exists and
matches at −6.35 dB. Add the real surroundings and there is no identifiable mode
at all. The surroundings are doing something large; they are simply not what
makes the solver floor.

**Two separate problems, now separated.** The floor is common to both cases, so
it belongs to something shared — the port, the feed, or the board model — and
neither the mesh (D26b, refuted) nor the passive copper (this case) explains it.
The detuning belongs to the surroundings and is a genuine RF result.

**And it gives the first actionable retune direction this project has had.** The
target is 2.44 GHz. The real board, with its real surroundings, sits at
**2.0701 GHz** — about **18 % low**, so the element must get **shorter**, not
longer. Bare it sits at 2.6744 GHz, above the band, which is consistent: the
surroundings load it heavily downward and the element was drawn for a lighter
load than it actually has. `ce-rf/tools/retune_for_board.py` converts that into
the four numbers that can be acted on, each absolute and as a fraction.

**A defect found in the log while reading this.** `solver.log` carries
`[sim] convergence: OK -- openEMS ran to its energy end-criteria with a complete
excitation` on one line, and on the next openEMS's own
`Warning: Max. number of timesteps was reached before the end-criteria of -40dB
was reached...`. The wrapper's summary asserts the opposite of the solver it
wraps. The `solver_converged` assertion correctly reads 0.0 and the case FAILS,
so nothing was published wrongly — but a log line that contradicts the tool
beneath it is the eighth direction in `docs/TOOLS-THAT-LIE.md` and it should be
made to read from the same source the assertion does.

## D26e — three hypotheses eliminated by measurement; what is left is common to all three

The batch is complete and all three cases ran to the 460,000-timestep cap:

| case | element | passive copper | outcome |
|---|---|---|---|
| one | nine teeth | coil + battery contact | floored |
| two | nine teeth | **none** | floored |
| three | **four teeth** | none | floored |

Cases two and three differ in trace length by **0.0078 mm**, which makes the
meander comparison a clean single variable.

**Eliminated, each by measurement rather than by argument:**

1. **The mesh** — refuted in D26c. Fixing `min_cell_mm` was a real defect fixed,
   and it changed nothing about the floor.
2. **The passive copper** — the coil and the battery contact. Case two floors on
   a bare board. (They do pull the resonance 604 MHz and destroy mode identity,
   per D26d — a large effect, but not this one.)
3. **The meander density** — case three floors with four teeth as readily as
   nine.

**What remains is whatever all three share:** the port, the feed, the board
model, or the solver setup. That is a real narrowing, and three branches closed
is worth more than one left open.

**The sharpest observation, and it is not mine.** All three reach the cap, and
the residual *floors flat* — one held −34.87 dB to within a hundredth of a
decibel across 418,000 timesteps. **A flat residual means the cap is not what is
binding.** The run would floor at any cap, so raising it again is the one thing
guaranteed not to help. Something stops the energy falling, and it is present
even on a bare board with a four-tooth element.

**Next hypothesis, labelled as one after three wrong in a row.** The air-box
padding is **30.591067 mm** in every case, which is almost exactly a quarter
wavelength at 2.45 GHz (30.6 mm). A quarter wave is a common minimum for
absorbing boundaries and a marginal one. Energy reflecting off an imperfect
boundary and re-circulating is a textbook cause of a residual that stops falling
at a fixed level. **The test is cheap and it is a single variable:** raise the
padding — half a wavelength, then one — and see whether the floor moves. If it
falls, the boundary was the cause. If it does not, the boundary is eliminated too
and the search moves to the port and feed. Either way a branch closes.

This is a hypothesis, not a finding. It is recorded here so that if it is wrong
it is wrong on the record, like the three above it.

## D26f — the boundary WAS the cause. Half a wavelength converges in 8 415 timesteps where a quarter floored for 460 000

*Lane T3, 2026-09-05. Three hypotheses were refuted here in a row. This is the
fourth, and it is the first one that held.*

**The test, one variable.** `halo-rev-a-2g4-meander4-bare` — the cheapest
floored geometry, bare, four teeth, already characterised — re-solved at three
air-box paddings with nothing else changed. `ce-rf/tools/emit_pad_study.py`
derives all three specs from the parent by deep copy, prints the leaf-key diff
and **exits 1 if anything outside an allow-list moved**; 27 leaf keys differ
and every one is the padding, the far-field switch, the asserts or their prose.

| pad | cells | timesteps | wall | residual | `solver_converged` |
|---|---|---|---|---|---|
| **0.250 λ** (30.591067 mm) | 1 071 648 | **460 000, capped** | 1783.9 s | 2.3600e-18, **floored** | **0.0 FAIL** |
| **0.500 λ** (61.182134 mm) | 2 000 000 | **8 415** | **143.8 s** | 6.4000e-19 | **1.0 PASS** |
| **1.000 λ** (122.364269 mm) | 4 451 698 | 8 600 | 336.2 s | 1.0200e-18 | **1.0 PASS** |

`solver_converged = 1.0` has not happened once in this family before.

**Two confounds, each closed by a number rather than an argument.**

- **The Courant timestep never moved.** Smallest cell 0.15000 mm in all three,
  set by the forced uniform mesh, so 460 000 timesteps is the *same physical
  duration* in every row. The larger boxes did not win by running longer.
- **The control reproduced the published run exactly.** All three study runs
  set `sim.farfield = false` and the published run did not, so a
  quarter-wavelength control was run to pay for that. It came back at
  **2.3600e-18 against the published 2.3600e-18 — 0.00 % apart** — and with
  identical `f_res` 4.27 GHz, `f_series_res` 2.4873 GHz, `s11_min` −1.5698 dB,
  `eps_eff` 0.9103, `R_at_series_res` 2.4661 Ω. Not close: the same numbers.
  The NF2FF box is a recorder and is now measured to be one.

**The larger box is CHEAPER, not dearer** — 12.4× less wall clock at 1.87× the
cells, because a run that converges stops. That is why the fix has no cost to
weigh.

**Half a wavelength is enough; a full one buys nothing.** `f_series_res` goes
2.4873 → 2.4877 → 2.4896 GHz — 2.3 MHz, 0.09 %, across the whole sweep — and
`R_at_series_res` goes 2.4661 → 2.7191 → 2.6748 Ω, where **the quarter wave is
the outlier and the two larger boxes agree to 1.6 %**. That is convergence in
the parameter, reached by 0.5 λ. A full wave costs 2.2× the cells and needs 2 %
*more* timesteps because the domain is bigger.

**The fix is in the core.** `cerf.fdtd.build_model`'s default padding is
`C0/f0/2` as of `a3d78d2b`; the model carries `airbox_pad_source`, and the
runner logs the padding **with its provenance** and warns below 0.499 λ naming
this measurement. Provenance is in the log because `min_cell_mm` hid behind
thirteen specs for months while the log printed a value and not where it came
from (D26b).

### What this means for everything already on disk

**Every antenna run in `ce-rf/out/` was solved against a boundary now measured
to be too close.** 20 of the 22 built models sit at exactly 0.250 λ. That
includes the three cases that are this project's actual question — the
nine-tooth element with the coil and the battery contact, its bare control, and
the four-tooth element — and `validation-staircase-straight`, which floors at
2.27e-17, the worst residual in the repo. **They are re-solvable, and faster
than they were.** Until they are, halo still has no antenna number (D26c
stands), and the 2.0701 GHz / 2.6744 GHz detuning result of D26d is a
resonance-frequency reading whose boundary error is now bounded at 0.09 % by
this study but which was still taken on the wrong boundary.

### It reconciles the 18-of-18 split rather than contradicting it

While the runs were in flight, `ce-rf/tools/floor_table.py` was written to read
the energy trace of every case on disk, and found a perfect split: **6 runs hit
the timestep cap and none of them has a short to the ground pour; 12 reached
the criterion and 10 of them do** — the two exceptions being the only cases
with no coplanar pour beside an isolated arm (a free-space dipole, and the
openEMS tutorial patch whose ground is on the opposite face). That looked like
a feed defect. It is the same boundary seen from the other side: a quarter-wave
MUR sets a reflection floor, a well-radiating shorted IFA decays *below* that
floor before it matters and converges anyway, and a coplanar monopole
presenting **2.47 Ω** at resonance never gets there. Two observations, one
cause.

### What was wrong with the prediction, and it is worth saying

The instruction that launched this test predicted the boundary would be
*eliminated*, on the reasoning that a quarter wave is a common minimum and that
20 of 22 models used it on both sides of the split. That reasoning was sound and
the conclusion was wrong, which is the whole reason the test was run instead of
argued. `ce-rf/tools/pad_study_verdict.py` had its criterion committed to disk
while the control was 36 % of the way through, before any result existed — and
that rule then had to be **amended**, because it assumed all three runs would
floor and never enumerated the outcome that happened. A converged run has no
floor. The amendment is stated as an amendment, above the original text, and
neither the flatness window nor the movement factor was loosened.

### Still open, and not this

`mode_identified` is 0.0 in all three rows. The element presents **2.72 Ω** at
its series resonance, below the 3–30 Ω radiator band the spec states in
advance. That is a design question about a monopole in a 2.6 mm annulus, not a
solver one, and it is the next thing this element has to answer.

## D26g — the absorbing boundary WAS the cause. Confirmed, and it makes solves 12× cheaper

The fourth hypothesis is the one that was right. One variable, the air-box
padding, on the bare four-tooth element:

| padding | timesteps | wall time | converged |
|---|---|---|---|
| **0.250 λ** (30.591 mm) — every run this project ever made | **460,000, capped** | 1783.9 s | **NO — floored** |
| **0.500 λ** (61.182 mm) | **8,415** | **143.8 s** | **YES** |
| 1.000 λ (122.364 mm) | 8,600 | 336.2 s | YES |

`solver_converged = 1.0` had **never once happened** in this family. And the
larger box is **12.4× cheaper in wall time at 1.87× the cells**, because a run
that converges stops.

**Two confounds closed with numbers rather than argument.** The smallest cell is
0.15000 mm in all three rows, so the timestep never moved and 460,000 timesteps
is the same physical duration in every case. And the quarter-wave control
reproduced the published run to **0.00 %** — 2.3600e-18 against 2.3600e-18, with
identical resonance, match, permittivity and resistance.

**Half a wavelength is enough.** Series resonance moves 2.4873 → 2.4877 →
2.4896 GHz across the three, a spread of 2.3 MHz or 0.09 %. The core default is
now a half wavelength, warned below 0.499 λ.

**Consequence: every result in `ce-rf/out/` was solved at a quarter wave.** All
of them are re-solvable, and faster than before.

**A caution that changes how these are read.** openEMS normalises its decibel
figures to the largest energy it happened to *sample*, on a wall-clock cadence —
so two identical runs printed −36.04 and −35.01 dB for residuals 0.4 % apart.
**How busy the machine was sets what a run has to reach.** The −40 dB criterion
inherits this. Tools now compare on energy rather than on decibels.

## D26h — the antenna question is now a DESIGN question, not a solver one

With the solver fixed, the remaining failure is ours. `mode_identified` reads
0.0 in every row because **the element presents 2.72 Ω** against a 3–30 Ω
radiator band that was stated in advance rather than fitted afterwards.

That is a design problem: a monopole in a **2.6 mm annulus** is too small a
radiator to present a usable resistance. It is not a meshing artefact, not the
boundary, not the passive copper and not the meander density — all four of those
are now closed.

**halo still has no antenna number**, and D26c stands until the three halo cases
are re-solved at half a wavelength, which is now minutes each rather than half an
hour. But the question has changed from *why will this not solve* to *is this
element viable in the space available*, and that is answerable by design work
rather than by more simulation.

**A bonus finding at zero solver cost.** Splitting all 18 existing runs on one
column: **6 hit the cap and none has a short to the ground pour; 12 converged and
10 do.** That looked like the feed. It is the same boundary seen from the other
side — a quarter-wave boundary sets a reflection floor, a well-radiating shorted
inverted-F decays below it and converges anyway, and a 2.47 Ω coplanar monopole
never gets there.

## D26i — halo has an antenna number at last, and it does NOT beat Apple's −3.2 dBi

D26c is closed. The three halo cases were re-solved at the new default
`airbox_pad_mm = C0/f0/2`, and **every one of them converged — none ever had.**
Run log: `ce-rf/out/_t3c/README.md`.

| case | 0.250 λ (void) | **0.500 λ** | wall |
|---|---|---|---|
| `validation-staircase-straight` | 398 970 CAP | **5 547** | 667.3 → **31 s** |
| `halo-rev-a-2g4-meander4-bare` | 459 459 CAP | **8 613** | 1786.6 → **121 s** |
| `halo-rev-a-2g4-meander9-bare` | 459 800 CAP | **8 500** | 1694.2 → **111 s** |
| `halo-rev-a-2g4-meander9-passive` | 459 100 CAP | **47 400** | 2012.9 → **381 s** |

**THE ANSWER**, `halo-rev-a-2g4-meander9-passive` — the shipping element with
the NFC winding and BT1's negative contact land as passive copper — at
`sim.farfield_f_GHz` 2.4418 GHz:

| radiation efficiency | total efficiency | directivity | **gain** | realized gain |
|---|---|---|---|---|
| 26.16 % | 12.75 % | 2.433 dBi | **−3.391 dBi** | −6.512 dBi |

**Apple's filed maximum gain is −3.2 dBi. halo measures −3.391 dBi. It is
0.19 dB short and it does not beat it.** `gain_dBi` is the comparable figure
because Apple's is a matched number; realized gain, which is what a radio sees
with no matching network, is −6.512 dBi, and the best BUILDABLE network cerf
can fit only reaches −4.954 dB worst-in-band against the spec's −6 dB assert.

**The "+0.521 dBi against Apple's −3.2 dBi" recorded elsewhere in this project
is a different antenna on a different board** — `halo-round-rim-ifa`, a rim IFA
on the Ø30 × 1.0 mm study puck. It never was rev A's number.

**Why halo is short, in one number: the element resonates at 2.0669 GHz**,
16 % below the BLE band, so 2.44 GHz is off-resonance and every figure above
is a measurement of an antenna used in the wrong place. Its bare control
resonates at **2.6763 GHz**, 7.8 % above. **The NFC winding pulls the element
down by 22.8 % and neither end lands in 2.400–2.4835 GHz.** A retune through
`ce-rf/tools/retune_for_board.py` is the difference between −3.391 dBi and
whatever this element can actually do.

**`mode_identified` is 0.0 on the shipping element for a different reason than
D26h recorded, and D26h's 2.72 Ω was the wrong geometry.**

| case | zeros | R at each | `mode_identified` |
|---|---|---|---|
| `meander4-bare` (not what ships) | 1 | 2.697 Ω | 0.0 — none in the 3–30 Ω band |
| `meander9-bare` | 1 | **3.300 Ω** | **1.0** |
| `meander9-passive` (ships) | 3 | 4.09 / 7.19 / 12.87 Ω | 0.0 — **all three qualify** |

The shipping element's failure is **ambiguity, not absence**: three things in
the model look like radiators and the spec cannot say which is the antenna.
That is a spec fix (narrow `mode_select.within_GHz`), not a design fix.

**And the fix generalises off this board, where it moved the ANSWER and not
just the convergence.** `validation-staircase-straight`, a 12 mm strip monopole
in vacuum at 6 GHz on a different mesh, converged 21.5× faster — and its
`f_series_res` moved 3.7476 → **4.6875 GHz (+25.1 %)**, its R 30.567 → **52.863 Ω
(+72.9 %)**. On halo the same change moved things 0.09 %, which is what made
the old results look merely unconverged. **Every quarter-wave result in
`ce-rf/out/` is void as an ANSWER, not only as a convergence record.**

## D26j — how much room the radiator needs, measured: 3.29 Ω → 9.71 Ω, and 10 Ω is still out of reach

D26h said the element "is too small a radiator to present a usable resistance"
in the annulus it has. That is a claim about ROOM, so it predicts a direction.
Five solves, ONE variable — the ground pour radius, top and bottom together —
with the decision rule (`MOVE_FACTOR` 2.0, `FLAT_RATIO` 1.30, `CONTROL_TOL`
25 %, targets 3.00 and 10.00 Ω) committed in
`ce-rf/tools/room_study_verdict.py` **before any of the five started**.

| pour R | gap to element | `f_series_res` | **R at it** | `mode_identified` |
|---|---|---|---|---|
| **9.74310 as built** | 1.44891 mm | 2.6761 GHz | **3.2911 Ω** | 1.0 |
| 8.50000 | 2.69201 mm | 2.7844 GHz | **5.4601 Ω** | 1.0 |
| 7.00000 | 4.19201 mm | 2.8459 GHz | **7.3218 Ω** | 1.0 |
| 5.50000 | 5.69201 mm | 2.9227 GHz | **8.6861 Ω** | 1.0 |
| 4.00000 | 7.19201 mm | 3.0570 GHz | **9.7058 Ω** | 1.0 |

**VERDICT: D26h SURVIVES.** Monotone rising, **2.949×** the control at the
largest gap. The resistance IS set by the space around this element.

**The control reproduces the published parent to −0.27 %** (3.2911 against
3.3000 Ω), which is what pays for the study: all five move the ground feed tab
to y = 0.00 so it cannot detach from a shrunken pour, and the control shows
that change costs a quarter of one percent.

**What it buys, what it costs, where it runs out — the decision, with numbers
on both sides:**

- **3.00 Ω, the radiator band's floor, is ALREADY MET as built** on the
  nine-tooth element. D26h's 2.72 Ω belongs to the four-tooth geometry that no
  longer ships.
- **Pour R8.50 doubles it to 5.46 Ω; pour R7.00 reaches 7.32 Ω.**
- **The cost is the copper under the battery.** A CR2032 is Ø20.00, so its
  footprint reaches R10.0 and the as-built R9.74310 is *already* inside it.
  R8.50 leaves the cell overhanging ground by 1.50 mm, R7.00 by 3.00 mm.
- **10.00 Ω — `mode_select.near_R_ohm`, stated in advance in all three specs —
  is NOT REACHED WITHIN THE SWEEP.** The largest measured resistance is
  9.7058 Ω at a pour of R4.00, an island smaller than the battery and not a
  buildable board. The tool interpolates between measured points and
  **refuses to extrapolate**, because an extrapolated "how much room would it
  need" becomes a design decision three documents later.
- **A second cost pointing the same way as everything else here: the
  resonance RISES with room**, 2.6761 → 3.0570 GHz, **14.2 %** across the
  sweep. The element already resonates high; room makes it worse, and any
  bought has to be paid back in conductor length.

**So: room is a real lever and it is not a sufficient one.** Getting this
element to the 10 Ω the specs expect is out of reach of the pour on a 26 mm
disc, which is the measured form of what Apple did differently — they did not
etch the antenna in board copper at all.

## D21a — correction: "50 Ω is not manufacturable on this stack" is conditional, and the condition decides it

D21 recorded that 50 Ω is reachable at 0.127 mm and the stackup document
concluded that a 50 Ω microstrip referenced to the inner ground **"is not
manufacturable on a 0.60 mm four-layer stack — that is a property of the
stack"**. That conclusion is computed at an outer dielectric of **0.0685 mm**,
which §1 of the same document correctly marks **CANNOT DETERMINE** and describes
as *"arithmetic, not a quote"*. The document was honest about its input and then
reasoned from it as though it were settled.

**The assumed set sums to 0.60 mm but is not made of stocked materials.**
Enumerating four-layer stackups from sourced prepregs and cores that reach
0.600 mm within 30 µm gives **19 combinations**, across which the outer
dielectric ranges **0.050 to 0.200 mm**. The board thickness does not determine
it. And the conclusion **reverses** inside that range: at h = 0.100 mm the 50 Ω
width is 0.1456 mm, comfortably above the 0.127 mm minimum, and one 2116 prepreg
on a 0.300 mm core lands at 0.6050 mm among the closest fits.

**Revision A's choice stands** — a short run absorbed in the pi network is
defensible at about 0.1 λ whatever the dielectric turns out to be. What changes
is the **recorded reason**, which is what a revision B decision would be built
on. And it sharpens the standing instruction to ask the factory for its stackup:
that answer does not feed the impedance question, **it decides it.**

**Two things closed alongside it so nobody re-attempts them.** High-density
interconnect does **not** rescue a six-layer AirTag board: published minimum
laser-blind core is 0.1 mm and minimum prepreg 0.06 mm — the same core as stocked
FR-4 and a *thicker* prepreg than the thinnest standard type — so six layers come
to 0.464 mm against thin FR-4's 0.448 mm, and neither fits 0.30 mm.

And the through-versus-blind via question was **abandoned for the best reason
recorded today**: the test is a claim about an **absence** — a land with no
counterpart on the opposite face — and on that layer the copper is sparse, so a
land the detector *missed* and a land that is genuinely *absent* produce
identical output. A test whose negative result is indistinguishable from a broken
instrument is not a test, and this one would have failed toward the more
interesting answer. It needs a cross-section or a resolving X-ray. The tool is
committed with its residual check going red rather than deleted.

## D26k — rt2 is the best antenna result yet, and it was killed before writing a verdict

The second retune, `halo-rev-a-2g4-rt2-passive`, is the closest any case has come
and it did not survive to record itself.

| | the three cases that refuted three hypotheses | **rt2** |
|---|---|---|
| best residual | −34.87 dB, floored | **−39.13 dB** |
| timesteps | 460,000, capped | **37,224** |
| scratch written | ~9 GB each | ~1 GB |

Criterion is −40 dB, so it fell **0.87 dB short** — but it got 4.3 dB deeper than
the floor that eliminated the mesh, the passive copper and the meander density,
and it did so in **8 % of the timesteps**. The energy decayed monotonically over
the run: −12.07, −23.05, −30.43, −34.52, −35.02, reaching −39.13.

**No `verdict.json` was written and the log ends mid-run rather than at a
completion line.** It was killed, not finished. Relaunched detached so it
survives a turn boundary — which is the failure that took it.

**Two reading errors worth recording, one mine and one caught before it
travelled.** The supervisor's monitor fired "scratch plateau — stopped short",
which reads as converged early; it did not relay that, because rt1 plateaued the
same way and FAILED, so a low plateau is ambiguous in this family between
converging and aborting. And it first read the energy as *rising* from the last
three log lines — three consecutive samples near a floor oscillate, and over the
whole run it decays.

**Mine: I read two peer Claude sessions as running solvers, twice, from
`ps | grep openEMS`.** Every session's command line here contains its entire
brief, so a brief that mentions openEMS matches. This is the same trap already
written into `TOOLS-THAT-LIE.md` for `pgrep -f freerouting`, and I walked into it
anyway — while relaunching a solve, which is exactly when believing a phantom
process would have made me *not* relaunch. The correct check is
`ps -axo comm=` and matching the **executable name**, which returned nothing.

## D28 · The antenna mode has never been identified on the real board

**2026-09-05, from six converged solves.** All three retune generations have now
finished honestly at the 0.5λ boundary, bare and passive. One row separates them
completely:

| case | f_series (GHz) | gain (dBi) | **mode_identified** |
|---|---|---|---|
| meander9-bare | 2.6763 | — | **1** |
| meander9-passive | 2.0669 | −3.39 | **0** |
| rt1-bare | 2.7058 | −1.46 | **1** |
| rt1-passive | 2.3730 | −11.81 | **0** |
| rt2-bare | 2.6630 | −1.52 | **1** |
| rt2-passive | 1.3532 | −9.18 | **0** |

**Every bare case identifies its mode; no passive case ever has.** The passive
case is the board that gets fabricated — it is the one carrying the NFC coil and
the land. So **no frequency this project has quoted from a passive case is a
confirmed antenna mode**, and that includes rows in the convergence table.

**The coupling is not the constant D26 recorded it as:**

| | bare | passive | shift |
|---|---|---|---|
| meander9 | 2.6763 | 2.0669 | −609 MHz |
| rt1 | 2.7058 | 2.3730 | −333 MHz |
| rt2 | 2.6630 | 1.3532 | **−1310 MHz** |

The bare resonances sit within **43 MHz** of one another across a −15% / +5%
conductor range. The passive ones wander over **1310 MHz** on the same geometry
changes. A fixed parasitic load cannot produce that. Two coupled resonators can,
and the split's dependence on their frequency separation has exactly this shape.
It also explains the extractor's behaviour: with two zeros present it reports
whichever lands lowest, and which one that is changes with length — so the
passive "series resonance" is not tracking one physical thing at all.

**D26 is superseded on this point.** It recorded the coil as costing a fixed
668 MHz. It does not; the cost ranges 333–1310 MHz and depends on the element.
The coil and the element are one coupled system, not an antenna with a
correction term.

**The decision.** Stop retuning the element. Six solves have demonstrated that
moving one resonator of a coupled pair moves both zeros unpredictably — that is
the table above, not a calibration error. The order is now:

1. **Solve the NFC coil alone** and find its self-resonance. If it is near
   2.44 GHz that is the entire problem, and it is a coil-geometry fix.
2. **Decouple or detune** — move the coil's self-resonance out of band, or cut
   the coupling (spacing, orientation, a ground fence).
3. **Only then** tune the element, on passive geometry, and require
   `mode_identified` = 1 before quoting any frequency.

**And the standing rule that comes out of it:** never quote `f_series_res_GHz`
from a case whose `mode_identified` is 0. That is a number the extractor
produced, not a mode anyone confirmed. When mode identification fails the
frequency row is **CANNOT DETERMINE**, not a value. See `CONCERNS.md` C-7 and
`docs/TOOLS-THAT-LIE.md` §10 for the related defect — a retune premise that was
a prediction wearing the word *measured*.
