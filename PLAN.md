# Feature: Registry category ID filters and round-trip

## Goal
Define one ID-based value space for `categories[]` across business and service registry search, and make every emitted category ID reusable as a filter that matches the emitting result.

## Non-goals
- Change any product registry implementation.
- Add a category-listing operation or define a universal category taxonomy.
- Replace the existing human-readable `ServiceSearchResult.category` projection.
- Change catalog category display or localization behavior.

## Must-preserve constraints
- Canonical registry data shapes live only in `schemas/registry.json`; bindings remain thin `$ref` overlays.
- Business and service `categories[]` filters use the same category-ID value space and exact ID matching.
- `RegistryEntry.categories` remains the round-trippable source for business category IDs.
- `ServiceSearchResult.category` remains display text, while `category_ids` carries filter tokens.
- Every category ID emitted by either result type must be accepted by the corresponding search filter and match that result, subject to the other filters.
- Specification and site documentation remain synchronized and contain no implementation-specific normative prose or issue/PR references.
- Existing services without projected category IDs may still appear in unfiltered search; `category_ids` can be empty, but each emitted token must round-trip.

## File actions

| Path | Action | Reason |
|------|--------|--------|
| PLAN.md | modify | Replace the bootstrap placeholder with converged scope, constraints, work units, and verification. |
| schemas/registry.json | modify | Add one canonical category-ID array `$def`, reference it from registration, results, and both filters, and add service `category_ids`. |
| specification.md | modify | Define ID matching and round-trip semantics in Sections 3.3, 6.1, 6.2, 6.3, and 6.3.1, and disambiguate examples. |
| site-docs/specification/discovery-registry.md | modify | Mirror registry category ID and round-trip rules and examples on the published site. |
| openrpc/usp-mcp.json | modify | Replace inline registry category filter arrays with a thin component reference to the canonical schema definition. |
| CHANGE_LOG.md | modify | Record the rationale for the specification amendment using the required current identity and timestamp. |

## Work units

| ID | Description | Files | Verification | Status |
|----|-------------|-------|--------------|--------|
| U1 | Converge and commit the implementation plan | PLAN.md | `test -f PLAN.md` | done |
| U2 | Define canonical ID arrays and synchronized normative/site behavior | schemas/registry.json, specification.md, site-docs/specification/discovery-registry.md | Parse schema JSON and search changed prose/examples for consistent ID and round-trip terminology | done |
| U3 | Point MCP category filter parameters at the canonical schema | openrpc/usp-mcp.json | Parse OpenRPC JSON and confirm OpenAPI/OpenRPC search filters resolve through schema `$ref`s | pending |
| U4 | Add the required change log entry and run repository verification | CHANGE_LOG.md | Run schema/binding validation and the documentation build available in the repository | pending |

## Revisions

### 2026-08-26T08:18:00+03:00 - Iterative planning convergence
- Chose category IDs because catalog filter semantics and the existing service request schema already establish ID matching.
- Added a shared category-ID array definition so business and service filters cannot drift.
- Preserved display text separately and added `category_ids` to service results for round-trip filtering.
- Allowed an empty service `category_ids` projection so uncategorized or label-only catalog services are not silently excluded from otherwise valid unfiltered discovery.
