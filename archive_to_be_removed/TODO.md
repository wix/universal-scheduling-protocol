# USP Specification — TODO

> **Last reviewed:** 2026-02-11 by protocol review
> **Spec version under review:** `2026-02-09`

---

## Review Summary

The USP specification is a well-structured companion to UCP with a clean separation of concerns. The three-tier availability funnel (Hint → Slot → Hold) is a genuinely novel contribution — it solves the n+1 query problem that plagues every scheduling aggregator. The availability hint concept is particularly strong for agentic use cases.

However, the specification has critical gaps that would block interoperable implementation. The security model is dangerously thin for a protocol handling PII and financial transactions. Several schemas are defined by example rather than by contract. Concurrency semantics, error handling, and transport bindings are either missing or hand-waved. These must be resolved before the spec can be considered implementable by independent parties.

The existing TODO items are accurate and well-triaged. The additions below reflect findings from a full-protocol review, organized by severity.

---

## Done

- [x] Add `availability_hint` to Service Schema for agent-assisted discovery
- [x] Add agent use cases table (10 scenarios)
- [x] Remove day-level granularity; simplify to hint → slot → hold
- [x] Redesign high-level architecture diagram (USP/UCP split)
- [x] Remove Credential Provider from architecture diagram
- [x] Remove unspecified intake form references

---

## P0 — Blocks Interoperable Implementation

### Security & Trust Model (Critical)

- [ ] **Authentication mechanism** — No specification of platform-to-business or business-to-platform auth/authorization. The spec MUST define at least one concrete mechanism (OAuth 2.0 client credentials is the obvious choice, consistent with how UCP likely works). Without this, no two independent implementations can securely communicate.
- [ ] **Data privacy and PII handling** — The `buyer` object carries email, phone, and name across protocol boundaries with zero guidance on data minimization, retention, consent, or GDPR/CCPA obligations. For an open protocol, this is a liability. At minimum: specify what PII is REQUIRED vs OPTIONAL per operation, and add a `data_retention` policy field to the business profile.
- [ ] **Webhook specification** — Events are listed but payload schema, delivery format (CloudEvents?), retry policy, and subscription/registration mechanism are entirely missing. This is a full sub-protocol that needs designing — not just a few bullet points.
- [ ] **Webhook signing** — "JWS using keys published in the business profile" is mentioned but key location (JWKS URI?), key format, JWS header requirements, and payload canonicalization are not specified. Without these details, webhook verification is unimplementable.

### Error Handling (Critical)

- [ ] **Error response schema** — No standard error format, HTTP status code mapping, or error code catalog. `slot_unavailable` is referenced in prose but never formally defined. Define a standard error envelope (e.g., `{error: {code, message, details[]}}`) and a registry of codes. Every operation should specify its possible error codes.
- [ ] **HTTP status codes** — No status codes are specified for any operation. What does `POST /bookings` return on success — `201 Created`? `200 OK`? What about `409 Conflict` for double-booking? `422` for validation errors? This is table-stakes for a REST specification.
- [ ] **Content type** — `application/json` is assumed but never stated. No `Accept` header negotiation. No charset requirements.

### Concurrency & Consistency (Critical)

- [ ] **Idempotency** — No idempotency keys for `create_booking`, hold operations, or `cancel`. Network retries can create duplicate bookings. Define an `Idempotency-Key` header requirement for all mutating operations.
- [ ] **Hold concurrency semantics** — What happens when two platforms attempt to hold the same slot simultaneously? First-writer-wins is the obvious answer, but the spec must say so explicitly and define the error response for the loser. Also: what about the race between hold expiration and `create_booking`? If the hold expires at T and `create_booking` arrives at T+50ms, does the booking succeed?
- [ ] **Optimistic concurrency on booking updates** — `PUT /bookings/{id}` has no ETag or version field. Two concurrent updates will silently clobber each other. Add a `version` or `updated_at` check.

### Versioning (Critical)

- [ ] **Version evolution strategy** — Date-based versions are fine, but the spec doesn't define: how breaking vs. non-breaking changes are signaled, whether multiple protocol versions can coexist on the same endpoint, or deprecation/sunset policy. Capability versions evolving independently from the protocol version adds combinatorial complexity that needs governance rules.

---

## P1 — Blocks Production-Quality Implementation

### Underspecified Schemas

- [ ] **Location schema** — `locations`, `slot.location`, and `booking.location` use `{id, name}` but a full schema (address lines, city, postal code, country, coordinates, instructions) is not defined. Platforms cannot render a map or provide directions without this.
- [ ] **Channel schema** — `virtual_provider` and `instructions` fields are listed but not typed or constrained. What are valid `virtual_provider` values? Is `instructions` plain text or structured?
- [ ] **Capacity/waitlist** — `capacity.waitlist` is mentioned but its type (boolean? integer? object?) and semantics (auto-enqueue? notification mechanism?) are not specified. Waitlist is a complex feature that deserves its own sub-section or should be deferred to an extension.
- [ ] **Message/error codes** — `messages` array has `{type, code, message, severity}` but no catalog of codes or severity levels. Define an enum for `type` and `severity`, and a registry for `code` values.
- [ ] **Pricing models** — `variable`, `per_person`, `hourly` are listed but derivation rules are not fully specified. How does a platform compute the price for a 90-minute `hourly` service? What does `variable` mean in the absence of slot-level pricing overrides?
- [ ] **Deposit schema** — `deposit.value` type (integer cents vs. percentage integer) is ambiguous. `refundable` is boolean but refund conditions are not linked to the cancellation policy. These must be reconciled.
- [ ] **Opening hours** — Appears in availability response but has no formal schema definition. What about holidays, temporary closures, special hours? This is a well-solved problem (schema.org/OpeningHoursSpecification) — reference or adapt it.
- [ ] **List Services filters** — Example shows `type` and `category_id` but no full filter schema. Can you filter by price range? Duration? Location? Resource? Without a defined filter contract, platforms can't build reliable search UIs.
- [ ] **Pagination** — Cursor format, semantics (opaque string? base64?), page size limits, and total count behavior are not specified. State: must cursors be used within a TTL? Are they stable across catalog changes?

### Behavioral Gaps

- [ ] **Manual confirmation timeout** — Duration of `pending` state and expiration behavior are not specified. If a business never confirms, the booking hangs forever. Define a REQUIRED `expires_at` for `pending` bookings and the terminal state on expiry.
- [ ] **Reschedule flow** — Whether a new hold is required for `new_slot_id` is not specified. If the reschedule targets a popular slot, the business could confirm and then find the slot was taken. The reschedule operation should be atomic or require a hold.
- [ ] **Cancellation refunds** — Refund timing and how it surfaces in the booking response are not specified. Is `payment.status` updated synchronously? Does the platform poll or receive a webhook?
- [ ] **Policy temporal references** — `free_cancellation_until: PT24H` — 24 hours before what? The slot start time? The booking creation time? This ambiguity will cause real disputes. Specify explicitly that these are relative to `slot.start`.
- [ ] **Resource mismatch** — Behavior when `resource_id` matches no available slots is undefined (empty result vs. error). Define: return empty `slots[]` with a `suggestions` field, or return `404`/`422`.
- [ ] **Slot pricing override** — Conditions for when slot-level pricing applies vs. service pricing are not specified. Is slot pricing always authoritative when present? What about `per_person` pricing at slot level?
- [ ] **`continue_url` callback/return** — When a booking enters `requires_action` with a `continue_url`, there's no callback or redirect mechanism for the platform to know when the user has completed the action. For agent flows, this is critical — the agent needs to resume. Define a `return_url` parameter on `create_booking` and/or a webhook for `requires_action` resolution.

### UCP Integration Gaps

- [ ] **Partial UCP failures** — No guidance on handling `submit_checkout` failure and its effect on USP booking state. If checkout fails, does the hold remain? Does the booking revert to `pending`? Does the platform need to cancel and re-create?
- [ ] **`usp_booking` metadata governance** — Schema is shown inline but not versioned or registered as a UCP extension. How does USP ensure UCP doesn't reject unknown metadata fields?
- [ ] **`payment_url` fallback** — Documented as fallback for non-UCP businesses but the flow for detecting payment completion (polling? redirect? webhook?) is not specified.
- [ ] **Shared `buyer` object** — "Identity linking capability" is mentioned in the comparison table but not defined in USP. Either define it, reference UCP's definition, or remove the claim.
- [ ] **Request correlation** — No request ID or correlation ID mechanism for tracing a booking through USP and UCP. When debugging a failed payment, operators need to correlate the USP `booking_id`, UCP `checkout_id`, and PSP transaction ID. Define a `X-Request-Id` or `X-Correlation-Id` header.

---

## P2 — Important for Adoption & Ecosystem

### Transport & Discovery

- [ ] **MCP transport binding** — Listed as a transport option in the profile but no endpoint spec, schema, operation mapping, or tool definitions are provided. Either specify the MCP binding fully or remove it from the profile example and mark it as future work.
- [ ] **A2A (Agent Card)** — Listed as a transport but not defined. Same treatment as MCP: specify or defer.
- [ ] **Platform profile schema** — `USP-Agent` header and `_meta.usp.profile` are referenced but the platform profile structure is not specified. What capabilities does a platform advertise? What fields are required?
- [ ] **Extensions mechanism** — The "extends" concept is mentioned with examples but has no schema, discovery, or API contract. This is fine as a forward declaration, but the spec should either define it minimally or explicitly mark it as "reserved for future specification."

### Protocol Design Concerns

- [ ] **`POST /services/list` breaks HTTP caching** — Using POST for a read operation is unconventional in REST. It prevents HTTP-level caching (CDNs, browser caches, proxy caches). Consider offering a GET alternative with query parameters for simple cases, or acknowledge the trade-off and recommend `Cache-Control` headers on responses. This matters especially for catalog data which the spec itself says should be cached.
- [ ] **Slot ID stability** — Slot IDs are described as "opaque" but examples use deterministic-looking IDs (`slot_20260315_0900`). The spec should clarify: are slot IDs stable across repeated `query` calls for the same time? Or are they transient and only valid for hold/booking within the same session? This affects caching and hold semantics.
- [ ] **Hold abuse prevention is incomplete** — "Max concurrent holds per buyer" is mentioned but buyer identity across platforms is not defined. An anonymous agent could create unlimited holds with synthetic buyer data. Consider: hold rate limiting by platform identity (not buyer), optional hold deposits for high-value slots, or a trust score mechanism.
- [ ] **Buyer object is too minimal** — Only `{first_name, last_name, email, phone_number}`. No locale, preferred language, accessibility requirements, or timezone. For an agentic protocol, the agent should be able to convey user preferences. At minimum add an optional `locale` and `metadata` map.
- [ ] **No generic metadata/custom fields on bookings** — Many verticals need custom data at booking time: restaurants need dietary restrictions, medical appointments need insurance info, salons need hair type. The spec mentions intake forms as future work, but an `extensions` or `metadata` map on the booking request would unblock vertical-specific needs immediately without a full extension system.
- [ ] **DST and timezone edge cases** — The spec handles timezones well at surface level but doesn't address DST transitions. What happens when a slot spans a DST change? Which offset is canonical? What about `start_date: "2026-03-08"` in `America/New_York` where the day is 23 hours long? These edge cases should be acknowledged with guidance.
- [ ] **iCalendar interoperability** — No mention of RFC 5545 (iCalendar). Many scheduling systems export `.ics` files and most calendar apps consume them. A confirmed booking should be expressible as an iCalendar event. Consider a `booking.ical_url` field or a mapping appendix.
- [ ] **No batch operations** — No batch availability query across multiple services, no batch booking (e.g., haircut + color as sequential appointments). This directly limits the "multi-service bundling" agent use case (#8) described in the availability hint section. At minimum, define the expected pattern (serial holds? atomic multi-booking?).

---

## P3 — Future Considerations

- [ ] Intake forms / custom fields capability (as an extension)
- [ ] Recurring bookings (weekly yoga class, monthly haircut)
- [ ] Multi-service / package bookings (atomic booking of sequential services)
- [ ] Loyalty and rewards integration
- [ ] Rating and review capability
- [ ] Overbooking policies (common in restaurants and airlines)
- [ ] Waitlist management as a standalone capability
- [ ] Capacity tiers (e.g., VIP vs. general seating for reservations)
- [ ] Service bundles / packages with combined pricing
- [ ] Calendar sync (iCalendar export, CalDAV integration)
- [ ] Structured availability data in hints (e.g., heatmap of open/busy days) — currently only natural language
- [ ] Multi-language support for service names, descriptions, and availability hints
- [ ] Agent identity and delegation model (agent acts on behalf of user with scoped permissions)

---

## Architectural Observations (Non-Actionable, For Discussion)

These are not bugs or gaps — they are design trade-offs worth discussing as the protocol evolves.

1. **The availability hint is the spec's strongest innovation.** The natural-language `summary` is a pragmatic bridge between structured APIs and LLM-powered agents. However, as the ecosystem matures, consider adding structured fields (e.g., a day-level boolean array of open/busy) alongside the prose summary, so non-LLM platforms can also benefit without parsing natural language.

2. **The UCP dependency is a double-edged sword.** Clean separation of concerns is good architecture. But requiring businesses to implement *two* protocol endpoints (USP + UCP) for paid services raises the adoption bar significantly. Consider whether USP should define a minimal built-in payment capability (e.g., `payment_url` + webhook) as a first-class alternative, not just a fallback — and reserve UCP integration for businesses that want the full commerce stack.

3. **The "server-selects" negotiation model is opaque.** The business fetches the platform's profile, computes the intersection, and responds with active capabilities. The platform has no visibility into *why* a capability was excluded. Consider a `negotiation_log` or `unsupported_capabilities` field in responses to aid debugging during integration.

4. **Webhook vs. polling is an unresolved tension.** The spec recommends webhooks for state changes but also mentions polling `GET /bookings/{id}`. For a production protocol, one should be primary and the other fallback. My recommendation: webhooks are primary, polling is the fallback for platforms that can't receive webhooks. But this needs to be stated, and the polling contract (expected latency of state transitions, recommended poll interval) needs to be specified.

5. **The spec is REST-first but claims transport agnosticism.** The operation reference table, URL patterns, HTTP methods, and examples are all REST. MCP and A2A are listed as transports but have zero specification. This is fine for v1 — be honest about it. Call REST the normative binding and MCP/A2A as future bindings, rather than listing them as equals in the profile schema.
