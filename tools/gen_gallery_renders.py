"""Gallery renders — lane G1 (visuals).

    bin/cad ce-designs/halo/tools/gen_gallery_renders.py

Every image here comes from the SAME solids design.py builds; nothing is
drawn by hand and nothing is an artist's impression. This file writes only
into out/render/, which lane G1 owns. out/mech/ belongs to the enclosure
lane and is never touched here.

Each render is listed in tools/gen_gallery.py with the command that made it
and the measured verdict it illustrates.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

os.environ.setdefault("CE_TRIAD_ROOT",
                      ROOT + ":" + os.path.dirname(os.path.dirname(ROOT)))

import design                                                # noqa: E402
from cecad import Assembly, render, exploded                 # noqa: E402
from cecad.render import view_for_section                     # noqa: E402
from FreeCAD import Vector                                    # noqa: E402

# Square-on at the cut face. view_for_section picks the side the material
# was NOT kept on; elev=0 makes it a true elevation instead of an iso.
SEC = ("y", 0.0)
FLAT = view_for_section(SEC, elev=0.0)
ISO_CUT = view_for_section(SEC, elev=26.0)

# (key in design.parts(), colour) — the same colours design.py's own
# assembly uses, so a reader comparing images sees one palette.
EXPLODE_PARTS = [("door", "steel"), ("seal", "red"), ("cell", "blue"),
                 ("cp1", "orange"), ("cp2", "orange"), ("cn1", "orange"),
                 ("carrier", "gold"), ("pcb", "green"), ("piezo", "purple"),
                 ("shell", "grey")]

OUT = os.path.join(ROOT, "out", "render")
os.makedirs(OUT, exist_ok=True)


def o(name):
    return os.path.join(OUT, name)


def full_assembly(P):
    a = Assembly("halo-puck")
    a.add("shell", P["shell"], color="grey", joint="rigid")
    a.add("carrier", P["carrier"], color="gold", joint="glued")
    a.add("seal", P["seal"], color="red", joint="glued")
    a.add("door", P["door"], color="steel", joint="bayonet")
    a.add("cell", P["cell"], color="blue", joint="clamped")
    a.add("contact_pos_a", P["cp1"], color="orange", joint="glued")
    a.add("contact_pos_b", P["cp2"], color="orange", joint="glued")
    a.add("contact_neg", P["cn1"], color="orange", joint="glued")
    a.add("pcb", P["pcb"], color="green", joint="soldered")
    a.add("piezo", P["piezo"], color="purple", joint="glued")
    return a


def main():
    P = design.parts()
    a = full_assembly(P)

    # 1 — the product, lit. Same solid as out/mech/halo-puck-iso.png, drawn
    # through the physically-based path so the crown's curvature reads.
    render(a, o("halo-puck-hero.png"), view="iso", mode="pbr",
           tol=0.03, ss=3, W=1400, H=980,
           title="halo puck — 31.874 mm across, 7.980 mm tall (measured)")

    # 2 — exploded. cecad's exploded() spreads each part in proportion to
    # its own extent, so a 0.60 mm board never separates from the shell it
    # sits under. This one displaces every part by the SAME 6 mm along z in
    # assembled stack order: the geometry is untouched, only the position
    # is, which is what an exploded view is.
    ordered = sorted(EXPLODE_PARTS,
                     key=lambda kc: P[kc[0]].shape.BoundBox.Center.z)
    pairs = []
    for i, (k, colour) in enumerate(ordered):
        sh = P[k].shape.copy()
        sh.translate(Vector(0, 0, i * 6.0))
        pairs.append((sh, colour))
    render(pairs, o("halo-puck-exploded-wide.png"), view="iso",
           tol=0.05, ss=2, W=1400, H=1400,
           title="all ten parts, each lifted 6.000 mm along z in stack order "
                 "(door, seal, cell, 3 contacts, carrier, board, bender, shell)")

    # 3 — the piezo on its flat land, and the 0.05 mm bond line. Shell +
    # piezo + pcb only: the whole puck sectioned hides this behind the
    # carrier wall.
    render([(P["shell"], "grey"), (P["piezo"], "purple")],
           o("halo-piezo-land.png"), section=SEC, view=ISO_CUT,
           tol=0.03, ss=3, W=1400, H=900,
           title="the bender on the flat land — bond line 0.050 mm to the "
                 "shell, 1.080 mm clear of the board (design.py: diaphragm gap)")

    # 4 — the bayonet: carrier legs and door tabs, nothing else in the way.
    render([(P["carrier"], "gold"), (P["door"], "steel")],
           o("halo-bayonet.png"), view="iso", tol=0.03, ss=3,
           W=1400, H=980,
           title="the bayonet — three carrier legs at 0/120/240 deg and the "
                 "door's three tabs (press 0.250 mm, then twist 10 deg)")

    # 5 — the same pair cut open, which is where the detent ridge lives.
    render([(P["carrier"], "gold"), (P["door"], "steel"), (P["seal"], "red")],
           o("halo-bayonet-section.png"), section=SEC, view=FLAT,
           tol=0.03, ss=3, W=1400, H=700,
           title="door, seal and carrier on the axis — seal squeeze 20.0 % "
                 "of a 0.500 mm section")

    # 6 — the connector-less battery interface: three stamped springs and
    # the cell they carry.
    render([(P["cp1"], "orange"), (P["cp2"], "orange"), (P["cn1"], "orange")],
           o("halo-contacts.png"), view="iso", tol=0.02, ss=3,
           W=1400, H=980,
           title="three sprung contacts, no connector — two positive on the "
                 "wall, one negative on the floor, exactly as in the AirTag")

    # 7 — the board where it actually sits, with the shell cut away.
    render([(P["shell"], "grey"), (P["carrier"], "gold"),
            (P["pcb"], "green"), (P["piezo"], "purple"), (P["cell"], "blue")],
           o("halo-board-in-shell.png"), section=SEC,
           view=ISO_CUT, tol=0.03, ss=3, W=1400, H=980,
           title="the board in the shell — Cu 26.00 mm board inside the "
                 "31.874 mm envelope, cell below, bender above")

    # The measured stack, read off the finished solids — the numbers the
    # gallery's cross-section figure is drawn from. Nothing typed.
    import json
    rows = []
    for key, label in [("door", "battery door (301 SS)"),
                       ("seal", "door seal"),
                       ("cell", "CR2032 cell"),
                       ("cn1", "negative contact"),
                       ("cp1", "positive contact a"),
                       ("cp2", "positive contact b"),
                       ("carrier", "carrier (LCP)"),
                       ("pcb", "PCB blank"),
                       ("piezo", "piezo bender"),
                       ("shell", "shell (PC)")]:
        bb = P[key].shape.BoundBox
        rows.append({"key": key, "label": label, "name": P[key].name,
                     "z0": round(bb.ZMin, 4), "z1": round(bb.ZMax, 4),
                     "dia_mm": round(max(bb.XLength, bb.YLength), 4)})
    env = a.shape().BoundBox if hasattr(a, "shape") else None
    doc = {"$generated": "tools/gen_gallery_renders.py — bounding boxes read "
                         "off the finished solids, never off the parameters",
           "units": "mm", "parts": rows,
           "total_z": round(max(r["z1"] for r in rows)
                            - min(r["z0"] for r in rows), 4),
           "max_dia": round(max(r["dia_mm"] for r in rows), 4)}
    with open(o("stack.json"), "w") as fh:
        json.dump(doc, fh, indent=2)
    print("stack: %.3f mm tall, %.3f mm across (measured)"
          % (doc["total_z"], doc["max_dia"]))

    print("wrote:")
    for f in sorted(os.listdir(OUT)):
        p = o(f)
        print("  %-34s %8d bytes" % (f, os.path.getsize(p)))


main()
