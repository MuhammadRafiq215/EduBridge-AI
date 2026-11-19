"""Student-friendly, transparent research-lab interface for EduBridge AI."""
from __future__ import annotations
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from .modeling import ARTIFACTS, run_experiment

MODEL_EXPLANATIONS = {
    "Dummy baseline": "A simple reference that follows the most common outcome.",
    "Logistic Regression": "A straightforward statistical model that estimates patterns in the available information.",
    "Random Forest": "Combines many decision trees to look for patterns across different combinations of factors.",
    "Extra Trees": "Combines highly varied decision trees to classify records.",
    "Gradient Boosting": "Builds a sequence of small models, each improving on earlier errors.",
    "RBF Support Vector Machine": "Finds a boundary between the two research groups and can capture non-linear patterns.",
    "K-Nearest Neighbours": "Uses outcomes from records that are similar in the dataset.",
}
FEATURE_LABELS = {
    "studytime": "Weekly study-time category", "failures": "Previous class failures",
    "absences": "Recorded school absences", "schoolsup": "Extra educational support",
    "famsup": "Family educational support", "internet": "Internet access at home",
    "higher": "Interest in higher education", "goout": "Reported social-outing frequency",
    "health": "Self-reported health category", "age": "Age", "sex": "Recorded sex category",
    "address": "Home area category", "school": "School identifier",
}

def _friendly_feature(value: str) -> str:
    return FEATURE_LABELS.get(str(value), str(value).replace("_", " ").strip().capitalize())

def render_research_lab(hero) -> None:
    hero("Understand the evidence. Use it wisely.",
         "A student-friendly guide to education statistics, research datasets and what machine learning can — and cannot — tell us.",
         "RESEARCH LAB")
    st.markdown(
        '<div class="pathway-banner"><div class="pathway-icon">🧪</div><h2>Research that speaks human.</h2>'
        '<p>Clear explanations first. Technical detail when you want to explore further.</p></div>',
        unsafe_allow_html=True)
    st.markdown("## Education in Pakistan")
    st.write("These national indicators describe the wider education context. They are not personal grades, class rankings or a comparison of you against other students.")
    country_cols = st.columns(2)
    country_cols[0].metric("Literacy rate", "63%", help="Pakistan Economic Survey 2025–26, using HIES 2024–25 data.")
    country_cols[1].metric("Numeracy indicator", "79%", help="Pakistan Economic Survey 2025–26, using HIES 2024–25 data.")
    st.caption("National population indicators; definitions and age groups differ from school examination marks. They cannot tell us how an individual learner is performing.")
    st.markdown(
        "- [Pakistan Economic Survey 2025–26 — Education chapter](https://finance.gov.pk/survey/chapter_26/10_education.pdf)\n"
        "- [Pakistan Institute of Education — official publications](https://pie.gov.pk/Publications)\n"
        "- [Pakistan Bureau of Statistics — HIES](https://www.pbs.gov.pk/hies/)")
    with st.expander("How should I read these national figures?"):
        st.write("Literacy and numeracy are population-level indicators. They describe broad skills across a defined population, not the marks of students in one class, school or province. Check the survey year, age group and definition before comparing indicators.")
    st.divider()
    st.markdown("## A separate international research experiment")
    st.info("The machine-learning experiment uses historical Mathematics records from two schools in Portugal. It is not Pakistani student data and is not connected to your saved profile. It teaches data-science methods; it does not score or predict learners.")
    st.markdown("### What question does the experiment explore?")
    st.write("Can a model find patterns in background and school-related information that distinguish two groups in this historical dataset? The groups are defined using a final mathematics mark threshold on the original 0–20 scale. That threshold is only an experiment definition.")
    st.markdown('<div class="dash-band"><strong>What happens when you run it?</strong><br><span class="small-muted">Check data quality → compare approaches → test on unseen records → explain results and limitations.</span></div>', unsafe_allow_html=True)
    if st.button("▶ Run the research experiment", type="primary", use_container_width=True):
        with st.spinner("Retrieving the official UCI archive, checking the data and evaluating models…"):
            try:
                st.session_state["research_results"] = run_experiment()
                st.session_state.pop("research_error", None)
                st.success("The research experiment completed.")
            except Exception as exc:
                st.session_state.pop("research_results", None)
                st.session_state["research_error"] = f"{type(exc).__name__}: {exc}"
                st.error("The research run could not be completed. Your account and learning profile are unaffected.")
                st.warning("The official dataset source may be temporarily unavailable. Check app logs if the issue continues.")
                with st.expander("Technical error details"):
                    st.code(st.session_state["research_error"], language="text")
    results = st.session_state.get("research_results")
    results_path = ARTIFACTS / "experiment_results.json"
    if results is None and results_path.exists():
        try:
            results = json.loads(results_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            results = None
    if results:
        audit = results.get("dataset_audit", {})
        metrics = results.get("test_metrics", {})
        st.markdown("## What the experiment found")
        st.caption("These results describe this dataset and test sample only.")
        cards = st.columns(3)
        cards[0].metric("Historical records analysed", f"{audit.get('rows', 0):,}")
        cards[1].metric("Repeated records", f"{audit.get('duplicate_rows', '—')}")
        cards[2].metric("Missing data cells", f"{audit.get('missing_cells', '—')}")
        st.markdown("### Model results, explained")
        st.write(f"In this held-out test sample, the selected model's F1 score was {float(metrics.get('f1', 0)):.2f}. It identified {float(metrics.get('recall', 0)):.0%} of records in the below-threshold research group. These measure this experiment, not an individual student's future.")
        st.caption(f"Selected approach: {metrics.get('selected_model', 'Not recorded')}. Model selection uses training cross-validation, followed by a separate held-out test.")
        st.markdown("### What do the scores mean?")
        st.write("- **F1:** balances correct positive classifications with how many positive cases were found.\n- **Recall:** among records truly in the research group, the share the model identified.\n- **Precision:** among records flagged by the model, the share that truly belonged to the group.\n- **Balanced accuracy:** gives both groups equal weight.")
        comparison = pd.DataFrame(results.get("model_comparison", []))
        if not comparison.empty:
            st.markdown("### Comparing machine-learning approaches")
            friendly = comparison.copy()
            friendly["Approach"] = friendly["model"].astype(str)
            friendly["What it does"] = friendly["model"].map(lambda name: MODEL_EXPLANATIONS.get(str(name), "A model evaluated in this experiment."))
            labels = {"cv_f1_mean": "Average F1", "cv_balanced_accuracy_mean": "Balanced accuracy", "cv_precision_mean": "Precision", "cv_recall_mean": "Recall"}
            cols = ["Approach", "What it does"] + [key for key in labels if key in friendly]
            display = friendly[cols].rename(columns=labels)
            st.dataframe(display.style.format({label: "{:.2f}" for label in labels.values() if label in display}), use_container_width=True, hide_index=True)
            st.caption("Scores are averages across training folds. A higher score does not automatically mean a model is safer or useful in real life.")
        with st.expander("Explore the dataset's mathematics-mark distribution"):
            grade_rows = results.get("research_overview", {}).get("grade_distribution", [])
            if grade_rows:
                chart = px.bar(pd.DataFrame(grade_rows), x="grade", y="count",
                               labels={"grade": "Final mathematics mark (0–20)", "count": "Number of records"},
                               title="Final mathematics marks in this dataset",
                               color="count", color_continuous_scale=["#B9B1FF", "#6757F5", "#27C9D2"])
                chart.update_layout(height=320, coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})
        with st.expander("Explore which information influenced this model"):
            importance_path = ARTIFACTS / "permutation_importance.csv"
            if importance_path.exists():
                importance = pd.read_csv(importance_path).head(10).copy()
                importance["Student-friendly factor"] = importance["feature"].map(_friendly_feature)
                importance = importance.sort_values("importance_mean")
                chart = px.bar(importance, x="importance_mean", y="Student-friendly factor", orientation="h",
                               error_x="importance_std", title="How model performance changed when each factor was shuffled",
                               color="importance_mean", color_continuous_scale=["#B9B1FF", "#6757F5", "#27C9D2"])
                chart.update_layout(height=max(300, 38 * len(importance)), coloraxis_showscale=False,
                                   xaxis_title="Change in F1 score", yaxis_title="",
                                   plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})
                st.caption("This shows how the fitted model used information. It does not prove that a factor causes an outcome.")
        with st.expander("Technical details for data-science learners"):
            st.write("Dataset: UCI Student Performance — Mathematics cohort (student-mat.csv).")
            st.write(f"Records: {audit.get('rows', '—')} · original columns: {audit.get('columns', '—')}")
            st.write(f"Original final-mark range: {audit.get('target_min', '—')}–{audit.get('target_max', '—')} out of 20.")
            st.write("The source calls its term/final grade fields G1, G2 and G3. These grade fields are excluded from model inputs in this experiment.")
            st.write(f"Training records: {metrics.get('train_size', '—')} · held-out test records: {metrics.get('test_size', '—')}")
            st.json(results.get("methodology", {}))
            st.json(metrics)
        with st.expander("Important limitations and responsible use"):
            for limitation in results.get("limitations", []):
                st.markdown(f"- {limitation}")
            st.warning("This research does not represent Pakistan, does not evaluate your profile and must never be used to rank, diagnose, punish, admit, exclude or deny support to a learner.")
        downloads = st.columns(2)
        comparison_path = ARTIFACTS / "model_comparison.csv"
        if comparison_path.exists():
            downloads[0].download_button("Download model comparison (CSV)", comparison_path.read_bytes(), file_name="edubridge_model_comparison.csv", mime="text/csv", use_container_width=True)
        downloads[1].download_button("Download research results (JSON)", json.dumps(results, indent=2).encode("utf-8"), file_name="edubridge_research_results.json", mime="application/json", use_container_width=True)
    else:
        st.markdown('<div class="dash-band"><strong>Your research workspace is ready.</strong><br><span class="small-muted">Run the experiment to see the real dataset audit, model comparison and evaluation. No metrics are invented.</span></div>', unsafe_allow_html=True)
    with st.expander("Datasets for future research"):
        st.markdown("- [Open University Learning Analytics Dataset (OULAD)](https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset) — a separate higher-education population.\n- [Higher Education Students Performance Evaluation](https://archive.ics.uci.edu/dataset/856/higher+education+students+performance+evaluation) — a small exploratory dataset.\n- [Pakistan Institute of Education publications](https://pie.gov.pk/Publications) — official national and provincial reports.")
