# Signature Expired

**Type URI:** `https://usp-protocol.dev/errors/signature-expired`

The HTTP message signature is outside its accepted time window.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
