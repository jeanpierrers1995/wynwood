import os

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

MAX_IMAGE_WIDTH = 1200

WEBP_QUALITY = 85


class Destination(models.Model):
    """
    A tourist destination (country/city) associated with properties.

    The slug is auto-generated from the name on the first save.
    """
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    image = models.ImageField(
        upload_to="destinations/",
        verbose_name=_("Image"),
    )
    country = models.CharField(max_length=100, verbose_name=_("Country"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Destination")
        verbose_name_plural = _("Destinations")

    def save(self, *args, **kwargs) -> None:
        """Auto-generate slug from name if not already set."""
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Amenity(models.Model):
    """
    An amenity or feature that a property may offer.

    Declared before Property so it can be referenced directly
    in the ManyToMany relationship.
    """
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    icon_class = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Bootstrap icon class (e.g. bi-wifi)"),
        verbose_name=_("Icon class"),
    )

    class Meta:
        verbose_name = _("Amenity")
        verbose_name_plural = _("Amenities")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class PropertyManager(models.Manager):
    """Custom manager with expressive querysets for filtering properties."""

    def available(
        self,
        city: str | None = None,
        check_in=None,
        check_out=None,
        guests: int | None = None,
    ) -> models.QuerySet:
        """
        Return active properties filtered by city, date range and guest count.

        Automatically excludes properties that have overlapping confirmed
        or pending bookings within the requested date range.

        Args:
            city: Case-insensitive destination name filter.
            check_in: Start date of the stay.
            check_out: End date of the stay.
            guests: Minimum guest capacity required.

        Returns:
            A QuerySet of matching Property instances.
        """
        qs = self.filter(is_active=True)

        if city:
            qs = qs.filter(destination__name__icontains=city)

        if guests:
            qs = qs.filter(max_guests__gte=guests)

        if check_in and check_out:
            from apps.bookings.models import Booking

            booked_ids = Booking.objects.filter(
                status__in=["pending", "confirmed"],
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).values_list("property_id", flat=True)

            qs = qs.exclude(id__in=booked_ids)

        return qs

    def featured(self) -> models.QuerySet:
        """Return active properties marked as featured."""
        return self.filter(is_active=True, is_featured=True)


class Property(models.Model):
    """
    A rental property available for booking on the Wynwood House platform.

    Manages location metadata, pricing, capacity, category and relationships
    with destinations and amenities.
    """
    CATEGORY_CHOICES = [
        ("all", _("All properties")),
        ("collection", _("The Collection*")),
        ("casa_wynwood", _("Casa Wynwood")),
    ]

    name = models.CharField(max_length=200, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    description = models.TextField(verbose_name=_("Description"))
    destination = models.ForeignKey(
        Destination,
        on_delete=models.PROTECT,
        related_name="properties",
        verbose_name=_("Destination"),
    )
    address = models.CharField(max_length=300, verbose_name=_("Address"))
    district = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("District / Neighbourhood"),
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_("Latitude"),
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_("Longitude"),
    )
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Price per night"),
    )
    max_guests = models.PositiveIntegerField(verbose_name=_("Max guests"))
    bedrooms = models.PositiveIntegerField(verbose_name=_("Bedrooms"))
    bathrooms = models.PositiveIntegerField(verbose_name=_("Bathrooms"))
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="all",
        verbose_name=_("Category"),
    )
    amenities = models.ManyToManyField(
        Amenity,
        blank=True,
        verbose_name=_("Amenities"),
    )
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    objects = PropertyManager()

    class Meta:
        ordering = ["-is_featured", "name"]
        verbose_name = _("Property")
        verbose_name_plural = _("Properties")

    def save(self, *args, **kwargs) -> None:
        """Auto-generate slug from name if not already set."""
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def get_primary_image(self) -> "PropertyImage | None":
        """Return the primary image or the first available one."""
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def city(self) -> str:
        """Return the destination city/name for display purposes."""
        return self.destination.name if self.destination_id else ""


class PropertyImage(models.Model):
    """
    An image associated with a property.

    On save, the image is automatically optimised: resized to at most
    MAX_IMAGE_WIDTH pixels wide and converted to WebP at WEBP_QUALITY.
    """
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Property"),
    )
    image = models.ImageField(
        upload_to="properties/",
        verbose_name=_("Image"),
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Alt text"),
    )
    is_primary = models.BooleanField(default=False, verbose_name=_("Primary"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))

    class Meta:
        ordering = ["order"]
        verbose_name = _("Property image")
        verbose_name_plural = _("Property images")

    def save(self, *args, **kwargs) -> None:
        """
        Save the image and optimise it to WebP, resizing if wider than MAX_IMAGE_WIDTH.

        Conversion is done with Pillow. If it fails for any reason, the original
        file is preserved without raising an exception.
        """
        super().save(*args, **kwargs)

        if self.image:
            try:
                from PIL import Image as PILImage

                img_path = self.image.path

                with PILImage.open(img_path) as img:
                    if img.width > MAX_IMAGE_WIDTH:
                        ratio = MAX_IMAGE_WIDTH / img.width
                        new_size = (MAX_IMAGE_WIDTH, int(img.height * ratio))
                        img = img.resize(new_size, PILImage.LANCZOS)

                    webp_path = os.path.splitext(img_path)[0] + ".webp"
                    img.save(webp_path, "WEBP", quality=WEBP_QUALITY)

                if img_path != webp_path and os.path.exists(img_path):
                    os.remove(img_path)

                relative_path = os.path.relpath(
                    webp_path,
                    start=str(self.image.storage.location),
                )

                PropertyImage.objects.filter(pk=self.pk).update(image=relative_path)

            except Exception:
                pass

    def __str__(self) -> str:

        return f"{self.property.name} — image {self.order}"
