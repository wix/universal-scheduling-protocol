# Universal Scheduling Protocol (USP)

**Version:** `2026-02-09`

**Status:** Draft

## Overview

The Universal Scheduling Protocol (USP) is an open standard that enables consumer platforms and AI agents to **discover**, **check availability of**, and **book** time-based services from businesses. USP is a standalone, complete protocol for both **paid** and **free** agentic scheduling.

USP defines the complete scheduling domain -- service catalog, availability, holds, and bookings -- as an independent protocol that references IETF standards directly for cross-cutting concerns (security, authorization, error format, idempotency, webhook verification).

For paid services, USP is not tied to any single commerce protocol. When payment is required, USP defines a `payment_context` handoff and a `confirm-payment` callback that any payment system can use. To maximize protocol interoperability, USP includes checkout path extensions for [UCP](https://ucp.dev) and [ACP](https://agenticcommerce.dev/), and is architecturally extensible for future commerce protocols. Platforms that already support a given commerce protocol can adopt the corresponding checkout path extension and benefit from natural integration with minimal effort.

## Problem

Existing scheduling standards -- iCalendar ([RFC 5545](https://www.rfc-editor.org/rfc/rfc5545)), iTIP ([RFC 5546](https://www.rfc-editor.org/rfc/rfc5546)), CalDAV Scheduling ([RFC 6638](https://www.rfc-editor.org/rfc/rfc6638)), [schema.org/Service](https://schema.org/Service), [Open Booking API](https://openactive.io/open-booking-api/EditorsDraft/1.0CR3/) -- address parts of the service scheduling lifecycle but are **fragmented**, lack **native payment integration**, and were not designed for **autonomous AI agent orchestration**. No single open standard unifies:

1. **Service discovery** -- types, pricing, policies, and availability hints for AI reasoning
2. **Real-time availability** -- time slots, capacity, resource scheduling, and slot holds
3. **Booking lifecycle** -- create, confirm, reschedule, cancel, waitlist management, and post-booking events
4. **Payment coordination** -- a payment handoff that works with any commerce protocol, with checkout path extensions for specific protocols
5. **Identity and consent** -- account linking, buyer consent management, and privacy compliance

in a way that is both machine-readable and interoperable with modern commerce protocols.

USP solves this with core support for **appointments**, **group sessions**, **reservations**, and **rentals**, with an extensible vertical model for additional service types. USP references IETF standards directly for cross-cutting infrastructure and provides checkout path extensions for natural integration with existing commerce protocols.

## Specification

| Document | Description |
|----------|-------------|
| [**USP Specification**](specification.md) | Complete protocol: discovery, service catalog, availability, booking, payment integration, security, and transport bindings |

### Capabilities

USP defines three core capabilities and a universal payment integration mechanism, with checkout path extensions for specific commerce protocols.

| Capability | Namespace | Type | Section |
|------------|-----------|------|---------|
| Service Catalog | `dev.usp.services.catalog` | Standalone | [Section 4](specification.md#4-service-catalog) |
| Availability | `dev.usp.services.availability` | Standalone | [Section 5](specification.md#5-availability) |
| Bookings | `dev.usp.services.bookings` | Standalone | [Section 6](specification.md#6-bookings) |
| Waitlist | `dev.usp.services.waitlist` | Extension (`extends: bookings`) | [Section 9](specification.md#9-waitlist-extension) |
| Payment Integration | (generic + extensions) | Core | [Section 7](specification.md#7-payment-integration) |

**Standalone capabilities** (catalog, availability, bookings) handle the full scheduling lifecycle. For free services, no checkout system is needed.

**Payment integration** uses a `payment_context` + `confirm-payment` pattern that works with any checkout system. Checkout path extensions for [UCP](specification.md#75-ucp-checkout-path) and [ACP](specification.md#76-acp-checkout-path) provide natural integration with those commerce protocols.

### Transport Bindings

USP supports multiple transport bindings. See [Section 10](specification.md#10-transport-bindings) of the specification.

| Binding | Description |
|---------|-------------|
| REST | HTTP/OpenAPI 3.x transport with idempotency support (primary) |
| MCP | JSON-RPC/OpenRPC transport for AI agents |
| A2A | Agent-to-Agent protocol for autonomous agent interactions |
| ESP | Embedded Scheduling Protocol for in-app booking UIs |

### Payment Architecture

USP provides a generic payment handoff and checkout path extensions for specific commerce protocols. The platform uses whichever checkout path the business supports:

| Path | When Used | API Calls |
|------|-----------|-----------|
| **Generic Path** | Business supports any checkout system | `create_booking` -> `payment_context` -> checkout -> `confirm-payment` |
| **UCP Path** | Business declares `dev.usp.services.paid_bookings` | `create_checkout` (with booking) -> token -> `complete_checkout` (atomic) |
| **ACP Path** | Business declares `checkout_systems: ["acp"]` | `create_booking` -> ACP checkout session -> `confirm-payment` |
| **Redirect Path** | Business provides `payment_url` | `create_booking` -> buyer redirected -> webhook |
| **Embedded Path** | Platform handles payment directly | `create_booking` -> platform PSP integration -> `confirm-payment` |

### Cross-Cutting Concerns (IETF Standards)

USP references IETF standards directly for all cross-cutting infrastructure:

| Concern | Standard | Section |
|---------|----------|---------|
| Discovery | RFC 8615 (Well-Known URIs) | [Section 3](specification.md#3-discovery-and-negotiation) |
| Error model | RFC 9457 (Problem Details for HTTP APIs) | [Section 10.1](specification.md#101-rest-binding) |
| Authorization | RFC 6749 (OAuth 2.0), RFC 9449 (DPoP) | [Section 11.6](specification.md#116-authentication-and-authorization) |
| Transport security | RFC 8446 (TLS 1.3), RFC 9110 (HTTP Semantics) | [Section 11.1](specification.md#111-transport-security) |
| Idempotency | draft-ietf-httpapi-idempotency-key-header | [Section 10.1.1](specification.md#1011-idempotency) |
| Webhook verification | RFC 9421 (HTTP Message Signatures) | [Section 11.3](specification.md#113-webhook-security) |
| Rate limiting | draft-ietf-httpapi-ratelimit-headers | [Section 11.2](specification.md#112-rate-limiting) |

## Key Design Principles

1. **Payment Flexibility**: USP is not tied to any single commerce protocol. The `payment_context` + `confirm-payment` pattern works with any payment system, and checkout path extensions provide natural integration with specific commerce protocols.
2. **IETF-native**: Cross-cutting concerns (security, auth, errors, idempotency, webhooks) reference IETF RFCs directly. USP does not inherit or redefine infrastructure from another protocol.
3. **Protocol Interoperability**: USP includes checkout path extensions for UCP and ACP, and is architecturally extensible for future commerce protocols. Platforms that already support a given commerce protocol can adopt the corresponding extension with minimal effort.
4. **Agent-first**: Every operation is designed for programmatic consumption, with `continue_url` escalation for human interaction and Embedded Scheduling Protocol (ESP) for in-app UIs.
5. **Extensible**: Vendors define custom capabilities under their reverse-domain namespace (e.g., `com.wix.services.courses`). Extensions use JSON Schema composition (`allOf`, `$defs`).
6. **Real-time availability**: Slot holds prevent double-booking with TTL-based automatic release. Idempotency keys prevent duplicate bookings on retry.
7. **Policy-driven**: Cancellation, rescheduling, and no-show policies are machine-readable.
8. **Versioned**: Date-based versioning (`YYYY-MM-DD`) with defined negotiation protocol and backwards-compatibility rules.
9. **Secure**: HTTP Message Signatures for webhook integrity, OAuth 2.0 identity linking, structured buyer consent, and PCI-DSS scope guidance.
10. **Graceful degradation**: Platforms always have a path to payment -- from protocol-specific checkout extensions to generic payment handoff to simple payment URL redirect -- without changing any USP scheduling calls.

## License

This specification is released under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).
