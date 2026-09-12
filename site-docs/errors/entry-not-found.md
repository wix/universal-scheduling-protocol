# Entry Not Found

**Type URI:** `https://usp-protocol.dev/errors/entry-not-found`

The waitlist entry identified in the request path does not exist or is not
visible to the caller.

Emitted only by businesses that advertise the
`dev.usp-protocol.services.waitlist` capability.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
