"""Official specification engine built on reviewed knowledge-base records.

The engine exposes scope-aware source retrieval and structured metadata. It does not
turn a general overview into a subject specification or infer missing exam rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.knowledge_base import load_knowledge_records, search_knowledge

SPECIFICATION_TYPES = {
    "qualification_overview",
    "subject_specification",
    "assessment_guidance",
    "grading_guidance",
    "recognition_guidance",
    "learning_resource",
    "other_official_guidance",
}


@dataclass(frozen=True)
class SpecificationQuery:
    question: str
    qualification: str | None = None
    country: str | None = None
    awarding_body: str | None = None
    subject: str | None = None
    exam_year: str | None = None
    exam_series: str | None = None


def classify_specification_topic(question: str) -> str:
    """Classify the kind of official specification evidence a question needs."""
    text = question.casefold()
    if any(word in text for word in ("grade", "threshold", "mark scheme", "percentage", "grading")):
        return "grading_guidance"
    if any(word in text for word in ("paper", "component", "assessment", "coursework", "practical", "exam format")):
        return "assessment_guidance"
    if any(word in text for word in ("equivalence", "recognition", "admission", "entry requirement")):
        return "recognition_guidance"
    if any(word in text for word in ("syllabus", "specification", "learning outcome", "topic", "content")):
        return "subject_specification"
    return "qualification_overview"


def _matches_scope(record: dict[str, Any], query: SpecificationQuery) -> bool:
    """Reject known scope conflicts; unknown scope remains visibly unknown."""
    checks = (
        (query.qualification, record.get("qualification", "")),
        (query.country, record.get("country", "")),
        (query.awarding_body, record.get("board", "")),
        (query.subject, record.get("subject", "")),
    )
    for requested, actual in checks:
        if not requested or not actual or actual.casefold() in {"general", "all", "not specified"}:
            continue
        if requested.casefold() not in actual.casefold() and actual.casefold() not in requested.casefold():
            # "International" is a legitimate broad country scope, not a mismatch.
            if actual.casefold() != "international":
                return False
    return True


def retrieve_specifications(
    query: SpecificationQuery,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Retrieve official sources, applying qualification/board/subject scope checks."""
    if not query.question.strip() or limit < 1:
        return []
    candidates = search_knowledge(
        query.question,
        qualification=query.qualification,
        country=query.country,
        board=query.awarding_body,
        limit=max(limit * 3, 12),
    )
    results = [record for record in candidates if _matches_scope(record, query)]
    requested_topic = classify_specification_topic(query.question)
    exact = [record for record in results if record.get("document_type") == requested_topic]
    ordered = exact + [record for record in results if record not in exact]
    return ordered[:limit]


def build_specification_context(records: list[dict[str, Any]], query: SpecificationQuery) -> str:
    """Build an explicit, bounded evidence context for the tutor."""
    scope = (
        f"Qualification={query.qualification or 'not supplied'}; "
        f"country={query.country or 'not supplied'}; "
        f"awarding body={query.awarding_body or 'not supplied'}; "
        f"subject={query.subject or 'not supplied'}; "
        f"exam year={query.exam_year or 'not supplied'}; "
        f"exam series={query.exam_series or 'not supplied'}."
    )
    if not records:
        return (
            "SPECIFICATION ENGINE RESULT: no matching verified official specification "
            "or guidance was found. " + scope + " Do not invent syllabus content, "
            "assessment components, grade thresholds, or current rules. Ask for the "
            "official specification or provide clearly labelled general study help."
        )
    sections = []
    for record in records:
        sections.append(
            f"[SPEC:{record['source_id']}] {record['title']} | Issuer: {record['issuer']}\n"
            f"Scope: qualification={record['qualification']}; country={record['country']}; "
            f"awarding body={record['board']}; subject={record.get('subject', 'not specified')}; "
            f"document type={record.get('document_type', 'not classified')}; "
            f"version={record.get('version', 'not recorded')}; "
            f"effective period={record.get('effective_from', 'not recorded')} to "
            f"{record.get('effective_to', 'not recorded')}.\n"
            f"Reviewed={record['reviewed_at']}; source={record['source_url']}\n"
            f"Reviewed summary: {record['content']}"
        )
    return (
        "SPECIFICATION ENGINE EVIDENCE. " + scope + "\n"
        "Use evidence only within its recorded scope. An overview is not a subject "
        "specification. If year, series, subject or version is missing, state that "
        "limitation and request the current official document. Cite exact [SPEC:id] "
        "labels for sourced facts; do not invent specification details.\n\n"
        + "\n\n".join(sections)
    )


def specification_coverage_summary() -> dict[str, Any]:
    """Return transparent counts by qualification, source type and review status."""
    records = load_knowledge_records()
    verified = [r for r in records if r.get("status") == "verified" and r.get("is_official") is True]
    by_type: dict[str, int] = {}
    for record in verified:
        kind = record.get("document_type", "unclassified")
        by_type[kind] = by_type.get(kind, 0) + 1
    return {
        "verified_official_records": len(verified),
        "qualification_labels": sorted({r["qualification"] for r in verified}),
        "awarding_bodies": sorted({r["board"] for r in verified}),
        "document_types": by_type,
        "subject_specifications": sum(r.get("document_type") == "subject_specification" for r in verified),
        "coverage_warning": "Record counts do not mean complete board, subject or year coverage.",
    }
