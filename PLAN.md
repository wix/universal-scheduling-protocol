# Feature: booking-expires-at

## Goal

Condition §5.2 booking-expiry MUSTs on advertising `expires_at` on Booking, so omission is a documented, conformant wire shape when the business does not hold unconfirmed inventory, while any advertised deadline stays a hard MUST (cancel, remain retrievable, release any hold).

## Non-goals

- Changing usp-impl or inventing a sliding `expires_at` in any product repo
- Changing Hold `expires_at`, Action `expires_at`, credential `expires_at`, or waitlist `offer_expires_at`
- JSON Schema `if`/`then` that requires `expires_at` by `status` (pending without the field is now allowed)
- Playground or example JSON that already advertises `expires_at` (that remains a valid advertised shape)
- Editing OpenAPI/OpenRPC object trees (they stay thin `$ref`s; no inline Booking duplication)
- Weakening payment-action expiry in §8.5.4 (that clock is independent of Booking `expires_at`)

## Must-preserve constraints

- If Booking includes `expires_at`, expiry MUSTs stay: cancel, remain retrievable, release any slot hold
- A business that holds slot capacity for a `pending` or `requires_action` booking MUST advertise `expires_at` (do not let holders omit the field and skip cancel)
- Hold alignment SHOULD (hold deadline aligned with or earlier than booking `expires_at`) remains, when the booking advertises the field
- Canonical Booking shape lives only in `schemas/booking.json`; bindings stay single `$ref`s
- No GitHub issue, PR, or `#N` citations in spec, site-docs, schemas, bindings, README, or new CHANGE_LOG bullets
- Site-docs stay in sync with the same normative rule

## File actions

| Path | Action | Reason |
|------|--------|--------|
| specification.md | modify | Replace "Present for pending/requires_action" and unconditional Booking Expiry MUSTs; condition §3.10 confirmation_mode and §8.5.4 alignment on advertised booking `expires_at` |
| schemas/booking.json | modify | Booking `expires_at` description currently says it is present for pending/requires_action, which would contradict omission |
| site-docs/specification/booking.md | modify | Site mirror of the §5.2 field table and Booking Expiry rules |
| CHANGE_LOG.md | modify | Required change-log entry with motivation; no tracker citations |

## Work units

| ID | Description | Files | Verification | Status |
|----|-------------|-------|--------------|--------|
| U1 | Plan and commit this PLAN.md | PLAN.md | test -f PLAN.md | done |
| U2 | Condition Booking expiry in specification.md (§5.2, §3.10, §8.5.4 alignment only) | specification.md | grep -n "Present for" specification.md; grep Booking Expiry block for "when" / omit | pending |
| U3 | Align schemas/booking.json Booking.expires_at description | schemas/booking.json | python3 -m json.tool schemas/booking.json >/dev/null; grep expires_at description | pending |
| U4 | Mirror the rule in site-docs/specification/booking.md | site-docs/specification/booking.md | grep -n "Present for\\|MAY omit\\|advertis" site-docs/specification/booking.md | pending |
| U5 | Append CHANGE_LOG.md entry (real date/git identity, no GitHub citations) | CHANGE_LOG.md | test -f CHANGE_LOG.md | pending |

## Revisions

### 2026-08-26T08:18:00+03:00 - iterative planning (converged after 3 iterations)

- Iteration 1: drafted from live §5.2 (optional field + "Present for pending/requires_action" + unconditional cancel/retrievable/release MUSTs), `schemas/booking.json` matching description, `site-docs/specification/booking.md` mirror, §3.10 confirmation_mode assuming a booking `expires_at`.
- Iteration 2 (critique): require advertising when the business holds unconfirmed inventory so holders cannot omit and skip cancel; item 4 is "any" hold; do not add status-based schema required; leave playground examples; keep payment-action expiry independent.
- Iteration 3 (critique): §8.5.4 SHOULD-align with booking `expires_at` only when that field is advertised; OpenAPI/OpenRPC already thin `$ref`s so no binding file actions; service-catalog site page does not restate the expires_at MUST so leave it. Evaluate found no further changes.
