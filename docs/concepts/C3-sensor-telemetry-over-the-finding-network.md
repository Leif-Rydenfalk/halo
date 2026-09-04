# C3 — Sensor telemetry over the finding network, with no gateway of its own

*The status byte is copied into the location report and encrypted to the owner's key, so a halo can report sensor state through a stranger's phone and Apple cannot read it.*

**Verdict: PROVEN** — The mechanism has been running in the field since 2022 (dakhnod/FakeTag, a mailbox sensor) and the receiving half is readable in FindMy.py's source: the status byte comes back at offset 9 of the DECRYPTED report payload. What is not proven is the throughput at any particular place, because that is a property of how many phones walk past — and the experiment below measures exactly that.

Family `telemetry` · value 5/5 against effort 1/5 · part of the halo concept portfolio, `docs/concepts/README.md`.

## What it is

Every Find My advertisement carries a one-byte status field at PDU byte 12. Apple's own protocol spends bits 7:6 on battery level and bits 5:4 on device type. The rest is unallocated, and it rides the network for free.

The decisive property is not that the byte is broadcast — it is what happens next. A finder device does not merely relay a location: it copies the tag's status byte into the location report and encrypts the whole report to the tag's own ephemeral public key. FindMy.py reads it back at `self._decrypted_data[1][9:10]`, in the same block as latitude, longitude and horizontal accuracy. So sensor state travelling this channel is end-to-end encrypted to the owner. Apple relays it and cannot read it, and neither can the stranger whose phone carried it.

That gives halo a capability Apple does not offer at all and no commercial tracker sells: a battery-powered sensor that reports state from anywhere with pedestrian traffic, with no gateway, no SIM, no LoRa, no subscription and no infrastructure of any kind. For Leif's digital twin it is the difference between an asset that is located and an asset that is also *sensed*.

Three channels stack on one advertisement, in increasing cost: the free bits of the status byte (no cost at all); which of several pre-generated keys is advertised in a given window, which is the Send My trick and costs 28 bytes of flash per key; and the Google Find Hub frame halo already emits in the same advertising event, which has its own payload and its own network.

## Why it beats the alternative

Against a cellular or LoRaWAN sensor: no radio module, no antenna, no gateway, no airtime contract, and an average current that does not move at all. The comparison is not close — the marginal cost of this channel is zero.

Against a BLE sensor beacon read by a phone app: those need somebody to walk within range WITH the app installed. This needs somebody to walk past with an iPhone, which is a vastly larger population, and it needs no app on their side and no consent flow, because it is the same mechanism that finds a lost AirTag.

Against doing it on Google's network instead: halo already advertises both, so this is not either/or. Google's Find Hub frame is a second, independent path with its own payload budget — see the open item below.

And against Apple's own product: an AirTag reports its battery level and nothing else. There is no API, no third-party payload, and no accessory in the Find My programme that carries sensor data. This is not a feature Apple does worse. It is one Apple does not have.

## The numbers

| quantity | value | where it comes from |
|---|---|---|
| Status byte, total | **8 bits** | PETS 2021 Table 2, byte 12; research/02 section 1.3 |
| Bits Apple's own decode uses | **7:6 battery level, 5:4 device type** | FindMy.py findmy/scanner/scanner.py BATTERY_LEVEL / APPLE_DEVICE_TYPE; research/02 section 1.4 |
| Bit named MAINTAINED by the one firmware that exploits this | **bit 2 (0b00000100)** | reference/FakeTag/main.c:38 STATUS_FLAG_MAINTAINED |
| Bits free with no claim about halo that is untrue | **3 (bits 3, 1, 0)** | [derived] — the bits no open decode assigns a meaning to |
| Bits demonstrated working end to end in the field | **6 (bits 5:0)** | reference/FakeTag/main.c:34 STATUS_FLAG_COUNTER_MASK 0b00111111, and its README |
| Where the byte is read on the owner's side | **offset 9 of the decrypted report payload** | reference/FindMy.py/findmy/reports/reports.py:196 |
| Ceiling on update rate | **one value per key window = one per 15 min** | DULT 3.5.1 key rotation; PETS section 6.3 four reports per key |
| Latency from sensing to readable | **median 26 min, hours if the finder is in low-power mode** | PETS 2021 section 6.3, quoted in research/02 section 1.6 |
| Extra current this costs | **0 uA — one register write into a payload that is transmitted anyway** | [derived] the 4.2506 uA baseline does not contain a term for the value of a byte |
| Extra money this costs | **$0.00** | [derived] no part is added |

### The arithmetic, written out

```
Channel capacity, if a finder passes in every key window:
  6 bits per 15 min window  =  6 / 900 s  =  0.0067 bit/s
                            =  96 windows/day x 6 bits  =  576 bits/day  =  72 bytes/day

With the conservative 3-bit budget that claims nothing untrue about the device:
                            =  96 x 3  =  288 bits/day  =  36 bytes/day

Adding key-multiplexing (Send My style), k bits per window from 2^k keys:
  flash cost  =  2^k x 28 bytes per window
  k = 8  ->  256 keys x 28 B  =  7.2 kB per window, 8 extra bits
  the nRF54L10 has 1 MB of NVM and the firmware uses 13,164 bytes of it

In a place no stranger walks (a plant room, a workshop, a field):
  reports per day  =  0.   The channel does not degrade, it stops. See C9.
```

## The evidence

| claim | source | date | confidence |
|---|---|---|---|
| The status byte reaches the owner through the network and is usable as a data channel — a vibration sensor on a mailbox, in service since 2022 | github.com/dakhnod/FakeTag README, local copy reference/FakeTag/README.md; hackaday.com/2022/05/30/check-your-mailbox-using-the-airtag-infrastructure/ | read 2026-09-05 (project 2022) | primary, source read locally |
| Six bits of the status byte are used as a counter: STATUS_FLAG_COUNTER_MASK 0b00111111, written into the advertisement at offline_finding_adv_template[6] | reference/FakeTag/main.c:34, :141, :316-317 | read 2026-09-05 | primary, source read locally |
| The status byte is carried inside the ENCRYPTED report, not merely broadcast: it is read at offset 9 of the decrypted payload, beside latitude at 0:4 and horizontal accuracy at 8:9 | reference/FindMy.py/findmy/reports/reports.py:189-197 | read 2026-09-05 | primary, source read locally |
| Bits 7:6 are battery level and 5:4 are device type | FindMy.py findmy/scanner/scanner.py BATTERY_LEVEL / APPLE_DEVICE_TYPE, quoted in research/02 section 1.4 | fetched 2026-09-03 | primary |
| Advertisement layout: byte 12 is Status, 13-34 the key, 35 the displaced key bits, 36 the Hint | PETS 2021 Table 2, transcribed research/02 section 1.3; cross-checked against OpenHaystack ESP32 firmware | fetched 2026-09-03 | primary |
| A finder uploads at most four reports for the same advertisement key; median generation-to-upload 26 min; reports retained seven days | PETS 2021 sections 6.3-6.4, quoted research/02 section 1.6 | fetched 2026-09-03 | primary |
| halo already carries an accelerometer on I2C whose low-power current is under 1 uA, so there is a sensor to report before anything is added | research/05 section on LIS2DW12TR (LCSC C189624, <1 uA low power); electronics/README.md section 7 | 2026-09-03 | primary (datasheet figure transcribed by lane E) |

**What is NOT established here, stated so nobody inherits it as a fact:**

- Whether the nRF54L10 has an on-die temperature sensor and what it costs to read. The nRF52 family has a TEMP peripheral; no document in this repository says so for nRF54L. Settle it by opening the nRF54L10 product specification's TEMP chapter — a five-minute job, not a research project.
- Whether the Hint byte (PDU byte 36, 0x00 on iOS reports) survives the round trip into the report. PETS says only what iOS puts there. If it does survive, the budget doubles. Settle it by putting a non-zero value there in the experiment below and looking for it in the fetched report.
- The payload budget in Google's Find Hub frame for the same trick. halo emits the frame byte for byte against Google's Tables 15 and 17 (D19) but this lane did not read the spec for spare bits.

## What it costs

| dimension | cost |
|---|---|
| money | $0.00 per unit. No part is added. The accelerometer that provides the first sensor is already on the board for DULT. |
| current | 0 uA. The status byte is transmitted in every advertisement whether it carries information or not; setting it is one register write. The measured 4.2506 uA baseline is unchanged. |
| size | 0 mm. Nothing is placed. |
| complexity | Small on the tag — one byte and a sensor read. Real on the receiving side: the fetch tool must decode the byte per halo's own schema, and that schema has to be published or the data means nothing. Budget the schema, not the firmware. |

## What it would break in the current design

- Nothing in the hardware, and nothing in the current budget.
- It collides with a decision halo already made. D19 refused to advertise Google's DULT Network ID 0x02 because that would be a false claim about who we are, and advertised 0x00 UNREGISTERED instead. Overwriting status bits 5:4 — which is exactly what FakeTag does to get six bits — makes the tag claim to be an 'Apple Device' or 'AirPods' depending on the sensor value. That is the same kind of false claim. THE DESIGN RULE THAT FALLS OUT: use bits 3, 1 and 0, and the hint byte if it survives; never bits 5:4. The budget is 3 bits, not 6, and the difference is honesty, not capability.
- Bits 7:6 must stay honest too. DULT's Get_Battery_Level opcode and the NFC URL's `b` parameter both report battery, and a tag whose battery bits carry a temperature reading is lying to an anti-stalking scanner.
- Key-multiplexing (the Send My path) does break something real: a key spent carrying data is a key not spent being findable, and the DULT rotation schedule is normative. Any scheme that chooses keys by data must still rotate on DULT's clock.

## The smallest experiment that would settle it

Flash two halos with firmware that writes a 3-bit counter into status bits 3/1/0 and a distinctive non-zero value into the hint byte, incrementing once per key window. Put one in a busy street and one in the workshop. Leave them 48 hours. Fetch with FindMy.py and count: how many distinct counter values arrived, how many were lost, what the latency distribution was, and whether the hint byte came back. That single fixture answers three questions at once — the channel's real capacity at each site, whether the hint byte is free, and the report-density question research/02 section 11 lists as the project's biggest open risk.

## What follows if it works

- halo becomes a sensor platform, not only a tracker, and that is the difference GOAL.md asks for between finding a thing and knowing about it.
- The same fixture measures report density, which is the project's largest standing risk (research/02 section 11 item 1).
- It composes with C9: where the count comes back zero, a private finder turns it into full coverage.

---

Generated from `spec/concepts.json` by `tools/gen_concepts.py` on 2026-09-05. Do not edit this file; edit the JSON.
