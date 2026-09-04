"""Write ce-rf specs for halo rev A's OWN copper, from footprints.py's geometry.

    cd ~/dev/ce-workshop
    python3 ce-designs/halo/electronics/halo_rev_a/sim/make_rf_specs.py
    ce-rf/bin/rf antenna  ce-designs/halo/electronics/halo_rev_a/sim/halo-rev-a-2g4.json
    ce-rf/bin/rf nfc-coil ce-designs/halo/electronics/halo_rev_a/sim/halo-rev-a-nfc.json

WHY THESE EXIST WHEN ce-rf ALREADY SHIPS NINE halo CASES. Every one of them
is a Ø30 mm board. Lane M's design.py fixes the real PCB at Ø26.00 x 0.60 mm
with three keying notches, and the CR2032 sits 0.578 mm BELOW it rather than
beside it. spec/convergence.json's "Board outline diameter" row compares 30.0
against 31.87 - two numbers, neither of which is the board. These specs are
the same solver pointed at the copper that is actually being fabricated.

Geometry is IMPORTED from footprints.py, not retyped, so the simulated
element and the etched element cannot drift apart.

---------------------------------------------------------------------------
WHAT ce-rf CANNOT BE TOLD ABOUT THIS BOARD, stated before the results
---------------------------------------------------------------------------
`cerf/fdtd.py::_ground_shapes` accepts exactly two ground primitives, `rect`
and `circle`. There is no polygon and there is no cutout. halo rev A's ground
is neither: it is a pour over most of a Ø26 disc with a 94-degree sector cut
out of all four layers under the antenna, fragmented in the outer annulus by
the NFC winding, three battery contact lands and eight UWB lands.

That shape cannot be written in this spec language. So the ground here is
modelled as a Ø20.8 mm disc on the top and bottom layers - the dense inner
pour, out to the radius where the annulus starts being other things - and
the annulus copper is ABSENT from the model.

THE CONSEQUENCE, AND ITS DIRECTION. A monopole works against its
counterpoise. Understating the counterpoise makes the ground look smaller
than it is, which typically raises the resonant frequency and lowers the
radiation resistance. So a resonance measured here is expected to sit ABOVE
the real board's, and the number is a BOUND rather than a prediction. It is
still worth having, because the two existing cases resonate at 4.0 and
5.8 GHz against a 2.44 GHz target and the question is whether our element
length is in the right neighbourhood at all.

Closing this properly needs one of two things, and both are recorded rather
than worked around: a polygon-or-cutout ground in ce-rf (lane T3's repo, so
it is a request and not a patch), or a direct openEMS model built from the
Gerbers. Neither is done here.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(HERE) not in sys.path:
    sys.path.insert(0, os.path.dirname(HERE))

import footprints as fpg                                          # noqa: E402

D_PCB = 26.00
T_PCB = 0.600
D_CELL = 20.00
R_GND = 10.40              # the dense inner pour's edge — see the docstring
FEED_DEG = 90.0            # the element is drawn with its feed at 12 o'clock
                           # so the port is axis-aligned, which is what
                           # cerf's feed `dir` requires. A circular board
                           # with a circular ground is rotation-invariant, so
                           # this costs nothing physically.
FEED_GAP = 0.80
TAB_W = 1.00


def polar(r, deg):
    a = math.radians(deg)
    return [r * math.cos(a), r * math.sin(a)]


def staircase(r, a0_deg, target_mm, step_deg=1.0, max_deg=360.0):
    """The arc as AXIS-ALIGNED copper, walked until it is `target_mm` long.

    ce-rf builds axis-aligned copper only and REFUSES a diagonal rather than
    silently staircasing it — which is the right refusal, because a
    staircased diagonal is longer than the diagonal and the difference is
    electrical length, the one quantity an antenna is most sensitive to.

    So the staircase is built here, deliberately, and it is walked until its
    COPPER LENGTH equals the quarter wave rather than until it has covered
    the arc's angle. A Manhattan path along an arc is about 1.15 to 1.27
    times as long as the arc it follows, so matching the angle would have
    modelled a conductor a fifth longer than the one being etched and
    resonated it correspondingly low. Matching the LENGTH models the right
    conductor in a slightly smaller angle, and the angle it reaches is
    reported so the difference is visible rather than buried.
    """
    pts = [polar(r, a0_deg)]
    total = 0.0
    a = a0_deg
    while total < target_mm and (a - a0_deg) < max_deg:
        a += step_deg
        nx, ny = polar(r, a)
        cx, cy = pts[-1]
        for cand in ((nx, cy), (nx, ny)):
            seg = abs(cand[0] - pts[-1][0]) + abs(cand[1] - pts[-1][1])
            if seg < 1e-9:
                continue
            if total + seg >= target_mm:
                # trim the last segment so the total is EXACTLY the target
                f = (target_mm - total) / seg
                pts.append([pts[-1][0] + (cand[0] - pts[-1][0]) * f,
                            pts[-1][1] + (cand[1] - pts[-1][1]) * f])
                return pts, target_mm, a - a0_deg
            total += seg
            pts.append([cand[0], cand[1]])
    return pts, total, a - a0_deg


def antenna_spec():
    arc_deg = fpg.ANT_ARC_MAX_DEG
    used = fpg.path_length_mm(fpg.element_path())
    tail = fpg.QUARTER_MM - used

    # The element as ce-rf can build it: an axis-aligned staircase along the
    # same circle, walked until its copper length IS the quarter wave.
    pts, stair_mm, stair_deg = staircase(fpg.ANT_R, FEED_DEG,
                                         fpg.QUARTER_MM)

    feed_r0 = fpg.ANT_R - FEED_GAP
    return {
        "case": "halo-rev-a-2g4",
        "kind": "antenna",
        "why": ("halo revision A's OWN 2.4 GHz element on its OWN board: a "
                "bent quarter-wave monopole, %.2f mm of arc at R%.2f (%.1f "
                "deg) plus a %.2f mm inward fold, %.2f mm of conductor, on "
                "the Ø26.00 x 0.60 mm four-layer disc lane M's design.py "
                "specifies. The nine cases ce-rf already carries are all "
                "Ø30 mm boards. THE GROUND IS UNDER-MODELLED - see "
                "make_rf_specs.py - so this resonance is a BOUND above the "
                "real board's, not a prediction of it. The element is an "
                "axis-aligned STAIRCASE here (ce-rf refuses diagonals) "
                "carrying the same %.3f mm of copper in %.1f deg of ring; "
                "the etched element MEANDERS that same length into %.1f deg "
                "with four teeth, which the staircase does not reproduce. "
                "Length is matched, shape is not, and a meander couples to "
                "itself in a way a plain run does not - so the etched part "
                "will resonate a little BELOW this model."
                % (used, fpg.ANT_R, arc_deg, tail, used + tail,
                   stair_mm, stair_deg, arc_deg)),
        "board": {
            "outline": {"shape": "circle", "diameter_mm": D_PCB},
            "thickness_mm": T_PCB,
            "epsilon_r": 4.3,
            "loss_tangent": 0.02,
            "copper_thickness_um": 35,
            "why": ("Ø26.00 x 0.600 mm, from ce-designs/halo/design.py "
                    "D_PCB and T_PCB. The three 26-degree keying notches are "
                    "NOT modelled - cerf outlines are circle or rect - and "
                    "they are what limits the element to 84 degrees, so "
                    "their absence changes the board's edge but not the "
                    "conductor length, which is the quantity under test. "
                    "eps_r 4.3 / tan_d 0.02 is GENERIC FR-4, not fab-quoted, "
                    "and is the largest single uncertainty in the frequency.")
        },
        "ground": {
            "layer": "top",
            "shapes": [
                {"shape": "circle", "diameter_mm": 2 * R_GND, "layer": "top",
                 "why": "the top pour out to R10.40, where the annulus stops "
                        "being ground and starts being the NFC winding, the "
                        "battery contact lands and the antenna's own cleared "
                        "sector"},
                {"shape": "circle", "diameter_mm": 2 * R_GND, "layer":
                 "bottom",
                 "why": "the bottom pour, same radius. The two INNER layers "
                        "are not modelled: cerf takes a top and a bottom "
                        "ground and no stackup, and that absence is stated "
                        "rather than guessed."},
                {"shape": "circle", "diameter_mm": D_CELL, "layer": "bottom",
                 "why": "THE CELL. A Ø20.0 mm steel can 0.578 mm below the "
                        "board (design.py Z_CELL_TOP 4.022, Z_DECK_TOP "
                        "4.600). It is modelled as copper at the bottom "
                        "layer because that is the nearest thing this "
                        "solver has to it; a real can is steel, further "
                        "away, and lossier."},
                {"shape": "rect", "layer": "top",
                 "x0_mm": -TAB_W / 2.0, "y0_mm": R_GND - 1.5,
                 "x1_mm": TAB_W / 2.0, "y1_mm": feed_r0,
                 "why": "the ground finger that carries the port out of the "
                        "pour, so the feed is a clean rectangle-to-conductor "
                        "gap of %.2f mm instead of a trace grazing a circle. "
                        "Real copper: the layout has a via stitch and a "
                        "ground return here." % FEED_GAP},
            ]
        },
        "antenna": {
            "type": "polyline",
            "trace_width_mm": fpg.ANT_W,
            "min_ground_clearance_mm": 0.15,
            "paths_mm": [pts],
            "feed_point_mm": polar(fpg.ANT_R, FEED_DEG),
        },
        "feed": {
            "resistance_ohm": 50,
            "from_mm": [0.0, feed_r0],
            "to_mm": [0.0, fpg.ANT_R],
            "dir": "y"
        },
        "sim": {
            "f0_GHz": 2.45, "fc_GHz": 1.6,
            "cells_per_wavelength": 22, "substrate_cells": 3,
            "end_criteria": 1e-4, "max_timesteps": 300000,
            "post_f_Hz": [1.0e9, 6.0e9, 1001],
            "fine_res_mm": 0.25,
            "farfield_s11_threshold_dB": -3.0,
            "farfield_f_GHz": 2.4418
        },
        "bands": [{"name": "ble", "lo_GHz": 2.4, "hi_GHz": 2.4835,
                   "why": "the 2400.0-2483.5 MHz ISM allocation BLE uses"}],
        "match": {
            "target_ohm": 50.0, "at_GHz": 2.4418,
            "why": ("the schematic carries a pi network (C20/L10/C21) at the "
                    "feed for exactly this. A bent monopole in a 3 mm "
                    "annulus has a low radiation resistance and its BARE "
                    "port is a poor match; ce-rf designs one L-section and "
                    "then MEASURES that fixed network across the band, which "
                    "is what the pi's values will be set from.")
        },
        "asserts": {
            "f_series_res_GHz": {"between": [2.4, 2.4835]},
            "s11_worst_in_ble_matched_dB": {"lte": -6.0},
            "solver_converged": {"gte": 1}
        },
        "asserts_why": {
            "f_series_res_GHz": ("no invented tolerance: the interval IS the "
                                 "2400.0-2483.5 MHz allocation, graded on "
                                 "the LOWEST SERIES RESONANCE rather than "
                                 "the deepest dip, because a small antenna "
                                 "has a shallow fundamental and a deep "
                                 "higher-order mode and grading the dip "
                                 "grades the wrong one"),
            "s11_worst_in_ble_matched_dB": ("-6 dB is VSWR 3.0, the loosest "
                                            "figure small-antenna practice "
                                            "accepts inside a puck, and it "
                                            "is the WORST reflection "
                                            "anywhere in the band"),
            "solver_converged": "an unconverged FDTD run is not a measurement"
        },
        "_geometry_source": {
            "file": "ce-designs/halo/electronics/halo_rev_a/footprints.py",
            "ANT_R_mm": fpg.ANT_R, "ANT_W_mm": fpg.ANT_W,
            "ANT_ARC_MAX_DEG": fpg.ANT_ARC_MAX_DEG,
            "quarter_wave_mm": fpg.QUARTER_MM,
            "arc_deg_used": arc_deg, "arc_mm": used, "fold_mm": tail,
            "conductor_mm": used + tail,
            "staircase_mm": stair_mm, "staircase_deg": stair_deg,
            "staircase_note": ("ce-rf builds axis-aligned copper only, so "
                               "the arc is walked as a Manhattan staircase "
                               "until its COPPER LENGTH equals the quarter "
                               "wave. Matching length rather than angle "
                               "models the right conductor; the angle it "
                               "reaches is smaller than the etched arc's "
                               "and that difference is reported here."),
            "why": "imported, not retyped, so the simulated element and the "
                   "etched element cannot drift apart"
        }
    }


def nfc_spec():
    r_in = fpg.NFC_R_OUT - (fpg.NFC_TURNS - 1) * (fpg.NFC_W + fpg.NFC_GAP)
    return {
        "case": "halo-rev-a-nfc",
        "kind": "nfc-coil",
        "why": ("halo revision A's OWN NFC coil: %d turns, %.2f mm trace / "
                "%.2f mm gap, outermost R%.2f, innermost R%.2f, on B.Cu. "
                "TWO TURNS, NOT FIVE, and that is forced rather than chosen: "
                "the usable annulus is R10.15 to R10.85 because R10.0 is the "
                "cell can and R10.94 is the nearest battery contact land "
                "minus clearance, and at the 0.30 mm pitch a 0.127 mm "
                "process allows that is 2.33 turns. ce-rf's shipped case "
                "uses a Ø28 mm 5-turn coil on a Ø30 board, which is a coil "
                "this product has no room for."
                % (fpg.NFC_TURNS, fpg.NFC_W, fpg.NFC_GAP, fpg.NFC_R_OUT,
                   r_in)),
        "f0_MHz": 13.56,
        "geometry": {
            "shape": "circle",
            "outer_diameter_mm": 2 * fpg.NFC_R_OUT,
            "turns": fpg.NFC_TURNS,
            "trace_width_mm": fpg.NFC_W,
            "trace_space_mm": fpg.NFC_GAP,
            "copper_thickness_um": 35
        },
        "ic": {
            "part": "nRF54L10 NFCT peripheral",
            "input_capacitance_pF": 8.0,
            "why": ("THERE IS NO NFC CHIP - SPEC.md F8. The load is the "
                    "SoC's own NFC-A tag peripheral on NFC1/NFC2 plus the "
                    "package and pin capacitance. 8 pF is an ESTIMATE for "
                    "that, NOT a datasheet figure: Nordic's NFCT chapter "
                    "specifies the tuning capacitors (about 130 pF per pin "
                    "for a 2 uH antenna) rather than its own input "
                    "capacitance. C_external moves 1:1 with this number, so "
                    "the external value below is only as good as the "
                    "estimate.")
        },
        "parasitic_capacitance_pF": 0.0,
        "asserts": {
            "inductance_uH": {"gt": 0.2},
            "C_external_pF": {"gt": 0.0},
            "cross_check_spread_pct": {"lte": 8.0}
        },
        "asserts_why": {
            "inductance_uH": ("0.2 uH, not the 0.5 uH ce-rf's Ø28 5-turn "
                              "case asserts. A 2-turn Ø21.5 coil cannot "
                              "reach 0.5 uH and asserting that it must would "
                              "be a target chosen to fail. What this assert "
                              "checks is that the solver returned a physical "
                              "inductance at all; WHETHER 2 turns couples "
                              "enough to read at a phone's field strength is "
                              "NOT settled here and no assert pretends it "
                              "is - see the README's open items."),
            "C_external_pF": "a tuning capacitance that is not positive "
                             "means the coil cannot be resonated at 13.56 "
                             "MHz with the stated load at all",
            "cross_check_spread_pct": "two independent inductance formulae "
                                      "must agree; if they do not, neither "
                                      "is trustworthy"
        },
        "_geometry_source": {
            "file": "ce-designs/halo/electronics/halo_rev_a/footprints.py",
            "NFC_R_OUT_mm": fpg.NFC_R_OUT, "NFC_W_mm": fpg.NFC_W,
            "NFC_GAP_mm": fpg.NFC_GAP, "NFC_TURNS": fpg.NFC_TURNS,
            "r_inner_mm": r_in
        }
    }


if __name__ == "__main__":
    for name, doc in (("halo-rev-a-2g4", antenna_spec()),
                      ("halo-rev-a-nfc", nfc_spec())):
        path = os.path.join(HERE, name + ".json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2)
        print("wrote", path)
    g = antenna_spec()["_geometry_source"]
    print("\n--- the element, from footprints.py ---")
    for k in ("quarter_wave_mm", "arc_deg_used", "arc_mm", "fold_mm",
              "conductor_mm", "staircase_mm", "staircase_deg"):
        print("  %-18s %.3f" % (k, g[k]))
    n = nfc_spec()["_geometry_source"]
    print("\n--- the coil, from footprints.py ---")
    print("  %d turns, %.2f/%.2f mm, R%.2f down to R%.2f"
          % (n["NFC_TURNS"], n["NFC_W_mm"], n["NFC_GAP_mm"],
             n["NFC_R_OUT_mm"], n["r_inner_mm"]))
