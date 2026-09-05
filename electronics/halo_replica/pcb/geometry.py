"""halo Replica — the board edge, from FITTED PRIMITIVES to KiCad shapes.

Reads `board/outline/outline-fit-oflynn.json` and `board/board.json` and
returns the outer edge and the routed centre pocket as ARCS AND STRAIGHT
SEGMENTS. Nothing here reads a per-degree silhouette, and nothing here
hard-codes a diameter.

---------------------------------------------------------------------------
WHY PRIMITIVES AND NOT THE SILHOUETTE
---------------------------------------------------------------------------
L5b's fit file says it in its own header: "FITTED MANUFACTURABLE PRIMITIVES,
not samples. The raw per-degree profile lives in
metrology/outline-raw-oflynn-front.json and is NEVER merged into this file."
A silhouette carries the edge detector's noise, cannot be dimensioned or
toleranced, and a router asked to follow 1194 rays cuts 1194 facets. So:

  OUTER  a circle of diameter `outer_diameter_mm` clipped by 4 straight
         chords. Emitted as TRUE ARCS (KiCad SHAPE_T_ARC) and TRUE
         SEGMENTS. The arc endpoints are solved exactly -- circle-line
         quadratic, or a 2x2 for line-line -- never sampled.

  POCKET a superellipse (n = 2.449, NOT a circle and NOT a rounded square)
         with 7 measured straight facets replacing it over their measured
         arcs. KiCad has no superellipse primitive and neither does any CAM
         format, so the superellipse runs are tessellated at a stated step
         and the facets are single straight segments. The tessellation
         chord error is COMPUTED and returned, not assumed.

---------------------------------------------------------------------------
THE THING THAT IS NOT MEASURED, AND IS DRAWN ANYWAY
---------------------------------------------------------------------------
board.json, verbatim: "Each facet ends in a RADIAL STEP where its measured
arc ends. A routed pocket really does have side walls, so a step is the
right kind of geometry - but the arc ends are where the boundary crosses
0.30 mm from the superellipse, NOT where the wall is. The wall positions are
NOT MEASURED."

Those steps are drawn, because a pocket without them is not the shape that
was fitted. `step_walls()` returns them separately from everything else so
the board can put them on a documentation layer as well as Edge.Cuts, and
so this refusal has somewhere to live in the fabrication output.

---------------------------------------------------------------------------
THE FRAME
---------------------------------------------------------------------------
Board centre in `images/airtag/oflynn-backside-fullres.jpeg`, origin_px
(1522.56, 1738.80), 106.313 px/mm, +x right and +y DOWN, theta from +x
through +y. Every millimetre this module returns is in THAT frame. The flip
to KiCad's own handedness happens once, in board.py, and never here.

SCALING. `outer_diameter_mm` in board.json is the DRAWN value, not a settled
diameter -- the OD is a BOUND, 24.95 to 26.34 mm, and if it moves it moves
DOWN. Every primitive returned by this module is multiplied by
`outer_diameter_mm / fitted_circle_diameter_mm`, so changing that one number
in board.json rescales the outline, the pocket and (in board.py) every
component position together. No diameter is hard-coded anywhere.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
FIT = os.path.join(REPLICA, "board", "outline", "outline-fit-oflynn.json")
BOARDJSON = os.path.join(REPLICA, "board", "board.json")

POCKET_STEP_DEG = 0.5      # superellipse tessellation. The chord error this
                           # produces is COMPUTED in pocket() and returned.


def load():
    return json.load(open(FIT)), json.load(open(BOARDJSON))


def scale_factor():
    """drawn OD / fitted OD. ONE number, and it is the only scale in here."""
    fit, bj = load()
    drawn = float(bj["parameters"]["outer_diameter_mm"]["value"])
    fitted = float(fit["outer"]["circle_diameter_mm"])
    return drawn / fitted, drawn, fitted


def _u(deg):
    r = math.radians(deg)
    return math.cos(r), math.sin(r)


# ---------------------------------------------------------------------------
# OUTER: a circle clipped by straight chords. Convex, origin inside.
# ---------------------------------------------------------------------------
def _outer_model():
    fit, _ = load()
    o = fit["outer"]
    k, drawn, fitted = scale_factor()
    cx, cy = [v * k for v in o["circle_centre_mm"]]
    R = fitted / 2.0 * k
    chords = []
    for c in o["chords"]:
        if not c.get("admitted", True):
            continue
        chords.append({"n": (c["nx"], c["ny"]), "d": c["offset_mm"] * k,
                       "arc": c["arc_deg"]})
    return (cx, cy), R, chords


def _r_circle(theta, c, R):
    """Distance from the FRAME ORIGIN to the circle along theta."""
    ux, uy = _u(theta)
    cx, cy = c
    b = cx * ux + cy * uy
    disc = b * b - (cx * cx + cy * cy - R * R)
    if disc < 0:
        return None
    return b + math.sqrt(disc)


def _r_line(theta, n, d):
    ux, uy = _u(theta)
    den = n[0] * ux + n[1] * uy
    if den <= 1e-9:
        return None
    return d / den


def _active(theta, c, R, chords):
    """Which primitive is the boundary at this bearing. min wins (convex)."""
    best, who = _r_circle(theta, c, R), -1
    for i, ch in enumerate(chords):
        r = _r_line(theta, ch["n"], ch["d"])
        if r is not None and r < best:
            best, who = r, i
    return who, best


def _circle_line_point(theta_hint, c, R, n, d):
    """EXACT circle-line intersection, the root nearest theta_hint."""
    cx, cy = c
    nx, ny = n
    # foot of the perpendicular from the circle centre onto the line
    t = d - (cx * nx + cy * ny)
    h2 = R * R - t * t
    if h2 < 0:
        return None
    h = math.sqrt(h2)
    tx, ty = -ny, nx
    px, py = cx + t * nx, cy + t * ny
    cands = [(px + h * tx, py + h * ty), (px - h * tx, py - h * ty)]
    hx, hy = _u(theta_hint)
    return max(cands, key=lambda p: (p[0] * hx + p[1] * hy) /
               (math.hypot(p[0], p[1]) or 1.0))


def _line_line_point(n1, d1, n2, d2):
    det = n1[0] * n2[1] - n1[1] * n2[0]
    if abs(det) < 1e-12:
        return None
    return ((d1 * n2[1] - n1[1] * d2) / det,
            (n1[0] * d2 - d1 * n2[0]) / det)


def outer(step_deg=0.02):
    """The outer edge as an ordered list of primitives.

    Returns (shapes, meta). Each shape is
        ("arc", (x0,y0), (xm,ym), (x1,y1), centre, R)   or
        ("seg", (x0,y0), (x1,y1), chord_index)
    in the measurement frame, mm, +y DOWN.
    """
    c, R, chords = _outer_model()
    k, drawn, fitted = scale_factor()

    n = int(round(360.0 / step_deg))
    who = [_active(i * step_deg, c, R, chords)[0] for i in range(n)]
    if len(set(who)) == 1:
        raise ValueError("no chord is ever the boundary — the clip did "
                         "nothing and this would silently be a plain disc, "
                         "which is exactly the board that was rejected")

    # run boundaries
    trans = [i for i in range(n) if who[i] != who[i - 1]]
    shapes = []
    for j, i0 in enumerate(trans):
        i1 = trans[(j + 1) % len(trans)]
        a0 = i0 * step_deg
        a1 = i1 * step_deg
        span = (a1 - a0) % 360.0
        prim = who[i0]
        prev = who[i0 - 1]
        nxt = who[i1]
        p0 = _corner(a0, prev, prim, c, R, chords)
        p1 = _corner(a1, prim, nxt, c, R, chords)
        if prim == -1:
            am = a0 + span / 2.0
            rm = _r_circle(am, c, R)
            ux, uy = _u(am)
            shapes.append(("arc", p0, (rm * ux, rm * uy), p1, c, R))
        else:
            shapes.append(("seg", p0, p1, prim))

    meta = {
        "drawn_outer_diameter_mm": drawn,
        "fitted_circle_diameter_mm": fitted,
        "scale_applied": k,
        "circle_centre_mm": list(c),
        "chords_admitted": len(chords),
        "chords_that_are_the_boundary": sorted(set(w for w in who if w >= 0)),
        "arcs": sum(1 for s in shapes if s[0] == "arc"),
        "segments": sum(1 for s in shapes if s[0] == "seg"),
    }
    return shapes, meta


def _corner(theta, a, b, c, R, chords):
    """The EXACT point where primitive a hands over to primitive b."""
    if a == -1 and b == -1:
        r = _r_circle(theta, c, R)
        ux, uy = _u(theta)
        return (r * ux, r * uy)
    if a == -1:
        return _circle_line_point(theta, c, R, chords[b]["n"], chords[b]["d"])
    if b == -1:
        return _circle_line_point(theta, c, R, chords[a]["n"], chords[a]["d"])
    return _line_line_point(chords[a]["n"], chords[a]["d"],
                            chords[b]["n"], chords[b]["d"])


# ---------------------------------------------------------------------------
# POCKET: a superellipse with 7 measured straight facets cut into it.
# ---------------------------------------------------------------------------
def _pocket_model():
    fit, _ = load()
    inn = fit["inner"]
    k, _, _ = scale_factor()
    ox, oy = fit["frame"]["origin_px"]
    ppm = fit["scale"]["px_per_mm"]
    cx = (inn["centre_px"][0] - ox) / ppm * k
    cy = (inn["centre_px"][1] - oy) / ppm * k
    a = inn["two_a_mm"] / 2.0 * k
    b = inn["two_b_mm"] / 2.0 * k
    return (cx, cy), a, b, float(inn["n"]), float(inn["phi_deg"]), \
        [dict(f) for f in inn["facets"]], k


def _r_superellipse(theta, c, a, b, n, phi):
    """Bisection on r. The frame origin is inside, so there is one root."""
    ux, uy = _u(theta)
    cp, sp = math.cos(math.radians(phi)), math.sin(math.radians(phi))

    def f(r):
        dx, dy = r * ux - c[0], r * uy - c[1]
        qx = dx * cp + dy * sp
        qy = -dx * sp + dy * cp
        return (abs(qx / a) ** n + abs(qy / b) ** n) - 1.0

    lo, hi = 0.0, max(a, b) * 3.0 + math.hypot(*c)
    if f(lo) > 0:
        raise ValueError("the frame origin is OUTSIDE the fitted pocket — "
                         "the ray construction this module rests on is void")
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2.0


def _in_arc(theta, a0, a1):
    return ((theta - a0) % 360.0) <= ((a1 - a0) % 360.0)


def pocket(step_deg=POCKET_STEP_DEG):
    """The routed centre pocket.

    Returns (segments, walls, meta). `segments` is the pocket boundary as an
    ordered list of ((x0,y0),(x1,y1)) in the measurement frame. `walls` is
    the subset of those that are RADIAL STEPS at a facet end — geometry
    whose position is NOT MEASURED (see the module docstring) — so the caller
    can mark them.
    """
    c, a, b, n, phi, facets, k = _pocket_model()
    for f in facets:
        f["offset_mm"] = f["offset_mm"] * k

    def facet_at(theta):
        for i, f in enumerate(facets):
            if _in_arc(theta, f["arc_deg"][0], f["arc_deg"][1]):
                return i
        return -1

    def r_at(theta, which):
        if which < 0:
            return _r_superellipse(theta, c, a, b, n, phi)
        f = facets[which]
        nx, ny = _u(f["normal_deg"])
        r = _r_line(theta, (nx, ny), f["offset_mm"])
        if r is None:
            return _r_superellipse(theta, c, a, b, n, phi)
        return r

    steps = int(round(360.0 / step_deg))
    pts, owner = [], []
    for i in range(steps):
        th = i * step_deg
        w = facet_at(th)
        r = r_at(th, w)
        ux, uy = _u(th)
        pts.append((r * ux, r * uy))
        owner.append(w)

    segs, walls = [], []
    for i in range(steps):
        j = (i + 1) % steps
        if owner[i] == owner[j]:
            segs.append((pts[i], pts[j]))
        else:
            # a radial step: close it at the shared bearing, both radii
            th = j * step_deg
            ux, uy = _u(th)
            ra = r_at(th, owner[i])
            rb = r_at(th, owner[j])
            pa = (ra * ux, ra * uy)
            pb = (rb * ux, rb * uy)
            segs.append((pts[i], pa))
            segs.append((pa, pb))
            segs.append((pb, pts[j]))
            walls.append((pa, pb))

    # CHORD ERROR OF THE TESSELLATION, computed rather than assumed.
    worst = 0.0
    for i in range(steps):
        w = owner[i]
        if w >= 0:
            continue
        th = (i + 0.5) * step_deg
        if facet_at(th) >= 0:
            continue
        rm = _r_superellipse(th, c, a, b, n, phi)
        ux, uy = _u(th)
        p = (rm * ux, rm * uy)
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % steps]
        num = abs((x1 - x0) * (y0 - p[1]) - (x0 - p[0]) * (y1 - y0))
        den = math.hypot(x1 - x0, y1 - y0) or 1.0
        worst = max(worst, num / den)

    radii = [math.hypot(*p) for p in pts]
    meta = {
        "primitive": "superellipse n=%.4f + %d measured straight facets"
                     % (n, len(facets)),
        "n_exponent": n,
        "two_a_mm": a * 2, "two_b_mm": b * 2, "phi_deg": phi,
        "centre_mm": list(c),
        "facets": len(facets),
        "radial_step_walls": len(walls),
        "walls_are_measured": False,
        "walls_note": "A facet's arc ends where the boundary crosses 0.30 mm "
                      "from the superellipse, NOT where the wall is. The "
                      "wall POSITIONS ARE NOT MEASURED (board.json).",
        "tessellation_step_deg": step_deg,
        "tessellation_max_chord_error_mm": round(worst, 6),
        "no_diameter_published": "This lane publishes NO centre-hole "
                                 "diameter. Three superellipse fits disagree "
                                 "on the exponent and in different "
                                 "directions (board.json).",
        "min_radius_mm": round(min(radii), 4),
        "max_radius_mm": round(max(radii), 4),
        "segments": len(segs),
    }
    return segs, walls, meta


if __name__ == "__main__":
    sh, m = outer()
    print("OUTER  ", json.dumps(m, indent=1))
    sg, wl, pm = pocket()
    print("POCKET ", json.dumps(pm, indent=1))
