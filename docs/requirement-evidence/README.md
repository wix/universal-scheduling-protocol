# Requirement Evidence

**Status:** Non-normative documentation convention.

This directory records *why* a generic USP capability exists, by linking it to
dated public evidence of the real-world requirement it serves. It is
documentation, not a protocol schema and not a conformance surface. Nothing
here changes what a conforming implementation must do; the specification and
the schemas under `schemas/` do that.

## What a registry is for

Normative USP text and conformance vectors stay provider-neutral. A requirement
such as "decide eligibility before the buyer spends time picking a slot" must
stand on its own. Evidence explains where the need came from, so a reviewer can
judge whether a capability is justified and whether its justification is still
current.

A registry entry **never** claims that USP interoperates with, implements,
certifies, or is compatible with a named product. It does not contain source
payload mappings, simulated provider adapters, or copied provider schemas.

## Files

Each topical registry is one JSON file in this directory, named for the USP area
it covers (for example `booking-questions.json`). Topical files are independent:
adding a registry for a new area never requires editing another registry, the
booking-questions schema, or the specification.

Not every normative statement needs evidence. Security invariants, internal
consistency rules, and requirements inherited from an RFC or another negotiated
protocol cite their actual authority in the specification. A registry is
appropriate when traceability materially explains why a generic capability
exists.

## Registry format

A topical registry is a JSON object:

| Member | Required | Meaning |
|---|---|---|
| `topic` | Yes | Short identifier of the USP area, for example `booking-questions`. |
| `claim_scope` | Yes | Fixed value `requirement_evidence_only`. |
| `disclaimer` | Yes | States that sources document the origin or rationale of requirements and do not claim adapter availability, implementation compatibility, certification, or provider conformance. |
| `capabilities` | Yes | Array of capability records. |

A capability record:

| Member | Required | Meaning |
|---|---|---|
| `capability_id` | Yes | Stable, provider-neutral identifier, unique across **every** registry in this directory. Where practical it equals the `requirement` slug of the vectors that exercise it. |
| `requirement` | Yes | Provider-neutral description of the need. Must make sense without reading any source. |
| `evidence` | Yes | One or more evidence records. |
| `coverage` | Yes | `{ "specification_sections": [...], "vectors": [...] }`. Sections are specification section numbers; vectors are repository paths under `tests/vectors/`. Every cited vector must exist. |

An evidence record:

| Member | Required | Meaning |
|---|---|---|
| `source_type` | Yes | One of the allowed source types below. |
| `source_name` | Yes | Human-readable title of the source. |
| `source_url` | Yes | Public `https://` URL. Private, confidential, or paywalled research is never published here. |
| `provider` | No | The organization whose product the source documents. Present only when the source documents a provider product. |
| `product_area` | No | The documented product area, when `provider` is present. |
| `observed_on` | Yes | RFC 3339 full-date the evidence was first recorded. |
| `last_verified_on` | Yes | RFC 3339 full-date the summary was last confirmed against the source. Never earlier than `observed_on`. |
| `evidence_summary` | Yes | The generic need the source establishes, in provider-neutral terms. Never a copied payload or schema. |
| `evidence_status` | Yes | `current`, `changed`, `unavailable`, or `historical`. |

### Allowed source types

| `source_type` | Use for |
|---|---|
| `provider_documentation` | Public help-center or developer documentation of a product. |
| `standard` | Standards and RFCs (IETF, ITU-T, ISO, W3C). |
| `regulation` | Statutes and regulatory guidance. |
| `accessibility_guidance` | Accessibility standards and guidance. |
| `interoperability_specification` | Published interoperability or agent-protocol specifications. |
| `operational_evidence` | Published business policies or operational practice that show a requirement in use. |

### Status semantics

- `current` - the source still supports the summary as of `last_verified_on`.
- `changed` - the source still exists but no longer states the summarized need in the same way. The record stays, because the capability's motivation is historical fact.
- `unavailable` - the source can no longer be retrieved.
- `historical` - kept deliberately for provenance after being superseded.

A source is never deleted merely because it changed or disappeared. Evidence and
protocol coverage evolve independently: re-verifying a source changes only its
evidence metadata, while discovering an uncovered generic capability requires
the normal schema, specification, documentation, and vector changes.

## Verification

`python tools/usp_check.py vectors` discovers every `*.json` registry here and
checks required members, allowed source types, full-date values and their
ordering, `https://` source URLs, the fixed claim scope, globally unique
capability ids, and that every cited vector path exists. It does **not** fetch
source pages: mutable third-party pages are not part of conformance CI.

A future real adapter for a named product adds its product-specific mapping
tests alongside its own implementation, outside this directory and outside the
provider-neutral conformance suite.
