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
| **haytag-core** | BLE only (nRF52-class, pre-certified module) | the open product anyone can build, sell or embed | modular approval, self-declared RED; the shipping default |
| **haytag-uwb** | BLE + a sourceable UWB transceiver | Leif's own sensor fleet doing peer-to-peer ranging in his digital twin, and anyone doing the same on their own premises | not a sold consumer product; ranging is haytag-to-haytag, so no Apple handshake and no MFi is involved |

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
an nRF54L-class part reaches useful accuracy — in which case haytag-uwb may not
need a second radio at all. That is a matter of fact and will be measured.

## D2 — the Bluetooth word mark (2026-09-03)

Lane F: Bluetooth SIG product qualification is **$12,000** under the schedule
effective 1 March 2026. **Decision: do not use the Bluetooth word mark or logo
anywhere in the product, packaging or documentation.** The radio is described
functionally ("2.4 GHz, compatible with Apple's Find My network"). Anyone
selling haytag commercially at volume can qualify on their own account.
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
