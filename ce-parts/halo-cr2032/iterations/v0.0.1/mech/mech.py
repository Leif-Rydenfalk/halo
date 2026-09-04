"""mech.py — halo-cr2032

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no
adjectives. A number nobody measured stays absent.
"""

_RECORD = {'slug': 'halo-cr2032',
 'material': 'CR2032',
 'density_g_cm3': 2.985,
 'mass_g': 3.0,
 'capacity_mah': 220,
 'voltage_v': 3.0,
 'source': 'Maxell CR2032 datasheet (research/07 §2.2)'}


def mech():
    return _RECORD
