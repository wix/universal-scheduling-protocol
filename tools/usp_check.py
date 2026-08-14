#!/usr/bin/env python3
"""Conformance checks for the USP specification repository.

Three subcommands, each useful on its own:

  schemas   Parse every JSON artefact, compile every file under schemas/ as a
            JSON Schema, and assert the protocol version literal agrees across
            the five places that assert this repository's version identity.

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

USP_SCHEMA_BASE = "https://usp.dev/schemas/"


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
    """Map a https://usp.dev/schemas/... URI onto candidate on-disk files.

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
        "https://usp.dev/schemas/profile.json": profile,
        "https://usp.dev/schemas/usp.json": usp,
    }
    credential_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": "https://usp.dev/schemas/profile.json#/$defs/BookingScopedCredential",
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

CHECKS = {"schemas": check_schemas, "refs": check_refs, "vectors": check_vectors}


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
