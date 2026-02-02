"""
beaches.ie API client.

Provides a client for interacting with the EPA beaches.ie API
to fetch location, water quality, and alert data.
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache

from .exceptions import (
    BeachesAPIError,
    BeachesAPIInvalidResponse,
    BeachesAPINotFound,
    BeachesAPITimeout,
)

logger = logging.getLogger(__name__)


@dataclass
class BeachesAPIConfig:
    """Configuration for beaches.ie API client."""

    base_url: str = field(
        default_factory=lambda: getattr(
            settings, "BEACHES_API", {}
        ).get("BASE_URL", "https://data.epa.ie/bw/api/v1")
    )
    timeout: int = field(
        default_factory=lambda: getattr(
            settings, "BEACHES_API", {}
        ).get("TIMEOUT", 10)
    )
    cache_timeout: int = field(
        default_factory=lambda: getattr(
            settings, "BEACHES_API", {}
        ).get("CACHE_TIMEOUT", 3600)
    )
    use_mock_data: bool = field(
        default_factory=lambda: getattr(
            settings, "BEACHES_API", {}
        ).get("USE_MOCK_DATA", False)
    )


class BeachesAPIClient:
    """
    Client for beaches.ie EPA API.

    Handles fetching location, water quality, and alert data
    with caching and graceful degradation.

    Example:
        >>> client = BeachesAPIClient()
        >>> location = client.get_location("IEWEBWC170_0000_0200")
        >>> quality = client.get_water_quality("IEWEBWC170_0000_0200")
        >>> summary = client.format_for_poster("IEWEBWC170_0000_0200")
    """

    def __init__(self, config: BeachesAPIConfig | None = None) -> None:
        """
        Initialize the API client.

        Args:
            config: Optional configuration. Uses settings if not provided.
        """
        self.config = config or BeachesAPIConfig()
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/json",
            "User-Agent": "BWIP/2.0",
        })

    def _strip_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        if not text:
            return ""
        clean = re.compile("<.*?>")
        return re.sub(clean, "", text).strip()

    def _make_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        use_cache: bool = True,
    ) -> dict[str, Any] | list[Any] | None:
        """
        Make a request to the API.

        Args:
            endpoint: API endpoint path.
            params: Optional query parameters.
            use_cache: Whether to check cache first.

        Returns:
            API response data.

        Raises:
            BeachesAPIError: On API errors.
            BeachesAPITimeout: On timeout.
            BeachesAPINotFound: If resource not found.
        """
        # Check if using mock data
        if self.config.use_mock_data:
            return self._get_mock_response(endpoint, params)

        cache_key = f"beaches_api:{endpoint}:{str(params)}"

        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {endpoint}")
                return cached

        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self._session.get(
                url,
                params=params,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            data = response.json()

            if use_cache and data:
                cache.set(cache_key, data, self.config.cache_timeout)

            return data

        except requests.Timeout:
            logger.warning(f"Timeout fetching {endpoint}")
            # Try to return stale cache
            cached = cache.get(cache_key)
            if cached:
                logger.info(f"Using stale cache for {endpoint}")
                return cached
            raise BeachesAPITimeout(f"Timeout fetching {endpoint}")

        except requests.HTTPError as e:
            if e.response.status_code == 404:
                raise BeachesAPINotFound(f"Resource not found: {endpoint}")
            raise BeachesAPIError(f"API error: {e}")

        except requests.RequestException as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            # Try stale cache
            cached = cache.get(cache_key)
            if cached:
                return cached
            raise BeachesAPIError(f"Request failed: {e}")

        except ValueError as e:
            raise BeachesAPIInvalidResponse(f"Invalid JSON response: {e}")

    def get_location(self, beach_id: str, use_cache: bool = True) -> dict[str, Any] | None:
        """
        Fetch location data from beaches.ie.

        Args:
            beach_id: The beaches.ie location identifier.
            use_cache: Whether to check cache first.

        Returns:
            Location data dict if found, None otherwise.
        """
        try:
            data = self._make_request(f"locations/{beach_id}", use_cache=use_cache)
            return data
        except BeachesAPINotFound:
            return None
        except BeachesAPIError as e:
            logger.error(f"Error fetching location {beach_id}: {e}")
            return None

    def get_measurements(
        self,
        beach_id: str,
        limit: int = 10,
        use_cache: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Fetch water quality measurements.

        Args:
            beach_id: The beaches.ie location identifier.
            limit: Maximum number of measurements to return.
            use_cache: Whether to check cache first.

        Returns:
            List of measurement records.
        """
        try:
            data = self._make_request(
                f"measurements",
                params={"beach_id": beach_id, "per_page": limit},
                use_cache=use_cache,
            )
            if isinstance(data, dict) and "data" in data:
                return data["data"][:limit]
            return data[:limit] if isinstance(data, list) else []
        except BeachesAPIError as e:
            logger.error(f"Error fetching measurements for {beach_id}: {e}")
            return []

    def get_latest_measurement(
        self,
        beach_id: str,
        use_cache: bool = True,
    ) -> dict[str, Any] | None:
        """
        Fetch the most recent measurement.

        Args:
            beach_id: The beaches.ie location identifier.
            use_cache: Whether to check cache first.

        Returns:
            Latest measurement or None.
        """
        measurements = self.get_measurements(beach_id, limit=1, use_cache=use_cache)
        return measurements[0] if measurements else None

    def get_alerts(self, beach_id: str, use_cache: bool = True) -> list[dict[str, Any]]:
        """
        Fetch current alerts for a location.

        Args:
            beach_id: The beaches.ie location identifier.
            use_cache: Whether to check cache first.

        Returns:
            List of active alerts.
        """
        try:
            data = self._make_request(
                f"alerts",
                params={"beach_id": beach_id, "is_active": True},
                use_cache=use_cache,
            )
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data if isinstance(data, list) else []
        except BeachesAPIError as e:
            logger.error(f"Error fetching alerts for {beach_id}: {e}")
            return []

    def format_for_poster(self, beach_id: str, use_cache: bool = True) -> dict[str, Any]:
        """
        Get all data formatted for poster generation.

        Fetches location, measurements, and alerts, then formats
        the data for use in poster templates.

        Args:
            beach_id: The beaches.ie location identifier.
            use_cache: Whether to check cache first.

        Returns:
            Formatted data dict for poster generation.
        """
        # Fetch all data
        location = self.get_location(beach_id, use_cache)
        measurements = self.get_measurements(beach_id, limit=5, use_cache=use_cache)
        alerts = self.get_alerts(beach_id, use_cache)

        # Build formatted response
        formatted = {
            "beach_id": beach_id,
            "beach_name": "",
            "beach_description": "",
            "classification": "",
            "classification_year": None,
            "last_sample_date": None,
            "last_sample_status": "",
            "ecoli_value": None,
            "enterococci_value": None,
            "recent_measurements": [],
            "has_active_alerts": False,
            "alert_details": {},
            "facilities": {
                "toilets": False,
                "parking": False,
                "lifeguard": False,
                "disability_access": False,
                "blue_flag": False,
            },
            "dogs_allowed": True,
            "short_term_pollution_risk": False,
            "fetched_at": datetime.now().isoformat(),
            "debug_mode": self.config.use_mock_data,
        }

        # Process location data
        if location:
            formatted["beach_name"] = location.get("name", location.get("beach_name", ""))
            formatted["beach_description"] = self._strip_html(
                location.get("description", "")
            )
            formatted["classification"] = location.get("classification", "")
            formatted["classification_year"] = location.get("classification_year")

            # Facilities
            facilities = location.get("facilities", {})
            if isinstance(facilities, dict):
                formatted["facilities"].update({
                    k: bool(v) for k, v in facilities.items()
                    if k in formatted["facilities"]
                })

            formatted["dogs_allowed"] = location.get("dogs_allowed", True)

        # Process measurements
        if measurements:
            latest = measurements[0]
            formatted["last_sample_date"] = latest.get("sample_date", latest.get("date"))
            formatted["last_sample_status"] = latest.get("status", latest.get("quality", ""))
            formatted["ecoli_value"] = latest.get("ecoli", latest.get("ecoli_value"))
            formatted["enterococci_value"] = latest.get(
                "enterococci", latest.get("enterococci_value")
            )

            # Format recent measurements
            formatted["recent_measurements"] = [
                {
                    "date": m.get("sample_date", m.get("date", "")),
                    "ecoli": m.get("ecoli", m.get("ecoli_value")),
                    "enterococci": m.get("enterococci", m.get("enterococci_value")),
                    "quality": m.get("status", m.get("quality", "")),
                }
                for m in measurements[:5]
            ]

        # Process alerts
        if alerts:
            formatted["has_active_alerts"] = True
            alert = alerts[0]  # Primary alert
            formatted["alert_details"] = {
                "type": alert.get("type", "NOTICE"),
                "title": alert.get("title", ""),
                "message": alert.get("message", ""),
                "start_date": alert.get("start_date"),
                "end_date": alert.get("end_date"),
                "is_season_long": alert.get("is_season_long", False),
            }

        return formatted

    def _get_mock_response(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Return mock data for testing/development.

        Args:
            endpoint: API endpoint.
            params: Query parameters.

        Returns:
            Mock response data.
        """
        beach_id = params.get("beach_id", "") if params else ""

        if "location" in endpoint:
            return self._get_mock_location(beach_id or endpoint.split("/")[-1])
        elif "measurement" in endpoint:
            return self._get_mock_measurements()
        elif "alert" in endpoint:
            return self._get_mock_alerts()

        return {}

    def _get_mock_location(self, beach_id: str) -> dict[str, Any]:
        """Return mock location data."""
        return {
            "beach_id": beach_id,
            "beach_name": "Dollymount Strand (Mock)",
            "name": "Dollymount Strand (Mock)",
            "description": "<p>A beautiful sandy beach on Dublin Bay.</p>",
            "classification": "Excellent Quality",
            "classification_year": 2024,
            "coordinates": {"latitude": 53.2695, "longitude": -6.1544},
            "facilities": {
                "toilets": True,
                "parking": True,
                "lifeguard": True,
                "disability_access": True,
                "blue_flag": True,
            },
            "dogs_allowed": False,
        }

    def _get_mock_measurements(self) -> dict[str, list[dict[str, Any]]]:
        """Return mock measurement data."""
        return {
            "data": [
                {
                    "sample_date": "2024-07-15",
                    "ecoli": 45,
                    "enterococci": 28,
                    "quality": "Excellent",
                },
                {
                    "sample_date": "2024-07-08",
                    "ecoli": 52,
                    "enterococci": 35,
                    "quality": "Excellent",
                },
                {
                    "sample_date": "2024-07-01",
                    "ecoli": 38,
                    "enterococci": 22,
                    "quality": "Excellent",
                },
            ]
        }

    def _get_mock_alerts(self) -> list[dict[str, Any]]:
        """Return mock alert data (empty by default)."""
        return []
