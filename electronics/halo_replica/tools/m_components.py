#!/usr/bin/env python3
"""m_components.py -- component positions on the project FRONT, in mm AND in
GENUINE pixels.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.

SIDE NAMING: FRONT = the COMPONENT side (Apple's FCC caption "MLB - Front").
O'Flynn's `backside-fullres.jpeg` IS this project's FRONT.

WHERE THE COORDINATES COME FROM.  O'Flynn's component-side photograph is the
sharp one but has NO scale reference and no measured outline (its surround is not
uniform -- dark clamp bars touch the board -- so an azimuthal edge finder returns
CANNOT DETERMINE on it, and it does).  So the board frame is not re-derived here.
It is TRANSFERRED through `c_register`'s validated homography from FCC photo 6,
where L1 measured the centre, the outline r(theta) and the hole:

    FCC6 full-res  ->  tgt.from_full  ->  H  ->  src.to_full  ->  O'Flynn full-res

`c_register` validate: worst held-out fold 0.1029 mm over four spatial folds.
Scale basis 15.6850 px/mm AT THE BOARD (M02), not the rule's 15.8875 -- see the
commit that added `--target-px-per-mm`; the built-in default is 1.29% high and
the held-out error is blind to that because it divides both sides by the same
number.

WHY EVERY POSITION IS ALSO QUOTED IN GENUINE PIXELS.  M06 measures this image at
0.195-0.258 of Nyquist over the board, i.e. **20-27 genuine px/mm** against
106.3 stored px/mm.  A position quoted to 0.01 mm off this source has three
digits of decoration on it.  The genuine-pixel column is what says how much of a
millimetre figure is real.

CONTROLS, both of which can fail:
 * THRESHOLD PLATEAU.  The segmentation threshold is SWEPT.  Count and total area
   must sit on a plateau; if they do not, the answer is CANNOT DETERMINE rather
   than a threshold picked to give a pleasing number.
 * THE CENTRE HOLE.  The identical detector is run inside the board's centre
   hole, which contains no board and therefore no components. Anything it finds
   there is what it invents.

Exit 0 measured, 2 CANNOT DETERMINE.  Prints its inputs.
"""
import argparse, hashlib, json, math, os, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import c_register as CR


def run_id(path):
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
    except Exception:
        rev = "unknown"
    return dict(run_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), git_rev=rev,
                image_sha256_12=hashlib.sha256(open(path, "rb").read()).hexdigest()[:12],
                tool="m_components.py")


def map_pts(H, src, tgt, XY):
    """FCC6 full-res points -> O'Flynn full-res points."""
    out = []
    for X, Y in XY:
        cx, cy = tgt.from_full(X, Y)
        sx, sy = CR.apply_H(H, cx, cy)
        out.append(src.to_full(sx, sy))
    return np.array(out, float)


def poly_mask(shape, poly):
    im = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in poly], fill=1)
    return np.asarray(im).astype(bool)


def segment(lum, mask, thr, min_area, max_area=None):
    m = (lum > thr) & mask
    m = ndimage.binary_opening(m, np.ones((3, 3)))
    lab, n = ndimage.label(m)
    if n == 0:
        return []
    objs = ndimage.find_objects(lab)
    out = []
    for k in range(1, n + 1):
        sl = objs[k - 1]
        blob = lab[sl] == k
        a = int(blob.sum())
        if a < min_area or (max_area is not None and a > max_area):
            continue
        ys, xs = np.nonzero(blob)
        ys = ys + sl[0].start; xs = xs + sl[1].start
        X = xs - xs.mean(); Y = ys - ys.mean()
        Ixx = (X * X).mean(); Iyy = (Y * Y).mean(); Ixy = (X * Y).mean()
        tr = Ixx + Iyy; dd = math.sqrt(max(((Ixx - Iyy) / 2) ** 2 + Ixy ** 2, 0))
        L = 4 * math.sqrt(max(tr / 2 + dd, 0)); W = 4 * math.sqrt(max(tr / 2 - dd, 0))
        out.append(dict(cx=float(xs.mean()), cy=float(ys.mean()), area_px=a,
                        long_px=L, short_px=W,
                        angle_deg=math.degrees(0.5 * math.atan2(2 * Ixy, Ixx - Iyy)) % 180))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fit", default=os.path.join(HERE, "..", "metrology",
                                                  "c_register-fit-boardscale.json"))
    ap.add_argument("--outline-raw", default=os.path.join(HERE, "..", "metrology",
                                                          "outline-raw-photo6.json"))
    ap.add_argument("--thr", default="95,155", help="segmentation sweep lo,hi")
    ap.add_argument("--thr-step", type=int, default=5)
    ap.add_argument("--min-area-mm2", type=float, default=0.10,
                    help="0201 is 0.6x0.3 = 0.18 mm^2; below ~0.10 mm^2 nothing here is real")
    ap.add_argument("--max-area-mm2", type=float, default=60.0,
                    help="upper bound on a COMPONENT. The largest part on this board is the "
                         "UWB shield can at roughly 35 mm^2. This exists so the centre-hole "
                         "control is well posed: the hole is BRIGHT BACKGROUND seen through "
                         "the board, so an unbounded detector always returns exactly one "
                         "object there (the whole hole) and the control could never pass. "
                         "The bound is physical, not tuned.")
    ap.add_argument("--hole-level", type=float, default=190.0,
                    help="luma level for O'Flynn's OWN centre hole. The hole transferred "
                         "from FCC photo 6 is visibly wrong (see the overlay) -- M02 Sec 4 "
                         "already records the FCC hole as only PARTIALLY DETERMINED.")
    ap.add_argument("--plateau-pct", type=float, default=25.0)
    ap.add_argument("--genuine-px-per-mm", default="20.7,27.4",
                    help="M06: rolloff 0.195-0.258 x 106.3 stored px/mm")
    ap.add_argument("--png", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    fit = json.load(open(a.fit))
    H = np.array(fit["H_target_to_source_cropframe"], float)
    ppm = fit["transferred_scale"]["source_px_per_mm_mean"]
    ppm_sd = fit["transferred_scale"]["source_px_per_mm_sd"]
    src, tgt, ds = CR.prepare(fit["source"]["name"], fit["target"]["name"], None)
    spath = os.path.join(ROOT, "images", "airtag", fit["source"]["path"])
    rid = run_id(spath)
    lum = np.asarray(Image.open(spath).convert("L")).astype(float)
    g_lo, g_hi = (float(v) for v in a.genuine_px_per_mm.split(","))

    print("m_components.py -- inputs:")
    print(f"  run_id      {rid['run_utc']} git {rid['git_rev']} image sha {rid['image_sha256_12']}")
    print(f"  SOURCE      {fit['source']['path']} (project FRONT = component side)")
    print(f"  frame from  {os.path.basename(a.fit)} : homography FCC6 -> O'Flynn, "
          f"NCC {fit['ncc']:.4f}, null margin {fit['null_control']['margin']:.2f}x")
    print(f"  scale       {ppm:.3f} +/- {ppm_sd:.3f} px/mm  [{fit['target']['px_per_mm_basis']}]")
    print(f"  GENUINE     {g_lo}-{g_hi} px/mm (M06). Stored/genuine = "
          f"{ppm/g_hi:.1f}-{ppm/g_lo:.1f}x -- that ratio is the decoration factor.")

    raw = json.load(open(a.outline_raw))
    ocx, ocy = raw["outer_centre"]
    O = np.array(raw["outer_r_theta"], float)
    outer_fcc = np.c_[ocx + O[:, 1] * np.cos(np.radians(O[:, 0])),
                      ocy + O[:, 1] * np.sin(np.radians(O[:, 0]))]
    icx, icy = raw["inner_centre"]
    I = np.array(raw["inner_r_theta"], float)
    inner_fcc = np.c_[icx + I[:, 1] * np.cos(np.radians(I[:, 0])),
                      icy + I[:, 1] * np.sin(np.radians(I[:, 0]))]
    outer = map_pts(H, src, tgt, outer_fcc)
    inner = map_pts(H, src, tgt, inner_fcc)
    origin = map_pts(H, src, tgt, [[ocx, ocy]])[0]
    print(f"  board frame TRANSFERRED: centre ({origin[0]:.1f},{origin[1]:.1f}) px, "
          f"outer {len(outer)} pts, hole {len(inner)} pts")

    # The hole is taken from O'FLYNN'S OWN image, not transferred. The transferred
    # FCC6 hole is visibly wrong on the overlay -- offset and too small -- which is
    # what M02 Sec 4's "PARTIALLY DETERMINED" looks like when you draw it.
    bright = lum > a.hole_level
    lab_h, nh = ndimage.label(bright)
    kh = lab_h[int(round(origin[1])), int(round(origin[0]))]
    if kh == 0:
        print("  CANNOT DETERMINE: the transferred board centre is not inside a bright "
              "region, so the centre hole cannot be segmented in this image")
        sys.exit(2)
    hole = ndimage.binary_fill_holes(lab_h == kh)
    outer_mask = poly_mask(lum.shape, outer)
    board = outer_mask & ~hole
    print(f"  hole        segmented in O'FLYNN'S OWN image at luma > {a.hole_level:.0f} "
          f"({int(hole.sum())} px); the FCC6 hole is NOT transferred (M02 Sec 4)")
    print(f"  masks       board annulus {int(board.sum())} px, "
          f"centre hole {int(hole.sum())} px (the NEGATIVE CONTROL region)")

    min_area = int(a.min_area_mm2 * ppm * ppm)
    max_area = int(a.max_area_mm2 * ppm * ppm)
    lo, hi = (int(v) for v in a.thr.split(","))
    rows = []
    for t in range(lo, hi + 1, a.thr_step):
        comps = segment(lum, board, t, min_area, max_area)
        ctrl = segment(lum, hole, t, min_area, max_area)
        rows.append((t, len(comps), sum(c["area_px"] for c in comps), len(ctrl)))
        print(f"    thr {t:3d}: {len(comps):4d} components, total area "
              f"{sum(c['area_px'] for c in comps):8d} px  |  centre-hole control: "
              f"{len(ctrl)}")

    cnt = np.array([r[1] for r in rows], float)
    spread = 100 * (cnt.max() - cnt.min()) / cnt.mean()
    ctrl_max = max(r[3] for r in rows)
    print(f"\n  PLATEAU   count varies {spread:.1f}% across the sweep "
          f"(limit {a.plateau_pct}%)")
    print(f"  CONTROL   the same detector inside the centre hole found at most "
          f"{ctrl_max} object(s)")
    ok = spread <= a.plateau_pct and ctrl_max == 0
    t_mid = rows[len(rows) // 2][0]
    comps = segment(lum, board, t_mid, min_area, max_area)
    for c in comps:
        dx = (c["cx"] - origin[0]) / ppm
        dy = (c["cy"] - origin[1]) / ppm
        c.update(x_mm=round(dx, 3), y_mm=round(dy, 3),
                 r_mm=round(math.hypot(dx, dy), 3),
                 theta_deg=round(math.degrees(math.atan2(dy, dx)) % 360, 2),
                 long_mm=round(c["long_px"] / ppm, 3), short_mm=round(c["short_px"] / ppm, 3),
                 area_mm2=round(c["area_px"] / ppm / ppm, 4),
                 long_genuine_px=[round(c["long_px"] / ppm * g_lo, 1),
                                  round(c["long_px"] / ppm * g_hi, 1)],
                 short_genuine_px=[round(c["short_px"] / ppm * g_lo, 1),
                                   round(c["short_px"] / ppm * g_hi, 1)])
        c["size_verdict"] = ("SOUND" if c["short_mm"] * g_lo >= 10
                             else "MARGINAL - short side under 10 genuine px")
    comps.sort(key=lambda c: -c["area_mm2"])
    print(f"\n  {len(comps)} components at threshold {t_mid}. "
          f"Registration hold-out 0.1029 mm = {0.1029*g_lo:.1f}-{0.1029*g_hi:.1f} genuine px.")
    print(f"  {'x_mm':>8} {'y_mm':>8} {'r_mm':>7} {'th':>7} {'long':>7} {'short':>7} "
          f"{'area':>8}  short in genuine px   verdict")
    for c in comps[:40]:
        print(f"  {c['x_mm']:8.3f} {c['y_mm']:8.3f} {c['r_mm']:7.3f} {c['theta_deg']:7.1f} "
              f"{c['long_mm']:7.3f} {c['short_mm']:7.3f} {c['area_mm2']:8.4f}  "
              f"{str(c['short_genuine_px']):>14}  {c['size_verdict']}")
    if len(comps) > 40:
        print(f"  ... {len(comps)-40} more in the JSON")
    n_sound = sum(1 for c in comps if c["size_verdict"] == "SOUND")
    print(f"\n  {n_sound}/{len(comps)} have a short side of at least 10 genuine px")
    if not ok:
        print(f"\n  CANNOT DETERMINE: plateau spread {spread:.1f}% "
              f"(limit {a.plateau_pct}%), centre-hole control {ctrl_max}")

    if a.png:
        im = Image.open(spath).convert("RGB")
        d = ImageDraw.Draw(im)
        d.line([tuple(p) for p in outer] + [tuple(outer[0])], fill=(0, 255, 0), width=5)
        hy, hx = np.nonzero(hole & ~ndimage.binary_erosion(hole))
        for i in range(0, len(hx), 40):
            d.ellipse([hx[i] - 3, hy[i] - 3, hx[i] + 3, hy[i] + 3], fill=(0, 200, 255))
        for c in comps:
            d.ellipse([c["cx"] - 9, c["cy"] - 9, c["cx"] + 9, c["cy"] + 9],
                      outline=(255, 0, 0), width=4)
        d.line([origin[0] - 40, origin[1], origin[0] + 40, origin[1]], fill=(255, 255, 0), width=5)
        d.line([origin[0], origin[1] - 40, origin[0], origin[1] + 40], fill=(255, 255, 0), width=5)
        im.resize((im.width // 3, im.height // 3), Image.LANCZOS).save(a.png)
        print(f"  wrote {a.png}  -- LOOK AT IT")
    if a.json:
        json.dump(dict(**rid, source=fit["source"]["path"],
                       frame_from=os.path.basename(a.fit),
                       px_per_mm=ppm, px_per_mm_sd=ppm_sd,
                       px_per_mm_basis=fit["target"]["px_per_mm_basis"],
                       genuine_px_per_mm=[g_lo, g_hi],
                       registration_holdout_mm=0.1029,
                       origin_px=[float(origin[0]), float(origin[1])],
                       threshold_used=t_mid, threshold_sweep=[lo, hi],
                       plateau_spread_pct=round(float(spread), 2),
                       control_centre_hole_max=ctrl_max,
                       verdict="MEASURED" if ok else "CANNOT DETERMINE",
                       n_components=len(comps), n_sound=n_sound,
                       components=comps), open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
