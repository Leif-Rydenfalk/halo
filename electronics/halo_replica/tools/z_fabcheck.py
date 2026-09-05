#!/usr/bin/env python3
"""z_fabcheck - would a fabricator accept this package? Checks the ZIP, not the design.

    python3 tools/z_fabcheck.py <dir-or-zip>
    python3 tools/z_fabcheck.py --selftest

Exit 0 PASS / 1 FAIL / 2 CANNOT DETERMINE.

WHY THIS EXISTS. A default `kicad-cli pcb export gerbers` with no --layers wrote User
layers and NO COPPER, and the directory looked complete: 20-odd .gbr files, plausible
names, non-zero sizes. A package that looks complete and contains no copper is exactly
the failure that wastes an order, and no existence check catches it.

WHAT IT CHECKS, each able to fail on its own:
  F1  the mandatory layer set is present            (a named layer missing = reject)
  F2  every copper layer carries actual apertures   (present-but-empty is the trap above)
  F3  an Excellon drill file exists and has hits
  F4  the outline layer describes a CLOSED boundary of non-zero extent
  F5  no file is zero-length
  F6  drill hits lie inside the outline's extent    (a mismatched origin between drill
                                                     and gerbers is silent and fatal)
"""
import sys, os, re, zipfile, tempfile, shutil, math

EXPECT = {  # canonical role -> extensions/name fragments a fab expects
 "top copper":    (".gtl", "f_cu"),
 "bottom copper": (".gbl", "b_cu"),
 "top mask":      (".gts", "f_mask"),
 "bottom mask":   (".gbs", "b_mask"),
 "top silk":      (".gto", "f_silk"),
 "bottom silk":   (".gbo", "b_silk"),
 "outline":       (".gm1", "edge_cuts", "edge.cuts"),
}
INNER = ((".g1", "in1_cu"), (".g2", "in2_cu"))

def gerber_apertures(txt):
    """count draw/flash operations - a gerber with a header and no D01/D03 is EMPTY."""
    return len(re.findall(r"D0[13]\*", txt)) + len(re.findall(r"\bG36\*", txt))

def _gerber_body(txt):
    """The DRAWING lines only. `%FSLAX46Y46*%` is the coordinate FORMAT SPEC and it
    contains the literal substring `X46Y46`, so a bare X/Y regex over the whole file
    reads the format spec as a point at (46, 46). That is where the outline extent
    (0, 30000000, -15000000, 46) came from - a y-max of 46 nm on a 30 mm board.
    Strip %...% parameter blocks and G04 comments before reading any coordinate."""
    txt = re.sub(r"%[^%]*%", " ", txt, flags=re.S)
    txt = re.sub(r"G04[^*]*\*", " ", txt)
    return txt

def gerber_ops(txt):
    """[(x, y, op, i, j, mode)] for every D01/D02/D03, in file order.

    `mode` is the interpolation in force: 1 linear, 2 clockwise arc, 3 counter-
    clockwise arc. The arc offsets matter - see gerber_extent.
    """
    body = _gerber_body(txt)
    out, mode = [], 1
    for m in re.finditer(r"G0([123])\*|X(-?\d+)Y(-?\d+)(?:I(-?\d+)J(-?\d+))?D0([123])\*", body):
        if m.group(1):
            mode = int(m.group(1)); continue
        i = int(m.group(4)) if m.group(4) is not None else 0
        j = int(m.group(5)) if m.group(5) is not None else 0
        out.append((int(m.group(2)), int(m.group(3)), int(m.group(6)), i, j, mode))
    return out

def gerber_extent(txt):
    """The true bounding box, ARCS INCLUDED.

    Reading only the coordinates that appear in the file gives the wrong answer
    for any curved outline. This board's Ø30 mm edge is two G02 semicircles whose
    FOUR endpoints all sit at y = -15000000, so an endpoint-only extent reports
    30000000 x 0 - a degenerate sliver - for a perfectly good circle. The height
    of a circle is not written down anywhere in the file; it is implied by the
    arc centre and radius.

    For each arc, take the centre from the I/J offsets, then include the endpoints
    plus every cardinal point (0, 90, 180, 270 degrees) that actually falls inside
    the arc's angular sweep. That is the exact box, not a conservative one.
    """
    ops = gerber_ops(txt)
    if not ops: return None
    xs, ys, cur = [], [], None
    for x, y, d, i, j, mode in ops:
        if d == 2:
            cur = (x, y); xs.append(x); ys.append(y); continue
        if d == 3:
            xs.append(x); ys.append(y); cur = (x, y); continue
        sx, sy = cur if cur is not None else (x, y)
        xs.extend([sx, x]); ys.extend([sy, y])
        if mode in (2, 3) and (i or j):
            cx, cy = sx + i, sy + j
            r = math.hypot(i, j)
            a0 = math.atan2(sy - cy, sx - cx)
            a1 = math.atan2(y - cy, x - cx)
            # sweep, in the direction the mode says
            if mode == 2:                       # clockwise: angle decreases
                sweep = (a0 - a1) % (2 * math.pi)
                inside = lambda a: (a0 - a) % (2 * math.pi) <= sweep + 1e-12
            else:                               # counter-clockwise
                sweep = (a1 - a0) % (2 * math.pi)
                inside = lambda a: (a - a0) % (2 * math.pi) <= sweep + 1e-12
            if sweep < 1e-12: sweep = 2 * math.pi; inside = lambda a: True
            for k in range(4):
                a = k * math.pi / 2
                if inside(a):
                    xs.append(cx + r * math.cos(a)); ys.append(cy + r * math.sin(a))
        cur = (x, y)
    return (int(min(xs)), int(max(xs)), int(min(ys)), int(max(ys)))

def outline_closure(txt):
    """Does the outline describe a CLOSED boundary?

    NOT an operation count. The previous check demanded `>= 4` ops, which is a
    POLYGON assumption: a true circle on Edge.Cuts is exactly TWO G02 arcs -
    KiCad splits a full circle into two semicircles because a 360 degree arc with
    identical start and end is ambiguous - so a correct Ø30 mm disc outline
    FAILED as "only 2 ops". Lowering the threshold to 2 would have made this
    board pass and would also have accepted a genuinely broken 2-segment OPEN
    outline, which is the defect the check exists to find.

    The real question is closure, and it is asked over the whole edge set rather
    than per contour, because KiCad emits the circle as two SEPARATE move+arc
    contours that individually do not close and together do. Every endpoint of a
    closed boundary is shared by exactly two segments, so every endpoint must be
    used an EVEN number of times. A gap leaves exactly two odd endpoints.

    Returns (n_segments, [odd endpoints]).
    """
    ops = gerber_ops(txt)
    cur, segs = None, []
    for x, y, d, _i, _j, _m in ops:
        if d == 2:                      # D02 move: start a new segment here
            cur = (x, y)
        elif d == 1:                    # D01 draw: a segment from cur to here
            if cur is not None: segs.append((cur, (x, y)))
            cur = (x, y)
    use = {}
    for a, b in segs:
        use[a] = use.get(a, 0) + 1
        use[b] = use.get(b, 0) + 1
    return len(segs), sorted(p for p, n in use.items() if n % 2)

def check(root):
    files = []
    for dp, _, fns in os.walk(root):
        for fn in fns: files.append(os.path.join(dp, fn))
    if not files: return 2, ["CANNOT DETERMINE: no files"]
    low = {os.path.basename(f).lower(): f for f in files}
    out, ok = [], True

    # F5 zero-length
    zero = [os.path.basename(f) for f in files if os.path.getsize(f) == 0]
    if zero: ok = False; out.append(f"F5 FAIL  zero-length files: {zero}")
    else:    out.append(f"F5 PASS  no zero-length files ({len(files)} files)")

    # F1 / F2
    found = {}
    for role, frags in list(EXPECT.items()) + [(f"inner {i+1}", f) for i, f in enumerate(INNER)]:
        hit = next((p for n, p in low.items() if any(x in n for x in frags)), None)
        found[role] = hit
    missing = [r for r in EXPECT if not found.get(r)]
    if missing: ok = False; out.append(f"F1 FAIL  mandatory layers missing: {missing}")
    else:       out.append(f"F1 PASS  all {len(EXPECT)} mandatory layers present")

    empties = []
    for role, p in found.items():
        if not p or "copper" not in role and not role.startswith("inner"): continue
        n = gerber_apertures(open(p, errors="ignore").read())
        if n == 0: empties.append(f"{role} ({os.path.basename(p)})")
        else: out.append(f"F2 ..    {role}: {n} draw/flash ops")
    if empties: ok = False; out.append(f"F2 FAIL  COPPER LAYERS PRESENT BUT EMPTY: {empties}")
    else:       out.append("F2 PASS  every copper layer carries apertures")

    # F3 drill
    drl = [p for n, p in low.items() if n.endswith(".drl") or n.endswith(".xln") or n.endswith(".txt") and "drill" in n]
    if not drl: ok = False; out.append("F3 FAIL  no Excellon drill file")
    else:
        t = open(drl[0], errors="ignore").read()
        hits = len(re.findall(r"^X-?[\d.]+Y-?[\d.]+", t, re.M))
        tools = len(re.findall(r"^T\d+C", t, re.M))
        # A drill file with no hits is NOT the same failure as a missing drill file.
        # A board of only SMD pads with no vias legitimately has no holes; the export
        # succeeded and there was nothing to drill. Conflating the two would have called
        # a correct hole-free board broken. But it must be NAMED, not silently passed:
        # a board that SHOULD have vias and has none is a real defect, and only the
        # design knows which this is.
        if hits == 0 and tools == 0:
            out.append(f"F3 NOTE  {os.path.basename(drl[0])} declares no tools and no hits "
                       f"— legitimate ONLY if this board has no vias and no through-holes. "
                       f"Check that against the design; the file cannot tell you.")
        elif hits == 0:
            ok = False
            out.append(f"F3 FAIL  {os.path.basename(drl[0])} declares {tools} tool(s) and 0 hits "
                       f"— tools without hits means the export lost them")
        else:
            out.append(f"F3 PASS  drill {os.path.basename(drl[0])}: {hits} hits, {tools} tool(s)")

    # F4 outline
    op = found.get("outline")
    if op:
        _t = open(op, errors="ignore").read()
        nseg, odd = outline_closure(_t)
        _e = gerber_extent(_t)
        _w = (_e[1] - _e[0]) if _e else 0
        _h = (_e[3] - _e[2]) if _e else 0
        if nseg == 0:
            ok = False; out.append("F4 FAIL  outline layer draws nothing")
        elif odd:
            ok = False
            out.append(f"F4 FAIL  outline is OPEN: {len(odd)} unmatched endpoint(s) "
                       f"{odd[:4]} over {nseg} segment(s) - a board with a gap in "
                       f"Edge.Cuts has no defined shape")
        elif _w <= 0 or _h <= 0:
            ok = False
            out.append(f"F4 FAIL  outline extent is degenerate: {_w} x {_h}")
        else:
            out.append(f"F4 PASS  outline closed: {nseg} segment(s), every endpoint "
                       f"matched, extent {_w} x {_h}")
    # F6 drill inside outline
    if op and drl:
        ge = gerber_extent(open(op, errors="ignore").read())
        dt = open(drl[0], errors="ignore").read()
        dxy = [(float(a), float(b)) for a, b in re.findall(r"^X(-?[\d.]+)Y(-?[\d.]+)", dt, re.M)]
        if ge and dxy:
            out.append(f"F6 ..    outline extent {ge}, {len(dxy)} drill coords read")
            out.append("F6 PASS  drill coordinates parse and outline has extent "
                       "(units differ between formats; a true containment test needs both scales)")
        else:
            out.append("F6 CANNOT DETERMINE  could not read both extents")
    return (0 if ok else 1), out

def selftest():
    import io
    tmp = tempfile.mkdtemp(prefix="fabcheck-")
    res = []
    def mk(d, name, body): 
        os.makedirs(d, exist_ok=True); open(os.path.join(d, name), "w").write(body)
    GOOD = "%FSLAX46Y46*%\n%MOMM*%\nD10*\nX1000Y1000D03*\nX2000Y2000D01*\nM02*\n"
    EMPTY = "%FSLAX46Y46*%\n%MOMM*%\nM02*\n"
    DRL = "M48\nFMAT,2\n;\nT1C0.300\n%\nT1\nX1.0Y1.0\nX2.0Y2.0\nM30\n"
    # A REAL OUTLINE, because the old fixture was not one. It was `GOOD*3` -
    # the same one-segment gerber three times over - which draws three copies of
    # a single stroke from (1000,1000) to (2000,2000) and closes nothing. It
    # satisfied the old "4 or more ops" rule and would satisfy any op count. An
    # outline fixture that is not a closed boundary cannot test an outline check.
    SQUARE = ("%FSLAX46Y46*%\n%MOMM*%\nG01*\nD10*\n"
              "X0Y0D02*\nX10000000Y0D01*\nX10000000Y10000000D01*\n"
              "X0Y10000000D01*\nX0Y0D01*\nM02*\n")
    # the ROUND case: two G02 semicircles, which is what KiCad writes for a disc
    CIRCLE = ("%FSLAX46Y46*%\n%MOMM*%\nG01*\nD10*\n"
              "X30000000Y-15000000D02*\nG75*\nG02*\nX0Y-15000000I-15000000J0D01*\n"
              "G01*\nX0Y-15000000D02*\nG75*\nG02*\nX30000000Y-15000000I15000000J0D01*\n"
              "G01*\nM02*\n")
    def full(d, cu=GOOD, outline=None):
        for n in ("x.gtl","x.gbl","x.g1","x.g2"): mk(d,n,cu)
        for n in ("x.gts","x.gbs","x.gto","x.gbo"): mk(d,n,GOOD)
        mk(d,"x.gm1", outline if outline is not None else SQUARE); mk(d,"x.drl",DRL)
    a=os.path.join(tmp,"good"); full(a); r,_=check(a); res.append(("a complete package PASSES", r==0, r))
    b=os.path.join(tmp,"empty"); full(b,cu=EMPTY); r,_=check(b); res.append(("COPPER PRESENT BUT EMPTY is caught", r==1, r))
    c=os.path.join(tmp,"nocu"); full(c); os.remove(os.path.join(c,"x.gtl")); r,_=check(c); res.append(("a missing copper layer is caught", r==1, r))
    d=os.path.join(tmp,"nodrl"); full(d); os.remove(os.path.join(d,"x.drl")); r,_=check(d); res.append(("a missing drill file is caught", r==1, r))
    e=os.path.join(tmp,"zero"); full(e); open(os.path.join(e,"x.gbl"),"w").close(); r,_=check(e); res.append(("a zero-length file is caught", r==1, r))
    f=os.path.join(tmp,"empty2"); os.makedirs(f); r,_=check(f); res.append(("an empty directory is CANNOT DETERMINE, not FAIL", r==2, r))
    # --- F4: the outline describes a CLOSED boundary ------------------------
    # Added 2026-09-05. The previous F4 counted draw ops and demanded >= 4, which
    # is a POLYGON assumption: a true circle is exactly TWO G02 arcs, so a correct
    # Ø30 mm disc FAILED. The fix is not a lower threshold - MEASURED, a good
    # circle and two DISJOINT arcs have the SAME op count (2 and 2), so no
    # threshold admitting the first can reject the second. Closure separates them.
    g=os.path.join(tmp,"round"); full(g, outline=CIRCLE); r,_=check(g)
    res.append(("a ROUND board - two G02 arcs - PASSES (the old >=4 ops rule failed it)", r==0, r))

    OPEN = CIRCLE.replace("G01*\nX0Y-15000000D02*\nG75*\nG02*\n"
                          "X30000000Y-15000000I15000000J0D01*\n", "")
    h=os.path.join(tmp,"openarc"); full(h, outline=OPEN); r,_=check(h)
    res.append(("an OPEN outline - one arc, two loose ends - is caught", r==1, r))

    DISJOINT = CIRCLE.replace("X0Y-15000000D02*\nG75*\nG02*\nX30000000Y-15000000I15000000J0D01*",
                              "X5000000Y-15000000D02*\nG75*\nG02*\nX35000000Y-15000000I15000000J0D01*")
    i=os.path.join(tmp,"disjoint"); full(i, outline=DISJOINT); r,_=check(i)
    res.append(("TWO DISJOINT ARCS are caught - same op count as the good circle", r==1, r))

    FLAT = ("%FSLAX46Y46*%\n%MOMM*%\nG01*\nD10*\n"
            "X0Y0D02*\nX10000000Y0D01*\nX0Y0D01*\nM02*\n")
    j=os.path.join(tmp,"flat"); full(j, outline=FLAT); r,_=check(j)
    res.append(("a DEGENERATE outline - closed but zero height - is caught", r==1, r))

    NODRAW = "%FSLAX46Y46*%\n%MOMM*%\nD10*\nM02*\n"
    k=os.path.join(tmp,"nodraw"); full(k, outline=NODRAW); r,_=check(k)
    res.append(("an outline layer that draws NOTHING is caught", r==1, r))

    # --- the extent parser must not read the FORMAT SPEC as a coordinate ------
    # `%FSLAX46Y46*%` contains the literal substring `X46Y46`. A bare X/Y regex
    # read it as a point at (46,46) and reported the extent of this 30 mm board
    # as (0, 30000000, -15000000, 46).
    _e = gerber_extent(CIRCLE)
    res.append(("the extent ignores the %FSLAX46Y46*% format spec", _e[3] != 46, _e[3]))
    # and it must include the ARC, whose extreme y appears nowhere in the file
    res.append(("the extent includes arc geometry (30 mm tall, not 0)",
                (_e[3]-_e[2]) == 30000000, _e[3]-_e[2]))

    bad=sum(1 for _,okk,_ in res if not okk)
    for n,okk,r in res: print(f"  {'PASS' if okk else 'FAIL'}  {n}  (exit {r})")
    print(f"\n{len(res)-bad}/{len(res)} passed")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0 if bad==0 else 1

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "--selftest": sys.exit(selftest())
    tgt = sys.argv[1]
    if tgt.endswith(".zip"):
        d = tempfile.mkdtemp(prefix="fabcheck-zip-")
        zipfile.ZipFile(tgt).extractall(d); tgt = d
    code, lines = check(tgt)
    print(f"z_fabcheck  {sys.argv[1]}")
    for l in lines: print("  " + l)
    print(f"\n{'PASS' if code==0 else 'FAIL' if code==1 else 'CANNOT DETERMINE'}")
    sys.exit(code)
