"""Standalone Streamlit workspace for EduBridge AI Phase 4."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data import load_student_math
from src.phase4 import run_phase4_analysis

st.set_page_config(page_title="EduBridge AI | Phase 4 Research", page_icon="🎓", layout="wide")
st.title("EduBridge AI — Phase 4 Research Lab")
st.caption("Probability calibration · Uncertainty · Robustness · Error analysis")
st.warning(
    "Research prototype only. The UCI dataset represents two Portuguese schools, "
    "not Pakistani learners. Never use these outputs to rank, diagnose, punish, "
    "admit, exclude, or determine an individual learner's access to support."
)

st.markdown(
    """
    ## Research questions
    - Do predicted probabilities align with observed outcome frequencies?
    - How uncertain are held-out performance estimates?
    - What kinds of classification errors occur?
    - How much do training-fold results vary across repeated splits?

    The positive class remains **G3 < 10** on the source 0–20 scale.
    """
)

with st.expander("Analysis settings", expanded=False):
    bootstrap_repeats = st.select_slider(
        "Bootstrap repetitions", options=[200, 500, 1000, 2000], value=1000,
        help="More repetitions stabilise percentile estimates but take longer.",
    )
    robustness_repeats = st.select_slider(
        "Repeated cross-validation cycles", options=[2, 3, 5], value=3,
    )

if st.button("Run Phase 4 analysis", type="primary"):
    with st.spinner("Training models, calibrating probabilities and estimating uncertainty…"):
        try:
            data = load_student_math()
            result = run_phase4_analysis(
                data, bootstrap_repeats=int(bootstrap_repeats),
                robustness_repeats=int(robustness_repeats),
            )
            Path("artifacts").mkdir(exist_ok=True)
            Path("artifacts/phase4_analysis.json").write_text(
                json.dumps(result, indent=2), encoding="utf-8"
            )
            st.session_state["phase4_result"] = result
            st.success("Phase 4 analysis completed.")
        except Exception as exc:
            st.error("The analysis could not be completed.")
            st.exception(exc)

result = st.session_state.get("phase4_result")
if result:
    calibration = result["probability_calibration"]
    raw = calibration["raw_metrics"]
    calibrated = calibration["calibrated_metrics"]
    a, b, c, d = st.columns(4)
    a.metric("Selected model", result["selected_model"])
    b.metric("Test records", result["sample_sizes"]["held_out_test"])
    c.metric("Raw Brier score", f"{raw['brier_score']:.3f}")
    d.metric("Calibrated Brier score", f"{calibrated['brier_score']:.3f}")

    st.divider()
    st.subheader("1. Probability calibration")
    st.caption("A reliability curve closer to the diagonal indicates closer agreement between predicted probabilities and observed frequencies.")
    raw_bins = pd.DataFrame(calibration["raw_reliability_bins"])
    cal_bins = pd.DataFrame(calibration["calibrated_reliability_bins"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Perfect calibration", line={"dash": "dash"}))
    if not raw_bins.empty:
        fig.add_trace(go.Scatter(
            x=raw_bins["mean_predicted_probability"], y=raw_bins["observed_positive_rate"],
            mode="lines+markers", name="Raw probabilities",
            marker={"size": raw_bins["count"] * 0 + 9},
        ))
    if not cal_bins.empty:
        fig.add_trace(go.Scatter(
            x=cal_bins["mean_predicted_probability"], y=cal_bins["observed_positive_rate"],
            mode="lines+markers", name="Sigmoid calibrated",
            marker={"size": cal_bins["count"] * 0 + 9},
        ))
    fig.update_layout(
        xaxis_title="Mean predicted probability", yaxis_title="Observed positive rate",
        xaxis={"range": [0, 1]}, yaxis={"range": [0, 1]}, height=430,
    )
    st.plotly_chart(fig, use_container_width=True)
    comparison = pd.DataFrame([
        {"version": "Raw", **raw},
        {"version": "Sigmoid calibrated", **calibrated},
    ])
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    st.subheader("2. Bootstrap uncertainty intervals")
    uncertainty_rows = []
    for version, payload in result["uncertainty"].items():
        for metric, interval in payload["intervals"].items():
            uncertainty_rows.append({
                "model_version": version.replace("_", " "),
                "metric": metric,
                "lower_95": interval["lower"],
                "upper_95": interval["upper"],
                "valid_resamples": interval["valid_bootstrap_samples"],
            })
    intervals = pd.DataFrame(uncertainty_rows)
    st.caption("Percentile intervals resample held-out predictions. They do not measure external validity.")
    st.dataframe(intervals, use_container_width=True, hide_index=True)
    st.info(result["uncertainty"]["calibrated_model"]["warning"])

    st.subheader("3. Error analysis")
    error = result["error_analysis"]
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Test errors", error["errors"])
    e2.metric("Error rate", f"{error['error_rate']:.1%}")
    e3.metric("False positives", error["false_positives"])
    e4.metric("False negatives", error["false_negatives"])
    counts = error["confusion_counts"]
    matrix = pd.DataFrame(
        [[counts["true_negative"], counts["false_positive"]],
         [counts["false_negative"], counts["true_positive"]]],
        index=["Actual negative", "Actual positive"],
        columns=["Predicted negative", "Predicted positive"],
    )
    fig = px.imshow(matrix, text_auto=True, aspect="auto", title="Confusion matrix")
    st.plotly_chart(fig, use_container_width=True)
    for group, rows in error["group_diagnostics"].items():
        st.markdown(f"**Descriptive error audit: {group}**")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption("Group comparisons are descriptive; small sample sizes make rates unstable and do not establish fairness.")

    st.subheader("4. Robustness across repeated training folds")
    robustness = pd.DataFrame(result["robustness"]["results"])
    st.dataframe(robustness, use_container_width=True, hide_index=True)
    st.caption(result["robustness"]["warning"])

    st.subheader("5. Methodology and limitations")
    st.json(result["methodology"])
    for limitation in result["limitations"]:
        st.markdown(f"- {limitation}")

    st.download_button(
        "Download Phase 4 research results (JSON)",
        data=json.dumps(result, indent=2),
        file_name="edubridge_phase4_analysis.json",
        mime="application/json",
    )
else:
    st.info("Run the analysis to generate calibration, uncertainty, error and robustness results.")
