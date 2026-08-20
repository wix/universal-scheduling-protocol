# Profile Not Trusted

**Type URI:** `https://usp-protocol.dev/errors/profile-not-trusted`

The discovered protocol profile is not trusted under local policy.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
