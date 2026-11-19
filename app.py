from __future__ import annotations

import json
from datetime import date, timedelta
from urllib.parse import quote

import pandas as pd
import plotly.express as px
import streamlit as st

from src.account_store import (get_supabase_client, restore_auth_session, save_auth_session, clear_auth_session, load_learner_profile, save_learner_profile, delete_learner_profile)
from src.student_guidance import LEVELS, LEVEL_SUBJECTS, PATHWAYS, build_learning_snapshot, build_weekly_plan
from src.modeling import ARTIFACTS, run_experiment
from src.profile_export import build_profile_pdf
from src.research_ui import render_research_lab
from src.feedback import ALLOWED_CATEGORIES, ALLOWED_WORKSPACES, validate_feedback

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

/* Phase 3: career studio + weekly planner */
.pathway-banner {position:relative;overflow:hidden;border-radius:24px;padding:28px 30px;color:#fff;background:linear-gradient(115deg,#1b1d3d 0%,#4d43b8 58%,#1e9ca8 100%);box-shadow:0 18px 42px rgba(47,47,115,.15);margin:12px 0 22px;}
.pathway-banner:after {content:"";position:absolute;width:220px;height:220px;right:-45px;top:-115px;border:1px solid rgba(255,255,255,.25);border-radius:50%;box-shadow:0 0 0 22px rgba(255,255,255,.05),0 0 0 48px rgba(255,255,255,.035);}
.pathway-icon {font-size:42px;line-height:1;margin-bottom:14px;}
.pathway-banner h2 {color:#fff!important;margin:0 0 8px;font-size:clamp(24px,3vw,34px)!important;}
.pathway-banner p {color:#e8eaff;margin:0;max-width:760px;line-height:1.65;}
.pathway-chip {display:inline-block;margin:5px 5px 5px 0;padding:8px 12px;border-radius:999px;background:#f0efff;border:1px solid #e4e1ff;color:#5145c4;font-size:12px;font-weight:700;}
.pathway-tile {height:100%;min-height:150px;background:#fff;border:1px solid #e7e9f5;border-radius:18px;padding:19px;box-shadow:0 8px 22px rgba(34,38,82,.04);}
.pathway-tile .tile-icon {font-size:25px;margin-bottom:10px;}
.pathway-tile h4 {font-size:15px;margin:0 0 7px;}
.pathway-tile p {font-size:12px;color:#69718f;line-height:1.55;margin:0;}
.week-day {height:100%;min-height:180px;background:#fff;border:1px solid #e7e9f5;border-radius:17px;padding:15px;box-shadow:0 7px 20px rgba(34,38,82,.035);}
.week-day .day-label {font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:#6657df;}
.week-day .day-count {font-family:'Space Grotesk',sans-serif;font-size:25px;font-weight:700;color:#202247;margin:4px 0 10px;}
.week-day .day-empty {font-size:12px;color:#8a90a8;line-height:1.5;}
.planner-progress {border-radius:18px;padding:20px 22px;background:linear-gradient(105deg,#f0efff,#e7fbfc);border:1px solid #e2e5fa;}
@media (max-width:800px) {.pathway-banner {padding:22px;border-radius:20px;} .week-day {min-height:0;padding:13px;}}

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

/* Student-pilot polish: subtle depth, clear focus states and motion-safe hover feedback. */
.dash-card {
  position:relative;
  overflow:hidden;
  transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.dash-card:before {
  content:"";
  position:absolute;
  inset:0 auto 0 0;
  width:4px;
  background:linear-gradient(180deg,#6757f5,#27c9d2,#c7f36b);
  opacity:.85;
}
.dash-card:hover {
  transform:translateY(-4px);
  border-color:#c9c5ff;
  box-shadow:0 16px 34px rgba(47,45,118,.11);
}
.dash-card .card-icon {
  background:linear-gradient(135deg,#efedff 0%,#e5fbfc 100%);
  box-shadow:inset 0 0 0 1px rgba(103,87,245,.07);
}
.pathway-tile,.week-day {
  transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.pathway-tile:hover,.week-day:hover {
  transform:translateY(-3px);
  border-color:#c9c5ff;
  box-shadow:0 14px 30px rgba(47,45,118,.09);
}
.stButton button:focus-visible,.stDownloadButton button:focus-visible,
input:focus-visible,textarea:focus-visible {
  outline:3px solid rgba(39,201,210,.65)!important;
  outline-offset:2px!important;
}
@media (prefers-reduced-motion: reduce) {
  .dash-card,.pathway-tile,.week-day,.stButton button,.stDownloadButton button {
    transition:none!important;
  }
  .dash-card:hover,.pathway-tile:hover,.week-day:hover,.stButton button:hover,.stDownloadButton button:hover {
    transform:none!important;
  }
}
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
    pending_workspace = st.session_state.pop("navigate_to_workspace", None)
    if pending_workspace in ["Dashboard", "My learning profile", "Career pathways", "Study planner", "Research insights", "Student feedback", "Account & privacy", "About EduBridge"]:
        st.session_state["workspace"] = pending_workspace
    page = st.radio("WORKSPACE", ["Dashboard", "My learning profile", "Career pathways", "Study planner", "Research insights", "Student feedback", "Account & privacy", "About EduBridge"], label_visibility="visible", key="workspace")
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

def auth_error_message(error: Exception, action: str) -> str:
    """Map common Supabase Auth failures to safe, actionable user guidance."""
    message = str(error).lower()
    if any(token in message for token in ("email_not_authorized", "email address not authorized", "not authorized to send")):
        return "Supabase's default email service only sends to authorised project-team addresses. Configure a custom SMTP provider in Supabase Auth → SMTP Settings before expecting confirmation emails to reach other addresses."
    if any(token in message for token in ("over_email_send_rate_limit", "email rate limit", "429")):
        return "Supabase's email limit has been reached. Please wait before requesting another message; repeated clicks will not speed up delivery."
    if any(token in message for token in ("already registered", "user already exists")):
        return "An account may already exist for this address. Try signing in, or use the resend-confirmation form if the address is still unverified."
    if any(token in message for token in ("invalid login credentials", "email not confirmed")):
        return "Sign-in was not completed. Check the email and password, and make sure the email address has been confirmed."
    if any(token in message for token in ("password", "weak_password")):
        return "Supabase rejected that password. Choose a longer password that meets the project's password policy."
    if action == "signup":
        return "Account creation could not be completed. Check Supabase Authentication logs for the exact provider error, then try again later."
    if action == "resend":
        return "The confirmation message could not be requested. Check the Auth logs and email-provider settings, and avoid repeated requests."
    return "Sign-in could not be completed. Check your credentials and Supabase Auth logs."

def profile_ready() -> bool:
    return isinstance(st.session_state.learner_profile, dict) and bool(st.session_state.learner_profile.get("confidence"))

profile = st.session_state.learner_profile

def render_share_strip() -> None:
    """Offer social share links without collecting recipient addresses."""
    app_url = "https://educationbridge-ai.streamlit.app/"
    title = "Try EduBridge AI"
    message = "Explore EduBridge AI, a student-centred learning and career companion."
    encoded_url = quote(app_url, safe="")
    encoded_title = quote(title, safe="")
    encoded_message = quote(message, safe="")
    st.markdown(
        '<div class="dash-kicker">✦ PASS IT FORWARD</div>'
        '<div class="dash-heading" style="font-size:22px">Know someone who would find this useful?</div>'
        '<p class="dash-subheading">Share the public website. No recipient email address is collected or displayed here.</p>',
        unsafe_allow_html=True,
    )
    share_cols = st.columns(5, gap="small")
    share_links = [
        ("Facebook", f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"),
        ("WhatsApp", f"https://wa.me/?text={encoded_message}%20{encoded_url}"),
        ("LinkedIn", f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}"),
        ("X", f"https://twitter.com/intent/tweet?text={encoded_title}&url={encoded_url}"),
        ("Email", f"mailto:?subject={encoded_title}&body={encoded_message}%0A{encoded_url}"),
    ]
    for column, (label, target) in zip(share_cols, share_links):
        with column:
            st.link_button(label, target, use_container_width=True)
    with st.expander("Share on Instagram"):
        st.caption("Copy the website address below and paste it into an Instagram message, story link or bio.")
        st.code(app_url, language=None)


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
                    st.session_state["navigate_to_workspace"] = "Study planner"
                    st.rerun()
                if st.button("Update my learning profile", use_container_width=True, key="dash_edit_profile"):
                    st.session_state["navigate_to_workspace"] = "My learning profile"
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
                    st.session_state["navigate_to_workspace"] = destination
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
                    st.session_state["navigate_to_workspace"] = destination
                    st.rerun()
        st.info("Your dashboard will show personal analytics after you add a learning profile. No sample scores or made-up progress are displayed.")

    else:
        hero("Your learning journey, upgraded.", "Explore your next direction, build better study habits and understand the data behind education — all in one student-first space.", "WELCOME TO EDUBRIDGE")
        render_share_strip()
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
                    st.session_state["navigate_to_workspace"] = "Career pathways"
                    st.session_state["career_pathway_select"] = name
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
                    st.session_state["navigate_to_workspace"] = destination
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
        pdf_bytes = build_profile_pdf(st.session_state.learner_profile)
        st.download_button(
            "Download my learning profile (PDF)",
            data=pdf_bytes,
            file_name="edubridge_learning_profile.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            help="A printable summary of the learning information you entered.",
        )
        with st.expander("Need a machine-readable backup?"):
            st.download_button(
                "Download profile data (JSON)",
                data=json.dumps(st.session_state.learner_profile, indent=2),
                file_name="edubridge_learning_profile.json",
                mime="application/json",
                help="JSON is intended for data portability and technical use.",
            )

elif page == "Career pathways":
    hero("Explore your next chapter.", "A visual career studio for comparing fields, building foundations and discovering small projects you can actually try.", "CAREER STUDIO")
    pathway_names = list(PATHWAYS.keys())
    if st.session_state.get("career_pathway_select") not in pathway_names:
        st.session_state.pop("career_pathway_select", None)
    selected = st.selectbox("Choose a field to explore", pathway_names, key="career_pathway_select")
    item = PATHWAYS[selected]
    pathway_art = {
        "Engineering": ("⚙️", "Design, test and improve the systems people rely on."),
        "Computer Science & AI": ("💻", "Turn logic, code and data into useful tools."),
        "Medicine & Health Sciences": ("🧬", "Explore life sciences, evidence and human wellbeing."),
        "Economics & Business": ("📈", "Understand choices, markets and how organisations work."),
        "Natural Sciences & Biotechnology": ("🔬", "Ask scientific questions and investigate the natural world."),
        "Social Sciences & Education": ("🌍", "Understand people, communities and how learning happens."),
        "Architecture & Design": ("🎨", "Shape spaces, products and digital experiences around people."),
    }
    icon, tagline = pathway_art.get(selected, ("✨", "Explore a field through curiosity and practical learning."))
    st.markdown(
        f'<div class="pathway-banner"><div class="pathway-icon">{icon}</div>'
        f'<h2>{selected}</h2><p>{tagline}</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Your field at a glance")
    st.write(item["description"])
    overview_cols = st.columns(3, gap="medium")
    overview = [
        ("🧭", "Preparation themes", f"{len(item['focus'])} broad subject areas"),
        ("🎓", "Degree directions", f"{len(item['degrees'])} degree areas to research"),
        ("🛠️", "Starter projects", f"{len(item['projects'])} practical ideas"),
    ]
    for col, (tile_icon, title, detail) in zip(overview_cols, overview):
        with col:
            st.markdown(
                f'<div class="pathway-tile"><div class="tile-icon">{tile_icon}</div>'
                f'<h4>{title}</h4><p>{detail}</p></div>',
                unsafe_allow_html=True,
            )
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown("### Skills & preparation")
        st.caption("These are broad exploration themes, not a universal admissions checklist.")
        chips = "".join(f'<span class="pathway-chip">{subject}</span>' for subject in item["focus"])
        st.markdown(chips, unsafe_allow_html=True)
        st.markdown("### Degree areas to investigate")
        for index, degree in enumerate(item["degrees"], start=1):
            st.markdown(f"**{index:02d} · {degree}**")
    with right:
        st.markdown("### Try a starter project")
        for index, project in enumerate(item["projects"], start=1):
            with st.container(border=True):
                st.markdown(f"**{index:02d} · {project}**")
                st.caption("Keep the scope small: define one question, build a first version and document what you learn.")
        st.markdown("### Free learning resources")
        for resource_title, resource_url in item.get("resources", []):
            st.markdown(f"- [{resource_title}]({resource_url})")
    if profile_ready():
        st.markdown("### How this connects with your learning profile")
        matches = [subject for subject in item["focus"] if subject in profile.get("subjects", [])]
        missing = [subject for subject in item["focus"] if subject not in profile.get("subjects", [])]
        match_cols = st.columns(2)
        match_cols[0].metric("Themes already in your profile", len(matches))
        match_cols[1].metric("Other themes to explore", len(missing))
        if matches:
            st.success("Already in your profile: " + ", ".join(matches))
        if missing:
            st.info("Not currently listed in your profile: " + ", ".join(missing))
        st.caption("This compares names in your self-reported subject list; it is not a suitability score or admissions assessment.")
        if st.button("Build a study plan around my profile", type="primary", use_container_width=True):
            st.session_state["navigate_to_workspace"] = "Study planner"
            st.rerun()
    else:
        st.info("You can explore every pathway without an account. Add a learning profile later if you want to compare these themes with your own subjects.")
    st.caption("University entry requirements vary by country, institution and programme. Always verify them on the official university website.")

elif page == "Study planner":
    hero("Make your week work for you.", "A flexible study planner built from your own subject-confidence ratings and weekly time budget — not generic productivity pressure.", "YOUR WEEKLY RESET")
    if not profile_ready():
        st.markdown('<div class="dash-band"><strong>Your planner starts with your learning profile.</strong><br><span class="small-muted">Add subjects, reflect on confidence and choose a realistic weekly study budget. EduBridge will then build a suggested allocation.</span></div>', unsafe_allow_html=True)
        if st.button("Create my learning profile", type="primary", use_container_width=True):
            st.session_state["navigate_to_workspace"] = "My learning profile"
            st.rerun()
    else:
        plan = build_weekly_plan(profile)
        total = sum(int(row["hours"]) for row in plan)
        st.markdown("### Your plan at a glance")
        k1, k2, k3 = st.columns(3)
        k1.metric("Planned focus time", f"{total} hrs", help="Based on the weekly hours you entered in your profile.")
        k2.metric("Focus subjects", len(plan))
        k3.metric("Weekly budget", f"{int(profile.get('weekly_hours', 0))} hrs")
        st.caption("This is a suggested allocation, not a requirement. Adjust it to your timetable, rest and other responsibilities.")
        st.markdown("### Time allocation")
        plan_frame = pd.DataFrame(plan).rename(columns={"subject": "Subject", "hours": "Hours", "activity": "Suggested activity"})
        plan_chart = px.bar(
            plan_frame, x="Hours", y="Subject", orientation="h", text="Hours",
            color="Subject", color_discrete_sequence=["#6757f5", "#27c9d2", "#ff8d75"],
        )
        plan_chart.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
        plan_chart.update_layout(
            height=max(250, 76 * len(plan)), margin=dict(l=8, r=30, t=18, b=12),
            showlegend=False, xaxis_title="Suggested hours this week", yaxis_title="",
            xaxis=dict(dtick=1, gridcolor="#eef0f8", zeroline=False),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#525a78"),
        )
        st.plotly_chart(plan_chart, use_container_width=True, config={"displayModeBar": False})
        st.markdown("### Your seven-day focus board")
        week_start = st.date_input("Choose the first day of your planning week", value=date.today(), key="planner_week_start")
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        monday = week_start - timedelta(days=week_start.weekday())
        blocks = []
        for row in plan:
            for _ in range(int(row["hours"])):
                blocks.append({"subject": row["subject"], "activity": row["activity"]})
        calendar = {day: [] for day in day_names}
        for index, block in enumerate(blocks):
            calendar[day_names[index % 7]].append(block)
        completed = 0
        for row_index in range(0, 7, 2):
            day_cols = st.columns(2, gap="medium")
            for offset, day in enumerate(day_names[row_index:row_index + 2]):
                with day_cols[offset]:
                    day_date = monday + timedelta(days=day_names.index(day))
                    entries = calendar[day]
                    st.markdown(
                        f'<div class="week-day"><div class="day-label">{day} · {day_date.strftime("%d %b")}</div>'
                        f'<div class="day-count">{len(entries)} <span style="font-size:12px;font-weight:600">focus block(s)</span></div>'
                        f'<div class="day-empty">{"Your suggested focus blocks are listed below." if entries else "Open space — keep it flexible."}</div></div>',
                        unsafe_allow_html=True,
                    )
                    if entries:
                        for block_index, block in enumerate(entries):
                            key = f"planner_done_{monday.isoformat()}_{day}_{block_index}"
                            st.checkbox(
                                f"{block['subject']} · 1 hour",
                                key=key,
                                help=block["activity"],
                            )
                            completed += int(bool(st.session_state.get(key, False)))
        st.markdown('<div class="planner-progress"><strong>Your session checklist</strong><br><span class="small-muted">Checked blocks: the count below reflects this browser session only. It is not saved study history.</span></div>', unsafe_allow_html=True)
        progress_cols = st.columns(2)
        progress_cols[0].metric("Blocks checked", f"{completed} / {len(blocks)}")
        progress_cols[1].metric("Checklist completion", f"{(completed / len(blocks) * 100):.0f}%" if blocks else "0%")
        st.progress(completed / len(blocks) if blocks else 0.0)
        st.markdown("### Your focus routine")
        for row in plan:
            with st.expander(f"{row['subject']} · {row['hours']} suggested hour(s)"):
                st.write(row["activity"])
                st.caption("Try a short review, a practice activity and a quick reflection. Take breaks and adapt the plan when needed.")
        st.caption("Your plan is generated from your saved learning profile. Checklist ticks are temporary and clear when the browser session ends.")

elif page == "Research insights":
    render_research_lab(hero)

elif page == "Account & privacy":
    hero("Your account, your learning space.", "Understand how sign-in works, what is saved and how to troubleshoot verification safely.", "ACCOUNT & PRIVACY")
    if not supabase:
        st.error("Supabase is not connected. Check the [deployment guide](https://github.com/MuhammadRafiq215/EduBridge-AI/blob/main/docs/DEPLOYMENT.md) and Streamlit Secrets.")
        st.code('[supabase]\nurl = "https://YOUR-PROJECT.supabase.co"\nanon_key = "YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY"', language="toml")
        st.warning("Never use a service-role key in this app. Keep row-level security enabled.")
    elif user:
        st.success(f"Signed in as {user.email}")
        st.write("Your profile is stored in the private student_profiles table and protected by row-level security.")
        if st.button("Delete my saved learning profile"):
            try:
                delete_learner_profile(supabase, str(user.id))
                st.session_state.learner_profile = None
                st.success("Your saved profile has been deleted.")
                st.rerun()
            except Exception as exc:
                st.error(auth_error_message(exc, "storage"))
        st.caption("Deleting the profile does not delete the login account; full account deletion needs a separately secured server-side process.")
    else:
        sign_in_tab, create_tab = st.tabs(["Sign in", "Create account"])
        with sign_in_tab:
            with st.form("sign_in_form"):
                email = st.text_input("Email address")
                password = st.text_input("Password", type="password")
                login = st.form_submit_button("Sign in", type="primary", use_container_width=True)
            if login:
                if not email.strip() or not password:
                    st.error("Enter both your email address and password.")
                else:
                    try:
                        response = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                        if response.session:
                            save_auth_session(response.session)
                            st.rerun()
                        st.error("No active session was returned. Your email may still need confirmation.")
                    except Exception as exc:
                        st.error(auth_error_message(exc, "signin"))
        with create_tab:
            st.write("Use an email address you can access. Do not enter identity numbers, home addresses or private documents.")
            with st.form("create_account_form"):
                new_email = st.text_input("Email address", key="signup_email")
                new_password = st.text_input("Password (at least 10 characters)", type="password", key="signup_password")
                confirm = st.text_input("Confirm password", type="password", key="signup_confirm")
                accepted = st.checkbox("I understand my learning profile will be stored in my account.")
                adult_review = st.checkbox("I am 18 or older, or my parent/guardian has reviewed and approved my use of this account.")
                signup = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if signup:
                if not accepted:
                    st.error("Please confirm the profile-storage notice.")
                elif not adult_review:
                    st.error("Please ask a parent or guardian to review and approve account use if you are under 18.")
                elif "@" not in new_email or "." not in new_email.rsplit("@", 1)[-1]:
                    st.error("Enter a valid email address.")
                elif len(new_password) < 10:
                    st.error("Use a password with at least 10 characters.")
                elif new_password != confirm:
                    st.error("The passwords do not match.")
                else:
                    try:
                        response = supabase.auth.sign_up({"email": new_email.strip(), "password": new_password})
                        if response.session:
                            save_auth_session(response.session)
                            st.success("Your account is ready.")
                            st.rerun()
                        st.success("If this address is eligible for registration, Supabase will send a confirmation email. Check Inbox, Spam and Promotions before requesting another message.")
                        st.info("Important: Supabase's built-in email service is limited to authorised project-team addresses and currently allows only two emails per hour across the project. For other recipients, the project owner must configure a supported custom SMTP provider.")
                    except Exception as exc:
                        st.error(auth_error_message(exc, "signup"))
            st.markdown("#### Didn't receive a confirmation email?")
            with st.form("resend_confirmation_form"):
                resend_email = st.text_input("Email address used for registration", key="resend_signup_email")
                resend = st.form_submit_button("Request another confirmation email", use_container_width=True)
            if resend:
                if "@" not in resend_email or "." not in resend_email.rsplit("@", 1)[-1]:
                    st.error("Enter the email address used during registration.")
                else:
                    try:
                        supabase.auth.resend({"type": "signup", "email": resend_email.strip()})
                        st.success("If a confirmation message can be sent for this address, Supabase will send a fresh one. Check Inbox, Spam and Promotions.")
                    except Exception as exc:
                        st.error(auth_error_message(exc, "resend"))
            st.caption("If the message still does not arrive, the project owner should check Supabase → Authentication → Logs and configure custom SMTP. Do not disable email confirmation as a workaround.")
    st.markdown("### Privacy")
    st.markdown("- Passwords are managed by Supabase Auth, not stored in learner profiles.")
    st.markdown("- Only enter education information needed for guidance; avoid sensitive personal details.")
    st.markdown("- Row-level security limits each account to its own profile.")
    st.markdown("- If you are under 18, involve a parent or guardian before creating an online account.")

elif page == "Student feedback":
    hero(
        "Help us make learning feel better.",
        "Tell us what worked, what felt confusing and what you would improve. Your feedback helps shape the next version.",
        "STUDENT VOICE",
    )
    st.markdown(
        '<div class="pathway-banner"><div class="pathway-icon">💬</div>'
        '<h2>Your experience matters.</h2>'
        '<p>Short, honest feedback is more useful than perfect feedback. You can submit without creating an account.</p></div>',
        unsafe_allow_html=True,
    )
    st.info(
        "Privacy first: this form does not ask for your name, email, phone number or school. "
        "Do not include personal details, passwords, identity numbers, private documents or information about another student. "
        "Submissions are stored for the project owner to review; other visitors cannot read them."
    )
    if not supabase:
        st.warning(
            "The feedback inbox needs the Supabase connection already used by EduBridge AI. "
            "Check the Streamlit Secrets setup in the deployment guide."
        )
    else:
        with st.form("student_feedback_form", clear_on_submit=True):
            category = st.selectbox(
                "What would you like to tell us?",
                sorted(ALLOWED_CATEGORIES),
            )
            workspace = st.selectbox(
                "Which part are you reviewing?",
                sorted(ALLOWED_WORKSPACES),
            )
            rating = st.radio(
                "How was your overall experience?",
                [1, 2, 3, 4, 5],
                horizontal=True,
                format_func=lambda value: f"{value} / 5",
            )
            message = st.text_area(
                "Your suggestion or issue",
                placeholder="For example: I liked the pathway ideas, but I could not find the next step…",
                max_chars=1000,
                help="Please write 10–1,000 characters. Do not include personal or sensitive information.",
            )
            confirmed = st.checkbox(
                "I have not included personal, identifying or sensitive information."
            )
            submitted = st.form_submit_button(
                "Send feedback",
                type="primary",
                use_container_width=True,
            )
        if submitted:
            if not confirmed:
                st.error("Please confirm that your feedback contains no personal or sensitive information.")
            else:
                payload, error = validate_feedback(category, workspace, rating, message)
                if error:
                    st.error(error)
                else:
                    try:
                        supabase.table("student_feedback").insert(payload).execute()
                        st.success("Thank you — your feedback has been submitted.")
                        st.caption("No contact details were requested. The form stores only the page, category, rating and comment you submitted.")
                    except Exception:
                        st.error(
                            "The feedback inbox is not ready yet. The project owner needs to run "
                            "supabase/feedback_schema.sql once in the Supabase SQL Editor."
                        )
                        with st.expander("Setup instructions"):
                            st.markdown(
                                "[Open the feedback database setup file on GitHub](https://github.com/MuhammadRafiq215/EduBridge-AI/blob/main/supabase/feedback_schema.sql)"
                            )
    st.caption(
        "Feedback is for improving the website's usability. It is not used to assess students or predict academic outcomes."
    )

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
