"""Small dataclasses used across retrieval, matching, and recommendation steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import InputValidationError


@dataclass
class GardenInputs:
    location: str
    month: str
    garden_space: str
    sun_exposure: str
    water_access: str
    garden_type: str
    plant_query: str
    usda_zone: str = ""

    def validate(self) -> None:
        if not self.location.strip():
            raise InputValidationError("Please enter a city, town, or ZIP code.")
        if not self.plant_query.strip():
            raise InputValidationError("Please enter a plant to search for.")


@dataclass
class LocationResult:
    name: str
    latitude: float
    longitude: float
    country: str = ""
    admin1: str = ""
    timezone: str = ""

    @property
    def display_name(self) -> str:
        parts = [self.name, self.admin1, self.country]
        return ", ".join(part for part in parts if part)


@dataclass
class ForecastDay:
    date: str
    temp_max: float | None
    temp_min: float | None
    precipitation_sum: float | None


@dataclass
class WeatherResult:
    current_temperature: float | None
    current_humidity: float | None
    current_precipitation: float | None
    temperature_unit: str = "F"
    precipitation_unit: str = "inch"
    humidity_unit: str = "%"
    forecast: list[ForecastDay] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def forecast_summary(self) -> str:
        if not self.forecast:
            return "No short-term forecast was returned."

        pieces: list[str] = []
        for day in self.forecast[:3]:
            temp_text = "temperature unavailable"
            if day.temp_min is not None and day.temp_max is not None:
                temp_text = f"{day.temp_min:.0f}-{day.temp_max:.0f}{self.temperature_unit}"

            rain_text = "precipitation unavailable"
            if day.precipitation_sum is not None:
                rain_text = f"{day.precipitation_sum:.2f} {self.precipitation_unit} precipitation"

            pieces.append(f"{day.date}: {temp_text}, {rain_text}")

        return "; ".join(pieces)


@dataclass
class PlantMatch:
    plant_id: int | None
    common_name: str
    scientific_name: list[str] = field(default_factory=list)
    other_names: list[str] = field(default_factory=list)
    sunlight: list[str] = field(default_factory=list)
    watering: str = ""
    cycle: str = ""
    care_level: str = ""
    hardiness_min: str = ""
    hardiness_max: str = ""
    description: str = ""
    detail_error: str = ""
    raw_search: dict[str, Any] = field(default_factory=dict)
    raw_details: dict[str, Any] = field(default_factory=dict)

    @property
    def scientific_name_text(self) -> str:
        return ", ".join(self.scientific_name) if self.scientific_name else "Not listed"

    @property
    def other_names_text(self) -> str:
        return ", ".join(self.other_names) if self.other_names else "Not listed"


@dataclass
class MatchAssessment:
    score: int
    label: str
    status: str
    reasons: list[str] = field(default_factory=list)
    cautions: list[str] = field(default_factory=list)


@dataclass
class Recommendation:
    assessment: MatchAssessment
    watering_guidance: str
    care_guidance: str
    explanation: str
    retrieved_context: dict[str, Any]
