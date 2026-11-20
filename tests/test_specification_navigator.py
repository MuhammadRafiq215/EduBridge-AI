import unittest

from src.knowledge_base import EducationalKnowledgeBase, load_registry
from src.specification_engine import (
    SpecificationQuery,
    build_specification_context,
    classify_specification_topic,
    find_subject_catalogue,
    retrieve_specifications,
    specification_coverage_summary,
)
from src.student_navigator import build_navigation_plan, build_student_snapshot


class SpecificationEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = EducationalKnowledgeBase()

    def test_classifies_grading_and_syllabus_questions(self):
        self.assertEqual(classify_specification_topic("How are grade thresholds set?"), "grading")
        self.assertEqual(classify_specification_topic("What topics are in the syllabus?"), "subject_specification")

    def test_retrieves_cambridge_awarding_source(self):
        query = SpecificationQuery(
            question="How are Cambridge grade thresholds decided?",
            jurisdiction="Global",
            qualification="IGCSE",
            awarding_body="Cambridge International",
        )
        records = retrieve_specifications(query, knowledge_base=self.kb)
        self.assertTrue(records)
        self.assertEqual(records[0]["source_id"], "cambridge-awarding")

    def test_subject_catalogue_is_labelled_as_catalogue_not_specification(self):
        matches = find_subject_catalogue("Mathematics", jurisdiction="Global", qualification="IGCSE")
        self.assertTrue(matches)
        self.assertIn(matches[0]["status"], {"catalogue_verified", "historical_reference"})

    def test_context_discloses_missing_exact_specification(self):
        query = SpecificationQuery(
            question="Explain the 2027 Biology practical paper",
            jurisdiction="Exampleland",
            qualification="Unlisted Biology Certificate",
            awarding_body="Example Board",
            subject="Biology",
            exam_year="2027",
        )
        context = build_specification_context([], query)
        self.assertIn("Do not invent", context)
        self.assertIn("exam year=2027", context)
        self.assertIn("Only specification_verified", context)

    def test_coverage_summary_warns_against_completeness(self):
        summary = specification_coverage_summary(load_registry())
        self.assertGreater(summary["source_records"], 0)
        self.assertIn("not complete", summary["coverage_warning"])


class StudentNavigatorTests(unittest.TestCase):
    def test_snapshot_uses_profile_and_current_session_history_only(self):
        profile = {
            "qualification": "Example A Levels",
            "subjects": ["Mathematics", "Computer Science"],
            "confidence": {"Mathematics": 2, "Computer Science": 4},
            "latest_results": {"Mathematics": "B"},
            "email": "not-for-ai-context",
        }
        history = [
            {"role": "user", "content": "Explain recursion"},
            {"role": "assistant", "content": "A recursive function calls itself."},
            {"role": "user", "content": "How does Big O work?"},
        ]
        snapshot = build_student_snapshot(profile, history)
        self.assertEqual(snapshot["subjects"], ["Mathematics", "Computer Science"])
        self.assertEqual(snapshot["recent_questions"], ["Explain recursion", "How does Big O work?"])
        self.assertNotIn("email", snapshot)

    def test_navigation_plan_uses_student_selected_subject(self):
        snapshot = build_student_snapshot({"subjects": ["Mathematics", "Computer Science"]})
        plan = build_navigation_plan(snapshot, focus_subject="Computer Science")
        self.assertIn("Computer Science", plan[0]["title"])

    def test_navigation_plan_prioritises_low_self_reported_confidence(self):
        snapshot = build_student_snapshot({
            "subjects": ["Mathematics"],
            "confidence": {"Mathematics": 1},
        })
        plan = build_navigation_plan(snapshot)
        self.assertIn("Mathematics", plan[0]["title"])
        self.assertNotIn("predicted_grade", snapshot)


if __name__ == "__main__":
    unittest.main()
