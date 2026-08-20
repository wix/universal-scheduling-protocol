# Booking Not Found

**Type URI:** `https://usp-protocol.dev/errors/booking-not-found`

The requested booking does not exist or is not visible to the caller.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
