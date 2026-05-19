"""
Booking models for Wynwood House.

Manages the full lifecycle of a reservation: creation, date validation,
overlap prevention, price calculation and status tracking.
"""

import builtins
import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Booking(models.Model):
    """
    A property reservation made by a guest.

    Business rules are enforced in ``clean()`` (coherent dates, no overlap,
    capacity). The total price is calculated automatically in ``save()``.
    """
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, _("Pending")),
        (STATUS_CONFIRMED, _("Confirmed")),
        (STATUS_CANCELLED, _("Cancelled")),
    ]

    PAYMENT_CARD = "card"
    PAYMENT_APPLE_PAY = "apple_pay"
    PAYMENT_GOOGLE_PAY = "google_pay"

    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_CARD, _("Credit card")),
        (PAYMENT_APPLE_PAY, _("Apple Pay")),
        (PAYMENT_GOOGLE_PAY, _("Google Pay")),
    ]

    property = models.ForeignKey(
        "properties.Property",
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name=_("Property"),
    )
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name=_("Guest"),
    )
    check_in = models.DateField(verbose_name=_("Check-in date"))
    check_out = models.DateField(verbose_name=_("Check-out date"))
    num_guests = models.PositiveIntegerField(verbose_name=_("Number of guests"))
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Total price"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name=_("Status"),
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_CARD,
        verbose_name=_("Payment method"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")
        ordering = ["-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(check_out__gt=models.F("check_in")),
                name="check_out_after_check_in",
            )
        ]

    def clean(self) -> None:
        """
        Validate business rules before saving:

        - Check-out must be after check-in.
        - Check-in cannot be in the past.
        - No overlapping bookings may exist for the same property.
        - Number of guests cannot exceed the property's maximum capacity.
        """
        if self.check_in and self.check_out:
            if self.check_in >= self.check_out:
                raise ValidationError(
                    _("Check-out date must be after the check-in date.")
                )

            if self.check_in < datetime.date.today():
                raise ValidationError(_("Check-in date cannot be in the past."))

            overlapping = Booking.objects.filter(
                property=self.property,
                status__in=[self.STATUS_PENDING, self.STATUS_CONFIRMED],
                check_in__lt=self.check_out,
                check_out__gt=self.check_in,
            ).exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError(
                    _("The selected dates are not available for this property.")
                )

        if (
            self.property_id
            and self.num_guests
            and self.num_guests > self.property.max_guests
        ):
            raise ValidationError(
                _(
                    "Number of guests (%(requested)s) exceeds the property's "
                    "maximum capacity (%(max)s)."
                )
                % {"requested": self.num_guests, "max": self.property.max_guests}
            )

    def save(self, *args, **kwargs) -> None:
        """
        Run ``full_clean()`` and calculate the total price before saving.

        The price is always recalculated from the current nightly rate,
        ensuring it stays consistent with any price updates on the property.
        """
        self.full_clean()

        if self.check_in and self.check_out and self.property_id:
            nights = (self.check_out - self.check_in).days
            self.total_price = nights * self.property.price_per_night

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"Booking #{self.pk} — {self.property} ({self.check_in} → {self.check_out})"
        )

    @builtins.property
    def nights(self) -> int:
        """Return the number of nights for this stay."""

        return (self.check_out - self.check_in).days
