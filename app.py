from __future__ import annotations

import json
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from src.account_store import (get_supabase_client, restore_auth_session, save_auth_session, clear_auth_session, load_learner_profile, save_learner_profile, delete_learner_profile)
from src.student_guidance import LEVELS, LEVEL_SUBJECTS, PATHWAYS, build_learning_snapshot, build_weekly_plan
from src.modeling import ARTIFACTS, run_experiment

st.set_page_config(page_title="EduBridge AI", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root {
  --ink:#171a35; --muted:#68708d; --paper:#f6f7ff; --line:#e7e9f5;
  --violet:#6757f5; --cyan:#27c9d2; --lime:#c7f36b; --coral:#ff8d75;
}
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:radial-gradient(circle at 88% 4%,rgba(103,87,245,.09),transparent 24%),var(--paper);color:var(--ink);}
header[data-testid="stHeader"] {background:rgba(246,247,255,.78);}
.main .block-container {max-width:1440px;padding:2rem 2.5rem 3.5rem;}
section[data-testid="stSidebar"] {background:linear-gradient(180deg,#171a35 0%,#242653 100%);border-right:0;}
section[data-testid="stSidebar"] * {color:#f6f7ff;}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {padding:10px 12px;border-radius:12px;transition:background .18s ease;}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {background:rgba(255,255,255,.10);}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:#b9bddb;}
section[data-testid="stSidebar"] hr {border-color:rgba(255,255,255,.14);}
h1,h2,h3,h4 {font-family:'Space Grotesk',sans-serif;color:var(--ink)!important;letter-spacing:-.035em;}
h2 {font-size:1.8rem!important;} h3 {font-size:1.3rem!important;}
.hero {position:relative;isolation:isolate;overflow:hidden;padding:38px 42px;border-radius:28px;background:linear-gradient(112deg,#171a35 0%,#292b67 58%,#5144c9 100%);color:#fff;margin:4px 0 28px;box-shadow:0 22px 55px rgba(44,42,112,.18);min-height:220px;}
.hero:before {content:"";position:absolute;z-index:-1;width:330px;height:330px;right:8%;top:-185px;border:1px solid rgba(255,255,255,.16);border-radius:50%;box-shadow:0 0 0 28px rgba(255,255,255,.035),0 0 0 58px rgba(255,255,255,.025);}
.hero:after {content:"";position:absolute;z-index:-1;width:250px;height:250px;right:13%;bottom:-190px;border-radius:50%;background:radial-gradient(circle,rgba(39,201,210,.45),rgba(39,201,210,0) 68%);}
.hero-inner {display:flex;align-items:center;justify-content:space-between;gap:24px;}
.hero-copy {max-width:760px;}
.hero .eyebrow {display:inline-flex;align-items:center;gap:8px;font-size:11px;letter-spacing:1.8px;font-weight:800;color:#d5f879;text-transform:uppercase;background:rgba(199,243,107,.12);border:1px solid rgba(199,243,107,.25);padding:7px 11px;border-radius:999px;}
.hero h1 {color:#fff!important;font-size:clamp(30px,4.3vw,49px);line-height:1.08;margin:15px 0 12px;max-width:760px;}
.hero p {color:#e0e3ff;font-size:16px;line-height:1.65;max-width:720px;margin:0;}
.hero-art {width:210px;min-width:170px;filter:drop-shadow(0 16px 24px rgba(0,0,0,.16));}
.hero-art svg {width:100%;height:auto;display:block;}
.section-card {background:#fff;border:1px solid var(--line);border-radius:20px;padding:22px 24px;margin-bottom:14px;box-shadow:0 8px 24px rgba(34,38,82,.045);}
.small-muted {color:var(--muted);font-size:13px;}
div[data-testid="stMetric"] {background:linear-gradient(145deg,#fff,#fbfbff);border:1px solid var(--line);border-radius:18px;padding:18px 18px;box-shadow:0 8px 22px rgba(34,38,82,.045);min-height:112px;}
div[data-testid="stMetricLabel"] p {color:#747b99;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;}
div[data-testid="stMetricValue"] {font-family:'Space Grotesk',sans-serif;color:#252653;font-weight:700;}
.stButton button,.stDownloadButton button {border-radius:12px;font-weight:700;min-height:44px;border:1px solid #dedff2;transition:transform .16s ease,box-shadow .16s ease;}
.stButton button[kind="primary"],.stFormSubmitButton button[kind="primary"] {background:linear-gradient(100deg,#6556ed,#8a62f5);border:0;color:white;box-shadow:0 8px 18px rgba(103,87,245,.22);}
.stButton button:hover,.stDownloadButton button:hover {transform:translateY(-1px);box-shadow:0 10px 22px rgba(45,45,100,.12);border-color:#b8b6f5;}
.stTabs [data-baseweb="tab"] {font-weight:700;}
.stTabs [aria-selected="true"] {color:#6556ed!important;}
div[data-testid="stForm"] {background:#fff;border:1px solid var(--line);border-radius:20px;padding:22px;box-shadow:0 8px 24px rgba(34,38,82,.04);}
div[data-baseweb="input"]>div,div[data-baseweb="select"]>div,div[data-testid="stTextInput"] input {border-radius:11px!important;}
div[data-testid="stDataFrame"],div[data-testid="stTable"] {border:1px solid var(--line);border-radius:16px;overflow:hidden;}
div[data-testid="stAlert"] {border-radius:14px;}
.stProgress>div>div>div>div {background:linear-gradient(90deg,#6757f5,#27c9d2);}
@media (max-width:800px) {
 .main .block-container {padding:1rem 1rem 2rem;}
 .hero {padding:26px 24px;border-radius:22px;min-height:0;}
 .hero-art {width:120px;min-width:100px;}
 .hero h1 {font-size:32px;}
 .hero p {font-size:14px;}
}
@media (max-width:520px) {.hero-art {display:none;}}

/* Phase 2 dashboard system */
.dash-kicker {display:inline-flex;align-items:center;gap:8px;color:#6255e9;font-size:11px;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;margin:2px 0 10px;}
.dash-heading {font-family:'Space Grotesk',sans-serif;font-size:clamp(25px,3vw,36px);font-weight:700;letter-spacing:-1.4px;color:#1b1d3d;line-height:1.12;margin:0 0 8px;}
.dash-subheading {font-size:15px;color:#69718f;line-height:1.65;margin:0 0 20px;}
.dash-card {height:100%;background:linear-gradient(145deg,#fff 0%,#fbfbff 100%);border:1px solid #e7e9f5;border-radius:20px;padding:22px;box-shadow:0 10px 28px rgba(35,38,85,.055);}
.dash-card .card-icon {display:grid;place-items:center;width:42px;height:42px;border-radius:14px;background:#efedff;color:#6255e9;font-size:21px;margin-bottom:15px;}
.dash-card h3 {font-family:'Space Grotesk',sans-serif;font-size:18px;color:#202247;margin:0 0 8px;letter-spacing:-.4px;}
.dash-card p {font-size:13px;line-height:1.6;color:#6c7390;margin:0;}
.dash-card .card-meta {display:inline-block;margin-top:15px;padding:5px 9px;border-radius:999px;background:#f0efff;color:#6255e9;font-size:10px;font-weight:800;letter-spacing:.7px;text-transform:uppercase;}
.dash-band {border-radius:22px;padding:23px 25px;background:linear-gradient(105deg,#f0efff 0%,#e9fbfc 100%);border:1px solid #e2e5fa;}
.dash-band strong {color:#262858;}
.dash-divider {height:1px;background:#e9eaf5;margin:22px 0;}
.dash-stat-note {font-size:11px;color:#7c829d;margin-top:4px;}
div[data-testid="stPlotlyChart"] {background:#fff;border:1px solid #e9eaf5;border-radius:18px;padding:8px 8px 0;box-shadow:0 8px 24px rgba(34,38,82,.035);}
@media (max-width:800px) {.dash-card {padding:17px;border-radius:17px;} .dash-heading {font-size:27px;}}
</style>
""", unsafe_allow_html=True)

supabase = get_supabase_client()
user = restore_auth_session(supabase) if supabase else None
if "learner_profile" not in st.session_state:
    st.session_state.learner_profile = None
if user and st.session_state.get("profile_loaded_for") != str(user.id):
    try:
        st.session_state.learner_profile = load_learner_profile(supabase, str(user.id))
        st.session_state["profile_loaded_for"] = str(user.id)
        st.session_state.pop("profile_load_error", None)
    except Exception:
        st.session_state.learner_profile = None
        st.session_state["profile_load_error"] = True

with st.sidebar:
    st.markdown("## 🎓 EduBridge AI")
    st.caption("YOUR LEARNING & CAREER COMPANION")
    if st.session_state.pop("navigate_to_profile", False):
        st.session_state["workspace"] = "My learning profile"
    if st.session_state.pop("navigate_to_account", False):
        st.session_state["workspace"] = "Account & privacy"
    page = st.radio("WORKSPACE", ["Dashboard", "My learning profile", "Career pathways", "Study planner", "Research insights", "Account & privacy", "About EduBridge"], label_visibility="visible", key="workspace")
    st.divider()
    if user:
        st.success("Signed in")
        st.caption(user.email or "Student account")
        if st.button("Sign out", use_container_width=True):
            try:
                supabase.auth.sign_out()
            finally:
                clear_auth_session()
                st.rerun()
    elif supabase:
        st.info("Sign in to save your learning profile.")
    else:
        st.warning("Student accounts need Supabase setup.")
    st.caption("A student-centred learning companion")
    st.caption("Your profile stays in this browser session unless you download it.")

def hero(title: str, subtitle: str, eyebrow: str = "LEARN · EXPLORE · GROW"):
    st.markdown(f"""
    <div class="hero">
      <div class="hero-inner">
        <div class="hero-copy">
          <div class="eyebrow">✦ {eyebrow}</div>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
        <div class="hero-art" aria-hidden="true">
          <svg viewBox="0 0 220 190" role="img" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="ebGlow" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#c7f36b"/><stop offset="1" stop-color="#27c9d2"/></linearGradient>
              <linearGradient id="ebCard" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".98"/><stop offset="1" stop-color="#dfe5ff" stop-opacity=".92"/></linearGradient>
            </defs>
            <circle cx="112" cy="92" r="77" fill="none" stroke="#ffffff" stroke-opacity=".20" stroke-width="1.5" stroke-dasharray="4 7"/>
            <circle cx="112" cy="92" r="57" fill="url(#ebGlow)" opacity=".18"/>
            <rect x="53" y="48" width="118" height="91" rx="17" fill="url(#ebCard)" transform="rotate(-7 112 94)"/>
            <rect x="69" y="67" width="38" height="38" rx="12" fill="#6656ed"/>
            <path d="M80 87l8 8 14-18" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <rect x="116" y="70" width="39" height="7" rx="3.5" fill="#292b67" opacity=".82"/>
            <rect x="116" y="84" width="29" height="6" rx="3" fill="#9ba1c7"/>
            <rect x="69" y="117" width="86" height="7" rx="3.5" fill="#c6cbe4"/>
            <circle cx="174" cy="37" r="13" fill="#c7f36b"/><path d="M174 30v14M167 37h14" stroke="#20234d" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="38" cy="137" r="10" fill="#27c9d2"/><path d="M34 137l3 3 6-7" fill="none" stroke="#172044" stroke-width="2" stroke-linecap="round"/>
            <circle cx="183" cy="151" r="5" fill="#ff8d75"/><circle cx="40" cy="42" r="4" fill="#c7f36b"/>
          </svg>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def profile_ready() -> bool:
    return isinstance(st.session_state.learner_profile, dict) and bool(st.session_state.learner_profile.get("confidence"))

profile = st.session_state.learner_profile

if page == "Dashboard":
    if user and profile_ready():
        snapshot = build_learning_snapshot(profile)
        hero("Your next move starts here.", "A clearer view of what you're learning, what needs attention and what you can do next.", "YOUR LEARNING HQ")
        st.markdown(f'<div class="dash-kicker">✦ PERSONAL LEARNING SNAPSHOT</div><div class="dash-heading">Welcome back to your workspace.</div><p class="dash-subheading">Your dashboard reflects the subjects and goals you entered. Update your profile whenever your priorities change.</p>', unsafe_allow_html=True)
        metrics = st.columns(4)
        metrics[0].metric("Subjects reviewed", snapshot["subjects_rated"])
        metrics[1].metric("Average confidence", f'{snapshot["average_confidence"]:.1f} / 5')
        metrics[2].metric("Weekly study budget", f'{int(profile.get("weekly_hours", 0))} hrs')
        metrics[3].metric("Learning stage", snapshot["confidence_label"])
        st.markdown('<div class="dash-divider"></div>', unsafe_allow_html=True)
        left, right = st.columns([1.25, 0.9], gap="large")
        with left:
            st.markdown("### Your subject pulse")
            st.caption("A visual summary of your own confidence ratings — not exam grades.")
            ratings_frame = pd.DataFrame(
                [{"Subject": name, "Confidence": int(score)} for name, score in profile["confidence"].items()]
            ).sort_values(["Confidence", "Subject"])
            chart = px.bar(
                ratings_frame, x="Confidence", y="Subject", orientation="h",
                range_x=[0, 5], text="Confidence",
                color="Confidence", color_continuous_scale=["#ff9b83", "#9a8cf8", "#27c9d2"],
            )
            chart.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
            chart.update_layout(
                height=max(280, 48 * len(ratings_frame)), margin=dict(l=8, r=28, t=12, b=12),
                coloraxis_showscale=False, xaxis_title="Self-rated confidence (1–5)",
                yaxis_title="", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans", color="#525a78"),
                xaxis=dict(range=[0, 5.6], dtick=1, gridcolor="#eef0f8", zeroline=False),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})
        with right:
            st.markdown("### Your next best moves")
            with st.container(border=True):
                st.markdown(f"**Current direction**  \n{snapshot['pathway']}")
                st.caption(f"{profile.get('level', 'Learning stage not set')} · {profile.get('programme') or 'Programme not specified'}")
                if snapshot["focus_subjects"]:
                    st.markdown("**Give a little extra attention to**")
                    for subject in snapshot["focus_subjects"]:
                        st.markdown(f"- {subject}")
                else:
                    st.markdown("**Keep your momentum**")
                    st.write("Your self-ratings show no immediate low-confidence focus area. Choose a stretch topic that interests you.")
                st.divider()
                if st.button("Open my study planner", type="primary", use_container_width=True, key="dash_open_planner"):
                    st.session_state["workspace"] = "Study planner"
                    st.rerun()
                if st.button("Update my learning profile", use_container_width=True, key="dash_edit_profile"):
                    st.session_state["workspace"] = "My learning profile"
                    st.rerun()
        st.markdown("### Your weekly game plan")
        plan = build_weekly_plan(profile)
        plan_cols = st.columns(min(3, len(plan)))
        for index, row in enumerate(plan):
            with plan_cols[index % len(plan_cols)]:
                st.markdown(
                    f'<div class="dash-card"><div class="card-icon">◷</div><h3>{row["subject"]}</h3>'
                    f'<p>{row["activity"]}</p><span class="card-meta">{row["hours"]} hour(s) this week</span></div>',
                    unsafe_allow_html=True,
                )
        st.caption("Ticking a focus block below is a temporary browser-session checklist; it is not stored as completed study history.")
        with st.expander("Track today's focus blocks"):
            for row in plan:
                st.checkbox(
                    f"{row['subject']} focus block ({row['hours']} hour(s))",
                    key=f"dash_focus_{row['subject']}",
                )
        st.markdown("### Keep exploring")
        action_cols = st.columns(3)
        actions = [
            ("Career pathways", "Explore degree families, preparation areas and starter projects.", "Explore pathways"),
            ("Research insights", "Inspect reproducible machine-learning experiments and their limits.", "Visit research lab"),
            ("My learning profile", "Refresh your subjects, interests and confidence reflections.", "Edit profile"),
        ]
        for col, (destination, description, label) in zip(action_cols, actions):
            with col:
                st.markdown(
                    f'<div class="dash-card"><div class="card-icon">✦</div><h3>{destination}</h3><p>{description}</p></div>',
                    unsafe_allow_html=True,
                )
                if st.button(label, use_container_width=True, key=f"dash_go_{destination}"):
                    st.session_state["workspace"] = destination
                    st.rerun()
        st.caption("Everything above is derived from your saved profile or clearly marked session-only interactions. EduBridge AI does not predict grades, admissions or individual outcomes.")

    elif user:
        hero("Your learning HQ is ready.", "Start with a few learning details. EduBridge will organise your subjects and turn your priorities into a practical plan.", "LET'S GET STARTED")
        st.markdown('<div class="dash-kicker">✦ YOUR FIRST STEPS</div><div class="dash-heading">Build a workspace that feels like yours.</div><p class="dash-subheading">Your account is signed in, but you have not saved a learning snapshot yet. Add only the education details you need for guidance.</p>', unsafe_allow_html=True)
        setup_cols = st.columns(3)
        setup_cards = [
            ("01", "Set your learning profile", "Choose your level, subjects, field of interest and confidence ratings.", "My learning profile"),
            ("02", "Explore possible directions", "Compare broad degree families, preparation areas and project ideas.", "Career pathways"),
            ("03", "Turn priorities into a plan", "Create a realistic weekly allocation from your own study-time estimate.", "Study planner"),
        ]
        for col, (number, title, description, destination) in zip(setup_cols, setup_cards):
            with col:
                st.markdown(
                    f'<div class="dash-card"><div class="card-icon">{number}</div><h3>{title}</h3><p>{description}</p></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Open workspace", use_container_width=True, key=f"setup_{number}"):
                    st.session_state["workspace"] = destination
                    st.rerun()
        st.info("Your dashboard will show personal analytics after you add a learning profile. No sample scores or made-up progress are displayed.")

    else:
        hero("Your learning journey, upgraded.", "Explore your next direction, build better study habits and understand the data behind education — all in one student-first space.", "WELCOME TO EDUBRIDGE")
        st.markdown('<div class="dash-kicker">✦ ONE SPACE. MORE POSSIBILITIES.</div><div class="dash-heading">Less guesswork. More direction.</div><p class="dash-subheading">A learning companion for curious students — designed to make academic planning feel clearer, more visual and more actionable.</p>', unsafe_allow_html=True)
        feature_cols = st.columns(3, gap="large")
        feature_cards = [
            ("01", "Know your learning style", "Organise your subjects and reflect on where you feel confident or want more practice.", "PERSONAL PROFILE"),
            ("02", "Explore what comes next", "Browse broad degree pathways, useful preparation areas and small projects to try.", "CAREER DISCOVERY"),
            ("03", "Make your time count", "Turn your own priorities and available hours into a manageable weekly plan.", "STUDY PLANNING"),
        ]
        for col, (number, title, description, meta) in zip(feature_cols, feature_cards):
            with col:
                st.markdown(
                    f'<div class="dash-card"><div class="card-icon">{number}</div><h3>{title}</h3><p>{description}</p><span class="card-meta">{meta}</span></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("### Explore a few pathways")
        pathway_cols = st.columns(4, gap="medium")
        pathway_preview = [
            ("Computer Science & AI", "Logic · Programming · Data"),
            ("Engineering", "Mathematics · Physics · Design"),
            ("Medicine & Health Sciences", "Biology · Chemistry · Evidence"),
            ("Economics & Business", "Analysis · Markets · Decisions"),
        ]
        for col, (name, tags) in zip(pathway_cols, pathway_preview):
            with col:
                st.markdown(
                    f'<div class="dash-card"><div class="card-icon">✧</div><h3>{name}</h3><p>{tags}</p></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Explore", use_container_width=True, key=f"guest_path_{name}"):
                    st.session_state["workspace"] = "Career pathways"
                    st.session_state["selected_pathway"] = name
                    st.rerun()
        st.markdown('<div class="dash-band"><strong>Built around real learning inputs.</strong><br><span class="small-muted">Personal dashboards use the learner’s own profile. Research results come from documented public datasets. Empty states stay honest — no fabricated streaks, scores or activity counts.</span></div>', unsafe_allow_html=True)
        st.markdown("### Jump into the platform")
        jump_cols = st.columns(3)
        for col, destination, label in zip(
            jump_cols,
            ["Career pathways", "Research insights", "About EduBridge"],
            ["Discover careers", "Explore the research", "See how it works"],
        ):
            with col:
                if st.button(label, use_container_width=True, key=f"guest_jump_{destination}"):
                    st.session_state["workspace"] = destination
                    st.rerun()
        st.caption("You can explore public learning and research features without signing in. Account features are subject to the service's eligibility requirements.")

elif page == "My learning profile":
    if not user:
        st.warning("You can explore the app, but sign in or create an account before saving a permanent learning profile. Open Account & privacy in the sidebar.")
    hero("Tell us about your learning.", "A few details help organise your subjects and suggest practical next steps.", "YOUR PROFILE")
    st.markdown("### Education and interests")
    with st.form("learner_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            level = st.selectbox("Current education level", LEVELS, index=2)
            institution = st.text_input("School, college or university (optional)", max_chars=100)
            board = st.selectbox("Curriculum / programme", ["Cambridge", "FBISE", "Sindh Board", "Punjab Board", "Other board", "University semester", "Other / not sure"])
        with col2:
            pathway = st.selectbox("Field you're exploring", list(PATHWAYS.keys()))
            programme = st.text_input("Programme / group (optional)", placeholder="e.g. Pre-Medical, Pre-Engineering, BS Computer Science")
            current_year = st.text_input("Current class, year or semester", placeholder="e.g. A2, Grade 11, BS Year 2 / Semester 3")
            weekly_hours = st.slider("Hours you can study each week", 1, 40, 8)
        available = LEVEL_SUBJECTS[level]
        suggested = [subject for subject in PATHWAYS[pathway]["focus"] if subject in available]
        subjects = st.multiselect("Subjects you're currently studying", available, default=suggested[:min(3, len(suggested))])
        st.markdown("#### How confident do you currently feel?")
        st.caption("Rate your own confidence from 1 (need more support) to 5 (comfortable). This is for planning, not grading.")
        ratings = {}
        latest_results = {}
        rating_cols = st.columns(2)
        for index, subject in enumerate(subjects):
            with rating_cols[index % 2]:
                ratings[subject] = st.slider(subject + " · confidence", 1, 5, 3, key=f"profile_rating_{subject}")
                latest_results[subject] = st.text_input(subject + " · latest result (optional)", max_chars=30, key=f"profile_result_{subject}", placeholder="e.g. A, B, 82%, 3.4 GPA")
        submitted = st.form_submit_button("Save my learning profile", type="primary", use_container_width=True)
    if submitted:
        if not subjects:
            st.error("Please choose at least one subject.")
        else:
            new_profile = {
                "level": level, "institution": institution.strip(), "board": board,
                "pathway": pathway, "programme": programme.strip(), "current_year": current_year.strip(),
                "weekly_hours": weekly_hours, "subjects": subjects,
                "confidence": ratings, "latest_results": latest_results, "updated": date.today().isoformat(),
            }
            if not user:
                st.error("Sign in first so this profile can be saved to your private account.")
            else:
                try:
                    save_learner_profile(supabase, str(user.id), new_profile)
                    st.session_state.learner_profile = new_profile
                    st.success("Your learning profile has been saved to your account.")
                    st.rerun()
                except Exception:
                    st.error("Profile storage is not ready. Run supabase/schema.sql in your Supabase project and check Streamlit secrets.")
    if profile_ready():
        st.divider()
        snapshot = build_learning_snapshot(st.session_state.learner_profile)
        a, b, c = st.columns(3)
        a.metric("Subjects reviewed", snapshot["subjects_rated"])
        b.metric("Average self-rating", f'{snapshot["average_confidence"]:.1f} / 5')
        c.metric("Learning stage", snapshot["confidence_label"])
        if any(value.strip() for value in st.session_state.learner_profile.get("latest_results", {}).values()):
            st.markdown("#### Your latest self-reported results")
            result_rows = [{"Subject": subject, "Result": value or "Not entered", "Confidence": f"{st.session_state.learner_profile['confidence'][subject]}/5"} for subject, value in st.session_state.learner_profile["latest_results"].items()]
            st.dataframe(pd.DataFrame(result_rows), use_container_width=True, hide_index=True)
        st.caption("Your profile is saved in your private Supabase account when signed in.")
        st.download_button("Download my profile (JSON)", json.dumps(st.session_state.learner_profile, indent=2), file_name="edubridge_learning_profile.json", mime="application/json")

elif page == "Career pathways":
    hero("Explore a direction that fits your interests.", "See common preparation areas and degree options. Always check the entry requirements of the universities you are considering.", "CAREER EXPLORER")
    selected = st.selectbox("Choose a field to explore", list(PATHWAYS.keys()))
    item = PATHWAYS[selected]
    st.markdown(f"### {selected}")
    st.write(item["description"])
    left, right = st.columns(2)
    with left:
        st.markdown("#### Common preparation areas")
        for subject in item["focus"]:
            st.markdown(f"- {subject}")
        st.markdown("#### Degree areas to explore")
        for degree in item["degrees"]:
            st.markdown(f"- {degree}")
    with right:
        st.markdown("#### Try a small project")
        for project in item["projects"]:
            st.markdown(f"- {project}")
        st.markdown("#### Free learning resources")
        for resource_title, resource_url in item.get("resources", []):
            st.markdown(f"- [{resource_title}]({resource_url})")
        st.info("These are broad orientation ideas, not official admission prerequisites. Requirements differ by country, university and programme.")
    if profile_ready():
        matches = [x for x in item["focus"] if x in profile.get("subjects", [])]
        st.markdown("#### Compare with your profile")
        st.write("Preparation areas already in your subject list: " + (", ".join(matches) if matches else "None yet — you can add relevant subjects in My learning profile."))

elif page == "Study planner":
    hero("Make a plan you can actually follow.", "Your plan uses the subjects you rated as needing more attention. Adjust your profile whenever your priorities change.", "WEEKLY STUDY PLAN")
    if not profile_ready():
        st.info("Create your learning profile first to generate a study plan.")
        if st.button("Open my learning profile"):
            st.session_state["navigate_to_profile"] = True
            st.rerun()
    else:
        plan = build_weekly_plan(profile)
        total = sum(row["hours"] for row in plan)
        st.metric("Planned study time", f"{total} hours / week")
        frame = pd.DataFrame(plan)
        st.dataframe(frame, use_container_width=True, hide_index=True)
        figure = px.pie(frame, values="hours", names="subject", hole=0.55, title="How your study time is allocated")
        figure.update_layout(margin=dict(t=55, b=10), height=350, legend_title_text="")
        st.plotly_chart(figure, use_container_width=True)
        st.markdown("#### A simple weekly routine")
        for row in plan:
            st.markdown(f"**{row['subject']} · {row['hours']} hour(s)** — {row['activity']}")
        st.caption("This is a suggested starting plan. Adapt it to your timetable, deadlines and wellbeing.")

elif page == "Research insights":
    hero("The science behind the guidance.", "Explore transparent machine-learning experiments separately from your personal learning profile.", "RESEARCH LAB")
    st.info("Research models use public, de-identified datasets. They do not analyse your personal profile or predict your individual academic future.")
    st.markdown("### Secondary-school benchmark")
    st.write("The UCI Student Performance dataset covers students from two Portuguese schools. It is useful for reproducible experiments, but it is not representative of Pakistani learners.")
    if st.button("Run benchmark experiment", type="primary"):
        with st.spinner("Downloading the public dataset and comparing models…"):
            try:
                results = run_experiment()
                st.success("Benchmark completed.")
                st.session_state["research_results"] = results
            except Exception as exc:
                st.error("The experiment could not be completed.")
                st.exception(exc)
    results = st.session_state.get("research_results")
    results_path = ARTIFACTS / "experiment_results.json"
    if results is None and results_path.exists():
        try:
            results = json.loads(results_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            results = None
    if results:
        comparison = pd.DataFrame(results["model_comparison"])
        st.markdown("#### Model comparison")
        show_cols = [c for c in ["model", "cv_accuracy_mean", "cv_balanced_accuracy_mean", "cv_precision_mean", "cv_recall_mean", "cv_f1_mean", "cv_roc_auc_mean"] if c in comparison]
        st.dataframe(comparison[show_cols].style.format({c: "{:.3f}" for c in show_cols if c != "model"}), use_container_width=True, hide_index=True)
        figure = px.bar(comparison, x="model", y="cv_f1_mean", error_y="cv_f1_std", title="Cross-validation F1 (training data only)", range_y=[0, 1])
        figure.update_layout(height=360, xaxis_title="", yaxis_title="Mean F1")
        st.plotly_chart(figure, use_container_width=True)
        metrics = results["test_metrics"]
        cols = st.columns(4)
        for col, label, key in zip(cols, ["F1", "Balanced accuracy", "Precision", "Recall"], ["f1", "balanced_accuracy", "precision", "recall"]):
            col.metric(label, f"{metrics[key]:.3f}")
        st.caption("The test set is held out from model selection. Metrics describe this dataset and split only; they are not evidence of local validity.")
    with st.expander("Other public datasets on the research roadmap"):
        st.markdown("- [Open University Learning Analytics Dataset (OULAD)](https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset) — 30,000+ higher-education registrations and online-learning activity. Its different population and task require a separate model, not pooled training.")
        st.markdown("- [Higher Education Students Performance Evaluation](https://archive.ics.uci.edu/dataset/856/higher+education+students+performance+evaluation) — a small 145-record benchmark from engineering and educational-science faculties; suitable for cautious exploratory comparison only.")
        st.markdown("- [Engineering student performance dataset](https://data.mendeley.com/datasets/83tcx8psxv/1) — a separate engineering-focused dataset; its schema and licence must be reviewed before integration.")

elif page == "Account & privacy":
    hero("Your account, your learning space.", "Create an account or sign in to save your learning profile across visits.", "ACCOUNT & PRIVACY")
    if not supabase:
        st.error("Supabase is not connected yet. Create a Supabase project, run supabase/schema.sql, then add the project URL and publishable/anon key to Streamlit Community Cloud Secrets.")
        st.code('[supabase]\nurl = "https://YOUR-PROJECT.supabase.co"\nanon_key = "YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY"', language="toml")
        st.warning("Never use a service-role key in this app. The publishable/anon key is safe only when row-level security is enabled.")
    elif user:
        st.success(f"Signed in as {user.email}")
        st.write("Your profile is stored in the private student_profiles table and protected by row-level security.")
        if st.button("Delete my saved learning profile"):
            try:
                delete_learner_profile(supabase, str(user.id))
                st.session_state.learner_profile = None
                st.success("Your saved profile has been deleted.")
                st.rerun()
            except Exception:
                st.error("Could not delete your profile. Check database policies.")
        st.caption("Deleting the profile does not delete the login account; full account deletion needs a separately secured server-side process.")
    else:
        sign_in_tab, create_tab = st.tabs(["Sign in", "Create account"])
        with sign_in_tab:
            with st.form("sign_in_form"):
                email = st.text_input("Email address")
                password = st.text_input("Password", type="password")
                login = st.form_submit_button("Sign in", type="primary", use_container_width=True)
            if login:
                try:
                    response = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                    if response.session:
                        save_auth_session(response.session)
                        st.rerun()
                    st.error("No active session was returned. Verify your email if required.")
                except Exception:
                    st.error("Sign-in failed. Check your email, password and email-verification status.")
        with create_tab:
            st.write("Use an email address you can access. Do not enter identity numbers, home addresses or private documents.")
            with st.form("create_account_form"):
                new_email = st.text_input("Email address", key="signup_email")
                new_password = st.text_input("Password (at least 10 characters)", type="password", key="signup_password")
                confirm = st.text_input("Confirm password", type="password", key="signup_confirm")
                accepted = st.checkbox("I understand my learning profile will be stored in my account.")
                signup = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if signup:
                if not accepted:
                    st.error("Please confirm the profile-storage notice.")
                elif len(new_password) < 10:
                    st.error("Use a password with at least 10 characters.")
                elif new_password != confirm:
                    st.error("The passwords do not match.")
                else:
                    try:
                        response = supabase.auth.sign_up({"email": new_email.strip(), "password": new_password})
                        if response.session:
                            save_auth_session(response.session)
                            st.rerun()
                        st.success("Check your inbox to verify your email, then sign in.")
                    except Exception:
                        st.error("Account creation failed. Check the email and Supabase Auth settings.")
    st.markdown("### Privacy")
    st.markdown("- Passwords are managed by Supabase Auth, not stored in learner profiles.")
    st.markdown("- Only enter education information needed for guidance; avoid sensitive personal details.")
    st.markdown("- Run the supplied SQL so row-level security limits each account to its own profile.")
    st.markdown("- If you are under 18, involve a parent or guardian before creating an online account.")

elif page == "About EduBridge":
    hero("Education is a journey, not a single score.", "EduBridge AI brings learning reflection, career exploration and transparent educational data science into one student-friendly space.", "ABOUT")
    st.markdown("### What this platform does")
    st.markdown("- Helps learners organise subjects and self-assess confidence.")
    st.markdown("- Suggests study priorities and manageable weekly plans.")
    st.markdown("- Explains broad academic and career pathways.")
    st.markdown("- Demonstrates reproducible machine-learning research on public datasets.")
    st.markdown("### What it does not do")
    st.markdown("- It does not calculate admission chances, rank students or issue diagnoses.")
    st.markdown("- It does not use your profile to train a model.")
    st.markdown("- It does not claim that overseas datasets represent Pakistani students.")
    st.markdown("### Privacy")
    st.write("Do not enter passwords, identity numbers, private records or sensitive personal details. Your saved learning profile is stored in your Supabase account when the database is configured. Do not enter passwords, identity numbers, private records or sensitive personal details.")
    st.markdown("### Account registration")
    st.write("Student accounts use Supabase Auth. Profiles are stored in a PostgreSQL table protected by row-level security after the project owner completes the setup in docs/DEPLOYMENT.md.")
    st.markdown("### Research data")
    st.markdown("- [UCI Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance)")
    st.markdown("- [OULAD](https://analyse.kmi.open.ac.uk/open_dataset)")

st.divider()
st.caption("EduBridge AI · A student learning companion and educational data-science research prototype.")
