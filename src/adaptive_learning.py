"""Transparent topic-progress tracking and adaptive study planning.

Scores are descriptive learning signals from student-entered practice data,
not grades, diagnoses, predictions, or an objective measure of ability.
"""
from __future__ import annotations

from datetime import date
from typing import Any

MAX_TOPIC_ENTRIES = 300
MAX_TEXT_LENGTH = 120


def normalise_topic_entry(
    subject: str,
    topic: str,
    confidence: int,
    attempted: int,
    correct: int,
    studied_on: str | None = None,
) -> dict[str, Any]:
    subject = str(subject).strip()[:MAX_TEXT_LENGTH]
    topic = str(topic).strip()[:MAX_TEXT_LENGTH]
    if not subject or not topic:
        raise ValueError("Enter both a subject and a topic.")
    if isinstance(confidence, bool) or not 1 <= int(confidence) <= 5:
        raise ValueError("Confidence must be between 1 and 5.")
    if isinstance(attempted, bool) or not 0 <= int(attempted) <= 100:
        raise ValueError("Practice attempts must be between 0 and 100.")
    if isinstance(correct, bool) or not 0 <= int(correct) <= int(attempted):
        raise ValueError("Correct answers must be between zero and the number attempted.")
    day = studied_on or date.today().isoformat()
    try:
        date.fromisoformat(day)
    except (TypeError, ValueError) as exc:
        raise ValueError("Study date must use YYYY-MM-DD format.") from exc
    return {
        "subject": subject,
        "topic": topic,
        "confidence": int(confidence),
        "attempted": int(attempted),
        "correct": int(correct),
        "studied_on": day,
    }


def summarise_topic_progress(entries: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Summarise latest entry per subject/topic without presenting it as a grade."""
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for raw in (entries or [])[-MAX_TOPIC_ENTRIES:]:
        try:
            row = normalise_topic_entry(
                raw.get("subject", ""), raw.get("topic", ""),
                raw.get("confidence", 3), raw.get("attempted", 0),
                raw.get("correct", 0), raw.get("studied_on"),
            )
        except (TypeError, ValueError, AttributeError):
            continue
        key = (row["subject"].casefold(), row["topic"].casefold())
        previous = latest.get(key)
        if previous is None or row["studied_on"] >= previous["studied_on"]:
            latest[key] = row

    summaries = []
    for row in latest.values():
        practice_accuracy = (row["correct"] / row["attempted"] * 100) if row["attempted"] else None
        confidence_percent = row["confidence"] * 20
        if practice_accuracy is None:
            progress_index = confidence_percent
            evidence = "Self-reflection only; add practice attempts for a stronger signal."
        else:
            progress_index = round(0.6 * practice_accuracy + 0.4 * confidence_percent)
            evidence = "A descriptive blend of recent practice accuracy (60%) and self-rated confidence (40%)."
        summaries.append({
            **row,
            "practice_accuracy": round(practice_accuracy, 1) if practice_accuracy is not None else None,
            "progress_index": int(progress_index),
            "evidence": evidence,
            "evidence_level": "practice_and_self_reflection" if row["attempted"] >= 5 else "provisional",
        })
    return sorted(summaries, key=lambda x: (x["progress_index"], x["subject"].casefold(), x["topic"].casefold()))


def build_adaptive_plan(entries: list[dict[str, Any]] | None, limit: int = 5) -> list[dict[str, str]]:
    """Suggest small next actions from the student's own latest topic records."""
    summaries = summarise_topic_progress(entries)
    plan = []
    for row in summaries[:max(1, min(int(limit), 10))]:
        if row["evidence_level"] == "provisional":
            action = "Complete at least five practice questions, then update your reflection."
        elif row["progress_index"] < 50:
            action = "Revisit one prerequisite, study a worked example, and try a short guided practice set."
        elif row["progress_index"] < 75:
            action = "Practise a different question type and explain the method in your own words."
        else:
            action = "Try a mixed or unfamiliar application to check whether the idea transfers."
        plan.append({
            "subject": row["subject"],
            "topic": row["topic"],
            "priority": "Review next" if row["progress_index"] < 50 else "Practise next" if row["progress_index"] < 75 else "Extend",
            "action": action,
            "basis": row["evidence"],
        })
    return plan
