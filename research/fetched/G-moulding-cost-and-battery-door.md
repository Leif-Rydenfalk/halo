# Injection moulding cost references and the button-cell battery door

All fetched 2026-09-03.

## Tooling and piece-part cost — Jaycon, "2026 Injection Molding Pricing Report"
https://www.jaycon.com/2026-injection-molding-pricing-report-us-costs-reshoring-tooling-data/

| SPI class | Tool material | Cavities | Tooling cost | Lead time |
|---|---|---|---|---|
| 105 | Aluminium (7075) | 1 | "$1,500 to $8,000" | 2-3 weeks |
| 104 | Pre-hardened steel (P20) | 1-2 | "$8,000 to $25,000" | 4-6 weeks |
| 103 | Pre-hardened steel (P20/H13) | 2-8 | "$25,000 to $60,000" | 6-8 weeks |
| 101 | Hardened steel (H13/S136) | 4-32+ | "$60,000 to $150,000+" | 10-14 weeks |

Piece price: at 1 000 units, "$2.50 to $6.00 for many commodity resin parts"; at 100 000+,
"$0.35 to $1.20, depending on material, cavitation and cycle time". On a 4-cavity hardened tool at
100 k units: PP/HDPE $0.42, ABS $0.50, **PC / PC-ABS $0.65**.

## Two-shot vs overmoulding — MoldMinds
https://moldminds.com/blog/overmolding-vs-insert-molding-vs-two-shot/

| Process | Tooling (offshore) | Lead time |
|---|---|---|
| Overmoulding (two tools) | "$18,000 to $38,000" | 10-14 weeks |
| Insert moulding (single tool) | "$14,000 to $28,000" | 8-12 weeks |
| **Two-shot (2K), single tool** | **"$45,000 to $95,000"** | 14-20 weeks |

Modelled 50 x 80 mm consumer-electronics part at 500 k/yr: overmould $0.74, insert $0.81,
**two-shot $0.43**. Cycle: overmould 22 s + 24 s; insert 35 s; two-shot 28 s combined.
> "At 500,000 parts per year with a $0.38 per-part advantage, the two-shot premium pays back in
>  12 to 18 months." Below ~100 000 units/yr overmoulding wins on total cost.

**Read-across for halo**: a 2K tool for a 32 mm puck is a $45-95 k commitment that only repays
above roughly 100-500 k units/year. A cheaper-to-manufacture clone should be a **single-material
moulding** wherever it can be, with colour/texture done in one shot.

## China tooling
https://www.haizol.com/news/china-injection-molding-industry-report-2026
> "single-cavity prototype molds at verified Chinese factories cost $1,000-3,000, compared to
>  $8,000-15,000+ at European toolmakers"
https://www.haizol.com/blog/injection-molding-tooling-cost-china
> "Injection molding tooling cost from China: $1,000 to $15,000+ by steel grade and cavity count."

## Protolabs
https://www.protolabs.com/help-center/pricing-and-payment-options/
> "Injection Molding Prices start around $1,495, depending on part geometry and complexity."

## The child-safety battery door — the mechanical constraint

US CPSC business guidance, Reese's Law / 16 CFR part 1263 / ANSI-UL 4200A-2023:
https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Button-Cell-and-Coin-Battery

> "Battery compartments containing replaceable button cell or coin batteries must be secured such
>  that they require the use of a tool or at least two independent and simultaneous hand movements
>  to open."

> "Button cell or coin battery compartments must not allow such batteries to be accessed or
>  liberated as a result of use and abuse testing."

Scope: "a single cell battery with a diameter greater than the height of the battery" (zinc-air
excluded). Compliance date 2023-10-23, extended by enforcement discretion to **2024-03-19**;
third-party testing for children's products 2023-12-20. Toys under 16 CFR 1250 are exempt.

UL's own FAQ page (https://www.ul.com/resources/reeses-lawul-4200a-standard-safety-products-incorporating-button-batteries-or-coin-cell)
confirms the abuse suite is a *sequence* on one sample:
> "All tests should be conducted on one sample in sequence as specified in sub-cl. 6.2.1 and
>  sub-cl. 6.3.1.1"
> "The drop test, like other abuse tests in UL 4200A, aims at testing the battery compartment to
>  see if the button cells become accessible or liberated after being dropped."
The numeric test parameters live in the paid ANSI/UL 4200A-2023 standard and were not obtained.
Lane F owns the legal analysis; this file records only the mechanical consequence.

### Mechanical options that satisfy "tool, or two independent and simultaneous motions"

| Option | How it satisfies the rule | Height cost | Tooling cost | Notes |
|---|---|---|---|---|
| **Press-and-twist bayonet** (the AirTag's) | Press down against a spring **and** rotate: two independent, simultaneous motions | ~0 mm — the door *is* the structure; the spring travel is absorbed by the cell's own compression against the contacts | Needs undercuts/tabs; a stamped metal cover plus three moulded lugs in the shell | Tool-free for the user, which is why Apple could keep it. Three tabs at 2/6/10 o'clock (Catley); iFixit notes three matching notches in the board/antenna shield |
| **Captive screw** (typ. M1.6-M2, Torx or Phillips) | "Use of a tool" | 1.5-2.5 mm of boss depth somewhere in the stack, plus screw head | Cheap — a moulded boss and a self-tapping screw | The default for open-hardware pucks. Costs the most height of any option and puts a metal fastener inside the antenna keep-out |
| **Two-motion latch** (squeeze two opposed tabs *and* lift) | Two independent simultaneous motions | ~0.5 mm for the latch shelf | Needs side-action or a moulded living hinge | Harder to seal to IP67 than a bayonet |
| **Plain snap-fit lid** | **Does not comply** | — | cheapest | Ruled out; lane F's conclusion is the same |
| **Sealed, non-replaceable cell** | Compartment is not "replaceable", so the rule does not bite the same way | saves the whole door | ultrasonic weld or adhesive | Kills the product's main selling point (a user-replaceable CR2032) and the 1-year+ battery story |

The press-and-twist bayonet is the only one of these that costs no vertical height, which is why
it is the right answer for an 8 mm puck even though it is the hardest to tool.

## IP67 sealing — what is actually known

Apple rates both generations IP67 per IEC 60529. No teardown found states the sealing method.
Observations that bear on it:
* iFixit: the assembly is "stubbornly glued in place"; drilling advice is to "only go through glue"
  between the three clips, i.e. there is a continuous bead of adhesive on the shell parting line.
* IT Home / Joseph Taylor on AirTag 2: "a large amount of glue is used to fix the components",
  markedly more than gen 1.
* A Taobao shopping-guide article claims "The original IP67 rating ... relies on a specific,
  factory-applied adhesive gasket" and that prying the cover deforms it
  (https://world.taobao.com/lang/en-us/shopping-guide/2012472018145902592.htm).
  **Low-trust source, unverified** — but it is the only public statement on the battery-door seal,
  and it is consistent with the door being a bayonet with a compressed elastomer or foam ring.
* Samsung's SmartTag, by contrast, "has the thickest adhesive barrier protecting its circuit board"
  yet carries "no official ingress protection rating" (iFixit).

**Nobody has published the AirTag's gasket material, cross-section or groove geometry.** For halo
this is a design decision, not a thing to copy: a moulded-in-place or O-ring seal in the bayonet
plus a bonded shell parting line is the conventional route to IP67 on a puck this size.
