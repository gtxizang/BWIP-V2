#!/usr/bin/env python
"""
Seed data script for BWIP development.

Creates demo data including:
- Local Authorities
- Users (admin and demo)
- Locations
- Poster Templates
- Sample Posters

Usage:
    python manage.py shell < scripts/seed_data.py
    OR
    python manage.py runscript seed_data
"""

import os
import sys
from decimal import Decimal

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django

django.setup()

from django.contrib.auth import get_user_model

from apps.accounts.models import UserProfile
from apps.locations.models import Alert, Location, WaterQualityData
from apps.organisations.models import LocalAuthority
from apps.posters.models import Poster, PosterTemplate

User = get_user_model()


def create_local_authorities():
    """Create Irish Local Authorities."""
    print("Creating Local Authorities...")

    authorities = [
        ("DCC", "Dublin City Council", "dublincity.ie"),
        ("FCC", "Fingal County Council", "fingal.ie"),
        ("DLRCC", "Dun Laoghaire-Rathdown County Council", "dlrcoco.ie"),
        ("SDCC", "South Dublin County Council", "sdcc.ie"),
        ("WCC", "Wicklow County Council", "wicklowcoco.ie"),
        ("WXC", "Wexford County Council", "wexfordcoco.ie"),
        ("WD", "Waterford City and County Council", "waterfordcouncil.ie"),
        ("CC", "Cork County Council", "corkcoco.ie"),
        ("KY", "Kerry County Council", "kerrycoco.ie"),
        ("CL", "Clare County Council", "clarecoco.ie"),
        ("GY", "Galway County Council", "galway.ie"),
        ("MO", "Mayo County Council", "mayococo.ie"),
        ("SL", "Sligo County Council", "sligococo.ie"),
        ("DL", "Donegal County Council", "donegalcoco.ie"),
    ]

    for code, name, domain in authorities:
        la, created = LocalAuthority.objects.get_or_create(
            code=code,
            defaults={
                "name": name,
                "email_domain": domain,
                "contact_email": f"env@{domain}",
                "is_active": True,
            },
        )
        status = "Created" if created else "Exists"
        print(f"  {status}: {name}")

    return LocalAuthority.objects.first()


def create_poster_templates():
    """Create poster templates."""
    print("\nCreating Poster Templates...")

    templates = [
        ("1A", "Identified - No Restrictions", "IDENTIFIED", "For identified bathing waters with no active restrictions or advisories."),
        ("1B", "Identified - Temporary Restrictions", "IDENTIFIED", "For identified bathing waters with temporary advisories in effect."),
        ("1C", "Identified - Season-Long Restrictions", "IDENTIFIED", "For identified bathing waters with season-long restrictions."),
        ("2A", "Non-Identified - With Restrictions", "NON_IDENTIFIED", "For non-identified bathing waters with advisories."),
        ("2B", "Non-Identified - No Restrictions", "NON_IDENTIFIED", "For non-identified bathing waters with no advisories."),
    ]

    for code, name, classification, description in templates:
        template, created = PosterTemplate.objects.get_or_create(
            code=code,
            defaults={
                "name": name,
                "classification": classification,
                "description": description,
                "is_active": True,
            },
        )
        status = "Created" if created else "Exists"
        print(f"  {status}: {code} - {name}")


def create_users(default_la):
    """Create admin and demo users."""
    print("\nCreating Users...")

    # Create superuser
    admin_email = "admin@example.com"
    admin, created = User.objects.get_or_create(
        email=admin_email,
        defaults={
            "username": admin_email,
            "is_staff": True,
            "is_superuser": True,
            "first_name": "Admin",
            "last_name": "User",
        },
    )
    if created:
        admin.set_password("adminpassword")
        admin.save()
        print(f"  Created: Admin user ({admin_email} / adminpassword)")
    else:
        print(f"  Exists: Admin user ({admin_email})")

    # Update admin profile
    if hasattr(admin, "userprofile"):
        admin.userprofile.role = UserProfile.Role.ADMIN
        admin.userprofile.local_authority = default_la
        admin.userprofile.save()

    # Create demo user
    demo_email = "demo@example.com"
    demo, created = User.objects.get_or_create(
        email=demo_email,
        defaults={
            "username": demo_email,
            "is_staff": False,
            "is_superuser": False,
            "first_name": "Demo",
            "last_name": "User",
        },
    )
    if created:
        demo.set_password("demopassword")
        demo.save()
        print(f"  Created: Demo user ({demo_email} / demopassword)")
    else:
        print(f"  Exists: Demo user ({demo_email})")

    # Update demo profile
    if hasattr(demo, "userprofile"):
        demo.userprofile.role = UserProfile.Role.OFFICER
        demo.userprofile.local_authority = default_la
        demo.userprofile.save()

    return admin, demo


def create_locations(default_la):
    """Create sample bathing water locations."""
    print("\nCreating Locations...")

    locations_data = [
        {
            "name_en": "Dollymount Strand",
            "name_ga": "Tra Dhollymount",
            "beaches_ie_id": "IEWEBWC170_0000_0200",
            "classification": "IDENTIFIED",
            "latitude": Decimal("53.2695"),
            "longitude": Decimal("-6.1544"),
            "has_toilets": True,
            "has_parking": True,
            "has_lifeguard": True,
            "has_disability_access": True,
            "has_blue_flag": True,
            "dogs_allowed": False,
        },
        {
            "name_en": "Sandymount Strand",
            "name_ga": "Tra an Chnoic Gainimh",
            "beaches_ie_id": "IEWEBWC170_0000_0300",
            "classification": "IDENTIFIED",
            "latitude": Decimal("53.3281"),
            "longitude": Decimal("-6.2118"),
            "has_toilets": False,
            "has_parking": True,
            "has_lifeguard": False,
            "has_disability_access": False,
            "has_blue_flag": False,
            "dogs_allowed": True,
        },
        {
            "name_en": "Portmarnock Beach",
            "name_ga": "Tra Phort Mearnóg",
            "beaches_ie_id": "IEWEBWC170_0000_0400",
            "classification": "IDENTIFIED",
            "latitude": Decimal("53.4234"),
            "longitude": Decimal("-6.1321"),
            "has_toilets": True,
            "has_parking": True,
            "has_lifeguard": True,
            "has_disability_access": True,
            "has_blue_flag": True,
            "dogs_allowed": False,
        },
        {
            "name_en": "Seapoint",
            "name_ga": "Pointe na Mara",
            "beaches_ie_id": "IEWEBWC170_0000_0500",
            "classification": "IDENTIFIED",
            "latitude": Decimal("53.2901"),
            "longitude": Decimal("-6.1654"),
            "has_toilets": True,
            "has_parking": False,
            "has_lifeguard": False,
            "has_disability_access": True,
            "has_blue_flag": False,
            "dogs_allowed": True,
        },
        {
            "name_en": "Forty Foot",
            "name_ga": "An Ceathracha Troigh",
            "beaches_ie_id": "IEWEBWC170_0000_0600",
            "classification": "NON_IDENTIFIED",
            "latitude": Decimal("53.2886"),
            "longitude": Decimal("-6.1145"),
            "has_toilets": False,
            "has_parking": True,
            "has_lifeguard": False,
            "has_disability_access": False,
            "has_blue_flag": False,
            "dogs_allowed": True,
        },
    ]

    for loc_data in locations_data:
        beaches_ie_id = loc_data.pop("beaches_ie_id")
        location, created = Location.objects.get_or_create(
            beaches_ie_id=beaches_ie_id,
            defaults={
                **loc_data,
                "local_authority": default_la,
                "is_active": True,
            },
        )
        status = "Created" if created else "Exists"
        print(f"  {status}: {location.name_en}")

        # Add water quality data
        if created:
            WaterQualityData.objects.create(
                location=location,
                sample_date="2024-07-15",
                ecoli_value=45,
                enterococci_value=28,
                quality_status="EXCELLENT",
                classification_year=2024,
                is_current=True,
            )

    return Location.objects.filter(local_authority=default_la)


def main():
    """Run the seed script."""
    print("=" * 50)
    print("BWIP v2 - Seeding Development Data")
    print("=" * 50)

    # Create Local Authorities
    default_la = create_local_authorities()

    # Create Poster Templates
    create_poster_templates()

    # Create Users
    admin, demo = create_users(default_la)

    # Create Locations
    locations = create_locations(default_la)

    print("\n" + "=" * 50)
    print("Seed Complete!")
    print("=" * 50)
    print("\nYou can now log in with:")
    print("  Admin: admin@example.com / adminpassword")
    print("  Demo:  demo@example.com / demopassword")
    print(f"\nLocations created: {locations.count()}")
    print(f"Templates created: {PosterTemplate.objects.count()}")


if __name__ == "__main__":
    main()
