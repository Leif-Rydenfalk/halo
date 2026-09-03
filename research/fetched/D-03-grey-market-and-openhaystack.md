# How a tag actually gets onto the Find My network — three doors

Fetched: 2026-09-03

## Door 1 — certified: Apple issues a Token per unit
See D-01. Apple assigns PPID / Token / UUID via the MFi Portal; the Token is base64-decoded
and "stored in the accessory Flash through pre-burning in the factory production line"
(Goodix). MFi membership is "USD $99 (plus any applicable taxes and fees) per membership
year" (https://mfi.apple.com/en/faqs.html). Per-unit royalties: "This information is only
available under NDA."

## Door 2 — unregistered keys (OpenHaystack). No Apple involvement at all.
URL: https://github.com/seemoo-lab/openhaystack

- The finder iPhone does not authenticate the tag. It reads the P-224 public key out of the
  BLE advert, encrypts its own GPS fix to that key, and uploads the report.
- "Nearby iPhones will not be able to distinguish our accessories from a genuine Apple device
  or certified accessory."
- "Apple protects their database against arbitrary access by requiring an authenticated Apple
  user to download location reports." — i.e. the gate is on the READ side (an Apple ID), not
  on the tag side.
- Targets: Nordic nRF51 (BBC micro:bit v1), Espressif ESP32 (ESP32-WROOM / WROVER), Linux HCI
  (Raspberry Pi 4, "Should support any Linux machine").

biemster/FindMy (https://github.com/biemster/FindMy) removes the Mac requirement: "only a
free Apple ID is required, with SMS 2FA properly setup" to pull reports. Keys via
`./generate_keys.py`.

Consequence: an unregistered-key tag IS locatable on Apple's network, but it does NOT show up
in the stock Find My app — you need your own app/backend. That is the functional gap the
certified Token buys.

## Door 3 — the AliExpress grey tags
biemster/FindMy README: "Lenze 17H66 is found in many 1$ tags obtained from Ali".

biemster/FindMy issue #14 (https://github.com/biemster/FindMy/issues/14), AliExpress item
1005004495296995, user Cyl0nius 2022-12-07:
- After stripping the board, "only 4 components (ST17H66, xtal and 2 capacitors) remained."
- "No capacitors at the xtal and no antenna matching at all."
- "Flashed with STC Auto-Programmer (CH340) without any problem." P10->TXD, P9->RXD, GND->GND,
  3.3 V to Battery +.
- "Runs with Open-Haystack-App with no problems."

Martyn Berlin, "$3 or less location tracking without a mac"
(https://musings.martyn.berlin/3-or-less-location-tracking-without-a-mac): bought
https://www.aliexpress.com/item/1005007391882805.html , received ST17H66 units, notes "No
guarantees that the next batch from this supplier will be the same." Flashed over UART on test
points P9/P10/GND/P15 at 3.3 V.

Positive Security, "Find You" (https://positive.security/blog/find-you): built a stealth clone
on an ESP32 + power bank; "iterate through 2000 key pairs and send one beacon every 30
seconds"; "Apple devices currently have no way to distinguish genuine AirTags from clones via
Bluetooth."

## The fourth thing, which is NOT a Find My tag at all
hotairtag.com/fake-airtag/: counterfeit AirTag *shells* sell for "$3–$15 on AliExpress",
contain "no U1 Ultra-Wideband chip, no Apple-certified Find My module", have "zero connection
to the Find My network" and are "a piece of plastic that does nothing." Do not confuse these
with the working ST17H66 grey tags.
