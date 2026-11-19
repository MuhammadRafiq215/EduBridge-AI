import unittest
from src.feedback import validate_feedback

class FeedbackValidationTests(unittest.TestCase):
    def test_valid_feedback_returns_only_requested_fields(self):
        payload, error = validate_feedback('Feature idea', 'Career pathways', 5, 'Please add more free university preparation resources.')
        self.assertIsNone(error)
        self.assertEqual(payload['rating'], 5)
        self.assertNotIn('email', payload)
        self.assertNotIn('name', payload)

    def test_rejects_unknown_category(self):
        payload, error = validate_feedback('Unknown', 'Dashboard', 4, 'The dashboard could use clearer labels.')
        self.assertIsNone(payload)
        self.assertIsNotNone(error)

    def test_rejects_short_or_long_messages(self):
        for message in ('Too short', 'x' * 1001):
            payload, error = validate_feedback('Other', 'Overall experience', 3, message)
            self.assertIsNone(payload)
            self.assertIsNotNone(error)

    def test_rejects_invalid_rating(self):
        payload, error = validate_feedback('Bug or error', 'Dashboard', 6, 'The page did not load correctly.')
        self.assertIsNone(payload)
        self.assertIsNotNone(error)

if __name__ == '__main__':
    unittest.main()
