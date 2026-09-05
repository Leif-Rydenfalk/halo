# R18 — is the coherent misfit a DOME? The test cannot see one about the board centre, and says so

*halo Replica, lane L2, 2026-09-05. Extends [R11](R11-R09-WAS-WRONG-A-NULL-WITHOUT-A-DETECTION-LIMIT.md); complements [R17](R17-THE-RULE-EDGES-ARE-STRAIGHT.md).*

R11 left the smooth coherent registration misfit with three candidate causes. R17 bounded
lens distortion in the target frames to under ~0.2 px of bow along the bottom rule. This
file attacks the remaining pair, because they make **different geometric predictions**:

- **A board that is not flat** displaces features **radially about the BOARD's own centre**,
  growing with distance from it.
- **Optics** displace features **radially about the IMAGE centre**, which is somewhere else.
- **A difference between two physical boards** has no reason to be radial about anything.

So: decompose each landmark's residual into radial and tangential parts about each candidate
centre and ask whether the radial part grows with radius.

## Measured

| face | centre | corr(radial, r) | z | radial px | tangential px | **smallest dome it could see** |
|---|---|---|---|---|---|---|
| FRONT (274 lm) | **board centre** | +0.005 | +0.0 | 1.049 | 0.799 | **NONE** |
| FRONT | target image centre | −0.051 | −1.0 | 0.886 | 0.977 | 0.923 px |
| FRONT | crop centre | +0.005 | +0.2 | 1.050 | 0.798 | **NONE** |
| BACK (192 lm) | **board centre** | +0.097 | +1.7 | 1.255 | 1.126 | 1.180 px |
| BACK | **target image centre** | **+0.298** | **+3.4** | 1.274 | 1.103 | **0.135 px** |
| BACK | crop centre | +0.097 | +1.6 | 1.255 | 1.126 | 1.180 px |

## The result that matters is the last column

**About the BOARD centre, on the FRONT, the test cannot detect a dome AT ALL** — a dome
injected at the *full* residual RMS still fails to clear the null. "detects a dome ≥ NONE"
is not a null result; it is the test reporting that it is blind.

Without that column this file would have said *"corr +0.005, z = +0.0 — no dome"* and it
would have meant **nothing**. That is the fifth time today this lane has come close to
publishing a confident negative from a check that could not have contradicted it, and the
first time the instrument caught it before the document did.

**Why it is blind:** the landmarks sit in an annulus, `0.42 R` to `0.95 R`. A statistic that
looks for radial displacement *growing with radius* has almost no lever arm over so narrow a
range of radii. This is a geometric limit of where the board has features, not a bug, and no
amount of extra landmarks fixes it.

## What can be said

- **A dome about the board centre: CANNOT DETERMINE, on both faces.** The front test is
  blind; the back's bound is a weak 1.180 px. **The board-flatness hypothesis is untouched
  and remains open.**
- **BACK, about photo 7's image centre: a weak but real radial trend**, corr +0.298 at
  z = +3.4, with genuine power (a 0.135 px dome would have been seen). Marginal — just over
  the threshold — and it sits awkwardly beside R17, which found photo 7's usable rule edge
  straight to 0.123 px. Both can be true: R17 measures the lens *where the rule is*, this
  measures leftover structure *where the board is*, and they are different parts of the field.
- **FRONT, about any centre: CANNOT DETERMINE**, with bounds where they exist.

## What this test can never see, whatever the power

**A uniform radial term is absorbed by the homography before these residuals exist.** The
fit has eight parameters and will happily take up any distortion it can represent. So this
statistic only ever sees the radial structure a homography *could not* absorb. A real dome
that happens to be well-approximated projectively is invisible here by construction, and no
detection limit rescues that.

## Consequence

R11's candidates stand as: **lens distortion bounded small (R17)**, **a non-flat board
untested and open (this file)**, **two different physical boards untested and open**.
Downstream numbers are unchanged: **FRONT 0.181 mm RMS / 0.288 mm p95, BACK 1.026 / 1.703.**

The only one of the three that a measurement on this machine could still settle is the
board-flatness question, and it would need landmarks spanning a wider range of radii than
this board provides — or a photograph of the board's edge-on profile, which the catalogue
does not contain.

## Controls

`selftest` **12/12**. The statistic finds a synthetic dome about the board centre at
corr +0.868, z = +11.9 (radial 0.802 px against tangential 0.156 px), stays at its null on a
field with no radial structure (z = +1.2), **and that null carries a detection limit rather
than a bare "no"** — a 0.406 px dome would have been seen against a 0.812 px residual RMS.

```
tools/c_register.py validate --folds 2 --step 8 --search 6
tools/c_register.py validate --source oflynn-back --target fcc7-back --folds 2 --step 8 --search 6
tools/c_register.py selftest
```
