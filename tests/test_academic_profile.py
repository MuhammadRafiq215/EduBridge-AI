import unittest
from src.academic_profile import calculate_academic_profile
class AcademicProfileTests(unittest.TestCase):
    def test_weighted_overall_and_equal_subject_average_are_distinct(self):
        r=calculate_academic_profile([{"subject":"A","marks_obtained":90,"maximum_marks":100},{"subject":"B","marks_obtained":20,"maximum_marks":50}])
        self.assertEqual(r["overall_percentage"],73.33); self.assertEqual(r["simple_average_subject_percentage"],65.0)
    def test_subject_rankings(self):
        r=calculate_academic_profile([{"subject":"Maths","marks_obtained":45,"maximum_marks":50},{"subject":"English","marks_obtained":60,"maximum_marks":100}])
        self.assertEqual(r["strongest_subject"],"Maths"); self.assertEqual(r["improvement_subject"],"English")
    def test_rejects_out_of_range_marks(self):
        with self.assertRaises(ValueError): calculate_academic_profile([{"subject":"Maths","marks_obtained":101,"maximum_marks":100}])
        with self.assertRaises(ValueError): calculate_academic_profile([{"subject":"Maths","marks_obtained":-1,"maximum_marks":100}])
    def test_rejects_zero_maximum(self):
        with self.assertRaises(ValueError): calculate_academic_profile([{"subject":"Maths","marks_obtained":10,"maximum_marks":0}])
    def test_rejects_duplicate_subjects(self):
        with self.assertRaises(ValueError): calculate_academic_profile([{"subject":"Maths","marks_obtained":10,"maximum_marks":20},{"subject":" maths ","marks_obtained":15,"maximum_marks":20}])
    def test_rejects_non_finite_marks(self):
        with self.assertRaises(ValueError): calculate_academic_profile([{"subject":"Maths","marks_obtained":float("nan"),"maximum_marks":100}])
    def test_does_not_invent_grades(self):
        r=calculate_academic_profile([{"subject":"Physics","marks_obtained":70,"maximum_marks":100}])
        self.assertIn("No letter grade",r["grade_note"])
if __name__=="__main__": unittest.main()
