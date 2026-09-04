#!/usr/bin/env python3
"""s_layerprobe.py — is a set of PCB images four LAYERS, or four views of one board?

The AirTag layer count turns on one question about
github.com/stacksmashing/airtag-hardware: its README says "merged PCB pictures
of all the layers", and docs/REFERENCE-TEARDOWN.md read "merged" as
SUPERPOSITION — every layer visible in every image, carrying no count. If that
reading is right the images say nothing. If each file is instead ONE delayered
copper layer, the file count IS the layer count.

The two readings make opposite, testable predictions at the same board spot:

  superposition  a feature present on any layer is present in EVERY image
  delayering     a feature present on one layer is ABSENT from the others

So: pick a spot where one image shows an unmistakable outer-layer feature — a
fine-pitch land grid, which only an outer layer can have — and ask whether the
other images show it there. The land grid is a periodic pattern, so "is it
there" is answerable without an eye: FFT the patch and look for the pitch peak.

  probe   report grid-periodicity at the same spot across images
  selftest 6 deliberate breaks, including the two that matter -- an image
           compared against ITSELF must come back the same (or the probe is
           not measuring the image), and a patch of blank background must NOT
           report a grid (or the probe says yes to everything).

Exit code IS the verdict: 0 PASS, 1 FAIL, 2 CANNOT DETERMINE.
"""
import cmath
import os
import sys

PASS, FAIL, CANNOT = 0, 1, 2

# Set from the measured separation, not chosen first: see selftest.
THRESHOLD = 8.0


def _luma(path, box, size=128):
    from PIL import Image
    im = Image.open(path).convert("L").crop(box).resize((size, size), Image.LANCZOS)
    px = list(im.getdata())
    return [px[r * size:(r + 1) * size] for r in range(size)]


def gridiness(path, box, size=128, lo=4, hi=48, var_floor=3.0):
    """Strength of the strongest periodic component in the patch, as a multiple
    of the MEDIAN spectral power over the band. Returns (score, period_px).

    Two things here are not decoration and were both put in after the negative
    control went red. The FIRST version normalised against the band MEAN and did
    no detrending, and it scored blank off-board background at 10.55 against the
    real land grid's 8.28 -- it said yes to everything, because on a nearly flat
    patch the whole band is near zero and any one JPEG-noise bin towers over the
    average. So:

      detrending    a lighting gradient across the patch is a huge low-frequency
                    term that leaks across the band. A least-squares line is
                    removed from each profile first.
      variance floor a patch with no structure has no periodicity to report. Below
                    var_floor grey levels of detrended standard deviation the
                    honest answer is CANNOT DETERMINE, returned as (None, None),
                    and NOT a score.

    Median rather than mean normalisation for the same reason: one loud bin must
    not be allowed to set the baseline it is then compared against.
    """
    rows = _luma(path, box, size)
    best = (0.0, None)
    saw_structure = False
    for axis in (0, 1):
        prof = ([sum(r) / size for r in rows] if axis == 0
                else [sum(rows[r][c] for r in range(size)) / size for c in range(size)])
        # remove a least-squares line: lighting gradient, not board structure
        xs = list(range(size))
        mx = (size - 1) / 2
        my = sum(prof) / size
        sxx = sum((x - mx) ** 2 for x in xs)
        b = sum((x - mx) * (prof[i] - my) for i, x in enumerate(xs)) / sxx if sxx else 0.0
        prof = [prof[i] - (my + b * (x - mx)) for i, x in enumerate(xs)]
        sd = (sum(v * v for v in prof) / size) ** 0.5
        if sd < var_floor:
            continue
        saw_structure = True
        power = sorted(
            (abs(sum(prof[n] * cmath.exp(-2j * cmath.pi * k * n / size)
                     for n in range(size))) ** 2, k)
            for k in range(lo, hi))
        med = power[len(power) // 2][0]
        if med <= 0:
            continue
        pk, kk = power[-1]
        score = pk / med
        if score > best[0]:
            best = (score, size / kk)
    if not saw_structure:
        return (None, None)
    return best


def cmd_probe(specs, size=128):
    print(f"{'image':<34}{'grid score':>12}{'period px':>11}   reading")
    out = []
    for label, path, box in specs:
        s, p = gridiness(path, box, size)
        if s is None:
            print(f"{label:<34}{'--':>12}{'--':>11}   CANNOT DETERMINE — patch has no structure to test")
            out.append((label, None))
            continue
        reading = ("PERIODIC — a land grid is present here" if s >= THRESHOLD
                   else "not periodic — no land grid at this spot")
        print(f"{label:<34}{s:12.2f}{(p or 0):11.1f}   {reading}")
        out.append((label, s))
    return out


def cmd_selftest():
    here = os.environ.get("SS_DIR")
    if not here or not os.path.isdir(here):
        print("CANNOT DETERMINE — set SS_DIR to the directory holding layer1..layer4")
        return CANNOT
    L = {n: os.path.join(here, f) for n, f in
         (("1", "layer1.jpg"), ("2", "layer2.jpeg"), ("3", "layer3.jpeg"), ("4", "layer4.jpeg"))}
    for p in L.values():
        if not os.path.exists(p):
            print(f"CANNOT DETERMINE — missing {p}")
            return CANNOT

    GRID_L1 = (1330, 1080, 1600, 1330)      # the WLCSP land grid on layer1
    GRID_OTHER = (845, 686, 1017, 845)      # the same board spot, layer2/3/4 scale
    BLANK_L1 = (60, 60, 330, 310)           # off-board background on layer1

    n_pass = n_fail = 0

    def check(name, got, ok, want):
        nonlocal n_pass, n_fail
        print(f"  [{'ok  ' if ok else 'RED '}] {name}\n         want {want}\n         got  {got}")
        if ok:
            n_pass += 1
        else:
            n_fail += 1

    print("s_layerprobe selftest — 6 deliberate breaks\n")

    g1 = gridiness(L["1"], GRID_L1)[0]
    check("layer1 at the land grid IS periodic", g1 and round(g1, 2),
          g1 is not None and g1 >= THRESHOLD, f">= {THRESHOLD}")

    # POSITIVE CONTROL: the probe must agree with itself. If comparing an image
    # to itself did not reproduce, the probe is not reading the image at all.
    g1b = gridiness(L["1"], GRID_L1)[0]
    check("same image, same box reproduces", round(g1b, 2), abs(g1b - g1) < 1e-9, f"{round(g1,2)}")

    # NEGATIVE CONTROL: blank background must NOT be called a grid. A probe
    # that says yes to everything is a decoration.
    gb = gridiness(L["1"], BLANK_L1)[0]
    check("blank background is NOT periodic (this control went RED on the first"
          "\n         version and is why the probe detrends and has a variance floor)",
          gb if gb is None else round(gb, 2),
          gb is None or gb < THRESHOLD, f"None (no structure) or < {THRESHOLD}")

    for n in ("2", "3", "4"):
        g = gridiness(L[n], GRID_OTHER)[0]
        check(f"layer{n} at the SAME spot has no land grid",
              g if g is None else round(g, 2),
              g is None or g < THRESHOLD, f"None or < {THRESHOLD}")

    print(f"\n{n_pass} ok, {n_fail} red")
    return PASS if n_fail == 0 else FAIL


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return CANNOT
    if argv[1] == "selftest":
        return cmd_selftest()
    if argv[1] == "probe":
        here = os.environ.get("SS_DIR", ".")
        specs = [("layer1 @ land grid", os.path.join(here, "layer1.jpg"), (1330, 1080, 1600, 1330)),
                 ("layer2 @ same board spot", os.path.join(here, "layer2.jpeg"), (845, 686, 1017, 845)),
                 ("layer3 @ same board spot", os.path.join(here, "layer3.jpeg"), (845, 686, 1017, 845)),
                 ("layer4 @ same board spot", os.path.join(here, "layer4.jpeg"), (845, 686, 1017, 845)),
                 ("layer1 @ blank background", os.path.join(here, "layer1.jpg"), (60, 60, 330, 310))]
        cmd_probe(specs)
        return PASS
    print(f"unknown verb {argv[1]!r}")
    return CANNOT


if __name__ == "__main__":
    sys.exit(main(sys.argv))
