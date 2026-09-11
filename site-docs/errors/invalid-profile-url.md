# Invalid Profile URL

**Type URI:** `https://usp-protocol.dev/errors/invalid-profile-url`

The supplied profile URL is malformed, uses a non-HTTPS scheme, or cannot be
resolved.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
