"""Live data retrieval for Open-Meteo and Perenual."""

from __future__ import annotations

import os
from typing import Any

import requests

from .errors import ApiRequestError, LocationLookupError, MissingApiKeyError, PlantLookupError
from .models import ForecastDay, LocationResult, PlantMatch, WeatherResult

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - app still works if dotenv is not installed
    load_dotenv = None


OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
PERENUAL_SEARCH_URL = "https://perenual.com/api/species-list"
PERENUAL_DETAILS_URL = "https://perenual.com/api/species/details/{plant_id}"
REQUEST_TIMEOUT_SECONDS = 15
US_STATE_ABBREVIATIONS = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "DC": "District of Columbia",
}


def load_environment() -> None:
    if load_dotenv is not None:
        load_dotenv()


def get_perenual_api_key(api_key: str | None = None) -> str:
    load_environment()
    key = (api_key or os.getenv("PERENUAL_API_KEY") or "").strip()
    if not key:
        raise MissingApiKeyError(
            "Missing Perenual API key. Set PERENUAL_API_KEY in your environment or in a .env file."
        )
    return key


def _get_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    safe_params = dict(params)
    if "key" in safe_params:
        safe_params["key"] = "***"

    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise ApiRequestError(f"API request failed with status {status}: {url}") from None
    except requests.exceptions.RequestException as exc:
        error_name = exc.__class__.__name__
        raise ApiRequestError(f"Network error while contacting {url}: {error_name}") from None

    try:
        payload = response.json()
    except ValueError as exc:
        raise ApiRequestError(f"API returned non-JSON data for {url} with params {safe_params}.") from None

    if not isinstance(payload, dict):
        raise ApiRequestError(f"API returned unexpected data for {url}.")

    return payload


def resolve_location(location_query: str) -> LocationResult:
    query = location_query.strip()
    if not query:
        raise LocationLookupError("Please enter a location before searching.")

    results = _lookup_location_candidates(query)
    region_hint = _location_region_hint(query)
    if not results:
        raise LocationLookupError(
            f"Open-Meteo could not find a location for '{location_query}'. Try a nearby city or ZIP code."
        )

    match = _choose_location_result(results, region_hint)
    try:
        return LocationResult(
            name=str(match.get("name") or query),
            latitude=float(match["latitude"]),
            longitude=float(match["longitude"]),
            country=str(match.get("country") or ""),
            admin1=str(match.get("admin1") or ""),
            timezone=str(match.get("timezone") or ""),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ApiRequestError("Open-Meteo returned an incomplete location result.") from exc


def _lookup_location_candidates(query: str) -> list[dict[str, Any]]:
    search_terms = [query]
    if "," in query:
        city_part = query.split(",", 1)[0].strip()
        if city_part and city_part not in search_terms:
            search_terms.append(city_part)

    for term in search_terms:
        payload = _get_json(
            OPEN_METEO_GEOCODING_URL,
            {
                "name": term,
                "count": 10,
                "language": "en",
                "format": "json",
            },
        )
        results = payload.get("results") or []
        if results:
            return results

    return []


def _location_region_hint(query: str) -> str:
    if "," not in query:
        return ""

    hint = query.split(",", 1)[1].strip()
    if not hint:
        return ""

    return US_STATE_ABBREVIATIONS.get(hint.upper(), hint)


def _choose_location_result(results: list[dict[str, Any]], region_hint: str) -> dict[str, Any]:
    if not region_hint:
        return results[0]

    normalized_hint = region_hint.lower()
    for result in results:
        admin1 = str(result.get("admin1") or "").lower()
        country = str(result.get("country") or "").lower()
        country_code = str(result.get("country_code") or "").lower()
        if normalized_hint in {admin1, country, country_code}:
            return result

    for result in results:
        admin1 = str(result.get("admin1") or "").lower()
        if normalized_hint and normalized_hint in admin1:
            return result

    return results[0]


def fetch_weather(location: LocationResult) -> WeatherResult:
    payload = _get_json(
        OPEN_METEO_FORECAST_URL,
        {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "inch",
            "forecast_days": 3,
            "timezone": "auto",
        },
    )

    current = payload.get("current") or {}
    current_units = payload.get("current_units") or {}
    daily = payload.get("daily") or {}
    daily_units = payload.get("daily_units") or {}

    forecast: list[ForecastDay] = []
    for index, date in enumerate(daily.get("time") or []):
        forecast.append(
            ForecastDay(
                date=str(date),
                temp_max=_list_value(daily.get("temperature_2m_max"), index),
                temp_min=_list_value(daily.get("temperature_2m_min"), index),
                precipitation_sum=_list_value(daily.get("precipitation_sum"), index),
            )
        )

    return WeatherResult(
        current_temperature=_number_or_none(current.get("temperature_2m")),
        current_humidity=_number_or_none(current.get("relative_humidity_2m")),
        current_precipitation=_number_or_none(current.get("precipitation")),
        temperature_unit=str(current_units.get("temperature_2m") or daily_units.get("temperature_2m_max") or "F"),
        humidity_unit=str(current_units.get("relative_humidity_2m") or "%"),
        precipitation_unit=str(current_units.get("precipitation") or daily_units.get("precipitation_sum") or "inch"),
        forecast=forecast,
        raw=payload,
    )


def fetch_plant_match(plant_query: str, api_key: str | None = None) -> PlantMatch:
    query = plant_query.strip()
    if not query:
        raise PlantLookupError("Please enter a plant name before searching.")

    key = get_perenual_api_key(api_key)
    search_payload = _get_json(PERENUAL_SEARCH_URL, {"key": key, "q": query})
    matches = search_payload.get("data") or []
    if not matches:
        raise PlantLookupError(f"Perenual did not find a plant match for '{plant_query}'. Try a common plant name.")

    search_match = _choose_plant_search_result(matches, query)
    plant_id = search_match.get("id")
    if plant_id is None:
        raise ApiRequestError("Perenual returned a plant match without an ID.")

    try:
        details_payload = _get_json(PERENUAL_DETAILS_URL.format(plant_id=plant_id), {"key": key})
        return _plant_match_from_payload(search_match, details_payload)
    except ApiRequestError as exc:
        plant = _plant_match_from_payload(search_match, {})
        plant.detail_error = str(exc)
        plant.raw_details = {"detail_error": str(exc)}
        return plant


def retrieve_live_context(location_query: str, plant_query: str, api_key: str | None = None) -> tuple[LocationResult, WeatherResult, PlantMatch]:
    location = resolve_location(location_query)
    weather = fetch_weather(location)
    plant = fetch_plant_match(plant_query, api_key=api_key)
    return location, weather, plant


def _plant_match_from_payload(search_match: dict[str, Any], details: dict[str, Any]) -> PlantMatch:
    merged = {**search_match, **details}
    hardiness = merged.get("hardiness") or {}

    return PlantMatch(
        plant_id=_int_or_none(merged.get("id")),
        common_name=str(merged.get("common_name") or "Unknown plant"),
        scientific_name=_clean_string_list(merged.get("scientific_name")),
        other_names=_clean_string_list(merged.get("other_name") or merged.get("other_names")),
        sunlight=_clean_string_list(merged.get("sunlight")),
        watering=str(merged.get("watering") or ""),
        cycle=str(merged.get("cycle") or ""),
        care_level=str(merged.get("care_level") or ""),
        hardiness_min=str(hardiness.get("min") or ""),
        hardiness_max=str(hardiness.get("max") or ""),
        description=str(merged.get("description") or ""),
        raw_search=search_match,
        raw_details=details,
    )


def _choose_plant_search_result(matches: list[dict[str, Any]], query: str) -> dict[str, Any]:
    normalized_query = query.strip().lower()

    def score(match: dict[str, Any]) -> int:
        common_name = str(match.get("common_name") or "").lower()
        scientific_names = _clean_string_list(match.get("scientific_name"))
        other_names = _clean_string_list(match.get("other_name") or match.get("other_names"))
        all_names = [common_name, *[name.lower() for name in scientific_names], *[name.lower() for name in other_names]]

        if common_name == normalized_query:
            return 100
        if normalized_query in common_name:
            return 80
        if any(name == normalized_query for name in all_names):
            return 70
        if any(normalized_query in name for name in all_names):
            return 55
        return 10

    return max(matches, key=score)


def _clean_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        values = [str(value)]

    cleaned: list[str] = []
    for item in values:
        text = str(item).strip()
        if text and text.lower() != "null":
            cleaned.append(text)
    return cleaned


def _list_value(values: Any, index: int) -> float | None:
    if not isinstance(values, list) or index >= len(values):
        return None
    return _number_or_none(values[index])


def _number_or_none(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None
