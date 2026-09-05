#!/usr/bin/env python3
"""k_backface - measure Apple's BACK face, the one the Replica never drew.

halo Replica lane L9, 2026-09-05.  Leif: "always manage its own tools and create any
tools that might be missing."

WHY THIS EXISTS.  THREE-WAY.md row 24: the Replica has drawn ONE of Apple's TWO
populated faces, and four axes are UNSTARTED for that single reason.  The blocker was
never the photograph - `oflynn-frontside-fullres.jpeg` resolves 33-42 genuine px/mm
(M06), the SHARPEST source in the project.  It was that no ruler-bearing view of this
face existed in c_register's catalogue, so no scale could reach it.  That is fixed
(view `fcc7-back`, 69.557 px/mm, held out at 0.1256 mm).  This tool spends it.

STATUS 2026-09-05: THIS TOOL DOES NOT YET WORK, AND ITS OWN CONTROLS ARE WHAT SAY SO.
`caps` REFUSES all five parts and `selftest` FAILS on S1/S6 - the width estimator returns
0.855 mm for a synthetic part that is 2.200 mm wide, and the same synthetic measures
differently through different window spans. It is committed in this state deliberately,
with evidence/E08, because a failed attempt with its controls named is worth more than a
number that passed because nothing could have stopped it. See E08 for what would fix it.

WHAT IT IS FOR.  The five bulk capacitors.  They are the right first target: they
are the largest discrete parts on either face, they are the row where halo_rev_a sits
at ONE TWELFTH of Apple's bulk with no package to compare against, and their body
carries a legible marking.  Everything else on this face is smaller and can wait.

THE SIGNATURE, and why it is not the dark-package problem.  M08 could not separate
Apple's black IC packages from black soldermask: same luma, same texture, four
attempts, ruled out BY MEASUREMENT.  These parts are the opposite case and it must be
said explicitly rather than assumed: a tantalum brick is a DARK body between TWO BRIGHT
METAL END TERMINATIONS.  Measured here: body mean luma 40.8 sd 15.7, terminations
200-225.  The discriminator is not "it is dark" - it is "two bright parallel bars of
equal width, collinear, separated by a dark elongated gap".  Soldermask has no such
pair, and a gold pad - which reaches the same 209-223 luma - is a single blob with no
partner and no dark body between.

WHAT IS OPERATOR-SEEDED AND WHAT IS MEASURED, kept apart on purpose.
    SEEDED   : which five places to look.  Read off a labelled overlay by eye.
    MEASURED : orientation, both body dimensions, and the centroid, by refinement
               from that seed.
A seed is not a measurement and is never reported as one.  The refinement is what can
fail, and the negative control below is the proof that it can: THE SAME REFINER, SEEDED
ON BARE SOLDERMASK, MUST REFUSE.  If it did not, the five results would be a function
of where the operator pointed - which is M08 attempt 3 exactly, where a stated ROI plus
Otsu returned an answer that swung 3.35 -> 4.50 mm on padding alone.

THREE VERDICTS, AND THEY ARE THE EXIT CODE
    0  PASS              admitted parts, with the input every number came from
    1  FAIL              it ran and a control went red
    2  CANNOT DETERMINE  the photograph does not support the measurement. Never a default.

VERBS
    caps        measure the five bulk capacitors
    selftest    synthetic ground truth + the deliberate breaks, each watched going red
    controls    the negative control on its own, verbose
"""
import sys, os, json, math, argparse
import numpy as np
from PIL import Image

PASS, FAIL, CANNOT = 0, 1, 2
V = {PASS: "PASS", FAIL: "FAIL", CANNOT: "CANNOT DETERMINE"}
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(LANE, "..", ".."))
IMG = os.path.join(REPO, "images", "airtag", "oflynn-frontside-fullres.jpeg")
FIT = os.path.join(LANE, "metrology", "c_register-fit-back.json")

# ---- SEEDS.  Operator-read off a labelled overlay, in full-res source pixels.
# These are WHERE TO LOOK and nothing else.  Every number this tool publishes is
# produced by refine() from these, and refine() refuses a seed that is on nothing.
SEEDS = [
    ("C1", 372, 1240), ("C2", 447, 1455), ("C3", 566, 1706),
    ("C4", 1917, 1237), ("C5", 1760, 1690),
]
# NEGATIVE-CONTROL SEEDS. Named "bare-soldermask seeds" in the first version, and that
# name was WRONG. The 12 lowest-variance windows on this annulus were rendered and looked
# at: every one still holds test pads, silkscreen and an IC marked 4BU LA. THERE IS NO
# BARE SOLDERMASK ON THIS FACE. So these are seeds on ORDINARY POPULATED BOARD, and what
# the control asks is the right question anyway and a harder one: can the refiner tell a
# capacitor from the board's ordinary structure? Measured answer, 2026-09-05: NO.
NULL_SEEDS = [
    ("N1", 700, 1000), ("N2", 1500, 900), ("N3", 800, 1750),
    ("N4", 1450, 1800), ("N5", 620, 1450), ("N6", 1650, 1450),
]

# MIN_CNR is NOT chosen. It is the bare-board floor measured by `calibrate` on this
# very photograph, plus a stated margin. See metrology/backface-cnr-floor.json.
# WHAT THIS GATE IS AND IS NOT, because `calibrate` established the limit rather than a
# number. Run over 60 random windows of this board's own annulus, z against each window's
# OWN row-permutation null came back median 116, p95 971, MAX 1341. That is not a null
# distribution - THERE IS NO BARE SOLDERMASK ON THIS FACE. Every low-variance window
# still holds pads, silkscreen and parts (looked at, 12 of them, not assumed). So a
# threshold cannot be calibrated from this photograph, and a threshold set at 1341 would
# reject every real part.
#
# THEREFORE THE z GATE IS NOT THE LOAD-BEARING CONTROL HERE and is not presented as one.
# Its only job is to exclude FEATURELESS NOISE, which it does: synthetic bare ground at
# the photograph's own measured body noise (sd 15.7) scores z ~3.5. The two controls that
# actually decide admission are structural and both have watched failures:
#     BAND-WIDTH MATCH  - two bars of unequal width are not one part's two terminations
#     WINDOW INVARIANCE - the same size through three window spans, or it is refused
MIN_CNR = 8.0
MIN_CNR_BASIS = ("excludes featureless noise only (synthetic bare ground at the "
                 "photograph's own body noise scores ~3.5). NOT calibrated from this "
                 "photograph - see the note above: the annulus has no null population. "
                 "The load-bearing controls are band-width match and window invariance.")

_f = os.path.join(LANE, "metrology", "backface-cnr-floor.json")

def gray(path=IMG):
    return np.asarray(Image.open(path).convert("L"), dtype=np.float64)

def rot_window(a, cx, cy, theta_deg, half_w, half_h):
    """Sample a rotated rectangle about (cx,cy). +theta rotates the SAMPLING frame."""
    from scipy import ndimage
    th = math.radians(theta_deg); ct, st = math.cos(th), math.sin(th)
    u = np.arange(-half_w, half_w + 1, 1.0)
    v = np.arange(-half_h, half_h + 1, 1.0)
    U, Vv = np.meshgrid(u, v)
    X = cx + U * ct - Vv * st
    Y = cy + U * st + Vv * ct
    return ndimage.map_coordinates(a, [Y, X], order=1, mode="constant", cval=np.nan)

# THE NULL THAT WAS TRIED FIRST AND DISCARDED, kept because the reason is the lesson.
# It reshuffled the profile's INCREMENTS and compared the resulting random walk's range
# against the real profile's range. It COULD NOT DISCRIMINATE: a clean synthetic part
# scored z=2.48 and bare ground z=-3.88, but the real part sat BELOW any threshold that
# would have rejected a single stray bar (z=2.00). A profile with two sharp peaks has
# large increments, so permuting them builds a random walk with a large range - the null
# manufactures the very property under test, which is E07 sec.2's failure exactly.
# It was replaced, NOT re-thresholded. Loosening a gate until the answer appears is the
# defect; the gate was measuring the wrong quantity.

def _robust_sd(x):
    """MAD-based sd. Robust because the peaks themselves are in this array."""
    m = np.median(x)
    return float(1.4826 * np.median(np.abs(x - m)) + 1e-9)

def _run_about(prof, i, half):
    """Contiguous run of samples about i that stay above `half`."""
    lo = hi = i
    while lo - 1 >= 0 and prof[lo - 1] > half: lo -= 1
    while hi + 1 < len(prof) and prof[hi + 1] > half: hi += 1
    return lo, hi

def band_score(prof, i1, i2, body):
    """Score the WEAKER of the two bands by INTEGRATED CONTRAST OVER ITS CONTIGUOUS RUN.

    Contiguity is the load-bearing part and it is chosen for the null, not for the
    signal. A termination is ~0.45 mm of CONSECUTIVE bright rows; the null below
    permutes the rows, which leaves every brightness value and the whole marginal
    distribution untouched and destroys only the ordering. A statistic built on the
    PEAK VALUE would be completely blind to that permutation - the two brightest rows
    survive it unchanged - so a peak-height statistic has a null that cannot fire.
    Integrated run contrast collapses under it. That is the difference between a
    control and a decoration.

    The MINIMUM of the two bands is used: one real termination and one noise excursion
    - a lone gold pad - must not pass on the strength of the real one.
    """
    out = []
    for i in (i1, i2):
        half = body + 0.5 * (prof[i] - body)
        lo, hi = _run_about(prof, i, half)
        seg = prof[lo:hi + 1] - body
        out.append(float(seg.sum()))
    return min(out), out

def band_null(prof, minsep, body_fn, rng, n=200):
    """The null: permute the ROWS. Identical brightness marginal, identical peak
    values, ordering destroyed. E07 sec.2 - permute the thing the statistic uses,
    not something adjacent to it.
    """
    vals = []
    for _ in range(n):
        q = rng.permutation(prof)
        idx = np.argsort(q)[::-1]
        p1 = int(idx[0]); p2 = None
        for j in idx[1:]:
            if abs(int(j) - p1) >= minsep:
                p2 = int(j); break
        if p2 is None:
            continue
        a_i, b_i = sorted((p1, p2))
        b = body_fn(q, a_i, b_i)
        v, _ = band_score(q, a_i, b_i, b)
        vals.append(v)
    if not vals:
        return None, None
    v = np.array(vals)
    return float(v.mean()), float(v.std() + 1e-9)

def refine(a, cx, cy, ppm, *, span_mm=2.6, min_z=None, min_sep_mm=1.2,
           max_width_mismatch=0.28, rng=None):
    """Locate a two-bright-band part about a seed. Returns a dict, or None with a why.

    The admission test is on the BANDS, not on the body: two bright bars, each standing
    clear of the profile's own null, of similar width, separated by a dark gap.
    """
    rng = rng or np.random.default_rng(11)
    if min_z is None:
        min_z = MIN_CNR
    hw = int(round(span_mm * ppm)); hh = hw
    best = None
    for theta in np.arange(0, 180, 1.0):
        w = rot_window(a, cx, cy, theta, hw, hh)
        if not np.isfinite(w).all():
            continue
        # long axis = v (rows). Profile of row means: two bright rows = the two bands.
        prof = np.nanmean(w, axis=1)
        # the two bands are the two tallest peaks with a gap between them
        lo, hi = prof.min(), prof.max()
        if hi - lo < 1e-6:
            continue
        # score: contrast of the top two separated maxima against the profile median
        med = np.median(prof)
        idx = np.argsort(prof)[::-1]
        p1 = idx[0]
        p2 = None
        minsep = int(round(min_sep_mm * ppm))
        for j in idx[1:]:
            if abs(int(j) - int(p1)) >= minsep:
                p2 = int(j); break
        if p2 is None:
            continue
        score = (prof[p1] - med) + (prof[p2] - med)
        if best is None or score > best[0]:
            best = (score, theta, w, prof, int(p1), p2, med)
    if best is None:
        return None, "no orientation gave two separated bright bands inside the window"
    score, theta, w, prof, p1, p2, med = best
    a_i, b_i = sorted((p1, p2))
    _bodyfn = lambda q, x, y: (float(np.median(q[x + 2:y - 1])) if y - x > 6 else float(np.median(q)))
    body = _bodyfn(prof, a_i, b_i)
    raw, both = band_score(prof, a_i, b_i, body)
    minsep = int(round(min_sep_mm * ppm))
    mu, sd = band_null(prof, minsep, _bodyfn, rng)
    if mu is None:
        return None, "the row-permutation null produced no comparable statistic"
    z = (raw - mu) / sd
    if z < min_z:
        return None, (f"the weaker termination does not stand clear of THIS WINDOW'S OWN "
                      f"row-permutation null: z={z:.2f} < {min_z} "
                      f"(integrated contrast {raw:.0f}, null {mu:.0f}+-{sd:.0f})")

    # OUTER edges of the two bands at half maximum above the local body level.
    def outer(i, direction):
        half = body + 0.5 * (prof[i] - body)
        j = i
        while 0 <= j + direction < len(prof) and prof[j + direction] > half:
            j += direction
        # linear interpolation onto the half-max crossing
        k = j + direction
        if 0 <= k < len(prof) and prof[j] != prof[k]:
            t = (prof[j] - half) / (prof[j] - prof[k])
            return j + t * direction
        return float(j)
    top = outer(a_i, -1); bot = outer(b_i, +1)
    length_px = bot - top

    # WIDTH from the bands themselves: the columns where each band exceeds half max.
    def band_width(i):
        row = np.nanmean(w[max(0, i - 1):i + 2, :], axis=0)
        base = np.median(row)
        half = base + 0.5 * (row.max() - base)
        on = np.where(row > half)[0]
        if on.size < 3:
            return None
        return float(on[-1] - on[0] + 1)
    w1, w2 = band_width(a_i), band_width(b_i)
    if w1 is None or w2 is None:
        return None, "a band has no resolvable width at half maximum"
    mism = abs(w1 - w2) / max(w1, w2)
    if mism > max_width_mismatch:
        return None, (f"the two bright bars are not the same width ({w1:.0f} vs {w2:.0f} px, "
                      f"{100*mism:.0f}% apart) - not one part's two terminations")
    width_px = 0.5 * (w1 + w2)

    # centroid: midpoint of the two band outer edges, back in full-frame coords
    mid_v = 0.5 * (top + bot) - hh
    th = math.radians(theta)
    ox = cx + (-mid_v) * (-math.sin(th))
    oy = cy + (-mid_v) * (math.cos(th))
    ox = cx - mid_v * (-math.sin(th)) * -1
    # explicit: window point (u=0, v=mid_v) maps to (cx - mid_v*sin, cy + mid_v*cos)
    ox = cx - mid_v * math.sin(th)
    oy = cy + mid_v * math.cos(th)

    return dict(theta_deg=float(theta % 180), z=float(z),
                length_px=float(length_px), width_px=float(width_px),
                band_width_px=[float(w1), float(w2)], band_width_mismatch=float(mism),
                length_mm=float(length_px / ppm), width_mm=float(width_px / ppm),
                cx_px=float(ox), cy_px=float(oy),
                body_luma=float(body), band_luma=float(0.5 * (prof[a_i] + prof[b_i])),
                integrated_contrast=float(raw), null_mean=float(mu), null_sd=float(sd)), None

# ------------------------------------------------------------- EIA case codes
# An EXTERNAL ruler this project did not fit anything to. If a measured body lands
# cleanly on ONE of these and not ambiguously between two, that corroborates the
# transferred scale by a route that does NOT pass through the FCC rulers or through
# the 920-/820- board-identity assumption.
EIA = {  # code: (length mm, width mm)  - tantalum chip case codes, body nominal
    "EIA 1608 / R": (1.6, 0.85), "EIA 2012 / P": (2.0, 1.25),
    "EIA 3216 / A": (3.2, 1.6), "EIA 3528 / B": (3.5, 2.8),
    "EIA 6032 / C": (6.0, 3.2), "EIA 7343 / D": (7.3, 4.3),
    "EIA 0805 (MLCC)": (2.0, 1.25), "EIA 1206 (MLCC)": (3.2, 1.6),
    "EIA 1210 (MLCC)": (3.2, 2.5),
}

def nearest_codes(L, W):
    out = []
    for k, (l, w) in EIA.items():
        e = math.hypot((L - l) / l, (W - w) / w)
        out.append((e * 100, k, l, w))
    out.sort()
    return out

# ------------------------------------------------------------------ verbs
def cmd_caps(args):
    if not os.path.exists(IMG):
        print(f"CANNOT DETERMINE: no such image {IMG}"); return CANNOT
    fit = json.load(open(FIT))
    ppm = fit["transferred_scale"]["source_px_per_mm_mean"]
    ppm_sd = fit["transferred_scale"]["source_px_per_mm_sd"]
    a = gray()
    print("k_backface caps")
    print(f"  INPUT   {os.path.relpath(IMG, REPO)}  {a.shape[1]}x{a.shape[0]}")
    print(f"  SCALE   {ppm:.4f} px/mm  (sd {ppm_sd:.4f} = {100*ppm_sd/ppm:.2f}% over the board)")
    print(f"  BASIS   {os.path.relpath(FIT, REPO)} - c_register oflynn-back -> fcc7-back,")
    print(f"          NCC {fit['ncc']:.4f} vs null max {max(fit['null_control']['ncc']):.4f}; "
          f"held out at 0.1256 mm (c_register-validate-back.json)")
    print(f"  GENUINE {ppm:.1f} raw px/mm; M06 measures 33-42 GENUINE px/mm on this face.")
    print(f"          Sizes below are quoted in both, and the genuine figure is the honest one.")
    print()
    rng = np.random.default_rng(11)
    rows, refused, candidates = [], [], []
    SPANS = (1.6, 2.0, 2.4)
    print("  ADMISSION: a part is admitted only if the SAME size comes back through all")
    print(f"  three window spans {SPANS} mm. M08 attempt 3 returned an answer that was")
    print("  purely a function of the operator's chosen box - 3.35 -> 4.50 mm on padding")
    print("  alone - and nothing in its output looked wrong. This is the gate for that.")
    print()
    for name, sx, sy in SEEDS:
        got = []
        for sp in SPANS:
            r, why = refine(a, sx, sy, ppm, span_mm=sp, rng=rng)
            got.append((sp, r, why))
        ok = [g for g in got if g[1] is not None]
        if len(ok) < len(SPANS):
            miss = "; ".join(f"span {sp}: {w}" for sp, r, w in got if r is None)
            refused.append((name, f"refused at {len(SPANS)-len(ok)} of {len(SPANS)} spans - {miss}"))
            if ok:
                candidates.append(dict(ref=name, seed_px=[sx, sy],
                                       per_span=[dict(span_mm=sp, length_mm=r["length_mm"],
                                                      width_mm=r["width_mm"], theta_deg=r["theta_deg"],
                                                      z=r["z"]) for sp, r, w in ok],
                                       admitted=False))
            continue
        L = [g[1]["length_mm"] for g in ok]; W = [g[1]["width_mm"] for g in ok]
        spreadL = max(L) - min(L); spreadW = max(W) - min(W)
        if spreadL > 0.15 or spreadW > 0.15:
            refused.append((name, f"THE ANSWER IS A FUNCTION OF THE WINDOW: length "
                                  f"{min(L):.3f}-{max(L):.3f} mm (spread {spreadL:.3f}), width "
                                  f"{min(W):.3f}-{max(W):.3f} mm (spread {spreadW:.3f}) over spans "
                                  f"{SPANS} mm. Tolerance 0.150 mm."))
            candidates.append(dict(ref=name, seed_px=[sx, sy],
                                   per_span=[dict(span_mm=sp, length_mm=r["length_mm"],
                                                  width_mm=r["width_mm"], theta_deg=r["theta_deg"],
                                                  z=r["z"]) for sp, r, w in ok],
                                   admitted=False,
                                   why_not="window-invariance control fired"))
            continue
        r = ok[len(ok)//2][1]
        r["span_spread_mm"] = [float(spreadL), float(spreadW)]
        r["ref"] = name; r["seed_px"] = [sx, sy]
        r["length_genuine_px"] = r["length_mm"] * 37.5   # M06 midpoint for this face
        r["width_genuine_px"] = r["width_mm"] * 37.5
        rows.append(r)
        print(f"  {name}  {r['length_mm']:.3f} x {r['width_mm']:.3f} mm   "
              f"theta {r['theta_deg']:5.1f} deg   z {r['z']:5.1f}   "
              f"bands {r['band_width_px'][0]:.0f}/{r['band_width_px'][1]:.0f} px "
              f"({100*r['band_width_mismatch']:.0f}% apart)")
    for name, why in refused:
        print(f"  {name}  REFUSED: {why}")
    if candidates:
        print()
        print("  CANDIDATES - RECORDED, NOT PUBLISHED. Each produced a number at one or more")
        print("  spans and failed the window-invariance gate. They are written to the JSON so")
        print("  the next lane has the lead AND the reason it was refused; they are NOT")
        print("  measurements and must never be quoted as sizes.")
        for c in candidates:
            for ps in c["per_span"]:
                print(f"      {c['ref']} span {ps['span_mm']}: {ps['length_mm']:.3f} x "
                      f"{ps['width_mm']:.3f} mm  theta {ps['theta_deg']:.0f}  z {ps['z']:.0f}")
    print()

    # ---- NEGATIVE CONTROL: the same refiner on bare soldermask must refuse.
    nfound = []
    for name, sx, sy in NULL_SEEDS:
        r, why = refine(a, sx, sy, ppm, rng=rng)
        if r is not None:
            nfound.append((name, r))
    print(f"  NEGATIVE CONTROL  {len(NULL_SEEDS)} seeds on ORDINARY POPULATED BOARD (there is no")
    print(f"  bare soldermask on this face - established by looking, not assumed), same refiner:")
    if nfound:
        for name, r in nfound:
            print(f"      {name} ADMITTED {r['length_mm']:.3f} x {r['width_mm']:.3f} mm z={r['z']:.1f}"
                  f"  <-- CONTROL FIRED: the refiner cannot tell a part from ordinary board here.")
    else:
        print(f"      0 of {len(NULL_SEEDS)} admitted. The refiner can refuse, and does.")

    verdict = PASS
    if len(rows) < 2:
        verdict = CANNOT
    if nfound:
        verdict = FAIL

    summary = {}
    if rows:
        L = np.array([r["length_mm"] for r in rows]); W = np.array([r["width_mm"] for r in rows])
        print()
        print(f"  ACROSS THE {len(rows)} ADMITTED PARTS")
        print(f"      length {L.mean():.3f} mm  sd {L.std(ddof=1) if len(L)>1 else 0:.3f}  "
              f"({100*L.std(ddof=1)/L.mean() if len(L)>1 else 0:.1f}%)   range {L.min():.3f}-{L.max():.3f}")
        print(f"      width  {W.mean():.3f} mm  sd {W.std(ddof=1) if len(W)>1 else 0:.3f}  "
              f"({100*W.std(ddof=1)/W.mean() if len(W)>1 else 0:.1f}%)   range {W.min():.3f}-{W.max():.3f}")
        print(f"      NOTE: five parts agreeing with EACH OTHER is a CONSISTENCY check and")
        print(f"      NOT an accuracy check. They are the same part number; they would agree")
        print(f"      just as well if the scale were 10% wrong.")
        cand = nearest_codes(L.mean(), W.mean())
        print()
        print(f"  AGAINST THE STANDARD CASE CODES - an external ruler nothing here was fitted to:")
        for e, k, l, w in cand[:3]:
            print(f"      {k:18s} {l:.2f} x {w:.2f} mm   {e:.1f}% away")
        gap = cand[1][0] - cand[0][0]
        if cand[0][0] < 8.0 and gap > 5.0:
            print(f"      -> lands on {cand[0][1]} and the runner-up is {gap:.1f}% further out.")
            print(f"         THIS CORROBORATES THE SCALE BY A ROUTE THAT DOES NOT PASS THROUGH")
            print(f"         THE FCC RULERS OR THE 920-/820- BOARD-IDENTITY ASSUMPTION.")
        else:
            print(f"      -> AMBIGUOUS between {cand[0][1]} and {cand[1][1]} "
                  f"({cand[0][0]:.1f}% vs {cand[1][0]:.1f}%). NOT quoted as a scale check:")
            print(f"         a body that sits between two codes corroborates neither.")
        summary = dict(n=len(rows), length_mm_mean=float(L.mean()), width_mm_mean=float(W.mean()),
                       length_mm_sd=float(L.std(ddof=1)) if len(L) > 1 else None,
                       width_mm_sd=float(W.std(ddof=1)) if len(W) > 1 else None,
                       nearest_codes=[dict(code=k, l=l, w=w, pct=e) for e, k, l, w in cand[:3]])

    out = dict(tool="k_backface.py", verb="caps", lane="L9",
               image=os.path.relpath(IMG, REPO), px_per_mm=ppm, px_per_mm_sd=ppm_sd,
               scale_basis=os.path.relpath(FIT, REPO),
               genuine_px_per_mm_M06="33-42 on this face; sizes are also quoted in genuine px",
               seeded_not_measured="SEEDS are operator-read positions. Orientation, both "
                                   "dimensions and the centroid are MEASURED by refine().",
               parts=rows, refused=[dict(ref=n, why=w) for n, w in refused],
               negative_control=dict(seeds=len(NULL_SEEDS), admitted=len(nfound),
                                     admitted_refs=[n for n, _ in nfound]),
               candidates_not_published=candidates,
               summary=summary, verdict=V[verdict])
    p = os.path.join(LANE, "metrology", "backface-caps.json")
    json.dump(out, open(p, "w"), indent=2)
    print(f"\n  wrote {os.path.relpath(p, REPO)}")
    print(f"  VERDICT: {V[verdict]}")
    return verdict

def cmd_calibrate(args):
    """Measure what z THIS PHOTOGRAPH's own board throws, and set the floor from it.

    The threshold is derived from the control, never from the answer. E07 sec.4: a
    control that is cleaner than its subject cannot fail, so every sample here is a
    real patch of this board's own annulus at this board's own noise.
    """
    a = gray(); fit = json.load(open(FIT))
    ppm = fit["transferred_scale"]["source_px_per_mm_mean"]
    rng = np.random.default_rng(4)
    cx0, cy0 = 1174.0, 1172.0
    got = []
    tried = 0
    while len(got) < args.n and tried < args.n * 40:
        tried += 1
        r = rng.uniform(0.42, 0.86) * 900.0
        th = rng.uniform(0, 2 * math.pi)
        sx, sy = cx0 + r * math.cos(th), cy0 + r * math.sin(th)
        v = _raw_cnr(a, sx, sy, ppm)
        if v is not None:
            got.append((v, float(sx), float(sy)))
    if len(got) < 20:
        print(f"CANNOT DETERMINE: only {len(got)} usable control windows"); return CANNOT
    vals = np.array([g[0] for g in got])
    floor = float(vals.max())
    chosen = round(floor + args.margin, 2)
    print(f"k_backface calibrate - the bare-board CNR floor, measured not chosen")
    print(f"  INPUT   {os.path.relpath(IMG, REPO)}, {len(got)} random annulus windows "
          f"(r 0.42-0.86 of the board), same refiner geometry")
    print(f"  z against each window's OWN row-permutation null, over real board windows: median {np.median(vals):.2f}  p95 {np.percentile(vals,95):.2f}  "
          f"MAX {floor:.2f}")
    print()
    print(f"  THIS IS NOT A NULL DISTRIBUTION AND NO THRESHOLD IS SET FROM IT.")
    print(f"  There is no bare soldermask on this face. The 12 lowest-variance windows on the")
    print(f"  annulus were rendered and LOOKED AT: every one still holds test pads, silkscreen")
    print(f"  ('2920 17', '-A') and an IC marked 4BU LA. So these {len(got)} samples are a")
    print(f"  population of REAL STRUCTURE, not of nothing, and a floor of {chosen:.0f} taken")
    print(f"  from them would reject every real part.")
    print(f"  CONSEQUENCE, recorded rather than worked around: the z gate cannot be calibrated")
    print(f"  from this photograph. It stays at {MIN_CNR}, where its only job is to exclude")
    print(f"  featureless noise. Admission is decided by BAND-WIDTH MATCH and WINDOW")
    print(f"  INVARIANCE, which are structural and can both be watched failing.")
    out = dict(tool="k_backface.py", verb="calibrate",
               image=os.path.relpath(IMG, REPO), n=len(got), tried=tried,
               cnr_median=float(np.median(vals)), cnr_p95=float(np.percentile(vals, 95)),
               cnr_max=floor, margin=args.margin, min_cnr=chosen,
               verdict="CANNOT DETERMINE - no null population exists on this face",
               basis=(f"z over {len(got)} random annulus windows of {os.path.basename(IMG)}: "
                      f"median {np.median(vals):.1f}, p95 {np.percentile(vals,95):.1f}, max "
                      f"{floor:.1f}. NOT A NULL: there is no bare soldermask on this face - "
                      f"the 12 lowest-variance windows were rendered and looked at and every "
                      f"one still holds pads, silkscreen and an IC. No threshold is set from "
                      f"this. The z gate stays at its noise-exclusion value and the "
                      f"load-bearing controls are band-width match and window invariance."))
    json.dump(out, open(_f, "w"), indent=2)
    print(f"  wrote {os.path.relpath(_f, REPO)}")
    return PASS

def _raw_cnr(a, cx, cy, ppm, span_mm=2.6):
    """The CNR refine() would compute, with NO admission test. For calibration only."""
    hw = int(round(span_mm * ppm))
    best = None
    for theta in np.arange(0, 180, 6.0):
        w = rot_window(a, cx, cy, theta, hw, hw)
        if not np.isfinite(w).all():
            return None
        prof = np.nanmean(w, axis=1)
        med = np.median(prof)
        idx = np.argsort(prof)[::-1]
        p1 = int(idx[0]); p2 = None
        minsep = int(round(1.2 * ppm))
        for j in idx[1:]:
            if abs(int(j) - p1) >= minsep:
                p2 = int(j); break
        if p2 is None:
            continue
        a_i, b_i = sorted((p1, p2))
        _bf = lambda q, x, y: (float(np.median(q[x + 2:y - 1])) if y - x > 6 else float(np.median(q)))
        body = _bf(prof, a_i, b_i)
        raw, _ = band_score(prof, a_i, b_i, body)
        mu, sd = band_null(prof, minsep, _bf, np.random.default_rng(2), n=60)
        if mu is None:
            continue
        v = (raw - mu) / sd
        if best is None or v > best:
            best = v
    return best

def cmd_controls(args):
    a = gray(); fit = json.load(open(FIT))
    ppm = fit["transferred_scale"]["source_px_per_mm_mean"]
    rng = np.random.default_rng(11)
    print("negative control, verbose - every bare-board seed and why it was refused")
    bad = 0
    for name, sx, sy in NULL_SEEDS:
        r, why = refine(a, sx, sy, ppm, rng=rng)
        if r is None:
            print(f"  {name} ({sx},{sy})  REFUSED: {why}")
        else:
            bad += 1
            print(f"  {name} ({sx},{sy})  ADMITTED {r['length_mm']:.3f}x{r['width_mm']:.3f} mm "
                  f"z={r['z']:.1f}  <-- BAD")
    return FAIL if bad else PASS

# ------------------------------------------------------------------ selftest
def _synth(ppm, L_mm, W_mm, theta, noise, size=400, band_mm=0.45):
    """A synthetic part on a noisy dark ground. Noise is set from the REAL photograph's
    measured body sd (15.7) rather than chosen, because E07 sec.4 is a control that was
    19x cleaner than its subject and therefore could not fail."""
    from scipy import ndimage
    a = np.full((size, size), 45.0)
    L = L_mm * ppm; W = W_mm * ppm; B = band_mm * ppm
    yy, xx = np.mgrid[0:size, 0:size].astype(float)
    cx = cy = size / 2.0
    th = math.radians(theta); ct, st = math.cos(th), math.sin(th)
    u = (xx - cx) * ct + (yy - cy) * st
    v = -(xx - cx) * st + (yy - cy) * ct
    body = (np.abs(u) <= W / 2) & (np.abs(v) <= L / 2)
    band = body & (np.abs(np.abs(v) - (L / 2 - B / 2)) <= B / 2)
    a[body] = 40.0
    a[band] = 212.0
    a = ndimage.gaussian_filter(a, 1.0)
    a = a + np.random.default_rng(3).normal(0, noise, a.shape)
    return np.clip(a, 0, 255)

def cmd_selftest(args):
    fails = []
    ppm = 69.5568
    def chk(name, cond, note):
        print(f"  [{'ok ' if cond else 'RED'}] {name}  {note}")
        if not cond: fails.append(name)

    # S1 recover a KNOWN size
    a = _synth(ppm, 3.50, 2.20, 37.0, 15.7)
    r, why = refine(a, 200, 200, ppm)
    ok = r is not None and abs(r["length_mm"] - 3.50) < 0.15 and abs(r["width_mm"] - 2.20) < 0.15
    chk("S1", ok, f"synthetic 3.500 x 2.200 mm at 37 deg -> " +
        (f"{r['length_mm']:.3f} x {r['width_mm']:.3f} mm at {r['theta_deg']:.1f} deg" if r else f"REFUSED: {why}"))

    # S2 a DIFFERENT known size - a tool that always answers 3.5x2.2 would pass S1
    a2 = _synth(ppm, 2.00, 1.25, 100.0, 15.7)
    r2, why2 = refine(a2, 200, 200, ppm)
    ok2 = r2 is not None and abs(r2["length_mm"] - 2.00) < 0.15 and abs(r2["width_mm"] - 1.25) < 0.15
    chk("S2", ok2, f"a DIFFERENT synthetic 2.000 x 1.250 mm -> " +
        (f"{r2['length_mm']:.3f} x {r2['width_mm']:.3f} mm" if r2 else f"REFUSED: {why2}"))

    # S3 BARE GROUND at the same noise must be REFUSED
    from scipy import ndimage
    bare = np.clip(ndimage.gaussian_filter(np.full((400, 400), 45.0), 1.0) +
                   np.random.default_rng(5).normal(0, 15.7, (400, 400)), 0, 255)
    r3, why3 = refine(bare, 200, 200, ppm)
    chk("S3", r3 is None, f"bare ground at the SAME noise -> " +
        (f"REFUSED: {why3}" if r3 is None else f"ADMITTED {r3['length_mm']:.2f}x{r3['width_mm']:.2f} - BAD"))

    # S4 ONE bright bar, no partner - a gold pad. Must be REFUSED.
    a4 = np.full((400, 400), 45.0)
    a4[190:210, 150:250] = 212.0
    a4 = np.clip(ndimage.gaussian_filter(a4, 1.0) + np.random.default_rng(7).normal(0, 15.7, a4.shape), 0, 255)
    r4, why4 = refine(a4, 200, 200, ppm)
    chk("S4", r4 is None, f"a SINGLE bright bar (a gold pad has no partner) -> " +
        (f"REFUSED: {why4}" if r4 is None else f"ADMITTED {r4['length_mm']:.2f}x{r4['width_mm']:.2f} - BAD"))

    # S5 TWO bars of UNEQUAL width - two unrelated pads, not one part's terminations
    a5 = np.full((400, 400), 45.0)
    a5[140:158, 150:250] = 212.0
    a5[242:260, 185:215] = 212.0
    a5 = np.clip(ndimage.gaussian_filter(a5, 1.0) + np.random.default_rng(9).normal(0, 15.7, a5.shape), 0, 255)
    r5, why5 = refine(a5, 200, 200, ppm)
    chk("S5", r5 is None, f"two bars 100 px and 30 px wide -> " +
        (f"REFUSED: {why5}" if r5 is None else f"ADMITTED {r5['length_mm']:.2f}x{r5['width_mm']:.2f} - BAD"))

    # S6 THE SHARED-ASSUMPTION CONTROL (E07 final form).
    # S1/S2 pass, and S3/S4/S5 refuse. All six share one assumption with each other:
    # that a millimetre is ppm pixels. If ppm were wrong, S1 and S2 would BOTH fail -
    # so they do test it. But a subtler failure survives all five: refine() could be
    # reading its answer out of the WINDOW SIZE rather than the image, exactly as M08
    # attempt 3 did (a stated ROI plus Otsu, whose answer swung 34% on padding alone).
    # So: the SAME part measured through THREE different window spans must give the
    # SAME size. A window-driven answer cannot.
    spans, got = (2.0, 2.6, 3.4), []
    for sp in spans:
        rr, _ = refine(a, 200, 200, ppm, span_mm=sp)
        got.append(None if rr is None else (rr["length_mm"], rr["width_mm"]))
    ok6 = all(g is not None for g in got) and \
          (max(g[0] for g in got) - min(g[0] for g in got)) < 0.10 and \
          (max(g[1] for g in got) - min(g[1] for g in got)) < 0.10
    chk("S6", ok6, "the same part through window spans 2.0/2.6/3.4 mm -> " +
        (", ".join(f"{g[0]:.3f}x{g[1]:.3f}" if g else "REFUSED" for g in got)) +
        "   (M08 attempt 3 swung 34% on padding alone; a window-driven answer cannot pass this)")

    # S7 and the break that proves S6 can fire: feed a window-size-dependent image.
    # A part LARGER than the smallest window must be clipped by it and the spans must
    # then DISAGREE. If S7 does not go red, S6 is decoration.
    big = _synth(ppm, 6.00, 2.20, 0.0, 15.7, size=700)
    got7 = []
    for sp in (2.0, 3.4):
        rr, _ = refine(big, 350, 350, ppm, span_mm=sp)
        got7.append(None if rr is None else rr["length_mm"])
    disagree = (got7[0] is None) != (got7[1] is None) or \
               (None not in got7 and abs(got7[0] - got7[1]) > 0.10)
    chk("S7", disagree, "a 6.00 mm part clipped by a 2.0 mm window MUST disagree with a "
        "3.4 mm one -> " + ", ".join("REFUSED" if g is None else f"{g:.3f}" for g in got7))

    print()
    if fails:
        print("SELFTEST FAIL: " + ", ".join(fails)); return FAIL
    print("SELFTEST PASS - 7 checks: 2 recoveries of DIFFERENT known sizes, 3 refusals at "
          "matched noise, and the window-invariance pair S6/S7.")
    return PASS

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("caps"); sub.add_parser("selftest"); sub.add_parser("controls")
    c = sub.add_parser("calibrate")
    c.add_argument("--n", type=int, default=120)
    c.add_argument("--margin", type=float, default=1.0)
    a = p.parse_args()
    return {"caps": cmd_caps, "selftest": cmd_selftest, "controls": cmd_controls,
            "calibrate": cmd_calibrate}[a.cmd](a)

if __name__ == "__main__":
    sys.exit(main())
