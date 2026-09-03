# Contributing to halo

## The hard rules

These are not preferences. A pull request that breaks one is closed.

1. **No stealth patches.** Anything that removes or disables the sound maker,
   suppresses the separated-state alert, cycles keys faster than the DULT
   schedule, or otherwise defeats platform tracker detection will be closed.
   The reasoning, with sources, is in `docs/ANTI-STALKING.md`. A researcher who
   needs such a build for defensive testing should read that document first and
   open an issue, not a pull request.
2. **No MFi-derived material.** If you have read Apple's Find My Network
   Accessory specification under its non-disclosure agreement, do not
   contribute to the firmware. halo is clean-room from the PoPETs 2021 paper
   and public reverse-engineering (decision D5).
3. **Every number carries its source.** A dimension, a price, a current, a
   dB figure: give the URL and the date you read it, or mark it measured and
   say with what. A claim with no source is not accepted, and "it is well
   known" is not a source.
4. **A verdict is PASS, FAIL or CANNOT DETERMINE.** Never a quiet pass. If a
   check could not run, the report says so.

## The shape of the repository

Read `GOAL.md` for what this is, `SPEC.md` for what it must do, `DECISIONS.md`
for why each question was answered the way it was, and `MISSION.md` for what
"finished" means. `research/` holds the dossiers every decision rests on, with
`research/sources.tsv` as the index of every source used.

## Licensing

See `LICENSE.md`. Contributions are accepted under the licence of the directory
they land in. By opening a pull request you agree to that.
