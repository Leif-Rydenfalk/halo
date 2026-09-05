# Raw pages behind §4 of docs/SOURCING-ALTERNATES.md

Saved as fetched so the distributor numbers can be re-read rather than trusted. All three retrieved
2026-09-05T07:39–07:40Z with `curl --max-time 60`, browser UA.

| file | URL | HTTP | bytes |
|---|---|--:|--:|
| `oemstrade-NRF54L10-QFAA-R7.html` | https://www.oemstrade.com/search/nRF54L10-QFAA-R7 | 200 | 237,102 |
| `oemstrade-NRF54L10-QFAA-R.html` | https://www.oemstrade.com/search/NRF54L10-QFAA-R | 200 | 316,358 |
| `nordic-ordering-info-HTTP403.html` | https://docs.nordicsemi.com/bundle/ps_nrf54L15/page/chapters/ordering_info/ordering_info.html | **403** | 5,925 |

The third is kept deliberately. It is the reason the `-R` / `-R7` equivalence is written up as four
distributors agreeing rather than as the manufacturer confirming, and 11,366 of the 14,956 authorized
pieces hang on that distinction.

Nothing here was obtained by contacting a distributor. No account, no quote, no order.

## Added 07:41Z — the three passive lines, same method

| file | URL | HTTP | bytes |
|---|---|--:|--:|
| `oemstrade-LQP03HQ3N5B02D.html` | https://www.oemstrade.com/search/LQP03HQ3N5B02D | 200 | 229,345 |
| `oemstrade-GJM0335C1HR50WB01D.html` | https://www.oemstrade.com/search/GJM0335C1HR50WB01D | 200 | 422,713 |
| `oemstrade-0201WMF4704TEE.html` | https://www.oemstrade.com/search/0201WMF4704TEE | 200 | 118,370 |

These three are why §3's L3/L4 verdict changed from "no qualified alternate at 10,000" to "PASS with
the fitted part, through an authorized distributor". DigiKey holds 398,982 of the 3.5 nH part that
JLCPCB holds 8,441 of. The parser is `parse` in the lane's scratchpad; re-read them with any HTML
tool — the numbers sit next to the distributor's own ECIA/authorized label on each row.

## Added 09:34Z — the manufacturer, settling what the distributors could only suggest

`nrf54l-datasheet-v1.0-chapter14-ordering.txt` — chapter 14 *Ordering information*, pp. 926–929, of
Nordic Semiconductor's **nRF54L15/nRF54L10/nRF54L05 datasheet v1.0, document `4503_018`**, extracted
verbatim with `pdftotext -layout`.

Source PDF: `https://datasheet.lcsc.com/datasheet/pdf/11cf20669bff633a577e95a4820b68c9.pdf`
(LCSC's mirror of Nordic's own document — `docs.nordicsemi.com` still 403s).
HTTP 200, **13,174,442 bytes**, `sha256 ade0d340ba95e31f8299e6721b08d53a702962335d9b87fa202f8d2767603554`,
fetched 2026-09-05T09:34Z. The PDF itself is not committed — 13 MB against a 172-line answer — but
the hash and URL make it re-fetchable and checkable.

**What it settles.** Table 109, *Container codes*: **`R7` = 7″ Reel, `R` = 13″ Reel.** Figure 203 and
Table 99 give the order code as `nRF54L<DD>-<PP><VV>-<CC>`, so the suffix is the **container**, not
the device. `NRF54L10-QFAA-R7` and `NRF54L10-QFAA-R` are identical in device (`10`), package (`QF` =
QFN48 6×6 mm 0.4 mm pitch, Table 101) and function variant (`AA`). Table 111 gives their MOQs as
1,000 and 3,000 — **exactly the `minPacketNumber` values LCSC's API returned for C44800139 and
C45022043** in the live probe, so the manufacturer's table and the vendor's API agree to the piece.

U1's authorized figure of **14,956 stands.** It does not collapse to 3,590.
