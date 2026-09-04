"""compat.py — can these two interfaces actually join?

Contract (TRIAD.md): `def compatible(a_iface, b_iface) -> Verdict` —
PASS / FAIL / CANNOT DETERMINE, with the measured why. CANNOT DETERMINE is
the honest answer when a dimension is missing; never guess one.
"""


def compatible(a_iface, b_iface):
    return {"verdict": "CANNOT DETERMINE",
            "why": "sprung-contact: compat.py has no rule yet"}
