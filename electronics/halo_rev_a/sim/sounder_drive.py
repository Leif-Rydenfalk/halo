"""halo rev A's sounder: a piezo bender across two GPIO, driven anti-phase.

    cd ~/dev/ce-workshop
    ce-spice/bin/spice run \
        ce-designs/halo/electronics/halo_rev_a/sim/sounder_drive.py \
        --out ce-designs/halo/out/release/board/sim/sounder_drive

WHAT DECISION THIS IS TESTING. DECISIONS.md D11a deletes the class-D
amplifier every AirTag clone carries and drives a bare Murata 7BB-20-3
bender straight from two SoC pins in anti-phase. research/05 §11.6 argues
that on the arithmetic this costs nothing:

    "The MAX98357A is a bridge-tied class-D output, so it swings +/-Vbat,
     about 6 V peak-to-peak from a 3 V cell. Two SoC pins driven anti-phase
     swing THE SAME 6 V peak-to-peak. What the amplifier would have bought
     is current, and a bender is a capacitive load: at 20-30 nF and 4 kHz,
     I = 2*pi*f*C*V gives 1.5-2.3 mA peak, which nRF54L GPIO in high-drive
     mode can source."

That paragraph ends by calling itself "derived arithmetic from the datasheet
capacitance class, not a measurement". THIS FILE IS THE MEASUREMENT of the
electrical half. It cannot measure loudness - no circuit simulator can - and
D11a already says the acoustic verdict comes off a calibrated meter.

The three questions it does answer, none of which the arithmetic does:

  1. WHAT THE PIN ACTUALLY SEES. The arithmetic uses the average sinusoidal
     current. A GPIO drives SQUARE waves, and a square edge into a capacitor
     is a current spike set by the driver's own output resistance, not by
     2*pi*f*C*V. That peak is what a pin either survives or does not.
  2. WHAT THE RAIL DOES. The bender runs off the same 40 uF and the same
     coin cell as the radio, for a DULT alert that lasts seconds rather than
     the radio's one millisecond. rail_droop.py measured a 1 ms pulse; this
     measures a continuous 4 kHz load at end of life.
  3. WHAT R9 IS WORTH. The schematic puts 100 R in series with one leg, on
     the argument that it holds the edge current down at a cost of about
     0.2 dB. Both halves of that are checked here, against a control with
     R9 replaced by a link.

---------------------------------------------------------------------------
THE BENDER MODEL, AND THE FACT THAT ITS DATASHEET WAS NEVER FETCHED
---------------------------------------------------------------------------
A piezo bender below resonance is a capacitor with a small series loss; at
resonance it is a series RLC in parallel with that capacitance (the
Butterworth-Van Dyke model). The parameters here are NOT from Murata's
7BB-20-3 datasheet, because research/05 §11.7 records that the part is not
in the LCSC or JLCPCB catalogues, Digi-Key answers 403 and Mouser a captcha,
and the factory lane has since confirmed CANNOT DETERMINE at every quantity.
ce-designs/halo/design.py carries "3.6 kHz free resonance, 500 ohm" for it
from lane G.

So this study does NOT claim the 7BB-20-3's own numbers. It runs a RANGE
that brackets any Ø20 mm bender of that class, and says so:

    Cp   15 / 25 / 40 nF     the free capacitance
    Rs   500 ohm             lane G's figure, via design.py

and the asserts are written so that a PASS means "any bender in this range
is safe to drive this way", which is the claim D11a actually needs. If the
real part comes in outside the range, this file is re-run with its numbers
and the range is deleted.
"""
from cespice import Circuit

F_DRIVE = 4000.0          # the drive frequency, near a Ø20 bender's resonance
PERIODS = 8
STOP_S = PERIODS / F_DRIVE
MEAS_LO = 4 / F_DRIVE     # measure after four periods, once settled

VDD = 2.0                 # end-of-life cell: the hardest case to drive from
ESR = 60.0                # TI SWRA349 section 3, end of life
BULK_F = 40e-6            # C9-C12
R_SERIES = 100.0          # R9
R_DRV = 40.0              # nRF54L GPIO high-drive output resistance

CAPS = [(15e-9, "the low end of a Ø20 mm bender's free capacitance"),
        (25e-9, "mid-range, and the middle of research/05 §11.6's own "
                "20-30 nF bracket"),
        (40e-9, "the high end — the worst case for peak current, because "
                "the edge current scales with C")]


#: The bender's series loss, and it turns out to DECIDE this study.
#: 500 ohm is lane G's figure via design.py, read here as a series loss
#: resistance. That reading is questionable and the alternative is run too:
#: a piezo's dielectric loss is usually tan(delta) ~ 0.02, which at 4 kHz and
#: 25 nF is Rs = tan(delta)/(w C) = 32 ohm, sixteen times smaller. Which one
#: is right changes the peak pin current by more than a factor of two and
#: decides whether R9 is load-bearing or decoration, so BOTH are measured.
LOSSES = [
    (500.0, "lane G's 500 ohm, carried in design.py, read as a series loss "
            "resistance. NOTE THIS READING IS UNCERTAIN: |Z| of 25 nF at "
            "4 kHz is 1592 ohm, so 500 ohm may instead be the motional "
            "resistance AT resonance, which is a different element."),
    (32.0, "derived instead from a typical piezo dielectric tan(delta) of "
           "0.02: Rs = tan(delta) / (2 pi f C) = 32 ohm at 4 kHz and 25 nF. "
           "This is the LOW-LOSS case and it is the one that stresses the "
           "pin, so it is the one the drive has to survive."),
]


def _sounder(cp, why, r_series=R_SERIES, name=None, rs=500.0, rs_why=""):
    c = Circuit(name or "sounder_%dnf" % round(cp * 1e9),
                "halo rev A sounder: %.0f nF bender, %s, anti-phase from two "
                "GPIO at %.1f kHz, 2.0 V cell at 60 ohm"
                % (cp * 1e9, ("%.0f R series" % r_series) if r_series
                   else "NO series resistor", F_DRIVE / 1e3),
                why=why)

    c.const("cp_F", cp, "F", why)
    c.const("f_res_est_Hz", 3600.0, "Hz",
            "design.py, lane G: the 7BB-20-3's free resonance is 3.6 kHz. "
            "The drive is run at 4.0 kHz, near but not on it.")
    c.const("rs_ohm", rs, "ohm", rs_why or
            "the bender's series loss. THE DATASHEET WAS NEVER FETCHED - "
            "research/05 §11.7 records the part is in no catalogue that "
            "answers a machine.")
    c.const("r_drive_ohm", R_DRV, "ohm",
            "nRF54L GPIO output resistance in HIGH DRIVE. Nordic's standard "
            "drive is nearer 100 ohm; the high-drive figure is taken as "
            "40 ohm. NOT FETCHED FROM THE DATASHEET - it is an estimate, and "
            "the peak current below is inversely proportional to it, so this "
            "is the largest uncertainty in this study.")
    c.const("vdd_V", VDD, "V",
            "end-of-life cell OCV — TI SWRA349's stated threshold. Driving "
            "from the WORST rail, not the nominal one.")
    c.const("f_drive_Hz", F_DRIVE, "Hz",
            "near the Ø20 bender's free resonance, design.py: 3.6 kHz. The "
            "drive is a square wave because a GPIO has no other shape.")
    if r_series:
        c.const("r9_ohm", r_series, "ohm",
                "R9 on the schematic: series damping on one leg, so a GPIO "
                "edge into a capacitive load is not an unlimited current "
                "spike off the bulk capacitors")

    # The supply the sounder actually runs from — the same cell and the same
    # bulk the radio uses, because there is no second rail on this board.
    c.V("cell", "vcell", "0", dc=VDD)
    c.R("esr", "vcell", "vbat", ESR)
    c.C("bulk", "vbat", "0", BULK_F)

    # Two GPIO in anti-phase. Each is modelled as a square voltage source
    # behind the pin's own output resistance — which is what a CMOS driver
    # is, and it is the part the 2*pi*f*C*V arithmetic leaves out.
    c.note("PULSE(V1 V2 TD TR TF PW PER) on each pin, the second delayed by "
           "half a period, is anti-phase: when P1.11 is at VDD, P1.12 is at "
           "0, so the bender sees +VDD, and half a cycle later -VDD. That is "
           "2 x VDD peak to peak from a single rail and it is the whole "
           "reason D11a needs no boost converter.")
    half = 1.0 / (2.0 * F_DRIVE)
    edge = 1e-6
    c.V("p", "drv_p", "0",
        pulse=(0.0, VDD, 0.0, edge, edge, half - edge, 1.0 / F_DRIVE))
    c.V("n", "drv_n", "0",
        pulse=(VDD, 0.0, 0.0, edge, edge, half - edge, 1.0 / F_DRIVE))
    c.R("drvp", "drv_p", "pin_p", R_DRV)
    c.R("drvn", "drv_n", "pin_n", R_DRV)

    if r_series:
        c.R("r9", "pin_p", "bend_p", r_series)
    else:
        c.R("r9", "pin_p", "bend_p", 1e-3)
    # The bender: free capacitance with its series loss. Below and around
    # resonance this is the branch that carries the current.
    c.C("bend", "bend_p", "bend_r", cp)
    c.R("bendloss", "bend_r", "pin_n", rs)

    # THE VOLTAGE ACROSS THE BENDER, not the voltage at one end of it. The
    # first version measured pp_of('bend_p'), which is bend_p to GROUND, and
    # reported 2.0 V where the differential swing is 4.0 V - it graded the
    # wrong quantity and FAILED an assert that was actually satisfied. A
    # behavioural source makes the difference a node the measurement can see.
    c.raw("Bdiff vdiff 0 V = V(bend_p) - V(pin_n)")

    c.tran(1.0 / (F_DRIVE * 400.0), STOP_S,
           maxstep=1.0 / (F_DRIVE * 400.0))

    c.measure("v_bender_pp_V", "pp_of('vdiff', %g, %g)" % (MEAS_LO, STOP_S),
              "V", why="the swing ACROSS the bender. D11a's whole claim is "
                       "that two anti-phase pins give the same 2 x VDD a "
                       "bridge-tied amplifier would.")
    c.measure("i_peak_mA",
              "absmax_of('i(vp)', %g, %g) * 1e3" % (MEAS_LO, STOP_S), "mA",
              why="the PEAK current one pin sources — the edge spike, not "
                  "the sinusoidal average research/05 §11.6 computes")
    c.measure("i_rms_mA",
              "rms_of('i(vp)', %g, %g) * 1e3" % (MEAS_LO, STOP_S), "mA",
              why="the RMS current, which is what the cell and the bulk "
                  "actually have to supply for the length of an alert")
    c.measure("v_rail_min_V", "min_of('vbat', %g, %g)" % (MEAS_LO, STOP_S),
              "V", why="the rail while the sounder runs. A DULT alert lasts "
                       "seconds; the radio's droop lasted a millisecond.")
    c.measure("rail_droop_mV",
              "(%g - min_of('vbat', %g, %g)) * 1e3" % (VDD, MEAS_LO, STOP_S),
              "mV", why="how far the rail falls while sounding")
    return c


def build():
    circuits = []
    for rs, rs_why in LOSSES:
        for cp, why in CAPS:
            c = _sounder(cp, why, rs=rs, rs_why=rs_why,
                         name="sounder_%dnf_rs%d" % (round(cp * 1e9), rs))
            c.assert_("v_bender_pp_V", ">", 1.5 * VDD,
                      why="D11a's claim is 2 x VDD peak to peak, the same "
                          "swing a bridge-tied class-D gives. 1.5 x VDD is "
                          "that with room for the drive and series "
                          "resistance; below it the anti-phase trick is not "
                          "working and the amplifier was not free to delete.")
            c.assert_("i_peak_mA", "<", 25.0,
                      why="an nRF54L GPIO in high drive is specified in the "
                          "single-digit to low-tens of mA. 25 mA is the "
                          "ceiling this study will call safe without the "
                          "datasheet figure in hand.")
            c.assert_("v_rail_min_V", ">", 1.7,
                      why="the SoC has to stay alive while it is making a "
                          "noise. Below 1.7 V it browns out mid-alert, which "
                          "is the one moment DULT requires it to be audible.")
            c.plot("bender voltage and the two pins - %.0f nF, %.0f ohm loss"
                   % (cp * 1e9, rs),
                   ["v(vdiff)", "v(pin_p)", "v(pin_n)"], "volts")
            c.plot("pin current - the edge spike the arithmetic omits",
                   ["i(vp)"], "amps")
            circuits.append(c)

    # THE CONTROL FOR R9, and it is run in the LOW-LOSS case because that is
    # the only one where R9 could matter. With the bender modelled at 500 ohm
    # its own loss already limits the edge and R9 changes 6.72 mA to 5.72 mA
    # - a 15 % trim, which does NOT justify a BOM line. At 32 ohm the pin
    # sees the capacitor almost directly and R9 is the only thing between a
    # GPIO and a 2 V step into 40 nF.
    bare = _sounder(40e-9,
                    "the worst-case bender with R9 replaced by a link, in "
                    "the low-loss model - the control that says whether R9 "
                    "earns its place",
                    r_series=0.0, name="sounder_40nf_rs32_no_r9",
                    rs=32.0, rs_why=LOSSES[1][1])
    bare.assert_("i_peak_mA", ">", 20.0,
                 why="THIS ONE IS MEANT TO BE HIGH. In the low-loss model "
                     "the edge is limited by the pin's own 40 ohm and the "
                     "bender's 32 ohm, so the spike approaches VDD/72 = "
                     "28 mA. A PASS here is the evidence that R9 is doing a "
                     "job; the fitted 40 nF / 32 ohm case above shows what "
                     "it reduces that spike to.")
    bare.plot("pin current with NO series resistor, low-loss bender",
              ["i(vp)"], "amps")
    circuits.append(bare)
    return circuits


CANNOT_DETERMINE = [
    "THE BENDER'S OWN PARAMETERS. The Murata 7BB-20-3 datasheet was never "
    "fetched - the part is in no catalogue that answers a machine "
    "(research/05 §11.7, confirmed by the factory lane at every quantity). "
    "This study brackets 15-40 nF instead of using its number, and the "
    "500 ohm loss is lane G's figure carried through design.py.",
    "THE GPIO's OUTPUT RESISTANCE. 40 ohm in high drive is an ESTIMATE, not "
    "a datasheet figure. Peak current is inversely proportional to it, so "
    "it is the largest single uncertainty here. Fetch the nRF54L10 GPIO DC "
    "characteristics table and re-run.",
    "LOUDNESS. No circuit simulator measures sound pressure. D11a is "
    "explicit that 60 Phon at 25 cm is settled by a calibrated meter "
    "against a bonded bender in a real shell, and VERIFICATION-DEBT V7 "
    "carries it as unproven and load-bearing.",
    "THE RESONANT BRANCH. A bender at resonance is a series RLC in parallel "
    "with the free capacitance (Butterworth-Van Dyke); only the free "
    "capacitance is modelled here, so the current at exactly 3.6 kHz will be "
    "HIGHER than these figures on a real part.",
]
