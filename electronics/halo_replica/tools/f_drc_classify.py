"""f_drc_classify — WHOSE unmanufacturability is each DRC error?

    python3 electronics/halo_replica/tools/f_drc_classify.py
    ... --break-unclassify   drop the evidence and watch everything become
                             OUR-ERROR, which is the default and must be

Exit 0 if every violation is classified, 1 if any OUR-ERROR remains,
2 if the inputs are not there.

---------------------------------------------------------------------------
WHY NOT JUST CLEAR THEM
---------------------------------------------------------------------------
DO NOT MOVE A MEASURED POSITION TO SATISFY A DESIGN RULE. Every land on this
board is a metrology row at a measured position and a measured size. If two
overlap, exactly one of the possibilities is a defect of ours; the other two
are findings. Nudging a pad to clear a rule would be FALSIFYING A
MEASUREMENT TO SATISFY A MANUFACTURING CONSTRAINT, and it would be invisible
in every render afterwards.

So the errors are CLASSIFIED, not cleared. The split is the deliverable: it
says which of this board's unmanufacturability belongs to Apple, which
belongs to the photographs, and which belongs to us.

---------------------------------------------------------------------------
THE FOUR CLASSES. EVERY ONE IS REPORTED, INCLUDING THE EMPTY ONES
---------------------------------------------------------------------------
A split that omits an empty class reads as though the question was never
asked.

MEASUREMENT-LIMITED  the two features are closer than this evidence base can
                     separate them. Checkable, not asserted: the front
                     handoff's own registration_holdout_mm is 0.1029 and the
                     back's 0.1256, and every row carries its short side in
                     GENUINE pixels.

                     The commonest case here is subtler and worth naming: a
                     handoff row is the MINIMUM-AREA RECTANGLE around a
                     connected component. Two separate blobs cannot overlap
                     — the segmentation guarantees it — but their rotated
                     bounding rectangles can, because a rect contains
                     background. An overlap between two CLASS B lands is
                     therefore a fact about the RECTANGLE REPRESENTATION and
                     not about Apple's copper.

BOUND-LIMITED        measured against an outline whose diameter IS A BOUND,
                     24.95-26.34 mm, not a number. AND IT DOES NOT RESOLVE
                     ITSELF: the signed expectation is that the OD moves
                     DOWN, so more copper falls outside a smaller board.
                     These get WORSE as the bound resolves. They cannot be
                     waited out.

GENUINELY-TOUCHING   Apple's own metal is continuous there. THIS CLASS IS
                     EMPTY AND THE METHOD SAYS WHY: asserting it needs
                     per-pair evidence of contiguity, and the only detector
                     that ran reports SEPARATE connected components by
                     construction. Nothing in this evidence base can put a
                     violation here. It is listed so the reader can see the
                     question was asked and refused, not skipped.

OUR-ERROR            a footprint or a transform we got wrong. THE DEFAULT.
                     Anything the evidence does not place elsewhere lands
                     here, which puts the incentive the right way round:
                     silence means our fault, not Apple's.

---------------------------------------------------------------------------
WHICH RUN
---------------------------------------------------------------------------
A DRC file is live and is re-run whenever the board changes; two readings an
hour apart are two different runs, not a disagreement. This tool records the
drc.json's mtime, its SHA-256 and the board's, and prints them. A
classification that does not name its run is not checkable.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPLICA, "pcb"))
import footprints as FP                                        # noqa: E402

DRC = os.path.join(REPLICA, "pcb", "out", "halo_replica.drc.json")
PCB = os.path.join(REPLICA, "pcb", "out", "halo_replica.kicad_pcb")
HF = os.path.join(REPLICA, "metrology", "HANDOFF-positions-front.json")
HB = os.path.join(REPLICA, "metrology", "HANDOFF-positions-back.json")
OUT = os.path.join(REPLICA, "pcb", "out", "drc-classification.json")

NUM = re.compile(r"(\d+\.\d+)\s*mm")
REF = re.compile(r"\b([A-Z]{1,4}\d{1,4})\b")


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def main():
    broken = "--break-unclassify" in sys.argv[1:]
    for p in (DRC, PCB, HF, HB):
        if not os.path.exists(p):
            print("CANNOT DETERMINE — missing %s" % p)
            return 2

    drc = json.load(open(DRC))
    hf, hb = json.load(open(HF)), json.load(open(HB))
    floor_f = float(hf["uncertainty"]["registration_holdout_mm"])
    floor_b = float(hb["uncertainty"]["registration_holdout_mm"])
    rows = {r["id"]: r for r in hf["rows"]}
    rows_b = {r["id"]: r for r in hb["rows"]}

    classes = {"MEASUREMENT-LIMITED": [], "BOUND-LIMITED": [],
               "GENUINELY-TOUCHING": [], "OUR-ERROR": []}

    # KiCad reports a solder_mask_bridge WITH NO DISTANCE, so it cannot be
    # classified on its own numbers. It does not need to be: a mask bridge
    # between two lands is the SAME PHYSICAL FACT as the clearance violation
    # between the same two lands — the copper is closer than the mask sliver
    # can survive. So a bridge inherits the class of the clearance violation
    # on its own pair, and inherits NOTHING if there is no such pair. The
    # inheritance is recorded on each row, so no violation is moved between
    # classes by an unstated rule.
    ml_pairs = set()
    for v in drc["violations"]:
        if v["type"] != "clearance":
            continue
        nums = [float(x) for x in NUM.findall(v["description"])]
        if len(nums) > 1 and nums[1] <= max(floor_f, floor_b):
            rr = []
            for it in v.get("items", []):
                rr += [m for m in REF.findall(it.get("description", ""))
                       if m in rows or m in rows_b]
            if len(set(rr)) == 2:
                ml_pairs.add(frozenset(rr))

    for v in drc["violations"]:
        nums = [float(x) for x in NUM.findall(v["description"])]
        rule = nums[0] if nums else None
        actual = nums[1] if len(nums) > 1 else None
        refs = []
        for it in v.get("items", []):
            refs += [m for m in REF.findall(it.get("description", ""))
                     if m in rows or m in rows_b]
        rec = {"type": v["type"], "severity": v.get("severity"),
               "rule_mm": rule, "actual_mm": actual, "refs": sorted(set(refs)),
               "description": v["description"]}

        if broken:
            classes["OUR-ERROR"].append(dict(rec, why="evidence withheld "
                                             "(--break-unclassify)"))
            continue

        if v["type"] == "copper_edge_clearance":
            rec["why"] = (
                "measured against the OUTLINE, whose diameter is a BOUND "
                "(24.95-26.34 mm), not a number. The signed expectation is "
                "that it moves DOWN, so this gets WORSE as the bound "
                "resolves — it cannot be waited out. The 0.5 mm rule is "
                "KiCad's default and is NOT a fab spec this lane chose.")
            classes["BOUND-LIMITED"].append(rec)
            continue

        if v["type"] in ("clearance", "solder_mask_bridge") and rec["refs"]:
            back = any(r in rows_b for r in rec["refs"])
            floor = floor_b if back else floor_f
            gpx = (hb if back else hf)["scale"]["genuine_px_per_mm"]
            if actual is not None and actual <= floor:
                rec["floor_mm"] = floor
                rec["genuine_px_per_mm"] = gpx
                rec["why"] = (
                    "actual %.4f mm is at or below the %s handoff's own "
                    "registration_holdout_mm of %.4f (%.1f-%.1f genuine "
                    "px/mm). %s"
                    % (actual, "back" if back else "front", floor,
                       gpx[0], gpx[1],
                       "Actual 0.0000 mm means the two rows' MINIMUM-AREA "
                       "RECTANGLES overlap. The segmentation reports "
                       "SEPARATE connected components, so the blobs do not "
                       "overlap; a rotated rect contains background, and "
                       "the overlap is in the representation rather than in "
                       "Apple's copper."
                       if actual == 0.0 else
                       "Two features this close cannot be separated by this "
                       "evidence base."))
                classes["MEASUREMENT-LIMITED"].append(rec)
                continue

        if (v["type"] == "solder_mask_bridge"
                and frozenset(rec["refs"]) in ml_pairs):
            rec["inherits_from"] = ("the clearance violation on the same "
                                    "pair, which is MEASUREMENT-LIMITED")
            rec["why"] = (
                "KiCad reports a mask bridge with NO distance, so it carries "
                "no number of its own. It does not need one: a bridge "
                "between these two lands is the same physical fact as the "
                "clearance violation between the same two lands, and that "
                "one is measurement-limited. Inherited, and the inheritance "
                "is recorded rather than assumed.")
            classes["MEASUREMENT-LIMITED"].append(rec)
            continue

        rec["why"] = ("not placed by any evidence available here. OUR-ERROR "
                      "is the DEFAULT class, so this is our fault until "
                      "something shows otherwise.")
        classes["OUR-ERROR"].append(rec)

    run = {"drc_json": os.path.relpath(DRC, REPLICA),
           "drc_sha256_16": _sha(DRC), "drc_mtime": os.path.getmtime(DRC),
           "board_sha256_16": _sha(PCB), "board_mtime": os.path.getmtime(PCB),
           "board_is_older_than_drc": os.path.getmtime(PCB)
                                      <= os.path.getmtime(DRC)}
    total = sum(len(v) for v in classes.values())
    print("f_drc_classify — %d violations, run %s (drc sha %s, board sha %s)"
          % (total, run["drc_mtime"], run["drc_sha256_16"],
             run["board_sha256_16"]))
    if broken:
        print("  BREAK ACTIVE: evidence withheld, everything must fall to "
              "the default class")
    for k in ("MEASUREMENT-LIMITED", "BOUND-LIMITED", "GENUINELY-TOUCHING",
              "OUR-ERROR"):
        print("  %-20s %3d" % (k, len(classes[k])))
    if not classes["GENUINELY-TOUCHING"]:
        print("     GENUINELY-TOUCHING is EMPTY, and by method rather than "
              "by absence: asserting it needs per-pair evidence that Apple's "
              "metal is continuous, and the only detector that ran reports "
              "SEPARATE connected components by construction. Nothing here "
              "can put a violation in that class.")
    for r in classes["OUR-ERROR"][:10]:
        print("     OUR-ERROR %-22s rule %s actual %s refs %s"
              % (r["type"], r["rule_mm"], r["actual_mm"], r["refs"]))

    if not broken:
        json.dump({"tool": "tools/f_drc_classify.py", "run": run,
                   "counts": {k: len(v) for k, v in classes.items()},
                   "classes": classes,
                   "rule": "DO NOT MOVE A MEASURED POSITION TO SATISFY A "
                           "DESIGN RULE. These are classified, not cleared.",
                   "genuinely_touching_method":
                       "empty by method: per-pair contiguity evidence does "
                       "not exist in this evidence base",
                   }, open(OUT, "w"), indent=1)
        print("  wrote %s" % os.path.relpath(OUT, REPLICA))
    return 1 if classes["OUR-ERROR"] else 0


sys.exit(main())
