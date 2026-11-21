"""Global education explorer and transparent ML research workspace."""
from __future__ import annotations

import json
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

from .modeling import ARTIFACTS, run_experiment

WORLD_BANK_INDICATORS = {
    "Adult literacy (ages 15+)": ("SE.ADT.LITR.ZS", "Percent of people ages 15 and above"),
    "Secondary school enrolment": ("SE.SEC.ENRR", "Gross enrolment ratio; may exceed 100%"),
    "Tertiary education enrolment": ("SE.TER.ENRR", "Gross enrolment ratio; may exceed 100%"),
    "Primary school enrolment": ("SE.PRM.ENRR", "Gross enrolment ratio; may exceed 100%"),
}
COUNTRIES = {
    "Pakistan": "PAK", "India": "IND", "Bangladesh": "BGD", "Türkiye": "TUR",
    "United Kingdom": "GBR", "United States": "USA", "Canada": "CAN",
    "Australia": "AUS", "Malaysia": "MYS", "Indonesia": "IDN",
    "Nigeria": "NGA", "South Africa": "ZAF", "Saudi Arabia": "SAU",
    "Germany": "DEU", "France": "FRA", "Japan": "JPN", "South Korea": "KOR",
    "Brazil": "BRA", "Kenya": "KEN", "Sri Lanka": "LKA",
}
MODEL_EXPLANATIONS = {
    "Dummy baseline": "A simple reference using the most common outcome.",
    "Logistic Regression": "A statistical model that estimates patterns in the available information.",
    "Random Forest": "Combines decision trees to identify patterns.",
    "Extra Trees": "Combines highly varied decision trees.",
    "Gradient Boosting": "Builds a sequence of models that learn from earlier errors.",
    "RBF Support Vector Machine": "Finds a boundary and can capture non-linear patterns.",
    "K-Nearest Neighbours": "Uses outcomes from similar records in this dataset.",
}


@st.cache_data(ttl=86400, show_spinner=False)
def _latest_indicator(country_code: str, indicator_code: str) -> dict:
    """Return the latest non-null World Bank observation for one country."""
    url = (
        f"https://api.worldbank.org/v2/country/{country_code}/indicator/"
        f"{indicator_code}?format=json&per_page=60"
    )
    response = requests.get(url, timeout=12)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
        return {"value": None, "year": None}
    for item in payload[1]:
        if item.get("value") is not None:
            return {"value": float(item["value"]), "year": item.get("date")}
    return {"value": None, "year": None}


def _render_global_explorer() -> None:
    st.markdown("## 🌍 Explore education around the world")
    st.caption("Compare published country-level indicators. These describe education systems—not your personal ability or class position.")
    selected_indicator = st.selectbox("What would you like to compare?", list(WORLD_BANK_INDICATORS))
    indicator_code, definition = WORLD_BANK_INDICATORS[selected_indicator]
    selected_countries = st.multiselect(
        "Choose countries",
        list(COUNTRIES),
        default=["Pakistan", "Türkiye", "United Kingdom", "Malaysia"],
        max_selections=8,
    )
    st.caption(definition + " · Source: World Bank EdStats / World Development Indicators")
    if not selected_countries:
        st.info("Choose at least one country to view its latest available observation.")
        return
    rows = []
    with st.spinner("Loading the latest available country observations…"):
        for country in selected_countries:
            try:
                result = _latest_indicator(COUNTRIES[country], indicator_code)
                rows.append({"Country": country, "Value": result["value"], "Year": result["year"], "Status": "Available" if result["value"] is not None else "No observation"})
            except (requests.RequestException, ValueError, TypeError):
                rows.append({"Country": country, "Value": None, "Year": None, "Status": "Temporarily unavailable"})
    frame = pd.DataFrame(rows)
    available = frame.dropna(subset=["Value"]).copy()
    if not available.empty:
        chart = px.bar(
            available.sort_values("Value", ascending=True),
            x="Value", y="Country", orientation="h", color="Value",
            color_continuous_scale=["#b9c8ff", "#4357f5", "#25b9b7"],
            text=available.sort_values("Value", ascending=True)["Value"].map(lambda x: f"{x:.1f}%"),
        )
        chart.update_traces(textposition="outside", cliponaxis=False)
        chart.update_layout(
            height=max(260, 58 * len(available)), margin=dict(l=8, r=46, t=12, b=12),
            coloraxis_showscale=False, xaxis_title="Percent (%)", yaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#526078"), showlegend=False,
        )
        st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No observations were returned for this selection. Try another indicator or country.")
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.markdown(
        '[Open the World Bank indicator source](https://data.worldbank.org/indicator/' + indicator_code + ')'
        ' · [World Bank API documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392)'
    )
    st.info("Latest available years can differ by country. Definitions, survey coverage and reporting gaps matter. This is not a league table and cannot be used to rank individual students.")


def _render_ml_experiment() -> None:
    st.markdown("## 🧪 Machine-learning research")
    st.caption("A separate historical experiment for learning data-science methods. It is not connected to your learner profile.")
    st.info("This experiment uses Mathematics records from two schools in Portugal. It is not Pakistani student data and does not predict your grades, potential or future.")
    st.markdown("**Research workflow**  ·  Audit data  →  Compare models  →  Test unseen records  →  Explain limitations")
    if st.button("▶ Run research experiment", type="primary", use_container_width=True):
        with st.spinner("Retrieving the official UCI archive and evaluating models…"):
            try:
                st.session_state["research_results"] = run_experiment()
                st.session_state.pop("research_error", None)
                st.success("Experiment completed.")
            except Exception as exc:
                st.session_state.pop("research_results", None)
                st.session_state["research_error"] = type(exc).__name__
                st.error("The experiment could not be completed. Your learner profile is unaffected.")
    results = st.session_state.get("research_results")
    results_path = ARTIFACTS / "experiment_results.json"
    if results is None and results_path.exists():
        try:
            results = json.loads(results_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            results = None
    if not results:
        st.caption("Run the experiment to generate real audit and evaluation results. No metrics are fabricated.")
        return
    audit = results.get("dataset_audit", {})
    metrics = results.get("test_metrics", {})
    metric_cols = st.columns(3)
    metric_cols[0].metric("Records in dataset", f'{audit.get("rows", "—"):,}' if isinstance(audit.get("rows"), int) else "—")
    metric_cols[1].metric("Selected model", metrics.get("selected_model", "—"))
    metric_cols[2].metric("Held-out F1", f'{float(metrics.get("f1", 0)):.2f}')
    st.caption("These values describe this dataset and test sample only—not a learner.")
    comparison = pd.DataFrame(results.get("model_comparison", []))
    if not comparison.empty:
        comparison["What it does"] = comparison["model"].map(lambda name: MODEL_EXPLANATIONS.get(str(name), "A model evaluated in this experiment."))
        st.dataframe(comparison, use_container_width=True, hide_index=True)
    with st.expander("Methodology and limitations"):
        st.write("The experiment excludes G1 and G2 from model inputs to reduce grade leakage. It uses training cross-validation and a separate held-out test partition.")
        for limitation in results.get("limitations", []):
            st.markdown(f"- {limitation}")
        st.warning("Never use this experiment to rank, diagnose, punish, admit, exclude or deny support to a learner.")


def render_research_lab(hero) -> None:
    hero(
        "See the bigger education picture.",
        "Explore global indicators, compare countries and learn how education data is analysed.",
        "GLOBAL LEARNING & RESEARCH",
    )
    st.markdown(
        '<div class="pathway-banner"><div class="pathway-icon">🌐</div>'
        '<h2>Education has a world of context.</h2>'
        '<p>Explore country-level evidence. Keep personal learning progress personal.</p></div>',
        unsafe_allow_html=True,
    )
    global_tab, research_tab = st.tabs(["🌍 Global explorer", "🧪 ML research lab"])
    with global_tab:
        _render_global_explorer()
    with research_tab:
        _render_ml_experiment()
