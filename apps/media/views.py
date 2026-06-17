from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.template.defaultfilters import filesizeformat
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView

from .constants import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE
from .forms import MediaUploadForm
from .models import MediaAsset


class MediaLibraryView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "media.view_mediaasset"
    template_name = "media/library.html"
    context_object_name = "assets"
    paginate_by = 24
    queryset = MediaAsset.objects.select_related("uploaded_by")


class MediaUploadView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "media.add_mediaasset"
    template_name = "media/upload.html"
    form_class = MediaUploadForm
    success_url = reverse_lazy("media:library")

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["allowed_types"] = ", ".join(e.upper() for e in sorted(ALLOWED_EXTENSIONS))
        ctx["max_size"] = filesizeformat(MAX_UPLOAD_SIZE)
        return ctx


class MediaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "media.delete_mediaasset"
    model = MediaAsset
    success_url = reverse_lazy("media:library")
    # Delete only on POST; no confirmation GET page needed for this minimal UI.
    http_method_names = ["post"]
