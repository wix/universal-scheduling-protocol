# Reschedule Limit Reached

**Type URI:** `https://usp-protocol.dev/errors/reschedule-limit-reached`

The booking has reached its allowed reschedule limit.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
