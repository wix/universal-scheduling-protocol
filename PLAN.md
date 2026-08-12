# Feature: keys-publisher-alignment

## Goal

Align USP publisher rules with UCP main/draft verifiers that require signing
material in top-level `keys[]`. Publishers **MUST** publish signing material in
`keys` (UCP-canonical), **MAY** also publish identical `signing_keys` during
transition (dual-publish preferred), and verifiers **MUST** resolve `keys`
first then fall back to `signing_keys`. Soften §10.1.1 / §8.2.1 /
§9.1.4 prose and related schemas/site-docs so `signing_keys` is no longer the
primary publisher MUST.

## Non-goals

- Do not change AuthorizationPolicy, covered components, replay rules,
  privileged MUST, or `booking_scoped_credential`.
- Do not invent Ed25519 / Web Bot Auth requirements.
- Do not change `config.authorization` placement or privileged-auth MUST.
- Do not create a PR or push; do not merge to integration.
- Do not edit the main checkout or sibling worktrees.

## Must-preserve constraints

- Webhook signing still required when businesses send signed webhooks;
  Standalone remains coherent (keys preferred; signing_keys allowed during
  transition; verifiers keys-first with signing_keys fallback).
- Privileged-operation authentication floor (§10.1.6) unchanged.
- Request `created` OPTIONAL and covered-component rules unchanged.
- Schema domain shapes stay in `schemas/`; bindings remain thin `$ref` overlays.
- Dual-publish: when both `keys` and `signing_keys` are present they MUST list
  the same keys.

## File actions

| Path | Action | Reason |
|------|--------|--------|
| PLAN.md | modify | Complete goal, non-goals, units before implementation |
| specification.md | modify | Flip publisher MUST to `keys`; soften `signing_keys`; align §8.2.1, §9.1.4, §10.1.1 and related prose/examples |
| schemas/profile.json | modify | Add/describe `keys` as canonical; `signing_keys` as transition alias; keys-first verifier note |
| site-docs/security.md | modify | Restate publisher/verifier rules to match spec |
| site-docs/transport/rest.md | modify | Platform signing keys: prefer `keys`, keys-first resolve |
| site-docs/deployment-modes/standalone.md | modify | Example/prose: prefer `keys`, allow `signing_keys` during transition |
| openapi/usp-rest.json | modify | Only if security scheme / example text still mandates `signing_keys` as primary |
| CHANGE_LOG.md | modify | Append newest-first entry per AGENTS.md |

## Work units

| ID | Description | Files | Verification | Status |
|----|-------------|-------|--------------|--------|
| U1 | Complete and commit PLAN.md | PLAN.md | test -f PLAN.md && grep -q 'Work units' PLAN.md | done |
| U2 | Spec publisher/verifier alignment (§8.2.1, §9.1.4, §10.1.1 + related prose/examples) | specification.md | rg -n 'MUST publish signing material in .keys' specification.md && rg -n 'signing_keys' specification.md \| head -40 | pending |
| U3 | Schema: keys canonical, signing_keys transition | schemas/profile.json | python3 -c 'import json; json.load(open("schemas/profile.json"))' && rg -n '"keys"|signing_keys' schemas/profile.json | pending |
| U4 | Site-docs (and openapi text if needed) publisher wording | site-docs/security.md, site-docs/transport/rest.md, site-docs/deployment-modes/standalone.md | rg -n 'signing_keys|`keys`' site-docs/security.md site-docs/transport/rest.md site-docs/deployment-modes/standalone.md | pending |
| U5 | Grep consistency check, CHANGE_LOG, final commit | CHANGE_LOG.md | rg -n 'MUST include a top-level .signing_keys' specification.md schemas/ site-docs/ \|\| true; test -z "$(rg -n 'MUST include a top-level .signing_keys' specification.md schemas/ site-docs/ \|\| true)" | pending |

## Revisions

### 2026-08-12 - initial plan
- Filled Goal, Non-goals, Must-preserve, File actions, and Work units from
  conformance recommendation (keys canonical publish; signing_keys transition;
  verifiers keys-first).
