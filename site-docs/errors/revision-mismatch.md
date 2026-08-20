# Revision Mismatch

**Type URI:** `https://usp-protocol.dev/errors/revision-mismatch`

The supplied resource revision does not match the current revision.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
