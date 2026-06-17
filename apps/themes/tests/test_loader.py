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
    # Midnight's public_base.html (its dark palette + footer) is now in use.
    assert b"Midnight theme" in response.content
    assert b"16 16 20" in response.content  # midnight --color-paper


def test_switching_back_restores_base(client):
    registry.activate_theme("midnight")
    registry.activate_theme("default")
    response = client.get(reverse("content:post_list"))
    assert b"Midnight theme" not in response.content
