# M09 — everything drawn back onto the photograph, and a judgement of what is real

*halo Replica, L1 PHOTOGRAPH METROLOGY lane, 2026-09-05.*

**SIDE NAMING:** FRONT = the COMPONENT side. O'Flynn's `backside-fullres.jpeg` **is** it.

**Artifact:** `evidence/E-L1-everything-on-the-photograph.png` — outline, hole, all
95 bright features numbered, the 5 blue packages, the nRF control box, the UWB can
rectangle. **Reproduce:** `tools/m_overlay_all.py --out-dir <dir> --tiles 9`,
which also writes **native-resolution** tiles, because a downsampled overlay
cannot answer the question it is being asked.

---

## THE JUDGEMENT — and it is labelled a judgement, not a measurement

Four native-resolution tiles were examined, covering roughly the top-centre,
left, right and bottom-left of the annulus — about 40 of the 95 features.
**What follows is my reading of pictures. It is not a measurement and must not be
quoted as one.**

| | judgement |
|---|---|
| land on something genuinely there | **~90 %** — metal terminations, gold pads, cans, olive and white chip capacitors, the big solder tabs |
| **one component counted twice** | **~0 %** — see the measurement below; this mode is essentially absent |
| on the grey rim material rather than a part | **~10–15 %** — measured proxy below |
| specular highlights on a fillet with nothing under them | **none clearly identified**, but I cannot exclude them at this resolution |

### Two of those are backed by a number rather than by my eye

**"One part counted twice" — essentially absent.** The failure mode would be a
two-terminal passive segmenting as its two bright terminations. A 0201's
terminations sit ~0.3–0.4 mm apart. Nearest-neighbour spacing over all 95:

| p5 | p10 | p25 | p50 |
|---|---|---|---|
| 0.614 mm | 0.671 mm | 0.727 mm | 0.840 mm |

**Nothing at all is closer than 0.45 mm**, and only 4 features (4 %) have a
neighbour inside 0.6 mm. The termination-splitting mode did not happen.

**"On the grey rim material" — 14 of 95.** M02 §8 established that a grey fibrous
material laps over the rim. Detections beyond 0.97 of the **local** edge radius:

| > 0.90 | > 0.93 | > 0.95 | **> 0.97** | max |
|---|---|---|---|---|
| 38 | 19 | 15 | **14** | **1.063** |

**One detection lies at 1.063 of the edge radius — outside the board entirely.**
All 14 are flagged `on_rim_material_suspect` in the handoff.

### What the pictures showed that the numbers did not

- The **nRF box fits the part exactly**; the control box around it is visibly
  larger, as intended.
- The **row of gold-terminated capacitors on the right gets one circle each** —
  no splitting, no merging.
- **Dark bodies are visibly absent**: the black "+AKN 847" IC, the "0561 1A8"
  package, the two small black diodes and the large black package at 9 o'clock
  all sit unmarked. The gap is exactly where M08 said it is.
- **Two clear false positives sit on the grey rim strip**, one in the bottom-left
  tile and one on the right — the same material as M02 §8, and the same 14 the
  radial test flags.
- **Genuine misses**: the two gold-ringed round parts and the large silver clip
  near the hole carry no marker. The clip abuts the hole's bright region and is
  absorbed by it.
- One blue-package detection is a **grey speckled strip**, not obviously a
  package — the 3.449 × 0.841 mm row. Flagged as sized but it should be treated
  as a feature, not a part.

## The outline, which I undersold in M07

The transferred outer outline follows the board through the flat, the notch and
both tangent regions — **a boundary derived from FCC photo 6, carried through a
homography fitted on interior landmarks, landing on a different photograph's
board edge, with no outline point ever fitted to.** An NCC of 0.6861 can be a
coincidence; a curve that lands like that cannot. **Cite this artifact whenever
`c_register`'s NCC is quoted.**

## Status

| # | quantity | verdict |
|---|---|---|
| 1 | do the detections land on real things | **JUDGEMENT: ~90 % yes** — my reading of four native-resolution tiles |
| 2 | one component counted twice | **MEASURED: essentially none** — nothing closer than 0.45 mm |
| 3 | detections on the grey rim material | **MEASURED: 14 of 95** beyond 0.97 of the local edge radius, one outside the board |
| 4 | specular-only detections | **CANNOT DETERMINE** — none identified, none excluded |
| 5 | dark IC bodies | **absent, as M08 states** — confirmed by eye |
