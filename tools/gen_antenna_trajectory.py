#!/usr/bin/env python3
"""The antenna trajectory, plotted from ce-rf's own verdict files — lane G2.

    python3 tools/gen_antenna_trajectory.py

Writes out/gallery/fig-antenna-trajectory.png and fig-antenna-trajectory.json.

WHY A TRAJECTORY AND NOT A HEADLINE. The one number this project was most
tempted to publish is "+0.521 dBi, better than Apple's -3.2 dBi". It is real,
it is measured, and it is a DIFFERENT ANTENNA ON A DIFFERENT BOARD — a rim IFA
on a Ø30 x 1.0 mm study puck, not the Ø26.00 x 0.60 mm board that ships.
CONCERNS.md C-5 records that it was quoted to Leif and withdrawn.

So this figure plots every solve in order, study and board alike, with the
2.400-2.4835 GHz band drawn as a band and Apple's filed -3.2 dBi drawn as a
line, and lets the reader see that the shipping element has been outside the
band in every solve so far. A single bar would have been a headline. This is
the shape of the work.

Nothing here is typed. Every number is read out of
ce-rf/out/<case>/verdict.json at generation time; a case with no file, or a
row whose value is null, is drawn as an explicit gap with the reason printed
beside it, never interpolated and never omitted.
"""
import datetime
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                # noqa: E402
from matplotlib.patches import Rectangle                       # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSHOP = os.path.dirname(os.path.dirname(ROOT))
CE_RF = os.path.join(WORKSHOP, "ce-rf")
OUT = os.path.join(ROOT, "out", "gallery")

BAND = (2.400, 2.4835)          # the BLE band, GHz
APPLE_DBI = -3.2                # Apple's own filed figure, FCC ID BCGA2187

# In the order they were solved. TWO flags, and the difference between them is
# the whole point of this figure:
#   board  — the Ø26.00 x 0.60 mm rev A geometry, not a study puck
#   loaded — the NFC winding and BT1's negative-contact land PRESENT as passive
#            copper, which is the condition the product actually ships in
# A bare control omits that copper. It is a legitimate control and it is NOT a
# performance figure for halo: measured, the winding pulls this element 22.8 %
# in frequency and costs it more than 10 dB of gain.
CASES = [
    ("halo-round-rim-ifa", "rim IFA\nØ30 study puck", False, False),
    ("halo-rev-a-2g4", "rev A 2G4 bare\nquarter-λ box", True, False),
    ("halo-rev-a-2g4-meander4-bare", "4-tooth bare\nhalf-λ box", True, False),
    ("halo-rev-a-2g4-meander9-bare", "9-tooth bare\nhalf-λ box", True, False),
    ("halo-rev-a-2g4-meander9-passive", "9-tooth LOADED\nas it ships", True, True),
    ("halo-rev-a-2g4-rt1-bare", "retune 1 bare", True, False),
    ("halo-rev-a-2g4-rt1-passive", "retune 1 LOADED\nships — LATEST", True, True),
]


def verdict(case):
    p = os.path.join(CE_RF, "out", case, "verdict.json")
    try:
        with open(p) as fh:
            v = json.load(fh)
    except Exception as exc:                                   # noqa: BLE001
        return None, "%s is not readable: %s" % (p, exc), None
    rows = {r["name"]: r for r in v.get("rows", [])}
    return v, rows, os.path.getmtime(p)


def val(rows, key):
    r = rows.get(key) if isinstance(rows, dict) else None
    if r is None:
        return None, "no row named %s" % key
    if r.get("value") is None:
        return None, r.get("why") or "value is null"
    return r["value"], r.get("why", "")


def main():
    data = []
    for case, label, is_board, is_loaded in CASES:
        v, rows, mt = verdict(case)
        if v is None:
            data.append(dict(case=case, label=label, board=is_board,
                             loaded=is_loaded, ok=False, why=rows))
            continue
        f, fwhy = val(rows, "f_series_res_GHz")
        g, gwhy = val(rows, "gain_dBi")
        s, swhy = val(rows, "s11_worst_in_ble_best_network_dB")
        conv, _ = val(rows, "solver_converged")
        data.append(dict(
            case=case, label=label, board=is_board, loaded=is_loaded, ok=True,
            verdict=v.get("verdict"), why=v.get("why"),
            f_GHz=f, f_why=fwhy, gain_dBi=g, gain_why=gwhy,
            s11_dB=s, s11_why=swhy, converged=conv,
            solved=datetime.datetime.fromtimestamp(mt).strftime(
                "%Y-%m-%d %H:%M")))

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(14.6, 9.8), sharex=True,
        gridspec_kw=dict(height_ratios=[1.05, 1], hspace=0.12))
    fig.patch.set_facecolor("white")

    x = list(range(len(data)))
    labels = [d["label"] for d in data]

    # ---- top: where the element resonates, against the band it must hit
    ax1.add_patch(Rectangle((-0.6, BAND[0]), len(data) - 0.8 + 0.2,
                            BAND[1] - BAND[0], facecolor="#bfe3c8",
                            edgecolor="#2f7d52", lw=1.1, zorder=0))
    ax1.text(-0.5, 2.93, "shaded: 2.400–2.4835 GHz, the band it must hit",
             va="top", ha="left", fontsize=10, color="#1d5c3a",
             fontweight="bold")

    for i, d in enumerate(data):
        if not d["ok"] or d["f_GHz"] is None:
            ax1.plot([i], [2.44], marker="x", ms=13, mew=2.6, color="#7a4fb5")
            ax1.annotate("no value", (i, 2.44), (0, -20),
                         textcoords="offset points", ha="center",
                         fontsize=8.5, color="#7a4fb5")
            continue
        f = d["f_GHz"]
        inband = BAND[0] <= f <= BAND[1]
        c = "#2f7d52" if inband else ("#b3541e" if d["board"] else "#41627e")
        m = "o" if d["board"] else "s"
        ax1.plot([i], [f], marker=m, ms=15 if d["loaded"] else 10,
                 color=c if d["loaded"] else "white", mec=c,
                 mew=1.4 if d["loaded"] else 2.4, zorder=3)
        off = 15 if f < 2.44 else -22
        ax1.annotate("%.4f" % f, (i, f), (0, off),
                     textcoords="offset points", ha="center",
                     fontsize=10, fontweight="bold", color=c)
        if not inband:
            pct = 100.0 * (f - sum(BAND) / 2) / (sum(BAND) / 2)
            ax1.annotate("%+.1f%%" % pct, (i, f), (0, off + (11 if off > 0
                                                             else -12)),
                         textcoords="offset points", ha="center",
                         fontsize=8.5, color=c)

    ax1.set_ylabel("series resonance  f_series_res  (GHz)", fontsize=10.5)
    ax1.set_title("halo's 2.4 GHz element, every solve in order — "
                  "where it resonates, and what it radiates",
                  fontsize=14, fontweight="bold", loc="left", pad=14)
    ax1.grid(axis="y", color="#e5e7eb", lw=0.8)
    ax1.set_axisbelow(True)
    ax1.set_ylim(1.9, 3.0)

    # ---- bottom: gain against Apple's own filed number
    ax2.axhline(APPLE_DBI, color="#a11", lw=1.6, ls="--", zorder=1)
    ax2.text(-0.5, -15.1,
             "dashed: Apple −3.2 dBi (FCC ID BCGA2187) — anything below "
             "that line is worse than the AirTag", va="bottom", ha="left",
             fontsize=9.5, color="#a11", fontweight="bold")

    for i, d in enumerate(data):
        g = d.get("gain_dBi")
        if g is None:
            ax2.plot([i], [-6.5], marker="x", ms=13, mew=2.6, color="#7a4fb5")
            why = (d.get("gain_why") or d.get("why") or "")[:46]
            ax2.annotate("CANNOT DETERMINE\n" + why, (i, -6.5), (0, -34),
                         textcoords="offset points", ha="center",
                         fontsize=7.6, color="#7a4fb5", linespacing=1.35)
            continue
        beats = g >= APPLE_DBI
        c = "#2f7d52" if beats else "#b3541e"
        if not d["board"]:
            c = "#41627e"
        ax2.plot([i], [g], marker="o" if d["board"] else "s",
                 ms=15 if d["loaded"] else 10,
                 color=c if d["loaded"] else "white", mec=c,
                 mew=1.4 if d["loaded"] else 2.4, zorder=3)
        ax2.annotate("%+.3f dBi" % g, (i, g), (0, 15),
                     textcoords="offset points", ha="center", fontsize=10,
                     fontweight="bold", color=c)
        dy = 29 if g >= APPLE_DBI else -24
        ax2.annotate("%+.2f dB vs Apple" % (g - APPLE_DBI), (i, g), (0, dy),
                     textcoords="offset points", ha="center", fontsize=8.5,
                     color=c)

    ax2.set_ylabel("gain at 2.44 GHz  (dBi)", fontsize=10.5)
    ax2.set_ylim(-15.5, 3.4)
    ax2.grid(axis="y", color="#e5e7eb", lw=0.8)
    ax2.set_axisbelow(True)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=9, linespacing=1.5)
    ax2.set_xlim(-0.6, len(data) - 0.4 + 0.35)

    ship = [d for d in data if d["board"] and d["loaded"]]
    beat = [d for d in ship if d.get("gain_dBi") is not None
            and d["gain_dBi"] >= APPLE_DBI]
    inband = [d for d in ship if d.get("f_GHz") is not None
              and BAND[0] <= d["f_GHz"] <= BAND[1]]
    bare_beat = [d for d in data if d["board"] and not d["loaded"]
                 and d.get("gain_dBi") is not None
                 and d["gain_dBi"] >= APPLE_DBI]

    fig.text(0.008, 0.008,
             "\u25cf filled = the rev A element WITH the NFC winding and "
             "BT1's land present — the condition it ships in.\n"
             "\u25cb hollow = the same board BARE: a control, not a product "
             "figure.   \u25a0 = a study puck, not this board.   "
             "\u2715 = no value was measured, and the reason is printed.\n"
             "MEASURED: of the %d solves of the element AS IT SHIPS, %d "
             "resonate inside 2.400\u20132.4835 GHz and %d beat Apple's "
             "\u22123.2 dBi. %d BARE control(s) do beat it — removing the "
             "winding is not a design halo can ship.\n"
             "Read out of ce-rf/out/<case>/verdict.json; nothing here is "
             "typed. python3 tools/gen_antenna_trajectory.py \u00b7 "
             "generated %s"
             % (len(ship), len(inband), len(beat), len(bare_beat),
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
             fontsize=8.4, color="#5c6370", linespacing=1.6)

    fig.subplots_adjust(left=0.068, right=0.985, top=0.928, bottom=0.205)
    os.makedirs(OUT, exist_ok=True)
    png = os.path.join(OUT, "fig-antenna-trajectory.png")
    fig.savefig(png, dpi=130, facecolor="white")
    plt.close(fig)

    summary = dict(
        tool="tools/gen_antenna_trajectory.py",
        generated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        band_GHz=list(BAND), apple_gain_dBi=APPLE_DBI,
        shipping_solves=len(ship),
        shipping_in_band=len(inband),
        shipping_beating_apple=len(beat),
        bare_controls_beating_apple=len(bare_beat),
        cases=data)
    with open(os.path.join(OUT, "fig-antenna-trajectory.json"), "w") as fh:
        json.dump(summary, fh, indent=2)

    print("wrote %s (%d bytes)" % (png, os.path.getsize(png)))
    for d in data:
        print("  %-34s f=%s gain=%s  %s"
              % (d["case"],
                 ("%.4f" % d["f_GHz"]) if d.get("f_GHz") is not None else "—",
                 ("%+.3f" % d["gain_dBi"]) if d.get("gain_dBi") is not None
                 else "CANNOT DETERMINE",
                 d.get("verdict", "?")))
    print("element AS IT SHIPS: %d solves, %d in band, %d beating Apple "
          "(%d bare controls do)"
          % (len(ship), len(inband), len(beat), len(bare_beat)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
