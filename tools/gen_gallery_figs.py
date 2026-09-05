#!/usr/bin/env python3
"""Gallery figures — lane G1 (visuals).

    python3 tools/gen_gallery_figs.py

Three drawings that no render can make, each built from numbers already
measured somewhere else in this repo and cited back to it:

  fig-stack.png            the 7.980 mm stack, to scale, from
                           out/render/stack.json (bounding boxes read off
                           the finished solids by tools/gen_gallery_renders.py)
  fig-halo-vs-airtag.png   halo against the AirTag: outline to scale, then
                           mass, antenna gain, cost and the one functional
                           gap, each with its source and its verdict
  fig-board-side-by-side.png   halo rev A against Apple's own board photo,
                           both scaled so 26 mm is the same width on screen

Nothing here invents a number. Where a figure would have to guess, it draws
CANNOT DETERMINE in the panel instead — see the antenna-gain row.
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                              # noqa: E402
from matplotlib.patches import Rectangle, FancyArrowPatch     # noqa: E402
import numpy as np                                            # noqa: E402
from PIL import Image                                         # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "gallery")
os.makedirs(OUT, exist_ok=True)

INK = "#16181d"
DIM = "#5c6370"
LINE = "#c8ced6"
PASS_C = "#0a7d33"
WARN_C = "#a86500"
CD_C = "#7a4fb5"
HALO_C = "#1f6fb2"
APPLE_C = "#8a8f98"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "DejaVu Sans"],
    "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": DIM, "ytick.color": DIM,
    "figure.facecolor": "white", "savefig.facecolor": "white",
})


def out(name):
    return os.path.join(OUT, name)


# ---------------------------------------------------------------- fig 1
def fig_stack():
    """The stack, to scale. One horizontal band per part at its MEASURED z,
    with the roll-call in a column beside it so nothing overlaps."""
    doc = json.load(open(os.path.join(ROOT, "out", "render", "stack.json")))
    parts = doc["parts"]
    # The three contacts occupy the same z band; draw them once.
    keep, seen = [], False
    for p in parts:
        if p["key"] in ("cp1", "cp2", "cn1"):
            if seen:
                continue
            seen = True
            p = dict(p, label="three sprung contacts", dia_mm=9.6059)
        keep.append(p)
    keep.sort(key=lambda p: -(p["z0"] + p["z1"]))

    colours = {"door": "#9aa2ad", "seal": "#c0504d", "cell": "#4a7ebb",
               "cn1": "#e08b2a", "carrier": "#c9a227", "pcb": "#3d8b4a",
               "piezo": "#7b5ea7", "shell": "#8d949e"}
    total = doc["total_z"]

    fig = plt.figure(figsize=(13.2, 5.6), dpi=150)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1.0], wspace=0.04)
    ax = fig.add_subplot(gs[0, 0])
    for p in keep:
        z0, z1, r = p["z0"], p["z1"], p["dia_mm"] / 2.0
        ax.add_patch(Rectangle((-r, z0), 2 * r, z1 - z0,
                               facecolor=colours.get(p["key"], "#999"),
                               edgecolor=INK, linewidth=0.7, alpha=0.88))
    ax.annotate("", xy=(-19.4, 0), xytext=(-19.4, total),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.3))
    ax.text(-20.2, total / 2.0, "%.3f mm" % total, rotation=90,
            va="center", ha="right", fontsize=12, fontweight="bold")
    for z in (0.0, total):
        ax.plot([-18.8, -16.2], [z, z], color=INK, lw=0.9)
    ax.annotate("", xy=(-15.937, -1.5), xytext=(15.937, -1.5),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.0))
    ax.text(0, -2.3, "%.3f mm" % doc["max_dia"], va="top", ha="center",
            fontsize=10, fontweight="bold")
    ax.set_xlim(-22, 18)
    ax.set_ylim(-3.4, total + 1.0)
    ax.set_aspect("equal")
    ax.axis("off")

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis("off"); ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
    ax2.text(0.0, 1.0, "part", fontsize=8, color=DIM, fontweight="bold",
             va="top")
    ax2.text(0.55, 1.0, "outer Ø", fontsize=8, color=DIM,
             fontweight="bold", va="top")
    ax2.text(0.74, 1.0, "z from – to", fontsize=8, color=DIM,
             fontweight="bold", va="top")
    y = 0.945
    for p in keep:
        ax2.add_patch(Rectangle((0.0, y - 0.030), 0.022, 0.024,
                                facecolor=colours.get(p["key"], "#999"),
                                edgecolor=INK, lw=0.5, alpha=0.88,
                                transform=ax2.transAxes, clip_on=False))
        ax2.text(0.035, y, p["label"], fontsize=9.4, va="top", color=INK)
        ax2.text(0.55, y, "%.2f" % p["dia_mm"], fontsize=9.4, va="top",
                 color=INK, family="monospace")
        ax2.text(0.74, y, "%.3f – %.3f" % (p["z0"], p["z1"]), fontsize=9.4,
                 va="top", color=INK, family="monospace")
        y -= 0.088
    ax2.text(0.0, y - 0.02,
             "Every row is a bounding box read off the finished solid.\n"
             "Bands overlap because the parts interlock: the carrier's\n"
             "legs run down past the cell, and the door closes over them.",
             fontsize=8, color=DIM, va="top", linespacing=1.5)

    fig.suptitle("halo puck — the stack, to scale on both axes: "
                 "%.3f mm tall, %.3f mm across (out/render/stack.json)"
                 % (total, doc["max_dia"]),
                 fontsize=12.5, x=0.008, ha="left", y=0.99,
                 fontweight="bold")
    fig.savefig(out("fig-stack.png"), bbox_inches="tight")
    plt.close(fig)
    return "fig-stack.png"


# ---------------------------------------------------------------- fig 2
# Every row states where the number came from. A row this repo cannot
# settle is drawn as CANNOT DETERMINE, never as a favourable estimate.
ROWS = [
    dict(k="diameter", label="maximum outer diameter",
         halo="31.874 mm", apple="31.87 mm", unit="",
         v="PASS", note="halo's profile is Apple's own drawing, so the match "
                        "is the point, not a coincidence",
         src="out/mech/verdicts.json 'envelope' · SPEC.md §4"),
    dict(k="height", label="overall height",
         halo="7.980 mm", apple="7.98 mm", unit="",
         v="PASS", note="measured on the assembled solid, both lanes agree",
         src="out/render/stack.json · out/mech/verdicts.json"),
    dict(k="mass", label="mass",
         halo="7.8 g", apple="11 g", unit="",
         v="PARTIAL", note="halo's 7.8 g is the ENCLOSURE only — no board "
                           "components, no copper. Not yet like-for-like",
         src="docs/MECHANICAL.md §10 · docs/TEST-PLAN.md FU-06"),
    dict(k="gain", label="BLE antenna realized gain",
         halo="CANNOT DETERMINE", apple="-3.2 dBi", unit="",
         v="CANNOT DETERMINE",
         note="the SHIPPED board's own solve (halo-rev-a-2g4) did not "
              "converge and reports no gain. A Ø30x1.0 mm study geometry "
              "(halo-round-rim-ifa) reaches +0.521 dBi and PASSES — but it "
              "is not this board",
         src="ce-rf/out/halo-rev-a-2g4/verdict.json (FAIL) · "
             "ce-rf/out/halo-round-rim-ifa/verdict.json (PASS)"),
    dict(k="cost", label="cost per unit at 10 000",
         halo="$6.75", apple="$29 retail", unit="",
         v="PARTIAL", note="halo's figure is BOM + board + assembly + "
                           "enclosure. Apple's is a shelf price, which "
                           "contains margin, network and packaging",
         src="spec/bom-resolved.json cost.model · GOAL.md"),
    dict(k="uwb", label="precision finding",
         halo="not reproducible", apple="Apple U1", unit="",
         v="FAIL", note="the one true hard wall: the U1 was never sold, and "
                        "the badge needs MFi",
         src="SPEC.md F9 · DECISIONS.md D1, D5"),
]
VC = {"PASS": PASS_C, "PARTIAL": WARN_C, "CANNOT DETERMINE": CD_C,
      "FAIL": "#a11"}


def _profile(halo_d, halo_h):
    """A side elevation of the puck, drawn from its own measured envelope:
    a spherical-cap crown on a short skirt. Silhouette only — the real
    geometry is in the renders, this is the ruler beside them."""
    d, h = halo_d, halo_h
    r = d / 2.0
    xs = np.linspace(-r, r, 400)
    # crown: a cap that meets the max diameter at z = 4.34 (Apple's drawing)
    z_max_d = 4.339
    cap_h = h - z_max_d
    zs = z_max_d + cap_h * np.sqrt(np.clip(1.0 - (xs / r) ** 2, 0, 1)) ** 0.62
    return xs, zs, z_max_d


def fig_compare():
    fig = plt.figure(figsize=(12.6, 11.4), dpi=150)
    gs = fig.add_gridspec(2, 2, height_ratios=[0.80, 1.45],
                          hspace=0.06, wspace=0.16)

    # --- to-scale silhouettes, side by side, same axes
    ax = fig.add_subplot(gs[0, :])
    for dx, (d, h, colour, name) in enumerate(
            [(31.874, 7.980, HALO_C, "halo  Ø31.874 x 7.980 mm (measured)"),
             (31.87, 7.98, APPLE_C, "AirTag  Ø31.87 x 7.98 mm (drawing)")]):
        off = dx * 40.0
        xs, zs, zmax = _profile(d, h)
        ax.fill_between(xs + off, 0, zs, facecolor=colour, alpha=0.30,
                        edgecolor=colour, linewidth=1.6)
        ax.plot([-d / 2 + off, d / 2 + off], [zmax, zmax], ls=":",
                color=colour, lw=1.0)
        ax.annotate("", xy=(-d / 2 - 2.5 + off, 0),
                    xytext=(-d / 2 - 2.5 + off, h),
                    arrowprops=dict(arrowstyle="<->", color=colour, lw=1.0))
        ax.text(-d / 2 - 3.4 + off, h / 2, "%.3f" % h, rotation=90,
                va="center", ha="right", fontsize=8, color=colour)
        ax.annotate("", xy=(-d / 2 + off, -1.6), xytext=(d / 2 + off, -1.6),
                    arrowprops=dict(arrowstyle="<->", color=colour, lw=1.0))
        ax.text(off, -2.5, ("%.3f" % d).rstrip("0").rstrip("."), va="top", ha="center", fontsize=8,
                color=colour)
        ax.text(off, h + 1.5, name, ha="center", fontsize=9.5,
                color=colour, fontweight="bold")
    ax.set_xlim(-24, 64)
    ax.set_ylim(-4.6, 10.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Same envelope, drawn to the same scale — halo's profile IS "
                 "Apple's dimensional drawing (research/fetched/"
                 "G-airtag-profile-from-dxf.md)",
                 fontsize=10.5, loc="left", color=DIM)

    # --- the table of claims. Row heights are computed from the text each
    # row actually carries: a fixed pitch collided the four-line antenna
    # note into the row below it, and a collision is a wrong picture.
    ax2 = fig.add_subplot(gs[1, :])
    ax2.axis("off")
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    cols = [0.005, 0.235, 0.395, 0.555, 0.70]
    hdr = ["", "halo", "AirTag", "verdict", "where the number comes from, "
           "and what it does not say"]
    notes = [_wrap(r["note"], 58) for r in ROWS]
    srcs = [_wrap(r["src"], 74) for r in ROWS]
    lines = [notes[i].count("\n") + 1 + srcs[i].count("\n") + 1 + 1
             for i in range(len(ROWS))]
    top, bot = 0.955, 0.01
    unit = (top - bot - 0.045) / sum(lines)      # 0.045 for the header
    y = top
    for x, t in zip(cols, hdr):
        ax2.text(x, y, t, fontsize=8.4, color=DIM, fontweight="bold",
                 va="top", transform=ax2.transAxes)
    y -= 0.030
    ax2.plot([0, 1], [y, y], color=LINE, lw=0.9, transform=ax2.transAxes,
             clip_on=False)
    y -= 0.015
    for i, r in enumerate(ROWS):
        c = VC[r["v"]]
        nl = notes[i].count("\n") + 1
        ax2.text(cols[0], y, r["label"], fontsize=9.2, va="top",
                 color=INK, fontweight="bold", transform=ax2.transAxes)
        ax2.text(cols[1], y, r["halo"], fontsize=9.2, va="top",
                 color=CD_C if r["v"] == "CANNOT DETERMINE" else HALO_C,
                 fontweight="bold", transform=ax2.transAxes)
        ax2.text(cols[2], y, r["apple"], fontsize=9.2, va="top",
                 color=APPLE_C, transform=ax2.transAxes)
        ax2.text(cols[3], y, r["v"], fontsize=7.6, va="top", color=c,
                 fontweight="bold", transform=ax2.transAxes)
        ax2.text(cols[4], y, notes[i], fontsize=7.8, va="top", color=INK,
                 transform=ax2.transAxes, linespacing=1.45)
        ax2.text(cols[4], y - unit * nl, srcs[i], fontsize=6.7, va="top",
                 color=DIM, transform=ax2.transAxes, family="monospace",
                 linespacing=1.45)
        y -= unit * lines[i]
        ax2.plot([0, 1], [y + unit * 0.35, y + unit * 0.35], color=LINE,
                 lw=0.6, transform=ax2.transAxes, clip_on=False)

    fig.suptitle("halo against the AirTag — six claims, each with its source",
                 fontsize=14, x=0.008, ha="left", y=0.995, fontweight="bold")
    fig.savefig(out("fig-halo-vs-airtag.png"), bbox_inches="tight")
    plt.close(fig)
    return "fig-halo-vs-airtag.png"


def _wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return "\n".join(lines)


# ---------------------------------------------------------------- fig 3
def _dark_bbox(im, thresh=150):
    """Bounding box of the pixels darker than `thresh`. Used to find the
    board in a photograph whose surround is pale."""
    a = np.asarray(im.convert("L"), dtype=np.int16)
    mask = a < thresh
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def _board_bbox(path):
    """halo's own render: the board is green on a lilac gradient. Take the
    pixels where green leads."""
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)
    g = a[:, :, 1] - (a[:, :, 0] + a[:, :, 2]) / 2.0
    mask = g > 6
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def fig_boards():
    # THE ROUTED board, rendered by tools/gen_board_renders.py from the
    # .kicad_pcb on disk. This pointed at out/render/halo_rev_a-top.png until
    # 2026-09-05, which was an ad-hoc render from the previous evening of an
    # UNROUTED board with a FOUR-tooth antenna. The figure was therefore
    # comparing Apple's shipped board against a halo board that no longer
    # existed. The scale is measured off whichever render this names, so
    # repointing it is safe: _board_bbox() re-derives px/mm from the pixels.
    halo_p = os.path.join(ROOT, "out", "render",
                          "halo_rev_a-routed-top.png")
    apple_p = os.path.join(ROOT, "images", "airtag",
                           "oflynn-frontside-26mm-cropped.jpg")
    halo_im = Image.open(halo_p).convert("RGB")
    apple_im = Image.open(apple_p).convert("RGB")

    hb = _board_bbox(halo_p)
    ab = _dark_bbox(apple_im, thresh=150)
    if hb is None or ab is None:
        print("CANNOT DETERMINE: could not find a board outline in one of "
              "the two images; not drawing a scale comparison")
        return None
    halo_px_per_mm = (hb[2] - hb[0]) / 26.00
    apple_px_per_mm = (ab[2] - ab[0]) / 26.0     # O'Flynn's own 26 mm crop

    # Crop each to a 30 mm square centred on its board, then scale both to
    # the same pixel size: after this, one screen pixel is the same number
    # of millimetres in both panels.
    def square(im, bb, ppm):
        cx, cy = (bb[0] + bb[2]) / 2.0, (bb[1] + bb[3]) / 2.0
        half = 13.0 * ppm
        box = (int(cx - half), int(cy - half), int(cx + half), int(cy + half))
        return im.crop(box).resize((900, 900), Image.LANCZOS)  # 26 mm

    h_sq = square(halo_im, hb, halo_px_per_mm)
    a_sq = square(apple_im, ab, apple_px_per_mm)

    fig, axes = plt.subplots(1, 2, figsize=(12.4, 7.0), dpi=150)
    for ax, im, ttl, sub in [
            (axes[0], h_sq, "halo rev A — top",
             "Ø26.00 mm, 4 layers, 0.60 mm. Nine-tooth 2.4 GHz "
             "element along the top arc; routed.\n"
             "measured %.1f px/mm in out/render/halo_rev_a-routed-top.png"
             % halo_px_per_mm),
            (axes[1], a_sq, "Apple AirTag A2187 — MLB front",
             "Ø~26 mm annular board, 0.30 mm. NFC coil at the centre.\n"
             "Colin O'Flynn, CC BY 4.0; measured %.1f px/mm on his 26 mm crop"
             % apple_px_per_mm)]:
        ax.imshow(im)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(LINE)
        ax.set_title(ttl, fontsize=11, color=INK, fontweight="bold", pad=8)
        ax.set_xlabel(sub, fontsize=8, color=DIM, labelpad=8)
        # a 10 mm scale bar, identical in both panels because the scale is
        bar = 10.0 * 900 / 26.0
        ax.add_patch(Rectangle((40, 850), bar, 12, facecolor=INK,
                               edgecolor="none"))
        ax.text(40 + bar / 2, 840, "10 mm", ha="center", va="bottom",
                fontsize=8.5, color=INK, fontweight="bold")
    fig.suptitle("Both boards at the same scale — each cropped to a 26 mm "
                 "square and shown at the same pixel size",
                 fontsize=12.5, y=0.965, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out("fig-board-side-by-side.png"), bbox_inches="tight")
    plt.close(fig)
    print("  halo board %.2f px/mm, Apple board %.2f px/mm"
          % (halo_px_per_mm, apple_px_per_mm))
    return "fig-board-side-by-side.png"


if __name__ == "__main__":
    made = [f for f in (fig_stack(), fig_compare(), fig_boards()) if f]
    for f in made:
        print("  %-32s %8d bytes" % (f, os.path.getsize(out(f))))
    print("%d figures in %s" % (len(made), OUT))
