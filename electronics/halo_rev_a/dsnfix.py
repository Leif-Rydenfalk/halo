"""dsnfix — repair what KiCad's Specctra export tells freerouting about THIS board.

LANE B1, 2026-09-04. Written because three autoroutes of halo_rev_a timed out
at 900 s, 3300 s and 2400 s while the SAME jar finishes a Ø31.87 mm test puck
in 96 s. The difference is not the board's difficulty. It is four statements
the exporter makes that are false about this board:

  1. `(layer In1.Cu (type signal))` and the same for In2.Cu. THEY ARE SOLID
     PLANES — GND on In1, VDD on In2 — poured over the whole disc. Told they
     are signal layers, freerouting must consider every trace on both of them,
     carving channels through plane copper it will then have to justify. That
     is 2x the layers and the worst 2x, because every candidate there collides
     with the pour. `(type power)` is Specctra's own word for a plane layer and
     freerouting honours it by not routing signals there.

  2. GND (39 pins) and VDD (24 pins) are in `(network)` as 63 pin-to-pin
     connections to route. They are not connections a router should make: the
     pours join them and board.py's `stitch()` already put the vias in. Left in
     the problem they are 63 of the 176 pins — 36 percent of the work, all of
     it wrong.

  3. Every existing wire comes out `(type route)`, which in freerouting means
     RIPPABLE. The 2.4 GHz element and the NFC spiral are drawn to solved
     dimensions; a router that reroutes them has destroyed the only two pieces
     of copper on this board whose shape was computed. `(type protect)` is the
     token that says do not touch.

  4. The keying notches and rule areas: CHECKED, NOT ASSUMED. Lane T1 measured
     KiCad exporting every rule area as a full copper keepout regardless of its
     flags, which made freerouting route 0 of 11 nets in 923 s. On this board
     the export is `(via_keepout)` x4 and `(keepout)` x0 — the antenna ground
     clearance, correctly, and nothing else. `report()` prints both counts so a
     regression in the exporter shows up as a number rather than a timeout.

Every edit is COUNTED and the count is returned. A rewrite that matched
nothing would otherwise look exactly like a rewrite that was not needed.

    python3 dsnfix.py in.dsn out.dsn [--keep-planes-in-network]
"""
import re
import sys

#: Nets whose copper is drawn by board.py to a solved shape and must survive.
PROTECT_NETS = ("ANT_FEED", "NFC1", "NFC2")

#: Layers that are poured planes on halo_rev_a, and the net each carries.
PLANE_LAYERS = {"In1.Cu": "GND", "In2.Cu": "VDD"}

#: Nets the pours and the via stitching already join.
PLANE_NETS = ("GND", "VDD")


def _layers_to_power(s):
    n = 0
    for lay in PLANE_LAYERS:
        pat = re.compile(r'(\(layer\s+' + re.escape(lay) +
                         r'\s*\n\s*\(type\s+)signal(\))')
        s, k = pat.subn(r'\1power\2', s)
        n += k
    return s, n


def _protect_wires(s, nets):
    """`(type route)` -> `(type protect)` on wires whose net is in `nets`."""
    n = 0
    out = []
    for line in s.split("\n"):
        m = re.search(r'\(net\s+"?([A-Za-z0-9_+.\-/]+)"?\)\(type route\)', line)
        if m and m.group(1) in nets:
            line = line.replace("(type route)", "(type protect)")
            n += 1
        out.append(line)
    return "\n".join(out), n


def _drop_nets_from_network(s, nets):
    """Delete `(net NAME (pins ...))` blocks and the class references.

    Balanced-paren scan, not a regex: a pin list runs over many lines and a
    lazy regex stops at the first `)` it sees, which silently truncates the
    file into something freerouting parses as a shorter board.
    """
    dropped = []
    for name in nets:
        i = s.find('(net %s\n' % name)
        if i < 0:
            i = s.find('(net "%s"' % name)
        if i < 0:
            continue
        depth, j = 0, i
        while j < len(s):
            if s[j] == "(":
                depth += 1
            elif s[j] == ")":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        s = s[:i] + s[j:]
        dropped.append(name)
    # and out of the (class ...) membership list
    k = s.find("(class ")
    if k >= 0:
        end = s.find("(circuit", k)
        head = s[k:end]
        for name in dropped:
            head = re.sub(r'(?<![\w"])' + re.escape(name) + r'(?![\w"])',
                          "", head)
        head = re.sub(r'[ \t]+\n', '\n', head)
        s = s[:k] + head + s[end:]
    return s, dropped


def report(s):
    return {
        "keepout": s.count("(keepout"),
        "via_keepout": s.count("(via_keepout"),
        "plane": s.count("(plane "),
        "wire": s.count("(wire "),
        "signal_layers": len(re.findall(r'\(type signal\)', s)),
        "power_layers": len(re.findall(r'\(type power\)', s)),
    }


def fix(text, drop_plane_nets=True, protect=PROTECT_NETS):
    before = report(text)
    s, n_lay = _layers_to_power(text)
    s, n_prot = _protect_wires(s, set(protect) | set(PLANE_NETS))
    dropped = []
    if drop_plane_nets:
        s, dropped = _drop_nets_from_network(s, PLANE_NETS)
    return s, {
        "before": before,
        "after": report(s),
        "plane_layers_retyped": n_lay,
        "wires_protected": n_prot,
        "nets_dropped": dropped,
    }


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    keep = "--keep-planes-in-network" in sys.argv
    txt = open(src).read()
    out, stats = fix(txt, drop_plane_nets=not keep)
    open(dst, "w").write(out)
    import json
    print(json.dumps(stats, indent=2))
    if stats["plane_layers_retyped"] != len(PLANE_LAYERS):
        sys.exit("REFUSED: retyped %d of %d plane layers — the exporter's "
                 "layer block is not the shape this expects, and a fix that "
                 "matched nothing is not a fix"
                 % (stats["plane_layers_retyped"], len(PLANE_LAYERS)))
