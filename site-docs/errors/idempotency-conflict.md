# Idempotency Conflict

**Type URI:** `https://usp-protocol.dev/errors/idempotency-conflict`

An idempotency key was reused with a different request.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
