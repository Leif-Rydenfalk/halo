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


def size_str(sz):
    if not isinstance(sz, dict):
        return esc(sz)
    v, verdict = sz.get("value"), sz.get("verdict", "")
    if v is None:
        return f"**{esc(verdict)}**"
    if isinstance(v, dict):
        return "**" + esc(verdict.split(",")[0]) + "** — " + \
               ", ".join(f"{k} {vv} mm" for k, vv in v.items())
    return f"**{esc(verdict)}** — {esc(v)}"


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
        if isinstance(ln.get("size_mm"), dict) and ln["size_mm"].get("ratios_to_datum"):
            w(f"- **ratios to the datum** — {ln['size_mm']['ratios_to_datum']}")
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
        w(f"- **Replica verdict** — {ln['replica_verdict']}\n")
    w("---\n")
    w("## Sources, and what each one is\n")
    for k, v in d["sources"].items():
        w(f"- **`{k}`** — {v}")
    w("")
    open(OUT, "w").write("\n".join(L))
    print(f"wrote {OUT}  ({len(lines)} lines, {len(L)} md lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
