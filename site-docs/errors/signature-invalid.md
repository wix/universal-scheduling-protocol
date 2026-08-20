# Signature Invalid

**Type URI:** `https://usp-protocol.dev/errors/signature-invalid`

The HTTP message signature could not be verified.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
