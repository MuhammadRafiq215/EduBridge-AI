from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from src.knowledge_base import EducationalKnowledgeBase, evaluate_retrieval, load_registry

st.set_page_config(page_title="Global Knowledge Hub | EduBridge AI", page_icon="🌍", layout="wide")
st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#f5f7ff 0%,#f9fbff 55%,#eef8f8 100%)}
.kb-hero{padding:30px 34px;border-radius:24px;background:linear-gradient(115deg,#171a35,#343477 62%,#087f8c);color:white;margin:8px 0 24px}
.kb-hero h1{color:white!important;font-size:38px;margin:0 0 8px}
.kb-hero p{color:#e3e9ff;font-size:15px;margin:0;max-width:820px}
</style>
""",unsafe_allow_html=True)
registry=load_registry()
kb=EducationalKnowledgeBase(registry)
st.markdown('<div class="kb-hero"><div style="font-size:12px;letter-spacing:2px;font-weight:800;color:#c9f27b">EDUBRIDGE INTELLIGENCE</div><h1>Global Knowledge Hub</h1><p>Explore qualification systems, retrieve source-linked guidance and inspect the evidence behind every indexed answer.</p></div>',unsafe_allow_html=True)
coverage=registry["coverage"]
a,b,c=st.columns(3)
a.metric("Indexed official sources",len(kb.documents))
b.metric("Systems tracked",len(coverage))
c.metric("Research pending",sum(x["status"]=="discovery_pending" for x in coverage))

search_tab,coverage_tab,eval_tab=st.tabs(["🔎 Ask the knowledge base","🌐 Global coverage","🧪 Retrieval evaluation"])
with search_tab:
    st.subheader("Ask an examination or qualification question")
    st.caption("This first release searches reviewed official-source notes. It does not yet ingest every full syllabus or generate unrestricted AI answers.")
    query=st.text_input("Your question",placeholder="How does Cambridge decide grade thresholds?")
    f1,f2,f3=st.columns(3)
    jurisdictions=["Any jurisdiction"]+sorted({x["jurisdiction"] for x in kb.documents})
    qualifications=["Any qualification"]+sorted({x["qualification"] for x in kb.documents})
    jurisdiction=f1.selectbox("Jurisdiction",jurisdictions)
    qualification=f2.selectbox("Qualification",qualifications)
    top_k=f3.selectbox("Sources to retrieve",[3,5,8],index=1)
    if st.button("Search verified knowledge",type="primary",use_container_width=True):
        results=kb.search(query,jurisdiction=None if jurisdiction=="Any jurisdiction" else jurisdiction,qualification=None if qualification=="Any qualification" else qualification,top_k=top_k)
        if not results:
            st.warning("No reviewed source matched. Try another wording or check coverage. EduBridge will not invent an answer.")
        else:
            st.success(f"Found {len(results)} relevant official source record(s).")
            for i,item in enumerate(results,1):
                with st.container(border=True):
                    st.markdown(f"**{i}. {item['title']}**")
                    st.caption(f"{item['publisher']} · {item['jurisdiction']} · {item['qualification']} · relevance {item['relevance_score']:.3f}")
                    for note in item["matched_notes"]:
                        st.markdown(f"- {note}")
                    st.info(item.get("limits","Check the linked official document for the exact subject and examination session."))
                    st.link_button("Open official source ↗",item["source_url"])
    st.markdown("**Try asking:**")
    st.write("How are Cambridge grade thresholds decided? · Where does FBISE publish HSSC model papers? · Does IB use internal and external assessment? · What is NECO SSCE External?")

with coverage_tab:
    st.subheader("Qualification-system coverage")
    st.caption("Coverage status measures our research progress, not the quality or completeness of an education system.")
    frame=pd.DataFrame(coverage)
    counts=frame.groupby(["jurisdiction","status"]).size().reset_index(name="systems")
    chart=px.bar(counts,x="jurisdiction",y="systems",color="status",barmode="stack",title="Tracked pathways by jurisdiction and research status")
    chart.update_layout(xaxis_title="",yaxis_title="Tracked pathways",legend_title="Research status")
    st.plotly_chart(chart,use_container_width=True)
    for region in sorted(frame["jurisdiction"].unique()):
        subset=frame[frame["jurisdiction"]==region]
        with st.expander(f"{region} · {len(subset)} tracked pathways"):
            for _,row in subset.iterrows():
                mark="🟢 Source reviewed" if row["status"]=="verified_snippet" else "🟡 Research pending"
                st.markdown(f"**{row['system']}** — {row['qualification']}  \n{mark}  \nNext: {row['next_task']}")
                for source_id in row["source_ids"]:
                    source=next(s for s in registry["sources"] if s["source_id"]==source_id)
                    st.markdown(f"[{source['title']}]({source['source_url']})")

with eval_tab:
    st.subheader("Measure retrieval instead of guessing")
    cases_path=Path(__file__).resolve().parents[1]/"data"/"knowledge"/"evaluation_cases.json"
    cases=json.loads(cases_path.read_text(encoding="utf-8"))
    report=evaluate_retrieval(kb,cases,top_k=5)
    x,y,z=st.columns(3)
    x.metric("Evaluation questions",report["total_cases"])
    y.metric("Source Recall@5",f"{report['recall_at_k']:.0%}")
    z.metric("Mean reciprocal rank",f"{report['mrr_at_k']:.3f}")
    st.caption(report["warning"])
    st.dataframe(pd.DataFrame(report["results"]),use_container_width=True,hide_index=True)
    st.download_button("Download evaluation report",json.dumps(report,indent=2),"edubridge_retrieval_evaluation.json","application/json")
st.divider()
st.caption("EduBridge AI · Phase 6 foundation · Verify the exact qualification, subject, level and examination session against the official source.")
