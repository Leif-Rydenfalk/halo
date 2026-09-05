#!/usr/bin/env python3
"""m_dark_packages.py -- locate the DARK IC bodies that m_components.py is blind to.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.
SIDE NAMING: FRONT = the COMPONENT side. O'Flynn's `backside-fullres.jpeg` IS it.

WHY.  M07 located 95 features and every one of them is METAL -- pads,
terminations, cans, solder -- because the detector thresholded on brightness.
The nRF52832, the black package at 9 o'clock and the other dark plastic bodies
are not in that list.  For a footprint list that may be right; for a picture that
has to read as an AirTag it is the wrong 95, because the big dark bodies are what
make the photograph recognisable.

THE DISCRIMINATOR IS COLOUR, AND IT GOT THERE BY FAILING TWICE FIRST.
  Attempt 1, dark + smooth + rectangular: FAILED. Bare soldermask is also dark
    and smooth, the package merged with it, and nothing survived the fill gate.
  Attempt 2, "darker than its local surround" (a black top-hat): FAILED. Large
    dark stretches of board connect into a single 1.76 Mpx blob spanning the
    board.
  Attempt 3, a stated region of interest with Otsu inside it: FAILED, AND IT IS
    THE MOST INSTRUCTIVE FAILURE. It returns an answer, and the answer is the
    BOX: padding the ROI by 0, 20, 40, 60 px gives 3.35, 3.98, 4.09 and 4.50 mm
    for the same package -- a 34% swing driven entirely by my choice of box -- and
    the blob touches the ROI edge at every padding. That is M01's "394 px was the
    crop frame" in a new costume: a number that looks like a measurement of the
    board and is a measurement of the operator.
  Attempt 4, COLOUR: the nRF52832's epoxy is BLUE. Measured B-R = +43 on the
    package against +1 median over the whole board. At B-R > 20 it segments as a
    rectangle of fill 1.000 -- a filled rectangle, not a leaked region.

SO WHAT THIS TOOL COVERS, AND WHAT IT DOES NOT.  It finds packages whose BODY
COLOUR differs from the soldermask. The neutral-black package at 9 o'clock has
B-R = +0.5 against the board's +1 and is INVISIBLE to it. Neutral dark packages
remain CANNOT DETERMINE, with attempt 3's ROI-sensitivity table as the evidence
that it is the photograph and not the effort.

THE POSITIVE CONTROL IS THE nRF52832-CIAA, AND IT IS THE RIGHT KIND.
Published body 2.956 x 3.226 mm (Nordic nRF52832 PS v1.4, Table 132, p.541 --
fetched by lane L3, not recalled).  It is a dark package, IN THIS PHOTOGRAPH, at
THIS noise, with a truth value that came from a datasheet rather than from me.
That is exactly what my synthetic rim control lacked this morning when it turned
out 19x cleaner than the photograph it stood in for: a control drawn from the
real image at real noise CANNOT be too easy, because it is exactly as hard as the
task.

Verbs:  control   run the nRF52832 positive control, and the deliberate breaks
        run       detect dark packages across the board
Exit 0 pass, 1 fail, 2 CANNOT DETERMINE.  Prints its inputs.
"""
import argparse, hashlib, json, math, os, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import c_register as CR
import m_components as MC

NRF_MM = (2.956, 3.226)          # Nordic PS v1.4 Table 132 p.541, fetched by L3
NRF_SOURCE = "Nordic nRF52832 PS v1.4, Table 132, p.541 (fetched by lane L3)"


def run_id(path):
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
    except Exception:
        rev = "unknown"
    return dict(run_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), git_rev=rev,
                image_sha256_12=hashlib.sha256(open(path, "rb").read()).hexdigest()[:12],
                tool="m_dark_packages.py")


def local_sd(a, w):
    k = np.ones((w, w)) / (w * w)
    m = ndimage.uniform_filter(a, w)
    m2 = ndimage.uniform_filter(a * a, w)
    return np.sqrt(np.clip(m2 - m * m, 0, None))


def rect_metrics(ys, xs):
    """Principal-axis extents and how well the blob fills that rectangle."""
    X = xs - xs.mean(); Y = ys - ys.mean()
    Ixx = (X * X).mean(); Iyy = (Y * Y).mean(); Ixy = (X * Y).mean()
    th = 0.5 * math.atan2(2 * Ixy, Ixx - Iyy)
    c, s = math.cos(-th), math.sin(-th)
    u = X * c - Y * s
    v = X * s + Y * c
    w = float(np.percentile(u, 99.5) - np.percentile(u, 0.5))
    h = float(np.percentile(v, 99.5) - np.percentile(v, 0.5))
    long_, short_ = max(w, h), min(w, h)
    fill = len(xs) / (w * h) if w * h > 0 else 0.0
    return long_, short_, fill, math.degrees(th) % 180


def detect(lum, mask, dark_thr, tex_thr, tex_win, min_area, max_area, min_fill, br=None):
    if br is not None:
        m = (br > dark_thr) & mask          # dark_thr carries the B-R threshold
    else:
        sd = local_sd(lum, tex_win)
        m = (lum < dark_thr) & (sd < tex_thr) & mask
    m = ndimage.binary_opening(m, np.ones((9, 9)))
    m = ndimage.binary_closing(m, np.ones((21, 21)))
    m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m)
    if n == 0:
        return []
    objs = ndimage.find_objects(lab)
    out = []
    for k in range(1, n + 1):
        sl = objs[k - 1]
        blob = lab[sl] == k
        a = int(blob.sum())
        if a < min_area or a > max_area:
            continue
        ys, xs = np.nonzero(blob)
        ys = ys + sl[0].start; xs = xs + sl[1].start
        L, W, fill, ang = rect_metrics(ys, xs)
        if fill < min_fill or W <= 0:
            continue
        out.append(dict(cx=float(xs.mean()), cy=float(ys.mean()), area_px=a,
                        long_px=L, short_px=W, fill=round(fill, 3),
                        angle_deg=round(ang, 1)))
    return out


def board_frame(fit_path, hole_level=190.0):
    fit = json.load(open(fit_path))
    H = np.array(fit["H_target_to_source_cropframe"], float)
    src, tgt, _ = CR.prepare(fit["source"]["name"], fit["target"]["name"], None)
    spath = os.path.join(ROOT, "images", "airtag", fit["source"]["path"])
    lum = np.asarray(Image.open(spath).convert("L")).astype(float)
    raw = json.load(open(os.path.join(HERE, "..", "metrology", "outline-raw-photo6.json")))
    ocx, ocy = raw["outer_centre"]
    O = np.array(raw["outer_r_theta"], float)
    outer_fcc = np.c_[ocx + O[:, 1] * np.cos(np.radians(O[:, 0])),
                      ocy + O[:, 1] * np.sin(np.radians(O[:, 0]))]
    outer = MC.map_pts(H, src, tgt, outer_fcc)
    origin = MC.map_pts(H, src, tgt, [[ocx, ocy]])[0]
    bright = lum > hole_level
    lab_h, _ = ndimage.label(bright)
    kh = lab_h[int(round(origin[1])), int(round(origin[0]))]
    hole = ndimage.binary_fill_holes(lab_h == kh) if kh else np.zeros(lum.shape, bool)
    board = MC.poly_mask(lum.shape, outer) & ~hole
    ppm = fit["transferred_scale"]["source_px_per_mm_mean"]
    return lum, board, outer, origin, ppm, spath, fit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["control", "run"])
    ap.add_argument("--fit", default=os.path.join(HERE, "..", "metrology",
                                                  "c_register-fit-boardscale.json"))
    ap.add_argument("--br-thr", type=float, default=20.0,
                    help="blue-minus-red threshold. Board median B-R is +1; the nRF is +43.")
    ap.add_argument("--dark-thr", type=float, default=95.0)
    ap.add_argument("--tex-thr", type=float, default=34.0)
    ap.add_argument("--tex-win", type=int, default=25)
    ap.add_argument("--min-area-mm2", type=float, default=0.45)
    ap.add_argument("--max-area-mm2", type=float, default=60.0)
    ap.add_argument("--min-fill", type=float, default=0.72)
    ap.add_argument("--genuine-px-per-mm", default="20.7,27.4")
    ap.add_argument("--nrf-box", default="1040,660,1400,990",
                    help="a generous box KNOWN to contain the nRF52832, from looking at "
                         "the photograph. The detector is not told where it is inside this.")
    ap.add_argument("--tol-pct", type=float, default=6.0)
    ap.add_argument("--png", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    lum, board, outer, origin, ppm, spath, fit = board_frame(a.fit)
    rgb = np.asarray(Image.open(spath).convert("RGB")).astype(float)
    BR = rgb[:, :, 2] - rgb[:, :, 0]
    rid = run_id(spath)
    g_lo, g_hi = (float(v) for v in a.genuine_px_per_mm.split(","))
    min_area = int(a.min_area_mm2 * ppm * ppm)
    max_area = int(a.max_area_mm2 * ppm * ppm)
    print("m_dark_packages.py -- inputs:")
    print(f"  run_id      {rid['run_utc']} git {rid['git_rev']} image sha {rid['image_sha256_12']}")
    print(f"  SOURCE      {fit['source']['path']} (project FRONT)")
    print(f"  scale       {ppm:.3f} px/mm  [{fit['target']['px_per_mm_basis']}]")
    print(f"  GENUINE     {g_lo}-{g_hi} px/mm (M06)")
    print(f"  criteria    B-R > {a.br_thr} (board median B-R = "
          f"{np.median(BR[board]):+.1f}), area {a.min_area_mm2}-{a.max_area_mm2} mm^2, "
          f"rect fill >= {a.min_fill}")

    if a.verb == "control":
        x0, y0, x1, y1 = (int(v) for v in a.nrf_box.split(","))
        box = np.zeros(lum.shape, bool); box[y0:y1, x0:x1] = True
        print(f"\n  POSITIVE CONTROL -- nRF52832-CIAA, published body "
              f"{NRF_MM[0]} x {NRF_MM[1]} mm")
        print(f"    source of truth: {NRF_SOURCE}")
        print(f"    search box {(x0,y0,x1,y1)} -- generous, and the detector is NOT told "
              f"where the part is inside it")
        rows, ok_any = [], False
        got = detect(lum, board & box, a.br_thr, a.tex_thr, a.tex_win,
                     min_area, max_area, a.min_fill, br=BR)
        if not got:
            print("    FAIL  nothing detected in the control box")
            sys.exit(1)
        # pick the MOST RECTANGULAR candidate, not the biggest and not the
        # closest to the published size -- selecting on the answer would make the
        # control agree with itself.
        got.sort(key=lambda c: -c["fill"])
        c = got[0]
        L, W = c["long_px"] / ppm, c["short_px"] / ppm
        eL = 100 * (L - max(NRF_MM)) / max(NRF_MM)
        eW = 100 * (W - min(NRF_MM)) / min(NRF_MM)
        ar, ar_t = L / W, max(NRF_MM) / min(NRF_MM)
        print(f"    detected  {L:.3f} x {W:.3f} mm  (fill {c['fill']}, "
              f"{c['area_px']} px, angle {c['angle_deg']} deg)")
        print(f"    published {max(NRF_MM):.3f} x {min(NRF_MM):.3f} mm")
        print(f"    ERROR     long {eL:+.2f}%   short {eW:+.2f}%   "
              f"aspect {ar:.4f} vs {ar_t:.4f} ({100*(ar-ar_t)/ar_t:+.2f}%)")
        okc = abs(eL) <= a.tol_pct and abs(eW) <= a.tol_pct
        print(f"    {'PASS' if okc else 'FAIL'}  tolerance +/-{a.tol_pct}%")
        print(f"\n    ASIDE, and it is a real disagreement rather than noise: this size is"
              f"\n    reached with the REGISTRATION-derived scale {ppm:.3f} px/mm. Making the"
              f"\n    nRF exactly its published size instead would require "
              f"{c['long_px']/max(NRF_MM):.2f} px/mm,"
              f"\n    {100*(c['long_px']/max(NRF_MM)-ppm)/ppm:+.2f}% from the registration route."
              f"\n    Two independent scale routes on one image; neither is fitted to the other.")

        print("\n  DELIBERATE BREAKS -- each must go RED")
        b1 = detect(lum, board & box, -999.0, a.tex_thr, a.tex_win,
                    min_area, max_area, 0.0, br=BR)
        big1 = max((x["area_px"] for x in b1), default=0)
        roi_px = int((board & box).sum())
        # THE ASSERTION HAD TO BE CORRECTED, and the correction is not a loosening.
        # "3x bigger than the package" cannot fire here: the search box CAPS the
        # blob at the ROI's own area, so a fully merged blob and a 3x-too-big one
        # are the same number. The evidence of merging is that the blob FILLS THE
        # WHOLE ROI -- there is no boundary left anywhere inside it.
        r1 = big1 >= 0.98 * roi_px
        print(f"    {'PASS' if r1 else 'FAIL'}  with the COLOUR criterion removed "
              f"(B-R > -999) the package merges into the board: the blob fills "
              f"{100.0*big1/roi_px:.1f}% of the ROI ({big1}/{roi_px} px) against the "
              f"control's {c['area_px']} px ({100.0*c['area_px']/roi_px:.1f}%)")
        b2 = detect(lum, board & box, a.br_thr, a.tex_thr, a.tex_win,
                    min_area, max_area, 1.001, br=BR)
        r2 = len(b2) == 0
        print(f"    {'PASS' if r2 else 'FAIL'}  an impossible fill requirement (>1.0) "
              f"rejects everything: {len(b2)} found")
        empty = np.zeros(lum.shape, bool); empty[2400:2700, 1400:1700] = True
        b3 = detect(lum, board & empty & ~board, a.br_thr, a.tex_thr, a.tex_win,
                    min_area, max_area, a.min_fill, br=BR)
        r3 = len(b3) == 0
        print(f"    {'PASS' if r3 else 'FAIL'}  an empty mask yields nothing: {len(b3)} found")
        allok = okc and r1 and r2 and r3
        if a.json:
            json.dump(dict(**rid, verb="control", nrf_published_mm=list(NRF_MM),
                           nrf_source=NRF_SOURCE, px_per_mm=ppm,
                           detected_long_mm=L, detected_short_mm=W,
                           err_long_pct=eL, err_short_pct=eW,
                           aspect=ar, aspect_published=ar_t,
                           implied_px_per_mm=c["long_px"] / max(NRF_MM),
                           breaks=dict(no_texture=r1, impossible_fill=r2, empty_mask=r3),
                           verdict="PASS" if allok else "FAIL"),
                      open(a.json, "w"), indent=2)
            print(f"  wrote {a.json}")
        print(f"\n  {'PASS' if allok else 'FAIL'}  positive control + 3 deliberate breaks")
        sys.exit(0 if allok else 1)

    got = detect(lum, board, a.br_thr, a.tex_thr, a.tex_win, min_area, max_area,
                 a.min_fill, br=BR)
    for c in got:
        dx = (c["cx"] - origin[0]) / ppm
        dy = (c["cy"] - origin[1]) / ppm
        c.update(x_mm=round(dx, 3), y_mm=round(dy, 3), r_mm=round(math.hypot(dx, dy), 3),
                 theta_deg=round(math.degrees(math.atan2(dy, dx)) % 360, 2),
                 long_mm=round(c["long_px"] / ppm, 3), short_mm=round(c["short_px"] / ppm, 3),
                 area_mm2=round(c["area_px"] / ppm / ppm, 4),
                 short_genuine_px=[round(c["short_px"] / ppm * g_lo, 1),
                                   round(c["short_px"] / ppm * g_hi, 1)])
        c["size_verdict"] = ("SOUND" if c["short_mm"] * g_lo >= 10
                             else "MARGINAL - short side under 10 genuine px")
    got.sort(key=lambda c: -c["area_mm2"])
    print(f"\n  {len(got)} dark packages")
    print(f"  {'x_mm':>8} {'y_mm':>8} {'r_mm':>7} {'th':>7} {'long':>7} {'short':>7} "
          f"{'area':>8} {'fill':>6} {'ang':>6}  short genuine px  verdict")
    for c in got:
        print(f"  {c['x_mm']:8.3f} {c['y_mm']:8.3f} {c['r_mm']:7.3f} {c['theta_deg']:7.1f} "
              f"{c['long_mm']:7.3f} {c['short_mm']:7.3f} {c['area_mm2']:8.3f} "
              f"{c['fill']:6.3f} {c['angle_deg']:6.1f}  {str(c['short_genuine_px']):>15}  "
              f"{c['size_verdict']}")
    if a.png:
        im = Image.open(spath).convert("RGB")
        d = ImageDraw.Draw(im)
        d.line([tuple(p) for p in outer] + [tuple(outer[0])], fill=(0, 255, 0), width=5)
        for c in got:
            L2, W2 = c["long_px"] / 2, c["short_px"] / 2
            th = math.radians(c["angle_deg"])
            pts = [(c["cx"] + dx * math.cos(th) - dy * math.sin(th),
                    c["cy"] + dx * math.sin(th) + dy * math.cos(th))
                   for dx, dy in ((-L2, -W2), (L2, -W2), (L2, W2), (-L2, W2))]
            d.line(pts + [pts[0]], fill=(255, 40, 255), width=6)
        im.resize((im.width // 3, im.height // 3), Image.LANCZOS).save(a.png)
        print(f"  wrote {a.png} -- LOOK AT IT")
    if a.json:
        json.dump(dict(**rid, verb="run", px_per_mm=ppm,
                       px_per_mm_basis=fit["target"]["px_per_mm_basis"],
                       genuine_px_per_mm=[g_lo, g_hi], criteria=dict(
                           dark_thr=a.dark_thr, tex_thr=a.tex_thr, tex_win=a.tex_win,
                           min_area_mm2=a.min_area_mm2, max_area_mm2=a.max_area_mm2,
                           min_fill=a.min_fill),
                       origin_px=[float(origin[0]), float(origin[1])],
                       n=len(got), packages=got), open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")
    sys.exit(0)


if __name__ == "__main__":
    main()
