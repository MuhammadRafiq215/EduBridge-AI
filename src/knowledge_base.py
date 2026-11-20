"""Curated, source-aware retrieval for EduBridge AI.

Only explicitly reviewed official records are eligible for retrieval. This module
does not scrape the web, infer exam-board rules, or treat user-entered qualifications
as verified facts.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DEFAULT_KB_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge_base" / "documents.jsonl"
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for",
    "from", "how", "i", "in", "is", "it", "me", "my", "of", "on", "or", "our",
    "please", "the", "this", "to", "what", "when", "where", "which", "with", "you",
}


def _tokens(value: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z0-9]+", value.casefold())
        if len(token) > 1 and token not in STOP_WORDS
    }


def validate_record(record: dict[str, Any]) -> None:
    """Validate required metadata and prevent unreviewed or non-HTTPS sources."""
    required = ("source_id", "title", "issuer", "source_url", "qualification",
                "country", "board", "topic", "content", "status", "reviewed_at")
    missing = [key for key in required if not isinstance(record.get(key), str) or not record[key].strip()]
    if missing:
        raise ValueError("Missing required knowledge record fields: " + ", ".join(missing))
    if not record["source_url"].startswith("https://"):
        raise ValueError("Knowledge source URLs must use HTTPS.")
    if record["status"] not in {"verified", "review_required", "archived"}:
        raise ValueError("Status must be verified, review_required or archived.")
    if not isinstance(record.get("is_official"), bool):
        raise ValueError("is_official must be explicitly true or false.")
    if record["status"] == "verified" and not record["is_official"]:
        raise ValueError("Only official sources can be marked verified.")


def load_knowledge_records(path: str | Path = DEFAULT_KB_PATH) -> list[dict[str, Any]]:
    """Load JSONL records; malformed rows fail closed instead of being ignored."""
    file_path = Path(path)
    if not file_path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError("Each row must be a JSON object.")
            validate_record(record)
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"Invalid knowledge record on line {line_number}: {exc}") from exc
        records.append(record)
    return records


def _field_match(query_value: str | None, record_value: str) -> float:
    if not query_value:
        return 0.0
    query = query_value.casefold().strip()
    value = record_value.casefold().strip()
    if not value or value in {"general", "all", "not applicable"}:
        return 0.15
    if query == value:
        return 1.0
    if query in value or value in query:
        return 0.65
    return -0.2


def search_knowledge(
    query: str,
    qualification: str | None = None,
    country: str | None = None,
    board: str | None = None,
    limit: int = 4,
    path: str | Path = DEFAULT_KB_PATH,
) -> list[dict[str, Any]]:
    """Return ranked, verified official records relevant to the learner's question."""
    if not query.strip() or limit < 1:
        return []
    query_tokens = _tokens(query)
    if not query_tokens:
        return []
    ranked: list[tuple[float, dict[str, Any]]] = []
    for record in load_knowledge_records(path):
        if record["status"] != "verified" or record["is_official"] is not True:
            continue
        searchable = " ".join(str(record.get(key, "")) for key in ("title", "issuer", "qualification", "country", "board", "topic", "content"))
        doc_tokens = _tokens(searchable)
        overlap = len(query_tokens & doc_tokens) / max(1, len(query_tokens))
        score = overlap
        score += 0.30 * _field_match(qualification, record["qualification"])
        score += 0.15 * _field_match(country, record["country"])
        score += 0.15 * _field_match(board, record["board"])
        if qualification and _field_match(qualification, record["qualification"]) < 0:
            score -= 0.15
        if country and _field_match(country, record["country"]) < 0:
            score -= 0.10
        if score > 0.08:
            ranked.append((score, record))
    ranked.sort(key=lambda item: (-item[0], item[1]["source_id"]))
    return [record for _, record in ranked[:limit]]


def build_knowledge_context(records: list[dict[str, Any]]) -> str:
    """Format retrieved source excerpts for the model with strict citation labels."""
    if not records:
        return (
            "No matching verified official source was found in the local knowledge base. "
            "Do not imply that a board-specific rule has been verified. Give general "
            "educational guidance only where safe, and ask for the country, awarding body, "
            "qualification name or a link to the official document when needed."
        )
    blocks = []
    for record in records:
        blocks.append(
            f"[KB:{record['source_id']}] {record['title']} — {record['issuer']}\n"
            f"Qualification: {record['qualification']} | Country: {record['country']} | "
            f"Board: {record['board']} | Topic: {record['topic']}\n"
            f"Reviewed: {record['reviewed_at']} | Official source: {record['source_url']}\n"
            f"Content: {record['content']}"
        )
    return (
        "Use the following retrieved records only for claims they directly support. "
        "Cite supported facts using their exact [KB:source_id] labels. Do not invent "
        "citations or extend a rule to another qualification or year. If sources conflict "
        "or appear out of date, explain the limitation.\n\n" + "\n\n".join(blocks)
    )
