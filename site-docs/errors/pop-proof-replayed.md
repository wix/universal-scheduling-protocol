# Pop Proof Replayed

**Type URI:** `https://usp-protocol.dev/errors/pop-proof-replayed`

The proof-of-possession proof has already been used.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
