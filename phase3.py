"""Standalone Streamlit workspace for EduBridge AI Phase 3."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data import load_student_math
from src.exploration import run_phase3_analysis

st.set_page_config(page_title="EduBridge AI | Phase 3 Research", page_icon="🎓", layout="wide")
st.title("EduBridge AI — Phase 3 Research Lab")
st.caption("Deeper exploratory analysis · Target-definition sensitivity")
st.warning(
    "Research prototype only. The UCI dataset represents two Portuguese schools, "
    "not Pakistani learners. Outputs must not be used to rank, diagnose, punish, "
    "admit, exclude, or determine an individual learner's access to support."
)

st.markdown(
    """
    ## Research question
    How do descriptive patterns and model evaluation results change when the
    definition of a below-threshold final grade changes?

    The positive class is tested at **G3 < 8**, **G3 < 10**, and **G3 < 12**.
    These are sensitivity scenarios, not proposed school policies.
    """
)

if st.button("Run Phase 3 analysis", type="primary"):
    with st.spinner("Downloading the UCI dataset and running the analysis…"):
        try:
            data = load_student_math()
            result = run_phase3_analysis(data)
            Path("artifacts").mkdir(exist_ok=True)
            Path("artifacts/phase3_analysis.json").write_text(
                json.dumps(result, indent=2), encoding="utf-8"
            )
            st.session_state["phase3_result"] = result
            st.success("Phase 3 analysis completed.")
        except Exception as exc:
            st.error("The analysis could not be completed.")
            st.exception(exc)

result = st.session_state.get("phase3_result")
if result:
    exploratory = result["exploratory"]
    sensitivity = pd.DataFrame(result["target_sensitivity"])
    a, b, c = st.columns(3)
    a.metric("Student records", f"{exploratory['rows']:,}")
    a.metric("Grade definitions", "3")
    b.metric("Predictor leakage", "G1/G2/G3 excluded")
    c.metric("Validation", "5-fold CV + held-out test")

    st.divider()
    st.subheader("1. Final-grade distribution")
    grades = pd.DataFrame(exploratory["grade_counts"])
    fig = px.bar(grades, x="grade", y="count", labels={"grade": "Final grade (G3)", "count": "Students"})
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("2. Numeric feature relationships with G3")
    corr = pd.DataFrame(exploratory["grade_correlations"])
    st.caption("Associations are descriptive; correlation does not establish causation.")
    if not corr.empty:
        fig = px.bar(corr.sort_values("correlation_with_G3"), x="correlation_with_G3", y="feature", orientation="h")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(corr, use_container_width=True, hide_index=True)

    st.subheader("3. Target-definition sensitivity")
    st.caption("Each definition is modelled separately. Metrics are not directly interchangeable because the positive class changes.")
    st.dataframe(sensitivity, use_container_width=True, hide_index=True)
    valid = sensitivity[sensitivity["status"] == "evaluated"]
    if not valid.empty:
        plot = valid.melt(
            id_vars="definition",
            value_vars=["test_precision", "test_recall", "test_f1", "test_balanced_accuracy"],
            var_name="metric", value_name="score",
        )
        fig = px.bar(plot, x="definition", y="score", color="metric", barmode="group", range_y=[0, 1])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("4. Categorical distributions")
    categorical = exploratory["categorical_distributions"]
    selected = st.selectbox("Explore categorical feature", list(categorical))
    st.dataframe(pd.DataFrame(categorical[selected]), use_container_width=True, hide_index=True)

    st.subheader("5. Research design and limitations")
    st.json(result["methodology"])
    st.markdown(
        """
        - The cut-offs are analytical scenarios, not diagnoses or universal standards.
        - The same stratified split seed is used, but each target creates a different classification task.
        - The selected model may differ across definitions; compare results as sensitivity evidence, not a leaderboard.
        - G1, G2 and G3 are excluded from predictors to avoid target leakage.
        - The dataset is small, historical and geographically limited.
        - Results do not establish validity, fairness, or usefulness for Pakistani schools.
        - A real-world study would require local governance, consent, privacy safeguards and independent review.
        """
    )
    st.download_button(
        "Download Phase 3 analysis (JSON)",
        data=json.dumps(result, indent=2),
        file_name="edubridge_phase3_analysis.json",
        mime="application/json",
    )
else:
    st.info("Run the analysis to generate the Phase 3 tables, charts and downloadable research output.")
