import json
import tempfile
import unittest
from pathlib import Path

from src.knowledge_base import build_knowledge_context, load_knowledge_records, search_knowledge, validate_record


def official_record(**overrides):
    record = {
        "source_id": "EXAM-001",
        "title": "Official assessment and grading guide",
        "issuer": "Example Examination Authority",
        "source_url": "https://example.edu/assessment-guide",
        "qualification": "Example Senior Certificate",
        "country": "Exampleland",
        "board": "Example Board",
        "topic": "assessment grading results",
        "content": "The authority publishes assessment and grading information in its official guide.",
        "status": "verified",
        "reviewed_at": "2026-11-20",
        "is_official": True,
    }
    record.update(overrides)
    return record


class KnowledgeBaseTests(unittest.TestCase):
    def write_records(self, path, records):
        path.write_text("\n".join(json.dumps(item) for item in records), encoding="utf-8")

    def test_loads_valid_jsonl_records(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "documents.jsonl"
            self.write_records(path, [official_record()])
            self.assertEqual(len(load_knowledge_records(path)), 1)

    def test_missing_knowledge_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(load_knowledge_records(Path(folder) / "missing.jsonl"), [])

    def test_invalid_record_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "documents.jsonl"
            path.write_text('{"source_id":"incomplete"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_knowledge_records(path)

    def test_unreviewed_and_non_official_sources_are_not_retrieved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "documents.jsonl"
            self.write_records(path, [
                official_record(source_id="DRAFT", status="review_required"),
                official_record(source_id="NONOFFICIAL", is_official=False, status="review_required"),
            ])
            self.assertEqual(search_knowledge("assessment grading", path=path), [])

    def test_retrieves_matching_verified_record(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "documents.jsonl"
            self.write_records(path, [official_record()])
            found = search_knowledge(
                "assessment grading information",
                qualification="Example Senior Certificate",
                country="Exampleland",
                board="Example Board",
                path=path,
            )
            self.assertEqual([item["source_id"] for item in found], ["EXAM-001"])

    def test_custom_unlisted_qualification_can_use_relevant_general_record(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "documents.jsonl"
            self.write_records(path, [official_record(qualification="General", country="General", board="General")])
            found = search_knowledge("assessment grading", qualification="Student-entered qualification", path=path)
            self.assertEqual(len(found), 1)

    def test_no_match_is_explicitly_not_verified(self):
        context = build_knowledge_context([])
        self.assertIn("No matching verified official source", context)
        self.assertIn("Do not imply", context)

    def test_context_includes_exact_citation_identifier_and_source(self):
        context = build_knowledge_context([official_record()])
        self.assertIn("[KB:EXAM-001]", context)
        self.assertIn("https://example.edu/assessment-guide", context)

    def test_verified_record_requires_official_https_source(self):
        with self.assertRaises(ValueError):
            validate_record(official_record(source_url="http://example.edu"))
        with self.assertRaises(ValueError):
            validate_record(official_record(is_official=False))


if __name__ == "__main__":
    unittest.main()
