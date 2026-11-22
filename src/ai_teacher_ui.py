"""AI Teacher and Student Navigator interfaces for EduBridge AI."""
from __future__ import annotations

import html

import streamlit as st

from src.ai_teacher import build_profile_context, build_provider_from_settings, LocalModelProvider
from src.account_store import save_learner_profile
from src.adaptive_learning import normalise_topic_entry, summarise_topic_progress, build_adaptive_plan, build_revision_schedule
from src.chat_history_store import load_chat_history, save_chat_history, delete_chat_history
from src.specification_engine import (
    SpecificationQuery,
    build_specification_context,
    find_subject_catalogue,
    retrieve_specifications,
    specification_coverage_summary,
)
from src.student_navigator import build_navigation_plan, build_student_snapshot
from src.global_education import get_subject_options
from src.guided_practice import (build_offline_practice_scaffold, build_practice_generation_prompt, normalise_practice_attempt, normalise_practice_request)


def _configured_provider():
    try:
        settings = st.secrets.get("ai", {})
    except Exception:
        return None
    try:
        return build_provider_from_settings(dict(settings))
    except Exception as exc:
        st.session_state["ai_provider_configuration_error"] = str(exc)
        return None


def render_student_navigator(profile: dict | None, supabase=None, user_id: str | None = None) -> None:
    """Render a concise, action-first learning navigator."""
    st.markdown("""
    <style>
    .eb-nav-hero{padding:24px 26px;border-radius:22px;background:linear-gradient(115deg,#14213d,#5148c8 68%,#13a6a4);color:#fff;margin:5px 0 16px}
    .eb-nav-kicker{font-size:10px;font-weight:850;letter-spacing:1.7px;color:#e1ff8d}
    .eb-nav-hero h2{color:#fff!important;margin:8px 0 5px;font-size:clamp(25px,3.5vw,36px)!important}
    .eb-nav-hero p{color:#e8edff;margin:0;font-size:14px}
    .eb-nav-step{border:1px solid #e5e9f5;border-radius:18px;padding:17px 19px;background:linear-gradient(145deg,#fff,#f7f8ff);margin:8px 0}
    .eb-nav-step.primary{border-color:#d7d2ff;background:linear-gradient(120deg,#f1efff,#fff 75%)}
    .eb-nav-label{font-size:10px;letter-spacing:1.2px;text-transform:uppercase;font-weight:850;color:#6254d9}
    .eb-nav-step h3{font-size:19px!important;margin:7px 0 5px}
    .eb-nav-step p{font-size:13px;color:#64708a;margin:0}
    @media(max-width:650px){.eb-nav-hero{padding:21px;border-radius:18px}.eb-nav-step{padding:15px}}
    </style>
    <section class="eb-nav-hero">
      <div class="eb-nav-kicker">YOUR STUDY COMPASS</div>
      <h2>Know your next move.</h2>
      <p>One clear priority. A practical action. Progress you can understand.</p>
    </section>
    """, unsafe_allow_html=True)

    profile_data = dict(profile or {})
    topic_owner = user_id or "anonymous-session"
    if st.session_state.get("topic_progress_owner") != topic_owner:
        st.session_state["topic_progress_session"] = []
        st.session_state["topic_progress_owner"] = topic_owner

    history = st.session_state.get("ai_teacher_messages", [])
    snapshot = build_student_snapshot(profile_data, history)
    coverage = specification_coverage_summary()
    saved_entries = profile_data.get("topic_progress", [])
    if not isinstance(saved_entries, list):
        saved_entries = []
    session_entries = st.session_state.setdefault("topic_progress_session", [])
    combined_entries = (saved_entries + session_entries)[-300:]

    if snapshot["subjects"]:
        st.caption("YOUR SUBJECTS  ·  " + "  /  ".join(snapshot["subjects"][:6]))
        focus_options = ["Let EduBridge choose"] + snapshot["subjects"]
        focus = st.selectbox("What do you want to focus on?", focus_options, key=f"navigator_focus_subject_{topic_owner}")
        focus_subject = None if focus == "Let EduBridge choose" else focus
    else:
        focus_subject = None
        st.info("Add your subjects in My learning profile to unlock subject-specific guidance.")
        if st.button("Set up my learning profile", key="navigator_profile_setup", use_container_width=True):
            st.session_state["navigate_to_workspace"] = "My learning profile"
            st.rerun()

    plan = build_navigation_plan(snapshot, focus_subject=focus_subject)
    adaptive = build_adaptive_plan(combined_entries, limit=3)
    if focus_subject:
        adaptive = [item for item in adaptive if item["subject"] == focus_subject]
    if adaptive:
        first = adaptive[0]
        next_title = f"{first['subject']} · {first['topic']}"
        next_action = first["action"]
        next_reason = f"{first['priority']} · based on your latest topic record"
        next_label = first["priority"].upper()
    else:
        first = plan[0]
        next_title = first["title"]
        next_action = first["action"]
        next_reason = first["reason"]
        next_label = "RECOMMENDED NEXT STEP"

    st.markdown(
        f'<section class="eb-nav-step primary"><div class="eb-nav-label">{next_label}</div>'
        f'<h3>{html.escape(str(next_title))}</h3><p>{html.escape(str(next_action))}</p></section>',
        unsafe_allow_html=True,
    )
    action_cols = st.columns(2, gap="small")
    with action_cols[0]:
        if st.button("Ask AI Teacher", key="navigator_open_teacher", type="primary", use_container_width=True):
            st.session_state["navigate_to_workspace"] = "AI Teacher"
            st.rerun()
    with action_cols[1]:
        if st.button("Open study planner", key=f"navigator_open_planner_{topic_owner}", use_container_width=True):
            st.session_state["navigate_to_workspace"] = "Study planner"
            st.rerun()

    if adaptive and len(adaptive) > 1:
        st.markdown("#### Also worth your attention")
        for item in adaptive[1:3]:
            st.markdown(
                f'<section class="eb-nav-step"><div class="eb-nav-label">{item["priority"]}</div>'
                f'<h3>{html.escape(str(item["subject"]))} · {html.escape(str(item["topic"]))}</h3><p>{html.escape(str(item["action"]))}</p></section>',
                unsafe_allow_html=True,
            )
    elif len(plan) > 1:
        st.caption(f"Another idea: {plan[1]['title']} — {plan[1]['action']}")

    if snapshot["recent_questions"]:
        with st.expander("Continue a recent question"):
            for question in snapshot["recent_questions"][-3:]:
                st.markdown(f"- {question}")

    with st.expander("Specification evidence"):
        st.caption(
            f"{coverage['specification_verified']} verified specifications · "
            f"{coverage['verified_snippets']} reviewed summaries · "
            f"{coverage['discovery_pending_systems']} systems awaiting discovery"
        )
        st.caption("Coverage is not complete for every subject or exam year. Open official sources before relying on exam-specific details.")
    with st.expander("How your guidance works"):
        st.caption("Recommendations use the subjects and progress you choose to share. They are study suggestions, not predicted grades, admissions chances or formal assessments.")
        st.caption("Your recent questions are limited to this browser session. Saved topic records remain in your own learner profile when you choose to save them.")
        st.caption("Keep passwords and private records out of chat. EduBridge is a study aid, not a replacement for a teacher.")

    st.divider()
    st.markdown("### Your topic progress")
    st.caption("Log a topic after studying it. EduBridge will suggest what to revisit.")

    with st.expander("＋ Record a topic", expanded=not bool(combined_entries)):
        save_progress = st.checkbox(
            "Save to my signed-in profile",
            value=False,
            disabled=not bool(supabase and user_id),
            help="Saved only to your own learner profile.",
            key=f"save_topic_progress_{topic_owner}",
        )
        subject_options = sorted(set(get_subject_options()) | set(snapshot["subjects"]) | {"General study"})
        with st.form(f"topic_progress_form_{topic_owner}", clear_on_submit=True):
            subject_choice = st.selectbox("Subject", subject_options)
            topic_name = st.text_input("Topic", placeholder="e.g. Recursion or differentiation")
            confidence = st.slider("Confidence after studying", 1, 5, 3)
            attempted = st.number_input("Questions attempted", min_value=0, max_value=100, value=0, step=1)
            correct = st.number_input("Correct answers", min_value=0, max_value=100, value=0, step=1)
            submitted = st.form_submit_button("Save topic progress", type="primary", use_container_width=True)
        if submitted:
            try:
                entry = normalise_topic_entry(subject_choice, topic_name, confidence, int(attempted), int(correct))
                if save_progress and supabase and user_id:
                    updated = (saved_entries + [entry])[-300:]
                    profile_data["topic_progress"] = updated
                    save_learner_profile(supabase, user_id, profile_data)
                    st.session_state.learner_profile = profile_data
                    st.success("Saved to your private learner profile.")
                else:
                    session_entries.append(entry)
                    st.success("Saved for this browser session.")
                st.rerun()
            except (ValueError, TypeError) as exc:
                st.error(str(exc))
            except Exception:
                st.error("Could not save progress. Check your account connection and try again.")

    combined_entries = (saved_entries + session_entries)[-300:]
    summaries = summarise_topic_progress(combined_entries)
    if summaries:
        st.markdown("#### Recent signals")
        for row in summaries[:3]:
            accuracy = f"{row['practice_accuracy']:.0f}% practice accuracy" if row["practice_accuracy"] is not None else "No practice score yet"
            st.markdown(
                f'<section class="eb-nav-step"><div class="eb-nav-label">{html.escape(str(row["subject"]))} · {row["confidence"]}/5 confidence</div>'
                f'<h3>{html.escape(str(row["topic"]))}</h3><p>{html.escape(accuracy)} · {html.escape(row["evidence_level"].replace("_", " "))}</p></section>',
                unsafe_allow_html=True,
            )
        if len(summaries) > 3:
            with st.expander(f"See all {len(summaries)} topic records"):
                for row in summaries[3:]:
                    st.write(f"**{row['subject']} · {row['topic']}** — {row['progress_index']}/100 study signal")
        st.caption("Study signals combine your practice and self-reflection; they are not exam grades.")
    else:
        st.caption("Your progress timeline will appear here after your first topic record.")

    render_guided_practice(profile_data, supabase=supabase, user_id=user_id)

def render_guided_practice(profile: dict, supabase=None, user_id: str | None = None) -> None:
    """Render model-assisted practice with a transparent offline fallback."""
    st.divider()
    st.markdown("### ✦ Guided Practice")
    st.markdown(
        """
        <style>
        .eb-practice-intro {padding:19px 21px;margin:10px 0 17px;border-radius:18px;
          background:linear-gradient(110deg,#171a35,#343579 65%,#168d9a);color:#fff;}
        .eb-practice-intro strong {display:block;color:#fff;font-family:'Space Grotesk',sans-serif;font-size:20px;}
        .eb-practice-intro span {display:block;margin-top:5px;color:#e3e8ff;font-size:12px;line-height:1.55;}
        </style>
        <div class="eb-practice-intro"><strong>Understand · Practise · Reflect</strong>
        <span>A short, supportive practice cycle. Your reflection stays yours; EduBridge does not turn it into a formal grade.</span></div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Choose a topic, try a short set and get a next step. Model-assisted feedback appears only when an approved model is configured.")
    owner = str(user_id) if user_id else "anonymous-session"
    if st.session_state.get("guided_practice_owner") != owner:
        st.session_state.pop("guided_practice_active", None)
        st.session_state.pop("guided_practice_feedback", None)
        st.session_state["guided_practice_owner"] = owner

    subjects = profile.get("subjects", []) if isinstance(profile.get("subjects", []), list) else []
    subject_options = [value for value in subjects if isinstance(value, str) and value.strip()] or ["General study"]
    with st.form(f"guided_practice_setup_{owner}"):
        practice_subject = st.selectbox("Practice subject", subject_options)
        practice_topic = st.text_input("Topic to practise", placeholder="e.g. Recursion, differentiation, cell structure")
        left, right = st.columns(2)
        difficulty = left.selectbox("Difficulty", ["Foundations", "Developing", "Challenge"])
        practice_format = right.selectbox("Practice style", ["Mixed practice", "Recall and explain", "Apply a method", "Find and fix an error"])
        create_set = st.form_submit_button("Create my practice session", type="primary", use_container_width=True)

    if create_set:
        try:
            request = normalise_practice_request(practice_subject, practice_topic, difficulty, practice_format)
            provider = _configured_provider()
            if provider is not None:
                question = build_practice_generation_prompt(request)
                qualification = profile.get("qualification") or profile.get("custom_qualification")
                board = profile.get("board")
                country = profile.get("country")
                query = SpecificationQuery(
                    question=question,
                    jurisdiction=country,
                    qualification=qualification,
                    awarding_body=board,
                    subject=practice_subject,
                )
                records = retrieve_specifications(query)
                evidence = build_specification_context(records, query) if records else None
                generated = provider.answer([{"role": "user", "content": question}], knowledge_context=evidence)
                st.session_state["guided_practice_active"] = {
                    "request": request, "mode": "ai_generated", "question_set": generated,
                    "evidence": evidence, "records": records,
                }
            else:
                scaffold = build_offline_practice_scaffold(request)
                st.session_state["guided_practice_active"] = {
                    "request": request, "mode": "offline_scaffold", "scaffold": scaffold,
                    "evidence": None, "records": [],
                }
                st.info("No live model is connected. This is a general study scaffold, not an AI-generated or subject-marked question set.")
        except (ValueError, RuntimeError, OSError, KeyError) as exc:
            st.error(f"Practice session could not be created: {exc}")

    active = st.session_state.get("guided_practice_active")
    if isinstance(active, dict):
        request = active["request"]
        st.markdown(f"#### {request['subject']} · {request['topic']}")
        st.caption(f"{request['difficulty']} · {request['practice_format']}")
        if active["mode"] == "ai_generated":
            st.markdown(active["question_set"])
            if active.get("records"):
                with st.expander("Official source context for this practice set"):
                    for record in active["records"]:
                        st.markdown(
                            f"**[{record.get('source_id', 'Source')}] {record.get('title', 'Official source')}**  \\n"
                            f"{record.get('system', '')} · {record.get('status', '')}  \\n"
                            f"[Open official source]({record.get('source_url', '')})"
                        )
        else:
            for index, step in enumerate(active["scaffold"], start=1):
                with st.container(border=True):
                    st.markdown(f"**{index}. {step['step']}**")
                    st.write(step["task"])
                    st.caption(step["check"])

        st.markdown("#### Your attempt")
        with st.form(f"guided_practice_attempt_{owner}"):
            learner_answer = st.text_area("Write your answer or learning notes", max_chars=5000, height=140)
            reflection = st.radio(
                "How did this attempt feel?",
                ["I can explain it in my own words", "I understand some of it", "I need to review this topic"],
            )
            confidence = st.slider("Confidence after this attempt", 1, 5, 3)
            save_attempt = st.checkbox(
                "Save this topic reflection to my signed-in profile",
                value=False,
                disabled=not bool(supabase and user_id),
            )
            submit_attempt = st.form_submit_button("Review my attempt", type="primary", use_container_width=True)
        if submit_attempt:
            try:
                attempt = normalise_practice_attempt(request, learner_answer, confidence, reflection)
                feedback = (
                    "Your reflection has been recorded. Revisit your notes, compare your method with a worked example, "
                    "and ask a teacher to check any step you are unsure about. This offline mode does not mark answers."
                )
                if active["mode"] == "ai_generated":
                    provider = _configured_provider()
                    if provider is None:
                        raise RuntimeError("The AI provider is no longer available. Your written attempt was not sent.")
                    feedback = provider.answer(
                        [
                            {"role": "user", "content": build_practice_generation_prompt(request)},
                            {"role": "assistant", "content": active["question_set"]},
                            {"role": "user", "content": (
                                "Here is my attempt. Give supportive, age-appropriate formative feedback. "
                                "Identify what is clear, explain one improvement, show a worked correction only "
                                "where justified, and give one small next question. Do not assign a formal grade.\n\n"
                                + attempt["answer"]
                            )},
                        ],
                        knowledge_context=active.get("evidence"),
                    )
                progress_entry = normalise_topic_entry(
                    request["subject"], request["topic"], confidence, 0, 0
                )
                if save_attempt and supabase and user_id:
                    updated_profile = dict(profile)
                    saved = updated_profile.get("topic_progress", [])
                    if not isinstance(saved, list):
                        saved = []
                    updated_profile["topic_progress"] = (saved + [progress_entry])[-300:]
                    save_learner_profile(supabase, user_id, updated_profile)
                    st.session_state.learner_profile = updated_profile
                    st.success("Your reflection was saved to your private learner profile.")
                else:
                    st.session_state.setdefault("topic_progress_session", []).append(progress_entry)
                    st.success("Your reflection was added to this browser session.")
                st.session_state["guided_practice_feedback"] = feedback
                st.session_state.pop("guided_practice_active", None)
                st.rerun()
            except (ValueError, RuntimeError, OSError) as exc:
                st.error(f"Your attempt could not be reviewed: {exc}")

    feedback = st.session_state.get("guided_practice_feedback")
    if feedback:
        with st.container(border=True):
            st.markdown("#### Feedback and next step")
            st.markdown(feedback)
            st.caption("This is formative learning support, not a formal mark or prediction of exam performance.")
            if st.button("Start another practice session", key=f"new_guided_practice_{owner}"):
                st.session_state.pop("guided_practice_feedback", None)
                st.rerun()

    combined = (profile.get("topic_progress", []) if isinstance(profile.get("topic_progress", []), list) else [])
    combined += st.session_state.get("topic_progress_session", [])
    schedule = build_revision_schedule(combined)
    if schedule:
        st.markdown("#### Your suggested revision queue")
        for item in schedule:
            with st.container(border=True):
                st.markdown(f"**{item['subject']} · {item['topic']}** — review {item['review_on']}")
                st.caption(item["reason"])
                st.caption(item["basis"])
    st.caption("Revision dates are transparent rule-based suggestions. Topic signals are self-reported, not grades or diagnoses.")


def render_ai_teacher(profile: dict | None, supabase=None, user_id: str | None = None) -> None:
    st.markdown("""
    <style>
    .eb-ai-hero{position:relative;overflow:hidden;padding:30px 32px;border-radius:26px;background:linear-gradient(118deg,#171a35 0%,#343579 58%,#168d9a 100%);color:#fff;margin:2px 0 18px;box-shadow:0 18px 42px rgba(39,39,105,.16)}
    .eb-ai-hero:after{content:"";position:absolute;width:230px;height:230px;right:-65px;top:-135px;border:1px solid rgba(255,255,255,.22);border-radius:50%;box-shadow:0 0 0 25px rgba(255,255,255,.045),0 0 0 52px rgba(255,255,255,.03)}
    .eb-ai-kicker{font-size:10px;font-weight:800;letter-spacing:1.8px;color:#d8fa83;text-transform:uppercase}
    .eb-ai-hero h1{color:#fff!important;font-size:clamp(27px,3.8vw,42px);line-height:1.08;margin:10px 0}
    .eb-ai-hero p{color:#e5e8ff;max-width:760px;line-height:1.6;margin:0;font-size:14px}
    .eb-ai-pill{display:inline-block;padding:7px 11px;margin:14px 6px 0 0;border:1px solid rgba(255,255,255,.2);border-radius:999px;background:rgba(255,255,255,.1);color:#f5f6ff;font-size:11px;font-weight:700}
    .eb-ai-prompt{height:100%;min-height:94px;padding:14px 15px;border:1px solid #e5e7f5;border-radius:16px;background:linear-gradient(145deg,#fff,#f8f8ff);box-shadow:0 6px 18px rgba(36,39,85,.04)}
    .eb-ai-prompt strong{display:block;color:#292b67;font-size:13px;margin-bottom:5px}
    .eb-ai-prompt span{display:block;color:#737b98;font-size:11px;line-height:1.5}
    .eb-ai-note{padding:13px 15px;border:1px solid #e3e7f5;border-radius:14px;background:#f8f9ff;color:#505875;font-size:12px;line-height:1.55}
    .eb-ai-hero p{max-width:620px}
    div[data-testid="stChatMessage"]{max-width:900px;margin-inline:auto}
    div[data-testid="stChatInput"]{max-width:900px;margin-inline:auto}
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]{line-height:1.68}
    @media(max-width:700px){
      .eb-ai-hero{padding:21px 18px}
      .eb-ai-hero h1{font-size:clamp(25px,7vw,32px)}
      .eb-ai-pill{font-size:10px;padding:6px 9px;margin:10px 4px 0 0}
      div[data-testid="stChatMessage"]{padding:11px 12px}
    }
    div[data-testid="stChatMessage"]{border:1px solid #e9eaf5;border-radius:17px;padding:14px 16px;background:#fff;box-shadow:0 5px 18px rgba(38,40,88,.035)}
    @media(max-width:700px){.eb-ai-hero{padding:23px 21px;border-radius:20px}.eb-ai-hero h1{font-size:29px}}
    </style>
    <div class="eb-ai-hero">
      <div class="eb-ai-kicker">YOUR STUDY SPACE</div>
      <h1>Learn it. Practise it. Own it.</h1>
      <p>Subject-aware explanations, one clear step at a time.</p>
      <span class="eb-ai-pill">Subject-aware</span><span class="eb-ai-pill">Guided practice</span><span class="eb-ai-pill">Source-aware</span>
    </div>
    """, unsafe_allow_html=True)

    coverage = specification_coverage_summary()
    chat_owner = str(user_id) if user_id else "anonymous-session"
    if st.session_state.get("ai_teacher_owner") != chat_owner:
        st.session_state["ai_teacher_messages"] = []
        st.session_state.pop("ai_teacher_history_loaded_for", None)
        st.session_state.pop("ai_teacher_persist_history", None)
        st.session_state.pop("ai_teacher_use_profile", None)
        st.session_state["ai_teacher_owner"] = chat_owner
    if "ai_teacher_messages" not in st.session_state:
        st.session_state["ai_teacher_messages"] = []

    with st.expander("Source coverage", expanded=False):
        st.caption(coverage["coverage_warning"])
        st.caption(f"{coverage['specification_verified']} verified specifications · {coverage['source_records']} source records")

    persist_history = False
    if supabase is not None and user_id:
        persist_history = st.checkbox(
            "Save my chat history to my private account",
            value=False,
            key="ai_teacher_persist_history",
            help="Optional and off by default. Only text messages are saved; uploaded screenshots are not stored."
        )
        if persist_history and st.session_state.get("ai_teacher_history_loaded_for") != user_id:
            try:
                st.session_state["ai_teacher_messages"] = load_chat_history(supabase, user_id)
                st.session_state["ai_teacher_history_loaded_for"] = user_id
                st.success("Your saved conversation history is available in this workspace.")
            except Exception:
                st.warning("Saved history could not be loaded. Check that the Phase 7 database migration has been applied.")
        if persist_history and st.button("Delete all saved chat history", key="delete_saved_ai_teacher_history"):
            try:
                delete_chat_history(supabase, user_id)
                st.session_state["ai_teacher_messages"] = []
                st.session_state["ai_teacher_history_loaded_for"] = user_id
                st.success("Saved chat history deleted from your account.")
                st.rerun()
            except Exception:
                st.error("Saved history could not be deleted. Check the database migration and account connection.")
    else:
        st.caption("Sign in to use optional cross-session history. Without sign-in, the conversation stays in this browser session.")

    use_profile = False
    if isinstance(profile, dict) and profile:
        use_profile = st.checkbox(
            "Use my saved learning profile to personalise explanations",
            value=False,
            key="ai_teacher_use_profile",
        )
    context = build_profile_context(profile) if use_profile else {}
    context = context or {}

    with st.expander("🎯 Examination and subject context", expanded=not bool(context.get("qualification"))):
        col_a, col_b = st.columns(2)
        qualification = col_a.text_input(
            "Qualification",
            value=str(context.get("qualification") or context.get("custom_qualification") or ""),
            placeholder="e.g. Cambridge A Levels, WAEC WASSCE, IB Diploma",
            key=f"ai_teacher_qualification_{chat_owner}",
        )
        jurisdiction = col_b.text_input(
            "Country / jurisdiction",
            value=str(context.get("country", "")),
            placeholder="e.g. Pakistan, Nigeria, Türkiye",
            key=f"ai_teacher_jurisdiction_{chat_owner}",
        )
        col_c, col_d = st.columns(2)
        awarding_body = col_c.text_input(
            "Awarding body / examination authority",
            value=str(context.get("board", "")),
            placeholder="e.g. Cambridge International, Pearson Edexcel, FBISE",
            key=f"ai_teacher_awarding_body_{chat_owner}",
        )
        subject_values = context.get("subjects", [])
        default_subject = subject_values[0] if isinstance(subject_values, list) and subject_values else ""
        subject = col_d.text_input(
            "Subject",
            value=default_subject,
            placeholder="e.g. Mathematics, Biology, Computer Science",
            key=f"ai_teacher_subject_{chat_owner}",
        )
        col_e, col_f = st.columns(2)
        exam_year = col_e.text_input("Exam year (optional)", placeholder="e.g. 2027", key=f"ai_teacher_year_{chat_owner}")
        exam_series = col_f.text_input("Exam series (optional)", placeholder="e.g. May/June, October/November", key=f"ai_teacher_series_{chat_owner}")
    context.update({
        "qualification": qualification.strip(),
        "country": jurisdiction.strip(),
        "board": awarding_body.strip(),
        "subject": subject.strip(),
        "exam_year": exam_year.strip(),
        "exam_series": exam_series.strip(),
    })
    context = {key: value for key, value in context.items() if value not in ("", None, [], {})}

    st.markdown("#### Conversation")
    width_choice = st.select_slider(
        "Chat width",
        options=["Compact", "Balanced", "Wide"],
        value="Balanced",
        key="ai_teacher_chat_width",
        help="Choose a comfortable reading width. Your choice stays selected during this browser session.",
    )
    chat_width = {"Compact": "620px", "Balanced": "820px", "Wide": "1080px"}[width_choice]
    st.markdown(
        f"""<style>
        div[data-testid="stChatMessage"], div[data-testid="stChatInput"] {{
            width: min(100%, {chat_width}) !important;
            max-width: {chat_width} !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}
        @media(max-width:700px) {{
            div[data-testid="stChatMessage"], div[data-testid="stChatInput"] {{
                width:100% !important; max-width:100% !important;
            }}
        }}
        </style>""",
        unsafe_allow_html=True,
    )
    for message in st.session_state.ai_teacher_messages:
        if message.get("role") in {"user", "assistant"}:
            with st.chat_message(message["role"]):
                st.markdown(message.get("content", ""))

    provider = _configured_provider()
    provider_error = st.session_state.pop("ai_provider_configuration_error", None)
    if provider is None:
        if provider_error:
            st.error(f"AI provider configuration needs attention: {provider_error}")
        st.info("Study tools are available. Live AI tutoring is not connected yet.")
        st.markdown("### 📚 Search trusted study sources")
        st.caption("Find reviewed exam and qualification information. This mode does not generate AI answers.")
        offline_question = st.chat_input("Search reviewed exam and qualification information...", max_chars=4000)
        if offline_question:
            st.session_state.ai_teacher_messages.append({"role": "user", "content": offline_question})
            with st.chat_message("user"):
                st.markdown(offline_question)
            with st.chat_message("assistant"):
                with st.spinner("Searching reviewed EduBridge records..."):
                    try:
                        offline_query = SpecificationQuery(
                            question=offline_question,
                            jurisdiction=context.get("country"),
                            qualification=context.get("qualification"),
                            awarding_body=context.get("board"),
                            subject=context.get("subject"),
                            exam_year=context.get("exam_year"),
                            exam_series=context.get("exam_series"),
                        )
                        offline_records = retrieve_specifications(offline_query)
                        offline_catalogue = find_subject_catalogue(
                            offline_query.subject or "",
                            jurisdiction=offline_query.jurisdiction,
                            qualification=offline_query.qualification,
                        ) if offline_query.subject else []
                        if offline_records:
                            reply_lines = [
                                "**Offline source search results**",
                                "",
                                "These are retrieved records, not AI-generated teaching. Check that the jurisdiction, qualification, subject and examination session match your question.",
                            ]
                            for record in offline_records:
                                reply_lines.extend([
                                    "",
                                    f"**{record.get('title', 'Official source')}**",
                                    f"{record.get('publisher', record.get('system', 'Publisher not recorded'))} · {record.get('jurisdiction', 'Jurisdiction not recorded')} · {record.get('qualification', 'Qualification not recorded')}",
                                    f"Status: `{record.get('status', 'not recorded')}` · Reviewed: {record.get('reviewed_on', 'date not recorded')}",
                                ])
                                notes = record.get("matched_notes", record.get("verified_notes", []))
                                if notes:
                                    reply_lines.extend(["", "Reviewed notes:"] + [f"- {note}" for note in notes])
                                reply_lines.extend([
                                    "",
                                    f"Limits: {record.get('limits', 'Check the exact official document before relying on this information.')}",
                                    f"[Open official source]({record.get('source_url', '')})",
                                ])
                            answer = "\n".join(reply_lines)
                        elif offline_catalogue:
                            answer = (
                                "**A subject catalogue mention was found, but no reviewed specification matched.**\n\n"
                                + "\n".join(
                                    f"- {item.get('system')} · {item.get('qualification')} · {item.get('status')} — {item.get('note')}"
                                    for item in offline_catalogue
                                )
                                + "\n\nA catalogue entry is not a full syllabus or proof of current assessment rules."
                            )
                        else:
                            answer = (
                                "I couldn't find a matching reviewed source in the current EduBridge registry. "
                                "Try adding the awarding body, qualification, subject and exam session above. "
                                "This offline mode cannot provide a generated lesson; a configured model is required for conversational tutoring."
                            )
                        st.markdown(answer)
                        st.session_state.ai_teacher_messages.append({"role": "assistant", "content": answer})
                        if persist_history and supabase and user_id:
                            try:
                                save_chat_history(supabase, user_id, st.session_state.ai_teacher_messages)
                            except Exception:
                                st.warning("The source results were shown, but chat history could not be saved.")
                    except (RuntimeError, ValueError, OSError, KeyError) as exc:
                        st.error(f"Offline source search could not be completed: {exc}")
            st.rerun()
        with st.expander("How this study mode works"):
            st.write("Searches reviewed examination records and official links. Generated explanations and conversational tutoring require a separately configured model.")
        st.code(
            '[ai]\nprovider = "local"\nmodel = "YOUR_INSTALLED_MODEL_NAME"\nbase_url = "http://127.0.0.1:11434"\ntimeout = 120\nsupports_vision = false',
            language="toml",
        )
        st.caption("Important: local mode works when Streamlit and the model server run on the same computer. A Streamlit Cloud app cannot reach localhost on your laptop. For cloud hosting, use an external provider only when its account, age, privacy and service terms permit that deployment.")
        st.caption("Never paste API keys or passwords into this chat or commit them to GitHub.")
        return

    is_local = isinstance(provider, LocalModelProvider)
    st.success(f"AI runtime connected: {getattr(provider, 'provider_name', 'Configured AI provider')} · {provider.model}")
    if is_local:
        st.caption("Local mode: prompts are sent to the model server on this same machine. A cloud deployment would need a separately configured hosted runtime.")
    else:
        st.caption("Hosted mode: the latest 12 conversation messages and any enabled screenshot are sent to the configured provider. Review that provider's privacy and retention terms.")

    prompt_cols = st.columns(3)
    subject_hint = context.get("subject") or "my subject"
    prompts = [
        ("Explain a topic", f"Teach me a difficult topic in {subject_hint} step by step, with a simple example and one practice question."),
        ("Practise a question", f"Give me one appropriately challenging practice question in {subject_hint}. Wait for my attempt before giving feedback."),
        ("Plan my revision", "Help me build a realistic revision plan. Ask only for the details you need."),
    ]
    pending_question = st.session_state.pop("ai_teacher_pending_question", None)
    for index, (label, prompt_text) in enumerate(prompts):
        with prompt_cols[index]:
            if st.button(label, key=f"ai_teacher_prompt_{index}", use_container_width=True):
                st.session_state["ai_teacher_pending_question"] = prompt_text
                st.rerun()

    with st.expander("Privacy and safety"):
        st.caption("Profile details are shared only when you opt in. Chat history is saved only when you enable it. Never share passwords, identity numbers or private records. Check important exam facts against official sources.")
    uploaded = None
    if getattr(provider, "supports_vision", False):
        uploaded = st.file_uploader(
            "Attach a question screenshot (PNG, JPEG or WebP; maximum 5 MB)",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"ai_teacher_image_{chat_owner}",
        )
    else:
        st.caption("Screenshot input is hidden because image support is not enabled for this configured model.")

    question = st.chat_input("Ask your AI Teacher anything about learning...", max_chars=4000)
    if not question:
        question = pending_question

    if question:
        image = (uploaded.getvalue(), uploaded.type or "image/jpeg") if uploaded is not None else None
        user_message = {"role": "user", "content": question}
        st.session_state.ai_teacher_messages.append(user_message)
        with st.chat_message("user"):
            st.markdown(question)
            if uploaded is not None:
                st.image(uploaded, caption="Attached question", use_container_width=True)
        with st.chat_message("assistant"):
            with st.spinner("Checking the official-source registry and preparing your explanation..."):
                try:
                    spec_query = SpecificationQuery(
                        question=question,
                        jurisdiction=context.get("country"),
                        qualification=context.get("qualification"),
                        awarding_body=context.get("board"),
                        subject=context.get("subject"),
                        exam_year=context.get("exam_year"),
                        exam_series=context.get("exam_series"),
                    )
                    records = retrieve_specifications(spec_query)
                    catalogue = find_subject_catalogue(
                        spec_query.subject or "",
                        jurisdiction=spec_query.jurisdiction,
                        qualification=spec_query.qualification,
                    ) if spec_query.subject else []
                    evidence = build_specification_context(records, spec_query, catalogue)
                    if not records:
                        st.info("No matching reviewed source was found for this exact context. The answer will distinguish general teaching from verified board-specific rules.")
                    answer = provider.answer(
                        st.session_state.ai_teacher_messages[:-1] + [user_message],
                        profile_context=context if use_profile else None,
                        image=image,
                        knowledge_context=evidence,
                    )
                    st.markdown(answer)
                    if records:
                        with st.expander("📚 Official sources used"):
                            for record in records:
                                st.markdown(
                                    f"**[{record['source_id']}] {record.get('title', 'Official source')}**  \n"
                                    f"{record.get('system', '')} · {record.get('status', '')} · "
                                    f"Reviewed {record.get('reviewed_on', 'date not recorded')}  \n"
                                    f"[Open official source]({record['source_url']})"
                                )
                    st.session_state.ai_teacher_messages.append({"role": "assistant", "content": answer})
                    if persist_history and supabase and user_id:
                        try:
                            save_chat_history(supabase, user_id, st.session_state.ai_teacher_messages)
                        except Exception:
                            st.warning("Your answer was generated, but it could not be saved. Check the Phase 7 database migration.")
                except (RuntimeError, ValueError, OSError) as exc:
                    st.error(str(exc))
        st.rerun()

    if st.session_state.ai_teacher_messages:
        if st.button("Clear this browser session", key="clear_ai_teacher_session"):
            st.session_state["ai_teacher_messages"] = []
            st.rerun()
        if persist_history:
            st.caption("Private cross-session history is enabled. Use 'Delete all saved chat history' above to remove the stored copy.")
        else:
            st.caption("This conversation is temporary in the current browser session.")

