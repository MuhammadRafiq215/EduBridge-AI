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


    def test_personalised_recommendations_explain_priority(self):
        from src.student_guidance import build_personalised_recommendations
        result = build_personalised_recommendations(self.profile)
        self.assertEqual(result["recommendations"][0]["subject"], "Mathematics")
        self.assertIn("confidence rating is 2/5", result["recommendations"][0]["reason"])
        self.assertIn("a trained ML model", result["note"])
        self.assertEqual(result["weekly_hours"], 8)

    def test_pathway_gaps_are_reported(self):
        from src.student_guidance import build_personalised_recommendations
        result = build_personalised_recommendations(self.profile)
        self.assertIn("Computing", result["pathway_gaps"])


if __name__ == "__main__":
    unittest.main()
