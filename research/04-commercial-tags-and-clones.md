# Lane D — Commercial Find My tags and the clone flood: what is inside, what it costs, how it gets on the network

Research lane D for `halo`. Every claim below carries a source link and the date I fetched
it. Where I could not verify something I say **unverified** and leave it unverified — there
are no invented prices and no invented part numbers in this file.

All fetch dates: **2026-09-03** unless stated otherwise. Full source list: `research/sources.tsv`
(lane `D`). Page extracts: `research/fetched/D-01…D-05`. FCC exhibits I downloaded and read:
`images/commercial/` with `images/commercial/CATALOG.md`.

---

## 1. The one thing that decides everything: there are three doors onto the Find My network

This is the finding that should shape halo, so it goes first.

**Door 1 — Apple's Token.** A certified accessory does not carry a key it made up. Apple
assigns it. From Goodix's public FMNA design note
([goodix-ble-wiki-en.readthedocs.io](https://goodix-ble-wiki-en.readthedocs.io/latest/DesignRef/FMNA.Case/Apple%20FindMy%E6%8A%80%E6%9C%AF%E6%96%B9%E6%A1%88.html)):

> "Submit the accessory product plan on the MFi Portal to get the information assigned by
> Apple, such as PPID, Token, UUID, Product Value, Product Category."

and the Token must be

> "decoded by Base64, and stored in the accessory Flash through pre-burning in the factory
> production line."

That per-unit pre-burn is the entire commercial moat. It is what makes a tag show up in the
stock **Find My app**. Getting the right to burn it costs: MFi membership at
["USD $99 (plus any applicable taxes and fees) per membership year"](https://mfi.apple.com/en/faqs.html),
a submitted product plan, an accredited-lab quote, and per-unit royalties whose amount is
["only available under NDA"](https://mfi.apple.com/en/faqs.html) — so I cannot state it, and
nobody who can has published it.

**Door 2 — unregistered keys (OpenHaystack).** The finder iPhone never authenticates the tag.
It reads a P-224 public key out of the BLE advert, encrypts its own GPS fix to that key, and
uploads it. [seemoo-lab/openhaystack](https://github.com/seemoo-lab/openhaystack):

> "Nearby iPhones will not be able to distinguish our accessories from a genuine Apple device
> or certified accessory."

> "Apple protects their database against arbitrary access by requiring an authenticated Apple
> user to download location reports."

The gate is on the **read** side, not the tag side. Positive Security's stealth clone
confirmed the same from the attacker direction
([positive.security/blog/find-you](https://positive.security/blog/find-you)):

> "Apple devices currently have no way to distinguish genuine AirTags from clones via
> Bluetooth."

[biemster/FindMy](https://github.com/biemster/FindMy) removes even the Mac: "only a free Apple
ID is required, with SMS 2FA properly setup" to pull reports. So a Door-2 tag **is** trackable
worldwide over Apple's crowd — it just never appears in the stock Find My app, and you supply
your own app or CLI.

**Door 3 — the grey AliExpress tags, which are mostly Door 2 with a factory image.** These are
real, they work, and they are absurdly cheap. biemster's README, verbatim:

> "Lenze 17H66 is found in many 1$ tags obtained from Ali"

The teardown in [biemster/FindMy issue #14](https://github.com/biemster/FindMy/issues/14)
(user Cyl0nius, 2022-12-07, AliExpress item 1005004495296995) is the whole story of the
category in two sentences:

> "only 4 components (ST17H66, xtal and 2 capacitors) remained."
> "No capacitors at the xtal and no antenna matching at all."

and it flashed over a $2 CH340 adapter — "Flashed with STC Auto-Programmer (CH340) without any
problem", P10→TXD, P9→RXD, GND→GND, 3.3 V to Battery+ — and then "Runs with Open-Haystack-App
with no problems." Martyn Berlin repeated the buy in 2025 and also got ST17H66 parts, with the
warning that matters when sourcing from that channel: **"No guarantees that the next batch
from this supplier will be the same"**
([musings.martyn.berlin](https://musings.martyn.berlin/3-or-less-location-tracking-without-a-mac)).

**I could not verify how (or whether) any AliExpress seller obtains genuine Apple Tokens.**
I searched for leaked/over-produced MFi tokens, factory over-runs and certificate resale and
found nothing credible. The honest reading of the evidence is that the working cheap tags are
Door 2 — self-generated keys plus a vendor app — not stolen Door 1 credentials. Anyone
claiming otherwise should be asked for the artefact. **Marked unverified.**

**The fourth thing, which is not a tag at all.** Counterfeit AirTag *shells* sell for
["$3–$15 on AliExpress"](https://hotairtag.com/fake-airtag/), contain "no U1 Ultra-Wideband
chip, no Apple-certified Find My module", have "zero connection to the Find My network", and
are "a piece of plastic that does nothing." Do not conflate these with the working ST17H66
boards; the price bands overlap and the reporting constantly mixes them up.

---

## 2. What is actually inside these things

### 2.1 Apple's own AirTag — the only genuinely expensive tag in the category

| part | source |
|---|---|
| Nordic **nRF52832** (BLE + NFC), 90 nm, WLCSP50 | [TechInsights](https://www.techinsights.com/blog/apple-airtag-teardown), [Catley](https://adamcatley.com/AirTag.html) |
| Apple **U1** UWB SiP, 16 nm, die marked "TMKA75", embedded XO + Sony RF switch | TechInsights, Catley |
| Bosch **BMA280** 3-axis accelerometer | [Catley](https://adamcatley.com/AirTag.html) |
| GigaDevice **GD25LE32D** 32 Mbit NOR flash | Catley, [iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks) |
| Maxim **MAX98357A/B** class-D audio amp | Catley, iFixit |
| TI **TPS62746** buck, TI **TLV9001** op-amp, ON Semi **FPF2487** OVP load switch | Catley, iFixit |
| Panasonic **CR2032**, 225 mAh / 0.66 Wh, user-replaceable | Catley, iFixit |
| Three antennas (NFC + BLE + UWB) on **one LDS-plated plastic frame** | TechInsights ("single frame with all three antennas designed on it") |
| Speaker: **a copper voice coil with a magnet driver** — not a piezo | iFixit |

TechInsights' cost line is the only credible public BOM figure anywhere in this category:

> "estimated manufacturing cost of USD 10 (not including software costs and R&D)"

against a retail price of "less than USD 30". That is a ~3x gross markup on a $29 product.

**AirTag 2** shipped 2026-01-28 at the same price
([MacRumors, 2026-01-26](https://www.macrumors.com/2026/01/26/10-things-to-know-about-the-new-airtag-2/)):
"$29" / "a pack of four available for $99", second-generation "UWB 2" chip, Precision Finding
"1.5x further away than before" and now working on Apple Watch Series 9+/Ultra 2+, speaker "up
to 50 percent louder than the speaker in the original", "a newer Bluetooth specification with
increased range", 11.8 g (7% heavier), IP67, still CR2032, "more than a year", requires iOS
26.2.1. **No public BOM for AirTag 2 exists that I could find — unverified.**

### 2.2 Every certified third party builds the same board

I downloaded and read five FCC internal-photo exhibits. Details and page-by-page observations
are in `images/commercial/CATALOG.md` and `research/fetched/D-04-fcc-internal-photos-observed.md`.
The pattern, seen with my own eyes on the photographs:

**One BLE SoC in a small QFN or WLCSP, a printed or chip antenna, a piezo transducer, a coin
cell or small LiPo, one tact switch, on a single ~25 mm two-layer board.**

- **Chipolo ONE Spot** (FCC **2AD85-C21M**, grant 2021-05-05 — model↔ID confirmed on
  [Chipolo's own regulatory page](https://chipolo.net/en-us/pages/regulatory)): meandered
  printed trace antenna down one board edge, one dominant SoC, Panasonic Industrial CR2032,
  gold annular transducer pad on the rear. No LDS frame, no UWB, no NFC coil.
- **UGREEN FineTrack CM816** (FCC **2AQI5-CM816**, grant 2024-11-20): the test lab annotated
  it for us — two red callouts reading **"RF Chip"** (one ~4×4 mm QFN) and **"PCB Antenna"**
  (a short meander, silkscreened "UGREEN FM21-CM816 V1.0"). That is the entire radio.
- **eufy SmartTrack Link** (FCC **2AOKB-T87B0**, Anker, grant 2022-05-25): black-soldermask
  ~25 mm board, silkscreen "TTB2H-MAX-V07", UL "E358074 94V-0", and — worth noting for halo —
  **silkscreened debug pads CLK / DIO / TX / RX / GND / 3V3 left visible on a shipping
  certified product.**
- **Motorola moto tag** (FCC **IHDT6AB3**, model XT2445-1, Sporton report EP441117A
  2024-05-28): round ~26 mm PCB with lab-annotated **"UWB Antenna"** and **"BLE Antenna"** as
  two *separate* edge antennas, test pads GND / VBAT / RST / TXD / RXD / SWCLK / SWDIO, date
  code 2024-04-08, big gold piezo disc on the mating half. Even the one UWB competitor does
  not copy Apple's shared LDS frame.
- **Pebblebee Clip** (FCC **2AG5O-PB-531-BG**, grant 2023-04-04): photos public; block diagram
  and schematics filed metadata-only, i.e. withheld.

**The FCC photographs do not resolve chip markings.** Every silicon identification below comes
from a vendor press release or a third-party teardown, cited per row — not from the exhibits.

### 2.3 The SoCs, and the price band each implies

| SoC | who uses it | evidence | band |
|---|---|---|---|
| Nordic **nRF52832** | Apple AirTag gen 1; Nutale Smart Finder | [TechInsights](https://www.techinsights.com/blog/apple-airtag-teardown); [Nordic PR](https://www.nordicsemi.com/Nordic-news/2022/06/Nutale-Smart-Finder-uses-nRF52832-SoC) | premium, > nRF52810 |
| Nordic **nRF52833** | Chipolo ONE Spot | [Nordic PR](https://www.nordicsemi.com/Nordic-news/2021/07/Chipolo-ONE-Spot-uses-Nordic-nRF52833-SoC) — Chipolo COO: chosen "mainly because of its size, price performance, and memory capacity to fit the solution's firmware with all functionality needed to work with Apple Find My" | premium |
| Nordic **nRF52840** + Qorvo **DW3210** | Motorola moto tag | third-party analysis relayed in search results; the [technotrend teardown](https://technotrend.substack.com/p/motorola-moto-tag-brief-product-analysis) body is paywalled — **treat the exact part numbers as second-hand** | premium + UWB |
| Nordic **nRF52810 / nRF52811 / nRF52805** | KKM P1, P11, C2 beacons; Minew HCB22E — the cheap-beacon workhorses | [vasimv/Everytag](https://github.com/vasimv/Everytag) supported-hardware list | **verified $1.90 @1k** ([LCSC C141828](https://www.lcsc.com/product-detail/C141828.html)), $1.7977 @1k for the WLCSP ([C519278](https://www.lcsc.com/product-detail/C519278.html)) |
| **Goodix GR5513 / GR5515 / GR533x** | Goodix's own FMNA reference design | [Goodix FMNA note](https://goodix-ble-wiki-en.readthedocs.io/latest/DesignRef/FMNA.Case/Apple%20FindMy%E6%8A%80%E6%9C%AF%E6%96%B9%E6%A1%88.html) | mid |
| **Telink TLSR921x / 951x / 922x / 952x / 827x** | Telink's certified FMNA SDK targets | [Telink FindMy SDK](https://doc.telink-semi.cn/doc/en/software/res/sdk/apple_findmy/findmy_en/) — "has passed Apple Find My Network Self-Certification Test Cases certification tests" | low-mid |
| **Telink TLSR825x** | *not* an official FMNA target; community firmware only | [biemster/tlsr825x_FindMy](https://github.com/biemster/tlsr825x_FindMy) | low |
| **Lenze ST17H66 / ST17H65** | the $1 AliExpress tags | [biemster/FindMy](https://github.com/biemster/FindMy), [issue #14](https://github.com/biemster/FindMy/issues/14) | rock bottom — **unit price unverified** |

**Nordic's official Find My sample runs on nRF54L15, nRF54L10, nRF52832, nRF52833 and
nRF52840** ([nordicsemi.com](https://www.nordicsemi.com/Products/Technologies/Apple-Find-My-network))
— *not* on the cheap nRF52810/11/05. And access is gated: "You will need to have an active MFi
licence to be granted access." Nordic's page also names **Belkin and Chipolo** as customers.
For Google's side, certified FHN chipsets include nRF54L15, nRF5340, nRF52833 and nRF52832.

**I could not obtain verified unit prices for PHY6222, ST17H66, TLSR8253 or DA14531.** LCSC's
search API and oemsecrets both refused automated access this session. The ~$0.30–0.60 band
these parts are usually quoted at is **unverified here**. What *is* verified is the outcome:
[a working ST17H66 Find My tag lands at about $1 retail on AliExpress](https://github.com/biemster/FindMy).

### 2.4 The firmware footprint — this is small

Goodix, on GR551x: FMNA is **"112.7 KB + 4 KB (Token saving) = 116.7 KB"** of flash and
**"21.5 KB"** of RAM. Telink's SDK defaults to 1 MB flash "reducible to 512 KB" with 64 KB RAM.
Chipolo picked the nRF52833 (512 KB flash / 128 KB RAM) explicitly for "memory capacity to fit
the solution's firmware." So the *certified* stack wants roughly 128 KB of free flash — which
is why the cheap nRF52810 (192 KB flash) is used for beacons and emulators but not for
certified Find My.

### 2.5 What FMNA requires in hardware — the checklist nobody states plainly

From the Goodix note, the required accessory hardware is: **BLE SoC + external 32 MHz crystal
+ BLE antenna + battery with ADC voltage sensing + a G-sensor on I²C + a PWM speaker driver
and a piezo sounder.** Crypto is **software** (wolfSSL) — **no secure element is required.**
That last point is the single most useful fact for an open design: the barrier is a Token in
flash, not a tamper-resistant part you cannot buy.

---

## 3. The comparison table

`?` = not published anywhere I could fetch. **unverified** = a figure I saw but could not
confirm at its source. Speaker dB figures are vendor marketing everywhere in this category and
are measured by nobody; read them as claims.

| product | network(s) | price | SoC | battery | life | NFC | speaker | accel | UWB | size | teardown / evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Apple AirTag** (2021) | Find My | $29 / $99 4-pk | Nordic nRF52832 + Apple U1 | CR2032, replaceable | >1 yr | yes (LDS coil) | copper voice coil + magnet | Bosch BMA280 | **yes (U1)** | 31.9 × 8.0 mm, 11 g | [iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks) · [Catley](https://adamcatley.com/AirTag.html) · [TechInsights](https://www.techinsights.com/blog/apple-airtag-teardown) |
| **Apple AirTag 2** (2026-01-28) | Find My | $29 / $99 4-pk | "UWB 2" + newer BT spec; exact parts **?** | CR2032 | ">1 yr" | yes | 50% louder than gen 1 | ? | **yes (UWB 2, 1.5×)** | 31.9 × 8 mm, 11.8 g, IP67 | [MacRumors](https://www.macrumors.com/2026/01/26/10-things-to-know-about-the-new-airtag-2/) |
| **Chipolo ONE Spot** | Find My | **$28** list ($15 on sale at fetch) | Nordic nRF52833 | CR2032, replaceable | "up to 1 year" | no | "Up to 120dB" | ? | no | 37.9 mm × 6.4 mm **unverified** | FCC **2AD85-C21M** (photos in repo) · [Nordic PR](https://www.nordicsemi.com/Nordic-news/2021/07/Chipolo-ONE-Spot-uses-Nordic-nRF52833-SoC) · [chipolo.net](https://chipolo.net/en/pages/chipolo-one-spot) |
| **Chipolo CARD Spot** | Find My | ~$35 **unverified** | ? | sealed, non-replaceable | 2 yr **unverified** | no | 105 dB **unverified** | ? | no | credit-card | FCC **2AD85-C21R** |
| **Chipolo Pop** | Find My **or** Find Hub (one at a time) | $29 | Nordic nRF52-series (Nordic names Chipolo for FHN) | CR2032 | ~12 mo | no | 120 dB | ? | no | 38.8 mm disc, 10 g, IP55 | FCC **2AD85-C24W** · [HotAirTag](https://hotairtag.com/best-dual-network-trackers/) |
| **Chipolo CARD** (2025) | dual (one at a time) | ~$39 | ? | Qi rechargeable | ~1 yr | no | ~110 dB | ? | no | 2.5 mm card, IP67 | FCC **2AD85-C24R** · [HotAirTag](https://hotairtag.com/best-find-my-trackers/) |
| **Chipolo LOOP** | dual | $39 | ? | USB-C rechargeable | ~1 yr | no | 125 dB | ? | no | keyring loop, IP67 | FCC **2AD85-C24O** |
| **Pebblebee Clip** (PB-531) | Find My | ~$30 **unverified** | ? (schematics withheld) | rechargeable | ~12 mo | no | ? | ? | no | clip | FCC **2AG5O-PB-531-BG** (photos in repo) |
| **Pebblebee Clip 5 / Universal** | dual | $35 (street $29.50) | ? | USB-C rechargeable | ~12 mo | no | 97 dB + LED | ? | no | IP66 | [HotAirTag](https://hotairtag.com/best-dual-network-trackers/) |
| **Pebblebee Card 5 / Universal** | dual | $35 (street $24.99) | ? | Qi rechargeable | ~18 mo | no | ? | ? | no | 1.8 mm card, IP66 | HotAirTag |
| **Pebblebee Tag Universal** | dual | $35 | ? | rechargeable | ~8 mo | ? | ? | ? | no | ? | HotAirTag |
| **eufy SmartTrack Link** (T87B0) | Find My | **$19.99** | ? — single QFN on the board | CR2032, replaceable | "up to one year" | no | loud alarm, dB not published | ? | no | ~25 mm PCB | FCC **2AOKB-T87B0** (photos in repo) · [eufy.com](https://www.eufy.com/products/t87b0011) |
| **eufy SmartTrack Card E30** | Find My | ~$25 **unverified** | ? | sealed rechargeable | ? | no | 80 dB **unverified** | ? | no | card | FCC **2AOKB-T87B1** |
| **UGREEN FineTrack Smart Finder** (CM816) | Find My | $19.99 | ? — lab labels it only "RF Chip" | CR2032 | "up to two years" | no | 80 dB | ? | no | 1.41 × 1.41 × 0.29 in; ~25 mm PCB | FCC **2AQI5-CM816** (annotated photos in repo) · [How-To Geek](https://howtogeek.com/ugreen-finetrack-slim-review/) |
| **UGREEN FineTrack Slim** | Find My | $23.99 | ? | built-in rechargeable | ~1 yr | no | ? | ? | no | 1.7 mm card, IP68 | How-To Geek |
| **UGREEN FineTrack Duo** | dual | ? | ? | USB-C rechargeable | ? | no | ? | ? | no | ? | [MightyGadget](https://mightygadget.com/ugreen-finetrack-duo-review/) |
| **Motorola moto tag** (XT2445-1) | **Google Find Hub** | $29.99 / $99.99 4-pk | Nordic nRF52840 + Qorvo DW3210 (second-hand) | CR2032, replaceable | ~1 yr | ? | piezo disc | ? | **yes** | 31.9 × 8 mm, IP67 | FCC **IHDT6AB3** (photos in repo) · [Smartprix](https://www.smartprix.com/bytes/motorola-launches-new-bluetooth-tracker-with-google-find-my-device-support-and-uwb-technology/) |
| **Rolling Square AirCard Pro Dual** | dual | $39.90 | ? | 220 mAh Qi, 1.5 h recharge | ~12 mo | no | 20 mm buzzer | ? | no | 2.2 mm card, alu frame | [rollingsquare.com](https://rollingsquare.com/products/aircardpro-dual) |
| **KeySmart SmartCard Gen 3** | dual | $40 | "Atlas Gen 3" (vendor name only) | Qi rechargeable | ~11 mo | no | ? | ? | no | 1.8 mm, IPX8 | HotAirTag |
| **Nutale Smart Finder** | Find My | ? | Nordic **nRF52832**, BT 5.3, 4 dBm | CR2032 | >1 yr | ? | ? | yes — "built-in motion sensors" | no | ? | [Nordic PR](https://www.nordicsemi.com/Nordic-news/2022/06/Nutale-Smart-Finder-uses-nRF52832-SoC) |
| **Belkin Find My tags** | Find My | ? | Nordic (vendor-named customer only) | ? | ? | ? | ? | ? | no | ? | [Nordic](https://www.nordicsemi.com/Products/Technologies/Apple-Find-My-network) |
| **Generic AliExpress "works with Find My"** | Find My via **unregistered keys** | **~$1** (biemster) to ~$9 | **Lenze ST17H66 / ST17H65** | CR2032 | ? | no | piezo | no | no | AirTag-ish disc | [biemster #14](https://github.com/biemster/FindMy/issues/14) · [Martyn](https://musings.martyn.berlin/3-or-less-location-tracking-without-a-mac) |
| **KKM ITrack 2 "Find My"** (B2B) | Find My claimed | **$4.51–$4.91 @ MOQ 200** | KKM's beacon line uses nRF52810/52833 ([Everytag](https://github.com/vasimv/Everytag)) | CR2032 | ? | ? | ? | K4P/K5 have one | no | ? | [Alibaba B2B guide](https://electronics.alibaba.com/product/cheap-key-finder) |
| **"Smart Tag (iOS compatible)"** (B2B) | Find My claimed | **$2.22–$2.52 @ MOQ 100** | ? | ? | ? | ? | ? | ? | no | ? | Alibaba B2B guide |
| **Counterfeit AirTag shell** | **none** | $3–$15 | none | — | — | no | — | no | no | AirTag lookalike | [HotAirTag](https://hotairtag.com/fake-airtag/) |

Two structural facts the table hides:

1. **UWB is essentially absent outside Apple.** Of 20+ shipping products, exactly one
   third-party tag (moto tag, on Google's network) has it.
2. **NFC is essentially absent outside Apple too.** Apple gets it free from the nRF52832 plus
   an LDS coil; nobody else pays for the coil.

---

## 4. The grey market and the ODM layer

**The ODMs are real and they advertise openly.** [Shenzhen Kingminson
Electronic](https://kingminson.com/) sells four Find My tracker models (M15, M13, M10, M06)
plus a Find My card, self-describes as an Apple MFi-authorised manufacturer, "Since 2014",
"1,300 sqm Area", "70 people", "50+" patents, "OEM-ready", "small-batch orders". They do not
publish MOQ, prices, or their MFi ID — **their MFi status is unverified from the page itself.**

**B2B finished-tag prices** ([Alibaba's own key-finder buying
guide](https://electronics.alibaba.com/product/cheap-key-finder), quoted verbatim in
`research/fetched/D-05-volume-pricing.md`):

| product | price | MOQ | supplier |
|---|---|---|---|
| Smart Tag (iOS Compatible) | $2.22–$2.52 | 100 pcs | Shenzhen Pet Baby Technology |
| Yanyi Google Mini Pet Key Finder | $3.20–$4.50 | 1 pc | Shenzhen Yanyi Technology |
| Air Tracker Tag Bluetooth Tracker | $3.33–$54.50 | 30 pcs | Shenzhen BHD Technology |
| Trangjan Find My Hub Tracker | $3.57–$5.57 | 1 pc | Dongguan Trangjan Industrial |
| WEST Dual System MFi Tracker | $3.76–$4.09 | 5 pcs | Shenzhen WEST Technology |
| Smart GPS Tracker (replaceable battery) | $3.90–$5.50 | 1,000 pcs | Hongkong Penglian Technology |
| ITrack 2 Find My Bluetooth Tracker | $4.51–$4.91 | 200 pcs | KKM Company Limited |
| Omni IPX6 Smart Tracker | $4.40–$7.40 | 100 pcs | Shenzhen Omni Intelligent |
| HLD Tuya Tracking Device | $6.10–$6.50 | 1,000 pcs | Shenzhen Homelead Electronics |
| Kaiqisheng MFI Smart Tag GPS | $6.49–$7.99 | 50 sets | ShenZhen Kaiqisheng Technology |
| Minew Smart Key Finder Tags | $7.50–$9.99 | 3 pcs | Shenzhen Minew Technologies |

The page's own summary: wholesale pricing "typically spans **$3.30–$8.00 per unit** in the
affordable segment, with many products featuring Apple MFi certification compatibility."

**Read "MFi certification compatibility" on a B2B listing as marketing, not evidence.** The
phrase is doing the same work "Bluetooth 5.0 compatible" does. Any of these that genuinely
carry Apple Tokens are Door 1; any that don't are Door 2 with a vendor app. Nothing on the
listing tells you which, and **I found no way to distinguish them without buying one.**

**Bare PCBA / board-only prices at 1k/10k on 1688 or Taobao: not obtained.** 1688 search
results were unusable through this tooling and the Alibaba showroom URLs now return HTTP 410.
**Marked unverified — this is the largest single gap in this lane.**

**Apple crackdown history: no evidence found.** I looked for Apple blocking uncertified
accessories via iOS updates and found nothing. Positive Security's own reading is the
opposite: nothing in the protocol lets an iPhone tell a clone from an AirTag over Bluetooth.
Apple's countermeasures have gone into *unwanted-tracking alerts* (a DULT problem), not into
excluding uncertified transmitters from the crowd. Hotel Existence's assessment, quoted:
["it would be challenging for Apple to block these devices"](https://www.hotelexistence.ca/further-thoughts-on-stealth-airtags/).

---

## 5. Google's side, for a network-agnostic design

Google's [Find Hub Network Accessory Specification](https://developers.google.com/nearby/fast-pair/specifications/extensions/fmdn)
(FMDN) is an end-to-end-encrypted BLE beacon scheme on top of Fast Pair, with DULT compliance
mandatory for unwanted-tracking. Certified FHN chipsets include **nRF54L15, nRF5340, nRF52833,
nRF52832** — an almost exact overlap with Apple's list. That overlap is the whole argument for
a network-agnostic design: **one SoC serves both networks; only the firmware and the
provisioning differ.**

The market has already proven it in hardware. Every "dual" product on the table —
Chipolo Pop, Pebblebee Clip 5 / Card 5, AirCard Pro Dual, KeySmart — ships one radio and makes
you **pick a network at setup**; ["Switching networks requires a factory reset and
re-pairing"](https://hotairtag.com/best-dual-network-trackers/). None broadcast on both at once.

[vasimv/Everytag](https://github.com/vasimv/Everytag) shows there is no technical reason for
that limit: it emulates AirTag with "up to 40 public keys rotating at default 10 minutes
interval" **and** Google FMDN with a non-rotating key, on nRF52805/810/811/832/833 and
nRF54L15, "broadcasting both Airtag and FMDN" with a configurable switch interval. The
one-network-at-a-time restriction is a certification and business constraint, not a physics
one. **For an open design that never seeks certification, simultaneous dual-network
broadcasting is available and unique.**

---

## 6. The price floor

### 6.1 What the market says, from the bottom up

| tier | verified price | what you get |
|---|---|---|
| Working Find My beacon, unregistered keys | **~$1** retail on AliExpress | ST17H66 + crystal + 2 caps + printed antenna + CR2032. No app, no anti-stalking, no accelerometer, no speaker on the minimal boards. |
| No-name "iOS compatible" tag, B2B | **$2.22–$2.52** @ MOQ 100 | finished, cased, cell included |
| Credible Find My ODM tag, B2B | **$4.51–$4.91** @ MOQ 200 (KKM) | finished, cased, brandable |
| B2B "affordable segment" band | **$3.30–$8.00** | Alibaba's own characterisation |
| Cheapest certified retail brand | **$19.99** (eufy SmartTrack Link, UGREEN FineTrack) | certified, in the stock Find My app, retail channel, warranty |
| Apple AirTag / AirTag 2 | **$29** | UWB, NFC, voice-coil speaker, LDS antenna frame |
| Apple's own manufacturing cost, gen 1 | **~$10** (TechInsights) | as above |

### 6.2 A BOM reconstruction, and how far I trust it

For a certified-class board — the FMNA hardware checklist in §2.5, on an nRF52833-class SoC:

| line | figure | trust |
|---|---|---|
| BLE SoC (nRF52810 QFN, the cheapest Nordic with a verified price) | **$1.90 @ 1k** | **verified** ([LCSC C141828](https://www.lcsc.com/product-detail/C141828.html)) |
| BLE SoC (nRF52832/52833, what FMNA actually needs) | higher than the above | **unverified** — could not get a price |
| 32 MHz + 32.768 kHz crystals | ~$0.10–0.20 | **unverified** |
| I²C accelerometer (FMNA-required) | ~$0.40–0.80 | **unverified** |
| Piezo transducer | ~$0.15–0.40 | **unverified** |
| CR2032 cell + holder | ~$0.30 | **unverified** |
| Passives, tact switch, 2-layer ~25 mm PCB, printed antenna | ~$0.30 | **unverified** |
| Injection-moulded case (+ tooling, amortised) | ~$0.20–0.50 | **unverified** |

**I will not present a total as fact when six of eight lines are unverified.** What I will say
is that the reconstruction lands in the **$3.5–$5** region, and that this is *corroborated
from the other direction* by the market: finished, cased, shipped ODM tags sell B2B at
**$3.30–$8.00**, and one credible Find My ODM quotes **$4.51–$4.91 at MOQ 200**. A finished
product cannot sell below its BOM for long, so the true BOM sits somewhere just under those
numbers. That agreement between a bottom-up estimate and a top-down market price is the
strongest thing I can offer here, and it is what the number should be treated as: a
**cross-checked estimate, not a measurement.**

### 6.3 So what does the cheapest working Find My tag cost to make at volume?

**About $1 in parts for a Door-2 beacon, and about $3.5–$5 for a certified-class tag.** Both
numbers are corroborated by products you can buy today at those prices.

**Which means: halo cannot win on unit cost. That race is over and China won it.** An
ST17H66 board with four components on it is at the physical floor — you cannot design your way
below a chip, a crystal, two capacitors and a coin cell.

### 6.4 Where an open design actually undercuts Apple

The gap worth attacking is not BOM-to-BOM, it is **$10 manufacturing cost → $29 retail**, and
the three specific things Apple spends that money on:

1. **The LDS-plated three-antenna frame.** Nobody else builds one. Every certified competitor
   uses a printed trace or a chip antenna — I have the FCC photographs. Dropping LDS costs you
   NFC and costs UWB its antenna, and costs the product nothing else.
2. **The copper voice-coil speaker.** Apple is the only vendor with a real driver; everyone
   else uses a piezo and claims a bigger dB number (Chipolo LOOP claims 125 dB, Chipolo Pop and
   ONE Spot 120 dB, against Apple's unquantified one). **A piezo is louder, cheaper, thinner
   and lighter. This is a straight win.**
3. **UWB.** Only one non-Apple tag in the whole survey has it. Dropping it removes a Qorvo
   DW3xxx-class part and a second antenna, and it removes the only feature Apple genuinely has
   that the crowd network does not provide.

Beyond that, the honest list of what an open halo can offer that no product in this table
does:

- **Your own keys, your own backend, no Apple ID or Google account required for the tag
  itself** — Door 2 is a feature, not a compromise, if the user wants it.
- **Simultaneous Apple + Google broadcasting**, which every commercial dual tag refuses to do
  ([Everytag](https://github.com/vasimv/Everytag) proves it works).
- **Repairability and a documented debug header.** eufy and Motorola both ship silkscreened
  SWD/UART pads on certified products — there is no regulatory reason to hide them.
- **A published BOM and a published firmware footprint**, against a category where Pebblebee's
  schematics are withheld from the FCC record and every competitor's SoC is a guess.

And the cost of the door you cannot open for free: **$99/year MFi plus per-unit royalties
under NDA plus accredited-lab fees**, in exchange for one thing — appearing in the stock
Find My app. That is the whole trade, stated plainly, and it is the decision halo has to
make before it picks a SoC.

---

## 7. Gaps in this lane, stated honestly

1. **Bare-PCBA prices on 1688 / Taobao at 100 / 1k / 10k: not obtained.** 1688 is not fetchable
   through this tooling and Alibaba's showroom URLs 410. Someone with a Chinese account should
   redo this.
2. **Unit prices for PHY6222, ST17H66, TLSR8253, DA14531, EFR32BG22: not obtained.** LCSC's
   search API and oemsecrets refused automated access.
3. **AirTag 2 has no public BOM.** iFixit's teardown is reported second-hand
   ([MacObserver](https://www.macobserver.com/news/ifixit-airtag-2-teardown-reveals-louder-speaker-and-new-uwb-chip/));
   I did not fetch the primary teardown.
4. **No evidence found of leaked or resold Apple Find My Tokens.** Absence of evidence, stated
   as such.
5. **Chip identities on the five FCC boards are not readable in the exhibits.** All silicon
   attributions come from press releases and third-party teardowns, and the moto tag's
   nRF52840 + DW3210 in particular is second-hand from a paywalled source.
6. **Speaker dB figures are vendor claims throughout.** Nobody in this category publishes a
   measurement method.
