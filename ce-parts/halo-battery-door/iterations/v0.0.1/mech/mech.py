"""mech.py — halo-battery-door

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no
adjectives. A number nobody measured stays absent.
"""

_RECORD = {'slug': 'halo-battery-door',
 'material': 'SS301',
 'density_g_cm3': 7.9,
 'youngs_gpa': 193.0,
 'yield_mpa': 520,
 'source': "301 full-hard stainless strip, 0.30 mm. The AirTag's cover "
           'thickness and alloy are UNMEASURED (research/07 §2.3) — this '
           "is halo's choice, not a copy",
 'offers': [{'joint': 'bayonet',
             'to': 'part:halo-carrier',
             'where': 'three tabs at 0/120/240 deg, Ø25.55..26.60, z '
                      '1.890..2.190'}]}


def mech():
    return _RECORD
