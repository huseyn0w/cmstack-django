import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from apps.media.models import MediaAsset

from .conftest import make_image

User = get_user_model()
pytestmark = pytest.mark.django_db


def test_library_requires_login(client):
    response = client.get(reverse("media:library"))
    assert response.status_code == 302  # redirected to login


def test_library_forbidden_without_permission(client):
    user = User.objects.create_user(username="plain", password="pw")  # Subscriber-less
    client.force_login(user)
    response = client.get(reverse("media:library"))
    assert response.status_code == 403


def test_editor_can_view_library(client):
    editor = User.objects.create_user(username="ed", password="pw")
    editor.groups.add(Group.objects.get(name="Editor"))
    client.force_login(editor)
    response = client.get(reverse("media:library"))
    assert response.status_code == 200


def test_upload_creates_asset_with_uploader(client):
    editor = User.objects.create_user(username="ed", password="pw")
    editor.groups.add(Group.objects.get(name="Editor"))
    client.force_login(editor)

    response = client.post(
        reverse("media:upload"),
        {"file": make_image(), "title": "Sky", "alt_text": "A sky"},
    )
    assert response.status_code == 302
    asset = MediaAsset.objects.get()
    assert asset.uploaded_by == editor
    assert asset.title == "Sky"


def test_contributor_cannot_upload(client):
    contributor = User.objects.create_user(username="c", password="pw")
    contributor.groups.add(Group.objects.get(name="Contributor"))  # no media.add
    client.force_login(contributor)
    response = client.post(reverse("media:upload"), {"file": make_image()})
    assert response.status_code == 403
    assert MediaAsset.objects.count() == 0


def test_delete_removes_row_and_files(client):
    import os

    editor = User.objects.create_user(username="ed", password="pw")
    editor.groups.add(Group.objects.get(name="Editor"))
    client.force_login(editor)

    asset = MediaAsset.objects.create(file=make_image())
    file_path = asset.file.path
    thumb_path = asset.thumbnail.path
    assert os.path.exists(file_path)

    response = client.post(reverse("media:delete", args=[asset.pk]))
    assert response.status_code == 302
    assert MediaAsset.objects.count() == 0
    # Files are removed from storage, not orphaned.
    assert not os.path.exists(file_path)
    assert not os.path.exists(thumb_path)


def test_delete_rejects_get(client):
    editor = User.objects.create_user(username="ed", password="pw")
    editor.groups.add(Group.objects.get(name="Editor"))
    client.force_login(editor)
    asset = MediaAsset.objects.create(file=make_image())
    assert client.get(reverse("media:delete", args=[asset.pk])).status_code == 405


def test_author_cannot_delete(client):
    author = User.objects.create_user(username="au", password="pw")
    author.groups.add(Group.objects.get(name="Author"))  # add+view, no delete
    client.force_login(author)
    asset = MediaAsset.objects.create(file=make_image())
    assert client.post(reverse("media:delete", args=[asset.pk])).status_code == 403
    assert MediaAsset.objects.count() == 1
