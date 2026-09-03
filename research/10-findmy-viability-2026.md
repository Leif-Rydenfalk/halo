# 10 — Is Apple's Find My network still open to an unregistered rolling-key tag in 2026?

*Lane J, 2026-09-03. The question the whole product rests on. Lane B flagged it
as "the single biggest project risk" (research/02 §11 item 1) and could not
close it. This document closes it as far as evidence allows, states exactly how
far that is, and names the one measurement that would remove the rest of the
doubt.*

**Method.** Every claim below is traced to a dated, quotable primary source —
GitHub issues and comments pulled through the GitHub REST API on 2026-09-03,
plus a 15-minute live BLE capture on this Mac. Reporters are **de-duplicated by
person, not by post**: the same individual cross-posting the same complaint to
three trackers counts once. That de-duplication turns out to be the single most
important analytical step in this document.

---

## 1. Verdict

> ### PASS, with two conditions and one unmeasured residual.
>
> **An unregistered rolling-key tag still gets located by Apple's network in
> 2026.** The "since 27 September 2025 custom tags rarely update" claim is
> **real but misattributed**: it is not Apple closing the network to
> unregistered keys. It is the superposition of four independent, separately
> documented faults, three of which are client-side and all four of which hit
> **genuine Apple AirTags too**.
>
> **Confidence: high on the negative claim** (there is no evidence Apple
> filters unregistered keys, and good structural and empirical reasons it
> cannot cheaply do so) — **medium on the positive claim** (nobody in the
> public record, and not this lane, has run the controlled experiment).
>
> **The two conditions, and they are design requirements, not caveats:**
> 1. **The tag must roll its keys.** Finder iPhones de-duplicate reports from
>    an unchanging identity. A static-key tag is reported once and then largely
>    ignored — this is the dominant cause of the complaints, and it is Apple
>    behaviour that has probably been there all along. haytag's SPEC F2 already
>    requires 15-minute rotation, so haytag is on the right side of this.
>    **Most OpenHaystack tags in the field are static-key, which is why the
>    complaint population looks the way it does.**
> 2. **The client must tolerate Apple's API misbehaving.** Empty 200s, spurious
>    401s, a broken time-window parameter, a vanished `datePublished` field and
>    an 88→89-byte report growth are all documented and all present a client
>    bug as "the network is dead". `tools/findmy_fetch.md` §2.4 lists all nine.

**What this does NOT say.** It does not say report *density* is adequate for
haytag's purposes. It is not, and never was — research/02 §10 already settled
that with the PoPETs numbers, and nothing here changes it. **Find My tells you
which city block, half an hour ago, if a stranger walked past.** For Leif's
sensor use (GOAL.md deliverable 3) that is close to useless and the answer
remains peer-to-peer ranging (DECISIONS.md D1, lane H). The Find My half of
haytag is for *finding lost things*, and for that it works.

---

## 2. Timeline

| date | event | source | failure mode |
|---|---|---|---|
| 2023-12-06 | iOS 17 breaks Find My reporting. Reports stop from *all* devices on iOS 17. | `biemster/FindMy#40`, @shiprec | (a) finder-side |
| 2024-03-18 | Confirmed to affect **genuine AirTags**: *"Regular airtag using apple findmy app gets no reports if there is no ios16 device around."* | `biemster/FindMy#40`, @Itheras | (a), **not DIY-specific** |
| 2024-03-22 | **iOS 17.4.1 fixes it.** Next day: *"Tested with 2 original AirTags, 2 official clones and several fake tags (status byte fully used, hint byte correctly set) – all fine."* | `#40`, @isibizi, @davesenior9, @humpataa | resolved after **3.5 months** |
| ~2024–25 | Encrypted report payload grows **88 → 89 bytes**; extra byte always `0x00`. | `biemster/FindMy#52`, `#86` | (d) client decode |
| 2025-09-23 | **FindMy.py v0.9.0** — "the biggest release yet". Migrates to the new `acsn` API (PR #144), new key-alignment algorithm, local anisette, breaking session format. | FindMy.py release notes | **client-side confounder** |
| 2025-09-24 | v0.9.2, "improve key alignment efficiency". | release notes | confounder |
| 2025-09-26 | @varac: AirTag returns `Last known location: None`. Cause found = key-alignment drift, not the network. Fixed by back-dating `alignment_date`. | `FindMy.py#183` | (d) client |
| **2025-09-27** | **The date everything is pinned to.** @lovelyelfpop: tags stop updating. | `biemster/FindMy#88` (2025-09-29) | claimed (a) |
| 2025-09-28 | @lovelyelfpop opens `macless-haystack#219`: *"Apple's new fetch api often returns empty string now since one or two days ago, even http status code is '200'"* — endpoint `gateway.icloud.com/findmyservice/v2/fetch`. | `#219` | **(b) fetch endpoint** |
| 2025-09-28 | Same day, **contradicted**: @fz6: *"I have a friend with an iPhone who carries one of mine, his iPhone definitely seems to report the tag repeatedly. I've also got one in my back garden that would only be in range of a couple of neighbours, whose phones reliably report it in"* | `biemster/FindMy#88` | counter-evidence |
| 2025-09-28 | @milaq: *"Works fine with 0.9.0"* — i.e. the regression tracks the **library version**, not the network. @pablobuenaposada: *"Something is off even with pre 0.9.2"*. | `FindMy.py#183` | (d) client |
| 2025-09-29 | **malmeloo (FindMy.py maintainer) opens #185 and settles the cause:** *"The FindMy app on MacOS also appears to be receiving empty responses, so it's most likely an issue on Apple's side."* | `FindMy.py#185` | **(b), and it hits Apple's own first-party app** |
| 2025-09-29 | **FindMy.py v0.9.3** ships the retry workaround. | release notes | mitigated |
| 2025-09-30 | malmeloo: *"I personally haven't experienced issues with a reduced number of location reports … The 'fix' is to just retry the request."* @merasil confirms the workaround works. | `biemster/FindMy#88` | counter-evidence |
| 2025-10-22 | @VoidMore reports rolling keys (5 min) mostly returning nothing. malmeloo: 5 min is too short, try 15–60 min; *"If your payload is correct Apple shouldn't be able to block your keys."* | `FindMy.py#197` | (a), plus a **design lesson** |
| 2025-11-03 | malmeloo: *"Apple doesn't care about what firmware you are using — as long as the bluetooth LE payload is correct, devices will accept it."* | `FindMy.py#197` | **the central negative claim** |
| 2025-11-11 / 11-20 | v0.9.5, v0.9.7 fix alignment and "no results for all but the first attempt". | release notes | (d) client |
| 2026-01-28 | @VoidMore opens `FindMy.py#222`. **malmeloo names the mechanism:** *"Apple devices do not upload every report they receive. Specifically, they tend to ignore duplicate reports from the same tag, and since (most) custom tags don't change their identity, the iPhone is probably ignoring it."* | `FindMy.py#222` | **(a), and the fix is rolling keys** |
| 2026-01-29 | @VoidMore measures it himself: *"I tested a single key pair and a derived key pair. The derived ones have slightly more reports."* | `#222` | corroborates the mechanism |
| 2026-01-31 | @fz6: *"I looked back over ~40k reports … I have 16k 88-byte reports and 26k 89 byte reports."* **Forty thousand reports on DIY tags.** | `biemster/FindMy#86` | **hard counter-evidence** |
| 2026-02-06 | @VoidMore cross-posts the same question as `openhaystack#286`. | `#286` | *same person as #222* |
| 2026-02-10→18 | Apple breaks authentication for several days, then it fixes itself. malmeloo's diagnosis: geographically-routed faulty servers. Reporter confirms recovery with no change. | `FindMy.py#227` | **(c) auth** |
| 2026-02-11 | malmeloo: *"they have introduced bugs in the past that caused tags not to be reported (including official airtags)."* | `#222` | not DIY-specific |
| 2026-03-09/10 | 5 identical requests → `200-empty, 401, 200-empty, 200-empty, 401`. Resolved by re-authenticating. Conclusion: *"not rely on HTTP response status, they're quite confused."* | `FindMy.py#231` | (b)/(c) |
| 2026-03-13→18 | Apple **removes/nulls `datePublished`**. Reported independently three times in four days. Clients crash → looks like "no reports". | `FindMy.py#232` (@fz6), `biemster#94`, `dscao/cloud_gps#36` | **(d) client decode** |
| **2026-03-17** | **The decisive one.** @lovelyelfpop — the original 2025-09-27 complainant — posts a working patch for macless-haystack's report decoder, using the timestamp *inside the decrypted report*. **He is receiving and decrypting DIY-tag location reports, six months after his own complaint.** | `dscao/cloud_gps#36` | **claimant self-refutes** |
| 2026-04-13 | @lovelyelfpop's much-quoted comment lands on `openhaystack#286` — but it is a **restatement of his September 2025 post**, not new observation. | `#286` | *same person, recycled* |
| 2026-06-02 | @dennisdebel: ESP32 says "advertising started", OpenHaystack says "no reports found". **Transmit never independently verified.** | `openhaystack#283` | unverifiable |
| 2026-08-14 | OpenTagViewer's maintainer audits adding static OpenHaystack-tag support and finds *"most of it already works — more than I expected"* in FindMy.py's current fetch path. | `OpenTagViewer#45` | ecosystem alive |
| 2026-08-27 | A **genuine Apple AirTag** shows the exact "reports stopped while Find My app updates" symptom. Cause: the tag was near its owner's device. | `FindMy.py#264` | **(e) by design, not a fault** |
| 2026-09-01 | FindMy.py last push. 3 235 stars, 28 open issues. | GitHub API | alive |

---

## 3. Evidence table

| # | claim | key source(s) | date | **independent reporters** |
|---|---|---|---|---|
| C1 | "Since 2025-09-27 custom tags' locations rarely update" | `macless-haystack#219`, `biemster#88`, `openhaystack#286` — **all @lovelyelfpop** | 2025-09-28 → 2026-04-13 | **1** |
| C2 | "Custom tag beside me only updates in a crowd" | `FindMy.py#222`, `openhaystack#286` — **both @VoidMore** | 2026-01/02 | **1** |
| C3 | Apple's fetch endpoint returns HTTP 200 with an empty body, intermittently | `#219`, `#88`, `FindMy.py#185`, `#231`, `#227` | 2025-09-28 → 2026-03 | **6+** (@lovelyelfpop, @malmeloo, @merasil, @milaq, @pablobuenaposada, @MarcoGhise, @RobinWei-dct) |
| C4 | **That endpoint fault hits Apple's own macOS Find My app** | `FindMy.py#185`, malmeloo | 2025-09-29 | 1, but it is the maintainer and it is checkable |
| C5 | Retrying the request works around it | `#88` (@malmeloo, @merasil), FindMy.py v0.9.3 ships it | 2025-09-30 | 2 + a shipped fix |
| C6 | **Finder iPhones ignore duplicate reports from an unchanging identity; rolling keys defeat this** | `FindMy.py#222` malmeloo | 2026-01-28 | 1 maintainer + 1 user replication (@VoidMore, "derived ones have slightly more reports") |
| C7 | **Apple does not filter by firmware or registration** — *"as long as the bluetooth LE payload is correct, devices will accept it"*; *"If your payload is correct Apple shouldn't be able to block your keys"* | `FindMy.py#197` malmeloo | 2025-10-24, 2025-11-03 | 1 maintainer, twice, unchallenged |
| C8 | DIY tags were producing reports **in volume** well after the claimed cutoff | `biemster#86` @fz6, 40 000 reports | 2026-01-31 | **1, quantitative** |
| C9 | DIY tags reported reliably by neighbours' phones right on the claimed cutoff date | `biemster#88` @fz6 | 2025-09-28 | 1 |
| C10 | **The original claimant was still successfully decrypting DIY reports six months later** | `dscao/cloud_gps#36` @lovelyelfpop | 2026-03-17 | 1 — *and it is C1's own author* |
| C11 | Apple has broken Find My before, for **months**, affecting **genuine AirTags**, then fixed it | `biemster#40` (iOS 17 → 17.4.1) | 2023-12 → 2024-03 | ~8 |
| C12 | A tag near its owner's Apple device is invisible to the network **by design** | `FindMy.py#264`, `OpenTagViewer#46` | 2026-06, 2026-08 | 2 + maintainer |
| C13 | FindMy.py v0.9.0 (2025-09-23) changed the fetch API and key alignment **4 days before the claimed cutoff** | FindMy.py release notes, PR #144 | 2025-09-23 | documented release |
| C14 | Apple removed the `datePublished` field ~2026-03-13, crashing naive clients | `FindMy.py#232`, `biemster#94`, `dscao/cloud_gps#36` | 2026-03-13→16 | **3** |
| C15 | Report payload grew 88 → 89 bytes; naive length checks reject the new form | `biemster#52`, `#86` | 2024–2026 | 2 |

### The population argument (negative evidence, and it is strong)

If Apple had closed the network to unregistered keys around 2025-09-27, the
DIY-tag issue trackers would be full of it. They are not.

| repo | stars | issues opened in **2026** | of which are about reports not arriving |
|---|---|---|---|
| `dchristl/macless-haystack` (the DIY-tag stack) | 2 169 | 12 | **0** — all are 2FA, Apple-ID sign-in, web UI, key format, decoder |
| `seemoo-lab/openhaystack` | 13 486 | 2 | **1** (`#286`, = @VoidMore) |
| `malmeloo/FindMy.py` | 3 235 | ~20 | **1** (`#222`, = @VoidMore, the same person) |

Two individuals, cross-posting across five threads, against zero corroborating
issues in the flagship DIY project for the whole of 2026. Lane B counted "two
2025–2026 user reports" and was exactly right; what was not visible from one
document is that both of them post everywhere, which makes the signal look
several times larger than it is.

### The structural argument

The Find My advertisement (research/02 §1, confirmed against live traffic in §4
below) contains **nothing but** a status byte, 22 bytes of an ephemeral P-224
public key, two spare key bits and a hint byte. There is no manufacturer field,
no accessory token, no registration identifier. A finder iPhone therefore
**cannot tell a registered accessory from an unregistered one** from the
advert. Filtering could only happen server-side at fetch time, keyed on
`SHA256(pubkey)` — and Apple would have to maintain a positive allow-list of
every legitimate key hash ever advertised by every certified accessory, which
is exactly the kind of central index the network's privacy design exists to
avoid. That is not proof, but it is why C7 is plausible rather than merely
asserted.

**The one lever Apple does have** is the status and hint bytes: those are
Apple-defined and a malformed value is a fingerprint. In 2024, @humpataa's
recovery test explicitly noted his fake tags had *"status byte fully used, hint
byte correctly set"*. **haytag firmware must set both correctly** — this is now
a design requirement, not a detail. Note that several OpenHaystack forks abuse
the status byte's low bits as a telemetry side channel (`dakhnod/FakeTag`,
`positive-security/send-my`); **haytag must not do that on the Find My advert.**

---

## 4. What was measured on this Mac, 2026-09-03

Tool: `tools/findmy_scan.py` (new, this lane). Host: macOS 26.6, arm64, Python
3.14.6, `bleak` over CoreBluetooth. Raw output: `out/lane-J/scan-900s.json`.

### 4.1 Does macOS filter raw manufacturer data? — **No. Measured.**

This had to be settled either way and it is settled: **CoreBluetooth delivers
Apple's own company-id 0x004C manufacturer data to a third-party process in
full, including the Find My type 0x12 payload.** A 900-second passive scan:

| | count |
|---|---|
| advertisements seen | **9 714** |
| with any manufacturer data | 8 513 |
| with Apple company id `0x004C` | **4 060** |
| distinct devices emitting `0x004C` | 174 |
| Apple type `0x12` (Find My / offline finding) adverts | **471** (31.4/min) |
| distinct devices emitting `0x12` | **69** |
| Apple type `0x16` adverts | 276, from 12 devices |
| type `0x10` Nearby Info | 1 847 |
| type `0x0C` Handoff | 886 |

### 4.2 Does macOS withhold anything? — **Yes, the BLE address. Measured.**

**All 174 devices came back as a CBPeripheral UUID; not one as a MAC address.**
This is fatal for full key recovery on macOS and must be written into the
toolchain: the Find My advert carries key bytes `p[0..5]` **in the advertising
address**, so from macOS we can recover `p[6..27]` and the top two bits of
`p[0]` — 22½ of 28 bytes — and never the rest. **Full-key verification of a
haytag on air needs a Linux/BlueZ host or an nRF sniffer.** RSSI is also
delivered as `127` (the "unavailable" sentinel) on some packets; treat 127 as
absent, not as a strong signal.

### 4.3 One real separated-state tag was captured, and our decoder handled it

```
peripheral   474C7654-7277-C3C0-0FC9-D0576230C946
seen         4 packets over 92 s, RSSI −84 … −67
raw 0x004C   12 19 6a 3ad08535e8c2f9ab4beac201f68a2b13502e4e3aae88 02 98
decoded      type       0x12  (Find My / offline finding)
             length     0x19  = 25 bytes of body — matches SPEC F1 exactly
             status     0x6a  (battery field 0b01 → "medium")
             key p[6..27] 3ad08535e8c2f9ab4beac201f68a2b13502e4e3aae88  (22 bytes)
             p[0]>>6    0x02  (= 0b10, a legal 2-bit value)
             hint       0x98
```

**This is the proof that our decode path is right against live traffic**: an
independently-emitted advert parsed into exactly the field layout SPEC F1
specifies, with the declared length, the key length and the 2-bit field all
self-consistent. The other 68 devices emitted the short near-owner form
(`12 02 <b0> <b1>`, 25 distinct status/hint combinations observed) — i.e.
iPhones and Macs that are still with their owners.

**One honest caveat on this capture:** `hint = 0x98`, not `0x00`. Per
research/02 §1 a tag emits hint `0x00` and an iDevice emits a non-zero hint
derived from the owner device's address. So the separated device we caught is
most likely **an iPhone or Mac in offline/separated state, not an AirTag**. We
did not catch an AirTag in separated state — unsurprising, since every AirTag
within range of this desk is presumably near its owner. That does not weaken
the decode proof (the payload structure is identical) but it should not be
overstated: **we have not yet observed a hint-`0x00` tag advert on this Mac.**

### 4.4 Transmit hardware — **none present. Measured.**

`system_profiler SPUSBDataType` and `ioreg -p IOUSB -w0 -l` both return
**nothing**: there are no USB devices attached to this Mac. `/dev/cu.*` holds
only the three built-ins (`Bluetooth-Incoming-Port`, `debug-console`,
`wlan-debug`). The only radio is the internal Apple **BCM_4378 on PCIe**, and
CoreBluetooth exposes no way to set the advertising address, which the Find My
advert requires. **No nRF52 dongle, no ESP32, no micro:bit. The transmit half
could not be tested and the end-to-end loop could not be closed today.** The
procedure for the day hardware arrives is written up in
`tools/findmy_fetch.md` §1 and §3.

---

## 5. The four failure modes, separated

The task asked for three; the evidence produced five. They have completely
different consequences and conflating them is what produced the scare.

| | mode | what it looks like | evidence it is real | consequence for haytag |
|---|---|---|---|---|
| **(a)** | **Finder iPhone never generates a report** | tag advertising, zero reports ever | **Real, and it has a named mechanism**: duplicate-identity suppression (C6). Also real transiently in the iOS 17 outage (C11). | **Manageable by design.** Roll keys — SPEC F2 already does, at 15 min. Do not go below ~15 min (C6/`#197`). This is the one that would kill us if it were registration-based; the evidence says it is identity-repetition-based. |
| **(b)** | **Apple's fetch endpoint refuses / returns nothing** | HTTP 200 + empty body, spurious 401 | **Real, ongoing since 2025-09-27, 6+ reporters** (C3) | **Not about us at all** — it hits Apple's own macOS app (C4). Retry, and never trust the status code. Costs us reliability engineering, not the product. |
| **(c)** | **Apple ID auth / anisette breakage** | login fails, 2FA never arrives, "Account limit reached" | **Real and recurrent**: it is the single largest category of 2026 issues in every DIY repo | Costs us an aged Apple ID with a card on file, and a retry/relogin path. See `tools/findmy_fetch.md` §2.2. |
| **(d)** | **Client decodes reports wrongly** | crash, or "0 reports" with a healthy fetch | **Real, at least 4 separate instances**: 88→89 bytes, `datePublished` removal, key-alignment drift, the v0.9.0 API migration (C13, C14, C15) | Ours to get right. Nine documented behaviours are listed in `tools/findmy_fetch.md` §2.4; a client that ignores them will report a false FAIL. |
| **(e)** | **Tag is near its owner** | "reports stopped", Find My app fine | **By design**, seen on a genuine AirTag (C12) | Every haytag experiment must physically separate the tag from every Apple device on the account, for >30 min. |

**iOS version:** claimed to matter (@lovelyelfpop blamed his iPhone 8 on iOS
16.7.11), but his own post immediately undercuts it — *"some of my friends use
iPhone 14 or iPhone with iOS 26, and the tags around them cannot update
locations either."* The one time iOS version demonstrably mattered was iOS 17
(C11), and that hit genuine AirTags too. **No usable evidence that current iOS
versions treat unregistered keys differently.**

**Registered vs unregistered accessory:** no source found that measures the
difference. The maintainer's position is that there is none at the BLE layer
(C7), the structural argument in §3 says a finder device could not implement
one, and every documented outage (C11, C12, C3/C4) hit registered AirTags as
hard as DIY tags. **CANNOT DETERMINE as a measurement; strongly indicated as an
answer.**

**Advertisement interval and key count:** no data at all in the public record.
Nobody has published a rate-vs-interval curve. `#197` gives one qualitative
data point (5-minute rotation is too fast, 15–60 min recommended) and `#222`
one directional one (rolling > static). **This is the biggest genuine gap.**

---

## 6. What would settle the residual doubt

Exactly one experiment, and it is cheap. From `tools/findmy_fetch.md` §3:

> Two identical nRF52840 tags, same firmware, same advertising interval, in a
> busy street location, >30 min from any owner Apple device.
> **Tag A: rolling keys, 15 min, 96 keys/day. Tag B: one static key (the
> control).** Fetch every 30 minutes for 14 days from one throwaway Apple ID.
> Log reports/day, fraction of keys with ≥1 report, median report age, p95 gap.
> Then repeat both in the workshop. Four cells.

That single 2×2 answers all three open sub-questions at once: whether
unregistered keys are located at all (either tag getting reports), whether
rolling beats static (the mechanism in C6), and what density looks like in a
crowd versus a private building (research/02 §10's warning, quantified for
Leif's actual site). It needs **one nRF52840 dongle, about €25, and a
throwaway Apple ID**. Nothing else in this project is blocked on so little.

Second priority, and it needs no Apple ID: **run `tools/findmy_scan.py` on a
Linux host** to confirm that the full 28-byte key including `p[0..5]` from the
advertising address matches what we generated. That closes the transmit-side
verification gap §4.2 opened.

---

## 7. If it is dead

It is not dead. But the premise deserves an answer that does not depend on
Apple's goodwill, and three of these are worth doing anyway.

### Priority 1 — **Google Find Hub, concurrently, not as a fallback**

DECISIONS.md D7 already commits haytag to broadcasting on both networks from
revision A, and lane B found **no open-source Find Hub tag firmware exists**.
This is the strongest position in the whole project and it should be treated as
a co-primary network, not a hedge.

* **What it costs us:** flash, RAM and average current for a second beacon —
  already budgeted (D8). Google's spec is public (`0xFEAA`, frame `0x40/0x41`,
  ~1024 s rotation), so no reverse engineering. Writing the first open Find Hub
  tag firmware is real work, perhaps a lane of its own.
* **What it buys us:** Android's installed base is larger than iOS's
  worldwide; a network whose tag spec Google *published* cannot be closed to us
  by the mechanism people fear from Apple; and it is a genuine first.
* **What it does not fix:** density in a private workshop is no better. Google's
  network is also crowd-sourced, and Find Hub's default aggregation settings are
  more conservative than Apple's in low-density areas.
* **Health check:** `leonboe1/GoogleFindMyTools`, 1 162 stars, last push
  2026-05-05 — alive but less active than FindMy.py.

### Priority 2 — **BLE gateways on Leif's own premises**

**This is the right answer for GOAL.md deliverable 3 regardless of what Apple
does**, and it is the cheapest thing on this list.

* **What it costs us:** an ESP32 (~€4) or a Raspberry Pi per building, running
  a passive scanner — `tools/findmy_scan.py` is already 90% of the software,
  and it works today. No Apple ID, no Google account, no cloud, no crowd.
* **What it buys us:** every haytag in the building reports to Twinton with
  seconds of latency instead of tens of minutes, with RSSI (which Find My never
  returns), and it works in a plant room where no stranger will ever walk.
* **What it does not fix:** nothing outside the buildings you own.
* **Note:** this makes the Find My and Find Hub adverts *dual-purpose* — the
  same broadcast that a stranger's phone might relay is the one our own gateway
  reads. No extra firmware.

### Priority 3 — **Our own crowd network**

* **What it costs us:** a phone app on enough phones to matter, in two app
  stores, plus a server, plus the privacy engineering to do it honestly, plus
  the DULT obligations that come with running a finding network. This is a
  company, not a feature.
* **What it buys us:** independence.
* **Verdict:** **not viable as a haytag deliverable.** The reason the Find My
  hack is valuable is precisely that a billion phones already exist. Listing it
  for completeness; it should not be planned for.

### What is *not* on the list

Paying for MFi and shipping a certified tag. It is refused on principle
(DECISIONS.md D5) — the MFi terms make the spec confidential, so reading it and
publishing the design cannot both happen.

---

## 8. Consequences for SPEC and DECISIONS

Proposed, for whoever owns those files:

1. **SPEC F2 (key rotation) is promoted from "DULT compliance" to
   "load-bearing for the product to function at all."** Evidence C6. Static-key
   operation must not be offered as a build option, even for debugging.
2. **New firmware requirement:** the Find My advert's **status byte and hint
   byte must carry Apple-conformant values**; the status byte must not be used
   as a telemetry side channel (§3, and `biemster#40` @humpataa 2024-03-23).
3. **New tooling requirement:** any haytag report client must tolerate the nine
   documented Apple API behaviours in `tools/findmy_fetch.md` §2.4 — variable
   report length, missing `datePublished`, empty 200s, spurious 401s, a broken
   time window. A client that does not is a false-negative generator.
4. **research/02 §11 item 1 is closed** by this document: PASS with conditions,
   confidence high/medium, residual named in §6.
5. **DECISIONS.md D7 (dual network) is strengthened**, not weakened, by this
   finding. Apple works, and depending on one crowd network we do not control
   is still the wrong shape.
6. **New, and it belongs in the SPEC:** an on-premises BLE gateway is the
   answer for Leif's sensor use, not Find My. research/02 §10 said the radio
   was wrong; §7 above says the *listener* is also ours to build, and it is
   nearly free.

---

## 9. Files this lane wrote

- `research/10-findmy-viability-2026.md` (this file)
- `tools/findmy_scan.py` — live Find My advertisement scanner and decoder
- `tools/findmy_fetch.md` — the tested-as-far-as-possible report-fetch procedure
- `out/lane-J/scan-900s.json`, `scan-900s.log`, `scan-smoke.json` — raw capture
- `out/lane-J/*.txt` — the archived issue threads the tables above quote
- rows tagged `J` appended to `research/sources.tsv`
