import unittest
from datetime import date
from src.student_intelligence import build_student_intelligence


class StudentIntelligenceTests(unittest.TestCase):
    def test_latest_topic_reflection_is_used(self):
        result = build_student_intelligence([
            {"subject":"Maths","topic":"Algebra","confidence":2,"attempted":0,"correct":0,"studied_on":"2026-11-19"},
            {"subject":"Maths","topic":"Algebra","confidence":4,"attempted":5,"correct":4,"studied_on":"2026-11-20"},
        ], today=date(2026,11,21))
        self.assertEqual(result["topic_count"],1)
        self.assertEqual(result["topics"][0]["confidence"],4)
        self.assertEqual(result["topics"][0]["accuracy"],80.0)

    def test_streak_and_weekly_active_days_are_date_based(self):
        result = build_student_intelligence([
            {"subject":"CS","topic":"A","confidence":3,"attempted":0,"correct":0,"studied_on":"2026-11-19"},
            {"subject":"CS","topic":"B","confidence":3,"attempted":0,"correct":0,"studied_on":"2026-11-20"},
            {"subject":"CS","topic":"C","confidence":3,"attempted":0,"correct":0,"studied_on":"2026-11-21"},
        ], today=date(2026,11,21))
        self.assertEqual(result["learning_streak"],3)
        self.assertEqual(result["active_days_last_7"],3)

    def test_invalid_records_are_ignored(self):
        result = build_student_intelligence([{"subject":"CS","topic":"Bad","confidence":9}], today=date(2026,11,21))
        self.assertEqual(result["topic_count"],0)
        self.assertEqual(result["learning_streak"],0)

    def test_practice_accuracy_is_not_inferred_without_attempts(self):
        result = build_student_intelligence([
            {"subject":"Physics","topic":"Waves","confidence":2,"attempted":0,"correct":0,"studied_on":"2026-11-21"}
        ], today=date(2026,11,21))
        self.assertIsNone(result["topics"][0]["accuracy"])
        self.assertEqual(result["topics"][0]["evidence"],"Provisional reflection")


if __name__ == "__main__":
    unittest.main()
