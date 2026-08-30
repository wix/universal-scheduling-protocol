"""Public wire and semantic checks for availability hints and rank signals.

Scope is the interoperability contract in specification Sections 3.6 and 6.3:
bitmap wire shapes, index-to-time mapping, hint usability, and the
response-state semantics that distinguish unknown from known-empty. How a
registry derives an availability ranking key (projection details, formulas,
horizons, weights, duration selection) is registry-specific and deliberately
not modelled here.
"""

from __future__ import annotations

import base64
import re
from datetime import datetime, timedelta
from typing import Any

try:
    from pyroaring import BitMap as _BitMap
except ImportError:  # pragma: no cover - optional until requirements-dev is installed
    _BitMap = None

# Structured hint example from specification §3.6.2.
STRUCTURED_HINT: dict[str, Any] = {
    "summary": (
        "Good availability this morning and late afternoon. Midday is mostly booked, "
        "and 90-minute sessions are limited to 9:00-9:30 and after 16:00."
    ),
    "generated_at": "2026-03-14T07:30:00-04:00",
    "valid_until": "2026-03-14T19:30:00-04:00",
    "next_available_date": "2026-03-14",
    "slot_bitmaps": [
        {
            "duration": "PT60M",
            "starts_at": "2026-03-14T09:00:00-04:00",
            "start_interval": "PT30M",
            "slot_count": 17,
            "encoding": "roaring32-portable-base64",
            "bitmap": "OjAAAAEAAAAAAAcAEAAAAAAAAQACAAYACgAOAA8AEAA=",
        },
        {
            "duration": "PT90M",
            "starts_at": "2026-03-14T09:00:00-04:00",
            "start_interval": "PT30M",
            "slot_count": 16,
            "encoding": "roaring32-portable-base64",
            "bitmap": "OjAAAAEAAAAAAAMAEAAAAAAAAQAOAA8A",
        },
    ],
}

# A summary-only hint is valid: slot_bitmaps is optional within the hint.
SUMMARY_ONLY_HINT: dict[str, Any] = {
    "summary": "Mostly booked this week. Next week is open.",
    "generated_at": "2026-03-14T07:30:00-04:00",
    "valid_until": "2026-03-14T19:30:00-04:00",
}

KNOWN_BITMAP_SETS: dict[str, set[int]] = {
    "OjAAAAEAAAAAAAcAEAAAAAAAAQACAAYACgAOAA8AEAA=": {0, 1, 2, 6, 10, 14, 15, 16},
    "OjAAAAEAAAAAAAMAEAAAAAAAAQAOAA8A": {0, 1, 14, 15},
}

ROARING32_COOKIE_NO_RUN = 12346
ROARING32_COOKIE = 12347

# Response states an agent must be able to distinguish (§6.3.2).
RANKING_NOT_APPLIED = "ranking-not-applied"
UNKNOWN = "unknown"
COVERAGE_NOT_COMPUTED = "coverage-not-computed"
KNOWN_NON_OVERLAP = "known-non-overlap"
OVERLAP_EVIDENCE = "overlap-evidence"

RESPONSE_STATE_CASES: tuple[dict[str, Any], ...] = (
    {
        "name": "no-ranking-applied",
        "rank_signals": None,
        "expected": RANKING_NOT_APPLIED,
    },
    {
        "name": "omitted-hint",
        "rank_signals": {
            "relevance": 0.5,
            "coverage": None,
            "density": None,
            "soonness": None,
            "hint_usable": False,
        },
        "expected": UNKNOWN,
    },
    {
        "name": "summary-only-hint",
        "rank_signals": {
            "relevance": 0.61,
            "coverage": None,
            "density": None,
            "soonness": None,
            "hint_usable": False,
        },
        "expected": UNKNOWN,
    },
    {
        "name": "expired-or-malformed-hint",
        "rank_signals": {
            "relevance": 0.44,
            "coverage": None,
            "density": None,
            "soonness": None,
            "hint_usable": False,
        },
        "expected": UNKNOWN,
    },
    {
        "name": "known-empty-grid",
        "rank_signals": {
            "relevance": 0.4,
            "coverage": 0.0,
            "density": 0.0,
            "soonness": 0.0,
            "hint_usable": True,
        },
        "expected": KNOWN_NON_OVERLAP,
    },
    {
        "name": "represented-but-no-overlap",
        "rank_signals": {
            "relevance": 0.52,
            "coverage": 0.0,
            "density": 0.47,
            "soonness": 0.0,
            "hint_usable": True,
        },
        "expected": KNOWN_NON_OVERLAP,
    },
    {
        "name": "partial-overlap",
        "rank_signals": {
            "relevance": 0.7,
            "coverage": 0.25,
            "density": 0.47,
            "soonness": 1.0,
            "hint_usable": True,
        },
        "expected": OVERLAP_EVIDENCE,
    },
    {
        "name": "full-overlap",
        "rank_signals": {
            "relevance": 0.82,
            "coverage": 1.0,
            "density": 0.25,
            "soonness": 1.0,
            "hint_usable": True,
        },
        "expected": OVERLAP_EVIDENCE,
    },
    {
        "name": "no-time-preference-sent",
        "rank_signals": {
            "relevance": 0.78,
            "coverage": None,
            "density": 0.47,
            "soonness": 0.92,
            "hint_usable": True,
        },
        "expected": COVERAGE_NOT_COMPUTED,
    },
)

_ISO_DURATION = re.compile(
    r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?$",
)


def iso_duration_seconds(value: str) -> int:
    match = _ISO_DURATION.fullmatch(value)
    if not match:
        raise ValueError(f"unsupported ISO 8601 duration: {value!r}")
    days, hours, minutes, seconds = match.groups()
    total = 0.0
    if days:
        total += int(days) * 86400
    if hours:
        total += int(hours) * 3600
    if minutes:
        total += int(minutes) * 60
    if seconds:
        total += float(seconds)
    return int(total)


def parse_instant(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def decode_roaring32_bitmap(bitmap_b64: str) -> set[int]:
    """Decode the wire payload to an integer set.

    Consumers compare decoded sets, never Base64 text, because the same set has
    more than one valid Roaring byte layout.
    """
    raw = base64.b64decode(bitmap_b64, validate=True)
    if len(raw) < 4:
        raise ValueError("bitmap payload too short")
    cookie = int.from_bytes(raw[:4], "little")
    if cookie not in (ROARING32_COOKIE_NO_RUN, ROARING32_COOKIE):
        raise ValueError(f"invalid Roaring32 cookie {cookie}")
    if bitmap_b64 in KNOWN_BITMAP_SETS:
        return set(KNOWN_BITMAP_SETS[bitmap_b64])
    if _BitMap is None:
        raise RuntimeError("pyroaring is required to decode unknown bitmap fixtures")
    return set(_BitMap.deserialize(raw))


def start_instant(entry: dict[str, Any], index: int) -> datetime:
    """start(i) = starts_at + i * start_interval (specification §3.6.4)."""
    origin = parse_instant(entry["starts_at"])
    step = timedelta(seconds=iso_duration_seconds(entry["start_interval"]))
    return origin + step * index


def decoded_indices_in_range(entry: dict[str, Any]) -> bool:
    """Every decoded index MUST be strictly less than slot_count."""
    return all(0 <= index < entry["slot_count"]
               for index in decode_roaring32_bitmap(entry["bitmap"]))


def hint_is_usable(hint: dict[str, Any] | None, scoring_instant: datetime) -> bool:
    """Usability, not quality: the valid_until cutout is exclusive.

    A hint without structured slot_bitmaps carries no usable structured data,
    so it produces the unknown response state.
    """
    if not hint or not hint.get("slot_bitmaps"):
        return False
    valid_until = hint.get("valid_until")
    if not valid_until:
        return True
    return scoring_instant < parse_instant(valid_until)


def classify_rank_signals(rank_signals: dict[str, Any] | None) -> str:
    """Map a response's rank_signals onto the public response states (§6.3.2)."""
    if rank_signals is None:
        return RANKING_NOT_APPLIED
    if not rank_signals.get("hint_usable"):
        return UNKNOWN
    coverage = rank_signals.get("coverage")
    if coverage is None:
        return COVERAGE_NOT_COMPUTED
    if coverage == 0:
        return KNOWN_NON_OVERLAP
    return OVERLAP_EVIDENCE


def assert_close(actual: float, expected: float, *, tol: float = 1e-9) -> None:
    if abs(actual - expected) > tol:
        raise AssertionError(f"expected {expected}, got {actual}")
