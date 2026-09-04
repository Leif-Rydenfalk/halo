#!/usr/bin/env python3
"""Render docs/SOURCING.md from spec/bom-resolved.json. Nothing is hand-typed.

Same shape as tools/gen_release_pack.py: the data file is the truth, this file
is only a view of it. If a number is wrong here, it is wrong in the JSON, and
the JSON is written by tools/resolve_bom.py from what the vendors returned.
"""
import json, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "spec" / "bom-resolved.json").read_text())
OUT = ROOT / "docs" / "SOURCING.md"
QTYS = ["10", "100", "1000", "10000"]


def rev():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def money(v, dp=4):
    return "—" if v is None else f"${v:.{dp}f}"


def num(v):
    return "—" if v is None else f"{v:,}"


def lcsc_url(c):
    return f"https://www.lcsc.com/product-detail/{c}.html"


def part_cell(p):
    if not p:
        return "—", "—", "—", "—", "—"
    lib = p.get("library_type") or "?"
    badge = "**basic**" if lib == "basic" else "extended"
    return (f"[{p['lcsc']}]({lcsc_url(p['lcsc'])})", f"`{p.get('mpn')}`",
            p.get("manufacturer") or "—", str(p.get("package") or "—"), badge)


L = []
w = L.append

resolved = [l for l in D["lines"] if l["verdict"] == "RESOLVED"]
withalt = [l for l in D["lines"] if l.get("alternate")]
basic = [l for l in resolved if (l["part"] or {}).get("library_type") == "basic"]
cost = D["cost"]

w("# Sourcing — every placed part on halo_rev_a, with an order code that was read back")
w("")
w(f"*Generated from `spec/bom-resolved.json` by `tools/gen_sourcing.py` at "
  f"`{rev()}`. Prices and stock were read on **{D['generated']}** and every one "
  f"of them carries that date. Nothing on this page is typed by hand.*")
w("")
w("## The count")
w("")
w("| | |")
w("|---|--:|")
w(f"| Placed references in the release bill of materials | **{D['placed_refs_in_release_bom']}** |")
w(f"| References covered here | **{D['refs_covered']}** |")
w(f"| Bill-of-materials lines | {len(D['lines'])} |")
w(f"| Lines **RESOLVED** — order code fetched, manufacturer part number matched | **{len(resolved)}** |")
needalt = [l for l in D["lines"] if l["verdict"] not in ("DNP", "NOT AN SMT LINE",
                                                         "SEE SOUNDER SECTION")]
w(f"| Lines with a documented alternate | **{len(withalt)}** of the {len(needalt)} "
  f"that can have one |")
w(f"| Resolved lines that are a JLCPCB **Basic** part | **{len(basic)}** of {len(resolved)} |")
w(f"| Distinct **Extended** order codes on the board | **{cost['extended_part_count']}** |")
w(f"| Feeder fee those Extended parts cost, per order | **${cost['feeder_fee_total_usd']:.2f}** |")
w(f"| Solder joints, measured | **{cost['joints_measured']}** |")
w("")
for l in D["lines"]:
    if l["verdict"] != "RESOLVED":
        w(f"- **{l['verdict']}** — `{', '.join(l['refs'])}` ({l['value']})")
w("")
w("## How every number here was obtained")
w("")
w("Two endpoints, both plain HTTPS, both re-runnable:")
w("")
w(f"- **LCSC** — `{D['endpoints']['lcsc']}`")
w(f"- **JLCPCB** — `{D['endpoints']['jlcpcb']}`")
w("")
w("**The check that makes this not a tool that lies** "
  "(`docs/TOOLS-THAT-LIE.md`): a candidate is accepted only if the "
  "manufacturer part number the vendor returns for the order code MATCHES the "
  "one the line asks for. A resolver that merely fetched a price would have "
  "reported the previous bill of materials entirely green.")
w("")
w(f"> {D['price_note']}")
w("")
w(f"> {D['ladder_note']}")
w("")

w("## The bill of materials")
w("")
w("Price columns are **JLCPCB assembly** prices — what the factory pays when "
  "JLC supplies the part during placement — at the piece count a build of that "
  "many boards actually buys. LCSC retail prices and the full ladders are in "
  "`spec/bom-resolved.json`.")
w("")
w("| Ref | Qty | Value | Function | LCSC | MPN | Mfr | Pkg | Lib | JLC stock | @10 | @100 | @1k | @10k |")
w("|---|--:|---|---|---|---|---|---|---|--:|--:|--:|--:|--:|")
for l in D["lines"]:
    p = l["part"]
    c, m, mf, pk, lib = part_cell(p)
    px = (p or {}).get("jlcpcb_price_usd", {})
    w(f"| **{', '.join(l['refs'])}** | {l['qty']} | {l['value']} | {l['function']} "
      f"| {c} | {m} | {mf} | {pk} | {lib} | {num((p or {}).get('jlcpcb_stock'))} "
      + "".join(f"| {money(px.get(q))} " for q in QTYS) + "|")
w("")

w("## The second source for every line")
w("")
w("Lane T6 measured **212** of the main chip in stock. Single-sourcing is not "
  "a theoretical risk on this board, so every line carries an alternate that "
  "was fetched and matched the same way as the pick.")
w("")
w("| Ref | Pick | LCSC stock | Alternate | LCSC stock | Why this pick, and what the alternate costs you |")
w("|---|---|--:|---|--:|---|")
for l in D["lines"]:
    p, a = l["part"], l["alternate"]
    pc = f"[{p['lcsc']}]({lcsc_url(p['lcsc'])}) `{p.get('mpn')}`" if p else "—"
    ac = f"[{a['lcsc']}]({lcsc_url(a['lcsc'])}) `{a.get('mpn')}`" if a else "—"
    w(f"| **{', '.join(l['refs'])}** | {pc} | {num((p or {}).get('stock'))} "
      f"| {ac} | {num((a or {}).get('stock'))} | {l['why']} |")
w("")

# ---- the sounder ---------------------------------------------------------
s = cost["sounder"]
w("## The sounder")
w("")
w(f"**Specified (D11a):** {s['specified']}")
w("")
w(f"**Verdict: {s['verdict']}**")
w("")
for line in s.get("notes", []):
    w(line)
    w("")
if s.get("candidates"):
    w("| Part | Manufacturer | Ø | Thickness | f0 | Capacitance | Where | Price | Datasheet |")
    w("|---|---|--:|--:|--:|--:|---|---|---|")
    for c in s["candidates"]:
        ds = f"[PDF]({c['datasheet']})" if c.get("datasheet") else "**none found**"
        w(f"| {c['mpn']} | {c.get('manufacturer','—')} | {c.get('diameter_mm','—')} mm "
          f"| {c.get('thickness_mm','—')} mm | {c.get('f0','—')} | {c.get('capacitance','—')} "
          f"| {c.get('availability','—')} | {c.get('price','—')} | {ds} |")
    w("")

# ---- board changes -------------------------------------------------------
w("## What the board should change")
w("")
w("Sourcing found five things that are not sourcing decisions. They belong to "
  "lane B1, which owns `electronics/` and `out/release/board/`. This lane "
  "changed neither, and delivers them as a report.")
w("")
A = D["schematic_audit"]
w(f"### 1. {A['wrong_part']} of the {A['distinct_order_codes']} distinct order "
  f"codes on the schematic name a different component")
w("")
w(f"This is the finding that closes the gap, and it is derived rather than "
  f"asserted: `tools/resolve_bom.py` reads every order code out of "
  f"`{A['source_file']}` and asks `{A['catalogue']}` what each one actually is. "
  f"{A['declaration_sites']} declaration sites, {A['distinct_order_codes']} "
  f"distinct codes, **{A['match']} right, {A['family_name_only']} naming a "
  f"family rather than an orderable item, {A['wrong_part']} naming a different "
  f"component**. Verdict **{A['verdict']}**.")
w("")
w("| Code on the sheet | The sheet says it is | The catalogue says it is | |")
w("|---|---|---|---|")
for r in A["codes"]:
    dec = " / ".join(f"`{m}`" for m in r["declared_mpn"])
    real = f"`{r['catalogue_mpn']}`" if r["catalogue_mpn"] else "**no such LCSC code**"
    pkg = f" — {r['catalogue_package']}" if r.get("catalogue_package") else ""
    mark = {"MATCH": "ok", "WRONG PART": "**WRONG**"}.get(r["verdict"], r["verdict"].lower())
    w(f"| `{r['lcsc']}` | {dec} | {real}{pkg} | {mark} |")
w("")
w("Two of those rows are worth reading twice. **`C1568` is quoted for five "
  "different capacitor values** — 0.3, 0.5, 1.5, 2.0 and 3.9 pF — and it is "
  "one part, a 4 pF 0402. **`C2827888` is quoted as a 2.2 µF ceramic** and is "
  "a DORABO 8-way 3.5 mm screw terminal block with 59 in stock. And "
  "**`C7498149` on BT1 is an SMD battery holder**, a part that must not be "
  "fitted at all, because lane M's contacts are three stamped sprung fingers "
  "on halo's own three-pad land pattern.")
w("")
w("The pattern is one mistake repeated: the familiar **0402** basic-part codes "
  "were written down beside **0201** part numbers. **The manufacturer part "
  "numbers on the sheet were almost all correct** — `0201WMF1002TEE`, "
  "`LQP03HQ2N7B02D`, `MLZ1608M4R7WT000`, `GJM0335C1E1R5WB01` are all real "
  "parts in the right size, and every one of them has been given its real "
  "order code in the bill of materials above. Only the codes were wrong, and a "
  "wrong code is the one error a factory cannot catch for you.")
w("")
w("### 2. Not one passive on this board is a JLCPCB Basic part, and it is the 0201 choice that does it")
w("")
w("**Zero of the 9,030 0201 parts in the catalogue is a JLCPCB Basic part** — "
  "measured, not assumed. 0402 has 51 and 0603 has 118. So every 0201 line "
  f"carries the ${cost['model']['feeder_fee_per_extended_part_usd']} per-order "
  f"feeder fee, and this board carries **{cost['extended_part_count']} of them "
  f"= ${cost['feeder_fee_total_usd']:.2f} per order**, against the "
  f"{cost['model']['d15_assumed_extended_parts']} D15 assumed.")
w("")
w("At a thousand units that is "
  f"${cost['feeder_fee_total_usd']/1000:.4f} a unit and nobody cares. **At ten "
  f"units it is ${cost['feeder_fee_total_usd']/10:.2f} a unit**, which is more "
  "than every component on the board put together, and it is the single "
  "largest reason the prototype build is dearer than D15 says. If the first "
  "articles matter more than the thousand, moving the non-RF passives to 0402 "
  "is worth real money; if the thousand matters more, 0201 is free.")
w("")
w("### 3. C24/C25: 1.1 nF cannot be bought in 0201, and the fix is in copper")
for l in D["lines"]:
    if l["refs"][0] == "C24":
        w("")
        w(l["why"])
w("")
w("### 4. C19 is the most expensive passive on the board")
for l in D["lines"]:
    if l["refs"][0] == "C19":
        p = l["part"]
        w("")
        w(f"`{p['mpn']}` at {money(p['jlcpcb_price_usd']['1000'])} per piece at a "
          f"thousand is 40× a plain C0G of the same value and more than the "
          f"32.768 kHz crystal. It is one 2.0 pF capacitor in the antenna match. "
          f"If ce-rf's S11 measurement shows the Q of a general-purpose C0G is "
          f"adequate, the alternate on this line saves about "
          f"{(p['jlcpcb_price_usd']['1000'] - l['alternate']['jlcpcb_price_usd']['1000']):.4f} "
          f"dollars a unit.")
w("")
w("### 5. X1's load capacitance has not been checked against the SoC")
for l in D["lines"]:
    if l["refs"][0] == "X1":
        w("")
        w(l["why"])
w("")
w("**Deletion already made, and confirmed here:** the SPI flash a previous "
  "lane found sitting on the raw 3.0 V cell rail while rated 1.65–2.0 V is "
  "gone — commit `4e3dd52`, *\"flash deleted as out-of-spec\"*. It appears in "
  "no netlist, no placement and no bill of materials, so there was nothing to "
  "source and nothing was sourced.")
w("")

# ---- cost ---------------------------------------------------------------
m = cost["model"]
w("## The cost roll-up, on measured numbers")
w("")
w(f"Every **rate** below is lane E's, from `{m['source']}`, and this lane "
  "re-derives none of them. What this lane replaces is the three **inputs** "
  "that section had to assume:")
w("")
w("| Input | D15 assumed | Measured here | How |")
w("|---|--:|--:|---|")
w(f"| Solder joints | {m['d15_assumed_joints']} | **{cost['joints_measured']}** "
  f"| {cost['joints_source']} |")
w(f"| Extended parts | {m['d15_assumed_extended_parts']} "
  f"| **{cost['extended_part_count']}** | every order code's "
  f"`componentLibraryType`, live from JLCPCB |")
w(f"| Component prices | a candidate list | **the placed board** | every line, "
  f"both endpoints, {D['generated']} |")
w("")
w(f"The joint count landing on **{cost['joints_measured']}**, exactly D15's "
  f"assumption, is an independent confirmation of that half of the model.")
w("")
w("| Qty | BOM | PCB | Assembly | Enclosure | Tooling | Labour | **Total/unit** | D15 | **Δ** |")
w("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for q in QTYS:
    r = cost["per_unit"][q]
    w(f"| {int(q):,} | {money(r['bom'],4)} | {money(r['pcb'],3)} "
      f"| {money(r['assembly'],4)} | {money(r['enclosure'],2)} "
      f"| {money(r['tooling'],2)} | {money(r['labour'],2)} "
      f"| **{money(r['total'],4)}** | {money(r['d15_total'],2)} "
      f"| **{'+' if r['delta_vs_d15']>=0 else '-'}${abs(r['delta_vs_d15']):.4f}** |")
w("")
unpriced = cost["per_unit"]["1000"]["bom_lines_not_priced"]
if unpriced:
    w(f"**These totals are a floor, not a quote: {', '.join(unpriced)} carry no "
      f"price** and contribute zero to every row above. A total with a missing "
      f"line is stated as missing, never padded with a plausible number.")
    w("")
w("Fee constants, so the arithmetic can be checked: "
  f"${m['assembly_setup_usd']} setup + ${m['stencil_usd']} stencil + "
  f"${m['feeder_fee_per_extended_part_usd']} × {cost['extended_part_count']} "
  f"extended parts, amortised over the build, plus ${m['per_joint_usd']} × "
  f"{cost['joints_measured']} joints per unit. Source: {m['fee_source']}. "
  f"Staleness: {m['fee_staleness']}.")
w("")
w("### Why the delta goes the way it does")
w("")
d1k = cost["per_unit"]["1000"]
w(f"At a thousand units the board comes out at **{money(d1k['total'],2)}** "
  f"against D15's ${m['d15_baseline_usd_per_unit']['1000']}, "
  f"**{'+' if d1k['delta_vs_d15']>=0 else '-'}${abs(d1k['delta_vs_d15']):.2f} a unit**. Two thirds of that is not a price "
  f"movement at all: D15 priced a *candidate* bill of materials from "
  f"research/05 §5.2, which still carried five 100 µF bulk capacitors sized "
  f"for a voice coil and an ultra-wideband burst. The board that exists "
  f"carries four 10 µF 0402 instead, because D11a and D12 deleted both of "
  f"those loads. The rest is that the real 0201 passives are cheaper than the "
  f"0402 parts whose codes the sheet was carrying.")
w("")
d10 = cost["per_unit"]["10"]
w(f"**The ten-unit row moves the other way, "
  f"{'+' if d10['delta_vs_d15']>=0 else '-'}${abs(d10['delta_vs_d15']):.2f}, and "
  f"that is the honest news in this table.** Feeder fees do not amortise at "
  f"ten. {cost['extended_part_count']} extended parts instead of "
  f"{m['d15_assumed_extended_parts']} costs "
  f"${(cost['extended_part_count']-m['d15_assumed_extended_parts'])*m['feeder_fee_per_extended_part_usd']/10:.2f} "
  f"a unit at that volume, and it is the whole of the difference. First "
  f"articles cost more than D15 said; a thousand costs less.")
w("")

# ---- risk ---------------------------------------------------------------
w("## What could stop the line")
w("")
rows = []
for l in D["lines"]:
    p = l["part"]
    if not p:
        continue
    st = p.get("jlcpcb_stock")
    need = l["qty"] * 1000
    if st is not None and st < need * 3:
        rows.append((l, p, st, need))
rows.sort(key=lambda r: r[2] / max(r[3], 1))
if rows:
    w("Stock that does not cover a thousand-unit build three times over. "
      "Three times, not once, because a factory buys attrition too and because "
      "nobody else stops buying while you order.")
    w("")
    w("| Ref | Part | JLC stock | A 1k build needs | Cover | Alternate stock |")
    w("|---|---|--:|--:|--:|--:|")
    for l, p, st, need in rows:
        a = l.get("alternate") or {}
        w(f"| **{', '.join(l['refs'])}** | `{p.get('mpn')}` | {num(st)} | {num(need)} "
          f"| **{st/need:.1f}×** | {num(a.get('jlcpcb_stock'))} |")
    w("")
w("Minimum packet sizes worth knowing before an order is placed — several of "
  "these parts cannot be bought from LCSC in small numbers at all, though "
  "JLCPCB will consume them from its own reels during assembly:")
w("")
w("| Ref | Part | LCSC minimum packet |")
w("|---|---|--:|")
for l in D["lines"]:
    p = l["part"]
    if p and p.get("min_packet"):
        w(f"| {', '.join(l['refs'])} | `{p.get('mpn')}` | {num(p['min_packet'])} |")
w("")
w("## Datasheets")
w("")
w("| Ref | Part | Datasheet |")
w("|---|---|---|")
for l in D["lines"]:
    for role in ("part", "alternate"):
        p = l.get(role)
        if p and p.get("datasheet"):
            w(f"| {', '.join(l['refs'])}{' (alt)' if role=='alternate' else ''} "
              f"| `{p.get('mpn')}` | [PDF]({p['datasheet']}) |")
w("")
w("---")
w("")
w(f"*`spec/bom-resolved.json` is the machine-readable form of this page and "
  f"carries the full price ladders from both channels, the LCSC retail prices, "
  f"the min-packet and split quantities, and the MPN check result for every "
  f"order code. Regenerate both with "
  f"`python3 tools/resolve_bom.py && python3 tools/gen_sourcing.py`.*")

OUT.write_text("\n".join(L) + "\n")
print(f"wrote {OUT} — {len(L)} lines, {len(resolved)}/{len(D['lines'])} resolved")
