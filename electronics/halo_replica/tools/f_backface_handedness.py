"""f_backface_handedness — is the BACK face mirrored, or rotated?

    python3 electronics/halo_replica/tools/f_backface_handedness.py
    ... --break-rotate 40   replace photo 7's angles with photo 6's ROTATED
                            by 40 deg; the mirror verdict must then not stand
    ... --break-tol 0.2     tighten the tolerance until the answer is refused

Exit 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

---------------------------------------------------------------------------
THE QUESTION, AND WHY IT IS NOT A CONVENTION
---------------------------------------------------------------------------
The front handoff is measured in O'Flynn's `backside-fullres.jpeg` (Apple's
COMPONENT side) and the back handoff in his `frontside-fullres.jpeg` (Apple's
BATTERY side). Each says "+x right, +y DOWN" -- IN ITS OWN PHOTOGRAPH. A board
has ONE global frame, defined looking at the top, so one of those two is
mirrored relative to it and NEITHER FILE SAYS WHICH.

Getting it wrong puts all 43 back-face pads at (-x, y) instead of (x, y). The
board still builds. The DRC still passes. The render still looks like a
board. That is the failure this file exists to refuse: a silent handedness
error is indistinguishable from correct work in every output except a
comparison nobody would think to run.

So it is MEASURED, from a quantity that was already on disk and was not
produced for this purpose.

---------------------------------------------------------------------------
THE TEST, AND WHY IT DISCRIMINATES
---------------------------------------------------------------------------
`metrology/outline-fit-photo6.json` (FCC "MLB - Front") and
`outline-fit-photo7.json` (FCC "MLB - Back") each report TWO angles of the
same physical board's outline in their own image frame: the bearing where the
caliper width is widest and where it is narrowest. The board is NOT round --
it carries four straight chords -- so these angles are real features of the
part, not artefacts.

Two hypotheses make OPPOSITE predictions, and this is the whole point:

  MIRROR about the vertical axis   theta -> 180 - theta, for BOTH angles
  PURE ROTATION by some unknown k  theta -> theta + k, THE SAME k for both

A rotation is free to fit ONE angle exactly -- it has a free parameter. It
can only fit BOTH if the two implied k agree. So the test is: does the
mirror reproduce both angles, and does the rotation's k disagree between
them? A hypothesis that cannot fail is not a hypothesis, and the rotation
branch is here precisely so this one can.

CROSS-CHECK, on a frame this file did not choose: the largest chord in
`board/outline/outline-fit-oflynn.json` -- fitted in O'Flynn's FRONT frame,
by a different tool, from a different photograph -- has its normal at
166.98 deg, against photo 6's 166 deg. The homography between the two frames
therefore preserves bearing to about a degree, which is what licenses
comparing photo 6's angles with photo 7's at all.

---------------------------------------------------------------------------
WHAT THIS DOES NOT SETTLE
---------------------------------------------------------------------------
It settles the HANDEDNESS. It does not settle a residual rotation of a degree
or two, and it says nothing about the two boards being different part numbers
(920-08283-01 vs 820-01736-A) -- the back handoff raises that itself and it
is not closed here.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
P6 = os.path.join(REPLICA, "metrology", "outline-fit-photo6.json")
P7 = os.path.join(REPLICA, "metrology", "outline-fit-photo7.json")
OFLYNN = os.path.join(REPLICA, "board", "outline", "outline-fit-oflynn.json")
OUT = os.path.join(REPLICA, "metrology", "backface-handedness.json")

TOL_DEG = 3.0      # the outline fits quote a 6.7-7.3 % caliper spread and
                   # sample at 0.25 deg; 3 deg is a few sample steps and is
                   # far tighter than the 90 deg the two hypotheses differ by.


def _ang(a):
    return a % 180.0


def _sep(a, b):
    return abs(((a - b + 90.0) % 180.0) - 90.0)


def main():
    argv = sys.argv[1:]
    tol = TOL_DEG
    if "--break-tol" in argv:
        tol = float(argv[argv.index("--break-tol") + 1])
    # THE NEGATIVE CONTROL, AND THE ONE IT REPLACED.
    # The first version of this control swapped the two files' angles. That
    # control was VOID and was watched being void: a reflection is its own
    # inverse, so swapping the sides is still a mirror and the tool returned
    # MIRROR both ways -- an assertion agreeing with itself. This one
    # SYNTHESISES a back face that is photo 6 ROTATED, which is the exact
    # hypothesis the tool claims it can rule out. If MIRROR still comes back,
    # the discrimination is fake.
    rotate = None
    if "--break-rotate" in argv:
        rotate = float(argv[argv.index("--break-rotate") + 1])
    swap = False

    f6, f7 = json.load(open(P6)), json.load(open(P7))
    front = {"widest": f6["outer"]["widest_phi_deg"],
             "narrowest": f6["outer"]["narrowest_phi_deg"]}
    back = {"widest": f7["outer"]["widest_phi_deg"],
            "narrowest": f7["outer"]["narrowest_phi_deg"]}
    if rotate is not None:
        back = {k: (v + rotate) % 180.0 for k, v in front.items()}

    mirror_err = {k: _sep(_ang(180.0 - front[k]), _ang(back[k]))
                  for k in front}
    rot_k = {k: (back[k] - front[k]) % 180.0 for k in front}
    rot_disagreement = _sep(rot_k["widest"], rot_k["narrowest"])

    ch = max(json.load(open(OFLYNN))["outer"]["chords"],
             key=lambda c: c["chord_span_mm"])
    cross = _sep(ch["normal_deg"], front["widest"])

    mirror_ok = all(v <= tol for v in mirror_err.values())
    rot_ok = rot_disagreement <= tol

    print("f_backface_handedness")
    print("  photo 6 (Apple MLB-Front): widest %.1f deg, narrowest %.1f deg"
          % (front["widest"], front["narrowest"]))
    print("  photo 7 (Apple MLB-Back) : widest %.1f deg, narrowest %.1f deg"
          % (back["widest"], back["narrowest"]))
    print("  tolerance %.2f deg%s"
          % (tol, "   [--break-rotate %.1f ACTIVE: photo 7 REPLACED by "
                  "photo 6 rotated]" % rotate if rotate is not None else ""))
    print("  MIRROR   theta -> 180 - theta : widest err %.2f, narrowest err "
          "%.2f  -> %s" % (mirror_err["widest"], mirror_err["narrowest"],
                           "FITS BOTH" if mirror_ok else "DOES NOT FIT"))
    print("  ROTATION theta -> theta + k   : k = %.1f from widest, %.1f from "
          "narrowest, disagreement %.2f deg -> %s"
          % (rot_k["widest"], rot_k["narrowest"], rot_disagreement,
             "consistent" if rot_ok else "INCONSISTENT, so ruled out"))
    print("  cross-check, O'Flynn front frame's largest chord normal %.2f "
          "deg vs photo 6's %.1f: %.2f deg apart"
          % (ch["normal_deg"], front["widest"], cross))

    if mirror_ok and not rot_ok:
        verdict, code = "MIRROR", 0
        print("  VERDICT MIRROR. The back-face frame is the front's reflected "
              "about the vertical axis: board_x = -x_back, board_y = +y_back.")
    elif rot_ok and not mirror_ok:
        verdict, code = "ROTATION", 1
        print("  VERDICT ROTATION — this REFUTES what pcb/board.py draws.")
    else:
        verdict, code = "CANNOT DETERMINE", 2
        print("  VERDICT CANNOT DETERMINE — %s. Not a soft pass: the back "
              "face must not be placed until this is settled."
              % ("both hypotheses fit, so the test does not discriminate"
                 if mirror_ok else "neither hypothesis fits"))

    if rotate is None and tol == TOL_DEG:
        json.dump({
            "tool": "tools/f_backface_handedness.py",
            "verdict": verdict,
            "transform": "board_x = -x_back, board_y = +y_back"
                         if verdict == "MIRROR" else None,
            "inputs": {"photo6": front, "photo7": back,
                       "source6": os.path.relpath(P6, REPLICA),
                       "source7": os.path.relpath(P7, REPLICA)},
            "mirror_residual_deg": mirror_err,
            "rotation_k_deg": rot_k,
            "rotation_disagreement_deg": rot_disagreement,
            "tolerance_deg": tol,
            "cross_check": {
                "what": "largest chord normal in the O'Flynn FRONT frame vs "
                        "photo 6's widest bearing — licenses comparing the "
                        "two FCC frames' angles at all",
                "chord_normal_deg": ch["normal_deg"],
                "photo6_widest_deg": front["widest"],
                "separation_deg": cross,
            },
            "what_this_does_not_settle": [
                "a residual rotation of a degree or two",
                "that the two FCC photographs are of the same part number as "
                "O'Flynn's board — 920-08283-01 vs 820-01736-A, raised by "
                "the back handoff itself and not closed here",
            ],
        }, open(OUT, "w"), indent=1)
        print("  wrote %s" % OUT)
    return code


sys.exit(main())
