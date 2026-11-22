"""EduBridge's shared visual identity: editorial clarity with a vivid learning-studio accent."""
from __future__ import annotations

import streamlit as st


def apply_visual_identity() -> None:
    """Apply the shared responsive visual system after each page's base styles."""
    st.markdown(
        """
        <style>
        :root {
          --eb-ink: #10182d;
          --eb-muted: #68748b;
          --eb-paper: #f7f8fb;
          --eb-surface: #ffffff;
          --eb-line: #e5e9f1;
          --eb-blue: #4357f5;
          --eb-cyan: #31c5c8;
          --eb-lime: #d7f36a;
          --eb-coral: #ff927b;
        }
        html, body, [class*="css"] { font-family: Inter, "DM Sans", sans-serif; }
        .stApp {
          background:
            radial-gradient(ellipse at 92% 0%, rgba(67,87,245,.085), transparent 27%),
            radial-gradient(ellipse at 0% 72%, rgba(49,197,200,.055), transparent 24%),
            var(--eb-paper) !important;
          color: var(--eb-ink);
        }
        .main .block-container {
          max-width: 1380px !important;
          padding: clamp(1rem, 3vw, 2.6rem) clamp(.85rem, 3.5vw, 3.2rem) 3.5rem !important;
        }
        h1, h2, h3, h4 {
          color: var(--eb-ink) !important;
          letter-spacing: -.045em !important;
          font-family: "Space Grotesk", Inter, sans-serif !important;
        }
        h1 { font-size: clamp(2rem, 4.2vw, 3.25rem) !important; line-height: 1.04 !important; }
        h2 { font-size: clamp(1.45rem, 2.6vw, 2rem) !important; }
        p, li { line-height: 1.68; }
        header[data-testid="stHeader"] { background: rgba(247,248,251,.82) !important; }
        /* Remove Streamlit's generated multipage list; EduBridge owns one consistent navigation. */
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display: none !important; }
        section[data-testid="stSidebar"] {
          background: #111a32 !important;
          border-right: 1px solid rgba(255,255,255,.08) !important;
        }
        section[data-testid="stSidebar"] > div {
          height: 100vh;
          overflow-y: auto !important;
          scrollbar-width: thin;
          scrollbar-color: rgba(255,255,255,.25) transparent;
        }
        section[data-testid="stSidebar"] * { color: #f5f7ff; }
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #aeb9d2 !important; }
        section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.13) !important; }
        section[data-testid="stSidebar"] [data-testid="stButton"] button,
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
          min-height: 43px;
          border: 1px solid transparent !important;
          border-radius: 12px !important;
          background: transparent !important;
          color: #dbe3f6 !important;
          font-weight: 620 !important;
          text-align: left !important;
          transition: background .16s ease, border-color .16s ease, transform .16s ease;
        }
        section[data-testid="stSidebar"] [data-testid="stButton"] button:hover,
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
          background: rgba(255,255,255,.09) !important;
          border-color: rgba(255,255,255,.1) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
          background: linear-gradient(105deg, #4a5cf4, #267f9d) !important;
          border-color: rgba(255,255,255,.14) !important;
          color: white !important;
          box-shadow: 0 8px 22px rgba(45,75,210,.22);
        }
        .eb-sidebar-brand { padding: 10px 0 13px; }
        .eb-sidebar-mark {
          border-radius: 14px !important;
          background: linear-gradient(140deg, #5265ff, #27b9c4) !important;
          box-shadow: 0 8px 22px rgba(49,115,220,.28);
        }
        .eb-sidebar-section {
          color: var(--eb-lime) !important;
          font-size: 10px !important;
          font-weight: 850 !important;
          letter-spacing: 1.6px !important;
        }
        .top-brand-strip {
          border: 1px solid var(--eb-line) !important;
          border-radius: 14px !important;
          background: rgba(255,255,255,.82) !important;
          box-shadow: 0 5px 18px rgba(18,31,61,.035) !important;
          color: var(--eb-ink) !important;
          padding: 7px 12px !important;
        }
        .hero {
          border-radius: 26px !important;
          background: linear-gradient(112deg, #111a32 0%, #25356c 57%, #4357f5 100%) !important;
          box-shadow: 0 24px 58px rgba(26,43,97,.16) !important;
          border: 1px solid rgba(255,255,255,.12);
        }
        .hero .eyebrow { color: var(--eb-lime) !important; }
        .hero h1 { color: #fff !important; }
        .hero p { color: #e2e9ff !important; }
        .dash-card, .welcome-loop-card, .pathway-tile, .week-day,
        div[data-testid="stMetric"], div[data-testid="stForm"] {
          background: var(--eb-surface) !important;
          border: 1px solid var(--eb-line) !important;
          border-radius: 18px !important;
          box-shadow: 0 8px 26px rgba(19,32,62,.045) !important;
        }
        .dash-card:hover, .pathway-tile:hover, .week-day:hover {
          border-color: #c9d1ff !important;
          box-shadow: 0 15px 34px rgba(39,58,120,.09) !important;
        }
        .dash-card:before { background: linear-gradient(180deg,var(--eb-blue),var(--eb-cyan),var(--eb-lime)) !important; }
        .dash-card .card-icon, .welcome-loop-card span {
          background: #eef1ff !important;
          color: var(--eb-blue) !important;
        }
        .dash-kicker { color: var(--eb-blue) !important; }
        .dash-heading { color: var(--eb-ink) !important; }
        .dash-subheading { color: var(--eb-muted) !important; }
        div[data-testid="stMetric"] { min-height: 108px; padding: 17px !important; }
        div[data-testid="stMetricLabel"] p { color: var(--eb-muted) !important; }
        div[data-testid="stMetricValue"] { color: var(--eb-ink) !important; font-variant-numeric: tabular-nums; }
        .stButton button, .stDownloadButton button, .stLinkButton a,
        .stFormSubmitButton button {
          min-height: 44px;
          border-radius: 12px !important;
          font-weight: 700 !important;
          transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
        }
        .stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] {
          background: linear-gradient(105deg,#4357f5,#287f9e) !important;
          border: 0 !important;
          color: #fff !important;
          box-shadow: 0 8px 20px rgba(67,87,245,.2);
        }
        .stButton button:hover, .stDownloadButton button:hover, .stLinkButton a:hover {
          transform: translateY(-1px);
          box-shadow: 0 10px 24px rgba(19,32,62,.1);
        }
        div[data-testid="stAlert"] { border-radius: 14px !important; }
        div[data-testid="stChatMessage"] {
          border: 1px solid var(--eb-line) !important;
          border-radius: 18px !important;
          background: #fff !important;
          box-shadow: 0 6px 20px rgba(19,32,62,.035);
        }
        div[data-testid="stChatInput"] {
          border: 1px solid #cfd6eb !important;
          border-radius: 18px !important;
          box-shadow: 0 8px 26px rgba(19,32,62,.06) !important;
        }
        input:focus-visible, textarea:focus-visible, button:focus-visible, a:focus-visible {
          outline: 3px solid rgba(49,197,200,.7) !important;
          outline-offset: 2px !important;
        }
        @media (max-width: 800px) {
          .main .block-container { padding: .9rem .8rem 2rem !important; }
          .hero { padding: 23px 21px !important; border-radius: 20px !important; }
          .hero h1 { font-size: clamp(1.8rem, 7vw, 2.35rem) !important; }
          .dash-card, .welcome-loop-card { padding: 16px !important; }
          section[data-testid="stSidebar"] > div { padding-top: .5rem; }
        }
        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after { transition-duration: .01ms !important; animation-duration: .01ms !important; }
        }
        
        /* Phase 24: a calmer, more tactile learning-studio surface. */
        .stApp {
          background:
            radial-gradient(ellipse at 82% 2%, rgba(99,102,241,.12), transparent 30%),
            radial-gradient(ellipse at 8% 42%, rgba(45,212,191,.08), transparent 26%),
            linear-gradient(180deg,#f8f9ff 0%,#f4f6fb 52%,#f8fafc 100%) !important;
        }
        .main .block-container { max-width: 1460px !important; }
        .stApp [data-testid="stVerticalBlockBorderWrapper"] {
          border-radius: 18px !important;
          border-color: #e5e9f3 !important;
        }
        .stApp [data-testid="stExpander"] {
          border: 1px solid #e4e8f2 !important;
          border-radius: 15px !important;
          background: rgba(255,255,255,.82) !important;
          overflow: hidden;
        }
        .stApp [data-testid="stExpander"] summary {
          font-weight: 700 !important;
          min-height: 44px;
        }
        .stApp [data-testid="stTextInput"] input,
        .stApp [data-testid="stTextArea"] textarea,
        .stApp [data-testid="stNumberInput"] input {
          border-radius: 12px !important;
          background: #fff !important;
        }
        .stApp [data-testid="stSelectbox"] [role="combobox"] {
          border-radius: 12px !important;
        }
        .stApp [data-testid="stChatInput"] textarea {
          min-height: 54px !important;
        }
        .stApp [data-testid="stChatMessage"] {
          border-radius: 18px !important;
          border: 1px solid #e5e9f3 !important;
          box-shadow: 0 8px 24px rgba(17,26,50,.045) !important;
        }
        .stApp .eb-nav-hero, .stApp .eb-ai-hero {
          position: relative;
          isolation: isolate;
          overflow: hidden;
          box-shadow: 0 24px 60px rgba(32,44,104,.17) !important;
        }
        .stApp .eb-nav-hero:after {
          content: "";
          position: absolute;
          z-index: -1;
          width: 250px; height: 250px;
          right: -65px; top: -155px;
          border: 1px solid rgba(255,255,255,.24);
          border-radius: 50%;
          box-shadow: 0 0 0 28px rgba(255,255,255,.045),0 0 0 58px rgba(255,255,255,.025);
        }
        .stApp .eb-nav-step {
          transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
          box-shadow: 0 8px 24px rgba(17,26,50,.045);
        }
        .stApp .eb-nav-step:hover {
          transform: translateY(-2px);
          border-color: #cbd3ff !important;
          box-shadow: 0 14px 32px rgba(48,61,125,.09);
        }
        @media (max-width: 700px) {
          .stApp .eb-nav-hero { padding: 21px 19px !important; border-radius: 19px !important; }
          .stApp .eb-nav-step { padding: 15px !important; }
          .stApp [data-testid="stHorizontalBlock"] { gap: .65rem !important; }
        }
        @media (prefers-reduced-motion: reduce) {
          .stApp .eb-nav-step { transition: none !important; }
        }

        /* AI Teacher receives the same signature system without changing provider behaviour. */
        .stApp .eb-ai-hero {
          border-radius: 24px !important;
          background: linear-gradient(112deg,#111a32 0%,#25356c 58%,#4357f5 100%) !important;
          box-shadow: 0 22px 54px rgba(26,43,97,.16) !important;
        }
        .stApp .eb-ai-hero h1 { color: #fff !important; }
        .stApp .eb-ai-pill {
          border-color: rgba(255,255,255,.22) !important;
          background: rgba(255,255,255,.12) !important;
          border-radius: 10px !important;
        }
        .stApp .eb-ai-note {
          background: #eef4ff !important;
          border: 1px solid #dbe5fb !important;
          border-radius: 15px !important;
          color: #34435f !important;
        }
        .stApp .eb-ai-prompt {
          border: 1px solid var(--eb-line) !important;
          border-radius: 16px !important;
          background: #fff !important;
          box-shadow: 0 8px 24px rgba(19,32,62,.045) !important;
        }
</style>
        """,
        unsafe_allow_html=True,
    )
