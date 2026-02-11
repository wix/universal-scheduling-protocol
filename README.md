# Universal Scheduling Protocol (USP)

**Version:** `2026-02-09`

## Overview

The Universal Scheduling Protocol (USP) is an open standard for discovering, querying availability of, and booking time-based services between consumer platforms, AI agents, and service businesses.

USP is a **companion protocol** to the [Universal Commerce Protocol (UCP)](https://ucp.dev). UCP handles product commerce -- checkout, payment, fulfillment, and order management for goods. USP fills the gap for **service commerce**: appointments, group sessions, reservations, and rentals. Payment is delegated to UCP's payment architecture rather than reinvented.

## Problem

No standard defines how an AI agent or consumer platform can:

1. **Discover** what services a business offers (types, pricing, policies)
2. **Query** real-time availability (open time slots, capacity, resources)
3. **Book** a time-based service through a standardized lifecycle (create, confirm, reschedule, cancel)

USP solves this for four verticals: **appointments**, **group sessions**, **reservations**, and **rentals**.

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

### Detailed Reference (extended spec)

The `specification/` directory contains the extended reference with full field tables, JSON Schemas, and transport bindings for implementers:

| Document | Description |
|----------|-------------|
| [Service Catalog](specification/service-catalog.md) | Full service catalog schema and operations |
| [Availability](specification/availability.md) | Availability queries, slot holds, opening hours |
| [Booking](specification/booking.md) | Booking lifecycle, all operations, webhooks |
| [Checkout Integration](specification/checkout-integration.md) | UCP payment orchestration flows |
| [REST Binding](specification/transport-rest.md) | HTTP/OpenAPI transport mapping |
| [MCP Binding](specification/transport-mcp.md) | JSON-RPC/OpenRPC transport for AI agents |

## Key Design Principles

1. **Companion to UCP**: USP complements UCP. A business MAY publish both `/.well-known/ucp` and `/.well-known/usp`. Payment flows reuse UCP payment handlers.
2. **Agent-first**: Every operation is designed for programmatic consumption, with `continue_url` escalation for human interaction.
3. **Extensible**: Vendors define custom capabilities under their reverse-domain namespace (e.g., `com.wix.services.courses`).
4. **Real-time availability**: Slot holds prevent double-booking with TTL-based automatic release.
5. **Policy-driven**: Cancellation, rescheduling, and no-show policies are machine-readable.

## License

This specification is released under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).
