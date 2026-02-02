"""Admin configuration for the accounts application."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import UserProfile

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile on the User admin page."""

    model = UserProfile
    can_delete = False
    verbose_name_plural = _("Profile")
    fk_name = "user"


class UserAdmin(BaseUserAdmin):
    """Custom User admin with UserProfile inline."""

    inlines = (UserProfileInline,)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "get_local_authority",
        "get_role",
    )
    list_select_related = ("userprofile", "userprofile__local_authority")

    def get_local_authority(self, obj: User) -> str:
        """Get the user's Local Authority name."""
        if hasattr(obj, "userprofile") and obj.userprofile.local_authority:
            return obj.userprofile.local_authority.name
        return "-"

    get_local_authority.short_description = _("Local Authority")
    get_local_authority.admin_order_field = "userprofile__local_authority__name"

    def get_role(self, obj: User) -> str:
        """Get the user's role."""
        if hasattr(obj, "userprofile"):
            return obj.userprofile.get_role_display()
        return "-"

    get_role.short_description = _("Role")


# Re-register User with custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""

    list_display = ("user", "local_authority", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "local_authority")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")
