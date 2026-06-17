from __future__ import annotations

import io
import mimetypes
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image

from .constants import RASTER_IMAGE_EXTENSIONS, THUMBNAIL_SIZE


def upload_to(instance: MediaAsset, filename: str) -> str:
    now = timezone.now()
    return f"library/{now:%Y/%m}/{filename}"


class MediaAsset(models.Model):
    """A single uploaded file in the media library (image or document)."""

    file = models.FileField(_("file"), upload_to=upload_to)
    thumbnail = models.ImageField(
        _("thumbnail"), upload_to="library/thumbnails/", blank=True, null=True
    )
    title = models.CharField(_("title"), max_length=200, blank=True)
    alt_text = models.CharField(_("alt text"), max_length=255, blank=True)

    mime_type = models.CharField(_("MIME type"), max_length=100, blank=True)
    file_size = models.PositiveBigIntegerField(_("file size"), default=0)
    width = models.PositiveIntegerField(_("width"), null=True, blank=True)
    height = models.PositiveIntegerField(_("height"), null=True, blank=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("uploaded by"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="media_assets",
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("media asset")
        verbose_name_plural = _("media assets")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title or os.path.basename(self.file.name)

    def save(self, *args, **kwargs) -> None:
        # Populate metadata and a thumbnail from the freshly uploaded file. Only
        # on the initial upload, so re-saving metadata edits doesn't re-process.
        if self.file and not self.pk:
            self._populate_metadata()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return self.file.url

    @property
    def extension(self) -> str:
        return os.path.splitext(self.file.name)[1].lstrip(".").lower()

    @property
    def is_image(self) -> bool:
        return self.mime_type.startswith("image/")

    def _populate_metadata(self) -> None:
        self.file_size = self.file.size
        guessed, _enc = mimetypes.guess_type(self.file.name)
        self.mime_type = guessed or "application/octet-stream"

        if self.extension not in RASTER_IMAGE_EXTENSIONS:
            return

        # Read the upload once into memory so we can both inspect it and leave the
        # original file pointer ready for Django to persist.
        self.file.seek(0)
        data = self.file.read()
        self.file.seek(0)
        try:
            image = Image.open(io.BytesIO(data))
            image.load()
        except (OSError, Image.DecompressionBombError):
            return

        self.width, self.height = image.size
        self._build_thumbnail(image)

    def _build_thumbnail(self, image: Image.Image) -> None:
        thumb = image.copy()
        thumb.thumbnail(THUMBNAIL_SIZE)
        fmt = (image.format or "PNG").upper()
        if fmt == "JPEG" and thumb.mode in ("RGBA", "P"):
            thumb = thumb.convert("RGB")
        buffer = io.BytesIO()
        thumb.save(buffer, format=fmt)
        base = os.path.splitext(os.path.basename(self.file.name))[0]
        self.thumbnail.save(
            f"{base}_thumb.{fmt.lower()}", ContentFile(buffer.getvalue()), save=False
        )
