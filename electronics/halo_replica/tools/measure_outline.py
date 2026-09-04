#!/usr/bin/env python3
"""MEASURE the annular outline of the AirTag MLB from oflynn-frontside-26mm-cropped.jpg.
Datum: O'Flynn's drawn marker circle, fitted at r=393.59 px, centre = frame centre,
declared by him as "~26 mm". The tilde is HIS - see docs/REFERENCE-TEARDOWN.md s7,
which lists the exact bare-board diameter as CANNOT DETERMINE. So:
  - RELATIVE numbers (ratios of the datum) are good to the fit residual, ~0.1%
  - ABSOLUTE mm carry a systematic from the 26 mm datum that this script CANNOT bound.
Both are printed. A ratio and a millimetre are not the same kind of number here.

Two independent quantities are measured, each by per-angle ray casting so the
SPREAD ACROSS ANGLES is the reported uncertainty rather than a fitted illusion:
  1. outer edge of the dark PCB  (does it coincide with O'Flynn's circle?)
  2. inner edge of the centre hole (the annulus - the thing halo_rev_a does not have)
"""
import numpy as np, os, json
from PIL import Image
IMG = os.path.expanduser("~/dev/ce-workshop/ce-designs/halo/images/airtag/oflynn-frontside-26mm-cropped.jpg")
a = np.asarray(Image.open(IMG).convert("L")).astype(float)
H, W = a.shape
CX = CY = 393.50            # from tools/calib_fit.py, stable over 3 thresholds
R_DATUM_PX = 393.59
D_DATUM_MM = 26.0           # O'Flynn's "~26 mm", APPROXIMATE
PXMM = (2*R_DATUM_PX) / D_DATUM_MM

def sample(th, rs):
    ys = CY + rs*np.sin(th); xs = CX + rs*np.cos(th)
    ok = (ys>=0)&(ys<H-1)&(xs>=0)&(xs<W-1)
    rs2, ys, xs = rs[ok], ys[ok], xs[ok]
    y0=ys.astype(int); x0=xs.astype(int); fy=ys-y0; fx=xs-x0
    v = (a[y0,x0]*(1-fy)*(1-fx)+a[y0+1,x0]*fy*(1-fx)
        +a[y0,x0+1]*(1-fy)*fx+a[y0+1,x0+1]*fy*fx)
    return rs2, v

def report(name, vals, unit_note=""):
    v = np.array(vals)
    if len(v) < 20:
        print(f"{name}: CANNOT DETERMINE - only {len(v)} of 720 rays gave a reading"); return None
    med = float(np.median(v)); iqr = float(np.percentile(v,75)-np.percentile(v,25))
    print(f"{name}:  n={len(v)}/720 rays")
    print(f"    median {med:8.2f} px = {med/PXMM:7.3f} mm   (radius)")
    print(f"    diameter {2*med/PXMM:7.3f} mm     ratio to datum dia = {2*med/(2*R_DATUM_PX):.4f}")
    print(f"    spread: IQR {iqr:.2f} px = {iqr/PXMM:.3f} mm | p5 {np.percentile(v,5):.1f} "
          f"p95 {np.percentile(v,95):.1f} px | sd {v.std():.2f} px")
    return {"n_rays":len(v),"median_px":med,"median_mm":med/PXMM,
            "diameter_mm":2*med/PXMM,"ratio_to_datum_dia":2*med/(2*R_DATUM_PX),
            "iqr_px":iqr,"p5_px":float(np.percentile(v,5)),"p95_px":float(np.percentile(v,95)),
            "sd_px":float(v.std())}

# ---- 1. OUTER EDGE OF DARK PCB: walking inward from the datum, first sustained dark ----
outer=[]
for k in range(720):
    th = 2*np.pi*k/720
    rs, v = sample(th, np.arange(R_DATUM_PX+6, 200, -0.25))
    for i in range(len(v)-30):
        if v[i] < 150 and (v[i:i+30] < 175).mean() > 0.85:   # sustained dark, i.e. board not shell
            outer.append(rs[i]); break

# ---- 2. INNER EDGE (centre hole): walking OUTWARD from centre, first sustained dark ----
inner=[]
for k in range(720):
    th = 2*np.pi*k/720
    rs, v = sample(th, np.arange(20, 330, 0.25))
    for i in range(len(v)-40):
        if v[i] < 150 and (v[i:i+40] < 175).mean() > 0.85:
            inner.append(rs[i]); break

print(f"SCALE BASIS: {2*R_DATUM_PX:.2f} px = {D_DATUM_MM} mm (APPROXIMATE, O'Flynn's tilde)")
print(f"             {PXMM:.4f} px/mm  =  {1/PXMM:.6f} mm/px\n")
o = report("OUTER EDGE of dark PCB", outer)
print()
i_ = report("INNER EDGE (centre hole / bright core)", inner)
print(f"\nDATUM CHECK - does O'Flynn's drawn circle sit on the board edge?")
if o: print(f"    drawn circle r=393.59 px, measured PCB outer r={o['median_px']:.2f} px"
            f"  ->  delta {o['median_px']-393.59:+.2f} px = {(o['median_px']-393.59)/PXMM:+.3f} mm")
json.dump({"scale":{"datum_source":"oflynn-frontside-26mm-cropped.jpg, drawn marker circle",
                    "datum_diameter_mm":D_DATUM_MM,"datum_is_approximate":True,
                    "datum_caveat":"O'Flynn wrote '~26 mm'. Exact bare-board diameter is CANNOT DETERMINE (REFERENCE-TEARDOWN.md s7). Absolute mm below inherit that systematic; ratios do not.",
                    "datum_radius_px":R_DATUM_PX,"px_per_mm":PXMM,"mm_per_px":1/PXMM,
                    "centre_px":[CX,CY]},
           "outer_edge":o,"inner_hole":i_},
          open("metrology/outline-measured.json","w"), indent=2)
