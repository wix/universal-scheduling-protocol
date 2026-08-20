# Feature: Complete AC-S for issue 156

## Goal

Complete every AC-S0 through AC-S5 task for issue 156 that can be performed in
this repository: make the breaking `2026-08-20` hard cutover to the owned
`usp-protocol.dev` authority, publish every normative artifact at its canonical
path, synchronize normative and site documentation, and enforce the migration
with existing validation and build machinery.

## Non-goals

- Modify downstream CLI, Wix implementation, registry, or checkout repositories.
- Operate the `usp.live` host or claim its owner-managed redirect is complete.
- Merge this feature branch, publish GitHub Pages, or announce a production
  cutover before the branch is reviewed and deployed.
- Preserve old protocol identifiers through dual acceptance. Old identifiers
  may appear only in an explicitly historical migration mapping.

## Must-preserve constraints

- Work only in
  `/Users/ranya/IdeaProjects/universal-scheduling-protocol/.cursor/worktrees/acs-156-complete`
  on `feat/acs-156-complete`.
- Domain shapes remain canonical JSON Schema `$defs` under `schemas/`; OpenAPI
  and OpenRPC components remain thin references without duplicated domain trees.
- `specification.md` and corresponding `site-docs/` pages stay synchronized.
- Canonical authority is `https://usp-protocol.dev`; capability namespace is
  `dev.usp-protocol.*`; compatibility policy is a breaking hard cutover.
- Canonical layout is `/specification` with canonical fragments,
  `$id`-matching `/schemas/...`, bindings under `/schemas/openapi/` and
  `/schemas/openrpc/`, and kebab-case problem slugs under `/errors/`.
- Canonical artifact requests resolve directly without redirect chains. GitHub
  Pages cannot emit arbitrary HTTP 301 responses, so feasible legacy aliases
  use static compatibility pages or copies and are documented honestly.
- Hosting model B is already live: `usp-protocol.dev` is the canonical full
  MkDocs site plus artifacts. The Pages CNAME, HTTPS assumptions, and pinned
  GitHub Actions policy must remain intact.
- Avoid unrelated IDE and hook files. Prepend one fresh `CHANGE_LOG.md` entry as
  the final file-change unit.

## File actions

| Path | Action | Reason |
|------|--------|--------|
| `specification.md`, `README.md` | modify | Version and normatively define the new authority, namespace, layout, and hard-cutover migration |
| `schemas/*.json` | modify | Move canonical `$id`, `$ref`, capability, spec, schema, and problem identifiers to the owned authority |
| `openapi/usp-rest.json`, `openrpc/usp-mcp.json` | modify | Migrate binding metadata/examples while preserving thin domain references |
| `site-docs/**/*.md`, `site-docs/*.txt` | modify/add | Keep the published specification, migration guidance, registry, problem pages, and links synchronized |
| `playground/**`, `site-docs/playground/**` | modify | Migrate fixtures and retain exact source/site mirrors |
| `docs/**`, `plans/**`, `overrides/home.html` | modify | Remove stale teaching examples and document publishing and external residuals |
| `scripts/build-site.sh` | add | Build MkDocs and copy artifacts to paths matching canonical identifiers |
| `package.json`, `.github/workflows/*.yml`, `scripts/publish-pages.sh` | modify | Use the artifact-aware build in local, CI, and Pages publication paths |
| `tools/usp_check.py` | modify | Add origin, namespace, published-layout, stale-identifier, mirror, and binding invariants to the existing checker |
| `site-docs/errors/*.md`, `site-docs/namespace.md` | add | Publish human-readable problem types and reserved namespace registry |
| `site-docs/spec/index.md`, `site-docs/problems/*.md` | add | Provide feasible GitHub Pages compatibility aliases without redirect chains |
| `CHANGE_LOG.md` | modify last | Record the migration motivations with fresh local identity and time |

## Work units

| ID | Description | Files | Verification | Status |
|----|-------------|-------|--------------|--------|
| U1 | Plan and commit this PLAN.md | PLAN.md | test -f PLAN.md | done |
| U2 | Version the breaking cutover and migration policy | `specification.md`, `README.md`, `site-docs/roadmap.md` | version identity scan | done |
| U3 | Publish migration, namespace, and release navigation | `site-docs/migration.md`, `site-docs/namespace.md`, `mkdocs.yml` | MkDocs nav parse | done |
| U4 | Migrate core schema identifiers | `schemas/usp.json`, `schemas/profile.json`, `schemas/rest_common.json` | schema checker | done |
| U5 | Migrate catalog and availability schema identifiers | `schemas/catalog.json`, `schemas/availability.json`, `schemas/calendar_freebusy.json` | schema checker | done |
| U6 | Migrate booking schema identifiers | `schemas/booking.json`, `schemas/paid_bookings.json`, `schemas/acp_booking_extension.json` | schema checker | done |
| U7 | Migrate extension schema identifiers | `schemas/waitlist.json`, `schemas/registry.json`, `schemas/webhook_event.json` | schema checker | done |
| U8 | Migrate and validate the REST binding | `openapi/usp-rest.json` | JSON parse and thin-ref check | done |
| U9 | Migrate and validate the MCP binding | `openrpc/usp-mcp.json` | JSON parse and thin-ref check | done |
| U10 | Complete normative namespace and URI rewrite | `specification.md` | stale scan and anchor check | done |
| U11 | Synchronize core site explanations | `site-docs/core-concepts.md`, `site-docs/getting-started.md`, `site-docs/security.md` | stale scan | done |
| U12 | Synchronize catalog and availability pages | `site-docs/specification/service-catalog.md`, `site-docs/specification/availability.md` | stale scan | done |
| U13 | Synchronize booking and registry pages | `site-docs/specification/booking.md`, `site-docs/specification/discovery-registry.md`, `site-docs/specification/index.md` | stale scan | done |
| U14 | Synchronize deployment mode pages | `site-docs/deployment-modes/index.md`, `site-docs/deployment-modes/standalone.md`, `site-docs/deployment-modes/ucp-native.md` | stale scan | done |
| U15 | Synchronize extension and transport pages | `site-docs/extensions.md`, `site-docs/transport/rest.md`, `site-docs/transport/mcp.md` | stale scan | done |
| U16 | Update machine-readable site summaries | `site-docs/llms.txt`, `site-docs/llms-full.txt`, `site-docs/index.md` | stale scan | done |
| U17 | Migrate homepage and standalone examples | `overrides/home.html`, `docs/ucp-native-demo-merchant-profile.example.json`, `README.md` | JSON parse and stale scan | done |
| U18 | Migrate playground services and profiles | root/site mirrored `services.json`, `business-profile.json`, `platform-profile.json` | mirror comparison and JSON parse | done |
| U19 | Migrate playground availability and holds | root/site mirrored `availability.json`, `holds.json` | mirror comparison and JSON parse | done |
| U20 | Migrate playground booking and management | root/site mirrored `bookings.json`, `manage.json` | mirror comparison and JSON parse | done |
| U21 | Migrate playground payment and waitlist | root/site mirrored `payment.json`, `waitlist.json` | mirror comparison and JSON parse | done |
| U22 | Migrate playground runtime source | `playground/src/playground.js`, site mirror, `site-docs/playground/src/playground-controller.js` | mirror comparison and stale scan | done |
| U23 | Update historical plans and remaining guidance | `plans/USP+UCP_implementation_plan.md`, `plans/V2_PRODUCTION_PLAN.md`, `plans/usp-registry-design-plan.md` | stale scan with historical allowlist | done |
| U24 | Add canonical problem documentation | `site-docs/errors/*.md` | required-slug coverage | done |
| U25 | Add feasible legacy path aliases | `site-docs/spec/index.md`, `site-docs/problems/*.md` | built alias coverage | pending |
| U26 | Wire canonical artifacts into site builds | `scripts/build-site.sh`, `package.json`, `scripts/publish-pages.sh` | local production build | pending |
| U27 | Use artifact-aware builds in workflows | `.github/workflows/ci.yml`, `.github/workflows/pages.yml` | workflow command scan | pending |
| U28 | Extend the existing conformance checker | `tools/usp_check.py` | all checker subcommands | pending |
| U29 | Update deployment operations and residual steps | `docs/website-deployment.md` | path checklist review | pending |
| U30 | Resolve migration-caused failures and stale identifiers | files implicated by verification | full local verification | pending |
| U31 | Prepend the required change-log entry | `CHANGE_LOG.md` | newest entry format and fresh identity | pending |
| U32 | Final verification and local commits | no file changes expected | schemas, refs, vectors, site, stale scan, lints, live safe GETs | pending |

## Revisions

### 2026-08-20T12:40:00+03:00 - Completed issue-driven plan

- Incorporated the latest issue comments establishing live hosting model B.
- Fixed the release date, hard-cutover policy, canonical fragment/path rules,
  and kebab-case error slug style before rewriting identifiers.
- Distinguished repository-completable AC-S work from external `usp.live`
  redirect, downstream-owner coordination, merge, publish, and announcement.
