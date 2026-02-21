# Change Log

## 21/02/26 at 10:12:28 by [Ran Yahalom](mailto:ranya@wix.com)

- Updated AGENTS.md entry format to include a mailto link for the author's git email, so each change log entry attributes the author with a clickable email link for traceability and easy contact

---

## 21/02/26 at 10:05:27 by Ran Yahalom

- **Fixed wrong cross-section links in specification.md:** Corrected Section 1.3 (Vertical) link from `#9-service-verticals` to `#13-service-verticals`; Section 4.4 (Caching Strategy) from `#34-caching-strategy` to `#44-caching-strategy`; RFC 6749 (OAuth) from non-existent Section 9.6 to Section 9.2.3 Authentication and Authorization (`#923-authentication-and-authorization`); RFC 9421 (Webhooks) from Section 9.3 to Section 9.1.1 Webhook Security (`#911-webhook-security`); Section 5.1 (Booking Status) from `#31-booking-status-lifecycle` to `#51-booking-status-lifecycle`
- **Fixed TOC:** Section 1.5 link text and anchor from "Deployment Modes and Implementation Guide" / `#15-deployment-modes-and-implementation-guide` to "Deployment Modes" / `#15-deployment-modes` to match actual heading
- **Added missing cross-links:** Converted plain "Section X" references to markdown links throughout the specification (intro, terminology table, implementation stages, deployment mode descriptions, core constructs table, booking schema, webhooks, security, extensions, etc.)

---

## 21/02/26 at 09:47:00 by Ran Yahalom

### Added JSON Schema links to specification.md

#### specification.md

**Added schema file links to all schema definition sections**
- Section 3.3 (Service Schema): added link to `schemas/catalog.json`
- Section 4 (Availability): added link to `schemas/availability.json`
- Section 5.2 (Booking Schema): added link to `schemas/scheduling.json`
- Section 7.6.1 (Booking Payment Schema): added link to `schemas/scheduling.json` with note pointing to `BookingPayment` and `PaymentContext` definitions
- Section 10.1.1 (WaitlistEntry Schema): added link to `schemas/waitlist.json`

**Fixed broken schema reference in Section 6.4 (Paid Bookings Extension Schema)**
- Updated `schemas/services/paid_bookings.json` → `schemas/paid_bookings.json` to reflect the schema file relocation from `schemas/services/` to `schemas/`
- Converted plain text reference to a proper Markdown link

---

### Fixed mislocated schema and response definitions in OpenAPI spec

#### openapi/usp-rest.json

**Moved 22 schemas out of `USPEnvelope` to top-level `components.schemas`**
- `PaginationRequest`, `Pagination`, `Service`, `Duration`, `Pricing`, `Location`, `Channel`, `ServicePolicies`, `AvailabilityHint`, `FeedSubscription`, `TimeSlot`, `Hold`, `Buyer`, `Booking`, `BookingPayment`, `PaymentContext`, `Message`, `WaitlistEntry`, `ResourceRequirement`, `RegistryEntry`, `ServiceSearchResult`, and `ProblemDetails` were incorrectly nested as extra keys inside the `USPEnvelope` schema object (siblings of its `type`/`required`/`properties`)
- All 22 are now proper siblings of `USPEnvelope` under `components.schemas`, which allows `$ref` pointers like `#/components/schemas/Duration` to resolve correctly

**Moved `responses` block from inside `schemas` to `components.responses`**
- The 8 response definitions (`BadRequest`, `Unauthorized`, `NotFound`, `Conflict`, `UnprocessableEntity`, `FailedDependency`, `TooManyRequests`, `InternalServerError`) were nested under `components.schemas.responses` instead of `components.responses`
- They are now correctly placed as a sibling of `schemas` under `components`

---

### Renamed business search endpoint and added service search

#### specification.md

**Section 7.5.2 – Renamed `POST /registry/search` → `POST /registry/search_business`**
- Endpoint path changed to disambiguate from the new service search endpoint

**Section 7.5.3 – Added Service Search (`POST /registry/search_services`)**
- New section enabling platforms to search across all registered businesses' services directly
- Request accepts `location`, `verticals`, `categories`, `query`, `price_range` (min/max/currency), `duration_range` (min_minutes/max_minutes), and `pagination`
- Response returns a `services` array with `service_id`, `service_name`, nested `business` object (id, usp_profile_url, name), `category`, `duration_minutes`, `price`, `location`, and `timezone`

**Section 7.5.4 – Renumbered Registry Governance**
- Previously 7.5.3, renumbered to accommodate the new Service Search section

**Section 11 – Endpoint Summary Table**
- Updated `/registry/search` row to `/registry/search_business`
- Added new row for `Search Services | POST | /registry/search_services | discovery (optional)`

#### openapi/usp-rest.json

**Renamed path `/registry/search` → `/registry/search_business`**
- operationId remains `searchBusinesses`

**Added path `/registry/search_services`**
- operationId: `searchServices`
- Request body includes `price_range` and `duration_range` filters in addition to the base search fields
- Response returns `services` array of `ServiceSearchResult` items with pagination

**Added schema `ServiceSearchResult`**
- Fields: `service_id`, `service_name`, `business` (id, usp_profile_url, name), `category`, `duration_minutes`, `price` (amount, currency), `location`, `timezone`

---

### Added missing response snippets and fixed snippets to conform to OpenAPI schemas

#### specification.md

**Section 7.5.1 – Business Registration (`POST /registry/businesses`)**
- Added `Request:` label before the existing JSON body
- Added `Response:` snippet returning a `USPEnvelope` with `dev.usp.discovery.registry` capability and a `registration` object containing `id`, echoed request fields, `status`, and `created_at`

**Section 7.5.2 – Business Search (`POST /registry/search_business`)**
- Added `Request:` label before the existing JSON body
- Added `Response:` snippet returning a `USPEnvelope` with a `businesses` array of `RegistryEntry` objects and `pagination` with `cursor`/`has_more`

**Section 4.3.3 – Release Slot response**
- Added `slot_id`, `service_id`, and `expires_at` to the `hold` object in the response, which are required fields per the `Hold` schema

**Section 7.5.2 – Business Search response**
- Added `status` and `created_at` to each business entry in the `businesses` array, which are required fields per the `RegistryEntry` schema

**Section 7.5.3 – Service Search request and response**
- Changed `price_range.min`/`max` from `50`/`200` to `5000`/`20000` (minor currency units)
- Changed `price.amount` from `120`/`180` to `12000`/`18000` (minor currency units), consistent with the convention used throughout the spec

**Section 7.7.4 – Deposit Flow**
- Added `slot_start` to `payment_context.metadata`, matching the `PaymentContext` schema and other `create_booking` response examples

---

### New and updated OpenAPI schemas

#### openapi/usp-rest.json

**New schemas**

| Schema | Description |
|--------|-------------|
| `Duration` | `fixed` / `range` (min, max, step), `buffer_before`, `buffer_after` |
| `Pricing` | `model` (enum), `amount`, `currency`, `deposit` (type, value, refundable) |
| `Location` | `id`, `name`, `address`, `coordinates` |
| `Channel` | `type` (enum: in_person/virtual/phone/hybrid), `virtual_provider`, `instructions` |
| `ServicePolicies` | `cancellation`, `rescheduling`, `no_show`, `booking_window`, `confirmation_mode`, `requires_payment`, `payment_timing` with all sub-fields |
| `AvailabilityHint` | `summary`, `generated_at`, `next_available_date` |
| `BookingPayment` | `status` (enum), `timing`, `amount`, `currency`, `amount_due`, `deposit_amount`, `transaction_id`, `order_reference`, `payment_url` |
| `PaymentContext` | `amount_due`, `currency`, `description`, `line_items`, `metadata`, `expires_at` |
| `ResourceRequirement` | `type` (enum: staff/room/equipment/other), `name`, `selectable`, `options` |
| `RegistryEntry` | `id`, `usp_profile_url`, `name`, `verticals`, `categories`, `location`, `timezone`, `status`, `created_at` |

**Updated schemas – added missing fields**

| Schema | Fields added |
|--------|-------------|
| `Service` | `category`, `locations`, `resources`, `images` |
| `Booking` | `resources`, `location`, `cancellation` |
| `WaitlistEntry` | `preferred_slots` |

**Updated schemas – added types, descriptions, defaults, and enums**

Every property across all schemas was updated from bare `{}` to include explicit `type`, `description`, `format`, `default`, and/or `enum` values. This applies to:

- `USPEnvelope` (version, capabilities)
- `Service` (all 14 properties)
- `FeedSubscription` (id, callback_url, categories, events, status, created_at)
- `TimeSlot` (all 10 properties including capacity sub-fields, resources items, location, pricing)
- `Hold` (id, slot_id, service_id, spots with default:1, expires_at, status)
- `Buyer` (first_name, last_name, email with format:email, phone_number)
- `Booking` (all 18 properties including slot sub-object, status enum with 7 values, confirmation_mode enum)
- `Message` (type, code, content, severity, path)
- `WaitlistEntry` (all 8 properties including preferred_slots items, offered_slot, position with minimum:1)
- `ResourceRequirement` (type, name, selectable with default:false, options)
- `RegistryEntry` (all 9 properties)
- `ServiceSearchResult` (all 8 properties)
- `ProblemDetails` (type, title, status, detail, instance, errors)

All request body schemas were also updated (list services filters, availability query, hold slot, create booking, update booking, cancel booking, reschedule booking, confirm payment, join waitlist, accept waitlist offer, register business, search businesses, search services).

**Updated endpoint responses**

| Endpoint | Change |
|----------|--------|
| `POST /registry/businesses` | Response now returns `USPEnvelope` + `{ registration: RegistryEntry }` instead of bare envelope |
| `POST /registry/search_business` | `businesses` array items now reference `RegistryEntry`; `pagination` now references `Pagination` schema |

**Fixed inconsistencies with specification.md**

| Issue | Fix |
|-------|-----|
| `Booking.status` enum missing `in_progress` | Added `in_progress` to the enum to match Section 5.1 lifecycle |
| `opening_hours` typed as `object` | Changed to `array` with items schema (`day_of_week`, `opens`, `closes`) to match Section 4.3.1 |
