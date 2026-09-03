# RuuviTag — github.com/ruuvi/ruuvitag_hw
Fetched 2026-09-03. Last commit (commits/master.atom): 2021-07-14.

## README (verbatim, raw.githubusercontent.com/ruuvi/ruuvitag_hw/master/README.md)
```
# RuuviTag: Open-Source Sensor Platform

* Rev.A1 - the first RuuviTag ever invented.
* Rev.A2 - minor modifications. Note: neither A1 or A2 are currently mass produced by Ruuvi.
* Rev.B1 - a completely new design. Larger footprint, nRF52 radio chip etc.
* Rev.B2 ... Rev.B8 - enhanced versions.

All the design files are licensed using Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).
Copyright: Lauri Jämsä, Ruuvi Innovations Ltd. Neither the name of the RuuviTag nor the names of
its contributors may be used to endorse or promote products derived from this project without
specific prior written permission. While unofficial products should not have "Ruuvi" in their
name, it's okay to describe your product in relation to the Ruuvi projects. More info: license@ruuvi.com.
```

## ruuvitag_revb8/ file listing (fetched 2026-09-03)
`README.md`, `ruuvitag_revb8.sch`, `ruuvitag_revb8.kicad_pcb`, `ruuvitag_revb8.pro`,
`ruuvitag_revb8-cache.lib`, `ruuvitag_revb8_schematic.pdf`, `fp-lib-table`,
`sym-lib-table`, `fp-info-cache`.
=> KiCad 5-era file set (.sch + -cache.lib + .pro). **No gerbers, no BOM in this dir.**

## revb8 changelog (raw README, fetched 2026-09-03)
Remove the reset button; remove the reverse polarity protection FET; make all vias
smaller; add a TMP117; replace the BME280 with a DPS310; add external I2C pull-ups;
power sensors using GPIO pins; 100nF caps to 1uF (except the nRF's D...)

## Physical / electrical (ruuvi.com tech spec, via search result snippet 2026-09-03)
- PCB diameter 45 mm; enclosure 52 mm max diameter, 12.5 mm high; 25 g with enclosure+battery.
- CR2477 coin cell, 1000 mAh.
- nRF52832; LIS2DH12 accelerometer; BME280 (older revs) / DPS310+TMP117 (B8); NFC-A tag antenna.
- RuuviTag Pro: 78.3 mm max enclosure diameter, 15 mm high, 38 g.
NOTE: an earlier WebFetch of https://ruuvi.com/i/u/ruuvitag-tech-spec-2023-04.pdf returned
"80 x 35 x 12 mm, CR2450 600 mAh" — that contradicts every other source and is treated as a
bad extraction. Dimensions above are the ones to trust; re-verify against the PDF before use.

## Assessment
The single best-documented open coin-cell BLE tag on the internet: real KiCad sources,
a real OSHW licence, an NFC-A antenna already laid out, an accelerometer already routed,
a round outline, and a production history of 8 revisions. Not a Find My tag and has no
sounder, and the board is 45 mm (AirTag PCB is inside a 31.9 mm puck).
