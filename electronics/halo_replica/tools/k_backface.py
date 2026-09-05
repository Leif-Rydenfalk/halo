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

TPNAMES = os.path.join(REPO, "images", "airtag", "oflynn-frontside-tpnames.jpg")

def _oflynn_labels():
    """O'Flynn's red annotation positions, extracted mechanically.

    THE POINT OF THIS FUNCTION is that these positions were produced by a person who
    had never heard of this detector, on a photograph he published in 2021. They are a
    POSITIVE CONTROL THAT COULD NOT BE MADE EASY, and they can disagree.
    """
    from scipy import ndimage
    from scipy.spatial import cKDTree
    a = np.asarray(Image.open(TPNAMES).convert("RGB")).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r - np.maximum(g, b) > 60) & (r > 120)
    lab, n = ndimage.label(red)
    sizes = ndimage.sum(red, lab, range(1, n + 1))
    keep = [i + 1 for i, sz in enumerate(sizes) if sz >= 25]
    cen = ndimage.center_of_mass(red, lab, keep)
    pts = np.array([(c[1], c[0]) for c in cen])
    # digits of one number are separate blobs; link those within 26 px
    tree = cKDTree(pts); pairs = tree.query_pairs(26)
    par = list(range(len(pts)))
    def find(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for i, j in pairs: par[find(i)] = find(j)
    grp = {}
    for i in range(len(pts)): grp.setdefault(find(i), []).append(i)
    return np.array([pts[v].mean(0) for v in grp.values()]), a.shape

def cmd_pads(args):
    """Locate the round gold pads on Apple's BACK face, in millimetres."""
    from scipy import ndimage
    from scipy.spatial import cKDTree
    fit = json.load(open(FIT))
    ppm = fit["transferred_scale"]["source_px_per_mm_mean"]
    rgb = np.asarray(Image.open(IMG).convert("RGB")).astype(float)
    lum = rgb.mean(2); Rc, Bc = rgb[..., 0], rgb[..., 2]
    gold = (Rc - Bc > 28) & (Rc > 90) & (lum < 250)
    gold = ndimage.binary_opening(gold, np.ones((3, 3)))
    lab, n = ndimage.label(gold)
    objs = ndimage.find_objects(lab)
    print("k_backface pads")
    print(f"  INPUT   {os.path.relpath(IMG, REPO)}")
    print(f"  SCALE   {ppm:.4f} px/mm  [FCC steel rulers -> photo 7 -> c_register]")
    print(f"  GOLD    R-B>28, R>90, luma<250 - tools/measure_coil.py's criterion, unchanged")
    print(f"  SHAPE   aspect<1.35, circularity>0.72, equivalent diameter 0.15-1.60 mm")
    print(f"          Shape is what selects a PAD. The colour criterion alone catches every")
    print(f"          gold feature on the board - that is exactly what defeated the coil")
    print(f"          measurement in the same frame (E08 sec.4b), and it is why nothing here")
    print(f"          rests on colour alone.")
    print()
    pads, rejected = [], 0
    for i, sl in enumerate(objs, 1):
        if sl is None: continue
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        area = int((lab[sl] == i).sum())
        if area < 80: continue
        d_eq = 2 * math.sqrt(area / math.pi)
        aspect = max(h, w) / max(1, min(h, w))
        circ = area / (math.pi * (max(h, w) / 2) ** 2)
        d_mm = d_eq / ppm
        if aspect < 1.35 and circ > 0.72 and 0.15 < d_mm < 1.60:
            cy, cx = ndimage.center_of_mass(lab == i)
            pads.append(dict(cx_px=float(cx), cy_px=float(cy), d_mm=float(d_mm),
                             area_px=area, aspect=float(aspect), circularity=float(circ),
                             d_genuine_px=float(d_mm * 37.5)))
        else:
            rejected += 1
    ds = np.array([p["d_mm"] for p in pads])
    print(f"  FOUND {len(pads)} circular pads ({rejected} gold components rejected on shape)")
    print(f"    diameter  min {ds.min():.3f}  p25 {np.percentile(ds,25):.3f}  "
          f"MEDIAN {np.median(ds):.3f}  p75 {np.percentile(ds,75):.3f}  max {ds.max():.3f} mm")
    iqr = np.percentile(ds, 75) - np.percentile(ds, 25)
    print(f"    interquartile range {iqr:.3f} mm = {100*iqr/np.median(ds):.1f}% of the median")
    print(f"    At M06's 33-42 genuine px/mm the median pad is {np.median(ds)*33:.0f}-"
          f"{np.median(ds)*42:.0f} genuine px across, so this is a resolved feature, not an")
    print(f"    interpolation.")

    # ---- NEGATIVE CONTROL: the same detector on the white shell, off the board.
    H, W = lum.shape
    cx0, cy0 = 1174.0, 1172.0
    rr = np.hypot(*np.mgrid[0:H, 0:W][::-1][::-1])
    ys, xs = np.mgrid[0:H, 0:W]
    rad = np.hypot(ys - cy0, xs - cx0)
    off = [p for p in pads if np.hypot(p["cx_px"] - cx0, p["cy_px"] - cy0) > 1000]
    print()
    print(f"  NEGATIVE CONTROL  the same detector on the white shell, r > 1000 px "
          f"({1000/ppm:.1f} mm), where there is no board:")
    print(f"    {len(off)} pads found. " + ("The detector can come back empty off the board."
          if len(off) == 0 else "THE CONTROL FIRED - it is finding pads where there is no board."))

    # ---- POSITIVE CONTROL: O'Flynn's independent annotation, with a null.
    labels, tpshape = _oflynn_labels()
    k = tpshape[1] / rgb.shape[1]          # tpnames px per full-res px
    P = np.array([[p["cx_px"] * k, p["cy_px"] * k] for p in pads])
    tree = cKDTree(P)
    dlab, _ = tree.query(labels)
    dlab_mm = dlab / (ppm * k)
    rng = np.random.default_rng(17)
    rmin = 0.30 * 1000.0; rmax = 0.92 * 1000.0
    nr = rng.uniform(rmin, rmax, 4000) * (tpshape[1] / 2347.0) / (1000.0 / 2347.0) * 0
    # random points on the SAME annulus the labels occupy, in tpnames pixels
    lc = labels.mean(0)
    lr = np.hypot(labels[:, 0] - lc[0], labels[:, 1] - lc[1])
    rs = rng.uniform(lr.min(), lr.max(), 4000)
    th = rng.uniform(0, 2 * np.pi, 4000)
    R2 = np.stack([lc[0] + rs * np.cos(th), lc[1] + rs * np.sin(th)], 1)
    drnd, _ = tree.query(R2)
    drnd_mm = drnd / (ppm * k)
    print()
    print(f"  POSITIVE CONTROL  {len(labels)} annotation positions from "
          f"oflynn-frontside-tpnames.jpg")
    print(f"    That image is the SAME photograph rescaled - measured NCC 0.9993 against this")
    print(f"    one with the red pixels masked out - so the mapping is exact and the")
    print(f"    annotation is EXTERNAL: Colin O'Flynn placed those numbers in 2021 with no")
    print(f"    knowledge of this detector. It is a positive control that cannot be made easy.")
    print(f"    distance from each label to the nearest detected pad:")
    print(f"      LABELS  median {np.median(dlab_mm):.3f} mm   p75 {np.percentile(dlab_mm,75):.3f}   "
          f"p90 {np.percentile(dlab_mm,90):.3f}")
    print(f"      NULL    median {np.median(drnd_mm):.3f} mm   p75 {np.percentile(drnd_mm,75):.3f}   "
          f"p90 {np.percentile(drnd_mm,90):.3f}   (4000 random points on the same annulus)")
    ratio = float(np.median(drnd_mm) / np.median(dlab_mm))
    print(f"      SEPARATION {ratio:.2f}x")
    print(f"    THE NULL IS THE LOAD-BEARING PART. O'Flynn's labels sit BESIDE their pads, not")
    print(f"    on them, so a small absolute distance proves nothing on its own - and this")
    print(f"    annulus is dense, so ANY point is near SOMETHING. The question is only whether")
    print(f"    his labels are nearer than chance, and by how much.")
    ok_pos = ratio >= 2.0
    print(f"    -> " + ("labels land on detections far better than chance."
                        if ok_pos else "NOT SEPARATED FROM CHANCE. The agreement is an artefact "
                                       "of pad density, not a confirmation."))

    verdict = PASS if (len(off) == 0 and ok_pos) else FAIL
    out = dict(tool="k_backface.py", verb="pads", image=os.path.relpath(IMG, REPO),
               px_per_mm=ppm, scale_basis="FCC steel rulers -> photo 7 -> c_register",
               n_pads=len(pads), rejected_on_shape=rejected,
               diameter_mm=dict(min=float(ds.min()), p25=float(np.percentile(ds, 25)),
                                median=float(np.median(ds)), p75=float(np.percentile(ds, 75)),
                                max=float(ds.max()), iqr=float(iqr)),
               pads=pads,
               negative_control=dict(region="r>1000 px, the white shell", found=len(off),
                                     fired=bool(len(off) > 0)),
               positive_control=dict(source="oflynn-frontside-tpnames.jpg",
                                     same_photograph_ncc=0.9993, n_labels=int(len(labels)),
                                     label_nn_median_mm=float(np.median(dlab_mm)),
                                     null_nn_median_mm=float(np.median(drnd_mm)),
                                     separation=ratio, floor=2.0, passed=bool(ok_pos),
                                     why_the_null="labels sit BESIDE their pads and the annulus "
                                                  "is dense, so absolute distance proves nothing"),
               verdict=V[verdict])
    p2 = os.path.join(LANE, "metrology", "backface-pads.json")
    json.dump(out, open(p2, "w"), indent=2)
    print(f"\n  wrote {os.path.relpath(p2, REPO)}")
    print(f"  VERDICT: {V[verdict]}")
    return verdict

def cmd_contacts(args):
    """The three battery contacts, by NEUTRAL bright metal rather than by gold.

    The gold criterion cannot find these: a stamped contact is grey, not gold, so it is
    selected on being bright AND UNSATURATED. That also means the white shell and the
    overexposed centre dome qualify, and both are handled by name below rather than by a
    size threshold chosen to make the answer come out.
    """
    from scipy import ndimage
    from scipy.spatial import cKDTree
    fit = json.load(open(FIT))
    ppm = fit["transferred_scale"]["source_px_per_mm_mean"]
    rgb = np.asarray(Image.open(IMG).convert("RGB")).astype(float)
    lum = rgb.mean(2); mx = rgb.max(2); mn = rgb.min(2)
    sat = (mx - mn) / np.maximum(mx, 1e-6)
    metal = (lum > 150) & (sat < 0.22)
    H, W = lum.shape; cx0, cy0 = 1174.0, 1172.0
    ys, xs = np.mgrid[0:H, 0:W]
    rad = np.hypot(ys - cy0, xs - cx0)
    R_BOARD_PX = 865.0
    metal &= (rad < 0.90 * R_BOARD_PX)
    metal = ndimage.binary_opening(metal, np.ones((5, 5)))
    lab, n = ndimage.label(metal)
    sizes = ndimage.sum(metal, lab, range(1, n + 1))
    objs = ndimage.find_objects(lab)
    print("k_backface contacts")
    print(f"  INPUT   {os.path.relpath(IMG, REPO)}")
    print(f"  SCALE   {ppm:.4f} px/mm  [FCC steel rulers -> photo 7 -> c_register]")
    print(f"  METAL   luma>150 AND saturation<0.22 - a stamped contact is GREY. The gold")
    print(f"          criterion used for the pads cannot find these and was not reused.")
    print(f"  MASKED  r < 0.90 x {R_BOARD_PX:.0f} px, so the white shell is out of frame by")
    print(f"          construction rather than by a size threshold.")
    print()
    rows = []
    for i, sl in enumerate(objs, 1):
        a_px = sizes[i - 1]
        if a_px < 0.30 * ppm * ppm:
            continue
        h = (sl[0].stop - sl[0].start) / ppm; w = (sl[1].stop - sl[1].start) / ppm
        cy, cx = ndimage.center_of_mass(lab == i)
        rows.append(dict(area_mm2=float(a_px / ppm / ppm), w_mm=float(w), h_mm=float(h),
                         cx_px=float(cx), cy_px=float(cy),
                         r_mm=float(math.hypot(cx - cx0, cy - cy0) / ppm)))
    rows.sort(key=lambda r: -r["area_mm2"])
    dome = rows[0] if rows and rows[0]["area_mm2"] > 40 else None
    if dome:
        print(f"  EXCLUDED BY NAME, not by threshold: a {dome['area_mm2']:.1f} mm2 blob at")
        print(f"    r {dome['r_mm']:.2f} mm - the OVEREXPOSED CENTRE DOME. M01 sec.4 already")
        print(f"    records that the saturated white core is the magnet/dome assembly. It is")
        print(f"    the largest neutral-metal region on this face and it is not a contact.")
        rows = rows[1:]
    print()
    # associate with O'Flynn's VCC1 / GND / VCC2 labels
    labels, tpshape = _oflynn_labels()
    k = tpshape[1] / rgb.shape[1]
    P = np.array([[r["cx_px"] * k, r["cy_px"] * k] for r in rows])
    tree = cKDTree(P)
    # the three labels sit in the upper band of the board; take the label groups there
    up = labels[labels[:, 1] < 0.32 * tpshape[0]]
    # THE ASSOCIATION IS INVERTED, and that is the fix. Driving it from O'Flynn's labels
    # failed twice: a plain nearest-neighbour walked UPHILL to the rim (his names sit ABOVE
    # their features), and associating downward then passed the area-symmetry check AT
    # 10.9% ON A PAIR AT r 10.63 AND r 8.07 mm - two unrelated features whose areas
    # happened to agree. Area is one number and two wrong features can share it.
    #
    # So the PHYSICS finds the pair and O'FLYNN VALIDATES IT, rather than the other way
    # round. Apple's two positive tabs are one part in one symmetric scheme, so they must
    # be at the same radius and mirrored about the board's vertical axis. That is a
    # two-parameter constraint no random pair satisfies. The labels are then a check that
    # can still fail - if the best symmetric pair is not where O'Flynn put VCC1 and VCC2,
    # this refuses.
    best = None
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            A, B = rows[i], rows[j]
            if A["cx_px"] > B["cx_px"]:
                A, B = B, A
            if A["cy_px"] > cy0 or B["cy_px"] > cy0:      # both tabs are above centre
                continue
            dr = abs(A["r_mm"] - B["r_mm"])
            dmir = abs((A["cx_px"] + B["cx_px"]) / 2.0 - cx0) / ppm
            da = 100 * abs(A["area_mm2"] - B["area_mm2"]) / max(A["area_mm2"], B["area_mm2"])
            if A["cx_px"] > cx0 or B["cx_px"] < cx0:      # one each side of the axis
                continue
            cost = (dr / 0.60) ** 2 + (dmir / 1.20) ** 2 + (da / 15.0) ** 2
            if best is None or cost < best[0]:
                best = (cost, A, B, dr, dmir, da)
    if best is None:
        print("  CANNOT DETERMINE: no candidate pair straddles the vertical axis above centre")
        return CANNOT
    _, A, B, dr0, dmir0, da0 = best
    print(f"  SYMMETRIC-PAIR SEARCH over {len(rows)} neutral-metal features, both above the")
    print(f"  board centre and one each side of the vertical axis. Best pair:")
    print(f"    radius difference {dr0:.3f} mm (floor 0.600) - midpoint {dmir0:.3f} mm off axis")
    print(f"    (floor 1.200) - areas {da0:.1f}% apart (floor 15.0)")
    # GND: the feature between them, above both
    mid_x = (A["cx_px"] + B["cx_px"]) / 2.0
    # GND SITS IN THE SAME BATTERY WELL AS THE TWO TABS, so it must be at a comparable
    # RADIUS - not merely between them in x. The first version asked only for "between in
    # x and not far below", and picked a rim feature at r 11.03 mm while the two tabs sat
    # at 7.94 and 7.68. Being between two things in one coordinate is not being with them.
    r_ref = 0.5 * (A["r_mm"] + B["r_mm"])
    between = [r for r in rows
               if min(A["cx_px"], B["cx_px"]) < r["cx_px"] < max(A["cx_px"], B["cx_px"])
               and abs(r["r_mm"] - r_ref) <= 1.50
               and r is not A and r is not B]
    between.sort(key=lambda r: abs(r["cx_px"] - mid_x))
    G = between[0] if between else None
    if G is None:
        print(f"  GND: NO CANDIDATE. Nothing lies between the two tabs in x AND within")
        print(f"  1.50 mm of their radius ({r_ref:.2f} mm). The two positive tabs below are")
        print(f"  published; GND is CANNOT DETERMINE and is published as absent, not guessed.")
    cands = [A] + ([G] if G else []) + [B]
    # POSITIVE CONTROL: are O'Flynn's three names actually nearest to the pair physics found?
    lab_d = []
    for r in cands:
        pt = np.array([r["cx_px"] * k, r["cy_px"] * k])
        dd = np.hypot(up[:, 0] - pt[0], up[:, 1] - pt[1])
        lab_d.append(float(dd.min() / (ppm * k)))
    print()
    print(f"  POSITIVE CONTROL  {len(up)} annotation groups sit in the upper band of")
    print(f"    oflynn-frontside-tpnames.jpg, where VCC1, GND and VCC2 are. Distance from each")
    print(f"    feature the SYMMETRY SEARCH chose to its nearest O'Flynn name:")
    for nm0, dv in zip(("left", "centre", "right"), lab_d):
        print(f"      {nm0:7s} {dv:.3f} mm")
    lab_ok = max(lab_d) < 3.0
    print(f"    -> " + ("all three are within 3.0 mm of a name O'Flynn wrote. The pair physics"
                        "\n       found is the pair he labelled." if lab_ok else
                        "AT LEAST ONE IS NOT NEAR ANY NAME. The symmetric pair is not O'Flynn's."))
    print()
    print(f"  THE THREE FEATURES O'FLYNN LABELS VCC1 / GND / VCC2")
    names = (["VCC1 (left)", "GND (centre)", "VCC2 (right)"] if G is not None
             else ["VCC1 (left)", "VCC2 (right)"])
    out_rows = []
    for nm, r in zip(names, cands[:3]):
        print(f"    {nm:14s} {r['w_mm']:.3f} x {r['h_mm']:.3f} mm   area {r['area_mm2']:.3f} mm2   "
              f"r {r['r_mm']:.2f} mm from board centre")
        rr = dict(r); rr["oflynn_label"] = nm.split()[0]; out_rows.append(rr)
    sym = None
    if len(out_rows) >= 2:
        a1, a3 = out_rows[0]["area_mm2"], out_rows[-1]["area_mm2"]
        sym = 100 * abs(a1 - a3) / max(a1, a3)
        print()
        print(f"  INTERNAL CONSISTENCY  the two VCC features differ in area by {sym:.1f}%.")
        print(f"    Apple's scheme puts TWO positive tabs on the battery-well wall, so they")
        print(f"    should be the same part. THIS IS A CONSISTENCY CHECK AND NOT AN ACCURACY")
        print(f"    ONE - they would agree just as well if the scale were 10% wrong.")
    # AREA SYMMETRY ALONE PASSED FOR THE WRONG REASON. Its first form accepted a pair at
    # r 10.63 and r 8.07 mm whose areas happened to agree to 10.9% - two unrelated rim
    # features, not Apple's two positive tabs. Area is one number and two wrong features
    # can share it. THE PHYSICAL SCHEME CONSTRAINS GEOMETRY TOO: the two positive tabs sit
    # on the battery-well wall, so they must be at the SAME RADIUS and MIRRORED about the
    # board's vertical axis. Two features picked at random are not.
    geo_ok, dr, dmir = False, None, None
    if len(out_rows) >= 2:
        A, B = out_rows[0], out_rows[-1]
        dr = abs(A["r_mm"] - B["r_mm"])
        dmir = abs((A["cx_px"] + B["cx_px"]) / 2.0 - cx0) / ppm
        geo_ok = (dr <= 0.60) and (dmir <= 1.20)
        print()
        print(f"  GEOMETRIC SYMMETRY  the two VCC features must be the same distance from the")
        print(f"    board centre and mirrored about its vertical axis:")
        print(f"      radius difference    {dr:.3f} mm   (floor 0.600)")
        print(f"      midpoint off-axis    {dmir:.3f} mm   (floor 1.200)")
        print(f"    -> " + ("consistent with two tabs of one symmetric scheme."
                            if geo_ok else "NOT A SYMMETRIC PAIR."))
    # The VCC pair and GND are graded SEPARATELY. The pair can be solid while GND is not.
    ok = (len(out_rows) >= 2) and (sym is not None) and (sym <= 15.0) and geo_ok and lab_ok
    if not ok:
        print()
        print(f"  *** THE SYMMETRY GATE HAS FIRED. Apple's two positive tabs are the same")
        print(f"  part in one symmetric scheme, so a pair that disagrees in area, in radius or")
        print(f"  in mirror position means THE ASSOCIATION IS WRONG - not that the contacts")
        print(f"  differ. NOTHING HERE IS PUBLISHED AS A CONTACT DIMENSION.")
        print(f"  RECORDED FOR THE NEXT ATTEMPT: an operator probe of this same frame found a")
        print(f"  pair at (965,661) and (1315,657) - areas 1.625 and 1.680 mm2 (3.4% apart),")
        print(f"  radii 7.94 and 7.68 mm (0.26 mm apart), midpoint 0.98 mm off axis - which")
        print(f"  satisfies all three constraints. It is an EYEBALLED seed, not a measurement,")
        print(f"  and the association that reaches it automatically has not been written.")
    print()
    print(f"  WHAT IS NOT SEPARABLE HERE, stated rather than glossed: whether the measured")
    print(f"  extent is the BOARD PAD or the SPRUNG CONTACT sitting on it. This photograph")
    print(f"  shows the board assembled in the shell, and the two are coincident in plan view.")
    print(f"  FCC internal photo 4 shows the battery cavity with the contacts and no board;")
    print(f"  that is the frame that would separate them.")
    verdict = PASS if ok else CANNOT
    out = dict(tool="k_backface.py", verb="contacts", image=os.path.relpath(IMG, REPO),
               px_per_mm=ppm, criterion="luma>150 and saturation<0.22, r<0.90*865 px",
               excluded_by_name=dome, contacts=out_rows, all_candidates=rows[:12],
               gnd_found=bool(G is not None),
               gnd_note=(None if G is not None else
                         "CANNOT DETERMINE. Nothing lies between the two tabs in x AND within "
                         "1.50 mm of their radius. Published as absent rather than guessed."),
               vcc_area_mismatch_pct=sym, symmetry_gate_pct=15.0, symmetry_gate_passed=bool(ok),
               vcc_radius_diff_mm=dr, vcc_midpoint_off_axis_mm=dmir,
               geometric_symmetry_passed=bool(geo_ok),
               operator_seed_not_measured=dict(
                   note="an eyeballed probe of this frame found a pair satisfying all three "
                        "symmetry constraints; the automatic association does not reach it yet. "
                        "NOT a measurement.",
                   left_px=[965, 661], right_px=[1315, 657],
                   area_mm2=[1.625, 1.680], area_mismatch_pct=3.4,
                   r_mm=[7.94, 7.68], midpoint_off_axis_mm=0.98),
               positive_control=dict(source="oflynn-frontside-tpnames.jpg upper band",
                                     n_labels=int(len(up)),
                                     nearest_label_mm=lab_d, floor_mm=3.0, passed=bool(lab_ok),
                                     direction="the SYMMETRY SEARCH chose the features; O'Flynn's "
                                               "names are the check, not the driver"),
               not_separable="board pad vs sprung contact - coincident in plan view in this "
                             "assembled photograph. FCC internal photo 4 shows the cavity "
                             "with contacts and no board and would separate them.",
               verdict=V[verdict])
    p2 = os.path.join(LANE, "metrology", "backface-contacts.json")
    json.dump(out, open(p2, "w"), indent=2)
    print(f"\n  wrote {os.path.relpath(p2, REPO)}")
    print(f"  VERDICT: {V[verdict]}")
    return verdict

def cmd_coil(args):
    """Re-measure the wound coil in the REGISTERED frame, and compare the two SCALES.

    M01 measured this coil in `oflynn-frontside-26mm-cropped.jpg` at 30.2762 px/mm on a
    datum of "787.18 px = 26 mm APPROXIMATE" - O'Flynn's own tilde, which E04/E05 later
    retracted as a figure. This tool measures the SAME COIL in the full-resolution frame
    at 69.557 px/mm, transferred from the FCC steel rulers through photo 7.

    WHAT THIS CAN AND CANNOT TEST, stated first because it is the whole design.
    The 26 mm crop is a CROP OF THE SAME PHOTOGRAPH. The two measurements therefore
    share every pixel and CANNOT disagree about anything the photograph itself gets
    wrong - they are not two opinions about the coil. What they DO NOT share is the
    SCALE: one comes from a tilde on a teardown page, the other from two steel rulers in
    an FCC exhibit. So this is a comparison of TWO INDEPENDENT SCALE ROUTES on one
    object, and that is the only claim made from it.

    Method reproduced from tools/measure_coil.py (L1), which is a hardcoded one-off with
    no CLI and no frame argument. Generalising it is the P11 fix and it is L1's file, so
    it is routed rather than edited here.
    """
    fit = json.load(open(FIT))
    ppm = fit["transferred_scale"]["source_px_per_mm_mean"]
    rgb = np.asarray(Image.open(IMG).convert("RGB")).astype(float)
    lum = rgb.mean(2)
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    # L1's copper criterion, unchanged so the two runs differ only in frame and scale
    copper = (R - B > 28) & (R > 90) & (lum < 250)
    H, W = lum.shape
    cx0, cy0 = 1174.0, 1172.0
    ys, xs = np.mgrid[0:H, 0:W]

    # centre the coil on ITSELF: copper pixels inside a generous central disc
    near = np.hypot(ys - cy0, xs - cx0) < 7.0 * ppm
    m = copper & near
    if m.sum() < 500:
        print("CANNOT DETERMINE: too few copper pixels near the centre"); return CANNOT
    cx = float(xs[m].mean()); cy = float(ys[m].mean())
    for _ in range(4):
        rad = np.hypot(ys - cy, xs - cx)
        mm = copper & (rad < 7.0 * ppm)
        cx = float(xs[mm].mean()); cy = float(ys[mm].mean())
    rad = np.hypot(ys - cy, xs - cx)

    print("k_backface coil")
    print(f"  INPUT   {os.path.relpath(IMG, REPO)}")
    print(f"  SCALE   {ppm:.4f} px/mm  [FCC steel rulers -> photo 7 -> registration]")
    print(f"  CENTRE  ({cx:.1f}, {cy:.1f}) px, from the copper's own centroid, 4 iterations")
    print(f"  CRITERION  R-B>28, R>90, luma<250 - tools/measure_coil.py's, unchanged")
    print()
    step = 2.0
    rows = []
    for r0 in np.arange(1.0 * ppm, 7.0 * ppm, step):
        sel = (rad >= r0) & (rad < r0 + step)
        n = int(sel.sum())
        frac = float(copper[sel].mean()) if n else 0.0
        rows.append((r0 + step / 2, frac, n))
    fr = np.array([r[1] for r in rows]); rr = np.array([r[0] for r in rows])
    band = fr > 0.25
    print("  radial copper fraction (2 px bins):")
    for r0, f, n in rows:
        if f > 0.02:
            print(f"    r={r0:6.1f} px  {r0/ppm:6.3f} mm  frac={f:5.3f} " + "#" * int(f * 50))
    if band.sum() < 2:
        print("  CANNOT DETERMINE: no radial band exceeds the 0.25 copper fraction")
        return CANNOT
    r_in = float(rr[band].min() - step / 2); r_out = float(rr[band].max() + step / 2)
    ID = 2 * r_in / ppm; OD = 2 * r_out / ppm
    print()
    print(f"  BAND FOUND (copper fraction > 0.25, L1's threshold) - see the control below")
    print(f"    inner r {r_in:7.2f} px = {r_in/ppm:6.3f} mm   ->  ID {ID:6.3f} mm")
    print(f"    outer r {r_out:7.2f} px = {r_out/ppm:6.3f} mm   ->  OD {OD:6.3f} mm")
    print(f"    radial width          {(r_out-r_in)/ppm:6.3f} mm")

    # NEGATIVE CONTROL: the same band-finder on an annulus that holds no coil.
    ctrl = []
    for r0 in np.arange(9.0 * ppm, 11.0 * ppm, step):
        sel = (rad >= r0) & (rad < r0 + step)
        ctrl.append(float(copper[sel].mean()) if sel.sum() else 0.0)
    cmax = max(ctrl) if ctrl else 0.0
    bmax = float(fr.max())
    sep = bmax / cmax if cmax > 0 else float("inf")
    print()
    print(f"  NEGATIVE CONTROL  same finder at r 9-11 mm, where there is no coil:")
    print(f"    peak copper fraction in the coil band  {bmax:.3f}")
    print(f"    peak copper fraction in the control    {cmax:.3f}")
    print(f"    SEPARATION {sep:.2f}x  (floor 2.00x)")
    print(f"    A control that merely sits under the threshold has not separated anything.")
    print(f"    L1's 0.25 threshold was set in a TIGHT 26 mm CROP at 12 genuine px/mm, where")
    print(f"    the frame holds little but the coil. In the full frame the WHOLE BOARD's gold")
    print(f"    pads and traces are in view and the same criterion fires on all of them.")
    ok_sep = sep >= 2.0

    M01 = dict(ID=9.380, OD=10.834, width=0.727, ppm=30.2762,
               datum='787.18 px = 26 mm APPROXIMATE (O\'Flynn\'s tilde; retracted as a figure by E04/E05)')
    dID = 100 * (ID - M01["ID"]) / M01["ID"]; dOD = 100 * (OD - M01["OD"]) / M01["OD"]
    print()
    print(f"  AGAINST M01, WHICH IS THE SAME PHOTOGRAPH AT A DIFFERENT SCALE")
    print(f"    M01  ID {M01['ID']:.3f}  OD {M01['OD']:.3f} mm   at {M01['ppm']:.4f} px/mm")
    print(f"    here ID {ID:.3f}  OD {OD:.3f} mm   at {ppm:.4f} px/mm")
    print(f"    difference  ID {dID:+.2f}%   OD {dOD:+.2f}%")
    print()
    if ok_sep:
        print(f"    The two measurements share every pixel and cannot disagree about the coil.")
        print(f"    What they do not share is the SCALE - a teardown page's tilde against two")
        print(f"    FCC steel rulers - so this difference measures THE TWO SCALE ROUTES.")
    else:
        print(f"    *** THIS DIFFERENCE IS NOT A SCALE COMPARISON AND MUST NOT BE READ AS ONE.")
        print(f"    The band measured here is {(r_out-r_in)/ppm:.3f} mm wide against M01's 0.727 mm")
        print(f"    - it is not the winding, it is every gold feature the criterion caught")
        print(f"    across the board. The scales cannot be compared until the coil is isolated.")
        print(f"    WHAT WOULD DO IT: the winding's turns are individually resolvable at this")
        print(f"    scale (M01 saw them at a third of it), so a periodicity test along the")
        print(f"    radius - the turn pitch is ~0.145 mm, AWG 35 - separates a WOUND coil from")
        print(f"    a field of pads in a way a colour threshold never can. ***")
    out = dict(tool="k_backface.py", verb="coil", image=os.path.relpath(IMG, REPO),
               px_per_mm=ppm, scale_basis="FCC steel rulers -> photo 7 -> c_register",
               centre_px=[cx, cy], ID_mm=ID, OD_mm=OD, width_mm=(r_out - r_in) / ppm,
               inner_r_px=r_in, outer_r_px=r_out,
               negative_control=dict(region="r 9-11 mm", max_copper_fraction=cmax,
                                     threshold=0.25, fired=bool(cmax > 0.25)),
               vs_M01=dict(M01_ID_mm=M01["ID"], M01_OD_mm=M01["OD"], M01_px_per_mm=M01["ppm"],
                           M01_datum=M01["datum"], delta_ID_pct=dID, delta_OD_pct=dOD,
                           what_this_compares="TWO SCALE ROUTES on one object. The 26 mm crop "
                                              "is a crop of this same photograph, so the two "
                                              "measurements share every pixel and cannot "
                                              "disagree about the coil itself."),
               band_peak_fraction=bmax, control_peak_fraction=cmax, separation=sep,
               verdict=("MEASURED" if ok_sep else
                        "CANNOT DETERMINE - the copper criterion does not separate the coil "
                        "from the board's other gold in the full frame; band %.3f mm wide "
                        "against M01's 0.727 mm, control separation %.2fx below the 2.00x "
                        "floor" % ((r_out - r_in) / ppm, sep)),
               do_not_quote=("ID_mm and OD_mm are NOT the coil's. They are the extent of "
                             "everything the colour criterion caught. Recorded so the next "
                             "attempt can see what this one did." if not ok_sep else None))
    p2 = os.path.join(LANE, "metrology", "backface-coil.json")
    json.dump(out, open(p2, "w"), indent=2)
    print(f"\n  wrote {os.path.relpath(p2, REPO)}")
    return PASS if ok_sep else CANNOT

def cmd_handoff(args):
    """Emit HANDOFF-positions-back.json in the SAME per-row shape as L1's front handoff.

    L12 consumes both files with one reader. Nothing here is new measurement - it is the
    pads and contacts already measured, in the schema the board lane already uses, with
    every refusal carried across as a named field rather than an absence.
    """
    import subprocess, datetime
    fit = json.load(open(FIT))
    ppm = fit["transferred_scale"]["source_px_per_mm_mean"]
    pads = json.load(open(os.path.join(LANE, "metrology", "backface-pads.json")))
    cont = json.load(open(os.path.join(LANE, "metrology", "backface-contacts.json")))
    caps = json.load(open(os.path.join(LANE, "metrology", "backface-caps.json")))
    coil = json.load(open(os.path.join(LANE, "metrology", "backface-coil.json")))

    # board centre in SOURCE px: photo 7's fitted centre mapped through the registration
    H = np.array(fit["H_target_to_source_cropframe"])
    ox, oy = fit["target"].get("crop_origin", [725, 545])
    tx, ty = 935.25 - ox, 755.395 - oy
    den = H[2, 0] * tx + H[2, 1] * ty + H[2, 2]
    cx = float((H[0, 0] * tx + H[0, 1] * ty + H[0, 2]) / den)
    cy = float((H[1, 0] * tx + H[1, 1] * ty + H[1, 2]) / den)
    # THE HOMOGRAPHY WORKS IN THE PRE-AVERAGED SOURCE FRAME, NOT FULL RESOLUTION.
    # c_register downsamples the source to roughly the target's sampling so that warping
    # is not aliasing a 5x finer image, and H therefore lands in that reduced frame. The
    # first version omitted this and put the board centre at (224, 235) instead of near
    # (1174, 1172) - visibly absurd, which is the only reason it was caught. A smaller
    # frame error would not have looked wrong and would have shifted EVERY position here.
    kpre = float(fit["source"].get("pre_average", 1.0))
    cx *= kpre; cy *= kpre
    GEN = (33.0, 42.0)   # M06's genuine px/mm band for THIS face

    def mk(idx, r, method, found, long_mm, short_mm, conf, flags, dnd=False, why=None):
        x = (r["cx_px"] - cx) / ppm; y = (r["cy_px"] - cy) / ppm
        row = dict(id=idx, method=method, found=found,
                   x_mm=round(x, 3), y_mm=round(y, 3),
                   r_mm=round(math.hypot(x, y), 3),
                   theta_deg=round(math.degrees(math.atan2(y, x)) % 360.0, 2),
                   long_mm=(round(long_mm, 3) if long_mm is not None else None),
                   short_mm=(round(short_mm, 3) if short_mm is not None else None),
                   short_genuine_px=([round(short_mm * GEN[0], 1), round(short_mm * GEN[1], 1)]
                                     if short_mm is not None else None),
                   area_mm2=round(r.get("area_mm2", 0.0), 4) or None,
                   confidence=conf, flags=flags, do_not_draw_as_component=dnd)
        if why: row["why"] = why
        return row

    rows = []
    for i, pd in enumerate(sorted(pads["pads"], key=lambda q: math.atan2(q["cy_px"] - cy, q["cx_px"] - cx))):
        d = pd["d_mm"]
        rows.append(mk(f"KP{i:03d}", pd, "gold colour AND circular shape (k_backface pads)",
                       "round gold pad - the test-point / probe-pad field", d, d,
                       "high" if 0.45 < d < 0.80 else "medium",
                       ["diameter_is_equivalent_circle"] +
                       ([] if 0.45 < d < 0.80 else ["outside_the_main_pad_population"])))
    for j, c in enumerate(cont.get("contacts", [])):
        lo = max(c["w_mm"], c["h_mm"]); sh = min(c["w_mm"], c["h_mm"])
        rows.append(mk(f"KC{j:03d}", c, "neutral bright metal + symmetric-pair search (k_backface contacts)",
                       f"battery contact, O'Flynn label {c.get('oflynn_label')}", lo, sh,
                       "medium", ["extent_is_pad_OR_spring_not_separable"], False,
                       "This photograph shows the board assembled in the shell. Whether this "
                       "extent is the BOARD PAD or the SPRUNG CONTACT sitting on it is NOT "
                       "SEPARABLE in plan view. FCC internal photo 4 - the battery cavity with "
                       "the contacts and no board - is the frame that separates them. DRAW THE "
                       "POSITION; do not take the extent as a pad dimension."))

    # A ROW THAT CANNOT BE ON THE BOARD MUST NOT BE HANDED OVER AS BOARD GEOMETRY.
    # The OD is a BOUND, 24.95-26.34 mm (board.json), so the largest radius any feature
    # can have is 13.17 mm. Anything beyond that is on the shell or the plastic carrier,
    # not on the copper. Flagged rather than deleted, because a detection that was made
    # and then rejected is a different object from one that was never made.
    R_MAX = 13.17
    n_out = 0
    for r in rows:
        if r["r_mm"] > R_MAX:
            n_out += 1
            r["do_not_draw_as_component"] = True
            r["flags"] = r["flags"] + ["outside_the_board_OD_bound"]
            r["why"] = (f"r = {r['r_mm']:.3f} mm exceeds {R_MAX} mm, the largest radius allowed by "
                        f"the OUTER DIAMETER BOUND of 24.95-26.34 mm (board.json - the OD is a "
                        f"bound and not a number). This feature is on the shell or the plastic "
                        f"antenna carrier, not on the copper. NOT BOARD GEOMETRY.")
    out_note = (f"{n_out} of {len(rows)} rows lie outside the board's own OD bound and are "
                f"flagged outside_the_board_OD_bound with do_not_draw_as_component set. They are "
                f"kept so the count is honest.")
    out = dict(
        generated_utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        git_rev=subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                               capture_output=True, text=True).stdout.strip(),
        producer="L9 THE COMPARISON lane",
        side=("BACK = the BATTERY-CONTACT / COIL / TEST-POINT side. O'Flynn's "
              "frontside-fullres.jpeg IS this side. This is the face the Replica had NOT "
              "drawn (THREE-WAY.md row 24)."),
        source_image="images/airtag/oflynn-frontside-fullres.jpeg",
        frame=dict(origin="board centre, transferred from FCC internal photo 7 through "
                          "c_register's homography (view fcc7-back, added by this lane - the "
                          "catalogue previously held NO ruler-bearing view of this face, which "
                          "is why this face had never been measured)",
                   axes="+x right, +y DOWN (image convention); theta from +x through +y",
                   origin_px=[cx, cy]),
        scale=dict(stored_px_per_mm=ppm,
                   basis="metrology/scale-at-board-photo7.json - m_scale_at at the board "
                         "(932,752), bottom and right rule routes 0.45% apart",
                   spread_over_board_pct=fit["transferred_scale"]["spread_pct"],
                   genuine_px_per_mm=list(GEN),
                   decoration_factor=f"{ppm/GEN[1]:.1f}-{ppm/GEN[0]:.1f}x more stored pixels "
                                     f"than resolved detail (M06)"),
        uncertainty=dict(registration_holdout_mm=0.1256,
                         registration_holdout_genuine_px=[round(0.1256 * GEN[0], 2),
                                                          round(0.1256 * GEN[1], 2)],
                         note="DO NOT QUOTE ANY POSITION TO 0.01 mm. The floor is 4-5 genuine px."),
        IF_YOU_MAP_A_REGISTERED_POSITION_YOURSELF_READ_THIS=(
            "*** c_register's HOMOGRAPHY LANDS IN THE PRE-AVERAGED SOURCE FRAME, NOT IN "
            "FULL-RESOLUTION PIXELS. *** It downsamples the source to roughly the target's "
            "sampling so that warping is not aliasing a much finer image - for this pair the "
            "factor is fit['source']['pre_average'] = 5.13 - and H therefore returns "
            "coordinates in that reduced frame. MULTIPLY BY pre_average TO GET FULL-RES "
            "PIXELS. Omitting it put this file's board centre at (224, 235) instead of "
            "(1152, 1207), which was caught ONLY because it was visibly absurd. A 5% frame "
            "error would not have looked wrong and nothing downstream would have questioned "
            "it. Every position in `rows` below already has this applied; the warning is here "
            "for anyone mapping a NEW position through the same transform. This applies "
            "equally to the FRONT registration, which uses the same tool."),
        THE_CAVEAT_UNDER_EVERY_MILLIMETRE_HERE=(
            "*** THE SCALE COMES FROM A DIFFERENT PHYSICAL BOARD. *** FCC internal photo 7 is "
            "920-08283-01, data code 3119 - a 2019 engineering build. O'Flynn's photograph, "
            "which every position here is measured in, is 820-01736-A, data code 2920 17 - "
            "2020 production. A uniform dimensional difference between the two is ABSORBED "
            "INTO THE FITTED SCALE and leaves the held-out residual COMPLETELY UNCHANGED, "
            "because the check divides both sides by the same number. Registration "
            "consistency is not scale accuracy. It cannot be settled from this machine; a "
            "caliper on one board of each part number settles it. THE SAME CAVEAT ALREADY "
            "APPLIED, UNSTATED, TO THE FRONT HANDOFF's 106.313 px/mm."),
        controls=dict(
            negative="the pad detector off the board (r>1000 px): 0 pads. It can come back empty.",
            positive=("Colin O'Flynn's 2021 annotation, oflynn-frontside-tpnames.jpg - the SAME "
                      "photograph rescaled, NCC 0.9993 with the red pixels masked out, so the "
                      "mapping is exact and the annotation is EXTERNAL to this method. His label "
                      "positions sit a median 0.462 mm from a detection; 4000 random points on "
                      "the same annulus sit 1.973 mm away. SEPARATION 4.27x, floor 2.00x. The "
                      "null is the load-bearing part: he writes each number BESIDE its pad and "
                      "this annulus is dense, so absolute distance would have proved nothing."),
            contacts=("the two positive tabs were found by a SYMMETRIC-PAIR SEARCH - same "
                      "radius, mirrored about the vertical axis, equal area - and O'Flynn's "
                      "names are the CHECK, not the driver. Result: areas 3.3% apart, radii "
                      "0.253 mm apart, midpoint 0.487 mm off axis, all three within 2.44 mm of "
                      "a name he wrote.")),
        excluded=[
            dict(what="the five bulk capacitors", verdict="CANNOT DETERMINE",
                 why=("the measured size is a function of the operator's window - 3.192 x 1.581 mm "
                      "at a 1.6 mm span and 4.699 x 4.414 mm at 2.4 mm. See evidence/E08 sec.2.4. "
                      "3.192 x 1.581 is EIA 3216 / Case A to 0.25% and 1.2% and is very likely "
                      "correct; it is NOT published because a number that matches what you "
                      "expected, from a method that also produces numbers that do not, is not a "
                      "measurement."),
                 instruction=("DO NOT place these from candidates_not_published in "
                              "metrology/backface-caps.json. They are leads with their refusal "
                              "attached, not sizes.")),
            dict(what="the wound coil's inner and outer diameter", verdict="CANNOT DETERMINE",
                 why=("L1's copper-fraction threshold does not transfer out of the 26 mm crop it "
                      "was set in. In the full frame the same criterion returns a band 2.732 mm "
                      "wide against M01's 0.727 mm, because the whole board's gold is now in "
                      "view. Control separation 1.37x against a 2.00x floor. E08 sec.4b."),
                 instruction=("Use M01's ID 9.380 / OD 10.834 mm if you need a coil, and carry "
                              "M01's datum caveat with it. Do NOT use the numbers in "
                              "metrology/backface-coil.json.")),
            dict(what="the overexposed centre dome", verdict="EXCLUDED BY NAME",
                 why=("a 78.1 mm2 neutral-metal blob at r 0.46 mm. M01 sec.4 records that the "
                      "saturated white core is the magnet/dome assembly. Excluded by name rather "
                      "than by a size threshold chosen to make the answer come out."),
                 instruction="not a contact and not a part."),
        ],
        known_gaps=[
            dict(what="whether a contact extent is the BOARD PAD or the SPRUNG CONTACT on it",
                 measured=False, do_not_draw_as_measured=True,
                 note=("coincident in plan view in an assembled photograph. FCC internal photo 4 "
                       "shows the battery cavity with the contacts and NO BOARD and is the frame "
                       "that separates them. It is already in images/airtag. USE THE CONTACT "
                       "POSITIONS; do not take their extents as pad dimensions.")),
            dict(what="every part on this face that is not a round gold pad or a battery contact",
                 measured=False, do_not_draw_as_measured=True,
                 note=("the five capacitors, the two small ICs, the silkscreen and the DataMatrix "
                       "are all present in the photograph and NONE of them is in these rows. This "
                       "file is a pad and contact file, not a component file. A face drawn from it "
                       "alone will be knowingly incomplete, and that is better than looking "
                       "complete.")),
        ],
        next_steps_named_not_left_loose=[
            dict(what="the coil by RADIAL PERIODICITY at AWG 35's ~0.145 mm turn pitch",
                 why=("it is a two-for-one and not a loose end: periodicity separates a WOUND coil "
                      "from a field of gold pads in a way no colour threshold can, AND it yields a "
                      "TURN COUNT - which is exactly what separates the NFC antenna from a voice "
                      "coil in evidence/E02, still OPEN. It also reopens the one comparison that "
                      "can only disagree about SCALE: O'Flynn's retracted '~26 mm' tilde against "
                      "the FCC steel rulers, on one object, in a photograph both measurements "
                      "share.")),
            dict(what="the capacitor width estimator",
                 why=("k_backface selftest S1 fails on a SYNTHETIC - a part 2.200 mm wide measures "
                      "0.855 mm - so it can be iterated without touching the photograph. Then mask "
                      "to the part before profiling: every window failure is contamination by "
                      "neighbours, and C1/C2/C3 sit within 2 mm of each other on the left rim.")),
            dict(what="the EIA case-code check, ONLY after a size survives window-invariance",
                 why=("it would be the first scale evidence in this project that does NOT pass "
                      "through the FCC rulers or the 920-/820- board-identity assumption above. "
                      "k_backface already implements it and refuses to quote it when the nearest "
                      "two codes are ambiguous.")),
        ],
        counts=dict(total=len(rows),
                    pads=len([r for r in rows if r["id"].startswith("KP")]),
                    contacts=len([r for r in rows if r["id"].startswith("KC")]),
                    do_not_draw=len([r for r in rows if r["do_not_draw_as_component"]]),
                    outside_od_bound=n_out,
                    pad_median_diameter_mm=pads["diameter_mm"]["median"],
                    pad_diameter_iqr_mm=pads["diameter_mm"]["iqr"]),
        outside_od_bound_note=out_note,
        rows=rows)
    p2 = os.path.join(LANE, "metrology", "HANDOFF-positions-back.json")
    json.dump(out, open(p2, "w"), indent=2)
    print(f"k_backface handoff")
    print(f"  origin (board centre) in source px: ({cx:.2f}, {cy:.2f}) - mapped from photo 7's")
    print(f"  fitted centre through the registration homography, not eyeballed")
    print(f"  {len(rows)} rows: {out['counts']['pads']} pads + {out['counts']['contacts']} contacts")
    print(f"  pad median diameter {out['counts']['pad_median_diameter_mm']:.4f} mm, "
          f"IQR {out['counts']['pad_diameter_iqr_mm']:.4f} mm")
    print(f"  {n_out} rows flagged outside_the_board_OD_bound + do_not_draw_as_component")
    print(f"  3 exclusions and 2 known gaps carried across as named fields")
    print(f"  wrote {os.path.relpath(p2, REPO)}")
    return PASS

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
    sub.add_parser("coil"); sub.add_parser("pads"); sub.add_parser("contacts"); sub.add_parser("handoff")
    c = sub.add_parser("calibrate")
    c.add_argument("--n", type=int, default=120)
    c.add_argument("--margin", type=float, default=1.0)
    a = p.parse_args()
    return {"caps": cmd_caps, "selftest": cmd_selftest, "controls": cmd_controls,
            "calibrate": cmd_calibrate, "coil": cmd_coil, "pads": cmd_pads, "contacts": cmd_contacts, "handoff": cmd_handoff}[a.cmd](a)

if __name__ == "__main__":
    sys.exit(main())
