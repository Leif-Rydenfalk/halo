#!/usr/bin/env python3
"""m_selftest.py -- synthetic ground truth and deliberate breaks for the L1 tools.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.

Every case states the ANSWER IT SHOULD GET and fails loudly if it does not.
Half of them exist to make a check GO RED on purpose, because an assertion never
seen to fail is not known to work.

The case that matters most is SIX PADS: M03 says the rim-pad count is CANNOT
DETERMINE because of RESOLUTION, not because the detector is broken. That is a
claim about the detector, and it was asserted, not shown. So this file builds a
synthetic rim at photo 6's real scale (r = 196 px, the measured luma statistics)
carrying SIX pads of a stated size, and requires the detector to find them and
beat its own control.  If it cannot, M03's explanation is wrong and says so.

Run:  python3 m_selftest.py            exit 0 all passed, 1 any failed
"""
import math, os, sys, tempfile
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m_ruler_calib as RC
import m_outline_fit as OF
import m_rim_pads as RP

RESULTS = []


def check(name, ok, detail):
    RESULTS.append((name, ok, detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")


# ---------------------------------------------------------------- rulers ----
def synth_ruler(pitch, n_ticks=110, h=40, noise=4.0, seed=1):
    rng = np.random.default_rng(seed)
    w = int(pitch * (n_ticks + 4))
    img = np.full((h + 60, w), 170.0)
    for i in range(n_ticks):
        x = int(round(pitch * (i + 2)))
        depth = h if i % 10 == 0 else (h * 3 // 5 if i % 5 == 0 else h // 3)
        img[10:10 + depth, x:x + max(1, int(pitch // 8))] = 35.0
    img[:8, :] = 245.0                                    # paper above the rule
    return np.clip(img + rng.normal(0, noise, img.shape), 0, 255)


def test_rulers():
    print("\nRULER PITCH -- m_ruler_calib")
    for pitch in (15.8875, 12.0, 20.5):
        img = synth_ruler(pitch)
        edge = RC.find_edge(img, "x", (0, 30), (0, img.shape[1]))
        box = (5, edge + 6, img.shape[1] - 5, edge + 6 + 18)
        fit, ang, snr, p0, n = RC.comb(img, box, "x", 8.0, 40.0)
        if fit is None:
            check(f"recover a {pitch} px comb", False,
                  f"no comb found at all (band {box}) -- the tool returned None")
            continue
        got = fit["pitch"]
        err = abs(got - pitch) / pitch * 100
        check(f"recover a {pitch} px comb", err < 0.5,
              f"got {got:.4f} px ({err:.3f}% error), {fit['n']} ticks, resid sd {fit['sd']:.3f} px")

    print("\n  DELIBERATE BREAK -- reading the wrong band")
    img = synth_ruler(15.8875)
    edge = RC.find_edge(img, "x", (0, 30), (0, img.shape[1]))
    box = (5, edge + 30, img.shape[1] - 5, edge + 30 + 12)   # below the mm ticks
    fit, *_ = RC.comb(img, box, "x", 8.0, 60.0)
    cov = fit["n"] / (fit["span"] + 1) if fit else 0.0
    check("the wrong band is caught by the coverage gate",
          fit is None or cov < 0.85 or abs(fit["pitch"] - 15.8875) / 15.8875 > 0.02,
          f"pitch {fit['pitch']:.3f} px, coverage {cov:.3f} -- this band holds the 5-mm ticks, "
          if fit else "no comb at all in that band, which is also a refusal -- "
          f"and reading it as mm is the 4% error M02 Sec 5 records")

    print("\n  DELIBERATE BREAK -- pure noise must not yield a comb")
    rng = np.random.default_rng(7)
    img = np.clip(rng.normal(150, 30, (110, 1700)), 0, 255)
    d, off, ang = RC.band_signal(img, (5, 20, 1695, 44), "x")
    p0, snr = RC.fft_pitch(d, 8.0, 40.0)
    fit, *_ = RC.comb(img, (5, 20, 1695, 44), "x", 8.0, 40.0)
    cov = fit["n"] / (fit["span"] + 1) if fit else 0.0
    check("noise gives no trustworthy comb", snr < 12 or cov < 0.85,
          f"fft peak/median {snr:.1f}, coverage {cov:.3f} -- one of the two gates must reject it")


# ------------------------------------------------------------- outlines ----
def synth_disc(R=196.0, size=520, shadow=True, blur=1.2, seed=3, squircle_n=None,
               a=None, b=None):
    """A dark disc on bright paper, with a one-sided contact shadow if asked."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size]
    cx = cy = size / 2.0
    dx, dy = xx - cx, yy - cy
    if squircle_n:
        rr = (np.abs(dx / a) ** squircle_n + np.abs(dy / b) ** squircle_n) ** (-1.0 / squircle_n)
        inside = np.hypot(dx, dy) <= 1.0 / np.maximum(rr, 1e-9) * np.hypot(dx, dy) * 0 + \
                 ((np.abs(dx / a) ** squircle_n + np.abs(dy / b) ** squircle_n) <= 1.0)
    else:
        inside = np.hypot(dx, dy) <= R
    img = np.where(inside, 35.0, 240.0)
    if shadow:
        # a broad, gentle penumbra to the lower-left ONLY -- the real trap
        d = np.hypot(dx, dy)
        pen = np.clip(1 - (d - R) / 34.0, 0, 1) * (d > R)
        side = np.clip((-dx - dy) / (0.7 * R) + 0.25, 0, 1)
        img = img - 150.0 * pen * side
    img = ndimage.gaussian_filter(img, blur)
    return np.clip(img + rng.normal(0, 2.5, img.shape), 0, 255)


def measure_disc(img, method):
    bad = np.zeros(img.shape, bool)
    size = img.shape[0]
    cx = cy = size / 2.0
    rr = np.arange(1, size / 2 - 2, 0.5)
    prof = np.mean([OF.bilinear(img, cx + rr * np.cos(t), cy + rr * np.sin(t))
                    for t in np.linspace(0, 2 * math.pi, 180, endpoint=False)], axis=0)
    ab = prof > 150
    rises = [i for i in range(1, len(rr)) if ab[i] and not ab[i - 1]]
    r0 = float(rr[rises[-1]])
    for _ in range(3):
        pr, _d = OF.profile(img, bad, cx, cy, r0 * 0.88, r0 * 1.14, "out", 360)
        T = np.radians([t for t, _ in pr]); R = np.array([r for _, r in pr])
        ncx, ncy, nr, _, _ = OF.robust_circle(cx + R * np.cos(T), cy + R * np.sin(T))
        cx, cy = ncx, ncy
    pr, _d = OF.profile(img, bad, cx, cy, nr * 0.91, nr * 1.10, "out", 720, method)
    T = np.array([t for t, _ in pr]); R = np.array([r for _, r in pr])
    X, Y = cx + R * np.cos(np.radians(T)), cy + R * np.sin(np.radians(T))
    _, _, rad, res, keep = OF.robust_circle(X, Y)
    return rad, float(res[keep].std())


def test_outline():
    print("\nOUTER EDGE -- m_outline_fit, gradient vs the halfmax negative control")
    for R in (196.0, 150.0):
        img = synth_disc(R=R, shadow=False)
        rad, sd = measure_disc(img, "gradient")
        check(f"recover a clean disc r={R}", abs(rad - R) < 1.0,
              f"got r {rad:.3f} px (err {rad-R:+.3f}), resid sd {sd:.3f} px")

    img = synth_disc(R=196.0, shadow=True)
    rg, sg = measure_disc(img, "gradient")
    rh, sh = measure_disc(img, "halfmax")
    check("gradient survives a one-sided contact shadow", abs(rg - 196.0) < 2.0,
          f"got r {rg:.3f} px (err {rg-196:+.3f}), resid sd {sg:.3f} px")
    check("HALFMAX IS SEEN TO FAIL on the same image (this is the point)",
          abs(rh - 196.0) > 2.0 or sh > 2.5 * sg,
          f"halfmax got r {rh:.3f} px (err {rh-196:+.3f}), resid sd {sh:.3f} px vs "
          f"gradient's {sg:.3f} -- the shadow, exactly as M02 Sec 5 records")


def test_superellipse():
    print("\nSUPERELLIPSE -- m_outline_fit.fit_superellipse")
    for n_true in (2.0, 2.7, 4.0):
        t = np.linspace(0, 2 * math.pi, 720, endpoint=False)
        a_, b_ = 100.0, 96.0
        r = OF.se_radius(t, a_, b_, n_true)
        X, Y = 300 + r * np.cos(t), 300 + r * np.sin(t)
        p, res = OF.fit_superellipse(X, Y, 300, 300, 98.0)
        check(f"recover a squircle n={n_true}", abs(p["n"] - n_true) < 0.15,
              f"got n {p['n']:.3f}, a {p['a']:.2f} (true {a_}), b {p['b']:.2f} (true {b_}), "
              f"resid sd {np.std(res):.4f} px")
    t = np.linspace(0, 2 * math.pi, 720, endpoint=False)
    r = OF.se_radius(t, 100.0, 100.0, 2.0)
    X, Y = 300 + r * np.cos(t), 300 + r * np.sin(t)
    p, _ = OF.fit_superellipse(X, Y, 300, 300, 100.0)
    check("a true CIRCLE is not mistaken for a squircle", abs(p["n"] - 2.0) < 0.1,
          f"got n {p['n']:.4f} on a perfect circle -- must stay at 2.00")


# ------------------------------------------------------------- rim pads ----
def synth_rim(n_pads, R=196.0, size=520, pad_arc_mm=1.0, px_per_mm=15.685,
              contrast=110.0, seed=11, clutter=True, texture=0.0):
    """A dark annulus at photo 6's real scale carrying n_pads bright edge pads."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size]
    cx = cy = size / 2.0
    d = np.hypot(xx - cx, yy - cy)
    th = np.degrees(np.arctan2(yy - cy, xx - cx)) % 360
    img = np.where(d <= R, 42.0, 240.0)
    img = np.where(d <= R * 0.53, 250.0, img)                  # the centre hole
    if clutter:                                                # components, set back
        for k in range(26):
            a0 = rng.uniform(0, 360); w = rng.uniform(3, 9)
            r0 = rng.uniform(0.62, 0.93) * R; r1 = r0 + rng.uniform(6, 16)
            m = (np.abs((th - a0 + 180) % 360 - 180) < w / 2) & (d > r0) & (d < r1)
            img = np.where(m, rng.uniform(120, 210), img)
    pad_deg = 360.0 * (pad_arc_mm * px_per_mm) / (2 * math.pi * R)
    pads = [i * 360.0 / n_pads + 7.0 for i in range(n_pads)]
    for a0 in pads:                                            # pads run OUT TO the edge
        m = (np.abs((th - a0 + 180) % 360 - 180) < pad_deg / 2) & (d > R * 0.955) & (d <= R)
        img = np.where(m, 42.0 + contrast, img)
    if texture:
        # Correlated surface texture, so the SYNTHETIC rim has the same radial
        # luma variation as the real board rather than a laboratory-clean one.
        t = ndimage.gaussian_filter(rng.normal(0, 1, img.shape), 6.0)
        t = t / (t.std() + 1e-9)
        img = np.where(d <= R, img + texture * t, img)
    img = ndimage.gaussian_filter(img, 1.3)
    return np.clip(img + rng.normal(0, 3.0, img.shape), 0, 255), pads, R, (cx, cy)


def count_pads(img, cx, cy, R, mode="differential"):
    redge = lambda dd: np.full(np.shape(dd), R, float)
    P, ang, F = RP.polar(img, cx, cy, redge, 0.86, 1.00, 1440, 56)
    rng = np.random.default_rng(20260905)
    if mode == "differential":
        S = RP.differential(P, F, ang)
        pk, _, _, _ = RP.diff_peaks(S, 1440, 4.0, 3.0, 1.0)
        got = [dict(angle_deg=float(ang[i]), signal=v) for i, v in pk]
        ctrl = []
        for _ in range(20):
            Pp = np.stack([np.roll(P[j], int(rng.integers(1440))) for j in range(P.shape[0])])
            ctrl.append(len(RP.diff_peaks(RP.differential(Pp, F, ang), 1440, 4.0, 3.0, 1.0)[0]))
        return got, np.array(ctrl)
    thr = float(np.percentile(P, 80.0))
    B = RP.blobs(P, F, ang, thr, 40, 0.975, 1440)
    got = [b for b in B if b["reach"] >= 0.975 and b["span_deg"] >= 1.0]
    ctrl = []
    for _ in range(20):
        Pp = np.stack([np.roll(P[j], int(rng.integers(1440))) for j in range(P.shape[0])])
        Bp = RP.blobs(Pp, F, ang, thr, 40, 0.975, 1440)
        ctrl.append(len([b for b in Bp if b["reach"] >= 0.975 and b["span_deg"] >= 1.0]))
    return got, np.array(ctrl)


def test_rim_pads():
    print("\nRIM PADS -- m_rim_pads: can it find pads that ARE there, at photo 6's scale?")
    print("  (M03 blames RESOLUTION for the CANNOT DETERMINE. That is a claim about this")
    print("   detector, so it is tested here rather than asserted.)")
    img, pads, R, (cx, cy) = synth_rim(6, pad_arc_mm=1.6)
    got_b, ctrl_b = count_pads(img, cx, cy, R, "blob")
    check("THE ORIGINAL BLOB DETECTOR IS SEEN TO FAIL its positive control",
          len(got_b) < 5,
          f"6 real pads present, blob mode found {len(got_b)} -- its threshold (80th pct of "
          f"the annulus) lands just above the board level and everything merges. This case "
          f"exists so the failure stays reproducible.")
    for n_true, arc in ((6, 1.0), (6, 1.6), (12, 1.0)):
        img, pads, R, (cx, cy) = synth_rim(n_true, pad_arc_mm=arc)
        got, ctrl = count_pads(img, cx, cy, R)
        beats = len(got) > ctrl.max()
        near = sum(1 for a0 in pads
                   if any(abs((g["angle_deg"] - a0 + 180) % 360 - 180) < 4 for g in got))
        check(f"{n_true} synthetic pads of {arc} mm arc are found and beat the control",
              beats and near >= n_true - 1,
              f"found {len(got)} (control max {ctrl.max()}), {near}/{n_true} at the right angles")

    print("\n  IS THE POSITIVE CONTROL REPRESENTATIVE?  Measured: it was NOT.")
    print("  The clean synthetic rim has a differential robust sd of ~1.8 luma; FCC photo 6")
    print("  measures 34.6 and photo 7 measures 37.3.  A pad carrying the synthetic's full")
    print("  111-luma contrast would therefore sit at ~3.2 sigma in the real photograph, under")
    print("  the 4-sigma gate.  So the clean case proves the detector's LOGIC and nothing")
    print("  about whether it can work on THIS source. This case is the honest one.")
    img, pads, R, (cx, cy) = synth_rim(6, pad_arc_mm=1.6, texture=60.0)
    redge = lambda dd: np.full(np.shape(dd), R, float)
    P, ang, F = RP.polar(img, cx, cy, redge, 0.86, 1.00, 1440, 56)
    S = RP.differential(P, F, ang)
    ks = 5
    Ss = np.convolve(np.concatenate([S] * 3), np.ones(ks) / ks, mode="same")[len(S):2 * len(S)]
    sd_real_like = RP.robust_sd(Ss)
    got, ctrl = count_pads(img, cx, cy, R)
    near = sum(1 for a0 in pads
               if any(abs((g["angle_deg"] - a0 + 180) % 360 - 180) < 4 for g in got))
    check("at the REAL photograph's noise level the detector CANNOT find 6 real pads",
          not (len(got) > ctrl.max() and near >= 5),
          f"differential robust sd {sd_real_like:.1f} luma (FCC photo 6 measures 34.6); "
          f"found {len(got)} (control max {ctrl.max()}), {near}/6 at the right angles. "
          f"THIS is why M03 is CANNOT DETERMINE -- not the detector, the source.")

    print("\n  DELIBERATE BREAK -- no pads at all must NOT produce pads")
    img, _, R, (cx, cy) = synth_rim(0, clutter=True)
    got, ctrl = count_pads(img, cx, cy, R)
    check("a rim with ZERO pads does not beat its control", len(got) <= ctrl.max(),
          f"found {len(got)} spurious, control max {ctrl.max()} -- the detector must not "
          f"invent pads from clutter alone")


def main():
    print("m_selftest.py -- synthetic ground truth and deliberate breaks, L1 metrology lane")
    test_rulers()
    test_outline()
    test_superellipse()
    test_rim_pads()
    n = len(RESULTS); f = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"\n{n - f}/{n} passed, {f} failed")
    sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
