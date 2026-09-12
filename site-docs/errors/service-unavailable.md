# Service Unavailable

**Type URI:** `https://usp-protocol.dev/errors/service-unavailable`

The business is temporarily unable to handle requests. Responses should carry a
`Retry-After` header.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
