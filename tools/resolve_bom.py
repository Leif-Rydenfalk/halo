#!/usr/bin/env python3
"""Resolve every placed part on halo_rev_a to a VERIFIED LCSC order code.

Writes spec/bom-resolved.json. Nothing in that file is typed by hand: the
manufacturer part number, package, stock, price ladder, library type and
datasheet URL are all READ BACK from the two vendor endpoints, on the day the
tool runs, and the date is written beside every number.

What IS hand-authored here is the CHOICE - which part answers which line, and
why - because that is engineering judgement and it carries its reason in
`why`. Everything else is measured.

Two endpoints, both plain HTTPS, both proven by lane E:
  LCSC   GET  lcsc.com/product-detail/<code>.html  -> the __NEXT_DATA__ blob
  JLCPCB POST jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/
              selectSmtComponentList                -> componentLibraryType

THE CHECK THAT MAKES THIS NOT A TOOL THAT LIES (docs/TOOLS-THAT-LIE.md):
a candidate is only accepted if the MPN the vendor returns for the order code
MATCHES the MPN this file claims. A code whose MPN does not match is written
out as a MISMATCH and the line is CANNOT DETERMINE - it is never quietly kept.
That check is what caught halo_rev_a's original bill of materials, in which 16
of 19 order codes named a different part from the one the schematic wanted.
"""
import json, os, pathlib, re, subprocess, sys, csv, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "spec" / "bom-resolved.json"
BOMCSV = ROOT / "out" / "release" / "board" / "halo_rev_a-BOM.csv"
CACHE = pathlib.Path(os.environ.get("HALO_SRC_CACHE", "/tmp/halo-sourcing"))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
JLC_URL = ("https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/"
           "smtGood/selectSmtComponentList")
TODAY = datetime.date.today().isoformat()
LADDER_QTYS = [10, 100, 1000, 10000]

# --------------------------------------------------------------------------
# The choices. `pick` and `alt` are order codes; `mpn` is what the vendor MUST
# come back with, or the line fails. `why` is why this part and not another.
# --------------------------------------------------------------------------
CHOICES = [
 dict(refs="C1,C2,C3,C4", value="100nF", fp="0201", function="SoC supply decoupling, one per VDD pin",
      pick="C5142565", pick_mpn="TCC0201X5R104K100ZT", alt="C190183", alt_mpn="CC0201KRX5R6BB104",
      why="Deepest 0201 100nF stock in the catalogue and the cheapest. 10 V X5R "
          "against a 3.0 V cell leaves margin for X5R DC-bias derating."),
 dict(refs="C5,C8", value="2.2uF", fp="0201", function="SoC DEC/DCDC reservoir",
      pick="C335106", pick_mpn="GRM033R61A225KE47D", alt="C318539", alt_mpn="CL03A225MP3CRNC",
      why="10 V X5R at 2.2 uF in 0201 is a stretched dielectric; the Murata part "
          "is the deepest-stocked one and Murata publishes its DC-bias curve."),
 dict(refs="C6", value="10nF", fp="0201", function="SoC decoupling",
      pick="C76941", pick_mpn="GRM033R71A103KA01D", alt="C285200", alt_mpn="0201X103K100NT",
      why="X7R rather than X5R at no cost premium; 330k stock."),
 dict(refs="C7", value="2.2nF", fp="0201", function="SoC decoupling",
      pick="C161479", pick_mpn="GRM033R71A222KA01D", alt="C2184294", alt_mpn="GCM033R71A222KA03D",
      why="THE SNAPSHOT'S FIRST CHOICE WAS WRONG BY A DAY. YAGEO C526940 held "
          "29,573 in the 2026-09-03 catalogue snapshot and 600 when the live "
          "page was read on 2026-09-04 - a 49x collapse overnight. Both parts "
          "here are Murata, which is a real weakness in this line: it has two "
          "order codes and one manufacturer."),
 dict(refs="C9,C10,C11,C12", value="10uF", fp="0402", function="bulk rail capacitance (4 x 10 uF replaces Apple's 5 x 100 uF)",
      pick="C15525", pick_mpn="CL05A106MQ5NUNC", alt="C7472949", alt_mpn="HGC0402R5106M100NTEJ",
      why="THE ONLY JLCPCB BASIC PART ON THIS BOARD. No feeder fee, ~10 M in "
          "stock. 6.3 V X5R at 3.0 V is inside spec but derates hard - the "
          "10 V alternate is there if the measured rail droop needs it."),
 dict(refs="C13", value="100pF", fp="0201", function="battery-sense divider settling cap",
      pick="C76922", pick_mpn="GRM0335C1H101JA01D", alt="C272870", alt_mpn="CC0201JRNPO9BN101",
      why="C0G, so the ADC settling time and the 0.24 ms cell-removal collapse "
          "do not move with temperature. Deepest line on the board: 826 k and "
          "1.2 M, two manufacturers."),
 dict(refs="C18", value="1.5pF", fp="0201", function="2.4 GHz match, Nordic reference network",
      pick="C435397", pick_mpn="GJM0335C1E1R5WB01D", alt="C88913", alt_mpn="GRM0335C1H1R5WA01D",
      why="Murata GJM03 is the high-Q RF series the Nordic reference network "
          "assumes; a general-purpose C0G would lower the match Q. The GRM "
          "alternate is that general-purpose C0G, 5x cheaper and deeper "
          "stocked - acceptable only once ce-rf has measured S11 with it."),
 dict(refs="C19", value="2.0pF", fp="0201", function="2.4 GHz match, Nordic reference network",
      pick="C668326", pick_mpn="GJM0335C1E2R0WB01D", alt="C577359", alt_mpn="CQ0201BRNPO8BN2R0",
      why="Same GJM03 high-Q family as C18. THE MOST EXPENSIVE PASSIVE ON THE "
          "BOARD at $0.064/1k - 40x a plain C0G - because 2.0 pF in the GJM "
          "high-Q series is a thin line. The YAGEO CQ series alternate is the "
          "deepest non-Murata 2 pF that survived the live stock check; the "
          "snapshot's two better-looking candidates (C161383, C1855389) read "
          "200 and ZERO on the live page."),
 dict(refs="C20,C21", value="0.5pF", fp="0201", function="antenna tuning pi, shunt legs (values are placeholders until ce-rf's S11)",
      pick="C237424", pick_mpn="GJM0335C1HR50WB01D", alt="C85922", alt_mpn="GRM0335C1HR50WA01D",
      why="THE SCHEMATIC ASKED FOR GJM0335C1ER50WB01 (25 V), which is C464955 "
          "with 329 pieces in stock - not orderable. The 50 V 1H variant is "
          "the same 0.5 pF part with 25x the stock."),
 dict(refs="C22", value="0.3pF", fp="0201", function="2.4 GHz match, series trim into the pi",
      pick="C3904589", pick_mpn="GJM0335C1HR30WB01D", alt="C723329", alt_mpn="0201CG0R3B500NT",
      why="GJM03 high-Q, 50 V. At 0.3 pF the parasitics of a cheap C0G are a "
          "large fraction of the value, so the RF series earns its price here."),
 dict(refs="C23", value="3.9pF", fp="0201", function="2.4 GHz shunt at ANT (Nordic Table 82; node placement CANNOT DETERMINE)",
      pick="C1852416", pick_mpn="GJM0335C1E3R9WB01D", alt="C285100", alt_mpn="0201CG3R9C250NT",
      why="GJM03 high-Q. Alternate is 28x cheaper and adequate if this ends up "
          "being a DNP once ce-rf measures the real feed."),
 dict(refs="C24,C25", value="1.1nF", fp="0201", function="NFC antenna tuning, series pair across the coil - MUST BE MATCHED TO EACH OTHER",
      pick=None, pick_mpn=None, alt="C161371", alt_mpn="GRM0335C1E102JA01D",
      verdict="CANNOT DETERMINE",
      why="NO 1.1 nF CAPACITOR EXISTS IN 0201 IN ANY DIELECTRIC, and none "
          "exists in 0402 either - the smallest 1.1 nF in the whole catalogue "
          "is 0603 (C710889), which is three sizes too big for this board. "
          "1.2 nF C0G does not exist in 0201 either, so there is no bracketing "
          "pair. The only 0201 part in the neighbourhood is 1.0 nF C0G, and "
          "the schematic's own note says that lands the NFC tank 5.3 % high at "
          "14.28 MHz. THE FIX IS FREE AND IT IS IN COPPER, NOT IN THE BOM: the "
          "tank tunes on L*C, so if each capacitor drops 1.109 nF -> 1.0 nF "
          "the series capacitance drops 554.6 -> 500 pF and the coil must rise "
          "by the same ratio, 554.6/500 = 1.1092, from ce-rf's measured "
          "0.2449 uH to 0.2716 uH. The coil is etched, so that costs nothing "
          "but a re-run of ce-rf's inductance solve on a slightly longer "
          "2-turn path. This is a BOARD CHANGE for lane B1, not a sourcing "
          "choice, and the alternate recorded here is the 1.0 nF part it "
          "would use."),
 dict(refs="C14,C15,C16,C17", value="DNP", fp="0201", function="crystal load capacitors, deliberately NOT FITTED (D-3: the nRF54L has on-die CAPVALUE load caps)",
      pick=None, pick_mpn=None, alt=None, alt_mpn=None, verdict="DNP",
      why="Not a sourcing gap. These four pads are the four parts jlc.md counts "
          "as CANNOT DETERMINE, and the right answer is that they carry no "
          "order code because nothing is placed on them."),
 dict(refs="R1,R2", value="4.7M", fp="0201", function="battery-sense divider (4.7 M keeps the divider current in the nanoamps)",
      pick="C778408", pick_mpn="0201WMF4704TEE", alt="C423341", alt_mpn="0201WMJ0475TEE",
      why="THINNEST STOCK ON THE BOARD AFTER THE SoC. 4.7 M in 0201 is a rare "
          "value: seven parts exist in the whole catalogue and only two carry "
          "four figures of stock. Both pick and alternate are UNI-ROYAL, so "
          "this line has ONE manufacturer, not two."),
 dict(refs="R5,R6,R7,R8,R10", value="10k", fp="0201", function="I2C/SWD pull-ups and strapping",
      pick="C473048", pick_mpn="0201WMF1002TEE", alt="C138117", alt_mpn="RC0201JR-0710KL",
      why="The exact MPN the schematic named - it was simply carrying the "
          "0402 part's order code. Half a million in stock."),
 dict(refs="R9", value="100R", fp="0201", function="piezo drive series resistor (D11a: limits GPIO current into a 40 nF bender)",
      pick="C270366", pick_mpn="0201WMF1000TEE", alt="C77623", alt_mpn="RC0201FR-07100RL",
      why="Again the schematic's own MPN under its real order code."),
 dict(refs="L1", value="4.7uH", fp="0603", function="SoC DC-DC inductor",
      pick="C76799", pick_mpn="MLZ1608M4R7WT000", alt="C394952", alt_mpn="CMH160808B4R7MT",
      why="The schematic's own TDK part under its real order code. The "
          "alternate is AEC-Q200 with 700 mA rating vs the TDK's 350 mA."),
 dict(refs="L2", value="2.7nH", fp="0201", function="2.4 GHz match, Nordic reference network",
      pick="C7216765", pick_mpn="LQP03HQ2N7B02D", alt="C76752", alt_mpn="MLG0603P2N7CT000",
      why="The schematic's own Murata high-Q part under its real order code. "
          "The TDK MLG0603 is the standard second source for LQP03 and is "
          "Q=14 vs Q=20 - acceptable, measurably worse."),
 dict(refs="L3,L4", value="3.5nH", fp="0201", function="2.4 GHz match, Nordic reference network",
      pick="C3911055", pick_mpn="LQP03HQ3N5B02D", alt="C206424", alt_mpn="LQP03TN3N5B02D",
      why="3.5 nH is a rare value: THREE parts exist in 0201 across the whole "
          "catalogue and the alternate holds only ~1.6 k. Both are Murata. "
          "If ce-rf's S11 permits 3.3 nH or 3.6 nH the sourcing risk vanishes."),
 dict(refs="L10", value="0R", fp="0201", function="antenna pi series element, fitted as a jumper so the board works untuned",
      pick="C473473", pick_mpn="0201WMF0000TEE", alt="C106228", alt_mpn="RC0201JR-070RL",
      why="Sits in an inductor footprint on purpose; a 0 ohm 0201 resistor is "
          "the same land pattern. Both options carry 500k+."),
 dict(refs="U1", value="nRF54L10-QFAA-R7", fp="QFN-48", function="the SoC: BLE + Channel Sounding + NFC-A (D12)",
      pick="C44800139", pick_mpn="NRF54L10-QFAA-R7", alt="C45022042", alt_mpn="NRF54L05-QFAA-R",
      why="D12. THE SINGLE LARGEST SUPPLY RISK ON THE BOARD - lane T6 measured "
          "212 pieces. D18 says the L05 fallback is not forced by memory, so "
          "the alternate is a real second source, at 512 kB/96 kB and a "
          "3,000-piece minimum packet."),
 dict(refs="U2", value="LIS2DW12TR", fp="LGA-12", function="3-axis accelerometer: motion wake, DULT unwanted-tracking detection",
      pick="C189624", pick_mpn="LIS2DW12TR", alt="C110926", alt_mpn="LIS2DH12TR",
      why="50 nA in the lowest-power mode, the deciding number for a coin cell. "
          "PIN COMPATIBILITY WITH THE ALTERNATE IS READ OFF BOTH DATASHEETS, "
          "not assumed: LIS2DW12 Table 2 and LIS2DH12 Table 2 both give "
          "1=SCL/SPC, 2=CS, 3=SDO/SA0, 4=SDA/SDI/SDO, 6=GND, and differ only "
          "at pin 5 (LIS2DH12 'Res, connect to GND' vs LIS2DW12 'NC, can be "
          "tied to VDD, VDDIO or GND'), which the board ties to GND either "
          "way. The cost is 500 nA against 50 nA - a build second source, not "
          "a design equal. REJECTED as an alternate on evidence: Silan "
          "SC7A20HTR (C19274408) has 106 k in stock and is a tenth of the "
          "price, but its own datasheet v0.7 p.5 gives pin 1 = SDO, 2 = SDx, "
          "3 = VDDIO - a DIFFERENT PINOUT in the same LGA-12 2x2 body. It "
          "would short VDDIO to the SDO net on this land pattern."),
 dict(refs="X1", value="32.768kHz", fp="SMD3215-2P", function="LFXO: the rotation clock the anti-stalking timing depends on",
      pick="C32346", pick_mpn="Q13FC13500004", alt="C95361", alt_mpn="Q13FC13500049",
      why="JLCPCB BASIC, so no feeder fee. CL 12.5 pF: THIS MUST BE CHECKED "
          "AGAINST THE nRF54L's on-die CAPVALUE RANGE, because D-3 deleted the "
          "external load capacitors. The alternate is the same Epson FC-135 "
          "body at CL 6 pF if the internal caps cannot reach 12.5 pF."),
 dict(refs="X2", value="32MHz", fp="SMD2016-4P", function="HFXO: the radio reference",
      pick="C843260", pick_mpn="NX2016SA-32MHZ-STD-CZS-5", alt="C718072", alt_mpn="X201632MKB4SI",
      why="CL 8 pF +/-10 ppm, which is what the schematic specified and what "
          "the vendor record confirms. The YXC alternate is the same 8 pF / "
          "+/-10 ppm at a third of the price with 60 k stock."),
 # ---- not on the JLC bill of materials, but real parts the product needs ----
 dict(refs="LS1", value="7BB-20-3", fp="bonded to shell, no land pattern", function="sounder: bare Ø20 x 0.22 mm piezo bender (D11a)",
      pick=None, pick_mpn=None, alt=None, alt_mpn=None,
      verdict="RESOLVED BY REPLACEMENT",
      why="Hand-assembled and bonded to the shell, so the machine never touches "
          "it and it carries no LCSC code by design. THE SPECIFIED MURATA PART "
          "IS END-OF-LIFE and is replaced by the PUI Audio AB2036B-2, which is "
          "a specification-for-specification match at 0.215 mm rather than "
          "0.22. Full evidence in the sounder section of docs/SOURCING.md and "
          "in the `cost.sounder` block of this file.", off_bom=True),
 dict(refs="BT1", value="CR2032", fp="halo:HALO_BATT_CONTACT_3PAD", function="the cell. The CONTACTS are three sprung C5191 fingers on halo's own land pattern - there is no bought holder",
      pick=None, pick_mpn=None, alt=None, alt_mpn=None, verdict="NOT AN SMT LINE",
      why="The schematic carried C7498149 here, which is a Lian Xin BS-CR2032-8 "
          "SMD BATTERY HOLDER. No holder is fitted - lane M's design puts three "
          "stamped fingers on halo's own three-pad footprint. The order code was "
          "wrong AND the part it named must not be ordered.", off_bom=True),
]

# --------------------------------------------------------------------------
def sh(args, out):
    subprocess.run(args + ["-o", str(out)], check=True)

def lcsc(code):
    """GET the product page and read the __NEXT_DATA__ blob."""
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"lcsc-{code}.html"
    if not p.exists() or p.stat().st_size < 50000:
        sh(["curl", "-sS", "--max-time", "90", "-A", UA,
            f"https://www.lcsc.com/product-detail/{code}.html"], p)
    h = p.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
    if not m:
        return {"error": "no __NEXT_DATA__ blob on the page"}
    # The blob carries recommended and recently-viewed products beside the one
    # asked for. FOUND BY THE SELF-TEST: a first-match walk happily returned a
    # JST connector for a piezo bender's order code, and for a code that does
    # not exist at all - which is exactly the shape of defect
    # docs/TOOLS-THAT-LIE.md is about, a well-formed answer about the wrong
    # thing. The node is only accepted if ITS OWN productCode is the one asked
    # for.
    def grab(o):
        if isinstance(o, dict):
            if {"productCode", "productModel", "productPriceList"} <= set(o) \
               and str(o.get("productCode", "")).upper() == code.upper():
                return o
            for v in o.values():
                r = grab(v)
                if r: return r
        elif isinstance(o, list):
            for v in o:
                r = grab(v)
                if r: return r
    d = grab(json.loads(m.group(1)))
    if not d:
        return {"error": f"the page carries no product node whose productCode "
                         f"is {code} - LCSC does not sell this order code"}
    return {"mpn": d.get("productModel"), "manufacturer": d.get("brandNameEn"),
            "package": d.get("encapStandard"), "stock": d.get("stockNumber"),
            "min_packet": d.get("minPacketNumber"), "split": d.get("split"),
            "datasheet": d.get("pdfUrl"), "category": d.get("catalogName"),
            "ladder": [[int(r["ladder"]), float(r["productPrice"])]
                       for r in (d.get("productPriceList") or [])]}

def jlc(code):
    """POST the catalogue endpoint; the answer carries the library type."""
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"jlc-{code}.json"
    if not p.exists() or p.stat().st_size < 50:
        sh(["curl", "-sS", "--max-time", "90", "-X", "POST", JLC_URL,
            "-H", "Content-Type: application/json", "-A", UA,
            "-d", json.dumps({"currentPage": 1, "pageSize": 5, "keyword": code})], p)
    try:
        d = json.loads(p.read_text())
    except Exception as e:
        return {"error": f"unreadable response: {e}"}
    lst = ((d.get("data") or {}).get("componentPageInfo") or {}).get("list") or []
    for it in lst:
        blob = (it.get("lcscGoodsUrl") or "") + (it.get("urlSuffix") or "")
        if code.upper() in blob.upper():
            lt = it.get("componentLibraryType")
            return {"library_type": {"base": "basic", "expand": "extended"}.get(lt, lt),
                    "stock": it.get("stockCount"), "desc": it.get("erpComponentName"),
                    "ladder": [[r["startNumber"], r["endNumber"], r["productPrice"]]
                               for r in (it.get("componentPrices") or [])]}
    return {"error": "not in the JLCPCB assembly catalogue",
            "meaning": "JLC cannot place this part even though LCSC sells it"}

def at(ladder, qty):
    """Unit price at qty from an LCSC [break, price] ladder. None if the ladder
    does not reach down that far - never extrapolated."""
    best = None
    for brk, price in sorted(ladder or []):
        if brk <= qty:
            best = price
    return best

def jlc_at(ladder, qty):
    for lo, hi, price in (ladder or []):
        if lo <= qty and (hi == -1 or qty <= hi):
            return price
    return None

def norm(s):
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper())

# KiCad footprint name -> the token the vendor's package string must contain.
# Read off the RELEASE BILL OF MATERIALS' own Footprint column, so it tracks
# the board rather than this file. This is the check that catches the exact
# defect this lane found: a 0402 order code under a 0201 land pattern is a real
# part, correctly valued, in stock, at a sane price - and twice the size of the
# pads it is going on. No price check can see that.
FP_TOKENS = [
 (re.compile(r"_0201_0603Metric"),      ["0201"]),
 (re.compile(r"_0402_1005Metric"),      ["0402"]),
 (re.compile(r"_0603_1608Metric"),      ["0603"]),
 (re.compile(r"_0805_2012Metric"),      ["0805"]),
 (re.compile(r"LGA-12_2x2"),            ["LGA-12"]),
 (re.compile(r"Crystal_SMD_3215"),      ["3215"]),
 (re.compile(r"Crystal_SMD_2016"),      ["2016"]),
 (re.compile(r"QFN-48.*6x6"),           ["QFN-48"]),
]


def package_check(footprint, vendor_package):
    if not footprint or not vendor_package:
        return "CANNOT DETERMINE", "no footprint or no vendor package string"
    for rx, tokens in FP_TOKENS:
        if rx.search(footprint):
            if any(t.upper() in vendor_package.upper() for t in tokens):
                return "MATCH", f"{footprint} wants {tokens[0]}, vendor says {vendor_package!r}"
            return "MISMATCH", (f"land pattern {footprint} is {tokens[0]}, but the "
                                f"vendor's package for this order code is "
                                f"{vendor_package!r}")
    return "CANNOT DETERMINE", (f"no size rule for footprint {footprint!r} - add one "
                                f"to FP_TOKENS rather than assuming it fits")


def resolve(code, want_mpn, footprint=None):
    if not code:
        return None
    L, J = lcsc(code), jlc(code)
    rec = {"lcsc": code, "expected_mpn": want_mpn, "fetched": TODAY,
           "lcsc_source": f"https://www.lcsc.com/product-detail/{code}.html",
           "jlcpcb_source": JLC_URL}
    rec.update({k: v for k, v in L.items() if k != "ladder"})
    rec["price_usd"] = {str(q): at(L.get("ladder"), q) for q in LADDER_QTYS}
    rec["price_ladder_lcsc"] = L.get("ladder")
    rec["library_type"] = J.get("library_type")
    rec["jlcpcb_stock"] = J.get("stock")
    rec["jlcpcb_price_usd"] = {str(q): jlc_at(J.get("ladder"), q) for q in LADDER_QTYS}
    rec["jlcpcb_ladder"] = J.get("ladder")
    if "error" in J:
        rec["jlcpcb_error"] = J["error"]
    if footprint:
        v, why = package_check(footprint, L.get("package"))
        rec["board_footprint"] = footprint
        rec["package_check"] = v
        rec["package_check_why"] = why
    if "error" in L:
        rec["mpn_check"] = "CANNOT DETERMINE"
        rec["mpn_check_why"] = L["error"]
    elif norm(L.get("mpn")).startswith(norm(want_mpn)) or norm(want_mpn).startswith(norm(L.get("mpn"))):
        rec["mpn_check"] = "MATCH"
    else:
        rec["mpn_check"] = "MISMATCH"
        rec["mpn_check_why"] = (f"order code {code} is {L.get('mpn')!r}, "
                                f"not the {want_mpn!r} this line asks for")
    return rec

# --------------------------------------------------------------------------
# The cost model. Every RATE here is lane E's, quoted from
# research/05-components-and-cost-model.md sections 10.3 and 11.6, and this
# lane does not re-derive any of them. What this lane replaces is the three
# INPUTS that section had to assume: the component prices, the solder-joint
# count, and how many order codes are JLCPCB Extended parts. All three are now
# read off the board and off the vendor.
# --------------------------------------------------------------------------
COST_MODEL = {
 "source": "research/05-components-and-cost-model.md sections 10.3 and 11.6 (lane E, 2026-09-03)",
 "assembly_setup_usd": 8.18,
 "stencil_usd": 1.53,
 "feeder_fee_per_extended_part_usd": 3.07,
 "per_joint_usd": 0.0016,
 "fee_source": "https://jlcpcb.com/help/article/pcb-assembly-price",
 "fee_staleness": "the fee table is the archived 2024-08-29 revision; ce-fab's "
                  "data/jlc-pricing.json records that the $8 Economic setup fee "
                  "still held on 2026-09-03 and the per-joint rate had moved "
                  "0.0017 -> 0.0016",
 "pcb_usd_per_unit": {"10": 6.211, "100": 0.692, "1000": 0.140, "10000": 0.085},
 "enclosure_usd_per_unit": {"10": 1.20, "100": 1.20, "1000": 0.90, "10000": 0.30},
 "tooling_usd_per_unit": {"10": 0.0, "100": 0.0, "1000": 0.0, "10000": 0.40},
 "labour_usd_per_unit": {"10": 0.30, "100": 0.30, "1000": 0.15, "10000": 0.08},
 "d15_baseline_usd_per_unit": {"10": 19.25, "100": 9.28, "1000": 7.17, "10000": 6.75},
 "d15_baseline_bom_usd": {"10": 8.21, "100": 6.57, "1000": 5.74, "10000": 5.67},
 "d15_assumed_joints": 131,
 "d15_assumed_extended_parts": 7,
}

# The sounder. D11a specifies a bare Murata 7BB-20-3, Diameter 20.0 x 0.22 mm,
# bonded to the inside of the shell and driven anti-phase from two GPIO. It is
# in NEITHER the LCSC nor the JLCPCB catalogue. Filled in by the sourcing pass;
# a null price is a null price and is never replaced by a plausible one.
SOUNDER = {
 "specified": "Murata 7BB-20-3, 20.0 mm brass disc, 0.22 mm total, ~3.6 kHz",
 "verdict": "RESOLVED - BY REPLACEMENT. The specified part is end-of-life.",
 "resolved_to": {
   "mpn": "AB2036B-2", "manufacturer": "PUI Audio (Same Sky)",
   "diameter_mm": 20.0, "thickness_mm": 0.215, "thickness_tol": "+/-10%",
   "ceramic_layer_mm": 0.1, "ceramic_layer_tol": "+/-0.015",
   "brass_mm": 0.115, "brass_note": "derived: 0.215 total - 0.100 ceramic",
   "ceramic_diameter_mm": 15.0, "electrode_diameter_mm": 13.5,
   "f0_hz": 3600, "f0_tol_hz": 600, "resonant_impedance_ohm_max": 500,
   "capacitance_pf": 20000, "capacitance_tol": "+/-30% @ 120 Hz",
   "max_input_vpp": 30, "plate": "Brass",
   "operating_c": "-20 to +70", "terminals": "bare, two pads, no wires, no housing",
   "datasheet": "https://puiaudio.com/file/specs-AB2036B-2.pdf",
   "datasheet_rev": "A, 2024-03-06, fetched 2026-09-04 (HTTP 200, 159,631 bytes)",
   "dimensions_read": "off the datasheet's own dimensioned drawing, page 1, "
                      "rendered at 200 dpi and read: 20 / 15 +/-0.3 / 13.5 "
                      "+/-0.3 diameters, 0.215 +/-10% total, 0.1 +/-0.015 "
                      "ceramic. The specification table is extractable text; "
                      "the drawing is not, so it was read as a picture.",
   "stock": {"Digi-Key": 390, "Mouser": 400},
   "usd_per_unit": {"10": 0.3620, "100": 0.2840, "1000": 0.2200, "10000": 0.1860},
   "price_source": "Mouser Electronics, ECIA member, authorized distributor, "
                   "via oemstrade.com/search/AB2036B-2, read 2026-09-04. "
                   "Ladder: 1 $0.48, 10 $0.362, 25 $0.326, 50 $0.303, "
                   "100 $0.284, 300 $0.251, 500 $0.237, 1000 $0.220, "
                   "5000 $0.186. The 10,000 figure is the 5000-and-up break, "
                   "which is the deepest the ladder publishes.",
   "corroboration": "Digi-Key (authorized, 390 in stock) quotes EUR 0.1595 at "
                    "5000 and EUR 0.43 at 1 on the same part.",
 },
 "alternate": {
   "mpn": "AB2036B", "manufacturer": "PUI Audio (Same Sky)",
   "diameter_mm": 20.0, "thickness_mm": 0.23, "thickness_tol": "+/-0.03",
   "ceramic_layer_mm": 0.1, "f0_hz": 3600, "f0_tol_hz": 500,
   "capacitance_pf": 25000, "max_input_vpp": 30,
   "datasheet": "https://puiaudio.com/file/specs-AB2036B.pdf",
   "stock": {"Digi-Key": 200},
   "why": "Same family, same 20 mm brass plate, 0.23 mm instead of 0.215, "
          "25 nF instead of 20 nF. Its drawing publishes the dimensions as "
          "extractable text (n20 +/-0.1, 0.23 +/-0.03, ceramic 0.1 +/-0.02), "
          "which makes it the better reference for the bond-pad and "
          "shell-cavity geometry even where the -2 is the part fitted.",
 },
 "why_not_the_specified_part": [
   "**The Murata 7BB-20-3 is end-of-life.** Four authorized channels agree, "
   "all read 2026-09-04: Digi-Key's product page says *\"Obsolete and no "
   "longer manufactured\"* with 0 stock; TME says *\"Product withdrawn from "
   "the offer\"*; RS Components returns `statusCode: STATUS_UNAVAILABLE` with "
   "an empty price-break array on both its SKUs; AXEL/ASONE Japan prefixes it "
   "[Discontinued].",
   "**It is not in the Chinese catalogues at all.** The keyword `7BB-20-3` "
   "returns ZERO rows from the JLCPCB assembly catalogue endpoint and from "
   "LCSC. Only 7BB-20-6C (C3812347), 7BB-20-6L0 (C3812354) and 7BB-20-6CL0 "
   "(C3812422) exist there, all at stockCount 0, and C3812347's LCSC page now "
   "returns HTTP 404.",
   "**The quantity that exists is broker stock.** Win Source lists 23,886 and "
   "several unauthorized brokers list 3,000-36,000 pieces of a part Digi-Key "
   "says is no longer manufactured. Designing that in means single-sourcing a "
   "product on dead stock with no traceability.",
   "**The only authorized stock anywhere is 38 pieces** at TTI, Americas. "
   "That is a sample quantity, not a supply.",
   "**Murata's own live status could not be read and is recorded as CANNOT "
   "DETERMINE.** murata.com/products/productdetail redirects to a "
   "client-rendered SPA that returns a 5,961-byte shell to any fetch; the "
   "/webapi/PsdispRest endpoints return an error page; and Murata's published "
   "*Discontinued Products Information of Sound Components* lists only PKM, "
   "PKB, PKLCS, PKHPS, PKMC, PKMCS and VSB housed parts, with no 7BB entry, "
   "while stating that not all discontinued products are listed. It therefore "
   "neither confirms nor clears the series.",
 ],
 "why_this_replacement": [
   "It is a **specification-for-specification match to what D11a asked for**, "
   "not an approximation: 20.0 mm brass plate, **0.215 mm total against the "
   "7BB-20-3's 0.22 mm**, 3,600 Hz +/-600, 20 nF +/-30%, <=500 ohm, 30 Vp-p, "
   "-20 to +70 C. Every one of those numbers is read off the vendor's own "
   "datasheet, and the thicknesses off its dimensioned drawing.",
   "**It is bare.** Two pads, no wires, no housing - which is what an "
   "anti-phase GPIO pair bonded to a shell needs, and what D17 requires: at "
   "0.215 mm +10% = 0.237 mm worst case it uses a sixth of the ~1.5 mm above "
   "the module, and nothing about it is over 3.5 mm.",
   "**The drive D11a specified still works, on the vendor's numbers.** At "
   "20 nF and 3,600 Hz, two pins swinging 6 V peak-to-peak draw "
   "I = 2*pi*f*C*V = 2*pi*3600*20e-9*3 = **1.36 mA peak**, inside nRF54L "
   "high-drive GPIO. R9's 100 ohms is 4.5% of the element's 2.21 kohm "
   "reactance at f0 and 20% of its <=500 ohm resonant impedance - the "
   "series resistor is correctly sized and stays on the bill of materials.",
   "**It is stocked at two authorized distributors today** - Digi-Key 390, "
   "Mouser 400 - so first articles can be built this week, and it is quoted "
   "in production quantity rather than by RFQ.",
 ],
 "cautions": [
   "**Digi-Key's own description string for this part is wrong.** It reads "
   "*BUZZER ELEMENT STD 6.3 KHZ 20MM*. The PUI datasheet says 3,600 Hz. Do "
   "not let a buyer reject the part on the catalogue line.",
   "**Do not substitute the CUI / Same Sky CEB-20D64 or CEB-20FD64** despite "
   "their far deeper stock (6,486 and 6,023 at Digi-Key). They are 0.43 mm "
   "thick, they arrive with lead wires already attached whose solder joints "
   "stack on top of the height budget, and at 10-13 nF they present about "
   "half the capacitive load the GPIO drive was sized around.",
   "**Skip LCSC and JLCPCB for this line entirely.** Of the 129 parts in "
   "JLCPCB's whole *Buzzer Plates* category, exactly one has stock (Dragonstate "
   "HE-2739E-C, 81 pieces, no datasheet published, and 27 mm). All 22 of the "
   "20 mm bare benders in that catalogue are at zero.",
   "**The loudness is still unmeasured and D11a says so.** A 3,600 Hz free-air "
   "element bonded to a stiff shell moves upward in loaded resonance; whether "
   "that lands 60 Phon at 25 cm is lane G's calibrated meter to answer, not "
   "this lane's, and nothing here converts a datasheet into a decibel.",
 ],
 "usd_per_unit": {"10": 0.3620, "100": 0.2840, "1000": 0.2200, "10000": 0.1860},
}

# Parts the product needs that the pick-and-place machine never touches.
# Priced here so the roll-up is comparable with D15's, which also carried them.
OFF_MACHINE = {
 "BT1": {"what": "CR2032 lithium coin cell",
         "usd_per_unit": {"10": 0.39, "100": 0.39, "1000": 0.39, "10000": 0.39},
         "basis": "lane E carried the qty-1 $0.39 upper bound at every volume; "
                  "this lane did not re-price it and does not pretend to",
         "verdict": "CARRIED FORWARD, NOT RE-MEASURED"},
}


def snapshot_joints(codes):
    """Solder joints per part, from JLCPCB's own catalogue, via ce-fab's
    snapshot. Never guessed from a footprint name."""
    import sqlite3
    db = pathlib.Path.home() / "dev/ce-workshop/ce-fab/data/jlcparts-slim.sqlite3"
    if not db.exists():
        return {}
    con = sqlite3.connect(str(db))
    out = {}
    for c in codes:
        r = con.execute("select joints from parts where lcsc=?", (c,)).fetchone()
        if r and r[0] is not None:
            out[c] = r[0]
    return out


def cost(lines, sounder):
    codes = [l["part"]["lcsc"] for l in lines if l.get("part") and l["on_jlc_bom"]]
    joints_by_code = snapshot_joints(codes)
    joints, extended, basic, unknown_joints = 0, [], [], []
    bom = {str(q): 0.0 for q in LADDER_QTYS}
    incomplete = {str(q): [] for q in LADDER_QTYS}
    # A second pass that substitutes the ALTERNATE wherever the pick is absent,
    # so the roll-up can also answer "what does this cost if the board takes
    # the recommended fix". Reported separately and labelled; it never
    # contributes to the primary total, which stays honestly incomplete.
    bom_fixed = {str(q): 0.0 for q in LADDER_QTYS}
    substituted = []
    for l in lines:
        p = l.get("part")
        if not p:
            # DNP is not a gap; BT1 and LS1 are priced below, off the machine.
            if l["verdict"] not in ("DNP",) and l["refs"][0] not in OFF_MACHINE \
               and l["refs"][0] != "LS1":
                for q in LADDER_QTYS:
                    incomplete[str(q)].append(",".join(l["refs"]))
            continue
        if l["on_jlc_bom"]:
            j = joints_by_code.get(p["lcsc"])
            if j is None:
                unknown_joints.append(p["lcsc"])
            else:
                joints += j * l["qty"]
            (basic if p.get("library_type") == "basic" else extended).append(p["lcsc"])
        for q in LADDER_QTYS:
            # price the LINE at the per-unit quantity, i.e. a 1000-unit build of
            # a 4-off part buys 4000 pieces and gets the 4000-piece price.
            unit = jlc_at(p.get("jlcpcb_ladder"), q * l["qty"]) or at(p.get("price_ladder_lcsc"), q * l["qty"])
            if unit is None:
                incomplete[str(q)].append(",".join(l["refs"]))
            else:
                bom[str(q)] += unit * l["qty"]
                bom_fixed[str(q)] += unit * l["qty"]
    # the substitution pass: a line with no pick but a fetched alternate
    for l in lines:
        if l.get("part") or not l.get("alternate") or not l["on_jlc_bom"]:
            continue
        a = l["alternate"]
        substituted.append({"refs": l["refs"], "lcsc": a["lcsc"], "mpn": a.get("mpn")})
        for q in LADDER_QTYS:
            unit = jlc_at(a.get("jlcpcb_ladder"), q * l["qty"]) or at(a.get("price_ladder_lcsc"), q * l["qty"])
            if unit is not None:
                bom_fixed[str(q)] += unit * l["qty"]
    # off-machine lines
    for ref, d in OFF_MACHINE.items():
        for q in LADDER_QTYS:
            bom[str(q)] += d["usd_per_unit"][str(q)]
            bom_fixed[str(q)] += d["usd_per_unit"][str(q)]
    for q in LADDER_QTYS:
        v = sounder.get("usd_per_unit", {}).get(str(q))
        if v is not None:
            bom[str(q)] += v
            bom_fixed[str(q)] += v
        else:
            incomplete[str(q)].append("LS1")
    m = COST_MODEL
    rows = {}
    for q in LADDER_QTYS:
        k = str(q)
        asm = (m["assembly_setup_usd"] + m["stencil_usd"]
               + m["feeder_fee_per_extended_part_usd"] * len(set(extended))) / q               + m["per_joint_usd"] * joints
        tot = bom[k] + m["pcb_usd_per_unit"][k] + asm + m["enclosure_usd_per_unit"][k]               + m["tooling_usd_per_unit"][k] + m["labour_usd_per_unit"][k]
        asm_j = m["per_joint_usd"] * joints
        tot_f = bom_fixed[k] + m["pcb_usd_per_unit"][k] + asm + m["enclosure_usd_per_unit"][k] \
                + m["tooling_usd_per_unit"][k] + m["labour_usd_per_unit"][k]
        rows[k] = {"bom": round(bom[k], 4),
                   "bom_with_alternates": round(bom_fixed[k], 4),
                   "total_with_alternates": round(tot_f, 4), "pcb": m["pcb_usd_per_unit"][k],
                   "assembly": round(asm, 4),
                   "enclosure": m["enclosure_usd_per_unit"][k],
                   "tooling": m["tooling_usd_per_unit"][k],
                   "labour": m["labour_usd_per_unit"][k],
                   "total": round(tot, 4),
                   "d15_total": m["d15_baseline_usd_per_unit"][k],
                   "delta_vs_d15": round(tot - m["d15_baseline_usd_per_unit"][k], 4),
                   "bom_lines_not_priced": sorted(set(incomplete[k]))}
    return {"model": m, "off_machine": OFF_MACHINE, "sounder": sounder,
            "joints_measured": joints,
            "joints_source": "JLCPCB's own solder-joint count per order code, "
                             "ce-fab data/jlcparts-slim.sqlite3 column `joints`, "
                             "multiplied by the quantity placed",
            "joints_unknown_for": unknown_joints,
            "extended_parts": sorted(set(extended)),
            "extended_part_count": len(set(extended)),
            "basic_parts": sorted(set(basic)),
            "basic_part_count": len(set(basic)),
            "substituted_lines": substituted,
            "substituted_note": "what the board would cost if lane B1 takes the "
                                "recommended fix on every unresolved line - the "
                                "alternate is a real fetched part, but the line "
                                "needs a board change first, so this total is "
                                "reported beside the honest one and never in "
                                "place of it",
            "feeder_fee_total_usd": round(len(set(extended)) * m["feeder_fee_per_extended_part_usd"], 2),
            "per_unit": rows}


def schematic_audit():
    """Read every order code OFF THE SCHEMATIC and ask the catalogue what it is.

    This is the audit that found the gap, and it is derived rather than typed:
    the codes come out of electronics/halo_rev_a/schematic.py, the answers come
    out of the catalogue, and the counts in docs/SOURCING.md are whatever this
    returns today. Lane B1 owns that file - this lane only reads it.
    """
    import sqlite3, collections
    sch = ROOT / "electronics" / "halo_rev_a" / "schematic.py"
    if not sch.exists():
        return {"verdict": "CANNOT DETERMINE", "why": "schematic.py not found"}
    sites = re.findall(r'P\("(C\d+)"\s*,\s*"([^"]*)"', sch.read_text())
    by_code = collections.defaultdict(set)
    for c, m in sites:
        by_code[c].add(m)
    db = pathlib.Path.home() / "dev/ce-workshop/ce-fab/data/jlcparts-slim.sqlite3"
    if not db.exists():
        return {"verdict": "CANNOT DETERMINE", "why": f"no catalogue snapshot at {db}"}
    con = sqlite3.connect(str(db))
    rows, wrong, loose, right = [], 0, 0, 0
    for c, ms in sorted(by_code.items()):
        r = con.execute("select mpn,package,description from parts where lcsc=?", (c,)).fetchone()
        real = r[0] if r else None
        exact = any(real and norm(real) == norm(m) for m in ms)
        prefix = any(real and (norm(real).startswith(norm(m)) or norm(m).startswith(norm(real))) for m in ms)
        # A declared string with spaces in it is a DESCRIPTION, not a part
        # number - "FC-135 32.768kHz" names a family, not an orderable item.
        # That is a documentation weakness, not a wrong component, and it is
        # counted separately so the headline number stays honest.
        descriptive = all(" " in m for m in ms)
        if exact or (prefix and not descriptive):
            verdict, right = "MATCH", right + 1
        elif descriptive:
            verdict, loose = "FAMILY NAME, NOT AN ORDER-CODE CHECK", loose + 1
        else:
            verdict, wrong = "WRONG PART", wrong + 1
        rows.append({"lcsc": c, "declared_mpn": sorted(ms), "catalogue_mpn": real,
                     "catalogue_package": r[1] if r else None,
                     "catalogue_description": r[2] if r else None,
                     "verdict": verdict})
    return {"declaration_sites": len(sites), "distinct_order_codes": len(by_code),
            "match": right, "family_name_only": loose, "wrong_part": wrong,
            "source_file": "electronics/halo_rev_a/schematic.py",
            "catalogue": "ce-fab data/jlcparts-slim.sqlite3",
            "verdict": "FAIL" if wrong else "PASS",
            "codes": rows}


def placed_bom():
    """What is actually on the board, read back from the release pack's own CSV."""
    rows = []
    with open(BOMCSV, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            rows.append(r)
    return rows

def main():
    csv_refs = set()
    for r in placed_bom():
        for ref in r["Designator"].split(","):
            csv_refs.add(ref.strip())
    lines, claimed = [], set()
    fp_by_ref = {}
    for r in placed_bom():
        for ref in r["Designator"].split(","):
            fp_by_ref[ref.strip()] = r["Footprint"]
    for ch in CHOICES:
        refs = [x.strip() for x in ch["refs"].split(",")]
        claimed.update(refs)
        fp = fp_by_ref.get(refs[0])
        pick = resolve(ch.get("pick"), ch.get("pick_mpn"), fp)
        alt = resolve(ch.get("alt"), ch.get("alt_mpn"), fp)
        verdict = ch.get("verdict")
        if verdict is None:
            if not (pick and pick["mpn_check"] == "MATCH"):
                verdict = "CANNOT DETERMINE"
            elif pick.get("package_check") == "MISMATCH":
                verdict = "PACKAGE MISMATCH"
            else:
                verdict = "RESOLVED"
        lines.append({"refs": refs, "qty": len(refs), "value": ch["value"],
                      "footprint": ch["fp"], "board_footprint": fp, "function": ch["function"],
                      "why": ch["why"], "verdict": verdict,
                      "on_jlc_bom": not ch.get("off_bom", False),
                      "part": pick, "alternate": alt})
    missing = sorted(csv_refs - claimed)
    doc = {"schema": "halo/bom-resolved/1", "generated": TODAY, "lane": "S1",
           "board": "halo_rev_a",
           "placed_refs_in_release_bom": len(csv_refs),
           "refs_covered": len(csv_refs & claimed),
           "refs_not_covered": missing,
           "endpoints": {
             "lcsc": "GET https://www.lcsc.com/product-detail/<code>.html, "
                     "__NEXT_DATA__ application/json blob",
             "jlcpcb": "POST " + JLC_URL + " {currentPage,pageSize,keyword}"},
           "price_note": "Two channels, never mixed. price_usd is LCSC RETAIL "
                         "(you buy the reel). jlcpcb_price_usd is what JLCPCB "
                         "charges when IT supplies the part during assembly. "
                         "They differ by up to 2x and the assembly number is "
                         "the one that belongs in a PCBA quote.",
           "ladder_note": "A price at a quantity the vendor's ladder does not "
                          "reach is null. Nothing here is extrapolated.",
           "lines": lines,
           "cost": cost(lines, SOUNDER),
           "schematic_audit": schematic_audit()}
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    res = sum(1 for l in lines if l["verdict"] == "RESOLVED")
    print(f"{res}/{len(lines)} lines RESOLVED; wrote {OUT}")
    for l in lines:
        if l["verdict"] != "RESOLVED":
            print(f"  {l['verdict']:22} {','.join(l['refs'])} {l['value']}")
    if missing:
        print("  refs in the release BOM with no choice here:", missing)

def self_test():
    """Break the MPN check on purpose and watch it go red.

    docs/TOOLS-THAT-LIE.md: "break every new check on purpose before trusting
    it". The whole value of this tool is one boolean - does the order code name
    the part the line asks for - and a boolean that cannot come back False is
    a decoration. Each case below is a way this tool could have reported PASS
    while being badly wrong.
    """
    cases = [
      # (order code, MPN claimed, expected verdict, why this case exists)
      ("C15525", "CL05A106MQ5NUNC", "MATCH",
       "the true positive: a code that really is the part"),
      ("C25744", "0201WMF1002TEE", "MISMATCH",
       "THE ACTUAL DEFECT THIS LANE FOUND - the sheet's 10k line. C25744 is a "
       "real, in-stock, correctly-valued 10k resistor, so a price-only check "
       "passes it. It is 0402 and the land pattern is 0201."),
      ("C1568", "GJM0335C1ER50WB01", "MISMATCH",
       "the code the sheet used for five different capacitor values"),
      ("C2827888", "CL03A225MQ3CSNC", "MISMATCH",
       "a ceramic capacitor line pointing at a screw terminal block"),
      ("C44800139", "NRF54L15-QFAA-R", "MISMATCH",
       "right family, wrong member: the L10 code claimed as an L15. A check "
       "that matched on 'NRF54L' would pass this one."),
      ("C0000000000", "ANYTHING", "CANNOT DETERMINE",
       "a code that does not exist must refuse, not invent"),
    ]
    pkg_cases = [
      ("C_0201_0603Metric", "0201", "MATCH", "the true positive"),
      ("C_0201_0603Metric", "0402", "MISMATCH",
       "THE DEFECT, ISOLATED: a correctly-valued, in-stock, sanely-priced 0402 "
       "part under a 0201 land pattern. Every check except this one passes it."),
      ("C_0402_1005Metric", "0201", "MISMATCH", "and the same error the other way"),
      ("Crystal_SMD_2016-4Pin_2.0x1.6mm", "SMD2016-4P", "MATCH", "non-chip packages too"),
      ("halo:HALO_BATT_CONTACT_3PAD", "SMD", "CANNOT DETERMINE",
       "halo's own land pattern has no size rule and must refuse rather than "
       "wave through whatever the vendor happens to say"),
    ]
    fails = 0
    for code, mpn, want, why in cases:
        got = (resolve(code, mpn) or {}).get("mpn_check")
        ok = got == want
        fails += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {code:12} as {mpn:20.20} "
              f"expected {want:17} got {got}")
        print(f"         {why}")
    for fp, pkg, want, why in pkg_cases:
        got, _ = package_check(fp, pkg)
        ok = got == want
        fails += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {fp:34.34} vs {pkg:12} "
              f"expected {want:17} got {got}")
        print(f"         {why}")
    n = len(cases) + len(pkg_cases)
    print(f"\nself-test: {n-fails}/{n} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    main()
