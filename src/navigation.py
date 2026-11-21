"""Shared navigation for every EduBridge legacy Streamlit page."""
from __future__ import annotations

import streamlit as st

from src.visual_design import apply_visual_identity


WORKSPACES = [
    ("Welcome", "✨", "Start here"),
    ("Dashboard", "🏠", "Your learning overview"),
    ("AI Teacher", "🤖", "Ask and understand"),
    ("Student Navigator", "🧭", "Plan your next steps"),
    ("My learning profile", "👤", "Your subjects and goals"),
    ("Career pathways", "🧩", "Explore future options"),
    ("Study planner", "📅", "Organise your week"),
    ("Research insights", "📊", "Explore data science"),
    ("Student feedback", "💬", "Help improve EduBridge"),
    ("Account & privacy", "🔒", "Manage your account"),
    ("About EduBridge", "ℹ️", "How the platform works"),
]


def _open_workspace(name: str) -> None:
    st.session_state["navigate_to_workspace"] = name
    st.switch_page("app.py")


def render_page_sidebar(active_page: str) -> None:
    """Render the same branded navigation on all three standalone tool pages."""
    apply_visual_identity()
    with st.sidebar:
        st.markdown(
            """
            <div class="eb-sidebar-brand">
              <div class="eb-sidebar-mark">✦</div>
              <div><strong>EduBridge AI</strong><span>LEARN · EXPLORE · GROW</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("YOUR LEARNING COMPANION")
        st.markdown('<div class="eb-sidebar-section">STUDENT WORKSPACES</div>', unsafe_allow_html=True)
        for name, icon, hint in WORKSPACES:
            if st.button(
                f"{icon}  {name}",
                key=f"shared_nav_{active_page}_{name}",
                type="primary" if active_page == name else "secondary",
                use_container_width=True,
                help=hint,
            ):
                _open_workspace(name)

        st.divider()
        st.markdown('<div class="eb-sidebar-section">EXPLORE TOOLS</div>', unsafe_allow_html=True)
        st.page_link("pages/1_Global_Knowledge_Hub.py", label="Global Knowledge Hub", icon="🌍")
        st.page_link("pages/2_Academic_Profile_Analyzer.py", label="Academic Profile Analyzer", icon="📊")
        st.page_link("pages/3_Subject_Catalogue.py", label="Subject Catalogue", icon="📚")
        st.divider()
        st.caption("A student-centred learning and research prototype.")
