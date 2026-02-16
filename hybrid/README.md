# Universal Scheduling Protocol (USP) — Hybrid Model

**Version:** `2026-02-09`

**Status:** Draft

## Overview

The Universal Scheduling Protocol (USP) is an open standard that enables consumer platforms and AI agents to **discover**, **check availability of**, and **book** time-based services from businesses.

USP is a **checkout-agnostic** scheduling protocol. It defines the complete scheduling domain — service catalog, availability, holds, and bookings — as an independent protocol that references IETF standards directly for cross-cutting concerns (security, authorization, error format, idempotency, webhook verification). USP does not depend on any specific checkout or payment system.

When payment is required, USP defines a **universal payment handoff**: the booking response includes a `payment_context` object that any checkout system can consume, and a `confirm-payment` callback that any checkout system can call upon completion. Specific checkout integrations (UCP, ACP, embedded checkout, redirect) are defined as **optional binding extensions** — not as part of USP core.

For businesses using [UCP](https://ucp.dev), an optional `dev.usp.services.paid_bookings` extension provides a **streamlined fast lane**: `create_checkout` carries the booking context as a first-class extension field, and `complete_checkout` atomically finalizes both payment and booking. This extension is recommended but not required.

## Problem

Existing scheduling standards -- iCalendar ([RFC 5545](https://www.rfc-editor.org/rfc/rfc5545)), iTIP ([RFC 5546](https://www.rfc-editor.org/rfc/rfc5546)), CalDAV Scheduling ([RFC 6638](https://www.rfc-editor.org/rfc/rfc6638)), [schema.org/Service](https://schema.org/Service), [Open Booking API](https://openactive.io/open-booking-api/EditorsDraft/1.0CR3/) -- address parts of the service scheduling lifecycle but are **fragmented**, lack **native payment integration**, and were not designed for **autonomous AI agent orchestration**. No single open standard unifies:

1. **Service discovery** -- types, pricing, policies, and availability hints for AI reasoning
2. **Real-time availability** -- time slots, capacity, resource scheduling, and slot holds
3. **Booking lifecycle** -- create, confirm, reschedule, cancel, waitlist management, and post-booking events
4. **Payment coordination** -- a checkout-agnostic payment handoff that works with any commerce protocol (UCP, ACP, embedded checkout)
5. **Identity and consent** -- account linking, buyer consent management, and privacy compliance

in a way that is both machine-readable and interoperable with modern commerce protocols.

USP solves this with core support for **appointments**, **group sessions**, **reservations**, and **rentals**, with an extensible vertical model for additional service types. USP references IETF standards directly for cross-cutting infrastructure and provides optional checkout binding extensions for streamlined payment flows.

## Specification

| Document | Description |
|----------|-------------|
| [**USP Specification**](specification.md) | Complete protocol: discovery, service catalog, availability, booking, checkout-agnostic payment integration, security, and transport bindings |

### Capabilities

USP defines three core capabilities and a universal payment integration mechanism. An optional UCP extension provides a streamlined checkout path.

| Capability | Namespace | Type | Section |
|------------|-----------|------|---------|
| Service Catalog | `dev.usp.services.catalog` | Standalone | [Section 4](specification.md#4-service-catalog) |
| Availability | `dev.usp.services.availability` | Standalone | [Section 5](specification.md#5-availability) |
| Bookings | `dev.usp.services.bookings` | Standalone | [Section 6](specification.md#6-bookings) |
| Waitlist | `dev.usp.services.waitlist` | Extension (`extends: bookings`) | [Section 9](specification.md#9-waitlist-extension) |
| Payment Integration | (checkout-agnostic) | Core | [Section 7](specification.md#7-payment-integration) |
| Paid Bookings (UCP) | `dev.usp.services.paid_bookings` | Optional binding extension | [Appendix A](specification.md#appendix-a-ucp-binding-extension) |

**Standalone capabilities** (catalog, availability, bookings) handle the full scheduling lifecycle. For free services, no checkout system is needed.

**Payment integration** uses a universal `payment_context` + `confirm-payment` pattern that works with any checkout system. The platform creates a booking, receives a `payment_context` describing what needs to be paid, processes payment through whatever checkout system is available, and calls `confirm-payment` to finalize.

**The UCP binding extension** (optional) provides a streamlined path for businesses using UCP: `create_checkout` with the booking context baked in, `complete_checkout` with atomic payment + booking confirmation.

### Transport Bindings

USP supports multiple transport bindings. See [Section 10](specification.md#10-transport-bindings) of the specification.

| Binding | Description |
|---------|-------------|
| REST | HTTP/OpenAPI 3.x transport with idempotency support (primary) |
| MCP | JSON-RPC/OpenRPC transport for AI agents |
| A2A | Agent-to-Agent protocol for autonomous agent interactions |
| ESP | Embedded Scheduling Protocol for in-app booking UIs |

### Payment Architecture

USP core is checkout-agnostic. Payment is handled through the universal `payment_context` → checkout system → `confirm-payment` pattern. The platform uses whichever checkout system the business supports:

| Path | When Used | API Calls |
|------|-----------|-----------|
| **UCP Extension** (fast lane) | Business declares `dev.usp.services.paid_bookings` | `create_checkout` (with booking) → token → `complete_checkout` (atomic) |
| **Generic + UCP** | Business has UCP but no extension | `create_booking` → `create_checkout` → `update_checkout` → token → `complete_checkout` → `confirm-payment` |
| **Generic + ACP** | Business uses ACP | `create_booking` → ACP payment flow → `confirm-payment` |
| **Generic + Redirect** | Business provides `payment_url` | `create_booking` → buyer redirected → webhook |
| **Generic + Embedded** | Platform handles payment directly | `create_booking` → platform PSP integration → `confirm-payment` |

### Cross-Cutting Concerns (IETF Standards)

USP references IETF standards directly for all cross-cutting infrastructure — it does not depend on any specific commerce protocol for these:

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

1. **Checkout-agnostic**: USP core has zero dependencies on any specific checkout or payment protocol. The `payment_context` + `confirm-payment` pattern works with UCP, ACP, embedded checkout, redirect, or any future commerce protocol.
2. **IETF-native**: Cross-cutting concerns (security, auth, errors, idempotency, webhooks) reference IETF RFCs directly. USP does not inherit or redefine infrastructure from another protocol.
3. **Fast lane for UCP**: The optional `dev.usp.services.paid_bookings` extension gives businesses on UCP the most streamlined path — atomic payment + booking, fewer API calls, schema-validated booking context.
4. **Agent-first**: Every operation is designed for programmatic consumption, with `continue_url` escalation for human interaction and Embedded Scheduling Protocol (ESP) for in-app UIs.
5. **Extensible**: Vendors define custom capabilities under their reverse-domain namespace (e.g., `com.wix.services.courses`). Extensions use JSON Schema composition (`allOf`, `$defs`).
6. **Real-time availability**: Slot holds prevent double-booking with TTL-based automatic release. Idempotency keys prevent duplicate bookings on retry.
7. **Policy-driven**: Cancellation, rescheduling, and no-show policies are machine-readable.
8. **Versioned**: Date-based versioning (`YYYY-MM-DD`) with defined negotiation protocol and backwards-compatibility rules.
9. **Secure**: HTTP Message Signatures for webhook integrity, OAuth 2.0 identity linking, structured buyer consent, and PCI-DSS scope guidance.
10. **Graceful degradation**: Platforms always have a path to payment — from the optimized UCP extension down to simple payment URL redirect — without changing any USP scheduling calls.

## License

This specification is released under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).
