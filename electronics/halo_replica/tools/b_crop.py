#!/usr/bin/env python3
"""b_crop.py — crop and upscale a region of a photograph for marking-reading.

Usage: b_crop.py <image> <x0> <y0> <x1> <y1> <scale> <out.png>
Coordinates are in the SOURCE image's pixels. Nothing is enhanced beyond a
Lanczos resample: no sharpening, no contrast stretch, so what is read off the
crop is what is in the photograph.
"""
import sys
from PIL import Image

def crop(src, x0, y0, x1, y1, scale, out):
    """Lanczos crop+upscale. Nothing else is done to the pixels."""
    im = Image.open(src).crop((x0, y0, x1, y1))
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    im.save(out)
    print(f"{out} {im.size} from {src}[{x0}:{x1},{y0}:{y1}] x{scale}")
    return im


def grid(src, x0, y0, x1, y1, scale, out, step=50):
    """Same crop, with SOURCE-pixel gridlines and labels burned in, so a human
    reading the picture can hand a correct --box to b_pkgsize.py."""
    from PIL import ImageDraw
    im = Image.open(src).crop((x0, y0, x1, y1))
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    for gx in range((x0 // step) * step, x1 + step, step):
        px = (gx - x0) * scale
        if 0 <= px < im.width:
            d.line([(px, 0), (px, im.height)], fill=(255, 0, 0), width=1)
            d.text((px + 2, 2), str(gx), fill=(255, 255, 0))
    for gy in range((y0 // step) * step, y1 + step, step):
        py = (gy - y0) * scale
        if 0 <= py < im.height:
            d.line([(0, py), (im.width, py)], fill=(255, 0, 0), width=1)
            d.text((2, py + 2), str(gy), fill=(0, 255, 255))
    im.save(out)
    print(f"{out} {im.size} grid step {step} src px")


if __name__ == "__main__":
    # L8 2026-09-05: this block used to run at IMPORT time, so `from b_crop import
    # grid` crashed with a bare-argv unpack. Importing a helper must not execute a
    # CLI. Behaviour of the command line itself is unchanged.
    _src, _x0, _y0, _x1, _y1, _scale, _out = sys.argv[1:8]
    crop(_src, int(_x0), int(_y0), int(_x1), int(_y1), float(_scale), _out)
