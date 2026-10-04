# Confirmation Failed

**Type URI:** `https://usp-protocol.dev/errors/confirmation-failed`

A `POST /bookings/{booking_id}/confirm-payment` call was accepted, but the
booking did not reach the status the booking lifecycle requires once the
payment action completes. Returned with `409 Conflict`.

The buyer has paid for a booking that is not confirmed. A platform must not
report it to the buyer as confirmed. It should reverse or refund the payment
through the checkout system that collected it, and should not retry the same
request unchanged.

Over MCP, the same condition is JSON-RPC `-32002` with `data.code`
`confirmation_failed`.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
