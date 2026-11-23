import unittest
from unittest.mock import patch

from src.ai_teacher import OpenAICompatibleProvider, build_provider_from_settings


class Phase30SafetyGateTests(unittest.TestCase):
    def test_cloudflare_provider_fails_closed_without_independent_screening(self):
        provider = build_provider_from_settings({
            "enabled": True,
            "provider": "cloudflare_workers_ai",
            "model": "@cf/meta/llama-3.1-8b-instruct",
            "api_key": "synthetic-test-token",
            "base_url": "https://api.cloudflare.com/client/v4/accounts/1234567890abcdef1234567890abcdef/ai/v1",
        })
        self.assertIsNotNone(provider)
        self.assertFalse(provider.moderation_enabled)
        with patch("src.ai_teacher.urllib.request.urlopen") as network:
            with self.assertRaisesRegex(RuntimeError, "AI Gateway Guardrails"):
                provider.answer([{"role": "user", "content": "Explain photosynthesis"}])
        network.assert_not_called()

    def test_official_openai_moderation_path_remains_available_for_tests(self):
        provider = OpenAICompatibleProvider(
            "synthetic-test-token", "synthetic-test-model", "https://api.openai.com/v1"
        )
        self.assertTrue(provider.moderation_enabled)

    def test_cloudflare_gate_does_not_expose_secret_in_error(self):
        secret = "synthetic-private-token-value"
        provider = build_provider_from_settings({
            "enabled": True,
            "provider": "cloudflare_workers_ai",
            "model": "synthetic-model",
            "api_key": secret,
            "base_url": "https://api.cloudflare.com/client/v4/accounts/1234567890abcdef1234567890abcdef/ai/v1",
        })
        with self.assertRaises(RuntimeError) as caught:
            provider.answer([{"role": "user", "content": "Explain algebra"}])
        self.assertNotIn(secret, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
