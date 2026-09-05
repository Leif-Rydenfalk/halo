#!/usr/bin/env python3
"""m_resolution_probe.py -- does this image hold the detail its pixel count implies?

L1 PHOTOGRAPH METROLOGY lane, halo Replica.

THE QUESTION, and it decides whether re-rendering the FCC exhibit is worth
anything.  Our AirTag JPEGs are 2134x1600 and CATALOG.md says they were rendered
from the FCC PDF AT 150 DPI.  If the PDF's embedded image is SMALLER than that,
the 150 dpi render already interpolated, and re-rendering at 600 dpi would
produce a four-times-larger file holding exactly the same information -- a rim
band 110 px deep instead of 27 px purely because a resampler invented the
pixels.  A blob detector would then find MORE candidates, more confidently, from
NO NEW EVIDENCE, and the failure would look like success.

MEASURED WITHOUT THE PDF.  Upsampling cannot create high spatial frequencies.
So take the radially-averaged power spectrum of a detailed region and find where
the energy dies.  An image carrying real detail to its own Nyquist has energy
right up to it; an image upsampled by a factor k rolls off at about 1/k of
Nyquist, and the ratio of the rolloff to Nyquist estimates the TRUE resolution.

THE CONTROL, and this tool is useless without it.  The same measurement is run
on (a) the image downsampled by 2 and re-upsampled by 2, which is KNOWN to have
half the true resolution, and (b) the image as-is.  If the probe cannot tell
those two apart it cannot answer the question at all, and it says so.  The
known-degraded case is what calibrates the number; the absolute rolloff of a
JPEG means little on its own.

Exit 0 measured, 2 CANNOT DETERMINE.  Prints its inputs.
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def radial_spectrum(a):
    a = a - a.mean()
    w = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1]))
    F = np.abs(np.fft.fftshift(np.fft.fft2(a * w))) ** 2
    h, w_ = a.shape
    cy, cx = h // 2, w_ // 2
    yy, xx = np.mgrid[0:h, 0:w_]
    r = np.hypot((yy - cy) / (h / 2), (xx - cx) / (w_ / 2))   # 1.0 = Nyquist
    nb = 64
    bins = np.clip((r * nb).astype(int), 0, nb - 1)
    p = np.array([F[bins == i].mean() if (bins == i).any() else np.nan for i in range(nb)])
    f = (np.arange(nb) + 0.5) / nb
    return f, p


def rolloff(f, p, frac=0.01):
    """Highest frequency at which the radial power is still `frac` of its
    low-frequency plateau. Normalised so 1.0 = the image's own Nyquist."""
    ref = np.nanmedian(p[2:8])
    thr = ref * frac
    ok = np.where(p > thr)[0]
    return float(f[ok[-1]]) if len(ok) else float("nan")


def degrade(a, k=2):
    im = Image.fromarray(a.astype(np.uint8))
    small = im.resize((max(1, im.width // k), max(1, im.height // k)), Image.LANCZOS)
    return np.asarray(small.resize(im.size, Image.LANCZOS)).astype(float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--box", required=True, help="x0,y0,x1,y1 -- pick a DETAILED region")
    ap.add_argument("--frac", type=float, default=0.01)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    path = a.image if os.path.isabs(a.image) else os.path.join(ROOT, "images", "airtag", a.image)
    lum = np.asarray(Image.open(path).convert("L")).astype(float)
    x0, y0, x1, y1 = (int(v) for v in a.box.split(","))
    sub = lum[y0:y1, x0:x1]
    print("m_resolution_probe.py -- inputs:")
    print(f"  image  {os.path.relpath(path, ROOT)}  ({lum.shape[1]}x{lum.shape[0]})")
    print(f"  region {(x0,y0,x1,y1)}  ({sub.shape[1]}x{sub.shape[0]} px), "
          f"luma sd {sub.std():.1f}")
    print(f"  rolloff = highest frequency still holding {a.frac:.1%} of the "
          f"low-frequency power; 1.000 = this image's own Nyquist")

    f, p = radial_spectrum(sub)
    r_as_is = rolloff(f, p, a.frac)
    ladder = {}
    for k in (2, 3, 4, 6):
        fk, pk = radial_spectrum(degrade(sub, k))
        ladder[k] = rolloff(fk, pk, a.frac)

    print(f"\n  as held                                      rolloff {r_as_is:.3f} of Nyquist")
    for k, v in ladder.items():
        lost = r_as_is - v
        print(f"  CONTROL /{k} then x{k} (known 1/{k} resolution)      {v:.3f}   "
              f"(costs {lost:+.3f})")

    # READ THE LADDER, do not just require a monotone drop.
    #
    # An earlier version demanded as_held > /2 > /4 and called anything else
    # "the probe cannot separate the controls". That was WRONG, and wrong in the
    # way that matters: if the image's real detail already dies below half its
    # own Nyquist, then throwing away everything above half Nyquist costs
    # NOTHING, so the /2 control MUST come out equal. The controls failing to
    # separate at /2 while separating at /4 is not the probe failing -- it is
    # the answer.
    SEP = 0.03
    separates = [k for k, v in ladder.items() if r_as_is - v > SEP]
    if not separates:
        print("\n  CANNOT DETERMINE: not even the /6 control is separated, so this probe "
              "cannot measure this region at all. Try a region with more fine detail.")
        sys.exit(2)
    k_first = min(separates)
    # detail survives 1/k_first-scale destruction but not the next step down
    lo, hi = 1.0 / k_first, 1.0 / (k_first - 1) if k_first > 1 else 1.0
    eff_lo, eff_hi = int(round(lum.shape[1] * lo)), int(round(lum.shape[1] * hi))
    print(f"\n  READING THE LADDER: throwing away everything above 1/{k_first} of Nyquist is "
          f"the FIRST step that costs measurable detail.")
    print(f"  Every coarser step ({', '.join('/'+str(k) for k in ladder if k < k_first) or 'none'}) "
          f"costs nothing, which means the detail was never there.")
    print(f"\n  VERDICT: this {lum.shape[1]}x{lum.shape[0]} image carries the real detail of "
          f"roughly {eff_lo}-{eff_hi} px of width.")
    if k_first >= 2:
        msg = (f"ALREADY SOFT / UPSAMPLED: real detail stops between 1/{k_first} and "
               f"1/{k_first-1} of Nyquist, i.e. about {eff_lo}-{eff_hi} px of genuine width "
               f"in a {lum.shape[1]} px file. RE-RENDERING THE SOURCE LARGER CANNOT ADD "
               f"INFORMATION THAT IS NOT THERE.")
    else:
        msg = ("carries detail to near its own Nyquist -- a larger render of the SOURCE "
               "could hold more")
    print(f"  {msg}")
    est = r_as_is
    if a.json:
        json.dump(dict(tool="m_resolution_probe.py",
                       image=os.path.relpath(path, ROOT), box=[x0, y0, x1, y1],
                       frac=a.frac, rolloff_as_held=r_as_is,
                       control_ladder={str(k): v for k, v in ladder.items()},
                       first_separating_step=k_first,
                       effective_width_px_range=[eff_lo, eff_hi],
                       verdict=msg), open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")
    sys.exit(0)


if __name__ == "__main__":
    main()
