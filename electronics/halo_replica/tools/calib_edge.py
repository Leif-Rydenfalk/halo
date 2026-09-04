#!/usr/bin/env python3
"""Find (a) the outer edge of the dark PCB and (b) the thin drawn circle overlay,
in oflynn-frontside-26mm-cropped.jpg. Per-angle ray casting, not a global fit,
so the spread across angles IS the uncertainty."""
import numpy as np, os
from PIL import Image
IMG = os.path.expanduser("~/dev/ce-workshop/ce-designs/halo/images/airtag/oflynn-frontside-26mm-cropped.jpg")
a = np.asarray(Image.open(IMG).convert("L")).astype(float)
H, W = a.shape
cy, cx = (H-1)/2.0, (W-1)/2.0

def ray(theta, rmax, step=0.25):
    rs = np.arange(0, rmax, step)
    ys = cy + rs*np.sin(theta); xs = cx + rs*np.cos(theta)
    ok = (ys>=0)&(ys<H-1)&(xs>=0)&(xs<W-1)
    rs, ys, xs = rs[ok], ys[ok], xs[ok]
    y0=ys.astype(int); x0=xs.astype(int); fy=ys-y0; fx=xs-x0
    v = (a[y0,x0]*(1-fy)*(1-fx) + a[y0+1,x0]*fy*(1-fx)
       + a[y0,x0+1]*(1-fy)*fx + a[y0+1,x0+1]*fy*fx)
    return rs, v

# --- full radial mean out to the corner, fine bins ---
ys,xs = np.mgrid[0:H,0:W]; R = np.hypot(ys-cy, xs-cx)
print("full radial mean luma (bin=4 px):")
line=[]
for r0 in range(150, int(np.hypot(H/2,W/2))+4, 4):
    m=(R>=r0)&(R<r0+4)
    if m.sum()>50: line.append(f"{r0}:{a[m].mean():.0f}")
print("  " + "  ".join(line))

# --- per-angle: last radius at which the ray is still "dark board" ---
DARK = 150.0
edges=[]; circ=[]
for k in range(720):
    th = 2*np.pi*k/720
    rs, v = ray(th, 560)
    dark = v < DARK
    # outer board edge: last dark sample before a sustained bright run (>=12 px bright)
    idx=None
    for i in range(len(v)-1, 40, -1):
        if dark[i]:
            # require 12px (48 samples) of bright beyond, within bounds
            tail = v[i+1:i+49]
            if len(tail)>=20 and (tail>DARK).mean() > 0.9:
                idx=i; break
    if idx is not None: edges.append((th, rs[idx]))
    # drawn circle: a narrow dark dip sitting inside an otherwise bright region
    if idx is not None:
        beyond = slice(idx+1, len(v))
        vb = v[beyond]; rb = rs[beyond]
        if len(vb) > 40:
            j = int(np.argmin(vb))
            # a real thin line: local min well below its neighbourhood, and narrow
            lo = max(0,j-24); hi = min(len(vb), j+25)
            nb = np.concatenate([vb[lo:max(lo,j-6)], vb[min(hi,j+7):hi]])
            if len(nb)>10 and vb[j] < nb.mean() - 35 and vb[j] < 215:
                circ.append((th, rb[j]))

E = np.array([r for _,r in edges]); C = np.array([r for _,r in circ])
print(f"\nBOARD OUTER EDGE from {len(E)} of 720 rays:")
print(f"  median {np.median(E):.2f} px   mean {E.mean():.2f}   sd {E.std():.2f}"
      f"   p5 {np.percentile(E,5):.2f}  p95 {np.percentile(E,95):.2f}  min {E.min():.1f} max {E.max():.1f}")
if len(C)>20:
    print(f"\nDRAWN CIRCLE candidate from {len(C)} of 720 rays:")
    print(f"  median {np.median(C):.2f} px   sd {C.std():.2f}"
          f"   p5 {np.percentile(C,5):.2f}  p95 {np.percentile(C,95):.2f}")
else:
    print(f"\nDRAWN CIRCLE: only {len(C)} hits — NOT established")
