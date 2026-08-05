# USP + UCP v2 - Production Readiness Plan (2 weeks)

> **Status:** approved; GitHub issues created (2026-08-05).
> **Goal:** take the existing end-to-end UCP-Native booking demo to a production MVP.
> **Predecessor:** [`plans/USP+UCP_implementation_plan.md`](USP+UCP_implementation_plan.md) (v1, the 2-week demo).
> **Registry design:** [`plans/usp-registry-design-plan.md`](usp-registry-design-plan.md).
> **Issue mapping:** see [Appendix A](#appendix-a---v2--github-issue-mapping).

v2 is **not** a feature release. Every item below exists because, without it, the system either
cannot be safely exposed to real buyers and real money, or cannot serve the target population of
merchants. No new USP capability is added.

---

## Table of contents

- [1. Scope and segment constraints](#1-scope-and-segment-constraints)
- [1a. Identity, authentication, and authorization clarifications](#1a-identity-authentication-and-authorization-clarifications)
- [2. Components and tracks](#2-components-and-tracks)
- [3. Step 1 - v2 from existing open issues](#3-step-1---v2-from-existing-open-issues)
  - [3.1 Mandated inclusions](#31-mandated-inclusions)
  - [3.2 Judgement inclusions (label `requires-approval`)](#32-judgement-inclusions-label-requires-approval)
  - [3.3 Exclusions](#33-exclusions)
- [4. Step 2 - missing mandatory issues to create](#4-step-2---missing-mandatory-issues-to-create)
  - [4.1 Cross-cutting](#41-cross-cutting)
  - [4.2 Track A - Link agent (`linkusp-cli`)](#42-track-a---link-agent-linkusp-cli)
  - [4.3 Track B - USP registry](#43-track-b---usp-registry)
  - [4.4 Track D - Wix business USP (`usp-impl`)](#44-track-d---wix-business-usp-usp-impl)
  - [4.5 Track E - UCP checkout (`acp-checkout`)](#45-track-e---ucp-checkout-acp-checkout)
  - [4.6 Conformance, docs and operations](#46-conformance-docs-and-operations)
- [5. Two-week schedule](#5-two-week-schedule)
- [6. Launch gates and honest risk assessment](#6-launch-gates-and-honest-risk-assessment)
- [7. Labelling actions](#7-labelling-actions)

---

## 1. Scope and segment constraints

### In scope

| Dimension | v2 |
|---|---|
| Deployment mode | **UCP-Native only** (`/.well-known/ucp` + `dev.usp.services.*`) |
| Cart | Single service, single booking |
| Payment | Stripe Shared Payment Token (SPT), full payment `at_booking` |
| Service providers | **Wix businesses with a connected, payin-capable Stripe account only** |
| Consumers | Buyers with a Stripe Link wallet |
| Agent harness | Base44 Superagent with `link-usp-superagent` SKILL, or any harness with `link-usp-agent` SKILL |
| Booking flow | discover -> profile/capability resolve -> availability -> create checkout -> SPT -> complete -> confirm -> cancel |

### Out of scope (deliberate, recorded as v2 conformance deviations)

Webhooks of any kind (and therefore RFC 9421 webhook signing/verification), Standalone mode,
redirect / non-UCP-native checkout, mixed carts, availability holds, deposits, 3DS /
`requires_escalation`, MCP and A2A bindings, service images, multi-taxonomy categories, interactive
user-consent OAuth / full consumer identity linking (`dev.ucp.common.identity_linking` and USP
§10.2.4), additional transport bindings.

**Important distinction:** deferring identity linking does **not** defer authorizing booking
get/cancel or any response that carries buyer PII. That authorization is a v2 launch requirement
(see [§1a](#1a-identity-authentication-and-authorization-clarifications) and [V2-X6](#41-cross-cutting)).

### Consequences of the segment constraints

The two constraints are not just filters, they are **the two hardest pieces of net-new work**:

1. *"Only Wix businesses with a connected Stripe account"* has **no implementation anywhere today.**
   The registry has no payment-readiness field, no admission check, no eviction path and in fact no
   Update or Delete operation at all. `acp-checkout` advertises the Stripe handler on a feature
   toggle alone and ignores the `supports_shared_payment_token` signal it already reads.
2. *"Any harness with the SKILL installed"* means the CLI can no longer rely on operator-side
   `.env` files, `DEMO_DEFAULTS`, or the `LINKUSP_UCP_TEST_SPT` / `--fake-payload` bypasses, and it
   cannot ship Google OAuth client secrets to consumer devices.

---

## 1a. Identity, authentication, and authorization clarifications

Recorded after clarifying whether Link wallet auth can piggyback into merchant consumer auth, what
"AS-backed" means, why unauthenticated transaction APIs are dangerous, and how booking PII
authorization relates to (optional) identity linking. These clarifications constrain [#9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9),
[V2-X1](#41-cross-cutting), [V2-X6](#41-cross-cutting),
[#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119), and
[#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134).

### AS-backed (definition)

An **Authorization Server (AS)** issues or endorses tokens after a login/consent ceremony.
**AS-backed** means the merchant trusts a token or session because *that merchant's* AS (or an AS
the merchant has configured as authoritative for its buyers) issued or endorsed it. Platform
`client_credentials` tokens and Link wallet tokens are each AS-backed for *their* audiences; they
are not interchangeable with merchant-member consumer credentials.

### Link-cli token and identity linking (verdict: no piggyback)

link-cli **0.8.2** authenticates the buyer to Stripe Link (OAuth device grant and/or
`login.link.com`). The access token is stored at
`~/Library/Preferences/link-cli-nodejs/config.json` (mode `0600`) as an opaque
`liwltoken_…` plus refresh `liwlrefresh_…`. Access tokens last about one hour; the CLI refreshes
silently.

There is **no** supported command that returns the full token. `auth status --format json`
exposes only a truncated preview. Supported interfaces are inputs such as `--auth` /
`LINK_AUTH_FILE` and `LINK_ACCESS_TOKEN` / `LINK_REFRESH_TOKEN`. Reading `config.json` directly is
an unsupported implementation detail.

**linkusp never forwards the Link token** to merchants. It uses auth status plus Link user-info /
shipping / spend-request APIs locally, then sends ordinary checkout `buyer` fields (with consent).

The Link token **cannot** be used as consumer authentication to the merchant:

- wrong issuer, audience, and scopes for USP/UCP identity linking;
- opaque (not a JWT the merchant can validate);
- `login.link.com` does not publish RFC 8414 / OIDC discovery or JWKS suitable for merchant
  verification;
- forwarding it would be token confusion and a wallet privilege leak.

UCP/USP identity linking requires the **merchant** as AS, exact issuer match, PKCE, and the rest of
the linking ceremony (USP §10.2.4). The Link token is not a shortcut; the deferral of
[#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119) stands for
full identity-linking implementation.

The **legitimate narrow form already shipped** is: use the Link token *locally* to fetch buyer
attributes, then populate checkout `buyer` fields under consent. That is attribute fill-in, **not**
identity linking.

### "Email match under consent" is not identity linking and not V2-X1

Matching a buyer email to a CRM record (even with consent language) is **CRM association only**.
Email is forgeable and is not proof of identity. It does **not** authorize `GET` / cancel of
bookings, and it does not protect PII in booking responses.

An earlier "cheapest path" framing only addressed a weak continuity goal (recognize a returning
customer without a full Wix login every time). It does **not** satisfy consumer authentication to
the business, and it is **not** a substitute for V2-X1 or V2-X6.

### Why unauthenticated UCP/USP transaction APIs are dangerous

Public resources (catalog, availability, profile / `/.well-known/ucp`) **may** remain anonymous.
The danger is **privileged operations**: create / update / complete / cancel checkout, booking
mutations, inventory holds, payment-adjacent complete, and any response that returns buyer PII,
with no trustworthy attribution, rate-limit key, or revocation handle.

A site UUID is approximately a public storefront id, not a credential. It is fine for discovery
routing. It is **not** sufficient to act as a platform on the control plane.

**V2-X1** therefore means: authorize privileged ops and attribute the calling platform/agent
(platform auth + `UCP-Agent` / `USP-Agent` validation). It does **not** mean "force identity
linking for browsing."

### Booking get / cancel / PII authorization is a v2 requirement

**Launch-blocking requirement:** booking get and cancel (and any response that includes buyer PII)
**MUST** be authorized. Unauthorized or cross-booking access **MUST** fail. Email obscurity and
booking-id obscurity alone do **not** count.

Identity linking is **one mechanism**, not the only requirement. Mechanism options:

1. **Platform-authenticated access** - the merchant trusts an authenticated platform that created
   the booking (or is otherwise allowed on that site) to get/cancel on the buyer's behalf
   ([V2-X1](#41-cross-cutting)).
2. **Booking-scoped capability credential** issued at create (adjacent to
   [#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134)).
3. **Full consumer identity linking**
   ([#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119)) when
   merchant-member semantics are in scope.

Do **not** frame "only the consumer who booked via merchant-member identity" as the sole
requirement. Frame **authorized access** as required; treat identity linking as optional unless
member semantics are required.

**Minimum recommended for UCP-Native + Link agents in v2:** V2-X1 platform auth, preferably plus a
booking-scoped credential (V2-X6 / #134). Keep #119 deferred unless a merchant needs member vs
guest pricing, package credits, member-only history/cancel rules, or an existing member portal that
must not trust agent-asserted email alone.

### UCP identity linking is optional (capability)

`dev.ucp.common.identity_linking` is an optional capability. Checkout may proceed unauthenticated
unless that capability is required or negotiated. Real merchants that *do* need member semantics
(gym / physio with member vs guest pricing, package credits, member-only history or cancel policy,
existing member portal) must not treat agent-asserted email as proof of membership.

### Spec note (PKCE / iss alignment)

[`specification.md`](../specification.md) §10.2.4 now aligns identity linking with UCP: platforms
**MUST** implement PKCE ([RFC 7636](https://www.rfc-editor.org/rfc/rfc7636)) with `S256`, businesses
**MUST** enforce PKCE at the token endpoint, and businesses **MUST** return the `iss` response
parameter per [RFC 9207](https://www.rfc-editor.org/rfc/rfc9207) with platform validation against
the discovered issuer. §14.1 normative references and link definitions cover RFC 7636, RFC 9207,
RFC 8414, and related citations. This closes a USP/UCP parity gap for when #119 is implemented; it
does not pull identity linking into the v2 launch set.

---

## 2. Components and tracks

| Track | Component | Repo / path | Language | Assignee |
|---|---|---|---|---|
| A | Link agent + SKILLs | [`yahalomran/linkusp-cli`](https://github.com/yahalomran/linkusp-cli) | Python | [`yahalomran`](https://github.com/yahalomran) |
| B | USP discovery registry | `wix-private/wix-vmr-repo` -> `usp-registry` | Java (Loom Prime) | [`maoryeh`](https://github.com/maoryeh) |
| C | Link platform services (proxy, vault, profile hosting) | Link platform + `linkusp-cli` | - | [`yahalomran`](https://github.com/yahalomran) |
| D | Wix business USP adapter | `wix-private/wix-vmr-repo` -> `usp-impl` | Java (Loom Prime) | [`maoryeh`](https://github.com/maoryeh) |
| E | UCP checkout + USP `paid_bookings` | `wix-private/ecom` -> `server/agentic-checkout/acp-checkout` | Scala | [`maoryeh`](https://github.com/maoryeh) |
| F | Stripe SPT / Cashier | `wix-private/ecom` + Stripe | Scala | [`maoryeh`](https://github.com/maoryeh) |
| S | Spec + schemas | this repo | JSON Schema / Markdown | [`yahalomran`](https://github.com/yahalomran) |

**GitHub issue assignment:** when creating the new mandatory issues in [§4](#4-step-2---missing-mandatory-issues-to-create), assign each issue to the track owner above:

- Assign to [`yahalomran`](https://github.com/yahalomran): tracks **A**, **C**, and **S**.
- Assign to [`maoryeh`](https://github.com/maoryeh): tracks **B**, **D**, **E**, and **F**.

Cross-track issues (for example S + B) take the assignee of the primary implementation track; if unclear, default to the first-listed track's owner.

---

## 3. Step 1 - v2 from existing open issues

55 issues are open. **25 are in v2**, 30 are deferred.

### 3.1 Mandated inclusions

These were designated for v2 up front. Justification below is the production implication of *not*
doing them.

| # | Title | Track | Production implication if omitted |
|---|---|---|---|
| [#42](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/42) | Disambiguate the term "Discovery" | S | The same word covers consumer search, profile/endpoint resolution and platform-business onboarding. v2 builds all three at once (registry search, `UCP-Agent` profile validation, credential onboarding) with different auth models, TTLs and idempotency. Conflating them in the normative text is how they get conflated in code - and the registry, the agent and `acp-checkout` are being written by three different teams from that one text. |
| [#47](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/47) | `usp-impl` returns HTTP 200 for all errors | D | **Confirmed still true**, and it is on the money path. Every handler catches `Exception` and returns a normal proto response, so `confirmation_failed` and `upstream_error` arrive as HTTP 200. Any client that branches on status - which is every standard HTTP library - reads a failed payment confirmation as success. The agent already carries a fragile `BookingServerError` workaround that sniffs the `messages` array. |
| [#54](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/54) | Multi-taxonomy `categories[]` on `Service` | S | Two competing category representations with a precedence rule, of which the registry uses exactly one flat string. Shipping both to production means every future consumer must implement the precedence rule and every producer must populate two fields; the drift is permanent once merchants are live. Resolve to one representation before there are external implementers. |
| [#59](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/59) | Registry filter-matching semantics unspecified | S + B | Filters are a yes/no contract. Range overlap vs point match, cross-currency price, `free` pricing, `undetermined` duration, geo units, and exclusion of coordinate-less businesses are all undefined. The registry has already made unilateral choices in `VespaQueryBuilder`; unwritten choices cannot be tested against, and a second registry would return different results for the same query. |
| [#75](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/75) | Link platform discovery integration test | A/C | Discovery is the entry point of every booking and is the one step with no integration coverage against a live registry. Without it, a registry search-semantics or projection change silently breaks every agent in the field and is only discovered by buyers. |
| [#86](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/86) | Execution guard on `complete_checkout` | E | **Double charge.** `acp-checkout` reads `Idempotency-Key` in exactly one place (`create_checkout`). `complete_checkout` has no guard, and in the booking flow the charge happens *before* `markCheckoutAsCompleted` - so any retry inside that window charges the buyer a second time. Today the only mitigation is a "do not retry" string in the response message. |
| [#108](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/108) | Prefer UCP checkout `payment_handlers` for `network_id`; demote MPP decode / 402 probe | S + A | The published normative docs and the SKILL still tell agents to obtain `network_id` by decoding an MPP or probing the merchant for a 402. That is a bridge built for a demo; in production it teaches every agent implementer a path that bypasses the handler contract and breaks the moment Stripe's published schema lands. `acp-checkout` already carries `TODO(#108)` on its provisional handler `spec`/`schema` URLs. |
| [#123](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/123) | Apply UCP capability intersection to checkout payloads | A | The agent computes the intersection and uses it only as a pass/fail gate; the negotiated set is never bound into `create_checkout` / `complete_checkout`. UCP requires the negotiated capability set to be carried in the request binding, not inferred from a header. Without it, a merchant cannot tell which capability version the agent actually intends to use, which is exactly the ambiguity that breaks the first time either side ships a second version. |
| [#124](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/124) | Production LinkUSP secrets, API proxy, and platform profile | A/C | This is the boundary between "an operator's laptop" and "a service". Today `--secrets-mode linkusp` is a stub that always raises, so the only working mode is `demo`, which injects a demo registry URL and a demo platform identity via `setdefault`. With the SKILL installed on arbitrary harnesses, merchant credentials and platform identity cannot live on the consumer device. |
| [#132](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/132) | Publish `linkusp-cli` to PyPI | A | The SKILL installs via `git+ssh://git@github.com/...`, i.e. it requires a private SSH key with repo access on the consumer's machine. No third-party harness can install the skill, no version can be pinned, and no security fix can be shipped without every user re-pulling `main`. |
| [#136](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/136) | Demo vs `linkusp` secrets-mode boundary | A | `demo` mode is not offline - it talks to the live registry and real merchants with demo defaults. Without a hard, documented boundary (and a production default), a production install silently runs with demo identity and demo config against real buyers and real money. |
| [#143](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/143) | SPT generation for merchants connected to Stripe under Cashier | F | Today `network_id` is resolved only from the Wix-Payments agentic configuration. Merchants connected to Stripe under Cashier therefore cannot produce an SPT - and they are part of the v2 target population. Omitting this shrinks the addressable merchant set to a subset that nobody has quantified. |
| [#149](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/149) | `availability_hint` may influence service-search ranking | S + B | The registry indexes availability attributes and does not score on them, so "book me the soonest haircut" - the single most common agent intent - ranks by text relevance and geo distance only. Buyers are offered fully-booked services first, then discover the failure three network hops later at availability query. |
| [#155](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/155) | Document checkout `links` types + merchant totals/links integration test | E | `totals` and `links` emission is currently proven only by live observation of one merchant. With no CI assertion, a mapper change silently drops the privacy policy or terms link from a real checkout, which is a compliance defect, not a cosmetic one. |

### 3.2 Judgement inclusions (label `requires-approval`)

| # | Title | Track | Production implication if omitted |
|---|---|---|---|
| [#9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9) | Finalize HTTP/REST transport binding authentication | S | **The single largest security gap.** USP §10.2.3 makes OAuth Bearer a MUST; UCP makes platform authentication a SHOULD and identity/`UCP-Agent` binding a MUST. Reality: `acp-checkout` is declared `service_exposure = PUBLIC` with the missing-permission lint suppressed and authenticates nobody, and `usp-impl` reads no `Authorization` header on any handler. The normative position has to be decided before three teams implement three different answers. This issue is the decision; the implementation is [V2-X1](#41-cross-cutting). Scope of the decision is **platform/agent authentication of privileged ops** (see [§1a](#1a-identity-authentication-and-authorization-clarifications)), not consumer identity linking and not "force login to browse catalog." Link wallet tokens and email match are explicitly out of scope as answers. |
| [#40](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/40) | Service delivery address gap | S + D | There is no first-class field for the buyer's service address anywhere - not on `POST /bookings`, not on `Buyer`, and `Booking.location` is the *business's* location. The flagship demo merchant is an HVAC business, i.e. a home service, and the SKILL already instructs the agent to supply the buyer's home address. Today that address can only go into free-text `notes`: unvalidated, unparseable for dispatch, and absent from the checkout page. A production home-service booking is therefore not fulfillable. **Cheaper alternative if this is cut:** exclude home-service verticals from the v2 registry admission gate and say so explicitly. |
| [#114](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/114) | Publish hosted per-agent platform profile | A/C | The profile URI is the unit of platform identity; businesses MUST fetch it over HTTPS with no redirects and cache it by URI. The demo gets away with an unfetchable local fixture only because neither `usp-impl` nor `acp-checkout` currently reads the header. The moment either one validates it - which v2 requires - every call from every agent fails. This has to land *before* the server-side validation it enables. |
| [#118](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/118) | `USPTokenStore` unit and integration tests | A | `USPTokenStore` (RFC 8414 discovery, RFC 7591 DCR, `client_credentials`, refresh with a 60s margin) becomes the *only* production **platform-to-merchant** auth path once the `LINKUSP_*_BEARER` env overrides are removed, and it has zero tests. An untested refresh path fails as a mid-booking auth error for every user simultaneously when tokens age out. Distinct from Link wallet tokens (never forwarded; not consumer identity linking; see [§1a](#1a-identity-authentication-and-authorization-clarifications)). |
| [#125](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/125) | LPOS and merchant credential vault | C | Once merchant APIs are authenticated, something must obtain and hold a credential **per merchant, for the whole registry**. Without it only hand-configured merchants are bookable, which contradicts the "all Wix Stripe businesses" scope, and the alternative - per-device DCR - puts merchant client secrets in a plaintext JSON file on consumer machines. **Scope down for v2:** drop the registry-webhook triggers (webhooks are out of scope) and drive onboarding from scheduled registry sync plus a manual repair command. |
| [#126](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/126) | Production USP registry MVP | B | The registry is the entry point of every booking and is today an explicitly Phase-1 demo service: no auth on any endpoint, no Update or Delete, hardcoded to the **dev** Vespa cluster (`VESPA_PLATFORM = "dev-v8"`), no metrics, no health checks, no pagination, no outbound timeouts, and never runtime-tested against a cluster. It cannot be exposed publicly in this state. This is the umbrella; the concrete work is [V2-B1..B9](#43-track-b---usp-registry). |
| [#128](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/128) | Service catalog enrichment and QA pipeline | B | With admission widened from one hand-picked merchant to the whole Wix Stripe population, data quality stops being cosmetic. The registry today silently substitutes `"Wix Bookings Business"` / `America/New_York` / `USD` when SiteProperties returns blanks, so a misconfigured site lands in the index with fabricated identity in the wrong timezone. Add the QA gates and the quarantine bucket; defer the LLM enrichment beyond what already exists. |
| [#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134) | Booking cancel: store credential + `flow book cancel` | A + S | Cancellation is a core booking-lifecycle operation (USP §5) and there is **no** way to reach it from the agent: the customer credential is not retained after booking and the `continue_url` session token expires in ~5 minutes. Buyers who booked through the agent must phone the business with a raw booking id. It is also the only remediation available when a charge succeeds against a wrong or unwanted booking. **Elevated for v2:** this is part of the launch-blocking booking authorization story ([V2-X6](#41-cross-cutting) / [§1a](#1a-identity-authentication-and-authorization-clarifications)), not an optional convenience. Prefer a booking-scoped capability credential at create (usable for get and cancel) over email match or booking-id obscurity; full merchant-member identity linking remains [#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119) (deferred). |
| [#141](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/141) | Detect a connected Stripe account before advertising the SPT handler | E/F | **This is the v2 admission constraint itself.** Confirmed: gating is the `uspBookingsEnabled` toggle alone; `resolveNetworkId` reads `stripe.supports_shared_payment_token` and then advertises `com.stripe` regardless, failing open on error. So a site with no usable Stripe account still advertises the handler, the agent acquires a real SPT against the buyer's wallet, and the charge dies late at Cashier as `payment_declined` - a payment failure presented for what is really an unoffered method. |
| [#144](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/144) | Replace `BOOKINGS.BOOKING_READ_ANY` with least-privilege site-scoped authorization | D | A temporary grant lets `usp-impl` read **any booking on any Wix site**. That is a cross-tenant PII capability sitting behind a service whose own inbound surface is unauthenticated. It cannot go to production and it is explicitly marked as a stopgap that must be reverted. |
| [#156](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/156) | Migrate namespace authority `usp.dev` -> `usp-protocol.dev` | S | We do not own `usp.dev`, yet every normative identifier, `$id`, profile `spec`, profile `schema` and problem `type` points there, and §2.5 binds the `dev.usp.*` namespace to that origin. Profiles MUST carry `spec` and `schema` per capability entry; ours resolve to a domain a third party can acquire and serve conflicting content from. This is a **breaking** revision: doing it now costs a rename, doing it after launch forces the break onto live merchants, cached profiles and deployed agents. `usp-protocol.dev` is already purchased. |

### 3.3 Exclusions

**Mandated exclusions** (label `v>2`), with the stated reason:

| # | Reason |
|---|---|
| [#17](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/17), [#46](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/46), [#103](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/103), [#135](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/135) | Standalone mode out of scope |
| [#51](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/51) | No additional transport bindings in v2 |
| [#49](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/49) | UCP checkout only; no redirect checkout URL to refresh |
| [#52](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/52), [#91](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/91), [#92](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/92), [#111](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/111), [#112](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/112), [#115](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/115), [#116](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/116) | No webhook support in v2 |
| [#58](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/58), [#68](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/68), [#106](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/106) | Registration is controlled and Wix-only; ownership proof, profile-URL validation and anti-abuse are not reachable attack surfaces in v2 |
| [#55](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/55) | Registry federation/discovery out of scope |
| [#93](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/93) | Link generates the SPT; no 3DS path |
| [#133](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/133) | Not necessary for production |
| [#139](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/139) | No mixed carts in v2 |
| [#26](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/26) | Launch without service images |

**Judgement exclusions** (label `v>2` + `requires-approval`):

| # | Title | Why it is not strictly necessary for v2 |
|---|---|---|
| [#44](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/44) | Business record & credential lifecycle spec section | Formalizes the persisted onboarding record plus signing-key rotation and revocation. Key rotation exists to serve webhook signing, which v2 does not do, and v2 has exactly one platform. The concrete credential handling is covered by [#124](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/124) / [#125](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/125) and revocation by the registry eviction path (V2-B2). |
| [#94](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/94) | Registry capability and payment search filters | The admission gate (V2-B2) makes every indexed business UCP-Native and SPT-capable *by construction*, so a `supports_spt` / `deployment_mode` filter has no reachable effect in v2. It becomes necessary the moment the registry admits a second merchant class. |
| [#102](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/102) | UCP conformance gaps rollup | A tracker for gaps deliberately excluded here. Production-relevant children are pulled out: platform authentication becomes [#9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9)/V2-X1, booking get/cancel/PII authorization becomes V2-X6 (with [#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134)), trusted-UI becomes V2-C1. Optional `dev.ucp.common.identity_linking` remains under [#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119) / v>2 unless member semantics are required. |
| [#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119) | Interactive OAuth / identity linking | Deferred for **merchant-member semantics**, not because booking PII may stay unprotected. v2 UCP-Native + Link agents do not require `dev.ucp.common.identity_linking`; checkout may be unauthenticated unless that capability is negotiated. `usp-impl` exposes no authorization server today; `client_credentials` + DCR covers platform-to-business. **Link wallet token piggyback is not viable** (wrong issuer/audience/scopes; opaque; no merchant-usable discovery/JWKS; token confusion / wallet privilege leak). Email match under consent is CRM association only, not identity linking. When #119 is implemented, follow [`specification.md`](../specification.md) §10.2.4 (PKCE S256 + RFC 9207 `iss`). Needed when a merchant requires member vs guest pricing, package credits, member-only history/cancel rules, or an existing member portal. |
| [#120](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/120) | Unit test `complete_checkout` signal retry | `acp-checkout` emits no `signal` messages at all, and it is the only merchant implementation in v2, so the retry branch is unreachable in production. The genuine risk in that code path - a retry minting a fresh idempotency key - is covered by V2-A1. |
| [#121](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/121) | Log negotiated UCP-Version in demo E2E | Changes demo harness step logs, not production behavior. Production visibility of the negotiated version is covered by V2-X4. |
| [#122](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/122) | Use `discover_service_via_registry` in demo and flow paths | A refactor to remove drift risk between the demo and the shared helper. No production capability is missing; the shipped `flow` path is exercised by [#75](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/75). |
| [#127](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/127) | Link-hosted buyer calendar OAuth | Calendar conflict-checking is an optional USP extension (§11.2), not part of the booking flow. The *unacceptable* part - Google client credentials on consumer devices - is fixed far more cheaply by V2-A4, which keeps the superagent connector path and disables device-side OAuth. |
| [#147](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/147) | UCP-Native deposit support | Deposits are explicitly out of scope. |

---

## 4. Step 2 - missing mandatory issues to create

35 issues. Each one is a gap found by reading the two specs against the four codebases; each states
what breaks in production without it. IDs are plan-local (`V2-*`) until the GitHub issues exist
(do not create them until this plan is approved).

### 4.1 Cross-cutting

| ID | Title | Repos | Production implication if omitted |
|---|---|---|---|
| **V2-X1** | Authenticate inbound USP/UCP privileged requests and validate platform identity | E, D, B | The whole control plane is currently open. `acp-checkout` is `service_exposure = PUBLIC` with the missing-permission lint suppressed, and `createCallScope` only validates that `site_id` is a UUID before stamping site context and signing *outbound* calls as the platform app - so anyone who knows a site UUID can create, mutate, complete and cancel checkouts on that site. `usp-impl` reads no `Authorization` header anywhere, and only `BookingHandler` consults the per-site toggle, leaving catalog, availability and profile open for every routed site (anonymous browse of public resources is acceptable; anonymous privileged ops are not). Neither service reads `UCP-Agent` / `USP-Agent` inbound, so there is no platform identity to authenticate, attribute, rate-limit or revoke. Scope: OAuth Bearer per USP §10.2.3 on privileged ops, mandatory `UCP-Agent`/`USP-Agent` with HTTPS-only + no-redirect profile fetch and caching, identity binding between credential and advertised profile, and the per-site gate on every privileged handler. **Not in scope:** consumer identity linking, Link-token piggyback, or email-as-auth (see [§1a](#1a-identity-authentication-and-authorization-clarifications)). Depends on the [#9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9) decision and on [#114](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/114) landing first. |
| **V2-X2** | Timeouts, bounded retries with backoff, and circuit breaking on every outbound call | A, B, D, E | There is not one explicit deadline on any outbound call in any of the four components: `acp-checkout` -> `usp-impl` gRPC and Cashier, `usp-impl` -> Wix Bookings/Confirmator/SiteProperties, registry -> vFeed/vSearch/Bookings/AI-gateway, agent -> merchant. `acp-checkout`'s only retry is an immediate no-backoff `withRetry(3)` on a post-charge re-read; the agent retries only 429/503 and not 5xx or connect timeouts. A single slow dependency therefore hangs the buyer's agent turn with no bound, and a failing merchant keeps being hammered. |
| **V2-X3** | Secrets, PII and credential log hygiene; remove all demo bypasses | A, B, D, E | Concretely: `acp-checkout` runs with `logRequests = true, logResponses = true`, so the `complete_checkout` body - which contains `payment.instruments[].credential.token`, the Stripe SPT - is written to logs, and `ConvertCreateCheckoutRequest` logs the entire buyer object at info level. `usp-impl` returns `e.toString()` to callers on every `upstream_error`. The agent writes buyer name/email/phone, booking ids and spend ids to a mode-`0644` `~/.linkusp/.usp-session.json`, persists merchant OAuth `client_secret` and access tokens unrestricted, and appends full request/response bodies to a multi-megabyte `http_trace.log`. `LINKUSP_UCP_TEST_SPT` completes a checkout without going through the buyer's Link approval, and `--fake-payload` injects buyer identity without `link-cli`. Any one of these is a launch blocker on PCI/GDPR grounds; the two bypasses additionally defeat the human gates the SKILL contract is built on. Includes a retention/purge path for agent-side buyer data (USP §10.1.3). |
| **V2-X4** | Money-path observability: metrics, alerts and an end-to-end correlation id | A, B, D, E | **Zero custom metrics exist in any of the four components.** There is no counter for charge attempts, declines, `payment_captured_booking_unconfirmed`, `confirmation_failed`, `price_mismatch`, registry search errors or search latency, so nothing can be alerted on and no SLO can be measured. There is also no correlation id: joining "this buyer's failed booking" across agent -> registry -> `acp-checkout` -> `usp-impl` -> Cashier means grepping on a booking id across four systems. A money-handling system that cannot detect its own failures is not production-ready by any standard. |
| **V2-X5** | Booking-flow latency budget, SLOs and a staging latency/soak test | all | "Latency must be within acceptable limits" is a v2 requirement with no target attached; the registry design's own scale/NFR decision (O14) is still recorded as TBD. Without a per-step budget and a repeatable measurement, the known hot spots (registry search, the agent's serial discovery fan-out, poll loops of up to 10 minutes) cannot be signed off or regression-tested. |
| **V2-X6** | Authorize booking get/cancel and any response carrying buyer PII | D, E, A, S | **Launch-blocking authorization requirement**, separate from optional identity linking. Today booking get/cancel and PII-bearing responses are reachable without a trustworthy authorization story (email match and booking-id obscurity do not count). Unauthorized or cross-booking access MUST fail. Mechanisms (pick at least one that is real authz): (1) platform-authenticated access under V2-X1 for the platform that created the booking / is allowed on the site; (2) booking-scoped capability credential at create ([#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134)-adjacent), retained by the agent for later get/cancel; (3) full consumer identity linking ([#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119)) only when merchant-member semantics are required. **Recommended minimum for UCP-Native + Link agents:** V2-X1 plus preferably a booking-scoped credential. Do not treat "consumer must be a linked merchant member" as the only acceptable design unless member semantics are in scope. |

### 4.2 Track A - Link agent (`linkusp-cli`)

| ID | Title | Production implication if omitted |
|---|---|---|
| **V2-A1** | Stable `Idempotency-Key` across HTTP retries | Keys are minted with `uuid.uuid4()` *inside* the header builder, and `with_http_retry` re-invokes the request function - so every retry attempt carries a **new** idempotency key. This is the agent-side half of [#86](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/86): server-side dedupe cannot work when the client changes the key. A retried `complete_checkout` or `POST /bookings` produces a double charge or a double booking, and no test asserts key stability. |
| **V2-A2** | Never report `CONFIRMED` before the booking reaches a terminal confirmed state; add the money-recovery path | After `complete_checkout` the flow sets `payment.status = paid` and `CONFIRMED` **even when the confirmation wait times out**. The buyer is told "you're booked" on the strength of a charge, not a booking. Combined with the absence of any flow-level `cancel_booking` / `cancel_checkout` wiring and no refund surface, a charge that does not produce a booking leaves the buyer with no automated remedy and the agent with nothing to say. Pairs with [#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134), [V2-X6](#41-cross-cutting), and V2-E2. |
| **V2-A3** | Parallelize and cache the discovery fan-out | Discovery is serial N+1: for each registry hit the agent waits a 200 ms pacing delay, fetches the profile, paces again, then fetches the service. With the client limit of 5 that is already multiple seconds of dead time before the buyer sees a single option, and it scales linearly with result count. This is the most visible latency in the flow and it is the step the buyer is waiting on. |
| **V2-A4** | Remove device-side Google OAuth credentials from the calendar path | The base harness performs local Google OAuth, which means shipping Google app client id and secret to every consumer device that installs the SKILL. Minimum fix: use harness-provided connector tokens (as the superagent variant already does) or ship with conflict-checking disabled. Shipping the credentials is a credential-disclosure defect, not a UX question. |
| **V2-A5** | Production-path E2E with a real Link wallet SPT | The E2E suite leans on `LINKUSP_UCP_TEST_SPT`, so the SPT acquisition and approval path that actually ships is the one path that is not tested end to end. The payment code that runs in production has never been exercised by CI. |

### 4.3 Track B - USP registry

| ID | Title | Production implication if omitted |
|---|---|---|
| **V2-B1** | Implement Update (§6.5) and Delete (§6.6) | Neither operation exists - no RPC, no handler, no path. There is therefore **no way to correct or remove a registry entry**: a business that unpublishes its site, disconnects Stripe, renames itself or asks to be delisted stays in the index and in search results forever. This also blocks V2-B2 and any GDPR/delisting request. |
| **V2-B2** | Stripe payin-capability admission gate + periodic re-verification and eviction | The defining v2 admission rule has no field on `RegistryEntry`, no field in the Vespa business schema, no check in `RegistrationHandler.register` or `OnboardHandler.onboard`, and no filter on either search. There is no reference to Stripe or to any Wix payments service anywhere in the registry. Without this, search returns businesses that cannot be paid, and the failure surfaces as a `payment_declined` against the buyer's real wallet. Re-verification is required because payment connection state changes after onboarding. |
| **V2-B3** | Opaque cursor pagination; remove the hard 100-result ceiling | `PaginationRequest.cursor` is read nowhere, `pagination` is never set on either search response, and hits are capped at `MAX_HITS = 100` with no offset support. Agents can only ever see one page of the entire Wix inventory and have no way to ask for more. USP §9.1.2 additionally requires cursors to be opaque, which cannot be satisfied by a field that is never emitted. |
| **V2-B4** | Correct error semantics: stop masking backend failures as HTTP 200 + empty results | `SearchHandler` catches every exception and returns HTTP 200 with an empty result array plus a `search_failed` message whose content is `String.valueOf(e)`. A vSearch outage is therefore indistinguishable from "no matches" for any client that reads `results`, emits no 5xx for monitoring to alert on, and leaks internal exception text to callers. `findBusinessById` similarly swallows failures and reports `not_found`. Also add RFC 9457 problem details, 404 on missing get, and 204 on delete. |
| **V2-B5** | Per-environment configuration, health checks and deployability | `VESPA_PLATFORM = "dev-v8"` and `AppDefId` are compile-time constants, so the service is hardwired to a **dev** Vespa cluster; there are no health checks, no dependency probes and no alerting, and the Vespa adapters have never been runtime-tested against a cluster. The service cannot be deployed to production as it stands. |
| **V2-B6** | Freshness: scheduled re-index of entries and availability hints | Ingestion is push-only plus a manual per-site orchestrator. Nothing re-runs onboarding, re-pulls a catalog, or refreshes availability hints; stale-service reconciliation only runs *within* a single onboard invocation. Once a site is onboarded, its index decays silently and permanently: deleted services stay searchable, prices go stale, and hints age past the 6-hour confidence window forever. §6.3 asks for re-index within 24h. |
| **V2-B7** | Onboarding throughput for the full Wix Stripe population | `OnboardHandler.onboard` loops over every service in a site and issues an availability query **plus an LLM call** per service, strictly sequentially, inside one synchronous HTTP request, with no timeout, no parallelism, no batching and no cache. That is acceptable for one demo merchant and cannot onboard a merchant population. |
| **V2-B8** | Search result quality: dedupe multi-location services, constrain `status`, exact-id get | The "nearest location per service" grouping was never implemented, so a multi-location service returns one duplicate row per location and consumes the result budget. Service `status` is indexed but never filtered, so a suspended service remains searchable. `findBusinessById` matches with `contains` on `doc_id` rather than an exact lookup. All three degrade the accuracy the v2 requirement calls for. |
| **V2-B9** | `Idempotency-Key` on registry writes | No key is read and no replay cache exists. The public register path mints a fresh `reg_<uuid>` per call, so a client retry silently creates a **duplicate business** in the index - and with no Delete operation (V2-B1) it cannot be cleaned up. |

### 4.4 Track D - Wix business USP (`usp-impl`)

| ID | Title | Production implication if omitted |
|---|---|---|
| **V2-D1** | Honor `Idempotency-Key` on `POST /bookings` and make `confirm-payment` replay-safe | `Idempotency-Key` appears nowhere in the service, `CreateBookingRequest.hold_id` is accepted and never read, and there is no dedupe store of any kind. A retried create produces a **duplicate booking on the same slot**; a retried confirm re-invokes the Confirmator instead of returning the current booking. `cancelBooking` is the only operation with (best-effort) replay handling. |
| **V2-D2** | Enforce pending-booking expiry | `expires_at` is computed as `now + 30 minutes` on **every read** and is never persisted or enforced, and there is no sweeper. An abandoned checkout therefore holds a real slot indefinitely, so slot inventory leaks and the merchant loses bookable capacity to agents that walked away. |
| **V2-D3** | Stop emitting fabricated policy and profile data | `cancellation.allowed` and `rescheduling.allowed` are hardcoded `true` regardless of the merchant's real Wix policy, and fee/deadline fields are never populated - so the agent tells buyers they can cancel free when they cannot, which is a consumer-protection and chargeback exposure. `confirmation_mode` is hardcoded `"auto"` on every booking even though the real mode is read elsewhere. Booking windows are fabricated from defaults (30-minute slot interval, one-year max advance). The profile still advertises `checkout_systems: ["redirect"]`, a checkout system that was removed - a UCP-Native profile claiming a mode it does not implement. |
| **V2-D4** | Money handling: remove float price parsing and silent currency/timezone fallbacks | `parseCentsFromDecimal` parses the price string as a `double` and rounds - a float path in a money conversion that feeds a real charge. `("Wix Bookings Business", "America/New_York", "USD")` is silently substituted whenever SiteProperties returns blanks or an invalid value, so a misconfigured merchant can be charged in the wrong currency and quoted slots in the wrong timezone. Both must fail closed. |
| **V2-D5** | Real catalog pagination | `ListServicesResponse` always sets `hasMore = false`, `limit` and `cursor` are accepted and ignored, and the downstream Wix search is called with no paging limit. For any merchant with more services than the implicit page size the catalog is silently truncated - for the agent and for registry ingestion alike. |
| **V2-D6** | Validation hardening on the booking path | The slot id is an unsigned, unencrypted Base64 JSON blob parsed by hand-rolled substring matching, so a caller can mint a slot id for any service, time or staff member and the only backstop is whatever Wix happens to reject. `party_size` has no upper bound and is never checked against slot capacity. The request's `service_id` is silently overridden by the decoded slot's. `validateConfirmAmount` **fails open** - it returns "valid" when the booking or service cannot be read, or on any exception - so a transient downstream blip disables the pre-charge price check rather than blocking the charge. |

### 4.5 Track E - UCP checkout (`acp-checkout`)

| ID | Title | Production implication if omitted |
|---|---|---|
| **V2-E1** | Capability intersection, protocol version validation and the negotiated `ucp` envelope on every response | No request-driven negotiation exists: the version is stamped from the constant `"2026-04-08"`, capabilities come from a static map, and the requested version is never read. The per-checkout envelope advertises only the shopping capabilities - the USP capabilities are never echoed, even on a booking checkout - and error responses carry no `ucp` envelope at all. UCP and USP §8.3/§8.4 both make intersection, version validation and per-response negotiated envelopes MUST-level. Without it, neither side can safely ship a second version, and `capabilities_incompatible` can never be returned. |
| **V2-E2** | Automatic compensation for post-charge failures | All three post-charge failure classes - `payment_captured_booking_unconfirmed`, `payment_captured_completion_failed`, `ChargeFailedAfterCompletion` - are documented in the code as requiring manual intervention, and nothing calls a refund or void anywhere in the module. **This is the worst failure mode in the system:** the buyer is charged, no booking exists, and the only remedy is a human noticing a log line. Needs automatic refund/void plus a reconciliation job over the captured-but-unconfirmed set. |
| **V2-E3** | Emit `available_instruments` and enforce `handler_id` equality | The `PaymentHandler` proto has **no `available_instruments` field** and nothing emits one, yet USP §7.4 makes checkout-time `available_instruments` authoritative over the profile and requires `complete_checkout`'s `payment.instruments[].handler_id` to equal the checkout handler instance id. The agent therefore cannot determine which instruments are usable at payment time, and the merchant advertises a `paid_bookings` extension it does not fully implement. |
| **V2-E4** | Verified legal `links`; suppress the zero fulfillment total for bookings | `privacy_policy` and `terms_of_service` are constructed by convention as `{origin}/privacy-policy` and `{origin}/terms-of-service` and are never verified to exist, so on most real merchant sites the links a buyer is shown at checkout will 404 - a compliance defect on a live payment surface. `totals` also always emits a `fulfillment` entry, including `0` for a booking with no shipping. Complements [#155](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/155). |
| **V2-E5** | Correct status and error semantics on the money path | Empty `payment_handlers` forces the checkout status to `REQUIRES_ESCALATION`, so a transient toggle or Stripe-resolution hiccup - both of which fail open to an empty map - silently degrades a bookable checkout into "escalation required" instead of reporting a payment problem. A deliberate policy rejection (USP toggle off) returns gRPC `UNIMPLEMENTED`, which is absent from the mapping table and surfaces as **HTTP 500**, so expected policy outcomes pollute error monitoring. The `messages[].type` taxonomy is also inconsistent across the money path (`payment_declined` is typed `system`, post-charge failures `error`). |
| **V2-E6** | Idempotency on `update_checkout` and `cancel_checkout` | Both read no idempotency key despite the proto documenting one on update, and `cancel_checkout` releases the booking before deleting the checkout - if `deleteCheckout` fails the booking is released while the checkout survives, so the buyer's slot is gone but the checkout still looks live. `complete_checkout` is covered by [#86](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/86). |

### 4.6 Conformance, docs and operations

| ID | Title | Production implication if omitted |
|---|---|---|
| **V2-C1** | Trusted-UI / human-confirmation conformance for agent-driven completion | UCP platform guidelines require checkout finalization through a trusted, deterministic UI unless AP2 mandates apply, and the v1 flow is fully agent-driven. In practice the Stripe Link spend-approval page *is* that trusted surface, but this is nowhere documented, and the gates that route through it can be bypassed by `LINKUSP_UCP_TEST_SPT` and `--fake-payload` (removed by V2-X3). Without a written position and a bypass-free build, agent-initiated completion has no defensible authorization story when a buyer disputes a charge. |
| **V2-C2** | v2 conformance checklist and recorded deviations | USP §9.1.5 lists webhook signing as a REST-binding MUST and §10.1.1 makes RFC 9421 webhook signing mandatory for all modes. v2 deliberately ships without webhooks. That has to be an explicit, reviewed conformance deviation with an owner and a target version, not a silent omission - otherwise "USP-conformant" is a claim nobody can substantiate. Same for holds, deposits and MCP. |
| **V2-C3** | Money-path incident runbook and reconciliation tooling | Until V2-E2 automation is proven, and permanently as an operational backstop, on-call needs a query to enumerate captured-but-unconfirmed charges, a documented manual refund procedure, and an escalation path. A production payment system without a reconciliation procedure has an unbounded worst case. |

---

## 5. Two-week schedule

Ten working days, six parallel tracks. Ordering is driven by three hard dependencies:
[#9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9) (auth decision)
gates V2-X1; [#114](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/114)
(hosted platform profile) must land **before** V2-X1 starts validating `UCP-Agent`;
[#156](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/156) (namespace
migration) is breaking and must land on day 1-2 or be dropped.

### Week 1 - decide, unblock, secure

| Day | S (spec) | A (agent) | B (registry) | C (platform) | D (`usp-impl`) | E/F (checkout) |
|---|---|---|---|---|---|---|
| 1 | #9 decision, #156 rename, #42 | V2-X3 bypass removal | V2-B5 config/deploy | #114 profile hosting | #47 HTTP status codes | #141 Stripe eligibility gate |
| 2 | #156, #54, #59 | V2-X3 storage hardening | V2-B1 update/delete | #114, #124 proxy | #47, #144 permissions | #141, #86 execution guard |
| 3 | #59, #149 | V2-A1 idempotency keys | V2-B2 admission gate | #124 secrets | V2-D1 idempotency | #86, V2-E6 |
| 4 | #108 handler docs | V2-A1, #118 token tests | V2-B2, V2-B9 | #124, #125 vault | V2-D4 money handling | V2-E2 compensation |
| 5 | #40 address (if approved) | V2-A2 no false confirm | V2-B4 error semantics | #125 LPOS onboarding | V2-D3 policy truthfulness | V2-E2, V2-E1 negotiation |

### Week 2 - conform, harden, measure

| Day | S | A | B | C | D | E/F |
|---|---|---|---|---|---|---|
| 6 | #40, V2-C2 | #134 cancel + V2-X6 | V2-B3 pagination | #125, #136 boundary | V2-D6 validation, V2-X6 | V2-E1, V2-E3 instruments |
| 7 | V2-C2 | #134, V2-A4 calendar | V2-B6 freshness | #132 PyPI | V2-D2 expiry | V2-E3, V2-E5 status semantics |
| 8 | V2-C1 trusted UI | V2-A3 discovery latency | V2-B7 onboarding scale | V2-X1 (agent side) | V2-D5 pagination | V2-E4 links, #155 |
| 9 | - | V2-A5 real-SPT E2E, #75 | V2-B8 search quality | V2-X1 | V2-X1 + V2-X6 (server) | V2-X1 (server side) |
| 10 | Conformance sign-off | V2-X4/X5 measurement | V2-X4/X5 | V2-C3 runbook | V2-X2 timeouts | V2-X2 timeouts |

V2-X2 (timeouts/retries), V2-X3 (log hygiene), V2-X4 (metrics/correlation id) are cross-cutting and
land per component alongside that component's other work; the table shows only the day they are
verified end to end.

---

## 6. Launch gates and honest risk assessment

**60 issues in 10 working days across 6 tracks is roughly one item per team per day.** That is
achievable for the small items and not achievable for
[#125](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/125) (LPOS +
vault), [#126](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/126) /
V2-B* (registry productionization) or V2-X1 / V2-X6 (authentication and booking authorization
across three services). The plan should be read as **two weeks to launch-blocking parity, with a
named tail.**

### Launch-blocking (no production traffic without these)

Money correctness: [#86](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/86),
V2-A1, V2-A2, V2-E2, V2-D1, [#47](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/47).
Security and privacy: V2-X1, **V2-X6**, V2-X3,
[#144](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/144),
[#114](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/114),
[#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134)
(credential + cancel path as part of V2-X6).
Admission: [#141](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/141), V2-B2, V2-B1.
Operability: V2-X4, V2-B5, V2-C3.

Identity linking ([#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119))
is **not** launch-blocking for UCP-Native + Link agents unless member semantics are required.
Email match and Link-token piggyback are **not** acceptable substitutes for V2-X1 or V2-X6.

### Necessary but survivable in a limited pilot

V2-B3, V2-B6, V2-B7, V2-B8, V2-D5, V2-A3, V2-X5, [#128](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/128),
[#132](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/132) - all of these
scale with merchant and buyer volume rather than gating correctness.

### If the schedule slips, cut population, not safety

The right lever is the size of the merchant allowlist and the buyer cohort, not the security or
money-correctness set. A pilot over a few hundred explicitly allowlisted Stripe-connected merchants
defers V2-B7, V2-B6 and V2-B3 without deferring a single item that protects a buyer's money.

### Open decisions needed from the owner

1. [#40](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/40) - add a
   structured service delivery address, or exclude home-service verticals from v2 admission?
2. [#9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9) - is authentication
   MUST or SHOULD in USP for privileged ops, and is the v2 mechanism OAuth `client_credentials` +
   DCR, or Wix-internal gateway authentication with a documented external contract? (Consumer
   identity linking and Link-token piggyback are already ruled out as answers; see [§1a](#1a-identity-authentication-and-authorization-clarifications).)
3. V2-X6 mechanism choice - for UCP-Native + Link agents, is platform-authenticated get/cancel
   under V2-X1 sufficient, or must v2 also ship a booking-scoped capability credential (#134)?
4. [#125](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/125) - full LPOS,
   or a minimal scheduled-sync + vault subset for v2?
5. [#156](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/156) - accept the
   breaking namespace migration on day 1-2, or knowingly launch on identifiers hosted at a domain we
   do not own?

---

## 7. Labelling actions

| Action | Issues |
|---|---|
| Add `v2` | 9, 40, 42, 47, 54, 59, 75, 86, 108, 114, 118, 123, 124, 125, 126, 128, 132, 134, 136, 141, 143, 144, 149, 155, 156 |
| Add `v>2` | 17, 26, 44, 46, 49, 51, 52, 55, 58, 68, 91, 92, 93, 94, 102, 103, 106, 111, 112, 115, 116, 119, 120, 121, 122, 127, 133, 135, 139, 147 |
| Add `requires-approval` | 9, 40, 44, 94, 102, 114, 118, 119, 120, 121, 122, 125, 126, 127, 128, 134, 141, 144, 147, 156 |
| Create + label `v2` (after plan approval) | the 35 `V2-*` issues in [section 4](#4-step-2---missing-mandatory-issues-to-create), including **V2-X6** (Authorize booking get/cancel and PII) |

Existing `v1` / `v>1` labels are preserved; v2 labels are additive. Do not create the `V2-*`
GitHub issues or relabel open issues until this plan is approved.
