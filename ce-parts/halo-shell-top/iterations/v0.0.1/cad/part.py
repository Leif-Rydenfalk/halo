"""part.py — halo-shell-top

Contract (TRIAD.md): `def build(doc, params=None) -> Part`. The geometry is
parametric and its ONE source is the repo-root `design.py`, so no dimension
in halo is typed twice. This file resolves that file and calls `shell_top()`.
"""
import importlib.util
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                     *[".."] * 4))
_DESIGN = os.path.join(_ROOT, "design.py")


def _design():
    spec = importlib.util.spec_from_file_location("halo_design", _DESIGN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(doc, params=None):
    return _design().shell_top()
