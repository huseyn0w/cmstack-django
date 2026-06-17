import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from apps.themes import registry

User = get_user_model()
pytestmark = pytest.mark.django_db


def _user(role):
    u = User.objects.create_user(username=role.lower(), password="pw")
    u.groups.add(Group.objects.get(name=role))
    return u


def test_appearance_requires_manage_settings(client):
    client.force_login(_user("Editor"))  # no manage_settings
    assert client.get(reverse("dashboard:themes")).status_code == 403


def test_admin_sees_theme_list(client):
    client.force_login(_user("Administrator"))
    response = client.get(reverse("dashboard:themes"))
    assert response.status_code == 200
    assert b"Midnight" in response.content


def test_admin_activates_theme(client):
    client.force_login(_user("Administrator"))
    response = client.post(reverse("dashboard:theme_activate", args=["midnight"]))
    assert response.status_code == 302
    assert registry.get_active_theme_slug() == "midnight"


def test_activate_requires_post(client):
    client.force_login(_user("Administrator"))
    assert client.get(reverse("dashboard:theme_activate", args=["midnight"])).status_code == 405


def test_activate_unknown_theme_via_view(client):
    client.force_login(_user("Administrator"))
    response = client.post(reverse("dashboard:theme_activate", args=["nonexistent"]))
    assert response.status_code == 302
    assert registry.get_active_theme_slug() == "default"
