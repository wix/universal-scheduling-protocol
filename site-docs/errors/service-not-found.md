# Service Not Found

**Type URI:** `https://usp-protocol.dev/errors/service-not-found`

The service identified in the request path does not exist or is not visible to
the caller. Returned with `404 Not Found` by `GET /services/{service_id}`.

Service identifiers are opaque, so this applies to any path segment the
business does not recognize as one of its service identifiers, whatever its
format. A missing service is never answered with `400` or `500`.

Over MCP, the same condition is JSON-RPC `-32602` with `data.code`
`service_not_found`.

An unresolved ID in the `POST /services/lookup` request body is not this
problem type. It is the `service_unresolved` business outcome, carried as a
`messages[]` warning with HTTP `200 OK`.

Servers use this URI as the `type` member of an RFC 9457 Problem Details
response. Clients must branch on the exact URI, not the human-readable title.
