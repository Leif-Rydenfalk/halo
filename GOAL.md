# GOAL — what halo is for

Leif, 2026-09-03, verbatim:

> the goal is to have a open source cheaper air tag and with the pcb open source
> its easy for everyone to integrate into their own pcbs and have any shape they
> want for it and integrate into any desings. i will use it in my sensors to
> know their local position relative to other sensors in my digital twin
> prohjects to have a cheap way of knowing the location of my sensors and
> devices and assets.

And, clarifying, same day, verbatim:

> i mean it should be a perfect copy of the internal airtag stuff so a find my
> puck which is cheap to produce and yo ucan take the pcb and integrate it
> everywhere

## What that means, in order

1. **A perfect copy of the AirTag internals.** Function for function, what is
   inside the AirTag is inside halo: the BLE SoC role (nRF52832 in Apple's
   board), the Find My advertisement and key rotation, the NFC tag the phone
   taps, the accelerometer that wakes it, the speaker that drives the shell,
   the UWB ranging that Precision Finding uses (Apple's U1 is unobtainable, so
   the closest sourceable substitute — research/05 and /08 settle which), the
   CR2032 and its contact scheme, the Ø ~32 × 8 mm envelope. Where a 1:1 part
   is not buyable, the substitute is chosen for the same function and pinned
   to a source; where a function cannot be reproduced at all (e.g. Apple-side
   Precision Finding UI with a non-Apple UWB chip) that is written down as a
   known gap, not glossed. Cheap to produce: BOM at 10 / 100 / 1 000 / 10 000
   against Apple's $29, every part on LCSC/JLCPCB.

2. **An embeddable block, not only a puck.** The tag is designed as a reusable
   *circuit block* that anyone can drop into their own board in any outline:
   a KiCad hierarchical sheet + footprints + a documented antenna keep-out, and
   a castellated/solder-down module variant for people who do not want to do
   RF layout. The round 32 mm puck is just the first host board for that block.

3. **Leif's own use: local relative position between his devices.** Find My
   tells you where a thing is at city scale (someone's iPhone walked past it).
   His sensors need to know where they are *relative to each other* at room
   scale so the digital twin (Twinton) can place every sensor, device and
   asset. The AirTag already carries the radio for this (UWB); a faithful copy
   with a sourceable UWB chip can range peer-to-peer between halos as well
   as toward a phone. research/08 settles whether the UWB substitute can do
   that, how well, at what battery cost, and what BLE-only fallback exists.

## Constraints that follow

- Cost is a first-class spec: BOM at 10 / 100 / 1 000 / 10 000, vs $29 retail.
- Anything in the block must be sourceable at LCSC/JLCPCB (no Apple U1).
- Every piece is open: CERN-OHL for hardware, permissive or AGPL-compatible
  firmware (research/06 decides), Find My marks used only as research says.
- Not a stalking tool: DULT behaviour is in the block, not an afterthought
  (docs/ANTI-STALKING.md).
- Feeds ce-workshop: the block becomes `part:halo-core` on the triad shelf so
  every ce-designs machine (sensor boards, rigs, robots) can reference it and
  report its position into Twinton.
