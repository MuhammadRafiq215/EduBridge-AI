"""Supabase-backed authentication and private learner-profile persistence.

A fresh client is created per Streamlit rerun so authenticated sessions are
never shared between users through a global cache.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st


def get_supabase_client():
    """Return a per-session Supabase client, or None when secrets are absent."""
    try:
        config = st.secrets.get("supabase", {})
        url = config.get("url", "")
        anon_key = config.get("anon_key", "")
    except Exception:
        return None

    if not url or not anon_key:
        return None

    from supabase import create_client

    return create_client(url, anon_key)


def save_auth_session(session: Any) -> None:
    """Keep short-lived auth tokens in this user's Streamlit session only."""
    st.session_state["sb_access_token"] = session.access_token
    st.session_state["sb_refresh_token"] = session.refresh_token
    st.session_state["sb_user_id"] = session.user.id
    st.session_state["sb_user_email"] = session.user.email


def restore_auth_session(client):
    """Restore/refresh the current user's Supabase session for this rerun."""
    access = st.session_state.get("sb_access_token")
    refresh = st.session_state.get("sb_refresh_token")
    if not access or not refresh:
        return None

    try:
        client.auth.set_session(access, refresh)
        current = client.auth.get_session()
        if current and current.user:
            save_auth_session(current)
            return current.user
    except Exception:
        clear_auth_session()
    return None


def clear_auth_session() -> None:
    for key in ("sb_access_token", "sb_refresh_token", "sb_user_id", "sb_user_email"):
        st.session_state.pop(key, None)
    st.session_state.pop("learner_profile", None)


def load_learner_profile(client, user_id: str) -> dict | None:
    """Read only the profile belonging to the authenticated user (RLS enforced)."""
    response = (
        client.table("student_profiles")
        .select("profile")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    data = response.data
    return data.get("profile") if data else None


def save_learner_profile(client, user_id: str, profile: dict) -> None:
    """Upsert a learner's own profile; database RLS must be enabled."""
    client.table("student_profiles").upsert(
        {
            "id": user_id,
            "profile": profile,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        on_conflict="id",
    ).execute()


def delete_learner_profile(client, user_id: str) -> None:
    """Delete the current learner's profile row."""
    client.table("student_profiles").delete().eq("id", user_id).execute()
