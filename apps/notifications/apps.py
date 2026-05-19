from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Configuration for the notifications Django application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"

    def ready(self) -> None:
        """Import signal handlers so they are registered at startup."""
