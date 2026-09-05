#!/usr/bin/env python3
"""g_package - cut a fabrication package from a routed board, and verify it.

    python3 tools/g_package.py <board.kicad_pcb> <outdir> [--thickness 0.4 0.8]

Writes gerbers with THE 13 FABRICATION LAYERS NAMED EXPLICITLY, an Excellon drill,
a README stub, and one zip per thickness. Then runs z_fabcheck on each zip.

WHY THE LAYERS ARE NAMED. A default `kicad-cli pcb export gerbers` with no --layers
wrote User layers and NO COPPER, and the directory looked complete: plausible names,
non-zero sizes, twenty-odd files. That package would have been uploaded.
"""
import os, subprocess, sys, zipfile, shutil, json

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
    ths = sys.argv[sys.argv.index("--thickness")+1:] if "--thickness" in sys.argv else ["0.4","0.8"]
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
                f"  min trace/space 0.09/0.09 mm or wider — inside JLC's 4-layer capability\n"
                f"  min via         0.25 mm pad / 0.15 mm drill\n"
                f"\nNOBODY HAS BUILT ONE. This board has never been powered on.\n")
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
