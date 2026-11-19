"""Streamlit workspace for Phase 5: Explainable AI."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data import load_student_math
from src.explainability import run_phase5_explanations

st.set_page_config(page_title="EduBridge AI | Phase 5 XAI", page_icon="🎓", layout="wide")
st.title("EduBridge AI — Phase 5: Explainable AI")
st.caption("SHAP global explanations · Record-level contribution analysis · Transparent limitations")
st.warning(
    "Research prototype only. These explanations describe model behaviour, not causes or "
    "recommended actions. The UCI dataset represents two Portuguese schools, not Pakistani "
    "learners. Never use this tool to rank, diagnose, punish, admit, exclude, or deny support."
)

with st.expander("What does SHAP explain?", expanded=True):
    st.markdown(
        """
        SHAP (SHapley Additive exPlanations) estimates how model features contribute to a
        prediction relative to a background dataset. Positive contributions move the model
        output upward; negative contributions move it downward.

        - **Global view:** average absolute contribution across the sampled held-out records.
        - **Record view:** contributions for one sampled held-out record.
        - **Important:** a contribution is not a cause, intervention, judgement, or proof of fairness.
        """
    )

with st.sidebar:
    st.subheader("Analysis settings")
    background_size = st.slider("Training background rows", 10, 80, 40, 5)
    explain_size = st.slider("Held-out records to explain", 5, 40, 25, 5)
    run = st.button("Run Phase 5 SHAP analysis", type="primary", use_container_width=True)

if run:
    with st.spinner("Selecting a model on training folds and calculating SHAP explanations…"):
        try:
            dataset = load_student_math()
            st.session_state["phase5_result"] = run_phase5_explanations(
                dataset, background_size=background_size, explain_size=explain_size
            )
            st.success("SHAP analysis completed.")
        except Exception as exc:
            st.error("The explanation analysis could not be completed.")
            st.exception(exc)

result = st.session_state.get("phase5_result")
if result:
    a, b, c = st.columns(3)
    a.metric("Selected model", result["selected_model"])
    b.metric("Training rows", result["sample_sizes"]["training"])
    c.metric("Explained held-out rows", result["sample_sizes"]["held_out_explained"])

    st.subheader("1. Global feature contributions")
    summary = pd.DataFrame(result["global_summary"])
    fig = px.bar(
        summary.sort_values("mean_abs_shap", ascending=True),
        x="mean_abs_shap", y="feature", orientation="h",
        labels={"mean_abs_shap": "Mean absolute SHAP value", "feature": "Feature"},
        title="Average contribution magnitude across the explained sample",
    )
    fig.update_layout(height=max(420, 24 * len(summary)), yaxis={"automargin": True})
    st.plotly_chart(fig, use_container_width=True)
    st.caption("This is a model-attribution ranking, not a ranking of what matters causally in education.")

    st.download_button(
        "Download global SHAP summary (CSV)",
        summary.to_csv(index=False).encode("utf-8"),
        file_name="edubridge_phase5_global_shap.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("2. Record-level explanation")
    records = result["explained_rows"]
    labels = [f"Sample record {i + 1}" for i in range(len(records))]
    chosen = st.selectbox("Choose an anonymised sample index", range(len(records)), format_func=lambda i: labels[i])
    contributions = pd.DataFrame({
        "feature": result["feature_names"],
        "shap_value": result["shap_values"][chosen],
    })
    contributions["direction"] = contributions["shap_value"].map(
        lambda value: "Raises model output" if value > 0 else "Lowers model output"
    )
    contributions = contributions.reindex(
        contributions["shap_value"].abs().sort_values(ascending=False).index
    ).head(15).sort_values("shap_value")
    local_fig = px.bar(
        contributions, x="shap_value", y="feature", color="direction",
        orientation="h",
        color_discrete_map={"Raises model output": "#e07a5f", "Lowers model output": "#4d9de0"},
        labels={"shap_value": "SHAP contribution to model output", "feature": "Feature"},
        title="Largest contributions for the selected sample record",
    )
    local_fig.add_vline(x=0, line_dash="dash", line_color="gray")
    local_fig.update_layout(height=560, yaxis={"automargin": True}, showlegend=True)
    st.plotly_chart(local_fig, use_container_width=True)
    base = result["base_values"][chosen]
    probability = result["predicted_probabilities"][chosen]
    st.caption(
        f"Model baseline output: {base:.3f} · Model output for this record: {probability:.3f}. "
        "Values are approximate additive contributions on the model probability scale."
    )

    with st.expander("Inspect the sampled feature values"):
        st.dataframe(pd.DataFrame([records[chosen]]), use_container_width=True, hide_index=True)

    st.subheader("3. Method and limitations")
    st.write(result["method"])
    st.json(result["training_cv"])
    for limitation in result["limitations"]:
        st.markdown(f"- {limitation}")
else:
    st.info("Select **Run Phase 5 SHAP analysis** in the sidebar to generate the explanations.")
