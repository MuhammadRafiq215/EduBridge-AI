"""AI Teacher and Student Navigator interfaces for EduBridge AI."""
from __future__ import annotations

import streamlit as st

from src.ai_teacher import OpenAICompatibleProvider, build_profile_context
from src.specification_engine import (
    SpecificationQuery,
    build_specification_context,
    find_subject_catalogue,
    retrieve_specifications,
    specification_coverage_summary,
)
from src.student_navigator import build_navigation_plan, build_student_snapshot


def _configured_provider():
    try:
        settings = st.secrets.get("ai", {})
        api_key = str(settings.get("api_key", "")).strip()
        model = str(settings.get("model", "")).strip()
        base_url = str(settings.get("base_url", "https://api.openai.com/v1")).strip()
    except Exception:
        return None
    if not api_key or not model:
        return None
    try:
        return OpenAICompatibleProvider(api_key=api_key, model=model, base_url=base_url)
    except ValueError:
        return None


def render_student_navigator(profile: dict | None) -> None:
    st.markdown("## 🧭 Student Navigator")
    st.write("A practical next-step guide based on your saved learning profile and the questions in your current browser session.")
    history = st.session_state.get("ai_teacher_messages", [])
    snapshot = build_student_snapshot(profile, history)
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


def render_ai_teacher(profile: dict | None) -> None:
    st.markdown("## 🤖 EduBridge AI Teacher")
    st.write("Ask a question about your studies, qualification, examination structure or subject content. Attach a screenshot when image input is supported by the configured provider.")
    coverage = specification_coverage_summary()
    st.caption(
        f"Knowledge registry: {coverage['source_records']} source records · "
        f"{coverage['specification_verified']} verified subject specifications."
    )
    st.caption("The number of source records does not mean complete coverage of any board.")
    provider = _configured_provider()
    if provider is None:
        st.info(
            "The AI Teacher interface is ready, but no AI provider is configured. "
            "It will not fabricate answers. Provider setup remains disabled until "
            "eligibility, privacy and data-handling terms have been checked."
        )
        st.write("The specification engine and Student Navigator can be explored without enabling an external AI provider.")
        return

    use_profile = False
    if isinstance(profile, dict) and profile:
        use_profile = st.checkbox("Use my saved education profile for personalised explanations", value=True)
    context = build_profile_context(profile) if use_profile else {}
    context = context or {}
    with st.expander("Examination context", expanded=not bool(context.get("qualification"))):
        qualification = st.text_input("Qualification", value=str(context.get("qualification") or context.get("custom_qualification") or ""), placeholder="e.g. Cambridge A Levels, WAEC WASSCE, IB Diploma")
        jurisdiction = st.text_input("Country / jurisdiction", value=str(context.get("country", "")), placeholder="e.g. Pakistan, Nigeria, Türkiye")
        awarding_body = st.text_input("Awarding body / examination authority", value=str(context.get("board", "")), placeholder="e.g. Cambridge International, Pearson Edexcel, FBISE")
        subject_values = context.get("subjects", [])
        default_subject = subject_values[0] if isinstance(subject_values, list) and subject_values else ""
        subject = st.text_input("Subject (optional)", value=default_subject, placeholder="e.g. Mathematics, Biology, Computer Science")
        exam_year = st.text_input("Exam year (optional)", placeholder="e.g. 2027")
        exam_series = st.text_input("Exam series (optional)", placeholder="e.g. May/June, October/November")
    context.update({
        "qualification": qualification.strip(),
        "country": jurisdiction.strip(),
        "board": awarding_body.strip(),
        "subject": subject.strip(),
        "exam_year": exam_year.strip(),
        "exam_series": exam_series.strip(),
    })
    context = {k: v for k, v in context.items() if v not in ("", None, [], {})}

    if "ai_teacher_messages" not in st.session_state:
        st.session_state.ai_teacher_messages = []
    for message in st.session_state.ai_teacher_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    uploaded = st.file_uploader(
        "Question screenshot (optional)",
        type=["png", "jpg", "jpeg", "webp"],
        key="ai_teacher_image",
        help="PNG, JPEG or WebP, maximum 5 MB.",
    )
    question = st.chat_input("Ask your AI Teacher...")
    if question:
        image = (uploaded.getvalue(), uploaded.type or "image/jpeg") if uploaded is not None else None
        user_message = {"role": "user", "content": question}
        st.session_state.ai_teacher_messages.append(user_message)
        with st.chat_message("user"):
            st.markdown(question)
            if uploaded is not None:
                st.image(uploaded, caption="Attached question", use_container_width=True)
        with st.chat_message("assistant"):
            with st.spinner("Searching reviewed sources and preparing your explanation..."):
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
                        st.info("No matching reviewed source was retrieved for this exact context. The tutor must distinguish general teaching from verified board-specific rules.")
                    answer = provider.answer(
                        st.session_state.ai_teacher_messages[:-1] + [user_message],
                        profile_context=context,
                        image=image,
                        knowledge_context=evidence,
                    )
                    st.markdown(answer)
                    if records:
                        with st.expander("Official sources used"):
                            for record in records:
                                st.markdown(
                                    f"**[{record['source_id']}] {record.get('title', 'Official source')}**  \n"
                                    f"{record.get('system', '')} · {record.get('status', '')} · "
                                    f"Reviewed {record.get('reviewed_on', 'date not recorded')}  \n"
                                    f"[Open official source]({record['source_url']})"
                                )
                    st.session_state.ai_teacher_messages.append({"role": "assistant", "content": answer})
                except (RuntimeError, ValueError, OSError) as exc:
                    st.error(str(exc))
        st.rerun()
    if st.session_state.ai_teacher_messages:
        if st.button("Clear this browser session's chat", key="clear_ai_teacher_chat"):
            st.session_state.ai_teacher_messages = []
            st.rerun()
        st.caption("The latest 12 turns may be sent to the configured model during this session. Chat is not stored permanently or used to train a model.")
