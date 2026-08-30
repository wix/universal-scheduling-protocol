---
title: Service Catalog
description: USP service catalog specification - service discovery, schemas, pricing, policies, and operations.
---

# Service Catalog

**Capability:** `dev.usp-protocol.services.catalog`

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
        "version": "2026-08-20",
        "capabilities": {
          "dev.usp-protocol.services.catalog": [
            { "version": "2026-08-20" }
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

> **JSON Schema:** [/$defs/ServiceCategory](https://github.com/wix/universal-scheduling-protocol/blob/master/schemas/catalog.json)

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

An optional snapshot of near-term availability for agent-assisted discovery and registry ranking. When present, it combines a natural-language `summary` with structured `slot_bitmaps` so platforms can narrow [availability query](availability.md) date ranges and registries can rank search results without treating the hint as a live slot feed.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `summary` | string | **Yes** | Natural-language description of near-term availability for AI agents. |
| `generated_at` | string | **Yes** | RFC 3339 timestamp when the snapshot was produced. Freshness timestamp only; not bit 0 on any ruler. |
| `valid_until` | string | No | RFC 3339 instant after `generated_at` when the snapshot stops being usable for availability ranking. |
| `next_available_date` | string | Conditional | Service-local `YYYY-MM-DD` date of the earliest available start across all duration bitmaps. **Required** when any bitmap has a set bit; **MUST** be omitted when every bitmap is all-zero or when the whole hint is omitted. |
| `slot_bitmaps` | Array[AvailabilitySlotBitmap] | **Yes** | Non-empty array of duration-specific availability rulers. See [What gets published](#what-gets-published) below. |

Each `AvailabilitySlotBitmap` entry:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `duration` | string | **Yes** | ISO 8601 duration of the booking this bitmap describes (for example `PT60M`). |
| `starts_at` | string | **Yes** | RFC 3339 instant of bit 0 (first candidate start on this ruler, not hint generation time). |
| `start_interval` | string | **Yes** | ISO 8601 duration between consecutive candidate starts. Independent of `duration`. |
| `slot_count` | integer | **Yes** | Number of candidate starts on this ruler (1 through 4294967296). Every decoded index **MUST** be strictly less than `slot_count`. |
| `encoding` | string | **Yes** | **MUST** be `roaring32-portable-base64`. |
| `bitmap` | string | **Yes** | Standard Base64 of a 32-bit Roaring portable serialization. Set bits are candidate starts with at least one approximately bookable unit. |

!!! warning "Not a Substitute for Real-time Queries"
    The availability hint is an **approximation**. Platforms **MUST NOT** use it as a substitute for real-time availability queries. Registries **MAY** use structured bitmaps for bounded secondary ranking only ([Discovery Registry - Availability ranking](discovery-registry.md#availability-ranking)).

A producer that did not sample a structured availability grid **MUST** omit the entire `availability_hint`. Summary-only hints, empty `slot_bitmaps` arrays, and dummy all-zero rulers **MUST NOT** represent unknown availability.

#### What gets published

##### Why a bitmap

The hint answers a discovery question, not a booking question: **which candidate
start times were approximately bookable when the catalog snapshot was made?**
A bitmap represents that answer as a finite set of integer indices on a time
ruler. One bit records one candidate start without repeating a timestamp or
slot object, so a producer can summarize many possible starts compactly.

USP uses the 32-bit Roaring portable format because availability can be sparse
or dense, and Roaring remains compact in both cases. It also provides the set
operations that ranking needs directly:

```text
available AND intent
    -> candidate starts both hinted open and acceptable to the buyer
cardinality(available AND intent) / cardinality(intent)
    -> coverage
cardinality(available) / slot_count
    -> density
minimum(available AND intent)
    -> earliest acceptable hinted start used for soonness
```

Standard Base64 is only the JSON transport wrapper around the portable Roaring
bytes. The complete path is:

```text
business schedule -> candidate-start ruler -> Roaring set -> Base64 in
availability_hint -> registry decode -> buyer-intent set -> intersection ->
coverage, density, soonness -> bounded secondary rank -> rank_signals
```

A bit represents a candidate booking start for one duration. It is not an
occupied minute, capacity count, live slot, or score. The registry uses decoded
sets only after normal search recall, and a missing or unusable hint never
removes a result.

`availability_hint` remains optional on a service. When a producer publishes it, the object **MUST** contain `summary`, `generated_at`, and a non-empty `slot_bitmaps` array.

`slot_bitmaps` is an array because one service can have more than one bookable duration. Each entry is one duration-specific ruler with its own `duration`, time origin, tick spacing, length, encoding, and bitmap. A duration **MUST** appear at most once. Shared snapshot metadata (`summary`, `generated_at`, optional `valid_until`, and conditional `next_available_date`) lives on the hint; per-duration grid metadata lives on each entry.

`generated_at` **MUST NOT** be treated as bit 0. `starts_at` **MAY** be later than `generated_at` (for example, the hint is generated at 07:30 and the shop opens at 09:00).

The producer **MAY** publish `valid_until` as an RFC 3339 instant after `generated_at`. When `valid_until` is absent, a registry **MAY** apply a documented validity policy. While a hint is usable, its age **MUST NOT** continuously reduce its score.

If any duration bitmap contains a set bit, `next_available_date` **MUST** be present and **MUST** equal the service-local calendar date of the earliest available start across all duration entries. If every duration bitmap is all-zero, `next_available_date` **MUST** be omitted. An all-zero bitmap means sampled and known empty; an omitted `availability_hint` means unknown.

Producers **MUST NOT** encode unknown values as `0`, `""`, a zero-length blob, an empty array, or a dummy all-zero ruler. Consumers **MUST** map absent data to a neutral availability signal, never to maximum soonness.

```json
{
  "id": "svc_back_massage_001",
  "business_id": "biz_downtown_spa",
  "name": "Back Massage",
  "type": "appointment",
  "duration": {
    "range": {
      "min": "PT60M",
      "max": "PT90M",
      "step": "PT30M"
    }
  },
  "availability_hint": {
    "summary": "Good availability this morning and late afternoon. Midday is mostly booked, and 90-minute sessions are limited to 9:00-9:30 and after 16:00.",
    "generated_at": "2026-03-14T07:30:00-04:00",
    "valid_until": "2026-03-14T19:30:00-04:00",
    "next_available_date": "2026-03-14",
    "slot_bitmaps": [
      {
        "duration": "PT60M",
        "starts_at": "2026-03-14T09:00:00-04:00",
        "start_interval": "PT30M",
        "slot_count": 17,
        "encoding": "roaring32-portable-base64",
        "bitmap": "OjAAAAEAAAAAAAcAEAAAAAAAAQACAAYACgAOAA8AEAA="
      },
      {
        "duration": "PT90M",
        "starts_at": "2026-03-14T09:00:00-04:00",
        "start_interval": "PT30M",
        "slot_count": 16,
        "encoding": "roaring32-portable-base64",
        "bitmap": "OjAAAAEAAAAAAAMAEAAAAAAAAQAOAA8A"
      }
    ]
  }
}
```

The two `slot_bitmaps` entries share the same `starts_at` and `start_interval` in this example, but they **MUST** be scored independently because their 1-bits differ. Subsequent subsections reuse this service as the running example.

#### What `start_interval` is

`start_interval` is the spacing of the grid of candidate start times that the bits sit on. It answers "how far apart are consecutive bits?", which is different from "how long is the booking?" (`duration`).

This restates, on the bitmap, the existing service policy `booking_window.slot_interval` ([Service Policies](#service-policies)): the interval at which slots are generated (for example `PT30M` means slots may start every 30 minutes). Publishing `start_interval` on the bitmap lets a consumer turn a bit index into a wall-clock start without fetching service policies.

| Field | Meaning | Back massage example |
| --- | --- | --- |
| `duration` | How long the booking occupies | `PT60M` or `PT90M` |
| `start_interval` | Gap between consecutive bits | `PT30M` |

When `start_interval` is smaller than `duration`, consecutive 1-bits describe overlapping windows. That is normal. A 90-minute massage starting at 09:00 and another starting at 09:30 are two legitimate options that cannot both be booked.

Both fields are required on every entry. On the example `PT30M` grid, both
durations can start at 09:00, 09:30, 10:00, and so on. The bits do not mean
"occupied 30-minute blocks." They mean "a booking of this entry's `duration`
can start at this tick."

#### How one bitmap maps onto time

Think of a ruler whose tick marks are candidate **start times**, not occupied minutes.

```text
generated_at  07:30-04:00     (freshness only; not a slot start)

starts_at     09:00-04:00     bit 0
              09:30-04:00     bit 1
              10:00-04:00     bit 2
              10:30-04:00     bit 3
              11:00-04:00     bit 4
              ...
              last tick       bit (slot_count - 1)

Each 1-bit means: a booking of this entry's duration can start at that tick.
Each 0-bit means: no known availability for that start.
```

The mapping **MUST** be:

```text
start(i) = starts_at + i * start_interval
end(i)   = start(i) + duration
i in [0, slot_count)
```

All arithmetic **MUST** use instants (RFC 3339), not local clock labels. Equal
instants with different offsets **MUST** compare equal.

A 1-bit **MUST** mean at least one approximately bookable unit exists for that start and duration at hint generation time. It **MUST NOT** be interpreted as a resource count, remaining capacity, or a live availability guarantee. Platforms **MUST NOT** treat the bitmap as a substitute for real-time slot queries ([Availability](availability.md)).

With `duration` `PT60M` and `start_interval` `PT30M`, bits 2 and 3 both being
1 means two overlapping candidate windows, 10:00-11:00 and 10:30-11:30.

```text
09:00  09:30  10:00  10:30  11:00  11:30  12:00  12:30
  1      0      1      1      0      0      1      0
  |------60m------|
         (taken)
                |------60m------|
                       |------60m------|
                                      (taken)
                                             |------60m------|
```

`slot_count` is the length of the ruler. It is required because Roaring32
indices stop at 4294967295 and because an open buyer preference must stop at
the end of represented data. Consumers **MUST** clip intent projection to
`[0, slot_count)`.

#### The example

The running back massage can be given for 60 minutes or 90 minutes. The catalog
duration is `{ min: "PT60M", max: "PT90M", step: "PT30M" }`, so the hint
carries one bitmap per selectable duration. The therapist works 09:00 to 18:00
local time (`America/New_York`, offset `-04:00`) on 14 March 2026, with three
commitments:

```text
11:00-12:00   existing booking
13:00-14:00   lunch
15:00-16:00   existing booking
```

On a 30-minute grid starting at 09:00, the two durations produce different bit patterns:

```text
 i    start    60 min window     60  90 min window     90
  0   09:00    09:00-10:00        1   09:00-10:30        1
  1   09:30    09:30-10:30        1   09:30-11:00        1
  2   10:00    10:00-11:00        1   10:00-11:30        0
  3   10:30    10:30-11:30        0   10:30-12:00        0
  4   11:00    11:00-12:00        0   11:00-12:30        0
  5   11:30    11:30-12:30        0   11:30-13:00        0
  6   12:00    12:00-13:00        1   12:00-13:30        0
  7   12:30    12:30-13:30        0   12:30-14:00        0
  8   13:00    13:00-14:00        0   13:00-14:30        0
  9   13:30    13:30-14:30        0   13:30-15:00        0
 10   14:00    14:00-15:00        1   14:00-15:30        0
 11   14:30    14:30-15:30        0   14:30-16:00        0
 12   15:00    15:00-16:00        0   15:00-16:30        0
 13   15:30    15:30-16:30        0   15:30-17:00        0
 14   16:00    16:00-17:00        1   16:00-17:30        1
 15   16:30    16:30-17:30        1   16:30-18:00        1
 16   17:00    17:00-18:00        1   (past close)
```

The 60-minute set is `{0, 1, 2, 6, 10, 14, 15, 16}`. The 90-minute set is `{0, 1, 14, 15}`.

Tick 2 (10:00) is why the durations need separate bitmaps. A 60-minute massage fits because it ends at 11:00 when the existing booking starts. A 90-minute massage does not, because it would run to 11:30. A consumer **MUST NOT** derive a 90-minute bitmap from a 60-minute bitmap.

`slot_count` differs: 17 for 60-minute (last start 17:00) and 16 for
90-minute (last start 16:30). Producers **MUST** publish the candidate starts
actually represented for each duration, not a shared count across durations.

#### The JSON

```json
"availability_hint": {
  "summary": "Good availability this morning and late afternoon. Midday is mostly booked, and 90-minute sessions are limited to 9:00-9:30 and after 16:00.",
  "generated_at": "2026-03-14T07:30:00-04:00",
  "valid_until": "2026-03-14T19:30:00-04:00",
  "next_available_date": "2026-03-14",
  "slot_bitmaps": [
    {
      "duration": "PT60M",
      "starts_at": "2026-03-14T09:00:00-04:00",
      "start_interval": "PT30M",
      "slot_count": 17,
      "encoding": "roaring32-portable-base64",
      "bitmap": "OjAAAAEAAAAAAAcAEAAAAAAAAQACAAYACgAOAA8AEAA="
    },
    {
      "duration": "PT90M",
      "starts_at": "2026-03-14T09:00:00-04:00",
      "start_interval": "PT30M",
      "slot_count": 16,
      "encoding": "roaring32-portable-base64",
      "bitmap": "OjAAAAEAAAAAAAMAEAAAAAAAAQAOAA8A"
    }
  ]
}
```

Field-by-field:

- `summary` is the natural-language hint for agents.
- `generated_at` is when this snapshot was produced. Its age does not continuously alter rank.
- `valid_until` is the producer-declared ranking-validity cutout. At or after that instant the hint contributes neutral availability data.
- `next_available_date` is the service-local date of the earliest 1-bit across both duration rulers.
- `slot_bitmaps[0].duration` `PT60M` identifies the 60-minute ruler, while `slot_bitmaps[1].duration` `PT90M` identifies the 90-minute ruler.
- `starts_at` is bit 0, and `start_interval` is the gap between bit `i` and bit `i+1`.
- `slot_count` 17 and 16 are the duration-specific ruler lengths.
- `encoding` names the wire contract so consumers do not guess the serialization.
- `bitmap` is Base64 of the Roaring32 portable blob holding the documented integer set.

The 60-minute Base64 decodes to 32 bytes:

```text
3a 30 00 00     cookie SERIAL_COOKIE_NO_RUNCONTAINER = 12346 little-endian
01 00 00 00     one container
00 00           container key 0 (indices 0..65535)
07 00           cardinality minus one = 7, so 8 values
10 00 00 00     container offset 16 from the start of the blob
00 00 01 00 02 00 06 00 0a 00 0e 00 0f 00 10 00
                array values 0, 1, 2, 6, 10, 14, 15, 16
```

The 90-minute payload decodes similarly with cardinality minus one 3 and values
`0, 1, 14, 15`.

Roaring can serialize the same set with different container layouts. Consumers
**MUST** compare decoded integer sets, not Base64 text. Cache keys **MUST NOT**
assume byte-stable re-indexing.

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
| `confirmation_mode` | string | **Yes** | `auto` (confirmed immediately) or `manual` (requires business approval; the business **SHOULD** respond within 24 hours). If the booking advertises `expires_at` and the business does not confirm before that deadline, the booking transitions to `canceled` per [Booking Expiry](booking.md#booking-expiry). |
| `requires_payment` | boolean | **Yes** | Whether this service requires any payment. |
| `payment_timing` | string | Conditional | **REQUIRED** when `requires_payment` is `true`. One of: `at_booking`, `at_service`, `deposit_required`. |

`ServicePolicies` covers booking lifecycle timing only. It does not declare
minimum age, audience tiers, or merchant-mandated checkboxes. For mandatory
acceptances, policy links, and eligibility enforcement, see
[UCP-Native merchant policy parity](../deployment-modes/ucp-native.md#merchant-policy-parity-and-eligibility-ucp-overlay)
and service [`links`](#links).

---

## Links

Typed links to policy and information pages. Platforms **SHOULD** surface these
before the buyer confirms.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | **Yes** | Well-known values include `cancellation_policy`, `rescheduling_policy`, `terms_of_service`, `privacy_policy`, `waiver`, `faq`. |
| `url` | string | **Yes** | URL to the linked page. |
| `title` | string | No | Optional display text. |

Service `links[]` complement provider-level links. They are hints for display;
mandatory acceptance and waivers that require affirmative buyer action are
enforced through UCP checkout escalation or booking `requires_action`, not
through a separate acceptance field on the service object.

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
        "version": "2026-08-20",
        "capabilities": {
          "dev.usp-protocol.services.catalog": [
            { "version": "2026-08-20" }
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
            "summary": "Good availability next week on Tuesday afternoon and Wednesday morning.",
            "generated_at": "2026-03-11T08:00:00-04:00",
            "valid_until": "2026-03-18T08:00:00-04:00",
            "next_available_date": "2026-03-17",
            "slot_bitmaps": [
              {
                "duration": "PT60M",
                "starts_at": "2026-03-17T09:00:00-04:00",
                "start_interval": "PT30M",
                "slot_count": 17,
                "encoding": "roaring32-portable-base64",
                "bitmap": "OjAAAAEAAAAAAAcAEAAAAAAAAQACAAYACgAOAA8AEAA="
              }
            ]
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
        "version": "2026-08-20",
        "capabilities": {
          "dev.usp-protocol.services.catalog": [
            { "version": "2026-08-20" }
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
        "version": "2026-08-20",
        "capabilities": {
          "dev.usp-protocol.services.catalog": [
            { "version": "2026-08-20" }
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

A conforming implementation of `dev.usp-protocol.services.catalog` **MUST**:

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
