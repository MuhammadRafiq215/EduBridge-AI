from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from src.knowledge_base import load_registry

st.set_page_config(page_title="Global Subject Catalogue | EduBridge AI",page_icon="🌐",layout="wide")
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
st.markdown('<div class="catalog-hero"><div style="font-size:12px;letter-spacing:2px;font-weight:800;color:#c9f27b">GLOBAL QUALIFICATION DIRECTORY</div><h1>Subject Catalogue</h1><p>Explore a growing directory of subjects across national boards and international qualifications. Each catalogue links back to official evidence and shows its research status.</p></div>',unsafe_allow_html=True)
rows=catalog["catalogues"]
a,b,c=st.columns(3)
a.metric("Qualification catalogues",len(rows))
b.metric("Subject entries",sum(len(x["subjects"]) for x in rows))
c.metric("Jurisdictions",len(set(x["jurisdiction"] for x in rows)))
st.caption("Subject-entry totals count the discovery-list entries shown here, not unique global subjects or official board-wide totals.")
countries=["All"]+sorted({x["jurisdiction"] for x in rows})
country=st.selectbox("Filter by country / jurisdiction",countries)
systems=["All"]+sorted({x["system"] for x in rows if country=="All" or x["jurisdiction"]==country})
system=st.selectbox("Filter by board / awarding body",systems)
query=st.text_input("Find a subject",placeholder="Try biology, computer science, economics, psychology…")
status_filter=st.selectbox("Research status",["All","catalogue_verified","historical_reference"])
filtered=[]
for item in rows:
    if country!="All" and item["jurisdiction"]!=country: continue
    if system!="All" and item["system"]!=system: continue
    if status_filter!="All" and item["status"]!=status_filter: continue
    subjects=[s for s in item["subjects"] if query.casefold() in s.casefold()] if query else item["subjects"]
    if query and not subjects: continue
    filtered.append((item,subjects))
if not filtered:
    st.info("No matching subject catalogue. Try a broader search or another jurisdiction.")
for item,subjects in filtered:
    with st.container(border=True):
        left,right=st.columns([4,1])
        left.markdown(f"**{item['system']}**")
        left.caption(f"{item['jurisdiction']} · {item['qualification']}")
        right.metric("Listed subjects",len(item["subjects"]))
        badge="Reviewed catalogue" if item["status"]=="catalogue_verified" else "Historical reference"
        st.markdown(f"**{badge}**")
        st.write(" · ".join(subjects))
        st.caption(item["note"])
        for sid in item.get("source_ids",[]):
            source=next((x for x in load_registry()["sources"] if x["source_id"]==sid),None)
            if source:
                st.markdown(f"[Official source: {source['title']}]({source['source_url']})")
st.divider()
st.info("A catalogue entry is not a full syllabus. To advise on examination papers, component weightings, grade boundaries or subject eligibility, EduBridge must retrieve the exact current subject specification and examination session.")
