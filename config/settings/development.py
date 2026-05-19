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
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
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

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
