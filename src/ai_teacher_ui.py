"""Streamlit interface for the modular EduBridge AI Teacher."""
from __future__ import annotations

import streamlit as st

from src.ai_teacher import OpenAICompatibleProvider, build_profile_context
from src.knowledge_base import load_knowledge_records
from src.specification_engine import (
    SpecificationQuery,
    build_specification_context,
    retrieve_specifications,
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


def _show_knowledge_status() -> None:
    try:
        count = len(load_knowledge_records())
    except ValueError:
        st.error("The local knowledge base contains an invalid record. Retrieval has been paused until it is corrected.")
        return
    st.caption(f"Verified official-source records available: {count}")
    st.caption("A source count is not a measure of complete qualification or subject coverage.")


def render_student_navigator(profile: dict | None) -> None:
    st.markdown("## 🧭 Student Navigator")
    st.write("A transparent next-step guide built from your saved learning profile and this browser session.")
    history = st.session_state.get("ai_teacher_messages", [])
    snapshot = build_student_snapshot(profile, history)
    left, right = st.columns(2)
    left.metric("Subjects in your profile", len(snapshot["subjects"]))
    right.metric("Questions in this session", snapshot["recent_question_count"])
    st.caption(f"Learning context: {snapshot['memory_scope']}")
    if snapshot["qualification"] != "Not specified":
        st.write(
            f"**Qualification:** {snapshot['qualification']}  ·  "
            f"**Country:** {snapshot['country']}  ·  "
            f"**Awarding body:** {snapshot['awarding_body']}"
        )
    if snapshot["subjects"]:
        focus = st.selectbox("What would you like to focus on next?", ["Let EduBridge suggest"] + snapshot["subjects"])
        focus_subject = None if focus == "Let EduBridge suggest" else focus
    else:
        focus_subject = None
        st.info("Add a qualification and subjects in My learning profile to get more relevant navigation.")
    weekly_minutes = st.slider("Study time to plan (minutes this week)", 15, 600, 120, step=15)
    plan = build_navigation_plan(snapshot, focus_subject=focus_subject, weekly_minutes=weekly_minutes)
    st.markdown("### Your suggested next steps")
    for index, item in enumerate(plan, start=1):
        with st.container(border=True):
            st.markdown(f"**{index}. {item['title']}**")
            st.caption(item["reason"])
            st.write(item["action"])
    if snapshot["recent_questions"]:
        with st.expander("Recent learning questions from this session"):
            for question in snapshot["recent_questions"]:
                st.markdown(f"- {question}")
    st.caption(
        "These are planning suggestions, not grade predictions or formal academic assessments. "
        "Session questions are temporary and are not saved as a permanent chat archive."
    )


def render_ai_teacher(profile: dict | None) -> None:
    st.markdown("## 🤖 Your AI Teacher")
    st.write("Ask for explanations, revision support or help understanding a question. You can also attach a screenshot or image for a vision-capable model to interpret.")
    _show_knowledge_status()
    provider = _configured_provider()
    if provider is None:
        st.info("The chat workspace is ready, but an AI provider has not been configured yet. The app will not pretend to generate AI answers. A project owner can add an eligible provider's credentials in Streamlit Secrets using the setup guide.")
        with st.expander("What will be supported?"):
            st.markdown(
                "- Profile-aware explanations for your qualification, subjects and study level.\n"
                "- Optional custom qualification, country, awarding-body, subject and exam-year details.\n"
                "- Retrieval from reviewed official sources, with source references.\n"
                "- PNG, JPEG and WebP question screenshots (up to 5 MB).\n"
                "- Current-session conversation context and Student Navigator suggestions."
            )
        return

    use_profile = False
    if isinstance(profile, dict) and profile:
        use_profile = st.checkbox("Personalise explanations using my saved learning profile", value=True)
        if use_profile:
            st.caption("Only selected education fields are sent as context with your question.")
    profile_context = build_profile_context(profile) if use_profile else {}
    profile_context = profile_context or {}

    with st.expander("Examination and specification context (optional)", expanded=not bool(profile_context.get("qualification"))):
        qualification = st.text_input(
            "Qualification / examination",
            value=str(profile_context.get("qualification") or profile_context.get("custom_qualification") or ""),
            placeholder="e.g. Cambridge International A Levels, WAEC, Turkish MEB",
        )
        country = st.text_input("Country or education system", value=str(profile_context.get("country", "")), placeholder="e.g. Pakistan, Nigeria, Türkiye")
        board = st.text_input("Awarding body / examination board", value=str(profile_context.get("board", "")), placeholder="e.g. Pearson Edexcel, FBISE, WAEC, MEB")
        subject_options = profile_context.get("subjects", [])
        subject_default = subject_options[0] if isinstance(subject_options, list) and subject_options else ""
        subject = st.text_input("Subject (optional)", value=subject_default, placeholder="e.g. Mathematics, Biology, Computer Science")
        exam_year = st.text_input("Examination year (optional)", placeholder="e.g. 2027")
        exam_series = st.text_input("Examination series / session (optional)", placeholder="e.g. May/June, October/November")
    profile_context.update({
        "qualification": qualification.strip(),
        "country": country.strip(),
        "board": board.strip(),
        "subject": subject.strip(),
        "exam_year": exam_year.strip(),
        "exam_series": exam_series.strip(),
    })
    profile_context = {key: value for key, value in profile_context.items() if value not in ("", None, [], {})}

    if "ai_teacher_messages" not in st.session_state:
        st.session_state.ai_teacher_messages = []
    for message in st.session_state.ai_teacher_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    uploaded = st.file_uploader(
        "Attach a question screenshot or image (optional)",
        type=["png", "jpg", "jpeg", "webp"],
        key="ai_teacher_image",
        help="Maximum 5 MB. The image is sent to the configured AI provider when you submit a question.",
    )
    question = st.chat_input("Ask your AI teacher a question...")
    if question:
        image = (uploaded.getvalue(), uploaded.type or "image/jpeg") if uploaded is not None else None
        user_message = {"role": "user", "content": question}
        st.session_state.ai_teacher_messages.append(user_message)
        with st.chat_message("user"):
            st.markdown(question)
            if uploaded is not None:
                st.image(uploaded, caption="Attached image", use_container_width=True)
        with st.chat_message("assistant"):
            with st.spinner("Checking official specifications and preparing your explanation..."):
                try:
                    spec_query = SpecificationQuery(
                        question=question,
                        qualification=profile_context.get("qualification"),
                        country=profile_context.get("country"),
                        awarding_body=profile_context.get("board"),
                        subject=profile_context.get("subject"),
                        exam_year=profile_context.get("exam_year"),
                        exam_series=profile_context.get("exam_series"),
                    )
                    sources = retrieve_specifications(spec_query)
                    specification_context = build_specification_context(sources, spec_query)
                    if not sources:
                        st.info("No matching verified official specification was found for this exact context. General explanation may still be possible, but board-specific rules will not be treated as verified.")
                    answer = provider.answer(
                        st.session_state.ai_teacher_messages[:-1] + [user_message],
                        profile_context=profile_context,
                        image=image,
                        knowledge_context=specification_context,
                    )
                    st.markdown(answer)
                    if sources:
                        with st.expander(f"Official specification and guidance sources ({len(sources)})"):
                            for source in sources:
                                st.markdown(
                                    f"**[{source['source_id']}] {source['title']}**  \n"
                                    f"{source['issuer']} · {source.get('document_type', 'official guidance')} · Reviewed {source['reviewed_at']}  \n"
                                    f"[Open official source]({source['source_url']})"
                                )
                    st.session_state.ai_teacher_messages.append({"role": "assistant", "content": answer})
                except (RuntimeError, ValueError) as exc:
                    st.error(str(exc))
        st.rerun()

    if st.session_state.ai_teacher_messages:
        if st.button("Clear this session's conversation", key="clear_ai_teacher_chat"):
            st.session_state.ai_teacher_messages = []
            st.rerun()
        st.caption("The current conversation is available to the tutor during this browser session only. It is not saved to the student profile or used to train a model.")
