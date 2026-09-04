#!/usr/bin/env python3
"""stl_bbox.py — read a binary STL back and report its bounding box.

    python3 tools/stl_bbox.py out/mech/*.stl

Stdlib only, and deliberately independent of ce-cad: it reads the file a
manufacturer would receive, not the solid the design believes it exported.
An exported file nobody read back is a file nobody has checked.
"""
import struct
import sys


def bbox(path):
    with open(path, "rb") as f:
        head = f.read(84)
        if len(head) < 84:
            return None, "shorter than an STL header"
        n = struct.unpack("<I", head[80:84])[0]
        data = f.read()
    if len(data) != n * 50:
        return None, ("header claims %d triangles = %d bytes, file carries %d"
                      % (n, n * 50, len(data)))
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    for i in range(n):
        vs = struct.unpack_from("<12f", data, i * 50)[3:12]
        for k in range(3):
            for a in range(3):
                v = vs[k * 3 + a]
                lo[a] = min(lo[a], v)
                hi[a] = max(hi[a], v)
    return (n, [round(hi[a] - lo[a], 4) for a in range(3)],
            [round(lo[a], 4) for a in range(3)],
            [round(hi[a], 4) for a in range(3)]), None


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        r, why = bbox(p)
        if r is None:
            print("CANNOT DETERMINE  %-44s %s" % (p.split("/")[-1], why))
            bad += 1
            continue
        n, size, lo, hi = r
        print("%-44s %7d tris  size %-26s z %.3f..%.3f"
              % (p.split("/")[-1], n, "x".join("%.3f" % v for v in size),
                 lo[2], hi[2]))
    sys.exit(1 if bad else 0)
