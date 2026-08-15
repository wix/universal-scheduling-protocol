# USP + UCP v2 - Production Readiness Plan (2 weeks)

> **Status:** approved; GitHub issues created (2026-08-05); **reconciled against GitHub, the spec
> and the agent on 2026-08-15** (see [§7](#7-labelling-actions) for what changed).
> **Goal:** take the existing end-to-end UCP-Native booking demo to a production MVP.
> **Predecessor:** [`plans/USP+UCP_implementation_plan.md`](USP+UCP_implementation_plan.md) (v1, the 2-week demo).
> **Registry design:** [`plans/usp-registry-design-plan.md`](usp-registry-design-plan.md).
> **Issues:** every item is a GitHub issue in
> [`wix-private/universal-scheduling-protocol-spec`](https://github.com/wix-private/universal-scheduling-protocol-spec),
> linked inline by number.

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
  - [3.2a Added after the 2026-08-05 plan (new `v2` issues)](#32a-added-after-the-2026-08-05-plan-new-v2-issues)
  - [3.3 Exclusions](#33-exclusions)
- [4. Step 2 - missing mandatory issues to create](#4-step-2---mandatory-issues-created-for-this-plan)
  - [4.1 Cross-cutting](#41-cross-cutting)
  - [4.2 Track A - Link agent (`linkusp-cli`)](#42-track-a---link-agent-linkusp-cli)
  - [4.3 Track B - USP registry](#43-track-b---usp-registry)
  - [4.4 Track D - Wix business USP (`usp-impl`)](#44-track-d---wix-business-usp-usp-impl)
  - [4.5 Track E - UCP checkout (`acp-checkout`)](#45-track-e---ucp-checkout-acp-checkout)
  - [4.6 Conformance, docs and operations](#46-conformance-docs-and-operations)
- [5. Ordering constraints](#5-ordering-constraints)
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
(see [§1a](#1a-identity-authentication-and-authorization-clarifications) and [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162)).

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
[#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157), [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162),
[#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119), and
[#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134).

### The authentication mechanism is DECIDED - `platform_key_pop` (2026-08-15)

[#9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9) is **no longer an
open question.** The design landed on `master` in PR #200 as USP **`2026-08-14`**,
[`specification.md`](../specification.md) **§10.1.6** ("Platform Authentication for Privileged
Operations"). Everything below in this section remains true, but it now explains *why the landed
design looks the way it does* rather than framing a decision to be taken.

**Two authority tiers, scoped honestly.** Platform identity answers *"which platform is calling"*,
not *"may this caller act on this booking."* Under permissionless onboarding, platform identity is
close to worthless as a cross-booking control - anyone can become *a* platform - so it contributes
identification, rate-limiting and revocation, and the per-resource question is answered separately:

| Tier (`x-usp-access`) | Applies to | Authorized by |
|---|---|---|
| `public` | catalog, availability, profile, registry search/get | nothing; anonymous is fine |
| `privileged_platform` | create booking/hold/waitlist, feed subscribe, registry register/update/delete | a mechanism from the business's `AuthorizationPolicy` |
| `privileged_scoped` | get/update/cancel/reschedule/confirm on an **existing** booking, hold or waitlist entry | same, and **SHOULD** prefer a retained `booking_scoped_credential` |

**`platform_key_pop` (§10.1.6).** The calling platform generates an **ephemeral Ed25519 key it
never transmits** and proves possession on every privileged request as a compact JWS derived from
DPoP ([RFC 9449](https://www.rfc-editor.org/rfc/rfc9449)). The business records the
[RFC 7638](https://www.rfc-editor.org/rfc/rfc7638) thumbprint (`jkt`) as the platform identifier
and binds any credential it issues to that thumbprint via `cnf.jkt`. Nothing is published,
registered or rotated, and **the platform profile stays keyless** - which is what makes the
mechanism permissionless, and why it suits a population of distinct personal-agent instances.

**`booking_scoped_credential`.** Issued at booking/waitlist creation, it authorizes operations on
**one specific booking**, independent of the calling platform's identity. Issued to a
`platform_key_pop` caller it carries `cnf` and is therefore **sender-constrained**: the credential
value alone is not usable. A credential that was issued with `cnf` but is presented without a valid
proof **MUST** be treated as absent, not as a bearer token (`pop_proof_missing` / `pop_proof_required`, HTTP 401).

**Policy publication.** Businesses **MUST** publish which mechanism(s) they require in an
`AuthorizationPolicy` ([`schemas/profile.json`](../schemas/profile.json) `$defs/AuthorizationPolicy`).
In **UCP-Native Mode** - the only v2 mode - that policy is published as **`config.authorization` on
the `dev.usp.services` service binding**, because USP does not add top-level members to a UCP profile.

**Enforcement is `required` by default, so client and server must land together.** The
`linkusp-cli` client half is **already implemented** (#9 AC-L) with the conformant posture on by
default, which means it **refuses privileged calls against a business that publishes no
`authorization` policy**. Until `usp-impl` publishes the policy and verifies proofs, the shipped
client cannot transact against it. This is a hard sequencing constraint on
[#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157)/[#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162), not a preference.

**v2 accepts `platform_key_pop` only.** RFC 9421 `http_message_signature` is the spec's RECOMMENDED
alternative and remains in the mechanism menu, but v2 does **not** implement it: no signature
verification, no `keyid`/`keys` resolution, no `Content-Digest`. The menu is open, so it can be
added later without a breaking change - reinstate it when a third-party agent that signs rather
than proves possession actually needs it.

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
full identity-linking implementation. The landed `platform_key_pop` design reinforces this: platform
authentication is an **ephemeral key the agent generates locally and never transmits**, which is
precisely the opposite of forwarding a wallet token it was given.

The **legitimate narrow form already shipped** is: use the Link token *locally* to fetch buyer
attributes, then populate checkout `buyer` fields under consent. That is attribute fill-in, **not**
identity linking.

### "Email match under consent" is not identity linking and not [#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157)

Matching a buyer email to a CRM record (even with consent language) is **CRM association only**.
Email is forgeable and is not proof of identity. It does **not** authorize `GET` / cancel of
bookings, and it does not protect PII in booking responses.

An earlier "cheapest path" framing only addressed a weak continuity goal (recognize a returning
customer without a full Wix login every time). It does **not** satisfy consumer authentication to
the business, and it is **not** a substitute for [#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157) or [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162).

### Why unauthenticated UCP/USP transaction APIs are dangerous

Public resources (catalog, availability, profile / `/.well-known/ucp`) **may** remain anonymous.
The danger is **privileged operations**: create / update / complete / cancel checkout, booking
mutations, inventory holds, payment-adjacent complete, and any response that returns buyer PII,
with no trustworthy attribution, rate-limit key, or revocation handle.

A site UUID is approximately a public storefront id, not a credential. It is fine for discovery
routing. It is **not** sufficient to act as a platform on the control plane.

**[#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157)** therefore means: authorize privileged ops and attribute the calling platform/agent
(`platform_key_pop` verification + `UCP-Agent` / `USP-Agent` validation and identity binding). It
does **not** mean "force identity linking for browsing." The `public` tier in the table above stays
anonymous by design.

### Booking get / cancel / PII authorization is a v2 requirement

**Launch-blocking requirement:** booking get and cancel (and any response that includes buyer PII)
**MUST** be authorized. Unauthorized or cross-booking access **MUST** fail. Email obscurity and
booking-id obscurity alone do **not** count.

Identity linking is **one mechanism**, not the only requirement. **The mechanism choice is now
made:** the spec answers this with the `privileged_scoped` tier plus a sender-constrained
`booking_scoped_credential`.

1. **Booking-scoped capability credential** issued at create, bound to the caller's `jkt` via
   `cnf` - **this is the v2 mechanism.** It answers the actual authorization question ("does this
   caller hold the credential for this booking?") rather than the weaker "is this caller a known
   platform?". The client-side retention half shipped as
   [#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134) (closed,
   completed).
2. **Platform-authenticated access** ([#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157)) - necessary, and it is what
   authenticates the `privileged_platform` tier, but on its own it is **not** sufficient for
   cross-booking control under permissionless onboarding.
3. **Full consumer identity linking**
   ([#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119)) - only
   when merchant-member semantics are in scope. Still deferred.

Do **not** frame "only the consumer who booked via merchant-member identity" as the sole
requirement. Frame **authorized access** as required; treat identity linking as optional unless
member semantics are required.

**Required for UCP-Native + Link agents in v2:** [#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157) platform authentication via
`platform_key_pop`, **plus** the sender-constrained booking-scoped credential ([#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162)). Keep #119
deferred unless a merchant needs member vs guest pricing, package credits, member-only
history/cancel rules, or an existing member portal that must not trust agent-asserted email alone.

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
| C | Link platform services (API proxy, hosted platform profile) | Link platform + `linkusp-cli` | - | [`yahalomran`](https://github.com/yahalomran) |
| D | Wix business USP adapter | `wix-private/wix-vmr-repo` -> `usp-impl` | Java (Loom Prime) | [`maoryeh`](https://github.com/maoryeh) |
| E | UCP checkout + USP `paid_bookings` | `wix-private/ecom` -> `server/agentic-checkout/acp-checkout` | Scala | [`maoryeh`](https://github.com/maoryeh) |
| F | Stripe SPT / Cashier | `wix-private/ecom` + Stripe | Scala | [`maoryeh`](https://github.com/maoryeh) |
| S | Spec + schemas | this repo | JSON Schema / Markdown | [`yahalomran`](https://github.com/yahalomran) |

**GitHub issue assignment:** when creating the new mandatory issues in [§4](#4-step-2---mandatory-issues-created-for-this-plan), assign each issue to the track owner above:

- Assign to [`yahalomran`](https://github.com/yahalomran): tracks **A**, **C**, and **S**.
- Assign to [`maoryeh`](https://github.com/maoryeh): tracks **B**, **D**, **E**, and **F**.

Cross-track issues (for example S + B) take the assignee of the primary implementation track; if unclear, default to the first-listed track's owner.

---

## 3. Step 1 - v2 from existing open issues

As reconciled 2026-08-15, **26 pre-existing issues are in v2**: the 13 mandated ([§3.1](#31-mandated-inclusions),
one of which - #42 - is done), the 8 judgement ([§3.2](#32-judgement-inclusions-label-requires-approval),
one of which - #134 - is done), and the 5 added since ([§3.2a](#32a-added-after-the-2026-08-05-plan-new-v2-issues),
two of which were created by this pass). Three previously-listed issues left the set: #124
(re-scoped to `v>2`), #125 and #196 (closed). The remaining ~30 open issues stay deferred
([§3.3](#33-exclusions)).

### 3.1 Mandated inclusions

These were designated for v2 up front. Justification below is the production implication of *not*
doing them.

| # | Title | Track | Assignee | Production implication if omitted |
|---|---|---|---|---|
| [#42](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/42) | Disambiguate the term "Discovery" | S | [`yahalomran`](https://github.com/yahalomran) | ✅ **Done** (closed, completed). The same word covered consumer search, profile/endpoint resolution and platform-business onboarding. v2 builds all three at once (registry search, `UCP-Agent` profile validation, credential onboarding) with different auth models, TTLs and idempotency. Conflating them in the normative text is how they get conflated in code - and the registry, the agent and `acp-checkout` are being written by three different teams from that one text. |
| [#47](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/47) | `usp-impl` returns HTTP 200 for all errors | D | [`maoryeh`](https://github.com/maoryeh) | **Confirmed still true**, and it is on the money path. Every handler catches `Exception` and returns a normal proto response, so `confirmation_failed` and `upstream_error` arrive as HTTP 200. Any client that branches on status - which is every standard HTTP library - reads a failed payment confirmation as success. The agent already carries a fragile `BookingServerError` workaround that sniffs the `messages` array. |
| [#54](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/54) | Multi-taxonomy `categories[]` on `Service` | S | [`maoryeh`](https://github.com/maoryeh) | **Resolved in spec:** singular `category` removed; enriched `categories[]` (`ServiceCategory`) is the sole representation, with an explicit primary rule and registry projection pick order. Implementers must adopt the new shape before merchants are live. |
| [#59](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/59) | Registry filter-matching semantics unspecified | S + B | [`maoryeh`](https://github.com/maoryeh) | Filters are a yes/no contract. Range overlap vs point match, cross-currency price, `free` pricing, `undetermined` duration, geo units, and exclusion of coordinate-less businesses are all undefined. The registry has already made unilateral choices in `VespaQueryBuilder`; unwritten choices cannot be tested against, and a second registry would return different results for the same query. |
| [#75](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/75) | Link platform discovery integration test | A/C | [`yahalomran`](https://github.com/yahalomran) | Discovery is the entry point of every booking and is the one step with no integration coverage against a live registry. Without it, a registry search-semantics or projection change silently breaks every agent in the field and is only discovered by buyers. |
| [#86](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/86) | Execution guard on `complete_checkout` | E | [`maoryeh`](https://github.com/maoryeh) | **Double charge.** `acp-checkout` reads `Idempotency-Key` in exactly one place (`create_checkout`). `complete_checkout` has no guard, and in the booking flow the charge happens *before* `markCheckoutAsCompleted` - so any retry inside that window charges the buyer a second time. Today the only mitigation is a "do not retry" string in the response message. |
| [#108](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/108) | Prefer UCP checkout `payment_handlers` for `network_id`; demote MPP decode / 402 probe | S + A | [`yahalomran`](https://github.com/yahalomran) | The published normative docs and the SKILL still tell agents to obtain `network_id` by decoding an MPP or probing the merchant for a 402. That is a bridge built for a demo; in production it teaches every agent implementer a path that bypasses the handler contract and breaks the moment Stripe's published schema lands. `acp-checkout` already carries `TODO(#108)` on its provisional handler `spec`/`schema` URLs. |
| [#123](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/123) | Apply UCP capability intersection to checkout payloads | A | [`yahalomran`](https://github.com/yahalomran) | The agent computes the intersection and uses it only as a pass/fail gate; the negotiated set is never bound into `create_checkout` / `complete_checkout`. UCP requires the negotiated capability set to be carried in the request binding, not inferred from a header. Without it, a merchant cannot tell which capability version the agent actually intends to use, which is exactly the ambiguity that breaks the first time either side ships a second version. |
| [#132](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/132) | Publish `linkusp-cli` to PyPI | A | [`yahalomran`](https://github.com/yahalomran) | The SKILL installs via `git+ssh://git@github.com/...`, i.e. it requires a private SSH key with repo access on the consumer's machine. No third-party harness can install the skill, no version can be pinned, and no security fix can be shipped without every user re-pulling `main`. |
| [#136](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/136) | Demo vs `linkusp` secrets-mode boundary | A | [`yahalomran`](https://github.com/yahalomran) | `demo` mode is not offline - it talks to the live registry and real merchants with demo defaults. Without a hard, documented boundary (and a production default), a production install silently runs with demo identity and demo config against real buyers and real money. |
| [#143](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/143) | SPT generation for merchants connected to Stripe under Cashier | F | [`olehtarapata`](https://github.com/olehtarapata), [`yahalomran`](https://github.com/yahalomran) | Today `network_id` is resolved only from the Wix-Payments agentic configuration. Merchants connected to Stripe under Cashier therefore cannot produce an SPT - and they are part of the v2 target population. Omitting this shrinks the addressable merchant set to a subset that nobody has quantified. |
| [#149](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/149) | `availability_hint` may influence service-search ranking | S + B | [`danieljaffe1`](https://github.com/danieljaffe1) | The registry indexes availability attributes and does not score on them, so "book me the soonest haircut" - the single most common agent intent - ranks by text relevance and geo distance only. Buyers are offered fully-booked services first, then discover the failure three network hops later at availability query. |
| [#155](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/155) | Document checkout `links` types + merchant totals/links integration test | E | [`maoryeh`](https://github.com/maoryeh) | `totals` and `links` emission is currently proven only by live observation of one merchant. With no CI assertion, a mapper change silently drops the privacy policy or terms link from a real checkout, which is a compliance defect, not a cosmetic one. |

### 3.2 Judgement inclusions (label `requires-approval`)

| # | Title | Track | Assignee | Production implication if omitted |
|---|---|---|---|---|
| [#9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9) | Authentication mechanism design | S | [`yahalomran`](https://github.com/yahalomran) | ✅ **Spec half landed** (USP `2026-08-14`, PR #200, §10.1.6): `platform_key_pop` + sender-constrained `booking_scoped_credential`. ✅ **Client half landed** in `linkusp-cli` (AC-L), enforcement `required` by default. **What remains is server-side**, tracked as [#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157) (#157, which absorbed #203) and [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162) (#162), plus registry writes in [#126](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/126) §5.4a. Keep this issue open until the server side interoperates, because the shipped client refuses privileged calls against a business publishing no `authorization` policy - client and server **must land together**. Scope was and remains **platform/agent authentication of privileged ops** (see [§1a](#1a-identity-authentication-and-authorization-clarifications)), not consumer identity linking and not "force login to browse catalog"; Link wallet tokens and email match were ruled out as answers. |
| [#40](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/40) | Service delivery address gap | S + D | [`maoryeh`](https://github.com/maoryeh) | There is no first-class field for the buyer's service address anywhere - not on `POST /bookings`, not on `Buyer`, and `Booking.location` is the *business's* location. The flagship demo merchant is an HVAC business, i.e. a home service, and the SKILL already instructs the agent to supply the buyer's home address. Today that address can only go into free-text `notes`: unvalidated, unparseable for dispatch, and absent from the checkout page. A production home-service booking is therefore not fulfillable. **Confirmed in v2** - this is no longer an open question for the owner. Which remedy to ship (a first-class structured service-address field, or excluding home-service verticals from the v2 admission gate) is an implementation choice made by [`maoryeh`](https://github.com/maoryeh) during execution; whichever is chosen must be recorded explicitly, since "exclude the vertical" silently narrows the target merchant population. |
| [#114](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/114) | Publish hosted per-agent platform profile | A/C | [`yahalomran`](https://github.com/yahalomran) | The profile URI is the unit of platform identity; businesses MUST fetch it over HTTPS with no redirects and cache it by URI. The demo gets away with an unfetchable local fixture only because neither `usp-impl` nor `acp-checkout` currently reads the header. The moment either one validates it - which v2 requires - every call from every agent fails. This has to land *before* the server-side validation it enables. |
| [#118](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/118) | `USPTokenStore` unit and integration tests | A | [`yahalomran`](https://github.com/yahalomran) | `USPTokenStore` (RFC 8414 discovery, RFC 7591 DCR, `client_credentials`, refresh with a 60s margin) becomes the *only* production **platform-to-merchant** auth path once the `LINKUSP_*_BEARER` env overrides are removed, and it has zero tests. An untested refresh path fails as a mid-booking auth error for every user simultaneously when tokens age out. Distinct from Link wallet tokens (never forwarded; not consumer identity linking; see [§1a](#1a-identity-authentication-and-authorization-clarifications)). |
| [#126](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/126) | Production USP registry MVP | B | [`maoryeh`](https://github.com/maoryeh) | The registry is the entry point of every booking and is today an explicitly Phase-1 demo service: no auth on any endpoint, no Update or Delete, hardcoded to the **dev** Vespa cluster (`VESPA_PLATFORM = "dev-v8"`), no metrics, no health checks, no pagination, no outbound timeouts, and never runtime-tested against a cluster. It cannot be exposed publicly in this state. This is the umbrella; the concrete work is [[#168](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/168)..B9](#43-track-b---usp-registry). |
| [#128](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/128) | Service catalog enrichment and QA pipeline | B | [`maoryeh`](https://github.com/maoryeh) | With admission widened from one hand-picked merchant to the whole Wix Stripe population, data quality stops being cosmetic. The registry today silently substitutes `"Wix Bookings Business"` / `America/New_York` / `USD` when SiteProperties returns blanks, so a misconfigured site lands in the index with fabricated identity in the wrong timezone. Add the QA gates and the quarantine bucket; defer the LLM enrichment beyond what already exists. |
| [#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134) | Booking cancel: store credential + `flow book cancel` | A + S | [`yahalomran`](https://github.com/yahalomran) | ✅ **Done** (closed, completed). Cancellation is a core booking-lifecycle operation (USP §5) and was unreachable from the agent: the customer credential was not retained after booking and the `continue_url` session token expires in ~5 minutes. **This is the client-side half of the v2 booking-authorization story:** the retained credential is the `booking_scoped_credential` that [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162) authorizes get/cancel against, so the *server* half (issuing it with `cnf`, verifying the proof) is still outstanding under [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162). Full merchant-member identity linking remains [#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119) (deferred). |
| [#141](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/141) | Detect a connected Stripe account before advertising the SPT handler | E/F | [`maoryeh`](https://github.com/maoryeh) | **This is the v2 admission constraint itself.** Confirmed: gating is the `uspBookingsEnabled` toggle alone; `resolveNetworkId` reads `stripe.supports_shared_payment_token` and then advertises `com.stripe` regardless, failing open on error. So a site with no usable Stripe account still advertises the handler, the agent acquires a real SPT against the buyer's wallet, and the charge dies late at Cashier as `payment_declined` - a payment failure presented for what is really an unoffered method. |
| [#144](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/144) | Replace `BOOKINGS.BOOKING_READ_ANY` with least-privilege site-scoped authorization | D | [`maoryeh`](https://github.com/maoryeh) | A temporary grant lets `usp-impl` read **any booking on any Wix site**. That is a cross-tenant PII capability sitting behind a service whose own inbound surface is unauthenticated. It cannot go to production and it is explicitly marked as a stopgap that must be reverted. |
| [#156](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/156) | Migrate namespace authority `usp.dev` -> `usp-protocol.dev` | S | [`yahalomran`](https://github.com/yahalomran) | We do not own `usp.dev`, yet every normative identifier, `$id`, profile `spec`, profile `schema` and problem `type` points there, and §2.5 binds the `dev.usp.*` namespace to that origin. Profiles MUST carry `spec` and `schema` per capability entry; ours resolve to a domain a third party can acquire and serve conflicting content from. This is a **breaking** revision: doing it now costs a rename, doing it after launch forces the break onto live merchants, cached profiles and deployed agents. `usp-protocol.dev` is already purchased. |

### 3.2a Added after the 2026-08-05 plan (new `v2` issues)

These were labelled `v2` after the plan was written and are integrated here.

| # | Title | Track | Assignee | Production implication if omitted |
|---|---|---|---|---|
| [#197](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/197) | Legal guidelines | S (product/legal) | [`yahalomran`](https://github.com/yahalomran) | **Launch-gating and not an engineering item.** Legal requires (1) notifying existing Wix Bookings providers that their services may be exposed to AI agents, with a simple **opt-out**; (2) excluding providers who asked not to be indexed by Google, **opt-in only**; and (3) **booking-experience parity** with the merchant's own website flow - identical price/currency/tax, the merchant's own policy-consent and required-checkbox flow, service-specific gates (age, eligibility, geographic availability), click-to-cancel for recurring services, and accessible authorization-evidence/audit trail from Link. Exposing merchants' services without the notice-and-opt-out commitment is a legal exposure, not a product gap. Engineering halves of (1) and (2) are #206 and #207 below; **item (3) is engineering-heavy and not yet split into issues** - see [§7](#7-labelling-actions). |
| [#206](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/206) | Honor merchant opt-out across registry admission, eviction and serving | B (+D) | [`maoryeh`](https://github.com/maoryeh) | The opt-out promised in #197 is only real if the registry enforces it. Today the registry has no notion of merchant consent, so an opted-out business keeps being indexed, returned in search and booked. Needs a single authoritative flag, refusal at admission, **eviction** of already-indexed entries (via [#168](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/168) Delete, re-checked by [#169](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/169)), and suppression at serving so a stale entry cannot leak. |
| [#207](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/207) | Exclude non-indexed provider sites from registry admission (opt-in only) | B | [`maoryeh`](https://github.com/maoryeh) | A site owner who suppressed search-engine indexing has expressed an intent not to be surfaced by automated discovery. The registry has no notion of that preference, so it indexes them **by default - the wrong default**. Requires the inverse gate (exclude unless explicit opt-in) and must **fail closed** when the preference cannot be read, rather than reusing the registry's existing "silently substitute a default" pattern. |
| [#201](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/201) | Generated USP SDKs and strict schema conformance | A + S | [`yahalomran`](https://github.com/yahalomran) | `linkusp-cli` hand-writes ~51 Pydantic models mirroring the USP schemas, and the models silently ignore unknown members - so spec fields simply vanish on parse. This already shipped two live defects: **`Booking.revision` was dropped**, which silently disabled §5.6 conditional writes end to end (the `If-Match` was wired but never sent), and `USPBusinessInfo.locations` was dropped. The property-presence sweep added afterwards compares **names only**, so wrong types, wrong optionality, wrong enums and wrong nesting all still pass - six spec-required properties are currently modelled as optional and the sweep is blind to every one. Generation from the canonical `schemas/` is the only thing that makes conformance structural rather than aspirational. |
| [#205](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/205) | Move the USP spec to a new public Wix repo | S | [`yahalomran`](https://github.com/yahalomran) | The spec is the normative reference that `spec` and `schema` URLs in every profile point at, and it currently lives in a **private** repo. Businesses and third-party agents cannot resolve what they are required to implement. Pairs with [#156](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/156): #156 moves the namespace authority to a domain we own, #205 makes the artefact behind it publicly reachable. Both are cheapest before launch and get harder once identifiers are cached in the field. |

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

| # | Title | Assignee | Why it is not strictly necessary for v2 |
|---|---|---|---|
| [#44](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/44) | Business record & credential lifecycle spec section | [`yahalomran`](https://github.com/yahalomran) | Formalizes the persisted onboarding record plus signing-key rotation and revocation. Key rotation exists to serve webhook signing, which v2 does not do, and v2 has exactly one platform. **Further reduced by the landed design:** under `platform_key_pop` the platform key is ephemeral and never published, so there is no signing key to persist, rotate or revoke; identity is the recorded `jkt`. Revocation is the registry eviction path ([#169](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/169)). |
| [#94](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/94) | Registry capability and payment search filters | [`maoryeh`](https://github.com/maoryeh), [`yahalomran`](https://github.com/yahalomran) | The admission gate ([#169](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/169)) makes every indexed business UCP-Native and SPT-capable *by construction*, so a `supports_spt` / `deployment_mode` filter has no reachable effect in v2. It becomes necessary the moment the registry admits a second merchant class. |
| [#102](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/102) | UCP conformance gaps rollup | [`yahalomran`](https://github.com/yahalomran) | A tracker for gaps deliberately excluded here. Production-relevant children are pulled out: platform authentication becomes [#9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9)/[#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157), booking get/cancel/PII authorization becomes [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162) (with [#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134)), trusted-UI becomes [#189](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/189). Optional `dev.ucp.common.identity_linking` remains under [#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119) / v>2 unless member semantics are required. |
| [#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119) | Interactive OAuth / identity linking | [`yahalomran`](https://github.com/yahalomran) | Deferred for **merchant-member semantics**, not because booking PII may stay unprotected. v2 UCP-Native + Link agents do not require `dev.ucp.common.identity_linking`; checkout may be unauthenticated unless that capability is negotiated. `usp-impl` exposes no authorization server today; `client_credentials` + DCR covers platform-to-business. **Link wallet token piggyback is not viable** (wrong issuer/audience/scopes; opaque; no merchant-usable discovery/JWKS; token confusion / wallet privilege leak). Email match under consent is CRM association only, not identity linking. When #119 is implemented, follow [`specification.md`](../specification.md) §10.2.4 (PKCE S256 + RFC 9207 `iss`). Needed when a merchant requires member vs guest pricing, package credits, member-only history/cancel rules, or an existing member portal. |
| [#120](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/120) | Unit test `complete_checkout` signal retry | [`yahalomran`](https://github.com/yahalomran) | `acp-checkout` emits no `signal` messages at all, and it is the only merchant implementation in v2, so the retry branch is unreachable in production. The genuine risk in that code path - a retry minting a fresh idempotency key - is covered by [#163](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/163). |
| [#121](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/121) | Log negotiated UCP-Version in demo E2E | [`yahalomran`](https://github.com/yahalomran) | Changes demo harness step logs, not production behavior. Production visibility of the negotiated version is covered by [#160](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/160). |
| [#122](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/122) | Use `discover_service_via_registry` in demo and flow paths | [`yahalomran`](https://github.com/yahalomran) | A refactor to remove drift risk between the demo and the shared helper. No production capability is missing; the shipped `flow` path is exercised by [#75](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/75). |
| [#127](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/127) | Link-hosted buyer calendar OAuth | [`yahalomran`](https://github.com/yahalomran) | Calendar conflict-checking is an optional USP extension (§11.2), not part of the booking flow. The *unacceptable* part - Google client credentials on consumer devices - is fixed far more cheaply by [#166](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/166), which keeps the superagent connector path and disables device-side OAuth. |
| [#147](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/147) | UCP-Native deposit support | [`yahalomran`](https://github.com/yahalomran) | Deposits are explicitly out of scope. |

---

## 4. Step 2 - mandatory issues created for this plan

35 issues, **all created 2026-08-05** in `wix-private/universal-scheduling-protocol-spec` and all
still open and `v2`-labelled. Each one is a gap found by reading the two specs against the four
codebases; each states what breaks in production without it.

> **[#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157) and [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162) were rewritten on GitHub (2026-08-15)** around the landed `platform_key_pop`
> design; #157 additionally absorbed #203. The rows below reflect the rewritten scope.

### 4.1 Cross-cutting

| # | Title | Repos | Assignee | Production implication if omitted |
|---|---|---|---|---|
| [#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157) | Authenticate inbound USP/UCP privileged requests and validate platform identity | E, D, B | [`maoryeh`](https://github.com/maoryeh) | The whole control plane is currently open. `acp-checkout` is `service_exposure = PUBLIC` with the missing-permission lint suppressed, and `createCallScope` only validates that `site_id` is a UUID before stamping site context and signing *outbound* calls as the platform app - so anyone who knows a site UUID can create, mutate, complete and cancel checkouts on that site. `usp-impl` reads no `Authorization` header anywhere, and only `BookingHandler` consults the per-site toggle, leaving catalog, availability and profile open for every routed site (anonymous browse of public resources is acceptable; anonymous privileged ops are not). Neither service reads `UCP-Agent` / `USP-Agent` inbound, so there is no platform identity to authenticate, attribute, rate-limit or revoke. Scope (**rewritten around the landed design**; #157 absorbed #203): implement **`platform_key_pop`** verification per §10.1.6 - the normative verification order, `jkt` computation and TOFU binding, `cnf`-bound credential issuance, the anti-downgrade MUST, a `jti` replay cache with bounded skew, distinguishable `pop_proof_missing` / `pop_proof_required` errors, and keyless-profile acceptance - plus publication of the `AuthorizationPolicy` as `config.authorization` on the `dev.usp.services` binding, mandatory `UCP-Agent`/`USP-Agent` with HTTPS-only + no-redirect profile fetch and caching, identity binding between credential and advertised profile, and the per-site gate on every privileged handler. **v2 implements `platform_key_pop` only** - no RFC 9421 `http_message_signature`. **Not in scope:** consumer identity linking, Link-token piggyback, or email-as-auth (see [§1a](#1a-identity-authentication-and-authorization-clarifications)); registry writes are [#126](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/126) §5.4a. **Must land together with the already-shipped client** (see [§1a](#1a-identity-authentication-and-authorization-clarifications)); depends on [#114](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/114) landing first. |
| [#158](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/158) | Timeouts, bounded retries with backoff, and circuit breaking on every outbound call | A, B, D, E | [`maoryeh`](https://github.com/maoryeh), [`yahalomran`](https://github.com/yahalomran) | There is not one explicit deadline on any outbound call in any of the four components: `acp-checkout` -> `usp-impl` gRPC and Cashier, `usp-impl` -> Wix Bookings/Confirmator/SiteProperties, registry -> vFeed/vSearch/Bookings/AI-gateway, agent -> merchant. `acp-checkout`'s only retry is an immediate no-backoff `withRetry(3)` on a post-charge re-read; the agent retries only 429/503 and not 5xx or connect timeouts. A single slow dependency therefore hangs the buyer's agent turn with no bound, and a failing merchant keeps being hammered. |
| [#159](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/159) | Secrets, PII and credential log hygiene; remove all demo bypasses | A, B, D, E | [`maoryeh`](https://github.com/maoryeh), [`yahalomran`](https://github.com/yahalomran) | Concretely: `acp-checkout` runs with `logRequests = true, logResponses = true`, so the `complete_checkout` body - which contains `payment.instruments[].credential.token`, the Stripe SPT - is written to logs, and `ConvertCreateCheckoutRequest` logs the entire buyer object at info level. `usp-impl` returns `e.toString()` to callers on every `upstream_error`. The agent writes buyer name/email/phone, booking ids and spend ids to a mode-`0644` `~/.linkusp/.usp-session.json`, persists merchant OAuth `client_secret` and access tokens unrestricted, and appends full request/response bodies to a multi-megabyte `http_trace.log`. `LINKUSP_UCP_TEST_SPT` completes a checkout without going through the buyer's Link approval, and `--fake-payload` injects buyer identity without `link-cli`. Any one of these is a launch blocker on PCI/GDPR grounds; the two bypasses additionally defeat the human gates the SKILL contract is built on. Includes a retention/purge path for agent-side buyer data (USP §10.1.3). |
| [#160](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/160) | Money-path observability: metrics, alerts and an end-to-end correlation id | A, B, D, E | [`yahalomran`](https://github.com/yahalomran) | **Zero custom metrics exist in any of the four components.** There is no counter for charge attempts, declines, `payment_captured_booking_unconfirmed`, `confirmation_failed`, `price_mismatch`, registry search errors or search latency, so nothing can be alerted on and no SLO can be measured. There is also no correlation id: joining "this buyer's failed booking" across agent -> registry -> `acp-checkout` -> `usp-impl` -> Cashier means grepping on a booking id across four systems. A money-handling system that cannot detect its own failures is not production-ready by any standard. |
| [#161](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/161) | Booking-flow latency budget, SLOs and a staging latency/soak test | all | [`yahalomran`](https://github.com/yahalomran) | "Latency must be within acceptable limits" is a v2 requirement with no target attached; the registry design's own scale/NFR decision (O14) is still recorded as TBD. Without a per-step budget and a repeatable measurement, the known hot spots (registry search, the agent's serial discovery fan-out, poll loops of up to 10 minutes) cannot be signed off or regression-tested. |
| [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162) | Authorize booking get/cancel and any response carrying buyer PII | D, E, A, S | [`maoryeh`](https://github.com/maoryeh), [`danieljaffe1`](https://github.com/danieljaffe1) | **Launch-blocking authorization requirement**, separate from optional identity linking. Today booking get/cancel and PII-bearing responses are reachable without a trustworthy authorization story (email match and booking-id obscurity do not count). Unauthorized or cross-booking access MUST fail. **The mechanism is no longer a choice:** implement the `privileged_scoped` tier with a **sender-constrained `booking_scoped_credential`** - issued at booking/waitlist create carrying `cnf.jkt` bound to the caller's `platform_key_pop` key, and required (together with a valid proof) on get/update/cancel/reschedule and every PII-bearing response. A credential issued with `cnf` but presented without a valid proof **MUST** be rejected, never accepted as a bearer token. Platform authentication under [#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157) is necessary but **not sufficient** on its own, since permissionless onboarding means anyone can be *a* platform. Full consumer identity linking ([#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119)) stays deferred unless merchant-member semantics are required. The agent-side retention half already shipped as [#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134); this issue is the **server** half and is **release-blocking for the client**, which already enforces by default. |

### 4.2 Track A - Link agent (`linkusp-cli`)

| # | Title | Assignee | Production implication if omitted |
|---|---|---|---|
| [#163](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/163) | Stable `Idempotency-Key` across HTTP retries | [`yahalomran`](https://github.com/yahalomran) | Keys are minted with `uuid.uuid4()` *inside* the header builder, and `with_http_retry` re-invokes the request function - so every retry attempt carries a **new** idempotency key. This is the agent-side half of [#86](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/86): server-side dedupe cannot work when the client changes the key. A retried `complete_checkout` or `POST /bookings` produces a double charge or a double booking, and no test asserts key stability. |
| [#164](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/164) | Never report `CONFIRMED` before the booking reaches a terminal confirmed state; add the money-recovery path | [`yahalomran`](https://github.com/yahalomran) | After `complete_checkout` the flow sets `payment.status = paid` and `CONFIRMED` **even when the confirmation wait times out**. The buyer is told "you're booked" on the strength of a charge, not a booking. Combined with the absence of any flow-level `cancel_booking` / `cancel_checkout` wiring and no refund surface, a charge that does not produce a booking leaves the buyer with no automated remedy and the agent with nothing to say. Pairs with [#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134), [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162), and [#184](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/184). |
| [#165](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/165) | Parallelize and cache the discovery fan-out | [`yahalomran`](https://github.com/yahalomran) | Discovery is serial N+1: for each registry hit the agent waits a 200 ms pacing delay, fetches the profile, paces again, then fetches the service. With the client limit of 5 that is already multiple seconds of dead time before the buyer sees a single option, and it scales linearly with result count. This is the most visible latency in the flow and it is the step the buyer is waiting on. |
| [#166](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/166) | Remove device-side Google OAuth credentials from the calendar path | [`yahalomran`](https://github.com/yahalomran) | The base harness performs local Google OAuth, which means shipping Google app client id and secret to every consumer device that installs the SKILL. Minimum fix: use harness-provided connector tokens (as the superagent variant already does) or ship with conflict-checking disabled. Shipping the credentials is a credential-disclosure defect, not a UX question. |
| [#167](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/167) | Production-path E2E with a real Link wallet SPT | [`yahalomran`](https://github.com/yahalomran) | The E2E suite leans on `LINKUSP_UCP_TEST_SPT`, so the SPT acquisition and approval path that actually ships is the one path that is not tested end to end. The payment code that runs in production has never been exercised by CI. |

### 4.3 Track B - USP registry

| # | Title | Assignee | Production implication if omitted |
|---|---|---|---|
| [#168](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/168) | Implement Update (§6.5) and Delete (§6.6) | [`danieljaffe1`](https://github.com/danieljaffe1) | Neither operation exists - no RPC, no handler, no path. There is therefore **no way to correct or remove a registry entry**: a business that unpublishes its site, disconnects Stripe, renames itself or asks to be delisted stays in the index and in search results forever. This also blocks [#169](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/169) and any GDPR/delisting request. |
| [#169](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/169) | Stripe payin-capability admission gate + periodic re-verification and eviction | [`danieljaffe1`](https://github.com/danieljaffe1) | The defining v2 admission rule has no field on `RegistryEntry`, no field in the Vespa business schema, no check in `RegistrationHandler.register` or `OnboardHandler.onboard`, and no filter on either search. There is no reference to Stripe or to any Wix payments service anywhere in the registry. Without this, search returns businesses that cannot be paid, and the failure surfaces as a `payment_declined` against the buyer's real wallet. Re-verification is required because payment connection state changes after onboarding. |
| [#170](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/170) | Opaque cursor pagination; remove the hard 100-result ceiling | [`danieljaffe1`](https://github.com/danieljaffe1) | `PaginationRequest.cursor` is read nowhere, `pagination` is never set on either search response, and hits are capped at `MAX_HITS = 100` with no offset support. Agents can only ever see one page of the entire Wix inventory and have no way to ask for more. USP §9.1.2 additionally requires cursors to be opaque, which cannot be satisfied by a field that is never emitted. |
| [#171](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/171) | Correct error semantics: stop masking backend failures as HTTP 200 + empty results | [`danieljaffe1`](https://github.com/danieljaffe1) | `SearchHandler` catches every exception and returns HTTP 200 with an empty result array plus a `search_failed` message whose content is `String.valueOf(e)`. A vSearch outage is therefore indistinguishable from "no matches" for any client that reads `results`, emits no 5xx for monitoring to alert on, and leaks internal exception text to callers. `findBusinessById` similarly swallows failures and reports `not_found`. Also add RFC 9457 problem details, 404 on missing get, and 204 on delete. |
| [#172](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/172) | Per-environment configuration, health checks and deployability | [`danieljaffe1`](https://github.com/danieljaffe1) | `VESPA_PLATFORM = "dev-v8"` and `AppDefId` are compile-time constants, so the service is hardwired to a **dev** Vespa cluster; there are no health checks, no dependency probes and no alerting, and the Vespa adapters have never been runtime-tested against a cluster. The service cannot be deployed to production as it stands. |
| [#173](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/173) | Freshness: scheduled re-index of entries and availability hints | [`danieljaffe1`](https://github.com/danieljaffe1) | Ingestion is push-only plus a manual per-site orchestrator. Nothing re-runs onboarding, re-pulls a catalog, or refreshes availability hints; stale-service reconciliation only runs *within* a single onboard invocation. Once a site is onboarded, its index decays silently and permanently: deleted services stay searchable, prices go stale, and hints age past the 6-hour confidence window forever. §6.3 asks for re-index within 24h. |
| [#174](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/174) | Onboarding throughput for the full Wix Stripe population | [`danieljaffe1`](https://github.com/danieljaffe1) | `OnboardHandler.onboard` loops over every service in a site and issues an availability query **plus an LLM call** per service, strictly sequentially, inside one synchronous HTTP request, with no timeout, no parallelism, no batching and no cache. That is acceptable for one demo merchant and cannot onboard a merchant population. |
| [#175](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/175) | Search result quality: dedupe multi-location services, constrain `status`, exact-id get | [`danieljaffe1`](https://github.com/danieljaffe1) | The "nearest location per service" grouping was never implemented, so a multi-location service returns one duplicate row per location and consumes the result budget. Service `status` is indexed but never filtered, so a suspended service remains searchable. `findBusinessById` matches with `contains` on `doc_id` rather than an exact lookup. All three degrade the accuracy the v2 requirement calls for. |
| [#176](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/176) | `Idempotency-Key` on registry writes | [`danieljaffe1`](https://github.com/danieljaffe1) | No key is read and no replay cache exists. The public register path mints a fresh `reg_<uuid>` per call, so a client retry silently creates a **duplicate business** in the index - and with no Delete operation ([#168](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/168)) it cannot be cleaned up. |

### 4.4 Track D - Wix business USP (`usp-impl`)

| # | Title | Assignee | Production implication if omitted |
|---|---|---|---|
| [#177](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/177) | Honor `Idempotency-Key` on `POST /bookings` and make `confirm-payment` replay-safe | [`maoryeh`](https://github.com/maoryeh) | `Idempotency-Key` appears nowhere in the service, `CreateBookingRequest.hold_id` is accepted and never read, and there is no dedupe store of any kind. A retried create produces a **duplicate booking on the same slot**; a retried confirm re-invokes the Confirmator instead of returning the current booking. `cancelBooking` is the only operation with (best-effort) replay handling. |
| [#178](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/178) | Enforce pending-booking expiry | [`maoryeh`](https://github.com/maoryeh) | `expires_at` is computed as `now + 30 minutes` on **every read** and is never persisted or enforced, and there is no sweeper. An abandoned checkout therefore holds a real slot indefinitely, so slot inventory leaks and the merchant loses bookable capacity to agents that walked away. |
| [#179](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/179) | Stop emitting fabricated policy and profile data | [`maoryeh`](https://github.com/maoryeh) | `cancellation.allowed` and `rescheduling.allowed` are hardcoded `true` regardless of the merchant's real Wix policy, and fee/deadline fields are never populated - so the agent tells buyers they can cancel free when they cannot, which is a consumer-protection and chargeback exposure. `confirmation_mode` is hardcoded `"auto"` on every booking even though the real mode is read elsewhere. Booking windows are fabricated from defaults (30-minute slot interval, one-year max advance). The profile still advertises `checkout_systems: ["redirect"]`, a checkout system that was removed - a UCP-Native profile claiming a mode it does not implement. |
| [#180](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/180) | Money handling: remove float price parsing and silent currency/timezone fallbacks | [`maoryeh`](https://github.com/maoryeh) | `parseCentsFromDecimal` parses the price string as a `double` and rounds - a float path in a money conversion that feeds a real charge. `("Wix Bookings Business", "America/New_York", "USD")` is silently substituted whenever SiteProperties returns blanks or an invalid value, so a misconfigured merchant can be charged in the wrong currency and quoted slots in the wrong timezone. Both must fail closed. |
| [#181](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/181) | Real catalog pagination | [`maoryeh`](https://github.com/maoryeh) | `ListServicesResponse` always sets `hasMore = false`, `limit` and `cursor` are accepted and ignored, and the downstream Wix search is called with no paging limit. For any merchant with more services than the implicit page size the catalog is silently truncated - for the agent and for registry ingestion alike. |
| [#182](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/182) | Validation hardening on the booking path | [`maoryeh`](https://github.com/maoryeh) | The slot id is an unsigned, unencrypted Base64 JSON blob parsed by hand-rolled substring matching, so a caller can mint a slot id for any service, time or staff member and the only backstop is whatever Wix happens to reject. `party_size` has no upper bound and is never checked against slot capacity. The request's `service_id` is silently overridden by the decoded slot's. `validateConfirmAmount` **fails open** - it returns "valid" when the booking or service cannot be read, or on any exception - so a transient downstream blip disables the pre-charge price check rather than blocking the charge. |

### 4.5 Track E - UCP checkout (`acp-checkout`)

| # | Title | Assignee | Production implication if omitted |
|---|---|---|---|
| [#183](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/183) | Capability intersection, protocol version validation and the negotiated `ucp` envelope on every response | [`maoryeh`](https://github.com/maoryeh) | No request-driven negotiation exists: the version is stamped from the constant `"2026-04-08"`, capabilities come from a static map, and the requested version is never read. The per-checkout envelope advertises only the shopping capabilities - the USP capabilities are never echoed, even on a booking checkout - and error responses carry no `ucp` envelope at all. UCP and USP §8.3/§8.4 both make intersection, version validation and per-response negotiated envelopes MUST-level. Without it, neither side can safely ship a second version, and `capabilities_incompatible` can never be returned. |
| [#184](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/184) | Automatic compensation for post-charge failures | [`maoryeh`](https://github.com/maoryeh) | All three post-charge failure classes - `payment_captured_booking_unconfirmed`, `payment_captured_completion_failed`, `ChargeFailedAfterCompletion` - are documented in the code as requiring manual intervention, and nothing calls a refund or void anywhere in the module. **This is the worst failure mode in the system:** the buyer is charged, no booking exists, and the only remedy is a human noticing a log line. Needs automatic refund/void plus a reconciliation job over the captured-but-unconfirmed set. |
| [#185](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/185) | Emit `available_instruments` and enforce `handler_id` equality | [`maoryeh`](https://github.com/maoryeh) | The `PaymentHandler` proto has **no `available_instruments` field** and nothing emits one, yet USP §7.4 makes checkout-time `available_instruments` authoritative over the profile and requires `complete_checkout`'s `payment.instruments[].handler_id` to equal the checkout handler instance id. The agent therefore cannot determine which instruments are usable at payment time, and the merchant advertises a `paid_bookings` extension it does not fully implement. |
| [#186](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/186) | Verified legal `links`; suppress the zero fulfillment total for bookings | [`maoryeh`](https://github.com/maoryeh) | `privacy_policy` and `terms_of_service` are constructed by convention as `{origin}/privacy-policy` and `{origin}/terms-of-service` and are never verified to exist, so on most real merchant sites the links a buyer is shown at checkout will 404 - a compliance defect on a live payment surface. `totals` also always emits a `fulfillment` entry, including `0` for a booking with no shipping. Complements [#155](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/155). |
| [#187](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/187) | Correct status and error semantics on the money path | [`maoryeh`](https://github.com/maoryeh) | Empty `payment_handlers` forces the checkout status to `REQUIRES_ESCALATION`, so a transient toggle or Stripe-resolution hiccup - both of which fail open to an empty map - silently degrades a bookable checkout into "escalation required" instead of reporting a payment problem. A deliberate policy rejection (USP toggle off) returns gRPC `UNIMPLEMENTED`, which is absent from the mapping table and surfaces as **HTTP 500**, so expected policy outcomes pollute error monitoring. The `messages[].type` taxonomy is also inconsistent across the money path (`payment_declined` is typed `system`, post-charge failures `error`). |
| [#188](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/188) | Idempotency on `update_checkout` and `cancel_checkout` | [`maoryeh`](https://github.com/maoryeh) | Both read no idempotency key despite the proto documenting one on update, and `cancel_checkout` releases the booking before deleting the checkout - if `deleteCheckout` fails the booking is released while the checkout survives, so the buyer's slot is gone but the checkout still looks live. `complete_checkout` is covered by [#86](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/86). |

### 4.6 Conformance, docs and operations

| # | Title | Assignee | Production implication if omitted |
|---|---|---|---|
| [#189](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/189) | Trusted-UI / human-confirmation conformance for agent-driven completion | [`yahalomran`](https://github.com/yahalomran) | UCP platform guidelines require checkout finalization through a trusted, deterministic UI unless AP2 mandates apply, and the v1 flow is fully agent-driven. In practice the Stripe Link spend-approval page *is* that trusted surface, but this is nowhere documented, and the gates that route through it can be bypassed by `LINKUSP_UCP_TEST_SPT` and `--fake-payload` (removed by [#159](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/159)). Without a written position and a bypass-free build, agent-initiated completion has no defensible authorization story when a buyer disputes a charge. |
| [#190](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/190) | v2 conformance checklist and recorded deviations | [`yahalomran`](https://github.com/yahalomran) | USP §9.1.5 lists webhook signing as a REST-binding MUST and §10.1.1 makes RFC 9421 webhook signing mandatory for all modes. v2 deliberately ships without webhooks. That has to be an explicit, reviewed conformance deviation with an owner and a target version, not a silent omission - otherwise "USP-conformant" is a claim nobody can substantiate. Same for holds, deposits and MCP. |
| [#191](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/191) | Money-path incident runbook and reconciliation tooling | [`maoryeh`](https://github.com/maoryeh) | Until [#184](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/184) automation is proven, and permanently as an operational backstop, on-call needs a query to enumerate captured-but-unconfirmed charges, a documented manual refund procedure, and an escalation path. A production payment system without a reconciliation procedure has an unbounded worst case. |

---

## 5. Ordering constraints

No calendar schedule is kept here - target dates changed faster than the plan could track them, and
a stale timetable is worse than none. What actually constrains ordering is dependencies, and there
are only a handful that matter:

| Constraint | Why |
|---|---|
| **[#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157) + [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162) must land together with the shipped client** | `linkusp-cli` already enforces `platform_key_pop` with posture `required` by default, so it **refuses privileged calls against a business publishing no `authorization` policy**. Until `usp-impl` publishes the policy and verifies proofs, the shipped client cannot transact. This is a mutual release gate in both directions, not a one-way dependency. |
| [#114](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/114) **before** [#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157) validation | The hosted platform profile must be fetchable before any server starts validating `UCP-Agent` / `USP-Agent`, or every agent call fails on the day validation turns on. |
| [#168](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/168) (Delete) **before** [#169](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/169), #206, #207 | Admission gating, opt-out eviction and non-indexed exclusion all need a working removal path. There is no way to evict from the index today. |
| [#156](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/156) + [#205](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/205) **before** launch | Both are cheap now and expensive later: a namespace rename and a repo move are breaking once identifiers and profiles are cached in the field. Decided for v2 ([§6](#6-launch-gates-and-honest-risk-assessment)). |
| [#163](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/163) (stable key) **with** [#86](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/86) (server guard) | Server-side dedupe cannot work while the client mints a new `Idempotency-Key` per retry. Either half alone leaves the double-charge open. |

[#158](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/158) (timeouts/retries), [#159](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/159) (log hygiene) and [#160](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/160) (metrics/correlation id) are cross-cutting:
each lands per component alongside that component's other work, and is verified end to end once.

---

## 6. Launch gates and honest risk assessment

The launch-blocking set below is large, and the two genuinely hard clusters are
[#126](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/126) / the registry issues #168-#176
(registry productionization) and [#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157) / [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162) (`platform_key_pop` verification and booking
authorization across three services). Read this as **a launch-blocking set with a named tail**, and
size the pilot to the set that is actually done.

### Launch-blocking (no production traffic without these)

Money correctness: [#86](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/86),
[#163](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/163), [#164](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/164), [#184](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/184), [#177](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/177), [#47](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/47).
Security and privacy: [#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157), **[#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162)**, [#159](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/159),
[#144](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/144),
[#114](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/114)
(✅ [#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134) client half
already done; the server half is [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162)).
Admission: [#141](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/141), [#169](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/169), [#168](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/168).
Legal / compliance: [#197](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/197)
(notice + opt-out commitment), [#206](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/206)
(opt-out enforced), [#207](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/207)
(non-indexed excluded). Exposing merchants without these is a legal exposure, not a product gap.
Correctness of the wire contract: [#201](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/201)
- schema drift already silently disabled §5.6 conditional writes once, and the current sweep cannot
catch a recurrence.
Operability: [#160](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/160), [#172](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/172), [#191](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/191).

Identity linking ([#119](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/119))
is **not** launch-blocking for UCP-Native + Link agents unless member semantics are required.
Email match and Link-token piggyback are **not** acceptable substitutes for [#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157) or [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162).

### Necessary but survivable in a limited pilot

[#170](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/170), [#173](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/173), [#174](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/174), [#175](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/175), [#181](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/181), [#165](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/165), [#161](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/161), [#128](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/128),
[#132](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/132) - all of these
scale with merchant and buyer volume rather than gating correctness.

### If work slips, cut population, not safety

The right lever is the size of the merchant allowlist and the buyer cohort, not the security or
money-correctness set. A pilot over a few hundred explicitly allowlisted Stripe-connected merchants
defers [#174](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/174), [#173](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/173) and [#170](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/170) without deferring a single item that protects a buyer's money. Note
that the legal set (#197 / #206 / #207) does **not** shrink with the pilot: a smaller cohort still
has to have been notified, and still must not include an opted-out or non-indexed merchant.

### Previously open decisions - now resolved

The plan's earlier "open decisions needed from the owner" list is closed. Recorded here so the
resolutions are not re-litigated:

| Decision | Resolution |
|---|---|
| [#9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9) auth mechanism | **`platform_key_pop`** + sender-constrained `booking_scoped_credential`, spec'd in §10.1.6, landed in USP `2026-08-14`; client half shipped. See [§1a](#1a-identity-authentication-and-authorization-clarifications). |
| [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162) mechanism | Decided by the above: booking-scoped credential issued at create with `cnf.jkt`. Platform auth alone is not sufficient. |
| [#40](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/40) service address | **In v2.** Which remedy (structured field vs excluding home-service verticals) is [`maoryeh`](https://github.com/maoryeh)'s implementation choice, recorded explicitly when made. |
| [#125](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/125) LPOS scope | **Closed, out of the design** - there is no concept of "onboarding to the USP agent". Removed from this plan. |
| [#156](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/156) namespace migration | **Do it in v2.** v2 is the first production version, so there is nothing live to break; the migration is only expensive after launch. |

---

## 7. Labelling actions

Applied 2026-08-05, with a reconciliation pass on **2026-08-15**.

### Original labelling (2026-08-05)

| Action | Issues |
|---|---|
| Add `v2` | 9, 40, 42, 47, 54, 59, 75, 86, 108, 114, 118, 123, 124, 125, 126, 128, 132, 134, 136, 141, 143, 144, 149, 155, 156 |
| Add `v>2` | 17, 26, 44, 46, 49, 51, 52, 55, 58, 68, 91, 92, 93, 94, 102, 103, 106, 111, 112, 115, 116, 119, 120, 121, 122, 127, 133, 135, 139, 147 |
| Add `requires-approval` | 9, 40, 44, 94, 102, 114, 118, 119, 120, 121, 122, 125, 126, 127, 128, 134, 141, 144, 147, 156 |
| Create + label `v2` | the 35 issues in [section 4](#4-step-2---mandatory-issues-created-for-this-plan), i.e. #157-#191 |

### Reconciliation (2026-08-15)

| Action | Issue | Reason |
|---|---|---|
| ✅ Closed, completed - **kept** in plan | 42, 134 | Work done. #134's retained credential is the client half of [#162](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/162). |
| Closed, **removed** from plan; `v2` dropped | [#125](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/125) | No longer relevant to the design - there is no "onboarding to the USP agent". |
| Closed as duplicate; `v2` removed | [#196](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/196) | Duplicate of [#132](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/132) (PyPI distribution). |
| Closed as duplicate; `v2` removed | [#204](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/204) | Registry write authz folded into [#126](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/126) §5.4a. |
| Re-scoped; `v2` → `v>2`, **removed** from plan | [#124](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/124) | Platform-profile content is #114; vault content is the closed #125; the v2-relevant remainder (demo/production boundary) is [#136](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/136). What is left is **Standalone-mode** config, out of v2 scope. Rewritten as per-repo/owner AC checklists. |
| Folded into #157; **not** a separate plan item | [#203](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/203) | `usp-impl` `platform_key_pop` verification. #157 ([#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157)) now carries every criterion verbatim. ⚠️ Still carries a `v2` label while closed - harmless, but strip it if the label is used to scope reporting. |
| **Added** to plan (already `v2`) | [#197](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/197), [#201](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/201), [#205](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/205) | Labelled `v2` after the plan was written. See [§3.2a](#32a-added-after-the-2026-08-05-plan-new-v2-issues). |
| **Created** + `v2`, assigned `maoryeh` | [#206](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/206), [#207](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/207) | Engineering halves split out of #197 items 1 and 2; #197 keeps the legal/product side under `yahalomran`. |

**⚠️ Not yet split into issues:** #197 **item 3** (booking-experience parity - price/currency/tax
parity, merchant policy-consent and required-checkbox flow, service-specific gates such as age or
geographic eligibility, click-to-cancel for recurring services, and accessible authorization-evidence
/ audit trail from Link) is substantial engineering work still sitting inside a legal issue. It needs
an owner decision on how to break it up before it can be scheduled or gated.

Existing `v1` / `v>1` labels are preserved; v2 labels are additive.
