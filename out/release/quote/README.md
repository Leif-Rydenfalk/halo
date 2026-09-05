# Getting halo quoted by JLCPCB

*Lane F1, 2026-09-05. Everything on this page was measured from this machine
on that date, with `curl` and with `ce-fab/bin/fab submit`. The commands are
here so a reader can disagree with me by running them.*

**A quotation is not an order.** Nothing in this directory, and no code path
in `ce-fab`, places an order or spends money. The two URIs that would are
listed in `cefab/openapi.FORBIDDEN` and raise before a socket is opened. If
halo is ever actually bought, that is a decision with Leif's name on it and a
different lane's job.

---

## The short version

| question | answer |
|---|---|
| Is there a machine interface? | **Yes.** JLCPCB runs a real ordering-and-quoting API. |
| Can we use it today? | **No.** It needs an app JLCPCB approves per-customer, and approval is reviewed on *"the partner's previous orders at JLCPCB"* — which for this account is none. |
| Is there an unauthenticated preflight? | **No.** The parts catalogue answers without auth; nothing that touches a board file does. |
| So how does halo get quoted? | **A person uploads a zip at <https://cart.jlcpcb.com/quote>.** `fab submit` builds and gates that exact zip. |
| Was halo submitted? | **No, and it should not be.** It fails three gates today. See below. |
| What does the quote cost? | Nothing. Quoting is free and non-binding on both the API and the website. |

---

## 1 · What the interface actually is

Three surfaces, and they are not the same thing.

| surface | URL | auth | what it gives you |
|---|---|---|---|
| **Ordering / quoting API** | gateway `https://open.jlcpcb.com`, portal `https://api.jlcpcb.com/` | `JOP` HMAC signature from an **approved app** | board price, gerber upload, engineering-review verdicts, order tracking |
| **Parts catalogue** | `https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList` | **none** | live stock and both price ladders — already used by `fab parts --live` |
| **Browser upload** | `https://cart.jlcpcb.com/quote` | a JLCPCB login, in a browser | the price a human sees, and JLCPCB's own DFM/gerber viewer |

### The API, precisely

The portal at `api.jlcpcb.com` is titled *"JLCPCB API Platform – Automate and
Streamline PCB, SMT Stencil, and 3D Printing Orders"* and offers four products:
PCB, SMT Stencil, 3D Printing and Parts. Its `/docs/*` pages render their
bodies client-side behind a sign-in, so the endpoint table is not readable
without an account.

The gateway is `open.jlcpcb.com`. It authenticates with a scheme of JLCPCB's
own:

```
Authorization: JOP appid="…",accesskey="…",timestamp="…",nonce="…",signature="…"
signature = base64( HMAC-SHA256( secret_key,
              "METHOD\n" + path?query + "\n" + timestamp + "\n" + nonce + "\n" + body + "\n" ))
```

**Measured 2026-09-05**, three requests to
`POST https://open.jlcpcb.com/overseas/openapi/pcb/calculate`:

| what was sent | what came back |
|---|---|
| no `Authorization` header | `400 {"code":400,"message":"The request authorization cannot be empty."}` |
| a well-formed `JOP` header with an unknown appid | `401 {"code":401,"message":"application not exists"}` |
| `Authorization: Bearer nope` | `500 {"code":500,"message":"An unknown error has occurred in the service"}` |

The 401 is the useful one. The gateway **parsed our header and got as far as
looking the app id up**, which means the signature this workshop builds is in
the shape JLCPCB expects. The wall is not the protocol. It is the account.

Reproduce it, no credentials needed:

```bash
ce-fab/bin/fab submit --interface        # exit 2 — transport PASS, no app
```
→ `jlcpcb-interface.json` / `.md` in this directory.

### What I could NOT establish, and why

**The endpoint paths are cited, not verified.** The gateway authenticates
*before* it routes:

```
/overseas/openapi/pcb/calculate              -> 400 "authorization cannot be empty"
/overseas/openapi/pcb/no-such-endpoint-xyzzy -> 400 "authorization cannot be empty"
```

A real path and a nonsense path are indistinguishable from outside. So the URI
list below cannot be confirmed by anyone without an approved app. It comes
from a third party's reverse-engineering of JLCPCB's own Java SDK JARs
([`i2cjak/jlcpcb_api`](https://github.com/i2cjak/jlcpcb_api),
`src/jlcpcb_api/models.py`, read 2026-09-05) and **every row in
`openapi.endpoints()` carries `verified: false`.** It stays false until a
credentialed call returns something other than 401.

| what it does | URI |
|---|---|
| upload the gerber zip | `POST /overseas/openapi/pcb/uploadGerber` |
| **the quote** | `POST /overseas/openapi/pcb/calculate` |
| JLCPCB's engineering review — the rejection reasons | `POST /overseas/openapi/pcb/audit/get` |
| production progress | `POST /overseas/openapi/pcb/wip/get` |
| ⛔ **place an order and charge the account** | `POST /overseas/openapi/pcb/create` |

⛔ is in `openapi.FORBIDDEN`. `JOPClient.call()` raises `OrderRefused` on it
before opening a socket, and `tests/prove_submit_gates.py` proves that by
replacing `urllib.request.urlopen` with a function that raises if it is ever
reached on those URIs.

### A correction to `ce-fab/README.md`

That page says, from a 2026-09-03 probe, that JLCPCB publishes *"no board-price
API that answers without a session"* and that *"the board calculator is not on
this API surface"*. The first half is right. The second half was reached by
guessing five path names on `jlcpcb.com` and getting 404 from all of them.

**The board calculator exists.** It is `/overseas/openapi/pcb/calculate` on a
different host behind a different auth scheme — which no amount of guessing on
the parts-endpoint prefix would ever have found. The conclusion "not on this
API surface" was true and the inference "therefore nowhere" was not.

---

## 2 · What it would take to use the API

**Do not ask Leif for credentials. There are none to ask for.** They do not
exist yet and cannot be bought; they are granted.

JLCPCB's own words, from
<https://jlcpcb.com/help/article/jlcpcb-online-api-available-now> (read
2026-09-05; the body is client-rendered, and this text was read out of the
`articleDetail` record inside the page's `__NUXT__` payload):

> To apply for API access, please visit api.jlcpcb.com. Please be aware that
> **not all applications will be approved; each application undergoes a review
> based on the partner's previous orders at JLCPCB, company and business
> situation.** If you're still interested in building a stronger business
> relationship with JLCPCB, feel free to submit your application.

and:

> All applicants should have an account at JLCPCB to access API… The JLCPCB API
> support team does not provide code reviews or coding solutions.

There are also brand restrictions on partners: no JLC trademark or logo on
your site or in ads, and no `JLC` in your URLs. Violation suspends API access
**and all associated accounts**.

**So the decision Leif has, in one reading:**

| | |
|---|---|
| **Cost of the API** | $0. There is no fee named anywhere for API access. |
| **What it needs** | A JLCPCB account with an **order history**, plus a company/business case, plus an approved application. |
| **Where we stand** | halo has never been ordered. On the published criterion, an application now is likely to be declined for lack of order history. |
| **The obvious sequence** | Order halo rev A through the website like anyone else. That creates the order history that makes an API application credible. The API is the reward for being a customer, not the way to become one. |
| **What to do if he wants it now** | Apply at <https://api.jlcpcb.com/> with a real company description. Costs nothing but the application. If approved, set `JLCPCB_APP_ID`, `JLCPCB_ACCESS_KEY`, `JLCPCB_SECRET_KEY` and `fab submit --transport api` works with no code change — that path is already written and already reaches the gateway. |

---

## 3 · What a submission contains

`fab submit` produces the bundle and refuses to produce a bad one.

```bash
ce-fab/bin/fab submit <board.kicad_pcb> --package <dir> [--assembly] [--qty N]
ce-fab/bin/fab submit <board.kicad_pcb> --rebuild        # regenerate, then gate
ce-fab/bin/fab submit <board.kicad_pcb> --transport api   # needs an approved app
ce-fab/bin/fab submit --interface                         # no board needed
```

| gate | refuses when |
|---|---|
| `G1-board` | the `.kicad_pcb` is not there |
| `G2-present` | the package has no gerber zip (or, with `--assembly`, no BOM/CPL) |
| **`G3-fresh`** | **any artifact is older than the board it claims to describe** |
| `G4-identity` | the zip's copper-layer count ≠ the board's copper layers |
| **`G5-routed`** | there are unconnected items, or no DRC ran to count them |
| `G6-dfm` | `fab dfm` is not PASS against JLCPCB's transcribed capability rules |
| `G7-sourced` | a placed part carries no LCSC number (`--assembly` only) |
| `G8-transport` | `--transport api` and there are no credentials |

A bare-board submission is **one file**: the gerber zip. A PCBA submission is
three: the zip, `-BOM.csv` and `-CPL.csv`. The bundle directory holds exactly
those, each with a sha256 in `submission.json`.

`--force` sends over a CANNOT DETERMINE and **never** over a FAIL. That is
tested.

### Exit codes

`0 PASS · 1 FAIL · 2 CANNOT DETERMINE · 3 REFUSED (malformed ask)`.

---

## 4 · Where halo stands today

Run in this directory, 2026-09-05, with KiCad's DRC actually running
(`submit.json` / `submit.md` here are its output):

```bash
ce-fab/bin/fab submit ce-designs/halo/electronics/halo_rev_a/out/halo_rev_a.kicad_pcb \
  --package ce-designs/halo/out/release/board --assembly --qty 5,30
```
**exit 1 — FAIL. Nothing was sent, and nothing should be.**

| gate | verdict | measured |
|---|---|---|
| `G1-board` | PASS | sha256 `8b512ff678f80532…` |
| `G2-present` | PASS | zip + BOM.csv + CPL.csv all present |
| **`G3-fresh`** | **FAIL** | **all 3 artifacts are older than the board, the worst by 6,461 s (1.8 h)** |
| `G4-identity` | PASS | 4 copper gerbers in the zip, 4 copper layers in the board |
| **`G5-routed`** | **FAIL** | **83 unconnected items** |
| **`G6-dfm`** | **FAIL** | `smd_pad_min`, `smt_min_package` |
| `G7-sourced` | PASS | 23 BOM lines, all with an LCSC number |

Three independent things say the same sentence: **the release package
describes a board that is not on disk any more.** The gerbers were exported
1.8 hours before the board file was last written, and the board they *were*
exported from is gone. A fab builds what you send. Sending this would produce
a real object that matches no design we have.

Note that `G4-identity` **passes** — the zip is a genuine 4-layer export. It
is a genuine 4-layer export *of the wrong revision*, which is why freshness is
a separate gate from identity.

Not measured here, and still open: the antenna is 16 % below band (lane T3),
which is not a manufacturability question and no gate here will catch it.

---

## 5 · The path is proved, on a board that is ready

Waiting for halo would have meant asserting the tool works. Instead it was run
end to end on `ce-pcb/examples/round32_4layer`, built and routed, which is
clean: **0 unconnected, 0 DRC violations.**

```
$ fab submit ce-pcb/out/round32_4layer/round32_4layer-routed.kicad_pcb --rebuild --qty 5,30
G1..G6 all PASS — 28 dfm rules PASS, 0 FAIL, 0 CANNOT DETERMINE
1 file staged in .../bundle                                              -> 0
```

and the API transport, with **deliberately invalid** credentials, to prove the
code path reaches JLCPCB rather than merely compiling:

```
POST https://open.jlcpcb.com/overseas/openapi/pcb/uploadGerber
  string_to_sign: 'POST\n/overseas/openapi/pcb/uploadGerber\n1788601984\n
                   P2NsDvzDpbp7FLGVItbHIbxffE64dpuq\n
                   {"fileName":"round32_4layer-routed-gerber-jlc.zip"}\n'
  -> HTTP 401  {"code":401,"message":"application not exists"}            -> 2
```

Both reports are committed under
`ce-fab/out/round32_4layer-routed/submit/` and `…/submit-api/`.

The gates themselves are broken on purpose and watched:

```
$ python3 ce-fab/tests/prove_submit_gates.py
36/36 deliberate breaks were caught.                                      -> 0
```

Two of those tests exist because the gates were **wrong when first written**,
and both were wrong in the direction that lets a bad package through:

- `G5-routed` read `unconnected_items: 0` out of a DRC that had never run and
  reported *"0 unconnected items in KiCad's own DRC"*. Measured on halo with
  `--no-drc`. A check that can agree with itself is not a check.
- `G4-identity` listed `.gl2`/`.gl3` as inner-copper extensions, counted 2
  copper layers in a 4-layer zip whose layers are named JLCPCB's own way
  (`GTL`/`G2L`/`G3L`/`GBL`), and failed a **good** package. A gate that goes
  red on a good package is as broken as one that goes green on a bad one.

---

## 6 · What a human must do that a machine cannot

Everything up to the upload is automated. These are not:

1. **Have a JLCPCB account.** ce-fab will not create one, will not store a
   password, and does not prompt for credentials. Register at
   <https://jlcpcb.com/> in a browser.
2. **Upload the bundle and read the price.** Go to
   <https://cart.jlcpcb.com/quote>, sign in, upload the zip from the bundle
   directory, and choose the options `fab dfm` already validated: **4 layers,
   1.6 mm, 1 oz outer / 0.5 oz inner.** The price appears on the page. It is
   free and commits to nothing.
3. **Read JLCPCB's own DFM verdict.** Their gerber viewer and DFM tool
   (<https://jlcdfm.com>) are the one opinion in this project with no
   incentive to agree with us. Whatever it says outranks `fab dfm`, which is a
   transcription of published limits, not their production rules.
4. **Decide whether to buy.** Not a machine's call, in this workshop or any
   other.
5. **Apply for API access** — see §2 — if the manual loop is worth removing.
6. **For PCBA specifically:** confirm the part substitutions JLCPCB proposes
   when something is out of stock. They ask; that is a human answer.

**And one thing nobody should do yet:** submit halo. Fix G3, G5 and G6 first.
The gate output above is the to-do list, and re-running the same command is
how you know it is done.

---

## Files here

| file | what |
|---|---|
| `jlcpcb-interface.json` / `.md` | the interface, the endpoint table, the live gateway probe, every source with its date |
| `submit.json` / `.md` | halo's current gate report — the refusal, with numbers |
| `dfm/` | the DRC and rule evaluation those gates read |

Regenerate all of it with the two commands in §1 and §4.
