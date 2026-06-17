import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    """Write uploads to a throwaway temp dir for every media test."""
    settings.MEDIA_ROOT = str(tmp_path)
    return tmp_path


def make_image(name: str = "pic.png", size=(800, 600), fmt: str = "PNG") -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", size, (120, 80, 40)).save(buffer, format=fmt)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=f"image/{fmt.lower()}")
