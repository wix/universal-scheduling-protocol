"""Reference projection and scoring checks for availability bitmap ranking."""

from __future__ import annotations

import base64
import re
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from pyroaring import BitMap as _BitMap
except ImportError:  # pragma: no cover - optional until requirements-dev is installed
    _BitMap = None

# Canonical back-massage hint from specification §3.6 / §6.3.
BACK_MASSAGE_HINT: dict[str, Any] = {
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

KNOWN_BITMAP_SETS: dict[str, set[int]] = {
    "OjAAAAEAAAAAAAcAEAAAAAAAAQACAAYACgAOAA8AEAA=": {0, 1, 2, 6, 10, 14, 15, 16},
    "OjAAAAEAAAAAAAMAEAAAAAAAAQAOAA8A": {0, 1, 14, 15},
}

PROJECTION_CASES: tuple[dict[str, Any], ...] = (
    {
        "name": "moment-on-grid",
        "preferences": [{"at": "2026-03-14T10:00:00-04:00"}],
        "intent": {2},
        "intersection": {2},
        "coverage": 1.0,
        "soonness": 1.0,
    },
    {
        "name": "moment-between-grid",
        "preferences": [{"at": "2026-03-14T10:07:00-04:00"}],
        "intent": {3},
        "intersection": set(),
        "coverage": 0.0,
        "soonness": 0.0,
    },
    {
        "name": "moment-before-origin",
        "preferences": [{"at": "2026-03-14T08:00:00-04:00"}],
        "intent": {0},
        "intersection": {0},
        "coverage": 1.0,
        "soonness": 1 - 3600 / (14 * 24 * 3600),
    },
    {
        "name": "moment-final-tick",
        "preferences": [{"at": "2026-03-14T17:00:00-04:00"}],
        "intent": {16},
        "intersection": {16},
        "coverage": 1.0,
        "soonness": 1.0,
    },
    {
        "name": "moment-after-horizon",
        "preferences": [{"at": "2026-03-14T17:01:00-04:00"}],
        "intent": set(),
        "intersection": set(),
        "coverage": None,
    },
    {
        "name": "bounded-aligned",
        "preferences": [{
            "start": "2026-03-14T10:00:00-04:00",
            "end": "2026-03-14T11:30:00-04:00",
        }],
        "intent": {2, 3, 4, 5},
        "intersection": {2},
        "coverage": 0.25,
        "soonness": 1.0,
    },
    {
        "name": "bounded-unaligned",
        "preferences": [{
            "start": "2026-03-14T10:07:00-04:00",
            "end": "2026-03-14T11:20:00-04:00",
        }],
        "intent": {3, 4},
        "intersection": set(),
        "coverage": 0.0,
        "soonness": 0.0,
    },
    {
        "name": "bounded-single-tick",
        "preferences": [{
            "start": "2026-03-14T10:00:00-04:00",
            "end": "2026-03-14T10:00:00-04:00",
        }],
        "intent": {2},
        "intersection": {2},
        "coverage": 1.0,
        "soonness": 1.0,
    },
    {
        "name": "bounded-no-ticks",
        "preferences": [{
            "start": "2026-03-14T10:01:00-04:00",
            "end": "2026-03-14T10:29:00-04:00",
        }],
        "intent": set(),
        "intersection": set(),
        "coverage": None,
    },
    {
        "name": "bounded-end-before-start",
        "preferences": [{
            "start": "2026-03-14T12:00:00-04:00",
            "end": "2026-03-14T11:00:00-04:00",
        }],
        "intent": set(),
        "intersection": set(),
        "coverage": None,
    },
    {
        "name": "bounded-clipped-left",
        "preferences": [{
            "start": "2026-03-14T07:00:00-04:00",
            "end": "2026-03-14T09:00:00-04:00",
        }],
        "intent": {0},
        "intersection": {0},
        "coverage": 1.0,
        "soonness": 1 - 2 * 3600 / (14 * 24 * 3600),
    },
    {
        "name": "bounded-clipped-right",
        "preferences": [{
            "start": "2026-03-14T17:00:00-04:00",
            "end": "2026-03-14T19:00:00-04:00",
        }],
        "intent": {16},
        "intersection": {16},
        "coverage": 1.0,
        "soonness": 1.0,
    },
    {
        "name": "bounded-spans-horizon",
        "preferences": [{
            "start": "2026-03-14T07:00:00-04:00",
            "end": "2026-03-14T19:00:00-04:00",
        }],
        "intent": set(range(17)),
        "intersection": {0, 1, 2, 6, 10, 14, 15, 16},
        "coverage": 8 / 17,
        "soonness": 1 - 2 * 3600 / (14 * 24 * 3600),
    },
    {
        "name": "open-before-origin",
        "preferences": [{"start": "2026-03-14T08:00:00-04:00"}],
        "intent": set(range(17)),
        "intersection": {0, 1, 2, 6, 10, 14, 15, 16},
        "coverage": 8 / 17,
        "soonness": 1 - 3600 / (14 * 24 * 3600),
    },
    {
        "name": "open-inside-horizon",
        "preferences": [{"start": "2026-03-14T16:00:00-04:00"}],
        "intent": {14, 15, 16},
        "intersection": {14, 15, 16},
        "coverage": 1.0,
        "soonness": 1.0,
    },
    {
        "name": "open-final-tick",
        "preferences": [{"start": "2026-03-14T17:00:00-04:00"}],
        "intent": {16},
        "intersection": {16},
        "coverage": 1.0,
        "soonness": 1.0,
    },
    {
        "name": "open-after-horizon",
        "preferences": [{"start": "2026-03-14T17:01:00-04:00"}],
        "intent": set(),
        "intersection": set(),
        "coverage": None,
    },
    {
        "name": "union-disjoint",
        "preferences": [
            {"at": "2026-03-14T10:00:00-04:00"},
            {
                "start": "2026-03-14T14:00:00-04:00",
                "end": "2026-03-14T15:00:00-04:00",
            },
        ],
        "intent": {2, 10, 11, 12},
        "intersection": {2, 10},
        "coverage": 0.5,
        "soonness": 1.0,
    },
    {
        "name": "union-overlap-and-duplicate",
        "preferences": [
            {
                "start": "2026-03-14T09:30:00-04:00",
                "end": "2026-03-14T10:30:00-04:00",
            },
            {
                "start": "2026-03-14T10:00:00-04:00",
                "end": "2026-03-14T11:00:00-04:00",
            },
            {
                "start": "2026-03-14T10:00:00-04:00",
                "end": "2026-03-14T11:00:00-04:00",
            },
        ],
        "intent": {1, 2, 3, 4},
        "intersection": {1, 2},
        "coverage": 0.5,
        "soonness": 1.0,
    },
    {
        "name": "union-mixed-shapes",
        "preferences": [
            {"at": "2026-03-14T10:00:00-04:00"},
            {
                "start": "2026-03-14T14:00:00-04:00",
                "end": "2026-03-14T15:00:00-04:00",
            },
            {"start": "2026-03-14T16:00:00-04:00"},
        ],
        "intent": {2, 10, 11, 12, 14, 15, 16},
        "intersection": {2, 10, 14, 15, 16},
        "coverage": 5 / 7,
        "soonness": 1.0,
    },
    {
        "name": "offset-equivalent-moment",
        "preferences": [{"at": "2026-03-14T14:00:00Z"}],
        "intent": {2},
        "intersection": {2},
        "coverage": 1.0,
        "soonness": 1.0,
    },
)

ROARING32_COOKIE_NO_RUN = 12346
ROARING32_COOKIE = 12347
HORIZON_SECONDS = 14 * 24 * 3600

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
    origin = parse_instant(entry["starts_at"])
    step = timedelta(seconds=iso_duration_seconds(entry["start_interval"]))
    return origin + step * index


def first_index_at_or_after(entry: dict[str, Any], instant: datetime) -> int | None:
    origin = parse_instant(entry["starts_at"])
    step_seconds = iso_duration_seconds(entry["start_interval"])
    if instant < origin:
        return 0
    delta = (instant - origin).total_seconds()
    if step_seconds <= 0:
        raise ValueError("start_interval must be positive")
    index = int(delta // step_seconds)
    if start_instant(entry, index) < instant:
        index += 1
    if index >= entry["slot_count"]:
        return None
    return index


def last_index_at_or_before(entry: dict[str, Any], instant: datetime) -> int | None:
    origin = parse_instant(entry["starts_at"])
    step_seconds = iso_duration_seconds(entry["start_interval"])
    if instant < origin:
        return None
    delta = (instant - origin).total_seconds()
    index = int(delta // step_seconds)
    if start_instant(entry, index) > instant:
        index -= 1
    if index < 0:
        return None
    return index


def project_intent(entry: dict[str, Any], preferences: list[dict[str, Any]]) -> set[int]:
    intent: set[int] = set()
    slot_count = entry["slot_count"]
    for pref in preferences:
        if "at" in pref:
            lo = first_index_at_or_after(entry, parse_instant(pref["at"]))
            if lo is None:
                continue
            hi = lo + 1
        elif "end" in pref:
            start = parse_instant(pref["start"])
            end = parse_instant(pref["end"])
            if end < start:
                continue
            lo = first_index_at_or_after(entry, start)
            if lo is None:
                continue
            last = last_index_at_or_before(entry, end)
            if last is None:
                continue
            hi = last + 1
        else:
            lo = first_index_at_or_after(entry, parse_instant(pref["start"]))
            if lo is None:
                continue
            hi = slot_count
        lo = max(0, lo)
        hi = min(slot_count, hi)
        if lo >= hi:
            continue
        intent.update(range(lo, hi))
    return intent


def preference_anchor(preferences: list[dict[str, Any]]) -> datetime:
    anchors: list[datetime] = []
    for pref in preferences:
        if "at" in pref:
            anchors.append(parse_instant(pref["at"]))
        else:
            anchors.append(parse_instant(pref["start"]))
    return min(anchors)


def soonness(
    entry: dict[str, Any],
    available: set[int],
    intent: set[int],
    *,
    preferences: list[dict[str, Any]] | None,
    scoring_instant: datetime,
    horizon_seconds: int = HORIZON_SECONDS,
) -> float:
    if preferences:
        candidates = available & intent
        anchor = preference_anchor(preferences)
    else:
        candidates = available
        anchor = scoring_instant
    if not candidates:
        return 0.0
    earliest = min(candidates)
    earliest_start = start_instant(entry, earliest)
    delay = max(0.0, (earliest_start - anchor).total_seconds())
    return max(0.0, 1.0 - delay / horizon_seconds)


def score_entry(
    entry: dict[str, Any],
    available: set[int],
    preferences: list[dict[str, Any]] | None,
    *,
    prefer_sooner: bool = True,
    scoring_instant: datetime | None = None,
) -> dict[str, float | None]:
    density = len(available) / entry["slot_count"]
    if not preferences:
        soon = soonness(
            entry,
            available,
            set(),
            preferences=None,
            scoring_instant=scoring_instant or datetime.now(timezone.utc),
        )
        return {"coverage": None, "density": density, "soonness": soon, "density_only": density}

    intent = project_intent(entry, preferences)
    if not intent:
        return {"coverage": None, "density": density, "soonness": None, "match_score": None}

    intersection = available & intent
    coverage = len(intersection) / len(intent)
    soon = soonness(
        entry,
        available,
        intent,
        preferences=preferences,
        scoring_instant=scoring_instant or datetime.now(timezone.utc),
    )
    match_score = coverage * soon if prefer_sooner else coverage
    return {
        "coverage": coverage,
        "density": density,
        "soonness": soon,
        "match_score": match_score,
    }


def select_best_entry(
    hint: dict[str, Any],
    preferences: list[dict[str, Any]] | None,
    *,
    prefer_sooner: bool = True,
    scoring_instant: datetime | None = None,
) -> tuple[dict[str, Any] | None, dict[str, float | None]]:
    best_entry: dict[str, Any] | None = None
    best_score: dict[str, float | None] = {}
    for entry in hint["slot_bitmaps"]:
        available = decode_roaring32_bitmap(entry["bitmap"])
        if any(index >= entry["slot_count"] for index in available):
            raise ValueError("decoded index outside slot_count")
        scored = score_entry(
            entry,
            available,
            preferences,
            prefer_sooner=prefer_sooner,
            scoring_instant=scoring_instant,
        )
        if preferences:
            key = scored.get("match_score")
            if key is None:
                continue
            tie_density = scored["density"] or 0.0
        else:
            if prefer_sooner:
                key = (scored["soonness"] or 0.0, scored["density"] or 0.0)
            else:
                key = scored["density"] or 0.0
            tie_density = scored["density"] or 0.0
        if not best_entry:
            best_entry, best_score = entry, scored
            best_tie = tie_density
            best_key = key
            continue
        if key > best_key or (key == best_key and tie_density > best_tie):
            best_entry, best_score, best_key, best_tie = entry, scored, key, tie_density
    return best_entry, best_score


def dominance_holds(clearly_better_gap: float, max_availability_weight: float) -> bool:
    return max_availability_weight < clearly_better_gap


def hint_is_usable(hint: dict[str, Any] | None, scoring_instant: datetime) -> bool:
    if not hint:
        return False
    valid_until = hint.get("valid_until")
    if not valid_until:
        return True
    return scoring_instant < parse_instant(valid_until)


def assert_close(actual: float, expected: float, *, tol: float = 1e-9) -> None:
    if abs(actual - expected) > tol:
        raise AssertionError(f"expected {expected}, got {actual}")
