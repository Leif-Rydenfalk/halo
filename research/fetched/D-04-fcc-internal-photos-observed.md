# FCC internal photos — what I actually SAW on the boards

Fetched: 2026-09-03. FCC exhibits are US public records; cite the FCC ID.
Files downloaded to ../../images/commercial/ (PDFs + rendered PNGs).

## Chipolo ONE Spot — FCC ID 2AD85-C21M (CHIPOLO d.o.o., grant 2021-05-05)
Model↔FCC-ID confirmed by Chipolo's own regulatory page
(https://chipolo.net/en-us/pages/regulatory): "ONE Spot | 2AD85-C21M | 22600-C21M".
Internal photos exhibit 5232705, lab CTC advanced, doc 1-1830/21-01-01_AnnexB, 2021-02-25.

Observed, page 2-3:
- Two-part black plastic shell, ~38 mm disc, Panasonic Industrial CR2032 3 V coin cell
  visible in the back half.
- Single small green 2-layer-looking PCB, roughly D-shaped, with a **meandered printed
  trace antenna** occupying the whole left edge of the board. No LDS frame, no chip antenna,
  no coax.
- One dominant QFN/WLCSP SoC mid-board plus a handful of 0402 passives and a crystal.
  Part markings are not legible at the exhibit's resolution — the nRF52833 identification
  comes from Nordic's own press release, not from these photos.
- Rear side: a large gold annular pad = the buzzer/transducer contact ring.
- No UWB, no NFC coil, no accelerometer visible as a separate package (may be inside the
  unreadable second package).

## eufy SmartTrack Link — FCC ID 2AOKB-T87B0 (Anker Innovations, grant 2022-05-25)
2402-2480 MHz, 0.0023 W conducted. Internal photos exhibit 5895281, lab Shenzhen Anbotek.

Observed, page 3:
- Small black-soldermask PCB, ~25 mm across per the ruler in frame.
- Silkscreen reads **"TTB2H-MAX-V07  2024?/2022-07"** and UL mark "E358074 94V-0".
- **Exposed programming pads labelled in silkscreen: CLK, DIO, TX, RX, GND, 3V3** — SWD plus
  UART, brought out and legible. (Useful precedent: shipping a certified tag with visible
  debug pads is normal.)
- One tact switch ("KEY" in silkscreen), one gold buzzer contact ring, a flex/ZIF tail.
- Antenna is off-board / edge; no chip antenna visible on this face.

## UGREEN FineTrack Smart Finder CM816 — FCC ID 2AQI5-CM816 (Ugreen Group, grant 2024-11-20)
2402-2480 MHz, 0.002 W conducted. Internal photos exhibit 7833668.

Observed, page 2 (the lab annotated it for us):
- **"MAIN BOARD TOP VIEW"** with two red callouts: **"PCB Antenna"** (a short meandered
  trace at the top edge, silkscreened "UGREEN FM21-CM816 V1.0") and **"RF Chip"** (a single
  ~4x4 mm QFN). That is the entire radio: one QFN plus a printed antenna.
- Board is ~25 mm across against the mm ruler in frame.
- Front also carries a large metal dome/transducer and a tact switch.
- **"MAIN BOARD REAR VIEW"**: a big gold annular ring + centre pad = the CR2032 contact,
  and a row of ~6 castellated/edge test pads.
- No crystal can vs. the die-adjacent package is ambiguous; no UWB, no NFC coil.

## Motorola moto tag — FCC ID IHDT6AB3 (Motorola Mobility, model XT2445-1)
Test report EP441117A, Sporton International (Kunshan), issued 2024-05-28, Rev 01.
Internal photos exhibit 7355558, 12 pages.

Observed:
- p.19: enclosure halves + CR2032, ~32 mm disc against the ruler.
- p.21: round green PCB ~26 mm dia. The lab annotated **"UWB Antenna"** and **"BLE Antenna"**
  as two SEPARATE small chip/patch antennas at the board edge — not one shared LDS frame.
- Silkscreened test pads, legible: **GND, VBAT, RST, TXD, RXD, SWCLK, SWDIO**. Date code
  silkscreen "2024-04-08".
- The mating half carries a large gold piezo/transducer disc.
- Chip identifications (Nordic nRF52840 + Qorvo DW3210) come from a third-party analysis, not
  from these photos — see sources.tsv.

## Pebblebee Clip — FCC ID 2AG5O-PB-531-BG (PB Inc, Issaquah WA, grant 2023-04-04)
2402-2480 MHz, 0.00154 W conducted. Internal photos exhibit 6455481, 5 pages, downloaded.
Block diagram and schematics are marked metadata-only (withheld).

## Pattern across all five
Every certified third-party tag is: **one BLE SoC in a QFN/WLCSP + a printed or chip antenna
+ a piezo transducer + a coin cell or LiPo + a tact switch, on a single small 2-layer board.**
Only the moto tag adds UWB, and it does so with a second discrete antenna rather than
Apple's LDS frame. Nobody but Apple builds a voice-coil speaker or an LDS antenna carrier.
