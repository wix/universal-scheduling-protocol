# USP Playground — Specification

## Overview

The USP Playground is a browser-based interactive simulator that walks users through the complete scheduling lifecycle defined by the Universal Scheduling Protocol. It runs entirely client-side with mocked business responses — no backend required. The playground is embedded in the USP documentation site (Material for MkDocs) as a dedicated page.

### Goals

1. **Teach by doing** — Let developers experience the full USP flow (discover → browse → check availability → hold → book → manage) with real protocol payloads.
2. **Validate understanding** — Show request/response schemas at every step, with inline annotations explaining each field.
3. **Demonstrate error handling** — Scenario dropdowns let users trigger validation errors, conflict states, and edge cases.
4. **Support both deployment modes** — Toggle between UCP-Native and Standalone flows to see how they differ.
5. **Cover all transport bindings** — Switch between REST, MCP, A2A, and ESP representations of the same operation.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  MkDocs Page (playground.md)                    │
│  ┌───────────────────────────────────────────┐  │
│  │  playground.js  (client-side engine)       │  │
│  │  ┌─────────┐ ┌──────────┐ ┌────────────┐ │  │
│  │  │ Stepper │ │  Mock    │ │  Schema    │ │  │
│  │  │   UI    │ │  Engine  │ │  Validator │ │  │
│  │  └─────────┘ └──────────┘ └────────────┘ │  │
│  │  ┌─────────────────┐ ┌─────────────────┐ │  │
│  │  │ Payload Editor  │ │ Response Viewer │ │  │
│  │  └─────────────────┘ └─────────────────┘ │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │  scenarios/*.json  (mock data per step)    │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Components

| Component | Responsibility |
|-----------|---------------|
| **Stepper UI** | Linear step navigation (back/forward), progress indicator, step titles |
| **Mock Engine** | Processes requests against scenario data, returns mock responses with realistic latency simulation |
| **Schema Validator** | Validates request/response payloads against USP JSON Schemas (`schemas/*.json`) at each step |
| **Payload Editor** | Editable JSON code block for each request, with syntax highlighting and field annotations |
| **Response Viewer** | Read-only syntax-highlighted response display with status code badge and timing |
| **Scenario Selector** | Dropdown per step to switch between happy path and error scenarios |
| **Transport Toggle** | Global toggle to view payloads as REST, MCP, A2A, or ESP |
| **Mode Toggle** | Global toggle between UCP-Native and Standalone deployment modes |

### Technology

- **Runtime**: Vanilla JS (no framework) — keeps the bundle small and avoids build tooling beyond MkDocs
- **Code display**: Prism.js or Monaco Editor (read-only mode for responses, editable for requests)
- **Schema validation**: Ajv (JSON Schema Draft 2020-12) loaded with USP schemas from `schemas/`
- **Styling**: Extends the existing `extra.css` design system with playground-specific classes
- **Hosting**: Static files served by MkDocs as part of the documentation site

---

## Step-by-Step Flow

The playground presents **8 steps** that mirror the complete USP scheduling lifecycle. Each step shows a request, lets the user run it, and displays the response.

### Step 1: Discovery

**Purpose**: Fetch the business's USP profile to learn what capabilities it supports.

| Field | Value |
|-------|-------|
| Method | `GET /.well-known/usp` |
| Target | `business.example.com` |
| Response | Business profile with `usp` metadata, capabilities, service bindings |

**What the user learns**: How USP discovery works, what a business profile looks like, what capabilities are declared.

**Scenarios**:
- **Standard profile** — Core capabilities only (catalog, availability, bookings)
- **Full profile** — All capabilities including waitlist extension and holds
- **Minimal profile** — No holds, no waitlist, appointment-only

**Standalone-specific**: Shows `/.well-known/usp` profile with `signing_keys` and `checkout_systems`.
**UCP-Native-specific**: Shows `/.well-known/ucp` profile with USP capabilities nested inside UCP.

---

### Step 2: Capability Negotiation

**Purpose**: Demonstrate how platform and business capabilities are intersected.

| Field | Value |
|-------|-------|
| Input | Platform profile + Business profile (from Step 1) |
| Output | Negotiated capability set |

**What the user learns**: The negotiation algorithm — intersection, version selection, extension pruning.

**Display**:
- Side-by-side: Platform capabilities vs Business capabilities
- Result: Intersection with annotations showing what was pruned and why
- Highlight: Orphaned extensions (e.g., waitlist without bookings)

**Scenarios**:
- **Full match** — Platform and business support identical capabilities
- **Partial match** — Business lacks holds; negotiation removes hold-dependent flows
- **Version mismatch** — Business supports older version; negotiation selects compatible version
- **Incompatible** — Empty intersection triggers `capabilities_incompatible` error

---

### Step 3: Browse Services

**Purpose**: Query the service catalog to find bookable services.

| Field | Value |
|-------|-------|
| Method | `POST /services/list` |
| Request | Filters (category, query, location), pagination, context (locale, currency) |
| Response | Array of `Service` objects with pricing, duration, media, resources |

**What the user learns**: Catalog structure, filtering, pagination, the `context` object.

**Mock business**: "Downtown Wellness Spa" with services:
- **Swedish Massage** (appointment, 60min, $120, staff resource)
- **Group Yoga Class** (group, 75min, $25/person, capacity 20)
- **Spa Suite** (reservation, 120min, $350, room resource)
- **Kayak Rental** (rental, variable duration, $45/hour)

**Scenarios**:
- **Happy path** — Returns all 4 services
- **Filtered by category** — Only returns matching services
- **Free-text search** — `query: "massage"` returns ranked results
- **Empty results** — No services match filters

---

### Step 4: Check Availability

**Purpose**: Query available time slots for a selected service.

| Field | Value |
|-------|-------|
| Method | `POST /availability/query` |
| Request | `service_id`, date range, `party_size`, optional `resource_id`, `location_id` |
| Response | Array of `TimeSlot` objects with capacity, pricing, resources |

**What the user learns**: Slot structure, capacity model, resource assignment, opening hours.

**Scenarios**:
- **Available slots** — Multiple slots across 3 days with varying capacity
- **Limited availability** — Only 2 slots remaining (group class nearly full)
- **Resource-specific** — Slots filtered by specific staff member
- **No availability** — Zero slots in requested range (triggers waitlist prompt)
- **Date range too wide** — `range_too_wide` error

**Per-vertical behavior**:
- Appointment: 1 slot = 1 resource, capacity 1
- Group: 1 slot = shared time, capacity N with `spots_remaining`
- Reservation: 1 slot = 1 resource (room), capacity from party_size
- Rental: Slots represent available time windows for the asset

---

### Step 5: Hold Slot (Optional)

**Purpose**: Temporarily reserve a slot before completing the booking.

| Field | Value |
|-------|-------|
| Method | `POST /availability/hold` |
| Request | `slot_id`, `service_id`, `spots` |
| Response | `Hold` object with `id`, `expires_at`, `status` |

**What the user learns**: Hold mechanics, expiry, the hold-to-booking bridge.

**Conditional**: Only shown if the business profile from Step 1 declares `"holds": true`. Otherwise, this step is skipped with an explanatory note.

**Scenarios**:
- **Hold granted** — 5-minute hold with countdown timer displayed
- **Slot no longer available** — `slot_unavailable` conflict error
- **Concurrent hold limit** — `hold_limit_exceeded` for appointment type
- **Release hold** — User can click "Release" to `DELETE /availability/holds/{hold_id}`

---

### Step 6: Create Booking

**Purpose**: Create a confirmed booking from the held (or unheld) slot.

| Field | Value |
|-------|-------|
| Method | `POST /bookings` |
| Request | `service_id`, `slot_id`, `hold_id` (optional), `buyer`, `party_size`, `notes` |
| Response | `Booking` object with `status`, `actions[]`, `payment` |

**What the user learns**: Booking creation, the `actions[]` pattern, status transitions.

**Scenarios**:
- **Instant confirmation** — `status: confirmed`, no actions needed (free service or pre-paid)
- **Payment required** — `status: requires_action`, `actions: [{type: "payment", status: "pending"}]`
- **Manual confirmation** — `status: pending`, business will confirm async
- **Validation error** — Missing required buyer fields
- **Slot expired** — Hold expired between Step 5 and Step 6

**Standalone vs UCP-Native**:
- Standalone: Payment action includes `continue_url` for redirect flow, or embedded checkout
- UCP-Native: No payment action in USP response; payment handled by UCP checkout

---

### Step 7: Complete Payment (Standalone Only)

**Purpose**: Demonstrate the payment flow for Standalone mode bookings.

| Field | Value |
|-------|-------|
| Method | `POST /bookings/{booking_id}/confirm-payment` |
| Request | `transaction_id`, `order_reference` (from PSP/ACP) |
| Response | Updated `Booking` with `status: confirmed`, `payment.status: paid` |

**What the user learns**: Payment integration patterns, the `confirm-payment` handshake.

**Conditional**: Only shown in Standalone mode. In UCP-Native mode, this step shows an informational card explaining that payment is handled by UCP checkout.

**Scenarios**:
- **Payment success** — Booking transitions to `confirmed`
- **Payment failed** — `payment_failed` error, booking remains `requires_action`
- **Actions pending** — Non-payment actions still pending, `actions_pending` error
- **Deposit flow** — Partial payment with deposit amount

---

### Step 8: Manage Booking

**Purpose**: Demonstrate post-booking lifecycle operations.

| Field | Value |
|-------|-------|
| Operations | Update, Cancel, Reschedule, Confirm (business-side) |
| Webhooks | Simulated webhook events |

**What the user learns**: Booking lifecycle state machine, webhooks, cancellation policies.

**Sub-steps** (tabbed interface):

#### 8a: View Booking
- `GET /bookings/{booking_id}` — Full booking object

#### 8b: Update Booking
- `PATCH /bookings/{booking_id}` — Change buyer info or notes

#### 8c: Reschedule
- `POST /bookings/{booking_id}/reschedule` — Pick a new slot
- Shows price change handling for peak/off-peak

#### 8d: Cancel
- `POST /bookings/{booking_id}/cancel` — With reason and canceled_by
- Shows refund calculation based on cancellation policy

#### 8e: Webhook Simulation
- **Event dropdown**: `booking.confirmed`, `booking.canceled`, `booking.rescheduled`, `booking.reminder`, `booking.service_started`, `booking.completed`
- "Simulate Event" button fires mock webhook POST with full payload
- Shows webhook signature headers (`Signature`, `Signature-Input`, `Content-Digest`)

---

## Bonus Step: Waitlist (Extension)

**Purpose**: Demonstrate the waitlist extension when no slots are available.

| Field | Value |
|-------|-------|
| Trigger | Shown when Step 4 returns zero slots AND business supports waitlist |
| Method | `POST /waitlist` |
| Flow | Join → Offered (simulated) → Accept → Converted to Booking |

**Scenarios**:
- **Join and wait** — Entry created with `status: waiting`
- **Offer received** — Simulated `waitlist.offered` webhook, slot offered
- **Accept offer** — `POST /waitlist/{entry_id}/accept` converts to booking
- **Decline offer** — Returns to `waiting` status
- **Offer expires** — Countdown timer, `waitlist.expired` event

---

## Transport Binding Toggle

A global toggle in the playground header lets users view any step's request/response in different transport formats:

### REST (default)
```
POST /bookings HTTP/1.1
Host: api.business.example.com
Content-Type: application/json
Authorization: Bearer {token}
Idempotency-Key: idk_abc123

{
  "service_id": "svc_massage_001",
  "slot_id": "slot_0315_0900",
  ...
}
```

### MCP (JSON-RPC 2.0)
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "usp_booking_create",
    "arguments": {
      "service_id": "svc_massage_001",
      "slot_id": "slot_0315_0900"
    },
    "_meta": {
      "usp": {
        "profile": "https://business.example.com/.well-known/usp",
        "idempotency_key": "idk_abc123"
      }
    }
  },
  "id": 1
}
```

### A2A (Agent-to-Agent)
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "params": {
    "id": "task_booking_001",
    "message": {
      "role": "user",
      "parts": [{
        "type": "data",
        "data": {
          "type": "usp.booking.create",
          "service_id": "svc_massage_001",
          "slot_id": "slot_0315_0900"
        }
      }]
    }
  }
}
```

### ESP (Embedded)
Shows an iframe embed code and a simulated embedded scheduling widget preview.

---

## Mock Business Data

All mock data lives in `playground/scenarios/` as JSON files.

### Directory Structure

```
playground/
├── SPEC.md                    # This file
├── scenarios/
│   ├── business-profile.json           # Step 1: Business profiles (standard, full, minimal)
│   ├── platform-profile.json           # Step 2: Platform profiles
│   ├── services.json                   # Step 3: Service catalog
│   ├── availability.json               # Step 4: Time slots per service
│   ├── holds.json                      # Step 5: Hold responses
│   ├── bookings.json                   # Step 6: Booking creation responses
│   ├── payment.json                    # Step 7: Payment confirmation responses
│   ├── manage.json                     # Step 8: Update/cancel/reschedule responses
│   ├── webhooks.json                   # Step 8e: Webhook event payloads
│   └── waitlist.json                   # Bonus: Waitlist extension responses
├── src/
│   ├── playground.js                   # Main engine: stepper, state machine, mock routing
│   ├── schema-validator.js             # Ajv wrapper loading USP schemas
│   ├── transport-formatter.js          # Converts REST payloads to MCP/A2A/ESP formats
│   ├── code-editor.js                  # Editable request pane (Prism.js or Monaco)
│   └── response-viewer.js             # Response display with status badge
├── styles/
│   └── playground.css                  # Playground-specific styles
└── index.md                            # MkDocs page entry point
```

### Mock Business: "Downtown Wellness Spa"

| Field | Value |
|-------|-------|
| Business ID | `biz_downtown_spa` |
| Name | Downtown Wellness Spa |
| Timezone | `America/New_York` |
| Verticals | `appointment`, `group`, `reservation`, `rental` |
| Location | 123 Wellness Ave, New York, NY 10001 |

**Services**:

| ID | Name | Type | Duration | Price | Resources |
|----|------|------|----------|-------|-----------|
| `svc_massage_001` | Swedish Massage | appointment | 60min | $120 | Staff: Sarah, Mike |
| `svc_yoga_001` | Morning Yoga | group | 75min | $25/person | Staff: Emma (max 20) |
| `svc_suite_001` | Spa Suite Experience | reservation | 120min | $350 | Room: Orchid Suite, Rose Suite |
| `svc_kayak_001` | Kayak Rental | rental | hourly ($45/hr) | variable | Equipment: Kayak #1-5 |

---

## UI Design

### Layout

```
┌──────────────────────────────────────────────────────────┐
│  ┌─ Mode ──┐  ┌─ Transport ─┐                           │
│  │Standalone│  │ REST ▾      │       USP Playground      │
│  └─────────┘  └─────────────┘                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ① Discovery  ② Negotiate  ③ Browse  ④ Availability     │
│  ⑤ Hold  ⑥ Book  ⑦ Payment  ⑧ Manage    [Waitlist]     │
│  ━━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Step 3: Browse Services                                 │
│  Query the catalog to find bookable services.            │
│                                                          │
│  Scenario: [Happy Path ▾]                                │
│                                                          │
│  ┌─ Request ─────────────────────────────────────────┐  │
│  │ POST /services/list                                │  │
│  │                                                    │  │
│  │ {                                                  │  │
│  │   "filters": {                                     │  │
│  │     "category": "wellness"                         │  │
│  │   },                                               │  │
│  │   "context": {                                     │  │
│  │     "language": "en",                              │  │
│  │     "currency": "USD"                              │  │
│  │   },                                               │  │
│  │   "pagination": { "limit": 10 }                    │  │
│  │ }                                                  │  │
│  │                                           [Edit]   │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  [ ◀ Back ]                    [ Run Request ▶ ]         │
│                                                          │
│  ┌─ Response ────────────────────────────────────────┐  │
│  │ 200 OK  ·  142ms                                  │  │
│  │                                                    │  │
│  │ {                                                  │  │
│  │   "usp": { "version": "2026-08-14", ... },        │  │
│  │   "services": [ ... ],                             │  │
│  │   "pagination": { "has_more": false }              │  │
│  │ }                                                  │  │
│  │                                     [Copy] [Expand]│  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ Schema Validation ───────────────────────────────┐  │
│  │  ✓ Request valid against ServiceListRequest       │  │
│  │  ✓ Response valid against USPEnvelope + Service[] │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  ◀ Previous: Capability Negotiation                      │
│                           Next: Check Availability ▶     │
└──────────────────────────────────────────────────────────┘
```

### Color & Style

- Inherits the USP teal palette from `extra.css`
- Request pane: Dark background (`#0f172a`), teal accent for method badge
- Response pane: Slightly lighter dark background, green badge for 2xx, red for 4xx/5xx
- Stepper: Teal active dot, muted gray for unvisited, checkmark for completed
- Transport toggle: Pill-style buttons matching the homepage badge style
- Mode toggle: Two-option switch (Standalone / UCP-Native)

---

## Implementation Phases

### Phase 1: Core Flow (MVP)
- Steps 1-4, 6, 8a (Discovery → Browse → Availability → Book → View)
- REST transport only
- Standalone mode only
- Happy-path scenarios only
- Static mock data (no editable payloads)

### Phase 2: Full Lifecycle
- Steps 5, 7, 8b-8e (Hold, Payment, Update/Cancel/Reschedule, Webhooks)
- Scenario dropdowns with error cases
- Editable request payloads
- Schema validation display

### Phase 3: Multi-Transport & Modes
- Transport binding toggle (REST, MCP, A2A, ESP)
- UCP-Native mode toggle
- Side-by-side transport comparison view

### Phase 4: Waitlist & Advanced
- Waitlist extension flow
- Monaco Editor for request editing
- Shareable playground state via URL hash
- "Export as cURL" / "Export as code" for each step

---

## Integration with MkDocs

The playground is a single MkDocs page at `/playground/` with:

```yaml
# mkdocs.yml addition
nav:
  - Playground: playground/index.md
```

```markdown
# playground/index.md
---
template: playground.html
title: Playground
description: Interactive USP scheduling flow simulator
hide:
  - navigation
  - toc
  - footer
---
```

A custom template `overrides/playground.html` extends `main.html` and loads the playground JS/CSS assets.

---

## Open Questions

1. **Editable vs read-only requests** — Should Phase 1 allow editing request payloads, or keep it simple with pre-built requests and scenario dropdowns?
2. **Schema bundle** — Should we bundle all JSON Schemas into a single file for the browser, or lazy-load per step?
3. **State persistence** — Should playground state survive page refresh (localStorage)?
4. **Code generation** — Should "Export as code" generate Python/Node/cURL snippets from the current request?
5. **Live API mode** — Future: allow users to point the playground at a real USP endpoint instead of mocks?
