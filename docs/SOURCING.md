# Sourcing — every placed part on halo_rev_a, with an order code that was read back

*Generated from `spec/bom-resolved.json` by `tools/gen_sourcing.py` at `ef3431e`. Prices and stock were read on **2026-09-04** and every one of them carries that date. Nothing on this page is typed by hand.*

## The count

| | |
|---|--:|
| Placed references in the release bill of materials | **42** |
| References covered here | **42** |
| Bill-of-materials lines | 26 |
| Lines **RESOLVED** — order code fetched, manufacturer part number and package both matched | **22** |
| Lines **RESOLVED BY REPLACEMENT** — specified part is end-of-life, a buyable equivalent is named | **1** |
| **Lines that now name a part a factory can buy** | **23** of 26 |
| Lines with a documented alternate | **23** of the 23 machine-placed lines (LS1 and BT1 carry theirs in prose) |
| Resolved lines that are a JLCPCB **Basic** part | **2** of 22 |
| Distinct **Extended** order codes on the board | **20** |
| Feeder fee those Extended parts cost, per order | **$61.40** |
| Solder joints, measured | **131** |

- **CANNOT DETERMINE** — `C24, C25` (1.1nF)
- **DNP** — `C14, C15, C16, C17` (DNP)
- **RESOLVED BY REPLACEMENT** — `LS1` (7BB-20-3)
- **NOT AN SMT LINE** — `BT1` (CR2032)

## How every number here was obtained

Two endpoints, both plain HTTPS, both re-runnable:

- **LCSC** — `GET https://www.lcsc.com/product-detail/<code>.html, __NEXT_DATA__ application/json blob`
- **JLCPCB** — `POST https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList {currentPage,pageSize,keyword}`

**Two checks make this not a tool that lies** (`docs/TOOLS-THAT-LIE.md`). An order code is accepted only if:

1. the **manufacturer part number** the vendor returns for it matches the one the line asks for, and
2. the **package** the vendor returns for it matches the size of the land pattern the release bill of materials places, read off that file's own Footprint column.

The second check is the one that catches this board's actual defect, and no price check can: a 0402 order code under a 0201 land pattern is a real part, correctly valued, deeply stocked and sanely priced. It is simply twice the size of the pads it is going on.

Both checks are **broken on purpose** by `python3 tools/resolve_bom.py --self-test`, which asserts that a nonexistent order code refuses rather than invents, that the L10's code claimed as an L15 fails, that a 0402 part on a 0201 pad fails, and that halo's own battery land pattern — for which there is no size rule — comes back CANNOT DETERMINE rather than waving through whatever the vendor happened to say. **11 of 11 pass.** Writing that self-test found a real bug in this tool: the page's JSON blob carries recommended and recently-viewed products beside the one asked for, and a first-match walk returned a JST connector for a piezo bender's order code. The parser now requires the node's own `productCode` to be the code requested.

> Two channels, never mixed. price_usd is LCSC RETAIL (you buy the reel). jlcpcb_price_usd is what JLCPCB charges when IT supplies the part during assembly. They differ by up to 2x and the assembly number is the one that belongs in a PCBA quote.

> A price at a quantity the vendor's ladder does not reach is null. Nothing here is extrapolated.

## The bill of materials

Price columns are **JLCPCB assembly** prices — what the factory pays when JLC supplies the part during placement — at the piece count a build of that many boards actually buys. LCSC retail prices and the full ladders are in `spec/bom-resolved.json`.

| Ref | Qty | Value | Function | LCSC | MPN | Mfr | Land pattern | Vendor pkg | Pkg check | Lib | JLC stock | @10 | @100 | @1k | @10k |
|---|--:|---|---|---|---|---|---|---|---|---|--:|--:|--:|--:|--:|
| **C1, C2, C3, C4** | 4 | 100nF | SoC supply decoupling, one per VDD pin | [C5142565](https://www.lcsc.com/product-detail/C5142565.html) | `TCC0201X5R104K100ZT` | CCTC | `C_0201_0603Metric` | 0201 | **ok** | extended | 6,133,888 | $0.0013 | $0.0013 | $0.0010 | $0.0008 |
| **C5, C8** | 2 | 2.2uF | SoC DEC/DCDC reservoir | [C335106](https://www.lcsc.com/product-detail/C335106.html) | `GRM033R61A225KE47D` | muRata | `C_0201_0603Metric` | 0201 | **ok** | extended | 97,335 | $0.0233 | $0.0233 | $0.0189 | $0.0165 |
| **C6** | 1 | 10nF | SoC decoupling | [C76941](https://www.lcsc.com/product-detail/C76941.html) | `GRM033R71A103KA01D` | muRata | `C_0201_0603Metric` | 0201 | **ok** | extended | 368,597 | $0.0047 | $0.0047 | $0.0039 | $0.0034 |
| **C7** | 1 | 2.2nF | SoC decoupling | [C161479](https://www.lcsc.com/product-detail/C161479.html) | `GRM033R71A222KA01D` | muRata | `C_0201_0603Metric` | 0201 | **ok** | extended | 11,619 | $0.0028 | $0.0028 | $0.0022 | $0.0019 |
| **C9, C10, C11, C12** | 4 | 10uF | bulk rail capacitance (4 x 10 uF replaces Apple's 5 x 100 uF) | [C15525](https://www.lcsc.com/product-detail/C15525.html) | `CL05A106MQ5NUNC` | Samsung Electro-Mechanics | `C_0402_1005Metric` | 0402 | **ok** | **basic** | 9,701,120 | $0.0256 | $0.0256 | $0.0192 | $0.0142 |
| **C13** | 1 | 100pF | battery-sense divider settling cap | [C76922](https://www.lcsc.com/product-detail/C76922.html) | `GRM0335C1H101JA01D` | muRata | `C_0201_0603Metric` | 0201 | **ok** | extended | 873,542 | $0.0066 | $0.0066 | $0.0054 | $0.0047 |
| **C18** | 1 | 1.5pF | 2.4 GHz match, Nordic reference network | [C435397](https://www.lcsc.com/product-detail/C435397.html) | `GJM0335C1E1R5WB01D` | muRata | `C_0201_0603Metric` | 0201 | **ok** | extended | 57,341 | $0.0337 | $0.0337 | $0.0244 | $0.0225 |
| **C19** | 1 | 2.0pF | 2.4 GHz match, Nordic reference network | [C668326](https://www.lcsc.com/product-detail/C668326.html) | `GJM0335C1E2R0WB01D` | muRata | `C_0201_0603Metric` | 0201 | **ok** | extended | 29,352 | $0.0949 | $0.0782 | $0.0636 | $0.0559 |
| **C20, C21** | 2 | 0.5pF | antenna tuning pi, shunt legs (values are placeholders until ce-rf's S11) | [C237424](https://www.lcsc.com/product-detail/C237424.html) | `GJM0335C1HR50WB01D` | muRata | `C_0201_0603Metric` | 0201 | **ok** | extended | 13,101 | $0.0257 | $0.0257 | $0.0181 | $0.0165 |
| **C22** | 1 | 0.3pF | 2.4 GHz match, series trim into the pi | [C3904589](https://www.lcsc.com/product-detail/C3904589.html) | `GJM0335C1HR30WB01D` | muRata | `C_0201_0603Metric` | 0201 | **ok** | extended | 24,048 | $0.0309 | $0.0309 | $0.0220 | $0.0200 |
| **C23** | 1 | 3.9pF | 2.4 GHz shunt at ANT (Nordic Table 82; node placement CANNOT DETERMINE) | [C1852416](https://www.lcsc.com/product-detail/C1852416.html) | `GJM0335C1E3R9WB01D` | muRata | `C_0201_0603Metric` | 0201 | **ok** | extended | 13,804 | $0.0243 | $0.0243 | $0.0171 | $0.0156 |
| **C24, C25** | 2 | 1.1nF | NFC antenna tuning, series pair across the coil - MUST BE MATCHED TO EACH OTHER | — | — | — | `C_0201_0603Metric` | — | — | — | — | — | — | — | — |
| **C14, C15, C16, C17** | 4 | DNP | crystal load capacitors, deliberately NOT FITTED (D-3: the nRF54L has on-die CAPVALUE load caps) | — | — | — | `C_0201_0603Metric` | — | — | — | — | — | — | — | — |
| **R1, R2** | 2 | 4.7M | battery-sense divider (4.7 M keeps the divider current in the nanoamps) | [C778408](https://www.lcsc.com/product-detail/C778408.html) | `0201WMF4704TEE` | UNI-ROYAL | `R_0201_0603Metric` | 0201 | **ok** | extended | 10,142 | $0.0019 | $0.0019 | $0.0015 | $0.0013 |
| **R5, R6, R7, R8, R10** | 5 | 10k | I2C/SWD pull-ups and strapping | [C473048](https://www.lcsc.com/product-detail/C473048.html) | `0201WMF1002TEE` | UNI-ROYAL | `R_0201_0603Metric` | 0201 | **ok** | extended | 640,390 | $0.0012 | $0.0012 | $0.0010 | $0.0009 |
| **R9** | 1 | 100R | piezo drive series resistor (D11a: limits GPIO current into a 40 nF bender) | [C270366](https://www.lcsc.com/product-detail/C270366.html) | `0201WMF1000TEE` | UNI-ROYAL | `R_0201_0603Metric` | 0201 | **ok** | extended | 792,721 | $0.0020 | $0.0020 | $0.0016 | $0.0013 |
| **L1** | 1 | 4.7uH | SoC DC-DC inductor | [C76799](https://www.lcsc.com/product-detail/C76799.html) | `MLZ1608M4R7WT000` | TDK | `L_0603_1608Metric` | 0603 | **ok** | extended | 19,472 | $0.0600 | $0.0502 | $0.0416 | $0.0368 |
| **L2** | 1 | 2.7nH | 2.4 GHz match, Nordic reference network | [C7216765](https://www.lcsc.com/product-detail/C7216765.html) | `LQP03HQ2N7B02D` | muRata | `L_0201_0603Metric` | 0201 | **ok** | extended | 14,930 | $0.0502 | $0.0415 | $0.0338 | $0.0312 |
| **L3, L4** | 2 | 3.5nH | 2.4 GHz match, Nordic reference network | [C3911055](https://www.lcsc.com/product-detail/C3911055.html) | `LQP03HQ3N5B02D` | muRata | `L_0201_0603Metric` | 0201 | **ok** | extended | 8,477 | $0.0431 | $0.0431 | $0.0306 | $0.0280 |
| **L10** | 1 | 0R | antenna pi series element, fitted as a jumper so the board works untuned | [C473473](https://www.lcsc.com/product-detail/C473473.html) | `0201WMF0000TEE` | UNI-ROYAL | `L_0201_0603Metric` | 0201 | **ok** | extended | 4,472,786 | $0.0009 | $0.0009 | $0.0007 | $0.0006 |
| **U1** | 1 | nRF54L10-QFAA-R7 | the SoC: BLE + Channel Sounding + NFC-A (D12) | [C44800139](https://www.lcsc.com/product-detail/C44800139.html) | `NRF54L10-QFAA-R7` | NORDIC | `QFN-48-1EP_6x6mm_P0.4mm_EP4.4x4.4mm` | VFQFN-48 | **ok** | extended | 1,003 | $3.2296 | $2.5944 | $2.3800 | $2.3800 |
| **U2** | 1 | LIS2DW12TR | 3-axis accelerometer: motion wake, DULT unwanted-tracking detection | [C189624](https://www.lcsc.com/product-detail/C189624.html) | `LIS2DW12TR` | ST | `LGA-12_2x2mm_P0.5mm` | LGA-12(2x2) | **ok** | extended | 14,150 | $1.0381 | $0.7961 | $0.7343 | $0.7343 |
| **X1** | 1 | 32.768kHz | LFXO: the rotation clock the anti-stalking timing depends on | [C32346](https://www.lcsc.com/product-detail/C32346.html) | `Q13FC13500004` | EPSON | `Crystal_SMD_3215-2Pin_3.2x1.5mm` | SMD3215-2P | **ok** | **basic** | 777,983 | $0.1714 | $0.1352 | $0.1016 | $0.0805 |
| **X2** | 1 | 32MHz | HFXO: the radio reference | [C843260](https://www.lcsc.com/product-detail/C843260.html) | `NX2016SA-32MHZ-STD-CZS-5` | NDK | `Crystal_SMD_2016-4Pin_2.0x1.6mm` | SMD2016-4P | **ok** | extended | 13,631 | $0.3518 | $0.2908 | $0.2322 | $0.2090 |
| **LS1** | 1 | 7BB-20-3 | sounder: bare Ø20 x 0.22 mm piezo bender (D11a) | — | — | — | `—` | — | — | — | — | — | — | — | — |
| **BT1** | 1 | CR2032 | the cell. The CONTACTS are three sprung C5191 fingers on halo's own land pattern - there is no bought holder | — | — | — | `—` | — | — | — | — | — | — | — | — |

## The second source for every line

Lane T6 measured **212** of the main chip in stock. Single-sourcing is not a theoretical risk on this board, so every line carries an alternate that was fetched and matched the same way as the pick.

| Ref | Pick | LCSC stock | Alternate | LCSC stock | Why this pick, and what the alternate costs you |
|---|---|--:|---|--:|---|
| **C1, C2, C3, C4** | [C5142565](https://www.lcsc.com/product-detail/C5142565.html) `TCC0201X5R104K100ZT` | 5,981,500 | [C190183](https://www.lcsc.com/product-detail/C190183.html) `CC0201KRX5R6BB104` | 3,151,600 | Deepest 0201 100nF stock in the catalogue and the cheapest. 10 V X5R against a 3.0 V cell leaves margin for X5R DC-bias derating. |
| **C5, C8** | [C335106](https://www.lcsc.com/product-detail/C335106.html) `GRM033R61A225KE47D` | 59,700 | [C318539](https://www.lcsc.com/product-detail/C318539.html) `CL03A225MP3CRNC` | 312,460 | 10 V X5R at 2.2 uF in 0201 is a stretched dielectric; the Murata part is the deepest-stocked one and Murata publishes its DC-bias curve. |
| **C6** | [C76941](https://www.lcsc.com/product-detail/C76941.html) `GRM033R71A103KA01D` | 242,700 | [C285200](https://www.lcsc.com/product-detail/C285200.html) `0201X103K100NT` | 14,000 | X7R rather than X5R at no cost premium; 330k stock. |
| **C7** | [C161479](https://www.lcsc.com/product-detail/C161479.html) `GRM033R71A222KA01D` | 11,600 | [C2184294](https://www.lcsc.com/product-detail/C2184294.html) `GCM033R71A222KA03D` | 12,000 | THE SNAPSHOT'S FIRST CHOICE WAS WRONG BY A DAY. YAGEO C526940 held 29,573 in the 2026-09-03 catalogue snapshot and 600 when the live page was read on 2026-09-04 - a 49x collapse overnight. Both parts here are Murata, which is a real weakness in this line: it has two order codes and one manufacturer. |
| **C9, C10, C11, C12** | [C15525](https://www.lcsc.com/product-detail/C15525.html) `CL05A106MQ5NUNC` | 5,672,100 | [C7472949](https://www.lcsc.com/product-detail/C7472949.html) `HGC0402R5106M100NTEJ` | 1,999,080 | THE ONLY JLCPCB BASIC PART ON THIS BOARD. No feeder fee, ~10 M in stock. 6.3 V X5R at 3.0 V is inside spec but derates hard - the 10 V alternate is there if the measured rail droop needs it. |
| **C13** | [C76922](https://www.lcsc.com/product-detail/C76922.html) `GRM0335C1H101JA01D` | 825,900 | [C272870](https://www.lcsc.com/product-detail/C272870.html) `CC0201JRNPO9BN101` | 1,215,200 | C0G, so the ADC settling time and the 0.24 ms cell-removal collapse do not move with temperature. Deepest line on the board: 826 k and 1.2 M, two manufacturers. |
| **C18** | [C435397](https://www.lcsc.com/product-detail/C435397.html) `GJM0335C1E1R5WB01D` | 53,420 | [C88913](https://www.lcsc.com/product-detail/C88913.html) `GRM0335C1H1R5WA01D` | 86,300 | Murata GJM03 is the high-Q RF series the Nordic reference network assumes; a general-purpose C0G would lower the match Q. The GRM alternate is that general-purpose C0G, 5x cheaper and deeper stocked - acceptable only once ce-rf has measured S11 with it. |
| **C19** | [C668326](https://www.lcsc.com/product-detail/C668326.html) `GJM0335C1E2R0WB01D` | 25,165 | [C577359](https://www.lcsc.com/product-detail/C577359.html) `CQ0201BRNPO8BN2R0` | 5,800 | Same GJM03 high-Q family as C18. THE MOST EXPENSIVE PASSIVE ON THE BOARD at $0.064/1k - 40x a plain C0G - because 2.0 pF in the GJM high-Q series is a thin line. The YAGEO CQ series alternate is the deepest non-Murata 2 pF that survived the live stock check; the snapshot's two better-looking candidates (C161383, C1855389) read 200 and ZERO on the live page. |
| **C20, C21** | [C237424](https://www.lcsc.com/product-detail/C237424.html) `GJM0335C1HR50WB01D` | 13,100 | [C85922](https://www.lcsc.com/product-detail/C85922.html) `GRM0335C1HR50WA01D` | 132,200 | THE SCHEMATIC ASKED FOR GJM0335C1ER50WB01 (25 V), which is C464955 with 329 pieces in stock - not orderable. The 50 V 1H variant is the same 0.5 pF part with 25x the stock. |
| **C22** | [C3904589](https://www.lcsc.com/product-detail/C3904589.html) `GJM0335C1HR30WB01D` | 23,660 | [C723329](https://www.lcsc.com/product-detail/C723329.html) `0201CG0R3B500NT` | 14,200 | GJM03 high-Q, 50 V. At 0.3 pF the parasitics of a cheap C0G are a large fraction of the value, so the RF series earns its price here. |
| **C23** | [C1852416](https://www.lcsc.com/product-detail/C1852416.html) `GJM0335C1E3R9WB01D` | 13,800 | [C285100](https://www.lcsc.com/product-detail/C285100.html) `0201CG3R9C250NT` | 14,300 | GJM03 high-Q. Alternate is 28x cheaper and adequate if this ends up being a DNP once ce-rf measures the real feed. |
| **C24, C25** | — | — | [C161371](https://www.lcsc.com/product-detail/C161371.html) `GRM0335C1E102JA01D` | 139,150 | NO 1.1 nF CAPACITOR EXISTS IN 0201 IN ANY DIELECTRIC, and none exists in 0402 either - the smallest 1.1 nF in the whole catalogue is 0603 (C710889), which is three sizes too big for this board. 1.2 nF C0G does not exist in 0201 either, so there is no bracketing pair. The only 0201 part in the neighbourhood is 1.0 nF C0G, and the schematic's own note says that lands the NFC tank 5.3 % high at 14.28 MHz. THE FIX IS FREE AND IT IS IN COPPER, NOT IN THE BOM: the tank tunes on L*C, so if each capacitor drops 1.109 nF -> 1.0 nF the series capacitance drops 554.6 -> 500 pF and the coil must rise by the same ratio, 554.6/500 = 1.1092, from ce-rf's measured 0.2449 uH to 0.2716 uH. The coil is etched, so that costs nothing but a re-run of ce-rf's inductance solve on a slightly longer 2-turn path. This is a BOARD CHANGE for lane B1, not a sourcing choice, and the alternate recorded here is the 1.0 nF part it would use. |
| **C14, C15, C16, C17** | — | — | — | — | Not a sourcing gap. These four pads are the four parts jlc.md counts as CANNOT DETERMINE, and the right answer is that they carry no order code because nothing is placed on them. |
| **R1, R2** | [C778408](https://www.lcsc.com/product-detail/C778408.html) `0201WMF4704TEE` | 10,100 | [C423341](https://www.lcsc.com/product-detail/C423341.html) `0201WMJ0475TEE` | 29,000 | THINNEST STOCK ON THE BOARD AFTER THE SoC. 4.7 M in 0201 is a rare value: seven parts exist in the whole catalogue and only two carry four figures of stock. Both pick and alternate are UNI-ROYAL, so this line has ONE manufacturer, not two. |
| **R5, R6, R7, R8, R10** | [C473048](https://www.lcsc.com/product-detail/C473048.html) `0201WMF1002TEE` | 600 | [C138117](https://www.lcsc.com/product-detail/C138117.html) `RC0201JR-0710KL` | 627,100 | The exact MPN the schematic named - it was simply carrying the 0402 part's order code. Half a million in stock. |
| **R9** | [C270366](https://www.lcsc.com/product-detail/C270366.html) `0201WMF1000TEE` | 713,400 | [C77623](https://www.lcsc.com/product-detail/C77623.html) `RC0201FR-07100RL` | 1,815,200 | Again the schematic's own MPN under its real order code. |
| **L1** | [C76799](https://www.lcsc.com/product-detail/C76799.html) `MLZ1608M4R7WT000` | 18,790 | [C394952](https://www.lcsc.com/product-detail/C394952.html) `CMH160808B4R7MT` | 49,800 | The schematic's own TDK part under its real order code. The alternate is AEC-Q200 with 700 mA rating vs the TDK's 350 mA. |
| **L2** | [C7216765](https://www.lcsc.com/product-detail/C7216765.html) `LQP03HQ2N7B02D` | 13,770 | [C76752](https://www.lcsc.com/product-detail/C76752.html) `MLG0603P2N7CT000` | 8,700 | The schematic's own Murata high-Q part under its real order code. The TDK MLG0603 is the standard second source for LQP03 and is Q=14 vs Q=20 - acceptable, measurably worse. |
| **L3, L4** | [C3911055](https://www.lcsc.com/product-detail/C3911055.html) `LQP03HQ3N5B02D` | 8,000 | [C206424](https://www.lcsc.com/product-detail/C206424.html) `LQP03TN3N5B02D` | 9,450 | 3.5 nH is a rare value: THREE parts exist in 0201 across the whole catalogue and the alternate holds only ~1.6 k. Both are Murata. If ce-rf's S11 permits 3.3 nH or 3.6 nH the sourcing risk vanishes. |
| **L10** | [C473473](https://www.lcsc.com/product-detail/C473473.html) `0201WMF0000TEE` | 4,142,500 | [C106228](https://www.lcsc.com/product-detail/C106228.html) `RC0201JR-070RL` | 1,019,400 | Sits in an inductor footprint on purpose; a 0 ohm 0201 resistor is the same land pattern. Both options carry 500k+. |
| **U1** | [C44800139](https://www.lcsc.com/product-detail/C44800139.html) `NRF54L10-QFAA-R7` | 671 | [C45022042](https://www.lcsc.com/product-detail/C45022042.html) `NRF54L05-QFAA-R` | 1,775 | D12. THE SINGLE LARGEST SUPPLY RISK ON THE BOARD - lane T6 measured 212 pieces. D18 says the L05 fallback is not forced by memory, so the alternate is a real second source, at 512 kB/96 kB and a 3,000-piece minimum packet. |
| **U2** | [C189624](https://www.lcsc.com/product-detail/C189624.html) `LIS2DW12TR` | 14,150 | [C110926](https://www.lcsc.com/product-detail/C110926.html) `LIS2DH12TR` | 297 | 50 nA in the lowest-power mode, the deciding number for a coin cell. PIN COMPATIBILITY WITH THE ALTERNATE IS READ OFF BOTH DATASHEETS, not assumed: LIS2DW12 Table 2 and LIS2DH12 Table 2 both give 1=SCL/SPC, 2=CS, 3=SDO/SA0, 4=SDA/SDI/SDO, 6=GND, and differ only at pin 5 (LIS2DH12 'Res, connect to GND' vs LIS2DW12 'NC, can be tied to VDD, VDDIO or GND'), which the board ties to GND either way. The cost is 500 nA against 50 nA - a build second source, not a design equal. REJECTED as an alternate on evidence: Silan SC7A20HTR (C19274408) has 106 k in stock and is a tenth of the price, but its own datasheet v0.7 p.5 gives pin 1 = SDO, 2 = SDx, 3 = VDDIO - a DIFFERENT PINOUT in the same LGA-12 2x2 body. It would short VDDIO to the SDO net on this land pattern. |
| **X1** | [C32346](https://www.lcsc.com/product-detail/C32346.html) `Q13FC13500004` | 657,565 | [C95361](https://www.lcsc.com/product-detail/C95361.html) `Q13FC13500049` | 134,310 | JLCPCB BASIC, so no feeder fee. CL 12.5 pF: THIS MUST BE CHECKED AGAINST THE nRF54L's on-die CAPVALUE RANGE, because D-3 deleted the external load capacitors. The alternate is the same Epson FC-135 body at CL 6 pF if the internal caps cannot reach 12.5 pF. |
| **X2** | [C843260](https://www.lcsc.com/product-detail/C843260.html) `NX2016SA-32MHZ-STD-CZS-5` | 12,840 | [C718072](https://www.lcsc.com/product-detail/C718072.html) `X201632MKB4SI` | 34,405 | CL 8 pF +/-10 ppm, which is what the schematic specified and what the vendor record confirms. The YXC alternate is the same 8 pF / +/-10 ppm at a third of the price with 60 k stock. |
| **LS1** | — | — | — | — | Hand-assembled and bonded to the shell, so the machine never touches it and it carries no LCSC code by design. THE SPECIFIED MURATA PART IS END-OF-LIFE and is replaced by the PUI Audio AB2036B-2, which is a specification-for-specification match at 0.215 mm rather than 0.22. Full evidence in the sounder section of docs/SOURCING.md and in the `cost.sounder` block of this file. |
| **BT1** | — | — | — | — | The schematic carried C7498149 here, which is a Lian Xin BS-CR2032-8 SMD BATTERY HOLDER. No holder is fitted - lane M's design puts three stamped fingers on halo's own three-pad footprint. The order code was wrong AND the part it named must not be ordered. |

## The sounder

**Specified:** D11a: Murata 7BB-20-3, 20.0 mm brass disc, 0.22 mm total, ~3.6 kHz

**Decision:** D20 supersedes D11a's PART CHOICE (not its acoustic reasoning) and names Same Sky CEB-2021. This lane followed that decision and re-verified it first-hand rather than restating it.

**Verdict: RESOLVED - BY REPLACEMENT, per D20. The specified part is end-of-life.**

### Why the specified part is not the part

- **The Murata 7BB-20-3 is end-of-life.** Four authorized channels agree, all read 2026-09-04: Digi-Key's product page says *"Obsolete and no longer manufactured"* with 0 stock; TME says *"Product withdrawn from the offer"*; RS Components returns `statusCode: STATUS_UNAVAILABLE` with an empty price-break array on both its SKUs; AXEL/ASONE Japan prefixes it [Discontinued].
- **It is not in the Chinese catalogues at all.** The keyword `7BB-20-3` returns ZERO rows from the JLCPCB assembly catalogue endpoint and from LCSC. Only 7BB-20-6C (C3812347), 7BB-20-6L0 (C3812354) and 7BB-20-6CL0 (C3812422) exist there, all at stockCount 0, and C3812347's LCSC page now returns HTTP 404 - which is D20's point that JLCPCB's library retains delisted parts, confirmed from the other end.
- **The quantity that exists is broker stock.** Win Source lists 23,886 and several unauthorized brokers list 3,000-36,000 pieces of a part Digi-Key says is no longer manufactured. Designing that in means single-sourcing a product on dead stock with no traceability.
- **The only authorized stock anywhere is 38 pieces** at TTI, Americas. That is a sample quantity, not a supply.
- **Murata's own live status could not be read and is recorded as CANNOT DETERMINE.** murata.com/products/productdetail redirects to a client-rendered SPA that returns a 5,961-byte shell to any fetch; the /webapi/PsdispRest endpoints return an error page; and Murata's published *Discontinued Products Information of Sound Components* lists only PKM, PKB, PKLCS, PKHPS, PKMC, PKMCS and VSB housed parts, with no 7BB entry, while stating that not all discontinued products are listed. It therefore neither confirms nor clears the series.

### What replaces it

**CEB-2021** — Same Sky (formerly CUI Devices) — [datasheet](https://www.sameskydevices.com/product/resource/ceb-2021.pdf) (1.01, 2024-09-11, fetched 2026-09-04 (HTTP 200, 238,947 bytes))

| | 7BB-20-3 (D11a asked for) | CEB-2021 (D20, what is buyable) |
|---|---|---|
| Diameter | 20.0 mm | **20.0 mm** |
| Total thickness | 0.22 mm | **0.21 mm +/-0.03** |
| Weight | — | 0.4 g |
| Ceramic layer | — | 0.1 mm +/-0.01 |
| Brass plate | — | 0.11 mm (derived: 0.21 total - 0.10 ceramic) |
| Ceramic / electrode Ø | — | 15.0 / None mm |
| Resonant frequency | ~3.6 kHz | **3,100 / 3,600 / 4,100 Hz** (min/typ/max) |
| Resonant impedance | — | ≤ 300 Ω |
| Capacitance | — | **21,000 pF** (15,750 / 21,000 / 26,250 @ 100 Hz) |
| Max input | — | 30 Vp-p |
| Plate | brass | brass |
| Termination | bare | **bare disc, externally driven, no wires and no housing** |
| Operating / storage | — | -20 to +70 / -30 to +80 °C |
| Authorized stock, 2026-09-04 | **0** (38 at TTI, Americas) | Digi-Key **3756** · Mouser **2202** |
| Price @10 / @100 / @1k / @10k | not orderable | **$0.5960 / $0.4580 / $0.3690 / $0.3150** |

*off Same Sky's own mechanical drawing, page 1, rendered at 150 dpi and read: n20 +/-0.1 brass, n15 +/-0.3 ceramic, 0.21 +/-0.03 total, 0.1 +/-0.01 ceramic. The specification table is extractable text; the drawing is not, so it was read as a picture.*

> **CEB-2021-L100 is the SAME ELEMENT WITH LEAD WIRES ALREADY ATTACHED and is a different order code, a different price and a different height. Digi-Key holds 4,261 of it and 3,756 of the bare part, so a buyer searching 'CEB-2021' will see the leaded one first. Order CEB-2021, not CEB-2021-L100.**

*Price: Mouser Electronics, ECIA member, authorized distributor, via oemstrade.com/search/CEB-2021, read 2026-09-04. Ladder: 1 $0.80, 10 $0.596, 25 $0.536, 50 $0.496, 100 $0.458, 250 $0.415, 500 $0.385, 1000 $0.369, 4000 $0.315. The 10,000 figure is the 4000-and-up break. Digi-Key (authorized, 3,756 in stock, part 2223-CEB-2021-ND) quotes EUR 0.2556 at 8,000, which is the $0.299-at-8,000 D20 recorded.*

- **D20 chose it and this lane re-derived the numbers rather than repeating them.** Every figure in the table above is read off Same Sky's own datasheet rev 1.01 fetched on 2026-09-04, and the thicknesses off its mechanical drawing rendered as an image, because the drawing is not extractable text. D20's headline numbers - Ø20 x 0.21 mm, brass, 3.6 kHz (3.1-4.1), 21 nF, <=300 ohm, 3,756 in stock - all hold.
- **It is bare and it is externally driven.** Two terminals, no wires, no housing, which is what D11a's anti-phase GPIO pair needs and what D17's flat shell interior requires. At 0.21 +0.03 = 0.24 mm worst case it uses a sixth of the ~1.5 mm above the module, and nothing about it approaches the 3.5 mm the mechanical lane measured as the hard limit.
- **The drive D11a specified still works, on the vendor's numbers.** At 21 nF typical and 3,600 Hz, two pins swinging 6 V peak-to-peak draw I = 2*pi*f*C*V = 2*pi*3600*21e-9*3 = **1.43 mA peak**, inside nRF54L high-drive GPIO. At the 26.25 nF maximum it is 1.78 mA, still inside. So R9 stays on the bill of materials and D11a's no-amplifier conclusion survives the part change.
- **R9's value is worth re-checking against this part, though.** The CEB-2021's resonant impedance is <=300 ohm, not the <=500 ohm of the Murata class D11a assumed. R9's 100 ohms is 4.5% of the element's 2.1 kohm reactance off resonance, but **at resonance it is up to a third of the load** and takes a third of the drive voltage with it. That is a loudness question for lane G's meter, not a sourcing one, but it is a number that changed when the part did.

### Second source

**AB2036B-2** — PUI Audio (Same Sky), Ø20.0 mm, 0.215 mm +/-10%, 3,600 ± 600 Hz, 20,000 pF, ≤500 Ω, Digi-Key 390 · Mouser 400 — [datasheet](https://puiaudio.com/file/specs-AB2036B-2.pdf) (A, 2024-03-06, fetched 2026-09-04 (HTTP 200, 159,631 bytes))

| | CEB-2021 (fitted) | AB2036B-2 (second source) |
|---|--:|--:|
| @10 | $0.5960 | $0.3620 (**−39%**) |
| @100 | $0.4580 | $0.2840 (**−38%**) |
| @1,000 | $0.3690 | $0.2200 (**−40%**) |
| @10,000 | $0.3150 | $0.1860 (**−41%**) |

A SECOND SOURCE THIS LANE FOUND THAT D20's NINE CANDIDATES DID NOT INCLUDE, and it is 40% cheaper at every break - $0.220 against $0.369 at a thousand, $0.186 against $0.315 at ten thousand, which is $0.149 a unit at a thousand. Ø20.0 mm brass, 0.215 mm +/-10%, 3,600 +/-600 Hz, 20 nF +/-30%, 30 Vp-p, bare two-pad, all read off the vendor's own datasheet and its dimensioned drawing. D20 rejected the PUI AB2036AF for having an alloy plate and a three-terminal feedback electrode; the -2 is a different part - brass plate, two terminals, externally driven - and was not among the nine.

D20's grounds for CEB-2021 hold and this lane did not overturn them: 0.21 mm against 0.215 is 0.005 mm thinner into a stack that has already spent 0.372 mm of D17's 0.542 mm of slack, and authorized stock is 5,958 pieces against 790 - 7.5x deeper, on a line with no third source. The AB2036B-2's ≤500 Ω resonant impedance against the CEB-2021's ≤300 Ω also makes R9's 100 Ω a 20% divider at resonance rather than 33%, which is lane G's to weigh. The cheaper part is recorded, priced and dated so whoever owns D20 can decide; this lane does not reopen a landed decision.

### Cautions

- **Order `CEB-2021`, not `CEB-2021-L100`.** The L100 is the same element with lead wires already attached: a different order code, roughly 45% dearer, and solder joints that stack on top of a height budget with 0.17 mm of slack left. Digi-Key holds 4,261 of the leaded part and 3,756 of the bare one, so a buyer searching the family name will meet the wrong one first.
- **Do not substitute the CEB-20D64 / CEB-20FD64** despite their far deeper stock (6,486 and 6,023 at Digi-Key). They are 0.43 mm thick, they arrive with lead wires, and at 10-13 nF they present half the capacitive load the GPIO drive was sized around. D20's physical finding is why: at Ø20 mm thin and high-frequency are mutually exclusive, and every 6.3-7.2 kHz element across three manufacturers measures 0.42-0.43 mm.
- **Skip LCSC and JLCPCB for this line entirely.** Of the 129 parts in JLCPCB's whole *Buzzer Plates* category, exactly one has stock (Dragonstate HE-2739E-C, 81 pieces, no datasheet published, and 27 mm). All 22 of the 20 mm bare benders in that catalogue are at zero. The Chinese factory buys this line through Digi-Key, Mouser or Same Sky direct, and it is a hand-assembly step either way.
- **The loudness is still unmeasured and D11a, D20 and this lane all say so.** A 3,600 Hz free-air element bonded to a stiff shell moves upward in loaded resonance; whether that lands 60 Phon at 25 cm is lane G's calibrated meter to answer. Nothing here converts a datasheet into a decibel.

## What the board should change

Sourcing found five things that are not sourcing decisions. They belong to lane B1, which owns `electronics/` and `out/release/board/`. This lane changed neither, and delivers them as a report.

### 1. 10 of the 15 distinct order codes on the schematic name a different component

This is the finding that closes the gap, and it is derived rather than asserted: `tools/resolve_bom.py` reads every order code out of `electronics/halo_rev_a/schematic.py` and asks `ce-fab data/jlcparts-slim.sqlite3` what each one actually is. 24 declaration sites, 15 distinct codes, **4 right, 1 naming a family rather than an orderable item, 10 naming a different component**. Verdict **FAIL**.

| Code on the sheet | The sheet says it is | The catalogue says it is | |
|---|---|---|---|
| `C1046` | `MLZ1608M4R7WT000` | `SDFL2012S100KTF` — 0805 | **WRONG** |
| `C1046539` | `LQP03HQ2N7B02D` | **no such LCSC code** | **WRONG** |
| `C1523` | `CL03C101JB3NNNC` | `0402B102K500NT` — 0402 | **WRONG** |
| `C1546` | `0201 C0G 1.1nF` / `CL03A104KA3NNNC` | `0402CG101J500NT` — 0402 | **WRONG** |
| `C15525` | `CL05A106MQ5NUNC` | `CL05A106MQ5NUNC` — 0402 | ok |
| `C1568` | `GJM0335C1E1R5WB01` / `GJM0335C1ER50WB01` | `0402CG4R0C500NT` — 0402 | **WRONG** |
| `C189624` | `LIS2DW12TR` | `LIS2DW12TR` — LGA-12 | ok |
| `C25076` | `0201WMF1000TEE` / `0201WMJ0000TEE` | `0402WGF1000TCE` — 0402 | **WRONG** |
| `C25744` | `0201WMF1002TEE` | `0402WGF1002TCE` — 0402 | **WRONG** |
| `C25765` | `0201WMF4704TEE` | `0402WGF2002TCE` — 0402 | **WRONG** |
| `C2827888` | `CL03A225MQ3CSNC` | `DB2EK-3.5-8P-BK-S` — P=3.5mm | **WRONG** |
| `C32346` | `FC-135 32.768kHz` | `Q13FC13500004` — SMD3215-2P | family name, not an order-code check |
| `C44800139` | `NRF54L10-QFAA-R7` | `NRF54L10-QFAA-R7` — VFQFN-48 | ok |
| `C7498149` | `CR2032` | `BS-CR2032-8` — SMD | **WRONG** |
| `C843260` | `NX2016SA-32MHZ` | `NX2016SA-32MHZ-STD-CZS-5` — SMD2016-4P | ok |

Two of those rows are worth reading twice. **`C1568` is quoted for five different capacitor values** — 0.3, 0.5, 1.5, 2.0 and 3.9 pF — and it is one part, a 4 pF 0402. **`C2827888` is quoted as a 2.2 µF ceramic** and is a DORABO 8-way 3.5 mm screw terminal block with 59 in stock. And **`C7498149` on BT1 is an SMD battery holder**, a part that must not be fitted at all, because lane M's contacts are three stamped sprung fingers on halo's own three-pad land pattern.

The pattern is one mistake repeated: the familiar **0402** basic-part codes were written down beside **0201** part numbers. **The manufacturer part numbers on the sheet were almost all correct** — `0201WMF1002TEE`, `LQP03HQ2N7B02D`, `MLZ1608M4R7WT000`, `GJM0335C1E1R5WB01` are all real parts in the right size, and every one of them has been given its real order code in the bill of materials above. Only the codes were wrong, and a wrong code is the one error a factory cannot catch for you.

### 2. Not one passive on this board is a JLCPCB Basic part, and it is the 0201 choice that does it

**Zero of the 9,030 0201 parts in the catalogue is a JLCPCB Basic part** — measured, not assumed. 0402 has 51 and 0603 has 118. So every 0201 line carries the $3.07 per-order feeder fee, and this board carries **20 of them = $61.40 per order**, against the 7 D15 assumed.

At a thousand units that is $0.0614 a unit and nobody cares. **At ten units it is $6.14 a unit**, which is more than every component on the board put together, and it is the single largest reason the prototype build is dearer than D15 says. If the first articles matter more than the thousand, moving the non-RF passives to 0402 is worth real money; if the thousand matters more, 0201 is free.

### 3. C24/C25: 1.1 nF cannot be bought in 0201, and the fix is in copper

NO 1.1 nF CAPACITOR EXISTS IN 0201 IN ANY DIELECTRIC, and none exists in 0402 either - the smallest 1.1 nF in the whole catalogue is 0603 (C710889), which is three sizes too big for this board. 1.2 nF C0G does not exist in 0201 either, so there is no bracketing pair. The only 0201 part in the neighbourhood is 1.0 nF C0G, and the schematic's own note says that lands the NFC tank 5.3 % high at 14.28 MHz. THE FIX IS FREE AND IT IS IN COPPER, NOT IN THE BOM: the tank tunes on L*C, so if each capacitor drops 1.109 nF -> 1.0 nF the series capacitance drops 554.6 -> 500 pF and the coil must rise by the same ratio, 554.6/500 = 1.1092, from ce-rf's measured 0.2449 uH to 0.2716 uH. The coil is etched, so that costs nothing but a re-run of ce-rf's inductance solve on a slightly longer 2-turn path. This is a BOARD CHANGE for lane B1, not a sourcing choice, and the alternate recorded here is the 1.0 nF part it would use.

### 4. C19 is the most expensive passive on the board

`GJM0335C1E2R0WB01D` at $0.0636 per piece at a thousand is 40× a plain C0G of the same value and more than the 32.768 kHz crystal. It is one 2.0 pF capacitor in the antenna match. If ce-rf's S11 measurement shows the Q of a general-purpose C0G is adequate, the alternate on this line saves about 0.0559 dollars a unit.

### 5. X1's load capacitance has not been checked against the SoC

JLCPCB BASIC, so no feeder fee. CL 12.5 pF: THIS MUST BE CHECKED AGAINST THE nRF54L's on-die CAPVALUE RANGE, because D-3 deleted the external load capacitors. The alternate is the same Epson FC-135 body at CL 6 pF if the internal caps cannot reach 12.5 pF.

**Deletion already made, and confirmed here:** the SPI flash a previous lane found sitting on the raw 3.0 V cell rail while rated 1.65–2.0 V is gone — commit `4e3dd52`, *"flash deleted as out-of-spec"*. It appears in no netlist, no placement and no bill of materials, so there was nothing to source and nothing was sourced.

## The cost roll-up, on measured numbers

Every **rate** below is lane E's, from `research/05-components-and-cost-model.md sections 10.3 and 11.6 (lane E, 2026-09-03)`, and this lane re-derives none of them. What this lane replaces is the three **inputs** that section had to assume:

| Input | D15 assumed | Measured here | How |
|---|--:|--:|---|
| Solder joints | 131 | **131** | JLCPCB's own solder-joint count per order code, ce-fab data/jlcparts-slim.sqlite3 column `joints`, multiplied by the quantity placed |
| Extended parts | 7 | **20** | every order code's `componentLibraryType`, live from JLCPCB |
| Component prices | a candidate list | **the placed board** | every line, both endpoints, 2026-09-04 |

The joint count landing on **131**, exactly D15's assumption, is an independent confirmation of that half of the model.

| Qty | BOM | PCB | Assembly | Enclosure | Tooling | Labour | **Total/unit** | D15 | **Δ** | with the C24/C25 fix |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 10 | $6.3895 | $6.211 | $7.3206 | $1.20 | $0.00 | $0.30 | **$21.4211** | $19.25 | **+$2.1711** | $21.4523 |
| 100 | $5.2161 | $0.692 | $0.9207 | $1.20 | $0.00 | $0.30 | **$8.3288** | $9.28 | **-$0.9512** | $8.3600 |
| 1,000 | $4.6213 | $0.140 | $0.2807 | $0.90 | $0.00 | $0.15 | **$6.0920** | $7.17 | **-$1.0780** | $6.1148 |
| 10,000 | $4.4795 | $0.085 | $0.2167 | $0.30 | $0.40 | $0.08 | **$5.5612** | $6.75 | **-$1.1888** | $5.5772 |

**The Total/unit column is a floor, not a quote: C24,C25 carry no price** and contribute zero to it. A total with a missing line is stated as missing, never padded with a plausible number. The last column is the same build with the recommended fix taken on every unresolved line — `C24, C25` → C161371 `GRM0335C1E102JA01D` — which is a real fetched part but needs a board change first, so it is reported beside the honest number and never in place of it.

Fee constants, so the arithmetic can be checked: $8.18 setup + $1.53 stencil + $3.07 × 20 extended parts, amortised over the build, plus $0.0016 × 131 joints per unit. Source: https://jlcpcb.com/help/article/pcb-assembly-price. Staleness: the fee table is the archived 2024-08-29 revision; ce-fab's data/jlc-pricing.json records that the $8 Economic setup fee still held on 2026-09-03 and the per-joint rate had moved 0.0017 -> 0.0016.

### Why the delta goes the way it does

At a thousand units the board comes out at **$6.09** against D15's $7.17, **-$1.08 a unit**. Two thirds of that is not a price movement at all: D15 priced a *candidate* bill of materials from research/05 §5.2, which still carried five 100 µF bulk capacitors sized for a voice coil and an ultra-wideband burst. The board that exists carries four 10 µF 0402 instead, because D11a and D12 deleted both of those loads. The rest is that the real 0201 passives are cheaper than the 0402 parts whose codes the sheet was carrying.

**The ten-unit row moves the other way, +$2.17, and that is the honest news in this table.** Feeder fees do not amortise at ten. 20 extended parts instead of 7 costs $3.99 a unit at that volume, and it is the whole of the difference. First articles cost more than D15 said; a thousand costs less.

## What could stop the line

Every line's JLCPCB stock against what a build actually consumes. Cover is stock divided by need; **a factory buys attrition too, and nobody else stops buying while you order, so anything under about 3x is a line that can stop.**

| Ref | Part | JLC stock | 1k build needs | cover | 10k build needs | cover | Alternate stock |
|---|---|--:|--:|--:|--:|--:|--:|
| **U1** | `NRF54L10-QFAA-R7` | 1,003 | 1,000 | **1.0×** | 10,000 | **0.1×** | 1,775 |
| **L3, L4** | `LQP03HQ3N5B02D` | 8,477 | 2,000 | 4.2× | 20,000 | **0.4×** | 9,454 |
| **R1, R2** | `0201WMF4704TEE` | 10,142 | 2,000 | 5.1× | 20,000 | **0.5×** | 29,417 |
| **C20, C21** | `GJM0335C1HR50WB01D` | 13,101 | 2,000 | 6.6× | 20,000 | **0.7×** | 135,053 |
| **C7** | `GRM033R71A222KA01D` | 11,619 | 1,000 | 11.6× | 10,000 | **1.2×** | 12,030 |
| **X2** | `NX2016SA-32MHZ-STD-CZS-5` | 13,631 | 1,000 | 13.6× | 10,000 | **1.4×** | 41,666 |
| **C23** | `GJM0335C1E3R9WB01D` | 13,804 | 1,000 | 13.8× | 10,000 | **1.4×** | 14,364 |
| **U2** | `LIS2DW12TR` | 14,150 | 1,000 | 14.2× | 10,000 | **1.4×** | 1,162 |
| **L2** | `LQP03HQ2N7B02D` | 14,930 | 1,000 | 14.9× | 10,000 | **1.5×** | 8,781 |
| **L1** | `MLZ1608M4R7WT000` | 19,472 | 1,000 | 19.5× | 10,000 | **1.9×** | 56,281 |
| **C22** | `GJM0335C1HR30WB01D` | 24,048 | 1,000 | 24.0× | 10,000 | **2.4×** | 15,149 |
| **C19** | `GJM0335C1E2R0WB01D` | 29,352 | 1,000 | 29.4× | 10,000 | **2.9×** | 5,854 |
| **C5, C8** | `GRM033R61A225KE47D` | 97,335 | 2,000 | 48.7× | 20,000 | 4.9× | 352,713 |
| **C18** | `GJM0335C1E1R5WB01D` | 57,341 | 1,000 | 57.3× | 10,000 | 5.7× | 86,329 |
| **R5, R6, R7, R8, R10** | `0201WMF1002TEE` | 640,390 | 5,000 | 128.1× | 50,000 | 12.8× | 930,146 |
| **C6** | `GRM033R71A103KA01D` | 368,597 | 1,000 | 368.6× | 10,000 | 36.9× | 14,016 |
| **X1** | `Q13FC13500004` | 777,983 | 1,000 | 778.0× | 10,000 | 77.8× | 135,144 |
| **R9** | `0201WMF1000TEE` | 792,721 | 1,000 | 792.7× | 10,000 | 79.3× | 2,067,381 |
| **C13** | `GRM0335C1H101JA01D` | 873,542 | 1,000 | 873.5× | 10,000 | 87.4× | 1,251,731 |
| **C1, C2, C3, C4** | `TCC0201X5R104K100ZT` | 6,133,888 | 4,000 | 1533.5× | 40,000 | 153.3× | 3,271,572 |
| **C9, C10, C11, C12** | `CL05A106MQ5NUNC` | 9,701,120 | 4,000 | 2425.3× | 40,000 | 242.5× | 1,999,506 |
| **L10** | `0201WMF0000TEE` | 4,472,786 | 1,000 | 4472.8× | 10,000 | 447.3× | 1,201,384 |

**1 of 22 lines cannot cover a thousand units three times over — U1. 12 of 22 cannot cover ten thousand — U1 · L3/L4 · R1/R2 · C20/C21 · C7 · X2 · C23 · U2 · L2 · L1 · C22 · C19.**

The ten-thousand column is the one to read before quoting that row of the cost table. It is not a price problem — it is that the catalogue does not hold the parts, and several of these are values with only two or three entries in the whole 685,000-part catalogue. Reserving stock, or asking ce-rf whether a neighbouring value will do, is cheaper than discovering it at the purchase order.

Minimum packet sizes worth knowing before an order is placed — several of these parts cannot be bought from LCSC in small numbers at all, though JLCPCB will consume them from its own reels during assembly:

| Ref | Part | LCSC minimum packet |
|---|---|--:|
| C1, C2, C3, C4 | `TCC0201X5R104K100ZT` | 15,000 |
| C5, C8 | `GRM033R61A225KE47D` | 15,000 |
| C6 | `GRM033R71A103KA01D` | 15,000 |
| C7 | `GRM033R71A222KA01D` | 15,000 |
| C9, C10, C11, C12 | `CL05A106MQ5NUNC` | 10,000 |
| C13 | `GRM0335C1H101JA01D` | 15,000 |
| C18 | `GJM0335C1E1R5WB01D` | 15,000 |
| C19 | `GJM0335C1E2R0WB01D` | 15,000 |
| C20, C21 | `GJM0335C1HR50WB01D` | 15,000 |
| C22 | `GJM0335C1HR30WB01D` | 15,000 |
| C23 | `GJM0335C1E3R9WB01D` | 15,000 |
| R1, R2 | `0201WMF4704TEE` | 15,000 |
| R5, R6, R7, R8, R10 | `0201WMF1002TEE` | 15,000 |
| R9 | `0201WMF1000TEE` | 15,000 |
| L1 | `MLZ1608M4R7WT000` | 4,000 |
| L2 | `LQP03HQ2N7B02D` | 15,000 |
| L3, L4 | `LQP03HQ3N5B02D` | 15,000 |
| L10 | `0201WMF0000TEE` | 15,000 |
| U1 | `NRF54L10-QFAA-R7` | 1,000 |
| U2 | `LIS2DW12TR` | 10,000 |
| X1 | `Q13FC13500004` | 3,000 |
| X2 | `NX2016SA-32MHZ-STD-CZS-5` | 3,000 |

## Datasheets

| Ref | Part | Datasheet |
|---|---|---|
| C1, C2, C3, C4 | `TCC0201X5R104K100ZT` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/0432613d484f4f946fa8f7c93b61cf7a.pdf?productCode=C5142565) |
| C1, C2, C3, C4 (alt) | `CC0201KRX5R6BB104` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/5b3aae1e7925073bc9bd92db48d7aba2.pdf?productCode=C190183) |
| C5, C8 | `GRM033R61A225KE47D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/a4d1e2744bd5d44ba57842651a3fd598.pdf?productCode=C335106) |
| C5, C8 (alt) | `CL03A225MP3CRNC` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/e5e1a6cb60bd6713d2271da395963f60.pdf?productCode=C318539) |
| C6 | `GRM033R71A103KA01D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/58a7d404c3534585b4a0e91caba788f7.pdf?productCode=C76941) |
| C6 (alt) | `0201X103K100NT` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/09fe2daf22580a99fa7fea93ccb20fb7.pdf?productCode=C285200) |
| C7 | `GRM033R71A222KA01D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/a4d1e2744bd5d44ba57842651a3fd598.pdf?productCode=C161479) |
| C7 (alt) | `GCM033R71A222KA03D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/e24d88067dc9621df8f575e43a84d279.pdf?productCode=C2184294) |
| C9, C10, C11, C12 | `CL05A106MQ5NUNC` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/65bc266350d348ca20afaa6e412e395a.pdf?productCode=C15525) |
| C9, C10, C11, C12 (alt) | `HGC0402R5106M100NTEJ` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/3025399970486160f9625970e5fd5973.pdf?productCode=C7472949) |
| C13 | `GRM0335C1H101JA01D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/fbf10c963bae4a138de5637c5c931495.pdf?productCode=C76922) |
| C13 (alt) | `CC0201JRNPO9BN101` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/4eca2bb4b507f1633db47e922d632b95.pdf?productCode=C272870) |
| C18 | `GJM0335C1E1R5WB01D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/f7493dd88fc4c7f1a8836b203c0b89c6.pdf?productCode=C435397) |
| C18 (alt) | `GRM0335C1H1R5WA01D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/bb7c7daf22f40d74dc9493dcdcae707d.pdf?productCode=C88913) |
| C19 | `GJM0335C1E2R0WB01D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/4aeb9678e7868d7812716d71d111f969.pdf?productCode=C668326) |
| C19 (alt) | `CQ0201BRNPO8BN2R0` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/d9e1f96faa5392c23fe073d37a19d097.pdf?productCode=C577359) |
| C20, C21 | `GJM0335C1HR50WB01D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/1bbf3c01064d6a4835f8edd560c28a07.pdf?productCode=C237424) |
| C20, C21 (alt) | `GRM0335C1HR50WA01D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/a4d1e2744bd5d44ba57842651a3fd598.pdf?productCode=C85922) |
| C22 | `GJM0335C1HR30WB01D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/55d59134d700e77e75eb700274d60200.pdf?productCode=C3904589) |
| C22 (alt) | `0201CG0R3B500NT` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/09fe2daf22580a99fa7fea93ccb20fb7.pdf?productCode=C723329) |
| C23 | `GJM0335C1E3R9WB01D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/44eb2aa2e9bd53c8ebdc6432b5170afa.pdf?productCode=C1852416) |
| C23 (alt) | `0201CG3R9C250NT` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/09fe2daf22580a99fa7fea93ccb20fb7.pdf?productCode=C285100) |
| C24, C25 (alt) | `GRM0335C1E102JA01D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/7aaee6e6d98f42c891adef4509cd7519.pdf?productCode=C161371) |
| R1, R2 | `0201WMF4704TEE` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/0a975aaa49b7c97f38a963127be4a823.pdf?productCode=C778408) |
| R1, R2 (alt) | `0201WMJ0475TEE` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/0a975aaa49b7c97f38a963127be4a823.pdf?productCode=C423341) |
| R5, R6, R7, R8, R10 | `0201WMF1002TEE` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/0a975aaa49b7c97f38a963127be4a823.pdf?productCode=C473048) |
| R5, R6, R7, R8, R10 (alt) | `RC0201JR-0710KL` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/b426be3ce22c6de3e0c3a2248e49159e.pdf?productCode=C138117) |
| R9 | `0201WMF1000TEE` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/0a975aaa49b7c97f38a963127be4a823.pdf?productCode=C270366) |
| R9 (alt) | `RC0201FR-07100RL` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/b426be3ce22c6de3e0c3a2248e49159e.pdf?productCode=C77623) |
| L1 | `MLZ1608M4R7WT000` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/e509de56baff45f8205b34b96f35b973.pdf?productCode=C76799) |
| L1 (alt) | `CMH160808B4R7MT` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/d286f068235a06893e31ac478b5041c4.pdf?productCode=C394952) |
| L2 | `LQP03HQ2N7B02D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/ac186320274d922facfc49f3dd9954de.pdf?productCode=C7216765) |
| L2 (alt) | `MLG0603P2N7CT000` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/d0574c5bb27de1a8c633eb940da510dd.pdf?productCode=C76752) |
| L3, L4 | `LQP03HQ3N5B02D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/ac186320274d922facfc49f3dd9954de.pdf?productCode=C3911055) |
| L3, L4 (alt) | `LQP03TN3N5B02D` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/21cc2e6abe84f1c64c93eab152a87fc9.pdf?productCode=C206424) |
| L10 | `0201WMF0000TEE` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/f42da6c80a0747bae77c2f98f4e46d1d.pdf?productCode=C473473) |
| L10 (alt) | `RC0201JR-070RL` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/b426be3ce22c6de3e0c3a2248e49159e.pdf?productCode=C106228) |
| U1 | `NRF54L10-QFAA-R7` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/11cf20669bff633a577e95a4820b68c9.pdf?productCode=C44800139) |
| U1 (alt) | `NRF54L05-QFAA-R` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/11cf20669bff633a577e95a4820b68c9.pdf?productCode=C45022042) |
| U2 | `LIS2DW12TR` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/faa0f1ff935ff2be849a090ec963fd19.pdf?productCode=C189624) |
| U2 (alt) | `LIS2DH12TR` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/80fd3cb5c04ce9b30e9bec7b53c4a455.pdf?productCode=C110926) |
| X1 | `Q13FC13500004` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/d4d1bd2e87b2e72a8e8e7fe7d590f4c0.pdf?productCode=C32346) |
| X1 (alt) | `Q13FC13500049` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/87f4fb5292528ca7f0dcfb918a7643ad.pdf?productCode=C95361) |
| X2 | `NX2016SA-32MHZ-STD-CZS-5` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/7d295f64f7c44230fecd37b1086251f1.pdf?productCode=C843260) |
| X2 (alt) | `X201632MKB4SI` | [PDF](https://datasheet.lcsc.com/datasheet/pdf/03f32cc3dfdcdfc9fffa8449db791193.pdf?productCode=C718072) |

---

*`spec/bom-resolved.json` is the machine-readable form of this page and carries the full price ladders from both channels, the LCSC retail prices, the min-packet and split quantities, and the MPN check result for every order code. Regenerate both with `python3 tools/resolve_bom.py && python3 tools/gen_sourcing.py`.*
