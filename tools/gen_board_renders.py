#!/usr/bin/env python3
"""Board renders — lane G2 (what Leif sees).

    python3 tools/gen_board_renders.py            # render, then measure
    python3 tools/gen_board_renders.py --check    # render nothing, just report

Renders the board KiCad holds RIGHT NOW into out/render/, and writes
out/render/board-renders.json recording, for every image:

    the .kicad_pcb it was rendered from, and that file's mtime
    the mtime of electronics/halo_rev_a/board.py, which GENERATES that pcb
    whether the render is CURRENT with respect to both

WHY THIS FILE EXISTS. out/render/halo_rev_a-top.png was made ad hoc at
2026-09-04 22:02 and then shown on the gallery for a day while the board
under it changed: nine-tooth antenna, the NFC coil moved off the arm, the
ground planes cut back, 81 unconnected items routed down to 28. A stale
render presented as current is the same defect as a stale gerber, and this
project shipped one of those on 2026-09-05.

So the rule here is not "render often". It is: EVERY RENDER CARRIES THE
mtime OF WHAT IT CAME FROM, and the page that shows it compares that mtime
to the source and says STALE out loud when it loses.

Lane G2 writes only into out/render/. electronics/ belongs to lane B1 and is
read here, never written.
"""
import datetime
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARD_DIR = os.path.join(ROOT, "electronics", "halo_rev_a")
OUT = os.path.join(ROOT, "out", "render")
CLI = "kicad-cli"

CHECK_ONLY = "--check" in sys.argv

# The two boards that exist. The routed one is what the fab pack is cut from;
# the unrouted one is what board.py emits before freerouting runs. Both are
# rendered, because "which of these is current" is exactly the question a
# reader of the gallery needs answered and hiding one does not answer it.
SOURCES = {
    "routed": os.path.join(BOARD_DIR, "out", "halo_rev_a-routed.kicad_pcb"),
    "unrouted": os.path.join(BOARD_DIR, "out", "halo_rev_a.kicad_pcb"),
}

# The generator whose output every one of those is. If this is newer than the
# pcb, the pcb itself is behind and NO render of it can be current.
GENERATOR = os.path.join(BOARD_DIR, "board.py")

VIEWS = [
    # (output name, source key, kicad-cli args, what it shows)
    ("halo_rev_a-routed-top.png", "routed",
     ["--side", "top", "--width", "1800", "--height", "1800"],
     "the routed board from directly above — the nine-tooth meander antenna "
     "runs along the top arc, outside the component field"),
    ("halo_rev_a-routed-bottom.png", "routed",
     ["--side", "bottom", "--width", "1800", "--height", "1800"],
     "the routed board from below"),
    ("halo_rev_a-routed-iso.png", "routed",
     ["--side", "top", "--rotate", "-30,0,25", "--perspective",
      "--width", "1800", "--height", "1350"],
     "the routed board on an isometric camera, so component height reads"),
    ("halo_rev_a-unrouted-top.png", "unrouted",
     ["--side", "top", "--width", "1800", "--height", "1800"],
     "the same board BEFORE the router ran — placement only. Shown so the "
     "routing is visible as a difference rather than asserted as one"),
]

COMMON = ["--quality", "high", "--use-board-stackup-colors",
          "--background", "opaque"]


def mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return None


def iso(t):
    if t is None:
        return None
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def read_back(path):
    """Open the PNG and decide whether it is a picture. rendercover's rule:
    a 404, a blank and a still-loading thumbnail look identical."""
    try:
        from PIL import Image, ImageStat
    except ImportError:
        return (None, "PIL not importable — cannot read the render back")
    try:
        with Image.open(path) as im:
            im.load()
            w, h = im.size
            if w < 200 or h < 200:
                return (False, "only %dx%d px" % (w, h))
            sd = ImageStat.Stat(im.convert("L")).stddev[0]
            if sd < 1.0:
                return (False, "blank: whole image stddev %.2f" % sd)
            return (True, "%dx%d px, stddev %.1f" % (w, h, sd))
    except FileNotFoundError:
        return (False, "no such file")
    except Exception as exc:                                   # noqa: BLE001
        return (False, "unreadable: %s" % exc)


def render(name, src, args):
    dst = os.path.join(OUT, name)
    cmd = [CLI, "pcb", "render", "--output", dst] + COMMON + args + [src]
    t0 = datetime.datetime.now()
    r = subprocess.run(cmd, capture_output=True, text=True)
    dt = (datetime.datetime.now() - t0).total_seconds()
    return (r.returncode, dt, cmd, (r.stderr or "").strip()[-400:])


def main():
    os.makedirs(OUT, exist_ok=True)
    gen_m = mtime(GENERATOR)
    rows = []
    fails = 0

    for name, key, args, what in VIEWS:
        src = SOURCES[key]
        src_m = mtime(src)
        row = dict(image="out/render/" + name, what=what,
                   source=os.path.relpath(src, ROOT),
                   source_mtime=iso(src_m),
                   generator=os.path.relpath(GENERATOR, ROOT),
                   generator_mtime=iso(gen_m))

        if src_m is None:
            row.update(verdict="CANNOT DETERMINE",
                       why="%s does not exist" % row["source"])
            rows.append(row)
            fails += 1
            continue

        if CHECK_ONLY:
            img_m = mtime(os.path.join(OUT, name))
            row["image_mtime"] = iso(img_m)
            row["verdict"] = ("CANNOT DETERMINE" if img_m is None
                              else ("PASS" if img_m >= src_m else "STALE"))
            row["why"] = ("--check: not rendered, only compared"
                          if img_m is not None else "no image on disk")
            rows.append(row)
            continue

        rc, dt, cmd, err = render(name, src, args)
        row["command"] = " ".join(
            c.replace(ROOT + "/", "") for c in cmd)
        row["seconds"] = round(dt, 1)
        if rc != 0:
            row.update(verdict="FAIL",
                       why="kicad-cli exited %d: %s" % (rc, err))
            rows.append(row)
            fails += 1
            continue

        ok, note = read_back(os.path.join(OUT, name))
        row["read_back"] = note
        img_m = mtime(os.path.join(OUT, name))
        row["image_mtime"] = iso(img_m)
        if ok is False:
            row.update(verdict="FAIL",
                       why="rendered, but the file is not a picture: " + note)
            fails += 1
        elif ok is None:
            row.update(verdict="CANNOT DETERMINE", why=note)
            fails += 1
        else:
            # The render is current WITH RESPECT TO THE PCB. Whether the pcb
            # itself is current with respect to board.py is a separate, and
            # louder, question.
            behind_gen = gen_m is not None and src_m < gen_m
            row["source_behind_generator"] = bool(behind_gen)
            row["verdict"] = "PASS"
            row["why"] = (
                "rendered from %s (%s) at %s; %s"
                % (row["source"], row["source_mtime"], row["image_mtime"],
                   ("the pcb is itself OLDER than %s (%s) — lane B1 has "
                    "edited the generator since this pcb was written, so "
                    "this picture is current for the pcb on disk and NOT "
                    "necessarily for the board B1 is now describing"
                    % (row["generator"], row["generator_mtime"]))
                   if behind_gen else
                   "the pcb is newer than its generator, so it is the "
                   "current output of board.py"))
        rows.append(row)

    manifest = dict(
        tool="tools/gen_board_renders.py",
        generated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        kicad=subprocess.run([CLI, "version"], capture_output=True,
                             text=True).stdout.strip(),
        generator=os.path.relpath(GENERATOR, ROOT),
        generator_mtime=iso(gen_m),
        renders=rows,
        verdict="PASS" if fails == 0 else "FAIL")

    if not CHECK_ONLY:
        with open(os.path.join(OUT, "board-renders.json"), "w") as fh:
            json.dump(manifest, fh, indent=2)

    for r in rows:
        print("%-16s %s  %s" % (r["verdict"], r["image"], r.get("why", "")))
    print("verdict %s" % manifest["verdict"])
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
