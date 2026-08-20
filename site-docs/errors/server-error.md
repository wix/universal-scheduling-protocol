# Server Error

**Type URI:** `https://usp-protocol.dev/errors/server-error`

The server encountered an unexpected failure.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
