#!/usr/bin/env python3
"""x_schematic_check — grade the Replica schematic against the things it claims.

    tools/x_schematic_check.py              PASS / FAIL / CANNOT DETERMINE
    tools/x_schematic_check.py --self-test  break it seven ways on purpose

Exit 0 = every check PASS. Exit 1 = any FAIL or any CANNOT DETERMINE. Exit 2 =
the toolchain is not here. A schematic that could not be graded is not a
schematic that passed.

---------------------------------------------------------------------------
WHY THIS EXISTS AND WHAT IT IS *NOT*
---------------------------------------------------------------------------
`bin/sch all` already runs KiCad's ERC. This tool does not re-run it and does
not second-guess it. It checks the four ways the schematic can be WRONG WHILE
ERC IS GREEN, which is the failure mode E07 spends 32 entries on:

  1. THE COMMITTED ARTIFACT IS NOT WHAT THE SOURCE PRODUCES. Somebody edited
     the .kicad_sch in KiCad, or the .kicad_sch is stale. ERC grades the file;
     nothing grades the file against `schematic.py`. C1 rebuilds and compares.
  2. A PART CITES A BOM LINE THAT IS NOT THERE. `schematic.py` checks this at
     build time from its own dict; C2 checks it by READING THE SAVED FILE and
     `bom/bom.json` separately, so a stale artifact cannot hide behind a
     source file that would still pass.
  3. NETS.md AND THE NETLIST HAVE DRIFTED. C3 does not compare NETS.md to the
     Python that wrote it — that would be a check agreeing with what it
     checks, E07 §1. It compares NETS.md to **KiCad's own netlister** reading
     the saved schematic.
  4. AN ERC REPORT THAT IS OLDER THAN THE SCHEMATIC, OR WEAKENED. A stale
     `.erc.json` is the classic check that cannot fail: it will happily report
     zero errors about a file that no longer exists in that form. C4 requires
     the report to be NEWER than the schematic, to name it, AND requires the
     project to carry no `erc_exclusions` and no downgraded rule severities.

And two regressions specific to what this lane was asked to preserve:

  5. U2 IS STILL DNP. The single instruction most likely to be "tidied" by a
     later hand is the unpopulated UWB module. C5 reads the flag out of the
     saved file.
  6. NOTHING HAS BEEN FILLED IN. Every part whose bom.json line says CANNOT
     DETERMINE must still say CANNOT DETERMINE on the sheet. This is the
     check that fires the day someone replaces "VALUE CANNOT DETERMINE" with
     "100nF" because it looked unfinished.

---------------------------------------------------------------------------
AND THE ONE THAT MATTERS MOST — C7, --self-test ONLY
---------------------------------------------------------------------------
**Can the ERC I am citing actually go red on THIS file?** E07's rule is that a
check which cannot fail is not a check, and "ERC PASS" is a claim about a tool
run by another tool through a project file this repository generated. C7 takes
a copy of the schematic, DELETES ONE no-connect flag, and requires kicad-cli
to report a real error. If it does not, then every ERC PASS in this lane is
decoration and the self-test says so instead of the schematic.

The other six breaks are the ordinary kind: mutate a copy so exactly one check
must go red, and require that it does — and require that the OTHER checks do
not, because a break that trips everything proves nothing about which check
caught it.

NOTE ON WHAT THIS TOOL DOES NOT AND CANNOT CHECK: whether the circuit is
Apple's. Nobody has traced Apple's copper. Every net on that sheet is
INFERRED or CHOSEN except seven, and NO TOOL IN THIS REPOSITORY CAN GRADE A
RECONSTRUCTION AGAINST A BOARD NOBODY HAS PROBED. This grades the drawing
against its own stated sources, and that is a smaller claim on purpose.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
WORKSHOP = "/Users/leifrydenfalk/dev/ce-workshop"
if os.path.join(WORKSHOP, "ce-pcb") not in sys.path:
    sys.path.insert(0, os.path.join(WORKSHOP, "ce-pcb"))

SCH_PY = os.path.join(REPLICA, "schematic", "schematic.py")
NETS_MD = os.path.join(REPLICA, "schematic", "NETS.md")
OUT = os.path.join(REPLICA, "out", "schematic")
SCH = os.path.join(OUT, "halo_replica.kicad_sch")
ERC = os.path.join(OUT, "halo_replica.erc.json")
PRO = os.path.join(OUT, "halo_replica.kicad_pro")
BOM = os.path.join(REPLICA, "bom", "bom.json")

PASS, FAIL, CANNOT = "PASS", "FAIL", "CANNOT DETERMINE"
MEASURED = "MEASURED"

#: the one string a part is allowed to carry instead of a bom.json ref, for a
#: component this sheet ADDED (D3, the D24 diode; the straps; the test points).
NOT_IN_BOM = "NOT IN bom.json - see Note"

#: The title block carries today's date, so two builds on two days differ by
#: one line and that difference is not drift. Nothing else may differ.
DATE_LINE = re.compile(r'^\s*\(date "[^"]*"\)\s*$')


class Result(object):
    def __init__(self, key, verdict, detail):
        self.key, self.verdict, self.detail = key, verdict, detail

    def __repr__(self):
        return "%-9s %-26s %s" % (self.verdict, self.key, self.detail)


def _normalise(text):
    """The schematic, minus the one line that legitimately changes daily."""
    return [ln for ln in text.splitlines() if not DATE_LINE.match(ln)]


# ==========================================================================
# the checks
# ==========================================================================

def c1_artifact_matches_source(paths):
    """C1 — rebuild from schematic.py and compare to the file on disk."""
    if not os.path.exists(paths["sch"]):
        return Result("C1 artifact=source", CANNOT,
                      "no schematic at %s to compare against." % paths["sch"])
    import importlib.util
    spec = importlib.util.spec_from_file_location("_replica_sch", SCH_PY)
    mod = importlib.util.module_from_spec(spec)
    tmp = tempfile.mkdtemp(prefix="x-sch-rebuild-")
    try:
        spec.loader.exec_module(mod)
        s = mod.build()
        # save(), NOT dumps(). save() writes the library tables FIRST and
        # canonicalises every symbol this sheet generated itself, and the
        # schematic then embeds the canonical form. dumps() alone is a
        # different document, and a C1 built on it would report drift on a
        # file that had never drifted - a check that can only fail.
        written = s.save(os.path.join(tmp, "halo_replica.kicad_sch"))
        with open(written, "r", encoding="utf-8") as fh:
            fresh = fh.read()
    except Exception as e:                                   # noqa: BLE001
        return Result("C1 artifact=source", CANNOT,
                      "schematic.py did not build, so nothing can be "
                      "compared to it: %s: %s" % (type(e).__name__, e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    with open(paths["sch"], "r", encoding="utf-8") as fh:
        onfile = fh.read()
    a, b = _normalise(fresh), _normalise(onfile)
    if a == b:
        return Result("C1 artifact=source", PASS,
                      "%d lines identical (the title-block date is excluded "
                      "and is the only permitted difference)." % len(a))
    first = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]),
                 min(len(a), len(b)))
    return Result(
        "C1 artifact=source", FAIL,
        "the committed .kicad_sch is NOT what schematic.py produces "
        "(%d lines on disk vs %d rebuilt; first difference at line %d).\n"
        "    on disk : %s\n    rebuilt : %s\n"
        "    Somebody edited the artifact, or it is stale. Rebuild with "
        "bin/sch all; never hand-edit the output."
        % (len(b), len(a), first + 1,
           (b[first] if first < len(b) else "<end of file>").strip()[:110],
           (a[first] if first < len(a) else "<end of file>").strip()[:110]))


def _symbols(sch_text):
    """(ref, {property: value, ...}) for every placed symbol.

    Parsed with cepcb's own reader rather than a regex, because a regex over
    an s-expression is a second, worse parser and it will disagree with KiCad
    exactly where it matters.
    """
    from cepcb import sexpr
    tree = sexpr.parse(sch_text)
    out = []
    for node in sexpr.children(tree, "symbol"):
        props = {}
        for p in sexpr.children(node, "property"):
            if len(p) >= 3:
                props[str(p[1])] = str(p[2])
        ref = props.get("Reference")
        if ref is None:
            continue
        # '#PWR01', '#FLG01': KiCad's own convention for a symbol that is not
        # a part - a power rail marker or a PWR_FLAG. cepcb places them
        # itself. They carry no BOM line because there is nothing to buy, and
        # demanding one would be a check that can only fail.
        if ref.startswith("#"):
            continue
        dnp = sexpr.child(node, "dnp")
        props["__dnp__"] = bool(dnp) and str(dnp[1]) == "yes"
        out.append((ref, props))
    return out


def c2_bom_cited(paths):
    """C2 — every part names a bom.json line, read from the SAVED file."""
    if not os.path.exists(paths["sch"]):
        return Result("C2 bom cited", CANNOT, "no schematic on disk.")
    if not os.path.exists(paths["bom"]):
        return Result("C2 bom cited", CANNOT,
                      "no bom.json at %s, so no citation can be resolved."
                      % paths["bom"])
    with open(paths["bom"], "r", encoding="utf-8") as fh:
        refs = {ln["ref"] for ln in json.load(fh)["lines"]}
    with open(paths["sch"], "r", encoding="utf-8") as fh:
        syms = _symbols(fh.read())
    bad, missing = [], []
    for ref, props in syms:
        cited = props.get("BOM line")
        if cited is None:
            missing.append(ref)
        elif cited != NOT_IN_BOM and cited not in refs:
            bad.append("%s cites %r" % (ref, cited))
    if missing or bad:
        parts = []
        if missing:
            parts.append("%d part(s) carry NO 'BOM line' field at all: %s"
                         % (len(missing), ", ".join(sorted(missing)[:10])))
        if bad:
            parts.append("%d part(s) cite a line bom.json does not have: %s"
                         % (len(bad), "; ".join(sorted(bad)[:10])))
        return Result("C2 bom cited", FAIL,
                      ". ".join(parts) + ".\n    The schematic and the BOM "
                      "have drifted, which means they describe two different "
                      "products.")
    n_real = sum(1 for _r, p in syms if p.get("BOM line") != NOT_IN_BOM)
    return Result("C2 bom cited", PASS,
                  "%d of %d parts resolve to a bom.json line; the other %d "
                  "declare themselves additions." %
                  (n_real, len(syms), len(syms) - n_real))


def _nets_md_rows(text):
    """{net: (basis, pin_count)} from the generated table."""
    rows = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*`([^`]+)`\s*\((\d+) pins\)\s*\|\s*\*\*(\w[\w ]*)"
                     r"\*\*\s*\|", line)
        if m:
            rows[m.group(1)] = (m.group(3).strip(), int(m.group(2)))
    return rows


def c3_nets_described(paths):
    """C3 — NETS.md against KICAD'S OWN netlist of the saved schematic."""
    if not os.path.exists(paths["nets_md"]):
        return Result("C3 nets described", CANNOT, "no NETS.md.")
    from cepcb import schematic as S
    if not S.kicad_cli():
        return Result("C3 nets described", CANNOT,
                      "kicad-cli is not on this machine, so the netlist "
                      "cannot be read back by the tool that reads it for "
                      "real. Comparing NETS.md to the Python that wrote it "
                      "would be a check agreeing with what it checks.")
    try:
        nets = S.netlist_of_sch(paths["sch"])
    except Exception as e:                                   # noqa: BLE001
        return Result("C3 nets described", CANNOT,
                      "KiCad could not net-list the schematic: %s" % e)
    with open(paths["nets_md"], "r", encoding="utf-8") as fh:
        rows = _nets_md_rows(fh.read())
    # KiCad emits one pseudo-net per no-connect pin, named
    # 'unconnected-(U1-P0.25-Pad37)'. Those are the 14 deliberate
    # no-connects, already printed by name at build time; they are not nets
    # anyone drew and NETS.md is right not to list them.
    real = {k: len(v) for k, v in nets.items()
            if k and not k.startswith("unconnected-(")}
    undescribed = sorted(set(real) - set(rows))
    stale = sorted(set(rows) - set(real))
    wrong = sorted("%s (NETS.md says %d pins, KiCad counts %d)"
                   % (k, rows[k][1], real[k])
                   for k in set(rows) & set(real) if rows[k][1] != real[k])
    if undescribed or stale or wrong:
        bits = []
        if undescribed:
            bits.append("%d net(s) in the netlist and NOT in NETS.md: %s"
                        % (len(undescribed), ", ".join(undescribed[:8])))
        if stale:
            bits.append("%d row(s) in NETS.md that are NOT nets: %s"
                        % (len(stale), ", ".join(stale[:8])))
        if wrong:
            bits.append("%d row(s) with the wrong pin count: %s"
                        % (len(wrong), "; ".join(wrong[:6])))
        return Result("C3 nets described", FAIL, ". ".join(bits) + ".")
    bases = {}
    for basis, _n in rows.values():
        bases[basis] = bases.get(basis, 0) + 1
    return Result("C3 nets described", PASS,
                  "%d nets, each described with a basis and a matching pin "
                  "count (%s)." % (len(rows),
                                   ", ".join("%d %s" % (v, k)
                                             for k, v in sorted(bases.items()))))


def c4_erc_fresh_and_clean(paths):
    """C4 — the ERC report is newer than the schematic, names it, and is not
    weakened by exclusions or downgraded severities."""
    if not os.path.exists(paths["erc"]):
        return Result("C4 erc fresh+clean", CANNOT,
                      "no .erc.json. Run bin/sch all. An absent report is "
                      "not a clean one.")
    if os.path.getmtime(paths["erc"]) < os.path.getmtime(paths["sch"]):
        return Result("C4 erc fresh+clean", FAIL,
                      "THE ERC REPORT IS OLDER THAN THE SCHEMATIC. It is a "
                      "verdict about a file that has since changed, which is "
                      "the exact shape of a check that cannot fail.")
    with open(paths["erc"], "r", encoding="utf-8") as fh:
        erc = json.load(fh)
    src = erc.get("source", "")
    if os.path.basename(str(src)) != os.path.basename(paths["sch"]):
        return Result("C4 erc fresh+clean", FAIL,
                      "the report names %r, not %r." %
                      (src, os.path.basename(paths["sch"])))
    errors = warnings = 0
    for sheet in erc.get("sheets", []):
        for v in sheet.get("violations", []):
            if v.get("severity") == "error":
                errors += 1
            elif v.get("severity") == "warning":
                warnings += 1
    weakened = []
    if os.path.exists(paths["pro"]):
        with open(paths["pro"], "r", encoding="utf-8") as fh:
            pro = json.load(fh)
        ex = pro.get("erc", {}).get("erc_exclusions") or []
        sev = pro.get("erc", {}).get("rule_severities") or {}
        if ex:
            weakened.append("%d erc_exclusions in the project" % len(ex))
        downgraded = [k for k, v in sev.items() if v in ("ignore", "warning")]
        if downgraded:
            weakened.append("rule severities downgraded: " +
                            ", ".join(sorted(downgraded)[:6]))
    if weakened:
        return Result("C4 erc fresh+clean", FAIL,
                      "the ERC that passed was weakened first: " +
                      "; ".join(weakened) + ". Never loosen a check to make "
                      "it pass.")
    if errors:
        return Result("C4 erc fresh+clean", FAIL,
                      "%d ERC error(s), %d warning(s)." % (errors, warnings))
    return Result("C4 erc fresh+clean", PASS,
                  "0 errors, %d warning(s), report newer than the schematic, "
                  "no exclusions and no downgraded severities." % warnings)


def c5_dnp_held(paths):
    """C5 — U2, Apple's UWB SiP, is still marked do-not-populate."""
    if not os.path.exists(paths["sch"]):
        return Result("C5 U2 still DNP", CANNOT, "no schematic on disk.")
    with open(paths["sch"], "r", encoding="utf-8") as fh:
        syms = dict(_symbols(fh.read()))
    if "U2" not in syms:
        return Result("C5 U2 still DNP", FAIL,
                      "U2 IS NOT ON THE SHEET AT ALL. Apple's UWB module is "
                      "placed precisely so that a replica which cannot be "
                      "finished says so on its own schematic. Deleting it "
                      "makes the sheet look buildable.")
    if not syms["U2"].get("__dnp__"):
        return Result("C5 U2 still DNP", FAIL,
                      "U2's DNP flag is GONE. Apple's U1 UWB SiP is not sold "
                      "to anyone, at any price, with any lead time, and its "
                      "pin numbering on this sheet is invented. A populated "
                      "U2 is an order nobody can place against a land "
                      "pattern that does not exist.")
    return Result("C5 U2 still DNP", PASS,
                  "U2 carries dnp=yes and its value says UNPOPULATED.")


def _identity_unknown(line):
    """Is this bom.json line's PART IDENTITY undetermined?

    THE FIRST VERSION OF THIS WAS WRONG AND THE TOOL CAUGHT IT ON ITS FIRST
    RUN. It asked whether the string "CANNOT DETERMINE" appeared anywhere in
    the confidence field, and that fired on ANT1/ANT2/ANT3 - three structures
    Apple LABELLED ITSELF in a regulatory filing, whose confidence reads
    "HIGH for the label. CANNOT DETERMINE for the geometry." An unknown
    GEOMETRY is not an unknown IDENTITY, and a check that cannot tell them
    apart demands that a well-identified part call itself unknown.

    The rule now: the identity is undetermined when the `part` field itself
    says so, or when the confidence LEADS with it. That is 12 of the 27
    lines, and it is the set whose value on the sheet must stay missing.
    """
    return ("CANNOT DETERMINE" in line["part"]
            or line["confidence"].strip().startswith("CANNOT DETERMINE"))


def c6_nothing_filled_in(paths):
    """C6 — a part whose BOM line is CANNOT DETERMINE still says so."""
    if not os.path.exists(paths["sch"]) or not os.path.exists(paths["bom"]):
        return Result("C6 nothing filled in", CANNOT,
                      "need both the schematic and bom.json.")
    with open(paths["bom"], "r", encoding="utf-8") as fh:
        lines = {ln["ref"]: ln for ln in json.load(fh)["lines"]}
    with open(paths["sch"], "r", encoding="utf-8") as fh:
        syms = _symbols(fh.read())
    tidied, watched = [], 0
    for ref, props in syms:
        cited = props.get("BOM line")
        if cited not in lines:
            continue
        if not _identity_unknown(lines[cited]):
            continue
        watched += 1
        if CANNOT not in props.get("Value", ""):
            tidied.append("%s (cites %s) now reads %r"
                          % (ref, cited, props.get("Value", "")[:60]))
    if tidied:
        return Result("C6 nothing filled in", FAIL,
                      "%d part(s) whose bom.json line is CANNOT DETERMINE no "
                      "longer say so on the sheet: %s.\n    A missing value "
                      "stays missing. Somebody filled in a plausible number, "
                      "and a plausible number is how a reconstruction starts "
                      "reading as a measurement."
                      % (len(tidied), "; ".join(tidied[:6])))
    return Result("C6 nothing filled in", PASS,
                  "%d part(s) rest on a CANNOT DETERMINE bom line and all %d "
                  "still carry it in their value." % (watched, watched))


CHECKS = [c1_artifact_matches_source, c2_bom_cited, c3_nets_described,
          c4_erc_fresh_and_clean, c5_dnp_held, c6_nothing_filled_in]


def _measured_line():
    """How many nets were measured — READ OFF THE SHEET, not typed.

    The sentence here used to say "Seven of 51 nets were measured". Both
    numbers went stale the same afternoon, when opening a cited file turned
    four CHOSEN nets into MEASURED ones and added nine test points. A count
    beside a table is a count that will be wrong; this one is a count OF the
    table.
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("_replica_sch3", SCH_PY)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        s = mod.build()
        rep = s.basis_report()
        return ("%d of %d nets are MEASURED (%d inferred, %d chosen)."
                % (rep["counts"]["MEASURED"], len(s.nets),
                   rep["counts"]["INFERRED"], rep["counts"]["CHOSEN"]))
    except Exception as e:                                   # noqa: BLE001
        return "CANNOT DETERMINE how many nets are measured (%s)." % e


def run(paths):
    return [fn(paths) for fn in CHECKS]


def live_paths():
    return {"sch": SCH, "erc": ERC, "pro": PRO, "bom": BOM,
            "nets_md": NETS_MD}


# ==========================================================================
# the self-test: break it on purpose, seven ways
# ==========================================================================

def _sandbox(tmp):
    """A complete, working copy of the artifacts, so a break is a break in
    ONE of them and everything else is genuinely intact."""
    dst = os.path.join(tmp, "out")
    shutil.copytree(OUT, dst)
    shutil.copy2(NETS_MD, os.path.join(tmp, "NETS.md"))
    shutil.copy2(BOM, os.path.join(tmp, "bom.json"))
    return {"sch": os.path.join(dst, "halo_replica.kicad_sch"),
            "erc": os.path.join(dst, "halo_replica.erc.json"),
            "pro": os.path.join(dst, "halo_replica.kicad_pro"),
            "bom": os.path.join(tmp, "bom.json"),
            "nets_md": os.path.join(tmp, "NETS.md")}


def _edit(path, fn):
    with open(path, "r", encoding="utf-8") as fh:
        t = fh.read()
    t2 = fn(t)
    if t2 == t:
        raise SystemExit("BROKEN SELF-TEST: the mutation of %s changed "
                         "nothing, so the check it targets was never given "
                         "anything to catch. E07 §12." % os.path.basename(path))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(t2)
    os.utime(path, None)


def _break_artifact(p):
    _edit(p["sch"], lambda t: t.replace('(rev "R1")', '(rev "R2")', 1))


def _break_bom_cite(p):
    _edit(p["sch"], lambda t: t.replace('"BOM line" "U1"',
                                        '"BOM line" "U404"', 1))


def _break_nets_md(p):
    _edit(p["nets_md"], lambda t: t.replace("| `NFC1` (2 pins)",
                                            "| `NFC1` (9 pins)", 1))


def _break_erc(p):
    def inject(t):
        d = json.loads(t)
        d["sheets"][0].setdefault("violations", []).append(
            {"severity": "error", "type": "self_test",
             "description": "deliberate break"})
        return json.dumps(d, indent=4)
    _edit(p["erc"], inject)


def _break_erc_by_exclusion(p):
    def weaken(t):
        d = json.loads(t)
        d.setdefault("erc", {})["erc_exclusions"] = ["a rule somebody muted"]
        return json.dumps(d, indent=2)
    _edit(p["pro"], weaken)


def _break_dnp(p):
    _edit(p["sch"], lambda t: t.replace("(dnp yes)", "(dnp no)", 1))


def _break_value(p):
    _edit(p["sch"], lambda t: t.replace(
        '"Value" "3-AXIS ACCELEROMETER - PART CANNOT DETERMINE (BMA280 is a '
        'teardown ASSERTION, not a marking)"', '"Value" "BMA280"', 1))


def _break_erc_stale(p):
    os.utime(p["sch"], None)
    st = os.stat(p["sch"])
    os.utime(p["erc"], (st.st_atime - 60, st.st_mtime - 60))


#: breaks that edit the .kicad_sch itself, and therefore MUST also trip C1
#: (artifact != source) and C4 (the ERC report now predates the file).
_ARTIFACT_EDITS = set()

BREAKS = [
    ("C1 artifact=source", _break_artifact,
     "edit the committed .kicad_sch by hand (rev R1 -> R2)"),
    ("C2 bom cited", _break_bom_cite,
     "point U1's BOM citation at a line bom.json does not have"),
    ("C3 nets described", _break_nets_md,
     "change one pin count in NETS.md so the document and the netlist "
     "disagree"),
    ("C4 erc fresh+clean", _break_erc,
     "inject one error into the ERC report"),
    ("C4 erc fresh+clean", _break_erc_by_exclusion,
     "weaken the ERC by adding an exclusion to the project, leaving the "
     "report itself clean"),
    ("C4 erc fresh+clean", _break_erc_stale,
     "touch the schematic so the clean ERC report is older than the file "
     "it grades"),
    ("C5 U2 still DNP", _break_dnp,
     "clear U2's do-not-populate flag"),
    ("C6 nothing filled in", _break_value,
     "tidy U4's CANNOT DETERMINE value into a confident 'BMA280'"),
]


def _drop_first_node(text, opener):
    """Delete the first balanced `(name ...)` node, leaving valid s-expr."""
    i = text.find(opener)
    if i < 0:
        return None
    depth, j = 0, i
    while j < len(text):
        c = text[j]
        if c == '"':                       # skip a quoted string wholesale
            j += 1
            while j < len(text) and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[:i] + text[j + 1:]
        j += 1
    return None


def anchors_can_fail():
    """C8 — can a MEASURED claim on THIS sheet go red?

    ce-pcb's tests prove the MECHANISM. They do not prove that this design's
    MEASURED nets are actually wired through it: a design could call basis()
    and still hold every claim in a way nothing resolves. So build the real
    sheet, corrupt ONE `contains` claim to a string that is not in the
    anchored file, and require check() to NAME THAT NET.

    That is the difference between "the feature has tests" and "the feature
    is load-bearing here", and E07 §14 is about exactly that gap: a break
    that runs in one place and a check that runs in another are not connected
    by hope.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("_replica_sch2", SCH_PY)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        s = mod.build()
    except Exception as e:                                   # noqa: BLE001
        return Result("C8 anchors can fail", CANNOT,
                      "schematic.py did not build: %s" % e)
    measured = [n for n, b in s.bases.items() if b["kind"] == MEASURED]
    if not measured:
        return Result("C8 anchors can fail", CANNOT,
                      "this sheet declares no MEASURED net, so there is no "
                      "anchor to break.")
    already = [m for _sev, m in s.check() if "does not resolve" in m]
    if already:
        return Result("C8 anchors can fail", FAIL,
                      "%d anchor(s) do not resolve BEFORE any break: %s"
                      % (len(already), already[0][:160]))
    victim = sorted(measured)[0]
    s.bases[victim]["contains"] = "A STRING THAT IS NOT IN THAT FILE 8f3a"
    named = [m for _sev, m in s.check()
             if "does not resolve" in m and victim in m]
    if not named:
        return Result(
            "C8 anchors can fail", FAIL,
            "corrupting %s's claim produced no FAIL row. Then this sheet's "
            "%d MEASURED nets are labels after all, and every count resting "
            "on them must be re-read." % (victim, len(measured)))
    return Result("C8 anchors can fail", PASS,
                  "%d MEASURED nets, all resolving; corrupting %s's claim "
                  "made check() name it. The basis counter on this sheet "
                  "cannot be improved by typing."
                  % (len(measured), victim))


def erc_can_fail():
    """C7 — the one that matters. Take a copy, delete ONE no-connect flag,
    and require kicad-cli to report a real error.

    Without this, every 'ERC PASS' in this lane is a claim about a tool that
    was never shown to be capable of saying no about THIS file.
    """
    from cepcb import schematic as S
    if not S.kicad_cli():
        return Result("C7 ERC can fail", CANNOT,
                      "kicad-cli is not on this machine.")
    tmp = tempfile.mkdtemp(prefix="x-erc-canfail-")
    try:
        dst = os.path.join(tmp, "out")
        shutil.copytree(OUT, dst)
        sch = os.path.join(dst, "halo_replica.kicad_sch")
        with open(sch, "r", encoding="utf-8") as fh:
            t = fh.read()
        # THE FIRST VERSION OF THIS BREAK COULD NOT FIRE, and the self-test
        # said so instead of passing: it renamed "(no_connect" to
        # "(no_connect_REMOVED_BY_SELFTEST", which leaves an s-expression
        # KiCad refuses to parse at all - "Failed to load schematic", rc 3.
        # That tests the PARSER, not the ERC, and E07 sections 12 and 14 are
        # both about exactly this: a break severed from the thing it was
        # meant to break. The fix is to delete the whole balanced node, so
        # the copy is a VALID schematic that is missing one no-connect flag.
        t2 = _drop_first_node(t, "(no_connect")
        if t2 is None:
            return Result("C7 ERC can fail", CANNOT,
                          "the sheet carries no no_connect marker to remove, "
                          "so this break has nothing to break.")
        with open(sch, "w", encoding="utf-8") as fh:
            fh.write(t2)
        rc, data, out, log = S.erc(sch, out=os.path.join(tmp, "broken.json"))
        if not os.path.exists(out):
            return Result("C7 ERC can fail", CANNOT,
                          "kicad-cli produced no report on the broken copy "
                          "(rc=%s):\n%s" % (rc, log[:400]))
        with open(out, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        errs = [v for sh in d.get("sheets", [])
                for v in sh.get("violations", [])
                if v.get("severity") == "error"]
        if not errs:
            return Result(
                "C7 ERC can fail", FAIL,
                "REMOVING A NO-CONNECT FLAG PRODUCED NO ERC ERROR. Then the "
                "ERC PASS this lane reports is not evidence about this file, "
                "and every claim resting on it must be re-read. This is the "
                "check that grades the checker.")
        return Result("C7 ERC can fail", PASS,
                      "deleting one no_connect produced %d ERC error(s) "
                      "(%s) — the ERC on this file can go red, so its PASS "
                      "carries information."
                      % (len(errs), errs[0].get("type", "?")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


_ARTIFACT_EDITS.update({_break_artifact, _break_bom_cite, _break_dnp,
                        _break_value})


def self_test():
    print("--- SELF-TEST: %d deliberate breaks, each must be caught by ONE "
          "named check ---\n" % len(BREAKS))
    ok = True
    for target, breaker, what in BREAKS:
        tmp = tempfile.mkdtemp(prefix="x-sch-selftest-")
        try:
            paths = _sandbox(tmp)
            breaker(paths)
            results = run(paths)
            hit = [r for r in results if r.verdict == FAIL]
            names = [r.key for r in hit]
            caught = target in names
            # A break that trips EVERY check proves nothing about which check
            # caught it, so the collateral is reported and counts against it.
            # Editing the .kicad_sch necessarily makes it differ from its
            # source (C1) and makes the existing ERC report a verdict about
            # a file that has changed (C4). Those two firing is the checks
            # being CONSISTENT, not a break that sprays. Only anything else
            # counts against specificity.
            consequential = ({"C1 artifact=source", "C4 erc fresh+clean"}
                             if breaker in _ARTIFACT_EDITS else set())
            collateral = [n for n in names
                          if n != target and n not in consequential]
            verdict = "CAUGHT " if caught and not collateral else (
                "CAUGHT*" if caught else "MISSED ")
            if not caught:
                ok = False
            print("  %s %-22s %s" % (verdict, target, what))
            if collateral:
                print("           (also tripped: %s — a break should be "
                      "specific)" % ", ".join(sorted(set(collateral))))
            if not caught:
                print("           NOTHING WENT RED. The check is decoration.")
                for r in results:
                    print("             " + repr(r)[:150])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print("")
    for grader in (erc_can_fail, anchors_can_fail):
        r = grader()
        print("  " + repr(r))
        if r.verdict == FAIL:
            ok = False
    print("\n%s: the checks %s fail." % ("PASS" if ok else "FAIL",
                                         "can" if ok else "CANNOT ALL"))
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    try:
        from cepcb import schematic as _S                    # noqa: F401
    except Exception as e:                                   # noqa: BLE001
        print("CANNOT DETERMINE: ce-pcb did not import (%s), so nothing "
              "here can be graded." % e)
        return 2
    results = run(live_paths())
    for r in results:
        print(repr(r))
    bad = [r for r in results if r.verdict != PASS]
    print("")
    if not bad:
        print("PASS — %d/%d checks. %s\n     Note what this does NOT say: "
              "that the circuit is Apple's. The rest is reconstruction, and "
              "no tool in this repository can grade a reconstruction against "
              "a board nobody has probed."
              % (len(results), len(results), _measured_line()))
        return 0
    print("%s — %d of %d checks did not pass."
          % (FAIL if any(r.verdict == FAIL for r in bad) else CANNOT,
             len(bad), len(results)))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
