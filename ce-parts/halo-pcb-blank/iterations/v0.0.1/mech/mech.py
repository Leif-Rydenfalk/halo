"""mech.py — halo-pcb-blank

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no
adjectives. A number nobody measured stays absent.
"""

_RECORD = {'slug': 'halo-pcb-blank',
 'material': 'FR4',
 'density_g_cm3': 1.9,
 'thickness_mm': 0.6,
 'layers': 4,
 'source': 'JLCPCB 4-layer standard stackup; the copper is the electronics '
           "lane's"}


def mech():
    return _RECORD
