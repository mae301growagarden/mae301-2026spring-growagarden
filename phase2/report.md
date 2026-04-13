# Phase 2 MVP Progress Report

## Grow A Garden: AI Garden Planning Assistant

---

## 1. Objective and Current MVP Definition

### Minimum Viable Product

Our MVP for this course is a working system that allows a user to:

1. Input gardening conditions such as:

   * USDA hardiness zone or location
   * current date or season
   * available garden space
   * sunlight and watering preference

2. Receive:

   * crop recommendations suited to their conditions
   * a structured weekly watering and planting schedule
   * explanations for why those recommendations were made

---

## 2. What Has Been Built So Far

At this stage, we have developed two working prototype systems that together demonstrate our MVP progress.

### A. Recommendation-Focused System (Primary Demo)

This system generates crop recommendations based on user inputs such as zone, sunlight, and watering preferences.

Capabilities:

* Uses a small, partially structured dataset and prompt-based logic
* Filters crops by approximate seasonal planting windows
* Matches crops to user constraints (sun, water, timing)
* Outputs recommendations with explanations

Limitations:

* **Does not reliably pull from structured datasets at runtime**
* Relies heavily on prompt-based reasoning (LLM-style)
* Limited dataset coverage leads to more generic outputs

This is our **primary MVP feature** because it directly answers the core user question: *"What should I plant right now?"*

---

### B. Scheduling-Focused System (Secondary Prototype)

This system focuses on generating an **8-week gardening schedule** based on selected crops.

Capabilities:

* Uses structured crop datasets
* Creates weekly planting and watering tasks
* Estimates irrigation needs
* Outputs structured schedules (tables, CSV, markdown)

This prototype demonstrates stronger use of datasets, but is currently less refined in usability and presentation.

---

### C. Data and Knowledge Base

We assembled an initial dataset including:

* USDA hardiness zone data
* plant growing seasons and temperature ranges
* watering requirements
* spacing and time-to-maturity information
* public gardening datasets (e.g., Kaggle)

However, dataset integration is **inconsistent across systems**, and most data is sourced from the United States.

---

### D. Workflow

The current system pipeline:

1. Load and preprocess crop data (used mainly in scheduling system)
2. Interpret user inputs (zone, date, constraints)
3. Generate recommendations (partially prompt-based)
4. Generate a schedule based on selected crops
5. Output results as tables and markdown summaries

---

## 3. Technical Bottlenecks

* **Limited dataset integration**: The recommendation system does not fully utilize structured datasets
* **Limited dataset scope**: Most data is sourced from the United States, reducing generalizability
* Incomplete crop coverage and missing edge cases
* Lack of real-time or dynamic data integration

---

## 4. What Does Not Work Yet

* Recommendation system produces outputs that can feel generic
* Weak connection between recommendations and underlying data
* No unified pipeline combining recommendation + scheduling
* Scheduling output is functional but not visually refined
* Limited personalization beyond basic inputs

---

## 5. Key Areas for Improvement

* **Combine the two demo systems** into a single, unified workflow
* Improve dataset usage in the recommendation system
* Improve the **layout and readability** of the scheduling output
* Expand dataset coverage beyond U.S.-based data
* Improve explanation quality to better reflect user-specific conditions

---

## 6. Evidence of Progress

We successfully built:

* A recommendation prototype (prompt-based)
* A dataset-driven scheduling system
* A reproducible demo in Google Colab
* Exportable outputs (CSV and markdown)

These components demonstrate meaningful technical progress and iteration toward a functional AI gardening assistant.

---

## 7. Phase 3 Plans

### Planned Next Steps

1. Integrate structured datasets directly into the recommendation system

2. Combine recommendation + scheduling into one system

3. Expand and improve the dataset:

   * add more crops and regions
   * clean and standardize data fields

4. Add a retrieval or lookup layer to reduce generic outputs

5. Improve input handling and user personalization

6. Build a simple user interface (Colab, CLI, or web app)

