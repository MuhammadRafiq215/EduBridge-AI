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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
:root { --ink:#15253a; --muted:#62748a; --accent:#087f70; --line:#e5ecf1; }
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:#f5f8fa;color:var(--ink);}
section[data-testid="stSidebar"] {background:#ffffff;border-right:1px solid var(--line);}
h1,h2,h3 {font-family:'Manrope',sans-serif;color:#15253a !important;letter-spacing:-.025em;}
.hero {padding:34px 36px;border-radius:22px;background:linear-gradient(120deg,#102b3b 0%,#145c5b 58%,#168c79 100%);color:#fff;margin:4px 0 26px;}
.hero .eyebrow {font-size:11px;letter-spacing:2px;font-weight:800;color:#a7f3df;text-transform:uppercase;}
.hero h1 {color:#fff !important;font-size:clamp(28px,4vw,44px);line-height:1.12;margin:12px 0;}
.hero p {color:#d9f2ed;font-size:16px;max-width:760px;margin-bottom:0;}
.section-card {background:#fff;border:1px solid #e5ecf1;border-radius:16px;padding:20px 22px;margin-bottom:12px;}
.small-muted {color:#62748a;font-size:13px;}
div[data-testid="stMetric"] {background:#fff;border:1px solid #e5ecf1;border-radius:14px;padding:14px;}
.stButton button,.stDownloadButton button {border-radius:10px;font-weight:700;min-height:42px;}
.stTabs [data-baseweb="tab"] {font-weight:700;}
div[data-testid="stForm"] {background:#fff;border:1px solid #e5ecf1;border-radius:16px;padding:18px;}
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
    page = st.radio("WORKSPACE", ["Home", "My learning profile", "Career pathways", "Study planner", "Research insights", "Account & privacy", "About EduBridge"], label_visibility="visible", key="workspace")
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
    st.markdown(f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

def profile_ready() -> bool:
    return isinstance(st.session_state.learner_profile, dict) and bool(st.session_state.learner_profile.get("confidence"))

profile = st.session_state.learner_profile

if page == "Home":
    hero("Your next step starts here.", "Understand your current learning priorities, explore degree pathways, and build a study plan around your goals.")
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("### A clearer route through education")
        st.write("EduBridge helps you organise what you're studying, what you want to pursue, and what you can work on next.")
        st.markdown("""
        <div class="section-card"><b>01 · Understand your position</b><br><span class="small-muted">Add your education level, subjects and confidence ratings.</span></div>
        <div class="section-card"><b>02 · Explore your direction</b><br><span class="small-muted">Compare preparation areas for engineering, computing, medicine, economics and more.</span></div>
        <div class="section-card"><b>03 · Turn goals into action</b><br><span class="small-muted">Create a manageable weekly plan and track your learning priorities.</span></div>
        """, unsafe_allow_html=True)
        if st.button("Build my learning profile", type="primary", use_container_width=True):
            st.session_state["navigate_to_profile"] = True
            st.rerun()
    with right:
        if profile_ready():
            snapshot = build_learning_snapshot(profile)
            st.markdown("### Your latest snapshot")
            st.metric("Self-rated confidence", f'{snapshot["average_confidence"]:.1f} / 5')
            st.write(f'**Current direction:** {snapshot["pathway"]}')
            st.write(f'**Education level:** {snapshot["level"]}')
            st.write("**Next focus:** " + (", ".join(snapshot["focus_subjects"]) or "Explore an advanced topic"))
        else:
            st.markdown("### What you can explore")
            st.markdown('<div class="section-card"><h3>Engineering</h3><p class="small-muted">Mathematics · Physics · Design</p></div><div class="section-card"><h3>Medicine & health</h3><p class="small-muted">Biology · Chemistry · Evidence</p></div><div class="section-card"><h3>Economics & business</h3><p class="small-muted">Mathematics · Economics · Analysis</p></div><div class="section-card"><h3>Computing & AI</h3><p class="small-muted">Logic · Programming · Mathematics</p></div>', unsafe_allow_html=True)
    st.info("EduBridge offers learning guidance and reflection. It does not estimate admission chances or make decisions about students.")

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
        sign_in_tab, create_tab, reset_tab = st.tabs(["Sign in", "Create account", "Reset password"])
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
        with reset_tab:
            with st.form("reset_password_form"):
                reset_email = st.text_input("Account email")
                reset = st.form_submit_button("Send password reset email")
            if reset:
                try:
                    supabase.auth.reset_password_for_email(reset_email.strip())
                    st.success("If the account exists, Supabase will send a password-reset email.")
                except Exception:
                    st.error("Could not send the reset email. Check Supabase Auth email settings.")
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
    st.write("Do not enter passwords, identity numbers, private records or sensitive personal details. At this stage, profile information remains in the current session and can be downloaded by you.")
    st.markdown("### Account registration")
    st.write("Permanent registration and sign-in are not enabled yet. A secure authentication provider and private database must be configured before accounts can be offered safely.")
    st.markdown("### Research data")
    st.markdown("- [UCI Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance)")
    st.markdown("- [OULAD](https://analyse.kmi.open.ac.uk/open_dataset)")

st.divider()
st.caption("EduBridge AI · A student learning companion and educational data-science research prototype.")
