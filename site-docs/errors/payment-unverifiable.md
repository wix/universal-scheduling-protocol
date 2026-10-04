# Payment Unverifiable

**Type URI:** `https://usp-protocol.dev/errors/payment-unverifiable`

A `POST /bookings/{booking_id}/confirm-payment` call could not be verified,
because the business has no price to check the payment against. For example,
the booking's service no longer exists, or a payable service states no price.
Returned with `409 Conflict`.

The booking is not confirmed. A platform must not report it to the buyer as
confirmed. It should reverse or refund the payment through the checkout
system that collected it, and should not retry the same request unchanged.

This is not `payment_amount_mismatch`. That business outcome applies when the
business has a price and the payment disagrees with it, and it is carried as a
`messages[]` entry with HTTP `200 OK`.

Over MCP, the same condition is JSON-RPC `-32002` with `data.code`
`payment_unverifiable`.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
