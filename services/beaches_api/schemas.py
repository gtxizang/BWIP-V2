"""
Data schemas for beaches.ie API responses.

Provides Pydantic models for validating and typing API responses.
"""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    """Geographic coordinates."""

    latitude: float
    longitude: float


class Facilities(BaseModel):
    """Beach facilities information."""

    toilets: bool = False
    parking: bool = False
    lifeguard: bool = False
    disability_access: bool = False
    blue_flag: bool = False


class LocationData(BaseModel):
    """Location data from beaches.ie API."""

    id: str = Field(alias="beach_id")
    name: str = Field(alias="beach_name")
    description: str = ""
    coordinates: Coordinates | None = None
    classification: str = ""
    facilities: Facilities = Field(default_factory=Facilities)
    dogs_allowed: bool = True

    class Config:
        populate_by_name = True


class Measurement(BaseModel):
    """Water quality measurement data."""

    date: date
    ecoli: int | None = None
    enterococci: int | None = None
    quality: str = "Not Classified"


class WaterQualityData(BaseModel):
    """Water quality data from beaches.ie API."""

    beach_id: str
    classification: str = ""
    classification_year: int | None = None
    last_sample_date: date | None = None
    last_sample_status: str = ""
    ecoli_value: int | None = None
    enterococci_value: int | None = None
    recent_measurements: list[Measurement] = Field(default_factory=list)


class AlertData(BaseModel):
    """Alert/notice data from beaches.ie API."""

    id: str = ""
    type: str = "NOTICE"
    title: str = ""
    message: str = ""
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool = True
    is_season_long: bool = False


class BeachSummary(BaseModel):
    """Complete beach summary combining location, quality, and alerts."""

    beach_id: str
    beach_name: str
    beach_description: str = ""
    classification: str = ""
    classification_year: int | None = None
    last_sample_date: str | None = None
    last_sample_status: str = ""
    ecoli_value: int | None = None
    enterococci_value: int | None = None
    recent_measurements: list[dict[str, Any]] = Field(default_factory=list)
    has_active_alerts: bool = False
    alert_details: dict[str, Any] = Field(default_factory=dict)
    facilities: dict[str, bool] = Field(default_factory=dict)
    dogs_allowed: bool = True
    short_term_pollution_risk: bool = False
    fetched_at: datetime = Field(default_factory=datetime.now)
    debug_mode: bool = False
