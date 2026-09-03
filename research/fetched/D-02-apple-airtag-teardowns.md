# AirTag / AirTag 2 — teardowns and official pricing

Fetched: 2026-09-03

## TechInsights, "Apple AirTag Teardown"
URL: https://www.techinsights.com/blog/apple-airtag-teardown

- Nordic **nRF52832**, 90 nm, WLCSP50 package
- Apple **U1 UWB SiP**, 16 nm, with embedded crystal oscillator and a Sony RF switch
- Maxim class-D audio amplifier
- "single frame with all three antennas designed on it"
- Radio IC footprint "less than 30 mm2, or 6%, of the entire available PCB area"
- COST: "estimated manufacturing cost of USD 10 (not including software costs and R&D)",
  against retail "less than USD 30"

## Adam Catley, "Apple AirTag Reverse Engineering"
URL: https://adamcatley.com/AirTag.html

Part numbers read off the board:
- Nordic **nRF52832** (BLE + NFC)
- Apple **U1** UWB (die marked "TMKA75")
- Bosch **BMA280** 3-axis accelerometer
- GigaDevice **GD25LE32D** 32 Mbit NOR flash
- Maxim **MAX98357AEWL** class-D audio amp
- TI **TPS62746** buck converter
- TI **TLV9001IDPWR** op-amp
- Panasonic **CR2032** (225 mAh, 3 V)
- 5x 100 uF electrolytic capacitors
- NFC / BLE / UWB antennas are custom LDS (laser direct structuring) on a plastic frame

## iFixit, "AirTag Teardown: Yeah, This Tracks"
URL: https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks

- Confirms nRF52832 + U1 + GD25LE32D + MAX98357B + TLV9001 + TPS62746 + BMA28x
- Adds ON Semi **FPF2487** over-voltage protection load switch
- Battery CR2032, 0.66 Wh, user-replaceable — "the first in any Apple product in years"
- Speaker: "a coil of copper to form a speaker" with a magnet driver — a real voice coil,
  NOT a piezo. This is the single most expensive mechanical difference vs every clone.
- "Donut-shaped logic board with gilded plastic antenna frame"

## AirTag 2 (MacRumors, 2026-01-26)
URL: https://www.macrumors.com/2026/01/26/10-things-to-know-about-the-new-airtag-2/

- Price unchanged: "$29" single, "a pack of four available for $99", free engraving
- Shipping from "Wednesday, January 28" (2026)
- "UWB 2" second-generation Ultra Wideband chip; Precision Finding "1.5x further away than before"
- Precision Finding now also on Apple Watch Series 9+ / Ultra 2+
- Speaker "up to 50 percent louder than the speaker in the original"
- "a newer Bluetooth specification with increased range"
- 11.8 g (7% heavier than gen 1), IP67, still CR2032, "more than a year" of battery
- Requires iOS 26.2.1
