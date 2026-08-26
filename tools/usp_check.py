#!/usr/bin/env python3
"""Conformance checks for the USP specification repository.

Four subcommands, each useful on its own:

  schemas   Parse every JSON artefact, compile every file under schemas/ as a
            JSON Schema, assert the protocol version literal agrees across
            the five places that assert this repository's version identity,
            and instance-validate the §7.2 UCP profile examples against
            business_schema.

  refs      Resolve every $ref two ways - by JSON Schema $id base-URI rules and
            by filesystem path - and fail when the two disagree. Every $id under
            schemas/ declares a directory (services/, platform/) that the flat
            on-disk layout does not have, so a cross-level $ref can resolve on
            one strategy and 404 on the other. Also reports unreferenced $defs
            and enforces the CLAUDE.md rule that binding components.schemas
            entries are thin single $refs.

  vectors   Validate tests/vectors/ against the schemas, recompute every
            published JCS digest, and assert each vector's reject_code and id
            are actually reachable from the normative text.

  authority Enforce the owned origin and capability namespace, canonical URL
            layout, published artifact coverage, playground mirrors, problem
            pages, and stale-identifier absence.

Accepted pre-existing failures live one per line in tools/known-issues.txt.
That file is an explicit, reviewable debt ledger - not a suppression flag - and
emptying it is the acceptance criterion for the hygiene commit that closes the
last of them.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

REPO = Path(__file__).resolve().parent.parent
KNOWN_ISSUES = Path(__file__).resolve().parent / "known-issues.txt"

SCHEMA_DIR = REPO / "schemas"
OPENAPI = REPO / "openapi" / "usp-rest.json"
OPENRPC = REPO / "openrpc" / "usp-mcp.json"
SPEC = REPO / "specification.md"
README = REPO / "README.md"
ROADMAP = REPO / "site-docs" / "roadmap.md"
SITE = REPO / "site"
USP_ORIGIN = "https://usp-protocol.dev"

# JSON trees that must parse. Globs are relative to the repository root.
PARSE_GLOBS = [
    "schemas/*.json",
    "openapi/*.json",
    "openrpc/*.json",
    "docs/*.json",
    "playground/scenarios/*.json",
    "site-docs/playground/scenarios/*.json",
]

# Binding-local schemas with no upstream $def in schemas/. These are the only
# sanctioned exceptions to the CLAUDE.md "thin $ref" rule: they describe MCP
# envelope shapes, not domain data, so there is nothing in schemas/ to point at.
BINDING_LOCAL_SCHEMAS = {
    "McpAuthorization",
    "McpUspMetaPublic",
    "McpUspMetaPrivilegedPlatform",
    "McpUspMetaPrivilegedPlatformNoIdempotency",
    "McpUspMetaPrivilegedScoped",
    "McpUspMetaPrivilegedScopedNoIdempotency",
}

# $defs that are deliberately informative - published for implementers to read
# rather than to be $ref'd from anywhere. Distinct from tools/known-issues.txt,
# which records debt that is meant to be paid off.
INFORMATIVE_DEFS = {
    ("calendar_freebusy.json", "CalendarProviderConfig"),
}

# $refs pointing outside this repository are recorded, never resolved.
EXTERNAL_REF_PREFIXES = ("https://ucp.dev/", "http://ucp.dev/")

USP_SCHEMA_BASE = f"{USP_ORIGIN}/schemas/"

# The reserved dev.usp-protocol.* names. Checked two ways: they must appear in the
# published namespace registry (authority), and they must satisfy every propertyNames
# pattern that governs a capability or service key map (schemas). The second is what a
# namespace rename breaks silently -- the 2026-08-20 cutover to dev.usp-protocol.* left
# these patterns hyphen-hostile, so the profile the specification tells implementers to
# publish did not validate against the specification's own schema.
RESERVED_NAMESPACE_NAMES = {
    "dev.usp-protocol.services",
    "dev.usp-protocol.services.catalog",
    "dev.usp-protocol.services.catalog.subscriptions",
    "dev.usp-protocol.services.availability",
    "dev.usp-protocol.services.bookings",
    "dev.usp-protocol.services.paid_bookings",
    "dev.usp-protocol.services.waitlist",
    "dev.usp-protocol.discovery.registry",
    "dev.usp-protocol.platform.calendar_freebusy",
}

# Third-party namespaces the specification's own examples use, which the same patterns
# govern whenever a profile carries them alongside ours.
FOREIGN_NAMESPACE_NAMES = {
    "dev.ucp.shopping",
    "dev.ucp.shopping.checkout",
    "dev.ucp.common.identity_linking",
    "com.stripe.payments",
}


class Findings:
    """Collects failures, filtering those listed in tools/known-issues.txt."""

    def __init__(self) -> None:
        self.failures: list[str] = []
        self.suppressed: list[str] = []
        self.known = self._load_known()

    @staticmethod
    def _load_known() -> set[str]:
        if not KNOWN_ISSUES.exists():
            return set()
        out = set()
        for line in KNOWN_ISSUES.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                out.add(line)
        return out

    def fail(self, key: str, message: str) -> None:
        if key in self.known:
            self.suppressed.append(f"{key}: {message}")
        else:
            self.failures.append(f"{key}: {message}")

    def report(self, check: str) -> int:
        for line in self.suppressed:
            print(f"  known-issue  {line}")
        for line in self.failures:
            print(f"  FAIL  {line}")
        if self.failures:
            print(f"{check}: {len(self.failures)} failure(s), "
                  f"{len(self.suppressed)} known issue(s)")
            return 1
        print(f"{check}: ok ({len(self.suppressed)} known issue(s))")
        return 0


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def iter_json_files() -> list[Path]:
    seen: list[Path] = []
    for pattern in PARSE_GLOBS:
        seen.extend(sorted(REPO.glob(pattern)))
    return seen


def walk(node, pointer: str = ""):
    """Yield (json_pointer, value) for every node in a JSON document."""
    yield pointer, node
    if isinstance(node, dict):
        for key, value in node.items():
            token = key.replace("~", "~0").replace("/", "~1")
            yield from walk(value, f"{pointer}/{token}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{pointer}/{index}")


def resolve_pointer(doc, pointer: str):
    """Resolve an RFC 6901 JSON Pointer. Raises KeyError when absent."""
    if pointer in ("", "#"):
        return doc
    node = doc
    for token in pointer.lstrip("#").lstrip("/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            node = node[int(token)]
        elif isinstance(node, dict):
            node = node[token]
        else:
            raise KeyError(pointer)
    return node


def usp_uri_to_paths(uri: str) -> list[Path]:
    """Map a canonical USP schema URI onto candidate on-disk files.

    The published $id values carry directory segments (services/, platform/)
    that the flat schemas/ directory does not have, so both forms are tried.
    """
    tail = uri[len(USP_SCHEMA_BASE):]
    candidates = [SCHEMA_DIR / tail]
    if "/" in tail:
        candidates.append(SCHEMA_DIR / tail.rsplit("/", 1)[1])
    return candidates


# --------------------------------------------------------------------------
# check: schemas
# --------------------------------------------------------------------------

def read_version_literals() -> dict[str, str]:
    """The five places that assert this repository's version identity."""
    out: dict[str, str] = {}

    for label, path in (("specification.md", SPEC), ("README.md", README)):
        match = re.search(r"^\*\*Version:\*\*\s*`([^`]+)`", path.read_text(), re.M)
        out[label] = match.group(1) if match else "<missing>"

    for label, path in (("openapi", OPENAPI), ("openrpc", OPENRPC)):
        out[label] = json.loads(path.read_text()).get("info", {}).get("version", "<missing>")

    # First data row of the roadmap's Version History table is the current one.
    roadmap = "<missing>"
    rows = re.findall(r"^\|\s*`([0-9]{4}-[0-9]{2}-[0-9]{2})`\s*\|", ROADMAP.read_text(), re.M)
    if rows:
        roadmap = rows[0]
    out["site-docs/roadmap.md"] = roadmap
    return out


def check_schemas(findings: Findings) -> None:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("  jsonschema not installed; run: pip install -r requirements-dev.txt",
              file=sys.stderr)
        findings.fail("SCHEMAS:dependency", "jsonschema is not installed")
        return

    for path in iter_json_files():
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            findings.fail(f"PARSE:{rel(path)}", f"invalid JSON: {exc}")
            continue
        if path.parent == SCHEMA_DIR:
            try:
                Draft202012Validator.check_schema(doc)
            except Exception as exc:  # noqa: BLE001 - surface any validator complaint
                findings.fail(f"SCHEMA:{rel(path)}", f"not a valid JSON Schema: {exc}")

    # Internal anchors: a link to a section that does not exist reads as a
    # working cross-reference and silently goes nowhere.
    spec = SPEC.read_text()
    headings = set()
    for line in spec.splitlines():
        match = re.match(r"^#{2,6}\s+(.*)$", line)
        if match:
            slug = re.sub(r"[^\w\s-]", "", match.group(1).strip().lower())
            headings.add("#" + re.sub(r"\s+", "-", slug))
    for anchor in sorted(set(re.findall(r"\]\((#[a-z0-9-]+)\)", spec)) - headings):
        findings.fail(f"ANCHOR:{anchor}",
                      f"specification.md links to {anchor}, which matches no heading")

    versions = read_version_literals()
    distinct = set(versions.values())
    if len(distinct) != 1:
        detail = ", ".join(f"{k}={v}" for k, v in versions.items())
        findings.fail("VERSION:mismatch",
                      f"version identity disagrees across artefacts: {detail}")

    check_namespace_key_patterns(findings)
    check_section_72_profile_examples(findings)


def check_namespace_key_patterns(findings: Findings) -> None:
    """Every reserved capability/service name satisfies the patterns that gate it.

    A propertyNames pattern on a capability or service map is a wire contract: a name it
    rejects cannot appear as a key in a conforming profile, whatever the prose says.
    """
    usp = json.loads((SCHEMA_DIR / "usp.json").read_text())
    names = sorted(RESERVED_NAMESPACE_NAMES | FOREIGN_NAMESPACE_NAMES)

    sites = 0
    for pointer, node in walk(usp):
        if not isinstance(node, dict):
            continue
        constraint = node.get("propertyNames")
        if not isinstance(constraint, dict) or "pattern" not in constraint:
            continue
        if not pointer.endswith(("/services", "/capabilities")):
            continue
        sites += 1
        pattern = re.compile(constraint["pattern"])
        for name in names:
            if not pattern.fullmatch(name):
                findings.fail(f"NAMEPATTERN:{pointer}",
                              f"propertyNames pattern {constraint['pattern']!r} rejects "
                              f"the reserved name {name!r}")

    if not sites:
        findings.fail("NAMEPATTERN:coverage",
                      "no capability or service propertyNames constraint found in usp.json; "
                      "this check silently stopped covering anything")


JSON_FENCE = re.compile(r"```json\n(.*?)```", re.S)
SITE_UCP_NATIVE = REPO / "site-docs" / "deployment-modes" / "ucp-native.md"


def markdown_slice(text: str, start_pattern: str, end_pattern: str) -> str | None:
    """Return the body after a heading match, up to the next heading match."""
    start = re.search(start_pattern, text, re.M)
    if not start:
        return None
    rest = text[start.end():]
    end = re.search(end_pattern, rest, re.M)
    return rest[:end.start()] if end else rest


def parsed_json_fences(markdown: str) -> list[tuple[int, object | None, str | None]]:
    """Each ```json fence as (1-based index, parsed value or None, error)."""
    out = []
    for index, body in enumerate(JSON_FENCE.findall(markdown), start=1):
        try:
            out.append((index, json.loads(body), None))
        except json.JSONDecodeError as exc:
            out.append((index, None, str(exc)))
    return out


def ucp_profile_instances(fences: list[tuple[int, object | None, str | None]]) -> list[tuple[int, dict]]:
    docs = []
    for index, parsed, _error in fences:
        if isinstance(parsed, dict) and isinstance(parsed.get("ucp"), dict):
            docs.append((index, parsed))
    return docs


def business_schema_validator():
    """Draft 2020-12 validator for usp.json business_schema, with $id registry."""
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource

    profile = json.loads((SCHEMA_DIR / "profile.json").read_text())
    usp = json.loads((SCHEMA_DIR / "usp.json").read_text())
    registry = Registry().with_resources(
        (uri, Resource.from_contents(doc))
        for uri, doc in (
            (f"{USP_SCHEMA_BASE}profile.json", profile),
            (f"{USP_SCHEMA_BASE}usp.json", usp),
        )
    )
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": f"{USP_SCHEMA_BASE}usp.json#/$defs/business_schema",
    }
    return Draft202012Validator(schema, registry=registry)


def check_section_72_profile_examples(findings: Findings) -> None:
    """The published §7.2 UCP profiles must instance-validate as business_schema."""
    spec = SPEC.read_text()
    section = markdown_slice(spec, r"^### 7\.2\b", r"^### ")
    if section is None:
        findings.fail("EXAMPLE72:section",
                      "specification.md has no ### 7.2 heading; cannot validate profile examples")
        return

    fences = parsed_json_fences(section)
    for index, _parsed, error in fences:
        if error is not None:
            findings.fail(f"EXAMPLE72:parse:{index}",
                          f"§7.2 json fence {index} is not valid JSON: {error}")
            return

    profiles = ucp_profile_instances(fences)
    if len(profiles) < 2:
        findings.fail("EXAMPLE72:count",
                      f"§7.2 must contain at least two json documents with a top-level ucp object "
                      f"(paid and free-service profiles); found {len(profiles)}")
        return

    try:
        validator = business_schema_validator()
    except ImportError as exc:
        findings.fail("EXAMPLE72:dependency",
                      f"jsonschema/referencing is required to validate §7.2 profiles: {exc}")
        return

    for index, doc in profiles:
        errors = sorted(validator.iter_errors(doc["ucp"]), key=lambda e: list(e.path))
        if errors:
            err = errors[0]
            path = "/".join(str(p) for p in err.absolute_path) or "<root>"
            findings.fail(f"EXAMPLE72:schema:{index}",
                          f"§7.2 json fence {index} ucp object fails business_schema at {path}: "
                          f"{err.message}")

    if not SITE_UCP_NATIVE.is_file():
        findings.fail("EXAMPLE72:site-docs",
                      f"{rel(SITE_UCP_NATIVE)} is missing; the published site would drift from §7.2")
        return

    site_section = markdown_slice(
        SITE_UCP_NATIVE.read_text(),
        r"^## Profile Registration",
        r"^## Inherited Infrastructure",
    )
    if site_section is None:
        findings.fail("EXAMPLE72:site-docs",
                      "ucp-native.md is missing the Profile Registration section that mirrors §7.2")
        return

    site_fences = parsed_json_fences(site_section)
    for index, _parsed, error in site_fences:
        if error is not None:
            findings.fail(f"EXAMPLE72:site-parse:{index}",
                          f"ucp-native.md profile json fence {index} is not valid JSON: {error}")
            return

    site_profiles = ucp_profile_instances(site_fences)
    spec_ucp = [doc["ucp"] for _index, doc in profiles]
    site_ucp = [doc["ucp"] for _index, doc in site_profiles]
    if spec_ucp != site_ucp:
        findings.fail("EXAMPLE72:site-docs",
                      "site-docs/deployment-modes/ucp-native.md profile examples do not match "
                      "the §7.2 ucp objects in specification.md")


# --------------------------------------------------------------------------
# check: refs
# --------------------------------------------------------------------------

def collect_refs() -> list[tuple[Path, str, str]]:
    """Every ($ref-bearing file, json pointer of the $ref, ref value)."""
    out = []
    for path in sorted(SCHEMA_DIR.glob("*.json")) + [OPENAPI, OPENRPC]:
        doc = json.loads(path.read_text())
        for pointer, node in walk(doc):
            if isinstance(node, dict) and isinstance(node.get("$ref"), str):
                out.append((path, pointer, node["$ref"]))
    return out


def check_refs(findings: Findings) -> None:
    docs = {}
    for path in sorted(SCHEMA_DIR.glob("*.json")) + [OPENAPI, OPENRPC]:
        docs[path] = json.loads(path.read_text())

    # Which $defs are referenced from anywhere, keyed by (resolved file, name).
    referenced: set[tuple[Path, str]] = set()

    for path, pointer, ref in collect_refs():
        if ref.startswith(EXTERNAL_REF_PREFIXES):
            continue

        file_part, _, fragment = ref.partition("#")
        fragment = fragment or ""

        if not file_part:  # internal ref
            target_path = path
        else:
            base_id = docs[path].get("$id")
            fs_candidate = (path.parent / file_part).resolve()

            if file_part.startswith(USP_SCHEMA_BASE):
                id_candidates = usp_uri_to_paths(file_part)
            elif base_id:
                id_candidates = usp_uri_to_paths(urljoin(base_id, file_part))
            else:
                # Binding files carry no $id; filesystem resolution is the only
                # applicable strategy, so the agreement check does not apply.
                id_candidates = [fs_candidate]

            id_hit = next((c for c in id_candidates if c.exists()), None)
            fs_hit = fs_candidate if fs_candidate.exists() else None

            if id_hit is None and fs_hit is None:
                findings.fail(f"REF:{rel(path)}:{ref}",
                              f"$ref at {pointer} resolves to no file "
                              f"(tried {[str(c) for c in id_candidates]})")
                continue
            if id_hit is not None and fs_hit is not None and id_hit != fs_hit:
                findings.fail(f"REF:{rel(path)}:{ref}",
                              f"$ref at {pointer} resolves differently by $id "
                              f"({rel(id_hit)}) and by path ({rel(fs_hit)})")
                continue
            if id_hit is None:
                findings.fail(f"REF:{rel(path)}:{ref}",
                              f"$ref at {pointer} resolves on the filesystem but not "
                              f"under $id base-URI rules "
                              f"(would be {[str(c) for c in id_candidates]})")
                continue
            target_path = id_hit

        # A *relative* $ref between two schema files whose $id values sit in
        # different directory segments is broken under $id base-URI rules even
        # though it resolves on the filesystem, because the published $id
        # segments (services/, platform/) do not exist on disk. The flat
        # fallback above deliberately tolerates same-level refs, so this is the
        # check that actually catches the cross-level case.
        if (file_part
                and not file_part.startswith(USP_SCHEMA_BASE)
                and path.parent == SCHEMA_DIR
                and target_path.parent == SCHEMA_DIR):
            def id_dir(p: Path) -> str:
                doc_id = docs.get(p, {}).get("$id", "") if p in docs else \
                    json.loads(p.read_text()).get("$id", "")
                tail = doc_id[len(USP_SCHEMA_BASE):] if doc_id.startswith(USP_SCHEMA_BASE) else ""
                return tail.rsplit("/", 1)[0] if "/" in tail else ""

            if id_dir(path) != id_dir(target_path):
                findings.fail(
                    f"REFLEVEL:{rel(path)}:{ref}",
                    f"relative $ref at {pointer} crosses an $id directory level "
                    f"({id_dir(path) or '<root>'} -> {id_dir(target_path) or '<root>'}); "
                    f"it resolves on the filesystem but under $id rules names "
                    f"a document that does not exist. Write it as the absolute "
                    f"canonical URI, or move the definition to a same-level file")

        if target_path not in docs:
            try:
                docs[target_path] = json.loads(target_path.read_text())
            except (OSError, json.JSONDecodeError) as exc:
                findings.fail(f"REF:{rel(path)}:{ref}", f"target unreadable: {exc}")
                continue

        if fragment:
            try:
                resolve_pointer(docs[target_path], fragment)
            except (KeyError, IndexError, ValueError):
                findings.fail(f"REF:{rel(path)}:{ref}",
                              f"$ref at {pointer} names a fragment that does not "
                              f"exist in {rel(target_path)}")
                continue
            if fragment.startswith("/$defs/"):
                referenced.add((target_path, fragment.split("/")[2]))

    # Unreferenced $defs: a definition nothing points at is usually an
    # extension that was declared but never wired up.
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        doc = docs[path]
        root_ref = doc.get("$ref", "")
        allof_refs = {
            item.get("$ref", "")
            for item in doc.get("allOf", []) if isinstance(item, dict)
        }
        for name in doc.get("$defs", {}):
            if (path, name) in referenced:
                continue
            if (path.name, name) in INFORMATIVE_DEFS:
                continue
            pointer = f"#/$defs/{name}"
            if root_ref == pointer or pointer in allof_refs:
                continue
            findings.fail(f"UNREFERENCED:{rel(path)}:{name}",
                          f"$defs/{name} is not referenced by anything")

    # CLAUDE.md: binding components.schemas entries are single $refs.
    for path in (OPENAPI, OPENRPC):
        for name, entry in docs[path].get("components", {}).get("schemas", {}).items():
            if name in BINDING_LOCAL_SCHEMAS:
                continue
            if not (isinstance(entry, dict) and list(entry.keys()) == ["$ref"]):
                findings.fail(f"THINREF:{rel(path)}:{name}",
                              "components.schemas entry is not a single $ref "
                              "(see CLAUDE.md: definitions live once in schemas/)")


# --------------------------------------------------------------------------
# check: vectors
# --------------------------------------------------------------------------

def jcs(value) -> bytes:
    """RFC 8785 JSON Canonicalization Scheme.

    Non-integer numbers raise: USP RECOMMENDS that canonicalized params avoid
    them precisely so JCS's ES6 number-serialization edge never bites, and
    refusing them here is what turns that RECOMMENDATION into something a
    vector author cannot accidentally violate.
    """
    if value is None:
        return b"null"
    if value is True:
        return b"true"
    if value is False:
        return b"false"
    if isinstance(value, int):
        return str(value).encode()
    if isinstance(value, float):
        if value != int(value):
            raise ValueError(
                f"non-integer JSON number {value!r} in canonicalized input; "
                "USP RECOMMENDS avoiding these (see specification.md 9.2.2)")
        return str(int(value)).encode()
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False).encode("utf-8")
    if isinstance(value, list):
        return b"[" + b",".join(jcs(v) for v in value) + b"]"
    if isinstance(value, dict):
        items = sorted(value.items(), key=lambda kv: kv[0].encode("utf-16-be"))
        body = b",".join(jcs(k) + b":" + jcs(v) for k, v in items)
        return b"{" + body + b"}"
    raise TypeError(f"not JSON: {value!r}")


def b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def unb64u(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def spec_error_codes() -> set[str]:
    """Codes documented in the 10.1.1 verification error-code table."""
    text = SPEC.read_text()
    start = text.find("Verification Error Codes")
    if start == -1:
        return set()
    window = text[start:start + 4000]
    return set(re.findall(r"^\|\s*`([a-z_]+)`\s*\|", window, re.M))


def check_vectors(findings: Findings) -> None:
    vector_dir = REPO / "tests" / "vectors"
    files = sorted(vector_dir.rglob("*.json")) if vector_dir.exists() else []
    if not files:
        print("  no vectors present yet")
        return

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        findings.fail("VECTORS:dependency", "jsonschema is not installed")
        return

    profile = json.loads((SCHEMA_DIR / "profile.json").read_text())
    usp = json.loads((SCHEMA_DIR / "usp.json").read_text())
    registry = {
        f"{USP_SCHEMA_BASE}profile.json": profile,
        f"{USP_SCHEMA_BASE}usp.json": usp,
    }
    credential_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": f"{USP_SCHEMA_BASE}profile.json#/$defs/BookingScopedCredential",
    }

    def validator_for(schema):
        try:
            from referencing import Registry, Resource
            res = Registry().with_resources(
                (uri, Resource.from_contents(doc)) for uri, doc in registry.items())
            return Draft202012Validator(schema, registry=res)
        except ImportError:
            return None

    documented = spec_error_codes()
    enum = set(resolve_pointer(
        json.loads(OPENRPC.read_text()),
        "/components/errors/USPProtocolError/data/properties/code/enum"))
    spec_text = SPEC.read_text()

    for path in files:
        vector = json.loads(path.read_text())
        vid = vector.get("id", rel(path))

        if vid not in spec_text:
            findings.fail(f"VECTOR:{vid}:uncited",
                          "vector id is not cited anywhere in specification.md, "
                          "so prose and vectors can drift apart unnoticed")

        code = vector.get("reject_code")
        if code:
            if code not in documented:
                findings.fail(f"VECTOR:{vid}:code-undocumented",
                              f"reject_code {code!r} is not in the 10.1.1 error-code table")
            if code not in enum:
                findings.fail(f"VECTOR:{vid}:code-unenumerated",
                              f"reject_code {code!r} is not in the OpenRPC "
                              "USPProtocolError code enum")

        credential = vector.get("credential")
        if credential is not None and vector.get("credential_wellformed", True):
            validator = validator_for(credential_schema)
            if validator is not None:
                errors = sorted(validator.iter_errors(credential), key=lambda e: e.path)
                if errors:
                    findings.fail(f"VECTOR:{vid}:credential",
                                  f"credential fails BookingScopedCredential: "
                                  f"{errors[0].message}")

        # Verify the signature for real where possible. A vector whose proof does
        # not actually verify is worse than no vector: it teaches the wrong bytes.
        proof, keyinfo = vector.get("proof"), vector.get("key")
        if proof and keyinfo and vector.get("expected_claims") is not None:
            try:
                from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            except ImportError:
                print("  cryptography not installed; skipping signature verification")
            else:
                try:
                    h_b64, p_b64, s_b64 = proof.split(".")
                    header = json.loads(unb64u(h_b64))
                    claims = json.loads(unb64u(p_b64))
                except Exception as exc:  # noqa: BLE001
                    findings.fail(f"VECTOR:{vid}:proof", f"proof is not a parseable JWS: {exc}")
                    continue

                if claims != vector["expected_claims"]:
                    findings.fail(f"VECTOR:{vid}:claims",
                                  "published expected_claims do not match the signed payload")

                jwk = header.get("jwk", {})
                jkt = b64u(hashlib.sha256(jcs(jwk)).digest())
                if keyinfo.get("jkt") and jkt != keyinfo["jkt"]:
                    findings.fail(f"VECTOR:{vid}:jkt",
                                  f"RFC 7638 thumbprint of the header jwk is {jkt}, "
                                  f"but the vector publishes {keyinfo['jkt']}")

                if header.get("alg") == "none":
                    if s_b64:
                        findings.fail(f"VECTOR:{vid}:alg-none",
                                      "an alg:none vector must carry an empty signature segment")
                else:
                    pub = Ed25519PublicKey.from_public_bytes(unb64u(jwk["x"]))
                    try:
                        pub.verify(unb64u(s_b64), f"{h_b64}.{p_b64}".encode())
                    except Exception:  # noqa: BLE001
                        findings.fail(f"VECTOR:{vid}:signature",
                                      "the published proof signature does not verify against "
                                      "its own header jwk")

                # The cross-key case must verify against its own key yet still be
                # rejected, which is exactly what distinguishes it from a forgery.
                cnf = (vector.get("credential") or {}).get("cnf", {})
                if cnf and vector.get("expect") == "reject" and \
                        vector.get("reject_code") == "pop_key_mismatch" and jkt == cnf.get("jkt"):
                    findings.fail(f"VECTOR:{vid}:cross-key",
                                  "a pop_key_mismatch vector must use a proof key that differs "
                                  "from the credential's cnf.jkt, or it tests nothing")

        canon = vector.get("canonicalization")
        if canon:
            try:
                produced = jcs(canon["params"])
            except (ValueError, TypeError) as exc:
                findings.fail(f"VECTOR:{vid}:jcs", str(exc))
                continue
            if "jcs" in canon and produced.decode("utf-8") != canon["jcs"]:
                findings.fail(f"VECTOR:{vid}:jcs",
                              f"published JCS bytes do not match: "
                              f"expected {canon['jcs']!r}, computed {produced.decode()!r}")
            digest = b64u(hashlib.sha256(produced).digest())
            if "usp_p" in canon and digest != canon["usp_p"]:
                findings.fail(f"VECTOR:{vid}:usp_p",
                              f"published usp_p does not match: "
                              f"expected {canon['usp_p']}, computed {digest}")


# --------------------------------------------------------------------------
# check: authority publication
# --------------------------------------------------------------------------

def iter_text_sources() -> list[Path]:
    """Tracked-style text sources relevant to identifier migration."""
    suffixes = {".html", ".js", ".json", ".md", ".py", ".sh", ".txt", ".yml", ".yaml"}
    excluded_names = {"CHANGE_LOG.md", "PLAN.md"}
    out = []
    for path in REPO.rglob("*"):
        if not path.is_file() or path.name in excluded_names:
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        if any(part in {".git", "site", "node_modules"} for part in path.parts):
            continue
        if path.suffix in suffixes or path.name in {"CNAME"}:
            out.append(path)
    return sorted(out)


def published_path(uri: str) -> Path:
    """Return the built-site path for a canonical authority URI."""
    path = uri.removeprefix(USP_ORIGIN).split("#", 1)[0].split("?", 1)[0]
    return SITE / path.lstrip("/")


def check_authority(findings: Findings) -> None:
    canonical_fragments = {
        "3-service-catalog",
        "4-availability",
        "5-booking-lifecycle",
        "7-ucp-native-mode",
        "waitlist-extension",
        "856-acp-booking-extension",
    }
    historical = {
        REPO / "site-docs" / "migration.md",
    }
    legacy_path_docs = historical | {
        SPEC,
        REPO / "scripts" / "build-site.sh",
    }
    external_host_docs = historical
    for path in iter_text_sources():
        text = path.read_text(errors="replace")
        stale_text = text
        if path == SPEC:
            stale_text = text.split(
                "## Appendix B. Namespace Authority Migration (Informative)", 1)[0]
        if path not in historical:
            if "https://usp.dev" in stale_text:
                findings.fail(f"STALE:{rel(path)}:origin",
                              "contains the retired https://usp.dev origin")
            if re.search(r"\bdev\.usp\.", stale_text):
                findings.fail(f"STALE:{rel(path)}:namespace",
                              "contains the retired dev.usp.* namespace")
        if path not in external_host_docs and re.search(r"\busp\.live\b", text):
            findings.fail(f"STALE:{rel(path)}:docs-host",
                          "contains the former docs host outside residual notes")
        if path not in legacy_path_docs and re.search(
                r"/services/(?:rest\.openapi|mcp\.openrpc)\.json", text):
            findings.fail(f"STALE:{rel(path)}:binding-path",
                          "contains a former binding path outside migration notes")
        for short in re.findall(
                r"https://usp-protocol\.dev/schemas/"
                r"(?:catalog|availability|booking|waitlist)\.json", text):
            findings.fail(f"LAYOUT:{rel(path)}:{short}",
                          "uses a deleted short schema path")

        for uri in re.findall(r"https://usp-protocol\.dev/(?:problems|spec/\d{4}-\d{2}-\d{2})"
                              r"[^\s\"'`)<]*", text):
            findings.fail(f"LAYOUT:{rel(path)}:{uri}",
                          "uses a non-canonical problem or versioned-spec path")
        for fragment in re.findall(
                r"https://usp-protocol\.dev/specification#([a-z0-9-]+)", text):
            if fragment not in canonical_fragments:
                findings.fail(f"SPECFRAGMENT:{rel(path)}:{fragment}",
                              "profile spec URI uses a non-canonical fragment")
        for slug in re.findall(r"https://usp-protocol\.dev/errors/([a-z0-9_-]+)", text):
            if "_" in slug or slug == "validation":
                findings.fail(f"ERRORSLUG:{rel(path)}:{slug}",
                              "problem type must use its canonical kebab-case slug")

    schema_ids = {}
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        schema_id = json.loads(path.read_text()).get("$id")
        if not isinstance(schema_id, str) or not schema_id.startswith(USP_SCHEMA_BASE):
            findings.fail(f"ORIGIN:{rel(path)}",
                          f"$id must start with {USP_SCHEMA_BASE}")
            continue
        if schema_id in schema_ids:
            findings.fail(f"SCHEMAID:{rel(path)}",
                          f"duplicates $id from {rel(schema_ids[schema_id])}")
        schema_ids[schema_id] = path
        target = published_path(schema_id)
        if not target.is_file():
            findings.fail(f"PUBLISH:{schema_id}",
                          f"built site is missing {rel(target)}")
        else:
            try:
                if json.loads(target.read_text()).get("$id") != schema_id:
                    findings.fail(f"PUBLISH:{schema_id}",
                                  "published schema $id differs from source")
            except json.JSONDecodeError as exc:
                findings.fail(f"PUBLISH:{schema_id}", f"published JSON is invalid: {exc}")

    for path in iter_json_files():
        doc = json.loads(path.read_text())
        for pointer, node in walk(doc):
            if not isinstance(node, dict):
                continue
            for name, entries in node.items():
                if not name.startswith("dev.usp-protocol.") or not isinstance(entries, list):
                    continue
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    for field in ("spec", "schema"):
                        uri = entry.get(field)
                        if uri is not None and (
                                not isinstance(uri, str) or
                                not uri.startswith(USP_ORIGIN + "/")):
                            findings.fail(
                                f"ORIGIN:{rel(path)}:{pointer}/{name}/{field}",
                                f"{field} must use {USP_ORIGIN}")

    binding_targets = {
        OPENAPI: SITE / "schemas" / "openapi" / "usp-rest.json",
        OPENRPC: SITE / "schemas" / "openrpc" / "usp-mcp.json",
    }
    for source, target in binding_targets.items():
        if not target.is_file():
            findings.fail(f"PUBLISH:{rel(source)}", f"missing {rel(target)}")
            continue
        if json.loads(source.read_text()) != json.loads(target.read_text()):
            findings.fail(f"PUBLISH:{rel(source)}", "published binding differs from source")
        for pointer, node in walk(json.loads(source.read_text())):
            if not isinstance(node, dict) or not isinstance(node.get("$ref"), str):
                continue
            ref = node["$ref"]
            if ref.startswith(("https://ucp.dev/", "#")):
                continue
            if not ref.startswith(USP_SCHEMA_BASE):
                findings.fail(f"BINDINGREF:{rel(source)}:{pointer}",
                              "external binding $ref is not a canonical schema URI")

    required_files = [
        SITE / "specification" / "index.html",
        SITE / "services" / "rest.openapi.json",
        SITE / "services" / "mcp.openrpc.json",
        SITE / "spec" / "index.html",
        SITE / "CNAME",
    ]
    for path in required_files:
        if not path.is_file():
            findings.fail(f"PUBLISH:{rel(path)}", "required published path is missing")
    cname = SITE / "CNAME"
    if cname.is_file() and cname.read_text().strip() != "usp-protocol.dev":
        findings.fail("PUBLISH:CNAME", "published CNAME does not bind usp-protocol.dev")

    specification_html = SITE / "specification" / "index.html"
    if specification_html.is_file():
        html = specification_html.read_text()
        for fragment in sorted(canonical_fragments):
            escaped = re.escape(fragment)
            if not re.search(rf'\bid=(?:"{escaped}"|{escaped})(?:\s|>)', html):
                findings.fail(f"SPECFRAGMENT:{fragment}",
                              "built specification page is missing canonical anchor")

    type_uris = set()
    for path in iter_text_sources():
        type_uris.update(re.findall(
            r"https://usp-protocol\.dev/errors/[a-z0-9-]+", path.read_text(errors="replace")))
    for uri in sorted(type_uris):
        slug = uri.rsplit("/", 1)[1]
        if not (SITE / "errors" / slug / "index.html").is_file():
            findings.fail(f"PROBLEM:{uri}", "built site has no canonical problem page")

    for source in sorted((REPO / "playground" / "scenarios").glob("*.json")):
        mirror = REPO / "site-docs" / "playground" / "scenarios" / source.name
        if not mirror.is_file() or source.read_bytes() != mirror.read_bytes():
            findings.fail(f"MIRROR:{rel(source)}", "site-docs scenario mirror differs")
    source_js = REPO / "playground" / "src" / "playground.js"
    mirror_js = REPO / "site-docs" / "playground" / "src" / "playground.js"
    identifier_pattern = re.compile(
        r"(?:https://usp-protocol\.dev/[a-z0-9_./#-]+|dev\.usp-protocol\.[a-z0-9_.-]+)")
    source_identifiers = set(identifier_pattern.findall(source_js.read_text()))
    mirror_identifiers = set(identifier_pattern.findall(mirror_js.read_text()))
    if source_identifiers != mirror_identifiers:
        findings.fail("MIRROR:playground.js",
                      "site-docs runtime advertises different protocol identifiers")

    registry = (REPO / "site-docs" / "namespace.md").read_text()
    for name in sorted(RESERVED_NAMESPACE_NAMES):
        if f"`{name}`" not in registry:
            findings.fail(f"NAMESPACE:{name}", "missing from namespace registry")


CHECKS = {
    "schemas": check_schemas,
    "refs": check_refs,
    "vectors": check_vectors,
    "authority": check_authority,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("check", choices=[*CHECKS, "all"])
    args = parser.parse_args()

    names = list(CHECKS) if args.check == "all" else [args.check]
    status = 0
    for name in names:
        print(f"== {name}")
        findings = Findings()
        CHECKS[name](findings)
        status |= findings.report(name)
    return status


if __name__ == "__main__":
    sys.exit(main())
