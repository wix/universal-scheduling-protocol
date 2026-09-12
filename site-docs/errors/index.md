# Problem types

USP uses RFC 9457 Problem Details for **protocol errors**. Every canonical
`type` URI is under `https://usp-protocol.dev/errors/` and uses a kebab-case
slug. Clients branch on the exact URI, never on the human-readable title.

Not every USP error code is a Problem type. Specification Section 9.4.1 splits
conditions into three disjoint families, and only the first family below has
`type` URIs.

## Protocol errors (RFC 9457 Problem types)

Returned with a `4xx` or `5xx` status and an `application/problem+json` body.
The full matrix of status, `type` slug, JSON-RPC code and MCP `data.code` is in
specification Section 9.4.3.

- [`algorithm-unsupported`](algorithm-unsupported.md): The requested signature or digest algorithm is not supported.
- [`authentication-required`](authentication-required.md): The operation requires valid authentication.
- [`booking-not-found`](booking-not-found.md): The requested booking does not exist or is not visible to the caller.
- [`cursor-expired`](cursor-expired.md): The supplied pagination cursor is no longer honored.
- [`digest-mismatch`](digest-mismatch.md): The supplied content digest does not match the request content.
- [`entry-not-found`](entry-not-found.md): The waitlist entry does not exist. Requires the waitlist capability.
- [`hold-limit-exceeded`](hold-limit-exceeded.md): The buyer has reached the allowed concurrent hold limit.
- [`idempotency-conflict`](idempotency-conflict.md): An idempotency key was reused with a different request.
- [`invalid-profile-url`](invalid-profile-url.md): The profile URL is malformed, non-HTTPS, or unresolvable.
- [`invalid-request`](invalid-request.md): The request is malformed or violates protocol requirements.
- [`key-not-found`](key-not-found.md): The verification key identified by the request could not be found.
- [`pop-key-mismatch`](pop-key-mismatch.md): The proof-of-possession key does not match the bound key.
- [`pop-proof-invalid`](pop-proof-invalid.md): The proof of possession failed to parse or verify.
- [`pop-proof-missing`](pop-proof-missing.md): A required proof-of-possession proof was not supplied.
- [`pop-proof-replayed`](pop-proof-replayed.md): The proof-of-possession proof has already been used.
- [`pop-proof-required`](pop-proof-required.md): A sender-constrained credential was presented without a proof.
- [`profile-malformed`](profile-malformed.md): The profile document fails schema validation.
- [`profile-not-trusted`](profile-not-trusted.md): The discovered protocol profile is not trusted under local policy.
- [`profile-unreachable`](profile-unreachable.md): The protocol profile could not be fetched.
- [`proof-nonce-required`](proof-nonce-required.md): The business requires a nonce in the proof.
- [`range-too-wide`](range-too-wide.md): The requested availability range exceeds the supported limit.
- [`rate-limited`](rate-limited.md): The caller has exceeded the applicable request rate.
- [`revision-mismatch`](revision-mismatch.md): The supplied resource revision does not match the current revision.
- [`server-error`](server-error.md): The server encountered an unexpected failure.
- [`service-unavailable`](service-unavailable.md): The business is temporarily unable to handle requests.
- [`signature-expired`](signature-expired.md): The HTTP message signature is outside its accepted time window.
- [`signature-invalid`](signature-invalid.md): The HTTP message signature could not be verified.
- [`signature-missing`](signature-missing.md): A required HTTP message signature was not supplied.
- [`validation-error`](validation-error.md): One or more request fields failed validation.
- [`version-unsupported`](version-unsupported.md): The requested USP version is not supported.

## Business outcome codes (not Problem types)

These are **not** `type` URIs. The request succeeded, and the business is
reporting a scheduling or policy outcome in a `messages[]` entry carried with
HTTP `200 OK`. Clients branch on `messages[].code`. The registry is
specification Section 9.4.2.

`slot_unavailable`, `hold_expired`, `booking_window_violated`,
`capacity_exceeded`, `reschedule_limit_reached`, `cancellation_not_allowed`,
`invalid_transition`, `payment_required`, `payment_expired`,
`payment_amount_mismatch`, `actions_pending`, `price_mismatch`,
`capabilities_incompatible`.

The waitlist extension registers its own codes in specification Section 11.1.6.

Pages kept for older links: [`actions-pending`](actions-pending.md),
[`reschedule-limit-reached`](reschedule-limit-reached.md),
[`slot-unavailable`](slot-unavailable.md),
[`slot-expired`](slot-expired.md).

## ESP frame codes (not Problem types)

The Embedded Scheduling Protocol carries failures as `esp.error` postMessage
frames, which are neither HTTP responses nor JSON-RPC errors: `canceled`,
`payment_failed`, `slot_unavailable`, `internal_error`. See specification
Section 9.5.5.

Page kept for older links: [`payment-failed`](payment-failed.md).
