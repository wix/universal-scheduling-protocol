---
title: Roadmap
description: USP protocol roadmap — current draft status, planned healthcare and education verticals, recurring bookings, and contribution guidelines.
keywords: USP roadmap, scheduling protocol future, healthcare scheduling, education booking, contributing to USP
---

# Roadmap

USP is currently in **Draft** status (`v2026-02-21`). This page outlines
what's implemented, what's planned, and how to contribute.

---

## Current Status

### Core Protocol — Draft

The complete domain core is specified and has machine-readable artifacts:

| Component | Status | Artifacts |
|-----------|--------|-----------|
| Service Catalog | Specified | JSON Schema, OpenAPI, OpenRPC |
| Availability | Specified | JSON Schema, OpenAPI, OpenRPC |
| Booking Lifecycle | Specified | JSON Schema, OpenAPI, OpenRPC |
| Discovery Registry | Specified | JSON Schema, OpenAPI, OpenRPC |

### Deployment Modes — Draft

| Mode | Status | Notes |
|------|--------|-------|
| UCP-Native Mode | Specified | Includes paid bookings extension schema |
| Standalone Mode | Specified | Includes generic payment flow and ACP extension |

### Transport Bindings — Draft

| Binding | Status | Notes |
|---------|--------|-------|
| REST | Specified | OpenAPI 3.1.0, idempotency, pagination |
| MCP | Specified | OpenRPC, JSON-RPC 2.0 |
| A2A | Specified | Agent Card, task-type mapping |
| ESP | Specified | Embedded iframe protocol |

### Extensions — Draft

| Extension | Status | Notes |
|-----------|--------|-------|
| Waitlist | Specified | Join, offer, accept/decline lifecycle |

---

## Planned

### Future Service Verticals

The following scheduling domains are under consideration for future
standardization as either core verticals or standard extensions:

| Domain | Description | Key Challenges |
|--------|-------------|----------------|
| **Healthcare** | Medical appointments with HIPAA/GDPR compliance | Consent management, insurance verification, referral chains |
| **Education** | Course enrollment, tutoring sessions | Semester-based scheduling, prerequisites, cohort management |
| **Government** | Permit appointments, public services | Multi-step workflows, document requirements |
| **Events & Ticketing** | Concert tickets, sporting events | Dynamic pricing, seat selection, transfer/resale |
| **Professional Services** | Legal, financial, tax consultations | Conflict-of-interest checks, document exchange |
| **Wellness & Spa** | Multi-service packages, spa days | Service sequencing, room/equipment dependencies |

### Protocol Enhancements

- **Recurring bookings** — Series creation and management
- **Package/bundle support** — Multi-session packages with shared policies
- **Calendar sync** — iCalendar export/import for confirmed bookings
- **Buyer calendar free/busy** — Cross-reference buyer availability with
  business availability

---

## Contributing

USP is open source under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

### How to Contribute

1. **Read the specification** — Understand the current protocol design.
2. **Open an issue** — Propose changes, report problems, or suggest new
   features on the GitHub repository.
3. **Submit a pull request** — Contribute schema changes, spec
   clarifications, or new transport bindings.
4. **Join the discussion** — Participate in GitHub Discussions for
   broader protocol design conversations.

### Contribution Guidelines

- **Schema changes** go in `schemas/` as JSON Schema `$defs`.
  Binding files (`openapi/`, `openrpc/`) reference schemas via `$ref`.
- **Spec changes** go in `specification.md`. Follow the existing section
  numbering and RFC 2119 keyword conventions.
- **Breaking changes** require a new version date (`YYYY-MM-DD`) and
  must be documented in the changelog.

---

## Version History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| `2026-02-21` | 2026-02-21 | Draft | Current version. Full domain core, two deployment modes, four transport bindings. |
| `2026-02-09` | 2026-02-09 | Superseded | Initial draft. |
