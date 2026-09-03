# 10 — Precision Finding: how the "compass to your keys" actually works, and whether direction-finding is a solved open-source problem

*Research lane A extension, written 2026-09-03 in answer to Leif's question: "AirTag is like a
compass on your phone so it tells you the direction and the distance very accurately. Is this a
solved open source problem or does it remain unsolved? Apple has not released much. Reverse
engineer it."*

All fetches **2026-09-03**. Sources in `research/sources.tsv` (lane `A`). Companion:
`research/01-airtag-hardware.md` (the teardown), `docs/REFERENCE-TEARDOWN.md` (the copy target).

Confidence tags: **[primary]** I read the artefact myself · **[teardown]** a reputable teardown
asserts it · **[secondary]** credible third party · **[unverified]** not confirmed ·
**CANNOT DETERMINE** nobody has published it, and I name what would settle it.

---

## 0. The answer in one paragraph

**The AirTag has no idea which direction it is in. It cannot.** It has **exactly one UWB antenna**
and it does nothing but emit pulses. *All* of the direction-finding — the arrow, the "12 ft, to your
left" — happens **inside the iPhone**, which has a multi-antenna UWB array and measures the *phase
difference* of the same pulse arriving at each of its antennas. So the question "is direction-finding
solved in open source?" splits into two completely different questions with two opposite answers:

- **Direction from an iPhone to a non-Apple tag → NOT open, and not solvable by reverse engineering.**
  It is gated by Apple's *Nearby Interaction accessory protocol*, which is licensed to UWB chipset
  vendors, not published for us to implement. This is a business wall, not a physics wall.
- **Direction between two of our own devices (haytag ↔ haytag — which is Leif's actual use case) →
  SOLVED, and open source.** ETH Zürich's PBL published open hardware, firmware and a dataset for
  dual-antenna UWB PDoA on the Qorvo DW3220, peer-reviewed in *IEEE TIM* (2023), reporting
  **2.4° average angular accuracy** and centimetre distance. It is GPL-3.0 and still being updated.

**So for haytag: the "compass" is a solved problem in the direction that matters to you, and an
unobtainable one in the direction that only benefits Apple.**

---

## 1. The reverse-engineering finding that reframes everything

### 1.1 The AirTag has one UWB antenna — primary evidence

From Apple's own FCC certification test report (UL Verification Services, report
`12791034-E2V3`, issued 1 Oct 2020, exhibit of FCC ID **BCGA2187**), §5.2 *Description of Available
Antennas*, **verbatim** **[primary]**:

> "One integral patch antenna is employed and the antenna gains of each channel are listed as follow:"
>
> | CH | Freq. Band (GHz) | Antenna Gain (dBi) |
> |---|---|---|
> | 5 | 6.5 | −1.6 |
> | 9 | 8.0 | −0.6 |

and §5.1:

> "The EUT is a UWB portable location tracking tag with an integral antenna and operates on 6.5 GHz
> (Channel 5) and 8 GHz (Channel 9). The EUT is powered by a 3 VDC battery."

and §5.3:

> "The UWB signal is BPSK pulsed modulated signal."

Source: <https://fccid.io/BCGA2187/Test-Report/12791034-E2V3-FCC15-519-Final-Report-5130980>
(archived: `research/fetched/A-fcc-bcga2187-extracts.md`). Apple's own labelled internal photo
confirms a single **"UWB Antenna"** segment on the carrier
([`images/airtag/fcc-BCGA2187-internal-photo-6.jpg`](../images/airtag/fcc-BCGA2187-internal-photo-6.jpg)).

**One antenna. There is no array in the tag.**

### 1.2 Adam Catley reached the same conclusion by measurement

From <https://adamcatley.com/AirTag.html> (archived `research/fetched/A-catley-airtag-reverse-engineering.md`),
**verbatim** **[primary]**:

> "Testing the Precision Finding feature gives the impression that UWB is only used to measure
> distance to the AirTag, not direction. The AirTag simply transmits pulses every ~60ms from its
> single antenna. Multiple antennas are needed on either the receiver or transmitter in order to
> measure direction from phase distances."

That is the whole reverse-engineering answer in three sentences, and it is confirmed independently by
Apple's own FCC filing. **The tag is a dumb, single-antenna responder.** Its entire job is to be a
precisely-timed reflector.

### 1.3 The phone is where the compass lives

Apple's `NearbyInteraction` framework API (read from Apple's documentation JSON API,
<https://developer.apple.com/documentation/nearbyinteraction>) **[primary]** — the properties are all
on `NINearbyObject`, meaning *"Location information for a peer device"*, computed **by the user's
device about the peer**:

| API member | Apple's abstract, verbatim |
|---|---|
| `direction` | "A vector that points from the user's device in the direction of the peer device." |
| `distance` | "The distance from the user's device to the peer device in meters." |
| `horizontalAngle` | "An angle in radians that indicates the azimuthal direction to the nearby object." |
| `verticalDirectionEstimate` | "The estimation of a nearby object's vertical position as it relates to the user's device." |
| `NINearbyObjectDirectionNotAvailable` | "A value that indicates that a nearby object's direction is unavailable." |
| `NINearbyObjectAngleNotAvailable` | "A value that indicates that a nearby object's horizontal angle is unavailable." |

Framework abstract: *"Locate and interact with nearby devices using identifiers, distance, and
direction."* And, notably: *"If a session can't provide peer direction or distance, it sets the
values to [nil]."* — direction is routinely **unavailable**, which is why the AirTag UI falls back to
"keep moving" and a distance-only readout until you are close and pointing roughly right.

iFixit's U1 coverage refers to *"cutouts in the phone's steel case lining that appear to house the
necessary antennas"* (plural) and to *"UWB's multiple-antenna technology"*
(<https://www.ifixit.com/News/33257/inside-the-tech-in-apples-ultra-wideband-u1-chip>) **[teardown]**.
The **exact iPhone UWB antenna count is CANNOT DETERMINE** from public teardowns I read — what would
settle it is an iPhone FCC UWB test report's antenna table (same document class as §1.1 above) or a
U1 module X-ray. The *principle* (multi-antenna on the phone) is nonetheless established three ways:
Apple's API returns a direction vector for the peer, the physics requires ≥2 spatially separated
receive antennas, and the tag provably has only one.

---

## 2. How the direction actually gets computed (the physics you'd have to implement)

Two independent measurements are happening, and people conflate them:

**Distance — Time of Flight (ToF), specifically two-way ranging (TWR).** The phone sends a pulse, the
tag replies after a known turnaround delay, the phone divides the round-trip time by two and
multiplies by c. UWB's ~500 MHz bandwidth (FCC report §8.1) gives ~1 ns time resolution → ~30 cm per
nanosecond, and sub-nanosecond edge estimation gets you to centimetres. **This needs one antenna at
each end.** This is the part the AirTag participates in.

**Direction — Phase Difference of Arrival (PDoA), a.k.a. Angle of Arrival (AoA).** The *same* arriving
pulse hits antenna A and antenna B on the phone, separated by roughly half a wavelength (at 6.5 GHz,
λ ≈ 46 mm, so d ≈ 23 mm — which is why this fits in a phone and not in a 32 mm puck with a coin cell
in the middle). The receiver measures the **phase difference** Δφ between the two receive chains, and

  θ = arcsin( Δφ · λ / (2π · d) )

gives the angle off boresight. Two antennas give you one angle (azimuth) plus a front/back ambiguity;
three non-collinear antennas give azimuth *and* elevation and resolve the ambiguity — which is exactly
what Apple's `horizontalAngle` + `verticalDirectionEstimate` pair looks like from the outside.

**Everything hard is in the receiver:** matched RF paths, per-unit phase calibration, and
multipath/reflection rejection. That is why Apple puts the array in the $800 phone and not the $29 tag,
and it is also why Apple added **camera assistance** (ARKit fusion) in iOS 16 — visual odometry
stabilises a noisy phase estimate. Front/back ambiguity and multipath are the named failure modes in
the open literature too (§4).

---

## 3. What Apple published, and what it did not

| thing | public? | evidence |
|---|---|---|
| `NearbyInteraction` **app-side** API (`distance`, `direction`, `horizontalAngle`) | **Yes**, fully documented | <https://developer.apple.com/documentation/nearbyinteraction> **[primary]** |
| The fact that third-party accessories *can* do Precision-Finding-style interaction | **Yes** | <https://developer.apple.com/nearby-interaction/>: *"Implement the Nearby Interaction accessory protocol with a Nearby Interaction-enabled UWB chipset to make accessories that interact with supported Apple products."* **[primary]** |
| **The Nearby Interaction accessory protocol / UWB specification itself** | **No — vendor-gated.** Apple's page routes you to your silicon vendor, not to a document: *"Contact your UWB chipset vendor to confirm feature support."* and, to vendors: *"Enable Apple UWB interoperability in your chipsets by implementing the Nearby Interaction specification."* | same page **[primary]** |
| U1 silicon, its ranging protocol details, its calibration | **No.** Apple-custom, die `TMKA75`, TSMC 16 nm, USI SiP | TechInsights; `research/01` **[teardown]** |
| The tag-side protocol ("Rose" over the "Durian" L2CAP opcodes) | **Reverse-engineered by SEEMOO, not published by Apple** — opcodes `Rose Init / Rose Ready / Rose Start Ranging / Rose Ranging Complete / Rose Set Parameters / Rose Stop / Rose P2P Timestamp` | `research/fetched/A-seemoo-airtag-firmware-and-opcodes.md` **[primary]** |

**Read that table carefully — it is the crux.** Apple's model is: the app API is open, the accessory
protocol is licensed to chipset vendors under agreement, and the silicon is closed. So an open-source
project cannot legitimately implement iPhone-facing direction-finding by reverse engineering; it would
need a chipset that has already been licensed and certified for Nearby Interaction (NXP SR150-class,
Qorvo NI-enabled parts), and then the accessory-side implementation comes from the vendor's SDK, not
from us. **This is the same shape of wall as the Find My "Token" (lane D's Door 1): commercial, not
technical.**

Interestingly, the underlying radio is *not* secret: UWB ranging is standardised as
**IEEE 802.15.4z HRP**, and the AirTag uses ordinary channels 5 (6.5 GHz) and 9 (8 GHz) with BPSK
pulses. Apple's value-add is the array, the calibration, the sensor fusion and the UI — not an exotic
waveform.

---

## 4. Is direction-finding solved in open source? — the honest state of the art

### 4.1 Yes, for peer-to-peer, with published hardware and numbers

**ETH Zürich PBL — `ETH-PBL/UWB_DualAntenna_AoA`** (<https://github.com/ETH-PBL/UWB_DualAntenna_AoA>)
**[primary]** — the strongest open artefact I found. From its README, **verbatim**:

> "This repository contains the hardware of an UWB-AoA shield using the Qorvo DW3220 … Additionally
> the repository contains firmware to use the module with an STM32 and dataset as presented in the
> publication."

> "This article presents an in-depth study and assessment of angle of arrival (AoA) UWB measurements
> using a compact, low-power solution integrating a novel commercial module with phase difference of
> arrival (PDoA) estimation as integrated feature. Results demonstrate the possibility of reaching
> centimeter distance precision and **2.4° average angular accuracy** in many operative conditions,
> e.g., in a 90° range around the center. Moreover, integrating the channel impulse response, the
> phase differential of arrival, and the point-to-point distance, an error correction model is
> discussed to compensate for **reflections, multipaths, and front-back ambiguity**."

| property | value | note for haytag |
|---|---|---|
| Peer-reviewed | *IEEE Trans. Instrumentation & Measurement*, [doi:10.1109/TIM.2023.3282289](https://doi.org/10.1109/TIM.2023.3282289); preprint [arXiv:2312.13672](https://doi.org/10.48550/arXiv.2312.13672) | not a hobby claim — measured and reviewed |
| Licence | **GPL-3.0** | compatible with haytag's D4 split, but GPL is stickier than CERN-OHL-S; check before copying layout |
| Boards released | `T_module` **22 × 28 mm** (cost/size optimised) and `UWB_AoA_module` **30 × 45 mm** (performance/R&D) | 22 × 28 mm nearly fits a 32 mm puck |
| Format | **Altium** (`.PcbDoc`, `.PrjPcb`) — **not KiCad** | a real porting cost for us; lane I should know |
| Silicon | **Qorvo DW3220** — PDoA is an *integrated feature* of the part | two RX antenna ports on-chip |
| Contents | hardware + STM32 firmware + dataset + ML error-correction models | unusually complete |
| Alive? | last updated **2026-09-03** | actively maintained |

Supporting open ecosystem for the same silicon (all **[primary]**, GitHub API):
`br101/zephyr-dw3000-decadriver` (77★, Zephyr driver), `br101/libdeca` (30★, UWB library),
`br101/dw3000-decadriver-source` (34★), `ProfFan/dw3000-ng` (26★, Rust),
`Makerfabs/Makerfabs-ESP32-UWB-DW3000` (165★, cheap dev boards), plus a long tail of PDoA/AoA
experiments (`Makerfabs/UWB-AOA-with-Display`, `yws94/Unlab_SR150`, several MATLAB AoA/TDoA fusion
projects). **The drivers, the chips, the boards, the algorithms and a labelled dataset are all
public.** This is a solved problem in the engineering sense: you can buy the parts and build it.

### 4.2 No, for "make an iPhone point an arrow at my open-source tag"

I found **no** open-source implementation of the Nearby Interaction accessory protocol, and I would
not expect one to be lawful or durable if it existed. A GitHub search for `nearby interaction
accessory` returns nothing relevant **[primary]**. The path Apple offers is: use an NI-enabled
chipset (NXP SR150 / Qorvo NI parts), sign the vendor's agreement, get the accessory-side stack from
the vendor. That is incompatible with haytag's **D5 (clean-room, no MFi enrolment)**.

### 4.3 The honest caveats on the open answer

- **2.4° is "in a 90° range around the center"** — accuracy degrades off-boresight, and the paper is
  explicit that reflections, multipath and **front-back ambiguity** need an error-correction model.
  Do not quote 2.4° as an unconditional spec.
- **PDoA needs two antennas ~23 mm apart at 6.5 GHz.** In a 32 mm puck whose centre is occupied by a
  magnet and a CR2032, that is tight but not impossible; on an *embeddable block* (GOAL.md §2) the
  host board can place them. **This is a real mechanical constraint on the `haytag-uwb` variant.**
- **Power.** UWB ranging is expensive next to a 2.3 µA BLE sleep. The AirTag only powers its U1 during
  an active Precision Finding session (Catley's power traces show ~25 mA spikes). Any haytag doing
  peer ranging must duty-cycle hard. Lane H owns the budget.
- **Both ends need the hardware.** Tag-to-tag direction means *every* haytag that must be pointed at
  needs the dual-antenna front end, not just the "phone" end.

---

## 5. What this means for haytag

| capability | status | why |
|---|---|---|
| Distance from an iPhone to a haytag (UWB) | **needs an NI-enabled chipset + vendor agreement** → out of scope under D5 | Apple gates the accessory protocol |
| **Direction arrow on an iPhone pointing at a haytag** | **NOT ACHIEVABLE** as open hardware. Known gap, written down per GOAL.md | same wall |
| **Distance between two haytags** | **Solved** — standard 802.15.4z two-way ranging, single antenna each end, many open drivers | this is what the AirTag's own radio does |
| **Direction between two haytags** (Leif's actual need: where is sensor B relative to sensor A) | **SOLVED in open source** — DW3220 + PDoA, ETH-PBL hardware/firmware/dataset, 2.4° | needs 2 antennas on the *measuring* node |
| Room-scale relative position for Twinton | **Achievable** — and arguably better than Apple's, because you control both ends and can use several anchors rather than one handheld array | trilateration from 3+ ranging peers needs **no AoA at all** |

**The strategic point worth stating plainly:** Leif's stated goal in `GOAL.md` is *"to know their local
position relative to other sensors."* For that, **you may not need direction-finding at all.** With
three or more haytags that can range to each other (distance only, one antenna, cheap, low power), you
get full 3-D relative position by trilateration — which is *more* accurate and *more* robust than a
single handheld device estimating one bearing. AoA is what you need when only *one* device is doing the
measuring, i.e. Apple's phone-hunting-a-lost-key use case. **In a sensor mesh, the mesh is the array.**
So the recommendation is: build ranging first (easy, solved, cheap), and treat PDoA/AoA as an optional
`haytag-uwb-aoa` variant for the single-anchor case. Lane H should evaluate this trade explicitly.

---

## 6. Open questions this dossier could not close

| question | what would settle it | who |
|---|---|---|
| Exact iPhone UWB antenna count and geometry | an iPhone FCC UWB test report antenna table, or a U1 module X-ray | A / H |
| Whether any Qorvo/NXP part gives NI interop **without** an NDA'd vendor stack | direct vendor enquiry; the terms are not public | E / F |
| Whether DW3220's PDoA is usable at the AirTag's 32 mm diameter with a coin cell in the middle | an RF sim (ce-rf / openEMS) of two antennas at ~23 mm on a 26 mm annulus | I / T3 |
| Power cost per ranging fix on DW3220 at haytag duty cycles | bench measurement, or the ETH paper's energy section | H |
| Whether the GPL-3.0 on ETH's boards infects a derived haytag layout | read the repo's LICENSE against CERN-OHL-S (D4) | F |
| Whether Apple's `Rose` opcodes reveal a usable tag-side ranging protocol | deeper RE of a dumped AirTag firmware — legally fraught, and D5 says clean-room | (not recommended) |

Nothing above is guessed. Where a number is not in a source it says CANNOT DETERMINE and names what
would settle it.

---

## 7. Sources

- FCC ID BCGA2187, UWB test report 12791034-E2V3 — <https://fccid.io/BCGA2187/Test-Report/12791034-E2V3-FCC15-519-Final-Report-5130980> (archived `research/fetched/A-fcc-bcga2187-extracts.md`)
- FCC ID BCGA2187, internal photos — <https://fccid.io/BCGA2187/Internal-Photos/A2187-Internal-Photos-v1-0-5130978> (rendered to `images/airtag/`)
- Adam Catley, *Apple AirTag Reverse Engineering* — <https://adamcatley.com/AirTag.html> (archived `research/fetched/A-catley-airtag-reverse-engineering.md`)
- Apple, *Nearby Interaction with UWB* — <https://developer.apple.com/nearby-interaction/>
- Apple, `NearbyInteraction` / `NINearbyObject` documentation — <https://developer.apple.com/documentation/nearbyinteraction>
- SEEMOO, AirTag L2CAP "Durian"/"Rose" opcodes — <https://github.com/seemoo-lab/airtag> (archived `research/fetched/A-seemoo-airtag-firmware-and-opcodes.md`)
- Margiani, Cortesi, Keller, Vogt, Polonelli, Magno, *Angle of arrival and centimeter distance estimation on a smart UWB sensor node*, IEEE TIM 2023 — <https://doi.org/10.1109/TIM.2023.3282289>, preprint <https://doi.org/10.48550/arXiv.2312.13672>
- `ETH-PBL/UWB_DualAntenna_AoA` (GPL-3.0, Qorvo DW3220, Altium) — <https://github.com/ETH-PBL/UWB_DualAntenna_AoA>
- Open DW3000 ecosystem: <https://github.com/br101/zephyr-dw3000-decadriver>, <https://github.com/br101/libdeca>, <https://github.com/ProfFan/dw3000-ng>, <https://github.com/Makerfabs/Makerfabs-ESP32-UWB-DW3000>
- iFixit, *Inside the Tech in Apple's Ultra Wideband U1 Chip* — <https://www.ifixit.com/News/33257/inside-the-tech-in-apples-ultra-wideband-u1-chip>
