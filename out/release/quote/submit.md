# Submission — halo_rev_a.kicad_pcb

**FAIL** — refused at G3-fresh, G5-routed, G6-dfm — 3 of 3 artifact(s) are older than halo_rev_a.kicad_pcb, the worst by 6,461 s (1.8 h). They were exported from a board that is no longer on disk. Re-export (`fab jlc`) or pass --rebuild.; 83 unconnected item(s). `fab dfm` is right not to FAIL on this — there is no copper to measure against a capability — but a fab builds what you send, and this is not a finished board.; 2 rule(s) FAIL: smd_pad_min,

Generated 2026-09-05T09:55:08Z. Transport: `manual`.

## Gates

| gate | verdict | what it checks | measured |
|---|---|---|---|
| `G1-board` | **PASS** | the board file exists | halo_rev_a.kicad_pcb, sha256 8b512ff678f80532…, modified 2026-09-04T23:54:19Z |
| `G2-present` | **PASS** | the package holds the files the fab needs | gerber zip = halo_rev_a-gerber-jlc.zip, BOM.csv = halo_rev_a-BOM.csv, CPL.csv = halo_rev_a-CPL.csv |
| `G3-fresh` | **FAIL** | no artifact predates the board | 3 of 3 artifact(s) are older than halo_rev_a.kicad_pcb, the worst by 6,461 s (1.8 h). They were exported from a board that is no longer on disk. Re-export (`fab jlc`) or pass --rebuild. |
| `G4-identity` | **PASS** | the zip describes the same stackup as the board | 4 copper gerbers in the zip, 4 copper layers in the board |
| `G5-routed` | **FAIL** | the board is fully routed | 83 unconnected item(s). `fab dfm` is right not to FAIL on this — there is no copper to measure against a capability — but a fab builds what you send, and this is not a finished board. |
| `G6-dfm` | **FAIL** | inside the fab's published capabilities | 2 rule(s) FAIL: smd_pad_min, smt_min_package |
| `G7-sourced` | **PASS** | every placed part has an LCSC number | 23 BOM lines, all sourceable |

> **REFUSED at G3-fresh, G5-routed, G6-dfm.** Nothing was submitted. Nothing was sent and no bundle was written. Fix the gate, do not loosen it.

## What this tool will not do

It will not call `/overseas/openapi/pcb/create`. That URI is in `openapi.FORBIDDEN` and `JOPClient.call()` raises `OrderRefused` on it before opening a socket. A quotation is not an order.
