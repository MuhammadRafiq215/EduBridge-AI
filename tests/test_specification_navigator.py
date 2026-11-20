import unittest

from src.specification_engine import (
    SpecificationQuery,
    build_specification_context,
    classify_specification_topic,
    retrieve_specifications,
    specification_coverage_summary,
)
from src.student_navigator import build_navigation_plan, build_student_snapshot


class SpecificationEngineTests(unittest.TestCase):
    def test_classifies_grading_and_subject_specification_questions(self):
        self.assertEqual(classify_specification_topic("How are grade thresholds calculated?"), "grading_guidance")
        self.assertEqual(classify_specification_topic("What topics are in the syllabus?"), "subject_specification")

    def test_retrieves_official_grading_guidance_for_matching_scope(self):
        query = SpecificationQuery(
            question="Explain grade thresholds and component weighting",
            qualification="Cambridge IGCSE",
            country="International",
            awarding_body="Cambridge International",
        )
        records = retrieve_specifications(query)
        self.assertTrue(records)
        self.assertTrue(any("THRESHOLDS" in item["source_id"] for item in records))

    def test_context_warns_when_no_matching_specification_exists(self):
        query = SpecificationQuery(
            question="Find the 2026 biology subject specification",
            qualification="Unlisted Board Biology Certificate",
            country="Exampleland",
            awarding_body="Example Board",
            subject="Biology",
            exam_year="2026",
        )
        context = build_specification_context([], query)
        self.assertIn("no matching verified official specification", context)
        self.assertIn("exam year=2026", context)

    def test_coverage_summary_does_not_claim_completeness(self):
        summary = specification_coverage_summary()
        self.assertGreaterEqual(summary["verified_official_records"], 1)
        self.assertIn("do not mean complete", summary["coverage_warning"].lower())


class StudentNavigatorTests(unittest.TestCase):
    def test_snapshot_uses_only_profile_and_current_session_questions(self):
        profile = {
            "qualification": "Example A Levels",
            "subjects": ["Mathematics", "Computer Science"],
            "confidence": {"Mathematics": 2, "Computer Science": 4},
            "latest_results": {"Mathematics": "B"},
            "email": "should-not-be-included",
        }
        history = [
            {"role": "user", "content": "Explain recursion"},
            {"role": "assistant", "content": "A recursive function..."},
            {"role": "user", "content": "How does Big O work?"},
        ]
        snapshot = build_student_snapshot(profile, history)
        self.assertEqual(snapshot["weak_subjects_by_self_rating"], ["Mathematics"])
        self.assertEqual(snapshot["recent_question_count"], 2)
        self.assertNotIn("email", snapshot)

    def test_plan_prioritises_student_selected_focus(self):
        snapshot = build_student_snapshot({
            "subjects": ["Mathematics", "Computer Science"],
            "confidence": {"Mathematics": 1},
        })
        plan = build_navigation_plan(snapshot, focus_subject="Computer Science")
        self.assertIn("Start with Computer Science", plan[0]["title"])

    def test_plan_uses_self_reported_confidence_not_predicted_grade(self):
        snapshot = build_student_snapshot({
            "subjects": ["Mathematics"],
            "confidence": {"Mathematics": 1},
        })
        plan = build_navigation_plan(snapshot)
        self.assertIn("Prioritise Mathematics", plan[0]["title"])
        self.assertNotIn("predicted_grade", snapshot)


if __name__ == "__main__":
    unittest.main()
