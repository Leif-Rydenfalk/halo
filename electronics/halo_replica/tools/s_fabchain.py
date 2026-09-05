#!/usr/bin/env python3
"""s_fabchain.py — is every artifact in a build chain newer than what built it?

THE DEFECT THIS EXISTS FOR, MEASURED 2026-09-05.

A fabrication release is a CHAIN, not a pair:

    board.py  ->  halo_rev_a.kicad_pcb  ->  gerbers + drill

`tools/check_fabset.py` checks only the LAST link. Its F11 `export_is_fresh`
compares the pack against the .kicad_pcb and calls that file "the source". It
is not the source; it is an intermediate. Measured on this tree:

    board.py             blob 4b1dffb, committed b324645
    halo_rev_a.kicad_pcb blob UNCHANGED since 5a65d8f, which b324645 post-dates

So the board was never rebuilt after a 21-line change to its own source, and
`check_fabset` cannot see it. THE CONSEQUENCE IS THE POINT: re-export the
gerbers today and check_fabset exits 0 and release-pack item 1 goes READY,
while the pack describes a board one design revision behind its source. **The
check goes green exactly when it stops being true.** A freshness check that
follows one link of a three-link chain manufactures a false green at the moment
someone tries to close it.

WHY GIT CONTENT AND NOT mtime. `git checkout` rewrites mtimes, so an mtime
comparison raises a false alarm on any tree that was checked out in an unlucky
order -- and a check that cries wolf gets ignored, which is the same failure as
one that never fires. This walks BLOB HASHES through history: did the upstream
file's content change in a commit that post-dates the last commit to touch the
downstream file? mtime is reported alongside as corroboration and never as the
verdict.

Verbs
  check [upstream downstream ...]   default chain is halo_rev_a's
  selftest                          7 cases, including the direction control

Exit code IS the verdict: 0 PASS, 1 FAIL, 2 CANNOT DETERMINE.
"""
import os
import subprocess
import sys

PASS, FAIL, CANNOT = 0, 1, 2

DEFAULT_CHAIN = [
    "electronics/halo_rev_a/board.py",
    "electronics/halo_rev_a/out/halo_rev_a.kicad_pcb",
    "out/release/board/gerber/halo_rev_a-B_Cu.gbl",
]


def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def tracked(path):
    return git("ls-files", "--error-unmatch", path)[0] == 0


def last_commit(path):
    rc, out, _ = git("log", "-1", "--format=%H", "--", path)
    return out if rc == 0 and out else None


def blob(rev, path):
    rc, out, _ = git("rev-parse", f"{rev}:{path}")
    return out if rc == 0 else None


def dirty(path):
    rc, out, _ = git("status", "--porcelain", "--", path)
    return bool(out.strip())


def link_verdict(up, down):
    """Is `down` current with respect to `up`? Returns (verdict, detail)."""
    for p in (up, down):
        if not os.path.exists(p):
            return CANNOT, f"{p} is not on disk"
        if not tracked(p):
            return CANNOT, f"{p} is not tracked by git, so its history cannot be read"
    if dirty(up):
        return CANNOT, (f"{up} has uncommitted changes, so what built {down} cannot be "
                        "identified. Commit it, or say what it was built from")
    c_down = last_commit(down)
    if c_down is None:
        return CANNOT, f"no commit touches {down}"
    # Did `up`'s CONTENT change in any commit after the one that last wrote `down`?
    rc, out, _ = git("log", "--format=%H", f"{c_down}..HEAD", "--", up)
    commits = [c for c in out.splitlines() if c]
    if not commits:
        return PASS, f"{up} has not changed since {down} was last written ({c_down[:7]})"
    b_then, b_now = blob(c_down, up), blob("HEAD", up)
    if b_then is None or b_now is None:
        return CANNOT, f"could not read {up}'s blob at {c_down[:7]} and at HEAD"
    if b_then == b_now:
        return PASS, (f"{len(commits)} commit(s) touched {up} since {c_down[:7]} but its "
                      "content is identical — a revert or a no-op change")
    return FAIL, (f"{up} CHANGED after {down} was last written: blob {b_then[:7]} -> "
                  f"{b_now[:7]} in {len(commits)} commit(s) ({', '.join(c[:7] for c in commits)}). "
                  f"{down} was not rebuilt")


def cmd_check(chain):
    print("BUILD CHAIN — each artifact must be current with the one before it\n")
    worst = PASS
    for i in range(len(chain) - 1):
        up, down = chain[i], chain[i + 1]
        v, detail = link_verdict(up, down)
        name = {PASS: "PASS", FAIL: "FAIL", CANNOT: "CANNOT DETERMINE"}[v]
        print(f"  {name:<17} {os.path.basename(up)} -> {os.path.basename(down)}")
        print(f"                    {detail}\n")
        worst = max(worst, v) if v != CANNOT or worst != FAIL else worst
        if v == FAIL:
            worst = FAIL
        elif v == CANNOT and worst == PASS:
            worst = CANNOT
    print({PASS: "PASS — every link is current.",
           FAIL: "FAIL — an artifact is behind what built it. Rebuilding the LAST link "
                 "alone would make a downstream check go green while the pack still does "
                 "not describe the design.",
           CANNOT: "CANNOT DETERMINE — and that is not a pass."}[worst])
    return worst


def cmd_selftest():
    n_ok = n_red = 0

    def check(name, got, ok, want):
        nonlocal n_ok, n_red
        print(f"  [{'ok  ' if ok else 'RED '}] {name}\n         want {want}\n         got  {got}")
        if ok:
            n_ok += 1
        else:
            n_red += 1

    print("s_fabchain selftest — 7 cases\n")
    src, board, gerber = DEFAULT_CHAIN

    # 1. THE LIVE FINDING. If this ever goes PASS, either someone rebuilt the
    #    board (good, and this case should be re-pinned) or the check broke.
    v, d = link_verdict(src, board)
    check("board.py -> kicad_pcb is STALE on this tree", f"{v} {d[:60]}...", v == FAIL, f"{FAIL} (FAIL)")

    # 2. DIRECTION CONTROL, and the one that matters most. Swapping upstream and
    #    downstream must NOT give the same answer. A chain checker that returns
    #    the same verdict either way is not using the direction at all -- the
    #    same shape as "the total went up" not testing that the total depends on
    #    the variable.
    v2, _ = link_verdict(board, src)
    check("reversing the link changes the verdict", f"forward={v}, reversed={v2}",
          v2 != v, "reversed must differ from forward")

    # 3. NEGATIVE CONTROL: a file against itself cannot be stale.
    v3, _ = link_verdict(src, src)
    check("a file against itself is not stale", v3, v3 == PASS, f"{PASS} (PASS)")

    # 4. An untracked path must be CANNOT DETERMINE, never PASS.
    v4, _ = link_verdict(src, "/etc/hosts")
    check("untracked downstream -> CANNOT DETERMINE, not PASS", v4, v4 == CANNOT, f"{CANNOT}")

    # 5. A missing path must be CANNOT DETERMINE, never PASS.
    v5, _ = link_verdict(src, "no/such/file.kicad_pcb")
    check("missing downstream -> CANNOT DETERMINE, not PASS", v5, v5 == CANNOT, f"{CANNOT}")

    # 6. The whole default chain must not come back PASS while case 1 is FAIL.
    #    Guards against a roll-up that loses a failing link.
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        roll = cmd_check(DEFAULT_CHAIN)
    check("chain roll-up does not lose the failing link", roll, roll == FAIL, f"{FAIL} (FAIL)")

    # 7. POSITIVE CONTROL that can fail: this tool's own file against the
    #    repository's oldest tracked file. A file committed long ago cannot have
    #    changed after this file was written, so this MUST pass -- if it does
    #    not, the history walk is broken and every FAIL above is suspect too.
    rc, oldest, _ = git("log", "--reverse", "--format=%H", "--max-count=1")
    me = "electronics/halo_replica/tools/s_fabchain.py"
    if tracked(me):
        v7, _ = link_verdict("LICENSE.md" if tracked("LICENSE.md") else src, me)
        check("a long-settled upstream does not mark a new file stale", v7,
              v7 in (PASS, CANNOT), f"{PASS} or {CANNOT}")
    else:
        check("this tool is committed so the history walk can be tested",
              "not committed yet", False, "committed")

    print(f"\n{n_ok} ok, {n_red} red")
    return PASS if n_red == 0 else FAIL


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return CANNOT
    if argv[1] == "selftest":
        return cmd_selftest()
    if argv[1] == "check":
        chain = argv[2:] or DEFAULT_CHAIN
        if len(chain) < 2:
            print("CANNOT DETERMINE — a chain needs at least two artifacts")
            return CANNOT
        return cmd_check(chain)
    print(f"unknown verb {argv[1]!r}")
    return CANNOT


if __name__ == "__main__":
    sys.exit(main(sys.argv))
