---
title: Security
description: USP security model — TLS transport, RFC 9421 webhook signatures, OAuth 2.0 authorization, rate limiting, hold abuse prevention, and PCI-DSS guidance.
keywords: USP security, webhook signatures, OAuth 2.0, TLS, rate limiting, scheduling API security, RFC 9421
---

# Security

USP's security model is built on IETF standards. This page covers both
the shared USP security requirements and the additional infrastructure
that Standalone Mode implementations must provide.

---

## USP Security Requirements

These requirements apply to **both** deployment modes:

### Transport Security

- All endpoints **MUST** use HTTPS with TLS 1.2+ (TLS 1.3 recommended per
  [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446)).
- HTTP Strict Transport Security (HSTS) headers **SHOULD** be sent.

### Webhook Security

USP uses [RFC 9421 HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421)
for webhook integrity verification:

- Businesses **MUST** sign webhook payloads using keys published in the
  business profile: UCP-canonical `keys` (**MUST** when signing), with
  optional identical `signing_keys` during transition (**RECOMMENDED**
  dual-publish). Verifiers resolve `keys` first, then fall back to
  `signing_keys`.
- Platforms **MUST** verify webhook signatures before processing events.
- Signatures **MUST** cover at minimum: the request body digest,
  `Content-Type` header, and a timestamp (the RFC 9421 `created` signature
  parameter, written `;created=...`, not as a covered component).

!!! warning "Replay Protection differs by direction"

    **Webhooks** carry no idempotency key, so receivers **MUST** reject
    payloads whose `created` parameter is older than a configurable window
    (recommended: 5 minutes) *and* de-duplicate on the event `id`.

    **Requests** follow UCP's model instead: replay protection is the signed
    `Idempotency-Key`, and `created` is OPTIONAL. Businesses **MUST NOT**
    reject a signed request merely because it carries no `created` parameter.

### Hold Abuse Prevention

Time slot holds are a potential abuse vector. Businesses **SHOULD** implement:

- **Maximum concurrent holds per buyer** — Prevent a single buyer from
  locking up all available slots.
- **Short TTLs** — Recommended 5-10 minutes. Holds auto-expire.
- **Backoff for repeated hold-and-release** — Detect patterns of holding
  and releasing without booking, and apply progressive delays.

### Idempotency

State-changing operations (booking creation, cancellation, rescheduling,
payment confirmation) **SHOULD** use an idempotency key:

- **REST:** `Idempotency-Key` header
  (per [draft-ietf-httpapi-idempotency-key-header](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/))
- **MCP:** `_meta.usp.idempotency_key` field

### Platform Authentication for Privileged Operations

This requirement applies in **both** deployment modes: it is not inherited
from UCP in UCP-Native Mode. See specification.md
[Section 10.1.6](../specification.md#1016-platform-authentication-for-privileged-operations)
for the full normative text and rationale.

- **Public operations** (catalog, availability, profile discovery) **MAY**
  remain unauthenticated.
- **Privileged operations** (booking create/update/confirm/cancel/reschedule,
  holds, waitlist actions, payment-adjacent completion, registry writes, and
  any response carrying buyer personal data) **MUST** be authenticated.
- Every request to a privileged operation **MUST** carry a `USP-Agent` (or
  `UCP-Agent`) header on REST, or `_meta.usp.profile` on MCP, that resolves to
  a profile fetchable over HTTPS with no redirects, cached by URI.
- A business **MUST** accept at least one of: HTTP Message Signatures
  (RFC 9421, **recommended default**, permissionless, works the same for one
  platform or a million distinct personal-agent instances), a booking-scoped
  capability credential (authorizes get/cancel/PII operations on one booking
  regardless of platform identity), OAuth 2.0 Bearer, an API key, or mTLS. A
  business **SHOULD NOT** accept only a pre-established mechanism (OAuth, API
  key, mTLS) once it intends to serve platforms it has not individually
  vetted.
- Businesses declare which mechanisms they require in the `authorization`
  object of their business profile
  ([`schemas/profile.json`](../schemas/profile.json) `$defs/AuthorizationPolicy`
  / `$defs/AuthorizationMechanism`). The same mechanism set is expressed in
  [`openapi/usp-rest.json`](../openapi/usp-rest.json) `components.securitySchemes`
  and [`openrpc/usp-mcp.json`](../openrpc/usp-mcp.json)
  `components.x-usp-securitySchemes`; MCP may present credentials on the HTTP
  layer (when MCP is over HTTP) or via `_meta.usp.authorization`.

!!! info "Why this diverges from UCP's optional-auth guidance"

    UCP treats platform authentication as `SHOULD`, which fits a world of a
    few well-known platforms that can be vetted out-of-band. USP's scheduling
    domain also has to serve personal, single-user "bring your own agent"
    deployments, where there is no realistic pre-onboarding step and no
    brand-level accountability. USP hardens this one point (privileged
    operations MUST be authenticated) while keeping every other UCP-inherited
    concern unchanged, and expresses the requirement as a declared business
    policy (not a single mandated mechanism) so it stays compatible if UCP's
    own posture evolves.

---

## Standalone Mode Security Infrastructure

!!! note "UCP-Native Mode"

    If you're using UCP-Native Mode, skip this section — UCP provides
    the security transport plumbing (rate limiting, CORS). Platform
    authentication for privileged operations above still applies.

Standalone Mode implementations **MUST** additionally provide:

### Pre-established Authentication Mechanics

The mechanism-agnostic requirement lives in
[Platform Authentication for Privileged Operations](#platform-authentication-for-privileged-operations)
above. For platforms using a pre-established mechanism in Standalone Mode,
USP uses [OAuth 2.0 (RFC 6749)](https://www.rfc-editor.org/rfc/rfc6749) with
[DPoP (RFC 9449)](https://www.rfc-editor.org/rfc/rfc9449):

- **Platform-to-business:** OAuth 2.0 client credentials flow for
  machine-to-machine API access, the **recommended** pre-established
  mechanism.
- **Identity linking:** OAuth 2.0 authorization code flow for linking
  buyer accounts across platforms and businesses.
- **Token binding:** DPoP tokens **SHOULD** be used to bind access
  tokens to the client's key pair, preventing token theft.

This list is not exclusive: HTTP Message Signatures and booking-scoped
credentials remain available (and recommended alongside any of the above) for
platforms without a pre-established relationship.

### Rate Limiting

Businesses **SHOULD** implement rate limiting per
[draft-ietf-httpapi-ratelimit-headers](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/):

- Return `429 Too Many Requests` with `Retry-After` header when limits
  are exceeded.
- Include `RateLimit-Limit`, `RateLimit-Remaining`, and `RateLimit-Reset`
  headers on responses.

### CORS

Businesses exposing USP endpoints for browser-based platforms **MUST**
implement appropriate CORS headers.

---

## PCI-DSS Scope Guidance

USP is designed to minimize PCI-DSS scope for implementations:

- **USP never handles raw payment credentials.** Payment processing is
  delegated to the checkout system (UCP or standalone).
- **The `payment_context` object** contains amount, currency, and metadata —
  never card numbers or sensitive payment data.
- **Credential Providers** (Google Wallet, Apple Pay) hold the sensitive
  instruments, not the platform or business.

---

## Security Checklist

| Requirement | UCP-Native | Standalone | Standard |
|-------------|:----------:|:----------:|----------|
| HTTPS / TLS 1.2+ | Required | Required | RFC 8446 |
| Webhook signatures | Required | Required | RFC 9421 |
| Idempotency keys | Recommended | Recommended | draft-ietf-httpapi-idempotency-key-header |
| Hold abuse prevention | Recommended | Recommended | USP spec |
| Privileged-op authentication (some accepted mechanism) | Required | Required | USP spec §10.1.6 |
| HTTP Message Signatures (recommended default mechanism) | Available | Available | RFC 9421 |
| Booking-scoped capability credential | Available (#134, #162) | Available (#134, #162) | USP spec §10.1.6 |
| OAuth 2.0 (one accepted mechanism) | Available | Available | RFC 6749 |
| DPoP token binding | Inherited | Recommended | RFC 9449 |
| Rate limiting | Inherited | Recommended | draft-ietf-httpapi-ratelimit-headers |
| CORS | Inherited | Required | Fetch Standard |
