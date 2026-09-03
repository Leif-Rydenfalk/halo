# SPEC — what haytag must be

*The specification the design is judged against. Every row is either SETTLED
(with its source) or PENDING with the lane that will settle it. Nothing here is
an assumption: a PENDING row is a work item, never a guess left to harden into
a fact. Companion documents: GOAL.md (why), MISSION.md (definition of done),
DECISIONS.md (how each question was resolved), docs/ANTI-STALKING.md (the
safety behaviour, non-optional).*

Started 2026-09-03. Revision: draft 0.

## 1. Product definition

haytag is a coin-cell Bluetooth tracker that reproduces the Apple AirTag
function for function from public information only, published openly, and
manufacturable cheaply. It ships in two variants (DECISIONS.md D1):

| | haytag-core | haytag-uwb |
|---|---|---|
| radios | 2.4 GHz BLE | 2.4 GHz BLE + UWB |
| purpose | the open product: find your things through Apple's Find My network | peer-to-peer ranging between the owner's own devices, for a digital twin |
| certification | pre-certified module, modular approval, RED self-declaration | owner-operated, not a sold consumer product |
| status | the shipping default | second board revision |

The circuit is published three ways so it can be embedded in any host board in
any outline (GOAL.md deliverable 2): a KiCad hierarchical design block, a
castellated solder-down module, and the Ø 32 mm puck as the first host.

## 2. Functional requirements, against the real AirTag

Each row: what the AirTag does, what haytag must do, and where the number comes
from. The part that implements each is section 3.

| # | function | requirement | state |
|---|---|---|---|
| F1a | Google Find Hub advertising | advertise concurrently on Google's network: service `0xFEAA`, frame `0x40/0x41`, ~1024 s ephemeral-ID rotation | SETTLED lane B (public spec); DECISIONS.md D7 |
| F1 | Find My advertising | non-connectable advertisement, 37 bytes on air: address = `p[0]\|0b11000000 ‖ p[1..5]`, then `1E FF 4C 00 12 19 <status> p[6..27] p[0]>>6 <hint>`, where p is the X coordinate of the rolling NIST P-224 public key | SETTLED lane B (PETS 2021 Table 2, cross-checked against OpenHaystack source) |
| F2 | key rotation | rotate the advertised key on the DULT schedule; MAC address rotation likewise | SETTLED lane F: 15 min key, 24 h MAC |
| F3 | sound maker | audible alert, **≥60 Phon at 25 cm (ISO 532-1:2017)**, mandatory, four non-owner sound opcodes | requirement SETTLED lane F; mechanism OPEN, see DECISIONS.md D11 |
| F4 | separated-state behaviour | near-owner → separated after >30 min; random 8–24 h alert timeout with 6 h back-off | SETTLED lane F |
| F5 | identifier retrieval | serial readable over NFC or BLE, behind a physical button, 5-minute window; printed unique serial on the housing | SETTLED lane F |
| F6 | owner information page | obfuscated owner-info page, ≥25-day retention | SETTLED lane F |
| F7 | motion detection | wake and change advertising behaviour on movement | PENDING lane A (which accelerometer, what thresholds) |
| F8 | NFC tap | phone tap reads the tag and opens the owner page | PENDING lane A / E (which NFC IC, coil geometry) |
| F9 | precision finding | AirTag does this with Apple's U1 | **known gap** — not reproducible without MFi (DECISIONS.md D1, D5) |
| F10 | peer ranging | haytag-uwb ranges to other haytags for local relative position | PENDING lane H (technology, accuracy, battery) |
| F11 | battery life | AirTag claims about a year on a CR2032 | PENDING lane A (Apple's claim) + ce-spice model |
| F12 | battery replacement | user-replaceable CR2032 behind a compliant door | SETTLED lane F: tool or two independent simultaneous movements (16 CFR 1263) |

## 2a. Budget floors (from lane B)

A Find My stack alone measures **116.7 KB flash / 21.5 KB RAM** (Goodix FMNA
figures, lane D). DULT adds a connectable advertisement set and a GATT service;
Google Find Hub adds a second beacon. The SoC is chosen with headroom over
those three together, not over the first (DECISIONS.md D8).

## 3. Component map — one row per function

PENDING lanes A and E. Structure fixed now so the dossiers drop straight in:
`function | AirTag part (as identified, with who identified it) | haytag part
| package | LCSC id | price at 1/100/1k/10k | datasheet | alternate | why`.

## 4. Physical envelope

PENDING lane G. Lane C's warning is already binding: on a 30 mm round board a
20 mm cell leaves only about a 5 mm annulus for the antenna keep-out and the
NFC coil together, which is why Apple moved to a laser-direct-structured
three-antenna frame. Either the puck grows, or the antenna and coil share the
annulus by design, or the cell moves off-centre. The ce-rf solver decides.

Target from the public product: Ø ≈ 31.9 mm, 8.0 mm thick,
11 g; the PCB diameter, stack budget and coil placement come from the teardown
measurements lane G is collecting. The embedded block variant is not bound by
this envelope; only the puck is.

## 5. Electrical requirements

| # | requirement | source |
|---|---|---|
| E1 | operate from a CR2032 across its full discharge curve, including the rising internal resistance at end of life | ce-spice model, lane T2 |
| E2 | survive the radio transmit current pulse without the rail dropping below the SoC minimum at end of life | ce-spice, asserted |
| E3 | sounder drive that reaches F3's loudness inside an 8 mm puck | lane G (mechanism) + ce-spice (drive current) |
| E4 | 2.4 GHz antenna matched on the real board outline, with the battery's copper in place | ce-rf, lane T3 |
| E5 | NFC coil tuned to 13.56 MHz for the chosen tag IC's input capacitance | ce-rf |
| E6 | per-layer current and voltage drop within IPC-2221B limits | ce-board-sim |

## 6. Manufacturing requirements

| # | requirement | source |
|---|---|---|
| M1 | 4-layer board, DRC-clean against JLCPCB's published capabilities | ce-fab dfm, lane T6 |
| M2 | every part in stock at LCSC with a named alternate | ce-fab bom, lane T6 |
| M3 | assembly files (BOM + pick-and-place) accepted by JLCPCB without manual correction | ce-fab jlc |
| M4 | panelized for volume | ce-fab panel |
| M5 | cost per unit at 10 / 100 / 1 000 / 10 000, compared to Apple's $29 retail | lane E |

## 7. Compliance requirements

The 30-item constraint checklist in research/06-legal-ip-certification-safety.md
is normative. The headline constraints: pre-certified radio module for modular
approval; no Bluetooth word mark (DECISIONS.md D2); Reese's Law battery door
(D3); DULT behaviour non-optional (docs/ANTI-STALKING.md); clean-room only,
no MFi (D5); licence split (D4).

## 8. Out of scope

Apple Precision Finding (F9), the "Works with Apple Find My" badge, and any
stealth or silent build target. The last is refused on principle, not omitted.
