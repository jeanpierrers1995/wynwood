from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from apps.bookings.models import Booking


@receiver(post_save, sender=Booking)
def send_booking_confirmation_email(
    sender,
    instance: Booking,
    created: bool,
    **kwargs,
) -> None:
    """
    Send a confirmation email when a booking reaches 'confirmed' status.

    The email is sent both when a booking is created already confirmed and
    when an existing booking's status is updated to confirmed. The notification
    is also recorded in the DB for audit purposes.

    Args:
        sender: The model class that triggered the signal (Booking).
        instance: The concrete Booking instance that was saved.
        created: True if the object was just created.
        **kwargs: Additional signal arguments (unused).
    """

    if instance.status != Booking.STATUS_CONFIRMED:
        return

    subject = f"Booking confirmation #{instance.pk} — Wynwood House"

    html_message = render_to_string(
        "emails/booking_confirmation.html",
        {"booking": instance},
    )

    send_mail(
        subject=subject,
        message=f"Your booking #{instance.pk} has been confirmed.",
        from_email="noreply@wynwoodhouse.com",
        recipient_list=[instance.guest.email],
        html_message=html_message,
        fail_silently=True,
    )

    try:
        from apps.notifications.models import Notification

        Notification.objects.create(
            recipient=instance.guest,
            notification_type="booking_confirmed",
            subject=subject,
            body=(
                f"Booking #{instance.pk} confirmed "
                f"from {instance.check_in} to {instance.check_out}."
            ),
        )

    except Exception:
        pass
