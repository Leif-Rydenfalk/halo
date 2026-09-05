#!/usr/bin/env python3
"""x_lcsc_resolve — fill the fab BOM's order codes FROM WHAT IS ALREADY ON DISK.

    tools/x_lcsc_resolve.py                 report: what resolves, what does not
    tools/x_lcsc_resolve.py --self-test     the refusals, broken on purpose

Exit 0 when every line resolved, 1 when any did not (which is the normal
answer and not a failure), 2 when the inputs are missing.

---------------------------------------------------------------------------
THE PROBLEM THIS SOLVES, AND THE ONE IT REFUSES TO
---------------------------------------------------------------------------
`schematic_fab.py` puts a real MPN on every line and NO LCSC order code,
because this lane did not pull a price ladder and a code with no pull date is
a rumour. That is honest and it is also useless to JLCPCB, whose assembly
service matches on LCSC codes.

**This tool does not fetch anything.** It never touches the network, and the
rules say so. What it does is read the price pulls THIS PROJECT ALREADY MADE
AND COMMITTED — `research/fetched/E-lcsc-price-pull-2026-09-03.md` and its
siblings — and resolve a code only where one of those files NAMES THE PART
NUMBER ON THE SAME LINE AS THE CODE.

So the output is a mixture, and the mixture is the point: some lines get a
code with a file, a line number and the pull date attached, and the rest get
CANNOT DETERMINE with the exact MPN a human has to look up. That turns "no
codes anywhere" into a short list of specific lookups.

---------------------------------------------------------------------------
WHY THE MATCH IS DELIBERATELY NARROW
---------------------------------------------------------------------------
The tempting implementation is fuzzy: search for "MAX98357" and take the
nearest `C\\d+`. That is how a BOM acquires a code for the WRONG PART, and a
wrong code is worse than no code — an empty cell stops the order, a wrong one
ships a board full of something else. So:

* the MPN must appear **on the same line** as the code, not in the same file;
* the match is on the MPN as written on the schematic, case-insensitively,
  and on nothing else — not the value, not the description, not the package;
* a line yielding **more than one distinct code is CANNOT DETERMINE**, not a
  choice. Ambiguity is not resolved by taking the first one.

`--self-test` breaks each of those on purpose and requires the refusal.
"""
import csv
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
HALO = os.path.dirname(os.path.dirname(REPLICA))
WORKSHOP = "/Users/leifrydenfalk/dev/ce-workshop"
if os.path.join(WORKSHOP, "ce-pcb") not in sys.path:
    sys.path.insert(0, os.path.join(WORKSHOP, "ce-pcb"))

SCH = os.path.join(REPLICA, "out", "schematic-fab",
                   "halo_replica_fab.kicad_sch")
OUT = os.path.join(REPLICA, "out", "schematic-fab",
                   "halo_replica_fab-bom-resolved.csv")

#: The pulls this project actually made and committed, newest intent first.
#: A file not in this list is not consulted — an allow-list, because "search
#: the repo for a C-number" would find order codes in prose, in other
#: designs' BOMs and in quoted forum posts.
PULLS = [
    "research/fetched/E-lcsc-price-pull-2026-09-03.md",
    "research/fetched/E-jlcpcb-search-2026-09-03.md",
    "research/fetched/H-lcsc-jlcpcb-prices.md",
    "research/fetched/D-05-volume-pricing.md",
]

CODE = re.compile(r"\bC\d{4,8}\b")

#: A row of the JLCPCB parts-library search dump:
#:   C60490   RC0402FR-0710KL   YAGEO   0402   expand  stk=9600477{...}
#: THE MANUFACTURER COLUMN IS TRUNCATED TO ITS WIDTH, so when the name fills
#: it there is only ONE space before the package — "Johanson Dielectr 1206".
#: A first version demanded two spaces there and silently parsed ZERO rows
#: for such parts, which then read as "searched and returned nothing". A
#: parser that fails to match does not look like a parser that failed: it
#: looks like an empty result, and here that is a MEASURED ABSENCE, which is
#: a claim. So the package is taken as the LAST token before base/expand
#: rather than by counting spaces.
_JLC_ROW = re.compile(
    r"^(C\d{4,8})\s+(\S.*?)\s{2,}(.*?)\s+(base|expand)\s+stk=(\d+)")


def _parse_row(line, rel, i):
    """One catalogue row, or None. Two shapes, both from committed pulls."""
    m = _JLC_ROW.match(line)
    if m:
        code, mpn, midway, lib, stock = m.groups()
        bits = midway.rsplit(None, 1)
        mfr, package = (bits[0], bits[1]) if len(bits) == 2 else ("", midway)
        return {"code": code, "mpn": mpn.strip(), "mfr": mfr.strip(),
                "package": package.strip(), "lib": lib, "stock": stock,
                "where": "%s:%d" % (rel, i)}
    if line.lstrip().startswith("|"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5:
            cm = re.search(r"C\d{4,8}", cells[0])
            if cm and not cells[0].lower().startswith("lcsc"):
                return {"code": cm.group(0), "mpn": cells[1],
                        "mfr": cells[2], "package": cells[3],
                        "lib": "", "stock": cells[4],
                        "where": "%s:%d" % (rel, i)}
    return None


def catalogue(root=None, names=None):
    """Structured rows from the committed pulls, plus the keywords SEARCHED.

    Line-scanning was enough to find a code; it is not enough to CHECK one.
    A resolution has to carry the package the catalogue lists, so it can be
    compared with the footprint on the sheet — the near-miss that shipped a
    wrong code here differed in its MPN, but the next one may differ only in
    its package, and a 1206 antenna under an 0402 land is the same class of
    defect arriving by a different door.

    `searched` is the set of `### <keyword>` headings in the JLCPCB dump.
    A keyword that was searched and returned NOTHING is a MEASURED ABSENCE
    and a completely different answer from one nobody ever looked up.
    """
    root = root or HALO
    rows, missing, searched, empty = [], [], set(), set()
    for rel in (names or PULLS):
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            missing.append(rel)
            continue
        heading, got = None, 0
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh, 1):
                if line.startswith("### "):
                    if heading is not None and got == 0:
                        empty.add(heading.lower())
                    heading = line[4:].strip()
                    searched.add(heading.lower())
                    got = 0
                    continue
                row = _parse_row(line, rel, i)
                if row is None:
                    continue
                got += 1
                rows.append(row)
        if heading is not None and got == 0:
            empty.add(heading.lower())
    return {"rows": rows, "missing": missing, "searched": searched,
            "empty": empty}
PASS, FAIL, CANNOT = "PASS", "FAIL", "CANNOT DETERMINE"


def load_pulls(root=None, names=None):
    """[(path, lineno, text)] for every line of every pull that is present.

    A pull named here and missing from disk is REPORTED, not skipped: the
    difference between "we looked and it was not there" and "we did not look"
    is the whole value of the answer.
    """
    root = root or HALO
    rows, missing = [], []
    for rel in (names or PULLS):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            missing.append(rel)
            continue
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh, 1):
                rows.append((rel, i, line))
    return rows, missing


def _names(line, mpn):
    """Does this line name EXACTLY this part number?

    SUBSTRING CONTAINMENT IS NOT ENOUGH AND THIS TOOL SHIPPED WRONG BECAUSE OF
    IT. Its first real run resolved the chip antenna to C89334, whose
    catalogue part number is `2450AT18A100E` while the schematic says
    `2450AT18A100` — a different part number, matched because the shorter is
    a substring of the longer. That is the "a wrong code is worse than no
    code" failure the module docstring warns about, produced by the tool that
    warns about it, and it was caught by reading the five source lines rather
    than by any check.

    The self-test had a case for the OTHER direction — a long schematic MPN
    against a short catalogue one — and passed, which is exactly how a
    one-directional test flatters. Both directions are covered now.

    So the match must be token-exact: the characters either side of it must
    not be alphanumeric. `\b` cannot do this because real part numbers
    contain `+`, `.` and `/` (MAX98357AETE+T, ABS07-32.768KHZ-T).
    """
    hay, needle = line.lower(), mpn.lower()
    start = 0
    while True:
        i = hay.find(needle, start)
        if i < 0:
            return False
        before = hay[i - 1] if i else " "
        after = hay[i + len(needle)] if i + len(needle) < len(hay) else " "
        if not before.isalnum() and not after.isalnum():
            return True
        start = i + 1


#: `\b` does NOT match between "_" and a digit, because "_" is a word
#: character — so "C_0402_1005Metric" never matched and every imperial
#: comparison silently returned CANNOT DETERMINE, including the one that
#: should have said 0402-against-0603 is WRONG. A check that answers "I
#: cannot tell" to everything looks exactly like a cautious check.
_IMPERIAL = re.compile(r"(?<!\d)(0201|0402|0603|0805|1206|1210)(?!\d)")
_PINPKG = re.compile(r"\b([A-Z]{2,5})-?(\d{1,3})[-_]?.*?(\d(?:\.\d+)?)\s*x\s*"
                     r"(\d(?:\.\d+)?)", re.I)


def package_agrees(cat_pkg, footprint):
    """Does the catalogue's package contradict the land pattern on the sheet?

    Returns (verdict, why): PASS, FAIL, or CANNOT DETERMINE.

    NOT a similarity score. It answers only "do these two CONTRADICT", because
    that is the question with a right answer: `0402` against a footprint whose
    name says 0603 is wrong and can be said so; `1206` against
    `RF_Antenna:Johanson_2450AT18x100` is unknown, because that land pattern's
    name carries no size at all. A checker that guessed the second would
    either invent agreement or invent an alarm, and both are worse than
    saying which of the two cases you are in.
    """
    cat_pkg, footprint = (cat_pkg or "").strip(), (footprint or "").strip()
    if not cat_pkg or not footprint:
        return CANNOT, "one side names no package"
    a, b = _IMPERIAL.search(cat_pkg), _IMPERIAL.search(footprint)
    if a and b:
        if a.group(1) == b.group(1):
            return PASS, "both say %s" % a.group(1)
        return FAIL, ("catalogue says %s and the sheet's land pattern says %s"
                      % (a.group(1), b.group(1)))
    ca, cb = _PINPKG.search(cat_pkg), _PINPKG.search(footprint)
    if ca and cb:
        if (ca.group(2), ca.group(3), ca.group(4)) == \
                (cb.group(2), cb.group(3), cb.group(4)):
            return PASS, ("both say %s pins, %sx%s mm"
                          % (ca.group(2), ca.group(3), ca.group(4)))
        return FAIL, ("catalogue %s-%s %sx%s vs land pattern %s-%s %sx%s"
                      % (ca.group(1), ca.group(2), ca.group(3), ca.group(4),
                         cb.group(1), cb.group(2), cb.group(3), cb.group(4)))
    return CANNOT, ("no comparable size in catalogue %r and land pattern %r"
                    % (cat_pkg[:22], footprint.split(":")[-1][:34]))


def resolve(mpn, rows, cat=None):
    """(code, why) for one MPN, or (None, why-not).

    The MPN must be on the SAME LINE as the code. See the module docstring
    for why this is not fuzzy.
    """
    mpn = (mpn or "").strip()
    if not mpn or mpn == "-":
        return None, "the schematic gives no MPN for this line"
    hits = {}
    for rel, i, line in rows:
        if not _names(line, mpn):
            continue
        for c in CODE.findall(line):
            hits.setdefault(c, []).append("%s:%d" % (rel, i))
    if not hits:
        if cat and mpn.lower() in cat["empty"]:
            return None, ("SEARCHED AND ABSENT: the catalogue was queried for "
                          "'%s' on 2026-09-03 and returned NO parts. This is "
                          "a measured absence, not an unchecked line - a "
                          "different part number is needed, not a lookup."
                          % mpn)
        if cat and mpn.lower() in cat["searched"]:
            return None, ("searched for '%s' and the results carry no order "
                          "code on the naming line" % mpn)
        return None, ("NOT SEARCHED: no committed pull queried '%s'. This is "
                      "the cheap kind of unknown - one catalogue lookup "
                      "closes it." % mpn)
    if len(hits) > 1:
        return None, ("AMBIGUOUS - %d different codes appear on lines naming "
                      "%s (%s). Ambiguity is not resolved by taking the "
                      "first." % (len(hits), mpn, ", ".join(sorted(hits))))
    code = next(iter(hits))
    extra = ""
    if cat:
        for r in cat["rows"]:
            if r["code"] == code and r["mpn"].lower() == mpn.lower():
                extra = " [%s%s, stock %s]" % (
                    r["package"], ", JLCPCB BASIC" if r["lib"] == "base"
                    else (", extended" if r["lib"] == "expand" else ""),
                    r["stock"])
                break
    return code, "%s names %s beside %s%s" % (hits[code][0], mpn, code, extra)


def run(sch=None, root=None, names=None, out=None, verbose=True):
    from cepcb.fab import bom_from_sch
    sch = sch or SCH
    if not os.path.exists(sch):
        return {"verdict": CANNOT, "why": "no fab schematic at %s" % sch}
    # The intermediate BOM goes to a TEMP DIRECTORY, not beside the real
    # output. Writing it next to the deliverable put `_bom-tmp.csv` into the
    # repository, where the next reader has to work out whether a file named
    # "tmp" is one of the files they are meant to send to a fab.
    tmpdir = tempfile.mkdtemp(prefix="lcsc-bom-")
    try:
        bom = bom_from_sch(sch, out=os.path.join(tmpdir, "bom.csv"),
                           verbose=False)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    rows, missing = load_pulls(root, names)
    cat = catalogue(root, names)

    resolved, unresolved, conflicts = [], [], []
    for line in bom["lines"]:
        if line["LCSC Part #"]:
            resolved.append((line, line["LCSC Part #"],
                             "already on the schematic"))
            continue
        code, why = resolve(line["MPN"], rows, cat)
        if not code:
            unresolved.append((line, None, why))
            continue
        # A CODE IS NOT ACCEPTED UNTIL ITS PACKAGE IS CHECKED AGAINST THE LAND
        # PATTERN ON THE SHEET. Matching a part number is one claim; that the
        # thing arrives in the shape the board expects is another, and a 1206
        # part under an 0402 land is the same class of defect as a wrong code
        # arriving by a different door.
        pkg = next((r["package"] for r in cat["rows"]
                    if r["code"] == code
                    and r["mpn"].lower() == line["MPN"].strip().lower()), "")
        v, pwhy = package_agrees(pkg, line["Footprint"])
        if v == FAIL:
            conflicts.append((line, code, pwhy))
            unresolved.append((line, None,
                               "REFUSED - package conflict: " + pwhy))
            continue
        resolved.append((line, code, why + " | package " + v + ": " + pwhy))

    out = out or OUT
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #",
                    "MPN", "Quantity", "Order code source"])
        for line, code, why in resolved + unresolved:
            w.writerow([line["Comment"], line["Designator"],
                        line["Footprint"], code or "", line["MPN"],
                        line["Quantity"], why])

    verdict = FAIL if conflicts else (PASS if not unresolved else CANNOT)
    if verbose:
        print("pulls consulted: %d line(s) across %d file(s)%s"
              % (len(rows), len(names or PULLS) - len(missing),
                 "" if not missing else
                 "; MISSING FROM DISK: " + ", ".join(missing)))
        print("resolved   %d of %d BOM lines" % (len(resolved),
                                                 len(bom["lines"])))
        for line, code, why in resolved:
            print("   %-9s %-26s %s" % (code or "-", line["Comment"][:26],
                                        line["Designator"][:26]))
            print("             %s" % why)
        print("\nCANNOT DETERMINE, and each names the exact lookup a human "
              "must do:")
        for line, _c, why in unresolved:
            print("   %-26s %-16s MPN %s"
                  % (line["Comment"][:26], line["Designator"][:16],
                     line["MPN"] or "(none on the sheet)"))
            print("             %s" % why)
        if conflicts:
            print("\nPACKAGE CONFLICTS - a matched code whose package the "
                  "board cannot accept:")
            for line, code, why in conflicts:
                print("   %-10s %-22s %s" % (code, line["Designator"][:22],
                                             why))
        print("\n%s  %s" % (verdict, out))
    return {"verdict": verdict, "path": out, "resolved": resolved,
            "unresolved": unresolved, "missing_pulls": missing,
            "conflicts": conflicts, "catalogue": cat,
            "n": {"lines": len(bom["lines"]), "resolved": len(resolved),
                  "unresolved": len(unresolved),
                  "conflicts": len(conflicts)}}


# ==========================================================================
# the self-test — each break asserts ITS OWN refusal
# ==========================================================================

def self_test():
    ok = True

    def case(name, mpn, lines, want_code, want_in_why):
        nonlocal ok
        rows = [("fake.md", i + 1, t) for i, t in enumerate(lines)]
        code, why = resolve(mpn, rows)
        good = (code == want_code) and (want_in_why.lower() in why.lower())
        print("  %s %-46s -> %s" % ("PASS " if good else "FAIL ", name,
                                    (code or why)[:70]))
        if not good:
            ok = False
            print("         wanted code=%r and %r in the reason"
                  % (want_code, want_in_why))

    print("--- SELF-TEST: the refusals this tool must make ---\n")
    case("a code on the same line as the MPN resolves",
         "MAX98357AETE+T",
         ["| C123456 | MAX98357AETE+T | Analog Devices | $1.20 |"],
         "C123456", "names")
    case("A CODE IN THE SAME FILE BUT NOT THE SAME LINE IS REFUSED",
         "MAX98357AETE+T",
         ["| C123456 | SOME OTHER PART |", "MAX98357AETE+T is mentioned here"],
         None, "no committed pull queried")
    case("TWO DIFFERENT CODES ON MATCHING LINES IS AMBIGUOUS",
         "MAX98357AETE+T",
         ["| C111111 | MAX98357AETE+T |", "| C222222 | MAX98357AETE+T |"],
         None, "ambiguous")
    case("the same code twice is NOT ambiguous",
         "MAX98357AETE+T",
         ["| C111111 | MAX98357AETE+T |", "| C111111 | MAX98357AETE+T | dup"],
         "C111111", "names")
    case("an empty MPN resolves to nothing, not to the first code seen",
         "", ["| C123456 | anything at all |"],
         None, "no MPN")
    case("a dash MPN is treated as no MPN",
         "-", ["| C123456 | anything at all |"],
         None, "no MPN")
    case("a longer schematic MPN does not match a shorter catalogue one",
         "MX25R3235FM1IL0",
         ["| C123456 | MX25R3235F | a different suffix |"],
         None, "no committed pull queried")
    case("A SHORTER SCHEMATIC MPN DOES NOT MATCH A LONGER CATALOGUE ONE",
         # The real defect: the schematic said 2450AT18A100 and the pull says
         # 2450AT18A100E, and substring containment called that a match.
         "2450AT18A100",
         ["| C89334 | 2450AT18A100E | Johanson Dielectrics | 1206 |"],
         None, "no committed pull queried")
    case("an exact MPN still matches when punctuation surrounds it",
         "MAX98357AETE+T",
         ["| C910544 | MAX98357AETE+T | MAXIM | TQFN-16-EP(3x3) |"],
         "C910544", "names")
    case("a code is not taken from a line naming a SUFFIXED variant",
         "RC0402FR-0710KL",
         ["| C1 | RC0402FR-0710KLX | not the same part |"],
         None, "no committed pull queried")

    print("\n--- and the missing-pull report, which must not be silent ---")
    tmp = tempfile.mkdtemp(prefix="lcsc-selftest-")
    rows, missing = load_pulls(root=tmp, names=["nope/does-not-exist.md"])
    good = (rows == [] and missing == ["nope/does-not-exist.md"])
    print("  %s a pull named and absent is REPORTED, not skipped -> %r"
          % ("PASS " if good else "FAIL ", missing))
    if not good:
        ok = False

    print("\n%s" % ("PASS: the refusals hold."
                    if ok else "FAIL: a refusal this tool depends on DID NOT "
                               "HOLD. Read the FAIL lines above - the tool is "
                               "free to emit a wrong order code until they "
                               "are green."))
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    try:
        from cepcb.fab import bom_from_sch                    # noqa: F401
    except Exception as e:                                    # noqa: BLE001
        print("CANNOT DETERMINE: ce-pcb did not import (%s)." % e)
        return 2
    r = run()
    return 0 if r["verdict"] == PASS else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
