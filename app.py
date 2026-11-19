from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data import load_student_math
from src.modeling import ARTIFACTS, run_experiment

st.set_page_config(
    page_title="EduBridge AI | Research Lab",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
    html, body, [class*="css"] {font-family: 'DM Sans', sans-serif;}
    .stApp {background: #09111f; color: #edf3ff;}
    section[data-testid="stSidebar"] {background: #101d31; border-right: 1px solid #263b59;}
    h1, h2, h3 {font-family: 'Manrope', sans-serif !important; color: #f4f7ff !important;}
    .hero {padding: clamp(20px, 4vw, 34px); border-radius: 20px;
      background: linear-gradient(115deg, #172b49, #244c70 58%, #14645e);
      border: 1px solid #38617c; margin-bottom: 22px;}
    .kicker {color: #8ce3ce; font-size: 11px; font-weight: 800; letter-spacing: 2px;}
    .hero-title {font-family: 'Manrope', sans-serif; font-size: clamp(25px, 4vw, 40px);
      line-height: 1.15; font-weight: 800; color: white; margin: 10px 0;}
    .subtle {color: #b8c9df; font-size: 0.92rem;}
    .metric {background: #13233a; border: 1px solid #2b4261; border-radius: 14px;
      padding: 16px; min-height: 112px;}
    .metric-label {font-size: 10px; letter-spacing: 1px; color: #9eb2cc; font-weight: 700;}
    .metric-value {font-family: 'Manrope', sans-serif; font-size: clamp(19px, 2vw, 26px);
      font-weight: 800; color: #f5f8ff; margin-top: 7px; overflow-wrap: anywhere;}
    div[data-testid="stMetric"] {background: #13233a; padding: 12px; border-radius: 12px;}
    .stButton button, .stDownloadButton button {border-radius: 10px; font-weight: 700;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("## 🎓 EduBridge AI")
st.sidebar.caption("RESPONSIBLE EDUCATIONAL ANALYTICS")
page = st.sidebar.radio(
    "RESEARCH WORKSPACE",
    [
        "Research Overview",
        "Dataset Explorer",
        "Model Lab",
        "Evaluation",
        "Explainability",
        "Responsible AI",
        "Methodology",
    ],
)
st.sidebar.divider()
st.sidebar.caption("PHASE 1 → PHASE 2")
st.sidebar.markdown("**Dataset:** UCI Student Performance · Mathematics")
st.sidebar.markdown("**Research target:** G3 below 10 / 20")
st.sidebar.caption("Research prototype only — not a student decision tool.")

result_path = ARTIFACTS / "experiment_results.json"
results = None
if result_path.exists():
    try:
        results = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        st.sidebar.error("Saved results could not be read. Run the experiment again.")

st.markdown(
    """
    <div class="hero">
      <div class="kicker">PHASE 02 · DATA SCIENCE & MACHINE LEARNING</div>
      <div class="hero-title">From educational data to explainable evidence.</div>
      <div class="subtle">Dataset audit · Leakage-aware preprocessing · Baseline comparison ·
      Held-out evaluation · Model inspection</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.sidebar.button("▶ Run / refresh experiment", use_container_width=True, type="primary"):
    with st.spinner("Downloading UCI data and running cross-validation..."):
        try:
            run_experiment()
            st.success("Experiment completed. Loading the new results…")
            st.rerun()
        except Exception as exc:
            st.error("The experiment could not be completed.")
            st.exception(exc)
            st.info("Check the app logs, internet connection, dependencies and UCI download availability.")

if results is None:
    st.info("No saved experiment results yet. Select **Run / refresh experiment** in the sidebar.")
    st.markdown("### How the research workflow operates")
    st.markdown(
        """
        1. Downloads the official UCI Mathematics dataset.
        2. Audits rows, columns, duplicates, missing values and target distribution.
        3. Defines G3 < 10 as this experiment's positive class.
        4. Excludes G1, G2 and G3 from the predictor set.
        5. Compares three baseline models using stratified five-fold cross-validation.
        6. Selects using training-fold F1 and evaluates on a held-out test set.
        """
    )
    st.warning(
        "The dataset represents two Portuguese schools. It is not evidence of model validity "
        "for Pakistani learners or any individual student."
    )
    st.stop()

try:
    audit = results["dataset_audit"]
    metrics = results["test_metrics"]
    comparison = pd.DataFrame(results["model_comparison"])
    required_metric_keys = {
        "selected_model", "test_size", "train_size", "accuracy",
        "balanced_accuracy", "precision", "recall", "f1", "roc_auc",
        "average_precision", "brier_score", "confusion_matrix",
        "classification_report", "roc_curve", "decision_threshold",
        "predictor_columns",
    }
    missing_keys = required_metric_keys.difference(metrics)
    if missing_keys:
        raise KeyError(f"Experiment results are missing fields: {sorted(missing_keys)}")
    if comparison.empty:
        raise ValueError("The model comparison table is empty.")
except (KeyError, TypeError, ValueError) as exc:
    st.error("The saved experiment results are incomplete or incompatible.")
    st.exception(exc)
    st.info("Select **Run / refresh experiment** in the sidebar to regenerate them.")
    st.stop()

if page == "Research Overview":
    st.subheader("Research at a glance")
    cards = [
        ("DATA RECORDS", f'{audit["rows"]:,}', "UCI Mathematics cohort"),
        ("PREDICTOR FEATURES", str(len(metrics["predictor_columns"])), "G1/G2/G3 excluded"),
        ("SELECTED MODEL", metrics["selected_model"], "Chosen by training CV F1"),
        ("HELD-OUT F1", f'{metrics["f1"]:.3f}', "One untouched test split"),
    ]
    columns = st.columns(4)
    for column, (label, value, note) in zip(columns, cards):
        with column:
            st.markdown(
                f'<div class="metric"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div><div class="subtle">{note}</div></div>',
                unsafe_allow_html=True,
            )

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("### Cross-validation model comparison")
        chart_data = comparison.melt(
            id_vars="model",
            value_vars=["cv_f1_mean", "cv_balanced_accuracy_mean"],
            var_name="metric",
            value_name="score",
        )
        figure = px.bar(
            chart_data,
            x="model",
            y="score",
            color="metric",
            barmode="group",
            range_y=[0, 1],
            template="plotly_dark",
        )
        figure.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dce7f7",
            legend_title_text="",
            height=350,
        )
        st.plotly_chart(figure, use_container_width=True)

    with right:
        st.markdown("### Held-out test metrics")
        names = ["accuracy", "balanced_accuracy", "precision", "recall", "f1", "roc_auc"]
        figure = go.Figure(
            go.Bar(
                x=[metrics[name] for name in names],
                y=names,
                orientation="h",
                marker={"color": "#42c7a5"},
            )
        )
        figure.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={"range": [0, 1]},
            height=350,
        )
        st.plotly_chart(figure, use_container_width=True)

    st.success("Preprocessing is inside model pipelines; G1 and G2 are excluded from predictors.")
    st.warning("The source data represents Portuguese schools. These results do not establish validity for Pakistan.")

elif page == "Dataset Explorer":
    st.subheader("Dataset audit")
    st.markdown(f"Source: [UCI Student Performance]({results['dataset_url']})")
    columns = st.columns(4)
    for column, (label, value) in zip(
        columns,
        [
            ("ROWS", audit["rows"]),
            ("COLUMNS", audit["columns"]),
            ("DUPLICATES", audit["duplicate_rows"]),
            ("MISSING CELLS", audit["missing_cells"]),
        ],
    ):
        with column:
            st.markdown(
                f'<div class="metric"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    try:
        @st.cache_data(ttl=3600, show_spinner="Loading the UCI dataset…")
        def cached_student_math():
            return load_student_math()

        data = cached_student_math()
        st.dataframe(data.head(30), use_container_width=True, hide_index=True)
        left, right = st.columns(2)
        with left:
            figure = px.histogram(
                data,
                x="G3",
                nbins=21,
                title="Final grade distribution (G3)",
                template="plotly_dark",
                color_discrete_sequence=["#42c7a5"],
            )
            figure.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(figure, use_container_width=True)
        with right:
            missing = (
                pd.Series(audit["missing_by_column"])
                .sort_values(ascending=False)
                .head(12)
                .rename_axis("Feature")
                .reset_index(name="Missing values")
            )
            figure = px.bar(
                missing,
                x="Missing values",
                y="Feature",
                orientation="h",
                title="Missing values by feature",
                template="plotly_dark",
            )
            figure.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(figure, use_container_width=True)
    except Exception as exc:
        st.warning(f"Dataset preview could not be reloaded: {exc}")

    st.info(
        "Positive class = G3 < 10 on the source 0–20 grade scale. This is an experiment "
        "definition, not a diagnosis or universal academic label."
    )

elif page == "Model Lab":
    st.subheader("Baseline model laboratory")
    st.caption("Model selection uses mean stratified five-fold CV F1 on training data.")
    display = comparison[
        [
            "model",
            "cv_accuracy_mean",
            "cv_balanced_accuracy_mean",
            "cv_precision_mean",
            "cv_recall_mean",
            "cv_f1_mean",
            "cv_roc_auc_mean",
        ]
    ]
    st.dataframe(
        display.style.format(
            {column: "{:.3f}" for column in display.columns if column != "model"}
        ),
        use_container_width=True,
        hide_index=True,
    )
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=comparison["model"],
            y=comparison["cv_f1_mean"],
            mode="markers",
            marker={"size": 13, "color": "#42c7a5"},
            error_y={"type": "data", "array": comparison["cv_f1_std"], "visible": True},
        )
    )
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"range": [0, 1], "title": "CV F1"},
        height=350,
    )
    st.plotly_chart(figure, use_container_width=True)
    st.info(
        f"Selected model: **{metrics['selected_model']}**. "
        "The held-out test set was not used to select it."
    )

elif page == "Evaluation":
    st.subheader("Held-out evaluation")
    st.caption(
        f"Test records: {metrics['test_size']} · Training records: {metrics['train_size']} · "
        f"Probability threshold: {metrics['decision_threshold']:.2f}"
    )
    columns = st.columns(4)
    for column, (label, key) in zip(
        columns,
        [("F1", "f1"), ("ROC-AUC", "roc_auc"), ("PR-AUC", "average_precision"), ("Brier score", "brier_score")],
    ):
        with column:
            st.metric(label, f"{metrics[key]:.3f}")

    left, right = st.columns(2)
    with left:
        figure = px.imshow(
            metrics["confusion_matrix"],
            text_auto=True,
            x=["Predicted ≥10", "Predicted <10"],
            y=["Actual ≥10", "Actual <10"],
            color_continuous_scale="Teal",
            title="Confusion matrix",
            template="plotly_dark",
        )
        figure.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=370)
        st.plotly_chart(figure, use_container_width=True)

    with right:
        curve = metrics["roc_curve"]
        figure = go.Figure()
        figure.add_trace(
            go.Scatter(
                x=curve["fpr"],
                y=curve["tpr"],
                mode="lines",
                name="ROC",
                line={"color": "#42c7a5", "width": 3},
            )
        )
        figure.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode="lines",
                name="Chance",
                line={"dash": "dash", "color": "#9aabc7"},
            )
        )
        figure.update_layout(
            title="ROC curve",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="False positive rate",
            yaxis_title="True positive rate",
            height=370,
        )
        st.plotly_chart(figure, use_container_width=True)

    st.markdown("### Decision-threshold sensitivity (held-out set)")
    st.caption("This table shows how the precision/recall trade-off changes. It is diagnostic only; the default 0.50 threshold is not tuned on the test set.")
    sensitivity = pd.DataFrame(metrics.get("threshold_sensitivity", []))
    if not sensitivity.empty:
        st.dataframe(sensitivity.style.format({column: "{:.3f}" for column in sensitivity.select_dtypes(include="number").columns}), use_container_width=True, hide_index=True)

    report = pd.DataFrame(metrics["classification_report"]).T
    st.dataframe(report.style.format("{:.3f}"), use_container_width=True)
    st.markdown(
        "Precision measures positive-prediction correctness; recall measures how many actual "
        "positive cases are identified. F1 balances both. ROC-AUC and PR-AUC measure ranking; "
        "Brier score measures probability error (lower is better)."
    )

elif page == "Explainability":
    st.subheader("Model inspection")
    st.caption("Permutation importance is computed on held-out data after model selection, not used for tuning.")
    importance_path = ARTIFACTS / "permutation_importance.csv"
    if importance_path.exists():
        importance = pd.read_csv(importance_path).head(15).sort_values("importance_mean")
        figure = px.bar(
            importance,
            x="importance_mean",
            y="feature",
            orientation="h",
            error_x="importance_std",
            template="plotly_dark",
            color="importance_mean",
            color_continuous_scale="Teal",
            title="Permutation importance (F1 decrease)",
        )
        figure.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            height=520,
        )
        st.plotly_chart(figure, use_container_width=True)
        st.dataframe(
            importance.sort_values("importance_mean", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No feature-importance file exists yet. Run the experiment from the sidebar.")

    st.warning(
        "Importance describes this model on this test sample. It does not prove causation, "
        "fairness, or that changing a feature changes a learner's outcome."
    )

elif page == "Responsible AI":
    st.subheader("Responsible AI and subgroup diagnostics")
    st.warning(
        "Group metrics are descriptive diagnostics, not proof of fairness. "
        "Small groups can make estimates unstable."
    )
    for group_name, rows in results.get("group_audit", {}).items():
        st.markdown(f"### Group: {group_name}")
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.caption("No subgroup rows were available for this group.")

    st.markdown("### Safeguards")
    safeguards = [
        "Never rank, punish, diagnose, admit or exclude learners using this prototype.",
        "Do not treat a model probability as a fact about an individual.",
        "Do not upload identifiable student data to a public repository.",
        "Portuguese school data is not validated for Pakistan.",
        "Any real-world pilot requires local consent, governance, expert review and independent evaluation.",
    ]
    for safeguard in safeguards:
        st.markdown(f"- {safeguard}")

else:
    st.subheader("Methodology and reproducibility")
    st.json(results["methodology"])
    st.markdown("### Limitations")
    for item in results["limitations"]:
        st.markdown(f"- {item}")

    st.markdown("### Download experiment artifacts")
    artifact_types = {
        "experiment_results.json": "application/json",
        "model_comparison.csv": "text/csv",
        "permutation_importance.csv": "text/csv",
        "test_predictions.csv": "text/csv",
        "threshold_sensitivity.csv": "text/csv",
    }
    for filename, mime_type in artifact_types.items():
        artifact_path = ARTIFACTS / filename
        if artifact_path.exists():
            st.download_button(
                f"Download {filename}",
                data=artifact_path.read_bytes(),
                file_name=filename,
                mime=mime_type,
            )
    st.caption("The fitted pipeline is stored locally as artifacts/selected_model.joblib and excluded from Git.")

st.divider()
st.markdown(
    '<p class="subtle" style="text-align:center">EduBridge AI · Phase 1 → Phase 2 · '
    'Learn · Analyze · Build · Improve</p>',
    unsafe_allow_html=True,
)
