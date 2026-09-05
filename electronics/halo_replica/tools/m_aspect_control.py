#!/usr/bin/env python3
"""m_aspect_control.py -- is the PHOTOGRAPH anisotropic?  Ask a known-round object.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.

THE QUESTION.  The bare MLB in FCC photos 6 and 7 images about 5% wider than it
is tall, consistently, in both.  Two explanations produce that and they lead to
opposite conclusions about the board's diameter:

  (a) the board is not circular, or is tilted, and the picture is faithful;
  (b) the board is circular and the PICTURE is horizontally stretched.

Under (b) the true diameter is width/(x-scale) = height/(y-scale) and both give
the same answer; under (a) they do not.  So the whole diameter rests on this.

THE CONTROL.  Each steel rule carries a punched hanging hole, which is round by
manufacture.  It is in the same photograph, on the same table, imaged through
the same lens.  If the round hole images round, the board's 5% is the board's.
If the round hole images 5% wider than tall, the 5% is the camera's and the
board is circular.  The control cannot be argued with, only measured.

METHOD.  Sub-pixel half-max between the object's own interior level and its own
surround level, on 360 rays about a refitted centre, then TRIMMED caliper widths
(0.5..99.5 percentile of the projection) so one bad ray cannot set the width.
Half-max, not steepest-gradient, because a paper-through-steel boundary is a
weaker step than a board-on-paper one and the gradient peak is not reliable at
that contrast -- stated because the two tools in this lane differ here on
purpose.

Exit 0 measured, 2 CANNOT DETERMINE.  Prints its inputs.
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def bilinear(img, x, y):
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    h, w = img.shape[:2]
    x0 = np.clip(x0, 0, w - 2); y0 = np.clip(y0, 0, h - 2)
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
            + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)


def seed(lum, box, bright):
    x0, y0, x1, y1 = box
    sub = lum[y0:y1, x0:x1]
    m = sub > bright if bright is not None else sub < 120
    lab, n = ndimage.label(m)
    if n == 0:
        return None
    sz = ndimage.sum(m, lab, range(1, n + 1))
    k = int(np.argmax(sz)) + 1
    b = ndimage.binary_fill_holes(lab == k)
    if b[0].any() or b[-1].any() or b[:, 0].any() or b[:, -1].any():
        return None
    ys, xs = np.nonzero(b)
    return (float(xs.mean()) + x0, float(ys.mean()) + y0,
            math.sqrt(b.sum() / math.pi), int(b.sum()))


def ray_halfmax(lum, cx, cy, ang, r_lo, r_hi, mode, min_step, step=0.2):
    rs = np.arange(r_lo, r_hi, step)
    v = bilinear(lum, cx + rs * math.cos(ang), cy + rs * math.sin(ang))
    q = max(5, len(rs) // 5)
    if mode == "in":       # bright inside, darker outside
        hi_, lo_ = np.median(v[:q]), np.median(v[-q:])
    else:                  # dark inside, brighter outside
        lo_, hi_ = np.median(v[:q]), np.median(v[-q:])
    if hi_ - lo_ < min_step:
        return None, "contrast across this ray is below the minimum"
    thr = 0.5 * (lo_ + hi_)
    above = v > thr
    idx = ([i for i in range(1, len(v)) if above[i - 1] and not above[i]] if mode == "in"
           else [i for i in range(1, len(v)) if above[i] and not above[i - 1]])
    if not idx:
        return None, "no crossing of the half-max level"
    i = idx[0] if mode == "in" else idx[-1]
    v0, v1 = v[i - 1], v[i]
    f = 0.0 if v1 == v0 else (thr - v0) / (v1 - v0)
    return float(rs[i - 1] + f * step), None


def outline(lum, cx, cy, r0, mode, min_step, n=360, lo=0.55, hi=1.55):
    pts, drop = [], {}
    for k in range(n):
        a = 2 * math.pi * k / n
        r, why = ray_halfmax(lum, cx, cy, a, r0 * lo, r0 * hi, mode, min_step)
        (pts.append((a, r)) if r is not None else drop.setdefault(why, []).append(k))
    return pts, drop


def trimmed_caliper(X, Y, n_phi=180):
    phi = np.linspace(0, math.pi, n_phi, endpoint=False)
    W = []
    for f in phi:
        p = X * math.cos(f) + Y * math.sin(f)
        W.append(np.percentile(p, 99.5) - np.percentile(p, 0.5))
    return np.degrees(phi), np.array(W)


def measure(lum, box, mode, min_step, label, n=360):
    br = 200 if mode == "in" else None
    sd = seed(lum, box, br)
    if sd is None:
        return dict(label=label, verdict="CANNOT DETERMINE",
                    reason="no whole blob inside the box (it touches a border, or none found)")
    cx, cy, r0, area = sd
    for _ in range(3):
        pts, drop = outline(lum, cx, cy, r0, mode, min_step, n)
        if len(pts) < n // 3:
            return dict(label=label, verdict="CANNOT DETERMINE", box=list(box),
                        reason=f"only {len(pts)}/{n} rays produced an edge; "
                               f"reasons: {[(k, len(v)) for k, v in drop.items()]}")
        A = np.array([a for a, _ in pts]); R = np.array([r for _, r in pts])
        X, Y = cx + R * np.cos(A), cy + R * np.sin(A)
        ncx, ncy = float(X.mean()), float(Y.mean())
        r0 = float(np.median(np.hypot(X - ncx, Y - ncy)))
        moved = math.hypot(ncx - cx, ncy - cy); cx, cy = ncx, ncy
        if moved < 0.05:
            break
    phi, W = trimmed_caliper(X, Y)
    wx, wy = float(W[0]), float(W[len(phi) // 2])
    return dict(label=label, verdict="MEASURED", box=list(box), mode=mode,
                min_step=min_step, seed_area_px=area,
                centre_px=[round(cx, 2), round(cy, 2)],
                rays_used=len(pts), rays_total=n,
                rejected={k: len(v) for k, v in drop.items()},
                width_horizontal_px=round(wx, 3), width_vertical_px=round(wy, 3),
                w_over_h=round(wx / wy, 4),
                caliper_median_px=round(float(np.median(W)), 3),
                caliper_min_px=round(float(W.min()), 3),
                caliper_min_phi_deg=round(float(phi[int(np.argmin(W))]), 1),
                caliper_max_px=round(float(W.max()), 3),
                caliper_max_phi_deg=round(float(phi[int(np.argmax(W))]), 1),
                caliper_max_over_min=round(float(W.max() / W.min()), 4))


TARGETS = {
    # photo: (hole box, hole is bright-inside), (board box, board is dark-inside)
    "6": dict(hole=(430, 1240, 640, 1420), board=(700, 440, 1210, 930)),
    "7": dict(hole=(520, 1230, 720, 1400), board=(680, 540, 1200, 990)),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photos", default="6,7")
    ap.add_argument("--json", default=None)
    ap.add_argument("--max-control-anisotropy", type=float, default=1.5,
                    help="percent; above this the PHOTOGRAPH is declared anisotropic")
    a = ap.parse_args()
    print("m_aspect_control.py -- inputs:")
    out = {}
    for p in a.photos.split(","):
        fn = f"fcc-BCGA2187-internal-photo-{p}.jpg"
        path = os.path.join(ROOT, "images", "airtag", fn)
        lum = np.asarray(Image.open(path).convert("L")).astype(float)
        t = TARGETS[p]
        print(f"\n  photo {p}: {fn}  ({lum.shape[1]}x{lum.shape[0]})")
        print(f"    control  = the punched hanging hole in the bottom steel rule, "
              f"box {t['hole']} (ROUND BY MANUFACTURE)")
        print(f"    subject  = the bare MLB outer edge, box {t['board']}")
        h = measure(lum, t["hole"], "in", 25.0, "ruler hanging hole (known round)")
        b = measure(lum, t["board"], "out", 35.0, "bare MLB outer edge")
        out[f"photo{p}"] = dict(control=h, subject=b)
        for r in (h, b):
            if r["verdict"] != "MEASURED":
                print(f"    {r['label']}: CANNOT DETERMINE -- {r['reason']}")
                continue
            print(f"    {r['label']}: {r['rays_used']}/{r['rays_total']} rays, "
                  f"centre {r['centre_px']}")
            print(f"      horizontal {r['width_horizontal_px']:.2f} px, vertical "
                  f"{r['width_vertical_px']:.2f} px, w/h = {r['w_over_h']:.4f}")
            print(f"      caliper max/min {r['caliper_max_over_min']:.4f} "
                  f"(max at {r['caliper_max_phi_deg']:.0f} deg, min at "
                  f"{r['caliper_min_phi_deg']:.0f} deg)")
            if r["rejected"]:
                print(f"      rejected: {r['rejected']}")
        if h["verdict"] == "MEASURED" and b["verdict"] == "MEASURED":
            ch = 100 * (h["w_over_h"] - 1)
            cb = 100 * (b["w_over_h"] - 1)
            print(f"\n    CONTROL says the photograph stretches a ROUND object by "
                  f"{ch:+.2f}% horizontally")
            print(f"    SUBJECT (the board) is        {cb:+.2f}% wider than tall")
            print(f"    unexplained residue: {cb - ch:+.2f} percentage points")
            out[f"photo{p}"]["control_anisotropy_pct"] = round(ch, 3)
            out[f"photo{p}"]["subject_anisotropy_pct"] = round(cb, 3)
            out[f"photo{p}"]["residue_pct_points"] = round(cb - ch, 3)
            if abs(ch) > a.max_control_anisotropy:
                print(f"    -> THE PHOTOGRAPH IS ANISOTROPIC. A width measured in px must be "
                      f"divided by an X scale and a height by a Y scale; one number for both "
                      f"is wrong by {ch:+.2f}%.")
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2)
        print(f"\n  wrote {a.json}")


if __name__ == "__main__":
    main()
