# ruff: noqa: F403, F405

from .base import *

DEBUG = True

INSTALLED_APPS += [
    "debug_toolbar",
    "django_extensions",
]

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1"]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG and not any(
        host in request.META.get("HTTP_HOST", "")
        for host in ["ngrok-free.app", "ngrok.io"]
    ),
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="wynwood"),
        "USER": env("POSTGRES_USER", default="wynwood"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="wynwood_dev"),
        "HOST": env("POSTGRES_HOST", default="localhost"),
        "PORT": env("POSTGRES_PORT", default="5433"),
    }
}

EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

ALLOWED_HOSTS = ALLOWED_HOSTS + [".ngrok-free.app", ".ngrok.io"]
CSRF_TRUSTED_ORIGINS = ["https://*.ngrok-free.app", "https://*.ngrok.io"]

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
    "loggers": {
        "django.core.mail": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps.notifications": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
