"""
Development settings.
"""

from .base import *

DEBUG = config("DEBUG", default=True, cast=bool)

# Only add debug toolbar if installed
try:
    import debug_toolbar  # type: ignore[import-untyped]  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
except ImportError:
    pass

CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
