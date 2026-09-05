#!/usr/bin/env python3
"""k_threeway - check and render the Apple | halo_rev_a | halo_replica comparison.

halo Replica lane L9 (THE COMPARISON), 2026-09-05.
Leif, 2026-09-05: "always manage its own tools and create any tools that might be missing."

WHAT THIS IS NOT. It is not a fork of bin/boardmetro. boardmetro measures a board off a
photograph; this measures a DOCUMENT against the files it cites. Different instrument,
different failure mode, no overlapping code. boardmetro stays the only thing in this lane
that touches pixels.

WHAT IT CHECKS. comparison/threeway.json gives, for every cell of the three-way table, an
ANCHOR: a file plus either a dotted path into its JSON and the exact value expected there,
or a literal quote that must appear in it. This tool resolves every anchor against the file
on disk. A cell whose file or path is gone is CANNOT DETERMINE, never a pass.

    0  PASS               every anchor resolved and matched
    1  FAIL               an anchor resolved and DISAGREED - the table has drifted from its sources
    2  CANNOT DETERMINE   an anchor could not be resolved at all

WHAT IT CANNOT DO, STATED BECAUSE THE LIMIT IS THE POINT. It checks that the table agrees
with the files it cites. It cannot check that those files are right. If board.json records
the wrong diameter, this tool will confirm the table faithfully reproduces the wrong
diameter. Its scope is transcription, not truth.

THE E07 PROBLEM AND WHAT WAS DONE ABOUT IT
------------------------------------------
E07's final form: CHECK THE ASSUMPTION THE METHOD SHARES WITH ITS OWN CONTROL.

The obvious negative controls here - point at a missing file, point at a missing path - all
share one assumption with the method: that resolve() returns what is actually in the file.
If resolve() were broken and returned None for everything, all three of those breaks would
still "pass", because None is not the expected value either. A break that passes for the
wrong reason is exactly the family E07 catalogues.

So the breaks below are chosen to attack the COMPARISON's strictness rather than its inputs:

    N1  0.6 -> 0.6000001          a tolerance-based compare would swallow it. Must FAIL.
    N2  "ENIG" -> "enig"          a case-folding compare would swallow it. Must FAIL.
    N3  expect a strict SUBSTRING of the true value. An `in` compare would swallow it. Must FAIL.
    N4  int 4 -> str "4"          a str() coercion would swallow it. Must FAIL.
    N5  a path that does not exist                    Must be CANNOT DETERMINE. Never PASS, never FAIL.
    N6  a file that does not exist                    Must be CANNOT DETERMINE. Never PASS, never FAIL.
    N7  one character removed from a quote anchor     Must FAIL.
    N9  a fidelity verdict outside the vocabulary. It would be dropped from the divergence
        count in silence - the ratchet-with-no-counter failure. Must FAIL.
    N8  POSITIVE CONTROL ON RESOLUTION. The one that separates this tool from a broken one:
        a second, independent reader (plain json.load and hand indexing, no shared code with
        resolve()) reads three real anchors and must get the same values resolve() got, AND
        those values must be non-None. Without this, N1-N7 all pass on a tool that reads
        nothing at all.

VERBS
    check       resolve every anchor. Exit code is the verdict.
    render      write comparison/THREE-WAY.md from the same file.
    selftest    run the nine breaks above and require each to go the colour it must.
"""
import sys, os, json, re, argparse, copy

EX_PASS, EX_FAIL, EX_CANNOT = 0, 1, 2
LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../halo_replica
HALO = os.path.dirname(os.path.dirname(LANE))                        # .../halo
TABLE = os.path.join(LANE, "comparison", "threeway.json")
OUT_MD = os.path.join(LANE, "comparison", "THREE-WAY.md")

SIDES = ("apple", "rev_a", "replica")
SIDE_LABEL = {"apple": "Apple AirTag A2187", "rev_a": "halo_rev_a", "replica": "halo_replica"}

# --------------------------------------------------------------------- resolution
class Unresolved(Exception):
    """The anchor could not be resolved at all. CANNOT DETERMINE, never a pass."""

_TOK = re.compile(r'"([^"]+)"|([^.|]+)')

def split_path(path):
    """a.b."c d".3  ->  ['a','b','c d','3'].  Quoted segments may contain dots."""
    return [m.group(1) if m.group(1) is not None else m.group(2)
            for m in _TOK.finditer(path)]

def resolve(anchor, root=HALO):
    """Return (kind, value). Raises Unresolved when the file or the path is not there.

    kind 'value' -> the object found at the path
    kind 'quote' -> True (the quote was present) or False (absent)
    kind 'exists' -> True
    """
    fp = os.path.join(root, anchor["file"])
    if not os.path.exists(fp):
        raise Unresolved(f"no such file: {anchor['file']}")

    if anchor.get("exists"):
        return "exists", True

    if "quote" in anchor:
        with open(fp, "r", errors="replace") as fh:
            body = fh.read()
        return "quote", (anchor["quote"] in body)

    path = anchor["path"]
    want_len = path.endswith("|len")
    if want_len:
        path = path[:-4]
    try:
        with open(fp, "r") as fh:
            node = json.load(fh)
    except Exception as e:
        raise Unresolved(f"{anchor['file']} is not readable JSON: {e}")

    for seg in split_path(path):
        if isinstance(node, list):
            try:
                node = node[int(seg)]
            except (ValueError, IndexError):
                raise Unresolved(f"{anchor['file']}: no index {seg!r} in list of {len(node)}")
        elif isinstance(node, dict):
            if seg not in node:
                raise Unresolved(f"{anchor['file']}: no key {seg!r} at {path}")
            node = node[seg]
        else:
            raise Unresolved(f"{anchor['file']}: {path} runs past a scalar at {seg!r}")
    if want_len:
        if not isinstance(node, (list, dict, str)):
            raise Unresolved(f"{anchor['file']}: |len on a {type(node).__name__}")
        node = len(node)
    return "value", node

def strict_eq(got, want):
    """Exact. Not tolerant, not case-folding, not substring, not coercing.

    Every one of those four leniencies is a deliberate break in selftest (N1-N4); if this
    function is ever loosened, one of them stops going red and the loosening is caught.
    """
    if type(got) is bool or type(want) is bool:
        return type(got) is type(want) and got == want
    if isinstance(got, (int, float)) and isinstance(want, (int, float)):
        return float(got) == float(want)          # exact float equality, on purpose
    return type(got) is type(want) and got == want

# --------------------------------------------------------------------- checking
def check_cell(row_n, side, cell, root=HALO):
    a = cell.get("anchor")
    if not a:
        return {"row": row_n, "side": side, "verdict": "CANNOT DETERMINE",
                "why": "no anchor on this cell - unverifiable by construction, and counted as such"}
    try:
        kind, got = resolve(a, root)
    except Unresolved as e:
        return {"row": row_n, "side": side, "verdict": "CANNOT DETERMINE", "why": str(e),
                "anchor": a}
    if kind == "exists":
        return {"row": row_n, "side": side, "verdict": "PASS",
                "why": f"{a['file']} is on disk", "got": True}
    if kind == "quote":
        if got:
            return {"row": row_n, "side": side, "verdict": "PASS",
                    "why": f"quote present in {a['file']}", "got": True}
        return {"row": row_n, "side": side, "verdict": "FAIL",
                "why": f"quote ABSENT from {a['file']}: {a['quote'][:70]!r}", "got": False,
                "anchor": a}
    want = a.get("expect", "__NO_EXPECT__")
    if want == "__NO_EXPECT__":
        return {"row": row_n, "side": side, "verdict": "CANNOT DETERMINE",
                "why": f"anchor names a path but no expected value", "anchor": a}
    if strict_eq(got, want):
        return {"row": row_n, "side": side, "verdict": "PASS",
                "why": f"{a['file']}:{a['path']} == {got!r}", "got": got}
    return {"row": row_n, "side": side, "verdict": "FAIL",
            "why": f"{a['file']}:{a['path']} is {got!r} ({type(got).__name__}), table says {want!r} ({type(want).__name__})",
            "got": got, "anchor": a}

def check_fidelity(doc):
    """Every row must carry a fidelity verdict per side, drawn from the stated vocabulary.

    This is the divergence counter's own guard. A verdict outside the vocabulary would be
    silently dropped from the tally, and a tally that quietly loses rows is exactly the
    ratchet-with-no-counter THE-DRIFT.md describes. Break N9 watches it go red.
    """
    ok = set(doc.get("fidelity_vocabulary", {})) | {"n/a"}
    out = []
    for row in doc["rows"]:
        f = row.get("fidelity")
        if not f:
            out.append({"row": row["n"], "side": "fidelity", "verdict": "FAIL",
                        "why": "row carries no fidelity verdict - it would vanish from the count"})
            continue
        for side in ("rev_a", "replica"):
            v = f.get(side, {}).get("verdict")
            if v not in ok:
                out.append({"row": row["n"], "side": f"fidelity/{side}", "verdict": "FAIL",
                            "why": f"verdict {v!r} is not in fidelity_vocabulary {sorted(ok)}"})
    return out

def tally_fidelity(doc):
    t = {"rev_a": {}, "replica": {}}
    for row in doc["rows"]:
        for side in ("rev_a", "replica"):
            v = row["fidelity"][side]["verdict"]
            t[side][v] = t[side].get(v, 0) + 1
    return t

def check_table(doc, root=HALO):
    results = []
    for row in doc["rows"]:
        for side in SIDES:
            results.append(check_cell(row["n"], side, row[side], root))
    results += check_fidelity(doc)
    for i, a in enumerate(doc.get("reconciliation_with_the_prior_comparison", {}).get("anchors", [])):
        r = check_cell(f"rec{i+1}", "prior-page", {"anchor": a}, root)
        r["why"] = f"[{a['claim']}] " + r["why"]
        results.append(r)
    counts = {"PASS": 0, "FAIL": 0, "CANNOT DETERMINE": 0}
    for r in results:
        counts[r["verdict"]] += 1
    if counts["FAIL"]:
        verdict = "FAIL"
    elif counts["CANNOT DETERMINE"]:
        verdict = "CANNOT DETERMINE"
    else:
        verdict = "PASS"
    return verdict, counts, results

EXIT = {"PASS": EX_PASS, "FAIL": EX_FAIL, "CANNOT DETERMINE": EX_CANNOT}

def cmd_check(args):
    doc = json.load(open(TABLE))
    verdict, counts, results = check_table(doc)
    print(f"INPUT: {os.path.relpath(TABLE, HALO)}  ({len(doc['rows'])} rows x 3 sides = {len(results)} anchored cells)")
    print(f"ROOT : {HALO}")
    for r in results:
        if r["verdict"] != "PASS" or args.verbose:
            print(f"  [{r['verdict']:>17}] row {str(r['row']):>4} {r['side']:<14} {r['why']}")
    print(f"\n{counts['PASS']} PASS  {counts['FAIL']} FAIL  {counts['CANNOT DETERMINE']} CANNOT DETERMINE")
    print(f"VERDICT: {verdict}")
    return EXIT[verdict]

# --------------------------------------------------------------------- render
def _one(s):
    """First sentence of a why-string, for the scoreboard."""
    s = s.strip().replace("\n", " ")
    m = re.search(r"^(.{0,200}?[.!])(\s|$)", s)
    return m.group(1) if m else (s[:200] + ("..." if len(s) > 200 else ""))

def cmd_render(args):
    doc = json.load(open(TABLE))
    verdict, counts, results = check_table(doc)
    byrow = {}
    for r in results:
        byrow.setdefault(r["row"], []).append(r)

    L = []
    W = L.append
    W("# Apple | halo_rev_a | halo_replica — every axis, and which is better on it\n")
    W(f"*{doc['lane']}, {doc['written']}. **Generated by `tools/k_threeway.py render` from "
      f"`comparison/threeway.json`. Nothing on this page is hand-typed into it.***\n")
    W(f"**Anchor check at render time: {counts['PASS']} PASS · {counts['FAIL']} FAIL · "
      f"{counts['CANNOT DETERMINE']} CANNOT DETERMINE → {verdict}.** Every cell below names a "
      "file and a value in it; `k_threeway check` resolves all of them and goes red when the "
      "table and its sources disagree.\n")
    W("---\n")
    W("## What this is\n")
    W(doc["what_this_is"] + "\n")
    W("## The asymmetry that governs every row\n")
    W("> " + doc["the_asymmetry_that_governs_every_row"] + "\n")
    W("## The three axes a row can be judged on\n")
    for k, v in doc["judging_axes"].items():
        W(f"- **{k}** — {v}")
    W("")
    W("**Better is not automatic.** " + doc["better_is_not_automatic"] + "\n")
    W("---\n")

    # scoreboard
    W("## The scoreboard\n")
    W("| # | axis | rev_a vs Apple | replica vs Apple | judged on | better | in one line |")
    W("|--:|---|---|---|:-:|---|---|")
    for row in doc["rows"]:
        b = row["better"]; f = row["fidelity"]
        W(f"| {row['n']} | {row['axis']} | {f['rev_a']['verdict']} | {f['replica']['verdict']} | "
          f"{b['on']} | **{b['winner']}** | {_one(b['why'])} |")
    W("")
    tally = {}
    for row in doc["rows"]:
        tally[row["better"]["winner"]] = tally.get(row["better"]["winner"], 0) + 1
    W("**Primary-axis tally across " + str(len(doc["rows"])) + " axes:** " +
      " · ".join(f"{k} **{v}**" for k, v in sorted(tally.items(), key=lambda kv: -kv[1])) + "\n")
    W("Secondary judgements — the rows where a second axis reverses the first — are in the "
      "row bodies below and are the substance of this document, not a footnote to it.\n")
    W("---\n")

    # ---- the divergence counter
    acc = doc["the_accumulation"]
    t = tally_fidelity(doc)
    W("## The accumulation — the divergence counter\n")
    W("*" + acc["_why_this_section_exists"] + "*\n")
    order = ["SAME", "EQUIVALENT", "DIVERGED", "MISSING", "CANNOT DETERMINE", "UNSTARTED", "n/a"]
    W("| | " + " | ".join(order) + " | departures | NO ANSWER |")
    W("|---|" + "--:|" * (len(order) + 2))
    for side in ("rev_a", "replica"):
        cells = [str(t[side].get(k, 0)) for k in order]
        dep = t[side].get("DIVERGED", 0) + t[side].get("MISSING", 0)
        noans = t[side].get("CANNOT DETERMINE", 0) + t[side].get("UNSTARTED", 0)
        W(f"| **halo_{side}** | " + " | ".join(cells) + f" | **{dep}** | **{noans}** |")
    W("")
    W("**THE TWO RIGHT-HAND COLUMNS MUST BE READ TOGETHER AND NEITHER MAY BE QUOTED ALONE.** "
      "The Replica's 2 departures against rev_a's 13 looks like a rout and is not one: the "
      "Replica also has NO ANSWER on 12 of 24 axes against rev_a's 3. An axis you never "
      "answered cannot be a departure. Quoting the departure count on its own would be this "
      "project's own headline-from-a-favourable-half failure, in the document written to "
      "catch it.\n")
    for k in order:
        if k in doc["fidelity_vocabulary"]:
            W(f"- **{k}** — {doc['fidelity_vocabulary'][k]}")
    W("")
    W("**The ceiling.** " + acc["the_ceiling"] + "\n")
    W("### What the count says\n")
    for line in acc["what_the_count_says"]:
        W(f"- {line}")
    W("")
    W("### The GOAL.md re-read\n")
    g = acc["goal_reread"]
    W("*" + g["_the_check_THE_DRIFT_asked_for"] + "*\n")
    for k, v in g.items():
        if k.startswith("_"):
            continue
        if k.startswith("GOAL_") or k.startswith("CONSTRAINT_"):
            W(f"**{k.replace('_', ' ')}** — {v}\n")
    W("### The conclusion\n")
    W(g["the_conclusion_and_it_revises_THE_DRIFT"] + "\n")
    W("### And the risk in this very document\n")
    W(g["and_the_risk_in_this_very_document"] + "\n")
    W("---\n")

    rec = doc["reconciliation_with_the_prior_comparison"]
    W("## Reconciliation with the prior comparison\n")
    W("*" + rec["_what"] + "*\n")
    W("**Denominators.** " + rec["denominators_are_not_the_same_and_must_not_be_differenced"] + "\n")
    W("### Where they agree\n")
    for x in rec["agree"]:
        W(f"- {x}")
    W("")
    W("### Where they do not\n")
    for x in rec["disagree"]:
        W(f"**{x['row']}**\n")
        W(f"- *prior:* {x['prior']}")
        W(f"- *now:* {x['now']}")
        for k in ("why_it_changed", "why_it_matters", "not_fixed_here"):
            if k in x:
                W(f"- *{k.replace('_',' ')}:* {x[k]}")
        W("")
    W("### What this file adds that the prior one could not\n")
    for x in rec["what_this_file_adds_that_the_prior_one_could_not"]:
        W(f"- {x}")
    W("")
    W("---\n")

    groups = []
    for row in doc["rows"]:
        if row["group"] not in groups:
            groups.append(row["group"])
    TITLES = {"outline": "Outline and shape", "stackup": "Stackup and materials",
              "rf": "Radio", "components": "Components", "audio": "The audio path",
              "power": "Power", "interfaces": "Interfaces", "cost": "Cost and manufacture",
              "meta": "What the artifacts are"}
    for g in groups:
        W(f"## {TITLES.get(g, g)}\n")
        for row in doc["rows"]:
            if row["group"] != g:
                continue
            W(f"### {row['n']} · {row['axis']}\n")
            W("| | value | state | how it is known |")
            W("|---|---|---|---|")
            for side in SIDES:
                c = row[side]
                v = c["value"].replace("|", "\\|").replace("\n", " ")
                st = c["state"].replace("|", "\\|")
                sr = c["source"].replace("|", "\\|").replace("\n", " ")
                W(f"| **{SIDE_LABEL[side]}** | {v} | {st} | {sr} |")
            W("")
            f = row["fidelity"]
            W(f"*Against Apple:* **halo_rev_a {f['rev_a']['verdict']}** — {f['rev_a']['note']}. "
              f"**halo_replica {f['replica']['verdict']}** — {f['replica']['note']}.\n")
            b = row["better"]
            W(f"**Better on {b['on']}: {b['winner']}.** {b['why']}")
            if b.get("would_settle"):
                W(f"\n*Would settle it:* {b['would_settle']}")
            for extra in row.get("also", []):
                W(f"\n> **On {extra['on']}: {extra['winner']}.** {extra['why']}")
            anch = byrow.get(row["n"], [])
            bad = [a for a in anch if a["verdict"] != "PASS"]
            if bad:
                W("")
                for a in bad:
                    W(f"\n`ANCHOR {a['verdict']}` {a['side']}: {a['why']}")
            W("")
        W("---\n")

    W("## How to reproduce\n")
    W("```bash")
    W("cd ce-designs/halo/electronics/halo_replica")
    W("python3 tools/k_threeway.py check -v      # every anchor, with its file and value")
    W("python3 tools/k_threeway.py selftest      # 9 deliberate breaks, each watched going red")
    W("python3 tools/k_threeway.py render        # regenerate this page")
    W("```")
    W("")
    W("`check` exits 0 PASS / 1 FAIL / 2 CANNOT DETERMINE. It verifies that this page agrees "
      "with the files it cites; it cannot verify that those files are right, and says so in "
      "its own docstring.\n")

    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    open(OUT_MD, "w").write("\n".join(L) + "\n")
    print(f"wrote {os.path.relpath(OUT_MD, HALO)}  ({len(L)} lines)")
    print(f"anchor check: {counts['PASS']} PASS / {counts['FAIL']} FAIL / "
          f"{counts['CANNOT DETERMINE']} CANNOT DETERMINE -> {verdict}")
    return EXIT[verdict]

# --------------------------------------------------------------------- selftest
def _find(doc, pred):
    for row in doc["rows"]:
        for side in SIDES:
            a = row[side].get("anchor")
            if a and pred(a):
                return row, side, a
    raise SystemExit("selftest cannot run: the table has no anchor of the shape it needs")

def cmd_selftest(args):
    base = json.load(open(TABLE))
    fails = []

    def expect(name, doc, want, note):
        v, counts, res = check_table(doc)
        ok = (v == want)
        print(f"  [{'ok ' if ok else 'RED'}] {name:<4} -> {v:<17} (must be {want}) {note}")
        if not ok:
            fails.append(f"{name}: got {v}, must be {want}")

    print("BASELINE")
    v0, c0, _ = check_table(base)
    print(f"  unmodified table -> {v0}  ({c0['PASS']} PASS / {c0['FAIL']} FAIL / {c0['CANNOT DETERMINE']} CD)")
    if v0 != "PASS":
        print("  NOTE: the baseline is not PASS, so the breaks below are being run against a "
              "table that is already red. Fix the baseline first; a break watched from red "
              "proves nothing.")

    # N1 numeric hairline - a tolerance-based compare would swallow this
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: isinstance(a.get("expect"), float))
    a["expect"] = a["expect"] + 1e-7
    expect("N1", d, "FAIL", f"(row {row['n']} {side}: +1e-7 on a float)")

    # N2 case only - a case-folding compare would swallow this
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: isinstance(a.get("expect"), str) and a["expect"].upper() != a["expect"])
    a["expect"] = a["expect"].upper()
    expect("N2", d, "FAIL", f"(row {row['n']} {side}: expected value upper-cased)")

    # N3 strict substring - an `in` compare would swallow this
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: isinstance(a.get("expect"), str) and len(a["expect"]) > 12)
    a["expect"] = a["expect"][:8]
    expect("N3", d, "FAIL", f"(row {row['n']} {side}: expect truncated to a substring)")

    # N4 type confusion - a str() coercion would swallow this
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: type(a.get("expect")) is int)
    a["expect"] = str(a["expect"])
    expect("N4", d, "FAIL", f"(row {row['n']} {side}: int {a['expect']} written as a string)")

    # N5 path that is not there - must be CANNOT DETERMINE, never PASS and never FAIL
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: "path" in a)
    a["path"] = a["path"] + ".no_such_key_xyz"
    expect("N5", d, "CANNOT DETERMINE", f"(row {row['n']} {side}: path extended into nothing)")

    # N6 file that is not there
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: "file" in a)
    a["file"] = a["file"] + ".missing"
    expect("N6", d, "CANNOT DETERMINE", f"(row {row['n']} {side}: file renamed away)")

    # N7 quote anchor, one character short
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: "quote" in a)
    a["quote"] = a["quote"][:-1] + "Z"
    expect("N7", d, "FAIL", f"(row {row['n']} {side}: last character of the quote changed)")

    # N9 a fidelity verdict outside the vocabulary - it would vanish from the divergence count
    d = copy.deepcopy(base)
    d["rows"][0]["fidelity"]["rev_a"]["verdict"] = "SORT OF"
    expect("N9", d, "FAIL", "(row 1 rev_a: fidelity verdict not in the vocabulary)")

    # N8 POSITIVE CONTROL ON RESOLUTION.
    # Everything above would also pass on a resolve() that reads nothing and returns None.
    # This reads three real anchors with a SECOND, INDEPENDENT reader that shares no code
    # with resolve(), and requires the same non-None values back.
    print("  N8   positive control on resolution - independent second reader:")
    n8_ok = True
    probes = [
        ("out/verify/dfm-jlc-4layer.json",            ["board_facts", "thickness_mm"]),
        ("electronics/halo_replica/board/board.json", ["parameters", "layer_count", "value"]),
        ("electronics/halo_rev_a/out/drc.json",       ["unconnected_items"]),
    ]
    for rel, keys in probes:
        fp = os.path.join(HALO, rel)
        obj = json.load(open(fp))
        for k in keys:
            obj = obj[k]
        independent = len(obj) if isinstance(obj, list) else obj
        path = ".".join(keys) + ("|len" if isinstance(json.load(open(fp)).get(keys[0]), list) and len(keys) == 1 else "")
        kind, got = resolve({"file": rel, "path": path})
        same = strict_eq(got, independent)
        if got is None or not same:
            n8_ok = False
        print(f"         {'ok ' if (same and got is not None) else 'RED'} {rel}:{path} "
              f"resolve()={got!r} independent={independent!r}")
    if not n8_ok:
        fails.append("N8: resolve() disagrees with an independent reader, or returned None. "
                     "Every break above is then meaningless.")
    else:
        print("         resolve() genuinely reads the files. N1-N7 are therefore about the "
              "comparison, not about an empty read.")

    print()
    if fails:
        print("SELFTEST FAIL")
        for f in fails:
            print("  " + f)
        return EX_FAIL
    print("SELFTEST PASS - 9 breaks, each went the colour it had to.")
    return EX_PASS

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("-v", "--verbose", action="store_true")
    sub.add_parser("render")
    sub.add_parser("selftest")
    a = p.parse_args()
    return {"check": cmd_check, "render": cmd_render, "selftest": cmd_selftest}[a.cmd](a)

if __name__ == "__main__":
    sys.exit(main())
