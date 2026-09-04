#!/usr/bin/env python3
"""Generate the concept portfolio from spec/concepts.json.

Writes, and nothing in any of them is hand-typed:

    docs/concepts/README.md          the portfolio index
    docs/concepts/<id>-<slug>.md     one file per concept
    out/concepts/INDEX.html          the page

Lane R1. Style follows tools/gen_release_pack.py: one JSON source of truth,
one generator, no HTML anywhere else in the repo.

Exit codes, deliver-style:
    0  every concept carries a verdict, a reason, an experiment and >=1 source
    1  a concept is malformed (missing a required field)
    2  a concept is SPECULATIVE with no "what would settle it" — the one
       failure mode docs/TOOLS-THAT-LIE.md exists to prevent
"""
import datetime
import html
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "spec" / "concepts.json"
DOCS = ROOT / "docs" / "concepts"
OUT = ROOT / "out" / "concepts"
E = html.escape

VERDICTS = ("PROVEN", "PLAUSIBLE", "SPECULATIVE")
REQUIRED = ("id", "slug", "title", "one_line", "family", "what_it_is",
            "why_it_beats", "verdict", "verdict_reason", "cost", "breaks",
            "evidence", "smallest_experiment", "value", "effort")
COST_KEYS = ("money", "current", "size", "complexity")


def rev():
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                           capture_output=True, text=True)
        return r.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def check(data):
    """Refuse to publish a portfolio that breaks its own rules. Returns exit code."""
    problems, refusals = [], []
    seen = set()
    for c in data["concepts"]:
        cid = c.get("id", "<no id>")
        for k in REQUIRED:
            if k not in c or c[k] in (None, "", [], {}):
                problems.append(f"{cid}: missing required field {k!r}")
        if cid in seen:
            problems.append(f"{cid}: duplicate id")
        seen.add(cid)
        if c.get("verdict") not in VERDICTS:
            problems.append(f"{cid}: verdict {c.get('verdict')!r} is not one of {VERDICTS}")
        for k in COST_KEYS:
            if k not in c.get("cost", {}):
                problems.append(f"{cid}: cost is missing {k!r}")
        if not c.get("evidence"):
            problems.append(f"{cid}: no evidence rows at all")
        for i, ev in enumerate(c.get("evidence", [])):
            for k in ("claim", "source", "date", "confidence"):
                if not ev.get(k):
                    problems.append(f"{cid}: evidence[{i}] missing {k!r}")
        if not str(c.get("smallest_experiment", "")).strip():
            refusals.append(f"{cid}: no experiment that would settle it")
        if c.get("verdict") == "SPECULATIVE" and not c.get("evidence"):
            refusals.append(f"{cid}: SPECULATIVE with nothing said about how to settle it")
        if not isinstance(c.get("value"), int) or not 1 <= c["value"] <= 5:
            problems.append(f"{cid}: value must be an integer 1-5")
        if not isinstance(c.get("effort"), int) or not 1 <= c["effort"] <= 5:
            problems.append(f"{cid}: effort must be an integer 1-5")
    for p in problems:
        print("MALFORMED:", p, file=sys.stderr)
    for r in refusals:
        print("REFUSED:", r, file=sys.stderr)
    if problems:
        return 1
    if refusals:
        return 2
    return 0


def ranked(concepts):
    """Value against effort. Ties broken by higher value, then by id."""
    return sorted(concepts, key=lambda c: (-(c["value"] / c["effort"]), -c["value"], c["id"]))


def counts(concepts):
    return {v: sum(1 for c in concepts if c["verdict"] == v) for v in VERDICTS}


# --------------------------------------------------------------------------
# markdown
# --------------------------------------------------------------------------

def md_concept(c, data):
    L = []
    a = L.append
    a(f"# {c['id']} — {c['title']}")
    a("")
    a(f"*{c['one_line']}*")
    a("")
    a(f"**Verdict: {c['verdict']}** — {c['verdict_reason']}")
    a("")
    a(f"Family `{c['family']}` · value {c['value']}/5 against effort {c['effort']}/5 "
      f"· part of the halo concept portfolio, `docs/concepts/README.md`.")
    a("")
    a("## What it is")
    a("")
    for para in c["what_it_is"]:
        a(para)
        a("")
    a("## Why it beats the alternative")
    a("")
    for para in c["why_it_beats"]:
        a(para)
        a("")
    if c.get("numbers"):
        a("## The numbers")
        a("")
        a("| quantity | value | where it comes from |")
        a("|---|---|---|")
        for n in c["numbers"]:
            a(f"| {n['what']} | **{n['value']}** | {n['from']} |")
        a("")
    if c.get("arithmetic"):
        a("### The arithmetic, written out")
        a("")
        a("```")
        for line in c["arithmetic"]:
            a(line)
        a("```")
        a("")
    a("## The evidence")
    a("")
    a("| claim | source | date | confidence |")
    a("|---|---|---|---|")
    for ev in c["evidence"]:
        a(f"| {ev['claim']} | {ev['source']} | {ev['date']} | {ev['confidence']} |")
    a("")
    if c.get("unverified"):
        a("**What is NOT established here, stated so nobody inherits it as a fact:**")
        a("")
        for u in c["unverified"]:
            a(f"- {u}")
        a("")
    a("## What it costs")
    a("")
    a("| dimension | cost |")
    a("|---|---|")
    for k in COST_KEYS:
        a(f"| {k} | {c['cost'][k]} |")
    a("")
    a("## What it would break in the current design")
    a("")
    for b in c["breaks"]:
        a(f"- {b}")
    a("")
    a("## The smallest experiment that would settle it")
    a("")
    a(c["smallest_experiment"])
    a("")
    if c.get("if_it_works"):
        a("## What follows if it works")
        a("")
        for x in c["if_it_works"]:
            a(f"- {x}")
        a("")
    a("---")
    a("")
    a(f"Generated from `spec/concepts.json` by `tools/gen_concepts.py` on "
      f"{data['generated']}. Do not edit this file; edit the JSON.")
    return "\n".join(L) + "\n"


def md_index(data):
    cs = data["concepts"]
    n = counts(cs)
    L = []
    a = L.append
    a(f"# {data['title']}")
    a("")
    a(f"*{data['subtitle']}*")
    a("")
    a(f"> {data['leif_verbatim']}")
    a("")
    for para in data["preamble"]:
        a(para)
        a("")
    a(f"**{len(cs)} concepts: {n['PROVEN']} PROVEN · {n['PLAUSIBLE']} PLAUSIBLE "
      f"· {n['SPECULATIVE']} SPECULATIVE.**")
    a("")
    a("## What the three verdicts mean here")
    a("")
    a("| verdict | means |")
    a("|---|---|")
    for v in VERDICTS:
        a(f"| **{v}** | {data['verdict_rules'][v]} |")
    a("")
    a("A concept with no source is SPECULATIVE and says what would settle it. "
      "That rule is `docs/TOOLS-THAT-LIE.md` applied to ideas rather than to tools: "
      "a portfolio that reads as all-green would be reporting completeness it had "
      "not earned.")
    a("")
    a("## Where halo stands before any of this")
    a("")
    a("| fact | number | source |")
    a("|---|---|---|")
    for b in data["baseline"]:
        a(f"| {b['what']} | **{b['value']}** | {b['from']} |")
    a("")
    a("## The portfolio")
    a("")
    a("| # | concept | verdict | value | effort | one line |")
    a("|---|---|---|---|---|---|")
    for c in cs:
        a(f"| {c['id']} | [{c['title']}]({c['id']}-{c['slug']}.md) | **{c['verdict']}** "
          f"| {c['value']} | {c['effort']} | {c['one_line']} |")
    a("")
    a("## Ranked by value against effort")
    a("")
    a("Value is what it is worth to the goal in `GOAL.md`; effort is what it costs "
      "to find out, not what it costs to ship. A cheap experiment on a big idea "
      "outranks an expensive certainty.")
    a("")
    a("| rank | concept | value/effort | verdict | the first move |")
    a("|---|---|---|---|---|")
    for i, c in enumerate(ranked(cs), 1):
        a(f"| {i} | {c['id']} {c['title']} | {c['value']}/{c['effort']} = "
          f"{c['value']/c['effort']:.2f} | {c['verdict']} | {c['first_move']} |")
    a("")
    a("## What was considered and left out")
    a("")
    for r in data["rejected"]:
        a(f"- **{r['what']}** — {r['why']}")
    a("")
    a("---")
    a("")
    a(f"Generated from `spec/concepts.json` by `tools/gen_concepts.py` on "
      f"{data['generated']}, commit `{rev()}`. The HTML page is "
      "`out/concepts/INDEX.html`. Do not edit these files; edit the JSON.")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------
# html
# --------------------------------------------------------------------------

CSS = """
:root{--ink:#16181d;--dim:#5c6370;--line:#dfe3e8;--bg:#fff;--card:#fafbfc;
 --proven:#0a7d33;--plausible:#a86500;--spec:#7a5bb5;--accent:#1a5fb4}
@media(prefers-color-scheme:dark){:root{--ink:#e8eaed;--dim:#9aa2ad;--line:#2c313a;
 --bg:#14161a;--card:#191c21;--proven:#4ec26f;--plausible:#e0a233;--spec:#b39ae0;--accent:#7aa8ea}}
*{box-sizing:border-box}
body{margin:0;padding:2.5rem 1.5rem 6rem;background:var(--bg);color:var(--ink);
 font:16px/1.65 -apple-system,"Helvetica Neue",sans-serif}
main{max-width:66rem;margin:0 auto}
h1{font-size:2.1rem;margin:0 0 .2rem;letter-spacing:-.02em}
h2{font-size:1.3rem;margin:3rem 0 .75rem;padding-bottom:.4rem;border-bottom:1px solid var(--line)}
h3{font-size:1.05rem;margin:2rem 0 .4rem}
h4{font-size:.9rem;margin:1.2rem 0 .3rem;color:var(--dim);text-transform:uppercase;letter-spacing:.06em}
.sub{color:var(--dim);margin:0 0 1.5rem}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.9rem}
th,td{text-align:left;vertical-align:top;padding:.5rem .7rem;border-bottom:1px solid var(--line)}
th{font-weight:600;color:var(--dim);font-size:.78rem;text-transform:uppercase;letter-spacing:.05em}
td.n{width:2.6rem;color:var(--dim);font-variant-numeric:tabular-nums}
.wrap{overflow-x:auto}
.badge{display:inline-block;font-size:.7rem;font-weight:700;letter-spacing:.06em;
 padding:.13rem .45rem;border-radius:3px;border:1px solid currentColor;white-space:nowrap}
.PROVEN{color:var(--proven)} .PLAUSIBLE{color:var(--plausible)} .SPECULATIVE{color:var(--spec)}
code,.mono{font:.85em ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim);word-break:break-word}
pre{background:var(--card);border:1px solid var(--line);border-radius:5px;padding:.8rem 1rem;
 overflow-x:auto;font:.82rem/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--ink)}
blockquote{margin:1rem 0;padding:.8rem 1.1rem;border-left:3px solid var(--line);
 background:rgba(127,127,127,.06)}
.card{border:1px solid var(--line);border-radius:7px;padding:1.2rem 1.4rem;margin:1.5rem 0;background:var(--card)}
.card h3{margin-top:0}
.one{color:var(--dim);font-style:italic;margin:.2rem 0 1rem}
.meta{color:var(--dim);font-size:.82rem;margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line)}
ul{padding-left:1.2rem} li{margin:.3rem 0}
.ve{font-variant-numeric:tabular-nums;font-weight:600}
.tally{display:flex;gap:1.5rem;flex-wrap:wrap;margin:1rem 0}
.tally div{border:1px solid var(--line);border-radius:6px;padding:.6rem 1rem;background:var(--card)}
.tally b{display:block;font-size:1.6rem;line-height:1.1;font-variant-numeric:tabular-nums}
a{color:var(--accent)}
.rule{color:var(--dim);font-size:.86rem}
"""


def badge(v):
    return f'<span class="badge {E(v)}">{E(v)}</span>'


def html_page(data):
    cs = data["concepts"]
    n = counts(cs)
    p = []
    a = p.append
    a('<!doctype html><html lang="en"><meta charset="utf-8">')
    a('<meta name="viewport" content="width=device-width,initial-scale=1">')
    a(f'<title>{E(data["title"])}</title><style>{CSS}</style><main>')
    a(f'<h1>{E(data["title"])}</h1>')
    a(f'<p class="sub">{E(data["subtitle"])} · generated {E(data["generated"])} '
      f'· commit <span class="mono">{rev()}</span></p>')
    a(f'<blockquote>{E(data["leif_verbatim"])}</blockquote>')
    for para in data["preamble"]:
        a(f'<p>{E(para)}</p>')
    a('<div class="tally">')
    a(f'<div><b>{len(cs)}</b>concepts</div>')
    for v in VERDICTS:
        a(f'<div class="{v}"><b>{n[v]}</b>{v.lower()}</div>')
    a('</div>')

    a('<h2>What the three verdicts mean here</h2><table><tr><th>Verdict</th><th>Means</th></tr>')
    for v in VERDICTS:
        a(f'<tr><td>{badge(v)}</td><td class="rule">{E(data["verdict_rules"][v])}</td></tr>')
    a('</table>')
    a('<p class="rule">A concept with no source is SPECULATIVE and says what would settle it. '
      'That is <code>docs/TOOLS-THAT-LIE.md</code> applied to ideas rather than to tools: a '
      'portfolio that read as all-green would be reporting completeness it had not earned.</p>')

    a('<h2>Where halo stands before any of this</h2>')
    a('<div class="wrap"><table><tr><th>Fact</th><th>Number</th><th>Source</th></tr>')
    for b in data["baseline"]:
        a(f'<tr><td>{E(b["what"])}</td><td><b>{E(b["value"])}</b></td>'
          f'<td class="mono">{E(b["from"])}</td></tr>')
    a('</table></div>')

    a('<h2>Ranked by value against effort</h2>')
    a('<p>Value is what it is worth to <code>GOAL.md</code>; effort is what it costs to find '
      'out, not what it costs to ship. A cheap experiment on a big idea outranks an expensive '
      'certainty.</p>')
    a('<div class="wrap"><table><tr><th>#</th><th>Concept</th><th>V/E</th><th>Verdict</th>'
      '<th>The first move</th></tr>')
    for i, c in enumerate(ranked(cs), 1):
        a(f'<tr><td class="n">{i}</td><td><a href="#{E(c["id"])}"><b>{E(c["id"])}</b> '
          f'{E(c["title"])}</a></td><td class="ve">{c["value"]}/{c["effort"]} = '
          f'{c["value"]/c["effort"]:.2f}</td><td>{badge(c["verdict"])}</td>'
          f'<td>{E(c["first_move"])}</td></tr>')
    a('</table></div>')

    a('<h2>The concepts</h2>')
    for c in cs:
        a(f'<div class="card" id="{E(c["id"])}">')
        a(f'<h3>{E(c["id"])} · {E(c["title"])} &nbsp; {badge(c["verdict"])}</h3>')
        a(f'<p class="one">{E(c["one_line"])}</p>')
        a(f'<p class="rule"><b>Why that verdict:</b> {E(c["verdict_reason"])}</p>')
        a('<h4>What it is</h4>')
        for para in c["what_it_is"]:
            a(f'<p>{E(para)}</p>')
        a('<h4>Why it beats the alternative</h4>')
        for para in c["why_it_beats"]:
            a(f'<p>{E(para)}</p>')
        if c.get("numbers"):
            a('<h4>The numbers</h4><div class="wrap"><table>'
              '<tr><th>Quantity</th><th>Value</th><th>From</th></tr>')
            for x in c["numbers"]:
                a(f'<tr><td>{E(x["what"])}</td><td><b>{E(x["value"])}</b></td>'
                  f'<td class="mono">{E(x["from"])}</td></tr>')
            a('</table></div>')
        if c.get("arithmetic"):
            a('<h4>The arithmetic, written out</h4><pre>' +
              E("\n".join(c["arithmetic"])) + '</pre>')
        a('<h4>The evidence</h4><div class="wrap"><table>'
          '<tr><th>Claim</th><th>Source</th><th>Date</th><th>Confidence</th></tr>')
        for ev in c["evidence"]:
            a(f'<tr><td>{E(ev["claim"])}</td><td class="mono">{E(ev["source"])}</td>'
              f'<td>{E(ev["date"])}</td><td>{E(ev["confidence"])}</td></tr>')
        a('</table></div>')
        if c.get("unverified"):
            a('<h4>Not established — do not inherit these as facts</h4><ul>')
            for u in c["unverified"]:
                a(f'<li>{E(u)}</li>')
            a('</ul>')
        a('<h4>What it costs</h4><table>')
        for k in COST_KEYS:
            a(f'<tr><th style="width:8rem">{k}</th><td>{E(c["cost"][k])}</td></tr>')
        a('</table>')
        a('<h4>What it would break in the current design</h4><ul>')
        for b in c["breaks"]:
            a(f'<li>{E(b)}</li>')
        a('</ul>')
        a(f'<h4>The smallest experiment that would settle it</h4><p>{E(c["smallest_experiment"])}</p>')
        if c.get("if_it_works"):
            a('<h4>What follows if it works</h4><ul>')
            for x in c["if_it_works"]:
                a(f'<li>{E(x)}</li>')
            a('</ul>')
        a(f'<p class="rule">Full page: <code>docs/concepts/{E(c["id"])}-{E(c["slug"])}.md</code></p>')
        a('</div>')

    a('<h2>What was considered and left out</h2><ul>')
    for r in data["rejected"]:
        a(f'<li><b>{E(r["what"])}</b> — {E(r["why"])}</li>')
    a('</ul>')

    a(f'<p class="meta">{E(data["generated_note"])} Regenerate with '
      f'<code>python3 tools/gen_concepts.py</code>. Source of truth: '
      f'<code>spec/concepts.json</code>.</p>')
    a('</main></html>')
    return "\n".join(p)


# --------------------------------------------------------------------------
# prove the checks fire — docs/TOOLS-THAT-LIE.md §6
# --------------------------------------------------------------------------

_GOOD = {
    "schema": "halo/concepts/1", "generated": "0000-00-00", "title": "t",
    "subtitle": "s", "leif_verbatim": "q", "preamble": ["p"], "generated_note": "n",
    "verdict_rules": {v: v.lower() for v in VERDICTS},
    "baseline": [{"what": "w", "value": "v", "from": "f"}],
    "rejected": [{"what": "x", "why": "y"}],
    "concepts": [{
        "id": "C1", "slug": "s", "title": "t", "one_line": "o", "family": "f",
        "what_it_is": ["a"], "why_it_beats": ["b"], "verdict": "PROVEN",
        "verdict_reason": "r",
        "cost": {"money": "m", "current": "c", "size": "s", "complexity": "x"},
        "breaks": ["b"],
        "evidence": [{"claim": "c", "source": "s", "date": "d", "confidence": "primary"}],
        "smallest_experiment": "e", "value": 3, "effort": 2, "first_move": "go"}],
}

_MUTATIONS = {
    "a concept with no verdict_reason":
        lambda d: d["concepts"][0].pop("verdict_reason"),
    "a verdict outside the three":
        lambda d: d["concepts"][0].__setitem__("verdict", "MAYBE"),
    "a concept with no evidence at all":
        lambda d: d["concepts"][0].__setitem__("evidence", []),
    "an evidence row with no date":
        lambda d: d["concepts"][0]["evidence"][0].pop("date"),
    "an evidence row with no source":
        lambda d: d["concepts"][0]["evidence"][0].pop("source"),
    "a cost with no current figure":
        lambda d: d["concepts"][0]["cost"].pop("current"),
    "a concept with no experiment that would settle it":
        lambda d: d["concepts"][0].__setitem__("smallest_experiment", "   "),
    "a value outside 1-5":
        lambda d: d["concepts"][0].__setitem__("value", 9),
    "an effort that is not a number":
        lambda d: d["concepts"][0].__setitem__("effort", "low"),
    "two concepts with the same id":
        lambda d: d["concepts"].append(json.loads(json.dumps(d["concepts"][0]))),
    "a concept with no list of what it breaks":
        lambda d: d["concepts"][0].__setitem__("breaks", []),
}


def self_test():
    """Break the input on purpose, once per assertion, and require a refusal.

    A check nobody has watched fail is not known to work. Exit 0 only if the
    good fixture passes AND every mutation is caught by name.
    """
    import io
    import contextlib

    def grade(doc):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = check(doc)
        return rc, err.getvalue().strip().splitlines()

    rc, _ = grade(json.loads(json.dumps(_GOOD)))
    print(f"{'CONTROL (a valid portfolio)':52s} exit {rc}  "
          f"{'ok' if rc == 0 else 'FAIL — the control is already red, so nothing below proves anything'}")
    if rc != 0:
        return 1
    bad = 0
    for name, mut in _MUTATIONS.items():
        doc = json.loads(json.dumps(_GOOD))
        mut(doc)
        rc, lines = grade(doc)
        fired = rc != 0
        bad += 0 if fired else 1
        first = (lines[0] if lines else "")[:64]
        print(f"{name:52s} exit {rc}  {'FIRED' if fired else 'SILENT <-- DEFECT'}  {first}")
    total = len(_MUTATIONS)
    print(f"\n{total - bad} of {total} assertions fired")
    return 1 if bad else 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    data = json.loads(SRC.read_text())
    code = check(data)
    if code:
        print(f"\nrefusing to generate: exit {code}", file=sys.stderr)
        return code

    DOCS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    written = []
    for c in data["concepts"]:
        f = DOCS / f"{c['id']}-{c['slug']}.md"
        f.write_text(md_concept(c, data), encoding="utf-8")
        written.append(f)
    idx = DOCS / "README.md"
    idx.write_text(md_index(data), encoding="utf-8")
    written.append(idx)
    page = OUT / "INDEX.html"
    page.write_text(html_page(data), encoding="utf-8")
    written.append(page)

    n = counts(data["concepts"])
    for f in written:
        print(f"wrote {f.relative_to(ROOT)} ({f.stat().st_size} bytes)")
    print(f"\n{len(data['concepts'])} concepts: "
          f"{n['PROVEN']} PROVEN, {n['PLAUSIBLE']} PLAUSIBLE, {n['SPECULATIVE']} SPECULATIVE")
    top = ranked(data["concepts"])[:3]
    print("top three by value against effort: " +
          ", ".join(f"{c['id']} ({c['value']}/{c['effort']})" for c in top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
