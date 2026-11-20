"""Specification-aware retrieval over EduBridge's reviewed source registry."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.knowledge_base import EducationalKnowledgeBase, load_registry

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUBJECT_CATALOG = ROOT / "data" / "knowledge" / "subject_catalog.json"


@dataclass(frozen=True)
class SpecificationQuery:
    question: str
    jurisdiction: str | None = None
    qualification: str | None = None
    awarding_body: str | None = None
    subject: str | None = None
    exam_year: str | None = None
    exam_series: str | None = None


def classify_specification_topic(question: str) -> str:
    text = question.casefold()
    if any(x in text for x in ("grade threshold", "grade boundaries", "grading", "grade", "marks to get")):
        return "grading"
    if any(x in text for x in ("paper", "component", "assessment", "coursework", "practical", "exam format")):
        return "assessment"
    if any(x in text for x in ("equivalence", "recognition", "entry requirement", "admission")):
        return "recognition"
    if any(x in text for x in ("syllabus", "specification", "learning outcome", "topics", "course content")):
        return "subject_specification"
    return "qualification_overview"


def _board_matches(row: dict[str, Any], awarding_body: str | None) -> bool:
    if not awarding_body:
        return True
    searchable = " ".join(str(row.get(key, "")) for key in ("system", "publisher", "title", "qualification"))
    return awarding_body.casefold() in searchable.casefold() or searchable.casefold() in awarding_body.casefold()


def retrieve_specifications(
    query: SpecificationQuery,
    knowledge_base: EducationalKnowledgeBase | None = None,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Retrieve only reviewed/indexable records, with strict known-scope filtering."""
    if not query.question.strip() or top_k < 1:
        return []
    kb = knowledge_base or EducationalKnowledgeBase()
    enriched_query = " ".join(
        x for x in (query.question, query.subject, query.exam_year, query.exam_series, query.awarding_body) if x
    )
    candidates = kb.search(
        enriched_query,
        jurisdiction=query.jurisdiction,
        qualification=query.qualification,
        top_k=max(top_k * 3, 12),
    )
    results = [row for row in candidates if _board_matches(row, query.awarding_body)]
    return results[:top_k]


def find_subject_catalogue(
    subject: str,
    jurisdiction: str | None = None,
    qualification: str | None = None,
    path: str | Path = DEFAULT_SUBJECT_CATALOG,
) -> list[dict[str, Any]]:
    """Find catalogue mentions; these are not proof of a full subject specification."""
    import json

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    matches = []
    for row in payload.get("catalogues", []):
        if jurisdiction and jurisdiction.casefold() not in row.get("jurisdiction", "").casefold():
            continue
        if qualification and qualification.casefold() not in (
            row.get("qualification", "") + " " + row.get("system", "")
        ).casefold():
            continue
        subjects = row.get("subjects", [])
        if any(subject.casefold() == item.casefold() for item in subjects):
            matches.append({
                "jurisdiction": row.get("jurisdiction"),
                "system": row.get("system"),
                "qualification": row.get("qualification"),
                "status": row.get("status"),
                "note": row.get("note"),
                "source_ids": row.get("source_ids", []),
            })
    return matches


def build_specification_context(
    records: list[dict[str, Any]],
    query: SpecificationQuery,
    subject_catalogue: list[dict[str, Any]] | None = None,
) -> str:
    """Format source excerpts and scope gaps for the AI tutor."""
    scope = (
        f"Jurisdiction={query.jurisdiction or 'not supplied'}; "
        f"qualification={query.qualification or 'not supplied'}; "
        f"awarding body={query.awarding_body or 'not supplied'}; "
        f"subject={query.subject or 'not supplied'}; "
        f"exam year={query.exam_year or 'not supplied'}; "
        f"exam series={query.exam_series or 'not supplied'}."
    )
    if not records:
        evidence = (
            "No matching reviewed official source was retrieved. Do not invent a "
            "board-specific syllabus, assessment structure, grade boundary, "
            "equivalence rule or current-year requirement."
        )
    else:
        sections = []
        for row in records:
            sections.append(
                f"[SPEC:{row['source_id']}] {row.get('title', 'Official source')} | "
                f"Issuer: {row.get('publisher', row.get('system', 'Not recorded'))}\n"
                f"System: {row.get('system', 'Not recorded')} | "
                f"Qualification: {row.get('qualification', 'Not recorded')} | "
                f"Jurisdiction: {row.get('jurisdiction', 'Not recorded')} | "
                f"Status: {row.get('status', 'Not recorded')} | "
                f"Reviewed: {row.get('reviewed_on', 'Not recorded')}\n"
                f"Source: {row.get('source_url', 'Not recorded')}\n"
                f"Verified notes: {' '.join(row.get('matched_notes', row.get('verified_notes', [])))}\n"
                f"Limits: {row.get('limits', 'Use only within the source scope.')}"
            )
        evidence = "\n\n".join(sections)
    catalogue_text = ""
    if subject_catalogue:
        catalogue_text = "\nSubject catalogue evidence (not a full specification):\n" + "\n".join(
            f"- {x['system']} / {x['qualification']} ({x['status']}): {x['note']}"
            for x in subject_catalogue
        )
    return (
        "OFFICIAL SPECIFICATION ENGINE CONTEXT\n" + scope + "\n"
        "Important: verified_snippet is a reviewed summary, not a full subject specification. "
        "catalogue_verified confirms catalogue discovery only. Only specification_verified "
        "records may be described as reviewed subject specifications. If the exact subject, "
        "version, year or series is not evidenced, disclose the gap and ask for the official "
        "document. Cite exact [SPEC:source_id] labels for supported claims. Never invent "
        "citations or infer a grade from raw marks without an exact official table.\n\n"
        + evidence + catalogue_text
    )


def specification_coverage_summary(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = registry or load_registry()
    sources = registry.get("sources", [])
    coverage = registry.get("coverage", [])
    return {
        "source_records": len(sources),
        "specification_verified": sum(x.get("status") == "specification_verified" for x in sources),
        "verified_snippets": sum(x.get("status") == "verified_snippet" for x in sources),
        "catalogue_verified_systems": sum(x.get("status") == "catalogue_verified" for x in coverage),
        "discovery_pending_systems": sum(x.get("status") == "discovery_pending" for x in coverage),
        "coverage_warning": "A verified snippet or catalogue is not complete subject-specification coverage.",
    }
