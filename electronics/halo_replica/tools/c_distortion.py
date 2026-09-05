#!/usr/bin/env python3
"""c_distortion - measure a lens's distortion from something that is straight by
construction, and refuse when the photograph cannot support it.

Lane L2 (component-side metrology), halo Replica, 2026-09-05.

WHY THIS EXISTS
    R11 measured a smooth, spatially coherent misfit in the registration between
    the FCC photographs and O'Flynn's, on BOTH faces (z = +8.5 and +11.1 against
    permutation nulls). Three causes were left open and could not be separated:
    a board that is not flat, uncorrected LENS DISTORTION, or a difference
    between two physically different boards. Adding free parameters did not help
    - poly2 came out 3.8x WORSE on the front.

    But one of the three can be measured directly and without touching the board,
    because the FCC frames contain STEEL RULERS, and a steel rule's edge is
    STRAIGHT. A straight edge that images curved is lens distortion, in pixels,
    with no model fitted to the board at all.

THREE VERDICTS, AND THEY ARE THE EXIT CODE
    0  PASS              a curvature, with the input it came from
    1  FAIL              measured, and outside the stated tolerance
    2  CANNOT DETERMINE  the edge is not measurable here. Never a default.

THE CONTROLS
  * NULL BY SHUFFLE. The curvature coefficient is refitted many times with the
    edge samples' POSITIONS PERMUTED. That destroys systematic curvature and
    keeps the noise exactly as it is, so the null says what this fit reads on a
    straight edge measured this noisily. A curvature that does not stand clear of
    that null is CANNOT DETERMINE, not zero.
  * SIGN CONSISTENCY ACROSS EDGES. Radial distortion has ONE centre. Two edges on
    different sides of the frame must bow in the directions a single centre
    predicts. If they do not, whatever was measured is not radial distortion, and
    saying so is the point of measuring two.
  * A SYNTHETIC EDGE WITH A KNOWN ANSWER, both ways: a truly straight edge must
    come back straight, and an edge bent by a known amount must come back bent by
    that amount. Both are selftest cases.
"""
import argparse, json, math, os, sys, tempfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
IMGDIR = os.path.join(REPO, 'images', 'airtag')
PASS, FAIL, CANNOT = 0, 1, 2
V = {PASS: 'PASS', FAIL: 'FAIL', CANNOT: 'CANNOT DETERMINE'}

# Edges that are STRAIGHT BY CONSTRUCTION: the long outer edges of the steel
# rules. Boxes bracket the edge; the scan finds it inside them.
# Rule edge y/x values are lane L1's, from metrology/ruler-calibration.json.
EDGES = {
    'photo6-bottom': dict(image='fcc-BCGA2187-internal-photo-6.jpg', axis='h',
                          box=(400, 1111, 2000, 1151), note="bottom rule's top edge, "
                          "rule_edge_px 1131 (L1 ruler-calibration photo6_bottom)"),
    'photo6-right':  dict(image='fcc-BCGA2187-internal-photo-6.jpg', axis='v',
                          box=(1503, 100, 1543, 900), note="right rule's left edge, "
                          "rule_edge_px 1523 (L1 ruler-calibration photo6_right)"),
    'photo7-bottom': dict(image='fcc-BCGA2187-internal-photo-7.jpg', axis='h',
                          box=(400, 1093, 2000, 1133), note="bottom rule's top edge, "
                          "rule_edge_px 1113"),
    'photo7-right':  dict(image='fcc-BCGA2187-internal-photo-7.jpg', axis='v',
                          box=(1537, 100, 1577, 900), note="right rule's left edge, "
                          "rule_edge_px 1557"),
}


def gray(path):
    return np.asarray(Image.open(path).convert('L'), dtype=np.float64)


def scan_edge(img, box, axis, min_grad=6.0, smooth=1.0):
    """Sub-pixel edge position along the box, one sample per column (h) or row (v).

    Returns (t, e, kept, discarded) where t is the along-edge coordinate and e the
    across-edge sub-pixel position. A sample whose gradient peak is weak, or sits
    on the box boundary (so the true edge may be outside the box), is DISCARDED
    and counted - never interpolated over.
    """
    x0, y0, x1, y1 = box
    sub = img[y0:y1, x0:x1]
    if axis == 'v':
        sub = sub.T
        t0, e0 = y0, x0
    else:
        t0, e0 = x0, y0
    n_t = sub.shape[1]
    ts, es = [], []
    disc = {}
    def bump(k): disc[k] = disc.get(k, 0) + 1
    for j in range(n_t):
        col = sub[:, j].astype(np.float64)
        if smooth > 0:
            # PAD BY REPLICATION, not with zeros. np.convolve(mode='same') pads
            # with zeros, which manufactures a large gradient at both ends of every
            # column - a fake edge exactly where a real one is hardest to see. It
            # was caught by the selftest's blank field, which discarded all 800
            # samples as 'on_box_boundary' instead of 'weak_gradient'.
            k = np.array([1.0, 2.0, 1.0]); k /= k.sum()
            col = np.convolve(np.pad(col, 1, mode='edge'), k, mode='valid')
        g = np.abs(np.diff(col))
        if g.size < 7:
            bump('too_short'); continue
        i = int(np.argmax(g))
        if g[i] < min_grad:
            bump('weak_gradient'); continue
        if i < 2 or i >= g.size-2:
            bump('on_box_boundary'); continue
        # GRADIENT CENTROID over a +-2 window, not a 3-point parabola. The parabola
        # pixel-locks on a hard step: it read a known 4.0 px bow as 3.032 px, a 24%
        # under-read, while reading a 1.0 px bow as 1.108. A position estimator whose
        # bias depends on the answer cannot measure a curve.
        w = np.arange(i-2, i+3)
        gw = g[w] - min(g[w].min(), 0.0)
        if gw.sum() <= 0:
            bump('weak_gradient'); continue
        off = float((w*gw).sum()/gw.sum())
        ts.append(t0 + j)
        es.append(e0 + off + 0.5)
    return np.asarray(ts, float), np.asarray(es, float), len(ts), disc


def curvature(t, e, trials=600, seed=5):
    """Fit line and line+quadratic. Report the SAGITTA - the greatest departure of
    the fitted quadratic from the straight chord joining its endpoints - which is
    the number a reader can picture, in pixels.

    The null permutes t among the samples, which cannot produce systematic
    curvature but keeps the noise, so it says what this fit reads on a straight
    edge measured this noisily.
    """
    if len(t) < 30:
        return None
    tc = (t - t.mean())/max(t.std(), 1e-9)
    L1 = np.polyfit(tc, e, 1)
    L2 = np.polyfit(tc, e, 2)
    r1 = e - np.polyval(L1, tc)
    r2 = e - np.polyval(L2, tc)

    def sag(c2):
        lo, hi = tc.min(), tc.max()
        mid = 0.5*(lo+hi)
        # quadratic minus the chord through its endpoints, evaluated at the middle
        return abs(c2*((hi-lo)/2.0)**2)/2.0*2.0

    s = sag(L2[0])
    rng = np.random.default_rng(seed)
    null = np.empty(trials)
    for k in range(trials):
        p = rng.permutation(len(tc))
        null[k] = abs(np.polyfit(tc, e[p], 2)[0])
    m, sd = float(null.mean()), float(null.std())
    z = (abs(L2[0]) - m)/sd if sd > 0 else float('nan')
    return dict(n=int(len(t)), span_px=float(t.max()-t.min()),
                slope=float(L1[0]), quad_coeff=float(L2[0]),
                sagitta_px=float(s), sign=int(np.sign(L2[0])),
                resid_sd_line_px=float(r1.std()), resid_sd_quad_px=float(r2.std()),
                null_mean=m, null_sd=sd, z=float(z),
                null_note="quadratic coefficient refitted %d times with the along-edge "
                          "positions PERMUTED: destroys curvature, keeps the noise" % trials)


def bows_away(axis, box, cx, cy, quad_coeff):
    """+1 if this edge's midpoint departs AWAY from the frame centre (barrel),
    -1 if TOWARD it (pincushion). Factored out of run_edge so it can be tested
    against constructed inputs - the version inlined there was WRONG on its first
    run (it demanded opposite signs from two edges that barrel makes agree) and a
    control that cannot be exercised is how that survived to be printed."""
    x0, y0, x1, y1 = box
    if axis == 'h':
        outward = math.copysign(1.0, (y0+y1)/2.0 - cy)
    else:
        outward = math.copysign(1.0, (x0+x1)/2.0 - cx)
    return int(math.copysign(1.0, -quad_coeff) * outward)

def measure(name, min_grad=6.0):
    spec = EDGES[name]
    img = gray(os.path.join(IMGDIR, spec['image']))
    t, e, kept, disc = scan_edge(img, spec['box'], spec['axis'], min_grad=min_grad)
    c = curvature(t, e) if kept >= 30 else None
    return spec, t, e, kept, disc, c


def run_edge(a):
    names = [a.edge] if a.edge else list(EDGES)
    print("c_distortion edge")
    print("  A steel rule's long edge is STRAIGHT BY CONSTRUCTION. Any bow in it is the "
          "LENS,\n  not the board - no model of the board is fitted anywhere in this file.")
    out, worst = {}, 0.0
    img_shape = {}
    verdict = PASS
    for n in names:
        spec, t, e, kept, disc, c = measure(n, a.min_grad)
        img_shape[spec['image']] = gray(os.path.join(IMGDIR, spec['image'])).shape
        print("\n  EDGE %s" % n)
        print("    image %s   box %s   axis %s" % (spec['image'], spec['box'], spec['axis']))
        print("    %s" % spec['note'])
        print("    samples %d kept, %d discarded %s"
              % (kept, sum(disc.values()), ' '.join('%s=%d' % kv for kv in sorted(disc.items()))))
        if c is None:
            print("    CANNOT DETERMINE: fewer than 30 usable edge samples")
            out[n] = dict(verdict='CANNOT DETERMINE', kept=kept, discarded=disc)
            verdict = max(verdict, CANNOT)
            continue
        print("    straight-line fit residual sd %.3f px   with a quadratic %.3f px"
              % (c['resid_sd_line_px'], c['resid_sd_quad_px']))
        print("    SAGITTA %.3f px over a %.0f px span   sign %+d" %
              (c['sagitta_px'], c['span_px'], c['sign']))
        print("    null (positions permuted): |c2| %.4g +- %.4g   ->  z = %+.1f"
              % (c['null_mean'], c['null_sd'], c['z']))
        if c['z'] < 3.0:
            print("    CANNOT DETERMINE: the bow does not stand clear of its own null.")
            c['reading'] = 'CANNOT DETERMINE'
        else:
            print("    MEASURED: this edge is genuinely bowed.")
            c['reading'] = 'MEASURED'
            worst = max(worst, c['sagitta_px'])
        out[n] = dict(spec=dict(image=spec['image'], box=list(spec['box']),
                                axis=spec['axis'], note=spec['note']),
                      kept=kept, discarded=disc, **c)

    # SIGN CONSISTENCY: radial distortion has ONE centre, so edges on different
    # sides of a frame must bow the way a single centre predicts. Two edges that
    # bow the same way in image coordinates cannot both be radial about a centre
    # between them.
    for img_name in sorted({EDGES[n]['image'] for n in names}):
        pair = [n for n in names if EDGES[n]['image'] == img_name
                and out.get(n, {}).get('reading') == 'MEASURED']
        if len(pair) == 2:
            # *** THIS CONTROL WAS WRONG ON ITS FIRST RUN AND IS KEPT CORRECTED. ***
            # It required OPPOSITE signs and reported "not radial distortion" for
            # photo 7. Re-deriving the geometry: under BARREL distortion a straight
            # line bows AWAY from the image centre. The bottom rule's top edge lies
            # BELOW the centre, so away = larger y at its midpoint; the right rule's
            # left edge lies RIGHT of the centre, so away = larger x at its midpoint.
            # In image coordinates both give the SAME sign. Requiring opposite signs
            # inverted the verdict and would have buried a real measurement.
            # The test is not "do the signs differ" - it is "does each edge bow away
            # from the frame centre, or toward it, CONSISTENTLY".
            H, W = img_shape[img_name]
            cx, cy = W/2.0, H/2.0
            aways, det = [], []
            for nm in pair:
                sp = EDGES[nm]
                x0, y0, x1, y1 = sp['box']
                aw = bows_away(sp['axis'], sp['box'], cx, cy, out[nm]['quad_coeff'])
                outward = (math.copysign(1.0, (y0+y1)/2.0 - cy) if sp['axis'] == 'h'
                           else math.copysign(1.0, (x0+x1)/2.0 - cx))
                aways.append(aw)
                det.append(dict(edge=nm, quad_sign=out[nm]['sign'], outward=outward,
                                bows=('AWAY from the frame centre' if aw > 0
                                      else 'TOWARD the frame centre'),
                                sagitta_px=out[nm]['sagitta_px']))
            print("\n  RADIAL CONSISTENCY in %s" % img_name)
            for d in det:
                print("    %-15s sagitta %.3f px, bows %s" % (d['edge'], d['sagitta_px'], d['bows']))
            ok = (aways[0] == aways[1])
            kind = ('BARREL' if aways[0] > 0 else 'PINCUSHION') if ok else None
            print("    Under BARREL a straight line bows AWAY from the image centre and "
                  "under\n    PINCUSHION toward it - so both edges must agree. Disagreement "
                  "means\n    whatever bows them is NOT a single radial distortion.")
            print("    -> %s" % ("CONSISTENT with a single radial centre: %s" % kind if ok
                                 else "NOT consistent with a single radial centre"))
            out.setdefault('_consistency', {})[img_name] = dict(
                edges=pair, detail=det, consistent=bool(ok), kind=kind)

    res = dict(tool='c_distortion.py', verb='edge',
               why="separate LENS DISTORTION from a non-flat board as the cause of the "
                   "coherent registration misfit measured in R11",
               edges=out, worst_measured_sagitta_px=worst, verdict=V[verdict])
    if a.json_out:
        with open(a.json_out, 'w') as fh: json.dump(res, fh, indent=1)
        print("\n  wrote %s" % a.json_out)
    print("\n  %s" % V[verdict])
    return verdict


def _synth_edge(tmp, bow_px, noise=1.5, n=1600, name='e.png'):
    """A synthetic dark/light boundary with a KNOWN bow, so the reader is graded
    against an answer instead of against itself."""
    h = 60
    a = np.zeros((h, n), dtype=np.float64)
    rng = np.random.default_rng(4)
    x = np.arange(n, dtype=np.float64)
    xc = (x - x.mean())/(n/2.0)
    y_edge = h/2.0 + bow_px*(1.0 - xc**2)          # sagitta = bow_px at the middle
    # COVERAGE model, not a where() plus a blend. The first version of this fixture
    # set the partial pixel to 40*(1-f) + 200*f, which is the blend INVERTED: for an
    # edge at y=34.3 it made row 34 mostly dark when 70% of it is light. The bias is
    # sub-pixel but it varies with f, and f varies systematically along a bowed edge,
    # so it read a known 4.0 px bow as 3.07 px while reading 1.0 px as 1.02. The tool
    # was right; the ruler I was grading it against was bent.
    rows = np.arange(h, dtype=np.float64)[:, None]      # row i covers [i, i+1)
    frac_dark = np.clip(y_edge[None, :] - rows, 0.0, 1.0)
    a = 40.0*frac_dark + 200.0*(1.0-frac_dark)
    a += rng.normal(0, noise, a.shape)
    p = os.path.join(tmp, name)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(p)
    return p, (0, 0, n, h)


def sagitta_for_k(axis, box, W, H, k, n=400):
    """Predicted sagitta of a STRAIGHT line at this edge's place in the frame, after
    a radial distortion r' = r(1 + k*rn^2) with rn = r/(W/2) about the frame centre.
    Computed numerically rather than in closed form, so the model in the docstring
    and the model in the code cannot drift apart."""
    x0, y0, x1, y1 = box
    cx, cy = W/2.0, H/2.0
    if axis == 'h':
        t = np.linspace(x0, x1, n); e = np.full(n, (y0+y1)/2.0)
        X, Y = t, e
    else:
        t = np.linspace(y0, y1, n); e = np.full(n, (x0+x1)/2.0)
        X, Y = e, t
    dx, dy = X-cx, Y-cy
    rn = np.hypot(dx, dy)/(W/2.0)
    f = 1.0 + k*rn**2
    Xd, Yd = cx + dx*f, cy + dy*f
    obs = Yd if axis == 'h' else Xd
    tc = (t-t.mean())/max(t.std(), 1e-9)
    c2 = np.polyfit(tc, obs, 2)[0]
    return float(abs(c2)*((tc.max()-tc.min())/2.0)**2), float(np.sign(c2))


def solve_k(axis, box, W, H, target_sag, lo=-0.5, hi=0.0, iters=60):
    """Bisect for the k whose predicted sagitta matches the measured one. Negative
    k is barrel."""
    f = lambda k: sagitta_for_k(axis, box, W, H, k)[0] - target_sag
    if f(lo)*f(hi) > 0:
        return None
    for _ in range(iters):
        mid = 0.5*(lo+hi)
        if f(lo)*f(mid) <= 0: hi = mid
        else: lo = mid
    return 0.5*(lo+hi)


def run_solvek(a):
    print("c_distortion solve-k")
    print("  Each MEASURED edge is asked what single barrel coefficient would produce the")
    print("  bow it shows. Two edges in one frame are two INDEPENDENT routes to one number.")
    print("  WHAT WOULD HAVE TO HAPPEN FOR THEM TO DISAGREE: the two edges sit at different")
    print("  radii and different orientations, so a bow caused by anything OTHER than a")
    print("  single radial term about the frame centre - a tilted rule, a scanner artifact,")
    print("  a bent rule - implies different k. Agreement is therefore a real check and not")
    print("  an arithmetic identity.")
    out = {}
    for n in (a.edge and [a.edge] or list(EDGES)):
        spec, t, e, kept, disc, c = measure(n, a.min_grad)
        if c is None or c['z'] < 3.0:
            print("\n  %-15s skipped: %s" % (n, 'no usable edge' if c is None else
                                             'bow does not clear its null (z=%+.1f)' % c['z']))
            out[n] = dict(skipped=True, z=(c or {}).get('z'))
            continue
        H_, W_ = gray(os.path.join(IMGDIR, spec['image'])).shape
        k = solve_k(spec['axis'], spec['box'], W_, H_, c['sagitta_px'])
        out[n] = dict(image=spec['image'], sagitta_px=c['sagitta_px'], k=k,
                      z=c['z'], W=W_, H=H_)
        print("\n  %-15s sagitta %.3f px  ->  k = %s"
              % (n, c['sagitta_px'], ('%.5f' % k) if k is not None else 'no solution in range'))
    for img in sorted({v.get('image') for v in out.values() if v.get('k') is not None}):
        ks = [(n, v['k']) for n, v in out.items() if v.get('image') == img and v.get('k')]
        if len(ks) == 2:
            k0, k1 = ks[0][1], ks[1][1]
            spread = abs(k0-k1)/abs(0.5*(k0+k1))
            print("\n  AGREEMENT in %s: k = %.5f (%s) and %.5f (%s), %.0f%% apart"
                  % (img, k0, ks[0][0], k1, ks[1][0], 100*spread))
            print("  -> %s" % ("the two edges agree on ONE barrel coefficient"
                               if spread < 0.5 else
                               "the two edges do NOT agree - a single radial term does not "
                               "explain both, so at least one bow has another cause"))
            out.setdefault('_agreement', {})[img] = dict(k=[k0, k1], spread=spread,
                                                         agree=bool(spread < 0.5))
    if a.json_out:
        with open(a.json_out, 'w') as fh: json.dump(out, fh, indent=1)
        print("\n  wrote %s" % a.json_out)
    return PASS

def run_selftest(a):
    print("c_distortion selftest - synthetic edges with known answers, and deliberate breaks")
    tmp = tempfile.mkdtemp(prefix='c_distortion-selftest-')
    res = []
    def rec(ok, m):
        res.append(ok); print("  %s  %s" % ('PASS' if ok else 'FAIL', m))

    for bow in (0.0, 1.0, 4.0):
        p, box = _synth_edge(tmp, bow, name='e%s.png' % bow)
        img = gray(p)
        t, e, kept, disc = scan_edge(img, box, 'h')
        c = curvature(t, e)
        if bow == 0.0:
            rec(c is not None and c['z'] < 3.0,
                "a STRAIGHT edge reads as straight: sagitta %.3f px, z=%+.1f (must stay "
                "under 3)" % (c['sagitta_px'], c['z']))
        else:
            err = abs(c['sagitta_px'] - bow)
            rec(err < 0.10*bow and c['z'] > 3.0,
                "a KNOWN %.1f px bow is recovered: %.3f px (err %.3f), z=%+.1f"
                % (bow, c['sagitta_px'], err, c['z']))

    # deliberate break: a blank field has no edge to find
    blank = os.path.join(tmp, 'blank.png')
    Image.fromarray(np.full((60, 800), 128, dtype=np.uint8)).save(blank)
    t, e, kept, disc = scan_edge(gray(blank), (0, 0, 800, 60), 'h')
    rec(kept == 0 and disc.get('weak_gradient', 0) == 800,
        "a BLANK field yields no edge samples, for the RIGHT reason - weak gradient, "
        "not a boundary artifact of the smoothing: %d kept, %s" % (kept, dict(disc)))

    # deliberate break: too few samples must refuse, not extrapolate
    p, box = _synth_edge(tmp, 2.0, name='short.png')
    t, e, kept, _ = scan_edge(gray(p), box, 'h')
    rec(curvature(t[:20], e[:20]) is None,
        "fewer than 30 samples REFUSES rather than fitting: curvature() returned None")

    # the sign must follow the direction of the bow
    p1, b1 = _synth_edge(tmp, 3.0, name='up.png')
    p2, b2 = _synth_edge(tmp, -3.0, name='dn.png')
    t1, e1, _, _ = scan_edge(gray(p1), b1, 'h'); c1 = curvature(t1, e1)
    t2, e2, _, _ = scan_edge(gray(p2), b2, 'h'); c2 = curvature(t2, e2)
    rec(c1['sign'] != c2['sign'],
        "the SIGN follows the direction of the bow: %+d for +3 px, %+d for -3 px"
        % (c1['sign'], c2['sign']))

    # THE k-INVERSION, round-tripped. Without this, a disagreement between two
    # edges could be my arithmetic rather than the photograph - and on 2026-09-05
    # it WAS a disagreement (photo 7's two edges implied k 9.7x apart), which is
    # only publishable as a finding if the inversion is known to be sound.
    W_, H_ = 2134, 1600
    K_TRUE = -0.030
    ok_rt = True
    for nm, (ax, bx) in {'bottom': ('h', (400, 1111, 2000, 1151)),
                         'right': ('v', (1503, 100, 1543, 900))}.items():
        sg, _ = sagitta_for_k(ax, bx, W_, H_, K_TRUE)
        kk = solve_k(ax, bx, W_, H_, sg)
        ok_rt &= (kk is not None and abs(kk-K_TRUE) < 0.002)
    rec(ok_rt,
        "k INVERSION round-trips on BOTH edge geometries: k=%.3f -> sagitta -> k "
        "recovered to within 0.002 for the bottom and right edges alike" % K_TRUE)
    sg_b, _ = sagitta_for_k('h', (400, 1111, 2000, 1151), W_, H_, K_TRUE)
    sg_r, _ = sagitta_for_k('v', (1503, 100, 1543, 900), W_, H_, K_TRUE)
    kb = solve_k('h', (400, 1111, 2000, 1151), W_, H_, sg_b)
    kr = solve_k('v', (1503, 100, 1543, 900), W_, H_, sg_r)
    spread = abs(kb-kr)/abs(0.5*(kb+kr))
    rec(spread < 0.05,
        "the AGREEMENT test CAN pass: two edges generated from ONE k=%.3f come back "
        "%.1f%% apart (sagittas %.2f and %.2f px are very different, so agreement is "
        "not an identity)" % (K_TRUE, 100*spread, sg_b, sg_r))

    # THE RADIAL-CONSISTENCY LOGIC, tested against constructed inputs. It was
    # wrong on its first real run - it demanded OPPOSITE signs and pronounced
    # photo 7 "not radial distortion" when photo 7 is cleanly barrel-distorted.
    # A 2134x1600 frame: centre (1067, 800).
    CX, CY = 1067.0, 800.0
    bot = ('h', (400, 1111, 2000, 1151))     # below the centre
    rgt = ('v', (1503, 100, 1543, 900))      # right of the centre
    b_bot = bows_away(bot[0], bot[1], CX, CY, -1.0)
    b_rgt = bows_away(rgt[0], rgt[1], CX, CY, -1.0)
    rec(b_bot == +1 and b_rgt == +1,
        "BARREL is read as barrel: a bottom edge BELOW centre and a right edge RIGHT "
        "of centre, both with a NEGATIVE quadratic, both bow AWAY (%+d, %+d) - this is "
        "the case the first version got backwards" % (b_bot, b_rgt))
    p_bot = bows_away(bot[0], bot[1], CX, CY, +1.0)
    p_rgt = bows_away(rgt[0], rgt[1], CX, CY, +1.0)
    rec(p_bot == -1 and p_rgt == -1,
        "PINCUSHION is read as pincushion: the same two edges with a POSITIVE "
        "quadratic both bow TOWARD the centre (%+d, %+d)" % (p_bot, p_rgt))
    rec(bows_away(bot[0], bot[1], CX, CY, -1.0) != bows_away(rgt[0], rgt[1], CX, CY, +1.0),
        "the control FIRES on genuinely inconsistent edges: one bowing away and one "
        "toward disagree, which no single radial centre can produce")
    top = ('h', (400, 100, 2000, 140))       # ABOVE the centre - outward flips
    rec(bows_away(top[0], top[1], CX, CY, +1.0) == +1,
        "an edge on the OTHER SIDE of the centre flips correctly: above centre, a "
        "POSITIVE quadratic is the one that bows away")

    ok = sum(1 for r in res if r)
    print("\n%d/%d passed, %d failed" % (ok, len(res), len(res)-ok))
    print("synthetic inputs kept at %s" % tmp)
    return PASS if ok == len(res) else FAIL


def run_doctor(a):
    print("c_distortion doctor")
    good = True
    print("  PASS  numpy %s" % np.__version__)
    for n, spec in EDGES.items():
        p = os.path.join(IMGDIR, spec['image'])
        e = os.path.exists(p); good &= e
        print("  %s  edge %-15s %s" % ('PASS' if e else 'FAIL', n, spec['image']))
    tmp = tempfile.mkdtemp(prefix='c_distortion-doctor-')
    p, box = _synth_edge(tmp, 2.5)
    t, e, kept, _ = scan_edge(gray(p), box, 'h')
    c = curvature(t, e)
    ok = c is not None and abs(c['sagitta_px']-2.5) < 0.6
    good &= ok
    print("  CANARY  known 2.50 px bow read back as %.3f px (z=%+.1f)"
          % (c['sagitta_px'], c['z']))
    print("  %s  canary - a doctor pass is a MEASUREMENT, not a ping" % ('PASS' if ok else 'FAIL'))
    return PASS if good else FAIL


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='verb', required=True)
    p = sub.add_parser('edge')
    p.add_argument('--edge', default=None, choices=list(EDGES))
    p.add_argument('--min-grad', type=float, default=6.0)
    p.add_argument('--json-out', default=None)
    q = sub.add_parser('solve-k')
    q.add_argument('--edge', default=None, choices=list(EDGES))
    q.add_argument('--min-grad', type=float, default=6.0)
    q.add_argument('--json-out', default=None)
    sub.add_parser('doctor'); sub.add_parser('selftest')
    a = ap.parse_args()
    return {'edge': run_edge, 'solve-k': run_solvek,
            'doctor': run_doctor, 'selftest': run_selftest}[a.verb](a)


if __name__ == '__main__':
    sys.exit(main())
