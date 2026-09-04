# MECHANICAL — the halo puck enclosure

*Lane M. Everything here is either transcribed from a named source, computed
from the parameters in [`design.py`](../design.py), or **read off the finished
solid** by the measured-check suite in that same file. Where a number is a
calculation rather than a measurement it says so, and where nothing has been
measured the verdict is CANNOT DETERMINE and the test that would settle it is
named. Nothing is asserted.*

Reproduce every number in this page with:

```bash
cd ce-designs/halo
~/dev/ce-workshop/ce-cad/bin/cad design.py          # builds, checks, renders, exports
CE_TRIAD_ROOT=$PWD ~/dev/ce-workshop/bin/triad check --all
```

Companion documents: [SPEC.md](../SPEC.md) §4 (the envelope), [DECISIONS.md](../DECISIONS.md)
**D3** (battery door), **D11a** (the sounder), **D13** (enclosure and tooling),
and [research/07](../research/07-mechanical-enclosure-and-3d-models.md) — lane G's
dossier, which is where every Apple number in this page comes from.

---

## 1. What halo's enclosure is

Four moulded/stamped parts, one bought bender, one cell, three stamped
springs and a bead of silicone.

| # | part | material | process | what it does |
|---|---|---|---|---|
| 1 | `part:halo-shell-top` | PC | injection moulded, **straight pull, no undercut** | the crown. It **is** the loudspeaker diaphragm and the NFC window |
| 2 | `part:halo-carrier` | LCP, LDS grade | injection moulded, **three lifters** + laser direct structuring | the PCB seat, the contact roots, the seal land, the bayonet feet, the antennas |
| 3 | `part:halo-battery-door` | 301 stainless, 0.30 mm | progressive stamping | the user-openable door; press-and-twist |
| 4 | `part:halo-door-seal` | LSR 70 Shore A | moulded in place on the carrier | the radial door seal |
| 5 | `part:halo-battery-contact` ×3 | C5191 phosphor bronze, 0.15 mm | stamped, formed, insert-moulded | the cell's three contacts. There is no holder |
| 6 | `part:halo-piezo-7bb-20-3` | brass + PZT | bought (Murata) | the sounder (D11a) |
| 7 | `part:halo-cr2032` | — | bought | the cell |
| 8 | `part:halo-pcb-blank` | FR4 | 4-layer PCB | the board outline (the copper is the electronics lane's) |

Plus two prototype variants, `part:halo-shell-top-fdm` and
`part:halo-battery-door-fdm`, §8.

**The frame, and it is Apple's own.** Origin on the axis of revolution at the
lowest point of the battery door's outer face; +z toward the crown apex at
z = 7.980; +x through the 6 o'clock bayonet ledge, so D13's three ledges are at
0 / 120 / 240° (6, 10 and 2 o'clock). Every part is **built** in this frame, so
every placement in `assembly:halo-puck` is the identity — a concentric product
has one datum and there is not a coordinate to get wrong.

**The single tooling decision that shapes the whole split.** A bayonet is an
undercut; something must have one. halo puts **every undercut on the carrier**,
which nobody sees, and leaves the cosmetic shell a pure straight pull. Catley
found the AirTag's retaining tabs are *separate plastic pieces glued to the
white shell* at 2, 6 and 10 o'clock — the same problem, solved by gluing rather
than by moving the feature to another part. Three lifters in a non-cosmetic LCP
tool is the cheaper answer, and it deletes an assembly operation.

---

## 2. The stack budget — it closes, and it closes with slack

Every row is on the axis, in the closed state, and every boundary is a variable
in `design.py`. The table is printed by `report_stack()` on every build.

| # | layer | from | to | dz | where the number comes from |
|---|---|---|---|---|---|
| 1 | door skin at the axis, 301 SS | 0.000 | 0.300 | **0.300** | halo's choice. Apple's is **unmeasured** (research/07 §5.2 row 1 is an estimate) |
| 2 | dome sagitta under the cell — dead air | 0.300 | 0.842 | **0.542** | read off Apple's own ordinate table at the cell's Ø20.00 rim |
| 3 | **CR2032** | 0.842 | 4.042 | **3.200** | Maxell datasheet |
| 4 | contact dimple + finger, compressed | 4.042 | 4.292 | **0.250** | 0.100 emboss + 0.150 C5191 stock |
| 5 | carrier deck: finger roots + PCB seat | 4.292 | 4.600 | **0.308** | halo design |
| 6 | **PCB** | 4.600 | 5.200 | **0.600** | halo's choice (Apple's is 0.30) |
| 7 | top-side component allowance inside Ø21.2 | 5.200 | 5.600 | **0.400** | halo keep-out |
| 8 | diaphragm moving gap | 5.600 | 6.280 | **0.680** | halo design |
| 9 | Murata 7BB-20-3 + 0.05 bond line | 6.280 | 6.550 | **0.270** | Murata datasheet + halo |
| 10 | PC crown wall at the axis | 6.550 | 7.980 | **1.430** | derived: flat land at 6.550, Apple's R92 crown above it |
| | **TOTAL** | | | **7.980** | Apple's drawing |

**Verdict: PASS.** The sum is 7.980 mm against the 7.980 mm of Apple's drawing,
and the built assembly measures **31.874 × 31.874 × 7.980 mm** — SPEC §4's
envelope, read off the solid, not asserted.

### 2.1 Why SPEC §4's "about 1.5 mm remains" is no longer the binding constraint

SPEC §4 says a CR2032 (3.20) plus a 3.30 mm internal module spends 81 % of the
height before the cover, leaving about 1.5 mm. **That 3.30 mm is Apple's**, and
Catley measured it with a magnet and a voice coil inside it. D11a deletes both
for a 0.22 mm Murata bender.

halo's equivalent of Apple's module is rows 4–7: **1.558 mm**. The bare bender
therefore **returns 1.742 mm to the budget**, and halo spends it on:

| what | mm | why |
|---|---|---|
| a 0.60 mm PCB instead of Apple's fragile 0.30 | +0.300 | far cheaper to fabricate; Apple's is "likely to cause damage when removed" |
| a real moving gap for the bender | +0.680 | Apple's coil moves in the same air the magnet sits in; a bonded bender needs its own clearance |
| a 1.430 mm crown at the axis, against Apple's ~0.88 residual for wall + clearance | +0.550 | see §4 — the flat internal land |
| unspent | +0.212 | absorbed by rows 4–5 |

**And there is 0.542 mm of reclaimable slack on top of that** — row 2, the dead
air under the cell's centre where the R92 door dome falls away. Emboss a flat
pad in the door's stamping and it comes back. It is not spent today because
nothing needs it; it is recorded here so the next lane knows where the money is.

The binding constraint on halo is therefore **not** the vertical stack. It is
(a) the crown wall thickness, which is an acoustic argument (§4), and (b) the
radial budget, §3.

### 2.2 What does NOT fit, stated plainly

- **A coin-cell holder.** The lowest-profile SMT retainer, Keystone 1057, still
  stands 2 mm above the board; 2 + 3.2 = 5.2 mm of 7.98 before a component.
  Sprung fingers clamped by the door is the only scheme that fits, which is
  exactly what Apple does. §5.
- **A housed buzzer.** The TDK PS1240P02CT meets DULT's loudness at 3 V and is
  3.5 mm tall — 44 % of the whole budget. §4.
- **A screw-down door.** 1.5–2.5 mm of boss depth plus a head, plus metal
  inside Apple's Ø37.31 antenna keep-out (D13).

---

## 3. The radial budget, and every callout used

SPEC §4 lists five stepped diameters. Lane G flagged two of them —
Ø27.90 and Ø27.84 — as **medium confidence**: they are plan-view callouts on
Apple's drawing that the CC BY half-section DXF omits entirely. halo's reading
is below, and it is halo's, not a measurement of an AirTag.

| Ø | what it is in halo | confidence |
|---|---|---|
| **31.874** | maximum outer diameter, at z = 4.339 | Apple's drawing; **measured on our solid** at z 4.263…4.384 |
| **28.94** | the shell's underside lip, at z = 2.290, with the 0.05 chamfer | Apple's drawing |
| **27.90** | the shell's bore — the hole the whole door assembly sits in | halo's reading of a plan-view callout |
| **27.84** | the carrier's three bayonet legs, sitting in that bore | halo's reading of the adjacent callout |
| **25.75 / 25.45** | the door's wall, with the 0.05 mm chamfer at each end | Apple's drawing (Ø25.55 band, Ø25.45 at each end) |
| **23.11** | the carrier's seal land — the widest *continuous* feature in the 0.40 mm band between the door's rim (z 1.890) and the shell's underside (z 2.290) | halo's reading |
| **25.75** | Apple's speaker keep-out, realised as the **diameter of the acoustic surround** and as a declared keep-out volume on the shell | Apple's drawing |
| **37.31** | Apple's antenna keep-out. **Measured: the annulus Ø31.874…Ø37.31 contains no halo material at all**, so the keep-out is entirely the host's obligation | Apple's drawing |

**The metal inside Ø37.31, named rather than hidden.** halo contains seven
conductive parts — the stamped door (Ø26.37 over the tabs), the board and its
copper (Ø26.00), the bender's brass shim (Ø20.00), the cell (Ø20.00) and three
contacts — all inside the Ø31.874 envelope, exactly as the AirTag's are. The
antennas sit *above* them on the carrier's outer wall, which is why Apple's
carrier is where the LDS traces go. **RF performance is ce-rf's lane and is
CANNOT DETERMINE here.**

**The wall at the equator is 2.0 mm.** With a straight Ø27.90 bore at 1° draft
and the outside bulging to Ø31.874, the shell's section at z = 4.34 is
(31.874 − 27.86)/2 = **2.01 mm** against a 0.80 mm crown — a 2.5 : 1 thickness
ratio on a glossy white PC part, which is a sink-mark and warp risk. It is not
avoidable without a collapsible core, because a barrel-shaped cavity wider than
its own mouth is an undercut; and it is not unusual, because Apple's own shell
is the same lens with a hole in it (lane G: 2.94 mm of section per side at the
equator). **Mitigation is a process decision — gate on the rim, long hold, and
accept a matte or lightly textured finish — and it is a first-article item, not
a CAD one.**

---

## 4. Acoustics: why the wall is 0.80 mm and why the land is flat

D11a settles the *part*: a bare Murata 7BB-20-3, Ø20.0 × 0.22 mm, bonded to the
inside of the shell and driven anti-phase from two SoC pins. It does not settle
the *structure*, and the structure is where the output comes from.

### 4.1 The land is flat because a curved one cracks the ceramic

The crown's outer surface is a spherical cap of R ≈ 92 mm, so its inner surface
is R ≈ 91.2 mm. Bonding a flat Ø20 bender to it means bending the bender to
that radius. The 7BB-20-3 is a 0.12 mm brass shim carrying a 0.10 mm PZT disc;
the laminate's neutral axis, weighting each layer by its modulus, sits **0.0944
mm** from the brass face, so the PZT's outer fibre is 0.1256 mm from it and the
strain on conforming is

> ε = y / R = 0.1256 / 91.2 = **0.1377 %**

against a tensile limit for hard PZT of about **0.1 %**. The bender would crack
on assembly. So the shell's **inside is a flat land, Ø21.20 at z = 6.550**,
while the outside keeps Apple's cap. This is not a compromise: a flat, thin,
stiff bond line is what a strain-coupled exciter wants, and it is repeatable in
production in a way a gap-filling adhesive wedge is not.

The cost is that the crown is thicker at the axis (1.430 mm) than at the land
edge (0.800 mm). That turns the acoustic architecture into the one every
loudspeaker uses: **a stiff piston (the Ø21.2 crown, driven in-plane by the
bender) on a compliant surround (the 0.800 mm annulus out to Ø25.75)**.

### 4.2 The wall thickness is chosen by the exciter's authority

An exciter that is far more compliant than the panel it is glued to cannot move
it. The measure is the ratio of flexural rigidities, computed in `design.py`
from the layer moduli:

| crown wall | D_shell (N·mm) | D_piezo / D_shell | reading |
|---|---|---|---|
| 0.60 mm | 0.0479 | 1.32 | best acoustically; below lane G's mouldable minimum |
| **0.80 mm** | **0.1136** | **0.662** | **chosen** |
| 1.00 mm | 0.2219 | 0.339 | |
| 1.20 mm (the FDM variant) | 0.3834 | 0.196 | the printed shell will be markedly quieter |

**0.80 mm is chosen** because the bender still has two-thirds of the crown's
own bending stiffness — real authority — and because 0.80 mm is the wall lane
G sourced as PC's practical minimum for this part ("toughness at 0.8 mm wall,
and a diaphragm stiff enough to radiate", research/07 §6.3). 0.60 mm is the
acoustic optimum and is left on the table deliberately; the first article is
what decides whether it moulds.

Outboard of Ø25.75 the wall steps to **1.20 mm**. That step is not decoration:
it is the **stiffening ring that terminates the diaphragm**, so the acoustic
boundary is a designed feature at exactly the diameter Apple's own "DO NOT
OBSTRUCT" callout gives, rather than wherever the skirt happens to stiffen.

### 4.3 What the design has to deliver, as a displacement

DULT requires **≥ 60 phon at 25 cm**. Between 2 and 5 kHz the ear is *more*
sensitive than at 1 kHz, so asking for 60 dB SPL there is asking for more than
60 phon — a conservative stand-in. Radiating as a monopole of the piston's area:

> x = √2 · p_rms · r / (π ρ f² S) = **0.410 µm** at 3600 Hz, 250 mm

Four tenths of a micron. A 20 mm bender does tens of microns free-air. **The
design is not displacement-limited**, which is the useful result: whatever
decides halo's loudness, it is not the actuator's stroke.

### 4.4 The sealed cavity is not the limiter either

The free air volume inside the puck, **measured** by subtracting every solid
from the product's envelope of revolution, is **1407 mm³** (an upper bound — it
includes the seam gap around the door, which is open to atmosphere). The air
spring behind a Ø21.2 piston is then γP₀S²/V = **12.6 kN/m**, which against the
bender's own 0.451 g resonates at about **840 Hz** — far below the 3.6 kHz drive
point, so at the design frequency the system is mass-controlled and the trapped
air is not what stops it.

### 4.5 And therefore: the SPL is CANNOT DETERMINE

Everything above says the mechanism is sound and nothing above says how loud it
is. Lane G's caveat stands verbatim: *"this is the one thing in this document
that has to be measured on real hardware before it is believed."* iFixit's only
lab figure for an AirTag is 78–80 dB at ~13 cm, and their finding that piezo
rivals were *"just as much, if not more, noise"* is the reason to expect this to
work — not proof that it does.

**Verdict on F3 (≥60 phon at 25 cm): CANNOT DETERMINE.** The test is lane G's
open item 6, and it is §9's first row.

---

## 5. The battery door, and the compliance argument

### 5.1 The mechanism

D3 and D13: a **press-and-twist bayonet, three tabs at 2, 6 and 10 o'clock**,
because it is the only 16 CFR 1263-compliant scheme that costs **zero** vertical
height. halo's realisation:

| feature | geometry |
|---|---|
| door tabs | three, 45° arc, Ø25.55 → **Ø26.60**, z 1.890 → 2.190, formed from the same 0.30 mm stock |
| carrier feet | three, 60° arc, R 12.90 → 13.40, bearing face at **z = 1.890**, body down to z = 1.290 |
| carrier legs | three, 60° arc, R 13.40 → **Ø27.84**/2, z 1.290 → 2.500, joining the feet to the carrier floor |
| entry windows | the three 60° gaps between the legs |
| **detent** | a **square** ridge on each foot, 4° of arc, **0.250 mm** tall, at the closed position's trailing edge |
| closing cam | a 12° ramp on each foot's leading edge, so the closing rotation lifts the tab onto the foot progressively |
| rotation to open | 60° |

The load path is: the contact springs push the cell **down**, the cell pushes
the door **down**, and the tabs bear **up** against the feet. Nothing else
retains the door, which is why the springs are a structural part and not just an
electrical one.

### 5.2 The compliance argument, and it is measured rather than argued

16 CFR 1263 / ANSI-UL 4200A require a **tool, or at least two independent and
simultaneous hand movements**. That is a claim about geometry, so `design.py`
measures it: it moves and rotates the real door solid against the real carrier
solid and reads the shared volume back out of the kernel. Five probes, and
**two of them must be non-zero** — a test that can only pass is not a test.

| probe | expected | measured |
|---|---|---|
| **A** closed, at rest | 0 mm³ — it fits | **0.0000** |
| **B** closed, dropped 0.3 mm | **> 0** — the feet retain it; it cannot fall out | **3.7114** |
| **C** twisted 10° with no press | **> 0** — the detent blocks rotation on its own | **0.2735** |
| **D** pressed 0.250 mm **and** twisted 10° | 0 mm³ — the two movements together free it | **0.0000** |
| **E** rotated into the entry windows and dropped | 0 mm³ — aligned with the gaps it comes out | **0.0000** |

**B + C + D is the compliance argument.** Rotation alone is refused by the
geometry — and because the detent is a *square* step rather than a ramp, it is
refused at **any** torque, not merely resisted. Pressing alone does nothing but
compress the springs. Only both at once opens it.

### 5.3 The forces

The three fingers are the spring. From the modelled geometry
(L = 6.074 mm, w = 3.60 mm, t = 0.15 mm, C5191, E = 110 GPa):

| quantity | value | note |
|---|---|---|
| spring rate, per finger | **1.491 N/mm** | k = 3EI/L³ |
| contact force at the closed position (δ = 0.400) | **0.596 N** per finger, **1.79 N** total | inside the usual 0.5–1.5 N band for a coin cell |
| bending stress there | **268 MPa**, 45 % of C5191's yield | |
| force with the door pressed 0.250 mm | **0.969 N** per finger, **2.91 N** total | |
| bending stress there | **436 MPa**, 74 % of yield | a transient, not a resting state |
| **press force to open** | **≥ 2.91 N** (0.30 kgf) | |
| **opening torque** | **≥ 13.4 N·mm** | friction only, μ = 0.35 assumed, on three tab/foot interfaces at R 13.15 |
| ... as a finger force at the door's rim | **1.05 N** | |

**Caveats, stated.** The spring rate is **calculated, not measured**: w/L = 0.59,
so the strip behaves partly as a plate and the real rate is up to ~12 % higher
(1/(1−ν²)). μ = 0.35 for PC on dry stainless is an **assumption**. And 16 CFR
1263 also requires the product to pass **abuse tests** — drop, torque,
compression — with the cell retained; those are physical and have not been done.
**Verdict on F12: the mechanism PASSES its geometric requirement; the standard's
test regime is CANNOT DETERMINE.**

### 5.4 The door is at cell potential, and that is safe

The door's inner dome bears on the cell's positive can, so the stainless floats
at +3 V. It is **not a circuit terminal** — all three contacts are on the
carrier, exactly as Catley found on the AirTag, and no current flows through the
door. There is no second exposed conductor anywhere on the outside of the
product, so no external short is possible. A 0.10 mm PET insulating disc under
the cell would remove even the question and costs 0.10 mm of the 0.542 mm of
slack in row 2; it is offered as an option, not taken as the baseline.

---

## 6. The sprung contacts

No coin-cell retainer fits (§2.2), so the contacts are three formed C5191
fingers, insert-moulded into three carrier spokes at 90 / 210 / 330°:

- an **arc cantilever**, 30° at R 11.60 — 6.074 mm of length inside a 26 mm
  ring, which a straight cantilever could not reach;
- **0.15 mm stock, 3.60 mm wide**. Width buys force without buying stress:
  σ = 1.5·E·t·δ/L² is independent of width, so the spring was widened rather
  than thickened to reach 0.6 N;
- a **Ø0.90 embossed dimple** at the tip, 0.100 mm proud, which is the actual
  contact and the reason row 4 of the stack is 0.250 and not 0.150;
- **two positive** on the cell's can rim at R 9.50, **one negative** on the
  negative face at R 6.00 — Catley's 2 + 1, all carrier-side.

In the model the fingers are **cut out of the carrier** with 0.020 mm of
clearance, because that is what insert moulding does: the metal displaces the
plastic. That is also why the interference check reads zero.

**Open:** the R 9.50 contact circle assumes the CR2032's positive can rim is
exposed outside its gasket from about Ø18.4 to Ø20.0. That is the standard
construction, but crimp geometry is per-vendor and it is a caliper job on the
cell actually sourced.

---

## 7. Sealing

IP67, and **nobody has published how the AirTag does it** (lane G open item 5).
So this is halo's design, not a copy.

- **The door:** a **radial** seal — a moulded-in-place LSR 70 Shore A bead on
  the carrier's Ø24.15 land, free radial section 0.50 mm, compressed into the
  0.40 mm gap to the door's Ø24.95 bore: **20 % squeeze**, measured off the
  modelled gap. Radial on purpose, because the contact springs push the door
  *outward* — an axial face seal at this interface would be unloaded exactly
  when it is needed. Moulded in place rather than an O-ring in a groove because
  the seal station is only 0.39 mm tall and no standard groove fits.
- **The parting line:** the carrier's Ø27.60 wall is bonded into the shell's
  Ø27.90 bore over 2.31 mm of height with a 0.15 mm gap — **198 mm² of bond
  area**. The same bead is the structural joint and the seal, which is what
  iFixit found on the real product ("aim between the three clips so you only go
  through glue").

**Verdict on IP67: CANNOT DETERMINE.** It is an IEC 60529 test on a built puck.
iFixit's own counterexample is the reason not to claim it: Samsung's SmartTag
has "the thickest adhesive barrier" of any tag they opened and carries no IP
rating at all.

---

## 8. Tolerances and the printed variant

### 8.1 Moulded

| fit | nominal | clearance | why |
|---|---|---|---|
| carrier wall Ø27.60 in shell bore Ø27.90 | — | 0.150 mm radial | adhesive gap; a structural epoxy wants 0.10–0.20 |
| door wall Ø25.55 in the shell's Ø27.90 bore | — | 1.175 mm radial | the tabs and the seam gap live here |
| door bore Ø24.95 on the carrier's Ø24.15 land | — | 0.400 mm radial | the seal's compressed section |
| tab Ø26.60 to leg R 13.40 | — | 0.100 mm radial | the tabs must rotate inside the legs |
| tab top (pressed) 2.440 to carrier floor 2.500 | — | 0.060 mm | the clearance the press probe measures |
| PCB Ø26.00 in the carrier rim Ø26.20 | — | 0.100 mm radial | |
| bore draft | 1° | — | straight pull |
| edge break | 0.05 × 45° | — | Apple's own callout |

### 8.2 The FDM prototype variant

`part:halo-shell-top-fdm` and `part:halo-battery-door-fdm` are built from the
same parametric source with `fdm=True`:

- **wall 1.200 mm** — three perimeters at a 0.4 mm nozzle, which is the real
  floor for an FDM shell;
- **every sliding fit opened 0.200 mm**;
- **the outer envelope is byte-identical to the moulded part**, so a printed
  puck still drops into the AirTag holder ecosystem (holders are cut with
  +0.15 to +0.30 mm of margin, research/07 §5.1);
- suggested process: 0.12 mm layers, **no brim**.

**A printed shell will be markedly quieter** — 1.20 mm of PC is 3.4× the
bending stiffness of 0.80 mm and the exciter authority falls from 0.66 to 0.20
(§4.2). The printed variant exists to exercise **fit and mechanism**, never
loudness. **Nothing has been queued to any printer.**

---

## 9. What only a physical sample can settle

Lane G's six open measurement tasks (research/07 §8), plus what this lane adds.

| # | question | what a sample settles | what halo did instead |
|---|---|---|---|
| 1 | **the magnet** — Ø, thickness, grade, pull force | nothing measurable is published; iFixit only photographs it | **deleted.** D11a replaces the moving-coil motor entirely, so halo has no magnet |
| 2 | **the voice coil** — bobbin Ø, wire gauge, turns, DCR | same | **deleted**, same reason |
| 3 | **the PCB outline and its central aperture**; layer count off a cross-section | Apple's board is "≤ 26 mm" by inference only; nobody has published a caliper reading | halo chose Ø26.00 × 0.60 mm, 4 layers, **no** central aperture — the aperture existed to pass Apple's magnet |
| 4 | **the white shell's wall thickness** at apex, equator and lip | the one number that would most change §4 | halo chose 0.800 / 2.01 / 1.430 mm from the exciter-authority argument, not from a measurement |
| 5 | **the steel cover's thickness and alloy** | "polished stainless steel" is all anyone has written | halo chose 0.30 mm 301 full hard |
| 6 | **the door seal** — gasket, cross-section, groove, or only adhesive | the single public statement about it is a low-trust Taobao page | halo designed a 20 %-squeeze radial MIP bead, §7 |
| **7** | **(new) the two plan-view callouts Ø27.90 and Ø27.84** | the CC BY half-section DXF omits both circles; lane G rates the interpretation *medium*. A donor sample sectioned through a bayonet tab settles what they are | halo reads them as the shell's bore and the carrier's leg circle, §3 |

And three verdicts this lane cannot close from geometry:

| what | verdict | the test |
|---|---|---|
| **SPL, ≥60 phon at 25 cm (SPEC F3)** | **CANNOT DETERMINE** | build the shell, bond a 7BB-20-3 to the flat land, measure dB(A) at 10 cm against a reference AirTag (lane G item 6) |
| **IP67 (SPEC §4)** | **CANNOT DETERMINE** | IEC 60529, 1 m for 30 min, on an assembled puck |
| **the contacts' spring rate and the door's opening force** | **CANNOT DETERMINE** | a force gauge on three stamped fingers, and a torque gauge on the door. The numbers in §5.3 are calculated |
| **antenna performance behind this carrier** | **CANNOT DETERMINE** | ce-rf's lane (SPEC §5 E4/E5); this lane guarantees only the geometry and the metal inventory |

---

## 10. Mass

The built assembly measures **7.8 g** against the AirTag's 11 g (gen 1) and
11.8 g (gen 2). The difference is almost exactly Apple's motor: a magnet, a
copper coil and the adhesive that holds them. halo is lighter because it is
doing the same job with a 0.45 g bender.

| part | measured mass |
|---|---|
| CR2032 | 3.0 g |
| shell (PC) | 1.5 g |
| door (301 SS) | 1.4 g |
| carrier (LCP) | 0.7 g |
| PCB blank (FR4, no copper, no components) | 0.6 g |
| bender | 0.5 g |
| three contacts | 0.1 g |
| seal | < 0.05 g |
| **assembly** | **7.8 g** |

The board's components and copper are not in this figure; they are the
electronics lane's, and they are the gap between 7.8 g and 11 g.

---

## 11. Files

| what | where |
|---|---|
| the ONE parametric source | [`design.py`](../design.py) |
| the blueprint (P12) — the stack budget as ten space claims | `ce-assemblies/halo-puck/current/blueprint.json`, `out/mech/halo-puck-blueprint.svg` |
| the assembly | `ce-assemblies/halo-puck/` — `assembly.json`, `bom.json` (8 rows), `joints.json` (5 rows) |
| the parts | `ce-parts/halo-*/` — ten folders, each with `cad/part.py`, `cad/interfaces.json`, `mech/mech.py`, `evidence/ledger.jsonl` |
| renders, section, STEP, STL | `out/mech/` |
| the measured verdicts, as data | `out/mech/verdicts.json` |
