# 06 — Legal, IP, certification, safety and anti-abuse constraints on an open AirTag-compatible tracker

**Research lane F.** Compiled 2026-09-03. All fetch dates are 2026-09-03 unless stated.

> **This is research, not legal advice.** Nothing here is a legal opinion and no lawyer wrote it. It is a
> literature review of primary sources (statutes, regulations, standards, patents, licence texts, vendor
> terms) assembled so that the haytag design team can ask a qualified lawyer the *right* questions before
> publishing or selling anything. Every factual claim below carries a link and a fetch date; where the
> exact wording matters, a short quote is included. Where a source could not be verified, that is stated
> explicitly rather than papered over.

Related lanes: A (teardown/reverse engineering), B (OpenHaystack / macless-haystack firmware ecosystem).
Full-text copies of the most important primary documents are in `research/fetched/F-*.md`.

---

## 0. Executive summary — the five things that actually bind this project

1. **Naming**: `AirTag` and `Find My` are registered Apple trademarks. The project may say it is
   *compatible with* Apple's Find My network in a referential phrase; it may not use those marks, or
   takeoffs of them, in its own name. That is why the repo is `haytag` (from *Haystack*), not `*airtag`.
   The **"Works with Apple Find My" badge is a licensed MFi badge** and is unavailable to an unlicensed
   project. See §1.
2. **The spec is under NDA**: the Find My Network Accessory Interface Specification is distributed only
   through the MFi Program ($99/yr membership) under an Apple NDA, and is "Apple Confidential". An open
   repo therefore must build on the **published academic reverse engineering** (OpenHaystack / PETS 2021),
   not on the MFi spec. See §3.
3. **Anti-stalking is the ethical crux, not a nice-to-have**: an unregistered, speaker-less, rotating-key
   beacon is *precisely* the "Find You" stalking device that security researchers built to demonstrate the
   hole in Apple's protections. The IETF DULT drafts define what a non-abusive accessory must do. haytag
   must implement the DULT accessory behaviours even though it cannot be MFi-certified. See §4 and
   `docs/ANTI-STALKING.md`.
4. **Radio certification is affordable only via a pre-certified module**: a Nordic nRF52-based module
   from Fanstel/Raytac/Minew carries an FCC ID, a CE/RED file and often a Giteki number; a bare nRF52 die
   on your own PCB does not, and full intentional-radiator certification runs into five figures. See §5.
5. **CR2032 + US market = Reese's Law**: 16 CFR part 1263 has applied to *consumer products containing
   button cells* manufactured or imported after 19 March 2024. A snap-fit or friction 3D-printed shell
   almost certainly fails it. Design the battery door for tool-or-two-independent-simultaneous-motions
   from day one. See §6.

---

## 1. Trademark — what an open project may and may not say

### 1.1 The marks

Apple's public trademark list includes both marks with their required generic terms:

| Mark | Generic term Apple specifies |
|---|---|
| AirTag® | accessories |
| Find My® | software feature |

Source: [Apple Legal — Trademark List](https://www.apple.com/legal/intellectual-property/trademark/appletmlist.html), fetched 2026-09-03.
The list also warns it is not exhaustive: *"The absence of a product or service name or logo from this
list does not constitute a waiver of Apple's trademark or other intellectual property rights concerning
that name or logo."* `APPLE AIRTAG` is additionally a filed US registration (USPTO serial 97086499,
[uspto.report/TM/97086499](https://uspto.report/TM/97086499), fetched 2026-09-03).

### 1.2 Apple's rules for third parties

From [Guidelines for Using Apple Trademarks and Copyrights](https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html) (fetched 2026-09-03), verbatim:

- Referential use is allowed: developers may use an Apple word mark *"in a referential phrase such as
  'runs on,' 'for use with,' 'for,' or 'compatible with.'"* — but **not** the Apple logo or any Apple
  graphic symbol.
- Takeoffs are forbidden: *"Third parties cannot use a variation, phonetic equivalent, foreign language
  equivalent, takeoff, or abbreviation of an Apple trademark for any purpose."* The guideline's own
  examples of unacceptable uses are `Appletree`, `Jackintosh`, `Apple Cart`, `iPodMart`.
- Names are forbidden: *"You may not use or register, in whole or in part, Apple, iPod, iTunes, Macintosh,
  iMac, or any other Apple trademark … as or as part of a company name, trade name, product name, or
  service name except as specifically noted in these guidelines."*
- Domains are forbidden: *"You may not use an identical or virtually identical Apple trademark as a second
  level domain name."*

### 1.3 The "Works with Apple Find My" badge is licensed, not free

Approved accessories can carry a **"Works with Apple Find My"** badge; the badge artwork, its size and
placement rules and the required compatibility language come from Apple and require the product to be
certified through the MFi Program
([Apple Newsroom, 7 Apr 2021](https://www.apple.com/newsroom/2021/04/apples-find-my-network-now-offers-new-third-party-finding-experiences/), fetched 2026-09-03;
badge guidelines document circulating publicly as *"Works with Apple Find My Identity Guidelines"*,
[copy on Scribd](https://es.scribd.com/document/691416525/Works-with-Apple-Find-My-Identity-Guidelines-March), fetched 2026-09-03 — treat that copy as unverified).
**haytag cannot use this badge.**

### 1.4 Nominative fair use — the doctrine that permits "compatible with"

US law recognises nominative fair use, formulated in *New Kids on the Block v. News America Publishing*
(9th Cir. 1992): the mark may be used where (1) the product cannot be readily identified without it,
(2) only so much of the mark is used as is reasonably necessary, and (3) nothing suggests sponsorship or
endorsement ([INTA fact sheet on fair use](https://www.inta.org/fact-sheets/fair-use-of-trademarks-intended-for-a-non-legal-audience/), fetched 2026-09-03;
[Wikipedia, Nominative use](https://en.wikipedia.org/wiki/Nominative_use), fetched 2026-09-03). The EU
analogue is the "honest practices" limitation on trade mark effects. In the EU the equivalent framing is
that use must be *"necessary to indicate the intended purpose of the product"* and *"made in accordance
with honest commercial practices"* ([WTR, using a third-party mark without infringing](https://www.worldtrademarkreview.com/article/united-states-how-use-third-party-mark-without-infringing), fetched 2026-09-03).

### 1.5 Why the repo is `haytag`

- `airtag`, `air-tag`, `AirTagClone`, `OpenAirTag` etc. are *takeoffs/abbreviations of an Apple mark used
  as part of a product name* — squarely inside the prohibition quoted in §1.2.
- `haytag` derives from **OpenHaystack** (TU Darmstadt, §3.3), which is itself a pun on *needle in a
  haystack*. It contains no Apple mark, no phonetic equivalent of one, and no Apple-owned graphic.
- The precedent set by the upstream ecosystem is the same: `OpenHaystack`, `macless-haystack`,
  `findmy.py` — none of them uses `AirTag` in the project name, and OpenHaystack's README carries an
  explicit disclaimer: *"OpenHaystack is not affiliated with or endorsed by Apple Inc."*
  ([seemoo-lab/openhaystack README](https://github.com/seemoo-lab/openhaystack), fetched via lane B).

**Practical naming rules for this repo** (research recommendation, not legal advice):
- Project name: `haytag`. Never `AirTag`-anything, never `iTag`, never an Apple logo.
- Permitted descriptive line: *"haytag is an open-source Bluetooth LE tag compatible with Apple's Find My
  network. haytag is not affiliated with, authorised, sponsored or endorsed by Apple Inc. Apple, AirTag
  and Find My are trademarks of Apple Inc."*
- Do **not** use the "Works with Apple Find My" badge or any Apple artwork, and do not imply certification.
- Do not register a domain containing `airtag` or `findmy`.
- Do not use the Bluetooth® word mark or logo unless the Bluetooth qualification/listing has been done (§5.4).

---

## 2. Patents — what exists, and what an open-hardware project's exposure actually looks like

> Patent counts and claim scope below come from Google Patents / USPTO records. No freedom-to-operate
> opinion is offered or implied; only a lawyer can give one, and an FTO search is a paid professional
> exercise, not a web crawl.

### 2.1 Apple patents on the crowd-sourced finding system

| Patent | Title | Assignee | Priority | Granted | Anticipated expiry | Why it matters |
|---|---|---|---|---|---|---|
| [US 9,479,920 B1](https://patents.google.com/patent/US9479920B1/en) | Power management in crowd-sourced lost-and-found service | Apple Inc | 2015-09-30 | 2016-10-25 | 2035-09-30 | The original crowd-sourced BLE-tag lost-and-found patent; spec expressly says *"the first signal source can be a Bluetooth low energy (BLE) tag"* |
| [US 11,889,302 B2](https://patents.google.com/patent/US11889302B2/en) | Maintenance of wireless devices | Apple Inc | 2020-08-28 | 2024-01-30 | ~2041-02-05 | Claims cover setting a **maintenance/near-owner status indicator in the advertisement packet** and **transitioning between broadcast modes on a timeout** — i.e. exactly the near-owner ↔ separated state machine a Find My accessory implements |
| [US 11,736,938 B2](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11736938) | Maintenance of wireless devices | Apple Inc | (same family) | 2023 | — | Same family as above |
| [US 12,073,705 B2](https://patents.google.com/patent/US12073705B2/en) | Separation alerts for notification while traveling | Apple Inc | 2021-05-07 | 2024-08-27 | — | Owner-side separation notifications |
| [US 12,495,353](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12495353) | Non-waking maintenance of near owner state | Apple Inc | — | — | — | Near-owner state maintenance without waking the owner device |
| [US 12,170,892](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12170892), [US 12,262,278](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12262278), [US 12,550,214](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12550214) | Maintenance of wireless devices by electronic devices / Proximity enhanced location query / Pairing groups of accessories | Apple Inc | — | — | — | Surrounding family: finder devices encrypting location data to a public key supplied in the beacon and reporting to a device-locator server |

All fetched 2026-09-03. The `Maintenance of wireless devices` family is the one most directly on point for
firmware: US 11,889,302's abstract describes *"the presence of a wireless device and/or accessory that
cannot maintain an independent network connection can be detected by network connected wireless devices
and the location of the detected device and/or accessory can be reported to a device location service."*

Notably, Apple's own patents are drawn to the *system* (accessory + finder phone + server). A bare
accessory that only advertises is a component of that system; whether a component supplier infringes a
system claim, and whether an unsold open-source design is an infringing "offer for sale", are exactly the
questions to put to counsel — not to a researcher.

### 2.2 Physical design: the speaker-driving-the-shell and the battery door

- **Speaker**: AirTag has no discrete speaker. Adam Catley's teardown records: *"The voice coil is glued
  to the outer plastic shell which acts as a diaphragm. Due to the fixed magnet, it moves back and forth
  when the coil is energised, producing sound to act as the speaker."*
  ([adamcatley.com/AirTag](https://adamcatley.com/AirTag.html), copy at `research/fetched/A-catley-airtag-reverse-engineering.md`).
  Also documented in the [iFixit AirTag teardown](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks) and the
  [9to5Mac teardown writeup](https://9to5mac.com/2021/04/30/airtag-teardown-speaker-design-more/) (both fetched 2026-09-03).
  **I could not verify a specific granted Apple patent covering "voice coil bonded to the enclosure shell
  as diaphragm" in this research pass.** Searches surfaced generic voice-coil/diaphragm patents from other
  assignees and Apple audio patents not tied to a tracking tag. Treat "Apple has a patent on the
  shell-as-diaphragm speaker" as **UNVERIFIED**; it should be checked by a patent attorney in a proper FTO
  search before haytag copies that construction. A conventional magnetic buzzer/piezo avoids the question
  entirely and is cheaper to source.
- **Battery door**: the AirTag door is a quarter-turn twist-lock. The patents surfaced by search for
  quarter-turn tracking-device housings — [US 12,393,817 B1](https://patents.google.com/patent/US12393817B1/en),
  [US 12,106,167 B1](https://patents.google.com/patent/US12106167B1/en), US 12,406,166 — are assigned to
  **Elevation Lab Inc**, not Apple, and cover aftermarket *housings that receive an AirTag* (fetched
  2026-09-03). So: the third-party accessory space around the battery door is patented, but I found no
  Apple patent asserting the twist door itself. **UNVERIFIED / no Apple patent located.** Note that
  quarter-turn bayonet closures are ancient prior art in general; the design freedom question is about
  ornamental design rights (below), not utility.
- **Ornamental design**: Apple holds design patents on the AirTag form factor, e.g.
  [USD958677 S1 "Electronic device"](https://patents.google.com/patent/USD958677S1/en) — Apple Inc, filed
  2020-02-27, granted 2022-07-26, term to ~2037, claim: *"The ornamental design for an electronic device,
  as shown and described"* (fetched 2026-09-03). **Design rights are about appearance.** The clean
  consequence for haytag: do not copy the AirTag's *look* — the polished-dome white shell, the exact disc
  proportions, the stainless mirror back. Function may be reimplemented; appearance should be
  deliberately, visibly different. Apple also holds an EU/registered-design portfolio in most markets
  (not enumerated here).

### 2.3 UWB / Precision Finding

Apple's Precision Finding uses the U1/U2 UWB radio to give distance-and-direction guidance in the Find My
UI ([Apple developer docs on Nearby Interaction direction finding](https://developer.apple.com/documentation/nearbyinteraction/extending-advanced-direction-finding-and-ranging), fetched 2026-09-03).
The published AirTag pre-announcement filings are the *Multi-Interface Transponder Device* pair
("Altering Power Modes" and "Power Management"), filed Feb 2019 from Apple's UK office, inventors James H.
Foster, Marlene Nilsen, Paul G. Puskarich, describing *"UWB, Bluetooth/Bluetooth LE, and LP/ULP"* support
and optional *"signaling hardware like lights, speakers and vibratory modules"*
([AppleInsider, 27 Aug 2020](https://appleinsider.com/articles/20/08/27/apples-smart-airtags-tracking-device-outlined-in-patent-filing), fetched 2026-09-03;
[MacRumors, 22 Oct 2020](https://www.macrumors.com/2020/10/22/apples-airtags-revealed-in-newly-published-patents/), fetched 2026-09-03).
**Practical consequence**: UWB in an open tag is (a) unreachable anyway because the Find My UWB pairing
handshake lives inside the NDA'd MFi spec, (b) an extra certification burden (§5.5), and (c) the densest
patent thicket in the product. *Recommendation: haytag ships BLE-only.*

### 2.4 Patents on the Find My protocol itself — and the anti-stalking side

- The rolling-key / encrypted-report design is covered by the Apple family in §2.1 and was independently
  *documented* (not licensed) by the TU Darmstadt reverse engineering (§3.3).
- Anti-stalking detection is itself patented, and not only by Apple: **[US 12,126,992 B2 "Unauthorized
  tracking device detection and prevention"](https://patents.google.com/patent/US12126992B2/en) is assigned
  to Tile Inc**, priority 2021-07-13, granted 2024-10-22, expiry ~2042 (fetched 2026-09-03). It reads on a
  phone detecting an unknown BLE device following a user, including *"complex identifier devices that
  periodically rotate their identity information to avoid detection."* That is platform-side, not
  accessory-side, so it is unlikely to bear on a tag, but it shows the space is enclosed.
- Litigation datapoint: *MuTag Tracking v. Apple* (AirTag patent suit) was dismissed with prejudice
  ([PatSnap case note](https://www.patsnap.com/resources/blog/litigation/mutag-tracking-v-apple-airtag-patent-dismissed-with-prejudice-patsnap/), fetched 2026-09-03).

### 2.5 How the OpenHaystack academics handled it, and what the exposure profile is

- The TU Darmstadt SEEMOO group **published the reverse engineering as peer-reviewed research**:
  Heinrich, Stute, Kornhuber, Hollick, *"Who Can Find My Devices? Security and Privacy of Apple's
  Crowd-Sourced Bluetooth Location Tracking System"*, PoPETs 2021
  ([arXiv:2103.02282](https://arxiv.org/abs/2103.02282);
  [PoPETs PDF](https://petsymposium.org/popets/2021/popets-2021-0045.pdf), fetched 2026-09-03), plus a
  WiSec'21 demo paper. They went through **responsible disclosure** first — one flaw was fixed by Apple as
  [CVE-2020-9986](https://support.apple.com/en-us/HT211849).
- They released the tooling as **research software with an explicit disclaimer**, AGPL-3.0 licensed, and
  stated plainly that it is *"experimental software. The code is untested and incomplete"* and *"not
  affiliated with or endorsed by Apple Inc."*
- They did **not** ask for or obtain a patent licence, and they did **not** sell hardware. The distinction
  that matters in practice is between (i) *publishing a design and research findings* — protected speech
  in most Western jurisdictions, and in the US supported by the DMCA §1201(f) interoperability carve-out
  for reverse engineering *"for the sole purpose of identifying and analyzing those elements of the
  program that are necessary to achieve interoperability of an independently created computer program"*
  ([EFF Coders' Rights Reverse Engineering FAQ](https://www.eff.org/issues/coders/reverse-engineering-faq), fetched 2026-09-03),
  and in the EU by Art. 6 of the Software Directive's decompilation-for-interoperability right
  ([EU reverse-engineering boundaries summary](https://vidstromlabs.com/blog/the-legal-boundaries-of-reverse-engineering-in-the-eu/), fetched 2026-09-03) —
  and (ii) *making, using, offering for sale or selling* a product, which is the conduct patents actually
  prohibit.
- Consequence for haytag: **publishing KiCad + firmware + docs has a materially different risk profile
  from selling assembled units.** A commercial vendor selling Find-My-compatible tags without an MFi
  licence is described in secondary commentary as operating *"in legal limbo"*
  ([discussion of macless-haystack commercial derivatives](https://www.blog.brightcoding.dev/2026/02/18/macless-haystack-build-diy-airtags-without-a-mac), fetched 2026-09-03) —
  a weak source, flagged as such, but consistent with the structural analysis above.

---

## 3. Apple's Find My Network Accessory Program — the actual terms

### 3.1 It is MFi, not a separate programme

Apple's developer page is unambiguous: *"Whether you're a developer or manufacturer looking to connect an
existing or new accessory to the Find My network, enroll in the MFi Program to access the technical
specifications and resources needed to create your product."*
([developer.apple.com/find-my](https://developer.apple.com/find-my/), fetched 2026-09-03).
Nordic Semiconductor, an MFi licensee shipping a Find My sample in nRF Connect SDK for nRF54L15 /
nRF52840 / nRF52833 / nRF52832, states it as a hard gate: *"You will need to have an active MFi licence to
be granted access"* to the Find My SDK ([nordicsemi.com Apple Find My network](https://www.nordicsemi.com/Products/Technologies/Apple-Find-My-network), fetched 2026-09-03).

### 3.2 Cost, NDA and confidentiality

From the [MFi Program FAQs](https://mfi.apple.com/en/faqs.html) and
[MFi enrolment page](https://mfi.apple.com/en/help/login-help/MFi-Enrollment) (both fetched 2026-09-03):

- **Fee**: *"The MFi Program is USD $99 (plus any applicable taxes and fees) per membership year."*
- **Who may enrol**: *"Companies, organizations, government entities and educational institutions."*
  Individuals building accessories purely for personal use do not need to join.
- **NDA**: applicants *"Execute an online NDA"*; the authorised-manufacturers list and the royalty
  schedule are available *"only … under NDA."*
- **Confidentiality of the spec**: *"The information shared under the MFi Program is Apple Confidential
  and is not intended to be used in an academic setting."*
- Beyond the $99, enrolled members are subject to a confidential fee schedule (per-product royalties,
  per-unit authentication-coprocessor costs). A publicly-circulating copy of an MFi contract
  ([MFiContract v7.0 PDF mirrored by a third party](https://www.bse-electronic.com/wp-content/uploads/2024/06/MFiContractv77.0.pdf), fetched 2026-09-03)
  states that termination of the Use Licence *does not* terminate the enrolment confidentiality
  agreement, which *"shall survive and remain in effect independent of the Use License."* Treat that
  mirrored PDF as unverified but indicative.

**The structural bind for an open project**: enrolling in MFi to read the spec creates a confidentiality
obligation that is *incompatible with publishing an implementation of that spec*. An open project must
therefore stay **outside** MFi and work only from published research. Anyone on the haytag team who has
ever signed an Apple NDA should stay away from the protocol implementation to avoid contamination
(clean-room hygiene). Copies of the *Find My Network Accessory Specification – Developer Preview – Release
R3* circulate on document-mirror sites; **do not use them** — they are Apple Confidential material and
using them destroys the clean-room posture. (OpenHaystack's own reference list cites the R3 spec via
Apple's developer download page, not a mirror.)

### 3.3 What "unregistered" OpenHaystack-style keys mean in practice

Mechanics, from the [OpenHaystack README](https://github.com/seemoo-lab/openhaystack) (fetched via lane B,
copy at `research/fetched/B-openhaystack-README.md`) and the PoPETs paper:

- A P-224 key pair is generated on the owner's machine; the public key goes into the BLE advertisement.
- *"Nearby iPhones will not be able to distinguish our accessories from a genuine Apple device or
  certified accessory."*
- *"Apple does not know which encrypted locations belong to which Apple account or device. Therefore,
  every Apple user can download any location report as long as they know the corresponding public key."*
- *"Apple protects their database against arbitrary access by requiring an authenticated Apple user to
  download location reports."* OpenHaystack originally obtained that authentication by installing an
  **Apple Mail plugin running with elevated entitlements** and requiring the user to
  `sudo spctl --master-disable` (disable Gatekeeper).

Legal touchpoints, each of which is a question for counsel rather than a settled answer:

- **Fetching reports needs an Apple ID.** The iCloud Terms of Service prohibit, under *V.B Your Conduct*,
  *"interfere with or disrupt the Service (including accessing the Service through any automated means,
  like scripts or web crawlers), or any servers or networks"*, and under *VI Software* state that use of
  the software or Service *"EXCEPT FOR USE OF THE SERVICE AS PERMITTED IN THIS AGREEMENT, IS STRICTLY
  PROHIBITED"* ([iCloud Terms & Conditions](https://www.apple.com/legal/internet-services/icloud/en/terms.html), fetched 2026-09-03).
  A tool that automates report retrieval through Apple's private endpoints is in obvious tension with
  those clauses. The realistic downside is **account-level enforcement (Apple ID suspension), not a
  lawsuit** — but the project should say so honestly to users.
- **Modern practice has moved off the Mail-plugin hack**: `macless-haystack` and `findmy.py` authenticate
  as an Apple account directly (see lane B). That removes the Gatekeeper-disabling step but not the ToS
  question.
- **Detection**: since iOS 14.5 an iPhone raises *"unknown accessory detected"* style unwanted-tracking
  notifications for AirTags and Find My accessories, and since **iOS 17.5** for any tracker compatible
  with the DULT industry specification
  ([Apple Support, Detect unwanted trackers](https://support.apple.com/guide/personal-safety/detect-unwanted-trackers-ips139b15fd9/web), fetched 2026-09-03).
  An OpenHaystack-style tag with a *fixed* public key is trackable-by-anyone-nearby and detectable; a tag
  with *rotating* keys and no sound-maker is the "Find You" stalking device (§4.4).
- **No evidence found of an Apple technical crackdown specifically blocking OpenHaystack-style keys.**
  I searched for reports of rate-limiting or key-registration enforcement against unregistered accessories
  in 2024–2026 and found none. Recorded as **NOT FOUND**, not as "does not exist" — Apple could change
  the acceptance rules for unregistered keys at any time, and the design must survive that.
- **Apple Developer Program License Agreement**: relevant only if the project ships an iOS/macOS app.
  The clauses that would matter are the private-API prohibition and the App Store Review Guidelines
  ban on undocumented API use; a companion app is best avoided or shipped outside the App Store. This
  was not verified against the current PDF in this pass — **UNVERIFIED, flagged for follow-up.**

### 3.4 The EU DMA angle (may change the picture)

Under the Digital Markets Act the Commission adopted two specification decisions against Apple on
19 March 2025 covering nine iOS connectivity features for connected devices, plus a request-based
interoperability process
([EC Digital Markets Act — guidance, 19 Mar 2025](https://digital-markets-act.ec.europa.eu/commission-provides-guidance-under-digital-markets-act-facilitate-development-innovative-products-2025-03-19_en), fetched 2026-09-03).
Apple has appealed ([MacRumors, 2 Jun 2025](https://www.macrumors.com/2025/06/02/apple-appeals-eu-dma-interoperability-rules/), fetched 2026-09-03),
while implementing pieces of it — iOS 26.3 brings third-party proximity pairing and notification
forwarding **in the EU only**
([Engadget, Dec 2025](https://www.engadget.com/mobile/apples-ios-263-will-introduce-proximity-pairing-to-third-party-devices-in-the-eu-133037696.html);
[MacRumors, 22 Dec 2025](https://www.macrumors.com/2025/12/22/ios-26-3-dma-airpods-pairing/), both fetched 2026-09-03).
**Find My network access is not, as of this research, among the specified features.** Worth re-checking:
if a future DMA specification decision covers Find My, the legitimate route for an open accessory in the
EU changes fundamentally.

---

## 4. Anti-stalking / DULT — the requirements and the ethics

### 4.1 Status of the standard (as of 2026-09-03)

There is **no RFC yet.** The IETF DULT working group has three documents
([datatracker DULT documents](https://datatracker.ietf.org/wg/dult/documents/), fetched 2026-09-03):

| Document | Rev | Date | State |
|---|---|---|---|
| [draft-ietf-dult-accessory-protocol](https://datatracker.ietf.org/doc/draft-ietf-dult-accessory-protocol/) | 00 | 2024-11-03 | **Expired** WG document (expired 8 May 2025) |
| [draft-ietf-dult-threat-model](https://datatracker.ietf.org/doc/draft-ietf-dult-threat-model/) | 05 | 2026-08-06 | **Active** WG document, in ARTART early review |
| [draft-ietf-dult-finding](https://datatracker.ietf.org/doc/draft-ietf-dult-finding/) | 01 | 2025-06-06 | Expired WG document |

The accessory protocol draft is authored by Brent Ledvina and Ben Detwiler (Apple) with David Lazarov and
Siddika Parlak Polatkan (Google), and replaces `draft-ledvina-dult-accessory-protocol`. Its expiry is a
process artefact, not a repudiation — it is still the only written specification of accessory-side
behaviour and it is what shipping trackers implement. Full text saved at
`research/fetched/F-dult-accessory-protocol-00.md`; the active threat model at
`research/fetched/F-dult-threat-model-05.md`; the finding draft at `research/fetched/F-dult-finding-01.md`.

The DULT abstract states its purpose plainly: *"By following these requirements and recommendations, a
location-tracking accessory will be compatible with unwanted tracking detection and alerts on mobile
platforms. This is an important capability for improving the privacy and safety of individuals in the
circumstance that those accessories are used to track their location without their knowledge or consent."*

### 4.2 What an accessory MUST do (draft-ietf-dult-accessory-protocol-00)

Extracted from the draft text (section numbers as in the draft; full text in `research/fetched/`):

| Area | Requirement | §|
|---|---|---|
| Advertisement | Service Data TLV, type `0x16`, 16-bit UUID **`0xFCB2`** in the advertisement; MAC address, Network ID byte, near-owner bit (LSB of byte 14) | 3.4.2, 3.6, Table 1 |
| Advertising | *"SHALL broadcast the location-enabled advertisement payload if location is available to the owner or was available any time within the past 24 hours"* | 3.4.3 |
| State machine | Near-owner → separated after **>30 minutes** of separation; separated → near-owner on reunification | 3.4.4–3.4.5 |
| Near-owner bit | 1 in near-owner mode, 0 in separated mode | 3.9, Table 3 |
| Advertising interval | Maximum 4 s; SHOULD be ≤ 2 s | 3.10 |
| MAC rotation | Every **15 min** in near-owner mode; every **24 h** in separated mode; and on every state transition | 3.5.1 |
| **Sound maker** | *"MUST include a sound maker (for example, a speaker) to play sound when in separated state"*, **minimum 60 Phon peak loudness (ISO 532-1:2017)** | 3.13.3 |
| Motion-triggered alert | After `TSEPARATED_UT_TIMEOUT` (**random 8–24 h**) enable motion detector at 10 s sampling; on motion drop to 0.5 s; play sound up to 10 times or 20 s total; then back off `TSEPARATED_UT_BACKOFF` = **6 h** | 3.13.2.1, Table 17 |
| Non-owner sound control | Opcodes `Sound_Start 0x0300`, `Sound_Stop 0x0301`, `Command_Response 0x0302`, `Sound_Completed 0x0303` all **REQUIRED**; `Get_Identifier 0x0404` / response `0x0405` optional. Sound commands *"SHALL only be available to the platform when the accessory is in the separated state."* | 3.13.4, Table 18 |
| Sound duration | 5 s min, 30 s max, **12 s RECOMMENDED** | 3.13.4.1 |
| Non-owner GATT | Service UUID `15190001-12F4-C226-88ED-2AC5579F2A85`, characteristic `8E0C0001-1D68-FB92-BF61-48377421680E` | 3.11 |
| Serial number | *"The serial number MUST be unique for each product ID"* and *"SHALL be printed and be easily accessible on the accessory"* | 3.15.1 |
| Identifier retrieval | Payload *"SHALL be readable either through NFC tap … or Bluetooth LE"* | 3.15.2 |
| BLE identifier gate | *"MUST have a physical mechanism, for example, a button"* to enable `Get_Identifier`; read state lasts **5 minutes** | 3.15.3 |
| Encryption | *"The identifier payload returned from an accessory in the paired state SHALL be encrypted."* | 3.15.4 |
| NFC / lost-mode URL | `https://{URL}?pid=%04x&b=%02x&fv=%08x&e=%s` with product id and encrypted identifier | 3.15.5 |
| Owner information page | Obfuscated owner contact *"MUST include at least one of the following: the last four digits of the owner's telephone number … or an email address with the first letter of the username and entity visible"* | 3.16.1 |
| Registry retention | Minimum **25 days** after disassociation | 3.16.2 |

### 4.3 Platform behaviour and the industry commitment

- Apple + Google announced the joint draft in May 2023, with **Samsung, Tile, Chipolo, eufy Security and
  Pebblebee** expressing support
  ([Apple Newsroom, May 2023](https://www.apple.com/newsroom/2023/05/apple-google-partner-on-an-industry-specification-to-address-unwanted-tracking/), fetched 2026-09-03).
  NNEDV's Erica Olsen called it *"a significant step forward"*; CDT's Alexandra Reeve Givens praised a
  *"universal, OS-level solution."*
- Shipped May 2024: iOS 17.5 and Android 6.0+ raise *"[Item] Found Moving With You"* alerts for any
  DULT-compatible tracker regardless of the platform it is paired with; *"Bluetooth tag manufacturers
  including Chipolo, eufy, Jio, Motorola, and Pebblebee have committed that future tags will be
  compatible"*
  ([Apple Newsroom, 13 May 2024](https://www.apple.com/newsroom/2024/05/apple-and-google-deliver-support-for-unwanted-tracking-alerts-in-ios-and-android/), fetched 2026-09-03).
- On iPhone the alert lets the user *"view the tracker's identifier, have the tracker play a sound to help
  locate it, and access instructions to disable it"* (same source).
- **Compliance is voluntary, not legally mandated.** Apple's own newsroom framing is that the spec *"offers
  instructions and best practices for manufacturers, should they choose to build unwanted tracking alert
  capabilities into their products."* There is (as of this research) no statute anywhere requiring a BLE
  tracker to implement DULT.

### 4.4 The threat model, and why this is the project's central ethical problem

- **The attack is proven and published.** Positive Security's *"Find You"* built a stealth AirTag clone on
  an ESP32 that cycled ~2,000 pre-generated public keys, one beacon every 30 s, with **no speaker at all**,
  and tracked a target iPhone user for **over five days without triggering a single alert**
  ([positive.security/blog/find-you](https://positive.security/blog/find-you), fetched 2026-09-03). Their
  conclusion: *"Since Apple in the current Find My design can't limit its usage to only genuine AirTags
  (and official partner's devices), they need to take into account the threats of custom-made, potentially
  malicious beacons."*
- Adam Catley's teardown shows the AirTag's own protection is fragile: *"The coil can be disconnected
  without disassembly. The AirTag operates as normal without the voice coil connected. I have observed all
  sound related events still occur, just silently."* (`research/fetched/A-catley-airtag-reverse-engineering.md`).
- The DULT threat model draft-05 (2026-08-06) is explicit about non-conformant tags, §4.1.4: four attack
  vectors — *impersonation, replay attacks, physical modifications, and firmware alterations* — and
  *"While it is not possible to limit the deployment of nonconformant Tags, a successful protocol would
  minimize the ability of nonconformant Tags to access the crowdsourced network."* Its core requirement,
  §4.2: *"The DULT Protocol should 1) allow Targets to detect Unwanted Tracking, 2) help Targets find Tags
  that are tracking them while minimizing false positives … and 3) provide instructions for Targets to
  disable those Tags."* Its guiding privacy principle, §4: *"Avoid privacy compromises for Tag Owner(s)
  when protecting against Unwanted Tracking. The privacy of Tag Owner(s) and the security of Targets
  should be considered equally."*
- **The harm is real and litigated.** *Hughes v. Apple, Inc.*, No. 3:22-cv-07668 (N.D. Cal.): Judge Vince
  Chhabria allowed negligence and product-liability claims by three plaintiffs to proceed in March 2024
  ([TechXplore report](https://techxplore.com/news/2024-03-apple-lawsuit-airtags-weapon-stalkers.html);
  [casemine summary](https://www.casemine.com/judgement/us/65f67201f0af1e2dac49b1c3), both fetched 2026-09-03).
  Class certification was later denied on state-law-variation and individualised-injury grounds, and Apple
  now faces **30+ individual suits**; reporting states Apple received **more than 40,000 stalking reports
  between April 2021 and April 2024** and that internal documents said its safeguards would *"deter as
  opposed to prevent malicious use"*
  ([MacRumors, 1 May 2026](https://www.macrumors.com/2026/05/01/airtag-stalking-lawsuits-apple/), fetched 2026-09-03).
- **Where the defensive ecosystem stands**: AirGuard (TU Darmstadt SEEMOO) is a free, open-source,
  passive scanner for Android and iOS that detects AirTags, Find My accessories, Samsung SmartTags, Tiles
  and Google trackers, processing all data locally
  ([AirGuard on F-Droid](https://f-droid.org/packages/de.seemoo.at_tracking_detection/);
  [AirGuard paper, arXiv:2202.11813](https://arxiv.org/pdf/2202.11813), both fetched 2026-09-03).
  The same lab that built OpenHaystack built AirGuard. **That pairing is the model haytag should copy:
  if you publish the tag, you owe the ecosystem the countermeasure.**

### 4.5 The position this project should publish

Drafted as `docs/ANTI-STALKING.md` in this same pass. The short version:

- haytag **implements the DULT separated-state sound and non-owner controls**, on real hardware, by
  default, and the firmware ships that way.
- haytag **does not** implement, document, or accept patches for silent modes, sound suppression,
  key-cycling beyond the DULT rotation schedule, or "stealth" build flags.
- haytag **publishes** an owner-information/lost-mode page format and a printed serial number so a person
  who finds a tag can act on it.
- haytag **links to AirGuard** and to the platform detection features in its own README, and tells buyers
  how to scan for unwanted trackers.
- haytag states plainly that a board with the buzzer depopulated is a stalking device, and that the
  project will not help anyone build one.

---

## 5. Radio certification

### 5.1 The decision that dominates the BOM: pre-certified module vs bare silicon

Under [47 CFR §15.212](https://www.law.cornell.edu/cfr/text/47/15.212) (fetched 2026-09-03) a *single
modular transmitter* can be granted its own FCC certification if it meets eight conditions, quoted in part:
*(i) "The radio elements of the modular transmitter must have their own shielding"*, *(ii) buffered
modulation/data inputs*, *(iii) "its own power supply regulation"*, *(iv) permanently attached antenna or
a "unique" antenna coupler*, *(v) "tested in a stand-alone configuration"*, *(vi) "equipped with either a
permanently affixed label or must be capable of electronically displaying its FCC identification number"*,
*(vii) compliance with the rules that apply to a complete transmitter*, *(viii)* RF-exposure compliance.

**Consequence**: if haytag uses a certified module (Fanstel, Raytac, Minew, Insight SiP etc. built on
nRF52) the intentional-radiator testing is already done and paid for by the module vendor. The host
product must:
- carry an exterior label such as *"Contains Transmitter Module FCC ID: XYZMODEL1"* or *"Contains FCC ID:
  XYZMODEL1"* when the module's own label is not visible (§15.212 / FCC KDB guidance;
  [FCC Transmitter Module Equipment Authorization Guide](https://apps.fcc.gov/eas/comments/GetPublishedDocument.html?id=50&tn=916170), fetched 2026-09-03);
- keep the module's certified antenna, RF layout, keep-out and integration conditions exactly as the
  vendor's integration guide specifies (any deviation can void modular approval);
- still be tested as an **unintentional radiator** (Part 15 subpart B) — the digital electronics around
  the module.
Raytac's own integration note confirms the practical split between module and non-module approval routes
([Raytac: module vs non-module approval](https://raytac.blog/2023/06/14/understanding-wireless-certification-and-compliancea-guide-to-module-and-non-module-approval-processes/), fetched 2026-09-03).
General industry guidance on the cost delta is summarised by
[EMC FastPass on pre-certified vs non-certified RF modules](https://emcfastpass.com/rf-modules/) (fetched 2026-09-03).

**Cost note (indicative, not quoted from a primary source):** full intentional-radiator certification of a
2.4 GHz design across FCC + CE + more is commonly cited in the five-figure USD range per market, versus
low-four-figure unintentional-radiator/host testing when using a certified module. Get real quotes; do not
budget from this document.

### 5.2 Which FCC rule part

BLE at 2.4 GHz is a digitally modulated intentional radiator under
[§15.247](https://www.law.cornell.edu/cfr/text/47/15.247) (fetched 2026-09-03): *"The minimum 6 dB
bandwidth shall be at least 500 kHz"* (§15.247(a)(2)); max conducted output *"1 Watt"* for 2400–2483.5 MHz
digital modulation (§15.247(b)(3)); power reduction required above 6 dBi antenna gain (§15.247(b)(4));
out-of-band *"at least 20 dB below"* the in-band level in any 100 kHz (§15.247(d)); PSD *"not be greater
than 8 dBm in any 3 kHz band"* (§15.247(e)). §15.249 is the alternative low-field-strength route for
2400–2483.5 MHz devices; **the certified nRF52 modules on the market are certified under §15.247**, so
this is settled by the module choice and is not an independent decision for haytag.
*(Note: I did not obtain a primary-source side-by-side of §15.247 vs §15.249 limits in this pass —
**partially verified**, §15.247 text quoted directly, §15.249 not fetched.)*

### 5.3 EU / CE — RED 2014/53/EU

Radio equipment sold in the EU needs a CE mark under the Radio Equipment Directive 2014/53/EU. Where
harmonised standards exist the manufacturer may self-declare under Module A (internal production control)
without a notified body ([RED explainer, IB-Lenhardt](https://ib-lenhardt.com/kb/faq/radio-equipment-directive-red);
[instrktiv RED guide](https://instrktiv.com/en/radio-equipment-directive/), both fetched 2026-09-03).
The applicable harmonised standards for a 2.4 GHz BLE product are:

| Article | Standard | Covers |
|---|---|---|
| 3.2 (spectrum) | **EN 300 328** | 2.4 GHz wideband data transmission ([ETSI EN 300 328 overview](https://ib-lenhardt.com/kb/glossary/en-300-328), fetched 2026-09-03) |
| 3.1(b) (EMC) | **EN 301 489-1** + **EN 301 489-17** | EMC, generic + broadband data transmission |
| 3.1(a) (health/safety) | **EN 62479** (low-power RF exposure assessment) and/or **EN 50665**; **EN IEC 62368-1** for electrical safety | RF exposure and product safety |

The Commission publishes the consolidated citation list for RED
([EC harmonised standards — radio equipment](https://single-market-economy.ec.europa.eu/single-market/european-standards/harmonised-standards/radio-equipment_en), fetched 2026-09-03;
the page hosts the summary as downloadable PDF/XLS, generated 13.10.2025). **The exact OJEU citation dates
for each standard were not extracted in this pass — verify against the current list before writing the
DoC.** A CE-marked product also needs a written **EU Declaration of Conformity** and a technical file.

### 5.4 UK, Japan and Bluetooth SIG

- **UK**: the Radio Equipment Regulations 2017 apply, enforced via UKCA. However the UK government has
  **extended indefinite recognition of the CE mark** for GB, so a CE-marked radio product can be placed on
  the GB market without a separate UKCA mark
  ([Hogan Lovells: CE marking to remain indefinitely recognised in the UK](https://www.hoganlovells.com/en/publications/outside-but-aligned-ce-marking-to-remain-indefinitely-recognised-in-the-uk);
  [UL Solutions on CE and UKCA for wireless](https://www.ul.com/resources/understanding-ce-and-ukca-marking-requirements-wireless-products), both fetched 2026-09-03).
- **Japan**: MIC/TELEC certification (the **Giteki** 技適 mark) is mandatory under the Radio Law, assessed
  by a Registered Certification Body — **not** self-declaration. Critically: *"If installing a module with
  existing Japan certification, additional certification for the host device is unnecessary, and you just
  need to include specified text to indicate the presence of a certified radio module."*
  ([MIC requirements, IB-Lenhardt](https://ib-lenhardt.com/kb/mic-requirements);
  [Element on Japan Radio Law and MIC certification](https://www.element.com/connected-technologies/wireless-radio-testing/japan-radio-law-and-mic-certification), both fetched 2026-09-03).
  So: pick a module that already carries a Giteki number if Japan matters.
- **Bluetooth SIG**: using the Bluetooth® word mark/logo requires SIG membership and product
  qualification — *"ALL Bluetooth® Products must be qualified"* and *"The Bluetooth Qualification Process
  must be completed before you take products to market"*, and *"Your supplier or other member companies
  cannot qualify your products on your behalf. You must complete the Bluetooth Qualification Process for
  your product under your company's membership account."*
  ([bluetooth.com qualification listing](https://www.bluetooth.com/develop-with-bluetooth/qualification-listing/), fetched 2026-09-03).
  Fees, from the [official fee schedule effective 1 March 2026](https://www.bluetooth.com/fee-schedule/)
  (fetched 2026-09-03):

  | Item | Adopter | Contributing Adopter | Associate |
  |---|---|---|---|
  | Annual dues | **$0** | $3,500 (small) / $16,500 (large) | $11,250 (small) / $52,500 (large) |
  | Company Identifier | $1,250 | $1,250 | $0 |
  | Product qualification fee | **$12,000** | $8,000 first (33% off) / $12,000 subsequent | $6,000 (50% off) |
  | 16-bit UUID | $3,750 | | |

  Also: *"A Product Qualification Fee will be required for the first product submission that includes a
  specific design. However, subsequent products you submit that include the same design will not be
  charged a fee."*
  **Consequence for haytag**: Adopter membership is free, but a listed product costs **$12,000** at
  Adopter tier under the 2026 schedule. That is a real barrier for a hobby/open project. Two honest
  outcomes: (a) do not use the Bluetooth word mark or logo anywhere on the product, packaging or
  marketing, and describe it as "2.4 GHz BLE-compatible" from the module's qualified design; or (b) budget
  the qualification. *Note: some sources cite lower historic Declaration ID fees ($4k–$8k); the fee
  schedule page is the authority and it is what is quoted above.*

### 5.5 UWB certification (only if UWB were added)

- **US**: UWB is 47 CFR Part 15 subpart F. FCC guidance: *"Whenever possible (i.e., if the UWB fundamental
  emission can be fully contained within the 5925−7250 MHz frequency band), Section 15.250 should be
  considered as an alternative to either Section 15.517 or Section 15.519."* And critically for a tag:
  *"Modular approval will only be considered for UWB applications under Section 15.519 requirements"*
  ([FCC OET TCB workshop, UWB certification issues and guidance](https://transition.fcc.gov/oet/ea/presentations/files/nov17/52-UWB-Guidance-SJ.pdf), fetched 2026-09-03).
  §15.519(a)(1) additionally requires a handheld UWB transmitter to *cease transmissions within 10 seconds
  of failing to receive an acknowledgement* — a firmware obligation, not just a test.
  Governing sections list: [47 CFR part 15 subpart F](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-F).
- **EU**: **ETSI EN 302 065** series is the RED harmonised standard for UWB SRDs — Part 1 generic UWB
  applications, with parts for location tracking, vehicles, and material sensing
  ([ETSI EN 302 065-1 V2.1.1 record](https://standards.iteh.ai/catalog/standards/etsi/986f0a76-a969-45a7-9126-970eb2660696/etsi-en-302-065-1-v2-1-1-2016-11);
  [ETSI EN 302 065-4-4 V2.1.1 (2025-07) PDF](https://www.etsi.org/deliver/etsi_en/302000_302099/3020650404/02.01.01_60/en_3020650404v020101p.pdf), both fetched 2026-09-03).
- **Verdict: skip UWB.** It adds a second radio certification, a second patent thicket (§2.3), a much
  larger BOM and battery drain, and the Find My UWB handshake is inside the NDA'd spec anyway.

---

## 6. Battery safety — the CR2032 is a regulated hazard, not a commodity

### 6.1 United States: Reese's Law / 16 CFR part 1263

Reese's Law was signed 16 August 2022; the CPSC's implementing rule is **16 CFR part 1263, Safety Standard
for Button Cell or Coin Batteries and Consumer Products Containing Such Batteries**, which incorporates
**ANSI/UL 4200A-2023** by reference
([Federal Register, 21 Sep 2023](https://www.federalregister.gov/documents/2023/09/21/2023-20334/safety-standard-for-button-cell-or-coin-batteries-and-consumer-products-containing-such-batteries);
[eCFR 16 CFR part 1263](https://www.ecfr.gov/current/title-16/chapter-II/subchapter-B/part-1263), both referenced 2026-09-03 — the eCFR fetch was blocked by a redirect, so the operative text below is quoted from CPSC's own business guidance).

From [CPSC Business Guidance — Button Cell and Coin Battery](https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Button-Cell-and-Coin-Battery) (fetched 2026-09-03), verbatim:

- Scope: *"consumer products that contain button cell or coin batteries"*, excluding zinc-air chemistries
  and toys complying with 16 CFR part 1250.
- **Performance requirement**: *"Battery compartments containing replaceable button cell or coin batteries
  must be secured such that they require the use of a tool or at least two independent and simultaneous
  hand movements to open."*
- **Warnings** must appear on *"the packaging for the overall product,"* on *"the product itself, if
  practicable,"* and in *"accompanying instructions and manuals."*
- **Dates**: general compliance for products *manufactured or imported after 19 March 2024*; packaging
  labelling requirements for products imported/manufactured *on or after 21 September 2024*.
- **Certification**: a **General Certificate of Conformity (GCC)** (or a Children's Product Certificate for
  children's products) citing the applicable rule.

UL 4200A itself: *"covers household type products that incorporate or may use button batteries or coin
cell batteries"*, requires compartments *"secured in a way that requires the use of a tool or at least two
independent hand movements to open"*, and prescribes warning text and font heights scaled to the
principal display panel
([UL Solutions on Reese's Law / UL 4200A](https://www.ul.com/resources/reeses-lawul-4200a-standard-safety-products-incorporating-button-batteries-or-coin-cell);
[CSA Group UL 4200A page](https://www.csagroup.org/testing-certification/product-areas/information-communication-technology-ict/ul-4200a-button-cell-coin-batteries/);
[Intertek: US Reese's Law](https://www.intertek.com/retail/us-reeses-law-button-cell-coin-battery/), all fetched 2026-09-03).

**How AirTag complies**: the twist-lock door requires *press-and-twist* — two independent movements — and
Apple prints the battery-ingestion warning on the product/packaging. (The accessibility cost of this is
real and documented:
[Forbes, "Apple's AirTags Are Accessible, But Their Achilles Heel Is An Inaccessible Battery Door"](https://www.forbes.com/sites/stevenaquino/2024/04/16/apples-airtags-are-accessible-but-their-achilles-heel-is-an-inaccessible-battery-door/), fetched 2026-09-03.)

**Implications for a 3D-printed or snap-fit haytag shell — the single biggest mechanical constraint:**
- A **friction snap-fit lid a fingernail can pop is a single hand movement and fails** the rule.
- Compliant options: (a) a **screw** (tool required — simplest and most 3D-print-friendly), (b) a
  **press-and-twist bayonet** like the AirTag's (needs printable tolerances and a detent, harder in FDM,
  achievable in SLA/MJF), (c) a latch requiring **simultaneous** press + slide.
- If the design is only ever *published as files* and never *sold as a consumer product in the US*,
  16 CFR 1263 does not attach — the rule regulates products manufactured or imported for sale. But
  publishing a non-compliant door design and inviting people to print it is exactly the sort of thing a
  responsible project shouldn't do. **Design it compliant.**
- Also plan the **warning label**: text on the product where practicable, on the packaging, and in the
  README/manual; and a GCC if units are ever sold.

### 6.2 European Union

There is **no direct EU equivalent of Reese's Law for non-toy consumer products** as of this research
([ComplianceGate: EU button/coin battery regulations](https://www.compliancegate.com/button-coin-battery-regulations-european-union/), fetched 2026-09-03).
What does apply:
- **GPSR (EU) 2023/988** — the General Product Safety Regulation *"covers virtually all consumer products,
  including button cell and coin batteries and products containing such batteries"* and imposes a general
  safety obligation plus documentation and labelling duties.
- **Batteries Regulation (EU) 2023/1542** — covers *"batteries and products containing batteries … including
  button cells and coin batteries"*, with substance restrictions, labelling, documentation and testing;
  it also carries removability/replaceability duties for portable batteries. *(Article 11's exact text and
  application date were **not retrieved** — EUR-Lex fetches returned empty in this pass. **Verify before
  relying on it.**)*
- **EN IEC 62115** (electric toys) is the standard containing the classic child-accessibility and
  fastener-retention requirements — e.g. a 20 N pull on the fastener for 10 s, which must remain attached
  ([QIMA guide to EN IEC 62115](https://blog.qima.com/lab-testing/guide-to-en-iec-62115-standard), fetched 2026-09-03).
  **haytag is not a toy**, so EN 62115 does not apply directly — but it is the obvious yardstick to design
  to, and satisfying UL 4200A will comfortably clear it.
- **EN IEC 60086-4** covers primary lithium cell safety, warning requirements and child-resistant packaging
  for the cells themselves.

### 6.3 Shipping lithium coin cells

- **UN 3090** = lithium *metal* batteries shipped alone; **UN 3091** = lithium metal batteries *contained in*
  or *packed with* equipment. Packing instruction **PI 969** for packed-with-equipment, **PI 970** for
  contained-in-equipment
  ([DHL lithium metal battery regulations PDF](https://mydhl.express.dhl/content/dam/downloads/global/en/lithium-batteries/lithium_metal_batteries_regulations.pdf.coredownload.pdf);
  [DG Inspector lithium battery shipping guide](https://dginspector.com/blog/lithium-battery-shipping-guide), both fetched 2026-09-03).
- Useful relief: *"For packages containing only button cell batteries installed in equipment (including
  circuit boards) it is not required to have the statement on the waybill and the Lithium Battery Mark on
  the package."*
  ([UN 3091 button cells in equipment, air](https://wrap-tds.com/un-3091-lithium-metal-button-cells-contained-in-equipment-by-international-air-within-limits-below/), fetched 2026-09-03).
- **Design consequence**: shipping a haytag **with the CR2032 already installed** (UN 3091, PI 970, button
  cell in equipment) is materially simpler than shipping loose cells (UN 3090). If a kit ships cells
  separately, the full UN 3090 marking/documentation regime applies. Also: cells must be UN 38.3 tested by
  their manufacturer — buy branded cells (Panasonic/Murata/Renata) and keep the test summaries.

---

## 7. Open-source licensing

### 7.1 The hardware licences

**CERN-OHL v2** comes in three variants ([cern-ohl.web.cern.ch](https://cern-ohl.web.cern.ch/), fetched 2026-09-03):

| Licence | SPDX | Character | Effect |
|---|---|---|---|
| CERN-OHL-P-2.0 | [SPDX](https://spdx.org/licenses/CERN-OHL-P-2.0.html) | Permissive | Use with few restrictions; keep notices; no warranty |
| CERN-OHL-W-2.0 | [SPDX](https://spdx.org/licenses/CERN-OHL-W-2.0.html) | Weakly reciprocal | Sources of the licensed work and modifications must be available under the same licence; *"a larger work using the licensed work through interfaces provided by the licensed work may be distributed under different terms and without sources for the larger work"* |
| CERN-OHL-S-2.0 | [SPDX](https://spdx.org/licenses/CERN-OHL-S-2.0.html) | Strongly reciprocal | Permissions *"are conditioned on making available complete sources of licensed works and modifications, which include larger works using a licensed work, under the same license"* |

(All SPDX pages fetched 2026-09-03; summary comparison also at
[choosealicense CERN-OHL-S](https://choosealicense.com/licenses/cern-ohl-s-2.0/) and
[Wikipedia: CERN Open Hardware Licence](https://en.wikipedia.org/wiki/CERN_Open_Hardware_Licence).)

Alternatives:
- **TAPR OHL** — the older (2007) reciprocal hardware licence; largely superseded by CERN-OHL-S in new
  projects and drafted against US law only.
- **CC-BY-SA 4.0** — Creative Commons themselves recommend *against* CC licences for software and for
  functional hardware designs; CC-BY-SA is appropriate for **documentation and images**, not for the
  KiCad sources.
- **MIT / Apache-2.0** — software licences; wrong instrument for board files (no patent-in-hardware or
  "Source" definition), right instrument for firmware and tools. Apache-2.0 additionally carries an
  express patent grant and a patent-retaliation clause, which is a genuine advantage in this domain.

**OSHWA certification** is a separate, free, self-certification layer, not a licence
([OSHWA certification requirements](https://certification.oshwa.org/requirements.html);
[mark usage](https://certification.oshwa.org/mark-usage.html), both fetched 2026-09-03). Requirements:
comply with the community Open Source Hardware Definition; share all of the creator's own contributions as
open source; ensure all parts within the creator's control are open source; self-certify via the online
form; register each unique product bearing the mark. *"Third-party closed components outside of their
control"* are allowed, but third-party components such as chips *"must have fully accessible and shareable
datasheets"*. Certification lasts one year with annual renewal; each project gets a UID (two-letter
country code + six digits), and the logo is required while the UID is optional-but-encouraged.
**Consequence for haytag**: an nRF52 module with a public datasheet qualifies; a module whose datasheet is
NDA-only would not. Choose the module accordingly.

### 7.2 The firmware licence problem — AGPL-3.0 upstream

- **OpenHaystack is AGPL-3.0**: *"OpenHaystack is licensed under the GNU Affero General Public License
  v3.0"* ([README](https://github.com/seemoo-lab/openhaystack), copy in `research/fetched/`).
- **macless-haystack is AGPL-3.0** too ([dchristl/macless-haystack](https://github.com/dchristl/macless-haystack), fetched via lane B).
- AGPL-3.0's distinguishing feature is §13: providing the program's functionality **over a network** to
  users triggers the obligation to offer them the corresponding source. Commercial use is *permitted*,
  but *"utilizing AGPLv3-licensed software in commercial services still entails an obligation to publish
  the source code"* ([GNU AGPL overview](https://en.wikipedia.org/wiki/GNU_Affero_General_Public_License), fetched 2026-09-03).

**What this means concretely for a commercial haytag:**
- Firmware **derived from** OpenHaystack/macless-haystack firmware inherits AGPL-3.0. Selling a tag with
  that firmware in it requires offering complete corresponding source to the purchaser — which for an open
  project is not a burden, it is the point.
- A **server/relay component** derived from macless-haystack and offered as a hosted service to users
  triggers AGPL §13: you must offer source to the service's users.
- The realistic trap is a downstream vendor who forks haytag firmware, sells tags with a hosted endpoint,
  and does not publish. AGPL is the licence that makes that a violation; MIT is the licence that makes it
  legal. **Pick deliberately.**
- If haytag's own firmware is written clean (not derived from OpenHaystack code) the licence is a free
  choice — but the ecosystem norm, and the enforcement value, both favour a copyleft licence.

### 7.3 Recommended licence split for this repo

*(Research recommendation. Confirm with counsel before publishing; a licence choice is a legal act.)*

| Directory / artefact | Recommended licence | Rationale |
|---|---|---|
| `electronics/`, `hardware/` — KiCad schematics, PCB, footprints, 3D shell (STEP/STL/FreeCAD) | **CERN-OHL-S-2.0** | Purpose-built for hardware; strongly reciprocal so a cloner who improves the board must publish the improvement; SPDX-recognised; the de-facto standard for serious open hardware |
| `firmware/` — nRF52 firmware, DULT implementation | **AGPL-3.0-or-later** if any OpenHaystack-derived code is used (required); otherwise **GPL-3.0-or-later** with a considered option of AGPL-3.0 to close the hosted-service loophole | Matches upstream; keeps the anti-stalking implementation in every fork rather than letting a vendor strip it |
| `tools/`, `spec/` — helper scripts, key generators, report fetchers | **AGPL-3.0-or-later** (if derived from macless-haystack/findmy.py) else **Apache-2.0** | Apache-2.0's express patent grant + retaliation clause is worth having in a patent-dense field |
| `docs/`, `research/`, images, renders | **CC-BY-SA-4.0** | Right instrument for prose and pictures; keeps derived documentation open |
| Third-party vendored code | its own licence, unchanged, recorded in `THIRD-PARTY.md` | Compliance hygiene |

Plus:
- Put an **SPDX-License-Identifier** header in every source file.
- Add a top-level `LICENSES/` directory with the full texts (REUSE-style) and a `NOTICE`/`TRADEMARKS.md`
  carrying the Apple disclaimer from §1.5.
- **Apply for OSHWA certification** once the board is released — free, and it commits the project publicly
  to the OSHW definition.
- Note the interaction: CERN-OHL-S on the board and (A)GPL on the firmware is a normal, workable
  combination — the licences govern different works; document which files are which.

---

## 8. Privacy and export law

### 8.1 GDPR

A BLE tracker sold in the EU is a personal-data machine. The relevant points:
- **BLE identifiers are personal data in context.** The UK ICO's 2023 position is that MAC addresses,
  recorded alongside timestamps and location, meet the threshold for personal data
  (as summarised in [needCode, BLE privacy by design & EU compliance](https://needcode.io/ble-privacy/), fetched 2026-09-03 — secondary source, flagged).
- **Privacy by design is a legal duty**, GDPR Art. 25 — protections must be *"integrated into the technical
  design of a product — not bolted on afterward"*
  ([GDPR and IoT devices: obligations for connected product manufacturers](https://dev.to/custodiaadmin/gdpr-and-iot-devices-privacy-obligations-for-connected-product-manufacturers-4127), fetched 2026-09-03 — secondary source).
- **Who is the controller?** This is the decisive question and it lands *well* for haytag. In the
  OpenHaystack architecture, key material is generated and held by the owner, location reports are
  end-to-end encrypted to the owner's key, and Apple stores only opaque ciphertext indexed by a key hash
  (PoPETs 2021, §3.3 above). **If the project ships no server and operates no service, it processes no
  personal data and is not a controller** — the tag owner is, for their own use, likely covered by the
  household exemption (Art. 2(2)(c)) unless they track another person. If haytag ever runs a hosted
  endpoint, relay or registry (including a DULT owner-information page, §4.2), **that service is
  processing personal data and needs a lawful basis, a privacy notice, retention limits and a DPO
  assessment.** Note the DULT draft's own §3.16.2 retention floor of 25 days for owner registry data —
  a retention *minimum* set by the protocol against a GDPR minimisation duty; reconcile the two deliberately.
- The academic literature on tracker privacy is directly useful:
  [A Tale of Three Location Trackers: AirTag, SmartTag, and Tile (arXiv:2501.17452)](https://arxiv.org/pdf/2501.17452) and
  [Privacy Analysis of Samsung's Crowd-Sourced Bluetooth Location Tracking System (arXiv:2210.14702)](https://arxiv.org/pdf/2210.14702), both fetched 2026-09-03.

### 8.2 Export control — confirmed as a non-issue, with one condition

- The device uses **standard cryptography** (P-224 ECC, AES) as an ancillary function. Under the EAR,
  publicly available encryption source code is **not subject to the EAR** once the §742.15(b) notification
  has been made, and — importantly — the Linux Foundation's guidance records that since 2021, *"if an open
  source project uses standard cryptography, there are no additional requirements or analysis required;
  however, if a project is using non-standard cryptography, email notifications are still required"*
  ([Linux Foundation, Understanding US export controls with open source projects](https://www.linuxfoundation.org/resources/publications/understanding-us-export-controls-with-open-source-projects);
  [BIS: encryption items not subject to the EAR](https://www.bis.gov/learn-support/encryption-controls/encryption-items-not-subject-to-ear);
  [15 CFR 742.15](https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C/part-742/section-742.15), all fetched 2026-09-03).
- Mass-market hardware with ancillary encryption typically classifies as **ECCN 5A992.c** and ships NLR /
  under License Exception ENC ([15 CFR 740.17](https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C/part-740/section-740.17), fetched 2026-09-03).
- **Conclusion: no meaningful export-control constraint on publishing haytag**, provided the project uses
  only standard cryptography and publishes openly. The usual sanctions/denied-party rules would apply to
  *selling* hardware, as for any product.

---

## 9. Constraints the design must honour

| # | Constraint | Source | Design consequence |
|---|---|---|---|
| C1 | Project name must not contain, abbreviate or be a takeoff of `AirTag`, `Find My`, `iTag` or any Apple mark | [Apple 3rd-party trademark guidelines](https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html) | Repo/product stays **`haytag`**; no `airtag` in repo name, domain, package name, silkscreen or BLE device name |
| C2 | Compatibility may only be stated in a referential phrase, with no Apple logo and no implication of endorsement | ibid.; nominative fair use ([INTA](https://www.inta.org/fact-sheets/fair-use-of-trademarks-intended-for-a-non-legal-audience/)) | README/packaging line: *"compatible with Apple's Find My network. Not affiliated with, sponsored or endorsed by Apple Inc."* Add `TRADEMARKS.md` |
| C3 | "Works with Apple Find My" badge is MFi-licensed | [Apple Newsroom 2021](https://www.apple.com/newsroom/2021/04/apples-find-my-network-now-offers-new-third-party-finding-experiences/) | Never render or ship that badge; no Apple artwork anywhere |
| C4 | The Find My accessory spec is Apple Confidential, NDA-gated | [MFi FAQs](https://mfi.apple.com/en/faqs.html) | **Clean-room only**: implement from PoPETs 2021 + OpenHaystack. Do not download, cite or copy leaked R3 spec mirrors. Contributors under Apple NDA must not touch protocol code |
| C5 | Do not copy the AirTag's ornamental design | [USD958677 S1](https://patents.google.com/patent/USD958677S1/en) (Apple, to ~2037) | Shell must look visibly different: different proportions, no polished white dome, no mirror-steel back. Document the deliberate divergence |
| C6 | Apple holds live patents on near-owner/separated advertisement state machines and crowd-sourced reporting | [US 11,889,302 B2](https://patents.google.com/patent/US11889302B2/en), [US 9,479,920 B1](https://patents.google.com/patent/US9479920B1/en) | Publish design + firmware as research/open hardware; get an FTO opinion **before** selling assembled units commercially. Mark this in the README's risk section |
| C7 | UWB adds a second patent thicket and a separate certification regime, and its Find My handshake is NDA-only | §2.3, §5.5; [FCC UWB guidance](https://transition.fcc.gov/oet/ea/presentations/files/nov17/52-UWB-Guidance-SJ.pdf) | **BLE only.** No UWB radio on the board; note as an explicit non-goal |
| C8 | Accessory MUST include a sound maker, ≥60 Phon peak (ISO 532-1:2017), audible in separated state | draft-ietf-dult-accessory-protocol-00 §3.13.3 | A real magnetic buzzer/piezo on the BOM, driven loud enough; measure it. Not a DNP option, not a jumper |
| C9 | Separated-state motion-triggered alert: random 8–24 h timeout, motion sampling 10 s → 0.5 s, sound ≤10 plays / 20 s, then 6 h back-off | ibid. §3.13.2.1, Table 17 | An accelerometer (or equivalent motion sense) is **required** on the BOM, plus the firmware timer/back-off state machine |
| C10 | Non-owner controls `Sound_Start/Stop/Command_Response/Sound_Completed` REQUIRED, available only in separated state | ibid. §3.13.4, Table 18 | Implement the DULT GATT service `15190001-…` / characteristic `8E0C0001-…` in firmware; a stranger's phone can make the tag beep |
| C11 | Serial number MUST be unique per product ID and SHALL be printed and easily accessible on the accessory | ibid. §3.15.1 | Silkscreen/label field on the shell and on the PCB; a per-unit serial in flash/UICR; a provisioning step in the build docs |
| C12 | Identifier payload SHALL be readable via NFC tap or BLE; BLE path needs a physical mechanism (e.g. a button) and a 5-minute read window; paired-state payload SHALL be encrypted | ibid. §3.15.2–3.15.4 | Either an NFC antenna/NTAG on the board, **or** a user-pressable button + the BLE `Get_Identifier` path. Pick one and implement it fully |
| C13 | Lost-mode/owner-information page with obfuscated owner contact (last 4 digits of phone, or first letter of email username + domain), retained ≥25 days after disassociation | ibid. §3.15.5, §3.16.1–3.16.2 | Define a `haytag.<domain>/found?...` URL format and a minimal owner-info page; reconcile the 25-day floor with GDPR minimisation |
| C14 | MAC/key rotation: 15 min near-owner, 24 h separated, and on every state transition; advertising ≤4 s (SHOULD ≤2 s) | ibid. §3.5.1, §3.10 | Firmware key schedule must follow DULT, **not** a stealth cycle. Never expose a "rotate faster / new key per beacon" build flag |
| C15 | No RFC exists yet; DULT accessory protocol -00 is expired, threat model -05 is active | [datatracker DULT docs](https://datatracker.ietf.org/wg/dult/documents/) | Pin the implementation to `draft-ietf-dult-accessory-protocol-00` **by name and revision** in the firmware docs; add a re-check task for when a successor or RFC appears |
| C16 | Radio: use a pre-certified nRF52 module to avoid intentional-radiator testing; keep vendor antenna/layout; label "Contains FCC ID: …" | [47 CFR §15.212](https://www.law.cornell.edu/cfr/text/47/15.212) | Module (Fanstel/Raytac/Minew) not bare nRF52 die. Reserve silkscreen for the FCC-ID text. Follow the module integration guide's keep-out exactly |
| C17 | 2.4 GHz limits under §15.247 (≥500 kHz 6 dB BW, ≤1 W, ≤8 dBm/3 kHz PSD, −20 dB OOB) | [47 CFR §15.247](https://www.law.cornell.edu/cfr/text/47/15.247) | Satisfied by the module's existing certification; do not modify TX power beyond the module's certified range |
| C18 | EU: CE under RED 2014/53/EU via EN 300 328, EN 301 489-1/-17, EN 62479, EN IEC 62368-1; self-declaration possible | [EC harmonised standards, RED](https://single-market-economy.ec.europa.eu/single-market/european-standards/harmonised-standards/radio-equipment_en) | Build a technical file + EU DoC even for a hobby release; verify current OJEU citations before signing |
| C19 | UK accepts CE indefinitely; Japan needs a Giteki-marked module | [Hogan Lovells on CE in UK](https://www.hoganlovells.com/en/publications/outside-but-aligned-ce-marking-to-remain-indefinitely-recognised-in-the-uk); [MIC requirements](https://ib-lenhardt.com/kb/mic-requirements) | No separate UKCA work. If Japan is in scope, filter module selection by existing Giteki number |
| C20 | Bluetooth word mark/logo requires SIG membership + product qualification ($12,000 at Adopter tier, effective 1 Mar 2026) | [Bluetooth SIG fee schedule](https://www.bluetooth.com/fee-schedule/); [qualification listing](https://www.bluetooth.com/develop-with-bluetooth/qualification-listing/) | Default: **do not use the Bluetooth word mark or logo**. Say "2.4 GHz BLE". Revisit only if the project commercialises |
| C21 | US: battery compartment must need **a tool, or ≥2 independent and simultaneous hand movements**; warnings on packaging, on product if practicable, and in instructions; GCC required; applies to products made/imported after 19 Mar 2024 | [CPSC business guidance](https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Button-Cell-and-Coin-Battery); 16 CFR 1263 / ANSI-UL 4200A-2023 | **Screw-secured or press-and-twist door — never a plain snap fit.** Add the ingestion warning to shell artwork, packaging and README. Budget UL 4200A testing if selling |
| C22 | EU: GPSR 2023/988 general safety duty; Batteries Regulation 2023/1542; EN IEC 62115 as the accessibility yardstick | [ComplianceGate EU button cell](https://www.compliancegate.com/button-coin-battery-regulations-european-union/); [QIMA EN IEC 62115](https://blog.qima.com/lab-testing/guide-to-en-iec-62115-standard) | Same physical door design satisfies both markets; keep a safety-assessment note in the technical file |
| C23 | Ship the cell installed (UN 3091 / PI 970) rather than loose (UN 3090) | [DHL lithium metal regs](https://mydhl.express.dhl/content/dam/downloads/global/en/lithium-batteries/lithium_metal_batteries_regulations.pdf.coredownload.pdf); [UN 3091 button cells in equipment](https://wrap-tds.com/un-3091-lithium-metal-button-cells-contained-in-equipment-by-international-air-within-limits-below/) | Assembly/packing instruction: cell fitted, tab pull or insulator, UN 38.3-tested branded cells only |
| C24 | Firmware derived from OpenHaystack / macless-haystack is AGPL-3.0 | [OpenHaystack README](https://github.com/seemoo-lab/openhaystack); [macless-haystack](https://github.com/dchristl/macless-haystack) | Firmware ships AGPL-3.0-or-later if derived; record provenance per file; publish complete corresponding source |
| C25 | OSHWA certification requires all creator-controlled parts open and third-party chip datasheets publicly shareable | [OSHWA requirements](https://certification.oshwa.org/requirements.html) | Select an nRF52 module whose datasheet is public and redistributable; avoid NDA-only parts |
| C26 | Running any hosted service (report relay, owner-info page) makes the project a GDPR controller | GDPR Art. 25/Art. 5; §8.1 | Prefer a serverless design; if a service is unavoidable, publish a privacy notice, minimise and time-box retention, and document the lawful basis |
| C27 | Publishing with standard cryptography raises no EAR obligation | [Linux Foundation export guide](https://www.linuxfoundation.org/resources/publications/understanding-us-export-controls-with-open-source-projects); [BIS](https://www.bis.gov/learn-support/encryption-controls/encryption-items-not-subject-to-ear) | Use standard primitives only (P-224/AES). No custom crypto. No notification needed |
| C28 | Automated retrieval of location reports sits in tension with the iCloud ToS | [iCloud T&Cs §V.B, §VI](https://www.apple.com/legal/internet-services/icloud/en/terms.html) | Warn users plainly in the README that a dedicated Apple ID may be suspended; never ship credentials; never bundle a Gatekeeper-disabling step |
| C29 | An accessory with no sound maker and non-DULT key cycling is a documented stalking device | [Positive Security "Find You"](https://positive.security/blog/find-you); [DULT threat model §4.1.4](https://www.ietf.org/archive/id/draft-ietf-dult-threat-model-05.html) | Publish `docs/ANTI-STALKING.md`; refuse stealth patches; state the buzzer is not optional; link AirGuard |
| C30 | Stalking harm is actively litigated against the market leader | [Hughes v. Apple](https://www.casemine.com/judgement/us/65f67201f0af1e2dac49b1c3); [MacRumors, 30+ suits](https://www.macrumors.com/2026/05/01/airtag-stalking-lawsuits-apple/) | Treat anti-stalking features as a product-safety requirement with the same status as the battery door, not as a checkbox |

---

## 10. Recommended licences (summary)

| Artefact | Licence | SPDX id |
|---|---|---|
| PCB, schematic, mechanical CAD, BOM | CERN Open Hardware Licence v2 — Strongly Reciprocal | `CERN-OHL-S-2.0` |
| Firmware (if derived from OpenHaystack lineage) | GNU Affero GPL v3 or later | `AGPL-3.0-or-later` |
| Firmware (if written clean) | GNU GPL v3 or later; AGPL-3.0-or-later if any networked component | `GPL-3.0-or-later` |
| Host tools / scripts (clean) | Apache License 2.0 (express patent grant + retaliation) | `Apache-2.0` |
| Host tools derived from macless-haystack / findmy.py | GNU Affero GPL v3 or later | `AGPL-3.0-or-later` |
| Documentation, renders, photos | Creative Commons Attribution-ShareAlike 4.0 | `CC-BY-SA-4.0` |
| Certification layer | OSHWA self-certification (free, annual renewal, per-product UID) | — |

Repository hygiene: `LICENSES/` with full texts, SPDX headers in every file, `THIRD-PARTY.md` for vendored
code, `TRADEMARKS.md` with the Apple disclaimer, and a `docs/ANTI-STALKING.md` linked from the README's
first screen.

---

## 11. Open items / not verified in this pass

1. **Apple patent on the shell-as-diaphragm speaker** — not located. Needs a professional patent search.
2. **Apple patent on the twist-lock battery door** — not located (the quarter-turn housing patents found
   belong to Elevation Lab and cover aftermarket cases).
3. **EU Batteries Regulation 2023/1542 Article 11** exact text and application date — EUR-Lex fetches
   returned empty; verify directly.
4. **Current OJEU citation dates** for EN 300 328 / EN 301 489-17 / EN 62479 under RED — the EC page serves
   the list as a downloadable PDF/XLS which was not parsed.
5. **Apple Developer Program License Agreement** clauses (private API use) — not fetched; relevant only if
   a companion app ships.
6. **FCC §15.249** limits — not fetched; moot if a §15.247-certified module is used.
7. **Whether Apple technically blocks or rate-limits unregistered OpenHaystack keys** — searched, nothing
   found. Recorded as NOT FOUND, not as "no".
8. Some sources used are secondary (compliance consultancies, trade press). They are labelled as such
   inline. Anything load-bearing should be re-verified against the primary text before it drives a
   spend or a public claim.
