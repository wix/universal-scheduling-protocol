#!/usr/bin/env bash
# Build the canonical docs and authority artifacts served by GitHub Pages.
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m mkdocs build

python3 - site <<'PY'
import json
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

root = Path.cwd()
site = root / sys.argv[1]
origin = "https://usp-protocol.dev"

for source in sorted((root / "schemas").glob("*.json")):
    schema = json.loads(source.read_text())
    schema_id = schema.get("$id")
    if not isinstance(schema_id, str) or not schema_id.startswith(origin + "/"):
        raise SystemExit(f"{source}: $id must use {origin}")
    parsed = urlparse(schema_id)
    if parsed.query or parsed.fragment:
        raise SystemExit(f"{source}: $id must not contain query or fragment")
    destination = site / parsed.path.lstrip("/")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)

bindings = {
    root / "openapi" / "usp-rest.json":
        site / "schemas" / "openapi" / "usp-rest.json",
    root / "openrpc" / "usp-mcp.json":
        site / "schemas" / "openrpc" / "usp-mcp.json",
}
for source, destination in bindings.items():
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)

# GitHub Pages cannot configure arbitrary 301 responses. Keep the former
# binding paths as direct static copies so existing tooling still receives JSON
# while all normative references use the canonical /schemas paths.
legacy = {
    bindings[root / "openapi" / "usp-rest.json"]:
        site / "services" / "rest.openapi.json",
    bindings[root / "openrpc" / "usp-mcp.json"]:
        site / "services" / "mcp.openrpc.json",
}
for source, destination in legacy.items():
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
PY

echo "Built canonical site and protocol artifacts in site/"
