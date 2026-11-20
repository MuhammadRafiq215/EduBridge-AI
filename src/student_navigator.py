"""Transparent student navigation built from learner-approved profile inputs."""
from __future__ import annotations

from typing import Any


def build_student_snapshot(profile: dict[str, Any] | None, chat_history: list[dict[str, str]] | None = None) -> dict[str, Any]:
    """Create a minimal in-session learning snapshot; never infer grades or identity."""
    profile = profile if isinstance(profile, dict) else {}
    subjects = profile.get("subjects", [])
    confidence = profile.get("confidence", {})
    results = profile.get("latest_results", {})
    weak_subjects = [
        subject for subject in subjects
        if isinstance(confidence, dict) and isinstance(confidence.get(subject), (int, float))
        and confidence[subject] <= 2
    ]
    recent_questions = [
        item.get("content", "").strip()
        for item in (chat_history or [])[-12:]
        if item.get("role") == "user" and isinstance(item.get("content"), str) and item.get("content").strip()
    ]
    return {
        "qualification": profile.get("qualification") or profile.get("custom_qualification") or "Not specified",
        "country": profile.get("country") or "Not specified",
        "awarding_body": profile.get("board") or "Not specified",
        "level": profile.get("level") or "Not specified",
        "subjects": [s for s in subjects if isinstance(s, str)],
        "weak_subjects_by_self_rating": weak_subjects,
        "self_reported_results": {k: v for k, v in results.items() if isinstance(v, str) and v.strip()} if isinstance(results, dict) else {},
        "recent_question_count": len(recent_questions),
        "recent_questions": recent_questions[-4:],
        "memory_scope": "Current browser session and learner-approved profile only.",
    }


def build_navigation_plan(
    snapshot: dict[str, Any],
    focus_subject: str | None = None,
    weekly_minutes: int = 120,
) -> list[dict[str, str]]:
    """Generate transparent next steps from explicit inputs, not predicted outcomes."""
    subjects = snapshot.get("subjects", [])
    weak = snapshot.get("weak_subjects_by_self_rating", [])
    plan: list[dict[str, str]] = []
    selected = focus_subject if focus_subject in subjects else None
    if selected:
        plan.append({
            "title": f"Start with {selected}",
            "reason": "You selected this as your current focus.",
            "action": "Choose one topic, review the official specification if available, then attempt a short practice set.",
        })
    elif weak:
        plan.append({
            "title": f"Prioritise {weak[0]}",
            "reason": "Your own confidence rating indicates that you want more support in this subject.",
            "action": "Identify one difficult topic and schedule a short, focused revision session.",
        })
    elif subjects:
        plan.append({
            "title": f"Review {subjects[0]}",
            "reason": "This is the first subject in your saved learning profile; no low-confidence subject was identified.",
            "action": "Pick a topic from the current official specification and check your understanding with practice questions.",
        })
    else:
        plan.append({
            "title": "Complete your learning profile",
            "reason": "EduBridge does not yet have your subjects or qualification.",
            "action": "Add only the education details you want to use for guidance.",
        })
    if snapshot.get("recent_questions"):
        plan.append({
            "title": "Continue your recent learning thread",
            "reason": "Recent questions are available in this browser session.",
            "action": "Review the last question and explain the part that still feels unclear.",
        })
    plan.append({
        "title": "Keep the plan manageable",
        "reason": f"Your selected weekly study allocation is {max(15, min(600, int(weekly_minutes)))} minutes.",
        "action": "Use short sessions, check understanding, and adjust the schedule based on your experience.",
    })
    return plan
