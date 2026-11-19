import unittest

from src.global_education import (
    FIELDS_OF_INTEREST,
    INTERNATIONAL_QUALIFICATIONS,
    get_countries,
    get_qualification_options,
    get_subject_options,
)


class GlobalEducationCatalogTests(unittest.TestCase):
    def test_country_catalog_is_broad_and_has_custom_fallback(self):
        countries = get_countries()
        self.assertGreaterEqual(len(countries), 190)
        self.assertIn("Other / not listed", countries)

    def test_international_qualifications_are_available(self):
        options = get_qualification_options("Pakistan")
        for qualification in ("Cambridge International (IGCSE / O Level / AS & A Level)", "Pearson Edexcel (International GCSE / International A Level)", "International Baccalaureate (PYP / MYP / DP / CP)", "Advanced Placement (AP)"):
            self.assertIn(qualification, options)

    def test_subject_catalog_covers_multiple_disciplines(self):
        subjects = get_subject_options()
        for subject in ("Artificial Intelligence", "Psychology", "Law", "Agriculture", "Music", "Statistics", "Public Health"):
            self.assertIn(subject, subjects)
        self.assertGreaterEqual(len(subjects), 70)

    def test_fields_of_interest_are_broad(self):
        self.assertIn("Law & International Relations", FIELDS_OF_INTEREST)
        self.assertIn("Agriculture & Food Systems", FIELDS_OF_INTEREST)


if __name__ == "__main__":
    unittest.main()
