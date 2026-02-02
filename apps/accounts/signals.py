"""
Signals for the accounts application.

Handles automatic creation of UserProfile when a User is created.
"""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance: User, created: bool, **kwargs) -> None:
    """
    Create a UserProfile automatically when a User is created.

    Args:
        sender: The User model class.
        instance: The User instance that was saved.
        created: True if the instance was just created.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance: User, **kwargs) -> None:
    """
    Save the UserProfile when the User is saved.

    Args:
        sender: The User model class.
        instance: The User instance that was saved.
    """
    if hasattr(instance, "userprofile"):
        instance.userprofile.save()
