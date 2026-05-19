"""
Forms for the bookings app.

Provides the booking creation form used on the property detail page,
and the payment form used on the payment page.
"""

import datetime

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Booking


class BookingForm(forms.Form):
    """
    Booking request form shown on the property detail page.

    Validates date coherence and guest count before the service layer
    performs the full availability check.
    """
    check_in = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control", "id": "id_check_in"},
        ),
        label=_("Check-in"),
        input_formats=["%Y-%m-%d"],
    )
    check_out = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control", "id": "id_check_out"},
        ),
        label=_("Check-out"),
        input_formats=["%Y-%m-%d"],
    )
    num_guests = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "1", "id": "id_num_guests"},
        ),
        label=_("Guests"),
    )

    def clean(self):
        """Validate that check-in is before check-out and not in the past."""
        cleaned = super().clean()

        check_in = cleaned.get("check_in")
        check_out = cleaned.get("check_out")

        if check_in and check_out:
            if check_in < datetime.date.today():
                self.add_error("check_in", _("Check-in date cannot be in the past."))

            if check_in >= check_out:
                self.add_error("check_out", _("Check-out must be after check-in."))

        return cleaned


class PaymentForm(forms.Form):
    """
    Payment method selection form.

    Simulates payment collection — no real payment gateway integration.
    """
    CARD = Booking.PAYMENT_CARD
    APPLE = Booking.PAYMENT_APPLE_PAY
    GPAY = Booking.PAYMENT_GOOGLE_PAY

    payment_method = forms.ChoiceField(
        choices=Booking.PAYMENT_METHOD_CHOICES,
        initial=CARD,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label=_("Payment method"),
    )
    card_number = forms.CharField(
        max_length=19,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "1234 5678 9012 3456",
                "class": "form-control",
                "autocomplete": "cc-number",
            }
        ),
        label=_("Card number"),
    )
    card_expiry = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "MM/YY",
                "class": "form-control",
                "autocomplete": "cc-exp",
            }
        ),
        label=_("Expiry date"),
    )
    card_cvv = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "CVV",
                "class": "form-control",
                "autocomplete": "cc-csc",
            }
        ),
        label=_("CVV"),
    )
    card_holder = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Name on card"),
                "class": "form-control",
                "autocomplete": "cc-name",
            }
        ),
        label=_("Cardholder name"),
    )

    def clean(self):
        """Require card fields when credit card is selected."""

        cleaned = super().clean()

        method = cleaned.get("payment_method")

        if method == self.CARD:
            for field in ("card_number", "card_expiry", "card_cvv", "card_holder"):
                if not cleaned.get(field):
                    self.add_error(
                        field, _("This field is required for card payments.")
                    )

        return cleaned
