"""mech.py — halo-piezo-7bb-20-3

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no
adjectives. A number nobody measured stays absent.
"""

_RECORD = {'slug': 'halo-piezo-7bb-20-3',
 'material': 'BRASS',
 'brass_t_mm': 0.12,
 'pzt_t_mm': 0.1,
 'pzt_d_mm': 14.0,
 'resonance_hz': 3600,
 'impedance_ohm': 500,
 'source': 'Murata 7BB-20-3 datasheet, via research/07 §4.2'}


def mech():
    return _RECORD
