"""Production settings: secure defaults, fail loudly on misconfiguration."""

from .base import *  # noqa: F401,F403

DEBUG = False

# SECRET_KEY and ALLOWED_HOSTS must be provided via the environment in prod.
SECRET_KEY = env("DJANGO_SECRET_KEY")  # noqa: F405  # raises if missing
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")  # noqa: F405  # raises if missing

# --------------------------------------------------------------------------- #
# Security hardening — assumes TLS termination in front of the app.
# --------------------------------------------------------------------------- #
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=31536000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
# SECURE_CONTENT_TYPE_NOSNIFF is set in base.py for all environments.
X_FRAME_OPTIONS = "DENY"

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405

# Built assets are always served from the manifest in production.
DJANGO_VITE["default"]["dev_mode"] = False  # noqa: F405
