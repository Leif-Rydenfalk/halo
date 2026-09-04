"""halo revision A — the real board's schematic, generated from code.

    cd ~/dev/ce-workshop
    ce-pcb/bin/sch all ce-designs/halo/electronics/halo_rev_a/schematic.py \
                   -o ce-designs/halo/electronics/halo_rev_a/out

LANE B1 owns this file. It is NOT `ce-pcb/examples/halo_core_sketch/`, which
is lane T5's tool-proving sketch; this is the circuit that goes to a factory.
What changed from that sketch, and why, is listed under "DELTAS" below.

Every part on this sheet carries an `LCSC` field with a real order code and
the price/stock ladder date, because MISSION.md item 3 wants a BOM whose
lines can be ordered, and a BOM generated from the schematic cannot carry a
number the schematic does not hold.

---------------------------------------------------------------------------
THE CIRCUIT, IN ONE PARAGRAPH
---------------------------------------------------------------------------
A CR2032 feeds an nRF54L10 directly — no buck, no LDO, no load switch
(research/05 §3.8: the SoC's 1.7-3.6 V range spans the whole cell curve, so
every regulator in Apple's board is a part we do not buy). The SoC's own
DC/DC runs off one inductor. It carries the 2.4 GHz radio, the NFC-A tag
peripheral that drives an etched coil through two tuning capacitors, and
Bluetooth Channel Sounding for peer ranging (D12). A LIS2DW12TR on I2C wakes
it on motion; a 32 Mbit SPI NOR holds firmware and key material; a bare
Murata 7BB-20-3 bender bonded to the shell is driven anti-phase from two
GPIO with no amplifier (D11a); and SWD comes out on Tag-Connect pads that
cost no height.

---------------------------------------------------------------------------
DELTAS FROM THE T5 SKETCH — each one is a requirement, not a preference
---------------------------------------------------------------------------
D-1  ACCELEROMETER MOVED SPI -> I2C.  The sketch put the LIS2DW12 on the
     flash's SPI bus. On I2C it costs two pins instead of four, frees the
     SPI bus for the reserved UWB option, and lets the part answer while the
     flash is deselected. CS is strapped high to select I2C and SA0 is
     strapped low, both per LIS2DW12 datasheet DS11811 Rev 9 §5.
D-2  A PI MATCHING NETWORK NOW EXISTS.  The sketch ends Nordic's reference
     network straight into the antenna. A trace antenna on a Ø26 mm board
     with a Ø20 mm battery can 0.58 mm underneath will not present 50 ohm,
     and ce-rf cannot tune what has no tuning elements. C20/L10/C21 are a
     classic shunt-series-shunt pi at the feed, all three fitted as
     placeholders and all three re-valued from a measured S11.
D-3  CRYSTAL LOAD-CAPACITOR FOOTPRINTS ADDED, DNP BY DEFAULT.  The nRF54L
     family has on-die load capacitors on both oscillators (CAPVALUE
     registers). Fitting external caps as well DOUBLE-LOADS the crystal and
     pulls it off frequency, so they are placed DNP: the pads exist so a
     factory can trim a crystal lot that does not pull in, and populating
     them is a documented instruction, not a rework.
D-4  BULK CAPACITANCE RE-SIZED AND RE-ARGUED.  Lane A counted five 100 uF
     capacitors in the AirTag. Two of the three loads that needed them are
     gone: D12 deleted the U1 and D11a deleted the class-D amplifier. Five
     0805 parts also do not fit — see HEIGHT below. Rev A carries 4 x 10 uF
     in 0402 and the hold-up time it buys is a ce-spice result, not a claim.
D-5  CELL-REMOVAL SENSE IS NOW A CIRCUIT, not a note.  SPEC.md §3 says the
     AirTag has TWO positive contacts "both sensed before boot", and the
     five-removals factory reset needs the SoC to stay alive across the
     removal. Rev A uses the second positive finger as a SENSE-ONLY contact
     (R1/R2 divider, gated by a GPIO so it burns nothing while idle) while
     the first carries the current. Pull the cell and VBAT_SNS collapses in
     under a millisecond while the bulk capacitors hold VDD up for seconds.
     Zero series loss, zero extra silicon, and it uses the second finger for
     the reason Apple has one.
D-6  UWB IS A CASTELLATED STUB, NOT A DW3110 LAND PATTERN.  See below.
D-7  THE SPI NOR FLASH IS DELETED, and it is a defect fix rather than a
     simplification. The GD25LQ32E is a 1.65-2.0 V part and this board's
     only rail is a raw 3.0 V coin cell. Block 6 carries the full argument
     and the part to fit if revision B ever needs one.
D-8  TEST ACCESS IS DESIGNED IN, not left to the fixture. Four-wire force
     and sense pairs on VDD and GND, probe pads on the two piezo nets, the
     cell-removal sense, the I2C bus and both NFC pins, two ASYMMETRIC
     fiducials, and a laser-mark land for the per-unit serial that
     compliance constraint C11 requires. Block 10.

---------------------------------------------------------------------------
WHAT THIS SHEET REFUSES TO ASSERT — read before believing it
---------------------------------------------------------------------------
X-1  THE DW3110 LAND PATTERN IS NOT DRAWN, and D12 asked for one. Two
     measured reasons, both of which would have to change first:
       (a) No document in this repository carries the DW3110's pin
           assignment. research/fetched/E-uwb-and-datasheet-specs.md has its
           package ("48-VFQFN Exposed Pad (6x6)"), its price and its stock,
           and nothing else. KiCad ships `RF:DW1000`, which is a DIFFERENT
           part in a similar package; using it would put 48 guessed net
           names on a board. DECISIONS.md D9 forbids exactly that.
       (b) It does not fit. The board is Ø26.00 mm (lane M, design.py
           D_PCB). The SoC alone is a 6x6 mm QFN. A second 6x6 mm QFN plus
           its own crystal, its own matching network and a UWB antenna, on a
           board whose middle Ø20 mm is shadowed by a battery can, is not a
           placement problem — it is 72 mm2 of body on a 531 mm2 disc that
           already carries 131 joints.
     What rev A does instead: J2, an 8-pad castellated stub on the board
     edge carrying SPI, an interrupt, a reset and power, so a halo-uwb
     daughtercard is a real option rather than a sentence. When the DW3110
     pin table is fetched, the stub is what it lands on.
X-2  NFC TUNING IS NOW MEASURED, AND THE FIRST VALUE WAS EIGHT TIMES WRONG.
     This sheet carried 130 pF, from Nordic's NFCT chapter, which quotes
     that FOR A 2 uH ANTENNA. The real coil is not 2 uH. ce-rf measured the
     2-turn Ø21.5 mm winding that actually fits between the cell can and
     the battery contact lands at 0.2449 uH, and returns C_external =
     554.6 pF across it, so each series capacitor is 1.109 nF. C24/C25 are
     1.1 nF. What is still open is whether a 1.1 nF C0G exists in 0201, and
     whether TWO TURNS couples enough to read at a phone's field strength -
     that is a bench measurement and no assert here pretends otherwise.
X-3  THE PI NETWORK VALUES ARE PLACEHOLDERS. They are seeded from Nordic's
     reference and will be replaced by whatever ce-rf's S11 on the real
     copper asks for. A pi network with unmeasured values is a tuning
     mechanism, not a match.
X-4  GPIO ASSIGNMENT IS THIS FILE'S CHOICE. Every nRF54L peripheral is
     routed by PSEL, so any function can go on any pin; that makes these
     assignments free and therefore unverified against a firmware build.
     The SPI pins are the exception: 12/13/15/16 are the pads Nordic labels
     SCK/SDO/SDI/CS, and rev A keeps them there so the default instance
     mapping works before anyone writes a pinctrl node.
X-5  HEIGHT. Lane M's stack (design.py) allows 0.400 mm of component height
     on the top face inside Ø21.2 mm and about 0.578 mm on the bottom face
     over the cell. A QFN48 is 0.85 mm tall. THE SoC DOES NOT FIT EITHER
     FACE OF THE CURRENT STACK, short by about 0.32 mm on the better side.
     This sheet is drawn anyway, because the netlist is correct regardless
     of who resolves the millimetre, and the delta is reported to lane M
     rather than absorbed silently. electronics/README.md carries the four
     candidate resolutions.
"""
import json
import os
import sys

WORKSHOP = "/Users/leifrydenfalk/dev/ce-workshop"
if WORKSHOP not in sys.path:
    sys.path.insert(0, os.path.join(WORKSHOP, "ce-pcb"))

from cepcb.schematic import Schematic                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PINOUTS = os.path.join(HERE, "pinouts.json")

# Land patterns, each verified present with cepcb.find() on 2026-09-04.
C0201 = "Capacitor_SMD:C_0201_0603Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
R0201 = "Resistor_SMD:R_0201_0603Metric"
L0201 = "Inductor_SMD:L_0201_0603Metric"

#: Price ladders and stock are lane E's live pull, research/05 §11.1 and §3,
#: dated 2026-09-03. A price with no date is a rumour.
PULLED = "2026-09-03"


def P(lcsc, mpn, mfr, price_1k=None, stock=None, extra=None):
    """One BOM line's sourcing, as schematic fields.

    THE FIELD IS CALLED "LCSC Part #", NOT "LCSC". ce-fab looks for a fixed
    list of spellings - "LCSC Part #", "LCSC Part", "LCSC PN", "LCSC P/N",
    "LCSC Part No.", "LCSC Part Number" - and a plain "LCSC" is in none of
    them. With the short name, `fab jlc` returned CANNOT DETERMINE on 42 of
    44 placed parts: every order code was present on the sheet and none of
    them reached the bill of materials. A field name is an interface.
    """
    f = {"LCSC Part #": lcsc, "MPN": mpn, "Manufacturer": mfr,
         "Priced": PULLED}
    if price_1k is not None:
        f["Price@1k"] = price_1k
    if stock is not None:
        f["Stock"] = stock
    if extra:
        f.update(extra)
    return f


def pinouts():
    if not os.path.exists(PINOUTS):
        raise SystemExit(
            "CANNOT DETERMINE: %s is missing, so this sheet has no sourced "
            "pinout to draw." % PINOUTS)
    with open(PINOUTS, "r", encoding="utf-8") as fh:
        return json.load(fh)["parts"]


def build():
    # NOTE: the project's fp-lib-table is written by board.py, NOT here.
    # `bin/sch build` calls build() and then save(), and save() writes its own
    # minimal fp-lib-table over anything this function had put there - 8
    # libraries, no halo, so ERC could not resolve a footprint and reported
    # one warning per part. Writing it at the END of the pipeline instead of
    # the start is the fix; footprints.write_fp_lib_table() is the one
    # implementation and board.py calls it.
    parts = pinouts()
    nrf, lis = parts["nRF54L10-QFAA"], parts["LIS2DW12"]

    s = Schematic(
        "halo_rev_a",
        title="halo revision A - open Find My tag, nRF54L10, CR2032, Ø26 mm",
        rev="A", company="Leif-Rydenfalk/halo - CERN-OHL-S",
        comments=[
            "Board is Ø26.00 x 0.60 mm, 4 layers (lane M design.py D_PCB).",
            "nRF54L10-QFAA-R7 per D12; piezo anti-phase on 2 GPIO per D11a.",
            "RF passives seeded from Nordic ref circuit config 1 (Fig 175).",
            "Values marked PLACEHOLDER are re-valued from ce-rf measurements.",
        ])

    soc_id = s.define(
        name="nRF54L10-QFAA", pins=[tuple(r) for r in nrf["pins"]],
        description="Multiprotocol BLE SoC with Bluetooth Channel Sounding "
                    "and an on-die NFC-A tag peripheral, QFN48 6x6. "
                    "halo DECISIONS.md D12.",
        keywords="nordic nrf54l ble channel sounding nfc soc",
        datasheet="https://www.farnell.com/datasheets/4557217.pdf",
        cite=nrf["cite"])
    acc_id = s.define(
        name="LIS2DW12", pins=[tuple(r) for r in lis["pins"]],
        description="3-axis MEMS accelerometer, I2C/SPI, LGA-12 2x2. Wakes "
                    "the tag on motion and supplies the orientation vector "
                    "that D12 attaches to every range.",
        keywords="accelerometer mems motion i2c",
        datasheet="https://www.st.com/resource/en/datasheet/lis2dw12.pdf",
        cite=lis["cite"])

    # =====================================================================
    # BLOCK 1 - the SoC
    # =====================================================================
    s.part("U1", soc_id, value="nRF54L10-QFAA-R7", group="soc",
           footprint="Package_DFN_QFN:QFN-48-1EP_6x6mm_P0.4mm_EP4.4x4.4mm",
           datasheet="https://www.farnell.com/datasheets/4557217.pdf",
           fields=P("C44800139", "NRF54L10-QFAA-R7", "Nordic Semiconductor",
                    "$2.4012", "669 LCSC / 1003 JLC",
                    {"Note": "1000-piece MINIMUM PACKET (research/05 §11.1) - "
                             "the only nRF54L whose minimum packet a 1k build "
                             "actually consumes. TX 3.7 mA @0 dBm, RX 2.1 mA, "
                             "System-ON 192 kB retained 2.4 uA (Table 86)."}))

    for pad in ("10", "22", "36", "47", "48"):
        s.net("VDD", "U1." + pad)
    for pad in ("32", "44", "49"):
        s.net("GND", "U1." + pad)

    # Per-pin decoupling. One 100 nF 0201 at each of the four VDD pins that
    # has room beside it, plus the two Nordic calls out by name.
    for ref, val, fp, note in [
            ("C1", "100nF", C0201, "at VDD pin 10"),
            ("C2", "100nF", C0201, "at VDD pin 22"),
            ("C3", "100nF", C0201, "at VDD pin 36"),
            ("C4", "100nF", C0201, "at VDD pins 47/48")]:
        s.part(ref, "Device:C", value=val, group="power", footprint=fp,
               fields=P("C5142565", "TCC0201X5R104K100ZT", "CCTC", "$0.0005",
                        "in stock",
                        {"Note": "0201 X5R 10V, " + note
                                 + ". Code re-verified 2026-09-05: C1546 is "
                                 "a 100 pF 0402, not this line (S1).",
                         "Tol": "10%"}))
        s.net("VDD", ref + ".1")
        s.net("GND", ref + ".2")

    # The SoC's own DC/DC. DCC -- L1 -- DECD, then DECA tied to DECRF because
    # the datasheet says "Must be connected to DECA", not because it is tidy.
    s.part("L1", "Device:L", value="4.7uH", group="power",
           footprint="Inductor_SMD:L_0603_1608Metric",
           fields=P("C76799", "MLZ1608M4R7WT000", "TDK", "$0.0301", "in stock",
                    {"Note": "0603 multilayer, >=120 mA Isat, DCC->DECD. "
                             "Code re-verified 2026-09-05: C1046 is a 10 uH "
                             "0805, not this line (S1). "
                             "0603 is 0.9 mm tall: BOTTOM FACE ONLY, and it "
                             "is one of the parts X-5's height delta binds."}))
    s.net("DCC", "U1.46", "L1.1")
    s.net("DECD", "U1.45", "L1.2")

    for ref, val, note in [
            ("C5", "2.2uF", "0201 X5R 10V, DECD reservoir (Table 82)"),
            ("C6", "10nF", "0201 X7R - Table 82 lists it, Figure 175's "
                           "extraction does not place its node. Wired to "
                           "DECD. CANNOT DETERMINE against the source."),
            ("C7", "2.2nF", "0201 X7R - same, CANNOT DETERMINE")]:
        # One code per VALUE, per S1: C2827888 is a 3.5 mm screw terminal
        # block and was serving all three of these lines at once.
        code, mpn = {"C5": ("C335106", "GRM033R61A225KE47D"),
                     "C6": ("C76941", "GRM033R71A103KA01D"),
                     "C7": ("C161479", "GRM033R71A222KA01D")}[ref]
        s.part(ref, "Device:C", value=val, group="power", footprint=C0201,
               fields=P(code, mpn, "muRata", "$0.0301", "in stock",
                        {"Note": note + " Code re-verified 2026-09-05 (S1)."}))
        s.net("DECD", ref + ".1")
        s.net("GND", ref + ".2")

    s.part("C8", "Device:C", value="2.2uF", group="power", footprint=C0201,
           fields=P("C335106", "GRM033R61A225KE47D", "muRata", "$0.0301",
                    "in stock", {"Note": "0201 X5R 10V, on the DECA=DECRF "
                                         "node. Code re-verified 2026-09-05 "
                                         "(S1)."}))
    s.net("DECA", "U1.43", "U1.33", "C8.1")
    s.net("GND", "C8.2")

    # =====================================================================
    # BLOCK 2 - the cell, its bulk store, and the removal sense
    # =====================================================================
    # Three sprung fingers on the carrier, not a holder: SPEC.md §4 says no
    # surface-mount retainer under 2 mm exists. The land patterns are three
    # plain pads the layout draws; there is no catalogue footprint for a
    # spring finger, and pretending otherwise is how a wrong part reaches a
    # fab. Symbol is a 2-pin cell so the netlist reads correctly.
    # Three fingers, so a two-pin battery symbol cannot draw it. Catley's
    # teardown counts 2 positive + 1 negative, all carrier-side, and lane M's
    # design.py places them at R 9.50 (x2) and R 6.00. The symbol is made
    # here from that, because a cell whose sense contact has nowhere to land
    # cannot express D-5's mechanism at all.
    cell_id = s.define(
        name="HALO-CR2032-3C",
        pins=[("1", "P+ (current)", "passive", "left"),
              ("2", "P- (return)", "passive", "left"),
              ("3", "P+ (sense)", "passive", "right")],
        description="CR2032 on three sprung C5191 fingers: two on the "
                    "positive can rim, one on the negative face. One "
                    "positive finger carries current, the other is sense "
                    "only - halo rev A D-5.",
        keywords="cr2032 coin cell sprung contact",
        datasheet="https://industrial.panasonic.com/cdbs/www-data/pdf/"
                  "AAC4000/AAC4000CE7.pdf",
        cite="Adam Catley AirTag teardown (2 positive + 1 negative "
             "carrier-side contacts, fetched 2026-09-03) and lane M's "
             "ce-designs/halo/design.py R_CONTACT_POS = 9.50 / "
             "R_CONTACT_NEG = 6.00, A_SPRING_DEG = 30.")
    s.part("BT1", cell_id, value="CR2032", group="battery",
           footprint="halo:HALO_BATT_CONTACT_3PAD",
           fields={"MPN": "CR2032", "Manufacturer": "Panasonic",
                   "LCSC Part #": "NO ORDER CODE - NOT AN SMT LINE",
                   "Note": "THE CELL IS BOUGHT, THE HOLDER IS NOT: no part "
                           "is fitted on BT1 - the contacts are three "
                           "stamped C5191 fingers on halo's OWN land "
                           "pattern. S1 2026-09-05: the code this line "
                           "carried, C7498149, is a Lian Xin BS-CR2032-8 "
                           "SMD BATTERY HOLDER, which must not be ordered "
                           "and cannot be fitted on this footprint. "
                           "Pad 1 = P+ current finger, pad 3 = P+ SENSE "
                           "finger, pad 2 = negative."})
    # The current finger IS the rail. The sense finger deliberately is not,
    # and that separation is the whole mechanism (D-5).
    s.net("VDD", "BT1.1")
    s.net("GND", "BT1.2")

    # Bulk. Four 10 uF 0402 rather than Apple's five 100 uF 0805: the two
    # loads that needed 500 uF (the U1's ranging bursts and a class-D
    # amplifier's 8 ohm voice coil) were deleted by D12 and D11a, and 0805
    # is 1.25 mm tall against a 0.578 mm bottom-face allowance. How long the
    # rail actually holds up is ce-spice's number, in out/release/board/sim.
    for ref in ("C9", "C10", "C11", "C12"):
        s.part(ref, "Device:C", value="10uF", group="battery", footprint=C0402,
               fields=P("C15525", "CL05A106MQ5NUNC", "Samsung", "$0.0136",
                        "in stock",
                        {"Note": "0402 X5R 6.3V, 0.55 mm tall. Bulk store: "
                                 "TX pulse support AND the hold-up the "
                                 "five-removals reset counts on."}))
        s.net("VDD", ref + ".1")
        s.net("GND", ref + ".2")

    # Cell-removal sense. The divider's bottom leg returns to a GPIO, so it
    # draws 3 V / 9.4 M = 0.32 uA only while that pin is driven low and
    # exactly nothing the rest of the time. On a 2.4 uA sleep budget a
    # permanently-on divider would have been a 13 % battery-life tax.
    s.part("R1", "Device:R", value="4.7M", group="battery", footprint=R0201,
           fields=P("C778408", "0201WMF4704TEE", "UNI-ROYAL", "$0.0015",
                    "in stock",
                    {"Note": "sense divider, high leg. Code re-verified "
                             "2026-09-05: C25765 is 20 k 0402 (S1)."}))
    s.part("R2", "Device:R", value="4.7M", group="battery", footprint=R0201,
           fields=P("C778408", "0201WMF4704TEE", "UNI-ROYAL", "$0.0015",
                    "in stock",
                    {"Note": "sense divider, low leg - returns to a GPIO, "
                             "not to GND, so the divider is OFF when idle"}))
    s.part("C13", "Device:C", value="100pF", group="battery", footprint=C0201,
           fields=P("C76922", "GRM0335C1H101JA01D", "muRata", "$0.0033",
                    "in stock",
                    {"Note": "settles the divider inside the ADC's "
                             "acquisition window; also sets the ~0.24 ms "
                             "collapse time when the cell leaves. Code "
                             "re-verified 2026-09-05: C1523 is a 1 nF 0402 "
                             "(S1)."}))
    s.net("VBAT_SNS_HI", "BT1.3", "R1.1")
    s.net("VBAT_SNS", "R1.2", "R2.1", "C13.1", "U1.5")      # P1.04/AIN0
    s.net("SNS_EN", "R2.2", "C13.2", "U1.6")                # P1.05/AIN1

    # =====================================================================
    # BLOCK 3 - the two oscillators
    # =====================================================================
    s.part("X1", "Device:Crystal", value="32.768kHz", group="clocks",
           footprint="Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm",
           fields=P("C95361", "Q13FC13500049", "Epson", "TBC",
                    "134,310",
                    {"Note": "Epson FC-135 32.768 kHz, CL = 6 pF. CHANGED "
                             "from C32346 (Q13FC13500004, CL 12.5 pF), which "
                             "was BOUGHT ON PRICE AND NEVER CHECKED AGAINST "
                             "THE SoC. D-3 deletes the external load "
                             "capacitors, so the whole load is the nRF54L's "
                             "on-die caps, and Nordic's own numbers refuse "
                             "12.5 pF twice over. Datasheet 4503_018 v1.0 "
                             "(Sept 2025) Sec 5.5.2: OSCILLATORS.XOSC32KI."
                             "INTCAP holds 3-18 pF in 0.65 pF steps, and with "
                             "internal caps CL = (C_INT + C_pcb)/2, so the "
                             "highest CL reachable is about (18+2)/2 = 10 pF "
                             "- 12.5 pF needs C_INT ~= 23 pF, 5 pF above the "
                             "hardware maximum. Sec 11.9.2 refuses it again "
                             "at the part level: CL_LFXO min 6 pF, MAX 9 pF, "
                             "which holds whether the caps are internal or "
                             "external. Nordic's own reference BOM (Sec 10.3) "
                             "is a CL 9 pF 2012 crystal with NO external load "
                             "capacitors. A 12.5 pF crystal here does not "
                             "start, or starts far off frequency, and the "
                             "board looks simply dead. OPEN: 6 pF is inside "
                             "the 6-9 pF window but at its edge; a 9 pF part "
                             "in this body would centre it. Package still "
                             "assumed to be the 3215 land pattern and NOT "
                             "confirmed against Epson's drawing. Still 0.9 mm "
                             "tall, which X-5's height delta binds."}))
    s.net("XL1", "U1.1", "X1.1")
    s.net("XL2", "U1.2", "X1.2")

    s.part("X2", "Device:Crystal_GND24", value="32MHz", group="clocks",
           footprint="Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm",
           fields=P("C843260", "NX2016SA-32MHZ-STD-CZS-5", "NDK", "$0.2333",
                    "in stock",
                    {"Note": "CL 8 pF, +/-10 ppm, 2.0x1.6x0.5 mm. Nordic's "
                             "BOM says a 2-pad 2016 and KiCad ships no 2-pin "
                             "2016 land pattern, so the 4-pad symbol is used "
                             "and the can is grounded - better RF practice "
                             "anyway. Recorded as a substitution. MPN "
                             "completed to the orderable suffix 2026-09-05."}))
    s.net("XC1", "U1.34", "X2.1")
    s.net("XC2", "U1.35", "X2.3")
    s.net("GND", "X2.2", "X2.4")

    # D-3: external load capacitors, DNP. The nRF54L has on-die load caps on
    # both oscillators; fitting these as well double-loads the crystal and
    # pulls it off frequency. The pads exist so a crystal lot that does not
    # pull in can be trimmed without a board spin. POPULATING THEM MEANS
    # DISABLING THE INTERNAL ONES - that is a firmware change, not a rework.
    for ref, net, note in [("C14", "XL1", "X1 load, DNP"),
                           ("C15", "XL2", "X1 load, DNP"),
                           ("C16", "XC1", "X2 load, DNP"),
                           ("C17", "XC2", "X2 load, DNP")]:
        s.part(ref, "Device:C", value="DNP", group="clocks", footprint=C0201,
               dnp=True, in_bom=False,
               fields={"Note": "NOT FITTED. " + note + ". Internal CAPVALUE "
                               "load capacitors are used instead. Fit ONLY "
                               "with the internal ones disabled."})
        s.net(net, ref + ".1")
        s.net("GND", ref + ".2")

    # =====================================================================
    # BLOCK 4 - 2.4 GHz: Nordic's reference network, then a tuning pi
    # =====================================================================
    s.part("AE1", "Device:Antenna", value="2G4 PCB antenna", group="rf",
           fields={"Note": "ETCHED COPPER, NOT A BOUGHT PART, and therefore "
                           "DELIBERATELY WITHOUT A FOOTPRINT - bin/sch check "
                           "reports it CANNOT DETERMINE, which is the true "
                           "answer. Geometry is ce-rf's (lane T3) on the "
                           "Ø26.00 outline with the cell can in the model."})
    for ref, val, note in [("L2", "2.7nH", "0201 LQP03HQ2N7B02, Nordic ref"),
                           ("L3", "3.5nH", "0201 LQP03HQ3N5B02, Nordic ref"),
                           ("L4", "3.5nH", "0201, = L3, Nordic ref")]:
        # One code per VALUE, per S1: C1046539 is not in the catalogue as an
        # inductor at all (2026-09-04 audit: a 33 MHz MEMS oscillator).
        code, mpn = {"L2": ("C7216765", "LQP03HQ2N7B02D"),
                     "L3": ("C3911055", "LQP03HQ3N5B02D"),
                     "L4": ("C3911055", "LQP03HQ3N5B02D")}[ref]
        s.part(ref, "Device:L", value=val, group="rf", footprint=L0201,
               fields=P(code, mpn, "Murata", "$0.0168",
                        "in stock", {"Note": note + " Code re-verified "
                                     "2026-09-05 (S1).", "Tol": "+/-0.1nH"}))
    for ref, val, note in [
            ("C18", "1.5pF", "0201 NP0 high-Q. LAYOUT RULE: its ground "
                             "connects ONLY to pin 32 (VSS_PA), on the top "
                             "layer. Nordic's words, Figure 175."),
            ("C19", "2.0pF", "0201 NP0. LAYOUT RULE: its ground MUST be "
                             "isolated from every ground layer except the "
                             "bottom. Nordic's words, Figure 175."),
            ("C22", "0.3pF", "0201 C0G, series trim into the pi"),
            ("C23", "3.9pF", "0201 C0G - Table 82 lists it, Figure 175's "
                             "extraction does not place its node. Wired as a "
                             "shunt at ANT. CANNOT DETERMINE.")]:
        # One code per VALUE, per S1: C1568 is a 4 pF 0402 and was serving
        # six different capacitor values at once (2026-09-04 audit).
        code, mpn = {"C18": ("C435397", "GJM0335C1E1R5WB01D"),
                     "C19": ("C668326", "GJM0335C1E2R0WB01D"),
                     "C22": ("C3904589", "GJM0335C1HR30WB01D"),
                     "C23": ("C1852416", "GJM0335C1E3R9WB01D")}[ref]
        s.part(ref, "Device:C", value=val, group="rf", footprint=C0201,
               fields=P(code, mpn, "Murata", "$0.0262",
                        "in stock", {"Note": note + " Code re-verified "
                                     "2026-09-05 (S1).", "Tol": "+/-0.05pF"}))

    s.net("RF_ANT", "U1.31", "L2.1", "C23.1")
    s.net("RF_A", "L2.2", "C18.1", "L3.1")
    s.net("RF_B", "L3.2", "C19.1", "L4.1")
    s.net("RF_50", "L4.2", "C22.1", "C20.1", "L10.1")
    for ref in ("C18", "C19", "C22", "C23"):
        s.net("GND", ref + ".2")

    # D-2: the pi. C20 shunt - L10 series - C21 shunt, between the 50 ohm
    # node and the antenna feed. ALL THREE ARE PLACEHOLDERS: the values below
    # are a starting guess for a slightly-inductive feed, and they are what
    # ce-rf's measured S11 replaces. A pi with unmeasured values is a tuning
    # mechanism, not a match, and X-3 says so on the sheet.
    s.part("C20", "Device:C", value="0.5pF", group="rf", footprint=C0201,
           fields=P("C237424", "GJM0335C1HR50WB01D", "Murata", "$0.0223",
                    "in stock",
                    {"Note": "PI SHUNT, source side. PLACEHOLDER - value "
                             "comes from ce-rf S11 on the real copper. Code "
                             "re-verified 2026-09-05: C1568 is 4 pF 0402 "
                             "(S1)."}))
    s.part("L10", "Device:L", value="0R", group="rf", footprint=L0201,
           fields=P("C473473", "0201WMF0000TEE", "UNI-ROYAL", "$0.0010",
                    "in stock",
                    {"Note": "PI SERIES, fitted as a 0 ohm jumper so the "
                             "board works untuned. Replaced by an inductor "
                             "if ce-rf's S11 asks for one. Code re-verified "
                             "2026-09-05: C25076 is 100 R 0402 (S1)."}))
    s.part("C21", "Device:C", value="0.5pF", group="rf", footprint=C0201,
           fields=P("C237424", "GJM0335C1HR50WB01D", "Murata", "$0.0223",
                    "in stock",
                    {"Note": "PI SHUNT, antenna side. PLACEHOLDER, as C20."}))
    s.net("ANT_FEED", "L10.2", "C21.1", "AE1.1")
    s.net("GND", "C20.2", "C21.2")

    # =====================================================================
    # BLOCK 5 - NFC: the SoC's own tag peripheral. THERE IS NO NFC CHIP.
    # =====================================================================
    # SPEC.md §3: no separate NFC front end exists in an AirTag either. The
    # whole BOM line is the coil (etched, free) and two capacitors.
    s.part("AE2", "Device:Antenna_Loop", value="NFC coil 13.56MHz",
           group="nfc",
           fields={"Note": "ETCHED COPPER on the outer annulus, no footprint "
                           "on purpose. Its inductance is ce-rf's "
                           "measurement and it drives C24/C25's value."})
    # 1.1 nF, NOT the 130 pF this sheet carried first, and the difference is
    # a measurement rather than an opinion. Nordic's NFCT chapter quotes
    # about 130 pF per pin FOR A 2 uH ANTENNA. Our coil is not 2 uH: ce-rf
    # measured the real 2-turn Ø21.5 mm winding at 0.2449 uH - eight times
    # smaller, because the annulus between the cell can and the battery
    # contact lands is 0.70 mm wide and holds two turns, not five. The same
    # run returns C_external = 554.6 pF ACROSS the coil, and Nordic's
    # topology puts C24 and C25 in series across it, so each is twice that:
    # 1.109 nF. See sim/halo-rev-a-nfc.json and out/release/board/sim.
    for ref in ("C24", "C25"):
        s.part(ref, "Device:C", value="1.0nF", group="nfc", footprint=C0201,
               fields=P("C161371", "GRM0335C1E102JA01D", "muRata", "TBC",
                        "139,150",
                        {"Note": "NFC tuning. 1.109 nF was the arithmetic; "
                                 "1.0 nF is what exists. Lane S1 searched the "
                                 "catalogue: NO 1.1 nF CAPACITOR EXISTS IN "
                                 "0201 IN ANY DIELECTRIC, none in 0402 "
                                 "either, and the smallest 1.1 nF anywhere is "
                                 "0603 - three sizes too big for this board. "
                                 "1.2 nF C0G does not exist in 0201 either, "
                                 "so there is not even a bracketing pair. "
                                 "THE FIX IS IN COPPER, NOT IN THE BOM: the "
                                 "tank tunes on L*C, so dropping each "
                                 "capacitor 1.109 -> 1.0 nF drops the series "
                                 "capacitance 554.6 -> 500 pF and the coil "
                                 "must rise by the same ratio, 554.6/500 = "
                                 "1.1092, from ce-rf's measured 0.2449 uH to "
                                 "0.2716 uH. footprints.py NFC_TURNS is 2.106 "
                                 "for that reason and the etched coil costs "
                                 "nothing to lengthen. The two capacitors "
                                 "must be MATCHED to each other - a mismatch "
                                 "unbalances the tag antenna. OPEN, and it is "
                                 "the whole tuning: the coil at 2.106 turns "
                                 "has NOT been re-solved by ce-rf, so its "
                                 "inductance is a TARGET, not a measurement, "
                                 "and the resonant frequency is CANNOT "
                                 "DETERMINE until that run exists."}))
        s.net("GND", ref + ".2")
    s.net("NFC1", "U1.3", "AE2.1", "C24.1")
    s.net("NFC2", "U1.4", "AE2.2", "C25.1")

    # =====================================================================
    # BLOCK 6 - THERE IS NO SPI NOR FLASH, and that is a correction
    # =====================================================================
    # Revision A carried a GD25LQ32EEIGR here, on VDD, which is the raw
    # CR2032 rail with no regulator anywhere on this board. THE PART'S
    # SUPPLY RANGE IS 1.65 TO 2.0 V. A fresh coin cell is 3.0 V, so it was
    # out of specification from the first second - the kind of fault that
    # half-works on a bench and fails in a field. Caught by the production
    # test lane reading this sheet, not by anything here.
    #
    # There were two ways out and the cheap one is right:
    #
    #   FIT A REGULATOR. That is what the real AirTag does - a TPS62746 buck
    #   to 1.8 V and an FPF2487 load switch (SPEC.md §3) - and it costs a
    #   part, an inductor, a rail, a test and board area this disc does not
    #   have. It buys nothing else, because nothing else on halo wants 1.8 V:
    #   the nRF54L10, the LIS2DW12TR and the bender all span the whole cell
    #   curve on their own.
    #
    #   DELETE THE FLASH. research/05 §3.7 and spec/bom-candidates.json
    #   already recommended omitting it, and the firmware lane has since
    #   measured the whole firmware at 13,164 bytes - 1.27 % of the
    #   nRF54L10's own 1 MB. The Find My stack's floor is 116.7 KB flash /
    #   21.5 KB RAM (SPEC.md §2a); DULT's 25-day owner-information retention
    #   and the rolling key window are kilobytes. There is nothing for an
    #   external memory to hold.
    #
    # So it is deleted, and with it a part, a rail problem, two pull-up
    # resistors, nine joints and a production test. The SPI pins stay
    # assigned and still reach J2, because the halo-uwb option needs them.
    #
    # IF REVISION B WANTS EXTERNAL FIRMWARE STAGING, the part to fit is NOT
    # another GD25LQ: it is a wide-range low-power NOR such as the Macronix
    # MX25R series, specified 1.65 to 3.6 V, which is the range a coin cell
    # actually presents. That is a sourcing job, not a redesign.

    # =====================================================================
    # BLOCK 7 - accelerometer, on I2C (D-1)
    # =====================================================================
    s.part("U2", acc_id, value="LIS2DW12TR", group="accel",
           footprint="Package_LGA:LGA-12_2x2mm_P0.5mm",
           datasheet="https://www.st.com/resource/en/datasheet/lis2dw12.pdf",
           fields=P("C189624", "LIS2DW12TR", "STMicroelectronics", "$0.7408",
                    "14651",
                    {"Note": "<1 uA low-power mode. SPEC.md F7: sample every "
                             "10 s at rest, 0.5 s once moving. LGA-12 2x2, "
                             "0.7 mm tall."}))
    s.net("VDD", "U2.9", "U2.10")           # VDD and VDD_IO
    s.net("GND", "U2.6", "U2.8")
    # Datasheet Table 1, verbatim: pin 7 RES "connect to GND"; pin 5 NC "can
    # be tied to VDD, VDDIO or GND". Both are the datasheet's instruction.
    s.net("GND", "U2.5", "U2.7")
    # I2C mode select: CS HIGH selects I2C, SA0 LOW sets address 0x18. Both
    # are straps, and both are done through a resistor rather than a via to
    # the plane so the mode can be changed on a bring-up board.
    s.part("R5", "Device:R", value="10k", group="accel", footprint=R0201,
           fields=P("C473048", "0201WMF1002TEE", "UNI-ROYAL", "$0.0010",
                    "in stock",
                    {"Note": "CS strapped HIGH = I2C mode (DS11811 §5). "
                             "Through a resistor, not a via, so SPI can be "
                             "selected on a bring-up board by moving it. "
                             "Code re-verified 2026-09-05: C25744 is 0402 "
                             "under an 0201 land (S1)."}))
    s.part("R6", "Device:R", value="10k", group="accel", footprint=R0201,
           fields=P("C473048", "0201WMF1002TEE", "UNI-ROYAL", "$0.0010",
                    "in stock", {"Note": "SA0 strapped LOW = address 0x18"}))
    s.net("VDD", "R5.1")
    s.net("ACC_CS", "R5.2", "U2.2")
    s.net("ACC_SA0", "R6.1", "U2.3")
    s.net("GND", "R6.2")
    # The bus. 10k pull-ups: at 400 kHz over 15 mm of trace the rise time is
    # dominated by ~10 pF of bus capacitance, so 10k gives ~0.1 us against a
    # 0.3 us budget, and it costs 300 uA only while a device holds the line
    # down - microseconds per 10-second sample.
    for ref, net in (("R7", "I2C_SCL"), ("R8", "I2C_SDA")):
        s.part(ref, "Device:R", value="10k", group="accel", footprint=R0201,
               fields=P("C473048", "0201WMF1002TEE", "UNI-ROYAL", "$0.0010",
                        "in stock", {"Note": "I2C bus pull-up"}))
        s.net("VDD", ref + ".1")
        s.net(net, ref + ".2")
    s.net("I2C_SCL", "U1.17", "U2.1")       # P2.06
    s.net("I2C_SDA", "U1.19", "U2.4")       # P2.08
    s.net("ACC_INT1", "U1.20", "U2.12")     # P2.09 - the wake line, F7
    s.net("ACC_INT2", "U1.21", "U2.11")     # P2.10 - orientation, D12

    # =====================================================================
    # BLOCK 8 - the sounder: D11a, two pins, anti-phase, no amplifier
    # =====================================================================
    # §11.6's arithmetic, restated because it is the reason there is no
    # MAX98357A here: a bridge-tied class-D swings +/-Vbat, about 6 Vpp from
    # a 3 V cell. Two GPIO driven anti-phase swing THE SAME 6 Vpp. What the
    # amplifier bought was current, and a bender is capacitive: at 20-30 nF
    # and 4 kHz, I = 2*pi*f*C*V is 1.5-2.3 mA peak, inside nRF54L high-drive.
    # The amplifier was the right part for Apple's 8 ohm voice coil and the
    # wrong part for a bender.
    s.part("LS1", "Device:Buzzer", value="7BB-20-3", group="sounder",
           fields={"MPN": "7BB-20-3", "Manufacturer": "Murata",
                   "LCSC Part #": "NOT IN CATALOGUE",
                   "Note": "NO FOOTPRINT ON PURPOSE: a bare Ø20.0 x 0.22 mm "
                           "bender BONDED TO THE INSIDE OF THE SHELL, wired "
                           "to the board, not soldered to it. Two flying "
                           "leads land on pads the layout draws. PRICE AND "
                           "STOCK ARE UNKNOWN - research/05 §11.7: not in "
                           "LCSC or JLCPCB, Digi-Key 403, Mouser captcha. "
                           "One rep quote closes it."})
    s.part("R9", "Device:R", value="100R", group="sounder", footprint=R0201,
           fields=P("C270366", "0201WMF1000TEE", "UNI-ROYAL", "$0.0012",
                    "in stock",
                    {"Note": "series damping on one leg, and it EARNS ITS "
                             "PLACE - measured, not argued. A bender is a "
                             "near-pure capacitance and a GPIO edge into it "
                             "is a current spike off the bulk capacitors. "
                             "sim/sounder_drive.py: with a low-loss 40 nF "
                             "bender the peak pin current is 32.0 mA with R9 "
                             "removed and 17.8 mA with it fitted - a 44 % "
                             "cut, and the difference between exceeding and "
                             "clearing a 25 mA ceiling. An earlier note here "
                             "said '100 R holds the peak near 30 mA', which "
                             "had the right magnitude and the wrong side of "
                             "it."}))
    s.net("PIEZO_P", "U1.39", "R9.1")       # P1.11
    s.net("PIEZO_DRV", "R9.2", "LS1.1")
    s.net("PIEZO_N", "U1.40", "LS1.2")      # P1.12

    # =====================================================================
    # BLOCK 9 - SWD, on pads, and the reserved UWB stub
    # =====================================================================
    s.part("J1", "Connector:Conn_ARM_SWD_TagConnect_TC2030", value="TC2030",
           group="debug",
           footprint="Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical",
           fields={"Note": "NO CONNECTOR IS FITTED. These are pogo-pin pads, "
                           "which cost 0 mm of height - the only debug "
                           "interface that fits SPEC.md §4's 1.5 mm budget.",
                   "LCSC Part #": "n/a"})
    s.part("R10", "Device:R", value="10k", group="debug", footprint=R0201,
           fields=P("C473048", "0201WMF1002TEE", "UNI-ROYAL", "$0.0010",
                    "in stock",
                    {"Note": "nRESET pull-up. Table 82 says 1k; 10k is used "
                             "because 1k across a coin cell is 3 mA if "
                             "anything ever holds reset low, and the "
                             "nRESET input's leakage is nanoamps."}))
    s.net("VDD", "J1.1", "R10.1")
    s.net("GND", "J1.5")
    s.net("SWDIO", "U1.25", "J1.2")
    s.net("SWDCLK", "U1.26", "J1.4")
    s.net("nRESET", "U1.30", "J1.3", "R10.2")
    s.net("SWO", "U1.18", "J1.6")           # P2.07/SWO

    # X-1: the UWB option, as a stub rather than a guessed land pattern.
    s.part("J2", "Connector_Generic:Conn_01x08", value="UWB stub",
           group="uwb", footprint="halo:HALO_UWB_LANDS_1x08_P1.00",
           fields={"Note": "8 SMD LANDS just inboard of the board edge, "
                           "reserving the halo-uwb option of D12 WITHOUT "
                           "drawing a DW3110 land pattern nobody has the pin "
                           "table for. Not fitted, not populated, costs one "
                           "row of plated edge slots. See X-1.",
                   "LCSC Part #": "n/a"})
    s.net("SPI_SCK", "U1.12")               # P2.01/SCK, out to J2 only
    s.net("SPI_MOSI", "U1.13")              # P2.02/SDO
    s.net("SPI_MISO", "U1.15")              # P2.04/SDI
    s.net("VDD", "J2.1")
    s.net("GND", "J2.2")
    s.net("SPI_SCK", "J2.3")
    s.net("SPI_MOSI", "J2.4")
    s.net("SPI_MISO", "J2.5")
    s.net("UWB_CS", "U1.23", "J2.6")        # P0.00
    s.net("UWB_IRQ", "U1.24", "J2.7")       # P0.01
    s.net("UWB_RST", "U1.27", "J2.8")       # P0.02

    # =====================================================================
    # BLOCK 10 - TEST ACCESS, designed in rather than left to the fixture
    # =====================================================================
    # Asked for by the production test lane, and every one of these exists
    # because a fixture cannot reach the net any other way once the shell is
    # bonded. Stage two of the test plan probes the board IN ITS CARRIER,
    # before the adhesive joint closes; after that the programming pads and
    # every battery pad are sealed inside permanently. So these must survive
    # until that step and be reachable AT it, which puts every one of them on
    # the TOP face.
    #
    # FORCE AND SENSE ARE SEPARATE PADS, and that is the whole point of four
    # of them. Sleep current on this board is single-digit microamps; a
    # two-wire measurement puts the probe's own contact resistance in series
    # with the thing being measured, and two probes landing in one battery
    # pad is a two-wire measurement wearing a four-wire name. Force carries
    # the current, sense carries none.
    TESTPOINTS = [
        ("TP1", "VDD", "VDD FORCE - carries the measurement current"),
        ("TP2", "VDD", "VDD SENSE - carries none, so contact resistance "
                       "does not appear in the reading"),
        ("TP3", "GND", "GND FORCE"),
        ("TP4", "GND", "GND SENSE"),
        ("TP5", "PIEZO_P", "the bender bonds to the SHELL, so this net "
                           "terminates on a wire land and nowhere a probe "
                           "can otherwise reach"),
        ("TP6", "PIEZO_N", "the other bender leg; the pair is what proves "
                           "the anti-phase drive before a shell exists"),
        ("TP7", "VBAT_SNS", "D-5's cell-removal sense node - the "
                            "five-removals reset cannot be tested without "
                            "seeing it"),
        ("TP8", "I2C_SDA", "accelerometer bus, for diagnostics"),
        ("TP9", "I2C_SCL", "accelerometer bus, for diagnostics"),
        ("TP10", "NFC1", "NFC coil pin - the coil is etched, so there is no "
                         "component lead to clip onto"),
        ("TP11", "NFC2", "the other NFC pin; the pair is what a tuning "
                         "measurement needs"),
    ]
    for ref, net, note in TESTPOINTS:
        s.part(ref, "Connector:TestPoint", value="TP", group="test",
               footprint="halo:HALO_TP_D0.8",
               fields={"Note": note, "LCSC Part #": "n/a"})
        s.net(net, ref + ".1")

    # TWO FIDUCIALS, AND THEY ARE ASYMMETRIC ON PURPOSE. A 26 mm circle has
    # no datum: it looks the same from every angle, so a placement machine
    # and a probe fixture have nothing to register against and the position
    # of every other pad is a guess. Two fiducials at different radii and a
    # non-diametric angle fix both position AND rotation, and being
    # asymmetric they also fix which way up the board is.
    for ref, note in (("FID1", "fiducial 1 of 2 - global datum. Placed at a "
                               "different radius from FID2 so the pair is "
                               "ASYMMETRIC and resolves rotation as well as "
                               "position."),
                      ("FID2", "fiducial 2 of 2 - the asymmetric partner")):
        # `Mechanical:Fiducial` is a ZERO-PIN symbol, which is exactly
        # right: a fiducial is bare copper with no net and no connection. A
        # two-pin Device:D was tried first and the board refused it by name -
        # "FID1 (Fiducial:Fiducial_1mm_Mask2mm) has no pad '2'" - because the
        # land pattern has no pads at all. A diode on a schematic that is not
        # a diode is how a wrong part reaches a fab, so the refusal was
        # right and this is the fix rather than a workaround.
        s.part(ref, "Mechanical:Fiducial", value="FIDUCIAL", group="test",
               footprint="Fiducial:Fiducial_0.5mm_Mask1mm", in_bom=False,
               fields={"Note": note, "LCSC Part #": "n/a"})

    s.power("VDD", "GND")

    # -- the sentences a reviewer needs, on the sheet itself ---------------
    s.text("halo revision A. Board Ø26.00 x 0.60 mm, 4 layers, three 26 deg "
           "keying notches at 0/120/240 deg to R12.60 (lane M, design.py). "
           "Ø31.87 mm is the SHELL max OD at z=4.339, NOT the board.")
    s.text("LAYOUT RULES THAT TRAVEL WITH THIS SHEET (Nordic Figure 175, "
           "verbatim): C18's ground connects ONLY to pin 32 (VSS_PA) on the "
           "top layer. C19's ground MUST be isolated from every ground layer "
           "except the bottom. U1 pad 49 MUST tie to VSS pins 32 and 44.")
    s.text("PLACEHOLDERS, not results: the pi network C20/L10/C21 and the "
           "NFC tuning C24/C25 are seeded values awaiting ce-rf's measured "
           "S11 and coil inductance on the real Ø26.00 copper.")
    s.text("HEIGHT DELTA, open against lane M: a QFN48 is 0.85 mm and the "
           "stack allows 0.400 mm on the top face inside Ø21.2 and about "
           "0.578 mm on the bottom face over the cell. Short by ~0.32 mm. "
           "L1 (0.9 mm) and X1 (0.9 mm) are bound by the same delta.")
    s.text("C14-C17 ARE NOT FITTED. The nRF54L's on-die CAPVALUE load "
           "capacitors are used. Fitting these as well double-loads the "
           "crystal; populate ONLY with the internal ones disabled.")
    s.text("TEST ACCESS (block 10): TP1/TP2 are VDD FORCE and SENSE and "
           "TP3/TP4 are GND FORCE and SENSE - four wires, because sleep "
           "current here is single-digit microamps and a two-wire reading "
           "measures the probe. FID1/FID2 are ASYMMETRIC: a 26 mm circle "
           "has no datum and without them every pad position is a guess.")
    s.text("IPC-A-610 ACCEPTANCE CLASS 2. Class 3 is for equipment whose "
           "failure cannot be tolerated - life support, avionics - and halo "
           "is not that. Class 1 is general consumer electronics where "
           "cosmetics do not matter, and a product with a DULT safety "
           "obligation and a user-replaceable cell is not that either. The "
           "AOI recipe is built from this line, so it is recorded here "
           "rather than left for the factory to choose.")
    s.text("THERE IS NO SPI NOR FLASH. The GD25LQ32E first drawn here is a "
           "1.65-2.0 V part and this board's only rail is a raw 3.0 V coin "
           "cell. Block 6 carries the argument; the firmware is 13,164 "
           "bytes, 1.27 % of the SoC's own 1 MB.")
    s.text("CELL REMOVAL: BT1 pad 1 carries current into VDD, BT1 pad 3 is "
           "SENSE ONLY through R1/R2 into AIN0, and R2 returns to a GPIO so "
           "the divider draws nothing while idle. Pull the cell and "
           "VBAT_SNS collapses in ~0.24 ms while the bulk holds VDD up.")

    s.unused_gpio = s.nc_unused()
    return s


SUBSTITUTIONS = [
    # (U3, the SPI NOR, was deleted in rev A - see block 6. Its symbol
    #  substitution note is kept out of this list because the part is not on
    #  the board; a substitution nobody fitted is not a substitution.)
    ("X2", "2-pad 2016 crystal (Nordic's BOM)",
     "Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm",
     "KiCad ships no 2-pin 2016 land pattern; the can is grounded, which is "
     "better RF practice than leaving it floating"),
    ("AE1", "etched 2.4 GHz antenna", "Device:Antenna",
     "a shape in copper is not a bought part; the symbol is a terminal so "
     "the matching network has somewhere to end"),
    ("AE2", "etched NFC coil", "Device:Antenna_Loop", "same reason"),
    ("LS1", "Murata 7BB-20-3 bare bender", "Device:Buzzer",
     "a bare bender is two terminals. It is NOT a housed buzzer and D11a is "
     "explicit that a housed buzzer does not fit"),
    ("BT1", "three sprung C5191 fingers", "Device:Battery_Cell",
     "SPEC.md §4: no coin-cell retainer under 2 mm exists, so there is no "
     "catalogue footprint. The land pattern is halo's own, drawn by layout"),
    ("J2", "reserved DW3110 land pattern", "Connector_Generic:Conn_01x08",
     "the DW3110 pin table is in no document in this repo and D9 forbids "
     "guessing 48 net names; and a second 6x6 QFN does not fit Ø26 mm"),
]

CANNOT_DETERMINE = [
    "C6 / C7 node - Nordic Table 82 lists them, Figure 175's text extraction "
    "does not place them. Wired to DECD here.",
    "C23 node - same. Wired as a shunt at ANT here.",
    "NFC tuning 130 pF - assumes Lant = 2 uH on a coil nobody has measured.",
    "Pi network C20/L10/C21 values - awaiting ce-rf S11 on the real copper.",
    "DW3110 land pattern - no sourced pin table exists; a stub is reserved.",
    "Murata 7BB-20-3 price and stock - not in any catalogue that answers a "
    "machine (research/05 §11.7).",
    "GPIO function assignment - legal on any pin via PSEL, so free, and "
    "therefore unverified against a firmware build.",
    "Component height - the SoC, L1 and X1 all exceed lane M's stack "
    "allowance. Reported to M, not absorbed.",
]


if __name__ == "__main__":
    s = build()

    for sev, msg in s.check():
        print("%-17s %s" % (sev, msg))

    unused = s.unused_gpio
    print("\n--- deliberately not connected (%d pins) ---" % len(unused))
    for key, name in unused:
        print("  %-10s %s" % (key, name))

    s.place()
    print("\n" + s.describe())
    out = s.save(os.path.join(HERE, "out", s.name + ".kicad_sch"))
    print("\nwrote", out)

    print("\n--- symbol substitutions ---")
    for ref, wanted, used, why in SUBSTITUTIONS:
        print("  %-4s %-38s -> %s\n       %s" % (ref, wanted, used, why))

    print("\n--- CANNOT DETERMINE, carried openly ---")
    for line in CANNOT_DETERMINE:
        print("  " + line)
