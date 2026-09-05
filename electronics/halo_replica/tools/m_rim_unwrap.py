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
    if img.ndim == 3:                       # colour: broadcast over the channel axis
        fx = fx[:, None]; fy = fy[:, None]
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
            + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)


def unwrap(img, cx, cy, f_lo, f_hi, n_ang, n_rad, redge):
    """Resample the rim with the radius normalised to the MEASURED edge r(theta).

    A fixed-radius annulus is wrong here: the board's apparent radius varies ~5%
    with angle (M02 Sec 3), so a constant-r ring crosses on and off the board and
    the strip fills with paper.  Sampling at f * r_edge(theta) keeps every column
    at the same fraction of the way to the edge, which is what "just inside the
    rim" actually means."""
    A = np.linspace(0, 2 * math.pi, n_ang, endpoint=False)
    Re = redge(np.degrees(A))
    F = np.linspace(f_lo, f_hi, n_rad)
    out = np.zeros((n_rad, n_ang) + img.shape[2:])
    for j, f in enumerate(F):
        r = f * Re
        out[j] = bilinear(img, cx + r * np.cos(A), cy + r * np.sin(A))
    return out, np.degrees(A), F


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
    ap.add_argument("--profile", default=None,
                    help="raw json from m_outline_fit.py; its measured r(theta) normalises "
                         "the unwrap. Without it a constant radius is used and the strip "
                         "will drift on and off the board.")
    ap.add_argument("--smooth-deg", type=float, default=1.5,
                    help="angular smoothing before peak finding. A rim pad is a degree or "
                         "two wide; without this the finder chases single-column noise and "
                         "cannot beat its own permutation control.")
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
    if a.profile:
        raw = json.load(open(a.profile))
        pr = np.array(raw["outer_r_theta"], float)
        pt, prr = pr[:, 0], pr[:, 1]
        o = np.argsort(pt); pt, prr = pt[o], prr[o]
        pt2 = np.concatenate([pt - 360, pt, pt + 360])
        pr2 = np.concatenate([prr, prr, prr])
        k = 41
        pr2s = np.convolve(pr2, np.ones(k) / k, mode="same")
        redge = lambda d: np.interp(np.asarray(d) % 360, pt, pr2s[len(pt):2 * len(pt)])
        prof_src = f"{os.path.basename(a.profile)} run {raw.get('run_utc')} git {raw.get('git_rev')}"
    else:
        redge = lambda d: np.full(np.shape(d), a.radius, float)
        prof_src = "NONE -- constant radius, the strip will drift on and off the board"
    r_lo, r_hi = a.radius * a.r_lo, a.radius * a.r_hi
    print("m_rim_unwrap.py -- inputs:")
    print(f"  image      {os.path.relpath(path, ROOT)}")
    print(f"  centre     ({cx:.2f}, {cy:.2f}) px, fitted outer radius {a.radius:.2f} px")
    print(f"  edge r(theta) from: {prof_src}")
    print(f"  annulus    {a.r_lo}..{a.r_hi} of the MEASURED local edge radius")
    print(f"  sampling   {a.n_ang} angular x {a.n_rad} radial bins "
          f"({360/a.n_ang:.3f} deg per column)")

    U, ang, rad = unwrap(lum, cx, cy, a.r_lo, a.r_hi, a.n_ang, a.n_rad, redge)
    b0, b1 = (float(v) for v in a.band.split(","))
    sel = (rad >= b0) & (rad <= b1)
    raw_sig = U[sel].mean(axis=0)
    ks = max(1, int(round(a.smooth_deg * a.n_ang / 360)) | 1)

    def smooth_wrap(v):
        k = np.ones(ks) / ks
        return np.convolve(np.concatenate([v, v, v]), k, mode="same")[len(v):2 * len(v)]

    sig = smooth_wrap(raw_sig)
    print(f"  signal     mean luma over {b0}..{b1} of the local edge radius "
          f"({int(sel.sum())} radial bins), smoothed {a.smooth_deg} deg ({ks} columns)")
    print(f"             range {sig.min():.1f}..{sig.max():.1f}, median {np.median(sig):.1f}, "
          f"sd {sig.std():.1f}")

    sep = max(1, int(round(a.min_separation_deg * a.n_ang / 360)))
    pk = find_peaks(sig, a.min_prominence, sep)
    rng = np.random.default_rng(20260905)
    # THE CONTROL MUST GO THROUGH THE SAME PIPELINE. Permuting the SMOOTHED signal
    # gives a jagged control where the real signal is smooth, so the finder invents
    # ~22 peaks from it and NOTHING could ever beat it. Permute the RAW columns
    # first, then smooth exactly as the real signal was smoothed: same histogram,
    # same smoothing, no features.
    ctrl = [len(find_peaks(smooth_wrap(rng.permutation(raw_sig)), a.min_prominence, sep))
            for _ in range(200)]
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
        vis = unwrap(rgb, cx, cy, a.r_lo, a.r_hi, a.n_ang, a.n_rad, redge)[0]
        im = Image.fromarray(np.clip(vis, 0, 255).astype(np.uint8))
        im = im.resize((a.n_ang, a.n_rad * 4), Image.LANCZOS)
        im.save(a.png)
        print(f"\n  wrote {a.png}  -- angle runs 0..360 deg left to right, "
              f"radius {a.r_lo}->{a.r_hi} of the local edge, top to bottom. COUNT IT BY EYE.")
    if a.json:
        json.dump(dict(tool="m_rim_unwrap.py", image=os.path.relpath(path, ROOT),
                       centre=[cx, cy], radius_px=a.radius,
                       annulus_fraction_of_local_edge=[a.r_lo, a.r_hi],
                       edge_profile_source=prof_src, smooth_deg=a.smooth_deg,
                       n_ang=a.n_ang, n_rad=a.n_rad,
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
