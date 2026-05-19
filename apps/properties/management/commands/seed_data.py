"""
Management command: seed_data

Populates the database with realistic demo data for development and testing.
Safe to run multiple times — uses get_or_create to avoid duplicates.

Usage:
    uv run python manage.py seed_data
    uv run python manage.py seed_data --clear   # wipe existing data first
"""

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
import io

try:
    from PIL import Image, ImageDraw
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

User = get_user_model()

DESTINATIONS = [
    {"name": "Bogotá", "country": "Colombia", "order": 1},
    {"name": "Medellín", "country": "Colombia", "order": 2},
    {"name": "Ciudad de México", "country": "México", "order": 3},
    {"name": "Lima", "country": "Perú", "order": 4},
    {"name": "Ciudad de Panamá", "country": "Panamá", "order": 5},
    {"name": "Madrid", "country": "España", "order": 6},
]

AMENITIES = [
    {"name": "WiFi", "icon_class": "bi-wifi"},
    {"name": "Pool", "icon_class": "bi-droplet"},
    {"name": "Air conditioning", "icon_class": "bi-thermometer-snow"},
    {"name": "Kitchen", "icon_class": "bi-cup-hot"},
    {"name": "Parking", "icon_class": "bi-p-square"},
    {"name": "Gym", "icon_class": "bi-bicycle"},
    {"name": "Pet friendly", "icon_class": "bi-heart"},
    {"name": "Washer", "icon_class": "bi-asterisk"},
    {"name": "TV", "icon_class": "bi-tv"},
    {"name": "Workspace", "icon_class": "bi-briefcase"},
]

PROPERTIES = [
    {
        "name": "Dazzling 2BR in Condesa",
        "destination": "Bogotá",
        "address": "Calle 93 #12-34, Chicó, Bogotá",
        "district": "Chicó",
        "description": (
            "Stunning two-bedroom apartment in the heart of Bogotá's upscale Chicó neighbourhood. "
            "Floor-to-ceiling windows, designer furnishings and breathtaking city views make this "
            "the perfect base for business travellers and discerning explorers alike."
        ),
        "price_per_night": "350.00",
        "max_guests": 4,
        "bedrooms": 2,
        "bathrooms": 2,
        "category": "collection",
        "is_featured": True,
        "amenities": ["WiFi", "Air conditioning", "Kitchen", "Workspace", "TV"],
        "latitude": "4.676540",
        "longitude": "-74.048270",
    },
    {
        "name": "Palermo Penthouse Suite",
        "destination": "Bogotá",
        "address": "Carrera 11 #82-71, Zona Rosa, Bogotá",
        "district": "Zona Rosa",
        "description": (
            "Rooftop penthouse with a private terrace overlooking the Andes. "
            "Sleek mid-century modern interiors, a fully equipped gourmet kitchen "
            "and walking distance to Bogotá's best restaurants and nightlife."
        ),
        "price_per_night": "480.00",
        "max_guests": 6,
        "bedrooms": 3,
        "bathrooms": 3,
        "category": "collection",
        "is_featured": True,
        "amenities": ["WiFi", "Pool", "Air conditioning", "Kitchen", "Gym", "Parking"],
        "latitude": "4.667240",
        "longitude": "-74.053980",
    },
    {
        "name": "Casa Wynwood Laureles",
        "destination": "Medellín",
        "address": "Circular 73 #39-15, Laureles, Medellín",
        "district": "Laureles",
        "description": (
            "A beautifully restored colonial casa in Laureles, Medellín's most charming "
            "residential neighbourhood. Private courtyard with fountain, original tile floors "
            "and curated local art throughout."
        ),
        "price_per_night": "290.00",
        "max_guests": 8,
        "bedrooms": 4,
        "bathrooms": 3,
        "category": "casa_wynwood",
        "is_featured": True,
        "amenities": ["WiFi", "Pool", "Kitchen", "Pet friendly", "Parking", "Washer"],
        "latitude": "6.244440",
        "longitude": "-75.590390",
    },
    {
        "name": "El Poblado Studio Loft",
        "destination": "Medellín",
        "address": "Calle 10 #32-18, El Poblado, Medellín",
        "district": "El Poblado",
        "description": (
            "Chic studio loft in El Poblado, steps from Parque El Poblado and the "
            "city's best cafés and restaurants. Industrial-style interiors with warm "
            "wood accents and a private balcony."
        ),
        "price_per_night": "175.00",
        "max_guests": 2,
        "bedrooms": 1,
        "bathrooms": 1,
        "category": "all",
        "is_featured": False,
        "amenities": ["WiFi", "Air conditioning", "TV", "Workspace"],
        "latitude": "6.208510",
        "longitude": "-75.568730",
    },
    {
        "name": "Polanco Residence",
        "destination": "Ciudad de México",
        "address": "Av. Presidente Masaryk 111, Polanco, CDMX",
        "district": "Polanco",
        "description": (
            "Sophisticated apartment in the prestigious Polanco district, "
            "Mexico City's answer to the Upper East Side. "
            "Surrounded by world-class dining, luxury boutiques and Chapultepec Park."
        ),
        "price_per_night": "320.00",
        "max_guests": 4,
        "bedrooms": 2,
        "bathrooms": 2,
        "category": "collection",
        "is_featured": True,
        "amenities": ["WiFi", "Air conditioning", "Kitchen", "Gym", "Workspace", "TV"],
        "latitude": "19.432610",
        "longitude": "-99.196840",
    },
    {
        "name": "Roma Norte Garden Flat",
        "destination": "Ciudad de México",
        "address": "Orizaba 101, Roma Norte, CDMX",
        "district": "Roma Norte",
        "description": (
            "Bright garden-level flat in vibrant Roma Norte. "
            "Private garden patio, exposed brick, and direct access to the neighbourhood's "
            "famous brunch spots, galleries and tree-lined boulevards."
        ),
        "price_per_night": "210.00",
        "max_guests": 3,
        "bedrooms": 1,
        "bathrooms": 1,
        "category": "all",
        "is_featured": False,
        "amenities": ["WiFi", "Kitchen", "Pet friendly", "Washer"],
        "latitude": "19.419340",
        "longitude": "-99.162550",
    },
    {
        "name": "Miraflores Ocean View",
        "destination": "Lima",
        "address": "Malecón de la Reserva 610, Miraflores, Lima",
        "district": "Miraflores",
        "description": (
            "Contemporary apartment perched on the Lima cliffs with unobstructed "
            "Pacific Ocean views. Watch paragliders soar from your living room window "
            "while enjoying gourmet Peruvian cuisine from the building's restaurant."
        ),
        "price_per_night": "260.00",
        "max_guests": 4,
        "bedrooms": 2,
        "bathrooms": 2,
        "category": "collection",
        "is_featured": True,
        "amenities": ["WiFi", "Pool", "Air conditioning", "Gym", "TV"],
        "latitude": "-12.130880",
        "longitude": "-77.028440",
    },
    {
        "name": "Casco Viejo Heritage Loft",
        "destination": "Ciudad de Panamá",
        "address": "Calle 1era Oeste 8-27, Casco Viejo, Panama City",
        "district": "Casco Viejo",
        "description": (
            "Lovingly restored loft in a 19th-century building in UNESCO-listed Casco Viejo. "
            "Original ornate balconies, high ceilings and just steps from Panama Bay. "
            "The perfect blend of colonial history and contemporary comfort."
        ),
        "price_per_night": "195.00",
        "max_guests": 2,
        "bedrooms": 1,
        "bathrooms": 1,
        "category": "collection",
        "is_featured": False,
        "amenities": ["WiFi", "Air conditioning", "TV", "Workspace"],
        "latitude": "8.952290",
        "longitude": "-79.535190",
    },
    {
        "name": "Malasaña Artist Apartment",
        "destination": "Madrid",
        "address": "Calle del Pez 21, Malasaña, Madrid",
        "district": "Malasaña",
        "description": (
            "Eclectic two-bedroom apartment in the heart of Madrid's creative Malasaña "
            "district. Original artwork, vintage furniture and a rooftop terrace with "
            "Gran Vía views. Madrid's best tapas bars and flamenco venues at your doorstep."
        ),
        "price_per_night": "230.00",
        "max_guests": 4,
        "bedrooms": 2,
        "bathrooms": 1,
        "category": "all",
        "is_featured": False,
        "amenities": ["WiFi", "Kitchen", "Washer", "TV"],
        "latitude": "40.422050",
        "longitude": "-3.704280",
    },
    {
        "name": "Salamanca Luxury Suite",
        "destination": "Madrid",
        "address": "Calle de Serrano 41, Salamanca, Madrid",
        "district": "Salamanca",
        "description": (
            "Opulent suite in Madrid's golden mile. Surrounded by flagship luxury boutiques, "
            "Michelin-starred restaurants and the Prado Museum. "
            "White-glove concierge service included."
        ),
        "price_per_night": "550.00",
        "max_guests": 2,
        "bedrooms": 1,
        "bathrooms": 1,
        "category": "collection",
        "is_featured": True,
        "amenities": ["WiFi", "Air conditioning", "Gym", "Workspace", "TV"],
        "latitude": "40.425680",
        "longitude": "-3.688230",
    },
]

DEMO_USERS = [
    {
        "email": "guest@wynwoodhouse.com",
        "first_name": "Alex",
        "last_name": "Traveller",
        "phone": "+1 555 000 1234",
        "country": "United States",
        "password": "password123",
    },
    {
        "email": "admin@wynwoodhouse.com",
        "first_name": "Admin",
        "last_name": "Wynwood",
        "phone": "+57 300 000 0000",
        "country": "Colombia",
        "password": "admin123!",
        "is_staff": True,
        "is_superuser": True,
    },
]


class Command(BaseCommand):
    """Populate the database with realistic demo data."""

    help = "Seed the database with destinations, amenities, properties and demo users."

    def add_arguments(self, parser):

        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing properties, destinations and amenities before seeding.",
        )

    def handle(self, *args, **options):

        from apps.properties.models import Amenity, Destination, Property, PropertyImage

        from apps.bookings.models import Booking

        if options["clear"]:
            self.stdout.write("Clearing existing data...")

            Booking.objects.all().delete()
            Property.objects.all().delete()

            Destination.objects.all().delete()

            Amenity.objects.all().delete()

            self.stdout.write(self.style.WARNING("Existing data cleared."))

        self.stdout.write("Creating amenities...")

        amenity_map: dict[str, Amenity] = {}

        for data in AMENITIES:
            obj, created = Amenity.objects.get_or_create(
                name=data["name"],
                defaults={"icon_class": data["icon_class"]},
            )

            amenity_map[obj.name] = obj

            if created:
                self.stdout.write(f"  + Amenity: {obj.name}")

        self.stdout.write("Creating destinations...")

        destination_map: dict[str, Destination] = {}

        for data in DESTINATIONS:
            slug = slugify(data["name"])

            obj, created = Destination.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": data["name"],
                    "country": data["country"],
                    "order": data["order"],
                    "is_active": True,
                },
            )

            if created and HAS_PILLOW:
                try:
                    import urllib.request
                    url = f"https://picsum.photos/seed/{obj.slug}-dest/800/800"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        img_data = response.read()
                    obj.image.save(f"{obj.slug}-dest.jpg", ContentFile(img_data), save=True)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"    ! Could not download destination image: {e}"))

            destination_map[data["name"]] = obj

            if created:
                self.stdout.write(f"  + Destination: {obj.name}, {obj.country}")

        self.stdout.write("Creating properties...")

        for data in PROPERTIES:
            destination = destination_map.get(data["destination"])

            if not destination:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ! Destination '{data['destination']}' not found, skipping."
                    )
                )

                continue

            slug = slugify(data["name"])

            prop, created = Property.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "destination": destination,
                    "address": data["address"],
                    "district": data.get("district", ""),
                    "price_per_night": data["price_per_night"],
                    "max_guests": data["max_guests"],
                    "bedrooms": data["bedrooms"],
                    "bathrooms": data["bathrooms"],
                    "category": data["category"],
                    "is_featured": data.get("is_featured", False),
                    "is_active": True,
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                },
            )

            if created:
                for amenity_name in data.get("amenities", []):
                    amenity = amenity_map.get(amenity_name)

                    if amenity:
                        prop.amenities.add(amenity)

                # Try to download a real random image, fallback to solid color if no internet
                if HAS_PILLOW:
                    try:
                        import urllib.request
                        # Use a seed to get consistent but distinct images per property
                        url = f"https://picsum.photos/seed/{prop.slug}/1200/800"
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=5) as response:
                            img_data = response.read()
                            
                        prop_img = PropertyImage(property=prop, is_primary=True)
                        prop_img.image.save(f"{prop.slug}-cover.jpg", ContentFile(img_data), save=False)
                        prop_img.save()
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"    ! Could not download image: {e}. Using solid color."))
                        img = Image.new('RGB', (1600, 1067), color=(44, 44, 44))
                        draw = ImageDraw.Draw(img)
                        draw.text((100, 100), data["name"], fill=(200, 154, 46))
                        
                        buffer = io.BytesIO()
                        img.save(buffer, format='JPEG')
                        
                        prop_img = PropertyImage(property=prop, is_primary=True)
                        prop_img.image.save(f"{prop.slug}-cover.jpg", ContentFile(buffer.getvalue()), save=False)
                        prop_img.save()

                self.stdout.write(f"  + Property: {prop.name} ({destination.name})")

        self.stdout.write("Creating demo users...")

        for data in DEMO_USERS:
            if not User.objects.filter(email=data["email"]).exists():
                user = User(
                    email=data["email"],
                    username=data["email"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    phone=data.get("phone", ""),
                    country=data.get("country", ""),
                    is_staff=data.get("is_staff", False),
                    is_superuser=data.get("is_superuser", False),
                )

                user.set_password(data["password"])

                user.save()

                self.stdout.write(
                    f"  + User: {user.email} (password: {data['password']})"
                )

            else:
                self.stdout.write(f"  = User already exists: {data['email']}")

        self.stdout.write(self.style.SUCCESS("\n✅ Seed data loaded successfully!"))

        self.stdout.write("")

        self.stdout.write("Demo credentials:")

        self.stdout.write("  Guest  → guest@wynwoodhouse.com  / password123")

        self.stdout.write("  Admin  → admin@wynwoodhouse.com  / admin123!")

        self.stdout.write("  Admin panel → http://127.0.0.1:8000/admin/")
