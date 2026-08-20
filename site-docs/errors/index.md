# Problem types

USP uses RFC 9457 Problem Details. Every canonical `type` URI is under
`https://usp-protocol.dev/errors/` and uses a kebab-case slug.

## Registry

- [`actions-pending`](actions-pending.md): Required follow-up actions have not completed.
- [`algorithm-unsupported`](algorithm-unsupported.md): The requested signature or digest algorithm is not supported.
- [`authentication-required`](authentication-required.md): The operation requires valid authentication.
- [`booking-not-found`](booking-not-found.md): The requested booking does not exist or is not visible to the caller.
- [`digest-mismatch`](digest-mismatch.md): The supplied content digest does not match the request content.
- [`hold-limit-exceeded`](hold-limit-exceeded.md): The caller or buyer has reached the allowed active hold limit.
- [`idempotency-conflict`](idempotency-conflict.md): An idempotency key was reused with a different request.
- [`invalid-request`](invalid-request.md): The request is malformed or violates protocol requirements.
- [`key-not-found`](key-not-found.md): The verification key identified by the request could not be found.
- [`payment-failed`](payment-failed.md): Payment could not be authorized or captured.
- [`pop-key-mismatch`](pop-key-mismatch.md): The proof-of-possession key does not match the bound key.
- [`pop-proof-missing`](pop-proof-missing.md): A required proof-of-possession proof was not supplied.
- [`pop-proof-replayed`](pop-proof-replayed.md): The proof-of-possession proof has already been used.
- [`profile-not-trusted`](profile-not-trusted.md): The discovered protocol profile is not trusted under local policy.
- [`profile-unreachable`](profile-unreachable.md): The protocol profile could not be fetched.
- [`range-too-wide`](range-too-wide.md): The requested availability range exceeds the supported limit.
- [`rate-limited`](rate-limited.md): The caller has exceeded the applicable request rate.
- [`reschedule-limit-reached`](reschedule-limit-reached.md): The booking has reached its allowed reschedule limit.
- [`revision-mismatch`](revision-mismatch.md): The supplied resource revision does not match the current revision.
- [`server-error`](server-error.md): The server encountered an unexpected failure.
- [`signature-expired`](signature-expired.md): The HTTP message signature is outside its accepted time window.
- [`signature-invalid`](signature-invalid.md): The HTTP message signature could not be verified.
- [`signature-missing`](signature-missing.md): A required HTTP message signature was not supplied.
- [`slot-expired`](slot-expired.md): The selected slot or hold expired before completion.
- [`slot-unavailable`](slot-unavailable.md): The selected slot is no longer available.
- [`validation-error`](validation-error.md): One or more request fields failed validation.
