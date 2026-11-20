"""Student Navigator using learner-approved profile and temporary chat context."""
from __future__ import annotations

from typing import Any


def build_student_snapshot(
    profile: dict[str, Any] | None,
    chat_history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build a minimal educational snapshot; do not infer identity or academic outcomes."""
    profile = profile if isinstance(profile, dict) else {}
    subjects = profile.get("subjects", [])
    confidence = profile.get("confidence", {})
    results = profile.get("latest_results", {})
    recent = [
        item.get("content", "").strip()
        for item in (chat_history or [])[-12:]
        if item.get("role") == "user" and isinstance(item.get("content"), str) and item.get("content").strip()
    ]
    return {
        "country": profile.get("country") or "Not specified",
        "level": profile.get("level") or "Not specified",
        "qualification": profile.get("qualification") or profile.get("custom_qualification") or "Not specified",
        "awarding_body": profile.get("board") or "Not specified",
        "subjects": [x for x in subjects if isinstance(x, str)] if isinstance(subjects, list) else [],
        "confidence": confidence if isinstance(confidence, dict) else {},
        "results": {k: v for k, v in results.items() if isinstance(v, str) and v.strip()} if isinstance(results, dict) else {},
        "recent_questions": recent[-4:],
        "memory_scope": "Saved profile plus current browser session only.",
    }


def build_navigation_plan(snapshot: dict[str, Any], focus_subject: str | None = None) -> list[dict[str, str]]:
    subjects = snapshot.get("subjects", [])
    confidence = snapshot.get("confidence", {})
    weak = [s for s in subjects if isinstance(confidence.get(s), (int, float)) and confidence[s] <= 2]
    plan: list[dict[str, str]] = []
    if focus_subject in subjects:
        plan.append({
            "title": f"Your chosen focus: {focus_subject}",
            "reason": "You selected this subject as your next priority.",
            "action": "Choose one topic, locate the current official specification, then practise a short set of questions.",
        })
    elif weak:
        plan.append({
            "title": f"Give {weak[0]} extra attention",
            "reason": "Your own confidence rating indicates that you would like more support in this subject.",
            "action": "Pick one topic you find difficult, review the official specification where available, and practise it in a short session.",
        })
    elif subjects:
        plan.append({
            "title": f"Continue with {subjects[0]}",
            "reason": "No low-confidence subject was identified from your self-ratings.",
            "action": "Choose a topic from your current course and test your understanding with practice questions.",
        })
    else:
        plan.append({
            "title": "Set up your learning profile",
            "reason": "Your subjects and qualification are not yet available to the Navigator.",
            "action": "Add the education details you want EduBridge to use for guidance.",
        })
    if snapshot.get("recent_questions"):
        plan.append({
            "title": "Continue your recent learning",
            "reason": "Recent questions from this browser session are available.",
            "action": "Revisit the last topic and ask the AI Teacher to explain any step that remains unclear.",
        })
    plan.append({
        "title": "Review your progress regularly",
        "reason": "The Navigator uses your self-reported information and does not predict grades.",
        "action": "Update your confidence or latest results when you choose, then adjust your next study focus.",
    })
    return plan
