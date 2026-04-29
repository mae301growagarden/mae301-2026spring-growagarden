"""Simple plant-to-garden matching logic grounded in retrieved data."""

from __future__ import annotations

import re

from .models import GardenInputs, MatchAssessment, PlantMatch, WeatherResult


def score_garden_match(inputs: GardenInputs, plant: PlantMatch, weather: WeatherResult) -> MatchAssessment:
    score = 65
    reasons: list[str] = []
    cautions: list[str] = []

    score += _score_sun(inputs.sun_exposure, plant, reasons, cautions)
    score += _score_water(inputs.water_access, plant, reasons, cautions)
    score += _score_zone(inputs.usda_zone, plant, reasons, cautions)
    score += _score_weather(weather, reasons, cautions)
    score += _score_space(inputs, plant, reasons, cautions)

    score = max(0, min(100, score))
    label, status = _label_for_score(score)
    return MatchAssessment(score=score, label=label, status=status, reasons=reasons, cautions=cautions)


def _score_sun(user_sun: str, plant: PlantMatch, reasons: list[str], cautions: list[str]) -> int:
    if not plant.sunlight:
        cautions.append("Perenual did not list a sunlight preference, so sun fit is uncertain.")
        return 0

    plant_sun = " ".join(plant.sunlight).lower()
    user_sun = user_sun.lower()

    compatible_terms = {
        "full sun": ["full sun", "sun", "direct sun"],
        "partial sun": ["partial sun", "part sun", "part shade", "partial shade", "filtered shade"],
        "shade": ["shade", "full shade", "part shade", "partial shade"],
    }

    if any(term in plant_sun for term in compatible_terms.get(user_sun, [])):
        reasons.append(f"The plant sunlight listing matches your {user_sun} conditions.")
        return 15

    if user_sun == "partial sun" and "full sun" in plant_sun:
        cautions.append("This plant may want more direct light than a partial-sun site provides.")
        return -8

    cautions.append(f"The plant sunlight listing ({', '.join(plant.sunlight)}) may not match {user_sun}.")
    return -15


def _score_water(user_water: str, plant: PlantMatch, reasons: list[str], cautions: list[str]) -> int:
    plant_water = plant.watering.strip().lower()
    if not plant_water:
        cautions.append("Perenual did not list watering frequency, so watering fit is uncertain.")
        return 0

    user_water = user_water.lower()
    low_terms = ["minimum", "minimal", "low", "none"]
    moderate_terms = ["average", "moderate", "regular"]
    high_terms = ["frequent", "high", "daily"]

    if user_water == "low" and any(term in plant_water for term in low_terms):
        reasons.append("The plant's watering need appears compatible with low water access.")
        return 15
    if user_water == "moderate" and any(term in plant_water for term in moderate_terms):
        reasons.append("The plant's watering need appears compatible with moderate water access.")
        return 15
    if user_water == "high" and any(term in plant_water for term in high_terms + moderate_terms):
        reasons.append("Your water access should support the plant's watering needs.")
        return 12
    if user_water == "low" and any(term in plant_water for term in high_terms):
        cautions.append("This plant may need more frequent watering than your setup can easily provide.")
        return -20
    if user_water == "high" and any(term in plant_water for term in low_terms):
        cautions.append("Avoid overwatering; this plant appears to prefer a lighter watering schedule.")
        return -5

    cautions.append(f"Watering fit is mixed because Perenual lists watering as '{plant.watering}'.")
    return -5


def _score_zone(user_zone: str, plant: PlantMatch, reasons: list[str], cautions: list[str]) -> int:
    if not user_zone.strip():
        return 0

    zone = _zone_number(user_zone)
    min_zone = _zone_number(plant.hardiness_min)
    max_zone = _zone_number(plant.hardiness_max)
    if zone is None or min_zone is None or max_zone is None:
        cautions.append("Hardiness zone fit could not be confirmed from the retrieved plant data.")
        return 0

    if min_zone <= zone <= max_zone:
        reasons.append(f"Your USDA zone {user_zone.strip()} falls inside the listed hardiness range.")
        return 12

    cautions.append(
        f"Your USDA zone {user_zone.strip()} is outside the listed hardiness range {plant.hardiness_min}-{plant.hardiness_max}."
    )
    return -20


def _score_weather(weather: WeatherResult, reasons: list[str], cautions: list[str]) -> int:
    temp = weather.current_temperature
    if temp is None:
        cautions.append("Current temperature was not returned, so weather fit is incomplete.")
        return 0

    if temp < 32:
        cautions.append("Current conditions are freezing, so protect new plantings or wait to transplant.")
        return -12
    if temp > 95:
        cautions.append("Current conditions are very hot, so planting stress and watering needs may be higher.")
        return -8

    reasons.append("Current temperature looks workable for garden planning.")
    return 6


def _score_space(inputs: GardenInputs, plant: PlantMatch, reasons: list[str], cautions: list[str]) -> int:
    garden_type = inputs.garden_type.lower()
    space = inputs.garden_space.lower()

    if garden_type == "container" and "tree" in plant.cycle.lower():
        cautions.append("A container garden may be too limiting if this plant grows like a tree or large perennial.")
        return -10

    if garden_type == "container" and space == "small":
        cautions.append("For a small container setup, confirm mature size before buying the plant.")
        return -3

    reasons.append(f"A {space} {garden_type} setup can work if spacing and drainage are managed.")
    return 4


def _zone_number(zone_text: str) -> float | None:
    match = re.search(r"\d+(?:\.\d+)?", zone_text or "")
    if not match:
        return None
    try:
        return float(match.group())
    except ValueError:
        return None


def _label_for_score(score: int) -> tuple[str, str]:
    if score >= 82:
        return "Strong match", "strong"
    if score >= 62:
        return "Good match", "good"
    if score >= 42:
        return "Needs planning", "caution"
    return "Poor fit", "poor"

