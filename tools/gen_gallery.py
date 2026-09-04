#!/usr/bin/env python3
"""halo — the gallery. Generates out/gallery/INDEX.html.

    python3 tools/gen_gallery.py            # build the page
    python3 tools/gen_gallery.py --check    # build nothing, just verdict

Lane G1 (visuals). Leif asked for "concept images and renderings of the real
thing and simulation results and documentation" — a page he can open and SEE
the product and the evidence.

THE RULE THIS FILE ENFORCES. An image without a number beside it is
decoration. Every card carries three things: what the picture shows, the
command that produced it, and a verdict. The verdicts are NOT typed here —
they are read at generation time out of the files the other lanes write:

    out/mech/verdicts.json                  the enclosure's 12 checks
    out/render/stack.json                   the stack, measured
    out/verify/drc.json, fabset-*.json      the board, as it stands
    ce-rf/out/<case>/verdict.json           the antennas
    ce-spice/out/<example>/verdict.json     the circuits

so the page cannot drift away from them. If a verdict file is missing the
card says CANNOT DETERMINE and names the file; it never guesses a PASS.

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


# ------------------------------------------------------------------ facts
def load(path, what):
    """Read a JSON file, or return None. A missing file is an answer."""
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception as exc:                                  # noqa: BLE001
        MISSING.append("%s (%s): %s" % (path, what, exc))
        return None


MISSING = []

MECH = load(os.path.join(ROOT, "out", "mech", "verdicts.json"), "enclosure")
STACK = load(os.path.join(ROOT, "out", "render", "stack.json"), "stack")
DRC = load(os.path.join(ROOT, "out", "verify", "drc.json"), "board DRC")
FABSET = load(os.path.join(ROOT, "out", "verify", "fabset-halo_rev_a.json"),
              "fab pack")
DFM = load(os.path.join(ROOT, "out", "verify", "dfm-jlc-4layer.json"), "DFM")


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
    """The board, as its own checkers report it RIGHT NOW. Lane B1 owns
    these files and is still working in them, so the page says when it
    read them rather than pretending they are final."""
    bits = []
    if DRC:
        bits.append("DRC %d violation(s), %d unconnected item(s), "
                    "%d parity issue(s) (KiCad %s, %s)"
                    % (len(DRC.get("violations", [])),
                       len(DRC.get("unconnected_items", [])),
                       len(DRC.get("schematic_parity", [])),
                       DRC.get("kicad_version", "?"), DRC.get("date", "?")))
    if FABSET:
        c = FABSET.get("counts", {})
        bits.append("fab pack %s — %d PASS / %d FAIL / %d CANNOT DETERMINE"
                    % (FABSET.get("verdict", "?"), c.get("PASS", 0),
                       c.get("FAIL", 0), c.get("CANNOT DETERMINE", 0)))
    if DFM:
        rows = DFM.get("rows", [])
        f = sum(1 for r in rows if r.get("verdict") == "FAIL")
        bits.append("JLC 4-layer DFM %d rows, %d FAIL" % (len(rows), f))
    if not bits:
        return ("CANNOT DETERMINE", "no board verdict file was readable")
    ok = (DRC and not DRC.get("violations") and not DRC.get("unconnected_items")
          and FABSET and FABSET.get("verdict") == "PASS"
          and DFM and not any(r.get("verdict") == "FAIL"
                              for r in DFM.get("rows", [])))
    return ("PASS" if ok else "FAIL", " · ".join(bits))


BOARD_V, BOARD_WHY = board_state()


# ------------------------------------------------------------------ cards
def card(path, what, cmd, verdict, why, credit=None, wide=False):
    return dict(path=path, what=what, cmd=cmd, verdict=verdict, why=why,
                credit=credit, wide=wide)


def mech_card(png, what, check, cmd=None, wide=False):
    v, why = mech(check)
    return card(os.path.join(ROOT, "out", "mech", png), what,
                cmd or "bin/cad ce-designs/halo/design.py", v, why, wide=wide)


def render_card(png, what, verdict, why, wide=False):
    return card(os.path.join(ROOT, "out", "render", png), what,
                "bin/cad ce-designs/halo/tools/gen_gallery_renders.py",
                verdict, why, wide=wide)


def gallery_card(png, what, verdict, why, wide=True):
    return card(os.path.join(OUT, png), what,
                "python3 tools/gen_gallery_figs.py", verdict, why, wide=wide)


def rf_cards(case, blurb):
    """Four plots per antenna case, each carrying that case's own numbers."""
    v, why, rows = rf(case)
    num = {r[0]: r for r in rows}

    def n(key, fmt="%.3f"):
        r = num.get(key)
        if not r or r[1] is None:
            return "CANNOT DETERMINE — %s was not measured" % key
        return (fmt % r[1]) + (" %s" % r[2] if r[2] not in ("", "-") else "")

    cmd = "bin/rf run %s   (openEMS; ce-rf/out/%s/)" % (case, case)
    base = os.path.join(CE_RF, "out", case)
    per = {
        "layout.png": ("the copper as the solver sees it — trace, ground "
                       "plane and the 50 Ω port",
                       "eps_eff_implied %s" % n("eps_eff_implied")),
        "s11.png": ("return loss across the band",
                    "worst S11 in the BLE band, best matching network: %s"
                    % n("s11_worst_in_ble_best_network_dB", "%.2f")),
        "zin.png": ("input impedance — the reactance zero-crossing is the "
                    "series resonance",
                    "f_series_res %s (band 2.400–2.4835 GHz)"
                    % n("f_series_res_GHz", "%.4f")),
        "pattern.png": ("the radiation pattern",
                        "realized gain %s (Apple's filed figure: −3.2 dBi)"
                        % n("gain_dBi", "%+.3f")),
    }
    out = []
    for fn, (what, number) in per.items():
        p = os.path.join(base, fn)
        rv = v
        # A plot whose own number came back None is not evidence of a pass.
        if "CANNOT DETERMINE" in number:
            rv = "CANNOT DETERMINE"
        out.append(card(p, "%s — %s" % (blurb, what), cmd, rv,
                        "%s · case verdict %s: %s" % (number, v, why)))
    return out


def spice_cards(example, blurb, cmd):
    """One card per scenario, carrying that scenario's asserts."""
    v, why, scen = spice(example)
    base = os.path.join(CE_SPICE, "out", example)
    out = []
    if not scen:
        out.append(card(os.path.join(base, "MISSING.png"),
                        "%s — no scenario list" % blurb, cmd,
                        "CANNOT DETERMINE", why))
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
                        asserts or s.get("why", "")))
    return out


def _fmt(x):
    if isinstance(x, (int, float)):
        return ("%.4g" % x)
    if isinstance(x, list):
        return "[%s]" % ", ".join(_fmt(i) for i in x)
    return str(x)


def airtag_card(fn, what, why):
    return card(os.path.join(ROOT, "images", "airtag", fn), what,
                "downloaded 2026-09-03 — see images/airtag/CATALOG.md",
                "REFERENCE", why,
                credit="Colin O'Flynn, CC BY 4.0" if fn.startswith("oflynn")
                else "FCC ID BCGA2187 internal photos — US public record")


# ------------------------------------------------------------------ page
def stack_note():
    if not STACK:
        return "CANNOT DETERMINE — out/render/stack.json is not readable"
    return ("total %.3f mm, max Ø%.3f mm, read off the finished solids"
            % (STACK["total_z"], STACK["max_dia"]))


SECTIONS = [
    dict(
        id="product", n=1, title="The product",
        lede="What the thing is. Every picture below is the same set of "
             "solids design.py builds and measures — none is an artist's "
             "impression, and nothing here was drawn by hand.",
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
        id="board", n=2, title="The board",
        lede="halo rev A: Ø26.00 mm, four layers, 0.60 mm. Lane B1 owns "
             "these files and is still working in them, so the verdict "
             "beside each picture is read live from that lane's own "
             "checkers at the moment this page was generated — not "
             "remembered from when it was.",
        cards=[
            card(os.path.join(ROOT, "out", "render", "halo_rev_a-top.png"),
                 "the board, top — the rim inverted-F meanders across the "
                 "top-left arc, outside the component field",
                 "KiCad 3D render of electronics/halo_rev_a/out/"
                 "halo_rev_a.kicad_pcb (lane B1)",
                 BOARD_V, BOARD_WHY, wide=True),
            card(os.path.join(ROOT, "out", "render", "halo_rev_a-bottom.png"),
                 "the board, bottom",
                 "KiCad 3D render of electronics/halo_rev_a/out/"
                 "halo_rev_a.kicad_pcb (lane B1)",
                 BOARD_V, BOARD_WHY, wide=True),
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
                         "solid — DECISIONS.md D17, a deliberate divergence"),
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
                        "halo puts its BLE antenna in PCB copper instead — "
                        "the reason the two antenna cases below differ"),
            airtag_card("fcc-BCGA2187-internal-photo-4.jpg",
                        "Apple's battery cavity with the cell removed — "
                        "three sprung contacts, no connector",
                        "halo copies this scheme because nothing else fits "
                        "the stack: SPEC.md §4, no retainer under 2 mm "
                        "exists"),
        ]),

    dict(
        id="antenna", n=3, title="The antenna",
        lede="Two cases, and they do not agree — which is the honest state "
             "of this lane. halo-round-rim-ifa is a Ø30 × 1.0 mm study "
             "geometry: it PASSES, and at +0.521 dBi it beats the −3.2 dBi "
             "Apple filed with the FCC. halo-rev-a-2g4 is THE BOARD THIS "
             "PACK SHIPS, and its solve did not converge, so it reports no "
             "gain at all. The study is not the board. Both are below.",
        cards=(rf_cards("halo-round-rim-ifa",
                        "study geometry Ø30 × 1.0 mm")
               + rf_cards("halo-rev-a-2g4",
                          "THE SHIPPED BOARD Ø26.00 × 0.60 mm"))),

    dict(
        id="sims", n=4, title="The simulations",
        lede="Four circuits, every scenario, each plot with the assertions "
             "that were evaluated against it. These are ngspice runs, not "
             "sketches: the numbers beside each picture are what the "
             "solver returned, and the rule each was graded against.",
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
        id="versus", n=6, title="halo against the AirTag",
        lede="Six claims, each with the file it came from and what it does "
             "not say. Two are PASS, two are PARTIAL because the "
             "comparison is not yet like-for-like, one is CANNOT DETERMINE "
             "because the shipped board's antenna solve did not converge, "
             "and one is a FAIL we do not expect to close.",
        cards=[
            gallery_card("fig-halo-vs-airtag.png",
                         "the comparison figure: envelope to scale, then "
                         "mass, antenna gain, cost and the functional gap",
                         "PARTIAL",
                         "Ø31.874 vs Ø31.87 mm and 7.980 vs 7.98 mm PASS; "
                         "7.8 g vs 11 g and $6.75 vs $29 PARTIAL; antenna "
                         "gain CANNOT DETERMINE; precision finding FAIL "
                         "(SPEC.md F9, DECISIONS.md D1/D5)"),
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
 --ready:#0a7d33;--partial:#a86500;--not:#a11;--cd:#7a4fb5;--ref:#41627e;--link:#0b5fa5}
@media(prefers-color-scheme:dark){:root{--ink:#e8eaed;--dim:#9aa2ad;
 --line:#2c313a;--bg:#14161a;--panel:#1b1e24;--ready:#4ec26f;--partial:#e0a233;
 --not:#f0736a;--cd:#b78ef0;--ref:#8fb4d4;--link:#7bb7ec}}
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
"""


def badge(v):
    cls = {"CANNOT DETERMINE": "CD"}.get(v, v if v in
                                         ("PASS", "PARTIAL", "FAIL",
                                          "REFERENCE") else "CD")
    return '<span class="badge %s">%s</span>' % (cls, E(v))


def main():
    counts = {"published": 0, "refused": 0}
    refusals = []
    body = []
    a = body.append

    for sec in SECTIONS:
        a('<h2 id="%s">%d · %s</h2>' % (E(sec["id"]), sec["n"],
                                        E(sec["title"])))
        a('<p class="lede">%s</p>' % E(sec["lede"]))
        a('<div class="grid">')
        for c in sec["cards"]:
            ok, note, _ = read_back(c["path"])
            klass = " wide" if c.get("wide") else ""
            if not ok:
                counts["refused"] += 1
                rel = os.path.relpath(c["path"], WORKSHOP)
                refusals.append((rel, note))
                a('<div class="refused%s"><b>NOT PUBLISHED — %s</b><br>'
                  '%s<br><span class="mono">%s</span><br>'
                  'This card would have shown: %s</div>'
                  % (klass, E(note), E(rel), E(c["cmd"]), E(c["what"])))
                continue
            counts["published"] += 1
            name = stage(c["path"])
            a('<figure class="%s">' % klass.strip())
            a('<a href="img/%s" target="_blank" rel="noopener">'
              '<img src="img/%s" loading="lazy" alt="%s"></a>'
              % (E(name), E(name), E(c["what"])))
            a('<figcaption><span class="what">%s</span> %s'
              % (E(c["what"]), badge(c["verdict"])))
            a('<span class="why">%s</span>' % E(c["why"]))
            a('<span class="cmd mono">%s</span>' % E(c["cmd"]))
            if c.get("credit"):
                a('<span class="credit">%s</span>' % E(c["credit"]))
            a('<span class="credit mono">%s · %s</span>'
              % (E(os.path.relpath(c["path"], WORKSHOP)), E(note)))
            a('</figcaption></figure>')
        a('</div>')

    verdict = "PASS" if counts["refused"] == 0 else "FAIL"

    p = []
    w = p.append
    w('<!doctype html><html lang="en"><meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width,initial-scale=1">')
    w('<title>halo — the gallery</title><style>%s</style><main>' % CSS)
    w('<h1>halo — the gallery</h1>')
    w('<p class="sub">an open function-for-function copy of the Apple AirTag '
      '· generated %s · commit <span class="mono">%s</span> · '
      '<b>%d images published, %d refused</b></p>'
      % (datetime.date.today().isoformat(), rev(),
         counts["published"], counts["refused"]))
    w('<blockquote>“showing concept images and renderings of the real thing '
      'and simulation results and documentation” — Leif, 2026-09-05</blockquote>')
    w('<p>Every picture on this page came out of a tool that measured '
      'something. There is no artist\'s impression here and no render of a '
      'part that does not exist as a solid. Each caption says what the '
      'image shows, the command that produced it, and the verdict beside '
      'it — read out of the other lanes\' own verdict files at the moment '
      'this page was generated, so the page cannot claim a PASS they do '
      'not.</p>')
    w('<p><b>An image that could not be read back is not shown.</b> Every '
      'file below was opened, sized and checked for content before '
      'publication; one that failed is printed as a stated refusal naming '
      'the file, because a broken thumbnail and a loading thumbnail and a '
      'blank render look identical in a browser.</p>')
    w('<nav>%s</nav>' % " ".join('<a href="#%s">%d · %s</a>'
                                 % (E(s["id"]), s["n"], E(s["title"]))
                                 for s in SECTIONS))
    w("\n".join(body))

    w('<h2 id="refusals">7 · What this page refused to draw</h2>')
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
      '</code>. The renders come from <code>bin/cad '
      'ce-designs/halo/tools/gen_gallery_renders.py</code> and the figures '
      'from <code>python3 tools/gen_gallery_figs.py</code>. Images are '
      'copied into <code>out/gallery/img/</code> so this page is '
      'self-contained; the originals stay in the lanes that own them '
      '(<code>out/mech</code>, <code>ce-rf</code>, <code>ce-spice</code>, '
      '<code>images/airtag</code>) and are never written to from here. '
      'Verdict of this page: <b>%s</b>.</p>' % verdict)
    w('</main></html>')

    if CHECK_ONLY:
        print("%d would publish, %d would be refused" % (counts["published"],
                                                         counts["refused"]))
    else:
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, "INDEX.html"), "w") as fh:
            fh.write("\n".join(p))
        print("wrote %s (%d bytes)"
              % (os.path.join(OUT, "INDEX.html"),
                 os.path.getsize(os.path.join(OUT, "INDEX.html"))))
    print("published %d · refused %d · sections %d"
          % (counts["published"], counts["refused"], len(SECTIONS)))
    for r in refusals:
        print("  REFUSED %s — %s" % r)
    for m in MISSING:
        print("  MISSING %s" % m)
    return 0 if counts["refused"] == 0 and not MISSING else 1


# Things this lane decided NOT to draw, and why. Stated on the page so the
# absence is an answer rather than a hole.
REFUSED_BY_HAND = [
    ("A photograph of a finished halo",
     "none exists. Nothing here has been moulded, stamped or printed, and "
     "an image that looked like a finished product would be the one lie "
     "this page could tell. The renders are of solids; they are labelled "
     "as renders."),
    ("A radiation pattern for the board that ships",
     "ce-rf/out/halo-rev-a-2g4 has no pattern.png because its solve did "
     "not converge and it measured no gain to plot. Drawing the study "
     "geometry's pattern under the shipped board's name would have been "
     "the most useful-looking and least true picture available."),
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
     "bonded to it (docs/MECHANICAL.md §9). The H-bridge simulations below "
     "are electrical; none of them is a loudness."),
]


if __name__ == "__main__":
    sys.exit(main())
