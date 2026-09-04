#!/usr/bin/env python3
"""Convergence table: how far halo is from the real AirTag, measured, not asserted.

TARGET comes from the research dossiers (Apple's drawing, the FCC exhibits, the
teardowns, the published studies). CURRENT is read live out of the tools' own
verdict/measurement files wherever one exists, so a row cannot claim a value no
tool produced. DELTA is computed. A row with no measurement is CANNOT DETERMINE,
and naming it is progress.
"""
import json, pathlib, datetime, html, subprocess

HALO = pathlib.Path(__file__).resolve().parent.parent
WS = HALO.parent.parent
OUT = HALO / "out" / "release"
OUT.mkdir(parents=True, exist_ok=True)
E = html.escape

def jload(p):
    try:
        d = json.loads(pathlib.Path(p).read_text())
        return d.get("record", d)
    except Exception:
        return None

def rf_verdict(case):
    r = jload(WS / "ce-rf" / "out" / case / "verdict.json")
    return (r or {}).get("verdict")

def rf(case, key):
    """Read one measured value out of a ce-rf case.

    A number from a case whose own verdict is FAIL is NOT a measurement of the
    thing we wanted — it is a number the solver emitted on the way to failing.
    Reading it and calling the row MATCH is exactly the defect this project
    keeps finding (docs/TOOLS-THAT-LIE.md). Found 2026-09-04: the antenna row
    read 2.425 GHz and showed MATCH while its case had hit max timesteps with no
    convergence and no reactance zero-crossing anywhere in the sweep.
    """
    if rf_verdict(case) == "FAIL":
        return None
    r = jload(WS / "ce-rf" / "out" / case / "measurements.json")
    if not r:
        return None
    for holder in ("measurements", "results", "measured"):
        block = r.get(holder)
        if isinstance(block, dict) and key in block:
            v = block[key]
            return v.get("value") if isinstance(v, dict) else v
    return None

def file_measure(path, pointer, reduce_=None):
    """Read one number out of a verification artifact on disk.

    The same reader as tools/check_convergence.py's, kept in step with it on
    purpose: this one produces the table, that one grades it, and the grader
    re-reads the file itself rather than trusting this. Returns None when the
    file or the key is missing, so a broken pointer shows as CANNOT DETERMINE
    instead of quietly holding the last value somebody typed.
    """
    f = HALO / path
    if not f.is_file():
        return None
    d = jload(f)
    if d is None:
        return None
    cur = d
    for seg in pointer.split("."):
        if isinstance(cur, list):
            try:
                cur = cur[int(seg)]
                continue
            except (ValueError, IndexError):
                return None
        if not isinstance(cur, dict) or seg not in cur:
            return None
        cur = cur[seg]
    if reduce_ == "max" and isinstance(cur, list) and cur:
        cur = max(cur)
    elif reduce_ == "min" and isinstance(cur, list) and cur:
        cur = min(cur)
    if isinstance(cur, (dict, list)):
        return None
    return cur


def spice_ok(example):
    r = jload(WS / "ce-spice" / "out" / example / "verdict.json")
    return r.get("verdict") if r else None

SPEC = json.loads((HALO / "spec" / "convergence.json").read_text())

rows = []
for r in SPEC["rows"]:
    cur, src = None, r.get("current_note")
    m = r.get("measure")
    if m:
        if m["from"] == "ce-rf":
            cur = rf(m["case"], m["key"])
            src = f'ce-rf/out/{m["case"]}/measurements.json'
        elif m["from"] == "ce-spice-verdict":
            cur = spice_ok(m["example"])
            src = f'ce-spice/out/{m["example"]}/verdict.json'
        elif m["from"] == "literal":
            cur = m["value"]
        elif m["from"] == "file":
            cur = file_measure(m.get("path", ""), m.get("pointer", ""),
                               m.get("reduce"))
            src = str(m.get("path")) + " -> " + str(m.get("pointer"))
    t = r.get("target_value")
    delta, state = "—", "OPEN"
    tt = r.get("target_text") or ""
    no_target = tt.startswith("CANNOT DETERMINE") or tt.startswith("n/a")
    # A descriptive target (a band, a rule, a physical bound) cannot be
    # subtracted. But if the tool that produced the number asserted it and its
    # case PASSED, the row is settled — by the tool, which is the whole point.
    # Reporting it OPEN would be my grader claiming a delta it never computed.
    descriptive = bool(tt) and not isinstance(t, (int, float)) and not no_target
    if descriptive and m and m.get("from") == "ce-rf" and rf_verdict(m["case"]) == "PASS":
        rows.append({**r, "current": cur, "delta": "asserted by the tool",
                     "state": "MATCH", "source": f'ce-rf/out/{m["case"]}/verdict.json — PASS'})
        continue
    if cur is None:
        state = "CANNOT DETERMINE"
        if m and m.get("from") == "ce-rf" and rf_verdict(m["case"]) == "FAIL":
            src = f'ce-rf/out/{m["case"]}/verdict.json says FAIL — its numbers are not admissible'
            delta = "source case FAILED"
    elif no_target:
        state = "NO TARGET"
        delta = "target unknown"
    elif isinstance(cur, str):
        state = "MATCH" if cur == r.get("target_text") else "OPEN"
        delta = "0" if state == "MATCH" else "—"
    elif isinstance(t, (int, float)):
        d = cur - t
        tol = r.get("tolerance")
        delta = f"{d:+.4g} {r.get('unit','')}".strip()
        if tol is not None:
            state = "MATCH" if abs(d) <= tol else "OPEN"
        # A DELIBERATE DIVERGENCE IS A THIRD ANSWER AND IT MUST BE ABLE TO BE
        # WRONG. Writing "we chose not to match this" as a text target made
        # the row answer OPEN for the right value and for a deliberately wrong
        # one, so its state was not derived from any measurement. A divergence
        # names its own committed value; land on it and the row is DIVERGENT,
        # miss both it and the target and the row is OPEN like any other.
        _div = r.get("divergence")
        if (isinstance(_div, dict) and isinstance(_div.get("value"), (int, float))
                and abs(cur - _div["value"]) <= _div.get("tolerance", 0.0)):
            state = "DIVERGENT"
            delta += "  (by decision " + str(_div.get("decision", "?")) + ")"
        rel = abs(d) / abs(t) * 100 if t else None
        if rel is not None:
            delta += f"  ({rel:.1f}%)"
    rows.append({**r, "current": cur, "delta": delta, "state": state, "source": src})

order = {"OPEN": 0, "CANNOT DETERMINE": 1, "NO TARGET": 2,
         "DIVERGENT": 3, "MATCH": 4}
rows.sort(key=lambda x: (order[x["state"]], -(x.get("weight", 1))))
tally = {k: sum(1 for x in rows if x["state"] == k) for k in order}

def fmt(v, unit=""):
    if v is None: return "—"
    if isinstance(v, float): return f"{v:.4g} {unit}".strip()
    return f"{v} {unit}".strip()

CSS = """:root{--ink:#16181d;--dim:#5c6370;--line:#dfe3e8;--bg:#fff;--ok:#0a7d33;--warn:#a86500;--bad:#a11}
@media(prefers-color-scheme:dark){:root{--ink:#e8eaed;--dim:#9aa2ad;--line:#2c313a;--bg:#14161a;--ok:#4ec26f;--warn:#e0a233;--bad:#f0736a}}
*{box-sizing:border-box}body{margin:0;padding:2.5rem 1.5rem 6rem;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,"Helvetica Neue","PingFang SC",sans-serif}main{max-width:70rem;margin:0 auto}
h1{font-size:1.9rem;margin:0 0 .2rem;letter-spacing:-.02em}p.sub{color:var(--dim);margin:0 0 1.5rem}
table{border-collapse:collapse;width:100%;font-size:.9rem;margin:1.2rem 0}
th,td{text-align:left;vertical-align:top;padding:.5rem .65rem;border-bottom:1px solid var(--line)}
th{font-size:.75rem;text-transform:uppercase;letter-spacing:.05em;color:var(--dim)}
.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.b{display:inline-block;font-size:.7rem;font-weight:700;letter-spacing:.05em;padding:.12rem .4rem;border:1px solid currentColor;border-radius:3px}
.OPEN{color:var(--bad)}.CD{color:var(--warn)}.MATCH{color:var(--ok)}.DIV{color:var(--dim)}
code{font:.85em ui-monospace,Menlo,monospace;color:var(--dim);word-break:break-all}
.meta{color:var(--dim);font-size:.82rem;margin-top:2.5rem;padding-top:1rem;border-top:1px solid var(--line)}"""

p = [f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
     f'<title>halo — convergence against the real AirTag</title><style>{CSS}</style><main>',
     '<h1>Convergence against the real AirTag</h1>',
     f'<p class="sub">Generated {datetime.date.today().isoformat()} · '
     f'<b class="OPEN">{tally["OPEN"]} open</b> · '
     f'<b class="CD">{tally["CANNOT DETERMINE"]} cannot determine</b> · '
     f'<b class="MATCH">{tally["MATCH"]} match</b> · '
     f'{tally["DIVERGENT"]} divergent by decision · '
     f'{tally["NO TARGET"]} measured but Apple\'s value unknown</p>',
     '<p>Every parameter where our board can be compared to Apple\'s. TARGET is the real '
     'AirTag, cited. CURRENT is read out of a tool\'s own output file, so no row can claim a '
     'number nothing produced. The loop picks the largest open delta, changes the design, '
     're-measures, and rewrites this table. A target is never loosened to make a row pass.</p>',
     '<table><tr><th>Parameter</th><th>Target (real AirTag)</th><th>Current (halo)</th>'
     '<th>Delta</th><th>State</th><th>Source</th></tr>']
for x in rows:
    cls = {"OPEN": "OPEN", "CANNOT DETERMINE": "CD", "NO TARGET": "CD",
           "DIVERGENT": "DIV", "MATCH": "MATCH"}[x["state"]]
    tgt = x.get("target_text") or fmt(x.get("target_value"), x.get("unit", ""))
    p.append(f'<tr><td><b>{E(x["name"])}</b><br><code>{E(x.get("cite",""))}</code></td>'
             f'<td class="num">{E(tgt)}</td><td class="num">{E(fmt(x["current"], x.get("unit","")))}</td>'
             f'<td class="num">{E(str(x["delta"]))}</td>'
             f'<td><span class="b {cls}">{E(x["state"])}</span></td>'
             f'<td><code>{E(x.get("source") or "no tool has produced this yet")}</code></td></tr>')
p.append('</table>')
p.append(f'<p class="meta">Generated from <code>spec/convergence.json</code> by '
         f'<code>tools/gen_convergence.py</code>, which reads the tools\' own output files live. '
         f'Re-run it after any simulation to refresh every row.</p></main></html>')
(OUT / "CONVERGENCE.html").write_text("\n".join(p), encoding="utf-8")

md = ["# Convergence against the real AirTag", "",
      f"Generated {datetime.date.today().isoformat()}. "
      f"**{tally['OPEN']} open · {tally['CANNOT DETERMINE']} cannot determine · "
      f"{tally['NO TARGET']} measured but Apple's value unknown · "
      f"{tally['DIVERGENT']} divergent by decision · {tally['MATCH']} match**", "",
      "| parameter | target | current | delta | state |", "|---|---|---|---|---|"]
for x in rows:
    tgt = x.get("target_text") or fmt(x.get("target_value"), x.get("unit", ""))
    md.append(f'| {x["name"]} | {tgt} | {fmt(x["current"], x.get("unit",""))} | {x["delta"]} | **{x["state"]}** |')
(OUT / "CONVERGENCE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(f'{tally["OPEN"]} open, {tally["CANNOT DETERMINE"]} cannot determine, {tally["MATCH"]} match')
for x in rows:
    if x["state"] == "OPEN":
        print(f'  OPEN  {x["name"]}: target {x.get("target_text") or x.get("target_value")} vs {fmt(x["current"])} -> {x["delta"]}')
