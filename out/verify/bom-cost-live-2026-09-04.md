# BOM cost — halo_rev_a-BOM.csv

*Read as `JLCPCB BOM.csv`. Catalogue snapshot **2026-09-03** (684,956 parts). Generated 2026-09-04T10:40:22Z. All prices USD.*

> LCSC unit prices from the jlcparts catalogue snapshot named above. Board fabrication, assembly labour, stencil, shipping and duty are NOT in these numbers -- see `fab quote`.

> Rows marked ⟲ were NOT in the snapshot and were priced from a live endpoint, named per row. The snapshot is JLCPCB's assembly catalogue; lcsc.com's retail catalogue is a different set, and a part in one and not the other is a CONSIGNED part, not a missing one.


## 10 boards — FAIL

| Designators | Qty/bd | Need | LCSC | MPN | Package | Type | Unit | Extended | Verdict |
|---|--:|--:|---|---|---|---|--:|--:|---|
| C5,C8 | 2 | 20 | C2827888 | DB2EK-3.5-8P-BK-S | P=3.5mm | extended | 0.7517 | 15.03 | PASS |
| R5,R6,R7,R10,R8 | 5 | 50→3,894 | C25744 | 0402WGF1002TCE | 0402 | basic | 0.0024 | 9.35 | PASS |
| L4,L3 ⟲ | 2 | 20 | C1046539 | SIT3372AC-1E2-33NZ133.650000X | L_0201_0603Metric | — | 14.7336 | 294.67 | FAIL |
| C7 | 1 | 10 | C2827888 | DB2EK-3.5-8P-BK-S | P=3.5mm | extended | 0.7517 | 7.52 | PASS |
| C22 | 1 | 10→20 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0014 | 0.03 | PASS |
| C23 | 1 | 10→20 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0014 | 0.03 | PASS |
| C18 | 1 | 10→20 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0014 | 0.03 | PASS |
| C4,C2,C1,C3 | 4 | 40→1,337 | C1546 | 0402CG101J500NT | 0402 | basic | 0.0068 | 9.09 | PASS |
| C25,C24 | 2 | 20→1,337 | C1546 | 0402CG101J500NT | 0402 | basic | 0.0068 | 9.09 | PASS |
| C6 | 1 | 10 | C2827888 | DB2EK-3.5-8P-BK-S | P=3.5mm | extended | 0.7517 | 7.52 | PASS |
| C21,C20 | 2 | 20→30 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0014 | 0.04 | PASS |
| R2,R1 | 2 | 20→30 | C25765 | 0402WGF2002TCE | 0402 | basic | 0.0012 | 0.04 | PASS |
| C19 | 1 | 10→20 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0014 | 0.03 | PASS |
| C13 | 1 | 10→20 | C1523 | 0402B102K500NT | 0402 | basic | 0.0024 | 0.05 | PASS |
| L2 ⟲ | 1 | 10 | C1046539 | SIT3372AC-1E2-33NZ133.650000X | L_0201_0603Metric | — | 14.7336 | 147.34 | FAIL |
| R9 | 1 | 10→20 | C25076 | 0402WGF1000TCE | 0402 | basic | 0.0012 | 0.02 | PASS |
| L10 | 1 | 10→20 | C25076 | 0402WGF1000TCE | 0402 | basic | 0.0012 | 0.02 | PASS |
| U1 | 1 | 10 | C44800139 | NRF54L10-QFAA-R7 | VFQFN-48 | extended | 2.9212 | 29.21 | PASS |
| C15,C17,C14,C16 | 4 | 40 | — | — | C_0201_0603Metric | — | — | — | CANNOT DETERMINE |
| C12,C10,C9,C11 | 4 | 40→50 | C15525 | CL05A106MQ5NUNC | 0402 | basic | 0.0199 | 0.99 | PASS |
| U2 | 1 | 10 | C189624 | LIS2DW12TR | LGA-12 | extended | 1.0103 | 10.10 | PASS |
| X2 | 1 | 10 | C843260 | NX2016SA-32MHZ-STD-CZS-5 | SMD2016-4P | extended | 0.3445 | 3.44 | PASS |
| L1 | 1 | 10→18 | C1046 | SDFL2012S100KTF | 0805 | basic | 0.0560 | 1.01 | PASS |
| X1 | 1 | 10 | C32346 | Q13FC13500004 | SMD3215-2P | basic | 0.1744 | 1.74 | PASS |

- **Parts subtotal: 104.39 USD** — covers 23 of 24 BOM lines - 1 line(s) are UNPRICED and are NOT in this total
- **Parts per board: 10.4390 USD**  — CARRIES LEFTOVER STOCK: a line hit a minimum purchase packet larger than this build, so part of this figure buys parts you keep. It is NOT the marginal cost of one more board.
- Unique parts: 8 basic, 5 extended
- Extended-part feeder fees: 15.00 USD — 5 unique extended parts x 3.0 USD. Feeders Loading fee — Economic PCBA — $3/ Extended | Standard PCBA — $1.5 basic/Extended [fee-table-2024 retrieved 2026-09-03]
  - `L4,L3` **FAIL** — needs 20 but jlcpcb.com shows 0 live at 2026-09-04T10:40:18Z (lcsc.com: 0). C1046539 is not in this catalogue snapshot. Either it is out of stock (this DB holds in-stock parts plus the Basic library) or the code is wrong.
  - `L2` **FAIL** — needs 10 but jlcpcb.com shows 0 live at 2026-09-04T10:40:21Z (lcsc.com: 0). C1046539 is not in this catalogue snapshot. Either it is out of stock (this DB holds in-stock parts plus the Basic library) or the code is wrong.
  - `C15,C17,C14,C16` **CANNOT DETERMINE** — line carries neither an LCSC code nor an MPN; nothing to look up

## 100 boards — FAIL

| Designators | Qty/bd | Need | LCSC | MPN | Package | Type | Unit | Extended | Verdict |
|---|--:|--:|---|---|---|---|--:|--:|---|
| C5,C8 | 2 | 200 | C2827888 | DB2EK-3.5-8P-BK-S | P=3.5mm | extended | 0.5727 | 114.54 | FAIL |
| R5,R6,R7,R10,R8 | 5 | 500→3,894 | C25744 | 0402WGF1002TCE | 0402 | basic | 0.0024 | 9.35 | PASS |
| L4,L3 ⟲ | 2 | 200 | C1046539 | SIT3372AC-1E2-33NZ133.650000X | L_0201_0603Metric | — | 5.7025 | 1140.50 | FAIL |
| C7 | 1 | 100 | C2827888 | DB2EK-3.5-8P-BK-S | P=3.5mm | extended | 0.5727 | 57.27 | FAIL |
| C22 | 1 | 100→110 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0014 | 0.15 | PASS |
| C23 | 1 | 100→110 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0014 | 0.15 | PASS |
| C18 | 1 | 100→110 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0014 | 0.15 | PASS |
| C4,C2,C1,C3 | 4 | 400→1,337 | C1546 | 0402CG101J500NT | 0402 | basic | 0.0068 | 9.09 | PASS |
| C25,C24 | 2 | 200→1,337 | C1546 | 0402CG101J500NT | 0402 | basic | 0.0068 | 9.09 | PASS |
| C6 | 1 | 100 | C2827888 | DB2EK-3.5-8P-BK-S | P=3.5mm | extended | 0.5727 | 57.27 | FAIL |
| C21,C20 | 2 | 200→210 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0014 | 0.29 | PASS |
| R2,R1 | 2 | 200→210 | C25765 | 0402WGF2002TCE | 0402 | basic | 0.0012 | 0.25 | PASS |
| C19 | 1 | 100→110 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0014 | 0.15 | PASS |
| C13 | 1 | 100→110 | C1523 | 0402B102K500NT | 0402 | basic | 0.0024 | 0.26 | PASS |
| L2 ⟲ | 1 | 100 | C1046539 | SIT3372AC-1E2-33NZ133.650000X | L_0201_0603Metric | — | 14.7336 | 1473.36 | FAIL |
| R9 | 1 | 100→110 | C25076 | 0402WGF1000TCE | 0402 | basic | 0.0012 | 0.13 | PASS |
| L10 | 1 | 100→110 | C25076 | 0402WGF1000TCE | 0402 | basic | 0.0012 | 0.13 | PASS |
| U1 | 1 | 100 | C44800139 | NRF54L10-QFAA-R7 | VFQFN-48 | extended | 2.3092 | 230.92 | PASS |
| C15,C17,C14,C16 | 4 | 400 | — | — | C_0201_0603Metric | — | — | — | CANNOT DETERMINE |
| C12,C10,C9,C11 | 4 | 400→410 | C15525 | CL05A106MQ5NUNC | 0402 | basic | 0.0199 | 8.16 | PASS |
| U2 | 1 | 100 | C189624 | LIS2DW12TR | LGA-12 | extended | 0.7696 | 76.96 | PASS |
| X2 | 1 | 100 | C843260 | NX2016SA-32MHZ-STD-CZS-5 | SMD2016-4P | extended | 0.2848 | 28.48 | PASS |
| L1 | 1 | 100→108 | C1046 | SDFL2012S100KTF | 0805 | basic | 0.0560 | 6.05 | PASS |
| X1 | 1 | 100 | C32346 | Q13FC13500004 | SMD3215-2P | basic | 0.1375 | 13.75 | PASS |

- **Parts subtotal: 622.62 USD** — covers 23 of 24 BOM lines - 1 line(s) are UNPRICED and are NOT in this total
- **Parts per board: 6.2262 USD**  — CARRIES LEFTOVER STOCK: a line hit a minimum purchase packet larger than this build, so part of this figure buys parts you keep. It is NOT the marginal cost of one more board.
- Unique parts: 8 basic, 5 extended
- Extended-part feeder fees: 15.00 USD — 5 unique extended parts x 3.0 USD. Feeders Loading fee — Economic PCBA — $3/ Extended | Standard PCBA — $1.5 basic/Extended [fee-table-2024 retrieved 2026-09-03]
  - `C5,C8` **FAIL** — needs 200 but only 59 in stock as of 2026-09-03
  - `L4,L3` **FAIL** — needs 200 but jlcpcb.com shows 0 live at 2026-09-04T10:40:18Z (lcsc.com: 0). C1046539 is not in this catalogue snapshot. Either it is out of stock (this DB holds in-stock parts plus the Basic library) or the code is wrong.
  - `C7` **FAIL** — needs 100 but only 59 in stock as of 2026-09-03
  - `C6` **FAIL** — needs 100 but only 59 in stock as of 2026-09-03
  - `L2` **FAIL** — needs 100 but jlcpcb.com shows 0 live at 2026-09-04T10:40:21Z (lcsc.com: 0). C1046539 is not in this catalogue snapshot. Either it is out of stock (this DB holds in-stock parts plus the Basic library) or the code is wrong.
  - `C15,C17,C14,C16` **CANNOT DETERMINE** — line carries neither an LCSC code nor an MPN; nothing to look up

## 1,000 boards — FAIL

| Designators | Qty/bd | Need | LCSC | MPN | Package | Type | Unit | Extended | Verdict |
|---|--:|--:|---|---|---|---|--:|--:|---|
| C5,C8 | 2 | 2,000 | C2827888 | DB2EK-3.5-8P-BK-S | P=3.5mm | extended | 0.4832 | 966.40 | FAIL |
| R5,R6,R7,R10,R8 | 5 | 5,000→5,010 | C25744 | 0402WGF1002TCE | 0402 | basic | 0.0024 | 12.02 | PASS |
| L4,L3 ⟲ | 2 | 2,000 | C1046539 | SIT3372AC-1E2-33NZ133.650000X | L_0201_0603Metric | — | 5.4036 | 10807.20 | FAIL |
| C7 | 1 | 1,000 | C2827888 | DB2EK-3.5-8P-BK-S | P=3.5mm | extended | 0.4832 | 483.20 | FAIL |
| C22 | 1 | 1,000→1,010 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0011 | 1.11 | PASS |
| C23 | 1 | 1,000→1,010 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0011 | 1.11 | PASS |
| C18 | 1 | 1,000→1,010 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0011 | 1.11 | PASS |
| C4,C2,C1,C3 | 4 | 4,000→4,010 | C1546 | 0402CG101J500NT | 0402 | basic | 0.0062 | 24.86 | PASS |
| C25,C24 | 2 | 2,000→2,010 | C1546 | 0402CG101J500NT | 0402 | basic | 0.0068 | 13.67 | PASS |
| C6 | 1 | 1,000 | C2827888 | DB2EK-3.5-8P-BK-S | P=3.5mm | extended | 0.4832 | 483.20 | FAIL |
| C21,C20 | 2 | 2,000→2,010 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0011 | 2.21 | PASS |
| R2,R1 | 2 | 2,000→2,010 | C25765 | 0402WGF2002TCE | 0402 | basic | 0.0010 | 2.01 | PASS |
| C19 | 1 | 1,000→1,010 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0011 | 1.11 | PASS |
| C13 | 1 | 1,000→1,010 | C1523 | 0402B102K500NT | 0402 | basic | 0.0021 | 2.12 | PASS |
| L2 ⟲ | 1 | 1,000 | C1046539 | SIT3372AC-1E2-33NZ133.650000X | L_0201_0603Metric | — | 5.4036 | 5403.60 | FAIL |
| R9 | 1 | 1,000→1,010 | C25076 | 0402WGF1000TCE | 0402 | basic | 0.0010 | 1.01 | PASS |
| L10 | 1 | 1,000→1,010 | C25076 | 0402WGF1000TCE | 0402 | basic | 0.0010 | 1.01 | PASS |
| U1 | 1 | 1,000 | C44800139 | NRF54L10-QFAA-R7 | VFQFN-48 | extended | 2.1042 | 2104.20 | FAIL |
| C15,C17,C14,C16 | 4 | 4,000 | — | — | C_0201_0603Metric | — | — | — | CANNOT DETERMINE |
| C12,C10,C9,C11 | 4 | 4,000→4,010 | C15525 | CL05A106MQ5NUNC | 0402 | basic | 0.0162 | 64.96 | PASS |
| U2 | 1 | 1,000 | C189624 | LIS2DW12TR | LGA-12 | extended | 0.7061 | 706.10 | PASS |
| X2 | 1 | 1,000 | C843260 | NX2016SA-32MHZ-STD-CZS-5 | SMD2016-4P | extended | 0.2273 | 227.30 | PASS |
| L1 | 1 | 1,000→1,008 | C1046 | SDFL2012S100KTF | 0805 | basic | 0.0443 | 44.65 | PASS |
| X1 | 1 | 1,000 | C32346 | Q13FC13500004 | SMD3215-2P | basic | 0.1034 | 103.40 | PASS |

- **Parts subtotal: 5,246.78 USD** — covers 23 of 24 BOM lines - 1 line(s) are UNPRICED and are NOT in this total
- **Parts per board: 5.2468 USD**  — includes JLCPCB's stated setup attrition, which is consumed and not stock you keep
- Unique parts: 8 basic, 5 extended
- Extended-part feeder fees: 15.00 USD — 5 unique extended parts x 3.0 USD. Feeders Loading fee — Economic PCBA — $3/ Extended | Standard PCBA — $1.5 basic/Extended [fee-table-2024 retrieved 2026-09-03]
  - `C5,C8` **FAIL** — needs 2000 but only 59 in stock as of 2026-09-03
  - `L4,L3` **FAIL** — needs 2000 but jlcpcb.com shows 0 live at 2026-09-04T10:40:18Z (lcsc.com: 0). C1046539 is not in this catalogue snapshot. Either it is out of stock (this DB holds in-stock parts plus the Basic library) or the code is wrong.
  - `C7` **FAIL** — needs 1000 but only 59 in stock as of 2026-09-03
  - `C6` **FAIL** — needs 1000 but only 59 in stock as of 2026-09-03
  - `L2` **FAIL** — needs 1000 but jlcpcb.com shows 0 live at 2026-09-04T10:40:21Z (lcsc.com: 0). C1046539 is not in this catalogue snapshot. Either it is out of stock (this DB holds in-stock parts plus the Basic library) or the code is wrong.
  - `U1` **FAIL** — needs 1000 but only 212 in stock as of 2026-09-03
  - `C15,C17,C14,C16` **CANNOT DETERMINE** — line carries neither an LCSC code nor an MPN; nothing to look up

## 10,000 boards — FAIL

| Designators | Qty/bd | Need | LCSC | MPN | Package | Type | Unit | Extended | Verdict |
|---|--:|--:|---|---|---|---|--:|--:|---|
| C5,C8 | 2 | 20,000 | C2827888 | DB2EK-3.5-8P-BK-S | P=3.5mm | extended | 0.4832 | 9664.00 | FAIL |
| R5,R6,R7,R10,R8 | 5 | 50,000→50,010 | C25744 | 0402WGF1002TCE | 0402 | basic | 0.0021 | 105.02 | PASS |
| L4,L3 ⟲ | 2 | 20,000 | C1046539 | SIT3372AC-1E2-33NZ133.650000X | L_0201_0603Metric | — | 5.4036 | 108072.00 | FAIL |
| C7 | 1 | 10,000 | C2827888 | DB2EK-3.5-8P-BK-S | P=3.5mm | extended | 0.4832 | 4832.00 | FAIL |
| C22 | 1 | 10,000→10,010 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0008 | 8.01 | FAIL |
| C23 | 1 | 10,000→10,010 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0008 | 8.01 | FAIL |
| C18 | 1 | 10,000→10,010 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0008 | 8.01 | FAIL |
| C4,C2,C1,C3 | 4 | 40,000→40,010 | C1546 | 0402CG101J500NT | 0402 | basic | 0.0060 | 240.06 | PASS |
| C25,C24 | 2 | 20,000→20,010 | C1546 | 0402CG101J500NT | 0402 | basic | 0.0060 | 120.06 | PASS |
| C6 | 1 | 10,000 | C2827888 | DB2EK-3.5-8P-BK-S | P=3.5mm | extended | 0.4832 | 4832.00 | FAIL |
| C21,C20 | 2 | 20,000→20,010 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0008 | 16.01 | FAIL |
| R2,R1 | 2 | 20,000→20,010 | C25765 | 0402WGF2002TCE | 0402 | basic | 0.0008 | 16.01 | PASS |
| C19 | 1 | 10,000→10,010 | C1568 | 0402CG4R0C500NT | 0402 | extended | 0.0008 | 8.01 | FAIL |
| C13 | 1 | 10,000→10,010 | C1523 | 0402B102K500NT | 0402 | basic | 0.0017 | 17.02 | PASS |
| L2 ⟲ | 1 | 10,000 | C1046539 | SIT3372AC-1E2-33NZ133.650000X | L_0201_0603Metric | — | 5.4036 | 54036.00 | FAIL |
| R9 | 1 | 10,000→10,010 | C25076 | 0402WGF1000TCE | 0402 | basic | 0.0009 | 9.01 | PASS |
| L10 | 1 | 10,000→10,010 | C25076 | 0402WGF1000TCE | 0402 | basic | 0.0009 | 9.01 | PASS |
| U1 | 1 | 10,000 | C44800139 | NRF54L10-QFAA-R7 | VFQFN-48 | extended | 2.1042 | 21042.00 | FAIL |
| C15,C17,C14,C16 | 4 | 40,000 | — | — | C_0201_0603Metric | — | — | — | CANNOT DETERMINE |
| C12,C10,C9,C11 | 4 | 40,000→40,010 | C15525 | CL05A106MQ5NUNC | 0402 | basic | 0.0153 | 612.15 | PASS |
| U2 | 1 | 10,000 | C189624 | LIS2DW12TR | LGA-12 | extended | 0.7061 | 7061.00 | PASS |
| X2 | 1 | 10,000 | C843260 | NX2016SA-32MHZ-STD-CZS-5 | SMD2016-4P | extended | 0.2047 | 2047.00 | FAIL |
| L1 | 1 | 10,000→10,008 | C1046 | SDFL2012S100KTF | 0805 | basic | 0.0399 | 399.32 | PASS |
| X1 | 1 | 10,000 | C32346 | Q13FC13500004 | SMD3215-2P | basic | 0.0819 | 819.00 | PASS |

- **Parts subtotal: 51,872.70 USD** — covers 23 of 24 BOM lines - 1 line(s) are UNPRICED and are NOT in this total
- **Parts per board: 5.1873 USD**  — includes JLCPCB's stated setup attrition, which is consumed and not stock you keep
- Unique parts: 8 basic, 5 extended
- Extended-part feeder fees: 15.00 USD — 5 unique extended parts x 3.0 USD. Feeders Loading fee — Economic PCBA — $3/ Extended | Standard PCBA — $1.5 basic/Extended [fee-table-2024 retrieved 2026-09-03]
  - `C5,C8` **FAIL** — needs 20000 but only 59 in stock as of 2026-09-03
  - `L4,L3` **FAIL** — needs 20000 but jlcpcb.com shows 0 live at 2026-09-04T10:40:18Z (lcsc.com: 0). C1046539 is not in this catalogue snapshot. Either it is out of stock (this DB holds in-stock parts plus the Basic library) or the code is wrong.
  - `C7` **FAIL** — needs 10000 but only 59 in stock as of 2026-09-03
  - `C22` **FAIL** — needs 10010 but only 3445 in stock as of 2026-09-03
  - `C23` **FAIL** — needs 10010 but only 3445 in stock as of 2026-09-03
  - `C18` **FAIL** — needs 10010 but only 3445 in stock as of 2026-09-03
  - `C6` **FAIL** — needs 10000 but only 59 in stock as of 2026-09-03
  - `C21,C20` **FAIL** — needs 20010 but only 3445 in stock as of 2026-09-03
  - `C19` **FAIL** — needs 10010 but only 3445 in stock as of 2026-09-03
  - `L2` **FAIL** — needs 10000 but jlcpcb.com shows 0 live at 2026-09-04T10:40:21Z (lcsc.com: 0). C1046539 is not in this catalogue snapshot. Either it is out of stock (this DB holds in-stock parts plus the Basic library) or the code is wrong.
  - `U1` **FAIL** — needs 10000 but only 212 in stock as of 2026-09-03
  - `C15,C17,C14,C16` **CANNOT DETERMINE** — line carries neither an LCSC code nor an MPN; nothing to look up
  - `X2` **FAIL** — needs 10000 but only 6665 in stock as of 2026-09-03

