"""part.py — halo-pcb-blank

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. The geometry is
parametric and its ONE source is the repo-root `design.py`, so no dimension
in halo is typed twice. This file resolves that file and calls `pcb_blank()`.
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
    return _design().pcb_blank()
