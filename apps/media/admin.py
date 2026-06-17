"""Interim Django admin for media (the bespoke library UI lands in Phase 5)."""

from django.contrib import admin
from django.utils.html import format_html

from .models import MediaAsset


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("__str__", "preview", "mime_type", "file_size", "uploaded_by", "created_at")
    list_filter = ("mime_type",)
    search_fields = ("title", "alt_text")
    readonly_fields = ("mime_type", "file_size", "width", "height", "thumbnail", "preview")

    @admin.display(description="Preview")
    def preview(self, obj: MediaAsset):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height:60px;border-radius:4px" />', obj.thumbnail.url
            )
        return "—"
