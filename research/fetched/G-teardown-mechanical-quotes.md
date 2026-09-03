# Mechanical quotes from the AirTag teardowns

All fetched 2026-09-03.

## Adam Catley, "Apple AirTag Reverse Engineering" — https://adamcatley.com/AirTag.html
(also mirrored at https://github.com/adamcatley/adamcatley.github.io/blob/master/docs/AirTag.md)

> "Note: Removing the PCB is likely to cause damage due to the thin PCB and being soldered to
>  the plastic tray."

> "They are all etched onto a single piece of plastic using Laser Direct Structuring (LDS) and
>  then soldered to the PCB around the edge. The NFC antenna also has a short trace on the other
>  side of the plastic (connected with a via at each end) to return the inside end of the coil to
>  the PCB."

> "### Speaker
>  The voice coil is glued to the outer plastic shell which acts as a diaphragm. Due to the fixed
>  magnet, it moves back and forth when the coil is energised, producing sound to act as the speaker."

> "The AirTag operates the same whether the voice coil is connected or not."

> "The coil can be disconnected without disassembly. The AirTag operates as normal without the
>  voice coil connected. ... Further, the magnet can be removed instead, if the AirTag is updated
>  to check for an open circuit."

> "There are 2 positive battery terminals. Both need 3V applied to boot the AirTag.
>  However, only the left side battery terminal powers the electronics. The voltage on the
>  right-side terminal is sensed but consumes only ~50nA in all modes."

> "There are 5 100uF capacitors around the edge of the top side of the PCB. They keep the device
>  powered up for several seconds with the battery removed."

Pin table extract: net "1 | Speaker | One end of the voice coil"; "38 | Speaker | The other end
of the voice coil". Antenna list: "Bluetooth Low Energy (left) - 2.4GHz; NFC (middle) - 13.56MHz;
Ultra-Wideband (right) - 6.5-8GHz". "The NFC antenna is located behind the white cover."

**Smallest-possible-dimensions table** (Catley's "AirTag in a host device" section):

| Version | Diameter | Height |
|---|---|---|
| Stock | 32 mm | 8.0 mm |
| Disassembled | 26 mm | 3.3 mm |

> "The host device's battery could be used for power, with the device casing acting as a diaphragm
>  for the speaker by attaching the voice coil. The smallest possible dimensions while retaining
>  all functionality is: ..."

Disassembly note: the grey ring is pried around to pull the inside piece out; plastic tabs are
glued to the white plastic at **2, 6 and 10 o'clock**; the metal disk that comes out is the
speaker magnet.

## iFixit, "AirTag Teardown: Yeah, This Tracks" — https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks

> "the relative darkness of the AirTag is due to a hefty central speaker magnet and its steel
>  battery cover - both fairly opaque to X-rays."

> "Did you notice the 'button' on the underside of the cover? That's not a clickable button ...
>  but rather the magnet we saw earlier in the X-ray. It sits right inside the donut-shaped logic
>  board, nested into a coil of copper to form a speaker. You read that right - the AirTag's body
>  is essentially a speaker driver. Power is sent to the voice coil, which drives the magnet
>  mounted to the diaphragm - in this case, the plastic cover where the battery lives - which
>  makes the sounds that lead you to your lost luggage."

> "Magnets not only add weight, they take up a lot of space. The dinky piezoelectric speakers in
>  the Mate and SmartTag made just as much, if not more, noise in our testing, so pure volume
>  isn't the answer. Looks like one corner Apple refused to cut on this tiny disk is sound quality."

> "measuring the decibel level at one iPhone-Mini-length away from the AirTag, the Hole-y One was
>  within a +/- 1 dB margin of error from a brand new 'Tag (about 78-80 dB). Considering Apple is
>  using the plastic dome itself as the speaker diaphragm, this comes as a pleasant surprise."

> "To drill through your AirTag safely, you'll need to bore through one of the notches in the
>  circuit board / antenna shield ... made for the clips that hold the tag together. We've
>  highlighted the three notches ... they roughly correspond to the clips for the metal battery
>  cover ... In a perfect world you'll miss the clip itself ... and only go through glue."

> "It's stubbornly glued in place ... A delicately soldered antenna housing surrounds the board,
>  and a very fragile copper voice coil lines the middle of the donut. The board is clearly
>  designed to stay put."

> "the AirTag board is layered. At left is the whole assembly as seen from the top, with the copper
>  voice coil in the center, still attached via two solder joints. The board nests inside a gilded
>  plastic antenna frame ... on the far right we've got the underside of the board."

> "Side one of the board is home to a 3-axis accelerometer, battery contact pins, and those voice
>  coil solder points."

> "Both AirTags and SmartTags use 3-volt CR2032 coin cell batteries, while the Tile uses the
>  smaller CR1632 cell. ... the 20 mm cells have a .66 Wh capacity, while the Tile's 16 mm cell
>  only has about .39 Wh."

> "the AirTag about 1.5 times as thick as the Tile"

**Note the contradiction with Catley**: iFixit writes that the magnet is "mounted to the
diaphragm"; Catley writes that the *coil* is glued to the shell and the magnet is fixed. Catley's
version is the one consistent with the rest of the evidence — the coil ends terminate on the PCB
("still attached via two solder joints" per iFixit itself), and iFixit's own AirTag 2 teardown
describes "two fine wires leading from the speaker coil to the PCB", i.e. flying leads to a
*moving* coil. Treat the AirTag as a **moving-coil, fixed-magnet driver whose diaphragm is the
white shell**.

## iFixit user teardown 218935 — https://www.ifixit.com/Teardown/Apple+Air+Tag+Teardown/218935

> "Twist the metal backplate off of the plastic case to reveal the battery compartment"
> "Use an opening pick or small flathead screwdriver to carefully unfasten the clips holding the
>  two plastic cases together."
> "The PCB is encased in a plastic shell with the antenna coil on top. To remove the PCB, carefully
>  slide an opening pick around the edge, and desolder or break off the four connections to the PCB."

## Circuit Cellar, "AirTag Teardown and Security Analysis" (Colin O'Flynn) — https://circuitcellar.com/research-design-hub/design-solutions/airtag-teardown-and-security-analysis/

> "The AirTag is a thin (0.3mm) PCB supported by a plastic holder, which also serves to hold the
>  various antennas in position."

## TechInsights, "Apple AirTag Teardown" — https://www.techinsights.com/blog/apple-airtag-teardown

> nRF52832 package is "WLCSP50", "75% smaller than the larger 48-pin 6 mm x 6 mm QFN option"
> Apple U1 UWB SiP: "total package area of 20.58 mm2"
> "the radio ICs of the Apple AirTag take up less than 30 mm 2, or 6%, of the entire available PCB area"
> Estimated manufacturing cost "USD 10 (not including software costs and R&D)"

If "less than 30 mm2" really is 6%, the total available PCB area is about **500 mm2**. Derived,
not stated; treat as an order-of-magnitude anchor only.

## IT Home (IT之家), 2026-01-29 — https://www.ithome.com/0/917/370.htm
Reporting Joseph Taylor's AirTag 2 teardown video of 2026-01-28.

> 「主板变薄，增大了扬声器线圈的物理尺寸，并使用了大量胶水固定组件。」
> "The main board is thinner, the physical size of the speaker coil has been increased, and a
>  large amount of glue is used to fix the components."

> 「由于苹果采用了大量胶水进行封装，拆解难度显著增加。该博主去除粘合剂后，发现 AirTag 2 的电路板（PCB）
>  较第一代更为纤薄，此外苹果还微调电池连接点布局，板上还新增了类似 QR 码的制造标记及测试触点。」
> "Because Apple used a great deal of glue for encapsulation, disassembly is markedly harder.
>  After removing the adhesive the blogger found the AirTag 2 PCB is thinner than the first
>  generation's; Apple also slightly adjusted the battery contact layout, and added a QR-code-like
>  manufacturing mark and test pads to the board."

> 「苹果为了兑现"音量提升 50%"的承诺，在 AirTag 2 内部配备了物理尺寸更大的扬声器线圈。值得注意的是，
>  相比第一代较为容易取下的扬声器磁铁，新款中的磁铁更牢固，难以移动。」
> "To deliver on the '50% louder' promise Apple fitted a physically larger speaker voice coil
>  inside AirTag 2. Notably, compared with the first generation's relatively easy-to-remove
>  speaker magnet, the magnet in the new model is more firmly fixed and hard to move."

> 「外观方面，AirTag 2 沿用了初代设计 ... 最直观的视觉变化仅在于金属后盖上的激光雕刻铭文：苹果将文字改为
>  全大写格式，并新增了防水防尘等级、Find My（查找）网络及 NFC 功能的相关标识。」
> "Externally AirTag 2 keeps the first-generation design ... the only visible change is the laser
>  engraving on the metal back cover: Apple switched the text to all caps and added markings for
>  the ingress-protection rating, the Find My network and NFC."

## iFixit AirTag 2 teardown, via 9to5Mac 2026-02-05 — https://9to5mac.com/2026/02/05/ifixit-tears-down-new-airtag-finds-50-louder-speaker-still-100-easy-to-disable/

> The speaker is "50% louder"; the assembly includes "two fine wires leading from the speaker coil
>  to the PCB"; the speaker "remains easy to disable" by removing those wires with a soldering iron.
> "Apple's U2 Ultra Wideband chip"; "upgraded SoC that handles Bluetooth and NFC functionality".

## Hackaday, "Teardown Of An Apple AirTag 2 With Die Shots", 2026-02-02 — https://hackaday.com/2026/02/02/teardown-of-an-apple-airtag-2-with-die-shots/

> "the small speaker, which is surrounded by the antenna for the ultrawide band (UWB) feature"
> the speaker is "nestled deep inside, well away from the battery. This is said to make disabling
>  it much harder without a destructive disassembly."
Original source: electronupdate, https://www.youtube.com/watch?v=UjUIXqiAIgA and
https://electronupdate.blogspot.com/2026/01/reverse-engineering-apple-airtag-2.html
