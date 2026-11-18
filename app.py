from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data import load_student_math
from src.modeling import ARTIFACTS, run_experiment

st.set_page_config(page_title="EduBridge AI | Research Lab", page_icon="🎓", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:#09111f;color:#edf3ff}
section[data-testid="stSidebar"]{background:#101d31;border-right:1px solid #263b59}
h1,h2,h3{font-family:'Manrope',sans-serif!important;color:#f4f7ff!important}
.hero{padding:28px;border-radius:18px;background:linear-gradient(115deg,#172b49,#244c70 58%,#14645e);border:1px solid #38617c;margin-bottom:20px}
.kicker{color:#8ce3ce;font-size:12px;font-weight:800;letter-spacing:2px}
.hero-title{font-family:'Manrope',sans-serif;font-size:clamp(26px,4vw,38px);font-weight:800;color:white;margin:8px 0}
.subtle{color:#b8c9df}
.metric{background:#13233a;border:1px solid #2b4261;border-radius:14px;padding:16px;min-height:105px}
.metric-label{font-size:11px;letter-spacing:1px;color:#9eb2cc;font-weight:700}
.metric-value{font-family:'Manrope',sans-serif;font-size:25px;font-weight:800;color:#f5f8ff;margin-top:7px;overflow-wrap:anywhere}
</style>
""",unsafe_allow_html=True)

st.sidebar.markdown("## 🎓 EduBridge AI")
st.sidebar.caption("RESPONSIBLE EDUCATIONAL ANALYTICS")
page=st.sidebar.radio("RESEARCH WORKSPACE",["Research Overview","Dataset Explorer","Model Lab","Evaluation","Explainability","Responsible AI","Methodology"])
st.sidebar.divider()
st.sidebar.caption("PHASE 2 · BASELINE RESEARCH")
st.sidebar.markdown("**Dataset:** UCI Student Performance · Mathematics")
st.sidebar.markdown("**Target:** G3 below 10 / 20")
st.sidebar.caption("Research demonstration only — not a student decision tool.")

result_path=ARTIFACTS/"experiment_results.json"
results=None
if result_path.exists():
    try:
        results=json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        st.sidebar.error("Saved results could not be read.")

st.markdown("""
<div class="hero">
 <div class="kicker">PHASE 02 · DATA SCIENCE & MACHINE LEARNING</div>
 <div class="hero-title">From educational data to explainable evidence.</div>
 <div class="subtle">Dataset audit · Leakage-aware preprocessing · Baseline comparison ·
 Held-out evaluation · Model inspection</div>
</div>
""",unsafe_allow_html=True)

if st.sidebar.button("▶ Run / refresh experiment",use_container_width=True,type="primary"):
    with st.spinner("Downloading UCI data and running cross-validation..."):
        try:
            run_experiment()
            st.success("Experiment finished. Refreshing dashboard.")
            st.rerun()
        except Exception as exc:
            st.error(f"Experiment could not finish: {exc}")
            st.info("Check internet access, installed dependencies, and the UCI download endpoint.")

if results is None:
    st.info("No experiment results exist yet. Select **Run / refresh experiment** in the sidebar.")
    st.markdown("### What the experiment does")
    st.markdown("1. Downloads the official UCI Mathematics cohort.\n2. Audits rows, columns, duplicates, missing values, and target distribution.\n3. Defines G3 < 10 as the experimental positive class.\n4. Excludes G1 and G2 from predictors to reduce grade leakage.\n5. Compares Dummy, Logistic Regression, and Random Forest with stratified 5-fold CV.\n6. Selects by training CV F1 and evaluates once on a held-out test set.")
    st.stop()

audit=results["dataset_audit"]
metrics=results["test_metrics"]
comparison=pd.DataFrame(results["model_comparison"])

if page=="Research Overview":
    st.subheader("Research at a glance")
    cards=[("DATA RECORDS",f'{audit["rows"]:,}',"UCI Mathematics cohort"),
           ("PREDICTOR FEATURES",str(len(metrics["predictor_columns"])),"G1/G2/G3 excluded"),
           ("SELECTED MODEL",metrics["selected_model"],"Chosen by training CV F1"),
           ("HELD-OUT F1",f'{metrics["f1"]:.3f}',"One untouched test split")]
    cols=st.columns(4)
    for col,(label,value,note) in zip(cols,cards):
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="subtle">{note}</div></div>',unsafe_allow_html=True)
    left,right=st.columns([1.2,1])
    with left:
        st.markdown("### Cross-validation model comparison")
        chart=comparison.melt(id_vars="model",value_vars=["cv_f1_mean","cv_balanced_accuracy_mean"],var_name="metric",value_name="score")
        fig=px.bar(chart,x="model",y="score",color="metric",barmode="group",range_y=[0,1],template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#dce7f7",legend_title_text="",height=350)
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown("### Held-out test metrics")
        names=["accuracy","balanced_accuracy","precision","recall","f1","roc_auc"]
        fig=go.Figure(go.Bar(x=[metrics[n] for n in names],y=names,orientation="h",marker=dict(color="#42c7a5")))
        fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis=dict(range=[0,1]),height=350)
        st.plotly_chart(fig,use_container_width=True)
    st.success("Preprocessing is inside model pipelines; G1 and G2 are excluded from predictors.")
    st.warning("The source data represents Portuguese schools. These results do not establish validity for Pakistani learners.")

elif page=="Dataset Explorer":
    st.subheader("Dataset audit")
    st.markdown(f"Source: [UCI Student Performance]({results['dataset_url']})")
    cols=st.columns(4)
    for col,(label,value) in zip(cols,[("ROWS",audit["rows"]),("COLUMNS",audit["columns"]),("DUPLICATES",audit["duplicate_rows"]),("MISSING CELLS",audit["missing_cells"])]):
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',unsafe_allow_html=True)
    try:
        data=load_student_math()
        st.dataframe(data.head(30),use_container_width=True,hide_index=True)
        left,right=st.columns(2)
        with left:
            fig=px.histogram(data,x="G3",nbins=21,title="Final grade distribution (G3)",template="plotly_dark",color_discrete_sequence=["#42c7a5"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig,use_container_width=True)
        with right:
            missing=pd.Series(audit["missing_by_column"]).sort_values(ascending=False).head(12).rename_axis("Feature").reset_index(name="Missing values")
            fig=px.bar(missing,x="Missing values",y="Feature",orientation="h",title="Missing values by feature",template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig,use_container_width=True)
    except Exception as exc:
        st.warning(f"Dataset preview could not be reloaded: {exc}")
    st.info("Positive class = G3 < 10 on the source 0–20 grade scale. This is an experiment definition, not a diagnosis or universal academic label.")

elif page=="Model Lab":
    st.subheader("Baseline model laboratory")
    st.caption("Model selection uses mean stratified 5-fold CV F1 on training data.")
    display=comparison[["model","cv_accuracy_mean","cv_balanced_accuracy_mean","cv_precision_mean","cv_recall_mean","cv_f1_mean","cv_roc_auc_mean"]]
    st.dataframe(display.style.format({c:"{:.3f}" for c in display.columns if c!="model"}),use_container_width=True,hide_index=True)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=comparison["model"],y=comparison["cv_f1_mean"],mode="markers",marker=dict(size=13,color="#42c7a5"),
                             error_y=dict(type="data",array=comparison["cv_f1_std"],visible=True)))
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",yaxis=dict(range=[0,1],title="CV F1"),height=350)
    st.plotly_chart(fig,use_container_width=True)
    st.info(f"Selected model: **{metrics['selected_model']}**. The held-out test set was not used to select it.")

elif page=="Evaluation":
    st.subheader("Held-out evaluation")
    st.caption(f'Test records: {metrics["test_size"]} · Training records: {metrics["train_size"]} · Probability threshold: {metrics["decision_threshold"]:.2f}')
    cols=st.columns(4)
    for col,(label,key) in zip(cols,[("F1","f1"),("ROC-AUC","roc_auc"),("PR-AUC","average_precision"),("Brier score","brier_score")]):
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{metrics[key]:.3f}</div></div>',unsafe_allow_html=True)
    left,right=st.columns(2)
    with left:
        fig=px.imshow(metrics["confusion_matrix"],text_auto=True,x=["Predicted ≥10","Predicted <10"],y=["Actual ≥10","Actual <10"],color_continuous_scale="Teal",title="Confusion matrix",template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",height=370)
        st.plotly_chart(fig,use_container_width=True)
    with right:
        curve=metrics["roc_curve"]
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=curve["fpr"],y=curve["tpr"],mode="lines",name="ROC",line=dict(color="#42c7a5",width=3)))
        fig.add_trace(go.Scatter(x=[0,1],y=[0,1],mode="lines",name="Chance",line=dict(dash="dash",color="#9aabc7")))
        fig.update_layout(title="ROC curve",template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis_title="False positive rate",yaxis_title="True positive rate",height=370)
        st.plotly_chart(fig,use_container_width=True)
    st.dataframe(pd.DataFrame(metrics["classification_report"]).T.style.format("{:.3f}"),use_container_width=True)
    st.markdown("Precision measures positive prediction correctness; recall measures how many actual positive cases are identified. F1 balances both. ROC-AUC and PR-AUC measure ranking; Brier score measures probability error (lower is better).")

elif page=="Explainability":
    st.subheader("Model inspection")
    st.caption("Permutation importance is computed on held-out data after model selection, not used for tuning.")
    path=ARTIFACTS/"permutation_importance.csv"
    if path.exists():
        importance=pd.read_csv(path).head(15).sort_values("importance_mean")
        fig=px.bar(importance,x="importance_mean",y="feature",orientation="h",error_x="importance_std",template="plotly_dark",color="importance_mean",color_continuous_scale="Teal",title="Permutation importance (F1 decrease)")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",coloraxis_showscale=False,height=520)
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(importance.sort_values("importance_mean",ascending=False),use_container_width=True,hide_index=True)
    st.warning("Importance describes this model on this test sample. It does not prove causation, fairness, or that changing a feature changes a learner's outcome.")

elif page=="Responsible AI":
    st.subheader("Responsible AI and subgroup diagnostics")
    st.warning("Group metrics are descriptive diagnostics, not proof of fairness. Small groups can make estimates unstable.")
    for group_name,rows in results.get("group_audit",{}).items():
        st.markdown(f"### Group: {group_name}")
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    st.markdown("### Safeguards")
    for item in ["Never rank, punish, diagnose, admit, or exclude learners using this prototype.",
                 "Do not treat a model probability as a fact about an individual.",
                 "Do not upload identifiable student data to a public repository.",
                 "Portuguese school data is not validated for Pakistan.",
                 "Any real-world pilot requires local consent, governance, expert review, and independent evaluation."]:
        st.markdown(f"- {item}")

else:
    st.subheader("Methodology and reproducibility")
    st.json(results["methodology"])
    st.markdown("### Limitations")
    for item in results["limitations"]:
        st.markdown(f"- {item}")
    st.markdown("### Download experiment artifacts")
    for filename in ["experiment_results.json","model_comparison.csv","permutation_importance.csv","test_predictions.csv"]:
        path=ARTIFACTS/filename
        if path.exists():
            st.download_button(f"Download {filename}",data=path.read_bytes(),file_name=filename,mime="application/octet-stream")
    st.caption("The fitted pipeline is stored locally as artifacts/selected_model.joblib and excluded from Git.")

st.divider()
st.markdown('<p class="subtle" style="text-align:center">EduBridge AI · Phase 2 research prototype · Learn · Analyze · Build · Improve</p>',unsafe_allow_html=True)
