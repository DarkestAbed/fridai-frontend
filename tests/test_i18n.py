"""Tests for the i18n text loader."""

import pytest
from app.i18n import t, set_language, get_language, available_languages
from app.i18n.loader import _STRINGS


class TestLoader:
    def test_strings_loaded(self):
        """YAML file should be loaded at import time."""
        assert isinstance(_STRINGS, dict)
        assert len(_STRINGS) > 0

    def test_simple_lookup(self):
        set_language("en")
        assert t("nav.home") == "Home"
        assert t("nav.brand") == "Task Manager"

    def test_nested_lookup(self):
        set_language("en")
        assert t("home.title") == "Task Management Dashboard"

    def test_missing_key_returns_key(self):
        assert t("nonexistent.key") == "nonexistent.key"
        assert t("nav.nonexistent") == "nav.nonexistent"

    def test_deeply_missing_key(self):
        assert t("a.b.c.d.e") == "a.b.c.d.e"

    def test_format_interpolation(self):
        set_language("en")
        result = t("errors.page_load_failed", error="boom")
        assert result == "Failed to load page: boom"

    def test_format_with_missing_kwargs(self):
        """If kwargs don't match template placeholders, return unformatted."""
        set_language("en")
        result = t("errors.page_load_failed")  # no error= kwarg
        assert "{error}" in result

    def test_format_with_extra_kwargs(self):
        """Extra kwargs that don't appear in template are silently ignored."""
        set_language("en")
        result = t("nav.home", extra="ignored")
        assert result == "Home"

    def test_all_sections_present(self):
        """Verify all expected top-level sections exist."""
        set_language("en")
        expected = [
            "shared", "errors", "empty_states", "nav", "home", "tasks",
            "all_tasks", "categories", "tags", "next", "notifications",
            "settings", "task_card", "stats", "notification_templates",
        ]
        for section in expected:
            assert section in _STRINGS, f"Missing section: {section}"

    def test_no_empty_values(self):
        """No string value should be empty (catch accidental blanks)."""
        set_language("en")

        def check_dict(d, prefix=""):
            for k, v in d.items():
                path = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    check_dict(v, path)
                elif isinstance(v, str):
                    assert v.strip(), f"Empty string at {path}"
        check_dict(_STRINGS)


class TestLanguageSwitching:
    def test_get_language_default(self):
        set_language("en")
        assert get_language() == "en"

    def test_switch_to_spanish(self):
        set_language("es")
        assert get_language() == "es"
        assert t("nav.home") == "Inicio"
        assert t("nav.brand") == "Gestor de Tareas"
        # Reset to English for other tests
        set_language("en")

    def test_fallback_to_english(self):
        """Unknown language code falls back to English."""
        set_language("xx_nonexistent")
        assert get_language() == "en"
        assert t("nav.home") == "Home"

    def test_available_languages(self):
        langs = available_languages()
        assert isinstance(langs, list)
        assert len(langs) >= 2
        codes = [code for code, _ in langs]
        assert "en" in codes
        assert "es" in codes
        # Verify display names
        lang_dict = dict(langs)
        assert lang_dict["en"] == "English"
        assert lang_dict["es"] == "Español"
