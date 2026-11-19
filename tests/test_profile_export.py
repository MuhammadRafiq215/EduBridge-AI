import unittest

from src.profile_export import build_profile_pdf


class ProfilePdfTests(unittest.TestCase):
    def test_profile_export_is_a_pdf(self):
        profile = {
            "level": "A Levels",
            "board": "Cambridge",
            "pathway": "Computer Science & AI",
            "programme": "A Levels",
            "current_year": "A2",
            "weekly_hours": 8,
            "subjects": ["Mathematics", "Computer Science"],
            "confidence": {"Mathematics": 3, "Computer Science": 4},
            "latest_results": {"Mathematics": "B", "Computer Science": ""},
            "updated": "2026-11-19",
        }
        pdf = build_profile_pdf(profile)
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 500)

    def test_empty_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            build_profile_pdf({})


if __name__ == "__main__":
    unittest.main()
