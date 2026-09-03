# ESP32 hardware design guidelines — module-on-baseboard antenna keep-out
Lane I. Fetched 2026-09-03.

Source: Espressif, *ESP Hardware Design Guidelines* (ESP32), master release, PDF
<https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/esp-hardware-design-guidelines-en-master-esp32.pdf>
(HTML index: <https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/index.html>)

## §1.4.8 "General Principles of PCB Layout for Modules (Positioning a Module on a Base Board)" — verbatim

> If module-on-board design is adopted, attention should be paid while positioning the module on the
> base board. The interference of the baseboard on the module's antenna performance should be minimized.
>
> It is suggested to place the module's on-board PCB antenna **outside the base board**, and the feed
> point of the antenna close to the edge of the base board. In the following example figures, positions
> with mark ✓ are strongly recommended, while positions without a mark are not recommended.
>
> If the antenna cannot extend beyond the board edge, the feed point should still be placed as close to
> the board edge as possible. Then **cut off the base board on both sides of the antenna and below it**
> to minimize the impact of the base board material on the PCB antenna and provide a sufficiently large
> clearance area for the PCB antenna. Note that **the module should not be placed in the center of the
> board with clearance created by hollowing out on all four sides.**
> Figure *Keepout Zone for ESP32 Module's Antenna (Antenna feed point on the Left)* shows the suggested
> clearance area. Please note that **sufficient ground copper and dense ground vias should be placed on
> the base board near the antenna**.
>
> After the base board is placed in the end product, please consider the impact of the housing on the
> antenna during end-product design. Ensure that the PCB antenna on the base board also has a
> sufficiently large clearance area inside the housing. **A clearance of at least 15 mm is recommended
> in all directions.**
>
> Please note that the final end product should be tested for throughput and communication range to
> ensure RF performance.

Figures referenced: Fig. 23 (feed point on the right), Fig. 24 (feed point on the left),
Fig. 25 *Keepout Zone for ESP32 Module's Antenna*.

Chapter list of the guideline set: About This Document · Product Overview · Schematic Checklist ·
PCB Layout Design · Download Guidelines · Related Documentation · Glossary · Revision History ·
Disclaimer.

## ESP32-WROOM-32 datasheet v3.7 — the numbers behind the footprint
Source: <https://documentation.espressif.com/esp32-wroom-32_datasheet_en.pdf>
(redirected from `https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32_datasheet_en.pdf`,
301, fetched 2026-09-03). Marked **NRND** on every page.

- Module dimensions: `18.00 ± 0.15 × 25.50 ± 0.15 × 3.10` mm (§9, Figure 7).
  Revision note v2.6, 2018-08: tolerance tightened from ±0.2 to ±0.10 mm.
- Pin count: **38 pads** plus a large centre thermal/GND pad numbered 39.
- Recommended PCB land pattern (Figure 8): `38 × 1.50` mm long pads, `38 × 0.90` mm wide,
  **1.27 mm pitch**, rows at 11.43 mm and 16.51 mm spans, thermal-pad via array in the centre.
- The land-pattern drawing carries an explicit **"Antenna Area"** rectangle at the top of the module,
  5.94 mm deep across the 18.00 mm width — the copper-free region the host board must reproduce.
- The pinout drawing (§2.1) labels the top of the module **"Keepout Zone"**.
- Espressif also ship "Source files of recommended PCB land patterns to measure dimensions not covered
  in Figure 10.1" — i.e. the module footprint is published as CAD, not only as a drawing.

## Why this matters for haytag
This is the canonical worked example of the thing GOAL.md asks for: a vendor publishes
(a) the module, (b) its land pattern as source CAD, and (c) a prose rule for the host board's copper
that is short enough to put in a README. The rule that survives translation to any outline is:
**feed point at the host board edge; no copper on any layer under or beside the antenna; ground pour
and via stitching everywhere else near it; never centre the module and hollow out four sides.**
