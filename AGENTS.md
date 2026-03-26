# AGENTS.md

## Change Log Policy

After completing any set of file changes in this repository, you 
MUST append a new entry to the root-level `CHANGE_LOG.md` file before finishing your response.

### Entry format

Each entry is a level-2 heading followed by a bulleted list:

    ## DD/MM/YY at HH:MM:SS by [<git_username>](mailto:<git_email>)

    - <change description>
    - <change description>

Where:
- `DD/MM/YY` is the current date (day/month/year, zero-padded)
- `HH:MM:SS` is the current time in the user's local timezone (24-hour, zero-padded)
- `<git_username>` is the output of `git config user.name`
- `<git_email>` is the output of `git config user.email`. If unavailable, use the plain username without a mailto link
- Each bullet describes one logical change with its **motivation or rationale** (e.g. "Fixed the bug where X caused Y", "Added missing Z required by W"), not just what was changed

### Rules

1. Append new entries to the **start** of the file (newest first)
2. Separate each entry from the previous one with a blank line and a horizontal rule (`---`)
3. If you make changes across multiple files, group related changes into a single entry
4. Do NOT edit or remove existing entries
5. Obtain the current date, time, and git username at the time you write the entry - do not guess or reuse stale values

## JSON Schema and binding artifacts (no duplication)

Domain data shapes MUST exist **once**, under [`schemas/`](schemas/) as JSON Schema **`$defs`**. The REST and MCP bindings are **overlays** only: paths, operations, parameters, request/response shapes, and examples.

### Rules

1. **Canonical definitions** — Add or change the real schema in the appropriate file in `schemas/` (e.g. [`schemas/catalog.json`](schemas/catalog.json), [`schemas/booking.json`](schemas/booking.json), [`schemas/usp.json`](schemas/usp.json), [`schemas/profile.json`](schemas/profile.json), [`schemas/registry.json`](schemas/registry.json), [`schemas/rest_common.json`](schemas/rest_common.json) for REST-only shared types such as Problem Details and feed subscriptions). Do not paste parallel copies into [`openapi/usp-rest.json`](openapi/usp-rest.json) or [`openrpc/usp-mcp.json`](openrpc/usp-mcp.json).

2. **Thin references in bindings** — In OpenAPI `components.schemas` and OpenRPC `components.schemas`, each named schema SHOULD be a **single** external reference, for example:
   `{ "$ref": "../schemas/catalog.json#/$defs/Service" }`.
   Internal pointers (e.g. `#/components/schemas/Service`) stay stable; the body lives only in `schemas/`.

3. **No intentional duplication** — Do not maintain “the same” object inline in a binding file for self-containment or IDE convenience. If consumers need one file, produce a **bundled** artifact (e.g. Redocly or Swagger CLI bundle) in CI or docs; the **editable** source remains multi-file with `$ref`s.

4. **REST/MCP-specific wrappers** — If a binding needs a shape that is not a pure domain type (e.g. MCP `_meta` or HTTP-only headers), define the minimal wrapper in the binding **or** add a small `$def` in `schemas/` if it is shared across bindings. Avoid copying whole domain objects inside those wrappers; reference `$defs` instead.

5. **Verification** — Before finishing a change that touches bindings, confirm `components.schemas` entries are not large inline `"type": "object"` trees. Grep for duplicated concept names across `schemas/` and `openapi/` / `openrpc/` if unsure.

### Why this matters

Duplicated schemas drift (one copy updated, the other not), break validators, and confuse implementers. One definition in `schemas/` plus `$ref` from [`openapi/usp-rest.json`](openapi/usp-rest.json) and [`openrpc/usp-mcp.json`](openrpc/usp-mcp.json) matches how this repository avoids that class of errors.
