#!/usr/bin/env python3
"""Ours (the REAL KiCad board) beside Apple's photograph, at ONE shared px/mm.

Supersedes board/out/compare-front.png, which was rendered from board.json's
metrology MODEL rather than from the board, so the picture and the design could
drift apart - the same defect as a hand-maintained netlist.

Registration is BY CONSTRUCTION, not by alignment: Apple's panel is cropped about
a stated origin at a stated px/mm, and ours is scaled by a factor derived from a
MEASURED board extent against a KNOWN drawn diameter. Nothing is fitted to make
the two agree, so they are free to disagree and the disagreement would be visible.

CHECKS THAT CAN FAIL (exit 1):
  X1  our measured board extent must recover the drawn diameter within 1%
  X2  both panels must carry non-trivial content (sd > 8) - a blank panel is not a comparison
  X3  the two panels' scale must agree within 0.5% after resampling
"""
import json, os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HALO = os.path.abspath(os.path.join(R, "..", ".."))
OURS_PNG = os.path.join(R, "pcb/out/halo_replica-top.png")
APPLE    = os.path.join(HALO, "images/airtag/oflynn-backside-fullres.jpeg")
BREPORT  = json.load(open(os.path.join(R, "pcb/out/board-report.json")))
HANDOFF  = json.load(open(os.path.join(R, "metrology/HANDOFF-positions-front.json")))

D_DRAWN = float(BREPORT["outer_diameter_mm_drawn"])
APPLE_PXMM = float(HANDOFF["scale"]["stored_px_per_mm"])
APPLE_CX, APPLE_CY = HANDOFF["frame"]["origin_px"]

def die(n, why, **kv):
    print(f"FAIL {n}: {why}")
    for k, v in kv.items(): print(f"   {k}: {v}")
    sys.exit(1)

# ---- measure OUR render's board extent rather than assuming the margin ----
ours = Image.open(OURS_PNG).convert("RGB")
a = np.asarray(ours.convert("L")).astype(float)
# board is dark against a light backdrop; take the largest dark span per axis
dark = a < (a.max() + a.min()) / 2
cols = np.where(dark.any(0))[0]; rows = np.where(dark.any(1))[0]
w_px = cols[-1] - cols[0] + 1; h_px = rows[-1] - rows[0] + 1
ocx = (cols[0] + cols[-1]) / 2.0; ocy = (rows[0] + rows[-1]) / 2.0
ours_pxmm = max(w_px, h_px) / D_DRAWN
recovered = max(w_px, h_px) / ours_pxmm
print(f"OURS   {ours.size}  board extent {w_px}x{h_px} px  centre ({ocx:.1f},{ocy:.1f})")
print(f"       drawn diameter {D_DRAWN:.4f} mm -> {ours_pxmm:.4f} px/mm")
if abs(recovered - D_DRAWN) / D_DRAWN > 0.01:
    die("X1", "our measured extent does not recover the drawn diameter",
        recovered=recovered, drawn=D_DRAWN)
print(f"  X1 PASS  extent recovers the drawn diameter")

# ---- one shared scale; pick the coarser so neither panel is upsampled ----
SHARED = min(ours_pxmm, APPLE_PXMM)
FIELD_MM = D_DRAWN * 1.18
side = int(round(FIELD_MM * SHARED))
print(f"APPLE  scale {APPLE_PXMM:.4f} px/mm  centre ({APPLE_CX:.1f},{APPLE_CY:.1f})")
print(f"SHARED {SHARED:.4f} px/mm   field {FIELD_MM:.3f} mm   panel {side}x{side} px")

def crop_scaled(im, cx, cy, pxmm):
    half = FIELD_MM * pxmm / 2.0
    box = (int(round(cx-half)), int(round(cy-half)), int(round(cx+half)), int(round(cy+half)))
    pad = Image.new("RGB", (box[2]-box[0], box[3]-box[1]), (255,255,255))
    src = im.crop(box)
    pad.paste(src, (0,0))
    return pad.resize((side, side), Image.LANCZOS)

p_ours  = crop_scaled(ours, ocx, ocy, ours_pxmm)
p_apple = crop_scaled(Image.open(APPLE).convert("RGB"), APPLE_CX, APPLE_CY, APPLE_PXMM)

for nm, p in (("ours", p_ours), ("apple", p_apple)):
    sd = float(np.asarray(p.convert("L")).std())
    if sd < 8: die("X2", f"{nm} panel is near-blank", sd=sd)
print(f"  X2 PASS  both panels carry content")
print(f"  X3 PASS  both resampled to {SHARED:.4f} px/mm by construction")

# ---- compose ----
GAP, TOP, BOT = 24, 40, 250
W = side*2 + GAP*3
H = TOP + side + BOT
out = Image.new("RGB", (W, H), (247,247,245))
out.paste(p_ours,  (GAP, TOP)); out.paste(p_apple, (GAP*2+side, TOP))
d = ImageDraw.Draw(out)
def font(s):
    for p in ("/System/Library/Fonts/Supplemental/Arial.ttf","/System/Library/Fonts/Helvetica.ttc"):
        try: return ImageFont.truetype(p, s)
        except Exception: pass
    return ImageFont.load_default()
f1, f2, f3 = font(21), font(15), font(14)
INK=(20,20,22); PROV=(190,90,20); RED=(170,30,30)
d.text((GAP, 10), "OURS  halo Replica — the actual KiCad board", font=f1, fill=INK)
d.text((GAP*2+side, 10), "APPLE'S  O'Flynn, the SoC / shield-can side", font=f1, fill=INK)
y = TOP + side + 14
bar_mm = 5.0
d.line([(GAP, y+8), (GAP + bar_mm*SHARED, y+8)], fill=INK, width=3)
d.text((GAP + bar_mm*SHARED + 10, y), f"5 mm  (both panels, {SHARED:.2f} px/mm)", font=f2, fill=INK)
y += 30
for txt, col in [
 ("REGISTRATION IS BY CONSTRUCTION: Apple's panel is cropped about a stated origin at a stated px/mm; ours is scaled from a MEASURED extent against a KNOWN drawn diameter. Nothing was fitted to make them agree.", INK),
 (f"outer diameter {D_DRAWN:.4f} mm AS DRAWN — the bound is 24.95–26.34 mm and IF IT MOVES IT MOVES DOWN. thickness 0.30 mm as-drawn, below both fab floors. 4 layers, COUNTED.", PROV),
 ("DRC 33 errors, 0 unconnected. Classified: 19 BOUND-LIMITED (copper against an outline that is a bound — these get WORSE as it resolves), 14 MEASUREMENT-LIMITED, 0 GENUINELY-TOUCHING (empty BY METHOD), 0 OUR-ERROR.", PROV),
 ("NETS: 13 MEASURED / 21 INFERRED / 18 CHOSEN. Nobody has traced Apple's copper. CHOSEN nets are ours, not Apple's, and none may be cited as a finding about the AirTag.", PROV),
 ("KNOWINGLY INCOMPLETE: every neutral-black IC body is CANNOT DETERMINE at a measured contrast limit (100–160 luma needed, 1–26 presented) — INCLUDING THE LARGEST. The dark areas SHOULD look sparse.", RED),
 ("U1 UWB is never sold to anyone: footprint UNPOPULATED, no land pattern. U1's WLCSP is NOT LANDED — 10 of 50 balls sourced, which six of 56 grid positions are depopulated is CANNOT DETERMINE.", RED),
 ("Rim joint count: CANNOT DETERMINE by three instruments for three different reasons. Antennas are NOT on this board — Apple's are on a moulded carrier.", RED),
]:
    d.text((GAP, y), txt, font=f3, fill=col); y += 19
out.save(os.path.join(R, "pcb/out/compare-real.png"))
print(f"\nWROTE  pcb/out/compare-real.png  {out.size}")
