#!/usr/bin/env python3
"""s_crop.py — crop + Lanczos-upscale a region of a photograph, stackup lane (L4).

Usage: s_crop.py <image> <x0> <y0> <x1> <y1> <scale> <out.png>
Source-image pixel coordinates. NOTHING is enhanced beyond the resample: no
sharpening, no contrast stretch, no gamma. What is read off the crop is what is
in the photograph. Any enhanced variant must be produced by s_enhance.py and
labelled as enhanced wherever it is quoted.
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
