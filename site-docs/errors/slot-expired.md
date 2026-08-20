# Slot Expired

**Type URI:** `https://usp-protocol.dev/errors/slot-expired`

The selected slot or hold expired before completion.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
