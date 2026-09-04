#!/usr/bin/env python3
"""b_crop.py — crop and upscale a region of a photograph for marking-reading.

Usage: b_crop.py <image> <x0> <y0> <x1> <y1> <scale> <out.png>
Coordinates are in the SOURCE image's pixels. Nothing is enhanced beyond a
Lanczos resample: no sharpening, no contrast stretch, so what is read off the
crop is what is in the photograph.
"""
import sys
from PIL import Image

src, x0, y0, x1, y1, scale, out = sys.argv[1:8]
x0, y0, x1, y1 = (int(v) for v in (x0, y0, x1, y1))
scale = float(scale)
im = Image.open(src).crop((x0, y0, x1, y1))
im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
im.save(out)
print(f"{out} {im.size} from {src}[{x0}:{x1},{y0}:{y1}] x{scale}")
