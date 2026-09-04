# Sourcing alternates — the lines halo_rev_a cannot buy at 1,000 and 10,000

*Lane S2 (availability). Every stock and price figure on this page was read **live on 2026-09-05**
from a named endpoint at a named second, not recalled and not taken from a catalogue snapshot.
The probe is `livestock.py` (below); its raw output is `out/verify/alternates-live-2026-09-05.json`.*

**This lane proposes. It does not apply.** `electronics/halo_rev_a/schematic.py`,
`out/release/board/` and `spec/bom-resolved.json` belong to the board and halo lanes. A change that
lands only in a resolved file is not landed: the 2026-09-04 fix wrote corrected order codes into
`spec/bom-resolved.json` but not onto the sheet, and the next regeneration exported the old wrong
codes again. **Whatever is adopted here has to land on `schematic.py`.**

---

## 0 · Read this first: the FAIL in the record is not the FAIL on the board

The failures this lane was spawned to close — `C1046539` at 0 stock and `C2827888` at 59 against a
need of 100 — **were never availability failures.** They were an identity defect, and the board lane
had already fixed it before this lane started.

| code in the 09-04 transcript | sat on | what that order code actually is |
|---|---|---|
| `C2827888` | C5, C6, C7, C8 — capacitor pads | `DB2EK-3.5-8P-BK-S`, an **8-pin 3.5 mm pitch screw terminal block** |
| `C1046539` | L2, L3, L4 — 0201 inductor pads | `SIT3372AC-1E2-33NZ133.650000X`, a **SiTime 133.65 MHz MEMS oscillator** |

`out/release/board/halo_rev_a-BOM.csv` was regenerated **2026-09-05 06:06** with correct codes
(`C335106`, `C7216765`, `C3911055` …). Both parts are now deeply stocked and both lines PASS at every
quantity. **Row 3's FAIL text should be superseded, not re-measured**, and no alternate should be
sought for either code. Chasing them would have been an hour spent finding a second source for a
screw terminal block.

---

## 1 · The tool that graded this was reading two-day-old stock

`ce-fab/bin/fab bom cost --live` **fetches live only for the lines the catalogue snapshot could not
match.** Every line the snapshot *did* match is graded on `stock as of 2026-09-03` — the per-line
prose says so, honestly, but **the PASS/FAIL verdict does not**, and the verdict is what people read.

Re-probing all 23 picks live moved four verdicts:

| line | code | snapshot 2026-09-03 | **live 2026-09-05** | move |
|---|---|--:|--:|---|
| C19 | `C668326` | 5,874 | **29,352** | FAIL → **PASS** (+400 %) |
| X2 | `C843260` | 6,665 | **13,596** | FAIL → **PASS** (+104 %) |
| L3, L4 | `C3911055` | 18,376 | **8,441** | **−54 % in two days** |
| U1 | `C44800139` | 212 | **927** | FAIL → FAIL |

and two candidate reads moved even harder: `C423341` read **29,417 live against 1,167 in the
snapshot — a 25× understatement**, and `C237447` read **7,693 live against 36,092 — a 79 % collapse**.

**Consequence for anyone reading this page:** two of the six lines the 09-04 run reported as
unbuyable at 10,000 are buyable today, and one it waved through has halved. Filed in
`docs/TOOLS-THAT-LIE.md`; the fix belongs in `ce-fab`, not in a warning.

---

## 2 · What actually fails, live, 2026-09-05

| build | verdict | lines failing on stock |
|---|---|---|
| **10 boards** | **PASS** | none |
| **100 boards** | **PASS** | none |
| **1,000 boards** | **FAIL** | **U1** only |
| **10,000 boards** | **FAIL** | **U1**, **L3/L4**, **R1/R2**, **C20/C21** |

Needs include JLCPCB's stated setup attrition, as `fab bom cost` computes them. Stock is JLCPCB
assembly stock — the channel that matters for a PCBA order — cross-checked against LCSC retail.

---

## 3 · The four lines, one row each

### C20, C21 — 0.5 pF pi shunts — **PASS with a stated dependency**

| | fitted | **proposed alternate** |
|---|---|---|
| LCSC | [C237424](https://www.lcsc.com/product-detail/C237424.html) | **[C85922](https://www.lcsc.com/product-detail/C85922.html)** |
| MPN | `GJM0335C1HR50WB01D` | `GRM0335C1HR50WA01D` |
| Manufacturer | Murata | Murata |
| Capacitance | 0.5 pF | **0.5 pF** |
| Tolerance | ±0.05 pF (`W`) | **±0.05 pF (`W`)** |
| Voltage | 50 V | **50 V** |
| Dielectric | C0G | **C0G** |
| Package / land pattern | 0201 / `C_0201_0603Metric` | **0201 / same land pattern** |
| Series | GJM03 — high-Q RF | GRM03 — general-purpose C0G |
| **JLC stock, live** | **13,101** | **135,053** |
| LCSC stock, live | 13,100 | 132,300 |
| JLC unit @1k / @10k | $0.0181 / $0.0165 | **$0.0053 / $0.0047** |
| Need @10,000 boards | 20,004 | 20,004 |
| **Verdict** | **FAIL** — short 6,903 | **PASS** — 6.75× cover, and **72 % cheaper** |

**Why it is qualified:** identical value, identical tolerance code, identical voltage, identical
dielectric, identical 0201 body, same manufacturer, same land pattern. The single parameter that
differs is **Q**: GJM03 is Murata's high-Q RF series, GRM03 is the general-purpose C0G. In a 2.4 GHz
shunt leg that shows up as insertion loss, not as a wrong value.

**The dependency, stated rather than hidden:** `schematic.py:497` says of this pi — *"ALL THREE ARE
PLACEHOLDERS: the values below are a starting guess for a slightly-inductive feed, and they are what
ce-rf's measured S11 replaces."* **You cannot commit 20,000 pieces of a value that has not been
chosen.** So this row is not closed by a part; it is closed by ce-rf's S11 fixing the value, after
which the GRM part is the deep-stock answer for whatever value that is.

**What would settle it:** ce-rf's S11 on the real copper, then one sweep re-run with GRM03's Q
instead of GJM03's. If the match holds, adopt C85922 and the line gains 10× stock and gets cheaper.

**A supply fact that outlives this row:** the GJM03 high-Q family is systematically thin in 0201 —
this board's five GJM parts read 5,994 / 13,101 / 13,804 / 24,048 / 29,352 live. **If ce-rf's final pi
wants high-Q parts, 10,000 boards is a family-wide supply constraint, not a one-part problem.**

---

### R1, R2 — 4.7 MΩ cell-removal sense divider — **PASS on stock, CANNOT DETERMINE on tolerance**

| | fitted | **proposed alternate** | value-change route |
|---|---|---|---|
| LCSC | [C778408](https://www.lcsc.com/product-detail/C778408.html) | **[C423341](https://www.lcsc.com/product-detail/C423341.html)** | [C423797](https://www.lcsc.com/product-detail/C423797.html) |
| MPN | `0201WMF4704TEE` | `0201WMJ0475TEE` | `0201WMF1005TEE` |
| Manufacturer | UNI-ROYAL | **UNI-ROYAL** | UNI-ROYAL |
| Resistance | 4.7 MΩ | **4.7 MΩ** | 10 MΩ |
| **Tolerance** | **±1 % (`F`)** | **±5 % (`J`)** | **±1 % (`F`)** |
| Temp coefficient | ±200 ppm/°C | **±200 ppm/°C** | ±200 ppm/°C |
| Rating | 50 mW / 25 V | **50 mW / 25 V** | 50 mW / 25 V |
| Package / land pattern | 0201 / `R_0201_0603Metric` | **0201 / same** | 0201 / same |
| **JLC stock, live** | **10,142** | **29,417** | 13,937 |
| JLC unit @1k / @10k | $0.0015 / $0.0013 | **$0.0008 / $0.0007** | $0.0016 / $0.0013 |
| Need @10,000 boards | 20,010 | 20,010 | 20,010 |
| **Verdict** | **FAIL** — short 9,868 | **PASS on stock** — 1.47× cover, **46 % cheaper** | **FAIL** — short 6,073 |

**Mechanically qualified:** same 0201 body, same land pattern, same manufacturer, same series, same
power and voltage rating, same tempco. Nothing about the board changes.

**Electrically — this is the honest part.** Dropping ±1 % → ±5 % widens the divider ratio worst case
from **±1.0 % to ±5.0 %**, which on a 3.0 V cell is **±150 mV instead of ±30 mV** on the reported
battery voltage.

- For the divider's **primary job it does not matter at all.** `schematic.py:843` — *"BT1 pad 3 is
  SENSE ONLY through R1/R2 into AIN0 … Pull the cell and VBAT_SNS collapses in ~0.24 ms."* Cell
  removal is a collapse to zero, not a threshold with 5 % of headroom at stake.
- For the **idle-current argument it does not matter either**: 3 V / 9.4 MΩ = 0.32 µA while the GPIO
  is driven, and tolerance moves that by ±5 % of a third of a microamp.
- For **reported battery level, no requirement exists to check it against.** SPEC.md F11 says *"about
  a year on a CR2032"* and states no gauge accuracy anywhere. **This is a CANNOT DETERMINE, and it is
  recorded as one rather than resolved by assuming ±150 mV is fine.**

**What would settle it:** one line in SPEC.md giving the battery-level accuracy the product owes, or
the firmware lane naming the bucket boundaries it reports. If levels are coarse buckets — the
AirTag-class norm — ±150 mV is comfortably inside and C423341 closes this row outright, cheaper.

**Why the 10 MΩ value-change route is recorded but not recommended.** It keeps ±1 % and it *halves*
the sense current to 150 nA, but: **no single 10 MΩ ±1 % 0201 covers 20,010 either** (13,937 UNI-ROYAL
+ 8,002 YAGEO `C469663`, two manufacturers, to reach 21,939), and it doubles the ADC source impedance
2.35 MΩ → 5 MΩ and the collapse time 0.24 ms → 0.50 ms, both of which are measured numbers on the
sheet today. It trades a tolerance question for two re-measurements. **Recorded so nobody re-derives
it; not proposed.**

**There is no third ±1 % source at 4.7 MΩ.** `C474424` (YAGEO `RC0201FR-074M7L`) reads **5 pieces**
live and 0 at LCSC. The ±5 % field beyond C423341 is `C158489` RALEC at 1,052 and `C171972` Walsin at
489 — neither is a supply. **This line has ONE manufacturer whichever tolerance is chosen.**

---

### L3, L4 — 3.5 nH match inductors — **NO QUALIFIED IN-STOCK ALTERNATE AT 10,000. This is a real finding.**

The recorded alternate does not cover it, **and neither does anything else at this value.** The
whole live band, every 0201 inductor from 3.3 nH to 4.3 nH, read 2026-09-05:

| LCSC | MPN | value | series / Q @500 MHz | DCR | **JLC stock, live** | @10k unit | covers 20,004? |
|---|---|--:|---|--:|--:|--:|---|
| [C3911055](https://www.lcsc.com/product-detail/C3911055.html) | `LQP03HQ3N5B02D` | **3.5 nH — fitted** | HQ / **20** | 170 mΩ | **8,441** | $0.0280 | **no** |
| [C206424](https://www.lcsc.com/product-detail/C206424.html) | `LQP03TN3N5B02D` | 3.5 nH — *recorded alternate* | TN / 14 | — | **9,348** | $0.0100 | **no** |
| [C237447](https://www.lcsc.com/product-detail/C237447.html) | `LQP03HQ3N6B02D` | 3.6 nH | HQ / **20** | 170 mΩ | 7,693 | $0.0207 | no |
| [C237380](https://www.lcsc.com/product-detail/C237380.html) | `LQP03HQ3N3B02D` | 3.3 nH | HQ / **20** | 170 mΩ | 14,462 | $0.0270 | no |
| [C337939](https://www.lcsc.com/product-detail/C337939.html) | `LQP03HQ3N9B02D` | 3.9 nH | HQ / **20** | 170 mΩ | 10,385 | $0.0243 | no |
| [C2041526](https://www.lcsc.com/product-detail/C2041526.html) | `LQP03HQ4N0B02D` | 4.0 nH | HQ / **20** | 170 mΩ | 13,906 | $0.0278 | no |
| [C2988753](https://www.lcsc.com/product-detail/C2988753.html) | `LQP03HQ4N3H02D` | 4.3 nH | HQ / **20** | 170 mΩ | 36,962 | $0.0220 | yes — but +23 % value |
| [C275212](https://www.lcsc.com/product-detail/C275212.html) | `MLG0603P3N6BTZ10` | 3.6 nH | TDK / 18 | 200 mΩ | 12,496 | $0.0055 | no |
| [C76756](https://www.lcsc.com/product-detail/C76756.html) | `MLG0603P3N9BTZ10` | 3.9 nH | TDK / 14 | 220 mΩ | 17,862 | $0.0018 | no |
| [C77115](https://www.lcsc.com/product-detail/C77115.html) | `LQP03TN3N9B02D` | 3.9 nH | TN / 14 | 300 mΩ | 49,208 | $0.0155 | yes — but Q 14 and +11 % |
| **[C98045](https://www.lcsc.com/product-detail/C98045.html)** | **`LQP03TN3N3B02D`** | **3.3 nH** | **TN / 14** | 250 mΩ | **135,099** | **$0.0118** | **yes — 6.8× cover** |

*Q, DCR and current figures are JLCPCB's own catalogue description text, not the Murata datasheet.*

**Three facts that decide this line:**

1. **At 3.5 nH there is no answer, and there is not even a two-code answer.** Both order codes in
   existence total **8,441 + 9,348 = 17,789**, short of 20,004. Splitting the line across both
   manufacturers' codes still FAILS.
2. **LCSC cannot sell one reel of the fitted part today.** `C3911055`'s minimum purchase packet is
   **15,000** against **8,040** in stock. The line is below one reel, not merely below the build.
3. **The high-Q family is thin everywhere near this value.** Every LQP03**HQ** part from 3.3 to 4.0 nH
   reads between 7,693 and 14,462. Only 4.3 nH breaks 20,000, and that is a 23 % value change.

**What this forces, stated so it can be decided in a minute rather than researched again:**

| route | part | live stock | what it costs |
|---|---|--:|---|
| **A · keep 3.5 nH** | `C3911055` | 8,441 | **caps the build at ~4,200 boards.** No alternate exists. |
| **B · move to 3.3 nH, keep Q=20** | `C237380` | 14,462 | still **FAILS** 20,004 — buys ~7,200 boards |
| **C · move to 3.3 nH, accept Q=14** | **`C98045`** | **135,099** | **the only deep answer.** −6 % value, Q 20→14, DCR 170→250 mΩ, **−58 % unit cost** |
| **D · move to 4.3 nH, keep Q=20** | `C2988753` | 36,962 | +23 % value — a different match, not a substitution |

**Verdict: FAIL at 10,000, with no qualified same-value alternate.** Route C is the only one with
real depth and it is **not a sourcing pick** — L3/L4 are Nordic's reference-network values
(`schematic.py:454`, tolerance ±0.1 nH), so changing them is ce-rf's and the board lane's call, not
this lane's. **At 1,000 boards every route passes and nothing needs deciding.**

**What would settle it:** ce-rf sweeps S11 at 3.3 nH with Q=14 instead of 3.5 nH with Q=20. If the
match holds, `C98045` closes the line with 6.8× cover at 58 % less cost and the risk disappears
permanently. If it does not, halo cannot build 10,000 boards on this match network.

---

### U1 — nRF54L10 — **FAIL at 1,000 and at 10,000. The catalogue has no answer at all.**

| LCSC | MPN | package | JLC stock, live | LCSC stock, live | min packet | @1k / @10k |
|---|---|---|--:|--:|--:|---|
| [C44800139](https://www.lcsc.com/product-detail/C44800139.html) | `NRF54L10-QFAA-R7` — **fitted** | VFQFN-48 | **927** | 671 | 1,000 | $2.3800 / $2.3800 |
| [C45022043](https://www.lcsc.com/product-detail/C45022043.html) | `NRF54L10-QFAA-R` — same die, different reel | VFQFN-48 | **0** | **0** | 3,000 | $3.4928 |
| [C45022042](https://www.lcsc.com/product-detail/C45022042.html) | `NRF54L05-QFAA-R` — **a different SoC** | VFQFN-48 | 1,775 | 1,775 | 3,000 | $2.0112 |

**Those three rows are the entire nRF54L presence in the JLCPCB and LCSC catalogues.** A keyword
sweep of `NRF54%` returns nothing else.

- **At 1,000 boards it is short by 73 pieces**, and the minimum purchase packet is exactly 1,000 —
  so LCSC cannot even sell one packet today.
- **At 10,000 it is short by 9,073.**
- `NRF54L05-QFAA-R` is **not a drop-in**: 512 kB flash / 96 kB RAM against the L10's 1 MB / 256 kB.
  It is pin-compatible in the same QFAA package, so it is a *build* second source, but adopting it is
  a firmware and memory-budget decision. **It also still misses 10,000 by 8,225.** DECISIONS.md D18
  already records that the L05 fallback is not forced by memory; the firmware measures 13,164 bytes.

**Verdict in this channel: FAIL at both quantities.** There is no qualified in-stock alternate at
LCSC or JLCPCB — 927 pieces, three order codes, and one of them is a different SoC.

**Verdict overall: PASS, through an authorized distributor — see §4.** 14,956 pieces are on hand
across authorized channels today and Future Electronics quotes 16 weeks at **$1.8900**, which is
**21 % below what JLCPCB itself charges**. The real content of this row is not scarcity, it is that
**JLCPCB cannot be the supplier**: U1 becomes a consigned part above ~900 boards. §4a puts the three
options side by side with a number on each.

---

## 4 · U1 through authorized channels — **the blocker dissolves into a scheduling fact**

*Read 2026-09-05T07:40Z from `https://www.oemstrade.com/search/NRF54L10-QFAA-R7` and
`.../NRF54L10-QFAA-R` (Supplyframe's aggregator, which labels each distributor's ECIA / authorized
status on the row). **Public stock pages only.** No distributor was contacted, no account opened, no
quote requested, nothing ordered. Nordic's own ordering-information page returned **HTTP 403** and is
recorded below as the one thing that could not be read.*

### On hand today, authorized channels only

| distributor | status | `-QFAA-R7` (fitted) | `-QFAA-R` (see note) | @1,000 |
|---|---|--:|--:|--:|
| Mouser | ECIA member · Authorized | **813** | **8,034** | $2.75 / $2.59 |
| DigiKey | ECIA member · Authorized | **754** | **1,649** | $2.6907 (T&R @3,000 $2.5356) |
| Newark / Farnell | ECIA member · Authorized | **423** *(one pool, two storefronts — counted once)* | **1,683** | $2.48 / $2.34 |
| Verical | Authorized | **1,000** (Americas) | — | $3.3960 |
| Rutronik | — | **600** (DE; HK 0, US 0, SG 0) | — | €2.0800 |
| TME | ECIA member · Authorized | **0** | — | — |
| **Authorized on hand** | | **3,590** | **11,366** | **14,956 combined** |

**Future Electronics** (ECIA member · Authorized) holds none on the shelf and instead quotes the
thing that actually decides this: **min qty 3,000, package multiple 3,000, lead time 16 weeks, full
reel, $1.8900.** That is **the cheapest price anywhere for this part — 21 % below the $2.3800
JLCPCB charges** to supply it during assembly.

Not counted, recorded so nobody counts them: Sierra IC **9,016** ("OEM/CM ONLY"), Win Source
**8,580**, Axis Part **1,100**, Quest **800**, Unikey **401**. None is an authorized channel, and
D20's piezo finding on this project is the precedent — broker stock of a part with no traceability
is not a supply.

### The `-R` / `-R7` question, stated as evidence rather than as fact

`NRF54L10-QFAA-R` is **where nearly all the stock is** (11,366 against 3,590), so whether it is the
same device matters more than any other number on this page. The evidence that it is the same die in
a different tape-and-reel quantity:

- Mouser lists both under the **identical description** — *"Wireless SOC, ultra low power 2.4 GHz
  radio + MCU, 1.0MB NVM"* — at the identical 1-off price of $4.0800.
- Newark carries both under the identical description with **consecutive house numbers**, `26AM1598`
  (`-R`) and `26AM1599` (`-R7`), which is how a distributor numbers two packaging options of one item.
- DigiKey's reel SKUs differ only in **minimum quantity**: `-R7TR-ND` min **1,000**, `-RTR-ND` min
  **3,000**. Future quotes the same split — package multiple 1,000 for `-R7`, 3,000 for `-R`.
- LCSC's own page lists `NRF54L10-QFAA-R` as an **associated part** of `-R7`, and stocks it as
  `C45022043` in the same VFQFN-48.

**What could not be read:** Nordic's ordering-information table
(`docs.nordicsemi.com/bundle/ps_nrf54L15/…/ordering_info.html`) returned **HTTP 403, 5,925 bytes**.
So this is four distributors agreeing, **not the manufacturer confirming**. **The board lane should
read the suffix off Nordic's datasheet before committing a reel.** If `-R` is a different device the
authorized number drops from 14,956 to 3,590 and the 10,000 answer changes.

### Verdict

| build | route | **verdict** |
|---|---|---|
| **1,000** | Mouser holds 8,034 (`-R`) — or 3,590 across five authorized distributors on `-R7` alone | **PASS** |
| **10,000** | 14,956 authorized on hand today, or Future at 16 weeks for $1.8900 | **PASS** |

**U1 is not a design blocker and it is not a money problem. It is a purchasing-channel fact:**

> **JLCPCB cannot supply this part.** It holds **927**. Every route that builds more than ~900
> boards makes U1 a **CONSIGNED** part — halo buys the reels from an authorized distributor and
> ships them to the assembler.

That is the whole decision, and it comes with a discount rather than a premium.

### What this means for the other three rows

Once U1 is consigned, the same door is open for **L3/L4**, whose 3.5 nH has no answer inside
LCSC/JLCPCB at 20,004 pieces. **This lane has not checked authorized-distributor stock for
`LQP03HQ3N5B02D`.** If Digi-Key or Mouser hold 20,000, route A in §3 survives and no value change is
needed. **That is the next measurement, and it is worth taking before anyone re-tunes a match
network.**

---

## 4a · The one thing for Leif, with a number on every option

The three options, at 10,000 boards, U1 only:

| option | cost of 10,000 U1 | when | what it costs you |
|---|--:|---|---|
| **A · consign from Future** | **$18,900** ($1.89) | **16 weeks** | Cheapest by a distance — **$4,900 less than JLCPCB's own price**. You wait 16 weeks and you carry the reels. |
| **B · consign from stock now** | ~$25,400 ($2.5356, DigiKey T&R) | **now** | +$6,500 against A. Needs 14,956 across ~4 distributors, so several POs and mixed date codes. |
| **C · nRF54L05 instead** | $20,112 ($2.0112) | now, **but only 1,775 in stock** | **Does not solve 10,000** — short by 8,225. And it is a different SoC: 512 kB / 96 kB against 1 MB / 256 kB. DECISIONS.md D18 already says the L05 fallback is not forced by memory, and firmware measures 13,164 bytes, so it would fit — but it is a firmware and memory-budget decision, not a substitution. |
| **D · do nothing** | — | — | JLCPCB supplies 927. **The build ceiling is ~900 boards.** |

**A and B both close the row. C does not.** The only genuine product question is A versus B —
16 weeks against $6,500 — and that is a schedule-versus-cash call that belongs to whoever owns the
launch date, not to this lane.

---

## 5 · How every number here was read

```
GET  https://www.lcsc.com/product-detail/<code>.html         -> __NEXT_DATA__ JSON blob
POST https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList
     {"currentPage":1,"pageSize":5,"keyword":"<code>"}
```

Both parsers are `tools/resolve_bom.py`'s `lcsc()` and `jlc()`, reused unchanged so the identity
guard is the same one the halo lane already broke on purpose: **a product node is accepted only if
its own `productCode` equals the code asked for**, because the LCSC page carries recommended and
recently-viewed products beside the one requested and a first-match walk returns the wrong part with
a straight face.

The probe forces a fresh fetch every run by pointing `HALO_SRC_CACHE` at a per-run directory —
`resolve_bom.py` caches to `/tmp/halo-sourcing` and will happily re-serve a stale page otherwise.
**A cached stock figure is the exact failure this page exists to correct.** Every request is bounded
at `--max-time 90`; this machine's outbound path is intermittent and a hang is the expected case, not
an exotic one. One JLCPCB read failed mid-run with `LibreSSL SSL_ERROR_SYSCALL` and was retried
rather than recorded as a zero — **a failed read is CANNOT DETERMINE, never 0 in stock.**

Raw results, one record per code with its endpoint and read timestamp:
`out/verify/alternates-live-2026-09-05.json`.
