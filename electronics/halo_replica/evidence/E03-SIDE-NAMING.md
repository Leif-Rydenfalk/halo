# E03 — the side-naming resolution, and why no measurement changed

*halo Replica lane (orchestrator), 2026-09-05, under a quota-RED ceiling.*

## What happened

`docs/REFERENCE-TEARDOWN.md` contradicted itself. Its header (halo commit 391f676) said
**"front = the component side"**, following Apple's FCC caption. Its §2 legend said
**"F = front/top side (battery contacts, coil, NFC)"** — the opposite face. Lane L4 found it.

**The legend wins.** The halo lane resolved it at commit c065273, and its reasoning is the
part worth keeping: *every* (F) and (B) tag in that document's tables was written under the
§2 legend. Redefining the header silently **inverted the meaning of every tag in the document
without touching one of them** — a worse defect than the ambiguity it was fixing.

I had taken the header on that lane's authority and written **"FRONT = COMPONENT SIDE, state
it at the top of every file"** into all five of my lane briefs. So the wrong convention
propagated through this entire lane.

## Why this cost nothing measured, which is the important part

**Every file in this lane correctly identifies which photograph shows which physical face.**
FCC internal photo 6 shows the side carrying the SoC and the shield can; O'Flynn's
`backside-*` images show that same face; his `frontside-*` images show the battery-contact
and coil side. Not one file got that wrong.

What was wrong is only the **word** applied to that face. So this is a **relabelling, not a
re-measurement**. No number in `metrology/`, `bom/`, `board/` or `evidence/` moves. The scale
bases, the outline profiles, the package sizes, the coil geometry and the layer count are all
unaffected.

## The house style, adopted lane-wide

Lane L4 proposed it, the halo lane has since adopted it into the dossier itself, and it is now
this lane's rule:

> **NAME FACES BY WHAT IS ON THEM.**
> "the side carrying the SoC and the shield can" · "the side carrying the battery contacts
> and the coil"

It is unambiguous under every convention, it survives the source document changing, and it
future-proofs against the next source that picks a fourth word. **Do not write "front" or
"back" of this board in any new file.** Three sources use those words for two different faces.

## What was swept, and what was not

**Done:** the user-visible captions — the render title and the comparison panel's convention
line, which are what a person actually reads off the picture.

**NOT done, and listed here rather than left silent:** the docstrings and `side_convention`
string fields in `tools/p_render.py`, `p_compare.py`, `p_outline.py`, `m_board_outline.py`,
`m_outline_fit.py`, `c_register.py`, and the `**side**` note in `bom/BOM-RECONSTRUCTED.md`
still carry "FRONT = component side". They are **descriptively correct about the physical face
and wrong only in the word**, so they mislead a reader without corrupting a number. They were
left because a blind textual flip of FRONT→BACK across working tools under a quota ceiling
risks introducing a real error to fix a cosmetic one, and `BOM-RECONSTRUCTED.md` is generated
— its source `bom.json` must be edited, not the markdown.

**Handoff:** sweep those to the house style, regenerate `BOM-RECONSTRUCTED.md` from
`bom.json` rather than editing it, and re-render both pictures.

## The thing worth keeping

An authority I trusted was wrong, and I propagated it into five briefs within minutes of
receiving it, with an instruction to repeat it at the top of every file. **Nothing in my
process would have caught it** — it was caught by a lane beneath me reading the source
document closely enough to notice it disagreed with itself. The general lesson is not "check
your sources"; it is that **a convention is exactly the kind of claim that gets propagated
faster than it gets checked**, because it looks like bookkeeping rather than like a finding.
