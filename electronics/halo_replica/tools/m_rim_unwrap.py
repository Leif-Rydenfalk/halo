#!/usr/bin/env python3
"""m_rim_unwrap.py -- unroll the board's rim to a straight strip, and COUNT.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.
SIDE NAMING: FRONT = component side (Apple's FCC caption). See M02.

WHY.  The dossier says SIX tear-off joints hold the antenna carrier to the
board's rim.  Counting features on a circle by eye is unreliable and counting
them by threshold is worse.  So: resample the annulus just inside the fitted
outer edge into a straight strip (angle across, radius down), which makes the
same features countable BY EYE and BY ALGORITHM independently -- and those two
counts are then a real check on each other rather than one number twice.

THE NEGATIVE CONTROL.  The peak finder is run again on the SAME strip with its
angular columns randomly permuted.  A permuted rim has the same brightness
histogram and the same number of bright pixels, but no features -- so any count
the finder returns there is the count it would invent from noise.  A detection
that does not beat its own permuted control by a wide margin is reported as
CANNOT DETERMINE, not as a count.

Exit 0 counted, 2 CANNOT DETERMINE.  Prints its inputs.
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def bilinear(img, x, y):
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    h, w = img.shape[:2]
    x0 = np.clip(x0, 0, w - 2); y0 = np.clip(y0, 0, h - 2)
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
            + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)


def unwrap(img, cx, cy, r_lo, r_hi, n_ang, n_rad):
    A = np.linspace(0, 2 * math.pi, n_ang, endpoint=False)
    R = np.linspace(r_lo, r_hi, n_rad)
    out = np.zeros((n_rad, n_ang) + img.shape[2:])
    for j, r in enumerate(R):
        out[j] = bilinear(img, cx + r * np.cos(A), cy + r * np.sin(A))
    return out, np.degrees(A), R


def find_peaks(sig, min_prom, min_sep_bins):
    """Local maxima with a prominence floor and a minimum separation."""
    n = len(sig)
    ext = np.concatenate([sig, sig, sig])       # wrap-safe
    cand = []
    for i in range(n, 2 * n):
        w = ext[i - min_sep_bins:i + min_sep_bins + 1]
        if ext[i] < w.max() - 1e-9:
            continue
        base = min(ext[i - min_sep_bins:i + 1].min(), ext[i:i + min_sep_bins + 1].min())
        prom = ext[i] - base
        if prom >= min_prom:
            cand.append((i - n, float(ext[i]), float(prom)))
    out = []
    for i, v, p in sorted(cand, key=lambda t: -t[2]):
        if all(min(abs(i - j), n - abs(i - j)) >= min_sep_bins for j, _, _ in out):
            out.append((i, v, p))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--centre", required=True, help="cx,cy px")
    ap.add_argument("--radius", type=float, required=True, help="fitted outer radius px")
    ap.add_argument("--r-lo", type=float, default=0.86)
    ap.add_argument("--r-hi", type=float, default=1.02)
    ap.add_argument("--n-ang", type=int, default=1440)
    ap.add_argument("--n-rad", type=int, default=90)
    ap.add_argument("--band", default="0.94,1.00", help="radial fraction to average for the signal")
    ap.add_argument("--min-prominence", type=float, default=18.0)
    ap.add_argument("--min-separation-deg", type=float, default=8.0)
    ap.add_argument("--px-per-mm", type=float, default=None)
    ap.add_argument("--png", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    path = a.image if os.path.isabs(a.image) else os.path.join(ROOT, "images", "airtag", a.image)
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(float)
    lum = np.asarray(Image.open(path).convert("L")).astype(float)
    cx, cy = (float(v) for v in a.centre.split(","))
    r_lo, r_hi = a.radius * a.r_lo, a.radius * a.r_hi
    print("m_rim_unwrap.py -- inputs:")
    print(f"  image      {os.path.relpath(path, ROOT)}")
    print(f"  centre     ({cx:.2f}, {cy:.2f}) px, fitted outer radius {a.radius:.2f} px")
    print(f"  annulus    r {r_lo:.1f}..{r_hi:.1f} px  ({a.r_lo}..{a.r_hi} of R)")
    print(f"  sampling   {a.n_ang} angular x {a.n_rad} radial bins "
          f"({360/a.n_ang:.3f} deg per column)")

    U, ang, rad = unwrap(lum, cx, cy, r_lo, r_hi, a.n_ang, a.n_rad)
    b0, b1 = (float(v) for v in a.band.split(","))
    sel = (rad >= a.radius * b0) & (rad <= a.radius * b1)
    sig = U[sel].mean(axis=0)
    print(f"  signal     mean luma over r {a.radius*b0:.1f}..{a.radius*b1:.1f} px "
          f"({int(sel.sum())} radial bins), per angular column")
    print(f"             range {sig.min():.1f}..{sig.max():.1f}, median {np.median(sig):.1f}, "
          f"sd {sig.std():.1f}")

    sep = max(1, int(round(a.min_separation_deg * a.n_ang / 360)))
    pk = find_peaks(sig, a.min_prominence, sep)
    rng = np.random.default_rng(20260905)
    ctrl = [len(find_peaks(rng.permutation(sig), a.min_prominence, sep)) for _ in range(200)]
    ctrl = np.array(ctrl)
    print(f"\n  peak finder: prominence >= {a.min_prominence} luma, separation >= "
          f"{a.min_separation_deg} deg ({sep} columns)")
    print(f"  FOUND {len(pk)} peaks")
    print(f"  NEGATIVE CONTROL -- the same finder on 200 angular permutations of the SAME "
          f"signal (same histogram, no features): mean {ctrl.mean():.2f}, max {ctrl.max()}, "
          f"p99 {np.percentile(ctrl, 99):.1f}")
    if len(pk) <= np.percentile(ctrl, 99):
        print("  CANNOT DETERMINE: the count does not beat what the finder invents from a "
              "feature-free permutation of the same pixels.")
        rc = 2
    else:
        print(f"  the count beats its own permuted control ({len(pk)} vs p99 "
              f"{np.percentile(ctrl, 99):.1f}) -- these are features, not noise.")
        rc = 0
    print("\n  peaks (image-coordinate angle, y down; 0 deg = +x, 90 deg = down):")
    for i, v, p in pk:
        deg = ang[i]
        arc = (2 * math.pi * a.radius * (360 / a.n_ang) / 360)
        print(f"    {deg:7.2f} deg   luma {v:6.1f}   prominence {p:5.1f}")
    if a.png:
        vis = unwrap(rgb, cx, cy, r_lo, r_hi, a.n_ang, a.n_rad)[0]
        im = Image.fromarray(np.clip(vis, 0, 255).astype(np.uint8))
        im = im.resize((a.n_ang, a.n_rad * 4), Image.LANCZOS)
        im.save(a.png)
        print(f"\n  wrote {a.png}  -- angle runs 0..360 deg left to right, "
              f"radius {r_lo:.0f}->{r_hi:.0f} px top to bottom. COUNT IT BY EYE.")
    if a.json:
        json.dump(dict(tool="m_rim_unwrap.py", image=os.path.relpath(path, ROOT),
                       centre=[cx, cy], radius_px=a.radius,
                       annulus_px=[r_lo, r_hi], n_ang=a.n_ang, n_rad=a.n_rad,
                       band_fraction=[b0, b1], min_prominence=a.min_prominence,
                       min_separation_deg=a.min_separation_deg,
                       n_peaks=len(pk),
                       control_mean=float(ctrl.mean()), control_max=int(ctrl.max()),
                       control_p99=float(np.percentile(ctrl, 99)),
                       verdict="COUNTED" if rc == 0 else "CANNOT DETERMINE",
                       peaks=[dict(angle_deg=round(float(ang[i]), 2), luma=round(v, 1),
                                   prominence=round(p, 1)) for i, v, p in pk],
                       signal=[round(float(v), 2) for v in sig]),
                  open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
