"""halo REPLICA — Apple AirTag A2187, reconstructed as a schematic.

    cd ~/dev/ce-workshop
    ce-pcb/bin/sch all ce-designs/halo/electronics/halo_replica/schematic/schematic.py \
                   -o ce-designs/halo/electronics/halo_replica/out/schematic

LANE L11 owns this file. It is NOT `electronics/halo_rev_a/schematic.py`,
which is the board halo SHIPS; this one is the board Apple shipped, drawn as
faithfully as the evidence in this repository permits and NO MORE.

===========================================================================
THE ONE SENTENCE A READER MUST NOT MISS
===========================================================================
**NOBODY IN THIS PROJECT HAS TRACED APPLE'S COPPER.** Not one net on this
sheet was read off a board. Every connection here is RECONSTRUCTED FROM
FUNCTION — from what each identified part is for, and from what its datasheet
family requires — and the parts themselves come from `bom/bom.json`, which is
photographs and markings, not continuity.

So every net carries a `basis` and this sheet prints them all:

    MEASURED   read off the hardware by a named source, in this repository
    INFERRED   required by the part's own datasheet family once the part is
               accepted (a crystal goes on the crystal pins; a flash's VCC
               goes to a rail). Wrong only if the part identification is wrong
    CHOSEN     this sheet picked it. Apple's actual assignment is unknown and
               a different GPIO would be equally consistent with every
               photograph. Never cite one of these as a finding about Apple

`NETS.md` beside this file lists every net, its basis, what drives it and what
it feeds. `schematic.py --nets` regenerates it, so the two cannot drift.

===========================================================================
FOUR THINGS THAT ARE ON THIS SHEET AS THEY ARE, NOT TIDIED
===========================================================================
1. **U2 — Apple's "U1" UWB SiP — IS PLACED AND IS DNP/UNPOPULATED.**
   Apple does not sell it. To anyone. It is not a sourcing problem, it is a
   does-not-exist-for-us problem, and a replica that quietly omits it is
   claiming a device it cannot build. It is drawn, marked DNP, and the
   refusal is written on the sheet itself in `s.text()`, not only here.
   Its symbol is a PLACEHOLDER with this sheet's own pin numbering: **no
   pinout for the Apple U1 SiP has ever been published**, so those numbers
   are not a land pattern and nobody may fabricate from them.

   NAME COLLISION, and it has bitten people: `bom/bom.json` follows
   REFERENCE-TEARDOWN and calls the **Nordic MCU U1**. The part the press
   calls "the U1" is **U2** here. Never write bare "U1" about the UWB part.

2. **U4's exact part is CANNOT DETERMINE.** `bom.json` U4: two visually
   identical metal-lid parts, no readable marking at any magnification
   available, and "BMA280" is a teardown assertion this project tried to
   corroborate by size and could not. It is drawn with a GENERIC 3-axis
   accelerometer symbol and its value field carries the ambiguity.

3. **U9 is CANNOT DETERMINE.** Marking `1A8 / 1950`, a part number nobody has
   published, and its *function* — "secondary regulator" — is itself an
   inference. Generic symbol, ambiguity in the value field, and its output
   goes to NOTHING on this sheet because nothing in the record says what it
   feeds. `check()` reports that net as CANNOT DETERMINE and that report is
   the correct answer, not a defect to silence.

4. **D3 — the series diode DECISIONS.md D24 requires.** Nordic's own nRF52832
   product specification §42.10, verbatim: *"If the antenna is exposed to a
   strong NFC field, current may flow in the opposite direction on the supply
   due to parasitic diodes and ESD structures. If the battery used does not
   tolerate return current, a series diode must be placed between the battery
   and the device in order to protect the battery."* A CR2032 does not
   tolerate return current, and a phone held against the tag is a strong field
   BY DESIGN. D3 sits between the positive power finger and everything else.
   **It costs a forward drop the power budget has not accounted for** — a few
   hundred mV for a Schottky against a cell whose end-of-life headroom the
   coin-cell model already tracks to 68 mV of droop, or millivolts for an
   ideal-diode controller that costs more money. D24 says the board lane
   prices both. THE COST IS ON THE SHEET (`s.text`), not hidden in a note.

   D3 IS AN ADDITION, NOT AN OBSERVATION. No photograph in this repository
   shows a series diode in Apple's power path. Apple may have solved this
   another way, or accepted it. `basis=CHOSEN`.

===========================================================================
THE POWER PATH, AND WHERE IT DEPARTS FROM iFIXIT
===========================================================================
REFERENCE-TEARDOWN §2.1 says U8 (FPF2487-class load switch) "gates U1 +
flash", where U1 is the Nordic MCU. **This sheet does not draw that, and the
reason is an engineering one that does not need a photograph:**

    A load switch that gates its own controller cannot be turned on. If the
    MCU's rail comes through U8, and U8's enable comes from the MCU, the
    board never boots. Something else would have to hold that enable — and
    the record names nothing that could.

So: the buck U6 makes 1.8 V; the MCU U1 sits on it directly; U8 gates the
flash U3 and the UWB module U2 from a GPIO, which is exactly the arrangement
that buys the 2.3 µA sleep the teardown reports. iFixit's line is single-
source, `bom.json` grades U8 **LOW / SILICON CITED** ("not corroborated by
Catley, O'Flynn or any photograph here"), and this is what was discarded and
why. Both readings are recorded in `DISCARDED` at the bottom of this file.

===========================================================================
THE PACKAGES ARE NOT THE REAL PACKAGES, AND THAT IS DELIBERATE
===========================================================================
Apple's U1 is an **nRF52832-CIAA, WLCSP-50**. There is no COMPLETE sourced
ball map for CIAA anywhere in this repository, and inventing 50 ball
designators is exactly the failure DECISIONS.md D9 forbids.

**TEN BALLS ARE SOURCED, AND THIS SHEET FIRST SAID NONE WERE.** O'Flynn's
test-point table names D3, E2, F1, F4, G1, G3, H1, H2, H3 and H4 against real
signals. Ten of fifty is not a ball map and does not become one, so the
substitution below stands — but the claim "no ball map is sourced" was too
strong, it was written before anyone opened the file, and the correction is
recorded here rather than quietly applied. This sheet therefore uses KiCad's
`MCU_Nordic:nRF52832-QFxx` — **the same die in the QFN-48 package** — so:

    * the netlist is correct BY SIGNAL NAME, which is what a netlist is for;
    * the pin NUMBERS are QFAA's, not CIAA's, and any board built from them
      is a QFN board, not a replica of Apple's WLCSP land pattern.

Every part carries an `FP-basis` field saying where its footprint came from:
MEASURED, SUBSTITUTION, or PLACEHOLDER-L12. L12 owns the land patterns; this
lane owns the connectivity, and marking the seam is how the two stay honest.

===========================================================================
WHAT IS ON THE REAL BOARD AND IS *NOT* ON THIS SHEET
===========================================================================
Placing a part means asserting what it is. These are in `bom.json`, they were
SEEN, and this sheet refuses to guess them into a circuit:

    D1, D2  marking `K11`, a matched pair. bom.json: "CANNOT DETERMINE for
            the part AND the function". Drawing them as Schottkys would put
            RESEARCH-A's word in a netlist as if it were a measurement.
    CT1     marking `6X A75`, blue body. bom.json: "CANNOT DETERMINE ...
            and whether it is a capacitor at all — 'blue body' is a colour,
            not a technology."
    UNK-A   large matte-black rectangle, no marking of any kind.
    UNK-B   pale ceramic square between U2 and J1. Position is consistent
            with an RF switch/filter/balun and POSITION IS NOT EVIDENCE OF
            FUNCTION. If it is a switch, then J1 and ANT3 are NOT the same
            net and this sheet's UWB_RF is wrong in a way it cannot detect.

Four parts absent is not four parts missed. It is four parts the record does
not identify, and `DISCARDED` says so on the sheet.
"""
import json
import os
import sys

WORKSHOP = "/Users/leifrydenfalk/dev/ce-workshop"
if WORKSHOP not in sys.path:
    sys.path.insert(0, os.path.join(WORKSHOP, "ce-pcb"))

from cepcb.schematic import Schematic                              # noqa: E402
from cepcb.schematic import MEASURED, INFERRED, CHOSEN            # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
BOM_JSON = os.path.join(REPLICA, "bom", "bom.json")

# Land patterns, each verified present with cepcb.find() on 2026-09-05.
C0201 = "Capacitor_SMD:C_0201_0603Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
R0402 = "Resistor_SMD:R_0402_1005Metric"
L0402 = "Inductor_SMD:L_0402_1005Metric"

#: The three bases are ce-pcb's now, not this file's. They were declared here
#: first; `Schematic.basis()` was added upstream on 2026-09-05 (P11) so that a
#: MEASURED net has to name a file and a claim about it, and `check()` opens
#: the file and compares. This design is that feature's first user.
#: net name -> (basis, driver, loads, why). Written by N() as the sheet is
#: built, so NETS.md is generated from the same statements that make the
#: netlist and cannot describe a different circuit.
NETS = {}

#: net -> the anchor handed to basis(). Kept beside NETS so the NETS.md table
#: keeps its four columns.
ANCHORS = {}

#: ce-designs/halo — anchors resolve against it.
REPO = os.path.dirname(os.path.dirname(REPLICA))

#: THE TWO DOCUMENTS EVERY MEASURED NET ON THIS SHEET RESTS ON, and nothing
#: else does. Every string claimed against them is checked at build time by
#: cepcb's basis resolver, so deleting the evidence breaks the build.
A_OFLYNN = "research/fetched/A-oflynn-testpoints-and-glitch-repos.md"
A_TEARDOWN = "docs/REFERENCE-TEARDOWN.md"


def N(name, basis, driver, loads, why, anchor=None, contains=None,
      derived_from=None):
    """Record what a net IS, next to where it is wired.

    A net table maintained by hand in a second document is a net table that
    is wrong within a week. This one is the same call that documents it.

    `anchor` + `contains` go to `cepcb.schematic.Schematic.basis()`, which
    OPENS THE FILE and checks the claim. A MEASURED net with no anchor is
    refused THERE, not here — a local wrapper that let MEASURED be reached by
    typing would be the ratchet with a nicer face.
    """
    if basis not in (MEASURED, INFERRED, CHOSEN):
        raise SystemExit("net %s: basis %r is not one of the three." %
                         (name, basis))
    if name in NETS:
        raise SystemExit(
            "net %s is described twice. One net, one basis, or the table "
            "means nothing." % name)
    NETS[name] = (basis, driver, loads, why)
    ANCHORS[name] = {"anchor": anchor, "contains": contains,
                     "derived_from": derived_from}
    return name


def bom_lines():
    """Every part on this sheet must name a line in bom/bom.json.

    Loaded, not remembered: if the BOM lane renames a designator this build
    fails rather than quietly drawing a part that no longer has a record.
    """
    if not os.path.exists(BOM_JSON):
        raise SystemExit(
            "CANNOT DETERMINE: %s is missing, so no part on this sheet can "
            "carry the BOM line it rests on." % BOM_JSON)
    with open(BOM_JSON, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    return {ln["ref"]: ln for ln in doc["lines"]}


BOM = bom_lines()


def B(bom_ref, fp_basis, note="", extra=None):
    """The fields every part carries: its BOM line, and where its land
    pattern came from.

    `bom_ref` is checked against bom.json NOW. A schematic and a BOM that
    drift apart are two documents describing two different products, and the
    cheapest place to stop that is the moment the part is placed.
    """
    if bom_ref is not None and bom_ref not in BOM:
        raise SystemExit(
            "CANNOT DETERMINE: this sheet places a part citing bom.json line "
            "%r, and bom.json has no such line. Lines it does have: %s"
            % (bom_ref, ", ".join(sorted(BOM))))
    if fp_basis not in ("MEASURED", "SUBSTITUTION", "PLACEHOLDER-L12", "n/a"):
        raise SystemExit("%s: FP-basis %r is not one of the four." %
                         (bom_ref, fp_basis))
    f = {"BOM line": bom_ref if bom_ref else "NOT IN bom.json - see Note",
         "FP-basis": fp_basis}
    if bom_ref:
        ln = BOM[bom_ref]
        f["BOM part"] = ln["part"]
        f["BOM confidence"] = ln["confidence"][:180]
        f["Evidence class"] = ln["evidence_class"]
    if note:
        f["Note"] = note
    if extra:
        f.update(extra)
    return f


def build():
    s = Schematic(
        "halo_replica",
        title="halo REPLICA - Apple AirTag A2187, reconstructed",
        rev="R1", company="ce-designs/halo - halo Replica lane L11",
        comments=[
            "NO COPPER WAS TRACED. Every net is INFERRED or CHOSEN "
            "unless marked MEASURED - see NETS.md.",
            "Parts from electronics/halo_replica/bom/bom.json (27 lines).",
            "U2 (Apple U1 UWB SiP) is DNP/UNPOPULATED - never sold to anyone.",
            "U4 and U9 are CANNOT DETERMINE: generic symbols, ambiguity in "
            "the value field.",
            "D3 is an ADDITION per DECISIONS.md D24 (NFC field back-drives "
            "the cell); no photograph shows one in Apple's board.",
        ])

    # =====================================================================
    # SYMBOLS THIS SHEET HAS TO MAKE, because the part is not in a library
    # or because the honest drawing of it is a box with a warning in it.
    # =====================================================================
    uwb_id = s.define(
        name="APPLE_U1_SIP_PLACEHOLDER",
        pins=[("1", "VDD", "power_in", "left"),
              ("2", "GND", "power_in", "left"),
              ("3", "SPI_SCK", "input", "left"),
              ("4", "SPI_MOSI", "input", "left"),
              ("5", "SPI_MISO", "output", "right"),
              ("6", "SPI_nCS", "input", "left"),
              ("7", "IRQ", "output", "right"),
              ("8", "nRESET", "input", "left"),
              ("9", "RF", "passive", "right")],
        description="PLACEHOLDER ONLY. Apple U1 UWB SiP (die TMKA75, USI "
                    "system-in-package). NEVER SOLD TO ANYONE, so this part "
                    "is DNP/UNPOPULATED on this sheet. NO PINOUT FOR THIS "
                    "MODULE HAS EVER BEEN PUBLISHED: these pin NUMBERS are "
                    "this sheet's own and are NOT a land pattern. The pin "
                    "NAMES are inferred from the nRF loading the U1's 'Rose' "
                    "firmware out of the shared SPI flash and driving it over "
                    "the 'Durian' opcode set.",
        keywords="uwb apple u1 sip dnp placeholder",
        cite="bom/bom.json U2; docs/REFERENCE-TEARDOWN.md 2.1; "
             "research/fetched/A-seemoo-airtag-firmware-and-opcodes.md. "
             "PIN NUMBERING IS UNSOURCED AND DELIBERATELY SO.")

    acc_id = s.define(
        name="ACCEL_3AXIS_GENERIC",
        pins=[("1", "VDD", "power_in", "left"),
              ("2", "VDDIO", "power_in", "left"),
              ("3", "GND", "power_in", "left"),
              ("4", "SCL/SPC", "input", "left"),
              ("5", "SDA/SDI", "bidirectional", "left"),
              ("6", "SDO/SA0", "bidirectional", "right"),
              ("7", "nCS", "input", "left"),
              ("8", "INT1", "output", "right"),
              ("9", "INT2", "output", "right")],
        description="GENERIC 3-axis accelerometer. The part is CANNOT "
                    "DETERMINE: bom.json U4 sees a metal-lid LGA and cannot "
                    "read a marking at any magnification available, and "
                    "'BMA280' is a teardown assertion this project failed to "
                    "corroborate by size. This pin set is the intersection "
                    "the BMA280, LIS2DH, LIS2DW12 and SC7A20 all share; the "
                    "NUMBERING IS THIS SHEET'S OWN and is not a land pattern.",
        keywords="accelerometer 3-axis generic cannot-determine",
        cite="bom/bom.json U4 (confidence: CANNOT DETERMINE which part is "
             "the accelerometer; LOW for BMA280).")

    buck_id = s.define(
        name="BUCK_TPS62746_CLASS",
        pins=[("1", "VIN", "power_in", "left"),
              ("2", "EN", "input", "left"),
              ("3", "GND", "power_in", "left"),
              ("4", "SW", "output", "right"),
              ("5", "VOUT/FB", "power_out", "right")],
        description="Step-down converter, 3 V cell to a 1.8 V rail. The "
                    "FAMILY is evidence (Apple's own board legend reads "
                    "'98C0051 / TPS746'); the specific part is not, and the "
                    "package is CANNOT DETERMINE. Pin numbering is this "
                    "sheet's own.",
        keywords="buck dcdc 1v8 tps62746",
        cite="bom/bom.json U6 (MEDIUM for 'a TPS746-family buck is on this "
             "board' - a board legend authored by Apple's layout engineer; "
             "LOW that the metal-lid part beside it is that buck).")

    lsw_id = s.define(
        name="LOADSWITCH_FPF2487_CLASS",
        pins=[("1", "VIN", "power_in", "left"),
              ("2", "EN", "input", "left"),
              ("3", "GND", "power_in", "left"),
              ("4", "VOUT", "power_out", "right")],
        description="Load switch / OVP. Power-gating is WHY the sleep current "
                    "is 2.3 uA. bom.json U8 is LOW confidence and single-"
                    "source (iFixit), uncorroborated by Catley, O'Flynn or "
                    "any photograph here. Pin numbering is this sheet's own.",
        keywords="load switch ovp gate fpf2487",
        cite="bom/bom.json U8; docs/REFERENCE-TEARDOWN.md 2.1.")

    u9_id = s.define(
        name="UNKNOWN_REGULATOR_1A8_1950",
        pins=[("1", "IN?", "power_in", "left"),
              ("2", "GND?", "power_in", "left"),
              ("3", "OUT?", "power_out", "right")],
        description="CANNOT DETERMINE. A leadless moulded part marked "
                    "'1A8' / '1950' exists at this location and that is ALL "
                    "that is established. Even its function - 'secondary "
                    "regulator' - is an inference, which is why every pin "
                    "name here ends in a question mark. Its output is wired "
                    "to nothing on this sheet because nothing in the record "
                    "says what it feeds.",
        keywords="unknown regulator cannot-determine 1A8 1950",
        cite="bom/bom.json U9 (CANNOT DETERMINE for the part number; HIGH "
             "only for 'a part bearing these two lines exists here').")

    batt_id = s.define(
        name="BATT_CONTACTS_3",
        pins=[("1", "P+_POWER", "passive", "left"),
              ("2", "P+_SENSE", "passive", "left"),
              ("3", "N-_DOME", "passive", "left")],
        description="Three sprung battery contacts: one negative dome on the "
                    "well floor and TWO positive tabs on the wall. Both "
                    "positives must see 3 V to boot; only the left carries "
                    "the logic current, the right is sensed at ~50 nA. This "
                    "is the connector-less battery interface and there is no "
                    "catalogue land pattern for it.",
        keywords="battery contacts cr2032 spring dual-positive",
        cite="bom/bom.json BATT-CONTACTS; docs/REFERENCE-TEARDOWN.md 2.5 "
             "(O'Flynn: the big pads under the terminals are NOT connected; "
             "the real contacts are the small pads under the tabs).")

    # =====================================================================
    # BLOCK 1 - the cell, both positive contacts, and D24's series diode
    # =====================================================================
    s.part("BT1", batt_id, value="3 SPRUNG CONTACTS (1 neg, 2 pos)",
           group="power", footprint="",
           fields=B("BATT-CONTACTS", "PLACEHOLDER-L12",
                    "L12 draws the land pattern. THE CELL IS NOT DRAWN ON "
                    "THIS SHEET AS A PART: in the assembled tag the CR2032's "
                    "top face touches BOTH positive fingers, so P+_POWER and "
                    "P+_SENSE are one node THROUGH THE CELL AND ONLY THROUGH "
                    "THE CELL. Drawing a battery symbol across them would "
                    "short two nets that must be separate in copper - and "
                    "that separation is the whole mechanism by which removal "
                    "is detectable on both.",
                    {"Cell": BOM["BATT"]["part"]}))

    s.part("D3", "Device:D_Schottky", value="SCHOTTKY or IDEAL-DIODE CTRL",
           group="power", footprint="Diode_SMD:D_0402_1005Metric",
           fields=B(None, "PLACEHOLDER-L12",
                    "ADDITION, NOT AN OBSERVATION. Required by DECISIONS.md "
                    "D24 from nRF52832 product specification 42.10: an NFC "
                    "field can push current backwards into the supply through "
                    "parasitic diodes and ESD structures, and a CR2032 does "
                    "not tolerate return current. NO PHOTOGRAPH IN THIS "
                    "REPOSITORY SHOWS A SERIES DIODE IN APPLE'S POWER PATH - "
                    "Apple may have solved this another way or accepted it. "
                    "COST: a Schottky drops a few hundred mV on a cell whose "
                    "end-of-life headroom is already tracked to 68 mV of "
                    "droop; an ideal-diode controller drops millivolts and "
                    "costs money. D24 says price both.",
                    {"Vf": "CANNOT DETERMINE - part not selected"}))

    N("VBAT_RAW", MEASURED, "BT1.1, the positive POWER finger",
      "D3 anode; R1 (sense divider for AIN0)",
      "Three sprung contacts with two positives is a direct observation "
      "(REFERENCE-TEARDOWN 2.5, iFixit had the tag in their hands), and "
      "O'Flynn labels the pads VCC1 and VCC2, '+3.0V input (1 of 2 - both "
      "needed)'. WHICH of the two carries the logic current is NOT settled "
      "by O'Flynn - he says both are needed and nothing about sensing - so "
      "the power/sense split here comes from REFERENCE-TEARDOWN 2.5 and "
      "could be the other way round.",
      anchor=A_TEARDOWN, contains="**3 sprung contacts**")
    s.net("VBAT_RAW", "BT1.1", "D3.1", "R1.1")

    N("VBAT", CHOSEN, "D3 cathode",
      "C1-C5 bulk; U6.VIN (buck); U9.IN; U5.VDD (amplifier)",
      "The rail behind D24's diode. That the bulk sits BEHIND the diode "
      "rather than in front of it is this sheet's choice and it is the "
      "choice that makes the diode work: hold-up capacitance in front of a "
      "blocking diode holds up the cell, not the load.")
    s.net("VBAT", "D3.2")

    N("VBAT_SNS_P2", MEASURED, "BT1.2, the positive SENSE finger",
      "R3 (divider to AIN1)",
      "REFERENCE-TEARDOWN 2.5: 'Both positives must see 3 V to boot; only "
      "the left powers the logic, the right is sensed at ~50 nA.' A ~50 nA "
      "sense current is a very large divider, which is why R3/R4 are "
      "megohms and why their exact values are CANNOT DETERMINE.",
      anchor=A_TEARDOWN, contains="~50 nA")
    s.net("VBAT_SNS_P2", "BT1.2", "R3.1")

    N("GND", MEASURED, "BT1.3, the negative dome on the well floor",
      "every ground pin on this sheet",
      "The negative contact is a direct observation. O'Flynn labels the pad "
      "GND and test point 7 lands on it.",
      anchor=A_TEARDOWN, contains="negative on the well floor")
    # BT1.3 WAS MISSING HERE ON THE FIRST BUILD, and nc_unused() caught it:
    # the ground return of the entire tag had been DESCRIBED in the net table
    # above and never WIRED, so the sheet would have shipped with the battery
    # dome silently marked no-connect. That is precisely the failure
    # nc_unused()'s docstring warns about - "an ERC that passes because 34
    # pins were quietly no-connected is not an ERC that passed" - and it is
    # why this file prints that list instead of discarding it.
    s.net("GND", "BT1.3")

    # The five bulk capacitors. This is the five-removals reset ritual, as a
    # circuit: pull the cell and the tag has to stay alive long enough to
    # count the removal, which is what this capacitance is FOR.
    for ref in ("C1", "C2", "C3", "C4", "C5"):
        s.part(ref, "Device:C", value="100uF? mark J107S - CANNOT DETERMINE", group="power", footprint=C0805,
               fields=B("C1..C5", "PLACEHOLDER-L12",
                        "Five of them, counted around the rim on the "
                        "battery-contact face. bom.json: HIGH for the "
                        "marking, the count and the location; MEDIUM for "
                        "'100 uF'; CANNOT DETERMINE for the technology. The "
                        "0805 body here is a PLACEHOLDER - the package size "
                        "is PENDING in bom.json, not measured.",
                        {"Marking": "J107S", "Hold-up time":
                         "CANNOT DETERMINE - no load current measured here"}))
        s.net("VBAT", ref + ".1")
        s.net("GND", ref + ".2")

    # =====================================================================
    # BLOCK 2 - the 1.8 V rail: buck, inductor, and the gated branch
    # =====================================================================
    s.part("U6", buck_id, value="TPS62746-CLASS BUCK 3V->1V8", group="power", footprint="",
           fields=B("U6", "PLACEHOLDER-L12",
                    "The evidence is a BOARD LEGEND, '98C0051 / TPS746', "
                    "silkscreened by Apple's own layout engineer. bom.json "
                    "records the trap it set: that string is legend, NOT a "
                    "package marking, and the metal-lid part beside it was "
                    "not shown to be the buck."))
    s.net("VBAT", "U6.1")
    s.net("GND", "U6.3")

    N("EN_BUCK", CHOSEN, "VBAT through R7", "U6.EN",
      "Nothing in the record says how the buck is enabled. Tied always-on "
      "here because a tag with no rail cannot enable anything.")
    s.part("R7", "Device:R", value="0R (strap)", group="power",
           footprint=R0402,
           fields=B(None, "PLACEHOLDER-L12",
                    "Enable strap. Not a part anyone has seen; it exists so "
                    "the enable is a decision on the sheet rather than a "
                    "wire nobody argued about."))
    s.net("VBAT", "R7.1")
    s.net("EN_BUCK", "R7.2", "U6.2")

    s.part("L1", "Device:L", value="WIREWOUND - CANNOT DETERMINE", group="power", footprint=L0402,
           fields=B("L1x", "PLACEHOLDER-L12",
                    "bom.json L1x: individual turns of copper wire are "
                    "DIRECTLY RESOLVABLE over the core between two "
                    "metallised end caps. That is a construction "
                    "observation, not an inference. Inductance, current "
                    "rating, DCR and manufacturer are all CANNOT DETERMINE, "
                    "and so is the 0402 body drawn here."))
    N("SW_BUCK", INFERRED, "U6.SW", "L1",
      "A buck with an external wirewound inductor switches into it. Which "
      "inductor is the buck's is bom.json's 'almost certainly, given its "
      "position' - position, again, not a trace.")
    s.net("SW_BUCK", "U6.4", "L1.1")

    N("V1V8", INFERRED, "U6.VOUT through L1",
      "U1 (nRF52832) VDD x3; U4 accelerometer; U7 op-amp V+; U8.VIN; C10-C13",
      "1.8 V because the flash Apple fitted is a 1.65-2.0 V part (O'Flynn "
      "read GD25LQ32C off the live chip over SPI with a J-Flash) and the "
      "teardown names the buck 3 V -> 1.8 V. The nRF52832's own range is "
      "1.7-3.6 V, so 1.8 V is legal for it too.")
    s.net("V1V8", "L1.2", "U6.5")

    for ref, note in (("C10", "1V8 bulk at the buck output"),
                      ("C11", "at U1 VDD pin 13"),
                      ("C12", "at U1 VDD pin 36"),
                      ("C13", "at U1 VDD pin 48")):
        s.part(ref, "Device:C", value="DECOUPLING - CANNOT DETERMINE",
               group="power", footprint=C0402,
               fields=B("R/C/L bulk", "PLACEHOLDER-L12",
                        note + ". bom.json is explicit that this is not a "
                        "gap any photograph can close: a 100 nF and a 1 uF "
                        "0402 are visually identical. The VALUE is left "
                        "missing rather than filled with a plausible one."))
        s.net("V1V8", ref + ".1")
        s.net("GND", ref + ".2")

    s.part("U8", lsw_id, value="FPF2487-CLASS LOAD SWITCH (LOW conf)", group="power", footprint="",
           fields=B("U8", "PLACEHOLDER-L12",
                    "Power-gating is why sleep is 2.3 uA - copy the INTENT "
                    "even if not the part. THIS SHEET DEPARTS FROM iFIXIT'S "
                    "WORDING: iFixit says U8 gates 'U1 + flash', where U1 is "
                    "the MCU. A load switch whose enable comes from the MCU "
                    "it powers cannot ever be turned on. Here it gates the "
                    "FLASH and the UWB module only."))
    s.net("V1V8", "U8.1")
    s.net("GND", "U8.3")

    N("EN_PERIPH", CHOSEN, "U1.15 (P0.12)", "U8.EN",
      "WHICH GPIO is entirely this sheet's choice - Apple's assignment is "
      "unknown and every nRF52832 GPIO could serve. THAT THERE IS A GATE "
      "UNDER FIRMWARE CONTROL IS NO LONGER AN ARGUMENT BUT A MEASUREMENT: "
      "see V1V8_SW. It sat on P0.15 until O'Flynn's table showed that pad is "
      "the flash's CIPO.",
      derived_from="this sheet's own pin budget, after the measured flash "
                   "bus took P0.11/P0.15/P0.16/P0.17")
    s.net("EN_PERIPH", "U1.15", "U8.2")

    N("V1V8_SW", MEASURED, "U8.VOUT", "U3 flash VCC/nWP/nHOLD; U2 UWB VDD "
      "(DNP); TP21",
      "O'Flynn, in his own words: 'The nrf controls power to the SPI flash, "
      "so you need to override it by supplying 1.8V on test point 21', and "
      "'most of time the flash is powered off and thus the pins are "
      "tri-stated'. THAT SETTLES THE ARGUMENT THIS SHEET HAD WITH iFIXIT BY "
      "MEASUREMENT rather than by self-consistency: the flash is on a "
      "switched 1.8 V rail the MCU commands. What is still CHOSEN is which "
      "GPIO commands it (EN_PERIPH) and that the switch is an FPF2487.",
      anchor=A_OFLYNN,
      contains="The nrf controls power to the SPI flash")
    s.net("V1V8_SW", "U8.4")

    # U9 - the part nobody has identified, wired the only honest way.
    s.part("U9", u9_id, value="CANNOT DETERMINE - mark 1A8/1950", group="power", footprint="",
           fields=B("U9", "PLACEHOLDER-L12",
                    "bom.json U9: HIGH only for 'a part bearing these two "
                    "lines exists at this location'. Its INPUT is drawn from "
                    "VBAT because a regulator has to come from somewhere and "
                    "VBAT is the only unregulated rail; its OUTPUT goes to "
                    "NOTHING, because the record does not say what it feeds "
                    "and a wire drawn to a plausible load would be this "
                    "sheet inventing a circuit. check() reports that net as "
                    "CANNOT DETERMINE, and that report is the answer."))
    s.net("VBAT", "U9.1")
    s.net("GND", "U9.2")
    N("U9_OUT_DESTINATION_UNKNOWN", CHOSEN, "U9.OUT?", "NOTHING ON THIS SHEET",
      "A one-terminal net, deliberately. The public record contains no "
      "statement about what U9 drives. What would settle it: a die-shot, a "
      "decapped board, or continuity on a live unit.")
    s.net("U9_OUT_DESTINATION_UNKNOWN", "U9.3")

    # =====================================================================
    # BLOCK 3 - U1, the nRF52832. CPU + BLE + NFC tag, one chip.
    # =====================================================================
    s.part("U1", "MCU_Nordic:nRF52832-QFxx",
           value="nRF52832-CIAA WLCSP-50 (drawn QFN-48)",
           group="soc",
           footprint="Package_DFN_QFN:QFN-48-1EP_6x6mm_P0.4mm_EP4.4x4.4mm",
           datasheet="https://infocenter.nordicsemi.com/pdf/"
                     "nRF52832_PS_v1.4.pdf",
           fields=B("U1", "SUBSTITUTION",
                    "THE PART IS CERTAIN AND THE PACKAGE IS SUBSTITUTED. "
                    "Marking 'N52832 CIAAE0 2102JK' was read off the die "
                    "photograph by lane L3 - fully legible, three lines. "
                    "CIAA is WLCSP-50 and NO COMPLETE BALL MAP IS SOURCED "
                    "HERE - O'Flynn's table gives TEN of the fifty (D3, E2, "
                    "F1, F4, G1, G3, H1, H2, H3, H4) - so this sheet uses "
                    "the QFN-48 (QFAA) symbol "
                    "of the SAME DIE. The netlist is right by signal name; "
                    "the pin NUMBERS are QFAA's. Inventing 50 ball "
                    "designators is what DECISIONS.md D9 forbids.",
                    {"Marking": "N52832 CIAAE0 2102JK",
                     "Real package": "WLCSP-50, 90 nm"}))

    for pad in ("13", "36", "48"):
        s.net("V1V8", "U1." + pad)
    for pad in ("31", "45", "49"):
        s.net("GND", "U1." + pad)

    # The DEC/DCC network. TOPOLOGY ONLY - see the sheet text.
    for ref, pad, note in (("C14", "1", "DEC1, pin 1"),
                           ("C15", "32", "DEC2, pin 32"),
                           ("C16", "33", "DEC3, pin 33"),
                           ("C17", "46", "DEC4, pin 46")):
        net = {"C14": "DEC1", "C15": "DEC2", "C16": "DEC3",
               "C17": "DEC4"}[ref]
        s.part(ref, "Device:C", value="CANNOT DETERMINE", group="soc",
               footprint=C0201,
               fields=B("R/C/L bulk", "PLACEHOLDER-L12",
                        "Decoupling at " + note + ". TOPOLOGY ONLY: no copy "
                        "of the nRF52832 product specification's reference "
                        "circuit is in this repository, so the VALUE stays "
                        "missing. A capacitor pin on an on-die regulator "
                        "output needs a capacitor; which capacitor is a "
                        "number this lane does not have."))
        s.net(net, "U1." + pad, ref + ".1")
        s.net("GND", ref + ".2")
    for nm, pad in (("DEC1", "1"), ("DEC2", "32"), ("DEC3", "33"),
                    ("DEC4", "46")):
        N(nm, INFERRED, "U1 internal regulator, pin " + pad,
          "its decoupling capacitor" +
          (" and L2 from DCC" if nm == "DEC4" else "") +
          (" and TP28" if nm == "DEC1" else ""),
          "The DEC pins are the on-die regulator's decoupling nodes. That "
          "they need capacitors is the part's own requirement; the values "
          "are CANNOT DETERMINE.")

    s.part("L2", "Device:L", value="DC/DC L - CANNOT DETERMINE",
           group="soc", footprint=L0402,
           fields=B("R/C/L bulk", "PLACEHOLDER-L12",
                    "The nRF52832's own DC/DC runs DCC (pin 47) through an "
                    "inductor into DEC4 (pin 46). NOT INDEPENDENTLY SOURCED "
                    "HERE - it is the family arrangement, and this repository "
                    "holds no copy of the reference circuit to check it "
                    "against. WHETHER APPLE ENABLED THE DC/DC AT ALL IS "
                    "UNKNOWN; the LDO mode needs no inductor and this "
                    "component would then not exist."))
    N("DCC", INFERRED, "U1.47, the SoC's own switching node", "L2",
      "See L2's note. This is the least-supported component on the sheet "
      "and it is drawn because omitting it would silently assert LDO mode.")
    s.net("DCC", "U1.47", "L2.1")
    s.net("DEC4", "L2.2")

    # =====================================================================
    # BLOCK 4 - both crystals. Two are SEEN, with markings read.
    # =====================================================================
    s.part("X1", "Device:Crystal", value="32 MHz? mark T320/RBEV - CANNOT DETERMINE", group="clock",
           footprint="Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm",
           fields=B("X1", "PLACEHOLDER-L12",
                    "HIGH that the marking is 'T320 / RBEV'. CANNOT "
                    "DETERMINE for manufacturer, part number, load "
                    "capacitance and tolerance. MEDIUM for '32 MHz' - that "
                    "is Catley's assignment, not a measurement. The 3215 "
                    "body is a PLACEHOLDER; bom.json has the package family "
                    "(seam-sealed ceramic, gold seal ring, two pads) but not "
                    "the size.",
                    {"Marking": "T320 / RBEV"}))
    s.part("X2", "Device:Crystal", value="32.768 kHz? mark A048L - CANNOT DETERMINE", group="clock",
           footprint="Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm",
           fields=B("X2", "PLACEHOLDER-L12",
                    "HIGH for the marking 'A048L'. MEDIUM for the frequency "
                    "assignment, untested. Visibly a LONGER, NARROWER "
                    "outline than X1 in the same photograph at the same "
                    "scale - which is what a 32.768 kHz can looks like "
                    "beside a 32 MHz one, and is the only physical support "
                    "the assignment has.",
                    {"Marking": "A048L"}))

    N("XC1", INFERRED, "U1.34 (XC1)", "X1 pin 1, C18",
      "The HFXO goes on the HFXO pins. Inferred from the part, not traced.")
    N("XC2", INFERRED, "U1.35 (XC2)", "X1 pin 2, C19", "Same.")
    N("XL1", INFERRED, "U1.2 (P0.00/XL1)", "X2 pin 1, C20",
      "The LFXO goes on the LFXO pins. On nRF52832 these are P0.00/P0.01, "
      "which is why the two lowest GPIO are unavailable for anything else.")
    N("XL2", INFERRED, "U1.3 (P0.01/XL2)", "X2 pin 2, C21", "Same.")
    s.net("XC1", "U1.34", "X1.1")
    s.net("XC2", "U1.35", "X1.2")
    s.net("XL1", "U1.2", "X2.1")
    s.net("XL2", "U1.3", "X2.2")

    for ref, net, xtal in (("C18", "XC1", "X1"), ("C19", "XC2", "X1"),
                           ("C20", "XL1", "X2"), ("C21", "XL2", "X2")):
        s.part(ref, "Device:C", value="LOAD CAP - CANNOT DETERMINE",
               group="clock", footprint=C0201,
               fields=B("R/C/L bulk", "PLACEHOLDER-L12",
                        "Load capacitor for " + xtal + ". THE CRYSTAL'S CL "
                        "IS UNPUBLISHED (bom.json: 'CANNOT DETERMINE for the "
                        "load capacitance'), and a load capacitor sized "
                        "without it is a frequency error, not a component. "
                        "The pads are drawn; the value is missing and stays "
                        "missing."))
        s.net(net, ref + ".1")
        s.net("GND", ref + ".2")

    # =====================================================================
    # BLOCK 5 - NFC. The tag peripheral is INSIDE the SoC. No NFC chip.
    # =====================================================================
    s.part("ANT2", "Device:Antenna_Loop",
           value="NFC COIL - WOUND WIRE, >=9 TURNS",
           group="rf", footprint="",
           fields=B("ANT2", "n/a",
                    "SEEN AND MEASURED, and the measurement was CORRECTED: "
                    "evidence/E02-THE-COIL-CORRECTION.md withdrew the "
                    "turn-count argument on 2026-09-05 because a solenoid "
                    "and a flat spiral present the same radial band width "
                    "from above, so two 'independent' numbers were one. What "
                    "survives is a direct observation: at full resolution the "
                    "conductors are individually resolved, coplanar and "
                    "equally lit. Per-sector counts 2, 6, 9, 6 across a "
                    "0.998 mm band give >=9 turns at ~111 um pitch, and 9 is "
                    "a LOWER BOUND.",
                    {"Open conflict": "The coil's two fine leads land on TP1 "
                     "and TP38. REFERENCE-TEARDOWN 2.4 calls those the VOICE "
                     "COIL's joints; Apple's own arrow in FCC photo 5 labels "
                     "that annulus the NFC ANTENNA. BOTH CANNOT BE TRUE and "
                     "this sheet does not resolve it - TP1/TP38 are "
                     "deliberately absent."}))

    for ref, pad, net in (("C6", "11", "NFC1"), ("C7", "12", "NFC2")):
        s.part(ref, "Device:C", value="NFC TUNING - CANNOT DETERMINE",
               group="rf", footprint=C0201,
               fields=B("R/C/L bulk", "PLACEHOLDER-L12",
                        "The NFC-A tag peripheral needs two series tuning "
                        "capacitors. Their value follows from the coil's "
                        "inductance, and APPLE'S COIL INDUCTANCE HAS NEVER "
                        "BEEN MEASURED HERE - only a lower bound on its turn "
                        "count. halo_rev_a learned this the expensive way: "
                        "its first NFC value was EIGHT TIMES WRONG because it "
                        "assumed a 2 uH antenna from a datasheet figure."))
    N("NFC1", INFERRED, "U1.11 (NFC1/P0.09)", "C6",
      "The NFC-A tag peripheral is the SoC's own, on pins P0.09/P0.10. There "
      "is NO separate NFC chip in an AirTag - that deletes a line most clone "
      "BOMs carry.")
    N("NFC2", INFERRED, "U1.12 (NFC2/P0.10)", "C7", "Same.")
    N("NFC_COIL_A", INFERRED, "C6", "ANT2 pin 1", "Series tuning into the "
      "coil. See ANT2's open conflict about what that annulus actually is.")
    N("NFC_COIL_B", INFERRED, "C7", "ANT2 pin 2", "Same.")
    s.net("NFC1", "U1.11", "C6.1")
    s.net("NFC2", "U1.12", "C7.1")
    s.net("NFC_COIL_A", "C6.2", "ANT2.1")
    s.net("NFC_COIL_B", "C7.2", "ANT2.2")

    # =====================================================================
    # BLOCK 6 - the 2.4 GHz path
    # =====================================================================
    s.part("ANT1", "Device:Antenna",
           value="BLE 2.4GHz INVERTED-F (on carrier)",
           group="rf", footprint="",
           fields=B("ANT1", "n/a",
                    "HIGH that Apple labels a Bluetooth antenna at that rim "
                    "position - they labelled it themselves in a regulatory "
                    "filing. CANNOT DETERMINE for the geometry. It is "
                    "printed onto the plastic carrier, so there is no PCB "
                    "land pattern at all and 'n/a' is the honest FP-basis."))
    for ref, val in (("C8", "PI SHUNT"), ("C9", "PI SHUNT")):
        s.part(ref, "Device:C", value=val + " - CANNOT DETERMINE",
               group="rf", footprint=C0201,
               fields=B("R/C/L bulk", "PLACEHOLDER-L12",
                        "A matching network between the SoC's ANT pin and a "
                        "printed antenna is required by the part; ITS VALUES "
                        "ARE A MEASUREMENT NOBODY HAS TAKEN on Apple's "
                        "copper. Drawn as a pi so the topology can hold a "
                        "future S11 result."))
    s.part("L3", "Device:L", value="PI SERIES - CANNOT DETERMINE",
           group="rf", footprint=L0402,
           fields=B("R/C/L bulk", "PLACEHOLDER-L12", "Series element of the "
                    "pi. Same refusal as C8/C9."))
    N("ANT_SOC", INFERRED, "U1.30 (ANT)", "C8 shunt, L3 series",
      "The radio comes out of the ANT pin. Everything after it is topology "
      "with no measured values.")
    N("ANT_FEED", INFERRED, "L3", "C9 shunt, ANT1",
      "The feed point of the printed inverted-F.")
    s.net("ANT_SOC", "U1.30", "C8.1", "L3.1")
    s.net("GND", "C8.2")
    s.net("ANT_FEED", "L3.2", "C9.1", "ANT1.1")
    s.net("GND", "C9.2")

    # =====================================================================
    # BLOCK 7 - the flash. Identified by INSTRUMENT, not by marking.
    # =====================================================================
    s.part("U3", "Memory_Flash:GD25QxxxEY",
           value="GD25LQ32C 32Mb 1.8V NOR (WLCSP-10)",
           group="memory", footprint="",
           datasheet="https://www.gigadevice.com/",
           fields=B("U3", "PLACEHOLDER-L12",
                    "THE BEST-EVIDENCED PART ON THIS SHEET THAT NOBODY EVER "
                    "SAW. O'Flynn did not read a marking - he read the CHIP: "
                    "Segger J-Flash SPI reported the device as a GD25LQ32C "
                    "over SPI. A JEDEC ID interrogated out of live silicon "
                    "outranks iFixit's visual 'GD25LE32D'. The package is "
                    "WLCSP-10 (ten pads, centre pads absent) and KiCad ships "
                    "no WLCSP-10 NOR symbol, so the WSON-8 symbol carries the "
                    "SAME EIGHT SIGNALS with different pin numbers. L12 draws "
                    "the real land pattern.",
                    {"Identified by": "JEDEC ID read over SPI, not a marking",
                     "Rejected": "GD25LE32D (iFixit, visual only)"}))
    s.net("V1V8_SW", "U3.8", "U3.3", "U3.7")
    s.net("GND", "U3.4", "U3.9")

    # THESE FOUR WERE "CHOSEN" UNTIL THE ANCHOR REQUIREMENT MADE SOMEBODY
    # OPEN THE FILE. O'Flynn's test-point table gives the flash bus by pad,
    # by nRF BALL and by GPIO, and three of this sheet's four assignments
    # were wrong. They are MEASURED now, and they are measured because a
    # feature designed to stop MEASURED being typed forced a read of the
    # source that was already being cited.
    N("SPI_SCK", MEASURED, "U1.20 (P0.17, nRF ball G3)",
      "U3 SCLK; U2 SPI_SCK (DNP); TP22",
      "O'Flynn, test point 22: '1.8V SPI Flash - SCLK / nRF ball G3 "
      "(P0.17)'. THIS SHEET FIRST DREW IT ON P0.12 AND THAT WAS WRONG.",
      anchor=A_OFLYNN, contains="nRF ball G3 (P0.17)")
    N("SPI_MOSI", MEASURED, "U1.19 (P0.16, nRF ball H3)",
      "U3 SI/IO0; U2 SPI_MOSI (DNP); TP19",
      "O'Flynn, test point 19: '1.8V SPI Flash - Data In (COPI) / nRF ball "
      "H3 (P0.16)'. COPI is into the flash, so it is the MCU's output. This "
      "sheet first drew it on P0.13.",
      anchor=A_OFLYNN, contains="Data In (COPI) / nRF ball H3 (P0.16)")
    N("SPI_MISO", MEASURED, "U3 SO/IO1 (and U2, DNP)",
      "U1.18 (P0.15, nRF ball H4); TP20",
      "O'Flynn, test point 20: '1.8V SPI Flash - Data Out (CIPO) /nRF ball "
      "H4 (P0.15)'. This sheet first drew it on P0.14.",
      anchor=A_OFLYNN, contains="Data Out (CIPO) /nRF ball H4 (P0.15)")
    N("FLASH_nCS", MEASURED, "U1.14 (P0.11, nRF ball F4)", "U3 nCS; TP24",
      "O'Flynn, test point 24: '1.8V SPI Flash - Chip Select (CS)/ nRF ball "
      "F4 (P0.11)'. THE ONLY ONE OF THE FOUR THIS SHEET HAD RIGHT, and it "
      "had it right by luck - it was CHOSEN, and a choice that happens to "
      "match a measurement is still a choice until somebody checks.",
      anchor=A_OFLYNN, contains="Chip Select (CS)/ nRF ball F4 (P0.11)")
    s.net("SPI_SCK", "U1.20", "U3.6")
    s.net("SPI_MOSI", "U1.19", "U3.5")
    s.net("SPI_MISO", "U1.18", "U3.2")
    s.net("FLASH_nCS", "U1.14", "U3.1")

    # =====================================================================
    # BLOCK 8 - U2. Apple's UWB SiP. PLACED, AND NOT POPULATED.
    # =====================================================================
    s.part("U2", uwb_id,
           value="APPLE U1 UWB SiP - DNP, NEVER SOLD",
           group="uwb", footprint="", dnp=True,
           fields=B("U2", "PLACEHOLDER-L12",
                    "DO NOT POPULATE. Apple's U1 (die TMKA75, TSMC 16 nm, in "
                    "a 20.58 mm2 USI system-in-package with an embedded "
                    "crystal and a Sony RF switch) is NOT SOLD TO ANYONE. "
                    "This is not a sourcing problem, it is a "
                    "does-not-exist-for-us problem, and it is the reason "
                    "Precision Finding is a GAP and not a to-do. THE PIN "
                    "NUMBERS ON THIS SYMBOL ARE THIS SHEET'S OWN INVENTION - "
                    "no pinout for this module has ever been published, so "
                    "the land pattern does not exist and cannot be "
                    "fabricated. It is drawn so that a replica which cannot "
                    "be finished says so on its own schematic.",
                    {"DNP": "YES - UNPOPULATED",
                     "Availability": "NEVER SOLD. Not a price, not a lead "
                                     "time - an impossibility."}))
    s.net("V1V8_SW", "U2.1")
    s.net("GND", "U2.2")
    s.net("SPI_SCK", "U2.3")
    s.net("SPI_MOSI", "U2.4")
    s.net("SPI_MISO", "U2.5")
    N("UWB_nCS", CHOSEN, "U1.27 (P0.22)", "U2 SPI_nCS (DNP)",
      "See SPI_SCK. Every UWB control line here is CHOSEN and lands on a "
      "part that is not populated.")
    N("UWB_IRQ", CHOSEN, "U2 IRQ (DNP)", "U1.28 (P0.23)", "Same.")
    N("UWB_nRESET", CHOSEN, "U1.29 (P0.24)", "U2 nRESET (DNP)", "Same.")
    s.net("UWB_nCS", "U1.27", "U2.6")
    s.net("UWB_IRQ", "U1.28", "U2.7")
    s.net("UWB_nRESET", "U1.29", "U2.8")

    s.part("ANT3", "Device:Antenna", value="UWB PATCH 6.5/8GHz (on carrier)", group="uwb", footprint="",
           fields=B("ANT3", "n/a",
                    "HIGH for the label - Apple labelled it in a regulatory "
                    "filing. CANNOT DETERMINE for the geometry. Its only "
                    "driver on this sheet is DNP."))
    # The value said "U.FL / IPEX MHF RECEPTACLE" until x_schematic_check's C6
    # fired on it: bom.json's J1 line begins "CANNOT DETERMINE — a U.FL /
    # IPEX MHF-class receptacle by construction", and a value that names a
    # family without naming the refusal reads as an identification. What is
    # HIGH is that a coaxial receptacle is FITTED; which one it is, is not.
    s.part("J1", "Connector:Conn_Coaxial",
           value="COAX RF RECEPTACLE - PART CANNOT DETERMINE",
           group="uwb",
           footprint="Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical",
           fields=B("J1", "SUBSTITUTION",
                    "THIS PART REFUTES 'CONNECTORS: NONE ANYWHERE', which "
                    "REFERENCE-TEARDOWN 2.5 states and SPEC.md repeats. A "
                    "circular RF receptacle - metal outer shell, four solder "
                    "tabs, dark dielectric annulus, gold centre contact - is "
                    "unambiguous at 5x on the component face. HIGH "
                    "confidence that it is fitted on this unit. WHICH "
                    "receptacle (U.FL vs one of the MHF variants) is a "
                    "SUBSTITUTION; the Hirose land pattern is the family's "
                    "common one."))
    N("UWB_RF", CHOSEN, "U2 RF (DNP)", "ANT3; J1 centre",
      "THE WEAKEST NET ON THIS SHEET AND IT IS LABELLED SO. bom.json J1: "
      "'its position beside the UWB module is consistent with a UWB "
      "conducted-test port, but THE NET IT LANDS ON IS NOT ESTABLISHED'. "
      "Worse: UNK-B sits between U2 and J1 and is 'consistent with an RF "
      "switch, filter or balun'. If UNK-B is a switch then J1 and ANT3 are "
      "NOT one net and this net is wrong in a way this sheet cannot detect.")
    s.net("UWB_RF", "U2.9", "ANT3.1", "J1.1")
    s.net("GND", "J1.2")

    # =====================================================================
    # BLOCK 9 - accelerometer. Generic, because the part is CANNOT DETERMINE.
    # =====================================================================
    s.part("U4", acc_id,
           value="3-AXIS ACCEL - PART CANNOT DETERMINE",
           group="sensor", footprint="",
           fields=B("U4", "PLACEHOLDER-L12",
                    "bom.json U4: TWO VISUALLY IDENTICAL METAL-LID PARTS are "
                    "present and neither is confidently the accelerometer. "
                    "They carry a single dark dimple and NO READABLE TEXT AT "
                    "ANY MAGNIFICATION AVAILABLE. 'BMA280' comes from "
                    "iFixit/Catley; this lane tried to corroborate it by "
                    "package size and could not. What would settle it: a "
                    "higher-resolution photograph of the lid, or a decap.",
                    {"Interface": "I2C CHOSEN. SPI is equally consistent "
                                  "with every photograph - the part is not "
                                  "even identified, let alone its bus."}))
    s.net("V1V8", "U4.1", "U4.2", "U4.7")
    s.net("GND", "U4.3", "U4.6")
    s.nc("U4.9")
    N("ACC_SCL", CHOSEN, "U1.8 (P0.06)", "U4 SCL/SPC",
      "I2C is CHOSEN over SPI: it costs two pins instead of four and lets "
      "the sensor answer while the flash is deselected. Nothing in the "
      "record says which bus Apple used.")
    N("ACC_SDA", CHOSEN, "U1.9 (P0.07) and U4 SDA/SDI", "both",
      "Same. R5 pulls it up.")
    N("ACC_INT1", CHOSEN, "U4 INT1", "U1.10 (P0.08)",
      "Motion wake is a real requirement - DULT anti-stalking needs it "
      "(docs/ANTI-STALKING.md) - so an interrupt line exists. Which pin is "
      "this sheet's.")
    s.net("ACC_SCL", "U1.8", "U4.4", "R5.1")
    s.net("ACC_SDA", "U1.9", "U4.5", "R6.1")
    s.net("ACC_INT1", "U1.10", "U4.8")
    for ref in ("R5", "R6"):
        s.part(ref, "Device:R", value="I2C PULL-UP - CANNOT DETERMINE",
               group="sensor", footprint=R0402,
               fields=B("R/C/L bulk", "PLACEHOLDER-L12",
                        "An I2C bus needs pull-ups. THE BUS ITSELF IS "
                        "CHOSEN (see U4), so these two resistors exist "
                        "because of this sheet's choice and not because "
                        "anyone saw them."))
        s.net("V1V8", ref + ".2")

    # =====================================================================
    # BLOCK 10 - the sounder: class-D amplifier into a voice coil
    # =====================================================================
    s.part("U5", "Audio:MAX98357A",
           value="MAX98357A-CLASS AMP (LOW conf)", group="audio",
           footprint="Package_CSP:WLCSP-16_4x4_B2.17x2.32mm_P0.5mm",
           fields=B("U5", "SUBSTITUTION",
                    "SILICON CITED, LOW confidence: the part is not "
                    "locatable in any photograph available here, and the two "
                    "sources disagree on the suffix (A vs B). It is on the "
                    "sheet because the tag demonstrably makes a sound and "
                    "the voice coil demonstrably exists. The KiCad symbol is "
                    "the TQFP-16 pinout; Apple's is WLCSP. SIGNALS TRAVEL, "
                    "PIN NUMBERS DO NOT."))
    s.net("VBAT", "U5.7", "U5.8")
    s.net("GND", "U5.3", "U5.11", "U5.15", "U5.17")
    s.nc("U5.5", "U5.6", "U5.12", "U5.13")

    s.part("R8", "Device:R", value="GAIN STRAP - CANNOT DETERMINE",
           group="audio", footprint=R0402,
           fields=B("R/C/L bulk", "PLACEHOLDER-L12",
                    "The MAX98357 family sets gain with one resistor on "
                    "GAIN_SLOT. Which gain Apple chose is unknown, and so "
                    "is whether this amplifier is the part at all."))
    N("AMP_GAIN", CHOSEN, "R8 to GND", "U5 GAIN_SLOT",
      "A gain strap has to go somewhere. Value missing.")
    s.net("AMP_GAIN", "U5.2", "R8.1")
    s.net("GND", "R8.2")

    N("I2S_BCLK", CHOSEN, "U1.16 (P0.13)", "U5 BCLK",
      "A class-D amplifier of this family takes I2S. THAT the MCU drives it "
      "digitally follows from the part; WHICH PINS is this sheet's choice. "
      "It sat on P0.16 until O'Flynn's table showed that pad is the flash's "
      "COPI.",
      derived_from="the part's own interface, on whatever pins the measured "
                   "flash bus left free")
    N("I2S_LRCLK", CHOSEN, "U1.17 (P0.14)", "U5 LRCLK",
      "Same. It sat on P0.17, which is the flash's measured SCLK.",
      derived_from="as I2S_BCLK")
    N("I2S_DIN", CHOSEN, "U1.22 (P0.19)", "U5 DIN", "Same.",
      derived_from="as I2S_BCLK")
    N("AMP_nSD", CHOSEN, "U1.23 (P0.20)", "U5 nSD_MODE",
      "Shutdown control. A tag that sleeps at 2.3 uA does not leave a "
      "class-D amplifier enabled, so a shutdown line is an argument; the pin "
      "is a choice.")
    s.net("I2S_BCLK", "U1.16", "U5.16")
    s.net("I2S_LRCLK", "U1.17", "U5.14")
    s.net("I2S_DIN", "U1.22", "U5.1")
    s.net("AMP_nSD", "U1.23", "U5.4")

    s.part("LS1", "Device:Speaker",
           value="VOICE COIL - WOUND MAGNET WIRE",
           group="audio", footprint="",
           fields=B("SPK-COIL", "n/a",
                    "There is no speaker in an AirTag. There is a VOICE COIL "
                    "against a fixed central magnet, and the HOUSING IS THE "
                    "DIAPHRAGM. HIGH for the mechanism - iFixit had it in "
                    "their hands - and LOW for anything geometric. The "
                    "magnet (bom.json SPK-MAGNET) is mechanical and carries "
                    "no net, so it is not on this sheet."))
    N("SPK_P", INFERRED, "U5 OUTP", "LS1 pin 1; R9 (sense divider)",
      "A class-D bridge drives the coil differentially. Inferred from the "
      "part family.")
    N("SPK_N", INFERRED, "U5 OUTN", "LS1 pin 2", "Same.")
    s.net("SPK_P", "U5.9", "LS1.1", "R9.1")
    s.net("SPK_N", "U5.10", "LS1.2")

    # =====================================================================
    # BLOCK 11 - U7, the op-amp. The part on this sheet with the LEAST
    # established purpose, drawn in the shape its source describes.
    # =====================================================================
    s.part("U7", "Amplifier_Operational:TLV9001IDCK",
           value="TLV9001-CLASS OP-AMP - ROLE INFERRED",
           group="audio", footprint="Package_TO_SOT_SMD:SOT-353_SC-70-5",
           fields=B("U7", "SUBSTITUTION",
                    "SILICON CITED, LOW confidence, package CANNOT "
                    "DETERMINE. REFERENCE-TEARDOWN says only 'op-amp "
                    "(speaker/analog path)'. THIS SHEET DRAWS IT AS A UNITY "
                    "BUFFER FROM A DIVIDER ON SPK_P INTO AN ADC INPUT, "
                    "because that is the one role in a speaker path that "
                    "needs an op-amp and costs no current when idle. IT "
                    "COULD EQUALLY BE A MICROPHONE PREAMP, A CURRENT-SENSE "
                    "AMPLIFIER OR A FILTER. This is the largest single "
                    "reconstruction on the sheet and it is labelled so.",
                    {"Alternative roles not excluded":
                     "current-sense amp; anti-alias filter; bias buffer"}))
    s.net("V1V8", "U7.5")
    s.net("GND", "U7.2")
    for ref, val in (("R9", "SENSE DIV TOP"), ("R10", "SENSE DIV BOT")):
        s.part(ref, "Device:R", value=val + " - CANNOT DETERMINE",
               group="audio", footprint=R0402,
               fields=B("R/C/L bulk", "PLACEHOLDER-L12",
                        "Part of this sheet's INFERRED role for U7. If U7 is "
                        "not a buffer, these two resistors do not exist."))
    N("SPK_DIV", CHOSEN, "R9/R10 divider on SPK_P", "U7 non-inverting input",
      "Entirely this sheet's reconstruction of U7's role.")
    N("SPK_SENSE", CHOSEN, "U7 output (unity buffer)", "U1.40 (P0.28/AIN4)",
      "Same. Wired as a follower - output to inverting input - so the "
      "drawing is at least self-consistent.")
    s.net("SPK_DIV", "R9.2", "R10.1", "U7.1")
    s.net("GND", "R10.2")
    s.net("SPK_SENSE", "U7.4", "U7.3", "U1.40")

    # =====================================================================
    # BLOCK 12 - cell-removal sense. Both positives, per REFERENCE-TEARDOWN.
    # =====================================================================
    for ref, val in (("R1", "SNS TOP P+_PWR"), ("R2", "SNS BOT P+_PWR"),
                     ("R3", "SNS TOP P+_SNS"), ("R4", "SNS BOT P+_SNS")):
        s.part(ref, "Device:R", value=val + " - CANNOT DETERMINE", group="sense", footprint=R0402,
               fields=B("R/C/L bulk", "PLACEHOLDER-L12",
                        "REFERENCE-TEARDOWN 2.5 gives the ONE electrical "
                        "number this sheet has about the sense path: the "
                        "right-hand positive is sensed at ~50 nA. At 3 V "
                        "that is a 60 Mohm total, which is a divider, not a "
                        "load - but the split between top and bottom is not "
                        "recorded anywhere and is left missing."))
    N("VBAT_SNS_1", INFERRED, "R1/R2 divider on VBAT_RAW", "U1.4 (P0.02/AIN0)",
      "The FIRST positive is sensed. Both positives being sensed is the "
      "measured fact; the divider and the ADC pin are this sheet's shape "
      "for it.")
    N("VBAT_SNS_2", INFERRED, "R3/R4 divider on VBAT_SNS_P2",
      "U1.5 (P0.03/AIN1)",
      "The SECOND positive is sensed, and THIS IS THE POINT OF THE WHOLE "
      "BLOCK. Pull the cell and both dividers collapse in well under a "
      "millisecond while C1-C5 hold VBAT up for seconds - which is exactly "
      "the window the five-removals factory reset counts in.")
    s.net("VBAT_SNS_1", "R1.2", "R2.1", "U1.4")
    s.net("VBAT_SNS_2", "R3.2", "R4.1", "U1.5")
    s.net("GND", "R2.2", "R4.2")

    # =====================================================================
    # BLOCK 13 - SWD and the glitch pad. THE ONLY MEASURED NET NAMES HERE.
    # =====================================================================
    # THE ANCHOR REQUIREMENT CORRECTED THE CITATION HERE TOO. Two of these
    # four are given in O'Flynn's own table WITH THEIR nRF BALL, and two are
    # not: his table says "35 | nRF ball F1 (SWCLK)" and "36 | nRF ball G1
    # (SWDIO)" with no GPIO, because SWCLK and SWDIO are dedicated pads and
    # have none. TP30 and TP31 carry both. Each row below claims the exact
    # string that is in the file it names, and cepcb opens the file.
    for ref, pin, net, note, anchor, claim in (
            ("TP30", "24", "nRESET",
             "O'Flynn's table, verbatim: '30 | nRF ball H1 (P0.21/nRST)'.",
             A_OFLYNN, "nRF ball H1 (P0.21/nRST)"),
            ("TP35", "25", "SWDCLK",
             "O'Flynn's table, verbatim: '35 | nRF ball F1 (SWCLK)'. No GPIO "
             "number, because SWCLK is a dedicated pad and has none.",
             A_OFLYNN, "nRF ball F1 (SWCLK)"),
            ("TP36", "26", "SWDIO",
             "O'Flynn's table, verbatim: '36 | nRF ball G1 (SWDIO)'.",
             A_OFLYNN, "nRF ball G1 (SWDIO)"),
            ("TP31", "21", "SWO",
             "O'Flynn's table, verbatim: '31 | nRF ball H2 (P0.18/SWO)'.",
             A_OFLYNN, "nRF ball H2 (P0.18/SWO)"),
    ):
        s.part(ref, "Connector:TestPoint", value=net + " (O'Flynn " + ref + ")",
               group="test", footprint="TestPoint:TestPoint_Pad_D1.0mm",
               in_bom=False,
               fields=B(None, "PLACEHOLDER-L12",
                        note + " THESE FOUR ARE THE ONLY NETS ON THIS SHEET "
                        "WHOSE NAMES WERE READ OFF THE HARDWARE: SWD is on "
                        "exposed test pads and O'Flynn published which pad "
                        "is which. APPROTECT is enabled on Apple's units, so "
                        "the pads are present and locked.",
                        {"Source": A_OFLYNN + " — the pad-to-BALL table, "
                                   "checked at build time by cepcb's basis "
                                   "resolver, which is how the first "
                                   "citation here was found to be pointing "
                                   "at the right file for the wrong reason"}))
        N(net, MEASURED, "U1 pin " + pin, ref + " (exposed test pad)", note,
          anchor=anchor, contains=claim)
        s.net(net, "U1." + pin, ref + ".1")

    s.part("TP28", "Connector:TestPoint", value="nRF CORE RAIL - THE GLITCH PAD", group="test",
           footprint="TestPoint:TestPoint_Pad_D1.0mm", in_bom=False,
           fields=B(None, "PLACEHOLDER-L12",
                    "O'Flynn's TP28 is the nRF core rail. LimitedResults' "
                    "nRF52 voltage glitch is applied HERE and defeats "
                    "APPROTECT - and their own words are that it 'cannot be "
                    "patched without Silicon redesign.' It is on this sheet "
                    "because a replica that hides its own attack surface is "
                    "not a replica, and because halo's threat model has to "
                    "assume an attacker can do this to OUR tags too.",
                    {"Source": "research/fetched/"
                               "A-limitedresults-nrf52-approtect-bypass.md"}))
    s.net("DEC1", "TP28.1")

    # THE REST OF O'FLYNN'S TABLE. Every one of these is a pad he named on a
    # board he had, and they are the densest measured evidence this whole
    # reconstruction has. They are placed so the net they land on carries the
    # measurement rather than a footnote pointing at it.
    for ref, net, claim, note in (
            ("TP5", "VBAT_SNS_P2", "| 5   | VCC2 (Connects to VCC2 input)",
             "O'Flynn: '5 | VCC2 (Connects to VCC2 input)'. WHICH of VCC1 "
             "and VCC2 is the sense finger is NOT in his table - he says "
             "only that both are needed - so the sense/power split is "
             "REFERENCE-TEARDOWN's and this pad could be the other one."),
            ("TP6", "VBAT_RAW", "| 6   | VCC1 (Connects to VCC1 input)",
             "O'Flynn: '6 | VCC1 (Connects to VCC1 input)'. Same caveat."),
            ("TP7", "GND", "| 7   | GND", "O'Flynn: '7 | GND'."),
            ("TP19", "SPI_MOSI", "Data In (COPI) / nRF ball H3 (P0.16)",
             "O'Flynn: the flash's COPI, on nRF ball H3."),
            ("TP20", "SPI_MISO", "Data Out (CIPO) /nRF ball H4 (P0.15)",
             "O'Flynn: the flash's CIPO, on nRF ball H4."),
            ("TP21", "V1V8_SW", "| 21  | 1.8V SPI Flash VCC",
             "O'Flynn: '21 | 1.8V SPI Flash VCC'. He forces the flash on by "
             "applying 1.8 V HERE, which is the direct evidence that this "
             "rail is switched and not the main one."),
            ("TP22", "SPI_SCK", "nRF ball G3 (P0.17)",
             "O'Flynn: the flash's SCLK, on nRF ball G3."),
            ("TP24", "FLASH_nCS", "Chip Select (CS)/ nRF ball F4 (P0.11)",
             "O'Flynn: the flash's chip select, on nRF ball F4."),
            ("TP29", "GND", "| 29  | Apple Logo :) GND",
             "O'Flynn: '29 | Apple Logo :) GND'. The Apple logo on the "
             "silkscreen is a ground pad, which is the most Apple sentence "
             "in the whole teardown."),
            ("TP34", "V1V8", "| 34  | 1.8V from nRF",
             "O'Flynn: '34 | 1.8V from nRF', VERBATIM AND AMBIGUOUS. It "
             "could mean the 1.8 V rail probed near the nRF, or 1.8 V the "
             "nRF itself sources. This sheet lands it on V1V8 and does not "
             "claim to have resolved his wording."),
    ):
        s.part(ref, "Connector:TestPoint", value=net + " (O'Flynn " + ref + ")",
               group="test", footprint="TestPoint:TestPoint_Pad_D1.0mm",
               in_bom=False,
               fields=B(None, "PLACEHOLDER-L12", note,
                        {"Source": A_OFLYNN}))
        s.net(net, ref + ".1")

    # TP9 lands on a GPIO whose FUNCTION O'Flynn does not give. The pad and
    # the ball are measured; what it does is not, and a test point on a net
    # named after its function would invent one.
    s.part("TP9", "Connector:TestPoint", value="P0.26 - FUNCTION CANNOT DETERMINE", group="test",
           footprint="TestPoint:TestPoint_Pad_D1.0mm", in_bom=False,
           fields=B(None, "PLACEHOLDER-L12",
                    "O'Flynn: '9 | nRF ball D3 (P0.26)'. He gives the pad "
                    "and the ball and NOT the function, so this net is named "
                    "for the pin and nothing else. TP8 IS DELIBERATELY "
                    "ABSENT: his table says '8 | nRF ball E2 (P0.16)' while "
                    "row 19 says the flash's COPI is 'nRF ball H3 (P0.16)'. "
                    "TWO DIFFERENT BALLS CARRY THE SAME GPIO NUMBER and one "
                    "of the two is a transcription error. This sheet takes "
                    "the SPI block's assignment because its four balls "
                    "H3/H4/G3/F4 form a coherent group, and records the "
                    "conflict rather than resolving it.",
                    {"Source": A_OFLYNN}))
    N("TP9_P0.26", MEASURED, "U1.38 (P0.26, nRF ball D3)", "TP9",
      "O'Flynn's table gives the pad and the ball. IT DOES NOT GIVE THE "
      "FUNCTION, so this net is named after the pin and asserts nothing "
      "about what Apple uses it for.",
      anchor=A_OFLYNN, contains="nRF ball D3 (P0.26)")
    s.net("TP9_P0.26", "U1.38", "TP9.1")

    s.power("VBAT_RAW", "VBAT", "V1V8", "V1V8_SW", "GND")

    # ---------------------------------------------------------------------
    # The sentences a reviewer needs, ON THE SHEET rather than in a document
    # nobody opens next to KiCad.
    # ---------------------------------------------------------------------
    s.text("halo REPLICA - Apple AirTag A2187 (FCC ID BCGA2187), "
           "reconstructed. NOBODY HAS TRACED APPLE'S COPPER. Every net "
           "carries a basis - MEASURED, INFERRED or CHOSEN - and NETS.md "
           "beside this file lists all of them with the counts DERIVED, "
           "never typed. 13 of 52 nets are MEASURED, and every one of those "
           "names a FILE AND A STRING THAT MUST BE IN IT, checked at build "
           "time. The other 39 are inference and choice.")
    s.text("FOUR NETS ON THIS SHEET WERE WRONG UNTIL A CHECK FORCED SOMEBODY "
           "TO OPEN THE FILE THEY ALREADY CITED. The flash bus was drawn on "
           "P0.12/P0.13/P0.14 as a free CHOICE. O'Flynn's test-point table "
           "gives it by pad, by nRF BALL and by GPIO: SCLK on P0.17 (ball "
           "G3), COPI on P0.16 (H3), CIPO on P0.15 (H4), CS on P0.11 (F4). "
           "Three of the four were wrong and the fourth was right by luck. "
           "The bus is MEASURED now.")
    s.text("TEN CIAA BALLS ARE SOURCED, AND FORTY ARE NOT. O'Flynn's table "
           "names nRF ball designators for D3, E2, F1, F4, G1, G3, H1, H2, "
           "H3 and H4. That is not a ball map and does not make one - the "
           "package here is still the QFN-48 substitution - but it is ten "
           "more than this sheet first claimed existed, and L12 should have "
           "them when it draws the WLCSP land.")
    s.text("A CONTRADICTION INSIDE O'FLYNN'S OWN TABLE, CARRIED NOT "
           "RESOLVED: row 8 reads 'nRF ball E2 (P0.16)' and row 19 reads "
           "'nRF ball H3 (P0.16)'. Two different balls with one GPIO number; "
           "one is a transcription error. This sheet takes row 19 because "
           "the SPI block's four balls H3/H4/G3/F4 are a coherent group, and "
           "TP8 IS DELIBERATELY ABSENT rather than drawn on a guess.")
    s.text("THE iFIXIT ARGUMENT IS NOW SETTLED BY MEASUREMENT, not by "
           "self-consistency. O'Flynn, verbatim: 'The nrf controls power to "
           "the SPI flash, so you need to override it by supplying 1.8V on "
           "test point 21', and 'most of time the flash is powered off and "
           "thus the pins are tri-stated'. The flash sits on a switched "
           "1.8 V rail the MCU commands - which is what this sheet drew from "
           "the argument that a load switch cannot gate its own controller.")
    s.text("U2 IS APPLE'S 'U1' UWB SiP AND IT IS DNP / UNPOPULATED. Apple "
           "does not sell it to anyone, at any price, with any lead time. "
           "That is not a sourcing problem, it is a does-not-exist-for-us "
           "problem, and Precision Finding is therefore a GAP and not a "
           "to-do. Its pin NUMBERS on this sheet are invented: no pinout for "
           "this module has ever been published, so its land pattern does "
           "not exist and NOTHING MAY BE FABRICATED FROM IT.")
    s.text("NAME COLLISION: on this sheet U1 is the NORDIC MCU and U2 is "
           "the Apple UWB part, following bom.json and REFERENCE-TEARDOWN. "
           "The press calls the Apple part 'the U1'. Never write bare U1 "
           "about it.")
    s.text("U4 IS CANNOT DETERMINE. Two visually identical metal-lid parts "
           "are on the board and neither is confidently the accelerometer; "
           "no marking is readable at any magnification available here. "
           "'BMA280' is a teardown assertion this project failed to "
           "corroborate. The symbol is generic and the value field says so.")
    s.text("U9 IS CANNOT DETERMINE, INCLUDING ITS FUNCTION. Marking "
           "'1A8 / 1950'. Its output is deliberately wired to NOTHING, "
           "because the record does not say what it feeds and a wire to a "
           "plausible load would be this sheet inventing a circuit.")
    s.text("D3 IS AN ADDITION, NOT AN OBSERVATION (DECISIONS.md D24). "
           "nRF52832 product spec 42.10: a strong NFC field can push current "
           "BACKWARDS into the supply through parasitic diodes and ESD "
           "structures, and a CR2032 does not tolerate return current. A "
           "phone on the tag is a strong field by design. COST: a Schottky "
           "drops a few hundred mV against a cell already tracked to 68 mV "
           "of end-of-life droop; an ideal-diode controller drops millivolts "
           "and costs money. No photograph here shows a diode in Apple's "
           "power path.")
    s.text("THE PACKAGES ARE NOT APPLE'S PACKAGES. U1 is an nRF52832-CIAA, "
           "WLCSP-50, drawn with the QFN-48 (QFAA) symbol of the same die "
           "because no COMPLETE CIAA ball map is sourced here (ten balls "
           "are; forty are not). U3 is a "
           "WLCSP-10 drawn as WSON-8. U5 is a WLCSP drawn as TQFP-16. THE "
           "NETLIST IS RIGHT BY SIGNAL NAME AND THE PIN NUMBERS ARE NOT "
           "APPLE'S. Every part carries an FP-basis field; L12 owns the land "
           "patterns.")
    s.text("THIS SHEET DEPARTS FROM iFIXIT ON ONE THING AND SAYS SO: iFixit "
           "has the load switch U8 gating 'U1 + flash' where U1 is the MCU. "
           "A load switch whose enable comes from the MCU it powers can "
           "never be turned on. Here U8 gates the FLASH and the UWB module "
           "and the MCU sits on the 1.8 V rail directly.")
    s.text("FOUR PARTS THAT ARE ON THE REAL BOARD AND NOT ON THIS SHEET, "
           "because placing a part asserts what it is: D1/D2 (marking K11, "
           "a matched pair - part AND function CANNOT DETERMINE), CT1 "
           "(marking '6X A75', blue body - and 'blue' is a colour, not a "
           "technology), UNK-A (large matte-black rectangle, no marking at "
           "all) and UNK-B (pale ceramic square between U2 and J1 - if it is "
           "an RF switch then this sheet's UWB_RF net is wrong).")
    s.text("J1 REFUTES 'CONNECTORS: NONE ANYWHERE', which REFERENCE-TEARDOWN "
           "2.5 states and SPEC.md repeats. A U.FL/IPEX-class coaxial "
           "receptacle is unambiguous at 5x on the component face of "
           "O'Flynn's retail unit. Two documents in this repository are "
           "wrong and this schematic is where that became unavoidable.")
    s.text("TP1 AND TP38 ARE DELIBERATELY ABSENT. The fine coil leads land "
           "there; REFERENCE-TEARDOWN 2.4 calls them the VOICE COIL's joints "
           "and Apple's own arrow in FCC photo 5 labels that annulus the "
           "NFC ANTENNA. Both cannot be true and this sheet does not pick a "
           "winner.")
    s.text("EVERY CAPACITOR AND RESISTOR VALUE ON THIS SHEET IS CANNOT "
           "DETERMINE, and that is not laziness. bom.json: 'This is not a "
           "gap that any photograph can close: a 100 nF and a 1 uF 0402 are "
           "visually identical.' A missing value stays missing. THIS BOARD "
           "IS NOT BUILDABLE AS DRAWN and saying so is the point.")

    # HAND EVERY BASIS TO ce-pcb, WHICH OPENS THE FILES. Until 2026-09-05
    # this file's basis table was a private dict and nothing checked it: a
    # net could be promoted to MEASURED by editing a string. `basis()` is
    # upstream now (P11) and refuses a MEASURED net with no resolvable
    # anchor, and `check()` reads every anchor off disk and compares. The
    # first run of it corrected four nets on this sheet.
    s.evidence_root = REPO
    for name in NETS:
        kind = NETS[name][0]
        a = ANCHORS.get(name) or {}
        s.basis(name, kind, anchor=a.get("anchor"),
                contains=a.get("contains"),
                derived_from=(a.get("derived_from") or
                              (NETS[name][4 - 1] if kind == INFERRED else None)),
                note=NETS[name][3])

    s.unused_gpio = s.nc_unused()
    # NETS.md IS WRITTEN HERE, INSIDE build(), and not from __main__.
    # It was in __main__ first, and that left an ordering hazard with teeth:
    # `bin/sch all` calls build() and save() itself and never runs __main__,
    # so a rebuild through the normal entry point refreshed the schematic and
    # left NETS.md describing the previous one. x_schematic_check's C4 caught
    # the symptom (an ERC older than the schematic) the first time the two
    # commands were run in the wrong order. Writing it here means there is no
    # order to get wrong.
    s.nets_md = write_nets_md(s, os.path.join(HERE, "NETS.md"))
    return s


SUBSTITUTIONS = [
    ("U1", "nRF52832-CIAA, WLCSP-50 (marking read: N52832 CIAAE0 2102JK)",
     "MCU_Nordic:nRF52832-QFxx",
     "the SAME DIE in QFN-48. No CIAA ball map is sourced anywhere in this "
     "repository, and inventing 50 ball designators is what D9 forbids. The "
     "netlist is right by signal; the pin numbers are QFAA's"),
    ("U2", "Apple U1 UWB SiP (die TMKA75, USI package)",
     "local:APPLE_U1_SIP_PLACEHOLDER",
     "no pinout has EVER been published for this module, and the part is not "
     "sold. Pin numbers are this sheet's own and are not a land pattern"),
    ("U3", "GD25LQ32C, WLCSP-10 (ten pads, centre pads absent)",
     "Memory_Flash:GD25QxxxEY",
     "KiCad ships no WLCSP-10 NOR symbol. The WSON-8 symbol carries the same "
     "eight signals under different numbers"),
    ("U4", "the accelerometer, part unidentified, metal-lid LGA",
     "local:ACCEL_3AXIS_GENERIC",
     "the part is CANNOT DETERMINE, so a named symbol would assert an "
     "identification this project could not make. The pin set is the "
     "intersection BMA280/LIS2DH/LIS2DW12/SC7A20 all share"),
    ("U5", "MAX98357A/B, WLCSP", "Audio:MAX98357A",
     "KiCad's symbol is the TQFP-16 pinout. Signals travel; pin numbers do "
     "not. The suffix itself is disputed between sources"),
    ("U6", "TPS62746-class buck, package CANNOT DETERMINE",
     "local:BUCK_TPS62746_CLASS",
     "the evidence is a board LEGEND ('98C0051 / TPS746'), not a package "
     "marking. A named symbol would over-claim"),
    ("U8", "FPF2487-class load switch", "local:LOADSWITCH_FPF2487_CLASS",
     "single-source (iFixit), LOW confidence, uncorroborated by any "
     "photograph here"),
    ("U9", "the part marked 1A8 / 1950", "local:UNKNOWN_REGULATOR_1A8_1950",
     "CANNOT DETERMINE, including whether 'regulator' is its function. Every "
     "pin name on that symbol ends in a question mark for that reason"),
    ("X1/X2", "two seam-sealed ceramic crystals, sizes unmeasured",
     "Device:Crystal + Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm",
     "the markings T320/RBEV and A048L were read; the manufacturers, part "
     "numbers, load capacitances and CASE SIZES were not"),
    ("BT1", "three sprung metal battery contacts", "local:BATT_CONTACTS_3",
     "a connector-less battery interface has no catalogue land pattern, and "
     "the two positive fingers must be two separate nets in copper"),
    ("LS1", "a voice coil glued to the housing dome", "Device:Speaker",
     "there is no speaker. There is a coil against a fixed magnet and the "
     "HOUSING IS THE DIAPHRAGM"),
    ("ANT1/ANT2/ANT3", "structures printed or wound on the plastic carrier",
     "Device:Antenna / Device:Antenna_Loop",
     "not bought parts and not PCB copper - the symbols are terminals so the "
     "networks have somewhere to end"),
]

DISCARDED = [
    "iFixit's 'GD25LE32D' for the flash - DISCARDED for O'Flynn's "
    "GD25LQ32C, which came from a Segger J-Flash SPI interrogation of the "
    "LIVE CHIP. A JEDEC ID read out of silicon outranks a visual "
    "identification, every time.",
    "iFixit's 'U8 gates U1 + flash' (U1 = the MCU) - DISCARDED for U8 "
    "gating the flash and the UWB module only. A load switch whose enable "
    "comes from the MCU it powers can never be turned on. iFixit's line is "
    "single-source and bom.json grades U8 LOW / SILICON CITED.",
    "D1/D2 as 'schottky pairs' (RESEARCH-A, from the K11 marking) - "
    "DISCARDED and the parts left OFF the sheet. bom.json: CANNOT DETERMINE "
    "for the part AND the function.",
    "CT1 as a tantalum capacitor (RESEARCH-A, 'a blue tantalum / 6X A75 "
    "cap') - DISCARDED and left off. 'Blue body' is a colour, not a "
    "technology, and bom.json cannot establish that it is a capacitor at all.",
    "UNK-A and UNK-B - left off. Seen, unmarked, unidentified. UNK-B's "
    "position between U2 and J1 is 'consistent with' an RF switch and "
    "position is not evidence of function.",
    "TP1/TP38 as the voice coil's joints (REFERENCE-TEARDOWN 2.4) - "
    "DISCARDED as unresolved, not as wrong: Apple's own FCC arrow labels "
    "that annulus the NFC antenna. Both cannot be true, so neither is drawn.",
    "The E02 turn-count corroboration for ANT2 - already withdrawn by its "
    "own author on 2026-09-05, because a solenoid and a flat spiral present "
    "the same radial band width from above, so the 'two agreeing "
    "measurements' were one measurement twice. Only the >=9-turn lower bound "
    "and the direct observation of resolved coplanar conductors survive.",
    "Filling any capacitor or resistor value with a plausible number - "
    "refused throughout. A 100 nF and a 1 uF 0402 are visually identical, "
    "so every value here is CANNOT DETERMINE and stays that way.",
]

CANNOT_DETERMINE = [
    "APPLE'S ACTUAL NETLIST. Nobody has traced the copper. This whole sheet "
    "is a reconstruction from function and the basis field on every net says "
    "which kind.",
    "Every GPIO assignment on U1 except the four SWD pads. nRF52832 routes "
    "most peripherals by PSEL, so the assignments are free and therefore "
    "unverified against anything Apple did.",
    "Every passive value. See DISCARDED.",
    "Whether the nRF52832's internal DC/DC is enabled at all. If it is not, "
    "L2 does not exist.",
    "The DEC2/DEC3 arrangement - no copy of the nRF52832 reference circuit "
    "is in this repository, so only the topology is drawn.",
    "U4's part, U4's bus (I2C vs SPI), and which of the two metal-lid parts "
    "it even is.",
    "U9's part number AND U9's function AND what its output feeds.",
    "U7's role. Drawn as a unity buffer from a divider on SPK_P; could "
    "equally be a current-sense amp, a filter or a bias buffer.",
    "Whether J1 and ANT3 are one net. UNK-B sits between them and may be a "
    "switch.",
    "Which annulus TP1/TP38 belong to - NFC coil or voice coil. Two sources "
    "contradict and one of them is Apple.",
    "The crystals' frequencies (Catley's assignment, untested), their load "
    "capacitances, their part numbers and their case sizes.",
    "The five bulk capacitors' technology and their actual capacitance - "
    "'100 uF' is MEDIUM and the marking J107S is what is HIGH.",
    "The forward drop D3 costs, because the diode has not been chosen; D24 "
    "requires both a Schottky and an ideal-diode controller to be priced.",
]


def write_nets_md(s, path):
    """NETS.md, generated from the same N() calls that made the netlist.

    A net table written by hand beside a netlist is a net table that is
    wrong within a week, and this project is named after that failure.
    """
    described = set(NETS)
    actual = set(s.nets)
    missing = sorted(actual - described)
    extra = sorted(described - actual)

    counts = {}
    for basis, _d, _l, _w in NETS.values():
        counts[basis] = counts.get(basis, 0) + 1

    out = []
    w = out.append
    w("# NETS.md — every net on the halo Replica schematic, and what it rests on")
    w("")
    w("**GENERATED FILE.** Written by `schematic/schematic.py`, from the same")
    w("`N()` calls that build the netlist. Do not edit it by hand; edit the")
    w("schematic and rebuild, or the two will disagree and the netlist wins.")
    w("")
    w("## The one thing to read first")
    w("")
    w("**Nobody in this project has traced Apple's copper.** Not one net below")
    w("was read off a board. The parts come from `bom/bom.json` — photographs")
    w("and package markings — and the *connections* are reconstructed from what")
    w("each part is for. The `basis` column is not decoration; it is the whole")
    w("epistemic content of this document.")
    w("")
    w("| basis | meaning |")
    w("|---|---|")
    w("| `MEASURED` | read off the hardware by a named source in this repo |")
    w("| `INFERRED` | required by the part's own datasheet family once the "
      "part is accepted. Wrong only if the part identification is wrong |")
    w("| `CHOSEN` | this sheet picked it. Apple's assignment is unknown and a "
      "different one would be equally consistent with every photograph. "
      "**Never cite one of these as a finding about Apple.** |")
    w("")
    meas = sorted(n for n in NETS if NETS[n][0] == MEASURED)
    w("Counts: " + ", ".join("**%d %s**" % (counts.get(b, 0), b)
                             for b in (MEASURED, INFERRED, CHOSEN))
      + ".  **%d of %d nets are MEASURED**, and they are the only ones: "
        "%s. Every one of those carries an ANCHOR — a file and a string that "
        "must be in it — which `cepcb.schematic.basis()` OPENS AND CHECKS at "
        "build time, so none of them can be reached by editing a label. "
        "Everything else on this board is reconstruction."
      % (len(meas), len(NETS), ", ".join("`%s`" % m for m in meas)))
    w("")
    w("## The nets")
    w("")
    w("| net | basis | driven by | feeds | why it is drawn this way |")
    w("|---|---|---|---|---|")
    for name in sorted(NETS):
        basis, driver, loads, why = NETS[name]
        n = len(s.nets.get(name, []))
        w("| `%s` (%d pins) | **%s** | %s | %s | %s |"
          % (name, n, basis, driver, loads, why.replace("\n", " ")))
    w("")
    w("## Consistency with the netlist itself")
    w("")
    if missing:
        w("**%d net(s) exist in the netlist and are NOT described above.** "
          "That is a defect in this file, not in the schematic:" % len(missing))
        for m in missing:
            w("  - `%s`" % m)
    else:
        w("Every net in the netlist is described above.")
    w("")
    if extra:
        w("**%d net(s) are described above and are NOT in the netlist:**"
          % len(extra))
        for e in extra:
            w("  - `%s`" % e)
    else:
        w("Every net described above is in the netlist.")
    w("")
    w("## What was discarded, and why")
    w("")
    for line in DISCARDED:
        w("- " + line)
    w("")
    w("## CANNOT DETERMINE, carried openly")
    w("")
    for line in CANNOT_DETERMINE:
        w("- " + line)
    w("")
    w("## Symbol substitutions")
    w("")
    w("| ref | what the AirTag has | what this sheet draws | why |")
    w("|---|---|---|---|")
    for ref, wanted, used, why in SUBSTITUTIONS:
        w("| %s | %s | `%s` | %s |" % (ref, wanted, used, why))
    w("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    return path, missing, extra


if __name__ == "__main__":
    s = build()

    problems = s.check()
    for sev, msg in problems:
        print("%-17s %s" % (sev, msg))

    unused = s.unused_gpio
    print("\n--- deliberately not connected (%d pins) ---" % len(unused))
    for key, name in unused:
        print("  %-10s %s" % (key, name))

    s.place()
    print("\n" + s.describe())
    print(s.describe_bases())
    out = s.save(os.path.join(REPLICA, "out", "schematic",
                              s.name + ".kicad_sch"))
    print("\nwrote", out)

    nets_md, missing, extra = s.nets_md
    print("wrote", nets_md)
    if missing or extra:
        print("NETS.md is INCOMPLETE: %d undescribed, %d stale"
              % (len(missing), len(extra)))

    print("\n--- symbol substitutions ---")
    for ref, wanted, used, why in SUBSTITUTIONS:
        print("  %-11s %-46s -> %s\n              %s" % (ref, wanted, used, why))

    print("\n--- DISCARDED, and why ---")
    for line in DISCARDED:
        print("  " + line)

    print("\n--- CANNOT DETERMINE, carried openly ---")
    for line in CANNOT_DETERMINE:
        print("  " + line)
