"""Pure dashboard parser for direct entity references.

Phase 2 intentionally handles only complete entity IDs stored as scalar values.
JavaScript strings and decluttering-template expansion are implemented in later phases.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .const import ENTITY_DOMAINS

_ENTITY_ID_RE = re.compile(
    rf"^(?:{'|'.join(re.escape(domain) for domain in ENTITY_DOMAINS)})\."
    r"[a-z0-9_]+$"
)

# Values of these keys are service/action names, not entity references.
_SERVICE_KEYS = {"service", "perform_action"}


@dataclass(frozen=True, slots=True)
class ParsedDashboard:
    """Direct entity references grouped by dashboard view."""

    entities: dict[str, list[str]]
    views: list[str]

    @property
    def checked_entities(self) -> int:
        """Return number of unique referenced entities."""
        return len(self.entities)


def parse_dashboard(config: dict[str, Any]) -> ParsedDashboard:
    """Extract direct entity IDs and associate them with their views.

    Only complete scalar values such as ``sensor.temperature`` are recognized.
    Embedded IDs in JavaScript or other text are deliberately ignored in Phase 2.
    Duplicate references are collapsed once per view.
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
        _collect_direct_entities(view, found_in_view)

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


def _collect_direct_entities(value: Any, found: set[str], key: str | None = None) -> None:
    """Recursively collect complete entity IDs from mappings and sequences."""
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            _collect_direct_entities(child_value, found, str(child_key))
        return

    if isinstance(value, list):
        for child_value in value:
            _collect_direct_entities(child_value, found, key)
        return

    if not isinstance(value, str) or key in _SERVICE_KEYS:
        return

    if _ENTITY_ID_RE.fullmatch(value):
        found.add(value)
