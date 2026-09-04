# C5 — Energy beyond a year

*Researched 2026-09-05 from vendor datasheets, not from marketing pages.
Three branches were costed: indoor solar, supercapacitor hybrids, and simply a
bigger cell. One wins outright and the other two fail for reasons worth keeping.*

## The anchor

halo's "about a year on a CR2032" implies **≈26 µA average at 3.0 V**
(225 mAh ÷ 26 µA = 8,654 h). Worth noting on its own: our component model
predicts 6.0 µA at a 5-second advertising interval and 9.9 µA at 2 seconds, so
**about 16 µA of the budget is overhead nobody has named yet.** That is a
measurement debt, not an energy problem.

## Branch C — a bigger cell. VERDICT: PROVEN, and it wins by a wide margin

| swap | height cost | energy | life at 26 µA | pulse capability |
|---|---|---|---|---|
| CR2032 (today) | — | 225 mAh | **0.99 yr** | 400 Ω, ~6.8 mA |
| **→ CR2450** | **+1.8 mm** | 620 mAh | **2.72 yr** | **300 Ω, 9.0 mA** |
| → CR2477 | +4.5 mm | 1000 mAh | **4.39 yr** | — |

Both fit the Ø31.87 mm face easily at 24.5 mm diameter, so this is purely a
thickness trade. No power-management chip, no photovoltaic cell, no antenna
re-solve, no acoustic compromise, no charge-voltage clamp, no cycle-life
question — about **$0.50 of parts** instead of about $6, and the **pulse
capability improves** rather than staying flat, which matters because pulse
droop at end of life is what the coin-cell model already tracks.

## Branch A — indoor solar. VERDICT: FAILS on this enclosure

Not on physics. **On our own keep-outs.** The face is 7.98 cm², but the inner
Ø25.75 mm is Apple's "do not obstruct" acoustic path, leaving an annulus of
**2.77 cm² — and that annulus lies entirely inside the Ø37.31 mm no-metal
antenna keep-out**, where the Bluetooth antenna and the NFC coil are already
fighting for room. A photovoltaic cell is metal in that zone.

Measured yields, triangulated across three vendors at 200 lux: bare cells reach
7.3–9.0 µW/cm², **packaged modules deliver 3.0–5.4**, and the round parts that
actually fit a disc manage **1.3–2.6**. On the real 2.77 cm² at 200 lux for
12 hours a day, net of the harvester chip's own 488 nA quiescent draw, the
result is **0.7 to 2.7 µA equivalent against a 26 µA draw — 3 to 14 percent**.

Break-even at even 10 µA needs **about 700 lux for 12 hours every day**. Office
task lighting is 500 lux; a living room is 50–150; a bag, a pocket or a car
footwell is **zero**. A tracker lives in the dark.

**The comparison that settles it:** every self-powered Bluetooth device that
actually works ships **6 to 11 times more collector area** than halo's entire
usable annulus — EnOcean's sensor needs 200 lux for 6 hours a day across about
16 cm², Minew's tag wants 400–1000 lux across 31 cm². The only solar Find My tag
on the market, UGREEN's, has a panel that **cannot recharge its battery** — a
reviewer who opened it found the panel genuinely connected, which he noted is
not always true, but it only extends life rather than sustaining it.

## Branch B — supercapacitors. VERDICT: REFUSED, with one narrow exception

**A thin supercapacitor leaks 1 to 2 µA — which is 50 to 150 percent of the
entire harvest.** One holds 0.36 J and **self-empties in 43 hours with no load
at all**. A rechargeable manganese-lithium coin of the same footprint holds
59 J, 165 times more, and loses about 2 percent per year, or 13 nanoamps.

So if a harvester is ever built here it stores into a rechargeable coin, never a
supercapacitor. The one defensible supercapacitor role is a **sub-second
transmit-pulse buffer** — 11 millifarads in a 3.2 × 2.5 × 0.9 mm chip holds
about 2,100 transmit bursts but only **8 minutes** of system draw. That is a
decoupling part, not a storage part.

**And a hard rule for any future harvester:** you cannot push harvested current
into a primary lithium cell. Energizer caps reverse charge at **1 µA** on both
the CR2032 and CR2450. A harvester needs its own rechargeable element and diode
isolation — which is exactly what one power-management chip's primary-cell
path-management block exists to do, and the only topology where a harvester and
a CR cell coexist legally.

## What this forces

The energy question is a **thickness decision**, not a technology decision. It
belongs to Leif: today's 8 mm puck and one year, or a 9.8 mm puck and nearly
three years for fifty cents. Everything else on this page is the evidence that
the clever options are worse than the obvious one.

## Also found

**There is no open-source solar Bluetooth tracker.** Eleven repository searches
returned nothing — "solar airtag" returns zero results. halo would be first, if
it were worth being first at, and this research says it is not.

**A widely repeated firmware claim is wrong.** The "almost 3 years on a CR2032"
figure carried by two popular Find My firmware repositories rests on a handheld
multimeter measurement whose burden voltage made it the wrong instrument. The
corrected figure, taken with a proper power analyser, is **2× higher current**:
7.60 µA with an external crystal, 9.21 µA on the internal oscillator — so the
crystal is worth 17 percent of the budget. One real elapsed-time datapoint
exists: a user replaced a cell after **four years** of actual service.
