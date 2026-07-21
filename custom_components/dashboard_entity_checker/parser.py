"""Pure dashboard parser for direct, JavaScript and decluttering references."""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from typing import Any

from .const import ENTITY_DOMAINS

MAX_TEMPLATE_DEPTH = 20
_DECLUTTERING_CARD_TYPE = "custom:decluttering-card"

_DOMAIN_PATTERN = "|".join(re.escape(domain) for domain in ENTITY_DOMAINS)
_ENTITY_PATTERN = rf"(?:{_DOMAIN_PATTERN})\.[a-z0-9_]+"

_ENTITY_ID_RE = re.compile(rf"^{_ENTITY_PATTERN}$")
_ENTITY_ID_IN_TEXT_RE = re.compile(
    rf"(?<![a-z0-9_])(?P<entity>{_ENTITY_PATTERN})(?![a-z0-9_.])"
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
# Negative lookarounds keep Button-Card's [[[ JavaScript ]]] syntax intact.
_DECLUTTERING_PLACEHOLDER_RE = re.compile(
    r"(?<!\[)\[\[\s*(?P<variable>[A-Za-z0-9_]+)\s*\]\](?!\])"
)

# Values of these keys are service/action names, not entity references.
_SERVICE_KEYS = {"service", "perform_action"}

# Generic entity-like text in these fields is usually CSS, a URL or metadata.
# Explicit states[...] / states.domain.object access is still recognized there.
_NON_ENTITY_TEXT_KEYS = {"style", "styles", "card_mod", "url", "icon", "type"}


@dataclass(frozen=True, slots=True)
class ParserDiagnostic:
    """A non-fatal problem encountered while resolving a template."""

    code: str
    message: str
    view: str
    template: str | None = None
    variable: str | None = None


@dataclass(frozen=True, slots=True)
class ParsedDashboard:
    """Entity and template references grouped by dashboard view."""

    entities: dict[str, list[str]]
    views: list[str]
    templates: dict[str, list[str]]
    diagnostics: tuple[ParserDiagnostic, ...]

    @property
    def checked_entities(self) -> int:
        """Return number of unique referenced entities."""
        return len(self.entities)


@dataclass(slots=True)
class _ParseContext:
    """Shared state for one parser run."""

    templates: dict[str, Any]
    template_views: dict[str, list[str]]
    diagnostics: list[ParserDiagnostic]
    view_name: str


def parse_dashboard(config: dict[str, Any]) -> ParsedDashboard:
    """Extract rendered entity IDs and associate them with dashboard views.

    The parser handles direct scalar IDs, Button-Card JavaScript and nested
    decluttering templates. Template problems are returned as diagnostics and
    do not abort the scan.
    """
    raw_views = config.get("views", [])
    if not isinstance(raw_views, list):
        return ParsedDashboard({}, [], {}, ())

    raw_templates = config.get("decluttering_templates", {})
    templates = raw_templates if isinstance(raw_templates, dict) else {}

    entities: dict[str, list[str]] = {}
    template_views: dict[str, list[str]] = {}
    diagnostics: list[ParserDiagnostic] = []
    view_names: list[str] = []

    for index, view in enumerate(raw_views):
        if not isinstance(view, dict):
            continue

        view_name = _view_name(view, index)
        view_names.append(view_name)
        found_in_view: set[str] = set()
        context = _ParseContext(
            templates=templates,
            template_views=template_views,
            diagnostics=diagnostics,
            view_name=view_name,
        )
        _collect_entities(view, found_in_view, context)

        for entity_id in sorted(found_in_view):
            entities.setdefault(entity_id, []).append(view_name)

    return ParsedDashboard(
        entities=entities,
        views=view_names,
        templates=template_views,
        diagnostics=tuple(diagnostics),
    )


def _view_name(view: dict[str, Any], index: int) -> str:
    """Return a stable human-readable view name."""
    title = view.get("title")
    path = view.get("path")
    if isinstance(title, str) and title:
        return title
    if isinstance(path, str) and path:
        return path
    return f"view_{index}"


def _collect_entities(
    value: Any,
    found: set[str],
    context: _ParseContext,
    key: str | None = None,
    template_stack: tuple[str, ...] = (),
    depth: int = 0,
) -> None:
    """Recursively collect rendered IDs from all supported source types."""
    if isinstance(value, dict):
        if value.get("type") == _DECLUTTERING_CARD_TYPE:
            _collect_decluttering_card(
                value, found, context, template_stack, depth
            )
            return
        for child_key, child_value in value.items():
            _collect_entities(
                child_value,
                found,
                context,
                str(child_key),
                template_stack,
                depth,
            )
        return

    if isinstance(value, list):
        for child_value in value:
            _collect_entities(
                child_value, found, context, key, template_stack, depth
            )
        return

    if not isinstance(value, str) or key in _SERVICE_KEYS:
        return

    if _ENTITY_ID_RE.fullmatch(value):
        found.add(value)
        return

    _collect_javascript_entities(value, found, key)


def _collect_decluttering_card(
    card: dict[str, Any],
    found: set[str],
    context: _ParseContext,
    template_stack: tuple[str, ...],
    depth: int,
) -> None:
    """Resolve one decluttering-card and scan its rendered card recursively."""
    raw_name = card.get("template")
    template_name = raw_name if isinstance(raw_name, str) and raw_name else None

    if template_name is None:
        _add_diagnostic(
            context,
            ParserDiagnostic(
                code="missing_template",
                message="Decluttering-Card enthält keinen gültigen Template-Namen.",
                view=context.view_name,
            ),
        )
        return

    if template_name in template_stack:
        chain = " -> ".join((*template_stack, template_name))
        _add_diagnostic(
            context,
            ParserDiagnostic(
                code="circular_template",
                message=f"Zirkuläre Template-Kette: {chain}",
                view=context.view_name,
                template=template_name,
            ),
        )
        return

    if depth >= MAX_TEMPLATE_DEPTH:
        _add_diagnostic(
            context,
            ParserDiagnostic(
                code="max_template_depth",
                message=(
                    f"Maximale Template-Tiefe {MAX_TEMPLATE_DEPTH} bei "
                    f"{template_name} erreicht."
                ),
                view=context.view_name,
                template=template_name,
            ),
        )
        return

    template = context.templates.get(template_name)
    if not isinstance(template, dict) or "card" not in template:
        _add_diagnostic(
            context,
            ParserDiagnostic(
                code="missing_template",
                message=f"Decluttering-Template {template_name} wurde nicht gefunden.",
                view=context.view_name,
                template=template_name,
            ),
        )
        return

    views = context.template_views.setdefault(template_name, [])
    if context.view_name not in views:
        views.append(context.view_name)

    variables = _variables_to_mapping(
        template.get("default"), context, template_name, "default"
    )
    variables.update(
        _variables_to_mapping(
            card.get("variables"), context, template_name, "variables"
        )
    )

    unknown_variables: set[str] = set()
    rendered_card = _substitute_placeholders(
        template["card"], variables, unknown_variables
    )
    for variable in sorted(unknown_variables):
        _add_diagnostic(
            context,
            ParserDiagnostic(
                code="unknown_variable",
                message=(
                    f"Variable {variable} fehlt beim Template {template_name}."
                ),
                view=context.view_name,
                template=template_name,
                variable=variable,
            ),
        )

    _collect_entities(
        rendered_card,
        found,
        context,
        template_stack=(*template_stack, template_name),
        depth=depth + 1,
    )


def _variables_to_mapping(
    raw_variables: Any,
    context: _ParseContext,
    template_name: str,
    source: str,
) -> dict[str, Any]:
    """Normalize decluttering default/variable list syntax to a mapping."""
    if raw_variables is None:
        return {}
    if isinstance(raw_variables, dict):
        return {str(key): value for key, value in raw_variables.items()}
    if isinstance(raw_variables, list):
        result: dict[str, Any] = {}
        invalid = False
        for item in raw_variables:
            if not isinstance(item, dict):
                invalid = True
                continue
            result.update({str(key): value for key, value in item.items()})
        if invalid:
            _add_diagnostic(
                context,
                ParserDiagnostic(
                    code="invalid_variables",
                    message=(
                        f"Ungültige {source}-Einträge beim Template {template_name}."
                    ),
                    view=context.view_name,
                    template=template_name,
                ),
            )
        return result

    _add_diagnostic(
        context,
        ParserDiagnostic(
            code="invalid_variables",
            message=f"Ungültiges Feld {source} beim Template {template_name}.",
            view=context.view_name,
            template=template_name,
        ),
    )
    return {}


def _substitute_placeholders(
    value: Any, variables: dict[str, Any], unknown_variables: set[str]
) -> Any:
    """Recursively replace decluttering placeholders without mutating config."""
    if isinstance(value, dict):
        rendered: dict[Any, Any] = {}
        for key, child in value.items():
            rendered_key = _substitute_placeholders(key, variables, unknown_variables)
            if isinstance(rendered_key, (dict, list)):
                rendered_key = str(rendered_key)
            rendered[rendered_key] = _substitute_placeholders(
                child, variables, unknown_variables
            )
        return rendered

    if isinstance(value, list):
        return [
            _substitute_placeholders(child, variables, unknown_variables)
            for child in value
        ]

    if not isinstance(value, str):
        return copy.deepcopy(value)

    full_match = _DECLUTTERING_PLACEHOLDER_RE.fullmatch(value)
    if full_match:
        variable = full_match.group("variable")
        if variable not in variables:
            unknown_variables.add(variable)
            return value
        return copy.deepcopy(variables[variable])

    def replace(match: re.Match[str]) -> str:
        variable = match.group("variable")
        if variable not in variables:
            unknown_variables.add(variable)
            return match.group(0)
        replacement = variables[variable]
        return replacement if isinstance(replacement, str) else str(replacement)

    return _DECLUTTERING_PLACEHOLDER_RE.sub(replace, value)


def _add_diagnostic(context: _ParseContext, diagnostic: ParserDiagnostic) -> None:
    """Add one stable diagnostic without duplicate spam."""
    if diagnostic not in context.diagnostics:
        context.diagnostics.append(diagnostic)


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
