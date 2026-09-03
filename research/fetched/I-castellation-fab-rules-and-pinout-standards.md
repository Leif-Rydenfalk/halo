# Castellation fab rules and small-module pinout standards
Lane I. Fetched 2026-09-03.

## JLCPCB — castellated holes and plated edges
<https://jlcpcb.com/capabilities/pcb-capabilities>

Castellated holes ("metalized half-holes on PCB edges, commonly used on daughter boards"):
- minimum hole diameter **≥ 0.5 mm**
- hole-to-hole spacing **≥ 0.5 mm**
- hole-to-board-edge **≥ 1 mm**
- board minimum size **10 × 10 mm**, minimum thickness **0.6 mm**
- trace/space minimum 0.10/0.10 mm at 1 oz copper

Plated edges:
- board minimum **10 × 10 mm**, thickness **0.6 mm**
- *"At least 3 breaks (more for larger PCBs) in the edge plating are required for support tab
  connections"*
- *"ENIG treated. **HASL is not supported.**"*

No separate surcharge is quoted on that page for castellated holes.

## PCBWay — castellated holes
<https://www.pcbway.com/capabilities.html>
- minimum half-hole diameter **0.4 mm**; edge-to-edge spacing **≥ 0.3 mm**
- verbatim: *"**Design Half-Holes greater than 0.4mm to ensure better connection between boards.**"*
- 0.4–0.7 mm diameter is classified medium difficulty and may go to non-standard review;
  < 0.4 mm or spacing < 0.3 mm requires non-standard review.
- No published surcharge line item; PCBWay directs you to a quote.

**Design rule this implies for a halo-core module:** a 1.27 mm pitch castellation with 0.6 mm plated
half-holes clears both houses with margin (0.6 ≥ 0.5 JLCPCB / ≥ 0.4 PCBWay; gap 0.67 mm ≥ 0.5/0.3), and
1.27 mm is what the two most-copied modules in the world already use.

## Pitches actually used by shipping castellated modules (measured from their own documents)
| module | pitch | pads | source |
|---|---|---|---|
| ESP32-WROOM-32 | **1.27 mm**, pads 1.50 × 0.90 mm | 38 + centre pad 39 | Espressif datasheet v3.7 Fig. 8 |
| Raspberry Pi Pico / Pico W | **2.54 mm** (0.1″, dual SMT + THT) | 40 | *Hardware design with RP2040* §3.5 |
| Raytac MDBT42Q | not stated in datasheet text | 41 ("41-SMD Module") | Raytac datasheet §2.2 / Digi-Key |
| Minew MS88SF2 | pad **1.8 × 0.8 mm**, 0.5 mm outward extension | 28 | Minew datasheet §5 |
| Insight SiP ISP1807 | **0.65 mm LGA, two rows** (NOT castellated) | 51 | ISP1807 datasheet §3 |
| SparkFun Artemis | not stated ("large SMD pads and spacing") | 59 | Artemis Integration Guide v1p0p0 |

## SparkFun MicroMod — the "processor board + carrier" standard
<https://learn.sparkfun.com/tutorials/designing-with-micromod>
- Uses an **M.2 edge connector** (not castellations). Processor boards are **0.8 mm thick with a 20° edge
  bevel** (usually made as a 45° chamfer). Single specified size today: **22 × 22 mm**.
- **60+ pins** grouped: power (3.3 V, GND, USB_VIN), USB, CAN, UART, I²C, SPI/SDIO, audio, **SWD**, ADC,
  PWM, and general digital (D0–D1, A0–A1, G0–G11).
- Split of responsibility: *processor boards* carry the MCU, decoupling, crystals, USB-serial and one
  status LED; *carrier boards* carry power regulation, UI, connectors and application peripherals.
- Design files and footprints live in the SparkFun Eagle Libraries repo (`SparkFun-MicroMod`);
  licensed **CC BY-SA 4.0**.
- Verdict for halo: the right *split of responsibility*, the wrong *connector* — an M.2 socket is
  taller and more expensive than the whole halo BOM target and cannot be reflowed flat under a coin
  cell.

## RAK WisBlock
<https://docs.rakwireless.com/product-categories/wisblock/>
- Base + Core + IO + Sensor modules that click together; slots named "Slot A to D"; a 40-pin power slot
  connector on some bases.
- **The mechanical/electrical interface specification, pinouts and footprints are not published on the
  documentation site** — it is a modular *product family*, not an open interface standard. Not a model
  to copy.

## Seeed XIAO
<https://wiki.seeedstudio.com/XIAO_BLE/> — 21 × 17.8 mm, single-sided components so the board can be
surface-mounted onto a host; 11 GPIO / 6 ADC on the nRF52840 variant. The wiki does not state the
castellation pitch. XIAO is a *de facto* small-form-factor pinout with many third-party carriers, but
there is no published interface spec document analogous to MicroMod's.

## Tag-Connect TC2030 — programming without a connector
<https://www.tag-connect.com/product/tc2030-idc-nl>
- **6 pins, 0.1″ pitch**, *"a tiny 0.02 sq inch footprint"* on the target board — the page compares it to
  the area of an 0805 resistor. "No Legs" (NL) version is hand-held or held with a retaining clip.
- **$33.95** for the cable (one-off tooling cost for the developer, zero recurring cost per board).
- Exact pad diameter / spacing / alignment-hole dimensions are not on the product page —
  **not verified here**; take them from Tag-Connect's published footprint drawing before laying out.

→ For halo this is the right answer to "how do you program a 15 × 20 mm module inside someone's
product": no connector on the host board at all, six pads plus two alignment holes, cost ≈ 0.
