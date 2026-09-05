# JLCPCB — what is actually exposed, measured 2026-09-05

**CANNOT DETERMINE** — transport reaches JLCPCB; no approved app, so no quote. the gateway parsed our JOP Authorization header and answered 401 'application not exists' — the header shape is right and the wall is the missing approved app

| surface | url | needs |
|---|---|---|
| ordering/quoting API portal | https://api.jlcpcb.com/ | an approved app |
| ordering/quoting API gateway | https://open.jlcpcb.com | JOP signature |
| API documentation | https://api.jlcpcb.com/docs/api-list | sign-in |
| browser upload | https://cart.jlcpcb.com/quote | a person |

## Approval

> To apply for API access, please visit api.jlcpcb.com. Please be aware that not all applications will be approved; each application undergoes a review based on the partner's previous orders at JLCPCB, company and business situation.

## Credentials on this machine

**CANNOT DETERMINE** — no JLCPCB OpenAPI credentials on this machine (set `JLCPCB_APP_ID`, `JLCPCB_ACCESS_KEY`, `JLCPCB_SECRET_KEY`)

## Endpoints

Every row is CITED, not verified — see `verified_why_not`.

| id | method | uri | what |
|---|---|---|---|
| `pcb.upload_gerber` | POST | `/overseas/openapi/pcb/uploadGerber` | upload the gerber zip; returns a file handle the other calls take |
| `pcb.calculate` | POST | `/overseas/openapi/pcb/calculate` | THE QUOTE. price a board from an uploaded gerber + a craft spec |
| `pcb.audit` | POST | `/overseas/openapi/pcb/audit/get` | JLCPCB's engineering review of the files — the rejection reasons |
| `pcb.wip` | POST | `/overseas/openapi/pcb/wip/get` | production progress of a placed order |
| `pcb.order_detail` | POST | `/overseas/openapi/pcb/order/detail` | an order by batch number |
| `pcb.impedance_templates` | POST | `/overseas/openapi/pcb/getImpedanceTemplateSettingList` | the controlled-impedance stackup templates JLCPCB will quote |
| `pcb.stencil_price_config` | GET | `/overseas/openapi/pcb/getSteelPriceConfig` | stencil price config |
| `pcb.create_order` ⛔ | POST | `/overseas/openapi/pcb/create` | PLACES AN ORDER AND SPENDS MONEY — forbidden in this package |
| `component.library_list` | POST | `/overseas/openapi/component/getComponentLibraryList` | the parts library, paged |
| `component.by_code` | POST | `/overseas/openapi/component/getComponentDetailByCode` | parts by LCSC code |
| `component.info` | POST | `/overseas/openapi/component/getComponentInfos` | part detail |
| `component.private_stock` | POST | `/overseas/openapi/component/getPrivateComponentLibrary` | your own consigned stock held at JLCPCB |

⛔ = in `openapi.FORBIDDEN`; ce-fab raises before it is called.

## Gateway probe

`POST https://open.jlcpcb.com/overseas/openapi/pcb/calculate` with synthetic (deliberately invalid) → HTTP 401 `code=401` `application not exists`

Transport: **PASS** — the gateway parsed our JOP Authorization header and answered 401 'application not exists' — the header shape is right and the wall is the missing approved app

## Sources

- **portal** https://api.jlcpcb.com/ — read 2026-09-05. plain curl; <title> is 'JLCPCB API Platform - Automate and Streamline PCB, SMT Stencil, and 3D Printing Orders'. Nuxt SPA. Its config blob names client_id 'OVERSEAS_OPEN_PLATFORM' and CAS_BASE_URL passport.jlcpcb.com. The /docs/* pages render their bodies client-side behind a sign-in, so the endpoint table is not readable by curl.
- **gateway** https://open.jlcpcb.com — read 2026-09-05. POST with and without an Authorization header. Live. 400 'The request authorization cannot be empty.' with no header; 401 'application not exists' with a well-formed JOP header carrying an unknown appid. Authenticates before routing, so path existence is not probeable from outside.
- **apply** https://jlcpcb.com/help/article/jlcpcb-online-api-available-now — read 2026-09-05. plain curl; the article body was read out of the articleDetail record inside the page's __NUXT__ payload. First-party statement of the approval criteria. See APPROVAL.
- **sdk-shape** https://github.com/i2cjak/jlcpcb_api — read 2026-09-05. raw.githubusercontent.com, src/jlcpcb_api/{auth,client,models}.py. THIRD PARTY, not JLCPCB. Self-described as 'reverse-engineered from the Java SDK JARs'. Source of the URI strings and of the signing recipe. Everything taken from here is marked unverified until a credentialed call proves it.