# Range Too Wide

**Type URI:** `https://usp-protocol.dev/errors/range-too-wide`

The requested availability range exceeds the supported limit.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
