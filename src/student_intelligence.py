"""Student-facing learning analytics from explicitly recorded topic reflections.

These descriptive indicators are planning aids, not grades, diagnoses or predictions.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def build_student_intelligence(progress: list[dict[str, Any]] | None, today: date | None = None) -> dict[str, Any]:
    today = today or date.today()
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    valid_days: set[date] = set()
    for raw in (progress or [])[-300:]:
        if not isinstance(raw, dict):
            continue
        subject = str(raw.get("subject", "")).strip()[:120]
        topic = str(raw.get("topic", "")).strip()[:120]
        try:
            confidence = int(raw.get("confidence", 3))
            attempted = int(raw.get("attempted", 0))
            correct = int(raw.get("correct", 0))
            studied = date.fromisoformat(str(raw.get("studied_on", "")))
        except (TypeError, ValueError):
            continue
        if not subject or not topic or not 1 <= confidence <= 5 or not 0 <= correct <= attempted <= 100:
            continue
        row = {"subject": subject, "topic": topic, "confidence": confidence,
               "attempted": attempted, "correct": correct, "studied_on": studied.isoformat()}
        key = (subject.casefold(), topic.casefold())
        if key not in latest or studied >= date.fromisoformat(latest[key]["studied_on"]):
            latest[key] = row
        valid_days.add(studied)

    topics = []
    for row in latest.values():
        accuracy = round(row["correct"] / row["attempted"] * 100, 1) if row["attempted"] else None
        signal = round(0.6 * accuracy + 0.4 * row["confidence"] * 20) if accuracy is not None else row["confidence"] * 20
        evidence = "Practice + reflection" if row["attempted"] >= 5 else "Provisional reflection"
        topics.append({**row, "accuracy": accuracy, "signal": signal, "evidence": evidence})
    topics.sort(key=lambda item: (item["signal"], item["subject"].casefold(), item["topic"].casefold()))

    streak = 0
    cursor = today
    if cursor not in valid_days:
        cursor -= timedelta(days=1)
    while cursor in valid_days:
        streak += 1
        cursor -= timedelta(days=1)

    week_start = today - timedelta(days=6)
    week_days = sorted(day.isoformat() for day in valid_days if week_start <= day <= today)
    return {
        "topics": topics,
        "topic_count": len(topics),
        "practice_attempts": sum(row["attempted"] for row in latest.values()),
        "average_confidence": round(sum(row["confidence"] for row in latest.values()) / len(latest), 1) if latest else None,
        "learning_streak": streak,
        "active_days_last_7": len(week_days),
        "recent_days": week_days,
        "review_first": topics[:5],
        "stronger_topics": [row for row in topics if row["signal"] >= 75],
        "note": "Signals combine self-reported confidence with recorded practice only where attempts are available. They are not exam marks or predictions.",
    }
