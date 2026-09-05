#!/usr/bin/env python3
"""halo — the gallery. Generates out/gallery/INDEX.html.

    python3 tools/gen_gallery.py             # build the page
    python3 tools/gen_gallery.py --check     # build nothing, just verdict
    python3 tools/gen_gallery.py --self-test # break both checks on purpose

Lane G2 (what Leif sees). Leif made this a condition of the project being
done, verbatim: "you have shown me renders of the latest design + the
documents in the browser".

THE FIRST RULE. An image without a number beside it is decoration. Every card
carries three things: what the picture shows, the command that produced it,
and a verdict. The verdicts are NOT typed here — they are read at generation
time out of the files the other lanes write:

    out/mech/verdicts.json                  the enclosure's 12 checks
    out/render/stack.json                   the stack, measured
    out/render/board-renders.json           every board render's provenance
    out/verify/*.json                       the board, as its checkers see it
    ce-rf/out/<case>/verdict.json           the antennas
    ce-spice/out/<example>/verdict.json     the circuits
    out/gallery/fig-antenna-trajectory.json the antenna trajectory

so the page cannot drift away from them. If a verdict file is missing the
card says CANNOT DETERMINE and names the file; it never guesses a PASS.

THE SECOND RULE, AND IT IS NEW. AN IMAGE IS AS OLD AS IT IS. Every card
names the file whose mtime governs it — the solid's design.py, the board's
.kicad_pcb, the simulation run's own INPUT (model.json for an antenna, the
scenario's .cir for a circuit) — and this page compares the two and prints
CURRENT or STALE with the gap. That comparison
exists because on 2026-09-05 this repository shipped a gerber pack cut
7,742 s before the board it claims to describe, and the gallery was showing
a board render from the previous evening with a four-tooth antenna on it
while the board had nine. A stale picture presented as current is the same
defect as a stale gerber.

Two different policies, because staleness means two different things:

    stale_policy="label"   the picture is of a real earlier state and the
                           comparison is worth seeing. Published under a
                           loud STALE band naming what has changed since.
    stale_policy="refuse"  a simulation plot older than the MODEL IT PLOTS
                           is a leftover from a previous solve. Not
                           published at all; listed as a refusal. The source
                           is the run's input rather than its verdict, so
                           this needs no tolerance: a plot always lands a
                           few seconds before the verdict, and comparing to
                           the verdict marked all 30 of them stale.

AND IT READS EVERY IMAGE BACK. rendercover's lesson: a 404 thumbnail and a
loading thumbnail and a blank render look identical in a browser. Every
image here is opened, measured and checked for content before it is
published; one that fails is rendered as a stated refusal, not as an
<img> tag pointing at nothing.

Images are COPIED into out/gallery/img/ so the page is self-contained and
serves through tools/docs_server.py, which can only reach files under this
repo. ce-rf, ce-spice, out/mech and electronics/ are other lanes' — this
file reads them and never writes to them.
"""
import datetime
import html
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageStat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSHOP = os.path.dirname(os.path.dirname(ROOT))
CE_RF = os.path.join(WORKSHOP, "ce-rf")
CE_SPICE = os.path.join(WORKSHOP, "ce-spice")
OUT = os.path.join(ROOT, "out", "gallery")
IMG = os.path.join(OUT, "img")
E = html.escape

CHECK_ONLY = "--check" in sys.argv
SELF_TEST = "--self-test" in sys.argv


# ------------------------------------------------------------------ facts
MISSING = []


def load(path, what):
    """Read a JSON file, or return None. A missing file is an answer."""
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception as exc:                                  # noqa: BLE001
        MISSING.append("%s (%s): %s" % (path, what, exc))
        return None


MECH = load(os.path.join(ROOT, "out", "mech", "verdicts.json"), "enclosure")
STACK = load(os.path.join(ROOT, "out", "render", "stack.json"), "stack")
BRENDER = load(os.path.join(ROOT, "out", "render", "board-renders.json"),
               "board render provenance")
TRAJ = load(os.path.join(OUT, "fig-antenna-trajectory.json"),
            "antenna trajectory")

V = os.path.join(ROOT, "out", "verify")
DRC_ROUTED = load(os.path.join(V, "drc-routed-current.json"),
                  "DRC on the routed board")
DRC_SRC = load(os.path.join(V, "drc-current.json"),
               "DRC on the source board")
ROUTED = load(os.path.join(V, "routed-check.json"), "router integrity")
FABSET = load(os.path.join(V, "fabset-halo_rev_a.json"), "fab pack")
DFM = load(os.path.join(V, "dfm-jlc-4layer.json"), "DFM")


# --------------------------------------------------------------- mtimes
# The files whose age governs a picture. Naming them here rather than at each
# card means a reader can check the whole chain in one place.
DESIGN_PY = os.path.join(ROOT, "design.py")
BOARD_PY = os.path.join(ROOT, "electronics", "halo_rev_a", "board.py")
PCB_ROUTED = os.path.join(ROOT, "electronics", "halo_rev_a", "out",
                          "halo_rev_a-routed.kicad_pcb")
PCB_SRC = os.path.join(ROOT, "electronics", "halo_rev_a", "out",
                       "halo_rev_a.kicad_pcb")
FIGS_PY = os.path.join(ROOT, "tools", "gen_gallery_figs.py")
TRAJ_PY = os.path.join(ROOT, "tools", "gen_antenna_trajectory.py")


def mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return None


def stamp(t):
    if t is None:
        return "—"
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M")


def gap(seconds):
    if seconds < 90:
        return "%.0f s" % seconds
    if seconds < 5400:
        return "%.0f min" % (seconds / 60.0)
    return "%.1f h" % (seconds / 3600.0)


def freshness(img_path, src_path):
    """Is this picture as new as the thing it is a picture of?

    Returns (state, note). state is CURRENT, STALE or CANNOT DETERMINE.
    A card with no declared source is UNGOVERNED — a reference photograph
    has no source in this repo and no age to be wrong about.
    """
    if src_path is None:
        return ("UNGOVERNED", "")
    im, sm = mtime(img_path), mtime(src_path)
    rel = os.path.relpath(src_path, WORKSHOP)
    if im is None:
        return ("CANNOT DETERMINE", "the image is not on disk")
    if sm is None:
        return ("CANNOT DETERMINE",
                "%s is not on disk, so nothing governs this picture's age"
                % rel)
    if im >= sm:
        return ("CURRENT",
                "drawn %s, from %s last written %s — the picture is the newer "
                "of the two" % (stamp(im), rel, stamp(sm)))
    return ("STALE",
            "drawn %s; %s was written %s, which is %s LATER. This picture is "
            "of an earlier state of that file."
            % (stamp(im), rel, stamp(sm), gap(sm - im)))


# --------------------------------------------------------- lane readers
def mech(name):
    """One of the enclosure's own checks, by name."""
    if not MECH:
        return ("CANNOT DETERMINE", "out/mech/verdicts.json is not readable")
    for c in MECH["checks"]:
        if c["name"] == name:
            return (c["verdict"], c["why"])
    return ("CANNOT DETERMINE", "no check named %r in out/mech/verdicts.json"
            % name)


def rf(case):
    """An antenna case's verdict, and the rows behind it."""
    p = os.path.join(CE_RF, "out", case, "verdict.json")
    v = load(p, "ce-rf %s" % case)
    if not v:
        return ("CANNOT DETERMINE",
                "ce-rf/out/%s/verdict.json is not readable" % case, [])
    rows = [(r["name"], r.get("value"), r.get("unit", ""), r["verdict"],
             r.get("why", "")) for r in v.get("rows", [])]
    return (v.get("verdict", "CANNOT DETERMINE"), v.get("why", ""), rows)


def spice(example):
    """A ce-spice example: its verdict and every scenario in it."""
    p = os.path.join(CE_SPICE, "out", example, "verdict.json")
    v = load(p, "ce-spice %s" % example)
    if not v:
        return ("CANNOT DETERMINE",
                "ce-spice/out/%s/verdict.json is not readable" % example, [])
    rec = v.get("record", {})
    return (rec.get("verdict", "CANNOT DETERMINE"), rec.get("why", ""),
            rec.get("scenarios", []))


def board_state():
    """The board, as its own checkers report it RIGHT NOW, on the ROUTED
    file — which is the one the fab pack is cut from. Lane B1 owns these
    files and is still working in them, so the page says when it read them
    rather than pretending they are final."""
    bits = []
    if DRC_ROUTED:
        bits.append("DRC on the ROUTED board: %d violation(s), %d "
                    "unconnected item(s) (KiCad %s, %s)"
                    % (len(DRC_ROUTED.get("violations", [])),
                       len(DRC_ROUTED.get("unconnected_items", [])),
                       DRC_ROUTED.get("kicad_version", "?"),
                       DRC_ROUTED.get("date", "?")))
    if DRC_SRC:
        bits.append("the unrouted source board it came from still reports %d "
                    "unconnected"
                    % len(DRC_SRC.get("unconnected_items", [])))
    if ROUTED:
        rows = ROUTED.get("rows") or ROUTED.get("checks") or []
        f = sum(1 for r in rows if r.get("verdict") == "FAIL")
        bits.append("router-integrity check %s (%d rows, %d FAIL) — the "
                    "protected antenna and coil copper came back unchanged"
                    % (ROUTED.get("verdict", "?"), len(rows), f))
    if DFM:
        rows = DFM.get("rows", [])
        f = sum(1 for r in rows if r.get("verdict") == "FAIL")
        bits.append("JLC 4-layer DFM %d rows, %d FAIL" % (len(rows), f))
    if not bits:
        return ("CANNOT DETERMINE", "no board verdict file was readable")
    unconn = (len(DRC_ROUTED.get("unconnected_items", []))
              if DRC_ROUTED else None)
    ok = (unconn == 0 and DFM
          and not any(r.get("verdict") == "FAIL" for r in DFM.get("rows", [])))
    return ("PASS" if ok else "FAIL", " · ".join(bits))


BOARD_V, BOARD_WHY = board_state()


# ------------------------------------------------------------------ cards
def card(path, what, cmd, verdict, why, credit=None, wide=False,
         source=None, stale_policy="label", stale_note=None):
    return dict(path=path, what=what, cmd=cmd, verdict=verdict, why=why,
                credit=credit, wide=wide, source=source,
                stale_policy=stale_policy, stale_note=stale_note)


def mech_card(png, what, check, cmd=None, wide=False):
    v, why = mech(check)
    return card(os.path.join(ROOT, "out", "mech", png), what,
                cmd or "bin/cad ce-designs/halo/design.py", v, why, wide=wide,
                source=DESIGN_PY)


def render_card(png, what, verdict, why, wide=False):
    return card(os.path.join(ROOT, "out", "render", png), what,
                "bin/cad ce-designs/halo/tools/gen_gallery_renders.py",
                verdict, why, wide=wide, source=DESIGN_PY)


def gallery_card(png, what, verdict, why, wide=True, source=None,
                 cmd=None):
    return card(os.path.join(OUT, png), what,
                cmd or "python3 tools/gen_gallery_figs.py", verdict, why,
                wide=wide, source=source if source is not None else FIGS_PY)


def board_render_card(png, wide=True):
    """A board render, with the provenance the render tool recorded."""
    p = os.path.join(ROOT, "out", "render", png)
    row = None
    for r in (BRENDER or {}).get("renders", []):
        if os.path.basename(r["image"]) == png:
            row = r
            break
    if row is None:
        return card(p, png, "python3 tools/gen_board_renders.py",
                    "CANNOT DETERMINE",
                    "out/render/board-renders.json names no render called %s, "
                    "so nothing records what board this picture came from"
                    % png, wide=wide, source=None)
    src = os.path.join(ROOT, row["source"])
    return card(p, row["what"], row.get("command", "kicad-cli pcb render"),
                BOARD_V, "%s · %s" % (row["why"], BOARD_WHY),
                wide=wide, source=src)


def rf_cards(case, blurb, plots=("layout.png", "s11.png", "zin.png",
                                 "pattern.png")):
    """Plots for one antenna case, each carrying that case's own numbers.

    THE SOURCE IS model.json, NOT verdict.json — and the difference matters.
    model.json is the solver's INPUT, written when the run starts; verdict.json
    is its output, written when the run ends. A plot always lands a few seconds
    before the verdict, so comparing a plot to the verdict marks every plot in
    the repository stale (measured: 30 false refusals on the first attempt at
    this check). Comparing it to the run's own input needs no tolerance at all:
    A PLOT OLDER THAN THE MODEL IT CLAIMS TO PLOT IS FROM A DIFFERENT RUN.

    Measured 2026-09-05, and this is the one it catches:
    halo-rev-a-2g4-meander9-bare/pattern.png is 15:25 minus 09:34 = 5 h 51
    older than that case's model.json. It is left over from the void
    quarter-wave solve; the converged run refused the far-field box entirely
    and grades gain CANNOT DETERMINE. Publishing it would have put a
    radiation pattern under a case whose gain the lane declined to compute.
    """
    v, why, rows = rf(case)
    num = {r[0]: r for r in rows}
    vpath = os.path.join(CE_RF, "out", case, "model.json")

    def n(key, fmt="%.3f"):
        r = num.get(key)
        if not r or r[1] is None:
            return "CANNOT DETERMINE — %s was not measured" % key
        return (fmt % r[1]) + (" %s" % r[2] if r[2] not in ("", "-") else "")

    cmd = "bin/rf antenna specs/%s.json   (openEMS; ce-rf/out/%s/)" % (case,
                                                                      case)
    base = os.path.join(CE_RF, "out", case)
    per = {
        "layout.png": ("the copper as the solver sees it — element, ground "
                       "pour, passive copper and the 50 Ω port",
                       "eps_eff_implied %s" % n("eps_eff_implied")),
        "s11.png": ("return loss across the swept span",
                    "worst S11 in the BLE band with the best BUILDABLE "
                    "matching network: %s"
                    % n("s11_worst_in_ble_best_network_dB", "%.2f")),
        "zin.png": ("input impedance — every upward reactance zero-crossing "
                    "is a series resonance, and this is where they are read",
                    "f_series_res %s (band 2.400–2.4835 GHz)"
                    % n("f_series_res_GHz", "%.4f")),
        "pattern.png": ("the radiation pattern",
                        "gain %s (Apple's filed figure: −3.2 dBi)"
                        % n("gain_dBi", "%+.3f")),
    }
    out = []
    for fn in plots:
        what, number = per[fn]
        p = os.path.join(base, fn)
        rv = v
        # A plot whose own number came back None is not evidence of a pass.
        if "CANNOT DETERMINE" in number:
            rv = "CANNOT DETERMINE"
        out.append(card(p, "%s — %s" % (blurb, what), cmd, rv,
                        "%s · case verdict %s: %s" % (number, v, why),
                        source=vpath, stale_policy="refuse",
                        stale_note="a simulation plot older than its own "
                                   "run is a picture of a solve that was "
                                   "superseded"))
    return out


def spice_cards(example, blurb, cmd):
    """One card per scenario, carrying that scenario's asserts."""
    v, why, scen = spice(example)
    base = os.path.join(CE_SPICE, "out", example)
    out = []
    if not scen:
        out.append(card(os.path.join(base, "MISSING.png"),
                        "%s — no scenario list" % blurb, cmd,
                        "CANNOT DETERMINE", why,
                        source=os.path.join(base, "verdict.json"),
                        stale_policy="refuse"))
        return out
    for s in scen:
        asserts = "; ".join(
            "%s %s %s → %s (%s)" % (a["name"], a["op"],
                                    _fmt(a.get("expect")),
                                    _fmt(a.get("actual")), a["verdict"])
            for a in s.get("asserts", []))
        out.append(card(os.path.join(base, s["circuit"] + ".png"),
                        "%s — scenario “%s”" % (blurb, s["circuit"]),
                        cmd, s.get("verdict", "CANNOT DETERMINE"),
                        asserts or s.get("why", ""),
                        # The scenario's own netlist, written by ngspice
                        # immediately before the plot it produced. Same rule
                        # as the antennas: the run's INPUT, not its verdict.
                        source=os.path.join(base, s["circuit"] + ".cir"),
                        stale_policy="refuse"))
    return out


def _fmt(x):
    if isinstance(x, (int, float)):
        return ("%.4g" % x)
    if isinstance(x, list):
        return "[%s]" % ", ".join(_fmt(i) for i in x)
    return str(x)


def airtag_card(fn, what, why):
    # A photograph of Apple's hardware has no source in this repo. It is
    # UNGOVERNED rather than CURRENT: it cannot go stale, because nothing
    # here generates it.
    return card(os.path.join(ROOT, "images", "airtag", fn), what,
                "downloaded 2026-09-03 — see images/airtag/CATALOG.md",
                "REFERENCE", why,
                credit="Colin O'Flynn, CC BY 4.0" if fn.startswith("oflynn")
                else "FCC ID BCGA2187 internal photos — US public record",
                source=None)


# ------------------------------------------------------------------ page
def stack_note():
    if not STACK:
        return "CANNOT DETERMINE — out/render/stack.json is not readable"
    return ("total %.3f mm, max Ø%.3f mm, read off the finished solids"
            % (STACK["total_z"], STACK["max_dia"]))


def traj_note():
    if not TRAJ:
        return ("CANNOT DETERMINE",
                "out/gallery/fig-antenna-trajectory.json is not readable")
    n = TRAJ["shipping_solves"]
    return ("FAIL" if TRAJ["shipping_beating_apple"] == 0 else "PARTIAL",
            "of the %d solves of the element AS IT SHIPS — the NFC winding "
            "and BT1's negative-contact land present as passive copper — %d "
            "resonate inside 2.400–2.4835 GHz and %d beat Apple's −3.2 dBi. "
            "%d BARE control(s) do beat it, and deleting the winding is not "
            "a board halo can ship."
            % (n, TRAJ["shipping_in_band"], TRAJ["shipping_beating_apple"],
               TRAJ.get("bare_controls_beating_apple", 0)))


SECTIONS = [
    dict(
        id="board", n=1, title="The board, as it is right now",
        lede="These four came out of KiCad today, from the .kicad_pcb files "
             "on disk at the moment this page was generated. The fifth is "
             "the render this gallery showed until now, kept because the "
             "difference between them IS the point: it has four antenna "
             "teeth and no routing, and the board has nine and 610 track "
             "segments. Every caption names the .kicad_pcb it came from and "
             "that file's own timestamp.",
        cards=[
            board_render_card("halo_rev_a-routed-top.png"),
            board_render_card("halo_rev_a-routed-iso.png"),
            board_render_card("halo_rev_a-routed-bottom.png"),
            board_render_card("halo_rev_a-unrouted-top.png"),
            card(os.path.join(ROOT, "out", "render", "halo_rev_a-top.png"),
                 "SUPERSEDED — the render this gallery showed until "
                 "2026-09-05. Four antenna teeth on a wide pitch, no track "
                 "routing at all. Look at it beside the first picture in "
                 "this section: they are not the same board",
                 "ad-hoc kicad-cli render, 2026-09-04 22:02 — no tool "
                 "recorded it, which is why nothing caught its age",
                 "FAIL",
                 "it was shown as current for about 20 hours while the "
                 "board went to a nine-tooth element, moved the NFC coil off "
                 "the antenna arm to a measured 0.3627 mm clearance, cut the "
                 "ground planes out from under the coil, and routed from 83 "
                 "unconnected items to 28",
                 wide=True, source=PCB_ROUTED),
            card(os.path.join(ROOT, "out", "render", "halo_rev_a-bottom.png"),
                 "SUPERSEDED — the matching bottom view from the same "
                 "2026-09-04 session",
                 "ad-hoc kicad-cli render, 2026-09-04 22:03",
                 "FAIL",
                 "same board, same evening, same problem: it predates the "
                 "coil keep-out and the plane clearing",
                 wide=True, source=PCB_ROUTED),
        ]),

    dict(
        id="antenna", n=2, title="The antenna — the trajectory, not the "
                                 "best number",
        lede="This is the lane where this project could most easily lie to "
             "itself, so it is the one shown at greatest length. halo does "
             "NOT currently beat Apple's −3.2 dBi on the element that "
             "ships. The best measured figure on the shipping board is "
             "−3.391 dBi at a resonance 15.4 % below the band; the latest "
             "solve, a retune finished at 17:55 today, reads −11.806 dBi at "
             "2.3730 GHz and is WORSE. The one number that beats Apple, "
             "+0.521 dBi, is a rim IFA on a Ø30 × 1.0 mm study puck — a "
             "different antenna on a different board, quoted to Leif once "
             "and withdrawn (CONCERNS.md C-5).",
        cards=[
            gallery_card("fig-antenna-trajectory.png",
                         "every 2.4 GHz solve in order: where the element "
                         "resonates against the band it must hit, and what "
                         "it radiates against Apple's filed figure. Filled "
                         "markers are the element WITH the NFC winding "
                         "present — the condition it ships in; hollow ones "
                         "are bare controls",
                         *traj_note(), source=TRAJ_PY,
                         cmd="python3 tools/gen_antenna_trajectory.py"),
        ]
        + rf_cards("halo-rev-a-2g4-rt1-passive",
                   "LATEST — retune 1, the shipping element loaded, "
                   "2026-09-05 17:55")
        + rf_cards("halo-rev-a-2g4-meander9-passive",
                   "the best measured state of the shipping element — "
                   "DECISIONS.md D26i")
        + rf_cards("halo-rev-a-2g4-rt1-bare",
                   "the bare control for the retune — a board with the NFC "
                   "winding deleted, which halo cannot ship")
        + rf_cards("halo-rev-a-2g4-meander9-bare",
                   "the bare nine-tooth control — the case that measured NO "
                   "far field at all, and whose leftover pattern.png this "
                   "page refuses below")
        + rf_cards("halo-round-rim-ifa",
                   "WITHDRAWN AS HALO'S NUMBER — the Ø30 × 1.0 mm study "
                   "puck, the only geometry here that beats Apple")),

    dict(
        id="boundary", n=3, title="Why four hypotheses were needed before "
                                  "any of this could be measured",
        lede="Every antenna solve in this repository before 2026-09-05 "
             "15:2x was void, and finding out why took three refuted "
             "hypotheses before the fourth held. The residual energy "
             "FLOORED instead of decaying — meander9-bare sat at −34.87 dB "
             "from timestep 41,745 to 459,690, flat to 0.01 dB over 418,000 "
             "timesteps, against a −40 dB end criterion, so more timesteps "
             "could never reach it. Refuted in order: (1) the mesh — the "
             "min_cell_mm fix was real and it floored again; (2) the "
             "passive copper — the bare control floored too; (3) the "
             "meander density — a four-tooth element differing by 0.0078 mm "
             "of trace floored as readily as nine. The fourth held: the "
             "absorbing boundary. sim.airbox_pad_mm went from a quarter "
             "wavelength to a half, and the same model converged in 8,415 "
             "timesteps where it had capped at 460,000. The Courant "
             "timestep never moved, so the bigger box did not win by "
             "running longer.",
        cards=[
            card(os.path.join(CE_RF, "out",
                              "halo-rev-a-2g4-meander4-bare-pad-quarter",
                              "s11.png"),
                 "0.250 λ absorbing boundary — the setting every solve in "
                 "this repo used until today. CAPPED at 460,000 timesteps, "
                 "1783.9 s of wall clock, solver_converged 0.0",
                 "bin/rf antenna specs/halo-rev-a-2g4-meander4-bare-"
                 "pad-quarter.json",
                 "FAIL",
                 "it also reproduced the published parent to 0.00 % on "
                 "residual, which is what pays for the study: the control "
                 "is the same run, so the difference below is the boundary "
                 "and nothing else",
                 source=os.path.join(
                     CE_RF, "out",
                     "halo-rev-a-2g4-meander4-bare-pad-quarter",
                     "model.json"),
                 stale_policy="refuse"),
            card(os.path.join(CE_RF, "out",
                              "halo-rev-a-2g4-meander4-bare-pad-half",
                              "s11.png"),
                 "0.500 λ — the same model, one variable changed. Converged "
                 "in 8,415 timesteps, 143.8 s, solver_converged 1.0",
                 "bin/rf antenna specs/halo-rev-a-2g4-meander4-bare-"
                 "pad-half.json",
                 "PASS",
                 "12.4× less wall clock at 1.87× the cells. Smallest cell "
                 "0.15000 mm in both, so 460,000 timesteps is the same "
                 "physical duration in each — the larger box did not win by "
                 "running longer",
                 source=os.path.join(
                     CE_RF, "out", "halo-rev-a-2g4-meander4-bare-pad-half",
                     "model.json"),
                 stale_policy="refuse"),
            card(os.path.join(CE_RF, "out",
                              "halo-rev-a-2g4-meander4-bare-pad-full",
                              "s11.png"),
                 "1.000 λ — the convergence check on the parameter itself",
                 "bin/rf antenna specs/halo-rev-a-2g4-meander4-bare-"
                 "pad-full.json",
                 "PASS",
                 "f_series_res moves 2.4873 → 2.4877 → 2.4896 GHz across "
                 "quarter, half and full: 0.09 % between half and full, so "
                 "half a wavelength is enough and the quarter is the outlier",
                 source=os.path.join(
                     CE_RF, "out", "halo-rev-a-2g4-meander4-bare-pad-full",
                     "model.json"),
                 stale_policy="refuse"),
            card(os.path.join(CE_RF, "out",
                              "halo-rev-a-2g4-room-r9743", "layout.png"),
                 "the room study, as built: the ground pour at R9.74310 mm, "
                 "1.44891 mm from the element's inner copper edge",
                 "python3 tools/emit_room_study.py; bin/rf antenna "
                 "specs/halo-rev-a-2g4-room-r9743.json",
                 "PASS",
                 "this control reproduces the published parent's resistance "
                 "to −0.27 % (3.2911 Ω against 3.3000 Ω), which is what "
                 "makes the four cases below it readable as one variable",
                 source=os.path.join(CE_RF, "out",
                                     "halo-rev-a-2g4-room-r9743",
                                     "model.json"),
                 stale_policy="refuse"),
            card(os.path.join(CE_RF, "out",
                              "halo-rev-a-2g4-room-r4000", "layout.png"),
                 "the same board with the pour pulled back to R4.00 mm — "
                 "an island smaller than the battery, and the far end of "
                 "the only lever a 26 mm disc has",
                 "python3 tools/emit_room_study.py; bin/rf antenna "
                 "specs/halo-rev-a-2g4-room-r4000.json",
                 "PARTIAL",
                 "radiation resistance rises monotonically 3.2911 → 9.7058 Ω "
                 "across the five cases, 2.949× — but the 10 Ω the specs "
                 "expect is NOT reached inside the sweep, and the tool "
                 "refuses to extrapolate past its measured points. Room is "
                 "a real lever and not a sufficient one",
                 source=os.path.join(CE_RF, "out",
                                     "halo-rev-a-2g4-room-r4000",
                                     "model.json"),
                 stale_policy="refuse"),
        ]),

    dict(
        id="product", n=4, title="The product",
        lede="What the thing is. Every picture below is the same set of "
             "solids design.py builds and measures — none is an artist's "
             "impression, and nothing here was drawn by hand. design.py has "
             "not changed since 2026-09-04 12:30, so these renders are "
             "current and say so.",
        cards=[
            render_card("halo-puck-hero.png",
                        "the assembled puck, lit — 31.874 mm across and "
                        "7.980 mm tall",
                        *mech("envelope"), wide=True),
            mech_card("halo-puck-iso.png",
                      "the same solid in flat CAD shading, which is where "
                      "the crown's concentric rings read",
                      "max-OD height"),
            gallery_card("fig-stack.png",
                         "the stack drawn to scale on both axes, one band "
                         "per part at its measured z",
                         "PASS" if STACK else "CANNOT DETERMINE",
                         stack_note()),
            mech_card("halo-puck-section-front.png",
                      "the 7.980 mm stack, sectioned on the axis and "
                      "square on — this is the picture of the constraint",
                      "envelope", wide=True),
            mech_card("halo-puck-section.png",
                      "the same cut on an isometric camera",
                      "cavity air (upper bound)"),
            render_card("halo-puck-exploded-wide.png",
                        "all ten parts, each lifted 6.000 mm along z in "
                        "stack order",
                        *mech("FDM variants assemble"), wide=True),
            mech_card("halo-shell-top.png",
                      "the shell alone, four views — a straight-pull "
                      "moulding with no undercut anywhere",
                      "shell wall"),
            mech_card("halo-carrier.png",
                      "the carrier alone — every undercut in the product "
                      "lives on this part, which nobody sees",
                      "stepped diameters"),
            mech_card("halo-battery-door.png",
                      "the stamped 301 stainless door",
                      "bayonet mechanism"),
            mech_card("halo-pcb-blank.png",
                      "the Ø26.00 mm board blank as the enclosure models it",
                      "metal inside the keep-out"),
        ]),

    dict(
        id="mechanism", n=5, title="The mechanism",
        lede="Three mechanisms carry this product, and each was measured "
             "by kernel probes rather than argued: the bayonet door, the "
             "sprung contacts, and the piezo bonded to a flat land it "
             "would otherwise have to conform to.",
        cards=[
            render_card("halo-bayonet.png",
                        "the bayonet — three carrier legs at 0/120/240° "
                        "and the door's three tabs",
                        *mech("bayonet mechanism"), wide=True),
            render_card("halo-bayonet-section.png",
                        "door, seal and carrier cut on the axis, where the "
                        "detent ridge lives",
                        *mech("door seal"), wide=True),
            render_card("halo-contacts.png",
                        "the three stamped springs alone — two positive on "
                        "the wall, one negative on the floor",
                        *mech("press travel")),
            mech_card("halo-battery-contact-pos-a.png",
                      "one contact, four views",
                      "press travel"),
            render_card("halo-piezo-land.png",
                        "the shell cut open: the flat internal land the "
                        "bender bonds to, instead of the crown's R91.2 "
                        "inner radius",
                        *mech("diaphragm gap"), wide=True),
            render_card("halo-board-in-shell.png",
                        "the board where it actually sits, shell cut away "
                        "— cell below, bender above",
                        *mech("metal inside the keep-out"), wide=True),
        ]),

    dict(
        id="sims", n=6, title="The circuits",
        lede="Four circuits, every scenario, each plot with the assertions "
             "that were evaluated against it. These are ngspice runs, not "
             "sketches: the numbers beside each picture are what the "
             "solver returned, and the rule each was graded against. Unlike "
             "the antenna, this lane is quiet — all four examples pass "
             "every assert, and have since 2026-09-04.",
        cards=(
            spice_cards("cr2032_pulse_load",
                        "the cell under a radio pulse",
                        "ce-spice: examples/cr2032_pulse_load/circuit.py")
            + spice_cards("speaker_hbridge",
                          "the sounder's H-bridge and boost",
                          "ce-spice: examples/speaker_hbridge/circuit.py")
            + spice_cards("decoupling_ldo",
                          "the 1.8 V rail and its decoupling",
                          "ce-spice: examples/decoupling_ldo/circuit.py")
            + spice_cards("nfc_tank",
                          "the NFC tank at 13.56 MHz",
                          "ce-spice: examples/nfc_tank/circuit.py"))),

    dict(
        id="versus", n=7, title="halo against the AirTag",
        lede="Apple's own hardware, photographed by other people, and the "
             "comparison figures built against it. These photographs have "
             "no source in this repository and cannot go stale — nothing "
             "here generates them.",
        cards=[
            gallery_card("fig-halo-vs-airtag.png",
                         "the comparison figure: envelope to scale, then "
                         "mass, antenna gain, cost and the functional gap",
                         "PARTIAL",
                         "Ø31.874 vs Ø31.87 mm and 7.980 vs 7.98 mm PASS; "
                         "7.8 g vs 11 g and $6.09 vs $29 PARTIAL; antenna "
                         "gain FAIL on the shipping element; precision "
                         "finding FAIL (SPEC.md F9, DECISIONS.md D1/D5)"),
            gallery_card("fig-board-side-by-side.png",
                         "halo rev A against Apple's own board photograph, "
                         "both cropped to a 26 mm square and shown at one "
                         "pixel scale — the two 10 mm bars are the same "
                         "length by construction",
                         "REFERENCE",
                         "halo Ø26.00 mm measured in the render at "
                         "52.9 px/mm; Apple's on O'Flynn's own 26 mm crop "
                         "at 30.3 px/mm. Apple's board is a 0.30 mm "
                         "annular flex-thin board; halo's is 0.60 mm and "
                         "solid — DECISIONS.md D17, a deliberate divergence. "
                         "NOTE: this figure was built from the SUPERSEDED "
                         "board render, so halo's half of it is the "
                         "four-tooth unrouted board — which is why it is "
                         "banded STALE against the .kicad_pcb below",
                         source=PCB_ROUTED),
            airtag_card("oflynn-frontside-tpnames.jpg",
                        "Apple's board, top, with every test point numbered "
                        "— the map halo's pinout was read against",
                        "silkscreen 820-01736-A, data code 2920 17. NFC "
                        "coil, magnet well and speaker-coil pads all "
                        "visible"),
            airtag_card("oflynn-backside-1000px.jpeg",
                        "Apple's board, bottom — nRF52832, 32 MHz crystal, "
                        "TPS62746 buck and the U1 shield can",
                        "the U1 is the one part of this photograph halo "
                        "cannot reproduce: SPEC.md F9"),
            airtag_card("fcc-BCGA2187-internal-photo-6.jpg",
                        "Apple's own functional labelling of its antenna "
                        "carrier: Bluetooth Antenna, Bluetooth Module, "
                        "UWB Module, UWB Antenna",
                        "three laser-direct-structured traces on plastic. "
                        "halo puts its BLE antenna in PCB copper on FR-4 "
                        "instead, which is why the two are not like-for-"
                        "like even where the numbers are"),
            airtag_card("fcc-BCGA2187-internal-photo-4.jpg",
                        "Apple's battery cavity with the cell removed — "
                        "three sprung contacts, no connector",
                        "halo copies this scheme because nothing else fits "
                        "the stack: SPEC.md §4, no retainer under 2 mm "
                        "exists"),
            airtag_card("fcc-BCGA2187-internal-photo-1.jpg",
                        "the AirTag beside a ruler, from Apple's own FCC "
                        "filing — the object halo is measured against",
                        "≈31–32 mm across in the frame; the drawing halo's "
                        "profile comes from says 31.87 mm"),
        ]),
]


# --------------------------------------------------------------- checking
def read_back(src):
    """Open the image and decide whether it is one. Returns
    (ok, note, (w, h))."""
    try:
        with Image.open(src) as im:
            im.load()
            w, h = im.size
            if w < 80 or h < 80:
                return (False, "only %dx%d px — too small to be a figure"
                        % (w, h), (w, h))
            st = ImageStat.Stat(im.convert("L"))
            if st.stddev[0] < 1.0:
                return (False, "blank: whole image has stddev %.2f"
                        % st.stddev[0], (w, h))
            return (True, "%dx%d px, stddev %.1f" % (w, h, st.stddev[0]),
                    (w, h))
    except FileNotFoundError:
        return (False, "no such file", None)
    except Exception as exc:                                  # noqa: BLE001
        return (False, "unreadable: %s" % exc, None)


def stage(src):
    """Copy an image into out/gallery/img/ under a name that says where it
    came from, and return that name."""
    rel = os.path.relpath(src, WORKSHOP).replace(os.sep, "-")
    rel = rel.replace("ce-designs-halo-", "").replace("..-", "")
    dst = os.path.join(IMG, rel)
    if not CHECK_ONLY:
        os.makedirs(IMG, exist_ok=True)
        if (not os.path.exists(dst)
                or os.path.getmtime(dst) < os.path.getmtime(src)):
            shutil.copy2(src, dst)
    return rel


def rev():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              cwd=ROOT, capture_output=True,
                              text=True).stdout.strip() or "unknown"
    except Exception:                                         # noqa: BLE001
        return "unknown"


CSS = """
:root{--ink:#16181d;--dim:#5c6370;--line:#dfe3e8;--bg:#fff;--panel:#f7f8fa;
 --ready:#0a7d33;--partial:#a86500;--not:#a11;--cd:#7a4fb5;--ref:#41627e;--link:#0b5fa5;
 --stale:#a04a00;--stalebg:#fdf1e3;--fresh:#0a7d33}
@media(prefers-color-scheme:dark){:root{--ink:#e8eaed;--dim:#9aa2ad;
 --line:#2c313a;--bg:#14161a;--panel:#1b1e24;--ready:#4ec26f;--partial:#e0a233;
 --not:#f0736a;--cd:#b78ef0;--ref:#8fb4d4;--link:#7bb7ec;
 --stale:#e79b4d;--stalebg:#2a2013;--fresh:#4ec26f}}
*{box-sizing:border-box}
body{margin:0;padding:2.5rem 1.5rem 6rem;background:var(--bg);color:var(--ink);
 font:16px/1.65 -apple-system,"Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif}
main{max-width:64rem;margin:0 auto}
h1{font-size:2rem;margin:0 0 .2rem;letter-spacing:-.02em}
h2{font-size:1.25rem;margin:3.5rem 0 .75rem;padding-bottom:.4rem;border-bottom:1px solid var(--line)}
.sub{color:var(--dim);margin:0 0 1.5rem}
.lede{color:var(--ink);margin:.2rem 0 1.6rem}
blockquote{margin:1rem 0;padding:.8rem 1.1rem;border-left:3px solid var(--line);
 color:var(--ink);background:rgba(127,127,127,.06)}
.badge{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.06em;
 padding:.15rem .45rem;border-radius:3px;border:1px solid currentColor;white-space:nowrap}
.PASS{color:var(--ready)} .PARTIAL{color:var(--partial)} .FAIL{color:var(--not)}
.CD{color:var(--cd)} .REFERENCE{color:var(--ref)}
code,.mono{font:.85em ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim);
 word-break:break-word}
figure{margin:0 0 2rem;border:1px solid var(--line);border-radius:6px;overflow:hidden;
 background:var(--panel)}
figure img{display:block;width:100%;height:auto;background:#fff}
figcaption{padding:.75rem .9rem .85rem;font-size:.86rem;line-height:1.55}
figcaption .what{color:var(--ink)}
figcaption .why{color:var(--ink);display:block;margin-top:.35rem}
figcaption .cmd{display:block;margin-top:.35rem}
figcaption .credit{display:block;margin-top:.3rem;font-size:.76rem;color:var(--dim)}
.agebar{padding:.45rem .9rem;font-size:.78rem;font-weight:600;letter-spacing:.02em;
 border-bottom:1px solid var(--line)}
.age-CURRENT{color:var(--fresh);background:rgba(10,125,51,.07)}
.age-STALE{color:var(--stale);background:var(--stalebg)}
.age-CANNOTDETERMINE{color:var(--cd);background:rgba(122,79,181,.08)}
.age-UNGOVERNED{color:var(--dim);background:rgba(127,127,127,.05)}
.agebar .n{font-weight:400;color:var(--dim)}
.age-STALE .n{color:var(--stale)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(20rem,1fr));gap:1.2rem}
.grid figure{margin:0}
.wide{grid-column:1/-1}
.refused{padding:1.1rem;border:1px dashed var(--not);border-radius:6px;color:var(--not);
 background:rgba(170,17,17,.05);font-size:.88rem}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.92rem}
th,td{text-align:left;vertical-align:top;padding:.5rem .7rem;border-bottom:1px solid var(--line)}
th{font-weight:600;color:var(--dim);font-size:.8rem;text-transform:uppercase;letter-spacing:.05em}
.meta{color:var(--dim);font-size:.82rem;margin-top:3.5rem;padding-top:1rem;border-top:1px solid var(--line)}
a{color:var(--link)}
nav{margin:1.5rem 0 0;padding:.7rem .9rem;background:var(--panel);border:1px solid var(--line);border-radius:6px}
nav a{margin-right:1.1rem;font-size:.9rem;white-space:nowrap;display:inline-block}
figure a{display:block;line-height:0}
.tally{display:flex;flex-wrap:wrap;gap:.6rem;margin:1.2rem 0}
.tally div{flex:1 1 9rem;padding:.7rem .9rem;border:1px solid var(--line);border-radius:6px;
 background:var(--panel)}
.tally b{display:block;font-size:1.5rem;line-height:1.2;font-variant-numeric:tabular-nums}
.tally span{font-size:.78rem;color:var(--dim)}
"""


def badge(v):
    cls = {"CANNOT DETERMINE": "CD"}.get(v, v if v in
                                         ("PASS", "PARTIAL", "FAIL",
                                          "REFERENCE") else "CD")
    return '<span class="badge %s">%s</span>' % (cls, E(v))


# ------------------------------------------------------------- self-test
def self_test():
    """Break both checks on purpose and require them to notice.

    A check that has never been seen to fail is not a check. These are the
    two this page's honesty rests on: does freshness() actually catch an
    image older than its source, and does read_back() actually catch a
    picture that is not one.
    """
    import tempfile
    rows = []

    def row(name, got, want):
        ok = got == want
        rows.append((ok, name, "got %r, wanted %r" % (got, want)))

    with tempfile.TemporaryDirectory() as d:
        img = os.path.join(d, "img.png")
        src = os.path.join(d, "src.txt")
        # A picture with actual content in it — half black, half white, so
        # its stddev is far above the blank threshold. The blank control
        # below is the same size and uniform.
        real = Image.new("RGB", (400, 300), "white")
        for y in range(150):
            for x in range(400):
                real.putpixel((x, y), (0, 0, 0))
        real.save(img)
        with open(src, "w") as fh:
            fh.write("x")

        # 1 — source older than the image: CURRENT
        os.utime(src, (0, os.path.getmtime(img) - 3600))
        row("an image newer than its source reads CURRENT",
            freshness(img, src)[0], "CURRENT")

        # 2 — source NEWER than the image: STALE. This is the whole point.
        os.utime(src, (0, os.path.getmtime(img) + 3600))
        row("an image OLDER than its source reads STALE",
            freshness(img, src)[0], "STALE")

        # 3 — one second is enough; the check has no fudge factor
        os.utime(src, (0, os.path.getmtime(img) + 1))
        row("one second of staleness is still STALE",
            freshness(img, src)[0], "STALE")

        # 4 — a missing image is not a pass
        row("a missing image is CANNOT DETERMINE",
            freshness(os.path.join(d, "nope.png"), src)[0],
            "CANNOT DETERMINE")

        # 5 — a missing source is not a pass either
        row("a missing source is CANNOT DETERMINE",
            freshness(img, os.path.join(d, "nope.txt"))[0],
            "CANNOT DETERMINE")

        # 6 — no source declared: UNGOVERNED, not CURRENT
        row("no declared source reads UNGOVERNED, never CURRENT",
            freshness(img, None)[0], "UNGOVERNED")

        # 7 — a real picture reads back
        row("a real picture reads back", read_back(img)[0], True)

        # 8 — a blank one does not
        blank = os.path.join(d, "blank.png")
        Image.new("RGB", (400, 300), "white").save(blank)
        row("a blank image is refused", read_back(blank)[0], False)

        # 9 — a thumbnail-sized one does not
        tiny = os.path.join(d, "tiny.png")
        Image.new("RGB", (40, 40), "red").save(tiny)
        row("a 40x40 image is refused", read_back(tiny)[0], False)

        # 10 — a file that is not an image at all
        row("a non-image file is refused", read_back(src)[0], False)

    bad = [r for r in rows if not r[0]]
    for ok, name, note in rows:
        print("  %-4s %s" % ("PASS" if ok else "FAIL", name),
              "" if ok else ("— " + note))
    print("self-test: %d of %d deliberate breaks were caught"
          % (len(rows) - len(bad), len(rows)))
    return 0 if not bad else 1


def main():
    counts = {"published": 0, "refused": 0, "CURRENT": 0, "STALE": 0,
              "CANNOT DETERMINE": 0, "UNGOVERNED": 0}
    refusals = []
    ages = []
    body = []
    a = body.append

    for sec in SECTIONS:
        a('<h2 id="%s">%d · %s</h2>' % (E(sec["id"]), sec["n"],
                                        E(sec["title"])))
        a('<p class="lede">%s</p>' % E(sec["lede"]))
        a('<div class="grid">')
        for c in sec["cards"]:
            rel = os.path.relpath(c["path"], WORKSHOP)
            klass = " wide" if c.get("wide") else ""
            state, note = freshness(c["path"], c.get("source"))

            ok, rnote, _ = read_back(c["path"])
            if not ok:
                counts["refused"] += 1
                refusals.append((rel, rnote))
                a('<div class="refused%s"><b>NOT PUBLISHED — %s</b><br>'
                  '%s<br><span class="mono">%s</span><br>'
                  'This card would have shown: %s</div>'
                  % (klass, E(rnote), E(rel), E(c["cmd"]), E(c["what"])))
                continue

            if state == "STALE" and c.get("stale_policy") == "refuse":
                counts["refused"] += 1
                why = "STALE and refused — %s. %s" % (
                    c.get("stale_note") or "the source is newer", note)
                refusals.append((rel, why))
                a('<div class="refused%s"><b>NOT PUBLISHED — STALE</b><br>'
                  '%s<br><span class="mono">%s</span><br>'
                  'This card would have shown: %s</div>'
                  % (klass, E(why), E(rel), E(c["what"])))
                continue

            counts["published"] += 1
            counts[state] = counts.get(state, 0) + 1
            ages.append((rel, state, note))
            name = stage(c["path"])
            a('<figure class="%s">' % klass.strip())
            if state != "UNGOVERNED":
                a('<div class="agebar age-%s">%s <span class="n">%s</span>'
                  '</div>' % (state.replace(" ", ""),
                              "STALE — DO NOT READ THIS AS CURRENT"
                              if state == "STALE" else state, E(note)))
            a('<a href="img/%s" target="_blank" rel="noopener">'
              '<img src="img/%s" loading="lazy" alt="%s"></a>'
              % (E(name), E(name), E(c["what"])))
            a('<figcaption><span class="what">%s</span> %s'
              % (E(c["what"]), badge(c["verdict"])))
            a('<span class="why">%s</span>' % E(c["why"]))
            a('<span class="cmd mono">%s</span>' % E(c["cmd"]))
            if c.get("credit"):
                a('<span class="credit">%s</span>' % E(c["credit"]))
            a('<span class="credit mono">%s · %s</span>' % (E(rel), E(rnote)))
            a('</figcaption></figure>')
        a('</div>')

    verdict = "PASS" if counts["STALE"] == 0 and counts["refused"] == 0 \
        else "PARTIAL"

    p = []
    w = p.append
    w('<!doctype html><html lang="en"><meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width,initial-scale=1">')
    w('<title>halo — the gallery</title><style>%s</style><main>' % CSS)
    w('<h1>halo — the gallery</h1>')
    w('<p class="sub">an open copy of the Apple AirTag · generated %s at %s '
      '· commit <span class="mono">%s</span></p>'
      % (datetime.date.today().isoformat(),
         datetime.datetime.now().strftime("%H:%M"), rev()))
    w('<blockquote>“you have shown me renders of the latest design + the '
      'documents in the browser” — Leif, 2026-09-05, one of the four '
      'conditions of this project being done</blockquote>')
    w('<div class="tally">')
    for k, lbl in [("published", "images published"),
                   ("CURRENT", "current — newer than what they show"),
                   ("STALE", "labelled STALE, shown anyway"),
                   ("UNGOVERNED", "reference photos, nothing to be stale "
                                  "against"),
                   ("refused", "refused, with the reason")]:
        w('<div><b>%d</b><span>%s</span></div>' % (counts.get(k, 0), lbl))
    w('</div>')
    w('<p>Every picture on this page came out of a tool that measured '
      'something. There is no artist\'s impression here and no render of a '
      'part that does not exist as a solid. Each caption says what the '
      'image shows, the command that produced it, and the verdict beside '
      'it — read out of the other lanes\' own verdict files at the moment '
      'this page was generated, so the page cannot claim a PASS they do '
      'not.</p>')
    w('<p><b>And every picture states its own age.</b> The band above each '
      'image names the file whose timestamp governs it — the solid\'s '
      '<code>design.py</code>, the board\'s <code>.kicad_pcb</code>, the '
      'simulation run\'s own INPUT (<code>model.json</code> for an antenna, '
      'the scenario\'s <code>.cir</code> for a circuit) — and says CURRENT '
      'or STALE with the gap. The input rather than the verdict, because a '
      'plot always lands a few seconds before the verdict and comparing to '
      'the verdict marked all 30 of them stale. A simulation plot older '
      'than the model it plots is <b>refused outright</b>, because it is a '
      'picture of physics that was thrown away. A stale render is published under a loud band, because '
      'the difference between the old picture and the new one is itself the '
      'thing worth seeing.</p>')
    w('<p><b>An image that could not be read back is not shown.</b> Every '
      'file below was opened, sized and checked for content before '
      'publication; one that failed is printed as a stated refusal naming '
      'the file, because a broken thumbnail and a loading thumbnail and a '
      'blank render look identical in a browser.</p>')
    w('<nav>%s <a href="STATE.html">→ current state, in a minute</a></nav>'
      % " ".join('<a href="#%s">%d · %s</a>' % (E(s["id"]), s["n"],
                                                E(s["title"]))
                 for s in SECTIONS))
    w("\n".join(body))

    w('<h2 id="ages">%d · Every image, and how old it is</h2>'
      % (len(SECTIONS) + 1))
    w('<p class="lede">The whole freshness table in one place, so nobody has '
      'to scroll to find out whether they are looking at today\'s work.</p>')
    w('<table><tr><th>image</th><th>state</th><th>against what, and when'
      '</th></tr>')
    for rel, state, note in sorted(ages, key=lambda r: (r[1] != "STALE",
                                                        r[0])):
        w('<tr><td class="mono">%s</td><td class="badge %s">%s</td>'
          '<td>%s</td></tr>'
          % (E(rel), "FAIL" if state == "STALE" else
             ("PASS" if state == "CURRENT" else "CD"), E(state), E(note)))
    w('</table>')

    w('<h2 id="refusals">%d · What this page refused to draw</h2>'
      % (len(SECTIONS) + 2))
    w('<p class="lede">A gallery is only worth reading if it is willing to '
      'be empty in the places where there is nothing to show.</p>')
    w('<table><tr><th>what</th><th>why it is not here</th></tr>')
    for what, why in REFUSED_BY_HAND + [(r[0], r[1]) for r in refusals]:
        w('<tr><td><b>%s</b></td><td>%s</td></tr>' % (E(what), E(why)))
    w('</table>')

    if MISSING:
        w('<h2>Files this page could not read</h2><ul>')
        for m in MISSING:
            w('<li class="mono">%s</li>' % E(m))
        w('</ul>')

    w('<p class="meta">Regenerate with <code>python3 tools/gen_gallery.py'
      '</code>. The board renders come from <code>python3 '
      'tools/gen_board_renders.py</code>, the solid renders from <code>'
      'bin/cad ce-designs/halo/tools/gen_gallery_renders.py</code>, the '
      'antenna trajectory from <code>python3 '
      'tools/gen_antenna_trajectory.py</code> and the comparison figures '
      'from <code>python3 tools/gen_gallery_figs.py</code>. Images are '
      'copied into <code>out/gallery/img/</code> so this page is '
      'self-contained; the originals stay in the lanes that own them '
      '(<code>out/mech</code>, <code>ce-rf</code>, <code>ce-spice</code>, '
      '<code>images/airtag</code>) and are never written to from here. '
      'Verdict of this page: <b>%s</b> — %d stale, %d refused.</p>'
      % (verdict, counts["STALE"], counts["refused"]))
    w('</main></html>')

    if CHECK_ONLY:
        print("%d would publish, %d would be refused" % (counts["published"],
                                                         counts["refused"]))
    else:
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, "INDEX.html"), "w") as fh:
            fh.write("\n".join(p))
        with open(os.path.join(OUT, "gallery.json"), "w") as fh:
            json.dump(dict(generated=datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"), counts=counts,
                ages=[dict(image=r, state=s, why=n) for r, s, n in ages],
                refusals=[dict(image=r, why=n) for r, n in refusals],
                verdict=verdict), fh, indent=2)
        print("wrote %s (%d bytes)"
              % (os.path.join(OUT, "INDEX.html"),
                 os.path.getsize(os.path.join(OUT, "INDEX.html"))))
    print("published %d (%d current, %d STALE, %d ungoverned) · refused %d "
          "· sections %d"
          % (counts["published"], counts["CURRENT"], counts["STALE"],
             counts["UNGOVERNED"], counts["refused"], len(SECTIONS)))
    for r in refusals:
        print("  REFUSED %s — %s" % r)
    for m in MISSING:
        print("  MISSING %s" % m)
    # A stale image is not a failure of this page — publishing one WITHOUT
    # saying so would be. Exit 1 only when something could not be read.
    return 0 if not MISSING else 1


# Things this lane decided NOT to draw, and why. Stated on the page so the
# absence is an answer rather than a hole.
REFUSED_BY_HAND = [
    ("A photograph of a finished halo",
     "none exists. Nothing here has been moulded, stamped or printed, and "
     "an image that looked like a finished product would be the one lie "
     "this page could tell. The renders are of solids; they are labelled "
     "as renders."),
    ("A radiation pattern for halo-rev-a-2g4-meander9-bare",
     "there is a pattern.png on disk for that case and it is 5 h 53 older "
     "than the run it sits in. It is left over from the void quarter-wave "
     "solve; the converged run refused the far-field box entirely, because "
     "|S11| at 2.4418 GHz was −0.82 dB — the structure accepts 17.2 % of "
     "the incident power against a declared 18.7 % floor, and Prad / "
     "P_accepted below that is a ratio without meaning. The refusal is "
     "correct and this page inherits it."),
    ("A gain figure for the retune that is currently solving",
     "halo-rev-a-2g4-rt2-passive started at 17:58 today and has no "
     "verdict.json, no measurements and a zero-byte result file. It is on "
     "disk and it is not an answer. Nothing about it is shown here."),
    ("halo's antenna performance from a bare control",
     "two solves on this board DO beat Apple's −3.2 dBi — meander4-bare at "
     "−1.850 dBi and rt1-bare at −1.464 dBi — and both delete the NFC "
     "winding from the model. Measured, that winding pulls this element "
     "22.8 % in frequency and costs it more than 10 dB. A bare control is a "
     "control; quoting one as the product's number is the favourable-half "
     "headline this project already published once."),
    ("A rendering of the assembled product with the real board inside it",
     "the enclosure models the board as a blank disc of the right diameter "
     "and thickness; the populated board lives in KiCad in another lane. "
     "The two are shown side by side instead of fused into one picture "
     "that would imply a fit check nobody has run."),
    ("A mass figure for the finished tag",
     "docs/MECHANICAL.md §10's 7.8 g is the enclosure only. No populated "
     "board mass exists in this repo, so the comparison figure marks the "
     "row PARTIAL rather than showing 7.8 g against Apple's 11 g as if "
     "they measured the same thing."),
    ("An acoustic result for the sounder",
     "SPL at 25 cm is CANNOT DETERMINE until a shell is built and a bender "
     "bonded to it (docs/MECHANICAL.md §9). The H-bridge simulations are "
     "electrical; none of them is a loudness."),
    ("A render of the board board.py currently describes",
     "board.py was last written 2026-09-05 14:50:31 and neither .kicad_pcb "
     "on disk has been regenerated since — they are 07:54 and 08:15. Every "
     "board picture here is therefore current for a file on disk and NOT "
     "necessarily for the board lane B1 is now describing. Rendering "
     "board.py would mean running lane B1's generator, which is not this "
     "lane's to run."),
]


if __name__ == "__main__":
    sys.exit(self_test() if SELF_TEST else main())
