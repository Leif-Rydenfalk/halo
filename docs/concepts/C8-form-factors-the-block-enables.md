# C8 — Form factors the embeddable block enables — and the one rule that decides each

*A card, a sticker, a bolt-on asset tag and a solder-down module are four different products, and DULT's own applicability test — not the electronics — is what changes between them.*

**Verdict: PLAUSIBLE** — The mechanism that makes any of these possible is measured: a KiCad 10 design block carried 9 footprints and 27 routed segments into a host of a different outline with worst pairwise error 0.000000 mm and the host's DRC clean. What is not demonstrated is any one of these four boards existing. The engineering per variant is real but bounded, and the surprising part is that the binding constraint is a compliance threshold rather than a millimetre.

Family `product` · value 4/5 against effort 2/5 · part of the halo concept portfolio, `docs/concepts/README.md`.

## What it is

GOAL.md deliverable 2 says anyone should be able to drop halo's circuit into their own board in any outline. D16 proved the mechanism and found its limit: a design block carries schematic AND routed copper, but it carries no design rules, so the antenna keep-out has to travel as a document the integrator reads.

That makes the interesting question not 'can the circuit move' — it can — but 'what changes when it does'. Four shapes are worth naming, and each is a different product with a different wall.

THE CARD. Credit-card outline, 85.6 x 54 mm, in a wallet or a passport sleeve. Electrically the easiest of the four: the board is larger than the D37.31 mm antenna keep-out in both dimensions, so the antenna problem that dominates the D26 mm puck simply goes away. The wall is the cell — a CR2032 is 3.2 mm and a card is not. A CR2016 (1.6 mm, about half the capacity) or a thin prismatic cell is the trade, and the battery-life number halves with it.

THE STICKER. A flexible label with a printed antenna and a thin flat cell, adhered to an asset. This is the one that does not work, and the reason is not electrical. DULT REQUIRES a sound maker at 60 Phon at 25 cm for any accessory small enough to hide, and a sticker cannot carry one. There is no thin-film transducer at that loudness. A sticker is therefore either non-compliant — which docs/ANTI-STALKING.md refuses on principle, not on convenience — or it is not a location tracker at all, and advertises only on a private network with no crowd-finding function. Both of those are honest answers; a compliant crowd-finding sticker is not available.

THE BOLT-ON ASSET TAG. An IP67 puck with a screw boss or a cable-tie slot, for a pallet, a pump, a length of pipe. This is the one where the enclosure stops fighting the electronics: give up Apple's 7.98 mm and a CR2450 (620 mAh) or CR2477 (1000 mAh) walks in, along with a bigger antenna and a real acoustic cavity for the sounder. It is the shape Leif's own digital twin actually wants, and it is the least like an AirTag.

THE SOLDER-DOWN MODULE, inside someone else's product. This is the form factor where the rules get EASIER rather than harder, and it is worth reading DULT section 2.1 carefully to see why: the applicability test asks about the accessory's own size, and an accessory larger than 30 cm in one dimension, or 18 x 13 cm in two, or 250 cm3 in volume, is 'easily discoverable' and the anti-stalking requirements become RECOMMENDED rather than REQUIRED. A halo block inside a bicycle, a toolbox, a robot or a machine skid is over that line. The sounder, the button and the whole DULT transport stop being mandatory — which is the largest single simplification available anywhere in this project.

## Why it beats the alternative

Against buying a module: D14 measured that no nRF54L module today is both certified and castellated. The Raytac part is certified but land-grid, so a hobbyist cannot hand-solder it; the Minew part is castellated but uncertified, which is strictly worse than bare silicon because it costs more and carries no grant. Publishing the block is the only route that exists.

Against re-laying the copper in every host, which was lane C's original assumption: measured wrong. The routed antenna travels.

Against Apple: there is nothing to compare. An AirTag is one shape and it is not for sale as a circuit.

## The numbers

| quantity | value | where it comes from |
|---|---|---|
| Design block transfer into a different host outline | **worst pairwise footprint error 0.000000 mm, rotations unchanged, host DRC 0 and 0** | DECISIONS.md D16, lane T5 measurement 2026-09-04 |
| What the block cannot carry | **design rules and the symbol library — so the keep-out ships as a one-page document** | DECISIONS.md D16 |
| The keep-out that has to travel as words | **D37.31 mm, no metal above or below; antenna end on the host outline with 16 x 6 mm clear on every layer** | SPEC.md section 4 (Apple's own callout); research/09 section 4.2 harmonised across five vendors |
| DULT applicability threshold — above this the sounder becomes RECOMMENDED, not REQUIRED | **30 cm in one dimension, or 18 x 13 cm in two, or 250 cm3** | draft-ietf-dult-accessory-protocol-00 section 2.1, quoted research/02 section 5.1 |
| Proposed module pinout, already worked out | **24 pads: 8 GND, 16 signal, never more than three signals between grounds so a 2-layer host can route it** | research/09 section 6.3 |
| Cell options as the shell grows | **CR2016 ~90 mAh / 1.6 mm; CR2032 235 mAh / 3.2 mm; CR2450 ~620 mAh / 5.0 mm; CR2477 ~1000 mAh / 7.7 mm** | CR2032 figure is the Energizer datasheet used by ce-spice; the others are catalogue nominals and are re-measured in C6 |

## The evidence

| claim | source | date | confidence |
|---|---|---|---|
| A KiCad 10 design block is a directory holding a schematic, a BOARD FRAGMENT and a JSON descriptor, and the layout is first class | DECISIONS.md D16; format read out of the KiCad library's own error strings by lane T5 | 2026-09-04 | primary, measured on this machine |
| Block applied into a host of a different outline, offset in both axes: worst pairwise footprint error 0.000000 mm, host DRC clean at 0 and 0 | DECISIONS.md D16 | 2026-09-04 | primary, measured |
| No nRF54L module today is both certified and castellated; certified module route costs +$1.16/unit | DECISIONS.md D14, from vendor drawings read directly (Raytac AN54LQ, Minew ME54BS11, u-blox NORA-B2) | 2026-09-03 | primary |
| DULT is REQUIRED for anything small and not easily discoverable, and the thresholds are 30 cm / 18x13 cm / 250 cm3 | draft-ietf-dult-accessory-protocol-00 section 2.1, archived research/fetched/B-draft-ietf-dult-*.txt | fetched 2026-09-03 | primary |
| DULT requires a sound maker at minimum 60 Phon peak loudness (ISO 532-1:2017) measured 25 cm from the accessory in free space | draft-ietf-dult-accessory-protocol-00 section 3.13.3 | fetched 2026-09-03 | primary |
| At D20 mm, thin and high-frequency are mutually exclusive: every 6.3-7.2 kHz element checked across three manufacturers measures 0.42-0.43 mm; elements in the 0.15-0.30 mm window all land at 3.6-4.2 kHz | DECISIONS.md D20, nine candidates verified against manufacturer mechanical drawings | 2026-09-04 | primary |
| Under 47 CFR 15.212 a certified module carries its own radio grant, so soldering it into any host outline does not disturb the grant — but the host must still be tested as an unintentional radiator | research/06 section 5.1, 47 CFR 15.212 fetched from law.cornell.edu | fetched 2026-09-03 | primary |

**What is NOT established here, stated so nobody inherits it as a fact:**

- That a card-outline board with a CR2016 actually meets the 60 Phon sounder requirement. The bender is 0.21 mm and fits, but a card has no acoustic cavity and the shell-as-diaphragm trick that D11a relies on has nowhere to happen. This is a bench measurement, and it is the card's real risk — not the battery.
- Whether a thin-film or electroactive-polymer transducer exists that could make a compliant sticker. This lane found none and did not exhaust the search. A single counterexample would reopen the sticker.
- The CR2450 and CR2477 capacities quoted above are catalogue nominals carried forward, not datasheet figures read in this lane. C6 re-measures them.

## What it costs

| dimension | cost |
|---|---|
| money | $0 for the block itself — it is a directory in the repository. Per variant: one board spin ($6-30 of PCB) plus the cell and enclosure delta. The bolt-on tag's cell delta is roughly +$0.30-0.60 at volume; the card's is negative. |
| current | Unchanged for the module and the card. The bolt-on tag's larger cell buys 2.6x (CR2450) or 4.3x (CR2477) the life at the same current, or the same life at a much higher ranging duty cycle. |
| size | Card 85.6 x 54 x ~2 mm; bolt-on tag unconstrained; module 15 x 20 mm on the research/09 proposal; sticker refused. |
| complexity | The block is done work. Each variant is a board spin plus its own antenna solve — the D37.31 mm keep-out and the ground rules are the whole integration guide, and D16 says a block that places perfect copper into a host that then floods ground over the antenna is WORSE than no block, because it looks correct. |

## What it would break in the current design

- Nothing in halo_rev_a. These are additional hosts for a block, not changes to the puck.
- It does break an assumption in the module pin list: research/09 section 6.3 numbers 24 pads against nRF52 functions, and D12 moved the SoC to nRF54L. Every nRF54L GPIO is routed by PSEL so the assignment is still free, but the pin list has to be re-derived against the nRF54L10 package before anyone fabricates a module.
- The sticker breaks docs/ANTI-STALKING.md and is refused here rather than quietly shipped as a 'sensor tag'. If it ever ships it ships without crowd finding, and that has to be stated on the product and not only in a file.

## The smallest experiment that would settle it

Take the halo_rev_a design block, drop it into a 85.6 x 54 mm card outline in ce-pcb, and run the antenna solve on the card's own copper with a CR2016 can in place. Two numbers come out: whether the resonance lands in band without a match (it should, because the card is larger than the keep-out in both axes) and what the realized gain is. That is one afternoon and it settles whether the card is a board spin or a research project. Do the card first, not the module: the card is the variant where the block's value shows up as a number rather than as a claim.

## What follows if it works

- part:halo-core goes onto the triad shelf as a real block with more than one host, which is what makes it reusable rather than merely published.
- The bolt-on asset tag is the shape Leif's own fleet wants, and it is the one where the energy concepts C4, C5 and C6 all get easier at once.

---

Generated from `spec/concepts.json` by `tools/gen_concepts.py` on 2026-09-05. Do not edit this file; edit the JSON.
