# USP Specification Review

**Reviewer:** Ranya
**Date:** 2026-02-14
**Spec Version:** `2026-02-09`

---

## 1. Formal RFC Format Deviations

The spec references RFC 2119 (Section 1, line 13) and uses MUST/SHOULD/MAY keywords
correctly throughout, which is good. However, it departs from formal IETF RFC structure
in the following ways:

### 1.1 Missing Standard Sections

A formal RFC (per RFC 7322 — RFC Style Guide) **requires** the following sections that
USP omits entirely:

| Required RFC Section | Present in USP? | Notes |
|---|---|---|
| **Abstract** | No | An RFC must open with a concise (<200 word) abstract summarizing the document's purpose. USP jumps straight into "1. Introduction." |
| **Status of This Memo** | No | Every RFC begins with a boilerplate status section indicating its standards track, informational, or experimental category. |
| **Copyright Notice** | No | RFCs require an IETF Trust copyright notice. The README mentions Apache 2.0, but the spec itself has no license/copyright section. |
| **Table of Contents** | No | RFCs include a machine-generated ToC. The spec has none. |
| **Terminology / Definitions** | Partial | Section 1 "Conventions" covers date/duration formats, but there is no dedicated terminology section defining terms like "hold," "slot," "booking," "capability," etc. The reader must infer these from context. A formal RFC would have a standalone "Terminology" or "Definitions" subsection (see RFC 8446 Section 1.2). |
| **IANA Considerations** | No | If USP introduces registries (capability namespaces, service verticals, status codes), a formal RFC requires an IANA Considerations section per RFC 8126. Even if no IANA action is needed, the section must be present stating "This document has no IANA actions." |
| **Security Considerations** | Partial | Section 9 covers security but is extremely thin (4 bullet points). A formal RFC requires a substantive security analysis: threat model, authentication/authorization requirements, data confidentiality, replay protection, etc. |
| **References (Normative / Informative)** | No | RFCs split references into normative (MUST be read to implement) and informative (helpful context). USP has inline links but no formal references section. |
| **Authors' Addresses** | No | Standard RFC metadata. |
| **Appendices** | No | Not strictly required, but the JSON schema examples, sequence diagrams, and the detailed agent use-case table would be better placed in appendices, keeping the normative text focused. |

### 1.2 Section Numbering Inconsistencies

The document numbers its top-level sections (1–10) but does not number subsections.
For example, "Service Schema," "Availability Hint," "Duration," "Pricing," "Service
Policies" under Section 4 are unnumbered. Formal RFCs use full hierarchical numbering
(4.1, 4.2, 4.2.1, etc.) for precise cross-referencing.

### 1.3 Normative Language Usage

While the spec imports RFC 2119, some normative statements are phrased casually:

- > "Recommended TTL: 5-10 minutes" (Section 5, Hold operations)

  Should be: "Businesses **SHOULD** set hold TTL between 5 and 10 minutes."

- > "A recommended refresh interval is every 1-24 hours"

  Should be: "Platforms **SHOULD** refresh cached catalog data at intervals between
  1 and 24 hours."

### 1.4 Missing Document Metadata

The spec has a version date (`2026-02-09`) but lacks:
- Document status (Draft, Proposed Standard, Informational)
- Revision history / changelog
- Intended audience
- Relationship to other documents (beyond inline mentions of UCP)

---

## 2. Why the README "Problem" Statement Is Incorrect

The README's "Problem" section (lines 13–18) states:

> *No standard defines how an AI agent or consumer platform can:*
> 1. *Discover what services a business offers*
> 2. *Query real-time availability*
> 3. *Book a time-based service through a standardized lifecycle*

**This claim is demonstrably false.** Multiple established standards already address
these problems:

### 2.1 iCalendar / iTIP / CalDAV (IETF Standards Track)

- **RFC 5545** (iCalendar) defines the core data format for calendar events, to-dos,
  free/busy information, and scheduling objects — including `VEVENT`, `VFREEBUSY`,
  and `VTODO` components that map directly to USP's concept of services, availability
  slots, and bookings.
- **RFC 5546** (iTIP) defines a transport-independent interoperability protocol for
  scheduling operations: `PUBLISH`, `REQUEST`, `REPLY`, `CANCEL`, `COUNTER`,
  `DECLINECOUNTER`, and `REFRESH`. These map directly to USP's create, confirm,
  reschedule, and cancel booking operations.
- **RFC 6638** (CalDAV Scheduling Extensions) extends CalDAV with server-side
  implicit scheduling, auto-scheduling, and free/busy queries — essentially the same
  capability USP's availability query provides.

These are **IETF Standards Track** RFCs, widely implemented by Google Calendar,
Apple Calendar, Microsoft Outlook/Exchange, and every major calendar system.

### 2.2 OpenActive Open Booking API (W3C Community Spec)

The **Open Booking API 1.0** (CR3) by the OpenActive Community Group under the W3C
is an HTTP API specification specifically designed for booking participation in
activities and services. It uses schema.org-based data models with JSON-LD context
and covers:

- Opportunity discovery via RPDE feeds (similar to USP's service catalog)
- Availability querying
- Booking creation with holds (OrderQuote → OrderProposal → Order)
- Cancellation and error handling

This is a published Candidate Release with real implementations in the fitness and
leisure industry.

### 2.3 schema.org Service / ReserveAction / BookAction

schema.org defines structured types for:

- `Service` — describing services with `hoursAvailable`, `hasOfferCatalog`, and
  `areaServed`
- `ReserveAction` / `BookAction` — actions for making reservations/bookings with
  `scheduledTime`, `provider`, `location`
- `Offer` — pricing and availability for services

Google, Bing, and other search engines already consume these for service discovery
and booking integration (Reserve with Google).

### 2.4 Google Maps Booking API / Reserve with Google

Google's **Maps Booking API** and **Reserve with Google** platform already provide:
- Merchant and service inventory management via feeds
- Availability data structure (party_size, spots_open, spots_total)
- Booking creation and management
- Integration across Search, Maps, and Assistant

### 2.5 What the Problem Statement Should Say

The problem is **not** that "no standard exists." The problem is that:

1. **Existing standards are fragmented** — iCalendar/CalDAV handles calendar
   interop but not commerce; schema.org provides discovery but not booking
   lifecycle; Reserve with Google is proprietary, not open.
2. **None natively integrate with payment protocols** — no existing standard
   bridges scheduling with a standardized checkout/payment flow like UCP.
3. **None are designed for agentic commerce** — existing standards predate the
   AI agent paradigm and lack constructs like availability hints for LLM-based
   reasoning, `continue_url` for human handoff, or MCP/A2A transport bindings.

A corrected problem statement might read:

> *Existing scheduling standards (iCalendar/RFC 5545, CalDAV/RFC 6638, schema.org,
> Open Booking API) address parts of the service scheduling lifecycle but are
> fragmented, lack native payment integration, and were not designed for autonomous
> AI agent orchestration. No single open standard unifies service discovery,
> real-time availability, booking lifecycle management, and payment coordination
> in a way that is both machine-readable and interoperable with modern commerce
> protocols like UCP.*

---

## 3. Missing Service Verticals and Pre-Existing RFCs

### 3.1 Missing Verticals

USP defines only four service verticals: `appointment`, `group`, `reservation`, and
`rental`. This is a narrow subset of real-world service commerce. The following
verticals are absent:

| Missing Vertical | Description | Examples | Why It Matters |
|---|---|---|---|
| `course` / `class` | Multi-session educational or training programs | University courses, cooking classes (6-week series), certification programs, tutoring packages | Unlike a one-off `group` session, courses span multiple dates with enrollment, progression, and completion semantics. |
| `event` | Ticketed one-time events with complex capacity models | Concerts, conferences, theater performances, sporting events | Events have seating maps, ticket tiers, general admission vs. reserved seating — none of which map cleanly to `group` or `reservation`. |
| `healthcare` | Clinical appointments with specialized requirements | Doctor visits, telehealth, lab work, procedures | Healthcare scheduling has unique constraints: insurance verification, referral requirements, HIPAA compliance, intake forms, follow-up scheduling. |
| `consultation` | Professional advisory sessions with variable scoping | Legal consultations, financial advising, architecture reviews | While `appointment` covers 1:1 sessions, consultations often involve pre-session questionnaires, document sharing, and engagement letters that are part of the booking flow. |
| `home_service` | On-location services at the buyer's premises | Plumbing, cleaning, pest control, moving, home repair | Travel time, service area boundaries, and on-site resource requirements differ fundamentally from in-studio appointments. |
| `tour` / `experience` | Time-bound guided experiences | City tours, wine tastings, adventure activities, museum guided tours | Tours combine group capacity with location/route, equipment, and often weather-dependent availability. |
| `subscription` / `recurring` | Recurring service memberships | Gym membership classes, weekly therapy, monthly coaching | Recurring bookings require series management (book N sessions, skip weeks, pause membership) not covered by one-off slots. |
| `coworking` | Shared workspace booking | Hot desks, meeting rooms, private offices by the hour/day | Combines elements of `rental` and `reservation` but with membership tiers, credit systems, and amenity bundles. |

### 3.2 Pre-Existing RFCs and Standards That Define These Services

Yes, there are pre-existing standards that USP should reference or align with:

| Standard | What It Defines | Relevance to USP |
|---|---|---|
| **RFC 5545** (iCalendar) | `VEVENT`, `VTODO`, `VFREEBUSY`, `VJOURNAL` — core calendar object types with recurrence rules (`RRULE`), attendees, alarms, and status. | USP's booking lifecycle (create, confirm, cancel) and availability (free/busy) are a subset of what iCalendar already models. USP should define a mapping to/from iCalendar for interop with existing calendar systems. |
| **RFC 5546** (iTIP) | Scheduling methods: `PUBLISH`, `REQUEST`, `REPLY`, `ADD`, `CANCEL`, `REFRESH`, `COUNTER`, `DECLINECOUNTER`. | USP's booking operations (create, confirm, reschedule, cancel) are semantically equivalent to iTIP methods. The spec should acknowledge this and define correspondence. |
| **RFC 6638** (CalDAV Scheduling) | Server-side scheduling, free-busy queries, auto-scheduling. | Directly parallels USP's availability query and auto-confirmation mode. |
| **RFC 7986** (New iCalendar Properties) | Adds `COLOR`, `IMAGE`, `CONFERENCE` (virtual meeting URIs), `REFRESH-INTERVAL`. | USP's `channel.virtual_provider` and `images` fields overlap with these properties. |
| **schema.org/Service** | Structured data vocabulary for services, offers, hours, and actions. | USP Section 4.1 already suggests schema.org/Service for web crawlers. The spec should formalize this mapping rather than leaving it as a MAY. |
| **OpenActive Open Booking API 1.0** | Full booking lifecycle for activities: opportunity feeds (RPDE), OrderQuote, Order, cancellation. | The closest existing open standard to USP's scope. USP should explicitly differentiate itself from OpenActive and explain why a separate protocol is needed (e.g., payment integration, agentic design, broader vertical coverage). |
| **Google Maps Booking API** | Feed-based inventory management, availability structures, booking notifications. | USP's catalog feed approach (Section 4, Caching and Indexing) should reference this prior art. |

### 3.3 Recommendation

The spec should either:
1. **Expand the verticals table** with additional types and mark them as future extensions, or
2. **Define the verticals table as extensible** with clear guidance on how vendors register custom verticals (similar to how capabilities use reverse-domain namespaces), or
3. Both — define a core set and an extension mechanism.

Additionally, Section 1 should include a "Relationship to Other Standards" subsection
acknowledging iCalendar, iTIP, CalDAV, schema.org, OpenActive, and Google's APIs,
explaining how USP relates to and differs from each.

---

## 4. Commerce vs. Non-Commerce Service Scheduling

### 4.1 Where the Distinction Is Unclear

The spec conflates commerce and non-commerce scheduling throughout, making it
difficult for implementers to know which parts apply when:

1. **`payment_timing: free` is listed alongside commerce values.** In the Service
   Policies table (Section 4), `payment_timing` accepts `at_booking`,
   `at_service`, `deposit_required`, and `free`. But `free` is not a "payment
   timing" — it's the absence of payment. Grouping it with commerce values
   conflates two fundamentally different flows.

2. **The Booking Payment schema always requires `amount` and `currency`.**
   (Section 7, Booking Payment table — all marked **Yes**.) For a free community
   yoga class, what should `amount` be? `0`? What `currency`? This forces
   non-commerce services to carry payment baggage.

3. **Section 7 title is "Payment Integration with UCP"** but it also governs
   free services implicitly. The `payment.status: not_required` value exists
   but is only discoverable by reading the schema table — there's no narrative
   explaining the free-service flow.

4. **The end-to-end flow (Section 8) only shows the payment path.** The
   `else No payment required` branch in the sequence diagram is a single
   line: "Booking returned as confirmed at step 4." There's no dedicated
   walkthrough for the non-payment flow, even though it's arguably the
   simpler and more common case for many verticals (community events,
   public library room reservations, government services, volunteer
   scheduling).

5. **The spec never defines what "commerce" means in context.** UCP is
   described as handling "product commerce" and USP as handling "service
   commerce," but the spec doesn't distinguish between:
   - **Paid services** (salon, massage) — require UCP integration
   - **Free services** (community meetup, library booking) — standalone USP
   - **Freemium services** (free consultation, paid follow-up) — hybrid
   - **Prepaid/membership services** (gym class included in membership) — no
     per-booking payment but not "free"

### 4.2 Proposed Clarification

The spec should add a subsection early in Section 2 ("Core Concepts") titled
**"Commerce and Non-Commerce Services"** that:

1. **Defines two operational modes explicitly:**

   | Mode | `payment_timing` Values | UCP Required? | Confirmation Flow |
   |------|------------------------|---------------|-------------------|
   | **Standalone (non-commerce)** | `free`, `at_service` | No | USP only: `pending` → `confirmed` (auto) or `pending` → `confirmed` (manual) |
   | **Integrated (commerce)** | `at_booking`, `deposit_required` | Yes | USP + UCP: `pending` → `requires_action` → (UCP checkout) → `confirmed` |

2. **Makes payment fields conditionally required:**
   - When `payment_timing` is `free`: the `payment` object on the booking
     **SHOULD** be omitted entirely (not present with `amount: 0`).
   - When `payment_timing` is `at_service`: the `payment` object **MAY** be
     present with `status: not_required` and `amount_due: 0`, but `payment_url`
     and UCP integration are not applicable.

3. **Provides a dedicated non-commerce end-to-end example** in Section 8,
   showing the full flow for booking a free community yoga class — from
   discovery through confirmation — without any payment steps. This validates
   that USP works standalone.

4. **Renames or restructures `payment_timing`** to separate the scheduling
   policy from the payment policy:
   - `requires_payment`: `boolean` — whether any payment is involved
   - `payment_timing`: `at_booking` | `at_service` | `deposit_required` —
     only present/relevant when `requires_payment` is `true`

   This avoids the semantic oddity of `free` being a "payment timing."

---

## 5. Specific Improvements

### 5.1 Catalog Caching and Indexing — Feed Mechanism

**Issue:** Section 4 ("Catalog Caching and Indexing") suggests that platforms and
aggregators should "periodically crawl `/.well-known/usp` endpoints and fetch the
service catalog via `List Services`." This is a **pull-based polling model** where
every aggregator independently hammers every business's API on a schedule.

**Why this is wrong if USP is similar to UCP:** UCP (and Google Merchant Center,
and OpenActive's RPDE feeds) use a **feed-based push/pull model** where:

1. The business publishes a **service catalog feed** (analogous to a product feed
   in UCP / Google Merchant Center) — a paginated, timestamped data export that
   aggregators can incrementally consume.
2. Aggregators maintain a cursor/checkpoint and fetch only **changed records**
   since their last sync, rather than re-fetching the entire catalog.
3. The feed includes **tombstone records** for deleted services, so aggregators
   can prune their index.

**The correct mechanism for USP should be:**

1. **Define a `GET /services/feed` endpoint** (or equivalent) that returns a
   paginated, chronologically ordered feed of service records with:
   - `modified_at` timestamps
   - Cursor-based pagination (similar to the existing `pagination.cursor`)
   - Deleted/archived service tombstones
   - `Content-Type: application/json` with cache headers

2. **Reference the RPDE (Realtime Paged Data Exchange) pattern** used by
   OpenActive, or the Google Merchant Center feed model, as prior art.

3. **Keep `List Services` for interactive use** (platform UI, agent queries) but
   distinguish it from the feed endpoint used for bulk indexing.

This is more efficient, more scalable, and consistent with how UCP's catalog
capability is expected to work.

### 5.2 Illegal Argument Value Combinations

**Issue:** If `payment_timing` is `free`, can the pricing `model` be `fixed`
(with an `amount`)? The spec doesn't say. There are several potentially illegal
combinations that are not enforced:

| `payment_timing` | `pricing.model` | `pricing.amount` | Legal? | Notes |
|---|---|---|---|---|
| `free` | `free` | (absent) | **Yes** | Consistent: no payment, no price. |
| `free` | `fixed` | `7500` | **Unclear** | Contradictory: the service is free but has a fixed price? |
| `free` | `variable` | (absent) | **Unclear** | Variable pricing on a free service? |
| `at_booking` | `free` | (absent) | **No** | Contradictory: payment at booking but price is free. |
| `deposit_required` | `free` | (absent) | **No** | Contradictory: deposit on a free service. |
| `at_service` | `free` | (absent) | **Unclear** | Could mean "pay at service but the service is free" — confusing. |
| `deposit_required` | `fixed` | `7500` | **Yes** | But requires `deposit` object — is that enforced? |

**Recommendation:** The spec should include a **"Validation Rules"** or
**"Constraint Matrix"** subsection that explicitly defines:

1. Which `(payment_timing, pricing.model)` combinations are legal.
2. When `pricing.amount` is REQUIRED vs. MUST NOT be present.
3. When `deposit` is REQUIRED (only when `payment_timing: deposit_required`
   AND `pricing.model` is not `free`).
4. Schema-level enforcement via JSON Schema `if/then/else` or `oneOf`
   constraints in the published schema files.

### 5.3 Missing Field Descriptions and Inconsistent Subsection Formatting

**Issue:** Schema field tables provide only terse descriptions that don't explain
**when** each value should be used or **what it means** in practice.

**Examples of insufficient descriptions:**

| Field | Current Description | What's Missing |
|---|---|---|
| `state: limited` (Time Slot) | "low capacity" | How low? Is it a threshold (e.g., <20% remaining)? Who decides? |
| `state: waitlist` (Time Slot) | (implied from field name) | When should a business return `waitlist` vs. not returning the slot at all? |
| `confirmation_mode: manual` | "business approves" | What's the expected turnaround time? Is there a timeout? What happens if the business never responds? |
| `severity: requires_buyer_input` (Messages) | (no description) | What other severity values exist? What does each mean? |
| `type: error` (Messages) | (no description) | What other `type` values exist? `warning`? `info`? |
| `pricing.model: variable` | (listed in enum) | Variable based on what? Time of day? Demand? Party size? How does the platform discover the actual price? |
| `channel.type: hybrid` | (listed in enum) | What does "hybrid" mean operationally? In-person some days, virtual others? Buyer's choice? |

**Inconsistent subsection formatting:**

- **Service Policies** (Section 4): Has a textual description before the table
  ("Machine-readable policies that enable agents to make informed decisions.").
- **Pricing** (Section 4): Has no textual description — just a bare table.
- **Time Slot** (Section 5): No textual description.
- **Hold** (Section 5): No textual description.
- **Booking Schema** (Section 6): No textual description.
- **Booking Payment** (Section 7): Has a textual description.

**Recommendation:** Every schema subsection should have:
1. A 1–2 sentence description of what the object represents and when it appears.
2. A table with expanded descriptions that explain semantics, not just types.
3. Explicit enumeration of all allowed values for enum fields, with a sentence
   explaining each value.

### 5.4 Missing "Request:" and "Response:" Labels

**Issue:** Some operations show JSON snippets without clearly labeling them as
request or response payloads. This creates ambiguity.

**Specific instances:**

| Section | Operation | Issue |
|---|---|---|
| Section 4 | `List Services` — `POST /services/list` | The JSON snippet is a request body, but there's no "Request:" label. The response is shown later under "Example Response" — inconsistent with other sections. |
| Section 4 | `Get Service` — `GET /services/{service_id}` | No request or response example at all. |
| Section 5 | `Query Availability` | Has an unlabeled request JSON, then "Response:" before the response JSON — inconsistent (request is unlabeled, response is labeled). |
| Section 5 | `Hold Slot` | Request JSON is unlabeled. Response is described in prose ("Returns a Hold with `expires_at`") but no JSON example. |
| Section 5 | `Release Slot` | No request or response examples at all. |
| Section 6 | `Create Booking` | Request JSON is unlabeled. No labeled response here (the example response appears later in Section 8). |
| Section 6 | `Confirm Booking` | No request or response examples. |
| Section 6 | `Cancel Booking` | Request JSON is unlabeled. No response example. |
| Section 6 | `Reschedule Booking` | Request JSON is unlabeled. No response example. |
| Section 6 | `Get Booking` / `Update Booking` | No examples at all. |

**Recommendation:** Every operation should follow a consistent pattern:

```
**Operation Name** — `METHOD /path`

Request:
​```json
{ ... }
​```

Response:
​```json
{ ... }
​```
```

### 5.5 "Hold and Release Operations" Placement

**Issue:** The "Hold and Release Operations" subsection appears **after** the
"Caching Strategy" subsection in Section 5. This is structurally wrong because:

1. Holds are **core operations** of the availability capability — they belong
   with the other operations (`Query Availability`).
2. The "Caching Strategy" subsection **references** holds (Tier 3: "Hold Slot
   (real-time)") but the hold operation hasn't been defined yet at that point
   in the document.
3. The natural reading order for Section 5 should be:
   - Schema definitions (Time Slot, Hold)
   - Operations (Query Availability, Hold Slot, Release Slot)
   - Caching Strategy (which summarizes how the operations fit together)

**Recommendation:** Move "Hold and Release Operations" to immediately after the
"Operations" subsection heading (before "Caching Strategy"), making the section
flow: Time Slot → Hold → Operations (Query + Hold + Release) → Caching Strategy.

### 5.6 Incorrect Booking Status in Payment Flow Description

**Issue:** In Section 7 ("Booking Payment"), the text states:

> *"the platform creates a UCP checkout session when `status` is `pending`."*

But the sequence diagram in the same section (and Section 8) clearly shows:

```
B-->>P: booking response (status: requires_action, payment.timing: at_booking)
```

And step 1 of the detailed flow description says:

> *"The business returns the booking with `status: requires_action`"*

The Booking Status Lifecycle diagram (Section 6) also shows that `requires_action`
is the status that means "Buyer input needed (payment)," while `pending` means
"Awaiting confirmation. Transient for auto mode."

**The text should say `requires_action`, not `pending`.** A booking in `pending`
status is awaiting business confirmation (manual mode), not payment. The platform
should create a UCP checkout when the booking status is `requires_action` with a
payment-related message.

### 5.7 Missing Cross-Reference Link

**Issue:** In Section 7 ("How USP Connects to the UCP Checkout Flow"), step 2 says:

> *"The platform maps the USP booking to UCP line items (see Line Item Mapping
> below)"*

The text says "see Line Item Mapping below" but this is plain text — it's not a
clickable cross-reference link. Since the rest of the document uses Markdown anchor
links (e.g., `[Availability Hint](#availability-hint)`, `[Section 7](#7-payment-integration-with-ucp)`),
this should also be a link:

```markdown
(see [Line Item Mapping](#line-item-mapping-usp--ucp) below)
```

### 5.8 Missing Detailed Service Binding Descriptions

**Issue:** Section 3 mentions three transport bindings — REST (OpenAPI 3.x),
MCP (OpenRPC / JSON-RPC), and A2A (Agent Card) — but the spec provides **zero
detail** on how the MCP and A2A bindings actually work. The entire spec is written
from a REST perspective (HTTP methods, URL paths, JSON request/response bodies).

**What's missing for MCP binding:**
- How do USP operations map to JSON-RPC methods? (e.g., is `POST /services/list`
  → `usp.services.list` as a JSON-RPC method?)
- What does the `_meta.usp.profile` field look like in a JSON-RPC request?
- How does capability negotiation work over JSON-RPC?
- How are errors mapped (HTTP status codes → JSON-RPC error codes)?
- How do webhooks work in MCP? (JSON-RPC notifications? Server-sent events?)

**What's missing for A2A binding:**
- What does the Agent Card look like for a USP-capable business?
- How does the full agent-to-agent scheduling flow work?
  - How does the platform agent discover and initiate a conversation with
    the business agent?
  - How are USP operations expressed as A2A tasks or messages?
  - How does the business agent respond with availability, confirmations, etc.?
  - How is state maintained across the multi-step booking flow?
- How does A2A handle the hold → book → pay lifecycle?
- How does `continue_url` work in an A2A context (agent-to-agent, no browser)?

**The README references extended spec documents** (`specification/transport-rest.md`,
`specification/transport-mcp.md`) but these files **do not exist** in the
repository. This means the transport bindings are promised but undelivered.

**Recommendation:** At minimum, the spec should include:
1. A mapping table for each binding (REST path → MCP method → A2A task type).
2. One complete end-to-end example for each binding (not just REST).
3. Error code mapping across transports.
4. Or, if the bindings are deferred, the spec should explicitly state they are
   planned extensions and remove the references to non-existent files.

### 5.9 Waiting List Capability

**Issue:** The spec defines `state: waitlist` as a possible slot state (Section 5,
Time Slot schema) but provides **no operations or lifecycle for waitlists.** There
is no way to:

- Join a waitlist for a fully booked slot
- Check position on a waitlist
- Get notified when a spot opens
- Automatically convert a waitlist entry to a booking
- Leave a waitlist

**Proposed Waitlist Extension:**

A waitlist capability could be defined as an extension to `dev.usp.services.booking`
with the following design:

#### Schema: WaitlistEntry

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | **Yes** | Unique waitlist entry identifier |
| `service_id` | string | **Yes** | The service |
| `slot_id` | string | No | Specific slot (null = any available slot in a date range) |
| `date_range` | object | No | `{start_date, end_date}` — preferred date range when `slot_id` is null |
| `buyer` | Buyer | **Yes** | The waitlisted buyer |
| `party_size` | integer | **Yes** | Number of spots needed |
| `position` | integer | **Yes** | Current position in the waitlist |
| `status` | string | **Yes** | `waiting`, `offered`, `expired`, `converted`, `declined`, `left` |
| `offer_expires_at` | string | No | RFC 3339 — when a spot is offered, deadline to accept |
| `preferences` | object | No | `{preferred_resources, preferred_times, flexible_dates}` |
| `created_at` | string | **Yes** | RFC 3339 |

#### Operations

| Operation | Method | Path | Description |
|---|---|---|---|
| Join Waitlist | `POST` | `/waitlist` | Add buyer to waitlist for a slot or date range |
| Get Waitlist Entry | `GET` | `/waitlist/{entry_id}` | Check status and position |
| Leave Waitlist | `DELETE` | `/waitlist/{entry_id}` | Remove from waitlist |
| Accept Offer | `POST` | `/waitlist/{entry_id}/accept` | Convert offered spot to booking |
| Decline Offer | `POST` | `/waitlist/{entry_id}/decline` | Pass on offered spot (moves to next in line) |

#### Lifecycle

```
waiting ──► offered ──► converted (becomes a booking)
   │            │
   │            └──► declined (spot offered to next person)
   │            │
   │            └──► expired (offer timed out, spot offered to next)
   │
   └──► left (buyer voluntarily leaves)
```

#### Cancellation Fee Waiver Use Case

This is the key scenario the user identified: when a booked user wants to cancel but
would incur a cancellation fee, the waitlist creates an opportunity to avoid that fee:

1. User A has a booking with a `late_cancellation_fee` of $25.
2. User A requests cancellation. The system checks the waitlist for that slot.
3. Users B, C, D are on the waitlist. User B receives an offer (with a TTL).
4. User B accepts → a new booking is created for User B.
5. Because the slot was re-filled, User A's cancellation fee is **waived**.
6. If no waitlist user accepts within a configured window, User A's cancellation
   proceeds with the standard fee.

This requires an additional policy field:

```json
{
  "cancellation": {
    "allowed": true,
    "free_cancellation_until": "PT24H",
    "late_cancellation_fee": 2500,
    "waive_fee_if_waitlist_fills": true,
    "waitlist_fill_window": "PT2H"
  }
}
```

#### Webhooks

| Event | Trigger |
|---|---|
| `waitlist.spot_offered` | A spot opened and was offered to the next waitlisted buyer |
| `waitlist.converted` | Waitlist entry was converted to a booking |
| `waitlist.expired` | Offer expired without acceptance |
| `waitlist.position_changed` | Buyer's position in the waitlist changed |

**Recommendation:** Define the waitlist as an official extension
(`dev.usp.services.waitlist`) that extends `dev.usp.services.booking`. The
`state: waitlist` value already exists in the Time Slot schema — this extension
would give it operational meaning.

---

## Summary of Recommendations

| # | Category | Priority | Recommendation |
|---|---|---|---|
| 1 | RFC Format | Medium | Add Abstract, ToC, Terminology, IANA Considerations, formal References, and Authors sections. |
| 2 | Problem Statement | High | Rewrite to acknowledge existing standards and articulate USP's unique value proposition (agentic + payment integration + unified). |
| 3 | Verticals | Medium | Expand verticals or define an extension mechanism. Add "Relationship to Other Standards" subsection. |
| 4 | Commerce vs. Non-Commerce | High | Add explicit operational modes, make payment fields conditional, provide non-commerce end-to-end example. |
| 5.1 | Catalog Feed | High | Replace polling-based caching advice with a proper feed endpoint, consistent with UCP's catalog feed model. |
| 5.2 | Validation Rules | High | Define legal argument value combinations and enforce via JSON Schema constraints. |
| 5.3 | Field Descriptions | Medium | Expand all schema field descriptions with semantics and usage guidance. Standardize subsection formatting. |
| 5.4 | Request/Response Labels | Low | Add consistent "Request:" and "Response:" labels to all operation JSON snippets. |
| 5.5 | Hold Placement | Low | Move Hold and Release Operations before Caching Strategy. |
| 5.6 | Status Bug | High | Change `pending` to `requires_action` in the Booking Payment text. |
| 5.7 | Cross-Ref Link | Low | Add Markdown anchor link to "Line Item Mapping" reference. |
| 5.8 | Service Bindings | High | Add MCP and A2A binding details, or mark as planned and remove references to non-existent files. |
| 5.9 | Waitlist | Medium | Define a waitlist extension with join/offer/accept lifecycle and cancellation fee waiver policy. |
