"""mech.py — halo-battery-door-fdm

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no
adjectives. A number nobody measured stays absent.
"""

_RECORD = {'slug': 'halo-battery-door-fdm',
 'material': 'PC',
 'density_g_cm3': 1.2,
 'youngs_gpa': 2.4,
 'note': 'printed; cannot seal to IP67'}


def mech():
    return _RECORD
