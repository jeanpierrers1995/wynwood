from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """
    A notification sent to a user.

    Stores what was sent, when and to whom, regardless of the delivery
    channel (email, push, etc.).
    """
    TYPE_BOOKING_CONFIRMED = "booking_confirmed"
    TYPE_BOOKING_CANCELLED = "booking_cancelled"
    TYPE_BOOKING_PENDING = "booking_pending"
    TYPE_GENERAL = "general"

    TYPE_CHOICES = [
        (TYPE_BOOKING_CONFIRMED, _("Booking confirmed")),
        (TYPE_BOOKING_CANCELLED, _("Booking cancelled")),
        (TYPE_BOOKING_PENDING, _("Booking pending")),
        (TYPE_GENERAL, _("General")),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Recipient"),
    )
    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default=TYPE_GENERAL,
        verbose_name=_("Type"),
    )
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    body = models.TextField(blank=True, verbose_name=_("Body"))
    is_read = models.BooleanField(default=False, verbose_name=_("Read"))
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sent at"))

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-sent_at"]

    def __str__(self) -> str:
        return f"[{self.get_notification_type_display()}] {self.subject} → {self.recipient}"

    def mark_as_read(self) -> None:
        """Mark this notification as read and persist the change."""
        if not self.is_read:
            self.is_read = True

            Notification.objects.filter(pk=self.pk).update(is_read=True)
