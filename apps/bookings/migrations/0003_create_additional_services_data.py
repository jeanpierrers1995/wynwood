"""
Data migration to add default additional services.

Run this after running the main migrations:
  python manage.py migrate
  python manage.py loaddata additional_services
"""

from django.db import migrations
from decimal import Decimal


def create_additional_services(apps, schema_editor):
    """Create default additional services for bookings."""
    AdditionalService = apps.get_model('bookings', 'AdditionalService')
    
    services = [
        {
            'name': 'Check-in & Check-out flexible',
            'description': 'Horario flexible de entrada y salida según tu conveniencia',
            'price': Decimal('15.00'),
            'is_active': True,
            'order': 1,
        },
        {
            'name': 'Servicio de transporte',
            'description': 'Transporte desde/hacia el aeropuerto o ubicación que prefieras',
            'price': Decimal('35.00'),
            'is_active': True,
            'order': 2,
        },
        {
            'name': 'Llena tu nevera',
            'description': 'Surtimos tu nevera con alimentos y bebidas básicas antes de tu llegada',
            'price': Decimal('25.00'),
            'is_active': True,
            'order': 3,
        },
        {
            'name': 'Cuna para bebé',
            'description': 'Cuna cómoda y segura para bebés hasta 2 años',
            'price': Decimal('10.00'),
            'is_active': True,
            'order': 4,
        },
    ]
    
    for service_data in services:
        AdditionalService.objects.get_or_create(
            name=service_data['name'],
            defaults=service_data
        )


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_additionalservice_booking_discount_code_and_more'),
    ]

    operations = [
        migrations.RunPython(create_additional_services, migrations.RunPython.noop),
    ]
