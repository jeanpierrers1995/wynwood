from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Extended user model with additional profile data.

    Adds phone number, country and preferred language on top of
    Django's standard auth fields.
    """

    LANGUAGE_CHOICES = [
        ("es", "Español"),
        ("en", "English"),
    ]
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Phone"),
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Country"),
    )
    preferred_language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default="es",
        verbose_name=_("Preferred language"),
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return self.email or self.username

    def get_full_name(self) -> str:
        """Return first + last name, falling back to username."""
        full = super().get_full_name()
        return full or self.username
