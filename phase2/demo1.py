#!/usr/bin/env python3
"""
Grow A Garden - AI Garden Planning Assistant
Standalone terminal chatbot prototype for MAE301 Phase 2 / Phase 3.

How it works:
- Collects user profile information (location/zone, month, space, sun, water access).
- Answers questions about plant suitability, watering, planting, and care.
- Uses a built-in knowledge base for a small set of common garden plants.
- Produces personalized, beginner-friendly responses.

Run:
    python grow_a_garden_chatbot.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import textwrap


MONTH_TO_SEASON = {
    "january": "winter",
    "february": "winter",
    "march": "spring",
    "april": "spring",
    "may": "spring",
    "june": "summer",
    "july": "summer",
    "august": "summer",
    "september": "fall",
    "october": "fall",
    "november": "fall",
    "december": "winter",
}

HOT_CLIMATE_KEYWORDS = {
    "phoenix", "arizona", "tucson", "las vegas", "nevada", "yuma",
    "hot", "desert", "zone 9", "zone 10", "zone 11"
}

COOL_CLIMATE_KEYWORDS = {
    "minnesota", "montana", "maine", "wisconsin", "vermont",
    "cold", "zone 3", "zone 4", "zone 5"
}


@dataclass
class Plant:
    name: str
    preferred_seasons: List[str]
    sunlight: str
    water_need: str
    watering_frequency: str
    space_type: str
    notes: str
    avoid_in_heat: bool = False
    does_well_in_heat: bool = False
    container_friendly: bool = False


PLANTS: Dict[str, Plant] = {
    "lettuce": Plant(
        name="lettuce",
        preferred_seasons=["spring", "fall", "winter"],
        sunlight="partial sun to full sun",
        water_need="moderate to high",
        watering_frequency="Keep the soil evenly moist. In mild weather, water about 3 to 4 times per week; in heat, check daily.",
        space_type="small to medium",
        notes="Lettuce is a cool-season crop. It grows best when temperatures stay relatively mild.",
        avoid_in_heat=True,
        container_friendly=True,
    ),
    "tomato": Plant(
        name="tomato",
        preferred_seasons=["spring", "summer"],
        sunlight="full sun",
        water_need="moderate to high",
        watering_frequency="Water deeply 2 to 3 times per week, increasing frequency during extreme heat or in containers.",
        space_type="medium to large",
        notes="Tomatoes need warm weather, consistent moisture, and strong sunlight.",
        does_well_in_heat=True,
        container_friendly=True,
    ),
    "basil": Plant(
        name="basil",
        preferred_seasons=["spring", "summer"],
        sunlight="full sun",
        water_need="moderate",
        watering_frequency="Water when the top inch of soil feels dry. Containers may need water every 1 to 2 days in warm weather.",
        space_type="small",
        notes="Basil grows well in warm weather and is well suited for small gardens and containers.",
        does_well_in_heat=True,
        container_friendly=True,
    ),
    "carrot": Plant(
        name="carrot",
        preferred_seasons=["spring", "fall", "winter"],
        sunlight="full sun",
        water_need="moderate",
        watering_frequency="Water enough to keep the soil consistently moist during germination, then about 1 inch per week.",
        space_type="small to medium",
        notes="Carrots prefer loose soil and milder temperatures.",
        avoid_in_heat=True,
        container_friendly=True,
    ),
    "pepper": Plant(
        name="pepper",
        preferred_seasons=["spring", "summer"],
        sunlight="full sun",
        water_need="moderate",
        watering_frequency="Water deeply 1 to 3 times per week depending on heat, soil drainage, and container use.",
        space_type="small to medium",
        notes="Peppers like warm conditions and steady sunlight.",
        does_well_in_heat=True,
        container_friendly=True,
    ),
    "spinach": Plant(
        name="spinach",
        preferred_seasons=["spring", "fall", "winter"],
        sunlight="partial sun to full sun",
        water_need="moderate",
        watering_frequency="Keep soil evenly moist. Water several times per week and monitor closely in warmer temperatures.",
        space_type="small to medium",
        notes="Spinach is a cool-season crop and can bolt quickly in hot weather.",
        avoid_in_heat=True,
        container_friendly=True,
    ),
    "cucumber": Plant(
        name="cucumber",
        preferred_seasons=["spring", "summer"],
        sunlight="full sun",
        water_need="high",
        watering_frequency="Water deeply 2 to 4 times per week. Increase during hot weather or when fruit is forming.",
        space_type="medium to large",
        notes="Cucumbers grow quickly and need warmth and steady moisture.",
        does_well_in_heat=True,
    ),
}


@dataclass
class UserProfile:
    location: str = ""
    month: str = ""
    garden_space: str = ""
    sun_exposure: str = ""
    water_access: str = ""
    garden_type: str = ""
    hardiness_zone: str = ""

    def season(self) -> str:
        return MONTH_TO_SEASON.get(self.month.lower().strip(), "unknown")

    def climate_hint(self) -> str:
        text = f"{self.location} {self.hardiness_zone}".lower()
        if any(keyword in text for keyword in HOT_CLIMATE_KEYWORDS):
            return "hot"
        if any(keyword in text for keyword in COOL_CLIMATE_KEYWORDS):
            return "cool"
        return "moderate"


def wrap(text: str) -> str:
    return textwrap.fill(text, width=90)


def normalize_plant_name(name: str) -> str:
    return name.strip().lower()


def ask_nonempty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter a value so I can personalize the recommendation.")


def collect_profile() -> UserProfile:
    print("\nWelcome to Grow A Garden!")
    print("I will ask a few questions so I can give more personalized plant advice.\n")

    profile = UserProfile(
        location=ask_nonempty("Location (city/state or region): "),
        month=ask_nonempty("Current month (for example: April): ").lower(),
        garden_space=ask_nonempty("Available garden space (small / medium / large): ").lower(),
        sun_exposure=ask_nonempty("Sun exposure (full sun / partial sun / shade): ").lower(),
        water_access=ask_nonempty("Water access (low / moderate / high): ").lower(),
        garden_type=ask_nonempty("Garden type (backyard bed / raised bed / container): ").lower(),
        hardiness_zone=input("USDA hardiness zone if known (optional): ").strip().lower(),
    )
    return profile


def suitability_score(plant: Plant, profile: UserProfile) -> Tuple[int, List[str]]:
    score = 0
    reasons: List[str] = []
    season = profile.season()
    climate = profile.climate_hint()

    if season in plant.preferred_seasons:
        score += 2
        reasons.append(f"{plant.name.title()} fits the current {season} growing season.")
    else:
        reasons.append(f"{plant.name.title()} is not usually a top choice for {season}.")

    if "container" in profile.garden_type and plant.container_friendly:
        score += 1
        reasons.append(f"{plant.name.title()} can work well in containers.")
    elif "container" in profile.garden_type and not plant.container_friendly:
        reasons.append(f"{plant.name.title()} is less ideal for containers than some other plants.")

    if profile.garden_space in plant.space_type:
        score += 1
        reasons.append(f"The plant size generally matches your {profile.garden_space} garden space.")

    if "full sun" in profile.sun_exposure and "full sun" in plant.sunlight:
        score += 1
        reasons.append("Your sunlight conditions are a good match.")
    elif "partial" in profile.sun_exposure and "partial" in plant.sunlight:
        score += 1
        reasons.append("Your partial sun conditions are a good match.")
    elif "shade" in profile.sun_exposure:
        reasons.append("Limited sunlight may reduce growth for many food crops.")

    if climate == "hot" and plant.avoid_in_heat:
        score -= 2
        reasons.append(f"{plant.name.title()} struggles in hotter conditions, especially later in the season.")
    elif climate == "hot" and plant.does_well_in_heat:
        score += 1
        reasons.append(f"{plant.name.title()} generally handles warm to hot weather fairly well.")
    elif climate == "cool" and plant.avoid_in_heat:
        score += 1
        reasons.append(f"Cooler conditions are generally favorable for {plant.name.title()}.")

    if profile.water_access == "low" and plant.water_need in {"high", "moderate to high"}:
        score -= 1
        reasons.append(f"{plant.name.title()} may be harder to maintain with limited watering.")
    elif profile.water_access in {"moderate", "high"}:
        score += 1
        reasons.append("Your water access should support regular plant care.")

    return score, reasons


def suitability_label(score: int) -> str:
    if score >= 4:
        return "Good fit"
    if score >= 2:
        return "Possible with attention"
    return "Not the best choice right now"


def generate_response(plant_name: str, profile: UserProfile) -> str:
    key = normalize_plant_name(plant_name)
    plant = PLANTS.get(key)

    if plant is None:
        available = ", ".join(sorted(p.title() for p in PLANTS))
        return wrap(
            f"I do not have detailed built-in data for '{plant_name}' yet. "
            f"Try one of these plants: {available}."
        )

    score, reasons = suitability_score(plant, profile)
    label = suitability_label(score)
    season = profile.season()
    climate = profile.climate_hint()

    climate_note = {
        "hot": "Your location appears to have a warmer climate, so heat stress and faster soil drying are important factors.",
        "cool": "Your location appears to have a cooler climate, so season length and frost timing are important factors.",
        "moderate": "Your location appears to have a moderate climate, so seasonal timing still matters, but extreme heat or cold may be less of an issue."
    }[climate]

    response = f"""
    Recommendation for {plant.name.title()}
    ----------------------------------------
    Overall suitability: {label}

    Why:
    - {' '.join(reasons)}

    Watering guidance:
    {plant.watering_frequency}

    Planting and care:
    - Preferred season(s): {', '.join(plant.preferred_seasons)}
    - Sun needs: {plant.sunlight}
    - Water need: {plant.water_need}
    - Notes: {plant.notes}

    Personalized context:
    - Your month/season: {profile.month.title()} / {season.title()}
    - Your garden type: {profile.garden_type}
    - Your space: {profile.garden_space}
    - Your sun exposure: {profile.sun_exposure}
    - {climate_note}

    Beginner tip:
    Start small and monitor the soil directly. If the top inch is dry, the plant likely needs water sooner, especially in containers or hot weather.
    """
    return wrap_multiline(response)


def wrap_multiline(text: str) -> str:
    lines = [line.rstrip() for line in text.strip().splitlines()]
    out_lines: List[str] = []
    for line in lines:
        if not line.strip():
            out_lines.append("")
        elif line.strip().startswith("- ") or line.strip().endswith(":") or set(line.strip()) == {"-"}:
            out_lines.append(line.strip())
        else:
            out_lines.append(textwrap.fill(line.strip(), width=90))
    return "\n".join(out_lines)


def print_help() -> None:
    print("\nCommands:")
    print("  ask <plant>     Get a recommendation for a plant")
    print("  profile         View your current gardening profile")
    print("  update          Re-enter your gardening profile")
    print("  plants          List available plants in the built-in dataset")
    print("  help            Show commands")
    print("  quit            Exit the chatbot\n")


def print_profile(profile: UserProfile) -> None:
    print("\nCurrent Gardening Profile")
    print("-------------------------")
    print(f"Location: {profile.location}")
    print(f"Month: {profile.month.title()}")
    print(f"Season: {profile.season().title()}")
    print(f"Garden space: {profile.garden_space}")
    print(f"Sun exposure: {profile.sun_exposure}")
    print(f"Water access: {profile.water_access}")
    print(f"Garden type: {profile.garden_type}")
    print(f"Hardiness zone: {profile.hardiness_zone or 'Not provided'}\n")


def main() -> None:
    profile = collect_profile()
    print_help()

    while True:
        user_input = input("Grow A Garden > ").strip()

        if not user_input:
            continue

        lowered = user_input.lower()

        if lowered in {"quit", "exit"}:
            print("Good luck with your garden!")
            break

        if lowered == "help":
            print_help()
            continue

        if lowered == "profile":
            print_profile(profile)
            continue

        if lowered == "update":
            profile = collect_profile()
            continue

        if lowered == "plants":
            print("\nAvailable plants:")
            for plant_name in sorted(PLANTS):
                print(f"- {plant_name.title()}")
            print()
            continue

        if lowered.startswith("ask "):
            plant_name = user_input[4:].strip()
            if not plant_name:
                print("Please type a plant name after 'ask'. Example: ask lettuce")
                continue
            print()
            print(generate_response(plant_name, profile))
            print()
            continue

        print("I did not understand that command. Type 'help' to see available commands.")


if __name__ == "__main__":
    main()

