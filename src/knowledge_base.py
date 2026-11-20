"""Source-aware educational knowledge retrieval for EduBridge AI."""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "data" / "knowledge" / "source_registry.json"

def load_registry(path=DEFAULT_REGISTRY) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema_version") != "1.0":
        raise ValueError("Unsupported knowledge registry schema version.")
    ids = [row["source_id"] for row in payload.get("sources", [])]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate source_id in knowledge registry.")
    return payload

def _text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def _document_text(row):
    values = [row.get("title"), row.get("qualification"), row.get("system"),
              row.get("jurisdiction"), row.get("topics", []), row.get("summary"),
              row.get("verified_notes", [])]
    return _text(" ".join(" ".join(map(str, x)) if isinstance(x, list) else str(x or "") for x in values))

class EducationalKnowledgeBase:
    """TF-IDF retrieval over reviewed official-source notes, with filters."""
    INDEXABLE = {"verified_snippet", "specification_verified", "catalogue_verified"}
    def __init__(self, registry=None):
        self.registry = registry or load_registry()
        self.documents = [x for x in self.registry.get("sources", [])
                          if x.get("status") in self.INDEXABLE and x.get("source_url") and x.get("verified_notes")]
        self.vectorizer = self.matrix = None
        if self.documents:
            self.vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2),
                strip_accents="unicode", sublinear_tf=True, token_pattern=r"(?u)\b\w+\b")
            self.matrix = self.vectorizer.fit_transform([_document_text(x) for x in self.documents])

    def search(self, query, *, jurisdiction=None, qualification=None, top_k=5):
        query = _text(query)
        if not query or self.matrix is None:
            return []
        scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix).ravel()
        results = []
        for i, score in enumerate(scores):
            row = self.documents[i]
            if jurisdiction and jurisdiction.casefold() not in (row.get("jurisdiction", "") + " " + row.get("system", "")).casefold():
                continue
            if qualification and qualification.casefold() not in (row.get("qualification", "") + " " + row.get("title", "")).casefold():
                continue
            if score > 0:
                results.append({**row, "relevance_score": round(float(score), 4),
                                "matched_notes": row.get("verified_notes", [])})
        return sorted(results, key=lambda x: x["relevance_score"], reverse=True)[:max(1, top_k)]

def evaluate_retrieval(kb, cases, top_k=5):
    evaluated, hits, rr = [], 0, []
    for case in cases:
        expected = set(case.get("expected_source_ids", []))
        found = kb.search(case["query"], top_k=top_k)
        ids = [x["source_id"] for x in found]
        rank = next((i + 1 for i, sid in enumerate(ids) if sid in expected), None)
        hits += int(rank is not None)
        rr.append(1 / rank if rank else 0.0)
        evaluated.append({"case_id": case.get("case_id"), "query": case["query"],
            "expected_source_ids": sorted(expected), "retrieved_source_ids": ids,
            "hit_at_k": rank is not None, "reciprocal_rank": round(1 / rank, 4) if rank else 0.0})
    n = len(cases)
    return {"total_cases": n, "recall_at_k": round(hits / n, 4) if n else 0.0,
            "mrr_at_k": round(sum(rr) / n, 4) if n else 0.0, "k": top_k,
            "results": evaluated,
            "warning": "Small curated development set; scores do not establish broad answer accuracy."}
