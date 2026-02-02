"""
CKAN API client.

Provides integration with CKAN open data portal for publishing
generated posters and data.
"""

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class CKANClient:
    """
    Client for CKAN open data portal.

    Handles publishing posters and data to CKAN.
    This is a placeholder implementation - configure with actual
    CKAN credentials for production use.

    Example:
        >>> client = CKANClient()
        >>> resource_id = client.upload_poster(poster, pdf_bytes)
    """

    def __init__(self) -> None:
        """Initialize the CKAN client."""
        self.api_url = getattr(settings, "CKAN_API_URL", "")
        self.api_key = getattr(settings, "CKAN_API_KEY", "")
        self._session = requests.Session()
        if self.api_key:
            self._session.headers.update({"Authorization": self.api_key})

    @property
    def is_configured(self) -> bool:
        """Check if CKAN is configured."""
        return bool(self.api_url and self.api_key)

    def upload_poster(
        self,
        poster,
        pdf_bytes: bytes,
        package_id: str = "bathing-water-posters",
    ) -> str | None:
        """
        Upload a poster PDF to CKAN.

        Args:
            poster: Poster model instance.
            pdf_bytes: PDF file bytes.
            package_id: CKAN dataset/package ID.

        Returns:
            CKAN resource ID if successful, None otherwise.
        """
        if not self.is_configured:
            logger.warning("CKAN not configured, skipping upload")
            return None

        try:
            # Create resource metadata
            resource_name = f"{poster.location.name_en} - {poster.template.code}"

            response = self._session.post(
                f"{self.api_url}/action/resource_create",
                data={
                    "package_id": package_id,
                    "name": resource_name,
                    "format": "PDF",
                    "description": f"Bathing water information poster for {poster.location.name_en}",
                },
                files={"upload": (poster.filename, pdf_bytes, "application/pdf")},
            )
            response.raise_for_status()
            result = response.json()

            if result.get("success"):
                resource_id = result["result"]["id"]
                logger.info(f"Uploaded poster to CKAN: {resource_id}")
                return resource_id

            logger.error(f"CKAN upload failed: {result.get('error')}")
            return None

        except requests.RequestException as e:
            logger.error(f"CKAN upload request failed: {e}")
            return None

    def get_package(self, package_id: str) -> dict[str, Any] | None:
        """
        Get a CKAN package/dataset.

        Args:
            package_id: CKAN package ID.

        Returns:
            Package data dict or None.
        """
        if not self.is_configured:
            return None

        try:
            response = self._session.get(
                f"{self.api_url}/action/package_show",
                params={"id": package_id},
            )
            response.raise_for_status()
            result = response.json()
            return result.get("result") if result.get("success") else None
        except requests.RequestException as e:
            logger.error(f"CKAN request failed: {e}")
            return None
