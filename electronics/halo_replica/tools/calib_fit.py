#!/usr/bin/env python3
"""Fit O'Flynn's drawn marker circle in oflynn-frontside-26mm-cropped.jpg.
The crop CLIPS the board, so the frame is NOT the datum - the drawn circle is.
Selection: a pixel is a candidate only if it is DARK while its 15px neighbourhood
MEDIAN is the white shell. That excludes the PCB entirely (PCB ground is never white).
Fit: Kasa algebraic + IRLS with a hard 2px band. Residuals printed, not asserted."""
import numpy as np, os, json
from PIL import Image
from scipy import ndimage as ndi
IMG = os.path.expanduser("~/dev/ce-workshop/ce-designs/halo/images/airtag/oflynn-frontside-26mm-cropped.jpg")
a = np.asarray(Image.open(IMG).convert("L")).astype(float)
H, W = a.shape

med15 = ndi.median_filter(a, size=15)
for DARK, GROUND in ((190,225),(200,230),(180,220)):
    cand = (a < DARK) & (med15 > GROUND)
    ys, xs = np.nonzero(cand)
    if len(ys) < 200: 
        print(f"DARK<{DARK} GROUND>{GROUND}: only {len(ys)} px - skipped"); continue

    def kasa(x, y, w):
        A = np.stack([x, y, np.ones_like(x)], 1) * w[:,None]
        b = (x*x + y*y) * w
        sol, *_ = np.linalg.lstsq(A, b, rcond=None)
        cx, cy = sol[0]/2, sol[1]/2
        return cx, cy, np.sqrt(max(sol[2] + cx*cx + cy*cy, 1e-9))

    x = xs.astype(float); y = ys.astype(float); w = np.ones_like(x)
    cx, cy, r = kasa(x, y, w)
    for it in range(30):
        d = np.abs(np.hypot(x-cx, y-cy) - r)
        band = max(2.0, 3.0*1.4826*np.median(d)) if it < 8 else 2.0
        w = (d < band).astype(float)
        if w.sum() < 100: break
        cx, cy, r = kasa(x, y, w)
    keep = w > 0
    if keep.sum() < 100:
        print(f"DARK<{DARK} GROUND>{GROUND}: collapsed, {int(keep.sum())} inliers"); continue
    res = np.hypot(x[keep]-cx, y[keep]-cy) - r
    th = np.degrees(np.arctan2(y[keep]-cy, x[keep]-cx)) % 360
    hist = np.histogram(th, bins=12, range=(0,360))[0]
    print(f"\nDARK<{DARK} GROUND>{GROUND}  candidates {len(x)}")
    print(f"  centre=({cx:.2f},{cy:.2f})  r={r:.2f} px  inliers {int(keep.sum())}"
          f"  res sd {res.std():.3f} px  p95|res| {np.percentile(np.abs(res),95):.2f}")
    print(f"  30deg angular bins: {' '.join(map(str,hist))}")
    print(f"  offset from frame centre ({(W-1)/2},{(H-1)/2}): ({cx-(W-1)/2:+.2f},{cy-(H-1)/2:+.2f})")
    if DARK == 190:
        json.dump({"cx_px":cx,"cy_px":cy,"r_px":r,"inliers":int(keep.sum()),
                   "residual_sd_px":float(res.std()),
                   "p95_abs_res_px":float(np.percentile(np.abs(res),95)),
                   "angular_bins_30deg":hist.tolist(),
                   "image":os.path.basename(IMG),"image_w":W,"image_h":H,
                   "selection":"a<190 and median15>225"},
                  open("metrology/drawn-circle-fit.json","w"), indent=2)
