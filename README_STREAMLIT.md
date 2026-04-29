# Grow A Garden Streamlit Demo

This folder contains the files needed to run and deploy the **Grow A Garden: AI Garden Planning Assistant** Streamlit demo.

## Files To Place In The GitHub Repo Root

```text
app.py
requirements.txt
.env.example
.gitignore
.streamlit/config.toml
garden_planner/
```

The app uses live retrieval from:

- Open-Meteo Geocoding API
- Open-Meteo Forecast API
- Perenual Plant API

## Run Locally

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Set your Perenual API key:

```bash
export PERENUAL_API_KEY="your_api_key_here"
```

On Windows PowerShell:

```powershell
$env:PERENUAL_API_KEY="your_api_key_here"
```

Run the app:

```bash
streamlit run app.py
```

## Deploy On Streamlit Community Cloud

1. Push these files to the root of the GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Create a new app from the GitHub repository.
4. Set the main file path to:

   ```text
   app.py
   ```

5. Add this secret in Streamlit Cloud:

   ```toml
   PERENUAL_API_KEY = "your_api_key_here"
   ```

6. Deploy.

Do not commit a real `.env` file or API key to GitHub.

## Demo Inputs

- Location: `Phoenix, AZ`
- Current month: `April`
- Garden space: `medium`
- Sun exposure: `full sun`
- Water access: `moderate`
- Garden type: `raised bed`
- USDA hardiness zone: `9b`
- Plant query: `tomato`

