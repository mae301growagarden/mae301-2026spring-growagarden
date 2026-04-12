def generate_garden_prompt(location, month, plant, garden_type="backyard bed"):
    return f"""
You are a gardening assistant for beginner gardeners.

User profile:
- Location: {location}
- Month: {month}
- Plant: {plant}
- Garden type: {garden_type}

Return:
1. Whether this plant is suitable right now
2. Watering guidance
3. Planting/care guidance
4. A short explanation of why
5. Any warnings or limitations
"""

if __name__ == "__main__":
    location = "Phoenix, AZ"
    month = "April"
    plant = "lettuce"
    print(generate_garden_prompt(location, month, plant))

