"""Pure dashboard parser for direct and JavaScript entity references.

Decluttering-template expansion is intentionally deferred to Phase 5.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .const import ENTITY_DOMAINS

_DOMAIN_PATTERN = "|".join(re.escape(domain) for domain in ENTITY_DOMAINS)
_ENTITY_PATTERN = rf"(?:{_DOMAIN_PATTERN})\.[a-z0-9_]+"

_ENTITY_ID_RE = re.compile(rf"^{_ENTITY_PATTERN}$")
_ENTITY_ID_IN_TEXT_RE = re.compile(
    rf"(?<![a-z0-9_])(?P<entity>{_ENTITY_PATTERN})(?![a-z0-9_])"
)
_STATES_BRACKET_RE = re.compile(
    rf"states\s*\[\s*(['\"])(?P<entity>{_ENTITY_PATTERN})\1\s*\]"
)
_STATES_DOT_RE = re.compile(rf"states\.(?P<entity>{_ENTITY_PATTERN})(?![a-z0-9_])")
_SERVICE_CONTEXT_RE = re.compile(
    r"\b(?:service|perform_action|action)\s*[:=]\s*['\"]?\s*$",
    re.IGNORECASE,
)
_JAVASCRIPT_MARKER_RE = re.compile(
    r"(?:\[\[\[|\]\]\]|\b(?:const|let|var|return|function)\b|=>|states\s*[.[])"
)

# Values of these keys are service/action names, not entity references.
_SERVICE_KEYS = {"service", "perform_action"}

# Generic entity-like text in these fields is usually CSS, a URL or metadata.
# Explicit states[...] / states.domain.object access is still recognized there.
_NON_ENTITY_TEXT_KEYS = {"style", "styles", "card_mod", "url", "icon", "type"}


@dataclass(frozen=True, slots=True)
class ParsedDashboard:
    """Entity references grouped by dashboard view."""

    entities: dict[str, list[str]]
    views: list[str]

    @property
    def checked_entities(self) -> int:
        """Return number of unique referenced entities."""
        return len(self.entities)


def parse_dashboard(config: dict[str, Any]) -> ParsedDashboard:
    """Extract direct and JavaScript entity IDs with their dashboard views.

    Complete scalar entity IDs are always recognized outside service fields.
    Phase 4 additionally scans JavaScript blocks, including comments. Duplicate
    references are collapsed once per view.
    """
    raw_views = config.get("views", [])
    if not isinstance(raw_views, list):
        return ParsedDashboard(entities={}, views=[])

    entities: dict[str, list[str]] = {}
    view_names: list[str] = []

    for index, view in enumerate(raw_views):
        if not isinstance(view, dict):
            continue

        view_name = _view_name(view, index)
        view_names.append(view_name)
        found_in_view: set[str] = set()
        _collect_entities(view, found_in_view)

        for entity_id in sorted(found_in_view):
            entities.setdefault(entity_id, []).append(view_name)

    return ParsedDashboard(entities=entities, views=view_names)


def _view_name(view: dict[str, Any], index: int) -> str:
    """Return a stable human-readable view name."""
    title = view.get("title")
    path = view.get("path")
    if isinstance(title, str) and title:
        return title
    if isinstance(path, str) and path:
        return path
    return f"view_{index}"


def _collect_entities(value: Any, found: set[str], key: str | None = None) -> None:
    """Recursively collect direct IDs and JavaScript references."""
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            _collect_entities(child_value, found, str(child_key))
        return

    if isinstance(value, list):
        for child_value in value:
            _collect_entities(child_value, found, key)
        return

    if not isinstance(value, str) or key in _SERVICE_KEYS:
        return

    if _ENTITY_ID_RE.fullmatch(value):
        found.add(value)
        return

    _collect_javascript_entities(value, found, key)


def _collect_javascript_entities(
    text: str, found: set[str], key: str | None
) -> None:
    """Extract explicit state access and safe generic IDs from JavaScript."""
    for pattern in (_STATES_BRACKET_RE, _STATES_DOT_RE):
        found.update(match.group("entity") for match in pattern.finditer(text))

    if key in _NON_ENTITY_TEXT_KEYS or not _looks_like_javascript(text):
        return

    for match in _ENTITY_ID_IN_TEXT_RE.finditer(text):
        if _is_non_entity_occurrence(text, match.start(), match.end()):
            continue
        found.add(match.group("entity"))


def _looks_like_javascript(text: str) -> bool:
    """Return whether a scalar contains recognizable JavaScript syntax."""
    return _JAVASCRIPT_MARKER_RE.search(text) is not None


def _is_non_entity_occurrence(text: str, start: int, end: int) -> bool:
    """Filter service assignments, URLs and CSS class selectors."""
    if not _inside_javascript_string_or_comment(text, start):
        return True

    if text[end : end + 2] == "${":
        return True

    if start > 0 and text[start - 1] == ".":
        return True

    context = text[max(0, start - 100) : start]
    if _SERVICE_CONTEXT_RE.search(context):
        return True

    token_start = max(
        context.rfind(" "),
        context.rfind("\n"),
        context.rfind("\t"),
        context.rfind("'"),
        context.rfind('"'),
        context.rfind("`"),
    )
    return "://" in context[token_start + 1 :]


def _inside_javascript_string_or_comment(text: str, start: int) -> bool:
    """Accept quoted literals and comments, but reject object properties."""
    line_start = text.rfind("\n", 0, start) + 1
    line_prefix = text[line_start:start]
    if "//" in line_prefix:
        return True

    if text.rfind("/*", 0, start) > text.rfind("*/", 0, start):
        return True

    active_quote: str | None = None
    escaped = False
    for char in text[:start]:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if active_quote:
            if char == active_quote:
                active_quote = None
            continue
        if char in {"'", '"', "`"}:
            active_quote = char

    return active_quote is not None
