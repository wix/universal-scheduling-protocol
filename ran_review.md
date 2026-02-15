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

---
## 6. USP vs. UCP: Comparative Analysis

This section compares USP against UCP based on a thorough read of the full
UCP specification (overview, cart, checkout, order, fulfillment, discount,
buyer consent, AP2 mandates, identity linking, embedded checkout, payment
handler guide, tokenization guide, and all transport bindings) and the full
UCP documentation (core concepts, roadmap, schema authoring, UCP and AP2).

### 6.1 The Services Construct: Copied, Not Inherited

USP Section 2.4 defines three core constructs — **Capabilities**, **Extensions**,
and **Services** — and explicitly states they are "consistent with UCP's architecture."
In practice, the `Services` construct was copied verbatim from UCP rather than
inherited or referenced.

**UCP's Services (from `overview.md`):**

```json
"services": {
  "dev.ucp.shopping": [
    {
      "version": "2026-01-11",
      "spec": "https://ucp.dev/specification/overview",
      "transport": "rest",
      "endpoint": "https://business.example.com/ucp/v1",
      "schema": "https://ucp.dev/services/shopping/openapi.json"
    },
    {
      "version": "2026-01-11",
      "transport": "mcp",
      "endpoint": "https://business.example.com/ucp/mcp",
      "schema": "https://ucp.dev/services/shopping/mcp.openrpc.json"
    }
  ]
}
```

**USP's Services (from Section 3.1):**

```json
"services": {
  "dev.usp.services": {
    "version": "2026-02-09",
    "spec": "https://usp.dev/specification",
    "rest": {
      "schema": "https://usp.dev/services/rest.openapi.json",
      "endpoint": "https://business.example.com/usp/v1"
    },
    "mcp": {
      "schema": "https://usp.dev/services/mcp.openrpc.json",
      "endpoint": "https://business.example.com/usp/mcp"
    }
  }
}
```

**Issue:** The concept is identical — transport bindings with schema URLs and
endpoints — but the wire formats are **structurally incompatible**:

| Aspect | UCP | USP |
|--------|-----|-----|
| Transport selection | Array of objects with `transport` discriminator | Flat object with transport keys (`rest`, `mcp`) |
| Multiple transports | Separate array entries | Sibling keys on same object |
| A2A transport | Defined with `endpoint` pointing to Agent Card | Not present in the service definition (only in A2A transport binding section) |
| Embedded transport | Defined (`"transport": "embedded"`) | Not supported |

If USP is truly a "companion protocol," the service definition format **SHOULD**
be structurally identical to UCP's. As it stands, the same business needs to
expose two different discovery documents with two incompatible service schemas.

**Recommendation:** Either (a) align the USP service definition format exactly
with UCP's array-of-transport-objects pattern, or (b) define a shared base
service schema that both protocols import. Option (b) is stronger because it
prevents future drift.

### 6.2 Capability Format Inconsistency

UCP and USP use different wire formats for the same concept (capabilities in
profiles and responses):

**UCP (registry pattern — object keyed by name):**

```json
"capabilities": {
  "dev.ucp.shopping.checkout": [{"version": "2026-01-11"}],
  "dev.ucp.shopping.fulfillment": [{"version": "2026-01-11", "extends": "dev.ucp.shopping.checkout"}]
}
```

**USP (array pattern):**

```json
"capabilities": [
  {"name": "dev.usp.services.catalog", "version": "2026-02-09"},
  {"name": "dev.usp.services.booking", "version": "2026-02-09"}
]
```

This inconsistency extends to response metadata. A platform implementing both
protocols must handle two different capability negotiation wire formats for
what is conceptually the same operation.

UCP's registry pattern (object keyed by name) is the more recent design and
is documented in the UCP Schema Authoring Guide as the canonical approach. USP
should adopt the same format.

### 6.3 Error Handling Model Divergence

UCP and USP use fundamentally different error models:

**UCP:** Errors are conveyed via a `messages` array on the response object,
each with `type` (`error`, `warning`, `info`), `code`, `content`, `path`, and
`severity` (`recoverable`, `requires_buyer_input`, `requires_buyer_review`).
Business outcomes (including errors like out-of-stock) return HTTP 200 with
the UCP envelope. Protocol errors use HTTP status codes.

**USP:** Errors are conveyed via a separate `error` object (`code`, `message`)
for failure cases, returning standard HTTP error status codes (404, 409, 422).
Bookings also have a `messages` array, but with a different severity model
(`requires_buyer_input`, `informational`, `actionable`).

| Aspect | UCP | USP |
|--------|-----|-----|
| Business error HTTP status | 200 (with messages) | 404/409/422 |
| Error container | `messages[]` array | `error` object |
| Severity values | `recoverable`, `requires_buyer_input`, `requires_buyer_review` | `requires_buyer_input`, `informational`, `actionable` |
| Path support | Yes (`$.buyer.email`) | Not specified |

This means a platform implementing both protocols needs two completely different
error handling codepaths. If USP intends to be a companion protocol, it should
use UCP's error model (messages array, HTTP 200 for business outcomes,
matching severity values).

### 6.4 Factual Error: `submit_checkout` Does Not Exist in UCP

USP repeatedly references `submit_checkout` as a UCP operation:

- Section 2.1.4: "The platform acquires a payment token from the PSP and submits it via UCP's `submit_checkout`."
- Section 2.6 table: "`create_checkout`, `update_checkout`, `submit_checkout`"
- Section 7.2 flow: "Platform calls `submit_checkout`"
- Section 8.1 sequence diagram: Step 8 is `submit_checkout`
- Section 8.3: Step 8 references `submit_checkout`

**UCP calls this operation `complete_checkout`**, not `submit_checkout`. The
UCP Checkout Capability specification defines five operations: `Create Checkout`,
`Get Checkout`, `Update Checkout`, `Complete Checkout`, and `Cancel Checkout`.
The REST binding maps Complete Checkout to `POST /checkout-sessions/{id}/complete`.
The MCP binding maps it to the `complete_checkout` tool.

There is no `submit_checkout` anywhere in UCP. Every reference to this
operation in USP is incorrect.

### 6.5 Missing Capabilities in USP That UCP Provides

USP does not address several capabilities that UCP provides out of the box:

| UCP Capability | What It Provides | USP Gap |
|----------------|-----------------|---------|
| **Identity Linking** (`dev.ucp.common.identity_linking`) | OAuth 2.0-based account linking so platforms can act on behalf of users at a business. Scoped tokens, revocation, RISC profile. | USP has **no identity/authentication model at all**. There is no way for a platform to authenticate as a specific buyer at a business. Section 11.6 says "USP does not prescribe a specific authentication mechanism" and lists options, but defines nothing. For commerce (bookings tied to accounts, loyalty, member pricing), identity linking is essential. |
| **Order Management** (`dev.ucp.shopping.order`) | Post-checkout lifecycle: order tracking, fulfillment events, expectations, adjustments (refunds, returns, disputes). Webhook-based event streaming with signature verification. | USP has no post-booking lifecycle beyond `completed` and `no_show`. There is no structured way to handle: refund tracking, dispute resolution, adjustment logging, or service delivery events. The `cancellation` object captures some of this, but it's limited to the cancel case. |
| **AP2 Mandates** (`dev.ucp.shopping.ap2_mandate`) | Cryptographic proof of checkout agreement — business signs the checkout, platform signs the mandate. Prevents tampering and replay. | USP has no cryptographic integrity for the booking agreement. For high-value bookings (medical procedures, equipment rentals), there's no way to prove what was agreed upon. |
| **Embedded Checkout** (ECP) | Allows a host to embed the business's checkout UI, with delegation for payment and fulfillment. Supports dark/light themes, MessageChannel, delegation negotiation. | USP has `continue_url` but no embedded scheduling UI protocol. A platform cannot embed the business's booking interface within its own app. |
| **Buyer Consent** (`dev.ucp.shopping.buyer_consent`) | Structured consent categories (analytics, marketing, data sale) transmitted at checkout. | USP has no consent mechanism. GDPR/CCPA compliance for service bookings (which often involve health data, location data) is left entirely to ad-hoc implementation. |
| **Discount** (`dev.ucp.shopping.discount`) | Discount codes, automatic discounts, allocation breakdown, stacking. | USP has no discount or promotional pricing mechanism. Many service businesses offer discount codes, referral credits, or loyalty discounts. |
| **Webhook Signature Verification** | Detailed spec: detached JWT (RFC 7797), `signing_keys` in profile, key rotation with multiple keys, `kid` claim for key identification. | USP says webhooks "SHOULD be signed" (Section 11.3) but provides no detail. No signing algorithm, no key format, no key rotation protocol, no verification algorithm. |

### 6.6 Contradictions Between USP and UCP

| # | USP Says | UCP Actually Says | Impact |
|---|----------|-------------------|--------|
| 1 | Operation is called `submit_checkout` (Sections 2.1.4, 2.6, 7.2, 8.1, 8.3) | Operation is `complete_checkout` (`POST /checkout-sessions/{id}/complete`) | Implementers following USP will call a non-existent UCP endpoint. Must be corrected. |
| 2 | UCP checkout status `ready_for_complete` is referenced in Section 7.2 | UCP uses `ready_for_complete` (correct). However, USP also references `status: pending` as the trigger for UCP checkout creation (Section 7.1 text), which contradicts its own booking lifecycle where `requires_action` is the correct trigger. | Confusion about which booking status triggers UCP checkout. The text in Section 7.1 still says "the platform creates a UCP checkout session when `status` is `pending`." Should be `requires_action`. |
| 3 | USP capabilities use arrays: `"capabilities": [{"name": "...", ...}]` | UCP capabilities use registries: `"capabilities": {"dev.ucp.shopping.checkout": [{...}]}` | A platform implementing both must handle two different capability formats. Breaks the "consistent with UCP" claim. |
| 4 | USP services use a flat object with transport keys (`"rest": {...}`, `"mcp": {...}`) | UCP services use an array of objects with `"transport"` discriminator | Same business, two incompatible service discovery formats. |
| 5 | USP errors use HTTP status codes for business outcomes (404, 409, 422) | UCP returns HTTP 200 for business outcomes with `messages[]` array | A platform that uses UCP's error handling pattern will miss USP errors and vice versa. |
| 6 | USP `messages[].severity` values: `requires_buyer_input`, `informational`, `actionable` | UCP `messages[].severity` values: `recoverable`, `requires_buyer_input`, `requires_buyer_review` | Only `requires_buyer_input` overlaps. The others are incompatible. |
| 7 | USP specifies `messages[].message` for human-readable text | UCP uses `messages[].content` for the same purpose | Field name mismatch on an otherwise identical concept. |

### 6.7 Unnecessary Overlaps

The following constructs are duplicated between USP and UCP where USP could
have directly imported or referenced UCP's definitions:

| Construct | In USP | In UCP | Could USP Reuse UCP's? |
|-----------|--------|--------|------------------------|
| **Services** (transport bindings) | Section 2.4 / 3.1 | `overview.md` — Services section | **Yes.** Same concept, different wire format. USP should import UCP's service schema. |
| **Capabilities** (feature declaration) | Section 2.4 / 3.3 | `overview.md` — Capabilities section | **Yes.** Same concept, different wire format. USP should use UCP's registry pattern. |
| **Extensions** (optional modules) | Section 2.4 | `overview.md` — Extensions section | **Yes.** USP describes extensions but doesn't define the schema composition (`allOf`, `$defs`) that makes UCP extensions actually work. |
| **Namespace governance** | Section 3.2 | `overview.md` — Namespace Governance | **Yes.** Identical rules. Should be a shared reference. |
| **Capability negotiation** | Section 3.3 | `overview.md` — Negotiation Protocol | **Partially.** Same server-selects model, but USP omits many details UCP includes (intersection algorithm, orphaned extension pruning, error codes). |
| **Platform profile advertisement** | `USP-Agent` header | `UCP-Agent` header | **Partially.** Same concept but different header names, preventing a unified implementation. |
| **`continue_url`** | Section 6.2 (booking) | `checkout.md` — Continue URL section | **Yes.** Same concept for buyer handoff. |
| **Buyer object** | `{first_name, last_name, email, phone_number}` | `buyer` entity in checkout | **Almost.** Similar fields but USP's buyer is simpler (no `consent`, no structured address). |

### 6.8 Summary of Recommendations

The following table summarizes what USP must fix:

| # | Category | Priority | Recommendation |
|---|----------|----------|----------------|
| 6.1 | Services construct | **High** | Align USP's service definition wire format with UCP's array-of-transport-objects pattern, or define a shared base schema. |
| 6.2 | Capability format | **High** | Adopt UCP's registry pattern (`object keyed by name`) instead of arrays for capabilities in profiles and responses. |
| 6.3 | Error model | **High** | Adopt UCP's error model: HTTP 200 for business outcomes with `messages[]`, matching severity values, and `content` (not `message`). |
| 6.4 | `submit_checkout` | **Critical** | Replace all references to `submit_checkout` with `complete_checkout`. This is a factual error. |
| 6.5 | Missing capabilities | **Medium** | Add identity linking, webhook signature spec, and consent mechanism. Consider post-booking lifecycle (equivalent to UCP's Order capability). |
| 6.6 | Contradictions | **High** | Fix all 7 contradictions identified above, especially the wire format inconsistencies that break the "consistent with UCP" positioning. |
| 6.7 | Overlaps | **Medium** | Import shared constructs (namespace governance, negotiation, service definitions) from UCP by reference rather than re-specifying them with incompatible formats. |
| 6.9 | Payment architecture depth | **High** | USP's payment bridge ignores UCP's Trust Triangle, PCI-DSS scope guidance, SCA/3DS challenge flow, risk signals, and payment handler filtering. |
| 6.10 | Versioning | **High** | Define a versioning strategy (format, negotiation, backwards-compatibility rules). USP currently has none. |
| 6.11 | Embedded scheduling UI | **Medium** | Consider an embedded scheduling protocol analogous to UCP's ECP — would enable in-app booking UIs with delegation for payment and address. |
| 6.12 | Operational completeness | **Medium** | Add idempotency specification, glossary of terms, and formal transport error code mappings. |

### 6.9 Payment Architecture Depth: What USP's Bridge Model Misses

USP's companion-protocol bridge
to UCP for payments introduces unnecessary complexity. After a complete read of
UCP's Payment Architecture section (overview.md — previously truncated), the
gap is even wider than initially assessed. UCP's payment system is a deeply
engineered, multi-participant security architecture that USP's lightweight
bridge cannot leverage.

#### 6.9.1 The Trust Triangle

UCP defines a "Trust-by-Design" philosophy with three relationships:

1. **Business ↔ Payment Credential Provider:** Pre-existing legal and technical
   relationship. The business holds API keys and a contract with the provider.
2. **Platform ↔ Payment Credential Provider:** The platform interacts with the
   provider's interface to tokenize data but is not the owner of funds.
3. **Platform ↔ Business:** The platform passes the result (token or mandate)
   to the business to finalize the order.

**USP impact:** USP's payment bridge (Section 7) never acknowledges this trust
model. When a USP booking requires payment, the spec says the platform "creates
a UCP checkout session" and "acquires a payment token from the PSP." But it
doesn't explain how the platform discovers which payment credential provider to
use, how the trust relationship is established, or how the business's handler
configuration drives the acquisition flow. The entire 3-step lifecycle
(Negotiation → Acquisition → Completion) that UCP defines is glossed over with
a single sentence.

#### 6.9.2 Payment Handler Framework

UCP's Payment Handler Guide (773 lines) defines a comprehensive framework with
5 core concepts:

| Concept | UCP Definition | USP Coverage |
|---------|---------------|--------------|
| **Participants** | Defines actors (Business, Platform, Tokenizer, PSP) with explicit roles | Not addressed |
| **Prerequisites** | Onboarding, identity establishment, `PaymentIdentity` schema | Not addressed |
| **Handler Declaration** | 3 variants (business_schema, platform_schema, response_schema) with JSON Schema `$defs` | Not addressed |
| **Instrument Acquisition** | Protocol for platform to acquire checkout instrument with binding context | Single sentence in Section 7.2 |
| **Processing** | Steps for business/PSP to process received instrument, error mapping | Not addressed |

UCP also provides 3 concrete payment handler examples:

- **Processor Tokenizer** (`com.example.processor_tokenizer`): Business or PSP
  hosts `/tokenize` endpoint. No detokenization needed — internal resolution.
- **Platform Tokenizer** (`com.example.platform_tokenizer`): Platform generates
  tokens and exposes `/detokenize` for businesses/PSPs to call back.
- **Encrypted Credential** (`com.example.encrypted_credential`): Platform
  encrypts credentials with business's public key. Zero runtime round-trips.

These patterns cover different security/compliance trade-offs. USP's bridge
model cannot express which pattern is in use or how the platform should behave
differently for each.

#### 6.9.3 PCI-DSS Scope Management

UCP dedicates a full subsection to PCI-DSS scope for each participant:

- **Platforms** can avoid PCI scope by using opaque credentials (tokens,
  encrypted payloads) and never accessing raw payment data.
- **Businesses** minimize scope by using provider-hosted tokenization or wallet
  providers.
- **Payment Credential Providers** are typically PCI-DSS Level 1 certified.

USP has no guidance on PCI-DSS scope for service bookings. For verticals like
healthcare (where payment data intersects with health data) or equipment rental
(where deposits may be large), this is a material gap.

#### 6.9.4 Risk Signals and SCA/3DS Challenges

UCP supports two mechanisms that USP ignores:

**Risk Signals:** The platform MAY include risk assessment data in the
`complete_checkout` call:

```json
{
  "risk_signals": {
    "session_id": "abc_123_xyz",
    "score": 0.95
  }
}
```

USP has no mechanism for platforms to pass fraud/risk signals during the
booking-payment flow.

**SCA/3DS Challenges:** When a payment requires Strong Customer Authentication,
UCP returns:

```json
{
  "status": "requires_escalation",
  "messages": [{
    "type": "error",
    "code": "requires_3ds",
    "content": "bank requires verification.",
    "severity": "requires_buyer_input"
  }],
  "continue_url": "https://psp.com/challenge/123"
}
```

The platform MUST open the `continue_url` in a WebView/Window for the user to
complete the bank check, then retry. USP's payment bridge makes no mention of
how SCA challenges are handled during a booking payment — a critical omission
for European bookings under PSD2.

#### 6.9.5 Dynamic Payment Handler Filtering

UCP requires: "Businesses **MUST** filter the `handlers` list based on the
context of the cart (e.g., removing Buy Now Pay Later for subscription items,
or filtering regional methods based on shipping address)."

For service bookings, handler filtering should consider:
- Service type (e.g., no BNPL for same-day appointments)
- Deposit vs. full payment (different handlers may apply)
- Geographic restrictions based on service location

USP's bridge has no mechanism for the business to dynamically filter handlers
based on the booking context.

### 6.10 Versioning: A Complete Gap

UCP defines a comprehensive versioning strategy (overview.md):

| Aspect | UCP | USP |
|--------|-----|-----|
| **Version format** | `YYYY-MM-DD` date-based | Version date exists (`2026-02-09`) but format is not formally specified |
| **Version negotiation** | Platform ≤ Business → process; Platform > Business → `version_unsupported` error | Not defined |
| **Backwards compatibility rules** | Explicit lists of breaking vs. non-breaking changes | Not defined |
| **Independent component versioning** | Protocol versions independently from capabilities; `dev.ucp.*` vs `com.{vendor}.*` | Not defined |
| **Version in responses** | `ucp.version` in every response confirms the version used | `usp.version` exists but negotiation logic is absent |

For USP to be a viable standard, it **MUST** define:

1. A version format and its semantics.
2. How platforms and businesses negotiate compatible versions.
3. What constitutes a breaking change to USP's schemas and operations.
4. How USP capability versions relate to the protocol version.

Without this, implementers have no guidance on forward/backward compatibility,
and any schema change could silently break existing integrations.

### 6.11 Embedded Scheduling UI: A Missing Modality

UCP's Embedded Checkout Protocol (ECP, 1391 lines) is a sophisticated protocol
enabling a host to embed a business's checkout UI while maintaining delegation
control over payment and fulfillment. Key features:

- **W3C Payment Request API alignment** — familiar patterns for web developers
- **Delegation negotiation** — host requests delegations via `ec_delegate` URL
  parameter; business accepts/rejects in `ec.ready` handshake; narrowing chain:
  `config.delegate ⊇ ec_delegate ⊇ ec.ready delegate`
- **JSON-RPC 2.0 messaging** — structured bidirectional communication:
  - Core: `ec.ready`, `ec.start`, `ec.complete`
  - State changes: `ec.line_items.change`, `ec.buyer.change`, `ec.payment.change`
  - Delegation requests: `ec.payment.credential_request`,
    `ec.fulfillment.address_change_request`
- **Communication channels** — `MessageChannel` for web hosts, injected globals
  for native hosts (`window.EmbeddedCheckoutProtocolConsumer`)
- **Security** — CSP directives, iframe sandbox attributes, credentialless
  iframes, prevention of unsolicited payment requests

USP's `continue_url` only supports a redirect-based flow (open in browser/
WebView). An **Embedded Scheduling Protocol (ESP)** analogous to ECP would
enable platforms to embed a business's scheduling UI with delegation for:

| ECP Delegation | Analogous ESP Delegation |
|----------------|--------------------------|
| `payment.credential` — host provides payment token | `scheduling.slot_selection` — host provides native date/time picker |
| `payment.instruments_change` — host shows payment method selection | `scheduling.resource_selection` — host shows staff/room picker |
| `fulfillment.address_change` — host shows address picker | `scheduling.party_details` — host provides participant info |

This would enable rich in-app booking experiences (e.g., an AI agent rendering
a native calendar widget for slot selection while the business's embedded UI
handles service-specific questions).

### 6.12 Operational Completeness Gaps

Several operational concerns that UCP specifies but USP omits:

#### 6.12.1 Idempotency

UCP's REST binding defines `Idempotency-Key` header semantics:
- State-modifying operations SHOULD support idempotency.
- Server MUST store the key with the result for at least 24 hours.
- Server MUST return cached result for duplicate keys.
- Server MUST return `409 Conflict` if key is reused with different parameters.

USP has no idempotency specification. For booking operations (which involve
real-world resource allocation), idempotency is critical. Network retries
without idempotency keys could create duplicate bookings.

#### 6.12.2 Glossary of Terms

UCP provides a formal glossary defining 12 core terms: AP2, A2A, Capability,
Credential Provider, Extension, Profile, Business, MCP, UCP, PSP, Platform,
VDC.

USP has no glossary. Terms like "hold," "slot," "booking," "capability,"
"service vertical," and "confirmation mode" are used throughout but never
formally defined. This was noted in Section 1 of this review (RFC Format
Deviations) and is reinforced by the UCP comparison — a companion protocol
should share terminology definitions with its parent.

#### 6.12.3 Transport Error Code Mapping

UCP provides explicit error code mapping across transports:

| Error | REST | MCP |
|-------|------|-----|
| Invalid profile URL | 400 | -32001 |
| Profile unreachable | 424 | -32001 |
| Profile malformed | 422 | -32001 |
| Authentication required | 401 | -32000 |
| Rate limit | 429 | -32000 |
| Server error | 500 | -32603 |

USP claims three transport bindings (REST, MCP, A2A) but provides no error
code mapping across them (as noted in Section 5.8 of this review). UCP's
mapping table should be adopted as the baseline for USP's transport bindings.

### 6.13 Companion Protocol vs. UCP Extension: The Core Positioning Question

This is the most consequential question: **should USP's commerce-related
parts be modeled as a UCP extension rather than a separate companion protocol?**

Sections 6.1–6.12 above document the full inventory of issues — wire format
divergences, missing capabilities, contradictions, unnecessary overlaps,
payment architecture gaps, versioning gaps, and operational completeness gaps.
This section proposes an alternative architectural model (USP as a set of UCP
extensions) and evaluates how it affects every issue identified above.

#### 6.13.1 How UCP Extensions Work

UCP has a mature, well-defined extension system (see UCP `overview.md` — Schema
Composition section):

1. Extensions declare parent capabilities via the `extends` field.
2. Extension schemas use `allOf` composition with `$defs` keyed by the
   parent capability's full name.
3. Extensions can add new fields to existing objects (e.g., `discount` adds
   a `discounts` object to checkout; `fulfillment` adds a `fulfillment` object
   to checkout).
4. Multi-parent extensions are supported (e.g., discount extends both checkout
   and cart).
5. Platforms resolve composed schemas client-side by fetching base + extension
   schemas.

Existing UCP extensions include:
- `dev.ucp.shopping.fulfillment` (extends checkout — adds shipping/pickup)
- `dev.ucp.shopping.discount` (extends checkout — adds discount codes)
- `dev.ucp.shopping.buyer_consent` (extends checkout — adds consent fields)
- `dev.ucp.shopping.ap2_mandate` (extends checkout — adds cryptographic
  mandates)
- `dev.ucp.shopping.cart` (standalone capability, with cart-to-checkout
  conversion)

#### 6.13.2 What the USP–UCP Bridge Currently Looks Like

When a USP booking requires payment, the current flow is:

1. **[USP]** Platform calls `create_booking` → Business returns booking with
   `status: requires_action`.
2. **[UCP]** Platform must now separately:
   a. Discover the business's UCP endpoint (`/.well-known/ucp`)
   b. Negotiate UCP capabilities
   c. Call `create_checkout` with manually constructed line items + a
      non-standard `usp_booking` metadata object
   d. Call `update_checkout` with fulfillment info
   e. Acquire a payment token from the PSP via UCP's payment handler
   f. Call `complete_checkout` with the token
3. **[USP]** Business internally links the UCP order back to the USP booking
   via `usp_booking.booking_id`.
4. **[USP]** Business sends `booking.confirmed` webhook.

**Problems with this approach:**

| Problem | Description |
|---------|-------------|
| **Protocol switching complexity** | The platform must implement two complete protocol stacks with different wire formats, error models, and negotiation patterns. For a single booking-with-payment flow, the platform makes ~6 API calls across two protocols. |
| **Non-standard bridging** | The `usp_booking` metadata is an ad-hoc field injected into UCP's `create_checkout` request. UCP has no schema for this. It's not discoverable, not validated, and not part of any capability negotiation. |
| **Dual discovery burden** | Businesses must publish and maintain both `/.well-known/usp` and `/.well-known/ucp`. Platforms must discover, fetch, and negotiate with both endpoints independently. |
| **Line item mapping is fragile** | USP Section 7.3 defines a manual mapping: `item.id` = `booking.service_id`, `item.price` = `booking.payment.amount / booking.party_size`. This is an implicit contract not enforced by any schema. If UCP or USP evolves, this mapping silently breaks. |
| **No atomicity** | The USP booking and UCP checkout are separate resources with separate lifecycles. If the UCP checkout fails after the USP booking was created, the platform must manually clean up the dangling USP booking. There's no transactional guarantee. |
| **Redundant buyer data** | The buyer's identity is sent twice — once in the USP `create_booking` request and again in the UCP `create_checkout` request. These must match, but nothing enforces that. |

#### 6.13.3 How a UCP Extension Model Would Work

Instead of USP being a fully separate companion protocol, the **commerce-
related parts** of USP could be modeled as a UCP extension. USP maintains
governance independence via its own `dev.usp` namespace — cross-namespace
extension is a supported UCP pattern. Concretely:

**New USP capabilities under `dev.usp.services.*`:**

| Capability | Type | Description |
|------------|------|-------------|
| `dev.usp.services.catalog` | Standalone | Service catalog (discovery, listing, feed). Same as current USP catalog. |
| `dev.usp.services.availability` | Standalone | Availability queries and slot holds. Same as current USP availability. |
| `dev.usp.services.scheduling` | Standalone | Booking lifecycle (create, confirm, cancel, get). Operates independently for non-commerce (free) services. This is the core domain capability that manages bookings regardless of whether payment is involved. |
| `dev.usp.services.bookings` | Extension (`extends: dev.ucp.shopping.checkout`) | Wires the booking context (slot, service_id, hold_id, booking status) into UCP checkout for paid services. Analogous to how `fulfillment` adds shipping/pickup context to checkout. |

The `dev.usp.services.bookings` extension would add a `booking` object
to checkout, analogous to how `fulfillment` adds a `fulfillment` object:

```json
{
  "dev.usp.services.bookings": [{
    "version": "2026-02-09",
    "spec": "https://usp.dev/specification/bookings",
    "schema": "https://usp.dev/schemas/services/bookings.json",
    "extends": "dev.ucp.shopping.checkout"
  }]
}
```

The checkout response with the bookings extension would look like:

```json
{
  "ucp": {
    "version": "2026-01-11",
    "capabilities": {
      "dev.ucp.shopping.checkout": [{"version": "2026-01-11"}],
      "dev.usp.services.bookings": [{"version": "2026-02-09"}]
    },
    "payment_handlers": { "..." : "..." }
  },
  "id": "chk_abc123",
  "status": "incomplete",
  "line_items": [
    {
      "id": "li_1",
      "item": {"id": "svc_massage_001", "title": "Deep Tissue Massage", "price": 12000},
      "quantity": 1
    }
  ],
  "booking": {
    "booking_id": "bkg_456def",
    "service_id": "svc_massage_001",
    "service_type": "appointment",
    "slot": {
      "id": "slot_20260316_1400",
      "start": "2026-03-16T14:00:00-04:00",
      "end": "2026-03-16T15:00:00-04:00",
      "duration": "PT60M"
    },
    "hold_id": "hold_xyz789",
    "resources": [{"id": "staff_jane", "type": "staff", "name": "Jane Smith"}],
    "booking_status": "requires_action",
    "confirmation_mode": "auto"
  },
  "totals": [ "..." ]
}
```

**Benefits of this model:**

Each benefit below directly resolves one or more of the problems identified in
Section 6.13.2:

| Benefit | Description | Resolves (6.13.2) |
|---------|-------------|-------------------|
| **Single protocol for payment** | No protocol switching. The `create_checkout` call already carries the booking context via the `dev.usp.services.bookings` extension. `complete_checkout` atomically finalizes both payment and booking. Platforms implement one protocol stack, one wire format, and one error model. | Protocol switching complexity |
| **Dramatically fewer API calls** | The current bridge model requires **~6 API calls across two protocols**: `create_booking` (USP), discover `/.well-known/ucp`, negotiate UCP capabilities, `create_checkout`, `update_checkout`, acquire payment token, `complete_checkout`. Under the extension model, the entire flow is **~3–4 calls within a single protocol**: `create_checkout` (with booking context), acquire payment token, `complete_checkout`. The separate USP booking creation, UCP discovery, and UCP capability negotiation steps are eliminated entirely. | Protocol switching complexity |
| **`usp_booking` metadata eliminated** | The `booking` object is a first-class, schema-validated, discoverable extension field — not an ad-hoc metadata injection. It participates in capability negotiation and schema composition like every other UCP extension. | Non-standard bridging |
| **Single discovery endpoint** | Business publishes `/.well-known/ucp` with shopping, scheduling, and bookings capabilities. Platform discovers and negotiates everything in one pass. No need to maintain or query a separate `/.well-known/usp` endpoint. | Dual discovery burden |
| **Schema composition** | The bookings extension schema is validated alongside checkout via UCP's `allOf` composition. Service-to-line-item mapping is enforced by the composed schema, not by an implicit, undocumented contract. | Fragile line-item mapping |
| **Atomicity** | A single `complete_checkout` call finalizes both payment and booking confirmation. If payment fails, no dangling USP booking is created. If booking fails, the checkout fails atomically. There is no cross-protocol cleanup to orchestrate. | No atomicity |
| **Buyer data sent once** | The buyer's identity is part of the UCP checkout — it is provided once and applies to both payment and booking. No redundant submissions, no risk of mismatch between USP and UCP buyer objects. | Redundant buyer data |
| **UCP's payment architecture is inherited** | Payment handlers, AP2 mandates, buyer consent, embedded checkout — all "just work" for service bookings without USP re-specifying or bridging to them. | Protocol switching complexity, Non-standard bridging |
| **Consistent error model** | Uses UCP's `messages[]` array with `severity` and `path` for all errors, including booking-specific ones. Platforms do not need to translate between two incompatible error models. | Protocol switching complexity |
| **Inherited non-scheduling infrastructure** | A viable, state-of-the-art scheduling protocol must still support identity linking, transport layer bindings, webhook signature verification, consent management, embedded UI, versioning, and namespace governance. Maintaining all of these independently is a massive undertaking. As a UCP extension, USP inherits all of this infrastructure for free — its maintainers can focus exclusively on the core scheduling domain (catalog, availability, booking lifecycle). This is likely to have a direct impact on adoption and utility: it is always better to ride on the shoulders of giants than to rebuild the giant from scratch. | Protocol switching complexity, Dual discovery burden |

**What stays standalone (not a UCP extension):**

- `dev.usp.services.catalog` — service catalog, listing, feed. Pure discovery
  with no payment involvement.
- `dev.usp.services.availability` — slot queries, holds. Also no payment
  involvement.
- `dev.usp.services.scheduling` — booking lifecycle (create, confirm, cancel,
  get). This is the core domain capability. For free services it operates
  entirely on its own. For paid services, the `dev.usp.services.bookings`
  extension wires it into UCP checkout.
- `dev.usp.services.waitlist` — waitlist management. Extends the scheduling
  capability.

##### 6.13.3.1 UCP's Roadmap Confirms the Overlap Trajectory

The UCP README's "What's Next" section explicitly lists expanding UCP into
**Services** verticals as a planned direction. This directly validates the
concern that if UCP itself plans to cover services, USP's
separate-protocol approach risks being superseded by UCP's native services
capabilities. This makes it even more strategic for USP to position itself
**within** UCP's extension system rather than alongside it.

#### 6.13.4 The Non-Commerce Case

The four-capability split cleanly separates the non-commerce and commerce
cases. When a service has `requires_payment: false`:

- The business publishes `dev.usp.services.catalog`,
  `dev.usp.services.availability`, and `dev.usp.services.scheduling`
  capabilities but does **not** publish `dev.ucp.shopping.checkout` or
  `dev.usp.services.bookings`.
- The `dev.usp.services.scheduling` capability provides the full booking
  lifecycle (create, confirm, cancel, get) via its own API endpoints —
  no UCP checkout is involved.
- Platforms discover and use scheduling exactly the same way they would
  any other standalone UCP capability.

When a service has `requires_payment: true`:

- The business additionally publishes `dev.ucp.shopping.checkout` and
  `dev.usp.services.bookings`.
- The `dev.usp.services.bookings` extension adds a `booking` object to
  the UCP checkout, carrying the slot, service, hold, and booking status.
- `complete_checkout` atomically finalizes both payment and booking.

This mirrors how UCP's `cart` capability can operate independently from
checkout (as a pre-purchase exploration tool), while `checkout` composes
cart items into a payment flow when commerce is involved.

#### 6.13.5 Recommendation

**Model USP as four capabilities under the `dev.usp.services` namespace:
`dev.usp.services.catalog` (standalone), `dev.usp.services.availability`
(standalone), `dev.usp.services.scheduling` (standalone), and
`dev.usp.services.bookings` (extension of `dev.ucp.shopping.checkout`).** USP
maintains governance independence via its own `dev.usp` namespace while
leveraging UCP's extension architecture — cross-namespace extension is a
supported UCP pattern.

This:
1. Eliminates the `usp_booking` metadata hack.
2. Gives businesses a single discovery endpoint.
3. Gives platforms a single protocol stack with one error model.
4. Leverages UCP's payment handlers, AP2 mandates, and embedded checkout
   automatically.
5. Preserves USP's standalone capabilities (catalog, availability, scheduling,
   waitlist) for the non-commerce case.
6. Cleanly separates the domain concern (scheduling) from the commerce
   concern (bookings) — the same booking lifecycle capability works for both
   free and paid services, with the bookings extension adding payment
   integration only when needed.

If the USP team prefers to keep USP as a separate protocol (for governance
or branding reasons), it should at minimum:
- Adopt UCP's wire formats exactly (registry pattern for capabilities, array
  pattern for services, messages array for errors).
- Define `usp_booking` as a formal UCP extension schema rather than ad-hoc
  metadata.
- Use `complete_checkout` (not `submit_checkout`) throughout.

#### 6.13.6 Comprehensive Impact Analysis: Extension Model vs. Companion Model

Sections 6.1–6.12 document every issue identified in this review under the
assumption that USP remains a standalone companion protocol. Section 6.8
summarizes the fixes required under that model. The table below evaluates
**every issue** under the extension model to quantify the delta — how many
problems are eliminated, simplified, or unchanged.

**Section 5: Original Specification Recommendations**

| # | Issue | Companion Model (fix required) | Extension Model | Status |
|---|-------|-------------------------------|-----------------|--------|
| 1 | RFC Format (Abstract, ToC, etc.) | Must add all standard sections | Must add all standard sections | **Still applies** |
| 2 | Problem Statement | Must rewrite to acknowledge existing standards | Simplified: USP is a scheduling extension of UCP, not a new protocol. Value prop is clearer. | **Simplified** |
| 3 | Verticals / extension mechanism | Must define an extension mechanism for verticals | Extension mechanism inherited from UCP (sub-extensions of `dev.usp.services.*`) | **Simplified** |
| 4 | Commerce vs. Non-Commerce separation | Must add explicit operational modes and conditional payment fields | Inherently resolved by capability split: `scheduling` (standalone) vs. `bookings` (extends checkout) | **Resolved** |
| 5.1 | Catalog Feed | Must define a feed endpoint from scratch | Can follow UCP's existing catalog feed model (cursor-based pagination, `If-None-Match`) | **Simplified** |
| 5.2 | Validation Rules | Must define JSON Schema constraints from scratch | UCP's `allOf` schema composition provides the validation framework | **Simplified** |
| 5.3 | Field Descriptions | Must expand schema field descriptions | Must expand schema field descriptions | **Still applies** |
| 5.4 | Request/Response Labels | Must add labels to all JSON snippets | Must add labels to all JSON snippets | **Still applies** |
| 5.5 | Hold Placement | Must reorder sections | Must reorder sections | **Still applies** |
| 5.6 | Status Bug (`pending` → `requires_action`) | Must fix the status reference | Eliminated: UCP checkout status drives the flow; no separate booking status triggers payment | **Resolved** |
| 5.7 | Cross-Ref Link to Line Item Mapping | Must add anchor link | Eliminated: no separate line-item mapping exists | **Resolved** |
| 5.8 | Service Bindings (MCP, A2A) | Must specify all three binding details | Transport bindings inherited from UCP; only standalone capability bindings need specifying | **Simplified** |
| 5.9 | Waitlist | Must define full waitlist extension | Must define full waitlist extension (`dev.usp.services.waitlist`) | **Still applies** |

**Section 6.1–6.4: Wire Format and Factual Issues**

| # | Issue | Companion Model (fix required) | Extension Model | Status |
|---|-------|-------------------------------|-----------------|--------|
| 6.1 | Services construct (incompatible wire format) | Must align USP's flat-object service format with UCP's array-of-transport-objects | Eliminated: USP capabilities are registered in UCP's profile using UCP's service schema format | **Resolved** |
| 6.2 | Capability format (array vs. registry) | Must convert from array pattern to UCP's registry pattern | Eliminated: extensions must use UCP's registry pattern — no alternative format exists | **Resolved** |
| 6.3 | Error model divergence (HTTP codes vs. messages[]) | Must adopt UCP's error model, rewrite all error handling | Eliminated: as a UCP extension, the `messages[]` array with UCP's severity values is the only error model | **Resolved** |
| 6.4 | `submit_checkout` factual error | Must rename all 5 references to `complete_checkout` | Eliminated: USP doesn't reference UCP checkout operations separately — the booking context lives inside checkout | **Resolved** |

**Section 6.5: Missing Capabilities**

| # | Issue | Companion Model (fix required) | Extension Model | Status |
|---|-------|-------------------------------|-----------------|--------|
| 6.5a | Identity Linking | Must design and specify an authentication/identity model from scratch | Inherited: `dev.ucp.common.identity_linking` (OAuth 2.0, scoped tokens, RISC) works for scheduling bookings | **Resolved** |
| 6.5b | Order Management (post-booking lifecycle) | Must design refund tracking, dispute resolution, adjustment logging | Inherited: `dev.ucp.shopping.order` provides post-checkout lifecycle, fulfillment events, adjustments | **Resolved** |
| 6.5c | AP2 Mandates (cryptographic integrity) | Must design a booking agreement integrity mechanism | Inherited: AP2 mandates automatically protect the `booking` extension field within checkout | **Resolved** |
| 6.5d | Embedded Checkout | Must design an embedded scheduling UI protocol from scratch (see 6.11) | Inherited: UCP's ECP (Embedded Checkout Protocol) works for checkout with booking context | **Resolved** |
| 6.5e | Buyer Consent | Must design consent categories and transmission mechanism | Inherited: `dev.ucp.shopping.buyer_consent` applies to checkout including booking data | **Resolved** |
| 6.5f | Discount | Must design discount/promo mechanism for services | Inherited: `dev.ucp.shopping.discount` applies to line items including service bookings | **Resolved** |
| 6.5g | Webhook Signature Verification | Must specify signing algorithm, key format, rotation protocol | Inherited: UCP's detached JWT (RFC 7797) signing, `signing_keys` in profile, `kid` claim | **Resolved** |

**Section 6.6: Contradictions**

| # | Issue | Companion Model (fix required) | Extension Model | Status |
|---|-------|-------------------------------|-----------------|--------|
| 6.6.1 | `submit_checkout` → `complete_checkout` | Must rename | Eliminated: no separate reference to UCP operations | **Resolved** |
| 6.6.2 | `pending` vs. `requires_action` status trigger | Must fix status reference | Eliminated: UCP checkout status drives the flow | **Resolved** |
| 6.6.3 | Capability format (array vs. registry) | Must convert format | Eliminated: must use UCP format for extensions | **Resolved** |
| 6.6.4 | Service format (flat vs. array) | Must convert format | Eliminated: must use UCP format | **Resolved** |
| 6.6.5 | Error model (HTTP codes vs. 200+messages) | Must adopt UCP model | Eliminated: inherits UCP model | **Resolved** |
| 6.6.6 | Severity values mismatch | Must align severity values | Eliminated: uses UCP's severity values | **Resolved** |
| 6.6.7 | `message` vs. `content` field name | Must rename field | Eliminated: uses UCP's field names | **Resolved** |

**Section 6.7: Unnecessary Overlaps**

| # | Issue | Companion Model (fix required) | Extension Model | Status |
|---|-------|-------------------------------|-----------------|--------|
| 6.7a | Services (transport bindings) | Must align wire format or define shared schema | Eliminated: uses UCP's service schema | **Resolved** |
| 6.7b | Capabilities (feature declaration) | Must adopt registry pattern | Eliminated: uses UCP's registry pattern | **Resolved** |
| 6.7c | Extensions (optional modules) | Must implement `allOf`/`$defs` composition | Eliminated: inherits UCP's schema composition | **Resolved** |
| 6.7d | Namespace governance | Must align or reference UCP's | Eliminated: operates within UCP's namespace governance (own `dev.usp` namespace) | **Resolved** |
| 6.7e | Capability negotiation | Must add intersection algorithm, orphan pruning, error codes | Inherited: UCP's negotiation protocol (intersection, pruning, errors) applies | **Resolved** |
| 6.7f | Platform profile (`USP-Agent` vs. `UCP-Agent`) | Must align or merge header | Eliminated: single `UCP-Agent` header covers all capabilities | **Resolved** |
| 6.7g | `continue_url` | Must align with UCP's definition | Inherited: UCP checkout's `continue_url` is the single handoff mechanism | **Resolved** |
| 6.7h | Buyer object | Must align fields or reference UCP's buyer entity | Inherited: UCP's `buyer` entity (with consent, structured address) is used | **Resolved** |

**Sections 6.9–6.12: Deeper Gaps**

| # | Issue | Companion Model (fix required) | Extension Model | Status |
|---|-------|-------------------------------|-----------------|--------|
| 6.9 | Payment architecture (Trust Triangle, handlers, PCI-DSS, SCA/3DS, filtering) | Must design or bridge to all 5 payment subsystems | Inherited: all 5 subsystems work for the `booking` extension field within checkout | **Resolved** |
| 6.10 | Versioning (format, negotiation, compatibility rules) | Must design a complete versioning strategy from scratch | Partially resolved: capability versioning follows UCP's `YYYY-MM-DD` format and negotiation rules. USP must still define what constitutes a breaking change to its own scheduling schemas. | **Simplified** |
| 6.11 | Embedded Scheduling UI | Must design a 1000+ line embedded protocol from scratch | Simplified: UCP's ECP (1391 lines) handles the embedded checkout flow. Scheduling-specific delegations (slot selection, resource picker) are additive, not a ground-up design. | **Simplified** |
| 6.12a | Idempotency | Must specify `Idempotency-Key` semantics from scratch | Inherited: UCP's REST binding already defines idempotency key semantics | **Resolved** |
| 6.12b | Glossary of Terms | Must define all terms from scratch | Partially resolved: UCP's 12-term glossary is inherited. Scheduling-specific terms (hold, slot, booking, etc.) still need defining. | **Simplified** |
| 6.12c | Transport Error Code Mapping | Must define REST/MCP/A2A error code mapping from scratch | Inherited: UCP's error code mapping table applies. Scheduling-specific errors are additive. | **Resolved** |
| 6.12d | Roadmap overlap risk | Risk of being superseded by UCP's planned services expansion | Eliminated: USP *is* the services expansion within UCP's ecosystem | **Resolved** |

---

**Aggregate Summary:**

| Status | Count | Percentage |
|--------|-------|------------|
| **Resolved** (no fix needed under extension model) | 40 | 77% |
| **Simplified** (less work needed under extension model) | 8 | 15% |
| **Still applies** (same work either way) | 4 | 8% |
| **Total issues** | 52 | 100% |

Under the companion model, all 52 issues require attention — ranging from
critical factual corrections to full subsystem designs. Under the extension
model, **40 of 52 issues (77%) are fully resolved** by architectural
inheritance, 8 are significantly simplified, and only 4 remain unchanged
(RFC document formatting, field descriptions, request/response labels, and
waitlist specification). The 4 unchanged issues are all documentation-quality
concerns, not architectural ones.

**The delta is stark:** the companion model requires USP to independently
design, specify, and maintain identity linking, error handling, payment
architecture, versioning, capability negotiation, webhook signing, consent
management, embedded UI, idempotency, and transport error mapping — all of
which UCP already provides. The extension model lets USP's maintainers focus
on the one thing that is genuinely unique to scheduling: **the domain logic of
catalog, availability, slot holds, booking lifecycle, and waitlist management.**
