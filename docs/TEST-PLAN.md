# halo — production test plan — what the factory measures on every unit, with limits, fixtures and sources

*Lane P1. Generated 2026-09-04 from `spec/test-plan.json` by `tools/gen_test_plan.py`. Nothing on this page is hand-typed. Companion: [`docs/TOOLS-THAT-LIE.md`](TOOLS-THAT-LIE.md), which is the standard this plan is written to, and [`out/release/TEST-PLAN.html`](../out/release/TEST-PLAN.html), which is the same data as a page for the factory.*

Thirty-one tests across three stations. Every limit in this plan names the datasheet page, the standard, the DECISIONS entry or the in-repo measurement it came from. Where no source exists the limit is written CANNOT DETERMINE with the one measurement that would settle it, because a limit we invented would be worse than no limit: the line would run to it, and the number would be wrong.

三个工位，三十一项测试。本计划中的每一个限值都注明来源：数据手册页码、标准条款、DECISIONS 决策记录，或本仓库内的实测值。凡无来源者一律写作 CANNOT DETERMINE（无法判定），并写明用哪一次测量可以定案 —— 因为我们编造的限值比没有限值更糟：产线会照着它做，而那个数字是错的。

---

## 1. The plan in numbers

**31 tests. 22 run on every unit. 99 limits, 87 of them gates a unit is judged against. 21 limits are CANNOT DETERMINE and name what would settle them, 15 of those being gates. Cycle-time estimate 4.4 min (263 s) per unit across all three stations; the busiest station is Assembled board in its carrier at 2.6 min (154 s), and that is the line's takt.**

| # | station | tests | on every unit | go/no-go | open limits | cycle per unit |
|---|---|---|---|---|---|---|
| 1 | Bare board | 5 | 1 | 3 | 4 | 21.1 s |
| 2 | Assembled board in its carrier | 17 | 15 | 12 | 3 | 2.6 min (154 s) |
| 3 | Sealed unit | 9 | 6 | 7 | 5 | 1.5 min (89 s) |
| | **total** | **31** | **22** | **22** | **12** | **4.4 min (263 s)** |

Per-unit cycle time is computed by tools/gen_test_plan.py as the sum over all tests of cycle_s × sampling_fraction, where the fraction is 1.0 for a 100 % test and n/lot for a sample test. Sample tests are amortised over an assumed lot of 500 units. The result is derived from the data, never typed.

Station cycle time is the sum for that station's stage. The line's takt is set by the slowest station, not by the total — the three stations run in parallel on different units. The dominating single test is AB-11 at 22 s, which is set by DULT's own advertising interval: to prove an interval of ≤ 4 s you must watch for long enough to count five advertisements.

- AB-11 and AB-06 can share one 20 s capture window at the same station, since both are radio observations of the same unit — this is already assumed in the station roll-up.
- AB-07's 8 s sleep window is the second-longest. It can be shortened only by accepting a noisier average; do not shorten it by starting the average before the part is actually asleep.
- FU-03 and FU-04 cannot be merged: the acoustic hood and the RF-quiet box are mutually exclusive environments, and the sounder command in FU-04 has to be heard by FU-03's microphone. Either the unit moves between two nests, or one nest is both, which is a harder fixture.

## 2. What each station is for

**1. Bare board** — at the PCB fabricator, before any component is placed. The copper is right and the board is buildable. Everything here is the fab's own process control; halo's job is to require the report and to check that the report was run against the right netlist.

**2. Assembled board in its carrier** — after reflow, after the board is seated in the LCP carrier with its three stamped contacts, before the shell is bonded. Every semiconductor answers, every rail is where it should be, the unit is programmed and given its identity, and all four radios-and-transducers paths — Bluetooth, NFC, motion, sounder drive — are proven electrically. This is the last station where anything can be reworked.

**3. Sealed unit** — after the shell is bonded to the carrier, cell fitted, door closed, label applied. The product as the customer receives it, running from its own cell with no wires attached. If a unit fails here it is a scrap or a de-bond investigation, never a rework — the parting line is a structural adhesive joint (MECHANICAL §7) and it does not come apart twice.

## 3. The tests

The verdict column grades THE TEST, not the unit. PASS = every GATE limit in the row traces to a named source, so the row can be run on a line as written. CANNOT DETERMINE = at least one gate limit has no source yet; the row says which and what would settle it. A gate is any limit the station judges a unit against; rows marked 'record', 'note' or '≈' are readings and design anchors, not gates, and a plan can be runnable while some of its recorded quantities still have no window. Section 10 lists every open limit, gate or not. No row is graded on whether a unit would pass it — nothing has been built.

> docs/TOOLS-THAT-LIE.md — every test row carries the sentence "this could report PASS while ___ is badly wrong" and the assert that closes it. A row with an empty counter-assert is not finished.

### Station 1 — Bare board (5 tests)

#### BB-01 — Netlist continuity and isolation, 100 % of nets — **CANNOT DETERMINE**

- **Proves.** the copper the fabricator made is the copper the schematic asked for
- **Traces to.** SPEC §6 M1; IPC-9252B (electrical test of unpopulated boards); electronics/halo_rev_a/out/halo_rev_a.net
- **Measurement.** flying-probe or grid test against the IPC-D-356 netlist exported from halo_rev_a.net
- **Limits.**
  - `nets tested = 41 nets` — halo_rev_a.net carries 52 net records, 11 of which are auto-generated unconnected-(U1-…) singles. 41 real nets remain and every one must appear in the ET report.
  - `opens = 0 count` — IPC-9252B — an open is a reject at any class
  - `shorts = 0 count` — IPC-9252B
  - `continuity threshold ≤ — Ω` — CANNOT DETERMINE — this plan does not hold a copy of IPC-9252B and will not quote its default table from memory. Settle it by taking the threshold from the fabricator's own ET process sheet and recording it here; the fab must state the value it used.
  - `isolation threshold ≥ — Ω` — CANNOT DETERMINE — same reason, same fix.
- **Equipment.** EQ-ET
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 20 s
- **On failure.** scrap — a bare board is the cheapest thing in the build and rework of inner-layer copper is not a thing
- **Recorded.** panel id, board position, net count tested, opens, shorts, the thresholds the fab used
- **This could report PASS while…** the netlist the tester ran against was extracted from the Gerbers rather than from the schematic — in which case a copper feature that is wrong in both files passes cleanly
- **…so assert.** the ET report's net count must equal 41. A Gerber-extracted netlist does not produce halo's net names or its count; it produces whatever the copper happens to connect.

#### BB-02 — Outline diameter and finished thickness — **CANNOT DETERMINE**

- **Proves.** the board fits the carrier's seat and the 7.980 mm stack still closes
- **Traces to.** DECISIONS.md D17; docs/MECHANICAL.md §2; design.py D_PCB / T_PCB
- **Measurement.** calipers on the routed outline at three angles; micrometer on the finished thickness at three points
- **Limits.**
  - `outline diameter = 26.0 mm` — design.py D_PCB, the value lane M's stack budget closes on (DECISIONS.md D17)
  - `finished thickness = 0.6 mm` — D17 — the 1.742 mm recovered by deleting Apple's motor was spent on a 0.60 mm board instead of Apple's 0.30 mm
  - `outline tolerance ± — mm` — CANNOT DETERMINE — halo has never stated a board tolerance. Settle it from the fabricator's routing capability sheet (JLCPCB publishes ±0.2 mm as standard) and record the agreed figure in SPEC §6.
  - `thickness tolerance ± — mm` — CANNOT DETERMINE — same. On a 0.60 mm board a ±10 % fab tolerance is ±0.06 mm and the stack has 0.542 mm of slack (MECHANICAL §2), so this is very unlikely to bind; it still has to be written down before it can be tested.
- **Equipment.** —
- **Sampling.** 5 boards per delivered panel lot
- **Type / cycle.** recorded, 60 s
- **On failure.** investigate at the fab — an outline error is a routing-program error and it is on every board in the lot, not on one
- **Recorded.** lot id, three diameters, three thicknesses
- **This could report PASS while…** the operator measures the panel rail instead of the board, or measures across a tab rather than the routed edge
- **…so assert.** three diameters at three different angles must agree within the measurement resolution; a tab or a rail shows up immediately as one reading that does not match the other two.

#### BB-03 — Controlled-impedance coupon — **CANNOT DETERMINE**

- **Proves.** the RF_50 trace is actually 50 Ω in the stackup the fab built, not in the stackup we drew
- **Traces to.** SPEC §5 E4; SPEC §6 M1; the stackup in out/release/board/ (lane B1 / T6)
- **Measurement.** TDR on the panel's impedance coupon
- **Limits.**
  - `single-ended impedance = 50 Ω` — the RF_50 net name and Nordic's reference circuit config 1 (schematic title-block comment 3); the antenna feed is a 50 Ω interface by construction
  - `impedance tolerance ± — %` — CANNOT DETERMINE — halo has not stated one. ±10 % is the industry-usual controlled-impedance class and is what most fabs quote by default, but this plan will not print a number nobody in this repo chose. Settle it in the stackup document, then this row becomes a hard limit.
- **Equipment.** —
- **Sampling.** one coupon per panel
- **Type / cycle.** recorded, 120 s
- **On failure.** investigate — an impedance miss is a stackup or an etch-compensation problem and affects the whole panel
- **Recorded.** panel id, measured Z0, the stackup revision the fab built
- **This could report PASS while…** the coupon was built from a different stackup than the boards, or the TDR was calibrated at the cable end rather than the probe tip
- **…so assert.** the coupon must be on the same panel as the boards it certifies, and the fab's report must name the stackup revision. Two coupons at opposite corners of the panel must agree.

#### BB-04 — Surface finish and solderability — **CANNOT DETERMINE**

- **Proves.** the 0201 and 0.4 mm-pitch QFN pads will wet
- **Traces to.** SPEC §6 M3; IPC-6012 (qualification and performance of rigid boards); IPC-4552 (ENIG); J-STD-003 (solderability)
- **Measurement.** the fabricator's own finish thickness measurement and solderability coupon
- **Limits.**
  - `gold and nickel thickness in — µm` — CANNOT DETERMINE — the surface finish has not been chosen in this repo. Settle it by naming the finish in the fabrication drawing (ENIG is the usual pick for a 0.4 mm-pitch QFN and 0201 passives), then take the thickness band from IPC-4552 and record it here.
  - `solderability = pass J-STD-003 category` — J-STD-003; the fabricator's coupon result, reported per lot
- **Equipment.** —
- **Sampling.** the fab's per-lot coupon
- **Type / cycle.** go/no-go, 0 s
- **On failure.** reject the lot — a non-wetting finish produces head-in-pillow joints that pass AOI and fail in the field
- **Recorded.** lot id, finish type, measured thickness, solderability result
- **This could report PASS while…** the coupon is from a different lot, or the finish is fresh and the boards sit for six months before assembly
- **…so assert.** record the fab date and require assembly within the finish's stated shelf life; a coupon result without a date on it is not evidence about the boards being built today.

#### BB-05 — Castellation integrity on the reserved UWB stub — **PASS**

- **Proves.** the eight plated half-vias on the board edge (J2) are not torn out by the routing pass
- **Traces to.** DECISIONS.md D12 (the DW3110 footprint is reserved, not populated); electronics/halo_rev_a/schematic.py block 9
- **Measurement.** microscope inspection of the eight half-vias plus continuity from each castellation to its net
- **Limits.**
  - `castellations with intact plating = 8 count` — schematic.py block 9 — J2 is an 8-way castellated stub
  - `burr or torn plating = 0 count` — a torn half-via is an open, and BB-01 will only catch it if the ET probes the castellation face
- **Equipment.** —
- **Sampling.** 5 boards per panel lot
- **Type / cycle.** go/no-go, 45 s
- **On failure.** investigate the routing program — it is a tool-path problem, not a board problem
- **Recorded.** lot id, count of intact castellations, photograph of any defect
- **This could report PASS while…** the ET probed the pad on the top surface rather than the castellation face, so a half-via that is open at the edge reads connected
- **…so assert.** probe the castellation face itself, at the board edge, and say so in the ET program. This is why the check is separate from BB-01 rather than folded into it.

### Station 2 — Assembled board in its carrier (17 tests)

#### AB-01 — Post-reflow automated optical inspection — **CANNOT DETERMINE**

- **Proves.** every one of the 51 placements is present, right way round, and wetted
- **Traces to.** SPEC §6 M3; IPC-A-610 (acceptability of electronic assemblies); the CPL in out/release/board/
- **Measurement.** AOI against the recipe built from the pick-and-place file
- **Limits.**
  - `placements inspected = 51 components` — halo_rev_a.net — 51 component records, of which C14–C17 are DNP crystal load capacitors and must be inspected as deliberately absent
  - `acceptance class = — IPC-A-610 class` — CANNOT DETERMINE — halo has never chosen a class. Class 2 is the default for consumer product and Class 3 would be an odd choice for a $7 tag, but nobody in this repo has decided, and the class changes the fillet criteria the AOI recipe is built from. This is a decision for the release pack, not for a test engineer to assume.
- **Equipment.** EQ-AOI
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 15 s
- **On failure.** rework — this is the station where a tombstoned 0201 is cheap to fix
- **Recorded.** board serial (panel + position), AOI defect codes, the recipe revision
- **This could report PASS while…** the four DNP crystal load capacitors C14–C17 are flagged as missing and the operator learns to click through the four false alarms, and clicks through a real one
- **…so assert.** C14–C17 must be programmed into the recipe as REQUIRED-ABSENT, so a board with them fitted fails. A DNP that is silently ignored trains the operator; a DNP that is asserted absent catches the day someone loads them.

#### AB-02 — Pre-power short test on the supply rail — **PASS**

- **Proves.** VDD is not shorted to GND before a cell or a supply is ever connected
- **Traces to.** electronics/halo_rev_a/schematic.py (the whole rail topology: BT1 → VDD, no regulator); ce-spice/out/cr2032_pulse_load/verdict.json
- **Measurement.** two-wire resistance between the BT1 positive pad (pad 1) and the BT1 negative pad (pad 2), test voltage below 1 V so no junction conducts
- **Limits.**
  - `R(VDD,GND) > 100000 Ω` — derived from the netlist: the lowest-resistance DC path from VDD to GND anywhere in this schematic is the cell-removal divider R1+R2 = 9.4 MΩ, and even that is gated by a GPIO that is normally not driven. 100 kΩ leaves two decades of margin under the lowest legitimate path, so anything below it is a defect and not a design current.
- **Equipment.** EQ-SMU
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 3 s
- **On failure.** rework — find the solder bridge; do not power the board first
- **Recorded.** board serial, measured resistance
- **This could report PASS while…** the meter's test voltage is high enough to forward-bias the SoC's ESD structures, so a genuine short reads as a diode drop and the operator sees 'a few hundred ohms, that's normal'
- **…so assert.** state the test voltage on the traveller and keep it under 1 V. Then there is no normal few-hundred-ohms reading: below 100 kΩ is always a fault.

#### AB-03 — SoC identity over SWD — **PASS**

- **Proves.** the part on the board is an nRF54L10 and not an L05, an L15, or a counterfeit
- **Traces to.** DECISIONS.md D12; nRF54L datasheet 4503_018 v0.10 §4.2.4.1.1.4 (INFO.PART) and §4.2.4.1.1.7 (INFO.RAM)
- **Measurement.** read the FICR block at 0x00FFC000 over SWD through the TC2030 pads
- **Limits.**
  - `INFO.PART at 0x00FFC31C = 0x00054B10 register value` — nRF54L datasheet §4.2.4.1.1.4: N54L15 = 0x00054B15, N54L10 = 0x00054B10, N54L05 = 0x00054B05. D12 picked the L10.
  - `INFO.RAM at 0x00FFC328 = 0xC0 register value` — nRF54L datasheet §4.2.4.1.1.7: K192 = 0xC0. The L10 is the 192 KB part; this is a second, independent way to tell it from an L05 (96 KB, 0x60) or an L15 (256 KB, 0x100).
  - `INFO.DEVICEID at 0x00FFC304 ≠ 0xFFFFFFFFFFFFFFFF register value` — nRF54L datasheet §4.2.4.1.1.2: a 64-bit unique device identifier, factory-programmed. The all-ones reset value means the die was never trimmed — a counterfeit or a reject.
  - `INFO.PACKAGE at 0x00FFC324 record — register value` — CANNOT DETERMINE — datasheet v0.10 §4.2.4.1.1.6 defines only 'Unspecified 0xFFFFFFFF' for this register and lists no QFN48 code. Record the value, do not assert on it, and revisit when a datasheet later than v0.10 defines the field.
- **Equipment.** EQ-SWD
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 6 s
- **On failure.** rework — replace the SoC, then re-run from AB-02
- **Recorded.** board serial, INFO.PART, INFO.RAM, INFO.DEVICEID (this is the unit's permanent key in the traceability database), INFO.PACKAGE
- **This could report PASS while…** the station reads a cached value from the previous unit because the pogo head did not make contact and the debugger returned the last successful session's data
- **…so assert.** INFO.DEVICEID is unique per die. The station must reject any DEVICEID already present in the traceability database — a stale read fails on the second board, not on the two-hundredth.

#### AB-04 — Programming, provisioning and identity readback — **PASS**

- **Proves.** the unit runs the firmware we shipped and carries a unique serial, a product ID and its own rolling key
- **Traces to.** SPEC §2 F1, F1a, F5; docs/ANTI-STALKING.md §4.1 (printed serial, unique per product ID); research/06 constraint C11; DULT §3.15.1; MISSION.md artifact 7
- **Measurement.** flash the signed image over SWD; write the serial, the product ID and the P-224 master key into UICR; read the whole region back and compare
- **Limits.**
  - `firmware image hash read back = the released build's hash SHA-256` — MISSION.md artifact 7 requires the hex and the provisioning step be part of the release; a readback compare is the only proof the write landed
  - `serial uniqueness = not previously issued database assertion` — DULT §3.15.1 — 'The serial number MUST be unique for each product ID'; research/06 C11
  - `key fingerprint stored = recorded, key material never recorded SHA-256 of the public key` — the private key must not leave the station; a fingerprint is enough to prove AB-11 saw this unit
- **Equipment.** EQ-SWD, EQ-DB
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 25 s
- **On failure.** rework — retry once, then replace the SoC. A part that fails programming twice is a part, not a process
- **Recorded.** board serial, halo serial issued, product ID, public-key fingerprint, firmware hash, station id, operator, UTC timestamp
- **This could report PASS while…** the same serial and the same key are written into every unit on the line, and every downstream test still passes because each unit is tested alone
- **…so assert.** the traceability database rejects a duplicate serial AND a duplicate key fingerprint at write time. Uniqueness is asserted by the database, never by the writer — a writer that repeats itself cannot detect that it repeated itself.

#### AB-05 — 32.768 kHz low-frequency crystal start and accuracy — **PASS**

- **Proves.** X1 oscillates, which is what the DULT key schedule and the separated-state timer are counted on
- **Traces to.** electronics/halo_rev_a/schematic.py block clocks (X1, CL 12.5 pF, ±20 ppm); docs/ANTI-STALKING.md §4.2 (15 min / 24 h rotation, 8–24 h timeout)
- **Measurement.** firmware reports LFXO started inside the startup timeout; the station then gates the RTC against its own reference for 10 s
- **Limits.**
  - `LFXO started = True boolean` — if the LFXO does not start the firmware falls back to the internal RC and the key schedule drifts — which is a DULT conformance failure, not a cosmetic one
  - `frequency error record — ppm` — CANNOT DETERMINE as a go/no-go. The crystal is specified ±20 ppm (schematic note) but the board's own load-capacitance error is not budgeted anywhere in this repo, so the assembled tolerance is unknown. Record the ppm on every unit; set the limit from the first-article distribution and from the DULT timer accuracy the firmware actually needs.
- **Equipment.** EQ-SWD
- **Sampling.** 100 %
- **Type / cycle.** recorded, 11 s
- **On failure.** rework — reflow or replace X1
- **Recorded.** board serial, LFXO start flag, measured ppm
- **This could report PASS while…** the firmware reports 'started' from a status bit that is set optimistically, while the oscillator is actually running on the internal RC
- **…so assert.** do not read a status bit — count RTC ticks against the station's reference for 10 s. An RC fallback is tens of thousands of ppm off and shows up in the first second.

#### AB-06 — 32 MHz high-frequency crystal start and carrier frequency — **PASS**

- **Proves.** X2 oscillates and the radio lands in the band
- **Traces to.** electronics/halo_rev_a/schematic.py block clocks (X2 = NDK NX2016SA-32MHZ, CL 8 pF, ±10 ppm); SPEC §5 E4
- **Measurement.** firmware puts the radio into a constant-carrier mode on channel 0 (2402 MHz); the scanner or a counter reads the carrier
- **Limits.**
  - `HFXO started = True boolean` — the radio cannot transmit at all without it, so this is implied by AB-11 — it is measured separately here so a failure names the crystal instead of the antenna
  - `carrier frequency error record — ppm` — CANNOT DETERMINE as a go/no-go. The crystal is ±10 ppm and the SoC has an internal trim (nRF54L datasheet §XOSC32MTRIM), but the Bluetooth Core Specification's centre-frequency tolerance is the number this should be judged against and this repo does not hold the Core Specification. Settle it by reading Core Spec Vol 6 Part A §3.1 and writing the ppm figure into SPEC §5.
- **Equipment.** EQ-BLE, EQ-BOX
- **Sampling.** 100 %
- **Type / cycle.** recorded, 4 s
- **On failure.** rework — reflow or replace X2
- **Recorded.** board serial, HFXO start flag, measured carrier ppm
- **This could report PASS while…** the measurement is of the scanner's own local oscillator, or of another station's DUT leaking into the box
- **…so assert.** EQ-BOX's leakage self-test (zero advertisements from a powered unit 300 mm outside the closed box) is the gate that makes any in-box reading attributable. Run it every shift and after any lid service.

#### AB-07 — Sleep current — **CANNOT DETERMINE**

- **Proves.** the unit will last its year on a 220 mAh cell
- **Traces to.** SPEC §2 F11; nRF54L datasheet 4503_018 v0.10 §11.1.2.1; research/fetched/E-nrf54l-datasheet-currents.md; LIS2DW12 DS11811 Rev 9 features page; research/fetched/G-acoustics-cells-and-holders.md (Maxell CR2032, 220 mAh)
- **Measurement.** the SMU sources 3.000 V into BT1 pad 1 with no cell fitted; the firmware is in the advertising-idle state; the station takes the current floor between advertisements over an 8 s window
- **Limits.**
  - `sleep floor current ≥ 2.0 µA` — nRF54L datasheet §11.1.2.1: ION_IDLE7 (System ON, wake on pin + GRTC, LFXO, 128 KB retained) = 2.0 uA. The nRF54L10 retains 192 KB, for which the datasheet has NO row at all — lane E records the real figure as bracketed between 2.0 and 3.1 uA and warns against quoting a single number. 2.0 uA is therefore a hard physics floor: the SoC alone cannot draw less than the 128 KB row, so a reading below it means the part is not retaining RAM, or the meter is lying. This is the assert no wrong answer can satisfy.
  - `sleep current ceiling ≤ — µA` — CANNOT DETERMINE. The design anchor is 3.1 µA (SoC, 256 KB row, the datasheet's next row up from the L10's 192 KB) plus below 1 µA for the LIS2DW12 in active low-power mode (DS11811 Rev 9, features page) plus the GD25LQ32E's deep-power-down current, which this plan could not source — see AB-13. Set the ceiling from the first-article distribution as mean + 3σ, and record the figure here. Until then this is a recorded value with a floor, not a go/no-go.
- **Equipment.** EQ-SMU
- **Sampling.** 100 %
- **Type / cycle.** recorded, 10 s
- **On failure.** investigate — a high sleep current is usually a leaky flux residue or an un-programmed GPIO, and both are process problems that will be on the next board too
- **Recorded.** board serial, sleep floor µA, 8 s average µA
- **This could report PASS while…** the ammeter's burden voltage browns the SoC out, so the part is stuck in reset and 'sleeps' beautifully at a current that means nothing
- **…so assert.** immediately after the current window, the station must still get an answer over SWD from the same power connection. A part in reset does not answer. Two tools, one connection, and they have to agree.

#### AB-08 — Transmit current at 0 dBm — **PASS**

- **Proves.** the radio is drawing what the datasheet says a working radio draws — the number MISSION.md asks for by name
- **Traces to.** MISSION.md artifact 9; nRF54L datasheet 4503_018 v0.10 §11.1.2 (ITX,0dBm = 3.7 mA; IAPPCPU0 = 2.6 mA); ce-spice/out/cr2032_pulse_load/verdict.json (i_peak_mA assert)
- **Measurement.** firmware transmits continuously at 0 dBm; the SMU reads the burst current at 3.000 V
- **Limits.**
  - `transmit current, floor ≥ 3.7 mA` — nRF54L datasheet §11.1.2: ITX,0dBM = 3.7 mA, radio-only, typical. The whole device cannot draw LESS than its radio does, so 3.7 mA is a floor no correct unit falls below. A reading under it means the radio is not transmitting, or the power setting is not 0 dBm — which is exactly the failure a naive 'current is low, good' test would celebrate.
  - `transmit current, ceiling ≤ 8.0 mA` — ce-spice/out/cr2032_pulse_load/verdict.json asserts i_peak_mA < 8.0 with the stated reason that the cell must never see the full 8 mA edge. The design's own simulation ceiling becomes the line's ceiling.
  - `design anchor, not a limit ≈ 6.3 mA` — 3.7 mA radio (ITX,0dBM) + 2.6 mA CPU (IAPPCPU0, Coremark at 128 MHz from NVM) = 6.3 mA typical composite. The datasheet publishes no max column, so this is where units should sit, not a limit they must meet.
- **Equipment.** EQ-SMU, EQ-BLE
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 6 s
- **On failure.** investigate — then rework the RF passives (L2/L3/L4, C18–C23) or replace the SoC
- **Recorded.** board serial, transmit current mA, the power setting the firmware used
- **This could report PASS while…** the current is being drawn by something that is not the radio — a shorted decoupling capacitor, a stuck GPIO driving a load — and the number lands in the window by coincidence
- **…so assert.** the current burst must be time-coincident with an advertisement decoded by EQ-BLE in AB-11. Two independent instruments, one event: the ammeter says power left the rail and the scanner says a packet arrived. Neither alone is evidence.

#### AB-09 — Rail droop under the transmit pulse — **PASS**

- **Proves.** the four 10 µF bulk capacitors are really there and really carrying the pulse
- **Traces to.** SPEC §5 E2; ce-spice/out/cr2032_pulse_load/verdict.json (droop_mV assert, TI SWRA349 §4)
- **Measurement.** scope on VDD at the BT1 pads, single-shot on the transmit burst, with a real CR2032 fitted
- **Limits.**
  - `droop < 400 mV` — ce-spice droop_mV assert: 'a droop this side of 400 mV means the 100 µF reservoir, and not the cell, is carrying the transmission — which is the design intent (TI SWRA349 section 4)'
  - `expected droop, fresh cell ≈ 68 mV` — ce-spice measured 68.175 mV on the fresh-cell scenario. A unit reading near 400 mV passes the limit and is still telling you the bulk is missing.
- **Equipment.** EQ-SCOPE
- **Sampling.** 5 boards per lot, and every board after any change to the bulk capacitor line
- **Type / cycle.** recorded, 90 s
- **On failure.** investigate — check C9–C12 are placed and are the 10 µF part and not a 100 nF from the wrong feeder
- **Recorded.** board serial, droop mV, cell lot
- **This could report PASS while…** the scope probe's ground lead is long enough that the measured droop is mostly probe inductance, or short enough that it misses the droop entirely
- **…so assert.** measure with a spring-tip ground at the BT1 pads and record the measured droop against ce-spice's 68 mV. A unit reading far below 68 mV is not better than the model — it is a probe that is not connected.

#### AB-10 — Accelerometer identity, self-test and response to motion — **PASS**

- **Proves.** the motion sensor DULT makes mandatory answers on its bus, moves when pushed, and reads an angle
- **Traces to.** SPEC §2 F7; docs/ANTI-STALKING.md §4.1 and §4.2; research/06 constraint C9; LIS2DW12 DS11811 Rev 9 §6.2.1 Table 16, §8.3 Table 26, Table 3 (mechanical characteristics); electronics/halo_rev_a/schematic.py (CS strapped high = I²C; SA0 strapped low)
- **Measurement.** over SWD, the firmware reads WHO_AM_I, runs the built-in self-test, then the tilt stage commands 90° and the firmware reports the angle and the wake-up interrupt
- **Limits.**
  - `I²C address responds = 0x18 (7-bit) address` — LIS2DW12 DS11811 §6.2.1: 'if the SA0/SDO pin is connected to ground, the address is 0011000b'. schematic.py strapped SA0 low deliberately and says so.
  - `WHO_AM_I register 0x0F = 0x44 register value` — LIS2DW12 DS11811 Rev 9 §8.3: 'This register is a read-only register. Its value is fixed at 44h.'
  - `self-test positive difference in 70 … 1500 mg` — LIS2DW12 DS11811 Rev 9 Table 3 Mechanical characteristics, symbol ST: min 70 mg, max 1500 mg
  - `measured tilt vs commanded 90° ≤ 10 degrees` — SPEC §2 F7 — 'DULT additionally requires ±10° accuracy'. The number is the standard's, not ours.
  - `wake-up interrupt on ACC_INT1 = asserted within the firmware's configured latency boolean` — docs/ANTI-STALKING.md §4.2: the separated-state alert is motion-triggered at 10 s sampling dropping to 0.5 s. Without this interrupt the tag cannot alert, which is a safety failure, not a feature failure.
- **Equipment.** EQ-SWD, EQ-TILT
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 12 s
- **On failure.** rework — reflow or replace U2; if WHO_AM_I fails, probe I2C_SDA / I2C_SCL first (see the pad request to lane B1)
- **Recorded.** board serial, WHO_AM_I, self-test delta per axis in mg, measured tilt angle, interrupt latency
- **This could report PASS while…** the bus is answered by a pull-up and the firmware returns a cached constant — WHO_AM_I alone proves only that something acknowledged an address
- **…so assert.** the self-test delta is the closer: a cached constant cannot move by 70–1500 mg on command and then move back. And the commanded 90° tilt is a third, mechanical, witness that the die itself responded.

#### AB-11 — Radio: the advertisement is decoded, not merely seen — **PASS**

- **Proves.** this unit is advertising, on both networks, with its own key, at a lawful interval
- **Traces to.** SPEC §2 F1 (Find My frame), F1a (Google Find Hub); DECISIONS.md D7; docs/ANTI-STALKING.md §4.2 (detection payload, advertising interval); tools/findmy_scan.py (the frame layout, from PoPETs 2021 Table 2 cross-checked against OpenHaystack); MISSION.md artifact 7
- **Measurement.** 20 s capture in the RF-quiet box on a Linux/BlueZ host with raw AD access; every field is parsed and compared
- **Limits.**
  - `Find My frame header = 1E FF 4C 00 12 19 bytes 0–5 of the advertisement` — SPEC §2 F1 and tools/findmy_scan.py: AD length 0x1E, AD type 0xFF manufacturer specific, company 0x004C Apple little-endian, Apple payload type 0x12 offline finding, payload length 0x19
  - `advertising address = (p[0] | 0b11000000) : p[1] : p[2] : p[3] : p[4] : p[5] of THIS unit's provisioned key BD_ADDR` — SPEC §2 F1. This is the decisive check: it is not enough that a Find My advertisement exists — it must carry the key AB-04 wrote into this die.
  - `payload key bytes = p[6..27] of this unit's key, then p[0]>>6, then the hint byte bytes 6–30` — SPEC §2 F1
  - `hint byte = 0x00 byte 30` — tools/findmy_scan.py: 'hint (0x00 from a tag; non-zero from an iDevice)'
  - `Google Find Hub service data = service 0xFEAA, frame type 0x40 or 0x41 service data` — SPEC §2 F1a and DECISIONS.md D7 — both networks advertise concurrently from revision A
  - `DULT detection payload = service data TLV type 0x16, 16-bit UUID 0xFCB2, network ID byte present, near-owner bit present service data` — docs/ANTI-STALKING.md §4.2 citing DULT §3.4.2 and §3.6. Without this the tag is invisible to platform detectors, which is the stalking-device failure mode documented in ANTI-STALKING §1.
  - `Find My advertisements in 20 s ≥ 5 count` — DULT §3.10 requires an advertising interval ≤ 4 s. 20 s ÷ 4 s = 5. Fewer than five means the interval is over the limit.
  - `Find My advertisements in 20 s, target ≥ 10 count` — DULT §3.10 targets ≤ 2 s. 20 s ÷ 2 s = 10. Recorded, not go/no-go, because the SHOULD is a target and the MUST is 4 s.
  - `RSSI at the fixture's fixed geometry record — dBm` — CANNOT DETERMINE as a limit. ce-rf has not closed the antenna (SPEC §5 E4; the release pack's own risk list records two round-board geometries that passed their tests while resonating outside the band). Record RSSI on every unit and set the window from the first-article distribution once ce-rf lands.
- **Equipment.** EQ-BLE, EQ-BOX
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 22 s
- **On failure.** investigate — a decode failure with a healthy AB-08 current is firmware or provisioning; a decode failure with a low current is the radio
- **Recorded.** board serial, advertisement count, the decoded frame as hex, key match true/false, FEAA frame type seen, FCB2 seen, RSSI
- **This could report PASS while…** the scanner is decoding a NEIGHBOURING unit's advertisement, or an operator's phone, and reports a beautiful pass for a dead board
- **…so assert.** two gates, and both are needed. First, the address and payload must carry THIS unit's provisioned key — a neighbour's advertisement fails the compare. Second, EQ-BOX runs a leakage self-test every shift: with a powered halo 300 mm outside the closed box the in-box scanner must see zero of its advertisements in 20 s. A box that fails that self-test makes every result in this row worthless.

#### AB-12 — NFC tag read: the owner URL comes back — **PASS**

- **Proves.** a phone tap will open this unit's owner page — the finder path DULT requires
- **Traces to.** SPEC §2 F5, F8; docs/ANTI-STALKING.md §4.3; research/06 constraints C12, C13; DULT §3.15.2–3.15.5; nRF54L datasheet §4.2.4.1.8–4.2.4.1.11 (FICR NFC.TAGHEADER0..3)
- **Measurement.** the fixture's reader, coaxial with the coil at the fixture's fixed gap, reads the NDEF message
- **Limits.**
  - `NDEF read succeeds = True boolean` — SPEC §2 F8 — the SoC's own NFC-A peripheral emulates a read-only Type 4 tag holding the owner URL
  - `URI record format matches https://{URL}?pid=%04x&b=%02x&fv=%08x&e=%s URI template` — docs/ANTI-STALKING.md §4.3 citing DULT §3.15.5
  - `pid field = the product ID written in AB-04 hex` — DULT §3.15.1 — the serial is unique per product ID, so the product ID has to be right for the serial to mean anything
  - `NFCID1 read on the air derives from FICR NFC.TAGHEADER0..3 of the die AB-03 read NFCID1` — nRF54L datasheet §4.2.4.1.8–§4.2.4.1.11: FICR holds a pre-defined valid NFCID1 the firmware populates the tag registers from. It is per-die and the SWD station already read it.
  - `read distance record — mm` — CANNOT DETERMINE as a limit. The absolute operating field limits are ISO/IEC 14443-2's, and this repo does not hold that standard. Record the maximum read distance on a sample and set the production go/no-go as a read at the fixture's fixed gap, calibrated against the golden unit each shift.
- **Equipment.** EQ-NFC
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 8 s
- **On failure.** rework — check AE2's two terminations and C24/C25 (130 pF each); a detuned coil reads at 2 mm and not at 10
- **Recorded.** board serial, the URI read back, NFCID1, read distance if measured
- **This could report PASS while…** the reader read the unit in the next nest, or read a badge in the operator's pocket
- **…so assert.** the NFCID1 the reader gets on the air must derive from the FICR TAGHEADER of the die the SWD station read three tests earlier, and the pid must be the one this station just wrote. A neighbour cannot satisfy either. Second gate: the reader must FAIL to read at the fixture's stated no-read distance — a reader that reads everything reads nothing.

#### AB-13 — SPI NOR flash identity — only if U3 is fitted — **CANNOT DETERMINE**

- **Proves.** the flash answers, if there is a flash
- **Traces to.** electronics/halo_rev_a/schematic.py block 8 (U3 = GD25LQ32E); spec/bom-candidates.json functions.flash
- **Measurement.** firmware issues RDID (0x9F) over the SPI bus and returns the three ID bytes
- **Limits.**
  - `manufacturer ID byte = — byte` — CANNOT DETERMINE. The GD25LQ32E datasheet could not be retrieved in this pass — GigaDevice's own URL returned 404 and LCSC served an HTML anti-bot page instead of the PDF; the only GigaDevice document obtained was the 2023 product selection guide, which carries no ID table. Settle it by reading the 'Read Identification (RDID) 9Fh' section of the GD25LQ32E datasheet and writing the three bytes here. Do NOT type a remembered value into a factory traveller.
  - `device ID bytes = — bytes` — CANNOT DETERMINE — same document, same fix
- **Equipment.** EQ-SWD
- **Sampling.** 100 % if fitted; the row is skipped entirely if U3 is depopulated
- **Type / cycle.** go/no-go, 4 s
- **On failure.** rework — reflow or replace U3
- **Recorded.** board serial, the three RDID bytes as read
- **This could report PASS while…** the SPI bus floats high and the firmware reads 0xFF 0xFF 0xFF, which some drivers report as 'a device'
- **…so assert.** 0xFF FF FF and 0x00 00 00 are both explicit rejects, whatever the correct ID turns out to be. Those two are assertable today even though the right answer is not.
- **Flag.** OPEN QUESTION FOR LANE B1, not a test problem: spec/bom-candidates.json recommends 'omit' for the flash — a halo whose firmware lives in the SoC's own memory does not need it. And GigaDevice's own 2023 product selection guide gives the GD25LQ32E a supply range of 1.65–2.0 V, while schematic.py puts U3 pin 8 on VDD, which is the raw CR2032 rail with no regulator anywhere on the board. If U3 stays, that pairing needs an answer. This plan tests it if it is fitted and says nothing about whether it should be.

#### AB-14 — Sounder drive: anti-phase, at resonance, into a reference bender — **PASS**

- **Proves.** both drive pins work and the drive lands on the bender's resonance
- **Traces to.** DECISIONS.md D11a; SPEC §2 F3, §5 E3; research/fetched/G-acoustics-cells-and-holders.md (Murata 7BB catalogue); docs/MECHANICAL.md §1
- **Measurement.** the fixture presents a reference 7BB-20-3 bender across PIEZO_P / PIEZO_N — the production bender is bonded to the shell, not to the board, so at this station there is nothing on the board to drive. The scope reads the differential waveform.
- **Limits.**
  - `differential drive amplitude > 1.05 × VDD V peak-to-peak` — derived from DECISIONS.md D11a: the bender is 'driven anti-phase from two SoC pins so no boost converter and no inductor are needed'. Anti-phase drive swings 2 × VDD. If either pin is dead, open, or stuck, the swing collapses to at most 1 × VDD. A threshold just above VDD therefore separates a working two-pin drive from every single-pin failure, using no number anyone had to invent.
  - `drive frequency in 3.0 … 4.2 kHz` — Murata 7BB catalogue via research/fetched/G-acoustics-cells-and-holders.md: 7BB-20-3 resonant frequency 3.6 ±0.6 kHz. The drive must sit inside the part's own resonance band or the acoustic test at station 3 has no chance.
  - `reference bender impedance at resonance ≤ 500 Ω` — same Murata catalogue table: 7BB-20-3 resonant impedance max 500 Ω. This is a check on the FIXTURE's reference bender, not on the DUT — a fixture bender that has drifted makes every unit look bad.
- **Equipment.** EQ-SCOPE, EQ-SWD
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 8 s
- **On failure.** rework — one dead GPIO on the SoC; reflow, then replace
- **Recorded.** board serial, Vpp differential, drive frequency, fixture bender serial and its last impedance check
- **This could report PASS while…** one pin drives and the other sits at a DC level, and a single-ended probe on PIEZO_P sees a beautiful full-amplitude square wave
- **…so assert.** measure differentially, never single-ended, and set the threshold above VDD. That is precisely the reading a single-ended probe cannot distinguish and a differential one cannot fake.

#### AB-15 — Cell-removal sense: the two positive rails are independent — **PASS**

- **Proves.** the sense finger is separate from the current finger, which is the whole five-removals reset mechanism
- **Traces to.** SPEC §3 (battery row: 'two positive rails both sensed before boot'); electronics/halo_rev_a/schematic.py (BT1 pad 1 = P+ current finger, pad 3 = P+ sense finger, pad 2 = negative; halo rev A D-5); ce-spice/out/cr2032_pulse_load/verdict.json (v_min_V assert)
- **Measurement.** 3.000 V applied to BT1 pads 1 and 3; firmware reads VBAT_SNS and VBAT_SNS_HI; the fixture then opens pad 3 only and the firmware reports the transition
- **Limits.**
  - `VBAT_SNS_HI with both fingers fed ≈ 3.0 V through the R1/R2 divider V` — schematic.py: R1 = R2 = 4.7 MΩ, 9.4 MΩ total, driven only while the GPIO is low
  - `sense collapse detected after pad 3 opens ≤ 10 ms` — schematic.py board text: 'VBAT_SNS collapses in ~0.24 ms while the bulk holds VDD up'. 10 ms is a 40× margin over the designer's own figure and still far inside a human's fastest cell swap.
  - `VDD during the sense collapse > 1.8 V` — ce-spice v_min_V assert: 'below 1.8 V there is under 100 mV to the SoC's absolute minimum; the radio browns out mid-transmission and the tracker goes silent'. The bulk must hold the rail up while the sense finger drops, or the reset counter loses its count.
- **Equipment.** EQ-SMU, EQ-SWD
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 7 s
- **On failure.** rework — a bridged pad 1 to pad 3 is the likely defect and it defeats the mechanism silently
- **Recorded.** board serial, VBAT_SNS, VBAT_SNS_HI, collapse time ms, VDD minimum during collapse
- **This could report PASS while…** pads 1 and 3 are shorted together by a solder bridge under the contact, so both read 3 V, both read the same thing, and the test that only checks voltages passes
- **…so assert.** the test must OPEN pad 3 alone and see VBAT_SNS_HI collapse while VDD holds. A bridge makes that impossible: either both collapse or neither does. Reading the two voltages is not the test; separating them is.

#### AB-16 — Battery contact continuity and resistance — **PASS**

- **Proves.** all three stamped fingers reach the copper, through the carrier, with the board seated
- **Traces to.** docs/MECHANICAL.md §6; SPEC §3 (three sprung contacts); ce-spice/out/cr2032_pulse_load/verdict.json; ce-connections/ (the contact-force connection folder grades itself CANNOT DETERMINE)
- **Measurement.** four-wire: force 10 mA from a probe on each stamped finger's cell-facing face to the board's VDD/GND, measure the drop
- **Limits.**
  - `resistance, each contact path — gate ≤ 1.0 Ω` — derived from two in-repo numbers: ce-spice's peak cell current is 8.0 mA, and the droop budget is 400 mV. 1 Ω at 8 mA is 8 mV, under 2 % of that budget — so 1 Ω is generous electrically while still failing any open, oxide or cold joint, which present as ohms or as an open. The tighter number belongs to the plating spec, which does not exist yet.
  - `resistance, each contact path — recorded record — mΩ` — CANNOT DETERMINE as a tight limit — nobody has measured a stamped C5191 finger against a plated pad in this project. Record every reading; once 200 units exist, replace the 1 Ω gate with mean + 3σ.
  - `continuity, all three fingers = 3 count` — docs/MECHANICAL.md §6 and schematic.py: pad 1 P+ current, pad 2 negative, pad 3 P+ sense. Two of three is a unit that boots and cannot count cell removals.
- **Equipment.** EQ-SMU
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 10 s
- **On failure.** rework — reseat the board in the carrier, or replace the contact
- **Recorded.** board serial, three resistances, carrier lot
- **This could report PASS while…** the probe presses the finger down onto the pad and makes the joint it is supposed to be measuring
- **…so assert.** the probe must contact the finger's CELL-facing face, at the point the cell touches, and never the root. Four-wire, so the probe's own contact resistance is out of the measurement. If a two-wire reading is ever used the number is the probe's, not the product's.

#### AB-17 — Contact spring force — **PASS**

- **Proves.** the three fingers push the cell with the force the door mechanism is designed around
- **Traces to.** docs/MECHANICAL.md §5.3 and §6; DECISIONS.md D3, D13
- **Measurement.** force gauge on each finger at the modelled closed-position deflection δ = 0.400 mm
- **Limits.**
  - `total contact force in 0.5 … 1.5 N` — docs/MECHANICAL.md §5.3 — the calculated 1.79 N total is described as 'inside the usual 0.5–1.5 N band for a coin cell'. Note the tension in that sentence: the repo's own model lands ABOVE the band it cites. Recording the measured value is how that gets settled.
  - `force per finger at δ = 0.400 mm ≈ 0.596 N` — docs/MECHANICAL.md §5.3, k = 3EI/L³ with L = 6.074 mm, w = 3.60 mm, t = 0.15 mm, C5191, E = 110 GPa. CALCULATED, NOT MEASURED — MECHANICAL §9 lists the contacts' spring rate as unmeasured and names a force gauge on three stamped fingers as the test that settles it. This row IS that test, which is why the value is an expected reading and not a gate.
  - `model correction note up to +12 % %` — docs/MECHANICAL.md §5.3: w/L = 0.59, so the strip behaves partly as a plate and the real rate may be up to 1/(1−ν²) higher. A measurement 12 % above the model is the model being right, not the part being wrong.
- **Equipment.** EQ-FORCE
- **Sampling.** 5 carriers per contact-stamping lot
- **Type / cycle.** recorded, 180 s
- **On failure.** investigate the stamping — spring force is a die and heat-treat problem, and it moves for a whole lot at once
- **Recorded.** carrier lot, three forces, deflection used
- **This could report PASS while…** the gauge measures the finger at the wrong deflection, so any spring rate produces the target force at some δ
- **…so assert.** measure force at TWO deflections and compute the rate. The rate is the part's property; a single force reading is a property of wherever the operator stopped.

### Station 3 — Sealed unit (9 tests)

#### FU-01 — Battery door: rotation alone must not open it — **PASS**

- **Proves.** the compliance claim — a tool or two independent simultaneous hand movements — on the real moulded part and not on the model
- **Traces to.** research/06 constraint C21; 16 CFR part 1263 / ANSI-UL 4200A-2023; DECISIONS.md D3, D13; docs/MECHANICAL.md §5.2 (probes B, C, D)
- **Measurement.** the operator twists the closed door without pressing, then presses and twists
- **Limits.**
  - `opens on rotation alone = False boolean` — 16 CFR 1263 via CPSC business guidance: 'Battery compartments … must be secured such that they require the use of a tool or at least two independent and simultaneous hand movements to open.' design.py probe C measured 0.2735 mm³ of interference at 10° with no press — the detent is a square step, so rotation is refused at ANY torque rather than merely resisted (MECHANICAL §5.2).
  - `opens on press + twist = True boolean` — design.py probe D measured 0.0000 mm³ at 0.250 mm press + 10° twist. A door that will not open is also a failure, and MECHANICAL §8 records that this exact check went red first on the printed variant.
  - `cell retained when the door is pushed down 0.3 mm = True boolean` — design.py probe B measured 3.7114 mm³ of foot engagement — the feet retain the door and it cannot fall out
- **Equipment.** —
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 12 s
- **On failure.** scrap or de-bond investigation — the shell is bonded and does not come apart twice
- **Recorded.** unit serial, rotation-alone result, press-and-twist result
- **This could report PASS while…** the operator applies a little press without noticing — human hands press while they twist — and a door that opens on rotation alone is passed as compliant
- **…so assert.** the twist must be applied through a mandrel that cannot transmit axial load, on a fixture that measures the axial force during the twist and rejects the trial if it exceeds a stated threshold. A compliance test done by hand measures the hand.

#### FU-02 — Battery door: opening force and torque — **CANNOT DETERMINE**

- **Proves.** the door is neither so loose it fails the standard nor so stiff nobody can open it
- **Traces to.** docs/MECHANICAL.md §5.3; research/06 §6.1 (and the Forbes accessibility piece it cites); DECISIONS.md D13
- **Measurement.** force gauge for the axial press, torque gauge for the rotation, both peak-hold
- **Limits.**
  - `press force to open ≥ 2.91 N` — docs/MECHANICAL.md §5.3 — 2.91 N total, three fingers at 0.969 N each with the door pressed 0.250 mm. CALCULATED, with the model's own caveats stated there. MECHANICAL §9 lists the door's opening force as unmeasured and names a force gauge and a torque gauge as the test. This row is that test.
  - `opening torque ≥ 13.4 N·mm` — docs/MECHANICAL.md §5.3 — friction only, μ = 0.35 ASSUMED for PC on dry stainless, on three tab/foot interfaces at R 13.15 mm. The assumption is flagged in MECHANICAL itself; the measurement replaces it.
  - `upper bound on press force and torque ≤ — N and N·mm` — CANNOT DETERMINE, and this is the more important gap. There is no published usability ceiling in this repo — only research/06 §6.1's citation of a Forbes piece calling the AirTag's door an accessibility failure, which carries no number. Settle it with a usability study across an age and grip-strength range, or by adopting a published hand-strength percentile. Until then a stiff door ships.
- **Equipment.** EQ-FORCE, EQ-TORQUE
- **Sampling.** 5 units per moulding-tool shot lot, and every unit of the first article
- **Type / cycle.** recorded, 150 s
- **On failure.** investigate the mould — the detent height (0.250 mm) and the 12° closing helicoid are tool features, and they move for a lot at a time
- **Recorded.** unit serial, shot lot, press force N, opening torque N·mm
- **This could report PASS while…** the torque gauge reads the operator's grip on the shell rather than the door's detent — the shell is bonded, so it resists too
- **…so assert.** clamp the shell in the fixture and drive only the door. Then record BOTH the breakaway peak and the running torque: a detent shows as a peak followed by a lower plateau. A single number with no peak means the mandrel slipped.

#### FU-03 — Acoustic output at 25 cm — **CANNOT DETERMINE**

- **Proves.** the sealed unit is audible — the requirement DULT makes mandatory and D11a bet the mechanical design on
- **Traces to.** SPEC §2 F3; docs/ANTI-STALKING.md §4.1; research/06 constraint C8; DULT §3.13.3; ISO 532-1:2017; DECISIONS.md D11a; DECISIONS.md D17 (the shell's inside is a flat land, so the bender is not strained); docs/MECHANICAL.md §9
- **Measurement.** sealed unit suspended in the acoustic hood, microphone on-axis at 250 mm; firmware plays the DULT sound; class 1 meter reads A-weighted fast SPL and the third-octave bands at 3.15 kHz and 4 kHz
- **Limits.**
  - `loudness level ≥ 60 Phon (ISO 532-1:2017) at 25 cm` — DULT §3.13.3 via docs/ANTI-STALKING.md §4.1 and research/06 constraint C8. THIS IS THE REQUIREMENT — and it cannot be measured with a sound level meter. Phon is a loudness level computed under ISO 532-1; dB(A) is not phon. The absolute compliance measurement is a qualification test (QUAL-04), not a line test.
  - `production A-weighted SPL at 25 cm ≥ — dB(A)` — CANNOT DETERMINE, and this is the single largest open number in the plan. The production limit must be the golden unit's dB(A) reading minus a tolerance from gauge R&R, where the golden unit's loudness in phon was measured under ISO 532-1 in qualification. Two measurements settle it: (1) QUAL-04's phon measurement on a golden unit, (2) a gauge R&R study on this hood and this meter. Neither has been done. Nobody may write a dB(A) number into this cell from the 60 in the row above — they are different quantities and swapping them is exactly the error docs/TOOLS-THAT-LIE.md exists to stop.
  - `reference datum, not a limit note 72.3–74.3 dB at 25 cm dB` — iFixit measured the real AirTag at 78–80 dB at about 13 cm (DECISIONS.md D11a). Inverse-square from 13 cm to 25 cm is 20·log₁₀(25/13) = 5.7 dB. This is what the product being copied does, recorded for comparison. It is NOT halo's limit — halo's requirement is DULT's 60 phon, and D11a warns that Apple's '50% louder' claim carries no decibel figure and must not be converted into one.
  - `spectral peak in 3.0 … 4.2 kHz` — Murata 7BB-20-3 resonance 3.6 ±0.6 kHz (research/fetched/G-acoustics-cells-and-holders.md). The energy must be at the bender's resonance; a broadband reading at the right level with no peak there is not this unit sounding.
  - `hood background with the DUT silent ≤ golden reading − 10 dB` — derived, not cited: 10 dB of separation means the background contributes 10·log₁₀(1 + 10⁻¹) = 0.41 dB to the total, which is below the meter's own class 1 tolerance. Any less separation and the line's noise is inside the measurement.
- **Equipment.** EQ-SLM, EQ-HOOD
- **Sampling.** 100 % — this is a safety requirement, not a quality requirement. A silent halo is the stalking device docs/ANTI-STALKING.md §1 refuses to ship, and a sampling plan lets some of them out of the door.
- **Type / cycle.** go/no-go, 20 s
- **On failure.** scrap or de-bond investigation — the bender is bonded to the shell and the shell is bonded to the carrier
- **Recorded.** unit serial, dB(A) at 25 cm, third-octave level at 3.15 and 4 kHz, hood background, calibrator check of the shift, golden unit reading of the shift
- **This could report PASS while…** the meter is reading the line's own noise, or the unit in the next hood, or a table reflection is adding several dB
- **…so assert.** three gates. The hood background must sit 10 dB below the golden reading with the DUT present but silent. The energy must peak in the bender's own 3.6 kHz band, which factory broadband noise does not do. And the unit must be suspended, never laid on a hard surface, because a reflecting plane can add up to 6 dB and would turn a failing unit into a passing one.

#### FU-04 — Final functional test, sealed, on its own cell, no wires — **PASS**

- **Proves.** the product as the customer receives it does all four of the things it exists to do
- **Traces to.** SPEC §2 F1, F1a, F3, F5, F7, F8; docs/ANTI-STALKING.md §4.2 (non-owner sound control); research/06 constraints C8, C10, C12; MISSION.md artifact 9
- **Measurement.** sealed unit in the RF-quiet box, powered only by its fitted cell. Four checks in one 30 s window.
- **Limits.**
  - `Find My advertisement decoded with this unit's key = True boolean` — as AB-11, re-run on the sealed unit because the shell, the carrier's LDS antennas and the cell's copper all sit inside the antenna's near field and none of them were present at station 2
  - `Google Find Hub frame seen = 0xFEAA, frame 0x40 or 0x41 service data` — SPEC §2 F1a, DECISIONS.md D7
  - `DULT detection payload seen = 0xFCB2 service data with the near-owner bit service data` — docs/ANTI-STALKING.md §4.2, DULT §3.4.2/§3.6
  - `NFC tap reads this unit's owner URL = True boolean` — SPEC §2 F8; the coil is now behind the moulded shell, which is the only configuration a customer ever sees
  - `sounder responds to a stranger's Sound_Start = Sound_Start (0x0300) accepted, Command_Response (0x0302) returned, Sound_Completed (0x0303) returned DULT opcodes` — docs/ANTI-STALKING.md §4.2 citing DULT §3.13.4 Table 18 — all four opcodes REQUIRED, available only in the separated state. The test station acts as the stranger's phone, which is exactly the safety path being verified.
  - `motion changes behaviour = True boolean` — SPEC §2 F7; the station shakes the nest and the advertising behaviour or the accelerometer's reported state must change
  - `sound duration in 5 … 30 s` — docs/ANTI-STALKING.md §4.2 citing DULT §3.13.4.1: 5 s minimum, 30 s maximum, 12 s target. The station measures the play length it commanded.
- **Equipment.** EQ-BLE, EQ-BOX, EQ-NFC, EQ-TILT
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 32 s
- **On failure.** scrap or investigate — nothing at this station is reworkable
- **Recorded.** unit serial, all seven results, the decoded frames as hex, sound duration measured
- **This could report PASS while…** the sealed unit is dead and the station is decoding the previous unit still sitting in the reject bin next to the box
- **…so assert.** the key compare pins every packet to this unit, the NFCID1 pins the tap to this die, and EQ-BOX's shift leakage self-test pins the whole measurement to the inside of the box. Also: the sounder check here is the only one in the plan that exercises the full path — GATT command in, opcode response out, acoustic energy in FU-03. Neither test alone proves a stranger can make this tag beep.

#### FU-05 — Printed serial matches the programmed serial — **PASS**

- **Proves.** the number a finder reads off the shell is the number inside the tag
- **Traces to.** docs/ANTI-STALKING.md §4.1; research/06 constraint C11; DULT §3.15.1
- **Measurement.** vision station reads the printed serial; the NFC reader reads the tag; the two are compared against the traceability database row for this unit
- **Limits.**
  - `printed serial = the serial written in AB-04 string` — DULT §3.15.1: 'The serial number MUST be unique for each product ID' and 'SHALL be printed and be easily accessible on the accessory'
  - `serial legible to the vision station = True boolean` — DULT §3.15.1 'easily accessible' — if a camera cannot read it, a frightened person holding a strange tag at arm's length cannot either
  - `battery ingestion warning present on the product = True boolean` — 16 CFR 1263 via CPSC business guidance and research/06 §6.1 — warnings must appear on the packaging, on the product 'if practicable', and in the instructions
- **Equipment.** EQ-VISION, EQ-NFC, EQ-DB
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 6 s
- **On failure.** rework the label if the label is wrong; scrap if the label was applied to the wrong unit and the unit is already sealed
- **Recorded.** unit serial, OCR result, NFC result, match true/false, label lot
- **This could report PASS while…** labels are applied from a roll in sequence and the roll slips by one, so every unit carries the next unit's serial and every unit still has A serial
- **…so assert.** the comparison is against the database row keyed on the SoC's factory DEVICEID, not against the label roll. A one-off slip fails on the first unit after the slip, not at the end of the roll.

#### FU-06 — Finished mass — **CANNOT DETERMINE**

- **Proves.** nothing is missing inside a sealed puck nobody can open
- **Traces to.** docs/MECHANICAL.md §10 (measured assembly 7.8 g, with the part-by-part breakdown)
- **Measurement.** precision balance, sealed unit with cell fitted
- **Limits.**
  - `mass window ± 0.3 g around the first-article mean` — derived from MECHANICAL §10's own breakdown: the cell is 3.0 g, the door 1.4 g, the shell 1.5 g, the carrier 0.7 g, the bender 0.5 g. Every part that could plausibly be left out weighs at least 0.5 g, so a ±0.3 g window separates a complete unit from a unit missing any one of them, with no overlap. This is a derivation from measured masses, not a chosen tolerance.
  - `absolute target mass = — g` — CANNOT DETERMINE. MECHANICAL §10's 7.8 g explicitly excludes the board's components and copper, and no populated-board mass exists in this repo. Weigh 30 first articles, take the mean, and this row becomes absolute. Until then the window is relative to that mean and cannot be set before the first article exists.
- **Equipment.** EQ-SCALE
- **Sampling.** 100 %
- **Type / cycle.** go/no-go, 5 s
- **On failure.** scrap — a sealed unit with the wrong mass has something missing inside it and cannot be opened to find out which
- **Recorded.** unit serial, mass g
- **This could report PASS while…** the balance drifts and the whole shift reads 0.4 g heavy, so a shift of units missing the bender passes together
- **…so assert.** weigh a certified mass at the start of every shift and after any bump to the bench, and record it. A drifting balance is caught by the check mass, never by the product.

#### FU-07 — Parting-line and seam inspection — **CANNOT DETERMINE**

- **Proves.** the shell-to-carrier adhesive joint closed, which is both the structural joint and the seal
- **Traces to.** docs/MECHANICAL.md §7 (198 mm² bond area, 0.15 mm gap); docs/MECHANICAL.md §8.1 (fits table)
- **Measurement.** visual inspection of the seam all the way round, plus a go/no-go feeler at the parting line
- **Limits.**
  - `radial adhesive gap, carrier Ø27.60 in shell bore Ø27.90 = 0.15 mm radial` — docs/MECHANICAL.md §8.1 — 'adhesive gap; a structural epoxy wants 0.10–0.20'
  - `visible adhesive squeeze-out on the outer surface = 0 count` — cosmetic; and squeeze-out on the outside means starvation somewhere on the inside of the 198 mm² bond
  - `seam step ≤ — mm` — CANNOT DETERMINE — no cosmetic specification exists for halo. Settle it by writing a cosmetic standard with a boundary-sample set, which is a normal first-article deliverable and a thing the factory is better at than we are.
- **Equipment.** EQ-VISION
- **Sampling.** 100 % visual; the gap measured on 5 units per shot lot
- **Type / cycle.** go/no-go, 8 s
- **On failure.** scrap — an under-filled bond is both a structural and a sealing failure and cannot be re-bonded
- **Recorded.** unit serial, shot lot, adhesive lot and cure time, defects found
- **This could report PASS while…** a bond that looks perfect from outside is starved on the inside, because the only thing anyone can see is the 0.15 mm seam
- **…so assert.** there is no per-unit assert available for bond coverage — this is honestly a process control, not a test. Control it by recording the adhesive lot, the dispensed mass per unit and the cure profile, and by sectioning units from each shot lot (QUAL-11). A visual check on a hidden joint is not evidence and is not presented as one.

#### FU-08 — Door retention pull — **PASS**

- **Proves.** the door does not come off in a pocket
- **Traces to.** research/06 §6.2 (EN IEC 62115 as the accessibility yardstick — 20 N for 10 s); docs/MECHANICAL.md §5.2 probe B
- **Measurement.** axial pull on the closed door with the shell clamped
- **Limits.**
  - `axial pull ≥ 20 N for 10 s without release` — research/06 §6.2, quoting the EN IEC 62115 fastener-retention test: 'a 20 N pull on the fastener for 10 s, which must remain attached'. research/06 is explicit that halo is NOT a toy so EN 62115 does not apply directly, but it names it as 'the obvious yardstick to design to'. Used here as a yardstick, labelled as one.
- **Equipment.** EQ-FORCE
- **Sampling.** 5 units per shot lot
- **Type / cycle.** go/no-go, 60 s
- **On failure.** investigate the mould — the bayonet feet are a tool feature
- **Recorded.** unit serial, shot lot, peak pull force, released yes/no
- **This could report PASS while…** the pull is applied to the shell and the whole unit moves, so nothing loads the bayonet at all
- **…so assert.** clamp the shell, pull the door. Record whether it released and at what force — 'did not release at 20 N' and 'released at 19 N' are different data and only the second tells you the margin.

#### FU-09 — Antenna return loss on the assembled unit — **CANNOT DETERMINE**

- **Proves.** the antenna resonates IN the band — the exact check whose absence produced two false passes in this project
- **Traces to.** SPEC §5 E4; docs/TOOLS-THAT-LIE.md (incident 2: two antenna simulations returned PASS while resonating at 4.0 and 5.8 GHz against a 2.44 GHz target); out/release/CONVERGENCE.html; 47 CFR §15.247; EN 300 328
- **Measurement.** VNA, 1-port, on a sacrificial unit with a coaxial pigtail soldered at the antenna feed — or, if lane B1 provides no feed access, on a near-field probe at a fixed position over the feed
- **Limits.**
  - `resonant frequency in 2400 … 2483.5 MHz` — the 2.4 GHz ISM band as defined by 47 CFR §15.247 and EN 300 328 (research/06 §5.2–5.3). THIS IS THE ASSERTION THAT WAS MISSING: docs/TOOLS-THAT-LIE.md records two antenna simulations that passed because the asserts tested only match depth and efficiency and never the frequency. Frequency is asserted first here, and depth second.
  - `|S11| at the resonance ≤ — dB` — CANNOT DETERMINE. −10 dB is the industry convention but nobody in this repo has chosen a figure and ce-rf has not landed the antenna on the real board outline with the cell's copper in place (SPEC §5 E4). Settle it from ce-rf's own assert once it exists.
  - `sanity assert = the implied effective permittivity must be greater than 1 dimensionless` — docs/TOOLS-THAT-LIE.md rule 4 — a dielectric cannot speed a wave up. The two failing geometries implied 0.676 and 0.216. Free to compute from the resonant frequency and the trace length, and no wrong answer satisfies it.
- **Equipment.** EQ-VNA
- **Sampling.** 3 units per build lot, destructive
- **Type / cycle.** recorded, 600 s
- **On failure.** investigate — the RF passives L2/L3/L4 and C18–C23 are marked PLACEHOLDER in the schematic title block and are re-valued from ce-rf measurements
- **Recorded.** unit serial, resonant frequency MHz, |S11| dB, the implied effective permittivity
- **This could report PASS while…** the match is deep and the resonance is in the wrong band entirely — which is not hypothetical, it happened twice in this project in one night
- **…so assert.** assert the frequency BEFORE the depth, and add the permittivity sanity check. Either one alone would have caught both historical failures.

## 4. The fixtures the factory must build

### FX-1 — Bare-board electrical test (the fabricator's) (bare)

Nothing for the factory to build. What halo must supply is the IPC-D-356 netlist exported from electronics/halo_rev_a/out/halo_rev_a.net, and what halo must demand back is the ET report with the net count, the thresholds used and the opens/shorts counts on it.

**Calibration.** the fab's own

The one thing that can go wrong here is invisible: a netlist extracted from the Gerbers instead of from the schematic. Require the 41-net count on the report.

### FX-2 — In-circuit, programming and functional fixture (board)

A single-nest bed-of-nails carrying the board-in-carrier sub-assembly. One nest, one pneumatic actuator, a TC2030 no-legs pogo head for SWD, a source-measure unit on the battery pads, a tilt/tap actuator, a reference piezo bender, and an RF-quiet enclosure the whole nest can be closed inside for AB-06 and AB-11. The nest must locate the board on its own features and not on the carrier, because the carrier's moulding tolerance is looser than the pogo pitch.

| probe point | net | for | does it exist? |
|---|---|---|---|
| `J1.1 … J1.6` | `VDD, SWDIO, nRESET, SWDCLK, GND, SWO` | AB-03, AB-04, AB-05, AB-10, AB-13, AB-14, AB-15 | YES — the TC2030 footprint is already on the board (schematic.py block 9, footprint Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical). No connector is fitted; these are pogo pads and they cost zero height, which is why they fit the 1.5 mm budget. |
| `BT1 pad 1` | `VDD (positive current finger)` | AB-02, AB-07, AB-08, AB-09, AB-15 | YES — a battery contact pad, probed directly. This is also the supply injection point, so no separate power pad is needed. |
| `BT1 pad 2` | `GND (negative)` | AB-02, AB-07, AB-08, AB-16 | YES |
| `BT1 pad 3` | `VBAT_SNS_HI (positive sense finger)` | AB-15, AB-16 | YES |
| `TP_VDD_FORCE / TP_VDD_SENSE` | `VDD` | AB-07 and AB-08 four-wire current measurement | NO — REQUEST TO LANE B1. A four-wire measurement needs two independent contacts per rail. Probing BT1 pad 1 twice with two pogos in one pad is not a Kelvin connection. |
| `TP_GND_FORCE / TP_GND_SENSE` | `GND` | AB-07, AB-08, AB-16 | NO — REQUEST TO LANE B1 |
| `TP_PIEZO_P / TP_PIEZO_N` | `PIEZO_P, PIEZO_N` | AB-14 | NO — REQUEST TO LANE B1. The production bender is bonded to the shell, so these two nets terminate nowhere the fixture can reach without pads. |
| `TP_VBAT_SNS` | `VBAT_SNS` | AB-15 diagnosis when the sense path fails | NO — REQUEST TO LANE B1 |
| `TP_SDA / TP_SCL` | `I2C_SDA, I2C_SCL` | AB-10 diagnosis when WHO_AM_I fails | NO — REQUEST TO LANE B1. Diagnostic only; the test itself runs over SWD. |
| `TP_NFC1 / TP_NFC2` | `NFC1, NFC2` | coil resonance measurement on a sample | NO — REQUEST TO LANE B1 |
| `two fiducials on the probed side` | `—` | bed-of-nails registration | NO — REQUEST TO LANE B1. A Ø26.00 mm circle has no datum. Without two fiducials the nest locates on the outline, and the outline tolerance is BB-02's CANNOT DETERMINE. |

**Calibration.** SMU verified each shift against a 1.000 MΩ ±0.01 % resistor, which must read 3.000 µA. Pogo tips replaced on a stroke count. Tilt stage checked weekly against an inclinometer. Reference bender's resonant impedance checked monthly against the Murata 500 Ω maximum.

The failure mode to design against is the ammeter's burden voltage browning the SoC out during AB-07, which produces a beautiful sleep current from a part sitting in reset. The fixture must be able to talk SWD through the same connection immediately after the current window.

### FX-3 — RF-quiet enclosure (board and unit)

A shielded, absorber-lined box large enough to close over the nest, with a fixed receive antenna at a stated distance and orientation, and a feed-through for the fixture's DC and SWD lines. The scanner host inside or outside must be Linux/BlueZ or an nRF sniffer.

**Calibration.** Acceptance is measured, not quoted from a brochure: with a powered halo 300 mm outside the closed box, the in-box scanner must see zero of its advertisements in a 20 s capture. Run this leakage self-test at the start of every shift and after any service to the lid seal or the feed-throughs. A box that fails it invalidates every AB-11, AB-06 and FU-04 result taken since the last passing self-test.

macOS is disqualified as a scanner host and the reason is documented, not assumed — tools/findmy_scan.py records that CoreBluetooth substitutes a per-host random UUID for the peripheral address and never exposes the raw AD structure. On macOS the key-match assert that makes AB-11 mean anything is impossible.

### FX-4 — NFC read station (board and unit)

An ISO/IEC 14443-A reader mounted coaxial with the coil at a gap fixed by the fixture, never by hand. Two positions: the nominal read gap, and a stated no-read gap.

**Calibration.** Each shift, against the golden unit: it must read at the nominal gap AND fail to read at the no-read gap. A reader that reads at both is over-driven and will pass a badly detuned coil.

At station 3 the coil is behind the moulded PC shell, which is why FU-04 repeats the read rather than trusting AB-12.

### FX-5 — Acoustic hood (unit)

A lined hood with the unit SUSPENDED — not laid on a plate, because a reflecting plane near a 20 mm radiator can add several dB and would turn a failing unit into a passing one. Microphone on-axis at 250 mm ±5 mm. Class 1 meter with third-octave analysis so the 3.15 kHz and 4 kHz bands can be read out separately.

**Calibration.** IEC 60942 class 1 acoustic calibrator on the meter at the start of every shift, recorded. Background measured with the DUT present but silent every shift; it must sit at least 10 dB below the golden unit's reading. The golden unit is measured every shift and its reading is recorded as a control chart, not glanced at.

This fixture cannot measure the requirement. The requirement is 60 Phon under ISO 532-1:2017; this hood measures dB(A). The transfer between them is QUAL-04 plus a gauge R&R study, and until both exist the production limit is an open number — see FU-03.

### FX-6 — Force and torque bench (board and unit)

A clamp that holds the shell (or the carrier) while a mandrel drives only the door, plus a force gauge for the axial press and for the contact fingers. The mandrel must not transmit axial load into the door during the torque measurement, or FU-01's compliance test measures the operator's hand.

**Calibration.** Force gauge checked daily against a 1 kg mass (9.81 N). Torque gauge annually, traceable.

This bench closes three of the four CANNOT DETERMINEs docs/MECHANICAL.md §9 lists: the contacts' spring rate, the door's press force and the door's opening torque. Those numbers are calculated today, with μ = 0.35 an admitted assumption.

### FX-7 — Traceability database (all)

One append-only row per unit, keyed on the SoC's factory INFO.DEVICEID — a 64-bit identifier Nordic burned in, which no station can accidentally duplicate. Every station writes to the same row.

**Calibration.** The duplicate-rejection path is exercised weekly with a deliberate duplicate serial and a deliberate duplicate key fingerprint. A uniqueness check nobody has ever seen fail is not known to work.

This is not a nice-to-have. AB-04's whole assert — that every unit gets its own serial and its own key — is enforced by this database and by nothing else, because a writer that repeats itself cannot detect that it repeated itself.

## 5. Equipment, and how each piece is proved honest

| id | instrument | specification | calibration / self-test | owner |
|---|---|---|---|---|
| `EQ-ET` | Bare-board electrical tester (flying probe or universal grid) | netlist-driven, IPC-D-356 input | the fabricator's own schedule; the ET report must state the continuity and isolation thresholds used | PCB fabricator |
| `EQ-SMU` | Source-measure unit, 3.00 V source with current measurement | sources 3.000 V ±0.5 %; measures 100 nA to 20 mA in one sweep without a range-change glitch that browns the SoC out; 1 nA resolution on the low range | annual, traceable; verified each shift against a 1.000 MΩ ±0.01 % resistor which must read 3.000 µA | test station 2 |
| `EQ-SWD` | SWD debug probe on a TC2030 no-legs pogo head | 6-pin 1.27 mm Tag-Connect TC2030-IDC-NL geometry, matching the J1 footprint already on the board | pogo tips replaced on a stroke count, not on failure | test station 2 |
| `EQ-BLE` | Bluetooth scanner with raw advertising-data access | Linux/BlueZ host or an nRF sniffer. Must expose the advertiser's Bluetooth address AND the raw AD structure. macOS/CoreBluetooth is disqualified — see notes. | self-test each shift: with the DUT unpowered, zero Find My advertisements in 20 s | test stations 2 and 3 |
| `EQ-BOX` | RF-quiet enclosure | shielded box, absorber-lined, DUT on a fixed nest, receive antenna at a fixed distance and orientation. Acceptance is measured, not quoted: with a powered halo 300 mm outside the closed box, the in-box scanner must see zero of its advertisements in 20 s. | leakage self-test at the start of every shift and after any lid-seal service | test stations 2 and 3 |
| `EQ-NFC` | NFC reader on a fixed geometry | ISO/IEC 14443-A reader, NFC Forum Type 4 Tag capable, mounted coaxial with the coil at a fixed gap set by the fixture, not by hand | each shift against the golden unit; the reader must also FAIL to read at the fixture's stated no-read distance, or it is over-driven | test stations 2 and 3 |
| `EQ-SCOPE` | Oscilloscope, 2 channels, differential-capable | ≥ 20 MHz, ≥ 8 bit, single-shot capture on a rail-droop trigger | annual, traceable | test station 2, sample tests |
| `EQ-TILT` | Motion actuator: a commanded tilt stage or a solenoid tapper | commands a repeatable 90° ±1° rotation about the board's X axis, and a repeatable tap | the commanded angle checked against an inclinometer weekly | test station 2 |
| `EQ-SLM` | Class 1 sound level meter | IEC 61672-1 class 1, A-weighting, fast, with third-octave analysis at the 3.15 kHz and 4 kHz bands | acoustic calibrator to IEC 60942 class 1 at the start of every shift; annual traceable calibration of the meter | test station 3 |
| `EQ-HOOD` | Acoustic hood | the DUT suspended (not laid on a hard surface — a table reflection can add several dB), microphone on-axis at 250 mm ±5 mm, hood lined so the background at the microphone is at least 10 dB below the golden unit's reading | background measured with the DUT present but silent at the start of every shift | test station 3 |
| `EQ-FORCE` | Force gauge | 0–20 N, ±0.5 % of reading, peak-hold | annual, traceable; checked daily against a 1 kg mass (9.81 N) | sample bench |
| `EQ-TORQUE` | Torque gauge | 0–100 N·mm, ±1 % of reading, peak-hold, with a mandrel that grips the door's rim without deforming the 0.30 mm stainless | annual, traceable | sample bench |
| `EQ-SCALE` | Precision balance | 0–50 g, 0.01 g resolution | internal calibration daily; external mass weekly | test station 3 |
| `EQ-VISION` | Vision station with OCR / 2D code reader | reads the printed serial and the ingestion-warning artwork; resolution sufficient to resolve the smallest printed character | each shift against a golden label carrier | test station 3 |
| `EQ-VNA` | Vector network analyser | 300 kHz – 6 GHz, 1-port calibrated at the probe tip | SOL calibration at the start of every measurement session, at the probe tip and not at the cable end | sample bench |
| `EQ-AOI` | Automated optical inspection | post-reflow AOI programmed from the CPL, with the 0201 passives in the recipe | the fabricator's own | SMT line |
| `EQ-DB` | Traceability database | one row per unit keyed on the SoC's factory DEVICEID; append-only; rejects a duplicate halo serial at write time | n/a — but the duplicate-serial rejection is exercised weekly with a deliberate duplicate | the line |

## 6. Test pads requested from lane B1

The board carries no test points today. Every point below is a request, not an edit — lane B1 owns `electronics/` and this lane did not touch it.

| # | pad | net | why | constraint |
|---|---|---|---|---|
| 1 | `TP_VDD_FORCE and TP_VDD_SENSE` | `VDD` | AB-07 and AB-08 are four-wire current measurements. Two pogos landing in one BT1 pad is not a Kelvin connection — the force current flows through the same contact the sense line measures, and the contact resistance ends up in the reading. Two independent pads. | Ø0.9 mm, soldermask-free, ≥1.27 mm pitch, ≥1.0 mm from the board edge, on the probed side |
| 2 | `TP_GND_FORCE and TP_GND_SENSE` | `GND` | same, for the return path, and AB-16's four-wire contact resistance needs it too | as above |
| 3 | `TP_PIEZO_P and TP_PIEZO_N` | `PIEZO_P, PIEZO_N` | AB-14 measures the differential drive amplitude, and the assert that catches a single dead GPIO is a differential one. The production bender is bonded to the shell (D11a), so these nets have no reachable termination on the board at all today. | as above; the two pads must be adjacent so a differential probe can span them with a short loop |
| 4 | `TP_VBAT_SNS` | `VBAT_SNS` | AB-15 proves the sense finger is independent of the current finger. When it fails, the pad is what tells you whether the fault is the divider or the contact. | as above; diagnostic, so a single pad is enough |
| 5 | `TP_SDA and TP_SCL` | `I2C_SDA, I2C_SCL` | AB-10 runs over SWD, so these are diagnostic only — but when WHO_AM_I returns nothing there is currently no way to tell a dead accelerometer from a dead bus without a microscope and a hand-held probe on a 0201. | as above; diagnostic |
| 6 | `TP_NFC1 and TP_NFC2` | `NFC1, NFC2` | the coil's tuned resonance is a sample measurement worth having, and C24/C25 are 130 pF each with no way to check the tank without unsoldering something | as above; sample-test use, so a small pad is fine |
| 7 | `two fiducials on the probed side` | `—` | a Ø26.00 mm circle has no datum. Without fiducials the bed-of-nails registers on the routed outline, whose tolerance BB-02 records as CANNOT DETERMINE. This is the request that matters most: without it every other pad is a probability, not a contact. | 1.0 mm copper with a 2.0 mm soldermask opening, as far apart as the outline allows, asymmetric so the board cannot be loaded rotated |
| 8 | `a machine-readable per-unit mark` | `—` | FU-05 compares the printed serial to the programmed one, and constraint C11 requires the serial be printed and easily accessible. Today there is nowhere on the board or in the artwork for it. A laser-mark land or a 2D-code area is a board decision, not a test decision. | flat, non-copper, readable by the vision station, on a surface visible after assembly for the shell mark and before assembly for the board mark |
| 9 | `near-field probe keep-clear over the antenna feed` | `RF_50 / ANT_FEED` | FU-09 asserts the resonant FREQUENCY, which is the assert docs/TOOLS-THAT-LIE.md records as missing when two antenna simulations passed while resonating at 4.0 and 5.8 GHz. A repeatable probe position is what makes the measurement comparable unit to unit. NOT a galvanic tap — a pad on RF_50 would change the thing being measured. | a documented keep-clear area, not a pad; state where the probe sits and let the fixture hold it there |
| 10 | `decision, not a pad: IPC-A-610 acceptance class` | `—` | AB-01's AOI recipe is built from the class's fillet criteria, and halo has never chosen one. Class 2 is the consumer default; Class 3 on a $7 tag would be an odd call. A test engineer should not be the person who picks it. | record it in SPEC §6 so the recipe traces to a decision |

## 7. Sampling, yield and what a failure means

| rule | applies to | why |
|---|---|---|
| **Anything that is a safety requirement is 100 %, regardless of cost.** | FU-03 acoustic output, FU-01 door rotation-alone, AB-10 accelerometer, FU-04 non-owner sound control, AB-11 DULT detection payload | docs/ANTI-STALKING.md §2.1 puts anti-stalking features 'at the same level as the battery door'. A sampling plan on a safety feature is a decision to ship some number of units that lack it. A silent halo with no motion sensor is precisely the device ANTI-STALKING §1 describes and refuses to build. |
| **Anything unique to the individual unit is 100 %.** | AB-03 SoC identity, AB-04 provisioning, AB-11 key match, AB-12 NFC URL, FU-05 serial match | A sample cannot speak for a unit's own serial or its own key. These tests exist precisely because each unit differs. |
| **Anything driven by a tool, a die or a stackup is sampled per lot, because the failure arrives for a whole lot at once.** | BB-02 outline, BB-03 impedance, BB-05 castellations, AB-17 contact force, FU-02 door force and torque, FU-08 door retention, FU-07 adhesive gap | Tool and stackup failures are not random per unit. Testing 100 % of a lot that is uniformly wrong costs the same as testing five and learns nothing more. |
| **Anything destructive is sampled and the sample is scrapped.** | FU-09 antenna return loss | Soldering a pigtail to the antenna feed destroys the unit. |
| **Sample sizes here are engineering judgement, not a statistical plan.** | every sampled row | CANNOT DETERMINE — halo has no AQL, no lot size and no accept/reject numbers, because it has no production volume and no agreed quality level. Settle it by choosing an AQL with the factory and taking the sample sizes from ISO 2859-1. The n = 5 figures in this plan are placeholders that say so. |

| station | on failure | why | when it escalates |
|---|---|---|---|
| Bare board | **SCRAP** | a bare board is the cheapest item in the build and inner-layer copper is not reworkable | three boards from one panel failing BB-01 is a fab process alarm, not three defects |
| Assembled board in its carrier | **REWORK, once** | this is the only station where anything can be fixed. The board is not yet bonded into anything. | a part that fails the same test twice is replaced, not reworked again. A test whose fallout crosses its control limit stops the line and becomes an investigation, because two units failing AB-07 for the same reason is a process, not a coincidence. |
| Sealed unit | **SCRAP or INVESTIGATE** | MECHANICAL §7: the shell is bonded to the carrier over 198 mm² and the same bead is the structural joint and the seal. It does not come apart twice. A sealed unit that fails is either scrapped or sectioned to learn why — never re-bonded and re-tested. | any FU-03 acoustic failure is an immediate stop-and-investigate, not a scrap-and-continue, because the bonded-bender process is the one D11a bet the whole mechanical design on and D17 warns it can crack in a way that passes every visual inspection. |

## 8. What is recorded per unit

**Key:** the SoC's factory INFO.DEVICEID at 0x00FFC304, a 64-bit unique identifier programmed by Nordic (nRF54L datasheet §4.2.4.1.1.2). It exists before halo touches the part and cannot be duplicated by a station error.

- INFO.DEVICEID (the key)
- INFO.PART and INFO.RAM as read
- panel id and board position
- halo serial issued
- product ID
- public-key fingerprint (SHA-256 of the public key — never the private key, never the key material)
- firmware image hash
- every measured value in this plan, with its unit
- every verdict, with the limit it was judged against
- station id, fixture id, operator, UTC timestamp per station
- calibration state of each instrument at the time of the measurement
- carrier lot, shot lot, contact-stamping lot, adhesive lot and cure profile, cell lot, label lot

**Retention.** CANNOT DETERMINE — no retention period has been agreed. Two floors bear on it: DULT §3.16.2's 25-day minimum for owner registry data (which is a different dataset and does not govern manufacturing records), and whatever the factory's own quality system requires. Settle it with the factory and record it here. Note that production records containing no personal data are not GDPR material; the owner registry, if one ever exists, is (research/06 §8.1, constraint C26).

A measured number with no instrument, no operator and no timestamp beside it is an assertion. docs/TOOLS-THAT-LIE.md's first rule is that a pass must name the number it passed on; this record is where that number lives after the unit has left the building.

## 9. What cannot be tested in production

Five things people will expect on this list and will not find, each with the reason: ingress protection (QUAL-01, a 30-minute immersion per unit), drop and battery-door abuse (QUAL-02, destructive), battery life (QUAL-03, it takes a year), loudness in phon (QUAL-04, phon is computed under ISO 532-1 and is not a meter reading), and DULT's behavioural timing (QUAL-06, the separated-state timeout is a random 8–24 hours). None of them is dropped; all five are in the qualification table with the standard they follow. What a production line can honestly do is confirm that a unit matches the units that were qualified — it cannot re-qualify the design on every unit, and a plan that pretends otherwise is the false pass docs/TOOLS-THAT-LIE.md is about.

| id | what | standard | why not on the line | where it stands | sample |
|---|---|---|---|---|---|
| `QUAL-01` | Ingress protection | IEC 60529, IPX7 — immersion at 1 m for 30 min | it is a 30-minute immersion per unit and it wets a product that is then shipped | docs/MECHANICAL.md §7 grades IP67 CANNOT DETERMINE and names this exact test. iFixit's counterexample is the reason not to claim it without the test: Samsung's SmartTag has the thickest adhesive barrier of any tag they opened and carries no IP rating at all. | first article, then per tool change |
| `QUAL-02` | Battery-door abuse tests | 16 CFR part 1263 / ANSI-UL 4200A-2023 — drop, torque and compression with the cell retained; General Certificate of Conformity | destructive, and the standard's regime is a test-lab campaign | docs/MECHANICAL.md §5.3: 'the mechanism PASSES its geometric requirement; the standard's test regime is CANNOT DETERMINE'. research/06 §6.1 and constraint C21 carry the full requirement including the warning text and the GCC. | first article, at an accredited lab |
| `QUAL-03` | Battery life | SPEC §2 F11 — about a year on a CR2032 | it takes a year, or an accelerated discharge that still takes weeks | The line's proxy is AB-07's measured sleep current against the Maxell CR2032's 220 mAh (research/fetched/G-acoustics-cells-and-holders.md). The proxy is honest only if the duty cycle is the shipped one; it says nothing about the cell's behaviour at end of life, which ce-spice models but nobody has measured. | 30 units on a life test, continuously, from the first article onward |
| `QUAL-04` | Loudness in Phon | ISO 532-1:2017 loudness at 25 cm, ≥ 60 Phon | phon is a computed loudness level, not a meter reading, and it needs an ISO 532-1 analyser in a qualified room | THIS IS THE TEST THAT UNLOCKS FU-03. Until a golden unit is measured in phon, the production dB(A) limit has no anchor and FU-03's go/no-go is an open number. DULT §3.13.3, research/06 constraint C8, SPEC §2 F3. | golden units — at least 5, so the golden reading is a mean and not one unit's luck |
| `QUAL-05` | Radio certification | FCC 47 CFR §15.247; RED 2014/53/EU via EN 300 328, EN 301 489-1 and -17, EN 62479, EN IEC 62368-1 | a chamber campaign on a handful of units | research/06 §5.1–5.3 and constraints C16–C18. Note that D14 places the chip BARE rather than using a pre-certified module, because no nRF54L module is both certified and castellated — which means halo owns the intentional-radiator testing that constraint C16 was written to avoid. | 3 units to an accredited lab |
| `QUAL-06` | DULT behavioural timing | draft-ietf-dult-accessory-protocol-00 §3.4.4–3.4.5, §3.5.1, §3.10, §3.13.2.1 Table 17 | the separated-state timeout is a random 8–24 h and the back-off is 6 h. One observation takes days. | The line can verify the mechanisms (AB-11's interval count, FU-04's opcode responses) but not the schedule. Verify the schedule in firmware qualification with the clock accelerated, and then confirm one unit in real time. | 3 units, real time, plus a full accelerated run on every firmware release |
| `QUAL-07` | Temperature range | SPEC §4 — −20 to +60 °C | thermal soak per unit is hours | Note the conflict to resolve: the Maxell CR2032 datasheet gives −20 to +85 °C for the cell, and SPEC §4 gives −20 to +60 °C for the product, transcribed from Apple. Nobody has checked whether the piezo bond, the LSR seal and the adhesive joint hold across that range. | 5 units per corner |
| `QUAL-08` | Electrostatic discharge | IEC 61000-4-2 as invoked by EN 301 489-1 | destructive and slow | CANNOT DETERMINE the levels — this plan does not hold EN 301 489-1 and will not quote its table from memory. Note the specific exposure: MECHANICAL §5.4 records that the stainless door floats at cell potential and is the only exposed conductor on the product. | 3 units |
| `QUAL-09` | Cell transport certification | UN 38.3; UN 3091 / PI 970, cell contained in equipment | it is the cell supplier's certificate, not a measurement on halo | research/06 §6.3 and constraint C23 — ship the cell installed rather than loose, UN 38.3-tested branded cells only. Collect the certificate per cell lot and file it with the traceability record. | per cell lot, documentary |
| `QUAL-10` | Channel Sounding ranging accuracy | SPEC §2 F10 — 6–20 cm line of sight, 30 s update | needs two units, a measured baseline and a room | DECISIONS.md D12 carries the known gap openly: Channel Sounding degrades from 25 cm to 331 cm when channels collide without deterministic scheduling, and a single-antenna device can lose metres to orientation. This is a lab measurement over a range of true distances, not a station check. | 8 units, the same configuration lane H's published study used |
| `QUAL-11` | Adhesive bond integrity | sectioning and a pull test on the shell-to-carrier joint | destructive, and FU-07 admits a visual check on a hidden joint is not evidence | MECHANICAL §7 designs a 198 mm² bond with a 0.15 mm gap; ce-connections grades adhesive strength CANNOT DETERMINE. Section units from each shot lot and measure the actual coverage against the designed area. | 3 units per shot lot, destructive |
| `QUAL-12` | Solder joint reliability | IPC-9701 thermal cycling | hundreds of cycles | Relevant because the board is 0.60 mm and carries a 0.4 mm-pitch QFN-48 with an exposed die pad that the datasheet requires be soldered to ground (pinouts.json ep_note). | first article |

## 10. What could not be sourced — 17 open limits

Each row is a work item, never a question for anyone to answer from memory. A limit we invented would be worse than no limit: the line would run to it, and the number would be wrong.

| what | what would settle it |
|---|---|
| **IPC-9252B continuity and isolation thresholds (BB-01)** | take the values from the fabricator's own ET process sheet, or from a copy of IPC-9252B, and record which |
| **Board outline and thickness tolerance (BB-02)** | write a tolerance into the fabrication drawing, taken from the fab's routing capability |
| **Controlled-impedance tolerance (BB-03)** | state it in the stackup document that lane B1 / T6 owns |
| **Surface finish and its thickness band (BB-04)** | name the finish in the fabrication drawing, then take the band from IPC-4552 |
| **IPC-A-610 acceptance class (AB-01)** | a decision in SPEC §6 — this is a product decision, not a measurement |
| **Sleep current ceiling (AB-07)** | the datasheet has no row for the nRF54L10's 192 KB retention (lane E records the 2.0–3.1 µA bracket explicitly) and no source exists for the GD25LQ32E's deep-power-down current. Characterise 30 first articles and set mean + 3σ. |
| **32.768 kHz and 32 MHz frequency-error limits (AB-05, AB-06)** | for the LFXO, the DULT timer accuracy the firmware actually needs; for the HFXO, the Bluetooth Core Specification Vol 6 Part A §3.1 centre-frequency tolerance. Neither document is in this repo. |
| **GD25LQ32E RDID identification bytes (AB-13)** | the 'Read Identification (RDID) 9Fh' section of the GD25LQ32E datasheet. GigaDevice's URL 404s and LCSC serves an anti-bot HTML page; the only document obtained was the 2023 product selection guide, which has no ID table. |
| **Battery contact resistance limit (AB-16)** | the 1 Ω gate is derived from ce-spice's 8 mA peak and 400 mV droop budget and is deliberately loose. Record 200 units and replace it with mean + 3σ. |
| **Door opening force and torque UPPER bounds (FU-02)** | a usability study, or a published hand-strength percentile. research/06 §6.1 cites the AirTag's door as a documented accessibility failure but the citation carries no number, so there is nothing to copy. |
| **Production acoustic limit in dB(A) (FU-03)** | QUAL-04's ISO 532-1 phon measurement on at least five golden units, plus a gauge R&R study on this hood and this meter. This is the largest gap in the plan and the one that blocks the line. |
| **Absolute finished mass (FU-06)** | weigh 30 first articles. MECHANICAL §10's 7.8 g excludes the board's components and copper, and no populated-board mass exists anywhere in this repo. |
| **Cosmetic standard and seam step (FU-07)** | a boundary-sample set agreed with the factory — a normal first-article deliverable |
| **Antenna |S11| limit (FU-09)** | ce-rf's own assert, once it has solved the antenna on the real board outline with the cell's copper in place (SPEC §5 E4). The FREQUENCY limit is already hard: 2400–2483.5 MHz. |
| **AQL, lot size and accept/reject numbers (sampling policy)** | agree an AQL with the factory and take the sample sizes from ISO 2859-1. Every n = 5 in this plan is a placeholder that says so. |
| **Traceability record retention period** | the factory's quality system, agreed and written down |
| **ESD test levels (QUAL-08)** | EN 301 489-1's table. Not held in this repo and not quoted from memory. |

## 11. Notes the test engineer should read before the first shift

- Stage 2 is the board fitted into its carrier with the three stamped contacts, before the shell is bonded. After the shell goes on, nothing electrical is reachable: the TC2030 pads, the battery pads and every test pad are sealed inside. That is the reason the stage boundary is where it is.
- The board carries NO test points today. Every bed-of-nails point in section 5 that is not already a component pad or a TC2030 pad is a request to lane B1, listed in b1_requests.
- The scanner host must be Linux/BlueZ or an nRF sniffer. macOS is disqualified as a test station and this is measured, not assumed: tools/findmy_scan.py documents that CoreBluetooth substitutes a per-host random UUID for the peripheral address and never hands up the raw AD structure, so on macOS key bytes p[0..5] are unrecoverable and the 0x1E/0xFF framing cannot be checked at all. A macOS station would report 'device seen' and could not tell one unit's advertisement from another's.
- Currents are quoted from the nRF54L15/L10/L05 PRELIMINARY DATASHEET v0.10, doc id 4503_018 v0.10, sections 11.1.2.1 and 11.1.2.3, archived as research/fetched/E-nrf54l-datasheet-currents.md. The datasheet gives typical values only — there is no max column — so every current window in this plan has a sourced floor and a ceiling that is either sourced from a different document or written CANNOT DETERMINE.
- 60 Phon is a loudness level under ISO 532-1:2017. It is NOT dB(A) and the two must never be swapped on a traveller. Production measures dB(A); qualification measures phon; the transfer between them is a golden-unit correlation, and it is listed as an open item, not quietly assumed.

---

*Generated from spec/test-plan.json by tools/gen_test_plan.py. Nothing in this page is hand-typed HTML or hand-typed Markdown. Regenerate with `python3 tools/gen_test_plan.py`. Audience: the partner factory's test engineers, and the ten engineers taking the release pack.*
