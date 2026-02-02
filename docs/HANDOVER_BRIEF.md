# BWIP v2 - Technical Handover Brief

**Prepared for:** Cormac
**Date:** January 2026
**Status:** Development Preview

---

## 1. Project Purpose (North Star)

### What is BWIP?

**Bathing Water Information Portal** - A system for Irish Local Authorities to generate and manage EPA-compliant bathing water signage.

### The Problem

Local Authorities are required to display water quality information at designated bathing locations. Currently:
- Poster generation is manual and error-prone
- Water quality data must be manually transcribed from EPA sources
- No audit trail of what was displayed and when
- Inconsistent signage across different authorities

### The Solution

BWIP automates the generation of compliant posters by:
1. **Pulling live data** from the beaches.ie EPA API
2. **Recommending the correct poster template** based on classification and alert status
3. **Generating print-ready PDFs** in multiple sizes (A1-A5)
4. **Maintaining an audit trail** of all generated materials
5. **Supporting multi-tenancy** so each Local Authority sees only their locations

### Success Metrics
- Reduce poster generation time from hours to minutes
- Eliminate data transcription errors
- 100% compliance with EPA signage requirements
- Full audit trail for regulatory purposes

---

## 2. Technical Approach

### Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Backend** | Django 5.2 | Mature, batteries-included, strong ORM |
| **Database** | PostgreSQL (SQLite for dev) | Production-grade, JSON support for EPA data snapshots |
| **PDF Generation** | WeasyPrint | HTML/CSS to PDF, no external dependencies |
| **API Integration** | httpx | Modern async-capable HTTP client |
| **Frontend** | Django Templates + Bootstrap 5 | Simple, maintainable, no SPA complexity |
| **Admin UI** | django-jazzmin | Modern Bootstrap-based admin theme |
| **Maps** | Leaflet.js | Lightweight, OSM-based |

### Key Design Decisions

**1. Service Layer Pattern**
```
apps/           → Django apps (views, models, forms)
services/       → Business logic (API clients, PDF generation)
```
Business logic is separated from Django, making it testable and reusable.

**2. Multi-Tenancy via LocalAuthority**
- Each user has a `UserProfile` linked to a `LocalAuthority`
- All queries are scoped to the user's Local Authority
- Users can only see/generate posters for their locations

**3. EPA Template Compliance**
Five poster templates per EPA specification:
- **1A, 1B, 1C** - Identified bathing waters (no restrictions, temporary, season-long)
- **2A, 2B** - Non-identified bathing waters (with/without restrictions)

Template recommendation is automatic based on:
- Location classification (IDENTIFIED vs NON_IDENTIFIED)
- Active alerts from EPA API
- Alert duration (temporary vs season-long)

**4. Audit Everything**
- All poster generations logged with user, timestamp, EPA data snapshot
- Login/logout events tracked
- Immutable audit records for regulatory compliance

---

## 3. Project Structure

```
bwip-v2/
├── apps/                       # Django applications
│   ├── accounts/               # User auth, profiles, roles
│   ├── api/                    # REST API for devices/kiosks
│   ├── audit/                  # Immutable audit logging
│   ├── core/                   # Base models, mixins, utilities
│   ├── locations/              # Beaches, water quality data, alerts
│   ├── organisations/          # Local Authorities (multi-tenancy)
│   └── posters/                # Poster generation, templates, history
│
├── services/                   # Business logic layer
│   ├── beaches_api/            # EPA API client (with mock support)
│   ├── pdf_generation/         # WeasyPrint PDF generator
│   └── ckan/                   # Open data publishing (placeholder)
│
├── config/                     # Django configuration
│   └── settings/
│       ├── base.py             # Shared settings
│       ├── development.py      # Local dev settings
│       ├── production.py       # Production settings
│       └── test.py             # Test settings
│
├── templates/                  # HTML templates
│   ├── pdf/                    # Poster templates (1a_en.html, etc.)
│   └── ...                     # Web UI templates
│
├── tests/                      # Test suite
│   ├── conftest.py             # Pytest fixtures
│   └── factories.py            # Factory Boy factories
│
└── scripts/                    # Utility scripts
    └── seed_data.py            # Demo data seeder
```

### Model Relationships

```
LocalAuthority
    ├── UserProfile (many)
    ├── Location (many)
    │       ├── WaterQualityData (many)
    │       ├── Alert (many)
    │       └── Poster (many)
    │               └── PosterTemplate (FK)
    └── Device (many) [for kiosk API]
```

---

## 4. Current State

### What's Working
- User authentication (email-based)
- Dashboard with interactive map
- Location management
- Poster generation workflow with template override tracking
- Custom notifications on posters (LA-specific messages)
- EPA API integration (mock mode)
- Template recommendation engine
- PDF generation (WeasyPrint)
- Audit logging (login/logout, poster generation, overrides)
- Modern admin UI (jazzmin)
- Seed data for development

### What's Not Yet Implemented

| Feature | Priority | Notes |
|---------|----------|-------|
| Test suite | High | Fixtures ready, tests not written |
| CI/CD pipeline | High | No GitHub Actions yet |
| Docker setup | Medium | No containerisation |
| Pre-commit hooks | Medium | Linting tools installed but not configured |
| API documentation | Medium | No OpenAPI/Swagger |
| Irish language templates | Low | English only currently |
| CKAN publishing | Low | Placeholder service |

---

## 5. Questions for Discussion

1. **Testing Strategy**
   - What level of coverage is expected before handover?
   - Unit tests only, or integration tests for EPA API?

2. **Deployment Target**
   - Docker/Kubernetes, or traditional VM deployment?
   - Which cloud provider (if any)?

3. **CI/CD Requirements**
   - GitHub Actions, or different CI platform?
   - Automated deployments, or manual promotion?

4. **Security Review**
   - External penetration testing required?
   - Specific compliance requirements beyond audit logging?

5. **Timeline**
   - What's the target date for Dev environment handover?
   - Phased delivery acceptable?

---

## 6. Demo Access

**Local Development Server:** http://localhost:8001/

**Test Accounts:**
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | adminpassword |
| Officer | demo@example.com | demopassword |

**Quick Test Flow:**
1. Login as demo user
2. Click a map marker → "Generate Poster"
3. Observe API data fetch and template recommendation
4. Generate poster (PDF)

---

## 7. Next Steps (Proposed)

Pending Cormac's guidance, suggested priorities:

1. Write core test suite (models, services, views)
2. Add CI pipeline + Docker setup
3. Security hardening + API documentation
4. Integration testing + handover documentation

---

*This document is a living brief. Updates will be made based on feedback from this discussion.*
