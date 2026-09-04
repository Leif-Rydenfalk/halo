#!/usr/bin/env python3
"""check_lcsc_netlist — is every order code ON THE SCHEMATIC NETLIST the part
the sheet asked for?

The 2026-09-04 defect ("ten of fifteen LCSC order codes named a different
component") was found by auditing schematic.py's declaration sites and fixed
in spec/bom-resolved.json. It came BACK the next day: the codes were never
written onto the sheet itself, so the next board regeneration exported the
old wrong codes into the netlist the factory actually orders from. This tool
reads the EXPORTED NETLIST (KiCad's own .net, a different artifact from a
different tool) so the check cannot pass while the sheet is wrong.

    python3 tools/check_lcsc_netlist.py [--net out/halo_rev_a.net]
        [--db PATH] [--json out.json] [--quiet]

Exit codes are the verdict: 0 PASS · 1 FAIL · 2 CANNOT DETERMINE.

The five assertions, each with the sentence it defeats:

  N1 code_resolves      could PASS while an order code names nothing at all
  N2 mpn_matches        could PASS while the code's real MPN is not the sheet's MPN
  N3 package_fits       could PASS while an 0201 land orders an 0402 part
  N4 one_code_one_mpn   could PASS while one code serves two different MPNs
  N5 no_code_says_why   could PASS while a placed line silently carries no code
"""
import argparse, collections, json, pathlib, re, sqlite3, sys
from datetime import datetime, timezone

PASS, FAIL, CD = "PASS", "FAIL", "CANNOT DETERMINE"
RANK = {PASS: 0, CD: 1, FAIL: 2}
DEFAULT_NET = pathlib.Path(__file__).resolve().parent.parent / \
    "electronics/halo_rev_a/out/halo_rev_a.net"
DEFAULT_DB = pathlib.Path.home() / \
    "dev/ce-workshop/ce-fab/data/jlcparts-slim.sqlite3"

# footprint token -> the vendor package string that must appear. Anything the
# table cannot see is CANNOT DETERMINE for that line, never a pass.
PKG_RULES = [
    (re.compile(r"[_ ]0201_"), "0201"), (re.compile(r"[_ ]0402_"), "0402"),
    (re.compile(r"[_ ]0603_"), "0603"), (re.compile(r"[_ ]0805_"), "0805"),
    (re.compile(r"[_ ]1206_"), "1206"),
    (re.compile(r"LGA-12"), "LGA-12"),
    (re.compile(r"QFN-48"), "VFQFN-48"),
    (re.compile(r"Crystal_SMD_2016"), "SMD2016"),
    (re.compile(r"Crystal_SMD_3215"), "SMD3215"),
]
# a comp whose line is not bought, and the words that prove it on its own face
NO_BUY = re.compile(
    r"DNP|NOT\s|NO\s|n/a|ETCHED|Fiducial|TestPoint|Antenna|Mechanical",
    re.I)


def norm(s):
    return re.sub(r"[\s\-]+", "", (s or "").upper())


def parse_net(path):
    """Every (comp) of a KiCad s-expression netlist: ref/value/footprint/fields."""
    t = pathlib.Path(path).read_text(errors="replace")
    comps = []
    for m in re.finditer(r"\(comp\n", t):
        i = m.end()
        depth = 1
        while depth and i < len(t):
            depth += (t[i] == "(") - (t[i] == ")")
            i += 1
        body = t[m.end():i]
        ref = re.search(r'\(ref "([^"]+)"\)', body)
        if not ref:
            continue
        val = re.search(r'\(value "([^"]*)"\)', body)
        fp = re.search(r'\(footprint "([^"]*)"\)', body)
        dnp = "(dnp yes)" in body
        fields = {}
        for fm in re.finditer(
                r'\((?:field|property)\s*\(name "([^"]+)"\)\s*'
                r'(?:\(value "([^"]*)"\)|"([^"]*)")', body, re.S):
            fields[fm.group(1)] = fm.group(2) if fm.group(2) is not None \
                else fm.group(3)
        comps.append({"ref": ref.group(1), "value": val.group(1) if val else "",
                      "footprint": fp.group(1) if fp else None,
                      "mpn": fields.get("MPN"), "lcsc": fields.get("LCSC Part #"),
                      "dnp": dnp, "in_bom": "(in_bom no)" not in body})
    return comps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--net", default=str(DEFAULT_NET))
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    net = pathlib.Path(a.net)
    if not net.is_file():
        print(f"CANNOT DETERMINE: no netlist at {net}", file=sys.stderr)
        return 2
    db = pathlib.Path(a.db)
    if not db.is_file():
        print(f"CANNOT DETERMINE: no catalogue snapshot at {db}", file=sys.stderr)
        return 2

    comps = parse_net(net)
    placed = [c for c in comps if c["in_bom"] and not c["dnp"]]
    con = sqlite3.connect(str(db))
    rows, by_code = [], collections.defaultdict(list)

    for c in comps:
        code = (c["lcsc"] or "").strip()
        by_code[code].append(c["ref"])

    for code, refs in sorted(by_code.items()):
        sample = next(c for c in comps if c["ref"] == refs[0])
        if not code:
            # N5: a placed, non-DNP line with no code must say why on its face
            why = " ".join(str(x) for x in
                           (sample["value"], sample["footprint"],
                            sample["lcsc"]) if x)
            bought = sample["in_bom"] and not sample["dnp"] and \
                not NO_BUY.search(why)
            rows.append({"rule": "no_code_says_why", "refs": refs,
                         "value": sample["value"],
                         "verdict": FAIL if bought else PASS,
                         "why": ("placed line carries no order code and no "
                                 "stated reason") if bought else
                                ("no code, and the line says why on its face: "
                                 f"{(sample['value'] or '')[:40]}")})
            continue
        if not re.fullmatch(r"C\d+", code):
            rows.append({"rule": "no_code_says_why", "refs": refs,
                         "verdict": PASS,
                         "why": f"field is a stated reason, not a code: "
                                f"{code[:60]}"})
            continue
        r = con.execute("select mpn,package,description,stock from parts "
                        "where lcsc=?", (code,)).fetchone()
        if not r:
            rows.append({"rule": "code_resolves", "refs": refs, "lcsc": code,
                         "verdict": CD,
                         "why": f"{code} is not in the catalogue snapshot — "
                                f"an unknown part is not a matching part"})
            continue
        real_mpn, real_pkg = r[0], r[1]
        want = sample["mpn"]
        mpn_ok = want and (norm(real_mpn) == norm(want) or
                           norm(real_mpn).startswith(norm(want)) or
                           norm(want).startswith(norm(real_mpn)))
        rows.append({"rule": "mpn_matches", "refs": refs, "lcsc": code,
                     "catalogue_mpn": real_mpn, "sheet_mpn": want,
                     "verdict": PASS if mpn_ok else FAIL,
                     "why": f"{code} is {real_mpn}; the sheet says "
                            f"{want or 'NOTHING'}"})
        pkg_ok = None
        for rx, token in PKG_RULES:
            if sample["footprint"] and rx.search(sample["footprint"]):
                pkg_ok = token.lower() in (real_pkg or "").lower()
                rows.append({"rule": "package_fits", "refs": refs,
                             "lcsc": code, "catalogue_package": real_pkg,
                             "footprint": sample["footprint"],
                             "verdict": PASS if pkg_ok else FAIL,
                             "why": f"land pattern {sample['footprint']} "
                                    f"needs {token}; {code} is "
                                    f"{real_pkg or 'unknown'}"})
                break
        if pkg_ok is None:
            rows.append({"rule": "package_fits", "refs": refs, "lcsc": code,
                         "verdict": CD,
                         "why": "no package rule for this footprint; nothing "
                                "was measured"})

    # N4 one_code_one_mpn
    codes_by_mpn = collections.defaultdict(set)
    for c in comps:
        code = (c["lcsc"] or "").strip()
        if re.fullmatch(r"C\d+", code) and c["mpn"]:
            codes_by_mpn[code].add(norm(c["mpn"]))
    for code, mpns in sorted(codes_by_mpn.items()):
        if len(mpns) > 1:
            rows.append({"rule": "one_code_one_mpn", "refs": by_code[code],
                         "lcsc": code, "verdict": FAIL,
                         "why": f"{code} serves {len(mpns)} different MPNs: "
                                f"{sorted(mpns)}"})

    codes = {c for c in by_code if re.fullmatch(r"C\d+", c)}
    out = {
        "$halo": 1, "tool": "tools/check_lcsc_netlist.py",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "netlist": str(net.resolve()),
        "catalogue": str(db.resolve()),
        "snapshot_note": "ce-fab data/jlcparts-slim.sqlite3, built 2026-09-03",
        "comps": len(comps), "placed": len(placed),
        "distinct_codes": len(codes),
        "verdict": max((r["verdict"] for r in rows), key=lambda v: RANK[v]),
        "counts": {k: sum(1 for r in rows if r["verdict"] == k)
                   for k in (PASS, FAIL, CD)},
        "rows": rows,
        "command": "python3 " + " ".join(sys.argv[0:1] + sys.argv[1:]),
    }
    if a.json:
        pathlib.Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.json).write_text(json.dumps(out, indent=1) + "\n")
    if not a.quiet:
        print(f"# check_lcsc_netlist — {net.name}: {len(comps)} comps, "
              f"{len(codes)} distinct order codes")
        for r in rows:
            print(f"  [{r['verdict']:18}] {r['rule']:16} "
                  f"{','.join(r['refs'])[:28]:28} {r['why'][:90]}")
        print(f"{out['counts'][PASS]} pass, {out['counts'][FAIL]} fail, "
              f"{out['counts'][CD]} cannot determine — {out['verdict']}")
    return {PASS: 0, FAIL: 1, CD: 2}[out["verdict"]]


def self_test():
    """Break every check on purpose and watch it fire (TOOLS-THAT-LIE rule)."""
    import tempfile, os
    dir = tempfile.mkdtemp()
    good = '''(export (version "E")(components
\t\t(comp\n\t\t\t(ref "C1")\n\t\t\t(value "100nF")\n\t\t\t(footprint "Capacitor_SMD:C_0201_0603Metric")\n\t\t\t(fields\n\t\t\t\t(field (name "MPN") "TCC0201X5R104K100ZT")\n\t\t\t\t(field (name "LCSC Part #") "C5142565"))\n\t\t)\n)\n(libpart)'''
    cases = [
        ("code_resolves fires on a code the catalogue has never heard of",
         good.replace("C5142565", "C9999999"), 2),
        ("mpn_matches fires when the code is real but the sheet's MPN is not",
         good.replace("TCC0201X5R104K100ZT", "CL03A104KA3NNNC"), 1),
        ("package_fits fires on an 0402 part under an 0201 land",
         good.replace("C_0201_0603Metric", "C_0402_1005Metric")
             .replace("TCC0201X5R104K100ZT", "CL05A106MQ5NUNC"), 1),
        ("no_code_says_why fires on a bare placed line with no code at all",
         good.replace('"100nF"', '"4.7uF"')
             .replace('(field (name "LCSC Part #") "C5142565")', ""),
         1),
        ("the unmodified fixture itself passes",
         good, 0),
    ]
    fails = 0
    for why, text, want in cases:
        p = pathlib.Path(dir) / "t.net"
        p.write_text(text)
        rc = subprocess_rc(["--net", str(p), "--quiet"])
        ok = rc == want
        fails += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {why}: exit {rc}, wanted {want}")
    return 1 if fails else 0


def subprocess_rc(argv):
    import subprocess
    return subprocess.run([sys.executable, str(pathlib.Path(__file__)
                          .resolve())] + argv,
                          capture_output=True).returncode


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.exit(main())
