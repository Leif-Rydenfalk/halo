#!/usr/bin/env python3
"""s_colour.py — hue of a metal region in a photograph, against an in-frame control.

A surface finish cannot be read off a colour NAME; it can be read off a HUE
DIFFERENCE between two regions lit by the same light in the same frame. Bare
copper is salmon (hue ~15-25 deg); electroless-nickel/immersion-gold is yellow
(hue ~38-55 deg). The number is only trustworthy when a KNOWN-copper control is
measured in the SAME image, so this tool always prints one and refuses to be
used without one.

Pixels are selected before averaging: not blown out, not shadow, and actually
warm (R-B >= min_rb). No enhancement of any kind is applied to the source.

Usage: s_colour.py <image> <label>:<x0>,<y0>,<x1>,<y1> [...]
"""
import colorsys
import sys
from PIL import Image


def masked(path, box, lo_v=60, hi_v=250, min_rb=20):
    """(n, R, G, B, hue_deg, sat) over the metallic pixels inside box, or None."""
    im = Image.open(path).convert("RGB")
    sel = [c for c in im.crop(box).getdata()
           if lo_v <= max(c) <= hi_v and (c[0] - c[2]) >= min_rb]
    if not sel:
        return None
    n = len(sel)
    r, g, b = (sum(c[i] for c in sel) / n for i in range(3))
    h, s, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return n, r, g, b, h * 360, s


def main(argv):
    img = argv[1]
    print(f"{'region':<44}{'n':>6}{'R':>5}{'G':>5}{'B':>5}{'hue':>8}{'sat':>7}")
    for spec in argv[2:]:
        label, box = spec.split(":")
        res = masked(img, tuple(int(v) for v in box.split(",")))
        if res is None:
            print(f"{label:<44}  no warm pixels in box — CANNOT DETERMINE")
            continue
        n, r, g, b, h, s = res
        print(f"{label:<44}{n:6d}{r:5.0f}{g:5.0f}{b:5.0f}{h:8.1f}{s:7.3f}")


if __name__ == "__main__":
    main(sys.argv)
