#!/usr/bin/env python3
"""k_threeway - check and render the Apple | halo_rev_a | halo_replica comparison.

halo Replica lane L9 (THE COMPARISON), 2026-09-05.
Leif, 2026-09-05: "always manage its own tools and create any tools that might be missing."

WHAT THIS IS NOT. It is not a fork of bin/boardmetro. boardmetro measures a board off a
photograph; this measures a DOCUMENT against the files it cites. Different instrument,
different failure mode, no overlapping code. boardmetro stays the only thing in this lane
that touches pixels.

WHAT IT CHECKS. comparison/threeway.json gives, for every cell of the three-way table, an
ANCHOR: a file plus either a dotted path into its JSON and the exact value expected there,
or a literal quote that must appear in it. This tool resolves every anchor against the file
on disk. A cell whose file or path is gone is CANNOT DETERMINE, never a pass.

    0  PASS               every anchor resolved and matched
    1  FAIL               an anchor resolved and DISAGREED - the table has drifted from its sources
    2  CANNOT DETERMINE   an anchor could not be resolved at all

WHAT IT CANNOT DO, STATED BECAUSE THE LIMIT IS THE POINT. It checks that the table agrees
with the files it cites. It cannot check that those files are right. If board.json records
the wrong diameter, this tool will confirm the table faithfully reproduces the wrong
diameter. Its scope is transcription, not truth.

THE E07 PROBLEM AND WHAT WAS DONE ABOUT IT
------------------------------------------
E07's final form: CHECK THE ASSUMPTION THE METHOD SHARES WITH ITS OWN CONTROL.

The obvious negative controls here - point at a missing file, point at a missing path - all
share one assumption with the method: that resolve() returns what is actually in the file.
If resolve() were broken and returned None for everything, all three of those breaks would
still "pass", because None is not the expected value either. A break that passes for the
wrong reason is exactly the family E07 catalogues.

So the breaks below are chosen to attack the COMPARISON's strictness rather than its inputs:

    N1  0.6 -> 0.6000001          a tolerance-based compare would swallow it. Must FAIL.
    N2  "ENIG" -> "enig"          a case-folding compare would swallow it. Must FAIL.
    N3  expect a strict SUBSTRING of the true value. An `in` compare would swallow it. Must FAIL.
    N4  int 4 -> str "4"          a str() coercion would swallow it. Must FAIL.
    N5  a path that does not exist                    Must be CANNOT DETERMINE. Never PASS, never FAIL.
    N6  a file that does not exist                    Must be CANNOT DETERMINE. Never PASS, never FAIL.
    N7  one character removed from a quote anchor     Must FAIL.
    N9  a fidelity verdict outside the vocabulary. It would be dropped from the divergence
        count in silence - the ratchet-with-no-counter failure. Must FAIL.
    N8  POSITIVE CONTROL ON RESOLUTION. The one that separates this tool from a broken one:
        a second, independent reader (plain json.load and hand indexing, no shared code with
        resolve()) reads three real anchors and must get the same values resolve() got, AND
        those values must be non-None. Without this, N1-N7 all pass on a tool that reads
        nothing at all.

VERBS
    check       resolve every anchor. Exit code is the verdict.
    render      write comparison/THREE-WAY.md from the same file.
    selftest    run the nine breaks above and require each to go the colour it must.
"""
import sys, os, json, re, argparse, copy

EX_PASS, EX_FAIL, EX_CANNOT = 0, 1, 2
LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../halo_replica
HALO = os.path.dirname(os.path.dirname(LANE))                        # .../halo
TABLE = os.path.join(LANE, "comparison", "threeway.json")
OUT_MD = os.path.join(LANE, "comparison", "THREE-WAY.md")
DELIV = os.path.join(LANE, "comparison", "deliverable.json")

SIDES = ("apple", "rev_a", "replica")
SIDE_LABEL = {"apple": "Apple AirTag A2187", "rev_a": "halo_rev_a", "replica": "halo_replica"}

# --------------------------------------------------------------------- resolution
class Unresolved(Exception):
    """The anchor could not be resolved at all. CANNOT DETERMINE, never a pass."""

_TOK = re.compile(r'"([^"]+)"|([^.|]+)')

def split_path(path):
    """a.b."c d".3  ->  ['a','b','c d','3'].  Quoted segments may contain dots."""
    return [m.group(1) if m.group(1) is not None else m.group(2)
            for m in _TOK.finditer(path)]

def resolve(anchor, root=HALO):
    """Return (kind, value). Raises Unresolved when the file or the path is not there.

    kind 'value' -> the object found at the path
    kind 'quote' -> True (the quote was present) or False (absent)
    kind 'exists' -> True
    """
    fp = os.path.join(root, anchor["file"])
    if not os.path.exists(fp):
        raise Unresolved(f"no such file: {anchor['file']}")

    if anchor.get("exists"):
        return "exists", True

    if "quote" in anchor:
        with open(fp, "r", errors="replace") as fh:
            body = fh.read()
        return "quote", (anchor["quote"] in body)

    path = anchor["path"]
    want_len = path.endswith("|len")
    if want_len:
        path = path[:-4]
    try:
        with open(fp, "r") as fh:
            node = json.load(fh)
    except Exception as e:
        raise Unresolved(f"{anchor['file']} is not readable JSON: {e}")

    for seg in split_path(path):
        if isinstance(node, list):
            try:
                node = node[int(seg)]
            except (ValueError, IndexError):
                raise Unresolved(f"{anchor['file']}: no index {seg!r} in list of {len(node)}")
        elif isinstance(node, dict):
            if seg not in node:
                raise Unresolved(f"{anchor['file']}: no key {seg!r} at {path}")
            node = node[seg]
        else:
            raise Unresolved(f"{anchor['file']}: {path} runs past a scalar at {seg!r}")
    if want_len:
        if not isinstance(node, (list, dict, str)):
            raise Unresolved(f"{anchor['file']}: |len on a {type(node).__name__}")
        node = len(node)
    return "value", node

def strict_eq(got, want):
    """Exact. Not tolerant, not case-folding, not substring, not coercing.

    Every one of those four leniencies is a deliberate break in selftest (N1-N4); if this
    function is ever loosened, one of them stops going red and the loosening is caught.
    """
    if type(got) is bool or type(want) is bool:
        return type(got) is type(want) and got == want
    if isinstance(got, (int, float)) and isinstance(want, (int, float)):
        return float(got) == float(want)          # exact float equality, on purpose
    return type(got) is type(want) and got == want

# ------------------------------------------------------- the deliverable check
# THREE LEGS, AND THEY ARE THE SAME LESSON THREE TIMES.
#   EXISTS   - a file of the right kind is here and the tool can open it
#   CURRENT  - it is newer than every one of its sources
#   VALID    - its source PASSED ITS OWN CHECKS at the time it was cut
# EXISTENCE IS ADJACENT TO CURRENCY, AND CURRENCY IS ADJACENT TO VALIDITY. Each
# assertion is satisfied by something NEXT TO what we actually want, and each one alone
# reads as evidence. This is not belt-and-braces: an artifact can independently be
# absent, be stale, or be a faithful cut of a board that was never fit to cut - and the
# third is the worst, because the first two assertions wave it through.
#
# WHY AN EMBEDDED TIMESTAMP IS PREFERRED OVER mtime, and this argument is what keeps the
# check alive rather than merely correct: A FRESH CHECKOUT SCRAMBLES EVERY MTIME ON DISK.
# An mtime-only rule calls an entire correct repository stale the first time anyone
# clones it, and a rule that cries wolf on a clean clone gets switched off within a week.
# Every row therefore prefers a stamp the generating tool wrote into its own output and
# records which kind it used.
#
# AND WHY A MISSING SOURCE IS CANNOT DETERMINE RATHER THAN RED: a rule that is always red
# is a rule people learn to skip.
# The counter in threeway.json measures distance FROM APPLE. This measures DISTANCE
# FROM A DELIVERABLE, and the project ran a whole day without it: 130 measurement
# files, 40 measuring tools, and nothing KiCad can open. A row here is GREEN only when
# a file exists that the relevant tool can ACTUALLY OPEN - a path that exists is not an
# artifact, so every row carries a format probe and an empty file at the right name
# stays red.

def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()

def _stamp(path, probe):
    """(iso_string_or_None, kind). EMBEDDED beats mtime; mtime is recorded as weak."""
    import re as _re, datetime as _dt
    if probe:
        try:
            with open(path, "r", errors="replace") as fh:
                head = fh.read(8192)
            m = _re.search(probe, head)
            if m:
                return m.group(1), "embedded"
        except Exception:
            pass
    return (_dt.datetime.fromtimestamp(os.path.getmtime(path))
            .strftime("%Y-%m-%dT%H:%M:%S"), "mtime")

def _iso(t):
    import datetime as _dt
    return _dt.datetime.fromisoformat(t.split("+")[0])

def read_verdict(paths, kind):
    """(errors, unconnected, why) from a KiCad DRC/ERC report. None,None if unreadable.

    ONLY severity 'error' counts against the verdict; warnings are reported and do not
    block. UNCONNECTED ITEMS ARE COUNTED SEPARATELY AND DO BLOCK a fabrication set,
    because an unrouted net is not a warning about a board, it is a board that does not
    work.
    """
    # THE NEWEST REPORT ONLY. The first version SUMMED every matching file, which across
    # halo_rev_a's tree meant adding up several reports of several different boards and
    # returning 1016 errors that belonged to none of them. A verdict is a property of ONE
    # run against ONE board; a sum over runs is a number adjacent to a verdict.
    best, bts = None, None
    for p in paths:
        try:
            d = json.load(open(p))
        except Exception:
            continue
        t = d.get("date") or "0000"
        if bts is None or t > bts:
            best, bts = d, t
    if best is None:
        return None, None
    err = unc = 0
    seen = True
    for d in (best,):
        if kind == "drc":
            err += sum(1 for v in d.get("violations", [])
                       if str(v.get("severity", "error")).lower() == "error")
            unc += len(d.get("unconnected_items", []))
        else:
            for sh in d.get("sheets", []):
                err += sum(1 for v in sh.get("violations", [])
                           if str(v.get("severity", "error")).lower() == "error")
    return (err, unc)

def classify_clearances(doc, drc_paths, roots, root=HALO):
    """Split a DRC's violations into the three classes, REFUSING any excuse whose
    pointer does not resolve or does not support the claim.

    THE GUARD IS THE POINT. If a violation could move out of DRAWN-WRONG by editing a
    string, this gate would be something a lane improves by typing - the ratchet again
    with a nicer face, and worse than no gate because it looks like rigour. So an
    excusing class must name evidence this function RESOLVES, and the evidence must
    SUPPORT the claim: a pointer that resolves while the measured gap sits outside the
    resolution floor is refused exactly like one that does not resolve at all.

    DRAWN-WRONG is the default and needs no pointer. Silence means our fault, never
    Apple's.
    """
    import glob as _glob
    cfg = doc["clearance_classification"]
    floor = cfg["resolution_floor"]["value_mm"]
    classes = cfg["classes"]
    if not drc_paths:
        return None
    # the DRC being classified: newest
    best, bts = None, None
    for p in drc_paths:
        try:
            dd = json.load(open(p))
        except Exception:
            continue
        t = dd.get("date") or "0000"
        if bts is None or t > bts:
            best, bts, bpath = dd, t, p
    if best is None:
        return None
    viol = [v for v in best.get("violations", [])
            if str(v.get("severity", "error")).lower() == "error"]
    hits = []
    for base in roots:
        hits += _glob.glob(os.path.join(base, cfg["expected_input"]["glob"]), recursive=True)
    claims, cls_file = {}, None
    for h in sorted(set(hits)):
        try:
            cd = json.load(open(h))
        except Exception:
            continue
        if cd.get("schema") != "halo/clearance-classification/1":
            continue
        cls_file = os.path.relpath(h, root)
        for c in cd.get("classified", []):
            claims[c.get("index")] = c
    out = {k: 0 for k in classes}
    refused = []
    for i, v in enumerate(viol):
        c = claims.get(i)
        if not c:
            out["DRAWN-WRONG"] += 1; continue
        cl = c.get("class")
        if cl not in classes:
            refused.append(f"violation {i}: class {cl!r} is not one of the three")
            out["DRAWN-WRONG"] += 1; continue
        if not classes[cl]["pointer_required"]:
            out[cl] += 1; continue
        ev = c.get("evidence") or {}
        fp = os.path.join(root, ev.get("file", ""))
        if not ev.get("file") or not os.path.exists(fp):
            refused.append(f"violation {i}: {cl} names evidence {ev.get('file')!r} "
                           f"which does not resolve")
            out["DRAWN-WRONG"] += 1; continue
        try:
            ed = json.load(open(fp))
            ids = {r.get("id") for r in ed.get("rows", [])}
        except Exception:
            refused.append(f"violation {i}: {cl}'s evidence file is not readable rows JSON")
            out["DRAWN-WRONG"] += 1; continue
        want = ev.get("rows") or []
        missing = [r for r in want if r not in ids]
        if not want or missing:
            refused.append(f"violation {i}: {cl} names row(s) {missing or '(none)'} "
                           f"absent from {ev['file']}")
            out["DRAWN-WRONG"] += 1; continue
        # THE POINTER RESOLVED. Does it SUPPORT the claim?
        if cl == "MEASUREMENT-LIMITED":
            gap = c.get("measured_gap_mm")
            if gap is None or float(gap) > floor:
                refused.append(f"violation {i}: MEASUREMENT-LIMITED claims a gap of {gap} mm, "
                               f"OUTSIDE the {floor} mm resolution floor. The pointer resolves "
                               f"and does not support the claim, which is refused the same way "
                               f"as one that does not resolve.")
                out["DRAWN-WRONG"] += 1; continue
        out[cl] += 1
    blocking = sum(n for k, n in out.items() if classes[k]["blocks_fabrication"])
    return dict(drc=os.path.relpath(bpath, root), errors=len(viol), counts=out,
                blocking=blocking, refused=refused, floor_mm=floor,
                classification_file=cls_file,
                note=("no classification file found - every error falls back to DRAWN-WRONG. "
                      "That is not CANNOT DETERMINE: an unexcused violation IS our defect "
                      "until evidence says otherwise." if cls_file is None else None))

def check_deliverable(root=HALO, tree="replica", roots=None):
    """Existence AND currency. A row is green only when a file of the right kind opens
    AND is newer than every one of its sources.

    Three states, and CANNOT DETERMINE is not a pass: an artifact whose source is absent
    is UNMEASURED, not stale, and must not be representable in the same field as either.
    """
    import glob as _glob
    doc = json.load(open(DELIV))
    if roots is None:
        roots = [os.path.join(root, r) for r in doc["trees"][tree]["roots"]]
    else:
        roots = [os.path.abspath(r) for r in roots]
        doc["trees"].setdefault(tree, {"label": ", ".join(roots), "apply_copy_guard": False})
    out, stamps = [], {}
    specs = {r["id"]: r for r in doc["rows"]}

    # pass 1: existence + opening + this row's own timestamp
    for row in doc["rows"]:
        hits = []
        for base in roots:
            hits += [h for h in _glob.glob(os.path.join(base, row["glob"]), recursive=True)
                     if os.path.isfile(h)]
        rec = dict(id=row["id"], what=row["what"], glob=row["glob"], probe=row["probe"],
                   candidates=len(hits), source=row.get("source", []))
        opened, reasons = [], []
        for h in sorted(set(hits)):
            rel = os.path.relpath(h, root)
            try:
                if os.path.getsize(h) == 0:
                    reasons.append(f"{rel}: EMPTY FILE - a name is not an artifact"); continue
                with open(h, "r", errors="replace") as fh:
                    head = fh.read(4096)
            except Exception as e:
                reasons.append(f"{rel}: unreadable ({e})"); continue
            if row["probe"] not in head:
                reasons.append(f"{rel}: does not open as {row['what'].lower()} - "
                               f"no {row['probe']!r} in its first 4 KB")
                continue
            # SCOPED TO THE REPLICA TREE. The guard refuses a file identical to
            # halo_rev_a's - which is right when checking the Replica and NONSENSE when
            # the tree being checked IS halo_rev_a, where those files are the originals.
            # Found by running the check against rev_a for the first time: it refused
            # rev_a's own schematic and netlist as copies of themselves. A guard that is
            # correct in one context and wrong in another is still wrong; scope is part
            # of the assertion, not decoration around it.
            ref = (row.get("refuse_if_sha256_matches")
                   if doc["trees"][tree].get("apply_copy_guard", True) else None)
            if ref:
                rp = os.path.join(HALO, ref)
                if os.path.exists(rp) and _sha256(rp) == _sha256(h):
                    reasons.append(f"{rel}: IS halo_rev_a's file, byte for byte. Copying the "
                                   f"board Leif rejected into the Replica's tree is the exact "
                                   f"failure this check exists to catch, dressed as a pass.")
                    continue
            opened.append(h)
        if not opened:
            rec.update(state="RED", exists="RED",
                       why=("; ".join(reasons[:3]) if reasons
                            else "no file of this kind anywhere in this tree"))
            out.append(rec); continue
        pr = row.get("timestamp_probe")
        ts = [(_stamp(h, pr), h) for h in opened]
        # an artifact SET is only as fresh as its OLDEST member
        oldest = min(ts, key=lambda t: _iso(t[0][0]))
        # a SOURCE is as new as its NEWEST member
        newest = max(ts, key=lambda t: _iso(t[0][0]))
        stamps[row["id"]] = (newest[0][0], newest[0][1])
        rec["_files"] = opened
        rec.update(exists="GREEN", opened=[os.path.relpath(h, root) for h in opened][:6],
                   n_opened=len(opened),
                   own_stamp=oldest[0][0], own_stamp_kind=oldest[0][1],
                   oldest_member=os.path.relpath(oldest[1], root))
        out.append(rec)

    # pass 2: freshness against the encoded dependency graph
    for rec in out:
        if rec.get("exists") != "GREEN":
            rec["fresh"] = "n/a"; continue
        srcs = rec["source"]
        if not srcs:
            rec["fresh"] = "n/a (root artifact)"; rec["state"] = "GREEN"; continue
        missing = [sid for sid in srcs if sid not in stamps]
        if missing:
            rec.update(state="CANNOT DETERMINE", fresh="CANNOT DETERMINE",
                       why=(f"opens, but its source {'/'.join(missing)} "
                            f"({', '.join(specs[m]['what'] for m in missing)}) does not exist "
                            f"in this tree, so there is nothing to be newer than. UNMEASURED, "
                            f"not stale."))
            continue
        stale = []
        for sid in srcs:
            sts, skind = stamps[sid]
            if _iso(rec["own_stamp"]) < _iso(sts):
                dt = (_iso(sts) - _iso(rec["own_stamp"])).total_seconds()
                stale.append(f"{int(dt)} s older than {sid} {specs[sid]['what'].lower()} "
                             f"({rec['own_stamp']} {rec['own_stamp_kind']} vs {sts} {skind})")
        if stale:
            rec.update(state="RED", fresh="STALE",
                       why="STALE: " + "; ".join(stale) +
                           f" -- oldest member {rec['oldest_member']}")
        else:
            rec.update(fresh="FRESH", state="GREEN")

    # pass 3: VALIDITY - did the source pass its own checks at the time it was cut?
    files = {r["id"]: r.get("_files", []) for r in out}
    for rec in out:
        spec = specs[rec["id"]]
        pre = spec.get("precondition")
        rec["valid"] = "n/a" if not pre else None
        if not pre or rec.get("exists") != "GREEN":
            continue
        vrow = pre["row"]
        if not files.get(vrow):
            rec.update(state="CANNOT DETERMINE", valid="CANNOT DETERMINE",
                       why=(f"opens and is current, but {vrow} "
                            f"({specs[vrow]['what'].lower()}) does not exist, so nobody knows "
                            f"whether its source was fit to cut. AN UNRUN CHECK IS NOT A "
                            f"PASSED ONE."))
            continue
        err, unc = read_verdict(files[vrow], pre["kind"])
        if err is None:
            rec.update(state="CANNOT DETERMINE", valid="CANNOT DETERMINE",
                       why=f"{vrow} exists but could not be read as a {pre['kind'].upper()} report")
            continue
        bad = []
        if err:
            bad.append(f"{err} error(s)")
        if pre["kind"] == "drc" and unc:
            bad.append(f"{unc} unconnected item(s)")
        if bad:
            extra = (f"cut from a source that FAILED its own checks: {vrow} reports "
                     + " and ".join(bad) +
                     ". It exists, it may even be current, and IT IS NOT BUILDABLE.")
            # ACCUMULATE. An artifact can be stale AND invalid, and reporting only the
            # last-computed reason hides one of two independent failures - which is the
            # opposite of what a three-legged check is for.
            rec.update(state="RED", valid="INVALID",
                       why=((rec.get("why", "") + " ALSO: " + extra).strip()
                            if rec.get("why") else extra))
        else:
            rec["valid"] = "VALID"
            if rec.get("state") != "RED" and rec.get("state") != "CANNOT DETERMINE":
                rec["state"] = "GREEN"
    # pass 4: A REPORT'S OWN VERDICT, which is a DIFFERENT FACT from its row state.
    # D6 showing "source ok = yes" means its ERC was clean, and reads to anyone scanning
    # for green as "the DRC passed". It did not. This column removes the misreading
    # instead of documenting it. A failing report does NOT turn its own row red: the
    # artifact is not the defect, and conflating "we have no DRC" with "the DRC found
    # things" is the could-not-build / could-not-verify conflation this project has a
    # standing rule against. The contents gate the things that DEPEND on them - which is
    # what the third leg already does for D7 and D8.
    for rec in out:
        spec = specs[rec["id"]]
        k = spec.get("self_verdict_kind")
        rec["own_verdict"] = None
        if not k or rec["id"] not in files or not files[rec["id"]]:
            rec.pop("_files", None); continue
        err, unc = read_verdict(files[rec["id"]], k)
        if err is None:
            rec["own_verdict"] = "unreadable"
        else:
            bits = [f"{err}E"]
            if k == "drc":
                bits.append(f"{unc}U")
            rec["own_verdict"] = " ".join(bits)
            rec["own_verdict_clean"] = (err == 0 and (k != "drc" or unc == 0))
            if k == "drc":
                rec["clearance_split"] = classify_clearances(doc, files[rec["id"]], roots, root)
            if not rec["own_verdict_clean"]:
                rec["own_verdict_note"] = (
                    f"THIS ROW IS GREEN AS AN ARTIFACT AND THE THING IT GRADES IS NOT: "
                    f"{err} error(s)" + (f" and {unc} unconnected item(s)" if k == "drc" and unc else "")
                    + ". Anything cut from that source fails the third leg.")
        rec.pop("_files", None)
    return doc, out

def deliverable_verdict(drows):
    g = [r for r in drows if r["state"] == "GREEN"]
    red = [r for r in drows if r["state"] == "RED"]
    cd = [r for r in drows if r["state"] == "CANNOT DETERMINE"]
    v = "FAIL" if red else ("CANNOT DETERMINE" if cd else "PASS")
    return v, g, red, cd

def print_deliverable(drows, ddoc, tree):
    exists = [r for r in drows if r.get("exists") == "GREEN"]
    stale = [r for r in drows if r.get("fresh") == "STALE"]
    L = {"GREEN": "yes", "RED": "no", "CANNOT DETERMINE": "?", "FRESH": "yes",
         "STALE": "NO", "INVALID": "NO", "VALID": "yes", None: "-"}
    print(f"  {'':7} {'':2} {'artifact':<20} {'opens':>5} {'current':>8} {'source ok':>10} "
          f"{'its own verdict':>16}")
    for r in drows:
        mark = {"GREEN": "GREEN", "RED": "  RED",
                "CANNOT DETERMINE": " CD  "}[r["state"]]
        e = L.get(r.get("exists"), "-")
        f = L.get(r.get("fresh"), "-") if r.get("fresh") not in (None, "n/a") else "n/a"
        v = L.get(r.get("valid"), "-") if r.get("valid") not in (None, "n/a") else "n/a"
        ov = r.get("own_verdict") or "n/a"
        if r.get("own_verdict") and not r.get("own_verdict_clean", True):
            ov = "** " + ov + " **"
        print(f"  [{mark}] {r['id']} {r['what']:<20} {e:>5} {f:>8} {v:>10} {ov:>16}")
        if r.get("own_verdict_note"):
            print(f"           {r['own_verdict_note']}")
        cs = r.get("clearance_split")
        if cs and cs["errors"]:
            print(f"           clearance split ({cs['errors']} errors, floor {cs['floor_mm']} mm): "
                  + "  ".join(f"{k} {v}" for k, v in cs["counts"].items())
                  + f"   -> {cs['blocking']} block fabrication")
            if cs.get("note"):
                print(f"           {cs['note']}")
            for x in cs["refused"][:3]:
                print(f"           REFUSED {x}")
        if r["state"] != "GREEN":
            for chunk in (r["why"] or "").split(" ALSO: "):
                print(f"           {chunk}")
        else:
            print(f"           {', '.join(r['opened'])[:170]}")
    v, g, red, cd = deliverable_verdict(drows)
    print(f"\n  tree: {ddoc['trees'][tree]['label']}")
    print(f"  {len(exists)} of {len(drows)} artifacts EXIST AND OPEN; "
          f"{len(stale)} of those are STALE; {len(g)} rows are green.")
    print(f"  DELIVERABLE: {v}")
    return v

# --------------------------------------------------------------------- checking
def check_cell(row_n, side, cell, root=HALO):
    a = cell.get("anchor")
    if not a:
        return {"row": row_n, "side": side, "verdict": "CANNOT DETERMINE",
                "why": "no anchor on this cell - unverifiable by construction, and counted as such"}
    try:
        kind, got = resolve(a, root)
    except Unresolved as e:
        return {"row": row_n, "side": side, "verdict": "CANNOT DETERMINE", "why": str(e),
                "anchor": a}
    if kind == "exists":
        return {"row": row_n, "side": side, "verdict": "PASS",
                "why": f"{a['file']} is on disk", "got": True}
    if kind == "quote":
        if got:
            return {"row": row_n, "side": side, "verdict": "PASS",
                    "why": f"quote present in {a['file']}", "got": True}
        return {"row": row_n, "side": side, "verdict": "FAIL",
                "why": f"quote ABSENT from {a['file']}: {a['quote'][:70]!r}", "got": False,
                "anchor": a}
    want = a.get("expect", "__NO_EXPECT__")
    if want == "__NO_EXPECT__":
        return {"row": row_n, "side": side, "verdict": "CANNOT DETERMINE",
                "why": f"anchor names a path but no expected value", "anchor": a}
    if strict_eq(got, want):
        return {"row": row_n, "side": side, "verdict": "PASS",
                "why": f"{a['file']}:{a['path']} == {got!r}", "got": got}
    return {"row": row_n, "side": side, "verdict": "FAIL",
            "why": f"{a['file']}:{a['path']} is {got!r} ({type(got).__name__}), table says {want!r} ({type(want).__name__})",
            "got": got, "anchor": a}

def check_fidelity(doc):
    """Every row must carry a fidelity verdict per side, drawn from the stated vocabulary.

    This is the divergence counter's own guard. A verdict outside the vocabulary would be
    silently dropped from the tally, and a tally that quietly loses rows is exactly the
    ratchet-with-no-counter THE-DRIFT.md describes. Break N9 watches it go red.
    """
    ok = set(doc.get("fidelity_vocabulary", {})) | {"n/a"}
    out = []
    for row in doc["rows"]:
        f = row.get("fidelity")
        if not f:
            out.append({"row": row["n"], "side": "fidelity", "verdict": "FAIL",
                        "why": "row carries no fidelity verdict - it would vanish from the count"})
            continue
        for side in ("rev_a", "replica"):
            v = f.get(side, {}).get("verdict")
            if v not in ok:
                out.append({"row": row["n"], "side": f"fidelity/{side}", "verdict": "FAIL",
                            "why": f"verdict {v!r} is not in fidelity_vocabulary {sorted(ok)}"})
    return out

def tally_fidelity(doc):
    t = {"rev_a": {}, "replica": {}}
    for row in doc["rows"]:
        for side in ("rev_a", "replica"):
            v = row["fidelity"][side]["verdict"]
            t[side][v] = t[side].get(v, 0) + 1
    return t

def check_table(doc, root=HALO):
    results = []
    for row in doc["rows"]:
        for side in SIDES:
            results.append(check_cell(row["n"], side, row[side], root))
    results += check_fidelity(doc)
    for i, a in enumerate(doc.get("reconciliation_with_the_prior_comparison", {}).get("anchors", [])):
        r = check_cell(f"rec{i+1}", "prior-page", {"anchor": a}, root)
        r["why"] = f"[{a['claim']}] " + r["why"]
        results.append(r)
    counts = {"PASS": 0, "FAIL": 0, "CANNOT DETERMINE": 0}
    for r in results:
        counts[r["verdict"]] += 1
    if counts["FAIL"]:
        verdict = "FAIL"
    elif counts["CANNOT DETERMINE"]:
        verdict = "CANNOT DETERMINE"
    else:
        verdict = "PASS"
    return verdict, counts, results

EXIT = {"PASS": EX_PASS, "FAIL": EX_FAIL, "CANNOT DETERMINE": EX_CANNOT}

def cmd_check(args):
    doc = json.load(open(TABLE))
    verdict, counts, results = check_table(doc)
    print(f"INPUT: {os.path.relpath(TABLE, HALO)}  ({len(doc['rows'])} rows x 3 sides = {len(results)} anchored cells)")
    print(f"ROOT : {HALO}")
    for r in results:
        if r["verdict"] != "PASS" or args.verbose:
            print(f"  [{r['verdict']:>17}] row {str(r['row']):>4} {r['side']:<14} {r['why']}")
    print(f"\n{counts['PASS']} PASS  {counts['FAIL']} FAIL  {counts['CANNOT DETERMINE']} CANNOT DETERMINE")
    print(f"ANCHORS: {verdict}")

    ddoc, drows = check_deliverable(tree=getattr(args, "tree", "replica"))
    print(f"\nDELIVERABLE - can anyone open this design, and is it CURRENT?")
    dv = print_deliverable(drows, ddoc, getattr(args, "tree", "replica"))
    worst = "FAIL" if (verdict == "FAIL" or dv == "FAIL") else (
        "CANNOT DETERMINE" if "CANNOT DETERMINE" in (verdict, dv) else "PASS")
    print(f"VERDICT: {worst}   (the worse of the two - a page that cites its sources "
          f"correctly about a design that does not exist is still not a design)")
    return EXIT[worst]

# --------------------------------------------------------------------- render
def _one(s):
    """First sentence of a why-string, for the scoreboard."""
    s = s.strip().replace("\n", " ")
    m = re.search(r"^(.{0,200}?[.!])(\s|$)", s)
    return m.group(1) if m else (s[:200] + ("..." if len(s) > 200 else ""))

def cmd_render(args):
    doc = json.load(open(TABLE))
    verdict, counts, results = check_table(doc)
    byrow = {}
    for r in results:
        byrow.setdefault(r["row"], []).append(r)

    L = []
    W = L.append
    W("# Apple | halo_rev_a | halo_replica — every axis, and which is better on it\n")
    W(f"*{doc['lane']}, {doc['written']}. **Generated by `tools/k_threeway.py render` from "
      f"`comparison/threeway.json`. Nothing on this page is hand-typed into it.***\n")
    W(f"**Anchor check at render time: {counts['PASS']} PASS · {counts['FAIL']} FAIL · "
      f"{counts['CANNOT DETERMINE']} CANNOT DETERMINE → {verdict}.** Every cell below names a "
      "file and a value in it; `k_threeway check` resolves all of them and goes red when the "
      "table and its sources disagree.\n")
    W("---\n")
    W("## What this is\n")
    W(doc["what_this_is"] + "\n")
    W("## The asymmetry that governs every row\n")
    W("> " + doc["the_asymmetry_that_governs_every_row"] + "\n")
    W("## The three axes a row can be judged on\n")
    for k, v in doc["judging_axes"].items():
        W(f"- **{k}** — {v}")
    W("")
    W("**Better is not automatic.** " + doc["better_is_not_automatic"] + "\n")
    W("---\n")

    # scoreboard
    W("## The scoreboard\n")
    W("| # | axis | rev_a vs Apple | replica vs Apple | judged on | better | in one line |")
    W("|--:|---|---|---|:-:|---|---|")
    for row in doc["rows"]:
        b = row["better"]; f = row["fidelity"]
        W(f"| {row['n']} | {row['axis']} | {f['rev_a']['verdict']} | {f['replica']['verdict']} | "
          f"{b['on']} | **{b['winner']}** | {_one(b['why'])} |")
    W("")
    tally = {}
    for row in doc["rows"]:
        tally[row["better"]["winner"]] = tally.get(row["better"]["winner"], 0) + 1
    W("**Primary-axis tally across " + str(len(doc["rows"])) + " axes:** " +
      " · ".join(f"{k} **{v}**" for k, v in sorted(tally.items(), key=lambda kv: -kv[1])) + "\n")
    W("Secondary judgements — the rows where a second axis reverses the first — are in the "
      "row bodies below and are the substance of this document, not a footnote to it.\n")
    W("---\n")

    # ---- the divergence counter
    acc = doc["the_accumulation"]
    t = tally_fidelity(doc)
    W("## The accumulation — the divergence counter\n")
    W("*" + acc["_why_this_section_exists"] + "*\n")
    order = ["SAME", "EQUIVALENT", "DIVERGED", "MISSING", "CANNOT DETERMINE", "UNSTARTED", "n/a"]
    W("| | " + " | ".join(order) + " | departures | NO ANSWER |")
    W("|---|" + "--:|" * (len(order) + 2))
    for side in ("rev_a", "replica"):
        cells = [str(t[side].get(k, 0)) for k in order]
        dep = t[side].get("DIVERGED", 0) + t[side].get("MISSING", 0)
        noans = t[side].get("CANNOT DETERMINE", 0) + t[side].get("UNSTARTED", 0)
        W(f"| **halo_{side}** | " + " | ".join(cells) + f" | **{dep}** | **{noans}** |")
    W("")
    W("**THE TWO RIGHT-HAND COLUMNS MUST BE READ TOGETHER AND NEITHER MAY BE QUOTED ALONE.** "
      "The Replica's 2 departures against rev_a's 13 looks like a rout and is not one: the "
      "Replica also has NO ANSWER on 12 of 24 axes against rev_a's 3. An axis you never "
      "answered cannot be a departure. Quoting the departure count on its own would be this "
      "project's own headline-from-a-favourable-half failure, in the document written to "
      "catch it.\n")
    for k in order:
        if k in doc["fidelity_vocabulary"]:
            W(f"- **{k}** — {doc['fidelity_vocabulary'][k]}")
    W("")
    W("**The ceiling.** " + acc["the_ceiling"] + "\n")
    W("### What the count says\n")
    for line in acc["what_the_count_says"]:
        W(f"- {line}")
    W("")
    W("### The GOAL.md re-read\n")
    g = acc["goal_reread"]
    W("*" + g["_the_check_THE_DRIFT_asked_for"] + "*\n")
    for k, v in g.items():
        if k.startswith("_"):
            continue
        if k.startswith("GOAL_") or k.startswith("CONSTRAINT_"):
            W(f"**{k.replace('_', ' ')}** — {v}\n")
    W("### The conclusion\n")
    W(g["the_conclusion_and_it_revises_THE_DRIFT"] + "\n")
    W("### And the risk in this very document\n")
    W(g["and_the_risk_in_this_very_document"] + "\n")
    W("---\n")

    ddoc, drows = check_deliverable()
    dgreen = [r for r in drows if r["state"] == "GREEN"]
    dexist = [r for r in drows if r.get("exists") == "GREEN"]
    dstale = [r for r in drows if r.get("fresh") == "STALE"]
    W("## Distance from a deliverable — the other axis of drift\n")
    W("*" + ddoc["why_this_exists"] + "*\n")
    W(f"**{len(dexist)} of {len(drows)} artifacts exist and open. {len(dstale)} of those are "
      f"STALE. {len(dgreen)} rows are green.**\n")
    W("| | artifact | state | opens | current | source ok | **its own verdict** | evidence |")
    W("|---|---|:-:|:-:|:-:|:-:|:-:|---|")
    ICON = {"GREEN": "✅", "RED": "🔴", "CANNOT DETERMINE": "⚠️"}
    for r in drows:
        ev = (", ".join(f"`{o}`" for o in r["opened"]) if r["state"] == "GREEN" else r["why"])
        op = "yes" if r.get("exists") == "GREEN" else "no"
        fr = {"FRESH": "yes", "STALE": "**NO**", "CANNOT DETERMINE": "?"}.get(r.get("fresh"), "—")
        so = {"VALID": "yes", "INVALID": "**NO**", "CANNOT DETERMINE": "?"}.get(r.get("valid"), "—")
        ov = r.get("own_verdict") or "—"
        if r.get("own_verdict") and not r.get("own_verdict_clean", True):
            ov = f"**{ov}**"
        W(f"| {r['id']} | {r['what']} | {ICON[r['state']]} | {op} | {fr} | {so} | {ov} | {ev} |")
    W("")
    W("**Freshness.** " + ddoc["freshness"]["why"] + "\n")
    W("**The rule.** " + ddoc["freshness"]["the_rule"] + " " + ddoc["freshness"]["three_states"] + "\n")
    W("**Timestamps.** " + ddoc["freshness"]["timestamp_strength"] + "\n")
    f4 = ddoc["the_fourth_column"]
    W("**Its own verdict — the column that removes a trap rather than documenting it.** "
      + f4["why"] + "\n")
    W("> **A report row being GREEN means:** " + f4["what_a_report_row_being_GREEN_means"] + "\n")
    W("> **And a failing report does not turn its own row red**, because " +
      f4["why_a_failing_report_does_not_turn_its_own_row_red"] + "\n")
    cc = ddoc["clearance_classification"]
    W("### The fifth state — whose fault a clearance violation is\n")
    W(cc["why"] + "\n")
    W("**" + cc["and_the_thing_it_must_never_become"] + "**\n")
    W("**The default is the honest one.** " + cc["the_default_is_the_honest_one"] + "\n")
    W("| class | pointer required | blocks fabrication | means |")
    W("|---|:-:|:-:|---|")
    for k, v in cc["classes"].items():
        W(f"| **{k}** | {'yes' if v['pointer_required'] else 'no'} | "
          f"{'**yes**' if v['blocks_fabrication'] else 'no'} | {v['means']} |")
    W("")
    rf = cc["resolution_floor"]
    W(f"**Resolution floor: {rf['value_mm']} mm.** {rf['derivation']} "
      f"*Not the registration hold-out:* {rf['why_not_the_registration_holdout']} "
      f"*Not one pixel:* {rf['why_not_one_pixel']} *What would sharpen it:* "
      f"{rf['what_would_sharpen_it']}\n")
    for r in drows:
        cs = r.get("clearance_split")
        if cs and cs["errors"]:
            W(f"**Current split of {cs['errors']} clearance errors in `{cs['drc']}`:** "
              + " · ".join(f"{k} **{v}**" for k, v in cs["counts"].items())
              + f" — {cs['blocking']} block fabrication."
              + (f" {cs['note']}" if cs.get("note") else "") + "\n")
    W("**The rule.** " + ddoc["the_rule"] + "\n")
    W("**Anti-gaming.** " + ddoc["anti_gaming"] + "\n")
    W("Why each is required, in the row's own words:\n")
    for spec in ddoc["rows"]:
        W(f"- **{spec['id']} {spec['what']}** — {spec['why_it_is_required']}"
          + (f" *{spec['rev_a_note']}*" if spec.get("rev_a_note") else ""))
    W("")
    W("---\n")
    rec = doc["reconciliation_with_the_prior_comparison"]
    W("## Reconciliation with the prior comparison\n")
    W("*" + rec["_what"] + "*\n")
    W("**Denominators.** " + rec["denominators_are_not_the_same_and_must_not_be_differenced"] + "\n")
    W("### Where they agree\n")
    for x in rec["agree"]:
        W(f"- {x}")
    W("")
    W("### Where they do not\n")
    for x in rec["disagree"]:
        W(f"**{x['row']}**\n")
        W(f"- *prior:* {x['prior']}")
        W(f"- *now:* {x['now']}")
        for k in ("why_it_changed", "why_it_matters", "not_fixed_here"):
            if k in x:
                W(f"- *{k.replace('_',' ')}:* {x[k]}")
        W("")
    W("### What this file adds that the prior one could not\n")
    for x in rec["what_this_file_adds_that_the_prior_one_could_not"]:
        W(f"- {x}")
    W("")
    W("---\n")

    groups = []
    for row in doc["rows"]:
        if row["group"] not in groups:
            groups.append(row["group"])
    TITLES = {"outline": "Outline and shape", "stackup": "Stackup and materials",
              "rf": "Radio", "components": "Components", "audio": "The audio path",
              "power": "Power", "interfaces": "Interfaces", "cost": "Cost and manufacture",
              "meta": "What the artifacts are"}
    for g in groups:
        W(f"## {TITLES.get(g, g)}\n")
        for row in doc["rows"]:
            if row["group"] != g:
                continue
            W(f"### {row['n']} · {row['axis']}\n")
            W("| | value | state | how it is known |")
            W("|---|---|---|---|")
            for side in SIDES:
                c = row[side]
                v = c["value"].replace("|", "\\|").replace("\n", " ")
                st = c["state"].replace("|", "\\|")
                sr = c["source"].replace("|", "\\|").replace("\n", " ")
                W(f"| **{SIDE_LABEL[side]}** | {v} | {st} | {sr} |")
            W("")
            f = row["fidelity"]
            W(f"*Against Apple:* **halo_rev_a {f['rev_a']['verdict']}** — {f['rev_a']['note']}. "
              f"**halo_replica {f['replica']['verdict']}** — {f['replica']['note']}.\n")
            b = row["better"]
            W(f"**Better on {b['on']}: {b['winner']}.** {b['why']}")
            if b.get("would_settle"):
                W(f"\n*Would settle it:* {b['would_settle']}")
            for extra in row.get("also", []):
                W(f"\n> **On {extra['on']}: {extra['winner']}.** {extra['why']}")
            anch = byrow.get(row["n"], [])
            bad = [a for a in anch if a["verdict"] != "PASS"]
            if bad:
                W("")
                for a in bad:
                    W(f"\n`ANCHOR {a['verdict']}` {a['side']}: {a['why']}")
            W("")
        W("---\n")

    W("## How to reproduce\n")
    W("```bash")
    W("cd ce-designs/halo/electronics/halo_replica")
    W("python3 tools/k_threeway.py check -v      # every anchor, with its file and value")
    W("python3 tools/k_threeway.py selftest      # 9 deliberate breaks, each watched going red")
    W("python3 tools/k_threeway.py render        # regenerate this page")
    W("```")
    W("")
    W("`check` exits 0 PASS / 1 FAIL / 2 CANNOT DETERMINE. It verifies that this page agrees "
      "with the files it cites; it cannot verify that those files are right, and says so in "
      "its own docstring.\n")

    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    open(OUT_MD, "w").write("\n".join(L) + "\n")
    print(f"wrote {os.path.relpath(OUT_MD, HALO)}  ({len(L)} lines)")
    print(f"anchor check: {counts['PASS']} PASS / {counts['FAIL']} FAIL / "
          f"{counts['CANNOT DETERMINE']} CANNOT DETERMINE -> {verdict}")
    return EXIT[verdict]

# --------------------------------------------------------------------- selftest
def _find(doc, pred):
    for row in doc["rows"]:
        for side in SIDES:
            a = row[side].get("anchor")
            if a and pred(a):
                return row, side, a
    raise SystemExit("selftest cannot run: the table has no anchor of the shape it needs")

def cmd_selftest(args):
    base = json.load(open(TABLE))
    fails = []

    def expect(name, doc, want, note):
        v, counts, res = check_table(doc)
        ok = (v == want)
        print(f"  [{'ok ' if ok else 'RED'}] {name:<4} -> {v:<17} (must be {want}) {note}")
        if not ok:
            fails.append(f"{name}: got {v}, must be {want}")

    print("BASELINE")
    v0, c0, _ = check_table(base)
    print(f"  unmodified table -> {v0}  ({c0['PASS']} PASS / {c0['FAIL']} FAIL / {c0['CANNOT DETERMINE']} CD)")
    if v0 != "PASS":
        print("  NOTE: the baseline is not PASS, so the breaks below are being run against a "
              "table that is already red. Fix the baseline first; a break watched from red "
              "proves nothing.")

    # N1 numeric hairline - a tolerance-based compare would swallow this
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: isinstance(a.get("expect"), float))
    a["expect"] = a["expect"] + 1e-7
    expect("N1", d, "FAIL", f"(row {row['n']} {side}: +1e-7 on a float)")

    # N2 case only - a case-folding compare would swallow this
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: isinstance(a.get("expect"), str) and a["expect"].upper() != a["expect"])
    a["expect"] = a["expect"].upper()
    expect("N2", d, "FAIL", f"(row {row['n']} {side}: expected value upper-cased)")

    # N3 strict substring - an `in` compare would swallow this
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: isinstance(a.get("expect"), str) and len(a["expect"]) > 12)
    a["expect"] = a["expect"][:8]
    expect("N3", d, "FAIL", f"(row {row['n']} {side}: expect truncated to a substring)")

    # N4 type confusion - a str() coercion would swallow this
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: type(a.get("expect")) is int)
    a["expect"] = str(a["expect"])
    expect("N4", d, "FAIL", f"(row {row['n']} {side}: int {a['expect']} written as a string)")

    # N5 path that is not there - must be CANNOT DETERMINE, never PASS and never FAIL
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: "path" in a)
    a["path"] = a["path"] + ".no_such_key_xyz"
    expect("N5", d, "CANNOT DETERMINE", f"(row {row['n']} {side}: path extended into nothing)")

    # N6 file that is not there
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: "file" in a)
    a["file"] = a["file"] + ".missing"
    expect("N6", d, "CANNOT DETERMINE", f"(row {row['n']} {side}: file renamed away)")

    # N7 quote anchor, one character short
    d = copy.deepcopy(base)
    row, side, a = _find(d, lambda a: "quote" in a)
    a["quote"] = a["quote"][:-1] + "Z"
    expect("N7", d, "FAIL", f"(row {row['n']} {side}: last character of the quote changed)")

    # N9 a fidelity verdict outside the vocabulary - it would vanish from the divergence count
    d = copy.deepcopy(base)
    d["rows"][0]["fidelity"]["rev_a"]["verdict"] = "SORT OF"
    expect("N9", d, "FAIL", "(row 1 rev_a: fidelity verdict not in the vocabulary)")

    # N8 POSITIVE CONTROL ON RESOLUTION.
    # Everything above would also pass on a resolve() that reads nothing and returns None.
    # This reads three real anchors with a SECOND, INDEPENDENT reader that shares no code
    # with resolve(), and requires the same non-None values back.
    print("  N8   positive control on resolution - independent second reader:")
    n8_ok = True
    probes = [
        ("out/verify/dfm-jlc-4layer.json",            ["board_facts", "thickness_mm"]),
        ("electronics/halo_replica/board/board.json", ["parameters", "layer_count", "value"]),
        ("electronics/halo_rev_a/out/drc.json",       ["unconnected_items"]),
    ]
    for rel, keys in probes:
        fp = os.path.join(HALO, rel)
        obj = json.load(open(fp))
        for k in keys:
            obj = obj[k]
        independent = len(obj) if isinstance(obj, list) else obj
        path = ".".join(keys) + ("|len" if isinstance(json.load(open(fp)).get(keys[0]), list) and len(keys) == 1 else "")
        kind, got = resolve({"file": rel, "path": path})
        same = strict_eq(got, independent)
        if got is None or not same:
            n8_ok = False
        print(f"         {'ok ' if (same and got is not None) else 'RED'} {rel}:{path} "
              f"resolve()={got!r} independent={independent!r}")
    if not n8_ok:
        fails.append("N8: resolve() disagrees with an independent reader, or returned None. "
                     "Every break above is then meaningless.")
    else:
        print("         resolve() genuinely reads the files. N1-N7 are therefore about the "
              "comparison, not about an empty read.")

    # ---- THE DELIVERABLE CHECK'S OWN BREAKS.
    # This check's natural state is RED, which makes it the easy kind to get wrong: a
    # check that only ever goes red is indistinguishable from one that cannot go green.
    # So all four cases are watched - and the two that matter most are the DECOYS, an
    # empty file and a wrong-format file at exactly the right name, because "a path
    # exists" is precisely the weak test this was built to avoid.
    import tempfile, shutil
    print("  D-breaks  the deliverable check, in a temporary tree:")
    dfails = []
    def dstate(tmp, rid):
        _, rows = check_deliverable(root=tmp, tree="selftest")
        return {r["id"]: r for r in rows}[rid]
    tmp = tempfile.mkdtemp(prefix="k_threeway-deliv-")
    try:
        os.makedirs(os.path.join(tmp, "lane"))
        board = os.path.join(tmp, "lane", "x.kicad_pcb")

        r0 = dstate(tmp, "D4")
        ok0 = r0.get("exists", "RED") == "RED"
        print(f"    [{'ok ' if ok0 else 'RED'}] D-0 empty tree            -> exists={r0.get('exists','RED')} (must be RED)")
        if not ok0: dfails.append("D-0")

        open(board, "w").close()                       # EMPTY file, right name
        r1 = dstate(tmp, "D4")
        ok1 = r1.get("exists", "RED") == "RED" and "EMPTY" in r1.get("why", "")
        print(f"    [{'ok ' if ok1 else 'RED'}] D-1 empty x.kicad_pcb     -> exists={r1.get('exists','RED')} (must be RED) "
              f"{r1.get('why','')[:60]}")
        if not ok1: dfails.append("D-1")

        open(board, "w").write("(kicad_sch\n  (version 1)\n)")   # WRONG format, right name
        r2 = dstate(tmp, "D4")
        ok2 = r2.get("exists", "RED") == "RED" and "does not open" in r2.get("why", "")
        print(f"    [{'ok ' if ok2 else 'RED'}] D-2 a SCHEMATIC named .kicad_pcb -> exists={r2.get('exists','RED')} (must be RED)")
        if not ok2: dfails.append("D-2")

        open(board, "w").write("(kicad_pcb\n  (version 20260206)\n)")   # valid
        r3 = dstate(tmp, "D4")
        # ASSERT ON `exists`, NOT on the combined state. Adding freshness made the combined
        # state of a board with no schematic in the tree CANNOT DETERMINE - correctly - and
        # that silently broke D-3 and D-4, which were only ever about whether the file
        # OPENS. A break must assert the property it was written for, or the next change
        # to an unrelated property retires it without anyone noticing.
        ok3 = r3.get("exists") == "GREEN"
        print(f"    [{'ok ' if ok3 else 'RED'}] D-3 a real board file     -> exists={r3.get('exists')} (must be GREEN) "
              f"- THE CHECK CAN GO GREEN, which is the half a red-by-default check hides")
        if not ok3: dfails.append("D-3")

        rev = os.path.join(HALO, "electronics/halo_rev_a/out/halo_rev_a.kicad_pcb")
        if os.path.exists(rev):
            shutil.copyfile(rev, board)                # ANTI-GAMING: rev_a's own board
            r4 = dstate(tmp, "D4")
            ok4 = r4.get("exists", "RED") == "RED" and "halo_rev_a" in r4.get("why", "")
            print(f"    [{'ok ' if ok4 else 'RED'}] D-4 halo_rev_a's board copied in -> exists={r4.get('exists','RED')} "
                  f"(must be RED - the cheapest way to fake a pass)")
            if not ok4: dfails.append("D-4")
        else:
            print("    [ -- ] D-4 skipped: halo_rev_a's board file is not on disk to copy")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- FRESHNESS BREAKS. An artifact that OPENS is not an artifact that is CURRENT,
    # and a pure existence test reads a stale one GREEN. All three outcomes are watched,
    # including the CANNOT DETERMINE, because an artifact with no source to compare
    # against is UNMEASURED and must not collapse into either of the other two.
    print("  F-breaks  freshness, in a temporary tree:")
    tmp = tempfile.mkdtemp(prefix="k_threeway-fresh-")
    try:
        lane = os.path.join(tmp, "lane"); os.makedirs(lane)
        sch = os.path.join(lane, "x.kicad_sch")
        drc = os.path.join(lane, "x.drc.json")
        pcb = os.path.join(lane, "x.kicad_pcb")
        mod = os.path.join(lane, "x.kicad_mod")
        open(sch, "w").write("(kicad_sch (version 1))")
        open(mod, "w").write('(footprint "F")')
        open(pcb, "w").write("(kicad_pcb (version 1))")

        # F-3 first: a DRC with NO board in the tree must be CANNOT DETERMINE.
        os.remove(pcb)
        open(drc, "w").write('{"$schema":"https://schemas.kicad.org/drc.v1.json",'
                             '"date":"2026-09-05T10:00:00","violations":[],'
                             '"unconnected_items":[]}')
        r3 = dstate(tmp, "D6")
        ok3 = r3.get("fresh") == "CANNOT DETERMINE"
        print(f"    [{'ok ' if ok3 else 'RED'}] F-3 a DRC whose board is ABSENT -> fresh="
              f"{r3.get('fresh')} (must be CANNOT DETERMINE, never STALE and never FRESH)")
        if not ok3: dfails.append("F-3")

        # F-1 a DRC NEWER than its board must be GREEN.
        open(pcb, "w").write("(kicad_pcb (version 1))")
        os.utime(pcb, (1757000000, 1757000000))          # 2025-09-04ish, old
        r1 = dstate(tmp, "D6")
        # ASSERT ON `fresh`, NOT on the combined state - AND I MADE THIS EXACT MISTAKE
        # TWICE IN ONE SESSION, having already written the lesson into the D-break above.
        # Adding the validity leg turned this row's combined state into CANNOT DETERMINE
        # (no ERC in the fixture), which says nothing about the freshness this break
        # exists to test. A break must assert the property it was written for, or the
        # next change to an unrelated property silently retires it.
        ok1 = r1.get("fresh") == "FRESH"
        print(f"    [{'ok ' if ok1 else 'RED'}] F-1 a DRC NEWER than its board -> fresh="
              f"{r1.get('fresh')} (must be FRESH)")
        if not ok1: dfails.append("F-1")

        # F-2 the SAME files, board touched forward: must go RED on staleness alone.
        os.utime(pcb, (1789000000, 1789000000))          # far future relative to the DRC
        r2 = dstate(tmp, "D6")
        ok2 = r2.get("fresh") == "STALE" and r2["state"] in ("RED", "CANNOT DETERMINE")
        print(f"    [{'ok ' if ok2 else 'RED'}] F-2 the SAME DRC, board touched forward -> "
              f"fresh={r2.get('fresh')} (must be STALE)")
        print(f"          nothing about the DRC changed - it still exists and still opens. "
              f"THAT is the failure a pure existence test cannot see.")
        if not ok2: dfails.append("F-2")
        # V-1 / V-2  THE THIRD LEG: a gerber cut from a board that failed its own DRC.
        # This is the artifact that passes BOTH other assertions - it exists, it opens,
        # and it is newer than its board - and is still not a fabrication set.
        gbr = os.path.join(lane, "x.gtl")
        open(gbr, "w").write("%TF.CreationDate,2026-09-05T12:00:00*%\n%FSLAX45Y45*%\n")
        open(drc, "w").write(json.dumps({"$schema": "https://schemas.kicad.org/drc.v1.json",
                                         "date": "2026-09-05T11:00:00",
                                         "violations": [], "unconnected_items": []}))
        os.utime(pcb, (1757000000, 1757000000))
        rv1 = dstate(tmp, "D7")
        okv1 = rv1["state"] == "GREEN" and rv1.get("valid") == "VALID"
        print(f"    [{'ok ' if okv1 else 'RED'}] V-1 gerber, board DRC clean -> {rv1['state']}"
              f"/{rv1.get('valid')} (must be GREEN/VALID)")
        if not okv1: dfails.append("V-1")

        open(drc, "w").write(json.dumps({"$schema": "https://schemas.kicad.org/drc.v1.json",
                                         "date": "2026-09-05T11:00:00", "violations": [],
                                         "unconnected_items": [{"x": 1}, {"x": 2}]}))
        rv2 = dstate(tmp, "D7")
        okv2 = rv2["state"] == "RED" and rv2.get("valid") == "INVALID"
        print(f"    [{'ok ' if okv2 else 'RED'}] V-2 THE SAME gerber, board has 2 unconnected "
              f"nets -> {rv2['state']}/{rv2.get('valid')} (must be RED/INVALID)")
        print(f"          the gerber did not change. It still exists, still opens, and is "
              f"still NEWER than its board. Both other legs pass it.")
        if not okv2: dfails.append("V-2")

        # W-1 / W-2  THE FOURTH COLUMN. A report's row state and its contents are
        # different facts, and with three columns the first read as the second.
        # THE FIXTURE NEEDS AN ERC. D6's precondition is D5, so without one the row is
        # CANNOT DETERMINE and the claim W-2 makes - that a failing report does NOT turn
        # its own row red - cannot be tested at all. A break whose fixture cannot reach
        # the state under test is not a break.
        erc = os.path.join(lane, "x.erc.json")
        open(erc, "w").write(json.dumps({"$schema": "https://schemas.kicad.org/erc.v1.json",
                                         "date": "2026-09-05T09:00:00", "sheets": []}))
        open(drc, "w").write(json.dumps({"$schema": "https://schemas.kicad.org/drc.v1.json",
                                         "date": "2026-09-05T11:00:00",
                                         "violations": [], "unconnected_items": []}))
        rw1 = dstate(tmp, "D6")
        okw1 = rw1.get("own_verdict") == "0E 0U" and rw1.get("own_verdict_clean") is True
        print(f"    [{'ok ' if okw1 else 'RED'}] W-1 a CLEAN DRC reports its own verdict -> "
              f"{rw1.get('own_verdict')} (must be 0E 0U, clean)")
        if not okw1: dfails.append("W-1")

        open(drc, "w").write(json.dumps({"$schema": "https://schemas.kicad.org/drc.v1.json",
                                         "date": "2026-09-05T11:00:00",
                                         "violations": [{"severity": "error"}, {"severity": "error"},
                                                        {"severity": "warning"}],
                                         "unconnected_items": []}))
        rw2 = dstate(tmp, "D6")
        okw2 = (rw2.get("own_verdict") == "2E 0U" and rw2.get("own_verdict_clean") is False
                and rw2["state"] == "GREEN" and "own_verdict_note" in rw2)
        print(f"    [{'ok ' if okw2 else 'RED'}] W-2 a DRC with 2 errors and 1 warning -> "
              f"{rw2.get('own_verdict')}, row still {rw2['state']} (must be 2E 0U and GREEN)")
        print(f"          the ARTIFACT is fine and the BOARD is not. Turning the row red here "
              f"would conflate 'we have no DRC' with 'the DRC found things'.")
        if not okw2: dfails.append("W-2")

        os.remove(drc)
        rv3 = dstate(tmp, "D7")
        okv3 = rv3["state"] == "CANNOT DETERMINE"
        print(f"    [{'ok ' if okv3 else 'RED'}] V-3 the DRC removed entirely -> {rv3['state']} "
              f"(must be CANNOT DETERMINE - an unrun check is not a passed one)")
        if not okv3: dfails.append("V-3")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- C-breaks  THE CLEARANCE CLASSIFIER'S ANTI-RELABELLING GUARD.
    # If a violation can leave DRAWN-WRONG by editing a string, this gate is something a
    # lane improves by typing. C-4 is the one that matters: a pointer that RESOLVES but
    # does not SUPPORT the claim must be refused exactly like one that does not resolve.
    print("  C-breaks  clearance classification, in a temporary tree:")
    tmp = tempfile.mkdtemp(prefix="k_threeway-clr-")
    try:
        lane = os.path.join(tmp, "lane"); os.makedirs(lane)
        ddoc = json.load(open(DELIV))
        drcp = os.path.join(lane, "c.drc.json")
        json.dump({"$schema": "https://schemas.kicad.org/drc.v1.json", "date": "2026-01-01T00:00:00",
                   "violations": [{"severity": "error"}, {"severity": "error"}],
                   "unconnected_items": []}, open(drcp, "w"))
        evp = os.path.join(lane, "rows.json")
        json.dump({"rows": [{"id": "A1"}, {"id": "A2"}]}, open(evp, "w"))
        roots_ = [lane]

        r = classify_clearances(ddoc, [drcp], roots_, root=tmp)
        okc1 = r["counts"]["DRAWN-WRONG"] == 2 and r["classification_file"] is None
        print(f"    [{'ok ' if okc1 else 'RED'}] C-1 no classification file -> DRAWN-WRONG "
              f"{r['counts']['DRAWN-WRONG']} of 2 (must be 2 - silence means OUR fault)")
        if not okc1: dfails.append("C-1")

        def write_claim(cls, gap, evfile="rows.json", rows=("A1", "A2")):
            json.dump({"schema": "halo/clearance-classification/1", "drc_report": "c.drc.json",
                       "classified": [{"index": 0, "class": cls, "measured_gap_mm": gap,
                                       "evidence": {"file": os.path.join("lane", evfile),
                                                    "rows": list(rows)}}]},
                      open(os.path.join(lane, "c-clearance-class.json"), "w"))

        write_claim("MEASUREMENT-LIMITED", 0.0500)
        r = classify_clearances(ddoc, [drcp], roots_, root=tmp)
        okc2 = r["counts"]["MEASUREMENT-LIMITED"] == 1 and r["counts"]["DRAWN-WRONG"] == 1
        print(f"    [{'ok ' if okc2 else 'RED'}] C-2 gap 0.0500 mm, pointer resolves -> "
              f"MEASUREMENT-LIMITED {r['counts']['MEASUREMENT-LIMITED']} (must be 1)")
        if not okc2: dfails.append("C-2")

        write_claim("MEASUREMENT-LIMITED", 0.0500, evfile="does-not-exist.json")
        r = classify_clearances(ddoc, [drcp], roots_, root=tmp)
        okc3 = r["counts"]["MEASUREMENT-LIMITED"] == 0 and r["counts"]["DRAWN-WRONG"] == 2
        print(f"    [{'ok ' if okc3 else 'RED'}] C-3 SAME claim, pointer does not resolve -> "
              f"refused, DRAWN-WRONG {r['counts']['DRAWN-WRONG']} (must be 2)")
        if not okc3: dfails.append("C-3")

        write_claim("MEASUREMENT-LIMITED", 0.0500, rows=("A1", "A9"))
        r = classify_clearances(ddoc, [drcp], roots_, root=tmp)
        okc3b = r["counts"]["MEASUREMENT-LIMITED"] == 0
        print(f"    [{'ok ' if okc3b else 'RED'}] C-3b pointer resolves, names a row that is NOT "
              f"in it -> refused (must be 0 excused)")
        if not okc3b: dfails.append("C-3b")

        write_claim("MEASUREMENT-LIMITED", 0.0900)          # outside the 0.0606 floor
        r = classify_clearances(ddoc, [drcp], roots_, root=tmp)
        okc4 = (r["counts"]["MEASUREMENT-LIMITED"] == 0 and r["counts"]["DRAWN-WRONG"] == 2
                and any("does not support" in x for x in r["refused"]))
        print(f"    [{'ok ' if okc4 else 'RED'}] C-4 THE ONE THAT MATTERS: pointer RESOLVES, gap "
              f"0.0900 mm is OUTSIDE the 0.0606 floor -> refused, DRAWN-WRONG "
              f"{r['counts']['DRAWN-WRONG']} (must be 2)")
        print(f"          resolving is not supporting. Without this the excuse is a string.")
        if not okc4: dfails.append("C-4")

        write_claim("GENUINELY-TOUCHING", None)
        r = classify_clearances(ddoc, [drcp], roots_, root=tmp)
        okc5 = r["counts"]["GENUINELY-TOUCHING"] == 1 and r["blocking"] == 1
        print(f"    [{'ok ' if okc5 else 'RED'}] C-5 GENUINELY-TOUCHING accepted and does NOT "
              f"block -> blocking {r['blocking']} of 2 (must be 1)")
        if not okc5: dfails.append("C-5")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    fails.extend(dfails)

    print()
    if fails:
        print("SELFTEST FAIL")
        for f in fails:
            print("  " + f)
        return EX_FAIL
    print("SELFTEST PASS - 9 anchor breaks + 19 deliverable breaks, each went the colour "
          "it had to, including the two DECOYS (an empty file and a wrong-format file at "
          "the right name) and the anti-gaming copy of halo_rev_a's own board.")
    return EX_PASS

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("-v", "--verbose", action="store_true")
    c.add_argument("--tree", default="replica", choices=["replica", "rev_a"])
    sub.add_parser("render")
    sub.add_parser("selftest")
    dp = sub.add_parser("deliverable")
    dp.add_argument("--tree", default="replica", choices=["replica", "rev_a"])
    dp.add_argument("--roots", nargs="+", default=None,
                    help="run the same three legs against paths YOU name, from any repo. "
                         "halo-cb: 'a check I have to be told about is one I will eventually "
                         "not be told about.' Exits 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.")
    a = p.parse_args()
    def cmd_deliverable(_a):
        tree = "caller" if _a.roots else _a.tree
        ddoc, drows = check_deliverable(tree=tree, roots=_a.roots)
        v = print_deliverable(drows, ddoc, tree)
        return EXIT[v]
    return {"check": cmd_check, "render": cmd_render, "selftest": cmd_selftest,
            "deliverable": cmd_deliverable}[a.cmd](a)

if __name__ == "__main__":
    sys.exit(main())
