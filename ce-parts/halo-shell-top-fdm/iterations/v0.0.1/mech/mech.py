"""mech.py — halo-shell-top-fdm

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no
adjectives. A number nobody measured stays absent.
"""

_RECORD = {'slug': 'halo-shell-top-fdm',
 'material': 'PC',
 'density_g_cm3': 1.2,
 'youngs_gpa': 2.4,
 'note': 'printed; anisotropic, and the through-layer direction is the '
         'weak one'}


def mech():
    return _RECORD
