# USP Website — Build Plan

**Goal:** Build usp.dev to the same level as ucp.dev  
**Stack:** Material for MkDocs (same as UCP)  
**Source:** Content derived from `specification.md` + `README.md` in this repo  

---

## 1. Tech Stack & Config

| Component | Choice | Notes |
|-----------|--------|-------|
| Framework | Material for MkDocs | Same as UCP, markdown-based, spec-friendly |
| Fonts | Inter (body), JetBrains Mono (code) | Modern, readable |
| Color | Teal/emerald primary | Distinct from UCP's blue, conveys "time/scheduling" |
| Hosting | TBD (GitHub Pages / Netlify / Vercel) | Static site, deploys anywhere |
| Repo | This repo — `mkdocs.yml` at root, `site-docs/` for content | Spec + website live together |

### Files to create

```
mkdocs.yml                          # Already created
requirements.txt                    # Already created
overrides/
  home.html                         # Custom homepage template
site-docs/
  index.md                          # Homepage (front matter → home.html)
  core-concepts.md                  # Core Concepts page
  getting-started.md                # Quick Start / Implementer Guide
  security.md                       # Security page
  extensions.md                     # Extensions (waitlist, future)
  roadmap.md                        # Roadmap
  stylesheets/
    extra.css                       # All custom styles (hero, cards, sections)
  javascripts/
    extra.js                        # Tab switching, animations
  images/
    (placeholder for logos, diagrams)
  specification/
    index.md                        # Spec overview + reading guide
    service-catalog.md              # Section 3 of spec
    availability.md                 # Section 4 of spec
    booking.md                      # Section 5 of spec
    discovery-registry.md           # Section 6 of spec
  deployment-modes/
    index.md                        # Overview: UCP-Native vs Standalone
    ucp-native.md                   # Section 7 of spec
    standalone.md                   # Section 8 of spec
  transport/
    index.md                        # Transport bindings overview
    rest.md                         # Section 9.1
    mcp.md                          # Section 9.2
    a2a.md                          # Section 9.3
    esp.md                          # Section 9.5
```

---

## 2. Homepage Sections (Mirroring UCP)

Each section below maps to a corresponding section on ucp.dev, adapted for USP.

### 2.1 Hero

| Element | Content |
|---------|---------|
| Headline | Universal Scheduling Protocol |
| Tagline | The open standard for agentic scheduling. |
| Description | USP enables platforms and AI agents to discover, check availability of, and book time-based services — without custom integrations. |
| CTA Primary | **Get Started** → `/getting-started/` |
| CTA Secondary | **View on GitHub** → repo link |
| Visual | Gradient background (dark slate → teal) |

### 2.2 Problem Statement (unique to USP — UCP doesn't have this but it adds value)

> Existing standards (iCalendar, CalDAV, schema.org/Service) are fragmented, lack payment integration, and weren't designed for AI agents. USP unifies service discovery, real-time availability, booking lifecycle, and payment coordination into one open protocol.

### 2.3 Service Verticals (maps to UCP's "Industries Covered")

Four cards with icons:

| Vertical | Icon | Examples |
|----------|------|----------|
| Appointments | calendar-user | Salon, dental, consulting, personal training |
| Group Sessions | users | Yoga class, workshop, group fitness |
| Reservations | utensils | Restaurant table, conference room, venue |
| Rentals | car | Car rental, studio space, equipment hire |

### 2.4 Core Features — 4 Pillars (maps to UCP's "Scalable/Merchant-centric/Open/Secure")

| Pillar | Title | Description |
|--------|-------|-------------|
| 1 | Interoperable | A standard language for platforms and businesses to transact time-based services. Two deployment modes: UCP-Native and Standalone. |
| 2 | Agent-First | Every operation is designed for programmatic consumption. AI agents autonomously discover, evaluate, and book services with `continue_url` handoff when human input is needed. |
| 3 | Secure & Private | OAuth 2.0 identity linking, HTTP Message Signatures for webhooks, structured buyer consent, TLS 1.3 transport. References IETF standards directly. |
| 4 | Open & Extensible | Apache 2.0 licensed. Vendor extensions via reverse-domain namespaces. JSON Schema composition for custom capabilities. |

### 2.5 How It Works — 3-Step Flow (unique to USP)

Visual flow diagram:

```
1. Discover Services    →    2. Check Availability    →    3. Book
   POST /services/list        POST /availability/query      POST /bookings
   Browse the catalog         Find open time slots          Create the booking
```

### 2.6 See It In Action — Tabbed Code Examples (maps to UCP's tabbed Checkout/Identity/Order)

Three tabs with JSON request/response examples:

**Tab 1: Service Catalog**
- Request: `POST /services/list` with filters
- Response: Service object (haircut example from spec)

**Tab 2: Availability**  
- Request: `POST /availability/query` with date range
- Response: Time slots with state, resources, capacity

**Tab 3: Booking**
- Request: `POST /bookings` with service, slot, buyer
- Response: Confirmed booking object

### 2.7 Deployment Modes (unique to USP — key differentiator)

Two-column comparison:

| | UCP-Native Mode | Standalone Mode |
|--|-----------------|-----------------|
| When to use | Platform already supports UCP | Self-contained scheduling |
| Discovery | `/.well-known/ucp` | `/.well-known/usp` |
| Payment | UCP atomic checkout | Generic `payment_context` + any checkout system |
| Infrastructure | Inherited from UCP | IETF standards directly |

### 2.8 Transport Bindings (maps to UCP's "Built on industry standards")

Four cards:

| Binding | Description |
|---------|-------------|
| REST | HTTP/OpenAPI 3.x — primary transport with idempotency |
| MCP | JSON-RPC for AI agent tool use |
| A2A | Agent-to-Agent protocol for autonomous interactions |
| ESP | Embedded Scheduling Protocol for in-app booking UIs |

### 2.9 Ecosystem — Audience Cards (maps to UCP's Developers/Businesses/AI Platforms/Payment Providers)

Four cards with descriptions and CTAs:

| Audience | Headline | CTA |
|----------|----------|-----|
| Developers | Build scheduling into any platform with a standardized API | Read the Spec |
| Businesses | Retain control of your schedule, resources, and customer relationships | Get Started |
| AI Platforms | Enable agents to autonomously discover and book services | View Transport Bindings |
| Payment Providers | Integrate with USP through UCP or standalone payment paths | See Payment Architecture |

### 2.10 Co-Developed By (maps to UCP's logo section)

Placeholder section: "Co-developed by industry leaders" with space for partner logos. Text: "USP is an open, community-driven protocol. Join the conversation."

### 2.11 CTA Footer (maps to UCP's Download/Playground/Contribute)

Three action cards:

| Action | Icon | Description | Link |
|--------|------|-------------|------|
| Read the Specification | book | Full protocol spec with schemas and examples | `/specification/` |
| Explore the Schemas | code | OpenAPI, OpenRPC, and JSON Schema artifacts | GitHub `/schemas/` |
| Contribute | git-pull-request | Join the community and help shape the standard | GitHub repo |

---

## 3. Content Pages

### 3.1 Core Concepts (`core-concepts.md`)
Source: Spec Section 2

Content:
- Roles and Participants (Platform, Business, CP, PSP) — with diagram
- Commerce and Non-Commerce Services
- High-Level Architecture diagram (USP for scheduling, UCP for payment)
- Core Constructs (Capabilities, Extensions, Services)
- Namespace Governance
- Multi-Location Businesses
- Error Handling Overview

### 3.2 Getting Started (`getting-started.md`)
Source: README "Implementer Quick Start"

Content:
- Reading guide: "Everyone starts with domain core (Sections 1-5)"
- Decision table: UCP-Native vs Standalone
- Mermaid reading flow diagram (from README)
- Capabilities table
- Links to each spec section
- Machine-readable artifacts table (schemas, OpenAPI, OpenRPC)

### 3.3 Specification Overview (`specification/index.md`)
Source: Spec Table of Contents + Abstract

Content:
- Protocol abstract
- Full table of contents with links to subsections
- Version info and status
- Conventions (dates, durations, currency, timezones)
- Terminology definitions

### 3.4 Service Catalog (`specification/service-catalog.md`)
Source: Spec Section 3

Content:
- Catalog caching and indexing strategies
- Service schema (all fields)
- Duration, Pricing, Policies, Resources schemas
- Operations: List Services, Get Service
- Full JSON example

### 3.5 Availability (`specification/availability.md`)
Source: Spec Section 4

Content:
- Time Slot schema
- Hold schema
- Operations: Query Availability (slot + day granularity), Hold Slot, Release Slot
- Caching strategy (Browse → Select → Commit tiers)
- JSON examples for both granularity modes

### 3.6 Booking Lifecycle (`specification/booking.md`)
Source: Spec Section 5

Content:
- Status lifecycle diagram (pending → confirmed → completed, etc.)
- Booking schema (all fields)
- Operations: Create, Get, Update, Confirm, Cancel, Reschedule
- Webhooks table
- Post-booking lifecycle
- Full JSON examples

### 3.7 Discovery Registry (`specification/discovery-registry.md`)
Source: Spec Section 6

Content:
- Business Registration
- Business Search
- Service Search
- Registry Governance

### 3.8 UCP-Native Mode (`deployment-modes/ucp-native.md`)
Source: Spec Section 7

Content:
- When to use
- Profile registration in `/.well-known/ucp`
- Inherited infrastructure
- Paid Bookings extension schema
- Checkout flow and atomicity guarantee
- End-to-end flow diagrams (paid + free)

### 3.9 Standalone Mode (`deployment-modes/standalone.md`)
Source: Spec Section 8

Content:
- When to use
- Business Profile (`/.well-known/usp`)
- Capability negotiation
- Versioning
- Payment integration (generic, ACP, redirect)
- End-to-end flow diagrams
- Payment path comparison table

### 3.10 Transport Bindings — Overview (`transport/index.md`)

Summary of all four bindings with comparison table and links.

### 3.11 REST Binding (`transport/rest.md`)
Source: Spec Section 9.1

Content: Idempotency, pagination, discovery, request signing, conformance.

### 3.12 MCP Binding (`transport/mcp.md`)
Source: Spec Section 9.2

Content: Method mapping, request/response format, webhook notifications, conformance.

### 3.13 A2A Binding (`transport/a2a.md`)
Source: Spec Section 9.3

Content: Task-type mapping, end-to-end example, Agent Card, DataPart conventions, session management, conformance.

### 3.14 ESP Binding (`transport/esp.md`)
Source: Spec Section 9.5

Content: Message schemas, delegation negotiation, iframe security, example flow, error handling, conformance.

### 3.15 Security (`security.md`)
Source: Spec Sections 10

Content:
- USP security requirements
- Webhook security (HTTP Message Signatures)
- Authentication and authorization
- Rate limiting
- Hold abuse prevention
- Transport security

### 3.16 Extensions (`extensions.md`)
Source: Spec Section 11

Content:
- How extensions work
- Waitlist extension (full schema and operations)
- How to create vendor extensions

### 3.17 Roadmap (`roadmap.md`)

Content:
- Current status (Draft)
- What's implemented
- What's planned (future verticals from Appendix A)
- How to contribute

---

## 4. Design System

### Colors

| Token | Value | Usage |
|-------|-------|-------|
| Primary | `#0D9488` (teal-600) | Headers, links, buttons |
| Primary Light | `#14B8A6` (teal-500) | Hover states, accents |
| Primary Lighter | `#2DD4BF` (teal-400) | Highlights, badges |
| Primary Dark | `#0F766E` (teal-700) | Active states |
| Hero BG | `#0F172A → #134E4A` gradient | Hero section |
| Surface | `#F8FAFC` (slate-50) | Alternating section backgrounds |
| Text | `#1E293B` (slate-800) | Body text |
| Text Muted | `#64748B` (slate-500) | Secondary text |

### Typography

- Headings: Inter, 700 weight
- Body: Inter, 400 weight
- Code: JetBrains Mono, 400 weight
- Hero headline: 3.5rem
- Section headings: 2.25rem
- Card headings: 1.25rem

### Component Patterns

- **Feature cards**: White bg, subtle border, icon top, hover shadow
- **Code blocks**: Dark bg with syntax highlighting, copy button
- **Comparison tables**: Alternating row colors, sticky header
- **CTA buttons**: Teal filled (primary), white outlined (secondary)
- **Section layout**: Alternating white / slate-50 backgrounds, 80px vertical padding
- **Max content width**: 1200px centered

---

## 5. Build Order

| Phase | Files | Priority |
|-------|-------|----------|
| 1 | `mkdocs.yml`, `requirements.txt` | ✅ Done |
| 2 | `overrides/home.html`, `stylesheets/extra.css`, `index.md` | Homepage — the hero moment |
| 3 | `core-concepts.md`, `getting-started.md` | Top-level orientation pages |
| 4 | `specification/*.md` (catalog, availability, booking, registry) | Core spec content |
| 5 | `deployment-modes/*.md` | Deployment modes |
| 6 | `transport/*.md` | Transport bindings |
| 7 | `security.md`, `extensions.md`, `roadmap.md` | Supporting pages |
| 8 | Polish: diagrams, code examples, cross-links | Final pass |

---

## 6. Open Questions

- [ ] Domain: Will this be hosted at `usp.dev` or stay at `usp.base44.app`?
- [ ] Logos: Which partner/co-developer logos to include?
- [ ] GitHub repo: Will the spec repo go public? (affects repo links in nav)
- [ ] Playground: Should we build an interactive playground (like UCP has)?
- [ ] Analytics: Google Analytics property ID needed
