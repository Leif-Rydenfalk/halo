"""f_render — render both faces AND MEASURE THAT THE PICTURE IS RIGHT.

    python3 electronics/halo_replica/tools/f_render.py
    ... --break-green      render WITHOUT the stackup colours and watch it fail

Exit 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

---------------------------------------------------------------------------
WHY A RENDER NEEDS A CHECK AT ALL
---------------------------------------------------------------------------
pcb/board.py writes `(color "black")` into the board's stackup and then
proves it by reloading the file and reading the token back. That check
passed. THE BOARD STILL RENDERED KICAD-DEFAULT GREEN, because
`kicad-cli pcb render` ignores the stackup unless it is given
`--use-board-stackup-colors`.

That is the exact shape this project keeps finding: a control that verifies
the thing next to the claim instead of the claim. The file really did say
black. The picture — the artifact a human looks at and believes — did not.
So the check moved to the picture: this reads the rendered PNG back and
measures the hue of the soldermask, and a green board FAILS here no matter
what any file says.

---------------------------------------------------------------------------
WHAT IS MEASURED, AND THE CONTROL
---------------------------------------------------------------------------
Mask pixels are sampled from an annulus between the pocket and the outer
edge, at radii that avoid both. For each, hue and value. The board passes
only if the sample is DARK AND NEUTRAL. THE NUMBERS ARE NOT COMPARED TO
APPLE'S: the stackup's V 65-128 is off a photograph under an unknown
illuminant and this is a raytraced render under lights of its own, so the
two are comparable in KIND and not in VALUE. What is tested — which is the same language the
stackup measurement uses for Apple's own mask ("V=65 to 128 ... R, G and B
within about 10 counts of each other") and is deliberately not a test for
"black", because the drawn colour is a CHOICE inside that bound and the
bound is the thing worth defending.

`--break-green` renders the SAME board without --use-board-stackup-colors.
If that does not fail, this check is measuring something other than the
mask.
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(HERE)
OUT = os.path.join(REPLICA, "pcb", "out")
PCB = os.path.join(OUT, "halo_replica.kicad_pcb")
CLI = "kicad-cli"

# A green soldermask is hue ~90-160 deg at high saturation. A dark neutral is
# low saturation at low value. The bar is set from the stackup lane's own
# measurement of Apple's mask, not from what this board happens to render.
MAX_V = 140          # stackup.json: Apple's flat mask patches read V 65-128
MAX_SAT = 0.35       # "R, G and B within about 10 counts of each other" is
                     # ~0.05; 0.35 is generous and still excludes any green.


def _png_rgb(path):
    """Read a PNG to (w, h, [(r,g,b)]) with the stdlib only.

    No Pillow, no numpy — zlib and struct are in the standard library and a
    dependency for reading back one's own output is a dependency too many.
    """
    import struct
    import zlib
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    i, idat, w = 8, b"", None
    while i < len(data):
        ln = struct.unpack(">I", data[i:i + 4])[0]
        typ = data[i + 4:i + 8]
        body = data[i + 8:i + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
            assert depth == 8, "expected 8-bit, got %d" % depth
            assert ctype in (2, 6), "expected RGB or RGBA, got %d" % ctype
            nch = 3 if ctype == 2 else 4
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        i += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * nch
    px, prev = [], bytearray(stride)
    pos = 0
    for _ in range(h):
        f = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride
        for x in range(stride):
            a = line[x - nch] if x >= nch else 0
            bq = prev[x]
            c = prev[x - nch] if x >= nch else 0
            if f == 1:
                line[x] = (line[x] + a) & 0xFF
            elif f == 2:
                line[x] = (line[x] + bq) & 0xFF
            elif f == 3:
                line[x] = (line[x] + ((a + bq) >> 1)) & 0xFF
            elif f == 4:
                p = a + bq - c
                pa, pb, pc = abs(p - a), abs(p - bq), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (bq if pb <= pc else c)
                line[x] = (line[x] + pr) & 0xFF
        prev = line
        px.append([tuple(line[x:x + 3]) for x in range(0, stride, nch)])
    return w, h, px


def _hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    v = mx
    s = 0.0 if mx == 0 else (mx - mn) / mx
    if mx == mn:
        h = 0.0
    elif mx == r:
        h = (60 * (g - b) / (mx - mn)) % 360
    elif mx == g:
        h = 60 * (b - r) / (mx - mn) + 120
    else:
        h = 60 * (r - g) / (mx - mn) + 240
    return h, s, v * 255.0


def _mask_sample(path):
    """Mask pixels: the annulus between the pocket and the outer edge."""
    w, h, px = _png_rgb(path)
    cx, cy = w / 2.0, h / 2.0
    # The board fills the frame; the pocket is roughly half the outer radius.
    r_out = min(w, h) / 2.0
    lo, hi = 0.62 * r_out, 0.80 * r_out
    got = []
    for k in range(4000):
        a = 2 * math.pi * k / 4000.0
        r = lo + (hi - lo) * ((k * 0.6180339887) % 1.0)
        x, y = int(cx + r * math.cos(a)), int(cy + r * math.sin(a))
        if 0 <= x < w and 0 <= y < h:
            got.append(px[y][x])
    return got


def main():
    argv = sys.argv[1:]
    break_green = "--break-green" in argv
    if not os.path.exists(PCB):
        print("CANNOT DETERMINE — no board at %s" % PCB)
        return 2

    results, worst = [], None
    for side in ("top", "bottom"):
        png = os.path.join(OUT, "halo_replica-%s%s.png"
                           % (side, "-BROKEN" if break_green else ""))
        cmd = [CLI, "pcb", "render", "--output", png, "--side", side,
               "--width", "1000", "--height", "1000",
               "--background", "opaque", "--quality", "high"]
        if not break_green:
            # THE FLAG THE FIRST ATTEMPT DID NOT HAVE, AND THE WHOLE REASON
            # THIS FILE EXISTS. Without it kicad-cli renders the appearance
            # preset and silently ignores the stackup the board carries.
            cmd.append("--use-board-stackup-colors")
        cmd.append(PCB)
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0 or not os.path.exists(png):
            print("CANNOT DETERMINE — render failed for %s (rc=%d): %s"
                  % (side, r.returncode,
                     (r.stderr.decode() or r.stdout.decode())[-300:]))
            return 2
        sample = _mask_sample(png)
        if len(sample) < 500:
            print("CANNOT DETERMINE — only %d mask samples on %s"
                  % (len(sample), side))
            return 2
        hsv = [_hsv(*p) for p in sample]
        hsv.sort(key=lambda t: t[2])
        med = hsv[len(hsv) // 2]
        greenish = sum(1 for hh, ss, vv in hsv
                       if 70 <= hh <= 170 and ss > MAX_SAT) / len(hsv)
        ok = med[2] <= MAX_V and med[1] <= MAX_SAT
        results.append({"side": side, "png": os.path.relpath(png, REPLICA),
                        "n": len(sample),
                        "median_hue_deg": round(med[0], 1),
                        "median_saturation": round(med[1], 3),
                        "median_value": round(med[2], 1),
                        "fraction_saturated_green": round(greenish, 3),
                        "bar": {"max_value": MAX_V, "max_saturation": MAX_SAT},
                        "verdict": "PASS" if ok else "FAIL"})
        if not ok:
            worst = results[-1]

    print("f_render — %s" % PCB)
    if break_green:
        print("  BREAK ACTIVE: rendered WITHOUT --use-board-stackup-colors")
    for r in results:
        print("  %-6s hue %6.1f deg  sat %.3f  V %5.1f  (bar: V<=%d, "
              "sat<=%.2f)  green frac %.3f  %s"
              % (r["side"], r["median_hue_deg"], r["median_saturation"],
                 r["median_value"], MAX_V, MAX_SAT,
                 r["fraction_saturated_green"], r["verdict"]))
    if worst:
        print("  FAIL — the mask in the PICTURE is not dark and neutral. The "
              "file saying so is not the same claim.")
        code = 1
    else:
        print("  PASS — both faces render DARK AND NEUTRAL, which is the "
              "only property this can test.")
        print("  NOT CLAIMED: that these numbers match Apple's. The "
              "stackup's V 65-128 is off a PHOTOGRAPH under an unknown "
              "illuminant; this is a raytraced render under lights of its "
              "own choosing, and V=11 here is not V=11 there. The two are "
              "comparable in KIND (dark, near-neutral) and not in VALUE. "
              "Apple's mask colour stays CANNOT DETERMINE and the drawn "
              "black is a CHOICE inside the measured bound.")
        code = 0
    if not break_green:
        json.dump({"tool": "tools/f_render.py", "results": results,
                   "verdict": "FAIL" if worst else "PASS"},
                  open(os.path.join(OUT, "render-check.json"), "w"), indent=1)
    return code


sys.exit(main())
