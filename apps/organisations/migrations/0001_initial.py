# Generated migration for LocalAuthority without django-organizations

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LocalAuthority",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        help_text="Full name of the Local Authority",
                        max_length=200,
                        verbose_name="name",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        help_text="Short code, e.g., 'DCC' for Dublin City Council",
                        max_length=10,
                        unique=True,
                        verbose_name="code",
                    ),
                ),
                (
                    "email_domain",
                    models.CharField(
                        blank=True,
                        help_text="Allowed email domain, e.g., 'dublincity.ie'",
                        max_length=100,
                        verbose_name="email domain",
                    ),
                ),
                (
                    "contact_email",
                    models.EmailField(
                        blank=True,
                        help_text="Primary contact email for the Local Authority",
                        max_length=254,
                        verbose_name="contact email",
                    ),
                ),
                (
                    "logo",
                    models.ImageField(
                        blank=True,
                        help_text="Local Authority logo for posters",
                        upload_to="logos/",
                        verbose_name="logo",
                    ),
                ),
                (
                    "primary_colour",
                    models.CharField(
                        default="#0066CC",
                        help_text="Hex colour code for branding, e.g., '#0066CC'",
                        max_length=7,
                        verbose_name="primary colour",
                    ),
                ),
                (
                    "secondary_colour",
                    models.CharField(
                        default="#FFFFFF",
                        help_text="Secondary hex colour code for branding",
                        max_length=7,
                        verbose_name="secondary colour",
                    ),
                ),
                (
                    "address",
                    models.TextField(
                        blank=True,
                        help_text="Physical address of the Local Authority",
                        verbose_name="address",
                    ),
                ),
                (
                    "website",
                    models.URLField(
                        blank=True,
                        help_text="Official website URL",
                        verbose_name="website",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        help_text="Contact phone number",
                        max_length=20,
                        verbose_name="phone",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Whether this Local Authority is active",
                        verbose_name="active",
                    ),
                ),
            ],
            options={
                "verbose_name": "local authority",
                "verbose_name_plural": "local authorities",
                "ordering": ["name"],
            },
        ),
    ]
