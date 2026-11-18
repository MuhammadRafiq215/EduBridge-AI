import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EduBridge AI", page_icon="🎓", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0b1020; color: #edf2ff; }
section[data-testid="stSidebar"] { background: #111a2e; border-right: 1px solid #24314d; }
section[data-testid="stSidebar"] * { color: #e8efff !important; }
h1,h2,h3 { font-family: 'Manrope', sans-serif !important; color: #f4f7ff !important; }
.hero { padding: 28px 30px; border-radius: 18px; background: linear-gradient(115deg,#172746,#243b66 55%,#164b5b); border: 1px solid #365277; margin-bottom: 22px; }
.kicker { color:#8de3d2; font-size:12px; font-weight:700; letter-spacing:2px; text-transform:uppercase; }
.hero-title { color:#fff; font-family:'Manrope',sans-serif; font-size:clamp(25px,4vw,36px); font-weight:800; margin:7px 0; }
.hero-sub,.muted { color:#c3d0e5; }
.metric { background:#141f35; border:1px solid #263653; border-radius:14px; padding:17px; min-height:108px; }
.metric-label { color:#9aabc7; font-size:11px; font-weight:700; letter-spacing:1px; }
.metric-value { color:#f6f8ff; font-family:'Manrope',sans-serif; font-size:28px; font-weight:800; margin-top:7px; }
.panel { background:#141f35; border:1px solid #263653; border-radius:14px; padding:18px; margin-bottom:12px; }
div[data-testid="stDataFrame"] { border:1px solid #263653; border-radius:12px; }
.stButton button { border-radius:9px; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# Demonstration records only. Never treat these as real student data or model predictions.
students = pd.DataFrame({
    "Student ID": [f"DEMO-{i:03d}" for i in range(1, 11)],
    "Learner": [f"Learner {letter}" for letter in "ABCDEFGHIJ"],
    "Attendance (%)": [92, 68, 85, 57, 96, 73, 81, 62, 89, 77],
    "Study Time (hrs/week)": [12, 5, 9, 3, 14, 6, 8, 4, 11, 7],
    "Previous Grade": [82, 54, 73, 48, 91, 61, 70, 51, 85, 66],
    "Review Indicator": ["On track", "Review", "On track", "Priority review", "On track",
                         "Review", "On track", "Priority review", "On track", "Review"]
})

st.sidebar.markdown("## 🎓 EduBridge AI")
st.sidebar.caption("EDUCATIONAL INTELLIGENCE")
page = st.sidebar.radio("NAVIGATION", ["Overview", "Learner Explorer", "AI & Explainability", "Learning Support", "Project"])
st.sidebar.divider()
st.sidebar.caption("PHASE 1 · UI PROTOTYPE")
st.sidebar.info("All displayed records are synthetic examples created for interface demonstration.")

st.markdown("""
<div class="hero">
  <div class="kicker">EDUCATION · DATA · RESPONSIBLE AI</div>
  <div class="hero-title">Every learner deserves a fair chance.</div>
  <div class="hero-sub">An educational analytics prototype exploring how understandable data insights
  can help educators notice learning needs and consider timely, human-led support.</div>
</div>
""", unsafe_allow_html=True)

if page == "Overview":
    st.subheader("Learning overview")
    st.caption("Illustrative interface metrics — not institutional statistics")
    metrics = [
        ("DEMO LEARNERS", str(len(students)), "Synthetic sample rows"),
        ("MEAN ATTENDANCE", f"{students['Attendance (%)'].mean():.1f}%", "Across demo records"),
        ("MEAN PRIOR GRADE", f"{students['Previous Grade'].mean():.1f}", "Illustrative grade scale"),
        ("REVIEW EXAMPLES", str(students["Review Indicator"].ne("On track").sum()), "Manually assigned demo labels")
    ]
    cols = st.columns(4)
    for col, (label, value, note) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="muted">{note}</div></div>', unsafe_allow_html=True)

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("### Attendance and prior grades")
        fig = px.scatter(students, x="Attendance (%)", y="Previous Grade",
                         size="Study Time (hrs/week)", color="Review Indicator",
                         hover_name="Learner", template="plotly_dark",
                         color_discrete_map={"On track":"#42c7a5","Review":"#f4b860","Priority review":"#ef7185"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#dce6f7", height=360, margin=dict(l=5,r=5,t=15,b=5))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("### Example review groups")
        counts = students["Review Indicator"].value_counts().rename_axis("Indicator").reset_index(name="Count")
        pie = px.pie(counts, names="Indicator", values="Count", hole=.65, template="plotly_dark",
                     color="Indicator",
                     color_discrete_map={"On track":"#42c7a5","Review":"#f4b860","Priority review":"#ef7185"})
        pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#dce6f7",
                          height=360, margin=dict(l=5,r=5,t=15,b=5), legend_title_text="")
        st.plotly_chart(pie, use_container_width=True)
    st.markdown("### Learner snapshot")
    st.dataframe(students, use_container_width=True, hide_index=True)
    st.warning("These labels are manually written demonstration values. No AI model has generated them.")

elif page == "Learner Explorer":
    st.subheader("Learner Explorer")
    st.caption("Search and filter the synthetic demonstration dataset.")
    query = st.text_input("Search learner or ID", placeholder="Try Learner A or DEMO-001")
    statuses = students["Review Indicator"].unique().tolist()
    selected = st.multiselect("Review indicator", statuses, default=statuses)
    view = students[students["Review Indicator"].isin(selected)]
    if query:
        view = view[
            view["Learner"].str.contains(query, case=False) |
            view["Student ID"].str.contains(query, case=False)
        ]
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(view)} of {len(students)} synthetic records.")

elif page == "AI & Explainability":
    st.subheader("AI & Explainability")
    st.warning("Machine-learning integration is planned, not implemented. This prototype produces no predictions, risk scores, or explanations.")
    st.markdown("### Planned workflow")
    steps = [
        "Document the dataset, target variable, and intended use.",
        "Check missingness, class balance, feature definitions, and possible leakage.",
        "Build simple baselines before comparing more complex models.",
        "Evaluate precision, recall, F1-score, confusion matrix, and calibration where appropriate.",
        "Investigate subgroup performance and explain model limitations.",
        "Present any future output as a prompt for human review, never an automated decision."
    ]
    for i, step in enumerate(steps, 1):
        st.markdown(f'<div class="panel"><b style="color:#8de3d2">{i:02d}</b> &nbsp; {step}</div>', unsafe_allow_html=True)
    st.markdown("### Candidate methods")
    st.write("Logistic Regression · Decision Tree · Random Forest · SHAP or permutation-based explanations")
    st.caption("The final methods will be selected only after data inspection and validation.")

elif page == "Learning Support":
    st.subheader("Learning Support Hub")
    st.caption("A concept for connecting insights with practical, supportive next steps.")
    cards = [
        ("📚", "Accessible learning resources", "Topic-based notes, practice materials, and curated learning links."),
        ("🧑‍🏫", "Teacher or tutor support", "Human guidance for learners who may benefit from extra explanation."),
        ("🗓️", "Study planning", "Manageable weekly goals and progress check-ins."),
        ("🌐", "Low-connectivity learning", "Downloadable and offline-friendly resources for limited internet access.")
    ]
    for icon, title, desc in cards:
        st.markdown(f'<div class="panel"><h3>{icon} {title}</h3><span class="muted">{desc}</span></div>', unsafe_allow_html=True)
    st.info("Support suggestions should be inclusive and optional. A model must never decide a learner's worth or access to education.")

else:
    st.subheader("About this project")
    st.markdown("""
**Mission:** Explore responsible, explainable educational analytics that may help educators understand learning patterns and consider additional support.

**Problem space:** Students do not always receive timely or consistent academic support, particularly in resource-constrained settings.

**Research direction:** Begin with a documented public dataset, establish a defensible target, compare baseline models, evaluate limitations, and only then consider integrating a validated model.

**Initial dataset candidate:** [UCI Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance). It represents Portuguese schools; results must not be assumed to generalize to Pakistan or any other education system.
""")
    st.markdown("### Responsible-use commitments")
    for item in [
        "Use documented, appropriately licensed data and protect personal information.",
        "Avoid target leakage and explain the modelling choices.",
        "Report uncertainty, limitations, and relevant fairness checks.",
        "Keep educators and learners central to decisions.",
        "Never use a prototype score to deny a learner an opportunity."
    ]:
        st.markdown(f"- {item}")
    roadmap = pd.DataFrame({
        "Phase": ["01 · Interface", "02 · Data", "03 · Modelling", "04 · Explainability", "05 · Evaluation", "06 · Deployment"],
        "Deliverable": ["Streamlit prototype", "Data audit and cleaning", "Baseline model comparison",
                        "Feature explanations", "Fairness and error analysis", "Documented demonstration app"],
        "Status": ["In progress", "Planned", "Planned", "Planned", "Planned", "Planned"]
    })
    st.markdown("### Development roadmap")
    st.dataframe(roadmap, use_container_width=True, hide_index=True)

st.divider()
st.markdown('<p class="muted" style="text-align:center">EduBridge AI · Student-led educational technology research prototype</p>', unsafe_allow_html=True)
