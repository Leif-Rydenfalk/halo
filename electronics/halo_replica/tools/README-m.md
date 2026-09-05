# `m_*` — the L1 PHOTOGRAPH METROLOGY toolkit

Every tool: re-runnable, prints its inputs, writes raw results to JSON beside the
prose, and answers **PASS / FAIL / CANNOT DETERMINE** through its exit code
(0 / 1 / 2). A number that does not name the photograph, the scale basis and the
method is not a measurement and is not printed as one.

**SIDE NAMING, used everywhere in this lane:** FRONT = the **component** side,
per Apple's own FCC caption *"A2187 MLB - Front"*. O'Flynn's "frontside"
(battery contacts, NFC coil) is this project's **BACK**.

**Run the selftest before trusting any of it:** `python3 m_selftest.py` —
19 cases, synthetic ground truth and **four deliberate breaks**, exit 0/1.

| tool | what it answers |
|---|---|
| `m_ruler_calib.py` | px/mm from a steel rule's mm ticks, as a periodic comb over ~100 ticks. Gates: split-half, tick coverage, an independent 5-mm comb. |
| `m_scale_field.py` | is px/mm constant across the frame? Local pitch along each rule, cubic differentiated. |
| `m_scale_at.py` | px/mm **at a point**, by two routes that share no tick, rule, direction or path. The route disagreement **is** the uncertainty. |
| `m_outline_fit.py` | the board outline as fitted primitives — circle outside, superellipse for the hole — with published residuals. `--method halfmax` is the **named negative control**. |
| `m_silhouette.py` | diameter from area, with the threshold **swept**; the plateau is the result and no plateau means CANNOT DETERMINE. |
| `m_aspect_control.py` | is the *photograph* anisotropic? Asks a known-round object (the rule's punched hole). |
| `m_resolution_probe.py` | does the image hold the detail its pixel count implies? Spectrum roll-off against a known-degraded ladder. |
| `m_rim_pads.py` | counts rim features. `--mode differential` (default) is validated; `--mode blob` is **kept because it fails its positive control**. |
| `m_rim_unwrap.py` | unrolls the rim to a strip, normalised to the measured `r(θ)`, so features can be counted by eye and by algorithm independently. |
| `m_pad_registration.py` | do FRONT and BACK agree on rim feature positions? Searches the mirror axis, and builds the null through the **same** search. |
| `m_overlay.py` | draws a measured `r(θ)` back onto the photograph. **A number you have not looked at is a number you have not checked** — this is how the shadow trap was caught. |

## The three checks that could not fail, all mine, all caught here

Recorded because each looked fine from the outside and none would have shown up
in the output.

1. **A control that could not lose.** `m_rim_unwrap` permuted the *smoothed*
   signal, so the control was jagged where the real signal is smooth; the finder
   invented ~22 peaks from it and nothing could ever have beaten it.
   *The control must go through the same pipeline as the measurement.*
2. **A control that manufactured the property under test.** `m_rim_pads`
   permuted angular *columns*; a permuted column is a full-height stripe, and
   every stripe trivially satisfies "reaches the edge". It returned 46.8 against
   a real 26.
3. **A positive control that was too easy.** The clean synthetic rim has a
   differential noise of 1.8 luma; the real photograph measures 34.6. Passing on
   the clean one proved the detector's *logic* and nothing about this source.
   **This is the subtlest of the three, because passing feels like evidence.**

The generalisation: check the assumption a method shares with its own control,
not only the inputs they do not share.
