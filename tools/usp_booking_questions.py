"""Booking-questions checks used by usp_check.py (specification Section 11.4).

JSON Schema validates the shape of a question set. It cannot see the rules that
span items: that a condition names an earlier question, that option values are
unique, that a section groups something. Nor can it compute which questions
apply once answers arrive, or which messages a business owes the platform for a
submission. Those rules live here, once, so wire, eval, flow, and composed
vectors are all recomputed by the same code instead of each asserting its own
reading of the prose.

Nothing in this module fetches a network resource.
"""

from __future__ import annotations

import copy
import itertools
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO / "schemas"
VECTOR_DIR = REPO / "tests" / "vectors"
FIXTURE_DIR = VECTOR_DIR / "fixtures"
EVIDENCE_DIR = REPO / "docs" / "requirement-evidence"
USP_SCHEMA_BASE = "https://usp-protocol.dev/schemas/"

ACTION_TYPE = "dev.usp-protocol.services.booking_questions.buyer_input"

# Codes a business derives mechanically from a definition and a submission. A
# flow step that asserts one of these is recomputed; every other code (token
# decisions, update permission, business policy) is asserted, not derived.
DERIVED_CODES = {
    "booking_question_answer_missing",
    "booking_question_answer_invalid",
    "booking_question_unknown",
    "booking_questions_changed",
    "booking_question_answer_ignored",
}
INFO_CODES = {"booking_question_answer_ignored"}
EXTENSION_CODES = DERIVED_CODES | {
    "booking_question_update_not_allowed",
    "booking_eligibility_required",
    "booking_eligibility_expired",
}

QUESTION_PATH_RE = re.compile(
    r"^\$(?:\.booking)?\.booking_question_submissions\[\?@\.set_id=='[A-Za-z0-9_.-]+'\]"
    r"(?:\.answers\['[A-Za-z0-9_.-]+'\])?$")
BUYER_PATH_RE = re.compile(r"^\$(?:\.booking)?\.buyer\.(?:first_name|last_name|email|phone_number)$")

EMAIL_RE = re.compile(r"^[^\s@<>()\[\]\",;:]+@[^\s@<>()\[\]\",;:]+\.[^\s@<>()\[\]\",;:]+$")
URI_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:[^\s]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$")
DATE_TIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d+)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)$")
PHONE_RE = re.compile(r"^\+[1-9]\d{1,14}$")
DURATION_BOUND_RE = re.compile(r"^(-?)P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?$")
VALIDITY_RE = re.compile(
    r"^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$")

ORDERED_OPS = {"gt", "gte", "lt", "lte"}
MAX_USE_DEPTH = 8
DEFAULT_MAX_CASES = 64

ALLOWED_SOURCE_TYPES = {
    "provider_documentation",
    "standard",
    "regulation",
    "accessibility_guidance",
    "interoperability_specification",
    "operational_evidence",
}
EVIDENCE_STATUSES = {"current", "changed", "unavailable", "historical"}


# --------------------------------------------------------------------------
# schema validation
# --------------------------------------------------------------------------

_VALIDATORS: dict[str, object] = {}


def validator(target: str):
    """Validator for ``file.json#/$defs/Name`` under schemas/, cached."""
    if target in _VALIDATORS:
        return _VALIDATORS[target]
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource

    docs = [json.loads(p.read_text()) for p in sorted(SCHEMA_DIR.glob("*.json"))]
    reg = Registry().with_resources(
        (doc["$id"], Resource.from_contents(doc)) for doc in docs if "$id" in doc)
    file_name, _, fragment = target.partition("#")
    base = next((d["$id"] for d in docs if d.get("$id", "").endswith(f"/{file_name}")), None)
    if not base or not fragment:
        raise ValueError(f"{target!r} does not name a schemas/ $def")
    _VALIDATORS[target] = Draft202012Validator(
        {"$schema": "https://json-schema.org/draft/2020-12/schema",
         "$ref": f"{base}#{fragment}"},
        registry=reg)
    return _VALIDATORS[target]


def schema_problems(target: str, instance) -> list[str]:
    errors = sorted(validator(target).iter_errors(instance), key=lambda e: list(e.path))
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]


# --------------------------------------------------------------------------
# definitions
# --------------------------------------------------------------------------

def answer_kind(schema: dict) -> str:
    """Coarse answer type of a question's answer schema."""
    if schema.get("type") == "array":
        return "multiple_choice"
    if schema.get("type") == "string" and "oneOf" in schema:
        return "single_choice"
    if schema.get("type") in ("integer", "number"):
        return "number"
    if schema.get("type") == "boolean":
        return "boolean"
    return {"date": "date", "time": "time", "date-time": "date_time"}.get(
        schema.get("format"), "string")


def options_of(schema: dict) -> list[dict]:
    if answer_kind(schema) == "multiple_choice":
        return schema.get("items", {}).get("anyOf", [])
    return schema.get("oneOf", []) if answer_kind(schema) == "single_choice" else []


def condition_leaves(condition):
    if not isinstance(condition, dict):
        return
    if "question" in condition:
        yield condition
    for key in ("all", "any"):
        for member in condition.get(key, []):
            yield from condition_leaves(member)
    if "not" in condition:
        yield from condition_leaves(condition["not"])


def semantic_set_errors(qset: dict) -> list[str]:
    """Cross-item rules JSON Schema cannot express, as ``rule:item_id`` strings."""
    errors: list[str] = []
    items = qset.get("items", [])
    seen_ids: set[str] = set()
    questions: dict[str, dict] = {}
    index_of: dict[str, int] = {}
    for i, item in enumerate(items):
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            index_of.setdefault(item["id"], i)

    notes = 0
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        iid = item.get("id")
        if iid in seen_ids:
            errors.append(f"duplicate_item_id:{iid}")
        seen_ids.add(iid)
        kind = item.get("kind")
        if kind == "section":
            following = items[i + 1] if i + 1 < len(items) else None
            if following is None or following.get("kind") == "section":
                errors.append(f"empty_section:{iid}")
        if kind == "question":
            schema = item.get("schema", {})
            consts = [o.get("const") for o in options_of(schema)]
            if len(consts) != len(set(consts)):
                errors.append(f"duplicate_option_const:{iid}")
            if item.get("maps_to") == "notes":
                notes += 1
                if notes == 2:
                    errors.append(f"multiple_maps_to_notes:{iid}")

        conditions = [item.get("when")]
        if isinstance(item.get("required"), dict):
            conditions.append(item["required"])
        for condition in conditions:
            for leaf in condition_leaves(condition):
                ref = leaf.get("question")
                if ref == iid:
                    errors.append(f"self_reference:{iid}")
                elif ref not in index_of:
                    errors.append(f"unknown_reference:{iid}")
                elif index_of[ref] > i:
                    errors.append(f"forward_reference:{iid}")
                elif ref not in questions:
                    errors.append(f"reference_not_question:{iid}")
                else:
                    kind_of_ref = answer_kind(questions[ref].get("schema", {}))
                    op = leaf.get("op")
                    if op == "contains" and kind_of_ref != "multiple_choice":
                        errors.append(f"operator_type_mismatch:{iid}")
                    if op in ORDERED_OPS and kind_of_ref not in (
                            "number", "date", "time", "date_time"):
                        errors.append(f"operator_type_mismatch:{iid}")
        if kind == "question":
            questions[iid] = item
    return errors


def semantic_errors_for(target: str, instance) -> list[str]:
    """Semantic errors for any instance that is or carries question sets."""
    name = target.rpartition("/")[2]
    if not isinstance(instance, (dict, list)):
        return []
    if name == "BookingQuestionSet":
        return semantic_set_errors(instance)
    sets = []
    if name == "BookingQuestionSets" and isinstance(instance, list):
        sets = instance
    elif isinstance(instance, dict) and isinstance(instance.get("booking_question_sets"), list):
        sets = instance["booking_question_sets"]
    elif name == "BookingQuestion" and isinstance(instance, dict):
        # A lone question has no siblings, so only its own option rule applies.
        return [e for e in semantic_set_errors({"items": [instance]})
                if e.startswith("duplicate_option_const:")]
    errors = []
    for qset in sets:
        if isinstance(qset, dict):
            errors.extend(semantic_set_errors(qset))
    return errors


# --------------------------------------------------------------------------
# answers
# --------------------------------------------------------------------------

def _shift(day: date, sign: int, years: int, months: int, days: int) -> date:
    total = day.year * 12 + day.month - 1 + sign * (years * 12 + months)
    year, month = divmod(total, 12)
    month += 1
    last = (date(year + (month == 12), month % 12 + 1, 1) - timedelta(days=1)).day
    return date(year, month, min(day.day, last)) + timedelta(days=sign * days)


def resolve_date_bound(bound: str, request_date: date) -> date:
    if DATE_RE.match(bound):
        return date.fromisoformat(bound)
    match = DURATION_BOUND_RE.match(bound)
    if not match:
        raise ValueError(f"not a date bound: {bound!r}")
    sign = -1 if match.group(1) else 1
    years, months, weeks, days = (int(g or 0) for g in match.groups()[1:])
    return _shift(request_date, sign, years, months, weeks * 7 + days)


def _parse_instant(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def _valid_date(text: str) -> bool:
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return bool(DATE_RE.match(text))


def answer_errors(question: dict, value, request_date: date | None = None) -> list[str]:
    """Reasons a present answer fails its question, as short slugs."""
    schema = question.get("schema", {})
    kind = answer_kind(schema)
    if kind == "multiple_choice":
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            return ["type"]
        errors = []
        options = {o["const"]: o for o in options_of(schema)}
        if any(v not in options for v in value):
            errors.append("option")
        if len(value) != len(set(value)):
            errors.append("unique")
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append("min_items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append("max_items")
        if len(value) > 1 and any(options.get(v, {}).get("exclusive") for v in value):
            errors.append("exclusive")
        return errors
    if kind == "single_choice":
        if not isinstance(value, str):
            return ["type"]
        return [] if value in {o["const"] for o in options_of(schema)} else ["option"]
    if kind == "boolean":
        if not isinstance(value, bool):
            return ["type"]
        return ["const"] if schema.get("const") is True and value is not True else []
    if kind == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return ["type"]
        if schema.get("type") == "integer" and not float(value).is_integer():
            return ["type"]
        errors = []
        if "minimum" in schema and value < schema["minimum"]:
            errors.append("minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append("maximum")
        return errors

    if not isinstance(value, str):
        return ["type"]
    errors = []
    if "minLength" in schema and len(value) < schema["minLength"]:
        errors.append("min_length")
    if "maxLength" in schema and len(value) > schema["maxLength"]:
        errors.append("max_length")
    fmt = schema.get("format")
    if fmt == "email" and not EMAIL_RE.match(value):
        errors.append("format")
    elif fmt == "uri" and not URI_RE.match(value):
        errors.append("format")
    elif fmt == "time" and not TIME_RE.match(value):
        errors.append("format")
    elif fmt == "phone":
        if not PHONE_RE.match(value):
            errors.append("format")
        elif schema.get("allowed_country_codes") and not any(
                value[1:].startswith(code) for code in schema["allowed_country_codes"]):
            errors.append("country_code")
    elif fmt in ("date", "date-time"):
        if fmt == "date" and not _valid_date(value):
            errors.append("format")
        elif fmt == "date-time" and not DATE_TIME_RE.match(value):
            errors.append("format")
        elif request_date is not None:
            day = date.fromisoformat(value[:10])
            if "not_before" in schema and day < resolve_date_bound(schema["not_before"], request_date):
                errors.append("not_before")
            if "not_after" in schema and day > resolve_date_bound(schema["not_after"], request_date):
                errors.append("not_after")
    return errors


# --------------------------------------------------------------------------
# localization (Section 3.5 fallback, Section 11.4.3 `localized`)
# --------------------------------------------------------------------------

def _plain(value):
    """Localizable text is a Description object; an option `title` is a string."""
    if isinstance(value, dict):
        return value.get("plain")
    return value


def _localized_member(node: dict, member: str, language: str):
    """Resolve one text member, falling back to the default when no override."""
    override = (node.get("localized") or {}).get(language) or {}
    if member in override:
        return _plain(override[member])
    return _plain(node.get(member))


def resolve_localized(qset: dict, language: str) -> dict[str, str]:
    """Flatten every buyer-facing text member of a set, resolved for `language`.

    Keys are stable dotted paths so a vector can pin the resolved text without
    restating the whole set. A missing locale or a missing member falls back to
    the default text, so asking for a language the set never declares yields the
    default strings unchanged.
    """
    resolved: dict[str, str] = {}
    for member in ("title", "description"):
        if member in qset:
            resolved[f"set.{member}"] = _localized_member(qset, member, language)
    for item in qset.get("items", []):
        iid = item.get("id")
        kind = item.get("kind")
        members = {
            "section": ("title", "description"),
            "notice": ("content",),
            "question": ("label", "description", "placeholder"),
            "external_task": ("label",),
        }.get(kind, ())
        for member in members:
            if member in item:
                resolved[f"items.{iid}.{member}"] = _localized_member(item, member, language)
        for option in options_of(item.get("schema", {}) or {}):
            const = option.get("const")
            resolved[f"items.{iid}.options.{const}.title"] = _localized_member(
                option, "title", language)
    return resolved


# --------------------------------------------------------------------------
# conditions
# --------------------------------------------------------------------------

def _ordered(kind: str, value):
    if kind == "date_time":
        return _parse_instant(value)
    if kind == "time":
        return value if len(value) == 8 else f"{value}:00"
    return value


def eval_condition(condition: dict, effective: dict, questions: dict) -> bool:
    if "all" in condition:
        return all(eval_condition(c, effective, questions) for c in condition["all"])
    if "any" in condition:
        return any(eval_condition(c, effective, questions) for c in condition["any"])
    if "not" in condition:
        return not eval_condition(condition["not"], effective, questions)
    ref, op = condition["question"], condition["op"]
    present = ref in effective
    if op == "answered":
        return present
    if not present:
        return False
    value, operand = effective[ref], condition.get("value")
    kind = answer_kind(questions[ref].get("schema", {}))
    try:
        if op == "equals":
            if kind == "date_time":
                return _parse_instant(value) == _parse_instant(operand)
            return value == operand
        if op == "in":
            return value in operand
        if op == "contains":
            return isinstance(value, list) and operand in value
        left, right = _ordered(kind, value), _ordered(kind, operand)
        return {"gt": left > right, "gte": left >= right,
                "lt": left < right, "lte": left <= right}[op]
    except (TypeError, ValueError):
        return False


def evaluate_set(qset: dict, answers: dict) -> dict:
    """Applicability of every item for one set of answers.

    Single pass in item order: conditions name only earlier questions, so an
    answer counts toward later conditions exactly when its own question applies.
    """
    questions: dict[str, dict] = {}
    effective: dict = {}
    applicable, required_unanswered, pruned = [], [], []
    section_on = True
    for item in qset.get("items", []):
        kind, iid = item.get("kind"), item.get("id")
        when = item.get("when")
        if kind == "section":
            section_on = when is None or eval_condition(when, effective, questions)
            if section_on:
                applicable.append(iid)
            continue
        on = section_on and (when is None or eval_condition(when, effective, questions))
        if kind == "question":
            questions[iid] = item
        if not on:
            if kind == "question" and iid in answers:
                pruned.append(iid)
            continue
        applicable.append(iid)
        if kind != "question":
            continue
        required = item.get("required")
        if isinstance(required, dict):
            required = eval_condition(required, effective, questions)
        if iid in answers:
            effective[iid] = answers[iid]
        elif required:
            required_unanswered.append(iid)
    known = {i.get("id") for i in qset.get("items", []) if i.get("kind") == "question"}
    return {
        "applicable": applicable,
        "required_unanswered": required_unanswered,
        "pruned": pruned,
        "unknown": [k for k in answers if k not in known],
    }


# --------------------------------------------------------------------------
# reference business validation
# --------------------------------------------------------------------------

PHASE_OF_STEP = {
    "check_eligibility": "preflight",
    "create_booking": "before_confirmation",
    "create_checkout": "before_confirmation",
    "update_booking": None,
    "update_checkout": None,
}


def _iso_duration(text: str) -> timedelta:
    match = VALIDITY_RE.match(text)
    y, mo, w, d, h, mi, s = (int(g or 0) for g in match.groups())
    return timedelta(days=y * 365 + mo * 30 + w * 7 + d, hours=h, minutes=mi, seconds=s)


def _set_path(prefix: str, set_id: str) -> str:
    return f"{prefix}[?@.set_id=='{set_id}']"


def _question_path(prefix: str, set_id: str, qid: str) -> str:
    return f"{_set_path(prefix, set_id)}.answers['{qid}']"


def derive_messages(service: dict, step: dict, history: list[dict] | None = None) -> list[tuple[str, str]]:
    """``(code, path)`` pairs a conforming business returns for one request.

    Failure order is fixed by Section 11.4.9: required buyer fields first in
    declaration order, then question sets in set order and item order. A
    create (or eligibility check) also reports required answers of the phase's
    sets that were never submitted; an update validates only what it carries.
    """
    name = step.get("step")
    phase = PHASE_OF_STEP.get(name)
    creating = name in ("create_booking", "create_checkout", "check_eligibility")
    with_ = step.get("with", {})
    prefix = "$.booking_question_submissions"
    at = step.get("at", "")
    request_date = date.fromisoformat(at[:10]) if DATE_RE.match(at[:10]) else None
    out: list[tuple[str, str]] = []

    if name in ("create_booking", "create_checkout"):
        buyer = with_.get("buyer") or {}
        for member in service.get("required_buyer_fields", []):
            if not buyer.get(member):
                out.append(("booking_question_answer_missing", f"$.buyer.{member}"))

    submissions = {s.get("set_id"): s for s in with_.get("booking_question_submissions", [])
                   if isinstance(s, dict)}
    prior = {h.get("set_id"): h for h in (history or [])}
    for qset in service.get("booking_question_sets", []):
        sid = qset["id"]
        sub = submissions.get(sid)
        in_phase = creating and qset.get("completion_timing") == phase
        required_set = qset.get("completion_requirement", "required") == "required"
        if sub is not None and sub.get("revision") != qset.get("revision"):
            out.append(("booking_questions_changed", _set_path(prefix, sid)))
            continue
        if sub is None:
            if not (in_phase and required_set):
                continue
            done = prior.get(sid)
            if done and qset.get("frequency") != "every_booking":
                if done.get("revision") != qset.get("revision"):
                    out.append(("booking_questions_changed", _set_path(prefix, sid)))
                    continue
                validity = qset.get("validity")
                if validity is None or (
                        at and _parse_instant(done["completed_at"]) + _iso_duration(validity)
                        > _parse_instant(at)):
                    continue
            answers = {}
        else:
            answers = dict(sub.get("answers", {}))

        acting = sub is not None and "action_id" in sub
        by_id = {i.get("id"): i for i in qset.get("items", [])}
        for qid in list(answers):
            item = by_id.get(qid)
            if (item and item.get("kind") == "question"
                    and item.get("collection") == "platform_surface" and not acting):
                del answers[qid]
        result = evaluate_set(qset, answers)
        missing = set(result["required_unanswered"]) if (in_phase and required_set) else set()
        for item in qset.get("items", []):
            qid = item.get("id")
            if item.get("kind") != "question" or qid not in result["applicable"]:
                continue
            if qid in answers:
                if answer_errors(item, answers[qid], request_date):
                    out.append(("booking_question_answer_invalid", _question_path(prefix, sid, qid)))
            elif qid in missing and item.get("collection", "in_band") == "in_band":
                out.append(("booking_question_answer_missing", _question_path(prefix, sid, qid)))
        for qid in result["unknown"]:
            out.append(("booking_question_unknown", _question_path(prefix, sid, qid)))
        for qid in result["pruned"]:
            out.append(("booking_question_answer_ignored", _question_path(prefix, sid, qid)))
    return out


# --------------------------------------------------------------------------
# flow checks
# --------------------------------------------------------------------------

FLOW_SCHEMA_KEYS = {
    "booking_question_sets": "booking_questions.json#/$defs/BookingQuestionSets",
    "required_buyer_fields": "booking_questions.json#/$defs/RequiredBuyerFields",
    "booking_question_submissions": "booking_questions.json#/$defs/BookingQuestionSubmissions",
    "booking_question_state": "booking_questions.json#/$defs/BookingQuestionStates",
    "booking_question_assessment_token": "booking_questions.json#/$defs/BookingQuestionAssessmentToken",
    "eligibility": "booking_questions.json#/$defs/BookingEligibilityCheckResult",
    "booking_questions": "booking_questions.json#/$defs/BookingQuestionsSummary",
}


def _walk_members(node, pointer=""):
    if isinstance(node, dict):
        if node.get("schema_checked") is False:
            return
        for key, value in node.items():
            here = f"{pointer}/{key}"
            yield key, value, here
            yield from _walk_members(value, here)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _walk_members(value, f"{pointer}/{i}")


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)


def _steps(case: dict) -> list[dict]:
    when = case.get("when")
    if isinstance(when, dict):
        when = when.get("steps", [])
    return [s for s in (when or []) if isinstance(s, dict)]


def _service(case: dict) -> dict:
    service = case.get("given", {}).get("service")
    return service if isinstance(service, dict) else {}


def evidence_capability_ids() -> set[str]:
    ids = set()
    for path in sorted(EVIDENCE_DIR.glob("*.json")) if EVIDENCE_DIR.exists() else []:
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        ids.update(c.get("capability_id") for c in doc.get("capabilities", []))
    return ids


def flow_case_problems(case: dict, outcome_codes: set[str]) -> list[tuple[str, str]]:
    """``(key, message)`` problems for one flow case (plain or expanded)."""
    problems: list[tuple[str, str]] = []
    evidence = case.get("evidence")
    if evidence is not None and evidence not in evidence_capability_ids():
        problems.append(("evidence", f"evidence {evidence!r} is not a capability_id in "
                         "docs/requirement-evidence/"))
    scan = {k: case.get(k) for k in ("given", "when", "then")}

    for key, value, pointer in _walk_members(scan):
        target = FLOW_SCHEMA_KEYS.get(key)
        if target is None or (key == "eligibility" and not (
                isinstance(value, dict) and "decision" in value)):
            continue
        for problem in schema_problems(target, value)[:1]:
            problems.append(("schema", f"{pointer} fails {target.rpartition('/')[2]}: {problem}"))
        if key == "booking_question_sets":
            for error in semantic_errors_for(target, value):
                problems.append(("semantic", f"{pointer}: {error}"))
    for key, value, pointer in _walk_members(scan):
        if key == ACTION_TYPE and isinstance(value, list):
            for i, action in enumerate(value):
                for problem in schema_problems(
                        "booking_questions.json#/$defs/BuyerInputAction", action)[:1]:
                    problems.append(("schema", f"{pointer}/{i} fails BuyerInputAction: {problem}"))
        if key != "actions" or not isinstance(value, list):
            continue
        for i, action in enumerate(value):
            if isinstance(action, dict) and action.get("type") == ACTION_TYPE:
                for problem in schema_problems("booking.json#/$defs/Action", action)[:1]:
                    problems.append(("schema", f"{pointer}/{i} fails Action: {problem}"))
                for problem in schema_problems(
                        "booking_questions.json#/$defs/BuyerInputActionConfig",
                        action.get("config"))[:1]:
                    problems.append(("schema", f"{pointer}/{i}/config: {problem}"))

    for key, value, pointer in _walk_members({"when": case.get("when"), "then": case.get("then")}):
        if key != "messages" or not isinstance(value, list):
            continue
        for i, message in enumerate(value):
            if not isinstance(message, dict) or "code" not in message:
                continue
            code, path = message["code"], message.get("path")
            shape = {k: v for k, v in message.items() if k != "policy"}
            for problem in schema_problems("booking.json#/$defs/Message", shape)[:1]:
                problems.append(("schema", f"{pointer}/{i} fails Message: {problem}"))
            # Informational and warning messages may carry business-authored codes
            # (eligibility reasons, alternatives); errors are always documented outcomes.
            if code not in outcome_codes and (
                    message.get("type") == "error" or code.startswith("booking_")):
                problems.append(("message-code", f"{pointer}/{i}: {code!r} is not a documented "
                                 "business outcome or informational code"))
            expected_type = "info" if code in INFO_CODES else "error"
            if (code in outcome_codes or code in EXTENSION_CODES) and \
                    message.get("type", expected_type) != expected_type:
                problems.append(("message-type", f"{pointer}/{i}: {code} is carried as "
                                 f"type {expected_type!r}"))
            if code.startswith("booking_question") and path is not None and not (
                    QUESTION_PATH_RE.match(path) or BUYER_PATH_RE.match(path)):
                problems.append(("message-path", f"{pointer}/{i}: path {path!r} is not a "
                                 "bracket-form RFC 9535 set or question path"))

    service = _service(case)
    sensitive = set()
    for qset in service.get("booking_question_sets", []):
        for item in qset.get("items", []):
            if item.get("kind") == "question" and item.get("sensitive"):
                sensitive.add(item["id"])
    secrets = set()
    for step in _steps(case):
        for sub in step.get("with", {}).get("booking_question_submissions", []) or []:
            for qid, value in (sub.get("answers") or {}).items():
                if qid in sensitive:
                    secrets.update(s for s in _strings(value) if len(s) >= 3)
    outputs = [case.get("then")] + [s.get("result") for s in _steps(case)]
    rendered = json.dumps(outputs, ensure_ascii=False)
    for secret in sorted(secrets):
        if secret in rendered:
            problems.append(("sensitive-leak", f"sensitive answer {secret!r} appears in a "
                             "result, echo, or message"))

    if case.get("given", {}).get("extension_negotiated") is False:
        for key, value, pointer in _walk_members({"when": case.get("when"), "then": case.get("then")}):
            if key == "code" and value in EXTENSION_CODES:
                problems.append(("unnegotiated-code", f"{pointer}: {value} emitted to a platform "
                                 "that did not negotiate the extension"))
        return problems

    if service.get("booking_question_sets") or service.get("required_buyer_fields"):
        history = case.get("given", {}).get("buyer_history", {}).get("completed_sets")
        for i, step in enumerate(_steps(case)):
            if step.get("step") not in PHASE_OF_STEP or "result" not in step or \
                    step.get("derive") is False:
                continue
            if "booking_question_submissions" not in step.get("with", {}) and \
                    step.get("step") not in ("create_booking", "check_eligibility"):
                continue
            derived = derive_messages(service, step, history)
            asserted = [(m.get("code"), m.get("path"))
                        for m in (step["result"].get("messages") or [])
                        if isinstance(m, dict) and m.get("code") in DERIVED_CODES
                        and not m.get("policy")]
            if derived != asserted:
                problems.append(("derived-messages",
                                 f"step {i} ({step.get('step')}): vector asserts {asserted}, "
                                 f"reference business validation derives {derived}"))
    return problems


# --------------------------------------------------------------------------
# fixtures and composition
# --------------------------------------------------------------------------

class ComposeError(Exception):
    pass


def load_fixtures() -> dict[str, dict]:
    fixtures = {}
    for path in sorted(FIXTURE_DIR.glob("*.json")) if FIXTURE_DIR.exists() else []:
        doc = json.loads(path.read_text())
        fixtures[doc.get("id", path.stem)] = doc
    return fixtures


def load_vectors_by_id() -> dict[str, dict]:
    out = {}
    for path in sorted(VECTOR_DIR.rglob("*.json")):
        if FIXTURE_DIR in path.parents:
            continue
        doc = json.loads(path.read_text())
        out[doc.get("id", path.stem)] = doc
    return out


_OMIT = object()


def _pointer_get(doc, pointer: str):
    node = doc
    for token in [t.replace("~1", "/").replace("~0", "~") for t in pointer.split("/")[1:]]:
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node


def apply_json_patch(doc, operations: list[dict]):
    """RFC 6902 subset: add, remove, replace, test, copy, move."""
    doc = copy.deepcopy(doc)
    for op in operations:
        kind, path = op.get("op"), op.get("path", "")
        tokens = [t.replace("~1", "/").replace("~0", "~") for t in path.split("/")[1:]]
        if kind == "test":
            if _pointer_get(doc, path) != op.get("value"):
                raise ComposeError(f"JSON Patch test failed at {path}")
            continue
        if kind in ("copy", "move"):
            value = copy.deepcopy(_pointer_get(doc, op["from"]))
            if kind == "move":
                doc = apply_json_patch(doc, [{"op": "remove", "path": op["from"]}])
            doc = apply_json_patch(doc, [{"op": "add", "path": path, "value": value}])
            continue
        if not tokens:
            if kind in ("add", "replace"):
                doc = copy.deepcopy(op["value"])
                continue
            raise ComposeError("cannot remove the document root")
        parent = _pointer_get(doc, "/" + "/".join(
            t.replace("~", "~0").replace("/", "~1") for t in tokens[:-1])) if tokens[:-1] else doc
        last = tokens[-1]
        try:
            if isinstance(parent, list):
                if kind == "add":
                    parent.insert(len(parent) if last == "-" else int(last), copy.deepcopy(op["value"]))
                elif kind == "remove":
                    del parent[int(last)]
                elif kind == "replace":
                    parent[int(last)] = copy.deepcopy(op["value"])
                else:
                    raise ComposeError(f"unsupported JSON Patch op {kind!r}")
            else:
                if kind == "add":
                    parent[last] = copy.deepcopy(op["value"])
                elif kind in ("remove", "replace"):
                    if last not in parent:
                        raise ComposeError(f"JSON Patch {kind} target {path} does not exist")
                    if kind == "remove":
                        del parent[last]
                    else:
                        parent[last] = copy.deepcopy(op["value"])
                else:
                    raise ComposeError(f"unsupported JSON Patch op {kind!r}")
        except (IndexError, KeyError, ValueError) as exc:
            raise ComposeError(f"JSON Patch {kind} at {path} failed: {exc}") from exc
    return doc


def apply_merge_patch(target, patch):
    """RFC 7396 JSON Merge Patch."""
    if not isinstance(patch, dict):
        return copy.deepcopy(patch)
    result = copy.deepcopy(target) if isinstance(target, dict) else {}
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        else:
            result[key] = apply_merge_patch(result.get(key), value)
    return result


def apply_edits(doc, edits: list[dict]):
    for edit in edits or []:
        if "merge" in edit:
            doc = apply_merge_patch(doc, edit["merge"])
        else:
            doc = apply_json_patch(doc, [edit])
    return doc


def resolve(node, fixtures: dict, vectors: dict, params: dict | None = None,
            stack: tuple = (), validated: list | None = None):
    """Inline ``$use`` references and substitute ``$param`` values."""
    if len(stack) > MAX_USE_DEPTH:
        raise ComposeError(f"$use nesting deeper than {MAX_USE_DEPTH}: {' > '.join(stack)}")
    if isinstance(node, list):
        out = []
        for item in node:
            value = resolve(item, fixtures, vectors, params, stack, validated)
            if value is not _OMIT:
                out.append(value)
        return out
    if not isinstance(node, dict):
        return node
    if set(node) == {"$param"}:
        name = node["$param"]
        if params is None or name not in params:
            raise ComposeError(f"$param {name!r} used outside a fixture that declares it")
        return params[name]
    if "$use" in node:
        ref = node["$use"]
        bound = {k: resolve(v, fixtures, vectors, params, stack, validated)
                 for k, v in (node.get("with") or {}).items()}
        extra = {k: v for k, v in node.items() if k not in ("$use", "with")}
        if ref in stack:
            raise ComposeError(f"$use cycle: {' > '.join(stack + (ref,))}")
        if ref.startswith("vector:"):
            vid, _, pointer = ref[len("vector:"):].partition("#")
            if vid not in vectors:
                raise ComposeError(f"unresolved $use {ref!r}")
            try:
                body = copy.deepcopy(_pointer_get(vectors[vid], pointer))
            except (KeyError, IndexError, ValueError) as exc:
                raise ComposeError(f"unresolved $use {ref!r}: {exc}") from exc
            value = resolve(body, fixtures, vectors, None, stack + (ref,), validated)
        else:
            fixture = fixtures.get(ref)
            if fixture is None:
                raise ComposeError(f"unresolved $use {ref!r}")
            declared = fixture.get("parameters", {})
            for name in bound:
                if name not in declared:
                    raise ComposeError(f"$use {ref!r} binds unknown parameter {name!r}")
            values = {}
            for name, spec in declared.items():
                if name in bound:
                    values[name] = bound[name]
                elif spec.get("required"):
                    raise ComposeError(f"$use {ref!r} is missing required parameter {name!r}")
                elif spec.get("optional"):
                    values[name] = _OMIT
                else:
                    values[name] = copy.deepcopy(spec.get("default"))
            value = resolve(copy.deepcopy(fixture["body"]), fixtures, vectors, values,
                            stack + (ref,), validated)
            if fixture.get("schema") and validated is not None:
                validated.append((ref, fixture["schema"], value))
        if extra:
            if not isinstance(value, dict):
                raise ComposeError(f"$use {ref!r} with sibling members must inline an object")
            value = {**value, **resolve(extra, fixtures, vectors, params, stack, validated)}
        return value
    out = {}
    for key, value in node.items():
        resolved = resolve(value, fixtures, vectors, params, stack, validated)
        if resolved is not _OMIT:
            out[key] = resolved
    return out


def fixture_problems(fixture: dict, fixtures: dict, vectors: dict) -> list[str]:
    problems = []
    if fixture.get("kind") != "fixture":
        problems.append("kind must be fixture")
    declared = fixture.get("parameters", {})
    if any(spec.get("required") for spec in declared.values()):
        return problems
    validated: list = []
    try:
        resolve({"$use": fixture["id"]}, fixtures, vectors, None, (), validated)
    except ComposeError as exc:
        return problems + [str(exc)]
    for ref, target, value in validated:
        for problem in schema_problems(target, value)[:1]:
            problems.append(f"default expansion of {ref} fails {target}: {problem}")
    return problems


def _assignment_key(assignment: list[tuple[str, str]]) -> str:
    return ",".join(f"{f}={lvl}" for f, lvl in assignment)


def _derive(compose: dict, steps: list[dict], assignment: list[tuple[str, str]]) -> dict:
    """Stage results under the evaluation rule fixed by the compose format."""
    factors = compose["factors"]
    present = {s.get("stage") for s in steps}
    stages = [s for s in compose["stages"] if s["name"] in present]
    derived: dict = {"rejected": False, "messages": [], "unreached": []}
    extra_then: dict = {}
    for index, stage in enumerate(stages):
        rejects, results = [], []
        for factor, level in assignment:
            for effect in factors[factor][level].get("effects", []):
                if effect.get("stage") != stage["name"]:
                    continue
                if "reject" in effect:
                    rejects.append(effect["reject"])
                if "result" in effect:
                    results.append(effect["result"])
                extra_then.update(effect.get("then", {}))
        derived["final_stage"] = stage["name"]
        if rejects:
            derived["rejected"] = True
            derived["rejections"] = rejects
            derived["messages"] = [r["path"] for r in rejects]
            derived["unreached"] = [s["name"] for s in stages[index + 1:]]
            derived.pop("final_status", None)
            break
        if len({json.dumps(r, sort_keys=True) for r in results}) > 1:
            raise ComposeError(f"conflicting results for stage {stage['name']!r}")
        result = results[-1] if results else stage.get("default", {})
        for key, value in result.items():
            derived["final_status" if key == "status" else key] = value
    derived.update(extra_then)
    create_rejected = derived["rejected"] and derived.get("final_stage") == stages[0]["name"]
    derived.setdefault("booking_created", not create_rejected)
    derived.setdefault("hold_changed", False if create_rejected else None)
    derived.setdefault("payment_authorized", False)
    if derived["hold_changed"] is None:
        del derived["hold_changed"]
    return derived


def _invariant_problems(name: str, case: dict, derived: dict) -> str | None:
    steps = _steps(case)
    create_rejected = derived["rejected"] and derived.get("final_stage") == (
        steps[0].get("stage") if steps else None)
    if name == "no_booking_resource_when_create_rejected":
        if create_rejected and derived.get("booking_created") is not False:
            return "a rejected create still reports a booking resource"
    elif name == "hold_expires_at_and_capacity_unchanged_when_create_rejected":
        if create_rejected and derived.get("hold_changed") is not False:
            return "a rejected create changes the hold"
    elif name == "no_payment_authorized_or_captured_before_confirmed":
        if derived.get("payment_authorized") and derived.get("final_status") != "confirmed":
            return "payment is authorized before the booking is confirmed"
    elif name == "bare_acknowledgement_never_resolves_action":
        service = _service(case)
        surface = {i["id"] for s in service.get("booking_question_sets", [])
                   for i in s.get("items", [])
                   if i.get("kind") == "question" and i.get("collection") == "platform_surface"}
        bare, acted = set(), set()
        for step in steps:
            for sub in step.get("with", {}).get("booking_question_submissions", []) or []:
                hit = surface & set(sub.get("answers", {}))
                (acted if "action_id" in sub else bare).update(hit)
        if (bare - acted) and (derived.get("final_status") == "confirmed"
                               or derived.get("acceptance_recorded") is True):
            return "a bare acknowledgement without an Action id resolved the Action"
    elif name == "messages_never_echo_answer_values":
        values = set()
        for step in steps:
            for sub in step.get("with", {}).get("booking_question_submissions", []) or []:
                values.update(s for s in _strings(sub.get("answers", {})) if len(s) >= 3)
        rendered = json.dumps(derived.get("rejections", []), ensure_ascii=False)
        if any(v in rendered for v in values):
            return "a message echoes a submitted answer value"
    else:
        return f"unknown invariant {name!r}"
    return None


def expand_compose(vector: dict, fixtures: dict, vectors: dict) -> tuple[list[dict], list[str]]:
    """Expanded flow cases and composition problems for one ``compose`` vector."""
    compose = vector.get("compose", {})
    problems: list[str] = []
    factors = compose.get("factors", {})
    names = list(factors)
    excluded = {e["case"] for e in compose.get("exclude", [])}
    for e in compose.get("exclude", []):
        if not e.get("reason"):
            problems.append(f"exclusion {e.get('case')!r} has no written reason")
    combos = [list(zip(names, levels)) for levels in itertools.product(*(list(factors[n]) for n in names))]
    combos = [c for c in combos if _assignment_key(c) not in excluded]
    limit = compose.get("max_cases", DEFAULT_MAX_CASES)
    if len(combos) > limit:
        return [], [f"{len(combos)} generated cases exceed max_cases {limit}"]

    cases = []
    for assignment in combos:
        key = _assignment_key(assignment)
        case_id = f"{vector['id']}[{key}]"
        try:
            raw = copy.deepcopy(compose["base"])
            for factor, level in assignment:
                raw = apply_edits(raw, factors[factor][level].get("apply", []))
            validated: list = []
            expanded = resolve(raw, fixtures, vectors, None, (), validated)
            for ref, target, value in validated:
                for problem in schema_problems(target, value)[:1]:
                    problems.append(f"{case_id}: expansion of {ref} fails {target}: {problem}")
            steps = _steps(expanded)
            derived = _derive(compose, steps, assignment)
        except ComposeError as exc:
            problems.append(f"{case_id}: {exc}")
            continue
        rejected_stage = derived.get("final_stage") if derived["rejected"] else None
        for step in steps:
            if step.get("stage") == rejected_stage:
                step["result"] = {"messages": [
                    {"type": "error", "code": r["outcome_code"],
                     "content": r.get("content", f"{r['outcome_code']} at {r['path']}"),
                     "severity": "recoverable", "path": r["path"]}
                    for r in derived.get("rejections", [])]}
            elif step.get("stage") in derived["unreached"]:
                step["unreached"] = True
            else:
                step["result"] = {"messages": []}
        expanded["when"] = {"steps": [s for s in steps if not s.get("unreached")]}
        expanded["when"]["unreached"] = [s.get("stage") for s in steps if s.get("unreached")]
        derived.pop("rejections", None)
        expanded["then"] = derived
        expanded = {"id": case_id, "kind": "flow", **expanded}
        for name in compose.get("invariants", []):
            problem = _invariant_problems(name, expanded, derived)
            if problem:
                problems.append(f"{case_id}: invariant {name}: {problem}")
        cases.append((key, expanded))

    anchors = compose.get("anchors", {})
    by_key = dict(cases)
    for key, expected in anchors.items():
        if key not in by_key:
            problems.append(f"anchor {key!r} names no generated case")
            continue
        got = by_key[key]["then"]
        for member, value in expected.items():
            if got.get(member) != value:
                problems.append(f"anchor {key!r}: {member} is {got.get(member)!r}, "
                                f"anchor expects {value!r}")
    if names:
        baseline = [(n, next(iter(factors[n]))) for n in names]
        required = {_assignment_key(baseline)}
        for i, name in enumerate(names):
            for level in list(factors[name])[1:]:
                deviation = list(baseline)
                deviation[i] = (name, level)
                required.add(_assignment_key(deviation))
        for key in sorted(required - set(anchors) - excluded):
            problems.append(f"case {key!r} must be anchored (all-pass or single-factor deviation)")
    return [c for _, c in cases], problems


# --------------------------------------------------------------------------
# requirement evidence
# --------------------------------------------------------------------------

def evidence_problems() -> list[tuple[str, str]]:
    problems: list[tuple[str, str]] = []
    seen: dict[str, str] = {}
    for path in sorted(EVIDENCE_DIR.glob("*.json")) if EVIDENCE_DIR.exists() else []:
        name = path.name
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            problems.append((name, f"not valid JSON: {exc}"))
            continue
        for member in ("topic", "claim_scope", "disclaimer", "capabilities"):
            if member not in doc:
                problems.append((name, f"missing {member}"))
        if doc.get("claim_scope") != "requirement_evidence_only":
            problems.append((name, "claim_scope must be requirement_evidence_only"))
        for cap in doc.get("capabilities", []):
            cid = cap.get("capability_id")
            key = f"{name}:{cid}"
            if not cid:
                problems.append((name, "capability without capability_id"))
                continue
            if cid in seen:
                problems.append((key, f"capability_id also defined in {seen[cid]}"))
            seen[cid] = name
            for member in ("requirement", "evidence", "coverage"):
                if member not in cap:
                    problems.append((key, f"missing {member}"))
            if not cap.get("evidence"):
                problems.append((key, "needs at least one evidence record"))
            for i, ev in enumerate(cap.get("evidence", [])):
                where = f"{key}:evidence[{i}]"
                for member in ("source_type", "source_name", "source_url", "observed_on",
                               "last_verified_on", "evidence_summary", "evidence_status"):
                    if member not in ev:
                        problems.append((where, f"missing {member}"))
                if ev.get("source_type") not in ALLOWED_SOURCE_TYPES:
                    problems.append((where, f"source_type {ev.get('source_type')!r} is not allowed"))
                if ev.get("evidence_status") not in EVIDENCE_STATUSES:
                    problems.append((where, f"evidence_status {ev.get('evidence_status')!r} "
                                     "is not allowed"))
                if not str(ev.get("source_url", "")).startswith("https://"):
                    problems.append((where, "source_url must be a public https:// URL"))
                if "product_area" in ev and "provider" not in ev:
                    problems.append((where, "product_area requires provider"))
                days = []
                for member in ("observed_on", "last_verified_on"):
                    value = ev.get(member, "")
                    if not _valid_date(str(value)):
                        problems.append((where, f"{member} must be an RFC 3339 full-date"))
                    else:
                        days.append(date.fromisoformat(value))
                if len(days) == 2 and days[1] < days[0]:
                    problems.append((where, "last_verified_on is earlier than observed_on"))
            coverage = cap.get("coverage", {})
            if not coverage.get("vectors"):
                problems.append((key, "coverage.vectors must cite at least one vector"))
            for vector_path in coverage.get("vectors", []):
                if not vector_path.startswith("tests/vectors/") or not (REPO / vector_path).is_file():
                    problems.append((key, f"cited vector {vector_path!r} does not exist"))
    return problems
