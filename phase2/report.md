# Phase 2 MVP Progress Report
## Grow A Garden: AI Garden Planning Assistant

## 1. Objective and Current MVP Definition

### Minimum Viable Product
Our MVP for this course is a working chatbot assistant that can:

1. Accept basic user inputs such as:
   - location
   - current season or month
   - available garden space
   - plant of interest

2. Return personalized gardening guidance including:
   - whether the plant is appropriate for the user’s region and season
   - a basic watering schedule
   - planting guidance and expected growing conditions
   - an explanation for why the recommendation was made

### Technical Risks
- Inaccurate recommendations due to insufficient datasets
- Holes in datasets that lack the specific crops a user wants to plant
- Generic advice that could be provided to the user by an LLM

## What Has Been Built So Far

At this stage, we have built a prototype workflow for generating gardening advice from user inputs.

### Current Prototype

#### A. User Input Structure
We defined a clear input schema for the assistant:
- user location or USDA hardiness zone
- current month or season
- plot size or available space
- plant/crop of interest
- optional notes such as “container garden” or “limited sun”

This gives the model more structured information than a freeform gardening question.

#### B. Gardening Knowledge Context
We assembled a small initial knowledge base from:
- USDA plant hardiness zone information
- public gardening guides
- plant care information such as water needs, planting seasons, and temperature ranges
- sample agricultural datasets from Kaggle

This knowledge was not used as a full production-grade retrieval system yet, but it was used to create a structured context prompt for the model.

#### C. Prompted Recommendation Workflow
We developed a prompt structure that asks the model to:
1. interpret the user’s location and season
2. determine whether the crop is suitable
3. provide watering and planting advice
4. explain the reason for the recommendation
5. mention uncertainties when the data is limited

This is better than a simple open-ended prompt because it enforces a more useful output structure.

#### D. Initial Test Scenarios
We prepared a set of representative user cases to test output quality, such as:
- lettuce in Arizona in April
- tomatoes in a hot region in midsummer
- carrots in a small raised bed in spring
- herbs in containers with partial sun

## What does not work yet
- responses were often generic and allows user to enter specific and broad locations (city/state)
- responses do not yet pull from external data
- recommendations are not detailed enough to be unique from regular LLMs
- the agent needs to have more capabilities such as creating specific plans and larger crop datasets
- explanations were not always tied to the user’s growing conditions


## Phase 3 Plans


1. building a cleaner and more reliable gardening knowledge source
2. improving how the system maps user location to relevant growing conditions
3. defining a repeatable evaluation process
4. deciding whether the final MVP should remain prompt-based or include retrieval and external data lookup


### Planned Next Steps
1. Expand the gardening knowledge base by cleaning and organizing plant data and defining fields such as watering needs, temperature range, planting window, and sunlight needs

2. Add a retrieval or lookup layer in order to pull plant-specific information before generation and reduce hallucinations

3. Improve input handling by standardizing user profiles and better supporting season and garden type

4. Build a minimal user interface such as a command-line demo, notebook interface, or lightweight web app



