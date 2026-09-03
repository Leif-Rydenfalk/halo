# Sound generators, coin cells and holders — datasheet numbers

All fetched 2026-09-03.

## CR2032 — Maxell data sheet
https://biz.maxell.com/en/primary_batteries/CR2032_DataSheet_20e.pdf (sheet dated 20.06)

| Parameter | Value |
|---|---|
| System | Manganese Dioxide-Li / organic electrolyte |
| Nominal voltage | 3 V |
| Nominal capacity | 220 mAh (to 2.0 V at 0.2 mA, 20 deg C) |
| Nominal discharge current | 0.2 mA |
| Operating temperature | -20 to +85 deg C |
| Weight | 3.0 g |
| **Diameter** | **20.0 mm** |
| **Height** | **3.2 mm** |
| UL recognition | MH12568 |

Sheet footnote: "Dimensions and weight are for the battery itself, but may vary depending on
terminal specifications and other factors." The drawing marks the cap face (-) and the can face (+).

Panasonic's CR2032 as fitted by Apple is quoted by Catley at "225mAh and 3V"; iFixit quotes
"0.66 Wh" for a 20 mm cell versus "about .39 Wh" for the Tile's CR1632.

## Murata 7BB piezoelectric diaphragms (bare bender elements, external drive)
https://www1.futureelectronics.com/doc/Murata/7BB-20-6-MUR.pdf (catalogue, specs as of May 2014)

| Part | Resonant freq. | Res. impedance max | Brass Ø (mm) | Ceramic Ø (mm) | Electrode Ø (mm) | **Total thickness (mm)** | Ceramic thickness (mm) | Base |
|---|---|---|---|---|---|---|---|---|
| 7BB-12-9 | 9.0 +/-1.0 kHz | 1000 Ω | 12.0 | 9.0 | 8.0 | **0.22** | 0.10 | Brass |
| 7BB-15-6 | 6.0 +/-1.0 kHz | 800 Ω | 15.0 | 10.0 | 9.0 | **0.22** | 0.10 | Brass |
| 7BB-20-3 | 3.6 +/-0.6 kHz | 500 Ω | 20.0 | 14.0 | 12.8 | **0.22** | 0.10 | Brass |
| 7BB-20-6 | 6.3 +/-0.6 kHz | 350 Ω | 20.0 | 14.0 | 12.8 | **0.42** | 0.20 | Brass |
| 7BB-27-4 | 4.6 +/-0.5 kHz | 200 Ω | 27.0 | 19.7 | 18.2 | **0.54** | 0.30 | Brass |

Minimum order quantities in the same catalogue: 7BB-20-6 = 1800, 7BB-27-4 = 1500, 7BB-12-9 = 5120.

These are the *elements*, not housed buzzers. They are 0.22-0.54 mm thick and must be clamped at
their node and given a cavity with a vent to be loud.

## TDK PS series piezoelectric buzzers (housed, external drive)
https://media.digikey.com/pdf/Data%20Sheets/TDK%20PDFs/PS%20Series_ps.pdf

Measuring method stated on the sheet: A-weighted, **10 cm**, anechoic chamber, rectangular-wave drive.

| Part | Outer Ø (mm) | **Height (mm)** | Pitch (mm) | SPL dB(A) @ 10 cm | Freq. (kHz) | Drive (Vo-p, square) |
|---|---|---|---|---|---|---|
| PS1240P02AT | 12.2 | 6.5 | 5 | 70 min. | 4 | 3 |
| **PS1240P02CT** | **12.2** | **3.5** | 5 | **60 min.** | 4 | **3** |
| PS1440P02BT | 14 | 8 | 5 | 75 min. | 4 | 3 |
| PS1420P02AT | 14 | 11 | 5 | 70 min. | 2 | 5 |
| PS1740P02 | 17 | 8 | 10 | 75 min. | 4 | 3 |
| **PS1740P02C1** | **17** | **5** | 10 | **60 min.** | 4 | 3 |
| PS1920P02 | 19 | 10.5 | 20 | 80 min. | 2 | 10 |
| PS1927P02 | 19 | 10.5 | 20 | 90 min. | 2.7 | 10 |

Read the trade-off directly off this table: at 3 V square-wave drive straight off a coin cell,
a **12.2 x 3.5 mm** housed buzzer gives **60 dB(A) at 10 cm**; buying 10 more dB costs 3 mm of
height. Nothing in the PS family that fits an 8 mm puck exceeds 60 dB(A) at 10 cm without a
boost converter.

## Micro dynamic speakers — Same Sky (formerly CUI Devices)
https://www.sameskydevices.com/catalog/audio/speakers/miniature-(10-mm~40-mm) and
https://www.digikey.com/en/product-highlight/c/cui/micro-speakers

> "Same Sky micro speakers feature compact packages from 10 mm to 18 mm ... The speakers feature
>  profiles as low as 2 mm, offer input power ratings as low as 0.003 W"
> "miniature speakers feature packages from 10 mm to 40 mm with profile depths as low as 2 mm"

So an off-the-shelf 10-18 mm micro speaker at 2 mm profile *is* stackable inside an 8 mm puck --
but it arrives with its own frame, magnet, cone and back volume, i.e. it duplicates volume that
the AirTag reclaims by making the shell itself the diaphragm.

## SMT CR2032 holders — the height problem
https://www.batterypoweronline.com/markets/component/ultra-low-profile-surface-mount-2032-coin-cell-holders/

Keystone's ultra-low-profile #2032 holders, part **1057** (bulk) / **1057TR** (tape and reel):
> "rise 2 mm above the PCB surface"; "Gold plated contacts"; "LCP, UL 94V-0 base";
> "dual-spring contacts"; "Built In Stabilization tabs"; designed for partial through-hole mounting.

Other standard 20 mm SMT retainers of the same class: Keystone **3002**, TE/Linx **BAT-HLD-001**
(both listed on DigiKey as "Battery Retainer Coin, 20.0mm 1 Cell SMD (SMT) Tab").

A retainer that rises 2 mm above the board plus a 3.2 mm cell puts the top of the cell about
3.2 mm above the board with the retainer arms overhanging it -- roughly 5.2 mm of the 8 mm budget
consumed on one side of the PCB before any component height. **This is the reason the AirTag has
no holder**: the cell is trapped between three stamped spring fingers on the carrier and the steel
cover that screws down on top of it, so the cell's own 3.2 mm is nearly all the height it costs.

## Loudness figures in the wild (weak sources, recorded for completeness)

* iFixit, measured, "one iPhone-Mini-length away": **about 78-80 dB** for AirTag 1. Distance is
  ~13 cm (iPhone 12 mini height 131.5 mm). This is the only measurement from a teardown lab found.
* Chipolo ONE / ONE Point / Pop: **"up to 120 dB"** -- manufacturer claim, no distance stated,
  https://chipolo.net/en/products/chipolo-one . Not comparable to the iFixit figure.
* Apple: AirTag 2 speaker is "50% louder" than AirTag 1 -- marketing claim, no dB, no distance.
  50% louder in loudness (sones) is about +6 dB; 50% more sound *power* is about +1.8 dB. Apple has
  not said which it means, so **do not convert this number**.
* atechsland.com claims "approximately 40 to 60 decibels" for an AirTag -- unsourced blog, no
  distance or weighting. **Unverified; do not use.**
