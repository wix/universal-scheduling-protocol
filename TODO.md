# USP Specification — TODO

## Done

- [x] Add `availability_hint` to Service Schema for agent-assisted discovery
- [x] Add agent use cases table (10 scenarios)
- [x] Remove day-level granularity; simplify to hint → slot → hold
- [x] Redesign high-level architecture diagram (USP/UCP split)
- [x] Remove Credential Provider from architecture diagram
- [x] Remove unspecified intake form references

## Core Protocol Gaps

- [ ] **Error response schema** — no standard error format, HTTP status code mapping, or error code catalog (e.g., `slot_unavailable` is referenced but never formally defined)
- [ ] **Authentication** — no specification of platform-to-business or business-to-platform auth/authorization
- [ ] **Idempotency** — no idempotency keys for `create_booking` or hold operations
- [ ] **Webhook specification** — events are listed but payload schema, delivery format, retry policy, and subscription/registration mechanism are missing
- [ ] **Webhook signing** — "JWS using keys published in the business profile" is mentioned but key location, format, and JWS details are not specified

## Underspecified Schemas

- [ ] **Location schema** — `locations`, `slot.location`, and `booking.location` use `{id, name}` but full schema (address, coordinates) is not defined
- [ ] **Channel schema** — `virtual_provider` and `instructions` fields are listed but not defined
- [ ] **Capacity/waitlist** — `capacity.waitlist` is mentioned but type and semantics are not specified
- [ ] **Message/error codes** — `messages` have `type`, `code`, `message`, `severity` but no catalog of codes
- [ ] **Pricing models** — `variable`, `per_person`, `hourly` are listed but derivation rules are not fully specified
- [ ] **Deposit schema** — `deposit.value` type (integer vs percentage) and `refundable` semantics are not specified
- [ ] **Opening hours** — appears in availability response but has no formal schema definition
- [ ] **List Services filters** — example shows `type` and `category_id` but no full filter schema
- [ ] **Pagination** — cursor format and semantics are not specified

## Behavioral Gaps

- [ ] **Manual confirmation** — duration of `pending` state and expiration behavior are not specified
- [ ] **Reschedule flow** — whether a new hold is required for `new_slot_id` is not specified
- [ ] **Cancellation refunds** — refund timing and how it surfaces in the booking response are not specified
- [ ] **Policy temporal references** — `free_cancellation_until`, `free_reschedule_until` don't specify what they're relative to (booking start? creation time?)
- [ ] **Resource mismatch** — behavior when `resource_id` matches no slots is undefined (empty result vs error)
- [ ] **Slot pricing override** — conditions for when slot-level pricing applies vs service pricing are not specified

## UCP Integration Gaps

- [ ] **Partial UCP failures** — no guidance on handling `submit_checkout` failure and its effect on USP booking state
- [ ] **`usp_booking` metadata governance** — schema is shown but compatibility with UCP changes is not addressed
- [ ] **`payment_url` fallback** — documented as fallback for non-UCP businesses but usage and payment completion signaling are not specified
- [ ] **Shared `buyer` object** — "identity linking capability" is mentioned but not defined in USP

## Transport & Discovery

- [ ] **MCP transport binding** — listed as a transport option but no endpoint spec, schema, or operation mapping
- [ ] **A2A (Agent Card)** — listed as a transport but not defined
- [ ] **Platform profile schema** — `USP-Agent` header and `_meta.usp.profile` are referenced but profile structure is not specified
- [ ] **Extensions mechanism** — "extends" concept is mentioned with examples but has no schema, discovery, or API contract

## Future Considerations

- [ ] Intake forms / custom fields capability (as an extension)
- [ ] Recurring bookings
- [ ] Multi-service / package bookings
- [ ] Loyalty and rewards integration
- [ ] Rating and review capability
