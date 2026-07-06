# [DTC Charter]: Time-Based Services (Scheduling)

## Problem Statement

Booking a time-based service (a haircut, a fitness class, a court, a rental) looks simple to a consumer, but the underlying logic is a combinatorial problem: service catalogs with policy and pricing rules, real-time slot computation across staff and resources, TTL-based holds to prevent double-booking, post-booking lifecycle (reschedule, cancel, waitlist), and payment coordination that must stay atomic when money is involved.

Today's scheduling landscape is fragmented across standards that each solve part of the problem but none of the whole:

- **iCalendar** ([RFC 5545](https://www.rfc-editor.org/rfc/rfc5545)) and **CalDAV Scheduling** ([RFC 6638](https://www.rfc-editor.org/rfc/rfc6638)) handle calendar data sharing within organizations, not cross-organization agentic commerce.
- **schema.org/Service** models services for search indexing, not programmatic booking flows.
- **OpenActive Open Booking API** covers physical-activity bookings but not the broader range of appointment, group, reservation, and rental verticals, and lacks native payment integration with modern commerce protocols.

No single open standard unifies **service discovery**, **real-time availability with holds**, **booking lifecycle with webhooks and idempotency**, **payment coordination**, and **buyer identity/consent** in a way that is both machine-readable and designed for autonomous AI agent orchestration.

Current agentic scheduling experiences are nascent and rely on monolithic, bespoke integrations. These integrations are not scalable: every new AI surface and every new scheduling platform requires a custom integration. The result is an O(N x M) problem that blocks the shift toward conversational, end-to-end booking.

Standardizing time-based services under UCP delivers compounding value to every participant:

- **For Consumers:** It transforms service booking into frictionless conversion. Consumers can discover services, view real-time availability, select a slot, and complete secure, end-to-end booking (including payment when required) directly within a single AI conversation, eliminating cross-site friction and drop-off.
- **For Businesses (e.g., salons, studios, clinics, venues):** It scales distribution without technical overhead. Instead of maintaining costly, bespoke integrations for every platform, businesses adopt a single open standard once to expose their service catalog, availability, and booking capabilities, while preserving proprietary pricing, policies, staff assignment, and direct customer ownership.
- **For Platforms (e.g., AI surfaces, agent wallets):** Rather than navigating unique business APIs for every scheduling provider, platforms leverage a unified UCP framework to orchestrate discovery, slot holds, checkout, and post-booking lifecycle across appointments, group sessions, reservations, and rentals.

### Domain Scope

The Time-Based Services domain covers four core verticals: **appointments** (1:1 sessions such as salon, clinic, and professional services), **group sessions** (capacity-limited classes and events), **reservations** (shared resources such as courts, lanes, and tables), and **rentals** (exclusive use of equipment, rooms, or venues for a duration), with an extensible model for additional verticals.

This scope is complementary to, not overlapping with, adjacent DTCs: **Lodging** ([#543](https://github.com/Universal-Commerce-Protocol/ucp/issues/543)) covers overnight stays, and **Food Ordering** ([#518](https://github.com/Universal-Commerce-Protocol/ucp/issues/518)) covers menu, cart, and order fulfillment. What defines this domain is a primitive neither of those requires: **real-time slot computation with holds across staff and resource calendars**. Where domains meet (e.g., a restaurant table reservation ahead of a food order, or a class booked alongside a retail purchase), UCP's composable capability model lets one checkout span both — which is precisely the argument for chartering this domain inside UCP rather than beside it.

## UCP Strategic Fit

Scheduling is a natural UCP vertical because time-based services need everything UCP already provides — discovery, negotiation, identity, consent, payment, webhooks — plus one domain-specific layer: availability and booking semantics. A working draft of exactly that layer already exists as the [Universal Scheduling Protocol (USP)](https://github.com/kobym707/universal-scheduling-protocol), designed from the start with a **UCP-Native deployment mode** in which scheduling is not a parallel protocol silo but a first-class UCP extension.

**Single-endpoint discovery.** In UCP-Native Mode, businesses register scheduling capabilities (`dev.usp.services.catalog`, `dev.usp.services.availability`, `dev.usp.services.bookings`, and optionally `dev.usp.services.paid_bookings`) alongside existing UCP shopping capabilities in `/.well-known/ucp`. Agents discover commerce and scheduling from one profile, one negotiation flow, and one error model.

**Atomic payment plus booking.** Paid scheduling requires that a slot hold and payment confirmation happen as a single atomic operation to prevent double-booking and payment-without-booking failures. The `paid_bookings` capability extends `dev.ucp.shopping.checkout` using UCP's `allOf` schema composition, adding a `booking` object (service, slot, hold, resources, policies) to the checkout request and response. `create_checkout` + `complete_checkout` confirm both payment and booking in one flow — no new payment machinery, just one added object on an existing UCP operation.

**Production-hardened primitives the scheduling vertical inherits.** UCP already provides the cross-cutting infrastructure scheduling needs:

| Concern | Inherited from UCP in UCP-Native Mode |
|---------|---------------------------------------|
| Discovery | `/.well-known/ucp` profile |
| Capability negotiation | UCP negotiation protocol |
| Identity linking | UCP identity linking (buyer account, loyalty) |
| Buyer consent | UCP consent mechanism |
| Payment execution | UCP `payment_handlers` (e.g., Stripe Shared Payment Tokens) |
| Idempotency, webhooks, errors, security | UCP infrastructure |

The Scheduling DTC can focus on **domain-specific capabilities** (service catalog schema, availability queries, slot holds, booking lifecycle, waitlist, vertical extensions) rather than reinventing commerce infrastructure.

**Write once, deploy everywhere.** UCP turns the O(N x M) integration problem into an O(1) problem for scheduling providers. A provider that implements scheduling capabilities in their UCP profile is legible to every AI platform that speaks UCP.

**Cross-vertical network effects.** As UCP primitives evolve (identity linking, loyalty, payment handlers, checkout schema), scheduling partners inherit those improvements automatically. Conversely, the scheduling checkout extension (the `booking` object on checkout) enriches UCP's composable capability model for other time-bound commerce verticals (lodging check-in windows, food pickup slots).

**A concrete starting point, contributed to UCP governance.** The [USP specification](https://github.com/kobym707/universal-scheduling-protocol) (draft `2026-02-21`, Apache 2.0) defines the complete domain core, UCP-Native Mode integration, machine-readable artifacts (JSON Schemas, OpenAPI, OpenRPC), and transport bindings (REST, MCP, A2A), with a working agent-wallet reference integration already exercising the end-to-end paid-booking flow. The submitters offer this specification as a **starting-point contribution** to be reviewed, adapted, and hardened under UCP governance. The DTC retains full authority over the final capability namespaces, schema shapes, and roadmap priorities; vendor-specific verticals (e.g., `com.wix.services.courses`) remain extensible via reverse-domain namespaces, per UCP convention.

## Use Case Roadmap

The Scheduling DTC will follow a phased rollout to ensure technical stability and partner readiness.

### Phase 1 (MVP): Core Scheduling plus Paid Checkout

- **Service Catalog capability**: discover services, pricing, duration, policies, and availability hints for AI reasoning
- **Availability capability**: real-time slot queries, resource assignment, and TTL-based holds
- **Bookings capability**: create, confirm, get, reschedule, cancel; webhook events for lifecycle changes
- **Paid Bookings extension**: atomic checkout via UCP `create_checkout` + `complete_checkout` with the `booking` extension object
- **Core verticals:** `appointment` (1:1 sessions), `group` (capacity-limited classes), `reservation` (shared resources), `rental` (exclusive use for a duration)
- **Identity linking** for returning buyers (name, contact, loyalty where applicable)
- **Payment execution** via UCP `payment_handlers` (Stripe Shared Payment Tokens and other registered handlers)

### Phase 2 (Expansion): Free Services, Post-Booking, and Discovery

- **Free services path** (catalog + availability + bookings without checkout; no paid-bookings capability required)
- **Waitlist extension**: join, position tracking, auto-promotion on cancellation
- **Post-booking lifecycle:** reschedule with policy enforcement, cancellation with refund rules, no-show handling, iCalendar export of confirmed bookings
- **Discovery registry** (optional): cross-business search for services and businesses
- **Buyer calendar free/busy extension:** pass buyer availability constraints so platforms surface only non-conflicting slots
- **Mixed cart support:** retail product line items alongside a scheduled service in a single UCP checkout session

### Phase 3 (Long-term): Vertical Depth and Agent-Native Experiences

- **Vertical-specific extensions** under vendor namespaces (e.g., multi-session courses, equipment add-ons, party-size rules for venues)
- **Embedded booking UI delegation** for journeys that require human interaction (waivers, intake forms, complex modifiers)
- **Agent-to-Agent (A2A) and MCP bindings:** full scheduling orchestration via agent protocols without REST-only assumptions
- **Personalization:** booking history, rebook-the-usual, loyalty-informed availability, and voice-based scheduling
- **Cross-domain scheduling:** composable booking of services that span domains (e.g., book a class plus purchase required equipment in one checkout)

## Platforms

Initial set of platforms committing to consume UCP scheduling capabilities.

- **Google** (AI Mode, Gemini, and Search surfaces) *(to be confirmed)*
- **Stripe** (Link agentic wallet) *(to be confirmed)*
- **Microsoft** (Copilot) *(to be confirmed)*

## Businesses

Initial set of businesses ready to implement UCP scheduling capabilities.

- **Wix** (Wix Bookings — appointments, classes, courses, and rentals for millions of merchants; reference implementation)
- **Square** (Square Appointments) *(to be confirmed)*
- **Mindbody + ClassPass** (fitness and wellness) *(to be confirmed)*
- **Fresha** (beauty and wellness marketplace) *(to be confirmed)*

## Commitment

- [ ] By submitting this charter, the named platforms and businesses formally commit to a long-term collaboration focused on developing and actively promoting the industry-wide adoption of the primitives proposed by this Domain Tech Council (DTC).

---

## Submission notes (internal — delete everything from the `---` above before filing)

Per [GOVERNANCE.md](https://github.com/Universal-Commerce-Protocol/.github/blob/main/GOVERNANCE.md#governance), file this as a new issue in the [UCP Issues tracker](https://github.com/Universal-Commerce-Protocol/ucp/issues) titled `[DTC Charter]: Time-Based Services (Scheduling)`. A charter requires **3+ committing organizations** in total across Platforms and Businesses; every named organization must have formally agreed before filing, and the commitment box must be checked.

### Candidate rationale (ranked)

**Platforms** (consume scheduling capabilities):

1. **Google** — UCP steward; the named platform on both precedent charters (Lodging [#543](https://github.com/Universal-Commerce-Protocol/ucp/issues/543), Food Ordering [#518](https://github.com/Universal-Commerce-Protocol/ucp/issues/518)). Scheduling extends the AI Mode / Gemini booking journeys UCP already powers.
2. **Stripe (Link)** — UCP Tech Council member; the Link agentic wallet already exercises the USP paid-booking flow end to end via the reference agent integration, making it the most credible "committed" platform on the list.
3. **Microsoft (Copilot)** — UCP Tech Council member with consumer agent surfaces.
4. Alternates: **Perplexity** (aggressive agentic-shopping roadmap), **Amazon** (Rufus / Alexa+; Tech Council member), **Salesforce** (Agentforce; Tech Council member, B2B services angle).

**Businesses** (implement scheduling capabilities):

1. **Wix (Wix Bookings)** — submitter; spans all four core verticals across millions of SMBs and owns the reference implementation.
2. **Square (Square Appointments)** — already a named business on the Food Ordering charter, so UCP commitment exists organizationally; large SMB scheduling footprint.
3. **Mindbody + ClassPass** — category leader for fitness/wellness; anchors the `group` vertical.
4. **Fresha** — global beauty/wellness marketplace (100k+ partner venues); anchors the `appointment` vertical.
5. Alternates: **Booksy**, **Vagaro**, **Zenoti** (beauty/wellness SaaS); **OpenTable / SevenRooms / Tock** (anchor the `reservation` vertical, with clean adjacency to Food Ordering); **Squarespace (Acuity)** or **GoDaddy** (website builders with scheduling, same shape as Wix); **Zocdoc** (healthcare appointments — regulated, better as a Phase 2 recruit).

**Minimum viable slate:** Wix + Google + Stripe satisfies the 3-organization floor and spans business, AI surface, and payments. **Recommended slate:** add Square and one of Mindbody/Fresha — a multi-vendor business list is the single strongest counter to the perception that this charter is a one-company (Wix) protocol push.

### Governance path after submission

1. GC reviews and approves/rejects the charter.
2. GC opens nomination for DTC members per [TC_ELECTIONS.md](https://github.com/Universal-Commerce-Protocol/.github/blob/main/TC_ELECTIONS.md).
3. GC elects DTC members and updates governance documentation.
