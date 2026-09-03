# reference/ — vendored snapshots

Depth-1 clones of the open-source projects the research lanes named, with
`.git` removed so they are plain read-only snapshots. Licences are the
upstream projects' own; nothing here is haytag's own work.

| folder | upstream | commit | licence | date | why |
|---|---|---|---|---|---|
| openhaystack ( 12M) | https://github.com/seemoo-lab/openhaystack | ea05dad | AGPL-3.0 | 2026-09-03 | Canonical Find My tag reference: adv byte layout, nRF51/ESP32/Linux firmware, macOS app. Read the firmware, do NOT copy AGPL code into a permissive firmware. |
| macless-haystack (5.0M) | https://github.com/dchristl/macless-haystack | 0bda271 | AGPL-3.0 | 2026-09-03 | The maintained end-to-end stack (key gen, docker endpoint, Android/web UI, ESP32+nRF5x firmware). Our bring-up path if we go the OpenHaystack route. |
| FindMy.py (1.9M) | https://github.com/malmeloo/FindMy.py | 31c7ef7 | MIT | 2026-09-03 | Best-maintained (v0.10.1, 2026-06) report fetch/decrypt library; MIT so usable in our tools/. Also decodes status bytes of scanned tags. |
| biemster-FindMy (2.7M) | https://github.com/biemster/FindMy | ce2b0cc | none declared | 2026-09-03 | Firmware ports for the cheap silicon we care about: Lenze ST17H66 ($1 Ali tags), Telink TLSR825X, WCH CH592, plus key generation. Licence unclear - treat as read-only reference. |
| acalatrava-openhaystack-firmware (1.0M) | https://github.com/acalatrava/openhaystack-firmware | db9ae09 | MIT | 2026-09-03 | Origin of every low-power nRF5x Find My firmware; SoftDevice-based, MIT, so we can actually derive from it. |
| heystack-nrf5x (812K) | https://github.com/pix/heystack-nrf5x | c5cb169 | none declared | 2026-09-03 | The maintained acalatrava descendant: nRF52810/nRF52832 targets, MAX_KEYS=500 rolling keys, TX-power stepping, DC/DC build variants. Closest match to our nRF52 BOM. |
| FakeTag (180K) | https://github.com/dakhnod/FakeTag | d9b688d | MIT | 2026-09-03 | nRF51 firmware with hourly key rotation and a working status-byte side channel (battery bits + event counter) - the pattern for getting sensor state out over Find My. |
| openhaystack-zephyr ( 76K) | https://github.com/koenvervloesem/openhaystack-zephyr | 86c4ea5 | MIT | 2026-09-03 | Zephyr module form of the tag; MIT and RTOS-portable, the cleanest base if haytag firmware targets Zephyr/NCS. |
| find-you (6.9M) | https://github.com/positive-security/find-you | ab7a3a9 | AGPL-3.0 | 2026-09-03 | Pre-generated key list + one-beacon-per-key firmware. Shows exactly how key rotation is implemented on ESP32 and what anti-stalking evasion looks like (so we can refuse to do it). |
| send-my ( 13M) | https://github.com/positive-security/send-my | c3b7ece | AGPL-3.0 | 2026-09-03 | Data-over-Find-My modem. Reference for using the key space as a low-rate uplink for sensor telemetry. |
| AirGuard ( 56M) | https://github.com/seemoo-lab/AirGuard | 7f71a37 | Apache-2.0 | 2026-09-03 | Android/iOS detector. Test harness: if AirGuard flags a haytag correctly, our DULT behaviour is right. |
| anisette-v3-server ( 48K) | https://github.com/Dadoum/anisette-v3-server | 2ef18d7 | none declared | 2026-09-03 | Required Apple-ID auth shim for Mac-free report fetching. Needed to run our own endpoint. |
| node-tile ( 72M) | https://github.com/lesleyxyz/node-tile | 04b2bc7 | MIT | 2026-09-03 | Reverse-engineered Tile BLE protocol; the only open client for a non-Apple/non-Google finding network. |
| google-nearby (139M) | https://github.com/google/nearby | 6d0ab62 | Apache-2.0 | 2026-09-03 | Google's own Fast Pair/Find Hub reference code; the network-agnostic second radio path for haytag. |
| ruuvitag_hw ( 14M) | https://github.com/ruuvi/ruuvitag_hw | afa1b03 | CC BY-SA 4.0 (+ no-"Ruuvi"-in-name clause) | 2026-09-03 | Only open round coin-cell nRF52832 tag with KiCad sources, a routed NFC-A coil and a routed LIS2DH12; 8 production revisions. Layout donor. Share-alike -- decide copy-vs-redraw before touching copper. |
| pinpoint-tracker ( 24M) | https://github.com/pinpoint-dev/tracker | 4e3a792 | TAPR Open Hardware License v1.0 | 2026-09-03 | The only open KiCad Apple-Find-My tag with a sounder. Reference implementation for the E73 module + piezo + battery-holder approach; reciprocal licence, safe to build on. |
| Everytag ( 11M) | https://github.com/vasimv/Everytag | cd626ba | GPL-3.0 | 2026-09-03 | Best Find My + Google FMDN firmware base (Zephyr, nRF52805/810/832/833, nRF54L15, BLE-reconfigurable, active 2026-04). hardware/ also has a complete KiCad + gerber Qi-charging beacon we can lift the BQ25121A block from. |
| shtc3_ble_beacon (9.0M) | https://github.com/Sensirion/shtc3_ble_beacon | f2957bf | BSD-3-Clause | 2026-09-03 | Permissively licensed complete CR2032 nRF52 beacon: schematic + PCB + gerbers + STEP housing. Safest design to copy outright from. |
| nrf5-eagle-reference-design (3.6M) | https://github.com/NordicPlayground/nrf5-eagle-reference-design | 108d3e6 | Nordic Semiconductor ASA, BSD-style (verify) | 2026-09-03 | Nordic's own nRF52832 QFAA / QFAA-DCDC / QFAA-NFC reference layouts (Eagle + PDF). Source of the matching network and antenna for a bare-chip haytag variant. NOTE Nordic says only the Altium versions are verified. |
| nordic-lib-kicad (5.9M) | https://github.com/hlord2000/nordic-lib-kicad | b12341f | not stated (verify) | 2026-09-03 | KiCad symbols + footprints for modern Nordic parts, packaged with reference-design blocks -- the closest existing model for haytag-core as a reusable KiCad block. |
| nrf52-kicad (3.0M) | https://github.com/jacobrosenthal/nrf52-kicad | 163d744 | not stated (verify) | 2026-09-03 | Nordic QFAA-DCDC reference converted to KiCad via altium2kicad and cleaned up. Shortcut to a KiCad-native nRF52 RF section; three conversions deep, re-verify against Nordic's Altium PDF. |
| nfc_antenna_generator (816K) | https://github.com/nideri/nfc_antenna_generator | f00a854 | not stated (verify) | 2026-09-03 | Parametric NFC coil generator that emits KiCad modules -- needed for the AirTag-parity NFC-A antenna on a 30 mm disc. |
| kicad-ifa (8.0K) | https://github.com/TobleMiner/kicad-ifa | 48083df | not stated (verify) | 2026-09-03 | KiCad inverted-F 2.4 GHz antenna footprints; starting point for the bare-chip haytag antenna and the documented keep-out. |
| EspruinoBoard ( 45M) | https://github.com/espruino/EspruinoBoard | 3c0f25d | custom Pur3 Ltd licence (verify) | 2026-09-03 | Puck.js round nRF52832 CR2032 puck schematics plus an Eagle part library for the Raytac MDBT42Q module -- prior art for "RF as a reusable part". |

## Trimmed from the snapshots (2026-09-03)

Four directories were removed after vendoring because they are bulk that no
part of this project reads, and keeping them would have made the repository
450 MB. Each is recoverable by cloning the upstream repository named above.

| removed | size | what it was | why it is not needed |
|---|---|---|---|
| `google-nearby/internal/platform/` | 121 MB | Google's cross-platform abstraction layer (Windows, Linux, Apple, embedded implementations) | we read the Fast Pair and Find Hub protocol definitions, not Google's platform porting layer |
| `node-tile/research/jadx/` | 72 MB | a decompiled Tile Android application | Tile is a comparison point in the research, not a network haytag targets |
| `AirGuard/fastlane/` | 51 MB | app-store screenshots in every locale | we use AirGuard as a detection test harness, not its store assets |
| `EspruinoBoard/frizting/` | 15 MB | Fritzing part files | we read the Puck.js coin-cell layout, not Fritzing assets |
