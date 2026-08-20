# Namespace authority migration

USP `2026-08-20` is a breaking hard cutover to an authority the project owns.
There is no dual-acceptance period in the protocol specification.

## Required changes

| Before `2026-08-20` | From `2026-08-20` |
|---|---|
| `dev.usp.*` | `dev.usp-protocol.*` |
| `https://usp.dev` | `https://usp-protocol.dev` |
| `/services/rest.openapi.json` | `/schemas/openapi/usp-rest.json` |
| `/services/mcp.openrpc.json` | `/schemas/openrpc/usp-mcp.json` |
| `/problems/{slug}` | `/errors/{kebab-case-slug}` |
| `/spec/{date}#{fragment}` | `/specification#{canonical-fragment}` |

Implementations must rename every advertised or accepted USP capability key and
move profile `spec`, `schema`, and Problem Details `type` values in the same
release. A mixed deployment cannot negotiate reliably because old and new
capability names are distinct protocol identifiers.

## Release coordination

1. Deploy this specification and its published artifacts.
2. Verify all advertised authority URLs return 200 over HTTPS.
3. Cut over the CLI, business adapter, registry, and checkout advertisers in one
   coordinated release.
4. Verify live profiles advertise only the new namespace.

The downstream implementation changes and the owner-operated redirect from
`usp.live` to `usp-protocol.dev` are external to this repository.
