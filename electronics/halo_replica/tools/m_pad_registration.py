#!/usr/bin/env python3
"""m_pad_registration.py -- do FRONT and BACK agree on where the rim features are?

L1 PHOTOGRAPH METROLOGY lane, halo Replica.
SIDE NAMING: FRONT = component side (Apple's FCC caption). See M02.

WHY THIS EXISTS.  m_rim_pads.py counts edge-reaching features in ONE photograph
and its count does not clear its own control: at 0.218 mm per degree of rim arc,
chance alignment of the same brightness statistics produces as many.  So a
single image cannot settle the dossier's SIX tear-off joints.

THE STRONGER TEST.  An edge-plated pad or a tear-off stub goes THROUGH the board,
so it must appear at the SAME angular position on the FRONT and on the BACK.  A
surface component appears on one side only.  Photo 6 and photo 7 are the two
sides of the same board, so the set of angles that appear in BOTH is evidence a
single image cannot give.

THE BOARD IS FLIPPED between the two photographs, so angles MIRROR:
    theta_back = (mirror_axis - theta_front) mod 360
with the mirror axis unknown.  It is searched, which means the search can find a
spurious alignment -- so the peak is tested against a NULL built the same way:
one set's angles are replaced by uniform random angles and the SAME search over
the SAME axis grid is run again, so the null contains the same
maximise-over-360-alignments optimism as the measurement.  Reporting a matched
count without that null would be reporting the maximum of ~360 tries as if it
were one try.

Exit 0 if the agreement beats the null, 2 CANNOT DETERMINE.  Prints its inputs.
"""
import argparse, json, math, os, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def circ_match(A, B, tol):
    """How many of A have a partner in B within tol degrees (greedy, 1-to-1)."""
    used, n, pairs = set(), 0, []
    for a in A:
        best, bj = None, None
        for j, b in enumerate(B):
            if j in used:
                continue
            d = abs((a - b + 180) % 360 - 180)
            if d <= tol and (best is None or d < best):
                best, bj = d, j
        if bj is not None:
            used.add(bj); n += 1; pairs.append((round(a, 2), round(B[bj], 2), round(best, 2)))
    return n, pairs


def scan(A, B, tol, axes):
    best = (-1, None, None)
    for ax in axes:
        Bm = [(ax - b) % 360 for b in B]
        n, pairs = circ_match(A, Bm, tol)
        if n > best[0]:
            best = (n, ax, pairs)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--front", required=True, help="rim-pads json for the FRONT (photo 6)")
    ap.add_argument("--back", required=True, help="rim-pads json for the BACK (photo 7)")
    ap.add_argument("--tol-deg", type=float, default=4.0)
    ap.add_argument("--axis-step-deg", type=float, default=0.5)
    ap.add_argument("--use", default="edge_features", choices=["edge_features", "all_blobs"])
    ap.add_argument("--trials", type=int, default=2000)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    F = json.load(open(a.front)); B = json.load(open(a.back))
    fa = [b["angle_deg"] for b in F[a.use]]
    ba = [b["angle_deg"] for b in B[a.use]]
    axes = np.arange(0, 360, a.axis_step_deg)
    print("m_pad_registration.py -- inputs:")
    print(f"  FRONT {os.path.basename(a.front)}  run {F.get('run_utc')} git {F.get('git_rev')} "
          f"image sha {F.get('image_sha256_12')}")
    print(f"        {len(fa)} {a.use}: {[round(v,1) for v in fa]}")
    print(f"  BACK  {os.path.basename(a.back)}   run {B.get('run_utc')} git {B.get('git_rev')} "
          f"image sha {B.get('image_sha256_12')}")
    print(f"        {len(ba)} {a.use}: {[round(v,1) for v in ba]}")
    print(f"  model theta_back = (axis - theta_front) mod 360, axis searched over "
          f"{len(axes)} values at {a.axis_step_deg} deg")
    print(f"  a pair counts as agreeing within {a.tol_deg} deg")

    n, ax, pairs = scan(fa, ba, a.tol_deg, axes)
    print(f"\n  BEST ALIGNMENT: axis {ax:.1f} deg, {n} of {min(len(fa), len(ba))} possible "
          f"features agree")
    for p in pairs:
        print(f"    front {p[0]:7.2f} deg  <->  back {p[1]:7.2f} deg   (off by {p[2]:.2f})")

    rng = np.random.default_rng(20260905)
    null = np.array([scan(fa, list(rng.uniform(0, 360, len(ba))), a.tol_deg, axes)[0]
                     for _ in range(a.trials)])
    p = float((null >= n).mean())
    print(f"\n  NULL: the SAME search (same axis grid, same maximise-over-{len(axes)}) with the "
          f"back angles replaced by uniform random ones, {a.trials} trials")
    print(f"    null mean {null.mean():.2f}, p95 {np.percentile(null,95):.1f}, "
          f"p99 {np.percentile(null,99):.1f}, max {null.max()}")
    print(f"    p(null >= {n}) = {p:.4f}")
    ok = p < 0.01
    if ok:
        print(f"\n  THE TWO SIDES AGREE: {n} rim features at matching angular positions, "
              f"p = {p:.4f}. These go THROUGH the board.")
    else:
        print(f"\n  CANNOT DETERMINE: {n} matches is not beyond what the same search finds "
              f"against random angles (p = {p:.4f}). This does NOT show the sides disagree -- "
              f"it shows these photographs cannot register them.")
    out = dict(tool="m_pad_registration.py", front=os.path.basename(a.front),
               back=os.path.basename(a.back), front_run=F.get("run_utc"),
               back_run=B.get("run_utc"), feature_set=a.use, tol_deg=a.tol_deg,
               n_front=len(fa), n_back=len(ba), best_axis_deg=float(ax), n_matched=n,
               matched_pairs=pairs, null_mean=float(null.mean()),
               null_p99=float(np.percentile(null, 99)), null_max=int(null.max()),
               p_value=p, verdict="AGREE" if ok else "CANNOT DETERMINE")
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
