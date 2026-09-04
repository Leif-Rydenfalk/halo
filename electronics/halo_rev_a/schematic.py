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
X-2  NFC TUNING IS 130 pF ON AN UNMEASURED COIL. Nordic's NFCT chapter says
     a 2 uH antenna wants about 130 pF per pin. Our coil's inductance is
     ce-rf's measurement and it has not been made on the real Ø26 outline.
     The value is a PLACEHOLDER and the convergence table says so.
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
    """One BOM line's sourcing, as schematic fields."""
    f = {"LCSC": lcsc, "MPN": mpn, "Manufacturer": mfr, "Priced": PULLED}
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
               fields=P("C1546", "CL03A104KA3NNNC", "Samsung", "$0.0029",
                        "in stock",
                        {"Note": "0201 X7R 16V, " + note,
                         "Tol": "10%"}))
        s.net("VDD", ref + ".1")
        s.net("GND", ref + ".2")

    # The SoC's own DC/DC. DCC -- L1 -- DECD, then DECA tied to DECRF because
    # the datasheet says "Must be connected to DECA", not because it is tidy.
    s.part("L1", "Device:L", value="4.7uH", group="power",
           footprint="Inductor_SMD:L_0603_1608Metric",
           fields=P("C1046", "MLZ1608M4R7WT000", "TDK", "$0.0180", "in stock",
                    {"Note": "0603 multilayer, >=120 mA Isat, DCC->DECD. "
                             "0603 is 0.9 mm tall: BOTTOM FACE ONLY, and it "
                             "is one of the parts X-5's height delta binds."}))
    s.net("DCC", "U1.46", "L1.1")
    s.net("DECD", "U1.45", "L1.2")

    for ref, val, note in [
            ("C5", "2.2uF", "0201 X6T 6.3V, DECD reservoir (Table 82)"),
            ("C6", "10nF", "0201 X7R - Table 82 lists it, Figure 175's "
                           "extraction does not place its node. Wired to "
                           "DECD. CANNOT DETERMINE against the source."),
            ("C7", "2.2nF", "0201 X7R - same, CANNOT DETERMINE")]:
        s.part(ref, "Device:C", value=val, group="power", footprint=C0201,
               fields=P("C2827888", "CL03A225MQ3CSNC", "Samsung", "$0.0091",
                        "in stock", {"Note": note}))
        s.net("DECD", ref + ".1")
        s.net("GND", ref + ".2")

    s.part("C8", "Device:C", value="2.2uF", group="power", footprint=C0201,
           fields=P("C2827888", "CL03A225MQ3CSNC", "Samsung", "$0.0091",
                    "in stock", {"Note": "0201 X6T, on the DECA=DECRF node"}))
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
           fields=P("C7498149", "CR2032", "Panasonic", "$0.39", "in stock",
                    {"Note": "THE FOOTPRINT IS halo's OWN, drawn by the "
                             "layout: three pads at the radii lane M fixed "
                             "(R_CONTACT_POS 9.50 x2, R_CONTACT_NEG 6.00 x1, "
                             "design.py). Pad 1 = P+ current finger, pad 3 = "
                             "P+ SENSE finger, pad 2 = negative."}))
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
           fields=P("C25765", "0201WMF4704TEE", "UNI-ROYAL", "$0.0012",
                    "in stock", {"Note": "sense divider, high leg"}))
    s.part("R2", "Device:R", value="4.7M", group="battery", footprint=R0201,
           fields=P("C25765", "0201WMF4704TEE", "UNI-ROYAL", "$0.0012",
                    "in stock",
                    {"Note": "sense divider, low leg - returns to a GPIO, "
                             "not to GND, so the divider is OFF when idle"}))
    s.part("C13", "Device:C", value="100pF", group="battery", footprint=C0201,
           fields=P("C1523", "CL03C101JB3NNNC", "Samsung", "$0.0029",
                    "in stock",
                    {"Note": "settles the divider inside the ADC's "
                             "acquisition window; also sets the ~0.24 ms "
                             "collapse time when the cell leaves"}))
    s.net("VBAT_SNS_HI", "BT1.3", "R1.1")
    s.net("VBAT_SNS", "R1.2", "R2.1", "C13.1", "U1.5")      # P1.04/AIN0
    s.net("SNS_EN", "R2.2", "C13.2", "U1.6")                # P1.05/AIN1

    # =====================================================================
    # BLOCK 3 - the two oscillators
    # =====================================================================
    s.part("X1", "Device:Crystal", value="32.768kHz", group="clocks",
           footprint="Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm",
           fields=P("C620155", "X321532768KGD2SI", "Yangxing Tech", "$0.1347",
                    "in stock",
                    {"Note": "CL 12.5 pF, +/-20 ppm. 3.2x1.5x0.9 mm - 0.9 mm "
                             "TALL, which X-5's height delta also binds. A "
                             "2012 part would fit; none was priced by lane E."}))
    s.net("XL1", "U1.1", "X1.1")
    s.net("XL2", "U1.2", "X1.2")

    s.part("X2", "Device:Crystal_GND24", value="32MHz", group="clocks",
           footprint="Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm",
           fields=P("C843260", "NX2016SA-32MHZ", "NDK", "$0.2333", "in stock",
                    {"Note": "CL 8 pF, +/-10 ppm, 2.0x1.6x0.5 mm. Nordic's "
                             "BOM says a 2-pad 2016 and KiCad ships no 2-pin "
                             "2016 land pattern, so the 4-pad symbol is used "
                             "and the can is grounded - better RF practice "
                             "anyway. Recorded as a substitution."}))
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
        s.part(ref, "Device:L", value=val, group="rf", footprint=L0201,
               fields=P("C1046539", "LQP03HQ2N7B02D", "Murata", "$0.0304",
                        "in stock", {"Note": note, "Tol": "+/-0.1nH"}))
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
        s.part(ref, "Device:C", value=val, group="rf", footprint=C0201,
               fields=P("C1568", "GJM0335C1E1R5WB01", "Murata", "$0.0091",
                        "in stock", {"Note": note, "Tol": "+/-0.05pF"}))

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
           fields=P("C1568", "GJM0335C1ER50WB01", "Murata", "$0.0091",
                    "in stock",
                    {"Note": "PI SHUNT, source side. PLACEHOLDER - value "
                             "comes from ce-rf S11 on the real copper."}))
    s.part("L10", "Device:L", value="0R", group="rf", footprint=L0201,
           fields=P("C25076", "0201WMJ0000TEE", "UNI-ROYAL", "$0.0012",
                    "in stock",
                    {"Note": "PI SERIES, fitted as a 0 ohm jumper so the "
                             "board works untuned. Replaced by an inductor "
                             "if ce-rf's S11 asks for one."}))
    s.part("C21", "Device:C", value="0.5pF", group="rf", footprint=C0201,
           fields=P("C1568", "GJM0335C1ER50WB01", "Murata", "$0.0091",
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
    for ref in ("C24", "C25"):
        s.part(ref, "Device:C", value="130pF", group="nfc", footprint=C0201,
               fields=P("C1571", "CL03C131JB3NNNC", "Samsung", "$0.0029",
                        "in stock",
                        {"Note": "NFC tuning, PLACEHOLDER (X-2). 130 pF is "
                                 "Nordic's NFCT chapter for Lant = 2 uH. The "
                                 "two must be MATCHED to each other - a "
                                 "mismatch unbalances the tag antenna."}))
        s.net("GND", ref + ".2")
    s.net("NFC1", "U1.3", "AE2.1", "C24.1")
    s.net("NFC2", "U1.4", "AE2.2", "C25.1")

    # =====================================================================
    # BLOCK 6 - SPI NOR flash
    # =====================================================================
    # research/05 §3.7 argues this line can be dropped, because the L10's
    # 1 MB of NVM holds the Find My stack's 116.7 KB with room. It is kept
    # in rev A for three reasons the cost model does not weigh: DULT's
    # 25-day owner-information retention, the rolling-key window, and the
    # fact that an open project wants its key material in a part that can be
    # erased independently of the firmware. It is a $0.41 line.
    s.part("U3", "Memory_Flash:W25Q32JVSS", value="GD25LQ32E 32Mbit",
           group="flash",
           footprint="Package_SON:Winbond_USON-8-1EP_3x2mm_P0.5mm_EP0.2x1.6mm",
           datasheet="https://www.gigadevice.com/datasheet/gd25lq32e/",
           fields=P("C2939873", "GD25LQ32EEIGR", "GigaDevice", "$0.4105",
                    "JLC", {"Note": "SYMBOL SUBSTITUTION: KiCad's W25Q32JVSS "
                                    "is the same 8-pin serial-NOR pinout "
                                    "(CS DO WP GND DI CLK HOLD VCC). 1.65-"
                                    "3.6 V, so it spans the whole cell "
                                    "curve. USON-8 2x3 mm, 0.6 mm tall - "
                                    "chosen over SOIC-8 because the board is "
                                    "26 mm across. Its exposed pad has no "
                                    "symbol pin; bonding it is the LAYOUT's "
                                    "decision, recorded there, not here."}))
    s.net("SPI_SCK", "U1.12", "U3.6")       # P2.01/SCK
    s.net("SPI_MOSI", "U1.13", "U3.5")      # P2.02/SDO
    s.net("SPI_MISO", "U1.15", "U3.2")      # P2.04/SDI
    s.net("FLASH_CS", "U1.16", "U3.1")      # P2.05/CS
    s.net("VDD", "U3.8")
    s.net("GND", "U3.4")
    # WP and HOLD idle high through resistors rather than strapped to the
    # rail. KiCad types them bidirectional because in quad mode they are
    # IO2/IO3, and a hard tie would both make quad SPI impossible and short a
    # driven output into the rail.
    for ref, pad in (("R3", "3"), ("R4", "7")):
        s.part(ref, "Device:R", value="100k", group="flash", footprint=R0201,
               fields=P("C25741", "0201WMF1003TEE", "UNI-ROYAL", "$0.0012",
                        "in stock",
                        {"Note": "idle-high pull-up, 100k not 10k: 30 uA of "
                                 "leakage on a 2.4 uA sleep budget would "
                                 "have been the largest current on the board"}))
        s.net("VDD", ref + ".1")
        s.net("FLASH_%s" % ("WP" if pad == "3" else "HOLD"),
              ref + ".2", "U3." + pad)

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
           fields=P("C25744", "0201WMF1002TEE", "UNI-ROYAL", "$0.0012",
                    "in stock",
                    {"Note": "CS strapped HIGH = I2C mode (DS11811 §5). "
                             "Through a resistor, not a via, so SPI can be "
                             "selected on a bring-up board by moving it."}))
    s.part("R6", "Device:R", value="10k", group="accel", footprint=R0201,
           fields=P("C25744", "0201WMF1002TEE", "UNI-ROYAL", "$0.0012",
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
               fields=P("C25744", "0201WMF1002TEE", "UNI-ROYAL", "$0.0012",
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
                   "LCSC": "NOT IN CATALOGUE",
                   "Note": "NO FOOTPRINT ON PURPOSE: a bare Ø20.0 x 0.22 mm "
                           "bender BONDED TO THE INSIDE OF THE SHELL, wired "
                           "to the board, not soldered to it. Two flying "
                           "leads land on pads the layout draws. PRICE AND "
                           "STOCK ARE UNKNOWN - research/05 §11.7: not in "
                           "LCSC or JLCPCB, Digi-Key 403, Mouser captcha. "
                           "One rep quote closes it."})
    s.part("R9", "Device:R", value="100R", group="sounder", footprint=R0201,
           fields=P("C25076", "0201WMF1000TEE", "UNI-ROYAL", "$0.0012",
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
                   "LCSC": "n/a - pads only, no part"})
    s.part("R10", "Device:R", value="10k", group="debug", footprint=R0201,
           fields=P("C25744", "0201WMF1002TEE", "UNI-ROYAL", "$0.0012",
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
           group="uwb", footprint="halo:HALO_CASTELLATED_1x08_P1.00",
           fields={"Note": "8 CASTELLATED HALF-VIAS on the board edge, "
                           "reserving the halo-uwb option of D12 WITHOUT "
                           "drawing a DW3110 land pattern nobody has the pin "
                           "table for. Not fitted, not populated, costs one "
                           "row of plated edge slots. See X-1.",
                   "LCSC": "n/a - castellations, no part"})
    s.net("VDD", "J2.1")
    s.net("GND", "J2.2")
    s.net("SPI_SCK", "J2.3")
    s.net("SPI_MOSI", "J2.4")
    s.net("SPI_MISO", "J2.5")
    s.net("UWB_CS", "U1.23", "J2.6")        # P0.00
    s.net("UWB_IRQ", "U1.24", "J2.7")       # P0.01
    s.net("UWB_RST", "U1.27", "J2.8")       # P0.02

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
    s.text("CELL REMOVAL: BT1 pad 1 carries current into VDD, BT1 pad 3 is "
           "SENSE ONLY through R1/R2 into AIN0, and R2 returns to a GPIO so "
           "the divider draws nothing while idle. Pull the cell and "
           "VBAT_SNS collapses in ~0.24 ms while the bulk holds VDD up.")

    s.unused_gpio = s.nc_unused()
    return s


SUBSTITUTIONS = [
    ("U3", "GigaDevice GD25LQ32EEIGR", "Memory_Flash:W25Q32JVSS",
     "identical 8-pin serial-NOR pinout; KiCad has no GigaDevice symbol"),
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
