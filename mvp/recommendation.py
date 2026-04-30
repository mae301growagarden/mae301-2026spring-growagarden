"""Recommendation text built from live retrieved context."""

from __future__ import annotations

from typing import Any

from .matching import score_garden_match
from .models import GardenInputs, LocationResult, PlantMatch, Recommendation, WeatherResult


def generate_recommendation(
    inputs: GardenInputs,
    location: LocationResult,
    weather: WeatherResult,
    plant: PlantMatch,
) -> Recommendation:
    assessment = score_garden_match(inputs, plant, weather)
    watering_guidance = _watering_guidance(inputs, plant, weather)
    care_guidance = _care_guidance(inputs, plant)
    explanation = _grounded_explanation(inputs, location, weather, plant)
    context = build_retrieved_context(inputs, location, weather, plant)

    return Recommendation(
        assessment=assessment,
        watering_guidance=watering_guidance,
        care_guidance=care_guidance,
        explanation=explanation,
        retrieved_context=context,
    )


def build_retrieved_context(
    inputs: GardenInputs,
    location: LocationResult,
    weather: WeatherResult,
    plant: PlantMatch,
) -> dict[str, Any]:
    return {
        "user_inputs": {
            "location": inputs.location,
            "month": inputs.month,
            "garden_space": inputs.garden_space,
            "sun_exposure": inputs.sun_exposure,
            "water_access": inputs.water_access,
            "garden_type": inputs.garden_type,
            "usda_zone": inputs.usda_zone or "not provided",
            "plant_query": inputs.plant_query,
        },
        "open_meteo": {
            "resolved_location": location.display_name,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "timezone": location.timezone,
            "current_temperature": weather.current_temperature,
            "current_humidity": weather.current_humidity,
            "current_precipitation": weather.current_precipitation,
            "forecast_summary": weather.forecast_summary(),
        },
        "perenual": {
            "plant_id": plant.plant_id,
            "common_name": plant.common_name,
            "scientific_name": plant.scientific_name,
            "other_names": plant.other_names,
            "sunlight": plant.sunlight,
            "watering": plant.watering,
            "cycle": plant.cycle,
            "care_level": plant.care_level,
            "hardiness_range": _hardiness_text(plant),
            "detail_note": plant.detail_error or "details retrieved",
        },
    }


def _watering_guidance(inputs: GardenInputs, plant: PlantMatch, weather: WeatherResult) -> str:
    base = plant.watering or "not specified"
    rain = weather.current_precipitation
    humidity = weather.current_humidity

    guidance = f"Perenual lists watering as '{base}'. For {inputs.garden_type} gardening with {inputs.water_access} water access, start with that baseline and check soil moisture before adding more water."

    if rain is not None and rain > 0:
        guidance += " Because Open-Meteo currently reports precipitation, reduce watering today unless the soil is still dry."
    elif humidity is not None and humidity < 30:
        guidance += " Current humidity is low, so containers and raised beds may dry out faster."

    if inputs.garden_type == "container":
        guidance += " Containers need drainage holes and more frequent soil checks than in-ground beds."

    return guidance


def _care_guidance(inputs: GardenInputs, plant: PlantMatch) -> str:
    sunlight = ", ".join(plant.sunlight) if plant.sunlight else "not specified"
    care = plant.care_level or "not specified"
    cycle = plant.cycle or "not specified"

    guidance = (
        f"Plan around the plant's listed sunlight ({sunlight}), care level ({care}), and cycle ({cycle}). "
        f"For a {inputs.garden_space} {inputs.garden_type}, leave enough room for airflow and keep the planting area easy to reach."
    )

    if inputs.usda_zone and plant.hardiness_min and plant.hardiness_max:
        guidance += f" Compare your USDA zone {inputs.usda_zone} with the retrieved hardiness range {plant.hardiness_min}-{plant.hardiness_max} before planting outdoors."

    return guidance


def _grounded_explanation(
    inputs: GardenInputs,
    location: LocationResult,
    weather: WeatherResult,
    plant: PlantMatch,
) -> str:
    temp = _format_value(weather.current_temperature, weather.temperature_unit)
    humidity = _format_value(weather.current_humidity, weather.humidity_unit)
    precipitation = _format_value(weather.current_precipitation, weather.precipitation_unit)
    sunlight = ", ".join(plant.sunlight) if plant.sunlight else "not listed"

    return (
        f"This recommendation combines the location resolved by Open-Meteo ({location.display_name}), "
        f"the current weather ({temp}, {humidity} humidity, {precipitation} precipitation), "
        f"and Perenual plant data for {plant.common_name}. Perenual lists sunlight as {sunlight} "
        f"and watering as {plant.watering or 'not listed'}, so the match is judged against your "
        f"{inputs.sun_exposure}, {inputs.water_access} water access, {inputs.garden_space} space, "
        f"and {inputs.garden_type} setup for {inputs.month}."
    )


def _format_value(value: float | None, unit: str) -> str:
    if value is None:
        return "not returned"
    return f"{value:.0f}{unit}" if unit in {"F", "C", "%", "degC"} else f"{value:.2f} {unit}"


def _hardiness_text(plant: PlantMatch) -> str:
    if plant.hardiness_min and plant.hardiness_max:
        return f"{plant.hardiness_min}-{plant.hardiness_max}"
    return "not listed"
