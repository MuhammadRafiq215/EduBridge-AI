"""Streamlit interface for the modular EduBridge AI Teacher."""
from __future__ import annotations

import streamlit as st

from src.ai_teacher import OpenAICompatibleProvider, build_profile_context


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


def render_ai_teacher(profile: dict | None) -> None:
    st.markdown("## 🤖 Your AI Teacher")
    st.write("Ask for explanations, revision support or help understanding a question. You can also attach a screenshot or image for a vision-capable model to interpret.")
    provider = _configured_provider()
    if provider is None:
        st.info("The chat workspace is ready, but an AI provider has not been configured yet. The app will not pretend to generate AI answers. A project owner can add an eligible provider's credentials in Streamlit Secrets using the setup guide.")
        with st.expander("What will be supported?"):
            st.markdown("- Profile-aware explanations for your qualification, subjects and study level.\n- PNG, JPEG and WebP question screenshots (up to 5 MB).\n- Conversation history for the current browser session.\n- A provider adapter that can be replaced without rewriting the interface.")
        return

    use_profile = False
    if isinstance(profile, dict) and profile:
        use_profile = st.checkbox("Personalise explanations using my saved learning profile", value=True)
        if use_profile:
            st.caption("Only selected education fields are sent as context with your question.")
    profile_context = build_profile_context(profile) if use_profile else None

    if "ai_teacher_messages" not in st.session_state:
        st.session_state.ai_teacher_messages = []
    for message in st.session_state.ai_teacher_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    uploaded = st.file_uploader("Attach a question screenshot or image (optional)",
        type=["png", "jpg", "jpeg", "webp"], key="ai_teacher_image",
        help="Maximum 5 MB. The image is sent to the configured AI provider when you submit a question.")
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
            with st.spinner("Preparing your explanation..."):
                try:
                    answer = provider.answer(st.session_state.ai_teacher_messages[:-1] + [user_message],
                                             profile_context=profile_context, image=image)
                    st.markdown(answer)
                    st.session_state.ai_teacher_messages.append({"role": "assistant", "content": answer})
                except (RuntimeError, ValueError) as exc:
                    st.error(str(exc))
        st.rerun()

    if st.session_state.ai_teacher_messages:
        if st.button("Clear this session's conversation", key="clear_ai_teacher_chat"):
            st.session_state.ai_teacher_messages = []
            st.rerun()
        st.caption("Conversation history is kept in this browser session only; it is not saved to the student profile.")
