import unittest
from datetime import date
from src.guided_practice import (
    build_offline_practice_scaffold,
    build_practice_generation_prompt,
    normalise_practice_attempt,
    normalise_practice_request,
)
from src.adaptive_learning import build_revision_schedule


class GuidedPracticeTests(unittest.TestCase):
    def setUp(self):
        self.request = {
            "subject": "Computer Science",
            "topic": "Recursion",
            "difficulty": "Developing",
            "practice_format": "Mixed practice",
        }

    def test_request_is_normalised(self):
        result = normalise_practice_request(**self.request)
        self.assertEqual(result["topic"], "Recursion")

    def test_rejects_empty_or_invalid_request(self):
        with self.assertRaises(ValueError):
            normalise_practice_request("Maths", "", "Foundations", "Mixed practice")
        with self.assertRaises(ValueError):
            normalise_practice_request("Maths", "Algebra", "Expert", "Mixed practice")

    def test_generation_prompt_is_subject_and_topic_aware(self):
        prompt = build_practice_generation_prompt(self.request)
        self.assertIn("Computer Science", prompt)
        self.assertIn("Recursion", prompt)
        self.assertIn("exactly three numbered questions", prompt)

    def test_offline_scaffold_is_explicitly_generic_and_actionable(self):
        steps = build_offline_practice_scaffold(self.request)
        self.assertEqual([row["step"] for row in steps], ["Recall", "Explain", "Apply"])
        self.assertTrue(all("Recursion" in row["task"] for row in steps))

    def test_attempt_requires_answer_and_valid_self_check(self):
        with self.assertRaises(ValueError):
            normalise_practice_attempt(self.request, "", 3, "I understand some of it")
        with self.assertRaises(ValueError):
            normalise_practice_attempt(self.request, "My answer", 3, "Perfect")
        result = normalise_practice_attempt(
            self.request, "Recursion is a function calling itself.", 3,
            "I understand some of it"
        )
        self.assertEqual(result["marking_status"], "self_reflection_only")
        self.assertEqual(result["correct"], 0)

    def test_revision_schedule_uses_transparent_intervals(self):
        entries = [
            {"subject": "Maths", "topic": "Algebra", "confidence": 2,
             "attempted": 0, "correct": 0, "studied_on": "2026-11-20"},
            {"subject": "Physics", "topic": "Waves", "confidence": 5,
             "attempted": 10, "correct": 9, "studied_on": "2026-11-20"},
        ]
        schedule = build_revision_schedule(entries, today=date(2026, 11, 21))
        by_topic = {row["topic"]: row for row in schedule}
        self.assertEqual(by_topic["Algebra"]["review_on"], "2026-11-22")
        self.assertEqual(by_topic["Waves"]["review_on"], "2026-11-28")


if __name__ == "__main__":
    unittest.main()
