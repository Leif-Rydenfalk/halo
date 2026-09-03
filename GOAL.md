# GOAL — what haytag is for

Leif, 2026-09-03, verbatim:

> the goal is to have a open source cheaper air tag and with the pcb open source
> its easy for everyone to integrate into their own pcbs and have any shape they
> want for it and integrate into any desings. i will use it in my sensors to
> know their local position relative to other sensors in my digital twin
> prohjects to have a cheap way of knowing the location of my sensors and
> devices and assets.

## The three deliverables this implies

1. **A cheaper open AirTag.** A complete puck — BLE tag that rides Apple's Find
   My network (OpenHaystack-style keys first; the official accessory-program
   path documented), sounder, NFC, accelerometer, CR2032, anti-stalking (DULT)
   behaviour — with every design file open and a BOM that undercuts Apple's $29.

2. **An embeddable block, not only a puck.** The tag is designed as a reusable
   *circuit block* that anyone can drop into their own board in any outline:
   a KiCad hierarchical sheet + footprints + a documented antenna keep-out, and
   a castellated/solder-down module variant for people who do not want to do
   RF layout. The round 32 mm puck is just the first host board for that block.

3. **Local relative position between devices.** Find My tells you where a
   thing is at city scale (someone's iPhone walked past it). Leif's sensors
   need to know where they are *relative to each other* at room scale, cheaply,
   so the digital twin (Twinton) can place every sensor, device and asset.
   That is a peer-to-peer ranging problem: UWB two-way ranging (DW3000-class)
   is the accurate route; BLE RSSI / AoA is the cheap route. The research must
   settle which the block carries, at what cost, and how a fleet of haytags
   self-locates without infrastructure.

## Constraints that follow

- Cost is a first-class spec: BOM at 10 / 100 / 1 000 / 10 000, vs $29 retail.
- Anything in the block must be sourceable at LCSC/JLCPCB (no Apple U1).
- Every piece is open: CERN-OHL for hardware, permissive or AGPL-compatible
  firmware (research/06 decides), Find My marks used only as research says.
- Not a stalking tool: DULT behaviour is in the block, not an afterthought
  (docs/ANTI-STALKING.md).
- Feeds ce-workshop: the block becomes `part:haytag-core` on the triad shelf so
  every ce-designs machine (sensor boards, rigs, robots) can reference it and
  report its position into Twinton.
