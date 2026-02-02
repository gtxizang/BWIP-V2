"""
Factory Boy factories for BWIP tests.
"""

from decimal import Decimal

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.accounts.models import UserProfile
from apps.locations.models import Alert, Location, WaterQualityData
from apps.organisations.models import LocalAuthority
from apps.posters.models import Poster, PosterTemplate

User = get_user_model()


class LocalAuthorityFactory(DjangoModelFactory):
    """Factory for LocalAuthority model."""

    class Meta:
        model = LocalAuthority

    name = factory.Sequence(lambda n: f"Test Council {n}")
    code = factory.Sequence(lambda n: f"TC{n:03d}")
    email_domain = factory.LazyAttribute(lambda o: f"{o.code.lower()}.ie")
    contact_email = factory.LazyAttribute(lambda o: f"env@{o.email_domain}")
    is_active = True


class UserFactory(DjangoModelFactory):
    """Factory for User model."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}@example.com")
    email = factory.LazyAttribute(lambda o: o.username)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after user creation."""
        password = extracted or "testpassword123"
        self.set_password(password)
        if create:
            self.save()

    @factory.post_generation
    def local_authority(self, create, extracted, **kwargs):
        """Assign local authority to user profile."""
        if create and extracted:
            self.userprofile.local_authority = extracted
            self.userprofile.save()


class LocationFactory(DjangoModelFactory):
    """Factory for Location model."""

    class Meta:
        model = Location

    name_en = factory.Sequence(lambda n: f"Test Beach {n}")
    name_ga = factory.Sequence(lambda n: f"Tra Tástála {n}")
    local_authority = factory.SubFactory(LocalAuthorityFactory)
    beaches_ie_id = factory.Sequence(lambda n: f"IETEST_{n:04d}_0001")
    classification = Location.Classification.IDENTIFIED
    latitude = factory.LazyFunction(lambda: Decimal("53.3498"))
    longitude = factory.LazyFunction(lambda: Decimal("-6.2603"))
    is_active = True


class WaterQualityDataFactory(DjangoModelFactory):
    """Factory for WaterQualityData model."""

    class Meta:
        model = WaterQualityData

    location = factory.SubFactory(LocationFactory)
    sample_date = factory.Faker("date_this_year")
    ecoli_value = factory.Faker("random_int", min=10, max=500)
    enterococci_value = factory.Faker("random_int", min=10, max=300)
    quality_status = WaterQualityData.QualityStatus.EXCELLENT
    classification_year = 2024
    is_current = True


class AlertFactory(DjangoModelFactory):
    """Factory for Alert model."""

    class Meta:
        model = Alert

    location = factory.SubFactory(LocationFactory)
    alert_type = Alert.AlertType.NOTICE
    title_en = factory.Faker("sentence", nb_words=4)
    message_en = factory.Faker("paragraph")
    start_date = factory.Faker("date_this_month")
    is_active = True
    is_season_long = False


class PosterTemplateFactory(DjangoModelFactory):
    """Factory for PosterTemplate model."""

    class Meta:
        model = PosterTemplate

    code = factory.Iterator(["1A", "1B", "1C", "2A", "2B"])
    name = factory.LazyAttribute(lambda o: f"Template {o.code}")
    classification = factory.LazyAttribute(
        lambda o: "IDENTIFIED" if o.code.startswith("1") else "NON_IDENTIFIED"
    )
    is_active = True


class PosterFactory(DjangoModelFactory):
    """Factory for Poster model."""

    class Meta:
        model = Poster

    location = factory.SubFactory(LocationFactory)
    template = factory.SubFactory(PosterTemplateFactory)
    poster_type = Poster.PosterType.FULL
    size = Poster.Size.A1
    orientation = Poster.Orientation.PORTRAIT
    language = Poster.Language.EN
    water_quality_data = factory.LazyFunction(dict)
