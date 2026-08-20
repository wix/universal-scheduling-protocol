# USP namespace registry

The USP governing body reserves `dev.usp-protocol.*`. Capability entries in
this namespace must use `https://usp-protocol.dev` for their `spec` and
`schema` origins.

## Reserved capability names

- `dev.usp-protocol.services`
- `dev.usp-protocol.services.catalog`
- `dev.usp-protocol.services.catalog.subscriptions`
- `dev.usp-protocol.services.availability`
- `dev.usp-protocol.services.bookings`
- `dev.usp-protocol.services.paid_bookings`
- `dev.usp-protocol.services.waitlist`
- `dev.usp-protocol.discovery.registry`
- `dev.usp-protocol.platform.calendar_freebusy`

Names below this authority are assigned by the USP specification. Vendors must
use a namespace derived from an origin they control, such as
`com.example.services.courses`, and must follow the origin-binding rules in
[Namespace Governance](specification/index.md#25-namespace-governance).
