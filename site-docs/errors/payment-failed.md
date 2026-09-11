# Payment Failed

**This is not a Problem type.** `payment_failed` is an **Embedded Scheduling
Protocol (ESP) frame code**, not an RFC 9457 Problem Details `type`. There is no
`https://usp-protocol.dev/errors/payment-failed` URI to branch on.

The payment credential was declined during an embedded scheduling flow.

It is delivered as the `code` of an `esp.error` postMessage frame between the
host application and the embedded scheduling iframe. It is not an HTTP response
and not a JSON-RPC error. The code is recoverable: the host can prompt for a
different payment credential and retry.

See specification Section 9.5.5 for the ESP error frame shape and the full list
of well-known `esp.error` codes.

!!! note "Looking for HTTP payment errors?"

    Payment conditions on the REST and MCP bindings use the business outcome
    codes `payment_required`, `payment_expired`, and `payment_amount_mismatch`,
    carried in `messages[]` with HTTP `200 OK`. See specification Section 9.4.2.
