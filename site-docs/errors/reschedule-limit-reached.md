# Reschedule Limit Reached

**This is not a Problem type.** `reschedule_limit_reached` is a **business
outcome code**, not an RFC 9457 Problem Details `type`. There is no
`https://usp-protocol.dev/errors/reschedule-limit-reached` URI to branch on.

The booking has reached the maximum number of reschedules its service policy
allows.

The business processed the request successfully and is reporting a policy
outcome, so it is carried with HTTP `200 OK`:

- **REST:** an entry in the response body's `messages[]` array.
- **MCP:** an entry in `result.structuredContent.messages[]`.

Severity is `requires_buyer_review`: the buyer must decide whether to keep the
existing booking or cancel it.

Clients branch on `messages[].code`, not on a `type` URI. See the business
outcome code registry in specification Section 9.4.2.
