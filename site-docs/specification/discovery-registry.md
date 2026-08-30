---
title: Discovery Registry
description: USP optional discovery registry for cold-start business discovery, search operations, and governance.
---

# Discovery Registry (Optional)

**Capability:** `dev.usp-protocol.discovery.registry` (optional extension)

This section defines **catalog discovery** via an optional registry: how a platform finds USP-enabled businesses and services when it does not already know a business's domain. **Profile discovery** (fetching `/.well-known/usp` or `/.well-known/ucp` for a known business) is defined in the Standalone and UCP-Native deployment mode pages. See [Specification Overview - Terminology](index.md#terminology) for normative definitions of catalog discovery, profile discovery, and platform onboarding.

Once a business is known, platforms fetch its profile (`/.well-known/usp` in Standalone Mode or `/.well-known/ucp` in UCP-Native Mode). This section defines an optional registry mechanism for the **cold-start problem**: how does a platform discover USP-enabled businesses when it does not yet have a domain?

A USP registry is a centralized or federated **directory** that maintains a searchable list of USP-enabled businesses, regardless of their deployment mode. Registries enable platforms to discover businesses by location, vertical, category, or keyword.

**Registry operations are not platform onboarding.** Registering a business in a discovery registry is a **directory listing** (publication of search metadata and a `profile_url`). It is **not** credential exchange, OAuth/DCR, checkout-path binding, or any other platform-business relationship setup. Those activities are **platform onboarding** and occur out-of-band.

!!! note "Independence"
    Registries are **independent** from USP-enabled businesses and from deployment mode. Multiple registries **MAY** coexist (federated model). A business **MAY** register with multiple registries.

---

## Business Registration -- `POST /registry/businesses`

Registers a business in the discovery registry.

### Registration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `profile_url` | string (URL) | **Yes** | The URL of the business's USP profile (`/.well-known/usp` or `/.well-known/ucp`). |
| `deployment_mode` | string | **Yes** | **MUST** be `standalone` or `ucp_native`. |
| `name` | string | **Yes** | Human-readable business name. |
| `description` | string | No | Brief description for discovery cards and search snippets. |
| `verticals` | Array[string] | **Yes** | Service verticals offered (e.g., `appointment`, `group`). |
| `categories` | Array[string] | **Yes** | Opaque business category IDs for search and filtering. Values are IDs, not display labels. |
| `location` | object | Conditional | `{address, coordinates: {lat, lng}}`. **REQUIRED** for businesses offering `at_business_location` or `hybrid` services. **MAY** be omitted for virtual-only businesses. |
| `timezone` | string | **Yes** | IANA timezone identifier (e.g., `America/New_York`). |

!!! warning "Profile Validation"
    The registry **MUST** validate that `profile_url` is reachable and returns a valid USP or UCP profile before accepting the registration. Registration failures **MUST** be reported using standard error codes (`profile_unreachable`, `validation_error`).

=== "Request"

    ```json
    {
      "profile_url": "https://sunrisewellness.com/.well-known/usp",
      "deployment_mode": "standalone",
      "name": "Sunrise Wellness Studio",
      "description": "Full-service wellness studio offering massage, facials, and yoga classes.",
      "verticals": ["appointment", "group"],
      "categories": ["cat_wellness", "cat_beauty", "cat_fitness"],
      "location": {
        "address": "123 Main St, New York, NY 10001",
        "coordinates": { "lat": 40.7484, "lng": -73.9967 }
      },
      "timezone": "America/New_York"
    }
    ```

=== "Response"

    ```json
    {
      "usp": {
        "version": "2026-08-20",
        "capabilities": {
          "dev.usp-protocol.discovery.registry": [
            { "version": "2026-08-20" }
          ]
        }
      },
      "registration": {
        "id": "reg_sunrise_001",
        "profile_url": "https://sunrisewellness.com/.well-known/usp",
        "deployment_mode": "standalone",
        "name": "Sunrise Wellness Studio",
        "description": "Full-service wellness studio offering massage, facials, and yoga classes.",
        "verticals": ["appointment", "group"],
        "categories": ["cat_wellness", "cat_beauty", "cat_fitness"],
        "location": {
          "address": "123 Main St, New York, NY 10001",
          "coordinates": { "lat": 40.7484, "lng": -73.9967 }
        },
        "timezone": "America/New_York",
        "status": "active",
        "created_at": "2026-03-14T10:00:00Z"
      }
    }
    ```

!!! tip "Envelope Scope"
    The `usp` envelope in registry responses describes the **registry's own** protocol and capability declaration, not the registered business's capabilities.

Business category IDs are registry filter tokens, not a universal taxonomy. A registry **MUST** preserve registered `categories[]` values in `RegistryEntry.categories`. Every returned ID **MUST** be accepted by the business-search `categories[]` filter and match that entry when all other filters are unchanged.

---

## Business Search -- `POST /registry/search_business`

Search for USP-enabled businesses by location, vertical, category, or keyword.

### Search Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `location` | object | No | Geographic filter: `coordinates` (`{lat, lng}`) and `radius_km` (kilometers). See [Filter Matching Semantics](#filter-matching-semantics). |
| `verticals` | Array[string] | No | Filter by service verticals (OR within field). |
| `categories` | Array[string] | No | Business category IDs, not display labels (OR within field, exact case-sensitive matching). |
| `query` | string | No | Free-text search across business names and categories. |
| `deployment_mode` | string | No | Filter by `standalone` or `ucp_native`. |
| `context` | object | No | Localization hints: `locale` (BCP 47) and `currency` (ISO 4217). |
| `pagination` | object | No | Cursor-based pagination. |

!!! warning "At Least One Filter Required"
    The request **MUST** contain at least one search filter (`location`, `verticals`, `categories`, `query`, or `deployment_mode`). A request containing only `pagination` and/or `context` is invalid and **MUST** be rejected with `validation_error`.

Search operations matching no results **MUST** return HTTP 200 with an empty `businesses[]` array (not an error). Filter matching follows [Filter Matching Semantics](#filter-matching-semantics).

=== "Request"

    ```json
    {
      "location": {
        "coordinates": { "lat": 40.7484, "lng": -73.9967 },
        "radius_km": 10
      },
      "verticals": ["appointment"],
      "categories": ["cat_wellness"],
      "query": "massage",
      "deployment_mode": "standalone",
      "context": { "locale": "en-US", "currency": "USD" },
      "pagination": { "limit": 20, "cursor": null }
    }
    ```

=== "Response"

    ```json
    {
      "usp": {
        "version": "2026-08-20",
        "capabilities": {
          "dev.usp-protocol.discovery.registry": [
            { "version": "2026-08-20" }
          ]
        }
      },
      "businesses": [
        {
          "id": "reg_sunrise_001",
          "profile_url": "https://sunrisewellness.com/.well-known/usp",
          "deployment_mode": "standalone",
          "name": "Sunrise Wellness Studio",
          "description": "Full-service wellness studio offering massage, facials, and yoga classes.",
          "verticals": ["appointment", "group"],
          "categories": ["cat_wellness", "cat_beauty", "cat_fitness"],
          "location": {
            "address": "123 Main St, New York, NY 10001",
            "coordinates": { "lat": 40.7484, "lng": -73.9967 }
          },
          "timezone": "America/New_York",
          "status": "active",
          "created_at": "2026-03-01T10:00:00Z"
        },
        {
          "id": "reg_serenity_002",
          "profile_url": "https://serenityspa.example.com/.well-known/usp",
          "deployment_mode": "standalone",
          "name": "Serenity Spa & Massage",
          "description": "Boutique spa and massage therapy in Manhattan.",
          "verticals": ["appointment"],
          "categories": ["cat_wellness", "cat_beauty"],
          "location": {
            "address": "456 Oak Ave, New York, NY 10002",
            "coordinates": { "lat": 40.7521, "lng": -73.9812 }
          },
          "timezone": "America/New_York",
          "status": "active",
          "created_at": "2026-03-05T14:30:00Z"
        }
      ],
      "pagination": { "cursor": "cursor_abc123", "has_more": true }
    }
    ```

---

## Service Search -- `POST /registry/search_services`

Search the registry for specific **services** offered by registered businesses. This enables more granular discovery -- rather than finding businesses and then querying each one, the platform can directly search across all registered businesses' services.

### Search Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `location` | object | No | Geographic filter: `coordinates` (`{lat, lng}`) and `radius_km` (kilometers). See [Filter Matching Semantics](#filter-matching-semantics). |
| `verticals` | Array[string] | No | Filter by service verticals (OR within field). |
| `categories` | Array[string] | No | Service category IDs, not display labels (OR within field, exact case-sensitive matching against `ServiceSearchResult.category_ids`). |
| `query` | string | No | Free-text search across service names, descriptions, and categories. |
| `price_range` | object | No | `{min, max, currency, match?}` -- amounts in minor currency units. See [Filter Matching Semantics](#filter-matching-semantics). |
| `duration_range` | object | No | `{min_minutes, max_minutes, match?}`. See [Filter Matching Semantics](#filter-matching-semantics). |
| `desired_service_time_ranges` | Array[object] | No | Buyer time preferences for **availability ranking only** (not a hard filter). See [Availability ranking](#availability-ranking). |
| `prefer_sooner_availability_slots` | boolean | No | When true (default), earlier acceptable openings rank above later ones within the availability signal. When false, the registry default ordering does not apply soonness. See [Availability ranking](#availability-ranking). |
| `context` | object | No | Localization hints: `locale` (BCP 47) and `currency` (ISO 4217). |
| `pagination` | object | No | Cursor-based pagination. |

!!! warning "At Least One Filter Required"
    The request **MUST** contain at least one search filter (`location`, `verticals`, `categories`, `query`, `price_range`, or `duration_range`). `desired_service_time_ranges` and `prefer_sooner_availability_slots` are ranking context only and do **not** satisfy this rule. A request containing only those fields plus `pagination` and/or `context` **MUST** be rejected with `validation_error`.

=== "Request"

    ```json
    {
      "location": {
        "coordinates": { "lat": 40.7484, "lng": -73.9967 },
        "radius_km": 10
      },
      "verticals": ["appointment"],
      "categories": ["cat_wellness"],
      "query": "deep tissue massage",
      "price_range": { "min": 5000, "max": 20000, "currency": "USD", "match": "overlap" },
      "duration_range": { "min_minutes": 30, "max_minutes": 90, "match": "overlap" },
      "context": { "locale": "en-US", "currency": "USD" },
      "pagination": { "limit": 20, "cursor": null }
    }
    ```

=== "Response"

    ```json
    {
      "usp": {
        "version": "2026-08-20",
        "capabilities": {
          "dev.usp-protocol.discovery.registry": [
            { "version": "2026-08-20" }
          ]
        }
      },
      "services": [
        {
          "service_id": "svc_deep_tissue_60",
          "service_name": "Deep Tissue Massage - 60 min",
          "business": {
            "id": "reg_sunrise_001",
            "profile_url": "https://sunrisewellness.com/.well-known/usp",
            "deployment_mode": "standalone",
            "name": "Sunrise Wellness Studio"
          },
          "category": "Wellness",
          "category_ids": ["cat_wellness"],
          "duration_minutes": 60,
          "pricing": {
            "model": "fixed",
            "amount": 12000,
            "currency": "USD"
          },
          "location": {
            "address": "123 Main St, New York, NY 10001",
            "coordinates": { "lat": 40.7484, "lng": -73.9967 }
          },
          "timezone": "America/New_York",
          "last_indexed_at": "2026-03-14T08:00:00Z",
          "availability_hint": {
            "summary": "Good availability this week, especially Tuesday and Wednesday afternoons.",
            "generated_at": "2026-03-14T07:00:00Z",
            "valid_until": "2026-03-15T07:00:00Z",
            "next_available_date": "2026-03-15",
            "slot_bitmaps": [
              {
                "duration": "PT60M",
                "starts_at": "2026-03-15T09:00:00-05:00",
                "start_interval": "PT30M",
                "slot_count": 17,
                "encoding": "roaring32-portable-base64",
                "bitmap": "OjAAAAEAAAAAAAcAEAAAAAAAAQACAAYACgAOAA8AEAA="
              }
            ]
          },
          "rank_signals": {
            "relevance": 0.91,
            "coverage": null,
            "density": 0.47,
            "soonness": 0.86,
            "hint_usable": true
          }
        },
        {
          "service_id": "svc_massage_90",
          "service_name": "Therapeutic Deep Tissue - 90 min",
          "business": {
            "id": "reg_serenity_002",
            "profile_url": "https://serenityspa.example.com/.well-known/usp",
            "deployment_mode": "standalone",
            "name": "Serenity Spa & Massage"
          },
          "category": "Wellness",
          "category_ids": ["cat_wellness"],
          "duration_minutes": 90,
          "pricing": {
            "model": "variable",
            "currency": "USD",
            "price_range": { "min": 15000, "max": 22000 }
          },
          "location": {
            "address": "456 Oak Ave, New York, NY 10002",
            "coordinates": { "lat": 40.7521, "lng": -73.9812 }
          },
          "timezone": "America/New_York",
          "last_indexed_at": "2026-03-14T07:30:00Z",
          "rank_signals": {
            "relevance": 0.78,
            "coverage": null,
            "density": null,
            "soonness": null,
            "hint_usable": false
          }
        }
      ],
      "pagination": { "cursor": "cursor_svc_xyz", "has_more": true }
    }
    ```

!!! tip "Indexing Strategy"
    Registries **SHOULD** index services from registered businesses by subscribing to catalog changes via [feed subscriptions](service-catalog.md#feed-subscriptions-post-servicesfeedsubscriptions) where the business supports them. For businesses without feed subscriptions, registries **SHOULD** re-index at most every 24 hours. Registry search results are **non-authoritative snapshots** -- platforms **MUST** fetch the business's live profile and [catalog](service-catalog.md) for booking-time decisions. When present on the indexed catalog service, registries **SHOULD** pass through `availability_hint` ([Availability Hint](service-catalog.md#availability-hint)) on each result; platforms **MUST NOT** treat it as authoritative or use it as a hard availability filter. `ServiceSearchResult.category` is display text projected from the catalog primary `categories[]` entry (pick order: primary `name`, else primary `value`, else primary `id`, else first entry `value`, else service `type`) and is not a filter token.

Every service search result **MUST** include `category_ids`, projected from indexed catalog `categories[].id` values. The array **MAY** be empty when the service has no category IDs. Every emitted ID **MUST** be accepted by the service-search `categories[]` filter and match that service when all other filters are unchanged.

When the registry applies availability ranking, or when the request carries time preferences, every `ServiceSearchResult` **MUST** include `rank_signals` so agents can inspect or re-order the returned page, including hits with no hint or a summary-only hint. See [Availability ranking](#availability-ranking).

---

## Availability ranking

Registries **MAY** use `availability_hint` from indexed catalog services as a bounded secondary ranking signal after hard-filter recall. Baseline relevance (text, geography, and other registry-specific signals) **MUST** remain dominant.

USP does not standardize how a registry derives an availability ranking key. Projection details, formulas, horizons, weights, duration selection, and score composition are registry-specific. What is standardized is the request shape, the observable guarantees, and the response signals below.

### Request fields

A platform or agent **MAY** convert a buyer's preferred start time or time ranges into `desired_service_time_ranges` on `POST /registry/search_services`. This field is ranking context. It is **not** a hard filter and does **not** satisfy the at-least-one-filter rule.

The request **MAY** include `prefer_sooner_availability_slots` (boolean, default `true`). When true, earlier acceptable available starts rank above later acceptable starts within the availability signal. When false, time direction contributes no ranking preference. A preference for a future period **MUST** be expressed with `desired_service_time_ranges`, not by interpreting `false` as "later is better."

Each element **MUST** be exactly one of:

```json
{ "at": "2026-03-14T10:00:00-04:00" }
```

```json
{ "start": "2026-03-14T10:00:00-04:00", "end": "2026-03-14T11:30:00-04:00" }
```

```json
{ "start": "2026-03-14T16:00:00-04:00" }
```

- `at` is a moment: the first candidate start at or after that instant.
- `start` and `end` is a bounded range (inclusive bounds; `end` is the latest acceptable **start**, not the latest acceptable occupancy).
- `start` alone is open-ended, bounded by what the service actually published.

All bounds are instants (RFC 3339), and equal instants with different offsets **MUST** compare equal. Agents **SHOULD** use a bounded range rather than a moment when the buyer named a strict latest acceptable start, because a moment resolves to the next candidate start and can fall after that limit. Date-only intent **SHOULD** be normalized in the service timezone. An open-ended preference **MUST NOT** be read as a claim of availability beyond the horizon a producer published.

### Observable guarantees

- Availability data is non-authoritative ranking context only. A hint that is missing, summary-only, expired, malformed, internally inconsistent, or non-overlapping **MUST NOT** remove a hit that hard-filter recall admitted, and **MUST NOT** be used as a hard time filter. Platforms **MUST** confirm live [availability](availability.md) before claiming that a time can or cannot be booked.
- Unusable or absent availability data is neutral, never favorable. Registries **MUST NOT** convert unknown availability into maximum soonness or into an earliest-opening claim, and **MUST NOT** parse a missing or empty `next_available_date` as epoch 0.
- Freshness decides usability, not quality. A hint is usable before a producer-declared `valid_until`, or under a registry-documented fallback validity policy when `valid_until` is absent. While a hint remains usable, its `generated_at` age **MUST NOT** continuously decay its availability contribution or the hit's final rank.
- Registries **MUST NOT** order results by raw counts of hinted openings, because raw counts reward a longer published horizon, a finer `start_interval`, or more duration variants without proving a better buyer match.
- Ranking **MUST** run before pagination. The scoring instant and index snapshot **MUST** stay frozen across a cursor sequence, and remaining ties **MUST** break deterministically, for example by ascending `service_id`.
- A registry that advertises availability ranking **SHOULD** document its availability inputs, normalization ranges, the maximum contribution availability can make relative to baseline relevance, and its refresh cadence. A registry **SHOULD NOT** advertise availability ranking unless it refreshes hints inside their validity policy; the conforming alternative is neutral availability ranking, not ranking from stale snapshots.

### Rank signals on each result

When a registry applies availability ranking, or when the request carries `desired_service_time_ranges` and/or `prefer_sooner_availability_slots`, every `ServiceSearchResult` in that response **MUST** include `rank_signals`, including hits with no hint and hits with a summary-only hint. When present, `rank_signals` **MUST** contain all five members:

| Field | Type | Meaning |
| --- | --- | --- |
| `relevance` | number in `[0, 1]` | Match apart from availability, including text, categories, geography, and registry signals. Registry-specific scale; compare only within this response. |
| `coverage` | number in `[0, 1]` or `null` | How much of the requested time has a hinted opening. `1` is full coverage, `0` is known non-overlap in the structured snapshot, and `null` is not computed: no time preference, no usable structured hint, or requested time outside what the service published. |
| `density` | number in `[0, 1]` or `null` | Share of all represented candidate starts that are open. `0` is a sampled empty grid; `null` is unknown. It does not express soonness or requested-window fit. |
| `soonness` | number in `[0, 1]` or `null` | Normalized delay to the earliest acceptable opening, relative to the request anchor and the registry's documented horizon. `0` includes no acceptable opening inside the horizon; `null` is unknown. It remains populated when `prefer_sooner_availability_slots` is `false`. |
| `hint_usable` | boolean | Whether the structured snapshot passed validity and consistency checks. `false` means availability was unknown for ranking (omitted hint, summary-only hint, expired snapshot, malformed bitmap, or invariant failure), not a worse service. |

`rank_signals` **MUST NOT** include a continuous freshness, age-decay, or confidence score. Agents that need expiry data read `availability_hint.generated_at`, `availability_hint.valid_until`, and `last_indexed_at`. Values **MUST NOT** be compared across registries, requests, snapshots, or scoring instants.

### Response-state semantics

An agent that sent time preferences **MUST NOT** treat a missing or summary-only hint as proof that the requested time cannot be satisfied. That state means the registry had no structured evidence; live availability remains the authority.

| Response state | Meaning | Required client handling |
| --- | --- | --- |
| `rank_signals` omitted | The registry did not apply availability ranking on this response. | Do not infer availability from the response ordering. |
| `hint_usable: false`, with `coverage`, `density`, and `soonness` all `null` | Unknown: omitted hint, summary-only hint, expired or malformed structured hint, or invariant failure. | Keep the hit. **MUST NOT** be treated as unavailable, as maximum soonness, or as a failed time match. |
| `hint_usable: true` and `coverage: null` | Coverage was not computed even though the snapshot was usable: no time preference was sent, or the requested time falls outside what this service published. `density` and `soonness` **MAY** still be populated. | Do not read this as a time match or a time mismatch. |
| `hint_usable: true` and `coverage: 0` | Known non-overlap on this registry's structured snapshot. | Not a hard exclusion. Confirm with live availability before telling a user the time cannot be booked. |
| `hint_usable: true` and `coverage` in `(0, 1]` | Structured evidence that the requested time overlaps hinted openings. | Still confirm with live availability before booking. |
| Mixed states within one page | Some hits had usable structured evidence and others did not. | Time preferences remain ranking context only; comparing a known value against a `null` is not a ranking or exclusion decision. |

`null` means unknown. `0` means known empty or known non-overlap. Agents **MUST NOT** collapse those states when re-sorting, and `summary` **MUST NOT** be turned into `coverage`, `density`, or `soonness`.

Agents **MAY** re-order the current page using these fields but **SHOULD** keep `hint_usable: false` hits. Page-local shuffling is not a global rerank: later pages were selected under the registry's original order, so a different global policy requires a new search.

---

## Filter Matching Semantics

Filters are hard constraints (yes/no). Ranking and free-text `query` scoring **MAY** differ across registries; match predicates **MUST** follow this section. Canonical schema descriptions (with worked examples) live in [`schemas/registry.json`](https://github.com/wix/universal-scheduling-protocol/blob/master/schemas/registry.json) (`PriceRangeFilter`, `DurationRangeFilter`, `RangeMatchMode`, `RegistrySearchLocation`).

**Composition**

- Distinct filter fields combine with **AND**.
- `verticals[]` and `categories[]` use **OR within the field** (match any listed value).
- Zero matches **MUST** return HTTP 200 with an empty result array. Requests with no real search filter **MUST** return `validation_error`.

**Category IDs (`categories`)**

- Both registry search operations use opaque category IDs, not display labels. Matching is exact and case-sensitive.
- Business search matches against `RegistryEntry.categories`.
- Service search matches against `ServiceSearchResult.category_ids`. `ServiceSearchResult.category` is display text and **MUST NOT** be interpreted as a filter token.
- Every emitted category ID **MUST** round-trip through that operation's `categories[]` filter and match the same result when all other filters are unchanged.

**Geographic (`location`)**

- `radius_km` is kilometers.
- Businesses or services with no coordinates (virtual/phone only) **MUST** be excluded when any location filter is present, and **SHOULD** appear only when no geographic filter is applied (search as well as registration).

**Range filters (`price_range`, `duration_range`)**

Optional `match` compares service interval **S** to filter interval **F**:

| `match` | Predicate | Default |
|---------|-----------|---------|
| `overlap` | S ∩ F ≠ ∅ | **Yes** (when `match` omitted) |
| `contained` | S ⊆ F | |
| `contains` | S ⊇ F | |
| `equals` | S = F | |

Omitted bounds on F are unbounded on that side. Point intervals (min = max) are valid.

Worked duration example: service offered **30-90 min**, filter `{ min_minutes: 60, max_minutes: 60 }` results in `overlap` yes, `contained` no, `contains` yes, `equals` no.

Worked price example: service **$50-$150**, filter `{ min: 8000, max: 10000 }` (minor units) results in `overlap` yes, `contained` no, `contains` yes, `equals` no.

**Building S (duration)**

- Fixed duration → `[d, d]` minutes.
- Range duration → `[min, max]` minutes.
- `duration.undetermined: true` (or no indexable duration) → excluded by any `duration_range` filter; **MAY** appear when no duration filter is set.

**Building S (price) and currency**

- Matching is **within-currency only** (no FX).
- Resolved match currency: `price_range.currency` if present; else `context.currency`; else `validation_error`. When both differ, `price_range.currency` wins for matching.
- `pricing.model: free` → amount **0**. Fixed amount → `[amount, amount]`. Published variable `price_range` → that interval. No indexable price → exclude when a price filter is present.

---

## Get Registration -- `GET /registry/businesses/{id}`

Returns the full registration record for a previously registered business.

| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| `id` | string | path | Registration identifier (`reg_*`). |

The response body matches the `registration` object from [Business Registration](#business-registration-post-registrybusinesses), wrapped in the standard `usp` envelope. If no registration exists for `id`, the registry **MUST** return `404 Not Found` with Problem Details.

---

## Update Registration -- `PUT /registry/businesses/{id}`

Updates an existing registration. The request body is the same as Business Registration (registration fields only; the path supplies `id`).

The registry **MUST** re-validate that `profile_url` is reachable and returns a valid profile when `profile_url` or `deployment_mode` changes. Successful responses return HTTP 200 with the updated `registration` object.

---

## Delete Registration -- `DELETE /registry/businesses/{id}`

Removes a business from the registry.

| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| `id` | string | path | Registration identifier (`reg_*`). |

On success the registry **MUST** return `204 No Content`. Registries **SHOULD** remove cached service metadata for the deleted business.

---

## Operations Summary

| Operation | Method | Path | Description |
|-----------|--------|------|-------------|
| Register Business | `POST` | `/registry/businesses` | Register a new business |
| Search Businesses | `POST` | `/registry/search_business` | Search by location, vertical, category |
| Search Services | `POST` | `/registry/search_services` | Search services across all registered businesses |
| Get Registration | `GET` | `/registry/businesses/{id}` | Get a specific registration record |
| Update Registration | `PUT` | `/registry/businesses/{id}` | Update an existing registration |
| Delete Registration | `DELETE` | `/registry/businesses/{id}` | Remove a business from the registry |

---

## Registry Governance

Registries are **independent** from USP-enabled businesses and from deployment mode.

- Multiple registries **MAY** coexist (federated model).
- A business **MAY** register with multiple registries.
- Registries **SHOULD** periodically validate that registered businesses still serve a valid profile at their declared `profile_url`.
- Registries indexing virtual-only businesses (no `location`) **MUST** exclude them from location-filtered search results and **SHOULD** return them only when no geographic filter is applied.
