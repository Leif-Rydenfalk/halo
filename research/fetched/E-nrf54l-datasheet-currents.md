# E — nRF54L15 / nRF54L10 / nRF54L05 datasheet: the current tables

**Provenance.** `nRF54L15, nRF54L10, and nRF54L05 Wireless SoCs`, **PRELIMINARY DATASHEET v0.10**,
footer id **`4503_018 v0.10`**, 906 pages, PDF `Title:` metadata `nRF54L15 - nRF54L10 - nRF54L05`.
Downloaded from nordicsemi.com on **2026-09-03** by this lane (first pass, before the session was
killed); the local copy used for these extracts was at `/tmp/nrf54l.pdf`, 14 488 090 bytes.

**The canonical URL could not be re-verified on 2026-09-03**: every `nordicsemi.com` and
`docs.nordicsemi.com` path tried returned **HTTP 403** to an automated fetch, including
`nordicsemi.com/Products/nRF54L10`. So the document is identified here by its own internal
version string and page numbers rather than by a link, and the extracts below are quoted verbatim
from `pdftotext -layout` output so anyone with the same PDF can grep them.

One thing this document settles that the product pages do not: **it covers all three parts.**
The L15, L10 and L05 differ only by memory, so every radio current below applies to the
nRF54L10 that D12 picked, and the sleep currents differ between them *only* through how much
RAM there is to retain.

---

## Section 11.1.2.1 — Sleep (page 860)

```
11.1.2 CURRENT Electrical specification
11.1.2.1 Sleep

Symbol            Description                                                        Min.   Typ.      Max.      Units
IOFF0             System OFF, Wake on pin, 0 KB RAM retained                                0.6                 μA
IOFF1             System OFF, Wake on pin + GRTC, LFXO, 0 KB RAM retained                   0.8                 μA
ION_IDLE0         System ON, Wake on pin, 0 KB RAM retained                                 0.7                 μA
ION_IDLE1         System ON, Wake on pin, 64 KB RAM retained                                1.3                 μA
ION_IDLE2         System ON, Wake on pin, 96 KB RAM retained                                1.5                 μA
ION_IDLE3         System ON, Wake on pin, 128 KB RAM retained                               1.8                 μA
ION_IDLE4         System ON, Wake on pin, 192 KB RAM retained                               2.4                 μA
ION_IDLE5         System ON, Wake on pin, 256 KB RAM retained                               3.0                 μA
ION_IDLE6         System ON, Wake on pin + GRTC, LFXO, 64 KB RAM retained                   1.5                 μA
ION_IDLE7         System ON, Wake on pin + GRTC, LFXO, 128 KB RAM retained                  2.0                 μA
ION_IDLE8         System ON, Wake on pin + GRTC, LFXO, 256 KB RAM retained                  3.1                 μA
ION_IDLE9         System ON, Wake on pin + GRTC, LFRC, 256 KB RAM retained                  3.7                 μA
ION_IDLE11        System ON, Wake on pin, Constant Latency mode, 0 KB RAM retained          0.53                mA


```

## Section 11.1.2.3 — CPU running (page 860)

```
IAPPCPU0          CPU running Coremark at 128 MHz from NVM, Cache enabled                   2.6                 mA
IAPPCPU1          CPU running Coremark at 128 MHz from RAM, Cache disabled                  2.9                 mA

```

## Radio TX / RX run currents

```
ITX,MaxdBm,QFN         TX only run current for QFN package, PRF at maximum power setting          9.1                  mA
ITX,MaxdBm,CSP         TX only run current for CSP package, PRF at maximum power setting          9.7                  mA
ITX,0dBM               TX only run current, PRF = 0 dBm                                           3.7                  mA
ITX,MINUS4dBM          TX only run current PRF = -4 dBm                                           2.8                  mA
ITX,MINUS8dBM          TX only run current PRF = -8 dBm                                           2.2                  mA
ITX,MINUS12dBM         TX only run current PRF = -12 dBm                                          1.9                  mA
ITX,MINUS16dBM         TX only run current PRF = -16 dBm                                          1.7                  mA
ITX,MINUS40dBM         TX only run current PRF = -40 dBm                                          1.2                  mA
IRX,1M                 RX only run current, 1 Mbps/1 Mbps Bluetooth LE mode                       2.1                  mA
IRX,2M                 RX only run current, 2 Mbps/2 Mbps Bluetooth LE mode                       2.1                  mA
```

---

## What these numbers mean for halo

1. **TX at 0 dBm is 3.7 mA**, not the 4.8 mA on Nordic's nRF54L15 product page — the page quotes a
   whole-device figure, the datasheet a radio-only one. RX at 1 Mbps is **2.1 mA**. Both are below
   the nRF52832 figures used in `research/05` §4's battery table, so every CR2032 life estimate
   there is a **floor** on nRF54L, not a ceiling.
2. **The nRF54L05 sleeps 0.9 µA lower than the nRF54L10** — `ION_IDLE2` (96 KB retained) 1.5 µA
   versus `ION_IDLE4` (192 KB retained) 2.4 µA — purely because there is less RAM to hold. On a tag
   whose average current is single-digit microamps that is a larger battery lever than the $0.39
   of silicon between the two parts. **The L05-versus-L10 decision is a battery decision as well
   as a cost decision.**
3. **CANNOT DETERMINE: the state halo actually advertises from is not published.** With GRTC and
   LFXO running, the datasheet gives 64 KB (1.5 µA), 128 KB (2.0 µA) and 256 KB (3.1 µA) — there is
   **no 192 KB row**, which is exactly the nRF54L10's RAM. The real figure is bracketed by 2.0 and
   3.1 µA. Do not quote a single number for it; lane H should measure it on the bench.
4. `IOFF1` — System OFF, wake on pin **plus GRTC on the LFXO**, 0 KB RAM retained — is **0.8 µA**.
   That is the deepest state that can still keep time, which is what a tag needs between
   advertising events if it is willing to re-derive state on each wake.
