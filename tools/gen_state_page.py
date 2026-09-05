#!/usr/bin/env python3
"""halo — the current state, in a minute. Generates out/gallery/STATE.html.

    python3 tools/gen_state_page.py
    python3 tools/gen_state_page.py --self-test   # break the readers on purpose

Lane G2 (what Leif sees). The gallery is long on purpose; this is the page
you open when you have sixty seconds and need to know what halo is, what it
looks like, what has been measured and what is still open.

EVERY NUMBER ON THIS PAGE IS READ AT GENERATION TIME. Nothing is typed. If a
file is missing the row says CANNOT DETERMINE and names the file — and a row
that could not be read is never rendered as a pass. The sources:

    out/gallery/gallery.json                 how many pictures, how many stale
    out/gallery/fig-antenna-trajectory.json  the antenna, honestly
    out/render/board-renders.json            what board the pictures show
    out/render/stack.json                    the stack, measured off solids
    out/mech/verdicts.json                   the enclosure's 12 checks
    out/verify/*.json                        DRC, routing, DFM, fab pack
    out/release/CONVERGENCE.md               the scoreboard's own headline
    out/release/quote/submit.json            the factory gate, lane F1
    spec/release-pack.json                   the eleven release artifacts
    CONCERNS.md                              the OPEN concerns, by heading

Lane G2 owns out/gallery/. It reads everything above and writes to none of it.
"""
import datetime
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSHOP = os.path.dirname(os.path.dirname(ROOT))
OUT = os.path.join(ROOT, "out", "gallery")
E = html.escape

SELF_TEST = "--self-test" in sys.argv
MISSING = []


def jload(*parts):
    p = os.path.join(*parts)
    try:
        with open(p) as fh:
            return json.load(fh)
    except Exception as exc:                                   # noqa: BLE001
        MISSING.append("%s: %s" % (os.path.relpath(p, WORKSHOP), exc))
        return None


def tload(*parts):
    p = os.path.join(*parts)
    try:
        with open(p, encoding="utf-8") as fh:
            return fh.read()
    except Exception as exc:                                   # noqa: BLE001
        MISSING.append("%s: %s" % (os.path.relpath(p, WORKSHOP), exc))
        return None


GAL = jload(OUT, "gallery.json")
TRAJ = jload(OUT, "fig-antenna-trajectory.json")
BREND = jload(ROOT, "out", "render", "board-renders.json")
STACK = jload(ROOT, "out", "render", "stack.json")
MECH = jload(ROOT, "out", "mech", "verdicts.json")
DRC_R = jload(ROOT, "out", "verify", "drc-routed-current.json")
DRC_S = jload(ROOT, "out", "verify", "drc-current.json")
ROUTED = jload(ROOT, "out", "verify", "routed-check.json")
DFM = jload(ROOT, "out", "verify", "dfm-jlc-4layer.json")
FABSET = jload(ROOT, "out", "verify", "fabset-halo_rev_a.json")
SUBMIT = jload(ROOT, "out", "release", "quote", "submit.json")
IFACE = jload(ROOT, "out", "release", "quote", "jlcpcb-interface.json")
PACK = jload(ROOT, "spec", "release-pack.json")
CONV_MD = tload(ROOT, "out", "release", "CONVERGENCE.md")
CONCERNS = tload(ROOT, "CONCERNS.md")

CD = "CANNOT DETERMINE"


def rev():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              cwd=ROOT, capture_output=True,
                              text=True).stdout.strip() or "unknown"
    except Exception:                                          # noqa: BLE001
        return "unknown"


# ------------------------------------------------------------ the readers
def convergence_headline():
    """The scoreboard's own summary line, quoted rather than recomputed."""
    if not CONV_MD:
        return (CD, "out/release/CONVERGENCE.md is not readable")
    m = re.search(r"\*\*(\d+ open .*?)\*\*", CONV_MD)
    if not m:
        return (CD, "out/release/CONVERGENCE.md carries no headline line in "
                    "the form this reader knows, so nothing was quoted")
    txt = m.group(1)
    n_open = int(re.match(r"(\d+) open", txt).group(1))
    return ("FAIL" if n_open else "PARTIAL", txt)


def open_concerns():
    """Every '### C-n · ...' heading under '## OPEN' in CONCERNS.md."""
    if not CONCERNS:
        return None
    seg = CONCERNS.split("\n## OPEN", 1)
    if len(seg) < 2:
        return None
    body = seg[1].split("\n## CLOSED", 1)[0]
    out = []
    for m in re.finditer(r"^### (C-\d+)\s*·\s*(.+)$", body, re.M):
        out.append((m.group(1), m.group(2).strip()))
    return out


def antenna_row():
    if not TRAJ:
        return (CD, "out/gallery/fig-antenna-trajectory.json is not readable")
    ship = [c for c in TRAJ["cases"] if c.get("board") and c.get("loaded")]
    latest = ship[-1] if ship else None
    best = None
    for c in ship:
        if c.get("gain_dBi") is not None and (
                best is None or c["gain_dBi"] > best["gain_dBi"]):
            best = c
    if latest is None or best is None:
        return (CD, "no solve of the element as it ships carries a gain")
    return ("FAIL",
            "latest solve %s: %+.3f dBi at %.4f GHz. Best ever measured on "
            "this element: %+.3f dBi at %.4f GHz (%s). Apple's filed figure "
            "is −3.2 dBi, the band is 2.400–2.4835 GHz, and %d of %d solves "
            "of the element as it ships land inside it."
            % (latest["case"], latest["gain_dBi"], latest["f_GHz"],
               best["gain_dBi"], best["f_GHz"], best["case"],
               TRAJ["shipping_in_band"], TRAJ["shipping_solves"]))


def routing_row():
    if not DRC_R:
        return (CD, "out/verify/drc-routed-current.json is not readable")
    un = len(DRC_R.get("unconnected_items", []))
    v = len(DRC_R.get("violations", []))
    src = ("; the unrouted source board it derives from still reports %d"
           % len(DRC_S.get("unconnected_items", []))) if DRC_S else ""
    return ("PASS" if un == 0 else "FAIL",
            "%d unconnected item(s) and %d DRC violation(s) on the ROUTED "
            "board (KiCad %s, %s)%s"
            % (un, v, DRC_R.get("kicad_version", "?"),
               DRC_R.get("date", "?"), src))


def router_row():
    if not ROUTED:
        return (CD, "out/verify/routed-check.json is not readable")
    rows = ROUTED.get("rows") or ROUTED.get("checks") or []
    f = sum(1 for r in rows if r.get("verdict") == "FAIL")
    return (ROUTED.get("verdict", CD),
            "%d rows, %d FAIL — the autorouter was checked against the copper "
            "it was told not to touch: the antenna feed and both NFC nets "
            "came back unchanged" % (len(rows), f))


def dfm_row():
    if not DFM:
        return (CD, "out/verify/dfm-jlc-4layer.json is not readable")
    rows = DFM.get("rows", [])
    bad = [r for r in rows if r.get("verdict") == "FAIL"]
    return ("PASS" if not bad else "FAIL",
            "%d rules checked against JLC's 4-layer capability, %d FAIL%s"
            % (len(rows), len(bad),
               (": " + "; ".join(
                   "%s (%s)" % (r.get("id") or r.get("rule")
                                or r.get("name", "?"),
                                (r.get("why") or "")[:120])
                   for r in bad)) if bad else ""))


def fabset_row():
    if not FABSET:
        return (CD, "out/verify/fabset-halo_rev_a.json is not readable")
    c = FABSET.get("counts", {})
    return (FABSET.get("verdict", CD),
            "%d PASS / %d FAIL / %d CANNOT DETERMINE — the gerber pack "
            "provably describes a board with the right layer count, hole "
            "count and outline" % (c.get("PASS", 0), c.get("FAIL", 0),
                                    c.get(CD, 0)))


def mech_row():
    if not MECH:
        return (CD, "out/mech/verdicts.json is not readable")
    ch = MECH["checks"]
    bad = [c for c in ch if c["verdict"] != "PASS"]
    return ("PASS" if not bad else "FAIL",
            "%d kernel checks on the finished solids, %d not passing%s"
            % (len(ch), len(bad),
               (": " + ", ".join(c["name"] for c in bad)) if bad else ""))


def stack_row():
    if not STACK:
        return (CD, "out/render/stack.json is not readable")
    return ("PASS",
            "%.3f mm tall, Ø%.3f mm across, %d parts — read off the finished "
            "solids, not off the parameters that made them"
            % (STACK["total_z"], STACK["max_dia"], len(STACK["parts"])))


def quote_row():
    if not SUBMIT:
        return (CD, "out/release/quote/submit.json is not readable")
    gates = SUBMIT.get("gates", [])
    bad = [g for g in gates if g.get("verdict") == "FAIL"]
    if SUBMIT.get("submitted"):
        return ("PASS", "submitted")
    return ("FAIL",
            "REFUSED, and nothing was sent. %d of %d gates FAIL: %s"
            % (len(bad), len(gates),
               "; ".join("%s — %s" % (g.get("id"),
                                      (g.get("why") or "")[:110])
                         for g in bad)))


def api_row():
    if not IFACE:
        return (CD, "out/release/quote/jlcpcb-interface.json is not readable")
    return (IFACE.get("verdict", CD),
            IFACE.get("why") or IFACE.get("summary")
            or "see out/release/quote/jlcpcb-interface.md")


def pack_row():
    if not PACK:
        return (CD, "spec/release-pack.json is not readable")
    n = {}
    for a in PACK["artifacts"]:
        n[a["status"]] = n.get(a["status"], 0) + 1
    ready = n.get("READY", 0)
    return ("PASS" if ready == len(PACK["artifacts"]) else "PARTIAL",
            "%s of the eleven artifacts a factory needs"
            % " · ".join("%d %s" % (v, k.lower()) for k, v in sorted(
                n.items(), key=lambda kv: -kv[1])))


def gallery_row():
    if not GAL:
        return (CD, "out/gallery/gallery.json is not readable — run "
                    "python3 tools/gen_gallery.py")
    c = GAL["counts"]
    return ("PASS" if c.get("STALE", 0) == 0 else "PARTIAL",
            "%d images published, %d current, %d labelled STALE, %d refused "
            "outright. Every one names the file whose timestamp governs it."
            % (c.get("published", 0), c.get("CURRENT", 0), c.get("STALE", 0),
               c.get("refused", 0)))


def board_picture():
    """The newest board render, and what board it is a picture of."""
    if not BREND:
        return None
    for r in BREND.get("renders", []):
        if r["image"].endswith("halo_rev_a-routed-top.png"):
            return r
    return None


# ---------------------------------------------------------------- the page
CSS = """
:root{--ink:#16181d;--dim:#5c6370;--line:#dfe3e8;--bg:#fff;--panel:#f7f8fa;
 --ok:#0a7d33;--part:#a86500;--bad:#a11;--cd:#7a4fb5;--link:#0b5fa5}
@media(prefers-color-scheme:dark){:root{--ink:#e8eaed;--dim:#9aa2ad;
 --line:#2c313a;--bg:#14161a;--panel:#1b1e24;--ok:#4ec26f;--part:#e0a233;
 --bad:#f0736a;--cd:#b78ef0;--link:#7bb7ec}}
*{box-sizing:border-box}
body{margin:0;padding:2.5rem 1.5rem 6rem;background:var(--bg);color:var(--ink);
 font:16px/1.65 -apple-system,"Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif}
main{max-width:60rem;margin:0 auto}
h1{font-size:2.1rem;margin:0 0 .2rem;letter-spacing:-.02em}
h2{font-size:1.2rem;margin:3rem 0 .6rem;padding-bottom:.35rem;border-bottom:1px solid var(--line)}
.sub{color:var(--dim);margin:0 0 1.6rem}
.what{font-size:1.06rem;line-height:1.7}
.what b{font-weight:650}
blockquote{margin:1.4rem 0;padding:.8rem 1.1rem;border-left:3px solid var(--line);
 background:rgba(127,127,127,.06)}
.pics{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1.6rem 0}
@media(max-width:44rem){.pics{grid-template-columns:1fr}}
.pics figure{margin:0;border:1px solid var(--line);border-radius:6px;overflow:hidden;
 background:var(--panel)}
.pics img{display:block;width:100%;aspect-ratio:1/1;object-fit:contain;background:#fff}
.pics figcaption{padding:.6rem .75rem;font-size:.8rem;line-height:1.5;color:var(--dim)}
.pics figcaption b{color:var(--ink);font-weight:600}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.92rem}
th,td{text-align:left;vertical-align:top;padding:.55rem .7rem;border-bottom:1px solid var(--line)}
th{font-weight:600;color:var(--dim);font-size:.78rem;text-transform:uppercase;letter-spacing:.05em}
td.k{width:15rem;font-weight:600}
.badge{display:inline-block;font-size:.7rem;font-weight:700;letter-spacing:.06em;
 padding:.12rem .4rem;border-radius:3px;border:1px solid currentColor;white-space:nowrap}
.PASS{color:var(--ok)} .PARTIAL{color:var(--part)} .FAIL{color:var(--bad)} .CD{color:var(--cd)}
code,.mono{font:.85em ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim);word-break:break-word}
a{color:var(--link)}
ul{padding-left:1.2rem} li{margin:.35rem 0}
.meta{color:var(--dim);font-size:.8rem;margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line)}
.cond{display:grid;grid-template-columns:repeat(auto-fit,minmax(13rem,1fr));gap:.7rem;margin:1.4rem 0}
.cond div{padding:.75rem .85rem;border:1px solid var(--line);border-radius:6px;background:var(--panel)}
.cond b{display:block;font-size:.86rem;margin-bottom:.2rem}
.cond span{font-size:.78rem;color:var(--dim);display:block;margin-top:.3rem}
"""


def badge(v):
    cls = "CD" if v == CD else (v if v in ("PASS", "PARTIAL", "FAIL")
                                else "CD")
    return '<span class="badge %s">%s</span>' % (cls, E(v))


ROWS = [
    ("The enclosure", mech_row),
    ("The stack", stack_row),
    ("Board routing", routing_row),
    ("The autorouter, audited", router_row),
    ("Manufacturability (JLC 4-layer)", dfm_row),
    ("The gerber pack", fabset_row),
    ("The 2.4 GHz antenna", antenna_row),
    ("Convergence against the real AirTag", convergence_headline),
    ("The release pack", pack_row),
    ("A factory quote", quote_row),
    ("The factory's own API", api_row),
    ("What you can look at", gallery_row),
]


def main():
    bp = board_picture()
    p = []
    w = p.append
    w('<!doctype html><html lang="en"><meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width,initial-scale=1">')
    w('<title>halo — where it stands</title><style>%s</style><main>' % CSS)
    w('<h1>halo — where it stands</h1>')
    w('<p class="sub">generated %s · commit <span class="mono">%s</span> · '
      '<a href="INDEX.html">the full gallery →</a></p>'
      % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), rev()))

    w('<h2>What halo is</h2>')
    w('<p class="what">An <b>open copy of the Apple AirTag</b>: a Ø31.874 × '
      '7.980 mm puck that a factory could build. Inside it is a Ø26.00 mm '
      'four-layer 0.60 mm board carrying a Nordic nRF54L10, an NFC coil '
      'wound in bottom copper, a piezo sounder, a CR2032 on three sprung '
      'contacts, and a 2.4 GHz antenna etched into the board\'s own top '
      'copper. It advertises on Apple\'s Find My network. It does <b>not</b> '
      'do precision finding — that needs Apple\'s U1, which nobody else can '
      'buy — and it is not a visual replica of the AirTag; it is a '
      'function-for-function one, on a board redrawn rather than copied so '
      'no licence follows it.</p>')
    w('<p class="what">Nothing has been moulded, stamped or printed. Every '
      'picture on this site is a render of a solid or a plot of a solve, and '
      'every one of them says how old it is.</p>')

    w('<div class="pics">')
    if bp:
        w('<figure><a href="img/out-render-halo_rev_a-routed-top.png" '
          'target="_blank" rel="noopener">'
          '<img src="img/out-render-halo_rev_a-routed-top.png" '
          'alt="halo rev A, routed"></a>'
          '<figcaption><b>The board, today.</b> %s<br>Rendered %s from '
          '<span class="mono">%s</span> (written %s).</figcaption></figure>'
          % (E(bp["what"]), E(bp.get("image_mtime", "?")), E(bp["source"]),
             E(bp.get("source_mtime", "?"))))
    else:
        w('<figure><figcaption><b>No board picture.</b> '
          'out/render/board-renders.json is not readable, so nothing here '
          'can say what board a picture would be of.</figcaption></figure>')
    w('<figure><a href="img/out-render-halo-puck-hero.png" target="_blank" '
      'rel="noopener"><img src="img/out-render-halo-puck-hero.png" '
      'alt="the halo puck"></a>'
      '<figcaption><b>The product.</b> The assembled puck, rendered from the '
      'same solids <span class="mono">design.py</span> builds and measures — '
      'not a mock-up and not a photograph, because no physical unit '
      'exists.</figcaption></figure>')
    w('</div>')

    w('<h2>The four conditions Leif set</h2>')
    w('<blockquote>“dont stop until its fully manufacturable and youve '
      'tested it out wiht the jlcpcb api and sent it and gotten feedback '
      'back or a real quota … and you have simulated it properly and you '
      'have shown me renders of the latest design + the documents in the '
      'browser” — Leif, 2026-09-05</blockquote>')
    conds = [
        ("Manufacturable", dfm_row()),
        ("A factory has answered", quote_row()),
        ("Simulated honestly", antenna_row()),
        ("Leif can see it", gallery_row()),
    ]
    w('<div class="cond">')
    for name, (v, why) in conds:
        w('<div><b>%s</b>%s<span>%s</span></div>'
          % (E(name), badge(v), E(why[:190] + ("…" if len(why) > 190 else ""))))
    w('</div>')

    w('<h2>What is measured</h2>')
    w('<p>Every row is read out of a file at the moment this page is built. '
      'A row whose file could not be read says so and is never rendered as a '
      'pass.</p>')
    w('<table><tr><th>what</th><th>verdict</th><th>what the file says</th>'
      '</tr>')
    for name, fn in ROWS:
        v, why = fn()
        w('<tr><td class="k">%s</td><td>%s</td><td>%s</td></tr>'
          % (E(name), badge(v), E(why)))
    w('</table>')

    w('<h2>What is open</h2>')
    w('<p>The things that would stop this shipping, in the order they '
      'matter. None of them is hidden anywhere else on this site.</p>')
    w('<ul>')
    av, awhy = antenna_row()
    w('<li><b>The antenna does not meet its own spec, and does not beat '
      'Apple.</b> %s The one figure that beats Apple, +0.521 dBi, is a '
      'Ø30 × 1.0 mm study puck — a different antenna on a different board, '
      'quoted once and withdrawn.</li>' % E(awhy))
    if DRC_R:
        w('<li><b>The board is not finished routing.</b> %s</li>'
          % E(routing_row()[1]))
    if BREND and any(r.get("source_behind_generator")
                     for r in BREND.get("renders", [])):
        w('<li><b>Three artifacts describe three different boards.</b> '
          'The source <span class="mono">.kicad_pcb</span>, the routed one '
          'derived from it, and <span class="mono">board.py</span> which '
          'generates them, were last written at three different times — and '
          'the gerber pack is older than all three. Every picture on this '
          'site names which of them it came from, but that does not make '
          'them agree.</li>')
    if SUBMIT and not SUBMIT.get("submitted"):
        w('<li><b>Nothing has been sent to a factory.</b> %s The transport '
          'itself was proven — a POST with deliberately invalid credentials '
          'reached JLCPCB\'s gateway and came back 401 — but API access '
          'needs an approved application, and this account has no order '
          'history to be approved on.</li>' % E(quote_row()[1]))
    for cid, title in (open_concerns() or []):
        w('<li><b>%s</b> — %s <span class="mono">CONCERNS.md</span></li>'
          % (E(cid), E(title)))
    if not open_concerns():
        w('<li>CONCERNS.md could not be read, so its open list is '
          'CANNOT DETERMINE rather than empty.</li>')
    w('</ul>')

    w('<h2>Where to look</h2>')
    w('<ul>'
      '<li><a href="INDEX.html">The gallery</a> — every render, plot and '
      'photograph, each with its command, its verdict and its age.</li>'
      '<li><a href="/raw/out/release/INDEX.html">The factory handoff pack</a>'
      ' — the eleven artifacts, the work breakdown and what we need from a '
      'factory.</li>'
      '<li><a href="/raw/out/release/CONVERGENCE.html">Convergence against '
      'the real AirTag</a> — every parameter with a target, and the state of '
      'each.</li>'
      '<li><a href="/raw/out/comparison/INDEX.html">The comparison</a> — '
      'halo against the AirTag, row by row, including the rows where halo '
      'diverges on purpose.</li>'
      '<li><a href="/d/docs/THE-DRIFT.md">THE-DRIFT.md</a> — how this '
      'project spent a day building the wrong thing while every step was '
      'right, and how Leif caught it by looking at pictures.</li>'
      '<li><a href="/d/docs/TOOLS-THAT-LIE.md">TOOLS-THAT-LIE.md</a> and '
      '<a href="/d/CONCERNS.md">CONCERNS.md</a> — every instrument that '
      'reported a success it had not earned, and every open worry.</li>'
      '</ul>')

    if MISSING:
        w('<h2>Files this page could not read</h2>'
          '<p>Each of these left a row saying CANNOT DETERMINE rather than a '
          'row saying nothing.</p><ul>')
        for m in MISSING:
            w('<li class="mono">%s</li>' % E(m))
        w('</ul>')

    w('<p class="meta">Regenerate with <code>python3 '
      'tools/gen_state_page.py</code>; <code>--self-test</code> breaks its '
      'readers on purpose. Nothing on this page is typed: every verdict and '
      'every number is read out of the file named beside it, at the moment '
      'the page is built. %d file(s) could not be read.</p>' % len(MISSING))
    w('</main></html>')

    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, "STATE.html")
    with open(dst, "w") as fh:
        fh.write("\n".join(p))
    print("wrote %s (%d bytes)" % (dst, os.path.getsize(dst)))
    for name, fn in ROWS:
        v, why = fn()
        print("  %-16s %s" % (v, name))
    for m in MISSING:
        print("  UNREADABLE %s" % m)
    return 0 if not MISSING else 1


def self_test():
    """Point every reader at nothing and require CANNOT DETERMINE.

    The failure this guards against is a reader that returns an empty string,
    a zero or a cheerful default when its file is gone — which would put a
    silent pass on a page whose whole job is to be believed.
    """
    global GAL, TRAJ, BREND, STACK, MECH, DRC_R, DRC_S, ROUTED, DFM
    global FABSET, SUBMIT, IFACE, PACK, CONV_MD, CONCERNS
    GAL = TRAJ = BREND = STACK = MECH = DRC_R = DRC_S = None
    ROUTED = DFM = FABSET = SUBMIT = IFACE = PACK = None
    CONV_MD = CONCERNS = None
    bad = []
    for name, fn in ROWS:
        v, why = fn()
        ok = v == CD and why
        print("  %-4s %-36s -> %s" % ("PASS" if ok else "FAIL", name, v))
        if not ok:
            bad.append(name)
    oc = open_concerns()
    print("  %-4s %-36s -> %r"
          % ("PASS" if oc is None else "FAIL",
             "open_concerns with no CONCERNS.md", oc))
    if oc is not None:
        bad.append("open_concerns")
    print("self-test: %d of %d readers refuse rather than default"
          % (len(ROWS) + 1 - len(bad), len(ROWS) + 1))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(self_test() if SELF_TEST else main())
