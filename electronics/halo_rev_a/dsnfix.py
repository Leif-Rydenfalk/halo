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

  4. THE FIDUCIALS HAVE NO CLEAR FIELD. FID1 and FID2 are optical targets for
     the placement machine's camera, not electrical parts: they carry no net,
     and what they need is not a net clearance but an area with NO COPPER IN
     IT. The Specctra export sends them as ordinary pads, so the router treats
     them as obstacles at the netclass clearance and routes right up to them.
     MEASURED on the first successful autoroute (2026-09-05, 856 s, 10 passes):
     four DRC errors, ALL FOUR at FID1/FID2 — a via 0.2017 mm from FID1's pad
     against its own declared 0.35 mm, the same via breaking hole clearance,
     that via and the pad bridged inside one solder-mask aperture, and an NFC2
     track 0.3361 mm from FID2. Zero errors anywhere else on the board.
     `fiducial_keepouts()` emits a real `(keepout)` circle on every copper
     layer around each part the export marks `(PN FIDUCIAL)`.

  5. The keying notches and rule areas: CHECKED, NOT ASSUMED. Lane T1 measured
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


def renet_nfc(text, hints):
    """Put the outer half of the NFC winding back on NFC1 in the DSN.

    KiCad merges NFC1 into NFC2 through the AE2 net tie — correctly, because a
    coil IS a DC short between its own terminals — so the .kicad_pcb, and
    therefore the Specctra export, label every winding segment NFC2 while the
    PADS keep their own nets. Handed that, freerouting sees one six-pin net
    and joins it by the shortest path it can find: a 2 mm trace across the
    feed, the coil bypassed, the DRC clean, and no NFC antenna. The winding is
    a spiral, so RADIUS separates the halves exactly; `board.py` computes the
    split and writes it to `out/dsn_hints.json`.
    """
    n = hints["nfc"]
    cx, cy = hints["dsn_centre_um"]
    rsplit, w = n["split_radius_um"], n["width_um"]
    out, moved, seen = [], 0, 0
    pat = re.compile(r'\(wire \(path (\S+) ([\d.]+)\s+([-\d.]+) ([-\d.]+)\s+'
                     r'([-\d.]+) ([-\d.]+)\)\(net "?([^")]+)"?\)')
    for line in text.split("\n"):
        m = pat.search(line)
        if m and m.group(1) == n["layer"] and abs(float(m.group(2)) - w) < 1.0:
            seen += 1
            r0 = ((float(m.group(3)) - cx) ** 2
                  + (float(m.group(4)) - cy) ** 2) ** 0.5
            r1 = ((float(m.group(5)) - cx) ** 2
                  + (float(m.group(6)) - cy) ** 2) ** 0.5
            r = min(r0, r1)      # BOTH ends outside, or it is not outer half
            # ONE DIRECTION ONLY. This restores outer-half copper that the
            # merge relabelled; it never moves anything the other way. The
            # two stubs that close the winding onto the tie cross the split
            # radius by construction, and a symmetric rule renamed them - 3
            # wires, each of which is the join the coil depends on.
            want = n["outer_half_net"]
            if r > rsplit and m.group(7) == n["inner_half_net"]:
                line = (line[:m.start(7)] + want + line[m.end(7):])
                moved += 1
        out.append(line)
    return "\n".join(out), {"coil_wires_seen": seen, "renamed": moved}


#: IPC-7351B: the clear area around a global fiducial is a radius of ONE
#: FIDUCIAL DIAMETER measured from the fiducial's edge — for halo's 1.00 mm
#: round fiducial that is a 1.00 mm clear radius, a 2.00 mm circle. This is a
#: published number and not one tuned until the board passed: the board's own
#: `(clearance 0.35)` would have needed only 0.85 mm, and clearing to the
#: standard also separates the 1.27 mm mask apertures that the first autoroute
#: bridged.
FIDUCIAL_CLEAR_DIA_MM = 2.00

#: Copper layers a fiducial keepout has to cover. A camera sees the outer
#: layers, but copper on an inner layer under a fiducial still shows through a
#: thin board as a shadow, and the placement machines that care about that are
#: the ones this project is aimed at.
COPPER_LAYERS = ("F.Cu", "In1.Cu", "In2.Cu", "B.Cu")


def fiducial_keepouts(s, dia_mm=FIDUCIAL_CLEAR_DIA_MM, layers=COPPER_LAYERS):
    """Give every `(PN FIDUCIAL)` part a real no-copper circle. -> (s, stats)

    Specctra coordinates on this export are micrometres — the header says
    `(resolution um 10)` and KiCad writes FID1 at 9716.607 for a pad the board
    puts at 9.716607 mm — so the diameter goes in as `dia_mm * 1000`.

    The keepout is inserted at the END of `(structure ...)`, beside the
    via_keepouts KiCad already writes there, because that is where freerouting
    reads them from. If the structure block cannot be found the function
    RETURNS UNCHANGED AND SAYS SO in its stats rather than writing a keepout
    somewhere freerouting will not look — a keepout in the wrong place is
    indistinguishable, in the output file, from a board that needed none.
    """
    places = re.findall(r"\(place\s+(\S+)\s+([-\d.]+)\s+([-\d.]+)\s+\w+\s+"
                        r"[-\d.]+\s+\(PN\s+FIDUCIAL\)", s)
    if not places:
        return s, {"fiducials": 0, "keepouts_added": 0,
                   "why": "no part in the export carries (PN FIDUCIAL)"}
    # end of the (structure ...) block
    i = s.find("(structure")
    if i < 0:
        return s, {"fiducials": len(places), "keepouts_added": 0,
                   "why": "no (structure ...) block; nothing written"}
    depth, j = 0, i
    while j < len(s):
        if s[j] == "(":
            depth += 1
        elif s[j] == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    if depth != 0:
        return s, {"fiducials": len(places), "keepouts_added": 0,
                   "why": "the (structure ...) block does not close; nothing written"}
    dia_um = dia_mm * 1000.0
    out, refs = [], []
    for ref, x, y in places:
        refs.append(ref)
        for lay in layers:
            out.append('    (keepout "" (circle %s %.1f %s %s))'
                       % (lay, dia_um, x, y))
    s = s[:j] + "\n" + "\n".join(out) + "\n  " + s[j:]
    return s, {"fiducials": len(places), "refs": refs,
               "keepouts_added": len(out), "clear_diameter_mm": dia_mm,
               "layers": list(layers),
               "why": "IPC-7351B clear area, one fiducial diameter of no copper"}


def report(s):
    return {
        "keepout": s.count("(keepout"),
        "via_keepout": s.count("(via_keepout"),
        "plane": s.count("(plane "),
        "wire": s.count("(wire "),
        "signal_layers": len(re.findall(r'\(type signal\)', s)),
        "power_layers": len(re.findall(r'\(type power\)', s)),
    }


def fix(text, drop=PLANE_NETS, protect=PROTECT_NETS, hints=None,
        fiducials=True):
    before = report(text)
    s, n_lay = _layers_to_power(text)
    nfc = {}
    if hints:
        s, nfc = renet_nfc(s, hints)
    s, n_prot = _protect_wires(s, set(protect) | set(PLANE_NETS))
    s, dropped = _drop_nets_from_network(s, drop) if drop else (s, [])
    fid = {"fiducials": 0, "keepouts_added": 0, "why": "not requested"}
    if fiducials:
        s, fid = fiducial_keepouts(s)
    return s, {
        "before": before,
        "after": report(s),
        "plane_layers_retyped": n_lay,
        "wires_protected": n_prot,
        "nets_dropped": dropped,
        "nfc": nfc,
        "fiducial_keepouts": fid,
    }


if __name__ == "__main__":
    import json
    import os
    src, dst = sys.argv[1], sys.argv[2]
    drop = PLANE_NETS
    for a in sys.argv[3:]:
        if a.startswith("--drop="):
            drop = tuple(x for x in a.split("=", 1)[1].split(",") if x)
    hints = None
    hp = os.path.join(os.path.dirname(os.path.abspath(src)), "dsn_hints.json")
    if os.path.exists(hp):
        hints = json.load(open(hp))
    txt = open(src).read()
    out, stats = fix(txt, drop=drop, hints=hints)
    open(dst, "w").write(out)
    print(json.dumps(stats, indent=2))
    if stats["plane_layers_retyped"] != len(PLANE_LAYERS):
        sys.exit("REFUSED: retyped %d of %d plane layers — the exporter's "
                 "layer block is not the shape this expects, and a fix that "
                 "matched nothing is not a fix"
                 % (stats["plane_layers_retyped"], len(PLANE_LAYERS)))
    f = stats["fiducial_keepouts"]
    if f["fiducials"] and not f["keepouts_added"]:
        sys.exit("REFUSED: %d fiducial(s) in the export and 0 keepouts written "
                 "(%s). Every DRC error on the first successful autoroute of "
                 "this board was copper crowding a fiducial; a filter that "
                 "silently skips that step leaves a DSN indistinguishable from "
                 "one that needed no fiducial keepouts"
                 % (f["fiducials"], f.get("why")))
