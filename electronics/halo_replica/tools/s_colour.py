#!/usr/bin/env python3
"""s_colour.py — mean sRGB of a rectangle in a photograph, with an in-frame control.

Surface finish cannot be read from a colour name; it can be read from a HUE
DIFFERENCE between two regions lit by the same light in the same frame. Bare
copper is salmon (hue ~15-25 deg); immersion/electroless gold is yellow
(hue ~40-55 deg). This prints hue so the two can be separated, and it is only
trustworthy when a known-copper control is measured in the SAME image.

Usage: s_colour.py <image> <label>:<x0>,<y0>,<x1>,<y1> [<label>:... ]
"""
import sys, colorsys
from PIL import Image

im = Image.open(sys.argv[1]).convert("RGB")
print(f"{'region':<22}{'n':>7}  {'R':>5}{'G':>5}{'B':>5}   {'hue_deg':>8}{'sat':>7}{'val':>7}")
for spec in sys.argv[2:]:
    label, box = spec.split(":")
    x0, y0, x1, y1 = (int(v) for v in box.split(","))
    px = list(im.crop((x0, y0, x1, y1)).getdata())
    n = len(px)
    r, g, b = (sum(c[i] for c in px) / n for i in range(3))
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    print(f"{label:<22}{n:>7}  {r:5.0f}{g:5.0f}{b:5.0f}   {h*360:8.1f}{s:7.3f}{v*255:7.0f}")
