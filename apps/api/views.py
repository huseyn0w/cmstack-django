"""Public read API viewsets + health probes.

Viewsets are the HTTP boundary: ``get_queryset`` delegates to ``api.services``
(which uses content repositories) and serializers own representation. Read access
is public; the write/MCP surfaces are separate and auth-gated.
"""

from __future__ import annotations

from django.conf import settings
from django.http import JsonResponse
from django.utils import translation
from rest_framework import viewsets

from . import serializers, services


class LanguageScopedMixin:
    """Activate a requested ``?lang=`` (if configured) for this request only.

    The API lives outside ``i18n_patterns``, so without this parler serialises the
    default language. ``?lang=de`` lets a client pull German translations.
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        lang = request.query_params.get("lang")
        if lang and lang in dict(settings.LANGUAGES):
            translation.activate(lang)


class PostViewSet(LanguageScopedMixin, viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"

    def get_queryset(self):
        return services.published_posts()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.PostDetailSerializer
        return serializers.PostSerializer


class PageViewSet(LanguageScopedMixin, viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"

    def get_queryset(self):
        return services.published_pages()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.PageDetailSerializer
        return serializers.PageSerializer


class ServiceViewSet(LanguageScopedMixin, viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"

    def get_queryset(self):
        return services.published_services()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.ServiceDetailSerializer
        return serializers.ServiceSerializer


class CategoryViewSet(LanguageScopedMixin, viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    serializer_class = serializers.CategorySerializer

    def get_queryset(self):
        return services.all_categories()


class TagViewSet(LanguageScopedMixin, viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        return services.all_tags()


# --- Health / readiness (plain JSON, no DRF machinery needed) --- #
def health(request) -> JsonResponse:
    """Liveness: the process is up and serving."""
    return JsonResponse({"status": "ok"})


def readiness(request) -> JsonResponse:
    """Readiness: the app can reach its database."""
    ok = services.database_ok()
    return JsonResponse(
        {"status": "ok" if ok else "unavailable", "database": ok},
        status=200 if ok else 503,
    )
