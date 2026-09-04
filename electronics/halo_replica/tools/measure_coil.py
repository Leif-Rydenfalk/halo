#!/usr/bin/env python3
"""Measure the NFC coil in oflynn-frontside-26mm-cropped.jpg.
Visual inspection at 2x (scratchpad/crop_centre.png) shows the coil is WOUND ROUND
MAGNET WIRE with individually resolvable turns - not a laser-structured trace.
That contradicts docs/REFERENCE-TEARDOWN.md s2.3, which lists ANT2 as an LDS coil.
This script measures what the photograph actually contains.

Datum as calib_fit.py: 787.18 px = 26 mm APPROXIMATE. Ratios are datum-free."""
import numpy as np, os, json
from PIL import Image
IMG = os.path.expanduser("~/dev/ce-workshop/ce-designs/halo/images/airtag/oflynn-frontside-26mm-cropped.jpg")
rgb = np.asarray(Image.open(IMG).convert("RGB")).astype(float)
lum = rgb.mean(2)
H, W, _ = rgb.shape
CX = CY = 393.50; R_DATUM_PX = 393.59; PXMM = 2*R_DATUM_PX/26.0

# copper: R clearly above B, and not blown out
R,G,B = rgb[...,0], rgb[...,1], rgb[...,2]
copper = (R - B > 28) & (R > 90) & (lum < 250)

ys, xs = np.mgrid[0:H,0:W]
rad = np.hypot(ys-CY, xs-CX)

print(f"scale {PXMM:.4f} px/mm (datum 26 mm APPROXIMATE)\n")
print("radial histogram of copper-coloured pixels (the winding), 2 px bins:")
prof=[]
for r0 in np.arange(120, 260, 2):
    m = (rad>=r0)&(rad<r0+2)
    frac = copper[m].mean() if m.sum() else 0
    prof.append((r0+1, frac, m.sum()))
for r0,f,n in prof:
    bar = "#"*int(f*60)
    print(f"  r={r0:5.0f} px {r0/PXMM:6.3f} mm  frac={f:5.3f} {bar}")

fr = np.array([f for _,f,_ in prof]); rr = np.array([r for r,_,_ in prof])
band = fr > 0.25
if band.sum() >= 2:
    r_in, r_out = rr[band].min()-1, rr[band].max()+1
    print(f"\nCOIL WINDING BAND (copper fraction > 0.25):")
    print(f"  inner r {r_in:.1f} px = {r_in/PXMM:.3f} mm   ->  ID {2*r_in/PXMM:.3f} mm")
    print(f"  outer r {r_out:.1f} px = {r_out/PXMM:.3f} mm   ->  OD {2*r_out/PXMM:.3f} mm")
    print(f"  radial width {(r_out-r_in)/PXMM:.3f} mm  ({r_out-r_in:.1f} px)")
    print(f"  ratios to datum dia: ID {2*r_in/(2*R_DATUM_PX):.4f}  OD {2*r_out/(2*R_DATUM_PX):.4f}")
    json.dump({"method":"copper chroma R-B>28 radial histogram",
               "datum":"787.18 px = 26 mm APPROXIMATE (O'Flynn)","px_per_mm":PXMM,
               "coil_inner_r_px":float(r_in),"coil_outer_r_px":float(r_out),
               "coil_ID_mm":float(2*r_in/PXMM),"coil_OD_mm":float(2*r_out/PXMM),
               "coil_radial_width_mm":float((r_out-r_in)/PXMM),
               "coil_ID_ratio_of_board_dia":float(2*r_in/(2*R_DATUM_PX)),
               "coil_OD_ratio_of_board_dia":float(2*r_out/(2*R_DATUM_PX)),
               "construction":"WOUND ROUND MAGNET WIRE - individual turns resolvable at 2x. NOT an LDS trace."},
              open("metrology/nfc-coil-measured.json","w"), indent=2)
else:
    print("\nCOIL BAND: CANNOT DETERMINE - no radius reached 25% copper coverage")
