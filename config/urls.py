"""Root URL configuration for DjangoPress."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # django-allauth: login, signup, logout, password reset, social login.
    path("accounts/", include("allauth.urls")),
    path("", include("apps.media.urls")),
    path("", include("apps.content.urls")),
    path("", include("apps.core.urls")),
]

# Serve user-uploaded media in development. In production these are served by the
# web server / object storage in front of the app.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
