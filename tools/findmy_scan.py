#!/usr/bin/env python3
"""
findmy_scan.py — passive BLE scanner for Apple Find My / "offline finding" (OF)
advertisements, written for halo lane J.

WHAT IT LOOKS FOR
-----------------
Per research/02-findmy-protocol-and-openhaystack.md §1 (PoPETs 2021 Table 2,
cross-checked against OpenHaystack's ESP32 main.c), a Find My tag in the
*separated* state emits a 37-byte non-connectable undirected advertisement:

    byte  0      : 0x1E   AD length (30)
    byte  1      : 0xFF   AD type = manufacturer specific data
    bytes 2-3    : 0x4C 0x00  company id 0x004C (Apple, little endian)
    byte  4      : 0x12   Apple payload type "offline finding"
    byte  5      : 0x19   payload length (25)
    byte  6      : status byte (battery state in the top bits; the OpenHaystack
                   forks also abuse the low bits as a side channel)
    bytes 7-28   : p[6..27] — public-key bytes 6..27 of the rolling P-224 key
    byte  29     : p[0] >> 6 — the two bits of key byte 0 that could not fit in
                   the BLE address
    byte  30     : hint (0x00 from a tag; non-zero from an iDevice)

    and, NOT in the payload, the advertising address itself carries the first
    six key bytes:  addr = (p[0] | 0b11000000) : p[1] : p[2] : p[3] : p[4] : p[5]

So the manufacturer-specific data as bleak reports it (company id stripped) is
25 bytes: 12 19 <status> <22 key bytes> <p0>>6> <hint>  — wait: 0x12 0x19 are
the type/length, and the 25 bytes counted by 0x19 are status..hint. bleak's
`manufacturer_data[0x004C]` therefore begins with 0x12 0x19.

Nearby-info adverts (type 0x10) and continuity adverts (0x0C, 0x07 ...) are
counted separately so we can see how much Apple traffic is around in total.

THE macOS CAVEAT — MEASURED, NOT ASSUMED
----------------------------------------
CoreBluetooth (which bleak uses on macOS via PyObjC) does NOT expose the
peripheral's Bluetooth address. It substitutes a per-host, per-boot random
CBPeripheral UUID. That means:

  * key bytes p[0..5] are UNRECOVERABLE on macOS. Only p[6..27] and the two
    top bits of p[0] are visible. A full 28-byte key needs a Linux/BlueZ or
    nRF-sniffer host.
  * CoreBluetooth also does not hand up the raw AD structure, only a parsed
    dictionary, so we cannot verify the 0x1E/0xFF framing bytes directly.

This script reports whether Apple manufacturer data reaches us at all, which
is the part that actually had to be measured.

USAGE
-----
    python3 tools/findmy_scan.py --seconds 300 --json out/lane-J/scan.json
"""

import argparse
import asyncio
import json
import platform
import sys
import time
from collections import defaultdict

try:
    from bleak import BleakScanner
except ImportError:
    sys.exit("bleak not installed:  pip install bleak")

APPLE_CID = 0x004C

APPLE_TYPES = {
    0x02: "iBeacon",
    0x05: "AirDrop",
    0x06: "HomeKit",
    0x07: "Proximity Pairing (AirPods etc)",
    0x08: "Hey Siri",
    0x09: "AirPlay target",
    0x0A: "AirPlay source",
    0x0B: "Magic Switch",
    0x0C: "Handoff",
    0x0D: "Tethering target",
    0x0E: "Tethering source",
    0x0F: "Nearby Action",
    0x10: "Nearby Info",
    0x12: "Find My / offline finding",
    0x16: "Find My (0x16 variant)",
}

BATTERY_STATE = {0b00: "full", 0b01: "medium", 0b10: "low", 0b11: "critically low"}


def decode_findmy(mfg: bytes):
    """Decode an Apple 0x12 offline-finding payload. mfg starts at the type byte."""
    if len(mfg) < 2 or mfg[0] not in (0x12, 0x16):
        return None
    plen = mfg[1]
    body = mfg[2:]
    out = {
        "apple_type": f"0x{mfg[0]:02x}",
        "raw_hex": mfg.hex(),
        "declared_len": plen,
        "actual_body_len": len(body),
    }
    if plen == 0x19 and len(body) >= 25:
        status = body[0]
        key_mid = body[1:23]          # p[6..27]
        p0_top = body[23]             # p[0] >> 6
        hint = body[24]
        out.update({
            "variant": "separated (full 0x19 payload)",
            "status_byte": f"0x{status:02x}",
            "battery": BATTERY_STATE.get((status >> 6) & 0b11, "?"),
            "status_low_bits": f"0b{status & 0x3F:06b}",
            "key_p6_p27_hex": key_mid.hex(),
            "p0_top2bits": f"0b{p0_top & 0b11:02b}" if p0_top <= 3 else f"0x{p0_top:02x}",
            "hint": f"0x{hint:02x}",
            "hint_meaning": "tag (0x00)" if hint == 0 else "iDevice / non-zero hint",
        })
    elif plen == 0x02 and len(body) >= 2:
        # "nearby / owner-connected" short form: 12 02 <status> <hint>
        out.update({
            "variant": "near-owner (short 0x02 payload)",
            "status_byte": f"0x{body[0]:02x}",
            "battery": BATTERY_STATE.get((body[0] >> 6) & 0b11, "?"),
            "hint": f"0x{body[1]:02x}",
        })
    else:
        out["variant"] = f"unrecognised (type 0x{mfg[0]:02x} len 0x{plen:02x})"
        out["raw"] = body.hex()
    return out


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=300)
    ap.add_argument("--json", default=None)
    ap.add_argument("--quiet", action="store_true", help="no per-packet lines")
    args = ap.parse_args()

    devices = {}          # key -> record
    counts = defaultdict(int)
    total_adv = 0
    apple_adv = 0
    any_mfg = 0
    t0 = time.time()

    def cb(dev, adv):
        nonlocal total_adv, apple_adv, any_mfg
        total_adv += 1
        md = adv.manufacturer_data or {}
        if md:
            any_mfg += 1
        for cid, payload in md.items():
            counts[f"cid_0x{cid:04x}"] += 1
            if cid != APPLE_CID:
                continue
            apple_adv += 1
            atype = payload[0] if payload else None
            counts[f"apple_type_0x{atype:02x}"] += 1
            rec = devices.setdefault(dev.address, {
                "address_or_uuid": dev.address,
                "name": dev.name,
                "first_seen": round(time.time() - t0, 1),
                "packets": 0,
                "rssi_min": 127, "rssi_max": -127,
                "apple_types": {},
                "findmy_payloads": [],
                "distinct_keys": set(),
            })
            rec["packets"] += 1
            rec["last_seen"] = round(time.time() - t0, 1)
            r = adv.rssi
            if r is not None:
                rec["rssi_min"] = min(rec["rssi_min"], r)
                rec["rssi_max"] = max(rec["rssi_max"], r)
                rec["rssi_last"] = r
            tname = APPLE_TYPES.get(atype, f"unknown 0x{atype:02x}")
            rec["apple_types"][f"0x{atype:02x}"] = tname
            if atype in (0x12, 0x16):
                d = decode_findmy(payload)
                if d:
                    if d.get("key_p6_p27_hex"):
                        rec["distinct_keys"].add(d["key_p6_p27_hex"])
                    if len(rec["findmy_payloads"]) < 6:
                        rec["findmy_payloads"].append(d)
                    if not args.quiet:
                        print(f"[{time.time()-t0:6.1f}s] FINDMY {dev.address} "
                              f"rssi={r} {d.get('variant')} "
                              f"batt={d.get('battery')} hint={d.get('hint')} "
                              f"key6-27={d.get('key_p6_p27_hex','')[:24]}...")
            elif not args.quiet and atype not in (0x10, 0x0C, 0x07):
                print(f"[{time.time()-t0:6.1f}s] apple  {dev.address} rssi={r} "
                      f"type=0x{atype:02x} {tname}")

    print(f"# findmy_scan.py — host {platform.platform()}  python {platform.python_version()}")
    print(f"# scanning {args.seconds}s for Apple 0x004C manufacturer data ...")
    scanner = BleakScanner(detection_callback=cb)
    await scanner.start()
    await asyncio.sleep(args.seconds)
    await scanner.stop()

    for r in devices.values():
        r["distinct_keys"] = sorted(r["distinct_keys"])
        r["n_distinct_keys"] = len(r["distinct_keys"])

    summary = {
        "host": platform.platform(),
        "started_epoch": t0,
        "duration_s": args.seconds,
        "total_advertisements": total_adv,
        "advertisements_with_any_manufacturer_data": any_mfg,
        "apple_manufacturer_advertisements": apple_adv,
        "counts": dict(counts),
        "macos_note": ("CoreBluetooth substitutes a random CBPeripheral UUID for the "
                       "BLE address, so key bytes p[0..5] cannot be recovered on macOS."),
        "devices": list(devices.values()),
    }

    print("\n===== SUMMARY =====")
    print(f"advertisements seen              : {total_adv}")
    print(f"  with any manufacturer data     : {any_mfg}")
    print(f"  with Apple company id 0x004C   : {apple_adv}")
    print("counts by company id / apple type:")
    for k, v in sorted(counts.items()):
        label = ""
        if k.startswith("apple_type_"):
            label = "  " + APPLE_TYPES.get(int(k[-2:], 16), "unknown")
        print(f"  {k:24s} {v:6d}{label}")
    fm = [d for d in devices.values() if any(t in d["apple_types"] for t in ("0x12", "0x16"))]
    print(f"\ndistinct devices emitting Find My (0x12/0x16): {len(fm)}")
    print(f"{'peripheral uuid (macOS)':38s} {'pkts':>5} {'rssi':>10} {'keys':>5}  variant")
    for d in sorted(fm, key=lambda x: -x["packets"]):
        v = d["findmy_payloads"][0].get("variant", "?") if d["findmy_payloads"] else "?"
        print(f"{d['address_or_uuid']:38s} {d['packets']:5d} "
              f"{d['rssi_min']:4d}..{d['rssi_max']:<4d} {d['n_distinct_keys']:5d}  {v}")

    if args.json:
        with open(args.json, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    asyncio.run(main())
