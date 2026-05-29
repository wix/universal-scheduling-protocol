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
  business profile.
- Platforms **MUST** verify webhook signatures before processing events.
- Signatures **MUST** cover at minimum: the request body digest,
  `Content-Type` header, and a timestamp.

!!! warning "Replay Protection"

    Webhook receivers **SHOULD** reject payloads older than a configurable
    window (recommended: 5 minutes) to prevent replay attacks.

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

---

## Standalone Mode Security Infrastructure

!!! note "UCP-Native Mode"

    If you're using UCP-Native Mode, skip this section — UCP provides
    the security infrastructure (auth, rate limiting, CORS).

Standalone Mode implementations **MUST** additionally provide:

### Authentication and Authorization

USP uses [OAuth 2.0 (RFC 6749)](https://www.rfc-editor.org/rfc/rfc6749) with
[DPoP (RFC 9449)](https://www.rfc-editor.org/rfc/rfc9449) for authorization:

- **Platform-to-business:** OAuth 2.0 client credentials flow for
  machine-to-machine API access.
- **Identity linking:** OAuth 2.0 authorization code flow for linking
  buyer accounts across platforms and businesses.
- **Token binding:** DPoP tokens **SHOULD** be used to bind access
  tokens to the client's key pair, preventing token theft.

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
| OAuth 2.0 | Inherited | Required | RFC 6749 |
| DPoP token binding | Inherited | Recommended | RFC 9449 |
| Rate limiting | Inherited | Recommended | draft-ietf-httpapi-ratelimit-headers |
| CORS | Inherited | Required | Fetch Standard |
