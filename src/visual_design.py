"""Shared visual identity and responsive polish for EduBridge AI."""
from __future__ import annotations

import streamlit as st


def apply_visual_identity() -> None:
    """Apply the Phase 11 design system without changing workspace behaviour."""
    st.markdown(
        """
        <style>
        :root {
          --eb-ink: #17233d;
          --eb-muted: #68758f;
          --eb-paper: #f5f7fc;
          --eb-line: #e4e9f3;
          --eb-violet: #5b4de8;
          --eb-teal: #12a6a6;
          --eb-coral: #f29a78;
          --eb-lime: #d4f06a;
        }
        .stApp {
          background:
            radial-gradient(ellipse at 7% 0%, rgba(18,166,166,.075), transparent 28%),
            radial-gradient(ellipse at 94% 5%, rgba(91,77,232,.09), transparent 26%),
            var(--eb-paper);
          color: var(--eb-ink);
        }
        .main .block-container {
          max-width: 1380px;
          padding-top: 1.65rem;
          padding-bottom: 4rem;
        }
        section[data-testid="stSidebar"] {
          background:
            radial-gradient(circle at 12% 5%, rgba(18,166,166,.22), transparent 30%),
            linear-gradient(165deg, #111b31 0%, #202b52 58%, #27366a 100%);
          border-right: 1px solid rgba(255,255,255,.08);
        }
        section[data-testid="stSidebar"] [data-testid="stRadio"] label {
          margin: 2px 0;
          border: 1px solid transparent;
          border-radius: 13px;
          padding: 10px 12px;
          transition: background .18s ease, border-color .18s ease, transform .18s ease;
        }
        section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
          background: rgba(255,255,255,.09);
          border-color: rgba(255,255,255,.09);
          transform: translateX(2px);
        }
        section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
          background: linear-gradient(100deg, rgba(91,77,232,.36), rgba(18,166,166,.18));
          border-color: rgba(255,255,255,.13);
        }
        .top-brand-strip {
          width: fit-content;
          max-width: 100%;
          gap: 11px;
          padding: 9px 15px 9px 10px;
          border: 1px solid rgba(218,224,240,.95);
          border-radius: 999px;
          background: rgba(255,255,255,.88);
          box-shadow: 0 8px 24px rgba(31,44,81,.07);
          backdrop-filter: blur(12px);
        }
        .top-brand-strip .brand-mark {
          width: 31px;
          height: 31px;
          border-radius: 11px;
          background: linear-gradient(135deg, var(--eb-violet), var(--eb-teal));
          box-shadow: 0 5px 12px rgba(91,77,232,.2);
        }
        .hero {
          background:
            radial-gradient(circle at 86% 22%, rgba(18,166,166,.32), transparent 26%),
            linear-gradient(118deg, #14213b 0%, #343b83 56%, #5144c9 78%, #168d98 120%);
          border: 1px solid rgba(255,255,255,.11);
          box-shadow: 0 22px 54px rgba(31,42,91,.17);
        }
        .hero .eyebrow {
          color: var(--eb-lime);
          background: rgba(212,240,106,.12);
          border-color: rgba(212,240,106,.24);
        }
        .dash-heading { color: var(--eb-ink); }
        .dash-kicker { color: var(--eb-violet); }
        .dash-card, .welcome-card, .pathway-tile, .week-day {
          border-color: var(--eb-line);
          box-shadow: 0 10px 28px rgba(31,44,81,.055);
        }
        .dash-card:hover, .welcome-card:hover, .pathway-tile:hover, .week-day:hover {
          border-color: rgba(91,77,232,.34);
          box-shadow: 0 17px 36px rgba(31,44,81,.105);
        }
        div[data-testid="stMetric"] {
          border-color: var(--eb-line);
          background: linear-gradient(145deg, #fff 0%, #f8faff 100%);
          box-shadow: 0 9px 24px rgba(31,44,81,.055);
        }
        div[data-testid="stMetricValue"] {
          color: #26325b;
        }
        .stButton button, .stDownloadButton button, .stLinkButton a,
        div[data-testid="stFormSubmitButton"] button {
          border-radius: 13px;
          font-weight: 700;
          min-height: 44px;
          transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
        }
        .stButton button[kind="primary"],
        div[data-testid="stFormSubmitButton"] button[kind="primary"] {
          background: linear-gradient(105deg, var(--eb-violet), #7866f4 58%, var(--eb-teal));
          border: 0;
          color: #fff;
          box-shadow: 0 8px 19px rgba(91,77,232,.2);
        }
        .stButton button:hover, .stDownloadButton button:hover, .stLinkButton a:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 22px rgba(31,44,81,.12);
        }
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
          border-radius: 12px !important;
          border-color: #dce2ef !important;
        }
        div[data-testid="stForm"] {
          border-color: var(--eb-line);
          border-radius: 20px;
          box-shadow: 0 9px 25px rgba(31,44,81,.045);
        }
        div[data-testid="stExpander"] {
          border-color: var(--eb-line);
          border-radius: 15px;
          background: rgba(255,255,255,.76);
        }
        div[data-testid="stChatMessage"] {
          border-color: var(--eb-line);
          border-radius: 18px;
          box-shadow: 0 6px 20px rgba(31,44,81,.045);
        }
        .eb-site-footer {
          margin-top: 42px;
          padding: 24px 26px;
          border: 1px solid rgba(219,225,240,.95);
          border-radius: 22px;
          background:
            radial-gradient(circle at 92% 10%, rgba(18,166,166,.11), transparent 28%),
            linear-gradient(120deg, #fff 0%, #f7f8ff 62%, #f0fbfb 100%);
          box-shadow: 0 12px 30px rgba(31,44,81,.055);
        }
        .eb-footer-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 18px;
          flex-wrap: wrap;
        }
        .eb-footer-brand {
          color: #202c50;
          font: 700 17px 'Space Grotesk', sans-serif;
          letter-spacing: -.4px;
        }
        .eb-footer-tagline {
          color: #68758f;
          font-size: 12px;
          margin-top: 5px;
        }
        .eb-footer-links {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 9px;
        }
        .eb-footer-links a {
          display: inline-flex;
          padding: 8px 11px;
          border: 1px solid #e2e6f1;
          border-radius: 999px;
          background: rgba(255,255,255,.86);
          color: #4e4baf;
          text-decoration: none;
          font-size: 11px;
          font-weight: 700;
        }
        .eb-footer-bottom {
          display: flex;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 18px;
          padding-top: 14px;
          border-top: 1px solid #e8ebf4;
          color: #7b849b;
          font-size: 10px;
          line-height: 1.5;
        }
        @media (max-width: 800px) {
          .main .block-container { padding: 1rem 1rem 2.5rem; }
          .hero { padding: 25px 22px; }
          .eb-site-footer { padding: 19px; border-radius: 18px; }
        }
        @media (prefers-reduced-motion: reduce) {
          .stButton button, .stDownloadButton button, .stLinkButton a,
          section[data-testid="stSidebar"] [data-testid="stRadio"] label {
            transition: none !important;
          }
          .stButton button:hover, .stDownloadButton button:hover,
          .stLinkButton a:hover,
          section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            transform: none !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_site_footer() -> None:
    """Render a compact, accessible project footer."""
    st.markdown(
        """
        <footer class="eb-site-footer">
          <div class="eb-footer-top">
            <div>
              <div class="eb-footer-brand">✦ EduBridge AI</div>
              <div class="eb-footer-tagline">Learn with clarity. Explore with confidence. Grow at your pace.</div>
            </div>
            <nav class="eb-footer-links" aria-label="Project links">
              <a href="https://github.com/MuhammadRafiq215/EduBridge-AI" target="_blank" rel="noopener noreferrer">GitHub repository ↗</a>
            </nav>
          </div>
          <div class="eb-footer-bottom">
            <span>© EduBridge AI · Student-centred learning and educational data science</span>
            <span>Research prototype · Verify important decisions with official sources</span>
          </div>
        </footer>
        """,
        unsafe_allow_html=True,
    )
