#!/usr/bin/env python3
"""s_packstatus.py — does the release pack's status match what its own command says?

THE GAP THIS EXISTS FOR, MEASURED 2026-09-05.

`spec/release-pack.json` gives each of the eleven artifacts a `status`
(READY / PARTIAL), a `reason`, an `evidence` line and, for ten of them, the
`command` that would prove it. `tools/gen_release_pack.py` **never runs any of
them.** Its only subprocess call is `git rev-parse`; every other use of
`status` is counting, sorting and rendering a badge. So all eleven statuses are
**hand-authored literals**, and the workshop's own rule is the opposite:
"`trust.json` is COMPUTED here, never hand-authored."

Being hand-authored is not the same as being wrong, and this tool exists
because the difference matters. Three were checked by hand on 2026-09-05:

    item 3  BOM identity     asserted READY   its command exits 0   AGREES
    item 4  CPL rotations    asserted READY   its command exits 0   AGREES
    item 9  test plan        asserted PARTIAL its selftest passes   conservative

Item 3 is worth dwelling on: VERIFICATION-DEBT V13 records 40 assertion
failures over 24 lines on that same BOM, including a screw terminal block
ordered as a 2.2 uF capacitor. It now reports 138 assertions, 0 fail. **The
defect was fixed and the debt row is stale.** Anyone reading V13 today and
relaying it would amplify a defect that no longer exists.

But item 5 shows the failure mode is real:

    item 5  "Panel drawing, stackup and materials"  asserted READY
            evidence: "proven on the O31.87 mm round board"
            this board:  25.6138 x 26.0000 mm   -- A DIFFERENT BOARD
            panel artifact in out/release/:  NONE

So the statuses are right by MAINTENANCE, not by MEASUREMENT, and nothing
tells anyone when one drifts. Item 5 is the proof that they drift.

WHY THIS TOOL DOES NOT RUN EVERYTHING. Several recorded commands are heavy --
a CAD kernel build, a firmware build, a solver, a `--live` price pull that
another lane has measured lying by 25x. Running all eleven on an 8 GB machine
that has kernel-panicked twice this week would be its own defect. Commands are
run only from an explicit CHEAP allowlist; everything else is reported
CANNOT DETERMINE with the reason, never as a pass.

Verbs
  audit     compare each asserted status against its own command where cheap
  artifacts flag items whose named deliverable is absent from the pack
  selftest  6 cases, including the control that a false READY is caught

Exit code IS the verdict: 0 PASS, 1 FAIL, 2 CANNOT DETERMINE.
"""
import json
import os
import subprocess
import sys

PASS, FAIL, CANNOT = 0, 1, 2
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SPEC = os.path.join(ROOT, "spec", "release-pack.json")

# Pure-python checkers that read files and exit in seconds. Anything that
# builds, solves, renders or hits a network stays OFF this list on purpose.
CHEAP = {
    1: ["python3", "tools/check_fabset.py", "out/release/board",
        "--board", "electronics/halo_rev_a/out/halo_rev_a.kicad_pcb",
        "--expect-layers", "4", "--expect-outline-mm", "26.0"],
    3: ["python3", "tools/check_bom_identity.py", "out/release/board/halo_rev_a-BOM.csv"],
    4: ["python3", "tools/check_cpl_rotations.py", "out/release/board",
        "--board", "electronics/halo_rev_a/out/halo_rev_a.kicad_pcb"],
    9: ["python3", "tools/gen_test_plan.py", "--selftest"],
}

# What each item must actually PUT IN THE PACK. A status is a claim about an
# artifact; an artifact that is not there cannot be READY whatever ran.
DELIVERABLE = {
    1: ["out/release/board/gerber"],
    3: ["out/release/board/halo_rev_a-BOM.csv"],
    4: ["out/release/board/halo_rev_a-CPL.csv"],
    5: ["out/release/board/STACKUP.md", "@panel"],   # @panel = any path matching *panel*
    9: ["out/release/TEST-PLAN.html"],
}


def load(spec=None):
    with open(spec or SPEC) as fh:
        return json.load(fh)["artifacts"]


def run_cheap(n, timeout=180):
    cmd = CHEAP.get(n)
    if cmd is None:
        return None, "no cheap checker recorded for this item; not run"
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, f"{' '.join(cmd[:3])} timed out after {timeout}s"
    except OSError as e:
        return None, f"{' '.join(cmd[:3])} could not run: {e}"
    return r.returncode, (r.stdout.strip().splitlines() or ["(no output)"])[-1][:110]


def artifact_missing(n):
    """Paths this item claims to deliver that are not in the pack."""
    missing = []
    for p in DELIVERABLE.get(n, []):
        if p == "@panel":
            hits = []
            for dirpath, _, files in os.walk(os.path.join(ROOT, "out", "release")):
                hits += [f for f in files if "panel" in f.lower()]
            if not hits:
                missing.append("a panel drawing (no file matching *panel* in out/release/)")
        elif not os.path.exists(os.path.join(ROOT, p)):
            missing.append(p)
    return missing


def cmd_audit(items):
    print("RELEASE PACK — asserted status vs the item's own command\n")
    worst = PASS
    for it in items:
        n, st = it["n"], it["status"]
        rc, note = run_cheap(n)
        if rc is None:
            verdict = "NOT RUN"
            worst = max(worst, CANNOT) if worst != FAIL else worst
        elif st == "READY" and rc != 0:
            verdict = "MISMATCH — asserted READY, its own command FAILS"
            worst = FAIL
        elif st == "READY" and rc == 0:
            verdict = "agrees"
        elif rc == 0:
            verdict = f"asserted {st}, command passes (conservative)"
        else:
            verdict = f"asserted {st}, command fails (consistent)"
        print(f"  {n:>2}  {st:<8} rc={'-' if rc is None else rc}  {verdict}")
        print(f"      {note}")
    print()
    return worst


def cmd_artifacts(items):
    print("RELEASE PACK — is the artifact each item claims actually in the pack?\n")
    worst = PASS
    for it in items:
        n, st = it["n"], it["status"]
        miss = artifact_missing(n)
        if not miss:
            if n in DELIVERABLE:
                print(f"  {n:>2}  {st:<8} present")
            continue
        tag = "FAIL — graded READY with a missing deliverable" if st == "READY" else "absent"
        if st == "READY":
            worst = FAIL
        print(f"  {n:>2}  {st:<8} {tag}")
        for m in miss:
            print(f"      MISSING: {m}")
        if n == 5:
            print(f"      and its evidence names a different board: {it['reason'][:96]}...")
    print()
    return worst



# Where an item's evidence lives, and therefore where its SIBLINGS live. The
# cherry-pick this catches is not a false citation -- every file item 6 cites
# really does pass -- it is a TRUE citation with a failing sibling left out.
EVIDENCE_TREES = {
    6: ["ce-spice/out", "ce-rf/out"],
}
WORKSHOP = os.path.abspath(os.path.join(ROOT, "..", ".."))


def _verdict_of(path):
    """PASS/FAIL/... out of a verdict.json, whichever schema it uses."""
    try:
        with open(path) as fh:
            d = json.load(fh)
    except Exception:                                    # noqa: BLE001
        return None
    for probe in (d, d.get("record") if isinstance(d.get("record"), dict) else None):
        if isinstance(probe, dict) and probe.get("verdict"):
            return probe["verdict"]
    return None


def classify(case):
    """Not every failing sibling is a defect, and treating them alike is how a
    real finding gets buried in noise. The FIRST run of this check flagged 17
    failing cases; 15 of them were fine.

      control     a case built to FAIL on purpose. Its FAIL is the check
                  WORKING -- e.g. halo-rim-ifa-coil-keepout-broken. Never flag.
      validation  the instrument measured against a known answer. A FAIL here
                  impeaches every number the instrument produces. ALWAYS flag.
      design      a geometry being iterated. Most variants in a sweep fail;
                  that is what a sweep is. Report, never flag.
    """
    if case.endswith("-broken") or "-broken-" in case:
        return "control"
    if case.startswith("validation-"):
        return "validation"
    return "design"


def cmd_evidence(items):
    """Flag a FAILING VALIDATION case sitting in a tree a READY item cites,
    that the item does not name. A status resting on a true citation with a
    failing sibling omitted is the hardest kind to catch by reading, because
    nothing the item says is false."""
    print("RELEASE PACK — failing results inside the trees an item cites\n")
    worst = PASS
    for it in items:
        trees = EVIDENCE_TREES.get(it["n"])
        if not trees:
            continue
        cited = it.get("evidence", "")
        named, unnamed = [], []
        for t in trees:
            base = os.path.join(WORKSHOP, t)
            if not os.path.isdir(base):
                print(f"  {it['n']:>2}  CANNOT DETERMINE — {t} not on disk")
                worst = CANNOT if worst == PASS else worst
                continue
            for case in sorted(os.listdir(base)):
                vp = os.path.join(base, case, "verdict.json")
                if not os.path.exists(vp):
                    continue
                v = _verdict_of(vp)
                (named if case in cited else unnamed).append((case, v, t))
        print(f"  item {it['n']} [{it['status']}] — {it['name']}")
        for case, v, t in named:
            print(f"      cited     {v or '?':<5} {t}/{case}")
        buckets = {"validation": [], "design": [], "control": []}
        for case, v, t in unnamed:
            buckets[classify(case)].append((case, v, t))
        for case, v, t in buckets["validation"]:
            flag = "  <-- A VALIDATION CASE FAILS AND IS NOT CITED" if v == "FAIL" else ""
            print(f"      not cited {v or '?':<5} [validation] {t}/{case}{flag}")
            if v == "FAIL" and it["status"] == "READY":
                worst = FAIL
        nf = [c for c, v, _ in buckets["design"] if v == "FAIL"]
        np_ = [c for c, v, _ in buckets["design"] if v != "FAIL"]
        print(f"      not cited [design]  {len(nf)} FAIL, {len(np_)} pass — "
              "iteration in a geometry sweep, NOT flagged")
        for c, v, _ in buckets["control"]:
            print(f"      not cited {v or '?':<5} [control] {c} — built to fail; "
                  "its FAIL is the check working, NOT flagged")
    print()
    if worst == FAIL:
        print("FAIL — a READY item cites a passing VALIDATION case while a failing")
        print("validation case sits beside it, uncited. A failing design variant is")
        print("iteration; a failing validation impeaches the instrument itself.")
    return worst


def cmd_selftest():
    items = load()
    n_ok = n_red = 0

    def check(name, got, ok, want):
        nonlocal n_ok, n_red
        print(f"  [{'ok  ' if ok else 'RED '}] {name}\n         want {want}\n         got  {got}")
        if ok:
            n_ok += 1
        else:
            n_red += 1

    print("s_packstatus selftest — 9 cases\n")

    check("the spec really carries 11 artifacts", len(items), len(items) == 11, 11)

    # THE LIVE FINDING. Item 5 is READY with no panel in the pack.
    m5 = artifact_missing(5)
    check("item 5 is READY with no panel artifact in the pack",
          m5, any("panel" in x for x in m5), "a missing-panel entry")

    # POSITIVE CONTROL: an item whose deliverable IS present must come back clean,
    # or the artifact check is just saying no to everything.
    check("item 3's deliverable is found (positive control)",
          artifact_missing(3), artifact_missing(3) == [], [])

    # NEGATIVE CONTROL: a fabricated READY item pointing at a path that cannot
    # exist MUST be caught. Without this the audit could be a rubber stamp.
    DELIVERABLE[99] = ["out/release/definitely-not-here.xyz"]
    fake = [{"n": 99, "status": "READY", "reason": "fabricated for the control"}]
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        v = cmd_artifacts(fake)
    del DELIVERABLE[99]
    check("a fabricated READY with a missing file is caught", v, v == FAIL, f"{FAIL} (FAIL)")

    # NEGATIVE CONTROL on the audit path: an item asserted READY whose command
    # exits non-zero must be a MISMATCH, not a pass.
    CHEAP[98] = ["python3", "-c", "import sys; sys.exit(3)"]
    with contextlib.redirect_stdout(io.StringIO()):
        v2 = cmd_audit([{"n": 98, "status": "READY", "reason": ""}])
    del CHEAP[98]
    check("a READY whose command exits non-zero is a MISMATCH", v2, v2 == FAIL, f"{FAIL} (FAIL)")

    # 7. THE LIVE FINDING: item 6 is READY and its evidence tree holds a FAIL
    #    it does not name.
    with contextlib.redirect_stdout(io.StringIO()):
        v6 = cmd_evidence([i for i in items if i["n"] == 6])
    check("item 6 READY with an uncited FAIL in its evidence tree", v6, v6 == FAIL, f"{FAIL} (FAIL)")

    # 8. NEGATIVE CONTROL: the same item marked PARTIAL must NOT be flagged --
    #    the check must key on READY, not fire on any failing sibling at all.
    p6 = [dict(i, status="PARTIAL") for i in items if i["n"] == 6]
    with contextlib.redirect_stdout(io.StringIO()):
        vp = cmd_evidence(p6)
    check("the same item as PARTIAL is not flagged", vp, vp != FAIL, f"not {FAIL}")

    # 9. NEGATIVE CONTROL on the classifier: a deliberately-broken case must
    #    NOT be what trips the check, and a design variant must not either.
    check("classifier: -broken is a control, validation- is validation, rest is design",
          [classify("halo-rim-ifa-coil-keepout-broken"),
           classify("validation-dipole-freespace"),
           classify("halo-rev-a-2g4-meander9-bare")],
          [classify("halo-rim-ifa-coil-keepout-broken"),
           classify("validation-dipole-freespace"),
           classify("halo-rev-a-2g4-meander9-bare")] == ["control", "validation", "design"],
          ["control", "validation", "design"])

    # An item with no cheap checker must be NOT RUN / CANNOT DETERMINE, never a pass.
    rc, note = run_cheap(7)
    check("an item with no cheap checker is NOT RUN, not a pass",
          f"rc={rc}", rc is None, "rc=None")

    print(f"\n{n_ok} ok, {n_red} red")
    return PASS if n_red == 0 else FAIL


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return CANNOT
    if argv[1] == "selftest":
        return cmd_selftest()
    items = load()
    if argv[1] == "audit":
        return cmd_audit(items)
    if argv[1] == "evidence":
        return cmd_evidence(items)
    if argv[1] == "artifacts":
        return cmd_artifacts(items)
    print(f"unknown verb {argv[1]!r}")
    return CANNOT


if __name__ == "__main__":
    sys.exit(main(sys.argv))
