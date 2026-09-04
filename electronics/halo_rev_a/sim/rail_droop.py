"""halo rev A's OWN rail, under the nRF54L10's OWN transmit pulse.

    cd ~/dev/ce-workshop
    ce-spice/bin/spice run ce-designs/halo/electronics/halo_rev_a/sim/rail_droop.py \
        --out ce-designs/halo/out/release/board/sim/rail_droop

WHY THIS EXISTS WHEN ce-spice ALREADY SHIPS `cr2032_pulse_load`. Leif asked
for our board simulated, not an example. The shipped example is a good model
and it is a model of a DIFFERENT BOARD: it draws 8 mA from an nRF52832 behind
100 uF of reservoir. halo rev A is an nRF54L10 behind 4 x 10 uF, and BOTH
numbers moved in the direction that matters:

    load       8.0 mA  ->  3.7 mA    nRF54L10 datasheet Table 86, ITX,0dBm
    reservoir   100 uF ->  40 uF     4 x 10 uF 0402, because 0805 does not fit
    sleep       2.0 uA ->  2.4 uA    Table 86 ION_IDLE4, 192 kB retained

The transmit current more than halved and the reservoir fell to 40 %. Those
pull the droop in opposite directions, so which wins is a question with a
number as its answer, and this file is how that number is obtained rather
than assumed.

WHAT THIS FILE ADDS THAT THE EXAMPLE DOES NOT MODEL AT ALL: the five-removals
factory reset. SPEC.md §3 records that the AirTag's five 100 uF capacitors
are "what keeps the tag alive for seconds after the cell is pulled, which is
how the five-removals reset works". D-5 in our schematic implements the
detection - the second positive contact is sense-only, so the sense node
collapses while the rail is still held up - but detection is worthless if the
rail does not actually outlive the removal. `holdup` below measures how long
40 uF keeps an nRF54L10 above its minimum with the cell gone.

---------------------------------------------------------------------------
THE MODEL, AND WHAT IT IS NOT
---------------------------------------------------------------------------
    Vcell --[Resr]--+-- vbat --+-- Cbulk 40 uF (4 x 10 uF 0402)
                    |          +-- Iload (sleep / TX pulse)
                  (removed in the holdup case)

The ESR ladder is NOT a depth-of-discharge curve. It is the same set of cited
resistances the shipped example uses, for the same reason: no datasheet this
workshop can reach states CR2032 ESR against depth of discharge as NUMBERS,
only as pictures, and digitising a picture is inventing data with extra
steps. Each point below names the sentence it comes from.

NOT MODELLED, and therefore not claimed: the SoC's internal DC/DC (which
makes the real load current vary with rail voltage instead of being the flat
source used here - a conservative simplification, because a buck draws MORE
current as the rail sags), the 0402 capacitors' DC bias derating (a 10 uF
X5R 6.3V part at 3 V retains materially less than 10 uF, and that is a real
and unquantified error in the optimistic direction - see the CANNOT
DETERMINE at the end), temperature, and the board's own copper resistance.
"""
from cespice import Circuit

# --------------------------------------------------------------- the profile
PERIOD_S = 2.0            # SPEC.md F2 / DULT: advertising interval
TX_S = 1e-3
SETTLE_S = 0.1
STOP_S = 4.2
MEAS_LO, MEAS_HI = 2.1, 4.1

BULK_F = 40e-6            # 4 x 10 uF 0402, schematic C9-C12
I_TX = 3.7e-3             # nRF54L10 datasheet Table 86, ITX,0dBm
I_SLEEP = 2.4e-6          # Table 86, ION_IDLE4 (192 kB retained = L10's RAM)
VDD_MIN = 1.7             # nRF54L operating range low limit
FLOOR = 1.8               # VDD_MIN + 100 mV of margin

POINTS = [
    ("fresh", 3.0, 30.3,
     "nominal 3.0 V (Energizer Form 2032NA0618, Specifications) with the "
     "only pulse impedance derivable from stated numbers, 30.3 ohm"),
    ("pulse-point", 2.9, 30.3,
     "Energizer's own pulse-test row: 2.9 V at 0.19 mA background and 2.7 V "
     "at the 6.8 mA pulse, so dV/dI = 0.2 V / 6.61 mA = 30.3 ohm"),
    ("end-of-life", 2.0, 60.0,
     "TI SWRA349 section 3: 'the IR limit for 15mA peak is approximately "
     "60ohm', at TI's own stated end of life, 'battery voltage below 2.0V'"),
    ("worst-case", 2.0, 140.0,
     "the top of the IR axis on Energizer Form 2032NA0618's pulse chart, the "
     "highest internal resistance that datasheet's own figure admits"),
]


def _consts(c):
    c.const("i_tx_A", I_TX, "A",
            "nRF54L10 datasheet (Nordic 4503_018 v0.10) Table 86, "
            "ITX,0dBm = 3.7 mA, radio-only TX current at 0 dBm. Transcribed "
            "in ce-designs/halo/research/fetched/"
            "E-nrf54l-datasheet-currents.md. NOT the 4.8 mA on Nordic's "
            "product page, which is a whole-device figure.")
    c.const("i_sleep_A", I_SLEEP, "A",
            "Table 86, ION_IDLE4 = 2.4 uA, System ON with 192 kB of RAM "
            "retained, which is the nRF54L10's whole RAM. research/05 §11.2 "
            "notes Nordic publishes no 192 kB + GRTC + LFXO row, so the "
            "advertising sleep state is bracketed by 2.0 and 3.1 uA and this "
            "uses the retention figure alone.")
    c.const("bulk_F", BULK_F, "F",
            "4 x 10 uF 0402 X5R 6.3V (C9-C12). NOT Apple's five 100 uF: D12 "
            "deleted the U1 and D11a deleted the class-D amplifier, which "
            "were two of the three loads that needed 500 uF, and an 0805 is "
            "1.25 mm tall against a 0.578 mm bottom-face allowance.")
    c.const("capacity_mAh", 235.0, "mAh",
            "Energizer CR2032 Form No. 2032NA0618, Specifications: 'Typical "
            "Capacity 235 mAh (to 2.0 volts), Rated at 15K ohms at 21C'")
    c.const("nrf54l_vdd_min_V", VDD_MIN, "V",
            "nRF54L operating supply range low limit, 1.7 V")
    c.const("floor_V", FLOOR, "V",
            "the assert floor: nrf54l_vdd_min_V plus 100 mV of margin")


def _cell(name, ocv, esr, why, bulk_F=BULK_F):
    c = Circuit("rail_droop_" + name.replace("-", "_"),
                "halo rev A rail: CR2032 at %.1f V / %.0f ohm, %s, "
                "nRF54L10 3.7 mA TX pulse"
                % (ocv, esr, ("%.0f uF bulk" % (bulk_F * 1e6)) if bulk_F
                   else "NO bulk"),
                why=why)
    _consts(c)
    v_ocv = c.const("ocv_V", ocv, "V",
                    "Energizer Form 2032NA0618 Specifications / TI SWRA349's "
                    "stated end-of-life threshold — see the point's own why")
    r_esr = c.const("esr_ohm", esr, "ohm", why)

    c.note("PULSE(I1 I2 TD TR TF PW PER) — ngspice puts a breakpoint on every "
           "corner of a PULSE source, so the end-of-pulse instant, where the "
           "droop is deepest, is sampled exactly and not interpolated.")
    c.V("cell", "vcell", "0", dc=v_ocv)
    c.R("esr", "vcell", "vbat", r_esr)
    if bulk_F:
        c.C("bulk", "vbat", "0", bulk_F)
    c.I("load", "vbat", "0",
        pulse=(I_SLEEP, I_TX, SETTLE_S, 1e-6, 1e-6, TX_S, PERIOD_S))
    c.tran(1e-4, STOP_S, maxstep=1e-4)

    c.measure("v_rest_V", "at_of('vbat', %g)" % (MEAS_LO - 1e-3), "V",
              why="the rail at rest, one ms before the transmission starts")
    c.measure("v_min_V", "min_of('vbat', %g, %g)" % (MEAS_LO, MEAS_LO + 0.02),
              "V", why="the deepest point of the droop, at the end of the "
                       "1 ms transmit slot")
    c.measure("droop_mV",
              "(at_of('vbat', %g) - min_of('vbat', %g, %g)) * 1e3"
              % (MEAS_LO - 1e-3, MEAS_LO, MEAS_LO + 0.02), "mV",
              why="how far the rail falls during one transmission")
    c.measure("i_peak_mA",
              "absmax_of('i(vcell)', %g, %g) * 1e3" % (MEAS_LO, MEAS_HI),
              "mA", why="peak current the CELL delivers. The bulk supplies "
                        "the rest of the 3.7 mA, which is what it is for")
    c.measure("i_avg_uA",
              "absmean_of('i(vcell)', %g, %g) * 1e6" % (MEAS_LO, MEAS_HI),
              "uA", why="time-weighted average cell current over one full "
                        "2 s period; battery life divides into this")
    c.measure("life_months",
              "capacity_mAh / (absmean_of('i(vcell)', %g, %g) * 1e3) / 730.5"
              % (MEAS_LO, MEAS_HI), "months",
              why="capacity_mAh / average mA / 730.5 h per month. IDEAL: it "
                  "spends every stated mAh and models no self-discharge, no "
                  "temperature and no capacity lost to pulsing")
    c.measure("life_months_derated",
              "capacity_mAh * 0.91 * (1 - 0.01 * (capacity_mAh / "
              "(absmean_of('i(vcell)', %g, %g) * 1e3) / 8766.0)) "
              "/ (absmean_of('i(vcell)', %g, %g) * 1e3) / 730.5"
              % (MEAS_LO, MEAS_HI, MEAS_LO, MEAS_HI), "months",
              why="the same figure with the two derations that can be cited: "
                  "TI SWRA349 Figure 3, 9 % average capacity loss for pulsed "
                  "draw, and Energizer's ~1 %/year self-discharge")
    return c


def _holdup(ocv, esr):
    """THE FIVE-REMOVALS CASE. The cell is pulled; how long does the rail live?

    Modelled as the cell's ESR rising to 1 Gohm at t = 0.5 s, which is what
    an open contact is. Everything after that instant is the bulk capacitance
    discharging into the sleep current, and the question is whether the SoC
    stays above its minimum long enough to notice, count and store the
    removal. D-5's sense divider collapses in about 0.24 ms; anything much
    longer than that here is enough.
    """
    c = Circuit("rail_droop_holdup",
                "halo rev A: the cell is REMOVED at t = 0.5 s and the 40 uF "
                "bulk holds the rail up",
                why="SPEC.md §3: the bulk capacitance is 'what keeps the tag "
                    "alive for seconds after the cell is pulled, which is how "
                    "the five-removals reset works'. Apple has 500 uF for it; "
                    "rev A has 40 uF and this measures what that buys.")
    _consts(c)
    c.const("ocv_V", ocv, "V", "end-of-life cell, the hardest case to hold up "
                               "from because it starts lowest")
    c.const("esr_ohm", esr, "ohm", "TI SWRA349 section 3, end of life")
    c.note("The removal is a PWL resistance: 60 ohm until t = 0.5 s, then "
           "1 Gohm. A behavioural resistor is used rather than a switch so "
           "there is no discontinuity for the integrator to trip over.")
    c.V("cell", "vcell", "0", dc=ocv)
    c.note("The removal is a voltage-controlled switch: Ron IS the cell's "
           "end-of-life ESR, Roff is an open contact, and the control source "
           "opens it at t = 0.5 s.")
    c.raw("SW1 vcell vbat sw_ctl 0 removal_sw")
    c.raw(".model removal_sw SW(Ron=%g Roff=1e9 Vt=0.5 Vh=0.01)" % esr)
    c.raw("Vctl sw_ctl 0 PWL(0 1 0.4999 1 0.5 0)")
    c.C("bulk", "vbat", "0", BULK_F)
    c.I("load", "vbat", "0", dc=I_SLEEP)
    c.tran(1e-4, 30.0, maxstep=1e-2)

    c.measure("v_before_V", "at_of('vbat', 0.45)", "V",
              why="the rail with the cell still in")
    c.measure("v_at_1s_V", "at_of('vbat', 1.5)", "V",
              why="one second after the cell leaves")
    c.measure("v_at_10s_V", "at_of('vbat', 10.5)", "V",
              why="ten seconds after the cell leaves")
    c.measure("v_at_30s_V", "at_of('vbat', 29.9)", "V",
              why="thirty seconds after — the end of the run")
    # Exact for a capacitor into a constant current: t = C dV / I. Reported
    # as a number rather than inferred from the plot, because it is the
    # figure the firmware's removal counter has to fit inside.
    c.measure("holdup_to_1v7_s",
              "bulk_F * (at_of('vbat', 0.45) - nrf54l_vdd_min_V) / i_sleep_A",
              "s",
              why="how long the rail stays above the nRF54L's 1.7 V minimum "
                  "after the cell leaves, at sleep current. t = C dV / I, "
                  "exact for a constant-current discharge.")
    c.measure("holdup_apple_500uF_s",
              "500e-6 * (at_of('vbat', 0.45) - nrf54l_vdd_min_V) / i_sleep_A",
              "s",
              why="the same figure with Apple's five 100 uF instead of our "
                  "four 10 uF — the cost of D-4's re-sizing, as a number")
    return c


def build():
    circuits = []
    for name, ocv, esr, why in POINTS:
        c = _cell(name, ocv, esr, why)
        c.assert_("v_min_V", ">", FLOOR,
                  why="below 1.8 V there is under 100 mV to the nRF54L's "
                      "1.7 V minimum; the radio browns out mid-transmission "
                      "and the tag goes silent")
        c.assert_("droop_mV", "<", 400.0,
                  why="a droop this side of 400 mV means the 40 uF bulk, and "
                      "not the cell, is carrying the transmission — which is "
                      "the design intent (TI SWRA349 section 4)")
        c.assert_("i_peak_mA", "<", 3.7,
                  why="the cell must never see the full 3.7 mA edge; if it "
                      "does, the bulk is too small and every pulse is drawn "
                      "through the ESR")
        c.plot("rail voltage over two 2 s periods — %s (%.1f V, %.0f ohm)"
               % (name, ocv, esr), ["v(vbat)", "v(vcell)"], "volts")
        c.plot("the droop, zoomed on one 1 ms transmission", ["v(vbat)"],
               "volts", xlim=(MEAS_LO - 5e-4, MEAS_LO + 5e-3))
        circuits.append(c)

    # THE CONTROL. The same worst case with the bulk removed. It exists to
    # show what 40 uF is buying, and it asserts the collapse it is meant to
    # demonstrate — so it PASSES by failing electrically. A study whose every
    # assert is written to pass has not been tested.
    bare = _cell("worst-case-no-bulk", 2.0, 140.0,
                 "the worst-case cell with the bulk removed — the control "
                 "that shows what C9-C12 are for", bulk_F=0)
    bare.assert_("v_min_V", "<", FLOOR,
                 why="THIS ONE IS MEANT TO COLLAPSE. With no bulk the 3.7 mA "
                     "pulse is drawn straight through 140 ohm, which is "
                     "518 mV of IR drop on a 2.0 V cell. A PASS here is the "
                     "evidence that C9-C12 are load-bearing, not decoration.")
    bare.assert_("i_peak_mA", ">", 3.6,
                 why="with no bulk the cell delivers the whole edge itself — "
                     "the mirror image of the assert the other four make")
    bare.plot("rail voltage — NO bulk: the rail follows the load",
              ["v(vbat)", "v(vcell)"], "volts")
    circuits.append(bare)

    h = _holdup(2.0, 60.0)
    # -------------------------------------------------------------------
    # THE ASSERT THAT WAS HERE FIRST, AND WHY IT WAS REPLACED. This file
    # originally asserted v_at_10s_V > 1.7 and it FAILED at 1.400 V. The
    # right response to that was not to loosen it, and it was also not to
    # keep it: TEN SECONDS CAME FROM NOWHERE. No document in this project
    # requires it, and it was written here as "robust to a user pulling and
    # reseating the cell quickly" — which is a sentence, not a requirement.
    # Asserting an invented threshold and then failing it teaches nothing,
    # and passing one teaches less.
    #
    # The REAL requirement is the one the mechanism has: after the cell
    # leaves, the SoC must wake, read the sense line, increment the removal
    # counter and commit it to non-volatile memory. That budget is
    #     0.24 ms   D-5's sense divider collapsing (4.7M/2 x 100 pF)
    #   + < 1 ms    an ADC sample and a compare
    #   + <= 10 ms  a counter word into RRAM  [NOT SOURCED - see below]
    #   ---------
    #     ~11 ms, and 100 ms is that with an order of magnitude of margin.
    #
    # The measured hold-up is reported either way, and so is what Apple's
    # 500 uF would have bought, so a reader can judge the trade rather than
    # take this file's word for the threshold.
    h.assert_("holdup_to_1v7_s", ">", 0.10,
              why="the firmware must detect the removal, count it and commit "
                  "the count before the rail dies. That budget is about "
                  "11 ms (0.24 ms sense collapse + <1 ms sample + <=10 ms "
                  "NVM write) and 100 ms is it with 10x margin. THE NVM "
                  "WRITE TIME IS NOT SOURCED - Nordic's RRAM write figure "
                  "was not fetched - so the 10 ms is a bounded estimate and "
                  "this assert is only as good as that bound.")
    h.assert_("v_at_1s_V", ">", VDD_MIN,
              why="a full second of life after the cell leaves, which is "
                  "roughly a hundred times the detect-and-commit budget")
    h.plot("the rail after the cell is pulled at t = 0.5 s",
           ["v(vbat)", "v(vcell)"], "volts")
    circuits.append(h)
    return circuits


CANNOT_DETERMINE = [
    "DC BIAS DERATING ON C9-C12. A 10 uF X5R 6.3V 0402 loses a large "
    "fraction of its capacitance at 3 V of bias, and the manufacturer's "
    "curve was not fetched. 40 uF is therefore an UPPER BOUND and every "
    "droop here is optimistic by an unmeasured amount. Fetch Samsung's "
    "CL05A106MQ5NUNC bias curve and re-run before believing the margin.",
    "THE SoC's INTERNAL DC/DC is not modelled. A buck draws more input "
    "current as the rail sags, so a flat current source is optimistic at "
    "the bottom of the droop. Conservative in the other direction: the "
    "3.7 mA figure is already the DC/DC-enabled number.",
    "THE ADVERTISING SLEEP CURRENT IS BRACKETED, NOT KNOWN. research/05 "
    "§11.2: Nordic publishes 128 kB (2.0 uA) and 256 kB (3.1 uA) with GRTC "
    "and LFXO running, but not the 192 kB row the nRF54L10 actually uses. "
    "Every battery-life figure here scales inversely with it.",
]
