# 08 — Local positioning for halo: UWB ranging, BLE Channel Sounding, and the open-source landscape

Research lane H. Written 2026-09-03. Every claim below carries a link and a fetch date;
where a number is my own arithmetic on cited inputs it is labelled **[derived]**; where I
could not confirm something it is labelled **unverified**.

**Scope note.** This lane started as "which UWB chip talks to an iPhone". Decision **D1**
(DECISIONS.md) changed the question: halo ships as two variants from one design —
`halo-core` (BLE only, the open product) and `halo-uwb` (BLE plus a ranging radio, for
Leif's own sensor fleet). For `halo-uwb` the ranging is **halo-to-halo**, so parts are
chosen on ranging accuracy, current draw and CR2032 feasibility. iPhone interoperability is
reported separately in §7 as a known gap, not as a selection criterion.

---

## 1. Headline verdict — the single most valuable number

**Bluetooth Channel Sounding on an nRF54L-class part reaches useful accuracy for
room-scale fleet self-location, and it is cheaper and better-sourced than any UWB option.**

The best independent measurement I found is a 2026 peer-reviewed-track paper from TH Köln
that built **eight CR2032-powered CS devices on the Nordic nRF54L15** and ranged them
pairwise over 0.5–5.5 m:

| Scenario (1 MHz spacing, 72 channels, 120 measurements per distance per pair) | MAE | Peak | P90 | STD |
|---|---|---|---|---|
| Collision-free pair 0↔1 | **10 cm** | 25 cm | 20 cm | 12 cm |
| Collision-free pair 2↔3 | **6 cm** | 25 cm | 16 cm | 9 cm |
| Collision-stress pair 4↔5 (24 overlapping channels) | 14 cm | 331 cm | 27 cm | 29 cm |
| Collision-stress pair 6↔7 | 13 cm | 309 cm | 28 cm | 20 cm |

> "Under collision stress, peak errors increase from 25 cm to over 300 cm and STD more than
> doubles." — Schex, Cremer, Dettmar, *Connectionless Bluetooth Channel Sounding via PAwR for
> Scalable and Energy-Efficient Ranging*, arXiv:2605.17094v2, Table I.
> <https://arxiv.org/abs/2605.17094> (fetched 2026-09-03; local copy
> `research/fetched/H-cs-pawr-arxiv-2605.17094.md`)

That is **6–10 cm mean, 16–20 cm at P90**, from a "proof-of-concept" IFFT estimator that the
authors explicitly say "is not presented as an accuracy benchmark" — i.e. this is a floor,
not a ceiling. It sits inside the same band as UWB two-way ranging (§4: 7.7–14 cm 2D).

**The caveats are as important as the number, and all four are load-bearing:**

1. **Line of sight, static, tripod-mounted, low-multipath, ≤5.5 m.** The same paper's setup
   section: two tripods, 0.5–5.5 m, devices at 140/156 cm height.
2. **Channel collisions destroy it.** Without deterministic channel assignment, peak error
   goes 25 cm → 331 cm. In a fleet of halos all ranging at once this is *the* failure mode,
   and the paper's contribution is precisely the scheduler that avoids it.
3. **Orientation is a first-order error term and is barely studied.** The first published
   study of it (Sep 2026) reports that "device orientation has a substantial effect on CS
   ranging accuracy" and cites prior work showing "single-antenna configurations can produce
   errors of several meters depending on how the device is oriented"; an IMU-fed Random Forest
   recovered 74.6 % of the MAE. Bapat & Nagaraj, arXiv:2609.00650, <https://arxiv.org/abs/2609.00650>
   (fetched 2026-09-03). A halo is a coin-cell puck that will sit at an arbitrary angle.
4. **Hobbyist reproduction is much worse than the lab.** A published nRF54L15 evaluation
   reports "overall jitter in any method was 60–120 cm, even when the mean distance was
   right", that "phase slope tended to over-estimate distance by 20–30 %", and that "the hopes
   of '20 cm precision' using single PCB antennas aren't realistic in this configuration".
   element14 Presents ep. 691, <https://community.element14.com/challenges-projects/element14-presents/project-videos/w/documents/71994/how-accurate-is-bluetooth-channel-sounding-a-deep-dive-with-the-nrf54l15----episode-691>
   — **caveat: this page 403s/times out to automated fetch; the quotes above come from a search-engine
   extract of it on 2026-09-03 and I could not read the primary page. Treat as secondary until re-read.**

Nordic's own sample logs the three estimators disagreeing badly on one measurement:

> `I: Distance estimates on antenna path 0: ifft: 1.039173, phase_slope: 1.581897, rtt: 3.075647`
> — nRF Connect SDK `samples/bluetooth/channel_sounding/ras_initiator/README.rst`, fetched
> from `nrfconnect/sdk-nrf@main` 2026-09-03 (`research/fetched/H-ncs-cs-ras-initiator-README.rst`).

And the Bluetooth SIG's own marketing is deliberately hedged: CS "was designed to achieve
centimeter-level accuracy" with early implementations at "+/- 20 cm".
<https://www.bluetooth.com/learn-about-bluetooth/feature-enhancements/channel-sounding/> (fetched 2026-09-03).

**Verdict.** For "place my sensors in a room in a digital twin", 6–20 cm LOS / sub-metre with
multipath and arbitrary orientation is *useful* — it is a factor of 5–20 better than BLE RSSI
(§10) and good enough to say which desk, which rack, which shelf. It is **not** the sub-10 cm
guarantee that UWB TWR gives in the same room. Given that it costs **zero extra silicon**
(§13), CS is the right primary bet for `halo-uwb` v1, with UWB kept as a documented option
on the same footprint. Full recommendation in §14.

---

## 2. UWB silicon — parts, prices, sourcing

The DW3000 family is one die in four skus. The authoritative variant table (Qorvo/Decawave
DW3000 User Manual v1.1, §1.1, p.7; PDF fetched 2026-09-03 from
<https://raw.githubusercontent.com/br101/zephyr-dw3000-decadriver/master/doc/DW3000_User_Manual.pdf>,
excerpts in `research/fetched/H-dw3000-user-manual-excerpts.md`):

| IC variant | Package | PDoA support |
|---|---|---|
| DW3110 | WLCSP52 | No |
| DW3120 | WLCSP52 | Yes |
| DW3210 | QFN40 | No |
| DW3220 | QFN40 | Yes |

Same document: "QFN40 (5mm x 5 mm) and WLCSP52 (3.1 mm x 3.5 mm) package options";
"Supports UWB channels 5 and 9 (6489.6 MHz and 7987.2 MHz)"; "Data rates of 850 kb/s, and
6.8 Mb/s"; "Asset location to an accuracy of 10 cm"; "Low power consumption (suitable for
coin cell battery powered applications)".

### 2.1 Price and availability (LCSC/JLCPCB catalogue, queried 2026-09-03)

Prices USD, from the JLCPCB parts API that serves the LCSC catalogue
(`POST https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`);
raw results in `research/fetched/H-lcsc-jlcpcb-prices.md`. Cross-checked against the LCSC
product page for DW3110 (<https://www.lcsc.com/product-detail/C3040882.html>, fetched
2026-09-03: "27 units in stock", 1+ $10.2268 / 10+ $8.8141 / 30+ $7.9534 / 100+ $7.2316).

| Part | LCSC code | Package | Stock (2026-09-03) | @1 | @100 | @1000 | Verdict for halo |
|---|---|---|---|---|---|---|---|
| Qorvo DW3110TR13 | C3040882 | WLCSP52 3.1×3.5 mm | **30** | $10.16 | $7.18 | — | Cheapest DW3000; stock too thin for a 100-unit run |
| Qorvo DW3120TR13 | C22384935 | WLCSP52 | **0** | — | — | — | Not sourceable |
| Qorvo DW3210(TR13) | C5210771 / C7498845 | QFN40 5×5 | **0** | — | — | — | Not sourceable |
| Qorvo DW3220TR13 | C5441013 | QFN40 5×5 | **9** | $22.36 | $18.09 | — | 2.5× DW3110 for the PDoA die in QFN |
| DecaWave DW1000-ITR7 | C95490 | QFN48-EP 6×6 | **0** | $10.11 | $6.72 | $6.64 | Legacy; not sourceable |
| Qorvo DWM3000(TR13) module | C3028890 / C5299931 | SMD-24P 22.7×13 mm | **0** | $23.06–26.54 | $22.45 | — | Module route; 3× the chip price, and out of stock |
| Partron ACS5200HFAUWB | C224424 | SMD 8×6 mm | **0** | $1.22 | $0.78 | $0.63 | UWB chip antenna; out of stock |
| NXP SR040 / SR150 | — | — | **not in catalogue** | — | — | — | Not sourceable at LCSC at all |

**Sourcing conclusion: there is no UWB transceiver you can buy 100 of at LCSC today.** The
only line with any stock is 30× DW3110 and 9× DW3220. That is a hard constraint against
"anything in the block must be sourceable at LCSC/JLCPCB" (GOAL.md). It does not kill
`halo-uwb` — it is a private fleet variant, and DW3110 is orderable from Qorvo's store,
RFMW, Digi-Key and Mouser — but it means UWB cannot be the *default* stuffing option.

### 2.2 NXP Trimension SR040 / SR150

NXP positions SR040 explicitly at this use case:

> "The Trimension SR040 is a specialized IC for battery-operated IoT devices, including UWB
> trackers and tags. Optimized to work with small batteries such as a CR2032 coin cell."
> — NXP Trimension SR150/SR040 fact sheet, <https://iotdesignpro.com/sites/default/files/component_datasheet/ultra-wideband-IC-Datasheet.pdf>
> (fetched 2026-09-03; local copy `research/fetched/H-nxp-trimension-sr040-sr150.md`)

Same fact sheet: "6 to 8.5 GHz, 500 MHz bandwidth per channel"; "Worldwide coverage using
channels 5, 6, 8, and 9"; "Range accuracy (nLOS): ±10 cm"; "Tx peak power: more than
+10.5 dBm"; "High Rx sensitivity: -97 dBm @ 10% PER"; SR150 is "Delivered in a WLCSP68
package" with an "Arm Cortex-M33 CPU with TrustZone".

The SR150 short data sheet (Rev. 1.0, 13 Oct 2021,
<http://download.91chip.com/datasheets/NXP/SR150-datasheet.pdf>, fetched 2026-09-03) gives
the only hard current figure NXP publishes in public docs — Figure 3, "Typical system
behavior from power on to ranging": **~25 mA** in the ACTIVE/ranging state, with a
"Wake up UWB + FW loaded 600 msec" boot phase and "DPD wakeup time: ~10 ms". The 600 ms
firmware download on cold boot is a real energy tax for a duty-cycled tag; the ~10 ms
deep-power-down wake is the number that matters in steady state.

**SR040/SR150 are not in the LCSC catalogue and NXP does not publish open pricing.** NXP's
UWB software stack is also delivered under NXP licence rather than an open one. For an
open-source project this is a worse position than Qorvo's. Not recommended.

### 2.3 Current consumption — a documentation gap I could not close

I could not obtain the DW3000 or DW1000 **datasheets**, which are the only documents with the
per-state current tables. `qorvo.com` returns HTTP 429 behind a "Vercel Security Checkpoint"
to every automated fetch (verified 2026-09-03 direct, via WebFetch, and via r.jina.ai);
mouser.com, digikey.com, alldatasheet and octopart all return 403/404 to automated fetch;
archive.org was serving "Internet Archive services are temporarily offline". The Qorvo UWB
FAQ itself defers the numbers to those documents:

> "Detailed information on power consumption in the various different DW1000 states is
> available in the DW1000 Data Sheet, Application Note APS001 ('DW1000 Power Consumption') and
> APH005 ('DW1000 Power Source Selection Guide')."
> — Qorvo UWB FAQs, Wayback snapshot 2023-01-31,
> <https://web.archive.org/web/20230131001459/https://www.qorvo.com/innovation/ultra-wideband/resources/faqs>
> (fetched 2026-09-03; `research/fetched/H-qorvo-uwb-faq-archived.md`)

Two marketing-grade DW3000-vs-DW1000 energy claims circulate ("50 % less energy than DW1000",
"3.3 µA/ms for a beacon with 12 bytes of payload", "lower energy than BLE and up to 5× lower
energy than DW1000"). They appear in Qorvo/Symmetry material, but I could not open a primary
Qorvo page to quote them. **Marked unverified — do not put these in the BOM justification
until someone opens the DW3000 datasheet by hand.** The measured, independent energy numbers
in §5 are better evidence anyway.

What the FAQ *does* give, usefully, on air time (same source):

> "Depending on the preamble length and data rate used, a single message can vary between
> 190 µs (6.81 Mbps, 27 bytes, 128 preamble) to 3.4 ms (110 kbps, 27 bytes, 1024 preamble).
> This means that time to calculate a single range can vary from couple of milliseconds to
> tens of milliseconds."
> "In TDoA systems the blink frame (with preamble length of 64-symbols) and 12 octets of
> message payload, is around 110 µs. This means that RTLS system can support 1700 blinks per
> second for 1 device or 170 blinks per second for 10 devices."

---

## 3. Ranging schemes and what each costs in messages

From the DW3000 User Manual §11 and Appendix 12 (excerpts file as above):

| Scheme | Messages per range | Needs synced anchors? | Who computes | Notes from the UM |
|---|---|---|---|---|
| SS-TWR | 2 (+1 if the initiator needs the result) | No | Either end | Error "increases as Treply increases"; DW3000 "is able to measure the clock offset of the remote transmitter … to produce results that are as good as can be achieved using DS-TWR where the reply times are not too long, (i.e. < 5 ms)" |
| DS-TWR (4 msg) | 4 | No | Either end | "reduced error even for quite long response delays" |
| DS-TWR (3 msg) | 3 | No | Either end | Same estimator as 4-message |
| TDoA | 1 blink from the tag | **Yes** — "may be achieved via a wired clock distribution" | Central location engine | "The TDoA is a lower power solution as there are fewer messages involved, and this also suits higher density deployments" |
| PDoA | 1 + array | No | Anchor | Requires a PDoA die (DW3120/DW3220) and two antennas |

> "Two-way ranging (ToF) is good for proximity detection and separation alarms, especially
> when both parties in the exchange are mobile nodes." — DW3000 UM §11.

That sentence is the halo case exactly: **both parties are mobile nodes, so TWR, not TDoA.**
TDoA is the low-power scheme but it buys its power saving by putting wired, clock-synchronised
anchors on the ceiling — which is precisely the infrastructure GOAL.md says to avoid.

**Clock-offset-compensated SS-TWR is the right scheme for a halo fleet**: 2 messages per
pairwise range, no synchronisation infrastructure, accuracy equal to DS-TWR when reply times
are short. Independent confirmation: "With CC-SS-TWR, Dotlic et al. shows that it is possible
to compensate for clock offsets with only two exchanged messages. In experimental tests with
the Qorvo DW1000, the ranging error was within 15 cm at 6 m distance." (WakeLoc, §II-A,
arXiv:2504.20545, <https://arxiv.org/abs/2504.20545>, fetched 2026-09-03).

Temperature and supply matter for absolute accuracy: "Typically the reported range will vary
by 2.15 mm / °C and by 5.35 cm / VBATT" (DW1000 User Manual, quoted in the Qorvo UWB FAQ,
archived snapshot above). **5.35 cm per volt of battery droop is not negligible on a CR2032
that sags from 3.0 V to 2.4 V over life** — the block needs either a regulated rail into the
UWB die or a battery-voltage term in the antenna-delay calibration.

---

## 4. Measured UWB positioning accuracy (independent, not vendor)

| System | Radio | Setup | Result | Source |
|---|---|---|---|---|
| WakeLoc, active tag | Qorvo **DWS3000 (DW3000)** + STM32L476 | 4 anchors in an 8.6×7.6 m room, 70 tag positions, 9467 fixes, Vicon ground truth | **2D 7.7 cm** avg, σ 4.8 cm; **3D 83.5 cm** (bad z anchor placement) | arXiv:2504.20545 §V-A |
| WakeLoc, passive tag | same | same | 2D 9.1 cm, σ 6.7 cm | same |
| FlexTDOA baseline | same | same | 2D 12.9 cm, σ 6.8 cm; 3D 43.8 cm | same |
| AP-TWR (Laadung et al.) | DW1000 | — | σ < 3.1 cm active tag, 6.2 cm passive anchors (no mean error reported) | cited in arXiv:2504.20545 Table I |
| AniTrack | UWB + LoRaWAN, ETH Zurich | 5 anchors, 600 m² outdoor, **self-localizing anchors** | **2D avg 13.96 cm** at 10 s update interval | arXiv:2506.00216, <https://arxiv.org/abs/2506.00216> |
| Bitcraze Loco Positioning | DWM1000 (DW1000) | Crazyflie indoor | "an accuracy in the 10 cm range"; "Ranging accuracy ±10 cm according to DWM1000 spec" | <https://www.bitcraze.io/documentation/system/positioning/loco-positioning-system/> and <https://www.bitcraze.io/products/old-products/roadrunner/> (fetched 2026-09-03) |
| Pozyx (commercial) | UWB | — | "up to 10 cm"; UWB tags "10-30cm" | <https://www.pozyx.io/products/hardware/hardware-tags> (fetched 2026-09-03) |

**Two things generalise from this table.** First, horizontal accuracy of ~8–15 cm is what
real UWB systems deliver, not the 10 cm datasheet number and not 1 cm. Second, **vertical
accuracy collapses** whenever the anchors are roughly coplanar — WakeLoc's 3D error is
83.5 cm against a 2D error of 7.7 cm, "This error could be improved by changing the
z-placement of the anchors". A halo fleet scattered on desks and shelves will be close to
coplanar. **Plan for good x/y and poor z, in both UWB and CS.** For a digital twin this is
usually acceptable — floor and room are known from other context — but it must be stated in
the data model rather than discovered later.

Anchor count, from the two authorities: "A theoretical minimum of 4 Anchors is required to
calculate the 3D position [in TWR] … a more realistic number is 6" (Bitcraze LPS docs), and
"The tag's 3D location is yielded by the intersection of the spheres resulting from ToF
measurements to the four anchors" (DW3000 UM §11).

---

## 5. Power budget — is a UWB tag feasible on a CR2032?

**Yes, if and only if the tag is scheduled and never idle-listens.** The ranging exchange
itself is cheap; the receiver being on is what kills coin cells.

The hard, independent numbers come from WakeLoc, which instrumented a DW3000 + STM32L4 node
with a Nordic PPK2 at 100 kSps (arXiv:2504.20545, Table IV):

| Contribution | Active tag | Passive tag | Anchor |
|---|---|---|---|
| Localization energy | 217.97 µJ + N·24.88 µJ | 236.97 µJ + (N−1)·24.88 µJ | 147.87 µJ + (N−1)/2·9.66 µJ |
| Localization duration | 3.19 ms + N·210 µs | 3.15 ms + (N−1)·210 µs | 2.78 ms + (N−1)/2·230 µs |
| Sleep power | 12.05 µW | 12.05 µW | 12.05 µW |
| Wake-up-radio energy | 5.61 mJ (transmitting the wake-up call) | 6.6 µJ | 5.61 µJ |

**[derived]** For N = 5 peers, one full position fix costs the active tag
217.97 + 5×24.88 = **342.4 µJ**, in **4.24 ms** of radio time. At one fix per minute that is
342.4 µJ / 60 s = **5.7 µW** average, plus 12.05 µW sleep = **17.8 µW**. A CR2032 at
240 mAh × 3 V = 720 mWh = 2592 J gives 2592 J / 17.8 µW ≈ **4.6 years** of nominal capacity.
That matches the paper's own headline for the anchor role: "anchors can achieve a power
consumption as low as 15.53 µW while the RTLS performs one on-demand localization per minute
for 5 tags, thus operate up to 5.01 years on a single coin cell battery (690mWh)".

**Three honest deratings on that 4.6 years.** (a) CR2032 pulse behaviour: a UWB TX burst pulls
tens of mA for a few ms and a coin cell's internal resistance rises steeply as it ages — the
block needs a bulk cap (100 µF class) across the cell or the ranging will brown out long
before the mAh are gone. Nordic's own guidance for coin cells: "For a typical CR2032 cell, a
constant draw of 0.5mA or less will get pretty much all of the stated capacity. If you
increase to a constant draw of 2mA, you only get around 85% of the capacity."
(<https://blog.nordicsemi.com/getconnected/improve-battery-life-in-ultra-low-power-wireless-applications>,
via search extract 2026-09-03 — **secondary, page not directly fetched**). (b) WakeLoc's
12.05 µW sleep figure includes an ASIC wake-up radio (36–93 nW) that **does not exist as a
buyable part** — "the promising WuR of Villani et al. is not commercially available yet, the
system was emulated using WuC generated over wires via GPIO interrupts". (c) Without a
wake-up radio you must either keep a schedule (drift-bounded by a 32.768 kHz crystal) or
duty-cycle a BLE receiver to get scheduling — the latter is where the real budget goes.

The contrasting, pessimistic datapoint is **AniTrack**, a complete deployed system: "a low
average power consumption of 20.44 mW per anchor and 7.19 mW per tag, the system allows fully
battery-powered operation for up to 25 days … at a localization interval of 40 s"
(arXiv:2506.00216). 7.19 mW at 3 V is ~2.4 mA average — that would flatten a CR2032 in about
4 days. The difference is that AniTrack's tag also runs a LoRaWAN uplink and is not
wake-up-radio-gated. **Reading: the UWB ranging is not what costs the energy; the always-on
parts of the system are.**

**Conclusion for the block.** A CR2032 UWB halo ranging a handful of neighbours once a
minute is feasible on paper with a multi-year budget, but only with (i) a scheduled TDMA-style
protocol so no node idle-listens, (ii) a bulk capacitor sized for the TX pulse, and (iii) a
32.768 kHz crystal for cheap drift-bounded wake-ups. Continuous or on-demand ranging with an
open receiver is **not** CR2032-feasible.

---

## 6. UWB antennas

| Option | Part / approach | Price | Availability | Notes |
|---|---|---|---|---|
| Chip antenna | Partron **ACS5200HFAUWB**, SMD 8×6 mm | $1.22@1 / $0.78@100 / $0.63@1000 (LCSC C224424) | **stock 0** at LCSC 2026-09-03 | This is the widely-used DWM1000-class UWB chip antenna. The Qorvo FAQ confirms "the Partron chip antenna supplied with the DWM1000" but does not name the part number — **the part-number link is widely reported and not confirmed by a primary Qorvo document; unverified.** |
| PCB antenna | Copy the Qorvo DWS3000 shield | free | schematics are open | `DWS3000 Schematics.pdf` / `DWS3000_Schematics_V1_2.pdf` ship inside <https://github.com/br101/zephyr-dw3000-decadriver> and <https://github.com/foldedtoad/dwm3000> — a public, buildable reference front end for DW3000 |
| Module | Qorvo DWM3000 (24-pin SMD, 22.7×13 mm, antenna included) | $22.45–26.54 | **stock 0** at LCSC | Skips all RF layout; costs 3× the die and is not sourceable |

Qorvo's antenna warnings that matter for a coin-cell puck carried on a person (Qorvo UWB FAQ,
archived snapshot):

> "The human body introduces approximately 30 dB of insertion loss so the transmitted signal
> from the tag will be heavily attenuated … Most monopole antennas are designed to operate in
> free space (i.e. not in proximity to the body). Proximity to the body reduces antenna
> efficiency and fidelity factor. This could distort the UWB pulse and thereby give an
> incorrect range measurement."

> "Antenna delay will vary slightly between different units of the same design. Depending on
> the accuracy you require you may decide that you do not need to calibrate out this inter-unit
> difference." (see Qorvo APS014 antenna-delay calibration)

**Per-unit antenna-delay calibration is a production step.** WakeLoc did exactly this: "The
first measurements of each anchor and tag have been used for antenna delay calibration of the
DW3000." Budget a calibration fixture and a per-unit constant in OTP/flash.

---

## 7. iPhone interoperability — reported as a gap, not a criterion

D1 removes this from the selection, but the finding is worth recording because it is the
reason the original brief was wrong.

- **Nearby Interaction accessory sessions are open to third parties.** Apple publishes the
  *Nearby Interaction Accessory Protocol Specification* and the *Nearby Interaction with UWB
  Interoperability Specification*, and instructs: "Implement the Nearby Interaction accessory
  protocol with a Nearby Interaction-enabled UWB chipset to make accessories that interact
  with supported Apple products" and "Contact your UWB chipset vendor to confirm feature
  support." <https://developer.apple.com/nearby-interaction/> (fetched 2026-09-03).
- **Qorvo's DW3110 is MFi-certified for it.** "Qorvo's DW3110, an integrated Impulse Radio UWB
  wireless transceiver with Nearby Interaction firmware, has completed MFi certification …
  Qorvo UWB solutions comply with the Nearby Interaction accessory protocol."
  Qorvo press release, 2022-07-20,
  <https://www.qorvo.com/newsroom/news/2022/qorvo-uwb-solutions-certified-for-apple-u1-interoperability>
  (accessed via search extract 2026-09-03 — qorvo.com itself 429s to automated fetch;
  mirrored at <https://www.globenewswire.com/en/news-release/2022/07/20/2482615/11142/en/Qorvo-UWB-Solutions-Certified-for-Apple-U1-Interoperability.html>).
- **But Precision Finding inside the Find My app remains AirTag-only.** "UWB is something that
  Apple seems to have no interest in allowing third-party Find My trackers to support. It's an
  AirTag exclusive." Also: "the reason you won't see any trackers that support both Apple's
  Find My and Android's Find Hub networks simultaneously is that Apple's terms block this."
  9to5Google, 2026-02-15,
  <https://9to5google.com/2026/02/15/android-find-hub-trackers-uwb/> (fetched 2026-09-03).

**So:** a DW3110 halo could do UWB ranging with an iPhone *through a halo-specific iOS app
using NearbyInteraction*, subject to MFi enrolment. It could **not** light up Precision Finding
in Apple's own Find My app. For an open-source project, the MFi requirement is a licensing
wall regardless. Record as a gap; do not design for it.

---

## 8. Open-source UWB hardware and firmware

| Project | URL | Licence | Hardware | Accuracy claimed | Status (last push) |
|---|---|---|---|---|---|
| Bitcraze **lps-node-firmware** | <https://github.com/bitcraze/lps-node-firmware> | **LGPL-3.0** | DWM1000 anchor/tag node (open HW) | system "accuracy in the 10 cm range" | active, 2026-09-02 |
| Bitcraze **lps-ros** | <https://github.com/bitcraze/lps-ros> | none stated | ROS driver for LPS | — | stale, 2022-02-16 |
| Bitcraze **lps-tools** | <https://github.com/bitcraze/lps-tools> | NOASSERTION | config tooling | — | 2024-01-26 |
| Bitcraze **lps-anchor-pos-estimator** | <https://github.com/bitcraze/lps-anchor-pos-estimator> | **GPL-2.0** | — (Python) | — | **archived**; README says "The library has not been debugged and verified yet, and might not work at all" |
| br101 **zephyr-dw3000-decadriver** | <https://github.com/br101/zephyr-dw3000-decadriver> | **ISC** (own code) + **LicenseRef-Qorvo-2** (vendored driver) | DW3000, Zephyr/DTS bindings | — | active, 2026-06-02 |
| br101 **libdeca** | <https://github.com/br101/libdeca> | **LGPL-3.0** | DW3000 TWR on Zephyr / ESP-IDF / nRF-SDK 17.1 | — | active, 2026-07-14 |
| **Makerfabs-ESP32-UWB-DW3000** | <https://github.com/Makerfabs/Makerfabs-ESP32-UWB-DW3000> | **none stated** | ESP32 + DW3000 board, schematic PDF in repo | — | active, 2026-07-01 |
| **Makerfabs-ESP32-UWB** (DW1000) | <https://github.com/Makerfabs/Makerfabs-ESP32-UWB> | none stated | ESP32 + DW1000 | — | active |
| Makerfabs **nRF52840-UWB-DW3000** | <https://github.com/Makerfabs/nRF52840-UWB-DW3000> | none stated | **nRF52840 + DW3000** — closest existing analogue to halo-uwb | — | active, 2026-08-29 |
| **Fhilb/DW3000_Arduino** | <https://github.com/Fhilb/DW3000_Arduino> | see repo | DW3000 Arduino lib, alternative to Makerfabs' | — | — |
| **jremington/UWB-Indoor-Localization_Arduino** | <https://github.com/jremington/UWB-Indoor-Localization_Arduino> | none stated | ESP32_UWB tags + anchors, 2D/3D solver | — | active |
| **vacabun/uwb-twr-rtls** | <https://github.com/vacabun/uwb-twr-rtls> | none stated | Zephyr RTLS, DW1000 **and** DW3000 | — | 2024-01-17 |
| **DhamuVkl/ESP32-DWM3000-UWB-Indoor-RTLS-Tracker** | <https://github.com/DhamuVkl/ESP32-DWM3000-UWB-Indoor-RTLS-Tracker> | **GPL-3.0** | ESP32 + DWM3000 | "centimeter-level" | 2025-12-15 |
| **realzoulou/esphome-uwb-dw3000** | <https://github.com/realzoulou/esphome-uwb-dw3000> | **Apache-2.0** | ESPHome component for the Makerfabs board | — | 2026-04-22 |
| **kk9six/dw3000** | <https://github.com/kk9six/dw3000> | none stated | SS-/DS-TWR, one tag ↔ many anchors, inter-distance ranging | — | 2025-07-23 |
| **Decawave/uwb-core** | <https://github.com/Decawave/uwb-core> | (Apache-2.0 in sibling repos) | MyNewt / Linux-kernel / standalone driver, MAC + Ranging Services | — | 2022-03-01, effectively abandoned |
| Decawave **mynewt-dw1000-core / -apps** | <https://github.com/Decawave/mynewt-dw1000-core> | Apache-2.0 | DW1000 | — | **DEPRECATED** by the vendor |
| **jkelleyrtp/dw1000-rs** | <https://github.com/jkelleyrtp/dw1000-rs> | none stated | Rust `embedded-hal` DW1000 driver | — | 2026-02-18 |
| **thotro/arduino-dw1000** | <https://github.com/thotro/arduino-dw1000> | **Apache-2.0** | the original DW1000 Arduino library (★574) | — | 2024-01-16 |
| **F-Army/arduino-dw1000-ng** | <https://github.com/F-Army/arduino-dw1000-ng> | **MIT** | maintained fork | — | 2023-11-09 |
| **TIERS/dwm1001-uwb-firmware** | <https://github.com/TIERS/dwm1001-uwb-firmware> | none stated | DWM1001, "neighborhood discovery and ad-hoc ranging" | — | 2021-05-03 |
| **TIERS/dynamic-uwb-firmware** | <https://github.com/TIERS/dynamic-uwb-firmware> | **MIT** | DWM1001-DEV, ToF **and** TDoA | — | 2022-03-10 |
| **KitSprout/UWB-Node** | <https://github.com/KitSprout/UWB-Node> | NOASSERTION | STM32F411 + DWM1000 open hardware node (★162) | — | 2019 |
| **d3s-trento/contiki-uwb** | <https://github.com/d3s-trento/contiki-uwb> | none stated | Contiki + Glossy + Crystal on EVB1000/DWM1001 | — | 2026-05-12 |
| **jonathanrjpereira/DWM1001-RTLS** | <https://github.com/jonathanrjpereira/DWM1001-Real-Time-Localization-System> | **GPL-3.0** | DWM1001 anchor/tag config | — | 2021 |

**No open KiCad UWB tag design worth vendoring exists.** GitHub searches for `uwb kicad`,
`uwb hardware kicad`, `uwb anchor tag pcb open hardware` (2026-09-03) return nothing with
stars, a licence and design sources. The two 2026 repos `KaviNDU0021/PCB-UWB-DW3000-TAG_PCB`
and `KaviNDU0021/PCB-UWB-DW3000_Anchor-Indoor-Positioning` exist at ★0 with no licence. **The
halo UWB block would be the first open, licensed KiCad DW3000 tag block I can find.** The
usable open references are the Makerfabs board schematic PDFs and the Qorvo DWS3000 shield
schematic PDF vendored in br101/foldedtoad.

### 8.1 The Qorvo driver licence — read this before choosing firmware

The `dwt_uwb_driver` source that every DW3000 project vendors is **not open source**. Full
text saved at `research/fetched/H-qorvo-driver-license.txt`, from
<https://raw.githubusercontent.com/br101/zephyr-dw3000-decadriver/master/dwt_uwb_driver/LICENSES/LicenseRef-QORVO-2.txt>
(fetched 2026-09-03). It is BSD-3-Clause-shaped with two extra clauses:

> "3. You may only use this software, with or without any modification, with an integrated
> circuit developed by Qorvo US, Inc. or any of its affiliates (collectively, 'Qorvo'), or any
> module that contains such integrated circuit."
> "4. You may not reverse engineer, disassemble, decompile, decode, adapt, or otherwise attempt
> to derive or gain access to the source code to any software distributed under this license in
> binary or object code form, in whole or in part."

Clause 3 is a **field-of-use restriction**, which fails OSD §6 ("No Discrimination Against
Fields of Endeavor"), so the driver is redistributable-but-not-open-source. Practical
consequences for halo firmware (research/06 owns the final call):

- It **can** be shipped in the repo (redistribution in source form is expressly permitted with
  the notice retained), the way br101 and Zephyr do.
- It is **GPL-incompatible** — a GPL/AGPL halo firmware cannot link it and be distributed.
  `libdeca` sits on top of it under LGPL-3.0, which is coherent (LGPL for the wrapper,
  Qorvo licence for the vendored driver), but the *combined* binary still carries clause 3.
- Permissive-licensed halo firmware (Apache-2.0 / MIT) is compatible in practice, provided
  the Qorvo notice is preserved and the licence file is shipped.
- Clause 5 forbids using the Qorvo name to endorse or naming derived products "Qorvo" — so
  the block must not be called anything like "halo-Qorvo".

**By contrast, the Channel Sounding stack in nRF Connect SDK is Nordic-licensed but the
`sdk-nrf` samples are open, and there is no equivalent "our silicon only" clause in the
Zephyr Bluetooth host.** That is another quiet point for CS.

---

## 9. Bluetooth Channel Sounding — the deep dive

### 9.1 What it is

Bluetooth Core Specification v6.0 (Sept 2024) added CS as a ranging primitive combining
**Phase-Based Ranging (PBR)** and **Round-Trip Time (RTT)**:

> "Phase-Based Ranging (PBR): An initiator device sends a signal to a reflector device, which
> returns the signal. This process is repeated across multiple frequencies."
> "Round-Trip Time (RTT): An initiator device sends cryptographically scrambled packets to a
> reflector device … The distance … is then calculated based on the time it took for the
> packets to travel back and forth."
> "up to 150 meters when both devices transmit at maximum power"
> — <https://www.bluetooth.com/learn-about-bluetooth/feature-enhancements/channel-sounding/> (fetched 2026-09-03)

Channel structure, from arXiv:2605.17094 §II: "CS measurements use channels from a defined set
of **72 CS RF channels with 1 MHz spacing** in the 2.4 GHz band"; "The channel spacing Δf sets
the maximum one-way unambiguous range d_u = c/(2Δf) … giving ≈150 m at 1 MHz and ≈75 m at
2 MHz"; up to 4 antenna paths.

### 9.2 Accuracy — see §1. Summary: 6–10 cm MAE / 16–20 cm P90 LOS static; orientation and
multipath are the open risks; channel collisions must be scheduled away.

### 9.3 Power and CR2032 feasibility — measured

Same paper, Nordic PPK2 at 100 kS/s, 3 V, nRF54L15 (Ezurio BL54L15 module) on a real CR2032:

| Quantity | Value |
|---|---|
| Steady-state active charge per 1 s update cycle, connected CS baseline | 103 µC (72 ch) / 67 µC (37 ch) |
| Steady-state active charge per 1 s cycle, connectionless PAwR CS | **62 µC (72 ch) / 35 µC (37 ch)** (40 % / 48 % less) |
| PAwR sync-PDU reception, no config change | Q_sync = 1 µC |
| Config-payload reception (partner switch) | Q_cfg = 3 µC — "a reduction of approximately 98 %" vs connection-based initiation |
| Sleep | Q_sleep = 3 µC/s, from datasheet I_sleep = 2.9 µA |
| 4 measurements/cycle to 4 peers, 37 ch, 0 dBm | Q_active ≈ **79 µC per cycle** |
| Battery life on a nominal CR2032 (240 mAh, 3 V) at that workload | **≈ 4 months at T_upd = 1 s; ≈ 5 years at T_upd = 30 s** |
| Scale | "up to 14,080 active devices per PAwR train" for a four-measurement workload (single antenna path, ~40 s minimum update cycle) |

**[derived]** Per pairwise CS range at 0 dBm/37 channels: (79 − 3) µC / 4 ≈ 19 µC ≈ **57 µJ**
at 3 V. Compare the UWB marginal cost from §5: 24.88 µJ per extra peer on top of a 218 µJ
session. **Per-range energy for CS and UWB is the same order of magnitude — tens to a few
hundred µJ.** Energy is therefore *not* a reason to pick UWB over CS.

Nordic's own nRF54L15 radio figures (<https://www.nordicsemi.com/Products/nRF54L15>, fetched
2026-09-03): **RX 3.4 mA, TX 4.8 mA @ 0 dBm (at 3 V), sleep 0.7 µA to 2.9 µA @ 3 V**,
TX power +8 dBm (CSP) / +7 dBm (QFN), RX sensitivity −96 dBm (BLE 1M).
Memory: nRF54L05 0.5 MB NVM / 96 KB RAM; nRF54L10 1 MB / 192 KB; nRF54L15 1.5 MB / 256 KB.
Packages CSP47, QFN52, QFN48, QFN40, 5×5 mm to 6×6 mm, 0.4 mm pitch.

### 9.4 Which nRF54L parts actually support CS, and can I buy them?

Nordic: "The nRF54L Series has official support for Channel Sounding, with a Bluetooth
qualified host and controller available in nRF Connect SDK from v3.0.1 and onwards"
(<https://www.nordicsemi.com/Products/Wireless/Bluetooth-Low-Energy/Channel-Sounding>,
fetched 2026-09-03), listing nRF54LM20A, nRF54L15, nRF54L10, nRF54L05, nRF54H20.

Confirmed against the source of truth — `sample.yaml` of the CS RAS Initiator sample in
`nrfconnect/sdk-nrf@main` (fetched via GitHub API 2026-09-03):

```
platform_allow:
  - nrf54l15dk/nrf54l05/cpuapp
  - nrf54l15dk/nrf54l10/cpuapp
  - nrf54l15dk/nrf54l15/cpuapp
  - nrf54h20dk/nrf54h20/cpuapp
  - nrf54lm20dk/nrf54lm20a/cpuapp
  - nrf54lm20dk/nrf54lm20b/cpuapp
  - nrf54lv10dk/nrf54lv10a/cpuapp
  - nrf54lc10dk/nrf54lc10a/cpuapp
```

**nRF54L05 and nRF54L10 are explicitly allowed, and both are in stock at LCSC right now:**

| Part | LCSC | Package | Stock | @1 | @100 | @1000 |
|---|---|---|---|---|---|---|
| NRF54L05-QFAA-R | C45022042 | VFQFN-48 6×6 | **1775** | $3.22 | **$2.20** | $2.01 |
| NRF54L10-QFAA-R7 | C44800139 | VFQFN-48 6×6 | **1003** | $3.76 | **$2.59** | $2.38 |
| NRF54L15-QFAA-R | C42458750 | QFN-48 6×6 | 0 | $3.98 | $2.71 | $2.48 |
| NRF54LM20A-PAAA-R | C52078754 | — | 0 | $9.67 | — | $3.67 |

(Same source as §2.1; `research/fetched/H-lcsc-jlcpcb-prices.md`.)

**This is the decisive sourcing fact of the whole lane: a CS-capable SoC is cheaper at 100 pcs
($2.20) than a plain nRF52832 ($2.81) or nRF52833 ($3.69), is in stock in four figures, and
needs no second radio, no second antenna, no 38.4 MHz UWB reference oscillator and no
antenna-delay calibration fixture.**

Open question flagged for firmware: whether the CS host+controller and the RAS/RAP GATT
services fit in the nRF54L05's 0.5 MB NVM / 96 KB RAM alongside the OpenHaystack/Find My
advertiser, DULT behaviour and the sensor application. Nordic allows the build target, which
is evidence but not proof at application scale. **Prototype on nRF54L10 (1 MB / 192 KB, also
in stock) and only shrink to L05 if it fits.**

### 9.5 Phone support

- **Android 16 has it.** "Software support for Channel Sounding was made publicly available
  with the release of Android 16, which introduced the RangingManager API" (Nordic, above);
  Android's own docs: <https://developer.android.com/develop/connectivity/ranging>.
  Google Pixel 10 is the first phone with CS.
- **iOS has no public CS API.** Reported consistently in the Nordic DevZone thread
  <https://devzone.nordicsemi.com/f/nordic-q-a/127111/ble-channel-sounding-with-nrf54l15-which-smartphones-are-actually-supported>
  (search extract 2026-09-03 — **secondary, not directly fetched; unverified**). Android's
  ranging module instead interoperates with iOS over UWB.
- Consequence for halo: **CS gives fleet-to-fleet ranging, not phone-to-tag ranging on
  iPhone.** Since D1 scopes `halo-uwb` to Leif's own fleet, this does not bite.

### 9.6 Open CS projects

| Project | URL | Licence | Notes |
|---|---|---|---|
| nRF Connect SDK CS samples (`ras_initiator` / `ras_reflector`) | <https://github.com/nrfconnect/sdk-nrf/tree/main/samples/bluetooth/channel_sounding> | Nordic 5-clause / LicenseRef-Nordic-5-Clause | The reference implementation; logs ifft / phase_slope / rtt estimates |
| mintisan **awesome-channel-sounding** | <https://github.com/mintisan/awesome-channel-sounding> | CC-BY-4.0 | Curated index of CS vendor docs, chips and boards |
| eriklins **BT-Channel-Sounding-AT-Command** | <https://github.com/eriklins/BT-Channel-Sounding-AT-Command> | **MIT** | AT command set to set up ranging sessions and extract raw IQ data |
| Milan232323 **Bluetooth_channel_sounding_localization** | <https://github.com/Milan232323/Bluetooth_channel_sounding_localization> | none | Datasets, firmware and Python analysis for CS ranging evaluation |
| RuijieXu0408 **Bl-CS-Evaluation-Dataset** | <https://github.com/RuijieXu0408/Bl-CS-Evaluation-Dataset> | none | Ranging measurements collected with a commercial smartphone |
| navelorange93 **channel_sounding_initiator / _reflector** | <https://github.com/navelorange93/channel_sounding_initiator> | none | Silicon Labs SoC-CS test projects |
| Emrecanbl **BLE-6.0-Channel-Sounding-Distance-Tracker** | <https://github.com/Emrecanbl/BLE-6.0-Channel-Sounding-Distance-Tracker> | none | Battery-powered nRF54L15↔nRF54L15 distance tracker |
| dgorbunov **proxlock** | <https://github.com/dgorbunov/proxlock> | none | Proximity lock on nRF54L15 CS |

(All GitHub metadata queried via the GitHub API on 2026-09-03.)

Non-Nordic CS silicon, for completeness: Silicon Labs **EFR32xG24** (the only commercial CS
platform with an integrated 6-axis IMU, per arXiv:2609.00650) and NXP **MCX-W72x**.

---

## 10. The cheaper BLE fallbacks, and why they are not enough

| Technique | Reported accuracy | Source |
|---|---|---|
| BLE RSSI trilateration | mean error ≈ **3.7 m**; with filtering, 90 % of errors < 1.20 m | search-extract synthesis of Sciendo/ResearchGate trilateration studies, 2026-09-03 — **secondary, individual papers not fetched; unverified** |
| BLE RSSI fingerprinting | typically **1–2 m**; a 2025 neural-network fingerprinting approach reports mean error **1.9 m** | <https://www.sciencedirect.com/science/article/pii/S2542660525000782> (search extract, 2026-09-03) — **secondary; unverified** |
| BLE (generic, controlled environment) | "**around 0.5 m**" | AniTrack §I, arXiv:2506.00216 (primary, fetched) |
| Wi-Fi FTM / RTT | "typically accurate within **1-2 meters**"; needs 802.11mc/az APs; "three or more access points" for multilateration | <https://developer.android.com/develop/connectivity/wifi/wifi-rtt> (fetched 2026-09-03) |
| Wi-Fi (generic) | "**2.4 m**" | AniTrack §I (primary) |
| BLE 5.1 AoA | needs an antenna array on the locator side | see below |
| Bluetooth CS | **6–20 cm** LOS (§1) | arXiv:2605.17094 (primary) |
| UWB TWR | **8–15 cm** 2D (§4) | arXiv:2504.20545, arXiv:2506.00216 (primary) |

**BLE RSSI is a factor of 10–30 worse than CS and cannot place a sensor on a desk.** It is
worth implementing anyway as a zero-cost coarse prior (which room, which floor) and as a
bootstrap for grouping devices before CS ranging — arXiv:2605.17094 proposes exactly this:
"Newly joining devices can be assigned based on coarse position cues (received signal
strength, angle-of-arrival) collected at initial synchronization".

**BLE 5.1 direction finding (AoA/AoD) is the wrong shape for halo.** The tag side is cheap —
a plain BLE SoC transmitting a constant-tone extension — but the *anchor* side needs a
multi-element switched antenna array plus an RTL (real-time locating) library. That is
per-room infrastructure, which is exactly what GOAL.md rules out. Reference open
implementations, should the anchor side ever be wanted:

| Project | URL | Licence | Notes |
|---|---|---|---|
| u-blox **c209-aoa-tag** | <https://github.com/u-blox/c209-aoa-tag> | **Apache-2.0** | BLE Direction Finding tag sample, works with u-connectLocate |
| saleh-unikie **direction_finding_connectionless_rx_multiple** | <https://github.com/saleh-unikie/direction_finding_connectionless_rx_multiple> | none | Zephyr DF rx sample extended to multiple AoA tags |
| TheRyanMajd **ble-aoa-direction-finding** | <https://github.com/TheRyanMajd/ble-aoa-direction-finding> | none | BLE 5.1 DF on Silicon Labs + RTL |
| ShekharShwetank **…-Angle-of-Arrival-AoA** | <https://github.com/ShekharShwetank/Bluetooth-Direction-Finding-using-Angle-of-Arrival-AoA> | none | nRF-based DF firmware |

Antenna-array locator boards (u-blox ANT-B10, Silicon Labs BG22 AoX kits) are in the tens to
low hundreds of dollars each — **I could not fetch a current price for either and am not
quoting one; unverified.**

---

## 11. A fleet that locates itself without infrastructure

This is the part GOAL.md actually asks for: *N* halos scattered in a building, no ceiling
anchors, each learning where it is relative to the others.

### 11.1 The geometry: how many ranges are needed

- **Per node, per fix:** the DW3000 UM is explicit — "The tag's 3D location is yielded by the
  intersection of the spheres resulting from ToF measurements to the four anchors" — so **≥3
  independent ranges for 2D, ≥4 for 3D**, from nodes whose positions are already fixed.
- **Practically:** Bitcraze — "A theoretical minimum of 4 Anchors is required to calculate the
  3D position of a tag, but a more realistic number is 6 to add redundancy and accuracy".
- **For the whole graph with no anchors at all,** the distance graph must be *globally rigid*
  in the target dimension, otherwise the solution is ambiguous up to reflections and flexes.
  A complete graph on *N* nodes has N(N−1)/2 edges; a rigid graph in R^d needs at least
  dN − d(d+1)/2 edges (2N−3 in 2D, 3N−6 in 3D) **[derived from standard rigidity theory;
  I did not fetch a citable primary source for this bound in this lane — treat as a known
  result to be cited properly in the firmware spec]**. Even then the solution floats: an
  anchor-free graph fixes shape but not global position, orientation or handedness. **You need
  at least one externally-known reference** (one halo whose position is surveyed, a
  gravity vector from the accelerometer to fix "down", and ideally a compass or a second
  surveyed node to fix yaw).
- **Practical schedule:** for N ≈ 10–30 devices in a building, ranging every pair every cycle
  is O(N²) and wasteful. Range each node to its 5–8 strongest neighbours (already the natural
  set — anything further is NLOS anyway) and let the graph optimiser stitch the clusters. The
  PAwR paper's Peer-to-Peer Assignment Matrix is exactly this abstraction: "the architecture
  is not limited to the conventional tag-to-anchor pattern and also supports arbitrary
  device-to-device pairings, including tag-to-tag measurements", with the matrix changed per
  cycle so peers rotate at a cost of "ΔQ_reconf = 2 µC".

### 11.2 Open implementations of cooperative / anchor-free localization

| Project / paper | URL | Licence | What it does | Status |
|---|---|---|---|---|
| **TIERS/uwb-cooperative-mrs-localization** | <https://github.com/TIERS/uwb-cooperative-mrs-localization> | **MIT** | ROS 2 nodes, relative Monte-Carlo multi-robot localization fusing odometry + UWB ranging + spatial detections; paper arXiv:2304.06264 | 2024-05-17 |
| **bitcraze/lps-anchor-pos-estimator** | <https://github.com/bitcraze/lps-anchor-pos-estimator> | **GPL-2.0** | Solves *anchor* positions from range samples alone — the exact "the fleet surveys itself" problem. Python port of Kenneth Batstone's (LTH) MATLAB code | **archived, unverified by its own README** |
| **kalleastrom/LocoPositioningSystemSlam** | <https://github.com/kalleastrom/LocoPositioningSystemSlam> | **MIT** | SLAM over Loco Positioning ranges | 2017 |
| **MitchPalmerEngineer/TDCP-UWB** | <https://github.com/MitchPalmerEngineer/TDCP-UWB> | **MIT** | Time-differenced carrier phase GNSS + UWB ranging fusion for precise relative positioning | 2025-07-09 |
| **TIERS/dwm1001-uwb-firmware** | <https://github.com/TIERS/dwm1001-uwb-firmware> | none | "neighborhood discovery and ad-hoc ranging" firmware — the peer-discovery layer | 2021 |
| AniTrack (paper, code not released) | <https://arxiv.org/abs/2506.00216> | — | **self-localizing anchors** over 600 m², 13.96 cm 2D | 2025 |
| arXiv:2605.17094 §V (future work) | <https://arxiv.org/abs/2605.17094> | — | "aggregating the pairwise distance estimates into a cooperative measurement graph extends the architecture from ranging to indoor localization, supporting both **anchor-free relative configuration** and anchor-supported absolute positioning" | 2026 |

**Honest state of the art: there is no drop-in open-source library that takes a stream of
pairwise ranges from N coin-cell devices and returns a stable relative map.** Every citation
above is either a robotics-scale ROS package with odometry, an archived and unverified Python
port, or future work. The halo fleet solver will have to be written. It is not hard —
classical MDS for an initial embedding, then a nonlinear least-squares / factor-graph refine
(GTSAM or Ceres) with a robust kernel for NLOS outliers — but budget it as real work, and
run it **off the tag**, in Twinton.

### 11.3 What the tag should report upward

**Raw ranges, not solved positions.** Reasons, all evidenced above:

1. **Solving needs the whole graph.** No single halo sees enough of the graph to solve it,
   and the graph changes as devices move. Centralising is what the PAwR architecture does:
   the Central Orchestrator "aggregates Initiator and Reflector reports into paired data
   points for downstream processing".
2. **Estimator choice is not settled.** Nordic's own sample emits three mutually inconsistent
   estimates per measurement (ifft / phase_slope / rtt, §1); which one to trust is a function
   of quality indicators and environment. Ship the evidence, decide upstream, and keep the
   ability to reprocess history when the estimator improves.
3. **Quality metadata is small and decisive.** CS reports a per-antenna-path tone quality
   indication ("high, medium, low, or unavailable") and a Reference Power Level; UWB gives
   first-path power, RSSI, and clock-offset (COE_PPM) diagnostics. Twinton's quality labels
   depend on these.
4. **Bandwidth is not the constraint.** The PAwR paper compacts a full per-path CS result to
   "a single RPL byte followed by the stream of sorted and compacted mode-2 step data",
   3 bytes + 2 quality bits per step — "reduces the ranging-data payload by approximately
   69 %". A pairwise range summary (peer id, distance, σ, quality, timestamp) is ~16 bytes.

**Proposed uplink record** (for the firmware spec to formalise):
`{tag_id, peer_id, t_utc, method:"cs-ifft"|"cs-rtt"|"uwb-sstwr", range_mm, sigma_mm, quality, rssi_dbm, n_steps}`
plus, optionally and rarely, the raw PCT/CIR blob for offline reprocessing. The solved
position is a Twinton-side artefact with its own uncertainty, never a tag output.

---

## 12. Anti-stalking note

UWB and CS both make a tag *more* findable at close range, which cuts both ways for DULT.
The PAwR paper flags a real privacy control worth copying: WakeLoc notes "its privacy can be
preserved by sending its messages with a random MAC address as the source address". Whatever
ranging radio ships, **its identifiers must rotate on the same schedule as the Find My
advertising identifiers**, or the ranging radio becomes a stable tracking identifier that
defeats the BLE-side privacy work. Hand this to docs/ANTI-STALKING.md.

---

## 13. Cost comparison

Per-unit silicon delta over a BLE-only halo, LCSC/JLCPCB pricing 2026-09-03
(`research/fetched/H-lcsc-jlcpcb-prices.md`). Passives, crystal and antenna estimated where
noted **[derived]**.

| Configuration | Radio silicon @100 | Radio silicon @1000 | Extra parts | Δ vs BLE-only @100 | Infrastructure needed | Buyable at LCSC today? |
|---|---|---|---|---|---|---|
| **BLE-only, nRF52832** (today's AirTag-clone baseline) | $2.81 | $2.64 | 32 MHz + 32.768 kHz xtals, chip antenna | — | none (rides Find My) | yes, 41 325 in stock |
| **BLE-only, nRF52833** | $3.69 | $3.39 | same | +$0.88 | none | yes, 21 088 in stock |
| **BLE + CS, nRF54L05** | **$2.20** | **$2.01** | same crystals, same single antenna | **−$0.61** | **none** (peer-to-peer; a PAwR gateway is optional and can itself be a halo on mains) | yes, **1775 in stock** |
| **BLE + CS, nRF54L10** | $2.59 | $2.38 | same | −$0.22 | none | yes, 1003 in stock |
| **BLE + CS, nRF54L15** | $2.71 | $2.48 | same | −$0.10 | none | **stock 0** |
| **BLE + UWB, nRF52832 + DW3110** | $2.81 + $7.18 = $9.99 | — | + Partron ACS5200HFAUWB $0.78, + 38.4 MHz TCXO/xtal ≈ $0.60 **[derived estimate]**, + balun/matching + 100 µF bulk ≈ $0.30 **[derived estimate]** | **+$8.86** | none for TWR; TDoA would need wired synced anchors | **no** — 30 pcs of DW3110, 0 pcs of the antenna |
| **BLE + UWB, nRF52832 + DW3220 (PDoA)** | $2.81 + $18.09 = $20.90 | — | + 2 antennas + xtal + matching | +$19.8 | none | **no** — 9 pcs |
| **BLE + UWB module, DWM3000** | $2.81 + $22.45 = $25.26 | — | none (antenna on module) | +$22.4 | none | **no** — 0 pcs |
| BLE 5.1 AoA tag | $2.81 (tag unchanged) | — | none on the tag | $0 on the tag | **antenna-array locators per room** (price unverified, tens–hundreds of $ each) | tag yes, locators no |
| Wi-Fi FTM | n/a for a coin cell | — | — | — | 802.11mc/az APs, ≥3 in range | n/a |

**At 100 units, adding UWB costs about $8.9 per tag and cannot actually be bought; adding
Channel Sounding costs about −$0.6 per tag and is in stock.** At 1000 units the UWB gap does
not close, because Qorvo does not publish a 1000-piece break at LCSC and stock is the binding
constraint, not price.

The AirTag retail comparison from GOAL.md: Apple sells AirTag at $29. A CS-capable halo's
radio silicon is $2.20 at 100 pcs. Even with a UWB die added the radio BOM is ~$11, so the
$29 target is not the binding constraint in either configuration — **sourcing is**.

---

## 14. Recommendation for the halo block

### v1 — carry Channel Sounding, on an nRF54L-class SoC, and no second radio

1. **Make the BLE SoC an nRF54L10 (LCSC C44800139, VFQFN-48 6×6, $2.59@100, 1003 in stock).**
   It is the cheapest part in this dossier that does everything: Find My / OpenHaystack
   advertising, DULT, the sensor application, *and* Bluetooth Channel Sounding ranging with an
   officially supported Nordic host + controller. Fall back to nRF54L05 ($2.20@100, 1775 in
   stock) only after the firmware is proven to fit its 0.5 MB / 96 KB; treat nRF54L15 as the
   development part (DK availability) but note it is out of stock at LCSC.
   *Evidence:* §9.4 (sample.yaml platform_allow), §2.1/§13 (prices and stock), §9.3 (Nordic
   RX 3.4 mA / TX 4.8 mA / sleep 0.7–2.9 µA).
2. **Accept 6–20 cm LOS / sub-metre real-world as the v1 ranging spec, and say so in the
   datasheet.** Do not claim centimetres.
   *Evidence:* §1, Table I of arXiv:2605.17094 (6–10 cm MAE, 16–20 cm P90) against the
   orientation and multipath caveats of arXiv:2609.00650 and the element14 jitter report.
3. **Design the ranging protocol as scheduled, connectionless, deterministic-channel CS from
   day one.** Connection-oriented CS caps out at ~20 concurrent ACL links per SoC and costs
   ~98 % more per partner switch; random channel sequences turn a 25 cm peak error into
   331 cm once several pairs range simultaneously.
   *Evidence:* §9.3 and §1 caveat 2, arXiv:2605.17094 §§III–IV.
4. **Budget power at the 30 s update cycle, not 1 s.** Four ranges per cycle at 0 dBm gives
   ≈4 months on a CR2032 at 1 s and ≈5 years at 30 s. Room-scale asset placement does not need
   1 Hz. Make the interval a runtime parameter and let Twinton raise it when something moves.
   *Evidence:* §9.3, arXiv:2605.17094 §IV-C-6.
5. **Ship an accelerometer-derived orientation vector alongside every range.** The AirTag
   already has an accelerometer for DULT/wake; reusing it as a CS error covariate is free
   silicon and is the only published mitigation for the largest known CS error term (74.6 %
   MAE reduction).
   *Evidence:* §1 caveat 3, arXiv:2609.00650.
6. **Report raw ranges plus quality metadata upward; solve positions in Twinton.**
   *Evidence:* §11.3.

### Option — a documented UWB stuffing option on the same footprint

7. **Reserve footprint and pin budget for a Qorvo DW3110 (WLCSP52, 3.1×3.5 mm) on SPI,** with
   a Partron ACS5200HFAUWB-class chip-antenna land and a keep-out, populated only on the
   `halo-uwb-hp` (high-precision) build. Cost +$8.86/unit at 100.
   *Why DW3110 and not the others:* it is the only DW3000 sku with any LCSC stock, the
   cheapest ($7.18@100 vs $18.09 for DW3220), the smallest (WLCSP52 3.1×3.5 mm vs QFN40
   5×5 mm), and the one Qorvo MFi-certified for Nearby Interaction should that ever matter.
   PDoA (DW3120/DW3220) buys angle-of-arrival that a coin-cell puck cannot use — it needs two
   antennas and a fixed orientation.
   *Evidence:* §2.1, §2.2, §7.
8. **Use clock-offset-compensated SS-TWR, never TDoA.** Two messages per pairwise range, no
   synchronised infrastructure, accuracy equal to DS-TWR for short reply times, ~8–15 cm 2D.
   *Evidence:* §3, §4.
9. **Firmware stack for the UWB option: `br101/zephyr-dw3000-decadriver` (ISC + vendored
   Qorvo driver) + `br101/libdeca` (LGPL-3.0) on Zephyr,** the same RTOS the CS path already
   uses. Read the Qorvo licence's field-of-use clause before choosing the halo firmware
   licence — it is not OSI-open and it is GPL-incompatible.
   *Evidence:* §8, §8.1, `research/fetched/H-qorvo-driver-license.txt`.
10. **If the UWB option is built, add per-unit antenna-delay calibration and a bulk
    capacitor,** and regulate the rail into the DW3110 — reported range varies by
    "5.35 cm / VBATT" and a CR2032 sags most of a volt over its life.
    *Evidence:* §3, §6.

### Explicitly rejected

- **NXP SR040/SR150** — not in the LCSC catalogue, no public pricing, vendor-licensed stack.
  Better silicon for a tag on paper (CR2032-optimised, on-chip FiRa MAC) but unsourceable and
  unopenable. §2.2.
- **DWM3000 module** — $22.45 and stock 0; the whole point of the block is that halo does
  the RF layout once so others do not have to. §2.1.
- **UWB TDoA** — needs wired, clock-synchronised anchors. §3.
- **BLE 5.1 AoA** — needs antenna-array locators per room. §10.
- **BLE RSSI as the positioning answer** — 1.9–3.7 m; keep it only as a coarse prior and a
  clustering bootstrap. §10.
- **Designing for iPhone Precision Finding** — AirTag-exclusive, and the accessory path is
  MFi-gated. §7.

### The one experiment that would change this recommendation

Build two nRF54L10 halo prototypes, place them 1–6 m apart in Leif's actual workspace (not a
tripod in a corridor), rotate each through nine orientations, and measure P90 range error with
and without the accelerometer covariate. If P90 stays under ~40 cm with arbitrary orientation
and real furniture, CS alone settles it and the UWB footprint is never stuffed. If P90 blows
past a metre, populate DW3110 on the `-hp` build and eat the $8.86.

---

## 15. Confidence and gaps

**High confidence (primary sources fetched and quoted):** CS accuracy and energy on nRF54L15
(arXiv:2605.17094); UWB TWR accuracy and per-fix energy on DW3000 (arXiv:2504.20545);
DW3000 variant/package/channel table and TWR/TDoA scheme descriptions (DW3000 User Manual);
nRF54L05/L10/L15 CS support (sdk-nrf sample.yaml); all LCSC/JLCPCB prices and stock; the
Qorvo driver licence text; Wi-Fi RTT accuracy; Bluetooth SIG CS claims; NXP SR040/SR150
fact sheet and ~25 mA ranging current.

**Gaps I could not close in this lane:**

- **DW3000 and DW1000 per-state current tables.** qorvo.com is behind a Vercel security
  checkpoint that 429s every automated fetch; Mouser/Digi-Key/alldatasheet/octopart 403;
  archive.org was offline. Someone should open the DW3000 datasheet and APS001 by hand and
  fill in TX / RX / IDLE / SLEEP / DEEPSLEEP currents. The §5 measured energy figures are a
  usable substitute for the CR2032 decision, but the datasheet numbers belong in the spec.
- **The "DW3000 uses 50 % less energy than DW1000 / 3.3 µA/ms per beacon / lower energy than
  BLE" claims** — widely repeated, primary source not opened. **Unverified.**
- **element14 ep. 691/693 CS jitter numbers (60–120 cm)** — the page blocks automated fetch;
  quotes are from a search extract. **Secondary.**
- **iOS Channel Sounding API status** — from a DevZone thread I could not fetch directly.
  **Secondary.** Worth re-checking each iOS release.
- **BLE AoA locator hardware prices** (u-blox ANT-B10, Silabs BG22 AoX kits) — not fetched,
  not quoted.
- **BLE RSSI trilateration/fingerprinting papers** — cited via search extracts, not fetched.
  The primary claim used in the recommendation (BLE ≈ 0.5 m in controlled environments) is
  from a fetched primary source (AniTrack).
- **Whether Partron ACS5200HFAUWB is *the* DWM1000 antenna** — reported everywhere, confirmed
  only as "the Partron chip antenna" by Qorvo. **Unverified part-number link.**
- **Whether the CS stack + Find My advertiser + DULT + application fit in nRF54L05's
  0.5 MB / 96 KB.** Nordic allows the build target; that is not proof at application scale.
- **Rigidity bound (2N−3 / 3N−6 edges)** — standard result, no primary citation fetched here.

