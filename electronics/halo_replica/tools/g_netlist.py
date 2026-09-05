"""g_netlist.py — READ the connectivity out of the ERC-PASSED schematic.

The orderable board NEVER retypes connectivity. This reads it with KiCad's own
netlister (cepcb.schematic.netlist_of_sch) and writes fab/netlist.json:

    {"nets": {name: ["REF.PIN", ...]},
     "parts": {ref: {lib_id, value, footprint}},
     "counts": {...}}

Run: python3 tools/g_netlist.py     (system python; kicad-cli does the work)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-pcb")

from cepcb.schematic import netlist_of_sch          # noqa: E402
from cepcb import sexpr                             # noqa: E402

SCH = os.path.join(REPLICA, "out", "schematic", "halo_replica.kicad_sch")
OUT = os.path.join(REPLICA, "fab", "netlist.json")


def parts_of_sch(path):
    tree = sexpr.parse(open(path, encoding="utf-8").read())
    parts = {}
    for s in sexpr.children(tree, "symbol"):
        props = {}
        for pr in sexpr.children(s, "property"):
            if len(pr) >= 3:
                props[str(pr[1])] = str(pr[2])
        ref = props.get("Reference")
        if not ref or ref.startswith("#"):
            continue
        parts[ref] = {
            "lib_id": str(sexpr.value(s, "lib_id", "")),
            "value": props.get("Value", ""),
            "footprint": props.get("Footprint", ""),
        }
    return parts


def main():
    nets = netlist_of_sch(SCH)
    parts = parts_of_sch(SCH)
    nets = {k: sorted(v) for k, v in sorted(nets.items()) if v}
    pins = sum(len(v) for v in nets.values())
    doc = {
        "source": os.path.relpath(SCH, REPLICA),
        "nets": nets,
        "parts": parts,
        "counts": {"nets": len(nets), "parts": len(parts), "pin_nodes": pins},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w"), indent=1, sort_keys=True)
    print("nets %d  parts %d  pin nodes %d -> %s"
          % (len(nets), len(parts), pins, os.path.relpath(OUT, REPLICA)))
    missing = sorted(r for r, p in parts.items() if not p["footprint"])
    print("parts with NO footprint (%d): %s" % (len(missing), " ".join(missing)))


if __name__ == "__main__":
    main()
