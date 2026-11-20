import unittest
from unittest.mock import patch

from src.ai_teacher import (OpenAICompatibleProvider, LocalModelProvider, build_provider_from_settings, build_profile_context, build_request_messages, build_system_prompt, extract_response_text, validate_image)


class AITeacherTests(unittest.TestCase):
    def test_profile_context_only_contains_allow_listed_education_fields(self):
        profile = {"qualification": "Cambridge International A Levels", "subjects": ["Mathematics"],
                   "email": "private@example.invalid", "password": "must-not-be-included"}
        context = build_profile_context(profile)
        self.assertEqual(context["qualification"], "Cambridge International A Levels")
        self.assertNotIn("email", context)
        self.assertNotIn("password", context)

    def test_request_contains_profile_context_and_recent_turns(self):
        turns = [{"role": "user", "content": f"Question {i}"} for i in range(15)]
        result = build_request_messages(turns, {"level": "A Levels"})
        self.assertEqual(len(result), 13)
        self.assertIn("A Levels", result[0]["content"])
        self.assertEqual(result[1]["content"], "Question 3")

    def test_verified_knowledge_context_is_added_to_system_prompt(self):
        result = build_request_messages(
            [{"role": "user", "content": "What is the grading policy?"}],
            knowledge_context="Use this official fact [KB:BOARD-2026].",
        )
        self.assertIn("CURATED KNOWLEDGE BASE CONTEXT", result[0]["content"])
        self.assertIn("[KB:BOARD-2026]", result[0]["content"])

    def test_system_prompt_requires_exact_specification_citations(self):
        prompt = build_system_prompt(None, "Use only [SPEC:example-source].")
        self.assertIn("cite only exact", prompt)
        self.assertIn("[SPEC:source_id]", prompt)

    def test_image_is_encoded_as_data_url(self):
        result = build_request_messages([{"role": "user", "content": "Explain"}], image=(b"\x89PNG\r\n\x1a\n" + b"payload", "image/png"))
        self.assertTrue(result[-1]["content"][1]["image_url"]["url"].startswith("data:image/png;base64,"))

    def test_unsupported_empty_and_oversized_images_are_rejected(self):
        for payload, mime in ((b"data", "image/gif"), (b"", "image/png"), (b"not-a-png", "image/png"), (b"\x89PNG\r\n\x1a\n" + b"x" * (5 * 1024 * 1024), "image/png")):
            with self.assertRaises(ValueError):
                validate_image(payload, mime)

    def test_extract_response_text(self):
        self.assertEqual(extract_response_text({"choices": [{"message": {"content": " Answer "}}]}), "Answer")

    def test_invalid_response_is_rejected(self):
        with self.assertRaises(ValueError):
            extract_response_text({"choices": []})

    def test_provider_posts_to_compatible_endpoint(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b'{"choices":[{"message":{"content":"Test answer"}}]}'
        with patch("src.ai_teacher.urllib.request.urlopen", return_value=FakeResponse()) as mocked:
            provider = OpenAICompatibleProvider("test-key", "test-model", "https://example.invalid/v1")
            result = provider.answer([{"role": "user", "content": "Hello"}])
        self.assertEqual(result, "Test answer")
        self.assertEqual(mocked.call_args.args[0].full_url, "https://example.invalid/v1/chat/completions")


    def test_local_provider_can_be_configured_without_an_api_key(self):
        provider = build_provider_from_settings({
            "provider": "local",
            "model": "demo-model",
            "base_url": "http://127.0.0.1:11434",
            "supports_vision": True,
        })
        self.assertIsInstance(provider, LocalModelProvider)
        self.assertEqual(provider.model, "demo-model")
        self.assertTrue(provider.supports_vision)

    def test_local_provider_rejects_non_loopback_hosts(self):
        with self.assertRaises(ValueError):
            build_provider_from_settings({
                "provider": "local",
                "model": "demo-model",
                "base_url": "https://example.invalid",
            })

    def test_hosted_provider_requires_an_api_key(self):
        self.assertIsNone(build_provider_from_settings({
            "provider": "openai_compatible",
            "model": "demo-model",
            "base_url": "https://example.invalid/v1",
        }))

    def test_local_provider_uses_native_chat_endpoint(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b'{"message":{"content":"Local answer"}}'
        with patch("src.ai_teacher.urllib.request.urlopen", return_value=FakeResponse()) as mocked:
            provider = LocalModelProvider("demo-model")
            answer = provider.answer([{"role": "user", "content": "Explain arrays"}])
        self.assertEqual(answer, "Local answer")
        self.assertEqual(mocked.call_args.args[0].full_url, "http://127.0.0.1:11434/api/chat")


if __name__ == "__main__":
    unittest.main()
