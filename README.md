# Universal Scheduling Protocol (USP)

**Version:** `2026-02-09`

## Overview

The Universal Scheduling Protocol (USP) is an open standard for discovering, querying availability of, and booking time-based services between consumer platforms, AI agents, and service businesses.

USP is a **companion protocol** to the [Universal Commerce Protocol (UCP)](https://ucp.dev). UCP handles product commerce -- checkout, payment, fulfillment, and order management for goods. USP fills the gap for **service commerce**: appointments, group sessions, reservations, and rentals. Payment is delegated to UCP's payment architecture rather than reinvented.

## Problem

Existing scheduling standards -- iCalendar ([RFC 5545](https://www.rfc-editor.org/rfc/rfc5545)), CalDAV Scheduling ([RFC 6638](https://www.rfc-editor.org/rfc/rfc6638)), [schema.org/Service](https://schema.org/Service), [Open Booking API](https://openactive.io/open-booking-api/EditorsDraft/1.0CR3/) -- address parts of the service scheduling lifecycle but are **fragmented**, lack **native payment integration**, and were not designed for **autonomous AI agent orchestration**. No single open standard unifies:

1. **Service discovery** -- types, pricing, policies, and availability hints for AI reasoning
2. **Real-time availability** -- time slots, capacity, resource scheduling, and slot holds
3. **Booking lifecycle** -- create, confirm, reschedule, cancel, and waitlist management
4. **Payment coordination** -- bridging scheduling with a standardized checkout/payment flow

in a way that is both machine-readable and interoperable with modern commerce protocols.

USP solves this with core support for **appointments**, **group sessions**, **reservations**, and **rentals**, with an extensible vertical model for additional service types.

## Specification

The full protocol is defined in a single document:

| Document | Description |
|----------|-------------|
| [**USP Specification**](specification.md) | Complete protocol: discovery, service catalog, availability, booking, and UCP payment integration |

### Capabilities

| Capability | Namespace | Section |
|------------|-----------|---------|
| Service Catalog | `dev.usp.services.catalog` | [Section 4](specification.md#4-service-catalog) |
| Availability | `dev.usp.services.availability` | [Section 5](specification.md#5-availability) |
| Booking | `dev.usp.services.booking` | [Section 6](specification.md#6-booking) |
| UCP Payment Integration | (extends booking) | [Section 7](specification.md#7-payment-integration-with-ucp) |
| Waitlist | `dev.usp.services.waitlist` (extends booking) | [Section 9](specification.md#9-waitlist-extension) |

### Transport Bindings

USP supports multiple transport bindings. See [Section 10](specification.md#10-transport-bindings) of the specification.

| Binding | Description |
|---------|-------------|
| REST | HTTP/OpenAPI 3.x transport (primary) |
| MCP | JSON-RPC/OpenRPC transport for AI agents |
| A2A | Agent-to-Agent protocol for autonomous agent interactions |

## Key Design Principles

1. **Companion to UCP**: USP complements UCP. A business MAY publish both `/.well-known/ucp` and `/.well-known/usp`. Payment flows reuse UCP payment handlers.
2. **Agent-first**: Every operation is designed for programmatic consumption, with `continue_url` escalation for human interaction.
3. **Extensible**: Vendors define custom capabilities under their reverse-domain namespace (e.g., `com.wix.services.courses`).
4. **Real-time availability**: Slot holds prevent double-booking with TTL-based automatic release.
5. **Policy-driven**: Cancellation, rescheduling, and no-show policies are machine-readable.

## License

This specification is released under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).
