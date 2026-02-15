# Universal Scheduling Protocol (USP) — ACP Binding

**Version:** `2026-02-09`

**Status:** Draft

## Overview

This document provides an **ACP binding** for the [Universal Scheduling Protocol (USP)](../extension/specification.md) - a mapping layer that enables sellers implementing the [Agentic Commerce Protocol (ACP)](https://agenticcommerce.dev/) to offer USP scheduling capabilities without adopting [UCP](https://ucp.dev).

USP is primarily a set of capabilities and extensions within the [Universal Commerce Protocol (UCP)](https://ucp.dev) ecosystem. The [USP Specification](../extension/specification.md) defines the complete scheduling domain - service catalog, availability, bookings, waitlist - along with all supporting infrastructure inherited from UCP. This ACP binding is a compatibility layer, not a second specification: it references the USP Specification for all scheduling domain content and defines only what is specific to ACP.

## Why USP Is a UCP Extension

A production-grade scheduling protocol requires far more than service catalog schemas and booking operations. It must support identity linking, transport layer bindings (REST, MCP, A2A), webhook signature verification, consent management, embedded UI, versioning, and namespace governance. Maintaining all of these independently is a massive undertaking.

As a UCP extension, USP inherits this entire infrastructure stack for free - its maintainers can focus exclusively on the core scheduling domain (catalog, availability, booking lifecycle). This is a deliberate architectural choice: it is better to ride on the shoulders of a general-purpose commerce protocol than to rebuild that infrastructure from scratch.

**UCP** was designed as a general-purpose commerce platform protocol with a rich capability registry, transport framework, identity linking, buyer consent, embedded UI (ECP), and extension architecture built for cross-namespace capabilities. USP plugs into UCP naturally.

**ACP** was designed as a focused agentic checkout protocol. It provides excellent checkout sessions, payment handlers, delegate payment, and order management - but it does not provide a general-purpose capability registry, MCP/A2A transport bindings, identity linking, buyer consent, or embedded UI infrastructure.

| Infrastructure | UCP Provides (USP inherits) | ACP Provides |
|---|---|---|
| Discovery & capability registry | `/.well-known/ucp` with general-purpose registry | No general discovery |
| Transport bindings | REST, MCP (JSON-RPC 2.0), A2A | REST only |
| Identity linking | `dev.ucp.common.identity_linking` | Not defined |
| Buyer consent | `dev.ucp.shopping.buyer_consent` | Not defined |
| Embedded UI | ECP (communication, delegation, security) | Not defined |
| Namespace governance | Explicit rules, cross-namespace extension | Reverse-domain for extensions only |
| Webhook signing | Detached JWS, key rotation | `Signature` + `Timestamp` headers |
| Payment architecture | Trust triangle, 3 handler patterns, PCI-DSS, SCA/3DS | Payment handlers, delegate payment, 3DS |

If USP were positioned as an ACP extension in the same way it is a UCP extension, it would need to independently define and maintain all the infrastructure that ACP does not provide. The scheduling domain experts who maintain USP would be responsible for evolving discovery mechanisms, transport bindings, identity flows, and consent models - none of which are scheduling concerns. This binding avoids that burden entirely.

## Role of This Binding

For a seller that has already implemented ACP's Agentic Checkout but hasn't adopted UCP, this binding provides a path to USP scheduling capabilities without switching commerce protocols. The seller:

1. **Implements USP standalone scheduling endpoints** (catalog, availability, bookings) using ACP's header and authentication conventions. The scheduling domain logic - schemas, operations, validation rules, policies - is identical to the UCP binding and is defined in the [USP Specification](../extension/specification.md).

2. **Bridges paid bookings through ACP checkout sessions** using ACP's formal extension mechanism. A `booking` object is added to `POST /checkout_sessions`, and completing the checkout atomically finalizes both payment and booking.

3. **Publishes a `/.well-known/usp` scheduling profile** for discovery, since ACP does not have UCP's general-purpose capability registry.

## Specification

| Document | Description |
|----------|-------------|
| [**USP Specification**](../extension/specification.md) | The normative, complete protocol: scheduling domain, infrastructure, transport bindings, security. Defined as a UCP extension. |
| [**ACP Binding**](specification.md) | This binding: infrastructure mapping, ACP-specific discovery, paid bookings via ACP checkout sessions, ACP-specific flow examples. |

The ACP binding references the USP Specification for all scheduling domain content (Sections 4-6, 9) and defines only:

- **Infrastructure mapping** - how ACP's headers, versioning, idempotency, error model, and webhook signing map to USP's UCP-based expectations
- **Discovery** - `/.well-known/usp` scheduling profile for ACP sellers
- **Paid bookings** - ACP checkout session extension replacing USP's UCP checkout extension
- **Post-booking lifecycle** - ACP order management for refunds and disputes

## Capabilities

USP capabilities are the same regardless of binding. The scheduling domain is commerce-protocol-independent.

| Capability | Namespace | Type | Defined In |
|------------|-----------|------|------------|
| Service Catalog | `dev.usp.services.catalog` | Standalone | [USP Spec, Section 4](../extension/specification.md#4-service-catalog) |
| Availability | `dev.usp.services.availability` | Standalone | [USP Spec, Section 5](../extension/specification.md#5-availability) |
| Bookings | `dev.usp.services.bookings` | Standalone | [USP Spec, Section 6](../extension/specification.md#6-bookings) |
| Paid Bookings | `dev.usp.services.paid_bookings` | ACP Extension | [ACP Binding, Section 5](specification.md#5-paid-bookings-via-acp-checkout) |
| Waitlist | `dev.usp.services.waitlist` | Extension | [USP Spec, Section 9](../extension/specification.md#9-waitlist-extension) |

**Standalone capabilities** are identical across UCP and ACP bindings. The same schemas, operations, and validation rules apply. The only differences are header conventions and response metadata envelope.

**Paid bookings** differ by binding: the UCP binding extends `dev.ucp.shopping.checkout`; the ACP binding uses ACP's extension mechanism to add a `booking` object to checkout sessions. The booking object schema is identical.

## Key Design Principles

1. **Mapping layer, not a rewrite**: This binding references the [USP Specification](../extension/specification.md) for all scheduling domain content. It does not redefine service schemas, availability models, booking lifecycles, or waitlist mechanics. Zero duplication.
2. **No independent infrastructure maintenance**: Discovery, transport bindings, identity linking, buyer consent, embedded UI, versioning, and namespace governance are defined in the USP Specification (inherited from UCP). ACP sellers implement these per the USP Specification where needed, rather than from a separate ACP-specific definition.
3. **ACP compatibility**: Sellers already implementing ACP gain scheduling capabilities via a well-defined bridge, reusing their existing checkout infrastructure, payment handlers, and webhook mechanisms for the commerce portions of the flow.
4. **Same scheduling domain**: The scheduling logic is commerce-protocol-independent. An agent interacting with a USP seller gets the same service catalog, availability, booking, and waitlist experience regardless of whether the seller uses UCP or ACP for payment.
5. **Atomic commerce**: For paid services, completing the ACP checkout atomically finalizes both payment and booking. No dangling bookings, no cross-protocol cleanup.

## License

This specification is released under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).
