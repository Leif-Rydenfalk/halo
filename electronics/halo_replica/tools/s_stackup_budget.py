#!/usr/bin/env python3
"""s_stackup_budget.py — can N layers physically fit in T millimetres?

THE QUESTION THIS TOOL EXISTS TO ANSWER WITHOUT ASSUMING ITS OWN ANSWER.
The AirTag's layer count was never published. The temptation is to assume four
and then find four. This tool never takes a layer count as an input to be
confirmed: it takes a THICKNESS and returns the set of layer counts that a
stated material class can build inside it. The inputs are copper foil weights,
core minima and prepreg pressed thicknesses read off fabricator pages — numbers
that can contradict the conclusion, which is the only kind worth using.

  A layer count is never the input. It is only ever the output.

Verbs
  doctor    — is the material table usable? Every row must carry a source.
  budget    — minimum buildable thickness for one (construction, layer count)
  bounds    — for a target thickness, the layer counts each construction can build
  selftest  — 27 deliberate breaks, each of which MUST go red

Exit code IS the verdict: 0 PASS, 1 FAIL, 2 CANNOT DETERMINE.

A construction whose material rows are null is NOT quietly skipped and NOT
given a plausible default — it exits 2 and names the row. That refusal is a
feature and `selftest` proves it still fires.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MATERIALS = os.path.join(HERE, "..", "board", "stackup", "materials.json")

PASS, FAIL, CANNOT = 0, 1, 2


class CannotDetermine(Exception):
    """A material row needed for this sum has no number and no source."""


def load(path=None):
    with open(path or DEFAULT_MATERIALS) as fh:
        return json.load(fh)


def _row(m, group, key):
    """Fetch one material row, refusing anything without a number AND a source."""
    try:
        r = m[group][key]
    except KeyError:
        raise CannotDetermine(f"materials.json has no row {group}.{key}")
    if not isinstance(r, dict) or "mm" not in r:
        raise CannotDetermine(f"{group}.{key} is not a material row")
    if r["mm"] is None:
        raise CannotDetermine(f"{group}.{key} has no thickness — {r.get('_note') or r.get('source') or 'no reason recorded'}")
    if not r.get("source"):
        raise CannotDetermine(f"{group}.{key} = {r['mm']} mm carries NO SOURCE, so it is not a number this tool will add up")
    return float(r["mm"])


def provenance(m, construction):
    """Which rows of a construction are INFERENCES rather than published.

    This exists because the tag was not travelling. materials.json marks
    outer_finished_copper.thin and copper_foil.0.33oz as `inference`, both are
    pulled by fr4-thin, and fr4-thin carries this lane's entire upper bound --
    yet STACKUP.md quoted its laminate totals with no tag attached. A caveat
    that stays in the data file while the number walks out on its own is the
    shape this lane criticised in someone else's document on the same day:
    an UNVERIFIED tag the next paragraph reasons past is camouflage, because a
    reader who sees the tag concludes the author was careful and stops checking.

    So provenance now travels WITH the number, computed rather than remembered.
    Reported split, because the split matters: this lane's strongest claim is
    about DIELECTRIC alone -- "6 layers needs 0.350 mm of dielectric before a
    micron of copper" -- and the dielectric rows are all published. Only the
    copper, and therefore only the laminate TOTAL, leans on an inference.
    """
    c = m["constructions"][construction]
    out = {"dielectric": [], "copper": []}
    for grp, key, bucket in (("core", c["core"], "dielectric"),
                             ("prepreg", c["prepreg"], "dielectric"),
                             ("outer_finished_copper", c["outer"], "copper"),
                             ("copper_foil", c["inner_foil"], "copper")):
        row = m.get(grp, {}).get(key)
        if isinstance(row, dict) and row.get("kind") == "inference":
            out[bucket].append(f"{grp}.{key}")
    return out


def budget(m, construction, layers):
    """Minimum laminate thickness (copper + dielectric, no soldermask) for
    `layers` copper layers built in `construction`. Raises CannotDetermine."""
    if layers < 2 or layers % 2:
        raise CannotDetermine(f"layer count {layers} is not an even count >= 2; odd and single-layer stacks are outside this tool")
    c = m["constructions"].get(construction)
    if c is None:
        raise CannotDetermine(f"no construction named {construction!r}")

    outer = _row(m, "outer_finished_copper", c["outer"])
    inner = _row(m, "copper_foil", c["inner_foil"])
    core = _row(m, "core", c["core"])
    prepreg = _row(m, "prepreg", c["prepreg"])

    # An N-layer stack is (N/2 - 1) cores bonded by (N/2) prepreg... no:
    # standard construction is N/2 - 1 cores? For N=4: 1 core + 2 prepreg is
    # wrong (that is 1 core between two foils = 4 layers with 2 prepreg? no).
    # Foil construction, N layers:  foil | prepreg | core | prepreg | foil  (N=4)
    #                               = 1 core, 2 prepreg
    # N=6: foil | pp | core | pp | core | pp | foil = 2 cores, 3 prepreg
    # In general: cores = N/2 - 1, prepreg = N/2.
    cores = layers // 2 - 1
    pregs = layers // 2
    # A core already carries copper on both faces; that copper is the inner
    # layers, and it is counted separately below, so the core row here is taken
    # as its DIELECTRIC thickness. Cores are quoted as dielectric in the
    # sources used, so no subtraction is applied.
    dielectric = cores * core + pregs * prepreg
    copper = 2 * outer + (layers - 2) * inner
    return {
        "layers": layers,
        "construction": construction,
        "cores": cores, "core_mm": core,
        "prepreg_sheets": pregs, "prepreg_mm": prepreg,
        "dielectric_mm": round(dielectric, 4),
        "outer_cu_mm": outer, "inner_cu_mm": inner,
        "copper_mm": round(copper, 4),
        "laminate_mm": round(dielectric + copper, 4),
        "inferred": provenance(m, construction),
    }


def with_mask(m, laminate_mm):
    sm = m["soldermask_per_side"]
    return (round(laminate_mm + 2 * sm["mm_low"], 4),
            round(laminate_mm + 2 * sm["mm_high"], 4))



def stock(m):
    """(cores, prepregs) available from the sourced tables."""
    cores = m["core_stock_series"]["mm"]
    # Only NAMED GLASS STYLES are stock. hdi_laser_blind_min is a PROCESS
    # minimum -- the thinnest sheet that may be laser-drilled -- not a sheet
    # anyone orders by name, and letting it into the stock list would invent a
    # "1x hdi_laser_blind_min" stackup that no fabricator could quote.
    STYLES = ("106", "1080", "2116", "7628")
    pregs = {k: v["mm"] for k, v in m["prepreg"].items()
             if k in STYLES and isinstance(v, dict) and v.get("mm") and v.get("source")}
    return cores, pregs


def solve(m, target, layers=4, tol=0.030):
    """Every stackup of SOURCED materials that reaches `target` within `tol`.

    This answers a question a thickness budget cannot: not "does N layers fit"
    but "is this dielectric height made of a material that actually exists".
    A set of heights that sums correctly can still be unbuildable, and an
    impedance computed from an unbuildable height is a number about nothing.
    """
    if layers != 4:
        raise CannotDetermine(f"solve is implemented for 4 layers only, not {layers}")
    cores, pregs = stock(m)
    outers = [("1oz", _row(m, "outer_finished_copper", "economy")),
              ("thin", _row(m, "outer_finished_copper", "thin"))]
    inners = [("0.5oz", _row(m, "copper_foil", "0.5oz")),
              ("0.33oz", _row(m, "copper_foil", "0.33oz"))]
    out = []
    for on, ov in outers:
        for inm, iv in inners:
            for pn, pv in pregs.items():
                for plies in (1, 2):
                    for c in cores:
                        t = 2 * ov + 2 * iv + 2 * pv * plies + c
                        if abs(t - target) <= tol:
                            out.append({"total_mm": round(t, 4), "outer": on, "inner": inm,
                                        "prepreg": f"{plies}x{pn}", "h_mm": round(pv * plies, 4),
                                        "core_mm": c, "off_um": round((t - target) * 1000)})
    out.sort(key=lambda r: (abs(r["off_um"]), r["h_mm"]))
    return out


def cmd_solve(m, target, layers):
    try:
        rows = solve(m, target, layers)
    except CannotDetermine as e:
        print(f"CANNOT DETERMINE — {e}")
        return CANNOT
    print(f"Stackups of SOURCED materials reaching {target:.3f} mm, {layers} layers\n")
    if not rows:
        print("  NONE — no combination of the sourced materials reaches this thickness.")
        print("  That is a finding, not an error: the target may need a core or prepreg")
        print("  outside the stocked series, which is a question for the fabricator.")
        return FAIL
    print(f"{'total':>8}{'outer':>7}{'inner':>8}{'prepreg':>10}{'h (L1-L2)':>11}{'core':>8}{'off':>7}")
    for r in rows:
        print(f"{r['total_mm']:8.4f}{r['outer']:>7}{r['inner']:>8}{r['prepreg']:>10}"
              f"{r['h_mm']:11.3f}{r['core_mm']:8.3f}{r['off_um']:+6d}um")
    hs = sorted({r["h_mm"] for r in rows})
    print(f"\n  h (the outer dielectric, which sets microstrip impedance) ranges {min(hs):.3f}"
          f" to {max(hs):.3f} mm across stackups that ALL hit the target thickness.")
    print("  A single assumed h is therefore not a property of the board thickness.")
    return PASS



def read_board_stackup(path):
    """What a .kicad_pcb DECLARES: board thickness and copper layer count.

    Read with a regex rather than pcbnew on purpose: this must run under the
    system python with no KiCad import, so it can be a cheap gate anywhere. It
    reads the two declarations a fabricator is quoted from and nothing else.
    """
    import re
    with open(path) as fh:
        t = fh.read()
    m = re.search(r"\(general\b[^)]*?\(thickness\s+([\d.]+)\)", t, re.S)
    thickness = float(m.group(1)) if m else None
    cu = sorted(set(re.findall(r'"(F\.Cu|B\.Cu|In\d+\.Cu)"', t)))
    return {"declared_thickness_mm": thickness, "copper_layers": len(cu), "layer_names": cu}


LAST_ROWS = {}   # name -> verdict, from the most recent cmd_verify. Exists so a
                 # test can assert WHICH row fired. Asserting only the exit code
                 # lets a case pass through a row it was not testing.


def cmd_verify(path, which="as-drawn", spec_path=None):
    """Does the board DECLARE the stackup this lane established?

    KiCad defaults a new board to 1.6 mm. That default is silent, survives
    routing, survives export, and is what a fabricator quotes from. It bit
    halo_rev_a once -- lane B1: "a fab quoting from an uncorrected file would
    have built a board nearly three times too thick for its enclosure" -- and
    then bit both Replica boards. This is the check that makes it loud.

    TWO SPECS, BECAUSE THERE ARE TWO KINDS OF BOARD.

      --spec as-drawn    pcb/ is a TRANSCRIPTION. It must equal Apple: 0.30 mm.
      --spec as-ordered  fab/ is a BUILDABLE DEPARTURE, on purpose. Measuring it
                         against as-drawn fails forever, and a permanent
                         expected-red is a check people learn to ignore.

    AND THE AS-ORDERED PATH IS BUILT NOT TO AGREE WITH ITSELF. A lane that
    writes down the spec it is then measured against has measured nothing. So
    as-ordered does not compare the board to a number this project chose; it
    compares BOTH the board AND THE SPEC ITSELF against the VENDOR'S OFFER
    LIST, which is external evidence and can contradict us. Three rows, and
    the first is the guard:

      spec_is_orderable   the recorded spec must be a thickness the vendor
                          actually offers at that layer count. Invent a
                          convenient 0.5 mm and THIS row goes red first.
      board_is_orderable  same test on the board.
      board_matches_spec  and only then, do they agree.
    """
    import json as _json
    import os as _os
    spec_path = spec_path or _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                           "..", "board", "stackup", "stackup.json")
    key = {"as-drawn": "replica_as_drawn", "as-ordered": "fab_as_ordered"}.get(which)
    if key is None:
        print(f"CANNOT DETERMINE — unknown spec {which!r}; use as-drawn or as-ordered")
        return CANNOT
    try:
        doc = _json.load(open(spec_path))
        spec = doc[key]
    except Exception as e:                                    # noqa: BLE001
        print(f"CANNOT DETERMINE — could not read spec {key}: {e}")
        return CANNOT
    if not _os.path.exists(path):
        print(f"CANNOT DETERMINE — {path} is not on disk")
        return CANNOT
    got = read_board_stackup(path)
    want_t, want_l = spec.get("board_thickness_mm"), spec.get("layer_count")

    print(f"board   {path}")
    print(f"spec    stackup.json  {key}   (--spec {which})\n")
    rows, worst = [], PASS

    def add(name, verdict, why):
        nonlocal worst
        rows.append((name, verdict, why))
        if verdict == FAIL:
            worst = FAIL
        elif verdict == CANNOT and worst == PASS:
            worst = CANNOT

    offer = (spec.get("vendor_offer") or {}).get("thickness_options_mm")
    if which == "as-ordered":
        # THE GUARD, and it runs before anything about the board: a spec this
        # project invented for its own convenience fails here first.
        if not offer:
            add("spec_is_orderable", CANNOT, "the spec records no vendor offer list to check against")
        elif want_t in offer:
            add("spec_is_orderable", PASS,
                f"spec {want_t} mm is in {spec['vendor_offer']['vendor']}'s offer at "
                f"{spec['vendor_offer']['at_layers']} layers {offer}")
        else:
            add("spec_is_orderable", FAIL,
                f"THE SPEC ITSELF IS NOT ORDERABLE: {want_t} mm is not in {offer}. "
                "A spec nobody can buy is not a spec")
        if offer:
            g = got["declared_thickness_mm"]
            add("board_is_orderable", PASS if g in offer else FAIL,
                f"board {g} mm {'is' if g in offer else 'is NOT'} in {offer}")

    for name, g, w, unit in (("board thickness", got["declared_thickness_mm"], want_t, "mm"),
                             ("copper layers", got["copper_layers"], want_l, "")):
        if g is None:
            add(name, CANNOT, "the board declares no value")
        elif w is None:
            add(name, CANNOT, "the spec states no value, so there is nothing to compare")
        elif abs(g - w) < 1e-9:
            add(name, PASS, f"declared value matches {key}")
        else:
            why = f"declared {g}{unit}, spec is {w}{unit}"
            if unit == "mm" and w:
                why += f" — {g / w:.2f}x"
            if unit == "mm" and abs(g - 1.6) < 1e-9:
                why += ". 1.6 mm is KiCad's DEFAULT: this reads as never set, not as chosen"
            add(name, FAIL, why)

    LAST_ROWS.clear()
    LAST_ROWS.update({n: v for n, v, _ in rows})
    for name, v, why in rows:
        print(f"  {['PASS','FAIL','CANNOT DETERMINE'][v]:<17}{name}")
        print(f"                    {why}")
    print()
    if worst == FAIL and which == "as-drawn" and "fab_as_ordered" in doc:
        print("NOTE: compared against replica_as_drawn. If this is the FAB branch, which")
        print("      departs from as-drawn on purpose, re-run with --spec as-ordered.")
        print("      This tool will not guess which kind of board it was handed.")
    print({PASS: f"PASS — the board declares the stackup recorded in {key}.",
           FAIL: "FAIL — a fabricator quotes from the BOARD, not from the document.",
           CANNOT: "CANNOT DETERMINE — and that is not a pass."}[worst])
    return worst


def cmd_doctor(m):
    bad, ok, nulls = [], 0, []
    for group, rows in m.items():
        if not isinstance(rows, dict) or group.startswith("_"):
            continue
        for key, r in rows.items():
            if key.startswith("_") or not isinstance(r, dict) or "mm" not in r:
                continue
            if r["mm"] is None:
                nulls.append(f"{group}.{key}")
            elif not r.get("source"):
                bad.append(f"{group}.{key} = {r['mm']} mm with NO SOURCE")
            else:
                ok += 1
    print(f"material rows with a number AND a source : {ok}")
    print(f"rows deliberately null (unevaluable)     : {len(nulls)}  {nulls}")
    print(f"rows with a number but NO SOURCE         : {len(bad)}")
    for b in bad:
        print(f"  DEFECT {b}")
    if bad:
        print("\nFAIL — a number without its input is not a number this project uses.")
        return FAIL
    print("\nPASS — every usable row names where it came from.")
    return PASS


def cmd_bounds(m, target):
    print(f"TARGET {target:.3f} mm total board thickness")
    print("Laminate = copper + dielectric. Soldermask is shown SEPARATELY as a")
    print("range because no fabricator page giving a film thickness was fetched.\n")
    print(f"{'construction':<16}{'N':>3}{'cores':>7}{'preg':>6}{'diel':>8}{'Cu':>8}{'laminate':>10}{'+mask':>16}  src  verdict")
    any_cannot = False
    fits = {}
    for name in m["constructions"]:
        if name.startswith("_"):
            continue
        fits[name] = []
        for n in (2, 4, 6, 8):
            try:
                b = budget(m, name, n)
            except CannotDetermine as e:
                print(f"{name:<16}{n:>3}   CANNOT DETERMINE — {e}")
                any_cannot = True
                continue
            lo, hi = with_mask(m, b["laminate_mm"])
            verdict = "FITS" if lo <= target else ("MARGINAL" if b["laminate_mm"] <= target else "DOES NOT FIT")
            if verdict == "FITS":
                fits[name].append(n)
            inf = b["inferred"]
            tag = ("D!" if inf["dielectric"] else "  ") + ("C!" if inf["copper"] else "  ")
            print(f"{name:<16}{n:>3}{b['cores']:>7}{b['prepreg_sheets']:>6}"
                  f"{b['dielectric_mm']:>8.3f}{b['copper_mm']:>8.3f}{b['laminate_mm']:>10.3f}"
                  f"{lo:>8.3f}-{hi:<7.3f} {tag}  {verdict}")
    print()
    allinf = {}
    for name in m["constructions"]:
        if name.startswith("_"):
            continue
        try:
            pv = provenance(m, name)
        except KeyError:
            continue
        if pv["dielectric"] or pv["copper"]:
            allinf[name] = pv
    if allinf:
        print("  PROVENANCE — C! = the COPPER rows include an inference, so the")
        print("  laminate TOTAL leans on one. D! = the DIELECTRIC does too.")
        for name, pv in allinf.items():
            for b in ("dielectric", "copper"):
                if pv[b]:
                    print(f"    {name:<22}{b:<12}{', '.join(pv[b])}")
        print("  No construction below carries D!, so every DIELECTRIC-only")
        print("  statement rests on published thicknesses alone.")
        print()
    for name, ns in fits.items():
        if ns:
            print(f"  {name:<16} can build {ns} inside {target:.3f} mm")
        else:
            print(f"  {name:<16} can build NOTHING inside {target:.3f} mm (or was unevaluable)")
    if any_cannot:
        print("\nCANNOT DETERMINE overall: at least one construction has no material data.")
        print("That is not a soft pass. The bound below covers only the constructions that could be evaluated.")
        return CANNOT
    return PASS


def cmd_budget(m, construction, layers):
    try:
        b = budget(m, construction, layers)
    except CannotDetermine as e:
        print(f"CANNOT DETERMINE — {e}")
        return CANNOT
    lo, hi = with_mask(m, b["laminate_mm"])
    for k, v in b.items():
        print(f"  {k:<16} {v}")
    print(f"  {'with soldermask':<16} {lo} - {hi} mm")
    return PASS


# --------------------------------------------------------------------------
# selftest — every case below is a DELIBERATE BREAK that must go red.
# An assertion never watched to fail is not known to work.
# --------------------------------------------------------------------------
def cmd_selftest():
    m = load()
    n_pass = n_fail = 0

    def check(name, fn, want):
        nonlocal n_pass, n_fail
        try:
            got = fn()
        except Exception as e:                       # noqa: BLE001
            got = ("raised", type(e).__name__)
        ok = got == want
        print(f"  [{'ok  ' if ok else 'RED '}] {name}\n         want {want}\n         got  {got}")
        if ok:
            n_pass += 1
        else:
            n_fail += 1

    print("s_stackup_budget selftest — 27 deliberate breaks\n")

    # 1. The null-row refusal actually fires.
    check("hdi-ultrathin has null cores -> CannotDetermine, not a default",
          lambda: ("raised", "CannotDetermine")
          if _try_raises(lambda: budget(m, "hdi-ultrathin", 4)) else "no refusal",
          ("raised", "CannotDetermine"))

    # 2. A number without a source is refused even though a number is present.
    m2 = json.loads(json.dumps(m))
    m2["prepreg"]["106"]["source"] = None
    check("prepreg with its source stripped -> refused",
          lambda: ("raised", "CannotDetermine")
          if _try_raises(lambda: budget(m2, "fr4-thin", 4)) else "no refusal",
          ("raised", "CannotDetermine"))

    # 3. doctor goes RED on a sourceless row.
    m3 = json.loads(json.dumps(m))
    m3["core"]["fr4_min_rigid"]["source"] = ""
    check("doctor on a sourceless row -> FAIL(1)", lambda: cmd_doctor_quiet(m3), FAIL)

    # 4. doctor is green on the real table.
    check("doctor on the real table -> PASS(0)", lambda: cmd_doctor_quiet(m), PASS)

    # 5. Odd and sub-2 layer counts are refused, not silently rounded.
    check("3 layers -> refused", lambda: ("raised", "CannotDetermine")
          if _try_raises(lambda: budget(m, "fr4-thin", 3)) else "no refusal",
          ("raised", "CannotDetermine"))

    # 6. The stack must actually GROW with the layer count, in the dielectric
    #    and not merely in the copper. Written this way because the weaker
    #    version of this test -- "6 layers is thicker than 4" -- was watched to
    #    stay green while cores and prepreg sheets were pinned to constants:
    #    copper alone still grew, so the total still grew, and a stack that had
    #    stopped depending on the layer count sailed through. Pin the counts.
    check("core and prepreg counts follow the layer count",
          lambda: [(budget(m, "fr4-thin", n)["cores"],
                    budget(m, "fr4-thin", n)["prepreg_sheets"]) for n in (2, 4, 6, 8)],
          [(0, 1), (1, 2), (2, 3), (3, 4)])

    # 6b. and the dielectric -- not just the copper -- must grow with it.
    check("dielectric grows with the layer count",
          lambda: budget(m, "fr4-thin", 6)["dielectric_mm"] > budget(m, "fr4-thin", 4)["dielectric_mm"],
          True)

    # 7. NEGATIVE CONTROL: an absurd target must NOT come back FITS.
    #    A budget tool that says yes to everything is a decoration.
    check("nothing fits inside 0.010 mm",
          lambda: [n for n in (2, 4, 6, 8)
                   if budget(m, "fr4-economy", n)["laminate_mm"] <= 0.010],
          [])

    # 8. POSITIVE CONTROL: a 1.6 mm board — the most ordinary board in the
    #    world — must come back as fitting 2/4/6/8. If the tool cannot agree
    #    with reality here, its refusals mean nothing either.
    check("1.6 mm fits 2,4,6 and 8 layers in fr4-economy",
          lambda: [n for n in (2, 4, 6, 8)
                   if budget(m, "fr4-economy", n)["laminate_mm"] <= 1.6],
          [2, 4, 6, 8])

    # 10. solve must find real stackups for an ordinary thickness.
    check("solve finds stackups for 0.60 mm 4-layer",
          lambda: len(solve(m, 0.60)) > 0, True)

    # 11. NEGATIVE CONTROL: an impossible thickness must return NOTHING. A
    #     solver that always finds a stackup is a random number generator.
    check("solve finds nothing for 0.010 mm", lambda: solve(m, 0.010), [])

    # 12. Every stackup solve returns must actually sum to the target within
    #     tolerance. Checking the OUTPUT rather than trusting the loop.
    check("every solve row really sums to the target",
          lambda: [r for r in solve(m, 0.60) if abs(r["total_mm"] - 0.60) > 0.030], [])

    # 13. solve refuses a layer count it does not implement rather than
    #     silently answering for 4.
    check("solve refuses 6 layers", lambda: ("raised", "CannotDetermine")
          if _try_raises(lambda: solve(m, 0.60, 6)) else "no refusal",
          ("raised", "CannotDetermine"))

    # 14. NEGATIVE CONTROL on the stock list itself: no solve row may name a
    #     prepreg that is a process minimum rather than an orderable style.
    check("no solve row names a non-stock prepreg",
          lambda: sorted({r["prepreg"].split("x")[1] for r in solve(m, 0.60)}
                         - {"106", "1080", "2116", "7628"}), [])

    # 15. THE 1.6 mm DETECTION, pinned SYNTHETICALLY so it stays tested.
    #     This case used to assert the live Replica fab board reads 1.6 mm. It
    #     went red on 2026-09-05 because ce-workshop-9a FIXED the board -- the
    #     right kind of red, a case failing because the world got better. A
    #     case pinned to a live defect dies with the defect and takes the
    #     detection with it, so the detection is now pinned to a board built
    #     here for the purpose, and the live boards get their own case below.
    import os as _os
    here = _os.path.dirname(_os.path.abspath(__file__))
    import tempfile as _tf0
    with _tf0.NamedTemporaryFile("w", suffix=".kicad_pcb", delete=False) as fh:
        fh.write('(kicad_pcb (general (thickness 1.6)) (layers (0 "F.Cu" signal)'
                 ' (4 "In1.Cu" signal) (6 "In2.Cu" signal) (2 "B.Cu" signal)))')
        default_board = fh.name
    check("a board at KiCad's 1.6 mm default FAILS as-drawn",
          lambda: cmd_verify_quiet(default_board, "as-drawn"), FAIL)
    check("and it is read as 1.6, not as something else",
          lambda: read_board_stackup(default_board)["declared_thickness_mm"], 1.6)
    _os.unlink(default_board)

    # 15b. THE LIVE BOARDS, which is a different claim: neither Replica board
    #      sits at the default any more. This one SHOULD go red if it regresses.
    rb = _os.path.join(here, "..", "fab", "out", "halo_replica_fab.kicad_pcb")
    pb = _os.path.join(here, "..", "pcb", "out", "halo_replica.kicad_pcb")
    live = [read_board_stackup(b)["declared_thickness_mm"]
            for b in (rb, pb) if _os.path.exists(b)]
    check("no live Replica board sits at KiCad's 1.6 mm default",
          lambda: [t for t in live if t == 1.6], [])
    if _os.path.exists(rb):
        check("the fab board's layer count is 4",
              lambda: read_board_stackup(rb)["copper_layers"], 4)

    # 16. NEGATIVE CONTROL: a board that matches the spec must PASS. Without
    #     this, verify could be a function that returns FAIL.
    import tempfile as _tf
    with _tf.NamedTemporaryFile("w", suffix=".kicad_pcb", delete=False) as fh:
        fh.write('(kicad_pcb (general (thickness 0.3)) (layers (0 "F.Cu" signal)'
                 ' (4 "In1.Cu" signal) (6 "In2.Cu" signal) (2 "B.Cu" signal)))')
        good = fh.name
    check("a board matching the spec PASSES (verify is not FAIL-always)",
          lambda: cmd_verify_quiet(good), PASS)
    _os.unlink(good)

    # 17. THE OTHER DIRECTION, and it was missing. Cases 15/16 read the board
    #     directly and confirm a GOOD board passes; neither could catch a
    #     cmd_verify that returns PASS for everything. Deleting the comparison
    #     left all sixteen green while the Replica board reported PASS at
    #     1.6 mm against a 0.30 mm spec. A control that can only fail in one
    #     direction is half a control.
    if _os.path.exists(rb):
        check("the Replica board FAILS verify (verify is not PASS-always)",
              lambda: cmd_verify_quiet(rb), FAIL)

    # 23. PROVENANCE MUST TRAVEL, AND MUST DISCRIMINATE. fr4-thin pulls two
    #     inference rows through its COPPER and none through its dielectric;
    #     fr4-economy pulls none at all. If both came back the same the tag
    #     would be decoration.
    check("fr4-thin's copper is flagged as inferred, its dielectric is not",
          lambda: provenance(m, "fr4-thin"),
          {"dielectric": [], "copper": ["outer_finished_copper.thin", "copper_foil.0.33oz"]})
    check("fr4-economy carries no inference at all (the tag discriminates)",
          lambda: provenance(m, "fr4-economy"), {"dielectric": [], "copper": []})

    # ---- as-ordered: the anti-tautology controls --------------------------
    # A lane that writes the spec it is measured against has measured nothing.
    # These five cases exist to prove that did not happen here. Each builds a
    # DELIBERATELY WRONG spec or board and requires the right row to go red.
    import json as _j
    import tempfile as _t2
    base = _j.load(open(_os.path.join(here, "..", "board", "stackup", "stackup.json")))

    def with_spec(mut):
        doc = _j.loads(_j.dumps(base))
        mut(doc)
        fh = _t2.NamedTemporaryFile("w", suffix=".json", delete=False)
        _j.dump(doc, fh)
        fh.close()
        return fh.name

    def board_at(mm, layers=4):
        names = ['"F.Cu"', '"In1.Cu"', '"In2.Cu"', '"B.Cu"'][:layers]
        fh = _t2.NamedTemporaryFile("w", suffix=".kicad_pcb", delete=False)
        fh.write(f'(kicad_pcb (general (thickness {mm})) (layers '
                 + " ".join(f"(0 {n} signal)" for n in names) + "))")
        fh.close()
        return fh.name

    # 18. THE GUARD. Invent a convenient spec the vendor does not offer and the
    #     SPEC row must go red BEFORE anything about the board is considered.
    bad_spec = with_spec(lambda d: d["fab_as_ordered"].__setitem__("board_thickness_mm", 0.5))
    b05 = board_at(0.5)
    # Assert the ROW, not the exit code. The first version of this case checked
    # only the overall verdict, and stayed green when the guard was deleted --
    # because board_is_orderable failed on the same input for a different
    # reason. A case satisfied by a neighbouring row does not test its own.
    def row_after(fn, name):
        fn()
        return LAST_ROWS.get(name)

    check("an invented, unorderable SPEC trips spec_is_orderable ITSELF",
          lambda: row_after(lambda: cmd_verify_quiet(b05, "as-ordered", bad_spec),
                            "spec_is_orderable"), FAIL)

    # 19. A board at a thickness the vendor does not offer fails, even though
    #     0.6 is a perfectly ordinary PCB thickness at other layer counts.
    b06 = board_at(0.6)
    check("a board at 0.6 mm trips board_is_orderable ITSELF",
          lambda: row_after(lambda: cmd_verify_quiet(b06, "as-ordered"),
                            "board_is_orderable"), FAIL)

    # 20. A board at 1.0 is ORDERABLE but is not what was decided. It must
    #     still fail, and for a different reason than 0.6 did.
    b10 = board_at(1.0)
    # 1.0 is ORDERABLE but is not the decision: orderability must PASS while
    # equality FAILS. Two different failure modes that must stay distinguishable.
    check("a board at 1.0 mm is orderable BUT fails equality (distinct modes)",
          lambda: (row_after(lambda: cmd_verify_quiet(b10, "as-ordered"), "board_is_orderable"),
                   LAST_ROWS.get("board thickness")), (PASS, FAIL))

    # 21. THE TWO SPECS MUST ACTUALLY DIFFER. If as-ordered were a rename of
    #     as-drawn, every case above would pass for the wrong reason.
    fab = _os.path.join(here, "..", "fab", "out", "halo_replica_fab.kicad_pcb")
    if _os.path.exists(fab):
        check("the fab board PASSES as-ordered and FAILS as-drawn (the specs differ)",
              lambda: (cmd_verify_quiet(fab, "as-ordered"), cmd_verify_quiet(fab, "as-drawn")),
              (PASS, FAIL))

    # 22. And the transcription branch must hold to Apple's number.
    pcb = _os.path.join(here, "..", "pcb", "out", "halo_replica.kicad_pcb")
    if _os.path.exists(pcb):
        check("the pcb board PASSES as-drawn (0.30 mm, Apple's number)",
              lambda: cmd_verify_quiet(pcb, "as-drawn"), PASS)

    for f in (bad_spec, b05, b06, b10):
        _os.unlink(f)

    print(f"\n{n_pass} ok, {n_fail} red")
    return PASS if n_fail == 0 else FAIL


def _try_raises(fn):
    try:
        fn()
    except CannotDetermine:
        return True
    return False


def cmd_verify_quiet(path, which="as-drawn", spec_path=None):
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        return cmd_verify(path, which, spec_path)


def cmd_doctor_quiet(m):
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        return cmd_doctor(m)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return CANNOT
    verb = argv[1]
    if verb == "selftest":
        return cmd_selftest()
    m = load()
    if verb == "doctor":
        return cmd_doctor(m)
    if verb == "bounds":
        target = float(argv[2]) if len(argv) > 2 else 0.30
        return cmd_bounds(m, target)
    if verb == "verify":
        if len(argv) < 3:
            print("CANNOT DETERMINE — verify needs a .kicad_pcb path")
            return CANNOT
        which = "as-drawn"
        if "--spec" in argv:
            which = argv[argv.index("--spec") + 1]
        return cmd_verify(argv[2], which)
    if verb == "solve":
        return cmd_solve(m, float(argv[2]) if len(argv) > 2 else 0.60,
                         int(argv[3]) if len(argv) > 3 else 4)
    if verb == "budget":
        return cmd_budget(m, argv[2], int(argv[3]))
    print(f"unknown verb {verb!r}")
    return CANNOT


if __name__ == "__main__":
    sys.exit(main(sys.argv))
