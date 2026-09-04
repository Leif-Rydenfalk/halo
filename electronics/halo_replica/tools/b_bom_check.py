#!/usr/bin/env python3
"""b_bom_check.py — the teeth on bom/bom.json.

Exit code IS the verdict: 0 PASS, 1 FAIL, 2 CANNOT DETERMINE (nothing to check).

Six rules, each of which CAN fail and each of which is watched failing by
`--self-test`. An assertion never seen to go red is not known to work.

  R1 every line carries every required field
  R2 a line that says CANNOT DETERMINE must name what would settle it
  R3 SILICON CITED without SILICON SEEN may not be HIGH confidence
  R4 a marking that was READ must name the photograph it was read off
  R5 every source key a line cites must exist in the sources block
  R6 every image named in the sources block must exist on disk

Usage:  b_bom_check.py [bom.json]        # check the real file
        b_bom_check.py --self-test       # break each rule on purpose
"""
import json, os, re, sys

REQUIRED = ["ref", "function", "part", "package", "size_mm", "marking", "locatable",
            "evidence_class", "confidence", "marking_establishes",
            "marking_does_not_establish", "would_settle_it", "rejected", "replica_verdict"]
NO_MARK = {"n/a", "none visible", "cannot determine",
           "none - chip passives of this size carry no marking",
           "no package marking was read."}
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(HERE))


def check(doc, images_must_exist=True):
    """Return a list of (rule, ref, message). Empty list means PASS."""
    bad = []
    sources = doc.get("sources", {})
    for ln in doc.get("lines", []):
        ref = ln.get("ref", "<no ref>")
        for f in REQUIRED:                                                  # R1
            if f not in ln:
                bad.append(("R1", ref, f"missing required field '{f}'"))
        blob = json.dumps(ln).upper()
        if "CANNOT DETERMINE" in blob:                                      # R2
            w = str(ln.get("would_settle_it", "")).strip().lower()
            if not w or w == "n/a":
                bad.append(("R2", ref, "says CANNOT DETERMINE but names nothing "
                                       "that would settle it"))
        ec = str(ln.get("evidence_class", "")).upper()                      # R3
        if "CITED" in ec and "SEEN" not in ec:
            if str(ln.get("confidence", "")).strip().upper().startswith("HIGH"):
                bad.append(("R3", ref, "SILICON CITED but claims HIGH confidence"))
        mk = ln.get("marking", {})                                          # R4
        txt = str(mk.get("text", "")).strip().lower()
        if txt and txt not in NO_MARK:
            rb = str(mk.get("read_by") or "")
            if not re.search(r"(IMG-[A-Z0-9]+|FCC-\d)", rb):
                bad.append(("R4", ref, f"marking {mk.get('text')!r} was read but "
                                       "read_by names no source photograph"))
        for key in set(re.findall(r"\b(IMG-[A-Z0-9]+|FCC-\d)\b", blob)):    # R5
            if key not in sources:
                bad.append(("R5", ref, f"cites source key {key} which the "
                                       "sources block does not define"))
    if images_must_exist:                                                   # R6
        for key, desc in sources.items():
            m = re.match(r"\s*(\S+\.(?:jpe?g|png|md|json))", desc)
            if m and not os.path.exists(os.path.join(REPO, m.group(1))):
                bad.append(("R6", key, f"source names {m.group(1)}, not on disk"))
    return bad


def self_test():
    """Break every rule on purpose and require each one to fire."""
    ok = lambda: {"ref": "T", "function": "f", "part": "p", "package": "pk",
                  "size_mm": {}, "marking": {"text": "n/a", "read_by": None},
                  "locatable": "yes", "evidence_class": "SILICON SEEN",
                  "confidence": "HIGH", "marking_establishes": "x",
                  "marking_does_not_establish": "y", "would_settle_it": "z",
                  "rejected": [], "replica_verdict": "1:1"}
    src = {"IMG-BACK": "images/airtag/oflynn-backside-fullres.jpeg — real"}
    cases = []
    l = ok(); del l["package"];                    cases.append(("R1", l))
    l = ok(); l["part"] = "CANNOT DETERMINE"; l["would_settle_it"] = "n/a"
    cases.append(("R2", l))
    l = ok(); l["evidence_class"] = "SILICON CITED"; cases.append(("R3", l))
    l = ok(); l["marking"] = {"text": "N52832", "read_by": "I saw it somewhere"}
    cases.append(("R4", l))
    l = ok(); l["locatable"] = "see FCC-9";        cases.append(("R5", l))

    fails, passes = 0, 0
    for rule, line in cases:
        got = {r for r, _, _ in check({"sources": src, "lines": [line]}, False)}
        if rule in got:
            print(f"  PASS  {rule} FIRES on a line built to break it")
            passes += 1
        else:
            print(f"  FAIL  {rule} stayed quiet on a line built to break it: {got}")
            fails += 1
    # R6 on purpose
    got = {r for r, _, _ in check({"sources": {"IMG-X": "images/airtag/nope.jpg — x"},
                                   "lines": []}, True)}
    if "R6" in got:
        print("  PASS  R6 FIRES on a source naming a file that is not on disk")
        passes += 1
    else:
        print("  FAIL  R6 stayed quiet on a missing file")
        fails += 1
    # and the negative control: a clean line must produce NOTHING
    got = check({"sources": src, "lines": [ok()]}, False)
    if got:
        print(f"  FAIL  negative control: a clean line produced findings {got}")
        fails += 1
    else:
        print("  PASS  negative control: a clean line produces no findings")
        passes += 1
    print(f"\n{passes}/{passes+fails} passed, {fails} failed")
    return 1 if fails else 0


def main():
    if "--self-test" in sys.argv:
        print("b_bom_check self-test — every rule broken on purpose\n")
        sys.exit(self_test())
    path = next((a for a in sys.argv[1:] if not a.startswith("-")),
                os.path.join(HERE, "bom", "bom.json"))
    if not os.path.exists(path):
        print(f"CANNOT DETERMINE — {path} does not exist")
        sys.exit(2)
    doc = json.load(open(path))
    lines = doc.get("lines", [])
    if not lines:
        print(f"CANNOT DETERMINE — {path} has no lines to check")
        sys.exit(2)
    print(f"b_bom_check  input: {path}  ({len(lines)} lines)")
    bad = check(doc)
    for rule, ref, msg in bad:
        print(f"  FAIL  [{rule}] {ref}: {msg}")
    if bad:
        print(f"\nFAIL — {len(bad)} finding(s)")
        sys.exit(1)
    # report the shape of the honesty, since that is the point of the document
    cd = sum(1 for l in lines if "CANNOT DETERMINE" in json.dumps(l).upper())
    seen = sum(1 for l in lines if "SEEN" in str(l.get("evidence_class", "")).upper())
    print(f"\nPASS — {len(lines)} lines, {seen} SILICON SEEN, "
          f"{len(lines)-seen} not, {cd} carrying at least one CANNOT DETERMINE")
    sys.exit(0)


if __name__ == "__main__":
    main()
