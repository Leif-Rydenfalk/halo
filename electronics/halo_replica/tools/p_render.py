#!/usr/bin/env python3
"""p_render.py -- draw the halo Replica main board from board/board.json.

Lane L5 (BOARD BUILD).  Exit code IS the verdict: 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

The board is PARAMETERISED: the outline is a NORMALISED profile r(theta)/r_mean read
from a photograph, multiplied by one scale parameter.  No diameter is hard-coded here.

CONTROLS
  R1 non-blank   -- the finished PNG is read back and must not be blank or near-blank.
                    A cached blank would be served as a hit forever.
  R2 shape       -- the drawn annulus must actually be an annulus: the pixel at the
                    centre must be BACKGROUND and the pixel at 0.8 x r_outer must be
                    BOARD.  A renderer that silently drew a filled disc passes every
                    "is the file non-empty" test.
  R3 scale       -- the drawn outer extent in px, divided by px_per_mm, must equal the
                    stated outer diameter to within 1%.  This is the check that would
                    have caught a renderer whose picture is right but whose scale is
                    wrong, which is the only kind of error a side-by-side cannot see.
  R4 provisional -- every PROVISIONAL parameter is stamped ON THE PICTURE.  A render
                    that does not carry its own caveats will be screenshotted without
                    them.
"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PASS, FAIL, CANNOT = 0, 1, 2
HERE = os.path.dirname(os.path.abspath(__file__))
BOARD_DIR = os.path.join(os.path.dirname(HERE), "board")

MASK = (26, 26, 28)        # Apple's black soldermask
MASK_EDGE = (70, 70, 74)
BG = (246, 245, 242)       # the FCC photo's paper background
PAD = (196, 168, 96)       # ENIG-ish
INK = (30, 30, 32)
PROV = (208, 92, 24)


def say(*a):
    print(*a, file=sys.stderr)


def font(sz):
    for p in ("/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def resample(rows, n=1440, smooth=5):
    """Put a sparse r(theta) list onto a uniform grid, interpolating ACROSS the rays
    p_outline.py discarded, and report which arcs are interpolated so the picture can
    say so. Then an angular median-of-`smooth` to take out single-pixel jpeg noise --
    and the maximum displacement it caused is REPORTED, because a smoother that quietly
    erased the notch at top centre would make the render look better and be wrong."""
    grid = np.arange(n) * 360.0 / n
    t = np.array([r[0] for r in rows], float)
    v = np.array([r[1] for r in rows], float)
    o = np.argsort(t); t, v = t[o], v[o]
    # wrap for periodic interpolation
    tt = np.concatenate([t - 360, t, t + 360])
    vv = np.concatenate([v, v, v])
    r = np.interp(grid, tt, vv)
    # which grid angles are further than one source step from any real measurement
    step = 360.0 / n
    d = np.min(np.abs((grid[:, None] - tt[None, :] + 180) % 360 - 180), axis=1)
    interpolated = d > 1.5 * step
    if smooth > 1:
        pad = np.concatenate([r[-smooth:], r, r[:smooth]])
        sm = np.array([np.median(pad[i:i + 2 * smooth + 1]) for i in range(n)])
        moved = float(np.max(np.abs(sm - r)))
        say(f"  angular median smoother (+/-{smooth} bins): max displacement "
            f"{moved:.4f} mm")
        r = sm
    return grid, r, interpolated


def load_profile(board):
    """Return closed polygons in mm, centred on the board centroid, scaled so the mean
    outer radius matches the stated diameter/2. ONE scale parameter; the SHAPE comes
    from the photograph."""
    src = os.path.join(BOARD_DIR, board["outline"]["profile_source"])
    with open(src) as f:
        o = json.load(f)
    tgt_r = board["parameters"]["outer_diameter_mm"]["value"] / 2.0
    om = o["outer"]["stats_mm"]["mean"]
    k = tgt_r / om                      # THE one scale parameter
    say(f"profile source  {os.path.relpath(src)}")
    say(f"normalised: mean outer r in source {om:.4f} mm -> target {tgt_r:.4f} mm, k={k:.6f}")

    say("outer profile:")
    to, ro, io_ = resample(o["outer"]["r_theta_deg_mm"])
    say(f"  {io_.sum()}/{len(io_)} angles are INTERPOLATED across discarded rays "
        f"({io_.sum()*360/len(io_):.1f} deg of arc) -- drawn, and marked on the picture")
    say("inner profile:")
    ti, ri, ii_ = resample(o["inner"]["r_theta_deg_mm"])
    say(f"  {ii_.sum()}/{len(ii_)} angles interpolated")

    def poly(t, r):
        return [(k * rr * math.cos(math.radians(a)), -k * rr * math.sin(math.radians(a)))
                for a, rr in zip(t, r)]

    return poly(to, ro), poly(ti, ri), o, k, io_, ii_


def draw(board, px_per_mm, margin_mm, with_caption):
    outer, inner, prof, k, interp_o, interp_i = load_profile(board)
    R = max(math.hypot(x, y) for x, y in outer)
    half = R + margin_mm
    W = H = int(round(2 * half * px_per_mm))
    cap = 150 if with_caption else 0
    im = Image.new("RGB", (W, H + cap), BG)
    d = ImageDraw.Draw(im, "RGBA")

    def P(pt):
        return (half + pt[0]) * px_per_mm, (half + pt[1]) * px_per_mm

    # soft drop shadow, so the render reads like the photograph it sits beside
    d.polygon([(P(p)[0] + 4, P(p)[1] + 6) for p in outer], fill=(180, 178, 172, 110))
    d.polygon([P(p) for p in outer], fill=MASK, outline=MASK_EDGE)
    d.polygon([P(p) for p in inner], fill=BG)
    d.line([P(p) for p in inner] + [P(inner[0])], fill=MASK_EDGE, width=2)

    # R4: the arcs that were INTERPOLATED across discarded rays are drawn in the
    # provisional colour. Where the picture is a guess, the picture says so.
    n = len(outer)
    for i in range(n):
        if interp_o[i] and interp_o[(i + 1) % n]:
            d.line([P(outer[i]), P(outer[(i + 1) % n])], fill=PROV + (255,), width=5)

    if with_caption:
        f1, f2 = font(26), font(19)
        p = board["parameters"]
        d.text((14, H + 8), "halo Replica MLB - FRONT (component side)", font=f1, fill=INK)
        lines = [
            (f"outer dia {p['outer_diameter_mm']['value']:.3f} mm", "PROVISIONAL - IN DISPUTE"),
            (f"thickness {p['thickness_mm']['value']:.2f} mm as-drawn",
             "below both fab floors - see board.json"),
            (f"{p['layer_count']['value']} layers", "STATED REPLICA CHOICE, not Apple's fact"),
            ("centre hole: rounded square + notch", f"roundness {p['centre_hole']['measured_roundness_rmax_over_rmin']:.3f}; NO diameter published"),
        ]
        y = H + 44
        for a, b in lines:
            d.text((14, y), a, font=f2, fill=INK)
            d.text((14 + 300, y), b, font=f2, fill=PROV)
            y += 25
    return im, R, prof, k


def controls(im, R, px_per_mm, margin_mm, want_dia):
    ok = True
    a = np.asarray(im.convert("L")).astype(float)
    # R1 non-blank
    sd = float(a.std())
    dark = float((a < 120).mean())
    say(f"R1 non-blank: pixel sd {sd:.2f}, dark fraction {dark:.4f}")
    if sd < 5 or dark < 0.02:
        say("R1 FIRED: the render is blank or near-blank.")
        ok = False
    # R2 annulus
    half = R + margin_mm
    cx = cy = half * px_per_mm
    centre = a[int(cy), int(cx)]
    ring = a[int(cy), int(cx + 0.8 * R * px_per_mm)]
    say(f"R2 annulus: centre luma {centre:.0f} (want light/background), "
        f"0.8R luma {ring:.0f} (want dark/board)")
    if not (centre > 150 and ring < 120):
        say("R2 FIRED: this is not an annulus. A filled disc passes every "
            "'file is non-empty' test and fails here.")
        ok = False
    # R3 scale -- measured the SAME WAY the parameter is defined: 2 x mean radius
    # over 1440 rays of the drawn silhouette. Comparing bounding-box extent would be
    # comparing a max to a mean, which for a non-circular outline is a different number.
    board_h = int(round(2 * half * px_per_mm))
    m = a[:board_h] < 120
    ys, xs = np.nonzero(m)
    dcx, dcy = xs.mean(), ys.mean()
    th = np.deg2rad(np.arange(1440) * 0.25)
    rr = np.arange(1.0, 0.75 * board_h, 0.25)
    RR, TT = np.meshgrid(rr, th)
    X = np.rint(dcx + RR * np.cos(TT)).astype(int)
    Y = np.rint(dcy - RR * np.sin(TT)).astype(int)
    okm = (X >= 0) & (Y >= 0) & (X < m.shape[1]) & (Y < m.shape[0])
    hit = np.zeros_like(RR, dtype=bool)
    hit[okm] = m[Y[okm], X[okm]]
    rad = np.array([rr[np.nonzero(h)[0][-1]] if h.any() else np.nan for h in hit])
    drawn_dia = 2 * np.nanmean(rad) / px_per_mm
    err = abs(drawn_dia - want_dia) / want_dia
    say(f"R3 scale: drawn 2 x mean radius {drawn_dia:.3f} mm vs stated "
        f"{want_dia:.3f} mm -> {err*100:.2f}%")
    if err > 0.01:
        say("R3 FIRED: the picture is drawn at the wrong scale. A side-by-side "
            "cannot see this error; only this check can.")
        ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", default=os.path.join(BOARD_DIR, "board.json"))
    ap.add_argument("--px-per-mm", type=float, default=60.0)
    ap.add_argument("--margin-mm", type=float, default=1.2)
    ap.add_argument("--no-caption", action="store_true")
    ap.add_argument("--out", default=os.path.join(BOARD_DIR, "out", "board-front.png"))
    ap.add_argument("--break-scale", type=float, default=None,
                    help="deliberately multiply the drawn scale by this, to watch R3 fire")
    a = ap.parse_args()
    with open(a.board) as f:
        board = json.load(f)
    say("INPUT")
    say(f"  board.json    {a.board}")
    say(f"  px_per_mm     {a.px_per_mm}")
    say(f"  side          {board['side_convention']}")
    say("")
    ppm = a.px_per_mm * (a.break_scale or 1.0)
    im, R, prof, k = draw(board, ppm, a.margin_mm, not a.no_caption)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    im.save(a.out)
    say(f"wrote {a.out}  {im.size[0]}x{im.size[1]}")
    back = Image.open(a.out)          # read the picture BACK, never trust the buffer
    # NOTE the asymmetry, and it is deliberate: the picture is DRAWN at ppm, the
    # control measures it at the px_per_mm the caller ASKED FOR. --break-scale makes
    # those differ, which is the only way this check can be seen to go red. Feeding
    # the same broken number to both sides would cancel and the check would pass a
    # broken build -- the exact failure L4 hit with its layer-count test.
    ok = controls(back, R, a.px_per_mm, a.margin_mm,
                  board["parameters"]["outer_diameter_mm"]["value"])
    code = PASS if ok else FAIL
    say({0: "PASS", 1: "FAIL", 2: "CANNOT DETERMINE"}[code])
    sys.exit(code)


if __name__ == "__main__":
    main()
