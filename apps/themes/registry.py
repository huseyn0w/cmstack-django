"""
Theme discovery and activation.

A theme is a directory under ``settings.THEMES_DIR`` containing a ``theme.json``
metadata file and an optional ``templates/`` directory whose files override the
project/app templates at runtime (see :mod:`apps.themes.loaders`). Themes are code
on disk, not database rows; only the *active* theme slug is persisted, on the
``SiteSettings`` singleton.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

DEFAULT_THEME = "default"


@dataclass(frozen=True)
class Theme:
    slug: str
    name: str
    description: str
    version: str
    author: str
    path: Path

    @property
    def template_dir(self) -> Path:
        return self.path / "templates"

    @property
    def has_templates(self) -> bool:
        return self.template_dir.is_dir()


def _themes_dir() -> Path:
    return Path(settings.THEMES_DIR)


def _load_theme(theme_path: Path) -> Theme | None:
    meta_file = theme_path / "theme.json"
    if not meta_file.is_file():
        return None
    try:
        meta = json.loads(meta_file.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    return Theme(
        slug=theme_path.name,
        name=meta.get("name", theme_path.name.title()),
        description=meta.get("description", ""),
        version=str(meta.get("version", "")),
        author=meta.get("author", ""),
        path=theme_path,
    )


def get_available_themes() -> list[Theme]:
    """All discoverable themes, sorted with the default first then by name."""
    base = _themes_dir()
    if not base.is_dir():
        return []
    themes = [
        theme
        for child in sorted(base.iterdir())
        if child.is_dir() and (theme := _load_theme(child)) is not None
    ]
    themes.sort(key=lambda t: (t.slug != DEFAULT_THEME, t.name.lower()))
    return themes


def get_theme(slug: str) -> Theme | None:
    base = _themes_dir().resolve()
    theme_path = (base / slug).resolve()
    # Containment: a theme is a DIRECT child of THEMES_DIR. This rejects path
    # traversal (e.g. slug="../secret") no matter how the slug arrived — the HTTP
    # route already constrains it, but registry functions are also called from
    # management commands / future MCP tools.
    if theme_path.parent != base:
        return None
    return _load_theme(theme_path)


def get_active_theme_slug() -> str:
    """Active theme slug from SiteSettings, defensively (DB may be unavailable)."""
    from django.db import OperationalError, ProgrammingError

    try:
        from apps.core.models import SiteSettings

        return SiteSettings.load().active_theme or DEFAULT_THEME
    except (OperationalError, ProgrammingError):
        # Table may not exist yet (pre-migrate) or DB unreachable — fall back.
        return DEFAULT_THEME


def get_active_theme() -> Theme | None:
    return get_theme(get_active_theme_slug())


def get_active_template_dir() -> Path | None:
    """Template directory of the active theme, or None if it has no overrides."""
    theme = get_active_theme()
    if theme and theme.has_templates:
        return theme.template_dir
    return None


def activate_theme(slug: str) -> bool:
    """Persist ``slug`` as the active theme. Returns False for unknown themes."""
    if get_theme(slug) is None:
        return False
    from apps.core.models import SiteSettings

    site = SiteSettings.load()
    site.active_theme = slug
    site.save()  # clears the SiteSettings cache
    return True
