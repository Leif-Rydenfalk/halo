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
import sys

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


def resolve(mpn, rows):
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
        return None, ("no committed price pull names %s on a line with an "
                      "order code" % mpn)
    if len(hits) > 1:
        return None, ("AMBIGUOUS - %d different codes appear on lines naming "
                      "%s (%s). Ambiguity is not resolved by taking the "
                      "first." % (len(hits), mpn, ", ".join(sorted(hits))))
    code = next(iter(hits))
    return code, "%s names %s beside %s" % (hits[code][0], mpn, code)


def run(sch=None, root=None, names=None, out=None, verbose=True):
    from cepcb.fab import bom_from_sch
    sch = sch or SCH
    if not os.path.exists(sch):
        return {"verdict": CANNOT, "why": "no fab schematic at %s" % sch}
    bom = bom_from_sch(sch, out=os.path.join(
        os.path.dirname(out or OUT), "_bom-tmp.csv"), verbose=False)
    rows, missing = load_pulls(root, names)

    resolved, unresolved = [], []
    for line in bom["lines"]:
        if line["LCSC Part #"]:
            resolved.append((line, line["LCSC Part #"],
                             "already on the schematic"))
            continue
        code, why = resolve(line["MPN"], rows)
        (resolved if code else unresolved).append((line, code, why))

    out = out or OUT
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #",
                    "MPN", "Quantity", "Order code source"])
        for line, code, why in resolved + unresolved:
            w.writerow([line["Comment"], line["Designator"],
                        line["Footprint"], code or "", line["MPN"],
                        line["Quantity"], why])

    verdict = PASS if not unresolved else CANNOT
    if verbose:
        print("pulls consulted: %d line(s) across %d file(s)%s"
              % (len(rows), len(names or PULLS) - len(missing),
                 "" if not missing else
                 "; MISSING FROM DISK: " + ", ".join(missing)))
        print("resolved   %d of %d BOM lines" % (len(resolved),
                                                 len(bom["lines"])))
        for line, code, why in resolved:
            print("   %-10s %-26s %s   [%s]"
                  % (code or "-", line["Comment"][:26], line["Designator"][:22],
                     why[:64]))
        print("\nCANNOT DETERMINE, and each names the exact lookup a human "
              "must do:")
        for line, _c, why in unresolved:
            print("   %-26s %-20s MPN %-22s %s"
                  % (line["Comment"][:26], line["Designator"][:20],
                     line["MPN"][:22] or "(none)", why[:70]))
        print("\n%s  %s" % (verdict, out))
    return {"verdict": verdict, "path": out, "resolved": resolved,
            "unresolved": unresolved, "missing_pulls": missing,
            "n": {"lines": len(bom["lines"]), "resolved": len(resolved),
                  "unresolved": len(unresolved)}}


# ==========================================================================
# the self-test — each break asserts ITS OWN refusal
# ==========================================================================

def self_test():
    import tempfile
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
         None, "no committed price pull")
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
         None, "no committed price pull")
    case("A SHORTER SCHEMATIC MPN DOES NOT MATCH A LONGER CATALOGUE ONE",
         # The real defect: the schematic said 2450AT18A100 and the pull says
         # 2450AT18A100E, and substring containment called that a match.
         "2450AT18A100",
         ["| C89334 | 2450AT18A100E | Johanson Dielectrics | 1206 |"],
         None, "no committed price pull")
    case("an exact MPN still matches when punctuation surrounds it",
         "MAX98357AETE+T",
         ["| C910544 | MAX98357AETE+T | MAXIM | TQFN-16-EP(3x3) |"],
         "C910544", "names")
    case("a code is not taken from a line naming a SUFFIXED variant",
         "RC0402FR-0710KL",
         ["| C1 | RC0402FR-0710KLX | not the same part |"],
         None, "no committed price pull")

    print("\n--- and the missing-pull report, which must not be silent ---")
    tmp = tempfile.mkdtemp(prefix="lcsc-selftest-")
    rows, missing = load_pulls(root=tmp, names=["nope/does-not-exist.md"])
    good = (rows == [] and missing == ["nope/does-not-exist.md"])
    print("  %s a pull named and absent is REPORTED, not skipped -> %r"
          % ("PASS " if good else "FAIL ", missing))
    if not good:
        ok = False

    print("\n%s: the refusals hold." % ("PASS" if ok else "FAIL"))
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
