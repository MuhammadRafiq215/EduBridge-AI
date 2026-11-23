"""Runtime readiness tests for EduBridge AI Teacher.

These tests use mocked HTTP responses. They do not contact or bill a live provider.
"""
import json
import unittest
from unittest.mock import patch

from src.ai_teacher import (
    OpenAICompatibleProvider,
    LocalModelProvider,
    build_provider_from_settings,
    build_request_messages,
)


class RuntimeReadinessTests(unittest.TestCase):
    def test_unconfigured_hosted_provider_stays_disabled(self):
        self.assertIsNone(build_provider_from_settings({
            "enabled": True, "provider": "openai_compatible",
            "model": "example-model",
            "base_url": "https://api.openai.com/v1",
        }))

    def test_openai_configuration_never_enables_vision(self):
        provider = build_provider_from_settings({
            "enabled": True, "provider": "openai_compatible",
            "model": "example-model",
            "api_key": "test-only-not-a-real-key",
            "base_url": "https://api.openai.com/v1",
            "supports_vision": True,
        })
        self.assertIsInstance(provider, OpenAICompatibleProvider)
        self.assertFalse(provider.supports_vision)
        self.assertTrue(provider.moderation_enabled)

    def test_local_runtime_is_explicit_and_loopback_only(self):
        provider = build_provider_from_settings({
            "enabled": True, "provider": "local",
            "model": "example-local-model",
            "base_url": "http://127.0.0.1:11434",
        })
        self.assertIsInstance(provider, LocalModelProvider)
        with self.assertRaises(ValueError):
            build_provider_from_settings({
                "enabled": True, "provider": "local",
                "model": "example-local-model",
                "base_url": "http://192.0.2.10:11434",
            })

    def test_official_evidence_is_marked_as_untrusted_and_citations_are_limited(self):
        messages = build_request_messages(
            [{"role": "user", "content": "Explain this qualification rule."}],
            knowledge_context="[SPEC:cambridge-2026] Official note: rule summary.",
        )
        prompt = messages[0]["content"]
        self.assertIn("UNTRUSTED SOURCE DATA", prompt)
        self.assertIn("[SPEC:cambridge-2026]", prompt)
        self.assertIn("cite only source IDs that appear exactly", prompt)

    def test_conversation_context_is_bounded_to_last_twelve_messages(self):
        history = [
            {"role": "user" if index % 2 == 0 else "assistant", "content": f"turn-{index}"}
            for index in range(16)
        ]
        messages = build_request_messages(history)
        self.assertEqual(len(messages), 13)
        self.assertEqual(messages[1]["content"], "turn-4")
        self.assertEqual(messages[-1]["content"], "turn-15")

    def test_openai_safety_screening_failure_blocks_generation(self):
        with patch("src.ai_teacher.urllib.request.urlopen", side_effect=OSError("offline")) as request:
            provider = OpenAICompatibleProvider("test-only", "example-model")
            with self.assertRaisesRegex(RuntimeError, "safety screening"):
                provider.answer([{"role": "user", "content": "Explain photosynthesis."}])
        self.assertEqual(request.call_count, 1)


if __name__ == "__main__":
    unittest.main()
