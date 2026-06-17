import pytest

from apps.media.models import MediaAsset

from .conftest import make_image

pytestmark = pytest.mark.django_db


def test_image_upload_populates_metadata_and_thumbnail():
    asset = MediaAsset.objects.create(file=make_image(size=(800, 600)))
    assert asset.mime_type == "image/png"
    assert asset.file_size > 0
    assert asset.width == 800
    assert asset.height == 600
    assert asset.is_image
    assert asset.thumbnail  # a thumbnail was generated


def test_thumbnail_is_downscaled_within_bounds():
    asset = MediaAsset.objects.create(file=make_image(size=(1600, 1200)))
    from PIL import Image

    with Image.open(asset.thumbnail.path) as thumb:
        assert max(thumb.size) <= 400


def test_non_image_has_no_dimensions(tmp_path):
    from django.core.files.uploadedfile import SimpleUploadedFile

    pdf = SimpleUploadedFile("doc.pdf", b"%PDF-1.4 fake", content_type="application/pdf")
    asset = MediaAsset.objects.create(file=pdf)
    assert asset.mime_type == "application/pdf"
    assert not asset.is_image
    assert asset.width is None
    assert not asset.thumbnail


def test_str_prefers_title():
    asset = MediaAsset.objects.create(file=make_image(), title="Hero shot")
    assert str(asset) == "Hero shot"


def test_jpeg_and_gif_thumbnails():
    jpeg = MediaAsset.objects.create(file=make_image("p.jpg", fmt="JPEG"))
    gif = MediaAsset.objects.create(file=make_image("p.gif", fmt="GIF"))
    assert jpeg.thumbnail and gif.thumbnail


def test_unreadable_image_falls_back_gracefully():
    from django.core.files.uploadedfile import SimpleUploadedFile

    broken = SimpleUploadedFile("broken.png", b"this is not a real png", content_type="image/png")
    asset = MediaAsset.objects.create(file=broken)
    # mime is guessed from the extension, but Pillow can't read it:
    assert asset.width is None and asset.height is None
    assert not asset.thumbnail


def test_stored_file_is_intact_after_metadata_read():
    img = make_image(size=(640, 480))
    original_len = len(img.read())
    img.seek(0)
    asset = MediaAsset.objects.create(file=img)
    with asset.file.open("rb") as fh:
        assert len(fh.read()) == original_len
