# ruff: noqa: F403, F405

from .base import *

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

SECURE_SSL_REDIRECT = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_HSTS_SECONDS = 31_536_000

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

DATABASES = {
    "default": env.db("DATABASE_URL"),
}

DATABASES["default"]["CONN_MAX_AGE"] = 60

DATABASES["default"]["OPTIONS"] = {
    "connect_timeout": 10,
}

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_HOST = env("EMAIL_HOST", default="")

EMAIL_PORT = env.int("EMAIL_PORT", default=587)

EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)

EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")

EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL",
    default="Wynwood House <noreply@wynwoodhouse.com>",
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env("DJANGO_LOG_LEVEL", default="WARNING"),
            "propagate": False,
        },
    },
}
