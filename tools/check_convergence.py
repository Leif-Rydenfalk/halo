#!/usr/bin/env python3
"""check_convergence — audit the convergence table for rows that cannot be wrong.

Lane V1, 2026-09-04. `out/release/CONVERGENCE.md` is the page a reader uses to
decide how close halo is to the real AirTag. Its own header says *"CURRENT is
read live out of the tools' own verdict/measurement files wherever one exists,
so a row cannot claim a value no tool produced."* Three things make that untrue
today, and each of them produces a green row.

**1. The weight-10 antenna row is green off a run that failed.**
`tools/gen_convergence.py:25-33` reads `ce-rf/out/<case>/measurements.json` and
never opens `verdict.json`. Measured here, by me, on
`halo-rim-ifa-low-loss-laminate`:

  - the case's own `verdict.json` says **FAIL** (`gain_dBi` -8.333 vs >= -3.2)
  - `solver.log` says *"Max. number of timesteps was reached before the
    end-criteria of -40dB was reached"* — the solve was cut off
  - `raw.json` has **no `convergence` block at all**, so `solver_converged` is
    None, which the spec's `gte: 1` would grade CANNOT DETERMINE
  - across the whole 1-6 GHz sweep there are **zero upward reactance
    zero-crossings**; in the BLE band the reactance runs +23.7j to +25.5j.
    There is no resonance. The "2.425 GHz" figure is the minimum of a smooth
    |S11| curve from a non-resonant impedance.

  CONVERGENCE.md prints that as `2.44 GHz target / 2.425 GHz current / MATCH`.

**2. The physics-sanity row can never go green and can never go red.**
Its target is text and its current is a number, and `gen_convergence.py:60-77`
has no branch for that pair: `state` stays at its initialised `"OPEN"` forever.
The check added specifically to catch impossible antennas is a decoration.

**3. Three MATCH rows are hardcoded literals.** A row whose current value is
typed into `spec/convergence.json` cannot disagree with its target. Board
outline diameter reads `31.87 mm MATCH` while the board in the factory pack
measures 25.61 x 26.00 mm.

    python3 tools/check_convergence.py [--json out.json] [--ws PATH]

Exit 0 PASS · 1 FAIL · 2 CANNOT DETERMINE.

The nine assertions, each with the sentence it defeats:

  G1 row_can_change_state  could PASS while a row's verdict is the same whatever
                           the tool measured -- the decoration case
  G2 source_verdict_passes could PASS while the case it reads FAILED its own asserts
  G3 solver_converged      could PASS while the solve was cut off before convergence
  G4 physics_floor         could PASS while a wave travels faster than light
  G5 resonance_exists      could PASS while there is no resonance, only a dip
  G6 high_weight_measured  could PASS while a weight-10 claim is a typed literal
  G7 source_is_fresh       could PASS while the measurement predates the spec it grades
  G8 source_file_resolves  could PASS while a row names a measurement file that does
                           not exist, or a key inside it that does not
  G9 divergence_is_earned  could PASS while any inconvenient row is relabelled
                           "deliberate divergence" and stops reading OPEN
"""
import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

PASS, FAIL, CD = "PASS", "FAIL", "CANNOT DETERMINE"
RANK = {PASS: 0, CD: 1, FAIL: 2}
HALO = pathlib.Path(__file__).resolve().parent.parent


def jload(p):
    try:
        d = json.loads(pathlib.Path(p).read_text())
        return d.get("record", d)
    except Exception:
        return None


def file_measurement(base, path, pointer, reduce_=None):
    """A value read out of a verification artifact on disk. -> (value, why)

    `from: "literal"` means somebody typed the number into the spec, and G6
    exists because a typed number cannot disagree with its target. But three
    of halo's board rows had numbers that a tool HAD measured and written to
    disk — the copper-layer count, the finished thickness and the outline
    extent all sit in out/verify/dfm-jlc-4layer.json's board_facts — and they
    were still typed in by hand. This reads them instead, and returns None
    with a reason whenever the file or the key is not there, because a source
    that silently resolves to nothing is worse than a literal: it LOOKS
    measured.
    """
    f = (base / path)
    if not f.is_file():
        return None, f"no such file: {path}"
    d = jload(f)
    if d is None:
        return None, f"{path} is not readable JSON"
    cur = d
    for seg in pointer.split("."):
        if isinstance(cur, list):
            try:
                cur = cur[int(seg)]
                continue
            except (ValueError, IndexError):
                return None, f"{path}: no element {seg} in the list at this point"
        if not isinstance(cur, dict) or seg not in cur:
            return None, f"{path}: no key {pointer!r}"
        cur = cur[seg]
    if reduce_ == "max" and isinstance(cur, list) and cur:
        cur = max(cur)
    elif reduce_ == "min" and isinstance(cur, list) and cur:
        cur = min(cur)
    elif reduce_ and not isinstance(cur, list):
        return None, f"{path}: reduce {reduce_!r} needs a list, got {type(cur).__name__}"
    if isinstance(cur, (dict, list)):
        return None, (f"{path}: {pointer!r} is a {type(cur).__name__}, not a value — "
                      f"name a scalar or give a reduce")
    return cur, f"{path} -> {pointer}"


def rf_measurement(ws, case, key):
    r = jload(ws / "ce-rf" / "out" / case / "measurements.json")
    if not r:
        return None
    for holder in ("measurements", "results", "measured"):
        b = r.get(holder)
        if isinstance(b, dict) and key in b:
            v = b[key]
            return v.get("value") if isinstance(v, dict) else v
    return None


def state_of(row, cur):
    """Reproduce gen_convergence.py's state machine exactly, for one value.

    Copied deliberately rather than imported: G1 asks whether THAT machine can
    produce two different answers, and a check that shares the code it grades
    can only agree with it.
    """
    t = row.get("target_value")
    tt = row.get("target_text") or ""
    no_target = tt.startswith("CANNOT DETERMINE") or tt.startswith("n/a")
    div = row.get("divergence")
    state = "OPEN"
    if cur is None:
        state = "CANNOT DETERMINE"
    elif no_target:
        state = "NO TARGET"
    elif isinstance(cur, str):
        state = "MATCH" if cur == row.get("target_text") else "OPEN"
    elif isinstance(t, (int, float)):
        tol = row.get("tolerance")
        if tol is not None:
            state = "MATCH" if abs(cur - t) <= tol else "OPEN"
        # A DELIBERATE DIVERGENCE IS A THIRD ANSWER, AND IT HAS TO BE ABLE TO
        # BE WRONG. The board is 0.60 mm where Apple's is 0.30 mm, on purpose
        # (D17). Writing that as "no target" made the row answer OPEN for the
        # right value and for a deliberately wrong one, which is the decoration
        # this file hunts. A divergence therefore names its OWN committed
        # value: land on it and the row is DIVERGENT, miss both it and the
        # target and the row is OPEN like any other.
        if (isinstance(div, dict) and isinstance(div.get("value"), (int, float))
                and abs(cur - div["value"]) <= div.get("tolerance", 0.0)):
            state = "DIVERGENT"
    return state


def probe_values(row, cur):
    """Two candidate values OF THE TYPE THIS ROW ACTUALLY PRODUCES.

    Probing a numeric row with strings is how this check first missed the row
    it was written for: the physics-sanity row has a TEXT target and a NUMERIC
    current, and probing it with two strings made the state machine look like
    it worked. The probe has to be the shape of the real measurement.
    """
    t = row.get("target_value")
    if isinstance(cur, (int, float)) and not isinstance(cur, bool):
        base = t if isinstance(t, (int, float)) else cur
        return base, base * 100.0 + 12345.0
    if isinstance(t, (int, float)):
        return t, t * 100.0 + 12345.0
    if row.get("target_text"):
        return row["target_text"], "DEFINITELY-NOT-THE-TARGET"
    return cur, "DEFINITELY-NOT-THE-TARGET"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", default=str(HALO.parent.parent))
    ap.add_argument("--spec", default=str(HALO / "spec" / "convergence.json"))
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    ws = pathlib.Path(a.ws)

    spec = jload(a.spec)
    if not spec or "rows" not in spec:
        print(f"CANNOT DETERMINE: no convergence spec at {a.spec}", file=sys.stderr)
        return 2

    checks = []

    def add(name, row_name, verdict, why, value=None, rule=None):
        checks.append({"name": name, "row": row_name, "verdict": verdict,
                       "why": why, "value": value, "rule": rule})

    for r in spec["rows"]:
        n = r["name"]
        m = r.get("measure") or {}
        src = m.get("from")
        cur, src_why = None, None
        if src == "ce-rf":
            cur = rf_measurement(ws, m["case"], m["key"])
        elif src == "literal":
            cur = m.get("value")
        elif src == "file":
            cur, src_why = file_measurement(HALO, m.get("path", ""),
                                            m.get("pointer", ""), m.get("reduce"))
        elif src == "ce-spice-verdict":
            v = jload(ws / "ce-spice" / "out" / m["example"] / "verdict.json")
            cur = v.get("verdict") if v else None

        # ---- G1 row_can_change_state ------------------------------------
        right, wrong = probe_values(r, cur)
        s_right, s_wrong = state_of(r, right), state_of(r, wrong)
        tt = r.get("target_text") or ""
        honest_no_target = tt.startswith("CANNOT DETERMINE") or tt.startswith("n/a")
        if honest_no_target:
            add("row_can_change_state", r["name"], PASS,
                f"the row states no target ({tt[:48]}...) and reports NO TARGET; there is "
                f"nothing to compare and the row says so", value=s_right)
        elif s_right == s_wrong:
            add("row_can_change_state", n, FAIL,
                f"the state machine answers {s_right!r} for a correct value AND for a "
                f"deliberately wrong one ({wrong!r}) — this row's verdict is not derived "
                f"from any measurement", value=s_right)
        else:
            add("row_can_change_state", n, PASS,
                f"correct value -> {s_right}, wrong value -> {s_wrong}", value=s_right)

        # ---- G6 high_weight_measured ------------------------------------
        w = r.get("weight", 1)
        if src == "literal":
            state = state_of(r, cur)
            v = FAIL if (w >= 8 and state == "MATCH") else (CD if state == "MATCH" else PASS)
            add("high_weight_measured", n, v,
                f"current value is a literal typed into spec/convergence.json (weight {w}, "
                f"state {state}); no tool produced it and it cannot disagree with its target",
                value=cur)
        elif src and cur is None:
            # THE HOLE THIS CLOSES: `elif src:` used to PASS on the STRING in
            # the `from` field alone. Any source name that was not "literal"
            # earned a pass whether or not it had produced a number, so a row
            # pointing at a file that does not exist graded better than one
            # that honestly typed its value in. A source that measured nothing
            # is not a measurement.
            add("high_weight_measured", n, CD,
                f"the row names source {src!r} (weight {w}) and that source produced NO "
                f"VALUE" + (f": {src_why}" if src_why else "")
                + " — a named source that resolves to nothing is not a measurement",
                value=None)
        elif src:
            add("high_weight_measured", n, PASS,
                f"current value {cur!r} was READ from {src_why or src}, not typed into "
                f"the spec file", value=cur)
        else:
            add("high_weight_measured", n, CD,
                f"the row declares no measurement source at all (weight {w})")

        # ---- G9 divergence_is_earned ------------------------------------
        # DIVERGENT is a state that stops a row reading OPEN, so it is exactly
        # the kind of label somebody reaches for when a delta will not close.
        # Two things make it honest and both are checkable: the divergence
        # names a DECISION, and its committed value lies OUTSIDE the target's
        # own tolerance band. A "divergence" inside the band is a match wearing
        # a costume, and a divergence with no decision behind it is a shrug.
        div = r.get("divergence")
        if isinstance(div, dict):
            dv, dec = div.get("value"), div.get("decision")
            tol, tgt = r.get("tolerance"), r.get("target_value")
            if not dec:
                add("divergence_is_earned", n, FAIL,
                    "the row declares a divergence with no decision behind it — a "
                    "state that stops the row reading OPEN needs a named reason",
                    value=dv)
            elif not isinstance(dv, (int, float)) or not isinstance(tgt, (int, float)):
                add("divergence_is_earned", n, CD,
                    f"the divergence names {dv!r} against target {tgt!r}; one of them is "
                    f"not a number, so the two cannot be compared", value=dv)
            elif tol is not None and abs(dv - tgt) <= tol:
                add("divergence_is_earned", n, FAIL,
                    f"the divergence's own value {dv} is INSIDE the target's tolerance "
                    f"({tgt} +/- {tol}) — that is a MATCH relabelled, and it would hide a "
                    f"row that had actually converged", value=dv)
            else:
                add("divergence_is_earned", n, PASS,
                    f"divergence to {dv} by decision {dec}, {abs(dv - tgt):.4g} from the "
                    f"target {tgt} and outside its tolerance {tol} — a real gap, chosen "
                    f"and named", value=dv)

        # ---- G8 source_file_resolves ------------------------------------
        if src == "file":
            add("source_file_resolves", n, PASS if cur is not None else FAIL,
                (f"{m.get('path')} exists and {m.get('pointer')!r} reads {cur!r}"
                 if cur is not None else
                 f"the row names {m.get('path')} -> {m.get('pointer')!r} and it does not "
                 f"resolve: {src_why}"),
                value=cur)

        if src != "ce-rf":
            continue
        case = m["case"]
        out = ws / "ce-rf" / "out" / case

        # ---- G2 source_verdict_passes -----------------------------------
        v = jload(out / "verdict.json")
        state = state_of(r, cur)
        if v is None:
            add("source_verdict_passes", n, CD,
                f"{case} has no verdict.json: the number is read out of measurements.json "
                f"with nothing grading it")
        elif v.get("verdict") == "PASS":
            add("source_verdict_passes", n, PASS, f"{case} verdict.json says PASS")
        else:
            failed = [x["name"] for x in v.get("rows", []) if x.get("verdict") != "PASS"]
            add("source_verdict_passes", n,
                FAIL if state == "MATCH" else CD,
                f"{case} verdict.json says {v.get('verdict')} "
                f"(failing: {', '.join(failed) or 'unnamed'}) yet this row reads {state}",
                value=v.get("verdict"))

        # ---- G3 solver_converged ----------------------------------------
        conv = rf_measurement(ws, case, "solver_converged")
        if conv is None:
            add("solver_converged", n, FAIL if state == "MATCH" else CD,
                f"{case} records no solver_converged value — the run cannot be shown to have "
                f"finished, and this row reads {state}", value=None, rule={"gte": 1})
        elif float(conv) >= 1:
            add("solver_converged", n, PASS, f"{case} solver_converged = {conv}", value=conv)
        else:
            add("solver_converged", n, FAIL,
                f"{case} solver_converged = {conv}: the solve did not converge", value=conv)

        # ---- G4 physics_floor -------------------------------------------
        eps = rf_measurement(ws, case, "eps_eff_implied")
        if eps is None:
            add("physics_floor", n, CD, f"{case} records no eps_eff_implied")
        elif eps < 1.0:
            add("physics_floor", n, FAIL,
                f"{case} eps_eff_implied = {eps:.4f} < 1.0. A dielectric cannot speed a wave "
                f"up: the reported resonance is ABOVE the free-space quarter-wave frequency "
                f"of the antenna's own arm, which is impossible. The spec's own floor of 0.64 "
                f"admits it; a physical law is not a tolerance",
                value=round(eps, 4), rule={"gte": 1.0})
        else:
            add("physics_floor", n, PASS,
                f"{case} eps_eff_implied = {eps:.4f} >= 1.0", value=round(eps, 4))

        # ---- G5 resonance_exists ----------------------------------------
        if "res" in m["key"] or "f_res" in m["key"]:
            ser = rf_measurement(ws, case, "f_series_res_GHz")
            if ser is None:
                add("resonance_exists", n, FAIL if state == "MATCH" else CD,
                    f"{case} has no f_series_res_GHz: the reactance never crosses zero "
                    f"anywhere in the sweep, so there is no resonance — only a dip in |S11|. "
                    f"This row reads {state} on a frequency that is not a resonance")
            else:
                add("resonance_exists", n, PASS,
                    f"{case} f_series_res_GHz = {ser} — a real reactance zero-crossing",
                    value=ser)

        # ---- G7 source_is_fresh -----------------------------------------
        spec_f = ws / "ce-rf" / "specs" / f"{case}.json"
        meas_f = out / "measurements.json"
        if not spec_f.is_file() or not meas_f.is_file():
            add("source_is_fresh", n, CD,
                f"cannot compare: spec {spec_f.name} or measurements.json missing")
        else:
            age = meas_f.stat().st_mtime - spec_f.stat().st_mtime
            add("source_is_fresh", n, PASS if age >= 0 else FAIL,
                f"{case} measurements.json is {abs(age):.0f} s "
                + ("newer than" if age >= 0 else "OLDER than") + " its spec",
                value=round(age, 1), rule={"gte": 0})

    tally = {PASS: 0, FAIL: 0, CD: 0}
    for c in checks:
        tally[c["verdict"]] += 1
    worst = max((c["verdict"] for c in checks), key=lambda v: RANK[v]) if checks else CD

    out = {"$halo": 1, "tool": "tools/check_convergence.py",
           "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "spec": str(pathlib.Path(a.spec).resolve()),
           "verdict": worst, "counts": tally, "checks": checks,
           "command": "python3 " + " ".join(sys.argv)}
    if a.json:
        pathlib.Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.json).write_text(json.dumps(out, indent=1) + "\n")

    if not a.quiet:
        print("# check_convergence — spec/convergence.json")
        for c in checks:
            if c["verdict"] == PASS:
                continue
            print(f"  {c['verdict']:<16} {c['name']:<22} {c['row']}")
            print(f"      {c['why']}")
        print(f"{worst}: {tally[PASS]} pass, {tally[FAIL]} fail, {tally[CD]} cannot determine")
    return {PASS: 0, FAIL: 1, CD: 2}[worst]


if __name__ == "__main__":
    sys.exit(main())
