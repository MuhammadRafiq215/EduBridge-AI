"""Guided practice scaffolds and safe learner-response validation.

Offline prompts are metacognitive study tasks, not subject-specific answer keys.
A configured AI provider may generate subject-aware questions and feedback.
"""
from __future__ import annotations

from datetime import date
from typing import Any

MAX_SUBJECT_LENGTH = 80
MAX_TOPIC_LENGTH = 120
MAX_ANSWER_LENGTH = 5000
DIFFICULTIES = ("Foundations", "Developing", "Challenge")
PRACTICE_FORMATS = ("Mixed practice", "Recall and explain", "Apply a method", "Find and fix an error")


def normalise_practice_request(
    subject: str, topic: str, difficulty: str, practice_format: str
) -> dict[str, str]:
    subject = str(subject or "").strip()[:MAX_SUBJECT_LENGTH]
    topic = str(topic or "").strip()[:MAX_TOPIC_LENGTH]
    difficulty = str(difficulty or "").strip()
    practice_format = str(practice_format or "").strip()
    if not subject or not topic:
        raise ValueError("Choose a subject and enter one specific topic.")
    if difficulty not in DIFFICULTIES:
        raise ValueError("Choose one of the available difficulty levels.")
    if practice_format not in PRACTICE_FORMATS:
        raise ValueError("Choose one of the available practice formats.")
    return {
        "subject": subject,
        "topic": topic,
        "difficulty": difficulty,
        "practice_format": practice_format,
    }


def build_practice_generation_prompt(request: dict[str, str]) -> str:
    """Build a bounded request for an age-appropriate, stepwise practice set."""
    clean = normalise_practice_request(
        request.get("subject", ""),
        request.get("topic", ""),
        request.get("difficulty", ""),
        request.get("practice_format", ""),
    )
    return (
        "Create a short, age-appropriate guided practice set for a learner.\n"
        f"Subject: {clean['subject']}\nTopic: {clean['topic']}\n"
        f"Difficulty: {clean['difficulty']}\nFormat: {clean['practice_format']}\n\n"
        "Return exactly three numbered questions, increasing gently in challenge. "
        "For each question include one small hint, but do not reveal the answer yet. "
        "Use clear language and show any assumptions. Avoid unsafe activities. "
        "Do not claim alignment to a particular examination board unless the supplied "
        "verified source context explicitly supports it. If the topic is ambiguous, "
        "state the interpretation you chose. Finish by asking the learner to attempt "
        "the questions in their own words. Do not invent source citations."
    )


def build_offline_practice_scaffold(request: dict[str, str]) -> list[dict[str, str]]:
    """Return transparent, content-neutral practice steps when no model is configured."""
    clean = normalise_practice_request(
        request.get("subject", ""),
        request.get("topic", ""),
        request.get("difficulty", ""),
        request.get("practice_format", ""),
    )
    subject, topic = clean["subject"], clean["topic"]
    return [
        {
            "step": "Recall",
            "task": f"Without looking at your notes, write what you already know about {topic} in {subject}.",
            "check": "Underline any term or step you could not explain clearly.",
        },
        {
            "step": "Explain",
            "task": f"Choose one key idea in {topic} and explain it as if teaching a classmate.",
            "check": "Include a definition, the reason it matters, and one example from your course material.",
        },
        {
            "step": "Apply",
            "task": f"Use a question from your textbook or teacher's notes about {topic}. Attempt it independently.",
            "check": "Compare your method with the worked solution and note one improvement.",
        },
    ]


def normalise_practice_attempt(
    request: dict[str, str],
    answer: str,
    confidence: int,
    self_check: str,
) -> dict[str, Any]:
    clean = normalise_practice_request(
        request.get("subject", ""),
        request.get("topic", ""),
        request.get("difficulty", ""),
        request.get("practice_format", ""),
    )
    answer = str(answer or "").strip()
    if not answer:
        raise ValueError("Write at least a short attempt before recording your practice.")
    if len(answer) > MAX_ANSWER_LENGTH:
        raise ValueError(f"Keep your practice response under {MAX_ANSWER_LENGTH} characters.")
    if isinstance(confidence, bool) or not 1 <= int(confidence) <= 5:
        raise ValueError("Confidence must be between 1 and 5.")
    allowed_checks = {
        "I can explain it in my own words",
        "I understand some of it",
        "I need to review this topic",
    }
    if self_check not in allowed_checks:
        raise ValueError("Choose one of the self-check options.")
    return {
        **clean,
        "answer": answer,
        "confidence": int(confidence),
        "self_check": self_check,
        "studied_on": date.today().isoformat(),
        "attempted": 1,
        # A self-check is not an independently marked score. Keep correctness unknown.
        "correct": 0,
        "marking_status": "self_reflection_only",
    }
