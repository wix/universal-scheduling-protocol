# USP test vectors

Worked examples for the parts of the specification that can be implemented
wrongly without any reviewer noticing. Run them with:

```bash
python tools/usp_check.py vectors
```

CI runs the same command on every push.

## Why these exist

`platform_key_pop` is specified on both bindings and implemented on neither.
Prose review catches a contradictory MUST; it does not catch a canonicalization
rule that two implementers read the same way and encode differently. These
vectors publish the exact bytes, so a second implementation can disagree with
the first *before* both ship.

The same argument applies to concurrency and time. A spec can say "atomic" and
"use instants" and be read as agreement by two implementations that behave
differently under a lapsed hold or a daylight-saving transition. The `flow/`
vectors write those cases down.

## Kinds of vector

| Directory | Asserts | Code field | Carried as |
|---|---|---|---|
| `pop/` | Protocol errors on the authentication path | `reject_code` | 4xx Problem Details / JSON-RPC `error` |
| `flow/` | Business outcomes on the booking path (`kind: flow`), and composed scenarios (`kind: compose`) | `outcome_code` | HTTP 200 with the code in `messages[]` |
| `wire/` | On-the-wire shape rules a schema cannot express | none | A producer conformance failure, not an error code |
| `eval/` | Booking-question condition evaluation | none | Recomputed applicability, not an error code |
| `fixtures/` | Reusable building blocks for composed vectors | none | Never cited; validated on their own |

The two code fields are checked against different mirrors and a vector may not
set both: a case is either a protocol error or a business outcome, never both. A
`reject_code` must appear in the §10.1.1 table and the OpenRPC
`USPProtocolError` enum. An `outcome_code` must appear in the §9.4.2
business-outcome table or an extension business-outcome table it points to
(§11.4.9), and must *not* appear in that enum, which is how the checker proves
the two error families stay disjoint.

## Format: `pop/`

One JSON object per file, under `pop/`.

| Field | Meaning |
|---|---|
| `id` | Stable identifier. **Must be cited in `specification.md`** — the checker fails otherwise, so prose and vectors cannot drift apart. |
| `section` | The specification section the vector pins down. |
| `requirement` | Short slug for the rule under test. |
| `binding` | `rest`, `mcp`, or both. |
| `expect` | `accept` or `reject`. |
| `reject_code` | For `reject` vectors. Must appear in the §10.1.1 error-code table **and** the OpenRPC `USPProtocolError` enum. |
| `notes` | What the vector is for, and what a naive implementation gets wrong. |
| `key` | Public JWK, its RFC 7638 thumbprint, and — for reproducibility — the raw private key. |
| `proof` | Compact JWS. Really signed; the checker verifies it. |
| `expected_claims` | The decoded payload, so a mismatch between prose and signature is caught. |
| `credential` | Validated against `schemas/profile.json#/$defs/BookingScopedCredential`. |
| `canonicalization` | `params` → `jcs` bytes → `usp_p` digest, all recomputed by the checker. |

## Format: `flow/`

One JSON object per file, under `flow/`. These are scenario vectors rather than
byte-level ones, so they read as given / when / then.

| Field | Meaning |
|---|---|
| `id` | Stable identifier. **Must be cited in `specification.md`**, same rule as `pop/`. |
| `section` | The specification section the vector pins down. |
| `requirement` | Short slug for the rule under test. |
| `kind` | `flow`. |
| `expect` | `accept` or `reject`. |
| `outcome_code` | For `reject` cases. Must be a §9.4.2 business-outcome code. |
| `given` | Starting state: the service, slot, capacity, and any hold. |
| `when` | Ordered steps with timestamps. Interleaved actors make the race explicit. |
| `then` | The required observable result, including capacity afterwards and whether a retry is worthwhile. |
| `wrong_answers` | Plausible implementations that violate the rule, and what each one costs. |
| `cases` / `variants` | Additional scenarios sharing the same setup. |

`wrong_answers` is the part that carries the weight. A vector that only records
the right answer tests a parser. Naming the specific wrong behaviours, and the
harm each causes, is what makes the vector useful to someone deciding how to
implement rather than checking that they already did.

| Vector | What it pins down |
|---|---|
| `101-hold-expiry-during-checkout` | A hold lapses mid-checkout while the slot stays free. Charging first strands a charged buyer with no booking; returning `slot_unavailable` throws away a slot that is still bookable. |
| `102-concurrent-holds-one-slot` | Two platforms race for the last capacity unit. Decidable only because capacity is consumed at hold creation, not at booking. |
| `103-dst-spanning-slot` | Two slots straddling a DST change where wall-clock arithmetic is wrong in opposite directions: 30 minutes for a 90-minute service, 2 hours for a 60-minute one. |
| `104-charge-without-booking` | The PSP charge succeeds and the booking write fails. There is no single transaction to roll back, so the vector records both permitted resolutions and the intermediate state that is forbidden. |
| `105-confirmation-mode-guard` | `confirm` from `pending` is legal only in manual mode. An auto-mode UCP-Native leftover that is still `pending` MUST be rejected with `invalid_transition` at HTTP 200; a booking-scoped credential MUST NOT authorize the call. |
| `106-ucp-native-fixed-deposit` | UCP-Native `deposit_required` with a fixed deposit: full checkout total, one selected term, one immediate schedule, balance `due_at` equal to slot start, order `accepted_term`, no `split_payments`. |
| `107-ucp-native-percentage-deposit` | Same shape with a percentage catalog deposit whose immediate amount is the business-computed integer 4000, not a platform-side 20 percent of total. |

## Format: `wire/`

One JSON object per file, under `wire/`. Each case is a concrete instance plus
what the checker must compute for it.

| Field | Meaning |
|---|---|
| `id` | Stable identifier. **Must be cited in `specification.md`**, same rule as `pop/`. |
| `section` | The specification section the vector pins down. |
| `requirement` | Short slug for the rule under test. |
| `kind` | `wire`. |
| `expect` | `accept` or `reject`. Must agree with the computed conformance. |
| `schema` | The `$def` the instance is validated against, as `file.json#/$defs/Name` under `schemas/`. |
| `instance` | The JSON a producer emitted. |
| `then.schema_valid` | Whether `instance` validates against `schema`. Recomputed. |
| `then.member_name_violations` | JSON Pointers of members that restyle a defined snake_case name (for example `serviceId`). Recomputed. |
| `then.conforming` | Schema-valid and no member-name violations. Recomputed. |
| `variants` / `wrong_answers` | As for `flow/`. Each variant carries its own `instance` and `then`. |

| Vector | What it pins down |
|---|---|
| `201-camelcase-member-names` | A service search hit that keeps every required member in snake_case but camelCases optional ones. It is schema-valid, because the schema allows extra members, and still non-conforming under the §1.1 member-name rule. |

Booking-questions wire vectors (`bq-schema-*`, §11.4.3) add two fields:

| Field | Meaning |
|---|---|
| `then.semantic_errors` | Cross-item definition rules JSON Schema cannot express, as `rule:item_id` (for example `forward_reference:q2`, `duplicate_option_const:hair_length`, `empty_section:about_you`, `multiple_maps_to_notes:more`). Recomputed; a non-empty list makes the case non-conforming. |
| `answer_cases` | Answers checked against the case's question: `{value, valid, errors?, request_date?, question?}`, or `{absent: true, valid}` for an unanswered required question. `request_date` fixes the date that relative date bounds (`P0D`, `-P18Y`) resolve against; `question` selects a question inside a set. Recomputed. |

## Format: `eval/`

Booking-question condition vectors (`bq-cond-*`, §11.4.3 Conditions). One JSON
object per file.

| Field | Meaning |
|---|---|
| `id`, `section`, `requirement`, `notes`, `wrong_answers` | As for `flow/`. |
| `kind` | `eval`. |
| `given.set` | A `BookingQuestionSet` shared by the cases. |
| `cases[]` | Each case has `case`, optional `set` (overrides `given.set`), optional `answers` (question id to value), and `then`. |
| `then.definition_valid` | Schema-valid against `BookingQuestionSet` and free of semantic errors. Recomputed. |
| `then.semantic_errors` | As for wire vectors. |
| `then.applicable` | Item ids that apply, in item order. |
| `then.required_unanswered` | Applicable questions whose `required` holds and that have no answer. |
| `then.pruned` | Answer keys whose question became inapplicable. |

Evaluation is a single pass in item order: a section's `when` switches its
group off, a question's own `when` must also hold, and only answers to
applicable questions count toward later conditions. An unanswered or
inapplicable reference makes `answered` false and every other operation false.

## Booking-questions `flow/` checks

`bq-flow-*` vectors use the ordinary flow format. The checker additionally:

- validates every `booking_question_sets`, `required_buyer_fields`,
  `booking_question_submissions`, `booking_question_state`,
  `booking_question_assessment_token`, `eligibility`, and `booking_questions`
  member it finds against its `$def`, and every buyer-input Action against
  `Action` and `BuyerInputActionConfig`. A subtree marked
  `"schema_checked": false` is skipped;
- validates every message against `Message`, requires §11.4.9 and §9.4.2 codes
  to be documented and carried with the right `type`, and requires
  booking-question paths to be bracket-form RFC 9535 set or question paths;
- scans every step `result` and `then` for the submitted value of any
  `sensitive` question;
- with `given.extension_negotiated: false`, fails on any §11.4.9 code;
- **derives** the messages a conforming business returns for every
  `check_eligibility`, `create_booking`, `update_booking`, `create_checkout`, or
  `update_checkout` step that carries top-level submissions, and compares them
  with the step's asserted `messages[]` in order. Derivation covers
  `booking_question_answer_missing`, `booking_question_answer_invalid`,
  `booking_question_unknown`, `booking_questions_changed`, and
  `booking_question_answer_ignored`; a message marked `"policy": true` is
  business policy beyond the schema and is not derived, and a step marked
  `"derive": false` is skipped. `given.buyer_history.completed_sets` supplies
  prior once-per-buyer completions;
- requires an optional `evidence` member to name a `capability_id` in a
  `docs/requirement-evidence/` registry.

## Format: `fixtures/`

One JSON object per file. Fixtures are building blocks, not requirements, so
they are never cited in `specification.md`.

| Field | Meaning |
|---|---|
| `id` | Stable fixture identifier, for example `bq-fx-q-text-required`. |
| `kind` | `fixture`. |
| `schema` | Optional `file.json#/$defs/Name`. Every expansion must validate against it. |
| `parameters` | Map of name to `{"default": ...}`, `{"required": true}`, or `{"optional": true}` (an unbound optional parameter removes the member that uses it). |
| `body` | The JSON value. `{"$param": "name"}` substitutes a whole value; there is no string interpolation. `{"$use": "<fixture-id>", "with": {...}}` inlines another fixture, and sibling members are merged onto the inlined object. `{"$use": "vector:<id>#<json-pointer>"}` reuses part of an existing vector. |

An unknown or missing required parameter, an unresolved reference, a reference
cycle, or nesting deeper than 8 levels fails the checker.

## Format: `compose`

A composed vector lives under `flow/` with `kind: compose`. It builds scenarios
from fixtures, generates combinations from declared factors, and derives each
combination's result from explicit per-level effects. The checker expands it
into ordinary flow cases and runs every booking-questions flow check on each,
including the independent message derivation, so declared effects cannot
silently agree with themselves.

| Member of `compose` | Meaning |
|---|---|
| `base` | Shared `given` / `when` scenario built from `$use` references. `when.steps[]` entries carry a `stage`. |
| `stages` | Ordered stages, each with a `default` result (`status` becomes `final_status`). |
| `factors` | Ordered map of factor to levels. A level has optional `apply` (RFC 6902 operations, or `{"merge": ...}` for RFC 7396) applied to the unresolved `base` in factor order, and `effects`. An effect names a `stage` and a `reject` (`outcome_code`, `path`, optional `content`), a `result`, and/or `then` assertions. |
| `invariants` | Named assertions every case must satisfy: `no_booking_resource_when_create_rejected`, `hold_expires_at_and_capacity_unchanged_when_create_rejected`, `no_payment_authorized_or_captured_before_confirmed`, `bare_acknowledgement_never_resolves_action`, `messages_never_echo_answer_values`. |
| `exclude` | Level combinations that are not meaningful, each with a written `reason`. |
| `anchors` | Hand-written expected results keyed by `factor=level,...`. Every composition anchors the all-pass case (each factor's first level) and every single-factor deviation from it. |
| `max_cases` | Upper bound on generated cases, default 64. |

The evaluation rule is fixed by the format: stages run in order (a stage runs
only when a step for it exists); if any effect rejects at a stage, the result is
a rejection whose messages hold one entry per rejecting effect in factor order,
and later stages are unreached; otherwise the result is the last `result`
effect, or the stage default. Conflicting non-reject results fail the checker.

Generated case ids are `<id>[<factor>=<level>,...]`. Only the parent id is
cited. Print the plain expanded cases with:

```bash
python tools/usp_check.py vectors --expand bq-flow-phone-text-ack-combined
```

## Booking-questions vectors

The full list, grouped by topic, is in specification §11.4.14. Wire vectors
validate question definitions and answers, eval vectors recompute condition
applicability, flow vectors pin eligibility, submission, lifecycle, Action, and
privacy outcomes, and `bq-flow-phone-text-ack-combined` composes a required
phone number, a required text answer, and an acknowledgment into 12 cases.
Requirement-derived scenarios cite a provider-neutral `evidence` capability id
from [`docs/requirement-evidence/booking-questions.json`](../../docs/requirement-evidence/booking-questions.json),
never a product name.

## The keys are deliberately published

`key.private_key_d` is in the repository on purpose. These are test keys derived
from fixed seeds (`0x01…01` and `0x02…02`) so that anyone can regenerate the
vectors byte-for-byte and confirm the signatures independently. **They are not
secret and must never be used for anything.** `K1` is the legitimate platform;
`K2` exists solely to be rejected by `006-cross-key-replay`.

## What the checker verifies

- Every published JCS serialization and `usp_p` digest is recomputed. Non-integer
  JSON numbers are refused outright, which turns the specification's
  RECOMMENDATION about them into something a vector author cannot violate.
- Every signature is verified against the JWK in its own proof header, and every
  published thumbprint is recomputed from that JWK.
- `expected_claims` matches the signed payload.
- A `pop_key_mismatch` vector actually uses a key differing from the credential's
  `cnf.jkt` — otherwise it would pass while testing nothing.
- Every `reject_code` is reachable from both error-code mirrors.
- Every `id` is cited in `specification.md`.
- Every `wire/` case's schema validity, member-name violations, semantic
  errors, answer cases, and conformance match what the vector asserts.
- Every `eval/` case's definition validity and applicability match.
- Every fixture's default expansion validates, and every composed vector expands
  within its limits, satisfies its invariants, and matches its anchors.
- Every `docs/requirement-evidence/` registry has the required metadata, allowed
  source types and statuses, ordered full dates, `https://` sources, the fixed
  claim scope, globally unique capability ids, and cited vectors that exist.

## Adding a vector

Add the file, cite its `id` in `specification.md`, and run the checker. If it is
a rejection case, prefer one that a *plausible* implementation would accept —
`006` is the model: it is a genuinely valid signature that must still be
rejected. A rejection vector that fails for an obvious reason tests the parser,
not the protocol.
