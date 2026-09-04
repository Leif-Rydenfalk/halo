#!/usr/bin/env python3
"""Generate docs/TEST-PLAN.md and out/release/TEST-PLAN.html from spec/test-plan.json.

Nothing here is hand-typed HTML and nothing here is a hand-typed number. The
test counts, the stage roll-ups, the cycle-time budget and the CANNOT DETERMINE
tally are all COUNTED from the data, because docs/TOOLS-THAT-LIE.md rule 3 says
count afterwards: the count is derived from the effect, the log line is not.

The generator also refuses to write a plan that does not meet the standard:

  * every test must carry a non-empty `could_pass_while` and `counter_assert`
    (TOOLS-THAT-LIE: "write down the sentence 'this could report PASS while ___
    is badly wrong' and fill the blank. If you can fill it, the check is
    incomplete.");
  * every limit must carry a `source`;
  * a limit with a null value must say CANNOT DETERMINE in its source, and a
    limit with a real value must NOT, because a sourced number and an unsourced
    one must never look the same on a factory traveller;
  * every test's declared verdict must equal the verdict the data implies.

If any of those fail the generator exits non-zero and writes nothing.

    python3 tools/gen_test_plan.py
"""
import json, pathlib, datetime, html, subprocess, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "spec" / "test-plan.json").read_text(encoding="utf-8"))
OUT = ROOT / "out" / "release"
DOCS = ROOT / "docs"
OUT.mkdir(parents=True, exist_ok=True)
E = html.escape


def rev():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


# ---------------------------------------------------------------- checks
NON_GATE = {"record", "note", "\u2248"}


def is_gate(lim):
    """A gate is a limit a station judges a unit against.

    Rows marked record / note / \u2248 are readings and design anchors. They may
    legitimately have no window yet — section 10 lists them either way — but they
    cannot make a runnable test unrunnable, and they cannot make an unrunnable
    one look fine.
    """
    return lim.get("op") not in NON_GATE


def check(data):
    """Refuse to generate a plan that does not meet docs/TOOLS-THAT-LIE.md."""
    problems = []
    for t in data["tests"]:
        tid = t["id"]
        if not t.get("could_pass_while", "").strip():
            problems.append(f"{tid}: empty could_pass_while — the blank is not filled")
        if not t.get("counter_assert", "").strip():
            problems.append(f"{tid}: empty counter_assert — nothing closes the blank")
        if not t.get("traces"):
            problems.append(f"{tid}: no traces — a test that proves nothing traceable")
        if not t.get("limits"):
            problems.append(f"{tid}: no limits — a test with no limit is an observation")
        seen = set()
        for lim in t["limits"]:
            src = lim.get("source", "")
            if lim.get("q") in seen:
                problems.append(f"{tid}/{lim.get('q')}: two limits with the same name — "
                                f"a traveller cannot tell them apart")
            seen.add(lim.get("q"))
            if not src.strip():
                problems.append(f"{tid}/{lim.get('q')}: limit with no source")
                continue
            unsourced = "CANNOT DETERMINE" in src
            if lim.get("value") is None and not unsourced:
                problems.append(
                    f"{tid}/{lim.get('q')}: null value but the source does not say "
                    f"CANNOT DETERMINE — an empty limit must announce itself")
            if is_gate(lim) and lim.get("value") is not None and unsourced:
                problems.append(
                    f"{tid}/{lim.get('q')}: a GATE with a value that also says CANNOT "
                    f"DETERMINE — pick one; a number nobody sourced must not look sourced")
        implied = "CANNOT DETERMINE" if any(
            is_gate(l) and "CANNOT DETERMINE" in l.get("source", "")
            for l in t["limits"]) else "PASS"
        if t.get("verdict") != implied:
            problems.append(
                f"{tid}: declared verdict {t.get('verdict')!r} but the limits imply "
                f"{implied!r} — the verdict must be derived from the rows, not asserted")
    return problems


def selftest():
    """Deliberate breaks, to prove the checks can fail.

    docs/MECHANICAL.md §5.2 states the principle for the battery-door probes: a
    test that can only pass is not a test. The same applies to this generator's
    own checks, so they are exercised against five deliberate breaks.
    """
    import copy
    cases = [
        ("empty counter_assert", lambda d: d["tests"][0].update(counter_assert="")),
        ("limit with no source", lambda d: d["tests"][0]["limits"][0].update(source="")),
        ("null value that does not announce itself",
         lambda d: d["tests"][0]["limits"][0].update(value=None, source="a datasheet")),
        ("verdict asserted rather than derived",
         lambda d: d["tests"][0].update(verdict="PASS", limits=[
             {"q": "x", "op": "=", "value": None, "unit": "u",
              "source": "CANNOT DETERMINE - nothing"}])),
        ("two limits with the same name",
         lambda d: d["tests"][0].update(limits=[
             {"q": "x", "op": "=", "value": 1, "unit": "u", "source": "s"},
             {"q": "x", "op": "=", "value": 2, "unit": "u", "source": "s"}])),
    ]
    ok = True
    for name, break_it in cases:
        d = copy.deepcopy(DATA)
        break_it(d)
        found = check(d)
        print(f"  {'caught' if found else 'MISSED'}: {name}")
        ok = ok and bool(found)
    clean = check(DATA)
    print(f"  {'clean' if not clean else 'DIRTY'}: the real plan, unbroken")
    ok = ok and not clean
    print("selftest PASS" if ok else "selftest FAIL")
    return 0 if ok else 1


if "--selftest" in sys.argv:
    sys.exit(selftest())

problems = check(DATA)
if problems:
    print("REFUSED — the plan does not meet docs/TOOLS-THAT-LIE.md:", file=sys.stderr)
    for p in problems:
        print("  " + p, file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- derived
LOT = DATA["cycle_time"]["lot_size_assumed"]
STAGES = {s["id"]: s for s in DATA["stages"]}


def fraction(sampling):
    """How much of one unit's cycle time this test costs. Derived, never typed.

    '100 %...'                    -> 1.0            (every unit)
    'n <things> per <something>'  -> n / LOT        (amortised over a lot)
    anything else                 -> 0.0            (someone else's machine time)
    """
    s = sampling.strip()
    if s.startswith("100 %"):
        # a row may be 100 % for one part and sampled for another; the 100 %
        # part dominates the cycle, so it is charged in full.
        return 1.0
    m = re.match(r"^(\d+)\s+\w+", s)
    if m:
        return int(m.group(1)) / LOT
    return 0.0


rows = []
for t in DATA["tests"]:
    f = fraction(t["sampling"])
    rows.append((t, f, t["cycle_s"] * f))

by_stage = {}
for t, f, cost in rows:
    b = by_stage.setdefault(t["stage"], {"n": 0, "cycle": 0.0, "cd": 0, "gonogo": 0, "full": 0})
    b["n"] += 1
    b["cycle"] += cost
    b["cd"] += t["verdict"] == "CANNOT DETERMINE"
    b["gonogo"] += t["type"] == "go/no-go"
    b["full"] += f == 1.0

TOTAL_CYCLE = sum(c for _, _, c in rows)
N_TESTS = len(DATA["tests"])
N_CD = sum(1 for t in DATA["tests"] if t["verdict"] == "CANNOT DETERMINE")
N_PASS = N_TESTS - N_CD
N_100 = sum(1 for _, f, _ in rows if f == 1.0)
N_LIMITS = sum(len(t["limits"]) for t in DATA["tests"])
N_LIMITS_CD = sum(1 for t in DATA["tests"] for l in t["limits"]
                  if "CANNOT DETERMINE" in l["source"])
N_GATES = sum(1 for t in DATA["tests"] for l in t["limits"] if is_gate(l))
N_GATES_CD = sum(1 for t in DATA["tests"] for l in t["limits"]
                 if is_gate(l) and "CANNOT DETERMINE" in l["source"])
SLOWEST = max(by_stage.items(), key=lambda kv: kv[1]["cycle"])


def dur(sec):
    if sec < 60:
        return f"{sec:.1f} s"
    return f"{sec/60:.1f} min ({sec:.0f} s)"


def limtext(l):
    v = l.get("value")
    if isinstance(v, list):
        v = " … ".join(str(x) for x in v)
    if v is None:
        v = "—"
    unit = l.get("unit") or ""
    return f'{l["q"]} {l["op"]} {v} {unit}'.strip()


# ---------------------------------------------------------------- HTML
CSS = """
:root{--ink:#16181d;--dim:#5c6370;--line:#dfe3e8;--bg:#fff;--ready:#0a7d33;--partial:#a86500;--not:#a11}
@media(prefers-color-scheme:dark){:root{--ink:#e8eaed;--dim:#9aa2ad;--line:#2c313a;--bg:#14161a;--ready:#4ec26f;--partial:#e0a233;--not:#f0736a}}
*{box-sizing:border-box}
body{margin:0;padding:2.5rem 1.5rem 6rem;background:var(--bg);color:var(--ink);
 font:16px/1.65 -apple-system,"Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif}
main{max-width:64rem;margin:0 auto}
h1{font-size:2rem;margin:0 0 .2rem;letter-spacing:-.02em}
h2{font-size:1.25rem;margin:3rem 0 .75rem;padding-bottom:.4rem;border-bottom:1px solid var(--line)}
h3{font-size:1rem;margin:1.75rem 0 .4rem}
.sub{color:var(--dim);margin:0 0 1.5rem}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.92rem}
th,td{text-align:left;vertical-align:top;padding:.55rem .7rem;border-bottom:1px solid var(--line)}
th{font-weight:600;color:var(--dim);font-size:.8rem;text-transform:uppercase;letter-spacing:.05em}
td.n{width:2.5rem;color:var(--dim);font-variant-numeric:tabular-nums}
.badge{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.06em;padding:.15rem .45rem;
 border-radius:3px;border:1px solid currentColor;white-space:nowrap}
.PASS{color:var(--ready)} .REC{color:var(--partial)} .NOT{color:var(--not)}
code,.mono{font:.85em ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim);word-break:break-word}
blockquote{margin:1rem 0;padding:.8rem 1.1rem;border-left:3px solid var(--line);color:var(--ink);background:rgba(127,127,127,.06)}
.zh{color:var(--dim);font-size:.9em}
.meta{color:var(--dim);font-size:.82rem;margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line)}
ul{padding-left:1.2rem} li{margin:.3rem 0}
.owner{font-size:.75rem;font-weight:600;color:var(--dim);letter-spacing:.04em}
.lie{color:var(--not);font-size:.85em}
.fix{color:var(--ready);font-size:.85em}
"""


def badge(v):
    cls = "PASS" if v == "PASS" else "NOT"
    return f'<span class="badge {cls}">{E(v)}</span>'


p = []
a = p.append
a('<!doctype html><html lang="en"><meta charset="utf-8">')
a('<meta name="viewport" content="width=device-width,initial-scale=1">')
a(f'<title>{E(DATA["title"])} — {E(DATA["subtitle"])}</title><style>{CSS}</style><main>')
a(f'<h1>{E(DATA["title"])}</h1>')
a(f'<p class="sub">{E(DATA["subtitle"])} · lane {E(DATA["lane"])} · generated '
  f'{datetime.date.today().isoformat()} · commit <span class="mono">{rev()}</span></p>')
a(f'<p>{E(DATA["summary_en"])}</p>')
a(f'<p class="zh">{E(DATA["summary_zh"])}</p>')
a(f'<blockquote>{E(DATA["leif_verbatim"])}</blockquote>')

a(f'<h2>1 · The plan in numbers — {N_TESTS} tests, {N_100} of them on every unit</h2>')
a(f'<p>Counted from <code>spec/test-plan.json</code>, not typed. {N_LIMITS} limits in total, '
  f'of which <b>{N_LIMITS_CD}</b> are CANNOT DETERMINE and say what would settle them. '
  f'{N_PASS} tests are ready to run as written; <b>{N_CD}</b> carry at least one open limit.</p>')
a('<table><tr><th>#</th><th>Station</th><th>Where</th><th>Tests</th><th>On every unit</th>'
  '<th>Go/no-go</th><th>Open limits</th><th>Cycle per unit</th></tr>')
for s in DATA["stages"]:
    b = by_stage.get(s["id"], {"n": 0, "cycle": 0, "cd": 0, "gonogo": 0, "full": 0})
    a(f'<tr><td class="n">{s["n"]}</td><td><b>{E(s["name"])}</b><br><span class="zh">{E(s["name_zh"])}</span></td>'
      f'<td>{E(s["where"])}</td><td>{b["n"]}</td><td>{b["full"]}</td><td>{b["gonogo"]}</td>'
      f'<td>{b["cd"]}</td><td>{E(dur(b["cycle"]))}</td></tr>')
a(f'<tr><td></td><td><b>total</b></td><td></td><td><b>{N_TESTS}</b></td><td><b>{N_100}</b></td>'
  f'<td><b>{sum(b["gonogo"] for b in by_stage.values())}</b></td><td><b>{N_CD}</b></td>'
  f'<td><b>{E(dur(TOTAL_CYCLE))}</b></td></tr>')
a('</table>')
a(f'<p><b>Cycle-time estimate: {E(dur(TOTAL_CYCLE))} per unit across all three stations.</b> '
  f'{E(DATA["cycle_time"]["method"])} The busiest station is '
  f'<b>{E(STAGES[SLOWEST[0]]["name"])}</b> at {E(dur(SLOWEST[1]["cycle"]))}, and since the three '
  f'stations run in parallel on different units, that number and not the total is the line\'s takt.</p>')
a(f'<p>{E(DATA["cycle_time"]["note"])}</p><ul>')
for c in DATA["cycle_time"]["compression_options"]:
    a(f'<li>{E(c)}</li>')
a('</ul>')

a('<h2>2 · What each station is for</h2>')
for s in DATA["stages"]:
    a(f'<h3>{s["n"]} · {E(s["name"])} <span class="zh">{E(s["name_zh"])}</span></h3>')
    a(f'<p>{E(s["what"])}</p>')

a(f'<h2>3 · The tests</h2>')
a(f'<p>{E(DATA["verdict_meaning"])}</p>')
a(f'<blockquote>{E(DATA["standard"])}</blockquote>')
for s in DATA["stages"]:
    ts = [t for t in DATA["tests"] if t["stage"] == s["id"]]
    a(f'<h3>Station {s["n"]} — {E(s["name"])} <span class="zh">{E(s["name_zh"])}</span> '
      f'— <span class="owner">{len(ts)} TESTS</span></h3>')
    for t in ts:
        a(f'<table><tr><th style="width:9rem">{E(t["id"])}</th>'
          f'<td><b>{E(t["name"])}</b> <span class="zh">{E(t["name_zh"])}</span> {badge(t["verdict"])}</td></tr>')
        a(f'<tr><th>Proves</th><td>{E(t["proves"])}</td></tr>')
        a('<tr><th>Traces to</th><td>' + "<br>".join(f'<span class="mono">{E(x)}</span>' for x in t["traces"]) + '</td></tr>')
        a(f'<tr><th>Measurement</th><td>{E(t["measure"])}</td></tr>')
        lim = "".join(f'<li><b>{E(limtext(l))}</b><br><span class="mono">source: {E(l["source"])}</span></li>'
                      for l in t["limits"])
        a(f'<tr><th>Limits</th><td><ul>{lim}</ul></td></tr>')
        eq = ", ".join(t["equip"]) or "—"
        a(f'<tr><th>Equipment</th><td><span class="mono">{E(eq)}</span></td></tr>')
        a(f'<tr><th>Sampling</th><td>{E(t["sampling"])}</td></tr>')
        a(f'<tr><th>Type / cycle</th><td>{E(t["type"])} · {t["cycle_s"]} s</td></tr>')
        a(f'<tr><th>On failure</th><td>{E(t["on_fail"])}</td></tr>')
        a(f'<tr><th>Recorded</th><td><span class="mono">{E(", ".join(t["records"]))}</span></td></tr>')
        a(f'<tr><th>Could pass while…</th><td class="lie">{E(t["could_pass_while"])}</td></tr>')
        a(f'<tr><th>…so assert</th><td class="fix">{E(t["counter_assert"])}</td></tr>')
        if t.get("flag"):
            a(f'<tr><th>Flag</th><td class="lie">{E(t["flag"])}</td></tr>')
        a('</table>')

a('<h2>4 · The fixtures the factory must build</h2>')
for f in DATA["fixtures"]:
    a(f'<h3>{E(f["id"])} · {E(f["name"])} <span class="zh">{E(f["name_zh"])}</span> '
      f'— <span class="owner">{E(f["stage"]).upper()}</span></h3>')
    a(f'<p>{E(f["build"])}</p>')
    if f["points"]:
        a('<table><tr><th>Probe point</th><th>Net</th><th>For</th><th>Does it exist?</th></tr>')
        for pt in f["points"]:
            a(f'<tr><td><span class="mono">{E(pt["point"])}</span></td>'
              f'<td><span class="mono">{E(pt["net"])}</span></td><td>{E(pt["for"])}</td>'
              f'<td>{E(pt["exists"])}</td></tr>')
        a('</table>')
    a(f'<p><b>Calibration.</b> {E(f["calibration"])}</p>')
    a(f'<p>{E(f["notes"])}</p>')

a('<h2>5 · Equipment, and how each piece is proved honest</h2>')
a('<table><tr><th>Id</th><th>Instrument</th><th>Specification</th><th>Calibration / self-test</th><th>Owner</th></tr>')
for e in DATA["equipment"]:
    a(f'<tr><td><span class="mono">{E(e["id"])}</span></td>'
      f'<td><b>{E(e["name"])}</b><br><span class="zh">{E(e["name_zh"])}</span></td>'
      f'<td>{E(e["spec"])}</td><td>{E(e["cal"])}</td><td>{E(e["owner"])}</td></tr>')
a('</table>')

a('<h2>6 · Test pads requested from lane B1</h2>')
a('<p>The board carries no test points today. Every point below is a request, not an edit — lane B1 owns '
  '<code>electronics/</code> and this lane did not touch it.</p>')
a('<table><tr><th>#</th><th>Pad</th><th>Net</th><th>Why</th><th>Constraint</th></tr>')
for r in DATA["b1_requests"]:
    a(f'<tr><td class="n">{r["n"]}</td><td><b><span class="mono">{E(r["pad"])}</span></b></td>'
      f'<td><span class="mono">{E(r["net"])}</span></td><td>{E(r["why"])}</td><td>{E(r["constraint"])}</td></tr>')
a('</table>')

a('<h2>7 · Sampling, yield and what a failure means</h2>')
a('<table><tr><th>Rule</th><th>Applies to</th><th>Why</th></tr>')
for s in DATA["sampling_policy"]:
    a(f'<tr><td><b>{E(s["rule"])}</b></td><td><span class="mono">{E(", ".join(s["applies_to"]))}</span></td>'
      f'<td>{E(s["why"])}</td></tr>')
a('</table>')
a('<table><tr><th>Station</th><th>On failure</th><th>Why</th><th>When it escalates</th></tr>')
for y in DATA["yield_and_failure"]:
    a(f'<tr><td><b>{E(STAGES[y["stage"]]["name"])}</b></td>'
      f'<td><span class="badge NOT">{E(y["on_fail"])}</span></td>'
      f'<td>{E(y["why"])}</td><td>{E(y["escalate"])}</td></tr>')
a('</table>')

a('<h2>8 · What is recorded per unit</h2>')
tr = DATA["traceability_record"]
a(f'<p><b>Key:</b> {E(tr["key"])}</p><ul>')
for f in tr["fields"]:
    a(f'<li>{E(f)}</li>')
a('</ul>')
a(f'<p><b>Retention.</b> {E(tr["retention"])}</p><p>{E(tr["why"])}</p>')

a('<h2>9 · What cannot be tested in production</h2>')
a(f'<p>{E(DATA["not_tested_in_production"])}</p>')
a('<table><tr><th>Id</th><th>What</th><th>Standard</th><th>Why not on the line</th><th>Where it stands</th><th>Sample</th></tr>')
for q in DATA["qualification"]:
    a(f'<tr><td><span class="mono">{E(q["id"])}</span></td>'
      f'<td><b>{E(q["name"])}</b><br><span class="zh">{E(q["name_zh"])}</span></td>'
      f'<td>{E(q["standard"])}</td><td>{E(q["why_not_on_the_line"])}</td><td>{E(q["status"])}</td>'
      f'<td>{E(q["sample"])}</td></tr>')
a('</table>')

a(f'<h2>10 · What could not be sourced — {len(DATA["cannot_determine"])} open limits</h2>')
a('<p>Each row is a work item, never a question for anyone to answer from memory. A limit we invented '
  'would be worse than no limit: the line would run to it, and the number would be wrong.</p>')
a('<table><tr><th>What</th><th>What would settle it</th></tr>')
for c in DATA["cannot_determine"]:
    a(f'<tr><td><b>{E(c["what"])}</b></td><td>{E(c["settles_it"])}</td></tr>')
a('</table>')

a('<h2>11 · Notes the test engineer should read before the first shift</h2><ul>')
for n in DATA["notes"]:
    a(f'<li>{E(n)}</li>')
a('</ul>')

a(f'<p class="meta">{E(DATA["generated_note"])} Regenerate with '
  f'<code>python3 tools/gen_test_plan.py</code>. Audience: {E(DATA["audience"])}</p>')
a('</main></html>')

(OUT / "TEST-PLAN.html").write_text("\n".join(p), encoding="utf-8")


# ---------------------------------------------------------------- Markdown
m = []
w = m.append
w(f"# {DATA['title']} — {DATA['subtitle']}")
w("")
w(f"*Lane {DATA['lane']}. Generated {datetime.date.today().isoformat()} from "
  f"`spec/test-plan.json` by `tools/gen_test_plan.py`. Nothing on this page is hand-typed. "
  f"Companion: [`docs/TOOLS-THAT-LIE.md`](TOOLS-THAT-LIE.md), which is the standard this plan "
  f"is written to, and [`out/release/TEST-PLAN.html`](../out/release/TEST-PLAN.html), which is "
  f"the same data as a page for the factory.*")
w("")
w(DATA["summary_en"])
w("")
w(DATA["summary_zh"])
w("")
w("---")
w("")
w(f"## 1. The plan in numbers")
w("")
w(f"**{N_TESTS} tests. {N_100} run on every unit. {N_LIMITS} limits, {N_GATES} of them gates a unit is "
  f"judged against. {N_LIMITS_CD} limits are CANNOT DETERMINE and name what would settle them, "
  f"{N_GATES_CD} of those being gates. Cycle-time estimate {dur(TOTAL_CYCLE)} per "
  f"unit across all three stations; the busiest station is {STAGES[SLOWEST[0]]['name']} at "
  f"{dur(SLOWEST[1]['cycle'])}, and that is the line's takt.**")
w("")
w("| # | station | tests | on every unit | go/no-go | open limits | cycle per unit |")
w("|---|---|---|---|---|---|---|")
for s in DATA["stages"]:
    b = by_stage.get(s["id"], {"n": 0, "cycle": 0, "cd": 0, "gonogo": 0, "full": 0})
    w(f"| {s['n']} | {s['name']} | {b['n']} | {b['full']} | {b['gonogo']} | {b['cd']} | {dur(b['cycle'])} |")
w(f"| | **total** | **{N_TESTS}** | **{N_100}** | "
  f"**{sum(b['gonogo'] for b in by_stage.values())}** | **{N_CD}** | **{dur(TOTAL_CYCLE)}** |")
w("")
w(DATA["cycle_time"]["method"])
w("")
w(DATA["cycle_time"]["note"])
w("")
for c in DATA["cycle_time"]["compression_options"]:
    w(f"- {c}")
w("")
w("## 2. What each station is for")
w("")
for s in DATA["stages"]:
    w(f"**{s['n']}. {s['name']}** — {s['where']}. {s['what']}")
    w("")
w("## 3. The tests")
w("")
w(DATA["verdict_meaning"])
w("")
w(f"> {DATA['standard']}")
w("")
for s in DATA["stages"]:
    ts = [t for t in DATA["tests"] if t["stage"] == s["id"]]
    w(f"### Station {s['n']} — {s['name']} ({len(ts)} tests)")
    w("")
    for t in ts:
        w(f"#### {t['id']} — {t['name']} — **{t['verdict']}**")
        w("")
        w(f"- **Proves.** {t['proves']}")
        w(f"- **Traces to.** {'; '.join(t['traces'])}")
        w(f"- **Measurement.** {t['measure']}")
        w(f"- **Limits.**")
        for l in t["limits"]:
            w(f"  - `{limtext(l)}` — {l['source']}")
        w(f"- **Equipment.** {', '.join(t['equip']) or '—'}")
        w(f"- **Sampling.** {t['sampling']}")
        w(f"- **Type / cycle.** {t['type']}, {t['cycle_s']} s")
        w(f"- **On failure.** {t['on_fail']}")
        w(f"- **Recorded.** {', '.join(t['records'])}")
        w(f"- **This could report PASS while…** {t['could_pass_while']}")
        w(f"- **…so assert.** {t['counter_assert']}")
        if t.get("flag"):
            w(f"- **Flag.** {t['flag']}")
        w("")
w("## 4. The fixtures the factory must build")
w("")
for f in DATA["fixtures"]:
    w(f"### {f['id']} — {f['name']} ({f['stage']})")
    w("")
    w(f["build"])
    w("")
    if f["points"]:
        w("| probe point | net | for | does it exist? |")
        w("|---|---|---|---|")
        for pt in f["points"]:
            w(f"| `{pt['point']}` | `{pt['net']}` | {pt['for']} | {pt['exists']} |")
        w("")
    w(f"**Calibration.** {f['calibration']}")
    w("")
    w(f["notes"])
    w("")
w("## 5. Equipment, and how each piece is proved honest")
w("")
w("| id | instrument | specification | calibration / self-test | owner |")
w("|---|---|---|---|---|")
for e in DATA["equipment"]:
    w(f"| `{e['id']}` | {e['name']} | {e['spec']} | {e['cal']} | {e['owner']} |")
w("")
w("## 6. Test pads requested from lane B1")
w("")
w("The board carries no test points today. Every point below is a request, not an edit — lane B1 owns "
  "`electronics/` and this lane did not touch it.")
w("")
w("| # | pad | net | why | constraint |")
w("|---|---|---|---|---|")
for r in DATA["b1_requests"]:
    w(f"| {r['n']} | `{r['pad']}` | `{r['net']}` | {r['why']} | {r['constraint']} |")
w("")
w("## 7. Sampling, yield and what a failure means")
w("")
w("| rule | applies to | why |")
w("|---|---|---|")
for s in DATA["sampling_policy"]:
    w(f"| **{s['rule']}** | {', '.join(s['applies_to'])} | {s['why']} |")
w("")
w("| station | on failure | why | when it escalates |")
w("|---|---|---|---|")
for y in DATA["yield_and_failure"]:
    w(f"| {STAGES[y['stage']]['name']} | **{y['on_fail']}** | {y['why']} | {y['escalate']} |")
w("")
w("## 8. What is recorded per unit")
w("")
w(f"**Key:** {tr['key']}")
w("")
for f in tr["fields"]:
    w(f"- {f}")
w("")
w(f"**Retention.** {tr['retention']}")
w("")
w(tr["why"])
w("")
w("## 9. What cannot be tested in production")
w("")
w(DATA["not_tested_in_production"])
w("")
w("| id | what | standard | why not on the line | where it stands | sample |")
w("|---|---|---|---|---|---|")
for q in DATA["qualification"]:
    w(f"| `{q['id']}` | {q['name']} | {q['standard']} | {q['why_not_on_the_line']} | {q['status']} | {q['sample']} |")
w("")
w(f"## 10. What could not be sourced — {len(DATA['cannot_determine'])} open limits")
w("")
w("Each row is a work item, never a question for anyone to answer from memory. A limit we invented "
  "would be worse than no limit: the line would run to it, and the number would be wrong.")
w("")
w("| what | what would settle it |")
w("|---|---|")
for c in DATA["cannot_determine"]:
    w(f"| **{c['what']}** | {c['settles_it']} |")
w("")
w("## 11. Notes the test engineer should read before the first shift")
w("")
for n in DATA["notes"]:
    w(f"- {n}")
w("")
w(f"---")
w("")
w(f"*{DATA['generated_note']} Regenerate with `python3 tools/gen_test_plan.py`. "
  f"Audience: {DATA['audience']}.*")

(DOCS / "TEST-PLAN.md").write_text("\n".join(m) + "\n", encoding="utf-8")

print(f"checks: {N_TESTS} tests, all carry a filled could_pass_while and counter_assert; "
      f"{N_LIMITS} limits, all sourced")
print(f"wrote {DOCS/'TEST-PLAN.md'} ({(DOCS/'TEST-PLAN.md').stat().st_size} bytes)")
print(f"wrote {OUT/'TEST-PLAN.html'} ({(OUT/'TEST-PLAN.html').stat().st_size} bytes)")
for s in DATA["stages"]:
    b = by_stage[s["id"]]
    print(f"  station {s['n']} {s['name']}: {b['n']} tests, {b['full']} on every unit, "
          f"{b['cd']} with open limits, {dur(b['cycle'])} per unit")
print(f"total {N_TESTS} tests · {N_100} on every unit · {N_PASS} PASS / {N_CD} CANNOT DETERMINE · "
      f"{N_LIMITS_CD}/{N_LIMITS} limits unsourced ({N_GATES_CD}/{N_GATES} gates) · cycle {dur(TOTAL_CYCLE)} per unit · "
      f"takt {dur(SLOWEST[1]['cycle'])} at {STAGES[SLOWEST[0]]['name']}")
