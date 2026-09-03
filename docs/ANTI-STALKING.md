# halo and unwanted tracking

**Status: DRAFT for review.** Written 2026-09-03 by research lane F. This is the project's public ethical
position and the concrete feature list that follows from it. It is not legal advice.

---

## 1. The problem, stated plainly

A Bluetooth tag that reports its location through a crowd-sourced finding network is, viewed from one
angle, a way to find your keys. Viewed from another, it is a $3 device for following a person without
their knowledge.

This is not hypothetical and it is not rare. Reporting on litigation against Apple states the company
received **more than 40,000 stalking reports between April 2021 and April 2024**, and that internal
documents acknowledged its safeguards would *"deter as opposed to prevent malicious use"*
([MacRumors, 1 May 2026](https://www.macrumors.com/2026/05/01/airtag-stalking-lawsuits-apple/)).
In *Hughes v. Apple, Inc.* (N.D. Cal., No. 3:22-cv-07668) a federal judge allowed negligence and
product-liability claims by stalking victims to proceed in March 2024
([case summary](https://www.casemine.com/judgement/us/65f67201f0af1e2dac49b1c3)); after class
certification was denied, 30+ individual suits followed.

And the specific danger of an *open, unregistered* tag is documented, publicly, with working code.
Positive Security's **"Find You"** built a stealth AirTag clone on an ESP32: ~2,000 pre-generated rotating
public keys, one beacon every 30 seconds, **no speaker at all**. It tracked a target iPhone user for
**more than five days without ever triggering an unwanted-tracking alert**
([positive.security/blog/find-you](https://positive.security/blog/find-you)). Their conclusion:

> "Since Apple in the current Find My design can't limit its usage to only genuine AirTags (and official
> partner's devices), they need to take into account the threats of custom-made, potentially malicious
> beacons."

**A halo board with no buzzer fitted and a stealth key schedule is that device.** We are not going to
pretend otherwise, and we are not going to ship it.

## 2. Our position

1. **Anti-stalking features are a product-safety requirement, at the same level as the battery door.**
   They are not a feature flag, not a "phase 2", and not optional in the reference design.
2. **The default build is the safe build.** The firmware we publish implements the IETF DULT accessory
   behaviours. There is no "silent mode", no "stealth" build target, and no documented procedure for
   disabling the sound.
3. **We publish the countermeasure alongside the tag.** The same lab that built OpenHaystack also built
   AirGuard, the free open-source tracker scanner
   ([AirGuard on F-Droid](https://f-droid.org/packages/de.seemoo.at_tracking_detection/),
   [paper](https://arxiv.org/pdf/2202.11813)). We link it from our README and our documentation, and we
   tell buyers how to scan for unwanted trackers.
4. **We will not merge stealth patches.** Pull requests that remove the sound-maker, suppress the
   separated-state alert, add faster-than-DULT key cycling, or otherwise defeat platform detection will be
   closed. This is stated in `CONTRIBUTING.md` as a hard rule, not a preference.
5. **We are honest about the limits.** A determined attacker with a soldering iron can defeat any of this
   — that is true of AirTag too; Adam Catley's teardown shows the AirTag voice coil *"can be disconnected
   without disassembly"* and the tag then *"operates as normal"*, silently
   ([adamcatley.com/AirTag](https://adamcatley.com/AirTag.html)). Our claim is not that halo cannot be
   abused. It is that **halo will not make abuse easy, will not document it, and will not ship it as a
   default.**
6. **Owner privacy and target safety are weighed equally.** This is the DULT threat model's own principle:
   *"Avoid privacy compromises for Tag Owner(s) when protecting against Unwanted Tracking. The privacy of
   Tag Owner(s) and the security of Targets should be considered equally."*
   (draft-ietf-dult-threat-model-05, §4)

## 3. The standard we implement

The IETF **Detecting Unwanted Location Trackers (DULT)** working group is the joint Apple/Google effort to
standardise cross-platform tracker detection
([Apple, May 2023](https://www.apple.com/newsroom/2023/05/apple-google-partner-on-an-industry-specification-to-address-unwanted-tracking/);
[Apple, May 2024](https://www.apple.com/newsroom/2024/05/apple-and-google-deliver-support-for-unwanted-tracking-alerts-in-ios-and-android/)).
Since iOS 17.5 and Android 6.0+, phones raise "[Item] Found Moving With You" alerts for any DULT-compatible
tracker, regardless of which platform it is paired with
([Apple Support: Detect unwanted trackers](https://support.apple.com/guide/personal-safety/detect-unwanted-trackers-ips139b15fd9/web)).

Status as of 2026-09-03 ([datatracker DULT documents](https://datatracker.ietf.org/wg/dult/documents/)):

| Document | Rev | Date | State |
|---|---|---|---|
| `draft-ietf-dult-accessory-protocol` | 00 | 2024-11-03 | Expired I-D (still the operative accessory spec) |
| `draft-ietf-dult-threat-model` | 05 | 2026-08-06 | Active I-D |
| `draft-ietf-dult-finding` | 01 | 2025-06-06 | Expired I-D |

**There is no RFC yet.** We pin our implementation to `draft-ietf-dult-accessory-protocol-00` by name and
revision, and we will re-review when a successor revision or an RFC appears. Full text is archived in this
repo at `research/fetched/F-dult-accessory-protocol-00.md`.

## 4. What halo will implement

Each item cites the section of `draft-ietf-dult-accessory-protocol-00` it comes from.

### 4.1 Hardware that anti-stalking requires (non-negotiable BOM items)

| Item | Why | DULT § |
|---|---|---|
| **Sound maker** (magnetic buzzer or piezo), **≥ 60 Phon peak loudness (ISO 532-1:2017)** | *"MUST include a sound maker (for example, a speaker) to play sound when in separated state"* | 3.13.3 |
| **Motion sensor** (accelerometer) | Separated-state alerting is motion-triggered; without it the tag cannot alert correctly | 3.13.2.1 |
| **Printed serial number** on the shell/label, unique per product ID | *"The serial number MUST be unique for each product ID"*; *"SHALL be printed and be easily accessible on the accessory"* | 3.15.1 |
| **A physical button** (or an NFC tag) for identifier retrieval | The identifier must be readable by a finder, gated by a deliberate physical action | 3.15.2–3.15.3 |

The buzzer is **not** a DNP option, **not** a solder-jumper, and **not** a "premium variant" part. A halo
without it is not a halo.

### 4.2 Firmware behaviour

| Behaviour | Specification | DULT § |
|---|---|---|
| State machine | Near-owner → separated after **> 30 minutes** apart; back to near-owner on reunification | 3.4.4–3.4.5 |
| Near-owner bit | Set to 1 near owner, 0 when separated, in the advertisement | 3.9 |
| Key/MAC rotation | **15 min** near-owner, **24 h** separated, **and on every state transition** — never faster, never per-beacon | 3.5.1 |
| Advertising interval | ≤ 4 s, target ≤ 2 s | 3.10 |
| Unwanted-tracking alert | After a **random 8–24 h** separated timeout, enable motion detection at 10 s sampling; on motion drop to 0.5 s; play sound; stop after **10 plays or 20 s** of motion; then back off **6 h** and repeat | 3.13.2.1, Table 17 |
| Sound duration | 5 s min / 30 s max, **12 s** target | 3.13.4.1 |
| Non-owner sound control | Implement `Sound_Start (0x0300)`, `Sound_Stop (0x0301)`, `Command_Response (0x0302)`, `Sound_Completed (0x0303)` — all REQUIRED. Available **only in the separated state**, so any stranger's phone can make a suspicious tag beep | 3.13.4, Table 18 |
| DULT GATT | Non-owner service `15190001-12F4-C226-88ED-2AC5579F2A85`, characteristic `8E0C0001-1D68-FB92-BF61-48377421680E` | 3.11 |
| Detection payload | Service Data TLV type `0x16` with 16-bit UUID **`0xFCB2`**, network ID byte, near-owner bit, so platform detectors can see us | 3.4.2, 3.6 |
| Identifier retrieval | `Get_Identifier` enabled by a physical action, read window **5 minutes**; paired-state payload **encrypted** | 3.15.3–3.15.4 |

### 4.3 Owner information / "I found this tag" path

- A lost-mode URL following the DULT NFC/identifier format
  `https://{URL}?pid=%04x&b=%02x&fv=%08x&e=%s` (§3.15.5), reachable by anyone who finds the tag.
- An owner-information page showing **obfuscated** contact details only — DULT §3.16.1 requires at least
  one of: the **last four digits of the owner's phone number**, or an **email address with the first
  letter of the username and the domain visible**. Never the full contact.
- DULT §3.16.2 sets a **25-day minimum** retention for owner registry data after disassociation. If halo
  ever operates such a registry it is a GDPR controller: publish a privacy notice, keep the retention at
  the DULT floor and no longer, and document the lawful basis. **Preferred design: no project-operated
  registry at all — a static instruction page plus the printed serial, with owner contact under the
  owner's own control.**

### 4.4 Documentation duties

- A prominent "If you think a halo is following you" section in the README and on any product page:
  how to find it, how to make it beep, how to disable it (remove the CR2032), and where to get help.
- Links to platform detection: [Apple's Detect unwanted trackers](https://support.apple.com/guide/personal-safety/detect-unwanted-trackers-ips139b15fd9/web),
  [Android's Find unknown trackers](https://support.google.com/android/answer/13658562), and
  [AirGuard](https://f-droid.org/packages/de.seemoo.at_tracking_detection/) for passive background scanning.
- A pointer to victim support resources (e.g. the National Network to End Domestic Violence's Safety Net
  project in the US, and equivalent national services), included on the "found a tag" page rather than
  buried in the repo.
- The `CONTRIBUTING.md` rule from §2.4 above, stated as policy.

## 5. What halo will not do

- No stealth firmware, no silent build target, no sound-suppression configuration option.
- No key schedule faster than the DULT rotation intervals, and no "fresh key per advertisement" mode.
- No documentation, tutorial, blog post or issue reply explaining how to defeat unwanted-tracking alerts.
  Requests for that will be closed and, where they describe intent to track a person, reported.
- No shell design that hides the buzzer port or damps the sound.
- No claim of Apple certification, no "Works with Apple Find My" badge (that badge is licensed through
  Apple's MFi Program and is not available to this project), and no implication of Apple endorsement.

## 6. Known gaps we are honest about

- **We cannot make a tag that a determined attacker cannot silence.** Cutting a buzzer trace takes
  seconds. AirTag has the same weakness. Our answer is detection: the DULT advertisement makes the tag
  visible to every iOS 17.5+ and Android 6.0+ phone whether or not it can beep.
- **The DULT accessory protocol draft has expired without an RFC.** We track the working group and will
  update. Pinning to a named revision is our mitigation.
- **Rotating keys are inherently hard to detect.** The DULT threat model concedes this: *"While it is not
  possible to limit the deployment of nonconformant Tags, a successful protocol would minimize the ability
  of nonconformant Tags to access the crowdsourced network"* (draft-05, §4.1.4). We conform so that
  detection works on us.
- **This document is a draft.** Review it, argue with it, and improve it — but the direction is settled:
  if we ship the tag, we ship the safety features.

---

### Sources

- draft-ietf-dult-accessory-protocol-00 — https://www.ietf.org/archive/id/draft-ietf-dult-accessory-protocol-00.html (archived in this repo at `research/fetched/F-dult-accessory-protocol-00.md`)
- draft-ietf-dult-threat-model-05 — https://www.ietf.org/archive/id/draft-ietf-dult-threat-model-05.html (`research/fetched/F-dult-threat-model-05.md`)
- IETF DULT working group documents — https://datatracker.ietf.org/wg/dult/documents/
- Apple Newsroom, "Apple, Google partner on an industry specification to address unwanted tracking", May 2023 — https://www.apple.com/newsroom/2023/05/apple-google-partner-on-an-industry-specification-to-address-unwanted-tracking/
- Apple Newsroom, "Apple and Google deliver support for unwanted tracking alerts in iOS and Android", 13 May 2024 — https://www.apple.com/newsroom/2024/05/apple-and-google-deliver-support-for-unwanted-tracking-alerts-in-ios-and-android/
- Apple Support, "Detect unwanted trackers" — https://support.apple.com/guide/personal-safety/detect-unwanted-trackers-ips139b15fd9/web
- Positive Security, "Find You: Building a stealth AirTag clone" — https://positive.security/blog/find-you
- Adam Catley, "Apple AirTag Reverse Engineering" — https://adamcatley.com/AirTag.html
- AirGuard (SEEMOO, TU Darmstadt) — https://f-droid.org/packages/de.seemoo.at_tracking_detection/ and https://arxiv.org/pdf/2202.11813
- Hughes v. Apple, Inc., N.D. Cal. No. 3:22-cv-07668 — https://www.casemine.com/judgement/us/65f67201f0af1e2dac49b1c3
- MacRumors, "Apple Faces Dozens of Lawsuits Over AirTag Stalking After Class Action Denied", 1 May 2026 — https://www.macrumors.com/2026/05/01/airtag-stalking-lawsuits-apple/

All links fetched 2026-09-03. Detailed legal/regulatory background: `research/06-legal-ip-certification-safety.md`.
