"""
Signals for the audit application.

Handles automatic audit logging for model changes.
"""

import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.locations.models import Location

from .models import AuditLog

logger = logging.getLogger(__name__)


def get_client_ip(request) -> str | None:
    """Extract client IP from request."""
    if request is None:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_user_agent(request) -> str:
    """Extract user agent from request."""
    if request is None:
        return ""
    return request.META.get("HTTP_USER_AGENT", "")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs) -> None:
    """Log user login events."""
    try:
        AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.USER_LOGIN,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={"email": user.email},
        )
    except Exception as e:
        logger.error(f"Failed to log user login: {e}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs) -> None:
    """Log user logout events."""
    if user is None:
        return
    try:
        AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.USER_LOGOUT,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={"email": user.email},
        )
    except Exception as e:
        logger.error(f"Failed to log user logout: {e}")


@receiver(post_save, sender=Location)
def log_location_change(sender, instance: Location, created: bool, **kwargs) -> None:
    """Log location creation and modifications."""
    try:
        action = AuditLog.Action.LOCATION_CREATED if created else AuditLog.Action.LOCATION_MODIFIED
        AuditLog.objects.create(
            action=action,
            location=instance,
            details={
                "name": instance.name_en,
                "beaches_ie_id": instance.beaches_ie_id,
                "classification": instance.classification,
            },
        )
    except Exception as e:
        logger.error(f"Failed to log location change: {e}")
