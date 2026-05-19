"""
Forms for the bookings app.

Provides the booking creation form used on the property detail page,
and the payment form used on the payment page.
"""

import datetime

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Booking, AdditionalService


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
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Email address"),
                "id": "id_email",
            }
        ),
        label=_("Email"),
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+57 3001234567",
                "id": "id_phone",
            }
        ),
        label=_("Phone"),
    )
    discount_code = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Discount code"),
                "id": "id_discount_code",
            }
        ),
        label=_("Discount code"),
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

    additional_services = forms.ModelMultipleChoiceField(
        queryset=AdditionalService.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

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
                "placeholder": "4111 1111 1111 1111",
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
                "placeholder": "12/25",
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
                "placeholder": "123",
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
                "placeholder": _("Jean Pierre Rivas"),
                "class": "form-control",
                "autocomplete": "cc-name",
            }
        ),
        label=_("Cardholder name"),
    )
    installments = forms.ChoiceField(
        choices=[("1", _("1 installment")), ("3", _("3 installments")), ("6", _("6 installments"))],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label=_("Select number of installments"),
    )
    address1 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Enter your address"), "class": "form-control"}),
        label=_("Address")
    )
    address2 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Enter your address"), "class": "form-control"}),
        label=_("Address 2 (optional)")
    )
    country = forms.ChoiceField(
        choices=[
            ("", _("Select your country")),
            ("PE", _("Peru")),
            ("CO", _("Colombia")),
            ("US", _("United States")),
            ("MX", _("Mexico"))
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label=_("Country")
    )
    state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Enter your state"), "class": "form-control"}),
        label=_("State/Region")
    )
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Enter city name"), "class": "form-control"}),
        label=_("City")
    )
    zip_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "00000", "class": "form-control"}),
        label=_("Postal Code")
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
