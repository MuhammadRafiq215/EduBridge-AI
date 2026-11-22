import unittest
from unittest.mock import patch

from src.account_store import clear_auth_session


class SessionPrivacyTests(unittest.TestCase):
    def test_sign_out_clears_credentials_and_learner_owned_ui_state(self):
        state = {
            "sb_access_token": "access",
            "sb_refresh_token": "refresh",
            "sb_user_id": "learner-a",
            "sb_user_email": "learner@example.invalid",
            "learner_profile": {"subjects": ["Mathematics"]},
            "profile_loaded_for": "learner-a",
            "ai_teacher_messages": [{"role": "user", "content": "private question"}],
            "ai_teacher_owner": "learner-a",
            "ai_teacher_history_loaded_for": "learner-a",
            "ai_teacher_persist_history": True,
            "ai_teacher_use_profile": True,
            "topic_progress_session": [{"subject": "Maths", "topic": "Algebra"}],
            "topic_progress_owner": "learner-a",
            "guided_practice_active": {"question_set": "private practice"},
            "guided_practice_feedback": "private feedback",
            "guided_practice_owner": "learner-a",
            "workspace": "Welcome",
            "unrelated_setting": "keep",
        }
        with patch("src.account_store.st.session_state", state):
            clear_auth_session()

        private_keys = {
            "sb_access_token", "sb_refresh_token", "sb_user_id", "sb_user_email",
            "learner_profile", "profile_loaded_for", "ai_teacher_messages",
            "ai_teacher_owner", "ai_teacher_history_loaded_for",
            "ai_teacher_persist_history", "ai_teacher_use_profile",
            "topic_progress_session", "topic_progress_owner",
            "guided_practice_active", "guided_practice_feedback",
            "guided_practice_owner",
        }
        self.assertTrue(private_keys.isdisjoint(state))
        self.assertEqual(state["workspace"], "Welcome")
        self.assertEqual(state["unrelated_setting"], "keep")


if __name__ == "__main__":
    unittest.main()
