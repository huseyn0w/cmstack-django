"""Template loader that resolves the active theme's templates first.

Registered ahead of the filesystem and app loaders, so a file present in the
active theme's ``templates/`` overrides the project/app version. Resolution is
dynamic per render (no compiled-template caching), so switching themes in the
admin takes effect immediately without a restart.
"""

from __future__ import annotations

from django.template.loaders.filesystem import Loader as FilesystemLoader


class ThemeLoader(FilesystemLoader):
    def get_dirs(self):
        from .registry import get_active_template_dir

        template_dir = get_active_template_dir()
        return [template_dir] if template_dir else []
