#!/usr/bin/env python3
"""r_frame.py -- the board frame, reconstructed from the ALLOW-LISTED inputs alone.

L10 BLIND RIM COUNT lane, halo Replica.

WHY THIS FILE EXISTS.  The protocol permits `tools/m_dark_packages.board_frame()`
for the frame, but that function imports `c_register` and `m_components`, and
NEITHER IS PRESENT IN THIS SANITISED WORKTREE -- they were removed with everything
else that could state the withheld figure.  Recovering them with `git checkout`
is forbidden and is the whole of what is left of the honour system, so the frame
is rebuilt here from the two permitted JSONs and the permitted image, and nothing
else.  Leif, on tools: "always manage its own tools and create any tools that
might be missing."

THE TRANSFORM, and it is verified rather than assumed:
  target(fcc6) FULL px  -> minus target.crop_origin  -> H_target_to_source_cropframe
  -> divide by w        -> times source.pre_average  -> source FULL px

CHECKED THREE WAYS, because a wrong frame puts the annulus somewhere else on the
board and every number after it is a correct computation on the wrong region --
which is the single failure this project has committed most often:
  1 the transform's own linear scale must reproduce the stored transferred scale
    (target px/mm x |H| x pre_average == source_px_per_mm_mean);
  2 the mapped outline's mean radius must equal the board's known half-diameter
    in source pixels;
  3 the mapped centre must land within a board-diameter of the recorded seed.
`selfcheck` runs all three and REFUSES rather than returning a frame it cannot
verify.  It also runs a DELIBERATE BREAK -- the transform with pre_average
dropped -- and requires the checks to go red.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FIT = os.path.join(HERE, "..", "metrology", "c_register-fit-boardscale.json")
RAW = os.path.join(HERE, "..", "metrology", "outline-raw-photo6.json")


def map_pts(fit, pts, pre_average=None):
    """FCC photo-6 full-image pixels -> O'Flynn source full-image pixels."""
    H = np.array(fit["H_target_to_source_cropframe"], float)
    o = np.array(fit["target"]["crop_origin"], float)
    k = fit["source"]["pre_average"] if pre_average is None else pre_average
    p = np.asarray(pts, float) - o
    q = np.c_[p, np.ones(len(p))] @ H.T
    return (q[:, :2] / q[:, 2:3]) * k


def poly_mask(shape, poly):
    im = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in poly], fill=255)
    return np.asarray(im) > 0


def background_mask(lum, outer, thr=190.0, dilate=3):
    """BRIGHT REGIONS CONNECTED TO THE OUTSIDE OF THE MAPPED OUTLINE.

    The mapped outline OVERSHOOTS at 2-4 o'clock (E07 records 0.277 mm fit residual
    sd on the same outline), so part of the annulus it defines is not board at all --
    it is the bright table.  That matters twice over: a paste site chosen for being
    QUIET lands there preferentially, because background is smooth, and a detection
    there is a detection of nothing.

    THIS MASK IS DELIBERATELY NOT USED TO DELETE ANYTHING.  A rim joint STRADDLES the
    board edge, so a bright joint can touch the background and be swallowed by the
    flood -- silently, which is E07 sec.29 (a mask that manufactures an absence) with
    the polarity that hurts most.  It is used ONLY where a false exclusion is free:
    choosing paste sites.  For the count, positions are LABELLED, never removed."""
    poly = poly_mask(lum.shape, outer)
    outside = ~ndimage.binary_dilation(poly, np.ones((3, 3)), iterations=dilate)
    bright = lum > thr
    lab, _ = ndimage.label(bright)
    seeds = np.unique(lab[bright & outside])
    seeds = seeds[seeds > 0]
    return np.isin(lab, seeds), poly


def board_frame(fit_path=FIT, raw_path=RAW, hole_level=190.0, pre_average=None):
    fit = json.load(open(fit_path))
    spath = os.path.join(ROOT, "images", "airtag", fit["source"]["path"])
    lum = np.asarray(Image.open(spath).convert("L")).astype(float)
    raw = json.load(open(raw_path))
    ocx, ocy = raw["outer_centre"]
    O = np.array(raw["outer_r_theta"], float)
    outer_fcc = np.c_[ocx + O[:, 1] * np.cos(np.radians(O[:, 0])),
                      ocy + O[:, 1] * np.sin(np.radians(O[:, 0]))]
    outer = map_pts(fit, outer_fcc, pre_average)
    origin = map_pts(fit, [[ocx, ocy]], pre_average)[0]
    bright = lum > hole_level
    lab, _ = ndimage.label(bright)
    kh = lab[int(round(origin[1])), int(round(origin[0]))]
    hole = ndimage.binary_fill_holes(lab == kh) if kh else np.zeros(lum.shape, bool)
    board = poly_mask(lum.shape, outer) & ~hole
    ppm = fit["transferred_scale"]["source_px_per_mm_mean"]
    return lum, board, outer, origin, ppm, spath, fit


def selfcheck(verbose=True, pre_average=None, quiet_fail=False):
    fit = json.load(open(FIT))
    H = np.array(fit["H_target_to_source_cropframe"], float)
    k = fit["source"]["pre_average"] if pre_average is None else pre_average
    lin = math.sqrt(abs(np.linalg.det(H[:2, :2])))
    ppm_pred = fit["target"]["px_per_mm"] * lin * k
    ppm_stored = fit["transferred_scale"]["source_px_per_mm_mean"]
    e1 = 100 * (ppm_pred - ppm_stored) / ppm_stored
    lum, board, outer, origin, ppm, spath, _ = board_frame(pre_average=pre_average)
    rr = np.hypot(outer[:, 0] - origin[0], outer[:, 1] - origin[1])
    dia_mm = 2 * rr.mean() / ppm
    seed = np.array(fit["source"]["seed_centre"], float)
    dcent = float(np.hypot(*(origin - seed)))
    ok1 = abs(e1) < 1.0
    ok2 = 24.0 < dia_mm < 28.0
    ok3 = dcent < 2 * rr.mean()
    if verbose:
        print(f"  1 scale  target {fit['target']['px_per_mm']:.4f} px/mm x |H| {lin:.5f} "
              f"x pre_average {k} = {ppm_pred:.4f}  vs stored {ppm_stored:.4f}  "
              f"({e1:+.3f} %)  {'PASS' if ok1 else 'FAIL'}")
        print(f"  2 size   mapped outline mean radius {rr.mean():.1f} px "
              f"({rr.min():.0f}-{rr.max():.0f}) -> diameter {dia_mm:.3f} mm  "
              f"{'PASS' if ok2 else 'FAIL'}")
        print(f"  3 place  mapped centre ({origin[0]:.1f},{origin[1]:.1f}) is {dcent:.0f} px "
              f"from the recorded seed ({seed[0]:.0f},{seed[1]:.0f})  "
              f"{'PASS' if ok3 else 'FAIL'}")
        print(f"    board mask {int(board.sum())} px; image {lum.shape[1]}x{lum.shape[0]}")
    return ok1 and ok2 and ok3, dict(ppm_pred=ppm_pred, ppm_stored=ppm_stored,
                                     scale_err_pct=e1, dia_mm=dia_mm,
                                     centre=[float(origin[0]), float(origin[1])],
                                     seed_dist_px=dcent, board_px=int(board.sum()))


if __name__ == "__main__":
    print("r_frame selfcheck -- the reconstructed frame, verified three ways\n")
    ok, d = selfcheck()
    print(f"\n  DELIBERATE BREAK: the same transform with pre_average dropped to 1.0")
    bad, _ = selfcheck(pre_average=1.0)
    print(f"  break {'went RED as required' if not bad else 'DID NOT FIRE -- the checks '
                                                            'cannot detect a wrong frame'}")
    print(f"\n  frame {'VERIFIED' if ok and not bad else 'REFUSED'}")
    sys.exit(0 if (ok and not bad) else 2)
