"""
Views for the bookings app.

Covers the full booking flow: checkout (booking creation),
payment simulation, confirmation and booking list.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView

from apps.properties.models import Property

from .forms import BookingForm, PaymentForm
from .models import Booking, AdditionalService
from .services import BookingError, create_booking


class CheckoutView(FormView):
    """
    Booking checkout view — step 1 of the booking flow.

    Displays a registration/login prompt for unauthenticated users,
    and a booking summary with the payment CTA for authenticated ones.
    The actual booking is created here and placed in PENDING status.
    """
    template_name = "pages/checkout.html"
    form_class = BookingForm

    def setup(self, request, *args, **kwargs):
        """Load the property from the URL slug before processing the form."""
        super().setup(request, *args, **kwargs)
        self.property = get_object_or_404(Property, slug=kwargs["slug"], is_active=True)

    def get_initial(self):
        """Pre-fill form fields from the search query string."""
        params = self.request.GET
        return {
            "check_in": params.get("check_in", ""),
            "check_out": params.get("check_out", ""),
            "num_guests": params.get("guests", ""),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["property"] = self.property

        from apps.accounts.forms import RegisterForm

        context["register_form"] = RegisterForm()
        return context

    def dispatch(self, request, *args, **kwargs):
        """Redirect unauthenticated users to the register page with next param."""
        if not request.user.is_authenticated:
            register_url = reverse("accounts:register")
            current_url = request.get_full_path()
            return redirect(f"{register_url}?next={current_url}")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Create a pending booking and redirect to the payment step."""
        data = form.cleaned_data

        try:
            booking = create_booking(
                property=self.property,
                guest=self.request.user,
                check_in=data["check_in"],
                check_out=data["check_out"],
                num_guests=data["num_guests"],
            )

        except BookingError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)

        return redirect(reverse("bookings:payment", kwargs={"booking_id": booking.pk}))

    def form_invalid(self, form):
        messages.error(
            self.request, _("Please correct the errors in the booking form.")
        )
        return super().form_invalid(form)


class PaymentView(LoginRequiredMixin, FormView):
    """
    Payment view — step 2 of the booking flow.

    Displays the payment form. On successful submission the booking
    status is updated to CONFIRMED, triggering the email signal.
    """
    template_name = "pages/payment.html"
    form_class = PaymentForm

    def setup(self, request, *args, **kwargs):
        """Load the booking and verify it belongs to the current user."""
        super().setup(request, *args, **kwargs)
        self.booking = get_object_or_404(
            Booking,
            pk=kwargs["booking_id"],
            guest=request.user,
            status=Booking.STATUS_PENDING,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["booking"] = self.booking
        context["available_services"] = AdditionalService.objects.filter(is_active=True).order_by("order")
        return context

    def form_valid(self, form):
        """Confirm the booking and redirect to the confirmation page."""
        from decimal import Decimal, ROUND_HALF_UP

        payment_method = form.cleaned_data["payment_method"]
        additional_services = form.cleaned_data.get("additional_services", [])

        Booking.objects.filter(pk=self.booking.pk).update(
            status=Booking.STATUS_CONFIRMED,
            payment_method=payment_method,
        )

        confirmed_booking = Booking.objects.get(pk=self.booking.pk)
        
        subtotal = Decimal(str(confirmed_booking.total_price))
        
        if additional_services:
            confirmed_booking.additional_services.set(additional_services)
            services_total = sum(Decimal(str(svc.price)) for svc in additional_services)
            subtotal += services_total

        vat = (subtotal * Decimal('0.16')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        city_tax = (subtotal * Decimal('0.03')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        final_total = (subtotal + vat + city_tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        confirmed_booking.total_price = final_total
        confirmed_booking.save(update_fields=["total_price"])

        from django.db.models.signals import post_save

        post_save.send(sender=Booking, instance=confirmed_booking, created=False)

        return redirect(
            reverse("bookings:confirmation", kwargs={"booking_id": self.booking.pk})
        )

    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            if field != "__all__":
                field_label = form.fields[field].label
                field_errors = ', '.join(str(e) for e in errors)
                error_messages.append(f"{field_label}: {field_errors}")

        if error_messages:
            for error in error_messages:
                messages.error(self.request, error)
        else:
            messages.error(self.request, _("Please check your payment details."))

        return super().form_invalid(form)


class ConfirmationView(LoginRequiredMixin, DetailView):
    """
    Booking confirmation view — step 3 (final) of the booking flow.

    Displays the confirmed booking summary to the guest.
    """
    template_name = "pages/confirmation.html"
    context_object_name = "booking"

    def get_object(self):
        """Return the confirmed booking owned by the current user."""
        return get_object_or_404(
            Booking,
            pk=self.kwargs["booking_id"],
            guest=self.request.user,
            status=Booking.STATUS_CONFIRMED,
        )


class MyBookingsView(LoginRequiredMixin, ListView):
    """
    Display all bookings belonging to the authenticated user.
    """
    template_name = "pages/my_bookings.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        """Return the user's bookings ordered by most recent first."""

        return (
            Booking.objects.filter(guest=self.request.user)
            .select_related("property", "property__destination")
            .prefetch_related("property__images")
            .order_by("-created_at")
        )
