from __future__ import annotations
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from src.academic_profile import calculate_academic_profile
from src.knowledge_base import load_registry

st.set_page_config(page_title="Academic Profile Analyzer | EduBridge AI",page_icon="📊",layout="wide")
from src.navigation import render_page_sidebar
from src.visual_design import apply_visual_identity

st.markdown("""
<style>
section[data-testid="stSidebar"] {background:linear-gradient(180deg,#171a35 0%,#242653 100%);border-right:0}
section[data-testid="stSidebar"] * {color:#f6f7ff}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:#b9bddb}
section[data-testid="stSidebar"] hr {border-color:rgba(255,255,255,.16)}
section[data-testid="stSidebar"] [data-testid="stButton"] button,
section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
  border-radius:12px;min-height:42px;font-weight:650
}
section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
  background:linear-gradient(100deg,#6556ed,#168d9a);border:0;color:#fff
}
.eb-sidebar-brand {display:flex;align-items:center;gap:12px;margin:8px 0 10px}
.eb-sidebar-mark {display:grid;place-items:center;width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,#6757f5,#27c9d2);font-size:22px;color:#fff}
.eb-sidebar-brand strong {display:block;color:#fff;font-size:21px;letter-spacing:-.6px}
.eb-sidebar-brand span {display:block;color:#bfc4e7;font-size:9px;letter-spacing:1.2px;margin-top:3px}
.eb-sidebar-section {color:#c7f36b;font-size:10px;font-weight:800;letter-spacing:1.5px;margin:16px 0 8px}
@media(max-width:700px) {
 .main .block-container {padding:1rem .85rem 2rem}
 .kb-hero,.profile-hero,.catalog-hero {padding:22px 20px;border-radius:20px}
 .kb-hero h1,.profile-hero h1,.catalog-hero h1 {font-size:29px}
}
</style>
""", unsafe_allow_html=True)
render_page_sidebar("Academic Profile Analyzer")

st.markdown("""<style>
.stApp{background:linear-gradient(135deg,#f5f7ff 0%,#fbfcff 58%,#eef9f8 100%)}
.profile-hero{padding:30px 34px;border-radius:24px;background:linear-gradient(115deg,#171a35,#393879 60%,#087f8c);color:white;margin:8px 0 24px}
.profile-hero h1{color:white!important;font-size:36px;margin:0 0 8px}
.profile-hero p{color:#e3e9ff;margin:0;max-width:850px}
</style>""",unsafe_allow_html=True)
apply_visual_identity()
st.markdown('<div class="profile-hero"><div style="font-size:12px;letter-spacing:2px;font-weight:800;color:#c9f27b">EDUBRIDGE STUDENT INTELLIGENCE</div><h1>Academic Profile Analyzer</h1><p>Calculate marks accurately, compare subject performance and create a clear academic snapshot — with transparent calculations and no invented grades.</p></div>',unsafe_allow_html=True)
registry=load_registry()
systems=sorted({x["system"] for x in registry["coverage"]})
with st.container(border=True):
    st.subheader("1 · Examination context")
    c1,c2,c3=st.columns(3)
    country=c1.selectbox("Country / jurisdiction",["Pakistan","Global","Nigeria","Türkiye","United States","England","Russia","India","Other"])
    options=sorted({x["system"] for x in registry["coverage"] if x["jurisdiction"]==country})
    board=c2.selectbox("Board / awarding body",options or systems)
    qualification=c3.selectbox("Qualification / level",["SSC","HSSC","Matric","Intermediate","IGCSE","O Level","AS Level","A Level","International GCSE","International A Level","WASSCE","NECO SSCE","YKS","AP","IB Diploma","GCSE","Other"])
    exam_session=st.text_input("Examination session / year",placeholder="e.g. May/June 2026 or Annual 2026")
st.subheader("2 · Enter subject marks")
st.caption("Enter marks awarded and maximum marks. Do not enter component totals and subject totals together, or marks will be double-counted.")
initial=pd.DataFrame([{"Subject":"English","Marks obtained":0.0,"Maximum marks":100.0},{"Subject":"Mathematics","Marks obtained":0.0,"Maximum marks":100.0},{"Subject":"Science","Marks obtained":0.0,"Maximum marks":100.0}])
edited=st.data_editor(initial,num_rows="dynamic",use_container_width=True,hide_index=True,
 column_config={"Subject":st.column_config.TextColumn("Subject",required=True),
 "Marks obtained":st.column_config.NumberColumn("Marks obtained",min_value=0,step=1,format="%.2f"),
 "Maximum marks":st.column_config.NumberColumn("Maximum marks",min_value=0.01,step=1,format="%.2f")})
if st.button("Calculate my academic profile",type="primary",use_container_width=True):
    rows=[{"subject":r["Subject"],"marks_obtained":r["Marks obtained"],"maximum_marks":r["Maximum marks"]} for _,r in edited.iterrows() if str(r.get("Subject","")).strip()]
    try:
        st.session_state["academic_profile_report"]=calculate_academic_profile(rows)
        st.session_state["academic_profile_context"]={"country":country,"board":board,"qualification":qualification,"exam_session":exam_session}
    except ValueError as exc:
        st.error(str(exc))
report=st.session_state.get("academic_profile_report")
if report:
    context=st.session_state.get("academic_profile_context",{})
    st.divider()
    st.subheader("3 · Your academic snapshot")
    st.caption("Context: "+" · ".join(str(context.get(k,"Not specified")) for k in ["country","board","qualification","exam_session"]))
    a,b,c,d=st.columns(4)
    a.metric("Overall percentage",f"{report['overall_percentage']:.2f}%")
    b.metric("Marks total",f"{report['total_marks_obtained']:g} / {report['total_maximum_marks']:g}")
    c.metric("Subjects entered",report["subject_count"])
    d.metric("Equal-weight subject average",f"{report['simple_average_subject_percentage']:.2f}%")
    df=pd.DataFrame(report["subjects"])
    chart=px.bar(df,x="subject",y="percentage",text="percentage",range_y=[0,100],title="Subject-wise performance")
    chart.update_traces(texttemplate="%{text:.1f}%",textposition="outside")
    chart.update_layout(xaxis_title="",yaxis_title="Percentage",showlegend=False)
    st.plotly_chart(chart,use_container_width=True)
    left,right=st.columns(2)
    left.success(f"Strongest entered subject: {report['strongest_subject']} ({report['strongest_percentage']:.2f}%)")
    right.info(f"Lowest entered subject: {report['improvement_subject']} ({report['improvement_percentage']:.2f}%)")
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.warning(report["grade_note"])
    st.caption(report["interpretation"])
    st.download_button("Download academic profile (JSON)",json.dumps({"context":context,**report},indent=2),"edubridge_academic_profile.json","application/json")
st.divider()
st.caption("Privacy note: this page calculates in the current session and does not ask for student name, roll number or certificate upload.")
