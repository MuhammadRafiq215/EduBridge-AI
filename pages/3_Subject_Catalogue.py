from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from src.knowledge_base import load_registry

st.set_page_config(page_title="Global Subject Catalogue | EduBridge AI",page_icon="🌐",layout="wide")
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
render_page_sidebar("Subject Catalogue")

ROOT=Path(__file__).resolve().parents[1]
catalog=json.loads((ROOT/"data"/"knowledge"/"subject_catalog.json").read_text(encoding="utf-8"))
st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#f5f7ff 0%,#fbfcff 58%,#eef9f8 100%)}
.catalog-hero{padding:30px 34px;border-radius:24px;background:linear-gradient(115deg,#171a35,#393879 60%,#087f8c);color:white;margin:8px 0 24px}
.catalog-hero h1{color:white!important;font-size:36px;margin:0 0 8px}
.catalog-hero p{color:#e3e9ff;margin:0;max-width:850px}
.subject-chip{display:inline-block;padding:6px 10px;margin:4px;border-radius:999px;background:#f0efff;color:#4b459f;border:1px solid #e3e1ff;font-size:12px}
</style>
""",unsafe_allow_html=True)
apply_visual_identity()
st.markdown('<div class="catalog-hero"><div style="font-size:12px;letter-spacing:2px;font-weight:800;color:#c9f27b">GLOBAL QUALIFICATION DIRECTORY</div><h1>Subject Catalogue</h1><p>Explore a growing directory of subjects across national boards and international qualifications. Each catalogue links back to official evidence and shows its research status.</p></div>',unsafe_allow_html=True)
rows=catalog["catalogues"]
a,b,c=st.columns(3)
a.metric("Qualification catalogues",len(rows))
b.metric("Listed subject entries",sum(len(x["subjects"]) for x in rows))
c.metric("Study systems",len(set(x["jurisdiction"] for x in rows)))
st.caption("Explore subject lists by education system. Subject combinations can vary by year and must be checked against the current official scheme.")
with st.container():
    st.markdown('<div class="catalog-toolbar">',unsafe_allow_html=True)
    f1,f2,f3=st.columns([1,1,1.4])
    countries=["All jurisdictions"]+sorted({x["jurisdiction"] for x in rows})
    country=f1.selectbox("Study location",countries)
    systems=["All awarding bodies"]+sorted({x["system"] for x in rows if country=="All jurisdictions" or x["jurisdiction"]==country})
    system=f2.selectbox("Education system",systems)
    query=f3.text_input("Search subjects",placeholder="Biology, coding, economics…")
    group=st.selectbox("Explore a subject family",["All subject families"]+catalog.get("subject_groups",[]))
    st.markdown('</div>',unsafe_allow_html=True)
filtered=[]
for item in rows:
    if country!="All jurisdictions" and item["jurisdiction"]!=country: continue
    if system!="All awarding bodies" and item["system"]!=system: continue
    subjects=[s for s in item["subjects"] if query.casefold() in s.casefold()] if query else item["subjects"]
    if group!="All subject families":
        keywords={
            "Languages":["English","Urdu","Sindhi","Pashto","Arabic","Persian","French","Punjabi"],
            "Mathematics and Statistics":["Math","Statistics"],
            "Sciences":["Science","Physics","Chemistry","Biology","Agriculture"],
            "Computing and Technology":["Computer","Information Technology","digital","Technical"],
            "Business and Economics":["Economics","Accounting","Commerce","Business","Entrepreneurship"],
            "Humanities and Social Sciences":["History","Geography","Civics","Psychology","Sociology","Philosophy","Education"],
            "Arts and Design":["Art","Fine Arts","Design","Drawing"],
            "Physical Education and Health":["Health","Physical Education"],
            "Technical and Vocational":["Technical","vocational","Agriculture","Home Economics"],
            "Religious and Cultural Studies":["Islamic","Islamiyat","Ethics","Pakistan Studies","Culture"]
        }.get(group,[])
        subjects=[s for s in subjects if any(k.casefold() in s.casefold() for k in keywords)]
    if query and not subjects: continue
    filtered.append((item,subjects))
if not filtered:
    st.info("No matching subject catalogue. Try a broader search or another jurisdiction.")
for item,subjects in filtered:
    with st.container():
        st.markdown('<div class="catalog-card">',unsafe_allow_html=True)
        st.markdown(f'<div class="catalog-kicker">{item["jurisdiction"]} · {item["qualification"]}</div>',unsafe_allow_html=True)
        st.subheader(item["system"])
        st.markdown(f'<span class="catalog-count">{len(subjects)} matching subjects</span>',unsafe_allow_html=True)
        st.write(" · ".join(subjects))
        if item["status"]=="catalogue_verified":
            st.caption("Official catalogue reviewed · Check current subject combinations")
        else:
            st.caption("Historical reference · Confirm the latest subject list with the awarding body")
        st.caption(item["note"])
        for sid in item.get("source_ids",[]):
            source=next((x for x in load_registry()["sources"] if x["source_id"]==sid),None)
            if source:
                st.markdown(f"[Open official source ↗]({source['source_url']})")
        st.markdown('</div>',unsafe_allow_html=True)
st.divider()
st.info("A catalogue entry is not a full syllabus. To advise on examination papers, component weightings, grade boundaries or subject eligibility, EduBridge must retrieve the exact current subject specification and examination session.")
