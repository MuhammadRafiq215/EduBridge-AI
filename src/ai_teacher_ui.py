"""AI Teacher and Student Navigator interfaces for EduBridge AI."""
from __future__ import annotations

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
    st.markdown("## 🧭 Student Navigator")
    st.write("A practical next-step guide based on your saved learning profile and the questions in your current browser session.")
    profile_data = dict(profile or {})
    topic_owner = user_id or "anonymous-session"
    if st.session_state.get("topic_progress_owner") != topic_owner:
        st.session_state["topic_progress_session"] = []
        st.session_state["topic_progress_owner"] = topic_owner
    history = st.session_state.get("ai_teacher_messages", [])
    snapshot = build_student_snapshot(profile_data, history)
    st.info(
        "EduBridge AI Teacher is an educational support tool, not a substitute for a teacher, parent or professional. "
        "Do not share passwords, identity numbers, private records or sensitive personal details. "
        "If a conversation raises a safety concern, please speak with a trusted adult. "
        "AI-generated explanations can be wrong; verify important exam information using the linked official sources."
    )

    coverage = specification_coverage_summary()
    first, second, third = st.columns(3)
    first.metric("Your subjects", len(snapshot["subjects"]))
    second.metric("Recent learning questions", len(snapshot["recent_questions"]))
    third.metric("Official source records", coverage["source_records"])
    st.caption(coverage["coverage_warning"])
    st.caption(f"Memory scope: {snapshot['memory_scope']}")
    if snapshot["qualification"] != "Not specified":
        st.write(
            f"**Qualification:** {snapshot['qualification']} · "
            f"**Country:** {snapshot['country']} · "
            f"**Awarding body:** {snapshot['awarding_body']}"
        )
    if snapshot["subjects"]:
        focus_options = ["Let EduBridge suggest"] + snapshot["subjects"]
        focus = st.selectbox("Choose your next subject focus", focus_options)
        focus_subject = None if focus == "Let EduBridge suggest" else focus
    else:
        focus_subject = None
        st.info("Add your qualification and subjects in My learning profile to make Navigator recommendations more relevant.")
    plan = build_navigation_plan(snapshot, focus_subject=focus_subject)
    st.markdown("### Your next steps")
    for index, item in enumerate(plan, start=1):
        with st.container(border=True):
            st.markdown(f"**{index}. {item['title']}**")
            st.caption(item["reason"])
            st.write(item["action"])
    if snapshot["recent_questions"]:
        with st.expander("Recent questions in this session"):
            for question in snapshot["recent_questions"]:
                st.markdown(f"- {question}")
    with st.expander("Specification coverage status"):
        st.metric("Verified subject specifications", coverage["specification_verified"])
        st.metric("Reviewed official summaries", coverage["verified_snippets"])
        st.metric("Discovery pending systems", coverage["discovery_pending_systems"])
        st.caption("A catalogue or reviewed summary is not the same as a complete subject specification.")
    st.caption("Navigator suggestions are planning support, not predicted grades, admission chances or formal academic assessments.")

    st.divider()
    st.markdown("### 📈 Topic progress and adaptive next steps")
    st.write("Record a topic after studying it. EduBridge combines your own confidence reflection with practice results; this is a planning signal, not an exam grade.")
    session_entries = st.session_state.setdefault("topic_progress_session", [])
    saved_entries = profile_data.get("topic_progress", []) if isinstance(profile_data.get("topic_progress", []), list) else []
    save_progress = st.checkbox(
        "Save topic progress to my signed-in learner profile",
        value=False,
        disabled=not bool(supabase and user_id),
        help="When enabled, the topic record is stored in your own profile under the existing account privacy rules."
    )
    subject_options = snapshot["subjects"] or ["General study"]
    with st.form("topic_progress_form", clear_on_submit=True):
        subject_choice = st.selectbox("Subject", subject_options)
        topic_name = st.text_input("Topic", placeholder="e.g. Recursion, differentiation, cell structure")
        confidence = st.slider("How confident do you feel after studying it?", 1, 5, 3)
        attempted = st.number_input("Practice questions attempted", min_value=0, max_value=100, value=0, step=1)
        correct = st.number_input("Correct answers", min_value=0, max_value=100, value=0, step=1)
        submitted = st.form_submit_button("Record topic progress", type="primary")
    if submitted:
        try:
            entry = normalise_topic_entry(subject_choice, topic_name, confidence, int(attempted), int(correct))
            if save_progress and supabase and user_id:
                updated = (saved_entries + [entry])[-300:]
                profile_data["topic_progress"] = updated
                save_learner_profile(supabase, user_id, profile_data)
                st.session_state.learner_profile = profile_data
                saved_entries = updated
                st.success("Topic progress saved to your private learner profile.")
            else:
                session_entries.append(entry)
                st.success("Topic progress recorded for this browser session.")
        except (ValueError, TypeError) as exc:
            st.error(str(exc))
        except Exception:
            st.error("Progress could not be saved. Check your account connection and try again.")

    combined_entries = (saved_entries + session_entries)[-300:]
    summaries = summarise_topic_progress(combined_entries)
    if summaries:
        st.markdown("#### Your latest topic signals")
        st.dataframe(
            [{
                "Subject": row["subject"],
                "Topic": row["topic"],
                "Practice accuracy": f'{row["practice_accuracy"]:.1f}%' if row["practice_accuracy"] is not None else "Not recorded",
                "Confidence": f'{row["confidence"]}/5',
                "Progress index": f'{row["progress_index"]}/100',
                "Evidence": "Stronger" if row["evidence_level"] == "practice_and_self_reflection" else "Provisional",
                "Last studied": row["studied_on"],
            } for row in summaries],
            use_container_width=True,
            hide_index=True,
        )
        st.caption("Progress index is a transparent 60% practice-accuracy + 40% self-reflection indicator. Fewer than five attempts are labelled provisional.")
        st.markdown("#### Suggested next actions")
        for item in build_adaptive_plan(combined_entries):
            st.markdown(f"**{item['subject']} · {item['topic']} — {item['priority']}**")
            st.write(item["action"])
            st.caption(item["basis"])
    else:
        st.info("No topic records yet. Add one above to start a personal progress timeline.")
    if not (supabase and user_id):
        st.caption("Sign-in is not connected in this session, so topic records remain temporary in this browser session.")

    render_guided_practice(profile_data, supabase=supabase, user_id=user_id)


def render_guided_practice(profile: dict, supabase=None, user_id: str | None = None) -> None:
    """Render model-assisted practice with a transparent offline fallback."""
    st.divider()
    st.markdown("### ✦ Guided Practice Studio")
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
    st.write("Choose one topic, attempt a short practice set and reflect on what you understand. When a model is configured, EduBridge can generate questions and formative feedback; otherwise it provides a clearly labelled self-guided study routine.")
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
    div[data-testid="stChatMessage"]{border:1px solid #e9eaf5;border-radius:17px;padding:14px 16px;background:#fff;box-shadow:0 5px 18px rgba(38,40,88,.035)}
    @media(max-width:700px){.eb-ai-hero{padding:23px 21px;border-radius:20px}.eb-ai-hero h1{font-size:29px}}
    </style>
    <div class="eb-ai-hero">
      <div class="eb-ai-kicker">✦ YOUR PERSONAL LEARNING SPACE</div>
      <h1>Meet your AI Teacher.</h1>
      <p>Ask freely, learn step by step, explore your exam specification and turn difficult topics into clear next actions.</p>
      <span class="eb-ai-pill">📘 Subject explanations</span>
      <span class="eb-ai-pill">🧭 Exam-board context</span>
      <span class="eb-ai-pill">📚 Reviewed-source search</span>
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

    metrics = st.columns(3)
    metrics[0].metric("Official source records", coverage["source_records"])
    metrics[1].metric("Verified subject specifications", coverage["specification_verified"])
    metrics[2].metric("Messages in this session", len(st.session_state.ai_teacher_messages))
    st.caption(coverage["coverage_warning"])

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

    for message in st.session_state.ai_teacher_messages:
        if message.get("role") in {"user", "assistant"}:
            with st.chat_message(message["role"]):
                st.markdown(message.get("content", ""))

    provider = _configured_provider()
    provider_error = st.session_state.pop("ai_provider_configuration_error", None)
    if provider is None:
        if provider_error:
            st.error(f"AI provider configuration needs attention: {provider_error}")
        st.warning("No live generative model is connected yet. You can still use the offline source helper below to search reviewed EduBridge education records.")
        st.markdown("### 📚 Offline source helper")
        st.caption("This mode searches EduBridge's reviewed source registry and subject catalogue. It does not generate AI explanations or send your question to an external model.")
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
        st.markdown("**What this mode can do**")
        st.write("- Search reviewed examination and qualification records.\n- Show source status, reviewed notes and official links.\n- Identify when the current registry does not contain enough evidence.")
        st.markdown("**What still needs a model connection**")
        st.write("Step-by-step generated explanations, follow-up tutoring and adaptive conversational responses.")
        st.markdown("**Local model option**")
        st.write("For private local testing, run a supported model server on the same computer as Streamlit. A Streamlit Cloud app cannot reach a model server running on your phone or laptop.")
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
    prompts = [
        ("Explain a difficult topic", "Explain recursion in computer science step by step, with a simple example and a short practice question."),
        ("Help me understand my syllabus", "Help me understand the key assessment requirements for my qualification. Separate verified specification facts from general guidance."),
        ("Build a revision plan", "Help me make a realistic one-week revision plan. Ask for any missing subjects or available study time."),
    ]
    pending_question = st.session_state.pop("ai_teacher_pending_question", None)
    for index, (label, prompt_text) in enumerate(prompts):
        with prompt_cols[index]:
            if st.button(label, key=f"ai_teacher_prompt_{index}", use_container_width=True):
                st.session_state["ai_teacher_pending_question"] = prompt_text
                st.rerun()

    st.markdown(
        '<div class="eb-ai-note">🔐 <strong>Privacy:</strong> profile information is only included when you opt in above. '
        'Conversation text is saved across sessions only when you enable private chat-history saving. '
        'Screenshots are sent to the configured model only when image support is enabled and are not saved in EduBridge chat history.</div>',
        unsafe_allow_html=True,
    )
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

