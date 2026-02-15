# Universal Scheduling Protocol (USP)

**Version:** `2026-02-09`

**Status:** Draft

## Overview

The Universal Scheduling Protocol (USP) is an open standard for discovering, querying availability of, and booking time-based services between consumer platforms, AI agents, and service businesses.

USP is a **companion protocol** to the [Universal Commerce Protocol (UCP)](https://ucp.dev). UCP handles product commerce -- checkout, payment, fulfillment, and order management for goods. USP fills the gap for **service commerce**: appointments, group sessions, reservations, and rentals. Payment is delegated to UCP's payment architecture rather than reinvented.

## Problem

Existing scheduling standards -- iCalendar ([RFC 5545](https://www.rfc-editor.org/rfc/rfc5545)), iTIP ([RFC 5546](https://www.rfc-editor.org/rfc/rfc5546)), CalDAV Scheduling ([RFC 6638](https://www.rfc-editor.org/rfc/rfc6638)), [schema.org/Service](https://schema.org/Service), [Open Booking API](https://openactive.io/open-booking-api/EditorsDraft/1.0CR3/) -- address parts of the service scheduling lifecycle but are **fragmented**, lack **native payment integration**, and were not designed for **autonomous AI agent orchestration**. No single open standard unifies:

1. **Service discovery** -- types, pricing, policies, and availability hints for AI reasoning
2. **Real-time availability** -- time slots, capacity, resource scheduling, and slot holds
3. **Booking lifecycle** -- create, confirm, reschedule, cancel, waitlist management, and post-booking events
4. **Payment coordination** -- bridging scheduling with a standardized checkout/payment flow (including trust triangle, PCI-DSS scope, SCA/3DS challenges)
5. **Identity and consent** -- account linking, buyer consent management, and privacy compliance

in a way that is both machine-readable and interoperable with modern commerce protocols.

USP solves this with core support for **appointments**, **group sessions**, **reservations**, and **rentals**, with an extensible vertical model for additional service types. USP shares wire formats, error models, and governance patterns with UCP to ensure seamless interoperability.

## Specification

The full protocol is defined in a single document:

| Document | Description |
|----------|-------------|
| [**USP Specification**](specification.md) | Complete protocol: discovery, service catalog, availability, booking, payment integration, security, and transport bindings |

### Capabilities

Capabilities use UCP's registry pattern (object keyed by capability name) for consistent cross-protocol implementation.

| Capability | Namespace | Section |
|------------|-----------|---------|
| Service Catalog | `dev.usp.services.catalog` | [Section 4](specification.md#4-service-catalog) |
| Availability | `dev.usp.services.availability` | [Section 5](specification.md#5-availability) |
| Booking | `dev.usp.services.booking` | [Section 6](specification.md#6-booking) |
| UCP Payment Integration | (extends booking) | [Section 7](specification.md#7-payment-integration-with-ucp) |
| Waitlist | `dev.usp.services.waitlist` (extends booking) | [Section 9](specification.md#9-waitlist-extension) |
| Identity Linking | (via OAuth 2.0) | [Section 11.7](specification.md#117-identity-linking) |
| Buyer Consent | (extends booking) | [Section 11.8](specification.md#118-buyer-consent) |

### Transport Bindings

USP supports multiple transport bindings. See [Section 10](specification.md#10-transport-bindings) of the specification.

| Binding | Description |
|---------|-------------|
| REST | HTTP/OpenAPI 3.x transport with idempotency support (primary) |
| MCP | JSON-RPC/OpenRPC transport for AI agents |
| A2A | Agent-to-Agent protocol for autonomous agent interactions |
| ESP | Embedded Scheduling Protocol for in-app booking UIs |

### Payment Architecture

USP delegates payment to UCP and inherits its full payment architecture:

- **Trust Triangle** -- three-party trust model between business, platform, and payment credential provider
- **Payment Handler Framework** -- processor tokenizer, platform tokenizer, and encrypted credential patterns
- **PCI-DSS Scope Guidance** -- minimizing sensitive data exposure across participants
- **SCA/3DS Challenge Flow** -- handling Strong Customer Authentication for European bookings
- **Dynamic Handler Filtering** -- context-aware payment method selection based on booking attributes

See [Sections 7.5–7.9](specification.md#75-trust-triangle) of the specification.

## Key Design Principles

1. **Companion to UCP**: USP complements UCP with structurally aligned wire formats — services use the array-of-transport-objects pattern, capabilities use the registry pattern, and errors use the `messages[]` model. A business MAY publish both `/.well-known/ucp` and `/.well-known/usp`. Payment flows reuse UCP's `complete_checkout` operation and payment handlers.
2. **Agent-first**: Every operation is designed for programmatic consumption, with `continue_url` escalation for human interaction and Embedded Scheduling Protocol (ESP) for in-app UIs.
3. **Extensible**: Vendors define custom capabilities under their reverse-domain namespace (e.g., `com.wix.services.courses`). Extensions use JSON Schema composition (`allOf`, `$defs`) consistent with UCP.
4. **Real-time availability**: Slot holds prevent double-booking with TTL-based automatic release. Idempotency keys prevent duplicate bookings on retry.
5. **Policy-driven**: Cancellation, rescheduling, and no-show policies are machine-readable.
6. **Versioned**: Date-based versioning (`YYYY-MM-DD`) with defined negotiation protocol and backwards-compatibility rules.
7. **Secure**: Detached JWS webhook signatures, OAuth 2.0 identity linking, structured buyer consent, and PCI-DSS scope guidance.

## License

This specification is released under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).
