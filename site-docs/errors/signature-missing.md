# Signature Missing

**Type URI:** `https://usp-protocol.dev/errors/signature-missing`

A required HTTP message signature was not supplied.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
