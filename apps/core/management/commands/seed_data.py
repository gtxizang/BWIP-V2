"""
Management command to seed development data.

Usage:
    python manage.py seed_data
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.models import UserProfile
from apps.locations.models import Location, WaterQualityData
from apps.organisations.models import LocalAuthority
from apps.posters.models import PosterTemplate

User = get_user_model()


class Command(BaseCommand):
    """Seed development data for BWIP."""

    help = "Seeds the database with development/demo data"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Delete existing data before seeding",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS("BWIP v2 - Seeding Development Data"))
        self.stdout.write(self.style.SUCCESS("=" * 50))

        if options["clean"]:
            self.clean_data()

        default_la = self.create_local_authorities()
        self.create_poster_templates()
        self.create_users(default_la)
        self.create_locations(default_la)

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 50))
        self.stdout.write(self.style.SUCCESS("Seed Complete!"))
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write("\nYou can now log in with:")
        self.stdout.write("  Admin: admin@example.com / adminpassword")
        self.stdout.write("  Demo:  demo@example.com / demopassword")

    def clean_data(self):
        """Delete existing seed data."""
        self.stdout.write("\nCleaning existing data...")
        # Don't delete - just skip existing

    def create_local_authorities(self):
        """Create Irish Local Authorities."""
        self.stdout.write("\nCreating Local Authorities...")

        authorities = [
            ("DCC", "Dublin City Council", "dublincity.ie"),
            ("FCC", "Fingal County Council", "fingal.ie"),
            ("DLRCC", "Dun Laoghaire-Rathdown County Council", "dlrcoco.ie"),
            ("SDCC", "South Dublin County Council", "sdcc.ie"),
            ("WCC", "Wicklow County Council", "wicklowcoco.ie"),
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
            self.stdout.write(f"  {status}: {name}")

        return LocalAuthority.objects.first()

    def create_poster_templates(self):
        """Create poster templates."""
        self.stdout.write("\nCreating Poster Templates...")

        templates = [
            ("1A", "Identified - No Restrictions", "IDENTIFIED"),
            ("1B", "Identified - Temporary Restrictions", "IDENTIFIED"),
            ("1C", "Identified - Season-Long Restrictions", "IDENTIFIED"),
            ("2A", "Non-Identified - With Restrictions", "NON_IDENTIFIED"),
            ("2B", "Non-Identified - No Restrictions", "NON_IDENTIFIED"),
        ]

        for code, name, classification in templates:
            template, created = PosterTemplate.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "classification": classification,
                    "is_active": True,
                },
            )
            status = "Created" if created else "Exists"
            self.stdout.write(f"  {status}: {code} - {name}")

    def create_users(self, default_la):
        """Create admin and demo users."""
        self.stdout.write("\nCreating Users...")

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
            self.stdout.write(f"  Created: Admin user ({admin_email} / adminpassword)")
        else:
            self.stdout.write(f"  Exists: Admin user ({admin_email})")

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
            self.stdout.write(f"  Created: Demo user ({demo_email} / demopassword)")
        else:
            self.stdout.write(f"  Exists: Demo user ({demo_email})")

        # Update demo profile
        if hasattr(demo, "userprofile"):
            demo.userprofile.role = UserProfile.Role.OFFICER
            demo.userprofile.local_authority = default_la
            demo.userprofile.save()

    def create_locations(self, default_la):
        """Create sample bathing water locations."""
        self.stdout.write("\nCreating Locations...")

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
            self.stdout.write(f"  {status}: {location.name_en}")

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
