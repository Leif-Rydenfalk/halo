#!/usr/bin/env python3
"""check_bom_identity — is the part we ordered the part the schematic asked for?

Lane V1, 2026-09-04. `fab bom cost` answers "is it in stock and what does it
cost". Nothing anywhere answered "is C1546 actually a 100 nF capacitor". It is
not: it is a **100 pF** capacitor, and it is on four decoupling lines and two
1.1 nF lines of the halo BOM at once.

Measured on out/release/board/halo_rev_a-BOM.csv, 2026-09-04:

    C2827888  ordered as 2.2 uF / 10 nF / 2.2 nF   is a 3.5 mm SCREW TERMINAL BLOCK
    C1046539  ordered as 2.7 nH / 3.5 nH inductors is a 33 MHz MEMS OSCILLATOR, $14.73
    C1546     ordered as 100 nF and as 1.1 nF      is 100 pF
    C1568     ordered as 2.0/0.3/3.9/0.5/1.5 pF    is 4.0 pF
    C25765    ordered as 4.7 M                     is 20 k
    C1523     ordered as 100 pF                    is 1 nF
    C25076    ordered as 100 R and as 0 R          is 100 R

Every one of those lines was graded PASS by the cost tool, because the cost
tool asks about stock and price and never about identity. That is the failure
docs/TOOLS-THAT-LIE.md names: the report describes what the tool chose to
measure, not what a reader infers from a pass.

    python3 tools/check_bom_identity.py <BOM.csv> [--json out.json] [--db PATH]

Exit 0 PASS · 1 FAIL · 2 CANNOT DETERMINE. A line whose part is not in the
catalogue is CANNOT DETERMINE, never a pass — an unknown part is not a
matching part.

The six assertions, each with the sentence it defeats:

  I1 part_resolves        could PASS while the LCSC code names nothing at all
  I2 class_matches        could PASS while a capacitor line orders a terminal block
  I3 value_matches        could PASS while a 100 nF line orders 100 pF
  I4 package_matches      could PASS while an 0201 footprint orders an 0402 part
  I5 one_code_one_value   could PASS while one LCSC code serves six different values
  I6 line_has_a_part      could PASS while a populated line names no part at all
"""
import argparse
import csv
import json
import pathlib
import re
import sqlite3
import sys
from datetime import datetime, timezone

PASS, FAIL, CD = "PASS", "FAIL", "CANNOT DETERMINE"
RANK = {PASS: 0, CD: 1, FAIL: 2}

DEFAULT_DB = pathlib.Path.home() / "dev/ce-workshop/ce-fab/data/jlcparts-slim.sqlite3"

# designator prefix -> (what it is, the SI unit its value must carry)
CLASS = {
    "C": ("capacitor", "F"), "R": ("resistor", "Ω"), "L": ("inductor", "H"),
    "X": ("crystal or oscillator", "Hz"), "Y": ("crystal or oscillator", "Hz"),
    "FB": ("ferrite bead", "Ω"),
}
# words in a catalogue description that identify the class, in priority order.
# "Inductors" before "Resistor" because a bead is described as both.
CLASS_WORDS = [
    ("Terminal Block", "terminal block"), ("Connector", "connector"),
    ("Oscillator", "oscillator"), ("Crystal", "crystal"), ("Resonator", "crystal"),
    ("Capacitors", "capacitor"), ("Capacitor", "capacitor"),
    ("Ferrite Bead", "ferrite bead"), ("Inductors", "inductor"), ("Inductor", "inductor"),
    ("Resistor", "resistor"), ("Diode", "diode"), ("Transistor", "transistor"),
]
COMPATIBLE = {
    "crystal or oscillator": {"crystal", "oscillator"},
    "capacitor": {"capacitor"}, "resistor": {"resistor"},
    "inductor": {"inductor", "ferrite bead"},
    "ferrite bead": {"ferrite bead", "inductor"},
}

MULT = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "μ": 1e-6, "m": 1e-3,
        "": 1.0, "k": 1e3, "K": 1e3, "M": 1e6, "G": 1e9, "R": 1.0}
UNIT_ALIASES = {"F": "F", "Ω": "Ω", "R": "Ω", "OHM": "Ω", "ohm": "Ω",
                "H": "H", "HZ": "Hz", "Hz": "Hz"}

VAL_RE = re.compile(r"(?<![A-Za-z0-9.])(\d+(?:\.\d+)?)\s*"
                    r"([pnuµμmkKMG]?)\s*(F|H|Hz|HZ|Ω|R|ohm|OHM)\b")
# an EIA / metric package token: 0201, 0402, 0603, 1005Metric, 0603Metric...
PKG_RE = re.compile(r"(?<![0-9])(01005|0201|0402|0603|0805|1206|1210|1812|2010|2512)(?![0-9])")
# crystals name a metric size instead: Crystal_SMD_2016-... / SMD2016-4P
XTAL_RE = re.compile(r"(?<![0-9])(2016|2520|3215|3225|5032)(?!Metric)(?![0-9])")
METRIC_RE = re.compile(r"(?<![0-9])(0402|0603|1005|1608|2012|3216)Metric")
# KiCad footprints name the imperial code first: C_0201_0603Metric
METRIC_TO_IMPERIAL = {"0402": "01005", "0603": "0201", "1005": "0402",
                      "1608": "0603", "2012": "0805", "3216": "1206"}


def si(num, mult, unit):
    u = UNIT_ALIASES.get(unit, unit)
    m = MULT.get(mult, None)
    if m is None:
        return None
    return float(num) * m, u


def parse_value_of(text, unit):
    """The first SI quantity in `text` carrying the unit asked for.

    A catalogue description lists several quantities: an inductor states its
    inductance AND its DC resistance, a crystal its frequency AND its load
    capacitance. Taking the first one found compares henries to ohms and
    reports FAIL for the wrong reason — a check that is red by accident is as
    untrustworthy as one that is green by accident.
    """
    if not text or not unit:
        return None
    for m in VAL_RE.finditer(text):
        v = si(m.group(1), m.group(2), m.group(3))
        if v and v[1] == unit:
            return v
    return None


def parse_value(text):
    """Read the first SI quantity out of a string. None if there is not one.

    Handles the bare-multiplier shorthand a schematic uses for passives:
    `10k` on an R line is 10 kΩ, `4.7M` is 4.7 MΩ, `0R` is 0 Ω, `2.7nH` is
    2.7 nH. The unit is only inferred from the designator class, never guessed
    across classes — a `10k` on a C line stays unparsed rather than becoming
    10 kF.
    """
    if not text:
        return None
    m = VAL_RE.search(text)
    if m:
        return si(m.group(1), m.group(2), m.group(3))
    return None


def parse_bare(text, unit):
    """`10k`, `4.7M`, `0R`, `2.2u` with the unit supplied by the designator."""
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([pnuµμmkKMGR]?)\s*", text or "")
    if not m:
        return None
    mult = m.group(2)
    if mult == "R":
        mult = ""
    return si(m.group(1), mult, unit)


def fmt(v):
    if v is None:
        return "—"
    x, u = v
    if x == 0:
        return f"0 {u}"
    for p, s in ((1e9, "G"), (1e6, "M"), (1e3, "k"), (1, ""), (1e-3, "m"),
                 (1e-6, "u"), (1e-9, "n"), (1e-12, "p")):
        if abs(x) >= p or p == 1e-12:
            return f"{x / p:g} {s}{u}"
    return f"{x:g} {u}"


def klass_of_description(desc):
    for word, name in CLASS_WORDS:
        if word.lower() in (desc or "").lower():
            return name
    return None


def imperial_of(footprint):
    """The imperial size code a KiCad passive footprint names, or None."""
    m = METRIC_RE.search(footprint or "")
    if m:
        return METRIC_TO_IMPERIAL.get(m.group(1))
    m = XTAL_RE.search(footprint or "")
    if m:
        return m.group(1)
    m = PKG_RE.search(footprint or "")
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bom")
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--value-tol-pct", type=float, default=1.0,
                    help="how far the catalogue value may sit from the schematic value")
    a = ap.parse_args()

    if not pathlib.Path(a.db).is_file():
        print(f"CANNOT DETERMINE: no parts catalogue at {a.db}", file=sys.stderr)
        return 2
    db = sqlite3.connect(a.db)
    db.row_factory = sqlite3.Row
    try:
        snapshot = dict(db.execute("select key,value from meta")).get("data_date", "unknown")
    except sqlite3.Error:
        snapshot = "unknown"

    rows, by_code = [], {}
    with open(a.bom, newline="", encoding="utf-8-sig") as fh:
        for line in csv.DictReader(fh):
            k = {(c or "").strip().lower(): (v or "").strip() for c, v in line.items()}
            desig = k.get("designator", "")
            code = k.get("lcsc part #") or k.get("lcsc") or ""
            value = k.get("value", "")
            fp = k.get("footprint", "")
            if not desig:
                continue

            first = desig.split(",")[0].strip()
            prefix = re.match(r"[A-Z]+", first)
            prefix = prefix.group(0) if prefix else ""
            want_class, want_unit = CLASS.get(prefix, (None, None))

            r = {"designator": desig, "lcsc": code, "value": value, "footprint": fp,
                 "prefix": prefix, "checks": []}

            def add(name, verdict, why, **kw):
                r["checks"].append({"name": name, "verdict": verdict, "why": why, **kw})

            # ---- I6 line_has_a_part -----------------------------------------
            if value.upper() == "DNP":
                add("line_has_a_part", PASS, "marked DNP: deliberately not fitted")
                rows.append(r)
                continue
            if not code:
                add("line_has_a_part", CD,
                    "the line names no LCSC code, so nothing can be ordered or checked")
                rows.append(r)
                continue
            add("line_has_a_part", PASS, f"names {code}")

            # ---- I1 part_resolves -------------------------------------------
            p = db.execute("select * from parts where lcsc=?", (code,)).fetchone()
            if p is None:
                add("part_resolves", CD,
                    f"{code} is not in the {snapshot} catalogue snapshot — its identity "
                    f"cannot be checked here, so nothing about this line is confirmed")
                rows.append(r)
                continue
            desc, mpn, pkg = p["description"] or "", p["mpn"] or "", p["package"] or ""
            r["mpn"], r["package"], r["description"] = mpn, pkg, desc
            add("part_resolves", PASS, f"{code} = {mpn} ({pkg})")

            # ---- I2 class_matches -------------------------------------------
            # A 0-ohm link is a resistor wherever the sheet puts it: an "L"
            # ref fitted as a 0 R jumper is normal practice (board.py's L10),
            # and refusing the class there would make the checker wrong, not
            # the board. The VALUE check below still has to say 0.
            zero_link = re.fullmatch(r"0\s*(Ω|R|ohm|ohms)?", (value or "").strip(),
                                     re.I) is not None
            got_class = klass_of_description(desc)
            if zero_link and want_class in ("inductor", "ferrite bead",
                                            "resistor"):
                add("class_matches", PASS,
                    f"{prefix}* is fitted as a 0 Ω jumper: {code} is a "
                    f"{got_class} of 0 Ω, which is the same link")
            elif want_class is None:
                add("class_matches", PASS,
                    f"{prefix}* is not a passive designator; identity is judged by MPN below")
            elif got_class is None:
                add("class_matches", CD,
                    f"the catalogue description names no component class: {desc[:70]!r}")
            elif got_class in COMPATIBLE.get(want_class, {want_class}):
                add("class_matches", PASS, f"{prefix}* wants a {want_class}; {code} is a {got_class}")
            else:
                add("class_matches", FAIL,
                    f"{prefix}* is a {want_class} but {code} ({mpn}) is a {got_class} — {desc[:80]}")

            # ---- I3 value_matches -------------------------------------------
            want = parse_value(value) or (parse_bare(value, want_unit) if want_unit else None)
            got = (parse_value_of(desc, want_unit) if want_unit else None) \
                or (parse_value_of(mpn, want_unit) if want_unit else None) \
                or parse_value(desc)
            if want_class is None:
                ok = mpn and value and (value.lower().replace("-", "") in
                                        mpn.lower().replace("-", "")
                                        or mpn.lower().replace("-", "") in
                                        value.lower().replace("-", ""))
                add("value_matches", PASS if ok else FAIL,
                    f"BOM value {value!r} vs catalogue MPN {mpn!r}: "
                    + ("the same part" if ok else "these are not the same part number"),
                    want=value, got=mpn)
            elif want is None:
                add("value_matches", CD, f"the BOM value {value!r} does not parse as a {want_unit}")
            elif got is None:
                add("value_matches", CD,
                    f"the catalogue description states no {want_unit} value: {desc[:70]!r}")
            elif got[1] != want[1]:
                add("value_matches", FAIL,
                    f"BOM asks for {fmt(want)} but {code} is specified in {got[1]}, a different quantity",
                    want=fmt(want), got=fmt(got))
            else:
                base = abs(want[0]) or abs(got[0]) or 1.0
                err = abs(got[0] - want[0]) / base * 100
                add("value_matches", PASS if err <= a.value_tol_pct else FAIL,
                    f"BOM asks for {fmt(want)}; {code} ({mpn}) is {fmt(got)} — "
                    + ("the same value" if err <= a.value_tol_pct
                       else f"off by {err:.0f}%"),
                    want=fmt(want), got=fmt(got), error_pct=round(err, 2))

            # ---- I4 package_matches -----------------------------------------
            want_pkg, got_pkg = imperial_of(fp), imperial_of(pkg)
            if want_class is None:
                add("package_matches", PASS, "not a passive: package is judged by the footprint library")
            elif want_pkg is None or got_pkg is None:
                add("package_matches", CD,
                    f"no size code readable from footprint {fp!r} / package {pkg!r}")
            else:
                add("package_matches", PASS if want_pkg == got_pkg else FAIL,
                    f"footprint {fp} is {want_pkg}; {code} is {got_pkg}"
                    + ("" if want_pkg == got_pkg else
                       " — the land pattern and the part are different sizes"),
                    want=want_pkg, got=got_pkg)

            by_code.setdefault(code, set()).add(value)
            rows.append(r)

    # ---- I5 one_code_one_value ---------------------------------------------
    collisions = {c: sorted(v) for c, v in by_code.items() if len(v) > 1}
    for r in rows:
        c = r.get("lcsc")
        if c in collisions:
            r["checks"].append({
                "name": "one_code_one_value", "verdict": FAIL,
                "why": f"{c} is ordered for {len(collisions[c])} different values on this BOM: "
                       f"{', '.join(collisions[c])} — one part cannot be all of them"})
        elif c:
            r["checks"].append({"name": "one_code_one_value", "verdict": PASS,
                                "why": f"{c} serves exactly one value on this BOM"})

    tally = {PASS: 0, FAIL: 0, CD: 0}
    for r in rows:
        for c in r["checks"]:
            tally[c["verdict"]] += 1
        r["verdict"] = max((c["verdict"] for c in r["checks"]), key=lambda v: RANK[v])
    worst = max((r["verdict"] for r in rows), key=lambda v: RANK[v]) if rows else CD

    out = {"$halo": 1, "tool": "tools/check_bom_identity.py",
           "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "bom": str(pathlib.Path(a.bom).resolve()), "catalogue_snapshot": snapshot,
           "verdict": worst, "lines": len(rows), "assertion_counts": tally,
           "code_collisions": collisions, "rows": rows,
           "command": "python3 " + " ".join(sys.argv)}
    if a.json:
        pathlib.Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.json).write_text(json.dumps(out, indent=1) + "\n")

    if not a.quiet:
        print(f"# check_bom_identity — {a.bom}  (catalogue snapshot {snapshot})")
        for r in rows:
            bad = [c for c in r["checks"] if c["verdict"] != PASS]
            if not bad:
                continue
            print(f"  {r['verdict']:<16} {r['designator']:<22} {r.get('value',''):<10} "
                  f"{r.get('lcsc','') or '—'}")
            for c in bad:
                print(f"      {c['verdict']:<16} {c['name']:<20} {c['why']}")
        print(f"{worst}: {len(rows)} line(s); assertions "
              f"{tally[PASS]} pass, {tally[FAIL]} fail, {tally[CD]} cannot determine")
    return {PASS: 0, FAIL: 1, CD: 2}[worst]


if __name__ == "__main__":
    sys.exit(main())
