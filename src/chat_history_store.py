"""Opt-in, per-user persistence for EduBridge AI chat history.

The database table must be created with the accompanying RLS migration.
No service-role key is required; use the authenticated user's session.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

MAX_STORED_MESSAGES = 100
MAX_MESSAGE_CHARS = 10000


def sanitise_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    clean = []
    for item in (messages or [])[-MAX_STORED_MESSAGES:]:
        if not isinstance(item, dict):
            continue
        role, content = item.get("role"), item.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            continue
        content = content.strip()
        if content:
            clean.append({"role": role, "content": content[:MAX_MESSAGE_CHARS]})
    return clean


def load_chat_history(client, user_id: str) -> list[dict[str, str]]:
    response = (
        client.table("student_chat_history")
        .select("messages")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    data = response.data
    return sanitise_messages(data.get("messages", [])) if data else []


def save_chat_history(client, user_id: str, messages: list[dict[str, Any]]) -> None:
    clean = sanitise_messages(messages)
    client.table("student_chat_history").upsert(
        {"user_id": user_id, "messages": clean, "updated_at": datetime.now(timezone.utc).isoformat()},
        on_conflict="user_id",
    ).execute()


def delete_chat_history(client, user_id: str) -> None:
    client.table("student_chat_history").delete().eq("user_id", user_id).execute()
