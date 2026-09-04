"""mech.py — halo-battery-contact

Contract (TRIAD.md): `def mech() -> dict`. Numbers with sources, no
adjectives. A number nobody measured stays absent.
"""

_RECORD = {'slug': 'halo-battery-contact',
 'material': 'C5191',
 'density_g_cm3': 8.8,
 'youngs_gpa': 110.0,
 'yield_mpa': 590,
 'source': 'C5191 phosphor bronze, spring temper — catalogue values, not a '
           'lot certificate',
 'spring': {'model': 'Euler-Bernoulli cantilever, k = 3EI/L^3',
            'L_mm': 6.074,
            'w_mm': 3.6,
            't_mm': 0.15,
            'k_N_per_mm': 1.491,
            'force_N_at_0p40': 0.596,
            'stress_MPa_at_0p40': 268.4,
            'caveat': 'w/L = 0.59, so the strip behaves partly as a plate '
                      'and the real rate is up to ~12 % higher '
                      '(1/(1-nu^2)). CALCULATED, never measured: the bench '
                      'measurement is an open item'}}


def mech():
    return _RECORD
