# Payment Failed

**Type URI:** `https://usp-protocol.dev/errors/payment-failed`

Payment could not be authorized or captured.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
