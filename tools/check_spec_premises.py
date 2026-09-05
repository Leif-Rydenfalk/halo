#!/usr/bin/env python3
"""Every number a spec consumes must name the artifact it came from.

A spec's `why` may cite a frequency as `measured <N> GHz`. That word is a
claim about PROVENANCE, and provenance is checkable: somewhere under
ce-rf/out/ there must be a verdict row holding that value. If there is not,
the number was computed -- most likely by the very law about to consume it --
and calling it measured closes a loop that no further solving can open.

See docs/TOOLS-THAT-LIE.md section 10, and CONCERNS.md C-7, which this check
was written from and which it still fails on.

    PASS   the value resolves to a verdict row, named in the output
    FAIL   nothing on disk holds that value
    exit   0 all resolve / 1 any unresolved / 2 nothing to check

This check has a positive and a negative control in the live data, so it
cannot be trusted merely because it is green somewhere: rt1's premise
(2.0669) resolves to meander9-passive, and rt2's (2.5565) resolves to
nothing. If BOTH come back the same way, the check is broken, not the specs.
"""
import json, os, re, sys, glob

CE_RF = os.path.expanduser("~/dev/ce-workshop/ce-rf")
# 0.5 MHz: tight enough that a scaled prediction cannot masquerade as a
# neighbouring measurement, loose enough to survive the 4 decimal places
# these specs are written to.
TOL_GHZ = 0.0005
CLAIM = re.compile(r"measured\s+([0-9]+\.?[0-9]*)\s*GHz", re.I)


def _rows_on_disk():
    """Every numeric verdict row that exists, as (value, case, row_name)."""
    out = []
    for v in glob.glob(os.path.join(CE_RF, "out", "*", "verdict.json")):
        case = os.path.basename(os.path.dirname(v))
        try:
            j = json.load(open(v))
        except Exception as e:
            print(f"  !! unreadable verdict {case}: {e}", file=sys.stderr)
            continue
        for r in j.get("rows", []):
            if isinstance(r.get("value"), (int, float)):
                out.append((float(r["value"]), case, r.get("name", "?")))
    return out


def main():
    rows = _rows_on_disk()
    if not rows:
        print("CANNOT DETERMINE: no verdict rows under ce-rf/out/ to check against")
        return 2

    specs = sorted(glob.glob(os.path.join(CE_RF, "specs", "*.json")))
    checked = failed = 0
    for s in specs:
        try:
            why = json.load(open(s)).get("why", "") or ""
        except Exception:
            continue
        for m in CLAIM.finditer(why):
            val = float(m.group(1))
            checked += 1
            hits = [(c, n) for (v, c, n) in rows if abs(v - val) <= TOL_GHZ]
            name = os.path.basename(s)
            if hits:
                c, n = hits[0]
                extra = f" (+{len(hits)-1} more)" if len(hits) > 1 else ""
                print(f"PASS  {name}\n        cites 'measured {val} GHz' -> {c} :: {n}{extra}")
            else:
                failed += 1
                # Show what it IS, if the 1/L law explains it -- that is the
                # signature of a prediction fed back as evidence.
                near = sorted(rows, key=lambda r: abs(r[0] - val))[:1]
                hint = f"; nearest real row is {near[0][0]:.4f} in {near[0][1]}" if near else ""
                print(f"FAIL  {name}\n        cites 'measured {val} GHz' -> NO VERDICT ROW HOLDS THIS{hint}")

    if checked == 0:
        print("CANNOT DETERMINE: no spec cites a measured frequency")
        return 2
    print(f"\n{checked - failed} resolve, {failed} do not, of {checked} premise(s) in {len(specs)} spec(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
