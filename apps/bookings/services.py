"""
Booking business-logic service layer.

Encapsulates reservation creation, separating concerns between the
model layer (persistence/constraints) and the view layer (HTTP handling).
"""

import datetime

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.bookings.models import Booking
from apps.properties.models import Property


class BookingError(Exception):
    """
    Domain-specific exception raised by the booking service.

    Allows callers (views) to distinguish expected business-rule failures
    from unexpected system errors without catching generic exceptions.
    """


def create_booking(
    property: Property,
    guest,
    check_in: datetime.date,
    check_out: datetime.date,
    num_guests: int,
    payment_method: str = Booking.PAYMENT_CARD,
) -> Booking:
    """
    Create and persist a new booking after applying all business validations.

    Args:
        property: The property instance to be booked.
        guest: The user making the reservation.
        check_in: Arrival date (must not be in the past).
        check_out: Departure date (must be after check_in).
        num_guests: Number of guests (must not exceed property.max_guests).
        payment_method: One of 'card', 'apple_pay', 'google_pay'.

    Returns:
        The newly created and saved ``Booking`` instance.

    Raises:
        BookingError: If any business rule is violated, with a human-readable
            message suitable for display in the UI.
    """
    if not property.is_active:
        raise BookingError(_("The selected property is not available."))

    if not isinstance(check_in, datetime.date) or not isinstance(
        check_out, datetime.date
    ):
        raise BookingError(_("Check-in and check-out dates are required."))

    if check_in < datetime.date.today():
        raise BookingError(_("Check-in date cannot be earlier than today."))

    if check_in >= check_out:
        raise BookingError(_("Check-out date must be after the check-in date."))

    if num_guests < 1:
        raise BookingError(_("Number of guests must be at least 1."))

    if num_guests > property.max_guests:
        raise BookingError(
            _(
                "Number of guests (%(requested)s) exceeds the property's "
                "maximum capacity (%(max)s)."
            )
            % {"requested": num_guests, "max": property.max_guests}
        )

    valid_payment_methods = {choice[0] for choice in Booking.PAYMENT_METHOD_CHOICES}

    if payment_method not in valid_payment_methods:
        raise BookingError(
            _("Invalid payment method. Valid options: %(options)s.")
            % {"options": ", ".join(sorted(valid_payment_methods))}
        )

    overlapping_qs = Booking.objects.filter(
        property=property,
        status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED],
        check_in__lt=check_out,
        check_out__gt=check_in,
    )

    if overlapping_qs.exists():
        raise BookingError(_("The selected dates are not available for this property."))

    nights: int = (check_out - check_in).days
    total_price: Decimal = Decimal(nights) * property.price_per_night

    try:
        booking = Booking(
            property=property,
            guest=guest,
            check_in=check_in,
            check_out=check_out,
            num_guests=num_guests,
            total_price=total_price,
            payment_method=payment_method,
            status=Booking.STATUS_PENDING,
        )

        booking.full_clean()

        booking.save()

    except ValidationError as exc:
        if hasattr(exc, "message_dict"):
            flat = "; ".join(
                f"{field}: {', '.join(msgs)}"
                for field, msgs in exc.message_dict.items()
            )

        else:
            flat = " ".join(str(m) for m in exc.messages)

        raise BookingError(flat) from exc

    return booking
