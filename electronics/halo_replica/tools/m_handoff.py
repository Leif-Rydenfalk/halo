#!/usr/bin/env python3
"""m_handoff.py -- ONE consolidated positions file for L5, with per-row flags.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.

WHY PER-ROW FLAGS AND NOT A DOCUMENT.  L5 draws what it is handed, and it has
already once drawn a per-degree silhouette as though it were board geometry.  So
anything that must NOT be drawn as a component says so IN ITS OWN ROW, in a field
called `do_not_draw_as_component`, with `why`.  A caveat in a markdown file two
directories away is not a safeguard.

EVERY ROW CARRIES: position in mm from the board centre, size in mm where the
size is trustworthy, THE SHORT SIDE IN GENUINE PIXELS (M06: this photograph
resolves 20.7-27.4 genuine px/mm against 106.3 stored, so a millimetre figure has
roughly 4-5x more digits than information), the method that found it, and a
confidence.

Board frame: origin = the board centre transferred from FCC photo 6 through
c_register's homography; +x right, +y DOWN in image convention; theta measured
from +x through +y.
"""
import argparse, hashlib, json, math, os, subprocess, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
M = os.path.join(HERE, "..", "metrology")

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(M, "HANDOFF-positions-front.json"))
ap.add_argument("--rim-frac", type=float, default=0.97,
                help="beyond this fraction of the local edge radius, a detection may be "
                     "sitting on the grey rim material rather than on the board")
ap.add_argument("--merge-mm", type=float, default=7.0)
a = ap.parse_args()

rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                     capture_output=True, text=True).stdout.strip()
comps = json.load(open(os.path.join(M, "components-front.json")))
darks = json.load(open(os.path.join(M, "dark-packages-front.json")))
raw = json.load(open(os.path.join(M, "outline-raw-oflynn-front.json")))
ocx, ocy = raw["outer_centre"]
P = np.array(raw["outer_r_theta"], float)
o = np.argsort(P[:, 0]); T, R = P[o, 0], P[o, 1]
Rs = np.convolve(np.concatenate([R] * 3), np.ones(41) / 41, mode="same")[len(R):2 * len(R)]
ppm = comps["px_per_mm"]
g_lo, g_hi = comps["genuine_px_per_mm"]

rows = []
for i, c in enumerate(comps["components"]):
    ang = math.degrees(math.atan2(c["cy"] - ocy, c["cx"] - ocx)) % 360
    frac = math.hypot(c["cx"] - ocx, c["cy"] - ocy) / float(np.interp(ang, T, Rs))
    flags, why, dnd = [], [], False
    if c["long_mm"] > a.merge_mm:
        flags.append("merged_pad_run"); dnd = True
        why.append(f"long side {c['long_mm']:.2f} mm exceeds {a.merge_mm} mm; adjacent pads "
                   f"join at this threshold. NOT A SINGLE PART.")
    if c["size_verdict"] != "SOUND":
        flags.append("located_not_sized")
        why.append(f"short side {c['short_genuine_px'][0]:.1f}-{c['short_genuine_px'][1]:.1f} "
                   f"genuine px, under 10. Position usable, SIZE IS NOT.")
    if frac > a.rim_frac:
        flags.append("on_rim_material_suspect")
        why.append(f"sits at {frac:.3f} of the local edge radius, where a grey fibrous "
                   f"material laps over the rim (M02 Sec 8). May be that material, not a part.")
    rows.append(dict(
        id=f"B{i:03d}", method="bright-metal segmentation (m_components.py)",
        found="metal: pad, termination, can or solder",
        x_mm=c["x_mm"], y_mm=c["y_mm"], r_mm=c["r_mm"], theta_deg=c["theta_deg"],
        long_mm=c["long_mm"] if "merged_pad_run" not in flags else None,
        short_mm=c["short_mm"] if c["size_verdict"] == "SOUND" else None,
        short_genuine_px=c["short_genuine_px"], area_mm2=c["area_mm2"],
        radial_fraction_of_edge=round(frac, 4),
        confidence=("low" if dnd or "on_rim_material_suspect" in flags
                    else ("medium" if "located_not_sized" in flags else "high")),
        flags=flags, do_not_draw_as_component=dnd, why="; ".join(why) or None))

for i, c in enumerate(darks["packages"]):
    ang = math.degrees(math.atan2(c["cy"] - ocy, c["cx"] - ocx)) % 360
    frac = math.hypot(c["cx"] - ocx, c["cy"] - ocy) / float(np.interp(ang, T, Rs))
    rows.append(dict(
        id=f"D{i:03d}", method="blue-body colour segmentation (m_dark_packages.py)",
        found="IC package body whose epoxy colour differs from the soldermask",
        x_mm=c["x_mm"], y_mm=c["y_mm"], r_mm=c["r_mm"], theta_deg=c["theta_deg"],
        long_mm=c["long_mm"], short_mm=c["short_mm"],
        short_genuine_px=c["short_genuine_px"], area_mm2=c["area_mm2"],
        body_angle_deg=c["angle_deg"], rect_fill=c["fill"],
        radial_fraction_of_edge=round(frac, 4),
        confidence="high", flags=[], do_not_draw_as_component=False, why=None))

out = dict(
    generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), git_rev=rev,
    producer="L1 PHOTOGRAPH METROLOGY lane",
    side="FRONT = the COMPONENT side (Apple's FCC caption). O'Flynn's "
         "backside-fullres.jpeg IS this side.",
    source_image="images/airtag/oflynn-backside-fullres.jpeg",
    frame=dict(origin="board centre, transferred from FCC photo 6 through c_register's "
                      "homography; the transferred OUTER outline lands on this board's edge "
                      "all the way round (evidence/E-L1-transferred-frame-on-oflynn-front.png) "
                      "and no outline point was fitted to",
               axes="+x right, +y DOWN (image convention); theta from +x through +y",
               origin_px=comps["origin_px"]),
    scale=dict(stored_px_per_mm=ppm,
               basis=comps["px_per_mm_basis"],
               genuine_px_per_mm=[g_lo, g_hi],
               decoration_factor=f"{ppm/g_hi:.1f}-{ppm/g_lo:.1f}x more stored pixels than "
                                 f"resolved detail (M06)",
               independent_check="the nRF52832 body measures -0.23% / -0.54% against its "
                                 "datasheet at this scale (M08)"),
    uncertainty=dict(registration_holdout_mm=0.1029,
                     registration_holdout_genuine_px=[round(0.1029 * g_lo, 2),
                                                      round(0.1029 * g_hi, 2)],
                     note="DO NOT QUOTE ANY POSITION TO 0.01 mm. The floor is 2-3 genuine px."),
    excluded=[dict(what="neutral-black IC packages, including the large one at 9 o'clock",
                   verdict="CANNOT DETERMINE",
                   why="B-R = +0.5 against a board median of +1, so colour cannot see them; "
                       "dark+smooth merges with bare soldermask; a black top-hat connects the "
                       "board into one 1.76 Mpx blob; and a stated ROI with Otsu inside "
                       "returns the BOX (0/20/40/60 px padding gives 3.35/3.98/4.09/4.50 mm "
                       "for the same part). See M08 Sec 2.",
                   instruction="DO NOT place these by hand from the transferred frame. An "
                               "eyeballed position in a file of measured ones is the "
                               "contamination this lane exists to prevent."),
              dict(what="the centre hole", verdict="PARTIALLY DETERMINED",
                   why="two photographs fail to pin it in DIFFERENT directions (M02 Sec 4, "
                       "M07 Sec 5). Publish no hole diameter."),
              dict(what="rim tear-off / edge pads", verdict="CANNOT DETERMINE",
                   why="M03/M05. Do not draw the withdrawn 15 or 13 candidate angles as pads.")],
    counts=dict(total=len(rows),
                bright=len(comps["components"]), dark=len(darks["packages"]),
                do_not_draw=sum(1 for r in rows if r["do_not_draw_as_component"]),
                located_not_sized=sum(1 for r in rows if "located_not_sized" in r["flags"]),
                on_rim_material_suspect=sum(1 for r in rows
                                            if "on_rim_material_suspect" in r["flags"]),
                high_confidence=sum(1 for r in rows if r["confidence"] == "high")),
    rows=rows)
json.dump(out, open(a.out, "w"), indent=2)
print("m_handoff.py -- inputs:")
print(f"  components-front.json   run {comps['run_utc']}  {comps['n_components']} rows")
print(f"  dark-packages-front.json run {darks['run_utc']}  {darks['n']} rows")
print(f"  outline-raw-oflynn-front.json  for the local edge radius")
print(f"\n  {out['counts']}")
print(f"  wrote {a.out}")
