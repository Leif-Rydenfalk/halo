"""mech.py — halo-shell-top

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no
adjectives. A number nobody measured stays absent.
"""

_RECORD = {'slug': 'halo-shell-top',
 'material': 'PC',
 'density_g_cm3': 1.2,
 'youngs_gpa': 2.4,
 'poisson': 0.37,
 'source': "ce-cad cecad/fits.py MATERIALS['PC']; resin choice from "
           'research/07 §6.3 (Apple uses PC; it is the only common resin '
           'giving optical white, toughness at 0.8 mm and a diaphragm '
           'stiff enough to radiate)',
 'offers': [{'joint': 'glued',
             'to': 'part:halo-carrier',
             'where': 'the Ø27.90 bore, z 2.60..4.90'},
            {'joint': 'glued',
             'to': 'part:halo-piezo-7bb-20-3',
             'where': 'the flat internal land at z=6.550, Ø21.20'}]}


def mech():
    return _RECORD
