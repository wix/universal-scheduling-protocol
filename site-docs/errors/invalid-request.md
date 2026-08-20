# Invalid Request

**Type URI:** `https://usp-protocol.dev/errors/invalid-request`

The request is malformed or violates protocol requirements.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
