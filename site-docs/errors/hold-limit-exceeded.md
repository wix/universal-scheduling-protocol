# Hold Limit Exceeded

**Type URI:** `https://usp-protocol.dev/errors/hold-limit-exceeded`

The caller or buyer has reached the allowed active hold limit.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
