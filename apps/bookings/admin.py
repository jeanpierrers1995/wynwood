"""
Django Admin configuration for the bookings app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for property bookings."""
    list_display = (
        "id",
        "property",
        "guest",
        "check_in",
        "check_out",
        "num_guests",
        "total_price",
        "status",
        "payment_method",
        "created_at",
    )
    list_filter = ("status", "payment_method", "created_at")
    search_fields = (
        "property__name",
        "guest__email",
        "guest__first_name",
        "guest__last_name",
    )
    date_hierarchy = "created_at"
    readonly_fields = ("total_price", "created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (
            None,
            {"fields": ("property", "guest", "status", "payment_method")},
        ),
        (
            _("Dates & Guests"),
            {"fields": ("check_in", "check_out", "num_guests")},
        ),
        (
            _("Pricing"),
            {"fields": ("total_price",)},
        ),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
