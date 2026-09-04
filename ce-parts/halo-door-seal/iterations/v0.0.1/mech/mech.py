"""mech.py — halo-door-seal

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no
adjectives. A number nobody measured stays absent.
"""

_RECORD = {'slug': 'halo-door-seal',
 'material': 'LSR70',
 'density_g_cm3': 1.15,
 'shore_a': 70,
 'source': 'liquid silicone rubber, 70 Shore A — a class, not a specific '
           'compound'}


def mech():
    return _RECORD
