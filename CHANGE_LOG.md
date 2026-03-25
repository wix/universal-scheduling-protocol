# Change Log

## 25/03/26 at 17:11:29 by [kobym707](mailto:kobym@wix.com)

- Adopted strict slot-per-resource model (§4.1, §5.3.1): a slot now represents a specific bookable combination of time window + assigned resources, eliminating the race condition and undefined behaviour caused by a separate `resource_id` selection at booking time.
- Added "One slot per resource combination" normative note to §4.1 (TimeSlot): when the same time window is available for multiple resources, the business MUST return a separate slot per option, each with its specific resource in the `resources` array.
- Expanded `resources` field description in §4.1 to make clear that each slot carries at most one resource of each type and that picking a slot is equivalent to picking both the time and the resource.
- Removed `resource_id` from the CreateBookingRequest field table (§5.3.1) — resource selection is now fully encoded in `slot_id`, making the field redundant.
- Updated all three `POST /bookings` request examples (§5.3.1) to remove `resource_id`, keeping the examples in sync with the new schema.
- Added introductory note to §5.3.1 explaining that resource selection happens at availability query time (via slot choice), not at booking time.

---

## 25/03/26 at 12:17:34 by [kobym707](mailto:kobym@wix.com)

- Added `> **JSON Schema:** [/$defs/TypeName](schemas/file.json)` blockquotes to every schema-describing and operation section in `specification.md` that was missing one: §3.12.1, §3.12.3, §3.12.4, §4.1, §4.2, §4.3.1, §4.3.2, §5.3.1–5.3.7, §7.4, §8.5.2, §8.5.5 — making it easy for implementors to jump directly to the machine-readable `$defs` entry for any section.
- Updated all 8 existing `> **JSON Schema:**` blockquotes from bare file links to specific `/$defs/TypeName` links (§3.3, §4 availability intro, §5.2, §5.5.2, §8.5.1, §10.1.1 signing keys, §11.1.1, §11.2.3), consistent with the new pattern.

---

## 25/03/26 at 12:08:27 by [kobym707](mailto:kobym@wix.com)

- Added `links[]` to the `Service` schema (§3.3, `catalog.json`, OpenAPI, OpenRPC): service-specific policy links (cancellation policy, waiver, ToS) belong at the service level so platforms can surface them during the booking flow before the buyer confirms, not after.
- Added `booking_url` to the `Booking` schema (§5.2, `booking.json`, OpenAPI, OpenRPC): stable permalink for the buyer to view and manage their booking, used in confirmation emails, calendar events, and buyer portals.
- Added `messages[]` to the `Booking` schema (§5.2, `booking.json`, OpenAPI, OpenRPC): soft informational messages from the business about booking state (e.g., manual confirmation pending), consistent with how `messages[]` is already documented on hold responses.
- Added `dispute` field and `Dispute` schema to the `Booking` object (§5.5.2, `booking.json`, OpenAPI, OpenRPC): formalizes the dispute lifecycle with structured `status`, `reason`, `opened_at`, and `resolved_at` fields; clarifies that opening a dispute does NOT change `payment.status`.
- Added `tax_amount` to `BookingPayment` (§8.5.1, `booking.json`, OpenAPI, OpenRPC) and clarified that `amount` is the pre-tax service fee: resolves ambiguity about whether pricing amounts are tax-inclusive.
- Added "Booking Expiry" behavioral rules to §5.2: business MUST transition to `canceled`, SHOULD send `booking.canceled` webhook, MUST keep expired booking retrievable via GET, and MUST release the slot.
- Added idempotency note to §5.3.1: `hold_id` serves as a natural idempotency key; second POST with same `hold_id` MUST return existing booking; no-hold flows SHOULD use `Idempotency-Key` header.
- Expanded §5.3.3 Update Booking with request field table and response description: documents the three mutable fields (`buyer`, `recipient`, `notes`) and partial-update semantics.
- Expanded §5.3.4 Confirm Booking with request field table, eligible status guidance, and response example.
- Expanded §5.3.5 Cancel Booking with request field table (`reason`, `canceled_by`), eligible statuses, slot-release requirement, and cancel/refund response example.
- Expanded §5.3.6 Reschedule Booking with eligible status guidance, booking-ID-preservation note, response description, and price-change handling for peak/off-peak rescheduling.
- Added webhook payload schema and example to §5.4.1 Booking Webhooks, mirroring the existing §5.4.2 Catalog Webhooks structure.
- Added single-service design note to §5 intro (Gap 4.14): USP bookings are single-service by design; multi-service coordination is handled by the platform issuing separate bookings.

---

## 24/03/26 at 23:03:02 by [kobym707](mailto:kobym@wix.com)

- Added non-transactional disclaimer to §4.1 (Gap 3.1): slots are advisory-only; platforms MUST NOT treat availability responses as booking commitments, and businesses MUST validate slot availability at booking creation time regardless of holds.
- Added `location_id` to §4.3.1 request field table (Gap 3.2): was already in OpenAPI/OpenRPC but absent from the normative prose; now synced across all artifacts.
- Added date range guidance to §4.3.1 (Gap 3.3): platforms SHOULD query at most 7 calendar days per request; businesses MAY reject wider ranges with HTTP 422 and error code `range_too_wide`.
- Added optional `messages` array to §4.3.1 query response (Gap 3.4): consistent with hold response; enables businesses to return soft warnings (e.g., holiday hours, reduced staffing) alongside slots.
- Added single-service design note to §4.3.1 (Gap 3.5): documents the deliberate single-service-per-query design choice and notes that a future multi-service availability extension is under consideration.
- Added §9.1.2 Pagination to the REST Binding section (Gap 3.6): defines shared cursor semantics (opaque cursors, 60s minimum TTL, ordering note, default page sizes) used by all paginated USP operations; added cross-reference in §4.3.1; noted the intentional `next_cursor` vs `cursor` distinction between the feed and all other endpoints in §3.1.
- Added `spots: 1` to §4.3.3 release response example (Gap 3.7): release response now matches hold response schema for consistency.
- Added "Concurrent Holds" subsection to §4.2 (Gap 3.8): normative MUST/MUST NOT rules for concurrent hold behavior by service type — `appointment` allows one active hold maximum, `group`/`reservation` allows multiple up to remaining capacity, `rental` treats resource overlap as unavailable.
- Added `opening_hours[]` field table to §4.3.1 response (Gap 3.9): defines `day_of_week` (lowercase day names), `opens` (HH:MM), `closes` (HH:MM), and clarifies the field reflects regular hours only; special closures are surfaced via absent slots. Fixed OpenRPC `usp_availability_query` result to include full item schema (was previously `"type": "array"` with no properties).
- Added optional `locale` (BCP 47) parameter to §4.3.1 (Gap 3.10): allows platforms to request locale-specific human-readable content; narrowed UCP's full context/signals suggestion to only the scheduling-relevant subset.
- Added `locale`, `cursor`, and `limit` parameters to `usp_availability_query` in `openrpc/usp-mcp.json` and `openapi/usp-rest.json` to keep all artifacts in sync.
- Expanded `Pagination` schema descriptions in both `usp-rest.json` and `usp-mcp.json`.
## 24/03/26 at 13:47:43 by [kobym707](mailto:kobym@wix.com)

- **Gap 2.10:** Added optional `tags` (array of strings) and `metadata` (freeform object) to Service schema, aligning with UCP. Enables freeform categorization and business-defined custom data.
- **Gap 2.11:** Fixed space-in-URL typo in feed example (`cursor=2026-03-10T08: 00: 00Z`). Changed feed cursor examples to opaque values (`crs_...`) since the spec says cursors are opaque. Removed `format: date-time` from feed cursor parameter in OpenAPI.
- **Gap 2.12:** Standardized feed pagination from `next_cursor` to `cursor` to match the `Pagination` component used by `/services/list`. Both endpoints now use `{cursor, has_more}`.
- **Gap 2.13:** Added §3.13 Catalog Conformance Requirements with 10 numbered MUST/SHOULD requirements for `dev.usp.services.catalog` implementations.
- **Gap 2.14:** Already addressed — formal filter table was added in the earlier catalog_search alignment commit.
- **Gap 2.15:** Added optional `categories` array (multi-taxonomy, `{value, taxonomy}` entries) to Service schema alongside existing `category`. If both present, `categories` is authoritative. Aligns with UCP.
- **Gap 2.16:** Added optional `handle` (URL-friendly slug) and `url` (canonical page) fields to Service schema. Aligns with UCP.
- **Gap 2.17:** Added `status` field to Service schema with values `active` (default), `suspended`, `archived`. Formally defines the `suspended` state referenced by `service.suspended` webhook events.
- **Gap 2.18:** Added formal webhook payload schema table for catalog change events, defining `event`, `service_id`, `subscription_id`, `timestamp`, and `data` fields with required/optional semantics.

---

## 24/03/26 at 12:12:11 by [kobym707](mailto:kobym@wix.com)

- Added optional `rating` object to the Service schema with `value` (required), `scale_min` (default 1), `scale_max` (required), and `count`. Matches UCP's rating schema exactly. Enables platforms and AI agents to display and compare service ratings without external lookups.
- Added `Rating` $def to `schemas/catalog.json` and `rating` field to `openapi/usp-rest.json` and `openrpc/usp-mcp.json`.

---

## 24/03/26 at 12:03:55 by [kobym707](mailto:kobym@wix.com)

- Added optional `provider` object to the Service schema (§3.3.3) with `name` (required), `url`, and `links` (array of typed links to policy pages). Aligns with UCP's `seller` object on product variants. Enables platforms to display business name, website, and policy links alongside services without a separate profile fetch — critical for multi-business search results, cached catalogs, and AI agent descriptions.
- Added `Provider` and `Link` $defs to `schemas/catalog.json`, and `provider` field to `openapi/usp-rest.json` and `openrpc/usp-mcp.json`.
- Link types follow UCP pattern: `privacy_policy`, `terms_of_service`, `refund_policy`, `cancellation_policy`, `faq`, with optional `title` for display text and graceful handling of unknown types.

---

## 24/03/26 at 09:40:22 by [kobym707](mailto:kobym@wix.com)

- Extended `description` field on the Service schema to accept either a plain string (backward compatible) or a structured `Description` object with `plain` (required), `markdown`, and `html` variants. Aligns with UCP's `Description` type which supports multi-format content. Platforms prefer the richest format they can safely render, falling back to `plain`.
- Added §3.3.2 Description Schema to `specification.md` documenting the structured format, backward compatibility rules, and HTML sanitization requirements.
- Added `Description` $def to `schemas/catalog.json` and updated `description` field in `openapi/usp-rest.json` and `openrpc/usp-mcp.json` with `oneOf` (string | object).

---

## 24/03/26 at 09:36:31 by [kobym707](mailto:kobym@wix.com)

- Added `media` array to the Service schema (§3.3.1), replacing `images`. Each media entry has `type` (format: `image`/`video`), `url`, `alt_text`, `role` (display: `hero`/`gallery`/`thumbnail`), and optional `width`/`height`. Aligns with UCP's typed media model. The previous `images` field (`{url, alt, type}`) is retained as a deprecated alias for backward compatibility.
- Separated media format type (`type`: image/video) from display role (`role`: hero/gallery/thumbnail) — the old `images.type` conflated both concepts.
- Renamed `alt` to `alt_text` for consistency with UCP and accessibility standards.
- Updated schema.org mapping to handle both image and video media types.
- Updated `schemas/catalog.json`, `openapi/usp-rest.json`, and `openrpc/usp-mcp.json`.

---

## 24/03/26 at 09:33:08 by [kobym707](mailto:kobym@wix.com)

- Added optional `price_range` (`{min, max}` in minor currency units) to the Pricing object in §3.8, `schemas/catalog.json`, `openapi/usp-rest.json`, and `openrpc/usp-mcp.json`. RECOMMENDED when pricing model is `variable`, `hourly`, or `per_person`, so platforms can display "from $50 – $150" without querying availability. Aligns with UCP's `price_range` on products. Closes the gap where USP services with variable pricing had no displayable price at catalog level.

---

## 24/03/26 at 09:30:00 by [kobym707](mailto:kobym@wix.com)

- Added `coordinates` field (`latitude`/`longitude`, WGS 84) to the `context` object, enabling proximity-based ranking and "near me" queries for scheduling services. Addresses the gap where USP had no mechanism for platforms to signal buyer geographic location beyond postal code.
- Extended `context` object to `POST /services/lookup` (previously only on `/services/list`), so both catalog request endpoints support buyer locale/intent signals for localization of returned content.
- Documented that the `context` object is shared across all catalog request payloads with the same field definitions, and that businesses MUST ignore unrecognized context fields without error for forward compatibility.

---

## 24/03/26 at 09:26:45 by [kobym707](mailto:kobym@wix.com)

- Extended `POST /services/list` filters to align with UCP `catalog_search`: added `categories` (array, OR logic) alongside existing `category_id`, and added `price` range filter (`min`/`max` in minor currency units). All filters combine with AND logic; within `categories`, values combine with OR logic.
- Added `context` object to `POST /services/list` request, aligning with UCP's context pattern. Carries buyer locale and intent signals (`address_country`, `address_region`, `postal_code`, `language`, `currency`, `intent`) that businesses use for relevance, localization, and personalization. Businesses MUST ignore unrecognized context fields without error.
- Updated §3.12.1 in `specification.md` with filter and context field tables, updated request examples, and documented precedence rules (`categories` over `category_id`, `context.currency` as denomination for price filters).

---

## 24/03/26 at 09:21:23 by [kobym707](mailto:kobym@wix.com)

- Added optional `query` free-text search parameter to `POST /services/list` in `specification.md` (§3.12.1), `openapi/usp-rest.json`, and `openrpc/usp-mcp.json` — aligns with UCP's `catalog_search` pattern. When present, business ranks results by relevance; when combined with filters, filters are hard constraints and query determines ranking within the filtered set.
- Defined graceful degradation: businesses that do not support search MUST ignore the `query` field (not error). Businesses that support it SHOULD advertise `"search": true` in their catalog capability entry.

---

## 24/03/26 at 08:55:39 by [kobym707](mailto:kobym@wix.com)

- Added `POST /services/lookup` batch endpoint (§3.12.4) to `specification.md`, `openapi/usp-rest.json`, and `openrpc/usp-mcp.json` — analogous to UCP's `catalog_lookup`. Accepts an array of service IDs and returns matching services with partial-success semantics (unresolved IDs reported via `messages[]` with `code: service_not_found`). Closes the gap where USP only offered single-service retrieval via `GET /services/{service_id}`.
- Defined batch size limits (MUST accept at least 50), deduplication rules (silent dedup), and ordering contract (unordered response) for the new lookup endpoint.
- Added `Lookup Services` to the §12 Operation Reference table.

---

## 24/03/26 at 08:48:29 by [kobym707](mailto:kobym@wix.com)

- Added optional `messages[]` array to all three catalog endpoint responses (`/services/list`, `/services/{service_id}`, `/services/feed`) in both `openapi/usp-rest.json` and `openrpc/usp-mcp.json`, aligning with the UCP message model where `catalog_lookup` and `catalog_search` responses carry structured messages for partial-success signalling, filter feedback, and service-level warnings.
- Updated the `Message` schema in both OpenAPI and MCP specs to match UCP: added `content_type` field (`plain`/`markdown`), added `unrecoverable` severity level, changed `path` field from JSON Pointer to RFC 9535 JSONPath, made `type` and `content` required fields, and expanded severity descriptions to match UCP's semantics.
- Added a formal Message field reference table and severity level table to §9.4 in `specification.md`, so the message contract is fully documented in the spec prose (previously only in the OpenAPI/MCP schemas).
- Updated §9.1 error model description to clarify that `messages[]` is available on all USP response envelopes including catalog responses, not only state-modifying operations.
- Added `messages[]` notes to §3.1 (feed), §3.12.1 (list), and §3.12.3 (get service) endpoint descriptions.

---

## 21/03/26 at 14:05:04 by [kobym707](mailto:kobym@wix.com)

- Added §11.2 Buyer Calendar Free/Busy Extension to `specification.md` — a MAY-level, platform-scoped extension that enables platforms to access a buyer's calendar for opaque free/busy blocks only, then cross-reference with business availability to suggest mutually free times. Addresses issue #18 requesting privacy-preserving calendar access for scheduling agents.
- Introduced the `dev.usp.platform.*` capability namespace in §2.5 to distinguish platform-scoped capabilities (implemented entirely by the platform) from business-facing `dev.usp.services.*` capabilities. Needed because the calendar free/busy extension is the first capability that does not require any business-side implementation.
- Created `schemas/calendar_freebusy.json` defining `BusyBlock` (opaque `{start, end}` with `additionalProperties: false` to enforce no event detail leakage), `BuyerFreeBusy` (aggregated buyer availability), and `CalendarProviderConfig` (informative provider reference).
- Added `BusyBlock` and `BuyerFreeBusy` component schemas to `openapi/usp-rest.json` for schema registry completeness, even though no new endpoints are introduced (the feature is platform-internal).
- Added `BusyBlock` and `BuyerFreeBusy` to the §1.2 Terminology table so the new types are discoverable alongside existing protocol terms.
- Updated §11 Extensions intro to note that extensions can be platform-scoped, not just business-scoped.
- Added informative references to §14.2 for RFC 4791 (CalDAV), Google Calendar FreeBusy API, and Microsoft Graph getSchedule API.

---

## 21/03/26 at 16:27:55 by [kobym707](mailto:kobym@wix.com)

- Expanded §11.2.2 Proactive Agent Use Cases with 4 business-initiated reactive scenarios (#8–#11) that compose calendar free/busy with USP webhooks and the waitlist extension: calendar-aware waitlist auto-accept/decline, proactive rebooking on business cancellation, smart conflict detection on business-initiated reschedule, and waitlist priority pre-fetching. These demonstrate the extension's value beyond buyer-initiated flows.
- Reorganized the use cases table into two groups — "Buyer-initiated scenarios" and "Business-initiated scenarios (reactive via webhooks)" — with cross-references to §5.4 (Webhooks) and §11.1 (Waitlist Extension).

---

## 21/03/26 at 14:12:18 by [kobym707](mailto:kobym@wix.com)

- Added §11.2.2 Proactive Agent Use Cases to the calendar free/busy extension, describing 7 buyer-initiated agentic scenarios (conflict-aware slot presentation, multi-service coordination, smart rescheduling, travel-time-aware scheduling, availability-first discovery, recurring pattern matching, group scheduling) to strengthen the motivation for the extension and illustrate its value for AI-driven scheduling agents.
- Renumbered §11.2.3–11.2.8 to §11.2.4–11.2.9 to accommodate the new sub-section.

---

## 19/03/26 at 18:03:50 by [Ran Yahalom](mailto:ranya@wix.com)

- Expanded `USPError` definition in `openrpc/usp-mcp.json` with a fully-typed `data` schema: `code` (string enum of all 22 §9.4 error codes including the 5 new profile error codes), `messages` (array of `$ref: Message`), and `severity` (enum). Previously the `data` field was an unstructured description string, making the error contract unvalidatable.
- Added `Forbidden` (403) response component to `openapi/usp-rest.json` for the `profile_not_trusted` error code. This was the only §9.4 protocol error without a corresponding OpenAPI response component.
- Added `403` and `424` error responses to all business-facing endpoints in `openapi/usp-rest.json`. Profile negotiation errors are protocol-level and can occur on any Standalone Mode call, but previously only `POST /services/list` referenced `FailedDependency` (424).
- Fixed previous CHANGE_LOG entry: corrected "four profile-related protocol error codes" to "five" — `profile_unreachable` was missing from the list.

---

## 18/03/26 at 23:26:59 by [Ran Yahalom](mailto:ranya@wix.com)

- Added `schemas/usp.json` — formal JSON Schema (Draft 2020-12) for the `usp`
  metadata object used in business profiles, platform profiles, and API
  responses. Defines `$defs/base`, `business_schema` (services, capabilities,
  checkout_systems, business identity, supported_versions), `platform_schema` (
  capabilities + optional service preferences), and `response_schema` (version +
  active capabilities), along with reusable `ServiceBinding`, `CapabilityEntry`,
  and `BusinessInfo` sub-types. Needed to give implementors a
  machine-validatable schema for the core protocol metadata object.
- Added `schemas/profile.json` — formal JSON Schema for the two USP profile
  document types: `$defs/BusinessProfile` (the document at `/.well-known/usp`)
  and `$defs/PlatformProfile` (the document advertised via `USP-Agent`). Defines
  `$defs/SigningKey` (JWK structure for webhook verification keys) with all
  required EC and RSA fields. Needed because there was no machine-validatable
  schema for either profile document, making automated validation impossible.
- Expanded `specification.md` §8.2 with four subsections: §8.2.1 Business
  Profile Fields (field-level tables for top-level profile, `usp` object,
  ServiceBinding, CapabilityEntry, and namespace governance), §8.2.2 Profile
  Hosting Requirements (HTTPS, no-redirect, Cache-Control, Content-Type rules
  and implementation obligations for both sides), §8.2.3 Platform Profile (full
  specification of the platform profile document structure, example, field
  table, hosting requirements, and business-side fetch/cache obligations), and
  §8.2.4 Backward Compatibility (the `supported_versions` map pattern with
  90-day guidance). Needed because the profile was documented only via a single
  example with no formal field definitions.
- Expanded `specification.md` §8.3 Capability Negotiation with a six-step
  negotiation algorithm covering platform profile fetch timing, caching,
  intersection computation, extension pruning, response envelope, and the
  empty-intersection error case. Needed to replace the bare four-bullet
  description with a complete normative algorithm.
- Added five profile-related protocol error codes to `specification.md` §9.4
  error table: `invalid_profile_url`, `profile_unreachable`, `profile_malformed`,
  `capabilities_incompatible`, and `profile_not_trusted`, with REST status codes
  and JSON-RPC codes. Needed to make profile failure modes first-class,
  consistent, and interoperable.
- Expanded `specification.md` §10.1.1 signing keys documentation with a full
  `SigningKey` field table (kid, kty, crv, x, y, n, e, use, alg) and
  cross-references to `schemas/profile.json`. Needed because `signing_keys`
  field-level constraints were undocumented.
- Updated `openapi/usp-rest.json`: marked `USP-Agent` parameter as
  `required: true`; added `SigningKey`, `ServiceBinding`, `CapabilityEntry`,
  `BusinessProfile`, and `PlatformProfile` component schemas; added
  `GET /.well-known/usp` path with full response schema and example. Needed to
  make the OpenAPI spec self-describing for both the profile endpoint and the
  header the spec already referenced.
- Updated `openrpc/usp-mcp.json`: tightened `_meta` param schema across all 19
  methods — `_meta.usp.profile` is now declared with `format: uri`, descriptive
  text clarifying it is required in Standalone Mode, and `required: ["profile"]`
  within the `usp` sub-object. Needed to align the MCP binding with the REST
  binding's capability negotiation semantics.

---

## 16/03/26 at 12:20:45 by [Ran Yahalom](mailto:ranya@wix.com)

- Implemented `USPRestClient.search_registry_for_services` method body per the
  `/registry/search_services` OpenAPI schema — performs a POST to the USP
  registry, builds the request from typed parameters (query, location,
  verticals, categories, price\_range, duration\_range, pagination), and parses
  the response into `ServiceSearchResult` models. Handles both camelCase and
  snake\_case response field names (e.g. `results` vs `services`,
  `pagingMetadata` vs `pagination`) so the client works against both the live
  API and schema-compliant implementations.
- Added four new Pydantic models to `shopping_agent/subagents/usp/models.py`:
  `ServiceSearchResultPrice`, `ServiceSearchResultLocation`,
  `ServiceSearchResult`, and `ServiceSearchPagination` — all configured with
  `alias_generator=to_camel` and `populate_by_name=True` for bidirectional
  camelCase/snake\_case support, matching the `ServiceSearchResult` and
  `Pagination` schemas in the OpenAPI spec.

---

## 01/03/26 at 15:28:19 by [Ran Yahalom](mailto:ranya@wix.com)

- **Scoped `post_payment_return_request` to the `redirect` checkout path:**
  Added a note in §8.5.5 and in all schema descriptions clarifying that the
  field applies only when `checkout_systems: redirect` is in use, and is not
  applicable to the `acp` or `embedded` checkout paths.
- **Made cancellation/abandonment a first-class outcome
  in `post_payment_return_request`:** Expanded all prose, table descriptions,
  and schema `description` strings to explicitly state the business MUST honor
  the return redirect in both terminal outcomes — payment completed *and*
  payment cancelled/abandoned — not only on success.
- **Added SHOULD recommendation for including `post_payment_return_request`:**
  Even though the field is optional, updated §8.5.5, the §5.3.1 field table, and
  all schema descriptions to state that the platform SHOULD always include it on
  the redirect path, because without it the platform has no way to predict or
  control where the buyer lands after payment or cancellation.

---

## 01/03/26 at 15:24:37 by [Ran Yahalom](mailto:ranya@wix.com)

- **Added `post_payment_return_request` to `POST /bookings` as a first-class
  spec field with MUST-level compliance language:** Resolves the missing
  return-redirect mechanism in the redirect-based payment flow. The new field
  lets the platform supply a return URL (with opaque correlation params) at
  booking creation time — exactly when a server-side checkout system (e.g. Wix
  headless checkout) needs it — rather than after the buyer reaches the payment
  page.
- **Introduced `PostPaymentReturnRequest` schema across all spec
  artefacts (`specification.md`, `openapi/usp-rest.json`,`openrpc/usp-mcp.json`,
  `schemas/scheduling.json`):** Defines `url` (required, URI) and `params` (
  optional, string key-value map) with descriptions that make clear the business
  must append `params` verbatim as query parameters on the GET redirect, and
  that keys/values are opaque platform-controlled correlation state.
- **Expanded §8.5.5 from "Action Continue URL" to "Redirect Flow and
  Post-Payment Return":** Added a mermaid sequence diagram of the full redirect
  round-trip, MUST language, and the analogy to OAuth 2.0's `redirect_uri` +
  `state` pattern.

---

## 26/02/26 at 10:27:59 by [kobym707](mailto:kobym@wix.com)

- **Renamed `schemas/scheduling.json` to `schemas/booking.json`:** Renamed the
  file and updated the schema identity (`$id`, `title`) to "USP Booking" to
  better reflect that the schema defines the booking lifecycle (Booking, Buyer,
  BookingPayment, etc.), not the broader scheduling domain. Updated all
  references in specification.md and README.md.

---

## 25/02/26 at 17:23:00 by [Ran Yahalom](mailto:ranya@wix.com)

- **Updated `openrpc/usp-mcp.json` to match the current OpenAPI and
  specification:** Expanded the sparse `Booking` schema to include all
  properties from the OpenAPI spec (`resources`, `location`, `payment`,
  `actions`, `notes`, `cancellation`, `created_at`, `updated_at`, `expires_at`)
  with proper types, enums, and descriptions. Added `BookingPayment`,
  `PaymentContext`, and `Action` component schemas matching the OpenAPI
  definitions. Updated `Message` schema to include `severity` enum, `path`
  field, and description. The OpenRPC now has full parity with the OpenAPI for
  all domain schemas (Booking, BookingPayment, PaymentContext, Action, Message).

---

## 25/02/26 at 17:16:27 by [Ran Yahalom](mailto:ranya@wix.com)

- **Updated `openapi/usp-rest.json` to match the actions[] changes:** Added
  `Action` schema to OpenAPI components. Removed `payment_context`, `messages`,
  and `continue_url` from the Booking schema and replaced with `actions` array
  referencing the new Action schema. Removed `payment_url` from BookingPayment.
  Removed `expires_at` from PaymentContext required fields and properties. Added
  description to Message schema clarifying its dual use (response-level and
  action-level).

---

## 25/02/26 at 16:11:33 by [Ran Yahalom](mailto:ranya@wix.com)

- **Introduced `actions[]` array on the booking object:** Replaced the flat
  `payment_context`, `continue_url`, and `messages` fields on the booking with
  an ordered `actions` array. Each action has `type`, `status`, `continue_url`,
  `expires_at`, and an optional `message`. Payment actions carry a nested
  `payment_context`. This makes the spec extensible for future non-payment
  action types (e.g., waivers, intake forms) while cleaning up the `payment_url`
  redundancy.
- **Established the status-actions invariant:**
  `booking.status: requires_action` is now structurally tied to `actions[]` —
  the booking MUST have this status if and only if at least one action has
  `status: pending`. When the last pending action completes, the business MUST
  transition the booking out of `requires_action`.
- **Made actions mode-agnostic for non-payment actions:** In UCP-Native Mode,
  `actions[]` never contains `payment`-type actions (payment is handled by UCP
  checkout), but non-payment actions may appear on the booking inside the
  `create_checkout` response. `complete_checkout` may be rejected if non-payment
  actions are still pending.
- **Added action ordering rationale:** Non-payment actions SHOULD precede
  payment actions so that the buyer can review requirements (e.g., read a
  liability waiver) and opt out before committing financially, avoiding
  unnecessary refunds.
- **Removed `payment_url` from BookingPayment:** Absorbed into the payment
  action's `continue_url` field.
- **Removed `expires_at` from PaymentContext:** Moved to the action-level
  `expires_at` field.
- **Removed `booking.messages[]`:** The only concrete usage (`payment_required`)
  now lives on `action.message`. Response-level `messages[]` remains for
  business outcome errors/warnings. Removed `info` from response-level message
  types.
- **Added `actions_pending` error code:** For when `confirm-payment` or
  `complete_checkout` is called while non-payment actions are still pending.
- **Updated `schemas/scheduling.json`:** Added `Action` definition to `$defs`
  with `type`, `status`, `continue_url`, `expires_at`, `message`, and
  `payment_context`. Removed `payment_context`, `messages`, and `continue_url`
  from Booking properties. Added `actions` array. Removed `payment_url` from
  BookingPayment. Removed `expires_at` from PaymentContext.
- **Updated all affected sections:** Glossary (1.2), operational modes (2.2.1),
  business responsibilities (2.1.2), architecture diagram text (2.3), booking
  status lifecycle (5.1), booking schema (5.2), create booking example (5.3.1),
  confirm-payment (5.3.7), UCP checkout flow (7.5), standalone mode (8), payment
  integration (8.5.1–8.5.7), checkout_systems (8.2), end-to-end flows (8.6),
  REST error model (9.1), and error code mapping (9.4).

---

## 25/02/26 at 12:51:33 by [Ran Yahalom](mailto:ranya@wix.com)

- **Promoted Discovery Registry to standalone Section 6:** Extracted Section
  7.5 (Discovery Registry) from Standalone Mode and promoted it to a top-level
  section (new Section 6) placed before the deployment modes. This reflects that
  the Discovery Registry is deployment-mode-independent and can index both
  Standalone and UCP-Native businesses. Incurred changes:
    - **Generalized Discovery Registry for both deployment modes:** Replaced
      `usp_profile_url` with `profile_url`, added a `deployment_mode` field (
      `standalone` or `ucp_native`) to registration and search schemas, and
      updated validation rules to support both `/.well-known/usp` and
      `/.well-known/ucp` profiles.
    - **Renumbered Sections 6-13 → 7-14:** Cascading renumber due to the new
      Section 6 insertion. UCP-Native Mode is now Section 7, Standalone Mode is
      Section 8, Transport Bindings is Section 9, Security is Section 10,
      Extensions is Section 11, Operation Reference is Section 12, IANA
      Considerations is Section 13, References is Section 14.
    - **Updated all cross-references, ToC, implementation stages, reading path
      diagram, and reading path tables** to reflect the new section numbering
      and the mode-independent Discovery Registry.

---

## 23/02/26 at 21:30:07 by [kobym707](mailto:kobym@wix.com)

- **Added Section 2.1.5 "Implementor Note: Expected Deployment Topology":**
  Clarifies that business-side USP is almost always implemented by SaaS
  platforms (Wix, Square, Mindbody) on behalf of their merchants, not by
  individual businesses. This sets reader expectations for why features like the
  catalog feed, subscriptions, and hold abuse prevention are scoped for
  professional platform teams, and preempts the "too complex for a small
  business" objection.

---

## 23/02/26 at 16:26:54 by [kobym707](mailto:kobym@wix.com)

- **Simplified Section 2.6 (Multi-Location Businesses):** Collapsed two
  sub-sections (2.6.1 Per-Location Profiles and 2.6.2 Parent-Entity Profile)
  into a single unified section. The per-location model was just standard
  single-location USP and didn't need its own sub-section; it's now a one-line
  note. The section now focuses on the only case that introduces protocol
  surface: a single endpoint serving multiple locations via the `locations[]`
  profile field and `location_id` filters.

---

## 23/02/26 at 16:21:59 by [kobym707](mailto:kobym@wix.com)

- **Fixed broken Mermaid diagram in Section 2.3 (High-Level Architecture):** The
  `graph TD` diagram used invalid single-dash edge syntax (` - "label" -->`)
  which caused a parse error on GitHub. Replaced with valid double-dash syntax (
  `-- "label" -->`) and switched `\n` to `<br/>` for multi-line edge labels.

---

## 22/02/26 at 15:36:29 by [kobym707](mailto:kobym@wix.com)

- **Made holds optional via feature flag on the availability capability:**
  Introduced a `holds` boolean feature flag on `dev.usp.services.availability`
  to explicitly declare whether a business supports the Hold Slot and Release
  Slot operations, because many businesses (especially small or low-contention
  ones) can operate safely without the hold mechanism, and forcing it on all
  implementers raised the integration bar unnecessarily.
- **Updated Section 4 (Availability) with feature flag table and discovery
  guidance:** Added the flag definition, profile declaration example, and
  clarified that when `holds` is absent or `false`, the booking flow proceeds
  directly from slot query to booking creation.
- **Gated Sections 4.2, 4.3.2, and 4.3.3 behind the holds flag:** Added callout
  blocks to the Hold entity, Hold Slot, and Release Slot operation sections
  noting they require `"holds": true`, preventing platforms from calling
  endpoints the business does not support.
- **Made `hold_id` explicitly optional in Create Booking (5.3.1) and
  Reschedule (5.3.6):** Added field-level tables with `hold_id` marked as
  optional, added a "without hold" request example, and updated the prose to
  describe both hold and no-hold flows.
- **Updated the caching strategy funnel (4.4):** Marked the Commit tier as
  optional and updated the Mermaid diagram to show a conditional branch for hold
  support.
- **Updated all end-to-end flow diagrams (6.7 and 7.7):** Changed Mermaid
  sequence diagrams to use `opt Business supports holds` blocks instead of
  showing holds as mandatory steps.
- **Updated A2A booking flow (8.3.2):** Made the hold step conditional and noted
  `hold_id` as optional in the booking creation step.
- **Updated profile examples (6.2, 7.2) to include `"holds": true`:**
  Demonstrates how businesses declare hold support in both UCP-Native and
  Standalone profiles.
- **Updated OpenAPI schema:** Added descriptions to hold/release endpoints
  noting the feature flag requirement, made `hold_id` optional in the reschedule
  request body, and updated `hold_id` descriptions in create booking.
- **Updated OpenRPC schema:** Added feature flag descriptions to hold/release
  methods and made `hold_id` optional (not required) in the reschedule method.
- **Updated paid_bookings.json schema:** Clarified `hold_id` description to note
  it depends on holds capability support.
- **Updated Operation Reference (11) and MCP/A2A mapping tables:** Annotated
  hold/release operations with `(holds: true)` to signal the feature flag
  requirement.
- **Updated Hold Abuse Prevention (9.1.2):** Scoped the section to apply only
  when holds are supported.

---

## 22/02/26 at 14:09:11 by [kobym707](mailto:kobym@wix.com)

- **Promoted Business ID and Localization to peer-level sections:** Extracted
  former 3.3.1 (Business ID) and 3.3.2 (Localization) from under the Service
  Schema section into their own top-level sections (3.4 and 3.5), consistent
  with how other complex Service fields (Duration, Pricing, Policies, etc.) are
  structured. Renumbered sections 3.4-3.10 to 3.6-3.12 and updated all
  cross-references throughout the spec.

---

## 22/02/26 at 13:54:36 by [kobym707](mailto:kobym@wix.com)

- **Moved extended verticals to informative Appendix A:** Relocated the five
  candidate verticals (`event`, `course`, `healthcare`, `home_service`, `tour`)
  from Section 1.3.2 to a new non-normative Appendix A, following RFC
  conventions for separating forward-looking content from normative spec. Added
  promotion criteria (A.2) requiring two independent implementations before a
  vertical can become core.
- **Renumbered Custom Verticals to Section 1.3.2:** Former Section 1.3.3 is now
  1.3.2 with a forward reference to Appendix A for candidate verticals.
- **Opened the `type` field enum in JSON schemas:** Removed the closed enum
  constraint on `service.type` in `usp-rest.json` and `paid_bookings.json` so
  that vendor-defined custom verticals using reverse-domain notation are not
  rejected by schema validation, aligning the schemas with what Section 1.3
  already permits.

---

## 22/02/26 at 12:18:07 by [kobym707](mailto:kobym@wix.com)

- **Added `business_id` to Service schema:** Every service object now carries
  the identifier of its owning business, making services self-describing for
  cross-business semantic search, cached catalog aggregation, and agent-to-agent
  hand-off. The composite key `(business_id, id)` is the globally unique
  identifier. Updated `catalog.json`, `usp-rest.json`, `usp-mcp.json`, and all
  service examples in `specification.md`.
- **Added localization (i18n) support:** Introduced the `localized` field on
  Service with per-locale overrides for `name`, `description`, `category_name`,
  and `channel_instructions` using IETF BCP 47 language tags. Enables businesses
  serving multilingual audiences to provide translations in a single cacheable
  response. Added `LocalizedFields` type to `catalog.json` and `usp-rest.json`.
- **Added undetermined duration option:** Services with no meaningful duration (
  consultations, custom quotes) can now set `duration.undetermined: true`
  instead of being forced to provide a fixed or range value. Added mutual
  exclusivity constraint with `fixed`/`range` and a validation rule preventing
  `hourly` pricing with undetermined duration.

---

## 21/02/26 at 11:42:09 by [Ran Yahalom](mailto:ranya@wix.com)

- **Extended USP Booking Form Profile with slot selection:** Added D0 derivation
  rules (slot picker, date picker), new inputs (`slots[]`, `flow_mode`), A2UI
  mappings for slot/date pickers, `usp_select_date` action, and D3/D4/D5
  fallbacks when slot not yet selected, enabling unified forms where slot
  selection is part of the form (pre-fetched or date-first flow)
- **Bumped profile version to 1.1**

---

## 21/02/26 at 10:47:37 by [Ran Yahalom](mailto:ranya@wix.com)

- **Added USP Booking Form Profile:** New separate spec (
  `docs/usp-booking-form-profile.md`) defining field derivation rules and A2UI
  component mapping for AI agent platforms building booking forms, so platforms
  know which form fields to show based on service/slot context and how to render
  them via A2UI
- **Added design doc:**
  `docs/plans/2026-02-21-usp-booking-form-profile-design.md` capturing the
  approved design from brainstorming
- **Updated README:** Added USP Booking Form Profile to the Specification
  documents table with link to the profile spec

---

## 21/02/26 at 10:12:28 by [Ran Yahalom](mailto:ranya@wix.com)

- Updated AGENTS.md entry format to include a mailto link for the author's git
  email, so each change log entry attributes the author with a clickable email
  link for traceability and easy contact

---

## 21/02/26 at 10:05:27 by Ran Yahalom

- **Fixed wrong cross-section links in specification.md:** Corrected Section
  1.3 (Vertical) link from `#9-service-verticals` to `#13-service-verticals`;
  Section 4.4 (Caching Strategy) from `#34-caching-strategy` to
  `#44-caching-strategy`; RFC 6749 (OAuth) from non-existent Section 9.6 to
  Section 9.2.3 Authentication and Authorization (
  `#923-authentication-and-authorization`); RFC 9421 (Webhooks) from Section 9.3
  to Section 9.1.1 Webhook Security (`#911-webhook-security`); Section 5.1 (
  Booking Status) from `#31-booking-status-lifecycle` to
  `#51-booking-status-lifecycle`
- **Fixed TOC:** Section 1.5 link text and anchor from "Deployment Modes and
  Implementation Guide" / `#15-deployment-modes-and-implementation-guide` to "
  Deployment Modes" / `#15-deployment-modes` to match actual heading
- **Added missing cross-links:** Converted plain "Section X" references to
  markdown links throughout the specification (intro, terminology table,
  implementation stages, deployment mode descriptions, core constructs table,
  booking schema, webhooks, security, extensions, etc.)

---

## 21/02/26 at 09:47:00 by Ran Yahalom

### Added JSON Schema links to specification.md

#### specification.md

**Added schema file links to all schema definition sections**

- Section 3.3 (Service Schema): added link to `schemas/catalog.json`
- Section 4 (Availability): added link to `schemas/availability.json`
- Section 5.2 (Booking Schema): added link to `schemas/scheduling.json`
- Section 7.6.1 (Booking Payment Schema): added link to
  `schemas/scheduling.json` with note pointing to `BookingPayment` and
  `PaymentContext` definitions
- Section 10.1.1 (WaitlistEntry Schema): added link to `schemas/waitlist.json`

**Fixed broken schema reference in Section 6.4 (Paid Bookings Extension Schema)
**

- Updated `schemas/services/paid_bookings.json` → `schemas/paid_bookings.json`
  to reflect the schema file relocation from `schemas/services/` to `schemas/`
- Converted plain text reference to a proper Markdown link

---

### Fixed mislocated schema and response definitions in OpenAPI spec

#### openapi/usp-rest.json

**Moved 22 schemas out of `USPEnvelope` to top-level `components.schemas`**

- `PaginationRequest`, `Pagination`, `Service`, `Duration`, `Pricing`,
  `Location`, `Channel`, `ServicePolicies`, `AvailabilityHint`,
  `FeedSubscription`, `TimeSlot`, `Hold`, `Buyer`, `Booking`, `BookingPayment`,
  `PaymentContext`, `Message`, `WaitlistEntry`, `ResourceRequirement`,
  `RegistryEntry`, `ServiceSearchResult`, and `ProblemDetails` were incorrectly
  nested as extra keys inside the `USPEnvelope` schema object (siblings of its
  `type`/`required`/`properties`)
- All 22 are now proper siblings of `USPEnvelope` under `components.schemas`,
  which allows `$ref` pointers like `#/components/schemas/Duration` to resolve
  correctly

**Moved `responses` block from inside `schemas` to `components.responses`**

- The 8 response definitions (`BadRequest`, `Unauthorized`, `NotFound`,
  `Conflict`, `UnprocessableEntity`, `FailedDependency`, `TooManyRequests`,
  `InternalServerError`) were nested under `components.schemas.responses`
  instead of `components.responses`
- They are now correctly placed as a sibling of `schemas` under `components`

---

### Renamed business search endpoint and added service search

#### specification.md

**Section 7.5.2 –
Renamed `POST /registry/search` → `POST /registry/search_business`**

- Endpoint path changed to disambiguate from the new service search endpoint

**Section 7.5.3 – Added Service Search (`POST /registry/search_services`)**

- New section enabling platforms to search across all registered businesses'
  services directly
- Request accepts `location`, `verticals`, `categories`, `query`,
  `price_range` (min/max/currency), `duration_range` (min_minutes/max_minutes),
  and `pagination`
- Response returns a `services` array with `service_id`, `service_name`, nested
  `business` object (id, usp_profile_url, name), `category`, `duration_minutes`,
  `price`, `location`, and `timezone`

**Section 7.5.4 – Renumbered Registry Governance**

- Previously 7.5.3, renumbered to accommodate the new Service Search section

**Section 11 – Endpoint Summary Table**

- Updated `/registry/search` row to `/registry/search_business`
- Added new row for
  `Search Services | POST | /registry/search_services | discovery (optional)`

#### openapi/usp-rest.json

**Renamed path `/registry/search` → `/registry/search_business`**

- operationId remains `searchBusinesses`

**Added path `/registry/search_services`**

- operationId: `searchServices`
- Request body includes `price_range` and `duration_range` filters in addition
  to the base search fields
- Response returns `services` array of `ServiceSearchResult` items with
  pagination

**Added schema `ServiceSearchResult`**

- Fields: `service_id`, `service_name`, `business` (id, usp_profile_url, name),
  `category`, `duration_minutes`, `price` (amount, currency), `location`,
  `timezone`

---

### Added missing response snippets and fixed snippets to conform to OpenAPI schemas

#### specification.md

**Section 7.5.1 – Business Registration (`POST /registry/businesses`)**

- Added `Request:` label before the existing JSON body
- Added `Response:` snippet returning a `USPEnvelope` with
  `dev.usp.discovery.registry` capability and a `registration` object containing
  `id`, echoed request fields, `status`, and `created_at`

**Section 7.5.2 – Business Search (`POST /registry/search_business`)**

- Added `Request:` label before the existing JSON body
- Added `Response:` snippet returning a `USPEnvelope` with a `businesses` array
  of `RegistryEntry` objects and `pagination` with `cursor`/`has_more`

**Section 4.3.3 – Release Slot response**

- Added `slot_id`, `service_id`, and `expires_at` to the `hold` object in the
  response, which are required fields per the `Hold` schema

**Section 7.5.2 – Business Search response**

- Added `status` and `created_at` to each business entry in the `businesses`
  array, which are required fields per the `RegistryEntry` schema

**Section 7.5.3 – Service Search request and response**

- Changed `price_range.min`/`max` from `50`/`200` to `5000`/`20000` (minor
  currency units)
- Changed `price.amount` from `120`/`180` to `12000`/`18000` (minor currency
  units), consistent with the convention used throughout the spec

**Section 7.7.4 – Deposit Flow**

- Added `slot_start` to `payment_context.metadata`, matching the
  `PaymentContext` schema and other `create_booking` response examples

---

### New and updated OpenAPI schemas

#### openapi/usp-rest.json

**New schemas**

| Schema                | Description                                                                                                                                |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| `Duration`            | `fixed` / `range` (min, max, step), `buffer_before`, `buffer_after`                                                                        |
| `Pricing`             | `model` (enum), `amount`, `currency`, `deposit` (type, value, refundable)                                                                  |
| `Location`            | `id`, `name`, `address`, `coordinates`                                                                                                     |
| `Channel`             | `type` (enum: in_person/virtual/phone/hybrid), `virtual_provider`, `instructions`                                                          |
| `ServicePolicies`     | `cancellation`, `rescheduling`, `no_show`, `booking_window`, `confirmation_mode`, `requires_payment`, `payment_timing` with all sub-fields |
| `AvailabilityHint`    | `summary`, `generated_at`, `next_available_date`                                                                                           |
| `BookingPayment`      | `status` (enum), `timing`, `amount`, `currency`, `amount_due`, `deposit_amount`, `transaction_id`, `order_reference`, `payment_url`        |
| `PaymentContext`      | `amount_due`, `currency`, `description`, `line_items`, `metadata`, `expires_at`                                                            |
| `ResourceRequirement` | `type` (enum: staff/room/equipment/other), `name`, `selectable`, `options`                                                                 |
| `RegistryEntry`       | `id`, `usp_profile_url`, `name`, `verticals`, `categories`, `location`, `timezone`, `status`, `created_at`                                 |

**Updated schemas – added missing fields**

| Schema          | Fields added                                   |
|-----------------|------------------------------------------------|
| `Service`       | `category`, `locations`, `resources`, `images` |
| `Booking`       | `resources`, `location`, `cancellation`        |
| `WaitlistEntry` | `preferred_slots`                              |

**Updated schemas – added types, descriptions, defaults, and enums**

Every property across all schemas was updated from bare `{}` to include explicit
`type`, `description`, `format`, `default`, and/or `enum` values. This applies
to:

- `USPEnvelope` (version, capabilities)
- `Service` (all 14 properties)
- `FeedSubscription` (id, callback_url, categories, events, status, created_at)
- `TimeSlot` (all 10 properties including capacity sub-fields, resources items,
  location, pricing)
- `Hold` (id, slot_id, service_id, spots with default:1, expires_at, status)
- `Buyer` (first_name, last_name, email with format:email, phone_number)
- `Booking` (all 18 properties including slot sub-object, status enum with 7
  values, confirmation_mode enum)
- `Message` (type, code, content, severity, path)
- `WaitlistEntry` (all 8 properties including preferred_slots items,
  offered_slot, position with minimum:1)
- `ResourceRequirement` (type, name, selectable with default:false, options)
- `RegistryEntry` (all 9 properties)
- `ServiceSearchResult` (all 8 properties)
- `ProblemDetails` (type, title, status, detail, instance, errors)

All request body schemas were also updated (list services filters, availability
query, hold slot, create booking, update booking, cancel booking, reschedule
booking, confirm payment, join waitlist, accept waitlist offer, register
business, search businesses, search services).

**Updated endpoint responses**

| Endpoint                         | Change                                                                                                  |
|----------------------------------|---------------------------------------------------------------------------------------------------------|
| `POST /registry/businesses`      | Response now returns `USPEnvelope` + `{ registration: RegistryEntry }` instead of bare envelope         |
| `POST /registry/search_business` | `businesses` array items now reference `RegistryEntry`; `pagination` now references `Pagination` schema |

**Fixed inconsistencies with specification.md**

| Issue                                       | Fix                                                                                            |
|---------------------------------------------|------------------------------------------------------------------------------------------------|
| `Booking.status` enum missing `in_progress` | Added `in_progress` to the enum to match Section 5.1 lifecycle                                 |
| `opening_hours` typed as `object`           | Changed to `array` with items schema (`day_of_week`, `opens`, `closes`) to match Section 4.3.1 |
