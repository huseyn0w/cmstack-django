import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.media.constants import MAX_UPLOAD_SIZE
from apps.media.forms import MediaUploadForm

from .conftest import make_image

pytestmark = pytest.mark.django_db


def test_valid_image_passes():
    form = MediaUploadForm(files={"file": make_image()})
    assert form.is_valid(), form.errors


def test_disallowed_extension_rejected():
    bad = SimpleUploadedFile(
        "evil.svg", b"<svg onload=alert(1)></svg>", content_type="image/svg+xml"
    )
    form = MediaUploadForm(files={"file": bad})
    assert not form.is_valid()
    assert "file" in form.errors


def test_oversize_rejected(monkeypatch):
    big = make_image()
    monkeypatch.setattr(big, "size", MAX_UPLOAD_SIZE + 1)
    form = MediaUploadForm(files={"file": big})
    assert not form.is_valid()
    assert "file" in form.errors
