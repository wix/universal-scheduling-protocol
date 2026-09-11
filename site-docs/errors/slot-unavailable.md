# Slot Unavailable

**This is not a Problem type.** `slot_unavailable` is a **business outcome
code**, not an RFC 9457 Problem Details `type`. There is no
`https://usp-protocol.dev/errors/slot-unavailable` URI to branch on.

The selected slot is no longer available.

The business processed the request successfully and is reporting a scheduling
outcome, so it is carried with HTTP `200 OK`:

- **REST:** an entry in the response body's `messages[]` array.
- **MCP:** an entry in `result.structuredContent.messages[]`.

Severity is `recoverable`: the platform can query availability again and retry
with a different slot.

Clients branch on `messages[].code`, not on a `type` URI. See the business
outcome code registry in specification Section 9.4.2.

!!! note "A separate ESP code shares this name"

    The Embedded Scheduling Protocol defines an `esp.error` frame code also
    named `slot_unavailable`, for a slot that became unavailable during an
    embedded flow. That is a postMessage frame, not an HTTP response. See
    specification Section 9.5.5.
