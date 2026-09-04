# halo electronics — the circuit, block by block

*Lane B1. This describes **revision A**, which lives in `halo_rev_a/`. Every
number here was produced by a tool on this machine; the last section is the
list of things that were not, and it is the most important one.*

---

## Where everything is

| path | what |
|---|---|
| `halo_rev_a/schematic.py` | the circuit, generated. **The only place a part number is typed.** |
| `halo_rev_a/board.py` | the copper. Reads the netlist back out of the schematic — it is never retyped. |
| `halo_rev_a/footprints.py` | the six land patterns KiCad does not have, and the antenna geometry |
| `halo_rev_a/pinouts.json` | the nRF54L10 and LIS2DW12 pin tables, transcribed from the datasheets with citations |
| `halo_rev_a/sim/` | our own circuit and electromagnetic models |
| `halo_rev_a/out/` | the built `.kicad_sch`, `.kicad_pcb`, PDF, SVG, netlist, ERC and DRC reports |
| `../out/release/board/` | the factory package — Gerbers, BOM, CPL, stackup, verdicts |

Rebuild the whole thing:

```bash
cd ~/dev/ce-workshop
python3 ce-designs/halo/electronics/halo_rev_a/footprints.py
ce-pcb/bin/sch build ce-designs/halo/electronics/halo_rev_a/schematic.py \
                  -o ce-designs/halo/electronics/halo_rev_a/out
ce-pcb/bin/pcb   ce-designs/halo/electronics/halo_rev_a/board.py
ce-pcb/bin/sch erc ce-designs/halo/electronics/halo_rev_a/out/halo_rev_a.kicad_sch
```

---

## The circuit, in one paragraph

A CR2032 feeds an nRF54L10 directly. There is no buck, no LDO and no load
switch: the SoC's 1.7–3.6 V range spans the whole cell curve, so every
regulator in Apple's board is a part we do not buy. The SoC carries the
2.4 GHz radio, the NFC-A tag peripheral that drives an etched coil through two
tuning capacitors, and Bluetooth Channel Sounding for peer ranging. A
LIS2DW12TR on I²C wakes it on movement; a bare piezo bender bonded to the
shell is driven anti-phase from two GPIO with no amplifier; SWD comes out on
pads that cost no height.

---

## Block by block, and why each part is there

### 1. The SoC — `nRF54L10-QFAA-R7`, LCSC **C44800139**

QFN-48, 6 × 6 mm, 0.4 mm pitch. **$2.4012 at 1000.** DECISIONS.md D12 chose
it over the nRF52840 on a measurement: Bluetooth Channel Sounding gives 6–10 cm
mean error on coin-cell hardware, the same accuracy band as ultra-wideband,
from a radio already on the tag — and it costs **61 cents less** than the
nRF52832, where adding UWB costs $8.86 more.

Its datasheet numbers drive every power figure in this project: **TX 3.7 mA at
0 dBm, RX 2.1 mA, System-ON with 192 kB retained 2.4 µA** (Table 86). Those are
radio-only figures and lower than the 4.8 mA on Nordic's marketing page, which
is whole-device.

Decoupling is four 100 nF 0201s, one per VDD pin. The SoC's own DC/DC runs off
L1 between `DCC` and `DECD`; `DECA` is tied to `DECRF` because the datasheet
says *"Must be connected to DECA"*, not because it is tidy. The passive values
are Nordic's own reference circuit configuration 1 (Figure 175 / Table 82),
copied component-for-component — the correct move for an RF front end and the
wrong one to improvise.

### 2. Power, the cell, and the five-removals reset

The CR2032 lands on **three sprung fingers**, not a holder: SPEC.md §4 records
that the lowest-profile surface-mount retainer stands 2 mm above the board and
the stack has about 1.5 mm in total. Lane M's carrier holds the cell; the
board's job is three solder lands under the finger roots.

**Bulk is 4 × 10 µF 0402, not Apple's five 100 µF.** Two of the three loads
that needed 500 µF are gone — D12 deleted the U1 and D11a deleted the class-D
amplifier — and an 0805 is 1.25 mm tall against a 0.578 mm allowance. What
40 µF actually buys is measured, not asserted: see §"What the simulations
say".

**Cell-removal detection is a circuit, not a note.** SPEC.md §3 says the
AirTag has two positive contacts *"both sensed before boot"*, and the
five-removals factory reset needs the SoC to stay alive across a removal. So
the second positive finger is **sense-only**: it feeds a 4.7 M/4.7 M divider
into AIN0 whose bottom leg returns to a GPIO rather than to ground, so it
draws 0.32 µA *only while that pin is driven low* and nothing at all the rest
of the time. On a 2.4 µA sleep budget a permanently-on divider would have been
a 13 % battery-life tax. Pull the cell and the sense node collapses in about
0.24 ms while the bulk holds the rail up for seconds. Zero series loss, zero
extra silicon, and it uses the second finger for the reason Apple has one.

### 3. Clocks

32 MHz (`NX2016SA`, C843260) and 32.768 kHz (Epson `C32346`) crystals.
**External load capacitors are placed but NOT FITTED.** The nRF54L family has
on-die load capacitors on both oscillators; fitting external ones as well
double-loads the crystal and pulls it off frequency. The pads exist so a
crystal lot that does not pull in can be trimmed without a board spin, and
populating them means disabling the internal ones — a firmware change, not a
rework.

### 4. The 2.4 GHz path

Nordic's reference matching network (L2/C18/L3/C19/L4/C22/C23) from the `ANT`
pin to a 50 Ω node, then a **pi network — C20 shunt, L10 series, C21 shunt** —
between that node and the antenna feed. L10 is fitted as a 0 Ω jumper so the
board works untuned; all three are re-valued from a measured S11.

The pi is not decoration. A trace antenna on a Ø26 mm board with a Ø20 mm
battery can 0.578 mm underneath will not present 50 Ω, and **a matching network
is the only place that error can be absorbed.**

Two layout rules travel with this block, and they are Nordic's own words from
Figure 175: **C18's ground connects ONLY to pin 32 (VSS_PA), on the top
layer**, and **C19's ground must be isolated from every ground layer except the
bottom.** Both are written onto the sheet, because a schematic cannot enforce
them and forgetting them breaks the radio.

### 5. NFC — and there is no NFC chip

SPEC.md F8: the SoC's own NFC-A peripheral drives the coil from two pins.
**There is no separate NFC front end in an AirTag either**, which deletes a
BOM line most clone designs carry. The whole block is an etched coil and two
capacitors.

The coil is **2 turns, not 5**, and that is forced rather than chosen: the
usable annulus is R10.15–R10.85, because R10.0 is the cell can and R10.94 is
the nearest battery contact land minus clearance. At the 0.30 mm pitch a
0.127 mm process allows, 0.70 mm of band is 2.33 turns.

C24/C25 are **1.1 nF, and they were 130 pF until the solver corrected them.**
130 pF is Nordic's figure *for a 2 µH antenna*; ce-rf measured the real
winding at 0.2449 µH and returned 554.6 pF of tuning across it, so each series
capacitor is 1.109 nF.

### 6. There is no SPI NOR flash — a defect fix

Revision A carried a GD25LQ32EEIGR on VDD. **That part's supply range is
1.65–2.0 V and this board's only rail is a raw 3.0 V coin cell**, so it was out
of specification from the first second — the kind of fault that half-works on
a bench and fails in a field. Caught by the production test lane reading the
sheet.

Fitting a regulator was the alternative and it is what the real AirTag does. It
costs a part, an inductor, a rail, a test and board area, and buys nothing:
nothing else here wants 1.8 V. Meanwhile the firmware measures **13,164 bytes,
1.27 % of the SoC's own 1 MB**, and research/05 §3.7 already recommended
omitting it. So it is deleted. If revision B wants external firmware staging,
the part is a **wide-range low-power NOR such as the Macronix MX25R
(1.65–3.6 V)** — not another GD25LQ.

### 7. Motion — `LIS2DW12TR`, LCSC **C189624**

LGA-12, 2 × 2 mm, under 1 µA in low-power mode, **$0.7408 at 1000**. Apple's
BMA280 is unbuyable (29 in stock against a 10,000-piece minimum packet).

**On I²C, not SPI.** It costs two pins instead of four, frees the SPI bus for
the reserved UWB option, and lets the part answer while nothing else is
selected. CS is strapped high to select I²C and SA0 low to set address 0x18,
both through resistors rather than vias so a bring-up board can change mode.
Both interrupt lines are wired: INT1 is the wake line SPEC.md F7 needs, INT2
carries the orientation vector D12 attaches to every range.

### 8. The sounder — two pins, no amplifier

D11a: a bare **Murata 7BB-20-3** piezo bender, Ø20.0 × 0.22 mm, bonded to the
inside of the shell and driven anti-phase from two GPIO. This is Apple's trick
— make the housing the radiating surface — done with a catalogue part a fifth
of a millimetre thick, because the obvious buzzer is 3.5 mm tall and the stack
has 1.5 mm.

**No MAX98357A.** A bridge-tied class-D swings ±Vbat; two pins driven
anti-phase swing the same. What the amplifier buys is current, and a bender is
capacitive. That was research/05 §11.6's arithmetic; it is now measured.

R9 is 100 Ω of series damping and it earns its line — see below.

### 9. Debug and the reserved UWB option

Six SWD lands at 1.27 mm pitch. **A Tag-Connect was drawn first and does not
fit**: its land pattern is about 80 mm² with two NPTH alignment holes, and the
DRC found those holes drilled through the SoC's pads. Six 0.8 × 1.4 mm lands
carry the same six signals in 9 mm² with no holes.

J2 reserves the halo-uwb variant of D12 as **eight SMD lands** carrying SPI, an
interrupt, a reset and power — **not a DW3110 land pattern.** No document in
this repository carries the DW3110's pin assignment, and D9 forbids guessing
48 net names; and a second 6 × 6 mm QFN does not fit a Ø26 mm board whose
middle Ø20 mm is shadowed by a battery.

### 10. Test access

Eleven probe lands and two asymmetric fiducials, placed by search rather than
by hand. **VDD and GND each get a FORCE and a SENSE pad** — sleep current is
single-digit microamps, and two probes landing in one battery pad is a
two-wire measurement wearing a four-wire name. **IPC-A-610 Class 2** is
recorded on the sheet because the optical inspection recipe is built from it.

---

## What the simulations say — about this board, not an example

| study | verdict | the number that matters |
|---|---|---|
| `sim/rail_droop.py` | **PASS** | 84.7 mV droop at end of life against a 400 mV limit; 64.5 months derated life |
| `sim/rail_droop.py` (hold-up) | **PASS** | 40 µF keeps the rail alive **4.998 s** after the cell is pulled |
| `sim/sounder_drive.py` | **PASS** | **3.98 V pp** across the bender from a 2.0 V cell — 2×VDD with no amplifier |
| `ce-rf` NFC coil | **PASS** | L = 0.2449 µH, tuning 554.6 pF |
| `ce-rf` 2.4 GHz | **FAIL** | 2.886 GHz against a 2.4–2.4835 GHz target |

**Three things the simulations changed in the design, rather than confirming.**

1. **The NFC tuning was eight times wrong.** 130 pF → 1.1 nF.
2. **R9 was justified for the wrong reason.** The schematic said 100 Ω "holds
   the peak near 30 mA". Measured: with a low-loss 40 nF bender the peak pin
   current is 32.0 mA *without* R9 and 17.8 mA *with* it. Right magnitude,
   wrong side of it. R9 is what keeps the pin under a 25 mA ceiling.
3. **The antenna was 3.78 mm too short.** openEMS returned
   `eps_eff_implied = 1.573` where the element had been sized on the textbook
   2.2, so the quarter wave is 24.49 mm and not 20.71. The element now
   meanders, with the tooth depth solved by bisection.

**Two studies caught their own mistakes**, which is the point of writing
asserts that can fail. The sounder study first measured the bender voltage
*to ground* instead of *across the bender*, reported 2.0 V where the swing is
4.0 V, and failed an assert that was actually satisfied. And the rail study
asserted the rail alive ten seconds after a cell removal — a threshold that
came from nowhere, failed at 1.400 V, and was replaced by the requirement that
actually exists (the firmware's detect-and-commit budget, about 11 ms) rather
than loosened.

---

## What is still unproven

**Load-bearing, in rough order of how much they matter.**

1. **The board is not routed.** 91 unconnected items, 0 vias. Freerouting
   was run three times and timed out three times — 900 s at 12 passes,
   3300 s at 3, 2400 s at 2. The tool works (lane T1 proved it on a Ø31.87 mm
   board); this board is denser than it can handle. Do not fabricate.
2. **The antenna has not passed.** 2.886 GHz measured on the 20.71 mm
   element, with `eps_eff_implied = 1.573` naming the cause. The corrected
   24.49 mm meander is drawn in the copper but its FDTD re-run did not
   complete — the confirmation that it lands in band is the missing piece,
   not the correction itself.
3. **Five part classes do not fit the enclosure — and the fix is already
   written down.** 46 PASS / 5 FAIL on the height check. A QFN-48 is 0.85 mm
   and the cell leaves 0.578 mm under the bottom face; X1 and L1 are over by
   0.322 mm, the SoC by 0.272.

   **DECISIONS.md D17 (lane M, 2026-09-04) ends: *"leaving 0.542 mm of dead
   air under the cell that a flat pad embossed in the door could still
   recover"*.** If that pad is embossed the cell drops and the bottom-face
   allowance becomes 0.578 + 0.542 = **1.120 mm**. The tallest part here is
   0.90 mm and needs 0.95 mm with a solder fillet, so **every part clears** —
   and only **0.372 mm of the 0.542 mm** has to be recovered to do it.

   **This is a request to lane M, and it is the single change that closes
   this lane's largest open item.** `board.py height_check()` prints the
   arithmetic on every run.
4. **Loudness is unmeasured and DULT makes it mandatory.** 60 Phon at 25 cm
   cannot be simulated; VERIFICATION-DEBT V7 carries it.
5. **The bender is unsourced at every quantity**, so its land pattern is
   deliberately generic.
6. **Two turns of NFC coil may not couple enough** to read at a phone's field
   strength. The inductance is measured; the read range is not, and no assert
   here pretends otherwise.
7. **The SoC's stock is 212 pieces** against a 1000-piece minimum packet.
8. **Channel Sounding between two halos has never been demonstrated** — the
   6–20 cm figure is from a published study on other hardware (V8).
9. **The 0402 bulk capacitors' DC bias derating is unfetched**, so 40 µF is an
   upper bound and every droop figure is optimistic by an unmeasured amount.
10. **The GPIO high-drive output resistance is an estimate** (40 Ω), and every
    peak sounder current is inversely proportional to it.
11. **Controlled impedance is not implemented**, and the fab's 0.60 mm 4-layer
    dielectric heights were never retrieved.
12. **eps_r 4.3 / tan δ 0.02 is generic FR-4**, not fab-quoted — the largest
    single uncertainty in every RF frequency here.
