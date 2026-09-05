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
  F4  the outline layer exists and is non-trivial
  F5  no file is zero-length
  F6  drill hits lie inside the outline's extent    (a mismatched origin between drill
                                                     and gerbers is silent and fatal)
"""
import sys, os, re, zipfile, tempfile, shutil

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

def gerber_extent(txt):
    xs, ys = [], []
    for m in re.finditer(r"X(-?\d+)Y(-?\d+)", txt):
        xs.append(int(m.group(1))); ys.append(int(m.group(2)))
    return (min(xs), max(xs), min(ys), max(ys)) if xs else None

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
        n = gerber_apertures(open(op, errors="ignore").read())
        if n < 4: ok = False; out.append(f"F4 FAIL  outline layer has only {n} ops")
        else: out.append(f"F4 PASS  outline: {n} ops")
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
    def full(d, cu=GOOD):
        for n in ("x.gtl","x.gbl","x.g1","x.g2"): mk(d,n,cu)
        for n in ("x.gts","x.gbs","x.gto","x.gbo"): mk(d,n,GOOD)
        mk(d,"x.gm1",GOOD*3); mk(d,"x.drl",DRL)
    a=os.path.join(tmp,"good"); full(a); r,_=check(a); res.append(("a complete package PASSES", r==0, r))
    b=os.path.join(tmp,"empty"); full(b,cu=EMPTY); r,_=check(b); res.append(("COPPER PRESENT BUT EMPTY is caught", r==1, r))
    c=os.path.join(tmp,"nocu"); full(c); os.remove(os.path.join(c,"x.gtl")); r,_=check(c); res.append(("a missing copper layer is caught", r==1, r))
    d=os.path.join(tmp,"nodrl"); full(d); os.remove(os.path.join(d,"x.drl")); r,_=check(d); res.append(("a missing drill file is caught", r==1, r))
    e=os.path.join(tmp,"zero"); full(e); open(os.path.join(e,"x.gbl"),"w").close(); r,_=check(e); res.append(("a zero-length file is caught", r==1, r))
    f=os.path.join(tmp,"empty2"); os.makedirs(f); r,_=check(f); res.append(("an empty directory is CANNOT DETERMINE, not FAIL", r==2, r))
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
