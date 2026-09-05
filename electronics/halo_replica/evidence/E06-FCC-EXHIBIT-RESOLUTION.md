# E06 — how much detail an FCC internal-photo exhibit actually carries

*halo Replica lane (orchestrator), 2026-09-05. A measured prior, taken from five documents
already on disk, that changes the expected value of a proposed fetch from "high" to "near
zero" — and would have made a failure look like a success.*

## The proposal

Lane L1 could not count the AirTag's rim solder pads: 15 candidates on the front against a
control mean of 19.5, 13 on the back against 23.0. **The count loses to its own control in
both photographs.** Its proposed unblocking step was to re-render the source FCC exhibit at
600 dpi, since `CATALOG.md` records our eight JPEGs as rendered at **150 dpi** — nominally a
4× linear gain, taking a 1 mm tear-off tab from ~15 px to ~60 px.

That is the right instinct and it was correctly escalated rather than taken unilaterally.

## The measurement that undercuts it

`pdfimages -list` on the five competitor FCC internal-photo exhibits already in this repo
(`images/commercial/`). poppler is installed locally, so this cost no network and no quota:

| exhibit | largest embedded image | effective ppi |
|---|---|---|
| eufy SmartTrack Link | **2048 × 1536** | 401 |
| Chipolo ONE Spot | 1370 × 1027 | 316 |
| moto tag | 1456 × 970 | 220 |
| UGREEN Smart Finder | 1039 × 779 | 220 |
| Pebblebee Clip | 793 × 1121 | 96 |

**Not one exceeds 2048 × 1536. Our Apple JPEGs are 2134 × 1600 — larger than every embedded
image in all five comparable exhibits, and a clean 4:3 like most of them.**

The likely reading: whoever produced our eight JPEGs already extracted them at the embedded
native size, and the "150 dpi" in `CATALOG.md` describes the page-render setting rather than
the information content. 2134 × 1600 at 150 dpi implies a 14.2 × 10.7 inch page, which is not
a real page size — it is the number you get when a render was matched to the embedded pixels.

## Why this mattered enough to write down

**The failure would have looked like success, precisely on the question we most want
answered.** Render a 27 px rim band at 4× and a resampler produces a smooth, well-separated
110 px band — exactly the signal L1's blob detector is built to find. It would have returned
*more* rim candidates with *higher* confidence from **no new evidence at all**, and there is
nothing in the output of that run that would have looked wrong.

This is the same family as the two defects already recorded today — a check that cannot fail
(`E05`, and L1's control that manufactured the property under test) — but arriving from a
third direction: not a bad control, but a **bad input dressed as a better one**.

## What was authorised, and how

The fetch **is** authorised: a US regulatory filing in the public FCC database is a primary
public record, it contacts nobody, needs no account, and buys nothing, and equivalent exhibits
for six competitors are already in this repo. But with the order of operations inverted:

1. `pdfimages -list` **first**.
2. **If ≤ 2134 × 1600, stop and do not render.** That is a *finished* answer — "the rim pad
   count is CANNOT DETERMINE at the best resolution the primary source contains" closes the
   question, where "CANNOT DETERMINE from these JPEGs" leaves it hanging on an unexplored
   option.
3. Only if genuinely larger, use `pdfimages -j` to extract the **stored** JPEGs rather than
   rendering pages at a dpi. Extraction gives the actual pixels; rendering resamples them
   through a rasteriser and can only lose.

Plus: new filenames, never overwriting the 150 dpi originals — L1 carries an image sha256 on
every output, and overwriting the inputs would silently invalidate the provenance of every
measurement this lane has published.

## The general fact, worth keeping

**FCC internal-photo exhibits carry roughly 220–400 ppi and about 1–2 megapixels.** Anyone in
this project reaching for an FCC exhibit expecting to resolve fine detail should know that
before they plan around it. They are excellent for *scale* — they contain steel rules, which
is why photo 6 gave us a datum at all — and poor for *fine geometry*.
