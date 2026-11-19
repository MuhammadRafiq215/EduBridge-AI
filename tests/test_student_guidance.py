import unittest

from src.student_guidance import build_learning_snapshot, build_weekly_plan


class StudentGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.profile = {
            "level": "Intermediate / A Levels",
            "pathway": "Engineering",
            "weekly_hours": 8,
            "confidence": {"Mathematics": 2, "Physics": 4, "Chemistry": 3},
        }

    def test_snapshot_identifies_self_reported_focus_and_strengths(self):
        result = build_learning_snapshot(self.profile)
        self.assertEqual(result["focus_subjects"], ["Mathematics", "Chemistry"])
        self.assertEqual(result["strength_subjects"], ["Physics"])
        self.assertEqual(result["subjects_rated"], 3)
        self.assertIn("not an objective grade", result["note"])

    def test_weekly_plan_allocates_all_hours(self):
        plan = build_weekly_plan(self.profile)
        self.assertEqual(sum(row["hours"] for row in plan), 8)
        self.assertLessEqual(len(plan), 3)

    def test_empty_confidence_is_rejected(self):
        with self.assertRaises(ValueError):
            build_learning_snapshot({"pathway": "Engineering", "confidence": {}})


if __name__ == "__main__":
    unittest.main()
