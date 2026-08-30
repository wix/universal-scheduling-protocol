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
| `prefer_sooner_availability_slots` | boolean | No | When true (default), earlier acceptable openings rank above later ones within the availability signal. When false, ranking uses coverage or density without soonness. |
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

When the registry applies availability ranking, every `ServiceSearchResult` **MUST** include `rank_signals` so agents can inspect or re-order the returned page. See [Availability ranking](#availability-ranking).

---

## Availability ranking

Registries **MAY** use `availability_hint.slot_bitmaps` from indexed catalog services as a bounded secondary ranking signal after hard-filter recall. Baseline relevance (text, geography, and other registry-specific signals) **MUST** remain dominant.

### How a search request uses it

A platform or agent **MAY** convert a buyer's preferred start time or time ranges into `desired_service_time_ranges` on `POST /registry/search_services`. This field is ranking context. It is **not** a hard filter and does **not** satisfy the at-least-one-filter rule.

The request **MAY** include `prefer_sooner_availability_slots` (boolean, default `true`). When true, earlier acceptable available starts rank above later acceptable starts within the availability signal. When false, time direction contributes no ranking preference. A preference for a future period **MUST** be expressed with `desired_service_time_ranges`, not by interpreting `false` as "later is better."

**Recommended intent mapping for agents:**

| Consumer intent | Recommended request representation | Soonness flag |
| --- | --- | --- |
| First available, "book ASAP", or "whenever is soonest" | Open `{ "start": "<now>" }` | Omit or `true` |
| At a specific time where grid rounding is acceptable | Moment `{ "at": "<instant>" }` | Usually `true`; irrelevant for one represented tick |
| At a specific time with tolerance | Bounded range from earliest through latest acceptable start | `true` if earlier is preferred, otherwise `false` |
| During one window | One bounded range | `true` if earlier in the window is preferred, otherwise `false` |
| During any of several windows | One bounded element per window | Set according to whether earlier alternatives are preferred |
| On a calendar date without a stated time | Bounded range for valid starts that date in the service timezone | `true` unless time order is irrelevant |
| Starting no earlier than a future boundary | Open `{ "start": "<earliest acceptable instant>" }` | `true` for first opening after it, otherwise `false` |
| Before a deadline | Bounded range from earliest acceptable start through deadline | Usually `true` |
| Exact duration plus time intent | Exact `duration_range` plus moment, bounded, or open preference | Set from the time wording |
| Flexible duration plus time intent | Acceptable `duration_range`; score each eligible ruler independently | Set from the time wording |
| Recurring desired windows | Expand each occurrence in the searched horizon into a bounded element | `false` unless earlier occurrences are preferred |
| Prefer a later known period | Encode that future boundary or window directly | Usually `true` within that period |
| No time preference, sooner is generally better | Omit `desired_service_time_ranges` | Omit or `true` |
| No time preference, no soonness preference | Omit `desired_service_time_ranges` | `false` |
| Ambiguous time wording or unknown timezone | Ask for clarification | Do not fabricate ranges |

Agents **SHOULD NOT** use a moment when the consumer named a strict latest
acceptable start, because ceiling could move past that limit. Date-only intent
**SHOULD** be normalized in the service timezone and sent as RFC 3339 instants
with offsets. Open ranges stop at each bitmap horizon.

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
- `start` and `end` is a bounded range (inclusive bounds; `end` is the latest acceptable **start**).
- `start` alone is open-ended, clipped to each bitmap's `slot_count`.

The registry **MUST** project intent onto each service bitmap's own ruler. Two services with different `starts_at` or `start_interval` **MUST NOT** share one intent bitmap.

**Projection.** For an `AvailabilitySlotBitmap` with origin `S`, interval `I`,
and `slot_count` `N`, define `start(i) = S + i * I` for `i` in `[0, N)`. All
comparisons use instants.

1. Start with an empty intent set.
2. For each preference, compute a half-open index range `[lo, hi)`:
   - Moment `{ "at": T }`: `lo` is the first `i` whose start is at or after `T`; `hi=lo+1`. If none exists, contribute nothing.
   - Bounded `{ "start": A, "end": B }`: if `B<A`, contribute nothing. Otherwise `lo` is the first start at or after `A`, and `hi` is one past the final start at or before `B`. Clip both to `[0,N)`.
   - Open `{ "start": A }`: `lo` is the first start at or after `A`, and `hi=N`. If none exists, contribute nothing.
3. Union every range. Overlaps and duplicates **MUST NOT** be double-counted.
4. Decode the 1-bits as `available`.
5. Compute `intersection = available AND intent`.

**Scoring.** For each valid bitmap entry:

```text
density = |available| / slot_count
```

Density is normalized so longer horizons, finer grids, and extra duration
variants do not gain an artificial advantage. Registries **MUST NOT** use raw
opening counts.

When preferences are present, skip entries with empty projected intent and
define:

```text
coverage = |intersection| / |intent|
```

Use Roaring minimum on `available AND intent` (or on `available` when no
preferences) for soonness:

```text
earliest = minimum(available AND intent)    # preferences present
earliest = minimum(available)               # preferences absent

delay = max(0, earliest_start - anchor)
soonness = max(0, 1 - delay / H)
```

`H` is a positive, registry-documented soonness horizon (worked examples use 14 days). `anchor` is the earliest lower-bound instant in `desired_service_time_ranges`, or the search scoring instant when preferences are absent.

An empty candidate set has soonness `0`. Missing
`next_available_date` **MUST NOT** become epoch 0 or maximum soonness. The
registry ranks from the exact earliest set-bit instant and **SHOULD** reject a
hint for ranking when `next_available_date` does not equal the service-local
date of the earliest bit across all rulers.

When `desired_service_time_ranges` is present:

```text
prefer_sooner_availability_slots = true:  match_score = coverage * soonness
prefer_sooner_availability_slots = false: match_score = coverage
```

Compare duration entries by `match_score`, then by `density`; take the best eligible entry. **MUST NOT** add scores across durations.

Two services can both have coverage 1 while one opens tomorrow and the other
opens at the 14-day horizon. With the default flag, their soonness separates
them. With the flag false, both have match score 1 and density is the next
tie-break.

When `desired_service_time_ranges` is absent:

```text
prefer_sooner_availability_slots = true:  compare (soonness, density) lexicographically
prefer_sooner_availability_slots = false: compare density
```

Lexicographic comparison means any greater soonness wins before density is
examined. For example, `(0.90,0.10)` beats `(0.80,0.90)`. With equal soonness,
`(0.90,0.60)` beats `(0.90,0.20)`. With the flag false, density alone decides.

**Freshness cutout.** While a hint remains usable (before `valid_until`, or under a registry-documented policy when absent), its age **MUST NOT** decay `coverage`, `density`, `soonness`, or final rank. At or after the cutout the hint contributes neutral availability ranking data.

The registry **MUST** apply availability only after hard-filter recall. For a
worked magnitude with baseline and availability each normalized to `[0,1]`:

```text
final_score = baseline_score + 0.15 * availability_score
```

The `0.15` value is illustrative, not portable across relevance engines.
Registries that advertise availability ranking **MUST** document:

1. baseline score range;
2. availability score range;
3. maximum availability contribution in baseline units;
4. soonness horizon;
5. the baseline gap treated as clearly better.

The configuration **MUST** satisfy the dominance check: maximum availability
contribution is strictly smaller than the clearly-better relevance gap, so a
maximally available lower-relevance hit cannot overtake a clearly better
neutral-availability hit.

Missing, expired, malformed, inconsistent, or non-overlapping hints contribute
neutral availability data and **MUST** remain in the result set.

Availability ranking **SHOULD** only be advertised with a functioning refresh
path. Producers **SHOULD** refresh on change or before expiry. Registries
**SHOULD** ingest feeds and use the documented re-index fallback. An outdated
pipeline produces neutral availability, not old ranking.

Ranking **MUST** run before pagination. The scoring instant and index snapshot
**MUST** remain frozen across a cursor sequence. Ties **MUST** break
deterministically, for example by `service_id`.

**Rank signals on each result.** When availability ranking applies, every hit **MUST** include `rank_signals`:

| Field | Type | Meaning |
| --- | --- | --- |
| `relevance` | number in `[0, 1]` | Match apart from availability, including text, categories, geography, and registry signals. Compare only within this response. |
| `coverage` | number in `[0, 1]` or `null` | Share of represented buyer-time intent with a hinted opening. `1` is full overlap, `0` is known non-overlap, and `null` is not computed or unknown. |
| `density` | number in `[0, 1]` or `null` | Share of all represented ticks that are open. `0` is a sampled empty grid; `null` is unknown. It does not express soonness or requested-window fit. |
| `soonness` | number in `[0, 1]` or `null` | Normalized delay to the earliest acceptable opening. `0` includes no opening inside the horizon; `null` is unknown. It remains populated when the flag is false. |
| `hint_usable` | boolean | Whether the snapshot passed validity and consistency checks. `false` is unknown ranking data, not a worse service. |

`null` means unknown; `0` means known empty or known non-overlap. Agents
**MUST NOT** collapse the two. `rank_signals` **MUST NOT** include a continuous
freshness or age-decay score.

Agents **MAY** re-order the current page using these fields but **SHOULD** keep
unusable-hint hits. Page-local shuffling is not a global rerank, and values
**MUST NOT** be compared across registries, requests, or scoring instants.

**Worked request (bounded range).** On the [back massage example](service-catalog.md#the-example), a buyer wants a start between 10:00 and 11:30 inclusive:

```json
{
  "query": "back massage",
  "desired_service_time_ranges": [
    {
      "start": "2026-03-14T10:00:00-04:00",
      "end": "2026-03-14T11:30:00-04:00"
    }
  ]
}
```

```text
PT60M: intent={2,3,4,5}; available={0,1,2,6,10,14,15,16}
intersection={2}; coverage=1/4; density=8/17
earliest=2 at 10:00; anchor=10:00; delay=0; soonness=1
match_score=0.25

PT90M: intent={2,3,4,5}; available={0,1,14,15}
intersection={}; coverage=0; soonness=0

Select PT60M with match_score 0.25. Do not add duration scores.
```

A moment at 10:07 ceils to index 3 at 10:30 and has coverage 0 on the
PT60M ruler. An open preference from 16:00 is completed below.

### Reading it back

The buyer wants a 90-minute back massage sometime after 16:00:

```json
{
  "query": "back massage",
  "duration_range": {
    "min_minutes": 90,
    "max_minutes": 90,
    "match": "overlap"
  },
  "desired_service_time_ranges": [
    { "start": "2026-03-14T16:00:00-04:00" }
  ]
}
```

1. Hard filters include the service; the hint is not consulted for inclusion.
2. The exact 90-minute filter makes only the `PT90M` ruler eligible.
3. Open preference from 16:00 yields `intent={14,15}` after clipping to `N=16`.
4. Decoded `available={0,1,14,15}`.
5. `intersection={14,15}`, so `coverage=2/2=1`.
6. Earliest index 14 is 16:00. Anchor 16:00 gives delay 0 and `soonness=1`. The default flag gives `match_score=1`; `density=4/16=0.25` is only the next tie-break.
7. The scoring instant is before `valid_until`, so the hint is usable. `generated_at` age does not reduce rank.
8. The bounded availability key is mixed with baseline relevance. Under the illustrative 0.15 weight, perfect availability contributes at most 0.15 and cannot defeat a clearly better baseline hit under the dominance rule. Pagination uses the frozen order.
9. The result includes:

```json
"rank_signals": {
  "relevance": 0.82,
  "coverage": 1.0,
  "density": 0.25,
  "soonness": 1.0,
  "hint_usable": true
}
```

`relevance` is comparable only inside this response. Coverage 1 means both
represented acceptable starts are hinted open. Density 0.25 describes the full
ruler, not just the requested tail. Soonness 1 means the first acceptable
opening is at the anchor. `hint_usable=true` means the snapshot passed validity,
not that the service is intrinsically better.

### Intent projection edge cases

Unless noted, these vectors use:

```text
S = 2026-03-14T09:00:00-04:00
I = PT30M
N = 17
available = {0,1,2,6,10,14,15,16}
density = 8/17
H = 14 days = 336 hours
validity = usable
prefer_sooner_availability_slots = true
```

`E` is earliest matching index, `A` is anchor, `D` is delay, and `K` is the
availability rank key. A skipped ruler has no represented intent. A represented
intent with no overlap instead has known coverage and soonness `0`.

#### Moment projection

| Request | Complete result |
| --- | --- |
| On grid, `at=10:00` | `intent={2}`; `intersection={2}`; `coverage=1`; `density=8/17`; `E=2`; `A=10:00`; `D=0`; `soonness=1`; usable; `K=1` |
| Between ticks, `at=10:07` | `intent={3}`; `intersection={}`; `coverage=0`; `density=8/17`; no `E`; `A=10:07`; `soonness=0`; usable; `K=0`, then density |
| Before origin, `at=08:00` | `intent={0}`; `intersection={0}`; `coverage=1`; `density=8/17`; `E=0`; `A=08:00`; `D=1h`; `soonness=335/336`, about `0.997024`; usable; `K=335/336` |
| Final tick, `at=17:00` | `intent={16}`; `intersection={16}`; `coverage=1`; `density=8/17`; `E=16`; `A=17:00`; `D=0`; `soonness=1`; usable; `K=1` |
| After horizon, `at=17:01` | `intent={}`; density exists on the ruler but it is skipped; no `E`; `soonness=null`; usable hint with no eligible ruler; neutral key |

#### Bounded projection

The lower bound is ceiled, the inclusive upper bound is floored, and the
half-open index range is clipped to `[0,N)`.

| Request | Complete result |
| --- | --- |
| Aligned, 10:00 through 11:30 | `intent={2,3,4,5}`; `intersection={2}`; `coverage=1/4`; `density=8/17`; `E=2`; `A=10:00`; `D=0`; `soonness=1`; usable; `K=0.25` |
| Unaligned, 10:07 through 11:20 | `intent={3,4}`; `intersection={}`; `coverage=0`; `density=8/17`; no `E`; `A=10:07`; `soonness=0`; usable; `K=0`, then density |
| Single tick, 10:00 through 10:00 | `intent={2}`; `intersection={2}`; `coverage=1`; `density=8/17`; `E=2`; `A=10:00`; `D=0`; `soonness=1`; usable; `K=1` |
| No tick, 10:01 through 10:29 | `intent={}` because `lo=hi`; ruler skipped; neutral key |
| End before start, 12:00 through 11:00 | contributes no indices; ruler skipped; neutral key |
| Clipped left, 07:00 through 09:00 | `intent={0}`; `intersection={0}`; `coverage=1`; `density=8/17`; `E=0`; `A=07:00`; `D=2h`; `soonness=334/336`; usable; `K=334/336` |
| Clipped right, 17:00 through 19:00 | `intent={16}`; `intersection={16}`; `coverage=1`; `density=8/17`; `E=16`; `A=17:00`; `D=0`; `soonness=1`; usable; `K=1` |
| Spans both sides, 07:00 through 19:00 | `intent={0..16}`; intersection is `available`; `coverage=8/17`; `density=8/17`; `E=0`; `A=07:00`; `D=2h`; `soonness=334/336`; usable; `K=(8/17)*(334/336)` |

#### Open projection and union behavior

Preferences are unioned before intersection, so overlapping and duplicate
indices count once.

| Request | Complete result |
| --- | --- |
| Open from 08:00 | `intent={0..16}`; intersection is `available`; `coverage=8/17`; `density=8/17`; `E=0`; `A=08:00`; `D=1h`; `soonness=335/336`; usable; `K=(8/17)*(335/336)` |
| Open from 16:00 | `intent={14,15,16}`; full intersection; `coverage=1`; `density=8/17`; `E=14`; `A=16:00`; `D=0`; `soonness=1`; usable; `K=1` |
| Open from final tick 17:00 | `intent={16}`; full intersection; `coverage=1`; `density=8/17`; `E=16`; `soonness=1`; usable; `K=1` |
| Open after horizon 17:01 | `intent={}`; ruler skipped; neutral key |
| Disjoint moment 10:00 plus bounded 14:00 through 15:00 | `intent={2,10,11,12}`; `intersection={2,10}`; `coverage=2/4`; `density=8/17`; `E=2`; `A=10:00`; `D=0`; `soonness=1`; usable; `K=0.5` |
| Overlapping 09:30 through 10:30 plus duplicate 10:00 through 11:00 ranges | union `intent={1,2,3,4}`; `intersection={1,2}`; `coverage=2/4`; `density=8/17`; `E=1`; `A=09:30`; `D=0`; `soonness=1`; usable; `K=0.5` |
| Moment 10:00, bounded 14:00 through 15:00, open from 16:00 | `intent={2,10,11,12,14,15,16}`; `intersection={2,10,14,15,16}`; `coverage=5/7`; `density=8/17`; `E=2`; `A=10:00`; `D=0`; `soonness=1`; usable; `K=5/7` |

#### Bitmap occupancy and duration eligibility

| Case | Complete result |
| --- | --- |
| All-zero bitmap with represented intent | `available={}`; empty intersection; `coverage=0`; `density=0`; no `E`; `soonness=0`; usable; `K=0`; omit `next_available_date` |
| All-one ruler, bounded 10:00 through 11:30 | `available={0..16}`; `intent={2,3,4,5}`; full intersection; `coverage=1`; `density=1`; `E=2`; `A=10:00`; `D=0`; `soonness=1`; usable; `K=1` |
| Non-empty bitmap with no overlap, bounded 11:00 through 11:30 | `intent={4,5}`; empty intersection; `coverage=0`; `density=8/17`; no `E`; `soonness=0`; usable; `K=0`, then density |
| Full overlap, open from 16:00 | `intent={14,15,16}`; full intersection; `coverage=1`; `density=8/17`; `E=14`; `soonness=1`; usable; `K=1` |
| Fixed 60-minute service | only `PT60M` is eligible |
| Exact 90-minute request, open from 16:00 | use `PT90M`: `intent={14,15}`; `available={0,1,14,15}`; full intersection; `coverage=1`; `density=4/16`; `E=14`; `soonness=1`; `K=1` |
| Several durations eligible | score independently, compare `(match_score,density)`, and select the maximum tuple; never add values |
| Requested duration has no ruler | neutral availability; service stays if hard recall admitted it |
| One selectable duration omitted | rank represented durations only; never derive the missing ruler |

Raw counts **MUST NOT** replace normalized coverage or density.

#### Invalid, missing, and inconsistent hints

| State | Handling |
| --- | --- |
| Hint omitted | unknown, neutral numbers, `hint_usable=false` |
| Missing or empty `slot_bitmaps`, or dummy unknown ruler | invalid payload, neutral, `hint_usable=false` |
| Malformed Base64 or unsupported encoding | neutral, never interpreted as empty |
| Invalid Roaring cookie or serialization | neutral, `hint_usable=false` |
| Decoded index `>=slot_count` | out-of-range ruler, neutral |
| Duplicate duration entries | ambiguous hint, neutral |
| Required duration variant absent | valid for represented durations, neutral when none is eligible |
| Set bit with missing or empty-string `next_available_date` | invariant failure, neutral, never epoch 0 |
| Date differs from earliest set-bit service-local date | invariant failure, neutral |
| Every ruler all-zero and date omitted | known empty: density 0, represented coverage 0, soonness 0, `hint_usable=true` |
| Every ruler all-zero but date present | invariant failure, neutral |

`null` is unknown. `0` is known empty or known non-overlap. Consumers **MUST
NOT** collapse them.

#### Flag-conditional ordering

| Request state | Ordering |
| --- | --- |
| Preferences, flag true or omitted | `coverage * soonness`, then density |
| Preferences, flag false | coverage, then density; soonness still returned |
| No preferences, flag true or omitted | `(soonness,density)` lexicographically; coverage null |
| No preferences, flag false | density only; soonness still returned |

With preferences, coverage 1 and soonness 0.5 gives `K=0.5` when true and
`K=1` when false. Without preferences, `(0.90,0.10)` beats `(0.80,0.90)`;
equal-soonness `(0.90,0.60)` beats `(0.90,0.20)`. False ignores soonness.

#### Freshness and refresh behavior

At scoring instant 18:00, cutouts 17:59 and 18:00 are expired; 18:01 is
usable. An absent `valid_until` uses documented registry policy. A
future-skewed `generated_at` beyond documented clock tolerance is inconsistent
and neutral. Different ages among still-usable identical hints do not alter
coverage, density, soonness, or rank.

Producers **SHOULD** refresh on change and before expiry. Registries **SHOULD**
ingest feeds and poll when feeds are unavailable. A pipeline that cannot keep
hints usable produces neutral signals and **SHOULD NOT** advertise effective
availability ranking.

#### Soonness horizon and instant arithmetic

For `H=14 days`, a matching start at the anchor has soonness 1, seven days
later has 0.5, exactly fourteen days later has 0, and later remains 0.
`2026-03-14T10:00:00-04:00` equals `2026-03-14T14:00:00Z` and projects to the
same index. Across daylight-saving transitions, add intervals on the instant
timeline. Repeated or skipped local labels do not create or remove indices.

#### Pagination and page-local reordering

Ranking runs before pagination. Scoring instant and index snapshot remain
frozen across cursor pages, with a deterministic final tie-break. Every hit in
a ranked response includes `rank_signals`, including omitted or expired hints
with null values and `hint_usable=false`. Known-empty density and known
non-overlap coverage are 0. Soonness remains populated when the flag is false.

Agents may re-order one returned page, but cannot recover a global alternative
ordering because later pages were selected under the original rank. A different
global policy requires a new search.

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
