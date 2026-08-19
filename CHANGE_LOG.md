# Change Log

## 19/08/26 at 19:00:14 by [Ran Yahalom](mailto:ranya@wix.com)

- Pinned every GitHub Actions `uses:` in `pages.yml`, `ci.yml`, and `mirror-to-public.yml` to full-length commit SHAs (checkout v4.4.0, setup-python v5.6.0, upload-pages-artifact v3.0.1, deploy-pages v4.0.5), because Wix org policy now requires SHA pins and tag-style refs such as `@v4` fail that check
- Updated `docs/website-deployment.md` and comments in `scripts/publish-pages.sh` so they describe auto-publish via `.github/workflows/pages.yml` when Pages Source is GitHub Actions, and treat `npm run publish:pages` as fallback only, because Actions is enabled and a branch deploy fights the workflow once that source is live

---

## 18/08/26 at 17:17:41 by [Ran Yahalom](mailto:ranya@wix.com)

- Published the MkDocs site to a new `gh-pages` branch and pointed GitHub Pages at it (branch source, `/ (root)`), so the website is live at <https://wix.github.io/universal-scheduling-protocol/>. GitHub Actions is disabled for this repository by the organisation, so `.github/workflows/pages.yml` cannot run; serving pre-built HTML with a `.nojekyll` marker publishes the site without waiting for an org policy change
- Added `scripts/publish-pages.sh` and the `publish:pages` npm script wrapping `mkdocs gh-deploy`, because with no workflow available the build-and-publish step has to be run deliberately and should be one reproducible command rather than remembered flags
- Documented the hosting model in `docs/website-deployment.md`, including how to switch to the existing `pages.yml` workflow once Actions is enabled, and the `CNAME`-in-`site-docs/` requirement so a future custom domain survives the branch overwrite that each publish performs
- Removed the root `PLAN.md`, an internal multitask planning artifact that described private repository permissions and organisation ruleset details and should never have been visible in a public repository

---

## 15/08/26 at 21:07:15 by [Ran Yahalom](mailto:ranya@wix.com)

- Reconciled `plans/V2_PRODUCTION_PLAN.md` against the current GitHub issue set, the landed USP `2026-08-14` specification and the `linkusp-cli` agent. The plan was written 2026-08-05 and had drifted far enough that it described decisions as pending that had already been made and listed issues that no longer exist in v2 - a plan that misreports the state of the work is worse than no plan, because the launch-blocking set is read off it
- Rewrote §1a and the V2-X1 / V2-X6 entries around the **landed `platform_key_pop` design** (§10.1.6, PR #200) instead of framing [#9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9) as an open decision. Added the two authority tiers (`privileged_platform` / `privileged_scoped`), the ephemeral-key proof-of-possession model, `cnf.jkt`-bound `booking_scoped_credential`s, and `config.authorization` policy publication. Recorded the sequencing consequence that matters operationally: the shipped client enforces `required` by default and so **refuses privileged calls against a business publishing no policy**, making client and server a mutual release gate
- Marked [#42](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/42) and [#134](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/134) as completed and kept them in the plan, since they were closed as *fixed*; noted that #134's retained credential is the client half of V2-X6, so the server half is still outstanding rather than the whole item being done
- Removed [#125](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/125) (closed - no concept of "onboarding to the USP agent" in the current design) and [#196](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/196) (closed as duplicate of #132) from the plan, and stripped the stale `v2` labels from #196 and [#204](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/204) so label-scoped reporting stops counting work that is tracked elsewhere
- Re-scoped [#124](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/124) on GitHub and dropped it from the plan: its platform-profile content duplicated #114 and was stale under the now-keyless profile model, its vault content died with #125, and its v2-relevant remainder is #136. Rewrote the body as per-repo/owner AC checklists covering only Standalone mode and moved the label `v2` → `v>2`, because v2 is UCP-Native only
- Integrated the `v2` issues added after the plan was written ([#197](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/197), [#201](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/201), [#205](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/205)) into a new §3.2a, and added #201 to the launch-blocking set - hand-written models silently dropped `Booking.revision` and disabled §5.6 conditional writes end to end, and the name-only conformance sweep cannot catch a recurrence
- Split the engineering halves out of the legal issue #197 into [#206](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/206) (honor merchant opt-out across admission, eviction and serving) and [#207](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/207) (exclude non-indexed provider sites, opt-in only, failing closed), both assigned to the registry owner. An opt-out that nothing enforces is not an opt-out, and the non-indexed rule needs the *inverse* default from the ordinary gate. Flagged #197 item 3 (booking-experience parity) as substantial engineering still sitting unsplit inside a legal issue
- Replaced the two-week schedule with a **dependency-ordering** section and deleted the "open decisions needed from the owner" block, recording each resolution instead. Dates churned faster than the plan could track, and every listed decision is now made: auth mechanism, V2-X6 mechanism, #40 (in v2, remedy chosen at implementation time), #125 (closed) and #156 (do the namespace migration in v2, while nothing is live to break)
- Updated the derived sections for consistency - table of contents, issue counts, §7 labelling actions with a full reconciliation table - and verified every internal anchor still resolves
- Removed the plan-local `V2-*` identifier scheme entirely, replacing every occurrence with a hyperlinked GitHub issue number, and deleted Appendix A which existed only to map between the two. Carrying two identifiers for the same item made the plan hard to read and meant every cross-reference had to be resolved through a lookup table
- Added an **Assignee** column to every per-issue table in sections 3 and 4, populated from the **live GitHub assignees** rather than the track-owner defaults the plan previously assumed. These had diverged: the registry issues (#168-#176, #149) are assigned to `danieljaffe1`, not the track owner named in §2, and several cross-cutting issues have two assignees. The grouped mandated-exclusions table is left without the column because its rows cover multiple issues at once

---

## 15/08/26 at 09:24:11 by [Ran Yahalom](mailto:ranya@wix.com)

- Switched `.github/workflows/ci.yml` to `runs-on: self-hosted`. GitHub-hosted runners are not permitted in this organisation, and `devex-gha-authority` does not merely warn - it **cancels the job**, which is why the `check` run on [#200](https://github.com/wix-private/universal-scheduling-protocol-spec/pull/200) reported a failure after one second without executing a single step. The validation tooling itself was never broken
- Avoided naming the forbidden runner label even in the explanatory comment, in case the policy check greps the workflow file rather than parsing it - otherwise the comment explaining the rule would trip the rule
- Narrowed the `push` trigger to `master`. Listening to both `push` and `pull_request` unqualified ran the whole job twice for every commit on a PR branch, which is what produced the two separate `ci` entries in the checks list

---

## 15/08/26 at 06:47:19 by [Ran Yahalom](mailto:ranya@wix.com)

- Added an optional opaque `revision` to `Booking` and `WaitlistEntry`, closing a gap the proof-of-possession work assumed was already filled: a booking `revision` did not exist anywhere in the repository, and neither did `ETag`, `If-Match`, or any other conditional-request machinery. A `booking_scoped_credential` authorizes a *resource* rather than a session and MAY be re-issued to the same key, so two agents - or one agent on two devices - can legitimately hold a valid credential for the same booking. Without a concurrency control the second write silently overwrote the first and **neither caller learned anything was lost**
- Specified conditional writes in a new §5.6 and carried the precondition the same way idempotency is already carried: `If-Match` on REST, `_meta.usp.if_match` on MCP - mirroring the existing `Idempotency-Key` / `_meta.usp.idempotency_key` pair rather than inventing a second convention for the same problem
- Chose `412 Precondition Failed` over reusing `409`, and said why in the text: `409` is already bound in this specification to idempotency-key conflicts, and collapsing the two would leave a platform unable to distinguish "your key was reused with different parameters" from "someone else edited this booking" - two failures with different remedies
- **Pinned the `Idempotency-Key` x `If-Match` ordering as a MUST**, which is a genuine correctness hole rather than a detail: an idempotent replay returns the stored response *without* re-evaluating the precondition. The caller's revision was current when the original request succeeded and that request changed it, so re-checking on replay would reject a call that had already been applied - converting a merely dropped response into a permanent failure
- Made `revision` **optional**, so the change is non-breaking and needs no version bump: adding a required response member would make every existing business non-conformant. Its presence in a response is itself the advertisement that conditional writes are supported, which is exactly the contract of an absent HTTP `ETag`, so no capability flag was invented for it
- Required the value to be opaque and to change on every modification, and warned against deriving it from `updated_at` alone - two modifications inside one timestamp tick produce the same value and defeat the check silently
- Scoped this to **bookings and waitlist entries**, the same pair §10.1.6 requires per-resource authorization for, and excluded holds deliberately: a hold has no update operation, only release, and releasing an already-released hold is idempotent, so there is no lost update to prevent. Because `usp_availability_release` shares the MCP metadata wrapper that now carries `if_match`, the field's description states that a business **MUST** ignore it there rather than leaving the ambiguity unaddressed
- Documented `revision` in the §5.2 and waitlist **field tables**, not only in the schemas. A member that exists only in `schemas/` is precisely the defect just corrected in §8.2.3, where §9.1.4 pointed at a field table that documented nothing
- Recorded that `_meta.usp.if_match` falls **inside** the `usp_p` proof digest, which strips only `_meta.usp.authorization`, so on MCP the precondition is tamper-evident against an intermediary while the REST `If-Match` header is not - the same asymmetry that already applies to method arguments
- Noted in §9.4 that allocating `-32002` **exhausts the USP JSON-RPC range**: `-32001` through `-32009` are now all assigned, and a future protocol error needs either a new range or a `data.code` discriminator, which is already the established pattern for the signature and proof-of-possession codes

---

## 15/08/26 at 05:08:33 by [Ran Yahalom](mailto:ranya@wix.com)

- Corrected `site-docs/deployment-modes/ucp-native.md`, which told UCP-Native implementers the **opposite of the specification** and is the highest-impact item here: its reading guidance listed only "Skip Sections 9.6 and 10.2" and omitted the entire "do not skip §10.1.6" carve-out, so a business following the published docs would have skipped the section that makes privileged-operation authentication mandatory. Also refreshed the stale Authentication row, which still read "UCP OAuth 2.0 support" after the specification broadened it to "UCP OAuth 2.0 / signature support"
- Fixed `docs/ucp-native-demo-merchant-profile.example.json`, which violated the rule it exists to demonstrate: `signing_keys` sat at the document root as a **top-level sibling of `ucp`** in a UCP profile - exactly what §10.1.6 forbids USP from doing. Moved it under `ucp` as the UCP-canonical `keys` with the transition alias dual-published, and added the `config.authorization` policy the binding had entirely lacked. This file is what implementers copy, so a defect here propagates
- Refreshed **133 stale `2026-02-09` example literals** across the specification, site docs, the OpenAPI examples, and the demo profile, while preserving the **7** that name a specific historical version on purpose - the `supported_versions` map, the `dev.usp.services.booking@2026-02-09` pin illustrating pin syntax, and the roadmap history rows. The distinction is made by matching what a line *says*, not by counting occurrences
- Added the missing `usp_services_lookup` row to the §9.2.1 method-mapping table, which listed 26 rows for 27 methods. The method is normative in REST and present in the MCP binding, so the omission made the table quietly wrong rather than merely incomplete
- Deleted the duplicated link-definition block at the end of the specification. Every reference definition appeared twice; the second copy is now removed
- Replaced the inline `POST /registry/businesses` request body in `openapi/usp-rest.json` with a thin `$ref` to `schemas/registry.json` `$defs/RegistrationRequest`, the duplication [CLAUDE.md](CLAUDE.md) rule 3 forbids. The two copies were verified byte-equivalent first, so this deduplicates before they drift rather than after
- Added the `requires` object to `schemas/paid_bookings.json`, which §1 says extension schemas **SHOULD** declare
- Fixed six pre-existing broken internal anchors, each resolved by locating the section whose heading actually matches rather than by guessing from the section number - `#1123-paid-bookings` pointed at a calendar schema section, and `#92-error-handling` pointed at the MCP binding rather than the error-code mapping. One, `#category-rules`, referenced a bold run-in paragraph that is not a heading at all and now reads as plain text
- Added an anchor check to `tools/usp_check.py`, so a link to a non-existent section fails the build instead of reading as a working cross-reference that goes nowhere
- **`tools/known-issues.txt` is now empty.** Every failure the validator found when it was introduced has been fixed rather than tolerated, which was the acceptance criterion for this commit

---

## 15/08/26 at 04:31:52 by [Ran Yahalom](mailto:ranya@wix.com)

- Added ten test vectors under `tests/vectors/pop/` covering canonicalization, issuance, presentation, and six rejection cases. `platform_key_pop` is specified on both bindings and implemented on neither, so without these the normative text ships entirely unvalidated - and canonicalization is the one part of it that can be wrong in a way review will not catch, because two implementers can read the same rule and encode it differently
- Signed the proof vectors with **real Ed25519 keys** derived from fixed seeds rather than publishing placeholders, so an independent implementation can verify them instead of taking them on trust. The private keys are in the repository deliberately, documented as test-only, precisely so the vectors are reproducible byte-for-byte
- Made `006-cross-key-replay` the centrepiece and said so in §10.1.6: its proof **verifies correctly against its own header key**, so an implementation that checks the signature and stops will accept it. Only comparing the thumbprint against the recorded `cnf.jkt` rejects it. That is the test the superseded profile-URI binding would have failed, and it is the difference between this mechanism and a bearer token wearing a proof
- Extended `tools/usp_check.py` to verify the vectors rather than merely parse them: it recomputes every JCS serialization and `usp_p` digest, verifies each signature against the JWK in its own proof header, recomputes each published thumbprint, checks `expected_claims` against the signed payload, and asserts that a `pop_key_mismatch` vector genuinely uses a key differing from the credential's `cnf.jkt` - otherwise that vector would pass while testing nothing
- Made the checker fail any vector whose `id` is not cited in `specification.md`, and cited all ten in a §10.1.6 table. Vectors that nothing references are the normal way this kind of artefact rots; this makes prose and vectors fail together instead of drifting apart
- Verified the checker is not vacuously green: tampering with a signature and neutering the cross-key vector each produce the expected failure

---

## 15/08/26 at 04:02:15 by [Ran Yahalom](mailto:ranya@wix.com)

- **BREAKING.** Raised §10.1.6's per-resource authorization requirement from **SHOULD** to **MUST** for privileged operations on an existing booking or waitlist entry. The section deferred this explicitly while the credential's issuance format was unspecified; that format is now specified, so the deferral has expired. Platform authentication alone does not satisfy it, which is the entire point: a business accepting only a platform-level mechanism authorizes any authenticated platform to act on any booking it can identify
- Named the resource types the MUST covers instead of leaving it as "get/cancel/reschedule/PII", because the other two resource families need different answers and an unqualified MUST would have swept them in. Feed subscriptions: **RECOMMENDED** - no buyer personal data, but a subscription ID is still not a credential. Registry registrations: **NOT REQUIRED** - authorized at platform tier against the registering platform's bound principal, since a registry entry has exactly one owner
- Bumped the protocol version from `2026-02-21` to `2026-08-14`, and recorded in the specification itself that this is a **breaking authorization change rather than a clarification**: a business conformant under `2026-02-21` may be non-conformant under this version without changing a line of its own code. Shipping that quietly under the old version number would have removed the only signal an implementer gets
- Restricted the bump to the five places that assert this repository's **version identity** - `specification.md`, `README.md`, both binding `info.version` fields, and a new roadmap row - and deliberately left every literal that names a *specific historical* version alone: the `/.well-known/usp-2026-02-09` `supported_versions` example, the `dev.usp.services.booking@2026-02-09` capability pin illustrating pin syntax, and the roadmap's history rows. Bumping a pin example would teach that pins track the current version, which is the opposite of what a pin is
- Fixed a two-release staleness in passing: both bindings carried `info.version` `2026-02-09` while the specification was at `2026-02-21`, so the bindings had been advertising a superseded version. The `version` assertion added with the CI now makes that class of drift a build failure rather than something found by inspection, and its entry in `tools/known-issues.txt` is now cleared
- Landed this as its own commit, apart from the additive mechanism registration, so the breaking and non-breaking halves of this work can be reviewed - and if necessary reverted - independently

---

## 15/08/26 at 03:38:40 by [Ran Yahalom](mailto:ranya@wix.com)

- Rewrote §10.1.6's identity-binding MUST, which was **unsatisfiable as written** for a permissionless caller. It required a business to confirm the authenticated principal is authorized to act on behalf of the profile in the agent header, but a profile URI is self-asserted, fetched over an unauthenticated GET, and deliberately shared by every instance of a platform - so nothing in the document distinguishes one caller from another. A requirement that cannot be met gets implemented as a string comparison against a caller-supplied header, which authorizes nothing at all; that is exactly the defect this work exists to correct
- Defined what the MUST means instead: the authenticated principal is the **key** (the `jkt` under `platform_key_pop`, the profile-published key under `http_message_signature`, the registered client otherwise), the profile URI carries branding and capabilities and **MUST NOT** be treated as an authentication factor, and the pairing is recorded trust-on-first-use with a later mismatch rejected
- Stated that a key-bound credential satisfies the mechanism-independent identity-binding MUST **on its own**, and that a business **MUST NOT** require a second platform credential on the same request merely to satisfy it. Without that sentence the natural reading forces every scoped call to carry two credentials, which would defeat the point of a per-resource one
- Applied the same reading to the MCP restatement of the rule, and recorded there why `_meta.usp.profile` is deliberately kept inside the `usp_p` digest: the profile a caller asserts is then covered by the proof rather than free to be rewritten in transit
- Made §10.1.6's mechanism table **illustrative rather than exhaustive**. Read strictly, "a business MUST accept at least one of the following" over a five-row table meant a business accepting only a newer mechanism accepted none of them and was non-conformant - contradicting the forward-compatibility rule twenty lines below, which makes the same list an extension point
- Specified credential lifetime and invalidation: `expires_at` tracks the resource rather than a session, invalidation at terminal state is a **MUST**, and re-issuance to the same bound key on an authenticated read is permitted so a long-lived booking survives an expiry without a new create call
- Scoped the word "revocable" honestly: USP defines **no revocation operation on any binding**. Expiry and terminal state are the only invalidation paths, and both are the business's own doing. Saying so plainly is what stops an implementer designing around a protocol facility that does not exist, and it is the reason `expires_at` is REQUIRED rather than optional - expiry is the only bound the protocol itself guarantees

---

## 15/08/26 at 03:14:22 by [Ran Yahalom](mailto:ranya@wix.com)

- Removed `booking_scoped_credential` from `PUT`/`DELETE /registry/businesses/{id}`, where it was offered although no booking exists - contradicting both the scheme's own description and the platform-tier `_meta` wrapper those methods used
- Closed the hole that removal opens, which "platform_key_pop replaces it" does **not** close on its own: `usp_registry_update` and `usp_registry_delete` were `privileged_scoped`, so dropping the credential would have left them with no per-resource authority at all, and raising scoped authorization to a **MUST** would then have made them MUST-scoped methods with nothing to scope against. Both are re-tiered to `privileged_platform` and authorized against the registering platform's bound `jkt`. A registry entry has exactly one owner, so trust-on-first-use ownership is already the model and no new credential type is needed
- Made the re-tier a **paired** edit and asserted it: `x-usp-access`, the `_meta` wrapper `$ref`, the method description, and the `_meta` parameter description all move together. Changing the tier without the parameter description would leave a platform-tier method whose own parameter documentation still recommends a booking-scoped credential. Post-conditions: tiers are 8 public / 8 platform / 11 scoped, boilerplate counts are 8/11/8/11, and no method is left half-swapped
- **Kept** `booking_scoped_credential` on the four REST feed-subscription operations rather than removing it alongside the registry ones. Feed subscriptions are a third resource family, neither booking nor waitlist, and a subscription ID is exactly the "a resource identifier is not a credential" case §10.1.6 opens by warning about - dropping the per-resource mechanism there would have made the specification weaker, and scoping the forthcoming MUST to booking and waitlist would have silently orphaned them. The credential's description now names all three families explicitly, and states that registry registrations are deliberately not among them
- Recorded the REST/MCP asymmetry rather than leaving it to look like an omission: MCP exposes no subscription-lifecycle methods at all, so those four operations exist only on REST. Requirement count for the credential moves from 17 to 15, with all four subscription operations intact
- Fixed the §9.2.2 prose tier lists, the only place the tiers are written out in English and therefore the easiest place for them to drift out of agreement with `x-usp-access`

---

## 15/08/26 at 02:51:07 by [Ran Yahalom](mailto:ranya@wix.com)

- Added five proof-of-possession error codes - `pop_proof_missing`, `pop_proof_invalid`, `pop_key_mismatch`, `pop_proof_replayed`, `proof_nonce_required` - to the §10.1.1 table and the OpenRPC `USPProtocolError` enum, and retitled that table to cover proof verification as well as signatures. Distinguishable codes matter more here than usual: wrong key, replayed proof, and missing proof are three different caller mistakes with three different fixes, and collapsing them into one 401 leaves a platform unable to tell a bug from an attack
- Allocated **one** new JSON-RPC code, `pop_proof_required` = `-32001`, rather than one per failure mode. The USP range `-32003`…`-32009` is fully consumed and only `-32001` and `-32002` remain, so spending both would have exhausted the range for a single feature. The fine-grained codes ride in `data.code` and the Problem Details `type`, which is exactly how the six existing `signature_*` codes already work - they appear in the OpenRPC enum and in no §9.4 row at all. `-32002` is left free
- Broadened `signature_missing` / `signature_invalid` / `signature_expired` to cover proofs as well as RFC 9421 signatures, and added a `data.mechanism` discriminator. Without it those codes became ambiguous the moment two mechanisms could produce them, leaving a caller unable to tell which credential to correct
- Added `data.nonce`, carried on `proof_nonce_required`. `USPProtocolError.data` was already an open object requiring only `code` and `content`, so this is one declared property rather than a structural change. The asymmetry is deliberate - a business **MAY** require nonces while a platform **MUST** support being challenged - which lets a business turn nonces on unilaterally without a flag day
- Mirrored the codes into `openapi/usp-rest.json`'s 401 prose and added three worked Problem Details examples, including the cross-key case, so the response shape is discoverable from the binding rather than only from the specification body

---

## 15/08/26 at 02:26:18 by [Ran Yahalom](mailto:ranya@wix.com)

- Fixed a latent defect that made the paid-bookings extension **inert**: `schemas/paid_bookings.json` declared `$defs/dev.ucp.shopping.checkout` - the object contributing `booking` to a UCP checkout - but the root `allOf` never referenced it, so the extension was applied to nothing and an instance with a missing or misshapen `booking` validated silently. This is a pre-existing bug, fixed here rather than deferred to the hygiene commit because the UCP-Native credential carriage is unimplementable without it: adding a property to an object nothing composes would have looked correct and validated nothing
- Added `booking_scoped_credential` to that extension object as a **sibling of `booking`**, settling where the credential rides in UCP-Native paid bookings. Not inside `booking`: `BookingContext` is scheduling data that platforms persist and re-display, so a credential placed there would be written to whatever store the booking is cached in - widening precisely the leak surface the `cnf` binding closes
- Recorded in §7.4 why this is not a namespace violation, since the obvious objection is that USP must not add members to a UCP-governed object. It is declared inside USP's own registered `dev.usp.services.paid_bookings` extension, by the same `allOf` composition that already contributes `booking`, so it is a *declared* extension member rather than an invented one and needs no governance rule beyond the one this extension already relies on
- Marked the credential response-only in the schema description - a platform **MUST NOT** send it on a request and a business **MUST** ignore it if received - because a bidirectional-looking field in a checkout object invites a client to echo back what it was given

---

## 15/08/26 at 02:04:53 by [Ran Yahalom](mailto:ranya@wix.com)

- Specified MCP proof carriage in §9.2.2 and wired it into `openrpc/usp-mcp.json`: one new `proof` property on `McpAuthorization`, the claim set, the canonicalization rule, and the credential returned on the three creating methods. The MCP binding previously could not express a mechanism its own advertised `AuthorizationMechanism` set contains, which is the same class of defect this work exists to fix
- Put `proof` **inside** `McpAuthorization` rather than as a sibling `_meta.usp.proof`. All five `_meta.usp` wrappers are `additionalProperties: false`, so the sibling form would have required a structural edit to every one of them; they already `$ref` `McpAuthorization` and needed only description changes. Easy to miss, and missing it would have made the design non-conformant with its own binding file
- Carried the proof in `_meta.usp.authorization.proof` on **both** MCP transports rather than giving MCP-over-HTTP a REST-style `DPoP` header. One client code path, and a business behind an SSE gateway does not need to know its own externally visible URL in order to verify a proof
- Gave the MCP proof `typ: usp-pop+jwt` rather than `dpop+jwt`, and bound `usp_m`/`aud` in place of `htm`/`htu`. The differing `typ` means a REST proof and an MCP proof cannot be replayed as one another, and a verifier rejects the mismatch before evaluating any claim
- Made `aud` **mandatory**. Without `htu` to bind the target, and with neither `ath` nor a credential present at issuance, a proof captured by one business would otherwise replay verbatim at a different business. `aud` is always available to the caller because a conformant business is discovered through its profile URI in the first place
- Specified the argument digest over **JCS-canonicalized** params rather than byte-exactly, because an MCP client does not control its own wire bytes - the SDK serializes `params` and gateways re-serialize freely. Removed only `_meta.usp.authorization` from the digest, deliberately leaving `_meta.usp.profile` and `_meta.usp.idempotency_key` inside it: the first gives identity binding something to bind against, the second covers create-replay for free
- Rewrote the four privileged wrapper descriptions, which actively **forbade** what this design requires. `McpUspMetaPrivilegedPlatform` stated that `booking_scoped_credential` "does not apply until a booking or waitlist entry exists" without saying that this is the tier at which one is *issued*, and the `authorization` property on all four recommended a retained credential with no mention of the proof its `cnf` binding requires
- Recorded, in `McpAuthorization.proof` itself, why the mandatory-proof rule is stated as policy rather than left to syntax: `mechanism` is caller-asserted and excluded from the digest, so without the rule an attacker holding a leaked credential could declare `mechanism: booking_scoped_credential`, omit `proof`, and present a sender-constrained credential as a bearer token
- Added two §9.2.4 conformance items and deliberately did **not** restate the existing MUSTs on profile binding and mechanism selection, which already cover their ground

---

## 15/08/26 at 01:29:11 by [Ran Yahalom](mailto:ranya@wix.com)

- Wired the REST carriage of `platform_key_pop`: the proof rides the `DPoP` request header, the credential rides `Authorization: DPoP <bsc_...>`, and `booking_scoped_credential` is now returned on the `POST /bookings`, `POST /availability/holds` and `POST /waitlist` creation responses. The credential was previously *consumable* by 17 operations and *issued* by none - the security scheme depended on a value no response in the document ever returned
- Modelled `PlatformKeyPop` as `apiKey` in the `DPoP` header rather than as `http`/`DPoP`, correcting the entry added when the mechanism was registered. On a resource-creating call there is **no `Authorization` header at all** and the proof header is itself the credential, so an `http` scheme would have misdescribed the wire form at exactly the point where the binding is established
- Moved `BookingScopedCredential` from `apiKey`/`Authorization` to `http`/`DPoP`. This resolves the three-way collision in which `BookingScopedCredential`, `ApiKey` and `OAuth2Bearer` all resolved to `Authorization: Bearer`, leaving a server unable to tell from the request alone which scheme the caller intended; the pre-existing `OAuth2Bearer`/`ApiKey` overlap remains and is out of scope. More importantly the scheme change is what stops a business silently accepting a sender-constrained credential as a plain bearer token
- Expressed the credential-plus-proof requirement as a **single security requirement object naming both schemes**, which is OpenAPI's AND semantics and therefore an accurate machine-readable statement of the anti-downgrade rule. Kept the credential-alone alternative, because OpenAPI cannot express "only when `cnf` is present" and unbound legacy credentials still exist; the conditional MUST stays in §10.1.6 and is stated in the scheme description so a reader of the binding alone does not conclude the bearer path is sanctioned
- Added `PlatformKeyPop` as an accepted alternative on all 23 privileged operations (6 platform-tier, 17 scoped), rather than only on the scoped ones. A create call is where the key binding is established, so omitting it there would have left the mechanism advertised but unreachable at issuance
- Described the credential on the creation responses as returned *beside* the created resource and never inside it, and said why: a platform that persists the credential into the booking it re-displays has widened exactly the leak surface the `cnf` binding exists to close

---

## 15/08/26 at 00:58:44 by [Ran Yahalom](mailto:ranya@wix.com)

- Specified the `platform_key_pop` mechanism normatively in §10.1.6: key generation and `jkt` as the platform identifier, in-band binding at issuance, the REST and MCP presentation forms side by side, accepted algorithms, downgrade resistance, the verification order, and replay defence. Until now the section reserved a mechanism name and defined nothing, so two implementers building it would have built two incompatible things
- Stated the **anti-downgrade MUST for both bindings**, which is the single load-bearing rule of the design. Syntax enforces it on neither binding by itself: REST's `Bearer` -> `DPoP` scheme change makes a downgrade visible but is not a rule, and MCP has no scheme at all while the declared `mechanism` sits inside `_meta.usp.authorization`, outside the argument digest. Without the rule, an attacker holding a leaked credential could declare `mechanism: booking_scoped_credential`, omit the proof, and present it as a bearer - the whole mechanism bypassable in one field
- Made the verification order normative and explained why the order is load-bearing rather than stylistic: each step returns a different code, so reordering leaks which part of the presentation was wrong. Recorded that at issuance the credential steps and `ath` are skipped and the thumbprint is *recorded* rather than compared, which is the one place the two flows genuinely differ
- Required replay defence on **reads as well as writes**. Idempotency-key de-duplication is only a **SHOULD** and only covers state-modifying operations, so read operations had no replay protection at all - and those are exactly the operations returning buyer personal data
- Added the forward-compatibility carve-out, without which the closed `cnf` and credential objects added earlier would contradict §10.1.6's ignore-what-you-do-not-recognize MUST. The two rules point in opposite directions deliberately: ignoring an unknown profile field costs a capability, whereas ignoring an unknown confirmation method downgrades a sender-constrained credential to a bearer token
- Chose EdDSA as the algorithm floor rather than ES256, to avoid the fixed-width `r||s` versus DER encoding trap that §9.1.4 already has to warn about; `ES256` remains permitted in addition. Also required rejecting `alg: none` and any header JWK carrying a private-key member
- Documented the three root-level platform-profile members - `keys`, `signing_keys`, `webhook_url` - in the §8.2.3 field table. They existed only in `schemas/profile.json`, and §9.1.4 pointed at §8.2.3 for the `keys` array, a reference that led nowhere. Placed them in a **second table** described as siblings of `usp`, because folding them into the existing table would have asserted `usp.keys` and contradicted the schema
- Stated explicitly that a non-signing platform publishing no `keys` is conformant, and quoted **both halves** of the schema's condition. An implementer reading only the first half would conclude that MCP-over-HTTP forces keys; since a proof rides in-band rather than as RFC 9421 headers, the keyless profile is conformant on both bindings, and that is what lets one shared profile serve every instance of a personal agent
- Recorded what the mechanism does *not* defend against - theft of local key material, or a hostile process on the platform host - rather than leaving the proof-of-possession framing to imply more than it delivers

---

## 15/08/26 at 00:21:37 by [Ran Yahalom](mailto:ranya@wix.com)

- Registered the `platform_key_pop` mechanism identifier across all **six** artefacts that duplicate the mechanism set by design: `schemas/profile.json` (`AuthorizationMechanism` examples and description, plus `accepted_mechanisms`), `openapi/usp-rest.json` `components.securitySchemes`, `openrpc/usp-mcp.json` `components.x-usp-securitySchemes`, the §10.1.6 mechanism table, `site-docs/security.md`, and the per-method boilerplate in the MCP binding. Partial updates are the most likely failure mode here and nothing enforced consistency, so a sweep across all six is part of the acceptance for this work
- Corrected the working assumption that the MCP per-method boilerplate was "~30 occurrences of one string". It is **four distinct strings totalling 38 occurrences across 19 methods**, and the one usually quoted appears only 6 times. A search-and-replace on that single string would have left 32 sites advertising a mechanism set the binding's own security schemes contradict. This entry updates the two strings that *enumerate* mechanisms (6 method descriptions, 6 `_meta` parameter descriptions), asserted by exact count before and after; the other two carry scoped-credential semantics and are updated where the proof requirement lands
- Registered the mechanism differently in each binding, because the two are **not symmetric** and treating them as such would have produced an invalid OpenAPI document: OpenRPC has a USP-specific `x-usp-securitySchemes` whose entries are `{mechanism, description}`, whereas OpenAPI has no such extension and uses standard `components.securitySchemes`, where the entry must be a real OpenAPI scheme (`type: http`, `scheme: DPoP`) carrying the shared identifier in `x-usp-mechanism`
- Retired the sentence "Detailed issuance and validation mechanics are tracked separately (issue #134)" from both places it was duplicated (§10.1.6 and `openapi/usp-rest.json`). It became false the moment the credential acquired a schema, and leaving it would have told implementers to wait for a specification that had already landed
- Added [RFC 7519], [RFC 7638], [RFC 7800] and [RFC 8785] as normative references with link definitions. The mechanism is described in terms of JWK thumbprints, `cnf` semantics, and JSON canonicalization, none of which the document previously cited; only [RFC 9449] and [RFC 7517] were already present
- Recorded in each description that this mechanism *composes with* rather than replaces the rows around it, since the single most likely misreading is that `platform_key_pop` is an alternative to `booking_scoped_credential` rather than the thing that makes it sender-constrained

---

## 14/08/26 at 23:58:12 by [Ran Yahalom](mailto:ranya@wix.com)

- Added `$defs/ConfirmationKey` and `$defs/PopProofJwt` to `schemas/usp.json` and `$defs/BookingScopedCredential` to `schemas/profile.json`. `booking_scoped_credential` has been an advertised mechanism name with **no object definition anywhere in `schemas/`** since it was reserved, so every implementer was free to invent an incompatible shape; §10.1.6 said as much, describing itself as reserving only the name
- Put the credential in `profile.json` rather than `booking.json`, against the obvious placement, for a reason the new `refs` check now proves mechanically: `booking.json`'s `$id` carries a `services/` segment while `usp.json`'s does not, so a relative `cnf` reference written from `booking.json` resolves under `$id` base-URI rules to `https://usp.dev/schemas/services/usp.json`, a document that does not exist. It would have validated in any filesystem-based editor and broken in any `$id`-honouring validator. `profile.json` shares an `$id` level with `usp.json`, so the reference is correct under both. The placement is also the semantically right one - a credential is an authorization object, beside `AuthorizationMechanism` and `AuthorizationPolicy`, not booking domain data
- Tightened the `refs` check to catch that class directly. The existing two-strategy comparison could not: its flat fallback, which same-level references legitimately need, silently absorbed the cross-level failure. It now flags any *relative* `$ref` between schema files whose `$id` directory segments differ, and it fires on a probe reference from `booking.json` while passing on the chosen placement
- Made `cnf` REQUIRED in practice by describing what its absence means rather than by schema alone: a credential without `cnf` is a plain bearer token, so anyone who observes the value in a log, an HTTP trace, or a compromised database can use it. `cnf` is left optional in the schema so that a business may issue an unbound credential and be visibly non-conformant, rather than being unable to express the legacy shape at all
- Required `bsc_` as a value prefix and forbade deriving the value from the resource identifier. The prefix keeps the credential distinguishable from an `oauth2_bearer` token or an `api_key` sharing the `Authorization` header and greppable when a leak has to be scoped; the derivation ban closes the resource-identifier-as-credential mistake that §10.1.6 opens by forbidding
- Documented that `expires_at` tracks the **resource** rather than a short session clock, since a booking made three months out still needs a cancel path on day 89 - the failure mode a naive short-lived-token reading would produce
- Made both closed objects (`additionalProperties: false`) and recorded why in the descriptions: the §10.1.6 forward-compatibility rule that requires consumers to ignore unrecognized members deliberately does **not** extend to credentials or confirmation keys, because ignoring an unrecognized confirmation method downgrades a sender-constrained credential to a bearer token
- Added thin `$ref` entries in both bindings' `components.schemas` per [CLAUDE.md](CLAUDE.md); no inline object trees. Note the OpenAPI name `BookingScopedCredential` now exists in both `securitySchemes` and `schemas`, which OpenAPI namespaces separately - the security scheme is referenced by 17 `security` arrays and was deliberately not renamed

---

## 14/08/26 at 23:34:05 by [Ran Yahalom](mailto:ranya@wix.com)

- Settled where `platform_key_pop` is normatively specified, which the surrounding design had left ambiguous in a way that would have made the mechanism inapplicable to half its audience. §10.2.3 already says businesses **SHOULD** support DPoP for proof-of-possession, but §10.2 is skipped in its entirety by UCP-Native deployments, so a mechanism specified there would not reach the deployments §7.3 explicitly directs to keep reading §10.1.6. The mechanism is therefore specified in §10.1.6, which is mode-agnostic, and §10.2.3 now carries a pointer saying so
- Stated that the two are **distinct rather than one generalizing the other**: §10.2.3's DPoP hardens an already-issued OAuth token, while `platform_key_pop` is permissionless and involves no token at all. Left unstated, an implementer would reasonably read the new mechanism as a restatement of the old sentence and implement only the OAuth-bound form
- Answered the open question of how the credential and proof travel in UCP-Native Mode, by separating two governance models that had been conflated. On USP's own service endpoint USP defines the headers in both modes. On a UCP-governed endpoint USP **MUST NOT** redefine `Authorization`, so the proof rides the additive `DPoP` header and an issued credential is returned inside the `dev.usp.services.paid_bookings` extension as a sibling of `booking` - never at the UCP checkout root, and never inside `booking`, which platforms persist and re-display and so must never hold a secret
- Recorded *why* that is permitted, since the namespace-governance rule alone does not answer it: that rule governs profile documents, whereas response bodies are governed by UCP's extension-composition model, which is already how `dev.usp.services.paid_bookings` contributes `booking` to a checkout. A credential added the same way is a declared extension member rather than an invented one, so no new governance rule is required
- Stated the UCP relationship honestly as an **extension, not an inheritance**: binding a key that is deliberately absent from the platform profile is a key-resolution path UCP does not define, so implementers **MUST NOT** read this as UCP conformance. Also recorded the converse, that USP's requirement for a fetchable profile on every privileged request is *stricter* than UCP's consistency-only rule, so the identity-binding work is not a divergence
- Split the `README.md` standards table so RFC 9449 is no longer listed as Standalone-only, and added RFC 7638 and RFC 7800 alongside it; the previous row would have told readers that proof-of-possession does not apply in UCP-Native Mode

---

## 14/08/26 at 23:12:40 by [Ran Yahalom](mailto:ranya@wix.com)

- Added `tools/usp_check.py`, the repository's first mechanical validation. Nothing here previously checked that the JSON artefacts parse, that `schemas/*.json` compile as JSON Schema, or that cross-file `$ref`s resolve at all - the only `package.json` script builds the docs site - so schema drift was detectable only by review
- Made the `refs` check resolve every `$ref` **two** ways, by `$id` base-URI rules and by filesystem path, and fail when they disagree. Every `$id` under `schemas/` declares a directory the flat on-disk layout does not have (`services/`, `platform/`), so a cross-level `$ref` such as `booking.json` -> `usp.json` resolves cleanly in a filesystem-based editor and 404s in any `$id`-honouring validator. Existing refs all happen to stay within one level, which is exactly why the trap is invisible until someone adds the first cross-level one
- Added a version-identity assertion across `specification.md`, `README.md`, both binding `info.version` fields, and the roadmap's current row, turning what was a manual grep discipline into a build failure. It fires immediately: both bindings carry `2026-02-09` while the spec is at `2026-02-21`
- Added an unreferenced-`$defs` report, which found that `schemas/registry.json` `$defs/RegistrationRequest` is referenced by nothing because `openapi/usp-rest.json` declares the `POST /registry/businesses` body as a large inline object tree - the duplication [CLAUDE.md](CLAUDE.md) rule 3 forbids, with the two copies already free to drift
- Added `tools/known-issues.txt` as an explicit debt ledger rather than a suppression flag, so the three pre-existing failures above stay visible and their removal is a reviewable event; deliberately informative `$defs` are listed separately in the script, because "accepted forever by design" and "not fixed yet" should not look alike
- Added `.github/workflows/ci.yml`, the repository's first CI, running the three checks and a docs build. Deliberately not `mkdocs --strict`: `site-docs` links to repository files outside `docs_dir` that resolve on GitHub but not in mkdocs, and failing CI permanently on a design choice would train people to ignore it

---

## 14/08/26 at 22:56:14 by [Ran Yahalom](mailto:ranya@wix.com)

- Resolved a contradiction where the schema permitted what the specification body forbids: `schemas/profile.json` justified not defaulting `privileged_operations_require_authentication` to true on the grounds that "free/demo/sandbox deployments MAY legitimately run without it", while §10.1.6 states that privileged operations - explicitly including creating a booking - **MUST** be authenticated. A business could therefore publish `false`, validate cleanly, and believe it was conformant while serving real bookings unauthenticated. The property description now states that the flag declares *enforcement posture* rather than permission to violate §10.1.6, that a conformant deployment serving real bookings or buyer data **MUST** set it `true`, and that `false` is permitted only for explicitly non-production sandbox deployments
- Added the matching §10.1.6 paragraph so the rule is normative in the body and not only in a schema description: a deployment publishing `false` declares itself out of conformance for privileged operations, and a platform **MUST** treat `false` as a signal to *refuse* to transact real bookings or transmit buyer personal data - refuse, not warn and continue. Stated the converse case too (publishing `true` while accepting unauthenticated privileged requests is equally non-conformant), since the flag is only meaningful if it describes actual behaviour

---

## 12/08/26 at 15:33:08 by [Ran Yahalom](mailto:ranya@wix.com)

- Aligned USP publisher rules so signing material **MUST** appear in top-level `keys` (UCP-canonical) with optional identical `signing_keys` during transition, dual-publish recommended, and verifiers resolving `keys` first across `specification.md` §8.2.1 / §9.1.4 / §10.1.1, `schemas/profile.json`, site-docs, and OpenAPI examples
- Softened former publisher **MUST** on `signing_keys` so USP publishers satisfy UCP main/draft verifiers that require `keys[]`, without breaking Standalone readers that still consume the transition alias
- Cleared residual AC-S contradictions in the same signing surfaces: request covered components match UCP (`@authority`/`@path`, not `@created` as a covered component), `created` is an OPTIONAL request signature parameter, and `digest_mismatch` is HTTP 400 in both the spec table and `openapi/usp-rest.json`

---

## 10/08/26 at 18:16:00 by [Ran Yahalom](mailto:ranya@wix.com)

- Added an explicit guard against the pre-move placement of the authorization policy: `ServiceBinding.authorization` is now declared with a never-satisfiable schema in `schemas/usp.json`, so a binding that publishes the policy as a direct member is rejected instead of passing silently under `additionalProperties`. Without the guard a business could publish the old shape, see no validation error, and believe it had advertised an authentication requirement that no conforming platform reads - a fail-open outcome. Stated the corresponding **MUST NOT** in §8.2.1 and recorded it in §10.1.6 as the single, deliberate exception to that section's ignore-unrecognized-fields rule, so the two rules do not appear to contradict each other
- Posted amendment comments on [#9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9) and [#157](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/157) recording the `config.authorization` path, the guard, and the tightened `ServiceBinding` required fields, since both issue bodies still instruct implementers to read and publish the policy at the old location

---

## 10/08/26 at 18:07:00 by [Ran Yahalom](mailto:ranya@wix.com)

- Moved the UCP-Native `authorization` policy from a sibling member of the `dev.usp.services` binding to `config.authorization` on that binding. Being inside the `dev.usp.*` key satisfies UCP namespace governance, but UCP already defines `config` as the slot for entity-specific settings on a service or capability entry, so a sibling member was an invented field where UCP has an idiomatic one; keeping USP's own extension inside `config` also means the binding stays fully self-describing against the service's published schema. Updated `schemas/usp.json` (new `config` object on `ServiceBinding` holding the `AuthorizationPolicy` `$ref`), the §7.2 examples, the §7.3 and §10.1.6 placement rules, the §8.2.1 field tables, `schemas/profile.json` descriptions, `openrpc/usp-mcp.json`, `site-docs/security.md`, and `site-docs/deployment-modes/ucp-native.md`
- Aligned `ServiceBinding` field requirements with the UCP service definition, so a USP binding published inside `/.well-known/ucp` is conformant as-is: `spec` is now required, `schema` is required for `rest` / `mcp` / `embedded`, and `endpoint` is required for `rest` / `mcp` / `a2a` (the last two enforced via `if`/`then` rather than left as prose). Previously the schema required only `version` and `transport` while the prose called `spec` and `schema` merely RECOMMENDED, which meant USP was publishing bindings that strict UCP profile validation rejects. Also added the UCP `id` field and documented that `spec` / `schema` origins MUST match the namespace authority of the service key
- Fixed the free-service-only UCP-Native profile example, which was the concrete instance of the above defect: it published a `dev.usp.services` REST binding with no `spec` and no `schema` and would have failed UCP validation if copied. Corrected in §7.2 of `specification.md` and in the mirrored example in `site-docs/deployment-modes/ucp-native.md`, and updated the `ServiceBinding` table in `site-docs/deployment-modes/standalone.md` to match the tightened rules

---

## 10/08/26 at 17:23:09 by [Ran Yahalom](mailto:ranya@wix.com)

- Fixed a conformance defect that would have broken interoperability with UCP verifiers: §9.1.4 required the signature to cover `@target-uri` and `@created`, but UCP requires `@method` / `@authority` / `@path` (plus `@query`, agent header, `idempotency-key`, `content-digest`, `content-type` when present), and `created` is an RFC 9421 signature *parameter*, not a covered component. A signer following the old text would have been rejected by any verifier that enforces covered components, since target components absent from the covered set are treated as unsigned. Updated the normative list, the example, `site-docs/transport/rest.md`, and the OpenAPI/OpenRPC security-scheme descriptions, and added an explicit note that `@target-uri` may be covered additionally but never instead
- Corrected the same `@created` mistake where it had propagated: the §10.1.1 webhook covered-component list, the webhook examples in `specification.md` and `site-docs/transport/mcp.md`, the signature error table, `openapi/usp-rest.json`, and the `USPProtocolError` enum in `openrpc/usp-mcp.json`
- Replaced the USP-invented signature-timestamp replay window for *requests* with UCP's model (replay protection is the signed `Idempotency-Key`; `created` is OPTIONAL and a business MUST NOT reject a request for lacking it), while keeping the 5-minute `created` window plus event-`id` de-duplication as a MUST for *webhooks*, which carry no idempotency key. Previously both directions were conflated into one rule that contradicted UCP
- Gave the §10.1.6 `authorization` policy a defined, namespace-legal home in UCP-Native Mode: it is published on the `dev.usp.services` service binding inside `/.well-known/ucp`, not as a top-level member of a UCP profile, because UCP namespace governance requires non-UCP declarations to sit under their own reverse-domain authority. Previously the spec required the policy "in the business profile" while `AuthorizationPolicy` was only defined for the Standalone `/.well-known/usp` document, so UCP-Native deployments had nowhere legal to publish it. Added the placement rules to §10.1.6, §7.3, §8.2.1, the §7.2 examples, and an `authorization` property on `ServiceBinding` in `schemas/usp.json` that references the single `AuthorizationPolicy` definition
- Made the profile documents forward compatible so that §10.1.6's own rationale (policy as data, so UCP evolution is a schema addition rather than a rewrite) actually holds: relaxed `additionalProperties` on `BusinessProfile`, `PlatformProfile`, and `AuthorizationPolicy`, and converted `AuthorizationMechanism` and `SigningKey.kty` / `crv` / `alg` from closed enums to documented open vocabularies. Added a normative rule that consumers MUST ignore unrecognized mechanisms, algorithms, and fields rather than reject the document, and MUST NOT treat an unrecognized mechanism as accepted, so ignore-unknown never becomes fail-open
- Added the `keys` alias alongside `signing_keys` in both profile types, with verifiers resolving `keys` first, so USP tracks UCP's migration to a top-level RFC 7517 JWK Set without a flag day for either field name
- Aligned the signature error surface with UCP: added `algorithm_unsupported`, moved `digest_mismatch` from 401 to 400 (the message is malformed, not unauthenticated), and rescoped `signature_expired` to signatures the verifier actually evaluates for freshness
- Added `WWW-Authenticate` guidance on 401 for privileged operations (spec §10.1.6 and an OpenAPI response header), so a mechanism mismatch between a business and an agent is diagnosable rather than a silent failure, matching UCP's own unauthorized-response example
- Recorded as a Security Consideration that platform-level authentication answers "which platform is calling," not "may this caller act on this booking," so a business accepting only platform-level mechanisms on get/cancel/reschedule and PII-bearing operations knowingly exposes any identifiable booking to any authenticated platform. Left as SHOULD rather than MUST while the booking-scoped credential format is still open (#134 / #162)
- Added profile-fetch hardening to §8.2.3 (reject special-use IP ranges per RFC 6890, validate the resolved address against DNS rebinding, bound response size and timeouts, keep discovery cost constant for unrecognized platforms, limit force-refresh to once per TTL per origin), because a caller-supplied platform profile URI makes first-contact fetches an unauthenticated-request-triggered outbound request. Mirrors UCP's own fetching rules so UCP-Native businesses inherit rather than reimplement them, and added RFC 6890 to §14.1
- Updated §1.4 to describe RFC 9421 as covering both webhook verification and request signing, since it had described webhooks only

---

## 09/08/26 at 18:09:19 by [Ran Yahalom](mailto:ranya@wix.com)

- Aligned `openrpc/usp-mcp.json` with the AC-S auth model already in `openapi/usp-rest.json`, so transport-agnostic privileged-vs-public access and the five authorization mechanisms are shared rather than REST-only: extracted `$defs/AuthorizationMechanism` in `schemas/profile.json` (referenced by `AuthorizationPolicy`), annotated OpenAPI `securitySchemes` with `x-usp-mechanism`, and added matching `components.x-usp-securitySchemes` plus `McpAuthorization` / `McpUspMeta*` schemas and per-method `x-usp-access` (`public` / `privileged_platform` / `privileged_scoped`) in the MCP binding
- Made privileged MCP methods require `_meta` with `_meta.usp.profile` (identity binding equivalent to `USP-Agent`) and optional `_meta.usp.authorization` for credentials that must ride inside the tool call (stdio or booking-scoped), while MCP-over-HTTP continues to prefer HTTP-layer Authorization / RFC 9421 Signature / mTLS
- Updated `specification.md` §9.1.4 MCP note, §9.2.2 request format, and §9.2.4 MCP conformance, plus `site-docs/security.md`, so both bindings are explicitly subject to §10.1.6 and point at the shared `AuthorizationPolicy` / `AuthorizationMechanism` definitions instead of duplicating mechanism enums

---

## 09/08/26 at 18:00:52 by [Ran Yahalom](mailto:ranya@wix.com)

- Updated [issue #9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9) so AC-L matches the locked AC-S resolution: `linkusp-cli` must negotiate auth from the business profile `authorization.accepted_mechanisms` (prefer RFC 9421 signatures, then OAuth Bearer / API key / mTLS, and booking-scoped credentials for get/cancel when available), not hardcode Bearer-only; marked AC-S checkboxes complete and left AC-L open for CLI/SKILL implementation

---

## 09/08/26 at 17:55:43 by [Ran Yahalom](mailto:ranya@wix.com)

- Implemented the AC-S resolution of issue #9 (Finalize HTTP/REST transport binding authentication): added `specification.md` §10.1.6 "Platform Authentication for Privileged Operations" as a new mode-agnostic requirement (public catalog/availability/profile stay optionally anonymous; booking/hold/waitlist/payment-adjacent/PII-bearing/registry-write operations **MUST** be authenticated by at least one of HTTP Message Signatures, a booking-scoped capability credential, OAuth 2.0 Bearer, an API key, or mTLS), replacing the old blanket "USP endpoints MUST support OAuth 2.0 Bearer tokens" text in §10.2.3 that named a single mandatory mechanism
- Motivation: UCP's own HTTP/REST binding treats platform authentication as optional (`SHOULD`) because its ecosystem today is dominated by a small, enumerable set of well-known large AI platforms that can be vetted out-of-band; USP's scheduling domain additionally has to support personal, single-user "bring your own agent" deployments (one distinct agent instance per consumer, no realistic pre-onboarding step, no brand-level accountability) where unauthenticated privileged mutations and PII exposure are materially riskier against a materially larger population, so USP hardens this one point rather than inheriting UCP's optional posture for it, while leaving every other UCP-inherited concern unchanged
- Made the requirement mechanism-agnostic and business-declared (rather than naming one mandatory mechanism) specifically so it stays compatible if UCP's own posture evolves toward permissionless/scoped-credential patterns, and so it does not force every personal agent instance through a pre-registration bottleneck that does not scale to "bring your own agent" populations
- Added `$defs/AuthorizationPolicy` to `schemas/profile.json` (referenced, not duplicated, from `BusinessProfile.authorization`) so a business can declare `privileged_operations_require_authentication` and its `accepted_mechanisms` (`http_message_signature`, `booking_scoped_credential`, `oauth2_bearer`, `api_key`, `mtls`) as versioned profile data instead of spec prose
- Reserved `booking_scoped_credential` as an accepted mechanism name answering "does this caller hold the credential for this specific booking," independent of platform identity; deferred its issuance/validation mechanics to issue #134 (which feeds the broader plan item V2-X6 / issue #162) rather than designing it here
- Updated `openapi/usp-rest.json`: added `components.securitySchemes` (`HttpMessageSignature`, `BookingScopedCredential`, `OAuth2Bearer`, `ApiKey`, `MutualTLS`) and set per-operation `security` (empty for public catalog/availability/profile/registry-search paths; the four platform-level mechanisms for create-type privileged paths; all five, including the booking/waitlist-scoped credential, for get/update/cancel/reschedule/confirm paths on an existing booking, waitlist entry, hold, feed subscription, or registry registration)
- Updated `specification.md` §7.3 (UCP-Native inherited-infrastructure table and reading guidance) to clarify that §10.1.6 is an additive USP floor that applies in UCP-Native Mode too, not something UCP-Native inherits automatically; updated §9.1.4 to cross-reference §10.1.6 as the recommended way to satisfy the privileged-operation requirement without a pre-established credential; rewrote §10.2.3 to defer to §10.1.6 for the mechanism-agnostic MUST and keep only Standalone-Mode-specific OAuth/DPoP mechanics
- Mirrored the decision in `site-docs/security.md`: added a "Platform Authentication for Privileged Operations" subsection under the shared USP Security Requirements (with a rationale callout), reframed the former Standalone-only "Authentication and Authorization" section as "Pre-established Authentication Mechanics", and updated the Security Checklist table so OAuth 2.0 is listed as one available mechanism rather than the sole required/inherited one
- Posted an "AC-S resolution" comment on [issue #9](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/9) documenting the full rationale (BYOA-vs-large-platform mental model, the booking-scoped credential answer to "does this caller hold the token for this booking," the intentional UCP-alignment strategy, and why the declared-policy design minimizes future rework if UCP's posture changes), so the AC-S1/AC-S2 decision trail is preserved on the issue itself
- Scope note: this change covers AC-S (spec + bindings + docs) only, per the user's request; AC-L (`linkusp-cli` sending the chosen headers/credentials) and server-side enforcement on `usp-impl`/`usp-registry`/`acp-checkout` remain tracked in issues #118 and #157 respectively and were not touched here

---

## 06/08/26 at 20:55:50 by [Ran Yahalom](mailto:ranya@wix.com)

- Resolved issue #40 by adding a first-class buyer service delivery address: `DeliveryAddress` in `schemas/booking.json`, referenced (not duplicated) from `POST /bookings`, `PUT /bookings/{booking_id}`, and echoed on the `Booking` object, so field-service bookings no longer have to smuggle an unparseable address into free-text `notes`
- Renamed `channel.type: in_person` to `at_business_location` and added `at_buyer_location` (plus optional `service_area`) in `schemas/catalog.json`, because `in_person` was defined as "the buyer must attend in person" which is semantically inverted for any service where the provider travels to the buyer; names were chosen against external precedent (Square Appointments' `BUSINESS_LOCATION`/`CUSTOMER_LOCATION` enum, schema.org `serviceLocation`/`areaServed`) rather than invented in isolation, and reuse USP's own **Business**/**Buyer** glossary terms
- Promoted the Appendix A candidate vertical from `home_service` to a core vertical named `field_service`, because `home_service` reads as residential-only even though the same scheduling shape (buyer names a delivery address, provider travels there) applies to offices and other buyer-specified premises; `field_service` matches existing field-service-management industry terminology (Skedulo, Salesforce, ServiceTitan)
- Updated all affected bindings and mirrors for consistency: `openapi/usp-rest.json` and `openrpc/usp-mcp.json` (thin `$ref`s only, no duplicated shapes per repo convention), `specification.md` (§1.3.1, Appendix A, §3.3 channel types and schema.org mapping table, §5.2 Booking schema, §5.3.1/§5.3.3 booking operations and examples), site-docs mirrors (`specification/index.md`, `specification/service-catalog.md`, `specification/discovery-registry.md`, `deployment-modes/ucp-native.md`, `roadmap.md`), and playground fixtures (`playground/scenarios/services.json`, `site-docs/playground/scenarios/services.json`)
- Wrote design doc `docs/superpowers/specs/2026-08-06-service-delivery-address-and-channel-naming-design.md` and implementation plan `docs/superpowers/plans/2026-08-06-service-delivery-address-and-channel-naming.md` documenting the naming research and file impact
- Reassigned GitHub issue #40 to `@maoryeh` (owner of the USP registry and Wix business USP adapter tracks) with a comment detailing the breaking enum rename and new fields, since the Vespa registry indexing and `usp-impl` business adapter both need matching updates that are out of scope for this spec-only change

---

## 06/08/26 at 19:46:43 by [Ran Yahalom](mailto:ranya@wix.com)

- Resolved issue #59 by adding normative registry filter-matching semantics (§6.3.1) so federated registries share the same yes/no inclusion contract: four `match` modes (`overlap` default, `contained`, `contains`, `equals`) on `price_range` / `duration_range`, within-currency matching with currency required when ambiguous, free-as-0, undetermined duration exclusion, geo km + virtual exclusion, and OR-within-field for multi-value filters
- Extended `schemas/registry.json` with `RangeMatchMode` and agent-facing worked examples in filter `$defs`, retargeted OpenAPI search request bodies to thin `$ref`s of `BusinessSearchRequest` / `ServiceSearchRequest` to avoid drifting inline duplicates, and mirrored the rules in site-docs plus the registry design plan

---

## 06/08/26 at 19:06:07 by [Ran Yahalom](mailto:ranya@wix.com)

- Removed the singular `category` field from the catalog `Service` schema because the dual-field precedence rule in issue #54 caused implementer confusion about which representation was authoritative
- Replaced the thin `{value, taxonomy}` categories entries with an enriched `ServiceCategory` $def (`taxonomy`, optional `id`/`name`/`parent_id`/`value`/`primary`) so one `categories[]` array covers merchant hierarchy, display/localization, and multi-taxonomy labeling (e.g. merchant path plus Google Business Profile)
- Documented normative primary selection, localization (`localized.category_name` overrides primary `name`), catalog filter match rules (primary `id`, MAY match any `id`), and registry projection pick order for the flat `ServiceSearchResult.category` string so producers and registries share one rule
- Updated `specification.md`, site-docs (service catalog, discovery registry), OpenAPI/OpenRPC filter descriptions, playground fixtures (including a multi-taxonomy salon haircut scenario), and plan notes (`V2_PRODUCTION_PLAN.md`, `usp-registry-design-plan.md`) to match the single-field model without duplicating schema bodies into bindings

---

## 06/08/26 at 18:38:43 by [Ran Yahalom](mailto:ranya@wix.com)

- Clarified overloaded "discovery" terminology in `specification.md` §1.2 (and mirrored site-docs) by adding normative definitions for **Catalog Discovery**, **Profile Discovery**, and **Platform Onboarding**, plus a Mermaid lifecycle diagram, so implementors no longer infer meaning only from section context (issue #42)
- Stated explicitly in §6 / discovery-registry docs that registry registration is a directory listing, not platform-business onboarding or credential exchange, to keep registry search SLAs and vault/DCR flows distinct (issue #42)
- Qualified ambiguous `checkout_systems` prose and schema description to reference profile discovery or platform onboarding with a cross-link to §1.2, and scoped §9.1.3 / REST Discovery to profile discovery only (issue #42)
- Relabeled end-to-end sequence-diagram notes from generic "Service Discovery" to "Catalog & Availability/Booking" (and related platform/role wording) so diagram labels match the three-phase terminology without renaming `dev.usp.discovery.registry` or RFC 8414 metadata discovery (issue #42)

---

## 05/08/26 at 20:43:08 by [Ran Yahalom](mailto:ranya@wix.com)

- Created all 35 plan-local V2-* GitHub issues (#157-#191) in `wix-private/universal-scheduling-protocol-spec` from `plans/V2_PRODUCTION_PLAN.md` §4 so production readiness work is tracked with full ACs, §1a clarifications, assignees, and `v2` labels
- Applied §7 labelling on existing open issues (`v2`, `v>2`, `requires-approval` additive with existing `v1`/`v>1`) and posted §1a/§3 clarification comments on key judgement inclusions and exclusions so implementers see scoped-down authz and deferral rationale on the issues themselves
- Updated `plans/V2_PRODUCTION_PLAN.md` status to approved/issues-created and added Appendix A (V2-* → GitHub # mapping) so the plan is the durable index after issue creation

---

## 05/08/26 at 20:04:20 by [Ran Yahalom](mailto:ranya@wix.com)

- Added per-track GitHub assignees to `plans/V2_PRODUCTION_PLAN.md` §2 (Components and tracks) so newly created v2 issues are assigned consistently: `yahalomran` owns A, C, and S; `maoryeh` owns B, D, E, and F

---

## 05/08/26 at 18:51:05 by [Ran Yahalom](mailto:ranya@wix.com)

- Added §1a "Identity, authentication, and authorization clarifications" to `plans/V2_PRODUCTION_PLAN.md` so the plan records the Link-token piggyback verdict (not viable), AS-backed definition, why unauthenticated privileged UCP/USP APIs are dangerous vs public catalog/availability, that email match is CRM-only (not identity linking / not V2-X1), that booking get/cancel/PII authorization is a launch requirement with multiple mechanisms, that UCP identity linking remains optional, and that `specification.md` §10.2.4 now requires PKCE S256 plus RFC 9207 `iss`
- Added plan-local **V2-X6** (Authorize booking get/cancel and any response carrying buyer PII), tightened V2-X1 to privileged ops plus platform attribution (not browse-identity), elevated #134 into the launch-blocking authz story, and refreshed #9 / #102 / #118 / #119 / launch gates / schedule / open decisions / labelling so identity linking (#119) stays deferred while booking authorization does not

---

## 05/08/26 at 15:31:04 by [Ran Yahalom](mailto:ranya@wix.com)

- Added PKCE requirements to `specification.md` §10.2.4 Identity Linking (new "Authorization Code Protection" paragraph plus `code_challenge`/`code_verifier` in linking flow steps 1 and 3), because USP's identity linking omitted PKCE entirely while UCP `dev.ucp.common.identity_linking` makes RFC 7636 with `S256` a MUST on both the platform and the business side, leaving USP-only deployments exposed to authorization code interception
- Added an "Issuer Identification" paragraph to §10.2.4 requiring businesses to return the RFC 9207 `iss` response parameter and platforms to validate it against the discovered issuer, for parity with the UCP Mix-Up Attack defense that the existing RFC 8414 exact issuer comparison alone does not provide
- Added normative reference entries for RFC 7617, RFC 7636, RFC 8414, and RFC 9207 to §14.1, fixing the defect where §10.2.4 cited RFC 8414 and RFC 7617 without listing them in §14 and covering the two newly cited RFCs
- Added the corresponding link definitions (including section-anchored `[RFC 8414 §3.3]` and `[RFC 6749 §10.12]`, which were previously cited but undefined) to both link-definition blocks at the end of `specification.md`, so the citations render as links instead of literal bracketed text

---

## 05/08/26 at 10:12:47 by [Ran Yahalom](mailto:ranya@wix.com)

- Added `plans/V2_PRODUCTION_PLAN.md`, a 2-week plan to take the existing UCP-Native end-to-end demo to a production MVP, because the v1 plan only covered the demo and there was no single document stating what is strictly required before real buyers and real money are involved
- Classified all 55 open GitHub issues into v2 (25) and v>2 (30) with a per-issue production-implication justification, so that scope decisions are traceable rather than re-argued, and recorded the mandated segment constraints (Wix businesses with a connected Stripe account; buyers with a Stripe Link wallet; Base44 Superagent or any harness with the Link USP SKILL)
- Derived 34 new mandatory issues (`V2-*`) from reading the USP and UCP normative requirements against all four codebases (`linkusp-cli`, `usp-registry`, `usp-impl`, `acp-checkout`), because the largest production gaps had no issue at all: no inbound authentication on any USP/UCP surface, no idempotency on `complete_checkout` or on agent retries, no compensation when a charge succeeds but the booking does not, no registry Update/Delete or Stripe-eligibility admission gate, and zero custom metrics in any component
- Documented the launch-blocking subset and the recommendation to cut merchant population rather than security or money-correctness work if the schedule slips, since 59 issues across 6 tracks in 10 days does not fit without a named tail

---

## 04/08/26 at 20:34:03 by [Ran Yahalom](mailto:ranya@wix.com)

- Updated USP-open-issues-status canvas note for #127 to record that acceptance criteria are now explicit (11 checkboxes) and that primary implementation remains yahalomran/linkusp-cli while the Link-hosted calendar.link.com path is still backlog

---

## 04/08/26 at 16:36:30 by [Ran Yahalom](mailto:ranya@wix.com)

- Added GitHub issue #156 (Migrate protocol namespace authority from usp.dev to usp.live) as STILL_OPEN Spec proposals in USP-open-issues-status so the inventory reflects the new open namespace-migration work
- Placed #156 in a new DISTINCT "Namespace authority migration" cluster in USP-issue-overlap (not website SEO or registry design) and bumped live open-count KPIs from 56 to 57 after verifying search is:issue is:open

---

## 04/08/26 at 16:23:38 by [Ran Yahalom](mailto:ranya@wix.com)

- Marked GitHub issue #131 (USP onboarding extensions) CLOSED in USP-open-issues-status and USP-issue-overlap canvases after confirming state=closed and state_reason=not_planned, so canvas inventory matches the user's closure
- Decremented live open-issue KPIs from 57 to 56 (verified via user-wix-github search is:issue is:open) and removed #131 from open LinkUSP cluster ranges while refreshing closed-inventory counts and backlog themes

---

## 04/08/26 at 08:30:54 by [Ran Yahalom](mailto:ranya@wix.com)

- Fully refreshed USP-open-issues-status and USP-issue-overlap canvases against live GitHub (57 open issues) so inventories, KPIs, consolidations (#56→#58, #50→#47, #14→#9), and #155 STILL_OPEN match current reality after recent closures
- Confirmed PR #152 closed without merge and emptied close-candidates while keeping remaining epic recommendations as pending (not marked done)

---

## 04/08/26 at 08:21:13 by [Ran Yahalom](mailto:ranya@wix.com)

- Closed GitHub issues #56, #50, and #14 in wix-private/universal-scheduling-protocol-spec as high-confidence consolidations into canonical #58, #47, and #9 to remove duplicate backlog without losing acceptance criteria
- Posted fold-in comments on #58 (signing_key ownership-proof sub-question), #47 (poll 200+error / empty-query / stuck PAYMENT_PENDING ACs), and #9 (keep vs remove Authorization header) so remaining work stays on the canonical issues
- Updated USP-issue-overlap and USP-open-issues-status canvases to mark those consolidations DONE and the three issues CLOSED for reviewer visibility

---

## 04/08/26 at 08:02:28 by [Ran Yahalom](mailto:ranya@wix.com)

- Added a focused Cursor Canvas for USP open-issue overlap analysis so reviewers can prioritize redundant closes, merge groups, and epic structures across all currently open issues without modifying GitHub
- Documented high-confidence consolidations (#56→#58, #50→#47, #14→#9) plus epic recommendations for webhook E2E, LinkUSP production, and registry clusters to reduce backlog noise while preserving owner/repo boundaries

---

## 03/08/26 at 20:41:07 by [Ran Yahalom](mailto:ranya@wix.com)

- Updated website domain references from `usp.dev` to `usp.live` in `mkdocs.yml`, `llms.txt`, `llms-full.txt`, `robots.txt`, `humans.txt`, and social-card assets so canonical/SEO/LLM URLs match the live site deployment
- Added missing `favicon` in `mkdocs.yml` so browser tabs show the USP logo instead of the default MkDocs icon
- Fixed MkDocs-strict broken internal anchors that used four dashes (`----`) instead of the collapsed single-dash slugs in availability, booking, and discovery-registry docs
- Left protocol namespace URLs (`https://usp.dev/schemas/...`, etc.) unchanged because those are spec identifiers, not website links
- Skipped the PR #152 responsive CSS chunk because later mobile styles on this branch already cover that need

---

## 03/08/26 at 20:22:55 by [Ran Yahalom](mailto:ranya@wix.com)

- Added an interactive Cursor Canvas for the USP open-issues status analysis so reviewers can scan headline KPIs, prioritize evidence-backed close candidates, compare backlog themes, and filter or sort the full supplied issue inventory
- Confirmed the detailed inventory matches the supplied headline count and documented evidence limitations so the analysis remains transparent about its verification scope

---

## 17/07/26 at 21:17:51 by [Ran Yahalom](mailto:ranya@wix.com)

- Fixed Standalone carousel sub-tabs (Catalog / Availability / Booking) clipping paragraph and code snippet text on the left on mobile by constraining `.sub-tab-content` width, stacking `.sub-tab-pane` vertically with `align-items: stretch`, and removing rigid `min-width` on pane children so code blocks stay within the viewport
- Replaced `(width <= Npx)` media query syntax with `(max-width: Npx)` for broader mobile browser support and aligned carousel pane alignment from `center` to `stretch` on narrow screens to prevent horizontally centered overflow from being clipped

---

- Improved mobile layout for the MkDocs site by adding overflow clipping, responsive padding, and stacked layouts for the landing page announcement banner, feature cards, promo sections, and carousel tabs in `extra.css`, so narrow viewports (320px-768px) no longer trigger horizontal scroll from negative margins or fixed `min-width` values
- Added responsive table and image rules for documentation pages so wide tables and figures scroll or scale within the content column on small screens
- Enhanced playground mobile styles in `playground.css` with stacked header toggles, 44px touch targets, wrapping transport buttons, two-column step pills, and full-width step footers so the interactive demo remains usable on phones

---

## 15/07/26 at 13:07:36 by [Ran Yahalom](mailto:ranya@wix.com)

- Fixed the UCP-Native "See it in action" checkout code panel being clipped on the homepage by removing the rigid `min-width` on `.pane-visuals`, allowing flex children to shrink with `min-width: 0`, and adding container queries so the pane and code blocks stack when the content column (including beside the docs sidebar) is too narrow for side-by-side layout

---

## 13/07/26 at 23:39:10 by [Ran Yahalom](mailto:ranya@wix.com)

- Fixed missing right margin on playground screens by adding symmetric horizontal padding and a centered max-width on `.pg-playground`, setting `min-width: 0` on split/grid panes to prevent overflow, and consolidating responsive padding so nested sections no longer double up horizontal inset

---

## 13/07/26 at 23:36:55 by [Ran Yahalom](mailto:ranya@wix.com)

- Made UCP-Native the default deployment mode in the homepage "See it in action" carousel by listing it first in the tab bar and marking its pane active on load, so visitors see the primary integration path before Standalone

---

## 13/07/26 at 23:35:36 by [Ran Yahalom](mailto:ranya@wix.com)

- Removed the homepage "Endorsed across the ecosystem" partner marquee from `home.html`, deleted all partner-carousel/chip CSS from `extra.css`, and dropped unused industry-tab autoplay logic from `extra.js`, so the site no longer displays placeholder partner, sponsor, or endorser affiliations

---

## 13/07/26 at 23:06:49 by [Ran Yahalom](mailto:ranya@wix.com)

- Changed `repo_name` in `mkdocs.yml` to "USP on GitHub" so the header source link matches the UCP site label instead of showing a truncated repository slug

---

## 13/07/26 at 22:34:17 by [Ran Yahalom](mailto:ranya@wix.com)

- Removed the homepage "Co-developed by industry leaders" partner tabs section from `home.html` and dropped the unused `#industry-tabs` CSS rules from `extra.css`, because that placeholder content is not ready to publish yet

---

## 13/07/26 at 22:31:32 by [Ran Yahalom](mailto:ranya@wix.com)

- Moved Overview and Specification navigation into the left sidebar only (matching UCP) by removing `navigation.tabs` and `navigation.tabs.sticky` from `mkdocs.yml`, and added defensive CSS in `extra.css` to hide the header tab bar and keep top-level nav items visible in the primary panel on all viewports

---

## 13/07/26 at 22:29:57 by [Ran Yahalom](mailto:ranya@wix.com)

- Reverted the site from green-tinted page backgrounds to white and neutral gray surfaces (`#fff`, `#f8f9fa`, `#f1f3f4`) in `extra.css`, restored teal accent colors (`#0d9488`) for links, badges, and active tabs, and added a subtle hero radial glow matching the earlier site
- Aligned playground panel and code backgrounds in `playground.css` to the same neutral palette and teal primary tokens

---

## 13/07/26 at 22:19:08 by [Ran Yahalom](mailto:ranya@wix.com)

- Fixed homepage Catalog / Availability / Booking sub-tabs (and Standalone / UCP-Native main tabs) not switching by aligning `openTab` and `openSubTab` in `extra.js` with the `onclick` + element-id markup in `home.html`, which toggles `.active` on `.tab-pane` and `.sub-tab-pane` siblings

---

## 13/07/26 at 22:10:35 by [Ran Yahalom](mailto:ranya@wix.com)

- Fixed playground response panes showing corrupted numeric placeholder output instead of real scenario JSON by reusing `highlightJson` from `code-editor.js` in `playground-controller.js`, which uses non-numeric placeholder tokens that survive the number-highlighting pass

---

## 13/07/26 at 22:04:57 by [Ran Yahalom](mailto:ranya@wix.com)

- Swapped the site surface palette to a green-tinted background scale (`--usp-bg-0` through `--usp-bg-4`) in `extra.css`, wired header, promo cards, sections, code blocks, partner carousel, and footer to those tokens, and kept normal body/landing text black via `--md-typeset-color` and `.landing-page { color: #000 }`
- Aligned playground panel/code backgrounds in `playground.css` to the same greenish elevated surfaces so the demo page matches the docs chrome

---

- Fixed playground bugs from verification: dynamic request pane headers on all steps, GET query strings in REST formatting, capability negotiation intersection with holds stripped on partial match, discovery refresh on scenario change, and accurate error labels (429 hold limit, 402 payment failed)
- Removed misleading schema-validation claim from playground intro; added `GET /services` MCP mapping and carousel mode/sub-panel opacity grid CSS for homepage tabs

---

## 13/07/26 at 20:06:42 by [Ran Yahalom](mailto:ranya@wix.com)

- Completed full ucp.dev homepage parity in `overrides/home.html`: banner icon, hero-wrapper without in-hero CTAs, Learn/Implement promo cards, co-developed industry tabs, flexibility principles, deployment-mode action carousel, two-column deployment promo, lifecycle ecosystem roles, endorsed partner marquee, and Get started today (removed stats, verticals, how-it-works, transport cards, and custom footer)
- Moved tab logic to `site-docs/javascripts/extra.js` as global `openTab`/`openSubTab` with industry-tab 3s autoplay; kept announce-banner dismiss and removed the legacy `usp-tabs` data-tab handler
- Ported UCP landing CSS into `site-docs/stylesheets/extra.css` (partner-carousel/chips, pane layout, opacity-grid carousel, lifecycle/two-column-promo blocks, get-started step chrome fix, 960px hero breakpoint) and added slate dark-mode palette to `mkdocs.yml`

---

## 13/07/26 at 20:04:37 by [Ran Yahalom](mailto:ranya@wix.com)

- Restructured homepage "See It in Action" to match ucp.dev: deployment-mode tabs (Standalone / UCP-Native), sub-tabs (Catalog / Availability / Booking), pane-text + pane-visuals layout, opacity/visibility grid panels, and scoped `openTab()` / `openSubTab()` handlers so panel height stays stable with fade-in transitions
- Replaced partners placeholder with UCP-style industry vertical tabs (Appointments / Group / Reservations / Rentals) using text chips, plus an infinite-scroll ecosystem marquee with scheduling-relevant names; industry tabs autoplay every 3s and pause on hover or click
- Fixed homepage CTA parity: hero GitHub opens in a new tab; Get Involved cards use `<div>` wrappers with title-only links; Playground and Contribute open in new tabs
- Restored primary docs sidebar on the landing page (matching ucp.dev), added carousel responsive stacking at 1200px and 960px, and aligned hero stack breakpoint to 960px

---

## 13/07/26 at 17:30:57 by [Ran Yahalom](mailto:ranya@wix.com)

- Wired the playground transport toggle to `transport-formatter.js` via ES module `playground-controller.js`, so REST/MCP/A2A/ESP switches re-render the request pane using the same formatting path as the full `playground.js` engine (matching UCP's integrated playground script pattern)
- Load playground controller as `type="module"` in `overrides/playground.html` and cache per-step scenario state so transport and mode changes refresh requests without re-fetching
- Added `/.well-known/ucp` tool mappings in `transport-formatter.js` for UCP-Native mode discovery

---

## 13/07/26 at 17:10:15 by [Ran Yahalom](mailto:ranya@wix.com)

- Fixed broken cross-doc link in `site-docs/deployment-modes/ucp-native.md` (pointed at repo-root `specification.md` outside `site-docs`) to the on-page `#paid-bookings-extension-schema` anchor so `mkdocs build --strict` passes after the UCP parity site work

---

## 13/07/26 at 17:09:20 by [Ran Yahalom](mailto:ranya@wix.com)

- Hid the primary docs sidebar on the homepage and playground so landing and demo pages use full-width layout like ucp.dev, instead of squeezing content beside the nav column
- Swapped the get-started CTA middle card to "Try the Playground" (matching UCP's Experiment card) so the bottom-of-page funnel highlights the interactive demo

---

## 13/07/26 at 17:08:44 by [Ran Yahalom](mailto:ranya@wix.com)

- Aligned USP docs site global chrome with ucp.dev: white Material header, Google Sans/Roboto Mono fonts, indigo accent palette (removed teal custom theme and dark-mode toggle), plus `navigation.tracking`, `content.code.select`, `content.tooltips`, and cookie consent `scope: /`
- Ported UCP landing-page patterns into `extra.css` and `home.html`: pill buttons, promo cards, light action-carousel code tabs with fade-in, vertical features list, light get-started CTA, announcement banner, and footer wrapper
- Upgraded playground UX: request/response split panes, functional mode/transport toggles, step fade animation, auto-run on discovery/negotiation enter, side-by-side negotiation capability grid, and "About this demo" callout; aligned `playground.css` tokens to UCP indigo/ink/surface colors
- Fixed broken social/OG image references to use existing `social-card.svg` and `usp-logo.svg` instead of missing PNG assets

---
## 13/07/26 at 17:08:42 by [Ran Yahalom](mailto:ranya@wix.com)

- Realigned the USP docs site visual system with [ucp.dev](https://ucp.dev/): white Material header, Google Sans typography, indigo accent palette, pill CTAs, light carousel tabs, and vertical principles layout so the sibling protocol sites read as one ecosystem
- Refreshed homepage markup (`overrides/home.html`) with announcement banner, Learn/Implement promo cards, light "See It in Action" section, get-started CTA, and custom footer wrapper matching UCP landing-page patterns
- Upgraded playground to UCP-style split request/response panes, negotiation capability grid, step fade transitions, functional mode toggle (USP vs UCP profile paths), and "About this demo" callout; rewrote `playground-controller.js` to match the new panel IDs
- Updated `mkdocs.yml` (Google Sans, white/indigo palette, `navigation.tracking`, consent `scope: /`) and fixed broken social/OG image references in `overrides/main.html` and `overrides/playground.html`

---

## 13/07/26 at 16:03:04 by [Ran Yahalom](mailto:ranya@wix.com)

- Added `package.json` with `python3 -m mkdocs build` so Vercel treats the project as a static MkDocs site instead of a Python serverless app (Vercel CLI 55+ errors on missing Python entrypoints when only `requirements.txt` is present)
- Added `vercel.json` with `outputDirectory: site`, `/spec` rewrites, `/github` redirect, and cache/security headers aligned with `render.yaml` so Vercel deployment matches the existing Render static-site behavior

---

## 13/07/26 at 14:52:16 by [Ran Yahalom](mailto:ranya@wix.com)

- Added optional `availability_hint` to `ServiceSearchResult` in `schemas/registry.json` (by `$ref` to catalog `AvailabilityHint`), so registry service search can pass through the catalog's approximate availability signal and agents can reason about near-term availability without an extra catalog fetch per hit
- Updated `specification.md` §6.3 and `site-docs/specification/discovery-registry.md` with response examples and normative guidance: registries SHOULD pass through the hint when present at index time; platforms MUST NOT treat it as authoritative or as a hard availability filter
- Aligned `plans/usp-registry-design-plan.md` §1.4, §1.10, and §2.3 with the wire-model change (replacing the prior index-only, not-returned decision from PR #57 review)

---

## 03/07/26 at 13:08:53 by [Ran Yahalom](mailto:ranya@wix.com)

- Refined `docs/dtc_charter_nomination.md` to increase GC approval odds: removed leftover assistant-conversation text from the submission body (e.g. "If you want, I can save this as a markdown file..."), which would have been embarrassing if filed as-is, and clearly fenced the internal submission notes behind a delete-before-filing marker
- Replaced the spec link pointing to the inaccessible private repo (`wix-private/universal-scheduling-protocol-spec`) with the public `kobym707/universal-scheduling-protocol` remote, since GC reviewers cannot evaluate evidence they cannot open
- Added a "Domain Scope" subsection delimiting the four core verticals against the adjacent Lodging (#543) and Food Ordering (#518) DTCs, to preempt GC scope-overlap objections
- Reframed the "Reference implementation" paragraph as a "starting-point contribution" with explicit DTC authority over final namespaces and schemas, to counter the perception of a pre-baked single-vendor (Wix/USP) protocol being rubber-stamped rather than chartered
- Filled the Platforms (Google, Stripe Link, Microsoft Copilot) and Businesses (Wix, Square, Mindbody+ClassPass, Fresha) placeholders with ranked candidates marked "to be confirmed", plus a rationale section with alternates, because the charter requires 3+ committed organizations before filing

---

## 13/07/26 at 14:52:16 by [Ran Yahalom](mailto:ranya@wix.com)

- Added optional `availability_hint` to `ServiceSearchResult` in `schemas/registry.json` (by `$ref` to catalog `AvailabilityHint`), so registry service search can pass through the catalog's approximate availability signal and agents can reason about near-term availability without an extra catalog fetch per hit
- Updated `specification.md` §6.3 and `site-docs/specification/discovery-registry.md` with response examples and normative guidance: registries SHOULD pass through the hint when present at index time; platforms MUST NOT treat it as authoritative or as a hard availability filter
- Aligned `plans/usp-registry-design-plan.md` §1.4, §1.10, and §2.3 with the wire-model change (replacing the prior index-only, not-returned decision from PR #57 review)

---

## 03/07/26 at 13:08:53 by [Ran Yahalom](mailto:ranya@wix.com)

- Refined `docs/dtc_charter_nomination.md` to increase GC approval odds: removed leftover assistant-conversation text from the submission body (e.g. "If you want, I can save this as a markdown file..."), which would have been embarrassing if filed as-is, and clearly fenced the internal submission notes behind a delete-before-filing marker
- Replaced the spec link pointing to the inaccessible private repo (`wix-private/universal-scheduling-protocol-spec`) with the public `kobym707/universal-scheduling-protocol` remote, since GC reviewers cannot evaluate evidence they cannot open
- Added a "Domain Scope" subsection delimiting the four core verticals against the adjacent Lodging (#543) and Food Ordering (#518) DTCs, to preempt GC scope-overlap objections
- Reframed the "Reference implementation" paragraph as a "starting-point contribution" with explicit DTC authority over final namespaces and schemas, to counter the perception of a pre-baked single-vendor (Wix/USP) protocol being rubber-stamped rather than chartered
- Filled the Platforms (Google, Stripe Link, Microsoft Copilot) and Businesses (Wix, Square, Mindbody+ClassPass, Fresha) placeholders with ranked candidates marked "to be confirmed", plus a rationale section with alternates, because the charter requires 3+ committed organizations before filing

---

## 01/07/26 at 16:07:29 by [Ran Yahalom](mailto:ranya@wix.com)

- Expanded `plans/USP+UCP_implementation_plan.md` [#89](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/89) section with full detail from [issue comment #4761877725](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/89#issuecomment-4761877725): checkout `payment_handlers` must expose Stripe SPT prerequisites (`network_id`), server-side HTTP 402 / `mpp decode` resolution during checkout creation, checkout-over-profile authority, acceptance criteria, and cross-links to [#64](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/64) and [#99](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/99) - so the implementation plan matches the GitHub issue guidance for UCP-native SPT acquisition
- Updated [#64](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/64) and demo-flow step 15 in the same plan to state the agent reads `network_id` from checkout `payment_handlers` (not merchant HTTP probing) when required for `shared_payment_token` spend requests
- Added normative intent note under [#99](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/99) that PSP acquisition inputs such as `network_id` belong only on UCP checkout `payment_handlers`, not USP-only extension fields

---

## 23/06/26 at 20:12:36 by [Ran Yahalom](mailto:ranya@wix.com)

- Moved all `signing_keys`-related work out of demo scope: created GitHub issue [#116](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/116) "usp-impl: RFC 9421 outbound webhook signing + signing_keys in merchant profile" (v>1, track-d, @maoryeh) as the single post-demo home for both Wix publishing signing_keys and signing outbound booking.confirmed webhooks
- Updated #91 (usp-impl booking.confirmed webhook) to send unsigned webhooks for demo and reference #116 for post-demo signing, removing the RFC 9421 criterion that was in scope
- Updated #70 (Demo merchant readiness prerequisite) to remove `signing_keys` presence from the demo checklist description, with an explicit note that it is deferred to #116
- Updated #102 (UCP conformance gaps rollup) to add a new tracked gap row and prose section for Wix RFC 9421 outbound signing (#116), and added #116 to the dedicated post-demo implementation issues table alongside #112, #114, #115
- Updated `plans/USP+UCP_implementation_plan.md` to reflect the same scope reduction: step 21 description, demo success criteria, #70 readiness checklist, #92 webhook receiver step 3, #91 signing step, and the out-of-scope section now all explicitly state the demo webhook is unsigned and point to #116 / #115 for post-demo hardening

---

## 23/06/26 at 17:45:39 by [Ran Yahalom](mailto:ranya@wix.com)

- Created GitHub issue #114 "Link: publish hosted per-agent platform profile (LINK_UCP_PLATFORM_PROFILE_URL)" (labels: v>1, track-a; assigned: yahalomran) with per-agent profile architecture (relay / tunnel / deployed), HTTPS hosting constraints, and `booking_webhook.py` durability requirements - motivated by #102 part (a) Link side lacking a dedicated actionable issue
- Created GitHub issue #115 "Link: RFC 9421 webhook signature verification (booking.confirmed inbound)" (labels: v>1, track-a; assigned: yahalomran) to replace the `LINKUSP_WEBHOOK_VERIFY=1` header-presence stub with full §10.1.1 verification - motivated by #102 rollup bullet having no dedicated Link implementation issue
- Updated GitHub issue #102 with cross-refs to #114 and #115 in summary table, subsections, and a new "Dedicated post-demo implementation issues" table linking #114, #115, and #112
- Updated GitHub issue #112 to reference #114 (Link profile prerequisite) and #115 (inbound verification) in the production path steps and references

---

## 22/06/26 at 13:55:56 by [Ran Yahalom](mailto:ranya@wix.com)

- Expanded GitHub issue #112 background with the full end-to-end "zero registration" production path (5 steps, §8.3 and §9.2.3 normative citations, `profile_unreachable`/`profile_malformed` error types, `FinalizeBookingOnPayment` trigger, signing-key publication detail, and Step 5 Link-side verification consequences) - motivated by the earlier description being accurate but too shallow to serve as a complete spec reference for the implementer
- Updated GitHub issue #112 acceptance criteria to replace the silent-fallback criterion with an explicit requirement that fetch failures MUST surface as protocol errors, and added a note that `USP_DEMO_PLATFORM_WEBHOOK_URL` may only remain as a clearly-labelled non-conformant dev override
- Expanded GitHub issue #102 "Production webhook URL derivation" subsection with the §9.2.3 normative quote, the "zero registration" framing, and the split between the already-structurally-complete Link side and the Wix-side `profile_unreachable`/`profile_malformed` obligation - also added `event_id` deduplication confirmation requirement to the RFC 9421 webhook verification bullet

---

## 22/06/26 at 13:45:38 by [Ran Yahalom](mailto:ranya@wix.com)

- Created GitHub issue #112 "usp-impl: derive webhook_url from platform profile (UCP-Agent header)" (labels: v>1, webhooks, track-d, usp-impl; assigned: maoryeh) to track the untracked Wix production path where the callback URL is derived from the UCP-Agent header rather than the out-of-band USP_DEMO_PLATFORM_WEBHOOK_URL env var - motivated by #91 step 4 naming this path without a dedicated issue or acceptance criteria
- Updated GitHub issue #102 "UCP conformance gaps" to add two new subsections in "Additional gaps": (a) "Production webhook URL derivation" covering the Link profile publication and Wix UCP-Agent fetch approach with cross-ref to #112; (b) "Full RFC 9421 webhook signature verification" covering replacement of the LINKUSP_WEBHOOK_VERIFY=1 header-presence stub - both gaps were previously untracked in any issue
- Added comment to GitHub issue #91 tagging @maoryeh and cross-referencing the new #112 issue as the dedicated follow-on for the production webhook URL derivation path named in #91 step 4

---

## 22/06/26 at 13:29:55 by [Ran Yahalom](mailto:ranya@wix.com)

- Created GitHub issue #111 "Consider per-capability webhook_url in USP to align with UCP's registration model" to track the design discussion around replacing USP's top-level `webhook_url` with per-capability `config.webhook_url` entries - motivated by the inconsistency between USP's current model and UCP's capability-scoped webhook registration, which creates a structural hybrid in UCP-Native mode profiles

---

## 24/06/26 at 10:43:20 by [Ran Yahalom](mailto:ranya@wix.com)

- Applied GitHub issue updates via wix-github MCP for the step 21 scope cut: #65 body + scope comment (demo ends at sync `complete_checkout`, no webhook assertion), #70 (removed `USP_DEMO_PLATFORM_WEBHOOK_URL` from demo checklist), #91 and #92 relabeled `v>1` with post-demo acceptance criteria; reopened #92 as open post-demo work

---

## 24/06/26 at 08:53:27 by [Ran Yahalom](mailto:ranya@wix.com)

- Moved plan step 21 (`booking.confirmed` webhook E2E) out of demo scope in `plans/USP+UCP_implementation_plan.md`: demo now ends at synchronous `complete_checkout` (step 20) with `status: completed`, `order_id`, and `booking.booking_status: confirmed`; removed G-12 from the in-scope gap matrix; updated sequence diagram, success criteria, Definition of Done, #65/#70/#91/#92 task sections, sprint calendar/critical path, and added a dedicated "Post-demo: booking.confirmed webhook E2E" out-of-scope section linking #91, #92, #112, #114, #115, #116
- Added GitHub issue update drafts under `.github/issue-drafts/` for #65, #70, #91 (v>1), and #92 (v>1) reflecting the same scope cut; wix-github MCP returned 401 on issue update (credentials unavailable in this session), so issues need a manual apply or re-run after auth is restored

---

## 23/06/26 at 20:12:36 by [Ran Yahalom](mailto:ranya@wix.com)

- Moved all `signing_keys`-related work out of demo scope: created GitHub issue [#116](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/116) "usp-impl: RFC 9421 outbound webhook signing + signing_keys in merchant profile" (v>1, track-d, @maoryeh) as the single post-demo home for both Wix publishing signing_keys and signing outbound booking.confirmed webhooks
- Updated #91 (usp-impl booking.confirmed webhook) to send unsigned webhooks for demo and reference #116 for post-demo signing, removing the RFC 9421 criterion that was in scope
- Updated #70 (Demo merchant readiness prerequisite) to remove `signing_keys` presence from the demo checklist description, with an explicit note that it is deferred to #116
- Updated #102 (UCP conformance gaps rollup) to add a new tracked gap row and prose section for Wix RFC 9421 outbound signing (#116), and added #116 to the dedicated post-demo implementation issues table alongside #112, #114, #115
- Updated `plans/USP+UCP_implementation_plan.md` to reflect the same scope reduction: step 21 description, demo success criteria, #70 readiness checklist, #92 webhook receiver step 3, #91 signing step, and the out-of-scope section now all explicitly state the demo webhook is unsigned and point to #116 / #115 for post-demo hardening

---

## 23/06/26 at 17:45:39 by [Ran Yahalom](mailto:ranya@wix.com)

- Created GitHub issue #114 "Link: publish hosted per-agent platform profile (LINK_UCP_PLATFORM_PROFILE_URL)" (labels: v>1, track-a; assigned: yahalomran) with per-agent profile architecture (relay / tunnel / deployed), HTTPS hosting constraints, and `booking_webhook.py` durability requirements - motivated by #102 part (a) Link side lacking a dedicated actionable issue
- Created GitHub issue #115 "Link: RFC 9421 webhook signature verification (booking.confirmed inbound)" (labels: v>1, track-a; assigned: yahalomran) to replace the `LINKUSP_WEBHOOK_VERIFY=1` header-presence stub with full §10.1.1 verification - motivated by #102 rollup bullet having no dedicated Link implementation issue
- Updated GitHub issue #102 with cross-refs to #114 and #115 in summary table, subsections, and a new "Dedicated post-demo implementation issues" table linking #114, #115, and #112
- Updated GitHub issue #112 to reference #114 (Link profile prerequisite) and #115 (inbound verification) in the production path steps and references

---

## 22/06/26 at 13:55:56 by [Ran Yahalom](mailto:ranya@wix.com)

- Expanded GitHub issue #112 background with the full end-to-end "zero registration" production path (5 steps, §8.3 and §9.2.3 normative citations, `profile_unreachable`/`profile_malformed` error types, `FinalizeBookingOnPayment` trigger, signing-key publication detail, and Step 5 Link-side verification consequences) - motivated by the earlier description being accurate but too shallow to serve as a complete spec reference for the implementer
- Updated GitHub issue #112 acceptance criteria to replace the silent-fallback criterion with an explicit requirement that fetch failures MUST surface as protocol errors, and added a note that `USP_DEMO_PLATFORM_WEBHOOK_URL` may only remain as a clearly-labelled non-conformant dev override
- Expanded GitHub issue #102 "Production webhook URL derivation" subsection with the §9.2.3 normative quote, the "zero registration" framing, and the split between the already-structurally-complete Link side and the Wix-side `profile_unreachable`/`profile_malformed` obligation - also added `event_id` deduplication confirmation requirement to the RFC 9421 webhook verification bullet

---

## 22/06/26 at 13:45:38 by [Ran Yahalom](mailto:ranya@wix.com)

- Created GitHub issue #112 "usp-impl: derive webhook_url from platform profile (UCP-Agent header)" (labels: v>1, webhooks, track-d, usp-impl; assigned: maoryeh) to track the untracked Wix production path where the callback URL is derived from the UCP-Agent header rather than the out-of-band USP_DEMO_PLATFORM_WEBHOOK_URL env var - motivated by #91 step 4 naming this path without a dedicated issue or acceptance criteria
- Updated GitHub issue #102 "UCP conformance gaps" to add two new subsections in "Additional gaps": (a) "Production webhook URL derivation" covering the Link profile publication and Wix UCP-Agent fetch approach with cross-ref to #112; (b) "Full RFC 9421 webhook signature verification" covering replacement of the LINKUSP_WEBHOOK_VERIFY=1 header-presence stub - both gaps were previously untracked in any issue
- Added comment to GitHub issue #91 tagging @maoryeh and cross-referencing the new #112 issue as the dedicated follow-on for the production webhook URL derivation path named in #91 step 4

---

## 22/06/26 at 13:29:55 by [Ran Yahalom](mailto:ranya@wix.com)

- Created GitHub issue #111 "Consider per-capability webhook_url in USP to align with UCP's registration model" to track the design discussion around replacing USP's top-level `webhook_url` with per-capability `config.webhook_url` entries - motivated by the inconsistency between USP's current model and UCP's capability-scoped webhook registration, which creates a structural hybrid in UCP-Native mode profiles

---

## 22/06/26 at 09:45:35 by [Ran Yahalom](mailto:ranya@wix.com)

- Repaired UTF-8 mojibake in `plans/USP+UCP_implementation_plan.md` (arrow `→`, section sign `§`, middle dot `·`, em dash turned into spaced hyphen ` - `) and normalized table-of-contents fragment links so GitHub-style anchors match the corrected headings, because the plan had been saved with Latin-1 mis-decoding of those UTF-8 sequences and stale double-hyphen slugs.

---

## 21/06/26 at 21:25:39 by [Ran Yahalom](mailto:ranya@wix.com)

- Closed the gap tracked as [wix-private/universal-scheduling-protocol-spec#99](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/99): `specification.md` §7.2 / §7.4 / §7.5 / §7.7.2 now show UCP-conformant `payment_handlers` (reverse-domain keys, handler arrays, `available_instruments`), normative rules that checkout responses override the profile at payment time with a **MUST** on using checkout `available_instruments` when present, and `complete_checkout` examples use `payment.instruments[].handler_id` tied to the handler instance `id`, so implementers stop mis-parsing flat `stripe_card` shapes and match [UCP payment architecture](https://ucp.dev/latest/specification/overview/#payment-architecture).
- Updated `site-docs/deployment-modes/ucp-native.md`, `plans/USP+UCP_implementation_plan.md` (step 4, §2.4 verification, [#89](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/89) / [#99](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/99) text), the Standalone §8.2 design note to separate UCP `payment_handlers` from `checkout_systems`, and added `docs/ucp-native-demo-merchant-profile.example.json` as the canonical illustrative merged profile for the demo, so Track E/F work and registry docs stay aligned with the same wire examples.

---


- Brought `README.md` in line with the current specification outline (domain core through optional Section 6 Discovery Registry, Sections 7-8 deployment modes, 9-10 infrastructure, 11 extensions, 12-14 appendices), updated internal links, cross-cutting RFC section pointers, the machine-readable artifacts path (`schemas/` plus the full current schema file list), and the Mermaid implementer diagram, because those details had drifted after Section 6 and later renumbering landed on `main`.
- Expanded `specification.md` Section 1 Introduction with the narrative from [wix-private/universal-scheduling-protocol-spec PR #38](https://github.com/wix-private/universal-scheduling-protocol-spec/pull/38) (problem framing, agentic design call-outs, protocol structure overview) while citing existing informative references and avoiding ambiguous punctuation, so first-time readers get the same motivation without reviving a stale merge branch.

---

## 17/06/26 at 17:22:24 by [maorye](mailto:maorye@wix.com)

- Updated `plans/usp-registry-design-plan.md` — the design plan for the USP discovery registry (`dev.usp.discovery.registry`, §6). Organized in three parts: vendor-neutral protocol-level design (operations, wire model, ownership handshake, ingestion contract, filter semantics), the Wix implementation (Vespa/vFeed/vSearch, projection, ingestion/auth/search), and phasing (Phase 1 demo = no auth + registration + push-only service ingestion + business/service search, then auth, conformant pull+subscription ingestion, MCP, Wix onboarding, hybrid ranking). Includes Mermaid flow diagrams and a decision log scoped Protocol-vs-Impl. Merged the latest design content onto the existing `plans/` version (keeping its table of contents, cross-reference hyperlinks, and canonical issue URLs) and removed the earlier `docs/` copy so the plan lives only under `plans/`.
- Per PR #57 review: the catalog `availability_hint` (§3.6) is **indexed and searched against** by the registry as a ranking/recall signal but is **not** returned in `ServiceSearchResult` and is **never** a hard filter — so it is an implementation choice only, requiring no spec or schema change (the source field already exists on catalog `Service`). Recorded the trust & anti-abuse concerns (legitimacy verification, Sybil/registry-pollution — issue #106) and the marketplace/aggregator-relay federation case (folded into #55) raised in review.

---

## 17/06/26 at 08:58:31 by [Ran Yahalom](mailto:ranya@wix.com)

- Pointed every `#54`–`#59` reference in `plans/usp-registry-design-plan.md` at canonical GitHub issue URLs on `wix-private/universal-scheduling-protocol-spec` so links work from forks, exports, and readers who are not already in the spec repo tree
- Confirmed via the API that those five issues still match the plan topics (categories, registry discovery, `signing_key` requirement, registration auth, search filter semantics); issue numbers needed no correction
- Posted the same short cross-reference comment on each of #54, #55, #56, #58, and #59 so the tickets link back to Part 1 §1.10 of the design plan on `main`

---

## 16/06/26 at 17:54:50 by [Ran Yahalom](mailto:ranya@wix.com)

- Added a table of contents and cross-reference hyperlinks throughout `plans/usp-registry-design-plan.md` so readers can navigate between Part 1/2/3 sections, the decision log, and phasing phases without scrolling
- Linked registry design sections to normative repo artifacts (`specification.md` §6/§3/§9/§10, `schemas/registry.json`, OpenAPI/OpenRPC bindings, site docs) and external references (UCP profile, RFC 9421/9457) so protocol gaps and implementation choices trace back to source material

---

## 16/06/26 at 17:19:23 by [Ran Yahalom](mailto:ranya@wix.com)

- Triaged GitHub issues in `wix-private/universal-scheduling-protocol-spec`: closed [#53](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/53) as duplicate of [#103](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/103) (GH-099), assigned `maoryeh` to #103 with `track-d`/`usp-impl` labels, closed [#19](https://github.com/wix-private/universal-scheduling-protocol-spec/issues/19) as superseded by sprint Track C #71-#75, labeled all 24 previously unscoped open issues with `v>1` plus component labels (`spec`, `usp-impl`, `registry`, `standalone`, `bug`, `question`), and added `out-of-scope` to #51
- Renamed scope label references from `v > 1` to `v>1` in `plans/USP+UCP_implementation_plan.md` and `scripts/update_plan_issues.py` to match the renamed GitHub label

---

## 16/06/26 at 12:40:08 by [Ran Yahalom](mailto:ranya@wix.com)

- Filed all 44 USP+UCP plan work items as GitHub issues [#60–#103](https://github.com/wix-private/universal-scheduling-protocol-spec/issues) in `wix-private/universal-scheduling-protocol-spec` (label `v1` for in-scope demo; `v > 1` for GH-054, GH-055, GH-098, GH-099)
- Updated `plans/USP+UCP_implementation_plan.md`: central issue-tracking assumption, replaced all `GH-NNN` placeholders with live issue URLs, removed Task A1–F5 headings in favor of issue-linked track sections, replaced Missing GitHub issues section with issue index table
- Added `scripts/issue_map.json` and `scripts/update_plan_issues.py` for plan ID to issue number mapping

---

## 15/06/26 at 14:12:36 by [Ran Yahalom](mailto:ranya@wix.com)

- Fixed internal step cross-references in `plans/USP+UCP_implementation_plan.md` after calendar renumbering (profile/catalog/availability/checkout tables now point at steps 5, 9, 12, 14, 17; step 9 Fields consumed as table; step 17/20 UCP correlation fields)
- Added UCP conformance gaps G-28–G-34 to §4 matrix with demo issues GH-058–GH-064, §2.3 UCP checkout binding rows, sprint timeline, Definition of Done, and Missing GitHub issues section; moved 3DS/G-21 to out-of-scope via GH-098
- Added § Out of scope — UCP conformance gaps (future) rollup for auth, trusted UI, 3DS, full UCP surface, and related non-demo items
- Created issue drafts under `.github/issue-drafts/` for GH-058–GH-064 (demo in-scope) and GH-098 (UCP conformance gaps out of scope)

---

## 14/06/26 at 16:43:39 by [Ran Yahalom](mailto:ranya@wix.com)

- Added buyer calendar free/busy availability slot filtering to the UCP-Native demo in `plans/USP+UCP_implementation_plan.md`, aligned with linkusp-cli (`flow calendar ask|connect|skip`, `filter_slots_by_busy_times`) and ds-general USP subagent (Scenario 2 calendar gate before `query_availability`): expanded §1 sequence diagram (steps 7-11), detailed steps, demo success criteria, §2.1 discovery and §2.2 architecture, §2.3 normative map (step 1c / §11.2), §3.2 Calendar section, gap G-27, Task A3b, GH-003b, GH-005/Task A5/Definition of Done updates; renumbered checkout/webhook steps 12-21

---

## 14/06/26 at 16:17:19 by [Ran Yahalom](mailto:ranya@wix.com)

- Augmented §1 step-by-step flow in `plans/USP+UCP_implementation_plan.md` with per-step field provenance tables (fields obtained/consumed → later `create_checkout`, `complete_checkout`, and webhook use), traceable to `paid_bookings.json` BookingContext, UCP checkout body, and upstream registry/catalog/availability schemas

---

## 14/06/26 at 16:13:58 by [Ran Yahalom](mailto:ranya@wix.com)

- Fixed relative hyperlinks in `plans/USP+UCP_implementation_plan.md` after move from repo root (`../specification.md`, `../schemas/`, `../openapi/`, `../openrpc/`, `../USP+UCP_readiness.md`, `../.github/issue-drafts/`, same-file `#` anchors); repaired broken GH-055 link in `CHANGE_LOG.md`

---

## 14/06/26 at 14:56:22 by [Ran Yahalom](mailto:ranya@wix.com)

- Removed the client-side `deployment_mode` post-filter step from the demo in `USP+UCP_implementation_plan.md` (sequence diagram, step-by-step flow, discovery path, Tasks A5/C2/C5, GH-005/021/024, out-of-scope, and GH-055 consumer scope); registry-side capability/payment filters via GH-055 are documented as the correct solution when agents need to narrow by deployment mode, payment handlers, or other USP/UCP capabilities

---

## 14/06/26 at 14:47:55 by [Ran Yahalom](mailto:ranya@wix.com)

- Numbered all interaction steps (1-19) in the §1 target demo sequence diagram in `USP+UCP_implementation_plan.md`, added the implicit availability response arrow, and inserted a matching step-by-step explanation list so each chronology step states what happens and why it is required

---

## 14/06/26 at 14:42:29 by [Ran Yahalom](mailto:ranya@wix.com)

- Reinstated spec-aligned **`GET /services/{service_id}`** in `USP+UCP_implementation_plan.md` demo path (after profile, before availability) per USP §6.3 live-catalog requirement; updated sequence diagram, §2.1/§2.2/§7.5 alignment, Tasks A3/A5/C5, GH-003/005/024, Definition of Done; kept `POST /services/list` out of scope

---

## 14/06/26 at 14:33:03 by [Ran Yahalom](mailto:ranya@wix.com)

- Removed `POST /services/list` from demo flow in `USP+UCP_implementation_plan.md` (sequence diagram, architecture, §7.5 map, Tasks A3/A5, GH-003/005); demo uses registry `search_services` + `service_id` then availability only, aligned with linkusp-cli and ds-general agents; added out-of-scope [Merchant-direct catalog discovery](#merchant-direct-catalog-discovery) section for list

---

## 10/06/26 at 18:55:51 by [Ran Yahalom](mailto:ranya@wix.com)

- Trimmed `USP+UCP_implementation_plan.md` gap matrix to in-scope gaps only (removed G-05–G-08, G-11, G-13, G-14, G-16–G-19, G-22–G-25); out-of-scope section no longer references removed matrix IDs

---

## 10/06/26 at 18:49:16 by [Ran Yahalom](mailto:ranya@wix.com)

- Brought `booking.confirmed` webhook with `order_id` into demo scope in `USP+UCP_implementation_plan.md` (USP §7.5 step 8): P0 gap G-12, Tasks D5/C6, GH-056/057, E2E/assertion updates, sequence diagram, removed from out-of-scope conformance list

---

## 10/06/26 at 18:44:07 by [Ran Yahalom](mailto:ranya@wix.com)

- Added plan §2.4 clarifying what "`paid_bookings` extends `checkout`" means (profile `extends` field verification, schema/protocol behavior, agent obligations); expanded Task C3, GH-022, GH-040, demo success criteria, and §2.1 discovery step 5 with explicit checks and `verify_paid_bookings_extends_checkout` example

---

## 10/06/26 at 18:39:45 by [Ran Yahalom](mailto:ranya@wix.com)

- Switched demo discovery path in `USP+UCP_implementation_plan.md` to **`search_services` only**: updated sequence diagram, §2.1 discovery steps, Track B/C/A tasks, Definition of Done, and GH-005/011/013/021/024 to use `ServiceSearchResult` with client-side `business.deployment_mode == ucp_native` post-filter (registry still implements business search for API completeness)

---

## 10/06/26 at 18:19:33 by [Ran Yahalom](mailto:ranya@wix.com)

- Added future-version out-of-scope task and [GH-055](plans/USP+UCP_implementation_plan.md#gh-055-registry-capability-and-payment-search-filters) to `plans/USP+UCP_implementation_plan.md` for registry business/service search filters on indexed profile-derived fields (capabilities, `payment_handlers`, `supports_spt`) with staleness and re-validation on register/update

---

## 10/06/26 at 18:03:28 by [Ran Yahalom](mailto:ranya@wix.com)

- Aligned `USP+UCP_implementation_plan.md` with USP §6 (registry `profile_url` as full document URL, `RegistrationRequest` shape, search filters, no capabilities snapshot), §7.2–7.5 (UCP-Native profile, §7.5 flow mapping, atomic complete), and UCP checkout/idempotency/payment_handlers; added normative protocol alignment map (§2.3), fixed discovery/E2E/registry examples and GH issue acceptance criteria

---

## 10/06/26 at 17:50:43 by [Ran Yahalom](mailto:ranya@wix.com)

- Refactored `USP+UCP_implementation_plan.md` to treat Link platform and USP registry as independent ecosystem components: registry registration moved to Track B operator process (GH-013/014), Track C reworked as registry consumer only (GH-020-024), added ecosystem architecture section, updated gap matrix (G-26), calendar, and GitHub issue specs; Link no longer registers businesses

---

## 10/06/26 at 15:30:17 by [Ran Yahalom](mailto:ranya@wix.com)

- Rewrote `USP+UCP_implementation_plan.md` as a single 2-week UCP-Native demo sprint with six parallel tracks (Link agent, registry, onboarding, Wix usp-impl, UCP+USP extension, Stripe SPT), updated gap matrix, fixed Mermaid diagrams, per-task rationale and steps, GitHub issue anchors (GH-001 through GH-054), and an Out of scope section for holds, mixed cart, order capability, and Standalone Mode

---

## 10/06/26 at 11:43:30 by [Ran Yahalom](mailto:ranya@wix.com)

- Added GitHub issue draft for `usp-impl` Pattern B checkout return relay (`.github/issue-drafts/usp-impl-checkout-return-relay-body.md`) documenting the Wix Headless allowed-redirect-domain failure and why a merchant-owned relay in `usp-impl` is required to serve arbitrary USP agents on redirect checkout

---

## 09/06/26 at 14:46:30 by [Ran Yahalom](mailto:ranya@wix.com)

- Added `USP+UCP_implementation_plan.md`, a phased gap-closure plan mapping all P0-P2 items from the readiness report to concrete tasks across `usp-impl` and `ecom/acp-checkout`, including architecture decisions, acceptance criteria, dependencies, risks, and GA checklist for USP Section 7.7.2

---

## 09/06/26 at 14:40:24 by [Ran Yahalom](mailto:ranya@wix.com)

- Added source-verified `ecom/acp-checkout` section to `USP+UCP_readiness.md` from downloaded codebase at `/Users/ranya/Downloads/ecom-master/server/agentic-checkout`, documenting UCP REST/MCP lifecycle, Google Pay-only payment handlers, and Stripe delegated-checkout as a separate webhook path (not UCP SPT)
- Revised Stripe SPT and UCP checkout readiness estimates and gap tables to reflect that no Stripe UCP payment handler or `paid_bookings` integration exists in either `acp-checkout` or `usp-impl`

---

## 09/06/26 at 14:20:38 by [Ran Yahalom](mailto:ranya@wix.com)

- Replaced inferred `usp-impl` architecture in `USP+UCP_readiness.md` with verified source-level analysis from downloaded codebase at `/Users/ranya/Downloads/wix-vmr-repo-master/usp-impl`, including handler layout, RPC scope, payment path (`ChannelType.WEB` + redirect), and documented source bugs (`GetBooking` empty query, `ConfirmPayment` gaps)
- Cross-referenced internal `usp-implemented-methods-gap-report.md` to confirm UCP-Native blockers (no holds, no UCP types, no SPT) and updated readiness estimates

---

## 09/06/26 at 14:14:49 by [Ran Yahalom](mailto:ranya@wix.com)

- Added inferred source-level architecture section to `USP+UCP_readiness.md` for Wix `usp-impl`, mapping RPC operations (`ListServices`, `CreateBooking`, etc.) and deployable artifact `com.wixpress.usp.impl.usp-impl` from live `x-wix-responded-by` headers after GitHub MCP remained unavailable for the private repo
- Expanded endpoint matrix and spec-divergence tables with black-box findings (404 routes, auth-gated operations, ID codecs, error model) so implementers have operation-level detail without source checkout

---

## 09/06/26 at 14:05:14 by [Ran Yahalom](mailto:ranya@wix.com)

- Revised `USP+UCP_readiness.md` after analyzing Wix `usp-impl` via live deployments (`hvac-koby`, `rolucknow.com`) and `linkusp-cli` integration, since GitHub MCP could not read the private `wix-vmr-repo` repository
- Documented that `usp-impl` already ships Standalone Mode USP (catalog, availability, create-booking with redirect payment) while UCP-Native `paid_bookings`, merged `/.well-known/ucp` profile, Stripe `payment_handlers`, and atomic SPT checkout remain gaps

---

## 09/06/26 at 13:41:59 by [Ran Yahalom](mailto:ranya@wix.com)

- Added `USP+UCP_readiness.md` gap analysis report evaluating Wix readiness to support USP as a UCP extension with Stripe Shared Payment Tokens, so implementers can see which components exist versus what still blocks end-to-end paid booking checkout
- Mapped required USP Section 7 capabilities (catalog, availability, bookings, paid_bookings) and UCP payment architecture requirements against Wix's `ecom` agentic-checkout module structure and public Bookings/ecom APIs

---

## 27/05/26 at 17:48:19 by [itays](mailto:itays@wix.com)

- Restructured Overview tab sidebar to match UCP's pattern (8 items vs previous 4) — moved Specification overview, Security, Extensions, and Playground from the Specification tab into Overview so the home page sidebar has comparable depth to ucp.dev

---

## 27/05/26 at 17:41:04 by [itays](mailto:itays@wix.com)

- Redesigned site aesthetics with a Swiss Precision / Technical Authority design system — new typography (Instrument Serif for display, DM Sans for body, DM Mono for code), refined color tokens with teal accent, and light editorial layout to replace the generic AI-generated look
- Updated home page template with section eyebrow labels (e.g., "The Problem", "Verticals", "Workflow", "Architecture") for a more editorial, magazine-like structure matching the new CSS design tokens
- Trimmed verbose code examples in the "See It in Action" section to keep the page scannable while still showing real API payloads
- Sidebar now always visible on home page (hero renders within content grid alongside sidebar, not above it)

---

## 27/05/26 at 14:45:02 by [itays](mailto:itays@wix.com)

- Restructured site navigation from 9 top tabs to 3 (Home, Overview, Specification) to match UCP's navigation pattern — consolidates Deployment Modes, Transport Bindings, Security, Extensions, and Playground under the Specification tab with a deep sidebar, and moves Roadmap under Overview
- Restored left sidebar navigation on the Playground page (was previously hidden) so users can navigate the site without leaving the playground, matching UCP's playground layout
- Removed CSS rules that force-hid the sidebar and forced full-width layout on the playground page

---

## 26/05/26 at 18:20:05 by [itays](mailto:itays@wix.com)

- Added `render.yaml` Render Blueprint spec for deploying the USP website as a static site on Render's global CDN, with PR preview environments, cache headers for assets and scenario data, security headers, convenience redirects (`/spec` → `/specification/`, `/github` → repo), and a build filter scoped to docs-related paths only

---

## 26/05/26 at 17:57:27 by [itays](mailto:itays@wix.com)

- Built interactive USP Playground at `/playground/` — server-rendered Jinja2 template (`overrides/playground.html`) with 8-step scheduling lifecycle simulator (Discovery, Negotiation, Browse Services, Check Availability, Hold Slot, Create Booking, Payment, Manage Booking), modeled after the UCP playground at ucp.dev
- Each step has a split layout: configuration panel (scenario dropdown + run button) and code panel (method badge, endpoint path, syntax-highlighted JSON response with copy button)
- Created `playground-controller.js` — lightweight vanilla JS controller handling step switching, scenario loading from JSON files, mock request execution with simulated latency, copy-to-clipboard, manage step method/path updates, and mode/transport toggle state
- Added step navigation pills, mode toggle (Standalone/UCP-Native), transport toggle (REST/MCP/A2A/ESP), and Next/Back navigation between steps
- Extended `playground.css` with template-specific styles: step pills, split layout grid, config panel, code panel, method badges (GET/POST/PATCH/DELETE), status badges, select dropdowns, syntax highlighting tokens, and responsive breakpoints
- Added Playground to `mkdocs.yml` navigation between Extensions and Roadmap

---

## 26/05/26 at 17:32:29 by [itays](mailto:itays@wix.com)

- Created `playground/src/playground.js` — core USP Playground engine implementing the 8-step scheduling lifecycle state machine (discovery, negotiation, browse, availability, hold, book, payment, manage) plus waitlist bonus step, with mode toggle (Standalone/UCP-Native), transport toggle (REST/MCP/A2A/ESP), scenario selection, mock request execution with simulated latency, step navigation with visibility filtering, and full DOM rendering of the playground UI
- Created `playground/src/code-editor.js` — lightweight JSON display module with regex-based syntax highlighting (keys=gray, strings=teal, numbers=amber, booleans=green, null=red), contentEditable support for request editing, getValue/getRawText parsing, and clipboard copy with fallback
- Created `playground/src/response-viewer.js` — read-only response display component with HTTP status badge (color-coded 2xx/4xx/5xx), simulated timing display, collapsible sections for large responses (30+ lines), and copy button
- Created `playground/src/transport-formatter.js` — transport binding converter that transforms REST request configurations into MCP (JSON-RPC 2.0 `tools/call` envelope with `_meta.usp`), A2A (`tasks/send` with DataPart), and ESP (iframe embed snippet with `postMessage` protocol) formats, with full method-to-tool-name and method-to-operation-type mapping tables

---

## 26/05/26 at 17:29:33 by [itays](mailto:itays@wix.com)

- Created 10 mock scenario JSON files in `playground/scenarios/` for the USP interactive playground simulator, covering the full scheduling lifecycle for "Downtown Wellness Spa" (business ID `biz_downtown_spa`) with 4 services across all USP verticals (appointment, group, reservation, rental)
- `business-profile.json`: 3 scenarios (standard, full, minimal) for `/.well-known/usp` business profile responses with varying capability sets, including waitlist/holds toggle and multi-location support
- `platform-profile.json`: 2 scenarios (standard, advanced) for platform capability negotiation with transport preferences and signing keys
- `services.json`: 4 scenarios (happy_path, filtered_wellness, search_massage, empty_results) with full catalog data for all 4 services including staff/room/equipment resources, policies, media, ratings, and availability hints
- `availability.json`: 5 scenarios (available_slots, limited_availability, resource_specific, no_availability, range_too_wide) with realistic time slots across 2026-03-15 to 2026-03-17 including peak/off-peak pricing and resource assignments
- `holds.json`: 4 scenarios (hold_granted, slot_unavailable, hold_limit_exceeded, release_hold) covering the hold lifecycle with proper TTL and error responses
- `bookings.json`: 5 scenarios (instant_confirmation, payment_required, manual_confirmation, validation_error, slot_expired) covering auto/manual confirmation, payment actions with PaymentContext, and error cases (422/409)
- `payment.json`: 3 scenarios (payment_success, payment_failed, deposit_flow) for payment completion including deposit-based spa suite reservations
- `manage.json`: 6 scenarios (view_booking, update_booking, cancel_booking, cancel_with_fee, reschedule_booking, reschedule_limit_reached) for the full booking management lifecycle including late cancellation fees and reschedule limits
- `webhooks.json`: 5 webhook payloads (booking.confirmed, booking.canceled, booking.rescheduled, booking.reminder, booking.completed) conforming to the BookingEvent schema
- `waitlist.json`: 4 scenarios (join_waitlist, offer_received, accept_offer, decline_offer) covering the waitlist lifecycle with offer expiration and conversion to booking
- All data uses consistent IDs across files (e.g., `slot_mass_0315_0900` appears in availability, holds, and bookings), amounts in minor currency units (cents), RFC 3339 timestamps, and the USP envelope pattern with `version: "2026-02-21"`

---

## 26/05/26 at 17:28:03 by [itays](mailto:itays@wix.com)

- Created comprehensive playground CSS (`playground/styles/playground.css`) with full design system: layout containers, horizontal stepper with numbered dots and connector lines (active/completed/upcoming/optional states), mode pill toggle and transport dropdown, request/response code panes with dark background and syntax highlighting classes, method badges (GET/POST/PATCH/DELETE), status badges (2xx/3xx/4xx/5xx), buttons with loading spinner state, navigation footer, negotiation capability grid, manage tab bar, field annotations, callouts, and utility classes — all prefixed with `pg-` to avoid conflicts with the main site CSS
- Created playground Jinja2 template (`overrides/playground.html`) extending `main.html` with sidebar/TOC hidden via `{% block sidebars %}`, OG/Twitter meta tags for social sharing, and deferred loading of playground CSS and JS module — keeps the top nav bar and footer from the main site
- Created playground MkDocs entry point (`playground/index.md`) with front matter specifying the custom template, SEO metadata (title, description, keywords), and hidden navigation/toc/footer sections
- All three files use the existing USP teal color palette (`#0d9488` family) and match the dark code-editor aesthetic established in `extra.css`, with responsive breakpoints at 1024px, 768px, and 480px plus print styles

---

## 26/05/26 at 17:20:43 by [itays](mailto:itays@wix.com)

- Created `playground/` directory and drafted comprehensive playground specification (`playground/SPEC.md`) modeled after the UCP playground at ucp.dev — an 8-step browser-based interactive simulator covering the full USP scheduling lifecycle (discovery, negotiation, browse, availability, hold, book, payment, manage) with scenario dropdowns, transport binding toggle (REST/MCP/A2A/ESP), deployment mode toggle (Standalone/UCP-Native), schema validation, and a waitlist extension bonus step

---

## 26/05/26 at 16:53:04 by [itays](mailto:itays@wix.com)

- Built full USP website using Material for MkDocs to replace the empty placeholder at usp.base44.app, matching the quality level of the UCP website (ucp.dev) with a teal color palette (#0D9488) distinct from UCP's blue
- Created custom homepage template (`overrides/home.html`) with 11 sections: hero, stats, verticals, design principles, how-it-works flow, interactive code examples, deployment modes, transport bindings, ecosystem, partners placeholder, and CTA footer
- Created 19 content pages derived from the 430KB `specification.md`: core concepts, getting started, security, extensions, roadmap, specification overview, service catalog, availability, booking lifecycle, discovery registry, deployment modes (index, UCP-Native, Standalone), transport bindings (index, REST, MCP, A2A, ESP)
- Added comprehensive SEO: Open Graph meta tags, Twitter Cards, JSON-LD structured data (WebSite + SoftwareSourceCode + Organization on homepage, TechArticle on inner pages), canonical URLs, robots.txt, sitemap.xml, keywords meta tags
- Created `llms.txt` and `llms-full.txt` following the emerging standard for LLM-readable site descriptions, providing structured protocol summaries for AI consumption
- Generated social card image (1200x630 SVG + PNG) with dark gradient background, calendar-clock icon, protocol title/tagline, code snippet preview, transport binding labels, and vertical pills for use in OG/Twitter social sharing
- Added custom CSS design system (`extra.css`, 615 lines) with CSS variables, dark mode support, responsive grid layouts, card styles, and homepage section styling
- Added Jinja2 template override (`overrides/main.html`) for global `<head>` meta tags with safe `{% if page %}` guard to handle 404.html rendering where `page` is None
- Created `mkdocs.yml` configuration with Material theme, Inter/JetBrains Mono fonts, navigation tabs, code copy/annotate, search suggestions, cookie consent, and minify plugin

---

## 28/03/26 at 00:47:53 by [Ran Yahalom](mailto:ranya@wix.com)

- Added `$defs/WaitlistEvent` in [
  `schemas/webhook_event.json`](schemas/webhook_event.json), REST
  `webhooks.waitlistEvent` in [`openapi/usp-rest.json`](openapi/usp-rest.json),
  and `WaitlistWebhookEvent` in [`openrpc/usp-mcp.json`](openrpc/usp-mcp.json)
  so waitlist webhooks match booking/catalog machine-readable artifacts;
  expanded [specification.md](specification.md) §11.1.5 and §9.2.3 accordingly.
- Extended `BookingEvent` with `booking.service_started` and
  `booking.service_updated`, aligned §5.4.1 and §5.5.3 prose, and fixed the
  §5.5.3 `businesses **MAY**` typo so service-delivery events are first-class
  booking webhook events.

---

## 29/03/26 at 14:34:01 by [roysha-wix](mailto:62389977+roysha-wix@users.noreply.github.com)

- Fixed missing space in §11.1 capability declaration (`extends\`...` → `extends \`...`) per gap 10.1
- Added request/response schema tables for all 6 waitlist operations in §11.1.3, including the new `POST /waitlist/list` pagination endpoint (gap 10.5, 10.12), with cross-reference hyperlinks to OpenAPI and OpenRPC binding files
- Clarified offer acceptance flow: accepting atomically creates a booking, response includes `{entry, booking}`, payment follows normal flow (gap 10.7)
- Added §11.1.6 with waitlist-specific error codes (`waitlist_full`, `offer_expired`, `entry_not_found`, `offer_already_accepted`) and explicit `messages[]` pattern reference (gap 10.4, 10.6), mirrored in §9.4 error code table
- Added introductory note to §12 explaining webhook URL configuration and ESP exclusion (gap 10.8), and split the operation reference into visually grouped sub-tables: Catalog, Availability, Booking, Extension (Waitlist), and Discovery (gap 10.10)
- Added `POST /waitlist/list` endpoint to `openapi/usp-rest.json` with request filtering (service_id, status) and cursor-based pagination
- Added `usp_waitlist_list` method to `openrpc/usp-mcp.json` with matching parameters and result schema
- Added `POST /waitlist/list` / `usp_waitlist_list` row to the §9.2.1 transport mapping table

---

## 29/03/26 at 11:21:16 by [roysha-wix](mailto:62389977+roysha-wix@users.noreply.github.com)

- Merged origin/master into gaps-9-security to incorporate Ranya's webhook formalization (schemas/webhook_event.json, OpenAPI webhooks, OpenRPC webhook refs), paid_bookings enhancements, ACP booking extension, and ProfileCapabilityEntry — all complementary to the security gap fixes on this branch
- Resolved CHANGE_LOG.md conflict (both sides prepended entries; kept both in chronological order)
- Verified alignment: webhook payloads chain through Booking → Buyer → BuyerConsent, signature error codes present in both bindings, all component schemas use thin $refs, no duplicate keys, and webhook sections cross-reference §10.1.1 signing requirements

---

## 28/03/26 at 00:47:53 by [Ran Yahalom](mailto:ranya@wix.com)

- Added `$defs/WaitlistEvent` in [
  `schemas/webhook_event.json`](schemas/webhook_event.json), REST
  `webhooks.waitlistEvent` in [`openapi/usp-rest.json`](openapi/usp-rest.json),
  and `WaitlistWebhookEvent` in [`openrpc/usp-mcp.json`](openrpc/usp-mcp.json)
  so waitlist webhooks match booking/catalog machine-readable artifacts;
  expanded [specification.md](specification.md) §11.1.5 and §9.2.3 accordingly.
- Extended `BookingEvent` with `booking.service_started` and
  `booking.service_updated`, aligned §5.4.1 and §5.5.3 prose, and fixed the
  §5.5.3 `businesses **MAY**` typo so service-delivery events are first-class
  booking webhook events.

---

## 27/03/26 at 23:35:39 by [Ran Yahalom](mailto:ranya@wix.com)

- Closed `gaps.md` §1–2 items in [specification.md](specification.md): §2.3
  profile hosting, graceful degradation (`continue_url`), and
  `supported_versions`; §2.4 transport-bindings terminology, capability field
  table, extension `requires` version rules; §2.5 governance model and
  spec/schema URL origin binding; §2.7 error-handling overview and idempotency
  forward refs; expanded §2.1.3 credential-provider rationale; fixed §2.1.1/§2.6
  formatting (spacing, blockquote).
- Added [`$defs/ProfileCapabilityEntry`](schemas/usp.json) in [
  `schemas/usp.json`](schemas/usp.json) (requires `spec` and `schema` in
  business/platform profiles, aligned with UCP); wired `business_schema` and
  `platform_schema` capability arrays to it; updated §8.2.1 profile field tables
  for consistency.
- Exposed `ProfileCapabilityEntry` in [
  `openapi/usp-rest.json`](openapi/usp-rest.json) and [
  `openrpc/usp-mcp.json`](openrpc/usp-mcp.json) via thin `$ref`s to canonical
  `$defs`.

---

## 27/03/26 at 23:18:18 by [Ran Yahalom](mailto:ranya@wix.com)

- Aligned §8.5.6 and §8.6.4 ACP booking extension with the Agentic Commerce
  Protocol: extension uses `extends` as a JSONPath array targeting
  `$.CheckoutSession.booking`, replaces the non-normative `extensions` bag with
  a named `booking` field, and fixes line-item / `totals` / currency examples so
  implementers map `payment_context` to real ACP `CheckoutSession` shapes.
- Documented PSP vs ACP identifiers for `confirm-payment` (`transaction_id` from
  PSP or handler; `order_reference` from `order.id` or `order.order_number`),
  deposit behaviour under ACP, empty `fulfillment_options` for scheduling, ACP
  payment sub-steps (handlers, delegate payment, `complete`, 3DS), and slot
  subset vs `SlotReference`.
- Added machine-readable [
  `schemas/acp_booking_extension.json`](schemas/acp_booking_extension.json) for
  the extension payload and pointed the spec’s `schema` URL to
  `https://usp.dev/schemas/acp_booking_extension.json`.

---

## 27/03/26 at 22:57:33 by [Ran Yahalom](mailto:ranya@wix.com)

- Addressed Standalone Mode gaps from `gaps.md` §7: expanded §8.5 with
  confirm-payment error codes (§9.4), buyer-side escalation, payment action
  expiry and abandonment, `checkout_systems` design note vs UCP
  `payment_handlers`, `continue_url` HTTPS rules, and fraud-signal delegation;
  renamed §8.5.4 to embedded/generic flow and merged lifecycle prose.
- Added optional `tax_amount` to [`schemas/booking.json`](schemas/booking.json)
  `$defs/PaymentContext` and tightened `Action.continue_url` description;
  updated Payment Context table in [specification.md](specification.md) §8.5.2.
- Restructured end-to-end flows: §7.7 and §8.6 now share a consistent preamble +
  JSON pattern; new §8.6.2–8.6.5 (Embedded, Redirect, ACP, Deposit) and new §8.7
  Payment Path Comparison across deployment modes; updated TOC and cross-links
  to [`schemas/`](schemas/), [`openapi/usp-rest.json`](openapi/usp-rest.json),
  and [`openrpc/usp-mcp.json`](openrpc/usp-mcp.json) where relevant.
- Fixed broken reading-guidance blockquote in §7.3.

---

## 27/03/26 at 14:08:18 by [Ran Yahalom](mailto:ranya@wix.com)

- Implemented UCP-Native Mode §7 gap fixes: `BookingContext.booking_status`
  derivation rules vs full `Booking.status`, `update_checkout`/`get_checkout`
  guidance, escalation/`continue_url`, cancel checkout semantics, `expires_at`
  vs hold, UCP-aligned `totals`/`links` in checkout example, `actions` on
  `BookingContext`, `confirmation_mode` manual vs atomicity, mixed cart note in
  §7.2, webhook `order_id` and delivery caveats, and `price_mismatch` in §9.4.
- Added machine-validatable webhooks:
  new [schemas/webhook_event.json](schemas/webhook_event.json) (`BookingEvent`,
  `CatalogEvent`), `webhooks` in [openapi/usp-rest.json](openapi/usp-rest.json),
  `BookingWebhookEvent` / `CatalogWebhookEvent` component `$ref`s
  in [openrpc/usp-mcp.json](openrpc/usp-mcp.json); reconciled §5.4.1 / §9.2.3
  with `event_id`, `order_id`, and `data` field naming; `BookingContextAction`
  and updated `booking_status`
  in [schemas/paid_bookings.json](schemas/paid_bookings.json).

---

## 26/03/26 at 17:54:46 by [roysha-wix](mailto:62389977+roysha-wix@users.noreply.github.com)

- Fixed security gaps 9.1–9.20 from issue #20, aligning §10 with UCP security patterns
- **Gap 9.1**: Added threat-model framing to §10.1.1 listing attacks that HTTP Message Signatures mitigate (impersonation, tampering, replay, method/endpoint confusion)
- **Gap 9.2**: Added ECDSA raw `r||s` encoding guidance — signatures MUST use fixed-width raw encoding, not ASN.1/DER
- **Gap 9.3**: Deprecated RSA-PSS algorithm — MUST NOT be used in UCP-Native mode, transition period ending 2027-12-31 for Standalone mode
- **Gap 9.4**: Increased key rotation grace period from 24 hours to 7 days, added 90-day rotation cadence and key compromise response guidance
- **Gap 9.5**: Added SHOULD-level response signing recommendation for booking confirmations and pricing data
- **Gap 9.6**: Added replay protection requirements — `@created` timestamp check (5-minute window) combined with idempotency key/event ID tracking
- **Gap 9.7**: Added intermediary warning that proxies MUST NOT re-serialize JSON bodies (would break Content-Digest)
- **Gap 9.8**: Added `@authority` and `@path` to covered components (replacing `@target-uri`), preventing cross-host relay attacks
- **Gap 9.9**: Aligned buyer consent categories with UCP — replaced `data_sharing` with `sale_of_data`, added `preferences`, retained `health_data` as USP extension
- **Gap 9.10**: Added declarative consent clarification — protocol communicates consent but does not enforce it
- **Gap 9.11**: Moved `consent` inside `buyer` object to match UCP's `checkout.buyer.consent` pattern; updated schemas/booking.json, openapi/usp-rest.json, openrpc/usp-mcp.json
- **Gap 9.12**: Added RFC 8414 OAuth Server Metadata Discovery requirement to §10.2.4
- **Gap 9.13**: Added CSRF protection via `state` parameter in authorization requests per RFC 6749 §10.12
- **Gap 9.14**: Added client authentication requirement — platforms MUST use `client_id`/`client_secret` via HTTP Basic Auth [RFC 7617]
- **Gap 9.15**: Added recursive token revocation — revoking refresh_token MUST also revoke associated access_tokens
- **Gap 9.16**: Added UCP scope mapping note for reverse-DNS naming convention in UCP-Native mode
- **Gap 9.17**: Added account creation flow requirement — authorization endpoint MUST support both login and registration
- **Gap 9.18**: Added SHOULD-level recommendation for OpenID RISC Profile 1.0 support for security event signaling
- **Gap 9.19**: Added §10.1.5 Sensitive Credential Handling — raw payment credentials MUST NOT traverse USP APIs
- **Gap 9.20**: Added signature verification error codes table (signature_missing, signature_invalid, key_not_found, digest_mismatch, signature_expired) to spec, OpenAPI, and OpenRPC

---

## 26/03/26 at 16:06:42 by [roysha-wix](mailto:62389977+roysha-wix@users.noreply.github.com)

- Fixed transport binding gaps 8.1–8.14 from issue #20, aligning §9 with UCP patterns
- **Gap 8.1**: Adopted `structuredContent`/`content` dual-envelope pattern for MCP responses so AI clients get both typed data and human-readable text
- **Gap 8.2**: Updated MCP binding to use `tools/call` wrapper instead of raw JSON-RPC methods, matching the MCP specification
- **Gap 8.3**: Added `idempotency_key` to `_meta.usp` for state-modifying MCP operations, providing parity with REST `Idempotency-Key` header
- **Gap 8.4**: Fixed MCP error model — business outcome errors now return in `result.structuredContent.messages[]`, not as JSON-RPC `error`; only protocol errors use JSON-RPC `error`
- **Gap 8.5**: Resolved JSON-RPC error code collisions — removed JSON-RPC codes from business errors table (they use `messages[]` now), assigned unique codes to all protocol errors
- **Gap 8.6**: Expanded A2A binding with Agent Card specification (§9.3.3), DataPart conventions (§9.3.4), and session management (§9.3.5)
- **Gap 8.7**: Added `403 Forbidden`, `503 Service Unavailable` to REST status code table; added `ServiceUnavailable` response component to OpenAPI; added `service_unavailable` protocol error
- **Gap 8.8**: Added `201 Created` to REST status code table; changed OpenAPI creation endpoints (bookings, holds, registry, waitlist, feed subscriptions) from 200 to 201
- **Gap 8.9**: Added §9.1.3 Discovery cross-referencing §8.2 business profiles and `USP-Agent` header
- **Gap 8.10**: Added §9.1.4 Request Signing for state-modifying REST requests using RFC 9421; added `signing_keys` to PlatformProfile in `schemas/profile.json`
- **Gap 8.11**: Added conformance subsections to all transport bindings: §9.1.5 REST, §9.2.4 MCP, §9.3.6 A2A, §9.5.6 ESP
- **Gap 8.12**: Fixed missing spaces between backtick-delimited `Idempotency-Key` and following words in §9.1.1
- **Gap 8.13**: Added ESP error handling (§9.5.5) with `esp.error`, `esp.cancel`, `esp.timeout` messages and well-known error codes
- **Gap 8.14**: Expanded webhook notifications (§9.2.3) with at-least-once delivery semantics, retry policy, acknowledgment requirements, URL registration, and signature verification; added `webhook_url` to PlatformProfile in `schemas/profile.json`
- Updated `openrpc/usp-mcp.json`: renamed `USPError` to `USPProtocolError` with only protocol error codes, wrapped all method results in `structuredContent` envelope, added `idempotency_key` to state-modifying methods, updated `info.description` for `tools/call`
- Updated `openapi/usp-rest.json`: added `ServiceUnavailable` (503) response to all endpoints, changed creation endpoints to return 201

---

## 26/03/26 at 13:53:40 by [Ran Yahalom](mailto:ranya@wix.com)

- Finished the zero-duplication OpenAPI/OpenRPC plan: documented
  in [specification.md](specification.md) §9.1 and §9.2 that [
  `schemas/`](schemas/) holds authoritative `$defs`, bindings use relative
  `$ref`s and are not self-contained until bundled, and pointed to
  Redocly/Swagger CLI for bundling.

---

## 26/03/26 at 13:50:39 by [Ran Yahalom](mailto:ranya@wix.com)

- Documented agent workflow in [AGENTS.md](AGENTS.md) so JSON Schema definitions
  stay single-sourced under `schemas/` and OpenAPI/OpenRPC bindings use thin
  external `$ref`s only, preventing drift from duplicated inline bodies and
  pointing to bundling when a self-contained file is needed.

---

## 26/03/26 at 11:24:35 by [Ran Yahalom](mailto:ranya@wix.com)

- Closed Discovery Registry gaps (§6): field tables for business and service
  search; MUST-level rule that at least one search filter is present;
  cross-references to §9.4 for errors; optional `context` (`locale`,
  `currency`); `pricing` (catalog-aligned) and `last_indexed_at` on service
  hits; conditional `location` and optional `description` on registration;
  clarified `usp` envelope as the registry’s own capability declaration;
  indexing guidance (feed subscriptions, 24h fallback, non-authoritative
  results).
- Added registry lifecycle operations `GET` / `PUT` / `DELETE`
  `/registry/businesses/{id}` (§6.4–6.6), renumbered Registry Governance to
  §6.7, updated Table of Contents, and documented six new MCP methods in §9.2.1.
- Added machine-readable [schemas/registry.json](schemas/registry.json) with
  `$defs` for registration, search requests, and service search results (
  including `$ref` to catalog `Pricing`).
- Updated [openapi/usp-rest.json](openapi/usp-rest.json): aligned `profile_url`
  and `deployment_mode` with the spec; `RegistryContext`; revised
  `RegistryEntry` and `ServiceSearchResult` (`pricing`, `last_indexed_at`);
  optional `messages` on registry responses; `GET`/`PUT`/`DELETE` under
  `/registry/businesses/{id}`.
- Updated [openrpc/usp-mcp.json](openrpc/usp-mcp.json): `usp_registry_*`
  methods, registry component schemas, and `PaginationRequest` for registry
  search params.

---

## 25/03/26 at 17:11:29 by [kobym707](mailto:kobym@wix.com)

- Adopted strict slot-per-resource model (§4.1, §5.3.1): a slot now represents a
  specific bookable combination of time window + assigned resources, eliminating
  the race condition and undefined behaviour caused by a separate `resource_id`
  selection at booking time.
- Added "One slot per resource combination" normative note to §4.1 (TimeSlot):
  when the same time window is available for multiple resources, the business
  MUST return a separate slot per option, each with its specific resource in the
  `resources` array.
- Expanded `resources` field description in §4.1 to make clear that each slot
  carries at most one resource of each type and that picking a slot is
  equivalent to picking both the time and the resource.
- Removed `resource_id` from the CreateBookingRequest field table (§5.3.1) —
  resource selection is now fully encoded in `slot_id`, making the field
  redundant.
- Updated all three `POST /bookings` request examples (§5.3.1) to remove
  `resource_id`, keeping the examples in sync with the new schema.
- Added introductory note to §5.3.1 explaining that resource selection happens
  at availability query time (via slot choice), not at booking time.

---

## 25/03/26 at 12:17:34 by [kobym707](mailto:kobym@wix.com)

- Added `> **JSON Schema:** [/$defs/TypeName](schemas/file.json)` blockquotes to
  every schema-describing and operation section in `specification.md` that was
  missing one: §3.12.1, §3.12.3, §3.12.4, §4.1, §4.2, §4.3.1, §4.3.2,
  §5.3.1–5.3.7, §7.4, §8.5.2, §8.5.5 — making it easy for implementors to jump
  directly to the machine-readable `$defs` entry for any section.
- Updated all 8 existing `> **JSON Schema:**` blockquotes from bare file links
  to specific `/$defs/TypeName` links (§3.3, §4 availability intro, §5.2,
  §5.5.2, §8.5.1, §10.1.1 signing keys, §11.1.1, §11.2.3), consistent with the
  new pattern.

---

## 25/03/26 at 12:08:27 by [kobym707](mailto:kobym@wix.com)

- Added `links[]` to the `Service` schema (§3.3, `catalog.json`, OpenAPI,
  OpenRPC): service-specific policy links (cancellation policy, waiver, ToS)
  belong at the service level so platforms can surface them during the booking
  flow before the buyer confirms, not after.
- Added `booking_url` to the `Booking` schema (§5.2, `booking.json`, OpenAPI,
  OpenRPC): stable permalink for the buyer to view and manage their booking,
  used in confirmation emails, calendar events, and buyer portals.
- Added `messages[]` to the `Booking` schema (§5.2, `booking.json`, OpenAPI,
  OpenRPC): soft informational messages from the business about booking state (
  e.g., manual confirmation pending), consistent with how `messages[]` is
  already documented on hold responses.
- Added `dispute` field and `Dispute` schema to the `Booking` object (§5.5.2,
  `booking.json`, OpenAPI, OpenRPC): formalizes the dispute lifecycle with
  structured `status`, `reason`, `opened_at`, and `resolved_at` fields;
  clarifies that opening a dispute does NOT change `payment.status`.
- Added `tax_amount` to `BookingPayment` (§8.5.1, `booking.json`, OpenAPI,
  OpenRPC) and clarified that `amount` is the pre-tax service fee: resolves
  ambiguity about whether pricing amounts are tax-inclusive.
- Added "Booking Expiry" behavioral rules to §5.2: business MUST transition to
  `canceled`, SHOULD send `booking.canceled` webhook, MUST keep expired booking
  retrievable via GET, and MUST release the slot.
- Added idempotency note to §5.3.1: `hold_id` serves as a natural idempotency
  key; second POST with same `hold_id` MUST return existing booking; no-hold
  flows SHOULD use `Idempotency-Key` header.
- Expanded §5.3.3 Update Booking with request field table and response
  description: documents the three mutable fields (`buyer`, `recipient`,
  `notes`) and partial-update semantics.
- Expanded §5.3.4 Confirm Booking with request field table, eligible status
  guidance, and response example.
- Expanded §5.3.5 Cancel Booking with request field table (`reason`,
  `canceled_by`), eligible statuses, slot-release requirement, and cancel/refund
  response example.
- Expanded §5.3.6 Reschedule Booking with eligible status guidance,
  booking-ID-preservation note, response description, and price-change handling
  for peak/off-peak rescheduling.
- Added webhook payload schema and example to §5.4.1 Booking Webhooks, mirroring
  the existing §5.4.2 Catalog Webhooks structure.
- Added single-service design note to §5 intro (Gap 4.14): USP bookings are
  single-service by design; multi-service coordination is handled by the
  platform issuing separate bookings.

---

## 24/03/26 at 23:03:02 by [kobym707](mailto:kobym@wix.com)

- Added non-transactional disclaimer to §4.1 (Gap 3.1): slots are advisory-only;
  platforms MUST NOT treat availability responses as booking commitments, and
  businesses MUST validate slot availability at booking creation time regardless
  of holds.
- Added `location_id` to §4.3.1 request field table (Gap 3.2): was already in
  OpenAPI/OpenRPC but absent from the normative prose; now synced across all
  artifacts.
- Added date range guidance to §4.3.1 (Gap 3.3): platforms SHOULD query at most
  7 calendar days per request; businesses MAY reject wider ranges with HTTP 422
  and error code `range_too_wide`.
- Added optional `messages` array to §4.3.1 query response (Gap 3.4): consistent
  with hold response; enables businesses to return soft warnings (e.g., holiday
  hours, reduced staffing) alongside slots.
- Added single-service design note to §4.3.1 (Gap 3.5): documents the deliberate
  single-service-per-query design choice and notes that a future multi-service
  availability extension is under consideration.
- Added §9.1.2 Pagination to the REST Binding section (Gap 3.6): defines shared
  cursor semantics (opaque cursors, 60s minimum TTL, ordering note, default page
  sizes) used by all paginated USP operations; added cross-reference in §4.3.1;
  noted the intentional `next_cursor` vs `cursor` distinction between the feed
  and all other endpoints in §3.1.
- Added `spots: 1` to §4.3.3 release response example (Gap 3.7): release
  response now matches hold response schema for consistency.
- Added "Concurrent Holds" subsection to §4.2 (Gap 3.8): normative MUST/MUST NOT
  rules for concurrent hold behavior by service type — `appointment` allows one
  active hold maximum, `group`/`reservation` allows multiple up to remaining
  capacity, `rental` treats resource overlap as unavailable.
- Added `opening_hours[]` field table to §4.3.1 response (Gap 3.9): defines
  `day_of_week` (lowercase day names), `opens` (HH:MM), `closes` (HH:MM), and
  clarifies the field reflects regular hours only; special closures are surfaced
  via absent slots. Fixed OpenRPC `usp_availability_query` result to include
  full item schema (was previously `"type": "array"` with no properties).
- Added optional `locale` (BCP 47) parameter to §4.3.1 (Gap 3.10): allows
  platforms to request locale-specific human-readable content; narrowed UCP's
  full context/signals suggestion to only the scheduling-relevant subset.
- Added `locale`, `cursor`, and `limit` parameters to `usp_availability_query`
  in `openrpc/usp-mcp.json` and `openapi/usp-rest.json` to keep all artifacts in
  sync.
- Expanded `Pagination` schema descriptions in both `usp-rest.json` and
  `usp-mcp.json`.

## 24/03/26 at 13:47:43 by [kobym707](mailto:kobym@wix.com)

- **Gap 2.10:** Added optional `tags` (array of strings) and `metadata` (
  freeform object) to Service schema, aligning with UCP. Enables freeform
  categorization and business-defined custom data.
- **Gap 2.11:** Fixed space-in-URL typo in feed example (
  `cursor=2026-03-10T08: 00: 00Z`). Changed feed cursor examples to opaque
  values (`crs_...`) since the spec says cursors are opaque. Removed
  `format: date-time` from feed cursor parameter in OpenAPI.
- **Gap 2.12:** Standardized feed pagination from `next_cursor` to `cursor` to
  match the `Pagination` component used by `/services/list`. Both endpoints now
  use `{cursor, has_more}`.
- **Gap 2.13:** Added §3.13 Catalog Conformance Requirements with 10 numbered
  MUST/SHOULD requirements for `dev.usp.services.catalog` implementations.
- **Gap 2.14:** Already addressed — formal filter table was added in the earlier
  catalog_search alignment commit.
- **Gap 2.15:** Added optional `categories` array (multi-taxonomy,
  `{value, taxonomy}` entries) to Service schema alongside existing `category`.
  If both present, `categories` is authoritative. Aligns with UCP.
- **Gap 2.16:** Added optional `handle` (URL-friendly slug) and `url` (canonical
  page) fields to Service schema. Aligns with UCP.
- **Gap 2.17:** Added `status` field to Service schema with values `active` (
  default), `suspended`, `archived`. Formally defines the `suspended` state
  referenced by `service.suspended` webhook events.
- **Gap 2.18:** Added formal webhook payload schema table for catalog change
  events, defining `event`, `service_id`, `subscription_id`, `timestamp`, and
  `data` fields with required/optional semantics.

---

## 24/03/26 at 12:12:11 by [kobym707](mailto:kobym@wix.com)

- Added optional `rating` object to the Service schema with `value` (required),
  `scale_min` (default 1), `scale_max` (required), and `count`. Matches UCP's
  rating schema exactly. Enables platforms and AI agents to display and compare
  service ratings without external lookups.
- Added `Rating` $def to `schemas/catalog.json` and `rating` field to
  `openapi/usp-rest.json` and `openrpc/usp-mcp.json`.

---

## 24/03/26 at 12:03:55 by [kobym707](mailto:kobym@wix.com)

- Added optional `provider` object to the Service schema (§3.3.3) with `name` (
  required), `url`, and `links` (array of typed links to policy pages). Aligns
  with UCP's `seller` object on product variants. Enables platforms to display
  business name, website, and policy links alongside services without a separate
  profile fetch — critical for multi-business search results, cached catalogs,
  and AI agent descriptions.
- Added `Provider` and `Link` $defs to `schemas/catalog.json`, and `provider`
  field to `openapi/usp-rest.json` and `openrpc/usp-mcp.json`.
- Link types follow UCP pattern: `privacy_policy`, `terms_of_service`,
  `refund_policy`, `cancellation_policy`, `faq`, with optional `title` for
  display text and graceful handling of unknown types.

---

## 24/03/26 at 09:40:22 by [kobym707](mailto:kobym@wix.com)

- Extended `description` field on the Service schema to accept either a plain
  string (backward compatible) or a structured `Description` object with
  `plain` (required), `markdown`, and `html` variants. Aligns with UCP's
  `Description` type which supports multi-format content. Platforms prefer the
  richest format they can safely render, falling back to `plain`.
- Added §3.3.2 Description Schema to `specification.md` documenting the
  structured format, backward compatibility rules, and HTML sanitization
  requirements.
- Added `Description` $def to `schemas/catalog.json` and updated `description`
  field in `openapi/usp-rest.json` and `openrpc/usp-mcp.json` with `oneOf` (
  string | object).

---

## 24/03/26 at 09:36:31 by [kobym707](mailto:kobym@wix.com)

- Added `media` array to the Service schema (§3.3.1), replacing `images`. Each
  media entry has `type` (format: `image`/`video`), `url`, `alt_text`, `role` (
  display: `hero`/`gallery`/`thumbnail`), and optional `width`/`height`. Aligns
  with UCP's typed media model. The previous `images` field (`{url, alt, type}`)
  is retained as a deprecated alias for backward compatibility.
- Separated media format type (`type`: image/video) from display role (`role`:
  hero/gallery/thumbnail) — the old `images.type` conflated both concepts.
- Renamed `alt` to `alt_text` for consistency with UCP and accessibility
  standards.
- Updated schema.org mapping to handle both image and video media types.
- Updated `schemas/catalog.json`, `openapi/usp-rest.json`, and
  `openrpc/usp-mcp.json`.

---

## 24/03/26 at 09:33:08 by [kobym707](mailto:kobym@wix.com)

- Added optional `price_range` (`{min, max}` in minor currency units) to the
  Pricing object in §3.8, `schemas/catalog.json`, `openapi/usp-rest.json`, and
  `openrpc/usp-mcp.json`. RECOMMENDED when pricing model is `variable`,
  `hourly`, or `per_person`, so platforms can display "from $50 – $150" without
  querying availability. Aligns with UCP's `price_range` on products. Closes the
  gap where USP services with variable pricing had no displayable price at
  catalog level.

---

## 24/03/26 at 09:30:00 by [kobym707](mailto:kobym@wix.com)

- Added `coordinates` field (`latitude`/`longitude`, WGS 84) to the `context`
  object, enabling proximity-based ranking and "near me" queries for scheduling
  services. Addresses the gap where USP had no mechanism for platforms to signal
  buyer geographic location beyond postal code.
- Extended `context` object to `POST /services/lookup` (previously only on
  `/services/list`), so both catalog request endpoints support buyer
  locale/intent signals for localization of returned content.
- Documented that the `context` object is shared across all catalog request
  payloads with the same field definitions, and that businesses MUST ignore
  unrecognized context fields without error for forward compatibility.

---

## 24/03/26 at 09:26:45 by [kobym707](mailto:kobym@wix.com)

- Extended `POST /services/list` filters to align with UCP `catalog_search`:
  added `categories` (array, OR logic) alongside existing `category_id`, and
  added `price` range filter (`min`/`max` in minor currency units). All filters
  combine with AND logic; within `categories`, values combine with OR logic.
- Added `context` object to `POST /services/list` request, aligning with UCP's
  context pattern. Carries buyer locale and intent signals (`address_country`,
  `address_region`, `postal_code`, `language`, `currency`, `intent`) that
  businesses use for relevance, localization, and personalization. Businesses
  MUST ignore unrecognized context fields without error.
- Updated §3.12.1 in `specification.md` with filter and context field tables,
  updated request examples, and documented precedence rules (`categories` over
  `category_id`, `context.currency` as denomination for price filters).

---

## 24/03/26 at 09:21:23 by [kobym707](mailto:kobym@wix.com)

- Added optional `query` free-text search parameter to `POST /services/list` in
  `specification.md` (§3.12.1), `openapi/usp-rest.json`, and
  `openrpc/usp-mcp.json` — aligns with UCP's `catalog_search` pattern. When
  present, business ranks results by relevance; when combined with filters,
  filters are hard constraints and query determines ranking within the filtered
  set.
- Defined graceful degradation: businesses that do not support search MUST
  ignore the `query` field (not error). Businesses that support it SHOULD
  advertise `"search": true` in their catalog capability entry.

---

## 24/03/26 at 08:55:39 by [kobym707](mailto:kobym@wix.com)

- Added `POST /services/lookup` batch endpoint (§3.12.4) to `specification.md`,
  `openapi/usp-rest.json`, and `openrpc/usp-mcp.json` — analogous to UCP's
  `catalog_lookup`. Accepts an array of service IDs and returns matching
  services with partial-success semantics (unresolved IDs reported via
  `messages[]` with `code: service_not_found`). Closes the gap where USP only
  offered single-service retrieval via `GET /services/{service_id}`.
- Defined batch size limits (MUST accept at least 50), deduplication rules (
  silent dedup), and ordering contract (unordered response) for the new lookup
  endpoint.
- Added `Lookup Services` to the §12 Operation Reference table.

---

## 24/03/26 at 08:48:29 by [kobym707](mailto:kobym@wix.com)

- Added optional `messages[]` array to all three catalog endpoint responses (
  `/services/list`, `/services/{service_id}`, `/services/feed`) in both
  `openapi/usp-rest.json` and `openrpc/usp-mcp.json`, aligning with the UCP
  message model where `catalog_lookup` and `catalog_search` responses carry
  structured messages for partial-success signalling, filter feedback, and
  service-level warnings.
- Updated the `Message` schema in both OpenAPI and MCP specs to match UCP: added
  `content_type` field (`plain`/`markdown`), added `unrecoverable` severity
  level, changed `path` field from JSON Pointer to RFC 9535 JSONPath, made
  `type` and `content` required fields, and expanded severity descriptions to
  match UCP's semantics.
- Added a formal Message field reference table and severity level table to §9.4
  in `specification.md`, so the message contract is fully documented in the spec
  prose (previously only in the OpenAPI/MCP schemas).
- Updated §9.1 error model description to clarify that `messages[]` is available
  on all USP response envelopes including catalog responses, not only
  state-modifying operations.
- Added `messages[]` notes to §3.1 (feed), §3.12.1 (list), and §3.12.3 (get
  service) endpoint descriptions.

---

## 21/03/26 at 14:05:04 by [kobym707](mailto:kobym@wix.com)

- Added §11.2 Buyer Calendar Free/Busy Extension to `specification.md` — a
  MAY-level, platform-scoped extension that enables platforms to access a
  buyer's calendar for opaque free/busy blocks only, then cross-reference with
  business availability to suggest mutually free times. Addresses issue #18
  requesting privacy-preserving calendar access for scheduling agents.
- Introduced the `dev.usp.platform.*` capability namespace in §2.5 to
  distinguish platform-scoped capabilities (implemented entirely by the
  platform) from business-facing `dev.usp.services.*` capabilities. Needed
  because the calendar free/busy extension is the first capability that does not
  require any business-side implementation.
- Created `schemas/calendar_freebusy.json` defining `BusyBlock` (opaque
  `{start, end}` with `additionalProperties: false` to enforce no event detail
  leakage), `BuyerFreeBusy` (aggregated buyer availability), and
  `CalendarProviderConfig` (informative provider reference).
- Added `BusyBlock` and `BuyerFreeBusy` component schemas to
  `openapi/usp-rest.json` for schema registry completeness, even though no new
  endpoints are introduced (the feature is platform-internal).
- Added `BusyBlock` and `BuyerFreeBusy` to the §1.2 Terminology table so the new
  types are discoverable alongside existing protocol terms.
- Updated §11 Extensions intro to note that extensions can be platform-scoped,
  not just business-scoped.
- Added informative references to §14.2 for RFC 4791 (CalDAV), Google Calendar
  FreeBusy API, and Microsoft Graph getSchedule API.

---

## 21/03/26 at 16:27:55 by [kobym707](mailto:kobym@wix.com)

- Expanded §11.2.2 Proactive Agent Use Cases with 4 business-initiated reactive
  scenarios (#8–#11) that compose calendar free/busy with USP webhooks and the
  waitlist extension: calendar-aware waitlist auto-accept/decline, proactive
  rebooking on business cancellation, smart conflict detection on
  business-initiated reschedule, and waitlist priority pre-fetching. These
  demonstrate the extension's value beyond buyer-initiated flows.
- Reorganized the use cases table into two groups — "Buyer-initiated scenarios"
  and "Business-initiated scenarios (reactive via webhooks)" — with
  cross-references to §5.4 (Webhooks) and §11.1 (Waitlist Extension).

---

## 21/03/26 at 14:12:18 by [kobym707](mailto:kobym@wix.com)

- Added §11.2.2 Proactive Agent Use Cases to the calendar free/busy extension,
  describing 7 buyer-initiated agentic scenarios (conflict-aware slot
  presentation, multi-service coordination, smart rescheduling,
  travel-time-aware scheduling, availability-first discovery, recurring pattern
  matching, group scheduling) to strengthen the motivation for the extension and
  illustrate its value for AI-driven scheduling agents.
- Renumbered §11.2.3–11.2.8 to §11.2.4–11.2.9 to accommodate the new
  sub-section.

---

## 19/03/26 at 18:03:50 by [Ran Yahalom](mailto:ranya@wix.com)

- Expanded `USPError` definition in `openrpc/usp-mcp.json` with a fully-typed
  `data` schema: `code` (string enum of all 22 §9.4 error codes including the 5
  new profile error codes), `messages` (array of `$ref: Message`), and
  `severity` (enum). Previously the `data` field was an unstructured description
  string, making the error contract unvalidatable.
- Added `Forbidden` (403) response component to `openapi/usp-rest.json` for the
  `profile_not_trusted` error code. This was the only §9.4 protocol error
  without a corresponding OpenAPI response component.
- Added `403` and `424` error responses to all business-facing endpoints in
  `openapi/usp-rest.json`. Profile negotiation errors are protocol-level and can
  occur on any Standalone Mode call, but previously only `POST /services/list`
  referenced `FailedDependency` (424).
- Fixed previous CHANGE_LOG entry: corrected "four profile-related protocol
  error codes" to "five" — `profile_unreachable` was missing from the list.

---

## 18/03/26 at 23:26:59 by [Ran Yahalom](mailto:ranya@wix.com)

- Added `schemas/usp.json` — formal JSON Schema (Draft 2020-12) for the `usp`
  metadata object used in business profiles, platform profiles, and API
  responses. Defines `$defs/base`, `business_schema` (services, capabilities,
  checkout_systems, business identity, supported_versions), `platform_schema` (
  capabilities + optional service preferences), and `response_schema` (version +
  active capabilities), along with reusable `ServiceBinding`, `CapabilityEntry`,
  and `BusinessInfo` sub-types. Needed to give implementors a
  machine-validatable schema for the core protocol metadata object.
- Added `schemas/profile.json` — formal JSON Schema for the two USP profile
  document types: `$defs/BusinessProfile` (the document at `/.well-known/usp`)
  and `$defs/PlatformProfile` (the document advertised via `USP-Agent`). Defines
  `$defs/SigningKey` (JWK structure for webhook verification keys) with all
  required EC and RSA fields. Needed because there was no machine-validatable
  schema for either profile document, making automated validation impossible.
- Expanded `specification.md` §8.2 with four subsections: §8.2.1 Business
  Profile Fields (field-level tables for top-level profile, `usp` object,
  ServiceBinding, CapabilityEntry, and namespace governance), §8.2.2 Profile
  Hosting Requirements (HTTPS, no-redirect, Cache-Control, Content-Type rules
  and implementation obligations for both sides), §8.2.3 Platform Profile (full
  specification of the platform profile document structure, example, field
  table, hosting requirements, and business-side fetch/cache obligations), and
  §8.2.4 Backward Compatibility (the `supported_versions` map pattern with
  90-day guidance). Needed because the profile was documented only via a single
  example with no formal field definitions.
- Expanded `specification.md` §8.3 Capability Negotiation with a six-step
  negotiation algorithm covering platform profile fetch timing, caching,
  intersection computation, extension pruning, response envelope, and the
  empty-intersection error case. Needed to replace the bare four-bullet
  description with a complete normative algorithm.
- Added five profile-related protocol error codes to `specification.md` §9.4
  error table: `invalid_profile_url`, `profile_unreachable`,
  `profile_malformed`,
  `capabilities_incompatible`, and `profile_not_trusted`, with REST status codes
  and JSON-RPC codes. Needed to make profile failure modes first-class,
  consistent, and interoperable.
- Expanded `specification.md` §10.1.1 signing keys documentation with a full
  `SigningKey` field table (kid, kty, crv, x, y, n, e, use, alg) and
  cross-references to `schemas/profile.json`. Needed because `signing_keys`
  field-level constraints were undocumented.
- Updated `openapi/usp-rest.json`: marked `USP-Agent` parameter as
  `required: true`; added `SigningKey`, `ServiceBinding`, `CapabilityEntry`,
  `BusinessProfile`, and `PlatformProfile` component schemas; added
  `GET /.well-known/usp` path with full response schema and example. Needed to
  make the OpenAPI spec self-describing for both the profile endpoint and the
  header the spec already referenced.
- Updated `openrpc/usp-mcp.json`: tightened `_meta` param schema across all 19
  methods — `_meta.usp.profile` is now declared with `format: uri`, descriptive
  text clarifying it is required in Standalone Mode, and `required: ["profile"]`
  within the `usp` sub-object. Needed to align the MCP binding with the REST
  binding's capability negotiation semantics.

---

## 16/03/26 at 12:20:45 by [Ran Yahalom](mailto:ranya@wix.com)

- Implemented `USPRestClient.search_registry_for_services` method body per the
  `/registry/search_services` OpenAPI schema — performs a POST to the USP
  registry, builds the request from typed parameters (query, location,
  verticals, categories, price\_range, duration\_range, pagination), and parses
  the response into `ServiceSearchResult` models. Handles both camelCase and
  snake\_case response field names (e.g. `results` vs `services`,
  `pagingMetadata` vs `pagination`) so the client works against both the live
  API and schema-compliant implementations.
- Added four new Pydantic models to `shopping_agent/subagents/usp/models.py`:
  `ServiceSearchResultPrice`, `ServiceSearchResultLocation`,
  `ServiceSearchResult`, and `ServiceSearchPagination` — all configured with
  `alias_generator=to_camel` and `populate_by_name=True` for bidirectional
  camelCase/snake\_case support, matching the `ServiceSearchResult` and
  `Pagination` schemas in the OpenAPI spec.

---

## 01/03/26 at 15:28:19 by [Ran Yahalom](mailto:ranya@wix.com)

- **Scoped `post_payment_return_request` to the `redirect` checkout path:**
  Added a note in §8.5.5 and in all schema descriptions clarifying that the
  field applies only when `checkout_systems: redirect` is in use, and is not
  applicable to the `acp` or `embedded` checkout paths.
- **Made cancellation/abandonment a first-class outcome
  in `post_payment_return_request`:** Expanded all prose, table descriptions,
  and schema `description` strings to explicitly state the business MUST honor
  the return redirect in both terminal outcomes — payment completed *and*
  payment cancelled/abandoned — not only on success.
- **Added SHOULD recommendation for including `post_payment_return_request`:**
  Even though the field is optional, updated §8.5.5, the §5.3.1 field table, and
  all schema descriptions to state that the platform SHOULD always include it on
  the redirect path, because without it the platform has no way to predict or
  control where the buyer lands after payment or cancellation.

---

## 01/03/26 at 15:24:37 by [Ran Yahalom](mailto:ranya@wix.com)

- **Added `post_payment_return_request` to `POST /bookings` as a first-class
  spec field with MUST-level compliance language:** Resolves the missing
  return-redirect mechanism in the redirect-based payment flow. The new field
  lets the platform supply a return URL (with opaque correlation params) at
  booking creation time — exactly when a server-side checkout system (e.g. Wix
  headless checkout) needs it — rather than after the buyer reaches the payment
  page.
- **Introduced `PostPaymentReturnRequest` schema across all spec
  artefacts (`specification.md`, `openapi/usp-rest.json`,`openrpc/usp-mcp.json`,
  `schemas/scheduling.json`):** Defines `url` (required, URI) and `params` (
  optional, string key-value map) with descriptions that make clear the business
  must append `params` verbatim as query parameters on the GET redirect, and
  that keys/values are opaque platform-controlled correlation state.
- **Expanded §8.5.5 from "Action Continue URL" to "Redirect Flow and
  Post-Payment Return":** Added a mermaid sequence diagram of the full redirect
  round-trip, MUST language, and the analogy to OAuth 2.0's `redirect_uri` +
  `state` pattern.

---

## 26/02/26 at 10:27:59 by [kobym707](mailto:kobym@wix.com)

- **Renamed `schemas/scheduling.json` to `schemas/booking.json`:** Renamed the
  file and updated the schema identity (`$id`, `title`) to "USP Booking" to
  better reflect that the schema defines the booking lifecycle (Booking, Buyer,
  BookingPayment, etc.), not the broader scheduling domain. Updated all
  references in specification.md and README.md.

---

## 25/02/26 at 17:23:00 by [Ran Yahalom](mailto:ranya@wix.com)

- **Updated `openrpc/usp-mcp.json` to match the current OpenAPI and
  specification:** Expanded the sparse `Booking` schema to include all
  properties from the OpenAPI spec (`resources`, `location`, `payment`,
  `actions`, `notes`, `cancellation`, `created_at`, `updated_at`, `expires_at`)
  with proper types, enums, and descriptions. Added `BookingPayment`,
  `PaymentContext`, and `Action` component schemas matching the OpenAPI
  definitions. Updated `Message` schema to include `severity` enum, `path`
  field, and description. The OpenRPC now has full parity with the OpenAPI for
  all domain schemas (Booking, BookingPayment, PaymentContext, Action, Message).

---

## 25/02/26 at 17:16:27 by [Ran Yahalom](mailto:ranya@wix.com)

- **Updated `openapi/usp-rest.json` to match the actions[] changes:** Added
  `Action` schema to OpenAPI components. Removed `payment_context`, `messages`,
  and `continue_url` from the Booking schema and replaced with `actions` array
  referencing the new Action schema. Removed `payment_url` from BookingPayment.
  Removed `expires_at` from PaymentContext required fields and properties. Added
  description to Message schema clarifying its dual use (response-level and
  action-level).

---

## 25/02/26 at 16:11:33 by [Ran Yahalom](mailto:ranya@wix.com)

- **Introduced `actions[]` array on the booking object:** Replaced the flat
  `payment_context`, `continue_url`, and `messages` fields on the booking with
  an ordered `actions` array. Each action has `type`, `status`, `continue_url`,
  `expires_at`, and an optional `message`. Payment actions carry a nested
  `payment_context`. This makes the spec extensible for future non-payment
  action types (e.g., waivers, intake forms) while cleaning up the `payment_url`
  redundancy.
- **Established the status-actions invariant:**
  `booking.status: requires_action` is now structurally tied to `actions[]` —
  the booking MUST have this status if and only if at least one action has
  `status: pending`. When the last pending action completes, the business MUST
  transition the booking out of `requires_action`.
- **Made actions mode-agnostic for non-payment actions:** In UCP-Native Mode,
  `actions[]` never contains `payment`-type actions (payment is handled by UCP
  checkout), but non-payment actions may appear on the booking inside the
  `create_checkout` response. `complete_checkout` may be rejected if non-payment
  actions are still pending.
- **Added action ordering rationale:** Non-payment actions SHOULD precede
  payment actions so that the buyer can review requirements (e.g., read a
  liability waiver) and opt out before committing financially, avoiding
  unnecessary refunds.
- **Removed `payment_url` from BookingPayment:** Absorbed into the payment
  action's `continue_url` field.
- **Removed `expires_at` from PaymentContext:** Moved to the action-level
  `expires_at` field.
- **Removed `booking.messages[]`:** The only concrete usage (`payment_required`)
  now lives on `action.message`. Response-level `messages[]` remains for
  business outcome errors/warnings. Removed `info` from response-level message
  types.
- **Added `actions_pending` error code:** For when `confirm-payment` or
  `complete_checkout` is called while non-payment actions are still pending.
- **Updated `schemas/scheduling.json`:** Added `Action` definition to `$defs`
  with `type`, `status`, `continue_url`, `expires_at`, `message`, and
  `payment_context`. Removed `payment_context`, `messages`, and `continue_url`
  from Booking properties. Added `actions` array. Removed `payment_url` from
  BookingPayment. Removed `expires_at` from PaymentContext.
- **Updated all affected sections:** Glossary (1.2), operational modes (2.2.1),
  business responsibilities (2.1.2), architecture diagram text (2.3), booking
  status lifecycle (5.1), booking schema (5.2), create booking example (5.3.1),
  confirm-payment (5.3.7), UCP checkout flow (7.5), standalone mode (8), payment
  integration (8.5.1–8.5.7), checkout_systems (8.2), end-to-end flows (8.6),
  REST error model (9.1), and error code mapping (9.4).

---

## 25/02/26 at 12:51:33 by [Ran Yahalom](mailto:ranya@wix.com)

- **Promoted Discovery Registry to standalone Section 6:** Extracted Section
  7.5 (Discovery Registry) from Standalone Mode and promoted it to a top-level
  section (new Section 6) placed before the deployment modes. This reflects that
  the Discovery Registry is deployment-mode-independent and can index both
  Standalone and UCP-Native businesses. Incurred changes:
    - **Generalized Discovery Registry for both deployment modes:** Replaced
      `usp_profile_url` with `profile_url`, added a `deployment_mode` field (
      `standalone` or `ucp_native`) to registration and search schemas, and
      updated validation rules to support both `/.well-known/usp` and
      `/.well-known/ucp` profiles.
    - **Renumbered Sections 6-13 → 7-14:** Cascading renumber due to the new
      Section 6 insertion. UCP-Native Mode is now Section 7, Standalone Mode is
      Section 8, Transport Bindings is Section 9, Security is Section 10,
      Extensions is Section 11, Operation Reference is Section 12, IANA
      Considerations is Section 13, References is Section 14.
    - **Updated all cross-references, ToC, implementation stages, reading path
      diagram, and reading path tables** to reflect the new section numbering
      and the mode-independent Discovery Registry.

---

## 23/02/26 at 21:30:07 by [kobym707](mailto:kobym@wix.com)

- **Added Section 2.1.5 "Implementor Note: Expected Deployment Topology":**
  Clarifies that business-side USP is almost always implemented by SaaS
  platforms (Wix, Square, Mindbody) on behalf of their merchants, not by
  individual businesses. This sets reader expectations for why features like the
  catalog feed, subscriptions, and hold abuse prevention are scoped for
  professional platform teams, and preempts the "too complex for a small
  business" objection.

---

## 23/02/26 at 16:26:54 by [kobym707](mailto:kobym@wix.com)

- **Simplified Section 2.6 (Multi-Location Businesses):** Collapsed two
  sub-sections (2.6.1 Per-Location Profiles and 2.6.2 Parent-Entity Profile)
  into a single unified section. The per-location model was just standard
  single-location USP and didn't need its own sub-section; it's now a one-line
  note. The section now focuses on the only case that introduces protocol
  surface: a single endpoint serving multiple locations via the `locations[]`
  profile field and `location_id` filters.

---

## 23/02/26 at 16:21:59 by [kobym707](mailto:kobym@wix.com)

- **Fixed broken Mermaid diagram in Section 2.3 (High-Level Architecture):** The
  `graph TD` diagram used invalid single-dash edge syntax (` - "label" -->`)
  which caused a parse error on GitHub. Replaced with valid double-dash syntax (
  `-- "label" -->`) and switched `\n` to `<br/>` for multi-line edge labels.

---

## 22/02/26 at 15:36:29 by [kobym707](mailto:kobym@wix.com)

- **Made holds optional via feature flag on the availability capability:**
  Introduced a `holds` boolean feature flag on `dev.usp.services.availability`
  to explicitly declare whether a business supports the Hold Slot and Release
  Slot operations, because many businesses (especially small or low-contention
  ones) can operate safely without the hold mechanism, and forcing it on all
  implementers raised the integration bar unnecessarily.
- **Updated Section 4 (Availability) with feature flag table and discovery
  guidance:** Added the flag definition, profile declaration example, and
  clarified that when `holds` is absent or `false`, the booking flow proceeds
  directly from slot query to booking creation.
- **Gated Sections 4.2, 4.3.2, and 4.3.3 behind the holds flag:** Added callout
  blocks to the Hold entity, Hold Slot, and Release Slot operation sections
  noting they require `"holds": true`, preventing platforms from calling
  endpoints the business does not support.
- **Made `hold_id` explicitly optional in Create Booking (5.3.1) and
  Reschedule (5.3.6):** Added field-level tables with `hold_id` marked as
  optional, added a "without hold" request example, and updated the prose to
  describe both hold and no-hold flows.
- **Updated the caching strategy funnel (4.4):** Marked the Commit tier as
  optional and updated the Mermaid diagram to show a conditional branch for hold
  support.
- **Updated all end-to-end flow diagrams (6.7 and 7.7):** Changed Mermaid
  sequence diagrams to use `opt Business supports holds` blocks instead of
  showing holds as mandatory steps.
- **Updated A2A booking flow (8.3.2):** Made the hold step conditional and noted
  `hold_id` as optional in the booking creation step.
- **Updated profile examples (6.2, 7.2) to include `"holds": true`:**
  Demonstrates how businesses declare hold support in both UCP-Native and
  Standalone profiles.
- **Updated OpenAPI schema:** Added descriptions to hold/release endpoints
  noting the feature flag requirement, made `hold_id` optional in the reschedule
  request body, and updated `hold_id` descriptions in create booking.
- **Updated OpenRPC schema:** Added feature flag descriptions to hold/release
  methods and made `hold_id` optional (not required) in the reschedule method.
- **Updated paid_bookings.json schema:** Clarified `hold_id` description to note
  it depends on holds capability support.
- **Updated Operation Reference (11) and MCP/A2A mapping tables:** Annotated
  hold/release operations with `(holds: true)` to signal the feature flag
  requirement.
- **Updated Hold Abuse Prevention (9.1.2):** Scoped the section to apply only
  when holds are supported.

---

## 22/02/26 at 14:09:11 by [kobym707](mailto:kobym@wix.com)

- **Promoted Business ID and Localization to peer-level sections:** Extracted
  former 3.3.1 (Business ID) and 3.3.2 (Localization) from under the Service
  Schema section into their own top-level sections (3.4 and 3.5), consistent
  with how other complex Service fields (Duration, Pricing, Policies, etc.) are
  structured. Renumbered sections 3.4-3.10 to 3.6-3.12 and updated all
  cross-references throughout the spec.

---

## 22/02/26 at 13:54:36 by [kobym707](mailto:kobym@wix.com)

- **Moved extended verticals to informative Appendix A:** Relocated the five
  candidate verticals (`event`, `course`, `healthcare`, `home_service`, `tour`)
  from Section 1.3.2 to a new non-normative Appendix A, following RFC
  conventions for separating forward-looking content from normative spec. Added
  promotion criteria (A.2) requiring two independent implementations before a
  vertical can become core.
- **Renumbered Custom Verticals to Section 1.3.2:** Former Section 1.3.3 is now
  1.3.2 with a forward reference to Appendix A for candidate verticals.
- **Opened the `type` field enum in JSON schemas:** Removed the closed enum
  constraint on `service.type` in `usp-rest.json` and `paid_bookings.json` so
  that vendor-defined custom verticals using reverse-domain notation are not
  rejected by schema validation, aligning the schemas with what Section 1.3
  already permits.

---

## 22/02/26 at 12:18:07 by [kobym707](mailto:kobym@wix.com)

- **Added `business_id` to Service schema:** Every service object now carries
  the identifier of its owning business, making services self-describing for
  cross-business semantic search, cached catalog aggregation, and agent-to-agent
  hand-off. The composite key `(business_id, id)` is the globally unique
  identifier. Updated `catalog.json`, `usp-rest.json`, `usp-mcp.json`, and all
  service examples in `specification.md`.
- **Added localization (i18n) support:** Introduced the `localized` field on
  Service with per-locale overrides for `name`, `description`, `category_name`,
  and `channel_instructions` using IETF BCP 47 language tags. Enables businesses
  serving multilingual audiences to provide translations in a single cacheable
  response. Added `LocalizedFields` type to `catalog.json` and `usp-rest.json`.
- **Added undetermined duration option:** Services with no meaningful duration (
  consultations, custom quotes) can now set `duration.undetermined: true`
  instead of being forced to provide a fixed or range value. Added mutual
  exclusivity constraint with `fixed`/`range` and a validation rule preventing
  `hourly` pricing with undetermined duration.

---

## 21/02/26 at 11:42:09 by [Ran Yahalom](mailto:ranya@wix.com)

- **Extended USP Booking Form Profile with slot selection:** Added D0 derivation
  rules (slot picker, date picker), new inputs (`slots[]`, `flow_mode`), A2UI
  mappings for slot/date pickers, `usp_select_date` action, and D3/D4/D5
  fallbacks when slot not yet selected, enabling unified forms where slot
  selection is part of the form (pre-fetched or date-first flow)
- **Bumped profile version to 1.1**

---

## 21/02/26 at 10:47:37 by [Ran Yahalom](mailto:ranya@wix.com)

- **Added USP Booking Form Profile:** New separate spec (
  `docs/usp-booking-form-profile.md`) defining field derivation rules and A2UI
  component mapping for AI agent platforms building booking forms, so platforms
  know which form fields to show based on service/slot context and how to render
  them via A2UI
- **Added design doc:**
  `docs/plans/2026-02-21-usp-booking-form-profile-design.md` capturing the
  approved design from brainstorming
- **Updated README:** Added USP Booking Form Profile to the Specification
  documents table with link to the profile spec

---

## 21/02/26 at 10:12:28 by [Ran Yahalom](mailto:ranya@wix.com)

- Updated AGENTS.md entry format to include a mailto link for the author's git
  email, so each change log entry attributes the author with a clickable email
  link for traceability and easy contact

---

## 21/02/26 at 10:05:27 by Ran Yahalom

- **Fixed wrong cross-section links in specification.md:** Corrected Section
  1.3 (Vertical) link from `#9-service-verticals` to `#13-service-verticals`;
  Section 4.4 (Caching Strategy) from `#34-caching-strategy` to
  `#44-caching-strategy`; RFC 6749 (OAuth) from non-existent Section 9.6 to
  Section 9.2.3 Authentication and Authorization (
  `#923-authentication-and-authorization`); RFC 9421 (Webhooks) from Section 9.3
  to Section 9.1.1 Webhook Security (`#911-webhook-security`); Section 5.1 (
  Booking Status) from `#31-booking-status-lifecycle` to
  `#51-booking-status-lifecycle`
- **Fixed TOC:** Section 1.5 link text and anchor from "Deployment Modes and
  Implementation Guide" / `#15-deployment-modes-and-implementation-guide` to "
  Deployment Modes" / `#15-deployment-modes` to match actual heading
- **Added missing cross-links:** Converted plain "Section X" references to
  markdown links throughout the specification (intro, terminology table,
  implementation stages, deployment mode descriptions, core constructs table,
  booking schema, webhooks, security, extensions, etc.)

---

## 21/02/26 at 09:47:00 by Ran Yahalom

### Added JSON Schema links to specification.md

#### specification.md

**Added schema file links to all schema definition sections**

- Section 3.3 (Service Schema): added link to `schemas/catalog.json`
- Section 4 (Availability): added link to `schemas/availability.json`
- Section 5.2 (Booking Schema): added link to `schemas/scheduling.json`
- Section 7.6.1 (Booking Payment Schema): added link to
  `schemas/scheduling.json` with note pointing to `BookingPayment` and
  `PaymentContext` definitions
- Section 10.1.1 (WaitlistEntry Schema): added link to `schemas/waitlist.json`

**Fixed broken schema reference in Section 6.4 (Paid Bookings Extension Schema)
**

- Updated `schemas/services/paid_bookings.json` → `schemas/paid_bookings.json`
  to reflect the schema file relocation from `schemas/services/` to `schemas/`
- Converted plain text reference to a proper Markdown link

---

### Fixed mislocated schema and response definitions in OpenAPI spec

#### openapi/usp-rest.json

**Moved 22 schemas out of `USPEnvelope` to top-level `components.schemas`**

- `PaginationRequest`, `Pagination`, `Service`, `Duration`, `Pricing`,
  `Location`, `Channel`, `ServicePolicies`, `AvailabilityHint`,
  `FeedSubscription`, `TimeSlot`, `Hold`, `Buyer`, `Booking`, `BookingPayment`,
  `PaymentContext`, `Message`, `WaitlistEntry`, `ResourceRequirement`,
  `RegistryEntry`, `ServiceSearchResult`, and `ProblemDetails` were incorrectly
  nested as extra keys inside the `USPEnvelope` schema object (siblings of its
  `type`/`required`/`properties`)
- All 22 are now proper siblings of `USPEnvelope` under `components.schemas`,
  which allows `$ref` pointers like `#/components/schemas/Duration` to resolve
  correctly

**Moved `responses` block from inside `schemas` to `components.responses`**

- The 8 response definitions (`BadRequest`, `Unauthorized`, `NotFound`,
  `Conflict`, `UnprocessableEntity`, `FailedDependency`, `TooManyRequests`,
  `InternalServerError`) were nested under `components.schemas.responses`
  instead of `components.responses`
- They are now correctly placed as a sibling of `schemas` under `components`

---

### Renamed business search endpoint and added service search

#### specification.md

**Section 7.5.2 –
Renamed `POST /registry/search` → `POST /registry/search_business`**

- Endpoint path changed to disambiguate from the new service search endpoint

**Section 7.5.3 – Added Service Search (`POST /registry/search_services`)**

- New section enabling platforms to search across all registered businesses'
  services directly
- Request accepts `location`, `verticals`, `categories`, `query`,
  `price_range` (min/max/currency), `duration_range` (min_minutes/max_minutes),
  and `pagination`
- Response returns a `services` array with `service_id`, `service_name`, nested
  `business` object (id, usp_profile_url, name), `category`, `duration_minutes`,
  `price`, `location`, and `timezone`

**Section 7.5.4 – Renumbered Registry Governance**

- Previously 7.5.3, renumbered to accommodate the new Service Search section

**Section 11 – Endpoint Summary Table**

- Updated `/registry/search` row to `/registry/search_business`
- Added new row for
  `Search Services | POST | /registry/search_services | discovery (optional)`

#### openapi/usp-rest.json

**Renamed path `/registry/search` → `/registry/search_business`**

- operationId remains `searchBusinesses`

**Added path `/registry/search_services`**

- operationId: `searchServices`
- Request body includes `price_range` and `duration_range` filters in addition
  to the base search fields
- Response returns `services` array of `ServiceSearchResult` items with
  pagination

**Added schema `ServiceSearchResult`**

- Fields: `service_id`, `service_name`, `business` (id, usp_profile_url, name),
  `category`, `duration_minutes`, `price` (amount, currency), `location`,
  `timezone`

---

### Added missing response snippets and fixed snippets to conform to OpenAPI schemas

#### specification.md

**Section 7.5.1 – Business Registration (`POST /registry/businesses`)**

- Added `Request:` label before the existing JSON body
- Added `Response:` snippet returning a `USPEnvelope` with
  `dev.usp.discovery.registry` capability and a `registration` object containing
  `id`, echoed request fields, `status`, and `created_at`

**Section 7.5.2 – Business Search (`POST /registry/search_business`)**

- Added `Request:` label before the existing JSON body
- Added `Response:` snippet returning a `USPEnvelope` with a `businesses` array
  of `RegistryEntry` objects and `pagination` with `cursor`/`has_more`

**Section 4.3.3 – Release Slot response**

- Added `slot_id`, `service_id`, and `expires_at` to the `hold` object in the
  response, which are required fields per the `Hold` schema

**Section 7.5.2 – Business Search response**

- Added `status` and `created_at` to each business entry in the `businesses`
  array, which are required fields per the `RegistryEntry` schema

**Section 7.5.3 – Service Search request and response**

- Changed `price_range.min`/`max` from `50`/`200` to `5000`/`20000` (minor
  currency units)
- Changed `price.amount` from `120`/`180` to `12000`/`18000` (minor currency
  units), consistent with the convention used throughout the spec

**Section 7.7.4 – Deposit Flow**

- Added `slot_start` to `payment_context.metadata`, matching the
  `PaymentContext` schema and other `create_booking` response examples

---

### New and updated OpenAPI schemas

#### openapi/usp-rest.json

**New schemas**

| Schema                | Description                                                                                                                                |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| `Duration`            | `fixed` / `range` (min, max, step), `buffer_before`, `buffer_after`                                                                        |
| `Pricing`             | `model` (enum), `amount`, `currency`, `deposit` (type, value, refundable)                                                                  |
| `Location`            | `id`, `name`, `address`, `coordinates`                                                                                                     |
| `Channel`             | `type` (enum: in_person/virtual/phone/hybrid), `virtual_provider`, `instructions`                                                          |
| `ServicePolicies`     | `cancellation`, `rescheduling`, `no_show`, `booking_window`, `confirmation_mode`, `requires_payment`, `payment_timing` with all sub-fields |
| `AvailabilityHint`    | `summary`, `generated_at`, `next_available_date`                                                                                           |
| `BookingPayment`      | `status` (enum), `timing`, `amount`, `currency`, `amount_due`, `deposit_amount`, `transaction_id`, `order_reference`, `payment_url`        |
| `PaymentContext`      | `amount_due`, `currency`, `description`, `line_items`, `metadata`, `expires_at`                                                            |
| `ResourceRequirement` | `type` (enum: staff/room/equipment/other), `name`, `selectable`, `options`                                                                 |
| `RegistryEntry`       | `id`, `usp_profile_url`, `name`, `verticals`, `categories`, `location`, `timezone`, `status`, `created_at`                                 |

**Updated schemas – added missing fields**

| Schema          | Fields added                                   |
|-----------------|------------------------------------------------|
| `Service`       | `category`, `locations`, `resources`, `images` |
| `Booking`       | `resources`, `location`, `cancellation`        |
| `WaitlistEntry` | `preferred_slots`                              |

**Updated schemas – added types, descriptions, defaults, and enums**

Every property across all schemas was updated from bare `{}` to include explicit
`type`, `description`, `format`, `default`, and/or `enum` values. This applies
to:

- `USPEnvelope` (version, capabilities)
- `Service` (all 14 properties)
- `FeedSubscription` (id, callback_url, categories, events, status, created_at)
- `TimeSlot` (all 10 properties including capacity sub-fields, resources items,
  location, pricing)
- `Hold` (id, slot_id, service_id, spots with default:1, expires_at, status)
- `Buyer` (first_name, last_name, email with format:email, phone_number)
- `Booking` (all 18 properties including slot sub-object, status enum with 7
  values, confirmation_mode enum)
- `Message` (type, code, content, severity, path)
- `WaitlistEntry` (all 8 properties including preferred_slots items,
  offered_slot, position with minimum:1)
- `ResourceRequirement` (type, name, selectable with default:false, options)
- `RegistryEntry` (all 9 properties)
- `ServiceSearchResult` (all 8 properties)
- `ProblemDetails` (type, title, status, detail, instance, errors)

All request body schemas were also updated (list services filters, availability
query, hold slot, create booking, update booking, cancel booking, reschedule
booking, confirm payment, join waitlist, accept waitlist offer, register
business, search businesses, search services).

**Updated endpoint responses**

| Endpoint                         | Change                                                                                                  |
|----------------------------------|---------------------------------------------------------------------------------------------------------|
| `POST /registry/businesses`      | Response now returns `USPEnvelope` + `{ registration: RegistryEntry }` instead of bare envelope         |
| `POST /registry/search_business` | `businesses` array items now reference `RegistryEntry`; `pagination` now references `Pagination` schema |

**Fixed inconsistencies with specification.md**

| Issue                                       | Fix                                                                                            |
|---------------------------------------------|------------------------------------------------------------------------------------------------|
| `Booking.status` enum missing `in_progress` | Added `in_progress` to the enum to match Section 5.1 lifecycle                                 |
| `opening_hours` typed as `object`           | Changed to `array` with items schema (`day_of_week`, `opens`, `closes`) to match Section 4.3.1 |
