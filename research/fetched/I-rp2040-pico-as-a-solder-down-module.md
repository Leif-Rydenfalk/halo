# Raspberry Pi Pico as a solder-down module — the carrier-board precedent
Lane I. Fetched 2026-09-03.

Source: Raspberry Pi, *Hardware design with RP2040*,
<https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf> (8.85 MB, converted locally
with `pdftotext -layout`).

## The published-reuse pattern
§2 *Minimal design example*:
> This minimal design example is intended to demonstrate how you can get started with your own RP2040
> based PCB designs. … **schematic and layout files are available for KiCad at RP2040 Minimal KiCad
> design (ZIP file)**. KiCad is a free, open source suite of tools for designing PCBs …

> The minimal design example … was deliberately designed with two copper layers …

§3 publishes a second, larger reference (the VGA/SD-card/audio demo boards) whose purpose is explicitly
to show **Pico used as a module**:
> Raspberry Pi Pico or Raspberry Pi Pico W as a module, used simply as a component on a larger design.

> Schematic, PCB layout and **Raspberry Pi Pico/Raspberry Pi Pico W footprint files are provided in KiCad
> format**, with similar design rules as the previous minimal design example …

## Castellated edges — verbatim
> Each pin on Raspberry Pi Pico and Raspberry Pi Pico W has two soldering options. You can either solder
> 0.1″ headers using the through-holes, or alternatively, as both have **castellated edges (where the pin
> extends to the edge of the board, and then down the edge of the PCB itself), a pin can be soldered down
> directly to a PCB. If the SWD pins are used then they should have an extra pin added to ensure a good
> connection.**

> The CAD footprint provided with this design **provides both options**, so Raspberry Pi Pico or
> Raspberry Pi Pico W can either be soldered direct to this design, or 0.1″ headers may be used …

## Antenna keep-out — verbatim (Pico W)
> **In Raspberry Pi Pico W there is a cutout for the antenna (14 mm × 9 mm). If anything is placed close
> to the antenna (in any dimension) the effectiveness of the antenna is reduced. Raspberry Pi Pico W
> should be placed on the edge of a board and not enclosed in metal to avoid creating a Faraday cage.
> Adding ground to the sides of the antenna improves the performance slightly.**

## The KiCad keep-out defect, verbatim — matters directly to haytag
> **KiCad currently doesn't have a keepout layer in its footprints. The recommended approach, and the one
> we've used here, is to show the keepout zones on the `dwgs.user` layer, and the user must then manually
> remove the copper on the PCB layout itself.**

Raspberry Pi's carrier footprint therefore carries three kinds of information beyond pads:
1. four drill holes under the USB connector so the module sits flat against the carrier
   ("These are here to help … sit flat against our carrier PCB, as the metal through-hole lugs which
   anchor the USB connector can sometimes protrude slightly");
2. **copper keep-outs on the top layer aligned with the module's underside test points** — "we consider it
   good practice … as it makes the chances of shorting these testpoints … almost zero";
3. a component keep-out:
   > Obviously, if you will be directly soldering Raspberry Pi Pico or Raspberry Pi Pico W to your board,
   > then the entire footprint will have to have a component keepout underneath.

## Lessons haytag should take
- Publish **one footprint that supports both** solder-down castellation and 0.1″ headers, so the same
  part serves production and prototyping.
- Call out the antenna cut-out as an explicit rectangle with numbers (`14 mm × 9 mm` here).
- Add a redundant pad on SWD lines, because a castellation alone is a marginal joint on a debug signal
  that must work when everything else does not.
- Put keep-outs on `dwgs.user` **and** say in the README that the host designer must delete the copper —
  a footprint cannot enforce it in KiCad.
