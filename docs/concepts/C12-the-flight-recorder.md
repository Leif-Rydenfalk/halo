# C12 — The flight recorder — an on-tag event log, read at an NFC tap

*An AirTag remembers nothing. A halo has 1 MB of NVM and uses 13 kB of it, so it can keep the last several thousand motion and ranging events and hand them over when somebody taps it.*

**Verdict: PLAUSIBLE** — The storage exists and is measured, the sensor and the ranging that would fill it are already specified, and the NFC peripheral that would read it out is on the die. What is not established is the write energy and the NVM endurance under this write pattern, and those two numbers decide whether the log is a feature or a battery bug.

Family `telemetry` · value 4/5 against effort 2/5 · part of the halo concept portfolio, `docs/concepts/README.md`.

## What it is

Find My answers 'which city block, about half an hour ago, if a stranger walked past'. In a workshop, a plant room or a field it answers nothing at all, forever, because nobody walks past. In exactly those places the tag itself still knows things: it felt motion, it ranged to its neighbours, its cell sagged.

The concept is to write those events down. A record of {timestamp, event type, peer id, range, quality, orientation} is about 16 bytes. The nRF54L10 has 1 MB of non-volatile memory and the whole firmware occupies 13,164 bytes of it, so the free space holds tens of thousands of records with no part added and no BOM line.

Reading it back has two routes that both already exist on this board. The DULT-mandated NFC tap is the interesting one: a phone taps the tag and gets a URL, and DULT's own format already carries optional parameters. The SWD pads are the other, for a maintenance visit.

For a digital twin this is the difference between a location and a history. 'This pallet was stationary until 14:32, then moved, and was 2.1 m from sensor 7 when it stopped' is a record no tracker on the market produces, because none of them have anywhere to put it.

## Why it beats the alternative

Against streaming everything to a gateway: no gateway. Against streaming over the crowd network: C3's channel is three bits per fifteen minutes, which is a state, not a history.

Against a separate data logger: the storage is already bought. D-7 deleted the SPI NOR flash from the board and the reason was a rail mismatch, not a lack of need; the SoC's own NVM is what replaces it, and it costs nothing.

Against Apple: an AirTag has no log, no readout and no API. This is a capability gap, not a quality gap.

## The numbers

| quantity | value | where it comes from |
|---|---|---|
| NVM on the part, and how much the firmware uses | **1 MB total, 13,164 bytes used (1.27 %)** | SPEC.md section 2a, measured on nRF54L10 |
| Records that fit, at 16 bytes each, in half the free space | **about 32,000** | [derived] (1,048,576 - 13,164) / 2 / 16 |
| Proposed record shape, already specified for the uplink | **{tag_id, peer_id, t_utc, method, range_mm, sigma_mm, quality, rssi_dbm, n_steps} ~ 16 bytes** | research/08 section 11.3 |
| Motion sampling rate DULT already mandates | **10 s at rest, 0.5 s once moving** | draft-ietf-dult-accessory-protocol-00 Table 17 |
| The NFC readout channel that already has to exist | **the SoC's own NFC-A peripheral on two pins, emulating a read-only Type-4 tag** | SPEC.md section 3; research/01 section 4 |

## The evidence

| claim | source | date | confidence |
|---|---|---|---|
| The firmware uses 13,164 bytes of flash on a 1 MB part, so the space is free and measured rather than assumed | SPEC.md section 2a; DECISIONS.md D18 | 2026-09-04 | primary, measured |
| The SPI NOR flash was deleted from halo_rev_a for a rail mismatch (GD25LQ32E is a 1.65-2.0 V part on a raw 3.0 V cell), not because logging was unwanted | electronics/halo_rev_a/schematic.py delta D-7 | 2026-09-04 | primary, source read locally |
| Tags should report raw ranges with quality metadata rather than solved positions, and the record shape is already drafted | research/08 section 11.3; DECISIONS.md D12 | 2026-09-03 | primary |
| DULT's NFC payload is a URL with optional parameters (b battery, bt MAC, fv firmware version) beside the required pid and e | draft-ietf-dult-accessory-protocol-00 section 3.15.5 | fetched 2026-09-03 | primary |
| Find My cannot supply a history at room scale: mean raw report error ~100 m, median 26 min latency, and zero reports where nobody walks past | PETS 2021 Tables 5-7; research/02 section 10.4 | fetched 2026-09-03 | primary |

**What is NOT established here, stated so nobody inherits it as a fact:**

- The energy of one NVM write on the nRF54L10 and the endurance of the RRAM/flash under a write-every-30-seconds pattern. These are the two numbers that decide the whole concept and neither is in this repository. Settle both by opening the nRF54L10 product specification's non-volatile memory chapter — write current, write time, and the endurance figure — and multiplying out against the 4.2506 uA baseline. If a write costs more than a few microjoules, the log has to batch in RAM and flush rarely, which is a firmware design, not a blocker.
- Whether the DULT URL is the right readout channel or whether a proprietary NDEF record beside it is cleaner. DULT says the URL SHALL be hosted by the network provider, which halo is not — this interacts with the open Network ID question in D19 and should not be resolved casually.
- Whether the NFC field alone can power a readout with the cell dead. Some tag ICs harvest enough from the reader field to answer; whether the nRF54L's NFC-A peripheral does is not established here. If it does, the log survives a flat battery, which changes what the feature is for.

## What it costs

| dimension | cost |
|---|---|
| money | $0.00. No part. The storage and the NFC peripheral are both already paid for. |
| current | UNKNOWN and load-bearing — see the unverified rows. A RAM ring buffer flushed once an hour is almost certainly free against a 4.2506 uA baseline; a write per event at 0.5 s during motion is almost certainly not. The design lives or dies on the flush policy. |
| size | 0 mm. |
| complexity | Moderate. A wear-levelled log in NVM, a flush policy, and a readout format. Zephyr ships NVS and settings subsystems that do most of it. |

## What it would break in the current design

- It puts a durable record of an asset's movements on a device that can be stolen. That is a privacy consequence and it belongs in docs/ANTI-STALKING.md before a line of it is written: a log that survives the tag changing hands is a surveillance artifact. The mitigation — encrypt the log to the owner's key, the same key that already protects the location reports — is cheap and should be in the design from the start, not retrofitted.
- It competes for NVM with the pre-generated key list (C11). 500 keys is 14 kB; a log is much larger. On a 1 MB part neither is scarce, but on the nRF54L05 fallback (0.5 MB) the arithmetic has to be redone.
- It adds a write pattern to a part whose sleep current is the whole battery budget. Nothing else on this board writes NVM in normal operation.

## The smallest experiment that would settle it

Open the nRF54L10 product specification, read the non-volatile memory chapter's write current, write time and endurance figures, and put them into the existing ce-spice rail_droop study as a sixth scenario: baseline advertising plus one 16-byte NVM write every 30 seconds. The study already computes i_avg_uA and life_months_derated, so the answer comes out in the units the project already uses, and it costs one afternoon. If the derated life stays over 24 months the concept is alive; if it does not, the flush policy is the design problem and the experiment has already told you by how much.

## What follows if it works

- The tag becomes useful in exactly the places Find My is useless, which is where Leif's sensors are.
- It is the natural store for C7's ranging measurements between uplink opportunities, so the two concepts share one mechanism.

---

Generated from `spec/concepts.json` by `tools/gen_concepts.py` on 2026-09-05. Do not edit this file; edit the JSON.
