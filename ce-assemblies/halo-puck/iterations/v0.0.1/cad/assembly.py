"""assembly.py — assembly:halo-puck.

Contract (TRIAD.md): `def build(doc, params=None) -> Assembly`.

NO LITERAL TRANSFORM APPEARS ANYWHERE, and none is needed: halo is a
concentric product with ONE datum (the axis of revolution and the lowest
point of the door's outer face, which is Apple's own drawing datum), and
every part in ce-parts/ is BUILT in that frame. So each placement here is
the identity — there is not a coordinate to get wrong. What HOLDS each part
is declared, and joints.json carries the same five joints with their
parameters and their reasons.
"""
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _design_path():
    """Walk up until design.py is found. The folder may be reached through
    `current/` (a symlink) or through `iterations/vX.Y.Z/`, so a fixed number
    of `..` is wrong for one of them."""
    d = _HERE
    for _ in range(8):
        p = os.path.join(d, "design.py")
        if os.path.isfile(p):
            return p
        d = os.path.dirname(d)
    raise FileNotFoundError("design.py not found above %s" % _HERE)


def _design():
    path = _design_path()
    spec = importlib.util.spec_from_file_location("halo_design", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(doc, params=None):
    return _design().build(fast=True)
