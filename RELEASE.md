# RELEASE — halo release dossier

*The one page that says what halo is, what is proven, what is not, and where every artifact is.
Started 2026-09-03 by research lane A at Leif's request ("start creating release docs and stuff
like for the microduck but for our airtag project"). Modelled on `ce-designs/microduck`'s
RELEASE/STATUS/BOM set.*

**Read it in a browser:** `python3 tools/docs_server.py 8891` → <http://127.0.0.1:8891/>
(renders every dossier, turns `research/sources.tsv` into a sortable table, and contact-sheets
`images/airtag/`). Declared in `ceapp.toml` `[launch.targets.docs]`, so the launchpad can start it.

**Standing rule, inherited from ce-workshop:** nothing on this page is claimed without a named
artifact. Three verdicts — **PASS / FAIL / CANNOT DETERMINE** — and CANNOT DETERMINE is never a
soft pass.

---

## 1. What halo is

An open-source, cheaper-to-manufacture copy of the Apple AirTag's internals, designed as an
**embeddable circuit block** rather than only a puck, so it can be dropped into any board in any
outline. Leif's own use is room-scale **relative** positioning between his sensors for Twinton.
Full statement of intent: [`GOAL.md`](GOAL.md). Product spec: [`SPEC.md`](SPEC.md).

**The finding that shapes the project** (research lane A): the AirTag is ~95 % catalogue parts
wrapped around a CR2032. Exactly **one** component is unobtainable — Apple's **U1** UWB chip.
See [`docs/REFERENCE-TEARDOWN.md`](docs/REFERENCE-TEARDOWN.md).

---

## 2. Release rungs — what "done" means

Eleven artifacts define done (`MISSION.md`). Their state today:

| # | rung | verdict | proof |
|---|---|---|---|
| 1 | **Know the copy target** — every chip, pin, antenna, contact and mechanism inside the AirTag | **PASS** | [`research/01-airtag-hardware.md`](research/01-airtag-hardware.md) (416 lines, exhaustive components table + function map), [`docs/REFERENCE-TEARDOWN.md`](docs/REFERENCE-TEARDOWN.md), 7 archived primary pages `research/fetched/A-*`, 15 photos in `images/airtag/` |
| 2 | **Know the network** — Find My advertisement format, key rotation, how a non-Apple board joins | **PASS** | [`research/02-findmy-protocol-and-openhaystack.md`](research/02-findmy-protocol-and-openhaystack.md) (lane B) |
| 3 | **Know the field** — existing open tag PCBs; commercial clones and what is in them | **PASS (D)** / running (C) | [`research/04-commercial-tags-and-clones.md`](research/04-commercial-tags-and-clones.md); `research/03-open-hardware-tag-designs.md` |
| 4 | **Know the law** — IP, DULT, FCC/CE, Reese's Law, licensing | **PASS** | [`research/06-legal-ip-certification-safety.md`](research/06-legal-ip-certification-safety.md) (lane F, 867 lines, 30-item checklist), [`docs/ANTI-STALKING.md`](docs/ANTI-STALKING.md) |
| 5 | **Substitution map + cost** — every AirTag function → a sourceable part, BOM at 10/100/1k/10k | running (E) | `spec/bom-candidates.json` |
| 6 | **Local positioning answer** — can a sourceable UWB (or BLE channel sounding) do peer-to-peer ranging | running (H) | `spec/positioning-candidates.json` |
| 7 | **Embeddable block rules** — KiCad hierarchical sheet, footprints, antenna keep-out, module variant | running (I) | — |
| 8 | **Mechanical** — enclosure, speaker, battery door | running (G) | — |
| 9 | **Schematic → simulated → laid out → verified** | not started | — |
| 10 | **Factory release pack** — Gerbers, BOM, CPL, DFM, quote | not started | — |
| 11 | **`part:halo-core` on the triad shelf** | not started | — |

**Honest summary: this is a research release, not a hardware release.** Rungs 1–4 are done and
evidenced. Nothing has been laid out, simulated, fabricated or measured. No board exists.

---

## 3. Decisions taken

From [`DECISIONS.md`](DECISIONS.md):

- **D1** two variants — `halo-core` (BLE-only) and `halo-uwb` (peer ranging)
- **D2** no Bluetooth word mark
- **D3** press-and-twist battery door (Reese's Law child safety)
- **D4** licence split: CERN-OHL-S (hardware) / AGPL / Apache / CC-BY-SA
- **D5** clean-room, **no MFi enrolment**

---

## 4. The two known gaps (named, not glossed)

GOAL.md requires that anything unreproducible is written down. There are exactly two, and both are
commercial/IP walls rather than engineering failures:

1. **Apple-side Precision Finding.** The U1 is Apple-custom silicon (die `TMKA75`, TSMC 16 nm, USI
   SiP) and is never sold. A third-party UWB chip gives **peer-to-peer** ranging — which is what
   Leif actually needs — but not Apple's Precision Finding UI. Lane H settles the substitute.
2. **Appearing in the stock Find My app.** That needs a per-unit Apple **Token** pre-burned at an
   MFi factory. D5 rules out MFi, so halo rides the **unregistered** OpenHaystack path: findable
   by the network, not listed in Apple's own app. Lane D calls this "Door 2".

---

## 5. Document map

| document | what it answers |
|---|---|
| [`GOAL.md`](GOAL.md) | why halo exists, in Leif's words |
| [`MISSION.md`](MISSION.md) | the eleven artifacts that define done |
| [`SPEC.md`](SPEC.md) | the product specification |
| [`STATUS.md`](STATUS.md) | live lane-by-lane state |
| [`DECISIONS.md`](DECISIONS.md) | decisions taken and why |
| [`TOOLCHAIN.md`](TOOLCHAIN.md) | the tools this repo needs and their state |
| **[`docs/REFERENCE-TEARDOWN.md`](docs/REFERENCE-TEARDOWN.md)** | **the copy target — every part inside an AirTag, with 1:1 / SUB / GAP verdicts** |
| [`docs/ANTI-STALKING.md`](docs/ANTI-STALKING.md) | DULT behaviour designed in, not bolted on |
| `research/01…09` | the research dossiers, one per lane |
| `research/sources.tsv` | every source every lane used (lane, url, title, date, note) |
| `research/fetched/` | raw text of the important pages, so the repo survives the sites vanishing |
| `images/airtag/` + `CATALOG.md` | teardown and FCC photographs, with licences |

---

## 6. Evidence hygiene

- Every claim in a dossier carries a source link and a fetch date.
- Primary sources are archived as text under `research/fetched/` so the repo does not depend on
  third-party sites staying up.
- Images are only redistributed where the licence permits: Colin O'Flynn's PCB photographs are
  **CC-BY-4.0** (attributed), the FCC BCGA2187 internal photos are **US public records**. iFixit,
  Creative Electron X-rays and Adam Catley's figures are **linked, not copied** — see
  `images/airtag/CATALOG.md`.
- Where nobody has published a number, the dossiers say **CANNOT DETERMINE** and name what would
  settle it. There are no invented part numbers and no invented prices in this repo.

---

## 7. What happens next

`SPEC.md` → schematic → simulate (ce-spice / ce-rf) → layout (ce-pcb) → verify → factory release
pack. The toolchain lanes T1–T6 are building the ce-workshop capabilities that make each of those
steps a measured PASS rather than an assertion.
