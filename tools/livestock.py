#!/usr/bin/env python3
"""Read stock+price LIVE for a list of LCSC order codes, from BOTH vendors,
and stamp every figure with the endpoint and the second it was read.

Reuses halo/tools/resolve_bom.py's parsers so the identity guard (the node's
own productCode must equal the code asked for) is the same one the halo lane
already broke on purpose.  ALWAYS fetches: the cache dir is unique per run.
"""
import datetime, json, os, pathlib, sys, time

RUN = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
os.environ["HALO_SRC_CACHE"] = f"/tmp/halo-livestock-{RUN}"
sys.path.insert(0, str(pathlib.Path.home() / "dev/ce-workshop/ce-designs/halo/tools"))
import resolve_bom as rb

def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def probe(code):
    rec = {"lcsc_code": code}
    t = now()
    try:
        L = rb.lcsc(code)
    except Exception as e:
        L = {"error": f"{type(e).__name__}: {e}"}
    rec["lcsc"] = L
    rec["lcsc_endpoint"] = f"https://www.lcsc.com/product-detail/{code}.html"
    rec["lcsc_read_at"] = t
    t = now()
    try:
        J = rb.jlc(code)
    except Exception as e:
        J = {"error": f"{type(e).__name__}: {e}"}
    rec["jlcpcb"] = J
    rec["jlcpcb_endpoint"] = rb.JLC_URL + "  {currentPage:1,pageSize:5,keyword:%s}" % code
    rec["jlcpcb_read_at"] = t
    return rec

if __name__ == "__main__":
    codes = sys.argv[2:]
    out = pathlib.Path(sys.argv[1])
    res = []
    for c in codes:
        r = probe(c)
        ls = r["lcsc"].get("stock"); js = r["jlcpcb"].get("stock")
        print(f"{c:14s} lcsc={ls!s:>10s}  jlc={js!s:>10s}  "
              f"{r['lcsc'].get('mpn') or r['lcsc'].get('error','')[:50]}", flush=True)
        res.append(r)
        time.sleep(0.6)
    out.write_text(json.dumps({"run": RUN, "probed_at_utc": now(),
                               "cache": os.environ["HALO_SRC_CACHE"],
                               "parser": "halo/tools/resolve_bom.py lcsc()/jlc()",
                               "results": res}, indent=1))
    print("wrote", out)
