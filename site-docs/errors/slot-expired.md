# Slot Expired

**This is not a Problem type, and it is not a USP error code.** No USP operation
emits `slot_expired`, and there is no
`https://usp-protocol.dev/errors/slot-expired` URI to branch on. This page
exists so that older links resolve to the correct replacement.

The condition it described - a held slot that expired before the booking could
be completed - is reported as **`hold_expired`**, a business outcome code
carried with HTTP `200 OK`:

- **REST:** an entry in the response body's `messages[]` array.
- **MCP:** an entry in `result.structuredContent.messages[]`.

Severity is `recoverable`: the hold is gone, but the platform can query
availability again and place a new hold.

See the business outcome code registry in specification Section 9.4.2, and
Section 4.2 for hold lifetime rules.
