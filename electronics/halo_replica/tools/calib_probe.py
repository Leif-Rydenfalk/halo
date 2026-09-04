#!/usr/bin/env python3
"""Exploratory: where IS the board edge in oflynn-frontside-26mm-cropped.jpg?
No assumption that the crop is tight. Prints raw profiles for a human to read."""
import numpy as np
from PIL import Image
import sys, os

IMG = os.path.expanduser("~/dev/ce-workshop/ce-designs/halo/images/airtag/oflynn-frontside-26mm-cropped.jpg")
im = Image.open(IMG).convert("L")
a = np.asarray(im).astype(float)
H, W = a.shape
print(f"image {W}x{H}  mean={a.mean():.1f} min={a.min()} max={a.max()}")

# horizontal scan through vertical centre, and vertical through horizontal centre
for name, prof in (("row y=H/2", a[H//2, :]), ("col x=W/2", a[:, W//2])):
    print(f"\n--- {name} --- (luma every 8 px, first 120 and last 120)")
    print("head:", " ".join(f"{int(v):3d}" for v in prof[:120:8]))
    print("tail:", " ".join(f"{int(v):3d}" for v in prof[-120::8]))

# corner luma: if the crop is tight to a circle, corners are background
print("\ncorner 20x20 means:",
      f"TL={a[:20,:20].mean():.0f} TR={a[:20,-20:].mean():.0f}",
      f"BL={a[-20:,:20].mean():.0f} BR={a[-20:,-20:].mean():.0f}")
print("edge-strip means: top", f"{a[:6,:].mean():.0f}", "bot", f"{a[-6:,:].mean():.0f}",
      "left", f"{a[:,:6].mean():.0f}", "right", f"{a[:,-6:].mean():.0f}")

# radial darkness profile from geometric centre
cy, cx = H/2.0, W/2.0
ys, xs = np.mgrid[0:H, 0:W]
r = np.hypot(ys-cy, xs-cx)
print("\nradial mean luma, r in px (bin=4):")
for r0 in range(0, int(min(H,W)/2)+4, 8):
    m = (r >= r0) & (r < r0+8)
    if m.sum(): print(f"  r={r0:3d}-{r0+8:3d}  mean={a[m].mean():6.1f}  n={m.sum()}")
