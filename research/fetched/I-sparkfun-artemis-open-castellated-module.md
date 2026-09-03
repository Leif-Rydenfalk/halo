# SparkFun Artemis — the open-source-hardware certified module precedent
Lane I. Fetched 2026-09-03.

Sources:
- Repo README, <https://raw.githubusercontent.com/sparkfun/SparkFun_Artemis/master/README.md>
- Repo listing via GitHub API, <https://api.github.com/repos/sparkfun/SparkFun_Artemis/contents>
- LICENSE.md, <https://raw.githubusercontent.com/sparkfun/SparkFun_Artemis/master/LICENSE.md>
- Product page, <https://www.sparkfun.com/products/15484>
- Integration guide PDF v1p0p0 (2019-06-02),
  <https://cdn.sparkfun.com/assets/learn_tutorials/9/0/9/Artemis_Integration_Guide.pdf>
- Tutorial, <https://learn.sparkfun.com/tutorials/designing-with-the-sparkfun-artemis>

## Why it is the precedent
README, verbatim:

> We're proud to say the SparkFun Artemis module is **the first open source hardware module with the
> design files freely and easily available here (on this repo)**. We've carefully designed the module so
> that **routing to the module can be done with low-cost 2-layer PCBs with 8mil trace/space**.
> Additionally, we've released four open-source-hardware example products that act as a starting point
> for your product.

> This repo contains the design files for the 4-layer PCB. This design is pretty reliant on sophisticated
> manufacturing tools. We *do not* recommend that you order PCBs and attempt to hand stencil or hand place
> these components.

That is exactly the halo split: a **4-layer, machine-assembled module** so that every **host board can
be a cheap 2-layer board a hobbyist routes by hand**.

## What is published
Repo top level: `Artwork/` (SVG of the laser etching on the RF shield), `Bootloader/`, `Documents/`,
`Hardware/` (**Eagle `.brd` + `.sch`**), `LICENSE.md`, `README.md`.
`Documents/` contains: `ASC_RFANT8010080A3T_V04.pdf` (the chip antenna datasheet),
`Apollo3 Pad Mapping.pdf`, two Apollo3 datasheets, **`Artemis Production Model V1.step` (5.4 MB) and
`.stl`** (a mechanical model of the module for the host board's 3D view), `Auto-Bootload Timing.jpg`.

License: **CC BY-SA 4.0** for hardware ("SparkFun hardware is released under Creative Commons
Share-alike 4.0 International"), plus the README's "maintain attribution … release any derivative under
the same license".

## Facts (integration guide v1p0p0)
| item | value |
|---|---|
| Module dimensions | **15.5 × 10.5 × 2.3 mm** (guide §3, "including antenna") |
| Weight | 0.6 g |
| Antenna | "2.4 – 2.5 GHz **Chip**" (Abracon ASC RFANT8010080A3T) |
| Pads | **59 numbered pads** in the pad-assignment table |
| SoC | Ambiq Apollo3 Blue, Cortex-M4F, up to 48 GPIO |
| Current | 6 µA/MHz from flash @3.3 V; 1 µA deep sleep with RTC, BLE off |
| Price | **$9.95** (sparkfun.com/products/15484) |
| Certification | "FCC/IC/CE Certified (**ID Number 2ASW8-ART3MIS**)" |

Guide §"Easy Integration": *"Large SMD pads and spacing allow for low cost 2-layer carrier board
implementations. Programming over pre-configured serial bootloader or JTAG."*
The guide publishes a *Recommended PCB Layout* (copper pad + paste aperture dimensions) and a separate
*Recommended Soldermask Layout* page.

## Host-board rules — verbatim from the integration guide §"Routing and Recommended Keep Out"
> The Artemis module was designed to be implemented onto low cost 2-layer PCBs with easy 8mil trace/space
> routing. **A good ground connection is essential. Routing under the module is allowed. Keep all ground
> pours away from the antenna area. If mechanical exposure allows for it the antenna can be extended over
> the edge of the PCB for increased reception.**

Note that "Routing under the module is allowed" is the opposite of the ESP32-WROOM rule for the antenna
region, and is only true because the Artemis antenna is a **chip** antenna at one end, not a PCB trace
antenna spanning the module.

## Pin-list shape worth copying
Pad 1 = GND. Pad 2 = GPIO20/**SWDCK**. Pad 3 = GPIO49/**RX0 bootload**. Pad 7 = **BOOT**
("Hold pin high during reset to initiate bootloader"). Pad 9 = GPIO48/**TX0 bootload**.
Pad 10 = GPIO21/**SWDIO**. Pads 34/35 = **XO/XI** (external 32.768 kHz crystal, brought *out* of the
module rather than fitted on it). Pad 50 = **nRESET**. GND pads at 1, 22, 38, 39, 47, 59 — i.e. ground
returns interleaved along the whole perimeter, not bunched at one corner.
