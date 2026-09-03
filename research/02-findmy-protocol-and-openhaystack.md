# 02 — The Find My network protocol and the open-source ecosystem that rides it

Research lane B. All fetches performed **2026-09-03** unless stated otherwise.
Raw page text is archived under `research/fetched/B-*`; every URL is also in
`research/sources.tsv` with lane tag `B`.

Conventions used here:
- **[verified]** — I read the primary artefact (spec text, source file, API response) myself.
- **[secondary]** — a credible third party asserts it; I did not see the primary.
- **[unverified]** — plausible but I could not confirm; do not build a decision on it.

---

## 0. The one-paragraph answer

Apple's *offline finding* (OF) network is a one-way, non-connectable BLE broadcast
of a NIST P-224 public key, wrapped in an Apple manufacturer-specific advertisement
(`0xFF 4C 00 12 19 …`). A tag does nothing but shout that key; every nearby iPhone
encrypts its own GPS fix under it and posts the ciphertext to Apple. There is no
pairing, no handshake, no association with an Apple account **at the radio layer** —
which is exactly why a $1 microcontroller can join the network, and why
OpenHaystack works at all. The hard part is not the tag; it is *fetching the reports
back*, which needs an authenticated Apple account. That is the fragile, actively
policed half of the stack.

---

## 1. Apple offline finding — the protocol

### 1.1 The four phases

OpenHaystack's README names the four phases the same way the PETS paper does
(`research/fetched/B-openhaystack-README.md`, fetched 2026-09-03) **[verified]**:

> **Pairing (1)** … we generate a public-private key pair on an elliptic curve (P-224). The private key remains on the Mac securely stored in the keychain, and the public key is deployed on the accessory
>
> **Losing (2)** … the accessories broadcast the public key as Bluetooth Low Energy (BLE) advertisements … Nearby iPhones will not be able to distinguish our accessories from a genuine Apple device or certified accessory.
>
> **Finding (3)** When a nearby iPhone receives a BLE advertisement, the iPhone fetches its current location via GPS, encrypts it using public key from the advertisement, and uploads the encrypted report to Apple's server. All iPhones on iOS 13 or newer do this by default.
>
> **Searching (4)** Apple does not know which encrypted locations belong to which Apple account or device. Therefore, every Apple user can download any location report as long as they know the corresponding public key.

Source: <https://github.com/seemoo-lab/openhaystack> (README, fetched 2026-09-03).

### 1.2 Cryptography and key rotation

From Heinrich, Stute, Kornhuber & Hollick, *"Who Can Find My Devices? Security and
Privacy of Apple's Crowd-Sourced Bluetooth Location Tracking System"*, PoPETs
2021(3):227–245, §6.1, PDF at
<https://www.petsymposium.org/2021/files/papers/issue3/popets-2021-0045.pdf>
(fetched 2026-09-03, text archived as
`research/fetched/B-pets-2021-0045-who-can-find-my-devices.txt`) **[verified]**:

> Initially, each owner device generates a private–public key pair (d₀, p₀) on the NIST P-224 curve and a 32-byte symmetric key SK₀ that together form the **master beacon key**. Those keys are never sent out via BLE and are used to derive the rolling advertisement keys included in the BLE advertisements.

> OF iteratively calculates the advertisement keys (dᵢ, pᵢ) for i > 0 as follows using the **ANSI X.963 key derivation function (KDF) with SHA-256** and a generator G of the NIST P-224 curve:

```
  SK_i      = KDF(SK_{i-1}, "update",    32)     (1)
  (u_i,v_i) = KDF(SK_i,     "diversify", 72)     (2)
  d_i       = (d_0 * u_i) + v_i                  (3)
  p_i       = d_i * G                            (4)
```

> Equation (1) derives a new symmetric key from the last used symmetric key with 32 bytes length. Equation (2) derives the so-called "anti-tracking" keys uᵢ and vᵢ … Finally, Eqs. (3) and (4) create the advertisement key pair via EC point multiplication using the anti-tracking keys and the master beacon key d₀.

Note the paper's own inconsistency: Eq. (2) says 72 bytes, the prose says
"a length of 36 bytes each" — 2 × 36 = 72, so both are consistent. **[verified]**

Only the **X coordinate** is advertised. Paper footnote 2:

> More precisely, OF only advertises the X coordinate of the public key, which has a length of 28 bytes. The Y coordinate is irrelevant for calculating a shared secret via ECDH, so the sign bit for the compressed format can be omitted.

**Report encryption** (finder side), §6.1 **[verified]**:

1. generate ephemeral P-224 key pair (d′, p′)
2. ECDH with the advertised public key pᵢ
3. ANSI X9.63 KDF over the shared secret, *with the advertised public key as
   shared info*, SHA-256
4. first 16 bytes → AES key e′
5. last 16 bytes → IV
6. AES-GCM encrypt the location report

> All location reports are identified by an ID, i.e., the **SHA-256 hash of pᵢ**.

**Report binary format** (Fig. 2 of the paper) **[verified]**: 4 B timestamp
(seconds since 2001-01-01) ‖ 1 B confidence ‖ 57 B ephemeral public key ‖
10 B encrypted location ‖ 16 B AES-GCM tag = 88 bytes. The plaintext inside is
4 B latitude ‖ 4 B longitude ‖ 1 B horizontal accuracy ‖ 1 B status.

**Key rotation cadence**, §6.2 **[verified]**:

> **Advertising Interval.** The same key is emitted during a window of **15 minutes**, after which the next key p_{i+1} is used. During a window, OF-enabled iOS and macOS devices emit **one BLE advertisement every two seconds** when they lose Internet connectivity.

### 1.3 The BLE advertisement — byte table

PETS Table 2, *"OF advertisement format (with zero-indexed bytes)"* **[verified]** —
this table counts the 6-byte BLE advertising address as bytes 0–5, i.e. it describes
the whole on-air PDU payload, not just the AD structure:

| Byte  | Field | Value / derivation | Notes |
|-------|-------|--------------------|-------|
| 0–5   | BLE advertising address | `(p_i[0] \| 0b11000000)` ‖ `p_i[1..5]` | Random static address; top two bits forced to `0b11` per BT spec, so those two bits of the key move to byte 35 |
| 6     | AD length | `0x1E` (30) | length of the single AD structure that follows |
| 7     | AD type | `0xFF` | Manufacturer Specific Data |
| 8–9   | Company ID | `0x4C 0x00` (little-endian `0x004C`) | Apple, Inc. |
| 10    | Apple subtype | `0x12` | "Offline Finding" |
| 11    | Subtype length | `0x19` (25) | bytes 12–36 |
| 12    | Status | e.g. `0x00` | battery / device-type bits, see §1.4 |
| 13–34 | Public key | `p_i[6..27]` (22 bytes) | remainder of the 28-byte X coordinate |
| 35    | Public key high bits | `p_i[0] >> 6` | the two bits displaced by the address constraint |
| 36    | Hint | `0x00` | "0x00 on iOS reports" per the paper |

Total on-air: 6 + 31 = 37 bytes, i.e. the legacy BLE advertising maximum.

The paper's explanation of *why* the key is split **[verified]**:

> Apple had to engineer its way around the fact that one BLE advertisement packet may contain at most 37 bytes … of which 6 bytes are reserved for the advertising MAC address, and up to 31 bytes can be used for the payload. For standard compliance, the custom OF advertisements needs to add a 4-byte header for specifying manufacturer-specific data, which leaves 27 bytes. Within this space, Apple uses a custom encoding for subtypes used by other wireless services such as AirDrop, which leaves **25 bytes for OF data**. To fit the 28-byte advertisement key in one packet, Apple **re-purposes the random address field to encode the key's first 6 bytes**. However, there is one caveat: the BLE standard requires that the first two bits of a random address are set to `0b11`. OF stores the first two bits of the advertisement key together with the 24 remaining bytes in the payload to solve the problem. … **Apple confirmed the reverse-engineered specification later.**

The canonical implementation is the OpenHaystack ESP32 firmware,
<https://raw.githubusercontent.com/seemoo-lab/openhaystack/main/Firmware/ESP32/main/openhaystack_main.c>
(fetched 2026-09-03, archived as `B-openhaystack-esp32-main.c`) **[verified]**:

```c
/** Advertisement payload */
static uint8_t adv_data[31] = {
    0x1e, /* Length (30) */
    0xff, /* Manufacturer Specific Data (type 0xff) */
    0x4c, 0x00, /* Company ID (Apple) */
    0x12, 0x19, /* Offline Finding type and length */
    0x00, /* State */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, /* First two bits */
    0x00, /* Hint (0x00) */
};

void set_addr_from_key(esp_bd_addr_t addr, uint8_t *public_key) {
	addr[0] = public_key[0] | 0b11000000;
	addr[1] = public_key[1];
	/* … addr[2..5] = public_key[2..5] … */
}

void set_payload_from_key(uint8_t *payload, uint8_t *public_key) {
    /* copy last 22 bytes */
	memcpy(&payload[7], &public_key[6], 22);
	/* append two bits of public key */
	payload[29] = public_key[0] >> 6;
}
```

and the advertising parameters:

```c
static esp_ble_adv_params_t ble_adv_params = {
    .adv_int_min        = 0x0640, // 1s
    .adv_int_max        = 0x0C80, // 2s
    .adv_type           = ADV_TYPE_NONCONN_IND,
    .own_addr_type      = BLE_ADDR_TYPE_RANDOM,
    .channel_map        = ADV_CHNL_ALL,
    .adv_filter_policy  = ADV_FILTER_ALLOW_SCAN_ANY_CON_ANY,
};
```

Two hardware-relevant facts fall straight out of this **[verified]**:
- the advert is **`ADV_TYPE_NONCONN_IND`** — non-connectable, non-scannable. The
  tag needs no GATT server, no link-layer connection support, no RX path at all
  for the Find My function. (DULT compliance changes this; see §5.)
- **TX power is never set** by the OpenHaystack ESP32 firmware. The protocol does
  not specify a TX power, and neither does DULT. It is purely a
  range-vs-battery choice for us.

### 1.4 The status byte

The PETS paper says only "Status (e.g., battery level)". The most precise open
decode is in FindMy.py `findmy/scanner/scanner.py`
(<https://raw.githubusercontent.com/malmeloo/FindMy.py/main/findmy/scanner/scanner.py>,
fetched 2026-09-03, archived as `B-findmy-py-scanner.py`) **[verified]**:

```python
APPLE_DEVICE_TYPE = {
    0b00: "Apple Device",
    0b01: "AirTag",
    0b10: "Licensed 3rd Party Find My Device",
    0b11: "AirPods",
}
BATTERY_LEVEL = {0b00: "Full", 0b01: "Medium", 0b10: "Low", 0b11: "Very Low"}
# device_type = (status >> 4) & 0b11
# battery_level = (status >> 6) & 0b11
```

So bits 7:6 = battery level, bits 5:4 = device type, bits 3:0 unspecified/free.

`dakhnod/FakeTag` exploits exactly those free bits as a data channel
(<https://github.com/dakhnod/FakeTag>, README fetched 2026-09-03) **[verified]**:

> It sends out advertisement keys defined in keys.h, rotating keys every hour. Also, an input pin can be defined. Whenever that input pin is triggered, **the status byte increments by one. The first two bits of the status byte contain battery information, the other six bits contain the counter in my code.** … That status byte, traveling through the FindMy network and OpenHaystack, reaches my smarthome and I get a notification.

This is directly relevant to haytag's sensor use case: a few bits of sensor state
ride the Find My network for free.

### 1.5 Near-owner vs separated adverts

FindMy.py distinguishes two OF payload lengths **[verified]**:

```python
class NearbyOfflineFindingDevice(OfflineFindingDevice):
    OF_PAYLOAD_LEN = 0x02  # 2 bytes (status, 2 bits of public key/mac address)

class SeparatedOfflineFindingDevice(OfflineFindingDevice, HasPublicKey):
    OF_PAYLOAD_LEN = 0x19  # 25 bytes (status, pubkey(22), first 2 bits of MAC/pubkey, hint)
```

i.e. a genuine Apple accessory near its owner advertises `… 0x12 0x02 …` — status
byte plus the two displaced key bits, no key material — and only switches to the
full `0x12 0x19` separated advert once it is away from its owner. **OpenHaystack
firmware only ever emits the separated (`0x19`) form.** This is one of the
fingerprints that distinguishes a DIY tag from a certified one.

### 1.6 Upload and fetch

PETS §6.3–6.4 **[verified]**:

- Upload: `HTTPS POST https://gateway.icloud.com/acsnservice/submit`; body prefixed
  with static header `0x0F8AE0` + 1 byte report count (so ≤255 reports/request).
  Headers `X-Apple-Sign1/2/3` carry a device identity certificate, the signing CA
  hash, and an ECDSA signature made **inside the Secure Enclave**.
- Fetch: `HTTPS POST https://gateway.icloud.com/acsnservice/fetch`, HTTP basic auth
  with an Apple ID identifier and a device-specific **search-party-token** that
  "changes at irregular intervals (in the order of weeks)", plus *anisette* headers.
- Latency: "the median time from generating to uploading a location report is
  **26 min**. … The delay can increase to several hours if the finder device is in
  a low power mode." Also: "A finder limits the number of uploaded reports for the
  same advertisement key to **four**."
- Retention: "Apple's servers store OF reports for **seven days**."

That upload authentication — SEP-signed, device-certificate-bound — is why **no
open-source project has ever implemented the finder side.** Open projects only
implement the *tag* and the *fetch*.

---

## 2. OpenHaystack itself

<https://github.com/seemoo-lab/openhaystack> · AGPL-3.0 · 13 486 stars ·
last push 2026-08-17 (GitHub API, queried 2026-09-03) **[verified]**.

**Architecture**: a macOS app + a **Mail plugin**. From the README **[verified]**:

> The OpenHaystack application requires a custom plugin for Apple Mail. It is used to download location reports from Apple's servers via a private API (technical explanation: the plugin inherits Apple Mail's entitlements required to use this API). Therefore, the installation procedure is slightly different and requires you to temporarily disable Gatekeeper.

Requires macOS 11+, and Mail must stay open while fetching.

**Firmware targets** (README table) **[verified]**:

| Platform | Tested on | Comment |
|---|---|---|
| Nordic nRF51 | BBC micro:bit v1 | "Only supports nRF51822 at this time (see issue #6)." |
| Espressif ESP32 | ESP32-WROOM, ESP32-WROVER | "Deployment can take up to 3 minutes. Requires Python 3." |
| Linux HCI | Raspberry Pi 4 w/ Raspbian | "Should support any Linux machine." |

**The disclaimer matters for us** **[verified]**:

> OpenHaystack is experimental software. The code is untested and incomplete. For example, OpenHaystack accessories using our firmware **broadcast a fixed public key and, therefore, are trackable by other devices in proximity** (this might change in a future release).

The ESP32 firmware README repeats it: "currently only implements advertising a
single static key. This means that **devices running this firmware are trackable**".

**Maintenance state (2026-09-03)** **[verified via GitHub API]**: the last
*code* commit to `main` is **2024-07-08** ("Use macOS 14 runner with Xcode 15.3").
The 2026-08-17 push is a README edit removing a dead owlink.org link. 130 open
issues. **Treat upstream OpenHaystack as archived-in-practice: a specification
artefact, not a maintained product.** The living work has moved to
Macless-Haystack and FindMy.py.

**Does it still work in 2026?** Mixed evidence, and this is important enough to
quote rather than summarise.

- Issue #283 *"Does this still work?"* opened 2025-11-06, **still open**
  (<https://github.com/seemoo-lab/openhaystack/issues/283>). Comment 2026-06-02
  by `dennisdebel`: *"With a combination of the latest compile, some manual
  flashing, I cant seem to get a OG ESP32 WROOM module to advertise, although the
  serial monitor says 'advertising started', the OpenHaystack app always returns
  'no reports found'"* **[verified]**
- Issue #286 *"Does the iOS update have an impact on location reporting for custom
  tag devices?"* opened 2026-02-06 by a user on iPhone 17 / iOS 26.2.1: *"my
  device is broadcasting and has been right beside me, but it only updates its
  location sporadically—unless I go to a crowded area."* Reply 2026-04-13 by
  `lovelyelfpop`: *"**Since September 27th 2025, the locations of custom tags have
  rarely updated.** I found my iphone 8 (ios 16.7.11) no longer reports my tags'
  locations, even new tags with new keys. When I went to the office, my tags works
  again, there are a lot of iPhones in my office and maybe part of them can report
  tags' locations."* **[verified]**
- Meanwhile Macless-Haystack shipped **v2.7.2 on 2026-03-15** and FindMy.py shipped
  **v0.10.1 on 2026-06-01** **[verified via GitHub API]** — both would be dead
  projects if the network had closed to DIY tags.

**Assessment [my judgement, flag as such]:** unregistered OpenHaystack-style tags
still receive reports as of mid-2026, but report density has visibly degraded and
users report needing crowded environments. Whether this is deliberate Apple
throttling of non-certified `0x12 0x19` adverts, an artefact of iOS 18/26 finder
behaviour, or simply reduced iPhone participation, **is not established by any
source I found. Mark as an open risk for the project, not a settled fact.**
See §9 for what to do about it.

---

## 3. Every open-source project found

GitHub metrics from the GitHub REST API, queried **2026-09-03**. "Last push" is
`pushed_at`, which includes non-default branches.

| Name | URL | Language / target | What it does | Licence | Last push | Stars | Status |
|---|---|---|---|---|---|---|---|
| **OpenHaystack** | github.com/seemoo-lab/openhaystack | Swift + C (nRF51822, ESP32, Linux HCI) | The reference: macOS app + Mail plugin + tag firmware | AGPL-3.0 | 2026-08-17 (code: 2024-07-08) | 13 486 | Spec artefact; code effectively frozen |
| **Macless-Haystack** | github.com/dchristl/macless-haystack | Dart/Flutter + C + Python | Full DIY stack with no Mac: key gen, Docker endpoint, Android/web UI, ESP32 + nRF5x firmware | AGPL-3.0 | 2026-03-15 (v2.7.2) | 2 169 | **Actively maintained — the practical route** |
| **FindMy.py** | github.com/malmeloo/FindMy.py | Python | Fetch + decrypt reports for AirTags, iDevices and OpenHaystack tags; scan and decode nearby OF adverts | **MIT** | 2026-09-01 (v0.10.1, 2026-06-01) | 3 235 | **Most active; MIT so we can use it in tools/** |
| **biemster/FindMy** | github.com/biemster/FindMy | Python + C | Mac-free report fetching; firmware for ESP32, **Lenze ST17H66**, **Telink TLSR825X**, **WCH CH592**, BlueZ | **none declared** | 2024-12-12 | 719 | Dormant; irreplaceable as the cheap-silicon firmware index |
| **acalatrava/openhaystack-firmware** | github.com/acalatrava/openhaystack-firmware | C (nRF51/nRF52, SoftDevice S130/S132, SDK11) | The low-power nRF rewrite everyone else forks | MIT | 2023-12-21 | 201 | Dormant but MIT — legally the best base |
| **pix/heystack-nrf5x** | github.com/pix/heystack-nrf5x | C (nRF51822, nRF52810, nRF52832) | Maintained acalatrava descendant: rolling keys (MAX_KEYS up to 500), DC/DC variants, TX-power stepping, tested on a real Tile tag | **none declared** | 2024-11-02 | 116 | Dormant; closest match to an nRF52 haytag |
| **dakhnod/FakeTag** | github.com/dakhnod/FakeTag | C (nRF51) | Hourly key rotation + status-byte side channel for a mailbox sensor | MIT | 2026-06-22 | 476 | Alive-ish; author explicitly says "not for beginners", keys generated by an undisclosed mechanism |
| **openhaystack-zephyr** | github.com/koenvervloesem/openhaystack-zephyr | C (Zephyr, any Zephyr BLE board) | Zephyr module form of the tag; single static key, no power management | MIT | 2022-06-10 | 90 | Dormant; cleanest base if haytag targets Zephyr/NCS |
| **tranthanh1699/findmy_nrf** | github.com/tranthanh1699/findmy_nrf | C (Zephyr) | Fork of openhaystack-zephyr | MIT | 2022-06-10 | 0 | Dead fork; ignore |
| **positive-security/find-you** | github.com/positive-security/find-you | Swift + C (ESP32) | Stealth clone: 2 000 pre-generated keys, one beacon per key, defeats unwanted-tracking alerts | AGPL-3.0 | 2022-02-24 | 1 242 | Dormant; read as the rolling-key reference and as the thing we must NOT be |
| **positive-security/send-my** | github.com/positive-security/send-my | C (ESP32) + Swift | Upload-only modem: arbitrary data encoded into advertised public keys, ~3 bytes/s | AGPL-3.0 | 2023-11-13 | 1 884 | Dormant; the telemetry-over-Find-My reference |
| **wistoff/Send-My-Python** | github.com/wistoff/Send-My-Python | C + Python | Send My with a Python receiver instead of the macOS app | AGPL-3.0 | 2024-06-24 | 9 | Dormant |
| **patlab-ucsd/tagalong** | github.com/patlab-ucsd/tagalong | C | Academic Send My fork | AGPL-3.0 | 2024-07-22 | 8 | Dormant |
| **seemoo-lab/AirGuard** | github.com/seemoo-lab/AirGuard | Kotlin (Android; also an iOS app) | Anti-tracking scanner; detects AirTags and Find My accessories, notifies "in less than an hour" | Apache-2.0 | 2026-08-30 | 2 488 | **Actively maintained — our test harness** |
| **Dadoum/anisette-v3-server** | github.com/Dadoum/anisette-v3-server | D | Serves Apple "anisette" auth data so a non-Apple host can log into iCloud | **none declared** | 2026-08-01 | 554 | Active; hard dependency of every Mac-free stack |
| **JJTech0130/pypush** | github.com/JJTech0130/pypush | Python | APNs/iMessage client; the Apple-ID auth breakthrough that removed the Mac requirement | NOASSERTION | 2026-03-15 | 3 772 | Active |
| **Chapoly1305/FindMy** | github.com/Chapoly1305/FindMy | Python | Another Find My query fork | GPL-3.0 | 2025-11-20 | 44 | Low activity |
| **jichaowang02-lang/macless-haystack-esp32s3** | github.com/jichaowang02-lang/macless-haystack-esp32s3 | C (ESP32-S3) | Ready-to-flash S3 build that upstream lacks | AGPL-3.0 | 2026-07-10 | 1 | New, unproven |
| **seemoo-lab/BTLEmap** | github.com/seemoo-lab/BTLEmap | Swift | "Nmap for BLE" — the scanner used to capture OF adverts for the PETS paper | Apache-2.0 | 2024-06-11 | 216 | Dormant |
| **seemoo-lab/owl** | github.com/seemoo-lab/owl | C | Open AWDL implementation — sibling SEEMOO reverse-engineering project, **not** Find My | GPL-3.0 | 2026-08-17 | 1 530 | Context only |
| **seemoo-lab/toothpicker** | github.com/seemoo-lab/toothpicker | Python | iOS Bluetooth fuzzer from the same lab | MIT | 2021-09-21 | 246 | Context only |
| **lesleyxyz/node-tile** | github.com/lesleyxyz/node-tile | TypeScript | Reverse-engineered Tile client — talk to and ring a Tile | MIT | 2025-03-12 | 40 | Dormant; only open Tile client found |
| **google/nearby** | github.com/google/nearby | C++ | Google's Fast Pair / Nearby reference implementation | Apache-2.0 | 2026-09-02 | 962 | Active; the Google-network path |

**Licence warning for firmware planning.** OpenHaystack, Macless-Haystack, Find You
and Send My are all **AGPL-3.0**. `acalatrava/openhaystack-firmware`,
`openhaystack-zephyr`, `FakeTag` and `FindMy.py` are **MIT**. `heystack-nrf5x` and
`biemster/FindMy` declare **no licence at all** (default: all rights reserved —
readable, not reusable). If haytag firmware is to be permissively licensed, the
derivation chain must start from the MIT set. Lane 06 owns this decision; this is
the input.

---

## 4. Macless-Haystack — the practical stack in 2026

<https://github.com/dchristl/macless-haystack> · AGPL-3.0 · 2 169 stars ·
v2.7.2 released 2026-03-15 **[verified]**. README **[verified]**:

> This project tries to unify several projects for an easy-to-use and easy-to-setup custom FindMy network. The goal is to run a FindMy network **without the need to own a real Mac or virtual Mac**. Also you don't have to install the mail plugin or openhaystack itself.

Prerequisites, verbatim: *"Docker installed · Python3 and pip3 installed ·
**Apple-ID with 2FA enabled. Only sms/text message as second factor is
supported!**"* Components: `dadoum/anisette-v3-server` on :6969 and
`christld/macless-haystack` endpoint on :6176, plus a Flutter web/Android frontend.

Credits section names exactly what was merged **[verified]**:

> - The original Openhaystack — Stripped down to the mobile application (Android) and ESP32 firmware. **ESP32 firmware combined with FindYou project and optimizations in power usage.**
> - Biemster's FindMy — … The standalone python webserver for fetching the FindMy reports
> - Positive security's Find you — ESP32 firmware customization for battery optimization
> - acalatrava's OpenHaystack-Fimware alternative — **NRF5x firmware customization for battery optimization**

Crucially, the nRF5x firmware README states the rolling-key behaviour
(<https://raw.githubusercontent.com/dchristl/macless-haystack/main/firmware/nrf5x/README.md>,
fetched 2026-09-03) **[verified]**:

> This firmware consumes more power when more than 1 key is used. **The controller wakes up every 30 minutes and switches the key.** … Currently, only the NRF51 build has been tested, and **the NRF52 build has not been tested yet**, but it should work.

Keys are patched into a prebuilt binary by searching for the ASCII marker
`OFFLINEFINDINGPUBLICKEYHERE!` — the same trick `openhaystack-zephyr` uses. Note
the mismatch: **Apple rotates every 15 min, macless-haystack every 30 min.** No
source explains whether the 30 min choice is a battery compromise or a
compatibility finding; **[unverified]**.

And a note that matters for our silicon choice **[verified]**:

> In general, any OpenHaystack-compatible device or its firmware is also compatible with Macless-Haystack (i.e. the ST17H66). Typically, only the Base64-encoded advertisement key is required.

`biemster/FindMy`'s README makes the cost point explicit **[verified]**:

> Deploy your advertisement keys on devices supported by OpenHaystack. The ESP32 firmware is a mirror of the OpenHaystack binary, **the Lenze 17H66 is found in many 1$ tags obtained from Ali**.

**Fragility.** The Macless-Haystack FAQ documents that Apple actively pushes back
on the *fetch* side **[verified]**:

> During the registration, an error occurs, for example: `It seems your account score is not high enough. Log in to https://appleid.apple.com/ and add your credit card (nothing will be charged) or additional data to increase it.` … **Unfortunately, there is no general solution as Apple changes the mechanism.**

Open issues on macless-haystack as of 2026-09-03 include "keep stucked on 2FA
verification" (2026-04-03), "A server problem is blocking Apple ID sign in"
(2026-03-14), "Account limit reached" (2026-01-27) **[verified]**. Also worth
flagging to whoever builds our tooling: open issue 2026-08-07 —
*"generate_keys.py uses random.getrandbits() (non-CSPRNG) for private keys —
should use secrets"* **[verified]**. Do not copy that key generator.

---

## 5. IETF DULT — what a compliant tag must do

The cross-platform anti-stalking standard. Apple Newsroom, 13 May 2024
(<https://www.apple.com/newsroom/2024/05/apple-and-google-deliver-support-for-unwanted-tracking-alerts-in-ios-and-android/>,
fetched 2026-09-03) **[verified]**:

> Apple and Google have worked together to create an industry specification — **Detecting Unwanted Location Trackers** … **Today Apple is implementing this capability in iOS 17.5, and Google is now launching this capability on Android 6.0+ devices.** … users will now get an "[Item] Found Moving With You" alert on their device if an unknown Bluetooth tracking device is seen moving with them over time, regardless of the platform the device is paired with. … Bluetooth tag manufacturers including **Chipolo, eufy, Jio, Motorola, and Pebblebee** have committed that future tags will be compatible.

Status **[verified]**: `draft-ietf-dult-accessory-protocol` is still at **rev 00**,
document dated 4 Nov 2024, datatracker last-touched 2025-05-07. Authors: B. Ledvina
and B. Detwiler (Apple), D. Lazarov and S. P. Polatkan (Google). Intended status
**Informational**. Siblings: `draft-ietf-dult-finding-01` (5 June 2025, Fossaceca
+ Rescorla) and `draft-ietf-dult-threat-model-05` (2026-08-06). **No RFC yet.**
Text archived as `B-draft-ietf-dult-*.txt`.

### 5.1 Does it apply to haytag?

§2.1 Applicability **[verified]**:

> These best practices are **REQUIRED** for location-enabled accessories that are **small and not easily discoverable**. For large accessories, such as a bicycle, these best practices are RECOMMENDED.
> Accessories are considered easily discoverable if they meet one of the following criteria: The item is larger than 30 cm in at least one dimension. The item is larger than 18 cm x 13 cm in two of its dimensions. The item is larger than 250 cm³ in three-dimensional space.

A 32 mm puck is nowhere near any of those thresholds. **DULT is REQUIRED for
haytag by its own terms.** (It is an Internet-Draft, so "required" is normative
language inside a document with no legal force — but it is the yardstick Apple and
Google both certify against, and the yardstick AirGuard measures with.)

### 5.2 The DULT advertisement (a *different* advert from Find My)

§3.4.2 Table 1 **[verified]**:

| Bytes | Description | Requirement |
|---|---|---|
| 0–5 | MAC address | REQUIRED |
| 6–8 | Flags TLV; length = 1 byte, type = 1 byte, value = 1 byte | OPTIONAL |
| 9–12 | Service Data TLV; length = 1 byte, type = `0x16`, value = `0xFCB2` | REQUIRED |
| 13 | Network ID | REQUIRED |
| 14 | Near-owner bit (1 bit, LSB) + reserved (7 bits) | REQUIRED |
| 15–36 | Proprietary company payload data | OPTIONAL |

Note this is a **16-bit service-data UUID `0xFCB2`** advert, not an Apple
manufacturer-specific advert. The Network ID byte is "set based on a registered
value for the manufacturer" — but the draft's registry section is a `TODO:
Section Finding Network Registry has been removed`. Google's spec (§7) says
`Get_Network_ID should return Google's identifier (0x02)`. **Apple's Network ID
value is not published anywhere I could find [unverified].** There is no open path
for an unaffiliated project to obtain a Network ID.

### 5.3 The behaviour requirements (all **[verified]** from the draft)

| Requirement | Value | Draft § |
|---|---|---|
| Transport | BLE; accessory SHALL advertise | 3.2.1 |
| **Connection** | "MUST support at least one **non-owner unencrypted connection** in a peripheral role", via GATT | 3.2.2 |
| Non-owner service UUID | `15190001-12F4-C226-88ED-2AC5579F2A85` | 3.11 |
| Non-owner characteristic UUID | `8E0C0001-1D68-FB92-BF61-48377421680E` | 3.11 |
| Advertise while location-enabled | "if location is available to the owner or was available any time within the past **24 hours**" | 3.4.3 |
| Near-owner → separated | after **>30 minutes** physical separation | 3.4.4 |
| Separated → near-owner | within **30 minutes** of reunification | 3.4.5 |
| Address rotation, near-owner | **every 15 minutes** | 3.5.1 |
| Address rotation, separated | **every 24 hours** | 3.5.1 |
| Rotation on state change | SHALL rotate on every near-owner↔separated transition | 3.5.1 |
| **Advertising interval** | "A **maximum advertising interval of 4 seconds SHALL be used**; for the best detection rate, the advertising interval SHOULD be **less than or equal to 2 seconds**." | 3.10 |
| **Sound maker** | "The accessory **MUST include a sound maker** (for example, a speaker) to play sound when in separated state, either periodically or when motion is detected." | 3.13.3 |
| Sound loudness | "minimum **60 Phon** peak loudness as defined by **ISO 532-1:2017** … measured by a calibrated free field microphone **25 cm** from the accessory suspended in free space" | 3.13.3 |
| Sound duration | Sound_Start "MUST play sound for a minimum duration of **5 seconds** and a maximum duration of **30 seconds**. The RECOMMENDED duration is **12 seconds**." | 3.13.4 |
| **Motion detector** | "SHOULD include a motion detector … If the accessory includes an accelerometer, it **MUST be configured to detect an orientation change of ±10° along any two axes**" | 3.13.2 |
| Separated UT timeout | "**random value between 8-24 hours** chosen from a uniform distribution" before enabling the motion detector | Table 17 |
| Motion sampling rate 1 / 2 | 10 s / 0.5 s | Table 17 |
| Backoff | **6 hours** after 20 s of motion or 10 sounds played | 3.13.2.1, Table 17 |
| **Identification** | "MUST include a way to uniquely identify it — either via a serial number or other privacy-preserving solution"; readable over **NFC tap or BLE** | 3.15 |
| BLE identifier gate | "MUST have a physical mechanism, for example, **a button**, that SHALL be required to enable the Get_Identifier opcode" | 3.15.3 |
| NFC payload | a URL `https://{URL}?pid=%04x&b=%02x&fv=%08x&e=%s` — `pid` product data and `e` encrypted identifier REQUIRED; `b` battery, `bt` MAC, `fv` firmware version optional. "The URL SHALL be hosted by the **network provider**." | 3.15.5 |
| Firmware update | "The accessory **SHOULD** have a mechanism for the manufacturer to provide firmware updates." | 5 |
| Accessory category | Location Tracker = 1; Other = 128; then Luggage 129 … Snowboard 142 | 4, Table 23 |

Mandatory GATT opcodes (§3.12.1, Table 4): `Get_Product_Data 0x0003`,
`Get_Manufacturer_Name 0x0004`, `Get_Model_Name 0x0005`,
`Get_Accessory_Category 0x0006`, `Get_Protocol_Implementation_Version 0x0007`,
`Get_Accessory_Capabilities 0x0008`, `Get_Network_ID 0x0009`,
`Get_Firmware_Version 0x000A` (all REQUIRED); `Get_Battery_Type 0x000B` and
`Get_Battery_Level 0x000C` OPTIONAL. Non-owner controls (§3.13.4):
`Sound_Start 0x0300`, `Sound_Stop 0x0301`, `Command_Response 0x0302` all REQUIRED;
`Get_Identifier 0x0404` OPTIONAL. **[verified]**

**Note the conflict with the Find My advert.** The OpenHaystack path uses a
non-connectable Apple manufacturer advert with a 15-minute rotation and no GATT.
DULT wants a *connectable* `0xFCB2` service-data advert, a 24-hour rotation while
separated, and a GATT server exposing a whole opcode set. A tag that does both
must interleave two advertisement sets and run a connectable link — that is a real
firmware and current-budget cost, not a checkbox.

---

## 6. Apple's official route: the Find My Network Accessory Program

<https://developer.apple.com/find-my/>, fetched 2026-09-03 **[verified]**. The
entire developer-facing content is:

> Let users locate your products with the Find My network. With hundreds of millions of Apple devices around the world, advanced end-to-end encryption, and industry leading security, the Find My network lets users easily locate their belongings in the Find My app with the peace of mind that their privacy is protected.
>
> Whether you're a developer or manufacturer looking to connect an existing or new accessory to the Find My network, **enroll in the MFi Program to access the technical specifications and resources needed to create your product.**

**There is no public download of the Find My Network Accessory Specification.**
The last publicly circulated version was the *Developer Preview – Release R3*
(2020), which OpenHaystack cites in its References section as
"Apple Inc. **Find My Network Accessory Specification – Developer Preview – Release R3.**
2020. 📄 Download https://developer.apple.com/find-my/" **[verified that
OpenHaystack cites it; that download link no longer serves the document]**.

MFi terms (<https://mfi.apple.com/en/faqs.html> and `/how-it-works.html`, fetched
2026-09-03) **[verified]**:

- "**Find My network**" is listed among "MFi licensed technologies and components"
- "**The MFi Program is USD $99 (plus any applicable taxes and fees) per membership year.**"
- "**This information is only available under NDA. You will be able to review this
  information once your application for the MFi License has been approved.**"
- "**Companies, organizations, government entities and educational institutions are
  eligible to apply.**" — i.e. **not individuals.**
- Certification flow: "1. Product Plan … 2. Development … 3. Certification — Use
  Apple's certification tools … **Submit production-ready samples and packaging
  materials for review.** 4. Mass Production — **Upon completion of certification
  approved by Apple**, begin manufacturing and sales."

A silicon vendor's page confirms the practical gate. Telink,
<https://wiki.telink-semi.cn/wiki/protocols/Apple-Find-My/> (fetched 2026-09-03,
note: their TLS certificate has expired; fetched with `curl -k`) **[verified]**:

> **Telink only provides the SDK and support for qualified clients with valid MFi license**, Please contact Telink Sales Team for more details.

Same page describes the accessory feature set that the OpenHaystack path does not
have: **Unwanted tracking detection**, **Lost Mode** ("they can access to the
contact details set by the owner by using NFC or Bluetooth LE"), and **Play sound**
("The Apple device creates Bluetooth LE connections to initiate the actions").

**Verdict for an open-source project.** The official path is structurally closed
to haytag as an open design: $99/yr is trivial, but the **NDA is not** — you
cannot publish an open implementation of a specification you received under NDA,
and Apple must approve production samples before mass production. An open,
self-manufactured, integrate-into-your-own-PCB block cannot be MFi-certified in
the form Leif describes. Document the official path; do not plan on it.

### 6.1 Precision Finding / UWB

<https://developer.apple.com/nearby-interaction/> (fetched 2026-09-03)
**[verified]**:

> Allow people to interact with connected accessories in completely new and exciting ways by leveraging the Ultra Wideband (UWB) chipset in a supported iPhone or Apple Watch.
> **Accessory manufacturers** — Implement the Nearby Interaction accessory protocol with a Nearby Interaction-enabled UWB chipset … *Nearby Interaction Accessory Protocol Specification* … *Nearby Interaction with UWB Interoperability Specification* … *(Developer Preview for iOS 27)*

Those two specifications **are** public downloads (unlike the Find My accessory
spec). But Nearby Interaction is a *separate framework from Find My*: a third-party
UWB accessory ranges against an iPhone **through the developer's own app**, not
through the Find My app's Precision Finding UI. Precision Finding inside Find My is
Apple-first-party. **[secondary — asserted by Apple's own framing that these are
separate programs and by developer-forum consensus; I did not find an Apple
document that states the exclusion in so many words. Treat the exclusion as
strongly indicated, not proven.]**

---

## 7. Google's Find My Device / Find Hub network

Unlike Apple, **Google publishes its accessory specification openly**:
<https://developers.google.com/nearby/fast-pair/specifications/extensions/fmdn>
("Find Hub Network Accessory Specification", an extension to Fast Pair, fetched
2026-09-03, archived as `B-google-fmdn-spec.md`) **[verified]**.

Advertisement (Table 15, 160-bit curve) **[verified]**:

| Octet | Value | Description |
|---|---|---|
| 0 | `0x02` | Length |
| 1 | `0x01` | Flags data type value |
| 2 | `0x06` | Flags data |
| 3 | `0x18` or `0x19` | Length |
| 4 | `0x16` | Service data data type value |
| 5–6 | `0xAA 0xFE` | 16-bit service UUID (Eddystone/Fast Pair `0xFEAA`) |
| 7 | `0x40` or `0x41` | FHN frame type, with unwanted-tracking-protection mode indication |
| 8–27 | 20-byte ephemeral identifier | |
| 28 | Hashed flags | battery and protection status |

Table 16 is the 256-bit-curve variant: length `0x24`/`0x25`, EID at octets 8–39,
hashed flags at 40.

Key facts **[verified]**:
- EID is computed by **AES-ECB-256** encrypting a counter structure under the
  Ephemeral Identity Key, then projecting onto **SECP160R1 or SECP256R1**; only
  the x-coordinate is advertised.
- "Rotation period exponent is fixed and set to 10, corresponding to **1024
  seconds**" — "Rotation should happen every 1024 seconds on average", randomised
  by a positive offset in a 1–204 s window.
- "Providers … should advertise FHN frames **at least once every 2 seconds**."
- Unwanted-tracking-protection mode pins "MAC private address rotation frequency to
  **once per 24 hours**", frame type `0x41`; normal mode is `0x40`.
- "Using 256-bit keys means that older phones that don't support BLE 5 can't"
  [see the source for the full sentence] — the 32-byte EID needs an extended advert.

Compliance gates **[verified]**:

> Certified FHN devices must also meet the requirements in the implementation version of the cross-platform specification for Detecting Unwanted Location Trackers (DULT).
> **Any FHN compatible device must be registered in the Nearby Device Console, and have the "Find Hub" capability activated.**
> Get_Network_ID should return **Google's identifier (0x02)**.
> Get_Accessory_Capabilities **must indicate the support for ringing** as well as BLE identifier lookup.
> Guidelines for implementing Identifier over NFC: As a URL, use **find-my.googleapis.com/lookup**.
> The operation should only return a valid response for **5 minutes** after the user activated the 'identification' mode, which **requires a combination of button presses**.

So: **the Google spec is readable by anyone and implementable in the open, but the
network itself is gated on a console registration and a model ID.** That is a
weaker gate than Apple's NDA — you can write and publish the firmware — but the
tag will not be tracked by the Find Hub network without registration. I found **no
open-source implementation of the Google FHN tag side** in this sweep; the closest
is Google's own `github.com/google/nearby` (Apache-2.0, 962 stars, pushed
2026-09-02) **[verified]**. This is a notable gap and a possible haytag
differentiator.

## 7.1 Samsung and Tile — briefly

- **Samsung SmartThings Find**: reverse-engineered in *"Privacy Analysis of
  Samsung's Crowd-Sourced Bluetooth Location Tracking System"*
  (<https://arxiv.org/pdf/2210.14702>) and the peer-reviewed
  *"Security and Privacy Analysis of Samsung's Crowd-Sourced Bluetooth Location
  Tracking System"*, USENIX Security '24
  (<https://www.usenix.org/system/files/usenixsecurity24-yu-tingfeng.pdf>).
  Tags broadcast a rotating "privacy ID". **No open tag firmware found.**
  **[secondary — I read the search-result abstracts, not the full PDFs.]**
- **Tile** (now Life360): *"Security and Privacy Analysis of Tile's Location
  Tracking Protocol"* (<https://arxiv.org/pdf/2510.00350>) reverse-engineers it by
  decompiling the Android app. The only open client is
  `lesleyxyz/node-tile` (MIT, 40 stars, last push 2025-03-12) which can talk to and
  ring a Tile — **not** join the network. **[secondary/verified metadata]**
- Best single cross-network reference: **"SoK: Offline Finding Protocols for
  Lightweight Location Tracking"**, Kumar, Ortega Pérez, Jaeger, Ristenpart &
  Specter, IACR ePrint 2026/488 (<https://eprint.iacr.org/2026/488.pdf>, fetched
  2026-09-03, archived) **[verified]**. It compares Apple, Google, Samsung and
  Tile side by side and confirms the general parameters: tags change identifiers
  "every Δ_conn = 15 minutes and in the lost mode every Δ_lost = 24 hours"; and
  notes "Tile does not end-to-end encrypt location reports" and "Tile and Samsung
  (default mode) do not encrypt location" — i.e. Apple and Google are the only two
  networks with owner-only location confidentiality.

Also relevant and recent: **"Snatcher: Apple Find My Network Exposes Your Lost
Devices To Strangers"**, arXiv 2606.21067, submitted 19 Jun 2026
(<https://arxiv.org/abs/2606.21067>, abstract fetched 2026-09-03) **[verified
that the paper exists and its abstract says this]**: "insecure BLE advertisements
and design tradeoffs allow unauthorized discovery and physical theft of lost Apple
devices … unencrypted BLE advertisements, unauthenticated acoustic triggers, and
slow MAC address randomization." Read this before finalising the sounder design —
an unauthenticated "play sound" is a theft aid as well as an anti-stalking feature.

---

## 8. Anti-abuse, and what an open tag must not do

**Find You** (Positive Security, <https://positive.security/blog/find-you> and
<https://github.com/positive-security/find-you>, both fetched 2026-09-03,
AGPL-3.0, 1 242 stars, last push 2022-02-24) is the canonical demonstration that
the OpenHaystack advert defeats unwanted-tracking detection **[verified]**:

> Added support to iterate over a preloaded list of public keys with **1 beacon per key** and a configurable delay

The blog explains the mechanism: broadcast "continuously … new, never-seen-before
public keys (just once per public key)", concretely "iterate through **2000 key
pairs** and send **one beacon every 30 seconds** (a public key will therefore be
repeated every ~17 hours)". Apple's and AirGuard's detection both key off an
identifier that persists long enough to be seen repeatedly; never repeating one
defeats both. The blog also notes Apple reduced the AirTag's own unattended beep
from 3 days to "a random time frame between 8 and 24 hours" — which is exactly the
`T_(SEPARATED_UT_TIMEOUT)` "random value between 8-24 hours" now written into DULT
§3.13.2.1 Table 17 **[verified: both sources read].**

Apple's own user-facing documentation confirms that the detection hinges on
identifier persistence — which is precisely what Find You defeats. From
"What to do if you get an alert that an AirTag, set of AirPods, Find My network
accessory, or compatible Bluetooth location-tracking device is with you"
(<https://support.apple.com/en-us/HT212227>, fetched 2026-09-03, archived as
`B-apple-support-airtag-safety.md`) **[verified]**:

> If the option to play a sound isn't available, the item might not be with you anymore or it's within range of its owner. Or **if it was with you overnight, its identifier might have changed. Find My uses the identifier to determine that it's the same item moving with you.**

The same page pins down the platform requirement — "The minimum system requirements
for Tracking Notifications are iOS 14.5 or later … **Compatible Bluetooth
location-tracking devices require iOS 17.5 or later**" — and confirms that
non-owner Precision Finding is limited to Apple's own hardware: "If the unknown
accessory is **an AirTag or AirPods Pro 3 charging case** and you have a supported
iPhone model with Ultra Wideband, you can tap Find Nearby to use Precision Finding".
**[verified]**

**AirGuard** (<https://github.com/seemoo-lab/AirGuard>, Apache-2.0, 2 488 stars,
last push 2026-08-30) **[verified]** is the counterpart and, for us, the test
instrument:

> The app periodically scans your surroundings for potential tracking devices, like AirTags or other Find My devices. If a devices follows you, **you will get a notification in less than an hour!**

**Design consequence for haytag.** Leif's own constraint in `GOAL.md` — "Not a
stalking tool: DULT behaviour is in the block, not an afterthought" — maps onto a
concrete firmware rule: **haytag must use a small, bounded, deterministic rolling
key set derived from a single master beacon key (Apple's own scheme, or
macless-haystack's 30-minute rotation), never a large pre-generated
never-repeating key list.** The Find You pattern must be structurally impossible
in our firmware, not merely discouraged in docs.

---

## 9. Battery and timing implications for the hardware

Everything the protocol dictates that costs current:

| Parameter | Apple OF (from PETS) | OpenHaystack ESP32 | macless-haystack nRF5x | DULT requirement | Google FHN |
|---|---|---|---|---|---|
| Advertising interval | 2 s | 1–2 s random | (inherits) | ≤4 s SHALL, ≤2 s SHOULD | ≥ once per 2 s |
| Advertisement type | non-connectable | `ADV_TYPE_NONCONN_IND` | non-connectable | **connectable** (non-owner GATT) | connectable |
| Key/ID rotation | 15 min | **none — one static key** | wake every 30 min | 15 min near-owner / 24 h separated (address) | ~1024 s |
| Channels | 3 (37/38/39) | `ADV_CHNL_ALL` | all | — | — |
| TX power | unspecified | **not set** | stepped (see below) | unspecified | unspecified |
| Payload | 31 B | 31 B | 31 B | ≤37 B | 29 or 41 B |

**The current budget is set by three numbers: adverts/second × 3 channels ×
31 bytes on air, plus whatever the key rotation costs, plus sleep leakage.**

At 2 s intervals on 3 channels the radio is on for roughly 3 × ~0.4 ms ≈ 1.2 ms
per event, i.e. a **duty cycle around 0.06 %** — which is why sleep current
dominates and why the choice of MCU sleep mode matters more than TX power.
**[my arithmetic from the protocol parameters, not a measurement — mark as
engineering estimate, to be confirmed on hardware by lane E/F.]**

The widely repeated **"CR2032 lasts almost 3 years"** claim traces to a single
GitHub comment, `seemoo-lab/openhaystack` issue #57, comment 841642356,
2021-05-15 by `mowtschan` (fetched 2026-09-03) **[verified as to what the comment
says; the claim itself is UNVERIFIED]**:

> Let's assume we have a battery with a capacity of 230 mAh and we will have ideal temperature of 20°C and also let's 'ignore' battery self-discharging thing. `(230/((0.0033*5+0.066*0.5)/(5+0.5)))/24 = 1064,814` days!!!

Decoded: 3.3 µA sleep for 5 s, 66 µA for 0.5 s, average ≈ **9 µA**, 230 mAh /
9 µA ≈ 25 500 h ≈ 1 065 days ≈ 2.9 years — **ignoring self-discharge, ignoring
CR2032 pulse-load voltage sag, and from a duty cycle that is not the OpenHaystack
2 s advert.** `acalatrava/openhaystack-firmware` repeats it as "It seems that a
CR2032 may last almost 3 years!" and `pix/heystack-nrf5x` repeats it again as
"some estimates suggesting up to three years on a CR2032 battery!". **Three
projects, one unverified forum calculation.** Do not put this number in the
haytag README until we measure it.

What *is* verified about TX power: `heystack-nrf5x`'s own debug log shows the
firmware stepping down until the SoftDevice accepts a level **[verified from its
README]**:

```
<info> app: ble_set_max_tx_power: 8 dB failed
<info> app: ble_set_max_tx_power: 7 dBm failed
... 5 dBm failed
<info> app: ble_set_max_tx_power: 4 dBm
<info> app: Rotating key: 59
```

i.e. on that nRF51822 target the achievable max is **+4 dBm**. `heystack-nrf5x`
also exposes `MAX_KEYS` (examples use 50 and 500) and separate `-dcdc` build
targets — DC/DC converter enabled is a first-order power decision on nRF5x and
needs the inductors on the BOM.

Storage cost of rolling keys, exactly: **28 bytes per advertisement key**. The
macless-haystack flashing instructions show it: "depending on the count of your
keys (in this example 3 keys => **3*28=84 Bytes**)". 500 keys = 14 kB of flash.
At 30-minute rotation, 500 keys ≈ **10.4 days** before wrap-around; at 15-minute
rotation ≈ **5.2 days**. **[verified arithmetic from verified parameters.]**
This is the single biggest firmware-architecture question for haytag: pre-generated
key list (simple, flash-hungry, bounded lifetime) versus on-device P-224 key
derivation (needs an EC point multiply on every rotation — feasible on nRF52
with the CryptoCell/uECC, expensive on an nRF51-class part).

---

## 10. What this means for the hardware

### 10.1 The absolute minimum to be a Find My tag via OpenHaystack

Every one of these is directly evidenced above:

1. **A BLE 4.0+ transmitter.** TX-only, non-connectable, legacy advertising. No
   scanning, no connections, no GATT, no bonding. Any BLE SoC qualifies — nRF51822,
   nRF52810, ESP32, Telink TLSR825X, WCH CH592, Lenze ST17H66 have all been done.
2. **The ability to set a random static BLE address from bytes of the key** — this
   is the only unusual radio requirement, and every BLE stack supports it.
3. **31 bytes of raw advertisement data** set verbatim (`esp_ble_gap_config_adv_data_raw`
   or equivalent) — *not* built by a helpful high-level AD-structure API.
4. **28 bytes of non-volatile storage per advertisement key** (ESP32 uses a
   dedicated `key` flash partition; nRF firmwares patch the binary at the
   `OFFLINEFINDINGPUBLICKEYHERE!` marker).
5. **A ~2 s periodic wake** and, for rolling keys, a 15–30 minute timer.
6. **Nothing else.** No accelerometer, no speaker, no NFC, no button, no RX.

That is the whole hardware requirement. It is why a $1 AliExpress beacon works.
**A haytag that only does this is trivially buildable and trivially cheaper than
$29** — but it is also, by DULT's own applicability test (§5.1), a
non-compliant stalking-capable device.

### 10.2 What DULT compliance adds to the BOM

To be the thing `GOAL.md` actually asks for, add:

| Requirement | Hardware consequence | DULT § |
|---|---|---|
| Non-owner unencrypted GATT connection | The BLE stack must support **peripheral connections**, not just adverts. Rules out TX-only/beacon-only stacks and the smallest flash parts. | 3.2.2 |
| Sound maker, ≥60 Phon @ 25 cm | Magnetic buzzer or piezo **plus a driver** (and a boost/H-bridge if piezo). Peak current here dwarfs the advertising budget and constrains the CR2032 choice. | 3.13.3 |
| Motion detector, ±10° on two axes | 3-axis accelerometer with a low-power wake-on-motion mode, sampled at 10 s / 0.5 s. | 3.13.2 |
| Serial number, readable via NFC **or** BLE | Either an NFC tag/NTAG or NFC-capable SoC (nRF52832/nRF52833 have an NFC-A tag peripheral and need two antenna pins + a coil), **or** a button + BLE `Get_Identifier`. | 3.15.2–3.15.5 |
| BLE identifier gate | A **physical button** if the identifier is served over BLE. | 3.15.3 |
| Firmware update mechanism (SHOULD) | DFU-capable bootloader; flash budget for dual-bank or an external flash. | 5 |
| Advert ≤2 s, plus a second `0xFCB2` advert set | Two interleaved advertisement sets ⇒ roughly double the radio duty cycle. | 3.4.2, 3.10 |

**That list is essentially the AirTag BOM**, which is the honest finding: the
cost gap between a $1 beacon and a $29 AirTag is not margin, it is the
anti-stalking hardware plus the sounder plus certification. Lane C/D own the BOM;
this is the requirements input.

The NFC route deserves a specific warning: DULT §3.15.5 says "The URL SHALL be
hosted by the **network provider**". For an OpenHaystack-style tag there *is* no
network provider — we would have to host the lookup endpoint ourselves, and it
would not be `find-my.googleapis.com` or Apple's. The button+BLE identifier route
avoids that dependency and is cheaper. **Recommend button+BLE over NFC for the
first board [my recommendation, flag as such].**

### 10.3 What the official Apple route would require instead

Add to §10.2: an **MFi licence** ($99/yr, company-only, **NDA**), a Find My
accessory-program enrolment, an Apple-approved implementation of the (NDA'd)
accessory protocol — pairing, Lost Mode, owner/non-owner connections, firmware
update, serial-number lookup — Bluetooth SIG qualification, per-market radio
certification, and **Apple approval of production samples before mass
production**. Precision Finding additionally requires a **U1/UWB** part, which
`GOAL.md` already excludes ("Anything in the block must be sourceable at
LCSC/JLCPCB (no Apple U1)"). The NDA alone forecloses this path for an open
design. Document it, do not plan on it.

### 10.4 Find My gives you city-scale, not room-scale — why local ranging is a separate subsystem

`GOAL.md` deliverable 3 asks the tag to tell Leif's sensors where they are
**relative to each other**. Nothing in the Find My protocol can do that, and the
numbers say why.

**Precision.** PETS 2021 Table 6, "Accuracy of OF location reports", measured
against a GPS ground truth in and around Frankfurt **[verified]**:

| Scenario | Reported accuracy value (m) | Raw report mean error (m) | After LOWESS path fit (m) |
|---|---|---|---|
| Walking | 121.9 | **81.4** | 25.9 |
| Restaurant | 117.2 | **60.2** | 27.4 |
| Train | 171.0 | **440.7** | 299.6 |
| Car | 145.2 | **580.7** | — (too sparse) |

In the paper's words: "raw reports have a mean error in the order of **100 m** for
the walking and restaurant scenarios … The raw location reports provide a decent
accuracy sufficient to **pinpoint an individual's location to a city district or
even a street**." Best case in the paper is 4.9–15.5 m, and that is only after
**clustering a week of reports** to find a repeatedly-visited top location
(§7.2, Table 7) — an offline statistical result over days, not a live position.

**Latency.** "the median time from generating to uploading a location report is
**26 min** … The delay can increase to several hours if the finder device is in a
low power mode." Plus the 15-minute key window and the four-reports-per-key cap.
A Find My position is **tens of minutes old at best.**

**Density dependence.** The report only exists if an iPhone walked past. Table 5
of the paper shows the swing: 489 reports in 55 min walking a city, versus **25
reports in 64 min** in a car. And in 2026 the DIY situation is worse — see the
issue #286 quote in §2: "*it only updates its location sporadically—unless I go to
a crowded area*". **A rack of sensors in a private workshop, a plant room, or a
field generates zero reports, forever.**

**No peer-to-peer path.** The OF advert is one-way and non-connectable; the tag
never learns anything. The finder-side upload is SEP-signed and closed. Apple
exposes **no** API that returns range, angle or peer distance from the Find My
network to a third party, and **Precision Finding (UWB ranging inside the Find My
app) is first-party only** — third-party UWB accessories go through the *Nearby
Interaction* framework, which needs the developer's own app on an iPhone in the
room and gives ranging **to that iPhone**, not between two haytags
(<https://developer.apple.com/nearby-interaction/>, fetched 2026-09-03)
**[secondary, see §6.1 caveat]** — and Apple's support page corroborates the
first-party limit even for *non-owner* finding: Find Nearby/Precision Finding is
offered only "If the unknown accessory is an AirTag or AirPods Pro 3 charging case"
(<https://support.apple.com/en-us/HT212227>, fetched 2026-09-03) **[verified]**.
Even RSSI is unhelpful: the tag has no receiver
in the OpenHaystack design, and the finder's RSSI is never returned to the owner.

**Conclusion for the architecture.** Find My answers *"which city block is this
thing on, as of about half an hour ago, if a stranger walked past."* It cannot
answer *"how far is sensor A from sensor B right now."* Those are different
problems with different radios and different error budgets — metres-to-hundreds-
of-metres and tens of minutes versus centimetres-to-decimetres and seconds. **The
relative-positioning function must be a separate subsystem on the haytag block
(peer-to-peer UWB two-way ranging, or BLE RSSI/AoA), designed to its own budget;
it shares only the enclosure, the battery and possibly the MCU.** Lane H owns
which technology. The only thing Find My contributes to it is a coarse global
anchor: it tells you *which building* the cluster is in, so a locally-solved
relative map can be pinned to a place in Twinton.

---

## 11. Open questions this lane could not close

1. **Is Apple degrading reports for unregistered `0x12 0x19` tags?** Two 2025–2026
   user reports say density dropped sharply from ~2025-09-27; no technical source
   confirms a cause. **This is the single biggest project risk.** Resolve by
   measurement, not by search: flash two tags, one in a busy street and one in the
   workshop, and log report arrival for a fortnight.
2. **Apple's DULT Network ID value.** Google's is `0x02`; Apple's is not published,
   and the draft's Finding Network Registry section is a `TODO`. A tag that is not
   on any network cannot fill this required byte honestly.
3. **Why macless-haystack rotates at 30 min when Apple rotates at 15 min.** No
   source explains it. Determines whether a 15-minute haytag is *more* or *less*
   compatible.
4. **Whether a `0xFCB2` DULT advert interleaved with an Apple `0x12 0x19` advert
   causes an iPhone to raise an unwanted-tracking alert on its own owner's tag.**
   The near-owner bit is defined in the DULT advert but the OpenHaystack path has
   no near-owner state at all. Testable with AirGuard and an iPhone.
5. **Whether any FHN (Google) tag firmware exists in the open.** I found none.
   If genuinely none exists, an open FHN tag is a bigger contribution than another
   OpenHaystack fork — Google's spec is public and DULT-aligned, which is exactly
   what `GOAL.md` wants.
6. **The Find My Network Accessory Specification R3 text.** Cited by OpenHaystack,
   no longer downloadable from Apple. Copies circulate; I did not fetch one and do
   not recommend building on a leaked NDA'd document.

---

## 12. Files this lane wrote

- `research/02-findmy-protocol-and-openhaystack.md` (this file)
- `research/fetched/B-*` — 33 archived primary sources (see `ls research/fetched/B-*`)
- appended 52 rows tagged `B` to `research/sources.tsv`
- appended 14 rows to `reference/CLONE-LIST.tsv`
