# Feature: webhook-signing-conformance

## Goal

Make REST §9.1.5 item 7 and MCP §9.2.4 item 7 conditional MUSTs so a binding that neither emits webhooks nor advertises outbound webhook delivery can satisfy the checklist without a recorded deviation. Signing and MCP notification shape remain mandatory when payloads are emitted. Matching `site-docs/transport/` conformance lists stay in sync with `specification.md`.

## Non-goals

- Implementing webhooks in any product repository
- Weakening §10.1.1 (or §9.2.3 signature-verification sentences) for implementations that do emit webhooks
- Rewriting §5.4 (already SHOULD notify, MUST sign payloads) or §9.2.3 delivery semantics
- Moving the checklist items to a permanent SHOULD
- Changing A2A or ESP conformance lists (they have no equivalent unconditional item)
- Changing schemas, OpenAPI, or OpenRPC except if a later unit finds a conformance checklist there (none expected)
- Citing GitHub issues, PRs, or issue numbers in spec, site-docs, schemas, bindings, README, or CHANGE_LOG

## Must-preserve constraints

- Every emitted webhook payload remains subject to §10.1.1 signing rules unchanged in substance
- MCP emitters still MUST use JSON-RPC notifications (no `id`) when they emit
- Trigger is outbound only: emitting payloads or advertising that this implementation will send webhooks. Publishing a platform-profile inbound `webhook_url` to receive events does not by itself impose item 7
- Site-docs REST/MCP conformance pages match the normative checklists after the edit
- CHANGE_LOG prepends a dated entry with git user identity and no GitHub tracker citations
- Domain shapes stay in `schemas/` (this feature does not add domain types)

## File actions

| Path | Action | Reason |
|------|--------|--------|
| PLAN.md | modify | Feature plan (U1) |
| specification.md | modify | Condition §9.1.5 item 7 and §9.2.4 item 7 |
| site-docs/transport/rest.md | modify | Mirror REST checklist item 7 |
| site-docs/transport/mcp.md | modify | Mirror MCP checklist webhook item; bring the rest of that page's MUST/SHOULD lists in line with current §9.2.4 so a touched conformance section does not keep a stale shorter list |
| CHANGE_LOG.md | modify | Record the spec/docs change |

## Work units

| ID | Description | Files | Verification | Status |
|----|-------------|-------|--------------|--------|
| U1 | Plan and commit PLAN.md | PLAN.md | test -f PLAN.md | in-progress |
| U2 | Condition REST §9.1.5 item 7 and MCP §9.2.4 item 7 in specification.md | specification.md | grep both items for outbound/emit condition; confirm §10.1.1 opening signing sentence unchanged | pending |
| U3 | Sync site-docs REST and MCP conformance lists | site-docs/transport/rest.md, site-docs/transport/mcp.md | grep site-docs lists match the new conditional wording; MCP MUST/SHOULD count matches §9.2.4 | pending |
| U4 | CHANGE_LOG entry and repo checks | CHANGE_LOG.md | date/git identity on new entry; `python3 tools/usp_check.py schemas`; confirm no GitHub issue citations in new entry | pending |

### U2 wording (normative)

Keep both items in the existing **MUST** numbered lists (do not move them to SHOULD).

**§9.1.5 item 7** replace:

`Implement webhook signing per [Section 10.1.1](#1011-webhook-security).`

with:

`When the implementation emits webhook payloads or advertises outbound webhook delivery, implement webhook signing per [Section 10.1.1](#1011-webhook-security). Implementations that do neither satisfy this item without implementing webhook signing.`

**§9.2.4 item 7** replace:

`Deliver webhook notifications as JSON-RPC notifications (no `id` field).`

with:

`When the implementation emits webhook notifications or advertises outbound webhook delivery, deliver them as JSON-RPC notifications (no `id` field). Implementations that do neither satisfy this item without delivering webhook notifications.`

Do not edit §10.1.1, §5.4, or §9.2.3 in this unit.

### U3 wording (site-docs)

**REST** (`site-docs/transport/rest.md` item 7): same condition as §9.1.5, keep the page's existing "per the security specification" citation style.

**MCP** (`site-docs/transport/mcp.md`): set the webhook MUST item to the same condition as §9.2.4 item 7. Replace the stale MUST/SHOULD lists in that Conformance Requirements section with the current §9.2.4 lists (items 5-8 MUST and SHOULD 1-5) so the page matches the spec after the webhook condition is applied. Do not rewrite those other items beyond copying the spec.

## Revisions

### 2026-08-26T08:20:00Z - iterative planning converged (3 iterations)

- Iteration 1 drafted from verified §9.1.5, §9.2.4, §10.1.1, §5.4, and site-docs REST/MCP checklists
- Iteration 2 narrowed the trigger to outbound emit-or-advertise, kept a conditional MUST, and scoped MCP site-docs to fix pre-existing checklist drift in the same section
- Iteration 3 locked exact replacement sentences and left §5.4 / §9.2.3 / §10.1.1 unedited; evaluation after that pass made no further plan edits
