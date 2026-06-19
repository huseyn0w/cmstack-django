"""The active theme's templates should override the base ones at render time."""

import pytest
from django.urls import reverse

from apps.themes import registry

pytestmark = pytest.mark.django_db


def test_default_theme_uses_base_public_shell(client):
    response = client.get(reverse("content:post_list"))
    assert response.status_code == 200
    assert b"Midnight theme" not in response.content


def test_activating_theme_changes_rendered_template(client):
    registry.activate_theme("midnight")
    response = client.get(reverse("content:post_list"))
    assert response.status_code == 200
    assert b"16 16 20" in response.content  # midnight --color-paper


def test_midnight_is_palette_only_and_keeps_shared_shell(client):
    """A theme recolors via the palette include only; it must NOT fork the whole
    shell, or the header drifts (loses Services / search / language switcher)."""
    registry.activate_theme("midnight")
    html = client.get(reverse("content:post_list")).content
    assert b"16 16 20" in html  # dark palette applied
    # The single shared shell is intact under the theme (can't drift):
    assert b'name="q"' in html  # header search box
    assert b"/services/" in html  # Services nav link


def test_switching_back_restores_base(client):
    registry.activate_theme("midnight")
    registry.activate_theme("default")
    response = client.get(reverse("content:post_list"))
    assert b"Midnight theme" not in response.content
