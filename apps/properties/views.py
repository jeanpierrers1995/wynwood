import datetime

from django.views.generic import DetailView, ListView, TemplateView

from .models import Destination, Property


class HomeView(TemplateView):
    """
    Home page view.

    Renders the hero section, destination carousel, featured properties and promotional sections.
    """

    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        """Inject featured properties and active destinations into the template context."""
        context = super().get_context_data(**kwargs)

        context["featured_properties"] = (
            Property.objects.featured()
            .select_related("destination")
            .prefetch_related("images")[:12]
        )

        context["destinations"] = Destination.objects.filter(is_active=True).order_by(
            "order"
        )

        context["categories"] = Property.CATEGORY_CHOICES

        return context


class SearchResultsView(ListView):
    """
    Property search results page.

    Filters properties by city, date range and guest count based on
    query parameters submitted by the home-page search bar.
    """

    model = Property
    template_name = "pages/search_results.html"
    context_object_name = "properties"
    paginate_by = 12

    def get_queryset(self):
        """Build the filtered queryset from GET parameters."""
        params = self.request.GET

        city = params.get("city", "").strip()
        guests_raw = params.get("guests", "").strip()
        check_in_raw = params.get("check_in", "").strip()
        check_out_raw = params.get("check_out", "").strip()

        guests = int(guests_raw) if guests_raw.isdigit() else None

        check_in = _parse_date(check_in_raw)
        check_out = _parse_date(check_out_raw)

        return (
            Property.objects.available(
                city=city or None,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
            )
            .select_related("destination")
            .prefetch_related("images")
        )

    def get_context_data(self, **kwargs):
        """Pass search parameters back to the template for form pre-fill."""
        context = super().get_context_data(**kwargs)

        params = self.request.GET

        context["search_city"] = params.get("city", "")
        context["search_guests"] = params.get("guests", "")
        context["search_check_in"] = params.get("check_in", "")
        context["search_check_out"] = params.get("check_out", "")

        context["destinations"] = Destination.objects.filter(is_active=True)

        context["total_count"] = self.get_queryset().count()

        return context


class PropertyDetailView(DetailView):
    """
    Individual property detail page.

    Displays the property gallery, description, amenities, location
    and the inline booking form.
    """

    model = Property
    template_name = "pages/property_detail.html"
    context_object_name = "property"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Only expose active properties."""
        return (
            Property.objects.filter(is_active=True)
            .select_related("destination")
            .prefetch_related("images", "amenities")
        )

    def get_context_data(self, **kwargs):
        """Inject booking form and booked-dates data."""
        context = super().get_context_data(**kwargs)

        from apps.bookings.forms import BookingForm

        context["form"] = BookingForm(
            initial={
                "check_in": self.request.GET.get("check_in", ""),
                "check_out": self.request.GET.get("check_out", ""),
                "num_guests": self.request.GET.get("guests", ""),
            }
        )

        booked_ranges = list(
            self.object.bookings.filter(
                status__in=["pending", "confirmed"],
                check_out__gte=datetime.date.today(),
            ).values("check_in", "check_out")
        )

        context["booked_ranges"] = booked_ranges

        return context


def _parse_date(value: str) -> datetime.date | None:
    """Parse a YYYY-MM-DD string into a date object, returning None on failure."""

    try:
        return datetime.date.fromisoformat(value)

    except (ValueError, TypeError):
        return None
