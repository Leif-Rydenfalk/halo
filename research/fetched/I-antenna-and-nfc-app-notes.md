# Antenna and NFC-coil app notes — the rules a movable block must carry
Lane I. Fetched 2026-09-03; PDFs downloaded with curl and converted with `pdftotext -layout`.

---
## TI AN043 / SWRA117D — "Small Size 2.4 GHz PCB antenna"
<https://www.ti.com/lit/an/swra117d/swra117d.pdf> (21 pp, Audun Andersen)

- *"The suggested antenna design requires **no more than 15.2 x 5.7 mm** of space and ensures a VSWR
  ratio of less than 2 across the 2.4 GHz ISM band when connected to a 50 ohm source."*
- *"The PCB antenna on the CC2511 USB dongle reference design is a **meandered Inverted F Antenna (IFA)**.
  The IFA was designed to match an impedance of 50 ohm at 2.45 GHz. Thus **no additional matching
  components are necessary**."*
- Design goal: *"A reflection of less than −10 dB across the 2.4 GHz ISM band … ensures that more than 90%
  of the available power is delivered to the antenna."*
- §4.3, the rule that governs any copied antenna, verbatim:
  > **Small changes of the antenna dimensions may have large impact on the performance. Therefore it is
  > strongly recommended to make an exact copy of the reference design to achieve optimum performance.**
  > The easiest way to implement the antenna is to **import the gerber or DXF file** showing the antenna
  > layout. … It is also recommended to **use the same thickness and type of PCB material** as used in the
  > reference design. … To compensate for a thicker/thinner PCB the antenna could be made
  > slightly shorter/longer.
- Published dimension table (Table 1): L1 3.94, L2 2.70, L3 5.00, L4 2.64, L5 2.00, L6 4.90,
  W1 0.90, W2 0.50, D1 0.50, D2 0.30, D3 0.30, D4 0.50, D5 1.40, D6 1.70 — all mm.
- **Ground-plane dependence, measured**: *"The size of the ground plane affects the performance of the PCB
  antenna. … In free space the antenna has a bandwidth of approximately **250 MHz**. When the USB dongle
  is connected to the laptop the bandwidth is reduced to around **100 MHz**, which still is enough to
  cover the whole 2.4 GHz ISM band."*
  → A quarter-wave printed antenna's tuning is a property of **the whole board it lands on**, which is
  exactly what changes when a haytag block moves into someone else's outline.

## TI AN058 / SWRA161B — "Antenna Selection Guide"
<https://www.ti.com/lit/an/swra161b/swra161b.pdf> (44 pp, Richard Wallace)

- §4.1 PCB antennas, verbatim: *"Designing a PCB antenna is not straight forward and usually a simulation
  tool must be used to obtain an acceptable solution. … **It is therefore recommended to make an exact
  copy of one of the reference designs** …, if the available board space permits such a solution."*
- §4.2 Chip antennas, verbatim:
  > If the available board space for the antenna is limited a chip antenna could be a good solution. …
  > The trade off compared to PCB antennas is that this solution will **add BOM and mounting cost. The
  > typical cost of a chip antenna is between $0.10 and $0.50.** Even if manufacturers of chip antennas
  > state that the antenna is matched to 50 ohms for a certain frequency band, **it is often required to
  > use additional matching components** to obtain optimum performance. The performance numbers and
  > recommended matching given in data sheets are often based on measurements done with a test board. …
  > **It is important to be aware that the performance and required matching will change if the chip
  > antenna is implemented on a PCB with different size and shape of the ground plane.**
- §5.1.2 Ground Effects: *"The size and shape of the ground plane will affect the radiation pattern."*
  (Measured example: an antenna board plugged into a SmartRF04EB with a solid ground plane vs the same
  board standalone.)
- §4.3 Whip antennas: *"**If a connector is used then to pass the regulations, conducted emission tests
  must also be performed.**"*

## TI DN035 / SWRA351B — "Antenna Selection Quick Guide"
<https://www.ti.com/lit/an/swra351a/swra351a.pdf> — a one-page comparison table. 2.4 GHz rows:

| app note | typical efficiency | BW @ VSWR 2.0 | dimensions (mm) |
|---|---|---|---|
| SWRU120 (first choice) | 80 % (EB) / 94 % (SA) | 280 MHz | 26 × 8 |
| **SWRA117 (second choice, = AN043)** | 68 % (EB) | 101 MHz | **15 × 6** |
| SWRA118 | 80 % (EB) | 100 MHz | 46 × 9 |
| SWRA093 | 65 % | 150 MHz | 45 × 2.5 |
| SWRA350 | 72 % (SA) | 497 MHz | 150 × 100 |

→ Useful calibration: the *small* 2.4 GHz PCB antenna costs ~15 × 6 mm and gives up ~12 points of
efficiency and two-thirds of the bandwidth versus the 26 × 8 mm one.

## Johanson Technology 2450AT18A100E-AEC — chip antenna, for the numbers
<https://www.johansontechnology.com/datasheets/2450AT18A100/2450AT18A100.pdf> (spec dated 2017-12-22)

- Size **3.20 × 1.60 × 1.30 mm** (L × W × T), 2400–2500 MHz, 50 Ω, peak gain 0.5 dBi typ, average gain
  −0.5 dBi typ, return loss 9.5 dB min, −40…+125 °C, AEC-Q200, 3000/reel.
- Two mounting options are drawn: **(a) without matching circuits** and **(b) with matching circuits**
  (a shunt-series-shunt π: 1.0 pF shunt, 3.9 nH series, 2.7 nH shunt on the evaluation board).
- Verbatim: *"It is recommended that the designer leave available slots for a 'pi' (or shunt-series-shunt)
  network. The antenna matching network values here are used when antenna is mounted on Johanson's
  evaluation board. **The matching values and topology on client's PCB will be different.**"*
- The evaluation board defines the ground-plane geometry the numbers were taken on: a 39.5 × 13.5 mm
  ground area, a 19 mm 50 Ω feed line, and a **6.5 × 6.5 mm "No Ground" antenna region**.
- *"Line width should be designed to provide 50 Ω impedance matching characteristics."*

→ Direct consequence for haytag: a chip antenna does **not** remove the host-board dependence, it only
moves it into a π-network that must be re-tuned per host. A **module** with its own ground plane and
shield is the only construction where the tuning travels with the part.

---
## ST AN2866 Rev 6 — "How to design a 13.56 MHz customized antenna for ST25 NFC/RFID tags"
<https://www.st.com/resource/en/application_note/an2866-...-stmicroelectronics.pdf>

- The tag antenna is an inductor resonating with the chip's internal tuning capacitance:
  *"The efficient transfer of energy from the reader to the tag depends upon the loop antenna tuned to the
  carrier frequency (usually 13.56 MHz)."*
- Table 2, *Antenna coil inductance for different Ctun values vs. tuning frequency*:

  | product | Ctun (pF) | tuning frequency (MHz) | required coil inductance (µH) |
  |---|---|---|---|
  | ST25TA series | 50.0 | 14.00 | 2.58 |
  | ST25TA series | 27.5 | 14.00 | 4.70 |
  | ST25TB series | 68.0 | 13.56 | 2.00 |
  | ST25TB series | 68.0 | 14.40 | 1.80 |

- §4.1 spiral inductance, verbatim formula:
  `L_ant = 31.33 × µ0 × N² × a² / (8a + 11c)` where `a = (r_in + r_out)/2` (average radius, m) and
  `c = r_out − r_in` (m).
- §4.2 square/octagonal/hexagonal coils use K1/K2 (Table 3): square **K1 2.34, K2 2.75**;
  octagonal 2.25 / 3.55; hexagonal 2.33 / 3.82.
- §4.3 points at ST's **eDesignSuite planar rectangular coil inductance calculator**, which takes PCB
  material and antenna dimensions and returns the equivalent inductance.
- §5 gives the two contactless tuning-measurement methods (network analyser; ISO standard loop antenna
  + oscilloscope) — i.e. the coil has to be **measured after layout**, per host shape.

→ Direct consequence for haytag: the NFC coil is the one part of the tag that **cannot** live inside a
15 × 20 mm module. Its inductance is set by turns and enclosed area, both of which are properties of the
host outline. The block must expose NFC1/NFC2 and ship a **parametric coil generator + a target
inductance**, not a fixed coil. (Nordic's nRF52 NFC-A tag needs ~2 µH-class coils in the same family;
the exact nRF52840 target is not verified in this lane — see the gap list.)
