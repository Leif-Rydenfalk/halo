#!/usr/bin/env python3
"""d_draw.py -- draw the boundary evidence back onto the photograph and LOOK at it.

L7 DARK-PACKAGE DETECTOR lane.  Every side is drawn in the colour of its own
verdict, so a reader sees WHICH boundaries the photograph carries rather than
reading that it carries few.  Green = clears the bar, amber = half, red = absent.
Nothing here is a component outline: the boxes are the EYEBALLED seeds, drawn so
the measurement can be checked, and they are labelled as such on the image.
"""
import json, math, os, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
DP = os.path.join(HERE, "..", "metrology", "darkpkg")
IMG = os.path.abspath(os.path.join(HERE, "..", "..", "..", "images", "airtag",
                                   "oflynn-backside-fullres.jpeg"))


def colour(z, bar):
    if z is None:
        return (150, 150, 150)
    if z >= bar:
        return (40, 220, 90)
    if z >= 0.5 * bar:
        return (245, 180, 40)
    return (230, 50, 50)


def main():
    h = json.load(open(os.path.join(DP, "HANDOFF-darkpackages.json")))
    bar = h["method"]["nulls"]["n3_real_board_random"]["p99"]
    im = Image.open(IMG).convert("RGB")
    d = ImageDraw.Draw(im)
    for r in h["rows"]:
        cx, cy = r["seed_stored_px"]
        t = math.radians(r["seed_theta_deg"])
        W = r["seed_short_mm"] * h["scale"]["stored_px_per_mm"] / 2
        H = r["seed_long_mm"] * h["scale"]["stored_px_per_mm"] / 2
        P = [(cx + u * math.cos(t) - v * math.sin(t), cy + u * math.sin(t) + v * math.cos(t))
             for u, v in ((-W, -H), (W, -H), (W, H), (-W, H))]
        for (p0, p1), key in zip([(P[0], P[3]), (P[1], P[2]), (P[0], P[1]), (P[3], P[2])],
                                 ["left", "right", "top", "bottom"]):
            d.line([p0, p1], fill=colour(r["side_abs_z"][key], bar), width=7)
        d.text((cx - 60, cy - H - 34),
               f"{r['name']}  {r['n_sides_supported']}/4  SEED, NOT A POSITION",
               fill=(255, 255, 255))
    ss = 3.226 * h["scale"]["stored_px_per_mm"] / 2
    for k, (px, py) in enumerate(h["detection_limit"]["sites_stored_px"]):
        d.rectangle([px - ss, py - ss, px + ss, py + ss], outline=(90, 160, 255), width=6)
        d.text((px - 66, py - ss - 30), f"limit site {k} (auto)", fill=(90, 160, 255))
    d.text((30, 30), f"L7 boundary evidence.  green |z|>={bar:.1f} (bar)  amber >=half  "
                     f"red absent.  1 of 20 boundaries supported.", fill=(255, 255, 255))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DP, "E-L7-boundary-evidence.png")
    im.resize((im.width * 2 // 3, im.height * 2 // 3), Image.LANCZOS).save(out)
    print(f"wrote {out}  -- LOOK AT IT")


if __name__ == "__main__":
    main()
