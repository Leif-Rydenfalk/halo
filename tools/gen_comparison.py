#!/usr/bin/env python3
"""halo vs the real AirTag — the comparison, generated from data.

    python3 tools/gen_comparison.py

Reads
    spec/comparison.json            the curated Apple-side facts, transcribed
                                    from research/01-airtag-hardware.md with
                                    every confidence tag carried through, plus
                                    this lane's own readings off the photographs
    spec/bom-resolved.json          halo's parts, order codes, stock and price
                                    -- pulled live, never retyped
    out/verify/dfm-jlc-4layer.json  halo's board facts, measured by `fab dfm`

Writes
    docs/COMPARISON.md              the document
    out/comparison/INDEX.html       the page, styled like the release pack
    out/comparison/comparison-summary.json   the counts, machine readable
    out/comparison/fig-boards-labelled.png   both boards, labelled, matched
                                    scale on the front pair only

Nothing on any of those pages is hand-typed. Where a number cannot be
established the generator prints CANNOT DETERMINE and says why; it never
substitutes a plausible one.

Lane C1. Owns: docs/COMPARISON.md, spec/comparison.json, this file,
out/comparison/. Reads electronics/ and out/gallery/ and writes to neither.
"""
import datetime
import html
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "comparison")
E = html.escape

BOARD_MM = (25.618092, 26.0)   # Edge.Cuts extent, measured off the .kicad_pcb


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


def rev():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


DATA = load("spec/comparison.json")
BOM = load("spec/bom-resolved.json")
DFM = load("out/verify/dfm-jlc-4layer.json")

# ---------------------------------------------------------------- halo parts
# one index: refdes -> the resolved BOM line. Fail loud on a ref that is not
# on the board, because a comparison row pointing at a part that does not
# exist is worse than a missing row.
BY_REF = {}
for line in BOM["lines"]:
    for r in line["refs"]:
        BY_REF[r] = line

MISSING_REFS = []
for c in DATA["components"]:
    for r in (c["halo"].get("refs") or []):
        if r not in BY_REF:
            MISSING_REFS.append((c["n"], r))


def _part_line(line, refs=None):
    """One compact line describing a resolved BOM line."""
    p = line.get("part") or {}
    tag = ", ".join(refs or line["refs"])
    if not p.get("mpn"):
        return "%s %s — no order code (%s)" % (tag, line.get("value") or "?",
                                               line.get("verdict") or "?")
    price = (p.get("price_usd") or {}).get("1000")
    return "%s %s — %s (%s) · %s · LCSC %s · %s · %s in stock" % (
        tag, line.get("value") or "?", p["mpn"], p.get("manufacturer") or "?",
        p.get("package") or "?", p["lcsc"],
        ("$%.4f at 1 000" % price) if price is not None
        else "price CANNOT DETERMINE — the vendor ladder does not reach 1 000",
        "{:,}".format(p["stock"]) if p.get("stock") is not None else "?")


def halo_part_cell(h):
    """halo's side of a component row, as (headline, detail lines).

    Where halo DELETED a part the headline says so -- putting the surviving
    passive's order code in the headline would read as if halo fitted an
    equivalent, which is the opposite of what happened.
    """
    refs = h.get("refs") or []
    det = []

    if h.get("price_from") == "cost.sounder":
        s = BOM["cost"]["sounder"]["resolved_to"]
        det = ["%s — %s" % (s["mpn"], s["manufacturer"]),
               "Ø%.1f × %.2f mm, %d Hz (%d–%d), %d nF, ≤%d Ω"
               % (s["diameter_mm"], s["thickness_mm"], s["f0_hz"],
                  s["f0_min_hz"], s["f0_max_hz"], s["capacitance_pf"] / 1000,
                  s["resonant_impedance_ohm_max"]),
               "$%.3f at 1 000 · Digi-Key %d + Mouser %d in stock · not on LCSC"
               % (s["usd_per_unit"]["1000"], s["stock"]["Digi-Key"],
                  s["stock"]["Mouser"])]
        return h.get("text") or "LS1", det

    # every distinct BOM line these refdes land on, in board order
    seen, lines = [], []
    for r in refs:
        ln = BY_REF[r]
        key = id(ln)
        if key not in seen:
            seen.append(key)
            lines.append((ln, [x for x in refs if BY_REF[x] is ln]))

    if h.get("class_of"):
        # a CLASS of parts, not one line: count what is actually on the board
        packs, parts = {}, {}
        for ln in BOM["lines"]:
            fp = (ln.get("footprint") or "?")
            packs[fp] = packs.get(fp, 0) + 1
            parts[fp] = parts.get(fp, 0) + len(ln["refs"])
        det.append("counted off spec/bom-resolved.json — BOM lines by package: %s"
                   % ", ".join("%d × %s" % (v, k)
                               for k, v in sorted(packs.items(),
                                                  key=lambda kv: -kv[1])))
        det.append("placed parts by package: %s"
                   % ", ".join("%d × %s" % (v, k)
                               for k, v in sorted(parts.items(),
                                                  key=lambda kv: -kv[1])))
        for ln, rr in lines:
            det.append(_part_line(ln, rr))
        return h["text"], det

    if not refs:
        return h.get("text") or h.get("value") or "—", []

    for ln, rr in lines:
        det.append(_part_line(ln, rr))
    if h.get("note"):
        det.append(h["note"])
    if h.get("text"):
        return h["text"], det
    ln0, rr0 = lines[0]
    p0 = ln0.get("part") or {}
    head = ("%s — %s (%s)" % (", ".join(rr0), p0["mpn"],
                              p0.get("manufacturer") or "?")
            if p0.get("mpn") else
            "%s — %s" % (", ".join(rr0), ln0.get("value") or "?"))
    det = det[1:] if len(lines) == 1 else det
    if len(lines) == 1:
        det.insert(0, "%s · %s · LCSC %s"
                   % (ln0.get("value") or "?", p0.get("package") or "?",
                      p0.get("lcsc") or "no order code"))
        price = (p0.get("price_usd") or {}).get("1000")
        det.insert(1, "%s · %s in stock"
                   % (("$%.4f at 1 000" % price) if price is not None
                      else "price CANNOT DETERMINE",
                      "{:,}".format(p0["stock"]) if p0.get("stock") is not None else "?"))
    return head, det


def deref(measure):
    """Follow a {path, pointer} into a file this repo already measured."""
    d = load(measure["path"])
    for key in measure["pointer"].split("."):
        d = d[key]
    return d


def halo_pcb_cell(h):
    if "measure" in h:
        v = deref(h["measure"])
        fmt = h.get("fmt", "%s")
        if isinstance(v, list):
            txt = fmt % tuple(v)
        elif isinstance(v, dict):
            txt = ("%d footprints · %d vias · %d track segments"
                   % (v["footprints"], v["vias"], v["track_segments"]))
        else:
            txt = fmt % v
        return txt, "measured: %s → %s" % (h["measure"]["path"], h["measure"]["pointer"])
    return h["value"], h.get("note", "")


# ---------------------------------------------------------------- the counts
ORDER = ["SAME", "EQUIVALENT", "DIVERGED", "MISSING", "ADDED", "CANNOT DETERMINE"]
comp_counts = {k: 0 for k in ORDER}
for c in DATA["components"]:
    comp_counts[c["verdict"]] += 1
pcb_counts = {k: 0 for k in ORDER}
for r in DATA["pcb"]:
    pcb_counts[r["verdict"]] += 1

RANKS = ["impossible", "expensive", "cheap"]
by_rank = {k: [] for k in RANKS}
for c in DATA["components"]:
    if c["verdict"] in ("DIVERGED", "MISSING") and c["exact"]["rank"] in RANKS:
        by_rank[c["exact"]["rank"]].append(c)

ident = DATA["bom_identification"]["rows"]
ORDERABLE = sum(1 for r in ident if r["state"] == "ORDERABLE")
AMBIG = sum(1 for r in ident if r["state"] == "AMBIGUOUS")
UNBUY = sum(1 for r in ident if r["state"] == "IDENTIFIED BUT UNBUYABLE")
UNID = sum(1 for r in ident if r["state"] in ("UNIDENTIFIED", "NOT A PART"))
NLINES = len(ident)

FUNC_REPRODUCIBLE = sum(1 for r in ident
                        if r["state"] != "IDENTIFIED BUT UNBUYABLE")

SUMMARY = {
    "schema": "halo/comparison-summary/1",
    "generated": datetime.date.today().isoformat(),
    "commit": rev(),
    "component_rows": len(DATA["components"]),
    "component_counts": comp_counts,
    "pcb_rows": len(DATA["pcb"]),
    "pcb_counts": pcb_counts,
    "exact_recreation_rank_counts": {k: len(v) for k, v in by_rank.items()},
    "airtag_bom_lines": NLINES,
    "orderable": ORDERABLE,
    "ambiguous": AMBIG,
    "identified_but_unbuyable": UNBUY,
    "unidentified": UNID,
    "pct_orderable": round(100.0 * ORDERABLE / NLINES, 1),
    "pct_orderable_incl_ambiguous": round(100.0 * (ORDERABLE + AMBIG) / NLINES, 1),
    "pct_reproducible_by_function": round(100.0 * FUNC_REPRODUCIBLE / NLINES, 1),
    "refs_not_on_board": MISSING_REFS,
    "residual": DATA["residual"],
}

# ---------------------------------------------------------------- the figure
FIG_SPAN_MM = 26.0          # both boards are ~26 mm; the panels frame that square


def figure():
    """Both boards, labelled.

    SCALE, stated rather than assumed. halo's panels are scaled off a
    MEASUREMENT: the Edge.Cuts extent of its own board file, 26.0000 mm on
    the major axis. Apple's front panel is scaled off a CITATION: O'Flynn
    named his crop `frontside-26mm-cropped` and images/airtag/CATALOG.md
    records it as "cropped to the ~26 mm PCB diameter". The tilde is his and
    it is carried through. Apple's BACK photograph has no scale reference of
    any kind and none is invented for it.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        import numpy as np
        from PIL import Image
    except ImportError as exc:
        print("CANNOT DETERMINE: no figure — %s" % exc)
        return None

    INK, DIM, LINE = "#16181d", "#5c6370", "#c8ced6"
    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Helvetica Neue", "Helvetica", "DejaVu Sans"],
                         "figure.facecolor": "white", "savefig.facecolor": "white"})
    N = 960                      # every scaled panel renders at this pixel size

    def green_bbox(path):
        a = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
        g = a[:, :, 1] - (a[:, :, 0] + a[:, :, 2]) / 2.0
        ys, xs = np.where(g > 6)
        if len(xs) == 0:
            return None
        return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1

    halo_top_p = os.path.join(ROOT, "out/render/halo_rev_a-top.png")
    halo_bot_p = os.path.join(ROOT, "out/render/halo_rev_a-bottom.png")
    ap_front_p = os.path.join(ROOT, "images/airtag/oflynn-frontside-26mm-cropped.jpg")
    ap_back_p = os.path.join(ROOT, "images/airtag/oflynn-backside-fullres.jpeg")
    for p in (halo_top_p, halo_bot_p, ap_front_p, ap_back_p):
        if not os.path.exists(p):
            print("CANNOT DETERMINE: no figure — missing %s" % p)
            return None

    hb_top, hb_bot = green_bbox(halo_top_p), green_bbox(halo_bot_p)
    if hb_top is None or hb_bot is None:
        print("CANNOT DETERMINE: could not find halo's board outline in its own "
              "render; not drawing a scale comparison")
        return None

    def halo_panel(path, bbox, mirror_x):
        """Crop the render to a FIG_SPAN_MM square centred on the board and
        resize to N. Returns (image, map(x_mm, y_mm) -> (px, py), px_per_mm)."""
        im = Image.open(path).convert("RGB")
        x0, y0, x1, y1 = bbox
        ppm_x = (x1 - x0) / BOARD_MM[0]
        ppm_y = (y1 - y0) / BOARD_MM[1]
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        half = FIG_SPAN_MM / 2.0 * ppm_y
        box = (cx - half, cy - half, cx + half, cy + half)
        crop = im.resize((N, N), Image.LANCZOS, box=box)
        k = N / (2 * half)

        def to_px(x_mm, y_mm):
            ox = x0 + (BOARD_MM[0] - x_mm if mirror_x else x_mm) * ppm_x
            oy = y0 + y_mm * ppm_y
            return (ox - box[0]) * k, (oy - box[1]) * k
        return crop, to_px, N / FIG_SPAN_MM

    def frac_panel(path, resize_to=None):
        """A photograph whose labels are fractions of the whole frame."""
        im = Image.open(path).convert("RGB")
        if resize_to:
            im = im.resize((resize_to, resize_to), Image.LANCZOS)
        w, h = im.size
        return im, (lambda fx, fy: (fx * w, fy * h)), None

    def panel(ax, im, put, labels, title, sub, ppm=None, bar_note=None):
        ax.imshow(im)
        W, H = im.size
        for L in labels:
            px, py = put(*L["_p"])
            lx, ly = L["lx"] * W, L["ly"] * H
            ha = "left" if L["lx"] < 0.5 else "right"
            ax.annotate(L["t"], xy=(px, py), xytext=(lx, ly),
                        fontsize=7.2, color=INK, ha=ha, va="center",
                        bbox=dict(boxstyle="round,pad=0.26", fc="white",
                                  ec=LINE, lw=0.7, alpha=0.94),
                        arrowprops=dict(arrowstyle="-", color="#c0392b", lw=1.0,
                                        shrinkA=0, shrinkB=2))
            ax.plot([px], [py], marker="o", ms=3.2, mfc="#c0392b",
                    mec="white", mew=0.7)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(LINE)
        ax.set_title(title, fontsize=11, color=INK, fontweight="bold", pad=7)
        ax.set_xlabel(sub, fontsize=7.5, color=DIM, labelpad=7)
        if ppm:
            bar = 10.0 * ppm
            yy = H * 0.955
            ax.add_patch(Rectangle((W * 0.035, yy), bar, H * 0.013,
                                   facecolor=INK, edgecolor="none"))
            ax.text(W * 0.035 + bar / 2, yy - H * 0.007, bar_note or "10 mm",
                    ha="center", va="bottom", fontsize=8.2, color=INK,
                    fontweight="bold")

    def prep_halo(labels):
        """Anchor points in board millimetres. Default is the footprint
        origin read out of the .kicad_pcb; `xy_mm` overrides it where the
        origin is not where the thing being pointed at actually is -- BT1's
        origin is the board centre and its three contacts are on the rim."""
        out_l = []
        for L in labels:
            if "xy_mm" in L:
                p_mm = tuple(L["xy_mm"])
            elif L["ref"] in HALO_XY:
                p_mm = HALO_XY[L["ref"]]
            else:
                print("  label skipped, no footprint %s" % L["ref"])
                continue
            d = dict(L)
            d["_p"] = p_mm
            out_l.append(d)
        return out_l

    def prep_frac(labels):
        return [dict(L, _p=(L["x"], L["y"])) for L in labels]

    fig, axes = plt.subplots(2, 2, figsize=(15.4, 16.2), dpi=140)

    bot_im, bot_put, bot_ppm = halo_panel(halo_bot_p, hb_bot, mirror_x=True)
    panel(axes[0][0], bot_im, bot_put, prep_halo(DATA["labels"]["halo_bottom"]),
          "halo rev A — BOTTOM (B.Cu): where the silicon is",
          "SOLID Ø26.00 mm disc, 4 layers, 0.60 mm. Mirrored, as a bottom view is.\n"
          "Every marker is a footprint position read out of "
          "out/verify/halo_rev_a.kicad_pcb in millimetres.",
          ppm=bot_ppm)

    apb, apb_put, _ = frac_panel(ap_back_p)
    panel(axes[0][1], apb, apb_put, prep_frac(DATA["labels"]["apple_back"]),
          "Apple AirTag A2187 — BACK: where the silicon is",
          "ANNULAR board, 0.30 mm. NOT TO SCALE, and not claimed to be: this\n"
          "photograph is oblique and carries no scale reference at all.\n"
          "Colin O'Flynn, CC BY 4.0.",
          ppm=None)

    top_im, top_put, top_ppm = halo_panel(halo_top_p, hb_top, mirror_x=False)
    panel(axes[1][0], top_im, top_put, prep_halo(DATA["labels"]["halo_top"]),
          "halo rev A — TOP (F.Cu): antenna, test access, sounder lands",
          "MEASURED scale: %.1f px/mm off a 26.0000 mm major axis. The minor axis\n"
          "is 25.6138 mm because of three 26° keying notches cut to R12.60."
          % top_ppm, ppm=top_ppm)

    apf, apf_put, _ = frac_panel(ap_front_p, resize_to=N)
    panel(axes[1][1], apf, apf_put, prep_frac(DATA["labels"]["apple_front"]),
          "Apple AirTag A2187 — FRONT: contacts, coil, bulk caps",
          "CITED scale, not measured: O'Flynn's crop is recorded as \u201c~26 mm\u201d\n"
          "and the tilde is his. Same square as the panel to its left, so the two\n"
          "are comparable to the precision anyone has published — no better.\n"
          "Board still on its plastic carrier. Colin O'Flynn, CC BY 4.0.",
          ppm=N / 26.0, bar_note="10 mm (~)")

    fig.suptitle("halo rev A beside the AirTag it is copied from — every label "
                 "this lane could justify, and the ones it could not",
                 fontsize=13.5, y=0.978, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.956))
    name = "fig-boards-labelled.png"
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight")
    plt.close(fig)
    print("  halo panels %.2f px/mm (measured); Apple front %.2f px/mm (cited '~26 mm'); "
          "Apple back not to scale" % (top_ppm, N / 26.0))
    return name


# footprint positions, read once out of the board file
def read_footprints():
    import re
    p = os.path.join(ROOT, "out/verify/halo_rev_a.kicad_pcb")
    if not os.path.exists(p):
        return {}
    t = open(p, encoding="utf-8", errors="replace").read()
    pos = {}
    for m in re.finditer(r"\(footprint ", t):
        chunk = t[m.start():m.start() + 3000]
        at = re.search(r"\(at ([-\d.]+) ([-\d.]+)", chunk)
        ref = re.search(r'\(property "Reference" "([^"]+)"', chunk)
        if at and ref:
            pos[ref.group(1)] = (float(at.group(1)), float(at.group(2)))
    return pos


HALO_XY = read_footprints()

# ---------------------------------------------------------------- markdown
def md():
    L = []
    a = L.append
    a("# halo vs the Apple AirTag — every row, side by side")
    a("")
    a("*Generated %s from `spec/comparison.json` by `tools/gen_comparison.py`, "
      "at commit `%s`. Nothing on this page is hand-typed: halo's parts, prices "
      "and stock come out of `spec/bom-resolved.json`, halo's board numbers out "
      "of `out/verify/dfm-jlc-4layer.json`, and Apple's side is transcribed from "
      "`research/01-airtag-hardware.md` with each confidence tag carried through "
      "rather than laundered into fact.*" % (SUMMARY["generated"], SUMMARY["commit"]))
    a("")
    a("> %s" % DATA["leif_verbatim"])
    a("")
    a("**That last sentence is answered in section 4, and the answer is not the "
      "one the dossier's headline suggests.** The dossier says a clone can "
      "reproduce about 95 percent of the AirTag one-for-one. That is true *by "
      "function*. **By part number it is %s percent.** %d of the %d lines in "
      "Apple's bill of materials have **no manufacturer part number in the public "
      "record at all**; one more — the ultra-wideband module everyone names as "
      "the wall — is identified and cannot be bought; and two more are named "
      "differently by two reputable teardowns. So the U1 is one of **%d** lines "
      "that block an exact copy, and it is not the hardest of them: it is at "
      "least *known*."
      % (SUMMARY["pct_orderable"], UNID, NLINES, UNID + UNBUY))
    a("")
    a("## The counts")
    a("")
    a("| | rows | SAME | EQUIVALENT | DIVERGED | MISSING | ADDED | CANNOT DETERMINE |")
    a("|---|--:|--:|--:|--:|--:|--:|--:|")
    a("| component comparison | %d | %d | %d | %d | %d | %d | %d |"
      % (len(DATA["components"]), comp_counts["SAME"], comp_counts["EQUIVALENT"],
         comp_counts["DIVERGED"], comp_counts["MISSING"], comp_counts["ADDED"],
         comp_counts["CANNOT DETERMINE"]))
    a("| PCB comparison | %d | %d | %d | %d | %d | %d | %d |"
      % (len(DATA["pcb"]), pcb_counts["SAME"], pcb_counts["EQUIVALENT"],
         pcb_counts["DIVERGED"], pcb_counts["MISSING"], pcb_counts["ADDED"],
         pcb_counts["CANNOT DETERMINE"]))
    a("")
    a("**Verdicts mean exactly this:**")
    a("")
    for k, v in DATA["verdict_vocabulary"]:
        a("- **%s** — %s" % (k, v))
    a("")

    a("## 1 · The component comparison")
    a("")
    a("One row per function. Every line in the AirTag bill of materials is here, "
      "including the ones halo deleted.")
    a("")
    a("| # | function | Apple's part | halo's part | verdict | decision · why |")
    a("|--:|---|---|---|---|---|")
    for c in DATA["components"]:
        ap = c["apple"]
        acell = "**%s**<br>%s<br>*pkg:* %s<br>*marking:* %s<br>`%s` · %s" % (
            ap["part"], "" if not ap.get("refdes") or ap["refdes"] == "—" else
            "*Apple ref %s, %s side*" % (ap["refdes"], ap["side"]),
            ap["package"], ap["marking"], ap["conf"], ap["source"])
        head, det = halo_part_cell(c["halo"])
        hcell = "**%s**" % head + ("<br>" + "<br>".join(det) if det else "")
        why = c["why"]
        if c.get("decision"):
            why = "**%s** — %s" % (c["decision"], why)
        if c.get("inconsistency"):
            why += "<br><br>**INCONSISTENCY FOUND:** " + c["inconsistency"]
        a("| %d | **%s** | %s | %s | **%s** | %s |"
          % (c["n"], c["function"], acell.replace("\n", " "),
             hcell.replace("\n", " "), c["verdict"], why.replace("\n", " ")))
    a("")

    a("## 2 · The PCB comparison")
    a("")
    a("| # | property | Apple | halo | verdict | decision · why |")
    a("|--:|---|---|---|---|---|")
    for r in DATA["pcb"]:
        hv, hn = halo_pcb_cell(r["halo"])
        why = r["why"]
        if r.get("decision"):
            why = "**%s** — %s" % (r["decision"], why)
        a("| %d | **%s** | %s<br>`%s` · %s | **%s**<br>*%s* | **%s** | %s |"
          % (r["n"], r["property"], r["apple"]["value"], r["apple"]["conf"],
             r["apple"]["source"], hv, hn, r["verdict"], why))
    a("")

    a("## 3 · Side by side, labelled")
    a("")
    a("![halo rev A beside the AirTag](../out/comparison/%s)" % FIGNAME
      if FIGNAME else "*No figure: %s*" % "the generator could not establish a scale")
    a("")
    a(DATA["labels"]["scale_note"])
    a("")
    a("### What this lane can actually find in Apple's photographs")
    a("")
    a(DATA["locate"]["note"])
    a("")
    a("| part | verdict | evidence |")
    a("|---|---|---|")
    for r in DATA["locate"]["rows"]:
        a("| %s | **%s** | %s |" % (r["part"], r["verdict"], r["evidence"]))
    a("")
    nloc = sum(1 for r in DATA["locate"]["rows"] if r["verdict"].startswith("LOCATED"))
    ncan = sum(1 for r in DATA["locate"]["rows"] if r["verdict"].startswith("CANNOT"))
    a("**%d of %d located, %d cannot be located.** The four ICs that cannot be "
      "found — the flash, the amplifier, the op-amp and the load switch — are "
      "exactly the four halo deleted, so nobody has ever pointed at them in a "
      "photograph either. Their identification rests entirely on iFixit and "
      "Catley having had the physical part."
      % (nloc, len(DATA["locate"]["rows"]), ncan))
    a("")

    a("## 4 · What recreating it exactly would take")
    a("")
    a("Leif asked for this directly. Each DIVERGED and MISSING row below is "
      "ranked on one question — what would it cost to match Apple instead?")
    a("")
    for rank, title in [("impossible", "Impossible — the part cannot be bought, or cannot be identified"),
                        ("expensive", "Expensive — buyable in principle, and it "
                                      "would cost the stack, the tooling or both"),
                        ("cheap", "Cheap — the part is on a shelf and we chose "
                                  "otherwise, for reasons that are yours to overrule")]:
        rows = by_rank[rank]
        a("### %s — %d rows" % (title, len(rows)))
        a("")
        a("| # | function | buyable? | what it costs the stack | money | schedule | what matching Apple would LOSE |")
        a("|--:|---|---|---|---|---|---|")
        for c in rows:
            x = c["exact"]
            a("| %d | **%s** | %s | %s | %s | %s | %s |"
              % (c["n"], c["function"], x["buyable"], x["stack"], x["cost"],
                 x["schedule"], x["loses"]))
        a("")

    a("### The honest ceiling: can you order an AirTag's bill of materials?")
    a("")
    a(DATA["bom_identification"]["note"])
    a("")
    a("| line | can you order it? | why |")
    a("|---|---|---|")
    for r in ident:
        a("| %s | **%s** | %s |" % (r["line"], r["state"], r["why"]))
    a("")
    a("**%d of %d lines are orderable today (%s percent).** Allow the two lines "
      "where two reputable teardowns name different part numbers and it is %d of "
      "%d (%s percent). **%d line is identified and cannot be bought at any "
      "price** — the Apple U1. **%d lines have no public part number at all**: an "
      "exact recreation would have to measure them off a physical AirTag."
      % (ORDERABLE, NLINES, SUMMARY["pct_orderable"], ORDERABLE + AMBIG, NLINES,
         SUMMARY["pct_orderable_incl_ambiguous"], UNBUY, UNID))
    a("")
    a("**So the two numbers, both true, measuring different things:**")
    a("")
    a("| question | answer |")
    a("|---|--:|")
    a("| Could a clone reproduce the AirTag's FUNCTIONS from catalogue parts? | **%s %%** of lines (%d of %d) — everything but the U1 |"
      % (SUMMARY["pct_reproducible_by_function"], FUNC_REPRODUCIBLE, NLINES))
    a("| Could you place an ORDER for the AirTag's actual bill of materials? | **%s %%** of lines (%d of %d) |"
      % (SUMMARY["pct_orderable"], ORDERABLE, NLINES))
    a("")
    a("### The residual, named")
    a("")
    for r in DATA["residual"]:
        a("- %s" % r)
    a("")
    a("*Regenerate with `python3 tools/gen_comparison.py`. Counts in "
      "`out/comparison/comparison-summary.json`.*")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- html
CSS = """
:root{--ink:#16181d;--dim:#5c6370;--line:#dfe3e8;--bg:#fff;--same:#0a7d33;--equiv:#2b6cb0;
 --div:#a86500;--miss:#a11;--add:#6b3fa0;--cd:#7a4fb5}
@media(prefers-color-scheme:dark){:root{--ink:#e8eaed;--dim:#9aa2ad;--line:#2c313a;--bg:#14161a;
 --same:#4ec26f;--equiv:#6fb0e8;--div:#e0a233;--miss:#f0736a;--add:#b490e0;--cd:#b490e0}}
*{box-sizing:border-box}
body{margin:0;padding:2.5rem 1.5rem 6rem;background:var(--bg);color:var(--ink);
 font:16px/1.65 -apple-system,"Helvetica Neue",sans-serif}
main{max-width:82rem;margin:0 auto}
h1{font-size:2rem;margin:0 0 .2rem;letter-spacing:-.02em}
h2{font-size:1.3rem;margin:3.2rem 0 .75rem;padding-bottom:.4rem;border-bottom:1px solid var(--line)}
h3{font-size:1.02rem;margin:2rem 0 .4rem}
.sub{color:var(--dim);margin:0 0 1.5rem}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.83rem}
th,td{text-align:left;vertical-align:top;padding:.5rem .6rem;border-bottom:1px solid var(--line)}
th{font-weight:600;color:var(--dim);font-size:.72rem;text-transform:uppercase;letter-spacing:.05em}
td.n{width:2rem;color:var(--dim);font-variant-numeric:tabular-nums}
.badge{display:inline-block;font-size:.68rem;font-weight:700;letter-spacing:.05em;padding:.12rem .4rem;
 border-radius:3px;border:1px solid currentColor;white-space:nowrap}
.SAME{color:var(--same)} .EQUIVALENT{color:var(--equiv)} .DIVERGED{color:var(--div)}
.MISSING{color:var(--miss)} .ADDED{color:var(--add)} .CD{color:var(--cd)}
code,.mono{font:.85em ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim);word-break:break-word}
blockquote{margin:1rem 0;padding:.8rem 1.1rem;border-left:3px solid var(--line);
 background:rgba(127,127,127,.06)}
.meta{color:var(--dim);font-size:.8rem;margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line)}
ul{padding-left:1.2rem} li{margin:.35rem 0}
img{max-width:100%;border:1px solid var(--line);border-radius:8px;background:#fff}
.tally{font-size:.9rem}
.big{font-size:1.05rem;padding:1rem 1.2rem;border:1px solid var(--line);border-radius:8px;
 background:rgba(127,127,127,.05);margin:1.4rem 0}
.rank-impossible{color:var(--miss);font-weight:700}
.rank-expensive{color:var(--div);font-weight:700}
.rank-cheap{color:var(--same);font-weight:700}
"""


def badge(s):
    cls = "CD" if s == "CANNOT DETERMINE" else s
    return '<span class="badge %s">%s</span>' % (cls, E(s))


def htmlpage():
    P = []
    a = P.append
    a('<!doctype html><html lang="en"><meta charset="utf-8">')
    a('<meta name="viewport" content="width=device-width,initial-scale=1">')
    a('<title>halo vs the Apple AirTag — the comparison</title>')
    a("<style>%s</style><main>" % CSS)
    a("<h1>halo vs the Apple AirTag</h1>")
    a('<p class="sub">Every row, side by side · generated %s · commit '
      '<span class="mono">%s</span> · lane C1</p>' % (SUMMARY["generated"], SUMMARY["commit"]))
    a("<blockquote>%s</blockquote>" % E(DATA["leif_verbatim"]))
    a('<div class="big"><b>The dossier says a clone can reproduce about 95 %% of '
      'the AirTag one-for-one. That is true <i>by function</i>. By <b>part number</b> '
      'it is <b>%s %%</b>.</b> %d of the %d lines in Apple\'s bill of materials have '
      '<b>no manufacturer part number in the public record at all</b>; one more — the '
      'ultra-wideband module everyone names as the wall — is identified and cannot be '
      'bought; two more are named differently by two reputable teardowns. The U1 is '
      'one of <b>%d</b> lines that block an exact copy, and it is not the hardest of '
      'them: it is at least <i>known</i>. Section 4 has the table.</div>'
      % (SUMMARY["pct_orderable"], UNID, NLINES, UNID + UNBUY))

    a("<h2>The counts</h2>")
    a('<table class="tally"><tr><th></th><th>rows</th>')
    for k in ORDER:
        a("<th>%s</th>" % E(k))
    a("</tr>")
    for name, n, cc in [("component comparison", len(DATA["components"]), comp_counts),
                        ("PCB comparison", len(DATA["pcb"]), pcb_counts)]:
        a("<tr><td><b>%s</b></td><td>%d</td>" % (E(name), n))
        for k in ORDER:
            a("<td>%d</td>" % cc[k])
        a("</tr>")
    a("</table><ul>")
    for k, v in DATA["verdict_vocabulary"]:
        a("<li>%s — %s</li>" % (badge(k), E(v)))
    a("</ul>")

    a("<h2>1 · The component comparison</h2>")
    a("<p>One row per function. Every line in the AirTag bill of materials is "
      "here, including the ones halo deleted.</p>")
    a("<table><tr><th>#</th><th>function</th><th>Apple's part</th>"
      "<th>halo's part</th><th>verdict</th><th>decision &middot; why</th></tr>")
    for c in DATA["components"]:
        ap = c["apple"]
        head, det = halo_part_cell(c["halo"])
        acell = "<b>%s</b>" % E(ap["part"])
        if ap.get("refdes") and ap["refdes"] != "—":
            acell += "<br><span class=mono>Apple ref %s &middot; %s side</span>" % (
                E(ap["refdes"]), E(ap["side"]))
        acell += "<br><span class=mono>pkg: %s</span>" % E(ap["package"])
        acell += "<br><span class=mono>marking: %s</span>" % E(ap["marking"])
        acell += "<br><span class=mono>[%s] %s</span>" % (E(ap["conf"]), E(ap["source"]))
        hcell = "<b>%s</b>" % E(head)
        for d in det:
            hcell += "<br><span class=mono>%s</span>" % E(d)
        why = E(c["why"])
        if c.get("decision"):
            why = "<b>%s</b> — %s" % (E(c["decision"]), why)
        if c.get("inconsistency"):
            why += "<br><br><b>INCONSISTENCY FOUND:</b> " + E(c["inconsistency"])
        a("<tr><td class=n>%d</td><td><b>%s</b></td><td>%s</td><td>%s</td>"
          "<td>%s</td><td>%s</td></tr>"
          % (c["n"], E(c["function"]), acell, hcell, badge(c["verdict"]), why))
    a("</table>")

    a("<h2>2 · The PCB comparison</h2>")
    a("<table><tr><th>#</th><th>property</th><th>Apple</th><th>halo</th>"
      "<th>verdict</th><th>decision &middot; why</th></tr>")
    for r in DATA["pcb"]:
        hv, hn = halo_pcb_cell(r["halo"])
        why = E(r["why"])
        if r.get("decision"):
            why = "<b>%s</b> — %s" % (E(r["decision"]), why)
        a("<tr><td class=n>%d</td><td><b>%s</b></td>"
          "<td>%s<br><span class=mono>[%s] %s</span></td>"
          "<td><b>%s</b><br><span class=mono>%s</span></td><td>%s</td><td>%s</td></tr>"
          % (r["n"], E(r["property"]), E(r["apple"]["value"]), E(r["apple"]["conf"]),
             E(r["apple"]["source"]), E(hv), E(hn), badge(r["verdict"]), why))
    a("</table>")

    a("<h2>3 · Side by side, labelled</h2>")
    if FIGNAME:
        a('<p><img src="%s" alt="halo rev A beside the AirTag, labelled"></p>' % FIGNAME)
    else:
        a("<p><b>CANNOT DETERMINE</b> — no figure was produced; see the "
          "generator's output for the reason.</p>")
    a("<p>%s</p>" % E(DATA["labels"]["scale_note"]))
    a("<h3>What this lane can actually find in Apple's photographs</h3>")
    a("<p>%s</p>" % E(DATA["locate"]["note"]))
    a("<table><tr><th>part</th><th>verdict</th><th>evidence</th></tr>")
    for r in DATA["locate"]["rows"]:
        a("<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>"
          % (E(r["part"]), E(r["verdict"]), E(r["evidence"])))
    a("</table>")
    nloc = sum(1 for r in DATA["locate"]["rows"] if r["verdict"].startswith("LOCATED"))
    ncan = sum(1 for r in DATA["locate"]["rows"] if r["verdict"].startswith("CANNOT"))
    a("<p><b>%d of %d located, %d cannot be located.</b> The four ICs that cannot "
      "be found — the flash, the amplifier, the op-amp and the load switch — are "
      "exactly the four halo deleted, so nobody has ever pointed at them in a "
      "photograph either. Their identification rests entirely on iFixit and "
      "Catley having had the physical part.</p>"
      % (nloc, len(DATA["locate"]["rows"]), ncan))

    a("<h2>4 · What recreating it exactly would take</h2>")
    a("<p>Leif asked for this directly. Each DIVERGED and MISSING row is ranked "
      "on one question — what would it cost to match Apple instead?</p>")
    for rank, title in [("impossible", "Impossible — the part cannot be bought, or cannot be identified"),
                        ("expensive", "Expensive — buyable in principle, and it "
                                      "would cost the stack, the tooling or both"),
                        ("cheap", "Cheap — the part is on a shelf and we chose "
                                  "otherwise, for reasons that are yours to overrule")]:
        rows = by_rank[rank]
        a('<h3><span class="rank-%s">%s</span> — %d rows</h3>' % (rank, E(title), len(rows)))
        a("<table><tr><th>#</th><th>function</th><th>buyable?</th>"
          "<th>what it costs the stack</th><th>money</th><th>schedule</th>"
          "<th>what matching Apple would LOSE</th></tr>")
        for c in rows:
            x = c["exact"]
            a("<tr><td class=n>%d</td><td><b>%s</b></td><td>%s</td><td>%s</td>"
              "<td>%s</td><td>%s</td><td>%s</td></tr>"
              % (c["n"], E(c["function"]), E(x["buyable"]), E(x["stack"]),
                 E(x["cost"]), E(x["schedule"]), E(x["loses"])))
        a("</table>")

    a("<h3>The honest ceiling: can you order an AirTag's bill of materials?</h3>")
    a("<p>%s</p>" % E(DATA["bom_identification"]["note"]))
    a("<table><tr><th>line</th><th>can you order it?</th><th>why</th></tr>")
    for r in ident:
        a("<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>"
          % (E(r["line"]), E(r["state"]), E(r["why"])))
    a("</table>")
    a('<div class="big"><b>%d of %d lines are orderable today (%s %%).</b> Allow the '
      'two lines where two reputable teardowns name different part numbers and it is '
      '%d of %d (%s %%). <b>%d line is identified and cannot be bought at any price</b> '
      '— the Apple U1. <b>%d lines have no public part number at all</b>: an exact '
      'recreation would have to measure them off a physical AirTag.</div>'
      % (ORDERABLE, NLINES, SUMMARY["pct_orderable"], ORDERABLE + AMBIG, NLINES,
         SUMMARY["pct_orderable_incl_ambiguous"], UNBUY, UNID))
    a("<table><tr><th>question</th><th>answer</th></tr>")
    a("<tr><td>Could a clone reproduce the AirTag's <b>functions</b> from catalogue "
      "parts?</td><td><b>%s %%</b> of lines (%d of %d) — everything but the U1</td></tr>"
      % (SUMMARY["pct_reproducible_by_function"], FUNC_REPRODUCIBLE, NLINES))
    a("<tr><td>Could you place an <b>order</b> for the AirTag's actual bill of "
      "materials?</td><td><b>%s %%</b> of lines (%d of %d)</td></tr>"
      % (SUMMARY["pct_orderable"], ORDERABLE, NLINES))
    a("</table>")
    a("<h3>The residual, named</h3><ul>")
    for r in DATA["residual"]:
        a("<li>%s</li>" % E(r))
    a("</ul>")

    a('<p class="meta">Generated from <code>spec/comparison.json</code>, '
      '<code>spec/bom-resolved.json</code> and '
      '<code>out/verify/dfm-jlc-4layer.json</code> by '
      '<code>tools/gen_comparison.py</code>. Apple-side facts are transcribed '
      'from <code>research/01-airtag-hardware.md</code> with their confidence '
      'tags intact. Photographs: Colin O\'Flynn (CC BY 4.0) and the FCC public '
      'record for BCGA2187 — see <code>images/airtag/CATALOG.md</code>.</p>')
    a("</main></html>")
    return "\n".join(P)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if MISSING_REFS:
        print("FAIL: comparison rows point at refdes that are not on the board:")
        for n, r in MISSING_REFS:
            print("  row %d -> %s" % (n, r))
        sys.exit(1)
    FIGNAME = figure()
    with open(os.path.join(ROOT, "docs", "COMPARISON.md"), "w", encoding="utf-8") as fh:
        fh.write(md())
    with open(os.path.join(OUT, "INDEX.html"), "w", encoding="utf-8") as fh:
        fh.write(htmlpage())
    with open(os.path.join(OUT, "comparison-summary.json"), "w", encoding="utf-8") as fh:
        json.dump(SUMMARY, fh, indent=1)
        fh.write("\n")
    print("wrote docs/COMPARISON.md, out/comparison/INDEX.html, "
          "out/comparison/comparison-summary.json")
    print("components: %d rows — %s"
          % (len(DATA["components"]),
             " · ".join("%d %s" % (comp_counts[k], k) for k in ORDER if comp_counts[k])))
    print("pcb:        %d rows — %s"
          % (len(DATA["pcb"]),
             " · ".join("%d %s" % (pcb_counts[k], k) for k in ORDER if pcb_counts[k])))
    print("exact recreation: %s"
          % " · ".join("%d %s" % (len(by_rank[k]), k) for k in RANKS))
    print("AirTag BOM: %d of %d lines orderable (%s%%), %d unidentified, "
          "%d identified but unbuyable"
          % (ORDERABLE, NLINES, SUMMARY["pct_orderable"], UNID, UNBUY))
