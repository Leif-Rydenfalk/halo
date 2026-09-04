"""mech.py — halo-carrier

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no
adjectives. A number nobody measured stays absent.
"""

_RECORD = {'slug': 'halo-carrier',
 'material': 'LCP_LDS',
 'density_g_cm3': 1.61,
 'youngs_gpa': 12.0,
 'source': 'Vectra E840i LDS class (laser-direct-structuring grade); NOT a '
           'measured datum for a specific pellet — the grade is a design '
           "choice and the supplier's datasheet governs",
 'offers': [{'joint': 'bayonet',
             'to': 'part:halo-battery-door',
             'where': 'three feet at 0/120/240 deg, R12.90..13.40, top '
                      'face z=1.890'},
            {'joint': 'soldered',
             'to': 'part:halo-pcb-blank',
             'where': 'four LDS feed pads on the PCB seat at z=4.600'}]}


def mech():
    return _RECORD
