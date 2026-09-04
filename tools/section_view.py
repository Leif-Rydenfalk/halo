"""section_view.py — the stack, square on, with the layers labelled.

    ~/dev/ce-workshop/ce-cad/bin/cad tools/section_view.py

A render-only pass over design.py's own solids: no check(), no exports, so it
is a few seconds rather than a few minutes. The iso section in
out/mech/halo-puck-section.png shows the parts in space; this one shows the
7.98 mm as a stack you can read heights off.
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

spec = importlib.util.spec_from_file_location(
    "halo_design", os.path.join(_ROOT, "design.py"))
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)

from cecad import Assembly, render                                  # noqa: E402

P = D.parts()
a = Assembly("halo-puck-section")
for label, key, colour in (("shell", "shell", "grey"),
                           ("carrier", "carrier", "gold"),
                           ("seal", "seal", "red"),
                           ("door", "door", "steel"),
                           ("cell", "cell", "blue"),
                           ("contact_pos_a", "cp1", "orange"),
                           ("contact_pos_b", "cp2", "orange"),
                           ("contact_neg", "cn1", "orange"),
                           ("pcb", "pcb", "green"),
                           ("piezo", "piezo", "purple")):
    a.add(label, P[key], color=colour, joint="rigid")

os.makedirs(os.path.join(_ROOT, "out/mech"), exist_ok=True)
# KEEP "max" (y > 0) and look from the FRONT (-y), so the camera sees the CUT.
# Keeping y < 0 and looking from the front shows an intact outside face and
# reveals nothing — it renders perfectly and it is useless.
render(a, os.path.join(_ROOT, "out/mech/halo-puck-section-front.png"),
       section=("y", 0.0, "max"), view="front",
       title="halo puck — the 7.98 mm stack, square on")
render(a, os.path.join(_ROOT, "out/mech/halo-puck-section-quarter.png"),
       section=("y", 0.0, "max"), view=(14.0, -70.0),
       title="halo puck — the bayonet, the contacts and the bender, "
             "cut on the axis")
print("wrote out/mech/halo-puck-section-front.png and -quarter.png")
