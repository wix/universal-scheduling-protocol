# Proof of Possession Invalid

**Type URI:** `https://usp-protocol.dev/errors/pop-proof-invalid`

The proof failed to parse or verify: a bad `typ`, a rejected `alg`, a signature
failure, or a mismatched `htm`/`htu`, `usp_m`/`aud`/`usp_p`, or `ath`.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
