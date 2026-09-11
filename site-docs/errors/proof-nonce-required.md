# Proof Nonce Required

**Type URI:** `https://usp-protocol.dev/errors/proof-nonce-required`

The business requires a nonce in the proof of possession. The response carries
the nonce; the client retries with a freshly built proof that includes it.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
