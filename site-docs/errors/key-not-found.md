# Key Not Found

**Type URI:** `https://usp-protocol.dev/errors/key-not-found`

The verification key identified by the request could not be found.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
