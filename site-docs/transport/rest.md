---
title: REST Binding
description: USP REST transport binding — HTTP/JSON endpoints with idempotency, pagination, discovery, and request signing.
---

# REST Binding

The REST binding uses HTTP/1.1 (or higher) with JSON request/response bodies. All examples in the USP specification use the REST binding.

| Property | Value |
|----------|-------|
| **Schema format** | OpenAPI 3.x (JSON) |
| **Content type** | `application/json` |
| **Schema reference** | `openapi/usp-rest.json` |
| **Data shapes** | Normative JSON Schema definitions under `schemas/` (`$defs` per file) |

!!! info "Schema resolution"

    The machine-readable `openapi/usp-rest.json` references schema documents with relative JSON Pointer URIs (e.g., `../schemas/catalog.json#/$defs/Service`) and is **not** self-contained unless bundled. Implementations and tools MUST resolve external `$ref`s against the repository layout or use a pre-bundled copy.

## Capability Negotiation

The platform advertises its profile URI via the `USP-Agent` header using Dictionary Structured Field syntax (RFC 8941):

```http
POST /services/list HTTP/1.1
Host: business.example.com
USP-Agent: profile="https://agent.example/profiles/scheduling-agent.json"
Content-Type: application/json

{"filters": {"type": "appointment"}}
```

## Error Responses

USP uses RFC 9457 Problem Details for HTTP API error responses and distinguishes between **protocol errors** and **business outcome errors**.

### Business Outcome Errors

Business outcome errors (e.g., slot unavailable, hold expired, capacity exceeded) return **HTTP 200** with a `messages[]` array on the response object. Each message has `type`, `code`, `content`, optional `content_type`, optional `severity`, and an optional `path` field.

!!! note

    The `messages[]` array is available on **all** USP response envelopes, including catalog responses (`/services/list`, `/services/{service_id}`, `/services/feed`), not only state-modifying operations. This enables partial-success signalling, filter feedback, service-level warnings, and deprecation notices.

### Protocol Errors

Protocol errors use standard HTTP status codes with RFC 9457 Problem Details:

| HTTP Status | USP Meaning |
|-------------|-------------|
| `200 OK` | Operation succeeded, or business outcome error (check `messages[]`) |
| `201 Created` | Resource created (bookings, holds, registry entries, waitlist entries, feed subscriptions) |
| `400 Bad Request` | Malformed JSON, missing required fields, invalid profile URL |
| `401 Unauthorized` | Authentication required or invalid credentials |
| `403 Forbidden` | Platform profile not in business allowlist |
| `422 Unprocessable Entity` | Syntactically valid but structurally invalid request |
| `424 Failed Dependency` | Business profile unreachable |
| `429 Too Many Requests` | Rate limited; retry after `Retry-After` header |
| `500 Internal Server Error` | Unexpected server failure |
| `503 Service Unavailable` | Business temporarily unable to handle requests |

## Idempotency

State-modifying operations (booking creation, cancellation, rescheduling, hold creation, confirm-payment) **SHOULD** support idempotency via the `Idempotency-Key` header, consistent with `draft-ietf-httpapi-idempotency-key-header`.

### Behavior

- The platform **SHOULD** send an `Idempotency-Key` header (UUID v4 recommended) with all state-modifying requests.
- The business **MUST** store the idempotency key with the operation result for at least 24 hours.
- If the business receives a request with a previously seen key **and the same parameters**, it **MUST** return the cached result without re-executing.
- If the business receives a request with a previously seen key **but different parameters**, it **MUST** return `409 Conflict`.

!!! warning "Why idempotency matters"

    Idempotency is critical for booking operations where network retries could create duplicate reservations. For read-only operations (`GET`, `POST /services/list`, `POST /availability/query`), idempotency keys are not required.

### Example

```http
POST /bookings HTTP/1.1
Host: business.example.com
USP-Agent: profile="https://agent.example/profiles/scheduling-agent.json"
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{"service_id": "svc_haircut_001", "slot_id": "slot_20260315_0900", ...}
```

```mermaid
sequenceDiagram
    participant P as Platform
    participant B as Business

    P->>B: POST /bookings (Idempotency-Key: abc-123)
    B->>B: Store key + result
    B-->>P: 201 Created (booking)

    Note over P,B: Network retry (same key, same params)
    P->>B: POST /bookings (Idempotency-Key: abc-123)
    B->>B: Key found, same params
    B-->>P: 201 Created (cached result)

    Note over P,B: Conflicting retry (same key, different params)
    P->>B: POST /bookings (Idempotency-Key: abc-123, different body)
    B->>B: Key found, different params
    B-->>P: 409 Conflict
```

## Pagination

Several USP operations return paginated result sets. All paginated operations use cursor-based pagination.

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cursor` | string | No | Opaque cursor from the previous response's `pagination.cursor`. Omit on first request. |
| `limit` | integer | No | Requested page size. Businesses MAY apply a lower or upper cap. |

### Response Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pagination.cursor` | string \| null | **Yes** | Opaque cursor for the next request. `null` when no more pages. |
| `pagination.has_more` | boolean | **Yes** | `true` if additional pages exist; `false` on the last page. |

### Semantics

- Cursors are **opaque strings** -- platforms MUST NOT parse or construct them.
- Businesses SHOULD honor a cursor for at least **60 seconds** after it is issued.
- Platforms that retry after cursor expiry MAY receive a `cursor_expired` error and SHOULD restart from the first page.
- Default page sizes: **50 items** for slot queries, **20 items** for service lists.

!!! note "Feed endpoint exception"

    The `GET /services/feed` endpoint uses a timestamp-based cursor named `next_cursor` (not `cursor`) because its pagination semantics are tied to the RPDE incremental-sync model. All other paginated USP operations use the `cursor`/`has_more` pattern.

### Example

```mermaid
sequenceDiagram
    participant P as Platform
    participant B as Business

    P->>B: POST /availability/query (no cursor)
    B-->>P: slots[], pagination: {cursor: "abc", has_more: true}

    P->>B: POST /availability/query (cursor: "abc")
    B-->>P: slots[], pagination: {cursor: "def", has_more: true}

    P->>B: POST /availability/query (cursor: "def")
    B-->>P: slots[], pagination: {cursor: null, has_more: false}
```

## Discovery

Platforms discover a business's REST endpoints through the business profile published at `/.well-known/usp`. The profile's `usp.services` array lists supported USP operations with their base URLs and transport type. Platforms MUST filter for entries where `transport` is `"rest"` to locate REST endpoints.

On each request, the platform identifies itself by sending the `USP-Agent` header:

```http
USP-Agent: profile="https://agent.example/profiles/scheduling-agent.json"
```

The business resolves the platform profile to perform capability negotiation. For UCP-Native deployments, discovery is inherited from `/.well-known/ucp`.

```mermaid
sequenceDiagram
    participant P as Platform
    participant B as Business

    P->>B: GET /.well-known/usp
    B-->>P: Business profile (services, capabilities, transport: "rest")

    P->>B: POST /services/list<br/>USP-Agent: profile="https://agent.example/..."
    B->>B: Resolve platform profile, negotiate capabilities
    B-->>P: Service catalog
```

## Request Signing

State-modifying REST requests (POST, PUT, DELETE on bookings, holds, waitlist, registry) **SHOULD** be signed using HTTP Message Signatures (RFC 9421) to ensure integrity and authenticity.

### Signed Components

The signature MUST cover at minimum:

- `content-digest`
- `content-type`
- `@method`
- `@target-uri`
- `@created`

The `usp-agent` and `idempotency-key` headers SHOULD also be included when present.

### Platform Signing Keys

The platform's signing keys are published in the platform profile via the `signing_keys` array. Businesses that enforce request verification MUST advertise this requirement in their business profile.

### Example

```http
POST /bookings HTTP/1.1
Host: business.example.com
Content-Type: application/json
USP-Agent: profile="https://agent.example/profiles/scheduling-agent.json"
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Digest: sha-256=:RK/0qy18MlBSVnWgjwz6lZEWjP/lF5HF9bvEF8FabDg=:
Signature-Input: sig1=("@method" "@target-uri" "content-digest" "content-type" "usp-agent" "idempotency-key");keyid="platform-2026";created=1711036800
Signature: sig1=:MEUCIQDXyK9N3p5Rt...:

{"service_id": "svc_haircut_001", "slot_id": "slot_20260315_0900", ...}
```

!!! info "MCP note"

    For the MCP binding, request integrity is ensured by the underlying MCP transport layer (stdio pipe or HTTP-SSE with TLS). The `_meta.usp.profile` field identifies the platform without transport-level signing.

## Conformance Requirements

### MUST

A conforming REST binding implementation **MUST:**

1. Serve all endpoints over HTTPS (TLS 1.2 or later).
2. Accept and return `application/json` on all endpoints.
3. Return RFC 9457 Problem Details for protocol errors.
4. Return business outcome errors as HTTP 200 with a `messages[]` array on the response object.
5. Support the `USP-Agent` header on all requests.
6. Return `201 Created` for resource creation operations (bookings, holds, registry entries, waitlist entries, feed subscriptions).
7. Implement webhook signing per the security specification.

### SHOULD

A conforming REST binding implementation **SHOULD:**

1. Support the `Idempotency-Key` header on state-modifying operations.
2. Sign state-modifying requests using HTTP Message Signatures (RFC 9421).
3. Support cursor-based pagination.
