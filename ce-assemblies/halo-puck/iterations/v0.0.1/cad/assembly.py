"""assembly.py — resolve the bom, walk the joints, place by mate().

Contract (TRIAD.md): `def build(doc, params=None) -> Assembly`. NO literal
transforms for joined parts — placement comes from the connections, or it is
a lie.
"""


def build(doc, params=None):
    raise NotImplementedError("halo-puck: no assembly yet")
