"""Streamlit UI for Grow A Garden: AI Garden Planning Assistant."""

from __future__ import annotations

import json
from datetime import datetime
from html import escape

import streamlit as st

from garden_planner.errors import (
    ApiRequestError,
    GardenPlannerError,
    InputValidationError,
    LocationLookupError,
    MissingApiKeyError,
    PlantLookupError,
)
from garden_planner.models import GardenInputs, PlantMatch, Recommendation, WeatherResult
from garden_planner.recommendation import generate_recommendation
from garden_planner.retrieval import retrieve_live_context


MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def main() -> None:
    st.set_page_config(
        page_title="Grow A Garden",
        page_icon=":seedling:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_styles()
    render_header()
    submitted_inputs = render_sidebar_form()

    if submitted_inputs is None:
        render_welcome_state()
        return

    try:
        submitted_inputs.validate()
    except InputValidationError as exc:
        st.warning(str(exc))
        return

    with st.spinner("Retrieving live location, weather, and plant data..."):
        try:
            location, weather, plant = retrieve_live_context(
                submitted_inputs.location,
                submitted_inputs.plant_query,
            )
            recommendation = generate_recommendation(submitted_inputs, location, weather, plant)
        except MissingApiKeyError as exc:
            st.error(str(exc))
            st.info("Create a Perenual API key, then set PERENUAL_API_KEY before running the app.")
            return
        except LocationLookupError as exc:
            st.error(str(exc))
            return
        except PlantLookupError as exc:
            st.error(str(exc))
            return
        except ApiRequestError as exc:
            st.error("A live data request failed. Please check your internet connection and try again.")
            st.caption(str(exc))
            return
        except GardenPlannerError as exc:
            st.error(str(exc))
            return

    render_results(location.display_name, weather, plant, recommendation)


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <p class="eyebrow">Live AI MVP demo</p>
            <h1>Grow A Garden</h1>
            <p class="hero-copy">
                An AI garden planning assistant that combines location lookup, live weather,
                short-term forecast data, and plant details to create grounded recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_form() -> GardenInputs | None:
    current_month = MONTHS[datetime.now().month - 1]
    with st.sidebar:
        st.header("Garden Inputs")
        st.caption("Enter a location and the conditions for the garden you want to plan.")

        with st.form("garden_form"):
            location = st.text_input("Location", placeholder="Phoenix, AZ")
            month = st.selectbox("Current month", MONTHS, index=MONTHS.index(current_month))
            garden_space = st.radio("Garden space", ["small", "medium", "large"], horizontal=True)
            sun_exposure = st.selectbox("Sun exposure", ["full sun", "partial sun", "shade"])
            water_access = st.selectbox("Water access", ["low", "moderate", "high"], index=1)
            garden_type = st.selectbox("Garden type", ["backyard bed", "raised bed", "container"], index=1)
            usda_zone = st.text_input("USDA hardiness zone (optional)", placeholder="9b")
            plant_query = st.text_input("Plant query", placeholder="tomato")

            submitted = st.form_submit_button("Generate Recommendation", type="primary", use_container_width=True)

        if not submitted:
            return None

        return GardenInputs(
            location=location,
            month=month,
            garden_space=garden_space,
            sun_exposure=sun_exposure,
            water_access=water_access,
            garden_type=garden_type,
            usda_zone=usda_zone,
            plant_query=plant_query,
        )


def render_welcome_state() -> None:
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Plan with live retrieved context")
        st.write(
            "Use the sidebar to enter your location, growing conditions, and a plant search. "
            "The app will resolve the location with Open-Meteo, retrieve current weather and forecast data, "
            "search Perenual for the plant, and produce a recommendation grounded in those results."
        )
    with right:
        st.markdown(
            """
            <div class="card">
                <h3>Demo flow</h3>
                <p>1. Resolve location</p>
                <p>2. Fetch live weather</p>
                <p>3. Retrieve plant data</p>
                <p>4. Generate recommendation</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_results(
    resolved_location: str,
    weather: WeatherResult,
    plant: PlantMatch,
    recommendation: Recommendation,
) -> None:
    st.markdown("### Plant Match")
    if plant.detail_error:
        st.warning(
            "Perenual plant search succeeded, but the detail endpoint was limited or unavailable. "
            "The recommendation is using the live search result plus any detail fields that were returned."
        )
    col1, col2, col3 = st.columns(3)
    col1.markdown(card_html("Common name", plant.common_name), unsafe_allow_html=True)
    col2.markdown(card_html("Scientific name", plant.scientific_name_text), unsafe_allow_html=True)
    col3.markdown(card_html("Other names", plant.other_names_text), unsafe_allow_html=True)

    st.markdown("### Live Location And Weather")
    st.markdown(
        f"<div class='source-pill'>Resolved by Open-Meteo: {html_text(resolved_location)}</div>",
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(3)
    metric_cols[0].metric("Current temperature", metric_text(weather.current_temperature, weather.temperature_unit))
    metric_cols[1].metric("Current humidity", metric_text(weather.current_humidity, weather.humidity_unit, decimals=0))
    metric_cols[2].metric("Current precipitation", metric_text(weather.current_precipitation, weather.precipitation_unit))

    st.markdown(
        f"""
        <div class="card wide-card">
            <h3>Short-term forecast</h3>
            <p>{html_text(weather.forecast_summary())}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Recommendation")
    status_class = f"badge-{recommendation.assessment.status}"
    st.markdown(
        f"""
        <div class="recommendation-card">
            <span class="badge {status_class}">{recommendation.assessment.label}</span>
            <span class="score">{recommendation.assessment.score}/100 suitability</span>
            <p>{html_text(recommendation.explanation)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    guidance_cols = st.columns(2)
    with guidance_cols[0]:
        st.markdown(card_html("Watering guidance", recommendation.watering_guidance), unsafe_allow_html=True)
    with guidance_cols[1]:
        st.markdown(card_html("Care guidance", recommendation.care_guidance), unsafe_allow_html=True)

    render_assessment_details(recommendation)
    render_source_transparency(recommendation)


def render_assessment_details(recommendation: Recommendation) -> None:
    detail_cols = st.columns(2)
    with detail_cols[0]:
        st.markdown("#### Positive Signals")
        if recommendation.assessment.reasons:
            for reason in recommendation.assessment.reasons:
                st.success(reason)
        else:
            st.info("No strong positive signals were available from the retrieved data.")

    with detail_cols[1]:
        st.markdown("#### Planning Notes")
        if recommendation.assessment.cautions:
            for caution in recommendation.assessment.cautions:
                st.warning(caution)
        else:
            st.success("No major cautions were identified from the retrieved data.")


def render_source_transparency(recommendation: Recommendation) -> None:
    st.markdown("### Source Transparency")
    st.info("Open-Meteo provides location, current weather, and forecast data. Perenual provides plant search and plant detail data.")

    context = recommendation.retrieved_context
    source_cols = st.columns(2)
    with source_cols[0]:
        st.markdown("#### Open-Meteo Context")
        st.code(json.dumps(context["open_meteo"], indent=2), language="json")
    with source_cols[1]:
        st.markdown("#### Perenual Context")
        st.code(json.dumps(context["perenual"], indent=2), language="json")

    with st.expander("Retrieved context used for recommendation"):
        st.code(json.dumps(context, indent=2), language="json")


def card_html(title: str, body: str) -> str:
    return f"""
    <div class="card">
        <p class="card-label">{html_text(title)}</p>
        <p class="card-value">{html_text(body)}</p>
    </div>
    """


def html_text(value: object) -> str:
    return escape(str(value), quote=True)


def metric_text(value: float | None, unit: str, decimals: int = 1) -> str:
    if value is None:
        return "Not returned"
    if decimals == 0:
        return f"{value:.0f}{unit}"
    return f"{value:.{decimals}f} {unit}"


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --garden-bg: #000000;
            --garden-panel: #111111;
            --garden-panel-2: #181818;
            --garden-border: #3a3a3a;
            --garden-text: #ffffff;
            --garden-muted: #d6d6d6;
            --garden-accent: #7ddc8f;
            --garden-accent-2: #9ddcff;
        }
        .stApp {
            background: var(--garden-bg);
            color: var(--garden-text);
        }
        .block-container {
            max-width: 1120px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3, h4, h5, h6,
        p, li, label, span,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] p,
        [data-testid="stCaptionContainer"],
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"] {
            color: var(--garden-text) !important;
        }
        [data-testid="stCaptionContainer"],
        .stCaption,
        small {
            color: var(--garden-muted) !important;
        }
        .hero {
            background: #0d0d0d;
            border: 1px solid var(--garden-border);
            border-radius: 8px;
            padding: 1.5rem 1.7rem;
            margin-bottom: 1.5rem;
        }
        .eyebrow {
            color: var(--garden-accent) !important;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0;
            margin: 0 0 0.2rem 0;
            text-transform: uppercase;
        }
        .hero h1 {
            color: var(--garden-text) !important;
            font-size: 2.8rem;
            line-height: 1.05;
            margin: 0;
            letter-spacing: 0;
        }
        .hero-copy {
            color: var(--garden-muted) !important;
            max-width: 760px;
            font-size: 1.05rem;
            margin: 0.7rem 0 0 0;
        }
        .card,
        .recommendation-card {
            background: var(--garden-panel);
            border: 1px solid var(--garden-border);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: none;
            min-height: 116px;
        }
        .wide-card {
            min-height: auto;
            margin-top: 0.8rem;
        }
        .card h3,
        .wide-card h3 {
            color: var(--garden-text) !important;
            font-size: 1.05rem;
            margin: 0 0 0.5rem 0;
        }
        .card p {
            margin: 0.35rem 0;
        }
        .card-label {
            color: var(--garden-accent) !important;
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        .card-value {
            color: var(--garden-text) !important;
            font-size: 1rem;
            line-height: 1.45;
            overflow-wrap: anywhere;
        }
        .source-pill {
            display: inline-block;
            background: #0c2433;
            border: 1px solid #2d6f94;
            border-radius: 999px;
            color: #ffffff !important;
            font-weight: 600;
            padding: 0.35rem 0.7rem;
            margin-bottom: 0.8rem;
        }
        .recommendation-card {
            min-height: auto;
            margin-bottom: 1rem;
        }
        .badge {
            border-radius: 999px;
            display: inline-block;
            font-weight: 800;
            padding: 0.3rem 0.7rem;
            margin-right: 0.6rem;
        }
        .badge-strong {
            background: #165a2a;
            color: #ffffff;
        }
        .badge-good {
            background: #11577a;
            color: #ffffff;
        }
        .badge-caution {
            background: #7a4f00;
            color: #ffffff;
        }
        .badge-poor {
            background: #7f1d1d;
            color: #ffffff;
        }
        .score {
            color: var(--garden-muted) !important;
            font-weight: 700;
        }
        div[data-testid="stMetric"] {
            background: var(--garden-panel);
            border: 1px solid var(--garden-border);
            border-radius: 8px;
            padding: 0.8rem 1rem;
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] div {
            color: var(--garden-text) !important;
        }
        section[data-testid="stSidebar"] {
            background: #050505;
            border-right: 1px solid var(--garden-border);
        }
        section[data-testid="stSidebar"] * {
            color: var(--garden-text) !important;
        }
        div[data-baseweb="input"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        input,
        textarea {
            background-color: var(--garden-panel-2) !important;
            color: var(--garden-text) !important;
            border-color: var(--garden-border) !important;
        }
        input::placeholder,
        textarea::placeholder {
            color: #bdbdbd !important;
            opacity: 1 !important;
        }
        [role="radiogroup"] label,
        [role="radiogroup"] span,
        [data-testid="stSelectbox"] *,
        [data-testid="stTextInput"] *,
        [data-testid="stRadio"] * {
            color: var(--garden-text) !important;
        }
        button[kind="primary"],
        div[data-testid="stFormSubmitButton"] button {
            background: var(--garden-accent) !important;
            color: #000000 !important;
            border: 1px solid var(--garden-accent) !important;
            font-weight: 800 !important;
        }
        button,
        [data-testid="stBaseButton-secondary"] {
            color: var(--garden-text) !important;
            border-color: var(--garden-border) !important;
        }
        .stAlert {
            background: var(--garden-panel) !important;
            color: var(--garden-text) !important;
            border: 1px solid var(--garden-border) !important;
        }
        .stAlert * {
            color: var(--garden-text) !important;
        }
        pre,
        code,
        [data-testid="stCodeBlock"] {
            background: #0b0b0b !important;
            color: #ffffff !important;
            border-color: var(--garden-border) !important;
        }
        details,
        [data-testid="stExpander"] {
            background: var(--garden-panel) !important;
            border-color: var(--garden-border) !important;
            color: var(--garden-text) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
