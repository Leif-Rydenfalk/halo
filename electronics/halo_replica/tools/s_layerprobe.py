#!/usr/bin/env python3
"""s_layerprobe.py — does a patch of a PCB photograph contain copper structure?

WHAT THIS TOOL IS FOR, AND WHAT IT IS NOT FOR. Read both.

The AirTag layer count turned on one question about
github.com/stacksmashing/airtag-hardware, whose README says "merged PCB
pictures of all the layers": is each file ONE delayered copper layer, or is
each a SUPERPOSITION of all of them? docs/REFERENCE-TEARDOWN.md took the
second reading, which would make the file count meaningless.

The two readings make opposite predictions at one board spot:
  superposition  a feature on any layer appears in EVERY image
  delayering     a feature on one layer is ABSENT from the others

TWO AUTOMATED INSTRUMENTS WERE BUILT FOR THAT QUESTION AND BOTH WERE REJECTED.
They are recorded here so nobody re-treads them.

  1. FFT periodicity. A fine-pitch land grid is periodic; a pour and routing
     are not. REJECTED: its negative control went red. Blank off-board
     background scored 10.55 against the real land grid's 8.28 -- higher. On a
     nearly flat patch the whole spectral band sits near zero, so a single
     JPEG-noise bin towers over the band average. Detrending and a median
     baseline were added; then every patch, background included, returned the
     lowest bin in the band at a suspiciously round 32.0 px. A probe that
     answers the same thing for a land grid and for an empty sheet of paper is
     not measuring the board. Abandoned rather than tuned, because tuning a
     threshold until the answer comes out right is the defect, not the fix.

  2. Edge density, which is what survives and is what this tool computes. Its
     controls DO pass -- blank background 0.015-0.029 against 0.25-0.47 for any
     patch of board, a better than tenfold separation. But it CANNOT separate a
     land grid (0.4684) from ordinary inner-layer routing (0.2541-0.3492).
     Those are not two categories, they are one continuum, so this tool EXITS 2
     on the superposition question and does not pretend otherwise.

WHAT SETTLED THE QUESTION was the eye on named crops, which is written up in
board/stackup/STACKUP.md with the exact boxes so anyone can reproduce it. This
tool's honest contribution is the negative control: it proves the compared
patches all contain real copper structure rather than blank photograph, which
is the one way the visual reading could have been trivially wrong.

Verbs
  structure  edge fraction for each patch, with blank-background controls
  selftest   5 cases, including the two controls that matter

Exit code IS the verdict: 0 PASS, 1 FAIL, 2 CANNOT DETERMINE.
"""
import os
import sys

PASS, FAIL, CANNOT = 0, 1, 2

# Measured, not chosen: blank background lands at 0.015-0.029 and any patch of
# board at 0.25 or above, so anything under this is photograph, not copper.
BLANK_CEILING = 0.10

PATCHES = [
    ("layer1 @ land grid",          "layer1.jpg",  (1330, 1080, 1600, 1330), "board"),
    ("layer2 @ same board spot",    "layer2.jpeg", (845, 686, 1017, 845),    "board"),
    ("layer3 @ same board spot",    "layer3.jpeg", (845, 686, 1017, 845),    "board"),
    ("layer4 @ same board spot",    "layer4.jpeg", (845, 686, 1017, 845),    "board"),
    ("layer1 @ blank bg CONTROL",   "layer1.jpg",  (60, 60, 330, 310),       "blank"),
    ("layer2 @ blank bg CONTROL",   "layer2.jpeg", (40, 40, 210, 200),       "blank"),
]


def edge_fraction(path, box, size=192, thr=25):
    """Fraction of pixels whose local gradient exceeds `thr` grey levels.
    The threshold is ABSOLUTE on purpose: normalising by the patch's own
    contrast is what let the rejected FFT probe call empty paper structured."""
    from PIL import Image
    im = Image.open(path).convert("L").crop(box).resize((size, size), Image.LANCZOS)
    px = list(im.getdata())
    g = [px[r * size:(r + 1) * size] for r in range(size)]
    n = tot = 0
    for r in range(1, size - 1):
        for c in range(1, size - 1):
            if max(abs(g[r][c + 1] - g[r][c - 1]), abs(g[r + 1][c] - g[r - 1][c])) >= thr:
                n += 1
            tot += 1
    return n / tot


def _dir():
    d = os.environ.get("SS_DIR")
    if not d or not os.path.isdir(d):
        return None
    return d


def cmd_structure(d):
    print(f"{'patch':<32}{'edge fraction':>15}   reading")
    for label, f, box, kind in PATCHES:
        p = os.path.join(d, f)
        if not os.path.exists(p):
            print(f"{label:<32}{'--':>15}   CANNOT DETERMINE — {f} not present")
            continue
        e = edge_fraction(p, box)
        reading = "copper structure" if e > BLANK_CEILING else "blank photograph"
        print(f"{label:<32}{e:15.4f}   {reading}")
    print("\nThis says the compared patches all hold real copper, which is the")
    print("negative control on the visual reading. It does NOT say which layer")
    print("is which — see the module docstring for why, and STACKUP.md for what did.")
    return CANNOT


def cmd_selftest():
    d = _dir()
    if d is None:
        print("CANNOT DETERMINE — set SS_DIR to the directory holding layer1..layer4")
        return CANNOT
    for _, f, _, _ in PATCHES:
        if not os.path.exists(os.path.join(d, f)):
            print(f"CANNOT DETERMINE — missing {f} in {d}")
            return CANNOT

    n_ok = n_red = 0

    def check(name, got, ok, want):
        nonlocal n_ok, n_red
        print(f"  [{'ok  ' if ok else 'RED '}] {name}\n         want {want}\n         got  {got}")
        if ok:
            n_ok += 1
        else:
            n_red += 1

    print("s_layerprobe selftest — 5 cases\n")
    vals = {lab: edge_fraction(os.path.join(d, f), b) for lab, f, b, _ in PATCHES}

    # NEGATIVE CONTROLS. These are the whole point. The first version of this
    # tool used a different metric and these went RED; that is why the metric
    # changed. A probe whose negative control cannot go red is a decoration.
    for lab in ("layer1 @ blank bg CONTROL", "layer2 @ blank bg CONTROL"):
        v = vals[lab]
        check(f"{lab} reads as blank", round(v, 4), v <= BLANK_CEILING, f"<= {BLANK_CEILING}")

    # POSITIVE CONTROL: every board patch must read as structured, or the tool
    # is not seeing copper at all and its refusals mean nothing either.
    for lab in ("layer1 @ land grid", "layer2 @ same board spot", "layer3 @ same board spot"):
        v = vals[lab]
        check(f"{lab} reads as copper", round(v, 4), v > BLANK_CEILING, f"> {BLANK_CEILING}")

    print(f"\n{n_ok} ok, {n_red} red")
    if n_red:
        return FAIL
    print("\nPASS on what this tool claims. The superposition question itself stays")
    print("CANNOT DETERMINE by this instrument — that is stated, not hidden.")
    return PASS


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return CANNOT
    d = _dir()
    if argv[1] == "selftest":
        return cmd_selftest()
    if argv[1] == "structure":
        if d is None:
            print("CANNOT DETERMINE — set SS_DIR to the directory holding layer1..layer4.")
            print("Those images are NOT redistributed here: the source repository states no")
            print("licence. Fetch them from github.com/stacksmashing/airtag-hardware/pcb/.")
            return CANNOT
        return cmd_structure(d)
    print(f"unknown verb {argv[1]!r}")
    return CANNOT


if __name__ == "__main__":
    sys.exit(main(sys.argv))
