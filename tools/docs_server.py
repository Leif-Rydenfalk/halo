#!/usr/bin/env python3
"""halo doc browser — renders this repo's markdown, TSV and images in a browser.

Usage:  python3 tools/docs_server.py [port] [repo-root]
        default port 8891, default root = the repo this file lives in.

Routes: /                     -> the AirTag hardware dossier
        /d/<rel path>         -> render a .md (marked.js) or .tsv (as a table)
        /gallery              -> images/airtag contact sheet
        /raw/<rel path>       -> the file itself (images, downloads)
        /api/health           -> {"app":"halo-doc-browser",...}  (launchpad probe)
Any other path 404s on purpose — that is the launchpad's negative control.
"""
import os, sys, html, mimetypes, json, subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

ROOT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else
                       os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8891
MARKER = "halo-doc-browser"

SHELL = """<!doctype html><html><head><meta charset=utf-8>
<title>%(title)s — halo docs</title>
<meta name=viewport content="width=device-width,initial-scale=1">
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<style>
:root{--bg:#fbfaf8;--fg:#1b1a17;--mut:#6b6862;--line:#e3ded5;--acc:#8a5a2b;--code:#f3efe8}
@media(prefers-color-scheme:dark){:root{--bg:#14130f;--fg:#eae6de;--mut:#9a958b;--line:#2e2b25;--acc:#d9a05b;--code:#1e1c17}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;display:flex}
aside{width:290px;flex:0 0 290px;height:100vh;overflow:auto;border-right:1px solid var(--line);padding:18px 14px;position:sticky;top:0}
aside h1{font-size:15px;letter-spacing:.09em;text-transform:uppercase;color:var(--mut);margin:0 0 4px}
aside .sub{font-size:12px;color:var(--mut);margin-bottom:16px}
aside h2{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--mut);margin:18px 0 6px;font-weight:600}
aside a{display:block;padding:5px 8px;border-radius:6px;color:var(--fg);text-decoration:none;font-size:13.5px}
aside a:hover{background:var(--code)} aside a.on{background:var(--acc);color:#fff}
main{flex:1;min-width:0;max-width:960px;padding:34px 46px 90px}
main img{max-width:100%%;border:1px solid var(--line);border-radius:8px;background:#fff}
h1,h2,h3{line-height:1.25} h1{font-size:29px;margin:.2em 0 .5em}
h2{font-size:21px;margin-top:1.9em;padding-bottom:.25em;border-bottom:1px solid var(--line)}
h3{font-size:16.5px;margin-top:1.5em}
a{color:var(--acc)}
table{border-collapse:collapse;width:100%%;margin:1.1em 0;font-size:13.2px;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}
th{background:var(--code);font-weight:600}
tr:nth-child(even) td{background:color-mix(in srgb,var(--code) 45%%,transparent)}
code{background:var(--code);padding:1px 5px;border-radius:4px;font-size:12.7px}
pre{background:var(--code);padding:12px 14px;border-radius:8px;overflow-x:auto}
pre code{background:none;padding:0}
blockquote{margin:1em 0;padding:2px 16px;border-left:3px solid var(--acc);color:var(--mut)}
.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.gal figure{margin:0} .gal figcaption{font-size:11.5px;color:var(--mut);margin-top:5px;word-break:break-all}
.bar{font-size:12px;color:var(--mut);margin-bottom:22px;padding-bottom:12px;border-bottom:1px solid var(--line)}
</style></head><body>
<aside><h1>halo</h1><div class=sub>%(marker)s · <a href="https://github.com/Leif-Rydenfalk/halo" target=_blank>GitHub &#8599;</a></div>%(nav)s</aside>
<main><div class=bar>%(path)s</div><div id=doc></div></main>
<script>
const raw = %(payload)s;
if (raw.kind === 'md') {
  marked.setOptions({gfm:true, breaks:false});
  document.getElementById('doc').innerHTML = marked.parse(raw.text);
} else { document.getElementById('doc').innerHTML = raw.text; }
</script></body></html>"""

SKIP = {".git", "__pycache__", ".venv", "trash", "node_modules", "out", ".DS_Store"}

def tree():
    """rel-path lists grouped by directory. Walk ONCE."""
    groups = {}
    for dirpath, dirnames, files in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for f in sorted(files):
            if not f.lower().endswith((".md", ".tsv")):
                continue
            rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
            groups.setdefault(os.path.dirname(rel) or ".", []).append(rel)
    return groups

def gallery_files():
    g = os.path.join(ROOT, "images/airtag")
    if not os.path.isdir(g):
        return []
    return sorted(f for f in os.listdir(g)
                  if f.lower().endswith((".jpg", ".jpeg", ".png")))

def nav_html(cur):
    groups = tree()                      # <- walk once, not once per group
    order = {".": 0, "research": 1, "docs": 2, "spec": 3, "electronics": 4,
             "hardware": 5, "firmware": 6, "images/airtag": 7}
    out = []
    for d in sorted(groups, key=lambda k: (order.get(k, 50), k)):
        out.append("<h2>%s</h2>" % html.escape(d if d != "." else "root"))
        for rel in groups[d]:
            cls = " class=on" if rel == cur else ""
            out.append('<a href="/d/%s"%s>%s</a>' %
                       (html.escape(rel), cls, html.escape(os.path.basename(rel))))
    out.append('<h2>gallery</h2><a href="/gallery">images/airtag (%d)</a>'
               % len(gallery_files()))
    return "".join(out)

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b))); self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        p = unquote(self.path.split("?")[0])
        if p == "/api/health":
            return self._send(200, json.dumps({"app": MARKER, "root": ROOT,
                                               "port": PORT, "status": "ok"}),
                              "application/json")
        if p == "/":
            p = "/d/research/01-airtag-hardware.md"
        if p.startswith("/raw/"):
            rel = p[5:]
            fp = os.path.realpath(os.path.join(ROOT, rel))
            if not fp.startswith(ROOT) or not os.path.isfile(fp):
                return self._send(404, "not found", "text/plain")
            ct = mimetypes.guess_type(fp)[0] or "application/octet-stream"
            return self._send(200, open(fp, "rb").read(), ct)
        if p == "/gallery":
            imgs = gallery_files()
            cards = "".join(
                '<figure><a href="/raw/images/airtag/%s" target=_blank>'
                '<img src="/raw/images/airtag/%s" loading=lazy></a>'
                '<figcaption>%s</figcaption></figure>' % (f, f, html.escape(f))
                for f in imgs)
            body = "<h1>images/airtag</h1><div class=gal>%s</div>" % cards
            return self._send(200, SHELL % dict(
                title="gallery", marker=MARKER, nav=nav_html(""),
                path="images/airtag — %d files" % len(imgs),
                payload=json.dumps({"kind": "html", "text": body})))
        if p.startswith("/d/"):
            rel = p[3:]
            fp = os.path.realpath(os.path.join(ROOT, rel))
            if not fp.startswith(ROOT) or not os.path.isfile(fp):
                return self._send(404, "no such document", "text/plain")
            txt = open(fp, encoding="utf-8", errors="replace").read()
            if fp.endswith(".tsv"):
                rows = [r.split("\t") for r in txt.strip().split("\n")]
                hdr = ["lane", "url", "title", "date", "note"]
                body = ("<h1>sources.tsv</h1><p>%d rows</p><table><tr>%s</tr>%s</table>" % (
                    len(rows), "".join("<th>%s</th>" % h for h in hdr),
                    "".join("<tr>%s</tr>" % "".join(
                        "<td>%s</td>" % (('<a href="%s" target=_blank>%s</a>'
                                          % (html.escape(c), html.escape(c[:70])))
                                         if c.startswith("http") else html.escape(c))
                        for c in (r + [""] * 5)[:5]) for r in rows)))
                payload = {"kind": "html", "text": body}
            else:
                # rewrite relative image links to /raw/
                base = os.path.dirname(rel)
                txt = txt.replace("](images/", "](/raw/images/")
                payload = {"kind": "md", "text": txt}
            return self._send(200, SHELL % dict(
                title=os.path.basename(rel), marker=MARKER, nav=nav_html(rel),
                path=html.escape(rel), payload=json.dumps(payload)))
        return self._send(404, "not found", "text/plain")

if __name__ == "__main__":
    print("halo docs on http://127.0.0.1:%d/  root=%s" % (PORT, ROOT), flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
