# What tags and their parts actually cost at volume

Fetched: 2026-09-03

## Finished "works with Find My" tags, B2B (Alibaba electronics guide, cheap-key-finder)
URL: https://electronics.alibaba.com/product/cheap-key-finder — quoted verbatim:

| Product | Price | MOQ | Supplier |
|---|---|---|---|
| Smart Tag (iOS Compatible) | $2.22–$2.52 | 100 pcs | Shenzhen Pet Baby Technology Co., Ltd. |
| Air Tracker Tag Bluetooth Tracker | $3.33–$54.50 | 30 pcs | Shenzhen BHD Technology Co., Ltd. |
| Yanyi Google Mini Pet Key Finder | $3.20–$4.50 | 1 pc | Shenzhen Yanyi Technology Co., Ltd. |
| Trangjan Find My Hub Tracker | $3.57–$5.57 | 1 pc | Dongguan Trangjan Industrial Co., Ltd. |
| WEST Dual System MFi Tracker | $3.76–$4.09 | 5 pcs | Shenzhen WEST Technology Co., Ltd. |
| Smart GPS Tracker (replaceable battery) | $3.90–$5.50 | 1,000 pcs | Hongkong Penglian Technology Ltd |
| ITrack 2 Find My Bluetooth Tracker | $4.51–$4.91 | 200 pcs | KKM Company Limited |
| Omni IPX6 Smart Tracker | $4.40–$7.40 | 100 pcs | Shenzhen Omni Intelligent Technology |
| Kingstar Bluetooth Locator | $5.56–$5.99 | 10 pcs | Shenzhen Kingstar Technology Co., Ltd. |
| HLD Tuya Tracking Device | $6.10–$6.50 | 1,000 pcs | Shenzhen Homelead Electronics Co., Ltd. |
| Kaiqisheng MFI Smart Tag GPS | $6.49–$7.99 | 50 sets | ShenZhen Kaiqisheng Technology Co., Ltd. |
| RSH Tuya Smart Tag | $7.00–$8.33 | 2 pcs | RSH Technology Co., Ltd. |
| Minew Smart Key Finder Tags | $7.50–$9.99 | 3 pcs | Shenzhen Minew Technologies Co., Ltd. |

Page's own summary: wholesale pricing "typically spans $3.30–$8.00 per unit in the
affordable segment, with many products featuring Apple MFi certification compatibility."

CAUTION: "MFi certification compatibility" in an Alibaba listing is a marketing phrase, not
evidence. Treat every certification claim on that table as UNVERIFIED unless the supplier's
MFi account number or an FCC filing backs it.

## Grey / unregistered-key tags
biemster/FindMy README: "Lenze 17H66 is found in many 1$ tags obtained from Ali".
Counterfeit non-functional AirTag shells: "$3–$15 on AliExpress" (hotairtag.com/fake-airtag/).

## The ODM layer
Shenzhen Kingminson Electronic Co., Ltd. (https://kingminson.com/) — self-described Apple
MFi-authorised manufacturer, "Since 2014", "1,300 sqm Area", "70 people", "50+" patents;
sells four Find My tracker models (M15, M13, M10, M06) plus a Find My card, "OEM-ready",
"small-batch orders". MOQ and prices not published. MFi ID not disclosed on the page —
UNVERIFIED that they hold one.

## Silicon, verified distributor pricing (LCSC, fetched 2026-09-03)
| Part | LCSC | 1+ | 100+ | 1000+ | stock |
|---|---|---|---|---|---|
| nRF52810-QCAA-R (WLCSP) | C519278 | $3.1885 | $1.9808 | $1.7977 | out of stock |
| NRF52810-QFAA-R (QFN48) | C141828 | $4.50 | $2.0914 | $1.9043 | 19,746 |

Cheap Chinese BLE SoC prices (PHY6222, ST17H66/ST17H65, TLSR825x) could NOT be verified —
LCSC's search API and oemsecrets both refused automated access this session. The ~$0.30–0.60
band usually quoted for these parts is UNVERIFIED here. What IS verified is the finished-tag
price they enable: a working ST17H66 Find My tag lands at roughly $1 on AliExpress.

## Apple
AirTag 2: "$29" single, "$99" four-pack, free engraving, shipping from 2026-01-28
(MacRumors). TechInsights on gen-1 AirTag: "estimated manufacturing cost of USD 10 (not
including software costs and R&D)".

## MFi
"The MFi Program is USD $99 (plus any applicable taxes and fees) per membership year."
Per-unit royalties: "This information is only available under NDA."
(https://mfi.apple.com/en/faqs.html)
