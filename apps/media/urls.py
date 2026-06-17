from django.urls import path

from . import views

app_name = "media"

urlpatterns = [
    path("library/", views.MediaLibraryView.as_view(), name="library"),
    path("library/upload/", views.MediaUploadView.as_view(), name="upload"),
    path("library/<int:pk>/delete/", views.MediaDeleteView.as_view(), name="delete"),
]
