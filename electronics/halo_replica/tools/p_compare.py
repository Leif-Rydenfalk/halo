#!/usr/bin/env python3
"""p_compare.py -- THE SIDE-BY-SIDE. Our render beside Apple's photograph at MATCHED
SCALE and MATCHED ORIENTATION, plus an outline overlay on the photograph itself.

Lane L5 (BOARD BUILD), halo Replica.  This picture is what this lane is judged on.
Exit code IS the verdict: 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

Three panels:
  1  OURS      -- rendered from board/board.json, no caption, on the photo's own paper
  2  APPLE'S   -- the FCC internal photo, cropped to the board, resampled to the SAME
                  millimetres-per-pixel as panel 1
  3  OVERLAY   -- our outline drawn in cyan ON Apple's photograph. This is the panel
                  that shows disagreement; the first two only show resemblance.

CONTROLS
  X1 scale-match  -- both panels are measured back off the finished image and their
                     2 x mean board radius in mm must agree to 1%. Two pictures that
                     merely LOOK the same size prove nothing.
  X2 non-blank    -- the finished PNG is read back; blank or near-blank is a FAIL.
  X3 mis-registration control -- --break-rotation N rotates our outline by N degrees
                     before overlaying. The residual MUST get worse. A comparison whose
                     number does not move when the alignment is destroyed is measuring
                     nothing.
  X4 residual     -- the overlay reports the RMS radial disagreement in mm between our
                     drawn outline and the photograph's own silhouette, per ray. This
                     is a number, not an adjective.
"""
import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

PASS, FAIL, CANNOT = 0, 1, 2
HERE = os.path.dirname(os.path.abspath(__file__))
REPL = os.path.dirname(HERE)
BOARD_DIR = os.path.join(REPL, "board")
ROOT = os.path.dirname(os.path.dirname(REPL))
BG = (246, 245, 242)
INK = (26, 26, 28)
PROV = (208, 92, 24)
CYAN = (0, 224, 232)


def say(*a):
    print(*a, file=sys.stderr)


def font(sz, bold=False):
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
              "/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def board_mask(a_l):
    """dark, largest component, holes filled -> the board silhouette"""
    m = a_l < 120
    lab, n = ndimage.label(m)
    if n == 0:
        return None
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    return ndimage.binary_fill_holes(lab == (int(np.argmax(sizes)) + 1))


def radial(mask, n=720):
    ys, xs = np.nonzero(mask)
    cx, cy = xs.mean(), ys.mean()
    th = np.deg2rad(np.arange(n) * 360.0 / n)
    rr = np.arange(1.0, 0.75 * max(mask.shape), 0.5)
    R, T = np.meshgrid(rr, th)
    X = np.rint(cx + R * np.cos(T)).astype(int)
    Y = np.rint(cy - R * np.sin(T)).astype(int)
    ok = (X >= 0) & (Y >= 0) & (X < mask.shape[1]) & (Y < mask.shape[0])
    hit = np.zeros_like(R, dtype=bool)
    hit[ok] = mask[Y[ok], X[ok]]
    r = np.array([rr[np.nonzero(h)[0][-1]] if h.any() else np.nan for h in hit])
    return cx, cy, np.rad2deg(th), r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", default=os.path.join(ROOT, "images", "airtag",
                                                    "fcc-BCGA2187-internal-photo-6.jpg"))
    ap.add_argument("--photo-box", nargs=4, type=int, default=[660, 400, 1250, 960])
    ap.add_argument("--photo-px-per-mm", type=float, default=15.887545712881764)
    ap.add_argument("--photo-scale-basis",
                    default="photo6 BOTTOM steel rule, 93 ticks, linear resid sd 0.573 px (L1 scale-field.json)")
    ap.add_argument("--px-per-mm", type=float, default=48.0, help="the shared scale of the montage")
    ap.add_argument("--board", default=os.path.join(BOARD_DIR, "board.json"))
    ap.add_argument("--break-rotation", type=float, default=0.0,
                    help="X3: rotate OUR outline by this many degrees before overlaying. "
                         "The residual must get worse. Watch the control go red.")
    ap.add_argument("--out", default=os.path.join(BOARD_DIR, "out", "compare-front.png"))
    a = ap.parse_args()

    say("INPUT")
    say(f"  photo             {os.path.relpath(a.photo, ROOT)}")
    say(f"  photo crop        {a.photo_box}")
    say(f"  photo px/mm       {a.photo_px_per_mm}   basis: {a.photo_scale_basis}")
    say(f"  montage px/mm     {a.px_per_mm}  (BOTH panels resampled to this)")
    say(f"  board model       {os.path.relpath(a.board, ROOT)}")
    if a.break_rotation:
        say(f"  X3 BREAK          our outline rotated {a.break_rotation} deg on purpose")
    say("")

    # ---- panel 1: render ours, uncaptioned, at the montage scale
    ours_png = os.path.join(BOARD_DIR, "out", ".compare-ours.png")
    r = subprocess.run([sys.executable, os.path.join(HERE, "p_render.py"),
                        "--board", a.board, "--px-per-mm", str(a.px_per_mm),
                        "--no-caption", "--out", ours_png],
                       capture_output=True, text=True)
    if r.returncode != 0:
        say("p_render.py refused; the montage inherits its verdict:")
        say(r.stderr.strip()[-800:])
        sys.exit(r.returncode)
    ours = Image.open(ours_png).convert("RGB")

    # ---- panel 2: the photo, resampled to the SAME px/mm
    ph = Image.open(a.photo).convert("RGB").crop(tuple(a.photo_box))
    f = a.px_per_mm / a.photo_px_per_mm
    ph = ph.resize((int(ph.width * f), int(ph.height * f)), Image.LANCZOS)
    say(f"photo resampled x{f:.4f} -> {ph.size[0]}x{ph.size[1]} px at {a.px_per_mm} px/mm")

    # ---- X1 scale match, measured off the two panels
    mo = board_mask(np.asarray(ours.convert("L")).astype(float))
    mp = board_mask(np.asarray(ph.convert("L")).astype(float))
    if mo is None or mp is None:
        say("X2 FIRED: no board silhouette in one of the panels.")
        sys.exit(CANNOT)
    ocx, ocy, oth, orad = radial(mo)
    pcx, pcy, pth, prad = radial(mp)
    od = 2 * np.nanmean(orad) / a.px_per_mm
    pd = 2 * np.nanmean(prad) / a.px_per_mm
    say(f"X1 scale match: OURS 2 x mean r = {od:.3f} mm | APPLE'S = {pd:.3f} mm | "
        f"delta {abs(od-pd)/pd*100:.2f}%")
    x1 = abs(od - pd) / pd <= 0.01
    if not x1:
        say("X1 FIRED: the two panels are not at the same scale.")

    # ---- X4 residual, per ray, in mm
    rot = a.break_rotation
    ours_r = np.interp((oth + rot) % 360, oth, orad, period=360)
    resid = (ours_r - prad) / a.px_per_mm
    good = np.isfinite(resid)
    rms = float(np.sqrt(np.nanmean(resid[good] ** 2)))
    p95 = float(np.nanpercentile(np.abs(resid[good]), 95))
    say(f"X4 outline residual (ours - Apple's, per ray, {good.sum()} rays): "
        f"RMS {rms:.3f} mm, p95 |.| {p95:.3f} mm, max {np.nanmax(np.abs(resid[good])):.3f} mm")

    # ---- panel 3: overlay
    ov = ph.copy()
    dv = ImageDraw.Draw(ov, "RGBA")
    pts = []
    for i in range(len(pth)):
        if not np.isfinite(ours_r[i]):
            continue
        ang = math.radians(pth[i])
        pts.append((pcx + ours_r[i] * math.cos(ang), pcy - ours_r[i] * math.sin(ang)))
    dv.line(pts + [pts[0]], fill=CYAN + (255,), width=3)

    # ---- montage
    cols = [("OURS  halo Replica R0", ours), ("APPLE'S  FCC BCGA2187 photo 6", ph),
            ("OVERLAY  ours (cyan) on Apple's", ov)]
    ch = max(i.height for _, i in cols)
    cw = max(i.width for _, i in cols)
    head, foot, gap = 66, 190, 22
    W = 3 * cw + 4 * gap
    H = head + ch + foot
    m = Image.new("RGB", (W, H), BG)
    dm = ImageDraw.Draw(m, "RGBA")
    fb, fs, ft = font(30, True), font(20), font(17)
    for i, (t, im2) in enumerate(cols):
        x = gap + i * (cw + gap)
        m.paste(im2, (x + (cw - im2.width) // 2, head + (ch - im2.height) // 2))
        dm.text((x, 22), t, font=fb, fill=INK)
    # a real scale bar, in the montage's own millimetres
    bx, by = gap, head + ch + 16
    dm.line([(bx, by), (bx + 10 * a.px_per_mm, by)], fill=INK, width=4)
    for t in range(11):
        dm.line([(bx + t * a.px_per_mm, by), (bx + t * a.px_per_mm, by - (12 if t % 5 else 20))],
                fill=INK, width=2)
    dm.text((bx + 10 * a.px_per_mm + 12, by - 12), "10 mm  (both panels, same scale)",
            font=fs, fill=INK)

    with open(a.board) as f2:
        bd = json.load(f2)
    y = by + 30
    for line, col in [
        (f"outline residual  RMS {rms:.3f} mm   p95 {p95:.3f} mm   over {good.sum()} rays", INK),
        (f"OURS 2 x mean r = {od:.3f} mm     APPLE'S = {pd:.3f} mm     delta {abs(od-pd)/pd*100:.2f}%", INK),
        (f"outer diameter {bd['parameters']['outer_diameter_mm']['value']:.3f} mm  PROVISIONAL AND IN DISPUTE "
         f"(O'Flynn '~26', L1 ~24.6, L5 {bd['parameters']['outer_diameter_mm']['value']:.2f} off photo 6)", PROV),
        ("thickness 0.30 mm AS-DRAWN; below PCBWay's and JLCPCB's 0.40 mm floors - a fact about US, not Apple", PROV),
        ("4 layers = STATED REPLICA CHOICE. Apple's true count is CANNOT DETERMINE in {4,6}", PROV),
        ("centre hole is a ROUNDED SQUARE WITH A NOTCH. This lane publishes no hole diameter.", PROV),
        ("NOT YET DRAWN: rim pads, component footprints, silkscreen, copper. Outline only.", PROV),
        (f"scale basis: {a.photo_scale_basis}", (110, 110, 114)),
        ("FACES NAMED BY WHAT IS ON THEM. This panel: the side carrying the SoC and the shield can", (110, 110, 114)),
        ("(= Apple FCC photo 6 'MLB - Front' = O'Flynn's 'backside-*'). The word 'front' is AMBIGUOUS", (110, 110, 114)),
        ("across sources and is not used here - see evidence/E03-SIDE-NAMING.md", (110, 110, 114)),
    ]:
        dm.text((bx, y), line, font=ft, fill=col)
        y += 19
    if rot:
        dm.text((bx + cw + gap, by - 4), f"X3 CONTROL ACTIVE: outline rotated {rot} deg on purpose",
                font=fs, fill=(200, 0, 0))

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    m.save(a.out)
    say(f"\nwrote {a.out}  {W}x{H}")

    back = np.asarray(Image.open(a.out).convert("L")).astype(float)
    x2 = back.std() > 5 and (back < 120).mean() > 0.02
    say(f"X2 non-blank: sd {back.std():.2f}, dark {(back<120).mean():.4f} -> {'ok' if x2 else 'FIRED'}")

    code = PASS if (x1 and x2) else FAIL
    say({0: "PASS", 1: "FAIL", 2: "CANNOT DETERMINE"}[code])
    print(json.dumps(dict(rms_mm=rms, p95_mm=p95, ours_dia_mm=od, apple_dia_mm=pd,
                          rays=int(good.sum()), rotation_deg=rot)))
    sys.exit(code)


if __name__ == "__main__":
    main()
