#!/usr/bin/env python3
"""m_ruler_calib.py -- px/mm from a steel rule's mm ticks, by periodic signal.

L1 PHOTOGRAPH METROLOGY lane, halo Replica.  Re-runnable, prints its inputs.

METHOD (stated so a reader can attack it):
  1. FIND THE RULE EDGE, per image.  Do not hardcode a band: the two FCC
     photographs place the same rules ~18 px apart and a hardcoded strip
     silently reads the 5-mm ticks instead of the mm ticks (this happened;
     it produced a 4% error -- see M02 "what I discarded").
  2. SCAN candidate tick bands below/right of that edge and keep the one whose
     FFT peak-to-median ratio is highest -- i.e. the band where the mm comb is
     the strongest periodic signal present.
  3. DESKEW by projecting along candidate angles and maximising projection
     variance (sharpest = parallel to the ticks).
  4. FFT the high-passed projection -> coarse pitch.
  5. Locate EVERY tick as a sub-pixel dark centroid, assign each an INTEGER
     index from the coarse pitch, then least-squares  pos = a*index + b  over
     all of them.  Slope `a` is a pitch averaged over the whole span; the
     residual is the honest uncertainty.  No two hand-picked ticks anywhere.
  6. CHECKS, all of which can fail:
     - split-half: fit the first and second halves separately; they must agree
     - index coverage: n_ticks / (span+1); a comb with holes is suspect
     - the 5-mm comb: a deeper band contains only the long ticks, whose pitch
       must come out 5x the mm pitch.  This is an independent periodicity in
       the same photograph and it is not fitted to the first.
"""
import argparse, json, math, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
IMGDIR = os.path.join(ROOT, "images", "airtag")


def load_gray(path):
    return np.asarray(Image.open(path).convert("L")).astype(np.float64)


def find_edge(img, axis, search, along):
    """Locate the rule's edge: the strongest bright->dark step.

    axis 'x' -> horizontal rule, edge is a row.  axis 'y' -> edge is a column.
    """
    a0, a1 = along
    prof = img[:, a0:a1].mean(1) if axis == "x" else img[a0:a1, :].mean(0)
    k = 5
    sm = np.convolve(prof, np.ones(k) / k, mode="same")
    g = np.gradient(sm)
    s0, s1 = search
    seg = g[s0:s1]
    return int(s0 + np.argmin(seg))


def project(strip, angle_deg, axis):
    if axis == "y":
        strip = strip.T
    h, w = strip.shape
    t = math.tan(math.radians(angle_deg))
    xs = np.arange(w)
    acc = np.zeros(w); cnt = np.zeros(w)
    mid = (h - 1) / 2.0
    for r in range(h):
        src = xs + t * (r - mid)
        i0 = np.floor(src).astype(int)
        f = src - i0
        ok = (i0 >= 0) & (i0 + 1 < w)
        np.add.at(acc, i0[ok], strip[r, ok] * (1 - f[ok]))
        np.add.at(acc, i0[ok] + 1, strip[r, ok] * f[ok])
        np.add.at(cnt, i0[ok], 1 - f[ok])
        np.add.at(cnt, i0[ok] + 1, f[ok])
    good = cnt > 0.5 * h
    out = np.full(w, np.nan); out[good] = acc[good] / cnt[good]
    return out


def highpass(sig, k=25):
    return sig - np.convolve(sig, np.ones(k) / k, mode="same")


def fft_pitch(d, pmin, pmax):
    n = len(d)
    F = np.abs(np.fft.rfft((d - d.mean()) * np.hanning(n)))
    fr = np.fft.rfftfreq(n, 1.0)
    ok = (fr > 1.0 / pmax) & (fr < 1.0 / pmin)
    idx = np.where(ok)[0]
    j = idx[int(np.argmax(F[idx]))]
    if 0 < j < len(F) - 1 and (F[j-1] - 2*F[j] + F[j+1]) != 0:
        dj = 0.5 * (F[j-1] - F[j+1]) / (F[j-1] - 2*F[j] + F[j+1])
    else:
        dj = 0.0
    f = fr[j] + dj * (fr[1] - fr[0])
    return 1.0 / f, float(F[j] / np.median(F[idx]))


def band_signal(img, box, axis, angle=None):
    x0, y0, x1, y1 = box
    strip = img[y0:y1, x0:x1]
    if angle is None:
        def score(a):
            p = project(strip, a, axis); p = p[np.isfinite(p)]
            if p.size < 50: return -1.0
            d = highpass(p)[25:-25]
            return float(np.var(d))
        g1 = np.arange(-2.0, 2.001, 0.25)
        a0 = g1[int(np.argmax([score(a) for a in g1]))]
        g2 = np.arange(a0 - 0.25, a0 + 0.2501, 0.02)
        angle = float(g2[int(np.argmax([score(a) for a in g2]))])
    p = project(strip, angle, axis)
    fin = np.isfinite(p)
    lo, hi = int(np.argmax(fin)), len(p) - int(np.argmax(fin[::-1]))
    return highpass(p[lo:hi]), lo, angle


def tick_centroids(d, pitch):
    v = -d
    thr = 0.35 * np.nanmax(v)
    half = max(2, int(round(pitch * 0.30)))
    out, n = [], len(v)
    for i in range(half, n - half):
        if not np.isfinite(v[i]) or v[i] < thr: continue
        seg = v[i-half:i+half+1]
        if not np.all(np.isfinite(seg)): continue
        if v[i] >= seg.max() - 1e-12:
            w = np.clip(seg, 0, None)
            if w.sum() <= 0: continue
            xs = np.arange(i-half, i+half+1)
            c = float((xs * w).sum() / w.sum())
            if out and c - out[-1] < 0.5 * pitch: continue
            out.append(c)
    return np.array(out)


def fit_pitch(pos, pitch0):
    idx = np.round((pos - pos[0]) / pitch0).astype(int)
    keep = np.concatenate([[True], np.diff(idx) > 0])
    pos, idx = pos[keep], idx[keep]
    A = np.vstack([idx, np.ones_like(idx)]).T.astype(float)
    for _ in range(3):
        sol, *_ = np.linalg.lstsq(A, pos, rcond=None)
        r = pos - A @ sol; s = r.std()
        if s < 1e-9: break
        good = np.abs(r) < 3 * s
        if good.sum() < 10 or good.all(): break
        A, pos, idx = A[good], pos[good], idx[good]
    sol, *_ = np.linalg.lstsq(A, pos, rcond=None)
    r = pos - A @ sol
    xm = A[:, 0].mean(); sxx = ((A[:, 0] - xm) ** 2).sum()
    sig = r.std(ddof=2) if len(pos) > 2 else float("nan")
    return dict(pitch=float(sol[0]), b=float(sol[1]), n=int(len(pos)),
                span=int(idx.max() - idx.min()), sd=float(sig),
                rmax=float(np.abs(r).max()),
                se=float(sig / math.sqrt(sxx)) if sxx > 0 else float("nan"),
                pos=pos, idx=idx)


def comb(img, box, axis, pmin, pmax, angle=None):
    d, off, ang = band_signal(img, box, axis, angle)
    p0, snr = fft_pitch(d, pmin, pmax)
    pos = tick_centroids(d, p0)
    if len(pos) < 8:
        return None, ang, snr, p0, len(pos)
    return fit_pitch(pos + off, p0), ang, snr, p0, len(pos)


def measure_rule(path, name, axis, along, search, verbose=True):
    img = load_gray(path)
    edge = find_edge(img, axis, search, along)
    a0, a1 = along
    # --- 2. scan candidate mm-tick bands -------------------------------------
    best = None
    for start in range(4, 26, 2):
        for depth in (18, 24, 30):
            o0, o1 = edge + start, edge + start + depth
            box = (a0, o0, a1, o1) if axis == "x" else (o0, a0, o1, a1)
            try:
                d, _, ang = band_signal(img, box, axis)
                _, snr = fft_pitch(d, 8.0, 40.0)
            except Exception:
                continue
            if best is None or snr > best[0]:
                best = (snr, box, start, depth)
    snr_scan, box, start, depth = best
    fit, ang, snr, p0, ncand = comb(img, box, axis, 8.0, 40.0)
    if fit is None:
        return dict(name=name, verdict="CANNOT DETERMINE",
                    reason=f"only {ncand} tick candidates in the best band {box}")
    pitch = fit["pitch"]
    # --- 6a. split-half ------------------------------------------------------
    m = len(fit["pos"]) // 2
    halves = []
    for sl in (slice(0, m), slice(m, None)):
        p, i = fit["pos"][sl], fit["idx"][sl]
        A = np.vstack([i, np.ones_like(i)]).T.astype(float)
        s, *_ = np.linalg.lstsq(A, p, rcond=None)
        halves.append(float(s[0]))
    # --- 6b. the 5-mm comb, deeper band, independent -------------------------
    five = None
    o0 = edge + start + depth + 6
    box5 = (a0, o0, a1, o0 + 22) if axis == "x" else (o0, a0, o0 + 22, a1)
    try:
        f5, _, snr5, p5, n5 = comb(img, box5, axis, 4.0 * pitch, 7.0 * pitch, ang)
        if f5 is not None and f5["n"] >= 8:
            five = dict(box=list(box5), pitch_px=f5["pitch"], n=f5["n"],
                        sd_px=f5["sd"],
                        implied_mm_pitch_px=f5["pitch"] / 5.0,
                        ratio_to_mm=f5["pitch"] / 5.0 / pitch)
    except Exception as e:
        five = dict(error=str(e))
    r = dict(
        name=name, verdict="MEASURED", image=os.path.relpath(path, ROOT),
        rule_edge_px=edge, tick_band_xyxy=list(box), band_offset_from_edge=start,
        band_depth=depth, projection_axis=axis, deskew_angle_deg=round(ang, 3),
        fft_pitch_px=round(p0, 4), fft_peak_over_median=round(snr, 1),
        px_per_mm=pitch, px_per_mm_stderr=fit["se"],
        n_ticks=fit["n"], span_mm=fit["span"],
        coverage=round(fit["n"] / (fit["span"] + 1), 4),
        resid_sd_px=fit["sd"], resid_max_px=fit["rmax"],
        split_half_px_per_mm=[round(h, 4) for h in halves],
        split_half_delta_pct=round(100 * abs(halves[0] - halves[1]) / pitch, 3),
        five_mm_comb=five,
    )
    if verbose:
        print(f"  {name}: {os.path.basename(path)}")
        print(f"    rule edge auto-found at {axis}={edge}; best mm band {box} "
              f"(offset +{start}, depth {depth}), fft peak/median {snr:.0f}")
        print(f"    deskew {ang:+.3f} deg | fft pitch {p0:.3f} px")
        print(f"    {fit['n']} ticks over {fit['span']} mm, coverage "
              f"{r['coverage']:.3f} | resid sd {fit['sd']:.3f} px max {fit['rmax']:.3f} px")
        print(f"    split-half {halves[0]:.4f} / {halves[1]:.4f} px/mm "
              f"({r['split_half_delta_pct']:.3f}% apart)")
        if five and "pitch_px" in five:
            print(f"    5-mm comb (independent, deeper band): {five['pitch_px']:.3f} px "
                  f"/5 = {five['implied_mm_pitch_px']:.4f} px/mm, "
                  f"ratio {five['ratio_to_mm']:.5f} of the mm comb ({five['n']} ticks)")
        else:
            print(f"    5-mm comb: CANNOT DETERMINE ({five})")
        print(f"    ==> PX/MM = {pitch:.4f} +/- {fit['se']:.4f} (fit stderr)")
    return r


RULES = {
    "photo6_bottom": ("fcc-BCGA2187-internal-photo-6.jpg", "x", (400, 2000), (1080, 1180)),
    "photo6_right":  ("fcc-BCGA2187-internal-photo-6.jpg", "y", (100, 900),  (1480, 1580)),
    "photo7_bottom": ("fcc-BCGA2187-internal-photo-7.jpg", "x", (400, 2000), (1060, 1160)),
    "photo7_right":  ("fcc-BCGA2187-internal-photo-7.jpg", "y", (100, 900),  (1500, 1600)),
    "photo1_bottom": ("fcc-BCGA2187-internal-photo-1.jpg", "x", (400, 2000), (1040, 1200)),
    "photo1_right":  ("fcc-BCGA2187-internal-photo-1.jpg", "y", (100, 900),  (1460, 1620)),
    "photo8_bottom": ("fcc-BCGA2187-internal-photo-8.jpg", "x", (400, 2000), (1040, 1200)),
    "photo8_right":  ("fcc-BCGA2187-internal-photo-8.jpg", "y", (100, 900),  (1460, 1620)),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    print("m_ruler_calib.py -- inputs (1 tick = 1 mm on both steel rules):")
    out = {}
    for k, (fn, axis, along, search) in RULES.items():
        if a.only and a.only not in k:
            continue
        out[k] = measure_rule(os.path.join(IMGDIR, fn), k, axis, along, search)
    ms = {k: v for k, v in out.items() if v.get("verdict") == "MEASURED"}
    print("\n  SUMMARY px/mm:")
    for k, v in ms.items():
        print(f"    {k:16s} {v['px_per_mm']:.4f}")
    for ph in ("photo6", "photo7", "photo1", "photo8"):
        b, r = ms.get(ph + "_bottom"), ms.get(ph + "_right")
        if b and r:
            d = 100 * abs(b["px_per_mm"] - r["px_per_mm"]) / ((b["px_per_mm"] + r["px_per_mm"]) / 2)
            print(f"    {ph}: bottom vs right rule disagree by {d:.2f}%  "
                  f"(this is a perspective measurement, not noise)")
    if a.json:
        def clean(v):
            return {kk: (list(vv) if isinstance(vv, np.ndarray) else vv)
                    for kk, vv in v.items() if kk not in ("pos", "idx")}
        json.dump({k: clean(v) for k, v in out.items()}, open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")


if __name__ == "__main__":
    main()
