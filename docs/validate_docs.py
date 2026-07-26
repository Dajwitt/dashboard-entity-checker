#!/usr/bin/env python3
"""Validate bilingual Markdown sources and generated HTML preview."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
MANIFEST = ROOT.parent / "custom_components" / "dashboard_entity_checker" / "manifest.json"
VERSION = json.loads(MANIFEST.read_text(encoding="utf-8"))["version"]
LANGUAGES = ("de", "en")
EXPECTED = {
    "index.md",
    "installation.md",
    "configuration.md",
    "how-it-works.md",
    "supported-references.md",
    "sensor.md",
    "services.md",
    "events.md",
    "notifications.md",
    "ignore-list.md",
    "diagnostics.md",
    "limitations.md",
    "troubleshooting.md",
    "requirements.md",
}
OWNED_ENTITY_IDS = {"sensor.dashboard_entity_checker"}
VERSIONED_PAGES = {"index.md", "installation.md", "diagnostics.md", "requirements.md"}
ENTITY_PATTERN = re.compile(
    r"\b(?:alarm_control_panel|automation|binary_sensor|button|calendar|camera|"
    r"climate|cover|device_tracker|fan|group|humidifier|input_boolean|"
    r"input_button|input_datetime|input_number|input_select|input_text|light|"
    r"lock|media_player|number|person|remote|scene|script|select|sensor|switch|"
    r"timer|update|vacuum|weather|zone)\.[a-z0-9_]+(?:\.[a-z0-9_]+)*\b"
)


def metrics(text: str) -> tuple[list[int], int, int, int, int]:
    headings = [len(match.group(1)) for match in re.finditer(r"^(#{1,3})\s", text, re.M)]
    return (
        headings,
        len(re.findall(r"^```", text, re.M)),
        len(re.findall(r"^\|.*\|$", text, re.M)),
        len(re.findall(r"^- ", text, re.M)),
        len(re.findall(r"^\d+\. ", text, re.M)),
    )


def main() -> int:
    errors: list[str] = []
    source: dict[str, dict[str, str]] = {}
    for language in LANGUAGES:
        files = {path.name for path in (ROOT / language).glob("*.md")}
        if files != EXPECTED:
            errors.append(f"{language}: file set differs: {sorted(files ^ EXPECTED)}")
        source[language] = {}
        for filename in sorted(EXPECTED):
            path = ROOT / language / filename
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            source[language][filename] = text
            if not re.search(r"^# .+", text, re.M):
                errors.append(f"{path}: missing H1")
            if filename in VERSIONED_PAGES and VERSION not in text:
                errors.append(f"{path}: current version {VERSION} is missing")
            for target in re.findall(r"\[[^]]+]\(\./([a-z0-9-]+\.md)\)", text):
                if target not in EXPECTED:
                    errors.append(f"{path}: broken local link {target}")
            scan_text = re.sub(r"\]\([^)]+\)", "]", text)
            scan_text = re.sub(r"https?://\S+", "", scan_text)
            for entity_id in ENTITY_PATTERN.findall(scan_text):
                if entity_id not in OWNED_ENTITY_IDS and ".example_" not in entity_id:
                    errors.append(f"{path}: non-fictional example entity ID {entity_id}")

    for filename in sorted(EXPECTED):
        if filename not in source.get("de", {}) or filename not in source.get("en", {}):
            continue
        if metrics(source["de"][filename]) != metrics(source["en"][filename]):
            errors.append(f"{filename}: DE/EN structural metrics differ")

    html_path = SITE / "index.html"
    if not html_path.exists():
        errors.append("site/index.html is missing")
    else:
        document = html_path.read_text(encoding="utf-8")
        for language in LANGUAGES:
            for filename in EXPECTED:
                slug = filename.removesuffix(".md")
                if f'"{language}/{slug}"' not in document:
                    errors.append(f"site/index.html: missing route {language}/{slug}")
        for required in ("switchLanguage", "setTheme", "toggleMenu", "Filter documentation", "Dokumentation filtern"):
            if required not in document:
                errors.append(f"site/index.html: missing UI token {required}")
        if f"v{VERSION}" not in document:
            errors.append(f"site/index.html: current version v{VERSION} is missing")

    if not (SITE / ".nojekyll").exists():
        errors.append("site/.nojekyll is missing")

    if errors:
        print("Documentation validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Documentation validation passed: 14 pages × 2 languages, links, examples, structure, and HTML routes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
