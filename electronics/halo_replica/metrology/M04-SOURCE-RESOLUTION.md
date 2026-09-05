# M04 — how much detail the FCC photographs actually contain

*halo Replica, L1 PHOTOGRAPH METROLOGY lane, 2026-09-05.*

**SIDE NAMING:** FRONT = the COMPONENT side (Apple's FCC caption). See M02.

**Why this exists.** M03 blamed the rim-pad CANNOT DETERMINE on resolution and
named one way out: re-render the FCC exhibit above the 150 dpi that
`CATALOG.md` records. That is only worth doing if there is more information in
the source than in the files we already hold — otherwise a resampler invents a
110 px rim band out of a 27 px one, the blob detector finds **more** candidates
**more** confidently from **no new evidence**, and the failure looks like
success on exactly the question we most want answered.

**Reproduce:**

```
tools/m_resolution_probe.py --image fcc-BCGA2187-internal-photo-6.jpg \
    --box 760,480,1150,870 --json metrology/resolution-probe-photo6-board.json
```

---

## 1. The fetch was attempted and REFUSED — recorded, not glossed

Three public endpoints, no account, no login, no form, nothing bought:

| endpoint | result |
|---|---|
| `fccid.io/BCGA2187/Internal-Photos/A2187-Internal-Photos-v1-0-5130978.pdf` | **HTTP 403** |
| `fcc.report/FCC-ID/BCGA2187/5130978.pdf` | **HTTP 403** |
| `apps.fcc.gov/eas/GetApplicationAttachment.html?id=5130978` | **HTTP 403** |

The PDF is not in this repo either — only the eight derived JPEGs. So
`pdfimages -list` could not be run on Apple's exhibit. **That question stays
open and is not claimed as answered.**

## 2. But the question it was asked to settle IS answered, without the PDF

Upsampling cannot create high spatial frequencies. So the files we hold can be
asked directly whether they carry the detail their pixel count implies.

`m_resolution_probe.py` takes the radially-averaged power spectrum of a region
and finds where the energy dies, then runs the identical measurement on the same
region deliberately destroyed to 1/2, 1/3, 1/4 and 1/6 resolution. **The
known-degraded ladder is what calibrates the number** — the absolute roll-off of
a JPEG means little on its own.

`fcc-BCGA2187-internal-photo-6.jpg`, 2134 × 1600:

| region | as held | /2 | /3 | /4 | /6 |
|---|---|---|---|---|---|
| **the board**, (760,480)-(1150,870) | 0.289 | **0.305** | 0.258 | 0.227 | 0.180 |
| the bottom rule, (400,1130)-(1400,1250) | 0.383 | 0.352 | 0.289 | 0.258 | 0.211 |

*(roll-off as a fraction of that image's own Nyquist)*

**Over the board, throwing away everything above half Nyquist costs nothing at
all — the /2 control comes out very slightly *better* than the original.** The
first step that costs measurable detail is /3.

> **The board region of a 2134 px-wide file carries the real detail of roughly
> 711–1067 px of width.** The board itself spans ~400 px there, so it holds
> perhaps 130–200 px of genuine board width. The rule region is sharper
> (~1067–2134 px), which is what high-contrast tick edges look like and is why
> the px/mm measurements in M02 are solid while the rim-pad count in M03 is not.

## 3. Consequence

**Do not re-render.** At best — if the exhibit embedded a perfectly sharp
2048 × 1536 image — extraction could gain a factor of ~2 over what we hold. But
the far more likely reading is that the source photograph is itself soft: the
orchestrator measured every embedded image in the five comparable FCC
internal-photo exhibits already in this repo, and **not one exceeds
2048 × 1536**, while our Apple JPEGs are *larger* at 2134 × 1600. A render
matched to the embedded pixels is what produces the otherwise-absurd 14.2 × 10.7
inch page that 2134 × 1600 at 150 dpi implies.

**A fact worth carrying beyond this lane:** FCC internal-photo exhibits in this
repo carry **220–401 ppi** (Chipolo 1370×1027 @ 316; eufy 2048×1536 @ 401;
UGREEN 1039×779 @ 220; moto tag 1456×970 @ 220; Pebblebee 793×1121 @ 96). Anyone
reaching for an FCC exhibit expecting to resolve fine detail should expect that
range and no more.

## 4. WHAT I DISCARDED — a verdict rule of mine that was backwards

`m_resolution_probe.py` first required `as_held > /2 > /4` and, when the /2
control came out *equal*, declared **"the probe cannot separate the controls, so
it cannot answer."** That was wrong, and wrong in the way that matters most:

> **If an image's real detail already dies below half its own Nyquist, then
> destroying everything above half Nyquist MUST cost nothing. The /2 control
> failing to separate is not the probe failing — it IS the answer.**

The /4 and /6 controls separated cleanly the whole time (0.227 and 0.180 against
0.289), which proves the probe works. I had built a tool that reported CANNOT
DETERMINE precisely when it had measured something, and I would have believed it
if I had not read the ladder. Fixed: the verdict now reads the *first* step that
costs detail, and only reports CANNOT DETERMINE when **no** step separates.

## 5. Status

| # | quantity | verdict |
|---|---|---|
| 1 | effective resolution of the board region, photo 6 | **MEASURED: ~711–1067 px of real width in a 2134 px file** |
| 2 | effective resolution of the rule region, photo 6 | **MEASURED: ~1067–2134 px** — the calibration is on the sharp part of the image |
| 3 | whether re-rendering the exhibit would help | **NO, on the evidence available.** Gain is bounded at ~2× in the best case and is probably zero |
| 4 | what Apple's exhibit actually embeds | **CANNOT DETERMINE** — all three public endpoints returned 403 and the PDF is not in this repo |
| 5 | M03's rim-pad CANNOT DETERMINE | **stands, with a measured reason attached** rather than an unexplored option hanging off it |
