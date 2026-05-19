from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Amenity, Destination, Property, PropertyImage


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    """Admin interface for tourist destinations."""

    list_display = ("name", "country", "order", "is_active", "preview_image")
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "country")
    search_fields = ("name", "country")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")

    @admin.display(description=_("Preview"))
    def preview_image(self, obj):
        """Render a small thumbnail of the destination image."""
        if obj.image:
            return format_html(
                '<img src="{}" height="40" style="border-radius:4px"/>', obj.image.url
            )

        return "—"


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    """Admin interface for property amenities."""

    list_display = ("name", "icon_class")
    search_fields = ("name",)
    ordering = ("name",)


class PropertyImageInline(admin.TabularInline):
    """Inline editor for property images within the Property admin."""

    model = PropertyImage
    extra = 1
    fields = ("image", "alt_text", "is_primary", "order")
    ordering = ("order",)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Admin interface for rental properties."""

    list_display = (
        "name",
        "destination",
        "category",
        "price_per_night",
        "max_guests",
        "bedrooms",
        "is_featured",
        "is_active",
    )
    list_editable = ("is_featured", "is_active", "price_per_night")
    list_filter = ("is_active", "is_featured", "category", "destination")
    search_fields = ("name", "address", "destination__name")
    filter_horizontal = ("amenities",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PropertyImageInline]
    ordering = ("-is_featured", "name")

    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "destination", "category")}),
        (
            _("Location"),
            {"fields": ("address", "district", "latitude", "longitude")},
        ),
        (
            _("Capacity & Pricing"),
            {
                "fields": (
                    "price_per_night",
                    "max_guests",
                    "bedrooms",
                    "bathrooms",
                    "amenities",
                )
            },
        ),
        (
            _("Status"),
            {"fields": ("is_featured", "is_active")},
        ),
    )
