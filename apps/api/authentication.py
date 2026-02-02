"""
Custom authentication for API endpoints.

Provides token-based authentication for smart signage devices.
"""

from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model

User = get_user_model()


class DeviceTokenAuthentication(authentication.BaseAuthentication):
    """
    Token-based authentication for smart signage devices.

    Devices authenticate using a token passed in the Authorization header:
    Authorization: Token <device-token>

    Example:
        >>> import requests
        >>> headers = {"Authorization": "Token abc123"}
        >>> response = requests.get(url, headers=headers)
    """

    keyword = "Token"

    def authenticate(self, request):
        """
        Authenticate the request using device token.

        Args:
            request: The HTTP request.

        Returns:
            Tuple of (user, token) if authentication succeeds, None otherwise.

        Raises:
            AuthenticationFailed: If token is invalid.
        """
        auth_header = authentication.get_authorization_header(request)
        if not auth_header:
            return None

        auth_parts = auth_header.decode().split()

        if not auth_parts or auth_parts[0].lower() != self.keyword.lower():
            return None

        if len(auth_parts) == 1:
            raise exceptions.AuthenticationFailed("Invalid token header. No credentials provided.")

        if len(auth_parts) > 2:
            raise exceptions.AuthenticationFailed("Invalid token header. Token should not contain spaces.")

        token = auth_parts[1]
        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token: str):
        """
        Validate the device token.

        Args:
            token: The device token string.

        Returns:
            Tuple of (user, token).

        Raises:
            AuthenticationFailed: If token is invalid or inactive.
        """
        from .models import DeviceToken

        try:
            device_token = DeviceToken.objects.select_related("device__local_authority").get(
                token=token,
                is_active=True,
            )
        except DeviceToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid or inactive token.")

        if not device_token.device.is_active:
            raise exceptions.AuthenticationFailed("Device is inactive.")

        # Update last used timestamp
        device_token.update_last_used()

        return (None, device_token)

    def authenticate_header(self, request):
        """Return the WWW-Authenticate header value."""
        return self.keyword
