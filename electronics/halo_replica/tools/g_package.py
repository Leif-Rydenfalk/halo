#!/usr/bin/env python3
"""g_package - cut a fabrication package from a routed board, and verify it.

    python3 tools/g_package.py <board.kicad_pcb> <outdir> [--thickness 0.4 0.8]

Writes gerbers with THE 13 FABRICATION LAYERS NAMED EXPLICITLY, an Excellon drill,
a README stub, and one zip per thickness. Then runs z_fabcheck on each zip.

WHY THE LAYERS ARE NAMED. A default `kicad-cli pcb export gerbers` with no --layers
wrote User layers and NO COPPER, and the directory looked complete: plausible names,
non-zero sizes, twenty-odd files. That package would have been uploaded.
"""
import os, re, subprocess, sys, zipfile, shutil, json

# ---------------------------------------------------------------------------
# WHAT JLCPCB WILL ACTUALLY ACCEPT, MEASURED IN THEIR LIVE QUOTE CONFIGURATOR
# on 2026-09-05 — not read off a capability page, because the capability page
# does not resolve it. It lists FR4 generally as 0.4/0.6/0.8/1.0/1.2/1.6/2.0 AND
# lists four-layer as 0.8/1.0/1.2/1.6, and those two statements disagree.
#
# Measured by uploading a real package and reading the Thickness row:
#   4 layers -> 0.8 1.0 1.2 1.6 2.0     0.4 and 0.6 GREYED OUT
#   2 layers -> 0.4 0.8 1.0 1.2 1.6 2.0        0.6 greyed
# Negative control: clicking 0.4mm at 4 layers does nothing, the selection stays
# on 1.6 — it is disabled, not merely unstyled.
# Positive control: switching 4 -> 2 layers RE-ENABLES 0.4mm in the same page
# with no reload, so the disable tracks layer count and is a real constraint.
#
# This exists because a zip named "jlc_0.4mm" for a 4-layer board is a file that
# gets uploaded and refused. Refusing to write it here is cheaper than finding
# out at the vendor.
JLC_THICKNESS = {2: {"0.4","0.8","1.0","1.2","1.6","2.0"},
                 4: {"0.8","1.0","1.2","1.6","2.0"}}
JLC_MEASURED  = "2026-09-05, live cart.jlcpcb.com/quote configurator"

LAYERS = ["F.Cu","In1.Cu","In2.Cu","B.Cu","F.Mask","B.Mask",
          "F.Silkscreen","B.Silkscreen","F.Paste","B.Paste","Edge.Cuts","F.Fab","B.Fab"]
PCB = os.path.expanduser("~/dev/ce-workshop/ce-pcb/bin/pcb")

def run(*a):
    r = subprocess.run(list(a), capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)

def main():
    if len(sys.argv) < 3:
        print(__doc__); return 2
    board, outdir = sys.argv[1], sys.argv[2]
    ths = sys.argv[sys.argv.index("--thickness")+1:] if "--thickness" in sys.argv else ["0.8"]
    allow = "--allow-unorderable" in sys.argv
    ths = [t for t in ths if not t.startswith("--")]
    n_layers = 4
    okset = JLC_THICKNESS.get(n_layers)
    bad = [t for t in ths if okset and t not in okset]
    if bad and not allow:
        print(f"REFUSED: {', '.join(bad)} mm is NOT orderable at {n_layers} layers "
              f"at JLCPCB.\n"
              f"  Measured {JLC_MEASURED}: at {n_layers} layers the Thickness row "
              f"offers {' '.join(sorted(okset))} and greys out the rest.\n"
              f"  Clicking the greyed value does nothing; switching to 2 layers "
              f"re-enables 0.4, so it is a real constraint and not styling.\n"
              f"  Orderable here: {' '.join(sorted(okset))}\n"
              f"  PCBWay documents 0.40 mm at 4 layers (medium difficulty) — that is a\n"
              f"  DOCUMENTATION claim, never put through their order form. If you want\n"
              f"  the package anyway for a different vendor: --allow-unorderable")
        return 1
    if bad and allow:
        print(f"NOTE: writing {', '.join(bad)} mm although JLCPCB does not offer it at "
              f"{n_layers} layers (measured {JLC_MEASURED}). For another vendor only.")
    if not os.path.exists(board): print(f"CANNOT DETERMINE: no board at {board}"); return 2
    gdir = os.path.join(outdir, "gerber")
    shutil.rmtree(gdir, ignore_errors=True); os.makedirs(gdir, exist_ok=True)

    c, o = run(PCB, "--cli", "pcb", "export", "gerbers", "--layers", ",".join(LAYERS),
               "--output", gdir, board)
    n = o.count("Plotted")
    print(f"GERBERS  exit {c}, {n} layers plotted")
    if c != 0 or n < len(LAYERS):
        print(o[-600:]); print(f"FAIL: expected {len(LAYERS)} layers, got {n}"); return 1

    c, o = run(PCB, "--cli", "pcb", "export", "drill", "--output", gdir, board)
    print(f"DRILL    exit {c}")
    if c != 0: print(o[-400:]); return 1

    # every copper layer must carry apertures, checked HERE as well as in the zip
    import re
    empty = []
    for f in os.listdir(gdir):
        if not re.search(r"\.(gtl|gbl|g1|g2)$", f, re.I): continue
        t = open(os.path.join(gdir, f), errors="ignore").read()
        if len(re.findall(r"D0[13]\*", t)) + len(re.findall(r"G36\*", t)) == 0:
            empty.append(f)
    if empty:
        print(f"FAIL: copper layers present but EMPTY: {empty}"); return 1
    print(f"COPPER   all copper layers carry apertures")

    zips = []
    # THE RULES THE BOARD ACTUALLY CARRIES, read from it rather than typed here.
    # ORDER-SETTINGS.txt used to state "min via 0.25 mm pad / 0.15 mm drill" as a
    # literal while the board carried 0.6 / 0.3 — a constant in a document that
    # nothing forced to agree with the artifact, which is the same defect as the
    # 1.6 mm thickness one level up. A fabricator reads the file; the file must
    # read the board.
    rules = {}
    rr = os.path.join(os.path.dirname(board),
                      os.path.basename(board).replace(".kicad_pcb", ".kicad_pro"))
    if os.path.exists(rr):
        try:
            pro = json.load(open(rr))
            dr = (pro.get("board", {}) or {}).get("design_settings", {}) or {}
            rl = dr.get("rules", {}) or {}
            for k, lbl in (("min_clearance", "clearance"),
                           ("min_track_width", "track"),
                           ("min_via_diameter", "via"),
                           ("min_through_hole_diameter", "via_drill")):
                if rl.get(k) is not None: rules[lbl] = float(rl[k])
        except Exception as e:
            print("RULES    CANNOT DETERMINE: %s" % e)
    # AND WHAT THE COPPER ACTUALLY CONTAINS. The rules above come from the
    # .kicad_pro sitting beside the board, which can be STALE relative to the
    # copper: restoring a routed board without its project file made
    # ORDER-SETTINGS.txt state "via 0.450 mm" over a board whose 58 vias are all
    # 0.6/0.3. A document that reads a SETTING is one file away from the artifact;
    # measuring the tracks and vias is not.
    import re as _re
    _t = open(board, errors="ignore").read()
    # KiCad 10 writes each via across several lines, so this must span newlines.
    _vias = _re.findall(r'\(via\b.*?\(size ([\d.]+)\).*?\(drill ([\d.]+)\)', _t, _re.S)
    _seg = sorted({m for m in _re.findall(r'\(segment\b.*?\(width ([\d.]+)\)', _t, _re.S)},
                  key=float)
    measured = ""
    if _vias:
        _vs = sorted({(a, b) for a, b in _vias}, key=lambda z: float(z[0]))
        measured += ("  vias IN COPPER  %d, sizes %s   (MEASURED off the board)\n"
                     % (len(_vias), ", ".join("%s/%s mm" % v for v in _vs)))
        if rules.get("via") and abs(float(_vs[0][0]) - rules["via"]) > 1e-6:
            measured += ("  ** the project file says via %.3f mm and the COPPER "
                         "says %s mm - trust the copper **\n"
                         % (rules["via"], _vs[0][0]))
    if _seg:
        measured += ("  track widths    %s mm   (MEASURED off the board)\n"
                     % ", ".join(_seg))
    if _vias or _seg:
        print("COPPER   %d vias, %d distinct track width(s), measured from the board"
              % (len(_vias), len(_seg)))

    if rules:
        rules_txt = ""
        if "clearance" in rules:
            rules_txt += ("  min trace/space %.3f mm   (READ FROM THE BOARD)\n"
                          % rules["clearance"])
        else:
            rules_txt += "  min trace/space CANNOT DETERMINE — the board states none\n"
        if "track" in rules:
            rules_txt += ("  min track width %.3f mm   (READ FROM THE BOARD)\n"
                          % rules["track"])
        if "via" in rules and "via_drill" in rules:
            rules_txt += ("  min via         %.3f mm pad / %.3f mm drill   "
                          "(READ FROM THE BOARD)\n"
                          % (rules["via"], rules["via_drill"]))
        print("RULES    read from the board: " +
              ", ".join("%s %.3f mm" % (k, v) for k, v in sorted(rules.items())))
    else:
        rules_txt = ("  min trace/space CANNOT DETERMINE — the board states no "
                     "design rules\n")
        measured = measured if "measured" in dir() else ""
        print("RULES    CANNOT DETERMINE: no rules found in the .kicad_pro — "
              "ORDER-SETTINGS will say so rather than state a number")

    # ---- ASSEMBLY FILES: gerbers say what the BARE BOARD is, and nothing more.
    # An assembly order also needs a CPL (where each part goes) and a BOM (what
    # to solder on). Without them the order is a bare-board order wearing an
    # assembly filename.
    cpl_src = os.path.join(gdir, "..", "cpl-kicad.csv")
    rc, _o = run(PCB, "--cli", "pcb", "export", "pos", board,
                 "-o", cpl_src, "--format", "csv", "--units", "mm",
                 "--side", "both", "--use-drill-file-origin")
    cpl_rows = []
    if rc == 0 and os.path.exists(cpl_src):
        import csv as _csv
        with open(cpl_src) as fh:
            for r in _csv.DictReader(fh):
                k = {c.lower().strip(): v for c, v in r.items() if c}
                ref = k.get("ref") or k.get("designator") or ""
                if not ref: continue
                side = (k.get("side") or "top").lower()
                cpl_rows.append([ref, k.get("posx") or k.get("midx") or "",
                                 k.get("posy") or k.get("midy") or "",
                                 "top" if side.startswith("t") else "bottom",
                                 k.get("rot") or k.get("rotation") or "0"])
        print(f"CPL      {len(cpl_rows)} placements exported")
    else:
        print("CPL      CANNOT DETERMINE: kicad-cli export pos failed - the "
              "package will be BARE BOARD ONLY, not assembly-ready")

    # THE BOM TRAP, and it is silent and expensive: JLCPCB's importer reads the
    # LCSC column LITERALLY. A cell saying "CANNOT DETERMINE - no price pull was
    # done" matches no part, and THE LINE IS DROPPED FROM THE ASSEMBLY WITH NO
    # ERROR ANYWHERE - the board comes back with parts missing. A non-answer must
    # be an EMPTY cell and a counted refusal, never prose in a part-number field.
    bom_src = None
    for cand in ("out/schematic-fab/halo_replica_fab-bom-resolved.csv",
                 "out/schematic-fab/halo_replica_fab-bom.csv"):
        c = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), cand)
        if os.path.exists(c): bom_src = c; break
    bom_txt, bom_named, bom_blank, bom_prose = None, 0, 0, []
    if bom_src:
        import csv as _csv
        with open(bom_src) as fh:
            rows = list(_csv.reader(fh))
        hdr = rows[0]
        li = next((i for i, c in enumerate(hdr) if "lcsc" in c.lower()), None)
        for r in rows[1:]:
            if li is None or li >= len(r): continue
            v = r[li].strip()
            if not v: bom_blank += 1
            elif re.match(r"^C\d+$", v): bom_named += 1
            else: bom_prose.append((r[1] if len(r) > 1 else "?", v[:40]))
        bom_txt = open(bom_src).read()
        print(f"BOM      {bom_named} lines carry a real LCSC code, {bom_blank} "
              f"blank (an honest refusal), {len(bom_prose)} carry prose")


    for th in ths:
        z = os.path.join(outdir, f"halo_replica_jlc_{th}mm.zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(os.listdir(gdir)):
                zf.write(os.path.join(gdir, f), f)
            zf.writestr("ORDER-SETTINGS.txt",
                f"halo Replica FAB VARIANT\n"
                f"  layers          4\n"
                f"  thickness       {th} mm   <-- SELECT THIS AT ORDER TIME\n"
                f"  Apple's board   0.30 mm   (delta {float(th)-0.30:+.2f} mm; see fab/README.md)\n"
                f"  surface finish  ENIG preferred (Apple's is gold-bearing; measured, see stackup.json)\n"
                f"{rules_txt}{measured}"
                f"\nORDERABLE AT JLCPCB AT 4 LAYERS: "
                f"{' '.join(sorted(JLC_THICKNESS[4]))} mm\n"
                f"  measured {JLC_MEASURED} — 0.4 and 0.6 mm are greyed out at 4\n"
                f"  layers and clicking them does nothing; they re-enable at 2 layers.\n"
                f"  Selecting 0.4 mm also FORCES ENIG (HASL is greyed — you cannot\n"
                f"  hot-air-level a board that thin), collapses Material Type to\n"
                f"  FR4 TG135 alone, and took a 5-off order from $4.10 to about $66.\n"
                f"\nWHAT THIS PACKAGE CAN AND CANNOT ORDER\n"
                f"  BARE BOARD:  ready. Gerbers + Excellon drill, {len(cpl_rows)} "
                f"parts placed.\n"
                f"  ASSEMBLY:    NOT ready. The BOM carries {bom_named} real LCSC "
                f"code(s) and {bom_blank} blank.\n"
                f"               A blank cell is an HONEST REFUSAL, not an "
                f"oversight: no price pull\n"
                f"               was done for those lines. Each names the exact "
                f"MPN a human must look\n"
                f"               up. Do NOT invent codes to fill them.\n"
                f"               JLCPCB's importer reads the LCSC column "
                f"LITERALLY - a cell holding\n"
                f"               prose matches no part and THE LINE IS DROPPED "
                f"FROM THE ASSEMBLY WITH\n"
                f"               NO ERROR ANYWHERE. The board comes back with "
                f"parts missing. That is\n"
                f"               why they are blank rather than explanatory.\n"
                f"\nNOBODY HAS BUILT ONE. This board has never been powered on.\n")
            if cpl_rows:
                import io as _io
                sio = _io.StringIO()
                sio.write("Designator,Mid X,Mid Y,Layer,Rotation\n")
                for r in cpl_rows:
                    sio.write("%s,%s,%s,%s,%s\n" % tuple(r))
                zf.writestr("halo_replica_fab-cpl.csv", sio.getvalue())
            if bom_txt:
                zf.writestr("halo_replica_fab-bom.csv", bom_txt)
        zips.append(z); print(f"ZIP      {z}  ({os.path.getsize(z)/1024:.0f} KB)")

    ok = True
    fc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "z_fabcheck.py")
    for z in zips:
        c, o = run(sys.executable, fc, z)
        print(f"\nz_fabcheck {os.path.basename(z)}: exit {c}")
        for line in o.strip().splitlines()[-9:]: print("   " + line)
        ok = ok and c == 0
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
