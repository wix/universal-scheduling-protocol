# Digest Mismatch

**Type URI:** `https://usp-protocol.dev/errors/digest-mismatch`

The supplied content digest does not match the request content.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
