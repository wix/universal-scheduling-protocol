# Proof of Possession Required

**Type URI:** `https://usp-protocol.dev/errors/pop-proof-required`

A sender-constrained credential was presented without a valid proof of
possession. The credential must not be accepted as a bearer token.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
