#!/usr/bin/env python3
"""p_provenance.py -- find checks whose SUBJECT is the artefact their INPUT came from.

Lane L5b BOARD BUILD.  Exit 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

WHY THIS EXISTS
  E07 entry 33.  `p_compare.py`'s X5 measured 4.23x enrichment of component-marker luma
  over 4000 random annulus positions.  It had a real negative control.  It had a real
  break, and the break worked -- 4.23x collapses to 1.44x under a 12 deg rotation.
  Every property this project normally demands was present.

  And the markers were extracted from the very image the check sampled.  The
  circularity sat in the DATA PROVENANCE, one file upstream of anything the check could
  see, so NO amount of reading the check reveals it.  It shipped, and I quoted it to two
  sessions and into the changelog.

  That defect is invisible to code review, so it needs a tool.

WHAT IT DOES
  For each tool: collect (a) the IMAGES it opens, and (b) the JSON files it loads and
  what image THOSE declare as their own source.  Where the two sets intersect, the tool
  is measuring a derived quantity against the artefact it was derived from -- a
  CANDIDATE, not a verdict.

WHAT IT IS NOT
  It is a CANDIDATE FINDER and it says so in every output.  A candidate is confirmed by
  reading the tool, because an intersection can be legitimate: a registration round-trip
  SHOULD sample its own source, and it is honest as long as it is named that way.
  Unresolvable references are COUNTED AND LISTED, never silently dropped -- a scanner
  that quietly skips what it cannot parse reports a clean sheet for a directory it never
  read.

CONTROLS
  P1 positive  p_compare.py MUST be flagged. It is the known true positive that caused
               this tool, and if it is not flagged the scanner is not working.
  P2 negative  a synthetic tool that samples one image while loading provenance naming
               a DIFFERENT one must NOT be flagged.
  P3 coverage  every unresolved reference is counted and named. Coverage is printed as
               a fraction, and a low fraction is a CANNOT DETERMINE, not a pass.
"""
import argparse, ast, glob, json, os, sys

PASS, FAIL, CANNOT = 0, 1, 2
HERE = os.path.dirname(os.path.abspath(__file__))
REPL = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(REPL))

IMG_HINT = ("images/airtag", ".jpg", ".jpeg", ".png")
PROV_KEYS = ("image", "source", "source_image", "photo", "image_basename")


def say(*a):
    print(*a, file=sys.stderr)


def string_literals(path):
    """Every string constant in the file, with no execution."""
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    except SyntaxError as e:
        return None, f"unparseable: {e}"
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    return out, None


def images_of(lits):
    return {s for s in lits
            if any(h in s for h in IMG_HINT) and "images" in s or
            (s.endswith((".jpg", ".jpeg")) and "/" not in s)}


def jsons_of(lits):
    return {s for s in lits if s.endswith(".json")}


def resolve_json(name, unresolved):
    """Find a named json under the replica tree and return the images IT declares."""
    cands = []
    base = os.path.basename(name)
    for d in ("metrology", "evidence", "board/outline", "board", "out", "."):
        p = os.path.join(REPL, d, base)
        if os.path.exists(p):
            cands.append(p)
    if not cands:
        unresolved.append(name)
        return set()
    imgs = set()
    for p in cands[:1]:
        try:
            d = json.load(open(p))
        except Exception as e:
            unresolved.append(f"{name} ({e})")
            return set()
        if not isinstance(d, dict):
            return set()
        for k in PROV_KEYS:
            v = d.get(k)
            if isinstance(v, str) and any(h in v for h in IMG_HINT):
                imgs.add(os.path.basename(v))
        # one level down, for files that nest their source
        for v in d.values():
            if isinstance(v, dict):
                for k in PROV_KEYS:
                    w = v.get(k)
                    if isinstance(w, str) and any(h in w for h in IMG_HINT):
                        imgs.add(os.path.basename(w))
    return imgs


def scan(paths):
    rows, unresolved, unparsed = [], [], []
    for p in sorted(paths):
        lits, err = string_literals(p)
        if lits is None:
            unparsed.append((os.path.basename(p), err))
            continue
        sampled = {os.path.basename(s) for s in images_of(lits)}
        js = jsons_of(lits)
        derived = set()
        for j in js:
            derived |= resolve_json(j, unresolved)
        overlap = sampled & derived
        rows.append(dict(tool=os.path.basename(p), samples=sorted(sampled),
                         input_jsons=sorted(os.path.basename(x) for x in js),
                         input_provenance=sorted(derived),
                         overlap=sorted(overlap)))
    return rows, unresolved, unparsed


def selftest():
    """P1 and P2, both run every time and both able to fail."""
    ok = True
    rows, _, _ = scan([os.path.join(HERE, "p_compare.py")])
    hit = rows and rows[0]["overlap"]
    say(f"P1 positive (p_compare.py, the known true positive): "
        f"overlap {rows[0]['overlap'] if rows else 'NO ROW'}")
    if not hit:
        say("P1 FIRED: the scanner does not flag the defect that caused it to be written.")
        ok = False

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        # P2: samples image A, loads provenance naming image B. Must NOT be flagged.
        jp = os.path.join(REPL, "metrology", "components-front.json")
        src = ('IMG = "images/airtag/fcc-BCGA2187-internal-photo-6.jpg"\n'
               'FIT = "components-front.json"\n')
        fp = os.path.join(td, "fake_clean.py")
        open(fp, "w").write(src)
        r2, _, _ = scan([fp])
        say(f"P2 negative (samples photo 6, provenance names "
            f"{os.path.basename(jp)} -> oflynn): overlap {r2[0]['overlap']}")
        if r2[0]["overlap"]:
            say("P2 FIRED: the scanner flags a tool that samples a DIFFERENT image "
                "from the one its input came from.")
            ok = False

        # P2b: the same file changed to sample the image its input DID come from
        src2 = ('IMG = "images/airtag/oflynn-backside-fullres.jpeg"\n'
                'FIT = "components-front.json"\n')
        fp2 = os.path.join(td, "fake_circular.py")
        open(fp2, "w").write(src2)
        r3, _, _ = scan([fp2])
        say(f"P2b positive (same file, now sampling the image its input came from): "
            f"overlap {r3[0]['overlap']}")
        if not r3[0]["overlap"]:
            say("P2b FIRED: the scanner misses a deliberately circular tool.")
            ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=HERE)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    say("CONTROLS FIRST")
    good = selftest()
    say("")
    if a.selftest:
        sys.exit(PASS if good else FAIL)
    if not good:
        say("FAIL: the scanner's own controls did not pass. No scan is published.")
        sys.exit(FAIL)

    paths = glob.glob(os.path.join(a.dir, "*.py"))
    rows, unresolved, unparsed = scan(paths)
    flagged = [r for r in rows if r["overlap"]]
    with_prov = [r for r in rows if r["input_provenance"]]

    say(f"scanned {len(rows)} tools in {os.path.relpath(a.dir, REPL)}")
    say(f"P3 coverage: {len(with_prov)}/{len(rows)} tools have a resolvable input "
        f"provenance; {len(unresolved)} references unresolved; {len(unparsed)} files "
        f"unparseable")
    for n, e in unparsed:
        say(f"   UNPARSEABLE {n}: {e}")
    if unresolved:
        say(f"   unresolved: {sorted(set(unresolved))[:8]}"
            f"{' ...' if len(set(unresolved)) > 8 else ''}")
    say("")
    say(f"CANDIDATES -- subject intersects input provenance ({len(flagged)}):")
    for r in flagged:
        say(f"  {r['tool']}")
        say(f"     samples          {r['samples']}")
        say(f"     input provenance {r['input_provenance']}")
        say(f"     OVERLAP          {r['overlap']}")
    say("")
    say("A CANDIDATE IS NOT A VERDICT. An intersection is legitimate when the check is "
        "NAMED for what it tests -- a registration round-trip should sample its own "
        "source. Confirm each by reading the tool.")

    if a.out:
        json.dump(dict(tool="p_provenance.py", dir=os.path.relpath(a.dir, REPL),
                       what_this_is="CANDIDATE FINDER for E07 entry 33, not a verdict",
                       n_tools=len(rows), n_with_provenance=len(with_prov),
                       n_unresolved=len(set(unresolved)),
                       unresolved=sorted(set(unresolved)),
                       unparseable=[n for n, _ in unparsed],
                       candidates=flagged, all_rows=rows),
                  open(a.out, "w"), indent=2)
        say(f"wrote {a.out}")

    if len(with_prov) < 0.15 * max(len(rows), 1):
        say("CANNOT DETERMINE: too few tools have a resolvable input provenance for "
            "this scan to mean anything.")
        sys.exit(CANNOT)
    say("PASS (scan complete; candidates listed, not judged)")
    sys.exit(PASS)


if __name__ == "__main__":
    main()
