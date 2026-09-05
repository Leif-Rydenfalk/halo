#!/usr/bin/env python3
"""b_bom_render.py — render bom/bom.json to bom/BOM-RECONSTRUCTED.md.

bom.json is the source of truth; the markdown is generated so the two cannot
drift. Editing BOM-RECONSTRUCTED.md by hand is a defect — it will be
overwritten. Exit 0 on success, 2 if there is nothing to render.
"""
import json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "bom", "bom.json")
OUT = os.path.join(HERE, "bom", "BOM-RECONSTRUCTED.md")


def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def unit_for(key):
    """The unit a field's NAME says it is in.

    L8 2026-09-05: this renderer used to append " mm" to every value in a size
    block, so `long_px 355.1 mm` and `aspect 1.087 mm` and
    `short_side_genuine_px [63.6, 84.2] mm` were all published. A pixel count
    labelled as millimetres is exactly the kind of number that becomes "what
    Apple did" downstream. The unit now comes from the field name and unknown
    fields get NO unit rather than a plausible one.
    """
    k = str(key)
    if k.endswith("px_per_mm"):          # BEFORE the _mm test, or "106.313 mm"
        return " px/mm"
    if k.endswith("_mm2") or k.endswith("_mm^2"):
        return " mm^2"
    if k.endswith("_mm") or k.endswith("_mm_lower_bound"):
        return " mm"
    if k.endswith("_px") or k.endswith("_px_lower_bound"):
        return " px"
    if k.endswith("_deg"):
        return " deg"
    return ""


def val_str(v, key=""):
    u = unit_for(key)
    if isinstance(v, list):
        if len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
            return f"{v[0]}–{v[1]}{u}"
        return esc(v)
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k} {val_str(vv, k)}" for k, vv in v.items()) + "}"
    if v is None:
        return "CANNOT DETERMINE"
    return f"{esc(v)}{u}"


def size_str(sz):
    if not isinstance(sz, dict):
        return esc(sz)
    v, verdict = sz.get("value"), sz.get("verdict", "")
    if v is None:
        return f"**{esc(verdict)}**"
    if isinstance(v, dict):
        return "**" + esc(verdict.split(",")[0]) + "** — " + \
               ", ".join(f"{k} {val_str(vv, k)}" for k, vv in v.items())
    return f"**{esc(verdict)}** — {esc(v)}"


def render_block(w, obj, depth=0):
    """Write an arbitrary nested block as a bullet list, so nothing is dropped."""
    pad = "  " * depth
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                w(f"{pad}- **{esc(k)}**")
                render_block(w, v, depth + 1)
            else:
                w(f"{pad}- **{esc(k)}** — {val_str(v, k)}")
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)):
                render_block(w, v, depth)
            else:
                w(f"{pad}- {esc(v)}")
    else:
        w(f"{pad}- {esc(obj)}")


def main():
    if not os.path.exists(SRC):
        print("CANNOT DETERMINE — no bom.json")
        return 2
    d = json.load(open(SRC))
    lines = d["lines"]
    L = []
    w = L.append
    w("# BOM-RECONSTRUCTED — every line of the AirTag's bill of materials\n")
    w("<!-- GENERATED FILE. Source of truth is bom/bom.json; regenerate with")
    w("     tools/b_bom_render.py. Hand edits here will be overwritten. -->\n")
    w(f"*{d['lane']}, {d['written']}. {d['document']}.*\n")
    w(f"**Status:** {d['status']}\n")
    w("**Checked by** `tools/b_bom_check.py` — six rules, each watched failing on")
    w("purpose by `--self-test`. Exit code is the verdict: 0 PASS, 1 FAIL,")
    w("2 CANNOT DETERMINE.\n")
    w("---\n")
    w("## Read this before the table\n")
    for k, v in d["conventions"].items():
        w(f"**{k.replace('_', ' ')}** — {v}\n")
    w("**Confidence scale**\n")
    for k, v in d["confidence_scale"].items():
        w(f"- **{k}** — {v}")
    w("")
    w(f"**The rule that shapes this document:** {d['evidence_class_rule']}\n")
    w("---\n")
    w("## The table\n")
    w("| ref | function | part | package | size | marking READ | seen? | confidence |")
    w("|---|---|---|---|---|---|---|---|")
    for ln in lines:
        mk = ln.get("marking", {})
        txt = mk.get("text", "")
        seen = "SEEN" if "SEEN" in str(ln.get("evidence_class", "")).upper() else "cited"
        w(f"| **{esc(ln['ref'])}** | {esc(ln['function'])[:80]} | {esc(ln['part'])} "
          f"| {esc(ln['package'])[:70]} | {size_str(ln.get('size_mm'))} "
          f"| `{esc(txt)}` | {seen} | {esc(ln['confidence'])[:60]} |")
    w("")
    LINE_KEYS = {"ref", "new_in_this_document", "function", "part", "package",
                 "size_mm", "marking", "locatable", "evidence_class", "confidence",
                 "marking_establishes", "marking_does_not_establish", "primary_quote",
                 "gain_measured", "would_settle_it", "contradicts", "open_question",
                 "would_settle_the_open_question", "rejected", "replica_verdict"}
    all_line_keys = set()
    for ln in lines:
        all_line_keys.update(ln.keys())
    dropped_line_keys = all_line_keys - LINE_KEYS
    w("---\n")
    w("## Every line in full\n")
    for ln in lines:
        w(f"### {ln['ref']} — {ln['function']}"
          + ("  *(added by this lane; not in REFERENCE-TEARDOWN)*"
             if ln.get("new_in_this_document") else "") + "\n")
        w(f"- **part** — {ln['part']}")
        w(f"- **package** — {ln['package']}")
        w(f"- **size** — {size_str(ln.get('size_mm'))}"
          + (f"  \n  {ln['size_mm'].get('note')}"
             if isinstance(ln.get("size_mm"), dict) and ln["size_mm"].get("note") else ""))
        # every OTHER key of the size block, generically — it used to be dropped
        if isinstance(ln.get("size_mm"), dict):
            extra = {k: v for k, v in ln["size_mm"].items()
                     if k not in ("value", "verdict", "note")}
            if extra:
                render_block(w, extra, 1)
        mk = ln.get("marking", {})
        w(f"- **marking** — `{mk.get('text')}`"
          + (f", read by {mk.get('read_by')}" if mk.get("read_by") else ""))
        if mk.get("legibility"):
            w(f"  - *legibility* — {mk['legibility']}")
        w(f"- **locatable in a photograph** — {ln['locatable']}")
        w(f"- **evidence class** — {ln['evidence_class']}")
        w(f"- **confidence** — {ln['confidence']}")
        w(f"- **what the marking establishes** — {ln['marking_establishes']}")
        w(f"- **what it does NOT establish** — {ln['marking_does_not_establish']}")
        if ln.get("primary_quote"):
            w(f"- **primary quote** — {ln['primary_quote']}")
        if ln.get("gain_measured"):
            w(f"- **measured gain** — {ln['gain_measured']}")
        w(f"- **what would settle it** — {ln['would_settle_it']}")
        if ln.get("contradicts"):
            w(f"- **⚠ contradicts an existing document** — {ln['contradicts']}")
        if ln.get("open_question"):
            w(f"- **open question** — {ln['open_question']}")
        if ln.get("would_settle_the_open_question"):
            w(f"  - *what would settle it* — {ln['would_settle_the_open_question']}")
        if ln.get("rejected"):
            w("- **considered and rejected**")
            for r in ln["rejected"]:
                w(f"  - *{r['candidate']}* (source: {r['source']}) — {r['why_rejected']}")
        w(f"- **Replica verdict** — {ln['replica_verdict']}")
        # Any key of this LINE the renderer does not know about, generically. The
        # top-level coverage check below caught `ruler` being dropped; the same defect
        # exists one level down, and it swallowed J1's whole family_test block on the
        # first run after it was written. L8 2026-09-05.
        extra_ln = {k: v for k, v in ln.items() if k not in LINE_KEYS}
        if extra_ln:
            render_block(w, extra_ln, 0)
            dropped_line_keys.difference_update(extra_ln)
        w("")
    w("---\n")
    # Every remaining top-level block, in the file's own order. A renderer that
    # silently drops content from its source of truth is not a projection of it:
    # the `ruler` block - the basis of every millimetre in the file - was dropped
    # entirely until 2026-09-05, and nothing said so.
    HANDLED = {"schema_version", "document", "lane", "written", "status",
               "conventions", "confidence_scale", "evidence_class_rule",
               "sources", "lines"}
    rendered = set(HANDLED)
    for k, v in d.items():
        if k in HANDLED:
            continue
        w(f"## {k.replace('_', ' ')}\n")
        render_block(w, v)
        w("")
        w("---\n")
        rendered.add(k)
    w("## Sources, and what each one is\n")
    for k, v in d["sources"].items():
        w(f"- **`{k}`** — {v}")
    w("")
    open(OUT, "w").write("\n".join(L))
    dropped = sorted(set(d) - rendered) + sorted(f"line key: {k}" for k in dropped_line_keys)
    print(f"wrote {OUT}  ({len(lines)} lines, {len(L)} md lines)")
    if dropped:
        print(f"  FAIL — these top-level blocks of bom.json were NOT rendered and "
              f"the markdown therefore misrepresents the source of truth: {dropped}")
        return 1
    print(f"  coverage: {len(rendered)}/{len(d)} top-level blocks and "
          f"{len(all_line_keys)}/{len(all_line_keys)} distinct line keys rendered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
