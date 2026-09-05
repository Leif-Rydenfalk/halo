"""halo Replica — THE FAB VARIANT. The one you can actually order and switch on.

    cd ~/dev/ce-workshop
    ce-pcb/bin/sch all ce-designs/halo/electronics/halo_replica/schematic/schematic_fab.py \
                   -o ce-designs/halo/electronics/halo_replica/out/schematic-fab

===========================================================================
THIS IS NOT THE REPLICA. READ THIS PARAGRAPH BEFORE ANYTHING ELSE.
===========================================================================
`schematic.py` beside this file is the FIDELITY RECORD: Apple's AirTag as
this project reconstructed it, with every net carrying MEASURED / INFERRED /
CHOSEN and 13 of its 52 nets measured. **Nothing in this file may be cited as
a finding about the AirTag.** It is a different circuit, built for a different
purpose: Leif asked for "the files ready to send to jlc pcb ... so i can try
it out if it works", and a board you can order is a board where every part is
buyable, every land pattern is real, and every value is a number.

The fidelity sheet is deliberately NOT buildable — eleven of its parts have no
footprint, every passive value is CANNOT DETERMINE, and its main UWB module
has never been sold to anyone. Filling those in would have destroyed the one
thing that sheet is for. So this is a SECOND sheet. The fidelity sheet is
untouched and stays the honest core.

**EVERY VALUE AND EVERY PART CHOICE HERE IS `CHOSEN`.** Not one of them is a
measurement of Apple's board. `DEPARTURES` at the bottom lists every place
this circuit differs from the reconstruction, with the reason.

===========================================================================
THE BIGGEST DEPARTURE, AND IT IS A DELETION — ONE RAIL, NOT THREE
===========================================================================
The reconstruction has CR2032 -> series diode -> buck -> 1.8 V -> load switch
-> 1.8 V flash. **This board deletes the buck and the 1.8 V rail entirely and
runs everything from the cell.**

That was forced, and then it turned out to be better:

* **FORCED.** KiCad ships no symbol for a coin-cell 1.8 V buck of the
  TPS62746 class. The fidelity sheet draws U6 with a symbol whose pin
  numbering is its own invention, and putting a REAL land pattern under an
  INVENTED pinout is precisely the defect that was just found and fixed on J1
  (a U.FL footprint under a part measured to be MHF4-class). There was no
  honest way to give U6 a real footprint.
* **BETTER.** The nRF52832 runs 1.7-3.6 V, which spans the whole CR2032
  discharge curve. The only reason 1.8 V exists in Apple's board is the 1.8 V
  flash and the UWB module — and the UWB module is not on this board because
  nobody can buy one. A buck from a coin cell is also the highest-risk block
  on a board whose entire purpose is to find out whether it works.
  `halo_rev_a` reached the same conclusion independently.

The flash becomes an **MX25R3235F**, 1.65-3.6 V, ultra-low-power, in KiCad's
own library and stocked by JLCPCB — it works at both ends of the cell's life,
which a 2.7 V part behind a Schottky would not.

**WHAT IS KEPT, because it is the one power idea worth copying:** the load
switch. O'Flynn measured that the nRF controls power to the SPI flash and
that the flash is off most of the time. That is why sleep is microamps, and
it survives here as a real MIC94090 gating the flash from a GPIO.

===========================================================================
WHAT IS NOT ON THIS BOARD, AND WHY
===========================================================================
U2   Apple's UWB SiP. NEVER SOLD TO ANYONE, and its pinout on the fidelity
     sheet is that sheet's own invention. A DNP part with a land pattern
     invites somebody to try to buy one. Off entirely, with ANT3 and J1.
J1   the coaxial receptacle. MEASURED to be MHF4-class and NOT a U.FL, and
     KiCad ships no MHF4 or W.FL land pattern. Rather than put a U.FL
     pattern under it — the exact defect just fixed — there is no connector.
U7   the op-amp. Its ROLE is this project's reconstruction, not an
     observation: it could be a buffer, a current-sense amp or a filter. A
     board should not carry a part whose purpose nobody knows.
U9   the part marked 1A8 / 1950. CANNOT DETERMINE down to its function, and
     its output on the fidelity sheet goes nowhere. Unbuyable and unplaceable.
U6   the buck, and L1 with it. See above.
R3/R4 and the second positive battery contact. A catalogue CR2032 holder has
     TWO terminals. Apple's three sprung contacts with both positives sensed
     cannot be reproduced with one, so this board senses the single positive
     and **the five-removals reset ritual is NOT reproduced**. Said plainly
     because it is a real loss of function, not a simplification.
"""
import json
import os
import sys

WORKSHOP = "/Users/leifrydenfalk/dev/ce-workshop"
if WORKSHOP not in sys.path:
    sys.path.insert(0, os.path.join(WORKSHOP, "ce-pcb"))

from cepcb.schematic import Schematic                              # noqa: E402
from cepcb.schematic import MEASURED, INFERRED, CHOSEN             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(REPLICA))
BOM_JSON = os.path.join(REPLICA, "bom", "bom.json")

# Land patterns and symbols, each verified present with cepcb on 2026-09-05.
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
R0402 = "Resistor_SMD:R_0402_1005Metric"

NETS = {}


def N(name, driver, loads, why):
    """Every net on this sheet is CHOSEN or INFERRED and none is MEASURED.

    There is no `basis` argument on purpose. A net on THIS sheet cannot be a
    measurement of Apple's board, because this is not Apple's board — and an
    API that let one be marked MEASURED here would be the one place the
    distinction the whole project rests on could be laundered.
    """
    if name in NETS:
        raise SystemExit("net %s described twice." % name)
    NETS[name] = (driver, loads, why)
    return name


def bom_refs():
    if not os.path.exists(BOM_JSON):
        raise SystemExit("CANNOT DETERMINE: %s is missing." % BOM_JSON)
    with open(BOM_JSON, "r", encoding="utf-8") as fh:
        return {ln["ref"] for ln in json.load(fh)["lines"]}


BOM = bom_refs()


def F(bom_ref, mpn, why_this_part, extra=None):
    """One buyable part. `bom_ref` is the fidelity sheet's line it stands in
    for, or None for something this board adds.

    THE FIELD NAMES MATTER: ce-fab looks for "LCSC Part #" and a plain "LCSC"
    is in none of its accepted spellings, which once cost 42 of 44 parts their
    order codes. No LCSC code is invented here — this lane did not pull a
    price ladder, and a code with no pull date is a rumour. `mpn` is a real
    manufacturer part number and the fab lane sources against it.
    """
    if bom_ref is not None and bom_ref not in BOM:
        raise SystemExit("bom.json has no line %r" % bom_ref)
    f = {"MPN": mpn, "Substitution basis": why_this_part,
         "Stands in for": bom_ref or "nothing - added by the fab variant",
         "LCSC Part #": "CANNOT DETERMINE - no price pull was done by this "
                        "lane; source against MPN"}
    if extra:
        f.update(extra)
    return f


def build():
    s = Schematic(
        "halo_replica_fab",
        title="halo Replica FAB VARIANT - orderable, NOT the fidelity record",
        rev="F1", company="ce-designs/halo - halo Replica lane L11",
        comments=[
            "NOT A REPLICA. Every value and part choice here is CHOSEN.",
            "The fidelity record is schematic.py / NETS.md beside this file.",
            "One 3 V rail: the buck and the 1.8 V rail are DELETED.",
            "No UWB: U2 is never sold, so U2/ANT3/J1 are absent.",
        ])

    # =====================================================================
    # POWER - one rail, and a diode that D24 requires
    # =====================================================================
    s.part("BT1", "Device:Battery_Cell", value="CR2032 3V in a holder",
           group="power",
           footprint="Battery:BatteryHolder_Keystone_1060_1x2032",
           fields=F("BATT-CONTACTS", "Keystone 1060",
                    "Apple uses THREE sprung contacts with both positives "
                    "sensed and no holder at all. No catalogue holder has "
                    "three terminals, so this board has two and THE "
                    "FIVE-REMOVALS RESET RITUAL IS NOT REPRODUCED. A real "
                    "loss of function, not a simplification."))

    s.part("D1", "Device:D_Schottky", value="BAT54HT1G (Vf~0.24V @1mA)",
           group="power", footprint="Diode_SMD:D_SOD-323",
           fields=F(None, "BAT54HT1G",
                    "DECISIONS.md D24 requires a series diode between the "
                    "cell and the device: an NFC field pushes current "
                    "backwards through parasitic diodes and a CR2032 does "
                    "not tolerate it. A Schottky is CHOSEN over an "
                    "ideal-diode controller because this board is a "
                    "first-article test, and its forward drop is the reason "
                    "the flash here must work down to 1.65 V.",
                    {"Cost of this part": "~0.24 V of the cell's 3.0 V"}))

    N("VBAT_RAW", "BT1 +", "D1 anode; R1 (sense divider)",
      "The cell. On Apple's board there are two positive contacts and both "
      "are sensed; here there is one.")
    s.net("VBAT_RAW", "BT1.1", "D1.1", "R1.1")

    N("VBAT", "D1 cathode",
      "U1 VDD x3; U3 through U2sw; U4; U5; the bulk capacitors",
      "THE ONLY RAIL ON THIS BOARD. Everything runs from the cell: the "
      "nRF52832 is 1.7-3.6 V, the MX25R flash 1.65-3.6 V, the SC7A20 "
      "1.8-3.6 V and the MAX98357A 2.5-5.5 V. The buck and the 1.8 V rail "
      "the reconstruction carries are deleted - see the module docstring.")
    s.net("VBAT", "D1.2")
    s.net("GND", "BT1.2")

    for ref in ("C1", "C2", "C3", "C4", "C5"):
        s.part(ref, "Device:C", value="100uF 6.3V X5R", group="power",
               footprint=C0805,
               fields=F("C1..C5", "CL21A107MQNNNNE",
                        "DECISIONS.md D23 counts FIVE 100 uF bulk "
                        "capacitors on Apple's board and this board keeps "
                        "the count. On a coin cell they are what lets a "
                        "class-D amplifier make a noise at all: the cell's "
                        "internal resistance cannot supply the peak."))
        s.net("VBAT", ref + ".1")
        s.net("GND", ref + ".2")

    # The load switch. THIS is the part of Apple's power design worth copying.
    s.part("U2", "Power_Management:MIC94090YC6",
           value="MIC94090YC6 (0.5 uA, 1.5 A)", group="power",
           footprint="Package_TO_SOT_SMD:SOT-363_SC-70-6",
           fields=F("U8", "MIC94090YC6",
                    "Stands in for the FPF2487-class load switch. O'Flynn "
                    "MEASURED that the nRF controls power to the SPI flash "
                    "and that the flash is off most of the time - that is "
                    "why sleep is microamps, and it is the one power idea on "
                    "Apple's board worth copying exactly. The MIC94090's "
                    "0.5 uA quiescent is what makes it worth having.",
                    {"NOTE": "On this sheet U2 is the LOAD SWITCH. On the "
                             "fidelity sheet U2 is Apple's UWB module, which "
                             "is not on this board. Do not carry a U2 "
                             "reference between the two sheets."}))
    s.net("VBAT", "U2.4")
    s.net("GND", "U2.2", "U2.5")
    s.nc("U2.3")

    N("FLASH_PWR_EN", "U1.15 (P0.12)", "U2 EN",
      "CHOSEN pin. That a GPIO gates the flash is O'Flynn's measurement; "
      "which GPIO is this board's choice. It is NOT P0.15: that is Apple's "
      "measured flash CIPO, and putting the enable there collided with the "
      "I2S clock two blocks later. check() named the pin before anything "
      "was drawn.")
    s.net("FLASH_PWR_EN", "U1.15", "U2.6")

    N("VFLASH", "U2 OUT", "U3 VCC, nWP, nRESET; C6",
      "The switched rail. Off in sleep, which is the whole point.")
    s.net("VFLASH", "U2.1")

    s.part("C6", "Device:C", value="1uF 16V X7R", group="power",
           footprint=C0402,
           fields=F(None, "CL05A105KA5NNNC",
                    "Decoupling on the switched rail so the flash sees a "
                    "clean supply when the switch turns on."))
    s.net("VFLASH", "C6.1")
    s.net("GND", "C6.2")

    # Cell-removal sense, on the ONE positive this board has.
    for ref, val in (("R1", "10M"), ("R2", "10M")):
        s.part(ref, "Device:R", value=val, group="power", footprint=R0402,
               fields=F("R/C/L bulk", "RC0402FR-0710ML",
                        "A 20 Mohm divider draws 150 nA from a 3 V cell, the "
                        "order of magnitude REFERENCE-TEARDOWN reports for "
                        "Apple's own sense (~50 nA). The exact values are "
                        "CHOSEN; Apple's are unpublished."))
    N("VBAT_SENSE", "R1/R2 divider on VBAT_RAW", "U1.4 (P0.02/AIN0)",
      "Half the cell voltage into an ADC input, so firmware can read the "
      "cell and detect removal. ONE positive only - see DEPARTURES.")
    s.net("VBAT_SENSE", "R1.2", "R2.1", "U1.4")
    s.net("GND", "R2.2")

    # =====================================================================
    # THE SoC - and here the pin numbers finally match the part
    # =====================================================================
    s.part("U1", "MCU_Nordic:nRF52832-QFxx", value="nRF52832-QFAA-R",
           group="soc",
           footprint="Package_DFN_QFN:QFN-48-1EP_6x6mm_P0.4mm_EP4.4x4.4mm",
           datasheet="https://infocenter.nordicsemi.com/pdf/"
                     "nRF52832_PS_v1.4.pdf",
           fields=F("U1", "NRF52832-QFAA-R",
                    "THE SAME DIE AS APPLE'S, IN A PACKAGE THAT CAN BE "
                    "LANDED. Apple fits the CIAA, WLCSP-50, and no complete "
                    "ball map for it has ever been published - only ten of "
                    "the fifty balls are sourced anywhere in this "
                    "repository. The QFAA is QFN-48 6x6 P0.4, it is in "
                    "KiCad's library with a verified land pattern, and it is "
                    "stocked. THE FIDELITY SHEET IS ALREADY DRAWN WITH THIS "
                    "SYMBOL, so on this board the pin NUMBERS are the part's "
                    "own rather than merely right by signal name.",
                    {"Package delta": "QFN-48 6x6x0.9 mm vs Apple's "
                                      "WLCSP-50 3.0x3.2x0.5 mm. THIS BOARD "
                                      "IS NOT THE SIZE OF AN AIRTAG, and it "
                                      "is a FORK not a compromise: the "
                                      "WLCSP fits Apple's ~6 mm annular ring "
                                      "and cannot be landed; the QFN can be "
                                      "landed and does not fit. No "
                                      "arrangement is both. Carry this into "
                                      "every downstream artifact."}))

    for pad in ("13", "36", "48"):
        s.net("VBAT", "U1." + pad)
    for pad in ("31", "45", "49"):
        s.net("GND", "U1." + pad)

    # Nordic's decoupling. Values CHOSEN from the family's ordinary practice,
    # because this repository holds no copy of the reference circuit.
    # THE MPN IS PER-VALUE, NOT PER-LOOP. It was one string for all four
    # until bom_from_sch grouped by (value, footprint, MPN) and split "1uF"
    # into two lines that were supposed to be one: C10 is 1 uF and was
    # carrying CL05B104KO5NNNC, which is a 100 nF part. Nothing else on this
    # sheet could have caught that — the value field was right, the footprint
    # was right, and only the order number was wrong.
    for ref, pad, net, val, mpn in (
            ("C7", "1", "DEC1", "100nF 16V X7R", "CL05B104KO5NNNC"),
            ("C8", "32", "DEC2", "100nF 16V X7R", "CL05B104KO5NNNC"),
            ("C9", "33", "DEC3", "100nF 16V X7R", "CL05B104KO5NNNC"),
            ("C10", "46", "DEC4", "1uF 16V X7R", "CL05A105KA5NNNC")):
        s.part(ref, "Device:C", value=val, group="soc", footprint=C0402,
               fields=F("R/C/L bulk", mpn,
                        "Decoupling at the SoC's on-die regulator pin %s. "
                        "VALUE CHOSEN: no copy of the nRF52832 reference "
                        "circuit is in this repository, so this is ordinary "
                        "practice for the family and not a datasheet "
                        "number." % net))
        s.net(net, "U1." + pad, ref + ".1")
        s.net("GND", ref + ".2")
        N(net, "U1 pin " + pad, ref,
          "On-die regulator decoupling. Value CHOSEN, not sourced.")

    for ref, pad, val in (("C11", "13", "100nF 16V X7R"),
                          ("C12", "36", "100nF 16V X7R"),
                          ("C13", "48", "100nF 16V X7R")):
        s.part(ref, "Device:C", value=val, group="soc", footprint=C0402,
               fields=F("R/C/L bulk", "CL05B104KO5NNNC",
                        "Per-pin supply decoupling at VDD pin " + pad + "."))
        s.net("VBAT", ref + ".1")
        s.net("GND", ref + ".2")

    # The SoC's own DC/DC is NOT used, and that is a decision with a reason.
    s.nc("U1.47")
    s.part("C14", "Device:C", value="DNP - see note", group="soc",
           footprint=C0402, dnp=True,
           fields=F(None, "-",
                    "THE nRF52832'S INTERNAL DC/DC IS LEFT OFF ON THIS "
                    "BOARD. It needs an inductor on DCC and saves current "
                    "only above about 1 mA average; a Find My tag is asleep "
                    "almost always, where the LDO mode is equal or better "
                    "and one fewer part can go wrong. Whether Apple enables "
                    "theirs is CANNOT DETERMINE. This pad exists so a "
                    "revision can try it without a re-spin."))
    s.nc("C14.1", "C14.2")

    # =====================================================================
    # CLOCKS - real, orderable crystals with real load capacitors
    # =====================================================================
    s.part("X1", "Device:Crystal", value="32MHz 10ppm CL=8pF", group="clock",
           footprint="Crystal:Crystal_SMD_2012-2Pin_2.0x1.2mm",
           fields=F("X1", "NX2012SA-32M-STD-CSW-5",
                    "Apple's crystal is marked T320 / RBEV and its "
                    "manufacturer, part number, load capacitance and case "
                    "size are all CANNOT DETERMINE. This is a real 32 MHz "
                    "part in a real case. The nRF52832 requires 40 ppm or "
                    "better for BLE; 10 ppm is CHOSEN for margin."))
    s.part("X2", "Device:Crystal", value="32.768kHz 20ppm CL=12.5pF",
           group="clock", footprint="Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm",
           fields=F("X2", "ABS07-32.768KHZ-T",
                    "Apple's is marked A048L and is otherwise CANNOT "
                    "DETERMINE. A 32.768 kHz LFXO is what lets the tag sleep "
                    "accurately between advertisements."))

    for nm, pad, xt in (("XC1", "34", "X1"), ("XC2", "35", "X1"),
                        ("XL1", "2", "X2"), ("XL2", "3", "X2")):
        N(nm, "U1 pin " + pad, xt + " and its load capacitor",
          "The oscillator pins the part defines. Nothing chosen here except "
          "the load capacitor values.")
    s.net("XC1", "U1.34", "X1.1")
    s.net("XC2", "U1.35", "X1.2")
    s.net("XL1", "U1.2", "X2.1")
    s.net("XL2", "U1.3", "X2.2")

    # Same defect, same cause: CL05C080CB5NNNC is an 8 pF part and it was
    # pasted onto the 22 pF lines too.
    for ref, net, val, note, mpn in (
            ("C15", "XC1", "8pF 50V C0G", "HFXO load, for CL=8pF",
             "CL05C080CB5NNNC"),
            ("C16", "XC2", "8pF 50V C0G", "HFXO load, for CL=8pF",
             "CL05C080CB5NNNC"),
            ("C17", "XL1", "22pF 50V C0G", "LFXO load, for CL=12.5pF",
             "CL05C220JB5NNNC"),
            ("C18", "XL2", "22pF 50V C0G", "LFXO load, for CL=12.5pF",
             "CL05C220JB5NNNC")):
        s.part(ref, "Device:C", value=val, group="clock", footprint=C0402,
               fields=F("R/C/L bulk", mpn,
                        note + ". CHOSEN to match the crystal CHOSEN above, "
                        "using the ordinary 2*(CL - Cstray) rule with "
                        "Cstray taken as ~4 pF. STRAY CAPACITANCE ON A BOARD "
                        "NOBODY HAS BUILT IS AN ESTIMATE: if the frequency "
                        "is off, these are the two parts to trim."))
        s.net(net, ref + ".1")
        s.net("GND", ref + ".2")

    # =====================================================================
    # FLASH - wide-range, so it works at both ends of the cell's life
    # =====================================================================
    s.part("U3", "Memory_Flash:MX25R3235FM1xx0",
           value="MX25R3235F 32Mb 1.65-3.6V", group="memory",
           footprint="Package_SO:JEITA_SOIC-8_3.9x4.9mm_P1.27mm",
           fields=F("U3", "MX25R3235FM1IL0",
                    "Apple's flash is a GD25LQ32C, which O'Flynn read out of "
                    "the LIVE CHIP over SPI - and it is a 1.65-2.0 V part "
                    "that CANNOT run on this board's 3 V rail. The MX25R is "
                    "the same 32 Mbit density, runs 1.65-3.6 V so it works "
                    "at both ends of the cell's discharge AND behind D1's "
                    "forward drop, and is the lowest-power SPI NOR in "
                    "KiCad's library. THIS SUBSTITUTION IS FORCED BY "
                    "DELETING THE 1.8 V RAIL, and is the clearest example on "
                    "this sheet of one departure making another necessary."))
    s.net("VFLASH", "U3.8", "U3.3", "U3.7")
    s.net("GND", "U3.4")

    N("SPI_SCK", "U1.20 (P0.17)", "U3 SCLK",
      "The GPIO is Apple's, MEASURED by O'Flynn on their board and kept here "
      "so firmware written against one works on the other. On THIS board it "
      "is a choice that happens to match; nothing here measures anything.")
    N("SPI_MOSI", "U1.19 (P0.16)", "U3 SI/SIO0", "As SPI_SCK.")
    N("SPI_MISO", "U3 SO/SIO1", "U1.18 (P0.15)", "As SPI_SCK.")
    s.net("SPI_SCK", "U1.20", "U3.6")
    s.net("SPI_MOSI", "U1.19", "U3.5")
    s.net("SPI_MISO", "U1.18", "U3.2")
    N("FLASH_nCS", "U1.14 (P0.11)", "U3 nCS", "As SPI_SCK.")
    s.net("FLASH_nCS", "U1.14", "U3.1")

    # =====================================================================
    # ACCELEROMETER - a real part, because Apple's is CANNOT DETERMINE
    # =====================================================================
    s.part("U4", "Sensor_Motion:SC7A20", value="SC7A20 3-axis, LGA-12",
           group="sensor", footprint="Package_LGA:LGA-12_2x2mm_P0.5mm",
           fields=F("U4", "SC7A20",
                    "Apple's accelerometer is CANNOT DETERMINE - two "
                    "visually identical metal-lid parts and no readable "
                    "marking. 'BMA280' is a teardown assertion this project "
                    "failed to corroborate, so there is nothing to copy and "
                    "this is a free choice. The SC7A20 is LGA-12 2x2, "
                    "1.8-3.6 V, I2C or SPI, and JLCPCB stocks it as a basic "
                    "part - which is why it is here rather than a BMA280."))
    s.net("VBAT", "U4.3", "U4.7")
    s.net("GND", "U4.8", "U4.9", "U4.1")
    s.nc("U4.4", "U4.11", "U4.6")

    N("ACC_SCL", "U1.8 (P0.06)", "U4 SCx; R3 pull-up",
      "I2C CHOSEN over SPI: two pins instead of four, and the sensor can "
      "answer while the flash is deselected.")
    N("ACC_SDA", "U1.9 (P0.07) and U4 SDx", "both; R4 pull-up", "As ACC_SCL.")
    N("ACC_INT1", "U4 INT1", "U1.10 (P0.08)",
      "Motion wake. DULT anti-stalking needs it, so the line is a "
      "requirement; the pin is a choice.")
    s.net("ACC_SCL", "U1.8", "U4.12", "R3.1")
    s.net("ACC_SDA", "U1.9", "U4.2", "R4.1")
    s.net("ACC_INT1", "U1.10", "U4.5")
    s.net("VBAT", "U4.10")            # nCS high = I2C mode

    for ref in ("R3", "R4"):
        s.part(ref, "Device:R", value="10k", group="sensor", footprint=R0402,
               fields=F("R/C/L bulk", "RC0402FR-0710KL",
                        "I2C pull-up. 10k is CHOSEN: at 400 kHz on a bus "
                        "this short it is comfortable, and on a coin cell "
                        "the 300 uA a 4.7k pair would draw while a byte is "
                        "clocked is not free."))
        s.net("VBAT", ref + ".2")

    s.part("C19", "Device:C", value="100nF 16V X7R", group="sensor",
           footprint=C0402,
           fields=F("R/C/L bulk", "CL05B104KO5NNNC", "Accelerometer supply "
                    "decoupling."))
    s.net("VBAT", "C19.1")
    s.net("GND", "C19.2")

    # =====================================================================
    # SOUNDER - the amplifier is real; the coil is off-board on purpose
    # =====================================================================
    s.part("U5", "Audio:MAX98357A", value="MAX98357A class-D, TQFN-16",
           group="audio",
           footprint="Package_DFN_QFN:TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm",
           fields=F("U5", "MAX98357AETE+T",
                    "The teardown names a MAX98357A (iFixit wrote "
                    "MAX98357B) and the part is not locatable in any "
                    "photograph here, so it is SILICON CITED at LOW "
                    "confidence. It is on this board because the tag "
                    "demonstrably makes a sound. The TQFN-16 is the "
                    "orderable package; Apple's is WLCSP."))
    s.net("VBAT", "U5.7", "U5.8")
    s.net("GND", "U5.3", "U5.11", "U5.15", "U5.17")
    s.nc("U5.5", "U5.6", "U5.12", "U5.13")

    s.part("R5", "Device:R", value="100k", group="audio", footprint=R0402,
           fields=F("R/C/L bulk", "RC0402FR-07100KL",
                    "GAIN_SLOT to GND selects 15 dB gain on the MAX98357 "
                    "family. CHOSEN as the family's mid setting; a coil in "
                    "a plastic shell is not a loudspeaker and this is the "
                    "number most likely to need changing after the first "
                    "listen."))
    N("AMP_GAIN", "R5 to GND", "U5 GAIN_SLOT", "Gain strap, value CHOSEN.")
    s.net("AMP_GAIN", "U5.2", "R5.1")
    s.net("GND", "R5.2")

    N("I2S_BCLK", "U1.16 (P0.13)", "U5 BCLK",
      "The amplifier takes I2S; the nRF52832's I2S peripheral routes to any "
      "pin. Pins CHOSEN around the flash bus.")
    N("I2S_LRCLK", "U1.17 (P0.14)", "U5 LRCLK", "As I2S_BCLK.")
    N("I2S_DIN", "U1.22 (P0.19)", "U5 DIN", "As I2S_BCLK.")
    N("AMP_nSD", "U1.23 (P0.20)", "U5 nSD_MODE",
      "Shutdown. A tag that sleeps at microamps does not leave a class-D "
      "amplifier enabled.")
    s.net("I2S_BCLK", "U1.16", "U5.16")
    s.net("I2S_LRCLK", "U1.17", "U5.14")
    s.net("I2S_DIN", "U1.22", "U5.1")
    s.net("AMP_nSD", "U1.23", "U5.4")

    s.part("C20", "Device:C", value="10uF 6.3V X5R", group="audio",
           footprint=C0603,
           fields=F("R/C/L bulk", "CL10A106MQ8NNNC",
                    "Local reservoir at the amplifier. A class-D output "
                    "stage draws its peaks from whatever is nearest."))
    s.net("VBAT", "C20.1")
    s.net("GND", "C20.2")

    s.part("J1", "Connector_Generic:Conn_01x02", value="VOICE COIL / SOUNDER",
           group="audio",
           footprint="Connector_PinHeader_2.54mm:PinHeader_1x02_"
                     "P2.54mm_Vertical",
           fields=F("SPK-COIL", "-",
                    "TWO PADS, NOT A SPEAKER. Apple's sounder is a voice "
                    "coil glued to the housing dome with the SHELL AS THE "
                    "DIAPHRAGM - there is no such catalogue part, and this "
                    "board is not that shell. A 2-pin header takes any coil "
                    "or magnetic transducer so the audio path can be tested "
                    "on a bench before anyone builds an enclosure."))
    N("SPK_P", "U5 OUTP", "J1 pin 1", "Bridge output, one side.")
    N("SPK_N", "U5 OUTN", "J1 pin 2", "Bridge output, other side.")
    s.net("SPK_P", "U5.9", "J1.1")
    s.net("SPK_N", "U5.10", "J1.2")

    # =====================================================================
    # RADIO - a chip antenna, because a printed one needs a board nobody
    # has drawn yet
    # =====================================================================
    s.part("AE1", "Device:Antenna_Chip", value="2450AT18A100 2.4GHz chip",
           group="rf", footprint="RF_Antenna:Johanson_2450AT18x100",
           fields=F("ANT1", "2450AT18A100E",
                    "Apple's 2.4 GHz antenna is an inverted-F PRINTED ON THE "
                    "PLASTIC CARRIER, and its geometry is CANNOT DETERMINE. "
                    "A chip antenna is CHOSEN because it works on a board of "
                    "any outline and needs no carrier: this board is meant "
                    "to be switched on, not to be the right shape. THE MPN "
                    "CARRIES ITS 'E': the catalogue has no part called "
                    "2450AT18A100, and x_lcsc_resolve matched that shorter "
                    "string inside the longer 2450AT18A100E and returned a "
                    "code for a part number this sheet did not name. Both "
                    "ends were wrong and both are fixed - the matcher is "
                    "token-exact, and this line now names what can actually "
                    "be bought."))
    for ref, val, note in (
            ("C21", "1.0pF 50V C0G", "shunt at the SoC side of the pi"),
            ("L1", "3.9nH", "series element of the pi"),
            ("C22", "1.0pF 50V C0G", "shunt at the antenna side")):
        lib = "Device:L" if ref.startswith("L") else "Device:C"
        fp = "Inductor_SMD:L_0402_1005Metric" if ref.startswith("L") else C0402
        s.part(ref, lib, value=val, group="rf", footprint=fp,
               fields=F("R/C/L bulk", "-",
                        note + ". PLACEHOLDER VALUES, and they are the "
                        "likeliest thing on this board to be wrong. A "
                        "matching network is a MEASUREMENT - it is tuned "
                        "against a VNA on the real copper. These three pads "
                        "exist so there is something to tune; fit 0R for L1 "
                        "and leave the shunts off to start."))
    N("ANT_SOC", "U1.30 (ANT)", "C21 shunt, L1 series",
      "The radio pin. Everything after it is a tuning network with untuned "
      "values.")
    N("ANT_FEED", "L1", "C22 shunt, AE1 FEED", "The antenna feed point.")
    s.net("ANT_SOC", "U1.30", "C21.1", "L1.1")
    s.net("GND", "C21.2")
    s.net("ANT_FEED", "L1.2", "C22.1", "AE1.1")
    s.net("GND", "C22.2", "AE1.2")

    # NFC - the SoC's own tag peripheral, into an off-board coil
    s.part("J2", "Connector_Generic:Conn_01x02", value="NFC COIL 13.56MHz",
           group="rf",
           footprint="Connector_PinHeader_2.54mm:PinHeader_1x02_"
                     "P2.54mm_Vertical",
           fields=F("ANT2", "-",
                    "Apple's NFC antenna is WOUND MAGNET WIRE around the "
                    "rim - at least 9 turns, measured, and a lower bound. "
                    "That is not a part anybody sells and it needs the "
                    "AirTag's geometry. Two pads take a wound coil so the "
                    "NFC tag can be read with a phone on the bench."))
    for ref in ("C23", "C24"):
        s.part(ref, "Device:C", value="150pF 50V C0G", group="rf",
               footprint=C0402,
               fields=F("R/C/L bulk", "-",
                        "NFC series tuning. VALUE DEPENDS ENTIRELY ON THE "
                        "COIL, which is off-board and not yet wound. 150 pF "
                        "suits roughly 1 uH at 13.56 MHz and is a starting "
                        "point, not a design. halo_rev_a's first NFC value "
                        "was EIGHT TIMES WRONG for exactly this reason."))
    N("NFC1", "U1.11 (NFC1/P0.09)", "C23",
      "The NFC-A tag peripheral is the SoC's own. THERE IS NO NFC CHIP - "
      "that is the single best thing this design inherits from Apple's.")
    N("NFC2", "U1.12 (NFC2/P0.10)", "C24", "As NFC1.")
    N("NFC_COIL_A", "C23", "J2 pin 1", "Series tuning into the coil.")
    N("NFC_COIL_B", "C24", "J2 pin 2", "As NFC_COIL_A.")
    s.net("NFC1", "U1.11", "C23.1")
    s.net("NFC2", "U1.12", "C24.1")
    s.net("NFC_COIL_A", "C23.2", "J2.1")
    s.net("NFC_COIL_B", "C24.2", "J2.2")

    # =====================================================================
    # PROGRAMMING - without this the board is a paperweight
    # =====================================================================
    s.part("J3", "Connector_Generic:Conn_01x05", value="SWD (nRST SWDIO "
           "SWCLK GND VBAT)", group="test",
           footprint="Connector_PinHeader_2.54mm:PinHeader_1x05_"
                     "P2.54mm_Vertical",
           fields=F(None, "-",
                    "THE ONE THING THIS BOARD ADDS THAT APPLE'S DOES NOT "
                    "HAVE, and without it the board cannot be programmed and "
                    "'try it out if it works' is impossible. Apple exposes "
                    "SWD on bare test pads and locks it with APPROTECT; this "
                    "is a header, unlocked, because it is ours."))
    N("nRESET", "U1.24 (P0.21/nRESET)", "J3 pin 1", "SWD reset.")
    N("SWDIO", "U1.26", "J3 pin 2", "SWD data.")
    N("SWDCLK", "U1.25", "J3 pin 3", "SWD clock.")
    s.net("nRESET", "U1.24", "J3.1")
    s.net("SWDIO", "U1.26", "J3.2")
    s.net("SWDCLK", "U1.25", "J3.3")
    s.net("GND", "J3.4")
    s.net("VBAT", "J3.5")

    s.part("R6", "Device:R", value="10k", group="test", footprint=R0402,
           fields=F("R/C/L bulk", "RC0402FR-0710KL",
                    "Pull-up on nRESET so the pin does not float. The "
                    "nRF52832 has an internal one, and an external one costs "
                    "a fraction of a microamp and removes a class of "
                    "bring-up mystery."))
    s.net("nRESET", "R6.1")
    s.net("VBAT", "R6.2")

    s.part("C25", "Device:C", value="100nF 16V X7R", group="test",
           footprint=C0402,
           fields=F("R/C/L bulk", "CL05B104KO5NNNC",
                    "nRESET debounce, and it makes a scope probe on the pin "
                    "meaningful."))
    s.net("nRESET", "C25.1")
    s.net("GND", "C25.2")

    N("GND", "BT1 -, and every ground pin", "everything",
      "The return. On a two-terminal holder there is one.")

    s.power("VBAT_RAW", "VBAT", "VFLASH", "GND")

    for name in NETS:
        d = NETS[name]
        s.basis(name, CHOSEN, note=d[2])

    s.text("halo Replica FAB VARIANT. THIS IS NOT THE REPLICA AND NOTHING ON "
           "IT MAY BE CITED AS A FINDING ABOUT THE AIRTAG. The fidelity "
           "record is schematic.py and NETS.md beside this file, where 13 of "
           "52 nets are MEASURED. HERE EVERY NET AND EVERY VALUE IS CHOSEN. "
           "This board exists to be ordered and switched on.")
    s.text("ONE RAIL. The reconstruction has cell -> diode -> buck -> 1.8 V "
           "-> load switch -> 1.8 V flash. This board DELETES the buck and "
           "the 1.8 V rail and runs everything from the cell, because the "
           "nRF52832 is 1.7-3.6 V and spans the whole CR2032 curve. It was "
           "forced - KiCad has no coin-cell 1.8 V buck symbol, and a real "
           "land pattern under an invented pinout is the J1 defect again - "
           "and it is also less to go wrong on a first article.")
    s.text("THE FLASH CHANGED BECAUSE THE RAIL DID. Apple's GD25LQ32C is a "
           "1.65-2.0 V part and cannot run at 3 V. The MX25R3235F is the "
           "same 32 Mbit at 1.65-3.6 V, so it works at both ends of the "
           "cell's life AND behind D1's forward drop. One departure making "
           "another necessary, which is why they are listed together.")
    s.text("WHAT IS NOT HERE: U2 Apple's UWB SiP (never sold to anyone, and "
           "a DNP part with a land pattern invites somebody to try to buy "
           "one), with ANT3 and the coaxial port; the op-amp (its ROLE is "
           "this project's reconstruction, not an observation); the part "
           "marked 1A8/1950 (unidentified down to its function). None of "
           "them can be bought, placed, or justified on a board.")
    s.text("THIS BOARD IS NOT THE SIZE OF AN AIRTAG, AND THAT IS A FORK "
           "RATHER THAN A COMPROMISE. Dimensional fidelity and buildability "
           "are in DIRECT CONFLICT here: Apple's WLCSP-50 fits the ~6 mm "
           "annular ring and CANNOT BE LANDED, because no complete ball map "
           "for it has ever been published. The QFN-48 is the same die, CAN "
           "be landed, and is 6x6 mm - which does not fit that ring. There "
           "is no arrangement that is both. THIS IS THE BUILDABLE BRANCH; "
           "the dimensional branch is the metrology record in pcb/, where "
           "the 0.30 mm board and the wafer-scale packages live. A person "
           "holding a board that works but is the wrong shape should not "
           "have to work out why.")
    s.text("THE FIVE-REMOVALS RESET IS NOT REPRODUCED. Apple has THREE "
           "sprung contacts with BOTH positives sensed. A catalogue CR2032 "
           "holder has two terminals, so this board senses one positive. A "
           "real loss of function, stated rather than quietly dropped.")
    s.text("THE MATCHING NETWORK C21/L1/C22 AND THE NFC CAPS C23/C24 ARE "
           "PLACEHOLDERS, and they are the likeliest things here to be "
           "wrong. A match is a MEASUREMENT taken against a VNA on the real "
           "copper. Start with L1 = 0R and the shunts unfitted. The NFC "
           "values depend on a coil that is not wound yet - halo_rev_a's "
           "first NFC value was EIGHT TIMES WRONG for exactly this reason.")
    s.text("J3 IS SWD AND IT IS THE REASON THIS BOARD CAN BE TRIED AT ALL. "
           "Apple's SWD is on bare pads behind APPROTECT. Ours is a header, "
           "unlocked. J1 and J2 are pads for an off-board sounder coil and "
           "NFC coil; neither is a part anybody sells.")

    s.unused_gpio = s.nc_unused()
    return s


DEPARTURES = [
    "THE BUCK AND THE 1.8 V RAIL ARE DELETED (U6, L1). Forced: KiCad ships "
    "no symbol for a coin-cell 1.8 V buck, and a real land pattern under the "
    "fidelity sheet's invented 5-pin symbol is the J1 defect repeated. Also "
    "better: the nRF52832 spans the whole cell curve, and a buck is the "
    "highest-risk block on a board whose purpose is to find out if it works.",
    "THE FLASH CHANGED FROM GD25LQ32C TO MX25R3235F. Consequence of the "
    "above, not a preference: Apple's part is 1.65-2.0 V and cannot run at "
    "3 V. The MX25R is 1.65-3.6 V and works behind D1's drop at end of life.",
    "U2, APPLE'S UWB SiP, IS ABSENT ENTIRELY - with ANT3 and the coaxial "
    "port. Never sold to anyone, pinout unpublished. UWB Precision Finding "
    "is a GAP on this board and on every board anyone outside Apple builds.",
    "U7, THE OP-AMP, IS ABSENT. Its role on the fidelity sheet is that "
    "sheet's own reconstruction and could equally be a buffer, a "
    "current-sense amp or a filter.",
    "U9 IS ABSENT. CANNOT DETERMINE down to its function; unbuyable.",
    "THE SECOND POSITIVE BATTERY CONTACT IS ABSENT, so the five-removals "
    "factory-reset ritual is NOT reproduced. A catalogue holder has two "
    "terminals.",
    "THE ACCELEROMETER IS AN SC7A20, not a BMA280. Apple's is CANNOT "
    "DETERMINE, so there was nothing to copy; the SC7A20 is a JLCPCB basic "
    "part, which is the whole argument.",
    "THE 2.4 GHz ANTENNA IS A CHIP ANTENNA, not Apple's printed inverted-F. "
    "Apple's geometry is CANNOT DETERMINE and lives on a plastic carrier "
    "this board does not have.",
    "THE SOUNDER COIL AND THE NFC COIL ARE OFF-BOARD, on 2-pin headers. "
    "Neither is a catalogue part and both need the AirTag's geometry.",
    "SWD IS A HEADER (J3) AND IS NOT LOCKED. Apple's is bare pads behind "
    "APPROTECT. Without it this board cannot be programmed.",
    "THE PACKAGE IS QFN-48, NOT WLCSP-50, so THIS BOARD IS NOT THE SIZE OF "
    "AN AIRTAG. The die is the same; the outline is not, and no outline here "
    "should be compared with the metrology lane's numbers.",
    "EVERY PASSIVE VALUE IS CHOSEN FROM FUNCTION. Not one is a measurement "
    "of Apple's board, which is why basis() marks all of them CHOSEN.",
]

NOT_VERIFIED = [
    "NOBODY HAS BUILT ONE. Every line below and every claim on the sheet is "
    "a paper claim. This is first in the list rather than last because it is "
    "the one that matters most, and a reader who stops after one line should "
    "stop after this one.",
    "No LCSC order code on any line. This lane did not pull a price ladder "
    "and a code with no pull date is a rumour. Every part carries a real MPN "
    "and the fab lane sources against it.",
    "The matching network C21/L1/C22 has never seen a VNA. Fit L1 = 0R and "
    "leave C21/C22 unfitted for the first article.",
    "The NFC tuning C23/C24 assumes roughly 1 uH for a coil that is not "
    "wound yet.",
    "The crystal load capacitors assume ~4 pF of stray on a board nobody has "
    "laid out. If the frequency is off, trim C15/C16 first.",
    "No thermal, no current budget and no sleep-current estimate has been "
    "computed for this board by this lane.",
]


if __name__ == "__main__":
    s = build()
    for sev, msg in s.check():
        print("%-17s %s" % (sev, msg))
    print("\n--- deliberately not connected (%d pins) ---" % len(s.unused_gpio))
    for key, name in s.unused_gpio:
        print("  %-10s %s" % (key, name))
    s.place()
    print("\n" + s.describe())
    print(s.describe_bases())
    out = s.save(os.path.join(REPLICA, "out", "schematic-fab",
                              s.name + ".kicad_sch"))
    print("\nwrote", out)
    print("\n--- DEPARTURES from the fidelity record ---")
    for line in DEPARTURES:
        print("  " + line)
    print("\n--- NOT VERIFIED, and nobody should assume otherwise ---")
    for line in NOT_VERIFIED:
        print("  " + line)
