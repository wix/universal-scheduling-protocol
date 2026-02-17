# Universal Scheduling Protocol (USP)

**Version:** `2026-02-09`

**Status:** Draft

## Overview

The Universal Scheduling Protocol (USP) provides scheduling capabilities as extensions within the [Universal Commerce Protocol (UCP)](https://ucp.dev) ecosystem. USP defines four capabilities under the `dev.usp.services` namespace that enable consumer platforms and AI agents to discover, query availability of, and book time-based services from businesses.

Three capabilities - catalog, availability, and bookings - are standalone UCP capabilities that operate independently for non-commerce (free) services. A fourth capability - paid bookings - extends UCP's `dev.ucp.shopping.checkout` to wire scheduling context into UCP's payment flow for paid services. USP maintains governance independence via its own `dev.usp` namespace while leveraging UCP's extension architecture - cross-namespace extension is a supported UCP pattern.

## Problem

Existing scheduling standards - iCalendar ([RFC 5545](https://www.rfc-editor.org/rfc/rfc5545)), iTIP ([RFC 5546](https://www.rfc-editor.org/rfc/rfc5546)), CalDAV Scheduling ([RFC 6638](https://www.rfc-editor.org/rfc/rfc6638)), [schema.org/Service](https://schema.org/Service), [Open Booking API](https://openactive.io/open-booking-api/EditorsDraft/1.0CR3/) - address parts of the service scheduling lifecycle but are **fragmented**, lack **native payment integration**, and were not designed for **autonomous AI agent orchestration**. No single open standard unifies:

1. **Service discovery** - types, pricing, policies, and availability hints for AI reasoning
2. **Real-time availability** - time slots, capacity, resource scheduling, and slot holds
3. **Booking lifecycle** - create, confirm, reschedule, cancel, waitlist management, and post-booking events
4. **Payment coordination** - atomic scheduling-plus-payment within a standardized checkout flow (including trust triangle, PCI-DSS scope, SCA/3DS challenges)
5. **Identity and consent** - account linking, buyer consent management, and privacy compliance

in a way that is both machine-readable and interoperable with modern commerce protocols.

USP solves this as a set of UCP extensions with core support for **appointments**, **group sessions**, **reservations**, and **rentals**, with an extensible vertical model for additional service types. By operating within UCP's ecosystem, USP inherits payment architecture, identity linking, versioning, transport bindings, webhook signing, and embedded UI infrastructure - allowing its maintainers to focus exclusively on the scheduling domain.

## Specification

The full protocol is defined in a single document:

| Document | Description |
|----------|-------------|
| [**USP Specification**](specification.md) | Complete protocol: capabilities, discovery, service catalog, availability, bookings, paid bookings extension, security, and transport bindings |

### Capabilities

USP defines four capabilities under the `dev.usp.services` namespace, registered within the business's UCP profile using UCP's registry pattern (object keyed by capability name).

| Capability | Namespace | Type | Section |
|------------|-----------|------|---------|
| Service Catalog | `dev.usp.services.catalog` | Standalone | [Section 4](specification.md#4-service-catalog) |
| Availability | `dev.usp.services.availability` | Standalone | [Section 5](specification.md#5-availability) |
| Bookings | `dev.usp.services.bookings` | Standalone | [Section 6](specification.md#6-bookings) |
| Paid Bookings | `dev.usp.services.paid_bookings` | Extension (`extends: dev.ucp.shopping.checkout`) | [Section 7](specification.md#7-paid-bookings-extension) |
| Waitlist | `dev.usp.services.waitlist` | Extension (`extends: dev.usp.services.bookings`) | [Section 9](specification.md#9-waitlist-extension) |

**Standalone capabilities** (catalog, availability, bookings) operate independently and require no UCP checkout infrastructure. They are sufficient for free services, pay-at-service services, and the full scheduling domain.

**The paid bookings extension** adds a `booking` object to UCP's checkout, analogous to how `dev.ucp.shopping.fulfillment` adds a `fulfillment` object. For paid services, `complete_checkout` atomically finalizes both payment and booking - no protocol switching, no bridging metadata, no cross-protocol cleanup.

### Transport Bindings

USP inherits UCP's transport framework. Standalone capabilities register their operations within this framework. See [Section 10](specification.md#10-transport-bindings) of the specification.

| Binding | Description |
|---------|-------------|
| REST | HTTP/OpenAPI 3.x transport with idempotency support (inherited from UCP) |
| MCP | JSON-RPC/OpenRPC transport for AI agents (inherited from UCP) |
| A2A | Agent-to-Agent protocol for autonomous agent interactions |
| ESP | Embedded Scheduling Protocol for in-app booking UIs (extends UCP's ECP) |

### Payment Architecture

USP inherits UCP's full payment architecture via the `dev.usp.services.paid_bookings` extension. No separate payment bridge or protocol switching is needed:

- **Trust Triangle** - inherited from UCP's three-party trust model
- **Payment Handler Framework** - processor tokenizer, platform tokenizer, and encrypted credential patterns (inherited)
- **PCI-DSS Scope Guidance** - inherited from UCP
- **SCA/3DS Challenge Flow** - inherited from UCP
- **Dynamic Handler Filtering** - context-aware payment method selection, with scheduling-specific criteria (e.g., no BNPL for same-day appointments)
- **AP2 Mandates** - cryptographic integrity for booking agreements (inherited)
- **Buyer Consent** - consent categories and transmission (inherited)

## Key Design Principles

1. **UCP Extension**: USP capabilities are registered within the business's UCP profile at `/.well-known/ucp`. Businesses publish a single discovery endpoint. Platforms discover and negotiate all capabilities - shopping, bookings, and paid bookings - in one pass.
2. **Clean domain separation**: The scheduling domain (catalog, availability, booking lifecycle) is cleanly separated from the commerce domain (checkout, payment). The `paid_bookings` extension bridges them only when payment is required. Free services use the standalone bookings capability with zero UCP checkout involvement.
3. **Agent-first**: Every operation is designed for programmatic consumption, with `continue_url` escalation for human interaction and Embedded Scheduling Protocol (ESP) for in-app UIs.
4. **Extensible**: Vendors define custom capabilities under their reverse-domain namespace (e.g., `com.wix.services.courses`). Extensions use JSON Schema composition (`allOf`, `$defs`) consistent with UCP.
5. **Real-time availability**: Slot holds prevent double-booking with TTL-based automatic release. Idempotency keys (inherited from UCP) prevent duplicate bookings on retry.
6. **Policy-driven**: Cancellation, rescheduling, and no-show policies are machine-readable.
7. **Versioned**: Date-based versioning (`YYYY-MM-DD`) inherited from UCP, with defined negotiation protocol and backwards-compatibility rules.
8. **Secure**: Detached JWS webhook signatures (inherited from UCP), OAuth 2.0 identity linking (inherited from UCP), structured buyer consent (inherited from UCP), and PCI-DSS scope guidance (inherited from UCP).
9. **Atomic commerce**: For paid services, `complete_checkout` atomically finalizes both payment and booking. No dangling bookings, no cross-protocol cleanup, no redundant buyer data.

## License

This specification is released under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).
