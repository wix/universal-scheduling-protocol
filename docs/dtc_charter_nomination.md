# [DTC Charter]: Time-Based Services (Scheduling)

## Problem Statement

Booking a time-based service (a haircut, a class, a table, a rental) looks simple to a consumer, but the underlying logic is a combinatorial problem: service catalogs with policy and pricing rules, real-time slot computation across staff and resources, TTL-based holds to prevent double-booking, post-booking lifecycle (reschedule, cancel, waitlist), and payment coordination that must stay atomic when money is involved.

Today's scheduling landscape is fragmented across standards that each solve part of the problem but none of the whole:

- **iCalendar** ([RFC 5545](https://www.rfc-editor.org/rfc/rfc5545)) and **CalDAV Scheduling** ([RFC 6638](https://www.rfc-editor.org/rfc/rfc6638)) handle calendar data sharing within organizations, not cross-organization agentic commerce.
- **schema.org/Service** models services for search indexing, not programmatic booking flows.
- **OpenActive Open Booking API** covers physical-activity bookings but not the broader range of appointment, group, reservation, and rental verticals, and lacks native payment integration with modern commerce protocols.

No single open standard unifies **service discovery**, **real-time availability with holds**, **booking lifecycle with webhooks and idempotency**, **payment coordination**, and **buyer identity/consent** in a way that is both machine-readable and designed for autonomous AI agent orchestration.

Current agentic scheduling experiences are nascent and rely on monolithic, bespoke integrations. These integrations are not scalable: every new AI surface and every new scheduling platform requires a custom integration. The result is an O(N x M) problem that blocks the shift toward conversational, end-to-end booking.

The **Universal Scheduling Protocol (USP)** addresses this gap as an open standard for discovering, checking availability of, and booking time-based services. In **UCP-Native Mode**, USP registers scheduling capabilities directly in `/.well-known/ucp` and composes with UCP's atomic checkout via the `dev.usp.services.paid_bookings` extension, giving platforms a single discovery endpoint and a single payment-plus-booking confirmation path.

Universal Commerce Protocol (UCP) for Time-Based Services aims to standardize the connection between AI platforms and scheduling providers, delivering compounding value to every participant:

- **For Consumers:** It transforms service booking into frictionless conversion. Consumers can discover services, view real-time availability, select a slot, and complete secure, end-to-end booking (including payment when required) directly within a single AI conversation, eliminating cross-site friction and drop-off.
- **For Businesses (e.g., salons, studios, clinics, venues):** It scales distribution without technical overhead. Instead of maintaining costly, bespoke integrations for every platform, businesses adopt a single open standard once to expose their service catalog, availability, and booking capabilities, while preserving proprietary pricing, policies, staff assignment, and direct customer ownership.
- **For Platforms (e.g., AI surfaces, agent wallets):** Rather than navigating unique business APIs for every scheduling provider, platforms leverage a unified UCP framework to orchestrate discovery, slot holds, checkout, and post-booking lifecycle across appointments, group sessions, reservations, and rentals.

## UCP Strategic Fit

UCP is the right foundation for time-based services because USP was designed from the start with a **UCP-Native deployment mode** where scheduling is not a parallel protocol silo but a first-class UCP extension.

**Single-endpoint discovery.** In UCP-Native Mode, businesses register USP capabilities (`dev.usp.services.catalog`, `dev.usp.services.availability`, `dev.usp.services.bookings`, and optionally `dev.usp.services.paid_bookings`) alongside existing UCP shopping capabilities in `/.well-known/ucp`. Agents discover commerce and scheduling from one profile, one negotiation flow, and one error model.

**Atomic payment plus booking.** Paid scheduling requires that a slot hold and payment confirmation happen as a single atomic operation to prevent double-booking and payment-without-booking failures. USP's `dev.usp.services.paid_bookings` capability extends `dev.ucp.shopping.checkout` using UCP's `allOf` schema composition, adding a `booking` object (service, slot, hold, resources, policies) to the checkout request and response. `create_checkout` + `complete_checkout` confirm both payment and booking in one flow.

**Production-hardened primitives the scheduling vertical inherits.** UCP already provides the cross-cutting infrastructure scheduling needs:

| Concern | Inherited from UCP in USP-Native Mode |
|---------|---------------------------------------|
| Discovery | `/.well-known/ucp` profile |
| Capability negotiation | UCP negotiation protocol |
| Identity linking | UCP identity linking (buyer account, loyalty) |
| Buyer consent | UCP consent mechanism |
| Payment execution | UCP `payment_handlers` (e.g., Stripe Shared Payment Tokens) |
| Idempotency, webhooks, errors, security | UCP infrastructure |

The Scheduling DTC can focus on **domain-specific capabilities** (service catalog schema, availability queries, slot holds, booking lifecycle, waitlist, vertical extensions) rather than reinventing commerce infrastructure.

**Write once, deploy everywhere.** UCP turns the O(N x M) integration problem into an O(1) problem for scheduling platforms. A provider that implements USP capabilities in their UCP profile is legible to every AI platform that speaks UCP.

**Cross-vertical network effects.** As UCP primitives evolve (identity linking, loyalty, payment handlers, checkout schema), scheduling partners inherit those improvements automatically. Conversely, scheduling-specific checkout extensions (the `booking` object on checkout) enrich UCP's composable capability model for other time-bound commerce verticals (lodging check-in windows, food pickup slots).

**Vertical-owned specs.** The Scheduling DTC will own the schema definitions for time-based service capabilities under the `dev.usp.services.*` namespace, including catalog, availability, bookings, paid bookings (as a checkout extension), and optional extensions such as waitlist and buyer calendar free/busy. Vendor-specific verticals (e.g., `com.wix.services.courses`) remain extensible via reverse-domain namespaces.

**Reference implementation.** The [Universal Scheduling Protocol specification](https://github.com/wix-private/universal-scheduling-protocol-spec) (draft `2026-02-21`) defines the complete domain core, UCP-Native Mode integration (Section 7), machine-readable artifacts (JSON Schemas, OpenAPI, OpenRPC), and transport bindings (REST, MCP, A2A, ESP) ready for DTC review and hardening within UCP governance.

## Use Case Roadmap

The Scheduling DTC will follow a phased rollout to ensure technical stability and partner readiness.

### Phase 1 (MVP): Core Scheduling plus Paid Checkout

- **Service Catalog capability** (`dev.usp.services.catalog`): discover services, pricing, duration, policies, and availability hints for AI reasoning
- **Availability capability** (`dev.usp.services.availability`): real-time slot queries, resource assignment, and TTL-based holds
- **Bookings capability** (`dev.usp.services.bookings`): create, confirm, get, reschedule, cancel; webhook events for lifecycle changes
- **Paid Bookings extension** (`dev.usp.services.paid_bookings`): atomic checkout via UCP `create_checkout` + `complete_checkout` with the `booking` extension object
- **Core verticals:** `appointment` (1:1 sessions), `group` (capacity-limited classes), `reservation` (shared resources), `rental` (exclusive use for a duration)
- **Identity linking** for returning buyers (name, contact, loyalty where applicable)
- **Payment execution** via UCP `payment_handlers` (Stripe Shared Payment Tokens and other registered handlers)

### Phase 2 (Expansion): Free Services, Post-Booking, and Discovery

- **Free services path** in UCP-Native Mode (catalog + availability + bookings without checkout; no `paid_bookings` capability required)
- **Waitlist extension** (`dev.usp.services.waitlist`): join, position tracking, auto-promotion on cancellation
- **Post-booking lifecycle:** reschedule with policy enforcement, cancellation with refund rules, no-show handling, iCalendar export of confirmed bookings
- **Discovery registry** (`dev.usp.discovery.registry`, optional): cross-business search for services and businesses
- **Buyer calendar free/busy extension:** pass buyer availability constraints so platforms surface only non-conflicting slots
- **Mixed cart support:** retail product line items alongside a scheduled service in a single UCP checkout session

### Phase 3 (Long-term): Vertical Depth and Agent-Native Experiences

- **Vertical-specific extensions** under vendor namespaces (e.g., multi-session courses, equipment add-ons, party-size rules for venues)
- **Embedded Scheduling Protocol (ESP):** in-app booking UI delegation for journeys that require human interaction (waivers, intake forms, complex modifiers)
- **Agent-to-Agent (A2A) and MCP bindings:** full scheduling orchestration via agent protocols without REST-only assumptions
- **Personalization:** booking history, rebook-the-usual, loyalty-informed availability, and voice-based scheduling
- **Cross-domain scheduling:** composable booking of services that span domains (e.g., book a class plus purchase required equipment in one checkout)

## Platforms

Initial set of platforms committing to consume UCP scheduling capabilities.

- **[Platform Name 1]** (e.g., Google surfaces)
- **[Platform Name 2]** (e.g., Link agent wallet / agentic commerce platform)
- **[Platform Name 3]**

## Businesses

Initial set of businesses ready to implement USP capabilities via UCP.

- **[Business Name 1]** (e.g., Wix Bookings merchants via UCP-Native USP implementation)
- **[Business Name 2]** (e.g., Square Appointments)
- **[Business Name 3]** (e.g., Mindbody, Fresha, Calendly, or other scheduling SaaS)

## Commitment

- [ ] By submitting this charter, the named platforms and businesses formally commit to a long-term collaboration focused on developing and actively promoting the industry-wide adoption of the primitives proposed by this Domain Tech Council (DTC).

---

## Submission notes
Here is a DTC charter nomination draft for **Time-Based Services (Scheduling)**, following the [DTC charter template](https://github.com/Universal-Commerce-Protocol/.github/blob/main/DOMAIN_TECH_COUNCIL_CHARTER.md) and the structure of the [Lodging](https://github.com/Universal-Commerce-Protocol/ucp/issues/543) and [Food Ordering](https://github.com/Universal-Commerce-Protocol/ucp/issues/518) submissions.

Per [GOVERNANCE.md](https://github.com/Universal-Commerce-Protocol/.github/blob/main/GOVERNANCE.md#governance), this should be filed as a new issue in the [UCP Issues tracker](https://github.com/Universal-Commerce-Protocol/ucp/issues). The **Platforms** and **Businesses** sections need at least **3 committing organizations** before submission; placeholders are marked where you should insert confirmed names.

**Suggested issue title:** `[DTC Charter]: Time-Based Services (Scheduling)`

**Before filing:**

1. Replace placeholder platform and business names with organizations that have formally agreed to participate (minimum 3 per [GOVERNANCE.md](https://github.com/Universal-Commerce-Protocol/.github/blob/main/GOVERNANCE.md#governance)).
2. Check the commitment box once all named parties have confirmed.
3. Optionally attach links to the USP specification, JSON Schemas, and any reference implementations (e.g., `linkusp` CLI) as supporting evidence.

**Governance path after submission:**

1. GC reviews and approves/rejects the charter.
2. GC opens nomination for DTC members per [TC_ELECTIONS.md](https://github.com/Universal-Commerce-Protocol/.github/blob/main/TC_ELECTIONS.md).
3. GC elects DTC members and updates governance documentation.

If you want, I can save this as a markdown file in the repo, tailor the Platforms/Businesses sections to specific partners you name, or open the GitHub issue directly.