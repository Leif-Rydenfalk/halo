# C11 — The tag you can audit — open debug, reproducible firmware, and why it costs almost no secrecy

*Nobody can prove what an AirTag does. A halo whose firmware hash an owner can verify against a published build is a procurement answer no commercial tracker can give — and with pre-generated keys it gives away almost nothing.*

**Verdict: PLAUSIBLE** — Every component is established: the debug header exists on the board as Tag-Connect pads, the key architecture that makes an open debug port nearly free is documented in research/02 section 9, and reproducible builds are ordinary practice. What has not been done is the analysis of exactly what an attacker gains from a flash dump under each key scheme, and that analysis — not a bench — is the work.

Family `trust` · value 3/5 against effort 1/5 · part of the halo concept portfolio, `docs/concepts/README.md`.

## What it is

D6 already lists 'a documented debug header' as one of the five things halo offers that nothing on sale does: certified tags from eufy and Motorola ship with debug pads on the board, undocumented. halo's are a header with a pinout.

The concept is to take that further and make it a stated property: a published, reproducible firmware build, a hash an owner can compute themselves, and a debug port that lets them dump the part and compare. For anyone deploying tags into a facility — which is Leif's use — 'prove this device only does what it says' is a procurement requirement, and no commercial tracker can meet it at any price.

The obvious objection is that an open debug port leaks the keys. That objection is weaker than it looks, and the reason is architectural. In the OpenHaystack scheme the tag holds a list of PUBLIC keys, 28 bytes each; the private key stays with the owner. A flash dump therefore does not reveal a secret that lets anyone read the tag's location reports. What it does reveal is the tag's FUTURE advertisements, which lets whoever has the dump recognise that tag later — but whoever has the dump is holding the tag.

The alternative architecture, on-device derivation from a master secret, is where an open port really does cost something: it hands over the master and with it every past and future key. So this concept is also a fork in the firmware design, and it is worth taking the fork deliberately rather than by accident.

## Why it beats the alternative

Against a certified commercial tag: those bind you to a vendor app and, on the certified path, to a per-unit Apple Token burned into flash at the factory. There is no version of them you can audit, and no version whose keys are yours.

Against 'open source' claimed on a repository page: a published source tree proves nothing about the part on your desk. A reproducible build plus a readable port is the difference between claiming and demonstrating, and it is a difference a purchasing department understands.

Against Apple: an AirTag's firmware was dumped once, by voltage-glitching APPROTECT, by a researcher. That is the state of the art for auditing an AirTag. It is not a procurement answer.

## The numbers

| quantity | value | where it comes from |
|---|---|---|
| Debug access already on the board | **SWD on Tag-Connect pads, zero vertical height** | electronics/halo_rev_a/schematic.py header, delta D-8 |
| Storage per pre-generated advertisement key | **28 bytes** | macless-haystack flashing instructions, quoted research/02 section 9 |
| How far 500 keys go | **14 kB of flash; about 10.4 days at 30 min rotation, 5.2 days at 15 min** | research/02 section 9, verified arithmetic on verified parameters |
| Free NVM on the chosen part | **1 MB total, 13,164 bytes used** | nRF54L10; SPEC.md section 2a measurement |
| What an AirTag flash dump costs today | **a voltage-glitching attack on APPROTECT** | research/01 section 7.3 |

## The evidence

| claim | source | date | confidence |
|---|---|---|---|
| Certified commercial tags ship with undocumented debug pads; halo's are documented | DECISIONS.md D6 point 3, from lane D's FCC exhibit reading | 2026-09-03 | primary |
| OpenHaystack-style tags hold public keys only, 28 bytes each, and nRF firmwares are patched at the OFFLINEFINDINGPUBLICKEYHERE! marker | research/02 section 10.1 item 4 | fetched 2026-09-03 | primary |
| The AirTag's nRF flash was dumped by glitching APPROTECT; this is the only known route | research/01 section 7.3 | 2026-09-03 | primary |
| halo's firmware occupies 13,164 bytes of flash and 704 bytes of RAM with all three protocol layers resident, so a reproducible build is a small artifact to verify | SPEC.md section 2a; DECISIONS.md D18 | 2026-09-04 | primary, measured |
| The licence split already commits the firmware to AGPL-3.0-or-later, which obliges source availability anyway | DECISIONS.md D4 | 2026-09-03 | primary |

**What is NOT established here, stated so nobody inherits it as a fact:**

- The exact attacker gain from a flash dump under each key scheme. The claim that pre-generated public keys leak 'only future advertisements' is reasoning from the protocol, not a result anyone published. Settle it by writing the threat model down explicitly and having it read by someone who did not write it — this is a paper exercise, not a bench one, and it belongs beside docs/ANTI-STALKING.md.
- Whether the nRF54L10's build is byte-reproducible under Zephyr with the current toolchain. Nothing in this repository has tried. Two builds on two machines and a diff would answer it in an hour.

## What it costs

| dimension | cost |
|---|---|
| money | $0.00. The pads are already on the board and cost no height. |
| current | 0 uA. Leaving APPROTECT open does not draw current. |
| size | 0 mm. Tag-Connect needs no connector. |
| complexity | Low in hardware, real in process: a reproducible build needs pinned toolchains and a published recipe, and a threat model needs writing. The cost is discipline, not engineering. |

## What it would break in the current design

- It forecloses the on-device key-derivation architecture, or at least makes choosing it a decision with a stated cost. Pre-generated keys are flash-hungry and have a bounded lifetime before wrap-around; on-device derivation is unbounded but puts a master secret on a part with an open port. research/02 section 9 calls this the single biggest firmware-architecture question in the project, and this concept is one of the two things that should decide it.
- It sits awkwardly beside DULT's identifier gate. DULT section 3.15.3 requires a physical mechanism before Get_Identifier will answer, precisely so a tag cannot be silently interrogated. An open SWD port bypasses that — but so does a screwdriver, and DULT's threat model assumes the attacker does not have the device in hand.

## The smallest experiment that would settle it

Build the current firmware twice, on two machines, with a pinned toolchain, and diff the two ELF files byte for byte. If they differ, find out where and whether it is a timestamp. That one command answers whether 'verify it yourself' is a claim halo can make at all, and it costs an hour. The threat model is the second half and it is writing, not measuring.

---

Generated from `spec/concepts.json` by `tools/gen_concepts.py` on 2026-09-05. Do not edit this file; edit the JSON.
