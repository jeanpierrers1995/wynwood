from decimal import Decimal, ROUND_HALF_UP
from django import template

register = template.Library()


@register.filter
def calculate_subtotal(booking, additional_services=None):
    """
    Calculate subtotal including base price, cleaning fee, and optional additional services.

    Args:
        booking: Booking object
        additional_services: List of AdditionalService objects (optional)

    Returns:
        Decimal: Subtotal amount
    """
    nights = booking.nights if hasattr(booking, 'nights') else (
        (booking.check_out - booking.check_in).days
    )
    price_per_night = Decimal(str(booking.property.price_per_night))
    base_price = price_per_night * nights
    cleaning_fee = Decimal('20.00')

    subtotal = base_price + cleaning_fee

    if additional_services:
        for service in additional_services:
            subtotal += Decimal(str(service.price))

    return subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


@register.filter
def calculate_vat(amount):
    """Calculate VAT at 16%."""
    amount = Decimal(str(amount))
    vat = (amount * Decimal('0.16')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return vat


@register.filter
def calculate_city_tax(amount):
    """Calculate city tax at 3%."""
    amount = Decimal(str(amount))
    city_tax = (amount * Decimal('0.03')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return city_tax


@register.filter
def calculate_total(subtotal, additional_cost=None):
    """
    Calculate final total including taxes.

    Args:
        subtotal: Base subtotal (Decimal or number)
        additional_cost: Optional additional costs dict with 'vat' and 'city_tax' keys

    Returns:
        Decimal: Final total
    """
    subtotal = Decimal(str(subtotal))

    if additional_cost is None or not isinstance(additional_cost, dict):
        vat = subtotal * Decimal('0.16')
        city_tax = subtotal * Decimal('0.03')
    else:
        vat = Decimal(str(additional_cost.get('vat', 0)))
        city_tax = Decimal(str(additional_cost.get('city_tax', 0)))

    total = (subtotal + vat + city_tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return total


@register.simple_tag
def booking_price_breakdown(booking, additional_services=None):
    """
    Generate complete price breakdown for a booking.

    Returns:
        Dict with all price components
    """
    nights = booking.nights if hasattr(booking, 'nights') else (
        (booking.check_out - booking.check_in).days
    )
    price_per_night = Decimal(str(booking.property.price_per_night))
    base_price = price_per_night * nights
    cleaning_fee = Decimal('20.00')

    services_total = Decimal('0.00')
    if additional_services:
        services_total = sum(
            Decimal(str(svc.price)) for svc in additional_services
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    subtotal = (base_price + cleaning_fee + services_total).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    vat = (subtotal * Decimal('0.16')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    city_tax = (subtotal * Decimal('0.03')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = (subtotal + vat + city_tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    wynwood_points = int(float(total) * 0.5)

    return {
        'nights': nights,
        'price_per_night': price_per_night,
        'base_price': base_price,
        'cleaning_fee': cleaning_fee,
        'services_total': services_total,
        'subtotal': subtotal,
        'vat': vat,
        'city_tax': city_tax,
        'total': total,
        'wynwood_points': wynwood_points,
    }

