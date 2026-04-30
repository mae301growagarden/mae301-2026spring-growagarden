## 1. Executive Summary

Grow A Garden is an AI-powered gardening assistant designed for beginner gardeners who want personalized help deciding what to plant and how to care for it. Many people are interested in growing their own food, but they often do not know which plants are suitable for their region, season, or garden conditions. Most online gardening advice is generic and requires users to search across multiple sources before they can make a decision.

Our MVP addresses this problem by combining live plant data, live weather data, and user-provided gardening conditions into one recommendation system. The product allows a user to enter their location, current month, garden size, sun exposure, water access, garden type, and optional USDA hardiness zone. The system then retrieves current weather and plant information and generates a recommendation about whether the plant is a good fit, how much water it may need, and what care considerations the user should keep in mind.

The MVP demonstrates a working live retrieval-based gardening assistant with a web interface. While it does not replace expert local gardening knowledge, it shows that an AI-assisted tool can reduce research effort and make gardening decisions more accessible for beginners.

## 2. User & Use Case

### Target User
The primary user is a beginner or casual gardener who has access to a backyard, raised bed, or container garden and wants help selecting plants and learning how to care for them. This user often has limited gardening knowledge and may not fully understand how season, climate, and plant needs interact.

### Persona
A typical user might be a student, homeowner, or renter who wants to grow vegetables or herbs to save money, eat healthier food, or live more sustainably. They are interested in gardening but feel overwhelmed by the amount of research required to get started.

### Use Case Narrative
A user in Phoenix wants to know if tomatoes are a good plant to grow in April in a raised bed with full sun and moderate water access. Instead of searching across many websites, they open Grow A Garden, enter their location and garden conditions, and ask about tomatoes. The system retrieves live weather data for Phoenix and live plant information for tomatoes, then generates a recommendation. The user sees whether the plant is suitable, what watering guidance to follow, and what environmental conditions they should pay attention to. The user can follow the simple and personalized plan given to them that adjusts to their personal conditions and current weather. This turns a complicated research process into one guided interaction.

## 3. System Design

The Grow A Garden MVP uses a retrieval-based workflow that combines live weather data, live plant information, and user gardening conditions to generate personalized recommendations. Instead of relying on a static chatbot response, the system retrieves current environmental and plant-specific context before producing its recommendation.

### High-Level Architecture

<img width="460" height="597" alt="image" src="https://github.com/user-attachments/assets/04bcb31b-882e-4245-abd1-8bde066bb888" />



---

## Section 4

## 4. Data

The MVP uses live data from external APIs rather than relying entirely on one static local dataset.

### Data Sources
- **Open-Meteo Geocoding API** for resolving user-entered locations into coordinates
- **Open-Meteo Forecast API** for current weather and short-term forecast data
- **Perenual Plant API** for plant search results and detailed plant records

### Data Used in the MVP
The system uses:
- location names and coordinates
- current temperature, humidity, and precipitation
- short-term weather forecast information
- plant common names and scientific names
- sunlight requirements
- watering categories and watering benchmarks
- care level and hardiness information
- general plant description fields

### Data Size
Since the MVP uses live APIs, the amount of data is dynamic and depends on the user’s query. For a typical request, the system retrieves:
- one location result
- one weather record plus short-term forecast data
- several plant search matches
- one plant detail record for the best-matched plant

### Data Cleaning and Processing
The MVP performs lightweight preprocessing by:
- normalizing location and plant query text
- selecting the best plant match from search results
- extracting the most relevant fields from the weather and plant responses
- structuring retrieved information into a consistent format for recommendation generation

### Data Splits
Traditional train, validation, and test splits are not used because this MVP is not a supervised learning system trained on a fixed dataset. Instead, the system is evaluated through scenario-based testing and qualitative output comparison.


## 5. Models

The current Grow A Garden MVP is best described as an agent-style retrieval system rather than a traditional trained machine learning model.

### Model Approach
The MVP uses a retrieval-augmented workflow that:
1. collects structured user input
2. retrieves live weather data
3. retrieves live plant data
4. combines that information into a recommendation
5. produces a contextual explanation for the user

### Workflow Strategy
The recommendation engine acts as the core reasoning layer of the system. It evaluates:
- whether the plant is suitable for the entered conditions
- whether watering needs align with weather and water access
- whether sunlight and garden type are compatible
- whether any cautions should be shown to the user

### Why This Qualifies as an AI-Enabled MVP
A basic lookup table could provide a fixed watering value for a plant, but it would not meaningfully combine live weather, plant traits, and user constraints into one recommendation. This MVP adds value by integrating multiple live inputs into a personalized response rather than returning a static rule-based output.

### Future Model Expansion
Although the current MVP does not use a fine-tuned nanoGPT or frontier language model in production, the architecture could later support an LLM layer on top of the retrieved context. That would improve the conversational quality and flexibility of the explanations while keeping the response grounded in live data.


## 6. Evaluation

The MVP was evaluated primarily through end-to-end testing and qualitative scenario analysis.

### Evaluation Criteria
The system was considered successful when it could:
- run without crashing
- correctly resolve the user’s location
- retrieve relevant plant data for common gardening queries
- generate a recommendation that reflects both weather and plant context
- provide a useful response in a reasonable amount of time

### Qualitative Evaluation
We tested the system using representative gardening scenarios, including:
- lettuce in Phoenix during spring
- tomatoes in warm climates with full sun
- herbs in a container garden
- plants with lower compatibility under shade or limited water access

Across these cases, the MVP produced more specific and useful outputs than generic gardening advice because it reflected live environmental conditions and plant-specific care information.

### Example Outcome
For a user asking about lettuce in a warm climate, the system can return:
- an assessment of whether lettuce is suitable for current conditions
- watering guidance informed by current weather
- caution notes related to heat stress or bolting
- an explanation grounded in retrieved weather and plant data

### Error Analysis
The most common issues observed were:
- ambiguous plant matches when multiple species have similar names
- incomplete detail records from the plant API
- reduced usefulness when the location is too vague or not resolved correctly
- recommendations that are still broad rather than expert-level local gardening advice

Overall, the MVP works well as a proof of concept, but the quality of the output still depends on the completeness and reliability of the live data sources.

## 7. Limitations & Risks

Although the MVP successfully demonstrates the concept, it still has several limitations and risks.

### Failure Modes
- The system may fail if the weather or plant API is unavailable.
- Some plant queries may return multiple possible matches.
- Some plant records may not include full care or watering details.
- Vague or incomplete location input may reduce accuracy.

### Data Limitations
- The system depends on third-party APIs, so output quality depends on external data quality.
- Some plants are better documented than others.
- General weather data may not fully reflect local microclimates, soil conditions, or shade patterns.

### Biases
- The system may perform better for common garden plants than for rare or specialized plants.
- Recommendations may reflect the strengths and weaknesses of the external plant database.

### Privacy Concerns
- The user enters location information, which is potentially sensitive.
- The MVP does not currently store accounts or long-term gardening history, which limits privacy risk.
- Future versions with saved plans or user profiles would require stronger privacy protections.

### Product Risk
Users may place too much trust in the recommendation, even though successful gardening also depends on factors the app cannot directly observe, such as pests, soil health, irrigation quality, and exact site conditions. The MVP should therefore be understood as a guidance tool, not as a guarantee.


## 8. Next Steps

With 2–3 more months of development, Grow A Garden could be improved significantly both technically and as a product.

### Technical Next Steps
1. Improve plant matching when multiple search results are similar.
2. Add fallback plant data sources so the system is not dependent on one provider.
3. Add an LLM-based explanation layer on top of the retrieved context.
4. Expand recommendations to include planting schedules, harvest timing, and companion planting.
5. Add stronger evaluation benchmarks across different locations and plant types.
6. Include clearer source citations in the recommendation output.

### Product Next Steps
1. Allow users to save their garden profile and preferred plants.
2. Generate full garden plans instead of only single-plant recommendations.
3. Add reminders for watering and planting tasks.
4. Improve the interface with more visual forecast and care summaries.
5. Make the app more mobile-friendly for use outside in the garden.

### Long-Term Vision
In a more advanced version, Grow A Garden could become a personalized gardening assistant that helps users decide what to plant, when to plant it, how to care for it, and how to adjust plans as weather conditions change.


