---
title: Discovery Registry
description: USP optional discovery registry for cold-start business discovery, search operations, and governance.
---

# Discovery Registry (Optional)

**Capability:** `dev.usp.discovery.registry` (optional extension)

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
| `categories` | Array[string] | **Yes** | Business categories for search and filtering. |
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
      "categories": ["wellness", "beauty", "fitness"],
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
        "version": "2026-08-14",
        "capabilities": {
          "dev.usp.discovery.registry": [
            { "version": "2026-08-14" }
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
        "categories": ["wellness", "beauty", "fitness"],
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

---

## Business Search -- `POST /registry/search_business`

Search for USP-enabled businesses by location, vertical, category, or keyword.

### Search Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `location` | object | No | Geographic filter: `coordinates` (`{lat, lng}`) and `radius_km` (kilometers). See [Filter Matching Semantics](#filter-matching-semantics). |
| `verticals` | Array[string] | No | Filter by service verticals (OR within field). |
| `categories` | Array[string] | No | Filter by business categories (OR within field). |
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
      "categories": ["wellness"],
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
        "version": "2026-08-14",
        "capabilities": {
          "dev.usp.discovery.registry": [
            { "version": "2026-08-14" }
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
          "categories": ["wellness", "beauty", "fitness"],
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
          "categories": ["wellness", "beauty"],
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
| `categories` | Array[string] | No | Filter by service categories (IDs matched against catalog service `categories[].id`; OR within field). |
| `query` | string | No | Free-text search across service names, descriptions, and categories. |
| `price_range` | object | No | `{min, max, currency, match?}` -- amounts in minor currency units. See [Filter Matching Semantics](#filter-matching-semantics). |
| `duration_range` | object | No | `{min_minutes, max_minutes, match?}`. See [Filter Matching Semantics](#filter-matching-semantics). |
| `context` | object | No | Localization hints: `locale` (BCP 47) and `currency` (ISO 4217). |
| `pagination` | object | No | Cursor-based pagination. |

!!! warning "At Least One Filter Required"
    The request **MUST** contain at least one search filter. A request containing only `pagination` and/or `context` is invalid.

=== "Request"

    ```json
    {
      "location": {
        "coordinates": { "lat": 40.7484, "lng": -73.9967 },
        "radius_km": 10
      },
      "verticals": ["appointment"],
      "categories": ["wellness"],
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
        "version": "2026-08-14",
        "capabilities": {
          "dev.usp.discovery.registry": [
            { "version": "2026-08-14" }
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
          "category": "wellness",
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
            "next_available_date": "2026-03-15"
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
          "category": "wellness",
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
          "last_indexed_at": "2026-03-14T07:30:00Z"
        }
      ],
      "pagination": { "cursor": "cursor_svc_xyz", "has_more": true }
    }
    ```

!!! tip "Indexing Strategy"
    Registries **SHOULD** index services from registered businesses by subscribing to catalog changes via [feed subscriptions](service-catalog.md#feed-subscriptions-post-servicesfeedsubscriptions) where the business supports them. For businesses without feed subscriptions, registries **SHOULD** re-index at most every 24 hours. Registry search results are **non-authoritative snapshots** -- platforms **MUST** fetch the business's live profile and [catalog](service-catalog.md) for booking-time decisions. When present on the indexed catalog service, registries **SHOULD** pass through `availability_hint` ([Availability Hint](service-catalog.md#availability-hint)) on each result; platforms **MUST NOT** treat it as authoritative or use it as a hard availability filter. `ServiceSearchResult.category` is a flat string projected from the catalog primary `categories[]` entry (pick order: primary `name`, else primary `value`, else primary `id`, else first entry `value`, else service `type`).

---

## Filter Matching Semantics

Filters are hard constraints (yes/no). Ranking and free-text `query` scoring **MAY** differ across registries; match predicates **MUST** follow this section. Canonical schema descriptions (with worked examples) live in [`schemas/registry.json`](../../schemas/registry.json) (`PriceRangeFilter`, `DurationRangeFilter`, `RangeMatchMode`, `RegistrySearchLocation`).

**Composition**

- Distinct filter fields combine with **AND**.
- `verticals[]` and `categories[]` use **OR within the field** (match any listed value).
- Zero matches **MUST** return HTTP 200 with an empty result array. Requests with no real search filter **MUST** return `validation_error`.

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

Worked duration example: service offered **30–90 min**, filter `{ min_minutes: 60, max_minutes: 60 }` → `overlap` yes, `contained` no, `contains` yes, `equals` no.

Worked price example: service **$50–$150**, filter `{ min: 8000, max: 10000 }` (minor units) → `overlap` yes, `contained` no, `contains` yes, `equals` no.

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
