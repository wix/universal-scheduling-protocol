# Actions Pending

**This is not a Problem type.** `actions_pending` is a **business outcome
code**, not an RFC 9457 Problem Details `type`. There is no
`https://usp-protocol.dev/errors/actions-pending` URI to branch on.

Non-payment actions must be completed before payment can proceed. It is returned
when `confirm-payment` or `complete_checkout` is called while non-payment
actions are still pending.

The business processed the request successfully and is reporting a scheduling
outcome, so it is carried with HTTP `200 OK`:

- **REST:** an entry in the response body's `messages[]` array.
- **MCP:** an entry in `result.structuredContent.messages[]`.

Severity is `requires_buyer_input`: the buyer must complete the outstanding
actions before the flow can continue.

Clients branch on `messages[].code`, not on a `type` URI. See the business
outcome code registry in specification Section 9.4.2.
