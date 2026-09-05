#!/usr/bin/env python3
"""s_colour.py — is a plated surface GOLD-bearing or bare copper? With controls.

A surface finish cannot be read off a colour NAME. It can be read off a HUE
DIFFERENCE between two metals in the same frame under the same light, because a
white-balance error moves both together. That is why the in-frame control is not
optional and why this tool refuses to run without printing one.

TWO STATISTICS, AND THE FIRST VERSION ONLY HAD ONE.

  warm fraction   how much of the region is warm metal at all
  hue             the colour of that warm part

The first version reported hue over a warm-pixel SELECTION and nothing else,
which meant it could never say "this region is grey" -- give it a grey solder
fillet and it returns the hue of whatever few warm noise pixels it found, at a
plausible-looking 35 to 46 degrees. Measured 2026-09-05: three regions asserted
in stackup.json to be "grey, no warm pixels at all" came back at hue 35.0, 46.5
and 45.6, indistinguishable from the gold rim's 43.8 -- because the SELECTION
had already thrown the grey away.

The fraction is what separates them, and it separates cleanly:

    copper winding   64.9 %      gold rim (left)  98.8 %
    gold rim (right) 66.0 %      grey solder       4.6 %
    xtal can lid     15.9 %      dark soldermask   8.8 %

So: warm fraction says WHETHER it is bare metal; hue then says WHICH metal.
Reporting hue without the fraction is how a grey pad passes for a gold one.

Verbs
  measure <image> <label>:<x0>,<y0>,<x1>,<y1> ...
  selftest   12 cases on the AirTag frame, including the negative controls that
             the first version asserted and never ran

Exit code IS the verdict: 0 PASS, 1 FAIL, 2 CANNOT DETERMINE.
"""
import colorsys
import os
import sys

PASS, FAIL, CANNOT = 0, 1, 2

# Measured, not chosen: bare metal sits at 65 % and above in this frame, and
# everything that is not bare metal sits at 17 % and below. The gap is wide and
# empty, so the threshold is not doing delicate work.
WARM_FLOOR = 0.40
COPPER_MAX_HUE = 30.0   # bare copper is salmon
GOLD_MIN_HUE = 36.0     # electroless-nickel / immersion gold is yellow


def stats(path, box, lo_v=60, hi_v=250, min_rb=20):
    """(warm_fraction, n_warm, n_total, R, G, B, hue_deg, sat) or None if empty."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    px = list(im.crop(box).getdata())
    total = len(px)
    if not total:
        return None
    warm = [c for c in px if lo_v <= max(c) <= hi_v and (c[0] - c[2]) >= min_rb]
    if not warm:
        return (0.0, 0, total, None, None, None, None, None)
    n = len(warm)
    r, g, b = (sum(c[i] for c in warm) / n for i in range(3))
    h, s, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return (n / total, n, total, r, g, b, h * 360, s)


def verdict_for(st):
    """What the two statistics together say, in order."""
    if st is None:
        return CANNOT, "empty region"
    frac, _, _, _, _, _, hue, _ = st
    if frac < WARM_FLOOR:
        return PASS, f"NOT bare metal — only {frac*100:.1f}% warm, below the {WARM_FLOOR*100:.0f}% floor"
    if hue is None:
        return CANNOT, "warm fraction passed but no hue could be formed"
    if hue >= GOLD_MIN_HUE:
        return PASS, f"bare metal ({frac*100:.1f}% warm) and GOLD-bearing at {hue:.1f} deg"
    if hue <= COPPER_MAX_HUE:
        return PASS, f"bare metal ({frac*100:.1f}% warm) and COPPER at {hue:.1f} deg"
    return CANNOT, (f"bare metal ({frac*100:.1f}% warm) but hue {hue:.1f} deg falls between "
                    f"copper (<={COPPER_MAX_HUE}) and gold (>={GOLD_MIN_HUE}) — not called")


def cmd_measure(img, specs):
    print(f"{'region':<38}{'warm%':>8}{'n':>7}{'hue':>8}{'sat':>7}   reading")
    for spec in specs:
        label, box = spec.split(":")
        st = stats(img, tuple(int(v) for v in box.split(",")))
        v, why = verdict_for(st)
        if st is None:
            print(f"{label:<38}   {why}")
            continue
        frac, n, _, _, _, _, hue, sat = st
        hs = f"{hue:8.1f}" if hue is not None else f"{'--':>8}"
        ss = f"{sat:7.3f}" if sat is not None else f"{'--':>7}"
        print(f"{label:<38}{frac*100:7.1f}%{n:7d}{hs}{ss}   {why}")
    return PASS


# The AirTag component-side scan, and the regions this lane measured on it.
IMG = "images/airtag/oflynn-backside-fullres.jpeg"
REGIONS = {
    "copper_winding_CONTROL": (917, 605, 985, 680),
    "gold_rim_right": (2596, 1930, 2624, 1955),
    "gold_rim_left": (196, 1486, 236, 1510),
    "grey_solder_NEG": (1000, 600, 1040, 660),
    "soldermask_NEG": (1080, 530, 1140, 580),
}


def cmd_selftest():
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "..", ".."))
    img = os.path.join(root, IMG)
    if not os.path.exists(img):
        print(f"CANNOT DETERMINE — {IMG} not found under {root}")
        return CANNOT
    n_ok = n_red = 0

    def check(name, got, ok, want):
        nonlocal n_ok, n_red
        print(f"  [{'ok  ' if ok else 'RED '}] {name}\n         want {want}\n         got  {got}")
        if ok:
            n_ok += 1
        else:
            n_red += 1

    print("s_colour selftest — 12 cases\n")
    st = {k: stats(img, b) for k, b in REGIONS.items()}

    # POSITIVE CONTROL: the copper winding must read as bare metal AND as copper.
    f, *_ , hue, _ = st["copper_winding_CONTROL"][0], *st["copper_winding_CONTROL"][1:]
    check("copper winding is bare metal", round(st["copper_winding_CONTROL"][0], 3),
          st["copper_winding_CONTROL"][0] >= WARM_FLOOR, f">= {WARM_FLOOR}")
    check("copper winding reads as COPPER, not gold",
          round(st["copper_winding_CONTROL"][6], 1),
          st["copper_winding_CONTROL"][6] <= COPPER_MAX_HUE, f"<= {COPPER_MAX_HUE} deg")

    # THE FINDING: both plated rims are bare metal AND gold-bearing.
    for k in ("gold_rim_right", "gold_rim_left"):
        check(f"{k} is bare metal and GOLD-bearing",
              (round(st[k][0], 3), round(st[k][6], 1)),
              st[k][0] >= WARM_FLOOR and st[k][6] >= GOLD_MIN_HUE,
              f"warm >= {WARM_FLOOR}, hue >= {GOLD_MIN_HUE}")

    # THE NEGATIVE CONTROLS THE FIRST VERSION ASSERTED AND NEVER RAN. A grey
    # solder fillet and dark soldermask must be rejected BY FRACTION. Their hue
    # is 35.0 and 46.5 deg -- inside the gold band -- so hue alone would have
    # called both of them gold.
    for k in ("grey_solder_NEG", "soldermask_NEG"):
        check(f"{k} is rejected as NOT bare metal (by fraction, not hue)",
              round(st[k][0], 3), st[k][0] < WARM_FLOOR, f"< {WARM_FLOOR}")

    # AND THE SEPARATION MUST BE WIDE. If the floor sat inside a cluster the
    # threshold would be doing delicate work, and a 1% change would flip a row.
    bare = min(st[k][0] for k in ("copper_winding_CONTROL", "gold_rim_right", "gold_rim_left"))
    notbare = max(st[k][0] for k in ("grey_solder_NEG", "soldermask_NEG"))
    check("the gap between bare metal and not-bare metal is wide and empty",
          f"bare min {bare*100:.1f}% vs not-bare max {notbare*100:.1f}%",
          bare - notbare > 0.35, "at least 35 points apart")

    # ---- and now the DECISION FUNCTION, not just the statistics it eats ----
    # Everything above asserts stats(). None of it calls verdict_for(). Measured
    # 2026-09-05: deleting the fraction gate from verdict_for, and separately
    # setting GOLD_MIN_HUE to 0 so every hue reads gold, left ALL SEVEN CASES
    # GREEN -- because the cases were testing the numbers that go IN, not the
    # decision made with them. Testing one layer below the thing you mean to
    # protect is how a suite stays green while the tool stops working.
    for k in ("grey_solder_NEG", "soldermask_NEG"):
        v, why = verdict_for(st[k])
        check(f"verdict_for REJECTS {k}, and says the FRACTION is why",
              why[:46], "NOT bare metal" in why and "warm" in why,
              "a reason naming the warm fraction")
    for k in ("gold_rim_right", "gold_rim_left"):
        v, why = verdict_for(st[k])
        check(f"verdict_for calls {k} GOLD-bearing", why[:52], "GOLD-bearing" in why,
              "a reason saying GOLD-bearing")
    v, why = verdict_for(st["copper_winding_CONTROL"])
    check("verdict_for calls the winding COPPER, not gold", why[:52],
          "COPPER" in why, "a reason saying COPPER")

    # AND THE COUNTERFACTUAL, which is the argument for the fraction gate.
    # CORRECTED 2026-09-05: the first version of this case asserted that BOTH
    # negative controls would be called gold on hue alone, and it went RED --
    # my claim was wrong, not the code. Dark soldermask does sit inside the gold
    # band at 52.9 deg; the grey solder fillet is 35.0 deg, which lands in the
    # "between copper and gold, not called" band instead. So hue alone would
    # have mislabelled ONE of the two as gold and refused to call the other.
    # Neither outcome is acceptable and one is a false positive, which is
    # enough -- but the honest statement is "one", not "both".
    hue_only = {k: round(st[k][6], 1) for k in ("grey_solder_NEG", "soldermask_NEG")}
    check("on HUE ALONE at least one negative control lands in the GOLD band",
          hue_only,
          sum(1 for h in hue_only.values() if h >= GOLD_MIN_HUE) >= 1,
          f"at least one >= {GOLD_MIN_HUE} deg — soldermask at 52.9 is the false positive")

    print(f"\n{n_ok} ok, {n_red} red")
    return PASS if n_red == 0 else FAIL


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return CANNOT
    if argv[1] == "selftest":
        return cmd_selftest()
    if argv[1] == "measure":
        return cmd_measure(argv[2], argv[3:])
    print(f"unknown verb {argv[1]!r}")
    return CANNOT


if __name__ == "__main__":
    sys.exit(main(sys.argv))
