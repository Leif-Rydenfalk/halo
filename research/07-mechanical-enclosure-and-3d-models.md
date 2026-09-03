# 07 — Mechanical: AirTag dimensions, construction, acoustics, and every open 3D model

Research lane G. All sources fetched **2026-09-03** unless stated otherwise.
Rules followed here: no number is invented; anything not traceable to a source is marked
`unverified` or listed under "What is not published". Derived numbers show their arithmetic.

---

## 0. The three things that matter most

1. **Apple publishes a real dimensioned drawing of the AirTag, free, no login.**
   `https://developer.apple.com/download/files/accessories/dimensional-drawings/airtag.pdf`
   It gives the full revolved profile as an ordinate table plus five concentric diameters, the
   overall height to 0.01 mm, the **speaker keep-out (Ø25.75)** and the **antenna keep-out
   (Ø37.31)**. As of Accessory Design Guidelines R30 (2026-06-08) the drawings are no longer inside
   the 300-page PDF — §1.1 now says "Dimensional drawings are available at
   https://developer.apple.com/accessories/dimensional-drawings/". Apple's sheet forbids
   reproduction, so it is **not** stored in this repo; the numbers are transcribed in
   `research/fetched/G-apple-airtag-dimensional-drawing.md`.

2. **A CC BY 4.0 DXF reproduces that drawing exactly**, which gives haytag a redistributable
   geometric source. `reference/models/airtag-classicgod/airtag_dimensions.dxf` (ClassicGOD,
   Printables 629265) contains the half-section as splines and polylines whose ordinates land on
   Apple's callouts to the hundredth of a millimetre. Decoded, with the coordinate convention
   proved out, in `research/fetched/G-airtag-profile-from-dxf.md`.

3. **The speaker is a moving-coil driver with no cone**: a fixed magnet on the carrier, a bare
   copper voice coil bonded to the inside of the white shell, and the shell itself as the
   diaphragm. That is what buys Apple the height. Nobody else does it — lane D found no other
   commercial tag with a copper voice-coil speaker or an LDS antenna frame. Everyone else uses a
   piezo disc.

---

## 1. Apple's published specifications

| Feature | AirTag (2021, A2187) | AirTag 2 (2026) | Source | Confidence |
|---|---|---|---|---|
| Diameter | 1.26 in (**31.9 mm**) | 1.26 in (**31.9 mm**) | [support.apple.com/en-us/111847](https://support.apple.com/en-us/111847), [/126203](https://support.apple.com/en-us/126203) | High |
| Height | 0.31 in (**8.0 mm**) | 0.31 in (**8.0 mm**) | same | High |
| Weight | 0.39 oz (**11 g**) | 0.42 oz (**11.8 g**) | same | High |
| Ingress | **IP67**, max 1 m for 30 min, IEC 60529 | IP67, same wording | same | High |
| Operating temperature | **−20 to +60 °C** (−4 to 140 °F) | −20 to +60 °C | same | High |
| Battery | User-replaceable **CR2032** | User-replaceable CR2032 | same | High |
| Sensor | Accelerometer | (not listed on the gen-2 page) | same | High |
| Radios | BLE + Apple U1 UWB + NFC (Lost Mode) | BLE + 2nd-gen UWB + NFC | same | High |

Mechanically the two generations are the **same part envelope**. The only spec-sheet delta is
+0.8 g of mass (+7%), which the teardowns attribute to a larger voice coil and more adhesive.

---

## 2. The dimensions table

Everything below is from Apple's own drawing (dated **04/20/21** in the title block, PDF footer
2021-04-23) unless another source is named. The `z` datum is the lowest point of the steel battery
cover, on the axis; `z = 7.98` is the apex of the white dome.

### 2.1 Outer envelope — measured/published

| Feature | Value | Source | Confidence |
|---|---|---|---|
| Max outer diameter | **Ø31.87 mm** | Apple drawing, plan view | High |
| Overall height | **7.98 mm** | Apple drawing, elevation | High |
| Height at which max diameter occurs | **z = 4.34 mm** | derived from the CC BY DXF (max-radius point x = −0.007 → Ø31.875 at z = 4.339) | High |
| White shell underside lip, outer edge | **Ø28.94** at **z = 2.29** | Apple drawing + DXF LWPOLYLINE/LINE at x = 1.460 | High |
| Bore in the white shell that the steel cover sits in | **Ø27.90** and **Ø27.84** (two adjacent callouts, i.e. a small step or a draft) | Apple drawing, plan view | High for the numbers; **medium** for the interpretation — the DXF omits these two circles |
| Steel cover, outer band | **Ø25.55 / Ø25.45**, from **z = 0.88 to z = 1.89** (1.01 mm tall) | Apple drawing (Ø25.55) + DXF LWPOLYLINE x = 3.155/3.205 | High |
| Recessed band above the cover band | **Ø23.11**, from **z = 1.89 to z = 2.29** (0.40 mm tall) | Apple drawing "Ø 23.11" + DXF LWPOLYLINE x = 4.375 | High |
| Steel cover domed outer face | rises from **z = 0.00** on the axis to **z = 0.88** at Ø25.44 | DXF SPLINE (3.210, 0.880) → (15.930, 0.000) | High |
| ⇢ implied radius of that dome | **R ≈ 92 mm** — `R = c²/8h + h/2 = 25.44²/(8×0.88) + 0.44 = 91.9 + 0.44` | derived | Medium (arithmetic is exact; assumes a true spherical cap) |
| Edge chamfer | **0.05 mm all around** | Apple drawing | High |
| **Speaker keep-out** ("DO NOT OBSTRUCT THIS AREA") | **Ø25.75** | Apple drawing, note [1] | High |
| **Antenna keep-out** (radial, "no metal ... including above and below the device") | **Ø37.31** | Apple drawing, note [2] | High |
| Full revolved profile | 36 z-ordinates × 21+18 radial ordinates | Apple Detail A "PROFILE ALL AROUND"; decoded copy in `G-airtag-profile-from-dxf.md` | High |

Apple's marketing numbers (31.9 / 8.0) are the drawing's 31.87 / 7.98 rounded. **Design to 31.87
and 7.98**, not to the rounded pair, if the clone is to drop into the existing AirTag holder
ecosystem.

### 2.2 Internals — what has actually been measured by someone

| Feature | Value | Source | Confidence |
|---|---|---|---|
| PCB thickness | **0.3 mm** ("a thin (0.3mm) PCB supported by a plastic holder") | Colin O'Flynn, [Circuit Cellar](https://circuitcellar.com/research-design-hub/design-solutions/airtag-teardown-and-security-analysis/) | High |
| Internal module, fully disassembled — diameter | **26 mm** | [Adam Catley](https://adamcatley.com/AirTag.html), "smallest possible dimensions while retaining all functionality" table | High |
| Internal module, fully disassembled — height | **3.3 mm** | same | High |
| Total available PCB area | **≈ 500 mm²** — `30 mm² / 0.06` from "the radio ICs ... take up less than 30 mm2, or 6%, of the entire available PCB area" | derived from [TechInsights](https://www.techinsights.com/blog/apple-airtag-teardown) | **Low** — "less than" makes this an upper bound on the numerator |
| PCB shape | annular / "donut-shaped logic board" with the magnet + coil in the central hole | [iFixit](https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks) | High |
| PCB outer diameter | ≤ 26 mm; the board "nests inside a gilded plastic antenna frame", so it is smaller than the 26 mm module OD | inference from Catley + iFixit | **Medium** — no one has published a caliper reading |
| PCB central aperture diameter | not published | — | — |
| Battery contacts | **3**, all on the PCB/carrier side: **2 positive** (only the left one carries current; the right is sensed at ~50 nA) + 1 negative | Catley | High |
| Battery orientation | positive face **up**, toward the steel cover | [Apple support 102600](https://support.apple.com/en-me/102600) | High |
| Does the steel cover carry a battery terminal? | **No.** The AirTag chimes the instant the cell is seated, *before* the cover is refitted, and all three contacts are on the board side. The cover is retention + seal only. | inference from Apple 102600 + Catley's 3 contacts + iFixit's "battery contact pins" on side one of the board | **Medium-high** — no source says it in so many words |
| Antenna carrier | one moulded plastic piece carrying BLE (2.4 GHz), NFC (13.56 MHz) and UWB (6.5–8 GHz) antennas, **etched by Laser Direct Structuring (LDS)** and soldered to the PCB around its edge; the NFC coil has a return trace on the opposite face joined by a via at each end | Catley | High |
| NFC coil placement | "The NFC antenna is located behind the white cover", middle position of the three antennas | Catley | High |
| Shell retention | plastic tabs glued to the white plastic at **2, 6 and 10 o'clock**; iFixit finds three matching notches in the board/antenna shield "made for the clips that hold the tag together", roughly aligned with the cover clips | Catley + iFixit | High |
| Bulk capacitance on the board | **5 × 100 µF** around the edge of the top side | Catley | High |
| Cell | CR2032, Panasonic, "225 mAh and 3 V"; 0.66 Wh per iFixit | Catley, iFixit | High |
| CR2032 standard dimensions | **Ø20.0 × 3.2 mm**, 3.0 g, 220 mAh, −20 to +85 °C | [Maxell datasheet](https://biz.maxell.com/en/primary_batteries/CR2032_DataSheet_20e.pdf) | High |

### 2.3 What is **not** published anywhere

These came back empty from every teardown, blog, patent-adjacent article and Chinese report found.
They are measurement tasks for haytag, not open questions:

* Magnet dimensions (diameter, thickness), grade and pull force. iFixit calls it "a hefty central
  speaker magnet" and shows it in an X-ray; no one has measured it.
* Voice-coil dimensions: bobbin diameter, wire gauge, turns, DC resistance. Catley's pin table only
  names the two coil ends (pins 1 and 38).
* White shell wall thickness.
* Steel cover material thickness and alloy (it is described only as "polished stainless steel").
* The IP67 seal: gasket material, cross-section, groove geometry. See §6.
* PCB layer count and exact outline.
* Any AirTag 2 internal dimension at all.

---

## 3. How the AirTag is actually built

Bottom (steel side) to top (white side):

1. **Polished stainless-steel battery cover**, a shallow spherical cap ~R92, Ø25.5, 1.89 mm of
   proud height. It is retained by a **press-and-twist bayonet with three tabs**: Apple's own
   instruction is "Press down on the polished stainless steel battery cover ... and rotate
   counterclockwise until the cover stops rotating." Third-party guides describe aligning "the
   three cover tabs". Catley finds glued plastic tabs at 2, 6 and 10 o'clock; iFixit finds three
   matching notches in the board/antenna shield.
2. **CR2032**, Ø20 × 3.2 mm, positive face up against the cover, negative face down onto the board.
3. **Three battery contacts on the carrier/PCB** — two positive (one live, one sensed), one
   negative. No holder, no retainer part: the cell is clamped between the spring contacts and the
   cover. This is the single biggest height saving in the design (§5).
4. **The 0.3 mm annular PCB**, soldered to the plastic carrier — "Removing the PCB is likely to
   cause damage due to the thin PCB and being soldered to the plastic tray."
5. **The LDS antenna carrier**, a "gilded plastic antenna frame" the board nests inside, carrying
   all three antennas, soldered to the board edge at four points.
6. **The speaker magnet**, a metal disc sitting in the central hole of the donut board.
7. **The copper voice coil**, bare, "a very fragile copper voice coil lines the middle of the
   donut", terminated to the board by two solder joints (gen 1) / "two fine wires" (gen 2).
8. **The white polycarbonate shell**, glued down, doubling as the speaker diaphragm and the NFC
   window.

### 3.1 The speaker mechanism, settled

The two headline teardowns disagree in their wording and it matters, so here is the resolution.

* Catley: *"The voice coil is glued to the outer plastic shell which acts as a diaphragm. Due to
  the fixed magnet, it moves back and forth when the coil is energised."* → **moving coil.**
* iFixit: *"Power is sent to the voice coil, which drives the magnet mounted to the diaphragm."*
  → reads as **moving magnet.**

Catley is right. iFixit's own photographs show the coil "still attached via two solder joints" to
the board, and iFixit's AirTag 2 teardown describes "two fine wires leading from the speaker coil
to the PCB" — flying leads are what a *moving* coil needs and a stationary one does not. Catley
also reports that the magnet can simply be lifted out to silence the tag, which is only possible if
the magnet is the loose, non-suspended part. Design conclusion:

> **A fixed magnet on the carrier; a bare voice coil bonded to the inside of the white shell;
> flexible leads to the board; the shell is the diaphragm.**

There is no cone, no surround, no frame and no back volume component. The magnet gap is formed
between the magnet's pole face and the coil, and the "suspension" is the stiffness of the moulded
shell itself. Apple's Ø25.75 speaker keep-out is the drawing's way of saying *this is the moving
area — don't glue a holder over it.*

### 3.2 What AirTag 2 changed, mechanically

From Joseph Taylor's teardown (2026-01-28) as reported by IT之家 and from iFixit's:

* The PCB is **thinner** than gen 1's 0.3 mm (no figure given).
* The **voice coil is physically larger** — this is how Apple gets "50% louder".
* The **magnet is fixed far more firmly**; gen 1's could be pulled out with tweezers.
* **Much more adhesive** throughout; disassembly is markedly harder.
* Battery contact layout "slightly adjusted"; a QR-code-like manufacturing mark and test pads added.
* Externally identical apart from the laser engraving on the steel cover (all-caps, plus IP rating,
  Find My and NFC marks).

---

## 4. Acoustics — how to get a useful noise out of a sealed 8 mm puck

### 4.1 The measured numbers that exist

| Figure | Conditions | Source | Status |
|---|---|---|---|
| **78–80 dB** | AirTag gen 1, "one iPhone-Mini-length away" ≈ **13 cm** (iPhone 12 mini height 131.5 mm) | iFixit teardown | **Measured** — the only lab figure found |
| "50% louder" | AirTag 2 vs gen 1 | Apple marketing | Claim; **no dB, no distance**. 50% louder in *loudness* is ≈ +6 dB; 50% more *power* is ≈ +1.8 dB. Apple has not said which, so do not convert it |
| "up to 120 dB" | Chipolo ONE / ONE Point / Pop | Chipolo marketing, no distance | Claim, not comparable |
| "40 to 60 dB" | AirTag, unsourced blog | atechsland.com | **Unverified — do not use** |
| "The dinky piezoelectric speakers in the Mate and SmartTag made just as much, if not more, noise in our testing" | Tile Mate, Galaxy SmartTag vs AirTag | iFixit | Measured, qualitative |

That last line is the most important sentence in the acoustic literature on this product: **Apple's
voice coil is not louder than a piezo. It is nicer.** iFixit's read is that Apple chose it for
sound quality — "Piezo speakers are tiny and cheap, and sound like it". A clone whose brief is
"cheaper to manufacture" therefore has an easy call to make.

### 4.2 The three options, with real datasheet numbers

| Approach | Height cost | SPL you can expect | BOM | Verdict for haytag |
|---|---|---|---|---|
| **Shell-as-diaphragm moving coil** (Apple's) | **~1.5–2 mm** for magnet + coil, but zero extra diameter — the diaphragm is a part you were moulding anyway | 78–80 dB @ 13 cm (measured) | custom magnet, custom wound coil, precision coil-to-shell bonding, a Class-D amp (Maxim, per TechInsights) | Best acoustics, worst manufacturability. Needs a coil-winding and bonding operation nobody sells off the shelf |
| **Bare piezo bender bonded to the shell** | **0.22–0.54 mm** | needs a cavity + vent to be loud; the housed equivalents below bracket it | Murata **7BB-20-3** Ø20.0 × **0.22 mm**, 3.6 kHz, 500 Ω; **7BB-20-6** Ø20.0 × **0.42 mm**, 6.3 kHz, 350 Ω; **7BB-12-9** Ø12.0 × **0.22 mm**, 9.0 kHz | **The obvious clone answer.** It is the thinnest option by an order of magnitude, it is a catalogue part, and it can be bonded to the same shell Apple bonds a coil to. Needs 20–30 V p-p drive from a boost/transformer to be loud, which costs a few components and some current |
| **Housed piezo buzzer** | 3.5–11 mm | **PS1240P02CT**: Ø12.2 × **3.5 mm**, **60 dB(A) min @ 10 cm**, 4 kHz, **3 V** square wave — drives straight off the coin cell. PS1740P02C1: Ø17 × 5 mm, 60 dB(A) @ 10 cm. Everything ≥ 70 dB(A) in the TDK PS family is ≥ 6.5 mm tall | one part, one FET, no magnetics | Fits an 8 mm puck only as the 3.5 mm PS1240P02CT, and only if the stack allows it. **Exactly 60 dB(A) at 10 cm** — the brief's target, met with a catalogue part at 3 V |
| **Micro dynamic speaker** | 2 mm minimum profile, 10–18 mm across (Same Sky) | comparable to piezo at these sizes | catalogue part | Duplicates the frame, magnet, cone and back volume that Apple deletes. Wrong trade at 8 mm |

**The ~60 dB question, answered concretely.** TDK's PS1240P02CT is Ø12.2 × 3.5 mm and gives
**60 dB(A) at 10 cm from 3 V p-p square wave** in an anechoic chamber. That is a catalogue part
meeting the brief's acoustic target with no magnetics and no boost converter — but 3.5 mm is 44% of
the total 7.98 mm budget, which almost certainly does not fit alongside a 3.2 mm cell (§5). The
realistic path is the **bare bender**: a Murata 7BB-20-3 is **0.22 mm** thick and Ø20.0, it fits
inside the Ø25.75 speaker keep-out with room to spare, and bonded to the shell it reuses Apple's
own acoustic trick with a component that costs cents. Its penalty is drive voltage.

**Caveat, stated plainly**: all of the SPL figures above are anechoic, on-axis, at 10 cm, into free
air. A bender bonded into a *sealed* IP67 puck with no vent will be far quieter than its datasheet.
Apple gets away with a sealed enclosure because the whole 25.75 mm shell moves; a 20 mm bender
bonded to the same shell should behave similarly, but **this is the one thing in this document that
has to be measured on real hardware before it is believed.**

---

## 5. Design envelope for the clone

### 5.1 Targets

| Parameter | Target | Why |
|---|---|---|
| Outer diameter | **31.87 mm** (Apple's drawing value, not the rounded 31.9) | Drops into the entire existing AirTag holder ecosystem. Printables/MakerWorld holders are cut with a +0.15 to +0.30 mm margin (`reference/models/airtag-gustav-hires/Cutout 0.15mm margin.stl`, `Cutout 0.30mm margin.stl`), so a clone up to ~+0.15 mm oversize still fits most of them; anything larger does not |
| Overall height | **7.98 mm** | same |
| Widest point | z = 4.34 mm | same |
| Acoustic area to keep clear | Ø25.75 centred | Apple's own keep-out; also defines the usable diaphragm |
| Metal keep-out | Ø37.31, above and below | Apple's own antenna keep-out. Any steel cover, magnet or shield must live well inside it |
| Battery | CR2032, Ø20.0 × 3.2 mm | Ubiquity; the whole point of the product |
| Battery door | press-and-twist bayonet, three tabs | Only compliant option (§6) that costs **zero** vertical height |
| PCB | annular, **Ø ≤ 26 mm**, **0.3 mm** if copying Apple; 0.6–0.8 mm is far cheaper to fabricate | see the budget below |

### 5.2 The vertical stack budget

Four numbers are anchored to sources; everything else is the residual. The check is that the
anchored numbers close against Apple's 7.98 mm total, and they do.

| # | Layer | mm | Source / status |
|---|---|---|---|
| 1 | Steel cover, material thickness at the axis | ~0.30 | **estimate, unverified** — no published measurement |
| 2 | Clearance, cover inner face to cell | ~0.10 | estimate |
| 3 | **CR2032 cell** | **3.20** | **Anchored** — Maxell datasheet |
| 4 | Contact compression / cell-to-PCB standoff | ~0.20 | estimate |
| 5 | **PCB + carrier + magnet + voice coil (the whole "disassembled" module)** | **3.30** | **Anchored** — Catley's "Disassembled: 26 mm × 3.3 mm" |
| 6 | White shell wall + internal clearance at the apex | ~0.88 | **residual** |
| | **Total** | **7.98** | **Anchored** — Apple's drawing |

Rows 3 + 5 alone are **6.50 mm of the 7.98 mm**, i.e. **81% of the height is the cell plus the
electro-acoustic module.** That is the whole design problem in one line, and it is why:

* **There is no coin-cell holder in an AirTag.** The cheapest SMT retainer that could hold a
  CR2032 — Keystone's ultra-low-profile **1057/1057TR** — still "rise[s] 2 mm above the PCB
  surface", and standard retainers (Keystone 3002, TE/Linx BAT-HLD-001) are taller. A 2 mm
  retainer plus a 3.2 mm cell consumes ~5.2 mm of the 7.98 mm budget on one side of the board
  before a single component. **Stamped spring fingers integrated into the carrier, with the door
  supplying the clamping force, is the only scheme that fits.**
* **Nothing 3.5 mm tall fits above or below the cell.** The 3.5 mm PS1240P02CT buzzer would have to
  come out of row 5's 3.30 mm, and row 5 already contains the board and the antenna carrier. A
  **bare 0.22–0.42 mm piezo bender bonded to the shell** is the only sound generator that fits the
  budget without redesigning it.
* **The PCB thickness is worth arguing about.** Apple spends 0.3 mm on a board that "is likely to
  cause damage [when removed] due to the thin PCB". Going to a normal 0.6 mm board costs 0.3 mm out
  of row 5 or row 6 and saves real money on fabrication. That trade should be made explicitly.

### 5.3 Radial budget

| Ring | Ø (mm) | Occupant |
|---|---|---|
| 0 → 25.75 | 25.75 | speaker keep-out / moving diaphragm area (Apple) |
| ≤ 26 | 26 | Catley's full internal module OD |
| 23.11 / 25.45–25.55 | | steel cover bands |
| 27.84 / 27.90 | | shell bore that the cover seats in |
| 28.94 | | outer edge of the shell's underside lip, at z = 2.29 |
| 31.87 | | max OD at z = 4.34 |
| 37.31 | | antenna keep-out — **no metal at all inside this diameter, above or below** |

The wall between the 26 mm module and the 31.87 mm outside is `(31.87 − 26)/2 = 2.94 mm` per side
at the equator, which is where the shell's structural section, the parting line, the seal and the
bayonet lugs all have to live.

---

## 6. Enclosure, sealing and the battery door

### 6.1 The door is the hard part, and Apple already solved it

16 CFR 1263 / ANSI-UL 4200A (Reese's Law): *"Battery compartments containing replaceable button
cell or coin batteries must be secured such that they require the use of a tool or at least two
independent and simultaneous hand movements to open"* — CPSC business guidance. Lane F owns the
legal reading; the mechanical consequence is in
`research/fetched/G-moulding-cost-and-battery-door.md`. The short version:

| Option | Complies? | Height cost | Verdict |
|---|---|---|---|
| Plain snap-fit lid | **No** | — | Ruled out |
| Captive M1.6–M2 screw | Yes ("tool") | **1.5–2.5 mm** of boss depth + head, plus metal inside the antenna keep-out | Cheap to tool, unaffordable in this budget |
| Two-motion squeeze latch | Yes | ~0.5 mm | Hard to seal to IP67 |
| **Press-and-twist bayonet, 3 tabs** | **Yes** — press *and* rotate | **~0 mm**; the spring travel is absorbed by the cell compressing onto its contacts | **The answer.** Hardest to tool, only one that fits |

### 6.2 IP67 — what is known and what is not

Apple rates both generations IP67 (IEC 60529, 1 m / 30 min) and **no teardown states how**. The
evidence:

* iFixit: the assembly is "stubbornly glued in place"; their drilling advice is to aim between the
  three clips so you "only go through glue" — i.e. a continuous adhesive bead on the shell parting
  line.
* IT之家 / Joseph Taylor on AirTag 2: "a large amount of glue is used to fix the components",
  notably more than gen 1.
* A Taobao shopping-guide page claims "The original IP67 rating ... relies on a specific,
  factory-applied adhesive gasket" that prying deforms — **low-trust, unverified**, but it is the
  only public statement about the door seal and it is consistent with a compressed elastomer ring
  in the bayonet.
* Counterexample from iFixit: Samsung's SmartTag has "the thickest adhesive barrier protecting its
  circuit board" and yet carries **no** IP rating at all — adhesive alone is not a rating.

**Nobody has published the AirTag's gasket material, cross-section or groove.** For haytag this is
a design decision, not something to copy: a compressed O-ring or moulded-in-place seal in the
bayonet, plus a bonded or ultrasonically welded shell parting line, is the conventional route.

### 6.3 Moulding cost

| Route | Tooling | Piece price | Source |
|---|---|---|---|
| Aluminium prototype tool (SPI 105), 1 cavity | **$1,500–8,000**, 2–3 weeks | $2.50–6.00/part at 1 000 units | [Jaycon 2026 report](https://www.jaycon.com/2026-injection-molding-pricing-report-us-costs-reshoring-tooling-data/) |
| P20 steel (SPI 104), 1–2 cavity | $8,000–25,000, 4–6 weeks | — | same |
| Hardened steel (SPI 101), 4–32+ cavity | $60,000–150,000+, 10–14 weeks | **PC / PC-ABS $0.65** at 100 k units (4-cavity) | same |
| China, single-cavity prototype tool | **$1,000–3,000** (vs "$8,000–15,000+ at European toolmakers") | — | [Haizol 2026](https://www.haizol.com/news/china-injection-molding-industry-report-2026) |
| Protolabs entry point | "start around **$1,495**" | — | [Protolabs](https://www.protolabs.com/help-center/pricing-and-payment-options/) |
| **Two-shot (2K), single tool** | **$45,000–95,000**, 14–20 weeks | $0.43 vs $0.74 overmoulded on a modelled 50×80 mm part at 500 k/yr | [MoldMinds](https://moldminds.com/blog/overmolding-vs-insert-molding-vs-two-shot/) |

**Conclusion for a cheaper-to-manufacture clone: do not go two-shot.** A 2K tool is a $45–95 k
commitment that only repays above roughly 100–500 k units/year. Two single-material mouldings —
a PC shell and a PC or LCP carrier — plus a stamped stainless cover, is the cost-correct
architecture. First article on a $1,500–3,000 single-cavity aluminium tool; the shell in PC because
that is what Apple uses and because it is the only common resin that gives you optical white,
toughness at 0.8 mm wall, and a diaphragm stiff enough to radiate.

---

## 7. The open 3D model landscape

**No public model of the AirTag internals exists.** Every AirTag CAD file found in this survey is
an outer-envelope model built for designing holders. The internal reconstruction the brief asks
about has not been done by anyone.

Full catalogue with licences, including everything deliberately *not* downloaded, is in
`reference/models/CATALOG.md`.

| Name | URL | Format | Licence | What it models | Fidelity | Held? |
|---|---|---|---|---|---|---|
| **Apple, AirTag Dimensional Drawings** | [developer.apple.com](https://developer.apple.com/download/files/accessories/dimensional-drawings/airtag.pdf) | PDF drawing | Apple proprietary — "NOT TO REPRODUCE OR COPY IT" | The authoritative outer geometry, keep-outs, full ordinate profile | **Definitive** | Linked; numbers transcribed |
| **"Yet another AirTag model." — ClassicGOD** | [Printables 629265](https://www.printables.com/model/629265-yet-another-airtag-model) | **DXF + STEP + F3D + STL + 3MF** | **CC BY 4.0** | Full revolved envelope; the DXF is the half-section profile | **High** — reproduces Apple's callouts exactly | **Yes** |
| **"Hi Res Apple AirTag model for Fusion 360 and more" — Gustav** | [Printables 255519](https://www.printables.com/model/255519-hi-res-apple-airtag-model-for-fusion-360-and-more) | **STEP + F3D + STL** | **CC BY 4.0** | Envelope + ready-made negative solids at +0.15 and +0.30 mm margin | Medium-high; author notes it omits "the flange between battery compartment and AirTag main body" | **Yes** |
| **"Apple AirTag Model" — MediaMan3D** | [Printables 217805](https://www.printables.com/model/217805-apple-airtag-model) / [Thingiverse 4835415](https://www.thingiverse.com/thing:4835415) | STL | **CC BY 4.0** | Envelope from "Apple's dimensions of 31.9mm X 8mm and photos" | Medium — photo-derived, predates the drawing. 4 428 downloads, the community default | **Yes** |
| **"Apple AirTag Reference Model" — blake•rohde** | [Printables 460110](https://www.printables.com/model/460110-apple-airtag-reference-model) | STL + **STEP** + **keepout solids** | CC BY-**NC**-SA | Envelope **plus separate speaker and antenna keep-out bodies**, from "Accessory Design Guidelines for Apple Devices, **page 400**" | High | **No** — NC clause. Rebuild keep-outs from Ø25.75 / Ø37.31 instead |
| GrabCAD "Apple AirTag" | [grabcad.com/library/apple-airtag-2](https://grabcad.com/library/apple-airtag-2) | CAD (login required) | GrabCAD ToS | "Dimensionally accurate 3D solid model of the Apple AirTag as released April 30, 2021. Dimensions derived from Apple Accessory-Design-Guidelin[es]" | High (claimed) | No |
| GrabCAD "Apple AirTag" (sizes from Apple site) | [grabcad.com/library/apple-airtag-1](https://grabcad.com/library/apple-airtag-1) | CAD | GrabCAD ToS | "Apple AirTag Sizes from official site" | Medium | No |
| GrabCAD "AirTag - gen1" | [grabcad.com/library/airtag-gen1-1](https://grabcad.com/library/airtag-gen1-1) | CAD | GrabCAD ToS | "No internals. Enclosure only" | Medium | No |
| Cults3D "…from Official Apple Measurements (Fusion360 Source Files)" — Xuis | [cults3d.com](https://cults3d.com/en/3d-model/gadget/apple-airtag-model-from-official-apple-measurements-fusion360-source-files) | STL + F3D | Cults3D per-model | "based on the measurements in the official Apple engineering drawings" | High (claimed) | No — same lineage as the CC BY files |
| MakerWorld AirTag models/collections | [makerworld.com](https://makerworld.com/en/collections/26173553-airtag) | STL/3MF | MakerWorld terms | Holders and subtraction bodies | Envelope evidence only | No |
| Sketchfab "Airtag" | [sketchfab.com](https://sketchfab.com/3d-models/airtag-045e724fe63c4905ab580aca4b9ce669) | GLB/glTF | per-model | Appearance mesh | Low | No |
| Onshape public documents | [cad.onshape.com](https://cad.onshape.com/help/Content/Plans/public_documents.htm) | — | — | **Nothing found.** Onshape has no keyword search over public documents (their own forum confirms it), so this is "not findable", not "not present" | — | No |
| **RuuviTag enclosure — Ruuvi Innovations** | [github.com/ruuvi/mechanics](https://github.com/ruuvi/mechanics) | **STEP** (base, lid, Pro) + dimensioned PDF | **CC BY-SA 4.0** | The vendor's own production enclosure for an open-source sensor puck; also PCB-with-battery STEP models | **Definitive** (it is the vendor's file) | **Yes** (enclosure + drawing; the 44 MB PCB models linked only) |
| Espruino Puck.js case | [github.com/espruino/EspruinoBoard](https://github.com/espruino/EspruinoBoard/tree/master/Puck.js/case) | source in-repo | Espruino open hardware | The other open CR2032 puck enclosure. Larger than our envelope | Reference precedent | No |
| Community Puck.js cases | [Thingiverse 3127639](https://www.thingiverse.com/thing:3127639) | STL | per-model | Printed case for the Espruino puck | Low | No |
| RuuviTag community enclosures | [Printables 162665](https://www.printables.com/model/162665-ruuvitag-enclosure), [Thingiverse 4722400](https://www.thingiverse.com/thing:4722400), [Thingiverse 3404102](https://www.thingiverse.com/thing:3404102) | STL | per-model | Printed outdoor / wall-mount cases | Low | No |
| "Compact-tag-" — coin-cell AirTag clone | [github.com/Krish-S25/Compact-tag-](https://github.com/Krish-S25/Compact-tag-) | repo | per-repo | "Compact coin cell powered AirTag-clone" — the nearest thing to an open clone enclosure found | Unassessed | No |

**Licence note that bites**: the Ruuvi files are CC BY-**SA** 4.0. Merging Ruuvi geometry into a
haytag part propagates share-alike onto haytag's mechanical files. Use them as reference, not as
a starting body, unless haytag's mechanics are themselves CC BY-SA.

---

## 8. Open items for haytag (measurement tasks, not questions)

1. Caliper the magnet (Ø, t) and the voice coil (bobbin Ø, wire gauge, DCR) off a donor AirTag.
2. Caliper the PCB outline and central aperture; count layers off a cross-section.
3. Section the white shell to get wall thickness at apex, equator and lip.
4. Measure the steel cover thickness and identify the alloy.
5. Section the bayonet to see whether there is a discrete gasket or only adhesive.
6. Build the first haytag shell to Ø31.87 × 7.98, bond a **Murata 7BB-20-3** (Ø20.0 × 0.22 mm)
   inside it, and measure dB(A) at 10 cm against a reference AirTag. That single test decides the
   acoustic architecture.

---

## 9. Files this lane produced

* `research/07-mechanical-enclosure-and-3d-models.md` (this file)
* `research/fetched/G-apple-airtag-dimensional-drawing.md` — every number off Apple's drawing
* `research/fetched/G-airtag-profile-from-dxf.md` — the full revolved profile, decoded, redistributable
* `research/fetched/G-apple-tech-specs-airtag-1-and-2.md`
* `research/fetched/G-teardown-mechanical-quotes.md`
* `research/fetched/G-acoustics-cells-and-holders.md`
* `research/fetched/G-moulding-cost-and-battery-door.md`
* `reference/models/CATALOG.md` + 13 CC BY / CC BY-SA model files
* `images/mechanical/CATALOG.md` + 8 CC BY / CC BY-SA photographs
