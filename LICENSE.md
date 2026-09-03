# Licensing

halo is published under a split licence, chosen by research lane F and
recorded as decision D4 in DECISIONS.md. Each part of the repository carries
the licence that fits what it is and what it derives from.

| what | licence | why |
|---|---|---|
| `hardware/`, `electronics/`, board and CAD files, enclosure | **CERN-OHL-S-2.0** | the strongly-reciprocal open-hardware licence: a fork that manufactures must publish its sources too |
| `firmware/` and any report-fetching tooling | **AGPL-3.0-or-later** | OpenHaystack and macless-haystack, which the firmware derives from, are AGPL-3.0; the obligation is inherited, not chosen |
| `tools/` written clean-room by this project | **Apache-2.0** | permissive with an express patent grant and retaliation clause |
| `docs/`, `research/`, `SPEC.md` and every other document | **CC-BY-SA-4.0** | share-alike documentation |
| `reference/` | **not ours** | vendored third-party snapshots; each keeps its upstream licence, listed in `reference/MANIFEST.md` |

Two consequences worth stating plainly:

- **A permissive firmware is possible but constrained.** Lane B's licence audit
  found the MIT-licensed line (acalatrava's original nRF5x firmware, the Zephyr
  port, FakeTag, FindMy.py) and the AGPL line (OpenHaystack itself,
  macless-haystack, find-you, send-my). Two projects, `heystack-nrf5x` and
  `biemster/FindMy`, **declare no licence at all** and are read-only reference.
  If halo firmware must be permissive, it derives from the MIT set only.
- **Nothing here derives from Apple's MFi specification.** Decision D5: the
  design is clean-room from the PoPETs 2021 academic paper and public
  reverse-engineering. Anyone who has read the MFi Find My specification under
  its non-disclosure agreement must not contribute to the firmware.

"AirTag" and "Find My" are trademarks of Apple Inc. halo is not affiliated
with, endorsed by, or certified by Apple. It is described as compatible with
Apple's Find My network, which is referential use; it does not carry, and may
not carry, the licensed "Works with Apple Find My" badge.
