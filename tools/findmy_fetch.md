# Fetching Find My location reports for a key we advertise

Lane J, 2026-09-03. The procedure, with every step marked **TESTED**, **NOT
TESTED (no hardware)** or **NOT TESTED (needs an Apple ID we will not use)**.

**Rule for this document: no Apple ID belonging to Leif is used, asked for, or
recorded anywhere.** The fetch side of Find My requires *an* Apple account and
there is no way around that (§4). Whoever runs this creates a throwaway account
for it. Nothing here needs Leif's.

---

## 0. The shape of the problem

Find My is two halves that fail independently, and the whole point of this file
is that you can test them separately:

```
  haytag  --BLE advert-->  a stranger's iPhone  --HTTPS-->  Apple
                                                              |
  you  <--HTTPS--  gateway.icloud.com  <---------------------- +
       (authenticated as SOME Apple ID, asking by SHA256(pubkey))
```

* **Transmit half** — does a tag advertising key `p` get picked up and uploaded?
  Needs a radio that can set an arbitrary BLE address and a non-connectable
  advert. **This Mac cannot do it** (§1).
* **Fetch half** — given the private key for `p`, can you pull and decrypt the
  reports? Needs an Apple ID, an anisette provider, and FindMy.py. Testable on
  this Mac the moment an account exists.

A "my tag has no location" report from a user conflates both halves plus at
least three client-side bugs. That conflation is exactly what made the
2025-09-27 scare hard to read — see `research/10-findmy-viability-2026.md`.

---

## 1. Transmit: what will and will not work

**TESTED, 2026-09-03:** this Mac has **no USB devices at all**
(`system_profiler SPUSBDataType` and `ioreg -p IOUSB -w0 -l` both return
nothing) and no serial ports beyond the three built-ins
(`/dev/cu.Bluetooth-Incoming-Port`, `/dev/cu.debug-console`,
`/dev/cu.wlan-debug`). The only Bluetooth radio is the internal Apple
**BCM_4378 on PCIe** (firmware 23.2.545.4048).

The internal radio **cannot** be used to impersonate a tag. The Find My advert
carries the first six bytes of the public key *in the BLE advertising address*
(`addr = p[0]|0b11000000 : p[1..5]`, research/02 §1). CoreBluetooth exposes no
API to set the advertising address, and macOS has no `hcitool`/`btmgmt`
equivalent for it. A tag advertised from this Mac would carry the wrong first
six key bytes and would be undecryptable by anyone.

So the transmit half needs one of these, none of which is present:

| host | firmware | note |
|---|---|---|
| ESP32 / ESP32-C3 / ESP32-S3 dev board | `seemoo-lab/openhaystack/Firmware/ESP32` (AGPL) or `dchristl/macless-haystack` ESP32 build | cheapest; ~$5; the advert is hard-coded at build time in upstream, rolling keys need the macless-haystack build |
| nRF52832 / nRF52840 dongle or dev kit | `pix/heystack-nrf5x` (rolling keys, `MAX_KEYS` up to 500) or `acalatrava/openhaystack-firmware` (MIT) | **the right one for haytag** — same SoC family as the target (SPEC D10) |
| BBC micro:bit | `openhaystack/Firmware/Microbit_v1` | easiest to flash (drag-and-drop UF2) |
| a Linux box with a USB BLE dongle | `biemster/FindMy/HCI.py` | needs root and a dongle whose address can be changed; several 2024 reports of `bdaddr` failing per-chipset |

### Procedure for when hardware arrives — nRF52840 dongle, the recommended path

```bash
# 1. keys.  28-byte P-224 private key, base64.  Use the CSPRNG version:
#    macless-haystack's generate_keys.py used random.getrandbits() until at
#    least 2026-08 (their issue #244) — that is NOT a CSPRNG.  Prefer:
python3 - <<'EOF'
from findmy import KeyPair
k = KeyPair.new()
print("private_b64:", k.private_key_b64)
print("adv_key_b64:", k.adv_key_b64)          # this is p, the X coordinate
print("hashed_key :", k.hashed_adv_key_b64)   # SHA256(p) — what Apple indexes by
EOF

# 2. firmware
git clone https://github.com/pix/heystack-nrf5x
# put the public keys in the generated key blob per its README, set
# ADVERTISING_INTERVAL and MAX_KEYS, build with the nRF5 SDK + SoftDevice.

# 3. flash
nrfutil pkg generate --hw-version 52 --sd-req 0x00 \
    --application heystack.hex --application-version 1 dfu.zip
nrfutil dfu usb-serial -pkg dfu.zip -p /dev/cu.usbmodemXXXX

# 4. PROVE IT IS ON AIR before blaming Apple.  This is the step everyone skips.
python3 tools/findmy_scan.py --seconds 120
#    You must see a 0x12 payload with declared_len 0x19 and hint 0x00, and its
#    key_p6_p27_hex must equal bytes 6..27 of your adv key.  If you do not see
#    that, the fetch side is irrelevant — nothing is being advertised.

# 5. take it away from every Apple device you own for >30 min, into a busy
#    place, and leave it for a few hours.  Then fetch (§2).
```

**Do not skip step 4.** In `seemoo-lab/openhaystack#283` (2026-06-02)
`dennisdebel` reported "no reports found" from an ESP32 whose serial monitor
said *"advertising started"* — an unverified transmit claim. `findmy_scan.py`
turns that into a measurement.

---

## 2. Fetch: the tested-as-far-as-possible procedure

**Library: `malmeloo/FindMy.py`, MIT, v0.10.1 (2026-06-01), last push
2026-09-01.** Chosen over macless-haystack (AGPL, last release 2026-03-15)
because MIT lets us vendor it into `tools/` (DECISIONS.md D4), and because it
is the more actively maintained of the two.

```bash
# TESTED 2026-09-03 on this Mac.  A bare `pip install findmy` is REFUSED here
# (PEP 668, Homebrew Python 3.14 is externally managed).  Use a venv:
python3 -m venv .venv && .venv/bin/pip install findmy
# -> findmy 0.10.1, pulling cryptography 50.0.1, bleak 3.0.2, anisette 1.2.4,
#    srp 1.0.22, unicorn 2.1.4 (the ADI emulator local anisette runs on).
#    Build takes ~3 min on this machine because cryptography compiles.
```

**TESTED, key generation end to end:**

```
$ .venv/bin/python -c "..."
findmy version: 0.10.1
pubkey X bytes: 28
hashed_adv_key_b64: BMHXrlGgDNfMJoZWoMohRckdCloISvwmASMI/a/0DHw=
BLE addr would be : D8:E6:64:65:60:9F
advert payload    : 1E FF 4C 00 12 19 00 81FE813673B67347D96E668BB8731F7FC2D32ED1F48B 00 00
```

That payload line is what a haytag must put on air for that key, and it is
byte-for-byte the shape SPEC F1 specifies. `findmy_scan.py` will show you the
`81FE81...F48B` half; the `D8:E6:64:65:60:9F` half lives in the advertising
address and **is not visible from macOS** (§1).

### 2.1 Anisette — no longer needs a server

**This is the single biggest change since most tutorials were written.**
FindMy.py **v0.9.0 (2025-09-23)** added **local Anisette** via `Anisette.py`:
it downloads Apple's `ani_libs.bin` (the ADI provisioning library) and runs it
on-device. You no longer need `Dadoum/anisette-v3-server` in Docker.

```python
from findmy.reports import AsyncAppleAccount, LocalAnisetteProvider
anisette = LocalAnisetteProvider("ani_libs.bin")   # downloaded on first use
acc = AsyncAppleAccount(anisette)
```

**TESTED:** `from findmy.reports import LocalAnisetteProvider` imports cleanly
on this Mac. `RemoteAnisetteProvider` is the fallback and is exported beside it.

A remote server is still supported and is the fallback if the local library
segfaults (a real failure mode — `parawanderer/OpenTagViewer#135`, 2026-08-22,
"Apple's ADI library is re-initialised on every Anisette request, and can
segfault").

**NOT TESTED here:** the local provider is not exercised without an account.

### 2.2 The account

```python
await acc.login("throwaway@example.com", "hunter2")
# -> LoginState.REQUIRE_2FA
methods = await acc.get_2fa_methods()
await methods[0].request()
await methods[0].submit(input("2FA code: "))
acc.to_json("account.json")      # reuse this; do not log in every run
```

**Apple ID requirements, from the issue trackers, all NOT TESTED here:**

| requirement | evidence |
|---|---|
| The account needs a **trusted device or a trusted phone number** for 2FA. SMS delivery to some numbers silently never arrives. | `biemster/FindMy#89` (2025-10-25), `openhaystack#284` (2025-12-08), `macless-haystack#218` (2025-09-22), `#224` (17 comments, 2025-12-12) |
| A brand-new, empty Apple ID is often **refused with `Account limit reached.`** or *"your account score is not high enough. Log in to appleid.apple.com and add your credit card (nothing will be charged)"*. Reporter tried several accounts with genuine iOS devices and card details and still failed. | `macless-haystack#229` (2026-01-27, @aarontrom); same error at `FindMy.py#102` (2025-01-17, @fz6) |
| **The account does not have to own the tag.** Any Apple ID can query any key hash — Apple's fetch endpoint indexes reports by `SHA256(advertisement key)` and performs no ownership check. This is the design property the whole DIY ecosystem rests on. | `macless-haystack` README + HN 42666734 (2025-01-11): *"The process of requesting locations for a certain tag is not tied to any Apple Account … you can just use a burner account."* |
| Authentication breaks on Apple's side periodically and comes back on its own. | `FindMy.py#225` (2026-02-10) — malmeloo: *"Just recently they broke authentication for a few days (#225) and then it randomly started working again."* |

**Practical consequence for haytag:** budget for an aged Apple ID with a card
on file, created and warmed well before it is needed. A cold burner made the
day of a demo is a documented failure mode.

### 2.3 The fetch

**TESTED:** the account API in v0.10.1 is `login`, `get_2fa_methods`,
`fetch_location`, `fetch_location_history` (plus `sms_2fa_request/submit` and
`td_2fa_request/submit`). There is no `fetch_last_reports` — older tutorials
that call it are pre-0.9.

```python
from findmy import KeyPair
key = KeyPair.from_b64(PRIVATE_KEY_B64)              # our advertised key
reports = await acc.fetch_location_history(key)      # or fetch_location(key)
for r in reports:
    print(r.timestamp, r.latitude, r.longitude, r.horizontal_accuracy, r.status)
```

For a *rolling*-key haytag, do not fetch keys one at a time. Use
`FixedRollingKeyPairAccessory` (FindMy.py ≥0.10.0, added by
`fischer-martin` in PR #243, "add support for devices with a list of
pre-generated keys") and hand it the whole pre-generated key list. It
implements the same `RollingKeyPairSource` interface as a real AirTag, so the
library batches the hashes into one request and tracks alignment state.

**TESTED:** `findmy.FixedRollingKeyPairAccessory` exists in 0.10.1 with
signature `(*, private_keys: list[bytes], name: str | None = None,
identifier: str | None)` — hand it the whole pre-generated key list as raw
28-byte private keys.

### 2.4 Behaviours you must code around — every one of these is documented

1. **HTTP 200 with an empty body, intermittently.** Since ~2025-09-27, on
   `gateway.icloud.com/findmyservice/v2/fetch`. **Apple's own macOS Find My app
   hits it too** (`FindMy.py#185`, malmeloo, 2025-09-29). FindMy.py ≥0.9.3
   retries automatically. If you reimplement, retry 5× with a few seconds
   between. `FindMy.py#231` (2026-03-09) measured 5 identical requests →
   `200-empty, 401, 200-empty, 200-empty, 401`. **Do not trust the HTTP status
   code** — that issue's own conclusion.
2. **The 401s are not always real.** Same issue: re-authenticating fixed it,
   but a 401 can also just be Apple. Re-login on 401, then retry.
3. **Geography matters.** malmeloo, `FindMy.py#227` (2026-02-18): *"My best
   guess … is that one or more of their servers are faulty, and their load
   balancer is making you hit those faulty servers due to geographical
   proximity."* If it fails persistently, try from a different IP.
4. **The time window is broken server-side.** malmeloo, `#231`: *"Apple's API
   does not check the time values properly and it is essentially broken."*
   Ask for a **fixed 7–14 day window** and filter client-side. Asking for
   "the last hour" returns garbage or nothing.
5. **`datePublished` disappeared around 2026-03-13.** Reported independently at
   `biemster/FindMy#94` (2026-03-14), `FindMy.py#232` (2026-03-13, @fz6), and
   `dscao/cloud_gps#36` (2026-03-16). Fix, from lovelyelfpop 2026-03-17: fall
   back to the timestamp inside the decrypted payload —
   `report_time = decrypted['timestamp'] if report.get('datePublished') is None
   else report['datePublished']`. **A client that hard-requires `datePublished`
   crashes and looks exactly like "no reports".**
6. **The encrypted report grew from 88 to 89 bytes** at some point in 2024–25;
   the extra byte is `0x00` in every observation. `biemster/FindMy#86`; @fz6
   counted **16 000 × 88-byte and 26 000 × 89-byte reports** across his own
   fleet (2026-01-31). Accept both lengths.
7. **Historical depth is now limited.** malmeloo, `#231`: *"It's no longer
   possible to obtain very old historical data — there is a limit on how many
   reports are now stored server-side."*
8. **Rate limits exist.** `FindMy.py#183`: polling too often produced the same
   `UnhandledProtocolError`; v0.9.0 was "more aggressive in terms of making
   requests to Apple than the last one" and tripped them.
9. **A tag near its owner's Apple device is invisible to the network, by
   design.** `FindMy.py#264` (2026-08-27) is a genuine AirTag showing exactly
   the "reports stopped" symptom for this reason alone. Test tags must be
   physically separated from every Apple device on the account.

---

## 3. What to run the day hardware arrives

The measurement that settles the open question in
`research/10-findmy-viability-2026.md`:

```
two identical nRF52840 tags, same firmware, same advertising interval
  tag A: rolling keys, 15 min rotation, 96 keys/day
  tag B: one static key                       <- the control
both placed in a busy street location, >30 min from any owner Apple device
fetch every 30 min for 14 days from one throwaway Apple ID
log: reports/day, unique keys with >=1 report, median report age, p95 gap
```

Then repeat both in the workshop. Four cells. The rolling-vs-static comparison
is the one nobody in the public record has actually run, and it is the exact
mechanism malmeloo names as the cause of the "custom tags rarely update"
complaints (`FindMy.py#222`, 2026-01-28).

---

## 4. What cannot be avoided

* **You need an Apple ID.** There is no unauthenticated read path. The account
  need not own the tag, and it need not be Leif's.
* **You need Apple's `ani_libs.bin`.** Local anisette downloads Apple's own
  binary and runs it. That is a redistribution question for anything haytag
  ships; for a test rig it is fine.
* **You cannot make an iPhone report your tag.** Everything above measures; none
  of it forces. If no iPhone walks past, there is no report and no client-side
  fix exists.
