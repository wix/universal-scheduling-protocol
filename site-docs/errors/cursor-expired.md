# Cursor Expired

**Type URI:** `https://usp-protocol.dev/errors/cursor-expired`

The supplied pagination cursor is no longer honored. Restart from the first page
by omitting the cursor.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
