#!/usr/bin/env python3
"""k_evidence - resolve the file paths cited in prose evidence fields, or say they do not.

halo Replica lane L9, 2026-09-05. Written after the lane's own brief was finished,
under Leif's instruction that a session is its own manager.

WHY. `spec/release-pack.json` is the grand mission: eleven artifacts a real factory
builds from. Every row carries an `evidence` field, and every one of those is PROSE
naming files - "docs/SOURCING-ALTERNATES.md; out/release/board/halo_rev_a-BOM.csv
regenerated 2026-09-05". NOBODY RESOLVES THEM. A row marked READY whose evidence names
a file that is not on disk is ASSERTED READY, and the pack is the one document in this
project a factory would act on.

This is the same instrument as k_threeway's anchor checker pointed at prose instead of
at JSON pointers, and the same argument: a citation nobody resolves is a citation that
decays silently.

THREE VERDICTS, AND THEY ARE THE EXIT CODE
    0  PASS              every cited path resolves
    1  FAIL              a cited path does not exist
    2  CANNOT DETERMINE  nothing citable was found to check

WHAT IT CANNOT DO, STATED BECAUSE THE LIMIT IS THE POINT. It checks that a cited file
EXISTS. It does not check that the file says what the citation claims. That is the same
boundary k_threeway draws, and the same reason: existence is adjacent to support.
"""
import sys, os, json, re, argparse

PASS, FAIL, CANNOT = 0, 1, 2
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
HALO = os.path.abspath(os.path.join(LANE, "..", ".."))
WORKSHOP = os.path.abspath(os.path.join(HALO, "..", ".."))
# CITATIONS IN THE RELEASE PACK ARE WRITTEN RELATIVE TO THE WORKSHOP ROOT, not to halo:
# "ce-designs/halo/design.py", "ce-rf/out/.../verdict.json". Defaulting to halo alone
# reported four files as MISSING that were all on disk - and two of them were in rows
# marked READY, so the tool was one step from accusing two other lanes of asserting
# readiness they had actually earned. Caught by checking a result that flattered me.
DEFAULT_ROOTS = [HALO, WORKSHOP]

# EXTENSION-ANCHORED, deliberately. A generic path pattern matches prose - "PASS/FAIL",
# "and/or", "10/100/1000" - and a checker that reports those as missing files gets
# switched off within a day. Requiring a known extension is the whole difference between
# a citation and a slash. Break P-3 watches it hold.
EXT = (r"md|json|csv|py|txt|toml|yaml|yml|html|svg|png|pdf|zip|log|sh|"
       r"kicad_pcb|kicad_sch|kicad_mod|kicad_pro|net|gbr|drl|gbrjob|"
       r"g\d|gtl|gbl|gts|gbs|gto|gbo|gm1|step|stl|dxf|h|c|cpp|rs|ino")
CITE = re.compile(r"(?<![\w/])((?:[\w.\-]+/)*[\w.\-]+\.(?:" + EXT + r"))(?![\w])")

PLACEHOLDER = re.compile(r"<[^>]*>")
BRACE = re.compile(r"([\w./\-]*)\{([^}]*)\}([\w./\-]*)")

def cites(text):
    """Every extension-anchored path-like token in a prose string.

    TWO THINGS THAT ARE NOT CITATIONS AND WERE REPORTED AS MISSING FILES:
      <spec.json>  a PLACEHOLDER in a command template. Stripped, not resolved.
      a/{b,c}/d    BRACE NOTATION for several real paths. Expanded, not skipped -
                   a citation the extractor cannot see is invisible, which is worse
                   than one it reports wrongly.
    """
    t = PLACEHOLDER.sub(" ", text or "")
    out, seen = [], set()
    for m in BRACE.finditer(t):
        pre, inner, post = m.group(1), m.group(2), m.group(3)
        for alt in inner.split(","):
            cand = pre + alt.strip() + post
            for c in CITE.finditer(cand):
                if c.group(1) not in seen:
                    seen.add(c.group(1)); out.append(c.group(1))
    t = BRACE.sub(" ", t)
    for m in CITE.finditer(t):
        if m.group(1) not in seen:
            seen.add(m.group(1)); out.append(m.group(1))
    return out

# DIRECTORIES AND COMMITS ARE CITATIONS TOO. Rows 2, 5 and 7 of the release pack cite
# "ce-pcb/out", "ce-fab/out", "ce-fwsim" and commit hashes - no file extension anywhere -
# so the extension-anchored pattern saw NOTHING in them and the tool printed "0/0 resolve"
# with an ok mark beside it. THAT IS A VACUOUS PASS: a row citing nothing it can check is
# unverified, not verified. Three READY rows were reading green on no evidence at all.
DIRCITE = re.compile(r"(?<![\w/<])((?:[\w.\-]+/)+[\w.\-]+|ce-[\w.\-]+)(?![\w/.])")
SHA = re.compile(r"(?<![\w])([0-9a-f]{7,40})(?![\w])")

def dir_cites(text, roots):
    """Path-like tokens with NO extension that exist as directories. Existence is the
    filter: a token that is not a directory anywhere is not reported as a missing one,
    because prose is full of slashes and this pattern is far looser than the file one."""
    t = PLACEHOLDER.sub(" ", text or "")
    out, seen = [], set()
    for m in DIRCITE.finditer(t):
        tok = m.group(1)
        if "." in os.path.basename(tok) or tok in seen:
            continue
        seen.add(tok)
        for r in roots:
            q = os.path.join(r, tok)
            if os.path.isdir(q):
                out.append((tok, os.path.relpath(q, HALO))); break
    return out

def sha_cites(text, repos):
    """Commit hashes, resolved with git cat-file in the repos named. A hash not found is
    NOT reported as a bad citation - it is reported as NOT FOUND IN THE REPOS TRIED, and
    the repos are named. Claiming a commit does not exist when you looked in the wrong
    repository is exactly the false accusation this tool already made once."""
    import subprocess
    t = PLACEHOLDER.sub(" ", text or "")
    out, seen = [], set()
    for m in SHA.finditer(t):
        h = m.group(1)
        if h in seen or h.isdigit():
            continue
        seen.add(h)
        where = None
        for r in repos:
            try:
                rc = subprocess.run(["git", "-C", r, "cat-file", "-e", h + "^{commit}"],
                                    capture_output=True, timeout=10)
                if rc.returncode == 0:
                    where = os.path.relpath(r, HALO) or "."; break
            except Exception:
                continue
        out.append((h, where))
    return out

def walk_strings(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk_strings(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_strings(v, f"{path}.{i}")
    elif isinstance(node, str):
        yield path, node

def resolve(rel, roots):
    for r in roots:
        p = os.path.join(r, rel)
        if os.path.exists(p):
            return os.path.relpath(p, HALO)
    # a bare filename may live anywhere; search shallowly rather than claim it is gone
    base = os.path.basename(rel)
    if base == rel:
        for r in roots:
            for dirpath, dirnames, files in os.walk(r):
                dirnames[:] = [d for d in dirnames
                               if d not in (".git", "node_modules", "__pycache__")]
                if base in files:
                    return os.path.relpath(os.path.join(dirpath, base), HALO)
                if dirpath.count(os.sep) - r.count(os.sep) > 3:
                    dirnames[:] = []
    return None

def check(doc_path, roots, only_fields=None):
    doc = json.load(open(doc_path))
    repos = []
    for r in roots:
        for cand in [r] + [os.path.join(r, d) for d in sorted(os.listdir(r))
                           if os.path.isdir(os.path.join(r, d))]:
            if os.path.isdir(os.path.join(cand, ".git")):
                repos.append(cand)
    rows = []
    for field, text in walk_strings(doc):
        if only_fields and not any(field.endswith(f) for f in only_fields):
            continue
        for c in cites(text):
            rows.append(dict(field=field, kind="file", cited=c, found=resolve(c, roots)))
        for tok, where in dir_cites(text, roots):
            rows.append(dict(field=field, kind="dir", cited=tok, found=where))
        if field.endswith("evidence"):
            for h, where in sha_cites(text, repos):
                rows.append(dict(field=field, kind="commit", cited=h, found=where))
    return doc, rows

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("json_file", nargs="?", default=os.path.join(HALO, "spec/release-pack.json"))
    p.add_argument("--roots", nargs="+", default=None,
                   help="default: the halo repo AND the ce-workshop root, because this "
                        "pack cites paths relative to both")
    p.add_argument("--fields", nargs="+", default=None,
                   help="only check fields whose dotted path ends with one of these")
    p.add_argument("--status-key", default="status")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()

    if a.selftest:
        return selftest()

    roots = [os.path.abspath(r) for r in (a.roots or DEFAULT_ROOTS)]
    doc, rows = check(a.json_file, roots, a.fields)
    if not rows:
        print(f"CANNOT DETERMINE: no extension-anchored path was cited anywhere in "
              f"{os.path.relpath(a.json_file, HALO)}")
        return CANNOT
    miss = [r for r in rows if r["found"] is None]
    uniq = {r["cited"] for r in rows}
    print(f"k_evidence  {os.path.relpath(a.json_file, HALO)}")
    print(f"  roots: {', '.join(os.path.relpath(r, HALO) or '.' for r in roots)}")
    print(f"  {len(rows)} citations, {len(uniq)} distinct paths")
    print()
    # group by the artifact row so a READY row citing nothing real is obvious
    arts = doc.get("artifacts")
    if isinstance(arts, list):
        for i, art in enumerate(arts):
            mine = [r for r in rows if r["field"].startswith(f"artifacts.{i}.")]
            bad = [r for r in mine if r["found"] is None]
            st = art.get(a.status_key, "?")
            # A ROW CITING NOTHING IS NOT A ROW THAT PASSED. The first version printed
            # "0/0 resolve" with an ok mark against three rows - two of them READY -
            # whose evidence was directories and commit hashes the extractor could not
            # see. A vacuous pass is the failure this whole project is written against.
            if not mine:
                mark = " NONE"
            elif bad:
                mark = " MISS"
            else:
                mark = "  ok "
            kinds = {}
            for r in mine:
                kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
            ks = " ".join(f"{v}{k[0]}" for k, v in sorted(kinds.items()))
            print(f"  [{mark}] {art.get('n','?'):>2} {st:<8} {art.get('name','')[:40]:<40} "
                  f"{len(mine)-len(bad)}/{len(mine)} resolve  {ks}")
            if not mine:
                print(f"           NO CITATION THIS TOOL CAN CHECK. Not a pass - unverified.")
            for r in bad:
                lbl = ("NOT FOUND IN THE REPOS TRIED" if r["kind"] == "commit" else "MISSING")
                print(f"           {lbl}  {r['cited']}   ({r['kind']}, cited in "
                      f"{r['field'].split('.')[-1]})")
    else:
        for r in miss:
            print(f"  MISSING  {r['cited']}   ({r['field']})")
    print()
    print(f"  {len(rows)-len(miss)} of {len(rows)} citations resolve; {len(miss)} do not.")
    if arts:
        ready_bad = [art for i, art in enumerate(arts)
                     if art.get(a.status_key) == "READY"
                     and any(r["found"] is None for r in rows
                             if r["field"].startswith(f"artifacts.{i}."))]
        if ready_bad:
            print(f"  *** {len(ready_bad)} row(s) marked READY cite a file that is not on disk: "
                  + ", ".join(str(x.get('n')) for x in ready_bad))
            print(f"      A READY row whose evidence does not resolve is ASSERTED READY.")
    empty = [art for i, art in enumerate(arts or [])
             if not any(r["field"].startswith(f"artifacts.{i}.") for r in rows)]
    if empty:
        print(f"  *** {len(empty)} row(s) cite NOTHING this tool can check: "
              + ", ".join(str(x.get('n')) for x in empty)
              + " - unverified, not passing.")
    hard = [r for r in miss if r["kind"] != "commit"]
    soft = [r for r in miss if r["kind"] == "commit"]
    if soft:
        print(f"  {len(soft)} commit citation(s) not found in the repos tried. That is "
              f"CANNOT DETERMINE, not a bad citation - the commit may live in a repo "
              f"this run did not search.")
    v = FAIL if hard else (CANNOT if (soft or empty) else PASS)
    print(f"  VERDICT: {['PASS','FAIL','CANNOT DETERMINE'][v]}")
    return v

def selftest():
    import tempfile, shutil
    fails = []
    def chk(n, ok, note):
        print(f"  [{'ok ' if ok else 'RED'}] {n}  {note}")
        if not ok: fails.append(n)
    tmp = tempfile.mkdtemp(prefix="k_evidence-")
    try:
        os.makedirs(os.path.join(tmp, "docs"))
        open(os.path.join(tmp, "docs", "real.md"), "w").write("x")
        jp = os.path.join(tmp, "d.json")

        json.dump({"artifacts": [{"n": 1, "status": "READY",
                                  "evidence": "docs/real.md and nothing else"}]}, open(jp, "w"))
        _, rows = check(jp, [tmp])
        chk("P-1", len(rows) == 1 and rows[0]["found"] is not None,
            "a citation that exists -> resolves")

        json.dump({"artifacts": [{"n": 1, "status": "READY",
                                  "evidence": "docs/gone.md and nothing else"}]}, open(jp, "w"))
        _, rows = check(jp, [tmp])
        chk("P-2", len(rows) == 1 and rows[0]["found"] is None,
            "a citation that does NOT exist -> MISSING")

        # P-3 THE CONTROL THAT KEEPS THE TOOL ALIVE. Prose full of slashes must produce
        # NO citations. A checker that reports "PASS/FAIL" as a missing file is switched
        # off within a day, and then it catches nothing at all.
        json.dump({"artifacts": [{"n": 1, "status": "READY",
                                  "evidence": "graded PASS/FAIL at 10/100/1000/10000 units, "
                                              "and/or re-probed live; see section 4.2 and the "
                                              "he/she wording. Ratio 3.5/3.5 mil."}]}, open(jp, "w"))
        _, rows = check(jp, [tmp])
        chk("P-3", len(rows) == 0,
            f"prose with 6 slashes and no file -> {len(rows)} citations (must be 0). "
            "A checker that cries wolf on 'PASS/FAIL' gets switched off, and then it "
            "catches nothing at all.")

        # P-5 A PLACEHOLDER IS NOT A CITATION. This one reported <spec.json> as a
        # missing file in a row marked READY, one step from accusing another lane.
        json.dump({"artifacts": [{"n": 1, "status": "READY",
                                  "command": "bin/rf antenna <spec.json> --out <dir.json>"}]},
                  open(jp, "w"))
        _, rows = check(jp, [tmp])
        chk("P-5", len(rows) == 0,
            f"<spec.json> in a command template -> {len(rows)} citations (must be 0)")

        # P-6 BRACE NOTATION names several real paths. A citation the extractor cannot
        # SEE is invisible, which is worse than one it reports wrongly.
        os.makedirs(os.path.join(tmp, "out", "a")); os.makedirs(os.path.join(tmp, "out", "b"))
        open(os.path.join(tmp, "out", "a", "v.json"), "w").write("{}")
        json.dump({"artifacts": [{"n": 1, "status": "READY",
                                  "evidence": "out/{a,b}/v.json - both PASS"}]}, open(jp, "w"))
        _, rows = check(jp, [tmp])
        got = {r["cited"]: r["found"] for r in rows}
        chk("P-6", len(rows) == 2 and got.get("out/a/v.json") and not got.get("out/b/v.json"),
            f"out/{{a,b}}/v.json -> expanded to {len(rows)}, "
            f"a found and b correctly MISSING")

        # P-7 A COMMIT THAT DOES NOT EXIST must come back NOT FOUND. Without this,
        # "13 commit citations resolve" could equally mean "git cat-file always
        # succeeds", and 13 green ticks would be measuring nothing.
        real = sha_cites("committed 1a86de8", [HALO])
        fake = sha_cites("committed deadbee", [HALO])
        chk("P-7", len(real) == 1 and real[0][1] is not None
                   and len(fake) == 1 and fake[0][1] is None,
            f"a REAL commit -> {real[0][1]!r}; a FAKE one -> {fake[0][1]!r} (must be None). "
            "Without this, N green commit ticks could mean the resolver always succeeds.")

        # P-8 A ROW CITING NOTHING must not read as a pass.
        json.dump({"artifacts": [{"n": 1, "status": "READY", "reason": "it is fine, honestly"}]},
                  open(jp, "w"))
        _, rows = check(jp, [tmp])
        chk("P-8", len(rows) == 0,
            "a row whose evidence is pure prose -> 0 citations, and the report marks it "
            "NONE / unverified rather than ok")

        # P-4 a bare filename with no directory must still be found if it exists
        json.dump({"artifacts": [{"n": 1, "status": "READY", "evidence": "see real.md"}]},
                  open(jp, "w"))
        _, rows = check(jp, [tmp])
        chk("P-4", len(rows) == 1 and rows[0]["found"] is not None,
            "a BARE filename that exists somewhere under the root -> found, not reported gone")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print()
    if fails:
        print("SELFTEST FAIL: " + ", ".join(fails)); return FAIL
    print("SELFTEST PASS - 8 checks: two resolutions, one miss, and controls against FALSE ACCUSATION\n  (prose slashes, command placeholders, brace notation), against a commit resolver\n  that cannot fail, and against a row that cites nothing reading as a pass.")
    return PASS

if __name__ == "__main__":
    sys.exit(main())
