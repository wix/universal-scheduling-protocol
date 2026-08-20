# Algorithm Unsupported

**Type URI:** `https://usp-protocol.dev/errors/algorithm-unsupported`

The requested signature or digest algorithm is not supported.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
