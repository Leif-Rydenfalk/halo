#!/usr/bin/env python3
"""m_overlay_all.py -- draw EVERYTHING this lane found back onto the photograph.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.
SIDE NAMING: FRONT = the COMPONENT side. O'Flynn's `backside-fullres.jpeg` IS it.

WHY.  Ninety-five rows with positions and a plateau statistic do not say whether
row 47 is a solder pad or a highlight on a solder fillet.  No residual can answer
that.  Looking is the only instrument for it, and in this lane looking has caught
three defects that every numeric check passed: the half-max detector following the
contact shadow, a resolution probe scoring 0.992 of Nyquist on empty background,
and a package size that was a measurement of my own ROI.

Draws: the fitted outer outline, the segmented hole, all bright features (M07),
the blue-bodied packages (M08), the nRF control box and the UWB can rectangle.
Writes one whole-board view plus NATIVE-RESOLUTION tiles, because a downsampled
overlay cannot answer the question it is being asked.
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import m_dark_packages as D

ap = argparse.ArgumentParser()
ap.add_argument("--out-dir", required=True)
ap.add_argument("--tiles", type=int, default=6)
a = ap.parse_args()
os.makedirs(a.out_dir, exist_ok=True)
M = os.path.join(HERE, "..", "metrology")

lum, board, outer, origin, ppm, spath, fit = D.board_frame(
    os.path.join(M, "c_register-fit-boardscale.json"))
comps = json.load(open(os.path.join(M, "components-front.json")))
darks = json.load(open(os.path.join(M, "dark-packages-front.json")))
print("m_overlay_all.py -- inputs:")
print(f"  image   {os.path.basename(spath)}  scale {ppm:.3f} px/mm")
print(f"  bright  {comps['n_components']} from components-front.json "
      f"(run {comps['run_utc']})")
print(f"  dark    {darks['n']} from dark-packages-front.json (run {darks['run_utc']})")
print(f"  origin  ({origin[0]:.1f}, {origin[1]:.1f}) px")

im = Image.open(spath).convert("RGB")
d = ImageDraw.Draw(im)
d.line([tuple(p) for p in outer] + [tuple(outer[0])], fill=(0, 255, 0), width=6)
for i, c in enumerate(comps["components"]):
    x, y = c["cx"], c["cy"]
    col = (255, 40, 40) if c["size_verdict"] == "SOUND" else (255, 170, 0)
    r = 14
    d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=4)
    d.text((x + r + 3, y - r), str(i), fill=col)
for c in darks["packages"]:
    L2, W2 = c["long_px"] / 2, c["short_px"] / 2
    th = math.radians(c["angle_deg"])
    pts = [(c["cx"] + dx * math.cos(th) - dy * math.sin(th),
            c["cy"] + dx * math.sin(th) + dy * math.cos(th))
           for dx, dy in ((-L2, -W2), (L2, -W2), (L2, W2), (-L2, W2))]
    d.line(pts + [pts[0]], fill=(255, 0, 255), width=7)
d.rectangle([1040, 660, 1400, 990], outline=(0, 220, 255), width=5)
d.rectangle([730, 2340, 1500, 2830], outline=(255, 255, 0), width=5)
whole = os.path.join(a.out_dir, "ALL-whole.png")
im.resize((im.width // 3, im.height // 3), Image.LANCZOS).save(whole)
print(f"  wrote {whole}")

ys, xs = np.nonzero(board)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
n = int(math.ceil(math.sqrt(a.tiles)))
tw, th_ = (x1 - x0) // n, (y1 - y0) // n
k = 0
for iy in range(n):
    for ix in range(n):
        if k >= a.tiles:
            break
        bx = x0 + ix * tw; by = y0 + iy * th_
        t = im.crop((bx, by, bx + tw, by + th_))
        p = os.path.join(a.out_dir, f"ALL-tile-{iy}{ix}.png")
        t.save(p)
        print(f"  wrote {p}  native crop ({bx},{by})-({bx+tw},{by+th_})")
        k += 1
