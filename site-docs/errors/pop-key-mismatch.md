# Pop Key Mismatch

**Type URI:** `https://usp-protocol.dev/errors/pop-key-mismatch`

The proof-of-possession key does not match the bound key.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
