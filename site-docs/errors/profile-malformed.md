# Profile Malformed

**Type URI:** `https://usp-protocol.dev/errors/profile-malformed`

The profile document is not valid JSON, or it fails schema validation against
`schemas/profile.json`.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
