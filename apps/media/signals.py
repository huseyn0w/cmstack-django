"""Remove the underlying files when a MediaAsset row is deleted.

Django's FileField/ImageField deliberately do NOT delete files from storage when
the model instance is deleted, which would otherwise orphan every upload. A
post_delete receiver also fires for queryset bulk deletes, so this covers the
DeleteView, the admin, and any ORM delete.
"""

from __future__ import annotations

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import MediaAsset


@receiver(post_delete, sender=MediaAsset)
def _delete_files(sender, instance: MediaAsset, **kwargs) -> None:
    if instance.file:
        instance.file.delete(save=False)
    if instance.thumbnail:
        instance.thumbnail.delete(save=False)
