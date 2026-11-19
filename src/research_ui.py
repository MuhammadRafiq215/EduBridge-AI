"""Polished, transparent research-lab interface for EduBridge AI."""
from __future__ import annotations
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from .modeling import ARTIFACTS, run_experiment

def render_research_lab(hero) -> None:
    hero("The science behind the guidance.",
         "Explore reproducible educational-data experiments, inspect the evidence and understand what the models cannot tell us.",
         "RESEARCH LAB")
    st.markdown(
        '<div class="pathway-banner"><div class="pathway-icon">🧪</div><h2>Evidence, not guesswork.</h2>'
        '<p>Public benchmark data · transparent methodology · interpretable evaluation · clear limitations</p></div>',
        unsafe_allow_html=True)
    st.info("Research models use a public, historical dataset from two Portuguese schools. They are separate from your personal learning profile and must never predict an individual learner's future or be used to rank students.")
    st.markdown("### Secondary-school benchmark")
    st.write("The UCI Student Performance mathematics cohort includes a final-grade field (G3). This experiment defines G3 < 10 on the original 0–20 scale as its analytical target. Earlier grades G1 and G2 are excluded from predictors to reduce target leakage.")
    st.markdown('<div class="dash-band"><strong>A complete research workflow</strong><br><span class="small-muted">Official source retrieval · data-quality audit · stratified model comparison · held-out evaluation · post-selection feature inspection</span></div>', unsafe_allow_html=True)

    if st.button("▶ Run the research experiment", type="primary", use_container_width=True):
        with st.spinner("Retrieving the official UCI archive, checking nested ZIP files and evaluating models…"):
            try:
                st.session_state["research_results"] = run_experiment()
                st.session_state.pop("research_error", None)
                st.success("Research experiment completed successfully.")
            except Exception as exc:
                st.session_state.pop("research_results", None)
                st.session_state["research_error"] = f"{type(exc).__name__}: {exc}"
                st.error("The research run could not be completed. Your account and learning profile are unaffected.")
                st.warning("The downloader now checks nested ZIP archives and retries the official UCI legacy archive. Check Streamlit app logs if the network source is temporarily unavailable.")
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
        overview = results.get("research_overview", {})
        metrics = results.get("test_metrics", {})
        st.markdown("## Research results")
        st.caption("Results below come from the latest completed experiment.")
        cards = st.columns(4)
        cards[0].metric("Dataset records", f"{audit.get('rows', 0):,}")
        cards[1].metric("Source variables", audit.get("columns", "—"))
        cards[2].metric("Duplicate rows", audit.get("duplicate_rows", "—"))
        cards[3].metric("Missing cells", audit.get("missing_cells", "—"))
        with st.expander("Dataset audit & source details"):
            st.markdown("[UCI Student Performance dataset](https://archive.ics.uci.edu/dataset/320/student+performance)")
            st.write("Cohort: student-mat.csv (Mathematics)")
            st.write(f"G3 range: {audit.get('target_min', '—')}–{audit.get('target_max', '—')} / 20 · mean: {audit.get('target_mean', '—')}")
            st.write(f"Below threshold: {audit.get('below_threshold_count', '—')} · At or above threshold: {audit.get('at_or_above_threshold_count', '—')}")
            st.write("Excluded predictors: G1, G2 and G3.")
            missing = audit.get("missing_by_column", {})
            if missing:
                st.dataframe(pd.DataFrame([{"Variable": k, "Missing values": v} for k, v in missing.items()]), use_container_width=True, hide_index=True)

        grade_rows = overview.get("grade_distribution", [])
        if grade_rows:
            st.markdown("### Explore the source data")
            chart = px.bar(pd.DataFrame(grade_rows), x="grade", y="count",
                           labels={"grade": "Final grade (G3)", "count": "Records"},
                           title="Distribution of final mathematics grades",
                           color="count", color_continuous_scale=["#B9B1FF", "#6757F5", "#27C9D2"])
            chart.update_layout(height=320, coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

        comparison = pd.DataFrame(results.get("model_comparison", []))
        if not comparison.empty:
            st.markdown("### Model comparison")
            cols = [c for c in ["model", "cv_accuracy_mean", "cv_balanced_accuracy_mean", "cv_precision_mean", "cv_recall_mean", "cv_f1_mean", "cv_roc_auc_mean"] if c in comparison.columns]
            st.dataframe(comparison[cols].style.format({c: "{:.3f}" for c in cols if c != "model"}), use_container_width=True, hide_index=True)
            model_chart = px.bar(comparison.sort_values("cv_f1_mean"), x="cv_f1_mean", y="model", orientation="h",
                                 error_x="cv_f1_std" if "cv_f1_std" in comparison else None, range_x=[0, 1],
                                 title="Training cross-validation F1", color="cv_f1_mean",
                                 color_continuous_scale=["#B9B1FF", "#6757F5", "#27C9D2"])
            model_chart.update_layout(height=360, coloraxis_showscale=False, xaxis_title="Mean F1 across training folds",
                                      yaxis_title="", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(model_chart, use_container_width=True, config={"displayModeBar": False})

        st.markdown("### Held-out evaluation")
        st.caption("The held-out test partition is evaluated only after model selection.")
        metric_cols = st.columns(4)
        for col, label, key in zip(metric_cols, ["F1", "Balanced accuracy", "Precision", "Recall"], ["f1", "balanced_accuracy", "precision", "recall"]):
            col.metric(label, f"{metrics.get(key, 0):.3f}")
        st.caption(f"Selected model: {metrics.get('selected_model', 'Not recorded')} · Train: {metrics.get('train_size', '—')} · Test: {metrics.get('test_size', '—')} · Threshold: {metrics.get('decision_threshold', 0.5):.2f}")

        matrix = metrics.get("confusion_matrix")
        if matrix:
            left, right = st.columns(2)
            with left:
                st.markdown("**Confusion matrix**")
                st.dataframe(pd.DataFrame(matrix, index=["Actual: at/above", "Actual: below"], columns=["Predicted: at/above", "Predicted: below"]), use_container_width=True)
            with right:
                st.markdown("**Interpretation**")
                st.write("These counts describe one held-out split only. They do not measure an individual learner or establish real-world suitability.")

        importance_path = ARTIFACTS / "permutation_importance.csv"
        if importance_path.exists():
            importance = pd.read_csv(importance_path).head(10).sort_values("importance_mean")
            st.markdown("### Model interpretation")
            st.caption("Permutation importance describes this fitted model's behaviour; it does not establish causation.")
            importance_chart = px.bar(importance, x="importance_mean", y="feature", orientation="h", error_x="importance_std",
                                      title="Top permutation-importance estimates", color="importance_mean",
                                      color_continuous_scale=["#B9B1FF", "#6757F5", "#27C9D2"])
            importance_chart.update_layout(height=max(300, 38 * len(importance)), coloraxis_showscale=False,
                                           xaxis_title="Change in held-out F1 after shuffling", yaxis_title="",
                                           plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(importance_chart, use_container_width=True, config={"displayModeBar": False})

        with st.expander("Methodology, limitations & responsible use"):
            st.json(results.get("methodology", {}))
            for limitation in results.get("limitations", []):
                st.markdown(f"- {limitation}")
            st.warning("This benchmark represents two Portuguese schools, not Pakistani learners. Never use its output for admissions, grading, diagnosis, discipline, ranking or support decisions.")

        dl = st.columns(2)
        comparison_path = ARTIFACTS / "model_comparison.csv"
        if comparison_path.exists():
            dl[0].download_button("Download model comparison (CSV)", comparison_path.read_bytes(),
                                  file_name="edubridge_model_comparison.csv", mime="text/csv", use_container_width=True)
        dl[1].download_button("Download full research results (JSON)", json.dumps(results, indent=2).encode("utf-8"),
                              file_name="edubridge_research_results.json", mime="application/json", use_container_width=True)
    else:
        st.markdown('<div class="dash-band"><strong>Your research workspace is ready.</strong><br><span class="small-muted">Run the benchmark to populate this space with the real dataset audit, exploratory charts, model comparison and held-out evaluation. No metrics are invented.</span></div>', unsafe_allow_html=True)

    with st.expander("Other public datasets on the research roadmap"):
        st.markdown("- [Open University Learning Analytics Dataset (OULAD)](https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset) — a separate higher-education population and task.")
        st.markdown("- [Higher Education Students Performance Evaluation](https://archive.ics.uci.edu/dataset/856/higher+education+students+performance+evaluation) — a small exploratory benchmark requiring separate evaluation.")
        st.markdown("- [Engineering student performance dataset](https://data.mendeley.com/datasets/83tcx8psxv/1) — a separate dataset requiring schema and licence review.")
