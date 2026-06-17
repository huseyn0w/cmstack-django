"""The role sync should grant media permissions per the role map."""

import pytest
from django.contrib.auth.models import Group

pytestmark = pytest.mark.django_db


def test_editor_has_full_media_permissions():
    editor = Group.objects.get(name="Editor")
    codenames = set(editor.permissions.values_list("codename", flat=True))
    assert {
        "add_mediaasset",
        "change_mediaasset",
        "delete_mediaasset",
        "view_mediaasset",
    } <= codenames


def test_author_can_add_but_not_delete_media():
    author = Group.objects.get(name="Author")
    codenames = set(author.permissions.values_list("codename", flat=True))
    assert "add_mediaasset" in codenames
    assert "view_mediaasset" in codenames
    assert "delete_mediaasset" not in codenames


def test_contributor_has_no_media_permissions():
    contributor = Group.objects.get(name="Contributor")
    codenames = set(contributor.permissions.values_list("codename", flat=True))
    assert not any(c.endswith("mediaasset") for c in codenames)
