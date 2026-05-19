# Wynwood House

**Home experience. Hotel quality.**

A full-stack property reservation platform built with Django. Users can browse destinations, search for available properties by city, dates and guest count, and complete a booking from checkout through payment confirmation.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Quick Start (Docker — Recommended)](#quick-start-docker--recommended)
- [Manual Setup with uv](#manual-setup-with-uv)
- [Environment Variables](#environment-variables)
- [Database Options](#database-options)
- [Seed Data](#seed-data)
- [Development Tools](#development-tools)
- [Internationalization](#internationalization)
- [Booking Flow](#booking-flow)
- [Deployment](#deployment)

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.12 |
| **Framework** | Django 6.x |
| **Package Manager** | [uv](https://docs.astral.sh/uv/) |
| **Database** | PostgreSQL 16 (Docker, port 5433) / SQLite (fallback) |
| **Fonts** | Acumin Pro ExtraCondensed Bold + Helvetica Neue LT Std |
| **Images** | Pillow — auto-converts uploads to WebP ≤ 1200 px |
| **Email** | Django `send_mail` — console backend in development |
| **i18n** | Django i18n (`gettext`) — Spanish (default) + English |
| **Static files** | WhiteNoise |
| **Dev tools** | Django Debug Toolbar + django-extensions |
| **Linting** | Ruff |

---

## Quick Start (Docker — Recommended)

This is the fastest way to get a fully working environment with PostgreSQL on port **5433**.

The `docker-compose.yml` runs **only the database** — Django runs locally via `uv`.
This avoids build complexity in development while still providing an isolated, reproducible PostgreSQL instance.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- [uv](https://docs.astral.sh/uv/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Steps

```bash
# 1. Clone the repository
git clone <repo-url> wynwood
cd wynwood

# 2. Copy environment variables (defaults work out of the box)
cp .env.example .env

# 3. Start the PostgreSQL container (port 5433)
docker compose up -d

# 4. Install Python dependencies (uv creates .venv automatically)
uv sync

# 5. Apply database migrations
uv run python manage.py migrate --settings=config.settings.development

# 6. Load seed data (destinations, properties, amenities, demo users)
uv run python manage.py seed_data --settings=config.settings.development

# 7. Run the development server
uv run python manage.py runserver --settings=config.settings.development
```

> **Tip:** Add this to your shell profile to avoid repeating `--settings` every time:
> ```bash
> export DJANGO_SETTINGS_MODULE=config.settings.development
> ```

Open **http://127.0.0.1:8000** in your browser.

Demo credentials (created by `seed_data`):
- **Guest:** `guest@wynwoodhouse.com` / `password123`
- **Admin:** `admin@wynwoodhouse.com` / `admin123!`
- **Admin panel:** http://127.0.0.1:8000/admin/

## Manual Setup with uv

Use this path if you prefer not to use Docker and already have PostgreSQL installed locally, or want to use SQLite.

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- PostgreSQL 16 (optional — see [Database Options](#database-options))

### Steps

```bash
# 1. Clone the repository
git clone <repo-url> wynwood
cd wynwood

# 2. Install all dependencies (uv creates .venv automatically)
uv sync

# 3. Copy environment file
cp .env.example .env
```

Edit `.env` to match your local database settings, then:

```bash
# 4. Apply migrations
uv run python manage.py migrate --settings=config.settings.development

# 5. Load demo data
uv run python manage.py seed_data --settings=config.settings.development

# 6. Create admin user
uv run python manage.py createsuperuser --settings=config.settings.development

# 7. Run the server
uv run python manage.py runserver --settings=config.settings.development
```

> **Tip:** To avoid typing `--settings=...` every time, set the environment variable:
> ```bash
> export DJANGO_SETTINGS_MODULE=config.settings.development
> uv run python manage.py runserver
> ```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```dotenv
# Django core
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database — full URL (used in production and as fallback)
DATABASE_URL=postgresql://wynwood:wynwood_dev@localhost:5433/wynwood

# PostgreSQL individual vars (used by development.py)
POSTGRES_DB=wynwood
POSTGRES_USER=wynwood
POSTGRES_PASSWORD=wynwood_dev
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

# Email (console backend for development — prints to terminal)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# EMAIL_HOST=smtp.sendgrid.net
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=apikey
# EMAIL_HOST_PASSWORD=your-sendgrid-api-key
# DEFAULT_FROM_EMAIL=Wynwood House <noreply@wynwoodhouse.com>
```

> **Never commit `.env` to version control.** It is already listed in `.gitignore`.

---

## Database Options

### Option A — PostgreSQL with Docker (default)

The `docker-compose.yml` spins up PostgreSQL 16 on **port 5433** (avoids conflicts with a local PostgreSQL instance on the standard 5432).

```bash
docker compose up -d        # start
docker compose down         # stop
docker compose down -v      # stop and delete all data
```

The `development.py` settings connect to this container automatically with the default `.env` values.

### Option B — PostgreSQL installed locally

Create the database and user:

```sql
CREATE DATABASE wynwood;
CREATE USER wynwood WITH PASSWORD 'wynwood_dev';
GRANT ALL PRIVILEGES ON DATABASE wynwood TO wynwood;
```

Update `POSTGRES_PORT=5432` (or whatever port your local instance uses) in `.env`.

### Option C — SQLite (no database server needed)

Set in `.env`:

```dotenv
DATABASE_URL=sqlite:///db.sqlite3
```

Then run migrations normally. SQLite is convenient for quick testing but is **not recommended for production**.

---

## Seed Data

Populate the database with realistic demo data:

```bash
uv run python manage.py seed_data --settings=config.settings.development
```

The command creates:

| Data | Details |
|---|---|
| **Destinations** | Colombia, México, Perú, Panamá, España |
| **Amenities** | WiFi, Pool, Air conditioning, Kitchen, Parking, Gym, Pet friendly |
| **Properties** | 10 properties across destinations (featured + collection + Casa Wynwood) |
| **Demo users** | `guest@wynwoodhouse.com` / `password123` |

To wipe and re-seed:

```bash
uv run python manage.py flush --no-input --settings=config.settings.development
uv run python manage.py seed_data --settings=config.settings.development
```

---

## Development Tools

### Django Debug Toolbar

Available at **http://127.0.0.1:8000** when `DEBUG=True`.

Shows SQL queries, cache hits, template rendering time and signal calls. Useful for catching N+1 query problems — look for `select_related` / `prefetch_related` opportunities.

### Django Extensions

Provides useful management commands:

```bash
# Interactive shell with all models auto-imported
uv run python manage.py shell_plus --settings=config.settings.development

# Print all registered URL patterns
uv run python manage.py show_urls --settings=config.settings.development

# Generate a visual model graph (requires graphviz)
uv run python manage.py graph_models -a -o models.png --settings=config.settings.development
```

### Ruff (linting & formatting)

```bash
# Check for issues
uv run ruff check .

# Auto-fix
uv run ruff check . --fix

# Format code
uv run ruff format .
```

### Translations

```bash
# Extract new translatable strings
uv run python manage.py makemessages -l en --settings=config.settings.development
uv run python manage.py makemessages -l es --settings=config.settings.development

# Compile .po files into .mo files
uv run python manage.py compilemessages --settings=config.settings.development
```

---

## Internationalization

The platform supports **Spanish** (default) and **English**.

- Language is switched via the `/i18n/setlang/` endpoint, called by the `EN / ES` toggle in the navbar.
- All user-facing strings in templates use `{% trans "..." %}` or `{% blocktrans %}`.
- All model `verbose_name` and `choices` labels use `gettext_lazy` (`_(...)`).
- Translation files live in `locale/es/` and `locale/en/`.

The default language (`LANGUAGE_CODE = "es"`) has no URL prefix. English adds `/en/` prefix (e.g. `/en/search/`).

---

## Booking Flow

```
Home page (search bar)
    ↓  city · dates · guests
Search Results  ←──── filtered by availability
    ↓
Property Detail  (gallery · amenities · inline booking form)
    ↓  check-in · check-out · guests
[Not logged in?]  → Register / Login  → back to checkout
    ↓
Checkout  (booking summary · guest details)
    ↓  booking created with status = pending
Payment  (credit card · Apple Pay · Google Pay — simulated)
    ↓  status → confirmed → email signal fires
Confirmation  (booking summary · reference number)
    + Email sent to guest (console output in development)
```

### Booking validation rules (enforced at model level)

- Check-in cannot be in the past.
- Check-out must be strictly after check-in.
- No overlapping bookings for the same property (active statuses: pending + confirmed).
- Number of guests cannot exceed `property.max_guests`.

### Image optimisation

Every image uploaded to a `PropertyImage` is automatically:
1. Resized to a maximum of **1200 px** wide (aspect ratio preserved).
2. Converted to **WebP** at 85% quality.
3. Stored in `media/properties/`.

---

## Deployment

### Collect static files

```bash
uv run python manage.py collectstatic --no-input --settings=config.settings.production
```

### Run with Gunicorn

```bash
uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### Recommended platforms

| Platform | Notes |
|---|---|
| **Railway** | `railway up` — PostgreSQL add-on available, auto-detects `Dockerfile` |
| **Render** | Free tier PostgreSQL, `gunicorn` start command, WhiteNoise for static files |
| **PythonAnywhere** | Manual setup — good for demos, free tier available |

### Production checklist

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` is a long random string (not the dev default)
- [ ] `ALLOWED_HOSTS` contains only your actual domain(s)
- [ ] `DATABASE_URL` points to the production PostgreSQL instance
- [ ] Email backend configured (SendGrid / Mailgun / SES)
- [ ] Static files collected (`collectstatic`)
- [ ] `uv sync --no-group dev` used in production builds

---

## Contributing

```bash
# Install dev dependencies
uv sync

# Run checks before committing
uv run ruff check . && uv run ruff format --check .
```

Commits follow [Conventional Commits](https://www.conventionalcommits.org/):  
`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`

---

*Wynwood House — &copy; 2026*
