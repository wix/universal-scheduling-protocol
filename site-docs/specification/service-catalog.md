---
title: Service Catalog
description: USP service catalog specification - service discovery, schemas, pricing, policies, and operations.
---

# Service Catalog

**Capability:** `dev.usp.services.catalog`

The catalog enables platforms to **discover what services a business offers** -- types, pricing, policies, resources, and delivery channels.

---

## Catalog Feed

Businesses **SHOULD** publish a service catalog feed for aggregators and indexing platforms. The feed enables incremental synchronization -- aggregators maintain a cursor and fetch only changed records since their last sync, rather than re-fetching the entire catalog.

**Feed Endpoint:** `GET /services/feed`

The feed returns a paginated, chronologically ordered list of service records, sorted by `modified_at` ascending. This design follows the Realtime Paged Data Exchange (RPDE) pattern used by OpenActive.

=== "Request"

    ```
    GET /services/feed?cursor=crs_a1b2c3d4e5f6&limit=50
    ```

=== "Response"

    ```json
    {
      "usp": {
        "version": "2026-02-09",
        "capabilities": {
          "dev.usp.services.catalog": [
            { "version": "2026-02-09" }
          ]
        }
      },
      "items": [
        {
          "state": "updated",
          "modified_at": "2026-03-10T09:15:00Z",
          "data": {
            "id": "svc_haircut_001",
            "business_id": "biz_glamour_salon_nyc",
            "name": "Women's Haircut & Style",
            "type": "appointment",
            "...": "full service object"
          }
        },
        {
          "state": "deleted",
          "modified_at": "2026-03-10T10:00:00Z",
          "data": {
            "id": "svc_old_service_002",
            "business_id": "biz_glamour_salon_nyc"
          }
        }
      ],
      "pagination": {
        "cursor": "crs_f7g8h9i0j1k2",
        "has_more": true
      },
      "feed_meta": {
        "feed_generated_at": "2026-03-10T10:05:00Z",
        "total_services": 47,
        "feed_status": "healthy"
      }
    }
    ```

### Feed Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `items[].state` | string | **Yes** | `updated` (new or modified service) or `deleted` (service removed; aggregators **MUST** prune this from their index). |
| `items[].modified_at` | string | **Yes** | RFC 3339 timestamp of when this record was last modified. Used as the cursor for incremental sync. |
| `items[].data` | object | **Yes** | Full service object for `updated` state; object containing only `id` for `deleted` state. |
| `pagination.next_cursor` | string | **Yes** | Opaque cursor to pass as the `cursor` query parameter on the next request. |
| `pagination.has_more` | boolean | **Yes** | Whether more records exist beyond this page. |
| `feed_meta.feed_generated_at` | string | **Yes** | RFC 3339 timestamp of when this feed page was computed. |
| `feed_meta.total_services` | integer | **Yes** | Total number of active (non-deleted) services in the business's catalog. |
| `feed_meta.feed_status` | string | **Yes** | Health status: `healthy`, `degraded`, or `rebuilding`. |

!!! note "Feed Cursor vs Pagination Cursor"
    The feed endpoint uses `pagination.next_cursor` (a timestamp string) rather than the generic `cursor` used by all other paginated USP operations. The feed cursor is a `modified_at` timestamp that enables incremental RPDE-style synchronization.

---

## Catalog Caching and Indexing

Service catalog data is relatively static -- services, pricing, and policies change infrequently compared to real-time availability. Platforms and aggregators **SHOULD** cache catalog data rather than querying it on every user interaction.

**Recommended caching strategies:**

- **Merchant aggregators** (e.g., Google Merchant Center): Index by consuming the catalog feed via incremental cursor-based synchronization. Synchronize at least once per hour for high-frequency businesses and once per day for low-frequency businesses.
- **Web crawlers and structured data**: Businesses **SHOULD** expose service catalog data as [schema.org/Service](https://schema.org/Service) structured data on their website.
- **Platform-level caching**: Cache catalog responses according to HTTP `Cache-Control` headers. Refresh at intervals between 1 and 24 hours.

!!! warning "Real-time Operations"
    Availability and booking are real-time operations and **MUST NOT** be served from stale caches. See [Availability Caching Strategy](availability.md#caching-strategy) for the tiered caching approach.

### Structured Data Mapping Guide

When exposing service catalog data as schema.org structured data:

| USP Field | schema.org Property | Notes |
|-----------|---------------------|-------|
| `name` | `schema:name` | Direct mapping |
| `description` | `schema:description` | Direct mapping |
| `type` | `schema:serviceType` | Map USP vertical to a human-readable string |
| `pricing.amount` | `schema:offers.price` | Convert from minor units to decimal (e.g., `7500` -> `75.00`) |
| `pricing.currency` | `schema:offers.priceCurrency` | Direct mapping (ISO 4217) |
| `channel.type: virtual` | `schema:availableChannel.serviceType` | Set to `OnlineOnly` |
| `channel.type: at_business_location` | `schema:availableChannel.serviceLocation` | Map to `schema:Place` with address |
| `channel.type: at_buyer_location` | `schema:areaServed` | Map `channel.service_area`, if present. Do not publish the buyer's `delivery_address` |
| `locations[]` | `schema:areaServed` / `schema:serviceLocation` | Map each location to a `schema:Place` |
| `availability_hint.next_available_date` | `schema:availabilityStarts` | Approximate; use with `schema:Offer` |
| `media[].url` (type=image) | `schema:image` | Direct mapping. Filter to `type: "image"` entries |
| `policies.cancellation` | `schema:cancellationPolicy` | Map to a human-readable string |
| `duration.fixed` | `schema:duration` | No direct schema.org equivalent for service duration |
| `capacity.max` | `schema:maximumAttendeeCapacity` | For `group` and `reservation` types |

---

## Service Schema

The service object represents a bookable offering from a business. Each service has a type (vertical), duration, pricing, policies, and optional resource requirements.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | **Yes** | Unique service identifier, scoped to the business. The composite key `(business_id, id)` is globally unique. |
| `business_id` | string | **Yes** | Identifier of the business that owns this service. Together with `id`, forms the globally unique composite key. |
| `provider` | Provider | No | Inline business metadata for display without a separate profile fetch. |
| `name` | string | **Yes** | Human-readable display name (e.g., "Women's Haircut & Style"). |
| `description` | string \| Description | No | Plain string or structured `Description` object with multiple format variants. |
| `type` | string | **Yes** | Service vertical: `appointment`, `group`, `reservation`, `rental`, `field_service`, or vendor-defined. |
| `categories` | Array[ServiceCategory] | No | Multi-taxonomy category labels. Each entry has required `taxonomy` plus optional `id`, `name`, `parent_id`, `value`, and `primary`. Simple case: one-element array with `taxonomy: "merchant"`. See [Category rules](#category-rules). |
| `duration` | Duration | **Yes** | Duration configuration. See [Duration](#duration) below. |
| `pricing` | Pricing | **Yes** | Pricing model and amounts. See [Pricing](#pricing) below. |
| `locations` | Array[Location] | No | Physical or virtual locations where the service is offered. |
| `resources` | Array[ResourceRequirement] | No | Required staff, rooms, or equipment. See [Resource Requirement](#resource-requirement). |
| `channel` | object | **Yes** | Delivery channel for the service. See channel types below. |
| `policies` | ServicePolicies | **Yes** | Booking, cancellation, rescheduling, and payment policies. See [Service Policies](#service-policies). |
| `capacity` | object | No | `{min, max, waitlist}` -- **REQUIRED** for `group` and `reservation` types. |
| `media` | Array[Media] | No | Service media items (images, videos). |
| `rating` | object | No | `{value, scale_min, scale_max, count}` -- aggregate service rating. |
| `status` | string | No | `active` (default), `suspended`, or `archived`. |
| `handle` | string | No | URL-friendly slug (e.g., `womens-haircut-style`). |
| `url` | string | No | Canonical service page URL on the business's website. |
| `tags` | Array[string] | No | Freeform tags for categorization and search. |
| `metadata` | object | No | Business-defined custom data. Platforms **SHOULD** pass through opaquely. |
| `availability_hint` | AvailabilityHint | No | Approximate availability summary for agent-assisted discovery. |
| `links` | Array[Link] | No | Typed links to policy and information pages specific to this service. |
| `localized` | LocalizedFields | No | Per-locale overrides for human-readable text fields. `category_name` overrides the primary `categories[]` entry's `name`. |

### Category rules

> **JSON Schema:** [/$defs/ServiceCategory](../../schemas/catalog.json)

Each `categories[]` entry carries required `taxonomy` and at least one of `id`, `name`, or `value`. External (non-`merchant`) taxonomies **MUST** carry `value`. Exactly one entry is primary: if exactly one has `primary: true`, that is the primary; else if no entry sets `primary` and exactly one has `taxonomy: "merchant"`, that entry is the primary; else the first entry is the primary. Never more than one `primary: true`. The primary entry is the source for display, localization, and registry projection of `ServiceSearchResult.category` (pick order: primary `name`, else primary `value`, else primary `id`, else first entry `value`, else service `type`).

Catalog filters (`category_id` / `categories`) match the primary entry's `id` and **MAY** match any entry's `id`. Filter parameters remain flat ID strings.

```json
"categories": [
  {
    "taxonomy": "merchant",
    "id": "cat_haircut",
    "name": "Haircut",
    "parent_id": "cat_hair",
    "value": "beauty > hair > haircut",
    "primary": true
  },
  {
    "taxonomy": "google_business_profile",
    "value": "job_type_id:hair_styling"
  }
]
```

### Channel Types

| `channel.type` | Description | Additional Fields |
|----------------|-------------|-------------------|
| `at_business_location` | Service is delivered at the business's physical location. The buyer travels there. | `instructions`: optional arrival instructions |
| `at_buyer_location` | Service is delivered at a location the buyer specifies. The business travels there; the booking requires `delivery_address`. | `instructions`, `service_area`: optional description of the area served |
| `virtual` | Service is delivered remotely via video/audio call. | `virtual_provider`: platform name (e.g., "Zoom"). `instructions`: join instructions |
| `phone` | Service is delivered via phone call. | `instructions`: optional call-in details |
| `hybrid` | Delivered via more than one of the above channels, at the buyer's choice. | `virtual_provider`, `instructions`, `service_area` |

### Description Schema

The `description` field accepts either a plain string or a structured object:

=== "Plain string"

    ```json
    "description": "A full haircut and styling session with one of our experienced stylists."
    ```

=== "Structured object"

    ```json
    "description": {
      "plain": "A full haircut and styling session with one of our experienced stylists.",
      "markdown": "A full **haircut and styling** session with one of our experienced stylists.\n\n- Consultation\n- Shampoo\n- Cut & blow-dry"
    }
    ```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plain` | string | **Yes** | Plain text content. Always required as the universal fallback. |
| `markdown` | string | No | Markdown-formatted content. |
| `html` | string | No | HTML-formatted content. Platforms **MUST** sanitize before rendering. |

!!! tip "Format Preference"
    Platforms **SHOULD** prefer the richest format they can safely render (`html` > `markdown` > `plain`), falling back to `plain` for unsupported formats.

### Provider Schema

The optional `provider` object carries inline business metadata so platforms can display the business name and policy links without a separate profile fetch.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | **Yes** | Business display name (e.g., "Glamour Salon NYC"). |
| `url` | string | No | Business website URL. |
| `links` | Array[Link] | No | Typed links to policy and information pages. Well-known `type` values: `privacy_policy`, `terms_of_service`, `refund_policy`, `cancellation_policy`, `faq`. |

```json
"provider": {
  "name": "Glamour Salon NYC",
  "url": "https://glamoursalon.nyc",
  "links": [
    {
      "type": "cancellation_policy",
      "url": "https://glamoursalon.nyc/policies/cancellation"
    },
    {
      "type": "terms_of_service",
      "url": "https://glamoursalon.nyc/terms",
      "title": "Booking Terms"
    }
  ]
}
```

### Availability Hint

An optional, lightweight summary of a service's near-term availability. Designed for AI agents and platforms that need to make smart decisions about **what date ranges to query** before calling the real-time [availability API](availability.md).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `summary` | string | **Yes** | Natural-language description of near-term availability for AI agents. |
| `generated_at` | string | **Yes** | RFC 3339 timestamp. A hint older than 6 hours **SHOULD** be treated with lower confidence. |
| `next_available_date` | string | No | `YYYY-MM-DD` date of the next day with known availability. |

!!! warning "Not a Substitute for Real-time Queries"
    The availability hint is an **approximation**. Platforms **MUST NOT** use it as a substitute for real-time availability queries. It is strictly a guide for narrowing the date range.

```json
{
  "id": "svc_haircut_001",
  "business_id": "biz_glamour_salon_nyc",
  "name": "Women's Haircut & Style",
  "availability_hint": {
    "summary": "Fully booked this week. Next week we have good availability on Tuesday afternoon and Wednesday morning. Thursday is filling up fast.",
    "generated_at": "2026-03-11T08:00:00-04:00",
    "next_available_date": "2026-03-17"
  }
}
```

---

## Duration

The duration object defines how long a service takes. Exactly one of `fixed`, `range`, or `undetermined` **MUST** be provided.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fixed` | string | Conditional | ISO 8601 duration. **REQUIRED** if neither `range` nor `undetermined` is present. |
| `range` | object | Conditional | `{min, max, step}` -- all ISO 8601 durations. Buyer selects a duration within this range. |
| `undetermined` | boolean | Conditional | Set to `true` when the service has no meaningful duration to display. |
| `buffer_before` | string | No | ISO 8601 duration. Non-bookable prep time before the service. |
| `buffer_after` | string | No | ISO 8601 duration. Non-bookable cleanup time after the service. |

=== "Fixed duration"

    ```json
    {
      "fixed": "PT60M",
      "buffer_after": "PT15M"
    }
    ```

=== "Variable duration (buyer selects)"

    ```json
    {
      "range": {
        "min": "PT30M",
        "max": "PT120M",
        "step": "PT30M"
      }
    }
    ```

=== "Undetermined duration"

    ```json
    {
      "undetermined": true
    }
    ```

---

## Pricing

The pricing object defines how a service is priced.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | **Yes** | The pricing model. See values below. |
| `amount` | integer | Conditional | Price in minor currency units (e.g., `7500` = $75.00). **REQUIRED** for `fixed`, `hourly`, or `per_person`. |
| `currency` | string | **Yes** | ISO 4217 currency code. **REQUIRED** even when `model` is `free`. |
| `price_range` | object | No | `{min, max}` -- displayable price range in minor units. **RECOMMENDED** for `variable`, `hourly`, or `per_person`. |
| `deposit` | object | No | `{type, value, refundable}` -- **REQUIRED** when `payment_timing` is `deposit_required`. |

### Pricing Models

| Model | Description |
|-------|-------------|
| `fixed` | Single, fixed price regardless of duration or party size. |
| `hourly` | Price per hour. Total = `amount * duration_in_hours`. |
| `per_person` | Price per participant. Total = `amount * party_size`. |
| `variable` | Price varies by time of day, demand, etc. Actual price returned on each slot in availability response. |
| `free` | No charge. `amount` **MUST NOT** be present. `requires_payment` **MUST** be `false`. |

---

## Service Policies

Machine-readable policies that enable agents to make informed decisions. These policies govern the [booking lifecycle](booking.md) and **MUST** be enforced by the business.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cancellation` | object | **Yes** | `allowed`, `free_cancellation_until` (ISO 8601 duration), `late_cancellation_fee` (minor units), `no_cancellation_after` (ISO 8601 duration). |
| `rescheduling` | object | **Yes** | `allowed`, `free_reschedule_until`, `max_reschedules`, `fee`. |
| `no_show` | object | No | `fee` (fixed) or `fee_percentage` (0-100), `grace_period` (ISO 8601 duration). |
| `booking_window` | object | **Yes** | `min_advance`, `max_advance`, `slot_interval` -- all ISO 8601 durations. |
| `confirmation_mode` | string | **Yes** | `auto` (confirmed immediately) or `manual` (requires business approval within 24 hours). |
| `requires_payment` | boolean | **Yes** | Whether this service requires any payment. |
| `payment_timing` | string | Conditional | **REQUIRED** when `requires_payment` is `true`. One of: `at_booking`, `at_service`, `deposit_required`. |

---

## Resource Requirement

Defines what staff, rooms, or equipment are needed for a service, and whether the buyer can select a specific resource.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | **Yes** | `staff`, `room`, `equipment`, or `other`. |
| `name` | string | No | Human-readable label (e.g., "Stylist", "Treatment Room"). |
| `selectable` | boolean | No | Whether the buyer can choose a specific resource. Default: `false`. |
| `options` | Array[Resource] | No | `{id, name, description, image_url}` -- available resource instances. **REQUIRED** when `selectable` is `true`. |

---

## Validation Rules

### Payment and Pricing Constraint Matrix

| `requires_payment` | `payment_timing` | `pricing.model` | `pricing.amount` | Legal? | Notes |
|--------------------|-------------------|-----------------|-------------------|--------|-------|
| `false` | (absent) | `free` | (absent) | **Yes** | Free service |
| `false` | (absent) | `fixed` | (any) | **No** | If no payment required, model **MUST** be `free` |
| `true` | `at_booking` | `free` | (any) | **No** | Cannot require payment for a free-priced service |
| `true` | `at_booking` | `fixed` | (required) | **Yes** | Standard paid service |
| `true` | `at_booking` | `variable` | (optional) | **Yes** | Variable pricing; actual price on each slot |
| `true` | `at_service` | `fixed` | (required) | **Yes** | Price shown but collected in person |
| `true` | `deposit_required` | `fixed` | (required) | **Yes** | Deposit collected upfront, remainder at service |

### Summary Rules

1. When `requires_payment` is `false`, `pricing.model` **MUST** be `free` and `payment_timing` **MUST NOT** be present.
2. When `requires_payment` is `true`, `pricing.model` **MUST NOT** be `free`.
3. When `payment_timing` is `deposit_required`, the `pricing.deposit` object **MUST** be present.
4. When `pricing.model` is `free`, `pricing.amount` **MUST NOT** be present.
5. When `pricing.model` is `fixed`, `hourly`, or `per_person`, `pricing.amount` **MUST** be present and greater than zero.
6. Exactly one of `duration.fixed`, `duration.range`, or `duration.undetermined` **MUST** be present.
7. When `duration.undetermined` is `true`, `pricing.model` **MUST NOT** be `hourly`.

---

## Operations

### List Services -- `POST /services/list`

Returns a filtered, paginated list of services from the business catalog. Designed for interactive use by platforms and AI agents.

**Filters:**

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Service vertical (e.g., `appointment`, `group`). |
| `category_id` | string | Single category ID to filter by. Matches the primary `categories[]` entry's `id`, and **MAY** match any entry's `id`. |
| `categories` | Array[string] | Category IDs to filter by (OR logic). Same match rule as `category_id`. |
| `location_id` | string | Location ID for multi-location businesses. |
| `price` | object | `{min, max}` in minor currency units. |

All specified filters combine with AND logic. Within `categories`, values combine with OR logic.

**Context (optional):**

| Field | Type | Description |
|-------|------|-------------|
| `address_country` | string | Buyer's country (ISO 3166-1 alpha-2). |
| `coordinates` | object | `{latitude, longitude}` for proximity-based ranking. |
| `language` | string | Preferred language (IETF BCP 47). |
| `currency` | string | Preferred currency (ISO 4217). |
| `intent` | string | Free-text description of the buyer's intent. |

=== "Request (structured filters)"

    ```json
    {
      "filters": {
        "type": "appointment",
        "category_id": "beauty"
      },
      "pagination": {
        "limit": 20,
        "cursor": null
      }
    }
    ```

=== "Request (free-text search with context)"

    ```json
    {
      "query": "deep tissue massage",
      "filters": {
        "type": "appointment",
        "categories": ["wellness", "spa"],
        "price": { "min": 5000, "max": 15000 }
      },
      "context": {
        "address_country": "US",
        "coordinates": { "latitude": 37.4419, "longitude": -122.1430 },
        "language": "en",
        "currency": "USD",
        "intent": "looking for a relaxing post-workout massage"
      },
      "pagination": { "limit": 10, "cursor": null }
    }
    ```

=== "Response"

    ```json
    {
      "usp": {
        "version": "2026-02-09",
        "capabilities": {
          "dev.usp.services.catalog": [
            { "version": "2026-02-09" }
          ]
        }
      },
      "services": [
        {
          "id": "svc_haircut_001",
          "business_id": "biz_glamour_salon_nyc",
          "name": "Women's Haircut & Style",
          "type": "appointment",
          "duration": { "fixed": "PT60M", "buffer_after": "PT15M" },
          "pricing": { "model": "fixed", "amount": 7500, "currency": "USD" },
          "channel": { "type": "at_business_location" },
          "resources": [
            {
              "type": "staff",
              "name": "Stylist",
              "selectable": true,
              "options": [
                { "id": "staff_jane", "name": "Jane Smith" },
                { "id": "staff_alex", "name": "Alex Johnson" }
              ]
            }
          ],
          "policies": {
            "cancellation": {
              "allowed": true,
              "free_cancellation_until": "PT24H",
              "late_cancellation_fee": 2500
            },
            "rescheduling": { "allowed": true, "free_reschedule_until": "PT24H", "max_reschedules": 2 },
            "no_show": { "fee_percentage": 100, "grace_period": "PT15M" },
            "booking_window": { "min_advance": "PT2H", "max_advance": "P60D", "slot_interval": "PT30M" },
            "confirmation_mode": "auto",
            "requires_payment": true,
            "payment_timing": "at_service"
          },
          "availability_hint": {
            "summary": "Fully booked this week. Next week we have good availability Tuesday afternoon and all day Wednesday.",
            "generated_at": "2026-03-11T08:00:00-04:00",
            "next_available_date": "2026-03-17"
          }
        }
      ],
      "pagination": { "cursor": null, "has_more": false }
    }
    ```

### Get Service -- `GET /services/{service_id}`

Returns the full service object for a single service.

=== "Request"

    ```
    GET /services/svc_haircut_001
    ```

=== "Response"

    ```json
    {
      "usp": {
        "version": "2026-02-09",
        "capabilities": {
          "dev.usp.services.catalog": [
            { "version": "2026-02-09" }
          ]
        }
      },
      "service": {
        "id": "svc_haircut_001",
        "business_id": "biz_glamour_salon_nyc",
        "name": "Women's Haircut & Style",
        "type": "appointment",
        "description": "A full haircut and styling session with one of our experienced stylists. Includes consultation, shampoo, cut, and blow-dry.",
        "duration": { "fixed": "PT60M", "buffer_after": "PT15M" },
        "pricing": { "model": "fixed", "amount": 7500, "currency": "USD" },
        "channel": { "type": "at_business_location" },
        "policies": {
          "cancellation": { "allowed": true, "free_cancellation_until": "PT24H", "late_cancellation_fee": 2500 },
          "rescheduling": { "allowed": true, "free_reschedule_until": "PT24H", "max_reschedules": 2 },
          "no_show": { "fee_percentage": 100, "grace_period": "PT15M" },
          "booking_window": { "min_advance": "PT2H", "max_advance": "P60D", "slot_interval": "PT30M" },
          "confirmation_mode": "auto",
          "requires_payment": true,
          "payment_timing": "at_service"
        }
      }
    }
    ```

### Lookup Services -- `POST /services/lookup`

Returns full service objects for a batch of service IDs in a single request. Designed for hydrating multiple service references at once.

!!! note "Batch Limits"
    Businesses **MUST** accept requests with at least 50 IDs. If the request exceeds the business's limit, return `422 Unprocessable Entity`. Duplicate IDs are silently ignored. The response array is **unordered**.

=== "Request"

    ```json
    {
      "ids": [
        "svc_haircut_001",
        "svc_massage_002",
        "svc_nonexistent_999"
      ],
      "context": { "language": "es", "currency": "EUR" }
    }
    ```

=== "Response (partial success)"

    ```json
    {
      "usp": {
        "version": "2026-02-09",
        "capabilities": {
          "dev.usp.services.catalog": [
            { "version": "2026-02-09" }
          ]
        }
      },
      "services": [
        { "id": "svc_haircut_001", "business_id": "biz_glamour_salon_nyc", "name": "Women's Haircut & Style", "type": "appointment" },
        { "id": "svc_massage_002", "business_id": "biz_glamour_salon_nyc", "name": "Deep Tissue Massage", "type": "appointment" }
      ],
      "messages": [
        {
          "type": "warning",
          "code": "service_not_found",
          "content": "Service ID 'svc_nonexistent_999' was not found.",
          "path": "$.ids[2]"
        }
      ]
    }
    ```

### Feed Subscriptions -- `POST /services/feed/subscriptions`

Platforms and aggregators **MAY** register for push-based catalog change notifications.

| Operation | Method | Path | Description |
|-----------|--------|------|-------------|
| Create Subscription | `POST` | `/services/feed/subscriptions` | Register for catalog change notifications |
| Get Subscription | `GET` | `/services/feed/subscriptions/{subscription_id}` | Get subscription status |
| Pause Subscription | `POST` | `/services/feed/subscriptions/{subscription_id}/pause` | Temporarily stop receiving events |
| Resume Subscription | `POST` | `/services/feed/subscriptions/{subscription_id}/resume` | Resume receiving events |
| Cancel Subscription | `DELETE` | `/services/feed/subscriptions/{subscription_id}` | Permanently cancel the subscription |

---

## Conformance Requirements

A conforming implementation of `dev.usp.services.catalog` **MUST**:

1. Implement `POST /services/list` returning a paginated list with the `usp` envelope, `services` array, and `pagination` object.
2. Implement `GET /services/{service_id}` returning a single service with the `usp` envelope.
3. Implement `POST /services/lookup` accepting at least 50 IDs with partial-success semantics.
4. Include all required fields on each `Service` object: `id`, `business_id`, `name`, `type`, `duration`, `pricing`, `channel`, `policies`.
5. Conform to the validation rules for `requires_payment`, `payment_timing`, and `pricing.model` combinations.
6. Ignore unrecognized `query`, `context`, and `filters` fields without returning an error (forward compatibility).
7. Use opaque cursors for pagination across all catalog endpoints.

A conforming implementation **SHOULD**:

1. Implement `GET /services/feed` for incremental catalog synchronization.
2. Populate `provider`, `rating`, `availability_hint`, and `price_range` when data is available.
