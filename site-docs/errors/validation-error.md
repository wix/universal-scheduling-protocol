# Validation Error

**Type URI:** `https://usp-protocol.dev/errors/validation-error`

One or more request fields failed validation.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
