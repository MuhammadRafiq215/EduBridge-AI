"""Global education explorer and learner-owned progress insights."""
from __future__ import annotations

import requests
import pandas as pd
import plotly.express as px
import streamlit as st

from .student_intelligence import build_student_intelligence

WORLD_BANK_INDICATORS = {
    "Adult literacy (ages 15+)": ("SE.ADT.LITR.ZS", "Percent of people ages 15 and above"),
    "Primary school enrolment": ("SE.PRM.ENRR", "Gross enrolment ratio; may exceed 100%"),
    "Secondary school enrolment": ("SE.SEC.ENRR", "Gross enrolment ratio; may exceed 100%"),
    "Tertiary education enrolment": ("SE.TER.ENRR", "Gross enrolment ratio; may exceed 100%"),
}


@st.cache_data(ttl=86400, show_spinner=False)
def _world_bank_countries() -> dict[str, str]:
    """Return every country/economy exposed by the World Bank country catalogue."""
    response = requests.get(
        "https://api.worldbank.org/v2/country?format=json&per_page=400",
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        raise ValueError("The World Bank country catalogue returned an unexpected response.")
    countries = {}
    for item in payload[1]:
        region = (item.get("region") or {}).get("value")
        code = item.get("id")
        name = item.get("name")
        if region and region != "Aggregates" and code and name:
            countries[str(name)] = str(code)
    if not countries:
        raise ValueError("No reporting economies were returned by the country catalogue.")
    return dict(sorted(countries.items(), key=lambda pair: pair[0].casefold()))


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
    st.markdown("## 🌍 Education around the world")
    st.caption("Compare published country-level indicators. These describe education systems, not individual students.")
    try:
        countries = _world_bank_countries()
    except (requests.RequestException, ValueError, TypeError):
        st.error("The global country catalogue is temporarily unavailable. Please try again later.")
        return

    selected_indicator = st.selectbox("Education indicator", list(WORLD_BANK_INDICATORS))
    indicator_code, definition = WORLD_BANK_INDICATORS[selected_indicator]
    preferred = ["Pakistan", "India", "Bangladesh", "Türkiye", "United Kingdom", "United States"]
    defaults = [name for name in preferred if name in countries]
    selected_countries = st.multiselect(
        f"Choose countries · {len(countries)} economies available",
        list(countries),
        default=defaults,
        max_selections=20,
    )
    st.caption(definition + " · Source: World Bank")
    if not selected_countries:
        st.info("Choose one or more countries to compare.")
        return

    rows = []
    with st.spinner("Loading the latest available observations…"):
        for country in selected_countries:
            try:
                result = _latest_indicator(countries[country], indicator_code)
                rows.append({
                    "Country": country, "Value": result["value"], "Year": result["year"],
                    "Status": "Available" if result["value"] is not None else "No observation",
                })
            except (requests.RequestException, ValueError, TypeError):
                rows.append({"Country": country, "Value": None, "Year": None, "Status": "Temporarily unavailable"})

    frame = pd.DataFrame(rows)
    available = frame.dropna(subset=["Value"]).copy()
    if not available.empty:
        ordered = available.sort_values("Value", ascending=True)
        chart = px.bar(
            ordered, x="Value", y="Country", orientation="h", color="Value",
            color_continuous_scale=["#b9c8ff", "#4357f5", "#25b9b7"],
            text=ordered["Value"].map(lambda value: f"{value:.1f}%"),
        )
        chart.update_traces(textposition="outside", cliponaxis=False)
        chart.update_layout(
            height=max(280, 42 * len(available)), margin=dict(l=8, r=46, t=12, b=12),
            coloraxis_showscale=False, xaxis_title="Percent (%)", yaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#526078"), showlegend=False,
        )
        st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No observations were returned. Try another indicator or country.")
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.markdown(
        f'[Open the World Bank indicator source](https://data.worldbank.org/indicator/{indicator_code})'
        ' · [API documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392)'
    )
    st.caption("Coverage and latest reporting year vary by indicator and country. Missing values are not zero. This is not a student ranking.")


def _render_my_learning_insights(profile: dict | None) -> None:
    st.markdown("## ✨ My learning insights")
    profile = profile if isinstance(profile, dict) else {}
    entries = profile.get("topic_progress", [])
    if not isinstance(entries, list):
        entries = []
    intelligence = build_student_intelligence(entries)

    if not entries:
        st.markdown(
            '<div class="pathway-banner"><div class="pathway-icon">🌱</div>'
            '<h2>Your learning picture starts with one topic.</h2>'
            '<p>Record a topic reflection in Student Navigator to see your own progress and review priorities here.</p></div>',
            unsafe_allow_html=True,
        )
        if st.button("Open Student Navigator", type="primary", use_container_width=True):
            st.session_state["navigate_to_workspace"] = "Student Navigator"
            st.rerun()
        return

    cols = st.columns(3)
    cols[0].metric("Topics explored", intelligence["topic_count"])
    cols[1].metric("Practice attempts", intelligence["practice_attempts"])
    cols[2].metric("Active days · 7 days", intelligence["active_days_last_7"])

    if intelligence["topics"]:
        frame = pd.DataFrame([
            {"Topic": f'{row["subject"]} · {row["topic"]}', "Learning signal": row["signal"]}
            for row in intelligence["topics"][:12]
        ])
        chart = px.bar(
            frame, x="Learning signal", y="Topic", orientation="h", color="Learning signal",
            range_x=[0, 100], text="Learning signal",
            color_continuous_scale=["#F29A78", "#5B4DE8", "#12A6A6"],
        )
        chart.update_traces(textposition="outside", cliponaxis=False)
        chart.update_layout(
            height=max(250, 42 * len(frame)), margin=dict(l=8, r=28, t=10, b=10),
            coloraxis_showscale=False, xaxis_title="Personal learning signal", yaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#526078"),
        )
        st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    priorities = intelligence.get("review_first", [])
    if priorities:
        st.markdown("### Your next review ideas")
        for row in priorities[:4]:
            with st.container(border=True):
                st.markdown(f'**{row["subject"]} · {row["topic"]}**')
                st.caption(f'{row["evidence"]} · confidence {row["confidence"]}/5')
                st.caption("Practice accuracy: " + (f'{row["accuracy"]}%' if row["accuracy"] is not None else "Not recorded"))
    st.caption("These insights are calculated from topic records you chose to enter. They are planning signals, not grades, diagnoses or predictions. Your personal records are not displayed as a public comparison.")


def render_research_lab(hero, profile: dict | None = None) -> None:
    hero(
        "Explore the world. Understand your progress.",
        "Compare global education indicators and discover your own next learning steps.",
        "GLOBAL LEARNING",
    )
    st.markdown(
        '<div class="pathway-banner"><div class="pathway-icon">🌐</div>'
        '<h2>Learning, seen from two perspectives.</h2>'
        '<p>Explore global education evidence and your own private learning journey.</p></div>',
        unsafe_allow_html=True,
    )
    global_tab, learner_tab = st.tabs(["🌍 Global explorer", "✨ My learning insights"])
    with global_tab:
        _render_global_explorer()
    with learner_tab:
        _render_my_learning_insights(profile)
