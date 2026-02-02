# BWIP - Bathing Water Information Portal

A Django-based internal tool for Irish Local Authorities to generate bathing water information posters.

## Overview

BWIP (Bathing Water Information Portal) enables Local Authorities to:
- Generate print-ready PDF posters (A1/A3/A4/A5) for bathing water locations
- Display current water quality status from EPA beaches.ie API
- Support bilingual content (English/Irish)
- Maintain audit trails for compliance
- Access via REST API for smart signage integration

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- WeasyPrint dependencies (Cairo, Pango, etc.)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd bwip-v2

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install WeasyPrint dependencies (macOS)
brew install cairo pango gdk-pixbuf libffi

# Set up environment
cp .env.example .env
# Edit .env with your database credentials

# Create database
createdb bwip_v2

# Run migrations
python manage.py migrate

# Seed development data
python manage.py shell < scripts/seed_data.py

# Run development server
python manage.py runserver
```

### Default Login Credentials

After seeding data:
- **Admin**: admin@example.com / adminpassword
- **Demo**: demo@example.com / demopassword

## Project Structure

```
bwip-v2/
├── config/                  # Django configuration
│   ├── settings/           # Settings modules (base/dev/prod/test)
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI configuration
│
├── apps/                    # Django applications
│   ├── core/              # Shared utilities and base classes
│   ├── accounts/          # User authentication and profiles
│   ├── organisations/     # Local Authority multi-tenancy
│   ├── locations/         # Bathing water locations
│   ├── posters/           # Poster generation
│   ├── api/               # REST API for smart signage
│   └── audit/             # Audit logging
│
├── services/               # Business logic layer
│   ├── beaches_api/       # EPA beaches.ie API integration
│   ├── pdf_generation/    # PDF poster generation
│   └── ckan/              # CKAN integration (optional)
│
├── templates/              # Django templates
│   ├── base.html          # Base template
│   ├── accounts/          # Account templates
│   ├── locations/         # Location templates
│   ├── posters/           # Poster templates
│   └── pdf/               # PDF poster templates
│
├── static/                 # Static files
├── media/                  # User-uploaded files
├── tests/                  # Test suite
└── scripts/                # Management scripts
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Django secret key | Required |
| DEBUG | Debug mode | false |
| DATABASE_URL | PostgreSQL connection URL | Required |
| BEACHES_API_BASE_URL | EPA API base URL | https://data.epa.ie/bw/api/v1 |
| BEACHES_API_USE_MOCK | Use mock data | false |

### beaches.ie API

The application integrates with the EPA beaches.ie API to fetch:
- Location information
- Water quality measurements
- Active alerts and advisories

In development, set `BEACHES_API_USE_MOCK=true` to use mock data.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov=services

# Run specific test file
pytest apps/locations/tests/test_models.py
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint
ruff check .

# Type checking
mypy apps services
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

## Poster Templates

The system supports 5 poster templates based on EPA specifications:

| Code | Description | Classification |
|------|-------------|----------------|
| 1A | Identified, no restrictions | Identified |
| 1B | Identified, temporary restrictions | Identified |
| 1C | Identified, season-long restrictions | Identified |
| 2A | Non-identified, with restrictions | Non-Identified |
| 2B | Non-identified, no restrictions | Non-Identified |

## API Documentation

### REST API Endpoints

The API provides read-only access for smart signage devices:

```
GET /api/v1/locations/           # List accessible locations
GET /api/v1/locations/{id}/      # Get location details
GET /api/v1/locations/{id}/water_quality/  # Get current water quality
GET /api/v1/locations/{id}/alerts/         # Get active alerts
```

Authentication is via device token in the Authorization header:
```
Authorization: Token <device-token>
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Configure secure `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS`
- [ ] Configure SSL/TLS
- [ ] Set up static file serving
- [ ] Configure email settings
- [ ] Set `BEACHES_API_USE_MOCK=false`
- [ ] Run `collectstatic`

### Docker

```bash
# Build image
docker build -t bwip -f docker/Dockerfile .

# Run container
docker-compose -f docker/docker-compose.yml up
```

## Contributing

1. Create a feature branch
2. Make changes with tests
3. Run code quality checks
4. Submit pull request

## License

Proprietary - All rights reserved.

## Support

For support, contact your system administrator or raise an issue in the project repository.
