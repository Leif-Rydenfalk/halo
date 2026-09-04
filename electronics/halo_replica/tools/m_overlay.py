#!/usr/bin/env python3
"""m_overlay.py -- draw a measured r(theta) back onto the photograph.

L1 metrology lane.  A number you have not LOOKED at is a number you have not
checked.  Reads the JSON that m_board_outline.py wrote and marks every measured
edge point, so a detector that is following a shadow instead of the board is
visible rather than merely suspected.
"""
import argparse, json, math, os
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

ap = argparse.ArgumentParser()
ap.add_argument("json")
ap.add_argument("--out", required=True)
ap.add_argument("--zoom", type=int, default=3)
ap.add_argument("--pad", type=int, default=40)
a = ap.parse_args()

d = json.load(open(a.json))
im = Image.open(os.path.join(ROOT, d["image"])).convert("RGB")
print(f"m_overlay.py -- inputs: {a.json} -> {d['image']}, zoom {a.zoom}x")

pts = {}
for key, col in (("outer", (255, 0, 0)), ("inner", (0, 200, 255))):
    if not d.get(key):
        continue
    cx, cy = d[key]["fitted_centre_px"]
    pts[key] = (col, [(cx + r * math.cos(math.radians(t)), cy + r * math.sin(math.radians(t)))
                      for t, r in d[key]["r_theta_deg_px"]], (cx, cy))
    print(f"  {key}: {len(d[key]['r_theta_deg_px'])} points, centre ({cx:.1f},{cy:.1f})")

allp = [p for _, ps, _ in pts.values() for p in ps]
x0 = int(min(p[0] for p in allp)) - a.pad; x1 = int(max(p[0] for p in allp)) + a.pad
y0 = int(min(p[1] for p in allp)) - a.pad; y1 = int(max(p[1] for p in allp)) + a.pad
z = a.zoom
crop = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * z, (y1 - y0) * z), Image.LANCZOS)
dr = ImageDraw.Draw(crop)
for key, (col, ps, c) in pts.items():
    for px, py in ps:
        X = (px - x0) * z; Y = (py - y0) * z
        dr.ellipse([X - 1.6, Y - 1.6, X + 1.6, Y + 1.6], fill=col)
    X = (c[0] - x0) * z; Y = (c[1] - y0) * z
    dr.line([X - 12, Y, X + 12, Y], fill=col, width=2)
    dr.line([X, Y - 12, X, Y + 12], fill=col, width=2)
crop.save(a.out)
print(f"  wrote {a.out}  ({crop.width}x{crop.height}, crop {x0},{y0},{x1},{y1})")
