"""Minimal i18n loader. One YAML file per language."""

from pathlib import Path
from typing import Any

import yaml

_STRINGS: dict[str, Any] = {}
_LANG: str = "en"
_DIR = Path(__file__).parent


def set_language(lang: str) -> None:
    """Load strings for the given language code. Falls back to English."""
    global _STRINGS, _LANG
    path = _DIR / f"strings_{lang}.yaml"
    if not path.exists():
        path = _DIR / "strings_en.yaml"
        lang = "en"
    with open(path, encoding="utf-8") as f:
        _STRINGS = yaml.safe_load(f) or {}
    _LANG = lang


def get_language() -> str:
    """Return the currently active language code."""
    return _LANG


def available_languages() -> list[tuple[str, str]]:
    """Return list of (code, display_name) for all installed language files."""
    langs = []
    for p in sorted(_DIR.glob("strings_*.yaml")):
        code = p.stem.removeprefix("strings_")
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        name = data.get("meta", {}).get("display_name", code)
        langs.append((code, name))
    return langs


def t(key: str, **kwargs: Any) -> str:
    """Dot-path lookup with .format() interpolation. Returns key on miss."""
    parts = key.split(".")
    node: Any = _STRINGS
    for part in parts:
        if isinstance(node, dict):
            node = node.get(part)
        else:
            return key
    if node is None:
        return key
    result = str(node)
    if kwargs:
        try:
            result = result.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return result


# Load default language at import time
set_language("en")
