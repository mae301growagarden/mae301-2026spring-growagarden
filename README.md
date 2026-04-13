# Grow A Garden – Phase 2 MVP

This folder contains our **Phase 2 MVP** for *Grow A Garden*, an AI-powered garden planning assistant.

The goal of this phase is to demonstrate a working prototype where:

> A user inputs their gardening conditions and receives **crop recommendations** and a **weekly watering schedule**.

---

## Demos

We built two versions of the system:

* **Recommendation-focused (main demo)**
  Suggests what crops to plant based on user inputs

* **Scheduling-focused (secondary)**
  Generates detailed weekly plans from selected crops

The recommendation system is used as the primary demo.

---

## How to Run

1. Download the `phase2` folder
2. Upload it to Google Drive
3. Open Google Colab
4. Mount your Drive:

   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
5. Run the demo script

Outputs will be saved in:

```text
artifacts/demo_run/
```

---
