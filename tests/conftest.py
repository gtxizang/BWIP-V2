"""
Pytest configuration and fixtures for BWIP tests.
"""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import UserProfile
from apps.locations.models import Location, WaterQualityData
from apps.organisations.models import LocalAuthority
from apps.posters.models import PosterTemplate

User = get_user_model()


@pytest.fixture
def local_authority(db):
    """Create a test Local Authority."""
    return LocalAuthority.objects.create(
        name="Test Council",
        code="TC001",
        email_domain="testcouncil.ie",
        contact_email="env@testcouncil.ie",
        is_active=True,
    )


@pytest.fixture
def user(db, local_authority):
    """Create a test user with organisation."""
    user = User.objects.create_user(
        username="testuser@example.com",
        email="testuser@example.com",
        password="testpassword123",
        first_name="Test",
        last_name="User",
    )
    user.userprofile.local_authority = local_authority
    user.userprofile.role = UserProfile.Role.OFFICER
    user.userprofile.save()
    return user


@pytest.fixture
def admin_user(db, local_authority):
    """Create a test admin user."""
    user = User.objects.create_superuser(
        username="admin@example.com",
        email="admin@example.com",
        password="adminpassword123",
        first_name="Admin",
        last_name="User",
    )
    user.userprofile.local_authority = local_authority
    user.userprofile.role = UserProfile.Role.ADMIN
    user.userprofile.save()
    return user


@pytest.fixture
def location(db, local_authority):
    """Create a test location."""
    return Location.objects.create(
        name_en="Test Beach",
        name_ga="Tra Tástála",
        local_authority=local_authority,
        beaches_ie_id="IETEST_0000_0001",
        classification=Location.Classification.IDENTIFIED,
        latitude=Decimal("53.2695"),
        longitude=Decimal("-6.1544"),
        has_toilets=True,
        has_parking=True,
        has_lifeguard=True,
        is_active=True,
    )


@pytest.fixture
def water_quality(db, location):
    """Create test water quality data."""
    return WaterQualityData.objects.create(
        location=location,
        sample_date="2024-07-15",
        ecoli_value=45,
        enterococci_value=28,
        quality_status=WaterQualityData.QualityStatus.EXCELLENT,
        classification_year=2024,
        is_current=True,
    )


@pytest.fixture
def poster_templates(db):
    """Create all poster templates."""
    templates = []
    template_data = [
        ("1A", "Identified - No Restrictions", "IDENTIFIED"),
        ("1B", "Identified - Temporary Restrictions", "IDENTIFIED"),
        ("1C", "Identified - Season-Long Restrictions", "IDENTIFIED"),
        ("2A", "Non-Identified - With Restrictions", "NON_IDENTIFIED"),
        ("2B", "Non-Identified - No Restrictions", "NON_IDENTIFIED"),
    ]
    for code, name, classification in template_data:
        template = PosterTemplate.objects.create(
            code=code,
            name=name,
            classification=classification,
            is_active=True,
        )
        templates.append(template)
    return templates


@pytest.fixture
def authenticated_client(client, user):
    """Return a client logged in as test user."""
    client.force_login(user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Return a client logged in as admin user."""
    client.force_login(admin_user)
    return client
