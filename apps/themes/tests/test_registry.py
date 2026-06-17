import pytest

from apps.themes import registry

pytestmark = pytest.mark.django_db


def test_discovers_shipped_themes():
    slugs = {t.slug for t in registry.get_available_themes()}
    assert {"default", "midnight"} <= slugs


def test_default_theme_listed_first():
    themes = registry.get_available_themes()
    assert themes[0].slug == "default"


def test_default_is_active_initially():
    assert registry.get_active_theme_slug() == "default"


def test_activate_known_theme():
    assert registry.activate_theme("midnight") is True
    assert registry.get_active_theme_slug() == "midnight"


def test_activate_unknown_theme_rejected():
    assert registry.activate_theme("does-not-exist") is False
    assert registry.get_active_theme_slug() == "default"


def test_get_theme_rejects_path_traversal():
    # Slugs that escape THEMES_DIR must not resolve to a theme.
    assert registry.get_theme("../config") is None
    assert registry.get_theme("../../etc") is None
    assert registry.activate_theme("../config") is False


def test_default_theme_has_no_template_overrides():
    # The default theme relies on the base templates; no override dir needed.
    assert registry.get_theme("default").has_templates is False
    assert registry.get_theme("midnight").has_templates is True
