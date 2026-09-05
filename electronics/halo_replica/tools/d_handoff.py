#!/usr/bin/env python3
"""d_handoff.py -- build metrology/darkpkg/HANDOFF-darkpackages.json from the
measurement files, never by hand.

L7 DARK-PACKAGE DETECTOR lane, halo Replica.  Reads d-probe.json (per-side
evidence per package), d-limit.json (the detection limit, measured with a
rectangle pasted into this same photograph) and d-bar.json (the whole-board
admission bar), and emits rows in the SAME shape as
metrology/HANDOFF-positions-front.json so a consumer needs no second reader.

It publishes NO position and NO size, and that is the result rather than a
shortfall: see the `excluded` block for the number that closes it.
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
MET = os.path.join(HERE, "..", "metrology")
DP = os.path.join(MET, "darkpkg")

WHAT = {
    "nRF52832_CIAA_control": ("the SoC, the positive control -- blue epoxy, "
                              "published body 2.956 x 3.226 mm"),
    "black_9oclock": "the large neutral-black package at 9 o'clock",
    "plus_AKN_8H7": 'the "+AKN 8H7" IC on the right of the board',
    "black_05I_1A8": 'the black package marked "05I 1A8"',
    "black_diode_lower": "a black two-terminal body (diode-like) below the 9 o'clock package",
}


def main():
    probe = json.load(open(os.path.join(DP, "d-probe.json")))
    limit = json.load(open(os.path.join(DP, "d-limit.json")))
    bar = json.load(open(os.path.join(DP, "d-bar.json")))
    src = json.load(open(os.path.join(MET, "HANDOFF-positions-front.json")))
    rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE,
                         capture_output=True, text=True).stdout.strip() or "unknown"

    lad = limit["ladder"]
    need3 = next((r["step_luma"] for r in sorted(lad, key=lambda r: r["step_luma"])
                  if r["sides_clearing"] >= 3), None)
    need4 = next((r["step_luma"] for r in sorted(lad, key=lambda r: r["step_luma"])
                  if r["sides_clearing"] >= 4), None)
    barz = probe["admission_bar_abs_z"]

    rows = []
    for i, r in enumerate(probe["rows"]):
        steps = r["side_step_luma_at_seed"]
        best = max(abs(v) for v in steps.values())
        rows.append(dict(
            id=f"D{i:03d}", name=r["name"], what=WHAT.get(r["name"], "unnamed dark body"),
            method="boundary-evidence per-side fit (tools/d_rect.py fit_sides via "
                   "tools/d_darkpkg.py probe); the statistic is a directional-derivative "
                   "line integral over an empirical null, with no intensity level in it",
            found="a dark body IS present here BY EYE at native resolution; what is "
                  "reported is how much of its boundary the photograph carries",
            x_mm=None, y_mm=None, r_mm=None, theta_deg=None,
            long_mm=None, short_mm=None, short_genuine_px=None, area_mm2=None,
            side_abs_z=r["side_abs_z"], side_supported=r["side_supported"],
            n_sides_supported=r["n_sides_supported"],
            side_step_luma_at_seed=steps, best_side_step_luma=best,
            seed_stored_px=r["seed_stored_px"], seed_theta_deg=r["seed_theta_deg"],
            seed_long_mm=r["seed_long_mm"], seed_short_mm=r["seed_short_mm"],
            seed_is_eyeballed=True,
            fit_long_mm=r["fit_long_mm"], fit_short_mm=r["fit_short_mm"],
            fit_long_spread_mm=r["fit_long_spread_mm"],
            fit_short_spread_mm=r["fit_short_spread_mm"],
            fit_centre_wander_mm=r["seed_swing_mm"],
            confidence="none",
            verdict="CANNOT DETERMINE",
            measured=False,
            do_not_draw_as_component=True,
            why=(f"{r['n_sides_supported']} of 4 boundaries clear the bar "
                 f"(|z| > {barz}, the 99th percentile of the same scan at random "
                 f"places and random angles ON THIS BOARD). A dimension needs BOTH "
                 f"sides of its axis, so no dimension exists. The seed position is "
                 f"EYEBALLED off a native tile and is present only so the reader can "
                 f"check the measurement; it is not a position and must not be drawn. "
                 f"Largest boundary step on any side: {best:.0f} luma, against the "
                 f"{need3:.0f} luma this photograph needs (see `excluded`).")))

    out = dict(
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        git_rev=rev,
        producer="L7 DARK-PACKAGE DETECTOR lane",
        side=src["side"],
        source_image=src["source_image"],
        frame=src["frame"], scale=src["scale"], uncertainty=src["uncertainty"],
        supersedes_nothing="M08 and M10 stand. This neither overturns nor confirms any "
                           "number in them; it closes the question they left open, by a "
                           "different route, with a limit.",
        method=dict(
            name="boundary evidence, per side",
            statistic="a straight edge integrates the directional derivative COHERENTLY "
                      "along its length (~L); texture sums incoherently (~sqrt L). The "
                      "score is that line integral divided by an EMPIRICAL null built by "
                      "rolling each gradient row independently. No absolute intensity, no "
                      "colour and no texture threshold appears anywhere.",
            why_not_closure="a four-sided closure test was tried first and is REFUTED on "
                            "this board by measurement: around the nRF52832 the four "
                            "boundary steps are -75, -10, +8 and +1 luma and the interior "
                            "luma runs 90/41/66/36, so the surround is brighter on one "
                            "side and darker on another. Requiring four alike boundaries "
                            "cannot recover a part whose fourth boundary is not in the "
                            "data, and settling for the best CLOSED rectangle nearby "
                            "returns a STABLE WRONG ANSWER (-26 % on the nRF, unmoved by "
                            "downsample, band width or peak count). Stability is not "
                            "correctness.",
            engine="tools/d_rect.py (selftest: `bin/boardmetro rect-selftest`, 10 cases, "
                   "4 of them watched failing on purpose)",
            nulls=dict(
                n1_phase_scramble=probe["nulls"]["n1_phase_scramble"],
                n3_real_board_random=probe["nulls"]["n3_real_board_random"],
                which_decides="N3. N1 only asks whether a boundary beats texture of the "
                              "same power spectrum. N3 asks the question a DETECTOR has "
                              "to answer: is a package boundary exceptional among the "
                              "straight structures this board already has -- traces, pad "
                              "rows, silkscreen, the rim.",
            ),
            whole_board_score_bar=bar["admission_bar"],
        ),
        detection_limit=dict(
            how="a 3.226 x 2.956 mm rectangle of KNOWN boundary step pasted into this same "
                "photograph, at the quietest 4.2 mm window that lies wholly on the board -- "
                "chosen by the code, not by me. A synthetic control cleaner than the "
                "photograph is not evidence (E07 sec.4), so this one is made OF the "
                "photograph.",
            paste_at_stored_px=limit["paste_at_stored_px"],
            ladder=lad,
            step_luma_for_3_of_4_sides=need3,
            step_luma_for_4_of_4_sides=need4,
            reading=f"this photograph needs a boundary step of about {need3:.0f} luma before "
                    f"3 of a package's 4 sides become exceptional, and about {need4:.0f} "
                    f"luma for all 4. Size recovery is good once that is met: at "
                    f"{need4:.0f} luma the pasted rectangle measures "
                    f"{lad[0]['long_mm']} x {lad[0]['short_mm']} mm against a true "
                    f"3.226 x 2.956.",
        ),
        excluded=[dict(
            what="every neutral-black IC package on this face, and the nRF52832 as well",
            verdict="CANNOT DETERMINE",
            why="the packages present 1 to 26 luma of boundary step on most of their sides "
                "(the nRF reaches 75 on ONE side and 1-10 on the other three), against the "
                f"{need3:.0f} luma this photograph is measured to need. This is not 'we "
                "could not see them'; it is 'at the boundary contrast they actually "
                "present, they could not have been seen by any boundary method on this "
                "source'.",
            instruction="DO NOT place any of these by hand from the transferred frame. The "
                        "seed positions in `rows` are eyeballed and are published so the "
                        "measurement can be checked, not so it can be drawn.",
        ), dict(
            what="the nRF52832's one supported boundary",
            verdict="MARGINAL, and not published as a position",
            why=f"|z| 37.2 clears the N3 99th percentile ({barz}) but not the N3 maximum "
                "(45.4). One boundary is a LINE, not a position, and a line at the 99th "
                "percentile of the board's own straight structures is not a datum.",
        )],
        known_gaps=[dict(
            what="the largest body on the board (the metal can at the lower left) and the "
                 "small can at the upper right",
            why_not_here="both are METAL, not dark plastic. They belong to the bright-metal "
                         "segmentation, and M08 sec.5 already measured the UWB can's short "
                         "side at 3.56-3.67 mm with its long side CANNOT DETERMINE. Not "
                         "re-measured here, and not claimed.",
            measured=False, do_not_draw_as_measured=True,
        )],
        counts=dict(total=len(rows), measured=0, located_not_sized=0,
                    cannot_determine=len(rows), do_not_draw=len(rows),
                    sides_supported_total=sum(r["n_sides_supported"] for r in rows),
                    sides_examined=4 * len(rows)),
        what_would_close_it=[
            "a photograph of THIS face with more genuine resolution AND more boundary "
            "contrast. M10 already showed that resolution alone does not do it: a source "
            "with 1.9x more genuine resolution left the packages inside the soldermask "
            "range on both luma and local texture. The missing quantity is CONTRAST AT THE "
            "BOUNDARY, and the number it has to reach is in `detection_limit`.",
            "oblique or raking illumination, which converts a package's HEIGHT into a "
            "boundary step. Every method tried on this project so far -- intensity, "
            "texture, colour, boundary -- reads a flat-lit photograph, and a 0.5 mm tall "
            "body under raking light has a shadow edge that none of them needs to infer.",
            "an X-ray or a die-level teardown image, where package outlines are geometry "
            "rather than reflectance.",
        ],
        rows=rows,
    )
    p = os.path.join(DP, "HANDOFF-darkpackages.json")
    json.dump(out, open(p, "w"), indent=2)
    print(f"wrote {p}  -- {len(rows)} rows, {out['counts']['measured']} measured, "
          f"{out['counts']['sides_supported_total']} of "
          f"{out['counts']['sides_examined']} boundaries supported")
    return 0


if __name__ == "__main__":
    sys.exit(main())
