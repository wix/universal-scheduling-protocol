# Rate Limited

**Type URI:** `https://usp-protocol.dev/errors/rate-limited`

The caller has exceeded the applicable request rate.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
