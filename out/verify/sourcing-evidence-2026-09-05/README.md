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
