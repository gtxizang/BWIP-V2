"""
Custom authentication backends for BWIP.

Provides email-based authentication instead of username-based.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Authentication backend that uses email instead of username.

    Allows users to log in with their email address.

    Example:
        >>> from django.contrib.auth import authenticate
        >>> user = authenticate(request, username="user@example.com", password="secret")
    """

    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs,
    ) -> User | None:
        """
        Authenticate a user by email and password.

        Args:
            request: The HTTP request.
            username: The email address (named username for compatibility).
            password: The user's password.

        Returns:
            The User if authentication succeeds, None otherwise.
        """
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            # Run the default password hasher to prevent timing attacks
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id: int) -> User | None:
        """
        Get a user by their ID.

        Args:
            user_id: The user's primary key.

        Returns:
            The User if found, None otherwise.
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
