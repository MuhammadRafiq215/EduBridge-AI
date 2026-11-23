import unittest

from src.chat_history_store import sanitise_messages


class ChatHistorySanitisationTests(unittest.TestCase):
    def test_keeps_only_bounded_user_and_assistant_text(self):
        clean = sanitise_messages([
            {"role": "system", "content": "must be discarded"},
            {"role": "tool", "content": "must be discarded"},
            {"role": "user", "content": "  Explain binary search  "},
            {"role": "assistant", "content": "It halves the search space."},
            {"role": "user", "content": "   "},
            {"role": "user", "content": 42},
            "not a message",
        ])
        self.assertEqual(clean, [
            {"role": "user", "content": "Explain binary search"},
            {"role": "assistant", "content": "It halves the search space."},
        ])

    def test_limits_message_count_and_content_length(self):
        messages = [{"role": "user", "content": f"Q{i}"} for i in range(105)]
        clean = sanitise_messages(messages)
        self.assertEqual(len(clean), 100)
        self.assertEqual(clean[0]["content"], "Q5")
        long_message = sanitise_messages([{"role": "user", "content": "x" * 12000}])
        self.assertEqual(len(long_message[0]["content"]), 10000)

    def test_empty_and_invalid_input_returns_empty_list(self):
        self.assertEqual(sanitise_messages([]), [])
        self.assertEqual(sanitise_messages(None), [])


if __name__ == "__main__":
    unittest.main()
